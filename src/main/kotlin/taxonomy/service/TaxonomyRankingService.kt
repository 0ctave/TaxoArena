package taxonomy.service

import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.decodeFromString
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
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
import java.sql.Connection
import java.sql.DriverManager

@Serializable
data class AgentRating(
    val agentName: String,
    val domain: String,
    val mu: Double = 25.0,
    val sigma: Double = 8.333
) {
    val ordinal: Double
        get() = mu - 2.0 * sigma
}

@Serializable
data class MatchRecord(
    val id: Int,
    val query: String,
    val domain: String,
    val winner: String,
    val loser: String,
    val isTie: Boolean,
    val timestamp: String
)

@Serializable
data class CachedMatchResult(
    val winner: String,
    val loser: String,
    val isTie: Boolean,
    val domain: String
)

@Serializable
data class CachedMatchResultWithQuery(
    val queryKey: String,
    val modelA: String,
    val modelB: String,
    val domain: String,
    val winner: String,
    val loser: String,
    val isTie: Boolean
)

@Serializable
data class LeaderboardGroup(
    val rank: Int,
    val agents: List<AgentRating>
)

@Serializable
data class SavedBenchmarkMetadata(
    val snapshotId: String,
    val models: List<String>,
    val queryLimit: Int,
    val category: String?,
    val confidenceGate: Double,
    val parallelism: Int,
    val updateRankings: Boolean,
    val reservedOnly: Boolean
)

@Service
class TaxonomyRankingService {
    private val log = LoggerFactory.getLogger("taxonomy.RankingService")
    private val dbUrl = "jdbc:sqlite:${System.getProperty("ranking.db.path", "ratings.db")}?journal_mode=WAL&synchronous=NORMAL&busy_timeout=10000&transaction_mode=IMMEDIATE"

    // Initial constant values matching standard OpenSkill (Weng-Lin) defaults
    private val initialMu = 25.0
    private val initialSigma = 8.333
    private val beta = 4.167 // Game outcomes noise (gamma)
    private val drawMargin = 0.1

    // Single held-open connection (WAL mode) guarded by a lock to avoid the cost
    // and contention of opening a new SQLite connection on every call.
    private val dbLock = Any()
    private val connection: Connection by lazy {
        val conn = DriverManager.getConnection(dbUrl)
        try {
            conn.autoCommit = true
            conn.createStatement().use { stmt ->
                stmt.execute("PRAGMA journal_mode=WAL;")
                stmt.execute("PRAGMA synchronous=NORMAL;")
                stmt.execute("PRAGMA busy_timeout=10000;")
            }
        } catch (e: Exception) {
            log.error("Failed to set SQLite PRAGMAs, closing connection: ${e.message}", e)
            try { conn.close() } catch (_: Exception) {}
            throw e
        }
        conn
    }

    @Volatile
    private var dbInitialized = false

    private inline fun <T> withConn(block: (Connection) -> T): T {
        return synchronized(dbLock) {
            ensureDatabaseInitialized()
            var attempts = 0
            val maxRetries = 10
            val delayMs = 100L
            var result: T? = null
            var completed = false
            while (!completed) {
                try {
                    result = block(connection)
                    completed = true
                } catch (e: java.sql.SQLException) {
                    attempts++
                    val msg = e.message ?: ""
                    val isBusy = e.errorCode == 5 || 
                                 msg.contains("busy", ignoreCase = true) ||
                                 msg.contains("locked", ignoreCase = true)
                    if (isBusy && attempts < maxRetries) {
                        log.warn("Database busy/locked (attempt $attempts/$maxRetries). Retrying in ${delayMs}ms...")
                        Thread.sleep(delayMs)
                    } else {
                        throw e
                    }
                }
            }
            @Suppress("UNCHECKED_CAST")
            result as T
        }
    }

    private fun safeRollback(conn: Connection) {
        try {
            if (!conn.autoCommit) {
                conn.rollback()
            }
        } catch (e: java.sql.SQLException) {
            log.debug("Rollback failed (possibly already rolled back by SQLite): ${e.message}")
        }
    }

    init {
        ensureDatabaseInitialized()
        try {
            Runtime.getRuntime().addShutdownHook(Thread {
                try {
                    synchronized(dbLock) {
                        if (!connection.isClosed) {
                            connection.close()
                            log.info("SQLite database connection closed cleanly via shutdown hook.")
                        }
                    }
                } catch (_: Exception) {}
            })
        } catch (_: Exception) {}
    }

    private fun ensureDatabaseInitialized() {
        if (dbInitialized) return
        synchronized(dbLock) {
            if (dbInitialized) return
            try {
                val conn = connection
                conn.createStatement().use { stmt ->
                    stmt.execute("""
                        CREATE TABLE IF NOT EXISTS agent_ratings_v2 (
                            snapshot_id TEXT NOT NULL,
                            agent_name TEXT NOT NULL,
                            domain TEXT NOT NULL,
                            mu REAL,
                            sigma REAL,
                            PRIMARY KEY (snapshot_id, agent_name, domain)
                        )
                    """.trimIndent())

                    // Migrate data if old table exists
                    try {
                        val rsTables = conn.metaData.getTables(null, null, "agent_ratings", null)
                        if (rsTables.next()) {
                            stmt.execute("""
                                INSERT OR IGNORE INTO agent_ratings_v2 (snapshot_id, agent_name, domain, mu, sigma)
                                SELECT 'global', agent_name, domain, mu, sigma FROM agent_ratings
                            """.trimIndent())
                            stmt.execute("DROP TABLE agent_ratings")
                            log.info("Migrated agent_ratings to agent_ratings_v2 and dropped old table.")
                        }
                    } catch (e: Exception) {
                        log.warn("Failed to migrate or drop old agent_ratings table: ${e.message}")
                    }

                    stmt.execute("""
                        CREATE TABLE IF NOT EXISTS match_history (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            snapshot_id TEXT NOT NULL DEFAULT 'global',
                            query TEXT,
                            model_a TEXT,
                            model_b TEXT,
                            domain TEXT,
                            winner TEXT,
                            loser TEXT,
                            is_tie INTEGER,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                        )
                    """.trimIndent())

                    stmt.execute("""
                        CREATE INDEX IF NOT EXISTS idx_match_snapshot_domain_query
                        ON match_history(snapshot_id, domain, query)
                    """.trimIndent())

                    stmt.execute("""
                        CREATE TABLE IF NOT EXISTS node_pair_stats (
                            snapshot_id TEXT NOT NULL,
                            node_id TEXT NOT NULL,
                            model_a TEXT NOT NULL,
                            model_b TEXT NOT NULL,
                            wins_a REAL,
                            wins_b REAL,
                            ties INTEGER,
                            total_comparisons INTEGER,
                            position_flips INTEGER,
                            last_updated INTEGER,
                            PRIMARY KEY (snapshot_id, node_id, model_a, model_b)
                        )
                    """.trimIndent())

                    stmt.execute("""
                        CREATE TABLE IF NOT EXISTS node_bt_states (
                            snapshot_id TEXT NOT NULL,
                            node_id TEXT NOT NULL,
                            bt_scores TEXT NOT NULL,
                            std_errors TEXT NOT NULL,
                            fit_version INTEGER,
                            total_comparisons INTEGER,
                            last_fit_at INTEGER,
                            PRIMARY KEY (snapshot_id, node_id)
                        )
                    """.trimIndent())

                    stmt.execute("""
                        CREATE TABLE IF NOT EXISTS benchmark_query_offsets (
                            snapshot_id TEXT NOT NULL,
                            key_str TEXT NOT NULL,
                            offset_val INTEGER NOT NULL,
                            PRIMARY KEY (snapshot_id, key_str)
                        )
                    """.trimIndent())

                    stmt.execute("""
                        CREATE TABLE IF NOT EXISTS benchmark_metadata (
                            snapshot_id TEXT PRIMARY KEY,
                            models TEXT NOT NULL,
                            query_limit INTEGER NOT NULL,
                            category TEXT,
                            confidence_gate REAL NOT NULL,
                            parallelism INTEGER NOT NULL,
                            update_rankings INTEGER NOT NULL,
                            reserved_only INTEGER NOT NULL
                        )
                    """.trimIndent())
                }

                // Migrate existing databases safely by adding new columns if they do not exist
                for (col in listOf("snapshot_id", "model_a", "model_b")) {
                    try {
                        conn.createStatement().use { stmt ->
                            stmt.execute("ALTER TABLE match_history ADD COLUMN $col TEXT")
                        }
                    } catch (e: Exception) {
                        // Column might already exist, safe to ignore
                    }
                }

                // Run migration to fill snapshot_id on older databases after alter table loop
                try {
                    conn.createStatement().use { s ->
                        s.execute("UPDATE match_history SET snapshot_id = 'global' WHERE snapshot_id IS NULL")
                    }
                } catch (_: Exception) {}

                dbInitialized = true
                log.info("SQLite Agent Ratings V2, Match History, and Bradley-Terry schema initialized.")
            } catch (e: Exception) {
                log.error("Failed to initialize database tables: ${e.message}", e)
            }
        }
    }

    fun clearDatabaseForTest() {
        withConn { conn ->
            conn.createStatement().use { stmt ->
                try { stmt.execute("DELETE FROM agent_ratings_v2") } catch (_: Exception) {}
                try { stmt.execute("DELETE FROM match_history") } catch (_: Exception) {}
                try { stmt.execute("DELETE FROM node_pair_stats") } catch (_: Exception) {}
                try { stmt.execute("DELETE FROM node_bt_states") } catch (_: Exception) {}
            }
        }
    }

    fun clearRatings(snapshotId: String) {
        withConn { conn ->
            val wasAutoCommit = conn.autoCommit
            conn.autoCommit = false
            try {
                listOf(
                    "DELETE FROM agent_ratings_v2 WHERE snapshot_id = ?",
                    "DELETE FROM match_history WHERE snapshot_id = ?",
                    "DELETE FROM node_pair_stats WHERE snapshot_id = ?",
                    "DELETE FROM node_bt_states WHERE snapshot_id = ?",
                    "DELETE FROM benchmark_query_offsets WHERE snapshot_id = ?",
                    "DELETE FROM benchmark_metadata WHERE snapshot_id = ?"
                ).forEach { sql ->
                    try {
                        conn.prepareStatement(sql).use { pstmt ->
                            pstmt.setString(1, snapshotId)
                            pstmt.executeUpdate()
                        }
                    } catch (e: Exception) {
                        // Table node_pair_stats or node_bt_states might not exist yet, but ratings/match_history should
                        if (sql.contains("agent_ratings_v2") || sql.contains("match_history")) {
                            throw e
                        }
                    }
                }
                conn.commit()
            } catch (e: Exception) {
                safeRollback(conn)
                throw e
            } finally {
                conn.autoCommit = wasAutoCommit
            }
        }
    }

    private val json = kotlinx.serialization.json.Json { ignoreUnknownKeys = true }

    fun saveNodePairStats(stats: NodePairStats, snapshotId: String = "global") {
        try {
            withConn { conn ->
                val sql = """
                    INSERT OR REPLACE INTO node_pair_stats 
                    (snapshot_id, node_id, model_a, model_b, wins_a, wins_b, ties, total_comparisons, position_flips, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """.trimIndent()
                conn.prepareStatement(sql).use { pstmt ->
                    pstmt.setString(1, snapshotId)
                    pstmt.setString(2, stats.nodeId)
                    pstmt.setString(3, stats.modelA)
                    pstmt.setString(4, stats.modelB)
                    pstmt.setDouble(5, stats.winsA)
                    pstmt.setDouble(6, stats.winsB)
                    pstmt.setInt(7, stats.ties)
                    pstmt.setInt(8, stats.totalComparisons)
                    pstmt.setInt(9, stats.positionFlips)
                    pstmt.setLong(10, stats.lastUpdated)
                    pstmt.executeUpdate()
                }
            }
        } catch (e: Exception) {
            log.error("Failed to save node pair stats for ${stats.modelA} vs ${stats.modelB} on node ${stats.nodeId}", e)
        }
    }

    fun getNodePairStats(nodeId: String, snapshotId: String = "global"): List<NodePairStats> {
        val list = mutableListOf<NodePairStats>()
        try {
            withConn { conn ->
                conn.prepareStatement("SELECT * FROM node_pair_stats WHERE snapshot_id = ? AND node_id = ?").use { pstmt ->
                    pstmt.setString(1, snapshotId)
                    pstmt.setString(2, nodeId)
                    val rs = pstmt.executeQuery()
                    while (rs.next()) {
                        list.add(
                            NodePairStats(
                                nodeId = rs.getString("node_id"),
                                modelA = rs.getString("model_a"),
                                modelB = rs.getString("model_b"),
                                winsA = rs.getDouble("wins_a"),
                                winsB = rs.getDouble("wins_b"),
                                ties = rs.getInt("ties"),
                                totalComparisons = rs.getInt("total_comparisons"),
                                positionFlips = rs.getInt("position_flips"),
                                lastUpdated = rs.getLong("last_updated")
                            )
                        )
                    }
                }
            }
        } catch (e: Exception) {
            log.error("Failed to get node pair stats for node $nodeId", e)
        }
        return list
    }

    fun getAllNodePairStats(snapshotId: String = "global"): Map<String, List<NodePairStats>> {
        val map = mutableMapOf<String, MutableList<NodePairStats>>()
        try {
            withConn { conn ->
                conn.prepareStatement("SELECT * FROM node_pair_stats WHERE snapshot_id = ?").use { pstmt ->
                    pstmt.setString(1, snapshotId)
                    val rs = pstmt.executeQuery()
                    while (rs.next()) {
                        val nodeId = rs.getString("node_id")
                        map.getOrPut(nodeId) { mutableListOf() }.add(
                            NodePairStats(
                                nodeId = nodeId,
                                modelA = rs.getString("model_a"),
                                modelB = rs.getString("model_b"),
                                winsA = rs.getDouble("wins_a"),
                                winsB = rs.getDouble("wins_b"),
                                ties = rs.getInt("ties"),
                                totalComparisons = rs.getInt("total_comparisons"),
                                positionFlips = rs.getInt("position_flips"),
                                lastUpdated = rs.getLong("last_updated")
                            )
                        )
                    }
                }
            }
        } catch (e: Exception) {
            log.error("Failed to get all node pair stats: ${e.message}", e)
        }
        return map
    }

    fun saveBtState(state: NodeBtState, snapshotId: String = "global") {
        try {
            val scoresJson = json.encodeToString(state.btScores)
            val stdErrorsJson = json.encodeToString(state.stdErrors)
            withConn { conn ->
                val sql = """
                    INSERT OR REPLACE INTO node_bt_states 
                    (snapshot_id, node_id, bt_scores, std_errors, fit_version, total_comparisons, last_fit_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """.trimIndent()
                conn.prepareStatement(sql).use { pstmt ->
                    pstmt.setString(1, snapshotId)
                    pstmt.setString(2, state.nodeId)
                    pstmt.setString(3, scoresJson)
                    pstmt.setString(4, stdErrorsJson)
                    pstmt.setInt(5, state.fitVersion)
                    pstmt.setInt(6, state.totalComparisons)
                    pstmt.setLong(7, state.lastFitAt)
                    pstmt.executeUpdate()
                }
            }
        } catch (e: Exception) {
            log.error("Failed to save BT state for node ${state.nodeId}", e)
        }
    }

    fun getBtState(nodeId: String, snapshotId: String = "global"): NodeBtState? {
        try {
            return withConn { conn ->
                conn.prepareStatement("SELECT * FROM node_bt_states WHERE snapshot_id = ? AND node_id = ?").use { pstmt ->
                    pstmt.setString(1, snapshotId)
                    pstmt.setString(2, nodeId)
                    val rs = pstmt.executeQuery()
                    if (rs.next()) {
                        val scoresMap = json.decodeFromString<Map<String, Double>>(rs.getString("bt_scores"))
                        val stdMap = json.decodeFromString<Map<String, Double>>(rs.getString("std_errors"))
                        NodeBtState(
                            nodeId = rs.getString("node_id"),
                            btScores = scoresMap,
                            stdErrors = stdMap,
                            fitVersion = rs.getInt("fit_version"),
                            totalComparisons = rs.getInt("total_comparisons"),
                            lastFitAt = rs.getLong("last_fit_at")
                        )
                    } else {
                        null
                    }
                }
            }
        } catch (e: Exception) {
            log.error("Failed to get BT state for node $nodeId", e)
            return null
        }
    }

    fun getAllBtStates(snapshotId: String = "global"): Map<String, NodeBtState> {
        val map = mutableMapOf<String, NodeBtState>()
        try {
            withConn { conn ->
                conn.prepareStatement("SELECT * FROM node_bt_states WHERE snapshot_id = ?").use { pstmt ->
                    pstmt.setString(1, snapshotId)
                    val rs = pstmt.executeQuery()
                    while (rs.next()) {
                        val nodeId = rs.getString("node_id")
                        val scoresMap = json.decodeFromString<Map<String, Double>>(rs.getString("bt_scores"))
                        val stdMap = json.decodeFromString<Map<String, Double>>(rs.getString("std_errors"))
                        map[nodeId] = NodeBtState(
                            nodeId = nodeId,
                            btScores = scoresMap,
                            stdErrors = stdMap,
                            fitVersion = rs.getInt("fit_version"),
                            totalComparisons = rs.getInt("total_comparisons"),
                            lastFitAt = rs.getLong("last_fit_at")
                        )
                    }
                }
            }
        } catch (e: Exception) {
            log.error("Failed to get all BT states: ${e.message}", e)
        }
        return map
    }

data class AggregatedLeaderboard(
    val ranks: List<ModelRank>,
    val leafsEligible: Int,
    val leafsTotal: Int,
    val totalComparisons: Int,
    val isReliable: Boolean   // leafsEligible / leafsTotal >= 0.30
)

    fun aggregateLeafScores(
        leafNodeIds: List<String>,
        snapshotId: String = "global",
        minComparisons: Int = 5,
        nodeToQuestions: Map<String, List<Int>> = emptyMap()
    ): AggregatedLeaderboard {
        val allStates = leafNodeIds.mapNotNull { getBtState(it, snapshotId) }
        val eligible = allStates.filter { it.totalComparisons >= minComparisons }

        if (eligible.isEmpty()) return AggregatedLeaderboard(
            emptyList(), 0, leafNodeIds.size, 0, false
        )

        val allModels = eligible.flatMap { it.btScores.keys }.toSet()
        val weightedSum = mutableMapOf<String, Double>()
        val weightTotal = mutableMapOf<String, Double>()

        for (state in eligible) {
            val leafWeight = nodeToQuestions[state.nodeId]?.size?.toDouble() ?: 1.0
            for (model in allModels) {
                val score = state.btScores[model] ?: continue
                val se = state.stdErrors[model]?.takeIf { it < 9.0 } ?: continue
                val w = (1.0 / (se * se)) * leafWeight
                weightedSum[model] = (weightedSum[model] ?: 0.0) + w * score
                weightTotal[model] = (weightTotal[model] ?: 0.0) + w
            }
        }

        val raw = allModels.mapNotNull { model ->
            val wSum = weightTotal[model] ?: return@mapNotNull null
            if (wSum == 0.0) return@mapNotNull null
            model to Pair(weightedSum[model]!! / wSum, 1.0 / kotlin.math.sqrt(wSum))
        }.toMap()

        val mean = if (raw.isNotEmpty()) raw.values.map { it.first }.average() else 0.0
        val ranks = raw.entries
            .map { (model, p) ->
                val score = p.first - mean
                val se = p.second
                ModelRank(model, score, se, 0, score - 2*se, score + 2*se,
                          winsTotal = 0.0,
                          comparisonsTotal = eligible.sumOf { it.totalComparisons })
            }
            .sortedByDescending { it.btScore }
            .mapIndexed { i, r -> r.copy(rank = i + 1) }

        val coverage = eligible.size.toDouble() / leafNodeIds.size
        return AggregatedLeaderboard(ranks, eligible.size, leafNodeIds.size,
                                     eligible.sumOf { it.totalComparisons }, coverage >= 0.30)
    }

    fun getNodeLeaderboard(nodeId: String, snapshotId: String = "global"): List<ModelRank>? {
        val state = getBtState(nodeId, snapshotId) ?: return null
        val pairStats = getNodePairStats(nodeId, snapshotId)
        val models = state.btScores.keys.toList()

        return models.map { modelId ->
            val btScore = state.btScores[modelId] ?: 0.0
            val stdError = state.stdErrors[modelId] ?: Double.MAX_VALUE
            val winsA = pairStats.filter { it.modelA == modelId }.sumOf { it.winsA }
            val winsB = pairStats.filter { it.modelB == modelId }.sumOf { it.winsB }
            val ties = pairStats.filter { it.modelA == modelId || it.modelB == modelId }.sumOf { it.ties }
            val totalWins = winsA + winsB + 0.5 * ties
            val comps = pairStats.filter { it.modelA == modelId || it.modelB == modelId }.sumOf { it.totalComparisons }
            ModelRank(
                modelId = modelId,
                btScore = btScore,
                stdError = stdError,
                rank = 0,
                confidenceIntervalLow = btScore - 2.0 * stdError,
                confidenceIntervalHigh = btScore + 2.0 * stdError,
                winsTotal = totalWins,
                comparisonsTotal = comps
            )
        }.sortedByDescending { it.btScore }
         .mapIndexed { index, modelRank -> modelRank.copy(rank = index + 1) }
    }

    fun getDomainLeaderboard(domainLabel: String, snapshotId: String = "global"): List<ModelRank>? {
        return getNodeLeaderboard(domainLabel, snapshotId)
    }

    fun getPositionFlipRate(nodeId: String, modelA: String, modelB: String, snapshotId: String = "global"): Double {
        val stats = getNodePairStats(nodeId, snapshotId).firstOrNull { 
            (it.modelA == modelA && it.modelB == modelB) || (it.modelA == modelB && it.modelB == modelA) 
        } ?: return 0.0
        return if (stats.totalComparisons > 0) stats.positionFlips.toDouble() / stats.totalComparisons else 0.0
    }

    fun getRating(agentName: String, domain: String, snapshotId: String = "global"): AgentRating {
        try {
            withConn { conn ->
                conn.prepareStatement("SELECT mu, sigma FROM agent_ratings_v2 WHERE snapshot_id = ? AND agent_name = ? AND domain = ?").use { pstmt ->
                    pstmt.setString(1, snapshotId)
                    pstmt.setString(2, agentName)
                    pstmt.setString(3, domain)
                    val rs = pstmt.executeQuery()
                    if (rs.next()) {
                        return AgentRating(agentName, domain, rs.getDouble("mu"), rs.getDouble("sigma"))
                    }
                }
            }
        } catch (e: Exception) {
            log.error("Failed to fetch rating for $agentName in $domain (snapshot: $snapshotId)", e)
        }
        return AgentRating(agentName, domain, initialMu, initialSigma)
    }

    fun saveRating(rating: AgentRating, snapshotId: String = "global") {
        try {
            withConn { conn ->
                conn.prepareStatement("INSERT OR REPLACE INTO agent_ratings_v2 (snapshot_id, agent_name, domain, mu, sigma) VALUES (?, ?, ?, ?, ?)").use { pstmt ->
                    pstmt.setString(1, snapshotId)
                    pstmt.setString(2, rating.agentName)
                    pstmt.setString(3, rating.domain)
                    pstmt.setDouble(4, rating.mu)
                    pstmt.setDouble(5, rating.sigma)
                    pstmt.executeUpdate()
                }
            }
        } catch (e: Exception) {
            log.error("Failed to save rating for ${rating.agentName} in ${rating.domain} (snapshot: $snapshotId)", e)
        }
    }

    fun getRecordedMatch(snapshotId: String, domain: String, query: String, modelA: String, modelB: String): CachedMatchResult? {
        try {
            return withConn { conn ->
                val sql = """
                    SELECT winner, loser, is_tie, domain 
                    FROM match_history 
                    WHERE snapshot_id = ? AND domain = ? AND query = ? 
                      AND ((model_a = ? AND model_b = ?) OR (model_a = ? AND model_b = ?))
                    LIMIT 1
                """.trimIndent()
                conn.prepareStatement(sql).use { pstmt ->
                    pstmt.setString(1, snapshotId)
                    pstmt.setString(2, domain)
                    pstmt.setString(3, query)
                    pstmt.setString(4, modelA)
                    pstmt.setString(5, modelB)
                    pstmt.setString(6, modelB)
                    pstmt.setString(7, modelA)
                    val rs = pstmt.executeQuery()
                    if (rs.next()) {
                        CachedMatchResult(
                            winner = rs.getString("winner"),
                            loser = rs.getString("loser"),
                            isTie = rs.getInt("is_tie") == 1,
                            domain = rs.getString("domain")
                        )
                    } else {
                        null
                    }
                }
            }
        } catch (e: Exception) {
            log.error("Failed to get recorded match for snapshot $snapshotId, domain: $domain, query: $query, models: $modelA vs $modelB", e)
            return null
        }
    }

    fun recordMatch(
        query: String,
        domain: String,
        winner: String,
        loser: String,
        isTie: Boolean,
        confidence: Double = 1.0,
        snapshotId: String = "global",
        modelA: String = winner,
        modelB: String = loser
    ) {
        try {
            withConn { conn ->
                val wasAutoCommit = conn.autoCommit
                conn.autoCommit = false
                try {
                    val existing = getRecordedMatch(snapshotId, domain, query, modelA, modelB)
                    if (existing != null) {
                        if (existing.winner != winner || existing.loser != loser || existing.isTie != isTie || existing.domain != domain) {
                            // Update existing record
                            val sql = """
                                UPDATE match_history 
                                SET winner = ?, loser = ?, is_tie = ? 
                                WHERE snapshot_id = ? AND domain = ? AND query = ? 
                                  AND ((model_a = ? AND model_b = ?) OR (model_a = ? AND model_b = ?))
                            """.trimIndent()
                            conn.prepareStatement(sql).use { pstmt ->
                                pstmt.setString(1, winner)
                                pstmt.setString(2, loser)
                                pstmt.setInt(3, if (isTie) 1 else 0)
                                pstmt.setString(4, snapshotId)
                                pstmt.setString(5, domain)
                                pstmt.setString(6, query)
                                pstmt.setString(7, modelA)
                                pstmt.setString(8, modelB)
                                pstmt.setString(9, modelB)
                                pstmt.setString(10, modelA)
                                pstmt.executeUpdate()
                            }
                            // Update ratings
                            updateRatings(winner, loser, domain, isTie, confidence, snapshotId)
                        }
                    } else {
                        // Insert new record
                        val sql = """
                            INSERT INTO match_history (snapshot_id, query, model_a, model_b, domain, winner, loser, is_tie) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """.trimIndent()
                        conn.prepareStatement(sql).use { pstmt ->
                            pstmt.setString(1, snapshotId)
                            pstmt.setString(2, query)
                            pstmt.setString(3, modelA)
                            pstmt.setString(4, modelB)
                            pstmt.setString(5, domain)
                            pstmt.setString(6, winner)
                            pstmt.setString(7, loser)
                            pstmt.setInt(8, if (isTie) 1 else 0)
                            pstmt.executeUpdate()
                        }
                        // Update ratings
                        updateRatings(winner, loser, domain, isTie, confidence, snapshotId)
                    }

                    conn.commit()
                } catch (e: Exception) {
                    log.warn("Error inside recordMatch transaction block: ${e.message}", e)
                    safeRollback(conn)
                    throw e
                } finally {
                    conn.autoCommit = wasAutoCommit
                }
            }
        } catch (e: Exception) {
            log.error("Failed to record match outcome in SQL", e)
        }
    }

    /**
     * Weng-Lin Bayesian updates for pairwise outcomes with confidence weighting.
     */
    private fun updateRatings(winner: String, loser: String, domain: String, isTie: Boolean, confidence: Double, snapshotId: String = "global") {
        val rW = getRating(winner, domain, snapshotId)
        val rL = getRating(loser, domain, snapshotId)

        val varW = rW.sigma * rW.sigma
        val varL = rL.sigma * rL.sigma
        val c2 = varW + varL + 2.0 * beta * beta
        val c = Math.sqrt(c2)
        val d = rW.mu - rL.mu

        var v = 0.0
        var w = 0.0

        if (isTie) {
            val t1 = (-drawMargin - d) / c
            val t2 = (drawMargin - d) / c
            val denom = cdf(t2) - cdf(t1)
            if (denom > 1e-9) {
                v = (pdf(t1) - pdf(t2)) / denom
                w = (t1 * pdf(t1) - t2 * pdf(t2)) / denom + v * v
            }
        } else {
            val t = d / c
            val cdfVal = cdf(t)
            if (cdfVal > 1e-9) {
                v = pdf(t) / cdfVal
                w = v * (v + t)
            }
        }

        val rawNextMuW = rW.mu + (varW / c) * v
        val rawNextMuL = rL.mu - (varL / c) * v
        val rawNextSigmaW = Math.sqrt((varW * (1.0 - (varW / c2) * w)).coerceAtLeast(1e-4))
        val rawNextSigmaL = Math.sqrt((varL * (1.0 - (varL / c2) * w)).coerceAtLeast(1e-4))

        // Confidence-weighted interpolation
        val nextMuW = rW.mu + confidence * (rawNextMuW - rW.mu)
        val nextMuL = rL.mu + confidence * (rawNextMuL - rL.mu)
        val nextSigmaW = rW.sigma + confidence * (rawNextSigmaW - rW.sigma)
        val nextSigmaL = rL.sigma + confidence * (rawNextSigmaL - rL.sigma)

        saveRating(AgentRating(winner, domain, nextMuW, nextSigmaW), snapshotId)
        saveRating(AgentRating(loser, domain, nextMuL, nextSigmaL), snapshotId)

        // Also propagate a fraction of the update to the "global" domain if not already global
        if (domain != "global") {
            updateGlobalAnchorRating(winner, loser, isTie, confidence, snapshotId)
        }
    }

    private fun updateGlobalAnchorRating(
        winner: String,
        loser: String,
        isTie: Boolean,
        confidence: Double,
        snapshotId: String = "global"
    ) {
        val decay = 0.3
        updateRatings(winner, loser, "global", isTie, confidence * decay, snapshotId)
    }

    /**
     * Reconstructs the pairwise dominance relation using Tarjan's SCC to identify equivalence classes,
     * and performs a topological sort on the condensation graph to yield the rank list.
     */
    fun getLeaderboard(domain: String, snapshotId: String = "global"): List<LeaderboardGroup> {
        val ratings = getAllRatingsInDomain(domain, snapshotId)
        val agents = ratings.map { it.agentName }.distinct()
        if (agents.isEmpty()) return emptyList()

        // 1. Build dominance graph based on match history
        val dominanceAdjacency = buildDominanceGraph(agents, domain, snapshotId)

        // 2. Tarjan's Strongly Connected Components
        val sccs = runTarjanScc(agents, dominanceAdjacency)

        // 3. Topologically sort the condensed components
        val sortedSccs = topologicalSortSccs(sccs, dominanceAdjacency)

        // 4. Map back to ratings sorted within each equivalence class by ordinal
        var currentRank = 1
        return sortedSccs.map { scc ->
            val groupRatings = scc.map { agent -> getRating(agent, domain, snapshotId) }
                .sortedByDescending { it.ordinal }
            val group = LeaderboardGroup(currentRank, groupRatings)
            currentRank += scc.size
            group
        }
    }

    private fun getAllRatingsInDomain(domain: String, snapshotId: String = "global"): List<AgentRating> {
        val list = mutableListOf<AgentRating>()
        try {
            withConn { conn ->
                conn.prepareStatement("SELECT agent_name, mu, sigma FROM agent_ratings_v2 WHERE snapshot_id = ? AND domain = ?").use { pstmt ->
                    pstmt.setString(1, snapshotId)
                    pstmt.setString(2, domain)
                    val rs = pstmt.executeQuery()
                    while (rs.next()) {
                        list.add(AgentRating(rs.getString("agent_name"), domain, rs.getDouble("mu"), rs.getDouble("sigma")))
                    }
                }
            }
        } catch (e: Exception) {
            log.error("Failed to read ratings in $domain", e)
        }
        return list
    }

    private fun buildDominanceGraph(agents: List<String>, domain: String, snapshotId: String = "global"): Map<String, List<String>> {
        val dominanceMap = mutableMapOf<String, MutableList<String>>()
        agents.forEach { dominanceMap[it] = mutableListOf() }

        // Fetch match counts between all pairs
        try {
            withConn { conn ->
                val query = """
                    SELECT winner, loser, COUNT(*) as count 
                    FROM match_history 
                    WHERE snapshot_id = ? AND domain = ? AND is_tie = 0
                    GROUP BY winner, loser
                """.trimIndent()
                conn.prepareStatement(query).use { pstmt ->
                    pstmt.setString(1, snapshotId)
                    pstmt.setString(2, domain)
                    val rs = pstmt.executeQuery()
                    val matchCounts = mutableMapOf<Pair<String, String>, Int>()
                    while (rs.next()) {
                        val w = rs.getString("winner")
                        val l = rs.getString("loser")
                        val cnt = rs.getInt("count")
                        matchCounts[w to l] = cnt
                    }

                    // For every pair of agents, evaluate if one dominates the other
                    for (i in agents.indices) {
                        for (j in i + 1 until agents.size) {
                            val a = agents[i]
                            val b = agents[j]
                            val wAB = matchCounts[a to b] ?: 0
                            val wBA = matchCounts[b to a] ?: 0

                            if (wAB > wBA) {
                                dominanceMap[a]?.add(b)
                            } else if (wBA > wAB) {
                                dominanceMap[b]?.add(a)
                            }
                        }
                    }
                }
            }
        } catch (e: Exception) {
            log.error("Failed to build dominance graph", e)
        }
        return dominanceMap
    }

    private fun runTarjanScc(vertices: List<String>, adjacency: Map<String, List<String>>): List<List<String>> {
        val tarjan = TarjanScc(vertices, adjacency)
        return tarjan.run()
    }

    private fun topologicalSortSccs(sccs: List<List<String>>, adjacency: Map<String, List<String>>): List<List<String>> {
        val sccMap = mutableMapOf<String, Int>()
        sccs.forEachIndexed { sccIdx, scc ->
            scc.forEach { agent -> sccMap[agent] = sccIdx }
        }

        val numSccs = sccs.size
        val sccAdj = MutableList(numSccs) { mutableSetOf<Int>() }
        val inDegree = IntArray(numSccs)

        adjacency.forEach { (u, neighbors) ->
            val uScc = sccMap[u] ?: return@forEach
            neighbors.forEach { v ->
                val vScc = sccMap[v] ?: return@forEach
                if (uScc != vScc) {
                    if (sccAdj[uScc].add(vScc)) {
                        inDegree[vScc]++
                    }
                }
            }
        }

        val queue = mutableListOf<Int>()
        for (i in 0 until numSccs) {
            if (inDegree[i] == 0) {
                queue.add(i)
            }
        }

        val sortedSccIndices = mutableListOf<Int>()
        while (queue.isNotEmpty()) {
            val u = queue.removeAt(0)
            sortedSccIndices.add(u)
            sccAdj[u].forEach { v ->
                inDegree[v]--
                if (inDegree[v] == 0) {
                    queue.add(v)
                }
            }
        }

        val result = mutableListOf<List<String>>()
        sortedSccIndices.forEach { idx ->
            result.add(sccs[idx])
        }

        for (i in 0 until numSccs) {
            if (i !in sortedSccIndices) {
                result.add(sccs[i])
            }
        }

        return result
    }

    // ─── Normal Distribution Mathematics ───
    private fun pdf(x: Double): Double = Math.exp(-x * x / 2.0) / Math.sqrt(2.0 * Math.PI)

    private fun cdf(x: Double): Double {
        return 0.5 * (1.0 + erf(x / Math.sqrt(2.0)))
    }

    private fun erf(z: Double): Double {
        val t = 1.0 / (1.0 + 0.3275911 * Math.abs(z))
        val a1 = 0.254829592
        val a2 = -0.284496736
        val a3 = 1.421413741
        val a4 = -1.453152027
        val a5 = 1.061405429
        val ans = 1.0 - (((((a5 * t + a4) * t + a3) * t + a2) * t + a1) * t) * Math.exp(-z * z)
        return if (z >= 0) ans else -ans
    }

    fun savePairQueryOffsets(offsets: Map<String, Int>, snapshotId: String) {
        synchronized(dbLock) {
            try {
                connection.prepareStatement("""
                    INSERT OR REPLACE INTO benchmark_query_offsets (snapshot_id, key_str, offset_val)
                    VALUES (?, ?, ?)
                """).use { stmt ->
                    offsets.forEach { (key, value) ->
                        stmt.setString(1, snapshotId)
                        stmt.setString(2, key)
                        stmt.setInt(3, value)
                        stmt.addBatch()
                    }
                    stmt.executeBatch()
                }
            } catch (e: java.sql.SQLException) {
                log.error("Failed to save pair query offsets for snapshot $snapshotId", e)
            }
        }
    }

    fun getPairQueryOffsets(snapshotId: String): Map<String, Int> {
        synchronized(dbLock) {
            val result = mutableMapOf<String, Int>()
            try {
                connection.prepareStatement("""
                    SELECT key_str, offset_val FROM benchmark_query_offsets WHERE snapshot_id = ?
                """).use { stmt ->
                    stmt.setString(1, snapshotId)
                    stmt.executeQuery().use { rs ->
                        while (rs.next()) {
                            result[rs.getString("key_str")] = rs.getInt("offset_val")
                        }
                    }
                }
            } catch (e: java.sql.SQLException) {
                log.error("Failed to load pair query offsets for snapshot $snapshotId", e)
            }
            return result
        }
    }

    fun getAllRecordedMatches(snapshotId: String): List<CachedMatchResultWithQuery> {
        val list = mutableListOf<CachedMatchResultWithQuery>()
        try {
            withConn { conn ->
                val sql = """
                    SELECT query, model_a, model_b, domain, winner, loser, is_tie 
                    FROM match_history 
                    WHERE snapshot_id = ?
                """.trimIndent()
                conn.prepareStatement(sql).use { pstmt ->
                    pstmt.setString(1, snapshotId)
                    val rs = pstmt.executeQuery()
                    while (rs.next()) {
                        list.add(
                            CachedMatchResultWithQuery(
                                queryKey = rs.getString("query"),
                                modelA = rs.getString("model_a"),
                                modelB = rs.getString("model_b"),
                                domain = rs.getString("domain"),
                                winner = rs.getString("winner"),
                                loser = rs.getString("loser"),
                                isTie = rs.getInt("is_tie") == 1
                            )
                        )
                    }
                }
            }
        } catch (e: Exception) {
            log.error("Failed to read all recorded matches for snapshot $snapshotId", e)
        }
        return list
    }

    fun saveBenchmarkMetadata(meta: SavedBenchmarkMetadata) {
        try {
            withConn { conn ->
                val sql = """
                    INSERT OR REPLACE INTO benchmark_metadata (
                        snapshot_id, models, query_limit, category, confidence_gate, parallelism, update_rankings, reserved_only
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """.trimIndent()
                conn.prepareStatement(sql).use { pstmt ->
                    pstmt.setString(1, meta.snapshotId)
                    pstmt.setString(2, json.encodeToString(meta.models))
                    pstmt.setInt(3, meta.queryLimit)
                    pstmt.setString(4, meta.category)
                    pstmt.setDouble(5, meta.confidenceGate)
                    pstmt.setInt(6, meta.parallelism)
                    pstmt.setInt(7, if (meta.updateRankings) 1 else 0)
                    pstmt.setInt(8, if (meta.reservedOnly) 1 else 0)
                    pstmt.executeUpdate()
                }
            }
        } catch (e: Exception) {
            log.error("Failed to save benchmark metadata for snapshot ${meta.snapshotId}", e)
        }
    }

    fun getBenchmarkMetadata(snapshotId: String): SavedBenchmarkMetadata? {
        try {
            return withConn { conn ->
                val sql = """
                    SELECT models, query_limit, category, confidence_gate, parallelism, update_rankings, reserved_only 
                    FROM benchmark_metadata 
                    WHERE snapshot_id = ?
                    LIMIT 1
                """.trimIndent()
                conn.prepareStatement(sql).use { pstmt ->
                    pstmt.setString(1, snapshotId)
                    val rs = pstmt.executeQuery()
                    if (rs.next()) {
                        val modelsStr = rs.getString("models")
                        val models = json.decodeFromString<List<String>>(modelsStr)
                        SavedBenchmarkMetadata(
                            snapshotId = snapshotId,
                            models = models,
                            queryLimit = rs.getInt("query_limit"),
                            category = rs.getString("category"),
                            confidenceGate = rs.getDouble("confidence_gate"),
                            parallelism = rs.getInt("parallelism"),
                            updateRankings = rs.getInt("update_rankings") == 1,
                            reservedOnly = rs.getInt("reserved_only") == 1
                        )
                    } else {
                        null
                    }
                }
            }
        } catch (e: Exception) {
            log.error("Failed to get benchmark metadata for snapshot $snapshotId", e)
            return null
        }
    }
}

private class TarjanScc(
    private val vertices: List<String>,
    private val adjacencyList: Map<String, List<String>>
) {
    private var index = 0
    private val stack = mutableListOf<String>()
    private val inStack = mutableSetOf<String>()
    private val indices = mutableMapOf<String, Int>()
    private val lowlinks = mutableMapOf<String, Int>()
    private val sccs = mutableListOf<List<String>>()

    fun run(): List<List<String>> {
        for (v in vertices) {
            if (!indices.containsKey(v)) {
                strongconnect(v)
            }
        }
        return sccs
    }

    private fun strongconnect(v: String) {
        indices[v] = index
        lowlinks[v] = index
        index++
        stack.add(v)
        inStack.add(v)

        val neighbors = adjacencyList[v] ?: emptyList()
        for (w in neighbors) {
            if (!indices.containsKey(w)) {
                strongconnect(w)
                lowlinks[v] = minOf(lowlinks[v]!!, lowlinks[w]!!)
            } else if (inStack.contains(w)) {
                lowlinks[v] = minOf(lowlinks[v]!!, indices[w]!!)
            }
        }

        if (lowlinks[v] == indices[v]) {
            val scc = mutableListOf<String>()
            while (true) {
                val w = stack.removeAt(stack.size - 1)
                inStack.remove(w)
                scc.add(w)
                if (w == v) break
            }
            sccs.add(scc)
        }
    }
}
