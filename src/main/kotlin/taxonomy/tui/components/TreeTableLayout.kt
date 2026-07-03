package taxonomy.tui.components

/**
 * Pure (composition-free) geometry + text helpers for the DAG tree table, so the layout/
 * truncation logic can be unit-tested without rendering a Mosaic frame.
 */
object TreeTableLayout {

    const val QUERY_COL = 6

    /** Width available for the tree text column given the panel content width. */
    fun treeWidth(pWidth: Int): Int =
        // [caret 2][tree treeW][space 1][queries QCOL][space 1][judge 1][ranks 24] + 1 take() margin
        (pWidth - 2 - 1 - QUERY_COL - 1 - 1 - 1 - 24).coerceAtLeast(10)

    /** Visible data rows given the panel content height (minus the column-header row). */
    fun visibleRows(pHeight: Int): Int = (pHeight - 2).coerceAtLeast(1)

    /** Plain-text (un-styled) render of a single tree row, for golden tests. */
    fun rowText(
        treeText: String,
        recursiveQueryCount: Int,
        hasJudge: Boolean,
        selected: Boolean,
        pWidth: Int,
        isLeaf: Boolean = false,
        topTwoRanks: Pair<String, String>? = null
    ): String {
        val treeW = treeWidth(pWidth)
        val clipped = treeText.take(treeW)
        val pad = " ".repeat((treeW - clipped.length).coerceAtLeast(0))
        val caret = if (selected) "\u276f " else "  "
        val qStr = recursiveQueryCount.toString().padStart(QUERY_COL)
        val judge = if (hasJudge) "\u2714" else "\u25cb"
        val ranks = if (isLeaf) {
            if (topTwoRanks != null) {
                val t1 = shortModelName(topTwoRanks.first)
                val t2 = shortModelName(topTwoRanks.second)
                if (t2.isNotEmpty()) "  [#1 $t1 \u00b7 #2 $t2]" else "  [#1 $t1]"
            } else "  [no data]"
        } else ""
        return (caret + clipped + pad + " " + qStr + " " + judge + ranks).take(pWidth - 1)
    }

    private fun shortModelName(name: String): String {
        val clean = name.lowercase()
        return when {
            clean.contains("claude") -> "claude"
            clean.contains("70b") -> "70B"
            clean.contains("8b") -> "8B"
            clean.contains("13b") -> "13B"
            clean.contains("7b") -> "7B"
            clean.contains("gpt-4") -> "gpt4"
            else -> name.take(8)
        }
    }

    /** Plain-text header row. */
    fun headerText(pWidth: Int): String {
        val treeW = treeWidth(pWidth)
        return ("  " + "Taxonomy DAG Hierarchy".take(treeW).padEnd(treeW) +
            " " + "Queries".padStart(QUERY_COL) + " \u2714" + "   Rankings").take(pWidth - 1)
    }
}
