package taxonomy.operations

/**
 * H9-REM construction-order shuffle (debug flag, 2026-09-16).
 *
 * The greedy construction loop visits its proposal sites in an arbitrary-but-deterministic
 * order: BFS/id-hash order inside a depth in the split pass, and the enumeration order of
 * `children` / `getAllNodes` in the four merge passes. The 2026-09-07 construction-loop
 * audit identified that order as one of the inputs the fixed point is a function of. This
 * helper permutes exactly those orders under a declared seed so a registered arm can measure
 * the path-dependence of the fixed point on its own, with the corpus, the split and every
 * threshold held fixed.
 *
 * Contract:
 *  - `seed == null` (the production default, and every run before this flag existed) is the
 *    IDENTITY: [arrange] returns the SAME list instance, allocates nothing and touches no RNG.
 *    The inert path is one null check, so a run without the key is byte-identical to a run
 *    built before the key existed.
 *  - With a seed, the permutation is a pure function of (seed, iteration, pass tag). It does
 *    not depend on how many shuffles ran before it, so an early-out in one pass, or the
 *    sibling-merge recursion visiting a different number of nodes, cannot shift every later
 *    permutation. `java.util.Random` + `Collections.shuffle` are JDK-specified, so the
 *    permutation of a registered arm reproduces across JVMs.
 *
 * What is NOT permuted (documented modelling decisions, not arbitrary hash orders): the
 * deepest-first depth schedule of the split pass and the ascending-k first-accept rule.
 */
class ConstructionOrder(private val seed: Long?) {

    /** True when a seed is declared, i.e. the arm is a shuffled one. */
    val active: Boolean get() = seed != null

    /**
     * The visiting order for one pass. Identity (same instance) when no seed is declared;
     * otherwise a fresh copy permuted by [derive]`(seed, iteration, pass)`.
     */
    fun <T> arrange(items: List<T>, iteration: Int, pass: String): List<T> {
        val s = seed ?: return items
        if (items.size < 2) return items
        val copy = ArrayList(items)
        java.util.Collections.shuffle(copy, java.util.Random(derive(s, iteration, pass)))
        return copy
    }

    companion object {
        /** The permutation key: the same (seed, iteration, pass) always gives the same order. */
        fun derive(seed: Long, iteration: Int, pass: String): Long =
            seed xor (iteration.toLong() * -0x61c8864680b583ebL) xor pass.hashCode().toLong()

        /** The order in force for a config: reads the effective formalism value per call. */
        fun of(config: taxonomy.config.TaxonomyConfig): ConstructionOrder =
            ConstructionOrder(config.formalism.constructionOrderShuffleSeed)
    }
}
