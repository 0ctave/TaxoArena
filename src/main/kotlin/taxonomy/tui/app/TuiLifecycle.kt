package taxonomy.tui.app

import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import kotlinx.coroutines.delay
import org.slf4j.LoggerFactory
import taxonomy.tui.controller.TuiEvent
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
    // One-shot self-test: emit a single INFO line on a `taxonomy.*` logger at TUI startup. If this
    // line shows up in the panel the whole pipeline (level filtering → root appender → buffer →
    // Compose recomposition) is proven alive; if it never appears, the empty-state diagnostics
    // below pinpoint where it broke.
    LaunchedEffect(Unit) {
        LoggerFactory.getLogger("taxonomy.tui.bootstrap").info("TUI logging pipeline alive")
    }

    // Clock → SpinnerTick event
    LaunchedEffect(Unit) {
        while (true) {
            delay(120.milliseconds)
            dispatch(TuiEvent.SpinnerTick)
        }
    }

    // Logs are now accumulated directly by TuiLogAppender.append() on the logging
    // thread (see TuiLogAppender), so no UI-side drain is needed. This loop only nudges
    // the scroll/snapshot bookkeeping periodically so the panel tracks the tail.
    LaunchedEffect(Unit) {
        while (true) {
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