package taxonomy.tui.input

/**
 * Semantic intents decoupling raw key presses from controller logic.
 */
sealed interface KeyAction {
    // ── Navigation ──
    object MoveUp : KeyAction
    object MoveDown : KeyAction
    object MoveLeft : KeyAction
    object MoveRight : KeyAction
    object CycleFocus : KeyAction

    // ── General Interactions ──
    object Select : KeyAction
    object GoBack : KeyAction
    object DeleteItem : KeyAction
    object ToggleViewMode : KeyAction
    object SelectAll : KeyAction
    object ClearOthers : KeyAction

    // ── Application Specific Commands ──
    object TriggerRegeneration : KeyAction
    object GenerateJudge : KeyAction
    object GenerateBatchJudges : KeyAction
    object RegenerateLabels : KeyAction
    object ExportAscii : KeyAction
    object RenameItem : KeyAction

    // ── Sub-Menu Triggers ──
    object OpenMetrics : KeyAction
    object OpenArena : KeyAction
    object OpenBenchmark : KeyAction
    object OpenTrickle : KeyAction
    object OpenStartup : KeyAction

    // ── Text Input ──
    data class TypeChar(val char: String) : KeyAction
    object Backspace : KeyAction
}