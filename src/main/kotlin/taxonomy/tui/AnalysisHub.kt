package org.eclipse.lmos.arc.app.taxonomy.tui

import androidx.compose.runtime.*
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.ui.*
import com.jakewharton.mosaic.layout.*
import com.jakewharton.mosaic.text.*
import com.jakewharton.mosaic.ui.TextStyle.Companion.Bold
import com.jakewharton.mosaic.ui.Color.Companion.Blue
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
import com.jakewharton.mosaic.ui.Color.Companion.Green
import com.jakewharton.mosaic.ui.Color.Companion.Magenta
import com.jakewharton.mosaic.ui.Color.Companion.Yellow
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Color.Companion.Black
import com.jakewharton.mosaic.ui.Color.Companion.Red
import com.jakewharton.mosaic.animation.animateColorAsState
import kotlinx.coroutines.*
import kotlinx.serialization.json.*
import java.time.LocalTime
import java.time.format.DateTimeFormatter
import org.eclipse.lmos.arc.app.taxonomy.*
import org.eclipse.lmos.arc.app.taxonomy.operations.*
import com.jakewharton.mosaic.LocalTerminalState
import com.jakewharton.mosaic.terminal.Terminal
import com.jakewharton.mosaic.terminal.*
import com.jakewharton.mosaic.animation.*
import org.fusesource.jansi.AnsiConsole

    @Composable
    internal fun TaxonomyTuiService.AnalysisHub(
        pWidth: Int,
        pHeight: Int,
        state: AnalysisPanelState,
        inspectorScroll: Int,
        inspectorLines: List<AnnotatedString>,
        selectedSettingIdx: Int,
        isEditingSetting: Boolean,
        editingValue: String,
        settingItems: List<SettingItem>,
        regeneratingColor: Color,
        selectedSnapshotIdx: Int,
        isSavingSnapshot: Boolean,
        snapshotDescInput: String,
        snapshotList: List<DagSnapshot>
    ) {
        when (state.mode) {
            AnalysisMode.IDLE          -> IdlePlaceholder(pWidth, pHeight)
            AnalysisMode.ARENA         -> DetailedArena(pWidth, pHeight, state)
            AnalysisMode.JUDGE_PROGRESS -> JudgeInductionProgress(pWidth, pHeight, state)
            AnalysisMode.NODE_DETAIL   -> NodeInspector(pWidth, pHeight, state.selectedNode, inspectorScroll, inspectorLines)
            AnalysisMode.SETTINGS      -> SettingsHub(pWidth, pHeight, selectedSettingIdx, isEditingSetting, editingValue, settingItems, isRegenerating, regeneratingColor)
            AnalysisMode.METRICS       -> MetricsHub(pWidth, pHeight)
            AnalysisMode.SNAPSHOTS     -> SnapshotsHub(pWidth, pHeight, selectedSnapshotIdx, isSavingSnapshot, snapshotDescInput, snapshotList)
            AnalysisMode.TRICKLE_TEST  -> TrickleTestHub(pWidth, pHeight)
            else                             -> IdlePlaceholder(pWidth, pHeight)
        }
    }

    @Composable
    internal fun TaxonomyTuiService.IdlePlaceholder(pWidth: Int, pHeight: Int) {
        Column {
            Spacer(Modifier.height(maxOf(0, pHeight / 2 - 3)))
            Text(
                "  ◈  Select a node  [ ↑↓ / Z·S ]  then press  [ Enter ]  to inspect  ◈"
                    .center(pWidth).take(pWidth - 1),
                color = Cyan
            )
            Spacer(Modifier.height(1))
            Text(
                "  Press  [ R ]  to generate a judge for the highlighted node"
                    .center(pWidth).take(pWidth - 1),
                color = White
            )
            Text(
                "  Press  [ G ]  to fill missing judges  ·  [ F ]  to regenerate all"
                    .center(pWidth).take(pWidth - 1),
                color = White
            )
        }
    }
