# TaxoArena performance and parallelization review (read-only, 2026-09-09)

Produced by a read-only review agent while the promoted bareq512_s42 build was running; nothing
was modified or executed beyond file/process inspection and a scratch micro-benchmark of a
copied Python function. Estimates are labelled as such; nothing below has been applied yet.

**Machine:** AMD Ryzen 9 7900X3D, 12 cores / 24 threads, 63.1 GB RAM, GraalVM JDK 21.0.6,
Gradle 8.10, Kotlin 2.1.10.

## Where the wall time goes (measured)

Construction build, 1024 dims (`experiment_results/dimsweep3/bareq1024_s2048`, chain wall 594 s):

| Segment | Time | Evidence |
|---|---|---|
| Gradle + Spring startup to first app log line | ~28 s | chain.log vs first log line |
| Dataset load, split, reserved-pool sync (160,484 rows flagged) | 13.5 s (9.6 s pool sync) | log |
| **phase4_split, 10 iterations** | **506.9 s (94 %)** | performance_report.json; per-iteration 78/69/57/54/46/41/41/41/40/41 s |
| of which iterations 6–10 (tree unchanged, 486 proposals attempted, 0 accepted each) | 205 s (37 %) | iteration_metrics.csv; `[CONVERGENCE] streak 5/5` |
| phase1/2/3/5 + J-bootstrap (B=200, ~1.2 s/iter) | < 20 s | perf table |
| snapshot save | 2.3 s | |
| validation.MAIN (3,599 held-out queries) | 24.9 s (144 q/s) | |
| JVM shutdown to chain exit | ~11 s | |

512-dim build (`dimsweep2/bareq512_s137`): phase4_split 235.9 s of 260 s; iterations 6–10 = 98 s
at 457 attempted / 0 accepted each; validation 16.9 s.

**Phase 4 is effectively single-threaded.** `TaxonomyOperations.splitNodesRecursive`
(`src/main/kotlin/taxonomy/operations/TaxonomyOperations.kt:163-221`) iterates nodes sequentially
and calls `tryProposal` (must be sequential: it mutates and restores the tree). Inside each attempt
the dominant work is `StatisticsUtils.pcaProject` (`StatisticsUtils.kt:641-740`): 30 power
iterations × (32/64/128 components), each a full pass over the n×d residual matrix. Only the EM
candidates (`performVmfKMeans`, 2–3 coroutines) and the full re-route on structurally changing
proposals (`reassignQueries`) are parallel. One depth-1 node at n=961, d=1024 ≈ 7.6 GFLOP per PCA
call, ×3 k-attempts ≈ 15 s of one core.

**Site-level null (`gradlew siteNull`, 1024 dims): 2,114 s and 2,205 s per seed.** 73 sites × 2 arms
× 300 reps = 43,800 `splitSingleNode` calls; ≈ 8.5e13 FLOP, of which PCA power iteration ≈ 89 %,
cloud generation ≈ 7 %, EM ≈ 4 %. At 24 threads × ~1.5 GFLOP/s the model predicts ~2,350 s —
matches the observed 2,205 s: CPU-bound on PCA. Structure (`SeparationNullBySizeTest.kt:1692-1796`):
sites sequential; within a site 300 reps as `async(Dispatchers.Default)` with an `awaitAll` barrier
per arm. RNG is a fresh `java.util.Random(seedBase + site.id.hashCode()*2654435761 + rep*104729)`
per replicate; the production splitter has no randomness (PCA init seeded from problem shape, EM
deterministic), so **the CSV is already scheduling-independent and bit-reproducible under any
thread count** — and per-rep work cannot be shared (each replicate is a different cloud).

**Labeled builds** (`promoted/bareq512_s42`): construction 494 s (phase4 424 s), labeling 66 s for
143 nodes (LLM-latency bound at the 3 req/s pacer), judge induction for 87 nodes with parallelism 8
≥ 7.5 min (log ended mid-induction).

## Critical finding: the build JVM runs without the optimising JIT

The construction process runs with `-XX:TieredStopAtLevel=1` — Spring Boot `bootRun`'s
"optimized launch" default (C1 only, no C2/Graal top tier); `build.gradle.kts:178-207` never
disables it. Every numeric hot loop of construction (PCA, EM, dot products, J) runs under the C1
baseline compiler, while the `siteNull`/`isoNullByDim` Test JVMs get the full JIT. C1 on tight
double loops is typically 2–4× slower than the top tier (not measured here).

## Safe quick wins (ranked by expected saving)

1. **Disable `optimizedLaunch` on `bootRun`** — `build.gradle.kts:178`
   (`tasks.named<BootRun>("bootRun") { optimizedLaunch = false }`). Expected: phase 4 507 s →
   ~130–250 s at 1024; build 594 s → ~220–340 s (estimate). Bit-identical for + − × ÷ sqrt and
   comparisons (Java strict FP, no FMA/reassociation); residual risk is `Math.exp/ln` (EM E-step,
   `logBesselI`) under Graal's top tier vs the C1 stub. **Gate: rerun one finished config
   (bareq512_s137) and diff `dag_snapshots.jsonl`, `fixed_point_certificate.txt`,
   `iteration_metrics.csv`.** Fallback `-XX:-UseJVMCICompiler` (HotSpot C2, shared stubs).
2. **Compute the PCA once per node per iteration across k = 2..4** — `TaxonomyOperations.kt:213-221`
   calls `splitSingleNode(node, forcedK = k)` for k = 2, 3, 4 and `TaxonomySplitter.kt:116-143`
   recomputes `targetQueries`, `rawVectors`, `pcaProject` each time; `forcedK` only changes the EM
   call. 471/486 (1024) and 438/457 (512) attempts per iteration are NO_PROPOSAL, so nearly every
   node pays 3×. Cache keyed on (node.id, iteration, population hash); `GraphStateBackup.restore`
   restores queries verbatim and `targetQueries` is sorted, so the input is bit-identical.
   Expected: phase 4 −40 to −55 %. Bit-identical. Small effort.
3. **Overlap `siteNull` of build N with build N+1 in the chain.** `siteNull` reads only
   snapshots DB (read-only, closed after load) and embeddings_cache.db; it never touches
   reserved_test_queries.json, the dataset DB pool flags or ratings.db. Build phase 4 is ~1 core so
   contention with the 24-thread null is ~5 %. Saves ≈ one build (~10 min) per additional arm.
   Bit-identical. Hazards: never with `--rerun-tasks` (recompiling classes under a running JVM);
   two concurrent Gradle invocations in one project dir share daemon/config-cache locks — test
   once; start the site-null before the next build.
4. **In-place residual deflation in `pcaProject`** — `StatisticsUtils.kt:699-705` allocates n fresh
   arrays per component (~1 GB per PCA call at n=961, d=1024, 128 comps; ~9.7 TB over the 1024
   site-null). `row[i] -= dot * vec[i]` in place, same arithmetic and order. Estimated 5–15 % of
   site-null wall (GC). Bit-identical. 3 lines.
5. **Parallelise the held-out validation loop** — `tui/service/BatchTrickleEvaluator.kt:170-216`
   routes 3,599 queries sequentially (17–25 s) while the construction trickler routes 8,305 in
   0.2 s in parallel. Ordered reduction keeps it bit-identical. ~20 s per build.
6. **Python analysis scripts (bit-identical):** one cached load of `eval_results` (973 MB table,
   every read is a full scan; `free_tests_f4_f7.py` does 12 scans per run, `clean_subset_reanalysis.py` 3,
   `synthetic_arena_scaling.py` 3, `judge_free_tests.py` up to 4) — caveat: the bare-column
   `GROUP BY question_id` at `free_tests_f4_f7.py:118,122` assumes category/options constant per
   question; embedding decode via `np.frombuffer(blob, ">f4")` (1.09 s → 0.03 s, verified
   array_equal; `free_tests_f4_f7.py:284` decodes the 215 MB cache once per tree, 7×); `loo_imp`
   (`free_tests_f4_f7.py:131-147`) via `np.bincount` (exact; 15–25 s → <1 s); `online_replay.py:105-108`
   dead O(n²) loop; `synthetic_arena_scaling.py` per-cell RNG → process pool with seed-ordered
   reduction (5–8×); memoise `load_live`/`gt_and_lengths` in `judge_free_tests.py`.
7. **Judge harnesses — raise in-flight concurrency (statistically identical).** Every Mistral run
   sat at 0.9–1.3 calls/s with 8–12 workers and zero 429s in any log; the binding constraint is
   workers × latency (8.5–12 s), not the 3 req/s cap. Splitting the two order calls into separate
   futures does not help; only more in-flight requests do. Sizing the aggregate across co-launched
   scripts to ~24–28 in flight is a plausible 1.5–2.5×. Outputs are already non-reproducible
   (no temperature/seed sent); cache PKs make DB content completion-order independent. Cheap fixes:
   per-call `timeout=600` pins a slot 10 min on a hung read; a failed order-2 call discards the paid
   order-1 result (308 matches lost that way in the R1 run).

## Needs care

8. **Keep the proposal memo across iterations** — `TaxonomyEngine.kt:293` calls
   `ops.invalidateCachedJ()` every iteration, which also clears `rejectedProposalsCache`
   (`TaxonomyOperations.kt:127-131`); `[MEMO] hits=0` in every log. Iterations 6–10 exist only for
   the 5-iteration J-stationarity streak and re-evaluate 486 identical proposals each. Stop clearing
   the memo on re-route (it is cleared on every accepted edit). ≈ 200 s (37 %) at 1024, ≈ 100 s at
   512. Tree bit-identical if the fingerprint pins the decision (the code argues it does), but
   `proposals.csv` rows change (MEMOIZED vs NO_PROPOSAL); the memo had a false-hit incident
   (comment `:197-200`). **Validate by full rerun + diff on two configs.**
9. **Parallelise `pcaProject` internally, bit-identically** — `StatisticsUtils.kt:671-719`: row
   dots in parallel, then coordinate-block-parallel accumulation walking rows in original order per
   coordinate (preserves each coordinate's summation order). Build only (site-null already saturates
   24 threads): phase 4 PCA ~6–12×. Medium effort; a reduction-order slip silently changes proposals
   — write an equality test (the Philosophy replay, sep 0.02077, is a ready check).
10. **Gradle/JVM:** `bootRun` has no `-Xmx` (default ≈ 15.8 GB, RSS 1.3 GB observed) — fine. Test
    harness `maxHeapSize = "6g"`; with the churn of #4 a larger young gen or ParallelGC on siteNull
    may help (unverified). `--rerun-tasks` is used by the chain scripts (`promoted_chain.ps1`,
    `d4_chain.ps1`, `RUN.md`) — a full Kotlin recompile per build (1–2 min, not measured); drop it
    (bit-neutral) and never combine with #3.
11. **Site-null: sites in parallel / no per-arm barriers** (`SeparationNullBySizeTest.kt:1712-1796`):
    2–3 sites concurrently is bit-identical for the CSV; buffer console rows per site
    (`Capture.unlabelled` is batch-scoped). 5–15 %.
12. **Judge induction chunk barriers** — `TaxonomyJudgeService.kt:71-82` `chunked(8)` + `awaitAll`
    waits for the slowest call per chunk (http p95 20 s vs p50 1.9 s). Sliding semaphore of 8–16:
    1.5–2× on the ≥ 7.5-min induction. Check the depth ordering (`:56`) for a parent-before-child
    dependency first.
13. **Bootstrap loops with a shared RNG stream (statistically identical only):** Kotlin `JBootstrap`
    (~1.2 s/iter, not worth it); Python `clean_subset_reanalysis.py:130-144` (2×1000 permutations,
    ~85 % of a 4–7 min run), `match_budget_curve.py:41`, `judge_free_tests.py:127-132`,
    `free_tests_f4_f7.py:150-155,207-208` (148M `randrange` calls). Bit-identical route: pre-draw
    indices serially, evaluate in a process pool with ordered reduction; numpy RNG is 30× faster but
    changes CI endpoints.

## Not recommended / leave alone
- Changing the PCA algorithm (eigensolver, block iteration, fewer than 30 iterations): 3–4× fewer
  FLOPs but changes proposals bit-wise and would re-baseline every frozen artifact.
- Two constructions in one repo root (reserved pool activation + reserved_test_queries.json shared).
- Reserved-pool sync (9.6 s) — inside the pool-hygiene guard; not worth the risk.

## Could not verify
- The C1→top-tier speedup ratio and Graal `Math.exp/log` bit-consistency (#1) — needs one replay + diff.
- GC share of the site-null (#4, #10) — no GC log.
- Gradle's behaviour with two concurrent invocations in one project dir (#3).
- `category`/`options_json` constancy per question in `eval_results` (#6); whether `Z:` is a network
  drive (decides whether the 1 GB scans cost 3 s or 30 s+).
- Judge-induction end time; actual 429 thresholds for Mistral/grok (no 429 in any log).
