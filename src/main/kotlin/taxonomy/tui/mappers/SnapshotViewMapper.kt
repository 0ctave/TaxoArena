package taxonomy.tui.mappers

import taxonomy.config.DatasetType
import taxonomy.service.DagSnapshot
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.Locale

data class SnapshotListRowModel(
    val id: String,
    val description: String,
    val datasetShortName: String,
    val timestamp: String,
    val isViewing: Boolean
)

object SnapshotViewMapper {
    private val formatter = DateTimeFormatter.ofPattern("MM/dd HH:mm").withZone(ZoneId.systemDefault())

    fun mapToListRow(snapshot: DagSnapshot, activeSnapshotId: String?): SnapshotListRowModel {
        return SnapshotListRowModel(
            id = snapshot.id,
            description = snapshot.description.takeIf { it.isNotBlank() } ?: "Unnamed Snapshot",
            datasetShortName = getShortName(snapshot.settings.datasetType),
            timestamp = formatter.format(snapshot.timestamp),
            isViewing = snapshot.id == activeSnapshotId
        )
    }

    private fun getShortName(type: DatasetType): String = when (type) {
        DatasetType.MMLU_PRO -> "MMLU_P"
        DatasetType.MMLU_ORIGINAL -> "MMLU_O"
        DatasetType.ARC -> "ARC"
        DatasetType.TWENTY_NEWSGROUPS -> "20News"
        DatasetType.AG_NEWS -> "AGNews"
    }

    fun formatMetric(value: Double?): String {
        return value?.let { "%.4f".format(Locale.US, it) } ?: "-"
    }
}