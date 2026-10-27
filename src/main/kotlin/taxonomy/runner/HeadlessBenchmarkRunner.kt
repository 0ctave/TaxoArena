package taxonomy.runner

import kotlinx.coroutines.runBlocking
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.jsonArray
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import kotlinx.serialization.json.encodeToJsonElement
import org.slf4j.LoggerFactory
import org.springframework.boot.CommandLineRunner
import org.springframework.stereotype.Component
import org.springframework.core.annotation.Order
import taxonomy.config.TaxonomyConfig
import taxonomy.service.TaxonomyBenchmarkService
import taxonomy.service.TaxonomyService
import taxonomy.service.TaxonomySnapshotManager
import taxonomy.service.TaxonomyArenaService
import taxonomy.dataset.ModelEvalStore
import taxonomy.service.TaxonomyRankingService
import taxonomy.service.ValidationService
import taxonomy.model.BenchmarkRequest
import taxonomy.model.ModelSource
import taxonomy.dataset.MMLUDatasetFetcher
import taxonomy.dataset.ModelEvalLoader
import taxonomy.model.GraphNode
import taxonomy.TaxonomyEngine
import taxonomy.service.TaxonomyJudgeService
import taxonomy.model.ModelRank
import taxonomy.model.Embedding
import taxonomy.utils.TaxonomyPerformanceTracker
import taxonomy.utils.ReportGenerator
import taxonomy.dataset.EmbeddingCache
import java.io.File
import java.time.Instant
import taxonomy.model.projectTo
import taxonomy.utils.StatisticsUtils
import taxonomy.tui.service.LeafDomainProfile
import taxonomy.model.BenchmarkReport
import kotlin.math.sqrt
import taxonomy.service.TaxonomyPersistence
import taxonomy.service.UnionGraft
import taxonomy.operations.TaxonomyOperations
import taxonomy.dataset.CorpusDomains

@Serializable
data class HeadlessCliConfig(
    val snapshotId: String = "unsaved",
    val models: List<String>,              // e.g. ["gpt-4o-2024-08-06", "llama-3-8b-instruct"]
    val queryLimit: Int = 0,               // 0 = no limit
    val category: String? = null,          // optional GT category limit
    val confidenceGate: Double = 0.65,
    val parallelism: Int = 6,
    val questionsPerRound: Int = 12,
    val reservedOnly: Boolean = true,
    // Resume a stopped/crashed run: keep the condition's existing match_history rows and
    // let the benchmark service reconstruct pair stats from them instead of wiping the
    // slate. Default false = the historical clear-and-start-fresh behaviour. A registered
    // run must never mix resume with a changed config/pool — same config, same db only.
    val resumeBenchmark: Boolean = false,
    // PROFILE mode: stop on SE targets per model x stratum instead of on rank
    // decisions (taxonomy.arena.ProfileTargets). profileStrataFile is the frozen
    // leaf->stratum map (experiment_configs/strata_profile_v1.json format).
    val profileMode: Boolean = false,
    val profileSeTarget: Double = 0.15,
    val profileStrataFile: String? = null,
    // Soft per-question reuse cap for the scheduler; Int.MAX_VALUE = historical behaviour.
    val maxQueryReuse: Int = Int.MAX_VALUE,
    // Optional reference-free match filter: "none" (default, byte-identical to the historical
    // scheduler) or "answerDisagreement". See taxonomy.arena.MatchFilter.
    val matchFilter: String = "none",
    // Acceptance floor for construction edits; null = keep the code default.
    val tau: Double? = null,
    // Post-loop final-metrics block; null = keep the code default.
    val enableFinalMetrics: Boolean? = null,
    // JSON file mapping depth-1 anchor label -> per-anchor separation bar; null = global bar.
    val adaptiveBarFile: String? = null,
    // D1 dimension sweep: MRL slice width and split-proposal PCA variants; null = code default.
    val embeddingSliceDim: Int? = null,
    val splitDropTopPcs: Int? = null,
    val splitWhiten: Boolean? = null,
    // PERF-8 exact proposal memo: "off" | "shadow" | "on"; null = code default (off).
    val proposalMemo: String? = null,
    val conditions: List<String> = listOf("MAIN", "ORACLE", "GENERIC_JUDGE", "RANDOM_SCHEDULER"),
    val outputDir: String = "experiment",
    val testRatio: Double = 0.3,           // 70/30 split
    val seed: Long = 42L,                  // deterministic seed
    val seeds: List<Long> = emptyList(),   // multi-seed support
    // Seed for the train/test split ONLY. Defaults to the construction seed, which is the
    // historical behaviour. Setting it pins the split while `seed`/`seeds` still vary
    // construction, which is the only way to separate sample variation from algorithmic
    // nondeterminism: with one knob driving both, a cross-seed spread confounds the two.
    val splitSeed: Long? = null,
    // H9-REM debug flag: seeded shuffle of the greedy construction loop's proposal order
    // (taxonomy.operations.ConstructionOrder). null = no shuffle = every run before the flag.
    // Only meaningful on a run that constructs (runPipeline = true, no unionSnapshots);
    // parseToml refuses it elsewhere so a registration cannot assert an order the run never
    // applied. Recorded in diagnostics/run_manifest.json.
    val constructionOrderShuffleSeed: Long? = null,
    // ANCHOR-FREE (registered 2026-09-16): grow the tree with no category anchors — every train
    // query at the root, the root a GROW site. false = the production bootstrap. Only meaningful
    // on a run that constructs (runPipeline = true, no unionSnapshots) and contradicts
    // excludeFromAnchoring (nothing is anchored, so nothing can be withheld from anchoring);
    // the init block refuses all three. Recorded in diagnostics/run_manifest.json (anchor_free).
    val anchorFree: Boolean = false,
    // K-SELECTION (registered 2026-09-19): geometric hysteresis on the splitter's creation-side
    // gates (weak-pair coarsening test and min-pair gate compare against multiplier x bar). null =
    // absent = 1.0 = the production path. Present: must lie in [1.0, 2.0] (init block, fatal
    // otherwise) and, like the shuffle seed, only meaningful on a run that constructs. Recorded in
    // diagnostics/run_manifest.json (proposal_accept_multiplier, 1.0 on every unprimed run).
    val proposalAcceptMultiplier: Double? = null,
    // Explicit held-out id file (reserved_test_queries.json format). Overrides the seeded split:
    // a seed does not reproduce a split across dataset-order changes (incident 2026-09-09).
    val reservedPoolFile: String? = null,
    // RP12 ARCH-V2-E-T: the engine pool file of a v2 pool (tools/analysis/v2_engine_pool.py output,
    // e.g. experiment_configs/engine_pool_pv2_41dbd3dbcd399df0.json). The split is taken AS GIVEN from
    // it (MMLUDatasetFetcher.splitByV2Pool: EVAL + GATE + their sentinels reserved, TRAIN one-to-one,
    // global closure checked), the global reserved keys are installed for every TrainOnlyGuard site,
    // and the build is stamped (snapshot settings.buildStamp, manifest split_v2, gate_ids.json).
    // null = absent = every existing path, byte-identical. Only meaningful on a run that constructs;
    // contradicts reservedPoolFile (two split sources); the init block refuses both.
    val v2PoolFile: String? = null,
    // RP12 B3: the union readout carries an item key (MAIN_union_routing_queries.csv gains a trailing item_id column,
    // plus MAIN_union_routing_train_queries.csv and MAIN_union_routing_leaves.csv; taxonomy.service.UnionRoutingExport).
    // false = absent = the pre-RP12 readout, byte-identical. Only meaningful on a union graft (the init block refuses it
    // elsewhere). Recorded in diagnostics/run_manifest.json (union_routing_item_key) only when true.
    val unionRoutingItemKey: Boolean = false,
    // READY_rp12_et D-2: the union graft admits a member built on ANOTHER pool of the same draw only when it is named here
    // with its engine pool file's LF sha, "pv2_<16 hex>:<64 hex>". Empty (absent) = no foreign member is admitted.
    val v2ForeignMembers: List<String> = emptyList(),
    // A human-declared second pin (FRAMEWORK item 18): the pool this run resolves (its own
    // split's, its loaded snapshot's, or the union's) must equal it, else the run refuses. It
    // replaces `pool_guard.py --activate` as the last step of a build: a build records its pool
    // and switches nothing, so the operator says which pool the run is about.
    val pool: String? = null,
    // "<snapshotId>:<count>" entries: a snapshot of record whose tree holds <count> EVAL texts
    // among its members (by content) may still be judged, and the count is printed as a
    // disclosure line under [SCORED-EVAL]. Any other count refuses. See TrainOnlyGuard.
    val acknowledgedEvalMembers: List<String> = emptyList(),
    val regenerateSplit: Boolean = false,
    val runPipeline: Boolean = false,
    val maxDepth: Int? = null,
    val minClusterSize: Int? = null,
    val proposalSeparationBar: Double? = null,
    val membershipFloor: Double? = null,
    val routingBeamGamma: Double? = null,
    val descentMargin: Double? = null,
    val acceptanceZ: Double? = null,
    val marginalEps: Double? = null,
    val maxK: Int? = null,
    val excludeFromAnchoring: List<String> = emptyList(),
    val expectedWithheldQueries: Int? = null,
    val enableRefitGate: Boolean? = null,
    val defaultKappaPrior: Double? = null,
    val enableLabeling: Boolean? = null,
    val judgeInduction: Boolean = false,
    val datasetType: String? = null,
    // Multi-corpus stage 0a (docs/multi_corpus_design.md §3.7). `corpora` lists the corpora a
    // run draws on; null = [datasetType]. `corpusDbPath` is the dataset/eval SQLite file; null =
    // the current path. Both defaults leave single-corpus runs unchanged.
    val corpora: List<String>? = null,
    val corpusDbPath: String? = null,
    // Multi-corpus stage 1b (federated construction): graft these per-corpus snapshots under a
    // union root instead of constructing. One snapshot per corpus listed in `corpora`; the union
    // reserved pool is the union of theirs. Empty = no graft (every other run).
    val unionSnapshots: List<String> = emptyList(),
    // Multi-corpus stage 1c: root routing rule for the union readout — "descent" (the production
    // trickle from the union root, the stage-1b behaviour), "flatLeaf" (nearest leaf centroid
    // over all grafted leaves) or "sourceGate" (nearest per-corpus root, then the production
    // descent inside that corpus tree). Read only by the union validation path.
    val unionRootRouting: String = taxonomy.service.UnionRouting.Rule.DEFAULT_KEY,
    val runBenchmark: Boolean = true,
    val runTrickle: Boolean = false,
    val domains: List<String> = emptyList(),
    val enableStableQuestionIds: Boolean? = null,
    val enableResidualRouting: Boolean? = null,
    val enableResidualSplitGate: Boolean? = null,
    val fusionSimilarityThreshold: Double? = null,
    val effectiveSupportFloor: Double? = null,
    val numIterations: Int? = null,
    val runBaselines: Boolean = true,
    val enableGtWarmStart: Boolean? = null,
    val maxLeafAssignments: Int? = null,
    val dagMode: String? = null,
    val enableProfiling: Boolean? = null,
    val judgeSeesOptions: Boolean? = null,
    val judgeOptionMode: String? = null,
    // JUDGE-WIRING (FRAMEWORK item 25): `judgeRecipe = "STACK-v2"` switches the judge to the
    // recipe path (grok + STACK-v2 + cached reference, raw Azure inference route); the other keys
    // override the kit path, model, completion budget and temperature literal. All absent = the
    // Mistral path, byte-identical. `judgeRecipeTemperature` absent = the field is OMITTED from the
    // payload and recorded as "omitted" (Amendment 1 D2); present = posted as a JSON float.
    val judgeRecipe: String? = null,
    val judgeRecipeKit: String? = null,
    val judgeRecipeModel: String? = null,
    val judgeRecipeMaxTokens: Int? = null,
    val judgeRecipeTemperature: Double? = null
) {
    init {
        // H9-REM: the shuffle is applied by the construction loop and nowhere else. On a run
        // that constructs nothing (runPipeline = false, or a union graft) the key would be
        // silently inert, and a registration must not assert an order the run never applied
        // (same principle as the matchFilter unknown-VALUE rule). Lives in the constructor so
        // the TOML parser and the JSON decoder share it: kotlinx.serialization goes through the
        // primary constructor, so a JSON config is checked by the same line.
        if (constructionOrderShuffleSeed != null) {
            require(runPipeline && unionSnapshots.isEmpty()) {
                "[CONFIG] constructionOrderShuffleSeed = $constructionOrderShuffleSeed asserts an order shuffle" +
                    " on a run that constructs nothing (needs runPipeline = true and no unionSnapshots)"
            }
        }
        // ANCHOR-FREE: same principle. The flag is applied by the construction bootstrap and
        // nowhere else, so a run that constructs nothing would carry it inertly; and a hold-out
        // (excludeFromAnchoring) presupposes anchors, which an anchor-free build has none of.
        if (anchorFree) {
            require(runPipeline && unionSnapshots.isEmpty()) {
                "[CONFIG] anchorFree = true asserts an anchor-free construction on a run that constructs" +
                    " nothing (needs runPipeline = true and no unionSnapshots)"
            }
            require(excludeFromAnchoring.isEmpty()) {
                "[CONFIG] anchorFree = true and excludeFromAnchoring = $excludeFromAnchoring contradict each other:" +
                    " an anchor-free build has no anchors to withhold a category from"
            }
        }
        // K-SELECTION: fail-closed range (the registration fixes [1.0, 2.0]; a NaN fails both
        // comparisons and is refused too), and the same "applied by the construction loop only"
        // principle as the shuffle seed: a run that constructs nothing must not carry it.
        // RP12 ARCH-V2-E-T: the v2 split is applied by the constructing path only, and it is a split
        // SOURCE: a second one (reservedPoolFile) would leave which side a row has undecided.
        if (v2PoolFile != null) {
            require(v2PoolFile.isNotBlank()) { "[CONFIG] v2PoolFile is empty" }
            // RP12 B2: a constructing run (runPipeline, no union) splits on it; a union graft (unionSnapshots,
            // no runPipeline) checks its members against it and installs its global keys.
            require((runPipeline && unionSnapshots.isEmpty()) || (!runPipeline && unionSnapshots.isNotEmpty())) {
                "[CONFIG] v2PoolFile = $v2PoolFile needs a constructing run (runPipeline = true, no unionSnapshots)" +
                    " or a union graft (unionSnapshots, runPipeline = false)"
            }
            require(reservedPoolFile == null) {
                "[CONFIG] v2PoolFile = $v2PoolFile and reservedPoolFile = $reservedPoolFile are two split sources; give one"
            }
        }
        if (v2ForeignMembers.isNotEmpty()) {
            require(v2PoolFile != null && unionSnapshots.isNotEmpty()) {
                "[CONFIG] v2ForeignMembers names foreign graft members on a run that is not a v2 union graft (needs v2PoolFile and unionSnapshots)"
            }
            taxonomy.dataset.V2ForeignMembers.parseForeign(v2ForeignMembers)
        }
        if (unionRoutingItemKey) {
            require(unionSnapshots.isNotEmpty()) {
                "[CONFIG] unionRoutingItemKey = true asserts an item-keyed union readout on a run that grafts no union (needs unionSnapshots)"
            }
        }
        if (proposalAcceptMultiplier != null) {
            require(proposalAcceptMultiplier >= 1.0 && proposalAcceptMultiplier <= 2.0) {
                "[CONFIG] proposalAcceptMultiplier = $proposalAcceptMultiplier is outside [1.0, 2.0]" +
                    " (K-SELECTION registers 1.05; absent = 1.0)"
            }
            require(runPipeline && unionSnapshots.isEmpty()) {
                "[CONFIG] proposalAcceptMultiplier = $proposalAcceptMultiplier asserts a creation-side" +
                    " acceptance rule on a run that constructs nothing (needs runPipeline = true and no unionSnapshots)"
            }
        }
        // INTENT-TRANSFER-S1 (docs/judge_v2_program.md L22682-L22710): an INTENT run is a label-free, ZERO-CALL construction on
        // ONE arm's TRAIN+GATE build DB whose GATE export is the reserved pool (tools/analysis/intent_s1_export.py). Every
        // other shape would read an intent corpus on a path the registration never admitted, so the init block refuses it
        // (shared by the TOML parser and the JSON decoder). No effect on any run without datasetType / corpora INTENT.
        if (datasetType?.uppercase() == "INTENT" || corpora?.any { it.uppercase() == "INTENT" } == true) {
            require(runPipeline && unionSnapshots.isEmpty()) {
                "[CONFIG] datasetType INTENT needs a constructing run (runPipeline = true, no unionSnapshots)"
            }
            require(corpora == null || corpora == listOf("INTENT")) {
                "[CONFIG] datasetType INTENT is single-corpus: corpora = $corpora is refused (one arm, one build DB)"
            }
            require(!corpusDbPath.isNullOrBlank()) {
                "[CONFIG] datasetType INTENT needs corpusDbPath = the arm's build DB (tools/analysis/intent_s1_export.py)"
            }
            require(!reservedPoolFile.isNullOrBlank() && v2PoolFile == null) {
                "[CONFIG] datasetType INTENT needs reservedPoolFile = the arm's GATE id export (and no v2PoolFile)"
            }
            require(!pool.isNullOrBlank()) {
                "[CONFIG] datasetType INTENT needs the [POOL-PIN] pool = the GATE export's id"
            }
            require(!runBenchmark && !judgeInduction && enableLabeling != true && judgeRecipe == null && models.isEmpty()) {
                "[CONFIG] datasetType INTENT is a zero-call build: runBenchmark, judgeInduction and enableLabeling must be false," +
                    " judgeRecipe absent and models = [] (runBenchmark=$runBenchmark, judgeInduction=$judgeInduction," +
                    " enableLabeling=$enableLabeling, judgeRecipe=$judgeRecipe, models=$models)"
            }
        }
    }
}

/**
 * gate_ids.json of a constructing run (FRAMEWORK Stage 0), extracted so it is testable: the function stamp,
 * the gate size, the (0) gate / eval overlap, the sorted gate ids and, ONLY on a v2 build (RP12), the build
 * stamp under `split_v2`. With [v2Stamp] null the text is exactly the pre-RP12 text.
 */
internal fun gateIdsJson(json: Json, ownPoolId: String?, gate: Set<Int>, v2Stamp: taxonomy.dataset.V2BuildStamp?): String {
    val gateJson = kotlinx.serialization.json.buildJsonObject {
        put("function", json.encodeToJsonElement(taxonomy.dataset.SplitSide.stamp(ownPoolId)))
        put("gate_size", kotlinx.serialization.json.JsonPrimitive(gate.size))
        put("gate_eval_overlap", kotlinx.serialization.json.JsonPrimitive(0))
        put("gate_ids", json.encodeToJsonElement(gate.sorted()))
        if (v2Stamp != null) put("split_v2", json.encodeToJsonElement(v2Stamp))
    }
    return json.encodeToString(gateJson)
}

@Component
@Order(2)
class HeadlessBenchmarkRunner(
    private val config: TaxonomyConfig,
    private val benchmarkService: TaxonomyBenchmarkService,
    private val snapshotManager: TaxonomySnapshotManager,
    private val taxonomyService: TaxonomyService,
    private val evalStore: ModelEvalStore,
    private val rankingService: TaxonomyRankingService,
    private val datasetFetcher: MMLUDatasetFetcher,
    private val evalLoader: ModelEvalLoader,
    private val taxonomyEngine: TaxonomyEngine,
    private val judgeService: TaxonomyJudgeService,
    private val embeddingCache: EmbeddingCache,
    private val arenaService: TaxonomyArenaService,
    private val perfTracker: TaxonomyPerformanceTracker,
    private val persistence: TaxonomyPersistence,
    private val ops: TaxonomyOperations,
    // JUDGE-WIRING: opened only by judgeRecipePreflight when the recipe is enabled.
    private val kitProvider: taxonomy.operations.RecipeKitProvider
) : CommandLineRunner {

    private val log = LoggerFactory.getLogger("taxonomy.HeadlessRunner")
    private val json = Json { prettyPrint = true; ignoreUnknownKeys = true }

    override fun run(vararg args: String?) {
        val configArg = args.indexOf("--config")
        if (configArg == -1) {
            // Only run if --config command line argument is passed
            return
        }

        val configPath = if (configArg + 1 < args.size) args[configArg + 1] else null
        if (configPath == null) {
            log.error("Missing path after --config parameter!")
            kotlin.system.exitProcess(1)
        }

        log.info("Starting Headless Benchmark Mode with config: $configPath")
        try {
            RatingsDbGuard.assertNotTracked()
            runHeadlessBenchmark(configPath)
            log.info("Headless Benchmark finished successfully.")
            kotlin.system.exitProcess(0)
        } catch (t: Throwable) {
            log.error("Headless Benchmark failed with error", t)
            kotlin.system.exitProcess(1)
        }
    }

    /**
     * JUDGE-WIRING preflight: with the recipe disabled this logs one line and returns before touching
     * anything. Enabled, it refuses (IllegalStateException, before any call) unless judgeOptionMode is
     * RESOLVED, the kit exists and its hash verifies, a key is present, and every condition has a
     * recipe form (MAIN / ORACLE / RANDOM_SCHEDULER; GENERIC_JUDGE, C3, C5 have none).
     */
    private fun judgeRecipePreflight(cliConfig: HeadlessCliConfig) {
        val rc = config.llm.judgeRecipe
        if (!rc.enabled) {
            log.info("[JUDGE-RECIPE] disabled: judge = ${config.llm.judgeModel} on the langchain4j path (byte-identical to the board of record)")
            return
        }
        rc.validate(config.llm.judgeOptionMode)
        val bad = cliConfig.conditions.filter { it.uppercase() !in setOf("MAIN", "ORACLE", "RANDOM_SCHEDULER") }
        check(bad.isEmpty()) { "[JUDGE-RECIPE] conditions $bad have no recipe form; run the recipe with conditions in {MAIN, ORACLE, RANDOM_SCHEDULER}" }
        val kit = kitProvider.get()                                  // opens read-only, verifies kit_hash and meta.recipe
        rc.kitHash = kit.kitHash
        val hasKey = !System.getenv("AZURE_GROK_API_KEY").isNullOrBlank() || config.llm.azure.apiKey.isNotBlank()
        check(hasKey) { "[JUDGE-RECIPE] no judge key: export AZURE_GROK_API_KEY (or AZURE_AI_API_KEY) before a recipe run" }
        check(config.llm.azure.endpoint.isNotBlank()) { "[JUDGE-RECIPE] AZURE_AI_ENDPOINT is blank; the recipe posts to {endpoint}/models/chat/completions" }
        log.info(
            "[JUDGE-RECIPE] ${rc.name} ENABLED: model ${rc.model} | route /models/chat/completions?api-version=${rc.inferenceApiVersion}" +
                " | max_tokens ${rc.maxTokens} | temperature ${rc.temperatureLabel} | kit ${rc.kitPath} hash ${rc.kitHash}" +
                " (${kit.questionCount} routed questions, reference_model ${kit.meta["reference_model"]})" +
                " | fingerprint ${rc.fingerprint()} | judgeOptionMode ${config.llm.judgeOptionMode} | key ${if (!System.getenv("AZURE_GROK_API_KEY").isNullOrBlank()) "AZURE_GROK_API_KEY" else "azure.apiKey"}" +
                " | judge_calls provenance -> ${System.getProperty("ranking.db.path", "ratings.db")}"
        )
    }

    private fun runHeadlessBenchmark(configPath: String) = runBlocking {
        val configFile = File(configPath)
        if (!configFile.exists()) {
            throw IllegalArgumentException("Config file does not exist: ${configFile.absolutePath}")
        }

        val cliConfig = if (configPath.endsWith(".toml", ignoreCase = true)) {
            parseToml(configFile.readText())
        } else {
            json.decodeFromString<HeadlessCliConfig>(configFile.readText())
        }

        log.info("Loaded CLI Configuration: $cliConfig")

        // Apply any pipeline configuration overrides from TOML config
        cliConfig.maxDepth?.let { config.formalism.maxDepth = it }
        cliConfig.minClusterSize?.let { config.formalism.minClusterSize = it }
        cliConfig.proposalSeparationBar?.let { config.formalism.proposalSeparationBar = it }
        cliConfig.membershipFloor?.let { config.formalism.membershipFloor = it }
        cliConfig.routingBeamGamma?.let { config.formalism.routingBeamGamma = it }
        cliConfig.descentMargin?.let { config.formalism.descentMargin = it }
        cliConfig.tau?.let { config.formalism.tau = it }
        // H9-REM: the shuffle seed is TOML-only. FormalismConfig is @ConfigurationProperties-
        // bound, so a `construction-order-shuffle-seed` key in application.yml or the
        // environment would otherwise bind silently and shuffle a run whose registered config
        // never asked for it. Refuse an effective value that did not come from the config file.
        require(config.formalism.constructionOrderShuffleSeed == null || cliConfig.constructionOrderShuffleSeed != null) {
            "[CONFIG] formalism.constructionOrderShuffleSeed = ${config.formalism.constructionOrderShuffleSeed} was bound" +
                " outside the run's config file (application.yml / environment); the H9-REM shuffle is TOML-only"
        }
        cliConfig.constructionOrderShuffleSeed?.let {
            config.formalism.constructionOrderShuffleSeed = it
            log.warn("[H9-ORDER] construction-order shuffle ACTIVE, seed=$it (debug arm; the DAG is NOT the production path)")
        }
        // ANCHOR-FREE: TOML-only for the same reason as the shuffle seed — an `anchor-free: true`
        // bound from application.yml / environment would build an unanchored tree under a
        // registered config that never asked for one.
        require(!config.formalism.anchorFree || cliConfig.anchorFree) {
            "[CONFIG] formalism.anchorFree = true was bound outside the run's config file" +
                " (application.yml / environment); the ANCHOR-FREE flag is TOML-only"
        }
        if (cliConfig.anchorFree) {
            config.formalism.anchorFree = true
            log.warn("[ANCHOR-FREE] anchor-free construction ACTIVE: no category anchors, every train query starts at the root (the DAG is NOT the production path)")
        }
        // K-SELECTION: TOML-only for the same reason — a `proposal-accept-multiplier` bound from
        // application.yml / environment would prime the creation gate under a registered config
        // that never asked for it. The value itself was range-checked in HeadlessCliConfig's init.
        require(config.formalism.proposalAcceptMultiplier == 1.0 || cliConfig.proposalAcceptMultiplier != null) {
            "[CONFIG] formalism.proposalAcceptMultiplier = ${config.formalism.proposalAcceptMultiplier} was bound" +
                " outside the run's config file (application.yml / environment); the K-SELECTION multiplier is TOML-only"
        }
        cliConfig.proposalAcceptMultiplier?.let {
            config.formalism.proposalAcceptMultiplier = it
            if (it != 1.0) {
                log.warn("[K-SELECTION] creation-side hysteresis ACTIVE: proposals accepted only at min-pair >= $it x bar (K-SELECTION arm; merger bar unchanged; the DAG is NOT the production path)")
            } else {
                log.info("[K-SELECTION] proposalAcceptMultiplier = 1.0 declared explicitly: the production gate, byte-identical to the key absent")
            }
        }
        cliConfig.adaptiveBarFile?.let { f ->
            val bars = kotlinx.serialization.json.Json.parseToJsonElement(java.io.File(f).readText())
            config.formalism.adaptiveBars = (bars as kotlinx.serialization.json.JsonObject)
                .mapValues { (_, v) -> (v as kotlinx.serialization.json.JsonPrimitive).content.toDouble() }
            log.info("[ADAPTIVE-BAR] loaded ${config.formalism.adaptiveBars.size} per-anchor bars from $f")
        }
        cliConfig.embeddingSliceDim?.let { config.formalism.embeddingSliceDim = it }
        cliConfig.splitDropTopPcs?.let { config.formalism.splitDropTopPcs = it }
        cliConfig.splitWhiten?.let { config.formalism.splitWhiten = it }
        cliConfig.proposalMemo?.let {
            config.formalism.proposalMemo = taxonomy.operations.MemoMode.parse(it).name.lowercase()
            log.info("[MEMO-X] proposalMemo = ${config.formalism.proposalMemo}")
        }
        // Must precede the first GraphNode/projection: every node's sliceDim and every
        // cached projection read this width at construction time.
        taxonomy.model.EmbeddingSlice.width = config.formalism.embeddingSliceDim
        log.info("[SLICE] embedding slice width = ${config.formalism.embeddingSliceDim}, " +
            "split PCA dropTop=${config.formalism.splitDropTopPcs} whiten=${config.formalism.splitWhiten}")
        cliConfig.enableFinalMetrics?.let { config.execution.enableFinalMetrics = it }
        cliConfig.acceptanceZ?.let { config.formalism.acceptanceZ = it }
        cliConfig.marginalEps?.let { config.formalism.marginalEps = it }
        cliConfig.maxK?.let { config.formalism.maxK = it }
        if (cliConfig.excludeFromAnchoring.isNotEmpty())
            config.formalism.excludeFromAnchoring = cliConfig.excludeFromAnchoring.toSet()
        cliConfig.expectedWithheldQueries?.let { config.formalism.expectedWithheldQueries = it }
        cliConfig.enableRefitGate?.let { config.formalism.enableRefitGate = it }
        // Headless splits on cliConfig.testRatio and never reads dataset.testSplitRatio, so the
        // two drifted: the banner and — more seriously — the EffectiveConfig provenance record
        // reported the Spring default (0.2) while every run actually split at the TOML value
        // (0.3). Sync them so the recorded configuration is the one that ran.
        config.dataset.testSplitRatio = cliConfig.testRatio
        cliConfig.defaultKappaPrior?.let { config.formalism.defaultKappaPrior = it }
        cliConfig.enableLabeling?.let { config.execution.enableLabeling = it }
        cliConfig.datasetType?.let {
            config.dataset.datasetType = taxonomy.config.DatasetType.valueOf(it.uppercase())
        }
        // Multi-corpus (docs/multi_corpus_design.md §3.7): `corpora = ["X"]` for a built-in type
        // is sugar for `datasetType = "X"`; a leaderboard source, or a union of them, is fetched
        // from the multi-corpus DB through `dataset.corpora` (stage 1) and the legacy
        // `datasetType` is left as configured. The DB path is published as the Spring property
        // before the context starts (Application.main), because the SQLite beans connect at
        // construction; verify here that the running store actually opened the requested file.
        val corpora = cliConfig.corpora ?: listOf(config.dataset.datasetType.name)
        if (corpora.size == 1 && corpora.single() in taxonomy.dataset.CorpusRegistry.BUILTIN) {
            config.dataset.datasetType = taxonomy.config.DatasetType.valueOf(corpora.single())
            config.dataset.corpora = emptyList()
        } else {
            config.dataset.corpora = corpora
        }
        cliConfig.corpusDbPath?.let { requested ->
            require(evalStore.dbPath == requested) {
                "[CONFIG] corpusDbPath = '$requested' but the eval store opened '${evalStore.dbPath}':" +
                    " the path must reach the beans at start-up (TOML via --config, or" +
                    " -Dtaxoadapt.eval.db-path); a JSON config cannot set it"
            }
        }
        log.info("[CORPUS] corpora=$corpora corpusDbPath=${evalStore.dbPath}")

        // NOTE: the three enable* flags (stable ids / residual routing / residual split
        // gate) are deliberately NOT applied here: dagMode's setter rewrites all three
        // as a block, so they must be applied only after dagMode, below. Assigning them
        // here as well would be dead code that a later reordering could silently revive.
        cliConfig.fusionSimilarityThreshold?.let { config.formalism.fusionSimilarityThreshold = it }
        cliConfig.effectiveSupportFloor?.let { config.formalism.effectiveSupportFloor = it }
        cliConfig.enableGtWarmStart?.let { config.formalism.enableGtWarmStart = it }
        cliConfig.maxLeafAssignments?.let { config.formalism.maxLeafAssignments = it }
        // dagMode's setter rewrites enableStableQuestionIds / enableResidualRouting /
        // enableResidualSplitGate as a block, so it MUST be applied before the individual
        // overrides — otherwise it silently clobbers them and the flags documented as
        // "overrideable for regression" are not in fact overrideable.
        // residual routing; TREE_BASELINE would switch all four off together.
        cliConfig.dagMode?.let {
            config.formalism.dagMode = taxonomy.config.DagMode.valueOf(it.uppercase())
        }
        cliConfig.enableResidualRouting?.let { config.formalism.enableResidualRouting = it }
        cliConfig.enableResidualSplitGate?.let { config.formalism.enableResidualSplitGate = it }
        cliConfig.enableStableQuestionIds?.let { config.formalism.enableStableQuestionIds = it }
        cliConfig.numIterations?.let { config.execution.numIterations = it }
        cliConfig.enableProfiling?.let { config.diagnostics.enableProfiling = it }
        cliConfig.judgeSeesOptions?.let { config.llm.judgeSeesOptions = it }
        cliConfig.judgeOptionMode?.let { config.llm.judgeOptionMode = it.trim().uppercase() }
        // JUDGE-WIRING: the same keys from a JSON config (parseToml already applied them to the live
        // config; re-applying is idempotent).
        cliConfig.judgeRecipe?.let { config.llm.judgeRecipe.enabled = true; config.llm.judgeRecipe.name = it }
        cliConfig.judgeRecipeKit?.let { config.llm.judgeRecipe.kitPath = it }
        cliConfig.judgeRecipeModel?.let { config.llm.judgeRecipe.model = it }
        cliConfig.judgeRecipeMaxTokens?.let { config.llm.judgeRecipe.maxTokens = it }
        cliConfig.judgeRecipeTemperature?.let { config.llm.judgeRecipe.temperature = it }
        judgeRecipePreflight(cliConfig)

        val targetDomains =if (cliConfig.domains.isNotEmpty()) cliConfig.domains else (cliConfig.category?.let { listOf(it) } ?: emptyList())
        if (targetDomains.isNotEmpty()) {
            config.dataset.selectedDomains = targetDomains
        }

        val seeds = if (cliConfig.seeds.isNotEmpty()) cliConfig.seeds else listOf(cliConfig.seed)

        // Only the FIRST seed in an in-process loop routes held-out queries correctly. Every
        // later seed strands roughly 80% of the test set as residuals (measured on seed 137:
        // NoMatchRate 0.816 in-loop against 0.0 isolated, Top-1 5.31% against 74.90%), while
        // the taxonomy itself looks healthy — purity ~0.76, plausible leaf counts, exit 0 — so
        // the corruption reads as enormous seed variance rather than as an error. Baselines are
        // unaffected because they use flat centroid assignment instead of routing through the
        // graph, which makes a corrupted run look internally consistent.
        //
        // The routing path is not yet repaired; this refuses the configuration instead of
        // producing plausible garbage. Run one seed per process.
        require(seeds.size <= 1) {
            "Multi-seed arrays route held-out queries for the first seed only. " +
                "Requested seeds=$seeds. Use one seed per process (see " +
                "experiment_configs/calibration/cal_iso_s*.toml)."
        }

        for (currentSeed in seeds) {
            perfTracker.clear()
            val baseDir = File(cliConfig.outputDir + "/seed_$currentSeed")
            baseDir.mkdirs()
            taxonomy.model.ExperimentOutputContext.activeBaseDir = baseDir
            val seedLogFile = File(baseDir, "headless_run.log")
            val seedAppender = try {
                startFileLogging(seedLogFile.absolutePath)
            } catch (e: Exception) {
                log.error("Failed to initialize seed file logging: ${e.message}")
                null
            }

            // Opened before anything else so a crash during construction still leaves a manifest
            // saying which commit and config produced it. The run log and dag_snapshots are
            // registered now but copied at close(), when the appender has flushed — copying the
            // log early would truncate the tail, which is where convergence lives.
            taxonomy.diagnostics.DiagnosticsBundle.open(
                outputDir = baseDir,
                configPath = File(configPath),
                resolvedConfigSummary = cliConfig.toString()
            )
            taxonomy.diagnostics.DiagnosticsBundle.registerCopy(seedLogFile, "headless_run.log")
            taxonomy.diagnostics.DiagnosticsBundle.registerCopy(
                File(baseDir, "dag_snapshots.jsonl"), "dag_snapshots.jsonl"
            )

            try {
                log.info("==================================================")
                log.info("STARTING PIPELINE AND EVALUATION WITH SEED: $currentSeed")
                log.info("==================================================")

                var snapshotId = cliConfig.snapshotId
                var root: GraphNode
                var ownPoolId: String? = null

            if (cliConfig.runPipeline) {
                log.info("Headless pipeline execution enabled. Starting DAG generation pipeline...")
                if (!datasetFetcher.isDatasetDownloaded()) {
                    log.info("Downloading dataset...")
                    datasetFetcher.downloadDataset()
                }
                log.info("Loading dataset for domains: $targetDomains")
                val dataset = datasetFetcher.fetchDataset(
                    maxQueries = cliConfig.queryLimit.takeIf { it > 0 } ?: Int.MAX_VALUE,
                    selectedDomains = targetDomains
                )
                val effectiveSplitSeed = cliConfig.splitSeed ?: currentSeed
                // RP12 ARCH-V2-E-T: the v2 pool, loaded and checked (L1-L5) before anything splits.
                val v2Pool = cliConfig.v2PoolFile?.let { taxonomy.dataset.V2EnginePool.load(File(it)) }
                val split = if (v2Pool != null) {
                    log.warn("[SPLIT-V2] the split is taken AS GIVEN from ${cliConfig.v2PoolFile} (${v2Pool.poolId}, ${v2Pool.rule}); seed, testRatio and reservedPoolFile are not used for the split")
                    datasetFetcher.splitByV2Pool(dataset, v2Pool)
                } else if (cliConfig.reservedPoolFile != null) {
                    log.info("Splitting dataset from the explicit reserved-pool file ${cliConfig.reservedPoolFile} (seed ignored for the split)")
                    datasetFetcher.splitByReservedFile(dataset, File(cliConfig.reservedPoolFile))
                } else {
                    log.info(
                        "Splitting dataset into train/test (ratio=${cliConfig.testRatio}," +
                            " splitSeed=$effectiveSplitSeed, constructionSeed=$currentSeed)..."
                    )
                    datasetFetcher.splitTrainTest(dataset, testRatio = cliConfig.testRatio, seed = effectiveSplitSeed)
                }
                val trainSet = split.train
                val testSet = split.test
                // The pool this run will be judged against comes from the split itself, never
                // from a pointer read back from the DB: saveSnapshot verifies the root file still
                // hashes to it (a concurrent run can rewrite that file), and [POOL-PIN] below
                // compares it with the declared `pool`.
                ownPoolId = split.poolId
                if (cliConfig.pool != null) {
                    // RP12: on a v2 build the declared pool is the v2 pool id (the id-list pool is recorded beside it).
                    val resolved = v2Pool?.poolId ?: ownPoolId
                    check(resolved == cliConfig.pool) { "[POOL-PIN] this split records pool $resolved but the config declares pool = ${cliConfig.pool}; refusing" }
                }
                // RP12: global reserved keys installed, manifest split_v2 recorded, stamp returned (V2EnginePool.activate).
                val v2Stamp = v2Pool?.let { p ->
                    p.activate(split, File(configPath), currentSeed, config.formalism.constructionOrderShuffleSeed).also {
                        log.warn("[TRAIN-ONLY] global reserved keys installed: ${p.globalReservedKeys.size} (${p.poolId}, all corpora, sentinels included); build stamp recorded")
                    }
                }
                // GATE slice of TRAIN (FRAMEWORK Stage 0): written with the function stamp. Nothing
                // consumes it yet (the batch loop has no held-out epoch gate; EpochGate.NONE).
                run {
                    val gateFile = File(baseDir, "gate_ids.json")
                    gateFile.writeText(gateIdsJson(json, ownPoolId, split.gate, v2Stamp))
                }
                taxonomy.diagnostics.DiagnosticsBundle.recordCorpus(
                    seed = currentSeed, splitSeed = cliConfig.splitSeed,
                    corpusSize = dataset.values.sumOf { it.size },
                    trainSize = trainSet.values.sumOf { it.size },
                    testSize = testSet.values.sumOf { it.size },
                    domains = targetDomains.toList(),
                    reservedPoolId = ownPoolId,
                    embeddingModel = config.llm.embeddingModel, judgeModel = config.llm.judgeModel,
                    gateSize = split.gate.size, gateEvalOverlap = 0,
                    functionStamp = taxonomy.dataset.SplitSide.stamp(ownPoolId)
                )
                log.info("[POOL] recorded ${ownPoolId ?: "<none>"} (seed=$effectiveSplitSeed, gate=${split.gate.size}, closedByContent=${split.closedByContent}); nothing activated")
                // H9-REM: the EFFECTIVE value (null on every non-shuffled run) goes into the
                // manifest, so a post-flag manifest states explicitly that no shuffle ran.
                taxonomy.diagnostics.DiagnosticsBundle.recordConstructionOrder(config.formalism.constructionOrderShuffleSeed)
                // RP12: the v2 build stamp (absent key on every non-v2 run).
                v2Stamp?.let { taxonomy.diagnostics.DiagnosticsBundle.recordSplitV2(it.toManifest()) }
                // EMB-TARGET2 C-ET-5 / E1-ROUTE R2: only when the explicit cache-file property is given (absent -> no manifest key);
                // the working copy's source sha256 beside it when the launcher passed it
                taxonomy.diagnostics.DiagnosticsBundle.recordEmbeddingCacheFromProperties { System.getProperty(it) }
                // ANCHOR-FREE: the effective value (false on every anchored run) goes into the
                // manifest, so a post-flag manifest states explicitly that the anchors were used.
                taxonomy.diagnostics.DiagnosticsBundle.recordAnchorFree(config.formalism.anchorFree)
                // K-SELECTION: the effective multiplier (1.0 on every unprimed run) goes into the
                // manifest, so a post-flag manifest states explicitly which creation gate ran.
                taxonomy.diagnostics.DiagnosticsBundle.recordProposalAcceptMultiplier(config.formalism.proposalAcceptMultiplier)

                log.info("Running GMM splitting and trickle routing pipeline...")
                root = taxonomyEngine.adaptTaxonomy(
                    rootLabel = datasetFetcher.datasetLabel(),
                    dataset = trainSet.mapValues { (_, qs) -> qs.map { it.text } }
                )
                // TRAIN-only tree state, by content (FRAMEWORK guard 3): the EVAL keys are the test
                // set's texts plus the pool's own texts (the pool may name questions the loaded
                // dataset slice does not carry). FATAL.
                run {
                    val evalTexts = HashSet<String>()
                    testSet.values.forEach { qs -> qs.forEach { evalTexts.add(it.text) } }
                    if (ownPoolId != null) runCatching { evalTexts.addAll(evalStore.getReservedQuestionTexts(ownPoolId!!)) }
                    // RP12: plus the global reserved keys of a v2 build (the same set when none is installed).
                    val report = taxonomy.model.TrainOnlyGuard.evalMembers(root, taxonomy.model.TrainOnlyGuard.withGlobal(taxonomy.model.TrainOnlyGuard.keysOf(evalTexts)))
                    taxonomy.model.TrainOnlyGuard.assertNone(report, "after construction")
                    log.info("[TRAIN-ONLY] after construction: 0 EVAL texts among the tree's members (${evalTexts.size} keys checked)")
                }

                if (cliConfig.judgeInduction) {
                    log.info("Starting headless LLM judge prompt induction...")
                    judgeService.generateJudgesForDag(root, poolId = ownPoolId ?: error("[JUDGE-LEAK] no pool recorded for this split; refusing induction"), replaceExisting = true)
                }

                log.info("Saving generated DAG snapshot to database...")
                val snapshotDesc = "Headless Run Auto-generated DAG"
                val snapshot = snapshotManager.saveSnapshot(root, snapshotDesc, expectedPoolId = ownPoolId, buildStamp = v2Stamp)
                    ?: throw IllegalStateException("Failed to save snapshot for the newly generated DAG")
                snapshotId = snapshot.id
                log.info("Successfully generated and saved snapshot. Snapshot ID: $snapshotId")

                // Generate baseline snapshots via Python subprocess
                if (cliConfig.runBaselines) {
                    try {
                        // The baselines must withhold THIS run's pool, never a default one: the script has no default
                        // pool (SPLIT-FUNCTION-IMPL); it verifies a registry pool by its id file and any other pool by rows.
                        val baselinePool = ownPoolId
                            ?: error("[POOL-PIN] no pool recorded for this split; refusing to generate baselines without one")
                        log.info("Generating baseline snapshots via Python subprocess (pool $baselinePool)...")
                        val pb = ProcessBuilder("python", "scripts/generate_baselines.py", baselinePool)
                        pb.directory(File("."))
                        pb.redirectOutput(ProcessBuilder.Redirect.INHERIT)
                        pb.redirectError(ProcessBuilder.Redirect.INHERIT)
                        val process = pb.start()
                        val exitCode = process.waitFor()
                        if (exitCode == 0) {
                            log.info("Baseline snapshots successfully generated.")
                        } else {
                            log.error("Baseline generation failed with exit code $exitCode")
                        }
                    } catch (e: Exception) {
                        log.error("Failed to run baseline generator: ${e.message}", e)
                    }
                }
            } else if (cliConfig.unionSnapshots.isNotEmpty()) {
                val assembled = assembleUnion(cliConfig, currentSeed, File(configPath))
                root = assembled.root
                snapshotId = assembled.snapshotId
                // The grafted run owns the union pool from here on (after the TRAIN-ONLY FATAL in
                // assembleUnion): a union run with runBenchmark = true resolves its pool to it, not
                // to whichever member snapshot loadSnapshot pinned last.
                ownPoolId = assembled.poolId
            } else {
                log.info("Loading pre-existing snapshot: $snapshotId")
                root = snapshotManager.loadSnapshot(snapshotId)
                    ?: throw IllegalStateException("Could not load snapshot: $snapshotId")
                taxonomy.diagnostics.DiagnosticsBundle.recordCorpus(
                    seed = currentSeed, splitSeed = cliConfig.splitSeed,
                    corpusSize = -1, trainSize = -1, testSize = -1,
                    domains = targetDomains.toList(),
                    reservedPoolId = snapshotManager.lastLoadedReservedPoolId,
                    embeddingModel = config.llm.embeddingModel, judgeModel = config.llm.judgeModel
                )
            }

            // Apply fallback judge prompts to all nodes in the loaded/generated tree to prevent runtime IllegalStateException
            fun ensureJudgePrompts(n: GraphNode, condition: String) {
                val isMain = condition.equals("MAIN", ignoreCase = true)
                if (n.children.isEmpty()) { // leaf node
                    if (isMain && cliConfig.runBenchmark && (n.judgePrompt.isNullOrBlank() || n.judgeRubric.isNullOrBlank())) {
                        throw IllegalStateException("Missing custom induced judge prompt/rubric for leaf node '${n.label}' (id=${n.id}) under MAIN condition!")
                    }
                }
                if (n.judgePrompt.isNullOrBlank()) {
                    n.judgePrompt = "You are a domain-expert judge evaluating answers in ${n.label}."
                }
                if (n.judgeRubric.isNullOrBlank()) {
                    n.judgeRubric = "Evaluate correctness based on accuracy and reasoning clarity."
                }
                n.children.forEach { ensureJudgePrompts(it, condition) }
            }
            ensureJudgePrompts(root, "MAIN")

            taxonomyService.setGraph(root)
            log.info("Active graph node set: ${root.id}")

            // Deterministic train/test split if requested for pre-existing snapshot
            if (cliConfig.regenerateSplit && !cliConfig.runPipeline) {
                log.info("Regenerating deterministic 70/30 split (ratio=${cliConfig.testRatio}, seed=$currentSeed)")
                if (!datasetFetcher.isDatasetDownloaded()) {
                    log.info("Downloading dataset...")
                    datasetFetcher.downloadDataset()
                }
                val dataset = datasetFetcher.fetchDataset(
                    maxQueries = cliConfig.queryLimit.takeIf { it > 0 } ?: Int.MAX_VALUE,
                    selectedDomains = targetDomains
                )
                val regenerated = datasetFetcher.splitTrainTest(dataset, testRatio = cliConfig.testRatio, seed = currentSeed)
                log.info("[POOL] regenerated split recorded as ${regenerated.poolId}; nothing activated (the loaded snapshot's pool stays pinned)")
            }

            // 3. Create export directories per seed
            val baseDir = File(cliConfig.outputDir + "/seed_$currentSeed")
            val validationDir = File(baseDir, "validation")
            val judgingDir = File(baseDir, "judging")
            validationDir.mkdirs()
            judgingDir.mkdirs()
            taxonomy.model.ExperimentOutputContext.activeBaseDir = baseDir

            // Export bridge details for diagnostics
            exportBridgeNodes(validationDir, root)
            exportBridgeResiduals(validationDir, root)

            // 4. Run trickle validation if enabled
            val reportsByCondition = mutableMapOf<String, BenchmarkReport>()
            val completedConditions = mutableListOf<String>()
            val logicalComparisonsMap = mutableMapOf<String, Int>()
            val judgeApiCallsMap = mutableMapOf<String, Int>()

            // 4. Run each condition back-to-back if enabled
            if (cliConfig.runBenchmark) {
                cliConfig.conditions.forEach { condition ->
                    log.info("========================================")
                    log.info("RUNNING BENCHMARK CONDITION: $condition")
                    log.info("========================================")

                    val isKmeans = condition.equals("KMEANS_BASELINE", ignoreCase = true)
                    val isWard = condition.equals("WARD_BASELINE", ignoreCase = true)
                    val isRandomNull = condition.equals("RANDOMNULL_BASELINE", ignoreCase = true)

                    val baseSnapshotId = snapshotId.substringBefore("_MAIN").substringBefore("_ORACLE").substringBefore("_C3").substringBefore("_C5").substringBefore("_GENERIC_JUDGE").substringBefore("_RANDOM_SCHEDULER").substringBefore("_KMEANS_BASELINE").substringBefore("_WARD_BASELINE").substringBefore("_RANDOMNULL_BASELINE")

                    val activeRoot = when {
                        isKmeans -> {
                            log.info("Loading Flat k-means baseline snapshot...")
                            snapshotManager.loadSnapshot("${baseSnapshotId}_baseline_kmeans")
                                ?: throw IllegalStateException("Required KMEANS_BASELINE snapshot not found: ${baseSnapshotId}_baseline_kmeans")
                        }
                        isWard -> {
                            log.info("Loading HAC Ward baseline snapshot...")
                            snapshotManager.loadSnapshot("${baseSnapshotId}_baseline_ward")
                                ?: throw IllegalStateException("Required WARD_BASELINE snapshot not found: ${baseSnapshotId}_baseline_ward")
                        }
                        isRandomNull -> {
                            log.info("Loading Random null baseline snapshot...")
                            snapshotManager.loadSnapshot("${baseSnapshotId}_baseline_randomnull")
                                ?: throw IllegalStateException("Required RANDOMNULL_BASELINE snapshot not found: ${baseSnapshotId}_baseline_randomnull")
                        }
                        else -> root
                    }

                    val isBaseline = isKmeans || isWard || isRandomNull
                    if (cliConfig.judgeInduction && isBaseline) {
                        log.info("Running judge prompt induction for baseline condition $condition to isolate topology effect...")
                        val inductionPool = ownPoolId ?: snapshotManager.lastLoadedReservedPoolId
                            ?: error("[JUDGE-LEAK] no pool for baseline induction on $condition")
                        judgeService.generateJudgesForDag(activeRoot, poolId = inductionPool, replaceExisting = true)
                    }

                    ensureJudgePrompts(activeRoot, condition)
                    taxonomyService.setGraph(activeRoot)

                    // Suffix active snapshotId to isolate condition stats in SQLite
                    val suffixedSnapshotId = "${snapshotId}_$condition"
                    taxonomyService.setActiveSnapshotId(suffixedSnapshotId)
                    
                    // Fresh run: clear this condition's prior state so the experiment starts from
                    // scratch. Resume run: KEEP match_history — the benchmark service reconstructs
                    // pair stats and completed slots from it, so already-paid verdicts are not
                    // re-judged. Before 2026-09-05 this clear was unconditional, which made every
                    // relaunch silently wipe a crashed run's verdicts and re-judge from zero.
                    if (cliConfig.resumeBenchmark) {
                        val kept = rankingService.countRecordedMatches(suffixedSnapshotId)
                        if (kept > 0) {
                            log.warn("[RESUME] resumeBenchmark=true: keeping $kept recorded matches for" +
                                " '$suffixedSnapshotId'; pair stats will be reconstructed from them." +
                                " Resume REQUIRES the identical config, pool and db as the interrupted run.")
                        } else {
                            log.info("[RESUME] resumeBenchmark=true but no recorded matches for" +
                                " '$suffixedSnapshotId' — starting fresh.")
                        }
                    } else {
                        rankingService.clearRatings(suffixedSnapshotId)
                    }

                    val modelSources = cliConfig.models.map { ModelSource(it) }
                    val profileStrata: Map<String, String> = if (cliConfig.profileMode) {
                        val path = cliConfig.profileStrataFile
                            ?: throw IllegalStateException("profileMode = true requires profileStrataFile")
                        val f = File(path)
                        check(f.exists()) { "profileStrataFile not found: " + f.absolutePath }
                        val root = Json.parseToJsonElement(f.readText()).jsonObject
                        val map = HashMap<String, String>()
                        for (el in root["strata"]!!.jsonArray) {
                            val o = el.jsonObject
                            val sid = o["id"]!!.jsonPrimitive.content
                            for (l in o["leafIds"]!!.jsonArray) map[l.jsonPrimitive.content] = sid
                        }
                        log.info("[PROFILE] loaded " + map.size + " leaf->stratum mappings over " +
                            map.values.toSet().size + " strata from " + path +
                            " (SE target " + cliConfig.profileSeTarget + ")")
                        map
                    } else emptyMap()
                    val request = BenchmarkRequest(
                        models = modelSources,
                        queryLimit = cliConfig.queryLimit,
                        category = cliConfig.category,
                        confidenceGate = cliConfig.confidenceGate,
                        parallelism = cliConfig.parallelism,
                        questionsPerRound = cliConfig.questionsPerRound,
                        updateRankings = true,
                        poolId = if (cliConfig.reservedOnly) {
                            ownPoolId ?: snapshotManager.lastLoadedReservedPoolId
                                ?: error("[POOL-PIN] no pool: build or load a snapshot before judging $condition")
                        } else null,
                        condition = condition,
                        seed = currentSeed,
                        profileSeTarget = if (cliConfig.profileMode) cliConfig.profileSeTarget else null,
                        profileStrata = profileStrata,
                        maxQueryReuse = cliConfig.maxQueryReuse,
                        matchFilter = cliConfig.matchFilter
                    )

                    // [POOL-PIN] A judged run must score exactly the pool its snapshot was built
                    // against, and says so by id: construction runs own their split, snapshot runs
                    // carry the pool loadSnapshot pinned, and the declared `pool` (when set) must
                    // agree. There is no active pool that another JVM could switch (FRAMEWORK
                    // item 18). TRAIN-only: a snapshot whose tree holds EVAL texts is refused
                    // unless the exact count is acknowledged, and then disclosed.
                    run {
                        val verdict = taxonomy.model.PoolPin.decide(
                            condition = condition,
                            requestPool = request.poolId,
                            snapshotRun = !cliConfig.runPipeline && cliConfig.unionSnapshots.isEmpty(),
                            pinnedPool = snapshotManager.lastLoadedReservedPoolId,
                            evalMembersKnown = snapshotManager.lastLoadedEvalMembersKnown,
                            evalMembers = snapshotManager.lastLoadedEvalMembersInTree,
                            acknowledged = cliConfig.acknowledgedEvalMembers,
                            snapshotId = baseSnapshotId,
                            declaredPool = cliConfig.pool
                        )
                        log.info("[POOL-PIN] judging $condition on reserved pool ${verdict.poolId ?: "NONE (unrestricted)"}")
                        // Printed directly under the [SCORED-EVAL] lines' section: the benchmark service
                        // logs those two lines first; the disclosure is the run's own admission.
                        verdict.disclosure?.let { log.warn(it) }
                    }
                    val report = benchmarkService.runBenchmark(request)
                    reportsByCondition[condition] = report
                    val logicalComparisons = report.queryResults.size
                    val judgeApiCalls = report.queryResults.count { it.hadJudge } * 2
                    logicalComparisonsMap[condition] = logicalComparisons
                    judgeApiCallsMap[condition] = judgeApiCalls

                    log.info("Condition $condition completed. Overall Agreement Rate: ${report.overallJudgeAccuracyAgreement}")
                    log.info("  - Logical Comparisons: $logicalComparisons")
                    log.info("  - LLM Judge API Calls: $judgeApiCalls")

                    // Export results
                    exportValidationMetrics(validationDir, condition, report)
                    exportMatchFilterSummary(validationDir, condition, report)
                    exportLeafLeaderboard(validationDir, condition, suffixedSnapshotId, activeRoot, cliConfig.models)
                    exportDomainStats(validationDir, condition, report)
                    exportVerdicts(judgingDir, condition, report)
                    ReportGenerator.generateAndExport(validationDir, condition, report, activeRoot, cliConfig.models)

                    // Compute and export LaTeX table for the global leaderboard
                    val leafIds = mutableListOf<String>()
                    val visited = mutableSetOf<String>()
                    fun walk(n: GraphNode) {
                        if (!visited.add(n.id)) return
                        if (n.children.isEmpty()) leafIds.add(n.id)
                        else n.children.forEach { walk(it) }
                    }
                    walk(activeRoot)
                    val globalLeaderboard = rankingService.aggregateLeafScores(leafIds, suffixedSnapshotId)
                    exportLatexTable(validationDir, condition, globalLeaderboard.ranks)

                    // Save backup of the full JSON benchmark report
                    val backupDir = File("benchmark_backups")
                    if (!backupDir.exists()) {
                        backupDir.mkdirs()
                    }
                    val timestamp = java.text.SimpleDateFormat("yyyyMMdd_HHmmss").format(java.util.Date())
                    val backupFile = File(backupDir, "benchmark_${suffixedSnapshotId}_$timestamp.json")
                    try {
                        val jsonString = json.encodeToString(report)
                        backupFile.writeText(jsonString)
                        log.info("Saved benchmark report backup to ${backupFile.absolutePath}")
                    } catch (e: Exception) {
                        log.error("Failed to backup benchmark report: ${e.message}", e)
                    }

                    completedConditions.add(condition)
                }

                // Write Experiment Manifest
                val manifestFile = File(baseDir, "manifest.json")
                val manifest = ExperimentManifest(
                    runId = "run_" + Instant.now().toString().replace(":", "-"),
                    snapshotId = snapshotId,
                    models = cliConfig.models,
                    seed = currentSeed,
                    testRatio = cliConfig.testRatio,
                    conditionsRun = completedConditions,
                    runTimestamp = Instant.now().toString(),
                    logicalComparisons = logicalComparisonsMap,
                    llmJudgeApiCalls = judgeApiCallsMap
                )
                manifestFile.writeText(json.encodeToString(manifest))
                log.info("Experiment manifest written to ${manifestFile.absolutePath}")
            }

            // 5. Run trickle validation if enabled
            if (cliConfig.runTrickle) {
                val baseSnapshotId = snapshotId.substringBefore("_MAIN").substringBefore("_ORACLE").substringBefore("_C3").substringBefore("_C5").substringBefore("_GENERIC_JUDGE").substringBefore("_RANDOM_SCHEDULER").substringBefore("_KMEANS_BASELINE").substringBefore("_WARD_BASELINE").substringBefore("_RANDOMNULL_BASELINE")

                // Hoist dataset fetch and reserved pool resolution above the validation loop
                val hoistedReservedFile = File("reserved_test_queries.json")
                val hoistedReservedByDomain: Map<String, List<Int>>? = if (hoistedReservedFile.exists()) {
                    try {
                        json.decodeFromString(hoistedReservedFile.readText())
                    } catch (_: Throwable) { null }
                } else null

                val hoistedTargetDomains = if (cliConfig.domains.isNotEmpty()) cliConfig.domains else (cliConfig.category?.let { listOf(it) } ?: emptyList())
                // Whole corpus, not the fetcher's 12,000-row default: that cap was invisible on the
                // v2 cache (exactly 12,000 rows) but on the multi-corpus DB it dropped the 32
                // highest-id MMLU-Pro rows (12,032), so their held-out members silently left the
                // trickle pool (mc6_s42, 2026-09-11). The construction fetch above uses this bound.
                val hoistedFullByDomain = try {
                    datasetFetcher.fetchDataset(
                        maxQueries = cliConfig.queryLimit.takeIf { it > 0 } ?: Int.MAX_VALUE,
                        selectedDomains = emptyList()
                    )
                } catch (_: Throwable) { null }

                log.info("========================================")
                log.info("RUNNING TRICKLE VALIDATION: MAIN")
                log.info("========================================")
                taxonomyService.setGraph(root)
                val mainCorrect = runHeadlessTrickle(root, "MAIN", cliConfig, baseDir, currentSeed, reportsByCondition["MAIN"], hoistedFullByDomain, hoistedReservedByDomain)
                if (cliConfig.unionSnapshots.isNotEmpty()) {
                    exportUnionRouting(File(baseDir, "validation"), root, currentSeed, hoistedFullByDomain, hoistedReservedByDomain,
                        taxonomy.service.UnionRouting.Rule.parse(cliConfig.unionRootRouting), cliConfig.unionRoutingItemKey)
                }

                if (cliConfig.runBaselines) {
                    var kmeansCorrect: Map<String, Boolean>? = null
                    val kmeansSnapshot = "${baseSnapshotId}_baseline_kmeans"
                    snapshotManager.loadSnapshot(kmeansSnapshot)?.let { kmeansRoot ->
                        log.info("========================================")
                        log.info("RUNNING TRICKLE VALIDATION: KMEANS_BASELINE")
                        log.info("========================================")
                        taxonomyService.setGraph(kmeansRoot)
                        kmeansCorrect = runHeadlessTrickle(kmeansRoot, "KMEANS_BASELINE", cliConfig, baseDir, currentSeed, reportsByCondition["KMEANS_BASELINE"], hoistedFullByDomain, hoistedReservedByDomain)
                    }

                    var wardCorrect: Map<String, Boolean>? = null
                    val wardSnapshot = "${baseSnapshotId}_baseline_ward"
                    snapshotManager.loadSnapshot(wardSnapshot)?.let { wardRoot ->
                        log.info("========================================")
                        log.info("RUNNING TRICKLE VALIDATION: WARD_BASELINE")
                        log.info("========================================")
                        taxonomyService.setGraph(wardRoot)
                        wardCorrect = runHeadlessTrickle(wardRoot, "WARD_BASELINE", cliConfig, baseDir, currentSeed, reportsByCondition["WARD_BASELINE"], hoistedFullByDomain, hoistedReservedByDomain)
                    }

                    var randomNullCorrect: Map<String, Boolean>? = null
                    val randomNullSnapshot = "${baseSnapshotId}_baseline_randomnull"
                    snapshotManager.loadSnapshot(randomNullSnapshot)?.let { randomNullRoot ->
                        log.info("========================================")
                        log.info("RUNNING TRICKLE VALIDATION: RANDOMNULL_BASELINE")
                        log.info("========================================")
                        taxonomyService.setGraph(randomNullRoot)
                        randomNullCorrect = runHeadlessTrickle(randomNullRoot, "RANDOMNULL_BASELINE", cliConfig, baseDir, currentSeed, reportsByCondition["RANDOMNULL_BASELINE"], hoistedFullByDomain, hoistedReservedByDomain)
                    }

                    // McNemar significance comparisons between MAIN and the baselines
                    try {
                        val mcnemarFile = File(validationDir, "mcnemar_significance_results.csv")
                        mcnemarFile.bufferedWriter().use { writer ->
                            writer.write("Baseline,BothCorrect,MainCorrectBaselineIncorrect,BaselineCorrectMainIncorrect,BothIncorrect,ChiSquared,PValue\n")
                            
                            fun checkMcNemar(baselineName: String, baselineCorrect: Map<String, Boolean>?) {
                                if (baselineCorrect == null) return
                                var bothCorrect = 0
                                var mainCorrectBaselineIncorrect = 0
                                var baselineCorrectMainIncorrect = 0
                                var bothIncorrect = 0
                                
                                for ((q, correctMain) in mainCorrect) {
                                    val correctBase = baselineCorrect[q] ?: false
                                    if (correctMain && correctBase) bothCorrect++
                                    else if (correctMain && !correctBase) mainCorrectBaselineIncorrect++
                                    else if (!correctMain && correctBase) baselineCorrectMainIncorrect++
                                    else bothIncorrect++
                                }
                                val discordant = mainCorrectBaselineIncorrect + baselineCorrectMainIncorrect
                                val chiSquared = if (discordant > 0) {
                                    val diff = kotlin.math.abs(mainCorrectBaselineIncorrect - baselineCorrectMainIncorrect).toDouble()
                                    val correctedDiff = (diff - 1.0).coerceAtLeast(0.0)
                                    (correctedDiff * correctedDiff) / discordant.toDouble()
                                } else 0.0
                                val pVal = ValidationService.chiSquaredToPValue(chiSquared)
                                writer.write("$baselineName,$bothCorrect,$mainCorrectBaselineIncorrect,$baselineCorrectMainIncorrect,$bothIncorrect,$chiSquared,$pVal\n")
                                
                                log.info("McNemar Significance (MAIN vs $baselineName):")
                                log.info("  - Chi-Squared: ${"%,.4f".format(chiSquared)}")
                                log.info("  - p-value: ${"%.4e".format(pVal)}")
                            }
                            
                            checkMcNemar("KMEANS_BASELINE", kmeansCorrect)
                            checkMcNemar("WARD_BASELINE", wardCorrect)
                            checkMcNemar("RANDOMNULL_BASELINE", randomNullCorrect)
                        }
                        log.info("McNemar significance results written to ${mcnemarFile.absolutePath}")
                    } catch (e: Exception) {
                        log.error("Failed to run McNemar significance tests: ${e.message}", e)
                    }
                }

                // Restore active root graph for downstream benchmark
                taxonomyService.setGraph(root)
            }
            
            // Print and Save Performance Report
            if (config.diagnostics.enableProfiling) {
                val perfReportFile = File(baseDir, "performance_report.json")
                perfTracker.exportJsonReport(perfReportFile)
                log.info("Performance report JSON written to ${perfReportFile.absolutePath}")
                val printedReport = perfTracker.printReport()
                log.info(printedReport)
            }
            } finally {
                // Order matters: stop the appender FIRST so the log is flushed and closed, then
                // close the bundle, which is what performs the copies. Copying a log still held
                // open by the appender loses the tail, and the tail is the convergence record.
                try {
                    stopFileLogging(seedAppender)
                } catch (e: Exception) {
                    log.error("Failed to stop seed file logging: ${e.message}")
                }
                taxonomy.diagnostics.DiagnosticsBundle.close("completed")
            }
        }
    }


    /**
     * Multi-corpus stage 1b — FEDERATED assembly (docs/multi_corpus_design.md, "Stage 1
     * certification result … design adjustment"). Each corpus was built alone (its own loop,
     * split and site null); here their snapshots are re-keyed (`<SOURCE>:` id prefix, depth + 1),
     * hydrated from the embeddings cache and grafted under a new union root — nothing beneath a
     * per-corpus root is refitted, so per-corpus certification carries over by construction.
     *
     * What the union adds is routing state at the new root (its vMF from the engine's own
     * single-node fit on the grafted region, the Jensen shrinkage, query ids) and ONE reserved
     * pool: the union of the members' pools, recorded and activated on the corpus DB exactly as
     * a construction run records its split, so the saved snapshot pins it ([POOL-PIN]).
     */
    /** A grafted union: its root, the saved snapshot id, and the union reserved pool it was pinned to. */
    private data class AssembledUnion(val root: GraphNode, val snapshotId: String, val poolId: String)

    private suspend fun assembleUnion(cliConfig: HeadlessCliConfig, currentSeed: Long, configFile: File? = null): AssembledUnion {
        val sources = cliConfig.corpora
            ?: throw IllegalStateException("[UNION] unionSnapshots needs corpora = [...] naming the union's members")
        log.info("[UNION] assembling ${cliConfig.unionSnapshots.size} per-corpus snapshot(s) under a union root: ${cliConfig.unionSnapshots}")

        class Member(val snapshotId: String, val source: String, val graph: taxonomy.service.SerializedGraph, val pool: Map<String, List<Int>>)
        val members = cliConfig.unionSnapshots.map { sid ->
            val graph = snapshotManager.readSerializedGraph(sid)
                ?: throw IllegalStateException("[UNION] snapshot '$sid' is not in snapshots.db")
            val rootNode = graph.nodes.firstOrNull { it.id == graph.rootId }
                ?: throw IllegalStateException("[UNION] snapshot '$sid' has no root node '${graph.rootId}'")
            val source = rootNode.label?.takeIf { it.isNotBlank() }
                ?: throw IllegalStateException("[UNION] snapshot '$sid': root has no label (a per-corpus build labels it with the corpus name)")
            check(source in sources) { "[UNION] snapshot '$sid' is a '$source' build, not one of corpora = $sources" }
            check(rootNode.depth == 0) { "[UNION] snapshot '$sid': root '$source' is at depth ${rootNode.depth}, expected 0" }
            val pool = snapshotManager.readReservedQueries(sid)
            check(!pool.isNullOrEmpty()) { "[UNION] snapshot '$sid' ($source) carries no reserved pool — a union member must own its split" }
            Member(sid, source, graph, pool)
        }
        val bySource = members.groupBy { it.source }
        check(bySource.values.all { it.size == 1 }) {
            "[UNION] more than one snapshot per corpus: ${bySource.filterValues { it.size > 1 }.mapValues { (_, v) -> v.map { it.snapshotId } }}"
        }
        check(bySource.keys == sources.toSet()) { "[UNION] corpora = $sources but the snapshots cover ${bySource.keys}" }
        // Config order = child order under the union root: deterministic, and what the label says.
        val ordered = sources.map { bySource.getValue(it).single() }

        // 1. Graph: re-key, hydrate, graft.
        val roots = ordered.map { m ->
            val rekeyed = UnionGraft.rekey(m.graph, m.source, depthShift = 1)
            val r = persistence.loadFromSerialized(rekeyed)
                ?: throw IllegalStateException("[UNION] could not hydrate snapshot '${m.snapshotId}' (${m.source})")
            check(r.id == UnionGraft.prefixedId(m.source, m.graph.rootId)) { "[UNION] ${m.source}: hydrated root id '${r.id}' is not the re-keyed root" }
            val hydrated = UnionGraft.nodes(r)
            check(hydrated.size == m.graph.nodes.size) { "[UNION] ${m.source}: hydrated ${hydrated.size} nodes, snapshot has ${m.graph.nodes.size}" }
            val leaves = hydrated.count { it.isLeaf }
            val queries = hydrated.sumOf { it.queries.size }
            log.info("[UNION] ${m.source}: snapshot ${m.snapshotId}, ${hydrated.size} nodes ($leaves leaves, $queries query slots)," +
                " reserved ${m.pool.values.sumOf { it.size }} ids in ${m.pool.size} domain(s), pool ${UnionGraft.poolId(m.pool)}")
            r
        }
        val label = sources.joinToString("+")
        val unionRoot = UnionGraft.graft(label, roots)

        // 2. Routing state at the new root. Hydration does not populate the embedding registry the
        // fitter reads, so register the grafted region first; then the engine's own single-node
        // fit (what the bootstrap gives a root), the descent-gate shrinkages, and query ids as
        // loadSnapshot assigns them. No grafted node is refitted.
        var registered = 0
        for (n in UnionGraft.nodes(unionRoot)) for (q in n.queries) { GraphNode.registerEmbedding(q); registered++ }
        ops.fitSingleNode(unionRoot)
        check(unionRoot.vmfMu.isNotEmpty() && unionRoot.vmfMu.size == taxonomy.model.EmbeddingSlice.width) {
            "[UNION] root vMF not fitted (dim ${unionRoot.vmfMu.size}, expected ${taxonomy.model.EmbeddingSlice.width})"
        }
        unionRoot.updateAllShrinkages()
        taxonomy.model.assignQueryIds(unionRoot, config.formalism.enableStableQuestionIds)
        val unionNodes = UnionGraft.nodes(unionRoot)
        log.info("[UNION] root '$label': ${unionRoot.children.size} corpus roots, ${unionNodes.size} nodes, ${unionNodes.count { it.isLeaf }} leaves;" +
            " root vMF fitted on $registered region embeddings (kappa=${"%.2f".format(java.util.Locale.US, unionRoot.vmfKappa)}," +
            " child-centroid shrinkage=${"%.4f".format(java.util.Locale.US, unionRoot.childCentroidShrinkage)})")

        // 3. Reserved pool = union of the members' pools, recorded on the corpus DB (never activated).
        val unionPool = UnionGraft.unionReservedPools(ordered.associate { it.source to it.pool })
        val expectedPoolId = UnionGraft.poolId(unionPool)
        File("reserved_test_queries.json").writeText(json.encodeToString(unionPool))
        val judgeableUnion = unionPool.mapValues { (_, ids) -> ids.filter { it > 0 } }.filterValues { it.isNotEmpty() }
        val recorded = evalStore.recordReservedPool(judgeableUnion, dataset = label, corpusSize = null, seed = null, testRatio = null)
        check(recorded == expectedPoolId) { "[POOL-PIN] union pool $expectedPoolId expected, recorded $recorded" }
        // RP12 B2 (READY_rp12_et C-0): a v2 graft's declared pool is the v2 pool id (the id-list union pool is recorded
        // beside it and is not in the p-pool registry); a legacy graft keeps the registry check.
        val v2Union = cliConfig.v2PoolFile?.let { taxonomy.dataset.V2EnginePool.load(File(it)) }
        if (cliConfig.pool != null) {
            if (v2Union != null) {
                check(v2Union.poolId == cliConfig.pool) { "[POOL-PIN] v2 union pool ${v2Union.poolId} != declared pool ${cliConfig.pool}; refusing" }
            } else {
                check(expectedPoolId == cliConfig.pool) { "[POOL-PIN] union pool $expectedPoolId != declared pool ${cliConfig.pool}; refusing" }
                val entry = taxonomy.dataset.ReservedPoolRegistry.resolve(cliConfig.pool)
                check(entry.corpus_set.toSet() == sources.toSet()) { "[POOL-PIN] registry corpus set ${entry.corpus_set} != corpora $sources for ${cliConfig.pool}" }
            }
        }
        log.info("[POOL-PIN] union reserved pool $expectedPoolId (${unionPool.values.sumOf { it.size }} ids across ${unionPool.size} domains)" +
            " = union of ${ordered.joinToString(", ") { "${it.source}:${UnionGraft.poolId(it.pool)}" }}; recorded, nothing activated")
        // RP12 B2: a v2 graft checks every member against the pool file and installs the global keys
        // before the guard below; absent = nothing here runs.
        val v2UnionStamp = v2Union?.let { p ->
            val (lines, st) = p.activateUnion(ordered.map { m ->
                taxonomy.dataset.V2EnginePool.UnionMember(m.snapshotId, m.source, snapshotManager.readBuildStamp(m.snapshotId),
                    m.pool.values.flatten().toSet())
            }, expectedPoolId, unionNodes.filter { it.isLeaf }.sumOf { it.queries.size }, unionPool, currentSeed, configFile,
                taxonomy.dataset.V2ForeignMembers.parseForeign(cliConfig.v2ForeignMembers))
            lines.forEach { log.warn(it) }
            st
        }
        // TRAIN-only, by content, against the union pool's texts (plus the global reserved keys of a v2 graft). FATAL.
        run {
            val report = taxonomy.model.TrainOnlyGuard.evalMembers(unionRoot, taxonomy.model.TrainOnlyGuard.withGlobal(taxonomy.model.TrainOnlyGuard.keysOf(evalStore.getReservedQuestionTexts(expectedPoolId))))
            taxonomy.model.TrainOnlyGuard.assertNone(report, "after union graft")
            log.info("[TRAIN-ONLY] after union graft: 0 EVAL texts among the grafted tree's members")
        }

        // 4. Snapshot, pinned to the union pool.
        val snapshot = snapshotManager.saveSnapshot(unionRoot, "Union graft of ${ordered.size} corpora", expectedPoolId = expectedPoolId, buildStamp = v2UnionStamp)
        v2UnionStamp?.let { taxonomy.diagnostics.DiagnosticsBundle.recordSplitV2(it.toManifest()) }
        log.info("Successfully assembled and saved union snapshot. Snapshot ID: ${snapshot.id}")
        taxonomy.diagnostics.DiagnosticsBundle.recordCorpus(
            seed = currentSeed, splitSeed = cliConfig.splitSeed,
            corpusSize = -1, trainSize = unionNodes.filter { it.isLeaf }.sumOf { it.queries.size },
            testSize = unionPool.values.sumOf { it.size },
            domains = sources, reservedPoolId = expectedPoolId,
            embeddingModel = config.llm.embeddingModel, judgeModel = config.llm.judgeModel
        )
        return AssembledUnion(unionRoot, snapshot.id, expectedPoolId)
    }

    /**
     * Union readout (stage 1b): for every held-out query, the routed leaf's depth-1 ancestor is
     * a corpus root and its depth-2 ancestor a designed (source, domain) anchor, so the union's
     * value as a routing layer is measured directly — routed source vs true source, routed anchor
     * vs designed domain — next to the standard profile-based Top-1, per source and overall.
     * Ancestry follows tree edges from the union root (first discovery, children by id).
     *
     * Stage 1c: [rule] selects the union ROOT step ([taxonomy.service.UnionRouting]). DESCENT is
     * the production trickle from the union root exactly as in stage 1b; FLAT_LEAF and
     * SOURCE_GATE read the held-out embeddings from the cache (never the embedding model) and
     * for SOURCE_GATE the production descent runs from the chosen corpus root. Source accuracy
     * under SOURCE_GATE is the gate's own pick, so it is reported even where the in-corpus
     * descent then stops above every leaf (counted unrouted for Top-1 and domain).
     */
    private fun exportUnionRouting(
        validationDir: File,
        root: GraphNode,
        currentSeed: Long,
        fullByDomain: Map<String, List<taxonomy.dataset.MMLUQuery>>?,
        reservedByDomain: Map<String, List<Int>>?,
        rule: taxonomy.service.UnionRouting.Rule = taxonomy.service.UnionRouting.Rule.DESCENT,
        itemKey: Boolean = false
    ) = runBlocking {
        if (itemKey) {
            log.warn("[UNION-ROUTING] RP12 B3: item-keyed readout (item_id column; TRAIN routing and leaf table written beside)")
            taxonomy.diagnostics.DiagnosticsBundle.recordUnionRoutingItemKey()
        }
        if (fullByDomain == null || reservedByDomain == null) {
            log.warn("[UNION-ROUTING] corpus or reserved pool unavailable; skipping the per-source readout"); return@runBlocking
        }
        val leaves = taxonomy.tui.service.BatchTrickleEvaluator.collectLeaves(root)
        // Leaf profiles over the DESIGNED (source, domain) keys of the corpus DB — the truth this
        // readout is defined against — with the rehydrated query category only as a fallback.
        // The query cache (embeddings_cache.db `queries`) is keyed by text and shared by every
        // corpus that holds that text: an MMLU_PRO run rewrites the MMLU_PRO_LB categories to
        // their bare form ("Physics"), which silently zeroed MMLU_PRO_LB Top-1 in a union run
        // (2026-09-11 14:35, stage 1c) although stage 1b had read 59.5% from the same graft.
        val textToDomain = HashMap<String, String>()
        for (leaf in leaves) for (emb in leaf.queries) emb.groundTruthCategory?.takeIf { it.isNotBlank() }?.let { textToDomain[emb.rawText] = it }
        var relabelled = 0
        for ((domainKey, queries) in fullByDomain) for (q in queries) {
            val prev = textToDomain.put(q.text, domainKey)
            if (prev != null && prev != domainKey) relabelled++
        }
        if (relabelled > 0) log.warn("[UNION-ROUTING] $relabelled leaf query categories disagreed with the corpus DB's designed key and were overridden (shared text-keyed query cache)")
        val profiles = taxonomy.tui.service.BatchTrickleEvaluator.buildLeafProfiles(leaves, textToDomain)

        val treeParent = taxonomy.service.UnionRouting.treeParents(root)
        fun ancestorAt(n: GraphNode?, depth: Int): GraphNode? = taxonomy.service.UnionRouting.ancestorAt(n, depth, treeParent)

        val idToText = fullByDomain.values.flatten().associate { it.id to it.text }
        val testQueries = reservedByDomain
            .flatMap { (domain, ids) -> ids.mapNotNull { id -> idToText[id]?.let { text -> domain to text } } }
            .shuffled(java.util.Random(currentSeed))

        // Cache-only embeddings for the non-descent rules (the trickle above has already routed
        // every held-out text, so every vector is on disk); a miss is counted as unrouted.
        val cached: Map<String, FloatArray> = if (rule == taxonomy.service.UnionRouting.Rule.DESCENT) emptyMap()
            else embeddingCache.getBatch(testQueries.map { it.second }.toSet())
        if (rule != taxonomy.service.UnionRouting.Rule.DESCENT) root.updateAllShrinkages()
        var cacheMisses = 0
        /** Production descent from [start] (the trickler, inference options), top leaf or null. */
        fun descendFrom(start: GraphNode, emb: Embedding): GraphNode? =
            ops.routeQuery(emb, start, isInference = true).entries
                .filter { it.key.isLeaf }
                .map { it.key to kotlin.math.exp(it.value).coerceIn(0.0, 1.0) }
                .sortedByDescending { it.second }
                .firstOrNull()?.first

        class Acc { var n = 0; var unrouted = 0; var top1 = 0; var source = 0; var domain = 0 }
        val perSource = java.util.TreeMap<String, Acc>()
        val all = Acc()
        val flow = java.util.TreeMap<String, java.util.TreeMap<String, Int>>()
        val unroutedKey = "<unrouted>"
        validationDir.mkdirs()
        val perQuery = File(validationDir, "MAIN_union_routing_queries.csv").bufferedWriter()
        perQuery.write(taxonomy.service.UnionRoutingExport.header(itemKey))
        /** One text through [rule] (the stage 1b / 1c paths verbatim); a cache miss counts in [misses]. */
        suspend fun routeOne(text: String, vectors: Map<String, FloatArray>, misses: IntArray): taxonomy.service.UnionRouting.Routed =
            if (rule == taxonomy.service.UnionRouting.Rule.DESCENT) {
                // Stage 1b path, verbatim: the service's own descent from the active (union) root.
                val top = try { taxonomyService.routeQueryToLeaves(text).firstOrNull()?.first } catch (t: Throwable) { null }
                taxonomy.service.UnionRouting.Routed(top, ancestorAt(top, 1))
            } else {
                val vec = vectors[text]
                if (vec == null) { misses[0]++; taxonomy.service.UnionRouting.Routed(null, null) }
                else {
                    val emb = Embedding(text, text, vec)
                    try {
                        taxonomy.service.UnionRouting.route(rule, emb, root, leaves, treeParent) { start -> descendFrom(start, emb) }
                    } catch (t: Throwable) { taxonomy.service.UnionRouting.Routed(null, null) }
                }
            }
        val missBox = IntArray(1)
        for ((domainKey, text) in testQueries) {
            val trueSource = CorpusDomains.sourceOfKey(domainKey) ?: domainKey
            val acc = perSource.getOrPut(trueSource) { Acc() }
            val row = flow.getOrPut(trueSource) { java.util.TreeMap() }
            acc.n++; all.n++
            val routed: taxonomy.service.UnionRouting.Routed = routeOne(text, cached, missBox)
            val routedSource = routed.source?.label
            val sourceOk = routedSource != null && routedSource == trueSource
            if (sourceOk) { acc.source++; all.source++ }
            val top = routed.leaf
            if (top == null) {
                acc.unrouted++; all.unrouted++; row.merge(routedSource ?: unroutedKey, 1, Int::plus)
                perQuery.write(taxonomy.service.UnionRoutingExport.row(domainKey, trueSource, rule.key, null, null, null, null, null,
                    routedSource, null, false, sourceOk, false, text, itemKey))
                continue
            }
            val routedDomain = ancestorAt(top, 2)?.label
            row.merge(routedSource ?: "?", 1, Int::plus)
            val profile = profiles[top.id]
            val top1Ok = profile?.dominantDomain == domainKey
            val domainOk = routedDomain == domainKey
            if (top1Ok) { acc.top1++; all.top1++ }
            if (domainOk) { acc.domain++; all.domain++ }
            perQuery.write(taxonomy.service.UnionRoutingExport.row(domainKey, trueSource, rule.key, top.id, top.label, top.depth,
                profile?.dominantDomain, profile?.purity, routedSource, routedDomain, top1Ok, sourceOk, domainOk, text, itemKey))
        }
        perQuery.close()
        cacheMisses += missBox[0]
        if (itemKey) {
            // RP12 B3: every TRAIN text of the loaded corpora through the same rule (G14's TRAIN tree cells; G13's comparator
            // fits on TRAIN), and the leaf table (G13's k_c). Aggregates above are untouched.
            val trainQueries = taxonomy.service.UnionRoutingExport.trainQueries(fullByDomain, reservedByDomain)
            val trainVectors: Map<String, FloatArray> = if (rule == taxonomy.service.UnionRouting.Rule.DESCENT) emptyMap()
                else embeddingCache.getBatch(trainQueries.map { it.second }.toSet())
            val trainMiss = IntArray(1)
            File(validationDir, taxonomy.service.UnionRoutingExport.TRAIN_FILE).bufferedWriter().use { w ->
                w.write(taxonomy.service.UnionRoutingExport.header(true))
                for ((domainKey, text) in trainQueries) {
                    val trueSource = CorpusDomains.sourceOfKey(domainKey) ?: domainKey
                    val routed = routeOne(text, trainVectors, trainMiss)
                    val routedSource = routed.source?.label
                    val sourceOk = routedSource != null && routedSource == trueSource
                    val top = routed.leaf
                    if (top == null) {
                        w.write(taxonomy.service.UnionRoutingExport.row(domainKey, trueSource, rule.key, null, null, null, null, null,
                            routedSource, null, false, sourceOk, false, text, true))
                        continue
                    }
                    val routedDomain = ancestorAt(top, 2)?.label
                    val profile = profiles[top.id]
                    w.write(taxonomy.service.UnionRoutingExport.row(domainKey, trueSource, rule.key, top.id, top.label, top.depth,
                        profile?.dominantDomain, profile?.purity, routedSource, routedDomain, profile?.dominantDomain == domainKey,
                        sourceOk, routedDomain == domainKey, text, true))
                }
            }
            File(validationDir, taxonomy.service.UnionRoutingExport.LEAVES_FILE).writeText(
                taxonomy.service.UnionRoutingExport.leavesCsv(leaves.map { Triple(it.id, it.label, it.depth) }, profiles))
            log.warn("[UNION-ROUTING] item-keyed: ${trainQueries.size} TRAIN text(s) routed (${trainMiss[0]} cache miss(es), unrouted);" +
                " ${leaves.size} leaves written")
        }
        if (cacheMisses > 0) log.warn("[UNION-ROUTING] $cacheMisses held-out text(s) had no cached embedding and were counted unrouted")

        fun pct(k: Int, n: Int) = if (n > 0) k.toDouble() / n else Double.NaN
        val (wLo, wHi) = taxonomy.service.UnionRouting.wilson(all.top1, all.n)
        val sb = StringBuilder()
        sb.appendLine("[UNION-ROUTING] held-out routing on the union (rule=${rule.key}; n=${all.n}; top1 = profile-based Top-1, source = routed depth-1 corpus root == true source, domain = routed depth-2 anchor == designed domain)")
        sb.appendLine("%-14s %6s %8s %8s %8s %8s".format("source", "n", "unrouted", "top1", "source", "domain"))
        fun line(name: String, a: Acc) = "%-14s %6d %8d %7.2f%% %7.2f%% %7.2f%%".format(java.util.Locale.US, name, a.n, a.unrouted, pct(a.top1, a.n) * 100, pct(a.source, a.n) * 100, pct(a.domain, a.n) * 100)
        for ((src, a) in perSource) sb.appendLine(line(src, a))
        sb.appendLine(line("ALL", all))
        sb.appendLine("union Top-1 %.2f%% [%.2f, %.2f] (95%% Wilson, n=%d)".format(java.util.Locale.US, pct(all.top1, all.n) * 100, wLo * 100, wHi * 100, all.n))
        log.info(sb.toString())

        validationDir.mkdirs()
        File(validationDir, "MAIN_union_routing_summary.txt").bufferedWriter().use { w ->
            w.write("rule=${rule.key}\n")
            w.write("n=${all.n}\nunrouted=${all.unrouted}\n")
            w.write("top1=${pct(all.top1, all.n)}\ntop1_wilson_low=$wLo\ntop1_wilson_high=$wHi\n")
            w.write("source_accuracy=${pct(all.source, all.n)}\ndomain_accuracy=${pct(all.domain, all.n)}\n")
        }
        File(validationDir, "MAIN_union_routing.csv").bufferedWriter().use { w ->
            w.write("source,n,unrouted,top1_accuracy,source_accuracy,domain_accuracy\n")
            for ((src, a) in perSource) w.write("${escapeCsv(src)},${a.n},${a.unrouted},${pct(a.top1, a.n)},${pct(a.source, a.n)},${pct(a.domain, a.n)}\n")
            w.write("ALL,${all.n},${all.unrouted},${pct(all.top1, all.n)},${pct(all.source, all.n)},${pct(all.domain, all.n)}\n")
        }
        val routedCols = (flow.values.flatMap { it.keys } - unroutedKey).toSortedSet().toList() + unroutedKey
        File(validationDir, "MAIN_union_source_flow.csv").bufferedWriter().use { w ->
            w.write("true_source," + routedCols.joinToString(",") { escapeCsv(it) } + "\n")
            for ((src, row) in flow) w.write(escapeCsv(src) + "," + routedCols.joinToString(",") { (row[it] ?: 0).toString() } + "\n")
        }
        log.info("[UNION-ROUTING] per-source readout written to ${File(validationDir, "MAIN_union_routing.csv").absolutePath}")
    }

    private fun runHeadlessTrickle(
        root: GraphNode, 
        condition: String, 
        cliConfig: HeadlessCliConfig, 
        baseDir: File,
        currentSeed: Long,
        benchmarkReport: BenchmarkReport? = null,
        hoistedFullByDomain: Map<String, List<taxonomy.dataset.MMLUQuery>>? = null,
        hoistedReservedByDomain: Map<String, List<Int>>? = null
    ): Map<String, Boolean> = runBlocking {
        val startVal = System.currentTimeMillis()
        log.info("Starting Headless Batch Trickle Validation for $condition...")

        val validationDir = File(baseDir, "validation")
        validationDir.mkdirs()
        try {
            exportGraphValidity(validationDir, root, condition)
            exportTaxonomyQuality(validationDir, root, condition)
            exportBridgeQuality(validationDir, root, condition)
        } catch (e: Exception) {
            log.error("Failed to export structural/quality metrics for $condition: ${e.message}", e)
        }

        val reservedByDomain: Map<String, List<Int>> = hoistedReservedByDomain ?: run {
            val reservedFile = File("reserved_test_queries.json")
            if (!reservedFile.exists()) {
                log.warn("reserved_test_queries.json not found — cannot run trickle validation."); return@runBlocking emptyMap()
            }
            try {
                json.decodeFromString(reservedFile.readText())
            } catch (t: Throwable) {
                log.error("Failed to parse reserved set for trickle validation", t); return@runBlocking emptyMap()
            }
        }

        fun cleanText(s: String): String = s.replace("\r\n", "\n").replace("\r", "\n").trim()

        val leaves = taxonomy.tui.service.BatchTrickleEvaluator.collectLeaves(root)
        val textToDomain = HashMap<String, String>()

        var embeddedCount = 0
        for (leaf in leaves) {
            for (emb in leaf.queries) {
                if (!emb.groundTruthCategory.isNullOrBlank()) {
                    textToDomain[emb.rawText] = emb.groundTruthCategory
                    textToDomain[cleanText(emb.rawText)] = emb.groundTruthCategory
                    embeddedCount++
                }
            }
        }
        log.info("Loaded $embeddedCount ground-truth categories directly from DAG queries.")

        val targetDomains = if (cliConfig.domains.isNotEmpty()) cliConfig.domains else (cliConfig.category?.let { listOf(it) } ?: emptyList())
        val fullByDomain = hoistedFullByDomain ?: datasetFetcher.fetchDataset(
            maxQueries = cliConfig.queryLimit.takeIf { it > 0 } ?: Int.MAX_VALUE,
            selectedDomains = emptyList()
        )
        val reservedIds: Set<Int> = reservedByDomain.values.flatten().toSet()
        var databaseCount = 0
        for ((domain, queries) in fullByDomain) {
            for (q in queries) if (q.id !in reservedIds) {
                if (!textToDomain.containsKey(q.text)) {
                    textToDomain[q.text] = domain
                    databaseCount++
                }
                val cleaned = cleanText(q.text)
                if (!textToDomain.containsKey(cleaned)) {
                    textToDomain[cleaned] = domain
                }
            }
        }
        log.info("Backfilled $databaseCount categories from local cache. Total mapping keys: ${textToDomain.size}")

        val profiles = taxonomy.tui.service.BatchTrickleEvaluator.buildLeafProfiles(leaves, textToDomain)
        log.info("Indexed leaves: ${profiles.size} / ${leaves.size} leaves tagged with a domain.")
        if (profiles.isEmpty()) {
            log.warn("No leaves could be tagged — DAG has no labeled training queries. Skipping trickle."); return@runBlocking emptyMap()
        }

        val idToText = fullByDomain.values.flatten().associate { it.id to it.text }
        val poolAll = reservedByDomain
            .flatMap { (domain, ids) ->
                ids.mapNotNull { id ->
                    idToText[id]?.let { text -> domain to text }
                }
            }
            .shuffled(java.util.Random(currentSeed))
        
        val testQueries = poolAll
        if (testQueries.isEmpty()) {
            log.warn("Reserved test set is empty. Skipping trickle."); return@runBlocking emptyMap()
        }

        log.info("Routing ${testQueries.size} test queries...")
        val selected: Set<String> =
            if (cliConfig.domains.isNotEmpty()) cliConfig.domains.toSet()
            else cliConfig.category?.let { setOf(it) } ?: emptySet()
        val anchorCache = HashMap<String, Set<String>>()

        val out = taxonomy.tui.service.BatchTrickleEvaluator.computeBatchTrickleMetrics(
            perLeafDomains = profiles,
            testQueries = testQueries,
            routeFn = { text ->
                val placements = try {
                    runBlocking {
                        taxonomyService.routeQueryToLeaves(text)
                    }
                } catch (t: Throwable) {
                    log.warn("Routing query failed: {}", t.message)
                    emptyList()
                }
                val kept = if (selected.isEmpty()) {
                    placements
                } else {
                    placements.filter { (leaf, _) ->
                        anchorsOf(leaf, anchorCache).any { anchor ->
                            selected.any { it.equals(anchor, ignoreCase = true) }
                        }
                    }
                }
                if (kept.isEmpty() && placements.isNotEmpty()) {
                    listOf("OUT_OF_SCOPE" to -1.0)
                } else {
                    kept.map { (leaf, conf) -> leaf.id to conf }
                }
            }
        )

        log.info("Batch Trickle Results ($condition):")
        log.info("  - Total Queries: ${out.totalQueries}")
        log.info("  - Top-1 Accuracy: ${"%,.2f%%".format(out.top1Accuracy * 100)} (95% Wilson CI: [${"%,.2f%%".format(out.top1WilsonLow * 100)}, ${"%,.2f%%".format(out.top1WilsonHigh * 100)}])")
        log.info("  - Any-Match Accuracy: ${"%,.2f%%".format(out.anyMatchAccuracy * 100)}")
        log.info("  - Mean Leaf Purity: ${"%,.2f%%".format(out.meanLeafPurity * 100)}")
        log.info("  - Expected Calibration Error (ECE): ${"%,.4f".format(out.ece)}")
        log.info("  - Macro F1: ${"%,.2f%%".format(out.macroF1 * 100)}")
        log.info("  - Avg Match Count (Eval): ${"%,.2f".format(out.avgMatchCountEval)} leaves/query")
        log.info("  - Median Nodes/Query (Eval): ${"%,.2f".format(out.medianNodesPerQueryEval)}")
        log.info("Held-out residual rate: ${"%.2f%%".format(java.util.Locale.US, out.heldOutResidualRate * 100)}")

        val tableStr = StringBuilder().apply {
            appendLine("Per-Domain Trickle Results ($condition):")
            appendLine("----------------------------------------------------------------------")
            appendLine("%-25s | %7s | %9s | %8s | %8s".format("Domain", "Support", "Precision", "Recall", "F1"))
            appendLine("----------------------------------------------------------------------")
            out.perDomainF1.entries.sortedByDescending { it.value.support }.forEach { (domain, f1) ->
                appendLine("%-25s | %7d | %8.1f%% | %7.1f%% | %7.1f%%".format(
                    domain.take(25), f1.support, f1.precision * 100, f1.recall * 100, f1.f1 * 100
                ))
            }
            appendLine("======================================================================")
        }.toString()
        log.info("\n$tableStr")

        val trickleDir = File(baseDir, "validation")
        trickleDir.mkdirs()
        val file = File(trickleDir, "${condition}_trickle_validation_results.csv")
        file.bufferedWriter().use { writer ->
            writer.write("Metric,Value\n")
            writer.write("TotalQueries,${out.totalQueries}\n")
            writer.write("Top1Accuracy,${out.top1Accuracy}\n")
            writer.write("Top1WilsonLow,${out.top1WilsonLow}\n")
            writer.write("Top1WilsonHigh,${out.top1WilsonHigh}\n")
            writer.write("AnyMatchAccuracy,${out.anyMatchAccuracy}\n")
            writer.write("MeanLeafPurity,${out.meanLeafPurity}\n")
            writer.write("MeanRoutingDepth,${out.meanRoutingDepth}\n")
            writer.write("MacroF1,${out.macroF1}\n")
            writer.write("NoMatchRate,${out.noMatchRate}\n")
            writer.write("ECE,${out.ece}\n")
            writer.write("AvgMatchCountEval,${out.avgMatchCountEval}\n")
            writer.write("MedianNodesPerQueryEval,${out.medianNodesPerQueryEval}\n")
            writer.write("HeldOutResidualRate,${out.heldOutResidualRate}\n")
        }
        log.info("Trickle validation results written to ${file.absolutePath}")

        // 1. Run Nearest Centroid flat sweep baseline
        try {
            runCentroidRoutingTest(leaves, profiles, testQueries, condition, baseDir)
        } catch (e: Exception) {
            log.error("Failed to run centroid routing test: ${e.message}", e)
        }

        // 2. Compute and export migration flow matrix
        try {
            val domainsList = profiles.values.map { it.dominantDomain }.distinct().sorted()
            val matrix = LinkedHashMap<String, LinkedHashMap<String, Int>>()
            for (trueDomain in testQueries.map { it.first }.distinct().sorted()) {
                val row = LinkedHashMap<String, Int>()
                domainsList.forEach { row[it] = 0 }
                row["Other"] = 0
                matrix[trueDomain] = row
            }

            for ((trueDomain, text) in testQueries) {
                val matched = try {
                    runBlocking {
                        taxonomyService.routeQueryToLeaves(text).mapNotNull { (leaf, conf) ->
                            profiles[leaf.id]?.let { it to conf }
                        }
                    }
                } catch (t: Throwable) {
                    emptyList()
                }
                val row = matrix[trueDomain] ?: continue
                if (matched.isEmpty()) {
                    row["Other"] = (row["Other"] ?: 0) + 1
                } else {
                    val top = matched.maxByOrNull { it.second }!!.first
                    val predicted = top.dominantDomain
                    row[predicted] = (row[predicted] ?: 0) + 1
                }
            }

            val matrixFile = File(trickleDir, "${condition}_migration_flow_matrix.csv")
            matrixFile.bufferedWriter().use { writer ->
                writer.write("TrueDomain," + domainsList.joinToString(",") + ",Other\n")
                for ((trueDomain, row) in matrix) {
                    writer.write(trueDomain + "," + domainsList.map { row[it] ?: 0 }.joinToString(",") + "," + (row["Other"] ?: 0) + "\n")
                }
            }
            log.info("Migration flow matrix written to ${matrixFile.absolutePath}")
        } catch (e: Exception) {
            log.error("Failed to generate migration flow matrix: ${e.message}", e)
        }

        // 3. Compute and export WARD/MAIN diagnostics & build calibration maps in a single loop
        val correctnessMap = HashMap<String, Boolean>()
        val predictedMap = HashMap<String, Map<String, Double>>()
        val gtMap = HashMap<String, String>()
        val matchCounts = mutableListOf<Int>()
        // Per-leaf held-out support: top-1 assignments and any-match appearances.
        val heldOutTop1Counts = HashMap<String, Int>()
        val heldOutAnyCounts = HashMap<String, Int>()
        var diagWriter: java.io.BufferedWriter? = null

        try {
            if (condition.equals("WARD_BASELINE", ignoreCase = true) || condition.equals("MAIN", ignoreCase = true)) {
                val diagFile = File(trickleDir, "${condition}_routing_diagnostics.txt")
                diagWriter = diagFile.bufferedWriter()
                diagWriter.write("=== Per-Query Routing Diagnostics ($condition) ===\n\n")
            }

            for ((trueDomain, text) in testQueries) {
                gtMap[text] = trueDomain
                val matched = try {
                    runBlocking {
                        taxonomyService.routeQueryToLeaves(text).mapNotNull { (leaf, conf) ->
                            profiles[leaf.id]?.let { it to conf }
                        }.sortedByDescending { it.second }
                    }
                } catch (t: Throwable) {
                    emptyList()
                }

                matchCounts.add(matched.size)
                if (matched.isNotEmpty()) {
                    val domainConf = matched.groupBy { it.first.dominantDomain }
                        .mapValues { (_, list) -> list.maxOf { it.second } }
                    predictedMap[text] = domainConf

                    val top1LeafId = matched.first().first.leafId
                    heldOutTop1Counts[top1LeafId] = (heldOutTop1Counts[top1LeafId] ?: 0) + 1
                    matched.map { it.first.leafId }.distinct().forEach { leafId ->
                        heldOutAnyCounts[leafId] = (heldOutAnyCounts[leafId] ?: 0) + 1
                    }
                }

                val isCorrect = if (matched.isEmpty()) {
                    false
                } else {
                    matched.first().first.dominantDomain == trueDomain
                }
                correctnessMap[text] = isCorrect

                diagWriter?.let { writer ->
                    writer.write("Query: \"$text\"\n")
                    writer.write("True Domain: $trueDomain\n")
                    writer.write("Candidate Count: ${matched.size}\n")
                    if (matched.isNotEmpty()) {
                        writer.write("Top-1 Leaf: ${matched.first().first.label} (ID: ${matched.first().first.leafId}) | Dominant: ${matched.first().first.dominantDomain} | Conf: ${"%.4f".format(matched.first().second)}\n")
                        
                        val firstCorrectIdx = matched.indexOfFirst { it.first.dominantDomain == trueDomain }
                        val firstCorrectRank = if (firstCorrectIdx != -1) (firstCorrectIdx + 1).toString() else "N/A"
                        writer.write("Rank of First Correct Domain Candidate: $firstCorrectRank\n")
                        
                        writer.write("All Match Candidates:\n")
                        matched.forEachIndexed { idx, (profile, conf) ->
                            writer.write("  [${idx + 1}] Leaf: ${profile.label} | Dominant: ${profile.dominantDomain} | Conf: ${"%.4f".format(conf)}\n")
                        }
                    } else {
                        writer.write("No candidates matched.\n")
                    }
                    writer.write("--------------------------------------------------\n")
                }
            }
        } catch (e: Exception) {
            log.error("Failed to write routing diagnostics: ${e.message}", e)
        } finally {
            diagWriter?.close()
        }

        // Per-leaf held-out support export: how many held-out queries each routable
        // leaf actually receives (top-1 and any-match), including zero-support leaves.
        try {
            val supportFile = File(trickleDir, "${condition}_heldout_leaf_support.csv")
            supportFile.bufferedWriter().use { writer ->
                writer.write("leafId,label,heldOutTop1Count,heldOutAnyCount\n")
                for ((leafId, profile) in profiles) {
                    writer.write("${escapeCsv(leafId)},${escapeCsv(profile.label)},${heldOutTop1Counts[leafId] ?: 0},${heldOutAnyCounts[leafId] ?: 0}\n")
                }
            }
            log.info("Held-out leaf support CSV written to ${supportFile.absolutePath}")

            val top1Dist = profiles.keys.map { heldOutTop1Counts[it] ?: 0 }.sorted()
            if (top1Dist.isNotEmpty()) {
                val minTop1 = top1Dist.first()
                val maxTop1 = top1Dist.last()
                val medianTop1 = if (top1Dist.size % 2 == 0) {
                    (top1Dist[top1Dist.size / 2].toDouble() + top1Dist[top1Dist.size / 2 - 1].toDouble()) / 2.0
                } else {
                    top1Dist[top1Dist.size / 2].toDouble()
                }
                val underSupported = top1Dist.count { it < cliConfig.questionsPerRound }
                log.info("Held-out leaf support ($condition): leaves=${top1Dist.size}, top1 min=$minTop1 median=${"%.1f".format(java.util.Locale.US, medianTop1)} max=$maxTop1, leaves with <${cliConfig.questionsPerRound} held-out top-1 queries: $underSupported")
            }
        } catch (e: Exception) {
            log.error("Failed to export held-out leaf support for $condition: ${e.message}", e)
        }

        try {
            val brierVal = computeBrierScore(predictedMap, gtMap, profiles.values)
            val maxLeafAssignments = config.formalism.maxLeafAssignments
            val maxAssignmentCapRate = if (testQueries.isNotEmpty()) {
                matchCounts.count { it >= maxLeafAssignments }.toDouble() / testQueries.size.toDouble()
            } else 0.0

            val calibrationFile = File(trickleDir, "${condition}_routing_calibration.csv")
            calibrationFile.bufferedWriter().use { writer ->
                writer.write("Metric,Value\n")
                writer.write("RoutingECE,${out.ece}\n")
                writer.write("BrierScore,$brierVal\n")
                writer.write("AvgMatchCount,${out.avgMatchCountEval}\n")
                writer.write("NoMatchRate,${out.noMatchRate}\n")
                writer.write("MaxAssignmentCapRate,$maxAssignmentCapRate\n")
            }
            log.info("Routing calibration CSV written to ${calibrationFile.absolutePath}")

            appendToTuningLedger(
                cliConfig.outputDir,
                currentSeed,
                condition,
                root,
                out,
                brierVal,
                maxAssignmentCapRate,
                testQueries,
                profiles,
                benchmarkReport,
                cliConfig
            )
        } catch (e: Exception) {
            log.error("Failed to compute and export calibration/ledger metrics for $condition: ${e.message}", e)
        }
        val endVal = System.currentTimeMillis()
        if (config.diagnostics.enableProfiling) {
            perfTracker.recordTime("arena.validation.$condition", endVal - startVal, testQueries.size.toLong())
        }
        return@runBlocking correctnessMap
    }

    private fun runCentroidRoutingTest(
        leaves: List<GraphNode>,
        profiles: Map<String, taxonomy.tui.service.LeafDomainProfile>,
        testQueries: List<Pair<String, String>>,
        condition: String,
        baseDir: File
    ) {
        val testTexts = testQueries.map { it.second }.toSet()
        val embeddings = embeddingCache.getBatch(testTexts)

        // Precompute and normalize leaf centroids to avoid redundant double array allocations in the hot loop
        val normalizedCentroids = leaves.mapNotNull { leaf ->
            val profile = profiles[leaf.id] ?: return@mapNotNull null
            val centroid = leaf.vmfMu
            if (centroid.isEmpty()) return@mapNotNull null
            val doubleCentroid = DoubleArray(centroid.size) { centroid[it].toDouble() }
            val normCentroid = l2Normalize(doubleCentroid)
            profile to normCentroid
        }

        var top1Correct = 0
        var top3Correct = 0
        var top5Correct = 0
        var top10Correct = 0
        var total = 0

        for ((trueDomain, text) in testQueries) {
            val emb = embeddings[text] ?: continue
            val doubleEmb = DoubleArray(emb.size) { emb[it].toDouble() }
            val normEmb = l2Normalize(doubleEmb)

            val scoredLeaves = normalizedCentroids.map { (profile, normCentroid) ->
                val dot = dotProduct(normEmb, normCentroid)
                profile to dot
            }.sortedByDescending { it.second }

            if (scoredLeaves.isEmpty()) continue
            total++

            if (scoredLeaves.first().first.dominantDomain == trueDomain) {
                top1Correct++
            }
            if (scoredLeaves.take(3).any { it.first.dominantDomain == trueDomain }) {
                top3Correct++
            }
            if (scoredLeaves.take(5).any { it.first.dominantDomain == trueDomain }) {
                top5Correct++
            }
            if (scoredLeaves.take(10).any { it.first.dominantDomain == trueDomain }) {
                top10Correct++
            }
        }

        val t1 = if (total > 0) top1Correct.toDouble() / total else 0.0
        val t3 = if (total > 0) top3Correct.toDouble() / total else 0.0
        val t5 = if (total > 0) top5Correct.toDouble() / total else 0.0
        val t10 = if (total > 0) top10Correct.toDouble() / total else 0.0

        log.info("Nearest-Centroid Routing Results ($condition):")
        log.info("  - Total Evaluated: $total")
        log.info("  - Top-1 Accuracy: ${"%,.2f%%".format(t1 * 100)}")
        log.info("  - Top-3 Accuracy: ${"%,.2f%%".format(t3 * 100)}")
        log.info("  - Top-5 Accuracy: ${"%,.2f%%".format(t5 * 100)}")
        log.info("  - Top-10 Accuracy: ${"%,.2f%%".format(t10 * 100)}")

        val trickleDir = File(baseDir, "validation")
        val file = File(trickleDir, "${condition}_centroid_routing_results.csv")
        file.bufferedWriter().use { writer ->
            writer.write("Metric,Value\n")
            writer.write("TotalQueries,$total\n")
            writer.write("Top1Accuracy,$t1\n")
            writer.write("Top3Accuracy,$t3\n")
            writer.write("Top5Accuracy,$t5\n")
            writer.write("Top10Accuracy,$t10\n")
        }
        log.info("Centroid routing results written to ${file.absolutePath}")
    }

    private fun l2Normalize(vec: DoubleArray): DoubleArray {
        var sum = 0.0
        for (x in vec) sum += x * x
        val mag = kotlin.math.sqrt(sum)
        if (mag == 0.0) return vec
        return DoubleArray(vec.size) { vec[it] / mag }
    }

    private fun dotProduct(a: DoubleArray, b: DoubleArray): Double {
        var sum = 0.0
        val limit = minOf(a.size, b.size)
        for (i in 0 until limit) {
            sum += a[i] * b[i]
        }
        return sum
    }

    private fun exportValidationMetrics(dir: File, condition: String, report: taxonomy.model.BenchmarkReport) {
        val file = File(dir, "${condition}_metrics.csv")
        file.bufferedWriter().use { writer ->
            writer.write("Condition,TotalQueries,TotalModelPairs,CoverageRate,OverallJudgeAccuracyAgreement\n")
            writer.write("${escapeCsv(condition)},${report.totalQueries},${report.totalModelPairs},${report.coverageRate},${report.overallJudgeAccuracyAgreement}\n")
        }
        log.info("Metrics CSV written to ${file.absolutePath}")
    }

    /**
     * Per-run readout of the optional answer-disagreement match filter.
     *
     * Written for every run, filter on or off, so a run's artifacts always state which
     * scheduling rule produced them. Naming follows the other validation exports:
     * `<condition>_match_filter_summary.csv` in the validation directory.
     */
    private fun exportMatchFilterSummary(dir: File, condition: String, report: taxonomy.model.BenchmarkReport) {
        val m = report.matchFilter
        val file = File(dir, "${condition}_match_filter_summary.csv")
        file.bufferedWriter().use { writer ->
            writer.write(
                "Condition,MatchFilter,SlotEvaluations,CandidateQuestionsBefore,CandidateQuestionsAfter," +
                    "RetainedFraction,FallbackSlots,MatchesScheduled,QuestionPairsSeen," +
                    "QuestionPairsUndetermined,Inert\n"
            )
            val retained = if (m.candidateQuestionsBefore > 0)
                m.candidateQuestionsAfter.toDouble() / m.candidateQuestionsBefore else 1.0
            writer.write(
                "${escapeCsv(condition)},${escapeCsv(m.filter)},${m.slotEvaluations}," +
                    "${m.candidateQuestionsBefore},${m.candidateQuestionsAfter},$retained," +
                    "${m.fallbackSlots},${m.matchesScheduled},${m.questionPairsSeen}," +
                    "${m.questionPairsUndetermined},${m.inert}\n"
            )
        }
        log.info("Match-filter summary CSV written to ${file.absolutePath}")
    }

    private fun exportLeafLeaderboard(dir: File, condition: String, snapshotId: String, root: GraphNode, models: List<String>) {
        val file = File(dir, "${condition}_leaf_leaderboard.csv")
        val btStates = rankingService.getAllBtStates(snapshotId)
        file.bufferedWriter().use { writer ->
            writer.write("Condition,LeafId,ModelId,BtScore,StdError,TotalComparisons\n")
            btStates.forEach { (leafId, state) ->
                models.forEach { model ->
                    val score = state.btScores[model] ?: 0.0
                    val err = state.stdErrors[model] ?: 10.0
                    writer.write("${escapeCsv(condition)},${escapeCsv(leafId)},${escapeCsv(model)},$score,$err,${state.totalComparisons}\n")
                }
            }
        }
        log.info("Leaderboard CSV written to ${file.absolutePath}")
    }

    private fun exportDomainStats(dir: File, condition: String, report: taxonomy.model.BenchmarkReport) {
        val file = File(dir, "${condition}_domain_stats.csv")
        file.bufferedWriter().use { writer ->
            writer.write("Condition,Domain,TotalQueries,AgreementRate,AvgConfidence,CoverageRate\n")
            report.perDomainStats.forEach { stat ->
                writer.write("${escapeCsv(condition)},${escapeCsv(stat.domain)},${stat.totalQueries},${stat.judgeAccuracyAgreementRate},${stat.avgConfidence},${stat.coverageRate}\n")
            }
        }
        log.info("Domain Stats CSV written to ${file.absolutePath}")
    }

    private fun exportVerdicts(dir: File, condition: String, report: taxonomy.model.BenchmarkReport) {
        val file = File(dir, "${condition}_verdicts.csv")
        file.bufferedWriter().use { writer ->
        // NodeId, the two per-order confidences, the two per-order win indicators and TieSource are
        // all needed to reconstruct a verdict downstream. Confidence alone is
        // `if (flip) 0.5 else avg(c1,c2) capped at 0.95`, which is irreversible — so without
        // ConfidenceFirstOrder/ConfidenceSecondOrder the judge's real confidence distribution
        // cannot be recovered from a completed run at any price. NodeId matters because a query
        // reaching two leaves produces two verdicts that are otherwise indistinguishable here.
        writer.write(
            "Condition,QueryId,QueryText,Category,NodeId,ModelA,ModelB,AnswerA,AnswerB," +
                "CorrectA,CorrectB,GroundTruth,Winner,Confidence,ConfidenceFirstOrder," +
                "ConfidenceSecondOrder,WinAFirst,WinASecond,PositionFlip,TieSource,Rationale\n"
        )
        report.queryResults.forEach { qr ->
            qr.pairEvaluations.forEach { (pairKey, evals) ->
                val models = pairKey.split("_vs_")
                val mA = models.getOrNull(0) ?: "Model A"
                val mB = models.getOrNull(1) ?: "Model B"
                val ansA = qr.modelAnswers[mA] ?: "?"
                val ansB = qr.modelAnswers[mB] ?: "?"
                val corrA = qr.modelCorrect[mA] ?: false
                val corrB = qr.modelCorrect[mB] ?: false

                evals.forEach { ev ->
                    writer.write(
                        "${escapeCsv(condition)}," +
                        "${qr.queryId}," +
                        "${escapeCsv(qr.query)}," +
                        "${escapeCsv(qr.gtCategory)}," +
                        "${escapeCsv(ev.nodeId ?: "")}," +
                        "${escapeCsv(mA)}," +
                        "${escapeCsv(mB)}," +
                        "${escapeCsv(ansA)}," +
                        "${escapeCsv(ansB)}," +
                        "$corrA," +
                        "$corrB," +
                        "${escapeCsv(qr.gtCorrectAnswer)}," +
                        "${escapeCsv(ev.winner)}," +
                        "${ev.confidence}," +
                        "${ev.confidenceFirstOrder}," +
                        "${ev.confidenceSecondOrder}," +
                        "${ev.winAFirst}," +
                        "${ev.winASecond}," +
                        "${ev.positionFlip}," +
                        "${escapeCsv(ev.tieSource ?: "")}," +
                        "${escapeCsv(ev.rationale)}\n"
                    )
                }
            }
        }
        }
        log.info("Verdicts CSV written to ${file.absolutePath}")
    }

    private fun exportBridgeNodes(dir: File, root: GraphNode) {
        val file = File(dir, "bridge_nodes.csv")
        val allNodes = mutableSetOf<GraphNode>()
        fun walk(n: GraphNode) {
            if (!allNodes.add(n)) return
            n.children.forEach { walk(it) }
            n.crossLinkChildren.forEach { walk(it) }
        }
        walk(root)

        fun collectSubtreeQueries(node: GraphNode): List<Embedding> {
            val queries = mutableListOf<Embedding>()
            val visited = mutableSetOf<String>()
            fun walk(n: GraphNode) {
                if (!visited.add(n.id)) return
                if (n.isLeaf) {
                    queries.addAll(n.queries)
                } else {
                    n.children.forEach { walk(it) }
                    n.crossLinkChildren.forEach { walk(it) }
                }
            }
            walk(node)
            return queries
        }

        val bridges = allNodes.filter { it.isBridge || it.parents.size > 1 || it.crossLinkChildren.isNotEmpty() }
        file.bufferedWriter().use { writer ->
            writer.write("BridgeId,Label,MemberDomains,ChildLeafIds,Coverage,Entropy,JsDivergence,Depth\n")
            bridges.forEach { b ->
                // Bridge / Cross-link children: evaluate both tree children and cross-link children
                val connectedChildren = (b.children + b.crossLinkChildren).distinctBy { it.id }
                val memberDomains = connectedChildren.mapNotNull { it.originalCategory ?: it.label }.distinct().joinToString(";")
                val childLeafIds = connectedChildren.map { it.id }.joinToString(";")
                val combinedQueries = connectedChildren.flatMap { collectSubtreeQueries(it) }.distinctBy { it.rawText }
                val coverage = combinedQueries.size
                val entropyVal = calculateGtEntropyForQueries(combinedQueries)
                val jsDiv = b.bridgeJsDivergence
                writer.write("${escapeCsv(b.id)},${escapeCsv(b.label ?: "")},${escapeCsv(memberDomains)},${escapeCsv(childLeafIds)},$coverage,${"%.4f".format(java.util.Locale.US, entropyVal)},${"%.4f".format(java.util.Locale.US, jsDiv)},${b.depth}\n")
            }
        }
        log.info("Bridge Nodes CSV written to ${file.absolutePath}")
    }

    private fun calculateGtEntropyForQueries(queries: List<Embedding>): Double {
        val counts = HashMap<String, Int>()
        for (q in queries) {
            val cat = q.groundTruthCategory
            if (!cat.isNullOrBlank()) {
                counts[cat] = (counts[cat] ?: 0) + 1
            }
        }
        val total = counts.values.sum().toDouble()
        if (total == 0.0) return 0.0
        var entropy = 0.0
        for (count in counts.values) {
            val p = count.toDouble() / total
            entropy -= p * (kotlin.math.log(p, 2.0))
        }
        return entropy
    }

    private fun exportBridgeResiduals(dir: File, root: GraphNode) {
        val file = File(dir, "bridge_residuals.csv")
        val allNodes = mutableSetOf<GraphNode>()
        fun walk(n: GraphNode) {
            if (!allNodes.add(n)) return
            n.children.forEach { walk(it) }
            n.crossLinkChildren.forEach { walk(it) }
        }
        walk(root)

        val queryIdToCategory = mutableMapOf<String, String>()
        allNodes.forEach { node ->
            node.queries.forEach { q ->
                val qIdStr = if (q.queryId != -1) q.queryId.toString() else q.rawText
                queryIdToCategory[qIdStr] = q.groundTruthCategory
            }
        }

        val nodesWithResiduals = allNodes.filter { it.residualQueries.isNotEmpty() }
        file.bufferedWriter().use { writer ->
            writer.write("NodeId,Label,ResidualCount,ResidualDomains,ConfDistribution\n")
            nodesWithResiduals.forEach { n ->
                val confs = n.residualConfidences.values
                val confSummary = if (confs.isEmpty()) {
                    "N/A"
                } else {
                    val avg = confs.average()
                    val min = confs.minOrNull() ?: 0.0
                    val max = confs.maxOrNull() ?: 0.0
                    "avg=${"%.4f".format(java.util.Locale.US, avg)};min=${"%.4f".format(java.util.Locale.US, min)};max=${"%.4f".format(java.util.Locale.US, max)}"
                }
                
                val domains = n.residualQueries.mapNotNull { qId ->
                    queryIdToCategory[qId]
                }.distinct().joinToString(";")

                writer.write("${escapeCsv(n.id)},${escapeCsv(n.label ?: "")},${n.residualQueries.size},${escapeCsv(domains)},${escapeCsv(confSummary)}\n")
            }
        }
        log.info("Bridge Residuals CSV written to ${file.absolutePath}")
    }

    private fun exportLatexTable(dir: File, condition: String, ranks: List<ModelRank>) {
        val file = File(dir, "${condition}_leaderboard.tex")
        file.bufferedWriter().use { writer ->
            writer.write("\\begin{table}[ht]\n")
            writer.write("\\centering\n")
            writer.write("\\caption{Global Bradley-Terry Leaderboard for Condition \\textsc{${condition.uppercase()}}}\n")
            writer.write("\\label{tab:leaderboard_${condition.lowercase()}}\n")
            writer.write("\\begin{tabular}{cccccc}\n")
            writer.write("\\hline\n")
            writer.write("\\textbf{Rank} & \\textbf{Model ID} & \\textbf{BT Score} & \\textbf{Std Error} & \\textbf{95\\% CI} & \\textbf{Total Matches} \\\\\n")
            writer.write("\\hline\n")
            ranks.forEach { r ->
                val ciLow = String.format(java.util.Locale.US, "%.4f", r.confidenceIntervalLow)
                val ciHigh = String.format(java.util.Locale.US, "%.4f", r.confidenceIntervalHigh)
                val scoreStr = String.format(java.util.Locale.US, "%+.4f", r.btScore)
                val seStr = String.format(java.util.Locale.US, "%.4f", r.stdError)
                writer.write("${r.rank} & ${r.modelId.replace("_", "\\_")} & $scoreStr & $seStr & $[$ciLow, $ciHigh]$ & ${r.comparisonsTotal} \\\\\n")
            }
            writer.write("\\hline\n")
            writer.write("\\end{tabular}\n")
            writer.write("\\end{table}\n")
        }
        log.info("LaTeX Leaderboard Table written to ${file.absolutePath}")
    }

    private fun escapeCsv(value: Any?): String {
        val s = value?.toString() ?: ""
        if (s.contains(",") || s.contains("\"") || s.contains("\n") || s.contains("\r")) {
            return "\"" + s.replace("\"", "\"\"") + "\""
        }
        return s
    }

    internal fun parseToml(text: String): HeadlessCliConfig {
        var snapshotId = "unsaved"
        var models = listOf<String>()
        var queryLimit = 0
        var category: String? = null
        var confidenceGate = 0.65
        var parallelism = 6
        var questionsPerRound = 12
        var reservedOnly = true
        var resumeBenchmark = false
        var profileMode = false
        var profileSeTarget = 0.15
        var profileStrataFile: String? = null
        var maxQueryReuse = Int.MAX_VALUE
        var matchFilter = "none"
        var tau: Double? = null
        var enableFinalMetrics: Boolean? = null
        var adaptiveBarFile: String? = null
        var embeddingSliceDim: Int? = null
        var splitDropTopPcs: Int? = null
        var splitWhiten: Boolean? = null
        var proposalMemo: String? = null
        var conditions = listOf("MAIN", "ORACLE", "GENERIC_JUDGE", "RANDOM_SCHEDULER")
        var outputDir = "experiment"
        var testRatio = 0.3
        var seed = 42L
        var seeds = listOf<Long>()
        var splitSeed: Long? = null
        var constructionOrderShuffleSeed: Long? = null
        var anchorFree = false
        var proposalAcceptMultiplier: Double? = null
        var reservedPoolFile: String? = null
        var v2PoolFile: String? = null
        var unionRoutingItemKey = false
        var v2ForeignMembers = listOf<String>()
        var pool: String? = null
        var acknowledgedEvalMembers = listOf<String>()
        var regenerateSplit = false
        var runPipeline = false
        var maxDepth: Int? = null
        var minClusterSize: Int? = null
        var proposalSeparationBar: Double? = null
        var membershipFloor: Double? = null
        var routingBeamGamma: Double? = null
        var descentMargin: Double? = null
        var acceptanceZ: Double? = null
        var marginalEps: Double? = null
        var maxK: Int? = null
        var excludeFromAnchoring: List<String> = emptyList()
        var expectedWithheldQueries: Int? = null
        var enableRefitGate: Boolean? = null
        var cosineTau: Double? = null
        var leafAcceptanceScale: Double? = null
        var assignmentGap: Double? = null
        var enableLabeling: Boolean? = null
        var judgeInduction = false
        var datasetType: String? = null
        var corpora: List<String>? = null
        var corpusDbPath: String? = null
        var unionSnapshots: List<String> = emptyList()
        var unionRootRouting: String = taxonomy.service.UnionRouting.Rule.DEFAULT_KEY
        var runBenchmark = true
        var runTrickle = false
        var domains = listOf<String>()
        var enableStableQuestionIds: Boolean? = null
        var enableResidualRouting: Boolean? = null
        var enableResidualSplitGate: Boolean? = null
        var fusionSimilarityThreshold: Double? = null
        var effectiveSupportFloor: Double? = null
        var enableGtWarmStart: Boolean? = null
        var maxLeafAssignments: Int? = null
        var dagMode: String? = null
        var numIterations: Int? = null
        var defaultKappaPrior: Double? = null
        var runBaselines = true
        var enableProfiling: Boolean? = null
        var judgeSeesOptions: Boolean? = null
        var judgeOptionMode: String? = null
        var judgeRecipe: String? = null
        var judgeRecipeKit: String? = null
        var judgeRecipeModel: String? = null
        var judgeRecipeMaxTokens: Int? = null
        var judgeRecipeTemperature: Double? = null

        val lines = mutableListOf<String>()
        var inArray = false
        var arrayBuffer = StringBuilder()

        text.lines().forEach { rawLine ->
            val trimmed = rawLine.substringBefore("#").trim()
            if (trimmed.isEmpty()) return@forEach

            if (inArray) {
                arrayBuffer.append(" ").append(trimmed)
                if (trimmed.contains("]")) {
                    lines.add(arrayBuffer.toString())
                    inArray = false
                }
            } else {
                if (trimmed.contains("=") && trimmed.substringAfter("=").trim().startsWith("[") && !trimmed.contains("]")) {
                    inArray = true
                    arrayBuffer = StringBuilder(trimmed)
                } else {
                    lines.add(trimmed)
                }
            }
        }

        lines.forEach { line ->
            val key = line.substringBefore("=").trim()
            val rawVal = line.substringAfter("=").trim()

            fun parseStringList(s: String): List<String> {
                return s.trim('[', ']').split(",").map { it.trim(' ', '"', '\'') }.filter { it.isNotEmpty() }
            }

            when (key) {
                "snapshotId" -> snapshotId = rawVal.trim('"', '\'')
                "models" -> models = parseStringList(rawVal)
                "queryLimit" -> queryLimit = rawVal.toInt()
                "category" -> category = rawVal.trim('"', '\'').takeIf { it != "null" && it.isNotEmpty() }
                "confidenceGate" -> confidenceGate = rawVal.toDouble()
                "parallelism" -> parallelism = rawVal.toInt()
                "questionsPerRound" -> questionsPerRound = rawVal.toInt()
                "reservedOnly" -> reservedOnly = rawVal.toBoolean()
                "resumeBenchmark" -> resumeBenchmark = rawVal.toBoolean()
                "profileMode" -> profileMode = rawVal.toBoolean()
                "profileSeTarget" -> profileSeTarget = rawVal.toDouble()
                "profileStrataFile" -> profileStrataFile = rawVal.trim('"', '\'')
                "maxQueryReuse" -> maxQueryReuse = rawVal.toInt()
                // Validated at parse time, not at scheduling time: an unknown key is fatal here,
                // and an unknown VALUE must be too, or a typo silently runs the default arm.
                "matchFilter" -> matchFilter = taxonomy.arena.MatchFilter.fromToml(rawVal).tomlValue
                "tau" -> tau = rawVal.toDouble()
                "enableFinalMetrics" -> enableFinalMetrics = rawVal.toBoolean()
                "adaptiveBarFile" -> adaptiveBarFile = rawVal.trim('"', '\'')
                "embeddingSliceDim" -> embeddingSliceDim = rawVal.toInt()
                "splitDropTopPcs" -> splitDropTopPcs = rawVal.toInt()
                "splitWhiten" -> splitWhiten = rawVal.toBoolean()
                "proposalMemo" -> {
                    // Fail-closed: absent = off; anything but the three literals is fatal at
                    // parse time, never silently off (the same stance as judgeOptionMode).
                    val m = rawVal.trim().trim('"', '\'')
                    require(m.lowercase() in setOf("off", "shadow", "on")) {
                        "[CONFIG] proposalMemo must be off, shadow or on (got '$rawVal')"
                    }
                    proposalMemo = m.lowercase()
                }
                "conditions" -> conditions = parseStringList(rawVal)
                "outputDir" -> outputDir = rawVal.trim('"', '\'')
                "testRatio" -> testRatio = rawVal.toDouble()
                "seed" -> seed = rawVal.toLong()
                "regenerateSplit" -> regenerateSplit = rawVal.toBoolean()
                "runPipeline" -> runPipeline = rawVal.toBoolean()
                "maxDepth" -> maxDepth = rawVal.toInt()
                "minClusterSize" -> minClusterSize = rawVal.toInt()
                "proposalSeparationBar" -> proposalSeparationBar = rawVal.toDouble()
                "membershipFloor" -> membershipFloor = rawVal.toDouble()
                "routingBeamGamma" -> routingBeamGamma = rawVal.toDouble()
                "descentMargin" -> descentMargin = rawVal.toDouble()
                "acceptanceZ" -> acceptanceZ = rawVal.toDouble()
                "marginalEps" -> marginalEps = rawVal.toDouble()
                "maxK" -> maxK = rawVal.toInt()
                "expectedWithheldQueries" -> expectedWithheldQueries = rawVal.toInt()
                "excludeFromAnchoring" -> excludeFromAnchoring =
                    rawVal.trim().removePrefix("[").removeSuffix("]")
                        .split(",")
                        .map { it.trim().trim('\"', '\'') }
                        .filter { it.isNotEmpty() }
                "enableRefitGate" -> enableRefitGate = rawVal.toBoolean()
                "enableLabeling" -> enableLabeling = rawVal.toBoolean()
                "judgeInduction" -> judgeInduction = rawVal.toBoolean()
                "datasetType" -> datasetType = rawVal.trim('"', '\'')
                "corpora" -> corpora = parseStringList(rawVal)
                "corpusDbPath" -> corpusDbPath = rawVal.trim('"', '\'')
                "unionSnapshots" -> unionSnapshots = parseStringList(rawVal)
                "unionRootRouting" -> unionRootRouting = rawVal.trim('"', '\'')
                "runBenchmark" -> runBenchmark = rawVal.toBoolean()
                "runTrickle" -> runTrickle = rawVal.toBoolean()
                "domains" -> domains = parseStringList(rawVal)
                "seeds" -> seeds = parseStringList(rawVal).map { it.toLong() }
                "splitSeed" -> splitSeed = rawVal.toLong()
                // H9-REM: a non-integer value throws (fatal); a mis-spelled key hits the
                // unknown-key throw below. Cross-key validation (runPipeline, no union) is in
                // HeadlessCliConfig's init block, shared with the JSON decoder.
                "constructionOrderShuffleSeed" -> constructionOrderShuffleSeed = rawVal.toLong()
                // ANCHOR-FREE: strict boolean. String.toBoolean() maps every non-"true" value to
                // false, so `anchorFree = ture` would run the anchored path under a config that
                // asserts the anchor-free one; only the literals true / false parse here.
                "anchorFree" -> anchorFree = rawVal.toBooleanStrictOrNull()
                    ?: throw IllegalArgumentException("[CONFIG] anchorFree must be true or false (got '$rawVal')")
                // K-SELECTION: strict number. A quoted or non-numeric value is fatal here with the key
                // named (toDouble's own NumberFormatException would not name it); the [1.0, 2.0]
                // range and the runPipeline / unionSnapshots cross-check are in the init block.
                "proposalAcceptMultiplier" -> proposalAcceptMultiplier = rawVal.trim().toDoubleOrNull()
                    ?.takeIf { it.isFinite() }
                    ?: throw IllegalArgumentException("[CONFIG] proposalAcceptMultiplier must be a finite number in [1.0, 2.0] (got '$rawVal')")
                "reservedPoolFile" -> reservedPoolFile = rawVal.trim('"', '\'')
                // RP12: a path; an empty value is fatal (init block), cross-checks there too.
                "v2PoolFile" -> v2PoolFile = rawVal.trim('"', '\'')
                // RP12 B3: strict boolean (only the literals true / false parse); the union cross-check is in the init block.
                "v2ForeignMembers" -> v2ForeignMembers = parseStringList(rawVal)
                "unionRoutingItemKey" -> unionRoutingItemKey = rawVal.toBooleanStrictOrNull()
                    ?: throw IllegalArgumentException("[CONFIG] unionRoutingItemKey must be true or false (got '$rawVal')")
                "pool" -> pool = rawVal.trim('"', '\'')
                "acknowledgedEvalMembers" -> acknowledgedEvalMembers = parseStringList(rawVal)
                "enableStableQuestionIds" -> enableStableQuestionIds = rawVal.toBoolean()
                "enableResidualRouting" -> enableResidualRouting = rawVal.toBoolean()
                "enableResidualSplitGate" -> enableResidualSplitGate = rawVal.toBoolean()
                "enableProfiling" -> {
                    config.diagnostics.enableProfiling = rawVal.toBoolean()
                    enableProfiling = rawVal.toBoolean()
                }
                "judgeSeesOptions" -> {
                    config.llm.judgeSeesOptions = rawVal.toBoolean()
                    judgeSeesOptions = rawVal.toBoolean()
                }
                "judgeOptionMode" -> {
                    val m = rawVal.trim().trim('"').uppercase()
                    require(m in setOf("OPTIONS", "RESOLVED", "BLIND")) {
                        "judgeOptionMode must be OPTIONS, RESOLVED or BLIND (got '$rawVal')"
                    }
                    config.llm.judgeOptionMode = m
                    judgeOptionMode = m
                }
                // JUDGE-WIRING keys. Applied to the live config here (as judgeOptionMode is) AND carried
                // on the CLI record; the recipe's own validation (RESOLVED, kit, key) runs at start-up.
                "judgeRecipe" -> {
                    val name = rawVal.trim().trim('"', '\'')
                    require(name == "STACK-v2") { "judgeRecipe must be \"STACK-v2\" (the only registered recipe; got '$rawVal')" }
                    config.llm.judgeRecipe.enabled = true
                    config.llm.judgeRecipe.name = name
                    judgeRecipe = name
                }
                "judgeRecipeKit" -> { val v = rawVal.trim().trim('"', '\''); config.llm.judgeRecipe.kitPath = v; judgeRecipeKit = v }
                "judgeRecipeModel" -> { val v = rawVal.trim().trim('"', '\''); config.llm.judgeRecipe.model = v; judgeRecipeModel = v }
                "judgeRecipeMaxTokens" -> {
                    val v = rawVal.trim().toInt()
                    require(v > 0) { "judgeRecipeMaxTokens must be positive (got '$rawVal')" }
                    config.llm.judgeRecipe.maxTokens = v; judgeRecipeMaxTokens = v
                }
                "judgeRecipeTemperature" -> {
                    val v = rawVal.trim().toDouble()
                    require(v.isFinite() && v >= 0.0) { "judgeRecipeTemperature must be a finite non-negative literal (got '$rawVal')" }
                    config.llm.judgeRecipe.temperature = v; judgeRecipeTemperature = v
                }
                "fusionSimilarityThreshold" -> fusionSimilarityThreshold = rawVal.toDouble()
                "effectiveSupportFloor" -> effectiveSupportFloor = rawVal.toDouble()
                "enableGtWarmStart" -> enableGtWarmStart = rawVal.toBoolean()
                "maxLeafAssignments" -> maxLeafAssignments = rawVal.toInt()
                "dagMode" -> dagMode = rawVal.trim().trim('"').trim('\'')
                "numIterations" -> numIterations = rawVal.toInt()
                "defaultKappaPrior" -> defaultKappaPrior = rawVal.toDouble()
                "runBaselines" -> runBaselines = rawVal.toBoolean()
                // H9b fix (2026-09-07): unknown keys are FATAL. The frozen config's own
                // 'tau' key was silently unparsed for weeks and worked only because the
                // code default coincided; a registration must never be able to assert a
                // value the run ignores.
                else -> throw IllegalArgumentException(
                    "[CONFIG] Unknown configuration key in TOML file: '$key' = '$rawVal' — " +
                        "unknown keys are fatal; add a parse case or remove the key")
            }
        }
        return HeadlessCliConfig(
            snapshotId = snapshotId,
            models = models,
            queryLimit = queryLimit,
            category = category,
            confidenceGate = confidenceGate,
            parallelism = parallelism,
            questionsPerRound = questionsPerRound,
            reservedOnly = reservedOnly,
            resumeBenchmark = resumeBenchmark,
            profileMode = profileMode,
            profileSeTarget = profileSeTarget,
            profileStrataFile = profileStrataFile,
            maxQueryReuse = maxQueryReuse,
            matchFilter = matchFilter,
            tau = tau,
            enableFinalMetrics = enableFinalMetrics,
            adaptiveBarFile = adaptiveBarFile,
            embeddingSliceDim = embeddingSliceDim,
            splitDropTopPcs = splitDropTopPcs,
            splitWhiten = splitWhiten,
            proposalMemo = proposalMemo,
            conditions = conditions,
            outputDir = outputDir,
            testRatio = testRatio,
            seed = seed,
            seeds = seeds,
            splitSeed = splitSeed,
            constructionOrderShuffleSeed = constructionOrderShuffleSeed,
            anchorFree = anchorFree,
            proposalAcceptMultiplier = proposalAcceptMultiplier,
            reservedPoolFile = reservedPoolFile,
            v2PoolFile = v2PoolFile,
            unionRoutingItemKey = unionRoutingItemKey,
            v2ForeignMembers = v2ForeignMembers,
            pool = pool,
            acknowledgedEvalMembers = acknowledgedEvalMembers,
            regenerateSplit = regenerateSplit,
            runPipeline = runPipeline,
            maxDepth = maxDepth,
            minClusterSize = minClusterSize,
            proposalSeparationBar = proposalSeparationBar,
            membershipFloor = membershipFloor,
            routingBeamGamma = routingBeamGamma,
            descentMargin = descentMargin,
            acceptanceZ = acceptanceZ,
            marginalEps = marginalEps,
            maxK = maxK,
            excludeFromAnchoring = excludeFromAnchoring,
            expectedWithheldQueries = expectedWithheldQueries,
            enableRefitGate = enableRefitGate,
            defaultKappaPrior = defaultKappaPrior,
            enableLabeling = enableLabeling,
            judgeInduction = judgeInduction,
            datasetType = datasetType,
            corpora = corpora,
            corpusDbPath = corpusDbPath,
            unionSnapshots = unionSnapshots,
            unionRootRouting = unionRootRouting,
            runBenchmark = runBenchmark,
            runTrickle = runTrickle,
            domains = domains,
            enableStableQuestionIds = enableStableQuestionIds,
            enableResidualRouting = enableResidualRouting,
            enableResidualSplitGate = enableResidualSplitGate,
            fusionSimilarityThreshold = fusionSimilarityThreshold,
            effectiveSupportFloor = effectiveSupportFloor,
            enableGtWarmStart = enableGtWarmStart,
            maxLeafAssignments = maxLeafAssignments,
            dagMode = dagMode,
            numIterations = numIterations,
            runBaselines = runBaselines,
            enableProfiling = enableProfiling,
            judgeSeesOptions = judgeSeesOptions,
            judgeOptionMode = judgeOptionMode,
            judgeRecipe = judgeRecipe,
            judgeRecipeKit = judgeRecipeKit,
            judgeRecipeModel = judgeRecipeModel,
            judgeRecipeMaxTokens = judgeRecipeMaxTokens,
            judgeRecipeTemperature = judgeRecipeTemperature
        ).also { parsed ->
            // Fail on a silent no-op rather than on a missing log line.
            //
            // If the key is present but misparsed (misspelling, wrong list syntax, a
            // parse branch that never runs) the set ends up empty, the [HOLD-OUT]
            // guards pass TRIVIALLY — no excluded category is among the anchors,
            // because there are none — and the run looks like a normal 14-anchor
            // build. The only signal would be the ABSENCE of a warning line, and an
            // absence is exactly what nobody notices.
            //
            // Same reasoning as the config-header provenance guard: the check has to
            // fire on the failure, not require someone to spot something missing.
            if (Regex("""^\s*excludeFromAnchoring\s*=""", RegexOption.MULTILINE).containsMatchIn(text)) {
                require(parsed.excludeFromAnchoring.isNotEmpty()) {
                    "Config declares excludeFromAnchoring but it parsed to an EMPTY set. " +
                        "The hold-out would silently run with every domain anchored and " +
                        "produce a clean-looking negative. Expected a list literal, e.g. " +
                        "excludeFromAnchoring = [Law]"
                }
            }
            // Multi-corpus (stage 1): every listed name must be a known corpus; a union is made
            // of leaderboard sources only (the built-in types own the v2 DB's tables and would
            // try to DOWNLOAD into whatever DB the run opened); and a leaderboard source needs
            // an explicit corpusDbPath — the default DB has no corpus_questions table. All of
            // this fails here, at parse time, not after a construction that silently used one
            // corpus.
            parsed.corpora?.let { list ->
                require(list.isNotEmpty()) { "corpora is declared but parsed to an EMPTY list" }
                require(list.size == list.toSet().size) { "[CONFIG] corpora = $list lists a corpus twice" }
                list.forEach { name ->
                    require(name in taxonomy.dataset.CorpusRegistry.KNOWN) {
                        "[CONFIG] unknown corpus '$name' in corpora (known: ${taxonomy.dataset.CorpusRegistry.KNOWN.keys})"
                    }
                }
                val leaderboard = list.filter { taxonomy.dataset.CorpusRegistry.isLeaderboard(it) }
                if (list.size > 1) {
                    require(leaderboard.size == list.size) {
                        "[CONFIG] corpora = $list: a union may list leaderboard corpora only" +
                            " (${taxonomy.dataset.CorpusRegistry.LEADERBOARD.keys}); built-in types are single-corpus"
                    }
                }
                if (leaderboard.isNotEmpty()) {
                    require(!parsed.corpusDbPath.isNullOrBlank()) {
                        "[CONFIG] corpora = $list needs corpusDbPath = \"<multi-corpus DB>\" (built by tools/ingest/multicorpus_db.py)"
                    }
                }
                parsed.datasetType?.let { dt ->
                    require(list.size == 1 && dt.uppercase() == list.single()) {
                        "[CONFIG] datasetType = '$dt' disagrees with corpora = $list; use one of them"
                    }
                }
            }
            // Stage 1b: a union run grafts existing per-corpus snapshots — it never constructs —
            // and `corpora` names the members (one leaderboard corpus per snapshot; the fetcher
            // and the trickle read all of them).
            if (parsed.unionSnapshots.isNotEmpty()) {
                require(!parsed.runPipeline) { "[CONFIG] unionSnapshots grafts existing snapshots; set runPipeline = false" }
                require(parsed.unionSnapshots.size == parsed.unionSnapshots.toSet().size) {
                    "[CONFIG] unionSnapshots = ${parsed.unionSnapshots} lists a snapshot twice"
                }
                val members = parsed.corpora
                require(members != null && members.size == parsed.unionSnapshots.size) {
                    "[CONFIG] unionSnapshots = ${parsed.unionSnapshots} needs corpora = [one leaderboard corpus per snapshot]" +
                        " (got corpora = $members)"
                }
                require(members.all { taxonomy.dataset.CorpusRegistry.isLeaderboard(it) }) {
                    "[CONFIG] unionSnapshots: every member of corpora = $members must be a leaderboard corpus"
                }
            }
            // Stage 1c: the union root routing rule is a union-readout key; a single-corpus run
            // must not carry it (it would be silently inert there).
            val rootRule = try { taxonomy.service.UnionRouting.Rule.parse(parsed.unionRootRouting) } catch (e: IllegalArgumentException) {
                throw IllegalArgumentException("[CONFIG] ${e.message}", e)
            }
            require(rootRule == taxonomy.service.UnionRouting.Rule.DESCENT || parsed.unionSnapshots.isNotEmpty()) {
                "[CONFIG] unionRootRouting = \"${parsed.unionRootRouting}\" applies to union runs only (set unionSnapshots = [...])"
            }
            // H9-REM: the constructionOrderShuffleSeed x runPipeline / unionSnapshots cross-check
            // is in HeadlessCliConfig's init block (shared with the JSON decoder), not here.
            // ANCHOR-FREE: likewise (anchorFree x runPipeline / unionSnapshots / excludeFromAnchoring).
            // K-SELECTION: likewise (proposalAcceptMultiplier range [1.0, 2.0] x runPipeline / unionSnapshots).
        }
    }

    private fun checkAcyclic(root: GraphNode): Boolean {
        val visited = mutableMapOf<String, Int>() // 0=unvisited, 1=visiting, 2=visited
        fun dfs(n: GraphNode): Boolean {
            val state = visited[n.id] ?: 0
            if (state == 1) return false
            if (state == 2) return true
            visited[n.id] = 1
            for (c in n.children + n.crossLinkChildren) {
                if (!dfs(c)) return false
            }
            visited[n.id] = 2
            return true
        }
        return dfs(root)
    }

    private fun getGitCommitSha(): String {
        return try {
            val process = Runtime.getRuntime().exec("git rev-parse HEAD")
            process.inputStream.bufferedReader().readText().trim()
        } catch (e: Exception) {
            "unknown"
        }
    }

    private fun computeConfigHash(): String {
        val raw = listOf(
            config.formalism.maxDepth,
            config.formalism.minClusterSize,
            config.formalism.proposalSeparationBar,
            config.formalism.membershipFloor,
            config.formalism.routingBeamGamma,
            config.formalism.descentMargin,
            config.formalism.maxLeafAssignments,
            config.formalism.dagMode,
            config.formalism.fusionSimilarityThreshold,
            config.formalism.effectiveSupportFloor
        ).joinToString(",")
        return String.format(java.util.Locale.US, "%08x", raw.hashCode())
    }

    private fun exportGraphValidity(dir: File, root: GraphNode, condition: String) {
        val file = File(dir, "${condition}_graph_validity.csv")
        val allNodes = mutableSetOf<GraphNode>()
        fun walk(n: GraphNode) {
            if (!allNodes.add(n)) return
            n.children.forEach { walk(it) }
            n.crossLinkChildren.forEach { walk(it) }
        }
        walk(root)

        val acyclic = checkAcyclic(root)
        val rootReachable = true
        val leafCount = allNodes.count { it.isLeaf }
        val bridgeCount = allNodes.count { it.isBridged }
        val orphanCount = allNodes.count { it.id != root.id && it.parents.isEmpty() }
        
        val bridges = allNodes.filter { it.isBridge || it.parents.size > 1 || it.crossLinkChildren.isNotEmpty() }
        val validBridgesWithConnections = bridges.filter { b ->
            b.parents.isNotEmpty() && (b.children.isNotEmpty() || b.crossLinkChildren.isNotEmpty())
        }
        val bridgeGroups = validBridgesWithConnections.groupBy { b ->
            (b.parents.map { p -> p.id }.toSet()) to (b.children.map { c -> c.id } + b.crossLinkChildren.map { c -> c.id }).toSet()
        }
        val duplicateBridgeCount = bridgeGroups.values.filter { it.size > 1 }.sumOf { it.size - 1 }

        val depthDist = allNodes.groupBy { it.depth }
            .entries.sortedBy { it.key }
            .joinToString(";") { "${it.key}:${it.value.size}" }

        val residualCount = allNodes.sumOf { it.residualQueries.size }

        file.bufferedWriter().use { writer ->
            writer.write("Metric,Value\n")
            writer.write("Acyclic,$acyclic\n")
            writer.write("RootReachable,$rootReachable\n")
            writer.write("OrphanCount,$orphanCount\n")
            writer.write("DuplicateBridgeCount,$duplicateBridgeCount\n")
            writer.write("DepthDistribution,$depthDist\n")
            writer.write("LeafCount,$leafCount\n")
            writer.write("BridgeCount,$bridgeCount\n")
            writer.write("ResidualCount,$residualCount\n")
        }
        log.info("Graph validity CSV for $condition written to ${file.absolutePath}")
    }

    private fun exportTaxonomyQuality(dir: File, root: GraphNode, condition: String) {
        val file = File(dir, "${condition}_taxonomy_quality.csv")

        val groundTruthMap = mutableMapOf<String, List<String>>()
        // The construction corpus, recovered from the frozen graph so that the global
        // objective J can be reported alongside the quality metrics in the run's
        // artefacts, not only as per-iteration [J-TRACK] log lines.
        val corpusByText = LinkedHashMap<String, Embedding>()
        fun walkGt(n: GraphNode, visited: MutableSet<String> = mutableSetOf()) {
            if (!visited.add(n.id)) return
            n.queries.forEach { emb ->
                val gt = emb.groundTruthCategory
                if (gt.isNotBlank()) {
                    groundTruthMap[emb.rawText] = listOf(gt)
                }
                corpusByText.putIfAbsent(emb.rawText, emb)
            }
            n.children.forEach { walkGt(it, visited) }
            n.crossLinkChildren.forEach { walkGt(it, visited) }
        }
        walkGt(root)

        val separationJ = try {
            taxonomy.utils.StatisticsUtils.computeDagSeparationJ(root, corpusByText.values.toList())
        } catch (e: Exception) {
            log.error("Failed to compute separation J for $condition: ${e.message}", e)
            Double.NaN
        }

        val startGen = System.currentTimeMillis()
        val reportObj = taxonomy.utils.TaxonomyMetrics(root, groundTruthMap).generateReport()
        val endGen = System.currentTimeMillis()
        if (config.diagnostics.enableProfiling) {
            perfTracker.recordTime("construction.finalization.generate_report", endGen - startGen, 1L)
        }

        file.bufferedWriter().use { writer ->
            writer.write("Metric,Value\n")
            writer.write("SeparationJ,$separationJ\n")
            writer.write("WeightedLeafPurity,${reportObj.weightedLeafPurity}\n")
            writer.write("DendrogramPurity,${reportObj.dendrogramPurity}\n")
            writer.write("SphericalSilhouette,${reportObj.sphericalSilhouette}\n")
            writer.write("TotalDasguptaCost,${reportObj.totalDasguptaCost}\n")
            writer.write("NormalisedSackinIndex,${reportObj.normalisedSackin}\n")
        }
        log.info("Taxonomy quality CSV for $condition written to ${file.absolutePath}")
    }

    private fun exportBridgeQuality(dir: File, root: GraphNode, condition: String) {
        val file = File(dir, "${condition}_bridge_quality.csv")
        val allNodes = mutableSetOf<GraphNode>()
        fun walk(n: GraphNode) {
            if (!allNodes.add(n)) return
            n.children.forEach { walk(it) }
            n.crossLinkChildren.forEach { walk(it) }
        }
        walk(root)

        val bridges = allNodes.filter { it.isBridge || it.parents.size > 1 || it.crossLinkChildren.isNotEmpty() }
        val sourceA = bridges.filter { it.parents.size > 1 && !it.id.startsWith("bridge_sourceB_") }
        val sourceB = bridges.filter { it.crossLinkChildren.isNotEmpty() || it.id.startsWith("bridge_sourceB_") }

        fun collectSubtreeQueries(node: GraphNode): List<Embedding> {
            val queries = mutableListOf<Embedding>()
            val visited = mutableSetOf<String>()
            fun walkSub(n: GraphNode) {
                if (!visited.add(n.id)) return
                if (n.isLeaf) {
                    queries.addAll(n.queries)
                } else {
                    n.children.forEach { walkSub(it) }
                    n.crossLinkChildren.forEach { walkSub(it) }
                }
            }
            walkSub(node)
            return queries
        }

        file.bufferedWriter().use { writer ->
            writer.write("Metric/BridgeId,BridgeType/Value,Depth,Coverage,CrossDomainLabelMix,TopRepresentativeQueries\n")
            writer.write("SourceA_Count,${sourceA.size},N/A,N/A,N/A,N/A\n")
            writer.write("SourceB_Count,${sourceB.size},N/A,N/A,N/A,N/A\n")
            bridges.forEach { b ->
                val bType = if (b.id.startsWith("bridge_sourceB_") || b.crossLinkChildren.isNotEmpty()) "SourceB" else "SourceA"
                val connectedChildren = (b.children + b.crossLinkChildren).distinctBy { it.id }
                val memberDomains = connectedChildren.mapNotNull { it.originalCategory ?: it.label }.distinct().joinToString(";")
                val combinedQueries = connectedChildren.flatMap { collectSubtreeQueries(it) }.distinctBy { it.rawText }
                val coverage = combinedQueries.size
                val topQueries = b.queries.take(10).map { it.rawText.replace(",", " ").replace("\n", " ").trim() }.joinToString(";")
                writer.write("${escapeCsv(b.id)},$bType,${b.depth},$coverage,${escapeCsv(memberDomains)},${escapeCsv(topQueries)}\n")
            }
        }
        log.info("Bridge quality CSV for $condition written to ${file.absolutePath}")
    }

    private fun computeBrierScore(
        predictedMap: Map<String, Map<String, Double>>,
        gtMap: Map<String, String>,
        perLeafDomains: Collection<taxonomy.tui.service.LeafDomainProfile>
    ): Double {
        if (gtMap.isEmpty()) return 0.0
        val allDomains = (perLeafDomains.map { it.dominantDomain } + gtMap.values).distinct().toSet()
        var brierSum = 0.0
        for ((text, trueDomain) in gtMap) {
            val domainConf = predictedMap[text] ?: emptyMap()
            var queryBrier = 0.0
            for (d in allDomains) {
                val f = domainConf[d] ?: 0.0
                val y = if (d == trueDomain) 1.0 else 0.0
                queryBrier += (f - y) * (f - y)
            }
            brierSum += queryBrier
        }
        return brierSum / gtMap.size
    }

    private fun appendToTuningLedger(
        outputDir: String,
        currentSeed: Long,
        condition: String,
        root: GraphNode,
        out: taxonomy.tui.BatchTrickleTestResults,
        brierVal: Double,
        maxAssignmentCapRate: Double,
        testQueries: List<Pair<String, String>>,
        profiles: Map<String, LeafDomainProfile>,
        benchmarkReport: BenchmarkReport?,
        cliConfig: HeadlessCliConfig
    ) {
        val ledgerFile = File(outputDir, "tuning_ledger.csv")
        val isNew = !ledgerFile.exists()

        val allNodes = mutableSetOf<GraphNode>()
        fun walk(n: GraphNode) {
            if (!allNodes.add(n)) return
            n.children.forEach { walk(it) }
            n.crossLinkChildren.forEach { walk(it) }
        }
        walk(root)

        val acyclic = checkAcyclic(root)
        val rootReachable = true
        val leafCount = allNodes.count { it.isLeaf }
        val bridges = allNodes.filter { it.isBridge || it.parents.size > 1 || it.crossLinkChildren.isNotEmpty() }
        val bridgeCount = bridges.size
        val orphanCount = allNodes.count { it.id != root.id && it.parents.isEmpty() }
        
        val validBridgesWithConnections = bridges.filter { b ->
            b.parents.isNotEmpty() && (b.children.isNotEmpty() || b.crossLinkChildren.isNotEmpty())
        }
        val bridgeGroups = validBridgesWithConnections.groupBy { b ->
            (b.parents.map { p -> p.id }.toSet()) to (b.children.map { c -> c.id } + b.crossLinkChildren.map { c -> c.id }).toSet()
        }
        val duplicateBridgeCount = bridgeGroups.values.filter { it.size > 1 }.sumOf { it.size - 1 }
        val residualCount = allNodes.sumOf { it.residualQueries.size }

        val sourceA = bridges.filter { it.parents.size > 1 && !it.id.startsWith("bridge_sourceB_") }
        val sourceB = bridges.filter { it.crossLinkChildren.isNotEmpty() || it.id.startsWith("bridge_sourceB_") }

        val groundTruthMap = mutableMapOf<String, List<String>>()
        fun walkGt(n: GraphNode, visited: MutableSet<String> = mutableSetOf()) {
            if (!visited.add(n.id)) return
            n.queries.forEach { emb ->
                val gt = emb.groundTruthCategory
                if (gt.isNotBlank()) {
                    groundTruthMap[emb.rawText] = listOf(gt)
                }
            }
            n.children.forEach { walkGt(it, visited) }
            n.crossLinkChildren.forEach { walkGt(it, visited) }
        }
        walkGt(root)

        val startGen = System.currentTimeMillis()
        val reportObj = taxonomy.utils.TaxonomyMetrics(root, groundTruthMap).generateReport()
        val endGen = System.currentTimeMillis()
        if (config.diagnostics.enableProfiling) {
            perfTracker.recordTime("construction.finalization.generate_report", endGen - startGen, 1L)
        }

        val configHash = computeConfigHash()
        val commitSha = getGitCommitSha()

        // ─── Extended metrics calculations ───
        val valReport = benchmarkReport?.let { report ->
            try {
                ValidationService.computeMetrics(report, cliConfig.models, "OVERALL")
            } catch (e: Exception) {
                null
            }
        }

        // Soft routing / borderline
        var borderlineCount = 0
        var softDegreeSum = 0
        var entropyGuardCount = 0
        var essSum = 0.0

        val queryToPrimaryLeaf = testQueries.associate { (_, text) ->
            val matched = try {
                runBlocking { taxonomyService.routeQueryToLeaves(text) }
            } catch (t: Throwable) {
                emptyList()
            }
            text to matched.firstOrNull()?.first
        }

        for ((_, text) in testQueries) {
            val matched = try {
                runBlocking { taxonomyService.routeQueryToLeaves(text) }
            } catch (t: Throwable) {
                emptyList()
            }
            
            val isBorderline = matched.size > 1
            if (isBorderline) {
                borderlineCount++
                softDegreeSum += matched.size
            }
            
            val softResult = try {
                runBlocking { arenaService.routeToLeavesSoft(text, null, null) }
            } catch (t: Throwable) {
                null
            }
            
            if (softResult != null) {
                val wSecondary = softResult.secondaryMemberships.values
                val wPrimary = (1.0 - wSecondary.sum()).coerceIn(0.0, 1.0)
                val sumW2 = wPrimary * wPrimary + wSecondary.sumOf { it * it }
                val ess = if (sumW2 > 0.0) 1.0 / sumW2 else 1.0
                essSum += ess
                
                if (isBorderline && wSecondary.isEmpty()) {
                    entropyGuardCount++
                }
            } else {
                essSum += 1.0
            }
        }

        val borderlineRate = if (testQueries.isNotEmpty()) borderlineCount.toDouble() / testQueries.size else 0.0
        val softDegreeMean = if (borderlineCount > 0) softDegreeSum.toDouble() / borderlineCount else 0.0
        val entropyGuardRate = if (borderlineCount > 0) entropyGuardCount.toDouble() / borderlineCount else 0.0
        val softEffSampleSize = essSum

        // Migration / non-vacuity
        var migrationCount = 0
        for ((trueDomain, text) in testQueries) {
            val primaryLeaf = queryToPrimaryLeaf[text]
            val primaryLeafId = primaryLeaf?.id
            val adaptedAnchor = if (primaryLeafId != null) profiles[primaryLeafId]?.dominantDomain else null
            if (adaptedAnchor != null && adaptedAnchor != trueDomain) {
                migrationCount++
            }
        }
        val crossAnchorMigrationRate = if (testQueries.isNotEmpty()) migrationCount.toDouble() / testQueries.size else 0.0

        val jaccards = mutableListOf<Double>()
        for ((leafId, profile) in profiles) {
            val canonicalQueries = testQueries.filter { it.first == profile.dominantDomain }.map { it.second }.toSet()
            val adaptedQueries = testQueries.filter { queryToPrimaryLeaf[it.second]?.id == leafId }.map { it.second }.toSet()
            
            val intersection = canonicalQueries.intersect(adaptedQueries).size
            val union = canonicalQueries.union(adaptedQueries).size
            if (union > 0) {
                jaccards.add(intersection.toDouble() / union.toDouble())
            }
        }
        val canonicalAdaptedJaccard = if (jaccards.isNotEmpty()) {
            val sorted = jaccards.sorted()
            if (sorted.size % 2 == 0) {
                (sorted[sorted.size / 2] + sorted[sorted.size / 2 - 1]) / 2.0
            } else {
                sorted[sorted.size / 2]
            }
        } else 0.0
        val canonicalAdaptedSymDiffMass = 1.0 - canonicalAdaptedJaccard

        // vMF kappa / dOverN summaries
        val leaves = allNodes.filter { it.isLeaf }
        val smallLeaves = leaves.filter { it.dOverN > 10.0 }
        val smallLeafFraction = if (leaves.isNotEmpty()) smallLeaves.size.toDouble() / leaves.size else 0.0
        
        val shrinkageVals = smallLeaves.mapNotNull { leaf ->
            val branchQueries = leaf.getAllQueriesInRegion()
            val n = branchQueries.size
            val d = leaf.sliceDim
            if (n > 0 && d > 0) {
                val projected = branchQueries.map { it.projectTo(d) }
                val sumVec = DoubleArray(d)
                for (vec in projected) for (i in 0 until d) sumVec[i] += vec[i]
                var normVec = 0.0
                for (i in 0 until d) normVec += sumVec[i] * sumVec[i]
                normVec = sqrt(normVec)
                val rBar = normVec / n
                val rawKappa = StatisticsUtils.correctedKappa(rBar, d, n)
                val kappaNew = leaf.vmfKappa
                if (rawKappa > 0.0) {
                    kotlin.math.abs(kappaNew - rawKappa) / rawKappa
                } else null
            } else null
        }
        val kappaShrinkageMean = if (shrinkageVals.isNotEmpty()) shrinkageVals.sum() / shrinkageVals.size else 0.0

        // Delta Rho decomposition
        val rhoCanonicalHard = valReport?.rhoHardCanonical ?: 0.0
        val rhoAdaptedHard = valReport?.rhoHardAdapted ?: 0.0
        val rhoAdaptedSoft = valReport?.rhoSoftAdapted ?: 0.0
        val deltaRhoGeom = valReport?.deltaRhoGeom ?: 0.0
        val deltaRhoSoft = valReport?.deltaRhoSoft ?: 0.0
        val deltaRhoTotal = valReport?.deltaRhoTotal ?: 0.0

        // Judge-readiness
        val leafCounts = leaves.map { it.getAllQueriesInRegion().size }
        val sortedCounts = leafCounts.sorted()
        val selectedNodeP10QueryCount = if (sortedCounts.isNotEmpty()) {
            val idx = (sortedCounts.size * 0.10).toInt().coerceAtMost(sortedCounts.size - 1)
            sortedCounts[idx].toDouble()
        } else 0.0
        
        val starvedThreshold = 10
        val starvedCount = leafCounts.count { it < starvedThreshold }
        val selectedNodeStarvedLeafFraction = if (leafCounts.isNotEmpty()) starvedCount.toDouble() / leafCounts.size else 0.0
        
        val totalQueriesInLeaves = leafCounts.sum().toDouble()
        val selectedNodeLeafBalanceEntropy = if (totalQueriesInLeaves > 0.0) {
            -leafCounts.sumOf { count ->
                val p = count.toDouble() / totalQueriesInLeaves
                if (p > 0.0) p * kotlin.math.log(p, kotlin.math.E) else 0.0
            }
        } else 0.0

        // Bridges
        val sourceBDepth2Count = sourceB.count { it.depth >= 2 }
        val sourceBCountPerDomain = mutableMapOf<String, Int>()
        for (b in sourceB) {
            val targetedDomains = b.crossLinkChildren.mapNotNull { target ->
                profiles[target.id]?.dominantDomain
            }.distinct()
            for (domain in targetedDomains) {
                sourceBCountPerDomain[domain] = (sourceBCountPerDomain[domain] ?: 0) + 1
            }
        }
        val allDomains = profiles.values.map { it.dominantDomain }.distinct()
        val sourceBPerAnchorMean = if (allDomains.isNotEmpty()) {
            allDomains.sumOf { domain -> sourceBCountPerDomain[domain] ?: 0 }.toDouble() / allDomains.size
        } else 0.0
        val bridgeStabilityScore = "NA"

        val totalNodesCount = allNodes.size
        val bridgeRatio = if (totalNodesCount > 0) bridgeCount.toDouble() / totalNodesCount.toDouble() else 0.0

        ledgerFile.parentFile?.mkdirs()
        val fw = java.io.FileWriter(ledgerFile, true)
        fw.buffered().use { writer ->
            if (isNew) {
                writer.write("ConfigHash,CommitSHA,Seed,Condition,Acyclic,RootReachable,OrphanCount,DuplicateBridgeCount,LeafCount,BridgeCount,BridgeRatio,TotalNodes,ResidualCount,WeightedLeafPurity,DendrogramPurity,SphericalSilhouette,TotalDasguptaCost,NormalisedSackinIndex,SourceA_Count,SourceB_Count,RoutingECE,BrierScore,AvgMatchCount,NoMatchRate,MaxAssignmentCapRate,Top1Accuracy,AnyMatchAccuracy,MacroF1,BorderlineRate,SoftDegreeMean,EntropyGuardRate,SoftEffSampleSize,CrossAnchorMigrationRate,CanonicalAdaptedJaccard,CanonicalAdaptedSymDiffMass,RhoCanonicalHard,RhoAdaptedHard,RhoAdaptedSoft,DeltaRhoGeom,DeltaRhoSoft,DeltaRhoTotal,SmallLeafFraction,KappaShrinkageMean,SelectedNodeP10QueryCount,SelectedNodeStarvedLeafFraction,SelectedNodeLeafBalanceEntropy,SourceBBridgeCount,SourceBDepth2Count,SourceBPerAnchorMean,BridgeStabilityScore\n")
            }
            writer.write("$configHash,$commitSha,$currentSeed,$condition,$acyclic,$rootReachable,$orphanCount,$duplicateBridgeCount,$leafCount,$bridgeCount,${"%.4f".format(java.util.Locale.US, bridgeRatio)},$totalNodesCount,$residualCount,${reportObj.weightedLeafPurity},${reportObj.dendrogramPurity},${reportObj.sphericalSilhouette},${reportObj.totalDasguptaCost},${reportObj.normalisedSackin},${sourceA.size},${sourceB.size},${out.ece},$brierVal,${out.avgMatchCountEval},${out.noMatchRate},$maxAssignmentCapRate,${out.top1Accuracy},${out.anyMatchAccuracy},${out.macroF1},$borderlineRate,$softDegreeMean,$entropyGuardRate,$softEffSampleSize,$crossAnchorMigrationRate,$canonicalAdaptedJaccard,$canonicalAdaptedSymDiffMass,$rhoCanonicalHard,$rhoAdaptedHard,$rhoAdaptedSoft,$deltaRhoGeom,$deltaRhoSoft,$deltaRhoTotal,$smallLeafFraction,$kappaShrinkageMean,$selectedNodeP10QueryCount,$selectedNodeStarvedLeafFraction,$selectedNodeLeafBalanceEntropy,${sourceB.size},$sourceBDepth2Count,$sourceBPerAnchorMean,$bridgeStabilityScore\n")
        }
        log.info("Appended condition $condition results to ledger at ${ledgerFile.absolutePath}")
    }

    private fun startFileLogging(filePath: String): ch.qos.logback.core.Appender<ch.qos.logback.classic.spi.ILoggingEvent>? {
        val context = org.slf4j.LoggerFactory.getILoggerFactory() as? ch.qos.logback.classic.LoggerContext ?: return null
        val rootLogger = context.getLogger(ch.qos.logback.classic.Logger.ROOT_LOGGER_NAME) as? ch.qos.logback.classic.Logger ?: return null

        val fileAppender = ch.qos.logback.core.FileAppender<ch.qos.logback.classic.spi.ILoggingEvent>()
        fileAppender.context = context
        fileAppender.name = "SEED_FILE_APPENDER"
        fileAppender.file = filePath
        fileAppender.isAppend = true

        val encoder = ch.qos.logback.classic.encoder.PatternLayoutEncoder()
        encoder.context = context
        encoder.charset = java.nio.charset.StandardCharsets.UTF_8
        encoder.pattern = "%d{HH:mm:ss.SSS} [%-5level] %logger{0} - %msg%n"
        encoder.start()

        fileAppender.encoder = encoder
        fileAppender.start()

        rootLogger.addAppender(fileAppender)
        return fileAppender
    }

    private fun stopFileLogging(appender: ch.qos.logback.core.Appender<ch.qos.logback.classic.spi.ILoggingEvent>?) {
        if (appender == null) return
        val context = org.slf4j.LoggerFactory.getILoggerFactory() as? ch.qos.logback.classic.LoggerContext ?: return
        val rootLogger = context.getLogger(ch.qos.logback.classic.Logger.ROOT_LOGGER_NAME) as? ch.qos.logback.classic.Logger ?: return
        rootLogger.detachAppender(appender)
        appender.stop()
    }

    private fun anchorsOf(
        node: GraphNode,
        cache: MutableMap<String, Set<String>> = HashMap()
    ): Set<String> {
        cache[node.id]?.let { return it }
        val result = LinkedHashSet<String>()
        val seen = HashSet<String>()
        val stack = ArrayDeque<GraphNode>()
        stack.addLast(node)
        while (stack.isNotEmpty()) {
            val cur = stack.removeLast()
            if (!seen.add(cur.id)) continue
            if (cur.depth == 1) {
                (cur.originalCategory ?: cur.label)?.let { result.add(it) }
                // depth-1 is an anchor; do not walk above it
                continue
            }
            for (p in cur.parents) stack.addLast(p)
        }
        cache[node.id] = result
        return result
    }
}

@Serializable
data class ExperimentManifest(
    val runId: String,
    val snapshotId: String,
    val models: List<String>,
    val seed: Long,
    val testRatio: Double,
    val conditionsRun: List<String>,
    val runTimestamp: String,
    val logicalComparisons: Map<String, Int> = emptyMap(),
    val llmJudgeApiCalls: Map<String, Int> = emptyMap()
)
