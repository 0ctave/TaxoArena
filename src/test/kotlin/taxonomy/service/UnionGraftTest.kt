package taxonomy.service

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import taxonomy.dataset.ReservedPool
import taxonomy.model.GraphNode
import java.security.MessageDigest

/**
 * Stage 1b federated assembly (docs/multi_corpus_design.md, "design adjustment"): the three
 * invariants the graft must hold — node ids stay unique across snapshots that were built in
 * separate processes (and so share the counter ids n00000001…), every depth shifts by exactly
 * one level, and the union's reserved-pool id is the content hash of the merged pools.
 */
class UnionGraftTest {

    /** A serialized three-node tree with the counter ids every per-corpus build starts from. */
    private fun serialized(rootLabel: String, anchorA: String, anchorB: String): SerializedGraph {
        val root = SerialNode(
            id = "n00000001", label = rootLabel, depth = 0,
            childIds = listOf("n00000002", "n00000003"), parentIds = emptyList(),
            queryIds = listOf("q_aaaa"), queryWeights = mapOf("q_aaaa" to 0.5)
        )
        val a = SerialNode(
            id = "n00000002", label = anchorA, depth = 1, childIds = listOf("n00000004"),
            parentIds = listOf("n00000001"), treeParentId = null, residualQueries = listOf("1000007")
        )
        val a1 = SerialNode(
            id = "n00000004", label = "$anchorA/leaf", depth = 2, childIds = emptyList(),
            parentIds = listOf("n00000002"), treeParentId = "n00000002",
            crossLinkChildIds = listOf("n00000003")
        )
        val b = SerialNode(
            id = "n00000003", label = anchorB, depth = 1, childIds = emptyList(),
            parentIds = listOf("n00000001", "n00000004"), treeParentId = null
        )
        return SerializedGraph(rootId = "n00000001", nodes = listOf(root, a, a1, b), version = 2)
    }

    @Test
    fun `rekey prefixes every id reference and shifts every depth by one`() {
        val g = serialized("BBH", "BBH/boolean_expressions", "BBH/navigate")
        val r = UnionGraft.rekey(g, "BBH")

        assertEquals("BBH:n00000001", r.rootId)
        val byId = r.nodes.associateBy { it.id }
        assertEquals(setOf("BBH:n00000001", "BBH:n00000002", "BBH:n00000003", "BBH:n00000004"), byId.keys)
        assertEquals(listOf("BBH:n00000002", "BBH:n00000003"), byId.getValue("BBH:n00000001").childIds)
        assertEquals(listOf("BBH:n00000001", "BBH:n00000004"), byId.getValue("BBH:n00000003").parentIds)
        assertEquals("BBH:n00000002", byId.getValue("BBH:n00000004").treeParentId)
        assertEquals(listOf("BBH:n00000003"), byId.getValue("BBH:n00000004").crossLinkChildIds)
        // depth + 1 everywhere, in lockstep with the original
        for (n in g.nodes) assertEquals(n.depth + 1, byId.getValue("BBH:" + n.id).depth, "depth of ${n.id}")
        // content keys are not ids: untouched
        assertEquals(listOf("q_aaaa"), byId.getValue("BBH:n00000001").queryIds)
        assertEquals(mapOf("q_aaaa" to 0.5), byId.getValue("BBH:n00000001").queryWeights)
        assertEquals(listOf("1000007"), byId.getValue("BBH:n00000002").residualQueries)
        // labels and everything else carried through
        assertEquals("BBH", byId.getValue("BBH:n00000001").label)
    }

    @Test
    fun `rekey makes two snapshots with identical counter ids disjoint`() {
        val bbh = UnionGraft.rekey(serialized("BBH", "BBH/a", "BBH/b"), "BBH")
        val math = UnionGraft.rekey(serialized("MATH", "MATH/Algebra", "MATH/Geometry"), "MATH")
        val ids = (bbh.nodes + math.nodes).map { it.id }
        assertEquals(ids.size, ids.toSet().size, "ids must be unique across the two re-keyed graphs")
        assertNotEquals(bbh.rootId, math.rootId)
        assertThrows(IllegalArgumentException::class.java) { UnionGraft.rekey(bbh, "X:Y") }
        assertThrows(IllegalArgumentException::class.java) { UnionGraft.rekey(bbh, " ") }
    }

    private fun tree(prefix: String, rootDepth: Int): GraphNode {
        val root = GraphNode(id = "$prefix:n00000001", label = prefix, depth = rootDepth)
        val a = GraphNode(id = "$prefix:n00000002", label = "$prefix/a", depth = rootDepth + 1)
        val leaf = GraphNode(id = "$prefix:n00000003", label = "$prefix/a/leaf", depth = rootDepth + 2)
        root.children.add(a); a.parents.add(root); a.treeParentId = root.id
        a.children.add(leaf); leaf.parents.add(a); leaf.treeParentId = a.id
        return root
    }

    @Test
    fun `graft attaches per-corpus roots at depth 1 under a depth-0 union root`() {
        val bbh = tree("BBH", 1)
        val math = tree("MATH", 1)
        val union = UnionGraft.graft("BBH+MATH", listOf(bbh, math))

        assertEquals(UnionGraft.UNION_ROOT_ID, union.id)
        assertEquals(0, union.depth)
        assertEquals("BBH+MATH", union.label)
        assertEquals(setOf(bbh, math), union.children)
        for (r in listOf(bbh, math)) {
            assertEquals(setOf(union), r.parents)
            assertEquals(union.id, r.treeParentId)
            assertEquals(1, r.depth)
        }
        val all = UnionGraft.nodes(union)
        assertEquals(7, all.size)
        assertEquals(all.size, all.map { it.id }.toSet().size)
        // every tree edge descends exactly one level
        for (n in all) for (c in n.children) assertEquals(n.depth + 1, c.depth, "${c.id} under ${n.id}")
    }

    @Test
    fun `graft refuses roots at the wrong depth, roots with parents, and duplicate ids`() {
        assertThrows(IllegalArgumentException::class.java) { UnionGraft.graft("X", listOf(tree("BBH", 0))) }
        val attached = tree("BBH", 1).also { it.parents.add(GraphNode(id = "other", label = "other", depth = 0)) }
        assertThrows(IllegalArgumentException::class.java) { UnionGraft.graft("X", listOf(attached)) }
        // two distinct node objects sharing an id (what an un-prefixed graft would produce)
        val a = tree("SAME", 1)
        val b = tree("SAME", 1)
        assertThrows(IllegalStateException::class.java) { UnionGraft.graft("X", listOf(a, b)) }
        // a depth gap inside a member is caught by verify
        val gapped = tree("GPQA", 1)
        gapped.children.first().children.first().depth = 5
        assertThrows(IllegalStateException::class.java) { UnionGraft.graft("X", listOf(gapped)) }
    }

    private fun sha16(lines: List<String>): String {
        val digest = MessageDigest.getInstance("SHA-256").digest(lines.sorted().joinToString("\n").toByteArray())
        return "p" + digest.take(8).joinToString("") { "%02x".format(it) }
    }

    @Test
    fun `union pool is the concatenation and its id is the content hash of the merged map`() {
        val bbh = mapOf("BBH/boolean_expressions" to listOf(1000180, 1000046), "BBH/navigate" to listOf(1000901))
        val math = mapOf("MATH/Algebra" to listOf(2000012, 2000007, -5))   // -5 = routing-only sentinel
        val union = UnionGraft.unionReservedPools(linkedMapOf("BBH" to bbh, "MATH" to math))

        assertEquals(bbh.keys + math.keys, union.keys)
        assertEquals(listOf(2000012, 2000007, -5), union["MATH/Algebra"], "ids are kept verbatim, sentinels included")

        val id = UnionGraft.poolId(union)
        // 1. the standard content id of the merged, sentinel-filtered map
        val expectedMap = mapOf(
            "BBH/boolean_expressions" to listOf(1000180, 1000046), "BBH/navigate" to listOf(1000901),
            "MATH/Algebra" to listOf(2000012, 2000007)
        )
        assertEquals(ReservedPool.computePoolId(expectedMap), id)
        // 2. spelled out: sha256 over the sorted canonical `source|domain:id` lines of BOTH pools
        val lines = listOf(
            "BBH|boolean_expressions:1000180", "BBH|boolean_expressions:1000046", "BBH|navigate:1000901",
            "MATH|Algebra:2000012", "MATH|Algebra:2000007"
        )
        assertEquals(sha16(lines), id)
        // 3. member order does not matter
        val reversed = UnionGraft.unionReservedPools(linkedMapOf("MATH" to math, "BBH" to bbh))
        assertEquals(id, UnionGraft.poolId(reversed))
        // 4. and the union id differs from every member's own id
        assertNotEquals(UnionGraft.poolId(bbh), id)
        assertNotEquals(UnionGraft.poolId(math), id)
    }

    @Test
    fun `union pool refuses foreign keys, duplicate keys and empty members`() {
        val bbh = mapOf("BBH/navigate" to listOf(1000901))
        assertThrows(IllegalArgumentException::class.java) {
            UnionGraft.unionReservedPools(mapOf("MATH" to bbh))                       // key belongs to BBH
        }
        assertThrows(IllegalArgumentException::class.java) {
            UnionGraft.unionReservedPools(mapOf("BBH" to mapOf("Philosophy" to listOf(1))))   // bare MMLU_PRO key
        }
        assertThrows(IllegalArgumentException::class.java) {
            UnionGraft.unionReservedPools(mapOf("BBH" to emptyMap()))
        }
        assertTrue(UnionGraft.unionReservedPools(mapOf("BBH" to bbh)).containsKey("BBH/navigate"))
    }
}
