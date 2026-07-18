package taxonomy.tui.state

import taxonomy.config.EffectiveConfig
import taxonomy.service.DagSnapshot

data class SnapshotUiState(
    val snapshotList: List<DagSnapshot> = emptyList(),
    val selectedSnapshotIdx: Int = 0,

    val isSavingSnapshot: Boolean = false,
    val snapshotDescInput: String = "",

    val isRenamingSnapshot: Boolean = false,
    val renameInput: String = "",

    val isViewingSnapshot: Boolean = false,
    val activeSnapshotId: String? = null,
    val activeSnapshotDescription: String? = null,

    /**
     * The [EffectiveConfig] that was embedded in the currently loaded/viewed snapshot.
     * Null when no snapshot is active (fresh live DAG or nothing loaded yet).
     * Used by the CONFIG panel to display the generation parameters.
     */
    val activeSnapshotConfig: EffectiveConfig? = null,

    /** Transient banner text describing the last auto-save (set after generation completes). */
    val lastAutoSaveMessage: String? = null,

    val lastCopiedId: String? = null,
    val snapshotVersion: Int = 0
) {
    val selectedSnapshotOrNull: DagSnapshot?
        get() = snapshotList.getOrNull(selectedSnapshotIdx)
}
