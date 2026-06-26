package taxonomy.tui.components

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.layout.height
import com.jakewharton.mosaic.layout.width
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.text.SpanStyle
import com.jakewharton.mosaic.text.buildAnnotatedString
import com.jakewharton.mosaic.text.withStyle
import com.jakewharton.mosaic.ui.Box
import com.jakewharton.mosaic.ui.Color
import com.jakewharton.mosaic.ui.Column
import com.jakewharton.mosaic.ui.Spacer
import com.jakewharton.mosaic.ui.Text
import com.jakewharton.mosaic.ui.TextStyle.Companion.Bold

/** * Titled panel with a coloured header and padded content box.
 * Fully domain-agnostic layout container.
 */
@Composable
fun Panel(
    title: String,
    accentColor: Color,
    width: Int,
    height: Int,
    content: @Composable () -> Unit
) {
    Column(modifier = Modifier.width(width).height(height)) {
        Text(
            buildAnnotatedString {
                withStyle(SpanStyle(color = accentColor, textStyle = Bold)) {
                    append(" $title ")
                }
            }.take(width - 1),
            modifier = Modifier.height(1)
        )
        Spacer(Modifier.height(1))
        Box(modifier = Modifier.width(width - 2).height(height - 2)) {
            content()
        }
    }
}