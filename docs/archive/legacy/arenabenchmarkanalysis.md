# TaxoArena Arena Benchmark — Run v3 Analysis (commit e6aba61d)

## What Changed in This Commit

Three files were modified. Two critical fixes landed, one critical fix did **not** land.

| File | Change | Effect |
|------|--------|--------|
| `TaxonomyBenchmarkService.kt` | `selectTargetNodes(maxNodes=100)` called **once before** the round loop; frozen list reused every round | ✅ Bug 1 fixed — evaluatedCount now advances |
| `BtMatchScheduler.kt` | `batchSize` parameter source changed | ✅ All 6 pairs now schedulable |
| `TaxonomyArenaService.kt` | Minor edits (position-flip logging added) | ✅ Flip detection now logged |
| `TaxonomyArenaService.kt` | `parseJudgeResponse` when-block: **TIE still absent** | ❌ Bug A not fixed |
| `TaxonomyArenaService.kt` | Judge prompt: **"Ties are strictly forbidden"** still present | ❌ Bug B not fixed |

***

## Run Summary

```
Start:    17:08:54  —  End: 17:17:52  (~9 minutes)
Models:   Llama-2-70b-hf, Llama-2-7b-hf, Meta-Llama-3-8B, Meta-Llama-3-70B
Rounds:   8  (rounds 0–7)
Queries:  64 total · 6 pairs · coverage 1.000
Judge-agreement: 0.797  ← significant improvement from 0.609
```

### Final BT Scores (Round 7)

| Model | Score | SE |
|-------|-------|----|
| Meta-Llama-3-70B | +0.700 | ±0.392 |
| Meta-Llama-3-8B | +0.332 | ±0.352 |
| Llama-2-70b-hf | −0.163 | ±0.328 |
| Llama-2-7b-hf | −0.869 | ±0.505 |

### Per-Pair Results

| Pair | JudgeA | JudgeB | Ties | Agreement | AvgConf |
|------|--------|--------|------|-----------|---------|
| 70b-hf vs 7b-hf | 5 | 1 | 0 | 0.800 | 0.872 |
| 70b-hf vs 3-8B | 2 | 5 | 0 | **0.875** | 0.894 |
| 70b-hf vs 3-70B | 1 | 9 | 0 | 0.688 | 0.943 |
| 7b-hf vs 3-8B | 0 | 4 | 0 | **0.750** | 0.905 |
| 7b-hf vs 3-70B | 0 | 1 | 0 | 1.000 | 0.875 |
| 3-8B vs 3-70B | 1 | 2 | 0 | **0.833** | 0.985 |

***

## What Is Now Working

### ✅ Bug 1 Fixed — Target Nodes Frozen, evaluatedCount Advances

The log confirms the fix at 17:08:54:
```
Selected fixed targetNodes for the entire run: [Organizational Behavior and Work Motivation Theories,
Lifespan Development and Behavioral Determinants, Mendelian and Quantitative Genetics Problems, ...]
```
25 leaf nodes are locked for the entire run. The scheduler now cycles through different questions across rounds: Round 0 uses q2807/q2809, Round 1 uses q2807/q2831, Round 2 uses q2812/q2844/q2848, and so on. **New question IDs appear each round** — q2831, q2844, q2848, q2849, q2852, q2857, q2862, q2869, q2873, q2884, q2889, q2890. The querySlice is finally advancing as intended.

### ✅ All 6 Pairs Now Scheduled

Every pair appears in the run results. `Meta-Llama-3-8B vs Meta-Llama-3-70B` receives 3 decisive evaluations (previously 0). `Llama-2-7b-hf vs Meta-Llama-3-70B` gets 1. The BT matrix is now fully connected, making the ranking globally comparable rather than only within sub-chains.

### ✅ Position Flip Detection Now Logged

`Position flip detected for pair X vs Y on node Z` appears correctly throughout the log. Flip rate is notably high — see analysis below.

### ✅ Judge-Agreement: 0.533 → 0.609 → 0.797

The jump from 0.609 to 0.797 is the largest single improvement across all three runs. It directly reflects fixing Bug 1: now that different questions are evaluated each round, the judge is no longer stuck on the same 2 questions where it systematically disagreed with ground truth.

***

## Remaining Issues

### 🔴 Critical: Bug A + Bug B Still Present — TIE Structurally Impossible

**Both the parser and the prompt are unchanged on this dimension.**

In `parseJudgeResponse`:
```kotlin
val cleanWinner = when (rawWinner.uppercase()) {
    "MODEL A" -> "Model A"
    "MODEL B" -> "Model B"
    else -> "INVALID"    // ← "TIE" still hits INVALID
}
```

In `buildJudgeSystemPrompt`:
```
Tie-break rules — you MUST output "Model A" or "Model B". Never "tie", "draw", or "equal":
```

In `buildJudgeUserPrompt`:
```
You MUST compare both models and choose a winner. Ties are strictly forbidden.
```

**Direct consequence in this run:** The summary line `Llama-2-70b-hf vs Llama-2-7b-hf: judgeA=5 judgeB=1 ties=0` shows **zero TIE outcomes** across all 6 pairs. This is implausible for 64 evaluations — some model pairs should agree on at least some questions. The `ties=0` counter reflects that TIEs only enter through the position-flip path (`positionFlip=true → winner="TIE"`), not through the judge voluntarily emitting a tie verdict. Any case where both models genuinely answer identically forces the judge to pick Model A or Model B via the positional tie-break — inflating false wins exactly as demonstrated in the previous session's Option G example.[^1][^2]

**The fix (unchanged from previous recommendation):**
```kotlin
// parseJudgeResponse:
val cleanWinner = when (rawWinner.uppercase()) {
    "MODEL A" -> "Model A"
    "MODEL B" -> "Model B"
    "TIE", "DRAW", "EQUAL" -> "TIE"   // ← add this line
    else -> "INVALID"
}

// Add semantic override:
val comparisonText = (element["comparison"]?.jsonPrimitive?.content ?: "").lowercase()
val impliesNoWinner = listOf("no decisive difference", "identical", "both arrive",
    "neither surpasses", "same conclusion", "indistinguishable").any { it in comparisonText }
val finalWinner = if (impliesNoWinner) "TIE" else cleanWinner
val finalConfidence = if (impliesNoWinner) minOf(0.5, confidence) else confidence
```

```
// buildJudgeSystemPrompt — replace tie-break section:
"If both models demonstrate equivalent reasoning: output winner: \"TIE\", confidence ≤ 0.5.
Only declare a decisive winner when one model has measurably stronger intermediate steps."

// buildJudgeUserPrompt — replace:
"Ties are strictly forbidden."
// With:
"If both models are genuinely equivalent, output winner: \"TIE\" with confidence ≤ 0.5."
```

***

### 🟡 High Position-Flip Rate from Org Behavior Node

Every round contains multiple `Position flip detected ... on node Organizational Behavior and Work Motivation Theories` lines, systematically accompanied by `evaluation confidence X is below confidenceGate 0.5`. The flip rate on this node is visibly higher than on domain-correct nodes (Molecular Genetics, Mendelian Genetics, etc.).

This is the Bug 2 residual: the Org Behavior node is still being invoked as a judge on biology questions, and because it has no relevant rubric, it essentially flips randomly between the two swap trials. The flip → LOW_CONFIDENCE_TIE pipeline correctly discards these at the `confidenceGate`, so the contamination is **contained but not eliminated**. The wasted LLM calls and noise in the position-flip counter remain.

**Count from this run:** approximately 20+ flip events, the majority on Org Behavior. Each flip costs 2 LLM calls + discards the result. Tightening the routing threshold to 0.75 for secondary judges (or filtering by domain category matching `req.category`) would eliminate these wasted calls.

***

### 🟡 Confidence Bimodality Persists — Overconfidence at 0.95–1.0

Despite the judge now correctly emitting TIEs via the position-flip mechanism for uncertain cases (0.25–0.49 confidence), the decisive verdicts cluster heavily at 0.95–1.0:
- Round 3: `Model B (confidence: 1.0)` × 3 separate evaluations
- Round 4: `Model B (confidence: 0.975)`, `Model A (confidence: 0.975)`, `Model B (confidence: 1.0)`
- Round 5: `Model B (confidence: 1.0)`, `Model B (confidence: 0.925)`
- Round 6: `Model A (confidence: 0.99)`, `Model B (confidence: 0.99)`, `Model B (confidence: 0.95)`

A confidence of 1.0 means the judge claims zero probability of error. On MMLU-Pro Biology open-response questions, this is not credible — even expert human raters rarely assign perfect confidence. These inflated values propagate directly into `winsA += 1.0` / `winsB += 1.0` in the BT MM fitter, giving individual evaluations excessive weight. The `avgConf=0.985` for the `3-8B vs 3-70B` pair (only 3 evaluations!) means the BT score for that pair is largely determined by 3 near-certain verdicts from a judge that was also flipping randomly on Org Behavior for the same pair in the same round.[^3][^4]

**Fix:** Add a maximum confidence cap in `evaluatePairwise`:
```kotlin
val finalConfidence = (if (positionFlip) avgConfidence * 0.5 else avgConfidence).coerceAtMost(0.95)
```
And add a prompt instruction: `"Reserve confidence 0.95–1.0 only for cases with overwhelming evidence. Default to 0.7–0.85 for clear wins."`[^5]

***

### 🟡 `evaluatedCount` Still Shows 0 in Scheduler Logs

The scheduler debug lines are no longer logged at INFO (they were removed or downgraded in this commit per the logging cleanup — they don't appear in this log). This means it's not possible to directly verify from the log whether `evaluatedCount` is now non-zero on re-visited nodes. The evidence is indirect: different question IDs appear each round, strongly implying the slice is advancing. However, a direct log line at DEBUG level confirming `evaluatedCount>0` would be useful to retain for verification.

***

### 🟡 Pair `7b-hf vs 3-70B` Has Only 1 Evaluation (BT Unreliable)

`judgeA=0, judgeB=1, ties=0, agreement=1.000, avgConf=0.875` — a single evaluation with 100% agreement is statistically trivial. The BT model needs at least ~4–6 comparisons per pair for reliable inference. This pair will have an inflated SE and may generate incorrect BT ordering if the one verdict happens to be wrong. The scheduler's utility function should explicitly penalise pairs with fewer than 4 comparisons to ensure minimum coverage before optimising for information gain.[^6][^7]

***

## BT Score Stability Assessment

| Round | 70B | 3-8B | 70b-hf | 7b-hf | Max Δ |
|-------|-----|------|--------|-------|-------|
| 0 | +1.099 | 0.000 | 0.000 | −1.099 | — |
| 1 | +0.937 | −0.193 | +0.123 | −0.867 | 0.193 |
| 2 | +0.871 | −0.054 | +0.322 | −1.139 | 0.272 |
| 3 | +0.876 | −0.058 | +0.143 | −0.961 | 0.179 |
| 4 | +0.742 | +0.182 | +0.138 | −1.062 | 0.240 |
| 5 | +0.750 | +0.239 | −0.064 | −0.925 | 0.202 |
| 6 | +0.733 | +0.349 | −0.137 | −0.946 | 0.110 |
| 7 | +0.700 | +0.332 | −0.163 | −0.869 | 0.049 |

The max Δ across models between consecutive rounds drops to **0.049** by Round 7, indicating near-convergence on the ordering `70B > 3-8B > 70b-hf > 7b-hf`. The SE values are narrowing correctly: 70B goes from ±1.633 → ±0.392, Llama-2-70b-hf from ±0.894 → ±0.328. However, the `7b-hf` SE remains wide (±0.505) because it only has 6 total verdicts across all pairs — the scheduler is underserving the weakest model.

***

## Priority Fix List

| Priority | Issue | File | Effort |
|----------|-------|------|--------|
| 1 | Add `"TIE"` to `parseJudgeResponse` when-block | `TaxonomyArenaService.kt` | 1 line |
| 2 | Remove "Ties are strictly forbidden" from both prompts | `TaxonomyArenaService.kt` | 3 lines |
| 3 | Add semantic TIE override from `comparison` field text | `TaxonomyArenaService.kt` | ~8 lines |
| 4 | Cap confidence at 0.95 in `evaluatePairwise` | `TaxonomyArenaService.kt` | 1 line |
| 5 | Tighten secondary judge routing threshold to 0.75 | `TaxonomyArenaService.kt` | 1 line |
| 6 | Minimum 4 comparisons per pair before utility optimisation | `BtMatchScheduler.kt` | ~5 lines |

---

## References

1. [[PDF] A Systematic Study of Position Bias in LLM-as-a-Judge](https://aclanthology.org/2025.ijcnlp-long.18.pdf)

2. [Judging the Judges: A Systematic Investigation of Position Bias in...](https://openreview.net/forum?id=y3jJmrKWQ4) - LLM-as-a-Judge presents a promising alternative to human evaluators across various tasks, but inhere...

3. [Bias and Uncertainty in LLM-as-a-Judge Estimation](https://arxiv.org/html/2605.06939v1)

4. [The Coin Flip Judge? Reliability and Bias in LLM-as-a-Judge ... - arXiv](https://arxiv.org/html/2606.13685)

5. [A Survey on LLM-as-a-Judge - arXiv](https://arxiv.org/html/2411.15594v6)

6. [What Does Preference Learning Recover from Pairwise Comparison ...](https://arxiv.org/html/2602.10286v1) - The Bradley–Terry (BT) model is the predominant approach, modeling preference probabilities as a fun...

7. [[PDF] Experimental Design under the Bradley-Terry Model - IJCAI](https://www.ijcai.org/proceedings/2018/0304.pdf) - We study the following experimental design problem: given a budget of expert comparisons, and a set ...

