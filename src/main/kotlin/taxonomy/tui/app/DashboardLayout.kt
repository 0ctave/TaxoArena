package taxonomy.tui.app

/**
 * Single source of truth for TUI screen geometry.
 *
 * The router renders from these values AND the controller's mouse hit-testing reads from the
 * SAME values, so click->row mapping can never drift from the layout. All coordinates are
 * 0-indexed screen cells (matching the mouse event coordinate space).
 *
 * Shell stack (top to bottom), shared by every screen:
 *   row 0            : Header
 *   row 1            : top horizontal rule
 *   rows 2 .. H-3    : screen content
 *   row H-2          : bottom horizontal rule
 *   row H-1          : footer / hotkey bar
 *
 * Within a bordered [taxonomy.tui.components.Panel]: border-top(1) + content-inset-top(1),
 * so a panel's first content row sits 2 cells below the panel's own top.
 */
object DashboardLayout {

    /** Rows consumed by the shell above the screen-content area (Header + top rule). */
    const val SHELL_TOP_ROWS = 2

    /** Rows a bordered Panel reserves above its first content row (border + top inset). */
    const val PANEL_CONTENT_TOP = 2

    /** Width of the right-aligned query column in the DAG tree table. */
    const val TREE_QUERY_COL = 6

    // ---- Main dashboard ----

    data class Dashboard(
        val width: Int,
        val height: Int,
        val bodyH: Int,
        val topH: Int,
        val bottomH: Int,
        /** Left DAG-explorer panel width (x in 0 until dagW). */
        val dagW: Int,
        /** Right analysis-hub panel width. */
        val arenaW: Int,
        /** Screen Y of the first tree data row (after header table row). */
        val treeFirstRowY: Int,
    )

    /** Mirrors MainDashboardRoute geometry exactly. */
    fun dashboard(width: Int, height: Int): Dashboard {
        val bodyH = (height - 5).coerceAtLeast(9)
        val topH = (bodyH * 0.62).toInt().coerceAtLeast(8)
        val bottomH = (bodyH - topH).coerceAtLeast(4)
        // Keep both panels + the 1-col gap within the terminal: cap dagW so the right panel
        // keeps its minimum width without overflowing on narrow terminals.
        val arenaMin = 20
        val dagW = 68.coerceAtMost((width - 1 - arenaMin).coerceAtLeast(10))
        val arenaW = (width - dagW - 1).coerceAtLeast(arenaMin)
        // SHELL_TOP_ROWS (2) + panel top (2) + the AsciiTreeTable column-header row (1) +
        // the column-header's own trailing row before data (1). Mosaic 0.18.0 already delivers
        // 0-based mouse coords (EventParser subtracts 1), so the off-by-one is corrected here on
        // the layout side rather than by re-subtracting from event.y.
        val treeFirstRowY = SHELL_TOP_ROWS + PANEL_CONTENT_TOP + 2
        return Dashboard(width, height, bodyH, topH, bottomH, dagW, arenaW, treeFirstRowY)
    }

    /** Which dashboard region a click landed in. */
    enum class Region { TOPOLOGY, ANALYSIS_HUB }

    fun dashboardRegion(layout: Dashboard, x: Int): Region =
        if (x < layout.dagW) Region.TOPOLOGY else Region.ANALYSIS_HUB

    /** Tree row index under a click in the topology panel, or -1 if above the first row. */
    fun treeRowIndex(layout: Dashboard, y: Int, scrollOffset: Int): Int {
        val idx = y - layout.treeFirstRowY + scrollOffset
        return if (idx < 0) -1 else idx
    }

    // ---- Config screen ----

    data class Config(
        val width: Int,
        val leftW: Int,
        /** Screen Y of the first row inside the DOMAINS / SETTINGS lists. */
        val firstRowY: Int,
    )

    fun config(width: Int, height: Int): Config {
        val leftW = (width * 0.35).toInt().coerceAtLeast(20)
        // SHELL_TOP_ROWS (2) + panel top (2) + a leading section row (1) = 5.
        val firstRowY = SHELL_TOP_ROWS + PANEL_CONTENT_TOP + 1
        return Config(width, leftW, firstRowY)
    }

    fun configRowIndex(layout: Config, y: Int): Int {
        val idx = y - layout.firstRowY
        return if (idx < 0) -1 else idx
    }

    enum class ConfigSide { DOMAINS, SETTINGS }

    fun configSide(layout: Config, x: Int): ConfigSide =
        if (x < layout.leftW) ConfigSide.DOMAINS else ConfigSide.SETTINGS

    // ---- Welcome screen ----

    /**
     * Welcome layout: the "Create new" entry sits at the top of the menu; saved snapshots are
     * listed below it. Returns the menu index for a click, where 0 = Create new and
     * 1..N = snapshot (snapshotIndex + 1), or null if the click is outside the menu.
     */
    data class Welcome(val firstMenuRowY: Int)

    fun welcome(width: Int, height: Int): Welcome =
        // SHELL_TOP_ROWS (2) + panel top (2) + title + spacer (2) = first menu row.
        Welcome(firstMenuRowY = SHELL_TOP_ROWS + PANEL_CONTENT_TOP + 2)

    /** Menu index for a welcome click: 0 = Create new, 1.. = snapshot. -1 if outside. */
    fun welcomeMenuIndex(layout: Welcome, y: Int, snapshotCount: Int): Int {
        val idx = y - layout.firstMenuRowY
        return if (idx < 0 || idx > snapshotCount) -1 else idx
    }
}
