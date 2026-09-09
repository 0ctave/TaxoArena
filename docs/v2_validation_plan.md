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

## D1 — slice width and within-node anisotropy (dimension sweep; registered 2026-09-08)
Question: does the MRL slice width, or removing a node's dominant shared directions
before the split proposal, change how much CERTIFIABLE sub-anchor structure the
construction finds? Motivation: the within-node null runs 3x the isotropic null
(shared dominant directions, not dimensionality per se), and the repo's own MRL
ladder (128 at the root) was abandoned for costing coarse-level accuracy.
Arms, 2 seeds each (137, 2048; body = p7_det_1, labeling off, structure only):
  d128 / d256 (baseline) / d512 — `embeddingSliceDim`;
  abt2 — 256 with the top-2 within-node principal components dropped before EM
  (`splitDropTopPcs = 2`, all-but-the-top); white — 256 with variance-whitened PCA
  coordinates before EM (`splitWhiten = true`). Both PCA variants act on the PROPOSAL
  only; routing, vMF fits and the separation gate stay on the raw slice.
Bar 0.025 flat in every arm. Registered confound: the isotropic null scales with the
width, so the same bar is looser at 128 and tighter at 512 — measured by
`gradlew isoNullByDim` (n = 130/406/900, 300 reps) and reported alongside; the
primary metric below is self-calibrated per arm and does not depend on it.
Metrics per build: (a) site-level certification count (`gradlew siteNull` at the
arm's own geometry, 300 reps, on the build's own snapshot; CSV per build under
experiment_results/dimsweep/); (b) cross-seed ARI of nearest-leaf-centroid train
assignments (P1 metric; baseline 0.663); (c) held-out Top-1 with Wilson CI;
(d) Philosophy leaf count and (e) leaf count, descriptive.
GATE: d256_s137 must reproduce experiment_results/p7_det_1's dag_snapshots.jsonl
hash — the refactor that made the width configurable must be a no-op at 256/0/false
or the sweep is void until it is.
REGISTERED PRIMARY (per arm vs d256): an arm IMPROVES granularity coherence iff
(a) exceeds d256's count in BOTH seeds AND (c)'s Wilson CI overlaps d256's in both
seeds AND (b) >= ARI(d256) - 0.02. Any other pattern = NO IMPROVEMENT.
PREDICTIONS (committed before launch): d128 loses certifications and Top-1; d512
changes little; abt2 and white are the only arms that can raise (a). Because they
change the proposal only, a null there is informative: it says the acceptance
geometry (raw-slice routing + min-pair gate), not the proposal, is the bottleneck,
which is the premise for a stage-2 representation-level whitening arm (pre-authorized
"more complex dimension management", to be registered separately if reached).
Readout: tools/analysis/dimsweep_report.py.
SPLIT HYGIENE (added 2026-09-08 mid-sweep, no design change): each arm builds on its
OWN seed split (splitSeed = seed), so ~69% of the frozen arena pool p2dca21ab5f4ef3ae
sits on these trees' TRAIN side and every build ACTIVATES its own pool in the dataset
DB. Consequences: (i) sweep trees are structural evidence only — any arm promoted to
arena use must be rebuilt with splitSeed = 42 (the frozen split) and its rubrics induced
in that run; (ii) after the chain, the frozen pool is re-pinned
(`tools/analysis/pool_guard.py --activate`) before any judged run or is_reserved-based
analysis. The metrics above are unaffected (site nulls use the build's own train
population; Top-1 uses the build's own held-out split; ARI uses questions outside the
frozen pool).

## D2 — stage-2 dimension sweep (registered 2026-09-09, before launch)
Arms, seeds 137 / 2048, body = D1: abt2d512 (`embeddingSliceDim 512`, `splitDropTopPcs
2`), bareq512 (512 dims, bar 0.0145 = 0.025 x isotropic-null ratio 0.0040/0.0069 — the
bar-equalized control for d512), abt1 (256 dims, `splitDropTopPcs 1` — dose-response).
Metrics: D1's (site-level certification at the arm's geometry, Top-1, cross-seed ARI,
Philosophy leaves) plus F6's key-only leaf-level LOO Brier vs the frozen tree.
REGISTERED: (i) bareq512 — the d512 certification gain is NOT a bar artefact iff
bareq512's certified count >= d256's (7, 9) in both seeds; (ii) abt2d512 IMPROVES iff its
certified count > d512's (13, 13) in both seeds AND its F6 leaf-level loss vs frozen is
>= −0.5 (x1000) — i.e. it certifies more without abt2's capability-information loss;
(iii) abt1 descriptive. Predictions: (i) holds (width effect real, with more leaves than
d512); (ii) FAILS on the F6 clause — abt2's loss is the leaf count, and abt2d512 will
also have ~60 leaves. Split hygiene as D1 (structural evidence only; splitSeed = 42
rebuild before any arena use); frozen pool re-pinned by the chain itself at the end.

## OUTCOMES (updated as tests adjudicate)

- P6 (2026-09-08): **NULL — overlap program closed, soft routing vindicated.** Full pool
  n = 3,599: D = (F−T) − (Pf−T) mean +0.1987, CI [+0.0495, +0.3478], but exact sign test
  p = 0.0923 with a NEGATIVE nonzero majority (+1007/−1085) — the conjunctive criterion
  fails. Both arms hurt the tree outright: F−T −0.728 (p 3.9e-22), Pf−T −0.927 (p 3.3e-17);
  every real pair negative on its own subset (Thermo, the largest twin, −6.85). Fusion
  implemented as the labeled QUERY-MOVE variant (no cross-anchor parent redirect).
  Artifacts: E2FusionRunner.kt, scripts/e2_fusion_analysis.py,
  experiment_configs/p6_fusion_registration.md, experiment_results/e2_fusion/. With E1+E2
  this closes every structural response to overlap (edge, bridge, merge); E3 stays unrun
  per the registered sequence.

- P1 (2026-09-08): **FALSIFIED** by the registered primary. Disjoint-half consensus
  ARI = 0.6533 (bar >= 0.90, falsifier < 0.80), vs baseline mean pairwise build ARI
  0.663 (0.585-0.704) — consensus over 10 builds agrees across halves NO BETTER than
  two individual seed builds. The v1 procedure (nearest-centroid assignments,
  average-linkage at co-assignment 0.6, min-cell 55 merges) does not stabilize leaf
  identity; the instability does not average out at B=10. Full-consensus descriptives:
  67 cells, size median 88. Artifacts: tools/analysis/consensus_tree.py,
  experiment_results/consensus_p1_report.txt, consensus_cells_v1.json. Possible
  procedure variants (higher B, co-assignment-weighted warm start, different cut)
  remain open but are NEW proposals needing their own registrations; P1 as designed
  is dead and the v2 recipe reorders around P2.

- P7 (2026-09-08): SPLIT VERDICT. Structure is bit-reproducible (dag_snapshots.jsonl
  hash-identical across two same-config builds at HEAD) — the core claim PASSES.
  The full byte-diff FAILS on 7 files, decomposing into: (i) JBootstrap SE column in
  proposals.csv differs at the 4th significant digit (deltaJ and decisions identical)
  — the paired bootstrap's capture iteration is not order-stable despite its fixed
  seed; (ii) trickle/routing/quality validation CSVs differ — evaluation-path float
  accumulation, the same family as the disclosed 0.9pp July-vs-HEAD Top-1 drift;
  (iii) timestamps (benign). Work items: sort JBootstrap capture iteration;
  deterministic accumulation in trickle validation; strip volatile fields from the
  gate's file set. Artifacts: experiment_results/p7_det_{1,2}/, p7 chain log.
  Also: the embeddinggemma arm failed twice on an Ollama-internal socket-exhaustion
  error (its runner, not our code); parked — nomic already carries the
  second-embedder axis (75 leaves, Top-1 0.716, Philosophy splits x4).

- P2 (2026-09-08): **FALSIFIED on both registered checks** (`gradlew siteNull`, 300 reps
  per site per arm; table `docs/data/site_null_frozen.csv`; full readout in
  `docs/separation_null_by_size.md` "SITE-LEVEL (2026-09-08)"). (a) power check FAIL —
  the deflated null certifies CS depth-1 (q_defl=0.043) but ALSO Philosophy depth-1, at
  exactly q_defl=0.050 (obs 0.03188 vs deflated p95 0.03162); at 300 reps the two q's are
  statistically indistinguishable (binomial SE ~0.013), so the construction lacks the
  registered discrimination — substantive, not a rounding accident. Philosophy's second
  site stays uncertified (0.257) as required. (b) trunk viability FAIL — matched
  site-level nulls certify 6/66 (9%): Chemistry 0.000, Biology 0.000, Math 0.013,
  Engineering 0.013, Business 0.027 (depth 1) + one depth-4 Math site (0.047); the
  registered falsifier (< 15: "trunk tier too thin; strata absorb its role") fires even
  though Chemistry and Biology certify as required. The anchor-level 35% clear was
  confirmed as an upper bound (collapses 4x under matched nulls). CERTIFIED TRUNK =
  {Chemistry, Math, Business, Engineering, Biology} depth-1 splits only; the drift clause
  is moot and unmeasured (offline geometry, no routing arm). Downstream: P3's candidate
  twig set must be re-derived against this 5-site trunk or its gate redesigned; P5's
  strata inherit the trunk tier's measurement role. Deflated null survives as a
  per-site diagnostic (q's in the CSV), not as the CS-vs-Philosophy discriminator;
  dip-test / mixture-BIC variants are unregistered future work.

- D1 (2026-09-08, registered 523b85d; gate PASSED — d256_s137 hash-identical to
  p7_det_1; tables experiment_results/dimsweep/site_null_<arm>_s<seed>.csv, report.txt,
  iso_null_by_dim.out; frozen pool re-pinned after the chain):
  **d512 IMPROVES (prediction "changes little" WRONG); d128, abt2, white NO IMPROVEMENT.**

  | arm | leaves | certified sites | trunk anchors | Top-1 | cross-seed ARI |
  |---|---|---|---|---|---|
  | d256 (base) | 84 / 83 | 7/60, 9/65 | 5, 7 | 0.737, 0.749 | 0.678 |
  | d128 | 95 / 94 | 5/75, 3/76 | 2, 2 | 0.719, 0.729 | 0.580 |
  | d512 | 75 / 84 | 13/54, 13/57 | 7, 7 | 0.747, 0.771 | 0.679 |
  | abt2 | 63 / 61 | 17/27, 18/25 | 15, 18 | 0.731, 0.755 | 0.657 |
  | white | 20 / 17 | 2/5, 1/3 | 2, 1 | 0.734, 0.744 | 0.756 |

  d128: more leaves, fewer certified, trunk collapses to Engineering+Math, Top-1 -2pp,
  ARI -0.10 — fewer dimensions manufacture noise splits (the MRL tail carries signal).
  d512: fewer splits, twice the certified count, trunk 7/7 (Law and Physics join),
  Top-1 up, ARI unchanged — passes all three clauses. Confound (registered): isotropic
  p95 at n=406 is 0.0115 / 0.0069 / 0.0040 at 128 / 256 / 512 dims, so the flat bar is
  2.2x / 3.6x / 6.2x the noise floor — 512 runs a stricter effective bar, which prunes
  but cannot by itself ADD certified sites (13 vs 7-9). A bar-equalized 512 arm
  (bar ~0.0145) is the stage-2 test that separates width from bar.
  abt2 (top-2 within-node PCs dropped before EM, geometry unchanged so NO bar
  confound): 63-72% of accepted sites certify (vs 12-14% baseline), trunk 15-18 of 14
  anchors' worth of sites INCLUDING Philosophy depth-1 in both seeds — the first arm ever
  to certify a Philosophy split; Top-1 within CI; ARI 0.6566 vs floor 0.6575 — misses
  the registered clause by 0.001 and is adjudicated NO IMPROVEMENT as registered.
  ARI across trees of different leaf counts is a blunt stability metric; this is the
  arm with the strongest signal in the sweep and the obvious stage-2 registration
  (abt1 / abt3, abt2 x 512 dims, bar-equalized).
  white: variance-whitened proposals almost never survive the raw-geometry gate —
  5 and 3 accepted splits, 20/17 leaves; ARI 0.756 is the stability of a near-stump.
  Confirms the proposal-only design's premise the other way: the acceptance geometry,
  not the proposal, is the binding constraint, and only proposals that stay compatible
  with it (abt2) get through.
  Split hygiene: all ten trees are structural evidence only (own-seed splits); any arm
  promoted to arena use is rebuilt with splitSeed = 42.

- LADDER (2026-09-08, registered 4c4e5e7): **PRIMARY FAILS — the specificity curve
  is not monotone.** generic 0.761 < anchor 0.774 > stratum 0.757 < leaf 0.770
  (n=967 fully paired); leaf-vs-anchor 35:38 discordant, p=0.68. Anchor-level
  induced rubrics match leaf rubrics and beat generic; the knee sits at or before
  ANCHOR granularity. No contradiction with the confirmed cell>generic (p=0.0001)
  and cell>wrong-cell (p=0.006) results: rubric value = domain-correct content,
  wrong specificity harms, finer-than-anchor right specificity adds ~nothing here.
  Old-vs-fresh session confound disclosed (leaf/generic arms reused as registered).
  Consequence: P3's twig gate loses its premise as designed; a same-session leaf
  re-judge (~4k calls) is the follow-up if the knee needs settling.
