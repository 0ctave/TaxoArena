package taxonomy.tui.components

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.layout.height
import com.jakewharton.mosaic.layout.width
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.ui.Color
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Color.Companion.Yellow
import com.jakewharton.mosaic.ui.Column
import com.jakewharton.mosaic.ui.Spacer
import com.jakewharton.mosaic.ui.Text

/**
 * Standardized empty content block for panels without data.
 */
@Composable
fun EmptyState(
    message: String,
    subMessage: String? = null,
    width: Int,
    height: Int,
    icon: String = "◌",
    color: Color = Yellow
) {
    Column(modifier = Modifier.width(width).height(height)) {
        val topPadding = maxOf(0, height / 2 - 2)
        Spacer(Modifier.height(topPadding))

        Text(
            " $icon $message"
                .center(width)
                .take(width - 1),
            color = color
        )

        if (subMessage != null) {
            Spacer(Modifier.height(1))
            Text(
                subMessage
                    .center(width)
                    .take(width - 1),
                color = White
            )
        }
    }
}