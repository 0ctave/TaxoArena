# The revised-scheduler batch — the results record

**Written 2026-07-31. This file holds the numbers the thesis reports.** It replaces a
2026-07-30 version with two faults: it covered three domains, and its headline said "Every
domain moved". Philosophy did not move — it held at +14.00 grid steps exactly, on a run
whose arms went from 0.901 balanced to 1.000 and whose cells went from `[16, 20, 66]` pairs
to complete. That is the strongest single item in the batch, and the earlier file omitted it.

Five domains, both arms each, on a scheduler and stopping rule that fixed two defects in
the earlier M = 12 batch. That earlier batch is not a baseline and is not comparable on
magnitude; it is kept in `docs/batch-M12-complete-record.md` as the record of what the
defects cost.

## What the batch is

| | |
|---|---|
| roster | 12 models, 7 families |
| frozen snapshot | `20260727_042523_Headless_Run_Auto_ge` |
| held-out pool | `is_reserved = 1`, all in-domain reserved questions |
| domains complete | 5 of 14 (philosophy, history, psychology, mathematics, engineering) |
| conditions | `MAIN` (per-leaf rubric) vs `C5` (generic, partition-free) |
| design | paired — both arms judge an identical question set |
| seed | 42 |
| dates | 2026-07-30 19:44 to 2026-07-31 00:26 |
| judge | Azure `Mistral-Large-3`, two calls per verdict (position swap) |

**Estimator.** Unpenalised pooled Bradley–Terry MM fit over each arm's verdicts, Spearman
ρ against per-model ground-truth accuracy on that arm's own question set. Same script and
same estimator for every row, including the old-batch rows quoted for comparison.
`Δρ = ρ_MAIN − ρ_C5`, so **positive favours the per-leaf arm**. At M = 12 the Spearman
statistic is quantised at 6/(12³−12) = 0.0034965 and Δρ is reported in grid steps as well
as raw; the pre-registered decisive threshold is two steps.

Every number below was recomputed from the ranking databases on 2026-07-31. Nothing is
copied from an earlier draft.

## The results

| domain | ρ MAIN | ρ C5 | Δρ | steps half | steps drop | n MAIN | n C5 | questions | cells |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| philosophy | 0.944056 | 0.895105 | +0.048951 | **+14.00** | +14.00 | 966 | 966 | 99 | 3 |
| history | 0.867133 | 0.853147 | +0.013986 | **+4.00** | +4.00 | 839 | 837 | 95 | 4 |
| psychology | 0.881119 | 0.874126 | +0.006993 | **+2.00** | +2.00 | 2405 | 2397 | 205 | 8 |
| mathematics | 0.930070 | 0.937063 | −0.006993 | **−2.00** | 0.00 | 2328 | 2328 | 218 | 11 |
| engineering | 0.989480 | 0.978953 | +0.010526 | **+3.01** | +3.01 | 649 | 649 | 66 | 4 |

ρ columns are half-weighted ties. Only mathematics differs between conventions
(0.930070 in both arms under ties-dropped, so Δρ = 0).

MAIN beats C5 in four of five. Mean ρ 0.9224 MAIN against 0.9077 C5. Complete pair
coverage in every cell of every run: all 66 model pairs in all 30 cells, both arms.

The claim this supports: **on matched comparison budgets, cell-scoped judging recovers
the ground-truth ranking more closely than a generic partition-free judge in four of five
domains, and both arms land close to the true MMLU-Pro ordering.** Every qualification it
has to carry is in the next section.

## What the batch does not carry

1. **Nothing here is registered.** Every prediction in
   `docs/prereg_generic_judge_baseline.md` was written against the old configuration.
   Addendum 4's registered mathematics re-run is the *old-logic* run
   (`math_rerun_secured`), so the mathematics row above does not satisfy it. There is no
   pre-registered prediction for any of these five domains under this scheduler.

2. **Five of eight, not eight of eight.** Physics was still running when this was
   written. Computer science has not been attempted. Law failed twice — see below — for
   reasons never established. Reporting five of five as a win rate would be reporting a
   set chosen by which runs finished.

3. **Engineering is unresolved.** Its old-logic run was the batch's one clean registered
   NULL: +1.00 half, −1.00 dropped, sign flipping, prediction met. Under the revised
   scheduler it is +3.01 under both conventions. Either the revised logic favours the
   per-leaf arm, or the old run was too broken to detect a real effect — its arms were
   0.833 balanced and one of its four cells held 4 of 66 pairs. Nothing in this batch
   distinguishes those two readings. Engineering must not be presented as a clean
   positive.

4. **Absolute ρ is not stable to three decimals** across defensible analysis conventions.
   The run exports apply a Jeffreys prior and give different absolute values from the
   table above. Paired contrasts within a run are safe; absolutes are indicative.

5. **No Bradley–Terry confidence interval exists anywhere in this project, and none may
   be added.** The variance computation was wrong before a dated fix and intervals were
   never recomputed. The revised scheduler replaces the collapsing query bootstrap with an
   inverse-variance combination of per-leaf Fisher SEs; that is a scheduler input, not a
   reportable interval.

6. **Mathematics is the one domain where the partition does not help.** −2.00 steps is
   two steps against a two-step threshold, and 0.00 under the other tie convention, so it
   is closer to a tie than to a loss. It is still the only negative sign in the batch, and
   it is corroborated by key agreement (§ below), where C5 leads by 4.2 points at 2.4
   combined SE. See also the adjacency caveat below, which cuts the other way.

7. **The code is uncommitted.** `git status` on 2026-07-31 shows 567 inserted and 190
   deleted lines across `ArcTaxonomyLLMClient.kt`, `ActiveBtRacingScheduler.kt`,
   `BtMatchScheduler.kt`, `BtStoppingPolicy.kt`, `TaxonomyBenchmarkService.kt` and
   `TaxonomyRankingService.kt`, all unstaged. There is no commit hash to cite and no
   configuration a future pre-registration could name.

8. **The batch is not code-identical across its five domains.** Change 9 below — ranking
   leaves on fitted Bradley–Terry strengths instead of Copeland win-rate sums — landed
   between the history run (finished 19:44) and the mathematics BT-adjacency run
   (finished 21:42). Psychology, philosophy and engineering ran after it. History ran
   before. Nothing in the run artefacts records the code state, so this is inferred from
   file timestamps; it is not verified.

9. **Two mathematics runs exist under the revised logic and they disagree.** The
   Copeland-adjacency run (`math_newlogic_secured`, 1724 per arm, 213 questions) gives
   −16.00 / −22.00 steps. The BT-adjacency run (`math_btrank_secured`, 2328 per arm, 218
   questions) gives −2.00 / 0.00. Same domain, same seed, same snapshot, same question
   pool; only the leaf ranking used to pick adjacent pairs differs. The table above quotes
   the BT-adjacency run because that is what the code now does and because it ran longer,
   but a 14-step spread between two runs of the same domain is the sharpest available
   evidence that per-domain magnitude is a property of the sampler, not of the domain.

## What the old logic got wrong

Two defects, both fixed, both scheduler-side.

**Every cell but one was starved.** The old bootstrap counted its 66-pair floor over the
whole domain and scheduled every bootstrap match on the largest leaf. The domain-level
comparison graph therefore looked complete while individual cells sat far below it.
Per-cell pair coverage, MAIN arm, of 66 possible:

| domain | old logic | revised |
|---|---|---|
| philosophy | [16, 20, 66] | [66, 66, 66] |
| history | [12, 12, 28, 66] | [66, 66, 66, 66] |
| psychology | [23, 23, 23, 23, 23, 26, 26, 66] | all 66 |
| mathematics (Add. 4 re-run) | [18, 19×9, 66] | all 66 |
| engineering | [4, 11, 33, 66] | [66, 66, 66, 66] |

Exactly one complete cell per domain, everywhere, in both arms. Across the whole old
batch the starved cells run from 4 pairs (engineering) to 33. Δρ is fitted on pooled
domain verdicts and survives this; every *per-cell* quantity in the old batch rests on
those graphs and does not.

**Three runs had unequal arms.** engineering 0.833, physics 0.888, philosophy 0.901. C5
now stops at MAIN's comparison count, so balance is 1.000 or within two comparisons of it
by construction: philosophy 966/966, engineering 649/649, mathematics 2328/2328, history
839/837, psychology 2405/2397. `(question, model pair)` overlap between the arms follows:
philosophy 89.9% → 100%, engineering 83.3% → 100%, history 99.9% → 99.8%, psychology
99.6% → 99.7%, mathematics 100% → 100%.

## Cost

| domain | old | revised | change |
|---|---:|---:|---|
| history | 1448 | 839 | −42% |
| psychology | 3300 | 2405 | −27% |
| philosophy | 1319 | 966 | −27% |
| engineering | 792 | 649 | −18% |
| mathematics | 2640 | 2328 | −12% |

Cheaper everywhere, and with complete per-cell coverage, despite the per-leaf bootstrap
costing 66 × cells calls before any adaptive sampling starts. Two fixes pay for it: the
batch-overspend fix (one pair used to absorb about 33 comparisons against a budget of 8–9
because `stats` only refreshed between rounds) and exact binomial resolution (a one-sided
pair retires at n = 9 instead of about 23 under the Hoeffding bound it replaced).

The revised runs also judge fewer questions than the old ones — philosophy 99 against
126, history 95 against 128, psychology 205 against 235, mathematics 218 against 248,
engineering 66 against 113. The question set is identical between the two arms of a run,
which is what the paired design requires, but it is **not** identical between an old run
and its revised counterpart. Nothing that compares an old number to a revised one on
absolute scale is comparing like with like.

## Answer-key agreement

Fraction of decisive comparisons — exactly one side correct against the MMLU-Pro key —
where the judge picked the correct side. Computed here for the first time under the
revised logic; the 2026-07-30 version of this file did not record it.

| domain | MAIN | C5 | gap | combined SE | gap / SE |
|---|---:|---:|---:|---:|---:|
| philosophy | 83.5% | 83.8% | −0.3 | 2.83 | −0.11 |
| history | 78.6% | 76.4% | +2.2 | 3.37 | +0.65 |
| psychology | 80.7% | 78.2% | +2.5 | 2.04 | +1.23 |
| mathematics | 81.8% | 86.0% | −4.2 | 1.77 | **−2.37** |
| engineering | 92.0% | 91.4% | +0.6 | 2.32 | +0.26 |

Mathematics is the only gap that clears its own noise, and it favours C5 — the same
direction as its Δρ, and the same direction the old logic gave (93.1% against 94.3%). The
other four gaps are inside one combined SE and support nothing.

**The philosophy dissociation does not replicate as a magnitude.** Under the old logic
philosophy paired the largest Δρ in the project with a key agreement 1.3 points *below*
C5 against a combined SE of 1.8. Under the revised logic Δρ holds at +14.00 steps and the
key-agreement gap falls to 0.3 points at 2.83 SE — the same sign, no longer measurable.
The dissociation may be stated as a direction. It may not be stated as an effect.

Key agreement is computed on each run's own question set, so these values are not
comparable to the old batch's on level, only on sign.

## Convergence

| domain | cells | best observed |
|---|---|---|
| philosophy | 3 | 2/3 |
| history | 4 | 4/4, per the 2026-07-30 record — **not re-verifiable**, its log has rotated out |
| psychology | 8 | 7/8 |
| mathematics (BT adj) | 11 | 2/11 |
| engineering | 4 | 1/4 |

Every run in the project before this batch terminated by exhausting schedulable work
rather than by meeting the criterion. History is the only claimed full convergence and
its log no longer exists, so it is **provenance unclear**: the 4/4 figure is carried over
from the 2026-07-30 record and cannot be checked against the surviving logs
(`logs/taxoarena{,.1,.2,.3}.log` start at 21:21 on 2026-07-30; history finished at
19:44).

The criterion requires all `k−1` adjacent pairs terminal simultaneously in a cell, which
at 11 cells is 121 pair-slots at once. Ranking adjacency on fitted BT scores rather than
Copeland sums moved mathematics from 0/11 to 2/11 — an improvement, not a fix. The
2026-07-30 record said mathematics was "0/11 throughout"; the BT-adjacency run reached
2/11 at 21:41.

## Provenance

| run | database | sha256 (16) |
|---|---|---|
| philosophy | `philo_newlogic_secured/ratings.db.final` | `7e8b5f81ad5946c4` |
| history | `history_newlogic_secured/ratings.db.final` | `4c9e6232ace993be` |
| psychology | `psych_newlogic_secured/ratings.db.final` | `8e53f88c6df9ac54` |
| mathematics (BT adjacency, reported) | `math_btrank_secured/ratings.db.final` | `37dbdedebdf7285c` |
| mathematics (Copeland adjacency) | `math_newlogic_secured/ratings.db.final` | `a301b3184bbd9ddb` |
| engineering | `eng_newlogic_secured/ratings.db.final` | `0a30d409bfec51bf` |

Superseded databases untouched: `ratings_philosophy_paired.db`,
`ratings_history_paired.db`, `ratings_psychology_paired.db`,
`ratings_engineering_paired.db`, `math_rerun_secured/ratings_math_rerun.db.final`,
`ratings_math_paired.db.final`.

Configs: `experiment_configs/arena_{philosophy,history_m12,psychology,math,engineering}_newlogic.toml`.
All six are identical apart from `category` and `outputDir`. Snapshot id in
`match_history` confirmed as `20260727_042523_Headless_Run_Auto_ge_{MAIN,C5}` in every
database.

`benchmark_metadata` is empty in all of these databases, and in the old batch's too, so
the run parameters are recoverable only from the TOML files, not from the artefact.

## Domains without a result

- **physics** — running at the time of writing (`ratings_physics_newlogic.db`, active
  WAL). Ten cells. No result.
- **computer science** — never attempted under the revised scheduler. Its old-logic run
  failed a registered null in the positive direction (+2.00 / +8.00).
- **law** — two attempts discarded. `ratings_law_slowrun_discarded.db` and
  `ratings_law_newlogic.db` both ran at about 30 verdicts/min against 90–100 for
  comparable domains, at both 48 and 32 permits, with the endpoint responding in 8.7 s
  sequentially and no 429s. Endpoint load, client backoff state and prompt size were each
  tested and ruled out — history has a near-identical prompt size and runs three times
  faster. **Unexplained.** Law has no revised-logic result.

## Runs discarded, and why

- **`ratings_math_btrank_netfail.db`** — a network outage at 20:47–20:51 on 2026-07-30
  produced 58 hard errors, 299 connection resets and 135 timeouts. The run reported
  `BUILD SUCCESSFUL` and wrote its exports; nothing in the pipeline flagged it. **Grep any
  log for `Hard error` and `Connection reset` before reading a result.** No assertion
  fails a network-damaged run. The five reported runs were checked: zero hard errors, and
  two transient connection resets at 22:39 during psychology, both retried on attempt 1
  of 3.
- **`ratings_history_m12_prev_attempt.db`** — history under changes 1–6 only. MAIN
  completed at 1445; C5 stopped at 547 and was discarded.

## Changes under test

1. Per-(leaf, pair) bootstrap floor, round-robin across leaves
2. Aggregate SE = inverse-variance combination of per-leaf Fisher SEs, replacing a query
   bootstrap that collapsed under separation and tripped `[ARENA-SE]` on all eight old runs
3. C5 stops at MAIN's comparison count — arm balance by construction
4. Per-(leaf, pair) budgets from each leaf's own pool, `clamp(q/4, 8, 25)`
5. Exact binomial resolution replacing an unreachable Hoeffding bound
6. Convergence fraction constant at 0.70 across granularities
7. Racing scheduler counts reserved comparisons within a batch
8. Globally-resolved pairs terminal in both scheduler and stopping policy
9. Adjacency ranked on fitted BT scores, Copeland only as a pre-fit fallback
10. Round loop exits when the scheduler returns an empty batch

Changes 1 and 3 are the two that make this batch the results and the old one a record of
defects. The rest are cost and correctness.

## Related

- `docs/batch-M12-complete-record.md` — the superseded batch, kept for what the defects cost
- `docs/math-run-original-record.md` — the first mathematics run, sparser again
- `docs/stale-results-audit.md` — where every superseded number still sits in `report/`
- `docs/prereg_generic_judge_baseline.md` — the registrations, none of which cover this batch
