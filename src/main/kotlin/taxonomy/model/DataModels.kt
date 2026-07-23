package taxonomy.model

import kotlinx.serialization.Serializable

object TextNormalizer {
    fun cleanText(s: String): String {
        return s.replace("\r\n", "\n").replace("\r", "\n").trim()
    }
}

object QuestionIdRegistry {
    private val textToId = java.util.concurrent.ConcurrentHashMap<String, Int>()

    fun register(text: String, id: Int) {
        textToId[text] = id
        textToId[TextNormalizer.cleanText(text)] = id
    }

    fun lookup(text: String): Int? {
        return textToId[text] ?: textToId[TextNormalizer.cleanText(text)]
    }

    fun clear() {
        textToId.clear()
    }
}

/**
 * Represents a high-dimensional vector x ∈ ℝᵈ along with its source text.
 * Stores both the original raw query and its distilled semantic signature.
 *
 * groundTruthCategory carries the MMLU-Pro category string (e.g. "chemistry")
 * stamped at query-creation time in TaxonomyEngine. This survives LLM relabeling
 * and is the single source of truth for GT-dependent metrics (H-F₁, NMI, ECE).
 * Default is "" so that existing serialized caches deserialize cleanly.
 */
@Serializable
data class Embedding(
    val rawText: String,
    val distilledText: String,
    val values: FloatArray,
    val groundTruthCategory: String = "",
    var queryId: Int = -1
) {

    val dimensions: Int get() = values.size

    // Convert to DoubleArray for high-precision statistical calculations (Mahalanobis/KL)
    fun toDoubleArray(): DoubleArray = DoubleArray(values.size) { values[it].toDouble() }

    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is Embedding) return false
        return rawText == other.rawText
    }

    override fun hashCode(): Int {
        return rawText.hashCode()
    }
}

/**
 * Parameters for a single component in a Gaussian Mixture Model.
 * High-dimensional vectors are stored in SQL and referenced by vectorId.
 */
@Serializable
data class GmmComponent(
    val mean: DoubleArray? = null,
    val diagonalCovariance: DoubleArray? = null,
    val weight: Double,
    val sampleCount: Int,
    val vectorId: String? = null
)

/**
 * Represents a Gaussian Mixture Model (GMM) distribution for a node.
 */
@Serializable
data class GmmParams(
    val components: List<GmmComponent>,
    var empiricalThreshold: Double = Double.MAX_VALUE
) {
    val totalSamples: Int get() = components.sumOf { it.sampleCount }
}

/**
 * Canonical, framework-wide metrics payload for the Taxonomy DAG at a single
 * point in time.
 *
 * This is the SINGLE SOURCE OF TRUTH for computed DAG metrics. It is computed
 * once by [taxonomy.utils.TaxonomyMetrics.generateReport] and then carried,
 * unchanged, into:
 *   - the per-iteration history ([IterationMetrics] = label + this payload),
 *   - DAG snapshot persistence ([taxonomy.service.SnapshotMetrics] wraps this),
 *   - the TUI metrics view.
 *
 * All defaults are tolerant so older serialized snapshots (which may omit
 * fields) still deserialize cleanly.
 */
@Serializable
data class TaxonomyMetricsData(
    val totalNodes: Int = 0,
    val leafNodes: Int = 0,
    val crossDomainNodes: Int = 0,
    val maxDepth: Int = 0,
    val avgLeafDepth: Double = 0.0,
    val medianLeafAssignments: Double = 1.0,
    val totalUniqueQueries: Int = 0,
    val residualQueries: Int = 0,
    val residualRatio: Double = 0.0,
    val maxLeafConcentration: Double = 0.0,
    val contaminationRatio: Double = 0.0,
    val equilibriumIndex: Double = 0.0,
    // vMF / NiW evaluation metrics
    val nmi: Double = 0.0,
    val ari: Double = 0.0,
    val dendrogramPurity: Double = 0.0,
    val weightedLeafPurity: Double = 0.0,
    val edgeF1: Double = 0.0,
    val sphericalSilhouette: Double = 0.0,
    val ancestorCorrectRate: Double = 0.0,
    // Hierarchical F₁ (Kosmopoulos et al. 2014) — ancestor-aware routing quality.
    val hPrecision: Double = 0.0,
    val hRecall: Double = 0.0,
    val hF1: Double = 0.0,
    val avgMatchCount: Double = 1.0,
    /** Average vMF concentration (κ) per depth level. */
    val kappaByDepth: Map<Int, Double> = emptyMap(),
    val leafDistribEntropy: Double = 0.0,
    // Publication-grade metrics (PR #49)
    val totalDasguptaCost: Double = 0.0,
    val routingECE: Double = 0.0,
    val tripletAccuracy: Double = 0.0,
    val normalisedSackin: Double = 0.0,
)

/**
 * A labelled metrics point in the per-iteration history.
 *
 * Composes the canonical [TaxonomyMetricsData] rather than duplicating its
 * fields, so there is exactly one definition of every metric. Property
 * accessors delegate to [metrics] for backward compatibility with call-sites
 * that read `iterationMetrics.totalNodes` etc. directly.
 */
@Serializable
data class IterationMetrics(
    val iteration: String,
    val metrics: TaxonomyMetricsData = TaxonomyMetricsData(),
) {
    val totalNodes: Int                 get() = metrics.totalNodes
    val leafNodes: Int                  get() = metrics.leafNodes
    val crossDomainNodes: Int           get() = metrics.crossDomainNodes
    val maxDepth: Int                   get() = metrics.maxDepth
    val avgLeafDepth: Double            get() = metrics.avgLeafDepth
    val medianLeafAssignments: Double   get() = metrics.medianLeafAssignments
    val totalUniqueQueries: Int         get() = metrics.totalUniqueQueries
    val residualQueries: Int            get() = metrics.residualQueries
    val residualRatio: Double           get() = metrics.residualRatio
    val maxLeafConcentration: Double    get() = metrics.maxLeafConcentration
    val contaminationRatio: Double      get() = metrics.contaminationRatio
    val equilibriumIndex: Double        get() = metrics.equilibriumIndex
    val nmi: Double                     get() = metrics.nmi
    val ari: Double                     get() = metrics.ari
    val dendrogramPurity: Double        get() = metrics.dendrogramPurity
    val weightedLeafPurity: Double      get() = metrics.weightedLeafPurity
    val edgeF1: Double                  get() = metrics.edgeF1
    val sphericalSilhouette: Double     get() = metrics.sphericalSilhouette
    val ancestorCorrectRate: Double     get() = metrics.ancestorCorrectRate
    val hPrecision: Double              get() = metrics.hPrecision
    val hRecall: Double                 get() = metrics.hRecall
    val hF1: Double                     get() = metrics.hF1
    val avgMatchCount: Double           get() = metrics.avgMatchCount
    val kappaByDepth: Map<Int, Double>  get() = metrics.kappaByDepth
    val leafDistribEntropy: Double      get() = metrics.leafDistribEntropy
    val totalDasguptaCost: Double       get() = metrics.totalDasguptaCost
    val routingECE: Double              get() = metrics.routingECE
    val tripletAccuracy: Double         get() = metrics.tripletAccuracy
    val normalisedSackin: Double        get() = metrics.normalisedSackin
}

fun Embedding.projectTo(targetDim: Int): DoubleArray {
    val sliced = values.copyOf(targetDim).map { it.toDouble() }.toDoubleArray()
    val norm   = kotlin.math.sqrt(sliced.sumOf { it * it })
    return if (norm > 0.0) DoubleArray(targetDim) { sliced[it] / norm } else sliced
}

/**
 * Stores details about the active taxonomy generation progress.
 */
@Serializable
data class GenerationProgress(
    val currentIteration: Int,
    val totalIterations: Int,
    val currentStep: String,
    val stepIndex: Int,
    val totalSteps: Int,
    val percentComplete: Double,
    val statusText: String
)

object ExperimentOutputContext {
    @Volatile
    var activeBaseDir: java.io.File? = null
}

enum class TraversalPolicy {
    TREE_ONLY,
    BRIDGE_ONLY,
    DAG_BOTH
}
