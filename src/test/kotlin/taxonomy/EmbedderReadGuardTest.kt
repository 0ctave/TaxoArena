package taxonomy

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.api.io.TempDir
import taxonomy.service.SerialNode
import java.io.File
import java.nio.ByteBuffer
import kotlin.math.sqrt

/**
 * EMBEDDER-PLUMBING (RP08; docs/judge_v2_program.md L21754-L21772): every branch of the site-null read guard
 * EXECUTED on synthetic SQLite caches in a temp dir (no DB of record is opened). P-2 (iii) and (v) are proved here;
 * (i) and (ii) are exercised here on synthetic data (their proof legs of record run on the real caches in a W-window).
 */
class EmbedderReadGuardTest {

    @TempDir lateinit var tmp: File

    // ── synthetic caches ─────────────────────────────────────────────────────────
    private val rng = java.util.Random(20260927L)

    private fun unit(v: DoubleArray): DoubleArray { val n = sqrt(v.sumOf { it * it }); return DoubleArray(v.size) { v[it] / n } }

    /** Two well-separated clusters of 4096-d "native" vectors (a fixed random direction each, plus noise). */
    private fun clusterVectors(n: Int, dim: Int, seedDir: DoubleArray, noise: Double): List<DoubleArray> =
        List(n) { DoubleArray(dim) { i -> seedDir[i] + noise * rng.nextGaussian() } }

    private fun randomVectors(n: Int, dim: Int): List<DoubleArray> = List(n) { DoubleArray(dim) { rng.nextGaussian() } }

    private fun blob(v: DoubleArray): ByteArray {
        val b = ByteBuffer.allocate(4 * v.size)          // big-endian, as EmbeddingCache writes
        v.forEach { b.putFloat(it.toFloat()) }
        return b.array()
    }

    private fun makeCache(name: String, rows: Map<String, DoubleArray>, withQueries: Boolean = true, withEmbeddings: Boolean = true): File {
        val f = File(tmp, name)
        java.sql.DriverManager.getConnection("jdbc:sqlite:${f.absolutePath}").use { c ->
            c.createStatement().use { st ->
                if (withEmbeddings) st.execute("CREATE TABLE embeddings (query TEXT PRIMARY KEY, vector BLOB)")
                if (withQueries) st.execute("CREATE TABLE queries (id TEXT PRIMARY KEY, raw_text TEXT, distilled_text TEXT, ground_truth_category TEXT DEFAULT '', query_id INTEGER DEFAULT -1)")
                if (!withQueries && !withEmbeddings) st.execute("CREATE TABLE other (a)")
            }
            if (withEmbeddings && withQueries) {
                c.prepareStatement("INSERT INTO queries (id, raw_text, distilled_text) VALUES (?, ?, ?)").use { ps ->
                    rows.keys.forEach { id -> ps.setString(1, id); ps.setString(2, "text $id"); ps.setString(3, "text $id"); ps.executeUpdate() }
                }
                c.prepareStatement("INSERT INTO embeddings (query, vector) VALUES (?, ?)").use { ps ->
                    rows.forEach { (id, v) -> ps.setString(1, "text $id"); ps.setBytes(2, blob(v)); ps.executeUpdate() }
                }
            }
        }
        return f
    }

    private val slice = 256
    private val idsA = List(60) { "q_a%02d".format(it) }
    private val idsB = List(60) { "q_b%02d".format(it) }
    private val dirA = DoubleArray(4096) { rng.nextGaussian() * 0.05 }
    private val dirB = DoubleArray(4096) { rng.nextGaussian() * 0.05 }
    private val native: Map<String, DoubleArray> by lazy {
        val va = clusterVectors(idsA.size, 4096, dirA, 0.02)
        val vb = clusterVectors(idsB.size, 4096, dirB, 0.02)
        (idsA.zip(va) + idsB.zip(vb)).toMap()
    }

    /** vmfMu as the fitter computes it: normalised mean of the sliced unit vectors (unit weights here). */
    private fun mu(ids: List<String>, vecs: Map<String, DoubleArray>): FloatArray {
        val m = DoubleArray(slice)
        ids.forEach { id -> val u = unit(vecs.getValue(id).copyOf(slice)); for (i in 0 until slice) m[i] += u[i] }
        val u = unit(m)
        return FloatArray(slice) { u[it].toFloat() }
    }

    private fun tree(vecs: Map<String, DoubleArray>, muLen: Int = slice): Pair<List<SerialNode>, Map<String, SerialNode>> {
        fun fit(ids: List<String>) = mu(ids, vecs).let { m -> if (muLen == slice) m else m.copyOf(muLen) }
        val a = SerialNode("n2", "A", 1, emptyList(), parentIds = listOf("n1"), vmfMu = fit(idsA), queryIds = idsA)
        val b = SerialNode("n3", "B", 1, emptyList(), parentIds = listOf("n1"), vmfMu = fit(idsB), queryIds = idsB)
        val root = SerialNode("n1", "ROOT", 0, listOf("n2", "n3"), parentIds = emptyList(), vmfMu = fit(idsA + idsB), dasguptaDeltaNorm = 0.2)
        val byId = listOf(root, a, b).associateBy { it.id }
        return listOf(root) to byId
    }

    private fun region(n: SerialNode, byId: Map<String, SerialNode>): Set<String> {
        val out = LinkedHashSet<String>(); val st = ArrayDeque(listOf(n))
        while (st.isNotEmpty()) { val c = st.removeLast(); out.addAll(c.queryIds); c.childIds.forEach { byId[it]?.let(st::add) } }
        return out
    }

    private fun capture(block: () -> Unit): Pair<String, Throwable?> {
        val old = System.out
        val bo = java.io.ByteArrayOutputStream()
        System.setOut(java.io.PrintStream(bo, true, "UTF-8"))
        val t = try { block(); null } catch (e: Throwable) { e } finally { System.setOut(old) }
        val text = bo.toString("UTF-8")
        print(text)                                         // echoed to the test log (the executed lines)
        return text to t
    }

    private fun guard(cache: File, vecsForMu: Map<String, DoubleArray>, model: String, muLen: Int = slice): Pair<String, Throwable?> {
        val (sites, byId) = tree(vecsForMu, muLen)
        return capture {
            val ro = org.sqlite.SQLiteConfig().apply { setReadOnly(true) }.toProperties()
            java.sql.DriverManager.getConnection("jdbc:sqlite:${cache.absolutePath}", ro).use { c ->
                EmbedderReadGuard.run(c, cache.path, sites, { region(it, byId) }, slice, EmbedderReadGuard.ModelChoice(model, "test"))
            }
        }
    }

    // ── (c) the vmfMu cosine guard and the dimension check ───────────────────────
    @Test
    fun `P-2 (i) the right embedder is ADMITTED, min cos and budget printed`() {
        val cache = makeCache("right.db", native)
        val (out, err) = guard(cache, native, "qwen3-embedding:latest")
        assertEquals(null, err, out)
        assertTrue(Regex("""\[EMB-GUARD] vmfMu cosine over 1 sites: min (0\.99\d\d|1\.0000) .* budget 0\.99 -> ADMIT""").containsMatchIn(out), out)
        assertTrue(out.contains("raw dims {4096=120}"), out)
    }

    @Test
    fun `P-2 (ii) a wrong embedder (other vectors, 768-d) is REFUSED, cosines printed below 0_2`() {
        val nomicLike = (idsA + idsB).associateWith { DoubleArray(768) { rng.nextGaussian() } }
        val cache = makeCache("embeddings_cache_nomic-embed-text_latest.db", nomicLike)
        val (out, err) = guard(cache, native, "qwen3-embedding:latest")
        assertTrue(err is EmbedderReadGuard.Refusal, out)
        assertTrue(out.contains("-> REFUSE"), out)
        assertTrue(err!!.message!!.contains("raw vector dimensions {768=120} != {4096}"), err.message)
        assertTrue(err.message!!.contains("< budget 0.99"), err.message)
        val cos = Regex("""site n1\s+n=120\s+found=120\s+cos=(-?[0-9.]+)""").find(out)!!.groupValues[1].toDouble()
        assertTrue(cos < 0.2, "wrong-embedder cosine $cos")
    }

    @Test
    fun `the cosine branch alone refuses (right dimension, wrong vectors)`() {
        val cache = makeCache("wrong4096.db", (idsA + idsB).associateWith { DoubleArray(4096) { rng.nextGaussian() } })
        val (out, err) = guard(cache, native, "qwen3-embedding:latest")
        assertTrue(err is EmbedderReadGuard.Refusal, out)
        assertTrue(err!!.message!!.contains("< budget 0.99") && !err.message!!.contains("raw vector dimensions"), err.message)
    }

    @Test
    fun `the dimension branch alone refuses (right vectors, model with another native dimension)`() {
        val cache = makeCache("right2.db", native)
        val (out, err) = guard(cache, native, "nomic-embed-text")       // untagged -> :latest, native 768
        assertTrue(err is EmbedderReadGuard.Refusal, out)
        assertTrue(err!!.message!!.contains("raw vector dimensions {4096=120} != {768}") && !err.message!!.contains("budget"), err.message)
        assertTrue(out.contains("min 1.0000") || out.contains("min 0.99"), out)   // the cosine is still printed
    }

    @Test
    fun `a mixed-length read refuses (the vacuous full size below slice check is replaced)`() {
        val mixed = native.toMutableMap()
        mixed[idsA[0]] = DoubleArray(768) { rng.nextGaussian() }            // 768 > 256: the old check admitted it
        val cache = makeCache("mixed.db", mixed)
        val (out, err) = guard(cache, native, "qwen3-embedding:latest")
        assertTrue(err is EmbedderReadGuard.Refusal, out)
        assertTrue(err!!.message!!.contains("{768=1, 4096=119}"), err.message)
    }

    @Test
    fun `a vmfMu of the wrong length and an unknown model refuse`() {
        val cache = makeCache("right3.db", native)
        val (o1, e1) = guard(cache, native, "qwen3-embedding:latest", muLen = 512)
        assertTrue(e1 is EmbedderReadGuard.Refusal && e1.message!!.contains("vmfMu length 512 != slice width 256"), o1)
        val (o2, e2) = guard(cache, native, "some-new-embedder:v1")
        assertTrue(e2 is EmbedderReadGuard.Refusal && e2.message!!.contains("no declared native dimension"), o2)
    }

    // ── READY_w0_rp08 F1 (H1): the MULTI-SITE gate, with known expected values ─────
    /** Two accepted split sites: n1 (root, A+B, 120 ids) and n3 (B, splitting into n6 = B[:30], n7 = B[30:]); [muN3] overrides n3's vmfMu. */
    private fun twoSiteTree(vecs: Map<String, DoubleArray>, muN3: FloatArray? = null): Pair<List<SerialNode>, Map<String, SerialNode>> {
        val a = SerialNode("n2", "A", 1, emptyList(), parentIds = listOf("n1"), vmfMu = mu(idsA, vecs), queryIds = idsA)
        val b1 = SerialNode("n6", "B1", 2, emptyList(), parentIds = listOf("n3"), vmfMu = mu(idsB.take(30), vecs), queryIds = idsB.take(30))
        val b2 = SerialNode("n7", "B2", 2, emptyList(), parentIds = listOf("n3"), vmfMu = mu(idsB.drop(30), vecs), queryIds = idsB.drop(30))
        val b = SerialNode("n3", "B", 1, listOf("n6", "n7"), parentIds = listOf("n1"), vmfMu = muN3 ?: mu(idsB, vecs), dasguptaDeltaNorm = 0.1)
        val root = SerialNode("n1", "ROOT", 0, listOf("n2", "n3"), parentIds = emptyList(), vmfMu = mu(idsA + idsB, vecs), dasguptaDeltaNorm = 0.2)
        val byId = listOf(root, a, b, b1, b2).associateBy { it.id }
        // the harness's own site filter (SeparationNullBySizeTest siteNull): childIds >= 2 and dasguptaDeltaNorm > 0
        return byId.values.filter { it.childIds.size >= 2 && it.dasguptaDeltaNorm > 0.0 }.sortedBy { it.id } to byId
    }

    private fun guardSites(cache: File, sites: List<SerialNode>, byId: Map<String, SerialNode>): Triple<String, Throwable?, EmbedderReadGuard.Result?> {
        var res: EmbedderReadGuard.Result? = null
        val (out, err) = capture {
            val ro = org.sqlite.SQLiteConfig().apply { setReadOnly(true) }.toProperties()
            java.sql.DriverManager.getConnection("jdbc:sqlite:${cache.absolutePath}", ro).use { c ->
                res = EmbedderReadGuard.run(c, cache.path, sites, { region(it, byId) }, slice, EmbedderReadGuard.ModelChoice("qwen3-embedding:latest", "test"))
            }
        }
        return Triple(out, err, res)
    }

    private fun expectedCos(ids: List<String>, m: FloatArray): Double =
        EmbedderReadGuard.cosine(ids.map { unit(native.getValue(it).copyOf(slice)) }, m)

    @Test
    fun `F1 a correct two-site tree is ADMITTED, each site read on its own region`() {
        val cache = makeCache("two_site.db", native)
        val (sites, byId) = twoSiteTree(native)
        assertEquals(listOf("n1", "n3"), sites.map { it.id })
        val (out, err, res) = guardSites(cache, sites, byId)
        assertEquals(null, err, out)
        assertEquals(listOf(Triple("n1", 120, 120), Triple("n3", 60, 60)), res!!.sites.map { Triple(it.id, it.n, it.found) })
        val exp = minOf(expectedCos(idsA + idsB, byId.getValue("n1").vmfMu!!), expectedCos(idsB, byId.getValue("n3").vmfMu!!))
        assertEquals(exp, res.minCos, 1e-12)
        assertTrue(out.contains("vmfMu cosine over 2 sites"), out)
    }

    @Test
    fun `F1 a wrong vmfMu at the SECOND site REFUSES and names it as the minimum while the root alone admits`() {
        val cache = makeCache("two_site_bad.db", native)
        val muA = mu(idsA, native)
        val (sites, byId) = twoSiteTree(native, muN3 = muA)
        val cRoot = expectedCos(idsA + idsB, byId.getValue("n1").vmfMu!!)
        val c3 = expectedCos(idsB, muA)
        assertTrue(cRoot >= EmbedderReadGuard.COS_BUDGET && c3 < 0.5, "fixture: root $cRoot, n3 $c3")
        val (out, err, _) = guardSites(cache, sites, byId)
        assertTrue(err is EmbedderReadGuard.Refusal, out)
        val c3s = "%.4f".format(java.util.Locale.US, c3)
        assertTrue(err!!.message!!.contains("min cosine $c3s < budget 0.99") && !err.message!!.contains("raw vector dimensions"), err.message)
        assertTrue(out.contains("min $c3s (site n3 'B'"), out)
    }

    @Test
    fun `F1 a NaN cosine at one site REFUSES on the undefined branch alone, and a tree with no split site REFUSES`() {
        val cache = makeCache("two_site_nan.db", native)
        val (sites, byId) = twoSiteTree(native, muN3 = FloatArray(slice))
        val (o1, e1, _) = guardSites(cache, sites, byId)
        assertTrue(e1 is EmbedderReadGuard.Refusal, o1)
        assertTrue(e1!!.message!!.endsWith("REFUSING before any replicate: the cosine is undefined on 1 site(s)"), e1.message)
        val (o2, e2, _) = guardSites(cache, emptyList(), byId)
        assertTrue(e2 is EmbedderReadGuard.Refusal && e2.message!!.contains("no site to check"), o2)
        assertTrue(o2.contains("vmfMu cosine over 0 sites"), o2)
    }

    @Test
    fun `F1 a variant tag of the manifest's model is a contradiction`() {
        val e = assertThrows<EmbedderReadGuard.Refusal> {
            EmbedderReadGuard.resolveModel(mapOf("embedding_model" to "qwen3-embedding:latest"), "qwen3-embedding:8b", false)
        }
        assertTrue(e.message!!.contains("contradicts"), e.message)
    }

    // ── (a) -DembeddingCacheFile ──────────────────────────────────────────────────
    @Test
    fun `P-2 (iii) absent resolves to the historical file unvalidated, a present value is validated fail-closed`() {
        val d = EmbedderReadGuard.resolveCacheFile(null)
        assertEquals(File("embeddings_cache.db"), d.file)
        assertFalse(d.explicit)
        assertThrows<EmbedderReadGuard.Refusal> { EmbedderReadGuard.resolveCacheFile("") }
        assertThrows<EmbedderReadGuard.Refusal> { EmbedderReadGuard.resolveCacheFile("  ") }
        assertThrows<EmbedderReadGuard.Refusal> { EmbedderReadGuard.resolveCacheFile(File(tmp, "absent.db").path) }
        assertThrows<EmbedderReadGuard.Refusal> { EmbedderReadGuard.resolveCacheFile(tmp.path) }                  // a directory
        val txt = File(tmp, "not_sqlite.db").apply { writeText("hello, not a database") }
        val e = assertThrows<EmbedderReadGuard.Refusal> { EmbedderReadGuard.resolveCacheFile(txt.path) }
        assertTrue(e.message!!.contains("not a SQLite database"))
        val noEmb = makeCache("noemb.db", emptyMap(), withQueries = true, withEmbeddings = false)
        assertTrue(assertThrows<EmbedderReadGuard.Refusal> { EmbedderReadGuard.resolveCacheFile(noEmb.path) }.message!!.contains("[embeddings]"))
        val noQ = makeCache("noq.db", emptyMap(), withQueries = false, withEmbeddings = true)
        assertTrue(assertThrows<EmbedderReadGuard.Refusal> { EmbedderReadGuard.resolveCacheFile(noQ.path) }.message!!.contains("[queries]"))
        val ok = makeCache("ok.db", native)
        val r = EmbedderReadGuard.resolveCacheFile(ok.path)
        assertTrue(r.explicit)
        assertEquals(ok.path, r.file.path)
    }

    // ── (d) the model must be named ──────────────────────────────────────────────
    @Test
    fun `P-2 (v) a manifest without embedding_model and no -D refuses, and the other naming branches`() {
        val R = EmbedderReadGuard
        assertThrows<EmbedderReadGuard.Refusal> { R.resolveModel(mapOf("seed" to 42), null, cacheFileExplicit = false) }
        assertThrows<EmbedderReadGuard.Refusal> { R.resolveModel(mapOf("embedding_model" to ""), null, cacheFileExplicit = false) }
        assertThrows<EmbedderReadGuard.Refusal> { R.resolveModel(null, null, cacheFileExplicit = true) }
        assertThrows<EmbedderReadGuard.Refusal> { R.resolveModel(null, "", cacheFileExplicit = false) }
        assertThrows<EmbedderReadGuard.Refusal> { R.resolveModel(mapOf("embedding_model" to "qwen3-embedding:latest"), "nomic-embed-text:latest", false) }
        assertEquals("nomic-embed-text:latest", R.resolveModel(mapOf("seed" to 42), "nomic-embed-text:latest", true).model)
        assertEquals("qwen3-embedding:latest", R.resolveModel(mapOf("embedding_model" to "qwen3-embedding:latest"), null, true).model)
        assertEquals("qwen3-embedding", R.resolveModel(mapOf("embedding_model" to "qwen3-embedding:latest"), "qwen3-embedding", false).model)
        val dflt = R.resolveModel(null, null, cacheFileExplicit = false)                     // ambiguity A1: the unconfigured site null
        assertEquals("qwen3-embedding:latest", dflt.model)
        assertTrue(dflt.source.startsWith("default"))
    }

    // ── the six unguarded harness arms refuse a set flag ─────────────────────────
    @Test
    fun `an arm without the vmfMu guard refuses -DembeddingCacheFile and -DembeddingModel`() {
        val m = SeparationNullBySizeTest::class.java.getDeclaredMethod("unguardedEmbDb", String::class.java).apply { isAccessible = true }
        val harness = SeparationNullBySizeTest()
        assertEquals(File("embeddings_cache.db"), m.invoke(harness, "withinNull"))
        for (p in listOf(EmbedderReadGuard.PROP_CACHE_FILE, EmbedderReadGuard.PROP_MODEL)) {
            val saved = System.getProperty(p)
            try {
                System.setProperty(p, "x")
                val e = assertThrows<java.lang.reflect.InvocationTargetException> { m.invoke(harness, "withinNull") }
                assertTrue(e.cause is IllegalStateException && e.cause!!.message!!.contains("admitted only by the siteNull arm"))
            } finally {
                if (saved == null) System.clearProperty(p) else System.setProperty(p, saved)
            }
        }
    }

    @Test
    fun `the native dimension table is the declared one`() {
        assertEquals(mapOf("qwen3-embedding:latest" to 4096, "nomic-embed-text:latest" to 768,
            "embeddinggemma:latest" to 768, "mxbai-embed-large:latest" to 1024), EmbedderReadGuard.NATIVE_DIM)
        assertEquals("nomic-embed-text:latest", EmbedderReadGuard.canonicalModel("nomic-embed-text"))
        assertEquals("qwen3-embedding:8b", EmbedderReadGuard.canonicalModel("qwen3-embedding:8b"))
    }
}
