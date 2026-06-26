package taxonomy.tui.components

import com.jakewharton.mosaic.text.AnnotatedString
import taxonomy.model.GraphNode

/** Navigation state for the top-level app flow. */
enum class StartupState {
    WELCOME,
    CONFIGANDDOMAINS,
    MAINDASHBOARD,
    LOADING
}

/** One rendered line in the DAG topology tree. */
data class TreeLine(
    val node: GraphNode,
    val text: AnnotatedString,
    val isPoly: Boolean
)

/** A single editable configuration item shown in SettingsHub. */
data class SettingItem(
    val name: String,
    val description: String,
    val category: String,
    val getValue: () -> String,
    val setValue: (String) -> Boolean
)

/** Rows rendered inside SettingsHub – either a category header or a concrete item. */
sealed interface SettingsRow

data class HeaderRow(
    val title: String
) : SettingsRow

data class ItemRow(
    val item: SettingItem,
    val flatIndex: Int
) : SettingsRow