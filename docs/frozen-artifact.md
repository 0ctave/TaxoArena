# The frozen construction artifact

Status: **current**, as of 2026-07-27. This is the artifact every downstream number
should be attributed to. If a figure elsewhere in `docs/` does not cite this snapshot or
a later one, check `void-results.md` before quoting it.

## Identity

| field | value |
|---|---|
| snapshot | `20260727_042523_Headless_Run_Auto_ge` |
| config | `experiment_configs/freeze_mcs55.toml` |
| commit | `c381211` (no production source dirty at run time) |
| output | `experiment_results/freeze_mcs55/seed_42/` |
| seed | 42 |
| nodes / leaves / maxDepth | 154 / 87 / 6 |
| mass | 8299.00, conserved, no `[MASS]` warnings |
| J | 0.253129 |
| labelling | 87/87 leaves labelled, 87/87 carry judge rubrics |

It **supersedes** `20260726_200711_Headless_Run_Auto_ge` (139 nodes / 88 leaves /
J 0.229418). That artifact was built with the biased split router and is void as a
quantitative source; see `router-shared-kappa-correction.md`.

## The fixed-point certificate

`experiment_results/freeze_mcs55/seed_42/fixed_point_certificate.txt`:

```
final iteration : 10
edits delta     : 0.000000e+00
trickle delta   : -3.330669e-16
max 1-cos(mu)   : 1.110223e-16
max rel d kappa : 4.246836e-13
tolerance (tau) : 1.000000e-06
CERTIFIED       : true
```

Iterations 8, 9 and 10 are identical on every column of `iteration_metrics.csv`.

**What the certificate means.** One further application of the construction operator
would change nothing the artifact consists of: the structural gate accepted no edit,
re-routing reproduced the same partition, and the refit moved no node's direction or
concentration. The refit term is not decoration — held-out queries route through
`(mu, kappa)`, so a certificate over structure and objective alone would not cover the
object being frozen.

**What it does not mean.** It certifies *this* artifact, not that the construction loop
terminates from an arbitrary start. It does not.

**Which fields are reproducible** (commit `7d33345`, measured by running the same commit
and config twice):

| field | status |
|---|---|
| `CERTIFIED`, `final iteration`, `edits delta`, `max 1-cos(mu)` | exact and reproducible |
| `trickle delta`, `max rel d kappa` | **bounded, not reproducible** |

Three observations of the same code: trickle delta 1.11e-16 / 3.33e-16 / 2.22e-16;
max rel d kappa 3.50e-13 / 3.85e-13 / 5.55e-13. Routing is parallel and float
accumulation over concurrently-routed queries is not associative, so those two residuals
carry scheduling noise even when every decision is identical. They land 7-10 orders below
the 1e-6 tolerance in every run, and **that bound is what the certificate supports**. An
earlier verification that reported the file as byte-identical was luck and must not be
restated as a reproducibility guarantee.

## Why each parameter has the value it has

State these in the direction given. Several of them are commonly stated backwards, and
the backwards version is a claim the evidence does not support.

### `minClusterSize = 55` — a budget choice, not a statistical requirement

Chosen so the cell count (87) matches what the judge budget can identify. Per-cell
reliability follows from it; it is not the target.

The licensing result is `prereg_discriminative_power.md`: observed Spearman rho between
cells is flat across an 11x change in granularity (0.929 at 14 domains / 0.922 at 88 /
0.922 at 87 / 0.905 at 152), with overlapping IQRs. Granularity is evaluatively flat, so
cell count is free to choose on budget grounds **at no measured evaluative cost**. Without
that result, 55 would be a compromise between coherence and support. With it, it is free.

Per-cell reliability is reported as a consequence: `r = n/(n+c)`. **Corrected 2026-07-30:**
the constant was published as 7.66, giving median 0.833 at 87 cells and 0.745 at 152. That
constant is 3.04x too large. The refit value is **`c = 2.52`** at the 11-model band
(`tools/analysis/reliability_constant.py`), so both reliabilities and the gap between them
were wrong; the derivation and the two errors are in `measurement-discipline.md`. Do not
quote 0.833 or 0.745.

### `acceptanceZ = 2.0` — defended on coherence alone

The gate accepts a structural edit when its measured `dJ` is large relative to the paired
bootstrap error of that same measurement (`TaxonomyOperations`, `[DJ-SE]` log lines,
`proposals.csv` `z` column).

The coherence argument: `SE(dJ)` spans **13.1x** from p10 to p90 on this corpus, so a
fixed tolerance cannot mean the same thing at two different sites. The uncalibrated rule
(`acceptanceZ = 0`, lexicographic on `(J, -|V|)` against `tau = 1e-6`) accepted **4 of 52**
edits below z = 1, the worst at **z = 0.156** (`dJ` 9.4e-06 against `SE(dJ)` 6.0e-05).
Committing an edit whose improvement is a sixth of its own measurement error is incoherent
regardless of what it does to any downstream number.

**Two empirical corroborations were tested and both were refuted. Report both as negative
results.**

1. *Stability tightening did not occur.* The effect of the gate is an additive offset of
   about **4.4 leaves**, not a change in dispersion. `corr(reduction, seed deviation) =
   +0.006`; variance ratio 1.05 against F(4,4) critical 6.39 — no detectable change in
   dispersion. The coefficient of variation rises 14.3% -> 15.7%, which is **mechanical
   from the mean shift** (same spread over a smaller mean) and must not be reported as
   degradation. This is the CV-vs-additive-effect error the pre-registration rules were
   written to prevent.
2. *J is not higher.* Higher on 2 of 5 seeds; sign test p = 0.812; median `dJ` -0.0001.
   The apparent J gain was seed 42 alone, the known outlier.

So the defensible sentence is: *the z-gate is adopted because a fixed absolute tolerance
is incoherent against a 13.1x spread in the error of the quantity it thresholds; it is
stability-neutral and J-neutral, and both of those were measured rather than assumed.*

### `maxK = 4` — a cost bound, but only since the k-fallback

Before the k-fallback (`e3c4b2c`), `maxK` was a **structural determinant**: raising it
4 -> 6 collapsed the tree to 36 leaves and J 0.181169, because a node whose single
proposal died at a downstream gate had no recourse and stayed an unsplit leaf. With the
fallback, `maxK` bounds cost (EM work is O(maxK^2), see `dag-construction-mechanisms.md`
§4) and no longer shapes the tree.

The plateau at maxK 6 -> 8 was measured before `c381211` and needs re-deriving.

### `proposalSeparationBar = 0.025` — positioned between two measured nulls

Isotropic null p95 spans 0.0055-0.0093 over n = 75..900; the within-node null p50 is
around 0.033-0.063 on sites with clean reach. The bar sits between them: conservative by
2.7x-4.5x against "more than nothing", permissive against "more than this node's own
elongation". Both statements are true simultaneously. Full table, method, caveats and the
six named marginal splits: `separation_null_by_size.md`.

The within-node numbers in that document were measured on the pre-`c381211` tree. The
**method survives**; the values need re-deriving.

### `descentMargin = 0.12` — a mode selector, not a tuned nuisance

Two justified operating points, not one optimum. delta = 0.12 is routing-optimal with
discovery off (what this artifact reports); delta ~ 0 turns discovery on at the cost of
about 5 points of routing quality and a 756-query residual reserve (9.1% of the corpus).
The corpus-size argument for choosing 0.12 here, and why it dissolves as the corpus grows,
is in `incremental-taxonomy.md`. Do not present 0.12 as "the tuned value".

## Known properties, stated rather than fixed

* **The floor is a birth constraint, not an invariant.** `minClusterSize` is enforced on
  the *routed* partition at split time. Populations drift under subsequent re-routing, so
  about 1% of leaves end marginally below it — 1/87 here, 1/152 at mcs=30, 1/104 in an
  earlier build. Three consistent instances. This is a property of the mechanism, not a
  bug to patch, and any statement of the form "every leaf holds at least
  `minClusterSize` queries" is false as written.
* `wall_ms` is declared in `iteration_metrics.csv` and never populated — 0 in every row.
* The manifest's `dirty` flag was true for this run from `report/*.tex` and one test file.
  No production source was dirty. The flag cannot currently distinguish those cases; see
  `known-defects.md`.

## Deriving a new config from this one

`freeze_mcs55.toml`'s header is a provenance record, not boilerplate. Rewrite it when
deriving; do not `sed` it. 42 configs in `experiment_configs/` had carried stale
sed-inherited headers (now corrected). The `# outputDir:` line is what
`ExperimentConfigHeaderTest` checks — and that guard is **test-only**; nothing validates
it at load time.
