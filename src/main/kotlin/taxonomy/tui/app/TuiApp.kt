package taxonomy.tui.app

import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import com.jakewharton.mosaic.terminal.Terminal
import kotlinx.coroutines.flow.filterIsInstance
import taxonomy.tui.controller.TuiController
import taxonomy.tui.controller.TuiEvent

@Composable
fun TuiApp(
    terminal: Terminal,
    deps: TuiDependencies
) {
    val controller = remember { deps.buildController() }
    val state by controller.state.collectAsState()
    val subscriptions = rememberTuiSubscriptions(deps)

    BindTuiLifecycle(deps, controller::dispatch, subscriptions)
    BindTerminalInput(terminal, controller::dispatch, state, subscriptions)

    TuiRouter(
        state = state,
        subscriptions = subscriptions,
        deps = deps,
        dispatch = controller::dispatch
    )
}