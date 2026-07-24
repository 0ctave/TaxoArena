# TaxoArena — Performance Optimization Report v2 (with Parallelization Guide)

Updated against commit `99029f2` and the new run.log (build 01:47:22 → run continues).
Reflects the optimizations already landed (EM cap, early-reject, concurrent k-EM, OPT-6
per-iteration gating, OPT-3 dataset hoisting) and the NEW dominant bottleneck they exposed.
Read-only inspection; no code modified.

---

## Where time goes NOW (post-EM-optimization)

Your EM work cut the build from ~165s → **77s** (DAG PERFORMANCE REPORT total). Good.
But two ~65–77s gaps in *finalization* are now the largest single cost, and they were
hidden before because the build dwarfed them.

| Phase | Duration | Nature | Status |
|---|---|---|---|
| DAG build (Phase 4 etc.) | 77s | CPU | ✅ optimized |
| **Finalization metrics (computed TWICE)** | **~65s + ~77s** | CPU | ❌ **new #1 bottleneck** |
| Snapshot DB save | 2.5s | IO | ✅ not a bottleneck |
| Baseline gen (Python subprocess) | 97s | subprocess | ❌ OPT-1 (skip in tuning) |

The "save takes a minute" is a **misattribution**: the DB save is 2.5s
(`01:49:44.146 → 01:49:46.659`, 164 nodes). The minute before the "Saving…" line is the
**second full metrics recompute** — the save log only prints after it returns.

---

## OPT-7 — Finalization computes the full metric suite TWICE  [ENGINE — highest ROI, ZERO risk]

**Root cause (verified).** `TaxonomyEngine.kt:370–372`:
```
val finalReport = TaxonomyMetrics(root, groundTruthMap)
finalReport.printReport(config)                       // line 371 → internally calls generateReport()  [compute #1]
...reportToIterationMetrics("Final", finalReport.generateReport())  // line 372 → generateReport() AGAIN [compute #2]
```
`printReport(config)` at `TaxonomyMetrics.kt:504` starts with `val r = generateReport()`.
So the full suite — including the O(same-label-pair²) LCA-walking **DendrogramPurity** over
~5700 queries — runs **twice back-to-back**. That is precisely the two ~65–77s gaps in the
log (one per call).

**Fix — compute once, reuse.** Add a `printReport` overload taking a precomputed `Report`:
```
val finalReport = TaxonomyMetrics(root, groundTruthMap)
val report = finalReport.generateReport()      // single compute
finalReport.printReport(config, report)        // new overload: prints the passed Report, no recompute
taxonomyService.addIterationMetrics(reportToIterationMetrics("Final", report))
```
`generateReport()` is deterministic on a frozen DAG → identical output, just once.

**Saving.** ~65–77s per run. **Zero DAG/metric change, no re-validation.** Do this first.

---

## OPT-8 — Gate or sample the final metrics for TUNING runs  [ENGINE — high ROI]

Even computed once, `generateReport()` is ~65s, dominated by DendrogramPurity's LCA walk.
Confirmed: the `"Final"` `addIterationMetrics` entry is **not consumed anywhere in
`HeadlessBenchmarkRunner`** — the selection ledger comes from `runHeadlessTrickle`, not this.
So for tuning sweeps the full architectural report is optional.

**Options (pick per use-case):**
- **Gate it** behind `enableIterationMetrics` (the flag you already added for OPT-6) or a new
  `enableFinalMetrics`, default OFF for sweeps → saves the remaining ~65s on every screen config.
- **Sample DendrogramPurity**: compute purity over a random subset of same-label pairs
  (Monath et al. themselves sample). Turns O(pairs²) into O(sample) with negligible accuracy
  loss. Keeps the metric available even in tuning at a fraction of the cost.

**Saving.** Up to ~65s per tuning config (gating) or ~50s (sampling, metric still produced).
**Caveat.** Gating removes the final report from that run's output — fine for tuning, keep it
ON for the canonical/final build you report in Ch6.

---

## OPT-1 (still open) — Skip baselines in tuning  [CONFIG — highest ROI, zero risk]

Baseline subprocess still ran here: `01:49:47 → 01:51:24 = 97s`. For a *tuning* run this is
pure waste (baselines are a fixed reference computed once for the final DAG).
Set `runBaselines = false` in sweep configs. **−97s per tuning config.**

---

## Combined effect (tuning run)

Current run ≈ build 77s + finalization ~140s (2× metrics) + baselines 97s + validation ≈ ~350s.

- OPT-7 (dedup): −70s → identical output.
- OPT-8 (gate for tuning): −65s → ledger unaffected.
- OPT-1 (no baselines in tuning): −97s.

**Tuning run ≈ 350s → ~120s**, with zero effect on selection or DAG output. None require
re-validation. That is the whole zero-risk envelope; everything below is extra parallelism.

---

# PARALLELIZATION GUIDE — where concurrency is SAFE vs. UNSAFE

Parallelism helps only for **independent, CPU-bound, side-effect-free** work. Here is the
map for TaxoArena, with the traps called out.

## ✅ SAFE and worthwhile

### P1 — Per-condition validation loop (MAIN + 3 baselines)
`HeadlessBenchmarkRunner.kt:463–493` runs `runHeadlessTrickle` for MAIN, KMEANS, WARD,
RANDOMNULL **sequentially**. These are **independent** — different snapshots, different
output CSVs, shared read-only dataset (already hoisted via `hoistedFullByDomain`). They can
run concurrently:
```
val results = listOf("MAIN" to root, "KMEANS_BASELINE" to kmeansRoot, ...)
    .map { (cond, r) -> async(Dispatchers.Default) { cond to runHeadlessTrickle(r, cond, ...) } }
    .awaitAll().toMap()
```
**Guard:** each `runHeadlessTrickle` must write to a **distinct** output path (it does — path
includes condition name) and must not mutate shared `taxonomyService` state. NOTE: current
code calls `taxonomyService.setGraph(kmeansRoot)` before each — that's **shared mutable
state**, so you must pass the graph explicitly instead of setting it globally before
parallelizing. Fix that first, then P1 is safe. **Saving: ~3× on the validation phase.**

### P2 — Independent metric families within generateReport()
Clustering metrics (silhouette, Dasgupta), classification metrics (hierarchical F1),
structural metrics (Sackin), and DendrogramPurity are **independent computations** over the
same frozen DAG. They can be computed in parallel `async` blocks and joined. DendrogramPurity
dominates, so this helps only modestly unless combined with OPT-8 sampling.
**Guard:** all are read-only over the DAG → safe. **Saving: bounded by the slowest (Dendrogram).**

### P3 — Baseline snapshot generation (already a subprocess)
The Python baseline generator (97s) produces KMEANS/WARD/RANDOMNULL independently. If you keep
baselines, these three could be generated concurrently inside the subprocess. Lower priority
than just skipping them in tuning (OPT-1).

## ⚠️ ALREADY parallel — do NOT double-wrap

### The split phase (`TaxonomySplitter.splitNodesRecursive`)
Already `withContext(Dispatchers.Default)` + per-node `async` + (now) concurrent per-k EM.
**Do not add another layer.** In fact, watch for the OPT-4 hazard below.

## ❌ UNSAFE — will deadlock or corrupt

### D1 — Nested `runBlocking` on `Dispatchers.Default` (EXISTING HAZARD from your OPT-4)
`performVmfKMeans` now opens `= runBlocking { ... async(Dispatchers.Default) ... }` and is
called from inside the splitter's `Dispatchers.Default` coroutine. `Dispatchers.Default` has a
bounded pool (= cores). A blocked `runBlocking` occupying a Default thread while waiting for
`async(Dispatchers.Default)` children can **starve/deadlock** under concurrent splits.
**Fix before any parallel sweep:** make `performVmfKMeans` a `suspend fun` using
`coroutineScope { }` (joins the existing hierarchy, no thread blocking), OR dispatch the inner
`async` on a **separate** pool. Never block and fan-out on the same bounded dispatcher.

### D2 — Parallelizing DB writes to the same SQLite file
SQLite (even WAL) serializes writers. Parallel snapshot/ledger writes to the same DB will
contend or lock. Persistence is already fast (2.5s) — leave it sequential.

### D3 — Parallel condition runs that share `taxonomyService.setGraph()`
As noted in P1: the current pattern mutates a shared active graph before each condition. That
global mutable state makes naive parallelization a **data race**. Must refactor to pass the
graph per call before P1 is safe.

### D4 — Judge/arena LLM calls beyond configured parallelism
Already concurrency-controlled (`llmParallelism`, semaphore in the arena). Don't add ad-hoc
parallelism — you'll blow rate limits and the dual-call swap accounting.

---

## Recommended order

1. **OPT-7** (dedup finalization metrics) — ~70s, zero risk, no re-validation.
2. **OPT-1** (`runBaselines=false` in tuning configs) — ~97s, config-only.
3. **OPT-8** (gate/sample final metrics for tuning) — ~65s.
4. **D1 fix** (remove nested `runBlocking` deadlock hazard) — correctness, do before any
   parallel sweep even if no speed goal.
5. **P1** (parallel per-condition validation) — ~3× on validation, but ONLY after fixing the
   shared `setGraph` state (D3).
6. **P2** (parallel metric families) — modest, best combined with OPT-8 sampling.

**Sequencing rule unchanged:** OPT-7/OPT-1/OPT-8/P1/P2 do not alter DAG output → no
re-validation. The EM changes already landed DO alter output → your current finalists must be
re-validated against the post-EM pipeline regardless of these speed changes.
