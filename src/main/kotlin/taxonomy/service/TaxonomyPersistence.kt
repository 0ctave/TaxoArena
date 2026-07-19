package taxonomy.service

import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Component
import taxonomy.config.TaxonomyConfig
import taxonomy.dataset.EmbeddingCache
import taxonomy.model.Embedding
import taxonomy.model.GraphNode
import java.io.File
import java.security.MessageDigest

@Serializable
data class SerialNode(
    val id: String,
    val label: String?,
    val depth: Int,
    val childIds: List<String>,
    val crossLinkChildIds: List<String> = emptyList(),
    val parentIds: List<String>,
    val vmfMu: FloatArray? = null,
    val vmfKappa: Double = 0.0,
    val vmfLogNormalizer: Double = 0.0,
    val niwM0: FloatArray? = null,
    val niwKappa0: Double = 0.0,
    val niwNu0: Double = 0.0,
    val niwLambda: FloatArray? = null,
    val dasguptaDeltaNorm: Double = 0.0,
    val phaseCompleted: Int = 0,
    val treeParentId: String? = null,
    val judgePrompt: String? = null,
    val judgeRubric: String? = null,
    val queryIds: List<String> = emptyList(),
    val proportionalWeight: Double = 1.0,
    val judgeCorpusFingerprint: String? = null,
    val judgeModelVersion: String? = null,
    val isBridge: Boolean = false,
    val bridgeJsDivergence: Double = 0.0,
    val residualQueries: List<String> = emptyList()
)

@Serializable
data class SerializedGraph(
    val rootId: String,
    val nodes: List<SerialNode>,
    val distillationEnabled: Boolean = false,
    val version: Int = 2
)

@Component
class TaxonomyPersistence(
    private val config: TaxonomyConfig,
    private val embeddingCache: EmbeddingCache
) {
    private val log = LoggerFactory.getLogger("taxonomy.Persistence")
    private val json = Json { 
        prettyPrint = false 
        ignoreUnknownKeys = true
        encodeDefaults = false 
    }

    private fun hashQuery(text: String): String {
        val bytes = MessageDigest.getInstance("SHA-256").digest(text.toByteArray())
        return bytes.joinToString("") { "%02x".format(it) }.take(16)
    }

    fun save(root: GraphNode, path: String): SerializedGraph {
        log.info("Saving taxonomy DAG with Vector-Offloading to $path...")
        
        val allNodes = mutableSetOf<GraphNode>()
        fun walk(n: GraphNode) {
            if (allNodes.add(n)) {
                n.children.forEach { walk(it) }
                n.crossLinkChildren.forEach { walk(it) }
            }
        }
        walk(root)

        // 1. Offload Queries to SQL
        val globalQueries = allNodes.flatMap { it.queries }.distinctBy { it.rawText }
        globalQueries.forEach { q ->
            val qId = "q_${hashQuery(q.rawText)}"
            embeddingCache.putQuery(qId, q.rawText, q.distilledText, q.groundTruthCategory)
        }

        // 2. Map nodes to SerialNodes
        val serialNodes = allNodes.map { node ->
            SerialNode(
                id = node.id,
                label = node.label,
                depth = node.depth,
                childIds = node.children.map { it.id },
                crossLinkChildIds = node.crossLinkChildren.map { it.id },
                parentIds = node.parents.map { it.id },
                vmfMu = if (node.vmfMu.isNotEmpty()) node.vmfMu else null,
                vmfKappa = node.vmfKappa,
                vmfLogNormalizer = node.vmfLogNormalizer,
                niwM0 = if (node.niwM0.isNotEmpty()) node.niwM0 else null,
                niwKappa0 = node.niwKappa0,
                niwNu0 = node.niwNu0,
                niwLambda = if (node.niwLambda.isNotEmpty()) node.niwLambda else null,
                dasguptaDeltaNorm = node.dasguptaDeltaNorm,
                phaseCompleted = node.phaseCompleted,
                treeParentId = node.treeParentId,
                judgePrompt = node.judgePrompt,
                judgeRubric = node.judgeRubric,
                queryIds = node.queries.map { "q_${hashQuery(it.rawText)}" },
                proportionalWeight = node.proportionalWeight,
                judgeCorpusFingerprint = node.judgeCorpusFingerprint,
                judgeModelVersion = node.judgeModelVersion,
                isBridge = node.isBridge,
                bridgeJsDivergence = node.bridgeJsDivergence,
                residualQueries = node.residualQueries.toList()
            )
        }

        val serialized = SerializedGraph(
            rootId = root.id, 
            nodes = serialNodes,
            distillationEnabled = false
        )
        
        File(path).writeText(json.encodeToString(serialized))
        log.info("Saved ${allNodes.size} nodes successfully (offloaded structure to SQL).")

        return serialized
    }

    fun load(path: String): GraphNode? {
        val file = File(path)
        if (!file.exists()) return null

        log.info("Loading Vector-Offloaded taxonomy from $path...")
        val serialized = json.decodeFromString<SerializedGraph>(file.readText())
        log.info("Loaded serialized graph version: ${serialized.version}")

        val allQueryIds = serialized.nodes.flatMap { it.queryIds }.toSet()
        val queryRowMap: Map<String, Triple<String, String, String>> = embeddingCache.getQueriesBatch(allQueryIds)
        val allDistilled = queryRowMap.values.map { it.second }.toSet()
        val vectorMap = embeddingCache.getBatch(allDistilled)

        val nodeMap = serialized.nodes.associate { sNode ->
            sNode.id to GraphNode(
                id = sNode.id,
                label = sNode.label,
                depth = sNode.depth
            ).apply {
                proportionalWeight = sNode.proportionalWeight
                isBridge = sNode.isBridge
                bridgeJsDivergence = sNode.bridgeJsDivergence
                residualQueries.addAll(sNode.residualQueries)
                judgePrompt = sNode.judgePrompt
                judgeRubric = sNode.judgeRubric

                treeParentId = sNode.treeParentId
                judgeCorpusFingerprint = sNode.judgeCorpusFingerprint
                judgeModelVersion = sNode.judgeModelVersion

                vmfMu = sNode.vmfMu ?: FloatArray(0)
                vmfKappa = sNode.vmfKappa
                vmfLogNormalizer = sNode.vmfLogNormalizer
                niwM0 = sNode.niwM0 ?: FloatArray(0)
                niwKappa0 = sNode.niwKappa0
                niwNu0 = sNode.niwNu0
                niwLambda = sNode.niwLambda ?: FloatArray(0)
                dasguptaDeltaNorm = sNode.dasguptaDeltaNorm
                phaseCompleted = sNode.phaseCompleted

                sNode.queryIds.forEach { qId ->
                    val (raw, distilled, gtCat) = queryRowMap[qId] ?: return@forEach
                    val vector = vectorMap[distilled] ?: return@forEach
                    val resolvedId = taxonomy.model.QuestionIdRegistry.lookup(raw) ?: qId.toIntOrNull() ?: -1
                    val emb = Embedding(raw, distilled, vector, gtCat)
                    emb.queryId = resolvedId
                    queries.add(emb)
                }
            }
        }

        serialized.nodes.forEach { sNode ->
            val node = nodeMap[sNode.id]!!
            sNode.childIds.forEach { cId -> nodeMap[cId]?.let { node.children.add(it) } }
            sNode.crossLinkChildIds.forEach { cId -> nodeMap[cId]?.let { node.crossLinkChildren.add(it) } }
            sNode.parentIds.forEach { pId -> nodeMap[pId]?.let { node.parents.add(it) } }
        }

        log.info("[DB] Successfully loaded and hydrated DAG with ${nodeMap.size} nodes.")
        return nodeMap[serialized.rootId]
    }
}
