package taxonomy.operations

import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import taxonomy.model.GraphNode
import java.io.File

@Serializable
data class VisualNode(
    val id: String,
    val label: String,
    val depth: Int,
    val isLeaf: Boolean,
    val parentIds: List<String>,
    val childIds: List<String>,
    val gmmComponents: List<VisualGmmComponent> = emptyList()
)

@Serializable
data class VisualGmmComponent(
    val mean: FloatArray,
    val diagonalCovariance: FloatArray,
    val weight: Double,
    val sampleCount: Int
)

@Serializable
data class VisualQuery(
    val text: String,
    val distilled: String,
    val vector: FloatArray,
    val assignedNodeId: String,
    val assignedNodeLabel: String,
    val originalCategories: String? = null // Join multiple categories for visualization
)

@Serializable
data class TaxonomyExport(
    val nodes: List<VisualNode>,
    val queries: List<VisualQuery>
)

@Service
class TaxonomyVisualizer {
    private val log = LoggerFactory.getLogger("taxonomy.Visualizer")
    
    // CRITICAL: Disable prettyPrint for massive numeric exports to prevent hanging
    private val json = Json { 
        prettyPrint = false 
        encodeDefaults = true 
    }

    fun exportForVisualization(root: GraphNode, groundTruthMap: Map<String, List<String>> = emptyMap(), fileName: String = "taxonomy_visualization.json") {
        log.info("Exporting taxonomy for UMAP visualization to $fileName (Fast-Export Mode)...")
        
        val nodes = mutableListOf<VisualNode>()
        val queries = mutableListOf<VisualQuery>()
        val visited = mutableSetOf<String>()
        
        // Cache for truncated vectors to avoid redundant math/allocation
        val truncatedVectorCache = mutableMapOf<String, FloatArray>()

        fun walk(node: GraphNode) {
            if (visited.contains(node.id)) return
            visited.add(node.id)

            val gmmComps = if (node.vmfMu.isNotEmpty()) {
                val truncatedMean = FloatArray(minOf(node.vmfMu.size, 1024)) { node.vmfMu[it] }
                val truncatedVar = if (node.niwLambda.isNotEmpty()) {
                    FloatArray(minOf(node.niwLambda.size, 1024)) { node.niwLambda[it] }
                } else {
                    FloatArray(truncatedMean.size) { 1.0f }
                }
                listOf(VisualGmmComponent(
                    mean = truncatedMean,
                    diagonalCovariance = truncatedVar,
                    weight = 1.0,
                    sampleCount = node.queries.size
                ))
            } else emptyList()

            nodes.add(VisualNode(
                id = node.id,
                label = node.label ?: node.id,
                depth = node.depth,
                isLeaf = node.isLeaf,
                parentIds = node.parents.map { it.id },
                childIds = node.children.map { it.id },
                gmmComponents = gmmComps
            ))

            node.queries.forEach { emb ->
                // Use cache for the heavy vector truncation
                val truncatedVector = truncatedVectorCache.getOrPut(emb.distilledText) {
                    if (emb.values.size > 1024) emb.values.copyOfRange(0, 1024) else emb.values
                }
                
                val originals = groundTruthMap[emb.rawText]?.joinToString(", ")
                
                queries.add(VisualQuery(
                    text = emb.rawText,
                    distilled = emb.distilledText,
                    vector = truncatedVector,
                    assignedNodeId = node.id,
                    assignedNodeLabel = node.label ?: node.id,
                    originalCategories = originals
                ))
            }

            node.children.forEach { walk(it) }
        }

        walk(root)

        val export = TaxonomyExport(nodes, queries)
        
        // Use a BufferedWriter for faster I/O on large strings
        val file = File(fileName)
        file.bufferedWriter().use { writer ->
            writer.write(json.encodeToString(export))
        }
        
        log.info("Export complete. ${nodes.size} nodes and ${queries.size} queries written to $fileName.")
    }
}
