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
data class LeaderboardGroup(
    val rank: Int,
    val agents: List<AgentRating>
)

@Service
class TaxonomyRankingService {
    private val log = LoggerFactory.getLogger("RankingService")
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
                        CREATE TABLE IF NOT EXISTS agent_ratings (
                            agent_name TEXT,
                            domain TEXT,
                            mu REAL,
                            sigma REAL,
                            PRIMARY KEY (agent_name, domain)
                        )
                    """.trimIndent())

                    stmt.execute("""
                        CREATE TABLE IF NOT EXISTS match_history (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            query TEXT,
                            domain TEXT,
                            winner TEXT,
                            loser TEXT,
                            is_tie INTEGER,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                        )
                    """.trimIndent())
                }
            }
            log.info("SQLite Agent Ratings and Match History schema initialized.")
        } catch (e: Exception) {
            log.error("Failed to initialize database tables for ranking.", e)
        }
    }

    fun getRating(agentName: String, domain: String): AgentRating {
        try {
            withConn { conn ->
                conn.prepareStatement("SELECT mu, sigma FROM agent_ratings WHERE agent_name = ? AND domain = ?").use { pstmt ->
                    pstmt.setString(1, agentName)
                    pstmt.setString(2, domain)
                    val rs = pstmt.executeQuery()
                    if (rs.next()) {
                        return AgentRating(agentName, domain, rs.getDouble("mu"), rs.getDouble("sigma"))
                    }
                }
            }
        } catch (e: Exception) {
            log.error("Failed to fetch rating for $agentName in $domain", e)
        }
        return AgentRating(agentName, domain, initialMu, initialSigma)
    }

    fun saveRating(rating: AgentRating) {
        try {
            withConn { conn ->
                conn.prepareStatement("INSERT OR REPLACE INTO agent_ratings (agent_name, domain, mu, sigma) VALUES (?, ?, ?, ?)").use { pstmt ->
                    pstmt.setString(1, rating.agentName)
                    pstmt.setString(2, rating.domain)
                    pstmt.setDouble(3, rating.mu)
                    pstmt.setDouble(4, rating.sigma)
                    pstmt.executeUpdate()
                }
            }
        } catch (e: Exception) {
            log.error("Failed to save rating for ${rating.agentName} in ${rating.domain}", e)
        }
    }

    fun recordMatch(query: String, domain: String, winner: String, loser: String, isTie: Boolean, confidence: Double = 1.0) {
        try {
            withConn { conn ->
                conn.prepareStatement("INSERT INTO match_history (query, domain, winner, loser, is_tie) VALUES (?, ?, ?, ?, ?)").use { pstmt ->
                    pstmt.setString(1, query)
                    pstmt.setString(2, domain)
                    pstmt.setString(3, winner)
                    pstmt.setString(4, loser)
                    pstmt.setInt(5, if (isTie) 1 else 0)
                    pstmt.executeUpdate()
                }
            }
            
            // Perform Weng-Lin updates
            updateRatings(winner, loser, domain, isTie, confidence)
            
        } catch (e: Exception) {
            log.error("Failed to record match outcome in SQL", e)
        }
    }

    /**
     * Weng-Lin Bayesian updates for pairwise outcomes with confidence weighting.
     */
    private fun updateRatings(winner: String, loser: String, domain: String, isTie: Boolean, confidence: Double) {
        val rW = getRating(winner, domain)
        val rL = getRating(loser, domain)

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

        saveRating(AgentRating(winner, domain, nextMuW, nextSigmaW))
        saveRating(AgentRating(loser, domain, nextMuL, nextSigmaL))

        // Also propagate a fraction of the update to the "global" domain if not already global
        if (domain != "global") {
            updateGlobalAnchorRating(winner, loser, isTie, v, w, c, c2, varW, varL, confidence)
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
        confidence: Double
    ) {
        val rW = getRating(winner, "global")
        val rL = getRating(loser, "global")

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

        saveRating(AgentRating(winner, "global", nextMuW, nextSigmaW))
        saveRating(AgentRating(loser, "global", nextMuL, nextSigmaL))
    }

    /**
     * Reconstructs the pairwise dominance relation using Tarjan's SCC to identify equivalence classes,
     * and performs a topological sort on the condensation graph to yield the rank list.
     */
    fun getLeaderboard(domain: String): List<LeaderboardGroup> {
        val ratings = getAllRatingsInDomain(domain)
        val agents = ratings.map { it.agentName }.distinct()
        if (agents.isEmpty()) return emptyList()

        // 1. Build dominance graph based on match history
        val dominanceAdjacency = buildDominanceGraph(agents, domain)

        // 2. Tarjan's Strongly Connected Components
        val sccs = runTarjanScc(agents, dominanceAdjacency)

        // 3. Topologically sort the condensed components
        val sortedSccs = topologicalSortSccs(sccs, dominanceAdjacency)

        // 4. Map back to ratings sorted within each equivalence class by ordinal
        var currentRank = 1
        return sortedSccs.map { scc ->
            val groupRatings = scc.map { agent -> getRating(agent, domain) }
                .sortedByDescending { it.ordinal }
            val group = LeaderboardGroup(currentRank, groupRatings)
            currentRank += scc.size
            group
        }
    }

    private fun getAllRatingsInDomain(domain: String): List<AgentRating> {
        val list = mutableListOf<AgentRating>()
        try {
            withConn { conn ->
                conn.prepareStatement("SELECT agent_name, mu, sigma FROM agent_ratings WHERE domain = ?").use { pstmt ->
                    pstmt.setString(1, domain)
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

    private fun buildDominanceGraph(agents: List<String>, domain: String): Map<String, List<String>> {
        val dominanceMap = mutableMapOf<String, MutableList<String>>()
        agents.forEach { dominanceMap[it] = mutableListOf() }

        // Fetch match counts between all pairs
        try {
            withConn { conn ->
                val query = """
                    SELECT winner, loser, COUNT(*) as count 
                    FROM match_history 
                    WHERE domain = ? AND is_tie = 0
                    GROUP BY winner, loser
                """.trimIndent()
                conn.prepareStatement(query).use { pstmt ->
                    pstmt.setString(1, domain)
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
