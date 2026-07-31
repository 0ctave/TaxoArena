# Known defects and instrumentation gaps

Status: **current**, as of 2026-07-27. Every item here is **documented rather than fixed**,
deliberately. Each entry states what is wrong, what it invalidates, and what a citation may
and may not say. Nothing here is a to-do list the thesis depends on.

## Certificate

**Two certificate fields are not reproducible run-to-run.** `trickle delta` and
`max rel d kappa` vary across runs of identical code at an identical seed:

| field | frozen | run A | run B |
|---|---|---|---|
| trickle delta | 1.110223e-16 | 3.330669e-16 | 2.220446e-16 |
| max rel d kappa | 3.500885e-13 | 3.847323e-13 | 5.545846e-13 |

Routing is parallel and float accumulation over concurrently-routed queries is not
associative, so these residuals carry scheduling noise even when every decision is
identical. `CERTIFIED`, `final iteration`, `edits delta` and `max 1-cos(mu)` **are** exact
and reproducible.

*Citation rule:* the two drifting fields are **bounded, not reproducible** — they land 7-10
orders below the 1e-6 tolerance in every run, and that bound is what the certificate
supports. An earlier verification that reported the file as byte-identical was luck and must
not be restated as a guarantee. Commit `7d33345`.

Consistent with the separately measured finding that a node's `kappa` never reaches
bit-identity between iterations, drifting at ~1e-13 forever (`...541 -> ...206 -> ...205 ->
...204`) while every gate outcome stays fixed.

**`tau` is overloaded (see `transferable-findings.md` §3c).** The same 1e-6 serves a per-edit
acceptance band and a per-iteration fixed-point tolerance. The acceptance half has been
taken over by the z-gate. The certificate half still uses `tau` and wants its own
derivation, `tau_cert`.

**A period-detecting certificate is wanted.** The current certificate tests period 1
(iteration i equals iteration i+1). The mcs=30 observation exhibited a 2e-6 alternation
between J = 0.287671 and J = 0.287673 — a tolerance-scale limit cycle that reads as
`CERTIFIED: false` forever and that a longer run will not close. The right instrument is
`certify(period = p)` for p in 1..4, which would distinguish "still moving" from "settled
into a 2-cycle at the tolerance scale". Not implemented.

## Provenance and manifests

**The manifest's `dirty` flag cannot distinguish source from prose.** It is true when any
tracked file is modified, so a thesis-text edit under `report/*.tex` marks a run dirty
identically to a change in `src/main`. The frozen artifact's run is flagged dirty for
exactly that reason and no production source was dirty. It should be split into
`dirty_src` / `dirty_other`.

**The `# outputDir:` provenance guard is test-only.** `ExperimentConfigHeaderTest`
(`src/test/kotlin/taxonomy/ExperimentConfigHeaderTest.kt`) checks that a config's header
`outputDir:` line matches its `outputDir` field. **Nothing checks this at load time.** A
config with a wrong or inherited header runs happily and writes to the directory in the
field while the header claims another. 42 configs carried stale sed-inherited headers; those
are now corrected, but the class of error is unguarded at runtime.

## Instrumentation that is declared but empty

**`wall_ms` in `iteration_metrics.csv`** — column declared, never populated, 0 in every row
of every bundle.

**Routing ECE is measured; its aggregation is wrong.** *Corrected 2026-07-30. The previous
text here — "`computeRoutingECE` returns 0.0 in every run in the project's history; routing
ECE has never been measured; do not report it" — was false, and is kept in this sentence so
the correction is visible rather than silent.*

`computeRoutingECE` (`src/main/kotlin/taxonomy/utils/AdditionalMetrics.kt:172`) is
implemented and reached. The `return 0.0` at line 179 is guarded on an empty ground-truth
map, which is not the state of a validation run. The frozen artifact exported a real value:

```
experiment_results/freeze_mcs55/seed_42/validation/MAIN_routing_calibration.csv:2
RoutingECE,0.21144242048722417
```

The same value appears in `MAIN_trickle_validation_results.csv` and in the tuning ledger, and
it passes the `Routing ECE <= 0.25` soft gate.

The real defect is one line upstream, at **both** call sites that build the predicted
distribution:

* `HeadlessBenchmarkRunner.kt:884-885`
* `BatchTrickleEvaluator.kt:195-196`

```kotlin
val domainConf = matched.groupBy { it.first.dominantDomain }
    .mapValues { (_, list) -> list.maxOf { it.second } }
```

A query routed to several leaves that share a dominant domain should contribute the **sum**
of those leaf shares to that domain. `maxOf` keeps only the largest single leaf. So the
confidence handed to the ECE is systematically understated whenever a domain is served by
more than one matched leaf, and the argmax can in principle pick the wrong domain — a domain
with one strong leaf beats a domain with three moderate ones. The bins are equal-width over
that understated confidence, so the reliability curve is shifted, not merely noisy.

*Citation rule:* **0.2114 is a real, exported measurement and may be cited as one**, with the
aggregation named. It may not be cited as a calibrated per-domain ECE. The sign of the error
is known — confidences are understated, so accuracy exceeds confidence in the affected bins —
but its magnitude has not been measured, because the fix has not been run. Either fix the two
`maxOf` sites to sum and re-run, or report 0.2114 with this paragraph attached. Do not report
it bare.

**Proposal accounting vs. proposal work.** Since `9a0aab2`/`a7fdf7d`, a memoized proposal
still records `attempted` + a `MEMOIZED` row, so `iteration_metrics.csv` counts are
unchanged by memoization — the saving is in work skipped, not proposals dropped. This is
correct but easy to misread: a `MEMOIZED` row is a repeat, not a new evaluation.

*Compatibility break:* `proposals.csv` files written before `a7fdf7d` carry repeats as full
`REJECTED` rows; after it, a repeat appears once as `MEMOIZED`. Any redundancy count that
crosses that boundary must treat `MEMOIZED` as the repeats. There is a second, earlier break
at `58f4aed` on the `k=` column (old-style semantics moved to `emK=`, and `sep_below_bar()`
no longer appears).

## Data

**~500 of 12000 `mmlu_pro` rows (4.2%) have no eval link.** The id-space repair joined by
question text (`mmlu_pro.id` is not the eval `question_id`; the numeric join produced a
clean, wrong result — see `transferable-findings.md` §4). The residual 4.2% is believed to
be the documented sentinel ids, but that has **not been confirmed**. Until it is, any
per-query coverage statement should carry the 4.2% as unattributed rather than as known
sentinels. Note that the discriminative-power join is exact and complete on its own
population (11769/11769) — this gap is upstream of that.

## Code paths that are unreachable in the reported configuration

These are not bugs; they are dead in *this* configuration and would become live in another,
so they are recorded so a config change makes them visible rather than silent.

* **The doubled small-node separation bar.** `requiredEps` doubles when
  `targetQueries.size < 2 * minClusterSize`, which the feasibility check at the top of
  `splitSingleNode` already forbids on the direct path. The only entrance is the
  diffuse-residual branch, and at `descentMargin = 0.12` the frozen tree carries zero
  residuals anywhere. `bar=0.0500` appears **0** times in the logs against 5628 of
  `bar=0.0250`.
* **`transitiveReduction`.** Not reached in the canonical tree (its call site is gated on
  `!enableResidualRouting`, and `DAG_MAX` sets that true). It **is** reached by
  `TREE_BASELINE` configs under `experiment_configs/calibration`, where it severs real
  edges — 54 `[TR] Severed N` lines with N up to 23. Deleting it would silently change every
  calibration baseline. Kept and documented.
* **`boundarySkips` in the proposal memo** is 0, as designed: the guard exempts sites with
  `vmfKappa < 1.0` (observed 130-200) or `depth >= 7` (observed max 5) from memoization. It
  is a safety net, not an active mechanism, and the count is reported so a future config
  change that makes it bind is visible.

## Removed, recorded so nobody re-adds them

`nearMisses` (a synchronized per-child ledger on the routing hot path whose only consumer
was deleted with cross-linking), `TaxonomySplitter.splitNodesRecursive` (an uncalled copy
that bypassed the `dJ` gate entirely — worse than dead), three duplicated flag assignments in
`HeadlessBenchmarkRunner` overwritten by the `dagMode` setter, the sibling-distinctness guard
(iterated a collection that `splitSingleNode`'s own precondition guarantees empty), the
`maxK=2` probe (three unreachable branches; `runVmfEm` has no randomness, so `k=2` is
evaluated identically under `maxK=2` and `maxK=4`), the dead k-way separation gate (rejected
nothing in 5682 opportunities), `secondaryMassFloor`, `bridgeSupportRelFraction` and the
`deltaThreshold` arguments.
