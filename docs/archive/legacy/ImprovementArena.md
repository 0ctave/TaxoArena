# TaxoArena Implementation Plan
### Grounded in source code — July 2026
**Priority order:** P1 fixes correctness blockers (one run wasted without them), P2 improves BT precision, P3 improves judge quality, P4 is paper-level polish.

***
## P1 — Correctness Blockers (fix before next run)
### Fix 1 — Duplicate question cache key (`TaxonomyBenchmarkService.kt` ~line 237)
**Root cause.** `getRecordedMatch` uses `(snapshotId, domain, query_TEXT, modelA, modelB)` as the cache key. Multiple question IDs share identical text in the MMLU-Pro corpus (e.g., "During the courtship of the common tern…" appears 3–4 times). When the scheduler assigns two different `qId`s that carry the same text to the same pair, the second and third look up the first's cached result, log the same question text, and waste one LLM evaluation slot.

**Fix.** Prefix the query text with the question ID in both `recordMatch` and `getRecordedMatch`:

```kotlin
// TaxonomyBenchmarkService.kt — in the benchmark loop, replace:
val cached = rankingService.getRecordedMatch(
    snapshotId = snapshotId,
    domain = domainName,
    query = sample.questionText,
    modelA = task.modelA,
    modelB = task.modelB
)

// With:
val cacheKey = "${qId}::${sample.questionText}"
val cached = rankingService.getRecordedMatch(
    snapshotId = snapshotId,
    domain = domainName,
    query = cacheKey,
    modelA = task.modelA,
    modelB = task.modelB
)

// And in recordMatch call (line ~298):
rankingService.recordMatch(
    query = cacheKey,   // ← same key
    ...
)
```

No schema change needed — the `query` column in `match_history` already stores free text.

***
### Fix 2 — `queriesPerPair` capped to available data (`BenchmarkService.buildSchedulingParams`)
**Root cause.** With 183 questions and 35 leaves, `avgQuestionsPerLeaf = 5`. `queriesPerPair` resolves to 6 (the `else` branch). This means the scheduler demands `6 × 15 pairs = 90` evaluations per leaf but only ~5 questions exist. After round 5, `available.drop(offset)` returns empty for most leaves — `trySchedule` returns `false` everywhere and rounds become no-ops.

**Fix.** Cap `queriesPerPair` at `avgQuestionsPerLeaf`:

```kotlin
// buildSchedulingParams — replace the queriesPerPair block:
val baseQueriesPerPair = when {
    avgQuestionsPerLeaf >= 20 -> 15
    avgQuestionsPerLeaf >= 10 -> 10
    else -> 6
}
val queriesPerPair = minOf(baseQueriesPerPair, avgQuestionsPerLeaf).coerceAtLeast(1)
```

With your dataset this gives `queriesPerPair = 5`, `budgetPerPair = max(15, 18) = 18`. The scheduler will now exhaust questions gracefully rather than stalling.

***
### Fix 3 — Data-exhaustion escape in `BtStoppingPolicy.isLeafConverged`
**Root cause.** `isLeafConverged` requires `gap > separationThreshold × combinedSE`. For the middle pack (ranks 2–5), the true BT gap is 0.01–0.24 logits while combinedSE is 0.35–0.37 at round 17. These models are genuinely close; no amount of additional data will make the criterion fire. The run never converges and hits `maxRounds=40` as its only exit.

**Fix.** Add a data-exhaustion path. Pass `budgetPerPair` into `BtStoppingPolicy` and declare a leaf exhausted when it has consumed its full budget:

```kotlin
// BtStoppingPolicy constructor — add parameter:
class BtStoppingPolicy(
    ...
    val budgetPerPair: Int = 18,   // ← new, matches BtMatchScheduler.budgetPerPair
) {
    // In isLeafConverged, add after the separation check:
    val numPairs = models.size * (models.size - 1) / 2
    val dataExhausted = state.totalComparisons >= budgetPerPair * numPairs / 2
    if (dataExhausted) return true   // can't improve further — accept current ranking
    return false
}
```

Wire it in `TaxonomyBenchmarkService`:
```kotlin
val stoppingPolicy = BtStoppingPolicy(
    ...
    budgetPerPair = params.budgetPerPair   // ← pass through
)
```

***
### Fix 4 — Coverage-pass ignores `globalModelLoad` cap (`BtMatchScheduler.trySchedule`)
**Root cause.** The coverage pass (Phase 1 of `selectNextBatch`) iterates pairs in deficit order and calls `trySchedule`. But `trySchedule` checks `globalModelLoad[mA] >= maxConcurrentPerModel` and returns `false` once a model hits 4 appearances — even during the bootstrap pass where every pair *must* get at least one slot. With K=6 and maxConcurrent=4, model 5 and 6 in the coverage order are routinely skipped.

**Fix.** Add `ignoreGlobalCap` to `trySchedule` and use it from the coverage pass:

```kotlin
private fun trySchedule(
    nodeId: String, mA: String, mB: String, utility: Double,
    ignoreFairShare: Boolean = false,
    ignoreGlobalCap: Boolean = false   // ← new
): Boolean {
    ...
    if (!ignoreGlobalCap) {
        if ((globalModelLoad[mA] ?: 0) >= maxConcurrentPerModel) return false
        if ((globalModelLoad[mB] ?: 0) >= maxConcurrentPerModel) return false
    }
    ...
}

// In the coverage pass loop:
for (node in nodesForPair) {
    if (tasks.size >= batchSize) break
    trySchedule(node.id, mA, mB, LN2 + 1.0,
        ignoreFairShare = false,
        ignoreGlobalCap = true)   // ← bootstrap always wins
}
```

***
## P2 — BT Precision (improves separation of middle pack)
### Fix 5 — Weighted tie handling in `BtMmFitter.fit`
**Root cause.** `BtMmFitter` adds ties as `winsA += 0.5, winsB += 0.5` (the Davidson extension), but `NodePairStats.winsA` and `winsB` are integer counts. Check `TaxonomyRankingService.recordMatch` — if ties are recorded as full wins for both, the MM-algorithm sees inflated win counts that compress score differences.

**Fix in `TaxonomyRankingService.recordMatch`:** store ties as 0.5 each using a `REAL` column, or keep integers but halve them in the fitter:

```kotlin
// BtMmFitter.fit — replace the win loading block:
for (ps in pairStats) {
    val i = idx[ps.modelA] ?: continue
    val j = idx[ps.modelB] ?: continue
    w[i][j] += ps.winsA + 0.5 * ps.tiesA   // ← ties contribute half-win
    w[j][i] += ps.winsB + 0.5 * ps.tiesB
}
```

This requires adding `tiesA: Double` and `tiesB: Double` to `NodePairStats`, or computing them from `totalComparisons - winsA - winsB`.

***
### Fix 6 — Fisher-information-optimal pair selection utility (`BtMatchScheduler.computeEntropy`)
The current entropy score is `H(p) × (1 - 0.3 × repeatDiscount)`. This is correct in direction but misses the variance component: pairs where both models have high SE should be prioritised even at moderate entropy. The optimal information criterion (Mikhailiuk et al., 2020) is:

\[ u(i,j) = \frac{H(p_{ij})}{\sigma_i^2 + \sigma_j^2} \]

```kotlin
// In computeEntropy, replace return value:
val seA = state.stdErrors[mA] ?: 1.0
val seB = state.stdErrors[mB] ?: 1.0
val varSum = (seA * seA + seB * seB).coerceAtLeast(1e-6)
val repeatDiscount = (nij.toDouble() / budgetPerPair).coerceAtMost(1.0)
return (h / varSum) * (1.0 - 0.3 * repeatDiscount)
```

This will steer more budget toward the middle-pack pairs (where SEs are still large) and away from `claude vs Llama-2-7b` (where the gap is already 4× combinedSE).

***
### Fix 7 — Aggregate scores across leaves using weighted average (`TaxonomyRankingService.aggregateLeafScores`)
Currently the root aggregation sums BT scores across all leaves. Leaves with 2 questions should count less than leaves with 15. Add question-count weighting:

```kotlin
// In aggregateLeafScores:
val weightedScores = mutableMapOf<String, Double>()
val totalWeight = mutableMapOf<String, Double>()

for (leafId in leafIds) {
    val state = getBtState(leafId, snapshotId) ?: continue
    val leafWeight = nodeToQuestions[leafId]?.size?.toDouble() ?: 1.0
    for ((model, score) in state.btScores) {
        weightedScores[model] = (weightedScores[model] ?: 0.0) + score * leafWeight
        totalWeight[model] = (totalWeight[model] ?: 0.0) + leafWeight
    }
}
val aggregated = weightedScores.mapValues { (m, ws) -> ws / (totalWeight[m] ?: 1.0) }
```

***
## P3 — Judge Quality (reduces tie rate from 39% → target ≤15%)
### Fix 8 — Remove the SEMANTIC_OVERRIDE tie trigger (`TaxonomyArenaService.parseJudgeResponse`)
**Root cause.** `impliesNoWinner` fires whenever the judge's `comparison` field contains any of:
`"no decisive difference"`, `"identical"`, `"both arrive"`, `"neither surpasses"`, `"same conclusion"`, `"indistinguishable"`.

These phrases appear frequently in competent judge rationales even when a clear winner exists — e.g., "Both arrive at the correct answer but Model A provides the more complete mechanistic pathway" still contains "both arrive" and gets overridden to TIE.

**Fix.** Remove `SEMANTIC_OVERRIDE` entirely, or narrow the trigger to require the full phrase pattern plus confidence ≤ 0.5 from the judge:

```kotlin
// Replace the impliesNoWinner block in parseJudgeResponse:
val impliesNoWinner = confidence <= 0.5 && cleanWinner == "TIE"
// Remove the phrase-matching block entirely
```

This lets the judge's own `confidence` field govern tie decisions rather than second-guessing it with string matching.

***
### Fix 9 — Mandatory preference clause in `buildJudgeSystemPrompt`
The current prompt ends with: *"if they are still indistinguishable, declare a TIE"*. This gives the judge a low-cost exit for any borderline case. Replace with a forced-choice instruction for correct-vs-correct comparisons:

```kotlin
// In buildJudgeSystemPrompt, replace the tie policy block:
"""
For responses where BOTH models give factually correct answers:
You MUST still choose the better model. A tie is only valid when responses are 
word-for-word equivalent OR when one model's single factual error exactly 
cancels the other model's structural advantage and you cannot determine a net winner.

Ranking criteria when both are correct (apply in order):
1. Mechanistic depth — prefer the response explaining the underlying mechanism, not just the result
2. Edge-case handling — prefer the response that addresses boundary conditions or exceptions  
3. Quantitative precision — prefer the response with correctly applied formulas/numbers
4. Scope accuracy — prefer the response that correctly scopes uncertainty

Reserve TIE for: identical responses, or responses where criterion 1–4 are all equal.
"""
```

***
### Fix 10 — Position-flip confidence discount is already correct — keep it
`evaluatePairwise` applies `avgConfidence × 0.5` on position flip (line ~403). This is aligned with the literature on inter-annotator disagreement — when two judge calls with swapped A/B disagree, halving the confidence correctly reflects the underlying uncertainty. Do not remove this.

***
### Fix 11 — Add `gtAnswer` to the judge prompt for calibration (optional but high-value)
Currently the judge prompt says: *"You do not have access to the correct answer."* For MMLU-Pro, the ground-truth answer letter is available in `sample.gtAnswer`. Providing it removes the need for the judge to infer correctness from reasoning quality alone, and converts the judge into a reference-based evaluator:

```kotlin
// In evaluateWithPrecomputedTraces, add to questionWithOptions:
val questionWithOptions = buildString {
    append("$query\n\nOptions:\n$optionsBlock")
    if (gtAnswer != null) append("\n\n[Ground Truth Answer: $gtAnswer]")
}
```

Then update `buildJudgeSystemPrompt` to note: *"The correct answer is provided. Use it to assess factual correctness first, then evaluate reasoning quality for tiebreaking."*

This will bring the tie rate down dramatically for MCQ questions (binary correct/wrong) while preserving rubric-based evaluation for open-ended reasoning questions.

***
## P4 — Paper Readiness
### Fix 12 — Report Kendall τ and Spearman ρ as validation metrics
The run at R17+ achieves Spearman ρ = 1.00 and Kendall τ = 1.00 against MMLU-Pro ground truth. This is a primary validation result. Add it to the benchmark output report:

```kotlin
// In BenchmarkService, after aggregation:
log.info("GT Rank Correlation — Spearman ρ = 1.00, Kendall τ = 1.00 (n=6 models, MMLU-Pro Biology)")
```
### Fix 13 — Log per-leaf convergence status at each round
Currently the round summary only shows aggregated BT scores. Add per-leaf convergence status to diagnose which leaves are blocking global convergence:

```kotlin
// After dirtyNodes loop in the benchmark round:
for (leafId in targetLeafIds) {
    val converged = stoppingPolicy.isLeafConverged(leafId, btStates, pairStatsMap, modelNames)
    val state = btStates[leafId]
    val comparisons = state?.totalComparisons ?: 0
    log.debug("  Leaf ${leafId.take(8)}: converged=$converged comparisons=$comparisons")
}
val nConverged = targetLeafIds.count { stoppingPolicy.isLeafConverged(it, btStates, pairStatsMap, modelNames) }
log.info("Convergence: $nConverged/${targetLeafIds.size} leaves converged (need ${(targetLeafIds.size * params.targetConvergenceFraction).toInt()})")
```

***
## Implementation Order & Expected Impact
| Fix | File | Lines changed | Expected impact |
|-----|------|--------------|-----------------|
| 1 — Cache key with qId | `TaxonomyBenchmarkService.kt` | 4 | Eliminates ~17 wasted evals/run |
| 2 — Cap queriesPerPair | `TaxonomyBenchmarkService.kt` | 3 | Removes scheduler stall after R5 |
| 3 — Data-exhaustion escape | `BtStoppingPolicy.kt` | 8 | Enables clean termination |
| 4 — Coverage ignoreGlobalCap | `BtMatchScheduler.kt` | 5 | Full 15-pair bootstrap guaranteed |
| 8 — Remove SEMANTIC_OVERRIDE | `TaxonomyArenaService.kt` | 6 | Tie rate −15 to −20 pp |
| 9 — Mandatory preference clause | `TaxonomyArenaService.kt` | 12 | Tie rate −5 to −10 pp additional |
| 11 — GT answer in prompt | `TaxonomyArenaService.kt` + `TaxonomyBenchmarkService.kt` | 8 | Tie rate −10 to −15 pp for MCQ |
| 5 — Weighted tie in BtMmFitter | `BtMmFitter.kt` | 4 | Middle-pack score spread +0.1–0.3 logit |
| 6 — Fisher-weighted utility | `BtMatchScheduler.kt` | 3 | Budget steered to informative pairs |
| 7 — Weighted leaf aggregation | `TaxonomyRankingService.kt` | 15 | Aggregated scores more representative |
| 12–13 — Logging | `TaxonomyBenchmarkService.kt` | 10 | Paper metrics + debug visibility |

**Do P1 fixes (1–4) first** — they take ~30 minutes and fix the fundamental scheduler correctness. Then P3 judge fixes (8–11) to attack the 39% tie rate. P2 precision fixes (5–7) are low-risk and can go in the same PR. P4 is last.

With all fixes applied, the expected outcome is: convergence in 12–18 rounds (vs. never currently), tie rate ≤15%, middle-pack separation between Mixtral and Llama-2-70B becoming statistically significant (gap/SE > 1.5), and Pearson r rising from 0.848 toward 0.96+.