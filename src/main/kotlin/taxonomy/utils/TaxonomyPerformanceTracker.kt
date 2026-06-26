package taxonomy.utils

import kotlinx.serialization.Serializable
import org.springframework.stereotype.Service
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.CopyOnWriteArrayList

@Serializable
data class PerformanceStats(
    val calls: Int,
    val totalMs: Long,
    val avgMs: Double,
    val maxMs: Long,
    val minMs: Long
)

@Service
class TaxonomyPerformanceTracker {
    private val metrics = ConcurrentHashMap<String, CopyOnWriteArrayList<Long>>()

    fun recordTime(phase: String, timeMs: Long) {
        metrics.computeIfAbsent(phase) { CopyOnWriteArrayList() }.add(timeMs)
    }

    fun clear() {
        metrics.clear()
    }

    fun getReport(): Map<String, PerformanceStats> {
        return metrics.mapValues { (_, times) ->
            PerformanceStats(
                calls = times.size,
                totalMs = times.sum(),
                avgMs = if (times.isNotEmpty()) times.average() else 0.0,
                maxMs = times.maxOrNull() ?: 0L,
                minMs = times.minOrNull() ?: 0L
            )
        }
    }

    fun printReport(): String {
        val sb = StringBuilder()
        sb.append("\n+----------------------------------------------------------------------------+\n")
        sb.append("|                       DAG PERFORMANCE REPORT (SPEED METRICS)               |\n")
        sb.append("+----------------------------------------------------------------------------+\n")
        val report = getReport()
        if (report.isEmpty()) {
            sb.append("| No performance metrics recorded yet.                                       |\n")
        } else {
            val totalTime = report.values.sumOf { it.totalMs }
            sb.append("| %-32s | %5s | %10s | %10s | %10s |\n".format("Phase / Operation", "Calls", "Total (ms)", "Avg (ms)", "Share"))
            sb.append("+----------------------------------+-------+------------+------------+------------+\n")
            report.entries.sortedByDescending { it.value.totalMs }.forEach { (phase, stats) ->
                val share = if (totalTime > 0) (stats.totalMs.toDouble() / totalTime) * 100.0 else 0.0
                sb.append("| %-32s | %5d | %10d | %10.1f | %9.1f%% |\n".format(
                    phase.take(32), stats.calls, stats.totalMs, stats.avgMs, share
                ))
            }
            sb.append("+----------------------------------+-------+------------+------------+------------+\n")
            sb.append("| %-32s | %5s | %10d | %10s | %9s |\n".format("TOTAL TIME", "", totalTime, "", "100.0%"))
        }
        sb.append("+----------------------------------------------------------------------------+\n")
        return sb.toString()
    }
}
