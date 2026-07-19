package taxonomy.tui

/**
 * Precision/recall/F1 for a single ground-truth domain, computed over the top-1
 * leaf-domain prediction across the sampled reserved test queries.
 */
data class DomainF1(
    val support: Int = 0,
    val precision: Double = 0.0,
    val recall: Double = 0.0,
    val f1: Double = 0.0,
)

/**
 * Aggregate results of running a batch of trickle-routing tests against the
 * active taxonomy DAG. Held in [taxonomy.tui.state.TrickleUiState] and rendered
 * by the benchmark feature panel.
 *
 * Metrics are computed by tagging each DAG leaf with the dominant MMLU-Pro domain
 * of its training queries, then routing the held-out reserved queries and scoring
 * the matched leaves' dominant domains against the query's true domain. All fields
 * default to zero/empty so an aborted run can still produce a value.
 */
data class BatchTrickleTestResults(
    val totalQueries: Int = 0,
    /** Top-1 leaf-domain accuracy: dominant domain of the highest-confidence matched leaf == truth. */
    val top1Accuracy: Double = 0.0,
    val top1WilsonLow: Double = 0.0,
    val top1WilsonHigh: Double = 0.0,
    /** Any-match accuracy: any matched leaf's dominant domain == truth. */
    val anyMatchAccuracy: Double = 0.0,
    /** Mean purity (topCount / leafSize) of the top-1 matched leaf — cluster-coherence signal. */
    val meanLeafPurity: Double = 0.0,
    /** Macro-averaged F1 over domains, on the top-1 leaf-domain prediction. */
    val macroF1: Double = 0.0,
    /** Mean tree depth of the top-1 matched leaf. */
    val meanRoutingDepth: Double = 0.0,
    /** Fraction of test queries that routed to no leaf at all. */
    val noMatchRate: Double = 0.0,
    /** Per-domain precision/recall/F1, keyed by domain. */
    val perDomainF1: Map<String, DomainF1> = emptyMap(),
    /** Expected Calibration Error of the routing confidence. */
    val ece: Double = 0.0,
    val avgMatchCountEval: Double = 1.0,
    val medianNodesPerQueryEval: Double = 1.0,
)
