package taxonomy.tui.controller.keys

import taxonomy.tui.components.SettingItem
import taxonomy.tui.controller.TuiEvent
import taxonomy.tui.state.ConfigSubPanel
import taxonomy.tui.state.FocusPanel
import taxonomy.tui.state.TuiAppState

/**
 * Handles keyboard input on the CONFIGANDDOMAINS screen (domains panel,
 * settings panel, setting editor, dataset-download count prompt).
 *
 * Also used by [MainDashboardKeyHandler] when the CONFIG panel holds focus
 * inside the main dashboard.
 */
internal class ConfigKeyHandler(
    private val settingItemsProvider: () -> List<SettingItem>,
    private val availableDomainsProvider: () -> List<Pair<String, Int>>,
) {

    fun handle(state: TuiAppState, key: String, dispatch: (TuiEvent) -> Unit) {
        // If a dataset download is active, only Esc/C can interrupt it.
        if (state.config.downloadingDataset && (key == "escape" || key == "c")) {
            dispatch(TuiEvent.CancelGeneration)
            return
        }

        // SYSTEM_LOGS sub-focus within the config screen.
        if (state.shell.focusedPanel == FocusPanel.SYSTEM_LOGS) {
            when (key) {
                "w", "z", "arrowup" ->
                    dispatch(TuiEvent.SetLogsScroll((state.logs.logScrollOffset - 1).coerceAtLeast(0)))
                "s", "arrowdown" ->
                    dispatch(TuiEvent.SetLogsScroll((state.logs.logScrollOffset + 1).coerceAtLeast(0)))
                "q", "escape", "arrowleft", "backspace" ->
                    dispatch(TuiEvent.FocusPanelRequested(FocusPanel.CONFIG))
            }
            return
        }

        if (state.config.isEditingSetting) {
            handleSettingEditorKeys(state, key, dispatch)
            return
        }

        if (state.config.promptingDownloadCount) {
            handleDownloadCountKeys(state, key, dispatch)
            return
        }

        when (key) {
            "tab" -> {
                val next = if (state.config.activeSubPanel == ConfigSubPanel.DOMAINS)
                    ConfigSubPanel.SETTINGS else ConfigSubPanel.DOMAINS
                dispatch(TuiEvent.SetConfigSubPanel(next))
            }

            "w", "z", "arrowup" -> {
                if (state.config.activeSubPanel == ConfigSubPanel.DOMAINS) {
                    dispatch(TuiEvent.SetSelectedDomainIdx((state.config.selectedDomainIdx - 1).coerceAtLeast(0)))
                } else {
                    dispatch(TuiEvent.SetSelectedSettingIdx((state.config.selectedSettingIdx - 1).coerceAtLeast(0)))
                }
            }

            "s", "arrowdown" -> {
                if (state.config.activeSubPanel == ConfigSubPanel.DOMAINS) {
                    val domains = availableDomainsProvider()
                    val maxIdx = (domains.size - 1).coerceAtLeast(0)
                    dispatch(TuiEvent.SetSelectedDomainIdx((state.config.selectedDomainIdx + 1).coerceAtMost(maxIdx)))
                } else {
                    val items = settingItemsProvider()
                    val maxIdx = (items.size - 1).coerceAtLeast(0)
                    dispatch(TuiEvent.SetSelectedSettingIdx((state.config.selectedSettingIdx + 1).coerceAtMost(maxIdx)))
                }
            }

            "enter", " ", "space" -> {
                if (state.config.activeSubPanel == ConfigSubPanel.DOMAINS) {
                    val domains = availableDomainsProvider()
                    domains.getOrNull(state.config.selectedDomainIdx)?.let { (name, _) ->
                        dispatch(TuiEvent.ToggleSelectedDomain(name))
                    }
                } else {
                    dispatch(TuiEvent.ActivateSelectedSetting)
                }
            }

            "d" -> dispatch(TuiEvent.PromptDatasetDownload)

            "r" -> when {
                state.runtime.isRegenerating    -> Unit
                state.runtime.isDatasetDownloaded -> dispatch(TuiEvent.StartGeneration)
                else                             -> dispatch(TuiEvent.PromptDatasetDownload)
            }

            "arrowdown", "arrowright" -> dispatch(TuiEvent.FocusPanelRequested(FocusPanel.SYSTEM_LOGS))

            "escape", "q" -> dispatch(TuiEvent.ReturnToWelcome)
        }
    }

    // ── Setting text-editor ──────────────────────────────────────────────────

    private fun handleSettingEditorKeys(state: TuiAppState, key: String, dispatch: (TuiEvent) -> Unit) {
        when (key) {
            "enter" -> {
                val item = settingItemsProvider().getOrNull(state.config.selectedSettingIdx)
                if (item != null) {
                    dispatch(TuiEvent.ApplySetting(item.name, state.config.editingValue))
                }
                dispatch(TuiEvent.ConfirmEditingSetting)
            }
            "escape"    -> dispatch(TuiEvent.CancelEditingSetting)
            "backspace" -> dispatch(TuiEvent.UpdateEditingValue(state.config.editingValue.dropLast(1)))
            else -> if (key.length == 1) {
                dispatch(TuiEvent.UpdateEditingValue(state.config.editingValue + key))
            }
        }
    }

    // ── Download-count prompt ────────────────────────────────────────────────

    private fun handleDownloadCountKeys(state: TuiAppState, key: String, dispatch: (TuiEvent) -> Unit) {
        when (key) {
            "enter" -> {
                val n = state.config.downloadCountInput.toIntOrNull() ?: 0
                dispatch(TuiEvent.StartDatasetDownload(n))
            }
            "escape", "q" -> dispatch(TuiEvent.CancelDatasetDownload)
            "backspace"   -> dispatch(
                TuiEvent.UpdateDownloadCountInput(state.config.downloadCountInput.dropLast(1))
            )
            else -> if (key.length == 1 && key[0].isDigit()) {
                dispatch(TuiEvent.UpdateDownloadCountInput(state.config.downloadCountInput + key))
            }
        }
    }
}
