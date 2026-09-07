# v2 validation plan — frozen tests for the seven proposals (2026-09-08)

Committed BEFORE any proposal's test runs. Each test adjudicates one proposal from
docs/v2_construction_proposals.md; descriptive readouts are labeled. Order follows
the recipe: P7 -> P1 -> P2 -> P5 -> P3, with P6 cheap-parallel and P4 deferred.

## P7 — determinism check (gate for everything)
Test: build the SAME config (seed 137 derivative, labeling off) twice into fresh
directories at current HEAD; byte-compare dag_snapshots.jsonl and the validation
CSVs. PASS iff bit-identical. Registered claim: the construction is bit-reproducible
at fixed (config, seed, code). Any diff is a P7 work item (sorted-accumulation gaps).

## P1 — consensus construction (the centerpiece)
Data: the 20 existing frozen-config seed builds (16 sweep + 4 arm-1), train-side
question assignments derived per build by nearest-leaf-centroid (max cos of the
256-slice vs leaf vmfMu) — the same disclosed approximation used for the ladder
corpora; the frozen build and embedder builds are additional descriptive axes.
Procedure (frozen): per anchor, co-assignment fraction across builds; average-linkage
agglomerative cut at co-assignment >= 0.6; cells below 55 train questions merged into
their nearest (by centroid) sibling cell.
REGISTERED PRIMARY: split the 20 builds into two disjoint 10-build halves by seeded
coin flip (seed 777); run the identical procedure per half; PASS iff
ARI(consensus_A, consensus_B) on shared train questions >= 0.90, reported against the
measured baseline mean pairwise ARI between INDIVIDUAL builds. FALSIFIED (per the
proposal's own criterion, adapted to the assignment metric) iff ARI < 0.80.
DESCRIPTIVE: consensus cell count per anchor; twin-absorption check (do the E1
within-anchor twin pairs land in one consensus cell?); cross-embedder agreement once
the nomic/gemma builds land. DEFERRED to the Kotlin warm-start build: the Top-1 and
mu-match clauses of the original proposal.

## P2 — site-level + deflated nulls, certification by pruning
Harness: extend the withinNull arm from anchors to every accepted split site of the
frozen artifact (population = the site's own train questions; same anisotropy-
preserving generator, 300 reps, seeded), plus the DEFLATED variant (split direction
projected out of the covariance).
REGISTERED: (a) power check — the deflated null must certify the known CS
contamination split while leaving Philosophy's two sites uncertified; (b) trunk
viability — site-level certification retains >= 15 splits, including the Chemistry
and Biology depth-1 splits (q = 0.000 at anchor level); trunk anchor drift <= 0.5pp.
Any other pattern reported as-is.

## P5 — support-derived strata floors
Procedure: rebuild strata with the acceptance rule "both halves >= 240 reserved"
(deff 2.0 x k/S^2 lower band) as strata_profile_v2.json — the frozen v1 file is
untouched. DESCRIPTIVE now: resulting stratum count and reserved-size distribution.
REGISTERED RIDER on the next profile-mode run: every stratum's QUERY-LEVEL SE <= 0.15
at <= 1.25x the R2 verdict budget.

## P6 — twin fusion vs placebo fusion (E2 harness variant)
Conditions on the frozen tree, full reserved pool, E2 metric: T (tree), F (top-3
cross-anchor E1 twin pairs FUSED: members merged, re-routed), Pf (3 placebo fusions:
random same-anchor-count leaf pairs at matched sizes, seed 999).
REGISTERED (two-sided): D = (F - T) - (Pf - T) per question; fusion helps iff mean
D > 0 with the 10,000-fold bootstrap CI excluding 0 AND sign p < 0.05; D <= 0 or CI
straddling 0 closes the overlap program with soft routing fully vindicated.

## P3 — functional twig gate (the one judge-spend test)
Prepared, NOT launched (>= 15k judge calls; runs on explicit go). Frozen design:
candidate twigs = every leaf whose parent is inside the (P2) certified trunk; probe =
per twig, up to 100 key-decidable reserved matches routed to it, sampled seeded,
QUESTIONS BURNED from future measurement use; arms = twig rubric vs PARENT rubric,
paired, dual-order; per-twig one-sided McNemar with Benjamini-Hochberg FDR 10%;
pooled kept-twig gain on a fresh probe draw as the registered secondary. The
Philosophy readout (does any Philosophy twig survive the functional gate?) is a
named descriptive.

## P4 — ll-objective (v2.1, deferred)
Design recorded in the proposals doc; no test frozen yet. Prerequisite: P1+P2
baseline stable. When scheduled: primary = cross-seed recurrence of ll-gated splits
exceeds J-gated baseline recurrence; reserved pool touched exactly once.
