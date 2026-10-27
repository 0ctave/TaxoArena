# TaxoArena v2 Construction — Improvement Proposals

(Design review, 2026-09-08, grounded in: test_ledger, h9_sweep registration/outcome +
stability_all, h9_adaptive outcome + quantile curve, separation_null_by_size CURRENT +
within_null_frozen_{anchors,splits}.csv, e2_registration + e1 overlap, x12_profile
outcomes, rubric_contrast + rubric_swap outcomes, and the construction code audit.)

## 0. Record checks (fixed alongside this commit)

1. `stability_all.txt` ended with an un-annotated `alpha ... FAIL` line — a script-scope
   artifact (spread computed over all 34 arms incl. bar-collapse runs, which the
   registered alpha never covered). Annotated in the file; registered adjudication
   stands (seed arms: PASS 1.6pp / n=20 descriptive 2.6pp).
2. Seed mu-match range is 62–79/87 = 71–91% (earlier notes said 71–85%).
3. The old memory note "within-domain null 0.068–0.130" refers to VOIDED mcs=30
   per-site values; current anchor-level band is p95 0.029–0.075.
4. All other campaign numbers verified against the repo record.

## 1. Three syntheses

**S1 — Certification-by-greedy-gating destroys certifiable structure** (the buried
headline of h9_adaptive). The frozen Chemistry depth-1 split (k=3, sep 0.0968) clears
Chemistry's honest p95 (0.0663) at q=0.000 — among the best-certified splits in the
artifact. Yet the adaptive run, gating in-loop at exactly that p95, left Chemistry
UNSPLIT (same for Biology, q=0.000). The greedy fixed point is order/seed-dependent in
its proposal stream, so raising the in-loop bar does not select the certified subset of
the good tree — it makes the greedy wander to a different object (mu-match 30/87).
Conclusion: certify by POST-HOC scoring and pruning of a permissively built tree, never
by in-loop gating. The adaptive run's "structure concentrates where nulls are tight" is
therefore partly a search artifact.

**S2 — Routing saturates at ~20 cells; the lower tree exists for rubrics, and rubric
value anti-correlates with geometric certifiability.** Bar 0.045+ collapses to 16–20
leaves at only 2–4.6pp Top-1 cost; beam/descent inert; Top-1 flat across mcs 30–75.
Rubric value is real, cell-level (cell > sibling ~ random, p=0.006), and largest
exactly where geometry certifies nothing (Philosophy: q=1.0000 at both split sites,
+5.7pp rubric gain). The lower tree's validation currency must be judging performance,
not separation or Top-1. This licenses a purpose-split construction.

**S3 — Leaf identity is a sample draw, and several E1 overlap pairs are the same draw's
duplicates.** Seeds move mu-match to 62–79/87 while anchors/routing are invariant. The
E1 top pairs (Thermo–Thermo across Chem/Engineering; two quantum-duality leaves; the
statistics pair split across Math/CS by benchmark-label contamination) read as TWIN
LEAVES the greedy instantiated twice — the seed-instability phenomenon materialized
inside one tree. E2 says bridging them hurts. The right response to both findings is
one mechanism: consensus over draws plus fusion of twins — not edges.

## 2. Proposals

### P1 — Consensus (stability-selection) construction
- Exploits: leaf identity as a sample draw (20 seed builds already on disk; 2 embedder
  builds add a second consensus axis).
- Mechanism: anchors fixed; per anchor, form the query–query co-assignment matrix over
  B permissive builds; cut at consensus >= ~0.6 (average linkage) to define consensus
  cells; warm-start ONE final standard fixed-point run at the frozen config so the
  artifact stays a certified J-stationary object. Twin leaves merge automatically.
  Never implement via `seeds = [...]` (multi-seed loop corrupts routing) — separate
  runs only.
- Prediction (falsifiable): consensus trees from DISJOINT 10-seed halves agree at
  mu-match >= 95% (baseline 71–91% pairwise); Top-1 stays >= 0.750; E1 twin-pair share
  drops. Falsified if disjoint-half mu-match <= 85%.
- Cost M (local; builds exist). Registered test: consensus reproducibility as above.

### P2 — Certify by pruning: per-SITE honest nulls applied post-hoc
- Fixes: S1; anchor-null anti-conservatism for deep sites ("35% clear" is an upper
  bound); the elongation caveat (CS worked example).
- Mechanism: build permissively (or take P1's tree); offline, run SITE-level
  anisotropy-preserving nulls at every accepted split (extend `gradlew withinNull`
  from anchors to sites); add a DEFLATED null (split-direction projected out of the
  covariance) or dip-test/mixture-BIC to separate texture from real heterogeneity the
  elongated null can't see — this adjudicates whether Philosophy's q=1.0 is
  Philosophy-is-smooth or CS-style contamination; mark certification flags; the
  CERTIFIED TRUNK is the maximal all-certified prefix — a VIEW, nothing deleted, so
  certified and functional trees stay mu-consistent (unlike adaptive, 30/87).
- Predictions: the trunk RETAINS Chemistry/Biology/Engineering/Math depth-1 splits the
  adaptive greedy lost (~30–55 leaves); falsified if site-level nulls certify < 15
  splits (trunk tier too thin; strata absorb its role). Deflated-null power check: it
  must certify the CS contamination split while leaving Philosophy uncertified.
- Cost S–M (offline, no judge calls). Registered test: freeze procedure + falsifiers +
  trunk drift <= 0.5pp, trunk Top-1 in seed floor.

### P3 — Purpose-split two-stage tree: certified trunk + functionally gated twigs
- Exploits S2. Trunk gate = statistical (P2). Twig gate = FUNCTIONAL, three parts:
  (1) support >= rubric-induction floor (P5); (2) cheap in-loop proxy: induced child
  rubrics non-redundant (pairwise rubric-embedding distance above a floor calibrated so
  sibling-swap rubrics fail); (3) behavioral gain, batched POST-HOC, never in-loop: on
  a probe set of key-decidable reserved questions, twig rubric beats the PARENT's
  rubric (rubric_swap design one level down).
- Circularity control: gate 3 scores against the GT KEY (key-decidable subset), and
  probe questions are BURNED (excluded from later measurement runs).
- Prediction: kept twigs replicate a positive cell-vs-parent McNemar on a fresh probe
  draw; rejected twigs ~ 0. Philosophy keeps 2–4 twigs under the functional gate
  despite q=1.0 geometry — and if it does not, the +5.7pp gain was anchor-level and
  the twig tier under Philosophy should die; either outcome is informative.
- Cost L but bounded/one-shot: ~60–90 candidate twigs x ~100 probe matches x 2 orders
  ~ 15–20k judge calls (one overnight, R2-scale). Registered test: the gate-3 batch
  itself (frozen sampling/filters, one-sided McNemar per twig, FDR 10%; pooled
  kept-twig gain > 0 on a fresh draw as secondary).

### P4 — Held-out routing likelihood as the acceptance statistic (v2.1)
- Fixes: J provably blind above leaves and anti-selective on ambiguous mass; the bar
  controls only isotropic false positives (accept% ~ 100% under every anchor's
  anisotropic null). E2 already built the better statistic: per-question
  ll(q) = logSumExp over reached leaves [log path mass + vMF log density].
- Mechanism: keep J's gate as prefilter; accept an edit iff delta-ll >= 0 (small
  z-margin) on a construction-validation fold carved from the TRAIN side (never the
  reserved pool); ll-stationarity replaces J-stationarity. E2BridgeRunner computes the
  metric; wire it into TaxonomyOperations acceptance.
- Prediction: ll-gated splits have higher cross-seed recurrence than J-only splits;
  falsified if recurrence is no better. ll may refuse deep twigs — fine (trunk
  objective; twigs are P3's).
- Cost M. Sequence AFTER P1/P2 provide a stable comparison baseline.

### P5 — Support-aware sizing from the k/S^2 law
- Exploits H6b: q >= k/S^2 (k ~ 2–4 theta^2), deff median 2.0x (worst 3.7x); R2 honest
  query-level SEs ran 0.14–0.245 against the 0.15 match-level target.
- Mechanism, three derived floors replacing conventions: strata reserved floor
  >= deff x k/S^2 ~ 240–380 reserved questions (change build_profile_strata.py's
  ">= 100" rule; merges the thinnest strata, ~20 -> ~14–17); leaf/twig floor set by
  rubric-induction stability, determined empirically by subsampled induction
  (n in {30,45,55,70}) scored on self-consistency + probe accuracy (leaves carry no
  theta claims, so k/S^2 does not bind them); trunk-certified nodes n >= 160 so the
  honest null is a genuine conditional quantile.
- Prediction: with derived floors, the next profile run lands query-level SE <= 0.15
  in EVERY stratum at <= 1.25x the R2 verdict budget. Cost S; rides on that run.

### P6 — Overlap: fuse twins, keep soft routing; E3 stays a cheap post-script
- Findings: E1 real+concentrated; E2 bridges lose to placebo; S3 twins.
- Mechanism: P1 absorbs within-anchor twins; add a CROSS-ANCHOR fusion check (current
  fusionSimilarityThreshold=0.90 sees only same-parent siblings, so the E1 cross-anchor
  pairs are structurally invisible to it) — score E1 top pairs for FUSION (merge +
  re-route) under the E2 metric with placebo-fusion control; the Math/CS statistics
  pair is ingest-label contamination (text-based relabeling, not topology); the
  residual stays on soft routing.
- Prediction: fusing the top-3 cross-anchor twins improves held-out ll where bridging
  degraded it; if fusion also loses to placebo, soft routing is fully vindicated and
  the overlap program closes. E3 (shared-child extraction) only if fusion signals;
  E2 harness verbatim, one afternoon, prior ~70% null.
- Cost S. Registered E2-style two-sided test.

### P7 — Determinism CI + config-surface reduction (gates everything)
- Findings: the disclosed 0.9pp same-config Top-1 drift across code versions at
  mu-match 87/87 (identical structure, drifted evaluation); beam/descent proven inert.
- Mechanism: promote the H9b byte-diff CI to a merge gate; hard-pin/remove
  routingBeamGamma + descentMargin from the swept surface; (done in this commit)
  annotate the stability_all alpha line.
- Without this, every v2 comparison inherits a +/-0.9pp unexplained noise floor that
  eats half the seed band. Cost S.

## 3. Recommended v2 recipe (build order)

| # | Change | Why this order | Cost | Validation spend |
|---|---|---|---|---|
| 1 | P7 determinism CI + inert-knob removal | downstream deltas are smaller than the current unexplained drift | S | none |
| 2 | P1 consensus over the existing 20 seed builds (+2 embedders) | fixes the largest measured pathology with artifacts already on disk | M | local; 1 registered test |
| 3 | P2 site + deflated-null certification by pruning on the consensus tree | trunk as a view; keeps Chemistry/Biology | S–M | local; 1 registered test |
| 4 | P5 support-derived floors | analysis change; adjudicated free on next profile run | S | rider |
| 5 | P3 functional twig gate | the only judge spend; doubles as validation of the two-stage idea | L | ~15–20k calls |

Deferred: P4 (ll objective) as v2.1 after the consensus/pruning baseline is stable;
P6 fusion arm whenever an afternoon of E2-harness time is free.
Total v2 validation budget: 3 registered local tests + 1 rider + one overnight judge
run — roughly one R2 of spend for the whole recipe.

## 4. DON'T list — changes the evidence argues against

- No DAGs / bridges (E2 decisive, placebo-controlled negative; soft routing carries
  the overlap; E3 moot unless the fusion arm signals).
- No in-loop honest-null gating, per-anchor or per-site (h9_adaptive loses q=0.000
  structure; certify by pruning).
- No global bar >= 0.045 for the functional tree (amputates the rubric tier exactly
  where its value is proven; the coarse tree is a VIEW, never the artifact).
- Never tune routingBeamGamma / descentMargin again (bit-identical outputs; Top-1
  provably beam-invariant).
- Don't re-litigate the z-gate (z0 vs z=2: +/-3 marginal leaves, Top-1 unchanged).
- Don't bless a seed; consensus uses the variance a pinned seed would hide. Never via
  `seeds = [...]` in one config.
- No judge inside the construction loop (batched post-hoc gates only; GT-key-anchored,
  burned probes are the circularity circuit breaker; recall the 17% peek reversal).
- Don't spend more optimization pressure on J as-is (blind above leaves,
  anti-selective on ambiguous mass; repair via P4 or demote to prefilter).
- Don't treat the adaptive-p95 35-leaf tree as "the frozen tree, certified" — it is a
  different object (mu-match 30/87) and its structure pattern is partly a search
  artifact (S1). The quantile curve is a measured trade worth citing; those trees are
  not v2 candidates.
