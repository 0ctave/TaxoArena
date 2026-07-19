# Codebase Audit Report: Potential Bugs

This report identifies potential bugs (such as race conditions, unhandled exceptions, incorrect edge cases, resource leaks, or SQLite concurrency issues) in the TaxoArena codebase.

---

### 1. Incorrect SQLite Schema Migration Order (High Priority)
* **File & Lines:** [TaxonomyRankingService.kt](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/service/TaxonomyRankingService.kt#L154-L245)
* **Problem Explanation:** 
  In the database initialization function `ensureDatabaseInitialized()`, the migration statement:
  ```kotlin
  s.execute("UPDATE match_history SET snapshot_id = 'global' WHERE snapshot_id IS NULL")
  ```
  is executed *before* the loop that alters the table to add missing columns (such as `snapshot_id`):
  ```kotlin
  for (col in listOf("snapshot_id", "model_a", "model_b")) {
      stmt.execute("ALTER TABLE match_history ADD COLUMN $col TEXT")
  }
  ```
  If an older `match_history` table exists that lacks the `snapshot_id` column, the `UPDATE` query will immediately throw an exception. While this exception is caught and ignored, the table is subsequently altered to add the column, leaving all pre-existing records with `NULL` in the `snapshot_id` field. Since subsequent queries assume `snapshot_id` is always populated (e.g., defaulting to `'global'`), this leads to inconsistent data query results.
* **Proposed Fix:** 
  Move the `UPDATE` migration query to execute *after* the `ALTER TABLE` loop completes:
  ```kotlin
  // First alter the table structure
  for (col in listOf("snapshot_id", "model_a", "model_b")) {
      try {
          conn.createStatement().use { stmt ->
              stmt.execute("ALTER TABLE match_history ADD COLUMN $col TEXT")
          }
      } catch (_: Exception) {}
  }
  
  // Then migrate the snapshot_id values
  try {
      conn.createStatement().use { s ->
          s.execute("UPDATE match_history SET snapshot_id = 'global' WHERE snapshot_id IS NULL")
      }
  } catch (_: Exception) {}
  ```

---

### 2. Thread Safety Violation: Unsynchronized Iteration on Synchronized List (Medium Priority)
* **File & Lines:** [GraphNode.kt](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/model/GraphNode.kt#L185-L206)
* **Problem Explanation:** 
  In `assignQueryIds(root: GraphNode)`, the code iterates over `node.queries` using `node.queries.forEach { ... }` in two walks:
  ```kotlin
  node.queries.forEach { q ->
      if (seenTexts.add(q.rawText)) { ... }
  }
  ```
  and:
  ```kotlin
  node.queries.forEach { q ->
      q.queryId = textToId[q.rawText] ?: -1
  }
  ```
  Although `node.queries` is initialized as a synchronized list (`Collections.synchronizedList(ArrayList())`), iterating over a synchronized list in Kotlin/Java is *not* thread-safe without explicit synchronization on the list instance. If another thread modifies `node.queries` concurrently (such as during parallel trickling or matching operations), this will trigger a `ConcurrentModificationException` or cause dirty reads.
* **Proposed Fix:** 
  Wrap all loop/iteration statements on `node.queries` in `synchronized(node.queries) { ... }` blocks (consistent with the other functions in the same file):
  ```kotlin
  synchronized(node.queries) {
      node.queries.forEach { q ->
          if (seenTexts.add(q.rawText)) {
              uniqueQueries.add(q)
          }
      }
  }
  ```
