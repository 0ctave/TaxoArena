package taxonomy.tui.components

/**
 * Pure (composition-free) geometry + text helpers for the DAG tree table, so the layout/
 * truncation logic can be unit-tested without rendering a Mosaic frame.
 */
object TreeTableLayout {

    const val QUERY_COL = 6

    /** Width available for the tree text column given the panel content width. */
    fun treeWidth(pWidth: Int): Int =
        // [caret 2][tree treeW][space 1][queries QCOL][space 1][judge 1] + 1 take() margin
        (pWidth - 2 - 1 - QUERY_COL - 1 - 1 - 1).coerceAtLeast(10)

    /** Visible data rows given the panel content height (minus the column-header row). */
    fun visibleRows(pHeight: Int): Int = (pHeight - 2).coerceAtLeast(1)

    /** Plain-text (un-styled) render of a single tree row, for golden tests. */
    fun rowText(
        treeText: String,
        recursiveQueryCount: Int,
        hasJudge: Boolean,
        selected: Boolean,
        pWidth: Int
    ): String {
        val treeW = treeWidth(pWidth)
        val clipped = treeText.take(treeW)
        val pad = " ".repeat((treeW - clipped.length).coerceAtLeast(0))
        val caret = if (selected) "\u276f " else "  "
        val qStr = recursiveQueryCount.toString().padStart(QUERY_COL)
        val judge = if (hasJudge) "\u2714" else "\u25cb"
        return (caret + clipped + pad + " " + qStr + " " + judge).take(pWidth - 1)
    }

    /** Plain-text header row. */
    fun headerText(pWidth: Int): String {
        val treeW = treeWidth(pWidth)
        return ("  " + "Taxonomy DAG Hierarchy".take(treeW).padEnd(treeW) +
            " " + "Queries".padStart(QUERY_COL) + " \u2714").take(pWidth - 1)
    }
}
