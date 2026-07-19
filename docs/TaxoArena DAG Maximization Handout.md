# TaxoArena — DAG Maximization Implementation Handout

**Goal:** Maximize the DAG structure so it can express cross-domain bridging parent nodes (e.g. a "Biomedical" node parenting both a Health leaf and a Biology leaf), surface the "missing child domain" signal that is currently silently lost, and fix the data-model coherence issues that would otherwise make that signal noisy. All new behavior is gated behind **independent flags** (`enableStableQuestionIds`, `enableResidualRouting`, `enableResidualSplitGate`, `enableBridging`) so that with all flags off the pipeline matches the baseline except for explicitly intended, documented corrections.

**Repo:** https://github.com/0ctave/TaxoArena · **Base commit:** latest `main` (`41143e2` or newer) · **Language:** Kotlin/JVM.

**Scope of this handout:** implement Phases 0–4 below, in order. Each phase lists exact file:line targets (verified against `41143e2`), new parameters, guard rails, and pitfalls. Phase 5 is verification.

---

## Design decisions (already validated — do NOT re-litigate)

1. **Post-hoc insertion, not split-time.** Bridges are created by a bounded pass over the *completed, stable* tree, not by entangling the top-down splitter. Rationale: the splitter is intra-subtree, single-`treeParentId`, `queries.clear()`-on-split; making it emit shared children would corrupt depth accounting and risk both failure modes during recursion.
2. **Bridges are query-less internal nodes stored off the `children` backbone** (via the existing `crossLinkChildren` channel). This is the structural guarantee against degeneration (a query-less node cannot swallow the corpus) AND keeps the trickler, arena (leaf-only), migration matrix, and depth metrics byte-for-byte unchanged.
3. **Two detection sources feed one consumer.** Bridging candidates come from (a) cross-domain leaf pairs in a vMF JS-divergence adjacency band, AND (b) coherent residual sub-clusters accumulated at internal nodes. Both feed the same `insertBridgingParents` pass with the same guard rails.
4. **The residual signal is the missing-child detector.** Today routing is a forced softmax (Laplace-smoothed, no threshold) → `NoMatchRate=0.0` is an artifact. We add a pre-smoothing confidence gate so dead-end mass becomes a real, countable signal that (i) is excluded from the parent's κ fit (fixing the diffusion pollution) and (ii) seeds bridging children.
5. **Universal serialized `question_id` is the prerequisite.** Residual tracking, bridging, and the DAG↔arena join all require stable identity; today identity degrades to non-serialized `rawText`. Do Phase 0 first.
6. **Depth-1 preservation invariant is sacred.** The 14 editorial MMLU-Pro domains remain the depth-1 layer. Bridges sit *below* depth 1, never above/among them, and never touch `root.children`.
7. **No ground-truth leakage into splitting.** The split decision is pure geometry (vMF k-means + Dasgupta delta). Do NOT introduce GT-domain purity into the split or the bridging decision (bridging uses GT-domain entropy only as a *guard rail* on the union, never as a selection criterion).

---

## Phase 0 — Universal serialized query identity (PREREQUISITE)

Do this first; every later phase depends on stable identity. Gated behind `enableStableQuestionIds` (default false). Note: even with this flag off, the migration to stable IDs is a *correction* — soft-membership double-counting and text-fragile joins are bugs being fixed, so this phase's diffs are intentional and must be reported as migration deltas, not regressions.

### 0.1 Make `question_id` the universal key
- **`model/GraphNode.kt:178-215` (`assignQueryIds`):** replace the sequential-int-by-`rawText`-dedup assignment with the MMLU `question_id` carried on the `Embedding`. If a row has no `question_id`, fall back to a stable hash of normalized text — never to a sequential counter.
- **`model/DataModels.kt:21-22`:** `queryId` is `@Transient` (not serialized) → after snapshot reload it is −1. Either serialize `question_id` on `Embedding` (preferred) or re-derive it deterministically on load. Remove the reload-to-−1 failure mode.
- **`model/DataModels.kt:29-40` (`Embedding.equals/hashCode`):** key on `question_id` (+ normalized text fallback), not raw `rawText`+values.

### 0.2 Normalize text once, everywhere
- **`runner/HeadlessBenchmarkRunner.kt:487` (`cleanText`):** currently applied only in the trickle path. Lift `cleanText` to a single shared normalizer used at embedding load, split, fit, snapshot, and the arena join. Two questions differing only by whitespace/encoding must collapse to one identity in ALL subsystems.

### 0.3 Two leaf-profile modes (fix the double-count, keep soft semantics)
- **`tui/service/BatchTrickleEvaluator.kt:61` (`buildLeafProfiles`):** today it iterates raw `leaf.queries` → a query in 1-3 leaves (soft membership, `assignmentGap=0.2`) inflates several leaves' domain histograms, purity, and `size`. Do NOT blindly dedup away the soft membership. Instead support two explicit modes:
  - **Partition profile:** each query counted once via top-1 / canonical membership → used for purity, `dominantDomain`, migration matrix, and all thesis metrics.
  - **Soft profile:** each query weighted by its route responsibility across its 1-3 leaves → used only for routing diagnostics / uncertainty analysis.
- Structural counts (`getAllQueriesInBranch`, `getRecursiveQueryCount` — already dedup at `GraphNode.kt:90-156`) and the **partition** profile must agree.

### 0.4 Fix the DAG↔arena join
- **`dataset/PrecomputedModelOutputLoader.kt:11-20`** (keys by `questionId`) vs **DAG routes by `rawText`** vs **`arena/ModelEvalStore.kt:373-399`** (`eval_question_link(question_id↔mmlu_pro_row_id↔has_embedding)`). Make the DAG↔arena bridge join on `question_id`, not text. Apply the shared `cleanText` only as a last-resort fallback.

### 0.5 Snapshot schema compatibility
- **`service/TaxonomySnapshotManager.kt`:** `isBridge`, bridge edges, residual traces, and the serialized `question_id` must survive save/load. Add a **snapshot schema version** and a backward-migration path for old snapshots that only have text identity (re-derive `question_id` from normalized text on load).

**Phase 0 acceptance:** a query is identifiable by one stable serialized `question_id` across split, fit, route, snapshot, arena, and migration matrix; the partition profile no longer double-counts soft-membership queries (soft profile preserved for diagnostics); no DAG↔arena join miss on whitespace/encoding differences; old snapshots migrate cleanly.

---

## Phase 1 — Residual signal: detect the missing-child mass

Turn the forced-softmax dead-end into a real, countable, κ-excluded signal. Gated behind `enableResidualRouting` (default false). **Critical: `routeQuery` must NOT mutate graph state during evaluation** — parallel trickle/eval would pollute snapshots and later runs.

### 1.1 Add the confidence gate (returns a RoutingResult, no mutation)
- **`operations/TaxonomyTrickler.kt:46-97` (`walk`):** before the Laplace-smoothed softmax over children (`:79-92`), compute the *pre-smoothing* best-child responsibility (vMF cosine / raw softmax max). When it falls below `routeConfidenceTau`, record a **residual hit** at that node (node id, query `question_id`, best-child score).
- Change `routeQuery` to return a **`RoutingResult(leaves, residualHits, trace)`** value object instead of mutating `GraphNode`.
  - **Construction mode** (`enableResidualRouting=true`): the runner accumulates `residualHits` into the per-node `residualQueries` set (1.2) — these feed Phase 2/3.
  - **Evaluation/trickle mode:** residuals are emitted to `*_routing_diagnostics` / a new `bridge_residuals.csv` only; the graph is never mutated. This keeps inference read-only.
  - The query is still routed (Top-1/Any-Match semantics stay comparable to today) BUT the low-confidence hit is now surfaced rather than silently force-assigned.
- **New param `routeConfidenceTau`** (default such that current behavior ≈ unchanged when `enableResidualRouting=false`).
- **Depth-1 residual rule:** do not treat weak routing at the root / depth-1 domain nodes as a missing-child signal (those are the frozen editorial domains). Residual creation starts at depth ≥ 2, or uses a separate (looser) threshold at depth 1.

### 1.2 Populate the vestigial residual fields (construction mode only)
- **`model/GraphNode.kt:33`:** the `queries` "residual unmapped/outlier queries" doc-comment is aspirational. Add a real `residualQueries: MutableSet<String>` storing **`question_id`s only** (not full embeddings — caps memory at scale; embeddings are re-resolvable by id) on internal nodes, populated by the construction-mode runner from 1.1.
- **`model/DataModels.kt:90-91`:** populate `residualQueries` count / `residualRatio` (currently dead) per node. Surface a real per-node and global `NoMatchRate` (distinct from the current forced-0.0 artifact).

### 1.3 Exclude residuals from the parent's κ fit (fixes the Part-2 pollution)
- **`fitter/TaxonomyFitter.kt:157-162, 177-180, 181-196`:** vMF μ/κ and NIW are fit from `node.queries` / `getAllQueriesInRegion()`. Ensure residual-tagged queries are **excluded from the parent's κ estimate** so orphan mass stops deflating κ and masking the signal.
  - Careful: residuals are still *train* queries and still belong to the parent's branch for structural purposes; the exclusion is specifically from the parent's *concentration* fit, so a missing child shows as a coherent residual cluster rather than as diffuse-κ noise.
  - If full exclusion destabilizes the existing κ-based split/route logic, alternative: fit κ on the non-residual subset AND record the residual mass separately, using the latter only as a split/bridge trigger.

**Phase 1 acceptance:** a query whose best-child responsibility is below `routeConfidenceTau` is recorded as a residual of that node, excluded from that node's κ, and `residualQueries`/`NoMatchRate` reflect reality (no longer a forced-0.0 artifact).

---

## Phase 2 — Residual-viability split gate (replace the missing-child-hiding skip)

Gated behind `enableResidualSplitGate` (default false). Depends on Phase 1.

### 2.1 Remove the size-based diffuse-node skip
- **`operations/TaxonomySplitter.kt:85-88`:**
  ```
  if (node.vmfKappa < 0.5 && node.queries.size < 10 * config.formalism.minClusterSize)  // = 400
      return  // "too diffuse"
  ```
  This skips splitting exactly the diffuse-but-modest nodes most likely to hide a missing child. Replace with a **residual-viability gate**: a diffuse node is allowed to split (or grow a bridging child) when its residual set contains a coherent sub-cluster of size ≥ `minClusterSize` that is angularly distinct from existing siblings (JS-divergence ≥ `separationEpsilon`).
- Keep the other gates intact: `size ≤ 2*minClusterSize` (`:78-79`), `depth ≥ maxDepth` (`:80-83`), child-floor `< minClusterSize` rejection (`:150-153`), Dasgupta delta (`:156-169`), sibling distinctness (`:174-189`).

### 2.2 Propose a new child from the residual cluster
- When the residual-viability gate fires, run vMF k-means / Dasgupta on the residual set to propose a new child (this is the existing split path, just unblocked for diffuse nodes with viable residuals). If the proposed child is cross-domain (spans 2 editorial domains), route it to the bridging consumer (Phase 3) rather than forcing it into one depth-1 subtree.

**Phase 2 acceptance:** a diffuse node with a coherent ≥`minClusterSize` residual sub-cluster can now split/grow a child; the `κ<0.5 && size<400` skip no longer suppresses the missing-child case.

---

## Phase 3 — Bridging-parent insertion (the consumer)

The core DAG-maximization step. New file **`operations/TaxonomyBridger.kt`** (or a method on `TaxonomyMerger`), invoked from **`operations/TaxonomyMerger.kt:36-50` (`optimizeHierarchy`)** between `mergeSimilarSiblings` and `transitiveReduction`.

### 3.1 Collect candidates (two sources)
- **Source A — cross-domain leaf pairs (adjacency band):** for every pair of leaves (or shallow subtree roots) whose `getDepth1Ancestor` domains differ, compute vMF JS-divergence at the **min common sliceDim** (reuse `StatisticsUtils.vmfJsDivergence` + `projectVector`, as `mergeSimilarSiblings:218-229` does). Keep pairs in the band `separationEpsilon < div < bridgeSeparationCeiling` (close enough to be adjacent, far enough not to be fused — `mergeSimilarSiblings` handles the `div < separationEpsilon` near-identical case).
- **Source B — residual sub-clusters:** coherent residual sets from Phase 1/2 that span 2 editorial domains (entropy-guarded, see 3.3).

### 3.2 Create the bridge node
For each accepted candidate group, create ONE internal `GraphNode` B:
- `depth = max(2, min(childDepths) - 1)` — a parent must be shallower than its children; never depth 1; if `min(childDepths) == 2`, either reject the bridge or store `bridgeDepth` as metadata only (do not put it in the tree `depth` used by `maxDepth`/Sackin).
- `vmf*`/`niw*` = size-weighted blend of members via `TaxonomyMerger.blendVmfAndNiw` — but at the **min common sliceDim** (see Pitfall P2).
- `queries` left **empty** (structural node — this is the degeneration guard).
- New field `isBridge: Boolean = true` on `GraphNode` (`model/GraphNode.kt`); label prefix `bridge::`.
- Wire B as a **shared parent off the `children` backbone**: `B.crossLinkChildren.add(leaf); leaf.parents.add(B)`. **Do NOT** add B or its edges to any `children` set. Give B its tree home under `root.crossLinkChildren` (or under both depth-1 domains as cross-link parents) — never under `root.children`.
- **Cycle prevention:** before adding any bridge edge, assert `B` is not already an ancestor of the leaf via existing edges (no parent cycles).

### 3.3 Guard rails
**Against DEGENERATION (giant mixed node):**
- Bridge holds no direct queries (primary structural guarantee).
- `bridgeSeparationCeiling` — only bridge pairs closer than this; far-apart domains (Law↔Chemistry) excluded.
- **Domain-pair guard uses ancestry, not true labels.** Prefer the depth-1 `treeParentId` / frozen editorial-domain ancestry of the member leaves as the "spans 2 domains" guard. If a GT-entropy cap (`bridgeEntropyCap`) is used, mark it **diagnostic-only / thesis-supervised** — using per-query GT labels to *accept/reject* a bridge is otherwise label leakage. Selection is always geometric (JS-divergence); GT/ancestry is a guard only.
- `bridgeMaxArity` (default 2, ≤3) — fixed small fan-in.
- Bridge is non-recursive, never re-fed to splitter/trickler (query-less).

**Against EXPLOSION (countless tiny bridges):**
- `bridgeParentBudget = 1` — each leaf may join at most one bridge (greedy assignment consumes the leaf).
- `maxBridgeNodes` (default ≈ number of depth-1 domains, ~14) — global cap.
- **`maxBridgesPerDomainPair`** (default 1-2) — prevents many Health↔Biology micro-bridges.
- **Candidate cap:** the O(n²) leaf-pair scan is bounded by a top-k nearest candidates per leaf (or per domain pair) — do not enumerate all pairs.
- `minBridgeCoverage` (default `2*minClusterSize`) — union of a bridge's members must cover ≥ this many queries.
- `maxDepth` untouched (bridge edges are cross-links, not tree edges).

### 3.4 Greedy selection
Lowest-divergence-first, consuming each leaf's single-bridge budget. Stop at `maxBridgeNodes`.

### 3.5 Bridge-aware outputs
Because off-backbone bridges are safe but invisible, emit explicit artifacts:
- **`bridge_nodes.csv`:** bridge id, label, member domains, child leaf ids, coverage, entropy, JS-divergence, depth.
- **`bridge_residuals.csv`:** per-node residual count, residual domains, best-child confidence distribution (from Phase 1).
- **`bridge_aggregate_ranking.csv` (optional):** aggregate descendant leaf arena verdicts under each bridge **post hoc, C2-style (no new judge calls)** — this is the arena utility of a bridge without making it a leaf. Do NOT add bridges to the arena as judge/competitor nodes.

**Phase 3 acceptance:** with `enableBridging=true`, bridges form at the predicted overlaps (Engineering↔Physics/Math, Health↔Biology, Chemistry↔Physics, Business↔Economics); each is query-less, off-backbone, arity ≤ `bridgeMaxArity`, domain-span ≤ `maxBridgesPerDomainPair` respected, entropy ≤ cap (if used); total bridges ≤ `maxBridgeNodes`; the 14 depth-1 domains are unchanged; no parent cycles; the three CSVs are emitted.

---

## Phase 4 — Must-fix pitfalls (do as part of Phase 3)

These are required for bridging correctness; a naive implementation WILL hit them.

**P1 — Label leakage via `getDepth1Ancestors`.** `utils/TaxonomyMetrics.kt:372-385` walks *all* `parents` up to `depth==1`. A bridge with two depth-1 parents makes every leaf beneath it resolve to BOTH domains → contamination drops, edge-F1/ancestor-correct-rate inflate artificially. **Fix:** make domain resolution follow the **`treeParentId` chain only** (or skip `isBridge` nodes / bridge edges). Bridge edges must be non-authoritative for domain identity. **Same fix in `arena/TournamentSimulator.kt:~82` (`getTrueSkill`)** which uses `parents.firstOrNull()` — resolve via `treeParentId`.

**P2 — `blendVmfAndNiw`/`fuseNodes` assume equal `sliceDim`.** `TaxonomyMerger.blendVmfAndNiw:56-88` indexes both nodes at `target.sliceDim`; `fuseNodes:90-91` has `require(target.sliceDim == source.sliceDim)`. A Health leaf (depth 3, dim 512) and a Biology leaf (depth 2, dim 256) → throws / `ArrayIndexOutOfBounds`. **Fix:** blend at `min` common dim, project both members first.

**P3 — Transitive reduction severs bridge edges.** `TaxonomyMerger.transitiveReduction:381-409` protects `treeParentId` (`:387`) but not bridge edges. **Fix:** exclude `isBridge` edges from TR, or protect them explicitly.

**P4 — Don't extend `mergeSimilarSiblings`.** `mergeSimilarSiblings:188-263` FUSES near-identical same-parent children (destroys distinctness — the opposite of a bridge). Keep bridging a separate pass; do not fold it into the merge.

**P5 — `isLeaf` / trickle / arena must stay leaf-only.** `GraphNode.isLeaf` (`:63`) = `children.isEmpty()`. Since bridges are added to `crossLinkChildren` (not `children`), a bridge with no tree children would wrongly be `isLeaf=true`. **Fix:** `isLeaf = children.isEmpty() && !isBridge` (or ensure every bridge has at least one cross-link child and exclude `isBridge` from leaf enumeration everywhere leaves are collected — `TournamentSimulator.routeToLeaves`, `TaxonomyArenaService.getLeaderboardForNode:~111`, `BatchTrickleEvaluator`). Confirm arena still operates on leaves only; a bridge must never become a judge/competitor. (Arena utility at bridge level = post-hoc C2-style aggregation, see 3.5.)

**P6 — Traversal-policy confusion.** Every downstream consumer must explicitly declare which edges it follows: **authoritative tree edges only** (`treeParentId`/`children`), **bridge/cross-link DAG edges** (`crossLinkChildren`/`parents` minus tree), or **both**. Consumers and their required policy:
- Domain resolution (`getDepth1Ancestors`), contamination, edge-F1, ancestor-correct, migration matrix → **tree-only** (bridges must not change a leaf's editorial domain).
- Arena leaf enumeration, trickle routing, leaf assignment, `NoMatchRate` → **tree-only**.
- Hierarchical metrics (LCA/dendrogram-purity/hF1 in `HierarchicalMetrics.kt`) → may use **both** (they are DAG-semantics metrics; decide deliberately and document).
- DOT export, `printHierarchy*`, `diffDagState`/`captureDagState` → **both**, with `isBridge` edges drawn in a distinct style.
- Report generators → **tree-only** unless explicitly bridging-aware.
Without an explicit traversal mode, bridge edges will either vanish from outputs or leak into tree-only metrics. Add a traversal-policy enum and use it at each site.

---

## New parameters (add to `FormalismConfig`, scale against current `separationEpsilon≈0.08`)

| Name | Default | Purpose | Phase |
|---|---|---|---|
| `enableStableQuestionIds` | false | gate Phase 0 identity migration | 0 |
| `enableResidualRouting` | false | gate Phase 1 residual signal | 1 |
| `enableResidualSplitGate` | false | gate Phase 2 residual-viability split | 2 |
| `enableBridging` | false | gate Phase 3 bridging insertion | 3 |
| `routeConfidenceTau` | (see 1.1) | pre-smoothing best-child responsibility below → residual | 1 |
| `bridgeSeparationCeiling` | 0.20 (≈3-5× `separationEpsilon`) | upper JS bound for "adjacent" | 3 |
| `bridgeEntropyCap` | 1.05 bits | max normalized GT-domain entropy of a bridge's members (diagnostic-only guard) | 3 |
| `bridgeMaxArity` | 2 | max subtrees per bridge | 3 |
| `bridgeParentBudget` | 1 | max bridges a leaf can join | 3 |
| `maxBridgeNodes` | 14 | global bridge count cap | 3 |
| `maxBridgesPerDomainPair` | 2 | prevents micro-bridges per domain pair | 3 |
| `bridgeCandidateTopK` | 10 | top-k nearest candidates per leaf (bounds O(n²) scan) | 3 |
| `minBridgeCoverage` | `2*minClusterSize` | min queries a bridge must cover | 3 |

Reuse: `separationEpsilon` (lower band edge / fusion boundary), `minClusterSize` (coverage floor scale), `StatisticsUtils.vmfJsDivergence`/`projectVector`, `TaxonomyMerger.blendVmfAndNiw`.

---

## Phase 5 — Verification

### 5.1 Regression (all new flags off)
- Run the full headless pipeline with `enableStableQuestionIds=false`, `enableResidualRouting=false`, `enableResidualSplitGate=false`, `enableBridging=false`. **Topology and routing outputs should match the `41143e2` baseline except for explicitly intended identity/dedup corrections, which must be reported as migration deltas.**
  - `NoMatchRate` stays at its current (artifact) value when `enableResidualRouting=false`.
  - If `enableStableQuestionIds` is flipped on in isolation, expect documented, intentional diffs: `buildLeafProfiles` partition profile no longer double-counts soft-membership queries (leaf `size`/purity become more accurate), and any text-fragile DAG↔arena joins are repaired. Report these as corrections, not regressions.

### 5.2 Feature (gates on)
- Run with `enableResidualRouting=true`, `enableResidualSplitGate=true`, `enableBridging=true` (and `enableStableQuestionIds=true`). Verify:
  - Bridges form at the predicted overlaps (Engineering↔Physics, Health↔Biology, Chemistry↔Physics, Business↔Economics, "Other" sink).
  - Each bridge is query-less, off-backbone, arity ≤ 2, entropy ≤ cap; total ≤ 14.
  - `residualQueries`/`NoMatchRate` reflect real dead-ends.
  - Parent κ no longer deflated by orphan mass (compare κ at bridged nodes pre/post).
  - Depth-1 = the 14 editorial domains, unchanged.
  - Arena still leaf-only; trickle Top-1/Any-Match unchanged in magnitude (bridges are off-backbone).

### 5.3 Unit tests
- Residual detection: a query below `routeConfidenceTau` is tagged + κ-excluded.
- Bridging: two cross-domain adjacent leaves produce one bridge; a far-apart pair (Law↔Chemistry) produces none; an entropy-3-domain group is rejected; a leaf can't join 2 bridges; `maxBridgeNodes` respected.
- Identity: same `question_id` survives snapshot reload; `buildLeafProfiles` counts a soft-membership query once per leaf; DAG↔arena join succeeds on whitespace-differing text.
- Pitfalls: `getDepth1Ancestors` follows `treeParentId` only (a bridged leaf resolves to ONE domain); `blendVmfAndNiw` blends cross-depth leaves at min dim without throwing; TR preserves `isBridge` edges; `isLeaf` excludes bridges.

---

## Definition of done

1. With all new flags off, pipeline output matches the `41143e2` baseline except for explicitly intended, documented identity/dedup corrections (reported as migration deltas).
2. With flags on, cross-domain bridging parents form at the predicted overlaps, query-less, off-backbone, guard-railed against degeneration and explosion; no parent cycles.
3. Missing-child signal is real: `residualQueries`/`NoMatchRate` populated (construction mode), residuals excluded from parent κ, diffuse-but-viable nodes can split/grow.
4. Universal serialized `question_id` keys split/fit/route/snapshot/arena/migration matrix; partition vs soft leaf profiles separated; DAG↔arena join no longer text-fragile; old snapshots migrate.
5. All six pitfalls (P1–P6) fixed and unit-tested, with an explicit traversal-policy enum at each consumer.
6. Depth-1 preservation invariant intact; arena leaf-only; bridge-level arena utility via post-hoc C2-style aggregation only; downstream tree-only metrics unchanged in magnitude.

---

## Implementation order & dependencies

```
Phase 0 (identity) ── prerequisite for all ──┐
                                            ├─→ Phase 1 (residual signal)
                                            │        │
                                            │        └─→ Phase 2 (residual-viability split gate)
                                            │                 │
                                            └─────────────────┴─→ Phase 3 (bridging insertion) ──→ Phase 4 (pitfalls, inline with 3) ──→ Phase 5 (verification)
```

Phase 0 first (unblocks identity). Phase 1 next (creates the signal). Phase 2 (lets diffuse nodes act on it). Phase 3 + 4 together (the consumer + its correctness fixes). Phase 5 last.

**Recommended commit boundaries:** one PR per phase (0, 1, 2, 3+4), each gated so `main` stays green with `enableBridging=false`.
