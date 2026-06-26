package taxonomy.tui.app

import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import kotlinx.coroutines.delay
import taxonomy.tui.controller.TuiEvent
import taxonomy.utils.TuiLogAppender
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
        deps.datasetFetcher.onDownloadProgress = { current, total, name ->
            val pct = if (total > 0) current.toFloat() / total else 0f
            dispatch(TuiEvent.DatasetDownloadProgress(pct, "Downloading $name... $current / $total"))
        }
    }

    // Initial snapshot load
    LaunchedEffect(Unit) {
        dispatch(TuiEvent.RefreshSnapshots)
    }
}