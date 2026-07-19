# TaxoArena — DAG Maximization: Change Inventory + Test Plan

**Branch analyzed:** `feature/dag-maximization` @ `e4b7151` ("feat: implement DAG maximization …")
**Base (merge-base with `main`):** `761dcce` ("Experiment fixes"). Note: the handout names `41143e2` as base, but the branch's actual parent/merge-base is `761dcce` (a descendant of `41143e2`); the diff below is `761dcce..e4b7151`.
**Method:** read-only analysis of the full diff (`git diff 761dcce e4b7151`, 23 files, +766/−150) plus source inspection. Handout file:line targets use a shortened layout; real paths are `src/main/kotlin/taxonomy/…`.

---

# PART A — CHANGE INVENTORY

## A1. Files changed, grouped by handout phase

### Phase 0 — Identity
| File | What it does |
|---|---|
| `model/DataModels.kt` | Adds `object TextNormalizer.cleanText` (CRLF→LF + trim) and `object QuestionIdRegistry` (in-memory text→id map). `Embedding.equals/hashCode` re-keyed to `queryId` (fallback = cleanText hashCode). `queryId` **remains `@kotlinx.serialization.Transient`** (line 40). Also adds `object ExperimentOutputContext.activeBaseDir`. |
| `model/GraphNode.kt` | `assignQueryIds(root, enableStableQuestionIds)`: when true, resolves `queryId` via `QuestionIdRegistry.lookup` → cleanText hash fallback; when false, old sequential-by-rawText path. Adds `isBridge` + `residualQueries` fields (below). |
| `dataset/MMLUDatasetFetcher.kt` | After `fetchDataset`, registers every `(text,id)` into `QuestionIdRegistry`. |
| `dataset/ModelEvalLoader.kt` | `fetchMmlProRowIds` / `fetchEmbeddingHits` now load the whole table once and match on exact text **and** `cleanText` fallback (repairs whitespace/encoding join misses). Still text-keyed, not `question_id`-keyed. |
| `tui/service/BatchTrickleEvaluator.kt` | `buildLeafProfiles` gains `ProfileMode.PARTITION` (top-1 canonical, count-once) vs `SOFT` (softmax responsibility weights); `LeafDomainProfile` gains `domainHistogramDouble`/`sizeDouble`. |
| `service/TaxonomyService.kt`, `service/TaxonomySnapshotManager.kt`, `TaxonomyEngine.kt` | Thread `enableStableQuestionIds` into `assignQueryIds` calls. |

### Phase 1 — Residual routing
| File | What it does |
|---|---|
| `operations/TaxonomyTrickler.kt` | New `RoutingResult(leaves, residualHits, trace)` + `ResidualHit(node, questionId, bestChildScore)`. `routeQuery` returns `RoutingResult` (no graph mutation). Pre-smoothing best-child responsibility gate: if `enableResidualRouting && node.depth>=2 && bestChildResp < routeConfidenceTau` → record residual hit (question_id string). **Also unconditionally changes routing to descend `children + crossLinkChildren`** and to skip `isBridge` nodes in results. |
| `operations/TaxonomyOperations.kt` | `.leaves` unwrapping at call sites; in `reassignQueries` (construction), under `enableResidualRouting`, drains `residualHits` into `node.residualQueries`. |
| `operations/TaxonomyFitter.kt` | κ fit uses `kappaQueries = branchQueries − residualQueries` (guarded by `enableResidualRouting`, `.ifEmpty{branchQueries}`). Also: NIW uses `effectiveN` capped for `isBridge` nodes. |
| `utils/TaxonomyMetrics.kt` | Real `residualQueries`/`residualRatio` from `node.residualQueries` when populated (else old text-diff artifact). |
| `model/DataModels.kt`, `model/GraphNode.kt` | `residualQueries: MutableSet<String>` (question_id strings) on every node. |

### Phase 2 — Residual-viability split gate
| File | What it does |
|---|---|
| `operations/TaxonomySplitter.kt` | The `κ<0.5 && size<400` hard skip is replaced by a gate: when `enableResidualSplitGate`, a diffuse node may split iff its residual subset ≥ `minClusterSize` and is JS-separated (≥ `separationEpsilon`) from all siblings. Split then targets the residual subset (`targetQueries`). Also switches lineage/parent lookups from `parents.first()` to `treeParentId`. |

### Phase 3 — Bridging insertion (+ Phase 4 pitfalls, inline)
| File | What it does |
|---|---|
| `operations/TaxonomyMerger.kt` | `insertBridgingParents(root, iteration)` called from `optimizeHierarchy` between `mergeSimilarSiblings` and cross-link/TR. O(n²) leaf-pair scan in JS band `[separationEpsilon, bridgeSeparationCeiling]`, cross-domain (via `getDepth1Ancestors`/treeParentId), GT-entropy reject `> bridgeEntropyCap`, creates query-less `isBridge` node on `crossLinkChildren`, wires `leaf.parents`+parent `crossLinkChildren`. `transitiveReduction` now excludes `isBridge` edges (P3). Emits `bridge_residuals.csv`. New helpers `collectAllLeaves`, `getDepth1Ancestors`, `calculateGtEntropy`. |
| `arena/TournamentSimulator.kt` | `getTrueSkill` walks `treeParentId` chain instead of `parents.first()` (P1). |
| `utils/TaxonomyMetrics.kt` | `getDepth1Ancestors` follows `treeParentId` only, skips bridge parents (P1). |
| `model/GraphNode.kt` | `isLeaf = children.isEmpty() && !isBridge` (P5). |
| `tui/components/TopologyTables.kt` | Tree view walks `children + crossLinkChildren` (renders bridges). |

### Config / other
| File | What it does |
|---|---|
| `config/TaxonomyConfig.kt`, `config/EffectiveConfig.kt` | Add 4 flags + 9 params with defaults. |
| `runner/HeadlessBenchmarkRunner.kt` | CLI/TOML plumbing for all 13 keys; sets `ExperimentOutputContext.activeBaseDir` per seed. |
| `service/TaxonomyRankingService.kt` | Unrelated SQLite fix: lazy connection re-opened when `ranking.db.path` changes; `getTables` ResultSet `.use{}`. |
| `dataset/MMLUDatasetFetcher.kt`, `service/TaxonomyService.kt` | (listed above) |
| tests: `MrlRoutingTest`, `TournamentSimulatorTest`, `integration/BenchmarkE2EIntegrationTest` | Mechanical fixes only (`.leaves`, set `treeParentId`, DB-path teardown). **No new feature tests.** |

## A2. Phase verdicts (with evidence)

### Phase 0 — **PARTIAL**
- `question_id` universal key: **PARTIAL.** `assignQueryIds` resolves via `QuestionIdRegistry` when `enableStableQuestionIds` (`GraphNode.kt:186-207`), `Embedding.equals/hashCode` re-keyed to `queryId` (`DataModels.kt:48-58`). **But `queryId` stays `@Transient` (`DataModels.kt:40`)** — not serialized; the true MMLU id is only in an in-memory registry populated at dataset fetch (`MMLUDatasetFetcher.kt:191`). On reload without a fresh fetch it falls back to `cleanText().hashCode()`, i.e. a stable hash, **not** the MMLU `question_id`. The handout's "serialize `question_id` on Embedding (preferred)" is not done.
- Partition vs soft profiles: **IMPLEMENTED.** `ProfileMode` + weighted counting (`BatchTrickleEvaluator.kt:51-130`). Partition counts each query once via top-1 similarity; soft uses softmax weights.
- Shared `cleanText` everywhere: **PARTIAL.** `TextNormalizer.cleanText` exists and is used in identity, eval-loader joins, profiles. The handout's specific `HeadlessBenchmarkRunner:487` trickle `cleanText` was **not** verified to be lifted to the shared normalizer (not touched in diff).
- DAG↔arena join on `question_id`: **PARTIAL/MISSING.** `ModelEvalLoader` still joins on **text (+cleanText fallback)** (`ModelEvalLoader.kt:283-330`), not on `question_id` as the primary key.
- Snapshot schema version + migration: **MISSING.** No schema version added; `TaxonomySnapshotManager.kt` change is only the `assignQueryIds` flag pass-through. **`isBridge`, bridge edges, and `residualQueries` are NOT persisted** (GraphNode is not `@Serializable`; snapshot DTO has only a legacy `residualQueries: Int` count, no `isBridge`). Bridges silently vanish on reload.

### Phase 1 — **IMPLEMENTED (with an ungated side-effect)**
- `RoutingResult`, no eval-time mutation: **IMPLEMENTED** (`TaxonomyTrickler.kt:18-29, 122-149`; mutation only in construction `reassignQueries`, `TaxonomyOperations.kt:95-101`).
- `routeConfidenceTau` gate, depth-1 exempt: **IMPLEMENTED** (`TaxonomyTrickler.kt:97-102`, `node.depth >= 2`).
- `residualQueries` = question_id strings, construction-only, not embeddings: **IMPLEMENTED** (`GraphNode.kt:60-61`, `TaxonomyOperations.kt:96-100`).
- Residuals excluded from parent κ: **IMPLEMENTED** (`TaxonomyFitter.kt:98-104, 165-196`) with `.ifEmpty` stabilizer.
- ⚠️ **Ungated behavior change:** `routeQuery` now walks `children + crossLinkChildren` and filters `isBridge` **unconditionally** (`TaxonomyTrickler.kt:59, 116, 126`) — not behind any flag. See A4.

### Phase 2 — **IMPLEMENTED (2.2 partial)**
- κ<0.5&&size<400 skip replaced by residual-viability gate: **IMPLEMENTED** (`TaxonomySplitter.kt:85-141`). Flag-off path preserves old behavior (diffuse→return).
- 2.2 cross-domain child routed to bridging consumer: **MISSING.** A residual-driven split just spawns normal tree children; no hand-off to `insertBridgingParents`.

### Phase 3 — **PARTIAL**
- `insertBridgingParents` exists, runs between `mergeSimilarSiblings` and TR: **IMPLEMENTED** (`TaxonomyMerger.kt:38-48, 574`).
- Query-less, off-backbone (crossLinkChildren): **IMPLEMENTED** (`TaxonomyMerger.kt:699-713`; no `children` writes; `queries` empty).
- Two candidate sources: **PARTIAL.** Source A (JS band) done; **Source B (residual sub-clusters) MISSING.**
- Bridge depth `max(2, min(childDepths)-1)`: ⚠️ **WRONG** — code uses `maxOf(2, maxOf(u.depth, v.depth) - 1)` (`TaxonomyMerger.kt:652`), i.e. **max** of child depths, not **min**. Can place the bridge at/above a shallower child's depth.
- Cycle prevention: **MISSING** (no ancestor assertion before edge add).
- Greedy lowest-divergence-first: **MISSING** (candidate pairs iterated in scan order, not sorted by `div`).
- CSV outputs: `bridge_residuals.csv` **emitted but mis-scoped** (it is a bridge-candidate decision log: `iteration,candidate_id,source_nodes,size,entropy,div,accepted,reason` — not per-node residual counts/domains/confidence). `bridge_nodes.csv` **MISSING.** `bridge_aggregate_ranking.csv` **MISSING** (optional).

### Phase 4 — pitfalls
- **P1 (label leakage via getDepth1Ancestors) — IMPLEMENTED.** `TaxonomyMetrics.kt:383-391` treeParentId-only; `TournamentSimulator.kt:82-83` treeParentId.
- **P2 (blend at min common sliceDim) — PARTIAL/side-stepped.** Bridge μ/κ computed manually at `commonDim` (`TaxonomyMerger.kt:657-674`), so no throw; but `blendVmfAndNiw`/`fuseNodes require(sliceDim==)` themselves are **unchanged** — the fix is avoidance, not repair.
- **P3 (TR protects isBridge) — IMPLEMENTED** (`TaxonomyMerger.kt:391, 396`).
- **P4 (keep bridging out of mergeSimilarSiblings) — IMPLEMENTED** (separate pass).
- **P5 (isLeaf excludes isBridge; arena leaf-only) — IMPLEMENTED** (`GraphNode.kt:63`; routeQuery/collectAllLeaves respect it). Caveat: relies on `isBridge` surviving reload — it does not (Phase 0.5), so reloaded bridges become leaves.
- **P6 (traversal-policy enum) — MISSING.** No enum. Consumers were patched ad hoc, and inconsistently: metrics/arena now tree-only (good), but **trickle routing was switched to follow crossLinkChildren** (violates the "tree-only" policy P6 assigns to routing).

## A3. Flag / param / guard-rail accounting

| Item | Present? | Evidence / note |
|---|---|---|
| `enableStableQuestionIds` | ✅ wired | `assignQueryIds` branch |
| `enableResidualRouting` | ✅ wired | trickler gate + fitter κ-exclusion + ops drain |
| `enableResidualSplitGate` | ✅ wired | splitter gate |
| `enableBridging` | ✅ wired | gates `insertBridgingParents` |
| `routeConfidenceTau` | ✅ used | trickler:99 |
| `bridgeSeparationCeiling` | ✅ used | band upper bound |
| `bridgeEntropyCap` | ⚠️ used as **accept/reject** | GT-entropy gate — see A4 (leakage) |
| `bridgeMaxArity` | ❌ **unused** | bridges hard-coded to pairs (arity 2) |
| `bridgeParentBudget` | ❌ **unused** | no per-leaf budget; a leaf can join many bridges |
| `maxBridgeNodes` | ✅ enforced | global cap check |
| `maxBridgesPerDomainPair` | ❌ **unused** | no per-domain-pair cap |
| `bridgeCandidateTopK` | ❌ **unused** | full O(n²) scan, not bounded (handout required bounding) |
| `minBridgeCoverage` | ❌ **unused** | no coverage floor enforced |
| Cycle prevention | ❌ missing | no ancestor check |
| Entropy guard "diagnostic-only" | ❌ | used to reject, not diagnostic |

## A4. Correctness concerns

1. **GT-entropy used as a bridge accept/reject criterion = label leakage.** `calculateGtEntropy` reads per-query GT `category` (`TaxonomyMerger.kt:764-778`) and `if (entropy > bridgeEntropyCap) continue` (`:635-647`) rejects the bridge. The handout explicitly forbids this ("using per-query GT labels to accept/reject a bridge is otherwise label leakage… mark it diagnostic-only"). This is a selection criterion driven by ground truth.
2. **Ungated routing change may break the flags-off regression.** `routeQuery` now descends `children + crossLinkChildren` and skips `isBridge` **regardless of flags** (`TaxonomyTrickler.kt:59,116,126`). Baseline used `children` only. If any pre-existing `crossLinkChildren` (from `evaluateCrossLinks`) exist at eval time, Top-1/Any-Match and NoMatchRate can shift even with all four flags off — violating Definition-of-Done #1. Needs an isolation run to confirm magnitude.
3. **Bridge depth uses `max(childDepths)-1` not `min`** (`TaxonomyMerger.kt:652`): a bridge can be placed at the same depth as (or below) a shallower member, breaking the "parent shallower than its children" invariant when member depths differ.
4. **No cycle check** before adding bridge edges (handout 3.2). Combined with parent-of-parent wiring (`:704-713`) this is an unguarded DAG-cycle risk.
5. **`isBridge`/`residualQueries` not serialized.** Snapshot save/load drops bridge identity → reloaded bridges satisfy `children.isEmpty()` → become `isLeaf=true` → enter arena as competitors and get queries routed to them (P5 violated post-reload). Also `residualQueries` set is lost.
6. **`bridgeParentBudget`, `maxBridgesPerDomainPair`, `bridgeCandidateTopK`, `minBridgeCoverage` unenforced** → explosion guards (handout 3.3) largely absent; only `maxBridgeNodes` and the entropy/band gates actually bound output. On a real corpus the O(n²) scan is also a performance risk.
7. **`queryId` transient + hash fallback**: identity is stable across a single process but is a text hash, not the serialized MMLU `question_id`; any consumer expecting the real id (e.g. a future arena join on id) still won't get it.

---

# PART B — TEST PLAN

**Invocation baseline.** Headless entry: `HeadlessBenchmarkRunner.run(--config <file>)` (`HeadlessBenchmarkRunner.kt:94-127`); config is TOML or JSON with keys incl. `outputDir`, `seeds`, `numIterations`, `runBenchmark`, `runTrickle`, `domains`, and all 13 new keys. Run via:
```
./gradlew bootRun --args="--config <config.toml>"
```
Unit tests: `./gradlew test` (JUnit5). Cost gate: `runBenchmark=true` → arena/judge LLM calls (expensive); `runTrickle=true` + `runBenchmark=false` + `enableLabeling=false` → taxonomy build + trickle only (free). Bridge LLM labeling fires only if `enableLabeling=true` (`TaxonomyMerger.kt:677`) — keep it off for cheap runs.

## B1. Unit tests

**Already in repo (touched, mechanical):** `MrlRoutingTest` (now `.leaves`), `TournamentSimulatorTest` (sets `treeParentId`), `BenchmarkE2EIntegrationTest` (db-path teardown). `TaxonomyMetricsIntegrationTest` references `residualQueries` (pre-existing count field).
**Missing (must be written) — no feature-specific tests exist for any DAG-max behavior.**

Write these (all pure JVM, free):
- **R1 residual detection + κ-exclusion:** build a node with two children; craft an embedding whose max raw child prob `< routeConfidenceTau`; assert `RoutingResult.residualHits` contains it (question_id key, depth≥2), and that depth-1 weak routing produces **no** hit. Then assert `TaxonomyFitter` κ computed on `kappaQueries` (residual-excluded) > κ computed on full branch (orphan mass no longer deflates).
- **R2 bridge accept (adjacent cross-domain):** two leaves, distinct depth-1 ancestors, JS-div in `[separationEpsilon, bridgeSeparationCeiling]`, entropy ≤ cap → exactly one `isBridge` node, query-less, wired via `crossLinkChildren`, not in any `children`.
- **R3 bridge rejects:** (a) far-apart pair (div > ceiling) → none; (b) 3-domain / entropy > cap group → none; (c) **budget:** a leaf appearing in two candidate pairs must join ≤ `bridgeParentBudget` bridges — **expected to FAIL today** (budget unenforced); (d) `maxBridgeNodes` respected → passes.
- **R4 identity across reload:** save+load a snapshot; assert the same query keeps its `queryId` (or stable cleanText-hash) and that `isBridge` survives — **expected to FAIL today** (isBridge not serialized). Document as a Phase-0.5 gap test.
- **R5 buildLeafProfiles partition vs soft:** a query soft-assigned to 3 leaves; PARTITION → counted once (Σ leaf sizes == distinct queries); SOFT → weights sum ≈ 1 across leaves.
- **P1:** a leaf under a two-domain bridge resolves via `TaxonomyMetrics.getDepth1Ancestors` to exactly ONE domain (its treeParentId chain).
- **P2:** `blendVmfAndNiw`-equivalent bridge build on a depth-3 (dim 512) + depth-2 (dim 256) pair does not throw (min common dim). Add a direct `require`-path test for `fuseNodes` to document the still-unpatched throw.
- **P3:** run `transitiveReduction` on a graph with an `isBridge` cross-edge; assert the bridge edge survives.
- **P5:** `GraphNode(isBridge=true, children=∅).isLeaf == false`; assert `collectAllLeaves` and arena leaf enumeration exclude it.
- **P6:** assert routing does **not** change a leaf's domain and (regression) assert routing over a graph with pre-existing crossLinkChildren matches tree-only routing — this pins concern A4#2.

## B2. Regression run (all four flags OFF)

Config `regression_off.toml`:
```
outputDir = "out/reg_off"
seeds = [42]
numIterations = 25
runBenchmark = false
runTrickle = true
enableLabeling = false
enableStableQuestionIds = false
enableResidualRouting = false
enableResidualSplitGate = false
enableBridging = false
```
Run the same config against `41143e2`/`761dcce` baseline and against `e4b7151`. Diff artifacts under `out/reg_off/seed_42/`: trickle CSVs (Top-1/Any-Match), migration matrix, trajectory, per-domain table, `NoMatchRate`.
- **Must match exactly:** topology (node/edge counts, depths, Sackin), migration matrix, contamination, edge-F1, ancestor-correct, Top-1/Any-Match magnitudes, and `NoMatchRate` stays at its **artifact** value (residual routing off).
- **Allowed migration deltas (handout 5.1):** none expected with `enableStableQuestionIds=false`; the identity/dedup corrections only appear when that flag flips on.
- **Watch item (A4#2):** if numbers move here, the culprit is the ungated `children + crossLinkChildren` routing change in `TaxonomyTrickler`, not a flag. This is the single most important regression check.

## B3. Feature run (flags ON)

Config `feature_on.toml`:
```
outputDir = "out/feat_on"
seeds = [42]
numIterations = 25
runBenchmark = true          # needed only for the arena/κ + NoMatchRate assertions
runTrickle = true
enableLabeling = false
enableStableQuestionIds = true
enableResidualRouting = true
enableResidualSplitGate = true
enableBridging = true
routeConfidenceTau = 0.5
bridgeSeparationCeiling = 0.20
bridgeEntropyCap = 1.05
maxBridgeNodes = 14
```
Assertions:
- Bridges form at predicted overlaps (Engineering↔Physics, Health↔Biology, Chemistry↔Physics, Business↔Economics) — inspect `bridge_residuals.csv` accepted rows (note: **`bridge_nodes.csv` is not emitted**, so verify via log lines "Created bridge …" + the CSV, and via DOT/topology which now renders crossLinkChildren).
- `bridge_residuals.csv` present with columns `iteration,candidate_id,source_nodes,size,entropy,div,accepted,reason` (⚠ not the handout's per-node schema; flag this deviation).
- `NoMatchRate` now real/non-zero where dead-ends exist (`TaxonomyMetrics` residual path) — compare vs B2's artifact 0.
- Parent κ no longer deflated: compare `vmfKappa` at nodes that gained a bridge, flags-off vs flags-on; expect flags-on κ ≥ flags-off at those nodes.
- Depth-1 == 14 editorial domains, unchanged; arena competitor set == leaves only (no `isBridge`); tree-only metrics (contamination, edge-F1, ancestor-correct, migration matrix) unchanged in magnitude vs B2.
- **Expected-fail / caveats to record:** bridge depth may violate parent<child when member depths differ (A4#3); explosion caps unenforced (A4#6) so bridge count may exceed intent on larger corpora even under `maxBridgeNodes`=14 only-cap; entropy-based rejection is GT leakage (A4#1).

## B4. Isolation runs (attribute each diff to its phase)

Run B2 config four more times, adding one flag at a time; diff each against the previous:
1. `+enableStableQuestionIds` → expect the documented Phase-0 corrections only: `buildLeafProfiles` partition no longer double-counts (leaf `size`/purity shift), text-fragile joins repaired. Report as migration deltas, not regressions.
2. `+enableResidualRouting` → `residualQueries`/`NoMatchRate` become real; κ at diffuse parents rises. Topology should be ~stable (residuals don't yet split).
3. `+enableResidualSplitGate` → previously-skipped diffuse nodes may now spawn children; watch depth/leaf-count growth.
4. `+enableBridging` → bridges appear (crossLinkChildren); tree-only metrics must stay flat; only DAG-aware views change.

This ladder localizes which phase moves which metric. Because concern A4#2 is **ungated**, any diff already visible at step "all-off vs baseline" (B2) belongs to the routing change, not to steps 1–4.

## B5. Budget / cost note & recommended order

- **Free (no LLM/arena):** all B1 unit tests; B2 and B4 with `runBenchmark=false, runTrickle=true, enableLabeling=false`; the topology/trickle/migration/κ/NoMatchRate portions of B3.
- **Expensive (LLM/arena):** any run with `runBenchmark=true` (judge tournaments) or `enableLabeling=true` (bridge/cluster labeling LLM calls). Only B3's arena-utility / competitor-set assertions strictly need `runBenchmark=true`.

**Cheapest-first order:** (1) B1 unit tests → (2) B2 regression flags-off (free, and the highest-value check for the ungated-routing concern) → (3) B4 isolation ladder (free) → (4) B3 free portion (bridges/NoMatchRate/κ/tree-metrics with `runBenchmark=false`) → (5) B3 arena assertions with `runBenchmark=true` **last**.

---

## Bottom line

- **Implemented:** Phase 1 (residual signal, RoutingResult, κ-exclusion), Phase 2 gate, Phase 0 profiles, and P1/P3/P4/P5; flags/params are all plumbed through config+CLI.
- **Partial/Missing:** Phase 0.5 snapshot versioning + `isBridge`/`residualQueries`/`question_id` serialization (queryId still `@Transient`); DAG↔arena join still text-keyed; Phase 3 Source-B residual candidates, greedy ordering, cycle check, and the explosion guards (`bridgeParentBudget`, `maxBridgesPerDomainPair`, `bridgeCandidateTopK`, `minBridgeCoverage`, `bridgeMaxArity` — all unused); `bridge_nodes.csv`; Phase-4 P6 traversal-policy enum; Phase-2.2 cross-domain hand-off.
- **Correctness concerns:** GT-entropy as accept/reject (label leakage); ungated `children+crossLinkChildren` routing change (flags-off regression risk); bridge depth `max` vs `min`; no cycle prevention; bridges lost on snapshot reload.
- **Cheapest first test:** the B1 unit suite, immediately followed by the **B2 flags-off regression** — the single check most likely to expose the unintended (ungated) routing behavior change.
