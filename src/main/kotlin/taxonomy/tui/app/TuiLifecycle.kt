package taxonomy.tui.app

import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.MutableFloatState
import androidx.compose.runtime.MutableIntState
import androidx.compose.runtime.MutableState
import androidx.compose.runtime.snapshotFlow
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext
import taxonomy.service.DagSnapshot
import taxonomy.tui.components.StartupState
import taxonomy.tui.components.TuiTheme.SPINNER
import taxonomy.utils.TaxonomyMetrics
import taxonomy.utils.TuiLogAppender
import java.time.LocalTime
import kotlin.time.Duration.Companion.milliseconds

/**
 * UI lifecycle binders extracted from the old DashboardView.
 *
 * These are the repeating side-effect loops that should not sit inline
 * in the rendering tree.
 */
@Composable
fun BindTuiLifecycle(
    deps: TuiDependencies,
    dispatch: (TuiEvent) -> Unit,
    subscriptions: TuiSubscriptions,
) {
    // Clock → SpinnerTick event
    LaunchedEffect(Unit) {
        while (true) {
            delay(120.milliseconds)
            dispatch(TuiEvent.SpinnerTick)
        }
    }

    // Log drain → LogsTick
    LaunchedEffect(Unit) {
        while (true) {
            var changed = false
            while (true) {
                val next = TuiLogAppender.logQueue.poll() ?: break
                TuiLogAppender.logs.add(next)
                changed = true
            }
            if (changed) {
                while (TuiLogAppender.logs.size > 2000) TuiLogAppender.logs.removeAt(0)
                TuiLogAppender.logsVersion.value++
            }
            dispatch(TuiEvent.LogsTick)
            delay(50.milliseconds)
        }
    }

    // Tree reset on graph change
    LaunchedEffect(subscriptions.rootNode, subscriptions.graphVersion) {
        // topology expanded-nodes reset is now handled in TuiEffects/CommandController
        // or via a dedicated event; no state to mutate here
    }

    // Dataset download progress registration (one-time)
    LaunchedEffect(Unit) {
        deps.datasetFetcher.onDownloadProgress { current, total, name ->
            val pct = if (total > 0) current.toFloat() / total else 0f
            dispatch(TuiEvent.DatasetDownloadProgress(pct, "Downloading $name... $current / $total"))
        }
    }

    // Initial snapshot load
    LaunchedEffect(Unit) {
        dispatch(TuiEvent.RefreshSnapshots)
    }
}

@Composable
private fun BindClockLifecycle(
    currentTime: MutableState<LocalTime>,
) {
    LaunchedEffect(Unit) {
        while (true) {
            delay(1000.milliseconds)
            currentTime.value = LocalTime.now()
        }
    }
}

@Composable
private fun BindSpinnerLifecycle(
    spinnerTick: MutableIntState,
) {
    LaunchedEffect(Unit) {
        while (true) {
            delay(120.milliseconds)
            spinnerTick.intValue = (spinnerTick.intValue + 1) % SPINNER.size
        }
    }
}

@Composable
private fun BindLogDrainLifecycle() {
    LaunchedEffect(Unit) {
        while (true) {
            var changed = false
            while (true) {
                val next = TuiLogAppender.logQueue.poll() ?: break
                TuiLogAppender.logs.add(next)
                changed = true
            }
            if (changed) {
                while (TuiLogAppender.logs.size > 2000) {
                    TuiLogAppender.logs.removeAt(0)
                }
                TuiLogAppender.logsVersion.value++
            }
            delay(50.milliseconds)
        }
    }
}

@Composable
private fun BindDatasetDownloadLifecycle(
    deps: TuiDependencies,
    state: TuiUiState,
) {
    LaunchedEffect(Unit) {
        deps.datasetFetcher.onDownloadProgress { current, total, name ->
            state.datasetDownloadProgress.floatValue =
                if (total > 0) current.toFloat() / total else 0f
            state.datasetDownloadStatusText.value =
                "Downloading $name... $current / $total"
        }
    }
}

@Composable
private fun BindSnapshotRefreshLifecycle(
    deps: TuiDependencies,
    state: TuiUiState,
) {
    LaunchedEffect(state.snapshotVersion.intValue) {
        val snapshots = withContext(Dispatchers.IO) {
            deps.snapshotManager.listSnapshots()
        }
        state.snapshotList.value = snapshots
    }
}

@Composable
private fun BindSnapshotSelectionClampLifecycle(
    state: TuiUiState,
) {
    LaunchedEffect(state.snapshotList.value) {
        val snapshots = state.snapshotList.value
        state.selectedSnapshotIdx.intValue =
            if (snapshots.isEmpty()) 0
            else state.selectedSnapshotIdx.intValue.coerceIn(0, snapshots.lastIndex)

        val welcomeOptionsCount = 1 + snapshots.size
        state.selectedWelcomeIdx.intValue =
            state.selectedWelcomeIdx.intValue.coerceIn(0, (welcomeOptionsCount - 1).coerceAtLeast(0))
    }
}

@Composable
private fun BindTreeResetLifecycle(
    state: TuiUiState,
    subscriptions: TuiSubscriptions,
) {
    LaunchedEffect(subscriptions.rootNode, subscriptions.graphVersion, state.settingsVersion.intValue) {
        state.expandedNodes.clear()
        subscriptions.rootNode?.let { root ->
            state.expandedNodes[root.id] = true
            root.children.forEach { child ->
                state.expandedNodes[child.id] = false
            }
        }
        state.selectedTreeIdx.intValue = 0
        state.treeScrollOffset.intValue = 0
    }
}

@Composable
private fun BindSnapshotLoadLifecycle(
    deps: TuiDependencies,
    state: TuiUiState,
) {
    LaunchedEffect(state.loadingSnapshotId.value) {
        val snapId = state.loadingSnapshotId.value ?: return@LaunchedEffect

        delay(150.milliseconds)

        val snapshot: DagSnapshot? =
            state.snapshotList.value.find { it.id == snapId }
                ?: withContext(Dispatchers.IO) {
                    deps.snapshotManager.listSnapshots().find { it.id == snapId }
                }

        if (snapshot == null) {
            state.startupState.value = StartupState.WELCOME
            state.loadingSnapshotId.value = null
            return@LaunchedEffect
        }

        val loadedRoot = withContext(Dispatchers.IO) {
            deps.snapshotManager.loadSnapshot(snapshot.id)
        }

        if (loadedRoot == null) {
            deps.log.error("Failed to load snapshot {}", snapshot.id)
            state.startupState.value = StartupState.WELCOME
            state.loadingSnapshotId.value = null
            return@LaunchedEffect
        }

        state.isViewingSnapshot.value = true
        state.activeSnapshotId.value = snapshot.id
        state.activeSnapshotDescription.value = snapshot.description

        deps.taxonomyService.setGraph(loadedRoot)
        deps.config.dataset.selectedDomains = snapshot.settings.selectedDomains
        deps.config.dataset.datasetType = snapshot.settings.datasetType
        deps.config.execution.enableLabeling = snapshot.settings.enableLabeling
        deps.config.execution.enableLiveLabeling = snapshot.settings.enableLiveLabeling
        deps.config.formalism.maxDepth = snapshot.settings.maxDepth
        deps.config.formalism.minClusterSize = snapshot.settings.minClusterSize
        deps.config.formalism.separationEpsilon = snapshot.settings.separationEpsilon
        deps.config.formalism.cosineTau = snapshot.settings.cosineTau
        deps.config.formalism.assignmentGap = snapshot.settings.assignmentGap
        deps.config.formalism.emaAlpha = snapshot.settings.emaAlpha

        state.settingsVersion.intValue++

        val uuid = snapshot.logUuid
        if (uuid != null) {
            val historicalLogs = withContext(Dispatchers.IO) {
                deps.snapshotManager.loadSnapshotLogs(uuid)
            }
            TuiLogAppender.loadHistoricalLogs(historicalLogs)
        } else {
            TuiLogAppender.loadHistoricalLogs(emptyList())
        }

        deps.taxonomyService.clearMetricsHistory()
        val report = TaxonomyMetrics(loadedRoot).generateReport()
        deps.taxonomyService.addIterationMetrics("Loaded Snapshot", report)

        state.startupState.value = StartupState.MAINDASHBOARD
        state.focusedPanel.value = TuiFocusedPanel.TOPOLOGY
        state.loadingSnapshotId.value = null
    }
}