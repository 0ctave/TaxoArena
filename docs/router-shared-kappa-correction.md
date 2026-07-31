# The kappa-normaliser bias: two sites, and the general form

Status: **current**. Fixed at commit `c381211` (second site) and earlier in the trickler
(first site). The search for further instances is closed.

This is the single most consequential correction in the project's history and it must be
propagated to every claim about granularity. Read this before quoting any pre-`c381211`
number.

## The defect

Two vMF components are being compared to decide where a query goes. There are two ways to
score them:

```
per-child density form   score_i = logC_d(kappa_i) + kappa_i * <mu_i, x>
shared-concentration     score_i = kappa_bar   * <mu_i, x>          kappa_bar = mean_i kappa_i
```

The first is the correct log-density of query `x` under child `i` *in isolation*. It is
the wrong thing to compare across children, because `logC_d(kappa)` decreases with kappa
while `kappa * cos` increases with it. At `d = 256` the two terms are of order tens of
nats and they do not cancel. The consequence is systematic and directional: **boundary
queries are handed to the more concentrated sibling on concentration bookkeeping rather
than on direction.**

The second form is scale-free across siblings. `kappa_bar` is a positive constant across
the competition set, so it cannot change the argmax — it is retained only so the two call
sites read identically and cannot drift apart silently.

## Site 1 — the trickler's sibling competition (fixed earlier)

`TaxonomyTrickler` originally scored siblings with the per-child density form. High-kappa
siblings absorbed their neighbours, and **four ground-truth domains were killed** by that
absorption. Production routing was moved to `kappa_bar * dot` plus an additive cosine beam
(`routingBeamGamma`). Related and separately measured on the same mechanism: under a
density-based *descent* gate, 56% of the corpus was mis-residualised at anchors, because
the Hornik-Grün shrinkage `(n-1)/(n+d-2)` scales with n and so fits parents systematically
sharper than children.

## Site 2 — the splitter's routing-sustainability check (fixed at `c381211`)

`TaxonomySplitter.routeToVmfs` was never updated when site 1 was. It kept scoring
candidate children with

```kotlin
score = vmf.logNormalizer + vmf.kappa * dot(x, vmf.mu)
```

The check this feeds is *routing sustainability*: reject the split unless every proposed
child holds at least `minClusterSize` under the level-local posterior the trickler uses.
Its justification is literally "the same posterior the trickler uses". It was not the same
posterior. **The splitter was validating candidates against a router the tree does not
use.**

The bias lands precisely on `min(routed child)`, which is the quantity the check tests, so
the failures concentrated on candidates with one tight and one diffuse child — exactly the
shape a real semantic split has.

### Measured effect, seed 42, z = 2.0, maxK = 4, k-fallback on

| | not-routing-sustainable rejections | nodes | leaves | J |
|---|---:|---:|---:|---:|
| density form (before) | 750 | 141 | 84 | 0.238987 |
| shared kappa (after) | **42** | 278 | 152 | **0.287671** |

Rejections fall 94%; leaves rise 81%; J rises 20.4%.

At matched granularity the correction is worth **+10.3% J**: the frozen mcs=55 artifact
(87 leaves) scores 0.253129 against the previous frozen artifact's 88 leaves at 0.229418.

### The consequence that must be propagated

**`minClusterSize` was not the binding constraint on granularity.** The binding constraint
was a scoring rule that did not match the router.

Any statement of the form

* "39 of 42 blocked splits hit `minClusterSize`",
* "379 of 459 blocked splits hit `minClusterSize`",
* "granularity is arena-derived because the size floor is what stops splitting",

is **wrong** and must be corrected wherever it appears. The honest replacement is in
`frozen-artifact.md`: `minClusterSize = 55` is a budget choice licensed by the measured
flatness of discriminative power, not a constraint the geometry imposed.

### Residual difference, stated rather than papered over

`routeToVmfs` is a hard argmax; the trickler is soft, with a beam and multi-membership. A
child's production population is therefore **greater than or equal to** its hard-argmax
population here. The check is now conservative in the right direction rather than biased in
an arbitrary one. It is not exact equivalence, and no document should claim it is.

## Search closure

`grep` over `src/` confirms the only remaining occurrence of the per-child normaliser is
the `VmfParameters` data-class declaration itself — no comparison site reads it. Both
instances are fixed; there is no third.

## The general form — state this in the thesis

> In a hierarchical von Mises-Fisher model, any comparison **across** nodes must be made
> at a shared concentration. Per-child normalisers are correct for a density and wrong for
> a decision: they bias assignment toward the concentrated sibling by tens of nats at
> d = 256, and the bias is directional rather than noisy, so it survives averaging and
> shows up as a systematic structural distortion rather than as variance.

Two corollaries the project paid for separately:

* Because `kappa` is fitted with an n-dependent shrinkage, comparing *levels* by density is
  worse than comparing siblings by density: parents always look sharper. This is why the
  descent gate is a direction-only Jensen-tight bound and not a likelihood ratio.
* A gate whose stated justification is "the same rule as X" is a maintenance liability. It
  needs to *be* the same expression, or a test that fails when the two drift. This defect
  survived a redesign that explicitly fixed the identical bug 30 metres away in the call
  graph.

## Convergence status of the mcs=30 observation

The 152-leaf run quoted above reported `CERTIFIED: false` at iteration 19. The leaf curve
was +27, +43, +36, +15, +1 then flat from iteration 6 — a cascade that finished, not
growth still climbing; iterations 7-19 added one leaf. J alternates 0.287671 / 0.287673, a
2e-6 oscillation against `tau = 1e-6`, i.e. a tolerance-scale limit cycle that a longer run
will not close. **152 leaves / J 0.287671 is an observation, not a certified artifact**, and
must be cited as such. The frozen artifact is the mcs=55 build (`frozen-artifact.md`).

Arena viability of the finer tree was checked and is favourable: at 152 leaves, 0 leaves
fall below the 12-held-out-query requirement (min 13, median 22). The cost was reported as
reliability — median `r = n/(n+7.66)` falling 0.842 -> 0.745 — which is why the
evaluative-redundancy analysis was recomputed rather than carried across.

**Corrected 2026-07-30.** That constant is 3.04x too large; the refit value is `c = 2.52`
(`measurement-discipline.md`). At 2.52 the reliability gap between 87 and 152 leaves is much
smaller than 0.842 -> 0.745 suggested, so the *stated reason* for recomputing weakens. The
recomputation itself was still right, for the `c381211` reason. Do not quote either figure.
