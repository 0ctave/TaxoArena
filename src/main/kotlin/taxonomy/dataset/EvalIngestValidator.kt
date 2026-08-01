package taxonomy.dataset

import org.slf4j.LoggerFactory
import org.springframework.beans.factory.annotation.Value
import org.springframework.stereotype.Service
import org.sqlite.SQLiteConfig
import java.sql.Connection
import java.sql.DriverManager
import java.util.Locale

/**
 * Pre-flight validation of `eval_results` ingestion, run BEFORE a model is allowed into the
 * arena benchmark.
 *
 * ## Why this exists
 *
 * `eval_results` is populated from one downloaded zip per model. Nothing in the loader or in
 * the schema ties a model's `question_id` to the same *question* every other model answered:
 *
 *  * `question_id` is whatever integer the model's own source zip used. At least one published
 *    zip (`Meta-Llama-3-70B-Instruct`) numbers the MMLU-Pro test set differently from all the
 *    others, so its row for `question_id = 70` holds a marketing question while the other 46
 *    models' row for `question_id = 70` holds a cone-clutch mechanics question.
 *  * `PRIMARY KEY (question_id, model_name)` + `INSERT OR IGNORE` means a zip whose numbering
 *    collides with itself silently loses rows — the load reports success and the model simply
 *    ends up short.
 *  * `mmlu_pro.id` is a local AUTOINCREMENT rowid, NOT the upstream question id. The two id
 *    spaces overlap numerically but are unrelated (a naive `mmlu_pro.id = question_id` join
 *    matches the question text in 1 of 11776 cases), so any code that conflates them is wrong.
 *
 * The arena joins model answers on `question_id` alone. A mis-keyed model therefore gets judged
 * on *someone else's* questions against its own traces — an error that is completely invisible
 * in the leaderboard, because every downstream export reports models, never provenance.
 *
 * ## How the decisive check works
 *
 * For every `question_id` the corpus holds up to 47 independent witnesses of what that question
 * says. The majority text wins, and each model is scored on how often it agrees. This is a
 * consensus vote over the *whole* table — not just the models participating in this run — which
 * is what makes it decisive: a mis-keyed model is outvoted 46-to-1 on essentially every row.
 *
 * Texts are compared after Unicode-insensitive whitespace stripping and ASCII lowercasing.
 * That normalisation is not cosmetic; it is required for correctness. Several zips ship the
 * same questions with different whitespace/LaTeX escaping — `gemini-3.1-pro_5-shots` renders
 * `"Forr(t) = [ln(t^3 + 1)..."` as `"For r(t) = [ln(t^3 + 1)..."`. Compared raw, that model
 * shows 167 "divergences"; after normalisation it shows 6, in line with every other clean model.
 * Without normalisation the check would false-positive on formatting, and the threshold needed
 * to tolerate that would be loose enough to let real mis-keying through.
 *
 * ## Cost
 *
 * Four grouped scans of `eval_results` for the whole table, not per-model scans (which would be
 * 47x the work). SQLite does the aggregation; only ~12.6k grouped rows cross the JDBC boundary
 * instead of 560k full rows with their CoT traces. Measured at roughly five seconds against the
 * 709 MB production cache.
 *
 * The database is opened strictly read-only; this class never writes.
 */
@Service
class EvalIngestValidator(
    @Value("\${taxoadapt.eval.db-path:mmlu_pro_dataset_cache_v2.db}")
    private val dbPath: String = "mmlu_pro_dataset_cache_v2.db"
) {
    private val log = LoggerFactory.getLogger("taxonomy.EvalIngestValidator")

    companion object {
        /**
         * Size of the MMLU-Pro test split. Used only as a sanity reference against the
         * consensus question count the corpus actually contains — never as the coverage
         * denominator, so the validator still works on small fixtures.
         */
        const val MMLU_PRO_TEST_SIZE = 12032

        /**
         * A `question_id` needs at least this many independent witnesses before a majority
         * vote over its text means anything. Three is the smallest number that can break a
         * tie. Clamped down when the table holds fewer models (fixtures, 2-model runs).
         *
         * Rows on ids below quorum are counted as ORPHANS rather than as agreements: a model
         * that is the sole witness of an id would otherwise be its own majority and score a
         * perfect 1.0 on exactly the rows that prove it is using a foreign id space.
         * `Meta-Llama-3-70B-Instruct` has 86 such ids; every other model has zero.
         */
        const val QUORUM = 3

        // ── QUESTION_IDENTITY ────────────────────────────────────────────────────────────
        // Measured on the production cache, the whole clean population sits at >= 0.9995
        // (worst clean model: 6 divergent rows out of 12032 — genuine duplicate question
        // texts upstream, where the same text appears under two ids and the majority vote is
        // arbitrary). The mis-keyed model sits at 0.0000. The gap spans four orders of
        // magnitude, so the thresholds only need to land somewhere inside it.
        //
        // WARN at 0.999 allows ~12 divergent rows, twice the observed clean maximum, so a
        // couple of extra upstream duplicates will not raise a false alarm.
        // FAIL at 0.95 requires ~600 divergent rows before rejecting — far beyond anything
        // duplicate texts can produce, and far below the ~7400 the real defect produces.
        const val IDENTITY_FAIL_BELOW = 0.95
        const val IDENTITY_WARN_BELOW = 0.999

        // ── ID_SPACE_ORPHANS ─────────────────────────────────────────────────────────────
        // Fraction of a model's rows sitting on question_ids no quorum of models can confirm.
        // Clean models: exactly 0. Any non-zero value means the zip invented ids, so WARN is
        // deliberately hair-triggered at 0.1%. FAIL at 10% is reserved for a model whose id
        // space is largely foreign — at that point the join key is meaningless.
        const val ORPHAN_WARN_ABOVE = 0.001
        const val ORPHAN_FAIL_ABOVE = 0.10

        // ── ROW_COVERAGE ─────────────────────────────────────────────────────────────────
        // Denominator is the consensus question count (ids confirmed by >= QUORUM models),
        // which equals 12032 on the production cache and adapts to fixtures.
        //
        // Below 1% missing is immaterial: the arena draws pairs from the intersection of the
        // participating models anyway. Below 90% the model's answerable pool differs from its
        // opponents' by more than a tenth, which biases every pairwise comparison set it takes
        // part in, and at that point the load itself is the suspect — `INSERT OR IGNORE` on a
        // colliding primary key drops rows without reporting an error.
        const val COVERAGE_FAIL_BELOW = 0.90
        const val COVERAGE_WARN_BELOW = 0.99

        // ── RESERVED_COVERAGE ────────────────────────────────────────────────────────────
        // Zero rows in the reserved pool means the arena has literally nothing to judge for
        // this model on a reservedOnly run, so it is a hard failure. Anything short of the
        // full pool is a WARN: the model simply contributes fewer comparisons.
        const val RESERVED_WARN_BELOW = 0.98

        // ── PRED_PRESENT ─────────────────────────────────────────────────────────────────
        // A null `pred` is a failed answer extraction. It is scored as incorrect, which is the
        // standard MMLU-Pro convention, and it is a property of weak base models rather than of
        // ingestion: `Qwen1.5-7B-Chat` legitimately sits at 0.767 and `deepseek` at 0.799, so
        // WARN sits below both at 0.90 only to make the asymmetry visible. FAIL at 0.50 is a
        // corruption/truncation detector — no real model fails extraction on half the test set.
        const val PRED_FAIL_BELOW = 0.50
        const val PRED_WARN_BELOW = 0.90

        // ── CORRECTNESS_CONSISTENCY ──────────────────────────────────────────────────────
        // `is_correct` must equal `pred == gt_answer` by construction. Any violation is a
        // loader bug, hence WARN on the very first one. FAIL at 1% keeps a handful of odd
        // rows from blocking a run while still rejecting a systematically miscomputed column.
        // (Observed on the production cache: zero violations, all 47 models.)
        const val CONSISTENCY_FAIL_BELOW = 0.99

        // ── GT_ANSWER_AGREEMENT ──────────────────────────────────────────────────────────
        // Same majority-vote machinery applied to `gt_answer`. This corroborates the identity
        // check from a second, independent column: a mis-keyed model carries its source's
        // answer key too, so it disagrees on the ground truth as well.
        //
        // The clean population is noisier here than on question text — most models disagree on
        // 33 of 12032 rows (0.9973), because MMLU-Pro shipped answer-key corrections that
        // different zips captured at different times. WARN at 0.995 (~60 rows) sits just below
        // that cluster; FAIL at 0.90 is far beyond any plausible key revision.
        const val GT_FAIL_BELOW = 0.90
        const val GT_WARN_BELOW = 0.995

        // ── TRACE_PRESENCE (advisory) ────────────────────────────────────────────────────
        // Fraction of rows carrying a non-blank `model_output`. This never blocks a run,
        // because TaxonomyBenchmarkService.getRobustTrace synthesises a trace from `pred` and
        // the option list when the stored output is blank. It is still reported, because it is
        // a real confound: 32 of the 47 cached models carry no chain-of-thought at all, so the
        // LLM judge sees a one-line synthetic statement for them and full reasoning for the
        // other 15. Advisory checks are shown but excluded from the model's rollup verdict.
        const val TRACE_WARN_BELOW = 0.50

        /**
         * SQL expression normalising `question_text` for the majority vote: NFKC-ish cleanup by
         * hand (SQLite has no Unicode normaliser), all whitespace removed, ASCII-lowercased.
         * Covers space, tab, LF, CR, form feed, vertical tab and U+00A0 no-break space — the
         * latter appears verbatim in the medical questions of the MMLU-Pro zips.
         */
        val NORMALISED_QUESTION_SQL: String = buildString {
            append("lower(")
            var expr = "question_text"
            for (code in intArrayOf(32, 9, 10, 13, 12, 11, 160)) {
                expr = "replace($expr, char($code), '')"
            }
            append(expr)
            append(")")
        }

        /** Kotlin twin of [NORMALISED_QUESTION_SQL]; kept next to it so the two cannot drift. */
        fun normaliseQuestion(text: String): String {
            val sb = StringBuilder(text.length)
            for (ch in text) {
                when (ch) {
                    ' ', '\t', '\n', '\r', '\u000C', '\u000B', '\u00A0' -> {}
                    else -> sb.append(ch.lowercaseChar())
                }
            }
            return sb.toString()
        }

        /**
         * Delimiter SQLite concatenates voter model names with. U+001F (unit separator) is a
         * control character no model name can contain, so the split is unambiguous where a
         * comma would not be.
         */
        const val VOTER_SEP: Char = '\u001F'
    }

    // ─── Result model ────────────────────────────────────────────────────────────────────

    enum class IngestStatus {
        PASS, WARN, FAIL, SKIP;

        /** SKIP is inert: it never drags a verdict down and never lifts one up. */
        fun worseOf(other: IngestStatus): IngestStatus = when {
            this == FAIL || other == FAIL -> FAIL
            this == WARN || other == WARN -> WARN
            this == PASS || other == PASS -> PASS
            else -> SKIP
        }
    }

    /**
     * One check applied to one model. [value] is the measured statistic in [0,1] (or NaN when
     * the check could not be evaluated); [detail] explains the verdict in prose.
     * Advisory checks are reported but do not contribute to the model's rollup status.
     */
    data class IngestCheck(
        val name: String,
        val status: IngestStatus,
        val value: Double,
        val detail: String,
        val advisory: Boolean = false
    )

    data class ModelIngestVerdict(
        val modelName: String,
        val status: IngestStatus,
        val totalRows: Int,
        val checks: List<IngestCheck>
    ) {
        val isFail: Boolean get() = status == IngestStatus.FAIL

        /** Human-readable reasons the verdict is not a clean PASS. */
        val reasons: List<String>
            get() = checks
                .filter { it.status == IngestStatus.WARN || it.status == IngestStatus.FAIL }
                .map { "${it.status} ${it.name} — ${it.detail}" }

        fun check(name: String): IngestCheck? = checks.firstOrNull { it.name == name }
    }

    data class EvalIngestReport(
        val verdicts: List<ModelIngestVerdict>,
        /** Question ids confirmed by at least [QUORUM] models — the coverage denominator. */
        val consensusQuestions: Int,
        val reservedPoolSize: Int,
        val quorum: Int,
        val modelsInCorpus: Int,
        /** Table-level observations that belong to no single model. */
        val corpusNotes: List<String>
    ) {
        val failed: List<ModelIngestVerdict> get() = verdicts.filter { it.status == IngestStatus.FAIL }
        val warned: List<ModelIngestVerdict> get() = verdicts.filter { it.status == IngestStatus.WARN }
        val passed: List<ModelIngestVerdict> get() = verdicts.filter { it.status == IngestStatus.PASS }

        /** Models cleared for the arena. */
        val admittedModels: List<String> get() = verdicts.filterNot { it.isFail }.map { it.modelName }

        fun verdictFor(model: String): ModelIngestVerdict? = verdicts.firstOrNull { it.modelName == model }

        /** One log line per model plus its non-PASS reasons, then a summary. Caller adds the tag. */
        fun renderLines(): List<String> = buildList {
            add(
                "corpus: ${modelsInCorpus} model(s), consensusQuestions=$consensusQuestions" +
                    " (quorum=$quorum), reservedPool=$reservedPoolSize question(s)"
            )
            corpusNotes.forEach { add("note: $it") }
            val width = (verdicts.maxOfOrNull { it.modelName.length } ?: 1).coerceAtLeast(1)
            // Loudest first: FAIL, then WARN, then SKIP, then PASS.
            val severity = mapOf(
                IngestStatus.FAIL to 0, IngestStatus.WARN to 1, IngestStatus.SKIP to 2, IngestStatus.PASS to 3
            )
            verdicts.sortedWith(compareBy({ severity[it.status] ?: 9 }, { it.modelName })).forEach { v ->
                add("%-4s %-${width}s rows=%d".format(Locale.US, v.status.name, v.modelName, v.totalRows))
                v.reasons.forEach { add("       $it") }
            }
            add(
                "summary: ${passed.size} PASS, ${warned.size} WARN, ${failed.size} FAIL" +
                    if (failed.isEmpty()) "" else " — rejected: ${failed.joinToString(", ") { it.modelName }}"
            )
        }
    }

    // ─── Raw aggregates pulled from SQLite ───────────────────────────────────────────────

    private data class ModelScalars(
        val totalRows: Int,
        val distinctQuestions: Int,
        val reservedRows: Int,
        val nullPred: Int,
        val inconsistent: Int,
        val blankTrace: Int
    )

    /** One (question_id, value) group: how many models voted for it, and which. */
    private data class VoteGroup(
        val voters: List<String>,
        val sample: String
    )

    // ─── Entry point ─────────────────────────────────────────────────────────────────────

    /**
     * Models that must never appear in a roster, with the reason. Checked by
     * [enforceNamedExclusions] and thrown on, because the failure mode these guard against
     * is silent: a bad model produces plausible numbers rather than an error.
     *
     * This exists because a documented exclusion is not an enforcement point. Every entry
     * below was already written down somewhere before it went on to corrupt a measurement.
     */
    private val BANNED_MODELS: Map<String, String> = mapOf(
        "Meta-Llama-3-70B-Instruct" to
            "different question-id space: 213 law rows overlap the other models' 287 on " +
            "exactly 1, so ANY roster containing it collapses to a near-empty intersection. " +
            "Was in the 8-model Math arena roster and produced the spurious 'law has only 20 " +
            "questions' result (archive/docs/arena-math-findings.md).",
        "deepseek" to "no trace field in the upstream archive; getRobustTrace substitutes a " +
            "one-line stub, reproducing the 99.4% format preference",
        "flash_0shots_00_35_03" to "no trace field in the upstream archive",
        "gpt4o(2024-05-13)" to "no trace field in the upstream archive",
        "opus_2shots_00_37_14" to "no trace field in the upstream archive",
        "sonnet-3.5_0shots_09_34_29" to "no trace field in the upstream archive",
        "sonnet_0shots_12_01_18" to "no trace field in the upstream archive",
        "jamba-1.5-large" to "mixed format: emits a bare answer on 68.4% of items, which " +
            "reintroduces the format preference inside its own comparisons",
        "gemini-1.5-pro-002" to "mixed format: bare answer on 35.4% of items",
        "gemini-1.5-flash-002" to "mixed format: bare answer on 27.6% of items",
    )

    /** Fails loudly at roster load rather than silently at analysis time. */
    fun enforceNamedExclusions(models: List<String>) {
        val hits = models.filter { it in BANNED_MODELS }
        check(hits.isEmpty()) {
            "roster contains ${hits.size} banned model(s):\n" +
                hits.joinToString("\n") { "  - $it: ${BANNED_MODELS[it]}" }
        }
    }

    /**
     * Validate [models] against the ingested corpus.
     *
     * Majorities are established over every model in `eval_results`, not just [models], so a
     * two-model run still gets all 47 witnesses backing its consensus.
     */
    fun validate(models: List<String>): EvalIngestReport {
        if (models.isEmpty()) {
            return EvalIngestReport(emptyList(), 0, 0, 0, 0, listOf("no models requested"))
        }
        enforceNamedExclusions(models)
        openReadOnly().use { c ->
            if (!hasEvalResults(c)) {
                return EvalIngestReport(
                    verdicts = models.map {
                        ModelIngestVerdict(
                            it, IngestStatus.FAIL, 0,
                            listOf(
                                IngestCheck(
                                    "TABLE_PRESENT", IngestStatus.FAIL, 0.0,
                                    "eval_results does not exist in '$dbPath' — nothing has been ingested"
                                )
                            )
                        )
                    },
                    consensusQuestions = 0, reservedPoolSize = 0, quorum = 0, modelsInCorpus = 0,
                    corpusNotes = listOf("eval_results table missing in '$dbPath'")
                )
            }

            val scalars = readModelScalars(c)
            val corpusModels = scalars.size
            val quorum = minOf(QUORUM, corpusModels).coerceAtLeast(1)
            val reservedPool = readReservedPoolSize(c)

            val identityGroups = readVoteGroups(c, NORMALISED_QUESTION_SQL, sampleExpr = "substr(question_text, 1, 110)")
            val gtGroups = readVoteGroups(c, "gt_answer", sampleExpr = "gt_answer")

            val identity = tally(identityGroups, quorum)
            val gt = tally(gtGroups, quorum)

            // The coverage denominator: ids the corpus can vouch for. Equals 12032 on the
            // production cache; on a fixture it is simply the fixture's question count.
            val consensusQuestions = identityGroups.count { (_, groups) ->
                groups.sumOf { it.voters.size } >= quorum
            }

            val corpusNotes = buildCorpusNotes(c, consensusQuestions, reservedPool, corpusModels, scalars)

            val verdicts = models.map { model ->
                buildVerdict(
                    model = model,
                    s = scalars[model],
                    identity = identity[model],
                    gt = gt[model],
                    consensusQuestions = consensusQuestions,
                    reservedPool = reservedPool
                )
            }
            return EvalIngestReport(
                verdicts = verdicts,
                consensusQuestions = consensusQuestions,
                reservedPoolSize = reservedPool,
                quorum = quorum,
                modelsInCorpus = corpusModels,
                corpusNotes = corpusNotes
            )
        }
    }

    // ─── Checks ──────────────────────────────────────────────────────────────────────────

    private fun buildVerdict(
        model: String,
        s: ModelScalars?,
        identity: Tally?,
        gt: Tally?,
        consensusQuestions: Int,
        reservedPool: Int
    ): ModelIngestVerdict {
        if (s == null || s.totalRows == 0) {
            return ModelIngestVerdict(
                model, IngestStatus.FAIL, 0,
                listOf(
                    IngestCheck(
                        "ROWS_PRESENT", IngestStatus.FAIL, 0.0,
                        "no rows in eval_results for '$model' — the model was never ingested"
                    )
                )
            )
        }
        val total = s.totalRows.toDouble()
        val checks = mutableListOf<IngestCheck>()

        // 1. QUESTION_IDENTITY — the decisive check.
        checks += identityCheck(identity, model)

        // 2. ID_SPACE_ORPHANS — rows on ids no quorum of models can confirm.
        checks += orphanCheck(identity, s)

        // 3. ROW_COVERAGE.
        checks += coverageCheck(s, consensusQuestions)

        // 4. RESERVED_COVERAGE.
        checks += reservedCheck(s, reservedPool)

        // 5. PRED_PRESENT.
        val predRate = 1.0 - s.nullPred / total
        checks += IngestCheck(
            "PRED_PRESENT",
            when {
                predRate < PRED_FAIL_BELOW -> IngestStatus.FAIL
                predRate < PRED_WARN_BELOW -> IngestStatus.WARN
                else -> IngestStatus.PASS
            },
            predRate,
            "${pct(predRate)} of ${s.totalRows} rows have an extracted answer" +
                " (${s.nullPred} null/blank pred, scored as incorrect)"
        )

        // 6. CORRECTNESS_CONSISTENCY.
        val consistency = 1.0 - s.inconsistent / total
        checks += IngestCheck(
            "CORRECTNESS_CONSISTENCY",
            when {
                consistency < CONSISTENCY_FAIL_BELOW -> IngestStatus.FAIL
                s.inconsistent > 0 -> IngestStatus.WARN
                else -> IngestStatus.PASS
            },
            consistency,
            if (s.inconsistent == 0) "is_correct matches (pred == gt_answer) on all ${s.totalRows} rows"
            else "${s.inconsistent} row(s) where is_correct disagrees with (pred == gt_answer)"
        )

        // 7. GT_ANSWER_AGREEMENT — independent corroboration of the identity check.
        checks += gtCheck(gt, model)

        // 8. TRACE_PRESENCE — advisory.
        val traceRate = 1.0 - s.blankTrace / total
        checks += IngestCheck(
            "TRACE_PRESENCE",
            if (traceRate < TRACE_WARN_BELOW) IngestStatus.WARN else IngestStatus.PASS,
            traceRate,
            "${pct(traceRate)} of rows carry a chain-of-thought trace" +
                if (s.blankTrace > 0)
                    "; ${s.blankTrace} blank output(s) will be judged on a synthesised one-line trace"
                else "",
            advisory = true
        )

        val rollup = checks.filterNot { it.advisory }
            .fold(IngestStatus.SKIP) { acc, ch -> acc.worseOf(ch.status) }
        return ModelIngestVerdict(model, rollup, s.totalRows, checks)
    }

    private fun identityCheck(t: Tally?, model: String): IngestCheck {
        val voted = (t?.agree ?: 0) + (t?.diverge ?: 0)
        if (t == null || voted == 0) {
            return IngestCheck(
                "QUESTION_IDENTITY", IngestStatus.FAIL, 0.0,
                "'$model' shares no quorum-backed question_id with the rest of the corpus," +
                    " so none of its rows can be matched to a known question"
            )
        }
        val rate = t.agree.toDouble() / voted
        val status = when {
            rate < IDENTITY_FAIL_BELOW -> IngestStatus.FAIL
            rate < IDENTITY_WARN_BELOW -> IngestStatus.WARN
            else -> IngestStatus.PASS
        }
        val detail = buildString {
            append("${pct(rate)} of $voted quorum-backed rows carry the majority question text")
            append(" for their question_id (${t.diverge} divergent)")
            if (status != IngestStatus.PASS && t.sampleQid != null) {
                append("; e.g. question_id=${t.sampleQid} stored \"${t.sampleMine}\"")
                append(" but ${t.sampleMajVotes} other model(s) store \"${t.sampleMajority}\"")
            }
        }
        return IngestCheck("QUESTION_IDENTITY", status, rate, detail)
    }

    private fun orphanCheck(t: Tally?, s: ModelScalars): IngestCheck {
        val orphans = t?.orphan ?: 0
        val rate = orphans / s.totalRows.toDouble()
        val status = when {
            rate > ORPHAN_FAIL_ABOVE -> IngestStatus.FAIL
            rate > ORPHAN_WARN_ABOVE -> IngestStatus.WARN
            else -> IngestStatus.PASS
        }
        return IngestCheck(
            "ID_SPACE_ORPHANS", status, rate,
            if (orphans == 0) "every question_id is confirmed by a quorum of other models"
            else "$orphans row(s) (${pct(rate)}) sit on question_ids no quorum of models confirms" +
                " — the source zip uses ids the rest of the corpus does not have"
        )
    }

    private fun coverageCheck(s: ModelScalars, consensusQuestions: Int): IngestCheck {
        if (consensusQuestions <= 0) {
            return IngestCheck("ROW_COVERAGE", IngestStatus.SKIP, Double.NaN, "no consensus question set to compare against")
        }
        val rate = s.totalRows.toDouble() / consensusQuestions
        val status = when {
            rate < COVERAGE_FAIL_BELOW -> IngestStatus.FAIL
            rate < COVERAGE_WARN_BELOW -> IngestStatus.WARN
            else -> IngestStatus.PASS
        }
        val missing = consensusQuestions - s.totalRows
        val detail = buildString {
            append("${s.totalRows} rows vs $consensusQuestions expected (${pct(rate)})")
            if (missing > 0) {
                append("; $missing question(s) missing — a colliding question_id is dropped silently")
                append(" by INSERT OR IGNORE on PRIMARY KEY (question_id, model_name)")
            } else if (missing < 0) {
                append("; ${-missing} row(s) beyond the consensus set")
            }
        }
        return IngestCheck("ROW_COVERAGE", status, rate, detail)
    }

    private fun reservedCheck(s: ModelScalars, reservedPool: Int): IngestCheck {
        if (reservedPool == 0) {
            return IngestCheck(
                "RESERVED_COVERAGE", IngestStatus.SKIP, Double.NaN,
                "no question is flagged is_reserved = 1 — a reservedOnly run would have nothing to judge"
            )
        }
        val rate = s.reservedRows.toDouble() / reservedPool
        val status = when {
            s.reservedRows == 0 -> IngestStatus.FAIL
            rate < RESERVED_WARN_BELOW -> IngestStatus.WARN
            else -> IngestStatus.PASS
        }
        return IngestCheck(
            "RESERVED_COVERAGE", status, rate,
            "${s.reservedRows} of $reservedPool reserved question(s) answered (${pct(rate)})" +
                if (s.reservedRows == 0) " — the arena cannot judge this model on a reservedOnly run" else ""
        )
    }

    private fun gtCheck(t: Tally?, model: String): IngestCheck {
        val voted = (t?.agree ?: 0) + (t?.diverge ?: 0)
        if (t == null || voted == 0) {
            return IngestCheck(
                "GT_ANSWER_AGREEMENT", IngestStatus.SKIP, Double.NaN,
                "no quorum-backed rows for '$model' to compare ground truth on"
            )
        }
        val rate = t.agree.toDouble() / voted
        val status = when {
            rate < GT_FAIL_BELOW -> IngestStatus.FAIL
            rate < GT_WARN_BELOW -> IngestStatus.WARN
            else -> IngestStatus.PASS
        }
        return IngestCheck(
            "GT_ANSWER_AGREEMENT", status, rate,
            "${pct(rate)} of $voted quorum-backed rows carry the majority gt_answer" +
                " (${t.diverge} divergent)"
        )
    }

    private fun buildCorpusNotes(
        c: Connection,
        consensusQuestions: Int,
        reservedPool: Int,
        corpusModels: Int,
        scalars: Map<String, ModelScalars>
    ): List<String> = buildList {
        if (consensusQuestions != MMLU_PRO_TEST_SIZE) {
            add(
                "consensus question count is $consensusQuestions, not the MMLU-Pro test size" +
                    " ($MMLU_PRO_TEST_SIZE) — coverage is scored against the corpus, not the constant"
            )
        }
        if (reservedPool == 0) {
            add("is_reserved is set on no question — reservedOnly runs will find an empty pool")
        } else if (reservedPool < 50) {
            add("reserved pool holds only $reservedPool question(s); reserved coverage is a coarse signal at this size")
        }
        val blank = scalars.count { it.value.blankTrace == it.value.totalRows }
        if (blank > 0) {
            add(
                "$blank of $corpusModels model(s) carry no chain-of-thought at all; the judge sees a" +
                    " synthesised one-line trace for them and full reasoning for the rest (advisory)"
            )
        }
        idSpaceNote(c)?.let { add(it) }
    }

    /**
     * Documents the third defect directly: `mmlu_pro.id` and `eval_results.question_id` are
     * unrelated id spaces. Sampled rather than scanned, because the point is qualitative and
     * `eval_question_link` (the correct bridge, by text) is not always in a settled state.
     */
    private fun idSpaceNote(c: Connection): String? = runCatching {
        c.prepareStatement(
            """
            SELECT COUNT(*), SUM(CASE WHEN e.question_text = m.question THEN 1 ELSE 0 END)
            FROM (SELECT question_id, MIN(question_text) AS question_text
                  FROM eval_results GROUP BY question_id LIMIT 500) e
            JOIN mmlu_pro m ON m.id = e.question_id
            """.trimIndent()
        ).use { ps ->
            ps.executeQuery().use { rs ->
                if (!rs.next()) return@runCatching null
                val joined = rs.getInt(1)
                val matched = rs.getInt(2)
                if (joined == 0) return@runCatching null
                if (matched.toDouble() / joined < 0.5) {
                    "mmlu_pro.id and eval_results.question_id are DISTINCT id spaces:" +
                        " a naive id join matches the question text in only $matched of $joined sampled" +
                        " rows — join through eval_question_link (by text), never on the raw id"
                } else null
            }
        }
    }.getOrNull()

    // ─── SQL ─────────────────────────────────────────────────────────────────────────────

    /**
     * Read-only handle. `SQLiteConfig.setReadOnly` opens with SQLITE_OPEN_READONLY, and
     * `PRAGMA query_only` is belt-and-braces in case a later refactor reuses the connection.
     */
    private fun openReadOnly(): Connection {
        val cfg = SQLiteConfig()
        cfg.setReadOnly(true)
        cfg.setBusyTimeout(15_000)
        val c = DriverManager.getConnection("jdbc:sqlite:$dbPath", cfg.toProperties())
        runCatching { c.createStatement().use { it.execute("PRAGMA query_only = 1") } }
        return c
    }

    private fun hasEvalResults(c: Connection): Boolean =
        c.createStatement().use { s ->
            s.executeQuery("SELECT name FROM sqlite_master WHERE type='table' AND name='eval_results'")
                .use { it.next() }
        }

    /** Single grouped scan producing every per-model scalar the checks need. */
    private fun readModelScalars(c: Connection): Map<String, ModelScalars> {
        val sql = """
            SELECT model_name,
                   COUNT(*),
                   COUNT(DISTINCT question_id),
                   SUM(CASE WHEN is_reserved = 1 THEN 1 ELSE 0 END),
                   SUM(CASE WHEN pred IS NULL OR TRIM(pred) = '' THEN 1 ELSE 0 END),
                   SUM(CASE WHEN is_correct = (CASE WHEN pred IS NOT NULL AND pred = gt_answer THEN 1 ELSE 0 END)
                            THEN 0 ELSE 1 END),
                   SUM(CASE WHEN model_output IS NULL OR TRIM(model_output) = '' THEN 1 ELSE 0 END)
            FROM eval_results
            GROUP BY model_name
        """.trimIndent()
        val out = HashMap<String, ModelScalars>()
        c.createStatement().use { s ->
            s.executeQuery(sql).use { rs ->
                while (rs.next()) {
                    out[rs.getString(1)] = ModelScalars(
                        totalRows = rs.getInt(2),
                        distinctQuestions = rs.getInt(3),
                        reservedRows = rs.getInt(4),
                        nullPred = rs.getInt(5),
                        inconsistent = rs.getInt(6),
                        blankTrace = rs.getInt(7)
                    )
                }
            }
        }
        return out
    }

    private fun readReservedPoolSize(c: Connection): Int =
        c.createStatement().use { s ->
            s.executeQuery("SELECT COUNT(DISTINCT question_id) FROM eval_results WHERE is_reserved = 1")
                .use { if (it.next()) it.getInt(1) else 0 }
        }

    /**
     * One grouped scan per voted-on column. Groups by (question_id, [groupExpr]) and returns,
     * for each distinct value, the models that voted for it plus a display sample.
     *
     * The model list is concatenated by SQLite with U+001F (unit separator), a character that
     * cannot occur in a model name, so only ~12.6k rows cross JDBC instead of 560k.
     */
    private fun readVoteGroups(
        c: Connection,
        groupExpr: String,
        sampleExpr: String
    ): Map<Int, List<VoteGroup>> {
        val sql = """
            SELECT question_id,
                   GROUP_CONCAT(model_name, char(31)),
                   MIN($sampleExpr)
            FROM eval_results
            GROUP BY question_id, $groupExpr
        """.trimIndent()
        val out = HashMap<Int, MutableList<VoteGroup>>()
        c.createStatement().use { s ->
            s.executeQuery(sql).use { rs ->
                while (rs.next()) {
                    val qid = rs.getInt(1)
                    val voters = rs.getString(2)?.split(VOTER_SEP) ?: emptyList()
                    out.getOrPut(qid) { ArrayList(2) }.add(VoteGroup(voters, rs.getString(3) ?: ""))
                }
            }
        }
        return out
    }

    // ─── Majority vote ───────────────────────────────────────────────────────────────────

    private data class Tally(
        var agree: Int = 0,
        var diverge: Int = 0,
        var orphan: Int = 0,
        var sampleQid: Int? = null,
        var sampleMine: String = "",
        var sampleMajority: String = "",
        var sampleMajVotes: Int = 0
    )

    /**
     * Majority vote per question_id. The winning group is the one with the most voters; ties
     * are broken on the lexicographically smallest voter list purely so the result is
     * deterministic (no tie occurs on the production cache). Question ids with fewer than
     * [quorum] witnesses produce ORPHAN rows instead of agreements.
     */
    private fun tally(groups: Map<Int, List<VoteGroup>>, quorum: Int): Map<String, Tally> {
        val out = HashMap<String, Tally>()
        fun t(m: String) = out.getOrPut(m) { Tally() }

        for ((qid, variants) in groups) {
            val witnesses = variants.sumOf { it.voters.size }
            if (witnesses < quorum) {
                variants.forEach { g -> g.voters.forEach { t(it).orphan++ } }
                continue
            }
            val majority = variants.maxWithOrNull(
                compareBy<VoteGroup>({ it.voters.size }, { it.voters.sorted().joinToString(VOTER_SEP.toString()) })
            ) ?: continue
            for (g in variants) {
                if (g === majority) {
                    g.voters.forEach { t(it).agree++ }
                } else {
                    g.voters.forEach { m ->
                        val tally = t(m)
                        tally.diverge++
                        if (tally.sampleQid == null) {
                            tally.sampleQid = qid
                            tally.sampleMine = g.sample.take(70)
                            tally.sampleMajority = majority.sample.take(70)
                            tally.sampleMajVotes = majority.voters.size
                        }
                    }
                }
            }
        }
        return out
    }

    private fun pct(v: Double): String =
        if (v.isNaN()) "n/a" else String.format(Locale.US, "%.2f%%", v * 100.0)
}
