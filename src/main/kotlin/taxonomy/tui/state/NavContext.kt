package taxonomy.tui.state

/**
 * What the left-hand NAVIGATOR pane should display, derived from app state.
 *
 * The navigator is context-driven: it never stacks data-type sections, it shows
 * exactly the one thing that is relevant to the current state.
 */
enum class NavContext {
    /** No DAG loaded and nothing in progress: offer snapshot load / new DAG. */
    SNAPSHOT_SELECT,

    /** User is configuring a new generation: pick domains of the dataset. */
    DOMAIN_SELECT,

    /** A DAG is present: explore its nodes (tree / flat list). */
    DAG_EXPLORE,
}

/**
 * Derive the navigator context.
 *
 * @param hasDag whether a taxonomy DAG is currently loaded (root present).
 * @param choosingDomains whether the user is in the new-DAG domain-selection flow.
 */
fun deriveNavContext(hasDag: Boolean, choosingDomains: Boolean): NavContext = when {
    choosingDomains -> NavContext.DOMAIN_SELECT
    hasDag          -> NavContext.DAG_EXPLORE
    else            -> NavContext.SNAPSHOT_SELECT
}
