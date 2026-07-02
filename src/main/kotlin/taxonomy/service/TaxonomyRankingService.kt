package taxonomy.service

import kotlinx.serialization.Serializable
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
data class LeaderboardGroup(
    val rank: Int,
    val agents: List<AgentRating>
)

@Service
class TaxonomyRankingService {
    private val log = LoggerFactory.getLogger("taxonomy.RankingService")
    private val dbUrl = "jdbc:sqlite:ratings.db?journal_mode=WAL&synchronous=NORMAL&busy_timeout=10000"

    // Initial constant values matching standard OpenSkill (Weng-Lin) defaults
    private val initialMu = 25.0
    private val initialSigma = 8.333
    private val beta = 4.167 // Game outcomes noise (gamma)
    private val drawMargin = 0.1

    // Single held-open connection (WAL mode) guarded by a lock to avoid the cost
    // and contention of opening a new SQLite connection on every call.
    private val dbLock = Any()
    private val connection: Connection by lazy {
        DriverManager.getConnection(dbUrl).also { conn ->
            conn.autoCommit = true
        }
    }

    private inline fun <T> withConn(block: (Connection) -> T): T = synchronized(dbLock) {
        block(connection)
    }

    init {
        initDatabase()
    }

    private fun initDatabase() {
        try {
            withConn { conn ->
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
                    val rsTables = conn.metaData.getTables(null, null, "agent_ratings", null)
                    if (rsTables.next()) {
                        stmt.execute("""
                            INSERT OR IGNORE INTO agent_ratings_v2 (snapshot_id, agent_name, domain, mu, sigma)
                            SELECT 'global', agent_name, domain, mu, sigma FROM agent_ratings
                        """.trimIndent())
                        stmt.execute("DROP TABLE agent_ratings")
                        log.info("Migrated agent_ratings to agent_ratings_v2 and dropped old table.")
                    }

                    stmt.execute("""
                        CREATE TABLE IF NOT EXISTS match_history (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            snapshot_id TEXT,
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
                }
            }
            log.info("SQLite Agent Ratings V2 and Match History schema initialized.")
        } catch (e: Exception) {
            log.error("Failed to initialize database tables for ranking.", e)
        }

        // Migrate existing databases safely by adding new columns if they do not exist
        for (col in listOf("snapshot_id", "model_a", "model_b")) {
            try {
                withConn { conn ->
                    conn.createStatement().use { stmt ->
                        stmt.execute("ALTER TABLE match_history ADD COLUMN $col TEXT")
                    }
                }
            } catch (e: Exception) {
                // Column might already exist, safe to ignore
            }
        }
    }

    fun clearDatabaseForTest() {
        withConn { conn ->
            conn.createStatement().use { stmt ->
                try { stmt.execute("DELETE FROM agent_ratings_v2") } catch (_: Exception) {}
                try { stmt.execute("DELETE FROM match_history") } catch (_: Exception) {}
            }
        }
    }

    fun clearRatings(snapshotId: String) {
        withConn { conn ->
            conn.prepareStatement("DELETE FROM agent_ratings_v2 WHERE snapshot_id = ?").use { pstmt ->
                pstmt.setString(1, snapshotId)
                pstmt.executeUpdate()
            }
            conn.prepareStatement("DELETE FROM match_history WHERE snapshot_id = ?").use { pstmt ->
                pstmt.setString(1, snapshotId)
                pstmt.executeUpdate()
            }
        }
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

    fun getRecordedMatch(snapshotId: String, query: String, modelA: String, modelB: String): CachedMatchResult? {
        try {
            return withConn { conn ->
                val sql = """
                    SELECT winner, loser, is_tie, domain 
                    FROM match_history 
                    WHERE snapshot_id = ? AND query = ? 
                      AND ((model_a = ? AND model_b = ?) OR (model_a = ? AND model_b = ?))
                    LIMIT 1
                """.trimIndent()
                conn.prepareStatement(sql).use { pstmt ->
                    pstmt.setString(1, snapshotId)
                    pstmt.setString(2, query)
                    pstmt.setString(3, modelA)
                    pstmt.setString(4, modelB)
                    pstmt.setString(5, modelB)
                    pstmt.setString(6, modelA)
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
            log.error("Failed to get recorded match for snapshot $snapshotId, query: $query, models: $modelA vs $modelB", e)
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
            val existing = getRecordedMatch(snapshotId, query, modelA, modelB)
            if (existing != null) {
                if (existing.winner == winner && existing.loser == loser && existing.isTie == isTie && existing.domain == domain) {
                    // If identical, do nothing (return)
                    return
                } else {
                    // Update existing record
                    withConn { conn ->
                        val sql = """
                            UPDATE match_history 
                            SET winner = ?, loser = ?, is_tie = ?, domain = ? 
                            WHERE snapshot_id = ? AND query = ? 
                              AND ((model_a = ? AND model_b = ?) OR (model_a = ? AND model_b = ?))
                        """.trimIndent()
                        conn.prepareStatement(sql).use { pstmt ->
                            pstmt.setString(1, winner)
                            pstmt.setString(2, loser)
                            pstmt.setInt(3, if (isTie) 1 else 0)
                            pstmt.setString(4, domain)
                            pstmt.setString(5, snapshotId)
                            pstmt.setString(6, query)
                            pstmt.setString(7, modelA)
                            pstmt.setString(8, modelB)
                            pstmt.setString(9, modelB)
                            pstmt.setString(10, modelA)
                            pstmt.executeUpdate()
                        }
                    }
                    // Update ratings
                    updateRatings(winner, loser, domain, isTie, confidence, snapshotId)
                }
            } else {
                // Insert new record
                withConn { conn ->
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
                }
                // Update ratings
                updateRatings(winner, loser, domain, isTie, confidence, snapshotId)
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
            updateGlobalAnchorRating(winner, loser, isTie, v, w, c, c2, varW, varL, confidence, snapshotId)
        }
    }

    private fun updateGlobalAnchorRating(
        winner: String,
        loser: String,
        isTie: Boolean,
        v: Double,
        w: Double,
        c: Double,
        c2: Double,
        varW: Double,
        varL: Double,
        confidence: Double,
        snapshotId: String = "global"
    ) {
        val rW = getRating(winner, "global", snapshotId)
        val rL = getRating(loser, "global", snapshotId)

        // Propagate updates with a decay factor to simulate global transfer
        val decay = 0.3
        val rawNextMuW = rW.mu + (rW.sigma * rW.sigma / c) * v * decay
        val rawNextMuL = rL.mu - (rL.sigma * rL.sigma / c) * v * decay
        val rawNextSigmaW = Math.sqrt((rW.sigma * rW.sigma * (1.0 - (rW.sigma * rW.sigma / c2) * w * decay)).coerceAtLeast(1e-4))
        val rawNextSigmaL = Math.sqrt((rL.sigma * rL.sigma * (1.0 - (rL.sigma * rL.sigma / c2) * w * decay)).coerceAtLeast(1e-4))

        val nextMuW = rW.mu + confidence * (rawNextMuW - rW.mu)
        val nextMuL = rL.mu + confidence * (rawNextMuL - rL.mu)
        val nextSigmaW = rW.sigma + confidence * (rawNextSigmaW - rW.sigma)
        val nextSigmaL = rL.sigma + confidence * (rawNextSigmaL - rL.sigma)

        saveRating(AgentRating(winner, "global", nextMuW, nextSigmaW), snapshotId)
        saveRating(AgentRating(loser, "global", nextMuL, nextSigmaL), snapshotId)
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
