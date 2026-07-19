# Codebase Audit Report: Optimizations

This report identifies performance optimizations (such as redundant calculation caching, SQL queries batching, coroutines usage, or memory/allocation reduction) in the TaxoArena codebase.

---

### 1. Severe N+1 SQL Query Storm in Hydration Loop (High Priority)
* **File & Lines:** [TaxonomyPersistence.kt](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/service/TaxonomyPersistence.kt#L155-L162)
* **Problem Explanation:** 
  In the `load(path: String)` method, the code loops over every node to map it back from `SerialNode` to `GraphNode`:
  ```kotlin
  val nodeMap = serialized.nodes.associate { sNode ->
      GraphNode(...).apply {
          ...
          val allQueryIds = serialized.nodes.flatMap { it.queryIds }.toSet()
          val queryRowMap: Map<String, Pair<String, String>> = embeddingCache.getQueriesBatch(allQueryIds)

          sNode.queryIds.forEach { qId ->
              val (raw, distilled) = queryRowMap[qId] ?: return@forEach
              val vector = embeddingCache.get(distilled) ?: return@forEach
              queries.add(Embedding(raw, distilled, vector))
          }
      }
  }
  ```
  This creates two major bottlenecks:
  1. For *every single node* in the graph, it flatmaps all nodes, extracts all query IDs, and executes a SQLite database batch query `getQueriesBatch` to fetch the metadata. If there are $N$ nodes, it queries the database for *all queries* $N$ times!
  2. For every query ID inside a node, it calls `embeddingCache.get(distilled)` individually, which executes a separate SQL `SELECT` statement to fetch the query vector. If a node has $M$ queries, this results in $M$ sequential SQL roundtrips per node.
* **Proposed Fix:** 
  Lift the extraction of `allQueryIds` and the execution of `getQueriesBatch` completely outside the `associate` loop. In addition, batch-fetch embedding vectors from the database rather than querying them one-by-one:
  ```kotlin
  val allQueryIds = serialized.nodes.flatMap { it.queryIds }.toSet()
  val queryRowMap = embeddingCache.getQueriesBatch(allQueryIds)
  
  // Extract all distilled query texts to batch-fetch vectors
  val allDistilledTexts = queryRowMap.values.map { it.second }.toSet()
  val vectorMap = embeddingCache.getEmbeddingsBatch(allDistilledTexts) // Implement a batch get in EmbeddingCache

  val nodeMap = serialized.nodes.associate { sNode ->
      sNode.id to GraphNode(
          id = sNode.id,
          label = sNode.label,
          depth = sNode.depth
      ).apply {
          ...
          sNode.queryIds.forEach { qId ->
              val (raw, distilled) = queryRowMap[qId] ?: return@forEach
              val vector = vectorMap[distilled] ?: return@forEach
              queries.add(Embedding(raw, distilled, vector))
          }
      }
  }
  ```

---

### 2. Excessive Array Allocations in EM (Expectation-Maximization) Loop (Medium Priority)
* **File & Lines:** [StatisticsUtils.kt](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/utils/StatisticsUtils.kt#L381-L391)
* **Problem Explanation:** 
  In the internal EM algorithm `runVmfEm`, there is a tight loop over the dataset ($N$ points) inside the EM iterations (up to 200 iterations):
  ```kotlin
  for (i in 0 until n) {
      val x = embeddings[i]
      val logPs = DoubleArray(k) { c -> ... }
      ...
      val exps  = DoubleArray(k) { exp(logPs[it] - maxLP) }
      ...
  }
  ```
  For $N = 1000$ points and 100 iterations, this allocates $200,000$ `DoubleArray` instances of size `k`. These temporary allocations create significant garbage collection (GC) pressure and decrease CPU cache locality.
* **Proposed Fix:** 
  Preallocate reusable scratch arrays (such as a single `logPs` and `exps` buffer array per run) and populate them in-place:
  ```kotlin
  val logPs = DoubleArray(k)
  val exps = DoubleArray(k)
  for (i in 0 until n) {
      val x = embeddings[i]
      for (c in 0 until k) {
          var dot = 0.0
          for (j in 0 until d) dot += mus[c][j] * x[j]
          logPs[c] = ln(pis[c].coerceAtLeast(1e-10)) + logNorms[c] + kappas[c] * dot
      }
      val maxLP = logPs.maxOrNull() ?: 0.0
      var sumExp = 0.0
      for (c in 0 until k) {
          exps[c] = exp(logPs[c] - maxLP)
          sumExp += exps[c]
      }
      for (c in 0 until k) {
          R[i][c] = exps[c] / sumExp
      }
      totalLikelihood += maxLP + ln(sumExp)
  }
  ```

---

### 3. Redundant List Flattening in Dasgupta Cost Calculation (Medium Priority)
* **File & Lines:** [StatisticsUtils.kt](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/utils/StatisticsUtils.kt#L210-L220)
* **Problem Explanation:** 
  The function `calculateDasguptaDeltaK(clusters: List<List<DoubleArray>>)` starts by flattening the clusters:
  ```kotlin
  val allPts = clusters.flatten()
  ```
  This creates a completely new, flat list of all double arrays. Since this function is called inside the splitter and k-means loops frequently, it leads to massive redundant memory allocations.
* **Proposed Fix:** 
  Avoid flattening the list. Compute `n` as the sum of cluster sizes and sum vectors directly:
  ```kotlin
  val n = clusters.sumOf { it.size }.toDouble()
  if (n < 2.0 || clusters.isEmpty()) return 0.0
  val d = clusters.firstOrNull { it.isNotEmpty() }?.firstOrNull()?.size ?: return 0.0

  val sumTotal = DoubleArray(d)
  for (cluster in clusters) {
      for (v in cluster) {
          for (i in 0 until d) {
              sumTotal[i] += v[i]
          }
      }
  }
  ```

---

### 4. Thread Contention from Shared Random Generator in PCA (Medium Priority)
* **File & Lines:** [StatisticsUtils.kt](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/utils/StatisticsUtils.kt#L517)
* **Problem Explanation:** 
  In the power iteration of `pcaProject()`, the code initializes random starting vectors using:
  ```kotlin
  var vec = DoubleArray(d) { Math.random() - 0.5 }
  ```
  `Math.random()` delegates to a single, globally shared and synchronized `java.util.Random` instance. When the splitter runs `splitNodesRecursive` using parallel coroutines (`async { splitSingleNode(node) }.awaitAll()`), threads will contentiously block each other waiting for the shared Random instance lock.
* **Proposed Fix:** 
  Use Kotlin's standard non-blocking `Random.nextDouble()` or a thread-local random instance:
  ```kotlin
  var vec = DoubleArray(d) { kotlin.random.Random.nextDouble() - 0.5 }
  ```

---

### 5. Repeated SQL Connection Opening Overhead (Medium Priority)
* **File & Lines:** 
  * [MMLUDatasetFetcher.kt](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/dataset/MMLUDatasetFetcher.kt#L45-L48)
  * [ModelEvalStore.kt](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/dataset/ModelEvalStore.kt#L54)
* **Problem Explanation:** 
  In `MMLUDatasetFetcher` and `ModelEvalStore`, connection helper properties open a brand new SQLite connection on every single invocation:
  ```kotlin
  private val connection: java.sql.Connection
      get() = DriverManager.getConnection(dbUrl).also { conn ->
          conn.autoCommit = true
      }
  ```
  This creates significant file handle and socket overhead, especially during sequential operations.
* **Proposed Fix:** 
  Implement a single held-open connection guarded by a lock (like in `EmbeddingCache` or `TaxonomyRankingService`), or use a light connection pool (e.g., HikariCP).
