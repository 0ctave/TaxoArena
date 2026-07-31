# What is void, and what may never be restated

Status: **current**, extended 2026-07-31. Read this before quoting any number from this
project.

The file began as a list of what commit `c381211` (2026-07-27) invalidated. It now has three
sections, because three different things can be wrong with a number:

* **§1 Void after `c381211`** — measured correctly, on a tree that no longer exists. The
  method survives; re-run it.
* **§2 Withdrawn** — measured with a wrong instrument, or on a comparison that does not
  support the claim. Named, with the correction.
* **§3 Irreproducible — never restate** — the script no longer returns the published value,
  or returns a different one, and nobody can say why. These are not pending. They are gone.

Nothing here is deleted. A record of a correction is part of the evidence trail.

---

## 1. Void after `c381211`

`c381211` changed how `TaxonomySplitter.routeToVmfs` scores candidate children — from the
per-child density form to shared-kappa direction-only, matching production routing. See
`router-shared-kappa-correction.md`. Everything downstream of the routing-sustainability
check moved.

**The rule: the methods survive, the numbers do not.** These results are marked rather than
deleted, because in every case the measurement design is still correct and re-running it is
mechanical.

### Needs re-measuring

| result | what it was | status |
|---|---|---|
| the **maxK plateau** | maxK 6 -> 8 showing no further leaf growth | measured pre-fix; re-derive |
| the **k-fallback figures** | 129/83/0.232559 (no fallback, maxK=4), 48/36/0.181169 (no fallback, maxK=6), 141/84/0.238987 (fallback, maxK=4), 155/93/0.241473 (fallback, maxK=6) | the *qualitative* finding (maxK was a structural determinant without the fallback) stands; all four rows are pre-fix |
| the **five-seed sweep** | seed dispersion, z-gate stability analysis | the analysis design and its two negative results are sound; the leaf counts underneath them are pre-fix |
| **core / fringe** | the core-vs-fringe leaf partition and its size | pre-fix |
| **matched-k ARI** | cross-seed agreement at matched k | pre-fix |
| the **within-node nulls** in `separation_null_by_size.md` | 50 accepted splits, q values, the six named marginal splits, the leaf-lineage exposure table (7/25/13 leaves, 9.2%/19.7%/10.3%) | computed on the 88-leaf pre-fix tree; **method survives**, values need re-deriving on the frozen mcs=55 artifact |
| the **lambda1 / lambda-bar proxy** fitted against those nulls | R^2 0.865, LOO Q^2 0.851 | **method survives** (the fit procedure and cross-validation are correct); the fitted values are against void targets |
| **Philosophy's `min_child` reading** | the interpretation of why Philosophy stayed a single leaf | pre-fix. The *separate* Philosophy finding — that its indivisibility is a property of the 256-dim MRL slice rather than of the corpus — is measured on the corpus geometry, not on the routing check, and is unaffected. It remains marginal on its own terms: arm B lands at q = 0.950 against a like-for-like null on 60 replicates, i.e. exactly at the p95 boundary, so "beats its own null" is suggestive and not established. |
| the **previous frozen artifact** `20260726_200711_...` | 139 nodes / 88 leaves / maxDepth 5 / J 0.229418 | superseded by `20260727_042523_...`; carries the same suppression |
| the **"39 of 42" / "379 of 459" granularity claims** | blocked splits attributed to `minClusterSize` | **wrong, not merely stale.** The binding constraint was the mis-scored routing check, not the size floor. Replace with the derivation in `frozen-artifact.md`. |

### Not void by `c381211`

* **`prereg_discriminative_power.md`'s observed column** — run after the fix, with both
  routers as an explicit control. Its *disattenuated* column and its centred-residual
  quartet are a separate problem; see §2 and §3.
* **The isotropic null table** in `separation_null_by_size.md` — generated on synthetic
  clouds through `splitSingleNode`, so it measures the splitter's behaviour on structureless
  data. The routing check's scoring rule affects which real splits pass, not the isotropic
  null's shape. The `reach%` / `accept%` columns and the two-regime reading stand.
* **Everything in `transferable-findings.md`** — three of the four findings are *about* the
  defect class that `c381211` belongs to, and their supporting measurements
  (`SE(dJ)` spread of 13.1x, the 4-of-52 sub-z=1 acceptances, the 0-of-613 vs 97-of-613
  mixed-group counts, the 3-in-404 rescue rate) are properties of the measurement machinery
  rather than of the tree.
* **The determinism result** (`b5313ed`, builds A/B/C) — an internal three-way comparison at
  a single commit; it does not claim absolute values.
* **The Tier-0 / Tier-1 verifications** (`7a5ca86`, `9a0aab2`, `a7fdf7d`) — each verified
  *identity* against the then-current frozen artifact (leaf partition, all 50 accepted-split
  separations to 9 dp, node/leaf counts, depth histogram, leaf size distribution, J). Those
  verifications are still valid as statements that the refactors changed nothing. They are
  not claims about the current tree.
* **The memoization speedups** (133,942 ms -> 98,701 ms total, 26%; 25% excluding the
  noisy trickle timer) — measured against the same commit without the fix, so the comparison
  is internally controlled.

---

## 2. Withdrawn — wrong instrument, wrong comparison

Added 2026-07-30. None of these were caught by `c381211`; each is its own error.

### The reliability constant 7.66, and everything derived from it

3.04x too large. Spearman-Brown was applied after the curve fit instead of to each point
before it (x0.499), and the constant's dependence on roster size went unnoticed (x0.656).
Corrected value **`c = 2.52`** at the 11-model band. Derivation and both errors:
`measurement-discipline.md`, appendix.

Void as a consequence: every `r = n/(n+7.66)` reliability; the "median reliability fell
0.842 -> 0.745" reading of the router correction; the whole disattenuated column of
`prereg_discriminative_power.md`, including its clipping past 1.0, which was an artifact of
the oversized constant rather than a property of the data.

Also: **disattenuation is two-sided.** Both quantities carry error, so it is `rho_obs / r`,
not `rho_obs / sqrt(r)`. Several documents use the square-root form. They are wrong.

### Bradley-Terry standard errors, and every confidence interval

The variance correction used `1/K` where it should have used `1/K^2`. So **no
pre-correction standard error in this project is a measurement**, and the intervals built
on them are not intervals.

Two rules follow, and they are absolute:

1. **No confidence interval may appear anywhere in the thesis.** BT intervals have not been
   recomputed. Until they are, there is nothing to print.
2. Do **not** write "every standard error was the floor constant" as a flat statement. The
   pilot's stored values are mostly substitutions written by the `[ARENA-SE]` guard, so that
   sentence describes the guard, not the fit.

### The first cells-diversity permutation null

A **permutation null** builds fake cells by reshuffling the real assignments, then asks
whether the real cells do anything the fake ones do not. The first version sampled
pseudo-leaves independently, which gave them **11-26% pairwise question overlap** where real
leaves have **1.6-4.9%**. Overlapping pseudo-leaves agree with each other for free, so the
null was inflated and the real cells looked distinctive by comparison.

The corrected version matches pseudo-leaf overlap to the real distribution. Its answer is
the opposite one: **no domain shows sub-structure after multiple-testing correction**, and
several domains — economics p = 1.000, health p = 1.000, law p = 0.957 — have leaves that
agree with each other *more* than random splits of the same sizes do. The corrected method
is documented in the header of `tools/analysis/leaf_substructure_null.py`.

Report the correction. It is the cleanest instance in the project of
`measurement-discipline.md` rule 1 — a null whose comparison arm was never checked.

### Routing ECE reported bare

`0.2114` is a real exported measurement. It is computed on confidences that are
systematically understated, because both export sites aggregate a domain's leaf shares with
`maxOf` instead of summing them. Cite it with the aggregation named, or not at all. See
`known-defects.md`.

### Every per-cell quantity from the M = 12 arena batch

Added 2026-07-31. The batch's bootstrap counted its 66-pair floor over the **whole domain**
and scheduled every bootstrap match on the largest leaf. So each domain's comparison graph
reached 66/66 at the domain level while exactly one cell inside it reached 66/66 and the rest
sat at 4 to 33 pairs. Verified in all eight domains, both arms: philosophy `[16, 20, 66]`,
history `[12, 12, 28, 66]`, engineering `[4, 11, 33, 66]`, psychology `[23×5, 26, 26, 66]`,
computer science `[8, 13, 15, 19, 25, 66]`, law `[17, 17, 18, 19, 19, 66]`, physics
`[7×7, 12, 23, 66]`, mathematics re-run `[18, 19×9, 66]`.

`Delta rho` is fitted on **pooled domain** verdicts and survives this. Nothing computed
**inside a cell** does. Specifically withdrawn:

* "8 of mathematics' 11 cells individually favour C5" — those cells held 18 or 19 pairs of 66.
* The near-clone per-pair supports and tie rates (`6_Results.tex:790-804`). Direct
  comparisons per arm for `claude-3.5-sonnet` against `claude-3-5-sonnet-20241022`, M = 12
  batch → revised: philosophy 2 → 27, engineering 2 → 16, mathematics 2 → 63, psychology
  18 → 79, history 35 → 22. Identical in both arms in every run. Philosophy's and
  engineering's "2 direct comparisons per arm, the bootstrap minimum, too thin to read" is
  no longer true of the pair, and the tie rates would be computed on supports an order of
  magnitude apart.
* The near-clone over-resolution check (`6_Results.tex:806-822`), fitted on per-leaf
  leaderboards over those graphs. Its own footnote already conceded a refit "could move them
  either way".
* Every logged `converged: X/Y` figure for the batch, which was already void under caveat 3
  of `batch-M12-complete-record.md` for a separate reason.

Five domains were re-run with a per-(leaf, pair) floor and reach 66/66 in every cell. The
defect is fixed, so this is a withdrawal of measurements, not of a method.

### The M = 12 batch as a whole, as results

Added 2026-07-31. Superseded, not void. Beyond the per-cell defect, three of its runs had
unequal arms — engineering 0.833, physics 0.888, philosophy 0.901 — which the revised
scheduler fixes by construction. The batch is **kept and must still be reported**: every
pre-registration was written against it, and two registered nulls failed in it, in opposite
directions. What may not be done is quote its per-domain magnitudes as current results. See
`batch-M12-complete-record.md` and `newlogic-rerun-record.md`.

### The Mathematics paired arena runs

Four mathematics runs exist and their magnitudes do not agree. The original covers **20 of
66 model pairs** at the domain level, with the leader in 55% of comparisons, and predates
commits `5e1be09` (bootstrap floor) and `a5c36fd` (per-leaf-pair shuffle): −18.22 / −2.00
grid steps. The registered Addendum 4 re-run reaches 66/66 at the domain level: −23.04 /
−29.05. Two revised-scheduler runs reach 66/66 in every cell and differ only in how leaves
are ranked for adjacency: Copeland −16.00 / −22.00, Bradley–Terry −2.00 / 0.00.

The sign is negative in all four. **The magnitude is not a measurement** — it spans 29 grid
steps, and 14 of that spread lies between two runs of the same configuration. No sentence
may quote a size for the cost the partition carries in mathematics.

What does hold up is the secondary outcome: C5 beats MAIN on answer-key agreement in
mathematics under both batches, and in the revised run it is the only key-agreement gap
anywhere in the project that clears its own noise (81.8% against 86.0%, 2.4 combined SE).

Writing "mathematics has no cell structure to exploit" is still not licensed by any of it.

---

## 3. Irreproducible — never restate

Added 2026-07-30. These are not pending re-measurement. The generating script no longer
returns the published value, and in the cases where it returns something, it returns
something else. A number nobody can regenerate is not evidence, whatever it once was.

| number | what it was | status |
|---|---|---|
| **redundancy 72.2% / 42.2%** | share of leaf pairs redundant at rho > 0.90, and saturated at 1.0 | does not reproduce. The inversion argument built on it goes with it. |
| **correctness-blind rho 0.74-0.76** | ranking fidelity with correctness hidden from the judge | does not reproduce |
| **leaf-level 0.922 on re-routed assignments** | the re-routed reading | does not reproduce (the re-routed figure is 0.884). Note `prereg_discriminative_power.md` also carries a **0.922** measured on each cell's own constituent queries — a *different quantity that shares the digits*. Disambiguate explicitly wherever either appears, or a reader will merge them. |
| **the centred-residual quartet** | -0.119 / -0.024 / -0.024 / -0.024 | does not reproduce. This kills the mechanical-null table built on it. |
| **the 11-band flatness pair 0.973 / 0.936** | flatness across granularity at the 11-model band | the script returns **0.948 / 0.908**. Neither pair may be cited: not the published one, and not the returned one, because the discrepancy is unexplained. |
| **within-domain vs between-domain leaf comparison** | leaves within a domain agreeing less than leaves across domains | the between-domain arm does not reproduce, so the contrast has no second side |

---

## How to mark this in the thesis

Where a void number appears in a draft, do not delete the paragraph. Replace the number and
keep the reasoning, then say in one clause that it was re-measured after the router
correction. The methodological content of most of these results is the part worth keeping;
silently dropping them loses the argument along with the digits.
