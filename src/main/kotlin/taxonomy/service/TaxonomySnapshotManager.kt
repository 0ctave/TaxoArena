package taxonomy.service

import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Component
import taxonomy.*
import taxonomy.arena.*
import taxonomy.config.*
import taxonomy.controller.*
import taxonomy.dataset.*
import taxonomy.model.*
import taxonomy.operations.*
import taxonomy.prompts.*
import taxonomy.runner.*
import taxonomy.service.*
import taxonomy.tui.*
import taxonomy.utils.*
import java.io.File
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

/**
 * Metrics stored alongside a DAG snapshot.
 *
 * The fields mirror the canonical [taxonomy.model.TaxonomyMetricsData] exactly
 * (plus the snapshot-only [nodesWithJudges]); all defaults are tolerant so old
 * snapshot rows written before a field existed still deserialize. The JSON
 * shape is kept FLAT (unchanged from earlier versions) for backward
 * compatibility — never reorder/rename existing fields.
 *
 * Construction must go through [fromReport] so there is a single place that
 * maps a computed report into persisted metrics. Use [toData] / [fromData] to
 * convert to and from the canonical payload.
 */
@Serializable
data class SnapshotMetrics(
    val totalNodes: Int,
    val leafNodes: Int,
    val crossDomainNodes: Int,
    val maxDepth: Int,
    val totalUniqueQueries: Int,
    val nmi: Double = 0.0,
    val ari: Double = 0.0,
    val dendrogramPurity: Double = 0.0,
    val weightedLeafPurity: Double = 0.0,
    val edgeF1: Double = 0.0,
    val sphericalSilhouette: Double = 0.0,
    val ancestorCorrectRate: Double = 0.0,
    val hPrecision: Double = 0.0,
    val hRecall: Double = 0.0,
    val hF1: Double = 0.0,
    val avgMatchCount: Double = 1.0,
    val contaminationRatio: Double = 0.0,
    val nodesWithJudges: Int = 0,
    val avgLeafDepth: Double = 0.0,
    val residualQueries: Int = 0,
    val residualRatio: Double = 0.0,
    val maxLeafConcentration: Double = 0.0,
    val equilibriumIndex: Double = 0.0,
    val leafDistribEntropy: Double = 0.0,
    val medianLeafAssignments: Double = 0.0,
    /** Average vMF κ per depth level. Defaulted for backward compatibility. */
    val kappaByDepth: Map<Int, Double> = emptyMap(),
    // Publication-grade metrics (PR #49)
    val totalDasguptaCost: Double = 0.0,
    val routingECE: Double = 0.0,
    val tripletAccuracy: Double = 0.0,
    val normalisedSackin: Double = 0.0,
) {
    /** Project onto the canonical metrics payload (drops snapshot-only fields). */
    fun toData(): TaxonomyMetricsData = TaxonomyMetricsData(
        totalNodes            = totalNodes,
        leafNodes             = leafNodes,
        crossDomainNodes      = crossDomainNodes,
        maxDepth              = maxDepth,
        avgLeafDepth          = avgLeafDepth,
        medianLeafAssignments = medianLeafAssignments,
        totalUniqueQueries    = totalUniqueQueries,
        residualQueries       = residualQueries,
        residualRatio         = residualRatio,
        maxLeafConcentration  = maxLeafConcentration,
        contaminationRatio    = contaminationRatio,
        equilibriumIndex      = equilibriumIndex,
        nmi                   = nmi,
        ari                   = ari,
        dendrogramPurity      = dendrogramPurity,
        weightedLeafPurity    = weightedLeafPurity,
        edgeF1                = edgeF1,
        sphericalSilhouette   = sphericalSilhouette,
        ancestorCorrectRate   = ancestorCorrectRate,
        hPrecision            = hPrecision,
        hRecall               = hRecall,
        hF1                   = hF1,
        avgMatchCount         = avgMatchCount,
        kappaByDepth          = kappaByDepth,
        leafDistribEntropy    = leafDistribEntropy,
        totalDasguptaCost     = totalDasguptaCost,
        routingECE            = routingECE,
        tripletAccuracy       = tripletAccuracy,
        normalisedSackin      = normalisedSackin,
    )

    companion object {
        /** Single bridge from the canonical payload to persisted snapshot metrics. */
        fun fromData(data: TaxonomyMetricsData, nodesWithJudges: Int = 0): SnapshotMetrics =
            SnapshotMetrics(
                totalNodes            = data.totalNodes,
                leafNodes             = data.leafNodes,
                crossDomainNodes      = data.crossDomainNodes,
                maxDepth              = data.maxDepth,
                totalUniqueQueries    = data.totalUniqueQueries,
                nmi                   = data.nmi,
                ari                   = data.ari,
                dendrogramPurity      = data.dendrogramPurity,
                weightedLeafPurity    = data.weightedLeafPurity,
                edgeF1                = data.edgeF1,
                sphericalSilhouette   = data.sphericalSilhouette,
                ancestorCorrectRate   = data.ancestorCorrectRate,
                hPrecision            = data.hPrecision,
                hRecall               = data.hRecall,
                hF1                   = data.hF1,
                avgMatchCount         = data.avgMatchCount,
                contaminationRatio    = data.contaminationRatio,
                nodesWithJudges       = nodesWithJudges,
                avgLeafDepth          = data.avgLeafDepth,
                residualQueries       = data.residualQueries,
                residualRatio         = data.residualRatio,
                maxLeafConcentration  = data.maxLeafConcentration,
                equilibriumIndex      = data.equilibriumIndex,
                leafDistribEntropy    = data.leafDistribEntropy,
                medianLeafAssignments = data.medianLeafAssignments,
                kappaByDepth          = data.kappaByDepth,
                totalDasguptaCost     = data.totalDasguptaCost,
                routingECE            = data.routingECE,
                tripletAccuracy       = data.tripletAccuracy,
                normalisedSackin      = data.normalisedSackin,
            )

        /** Single bridge from a freshly computed report to persisted snapshot metrics. */
        fun fromReport(report: TaxonomyMetrics.Report, nodesWithJudges: Int = 0): SnapshotMetrics =
            fromData(report.toData(), nodesWithJudges)
    }
}

@Serializable
data class SnapshotSettings(
    val selectedDomains: List<String>,
    val maxDepth: Int,
    val enableLabeling: Boolean,
    val enableLiveLabeling: Boolean,
    val separationEpsilon: Double,
    val minClusterSize: Int,
    val cosineTau: Double,
    val assignmentGap: Double,
    val emaAlpha: Double,
    val datasetType: DatasetType = DatasetType.MMLU_PRO
) {
    /** Map the legacy persisted settings onto the effective config; unknown fields keep defaults. */
    fun toEffectiveConfig(): EffectiveConfig = EffectiveConfig(
        execution = EffectiveConfig.Execution(
            enableLabeling = enableLabeling,
            enableLiveLabeling = enableLiveLabeling
        ),
        dataset = EffectiveConfig.Dataset(
            datasetType = datasetType,
            selectedDomains = selectedDomains
        ),
        formalism = EffectiveConfig.Formalism(
            maxDepth = maxDepth,
            minClusterSize = minClusterSize,
            separationEpsilon = separationEpsilon,
            cosineTau = cosineTau,
            assignmentGap = assignmentGap,
            emaAlpha = emaAlpha
        )
    )
}

@Serializable
data class DagSnapshot(
    val id: String,
    val timestamp: String,
    val description: String,
    val graph: SerializedGraph,
    val metrics: SnapshotMetrics,
    val settings: SnapshotSettings,
    val logUuid: String? = null,
    val reservedQueries: Map<String, List<String>> = emptyMap(),
    // Full effective config that travels with the snapshot. Null for legacy
    // snapshots saved before config embedding; callers fall back to [settings].
    val config: EffectiveConfig? = null
)

@Serializable
data class DagSnapshotMetadata(
    val id: String,
    val timestamp: String,
    val description: String,
    val metrics: SnapshotMetrics,
    val settings: SnapshotSettings,
    val logUuid: String? = null,
    val reservedQueries: Map<String, List<String>> = emptyMap(),
    val config: EffectiveConfig? = null
)

@Component
class TaxonomySnapshotManager(
    private val config: TaxonomyConfig,
    private val persistence: TaxonomyPersistence
) {
    private val log = LoggerFactory.getLogger("SnapshotManager")
    private val json = Json { 
        prettyPrint = true 
        ignoreUnknownKeys = true
        encodeDefaults = true 
    }
    
    private val dbUrl = if (System.getProperty("java.class.path")?.contains("junit") == true ||
        System.getProperty("org.gradle.test.worker") != null
    ) {
        "jdbc:sqlite:snapshots_test.db?journal_mode=WAL&synchronous=NORMAL&busy_timeout=10000"
    } else {
        "jdbc:sqlite:snapshots.db?journal_mode=WAL&synchronous=NORMAL&busy_timeout=10000"
    }

    private val connection: java.sql.Connection
        get() = java.sql.DriverManager.getConnection(dbUrl).also { conn ->
            conn.autoCommit = true
        }

    /** Decode the embedded effective config, falling back to legacy [SnapshotSettings] for old rows. */
    private fun decodeConfig(configStr: String?, settings: SnapshotSettings): EffectiveConfig =
        if (!configStr.isNullOrEmpty()) {
            try {
                json.decodeFromString<EffectiveConfig>(configStr)
            } catch (e: Exception) {
                settings.toEffectiveConfig()
            }
        } else {
            settings.toEffectiveConfig()
        }

    private fun readConfig(rs: java.sql.ResultSet, settings: SnapshotSettings): EffectiveConfig {
        val configStr = try { rs.getString("config") } catch (e: Exception) { null }
        return decodeConfig(configStr, settings)
    }

    init {
        initDatabase()
        migrateExistingJsonSnapshots()
    }

    private fun initDatabase() {
        try {
            val logsDir = File("snapshots/logs")
            if (!logsDir.exists()) {
                logsDir.mkdirs()
            }
            connection.use { conn ->
                conn.createStatement().use { stmt ->
                    stmt.execute("""
                        CREATE TABLE IF NOT EXISTS snapshots (
                            id TEXT PRIMARY KEY,
                            timestamp TEXT NOT NULL,
                            description TEXT NOT NULL,
                            graph TEXT NOT NULL,
                            metrics TEXT NOT NULL,
                            settings TEXT NOT NULL,
                            log_uuid TEXT,
                            reserved_queries TEXT,
                            config TEXT
                        )
                    """.trimIndent())

                    try {
                        stmt.execute("ALTER TABLE snapshots ADD COLUMN reserved_queries TEXT")
                    } catch (e: Exception) {
                        // Column might already exist, which is fine
                    }

                    try {
                        stmt.execute("ALTER TABLE snapshots ADD COLUMN config TEXT")
                    } catch (e: Exception) {
                        // Column might already exist, which is fine
                    }
                }
            }
        } catch (e: Exception) {
            log.error("Failed to initialize snapshots database", e)
        }
    }

    private fun migrateExistingJsonSnapshots() {
        val isTest = System.getProperty("java.class.path")?.contains("junit") == true || 
                     System.getProperty("org.gradle.test.worker") != null ||
                     System.getenv("SPRING_PROFILES_ACTIVE") == "test"
        if (isTest) {
            log.info("Test environment detected. Skipping JSON snapshot migration.")
            return
        }
        try {
            val snapshotsDir = File("snapshots")
            if (!snapshotsDir.exists()) return
            val jsonFiles = snapshotsDir.listFiles { _, name -> name.endsWith(".json") } ?: return
            if (jsonFiles.isEmpty()) return

            log.info("Migrating ${jsonFiles.size} existing JSON snapshots to snapshots.db...")
            connection.use { conn ->
                conn.prepareStatement("""
                    INSERT OR REPLACE INTO snapshots (id, timestamp, description, graph, metrics, settings, log_uuid, reserved_queries, config)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """).use { stmt ->
                    for (file in jsonFiles) {
                        try {
                            val content = file.readText()
                            val snapshot = json.decodeFromString<DagSnapshot>(content)

                            stmt.setString(1, snapshot.id)
                            stmt.setString(2, snapshot.timestamp)
                            stmt.setString(3, snapshot.description)
                            stmt.setString(4, json.encodeToString(snapshot.graph))
                            stmt.setString(5, json.encodeToString(snapshot.metrics))
                            stmt.setString(6, json.encodeToString(snapshot.settings))
                            stmt.setString(7, snapshot.logUuid)
                            stmt.setString(8, json.encodeToString(snapshot.reservedQueries))
                            stmt.setString(9, snapshot.config?.let { json.encodeToString(it) })
                            stmt.execute()

                            // Delete migrated JSON file
                            file.delete()
                            
                            // Also check if there is an old .tmp file and delete it (it's now stored in db)
                            val tmpFile = File(snapshotsDir, "${snapshot.id}.tmp")
                            if (tmpFile.exists()) {
                                tmpFile.delete()
                            }
                        } catch (e: Exception) {
                            log.error("Failed to migrate snapshot file ${file.name}", e)
                        }
                    }
                }
            }
        } catch (e: Exception) {
            log.error("Error during JSON snapshots migration", e)
        }
    }

    fun listSnapshots(): List<DagSnapshot> {
        val list = mutableListOf<DagSnapshot>()
        try {
            connection.use { conn ->
                conn.createStatement().use { stmt ->
                    stmt.executeQuery("""
                        SELECT id, timestamp, description, metrics, settings, log_uuid, reserved_queries, config
                        FROM snapshots
                        ORDER BY timestamp DESC
                    """.trimIndent()).use { rs ->
                        while (rs.next()) {
                            val id = rs.getString("id")
                            val timestamp = rs.getString("timestamp")
                            val description = rs.getString("description")
                            val metricsStr = rs.getString("metrics")
                            val settingsStr = rs.getString("settings")
                            val logUuid = rs.getString("log_uuid")
                            val reservedQueriesStr = try { rs.getString("reserved_queries") } catch (e: Exception) { null }

                            val metrics = json.decodeFromString<SnapshotMetrics>(metricsStr)
                            val settings = json.decodeFromString<SnapshotSettings>(settingsStr)
                            val reservedQueries = if (reservedQueriesStr.isNullOrEmpty()) {
                                emptyMap()
                            } else {
                                try {
                                    json.decodeFromString<Map<String, List<String>>>(reservedQueriesStr)
                                } catch (e: Exception) {
                                    emptyMap()
                                }
                            }

                            list.add(
                                DagSnapshot(
                                    id = id,
                                    timestamp = timestamp,
                                    description = description,
                                    graph = SerializedGraph(rootId = "", nodes = emptyList()),
                                    metrics = metrics,
                                    settings = settings,
                                    logUuid = logUuid,
                                    reservedQueries = reservedQueries,
                                    config = readConfig(rs, settings)
                                )
                            )
                        }
                    }
                }
            }
        } catch (e: Exception) {
            log.error("Failed to list snapshots from DB", e)
        }
        return list
    }

    /**
     * Effective config of the most recently saved/loaded snapshot, used to restore tunables on
     * startup. Falls back to legacy [SnapshotSettings] for snapshots saved before config embedding.
     */
    fun latestConfig(): EffectiveConfig? {
        try {
            connection.use { conn ->
                conn.createStatement().use { stmt ->
                    stmt.executeQuery("""
                        SELECT settings, config FROM snapshots ORDER BY timestamp DESC LIMIT 1
                    """.trimIndent()).use { rs ->
                        if (rs.next()) {
                            val settings = json.decodeFromString<SnapshotSettings>(rs.getString("settings"))
                            return decodeConfig(rs.getString("config"), settings)
                        }
                    }
                }
            }
        } catch (e: Exception) {
            log.error("Failed to load latest snapshot config from DB", e)
        }
        return null
    }

    fun saveSnapshot(root: GraphNode, description: String, logsToSave: List<String>? = null): DagSnapshot {
        val timestampStr = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"))
        val fileTimestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"))
        val sanitizedDesc = description.replace(Regex("[^a-zA-Z0-9_]"), "_").take(20)
        val snapshotId = "${fileTimestamp}_${sanitizedDesc}"

        val tempFile = File("temp_graph_save.tmp")
        val serializedGraph = try {
            persistence.save(root, tempFile.absolutePath)
        } finally {
            if (tempFile.exists()) tempFile.delete()
        }
        
        val nodesWithJudges = serializedGraph.nodes.count { !it.judgePrompt.isNullOrEmpty() }
        val report = TaxonomyMetrics(root).generateReport()
        val metrics = SnapshotMetrics.fromReport(report, nodesWithJudges)

        val settings = SnapshotSettings(
            selectedDomains = config.dataset.selectedDomains,
            maxDepth = config.formalism.maxDepth,
            enableLabeling = config.execution.enableLabeling,
            enableLiveLabeling = config.execution.enableLiveLabeling,
            separationEpsilon = config.formalism.separationEpsilon,
            minClusterSize = config.formalism.minClusterSize,
            cosineTau = config.formalism.cosineTau,
            assignmentGap = config.formalism.assignmentGap,
            emaAlpha = config.formalism.emaAlpha,
            datasetType = config.dataset.datasetType
        )
        
        val timestampFileStr = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"))
        val datasetName = config.dataset.datasetType.name
        val uuid = "$datasetName/${timestampFileStr}_${java.util.UUID.randomUUID()}"
        val logs = logsToSave ?: synchronized(TuiLogAppender.logs) { TuiLogAppender.logs.toList() }
        writeLogs(uuid, logs)
        
        val reservedFile = File("reserved_test_queries.json")
        val reservedQueries = if (reservedFile.exists()) {
            try {
                val content = reservedFile.readText()
                json.decodeFromString<Map<String, List<String>>>(content)
            } catch (e: Exception) {
                log.error("Failed to read/parse reserved_test_queries.json during save", e)
                emptyMap()
            }
        } else {
            emptyMap()
        }

        val effectiveConfig = config.toEffectiveConfig()

        val snapshot = DagSnapshot(
            id = snapshotId,
            timestamp = timestampStr,
            description = description,
            graph = serializedGraph,
            metrics = metrics,
            settings = settings,
            logUuid = uuid,
            reservedQueries = reservedQueries,
            config = effectiveConfig
        )

        try {
            connection.use { conn ->
                conn.prepareStatement("""
                    INSERT OR REPLACE INTO snapshots (id, timestamp, description, graph, metrics, settings, log_uuid, reserved_queries, config)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """).use { stmt ->
                    stmt.setString(1, snapshotId)
                    stmt.setString(2, timestampStr)
                    stmt.setString(3, description)
                    stmt.setString(4, json.encodeToString(serializedGraph))
                    stmt.setString(5, json.encodeToString(metrics))
                    stmt.setString(6, json.encodeToString(settings))
                    stmt.setString(7, uuid)
                    stmt.setString(8, json.encodeToString(reservedQueries))
                    stmt.setString(9, json.encodeToString(effectiveConfig))
                    stmt.execute()
                }
            }
            log.info("Successfully created and saved snapshot to DB: $snapshotId")
        } catch (e: Exception) {
            log.error("Failed to save snapshot $snapshotId into DB", e)
        }
        
        return snapshot
    }

    fun renameSnapshot(snapshotId: String, newDescription: String): DagSnapshot? {
        try {
            var snapshot: DagSnapshot? = null
            connection.use { conn ->
                conn.prepareStatement("""
                    SELECT timestamp, metrics, settings, log_uuid, reserved_queries, config FROM snapshots WHERE id = ?
                """).use { stmt ->
                    stmt.setString(1, snapshotId)
                    stmt.executeQuery().use { rs ->
                        if (rs.next()) {
                            val timestamp = rs.getString("timestamp")
                            val metrics = json.decodeFromString<SnapshotMetrics>(rs.getString("metrics"))
                            val settings = json.decodeFromString<SnapshotSettings>(rs.getString("settings"))
                            val logUuid = rs.getString("log_uuid")
                            val reservedQueriesStr = try { rs.getString("reserved_queries") } catch (e: Exception) { null }
                            val reservedQueries = if (reservedQueriesStr.isNullOrEmpty()) {
                                emptyMap()
                            } else {
                                try {
                                    json.decodeFromString<Map<String, List<String>>>(reservedQueriesStr)
                                } catch (e: Exception) {
                                    emptyMap()
                                }
                            }
                            snapshot = DagSnapshot(snapshotId, timestamp, newDescription, SerializedGraph("", emptyList()), metrics, settings, logUuid, reservedQueries, readConfig(rs, settings))
                        }
                    }
                }
                
                if (snapshot != null) {
                    conn.prepareStatement("UPDATE snapshots SET description = ? WHERE id = ?").use { stmt ->
                        stmt.setString(1, newDescription)
                        stmt.setString(2, snapshotId)
                        stmt.execute()
                    }
                    return snapshot
                }
            }
        } catch (e: Exception) {
            log.error("Failed to rename snapshot $snapshotId in DB", e)
        }
        return null
    }

    fun updateSnapshot(snapshotId: String, root: GraphNode): DagSnapshot? {
        return try {
            var oldSnapshot: DagSnapshot? = null
            connection.use { conn ->
                conn.prepareStatement("""
                    SELECT timestamp, description, settings, log_uuid, reserved_queries, config FROM snapshots WHERE id = ?
                """).use { stmt ->
                    stmt.setString(1, snapshotId)
                    stmt.executeQuery().use { rs ->
                        if (rs.next()) {
                            val timestamp = rs.getString("timestamp")
                            val description = rs.getString("description")
                            val settings = json.decodeFromString<SnapshotSettings>(rs.getString("settings"))
                            val logUuid = rs.getString("log_uuid")
                            val reservedQueriesStr = try { rs.getString("reserved_queries") } catch (e: Exception) { null }
                            val reservedQueries = if (reservedQueriesStr.isNullOrEmpty()) {
                                emptyMap()
                            } else {
                                try {
                                    json.decodeFromString<Map<String, List<String>>>(reservedQueriesStr)
                                } catch (e: Exception) {
                                    emptyMap()
                                }
                            }
                            oldSnapshot = DagSnapshot(snapshotId, timestamp, description,
                                SerializedGraph("", emptyList()),
                                SnapshotMetrics(0, 0, 0, 0, 0),  // placeholder; real metrics recomputed below
                                settings, logUuid, reservedQueries, readConfig(rs, settings))                        }
                    }
                }
            }
            val oldSnap = oldSnapshot ?: return null
            
            val tempFile = File("temp_graph_update.tmp")
            val serializedGraph = try {
                persistence.save(root, tempFile.absolutePath)
            } finally {
                if (tempFile.exists()) tempFile.delete()
            }

            val nodesWithJudges = serializedGraph.nodes.count { !it.judgePrompt.isNullOrEmpty() }
            val report = TaxonomyMetrics(root).generateReport()
            val metrics = SnapshotMetrics.fromReport(report, nodesWithJudges)
            
            val updatedSnapshot = oldSnap.copy(
                graph = serializedGraph,
                metrics = metrics
            )
            
            connection.use { conn ->
                conn.prepareStatement("""
                    UPDATE snapshots SET graph = ?, metrics = ? WHERE id = ?
                """).use { stmt ->
                    stmt.setString(1, json.encodeToString(serializedGraph))
                    stmt.setString(2, json.encodeToString(metrics))
                    stmt.setString(3, snapshotId)
                    stmt.execute()
                }
            }
            log.info("Successfully updated snapshot $snapshotId in DB with new DAG data.")
            updatedSnapshot
        } catch (e: Exception) {
            log.error("Failed to update snapshot $snapshotId in DB", e)
            null
        }
    }

    fun loadSnapshot(snapshotId: String): GraphNode? {
        try {
            var graphStr: String? = null
            var reservedQueriesStr: String? = null
            connection.use { conn ->
                conn.prepareStatement("SELECT graph, reserved_queries FROM snapshots WHERE id = ?").use { stmt ->
                    stmt.setString(1, snapshotId)
                    stmt.executeQuery().use { rs ->
                        if (rs.next()) {
                            graphStr = rs.getString("graph")
                            reservedQueriesStr = try { rs.getString("reserved_queries") } catch (e: Exception) { null }
                        }
                    }
                }
            }
            val serializedGraphJson = graphStr ?: return null
            val graph = json.decodeFromString<SerializedGraph>(serializedGraphJson)
            
            // Restore reserved_test_queries.json
            if (!reservedQueriesStr.isNullOrEmpty()) {
                try {
                    val reservedFile = File("reserved_test_queries.json")
                    // Validate deserialization to make sure it's valid JSON map
                    val reservedQueries = json.decodeFromString<Map<String, List<String>>>(reservedQueriesStr)
                    val prettyJson = Json { prettyPrint = true }
                    reservedFile.writeText(prettyJson.encodeToString(reservedQueries))
                    log.info("Successfully restored reserved_test_queries.json from snapshot $snapshotId with ${reservedQueries.size} domains.")
                } catch (e: Exception) {
                    log.error("Failed to restore reserved_test_queries.json from snapshot $snapshotId", e)
                }
            } else {
                // If there's no reserved_queries saved, delete the file so it falls back to splitting
                val reservedFile = File("reserved_test_queries.json")
                if (reservedFile.exists()) {
                    reservedFile.delete()
                }
                log.warn("No reserved queries found in snapshot $snapshotId database entry. Cleaned up reserved_test_queries.json.")
            }

            val tempFile = File("temp_graph_load.tmp")
            val root = try {
                tempFile.writeText(json.encodeToString(graph))
                persistence.load(tempFile.absolutePath)
            } finally {
                if (tempFile.exists()) tempFile.delete()
            }
            if (root != null) {
                assignQueryIds(root)
            }
            return root
        } catch (e: Exception) {
            log.error("Failed to load snapshot $snapshotId from DB", e)
            return null
        }
    }

    fun deleteSnapshot(snapshotId: String): Boolean {
        try {
            var logUuid: String? = null
            connection.use { conn ->
                conn.prepareStatement("SELECT log_uuid FROM snapshots WHERE id = ?").use { stmt ->
                    stmt.setString(1, snapshotId)
                    stmt.executeQuery().use { rs ->
                        if (rs.next()) {
                            logUuid = rs.getString("log_uuid")
                        }
                    }
                }
            }
            
            if (logUuid != null) {
                val logFile = File("snapshots/logs/$logUuid.log")
                if (logFile.exists()) {
                    logFile.delete()
                }
            }
            
            var rowsDeleted = 0
            connection.use { conn ->
                conn.prepareStatement("DELETE FROM snapshots WHERE id = ?").use { stmt ->
                    stmt.setString(1, snapshotId)
                    stmt.execute()
                    rowsDeleted = stmt.updateCount
                }
            }
            return rowsDeleted > 0
        } catch (e: Exception) {
            log.error("Failed to delete snapshot $snapshotId from DB", e)
            return false
        }
    }

    private fun writeLogs(uuid: String, lines: List<String>) {
        val logFile = File("snapshots/logs/$uuid.log")
        val parent = logFile.parentFile
        if (parent != null && !parent.exists()) {
            parent.mkdirs()
        }
        logFile.writeText(lines.joinToString("\n"))
    }

    private fun appendLogs(uuid: String, lines: List<String>) {
        val logFile = File("snapshots/logs/$uuid.log")
        val parent = logFile.parentFile
        if (parent != null && !parent.exists()) {
            parent.mkdirs()
        }
        logFile.appendText(if (logFile.exists()) "\n" + lines.joinToString("\n") else lines.joinToString("\n"))
    }

    fun appendLogsToSnapshot(snapshotId: String, logsToAppend: List<String>) {
        try {
            var currentLogUuid: String? = null
            connection.use { conn ->
                conn.prepareStatement("SELECT log_uuid FROM snapshots WHERE id = ?").use { stmt ->
                    stmt.setString(1, snapshotId)
                    stmt.executeQuery().use { rs ->
                        if (rs.next()) {
                            currentLogUuid = rs.getString("log_uuid")
                        }
                    }
                }
            }
            
            if (currentLogUuid == null) {
                val timestampFileStr = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"))
                val datasetName = config.dataset.datasetType.name
                currentLogUuid = "$datasetName/${timestampFileStr}_${java.util.UUID.randomUUID()}"
                connection.use { conn ->
                    conn.prepareStatement("UPDATE snapshots SET log_uuid = ? WHERE id = ?").use { stmt ->
                        stmt.setString(1, currentLogUuid)
                        stmt.setString(2, snapshotId)
                        stmt.execute()
                    }
                }
            }
            appendLogs(currentLogUuid!!, logsToAppend)
        } catch (e: Exception) {
            log.error("Failed to append logs to snapshot $snapshotId in DB", e)
        }
    }

    fun loadSnapshotLogs(uuid: String): List<String> {
        val logFile = File("snapshots/logs/$uuid.log")
        return if (logFile.exists()) {
            logFile.readLines()
        } else {
            emptyList()
        }
    }
}
