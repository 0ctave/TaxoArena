package taxonomy.tui.components

/**
 * Pure domain-agnostic drag math helper.
 * Given a vertical click/drag event, calculates the new desired scroll index.
 */
object ScrollBarDragManager {

    /**
     * Calculates the scroll target offset based on the mouse Y coordinate.
     * * @param clickY Absolute Y coordinate of the click/drag event
     * @param trackStartY Absolute Y coordinate where the scrollable list begins
     * @param visibleItems Number of rows visible in the container
     * @param totalItems Total number of rows in the data set
     * @param reversed Whether the scrollbar is visually inverted (e.g., chat logs)
     * @return New integer scroll offset intended for the state
     */
    fun calculateScrollTarget(
        clickY: Int,
        trackStartY: Int,
        visibleItems: Int,
        totalItems: Int,
        reversed: Boolean = false
    ): Int {
        val maxScroll = maxOf(0, totalItems - visibleItems)
        if (maxScroll <= 0) return 0

        val trackEndY = trackStartY + visibleItems - 1
        val boundedY = clickY.coerceIn(trackStartY, trackEndY)

        val relativeY = boundedY - trackStartY

        val rawRatio = if (visibleItems > 1) {
            relativeY.toDouble() / (visibleItems - 1).toDouble()
        } else {
            0.0
        }

        val effectiveRatio = if (reversed) 1.0 - rawRatio else rawRatio

        return (effectiveRatio * maxScroll).toInt().coerceIn(0, maxScroll)
    }
}