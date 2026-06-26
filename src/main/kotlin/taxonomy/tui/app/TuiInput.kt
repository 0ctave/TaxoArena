package taxonomy.tui.app

import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import com.jakewharton.mosaic.terminal.KeyboardEvent
import com.jakewharton.mosaic.terminal.MouseEvent
import com.jakewharton.mosaic.terminal.ResizeEvent
import com.jakewharton.mosaic.terminal.Terminal
import taxonomy.tui.controller.MouseButton
import taxonomy.tui.controller.TuiEvent
import taxonomy.tui.controller.WheelDirection

/**
 * Bridges the Mosaic [Terminal] event/size streams onto the MVI dispatch
 * channel. Terminal concerns stay isolated here; the controller only ever
 * sees [TuiEvent]s.
 */
@Composable
fun BindTerminalInput(
    terminal: Terminal,
    dispatch: (TuiEvent) -> Unit,
) {
    LaunchedEffect(terminal) {
        terminal.state.size.collect { size ->
            dispatch(TuiEvent.Resize(size.columns, size.rows))
        }
    }

    LaunchedEffect(terminal) {
        for (event in terminal.events) {
            when (event) {
                is KeyboardEvent -> mapKeyboard(event)?.let(dispatch)
                is MouseEvent -> mapMouse(event)?.let(dispatch)
                is ResizeEvent -> dispatch(TuiEvent.Resize(event.columns, event.rows))
                else -> Unit
            }
        }
    }
}

private fun mapKeyboard(event: KeyboardEvent): TuiEvent? {
    if (event.eventType == KeyboardEvent.EventTypeRelease) return null

    // Global quit: Ctrl-C (raw-mode delivers it as codepoint 3, or as Ctrl + 'c'/'q').
    val ctrl = (event.modifiers and KeyboardEvent.ModifierCtrl) != 0
    if (event.codepoint == 3 || (ctrl && (event.codepoint == 'c'.code || event.codepoint == 'q'.code))) {
        return TuiEvent.QuitRequested
    }

    val key = when (event.codepoint) {
        KeyboardEvent.Up -> "arrowup"
        KeyboardEvent.Down -> "arrowdown"
        KeyboardEvent.Left -> "arrowleft"
        KeyboardEvent.Right -> "arrowright"
        KeyboardEvent.PageUp -> "pageup"
        KeyboardEvent.PageDown -> "pagedown"
        KeyboardEvent.Home -> "home"
        KeyboardEvent.End -> "end"
        KeyboardEvent.Insert -> "insert"
        KeyboardEvent.Delete -> "delete"
        13, 10 -> "enter"
        27 -> "escape"
        9 -> "tab"
        8, 127 -> "backspace"
        32 -> " "
        else -> {
            val text = event.text
            if (!text.isNullOrEmpty()) text
            else String(Character.toChars(event.codepoint))
        }
    }
    return TuiEvent.KeyPressed(key)
}

private fun mapMouse(event: MouseEvent): TuiEvent? {
    val button = when (event.button) {
        MouseEvent.Button.Right -> MouseButton.Right
        MouseEvent.Button.Middle -> MouseButton.Middle
        else -> MouseButton.Left
    }
    return when (event.type) {
        MouseEvent.Type.Press ->
            when (event.button) {
                MouseEvent.Button.WheelUp -> TuiEvent.MouseWheel(event.x, event.y, WheelDirection.Up)
                MouseEvent.Button.WheelDown -> TuiEvent.MouseWheel(event.x, event.y, WheelDirection.Down)
                else -> TuiEvent.MousePressed(event.x, event.y, button)
            }
        MouseEvent.Type.Release -> TuiEvent.MouseReleased(event.x, event.y, button)
        MouseEvent.Type.Drag -> TuiEvent.MouseDragged(event.x, event.y)
        MouseEvent.Type.Motion -> null
    }
}
