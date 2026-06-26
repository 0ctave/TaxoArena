package taxonomy.tui.state

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

    val snapshotVersion: Int = 0
) {
    val selectedSnapshotOrNull: DagSnapshot?
        get() = snapshotList.getOrNull(selectedSnapshotIdx)
}