package taxonomy.tui.input

/**
 * Maps raw terminal keys to semantic actions.
 * Aware of text input modes to prevent hotkey collisions.
 */
object Keymap {

    /**
     * @param rawKey The raw key string from Mosaic's KeyEvent
     * @param isTextInputActive True if a text field is currently focused/active
     */
    fun map(rawKey: String, isTextInputActive: Boolean): KeyAction? {
        val cleanKey = rawKey.filter { !it.isISOControl() }
        val lowerKey = cleanKey.lowercase()

        // 1. Universal keys (always behave the same regardless of text mode)
        when (lowerKey) {
            "enter", " " -> if (lowerKey == " " && isTextInputActive) return KeyAction.TypeChar(" ") else return KeyAction.Select
            "escape" -> return KeyAction.GoBack
            "tab", "\t" -> return KeyAction.CycleFocus
            "backspace" -> return KeyAction.Backspace
            "arrowup" -> return KeyAction.MoveUp
            "arrowdown" -> return KeyAction.MoveDown
            "arrowleft" -> return KeyAction.MoveLeft
            "arrowright" -> return KeyAction.MoveRight
        }

        // 2. Text Input Mode
        if (isTextInputActive) {
            return if (cleanKey.isNotEmpty()) KeyAction.TypeChar(cleanKey) else null
        }

        // 3. Command/Navigation Mode
        return when (lowerKey) {
            // Navigation fallbacks (Z/W for up, S for down)
            "z", "w" -> KeyAction.MoveUp
            "s" -> KeyAction.MoveDown

            // Standard commands
            "q" -> KeyAction.GoBack
            "d" -> KeyAction.DeleteItem
            "v" -> KeyAction.ToggleViewMode
            "n" -> KeyAction.RenameItem

            // App actions
            "r" -> KeyAction.TriggerRegeneration
            "e" -> KeyAction.ExportAscii
            "l" -> KeyAction.RegenerateLabels

            // Hub triggers
            "m" -> KeyAction.OpenMetrics
            "a" -> KeyAction.OpenArena
            "b" -> KeyAction.OpenBenchmark
            "t" -> KeyAction.OpenTrickle
            "x" -> KeyAction.OpenStartup

            // Selection modifiers
            "c" -> KeyAction.ClearOthers

            // Dual-mapped commands depending on exact context handled downstream
            "g", "f" -> KeyAction.GenerateBatchJudges

            else -> {
                if (cleanKey.isNotEmpty()) KeyAction.TypeChar(cleanKey) else null
            }
        }
    }
}