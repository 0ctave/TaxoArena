package taxonomy.tui.controller.keys

import taxonomy.service.AnalysisMode
import taxonomy.tui.controller.CommandController
import taxonomy.tui.controller.TuiEffects
import taxonomy.tui.controller.TuiEvent
import taxonomy.tui.state.BenchmarkSection
import taxonomy.tui.state.BenchmarkType
import taxonomy.tui.state.MetricsZoneFocus
import taxonomy.tui.state.TuiAppState
import taxonomy.tui.features.benchmark.buildArenaSettingItems

/**
 * Handles keyboard input for the ANALYSIS_HUB panel and all its sub-modes
 * (NODE_DETAIL, METRICS, ARENA, TRICKLE_TEST, BENCHMARK) plus the shared
 * text-input router.
 */
internal class AnalysisKeyHandler(
    private val effects: TuiEffects,
    private val commandController: CommandController,
    private val metricsHistorySizeProvider: () -> Int,
    private val availableDomainsProvider: () -> List<Pair<String, Int>>,
) {

    // ── Public entry point ────────────────────────────────────────────────────

    fun handle(state: TuiAppState, key: String, dispatch: (TuiEvent) -> Unit) {
        when (state.analysis.mode) {
            AnalysisMode.NODE_DETAIL  -> handleNodeDetail(state, key, dispatch)
            AnalysisMode.METRICS      -> handleMetrics(state, key, dispatch)
            AnalysisMode.ARENA        -> handleArena(state, key, dispatch)
            AnalysisMode.TRICKLE_TEST -> handleTrickle(state, key, dispatch)
            AnalysisMode.BENCHMARK    -> handleBenchmark(state, key, dispatch)
            AnalysisMode.SNAPSHOTS    -> handleSnapshots(state, key, dispatch)
            AnalysisMode.JUDGE_PROGRESS -> handleJudgeProgress(state, key, dispatch)
            AnalysisMode.LEADERBOARD  -> handleLeaderboard(state, key, dispatch)
            else                      -> Unit
        }
    }

    /** True when any text-input field is active in the analysis hub or global dashboard. */
    fun isTextInputActive(state: TuiAppState): Boolean =
        state.analysis.isEnteringBatchGenerality ||
        state.analysis.isEditingBatchSetting ||
        state.analysis.isPickingBatchDomains ||
        state.snapshot.isSavingSnapshot ||
        state.snapshot.isRenamingSnapshot ||
        state.arena.isEnteringArenaQuestionId ||
        state.arena.isEnteringArenaQuery ||
        state.arena.isEnteringArenaModelA ||
        state.arena.isEnteringArenaModelB ||
        state.trickle.isEnteringTrickleQuery ||
        state.benchmark.isEnteringTrickleQueryLimit ||
        state.benchmark.isEditingBenchmarkField

    /** Routes a key to whichever text-input field is currently active. */
    fun handleActiveTextInput(state: TuiAppState, key: String, dispatch: (TuiEvent) -> Unit) {
        when {
            state.analysis.isPickingBatchDomains        -> handleBatchDomainsPickerKeys(state, key, dispatch)
            state.analysis.isEnteringBatchGenerality    -> handleBatchSettingsInput(state, key, dispatch)
            state.snapshot.isSavingSnapshot             -> handleSnapshotDescInput(state, key, dispatch)
            state.snapshot.isRenamingSnapshot           -> handleRenameInput(state, key, dispatch)
            state.arena.isEnteringArenaQuestionId       -> handleArenaQuestionIdInput(state, key, dispatch)
            state.arena.isEnteringArenaQuery            -> handleArenaQueryInput(state, key, dispatch)
            state.arena.isEnteringArenaModelA           -> handleArenaModelInput(state, key, dispatch, model = "A")
            state.arena.isEnteringArenaModelB           -> handleArenaModelInput(state, key, dispatch, model = "B")
            state.trickle.isEnteringTrickleQuery        -> handleTrickleQueryInput(state, key, dispatch)
            state.benchmark.isEnteringTrickleQueryLimit -> handleTrickleQueryLimitInput(state, key, dispatch)
            state.benchmark.isEditingBenchmarkField     -> handleBenchmarkEditingFieldInput(state, key, dispatch)
        }
    }

    // ── NODE_DETAIL ───────────────────────────────────────────────────────────

    private fun handleNodeDetail(state: TuiAppState, key: String, dispatch: (TuiEvent) -> Unit) {
        when (key) {
            "w", "z", "arrowup" ->
                dispatch(TuiEvent.SetInspectorScroll((state.analysis.inspectorScroll - 1).coerceAtLeast(0)))
            "s", "arrowdown" ->
                dispatch(TuiEvent.SetInspectorScroll(state.analysis.inspectorScroll + 1))
            "r" -> {
                dispatch(TuiEvent.SetGeneratingJudge(true))
                effects.regenerateJudgeForCurrentNode(dispatch)
            }
            "arrowleft", "q", "escape" ->
                dispatch(TuiEvent.SetAnalysisMode(AnalysisMode.IDLE))
            "m" -> dispatch(TuiEvent.SetAnalysisMode(AnalysisMode.METRICS))
        }
    }

    // ── METRICS ───────────────────────────────────────────────────────────────

    private fun handleMetrics(state: TuiAppState, key: String, dispatch: (TuiEvent) -> Unit) {
        val focus = state.analysis.metricsZoneFocus
        when (key) {
            "w", "z", "arrowup" -> {
                if (focus == MetricsZoneFocus.TABLE) {
                    val histSize = metricsHistorySizeProvider()
                    val cur = state.analysis.selectedIterationIndex
                    val next = if (cur < 0) (histSize - 2).coerceAtLeast(-1)
                               else (cur - 1).coerceAtLeast(-1)
                    dispatch(TuiEvent.SetMetricsIterationIndex(next))
                } else {
                    dispatch(TuiEvent.SetMetricsDetailScroll((state.analysis.detailScrollOffset - 1).coerceAtLeast(0)))
                }
            }
            "s", "arrowdown" -> {
                if (focus == MetricsZoneFocus.TABLE) {
                    val histSize = metricsHistorySizeProvider()
                    val cur = state.analysis.selectedIterationIndex
                    val next = if (cur < 0) -1 else (cur + 1).let { if (it >= histSize) -1 else it }
                    dispatch(TuiEvent.SetMetricsIterationIndex(next))
                } else {
                    dispatch(TuiEvent.SetMetricsDetailScroll(state.analysis.detailScrollOffset + 1))
                }
            }
            "home"     -> dispatch(TuiEvent.SetMetricsIterationIndex(0))
            "end"      -> dispatch(TuiEvent.SetMetricsIterationIndex(-1))
            "p"        -> dispatch(TuiEvent.ToggleMetricsPerformance)
            "tab"      -> dispatch(TuiEvent.SetMetricsZoneFocus(
                if (focus == MetricsZoneFocus.TABLE) MetricsZoneFocus.DETAIL
                else MetricsZoneFocus.TABLE
            ))
            "arrowleft", "q", "escape" -> dispatch(TuiEvent.SetAnalysisMode(AnalysisMode.IDLE))
        }
    }

    // ── ARENA ─────────────────────────────────────────────────────────────────

    private fun handleArena(state: TuiAppState, key: String, dispatch: (TuiEvent) -> Unit) {
        when (key) {
            "w", "z", "arrowup" ->
                dispatch(TuiEvent.SetLeaderboardScrollOffset((state.arena.leaderboardScrollOffset - 1).coerceAtLeast(0)))
            "s", "arrowdown" ->
                dispatch(TuiEvent.SetLeaderboardScrollOffset(state.arena.leaderboardScrollOffset + 1))
            "l" -> dispatch(TuiEvent.ToggleLeaderboard)
            "q", "escape" -> dispatch(TuiEvent.SetAnalysisMode(AnalysisMode.IDLE))
        }
    }

    // ── TRICKLE_TEST ──────────────────────────────────────────────────────────

    private fun handleTrickle(state: TuiAppState, key: String, dispatch: (TuiEvent) -> Unit) {
        when (key) {
            "q", "escape" -> dispatch(TuiEvent.SetAnalysisMode(AnalysisMode.IDLE))
        }
    }

    // ── BENCHMARK ─────────────────────────────────────────────────────────────

    private fun handleBenchmark(state: TuiAppState, key: String, dispatch: (TuiEvent) -> Unit) {
        val bench = state.benchmark
        when (key) {
            "w", "z", "arrowup" -> {
                when (bench.benchmarkType) {
                    BenchmarkType.NONE -> dispatch(
                        TuiEvent.SetBenchmarkTypeSelectionIndex(
                            (bench.benchmarkTypeSelectionIndex - 1).coerceAtLeast(0)
                        )
                    )
                    BenchmarkType.ARENA -> dispatch(
                        TuiEvent.SetSelectedBenchmarkField((bench.selectedBenchmarkField - 1).coerceAtLeast(0))
                    )
                    BenchmarkType.TRICKLE -> Unit
                }
            }
            "s", "arrowdown" -> {
                when (bench.benchmarkType) {
                    BenchmarkType.NONE -> dispatch(
                        TuiEvent.SetBenchmarkTypeSelectionIndex(
                            (bench.benchmarkTypeSelectionIndex + 1).coerceAtMost(1)
                        )
                    )
                    BenchmarkType.ARENA -> dispatch(
                        TuiEvent.SetSelectedBenchmarkField((bench.selectedBenchmarkField + 1).coerceAtMost(6))
                    )
                    BenchmarkType.TRICKLE -> Unit
                }
            }
            " ", "space" -> {
                if (bench.benchmarkType == BenchmarkType.ARENA) {
                    val items = buildArenaSettingItems(bench, availableDomainsProvider().map { it.first }, dispatch)
                    val item = items.getOrNull(bench.selectedBenchmarkField)
                    if (item != null) {
                        if (item.name == "Query limit" || item.name == "Parallelism") {
                            dispatch(TuiEvent.StartEditingBenchmarkField)
                        } else {
                            val next = item.nextValue() ?: ""
                            item.setValue(next)
                        }
                    }
                }
            }
            "enter" -> {
                when (bench.benchmarkType) {
                    BenchmarkType.NONE -> {
                        val type = if (bench.benchmarkTypeSelectionIndex == 0)
                            BenchmarkType.ARENA else BenchmarkType.TRICKLE
                        dispatch(TuiEvent.SetBenchmarkType(type, availableDomainsProvider().map { it.first }))
                        if (type == BenchmarkType.ARENA) effects.loadBenchmarkModels(dispatch)
                    }
                    BenchmarkType.ARENA -> {
                        val items = buildArenaSettingItems(bench, availableDomainsProvider().map { it.first }, dispatch)
                        val item = items.getOrNull(bench.selectedBenchmarkField)
                        if (item != null) {
                            if (item.name == "Query limit" || item.name == "Parallelism") {
                                dispatch(TuiEvent.StartEditingBenchmarkField)
                            } else {
                                val next = item.nextValue() ?: ""
                                item.setValue(next)
                            }
                        }
                    }
                    BenchmarkType.TRICKLE -> Unit
                }
            }
            "v" -> dispatch(TuiEvent.ToggleBenchmarkLiveView)
            "o" -> dispatch(TuiEvent.OpenEvalCatalogPicker)
            "d" -> dispatch(TuiEvent.DownloadEvalResults)
            "q", "escape" -> {
                if (bench.benchmarkType != BenchmarkType.NONE) {
                    effects.resetBenchmarkReport()
                    dispatch(TuiEvent.ResetBenchmarkType)
                } else {
                    dispatch(TuiEvent.SetAnalysisMode(AnalysisMode.IDLE))
                }
            }
        }
    }

    // ── SNAPSHOTS ─────────────────────────────────────────────────────────────

    private fun handleSnapshots(state: TuiAppState, key: String, dispatch: (TuiEvent) -> Unit) {
        when (key) {
            "q", "escape" -> dispatch(TuiEvent.SetAnalysisMode(AnalysisMode.IDLE))
        }
    }

    // ── JUDGE PROGRESS ────────────────────────────────────────────────────────

    private fun handleJudgeProgress(state: TuiAppState, key: String, dispatch: (TuiEvent) -> Unit) {
        when (key) {
            "escape", "q" -> {
                effects.cancelActiveJob()
                dispatch(TuiEvent.SetAnalysisMode(AnalysisMode.IDLE))
            }
        }
    }

    // ── Benchmark multi-select picker (models / domains) ──────────────────────

    fun handleBenchmarkPickerKeys(state: TuiAppState, key: String, dispatch: (TuiEvent) -> Unit) {
        when (key) {
            "w", "z", "arrowup"  -> dispatch(TuiEvent.MoveBenchmarkPickerCursor(-1))
            "s", "arrowdown"     -> dispatch(TuiEvent.MoveBenchmarkPickerCursor(+1))
            " ", "space"         -> dispatch(TuiEvent.ToggleBenchmarkPickerItem)
            "escape", "q", "enter" -> dispatch(TuiEvent.CloseBenchmarkPicker)
        }
    }

    // ── Batch domains picker key handler ──────────────────────────────────────

    fun handleBatchDomainsPickerKeys(state: TuiAppState, key: String, dispatch: (TuiEvent) -> Unit) {
        when (key) {
            "w", "z", "arrowup" -> dispatch(TuiEvent.MoveBatchDomainsPickerCursor(-1))
            "s", "arrowdown" -> dispatch(TuiEvent.MoveBatchDomainsPickerCursor(1))
            " ", "space" -> dispatch(TuiEvent.ToggleBatchDomainsPickerItem)
            "enter" -> dispatch(TuiEvent.ConfirmBatchDomainsSelection)
            "escape" -> dispatch(TuiEvent.CancelBatchDomainsSelection)
        }
    }

    // ── Eval-catalog picker ───────────────────────────────────────────────────

    fun handleEvalCatalogPickerKeys(state: TuiAppState, key: String, dispatch: (TuiEvent) -> Unit) {
        when (key) {
            "w", "z", "arrowup"  -> dispatch(TuiEvent.MoveEvalCatalogCursor(-1))
            "s", "arrowdown"     -> dispatch(TuiEvent.MoveEvalCatalogCursor(+1))
            " ", "space"         -> dispatch(TuiEvent.ToggleEvalCatalogSelection)
            "a"                  -> dispatch(TuiEvent.SelectAllNonIngestedEntries)
            "enter"              -> dispatch(TuiEvent.ConfirmEvalCatalogSelection)
            "escape", "q"        -> dispatch(TuiEvent.CloseEvalCatalogPicker)
        }
    }

    // ── Logs (SYSTEM_LOGS focus inside main dashboard) ─────────────────────────

    fun handleLogsKeys(state: TuiAppState, key: String, dispatch: (TuiEvent) -> Unit) {
        when (key) {
            "w", "z", "arrowup" ->
                dispatch(TuiEvent.SetLogsScroll((state.logs.logScrollOffset - 1).coerceAtLeast(0)))
            "s", "arrowdown" ->
                dispatch(TuiEvent.SetLogsScroll((state.logs.logScrollOffset + 1).coerceAtLeast(0)))
        }
    }

    // ── Text-input field handlers ─────────────────────────────────────────────

    private fun handleBatchSettingsInput(state: TuiAppState, key: String, dispatch: (TuiEvent) -> Unit) {
        val analysis = state.analysis
        if (analysis.isEditingBatchSetting) {
            when (key) {
                "enter" -> dispatch(TuiEvent.ConfirmBatchEditingSetting)
                "escape" -> dispatch(TuiEvent.CancelBatchEditingSetting)
                "backspace" -> dispatch(TuiEvent.UpdateBatchEditingValue(analysis.batchEditingValue.dropLast(1)))
                else -> {
                    if (key.length == 1) {
                        if (analysis.batchSelectedSettingIdx == 0) {
                            if (key[0].isDigit()) {
                                dispatch(TuiEvent.UpdateBatchEditingValue(analysis.batchEditingValue + key))
                            }
                        } else if (analysis.batchSelectedSettingIdx == 1) {
                            dispatch(TuiEvent.UpdateBatchEditingValue(analysis.batchEditingValue + key))
                        }
                    }
                }
            }
        } else {
            val idx = analysis.batchSelectedSettingIdx
            when (key) {
                "w", "z", "arrowup" -> dispatch(TuiEvent.SetBatchSelectedSettingIdx((idx - 1).coerceAtLeast(0)))
                "s", "arrowdown" -> dispatch(TuiEvent.SetBatchSelectedSettingIdx((idx + 1).coerceAtMost(3)))
                "escape" -> dispatch(TuiEvent.CancelBatchGeneralityInput)
                "enter" -> {
                    when (idx) {
                        0 -> dispatch(TuiEvent.StartEditingBatchSetting(analysis.batchGeneralityInput))
                        1 -> {
                            val currentDomains = analysis.batchDomainsInput
                                .split(",")
                                .map { it.trim() }
                                .filter { it.isNotEmpty() }
                                .toSet()
                            val available = availableDomainsProvider().map { it.first }
                            dispatch(TuiEvent.StartPickingBatchDomains(currentDomains, available))
                        }
                        2 -> dispatch(TuiEvent.SetBatchReplaceExisting(!analysis.batchReplaceExisting))
                        3 -> dispatch(TuiEvent.ConfirmBatchGeneralityInput)
                    }
                }
            }
        }
    }

    private fun handleSnapshotDescInput(state: TuiAppState, key: String, dispatch: (TuiEvent) -> Unit) {
        when (key) {
            "enter"     -> dispatch(TuiEvent.ConfirmSaveSnapshot)
            "escape"    -> dispatch(TuiEvent.CancelSaveSnapshot)
            "backspace" -> dispatch(TuiEvent.UpdateSnapshotDescInput(state.snapshot.snapshotDescInput.dropLast(1)))
            else -> if (key.length == 1) {
                dispatch(TuiEvent.UpdateSnapshotDescInput(state.snapshot.snapshotDescInput + key))
            }
        }
    }

    private fun handleRenameInput(state: TuiAppState, key: String, dispatch: (TuiEvent) -> Unit) {
        when (key) {
            "enter"     -> dispatch(TuiEvent.ConfirmRenameSnapshot)
            "escape"    -> dispatch(TuiEvent.CancelRenameSnapshot)
            "backspace" -> dispatch(TuiEvent.UpdateRenameInput(state.snapshot.renameInput.dropLast(1)))
            else -> if (key.length == 1) {
                dispatch(TuiEvent.UpdateRenameInput(state.snapshot.renameInput + key))
            }
        }
    }

    private fun handleArenaQuestionIdInput(state: TuiAppState, key: String, dispatch: (TuiEvent) -> Unit) {
        when (key) {
            "enter"     -> dispatch(TuiEvent.ConfirmArenaQuestionIdInput)
            "escape"    -> dispatch(TuiEvent.CancelArenaInput)
            "backspace" -> dispatch(TuiEvent.UpdateArenaQuestionIdInput(state.arena.arenaQuestionIdInput.dropLast(1)))
            else -> if (key.length == 1) {
                dispatch(TuiEvent.UpdateArenaQuestionIdInput(state.arena.arenaQuestionIdInput + key))
            }
        }
    }

    private fun handleArenaQueryInput(state: TuiAppState, key: String, dispatch: (TuiEvent) -> Unit) {
        when (key) {
            "enter"     -> dispatch(TuiEvent.ConfirmArenaQueryInput)
            "escape"    -> dispatch(TuiEvent.CancelArenaInput)
            "backspace" -> dispatch(TuiEvent.UpdateArenaQueryInput(state.arena.arenaQueryInput.dropLast(1)))
            else -> if (key.length == 1) {
                dispatch(TuiEvent.UpdateArenaQueryInput(state.arena.arenaQueryInput + key))
            }
        }
    }

    private fun handleArenaModelInput(
        state: TuiAppState,
        key: String,
        dispatch: (TuiEvent) -> Unit,
        model: String,
    ) {
        when (key) {
            "enter" -> dispatch(
                if (model == "A") TuiEvent.ConfirmArenaModelAInput else TuiEvent.ConfirmArenaModelBInput
            )
            "escape" -> dispatch(TuiEvent.CancelArenaInput)
            "backspace" -> {
                val cur = if (model == "A") state.arena.arenaModelAInput else state.arena.arenaModelBInput
                dispatch(
                    if (model == "A") TuiEvent.UpdateArenaModelAInput(cur.dropLast(1))
                    else              TuiEvent.UpdateArenaModelBInput(cur.dropLast(1))
                )
            }
            else -> if (key.length == 1) {
                val cur = if (model == "A") state.arena.arenaModelAInput else state.arena.arenaModelBInput
                dispatch(
                    if (model == "A") TuiEvent.UpdateArenaModelAInput(cur + key)
                    else              TuiEvent.UpdateArenaModelBInput(cur + key)
                )
            }
        }
    }

    private fun handleTrickleQueryInput(state: TuiAppState, key: String, dispatch: (TuiEvent) -> Unit) {
        when (key) {
            "enter"     -> dispatch(TuiEvent.ConfirmTrickleQueryInput)
            "escape"    -> dispatch(TuiEvent.CancelTrickleInput)
            "backspace" -> dispatch(TuiEvent.UpdateTrickleQueryInput(state.trickle.trickleQueryInput.dropLast(1)))
            else -> if (key.length == 1) {
                dispatch(TuiEvent.UpdateTrickleQueryInput(state.trickle.trickleQueryInput + key))
            }
        }
    }

    private fun handleTrickleQueryLimitInput(state: TuiAppState, key: String, dispatch: (TuiEvent) -> Unit) {
        when (key) {
            "enter" -> {
                val maxQ = state.benchmark.trickleQueryLimitInput.toIntOrNull() ?: 0
                dispatch(TuiEvent.RunBatchTrickleTest(maxQ))
            }
            "escape", "q" -> dispatch(TuiEvent.CancelTrickleBenchmarkInput)
            "backspace"   -> dispatch(
                TuiEvent.UpdateTrickleQueryLimitInput(state.benchmark.trickleQueryLimitInput.dropLast(1))
            )
            else -> if (key.length == 1 && key[0].isDigit()) {
                dispatch(TuiEvent.UpdateTrickleQueryLimitInput(state.benchmark.trickleQueryLimitInput + key))
            }
        }
    }

    private fun handleBenchmarkEditingFieldInput(state: TuiAppState, key: String, dispatch: (TuiEvent) -> Unit) {
        when (key) {
            "enter"     -> dispatch(TuiEvent.ConfirmEditingBenchmarkField)
            "escape"    -> dispatch(TuiEvent.CancelEditingBenchmarkField)
            "backspace" -> dispatch(
                TuiEvent.UpdateBenchmarkEditingValue(state.benchmark.benchmarkEditingValue.dropLast(1))
            )
            else -> if (key.length == 1 && key[0].isDigit()) {
                dispatch(TuiEvent.UpdateBenchmarkEditingValue(state.benchmark.benchmarkEditingValue + key))
            }
        }
    }

    private fun handleLeaderboard(state: TuiAppState, key: String, dispatch: (TuiEvent) -> Unit) {
        when (key) {
            "w", "z", "arrowup" ->
                dispatch(TuiEvent.SetLeaderboardScrollOffset((state.arena.leaderboardScrollOffset - 1).coerceAtLeast(0)))
            "s", "arrowdown" ->
                dispatch(TuiEvent.SetLeaderboardScrollOffset(state.arena.leaderboardScrollOffset + 1))
            "k", "K" ->
                dispatch(TuiEvent.ClearLeaderboard)
            "l", "escape", "q" ->
                dispatch(TuiEvent.SetAnalysisMode(AnalysisMode.IDLE))
        }
    }
}
