package taxonomy.config

import org.springframework.boot.context.properties.ConfigurationProperties
import org.springframework.context.annotation.Configuration
import taxonomy.model.Embedding
import taxonomy.model.GraphNode
import java.io.Serializable
import kotlinx.serialization.Serializable as KotlinxSerializable

@KotlinxSerializable
enum class DagMode { TREE_BASELINE, DAG_MAX }

/**
 * Defines the thermodynamic constraints and dynamic parameters of the domain inference space.
 * Updated to align with the Thermodynamic Formalism using vMF-k-means and NiW posteriors.
 */
@Configuration
@ConfigurationProperties(prefix = "taxoadapt")
class TaxonomyConfig {
    var execution: ExecutionConfig = ExecutionConfig()
    var dataset: DatasetConfig = DatasetConfig()
    var llm: LlmConfig = LlmConfig()
    var formalism: FormalismConfig = FormalismConfig()

    class ExecutionConfig {
        var startService: Boolean = false
        var numIterations: Int = 15
        var enableEarlyStopping: Boolean = true
        var enableVisualization: Boolean = true
        var enableTui: Boolean = true
        var enableLabeling: Boolean = false
        var enableIterationMetrics: Boolean = false
        var enableFinalMetrics: Boolean = true

        /**
         * Kill-switch for the pre-flight TTY probe done before the TUI enters the alt-screen.
         * The probe reflectively calls Mosaic's internal `Tty.tryBind()` to fail fast (and loudly)
         * when there is no controlling terminal. Set true to skip it entirely if the probe itself
         * ever misbehaves (e.g. the internal API changes); the TUI then starts optimistically.
         */
        var skipTtyPrecheck: Boolean = false
        var llmParallelism: Int = 8
    }

    class DatasetConfig {
        var datasetType: DatasetType = DatasetType.AG_NEWS
        var splitDataset: Boolean = true
        var testSplitRatio: Double = 0.2
        var selectedDomains: List<String> = emptyList()

        // Directory holding TIGER-AI-Lab MMLU-Pro eval_results files
        // (`model_outputs_<MODEL>_<N>shots.zip` / `.json`) for precomputed-answer mode.
        var evalResultsDir: String = "eval_results"
    }

    class LlmConfig {
        var provider: LlmProviderType = LlmProviderType.OLLAMA
        var embeddingProvider: LlmProviderType = LlmProviderType.OLLAMA
        var judgeModel: String = "ministral-3:14b"
        var labelingModel: String = "ministral-3:14b"
        var embeddingModel: String = "qwen3-embedding"
        var maxJudgeGenerality: Int = 1 // 0 = only leaves, 1 = leaves + parents, etc.
        var judgeDomains: List<String> = emptyList()
        var azure: AzureConfig = AzureConfig()
    }


    class AzureConfig {
        var endpoint: String = ""
        var apiKey: String = ""
        var deploymentName: String = ""
        var embeddingDeploymentName: String = ""
        var apiVersion: String = "2024-02-15-preview"
    }


    class FormalismConfig {
        // ── Tree structure ────────────────────────────────────────────────────
        var maxDepth: Int = 12

        // ── Splitting ─────────────────────────────────────────────────────────
        // Minimum queries a node must hold before it is eligible for splitting.
        var minClusterSize: Int = 25

        // Lexicographic convergence tolerance. E.g. 1e-6.
        var tau: Double = 1e-6

        /**
         * Acceptance threshold in units of the paired bootstrap standard error of dJ.
         *
         * 0.0 keeps the historical rule: accept iff dJ > [tau], with a node-count tie-break
         * inside the band. tau is a float tolerance, so that rule accepts edits whose measured
         * improvement is far below the resolution of the measurement — the most marginal
         * accepted edit observed carried dJ = 5.5e-6 against SE(dJ) = 9.5e-5, i.e. z = 0.06.
         *
         * Set > 0 to gate on z = dJ / SE(dJ) instead. SE(dJ) spans an order of magnitude
         * between proposals because it scales with the affected node's population, so no
         * fixed tolerance can track it.
         *
         * The termination argument survives, and tightens. SE >= 0, so any edit accepted with
         * SE > 0 has dJ > z*SE >= 0 and J strictly increases; the SE == 0 clause admits only
         * edits that leave J exactly unchanged while strictly reducing |V|. The lexicographic
         * (J, -|V|) argument goes through with a strictly smaller acceptance region.
         */
        var acceptanceZ: Double = 0.0

        /**
         * Gate the parameter refit on J, like every structural edit. OFF by default: it is an
         * ablation, not the canonical path.
         *
         * Measured on seed 42: the gated variant terminates provably and certifies a fixed
         * point, but reaches J 0.24303 against 0.24714, 92 leaves against 104, and held-out
         * Top-1 73.33% against 74.19%.
         *
         * The cost is attributable to the gate's GRANULARITY, not to monotonicity as such. The
         * refit is gated whole-tree, so one node whose update transiently lowers J freezes the
         * parameters of every node. In that run it fired from iteration 3 onward while
         * structural edits were still landing, so later splits were proposed against stale
         * parent geometry, and the identical recurring rejection (-6.106e-04 every iteration)
         * is the signature of frozen theta with a settled structure. Whether a per-node or
         * per-subtree refit gate preserves monotonicity without this cost is untested.
         */
        var enableRefitGate: Boolean = false

        // Dasgupta separation threshold: a split is accepted when its delta
        // exceeds this value, guaranteeing the two children are geometrically
        // separated in vMF space.
        var proposalSeparationBar: Double = 0.04

        // ── Routing ───────────────────────────────────────────────────────────
        // Final membership share: after the trickle walk, a query's memberships are
        // normalized over the leaves it actually reached, and a leaf counts as a genuine
        // destination iff it holds at least this fraction of THAT query's own membership.
        // Self-normalized, so its meaning is invariant to tree depth and fan-out — unlike
        // the previous absolute product-vs-floor test, which made balanced structure
        // unreachable below depth 2 and forced dominant-child (wrapper) chains.
        var membershipFloor: Double = 0.10

        // Per-level relative beam: a child stays on the beam iff its responsibility is at
        // least this fraction of the BEST sibling's. Relative-to-best is scale-free and
        // concentration-adaptive: 0.50/0.50 sharing survives (both within gamma of best)
        // while 0.90/0.05 drops the tail — an absolute floor cannot distinguish the two.
        // Descent-vs-residual needs no parameter at all: the walk descends only where some
        // child explains the query at least as well as the parent's own vMF component does
        // (a parent-vs-children Bayes factor at threshold 1).
        var routingBeamGamma: Double = 0.15

        // Descent-gate slack (the residual-loosening knob). The parameter-free gate
        // residualizes a query at node p iff max_c <mu_c,x> < r_bar_p * <mu_p,x>
        // (Jensen-tight bound). With margin d the bar becomes (r_bar_p - d) * <mu_p,x>:
        // 0.0 keeps the exact tight bound; each increment admits queries whose best
        // child is slightly worse than the children's weighted-mean alignment, pushing
        // domain-central generalists into their nearest child instead of the residual
        // pool. Trade-off: fewer measured residuals vs. slightly diluted leaf purity.
        var descentMargin: Double = 0.0

        // Judge-call-cost bound for arena-time evaluation only (how many leaves a single held-out
        // query may be scored against) — an engineering constraint, not a geometric-correctness
        // knob. Construction-time membership is unbounded, driven purely by membershipFloor.
        var maxLeafAssignments: Int = 5


        // ── Mode Switch ──────────────────────────────────────────────────────
        /**
         * k-selection increment for performVmfKMeans: "how much must cluster k+1 ADD?".
         * A DIFFERENCE of separations, whereas proposalSeparationBar is a LEVEL ("is
         * every pair distinct?"). One constant served both for the whole history of the
         * project; this decouples them.
         *
         * NEGATIVE means "fall back to proposalSeparationBar", so every existing config
         * keeps its exact behaviour and this is inert until set.
         */
        var marginalEps: Double = -1.0

        /**
         * Upper bound on k for the EM mixture search. Historically hardcoded to 4.
         * With marginalEps > 0 the increment test bound k below this and the cap was
         * slack; with marginalEps = 0 nothing stops k except the coarsening loop, the
         * min-pair gate and this constant — so it can become the binding selector,
         * which would replace a documented threshold with an undocumented one.
         */
        var maxK: Int = 4

        /**
         * Ground-truth categories excluded from BOOTSTRAP ANCHORING only.
         *
         * Their queries still enter the corpus and the ground-truth map — they are
         * simply denied a depth-1 anchor, so they must route from the root like any
         * unexplained query. This is the entry path the incremental claim needs: a
         * domain that ARRIVES rather than one that is seeded.
         *
         * Without it the only expressible hold-out is relabel-to-an-existing-category,
         * which seeds the withheld queries INSIDE a host anchor and therefore tests
         * whether construction can evict a foreign body — the contamination story, not
         * the discovery story. That question already has an answer (the Computer
         * science split, q = 0.007 against its own within-node null); this one has
         * none.
         *
         * Empty in every reported configuration. It changes the bootstrap for the
         * REMAINING domains too — different corpus, different initial partition — so a
         * hold-out run is its own construction with its own baseline and its leaf count
         * is NOT comparable to the canonical artifact.
         *
         * The baseline for a hold-out run is THE SAME RUN'S 13 remaining domains, not
         * the canonical artifact. Recovery is scored as precision/recall against the
         * withheld label, and any structural comparison is within-run. Diffing leaf
         * counts against the frozen 87 would compare two different constructions.
         */
        var excludeFromAnchoring: Set<String> = emptySet()

        var dagMode: DagMode = DagMode.DAG_MAX
            set(value) {
                field = value
                val isDag = (value == DagMode.DAG_MAX)
                enableStableQuestionIds = isDag
                enableResidualRouting = isDag
                enableResidualSplitGate = isDag
            }

        // ── Internal boolean flags (mapped by dagMode, overrideable for regression)
        var enableStableQuestionIds: Boolean = true
        var enableResidualRouting: Boolean = true
        var enableResidualSplitGate: Boolean = true
        var enableGtWarmStart: Boolean = false

        var fusionSimilarityThreshold: Double = 0.92
        var effectiveSupportFloor: Double = 2.0
        var defaultKappaPrior: Double = 10.0
    }

    var diagnostics: DiagnosticsConfig = DiagnosticsConfig()

    class DiagnosticsConfig {
        var enableProfiling: Boolean = false
    }

    fun formatConfigReport(): String {
        val sb = StringBuilder()
        sb.append("\n┌── TAXONOMY CONFIGURATION PARAMETERS ─────────────────────\n")
        sb.append("│ Execution Settings:\n")
        sb.append("│   - Dataset Type:         ${dataset.datasetType.name}\n")
        sb.append("│   - Num Iterations:       ${execution.numIterations}\n")
        sb.append("│   - Early Stopping:       ${execution.enableEarlyStopping}\n")
        sb.append("│   - Labeling:             ${execution.enableLabeling}\n")
        sb.append("│   - Selected Domains:     ${dataset.selectedDomains.ifEmpty { listOf("All") }}\n")
        sb.append("│   - Split Dataset:        ${dataset.splitDataset}\n")
        sb.append("│   - Test Split Ratio:     ${dataset.testSplitRatio}\n")
        sb.append("├── LLM & Embedding Models:\n")
        sb.append("│   - LLM Provider:         ${llm.provider}\n")
        sb.append("│   - Embedding Provider:   ${llm.embeddingProvider}\n")
        sb.append("│   - Embedding Model:      ${llm.embeddingModel}\n")
        sb.append("│   - Judge Model:          ${llm.judgeModel}\n")
        sb.append("│   - Labeling Model:       ${llm.labelingModel}\n")
        sb.append("│   - Max Judge Generality: ${llm.maxJudgeGenerality}\n")
        sb.append("├── Advanced Mathematical Formalism Controls:\n")
        sb.append("│   - DAG Mode:             ${formalism.dagMode}\n")
        sb.append("│   - Max Depth:            ${formalism.maxDepth}\n")
        sb.append("│   - Min Cluster Size:     ${formalism.minClusterSize}\n")
        sb.append("│   - Separation Bar:       ${formalism.proposalSeparationBar}\n")
        sb.append("│   - Lexicographic Tau:    ${formalism.tau}\n")
        sb.append("│   - Membership Floor:     ${formalism.membershipFloor}\n")
        sb.append("│   - Routing Beam Gamma:   ${formalism.routingBeamGamma}\n")
        sb.append("│   - Descent Margin:       ${formalism.descentMargin}\n")
        sb.append("│   - Fusion Sim Threshold: ${formalism.fusionSimilarityThreshold}\n")
        sb.append("│   - Eff Support Floor:    ${formalism.effectiveSupportFloor}\n")
        sb.append("│   - Default Kappa Prior:  ${formalism.defaultKappaPrior}\n")
        sb.append("└──────────────────────────────────────────────────────────")
        return sb.toString()
    }

    /** Capture the current tunables as an immutable, serializable snapshot (secrets excluded). */
    fun toEffectiveConfig(): EffectiveConfig = EffectiveConfig(
        execution = EffectiveConfig.Execution(
            numIterations = execution.numIterations,
            enableEarlyStopping = execution.enableEarlyStopping,
            enableLabeling = execution.enableLabeling
        ),
        dataset = EffectiveConfig.Dataset(
            datasetType = dataset.datasetType,
            splitDataset = dataset.splitDataset,
            testSplitRatio = dataset.testSplitRatio,
            selectedDomains = dataset.selectedDomains
        ),
        llm = EffectiveConfig.Llm(
            provider = llm.provider,
            embeddingProvider = llm.embeddingProvider,
            judgeModel = llm.judgeModel,
            labelingModel = llm.labelingModel,
            embeddingModel = llm.embeddingModel,
            maxJudgeGenerality = llm.maxJudgeGenerality,
            judgeDomains = llm.judgeDomains
        ),
        formalism = EffectiveConfig.Formalism(
            dagMode = formalism.dagMode,
            maxDepth = formalism.maxDepth,
            minClusterSize = formalism.minClusterSize,
            proposalSeparationBar = formalism.proposalSeparationBar,
            tau = formalism.tau,
            membershipFloor = formalism.membershipFloor,
            routingBeamGamma = formalism.routingBeamGamma,
            descentMargin = formalism.descentMargin,
            maxLeafAssignments = formalism.maxLeafAssignments,
            enableStableQuestionIds = formalism.enableStableQuestionIds,
            enableResidualRouting = formalism.enableResidualRouting,
            enableResidualSplitGate = formalism.enableResidualSplitGate,
            enableGtWarmStart = formalism.enableGtWarmStart,
            fusionSimilarityThreshold = formalism.fusionSimilarityThreshold,
            effectiveSupportFloor = formalism.effectiveSupportFloor,
            defaultKappaPrior = formalism.defaultKappaPrior
        ),
        diagnostics = EffectiveConfig.Diagnostics(
            enableProfiling = diagnostics.enableProfiling
        )
    )

    /** Apply a restored snapshot's tunables onto the live config. Secrets are left untouched. */
    fun applyEffectiveConfig(c: EffectiveConfig) {
        execution.numIterations = c.execution.numIterations
        execution.enableEarlyStopping = c.execution.enableEarlyStopping
        execution.enableLabeling = c.execution.enableLabeling

        dataset.datasetType = c.dataset.datasetType
        dataset.splitDataset = c.dataset.splitDataset
        dataset.testSplitRatio = c.dataset.testSplitRatio
        dataset.selectedDomains = c.dataset.selectedDomains

        llm.provider = c.llm.provider
        llm.embeddingProvider = c.llm.embeddingProvider
        llm.judgeModel = c.llm.judgeModel
        llm.labelingModel = c.llm.labelingModel
        llm.embeddingModel = c.llm.embeddingModel
        llm.maxJudgeGenerality = c.llm.maxJudgeGenerality
        llm.judgeDomains = c.llm.judgeDomains

        formalism.dagMode = c.formalism.dagMode
        formalism.maxDepth = c.formalism.maxDepth
        formalism.minClusterSize = c.formalism.minClusterSize
        formalism.proposalSeparationBar = c.formalism.proposalSeparationBar
        formalism.tau = c.formalism.tau
        formalism.membershipFloor = c.formalism.membershipFloor
        formalism.routingBeamGamma = c.formalism.routingBeamGamma
        formalism.descentMargin = c.formalism.descentMargin
        formalism.maxLeafAssignments = c.formalism.maxLeafAssignments
        formalism.enableStableQuestionIds = c.formalism.enableStableQuestionIds
        formalism.enableResidualRouting = c.formalism.enableResidualRouting
        formalism.enableResidualSplitGate = c.formalism.enableResidualSplitGate
        formalism.enableGtWarmStart = c.formalism.enableGtWarmStart
        formalism.fusionSimilarityThreshold = c.formalism.fusionSimilarityThreshold
        formalism.effectiveSupportFloor = c.formalism.effectiveSupportFloor
        formalism.defaultKappaPrior = c.formalism.defaultKappaPrior

        diagnostics.enableProfiling = c.diagnostics.enableProfiling
    }
}

@kotlinx.serialization.Serializable
enum class LlmProviderType {
    OLLAMA,
    AZURE
}

@kotlinx.serialization.Serializable
enum class DatasetType {
    MMLU_PRO,
    MMLU_ORIGINAL,
    ARC,
    TWENTY_NEWSGROUPS,
    AG_NEWS
}
