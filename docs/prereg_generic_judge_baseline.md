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
Bounded honestly: n = 11 models gives a grid of 0.0035, and math's GT ordering is
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
