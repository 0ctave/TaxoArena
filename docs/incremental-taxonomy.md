# The batch artifact is the stationary limit of an incremental system

Status: **current**. Material for Discussion / Future Work. Everything here is either
already implemented or a named, costed experiment — nothing in this document is a
speculative extension.

## The claim

The frozen taxonomy is a batch object, but the system that produces it was designed to be
**incremental**. Three design decisions exist only for that reason and are otherwise
unmotivated:

1. **Residual retention.** A query that reaches no leaf is kept at the node the walk
   converged to, with full weight, its embedding, and a residual flag — rather than being
   dropped or force-assigned. In a batch run its only visible effects are mass conservation
   and an extra J-cell. Its actual purpose is that unexplained mass must survive to be
   *re-examined* when more of it arrives.
2. **Anchor invariance.** The depth-1 anchors are unprunable (constraint C4). In a batch
   run this is a mild structural restriction. In an incremental one it is the point: it
   gives arriving queries a **fixed reference frame**, so a taxonomy after 20k queries is
   comparable to the same taxonomy after 8k rather than being a different object with
   coincidentally similar labels.
3. **Routing / generation separation.** Routing a query and generating structure are
   distinct operations with distinct gates. A new query can be routed without proposing any
   edit; an edit is proposed only when residual mass justifies it. Batch construction never
   exercises the separation, because every query is present from the start.

So the honest framing is not "we built a batch clusterer and might extend it later". It is:
*the batch artifact is the stationary limit of an online operator, and the fixed-point
certificate is the statement that the limit was reached.*

## `descentMargin` is a mode selector

`descentMargin` (delta) is the slack below the Jensen-tight descent bar:

```
descend iff   max_c <mu_c, x>  >=  (r_v - delta) * <mu_v, x>
```

At delta = 0 the test is the tight bound: a query is residual only when its best child does
worse than the children's own weighted-average alignment — genuinely unexplained mass.
Raising delta forces descent that the bound does not support, converting would-be residuals
into leaf population.

There are two justified operating points, and they correspond to two modes of the system,
not to a tuning curve with an optimum:

| mode | delta | residuals | routing | what it is for |
|---|---:|---|---|---|
| **discovery off, routing optimal** | 0.12 | ~0 across the tree | best measured | the reported batch artifact |
| **discovery on** | ~0 | 756 queries = 9.1% of the corpus | ~5 points worse | streaming / arrival of new queries |

Do not present 0.12 as "the tuned value". It is the setting under which the reported
artifact is a *routing* object rather than a *discovery* object, and the thesis should say
which mode each number was produced in.

Note also that at delta = 0.12 all nodes of the frozen tree carry **zero** residuals, which
makes several residual-dependent code paths unreachable in the reported configuration —
including the diffuse-residual split branch and the doubled small-node separation bar. See
`known-defects.md`.

## Why the corpus forces delta = 0.12 here — and why that dissolves

The tension is arithmetic, not conceptual. At 8299 construction queries and 87 cells:

* median cell holds 88 queries;
* a 9.1% residual reserve costs about **8.7 queries per cell**;
* cells near the `minClusterSize = 55` floor would be pushed toward or below it, and the
  floor is a birth constraint that re-routing already violates for ~1% of leaves
  (`frozen-artifact.md`).

So at this corpus size, discovery mode is bought by degrading the cells the arena depends
on. That is a real constraint and it is why the reported artifact runs at delta = 0.12.

**But the constraint is a corpus-size constraint, and it relaxes monotonically.** The
reserve is a fixed *fraction*; the per-cell budget is an absolute count. Doubling the corpus
at fixed cell count doubles the per-cell margin above the floor while the reserve fraction
stays put. The setting where discovery matters — a corpus that keeps growing — is exactly
the setting where the reason to switch it off disappears.

That is the Discussion paragraph: not "delta = 0 was worse", but *"delta = 0 is the mode
this system is for, and the only reason it is not the reported setting is a corpus-size
constraint that the incremental setting removes by definition."*

## The cheap experiment that would test it: hold-out-a-domain

Construct on 13 of the 14 MMLU-Pro domains. Stream the 14th in as arrivals. Measure
recovery: does the held-out domain's mass accumulate as residual, does the residual pool
carve children, and do those children correspond to the held-out domain's structure?

Why this is the right test:

* It uses the mechanism end-to-end (retention -> residual accumulation -> residual split)
  rather than testing a component in isolation.
* It has a ground-truth target — the held-out domain's own taxonomy from a full-corpus run
  — so recovery is measurable rather than eyeballed.
* Anchor invariance is what makes the comparison legal: the 13 retained anchors are fixed,
  so the two trees are the same object with one branch added.
* It costs one construction run plus one streaming pass. No arena, no judge calls, no Azure.

**It MUST be run at delta ~ 0, or it fails by construction.** At delta = 0.12 the held-out
domain's queries are forced down into existing branches and never accumulate as residual
mass, so there is nothing for the discovery mechanism to act on. A hold-out experiment at
the reported artifact's setting would produce a clean, meaningless null — which is exactly
the failure mode catalogued as finding 4 in `transferable-findings.md`.

Pre-register the recovery criterion before running it.

## Open, not claimed

Nothing in this document is evidence that the incremental mode works. It is evidence that
the system was *built* for it, plus a design of the experiment that would test it. The
hold-out experiment has not been run.
