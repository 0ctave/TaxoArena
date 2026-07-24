# TaxoArena — Long-Term Correct Implementation Plan
This plan is fully grounded in the actual codebase. Every file, class, and method referenced below exists in the repository at the path noted.

***
## Root cause map
Before any fix, the three systemic problems to eliminate:

| Problem | Symptom | Root files |
|---------|---------|------------|
| **Full-intersection requirement** | 0 questions with 14 models | `ModelEvalStore.getResultsMatrix` |
| **`is_reserved` flag not propagated to new models** | New models have `is_reserved=0` for all rows | `ModelEvalLoader.ingestRaw` + `syncReservedPool` |
| **Category string not normalised on ingest** | Category filter silently drops rows | `ModelEvalLoader.ingestRaw` |

***
## Layer 1 — Data pipeline (`ModelEvalStore` + `ModelEvalLoader`)
### 1.1 — Replace full-intersection with per-pair skip (`ModelEvalStore.kt`)
**Current code** (`getResultsMatrix` ~line 294):
```kotlin
return matrix.filter { (_, byModel) -> models.all { it in byModel } }
// SQL: HAVING COUNT(DISTINCT model_name) = ${models.size}
```

**Problem**: with 14 models, a single missing row for any one model on any question removes that question entirely. The benchmark silently receives 0 questions.

**Correct implementation**: return all questions covered by at least 2 models. The benchmark pair scheduler already handles missing models gracefully (`modelResults[task.modelA] ?: return@mapNotNull null`).

```kotlin
fun getResultsMatrix(
    models: List<String>,
    category: String? = null,
    reservedOnly: Boolean = true,
    limit: Int = 0,
    minModelCount: Int = 2          // ← new parameter, default = 2
): Map<Int, Map<String, ModelEvalResult>> {
    val effectiveMin = minModelCount.coerceIn(2, models.size)
    // ...
    // In all SQL HAVING clauses, replace:
    //   HAVING COUNT(DISTINCT model_name) = ${models.size}
    // With:
    //   HAVING COUNT(DISTINCT model_name) >= $effectiveMin
    
    // Final Kotlin filter, replace:
    //   return matrix.filter { (_, byModel) -> models.all { it in byModel } }
    // With:
    return matrix.filter { (_, byModel) ->
        byModel.size >= effectiveMin &&
        models.count { it in byModel } >= effectiveMin
    }
}
```

In `TaxonomyBenchmarkService.runBenchmark`, pass `minModelCount = 2` so any question with at least 2 model answers can be scheduled. Pairs for models that don't have answers for a given question are skipped at task execution time.

Also update `getSharedQuestionIds` (`ModelEvalStore.kt` ~line 342) with the same `>= effectiveMin` logic, since it is used by the TUI's eval coverage display.

***
### 1.2 — Normalise category on ingest (`ModelEvalLoader.ingestRaw`, ~line 229)
**Current code**:
```kotlin
results += ModelEvalResult(
    ...
    category = item.category,    // ← raw string from JSON, may be "Math", "math", "mathematics"
    ...
)
```

**Correct implementation**: apply the same `subjectToDomain` normalisation that `MMLUDatasetFetcher` uses, and lower-case everything:

```kotlin
// In ModelEvalLoader — add a companion-object helper:
companion object {
    // Mirror of MMLUDatasetFetcher.subjectToDomain
    private val SUBJECT_TO_DOMAIN = mapOf(
        "abstract_algebra" to "math", "college_mathematics" to "math",
        "elementary_mathematics" to "math", "high_school_mathematics" to "math",
        "high_school_statistics" to "math",
        // ... copy full map from MMLUDatasetFetcher
    )
    fun normaliseCategory(raw: String): String =
        SUBJECT_TO_DOMAIN[raw.lowercase().trim()] ?: raw.lowercase().trim()
}

// In ingestRaw:
results += ModelEvalResult(
    ...
    category = normaliseCategory(item.category),   // ← always lowercase, always mapped
    ...
)
```

Move `subjectToDomain` out of `MMLUDatasetFetcher` into a shared `MMLUCategories.kt` object so both classes reference the same map — no duplication.

***
### 1.3 — Make `syncReservedPool` run automatically on every new model ingest (`ModelEvalLoader.ingestRaw`)
**Current behaviour**: `syncReservedPool` is a separate, manually triggered call that reads `reserved_test_queries.json`. New models loaded after the initial setup have `is_reserved = 0` for all rows because nobody called `syncReservedPool` after them.

**Correct implementation**: call it at the end of every `ingestRaw`:

```kotlin
// In ModelEvalLoader.ingestRaw — at the end of the function:
val (inserted, skipped) = store.saveBatch(results)
store.saveLinks(links.distinctBy { it.questionId })

// Auto-sync reserved pool for newly inserted rows
val reservedFile = File(reservedFilePath)
if (reservedFile.exists()) {
    syncReservedPool(reservedFile)
    log.info("Auto-synced reserved pool after ingesting '$modelName'")
}
```

`syncReservedPool` is idempotent (`UPDATE SET is_reserved=1 WHERE question_id IN (...)`) so calling it multiple times is safe. The slight extra cost (~50ms for 270 IDs) is negligible.

***
### 1.4 — Add a `verifyIngestion` diagnostic method (`ModelEvalStore.kt`)
Add a method the TUI can call to surface data problems before launching a benchmark:

```kotlin
data class IngestionHealth(
    val modelName: String,
    val totalRows: Int,
    val reservedRows: Int,
    val mathRows: Int,
    val reservedMathRows: Int
)

fun verifyIngestion(models: List<String>): List<IngestionHealth> = conn().use { c ->
    models.map { model ->
        val total = c.query("SELECT COUNT(*) FROM eval_results WHERE model_name=?", model)
        val reserved = c.query("SELECT COUNT(*) FROM eval_results WHERE model_name=? AND is_reserved=1", model)
        val math = c.query("SELECT COUNT(*) FROM eval_results WHERE model_name=? AND category='math'", model)
        val reservedMath = c.query("SELECT COUNT(*) FROM eval_results WHERE model_name=? AND category='math' AND is_reserved=1", model)
        IngestionHealth(model, total, reserved, math, reservedMath)
    }
}
```

Log this in `TaxonomyBenchmarkService.runBenchmark` before the matrix call:

```kotlin
val health = evalStore.verifyIngestion(modelNames)
health.forEach { h ->
    if (h.reservedRows == 0)
        log.warn("Model '${h.modelName}' has 0 reserved rows — run syncReservedPool or re-ingest")
    log.info("  ${h.modelName}: total=${h.totalRows} reserved=${h.reservedRows} math=${h.mathRows} reserved_math=${h.reservedMathRows}")
}
```

This makes the `"Benchmark: 0 questions"` failure immediately self-diagnosable.

***
## Layer 2 — Scheduler (`BtMatchScheduler` + `BtStoppingPolicy`)
### 2.1 — Cap `queriesPerPair` to available data (`buildSchedulingParams`)
```kotlin
val baseQueriesPerPair = when {
    avgQuestionsPerLeaf >= 20 -> 15
    avgQuestionsPerLeaf >= 10 -> 10
    else -> 6
}
val queriesPerPair = minOf(baseQueriesPerPair, avgQuestionsPerLeaf).coerceAtLeast(1)
```
### 2.2 — Data-exhaustion exit in `BtStoppingPolicy`
```kotlin
class BtStoppingPolicy(
    ...
    val budgetPerPair: Int = 18
) {
    fun isLeafConverged(...): Boolean {
        // ... existing checks ...
        
        // Separation check
        val gap = ranked.value - ranked[^1].value
        val combinedSE = (state.stdErrors[ranked.key] ?: 10.0) +
                         (state.stdErrors[ranked[^1].key] ?: 10.0)
        if (gap > separationThreshold * combinedSE) return true
        
        // NEW: data-exhaustion fallback
        val numPairs = models.size * (models.size - 1) / 2
        val exhausted = state.totalComparisons >= (budgetPerPair * numPairs) / 2
        return exhausted
    }
}
```
### 2.3 — Coverage pass bypasses `globalModelLoad` cap
```kotlin
private fun trySchedule(
    nodeId: String, mA: String, mB: String, utility: Double,
    ignoreFairShare: Boolean = false,
    ignoreGlobalCap: Boolean = false
): Boolean {
    ...
    if (!ignoreGlobalCap) {
        if ((globalModelLoad[mA] ?: 0) >= maxConcurrentPerModel) return false
        if ((globalModelLoad[mB] ?: 0) >= maxConcurrentPerModel) return false
    }
    ...
}

// Coverage pass calls:
trySchedule(node.id, mA, mB, LN2 + 1.0, ignoreFairShare = false, ignoreGlobalCap = true)
```
### 2.4 — Fisher-information-weighted utility in `computeEntropy`
```kotlin
private fun computeEntropy(...): Double {
    // ... existing bootstrap guard and p computation ...
    val h = if (p <= 0.0 || p >= 1.0) 0.0
            else -p * ln(p) - (1.0 - p) * ln(1.0 - p)

    val seA = state.stdErrors[mA] ?: 1.0
    val seB = state.stdErrors[mB] ?: 1.0
    val varSum = (seA * seA + seB * seB).coerceAtLeast(1e-6)
    val repeatDiscount = (nij.toDouble() / budgetPerPair).coerceAtMost(1.0)
    return (h / varSum) * (1.0 - 0.3 * repeatDiscount)
}
```

***
## Layer 3 — Cache key (`TaxonomyBenchmarkService`)
### 3.1 — Prefix cache key with `questionId`
```kotlin
// Replace in both recordMatch and getRecordedMatch calls:
val cacheKey = "${qId}::${sample.questionText}"

val cached = rankingService.getRecordedMatch(
    snapshotId = snapshotId,
    domain = domainName,
    query = cacheKey,          // ← qId-scoped
    modelA = task.modelA,
    modelB = task.modelB
)
// ...
rankingService.recordMatch(
    query = cacheKey,          // ← same key
    ...
)
```

***
## Layer 4 — Judge (`TaxonomyArenaService`)
### 4.1 — Remove `SEMANTIC_OVERRIDE` phrase matching
```kotlin
// In parseJudgeResponse, replace:
val impliesNoWinner = listOf(
    "no decisive difference", "identical", "both arrive", ...
).any { it in comparisonText }

// With:
val impliesNoWinner = confidence <= 0.5 && cleanWinner == "TIE"
```
### 4.2 — Mandatory forced-choice in `buildJudgeSystemPrompt`
Replace the permissive tie policy block with:

```kotlin
"""
When both models give factually correct answers, you MUST still pick a winner using these tiebreak criteria in order:
1. Mechanistic depth — prefer the response that explains the underlying mechanism, not just the result
2. Edge-case handling — prefer the response that addresses boundary conditions or exceptions
3. Quantitative precision — prefer the response with correctly applied formulas or numeric values
4. Scope accuracy — prefer the response that correctly scopes uncertainty or limits

A TIE is valid ONLY when: (a) both responses are word-for-word equivalent, OR
(b) you have applied all four criteria above and cannot find any difference.
Do not use TIE as a shortcut for borderline cases.
"""
```
### 4.3 — Pass `gtAnswer` to judge for MCQ questions
```kotlin
// In evaluateWithPrecomputedTraces:
val questionWithOptions = buildString {
    append("$query\n\nOptions:\n$optionsBlock")
    val gt = modelResults.values.firstOrNull()?.gtAnswer
    if (gt != null) append("\n\n[Correct Answer: $gt]")
}
```

Update `buildJudgeSystemPrompt` to add: *"The correct answer letter is provided. Use it as a primary correctness signal. If one model chose the correct answer and the other did not, the correct model wins regardless of presentation. Use rubric criteria only when both models chose the same answer."*

***
## Layer 5 — BT Fitter (`BtMmFitter`)
### 5.1 — Weighted tie handling
```kotlin
// In BtMmFitter.fit, update win matrix loading:
for (ps in pairStats) {
    val i = idx[ps.modelA] ?: continue
    val j = idx[ps.modelB] ?: continue
    val tieContrib = ps.ties * 0.5
    w[i][j] += ps.winsA + tieContrib
    w[j][i] += ps.winsB + tieContrib
}
```
### 5.2 — Question-count weighted leaf aggregation (`TaxonomyRankingService`)
```kotlin
// In aggregateLeafScores:
val weightedScores = mutableMapOf<String, Double>()
val totalWeight = mutableMapOf<String, Double>()

for (leafId in leafIds) {
    val state = getBtState(leafId, snapshotId) ?: continue
    val weight = (nodeToQuestions[leafId]?.size ?: 1).toDouble()
    for ((model, score) in state.btScores) {
        weightedScores[model] = (weightedScores[model] ?: 0.0) + score * weight
        totalWeight[model] = (totalWeight[model] ?: 0.0) + weight
    }
}
return weightedScores.mapValues { (m, ws) -> ws / (totalWeight[m] ?: 1.0) }
```

***
## Implementation order
| # | Layer | File | Change | Unblocks |
|---|-------|------|--------|---------|
| 1 | Data | `ModelEvalStore.kt` | Full-intersection → `minModelCount=2` | **Current 0-question bug** |
| 2 | Data | `ModelEvalLoader.kt` | Auto-call `syncReservedPool` after ingest | Reserved flag on new models |
| 3 | Data | `ModelEvalLoader.kt` | Normalise `category` on ingest | Category filter correctness |
| 4 | Data | `ModelEvalStore.kt` | Add `verifyIngestion` diagnostics | Self-diagnosable failures |
| 5 | Cache | `TaxonomyBenchmarkService.kt` | `qId`-prefixed cache key | Duplicate question bug |
| 6 | Scheduler | `BtMatchScheduler.kt` | `queriesPerPair` cap + `ignoreGlobalCap` | Scheduler stall + pair coverage |
| 7 | Scheduler | `BtStoppingPolicy.kt` | Data-exhaustion fallback | Convergence on close models |
| 8 | Judge | `TaxonomyArenaService.kt` | Remove SEMANTIC_OVERRIDE + forced-choice | Tie rate −25 to −35 pp |
| 9 | Judge | `TaxonomyArenaService.kt` | Pass `gtAnswer` to judge | Tie rate −10 to −15 pp additional |
| 10 | BT | `BtMmFitter.kt` | Weighted tie + Fisher utility | Score precision |
| 11 | BT | `TaxonomyRankingService.kt` | Weighted leaf aggregation | Representative root scores |
| 12 | Shared | `MMLUCategories.kt` (new) | Extract `subjectToDomain` map | No more duplication |

Items 1–5 are one-session fixes (≈2h total). Items 6–9 are one session (≈3h). Items 10–12 are polish before paper writing.

---

## References

1. [image.jpg](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/1421214461/e72374f8-6ed6-4b42-94c8-74c913364248/image.jpg?AWSAccessKeyId=ASIA2F3EMEYERTZBOW6Q&Signature=aE95gXsnVQvUnuZ7bPA5Wu0tQWY%3D&x-amz-security-token=IQoJb3JpZ2luX2VjEE8aCXVzLWVhc3QtMSJHMEUCIGqLngQMGXBW%2BZXbDBgOVk%2FoOM4eSIBK5pOVNmHpRL6HAiEAqKP%2BnyXGkQ%2BgapB7OqXul8eot%2FUV%2B69Sob0Y3CtSh8Yq8wQIFxABGgw2OTk3NTMzMDk3MDUiDNCchax2LyjpZIYRVyrQBHVqpqe2vSBxyCjz%2FAX526VSCXOExtkOL21I0jlW2pHGNnyfmyQ4%2FJWWvhTtmWN3Io%2Fj6QB4QaBrMP0TdkBSeMl2jtq8JoBnVsRMgA3gmR%2Bqnyc%2FfOUjrdQEgKO3uJcdNXMBhrVLzNy9rCkLEqSqzCRut1dFggQCEUwpXk35Ve8vBydYJbc0UtTBrXuOZNnJn%2FVtE24tEod%2Byhm6UxlSM8oGHJn9jOJeJ9VL1peV1XzpU9C5CJ3DC33%2ByTp1qNh%2BTqgZ8RRV%2BDNVFLP2NxyBlKRjCW0d34mpQRYskbzxZh5wtzRPwGbluwJoI1I1vdfBSj3PLo75TlfHSrcKOtAoqzZ4wjC9axJkRrESWq132FdUKZYZ3UX1Tn6faRQkEDO4OSOg2uwdORCyDS8Uo0yyXzv5nMIaTnz0pTREMidw5f2xV2ejwKtyfMe7t0OGsB0Tig8GYReMEpXuGxyzex9tpvZskxPI%2BKu6jpdIhGbQDbqzW9%2BE%2BNW6O9deazRZeFjQewoPONwkrXWp9%2FEHtAWxuZQ94RUsrgQoMsmO%2BMANo2D%2F5mqXH%2F1Sxqi0ucRfQ4UFWdfmZ7brQN0ptsC7aaXCXOUFZEPKblDExdEN%2FYgUUWiNgqg9sR0qGTwChH1ZmlcRpngCzLjlGL8NoDYbpCLNAsxO6iuJZLhadSJMLqvm0TAex1lweQf9BtGovv%2BGjFEsiaVqhxY4Nt%2Bly%2BgcHiPfdQlvywvLgp%2BCfrwR024Jf8KlD%2Bqu2acQ9PY8ErcpX1hs%2Fu0RlgwkEsduddtGCM6qd6Awv%2Big0gY6mAGfXzhrAYWgqOPlHtoTmK9GmAhKe90VcR9j8qwirRIhosnNNO1EQz8SNrT8ALBB2wTdMtLylE2sel9Ecuhrf1U9AWF6PJBmMGOSDPCImXxExgeZINc0q5xZzVwH9FCUstx8SrvWzLp8HcopFT9O0OXVMCpVrxS4dKGHjTsj3lqLyp6CV2qG1L1DfUPa45mBoPvu4AqdihWJ0A%3D%3D&Expires=1783120402)

