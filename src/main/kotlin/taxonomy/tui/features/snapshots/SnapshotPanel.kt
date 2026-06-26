package taxonomy.tui.features.snapshots

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.layout.width
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.ui.Row
import com.jakewharton.mosaic.ui.Text
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
import taxonomy.service.DagSnapshot
import taxonomy.tui.state.SnapshotUiState

/**
 * Handles intent callbacks to the Controller.
 */
interface SnapshotController {
    fun onSaveSnapshot(description: String)
    fun onRenameSnapshot(id: String, newDescription: String)
    fun onDeleteSnapshot(id: String)
    fun onLoadSnapshot(id: String)
}

/**
 * Top-level Snapshot Hub composable purely driven by state.
 */
@Composable
internal fun SnapshotPanel(
    width: Int,
    height: Int,
    state: SnapshotUiState,
    snapshotList: List<DagSnapshot>,
    controller: SnapshotController // (Optional) Passed for direct button clicks if needed, otherwise handled via KeyDispatcher
) {
    val listWidth = ((width - 3) * 0.46).toInt().coerceAtLeast(30)
    val detailWidth = (width - listWidth - 1).coerceAtLeast(24)

    Row(modifier = Modifier.width(width)) {
        SnapshotArchivePane(
            width = listWidth,
            height = height,
            state = state,
            snapshotList = snapshotList
        )

        Text("│", color = Cyan)

        SnapshotDetailPane(
            width = detailWidth,
            height = height,
            state = state,
            snapshotList = snapshotList
        )
    }
}

@Composable
private fun SnapshotArchivePane(
    width: Int,
    height: Int,
    state: SnapshotUiState,
    snapshotList: List<DagSnapshot>
) {
    // Content extracted from DashboardSnapshots.kt ...
    // ... replaced local state checks with state.isSavingSnapshot, etc.
}

@Composable
private fun SnapshotDetailPane(
    width: Int,
    height: Int,
    state: SnapshotUiState,
    snapshotList: List<DagSnapshot>
) {
    // Content extracted from DashboardSnapshots.kt ...
}