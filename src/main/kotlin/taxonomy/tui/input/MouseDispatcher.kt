package taxonomy.tui.input

import taxonomy.tui.components.ScrollBarDragManager

/**
 * Semantic intents originating from mouse interactions.
 */
sealed interface MouseAction {
    data class FocusPanel(val region: PanelRegion) : MouseAction
    data class ScrollUpdate(val region: PanelRegion, val newOffset: Int) : MouseAction
    data class ClickRow(val region: PanelRegion, val relativeY: Int) : MouseAction
}

/**
 * Interface for feature controllers to receive semantic mouse actions.
 */
interface MouseController {
    fun handleMouseAction(action: MouseAction): Boolean
}

/**
 * Converts raw Mosaic mouse coordinates into contextual semantic actions.
 */
class MouseDispatcher(
    private val controllers: List<MouseController>
) {

    fun dispatchClick(x: Int, y: Int, metrics: HitTesting.LayoutMetrics, totalItems: Int, visibleItems: Int, isReversed: Boolean = false): Boolean {
        val region = HitTesting.getRegionForCoordinate(x, y, metrics)

        if (region == PanelRegion.OUT_OF_BOUNDS) return false

        // 1. First, always emit a FocusPanel action so the UI can activate borders
        broadcastAction(MouseAction.FocusPanel(region))

        // 2. Check if the click is on a Scrollbar (typically right-most 2-3 characters of a panel)
        val isScrollbarClick = isClickOnScrollbar(x, region, metrics)

        if (isScrollbarClick) {
            // Calculate absolute track bounds based on the region
            val trackStartY = if (region == PanelRegion.SYSTEM_LOGS || region == PanelRegion.GPU_TRACES) {
                metrics.bottomRowStartY + 1 // Account for panel header padding
            } else {
                metrics.topRowStartY + 1
            }

            val newOffset = ScrollBarDragManager.calculateScrollTarget(
                clickY = y,
                trackStartY = trackStartY,
                visibleItems = visibleItems,
                totalItems = totalItems,
                reversed = isReversed
            )

            return broadcastAction(MouseAction.ScrollUpdate(region, newOffset))
        }

        // 3. Otherwise, it's a content click (translate to relative row)
        val relativeY = y - (if (region.name.contains("LOGS") || region.name.contains("GPU")) metrics.bottomRowStartY else metrics.topRowStartY) - 1
        if (relativeY >= 0) {
            return broadcastAction(MouseAction.ClickRow(region, relativeY))
        }

        return true
    }

    private fun broadcastAction(action: MouseAction): Boolean {
        for (controller in controllers) {
            if (controller.handleMouseAction(action)) return true
        }
        return false
    }

    private fun isClickOnScrollbar(x: Int, region: PanelRegion, metrics: HitTesting.LayoutMetrics): Boolean {
        // Standard panel gutters assume scrollbars are ~2-3 chars wide at the far right of the region
        val endX = when (region) {
            PanelRegion.TOPOLOGY -> metrics.dagWidth
            PanelRegion.ANALYSIS_HUB -> metrics.width
            PanelRegion.CONFIG_LEFT -> metrics.configLeftWidth
            PanelRegion.CONFIG_RIGHT -> metrics.width
            PanelRegion.SYSTEM_LOGS -> metrics.logsWidth
            PanelRegion.GPU_TRACES -> metrics.width
            else -> return false
        }
        return x in (endX - 3)..endX
    }
}