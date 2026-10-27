package taxonomy

import org.junit.jupiter.api.Test
import taxonomy.arena.*
import taxonomy.model.NodePairStats
import java.io.File
import java.sql.DriverManager

/**
 * Replays a settled domain's recorded verdicts through the placement stopping rule, to see
 * where it would have stopped against where the run actually stopped.
 *
 * No API calls and no writes: the r8 ratings databases are opened read-only and the recorded
 * MAIN verdicts are fed back in the order they were produced. After each verdict the cell's
 * Bradley-Terry fit is recomputed from the evidence available AT THAT POINT — anchors taken
 * from the final fit would encode the whole run and flatter the rule — and `placedModels` is
 * asked whether every model's position is pinned.
 *
 * Excluded from `gradlew test` (seconds of refitting, no assertions). Run it with
 * `gradlew placementReplay`.
 */
class PlacementReplayHarness {

    private data class Verdict(val node: String, val a: String, val b: String, val winner: String?, val tie: Boolean)

    private fun load(db: File): List<Verdict> {
        val url = "jdbc:sqlite:file:${db.absolutePath.replace('\\', '/')}?mode=ro"
        DriverManager.getConnection(url).use { c ->
            c.createStatement().use { st ->
                val rs = st.executeQuery(
                    "select node_id, model_a, model_b, winner, is_tie from match_history" +
                        " where condition='MAIN' order by id"
                )
                val out = ArrayList<Verdict>()
                while (rs.next()) {
                    out += Verdict(
                        rs.getString(1), rs.getString(2), rs.getString(3),
                        rs.getString(4), rs.getInt(5) != 0
                    )
                }
                return out
            }
        }
    }

    /** Running per-pair tallies for one cell, in the shape the fitter and the rule both read. */
    private class Cell(val id: String) {
        val stats = HashMap<PairKey, PairStats>()
        val nodePairs = HashMap<PairKey, NodePairStats>()
        var n = 0

        fun record(v: Verdict) {
            val key = ordered(v.a, v.b)
            val s = stats.getOrPut(key) { PairStats() }
            // Doubles throughout: NodePairStats has two constructors that differ only in the
            // types of `ties`/`totalComparisons`, so untyped literals are ambiguous.
            val np = nodePairs.getOrPut(key) {
                NodePairStats(
                    nodeId = id, modelA = key.first, modelB = key.second,
                    winsA = 0.0, winsB = 0.0, ties = 0.0, totalComparisons = 0.0
                )
            }
            s.n += 1
            np.totalComparisons += 1.0
            when {
                v.tie -> { s.sumX += 0.5; np.ties += 1.0 }
                v.winner == key.first -> { s.sumX += 1.0; np.winsA += 1.0 }
                else -> np.winsB += 1.0
            }
            n += 1
        }
    }

    /** Running tally of one model's record against each opponent. */
    private class Record {
        val wins = HashMap<String, Double>()
        val losses = HashMap<String, Double>()
        val ties = HashMap<String, Double>()
        var n = 0

        fun add(opponent: String, outcome: Int) {   // 1 win, 0 loss, -1 tie
            when (outcome) {
                1 -> wins.merge(opponent, 1.0, Double::plus)
                0 -> losses.merge(opponent, 1.0, Double::plus)
                else -> ties.merge(opponent, 1.0, Double::plus)
            }
            n++
        }

        fun outcomes(): List<ModelPlacement.Outcome> =
            (wins.keys + losses.keys + ties.keys).map { o ->
                ModelPlacement.Outcome(o, wins[o] ?: 0.0, losses[o] ?: 0.0, ties[o] ?: 0.0)
            }
    }

    /**
     * The real use case: a board that already exists, and ONE model joining it.
     *
     * For every (cell, model) the model is held out entirely — the anchors are refit from the
     * other seven alone, so nothing about the newcomer leaks into the board it is being placed
     * against. Its own recorded verdicts are then fed back and the count at which its rank slot
     * closes is read off.
     *
     * Two orders, both drawing on the same real verdicts:
     *   RECORDED — the sequence the racing scheduler actually produced.
     *   ADAPTIVE — opponents chosen by expected Fisher information at each step, consuming a
     *              real recorded outcome against whichever opponent is picked. This is the
     *              counterfactual: same evidence, better questions.
     */
    @Test
    fun `hold out one model and measure the matches needed to place it`() {
        val root = File(".").absoluteFile.parentFile ?: File(".")
        val domains = listOf("philosophy", "history", "engineering", "cs", "law", "psychology", "math", "physics")
        val placement = ModelPlacement()
        val slacks = listOf(0, 1, 2)

        // domain -> slack -> (placed counts, matches used when placed), per order
        data class Acc(val placed: MutableList<Int> = ArrayList(), var cases: Int = 0)
        val recorded = HashMap<Pair<String, Int>, Acc>()
        val adaptive = HashMap<Pair<String, Int>, Acc>()

        for (domain in domains) {
            val db = File(root, "experiment_results/r8/$domain/ratings_r8_$domain.db")
            if (!db.exists()) continue
            val verdicts = load(db)
            val models = verdicts.flatMap { listOf(it.a, it.b) }.distinct().sorted()

            for ((cellId, cv) in verdicts.groupBy { it.node }) {
                for (heldOut in models) {
                    val others = models - heldOut

                    // Anchors: the board WITHOUT the newcomer.
                    val boardCell = Cell(cellId)
                    cv.filter { it.a != heldOut && it.b != heldOut }.forEach { boardCell.record(it) }
                    if (boardCell.nodePairs.isEmpty()) continue
                    val anchorScores = try {
                        BtMmFitter.fit(others, boardCell.nodePairs.values.toList(), context = "holdout/$cellId")
                    } catch (e: Exception) { continue }
                    val anchors = ModelPlacement.anchorsFrom(anchorScores, emptyMap(), others.toSet())
                    if (anchors.size < 2) continue

                    val mine = cv.filter { it.a == heldOut || it.b == heldOut }
                    if (mine.isEmpty()) continue

                    fun outcomeOf(v: Verdict): Pair<String, Int> {
                        val opp = if (v.a == heldOut) v.b else v.a
                        val res = when {
                            v.tie -> -1
                            v.winner == heldOut -> 1
                            else -> 0
                        }
                        return opp to res
                    }

                    // ── recorded order ──────────────────────────────────────────────
                    run {
                        val rec = Record()
                        val hit = HashMap<Int, Int>()
                        for (v in mine) {
                            val (opp, res) = outcomeOf(v)
                            rec.add(opp, res)
                            if (slacks.all { hit.containsKey(it) }) break
                            val belief = placement.posterior(anchors, rec.outcomes())
                            for (sl in slacks) if (!hit.containsKey(sl) &&
                                placement.isSettled(belief, anchors, sl)) hit[sl] = rec.n
                        }
                        for (sl in slacks) {
                            val acc = recorded.getOrPut(domain to sl) { Acc() }
                            acc.cases++
                            hit[sl]?.let { acc.placed += it }
                        }
                    }

                    // ── adaptive order, same pool of real verdicts ──────────────────
                    run {
                        val pool = HashMap<String, ArrayDeque<Int>>()
                        for (v in mine) {
                            val (opp, res) = outcomeOf(v)
                            pool.getOrPut(opp) { ArrayDeque() }.addLast(res)
                        }
                        val rec = Record()
                        val hit = HashMap<Int, Int>()
                        while (pool.values.any { it.isNotEmpty() }) {
                            val belief = placement.posterior(anchors, rec.outcomes())
                            for (sl in slacks) if (!hit.containsKey(sl) &&
                                placement.isSettled(belief, anchors, sl)) hit[sl] = rec.n
                            if (slacks.all { hit.containsKey(it) }) break
                            val opp = placement.nextOpponent(belief, anchors) {
                                pool[it]?.isNotEmpty() == true
                            } ?: break
                            rec.add(opp.model, pool.getValue(opp.model).removeFirst())
                        }
                        val belief = placement.posterior(anchors, rec.outcomes())
                        for (sl in slacks) if (!hit.containsKey(sl) &&
                            placement.isSettled(belief, anchors, sl)) hit[sl] = rec.n
                        for (sl in slacks) {
                            val acc = adaptive.getOrPut(domain to sl) { Acc() }
                            acc.cases++
                            hit[sl]?.let { acc.placed += it }
                        }
                    }
                }
            }
        }

        fun report(label: String, m: Map<Pair<String, Int>, Acc>) {
            println()
            println("$label — one model held out, placed against the other seven")
            println("%-12s %6s %28s %28s".format("domain", "cases", "slack=0  placed / median n", "slack=2  placed / median n"))
            println("-".repeat(80))
            for (domain in domains) {
                val row = slacks.map { sl -> m[domain to sl] }
                if (row.all { it == null }) continue
                fun cell(a: Acc?): String {
                    if (a == null || a.cases == 0) return "     -"
                    val pct = 100.0 * a.placed.size / a.cases
                    val med = if (a.placed.isEmpty()) "-" else a.placed.sorted()[a.placed.size / 2].toString()
                    return "%5.0f%% / %-4s".format(pct, med)
                }
                println(
                    "%-12s %6d %28s %28s".format(
                        domain, row[0]?.cases ?: 0, cell(row[0]), cell(row[2])
                    )
                )
            }
            for (sl in slacks) {
                val all = domains.mapNotNull { m[it to sl] }
                val cases = all.sumOf { it.cases }
                val placed = all.sumOf { it.placed.size }
                val ns = all.flatMap { it.placed }.sorted()
                println(
                    "  ALL slack=%d: %d of %d placed (%.0f%%), median %s matches, p90 %s".format(
                        sl, placed, cases, 100.0 * placed / cases.coerceAtLeast(1),
                        if (ns.isEmpty()) "-" else ns[ns.size / 2].toString(),
                        if (ns.isEmpty()) "-" else ns[(ns.size * 9 / 10).coerceAtMost(ns.size - 1)].toString()
                    )
                )
            }
        }

        report("RECORDED ORDER", recorded)
        report("ADAPTIVE ORDER (Fisher-optimal opponent, same real verdicts)", adaptive)
    }

    /**
     * How placement scales with roster size, and whether growing a board one model at a time
     * beats ranking everything at once.
     *
     * Simulated, because no 16- or 32-model run exists: true strengths are spread over a FIXED
     * range of 3.2 logits — the span the real r8 boards actually occupy — so a larger roster
     * means a more crowded board, which is the realistic way rosters grow. Outcomes are drawn
     * from Bradley-Terry with a 20% tie rate, matching the measured judge.
     *
     * The newcomer is placed against a board whose strengths are known exactly. That flatters
     * the from-scratch case, whose anchors would in reality be uncertain too, so any advantage
     * incremental insertion shows here is a lower bound on its real advantage.
     */
    @Test
    fun `scaling with roster size, and incremental insertion versus ranking at once`() {
        val rng = java.util.Random(20260808L)
        val range = 3.2                       // logits spanned by the whole board
        val tieRate = 0.20
        val seeds = 9
        val cap = 400

        fun insertionCost(boardSize: Int, slack: Int, margin: Double): List<Int> {
            val placement = ModelPlacement(equivalenceMargin = margin)
            val out = ArrayList<Int>()
            repeat(seeds) { s ->
                // Board of `boardSize` models evenly spread across the range.
                val thetas = (0 until boardSize).map { -range / 2 + range * it / (boardSize - 1).coerceAtLeast(1) }
                val anchors = thetas.mapIndexed { i, t -> ModelPlacement.Anchor("m$i", t) }
                    .sortedByDescending { it.theta }
                // Newcomer lands at a reproducible spot inside the board, varied by seed.
                val newTheta = -range / 2 + range * ((s + 0.5) / seeds)
                val rec = Record()
                var n = 0
                while (n < cap) {
                    val belief = placement.posterior(anchors, rec.outcomes())
                    if (placement.isSettled(belief, anchors, slack)) break
                    val opp = placement.nextOpponent(belief, anchors) ?: break
                    val p = 1.0 / (1.0 + kotlin.math.exp(-(newTheta - opp.theta)))
                    val res = when {
                        rng.nextDouble() < tieRate -> -1
                        rng.nextDouble() < p -> 1
                        else -> 0
                    }
                    rec.add(opp.model, res)
                    n++
                }
                out += n
            }
            return out.sorted()
        }

        fun median(xs: List<Int>) = xs[xs.size / 2]

        println()
        println("COST TO INSERT ONE MODEL INTO A SETTLED BOARD (median of $seeds, cap $cap)")
        println("Strength range held at $range logits, so a bigger roster is a denser board.")
        println("%6s %10s %14s %14s".format("board k", "slot width", "slack=2 margin=0", "slack=2 margin=0.2"))
        println("-".repeat(50))
        val ks = listOf(8, 12, 16, 24, 32)
        for (k in ks) {
            val slot = range / (k - 1)
            val noMargin = median(insertionCost(k, slack = 2, margin = 0.0))
            val withMargin = median(insertionCost(k, slack = 2, margin = 0.2))
            println(
                "%6d %10.3f %14s %14s".format(
                    k, slot,
                    if (noMargin >= cap) ">$cap" else "$noMargin",
                    if (withMargin >= cap) ">$cap" else "$withMargin"
                )
            )
        }

        println()
        println("BUILDING A BOARD FROM SCRATCH, ONE MODEL AT A TIME (slack=2, margin=0.2)")
        println("%6s %18s %18s %14s".format("board k", "incremental total", "round robin pairs", "ratio"))
        println("-".repeat(60))
        var cumulative = 0
        var next = 0
        for (k in 3..ks.max()) {
            cumulative += median(insertionCost(k, slack = 2, margin = 0.2))
            if (k in ks) {
                // Round robin as the reference: every pair played to the same evidence depth a
                // single insertion needs, which is the cheapest honest version of "rank at once".
                val depth = median(insertionCost(k, slack = 2, margin = 0.2)).coerceAtLeast(1)
                val rr = k * (k - 1) / 2 * depth
                println(
                    "%6d %18d %18d %13.1fx".format(k, cumulative, rr, rr.toDouble() / cumulative.coerceAtLeast(1))
                )
                next = cumulative
            }
        }
        if (next > 0) Unit
    }

    /** Does the equivalence margin actually fire on the real boards, and at what size? */
    @Test
    fun `sweep the equivalence margin on real data`() {
        val root = File(".").absoluteFile.parentFile ?: File(".")
        val domains = listOf("philosophy", "history", "engineering", "cs", "law", "psychology", "math", "physics")
        val margins = listOf(0.0, 0.2, 0.4, 0.6, 1.0)
        val slack = 2

        println()
        println("EQUIVALENCE MARGIN SWEEP (slack=$slack), settled r8 verdicts")
        println("%8s %14s %10s".format("margin", "verdicts kept", "saved"))
        println("-".repeat(36))

        for (margin in margins) {
            val placement = ModelPlacement(equivalenceMargin = margin)
            var spent = 0
            var stop = 0
            for (domain in domains) {
                val db = File(root, "experiment_results/r8/$domain/ratings_r8_$domain.db")
                if (!db.exists()) continue
                val verdicts = load(db)
                val models = verdicts.flatMap { listOf(it.a, it.b) }.distinct().sorted()
                for ((cellId, cv) in verdicts.groupBy { it.node }) {
                    val cell = Cell(cellId)
                    var at = -1
                    for (v in cv) {
                        cell.record(v)
                        if (at >= 0) continue
                        val scores = try {
                            BtMmFitter.fit(models, cell.nodePairs.values.toList(), context = "sweep/$cellId")
                        } catch (e: Exception) { continue }
                        if (placedModels(placement, models, scores, cell.stats, slack).containsAll(models)) at = cell.n
                    }
                    spent += cell.n
                    stop += if (at < 0) cell.n else at
                }
            }
            println("%8.1f %14d %9.0f%%".format(margin, stop, 100.0 * (spent - stop) / spent.coerceAtLeast(1)))
        }
    }

    /**
     * Tiers as contiguous runs of the strength order, cut wherever consecutive models differ by
     * more than [margin]. A partition, unlike "maximal sets of indistinguishable models", which
     * is not one — indistinguishability is not transitive (A~B and B~C does not give A~C).
     */
    private fun tiers(scores: Map<String, Double>, margin: Double): List<List<String>> {
        val sorted = scores.entries.sortedByDescending { it.value }
        if (sorted.isEmpty()) return emptyList()
        val out = ArrayList<MutableList<String>>()
        out += mutableListOf(sorted[0].key)
        for (i in 1 until sorted.size) {
            if (sorted[i - 1].value - sorted[i].value > margin) out += mutableListOf<String>()
            out.last() += sorted[i].key
        }
        return out
    }

    /**
     * Does tiering per cell say anything a single global tiering does not?
     *
     * This is the question that decides whether tiers are worth carrying through the router. If
     * every cell's tiering is the pooled tiering, routing to a cell buys nothing over a global
     * leaderboard and the tree earns nothing at recommendation time. If cells disagree, that
     * disagreement IS the product.
     */
    @Test
    fun `do per-cell tiers differ from a global tiering`() {
        val root = File(".").absoluteFile.parentFile ?: File(".")
        val domains = listOf("philosophy", "history", "engineering", "cs", "law", "psychology", "math", "physics")

        // OBSERVED uses the real cell assignment. NULL shuffles which cell each verdict belongs
        // to, keeping every cell's size, so cells become random subsets of the same domain. Tier
        // movement under the null is what small samples produce on their own; only movement
        // ABOVE it is the taxonomy saying something.
        for (shuffled in listOf(false, true)) {
        for (margin in listOf(0.2, 0.4)) {
            var cells = 0
            var tierCountSum = 0
            var assignments = 0
            var moved = 0
            var movedByTwo = 0
            var topTierSame = 0

            for (domain in domains) {
                val db = File(root, "experiment_results/r8/$domain/ratings_r8_$domain.db")
                if (!db.exists()) continue
                val verdicts = load(db)
                val models = verdicts.flatMap { listOf(it.a, it.b) }.distinct().sorted()

                // Pooled board for this domain: every cell's evidence, one fit.
                val pooled = Cell("pooled")
                verdicts.forEach { pooled.record(it) }
                val pooledScores = BtMmFitter.fit(models, pooled.nodePairs.values.toList(), context = "pooled")
                val pooledTiers = tiers(pooledScores, margin)
                val pooledIndex = HashMap<String, Int>()
                pooledTiers.forEachIndexed { i, t -> t.forEach { pooledIndex[it] = i } }
                val pooledTop = pooledTiers.firstOrNull()?.toSet() ?: emptySet()

                val grouped = if (!shuffled) verdicts.groupBy { it.node } else run {
                    val sizes = verdicts.groupBy { it.node }.map { it.key to it.value.size }
                    val pool = verdicts.shuffled(java.util.Random(20260808L + domain.hashCode().toLong()))
                    var at = 0
                    sizes.associate { (id, n) -> id to pool.subList(at, (at + n).also { at = it }).toList() }
                }
                for ((cellId, cv) in grouped) {
                    val cell = Cell(cellId)
                    cv.forEach { cell.record(it) }
                    val scores = try {
                        BtMmFitter.fit(models, cell.nodePairs.values.toList(), context = "tier/$cellId")
                    } catch (e: Exception) { continue }
                    val cellTiers = tiers(scores, margin)
                    val cellIndex = HashMap<String, Int>()
                    cellTiers.forEachIndexed { i, t -> t.forEach { cellIndex[it] = i } }

                    cells++
                    tierCountSum += cellTiers.size
                    for (m in models) {
                        val a = pooledIndex[m] ?: continue
                        val b = cellIndex[m] ?: continue
                        assignments++
                        if (a != b) moved++
                        if (kotlin.math.abs(a - b) >= 2) movedByTwo++
                    }
                    if (cellTiers.firstOrNull()?.toSet() == pooledTop) topTierSame++
                }
            }

            println()
            println("TIER STABILITY, margin=$margin logits, ${if (shuffled) "NULL (cells shuffled)" else "OBSERVED"}")
            println("  cells                      : $cells")
            println("  mean tiers per cell        : %.2f".format(tierCountSum.toDouble() / cells.coerceAtLeast(1)))
            println("  model-cell assignments     : $assignments")
            println("  moved tier vs pooled       : %d (%.0f%%)".format(moved, 100.0 * moved / assignments.coerceAtLeast(1)))
            println("  moved by two or more tiers : %d (%.0f%%)".format(movedByTwo, 100.0 * movedByTwo / assignments.coerceAtLeast(1)))
            println("  cells whose TOP TIER equals the pooled top tier: %d of %d (%.0f%%)".format(
                topTierSame, cells, 100.0 * topTierSame / cells.coerceAtLeast(1)))
        }
        }
    }

    /**
     * Do cells genuinely disagree about a model PAIR, beyond sampling error?
     *
     * Cochran's Q, the standard between-study heterogeneity test, applied per model pair with
     * cells as the studies. Each cell contributes a log-odds y_i with variance v_i (Haldane-
     * Anscombe 0.5 correction, since per-cell counts are small and often lopsided), weighted by
     * w_i = 1/v_i. Under "every cell shares one true value" Q has df = cells - 1, so Q/df near 1
     * means no heterogeneity and I-squared is the share of variance that is real rather than
     * sampling.
     *
     * WHY THIS RATHER THAN TIER MOVEMENT. Tier assignment thresholds a noisy estimate, so it
     * churns hardest exactly where models are near-tied — which is most of the board — and that
     * churn appears in the shuffled null too, leaving the statistic with almost no power. Q
     * weights each cell by its precision instead of thresholding, so a well-separated pair
     * measured tightly in two cells can register disagreement that tier movement cannot see.
     *
     * Reported separately for well-separated pairs, which is where a spectrum-spanning roster
     * should show its hand if anywhere.
     */
    @Test
    fun `test between-cell heterogeneity per model pair`() {
        val root = File(".").absoluteFile.parentFile ?: File(".")
        val domains = listOf("philosophy", "history", "engineering", "cs", "law", "psychology", "math", "physics")

        data class Row(val domain: String, val pair: String, val gap: Double, val q: Double, val df: Int, val i2: Double)

        fun analyse(shuffled: Boolean): List<Row> {
            val rows = ArrayList<Row>()
            for (domain in domains) {
                val db = File(root, "experiment_results/r8/$domain/ratings_r8_$domain.db")
                if (!db.exists()) continue
                val verdicts = load(db)
                val models = verdicts.flatMap { listOf(it.a, it.b) }.distinct().sorted()

                val pooled = Cell("pooled")
                verdicts.forEach { pooled.record(it) }
                val pooledScores = BtMmFitter.fit(models, pooled.nodePairs.values.toList(), context = "het")

                val grouped = if (!shuffled) verdicts.groupBy { it.node } else run {
                    val sizes = verdicts.groupBy { it.node }.map { it.key to it.value.size }
                    val pool = verdicts.shuffled(java.util.Random(4242L + domain.hashCode().toLong()))
                    var at = 0
                    sizes.associate { (id, n) -> id to pool.subList(at, (at + n).also { at = it }).toList() }
                }
                val cells = grouped.map { (id, cv) -> Cell(id).also { c -> cv.forEach { c.record(it) } } }

                for (i in models.indices) for (j in i + 1 until models.size) {
                    val key = ordered(models[i], models[j])
                    val ys = ArrayList<Double>()
                    val ws = ArrayList<Double>()
                    for (c in cells) {
                        val s = c.stats[key] ?: continue
                        if (s.n < 3) continue
                        val wins = s.sumX
                        val losses = s.n - s.sumX
                        val y = kotlin.math.ln((wins + 0.5) / (losses + 0.5))
                        val v = 1.0 / (wins + 0.5) + 1.0 / (losses + 0.5)
                        ys += y; ws += 1.0 / v
                    }
                    if (ys.size < 3) continue
                    val wSum = ws.sum()
                    val mean = ys.indices.sumOf { ws[it] * ys[it] } / wSum
                    val q = ys.indices.sumOf { ws[it] * (ys[it] - mean) * (ys[it] - mean) }
                    val df = ys.size - 1
                    val i2 = ((q - df) / q).coerceAtLeast(0.0)
                    val gap = kotlin.math.abs(
                        (pooledScores[key.first] ?: 0.0) - (pooledScores[key.second] ?: 0.0)
                    )
                    rows += Row(domain, "${key.first}|${key.second}", gap, q, df, i2)
                }
            }
            return rows
        }

        val obs = analyse(false)
        val nul = analyse(true)

        fun summarise(label: String, rows: List<Row>) {
            if (rows.isEmpty()) { println("$label: no rows"); return }
            val qdf = rows.map { it.q / it.df }.sorted()
            val i2 = rows.map { it.i2 }.sorted()
            println(
                "  %-22s pairs=%3d  median Q/df=%.2f  mean Q/df=%.2f  median I2=%.2f  frac Q/df>2 = %.0f%%".format(
                    label, rows.size, qdf[qdf.size / 2], qdf.average(), i2[i2.size / 2],
                    100.0 * rows.count { it.q / it.df > 2.0 } / rows.size
                )
            )
        }

        println()
        println("BETWEEN-CELL HETEROGENEITY (Cochran's Q; Q/df = 1 means cells agree)")
        summarise("OBSERVED, all pairs", obs)
        summarise("NULL, all pairs", nul)
        println()
        for (lo in listOf(0.0, 0.5, 1.0, 2.0)) {
            summarise("OBSERVED gap>=%.1f".format(lo), obs.filter { it.gap >= lo })
            summarise("NULL     gap>=%.1f".format(lo), nul.filter { it.gap >= lo })
        }
    }

    @Test
    fun `diagnose why cells do or do not place`() {
        val root = File(".").absoluteFile.parentFile ?: File(".")
        val placement = ModelPlacement()

        for (domain in listOf("philosophy", "physics", "psychology")) {
            val db = File(root, "experiment_results/r8/$domain/ratings_r8_$domain.db")
            if (!db.exists()) continue
            val verdicts = load(db)
            val models = verdicts.flatMap { listOf(it.a, it.b) }.distinct().sorted()

            for ((cellId, cellVerdicts) in verdicts.groupBy { it.node }.entries.sortedBy { it.key }.take(2)) {
                val cell = Cell(cellId)
                cellVerdicts.forEach { cell.record(it) }
                val pairs = cell.nodePairs.values.toList()
                val scores = BtMmFitter.fit(models, pairs, context = "diag/$cellId")
                val sorted = scores.entries.sortedByDescending { it.value }

                println()
                println("$domain / $cellId — ${cell.n} verdicts, ${pairs.size} pairs")
                println("  fitted strengths, and the gap to the next model down:")
                sorted.forEachIndexed { i, (m, t) ->
                    val gap = if (i < sorted.size - 1) t - sorted[i + 1].value else Double.NaN
                    val anchors = ModelPlacement.anchorsFrom(scores, emptyMap(), (models - m).toSet())
                    val outcomes = anchors.mapNotNull { a ->
                        val k = ordered(m, a.model)
                        val s = cell.stats[k] ?: return@mapNotNull null
                        if (s.n == 0) return@mapNotNull null
                        val w = if (k.first == m) s.sumX else s.n - s.sumX
                        ModelPlacement.Outcome(a.model, wins = w, losses = s.n - w)
                    }
                    val belief = placement.posterior(anchors, outcomes)
                    val m0 = placement.bestWindow(belief, anchors, 0).second
                    val m1 = placement.bestWindow(belief, anchors, 1).second
                    val nObs = outcomes.sumOf { it.n }
                    println(
                        "   %-30s theta=%+6.3f gap=%6s  n=%3.0f  slack0=%.2f slack1=%.2f  postSd=%.2f".format(
                            m.take(30), t, if (gap.isNaN()) "-" else "%.3f".format(gap),
                            nObs, m0, m1, belief.sd
                        )
                    )
                }
            }
        }
    }

    @Test
    fun `replay the settled domains and report where placement would have stopped`() {
        val root = File(".").absoluteFile.parentFile ?: File(".")
        val domains = listOf("philosophy", "history", "engineering", "cs", "law", "psychology", "math", "physics")
        val placement = ModelPlacement()

        val slacks = listOf(0, 1, 2, 3)
        println()
        println("PLACEMENT REPLAY — recorded MAIN verdicts, refitting BT at every step")
        println("Stop point per cell, by how many rank slots the claim is allowed to span.")
        println("%-12s %-8s %6s %8s %8s %8s %8s".format("domain", "cell", "spent", "slack=0", "slack=1", "slack=2", "slack=3"))
        println("-".repeat(64))

        var totalSpent = 0
        val totalAt = HashMap<Int, Int>()

        for (domain in domains) {
            val db = File(root, "experiment_results/r8/$domain/ratings_r8_$domain.db")
            if (!db.exists()) { println("$domain: no database, skipped"); continue }
            val verdicts = load(db)
            val models = verdicts.flatMap { listOf(it.a, it.b) }.distinct().sorted()

            for ((cellId, cellVerdicts) in verdicts.groupBy { it.node }.entries.sortedBy { it.key }) {
                val cell = Cell(cellId)
                val placedAt = HashMap<Int, Int>()

                for (v in cellVerdicts) {
                    cell.record(v)
                    if (slacks.all { placedAt.containsKey(it) }) continue
                    val pairs = cell.nodePairs.values.toList()
                    val scores = try {
                        BtMmFitter.fit(models, pairs, context = "replay/$cellId")
                    } catch (e: Exception) { continue }
                    for (sl in slacks) {
                        if (placedAt.containsKey(sl)) continue
                        if (placedModels(placement, models, scores, cell.stats, slack = sl).containsAll(models)) {
                            placedAt[sl] = cell.n
                        }
                    }
                }

                val spent = cell.n
                totalSpent += spent
                for (sl in slacks) totalAt[sl] = (totalAt[sl] ?: 0) + (placedAt[sl] ?: spent)
                println(
                    "%-12s %-8s %6d %8s %8s %8s %8s".format(
                        domain, cellId.takeLast(6), spent,
                        *slacks.map { (placedAt[it]?.toString() ?: "never") as Any }.toTypedArray()
                    )
                )
            }
        }

        println("-".repeat(64))
        for (sl in slacks) {
            val at = totalAt[sl] ?: totalSpent
            println(
                "slack=%d: would stop after %d of %d verdicts (%.0f%% saved)".format(
                    sl, at, totalSpent, 100.0 * (totalSpent - at) / totalSpent.coerceAtLeast(1)
                )
            )
        }
        println(
            "NOTE: 'never' means the cell's order was still open when its recorded evidence ran " +
                "out, so its spend counts in full — the saving is not inflated by unfinished cells."
        )
    }
}
