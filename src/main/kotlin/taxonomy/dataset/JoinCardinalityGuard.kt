package taxonomy.dataset

import java.util.concurrent.atomic.AtomicLong

/**
 * JOIN-CARDINALITY-GUARD (queue item; engineering; zero calls).
 *
 * The construction loader [MMLUDatasetFetcher] reads every corpus table as
 * `FROM <table> m LEFT JOIN eval_question_link l ON m.id = l.mmlu_pro_row_id`. The link table's key is the UPSTREAM
 * `question_id`; `mmlu_pro_row_id` carries an index but NO uniqueness constraint. Two link rows naming one local row
 * (two upstream ids filed under one text, a re-link, a hand repair) make the LEFT JOIN emit that question TWICE with
 * two different ids: construction then clusters one text as two queries, the arena can route either id, and the
 * `LIMIT ?` counts the duplicate against the cap. Nothing downstream detects it.
 *
 * The guard: every local row id must appear AT MOST ONCE in the joined result. A repeat is FATAL (fail closed); the
 * exception names the table, the number of fanned-out local rows, the extra rows, and the first ids with their upstream
 * ids. It is a [JoinCardinalityException], which the loader re-throws past its generic `catch (Exception)` (that catch
 * would otherwise turn the refusal into a logged, partial load).
 *
 * Inert when it does not fire: it only reads the ids the loader already built; the rows returned are the same objects
 * in the same order. [checks] / [rowsChecked] count executions (the execution discriminator of the inertness test).
 * On the corpus DB of record the link table has 11,500 distinct non-null mmlu_pro_row_id over 11,500 non-null rows
 * (0 fan-out; read mode=ro&immutable=1 on 2026-10-04), so no recorded load changes.
 */
object JoinCardinalityGuard {
    val checks = AtomicLong()
    val rowsChecked = AtomicLong()

    /** [pairs] = (local row id, upstream id or null) in the order the join returned them. */
    fun assertAtMostOnePerLocalRow(table: String, pairs: List<Pair<Int, Int?>>) {
        checks.incrementAndGet()
        rowsChecked.addAndGet(pairs.size.toLong())
        val byLocal = LinkedHashMap<Int, MutableList<Int?>>()
        for ((local, upstream) in pairs) byLocal.getOrPut(local) { mutableListOf() }.add(upstream)
        val fanned = byLocal.filterValues { it.size > 1 }
        if (fanned.isEmpty()) return
        val extra = fanned.values.sumOf { it.size - 1 }
        val first = fanned.entries.take(5).joinToString("; ") { (k, v) -> "local $k -> upstream $v" }
        throw JoinCardinalityException(
            "[JOIN-CARDINALITY] $table LEFT JOIN eval_question_link: ${fanned.size} local row(s) joined more than one" +
                " link row ($extra extra row(s) of ${pairs.size}); first: $first. One question would enter construction" +
                " under two ids: REFUSED. Repair eval_question_link so each mmlu_pro_row_id is linked at most once."
        )
    }
}

class JoinCardinalityException(message: String) : IllegalStateException(message)
