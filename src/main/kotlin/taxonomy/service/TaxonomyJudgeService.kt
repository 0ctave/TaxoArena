package taxonomy.service

import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.coroutineScope
import kotlinx.serialization.json.Json
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import taxonomy.config.TaxonomyConfig
import taxonomy.dataset.MMLUDatasetFetcher
import taxonomy.dataset.ModelEvalStore
import taxonomy.model.GraphNode
import taxonomy.operations.TaxonomyLlmClient
import taxonomy.prompts.JudgePrompts
import kotlin.math.abs

@Service
class TaxonomyJudgeService(
    private val datasetFetcher: MMLUDatasetFetcher,
    private val llmClient: TaxonomyLlmClient,
    private val config: TaxonomyConfig,
    private val arenaService: TaxonomyArenaService,
    private val evalStore: ModelEvalStore
) {
    private val log = LoggerFactory.getLogger("taxonomy.JudgeService")
    private val json = Json { ignoreUnknownKeys = true; isLenient = true }

    /**
     * Generates judges for all qualifying nodes in the DAG.
     *
     * @param root           Root of the DAG.
     * @param replaceExisting When true, regenerate judges even for nodes that already have one.
     * @param parallelismOverride When > 0, overrides [TaxonomyConfig.ExecutionConfig.llmParallelism]
     *   for this run only. The value is clamped to [1, llmParallelism] so it can never exceed the
     *   configured ceiling. Use 0 (default) to keep the config value.
     */
    suspend fun generateJudgesForDag(
        root: GraphNode,
        replaceExisting: Boolean = false,
        maxGenerality: Int = 0,
        parallelismOverride: Int = 0,
        onNodeComplete: (suspend (GraphNode) -> Unit)? = null
    ) = coroutineScope {
        log.info("Starting Grounded Agent Judge Induction (Replace: $replaceExisting, maxGenerality: $maxGenerality, parallelismOverride: $parallelismOverride)")
        val allNodes = mutableSetOf<GraphNode>()
        fun walk(n: GraphNode) { if (allNodes.add(n)) n.children.forEach { walk(it) } }
        walk(root)

        val distances = calculateDistancesFromLeaves(allNodes)

        val targetNodes = allNodes.filter { node ->
            val dist = distances[node.id] ?: 0.0
            dist <= maxGenerality &&
                (replaceExisting || node.judgePrompt == null) &&
                belongsToAnyDomain(node, config.llm.judgeDomains)
        }.sortedBy { it.depth }

        if (targetNodes.isEmpty()) {
            log.info("No nodes require judge generation.")
            arenaService.updateJudgeProgress("All Judges", 1, 1, "UP-TO-DATE")
            return@coroutineScope
        }

        val chunkSize = if (parallelismOverride > 0) {
            parallelismOverride.coerceAtLeast(1)
        } else {
            config.execution.llmParallelism
        }

        log.info("Generating judges for ${targetNodes.size} node(s) with parallelism=$chunkSize")
        targetNodes.chunked(chunkSize).forEach { chunk ->
            chunk.map { node ->
                async {
                    try {
                        generateJudgeForNode(node, onNodeComplete)
                    } catch (t: Throwable) {
                        log.error("Failed to generate judge for node '${node.label}' (id=${node.id}): ${t.message}", t)
                        arenaService.updateJudgeProgress(node.label ?: "Emergent Concept", 0, 1, "ERROR")
                    }
                }
            }.awaitAll()
        }
        log.info("Agent Judge induction complete.")
    }

    suspend fun generateJudgeForNodeById(root: GraphNode, nodeId: String) {
        val allNodes = mutableSetOf<GraphNode>()
        fun walk(n: GraphNode) { if (allNodes.add(n)) n.children.forEach { walk(it) } }
        walk(root)
        
        val node = allNodes.find { it.id == nodeId } ?: throw IllegalArgumentException("Node $nodeId not found")
        generateJudgeForNode(node)
    }

    private fun belongsToAnyDomain(node: GraphNode, domains: List<String>): Boolean {
        if (domains.isEmpty()) return true
        val visited = mutableSetOf<String>()
        fun walkUp(n: GraphNode): Boolean {
            if (!visited.add(n.id)) return false
            val label = n.label
            if (label != null && domains.any { it.equals(label, ignoreCase = true) }) {
                return true
            }
            return n.parents.any { walkUp(it) }
        }
        return walkUp(node)
    }

    private fun calculateDistancesFromLeaves(allNodes: Set<GraphNode>): Map<String, Double> {
        val distances = mutableMapOf<String, Double>()
        
        fun computeAvgDist(node: GraphNode): Double {
            if (node.isLeaf) {
                distances[node.id] = 0.0
                return 0.0
            }
            if (distances.containsKey(node.id)) return distances[node.id]!!
            
            val allLeafDistances = mutableListOf<Int>()
            fun collect(n: GraphNode, dist: Int, pathVisited: MutableSet<String>) {
                if (!pathVisited.add(n.id)) return
                if (n.children.isEmpty()) {
                    allLeafDistances.add(dist)
                } else {
                    n.children.forEach { collect(it, dist + 1, pathVisited) }
                }
                pathVisited.remove(n.id)
            }
            collect(node, 0, mutableSetOf())
            
            val avg = if (allLeafDistances.isNotEmpty()) allLeafDistances.average() else 0.0
            distances[node.id] = avg
            return avg
        }
        
        allNodes.forEach { computeAvgDist(it) }
        return distances
    }

    suspend fun generateJudgeForNode(
        node: GraphNode,
        onComplete: (suspend (GraphNode) -> Unit)? = null
    ) {
        // Bug 2 fix: for leaf nodes, use getAllQueriesInRegion() instead of node.queries directly.
        //
        // After the merger's evaluateCrossLinks pass, some leaf nodes receive training queries
        // exclusively via crossLinkChildren. Their node.queries list is empty in those cases,
        // causing details.isEmpty() and an early return with no judge generated.
        //
        // getAllQueriesInRegion() walks both tree children AND cross-link children, so it captures
        // the full corpus this leaf "covers" geometrically.  For non-leaf nodes we keep
        // getAllQueriesInBranch() (tree-only) because branch semantics are intentional there.
        val corpusEmbeddings = if (node.isLeaf) {
            node.getAllQueriesInRegion()
        } else {
            node.getAllQueriesInBranch()
        }.filter {
            abs(it.rawText.hashCode()) % 5 != 0
        }
        val detailsMap = datasetFetcher.getDetailsForQueries(corpusEmbeddings.map { it.rawText })
        val reservedTexts = evalStore.getReservedQuestionTexts()
        val resolved = corpusEmbeddings.mapNotNull { detailsMap[it.rawText] }
        val details = resolved.filter { it.question !in reservedTexts }

        // Supervised separation is the whole basis of the answer-key-blind-at-judgment claim:
        // rubrics are induced on the construction split and applied to the held-out split. But
        // `detailsMap` is keyed on Embedding.rawText while the filter tests HFProRowData.question,
        // so if those ever diverge the `!in` test compares different string spaces and silently
        // removes nothing — the same failure mode as joining on a raw id instead of question text.
        // Verified as matching (100% of active-pool reserved texts join mmlu_pro.question
        // verbatim), but an instruction is not a guarantee, so measure it rather than trust it.
        run {
            val heldOutInRegion = resolved.count { it.question in reservedTexts }
            val removed = resolved.size - details.size
            check(removed == heldOutInRegion) {
                "Judge induction held-out filter is inconsistent for node '${node.label}': " +
                    "counted $heldOutInRegion held-out questions but removed $removed. The filter " +
                    "and the membership test disagree, which means rubrics may be induced on " +
                    "questions this judge will later be asked to grade."
            }
            if (heldOutInRegion > 0) {
                log.info(
                    "[JUDGE-LEAK] node '${node.label}': withheld $heldOutInRegion of ${resolved.size}" +
                        " region question(s) from induction (held-out split)"
                )
            } else if (resolved.isNotEmpty()) {
                // Not an error — a node can legitimately contain no held-out queries — but worth
                // surfacing, because it is indistinguishable from a filter that stopped working.
                log.debug(
                    "[JUDGE-LEAK] node '${node.label}': no held-out questions among" +
                        " ${resolved.size} region question(s); nothing to withhold"
                )
            }
        }

        if (details.isEmpty()) {
            log.warn("generateJudgeForNode: empty corpus for node '${node.label}' (id=${node.id}). " +
                "queries=${node.queries.size}, crossLinkChildren=${node.crossLinkChildren.size}. Skipping.")
            arenaService.updateJudgeProgress(node.label ?: "Emergent Concept", 0, 1, "SKIPPED")
            return
        }

        val chunks = details.chunked(25)
        val chunksCount = chunks.size
        val hasSynthesis = chunksCount > 1
        val finalSteps = chunksCount + (if (hasSynthesis) 1 else 0) + 1 // +1 for final judge synthesis
        var currentStep = 0

        // PROGRESS TRACKING START
        arenaService.updateJudgeProgress(node.label ?: "Emergent Concept", currentStep, finalSteps, "BATCHING")

        val partialGuidelines = chunks.mapIndexed { index, batch ->
            val corpusStrings = batch.map { item ->
                val answerIndex = item.answer?.firstOrNull()?.let { it.uppercaseChar() - 'A' } ?: -1
                val choices = item.options.mapIndexed { i, opt ->
                    val letter = ('A' + i)
                    if (i == answerIndex) "$letter) $opt ✓" else "$letter) $opt"
                }.joinToString(" | ")
                val cot = item.cot_content?.trim() ?: ""
                buildString {
                    append("Q: ${item.question}\nChoices: $choices")
                    if (cot.isNotEmpty()) {
                        append("\nCorrect Reasoning: $cot")
                    }
                }
            }

            val result = llmClient.queryModel(
                config.llm.judgeModel,
                null,
                JudgePrompts.induceBatchGuidelines(corpusStrings, node.label ?: "General")
            )

            // UPDATE PROGRESS
            currentStep = index + 1
            arenaService.updateJudgeProgress(node.label ?: "Emergent Concept", currentStep, finalSteps, "INDUCTING")
            
            result
        }

        val masterGuidelines = if (chunksCount > 1) {
            arenaService.updateJudgeProgress(node.label ?: "Emergent Concept", currentStep, finalSteps, "SYNTHESIZING")
            val res = llmClient.queryModel(config.llm.judgeModel, null, JudgePrompts.synthesizeGlobalGuidelines(partialGuidelines))
            currentStep = chunksCount + 1
            arenaService.updateJudgeProgress(node.label ?: "Emergent Concept", currentStep, finalSteps, "SYNTHESIZING")
            res
        } else partialGuidelines.first()

        arenaService.updateJudgeProgress(node.label ?: "Emergent Concept", currentStep, finalSteps, "FINALIZING")
        val rawSynthesis = llmClient.queryModel(
            config.llm.judgeModel, null,
            JudgePrompts.synthesizeFinalJudge(masterGuidelines, node.label ?: "General")
        )
        currentStep = finalSteps - 1
        arenaService.updateJudgeProgress(node.label ?: "Emergent Concept", currentStep, finalSteps, "SAVING")
        
        // Correct-option text of every item the rubric was induced from — the strings a rubric
        // must not have memorised. Computed once for the leakage audit below.
        val sourceCorrectOptions = details.mapNotNull { item ->
            val ai = item.answer?.firstOrNull()?.let { it.uppercaseChar() - 'A' } ?: -1
            item.options.getOrNull(ai)
        }.filter { it.isNotBlank() }

        if (validateAndSaveJudge(node, rawSynthesis)) {
            auditRubricLeakage(node, sourceCorrectOptions)
            arenaService.updateJudgeProgress(node.label ?: "Emergent Concept", finalSteps, finalSteps, "READY")
            onComplete?.invoke(node)
        } else {
            // PHASE 3: AUTOMATED REPAIR
            log.warn("Judge JSON for '${node.label}' is malformed. Attempting LLM repair...")
            val repairSteps = finalSteps + 1
            arenaService.updateJudgeProgress(node.label ?: "Emergent Concept", finalSteps - 1, repairSteps, "REPAIRING")
            
            val repairedJson = llmClient.queryModel(config.llm.judgeModel, null, JudgePrompts.repairMalformedJson(rawSynthesis))
            currentStep = finalSteps
            arenaService.updateJudgeProgress(node.label ?: "Emergent Concept", currentStep, repairSteps, "SAVING")
            
            if (validateAndSaveJudge(node, repairedJson)) {
                auditRubricLeakage(node, sourceCorrectOptions)
                log.info("Successfully repaired judge JSON for '${node.label}'.")
                arenaService.updateJudgeProgress(node.label ?: "Emergent Concept", repairSteps, repairSteps, "READY")
                onComplete?.invoke(node)
            } else {
                log.error("Failed to repair judge JSON for '${node.label}' after LLM assistance.")
                arenaService.updateJudgeProgress(node.label ?: "Emergent Concept", repairSteps, repairSteps, "ERROR")
            }
        }
    }

    /**
     * Validates that the input string is a proper Judge JSON and saves it to the node.
     */
    private fun validateAndSaveJudge(node: GraphNode, input: String): Boolean {
        val parsed = JudgePrompts.parseJudgeJson(input) ?: return false
        node.judgePrompt = parsed.first
        node.judgeRubric = parsed.second
        return true
    }

    /**
     * Longest word n-gram shared between [text] and any string in [sources], as a token count.
     *
     * The induction prompt instructs the model not to restate question text or correct options,
     * but an instruction is not a check — nothing verified it, so nothing could be reported about
     * it. This turns the constraint into a measured property: a rubric that shares a long n-gram
     * with a correct option has memorised that option rather than abstracted a rule, which is a
     * leakage channel into the held-out split even though the questions themselves were withheld.
     *
     * Word-level rather than character-level, and case- and punctuation-insensitive, so
     * paraphrase-level reuse is not mistaken for verbatim copying and vice versa.
     */
    internal fun maxSharedNgram(text: String, sources: List<String>, cap: Int = 12): Pair<Int, String> {
        fun tokens(s: String) = s.lowercase()
            .replace(Regex("[^a-z0-9\\s]"), " ")
            .split(Regex("\\s+")).filter { it.isNotBlank() }

        val t = tokens(text)
        if (t.isEmpty()) return 0 to ""
        val srcGrams = HashMap<Int, MutableSet<String>>()
        for (s in sources) {
            val st = tokens(s)
            for (k in 1..minOf(cap, st.size)) {
                val set = srcGrams.getOrPut(k) { HashSet() }
                for (i in 0..st.size - k) set.add(st.subList(i, i + k).joinToString(" "))
            }
        }
        var best = 0
        var bestGram = ""
        for (k in minOf(cap, t.size) downTo 1) {
            val src = srcGrams[k] ?: continue
            for (i in 0..t.size - k) {
                val g = t.subList(i, i + k).joinToString(" ")
                if (g in src) {
                    best = k; bestGram = g
                    break
                }
            }
            if (best > 0) break
        }
        return best to bestGram
    }

    /**
     * Reports whether an induced rubric reuses wording from the correct options it was induced
     * from. Threshold 5 follows the usual verbatim-reuse convention; single words and short
     * technical phrases ("standard deviation") are expected and not leakage.
     */
    private fun auditRubricLeakage(node: GraphNode, sourceCorrectOptions: List<String>) {
        val rubric = node.judgeRubric ?: return
        if (sourceCorrectOptions.isEmpty()) return
        val (n, gram) = maxSharedNgram(rubric, sourceCorrectOptions)

        // A long shared span is only evidence of MEMORISATION if it is specific to one answer.
        // A span occurring across many correct options is domain vocabulary, and penalising it
        // penalises exactly the domains whose terminology is multi-word.
        //
        // This fired on 'Dormant Commerce Clause and State Protectionism' for the 5-token span
        // "the privileges and immunities clause" — a named clause of the US Constitution, not a
        // leaked answer. Of 86 clean nodes the next-highest spans were 4 tokens, and every one of
        // those was law or economics ("Real Property Rights", "Criminal Liability and Mens Rea",
        // "Market Equilibrium and Elasticity"). The smoke test could not have caught it: History
        // and Computer science topped out at 2 tokens because they have no multi-word doctrine
        // names. Raising the threshold to 6 would only move the failure to a longer doctrine.
        val norm = { s: String -> s.lowercase().replace(Regex("[^a-z0-9\\s]"), " ")
            .split(Regex("\\s+")).filter { it.isNotBlank() }.joinToString(" ") }
        val occurrences = if (gram.isBlank()) 0 else sourceCorrectOptions.count { norm(it).contains(gram) }

        if (n >= 5 && occurrences > 1) {
            log.info(
                "[JUDGE-LEAK] node '${node.label}': $n-token span \"$gram\" appears in" +
                    " $occurrences of ${sourceCorrectOptions.size} source options — domain" +
                    " vocabulary rather than a memorised answer; not treated as leakage."
            )
        } else if (n >= 5) {
            // A GATE, not a warning, and deliberately at save time rather than at judgment.
            //
            // The alternative — asserting the answer text is absent from the assembled judge
            // prompt — requires threading the correct-option string into the judging path purely
            // so a check can confirm it is not there, which adds the exact surface it polices and
            // leaves a refactor free to drop the assertion while keeping the string in scope.
            // Rubrics are static per snapshot and the answer texts are already in scope here, so a
            // rubric that is clean when saved is clean at every subsequent use. Gating here makes
            // the runtime assertion unnecessary.
            //
            // Failing loudly is the right severity: a rubric that reproduces an answer invalidates
            // every verdict in its leaf, and a run that stops is recoverable where a leaderboard
            // built on a leaked rubric is not. If this proves too brittle, the graded response is
            // to drop the offending rules and re-synthesise, not to downgrade it to a warning.
            throw IllegalStateException(
                "Rubric leakage gate failed for node '${node.label}' (id=${node.id}): the induced" +
                    " rubric shares a $n-token span with a source correct option — \"$gram\"." +
                    " The rule has memorised an answer rather than abstracted a reasoning property," +
                    " so it would carry answer information into the held-out split. Refusing to save."
            )
        } else {
            log.info(
                "[JUDGE-LEAK] node '${node.label}': rubric leakage audit clean" +
                    " (max shared span $n token(s) vs ${sourceCorrectOptions.size} source options," +
                    " threshold 5)"
            )
        }
    }

    fun listJudges(root: GraphNode): List<JudgeMetadata> {
        val judges = mutableListOf<JudgeMetadata>()
        fun walk(node: GraphNode, visited: MutableSet<String>) {
            if (!visited.add(node.id)) return
            if (node.judgePrompt != null) {
                judges.add(JudgeMetadata(node.id, node.label ?: node.id.toString(), node.depth, node.judgeRubric != null, node.judgePrompt?.take(150) + "..."))
            }
            node.children.forEach { walk(it, visited) }
        }
        walk(root, mutableSetOf())
        return judges.sortedBy { it.depth }
    }
}

@kotlinx.serialization.Serializable
data class JudgeMetadata(val nodeId: String, val label: String, val depth: Int, val hasRubric: Boolean, val promptPreview: String)
