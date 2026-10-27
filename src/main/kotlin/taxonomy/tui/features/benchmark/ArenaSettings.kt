package taxonomy.tui.features.benchmark

import taxonomy.tui.components.SettingItem
import taxonomy.tui.components.SettingKind
import taxonomy.tui.controller.TuiEvent
import taxonomy.tui.state.BenchmarkUiState

/**
 * Returns the list of SettingItems representing the Arena configuration.
 * Order: Query limit, Reserved-only, Update rankings, Select models, Select domains, Run benchmark.
 */
fun buildArenaSettingItems(
    b: BenchmarkUiState,
    availableDomains: List<String> = emptyList(),
    dispatch: (TuiEvent) -> Unit = {}
): List<SettingItem> {
    return listOf(
        SettingItem(
            name = "Query limit",
            description = "Limit the number of queries evaluated",
            category = "Arena Settings",
            getValue = { b.benchmarkQueryLimitInput },
            setValue = { s ->
                dispatch(TuiEvent.UpdateBenchmarkEditingValue(s))
                true
            },
            kind = SettingKind.NUMBER
        ),
        SettingItem(
            name = "Parallelism",
            description = "Number of parallel LLM calls for evaluations",
            category = "Arena Settings",
            getValue = { b.benchmarkParallelismInput },
            setValue = { s ->
                dispatch(TuiEvent.UpdateBenchmarkEditingValue(s))
                true
            },
            kind = SettingKind.NUMBER
        ),
        SettingItem(
            name = "Reserved-only",
            description = "Evaluate only on reserved test split queries",
            category = "Arena Settings",
            getValue = { b.benchmarkReservedOnlyInput },
            setValue = { s ->
                dispatch(TuiEvent.ToggleBenchmarkReservedOnly)
                true
            },
            kind = SettingKind.BOOLEAN
        ),
        SettingItem(
            name = "Update rankings",
            description = "Update models' Elo rankings dynamically",
            category = "Arena Settings",
            getValue = { b.benchmarkUpdateRankingsInput },
            setValue = { s ->
                dispatch(TuiEvent.ToggleBenchmarkUpdateRankings)
                true
            },
            kind = SettingKind.BOOLEAN
        ),
        SettingItem(
            name = "Reset rankings",
            description = "Reset model rankings on starting this run",
            category = "Arena Settings",
            getValue = { b.benchmarkResetRankingsInput },
            setValue = { s ->
                dispatch(TuiEvent.ToggleBenchmarkResetRankings)
                true
            },
            kind = SettingKind.BOOLEAN
        ),
        SettingItem(
            name = "Select models",
            description = "Pick which models to evaluate",
            category = "Arena Settings",
            getValue = { b.benchmarkSelectedModels.size.toString() },
            setValue = { _ ->
                dispatch(TuiEvent.OpenBenchmarkPicker(domains = false))
                true
            },
            kind = SettingKind.TEXT
        ),
        SettingItem(
            name = "Select domains",
            description = "Filter evaluation by specific domains",
            category = "Arena Settings",
            getValue = { b.benchmarkSelectedDomains.size.toString() },
            setValue = { _ ->
                dispatch(TuiEvent.OpenBenchmarkPicker(domains = true, domainOptions = availableDomains))
                true
            },
            kind = SettingKind.TEXT
        ),
        SettingItem(
            name = "Run benchmark",
            description = "Start the Arena evaluation run",
            category = "Arena Settings",
            getValue = { "" },
            setValue = { _ ->
                dispatch(TuiEvent.RunBenchmark)
                true
            },
            kind = SettingKind.TEXT
        )
    )
}
