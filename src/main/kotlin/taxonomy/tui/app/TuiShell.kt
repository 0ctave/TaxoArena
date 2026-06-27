package taxonomy.tui.app

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.layout.padding
import com.jakewharton.mosaic.layout.width
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.ui.Color.Companion.Black
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Color.Companion.Yellow
import com.jakewharton.mosaic.ui.Column
import com.jakewharton.mosaic.ui.Text
import com.jakewharton.mosaic.ui.TextStyle.Companion.Bold
import taxonomy.tui.components.HRule
import taxonomy.tui.components.Header

/** Minimum terminal size required to render the full 3-region layout. */
private const val MIN_WIDTH = 100
private const val MIN_HEIGHT = 20

@Composable
fun TuiShell(
    width: Int,
    height: Int,
    time: String,
    totalNodes: Int,
    activeDatasetName: String,
    activeSnapshotName: String?,
    maxDepth: Int = 0,
    leafCount: Int = 0,
    content: @Composable () -> Unit,
) {
    if (width < MIN_WIDTH || height < MIN_HEIGHT) {
        Column {
            Text(" WINDOW TOO SMALL ", color = Black, background = Yellow, textStyle = Bold)
            Text("", color = White)
            Text("Minimum ${MIN_WIDTH}x$MIN_HEIGHT · current ${width}x$height", color = Yellow)
            Text("Resize the terminal to continue.", color = White)
        }
        return
    }

    Column(
        modifier = Modifier
            .width(width)
            .padding(left = 0, top = 0)
    ) {
        Header(
            width = width,
            time = time,
            totalNodes = totalNodes,
            activeDatasetName = activeDatasetName,
            activeSnapshotName = activeSnapshotName,
            maxDepth = maxDepth,
            leafCount = leafCount,
        )
        HRule(width, Cyan, White, White)
        content()
        HRule(width, White, Cyan, White)
    }
}