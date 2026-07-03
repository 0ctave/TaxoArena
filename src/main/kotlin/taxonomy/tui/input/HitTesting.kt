package taxonomy.tui.input

/**
 * Semantic layout regions for mouse interactions.
 */
enum class PanelRegion {
    TOPOLOGY,
    CONFIG_LEFT,
    CONFIG_RIGHT,
    ANALYSIS_HUB,
    SYSTEM_LOGS,
    GPU_TRACES,
    HEADER,
    FOOTER_HOTKEYS,
    OUT_OF_BOUNDS
}

/**
 * Pure math object to calculate bounding boxes and translate terminal
 * X/Y coordinates into semantic panel regions.
 */
object HitTesting {

    data class LayoutMetrics(
        val width: Int,
        val height: Int,
        val isConfigMode: Boolean
    ) {
        val dagWidth = 68.coerceAtMost((width - 1 - 20).coerceAtLeast(10))
        val arenaWidth = (width - dagWidth - 1).coerceAtLeast(20)

        val topHeight = ((height - 7) * 0.62).toInt().coerceAtLeast(10)
        val bottomHeight = (height - 7 - topHeight).coerceAtLeast(5)

        val logsWidth = (width * 0.60).toInt().coerceAtLeast(20)

        val configLeftWidth = (width * 0.35).toInt().coerceAtLeast(20)

        val topRowStartY = 3
        val topRowEndY = topRowStartY + topHeight - 1

        val bottomRowStartY = topRowEndY + 2
        val bottomRowEndY = bottomRowStartY + bottomHeight - 1
    }

    /**
     * Determines which major UI panel contains the given X/Y coordinate.
     */
    fun getRegionForCoordinate(x: Int, y: Int, metrics: LayoutMetrics): PanelRegion {
        if (x < 0 || x >= metrics.width || y < 0 || y >= metrics.height) {
            return PanelRegion.OUT_OF_BOUNDS
        }

        if (y < 3) return PanelRegion.HEADER
        if (y >= metrics.height - 2) return PanelRegion.FOOTER_HOTKEYS

        // Top Row Panels
        if (y in metrics.topRowStartY..metrics.topRowEndY) {
            if (metrics.isConfigMode) {
                return if (x < metrics.configLeftWidth) PanelRegion.CONFIG_LEFT else PanelRegion.CONFIG_RIGHT
            } else {
                return if (x < metrics.dagWidth) PanelRegion.TOPOLOGY else PanelRegion.ANALYSIS_HUB
            }
        }

        // Bottom Row Panels
        if (y in metrics.bottomRowStartY..metrics.bottomRowEndY) {
            return if (x < metrics.logsWidth) PanelRegion.SYSTEM_LOGS else PanelRegion.GPU_TRACES
        }

        return PanelRegion.OUT_OF_BOUNDS
    }
}