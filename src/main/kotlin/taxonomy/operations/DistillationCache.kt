package org.eclipse.lmos.arc.app.taxonomy.operations

import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import java.sql.DriverManager

@Service
class DistillationCache {
    private val log = LoggerFactory.getLogger(DistillationCache::class.java)
    private val dbUrl = "jdbc:sqlite:distillation_cache.db"

    init {
        initDatabase()
    }

    private fun initDatabase() {
        try {
            DriverManager.getConnection(dbUrl).use { conn ->
                conn.createStatement().use { stmt ->
                    stmt.execute("""
                        CREATE TABLE IF NOT EXISTS distillation (
                            query TEXT,
                            domain TEXT,
                            keywords TEXT,
                            PRIMARY KEY (query, domain)
                        )
                    """.trimIndent())
                }
            }
            log.info("SQLite Distillation Cache initialized successfully.")
        } catch (e: Exception) {
            log.error("Failed to initialize Distillation cache database.", e)
        }
    }

    fun get(query: String, domain: String): String? {
        try {
            DriverManager.getConnection(dbUrl).use { conn ->
                conn.prepareStatement("SELECT keywords FROM distillation WHERE query = ? AND domain = ?").use { pstmt ->
                    pstmt.setString(1, query)
                    pstmt.setString(2, domain)
                    val rs = pstmt.executeQuery()
                    if (rs.next()) {
                        return rs.getString("keywords")
                    }
                }
            }
        } catch (e: Exception) {
            log.error("Failed to get from Distillation cache", e)
        }
        return null
    }

    fun put(query: String, domain: String, keywords: String) {
        try {
            DriverManager.getConnection(dbUrl).use { conn ->
                conn.prepareStatement("INSERT OR REPLACE INTO distillation (query, domain, keywords) VALUES (?, ?, ?)").use { pstmt ->
                    pstmt.setString(1, query)
                    pstmt.setString(2, domain)
                    pstmt.setString(3, keywords)
                    pstmt.executeUpdate()
                }
            }
        } catch (e: Exception) {
            log.error("Failed to save to Distillation cache", e)
        }
    }

    fun flush() {
        try {
            DriverManager.getConnection(dbUrl).use { conn ->
                conn.createStatement().use { stmt ->
                    stmt.execute("DELETE FROM distillation")
                }
            }
            log.info("Distillation cache flushed successfully.")
        } catch (e: Exception) {
            log.error("Failed to flush Distillation cache", e)
        }
    }
}
