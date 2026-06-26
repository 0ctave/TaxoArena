package taxonomy.tui.app

import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import com.jakewharton.mosaic.terminal.Terminal

@Composable
fun TuiApp(
    terminal: Terminal,
    deps: TuiDependencies,
    onQuit: () -> Unit = {},
) {
    val controller = remember { deps.buildController(onQuit) }
    val state by controller.state.collectAsState()
    val subscriptions = rememberTuiSubscriptions(deps)

    BindTuiLifecycle(deps, controller::dispatch, subscriptions)
    BindTerminalInput(terminal, controller::dispatch)

    TuiRouter(
        state = state,
        subscriptions = subscriptions,
        deps = deps,
        dispatch = controller::dispatch
    )
}