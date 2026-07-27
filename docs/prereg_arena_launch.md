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
