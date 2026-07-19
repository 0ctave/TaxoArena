# Codebase Audit Report: Factorisation

This report identifies duplicated code segments, redundant helper functions, and DRY cleanups in the TaxoArena codebase.

---

### 1. Duplicated SQLite Connection Query Parameters (Medium Priority)
* **File & Lines:** 
  * [EmbeddingCache.kt](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/dataset/EmbeddingCache.kt#L27)
  * [MMLUDatasetFetcher.kt](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/dataset/MMLUDatasetFetcher.kt#L43)
  * [ModelEvalStore.kt](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/dataset/ModelEvalStore.kt#L52)
  * [ModelEvalLoader.kt](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/dataset/ModelEvalLoader.kt#L45)
  * [TaxonomyRankingService.kt](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/service/TaxonomyRankingService.kt#L62)
  * [TaxonomySnapshotManager.kt](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/service/TaxonomySnapshotManager.kt#L237)
* **Problem Explanation:** 
  The SQLite connection URL configuration suffix `?journal_mode=WAL&synchronous=NORMAL&busy_timeout=10000` is hardcoded and repeated verbatim in almost every file that creates a connection. This violates DRY (Don't Repeat Yourself) principles and makes it hard to globally adjust SQLite settings (such as busy timeouts or synchronous mode).
* **Proposed Fix:** 
  Centralize connection URL parameters in a single utility or configuration bean:
  ```kotlin
  object SqliteConfig {
      const val CONNECTION_PARAMS = "journal_mode=WAL&synchronous=NORMAL&busy_timeout=10000"
      fun getUrl(dbPath: String) = "jdbc:sqlite:$dbPath?$CONNECTION_PARAMS"
  }
  ```

---

### 2. Duplicated Kotlin Json Configurations (Medium Priority)
* **File & Lines:** 
  * Duplicated across 15+ files (e.g. `EmbeddingCache.kt`, `MMLUDatasetFetcher.kt`, `ModelEvalStore.kt`, `TaxonomyValidator.kt`, etc.)
* **Problem Explanation:** 
  Almost every service, loader, or client class constructs its own localized `Json` serializer instance:
  ```kotlin
  private val json = Json { ignoreUnknownKeys = true; isLenient = true; coerceInputValues = true }
  ```
  This duplicates serializer initialization and memory footprint, and makes it hard to enforce a unified JSON parsing behavior across the application.
* **Proposed Fix:** 
  Define a single configured `Json` instance as a Spring `@Bean` in a configuration class and inject it where needed:
  ```kotlin
  @Configuration
  class JacksonSerializationConfig {
      @Bean
      fun kotlinJson(): Json = Json {
          ignoreUnknownKeys = true
          isLenient = true
          coerceInputValues = true
      }
  }
  ```

---

### 3. Redundant SQL PRAGMA Statements Execution (Low Priority)
* **File & Lines:** [TaxonomyRankingService.kt](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/service/TaxonomyRankingService.kt#L78-L80)
* **Problem Explanation:** 
  In `TaxonomyRankingService`, the database URL already contains the synchronous/WAL query parameters:
  ```kotlin
  private val dbUrl = "...?journal_mode=WAL&synchronous=NORMAL&busy_timeout=10000&transaction_mode=IMMEDIATE"
  ```
  However, the connection initializer *also* executes explicit PRAGMA queries:
  ```kotlin
  stmt.execute("PRAGMA journal_mode=WAL;")
  stmt.execute("PRAGMA synchronous=NORMAL;")
  stmt.execute("PRAGMA busy_timeout=10000;")
  ```
  These explicit PRAGMA executions are completely redundant as the JDBC URL parameters have already configured these connection parameters.
* **Proposed Fix:** 
  Remove the redundant PRAGMA executions in the initializer.
