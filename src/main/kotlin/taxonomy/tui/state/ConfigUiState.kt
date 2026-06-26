package taxonomy.tui.state

data class ConfigUiState(
    val activeSubPanel: ConfigSubPanel = ConfigSubPanel.DOMAINS,

    val selectedDomainIdx: Int = 0,
    val domainScrollOffset: Int = 0,

    val selectedSettingIdx: Int = 0,
    val isEditingSetting: Boolean = false,
    val editingValue: String = "",

    val downloadingDataset: Boolean = false,
    val datasetDownloadProgress: Float = 0f,
    val datasetDownloadStatusText: String = "",

    val generationStatusText: String = "",

    val settingsVersion: Int = 0
)