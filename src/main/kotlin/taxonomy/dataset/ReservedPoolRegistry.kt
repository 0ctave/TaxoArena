package taxonomy.dataset

import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import java.io.File

/**
 * The registry of pinned reserved pools, experiment_configs/reserved_pools.json, read by both
 * languages (tools/analysis/pool_guard.py is the Python reader). A pinned pool is an explicit id
 * file whose judgeable ids hash to the pool id ([ReservedPool.computePoolId]); the registry maps
 * the id to that file, to the dataset DB whose `reserved_pool` rows corroborate it, and to the
 * corpus set the pool is versioned with. There is no active pool anywhere: a run names the pool
 * it scores, and the registry says what that pool is.
 */
object ReservedPoolRegistry {
    const val DEFAULT_PATH = "experiment_configs/reserved_pools.json"

    @Serializable
    data class Entry(
        val db: String,
        val id_file: String,
        val corpus_set: List<String>,
        val corpus_set_version: String? = null,
        val judgeable: Int,
        val sentinels: Int = 0,
        val keys: Int = 0,
        val snapshot_of_origin: String? = null,
        val member_pools: Map<String, String> = emptyMap()
    )

    @Serializable
    private data class Registry(val pools: Map<String, Entry>)

    private val json = Json { ignoreUnknownKeys = true }

    fun load(path: File = File(DEFAULT_PATH)): Map<String, Entry> {
        require(path.isFile) { "[POOL-REGISTRY] ${path.path} not found; run from the repo root" }
        return json.decodeFromString<Registry>(path.readText()).pools
    }

    /** The registry entry for [poolId]; throws with the registry path when the id is unknown. */
    fun resolve(poolId: String, path: File = File(DEFAULT_PATH)): Entry {
        require(poolId.isNotBlank()) { "[POOL-REGISTRY] a pool id is mandatory (see ${path.path})" }
        val pools = load(path)
        return pools[poolId] ?: throw IllegalArgumentException(
            "[POOL-REGISTRY] pool '$poolId' is not in ${path.path} (known: ${pools.keys.sorted()})"
        )
    }

    /** `key -> ids` exactly as the id file lists them (sentinels included). */
    fun idFile(entry: Entry, root: File = File(".")): Map<String, List<Int>> =
        Json.decodeFromString<Map<String, List<Int>>>(File(root, entry.id_file).readText())

    /** Judgeable ids by key: sentinels dropped, empty keys dropped; what [ReservedPool.computePoolId] hashes. */
    fun judgeable(ids: Map<String, List<Int>>): Map<String, List<Int>> =
        ids.mapValues { (_, v) -> v.filter { it > 0 } }.filterValues { it.isNotEmpty() }

    /**
     * Reproduces [poolId] from its id file: the judgeable ids hash to it and the count matches
     * the registry. Returns the judgeable ids by key. This is the Kotlin half of the 3/3 criterion.
     */
    fun reproduce(poolId: String, path: File = File(DEFAULT_PATH), root: File = File(".")): Map<String, List<Int>> {
        val entry = resolve(poolId, path)
        val ids = judgeable(idFile(entry, root))
        val got = ReservedPool.computePoolId(ids)
        check(got == poolId) { "[POOL-REGISTRY] ${entry.id_file} hashes to $got, not $poolId" }
        val n = ids.values.sumOf { it.size }
        check(n == entry.judgeable) { "[POOL-REGISTRY] ${entry.id_file} lists $n judgeable ids, registry says ${entry.judgeable}" }
        for ((source, memberId) in entry.member_pools) {
            val member = ids.filterKeys { CorpusDomains.sourceOfKey(it) == source }
            val mid = ReservedPool.computePoolId(member)
            check(mid == memberId) { "[POOL-REGISTRY] member pool $source of $poolId hashes to $mid, registry says $memberId" }
        }
        return ids
    }
}
