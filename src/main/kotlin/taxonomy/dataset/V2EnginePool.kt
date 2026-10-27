package taxonomy.dataset

import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.int
import kotlinx.serialization.json.jsonArray
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import java.io.File
import java.security.MessageDigest

/**
 * The engine's reserved-pool file of a v2 pool (RP12 ARCH-V2-E-T, engineering prerequisite 1; the
 * orchestrator's scope ruling of 2026-09-29: the engine takes the Python v2 CK-CLOSE closure AS GIVEN,
 * it does not re-implement it).
 *
 * The file is written ONCE by tools/analysis/v2_engine_pool.py from the draw of record's committed side
 * export and the engine's own rows (that script's docstring carries its checks S1-S6). It lists the
 * engine ids of every loaded mmlu_pro row by side: EVAL and GATE are RESERVED (sentinel ids among them,
 * negative, listed explicitly), TRAIN is listed so the split can be checked one-to-one.
 *
 * [load] re-checks, FATAL on any failure (IllegalStateException / IllegalArgumentException, "[SPLIT-V2]"):
 *  L1 format, rule and a `pv2_` + 16 hex pool id;
 *  L2 the id lists are duplicate-free and pairwise disjoint, every sentinel is a reserved negative id, and
 *     the file's counts equal the list sizes;
 *  L3 the side export the file names hashes (LF rendering, sha256) to the pinned `sha256_lf`, and its
 *     header row count equals its rows;
 *  L4 the pool id recomputed here from the export (pv2_ + sha256 of the sorted EVAL component ids with a
 *     member in the file's corpus, LF-joined, first 16 hex) equals the file's pool id: the Kotlin half of
 *     the two-language pool-id check (data_v2/split.py pool_id);
 *  L5 [globalReservedKeys] = the stem keys of EVERY non-TRAIN item of the export, over ALL corpora of the
 *     draw (sentinels included, since they are items): the GLOBAL closure set the split and every
 *     TrainOnlyGuard site check against.
 */
data class V2EnginePool(
    val poolId: String,
    val corpus: String,
    val rule: String,
    val filePath: String,
    val fileSha256Lf: String,
    val sideExportPath: String,
    val sideSha256Lf: String,
    val sideTableSha: String,
    val splitSha256: String,
    val evalIds: Set<Int>,
    val gateIds: Set<Int>,
    val trainIds: Set<Int>,
    val sentinelIds: Set<Int>,
    val globalReservedKeys: Set<String>,
    val evalComponents: Int,
    /**
     * RP12 B2: a multi-corpus pool file (the union member pv2_1575de61bb20e977 over corpus_questions) names the
     * corpus namespaces of its ids (DB source -> id offset, width [CorpusRegistry.NAMESPACE_WIDTH]); a per-corpus
     * member build loads ONE source, and the one-to-one checks run on the namespaces it loaded ([scopedTo]). null
     * (the single-corpus pv2_41dbd3dbcd399df0 file) = every list is checked whole, as before.
     */
    val namespaces: Map<String, Int>? = null
) {
    val reservedIds: Set<Int> = evalIds + gateIds

    /** The namespaces (DB sources) holding at least one of [loadedIds]; empty when the file declares none. */
    fun namespacesOf(loadedIds: Collection<Int>): List<String> {
        val ns = namespaces ?: return emptyList()
        return ns.entries.filter { (_, off) -> loadedIds.any { it >= off && it < off + CorpusRegistry.NAMESPACE_WIDTH } }
            .map { it.key }.sorted()
    }

    /** (train ids, reserved ids) restricted to the namespaces [loaded]; the whole lists when the file declares none. */
    fun scopedTo(loaded: List<String>): Pair<Set<Int>, Set<Int>> {
        val ns = namespaces ?: return trainIds to reservedIds
        val offs = loaded.map { ns.getValue(it) }
        fun inScope(i: Int) = offs.any { i >= it && i < it + CorpusRegistry.NAMESPACE_WIDTH }
        return trainIds.filterTo(HashSet()) { inScope(it) } to reservedIds.filterTo(HashSet()) { inScope(it) }
    }

    companion object {
        const val FORMAT = "taxoarena-engine-pool-v2"
        const val RULE = "CK-CLOSE-v2"
        const val SIDE_EXPORT_FORMAT = "taxoarena-side-export-v1"
        val SIDE_COLS = listOf("item_id", "component_id", "side", "stratum_source", "stratum_domain", "corpora")
        private val POOL_ID = Regex("pv2_[0-9a-f]{16}")

        fun sha256Hex(bytes: ByteArray): String =
            MessageDigest.getInstance("SHA-256").digest(bytes).joinToString("") { "%02x".format(it) }

        /** The LF rendering of a text file's bytes (CRLF -> LF); a bare CR is refused. */
        fun lfBytes(file: File): ByteArray {
            val s = String(file.readBytes(), Charsets.UTF_8).replace("\r\n", "\n")
            check('\r' !in s) { "[SPLIT-V2] $file carries a bare CR" }
            return s.toByteArray(Charsets.UTF_8)
        }

        /** One side-export row. */
        data class SideRow(val component: String, val side: Side, val corpora: Set<String>)

        /** Parses the export's LF rendering: item_id -> row, and the header's (rows, table_sha, split_sha256). */
        fun readSideExport(lf: String, where: String): Pair<Map<String, SideRow>, Triple<Int, String, String>> {
            val lines = lf.split("\n")
            check(lines.last() == "") { "[SPLIT-V2] side export $where does not end with LF" }
            val head = lines[0].split(Regex("\\s+")).filter { it.isNotEmpty() }
            check(head.size == 5 && head[0] == "#" && head[1] == SIDE_EXPORT_FORMAT) { "[SPLIT-V2] side export $where: bad header '${lines[0]}'" }
            val hdr = head.drop(2).associate { it.substringBefore('=') to it.substringAfter('=') }
            check(lines[1].split("\t") == SIDE_COLS) { "[SPLIT-V2] side export $where: bad column header" }
            val items = LinkedHashMap<String, SideRow>()
            for (ln in lines.subList(2, lines.size - 1)) {
                val c = ln.split("\t")
                check(c.size == SIDE_COLS.size) { "[SPLIT-V2] side export $where: malformed row '${ln.take(80)}'" }
                val side = Side.entries.firstOrNull { it.name == c[2] } ?: error("[SPLIT-V2] side export $where: side '${c[2]}' of ${c[0]}")
                check(c[0].startsWith("i:")) { "[SPLIT-V2] side export $where: item id '${c[0]}' lacks the i: prefix" }
                check(items.put(c[0], SideRow(c[1], side, c[5].split(",").toSet())) == null) { "[SPLIT-V2] side export $where: item ${c[0]} repeated" }
            }
            val rows = hdr["rows"]?.toIntOrNull() ?: error("[SPLIT-V2] side export $where: header lacks rows=")
            check(rows == items.size) { "[SPLIT-V2] side export $where: header rows=$rows but ${items.size} rows" }
            return items to Triple(rows, hdr["table_sha"] ?: error("[SPLIT-V2] no table_sha"), hdr["split_sha256"] ?: error("[SPLIT-V2] no split_sha256"))
        }

        /** pv2_ + sha256(sorted EVAL component ids with a member in [corpus], LF-joined)[:16] (data_v2/split.py pool_id). */
        fun poolIdOf(items: Map<String, SideRow>, corpus: String): Pair<String, Int> {
            val comps = items.values.filter { it.side == Side.EVAL && corpus in it.corpora }.map { it.component }.toSortedSet()
            // Python sorts str by code point; component ids are "c:" + lowercase hex, so the orders agree.
            return "pv2_" + sha256Hex(comps.joinToString("\n").toByteArray(Charsets.UTF_8)).take(16) to comps.size
        }

        private fun ids(o: JsonObject, key: String): Set<Int> {
            val arr = (o[key] ?: error("[SPLIT-V2] engine pool file lacks '$key'")).jsonArray
            val list = arr.map { it.jsonPrimitive.int }
            val set = list.toSet()
            check(set.size == list.size) { "[SPLIT-V2] engine pool file: '$key' repeats ${list.size - set.size} id(s)" }
            return set
        }

        private fun str(o: JsonObject, key: String): String =
            ((o[key] ?: error("[SPLIT-V2] engine pool file lacks '$key'")) as? JsonPrimitive)?.takeIf { it.isString }?.content
                ?: error("[SPLIT-V2] engine pool file: '$key' is not a string")

        /** Loads and checks (L1-L5). A relative side-export path resolves against [baseDir] (the run's working dir). */
        fun load(file: File, baseDir: File = File(".")): V2EnginePool {
            check(file.isFile) { "[SPLIT-V2] engine pool file $file does not exist" }
            val lf = lfBytes(file)
            val o = Json.parseToJsonElement(String(lf, Charsets.UTF_8)).jsonObject
            // L1
            check(str(o, "format") == FORMAT) { "[SPLIT-V2] $file: format '${str(o, "format")}' is not $FORMAT" }
            check(str(o, "rule") == RULE) { "[SPLIT-V2] $file: rule '${str(o, "rule")}' is not $RULE" }
            val poolId = str(o, "pool_id")
            check(POOL_ID.matches(poolId)) { "[SPLIT-V2] $file: pool id '$poolId' is not pv2_ + 16 hex" }
            val corpus = str(o, "corpus")
            // L2
            val eval = ids(o, "eval_ids"); val gate = ids(o, "gate_ids"); val train = ids(o, "train_ids"); val sentinels = ids(o, "sentinel_ids")
            check((eval intersect gate).isEmpty() && (eval intersect train).isEmpty() && (gate intersect train).isEmpty()) {
                "[SPLIT-V2] $file: the eval / gate / train lists intersect (${(eval intersect gate).size} / ${(eval intersect train).size} / ${(gate intersect train).size})"
            }
            check(sentinels.all { it < 0 && (it in eval || it in gate) }) {
                "[SPLIT-V2] $file: sentinel ids must be negative reserved ids (${sentinels.filter { !(it < 0 && (it in eval || it in gate)) }.take(5)})"
            }
            check((eval + gate).filter { it < 0 }.toSet() == sentinels) { "[SPLIT-V2] $file: a negative reserved id is not listed as a sentinel" }
            // RP12 B2: optional namespaces; when present every listed id lies in exactly one of them
            val namespaces: Map<String, Int>? = o["namespaces"]?.jsonObject?.mapValues { it.value.jsonPrimitive.int }
            if (namespaces != null) {
                check(namespaces.isNotEmpty() && namespaces.values.toSet().size == namespaces.size) { "[SPLIT-V2] $file: namespaces empty or offsets repeated" }
                val outside = (eval + gate + train).filter { i -> namespaces.values.count { i >= it && i < it + CorpusRegistry.NAMESPACE_WIDTH } != 1 }
                check(outside.isEmpty()) { "[SPLIT-V2] $file: ${outside.size} id(s) lie in no declared namespace (first ${outside.sorted().take(5)})" }
            }
            val counts = (o["counts"] ?: error("[SPLIT-V2] engine pool file lacks 'counts'")).jsonObject
            for ((k, v) in listOf("eval" to eval.size, "gate" to gate.size, "train" to train.size, "reserved" to eval.size + gate.size, "sentinels_reserved" to sentinels.size)) {
                check(counts[k]?.jsonPrimitive?.int == v) { "[SPLIT-V2] $file: counts.$k = ${counts[k]} but the list holds $v" }
            }
            // L3
            val se = (o["side_export"] ?: error("[SPLIT-V2] engine pool file lacks 'side_export'")).jsonObject
            val sidePath = str(se, "path")
            val sideFile = File(sidePath).let { if (it.isAbsolute) it else File(baseDir, sidePath) }
            check(sideFile.isFile) { "[SPLIT-V2] side export $sideFile does not exist" }
            val sideLf = lfBytes(sideFile)
            val sideSha = sha256Hex(sideLf)
            check(sideSha == str(se, "sha256_lf")) { "[SPLIT-V2] side export $sidePath: sha256(LF) $sideSha != the pinned ${str(se, "sha256_lf")}" }
            val (items, hdr) = readSideExport(String(sideLf, Charsets.UTF_8), sidePath)
            check(hdr.second == str(se, "table_sha")) { "[SPLIT-V2] side export $sidePath: header table_sha ${hdr.second} != the file's ${str(se, "table_sha")}" }
            // L4
            val (recomputed, nComp) = poolIdOf(items, corpus)
            check(recomputed == poolId) { "[SPLIT-V2] $file: the side export's $corpus pool is $recomputed, not $poolId" }
            // L5
            val global = items.filterValues { it.side != Side.TRAIN }.keys.mapTo(HashSet()) { it.removePrefix("i:") }
            return V2EnginePool(
                poolId = poolId, corpus = corpus, rule = RULE, filePath = file.path, fileSha256Lf = sha256Hex(lf),
                sideExportPath = sidePath, sideSha256Lf = sideSha, sideTableSha = hdr.second, splitSha256 = hdr.third,
                evalIds = eval, gateIds = gate, trainIds = train, sentinelIds = sentinels,
                globalReservedKeys = global, evalComponents = nComp, namespaces = namespaces
            )
        }
    }

    /**
     * The runner's v2 wiring after [MMLUDatasetFetcher.splitByV2Pool], in one testable place: installs the
     * GLOBAL reserved keys for every TrainOnlyGuard site (tree after construction, saveSnapshot, judge
     * induction), records the stamp in the diagnostics manifest (`split_v2`), and returns the stamp the
     * runner writes into gate_ids.json and the snapshot. [configFile] is the run's TOML (its LF sha is stamped).
     */
    fun activate(split: MMLUDatasetFetcher.Split, configFile: File, seed: Long?, constructionOrderShuffleSeed: Long?): V2BuildStamp {
        taxonomy.model.TrainOnlyGuard.GlobalReserved.install(globalReservedKeys, poolId)
        val test = split.test.values.flatten()
        val loaded = split.train.values.flatten().map { it.id } + test.map { it.id }
        val s = stamp(
            legacyPoolId = split.poolId, trainRows = split.train.values.sumOf { it.size }, reservedRows = test.size,
            gateRows = test.count { it.id in gateIds }, sentinelRows = test.count { it.id < 0 },
            configSha256Lf = sha256Hex(lfBytes(configFile)), seed = seed, constructionOrderShuffleSeed = constructionOrderShuffleSeed
        ).let { if (namespaces != null) it.copy(namespacesLoaded = namespacesOf(loaded)) else it }
        taxonomy.diagnostics.DiagnosticsBundle.recordSplitV2(s.toManifest())
        return s
    }

    /**
     * RP12 B2, the union graft on this pool (unionSnapshots + v2PoolFile): every member snapshot must carry a v2 build
     * stamp of the SAME draw (side export sha and rule); a member built on THIS pool must hold, as its reserved ids,
     * exactly this file's reserved ids of the namespaces it loaded; a member built on another pool of the same draw
     * (the MMLU-Pro member on pv2_41dbd3dbcd399df0, the mmlu_pro table) is admitted on its own stamp and printed.
     * FATAL ("[SPLIT-V2] UNION") otherwise. Returns the printed lines.
     */
    data class UnionMember(val snapshotId: String, val source: String, val stamp: V2BuildStamp?, val reservedIds: Set<Int>)

    fun checkUnionMembers(members: List<UnionMember>, allowedForeign: Set<Pair<String, String>> = emptySet()): List<String> {
        val out = ArrayList<String>()
        for (m in members) {
            val s = m.stamp ?: error("[SPLIT-V2] UNION member ${m.snapshotId} (${m.source}) carries no v2 build stamp: a v2 graft grafts v2 members only")
            check(s.rule == rule && s.sideExportSha256Lf == sideSha256Lf) {
                "[SPLIT-V2] UNION member ${m.snapshotId} (${m.source}) is of another draw (rule ${s.rule}, side export ${s.sideExportSha256Lf.take(16)} vs ${sideSha256Lf.take(16)})"
            }
            if (s.poolId == poolId) {
                val ns = s.namespacesLoaded ?: error("[SPLIT-V2] UNION member ${m.snapshotId} (${m.source}) on $poolId names no loaded namespace")
                val want = scopedTo(ns).second
                check(m.reservedIds == want) {
                    "[SPLIT-V2] UNION member ${m.snapshotId} (${m.source}): reserved ${m.reservedIds.size} ids vs the file's ${want.size} for $ns" +
                        " (only in the snapshot: ${(m.reservedIds - want).sorted().take(5)}; only in the file: ${(want - m.reservedIds).sorted().take(5)})"
                }
                out += "[SPLIT-V2] UNION member ${m.snapshotId} (${m.source}) on $poolId, namespaces $ns: reserved ${want.size} ids == the file's"
            } else {
                // READY_rp12_et D-2: a foreign-pool member is admitted only when the graft's TOML names its pool AND its
                // engine pool file's LF sha (v2ForeignMembers); the stamp alone is not enough.
                check((s.poolId to s.enginePoolSha256Lf) in allowedForeign) {
                    "[SPLIT-V2] UNION member ${m.snapshotId} (${m.source}) is on the foreign pool ${s.poolId} (engine pool sha256(LF)" +
                        " ${s.enginePoolSha256Lf.take(16)}), not on the graft's allow-list v2ForeignMembers ${allowedForeign.map { "${it.first}:${it.second.take(16)}" }}"
                }
                out += "[SPLIT-V2] UNION member ${m.snapshotId} (${m.source}) on the allow-listed foreign pool ${s.poolId} of the same draw" +
                    " (engine pool sha256(LF) ${s.enginePoolSha256Lf}); admitted"
            }
        }
        return out
    }

    /**
     * RP12 B2, the union graft's v2 wiring in one testable place: [checkUnionMembers] (FATAL on a defect), then the
     * GLOBAL reserved keys installed (the after-graft guard and saveSnapshot read them), then the union's stamp
     * (namespacesLoaded = the members' sources, the legacy id-list union pool beside the v2 pool id). Returns the
     * printed lines and the stamp.
     */
    fun activateUnion(members: List<UnionMember>, legacyPoolId: String, trainRows: Int, unionPool: Map<String, List<Int>>,
                      seed: Long?, configFile: File? = null, allowedForeign: Set<Pair<String, String>> = emptySet()): Pair<List<String>, V2BuildStamp> {
        val lines = checkUnionMembers(members, allowedForeign)
        taxonomy.model.TrainOnlyGuard.GlobalReserved.install(globalReservedKeys, poolId)
        val all = unionPool.values.flatten()
        val s = stamp(
            legacyPoolId = legacyPoolId, trainRows = trainRows, reservedRows = all.size, gateRows = all.count { it in gateIds },
            sentinelRows = all.count { it < 0 }, configSha256Lf = configFile?.let { sha256Hex(lfBytes(it)) }, seed = seed,
            constructionOrderShuffleSeed = null
        ).copy(namespacesLoaded = members.map { it.source })
        return (lines + "[TRAIN-ONLY] union graft: global reserved keys installed: ${globalReservedKeys.size} ($poolId)") to s
    }

    /** The build stamp of a construction on this pool (the snapshot's `settings.buildStamp`, the manifest's `split_v2`). */
    fun stamp(legacyPoolId: String?, trainRows: Int, reservedRows: Int, gateRows: Int, sentinelRows: Int,
              configSha256Lf: String?, seed: Long?, constructionOrderShuffleSeed: Long?): V2BuildStamp =
        V2BuildStamp(
            rule = rule, poolId = poolId, corpus = corpus, enginePoolFile = filePath.replace('\\', '/'),
            enginePoolSha256Lf = fileSha256Lf, sideExportPath = sideExportPath, sideExportSha256Lf = sideSha256Lf,
            sideTableSha = sideTableSha, splitSha256 = splitSha256, legacyPoolId = legacyPoolId,
            trainRows = trainRows, reservedRows = reservedRows, gateRows = gateRows, sentinelRows = sentinelRows,
            globalReservedKeys = globalReservedKeys.size, configSha256Lf = configSha256Lf, seed = seed,
            constructionOrderShuffleSeed = constructionOrderShuffleSeed
        )
}

/**
 * Provenance of a v2 build, stamped IN the snapshot (SYNTHESIS section 2 Stage T "Provenance: stamped in the
 * snapshot"; gate G10 "the snapshot stamp equals the TOML, the manifest and the pointer file"). The same
 * values go to the snapshot's settings (`buildStamp`), the diagnostics manifest (`split_v2`, [toManifest])
 * and gate_ids.json. Absent (null, and not encoded) on every non-v2 build.
 */
@Serializable
data class V2BuildStamp(
    val rule: String,
    val poolId: String,
    val corpus: String,
    val enginePoolFile: String,
    val enginePoolSha256Lf: String,
    val sideExportPath: String,
    val sideExportSha256Lf: String,
    val sideTableSha: String,
    val splitSha256: String,
    val legacyPoolId: String?,
    val trainRows: Int,
    val reservedRows: Int,
    val gateRows: Int,
    val sentinelRows: Int,
    val globalReservedKeys: Int,
    val configSha256Lf: String?,
    val seed: Long?,
    val constructionOrderShuffleSeed: Long?,
    /** RP12 B2: the DB sources a namespaced (multi-corpus) pool file's build loaded; null on a single-corpus file. */
    val namespacesLoaded: List<String>? = null
) {
    fun toManifest(): Map<String, Any?> = linkedMapOf<String, Any?>(
        "rule" to rule, "pool_id" to poolId, "corpus" to corpus, "engine_pool_file" to enginePoolFile,
        "engine_pool_sha256_lf" to enginePoolSha256Lf, "side_export_path" to sideExportPath,
        "side_export_sha256_lf" to sideExportSha256Lf, "side_table_sha" to sideTableSha, "split_sha256" to splitSha256,
        "legacy_pool_id" to legacyPoolId, "train_rows" to trainRows, "reserved_rows" to reservedRows, "gate_rows" to gateRows,
        "sentinel_rows" to sentinelRows, "global_reserved_keys" to globalReservedKeys, "config_sha256_lf" to configSha256Lf,
        "seed" to seed, "construction_order_shuffle_seed" to constructionOrderShuffleSeed
    ).also { if (namespacesLoaded != null) it["namespaces_loaded"] = namespacesLoaded }
}

/** RP12 READY_rp12_et D-2: the graft's allow-list of foreign-pool members. */
object V2ForeignMembers {
    private val FOREIGN = Regex("(pv2_[0-9a-f]{16}):([0-9a-f]{64})")

    /** `v2ForeignMembers = ["pv2_<16 hex>:<64 hex sha256 of the engine pool file's LF rendering>"]` -> (pool, sha) pairs. */
    fun parseForeign(entries: List<String>): Set<Pair<String, String>> = entries.mapTo(LinkedHashSet()) { e ->
        val m = FOREIGN.matchEntire(e.trim()) ?: throw IllegalArgumentException(
            "[CONFIG] v2ForeignMembers entry '$e' is not pv2_<16 hex>:<64 hex sha256(LF) of the member's engine pool file>")
        m.groupValues[1] to m.groupValues[2]
    }
}
