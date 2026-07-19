# Codebase Audit Report: Improvements

This report identifies codebase improvements (such as logging quality, configuration robustness, or readable Kotlin idioms) in the TaxoArena codebase.

---

### 1. Tomcat Thread Blocking via runBlocking in Spring REST Controllers (High Priority)
* **File & Lines:** 
  * [ModelEvalController.kt](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/controller/ModelEvalController.kt#L33)
  * [TaxonomyArenaController.kt](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/controller/TaxonomyArenaController.kt#L33)
  * [TaxonomyController.kt](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/controller/TaxonomyController.kt#L17)
  * [TaxonomyJudgeController.kt](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/controller/TaxonomyJudgeController.kt#L23)
* **Problem Explanation:** 
  In the Spring REST controllers, endpoints are defined as standard synchronous methods that invoke asynchronous coroutine tasks via `runBlocking`:
  ```kotlin
  @PostMapping("/load")
  fun loadModel(@RequestBody req: LoadRequest): LoadResponse = runBlocking {
      ...
  }
  ```
  Calling `runBlocking` in a Tomcat request handler thread blocks the thread until the coroutine completes. This completely defeats the purpose of non-blocking concurrency, saturates the Tomcat thread pool under load, and degrades overall server throughput.
* **Proposed Fix:** 
  Refactor the controller endpoints to return `DeferredResult` or `CompletableFuture` (or if using Spring Boot 3+ with Kotlin coroutines support, declare the endpoints as `suspend` functions directly):
  ```kotlin
  @PostMapping("/load")
  suspend fun loadModel(@RequestBody req: LoadRequest): LoadResponse {
      ...
  }
  ```

---

### 2. Inefficient Sorting Keys Computation in Node Selection (Medium Priority)
* **File & Lines:** [BtMatchScheduler.kt](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/service/BtMatchScheduler.kt#L305)
* **Problem Explanation:** 
  In `selectTargetNodes()`, the nodes are sorted:
  ```kotlin
  return allNodes
      .filter { ... }
      .sortedWith(
          compareByDescending<GraphNode> { node -> (btStates[node.id]?.totalComparisons ?: 0) == 0 }
          .thenByDescending { node -> btStates[node.id]?.stdErrors?.values?.average() ?: 10.0 }
          ...
      )
  ```
  The expression `btStates[node.id]?.stdErrors?.values?.average() ?: 10.0` is computed on *every comparison* of the sorting algorithm (taking $O(N \log N)$ operations). Extrapolating the average of a list inside a comparator involves map lookups and collection iteration, which leads to redundant CPU cycles and iterator allocations.
* **Proposed Fix:** 
  Precompute the sort keys (average standard errors) once per node before sorting, or associate them:
  ```kotlin
  val nodeAvgSe = allNodes.associate { node ->
      node.id to (btStates[node.id]?.stdErrors?.values?.average() ?: 10.0)
  }
  return allNodes
      .filter { ... }
      .sortedWith(
          compareByDescending<GraphNode> { node -> (btStates[node.id]?.totalComparisons ?: 0) == 0 }
          .thenByDescending { node -> nodeAvgSe[node.id] ?: 10.0 }
          ...
      )
  ```

---

### 3. Use Kotlin Idiomatic Properties instead of Direct Set Checks (Low Priority)
* **File & Lines:** [BtMatchScheduler.kt](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/service/BtMatchScheduler.kt#L297)
* **Problem Explanation:** 
  The filter check in `selectTargetNodes` contains:
  ```kotlin
  node.children.isEmpty()
  ```
  Since `GraphNode` already declares a specific, readable custom getter property `isLeaf: Boolean` which delegates exactly to `children.isEmpty()`, using `isLeaf` is more idiomatic Kotlin and improves readability.
* **Proposed Fix:** 
  ```kotlin
  return allNodes
      .filter { node ->
          node.isLeaf
          && ...
      }
  ```
