package taxonomy.dataset

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotEquals
import org.junit.jupiter.api.Test

class MMLUDatasetFetcherProgressTest {

    @Test
    fun `unbounded full-dataset cap never reports Int MAX_VALUE as progress total`() {
        val total = MMLUDatasetFetcher.resolveProgressTotal(MMLUDatasetFetcher.UNBOUNDED_MAX_QUERIES)
        assertNotEquals(Int.MAX_VALUE, total, "Sentinel cap must not leak to the UI as the total")
        assertEquals(0, total, "Unknown total signals an indeterminate bar")
    }

    @Test
    fun `a real bounded cap is reported verbatim as the progress total`() {
        assertEquals(500, MMLUDatasetFetcher.resolveProgressTotal(500))
        assertEquals(12000, MMLUDatasetFetcher.resolveProgressTotal(12000))
    }

    @Test
    fun `non-positive cap is treated as unknown`() {
        assertEquals(0, MMLUDatasetFetcher.resolveProgressTotal(0))
        assertEquals(0, MMLUDatasetFetcher.resolveProgressTotal(-1))
    }
}
