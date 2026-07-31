# Pre-registration: arena launch decisions

Written **before** the smoke run reports, so the cut is not chosen with the
number in front of us. Reading a value and deciding what it means at the same
time is the shape of most errors this session caught.

## Decision 1 — where to cut the tree for judging

`[ARENA-IDENT]` reports pairs-with-data and total comparisons on every
identified fit. Take the **minimum per node across rounds** — that is the cost;
anything above it is scheduler allocation, not requirement.

Budget ~10,000 judge calls, 87 leaves.

| observed calls/cell | 87-cell total | decision |
|---:|---:|---|
| **<= 40** | <= 3,500 | judge at LEAVES; room left to resolve beyond identification |
| **40-70** | 3,500-6,100 | judge at leaves, at the floor. Per-cell rankings are bare identification and must be reported as such |
| **> 70** | > 6,100 | leaf-level consumes the budget. CUT AT DEPTH-3 and report the fine end of the fidelity curve as unmeasured |

Fixed in advance. No band is to be renegotiated after the number is seen.

### Report the distribution, not the mean

Rule 2 applies here as much as anywhere. Report median, IQR and n, and
specifically:

* **does cost rise on smaller cells?** Plausible a priori — fewer queries means
  fewer distinct comparisons available per pair. If it does, the leaf arm is
  more expensive than any average suggests, because the small cells are the ones
  that push the total.
* **does it vary enough that a single figure misleads?** The Math run spent
  exactly 56 on every cell across a 3.4x size range, which was an allocation.
  A genuine cost should vary; if the new number is also constant, the scheduler
  is still capping rather than converging and the measurement is void again.

## Decision 2 — two smoke-run checks that must FIRE, not merely exist

**`validateVerdictNodeIds` must be exercised against a deliberately wrong
node_id and confirmed to fail.** An assertion that has never fired is in the
same category as a gate that has never fired — see rule 0. Present-and-untested
is not tested.

**A non-MAIN verdict CSV must appear.** `isExportCondition` gates the frozen-
triples export on `condition == "MAIN"`. Per-condition CSVs are believed to be
written for every arm, but A5 (per-cell MAIN-minus-GENERIC against reusable
share) needs GENERIC_JUDGE separable from MAIN. Confirm in a four-condition
smoke run at trivial budget; if only MAIN exports, A5 has no data and that is a
code change, not a reporting choice.

Also verify in the same run: `rank_history.csv` populates (wired, never
exercised with `runBenchmark = true`), and the three new `match_history` columns
land non-NULL.

## Decision 3 — what a PARTIAL rubric result means

The random-cell arm's bands are fixed in `prereg_rubric_specificity.md`
(<= 0.05 causal, >= 0.10 refuted, between = partial). Recording here what the
partial band would MEAN, so it is not argued afterwards:

> Random cells at ~0.05 specificity would say the model produces somewhat
> cell-specific language regardless of coherence, and that coherence roughly
> doubles it.

That is weaker than "coherence causes specificity" but it is still a real
finding, and it is reportable as stated rather than as a failed test.

## Order

smoke run -> read cost against the bands above -> set the cut -> launch.

The 20-cell rubric arm and the hold-out experiments run in parallel with the
arena; neither touches it.

---

# Addendum (2026-07-30) — outcomes, and one prediction that fired

**Nothing above is edited.**

## The band attribution is resolved, against this document

Line 58-59 above states that the random-cell arm's bands (`<= 0.05` causal, `>= 0.10`
refuted, between = partial) are fixed in `prereg_rubric_specificity.md`. That document's
addendum rules the other way: the band is stated **here**, it governs the random arm's
absolute own-cell specificity, and that document's attribution of the band to this one is an
error in that document. Recorded so the two files agree on where the band lives.

## The partial band never applied

The random arm landed at **0.012**, inside the `<= 0.05` causal band. Leaf rubrics landed at
**0.138**, Mann-Whitney one-sided **p = 1.21e-6** over 87 leaf rubrics against 13 random
cells, with terms appearing in >= 90% of rubrics at **0 vs 6**. The partial reading at lines
63-65 is moot.

## The constant-allocation warning fired, on mathematics

Lines 33-36 above warn: *"the Math run spent exactly 56 on every cell across a 3.4x size
range, which was an allocation ... if the new number is also constant, the scheduler is still
capping rather than converging and the measurement is void again."*

That is the confound that later surfaced. The mathematics paired run covers **20 of 66 model
pairs**, with the leader in 55% of comparisons, against 66 of 66 in every other domain. It is
the only paired run predating commits `5e1be09` (bootstrap floor) and `a5c36fd`
(per-(leaf,pair) shuffle). A re-run is registered under Addendum 4 of
`prereg_generic_judge_baseline.md` and is pending.

This document predicted the failure mode before the run. Cite it when the confound is
discussed; a warning that fired is worth more than one that was never tested.

## Not verified

The three smoke-run assertions this document required — that `validateVerdictNodeIds` fires,
that a non-MAIN verdict CSV is written, and that `rank_history.csv` is populated — have not
been confirmed to have fired. They remain open.
