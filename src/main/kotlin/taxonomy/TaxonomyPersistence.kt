package org.eclipse.lmos.arc.app.taxonomy

import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Component
import java.io.File
import java.security.MessageDigest

@Serializable
data class SerialNode(
    val id: String,
    val label: String,
    val depth: Int,
    val childIds: List<String>,
    val parentIds: List<String>,
    val distribution: GmmParams?,
    val judgePrompt: String? = null,
    val judgeRubric: String? = null,
    val queryIds: List<String> = emptyList()
)

@Serializable
data class SerializedGraph(
    val rootId: String,
    val nodes: List<SerialNode>,
    val distillationEnabled: Boolean = false
)

@Component
class TaxonomyPersistence(
    private val config: TaxonomyConfig,
    private val embeddingCache: EmbeddingCache
) {
    private val log = LoggerFactory.getLogger(TaxonomyPersistence::class.java)
    private val json = Json { 
        prettyPrint = false 
        ignoreUnknownKeys = true
        encodeDefaults = false 
    }

    private fun hashQuery(text: String): String {
        val bytes = MessageDigest.getInstance("SHA-256").digest(text.toByteArray())
        return bytes.joinToString("") { "%02x".format(it) }.take(16)
    }

    fun save(root: GraphNode, path: String) {
        log.info("Saving taxonomy DAG with Vector-Offloading to $path...")
        
        val allNodes = mutableSetOf<GraphNode>()
        fun walk(n: GraphNode) {
            if (allNodes.add(n)) n.children.forEach { walk(it) }
        }
        walk(root)

        // 1. Offload Queries to SQL
        val globalQueries = allNodes.flatMap { it.queries }.distinctBy { it.rawText }
        globalQueries.forEach { q ->
            val qId = "q_${hashQuery(q.rawText)}"
            embeddingCache.putQuery(qId, q.rawText, q.distilledText)
        }

        // 2. Map nodes to SerialNodes
        val serialNodes = allNodes.map { node ->
            val serialGmm = node.distribution?.let { gmm ->
                val offloadedComponents = gmm.components.mapIndexed { index, comp ->
                    if (comp.mean != null && comp.diagonalCovariance != null) {
                        val vectorId = "gmm_${node.id}_$index"
                        embeddingCache.putGmmVectors(vectorId, comp.mean, comp.diagonalCovariance)
                        comp.copy(mean = null, diagonalCovariance = null, vectorId = vectorId)
                    } else comp
                }
                gmm.copy(components = offloadedComponents)
            }

            SerialNode(
                id = node.id,
                label = node.label,
                depth = node.depth,
                childIds = node.children.map { it.id },
                parentIds = node.parents.map { it.id },
                distribution = serialGmm,
                judgePrompt = node.judgePrompt,
                judgeRubric = node.judgeRubric,
                queryIds = node.queries.map { "q_${hashQuery(it.rawText)}" }
            )
        }

        val serialized = SerializedGraph(
            rootId = root.id, 
            nodes = serialNodes,
            distillationEnabled = config.execution.enableDistillation
        )
        
        File(path).writeText(json.encodeToString(serialized))
        log.info("Saved ${allNodes.size} nodes successfully (offloaded structure to SQL).")
    }

    fun load(path: String): GraphNode? {
        val file = File(path)
        if (!file.exists()) return null

        log.info("Loading Vector-Offloaded taxonomy from $path...")
        val serialized = json.decodeFromString<SerializedGraph>(file.readText())
        
        val queryCache = mutableMapOf<String, Embedding?>()

        val nodeMap = serialized.nodes.associate { sNode ->
            sNode.id to GraphNode(
                id = sNode.id,
                label = sNode.label,
                depth = sNode.depth
            ).apply {
                judgePrompt = sNode.judgePrompt
                judgeRubric = sNode.judgeRubric
                
                distribution = sNode.distribution?.let { gmm ->
                    val hydratedComponents = gmm.components.map { comp ->
                        if (comp.vectorId != null) {
                            val vectors = embeddingCache.getGmmVectors(comp.vectorId)
                            comp.copy(mean = vectors?.first, diagonalCovariance = vectors?.second)
                        } else comp
                    }
                    gmm.copy(components = hydratedComponents)
                }

                sNode.queryIds.forEach { qId ->
                    val emb = queryCache.getOrPut(qId) {
                        embeddingCache.getQuery(qId)?.let { (raw, distilled) ->
                            val vector = embeddingCache.get(distilled)
                            if (vector != null) Embedding(raw, distilled, vector) else null
                        }
                    }
                    emb?.let { queries.add(it) }
                }
            }
        }

        serialized.nodes.forEach { sNode ->
            val node = nodeMap[sNode.id]!!
            sNode.childIds.forEach { cId -> nodeMap[cId]?.let { node.children.add(it) } }
            sNode.parentIds.forEach { pId -> nodeMap[pId]?.let { node.parents.add(it) } }
        }

        log.info("[DB] Successfully loaded and hydrated DAG with ${nodeMap.size} nodes.")
        return nodeMap[serialized.rootId]
    }
}
