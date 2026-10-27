package taxonomy.dataset

import taxonomy.service.SnapshotSettings
import java.security.MessageDigest

/**
 * Shared fixture of the RP12 ARCH-V2-E-T tests (V2SplitInertnessTest, V2EnginePoolTest): a small
 * two-domain corpus with a linked duplicate and a sentinel-id duplicate of one question, the
 * legacy pinned id file, a fixed SnapshotSettings, and the digest the legacy goldens are taken
 * over. Every value here is a literal so the goldens pinned on base 32c4c72 stay reproducible.
 */
object V2Fixture {
    const val EVAL_TEXT = "What is the capital of France?"

    fun dataset(): Map<String, List<MMLUQuery>> = linkedMapOf(
        "Geography" to listOf(
            MMLUQuery(101, EVAL_TEXT, "Geography"),
            MMLUQuery(102, "What is the capital of Spain?", "Geography"),
            MMLUQuery(103, "What is the capital of Italy?", "Geography"),
            MMLUQuery(104, "What is the capital of Peru?", "Geography"),
            MMLUQuery(UNLINKED_QUERY_ID_BASE - 7, "  what IS the capital   of France? ", "Geography"),
            MMLUQuery(105, "What is the capital of France?", "Geography"),
        ),
        "History" to (1..12).map { MMLUQuery(200 + it, "History question number $it", "History") }
    )

    const val PINNED_JSON = """{ "Geography": [101, 102], "History": [201, 202, 203] }"""

    fun settings(): SnapshotSettings = SnapshotSettings(
        selectedDomains = listOf("Geography", "History"), maxDepth = 8, enableLabeling = false,
        proposalSeparationBar = 0.025, minClusterSize = 55, splitFunction = SplitSide.stamp("ptest0000000000000")
    )

    fun sha(s: String): String = MessageDigest.getInstance("SHA-256").digest(s.toByteArray(Charsets.UTF_8)).joinToString("") { "%02x".format(it) }

    /** pool | closed | train ids | test ids | gate ids | sha(reserved json), every id list sorted. */
    fun digest(s: MMLUDatasetFetcher.Split, reservedJson: String): String {
        fun ids(m: Map<String, List<MMLUQuery>>) = m.values.flatten().map { it.id }.sorted().joinToString(",")
        return listOf(s.poolId, s.closedByContent, ids(s.train), ids(s.test), s.gate.sorted().joinToString(","), sha(reservedJson))
            .joinToString("|")
    }
}
