package org.eclipse.lmos.arc.app.taxonomy

import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.json.Json
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Component
import java.io.File
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

@Serializable
data class SnapshotMetrics(
    val totalNodes: Int,
    val leafNodes: Int,
    val crossDomainNodes: Int,
    val maxDepth: Int,
    val totalUniqueQueries: Int,
    val totalPathRedundancy: Double,
    val totalLogVolume: Double,
    val relevanceComplianceRatio: Double
)

@Serializable
data class SnapshotSettings(
    val selectedDomains: List<String>,
    val sampleSize: Int = 0,
    val enableMrl: Boolean,
    val fixedMrlDimension: Int,
    val tauFit: Double,
    val tauReparent: Double,
    val tauMerge: Double,
    val maxDepth: Int,
    val collapseMarginalRatio: Double = 0.05,
    val enableLiveLabeling: Boolean = true
)

@Serializable
data class DagSnapshot(
    val id: String,
    val timestamp: String,
    val description: String,
    val graph: SerializedGraph,
    val metrics: SnapshotMetrics,
    val settings: SnapshotSettings
)

@Component
class TaxonomySnapshotManager(
    private val config: TaxonomyConfig,
    private val persistence: TaxonomyPersistence
) {
    private val log = LoggerFactory.getLogger(TaxonomySnapshotManager::class.java)
    private val json = Json { 
        prettyPrint = true 
        ignoreUnknownKeys = true
        encodeDefaults = true 
    }
    
    private val snapshotsDir = File("snapshots")

    init {
        if (!snapshotsDir.exists()) {
            snapshotsDir.mkdirs()
        }
    }

    fun listSnapshots(): List<DagSnapshot> {
        val files = snapshotsDir.listFiles { _, name -> name.endsWith(".json") } ?: emptyArray()
        return files.mapNotNull { file ->
            try {
                json.decodeFromString<DagSnapshot>(file.readText())
            } catch (e: Exception) {
                log.error("Failed to decode snapshot from ${file.name}", e)
                null
            }
        }.sortedByDescending { it.timestamp }
    }

    fun saveSnapshot(root: GraphNode, description: String): DagSnapshot {
        val timestampStr = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"))
        val fileTimestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"))
        val sanitizedDesc = description.replace(Regex("[^a-zA-Z0-9_]"), "_").take(20)
        val snapshotId = "${fileTimestamp}_${sanitizedDesc}"
        
        val tempFile = File(snapshotsDir, "${snapshotId}.tmp")
        persistence.save(root, tempFile.absolutePath)
        
        val serializedGraphJson = tempFile.readText()
        val serializedGraph = json.decodeFromString<SerializedGraph>(serializedGraphJson)
        tempFile.delete()
        
        val report = TaxonomyMetrics(root).generateReport()
        val metrics = SnapshotMetrics(
            totalNodes = report.totalNodes,
            leafNodes = report.leafNodes,
            crossDomainNodes = report.crossDomainNodes,
            maxDepth = report.maxDepth,
            totalUniqueQueries = report.totalUniqueQueries,
            totalPathRedundancy = report.totalPathRedundancy,
            totalLogVolume = report.totalLogVolume,
            relevanceComplianceRatio = report.relevanceComplianceRatio
        )
        
        val settings = SnapshotSettings(
            selectedDomains = config.dataset.selectedDomains,
            sampleSize = 0,
            enableMrl = config.formalism.enableMrl,
            fixedMrlDimension = config.formalism.fixedMrlDimension,
            tauFit = config.formalism.tauFit,
            tauReparent = config.formalism.tauReparent,
            tauMerge = config.formalism.tauMerge,
            maxDepth = config.formalism.maxDepth,
            collapseMarginalRatio = config.formalism.collapseMarginalRatio,
            enableLiveLabeling = config.formalism.enableLiveLabeling
        )
        
        val snapshot = DagSnapshot(
            id = snapshotId,
            timestamp = timestampStr,
            description = description,
            graph = serializedGraph,
            metrics = metrics,
            settings = settings
        )
        
        val snapshotFile = File(snapshotsDir, "${snapshotId}.json")
        snapshotFile.writeText(json.encodeToString(snapshot))
        
        log.info("Successfully created snapshot: ${snapshot.id}")
        return snapshot
    }

    fun renameSnapshot(snapshotId: String, newDescription: String): DagSnapshot? {
        val snapshotFile = File(snapshotsDir, "${snapshotId}.json")
        if (!snapshotFile.exists()) return null
        
        return try {
            val snapshot = json.decodeFromString<DagSnapshot>(snapshotFile.readText())
            val updatedSnapshot = snapshot.copy(description = newDescription)
            snapshotFile.writeText(json.encodeToString(updatedSnapshot))
            log.info("Successfully renamed snapshot $snapshotId to '$newDescription'")
            updatedSnapshot
        } catch (e: Exception) {
            log.error("Failed to rename snapshot $snapshotId", e)
            null
        }
    }

    fun updateSnapshot(snapshotId: String, root: GraphNode): DagSnapshot? {
        val snapshotFile = File(snapshotsDir, "${snapshotId}.json")
        if (!snapshotFile.exists()) return null
        
        return try {
            val oldSnapshot = json.decodeFromString<DagSnapshot>(snapshotFile.readText())
            
            val tempFile = File(snapshotsDir, "${snapshotId}.tmp")
            persistence.save(root, tempFile.absolutePath)
            val serializedGraphJson = tempFile.readText()
            val serializedGraph = json.decodeFromString<SerializedGraph>(serializedGraphJson)
            tempFile.delete()
            
            val report = TaxonomyMetrics(root).generateReport()
            val metrics = SnapshotMetrics(
                totalNodes = report.totalNodes,
                leafNodes = report.leafNodes,
                crossDomainNodes = report.crossDomainNodes,
                maxDepth = report.maxDepth,
                totalUniqueQueries = report.totalUniqueQueries,
                totalPathRedundancy = report.totalPathRedundancy,
                totalLogVolume = report.totalLogVolume,
                relevanceComplianceRatio = report.relevanceComplianceRatio
            )
            
            val updatedSnapshot = oldSnapshot.copy(
                graph = serializedGraph,
                metrics = metrics
            )
            
            snapshotFile.writeText(json.encodeToString(updatedSnapshot))
            log.info("Successfully updated snapshot $snapshotId with new DAG data.")
            updatedSnapshot
        } catch (e: Exception) {
            log.error("Failed to update snapshot $snapshotId", e)
            null
        }
    }

    fun loadSnapshot(snapshotId: String): GraphNode? {
        val snapshotFile = File(snapshotsDir, "${snapshotId}.json")
        if (!snapshotFile.exists()) return null
        
        try {
            val snapshot = json.decodeFromString<DagSnapshot>(snapshotFile.readText())
            val tempFile = File(snapshotsDir, "${snapshotId}.tmp")
            tempFile.writeText(json.encodeToString(snapshot.graph))
            val root = persistence.load(tempFile.absolutePath)
            tempFile.delete()
            if (root != null) {
                assignQueryIds(root)
            }
            return root
        } catch (e: Exception) {
            log.error("Failed to load snapshot $snapshotId", e)
            return null
        }
    }

    fun deleteSnapshot(snapshotId: String): Boolean {
        val snapshotFile = File(snapshotsDir, "${snapshotId}.json")
        return if (snapshotFile.exists()) {
            snapshotFile.delete()
        } else false
    }
}
