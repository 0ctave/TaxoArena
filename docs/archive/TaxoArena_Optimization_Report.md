# TaxoArena — Performance Optimization Report

Grounded in `run.log` (L9_001_seed42, full run 19:37:49→19:45:28 ≈ 7m39s) and verified
against repo commit `65a3c0b`. Every claim traces to a log timestamp or a code line.
No code was modified; this is a prioritized plan with exact locations.

---

## Executive summary — where the time actually goes

Total wall-clock ≈ **459s** for one L9 tuning config. Measured breakdown:

| Phase | Duration | Share | Nature |
|---|---|---|---|
| DAG build (Phase 4 splitting dominates) | ~165s | 36% | CPU (vMF EM) |
| Baseline generation (Python subprocess) | ~86s | 19% | subprocess + IO |
| Post-build validation / CSV / routing (×4 conditions) | ~132s | 29% | CPU + redundant IO |
| Startup, dataset load, misc | ~35s | 8% | IO |
| Snapshot DB save | ~2s | <1% | **not a bottleneck** |

**Two headline findings:**
1. **The database is NOT a bottleneck.** Snapshot persistence is ~1.8s for 184 nodes
   with vector-offloading — well-engineered, leave it alone.
2. **~48% of wall-clock is post-build validation + baselines that a *tuning* run does
   not need**, plus redundant per-condition dataset re-fetching. This is the biggest,
   cheapest win and requires only config + loop-hoisting changes, not algorithm work.

Optimization priority: (1) skip baselines in tuning, (2) EM iteration cap, (3) hoist
per-condition redundant IO, (4) intra-node split parallelism. In that order.

---

## OPT-1 — Skip baseline generation in tuning runs  [CONFIG — highest ROI, zero risk]

**Evidence.** Log shows this is `tuning/runs/L9_001_seed42` (a screen config), yet it
spent 19:41:49→19:43:16 (~86s) generating KMeans/Ward/RandomNull baseline snapshots via
a Python subprocess, then ~100s+ validating all three. `runBaselines=true` is the driver
(`HeadlessBenchmarkRunner.kt:75`, gated at `:452`).

**Why it's waste.** Baselines are a *fixed reference* computed once against your final
chosen DAG — they do not change per L9 config and contribute nothing to gate/Pareto
selection. Paying ~3min of baseline cost on every screen config means ~27min wasted
across a 9-config L9 sweep.

**Fix.** Set `runBaselines = false` in all sweep/screen configs. Compute baselines exactly
once, against the final canonical DAG, in a dedicated `C_baseline_arena` run.

**Expected saving.** ~186s per tuning config → the single largest reduction available.
Cuts each L9 run from ~459s to ~273s (−40%).

---

## OPT-2 — Cap / relax vMF EM iterations  [ENGINE — high ROI, low risk]

**Evidence.** Phase 4 (Adaptive Splitting) = 159,560ms = **97% of build time**.
Iteration 1 alone = 50,668ms (31% of build) — the signature of heavy per-node EM when
clusters are largest. Call chain: `TaxonomySplitter.splitNodesRecursive` →
`StatisticsUtils.performVmfKMeans` (k=2..4) → `runVmfEm`.

**Root cause.** `runVmfEm` (`StatisticsUtils.kt:369`) loops `for (iter in 0 until 200)`.
A convergence check exists (`StatisticsUtils.kt:394`: `abs(Δlikelihood) < 1e-5 → break`)
but the tolerance is very tight, so EM frequently runs far past practical convergence.
vMF EM on well-separated embedding clusters typically stabilizes in 15–40 iterations.

**Fix (two options, do both).**
- Lower the ceiling: `for (iter in 0 until 50)`.
- Relax the tolerance one order: `< 1e-4` at line 394.

**Verify first (5-min probe).** Before changing, add a debug log of the actual exit
iteration in `runVmfEm` and run once. If most calls already exit <50 via convergence, the
win is smaller and OPT-4 matters more. If they run to ~200, this is your biggest build win.

**Expected saving.** If EM is over-iterating as the pattern suggests, 40–60% of Phase 4 →
build drops from ~165s toward ~70–100s.

**Caveat.** This is an engine change; fewer EM iterations can slightly shift cluster means,
so **re-run tuning validation after applying**, and do NOT apply after locking the final DAG.

---

## OPT-3 — Hoist per-condition redundant IO out of the validation loop  [ENGINE — med ROI]

**Evidence.** `runHeadlessTrickle` is called once per condition (`HeadlessBenchmarkRunner.kt:317`
loop; baselines at `:452`), and each call independently:
- re-runs `datasetFetcher.fetchDataset(...)` (`:589`) — log shows "Fetched 12000 MMLU Pro
  queries" *during* WARD validation (19:44:27), long after startup load.
- re-resolves the reserved pool + re-syncs `is_reserved` flags — log shows
  "Reserved pool reset: 3551 questions" and "Re-synced is_reserved flags" repeating per
  baseline (19:43:33, 19:44:21, …).

For 4 conditions (MAIN + 3 baselines) that's the same 12k-query fetch and 3551-flag sync
done ~4×.

**Fix.** Hoist the dataset fetch and reserved-pool resolution *above* the condition loop;
compute once, pass the in-memory result into `runHeadlessTrickle`. The reserved set and
full dataset are identical across conditions for a given seed — there is no correctness
reason to recompute per condition.

**Expected saving.** ~3× redundant 12k fetches + flag syncs eliminated → ~20–40s per
multi-condition run. Larger if `fetchDataset` hits disk each time.

**Note.** Only matters when running multiple conditions (i.e., the baseline/arena runs).
If OPT-1 removes baselines from tuning, this optimization's value concentrates in the
final baseline/arena run — still worth doing there.

---

## OPT-4 — Parallelize *within* large-node splits  [ENGINE — med ROI, addresses iter-1 spike]

**Evidence.** `splitNodesRecursive` (`TaxonomySplitter.kt:51`) parallelizes *siblings at the
same depth* (`nodesAtDepth.map { async {...} }`). At iteration 1 there are very few nodes
(splitting root / top handful), so there's almost nothing to parallelize — one huge node
runs effectively serially. This is exactly why iter-1 = 50.7s vs steady-state ~6s.

**Fix.** Parallelize *inside* a large node's split: the `for (k in 2..maxK)` loop in
`performVmfKMeans` runs independent `runVmfEm` calls per k — dispatch them concurrently so
the biggest, slowest node uses multiple threads instead of only benefiting when siblings
exist. Optionally add k-means++ warm-start (k=3 reuses k=2's converged centers) to avoid
three independent from-scratch EM runs.

**Expected saving.** Directly targets the iteration-1 serial spike (~31% of build). Combined
with OPT-2, build could approach ~60–80s.

**Caveat.** Engine change; same re-validation requirement as OPT-2.

---

## OPT-5 — Early-reject infeasible k before running EM  [ENGINE — low ROI, cheap]

**Evidence.** `performVmfKMeans` runs full EM for each k in 2..4, then checks `minClusterSize`
*after* (`StatisticsUtils.kt` post-EM cluster-size reject). A node barely above 2×minClusterSize
cannot satisfy a k=3/k=4 split, yet still pays full EM for those k's.

**Fix.** Pre-cap `maxK = min(maxK, n / minClusterSize)` per node before the loop, skipping EM
runs that cannot possibly pass the floor.

**Expected saving.** Small in aggregate (helps small nodes, which are already fast), but
free and safe. Do it alongside OPT-4 while touching the same function.

---

## What is NOT worth optimizing (verified)

- **Snapshot DB persistence** — ~1.8s/184 nodes, vector-offloaded. Not a bottleneck.
  Do not invest in the persistence layer.
- **`calculateDasguptaDeltaK`** (`StatisticsUtils.kt:159`) — already O(N·d), single-pass.
  Clean. Not the hotspot despite being in the split path.
- **Trickle routing** (Phase 3) — 1,964ms total (1.2%). Fine.
- **Refit / Hierarchy Optimization / Passthrough** — all <2% combined.

---

## Saved-data usefulness audit (the second question)

**Useful — keep:** the snapshot (structure + offloaded vectors), MAIN validity/quality/
bridge CSVs, tuning ledger row, routing-calibration CSV. These are your actual results and
directly feed Ch6.

**Wasteful in tuning runs — cut:** per-config baseline snapshots (OPT-1), the ~19 per-
condition CSVs written for baselines during *screen* runs (KMEANS/WARD/RANDOMNULL_*.csv) —
these are only meaningful for the final DAG, not for each L9 point. Redundant per-condition
dataset fetches and reserved-flag syncs (OPT-3) produce no new saved data at all — pure
recompute.

**Verdict:** the data saved is useful; the *recomputation and per-config baseline export* is
where the waste is — not in what's stored, but in how many times equivalent work runs.

---

## Recommended execution order

1. **OPT-1** (config, zero risk): `runBaselines=false` in sweep configs. −40% per tuning run
   immediately, no re-validation needed.
2. **OPT-2 verify-probe**: log EM exit iterations, confirm over-iteration. 5 minutes.
3. **OPT-2** (engine): cap EM at 50 + tolerance 1e-4, if probe confirms. Re-validate tuning.
4. **OPT-4 + OPT-5** (engine, same function): intra-node parallelism + early-k-reject.
   Re-validate.
5. **OPT-3** (engine): hoist dataset/reserved-sync above the condition loop — apply in the
   final baseline/arena run where multiple conditions actually run.

**Combined expected effect:** tuning run ~459s → ~180–220s (OPT-1 + OPT-2). Final arena/
baseline run additionally benefits from OPT-3.

**Sequencing rule:** OPT-1 and OPT-3 are safe anytime. OPT-2/4/5 change DAG output slightly
(EM path) — apply them BEFORE locking the final DAG, then re-run tuning validation, or not
at all. Never optimize the splitter after the canonical DAG is chosen.
