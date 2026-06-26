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

@Composable
fun TuiShell(
    width: Int,
    height: Int,
    time: String,
    totalNodes: Int,
    activeDatasetName: String,
    activeSnapshotName: String?,
    content: @Composable () -> Unit,
) {
    if (width < 100 || height < 20) {
        Column {
            Text("", color = Yellow, textStyle = Bold)
            Text("WINDOW TOO SMALL", color = Black, background = Yellow, textStyle = Bold)
            Text("", color = Yellow, textStyle = Bold)
            Text("Minimum: 100x20  Current: ${width}x$height", color = White)
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
            activeSnapshotName = activeSnapshotName
        )
        HRule(width, Cyan, White, White)
        content()
        HRule(width, White, Cyan, White)
    }
}