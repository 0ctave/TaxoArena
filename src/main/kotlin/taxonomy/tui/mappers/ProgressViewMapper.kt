package taxonomy.tui.mappers

import taxonomy.model.GenerationProgress

data class ProgressViewModel(
    val title: String,
    val percent: Double,
    val labelText: String,
    val details: String? = null
)

object ProgressViewMapper {

    /** Maps DAG generation progress */
    fun mapGenerationProgress(progress: GenerationProgress?): ProgressViewModel? {
        if (progress == null) return null
        return ProgressViewModel(
            title = "DAG GENERATION",
            percent = (progress.current.toDouble() / progress.total.coerceAtLeast(1)) * 100,
            labelText = "${progress.current} / ${progress.total}",
            details = progress.message
        )
    }

    /** Maps Labeling progress */
    fun mapLabelingProgress(progress: Pair<Int, Int>?): ProgressViewModel? {
        if (progress == null) return null
        return ProgressViewModel(
            title = "LABELING NODES",
            percent = (progress.first.toDouble() / progress.second.coerceAtLeast(1)) * 100,
            labelText = "${progress.first} / ${progress.second}"
        )
    }

    /** Maps Embedding progress */
    fun mapEmbeddingProgress(progress: Pair<Int, Int>?): ProgressViewModel? {
        if (progress == null) return null
        return ProgressViewModel(
            title = "COMPUTING EMBEDDINGS",
            percent = (progress.first.toDouble() / progress.second.coerceAtLeast(1)) * 100,
            labelText = "${progress.first} / ${progress.second}"
        )
    }
}