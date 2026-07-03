package taxonomy.tui.components

import com.jakewharton.mosaic.text.AnnotatedString
import taxonomy.model.GraphNode

/** Navigation state for the top-level app flow. */
enum class StartupState {
    LOAD_DAG,
    CONFIGANDDOMAINS,
    MAINDASHBOARD,
    LOADING
}

/** One rendered line in the DAG topology tree. */
data class TreeLine(
    val node: GraphNode,
    val text: AnnotatedString,
    val isPoly: Boolean,
    val topTwoRanks: Pair<String, String>? = null
)

/** The kind of input a [SettingItem] uses, which drives both rendering and editing. */
enum class SettingKind {
    /** true/false — toggled instantly with Space/Enter, no text entry. */
    BOOLEAN,
    /** One of a fixed set of [SettingItem.options] — cycled instantly with Space/Enter. */
    SELECT,
    /** Numeric — opened in the inline editor, pre-filled with the current value. */
    NUMBER,
    /** Free text — opened in the inline editor, pre-filled with the current value. */
    TEXT,
}

/** A single editable configuration item shown in SettingsHub. */
data class SettingItem(
    val name: String,
    val description: String,
    val category: String,
    val getValue: () -> String,
    val setValue: (String) -> Boolean,
    val kind: SettingKind = SettingKind.TEXT,
    /** Allowed values for [SettingKind.SELECT]. */
    val options: List<String> = emptyList(),
) {
    /** BOOLEAN and SELECT are applied instantly (toggle/cycle); NUMBER and TEXT open the editor. */
    val isInstant: Boolean get() = kind == SettingKind.BOOLEAN || kind == SettingKind.SELECT

    /** The next value when the item is toggled/cycled in place; null if not instant. */
    fun nextValue(): String? = when (kind) {
        SettingKind.BOOLEAN -> (!(getValue().toBooleanStrictOrNull() ?: false)).toString()
        SettingKind.SELECT -> {
            if (options.isEmpty()) null else {
                val i = options.indexOf(getValue())
                options[(i + 1).mod(options.size)]
            }
        }
        else -> null
    }
}

/** Rows rendered inside SettingsHub – either a category header or a concrete item. */
sealed interface SettingsRow

data class HeaderRow(
    val title: String
) : SettingsRow

data class ItemRow(
    val item: SettingItem,
    val flatIndex: Int
) : SettingsRow