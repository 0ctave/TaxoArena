package taxonomy.utils

import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import kotlinx.serialization.encodeToString
import org.springframework.stereotype.Service
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.ConcurrentLinkedQueue

@Serializable
data class PerformanceStats(
    val calls: Int,
    val totalMs: Long,
    val avgMs: Double,
    val maxMs: Long,
    val minMs: Long,
    val p50Ms: Long,
    val p95Ms: Long,
    val count: Long = 0L,
    val throughputPerSec: Double = 0.0
)

data class Measurement(val timeMs: Long, val count: Long)

@Service
class TaxonomyPerformanceTracker {
    private val metrics = ConcurrentHashMap<String, ConcurrentLinkedQueue<Measurement>>()
    private val json = Json { prettyPrint = true }

    fun recordTime(phase: String, timeMs: Long, count: Long = 0L) {
        metrics.computeIfAbsent(phase) { ConcurrentLinkedQueue() }.add(Measurement(timeMs, count))
    }

    fun clear() {
        metrics.clear()
    }

    fun getReport(): Map<String, PerformanceStats> {
        return metrics.mapValues { (_, queue) ->
            val times = queue.map { it.timeMs }
            val counts = queue.sumOf { it.count }
            val sorted = times.sorted()
            val totalTime = times.sum()
            val avg = if (times.isNotEmpty()) times.average() else 0.0
            val p50 = if (sorted.isNotEmpty()) sorted[sorted.size / 2] else 0L
            val p95 = if (sorted.isNotEmpty()) sorted[(sorted.size * 0.95).toInt().coerceAtMost(sorted.size - 1)] else 0L
            val throughput = if (totalTime > 0) (counts.toDouble() / (totalTime.toDouble() / 1000.0)) else 0.0
            
            PerformanceStats(
                calls = times.size,
                totalMs = totalTime,
                avgMs = avg,
                maxMs = times.maxOrNull() ?: 0L,
                minMs = times.minOrNull() ?: 0L,
                p50Ms = p50,
                p95Ms = p95,
                count = counts,
                throughputPerSec = throughput
            )
        }
    }

    fun exportJsonReport(file: java.io.File) {
        try {
            val report = getReport()
            val jsonStr = json.encodeToString(report)
            file.writeText(jsonStr, Charsets.UTF_8)
        } catch (e: Exception) {
            // Log warning or ignore
        }
    }

    fun printReport(): String {
        val sb = StringBuilder()
        sb.append("\n========================================================================================================\n")
        sb.append("                               DAG PERFORMANCE REPORT & INSTRUMENTATION                                 \n")
        sb.append("========================================================================================================\n")
        
        val report = getReport()
        if (report.isEmpty()) {
            sb.append("No performance metrics recorded yet.\n")
            sb.append("========================================================================================================\n")
            return sb.toString()
        }

        val totalTime = report.values.sumOf { it.totalMs }

        // Section grouping
        val constructionMetrics = report.filterKeys { 
            it.startsWith("construction.") || it.startsWith("Phase") || it.startsWith("Bootstrap") || it.startsWith("Refit") || it.startsWith("Post-Pass") 
        }
        val arenaMetrics = report.filterKeys { it.startsWith("arena.") }
        val persistenceMetrics = report.filterKeys { it.startsWith("persistence.") }
        
        val constructionTotal = constructionMetrics.values.sumOf { it.totalMs }
        val arenaTotal = arenaMetrics.values.sumOf { it.totalMs }
        val persistenceTotal = persistenceMetrics.values.sumOf { it.totalMs }
        val otherTotal = totalTime - constructionTotal - arenaTotal - persistenceTotal

        // 1. Roll-Up Shares
        sb.append("Top-Level Roll-Up:\n")
        fun formatShareRow(name: String, total: Long) {
            val share = if (totalTime > 0) (total.toDouble() / totalTime) * 100.0 else 0.0
            sb.append("  %-16s : %,10d ms (%5.1f%%)\n".format(name, total, share))
        }
        formatShareRow("Construction", constructionTotal)
        formatShareRow("Arena/Bench", arenaTotal)
        formatShareRow("Persistence", persistenceTotal)
        formatShareRow("Other", otherTotal)
        sb.append("  %-16s : %,10d ms (100.0%%)\n".format("TOTAL TIME", totalTime))
        sb.append("========================================================================================================\n")

        // Helper to print section table
        fun printSectionTable(sectionName: String, secMetrics: Map<String, PerformanceStats>) {
            if (secMetrics.isEmpty()) return
            sb.append("\nSection: $sectionName\n")
            sb.append("+---------------------------------------------+-------+-----------+---------+---------+---------+-----------+-----------+------+\n")
            sb.append("| %-43s | %5s | %9s | %7s | %7s | %7s | %9s | %9s | %4s |\n".format("Phase / Operation", "Calls", "Total(ms)", "Avg(ms)", "p50(ms)", "p95(ms)", "Count", "Unit/s", "Shr"))
            sb.append("+---------------------------------------------+-------+-----------+---------+---------+---------+-----------+-----------+------+\n")
            
            secMetrics.entries.sortedByDescending { it.value.totalMs }.forEach { (name, stats) ->
                val share = if (totalTime > 0) (stats.totalMs.toDouble() / totalTime) * 100.0 else 0.0
                val cleanName = name.substringAfter("construction.").substringAfter("arena.").substringAfter("persistence.").take(43)
                val throughputStr = if (stats.throughputPerSec > 0.0) "%,9.1f".format(stats.throughputPerSec) else ""
                val countStr = if (stats.count > 0L) "%,9d".format(stats.count) else ""
                sb.append("| %-43s | %5d | %9d | %7.1f | %7d | %7d | %9s | %9s | %3.1f%% |\n".format(
                    cleanName, stats.calls, stats.totalMs, stats.avgMs, stats.p50Ms, stats.p95Ms, countStr, throughputStr, share
                ))
            }
            sb.append("+---------------------------------------------+-------+-----------+---------+---------+---------+-----------+-----------+------+\n")
        }

        // 2. Sections Drill-Down
        printSectionTable("CONSTRUCTION DETAILS", constructionMetrics)
        printSectionTable("ARENA/BENCHMARK DETAILS", arenaMetrics)
        printSectionTable("PERSISTENCE DETAILS", persistenceMetrics)

        // 3. Per-Iteration timeline
        val iterMetrics = report.filterKeys { it.contains("@iter=") }
        if (iterMetrics.isNotEmpty()) {
            sb.append("\nConstruction Per-Iteration Step Times:\n")
            val iterPattern = """@iter=(\d+)""".toRegex()
            val iterGroups = iterMetrics.entries.groupBy { (key, _) ->
                iterPattern.find(key)?.groupValues?.get(1)?.toInt() ?: 0
            }.filterKeys { it > 0 }.toSortedMap()

            iterGroups.forEach { (iter, entries) ->
                val totalIterMs = entries.sumOf { it.value.totalMs }
                sb.append("  Iter %2d: %,6d ms".format(iter, totalIterMs))
                val details = entries.joinToString(", ") { (key, stats) ->
                    val opName = key.substringBefore("@").substringAfterLast(".")
                    "$opName=%dms".format(stats.totalMs)
                }
                if (details.isNotEmpty()) {
                    sb.append("  [$details]")
                }
                sb.append("\n")
            }
        }

        sb.append("========================================================================================================\n")
        return sb.toString()
    }
}
