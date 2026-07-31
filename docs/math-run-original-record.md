# The original mathematics paired run — frozen record

**Written 2026-07-30, immediately before the re-run registered in Addendum 4.**

> **Four mathematics runs now exist (noted 2026-07-31).** This one (20 of 66 domain-level
> pairs, −18.22 / −2.00 steps); the registered Addendum 4 re-run (66/66 at domain level,
> cells at 18–19 of 66, −23.04 / −29.05); and two under the revised scheduler, complete in
> every cell, differing only in how leaves are ranked for adjacency — Copeland −16.00 /
> −22.00, Bradley–Terry −2.00 / 0.00. The sign is negative in all four. The magnitude
> spans 29 grid steps, and 14 of that spread lies between two runs of the same
> configuration. Nothing below changes; the file is left as the frozen copy Addendum 4
> requires. See `docs/newlogic-rerun-record.md`.

This file exists so that the original run cannot be quietly replaced by the
re-run. Addendum 4 fixes the reading of all three possible outcomes in advance
and states that "reporting only the re-run and discarding the original would be
unacceptable under any outcome; both appear, with the reason for preferring one
stated." This is the copy of the original that obligation refers to.

## Provenance

| | |
|---|---|
| database | `ratings_math_paired.db.final` |
| sha256 (first 24) | `179256e8ab0483a1174a0fa9` |
| identical to | `ratings_math_paired.db` at the time of copying |
| run date | 2026-07-28 |
| config | `experiment_configs/arena_math_paired.toml` |
| snapshot | `20260727_042523_Headless_Run_Auto_ge` |
| roster | 12-model Run-B roster, seed 42 |

## The numbers

Unpenalised pooled MM fit, the same estimator used for every other domain in
`tab:c5-all-domains`. The run exports apply a Jeffreys prior and differ in
absolute value; contrasts are unaffected.

| arm | ρ half-weighted | ρ ties-dropped | n | questions | ties | pair coverage | cells |
|---|---|---|---|---|---|---|---|
| MAIN | 0.887346 | 0.916084 | 2640 | 250 | 22.0% | **20 / 66** | 11 |
| C5 | 0.951049 | 0.923077 | 2638 | 250 | 26.6% | **20 / 66** | 11 |

**Δρ = MAIN − C5**

| convention | value | grid steps |
|---|---|---|
| half-weighted | **−0.063703** | −18.219 |
| ties-dropped | **−0.006993** | **−2.000** |

Grid step at M = 12 is 6/(12³−12) = 0.0034965.

Both arms favour the partition-free arm. The registered prediction was a null
(`|Δρ| < 0.007`, or inconsistent sign), so this is a **failed registered
prediction**, not a null and not a win for either side.

### A note on the ties-dropped value

−0.006993 is exactly two grid steps, which is the threshold the pre-registration
describes as "two steps of the Spearman grid" but quotes as the rounded number
`0.007`. Two grid steps is 0.0069930, seven millionths *below* 0.007, so this run
is decisive under the stated meaning of the rule and not decisive under its
literal number. The computer-science run landed on the same seam with the
opposite sign (+0.006993 half-weighted). The seam is recorded here rather than
resolved in whichever direction suits a given run; it needs one ruling applied
to both.

## The confound this run carries

Pair coverage, distinct model pairs with at least one comparison out of the 66
possible on a 12-model roster:

```
math          20 / 66      46 pairs never compared
law           66 / 66
philosophy    66 / 66
history       66 / 66
psychology    66 / 66
engineering   66 / 66
physics       66 / 66
computer sci  66 / 66
```

The most-compared model, `gemini-3.1-pro_5-shots`, appears in **55.0%** of all
MAIN comparisons. The Bradley–Terry fit therefore rests on a leader-centric star
of 20 pairs while every comparison domain has a complete comparison graph, and
sparse graphs are where Bradley–Terry estimates are least stable.

This run predates two commits:

- `5e1be09` — mandatory 66-pair bootstrap floor with an in-run coverage assertion
- `a5c36fd` — per-(leaf, pair) question shuffling

## What is and is not valid here

**Valid.** Both arms share the same sparse structure and the same 250 questions,
so the *paired contrast* is internally valid. The two arms are comparable to each
other.

**Not valid.** Any inference from this run to a property of mathematics as a
domain. The estimate comes from a graph three times sparser than every domain it
is compared against, and the comparison across domains is exactly what such an
inference requires.

## What the re-run changes, and what it cannot settle

The re-run holds everything fixed except the scheduler repairs: same 12-model
roster, same both-arms-identical-question-set design, same frozen snapshot,
confidence gate disabled, `|Δρ| ≥ 0.007` threshold, both tie conventions,
isolated ranking database.

Addendum 4 fixes all three readings in advance. Briefly: reproducing a negative
beyond threshold strengthens the finding on a complete graph; a null means the
original failure was a sparse-graph artifact and the original is superseded on
the grounds recorded here; a positive beyond threshold would be a screen failure
in the opposite direction from philosophy.

A single re-run at one seed does not separate scheduler effect from run-to-run
variance. If the two outcomes differ only marginally, the honest conclusion is
that mathematics is not stable enough to carry the weight the thesis places on
it, and the failed-null framing should be weakened accordingly.

## Related

- `docs/prereg_generic_judge_baseline.md` — Addendum 4 (the registration) and the
  2026-07-30 correction note (leaf-count definitions, routing-path disagreement)
- `docs/arena-math-findings.md` — the earlier analysis of this run
- `cs_secured/` — the computer-science run, the other registered null that failed,
  and the one with clean 66/66 coverage
