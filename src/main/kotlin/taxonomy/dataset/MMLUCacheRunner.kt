package taxonomy.dataset

import kotlinx.coroutines.runBlocking
import org.slf4j.LoggerFactory
import org.springframework.beans.factory.annotation.Value
import org.springframework.boot.CommandLineRunner
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty
import org.springframework.stereotype.Component

/**
 * Cache-Only Runner: Fetches the MMLU Pro dataset and precomputes embeddings.
 * Runs ONLY when the application is started with: --app.mode=mmlupro-cache
 */
@Component
@ConditionalOnProperty(prefix = "app", name = ["mode"], havingValue = "mmlupro-cache")
class MMLUCacheRunner(
    @Value("\${dataset.sample:500}") private val samples: Int,
    private val mmluDatasetFetcher: MMLUDatasetFetcher,
    private val embeddingCache: EmbeddingCache
) : CommandLineRunner {

    private val log = LoggerFactory.getLogger("MMLUCacheRunner")

    override fun run(vararg args: String?) = runBlocking {
        log.info("Starting MMLU Pro Dataset Fetcher & Embedding Cacher...")

        // 1. Fetch MMLU Pro Data
        val mmluProDataset = mmluDatasetFetcher.fetchDataset(maxQueries = samples)

        // 2. Extract and flatten queries
        val queries = mmluProDataset.values.flatten()
        log.info("Extracted ${queries.size} total queries. Precomputing embeddings...")

        // 3. Precompute and cache in existing vector cache
        embeddingCache.precompute(queries)

        log.info("Finished MMLU Pro Cache job. Shutting down safely.")
    }
}