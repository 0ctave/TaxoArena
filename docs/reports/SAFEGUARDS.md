# Codebase Audit Report: Safeguards

This report identifies missing or weak safeguards (such as timeout controls, boundary checks, null-safety enforcement, validation, input sanitisation, or transaction safety) in the TaxoArena codebase.

---

### 1. Lack of HTTP Connect and Request Timeout Controls (High Priority)
* **File & Lines:** 
  * [ArcTaxonomyLLMClient.kt](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/operations/ArcTaxonomyLLMClient.kt#L142)
  * [MMLUDatasetFetcher.kt](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/dataset/MMLUDatasetFetcher.kt#L190)
  * [TuiGatewayImpl.kt](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/tui/service/TuiGatewayImpl.kt#L554)
* **Problem Explanation:** 
  In several HTTP service components, requests are dispatched using the Java 11 `HttpClient` and `HttpRequest` APIs without setting connection or request timeouts. By default, `HttpClient.newHttpClient()` and `HttpRequest.newBuilder()` do not apply timeouts. If any upstream APIs (such as HuggingFace datasets-server, GitHub repository API, or the local Ollama LLM endpoint) hang, block, or experience network drops, the application threads will block indefinitely, leading to resource exhaustion (e.g., Tomcat thread pool saturation or coroutine thread starvation).
* **Proposed Fix:** 
  Configure connect timeouts on the `HttpClient` builder and request-specific timeouts on the `HttpRequest` builder:
  ```kotlin
  // Instantiate client with connect timeout
  val client = HttpClient.newBuilder()
      .connectTimeout(java.time.Duration.ofSeconds(10))
      .build()

  // Build request with explicit read timeout
  val request = HttpRequest.newBuilder()
      .uri(URI.create(url))
      .timeout(java.time.Duration.ofSeconds(15))
      .GET()
      .build()
  ```

---

### 2. Database Connection Leak Safeguard during PRAGMA Initialization (Low Priority)
* **File & Lines:** [TaxonomyRankingService.kt](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/service/TaxonomyRankingService.kt#L73-L86)
* **Problem Explanation:** 
  In the lazy initialization of `connection`, PRAGMAs are executed on a newly opened connection:
  ```kotlin
  private val connection: Connection by lazy {
      DriverManager.getConnection(dbUrl).also { conn ->
          conn.autoCommit = true
          try {
              conn.createStatement().use { stmt ->
                  stmt.execute("PRAGMA journal_mode=WAL;")
                  ...
              }
          } catch (e: Exception) {
              log.warn("Failed to set SQLite PRAGMAs: ${e.message}")
          }
      }
  }
  ```
  If an exception is thrown inside the `try` block (e.g., due to a corrupted SQLite driver or database file lock), the exception is logged but the connection `conn` is still returned as the initialized connection. This could leave the application with a half-initialized or broken connection, and the driver might not clean it up properly.
* **Proposed Fix:** 
  If an exception occurs during the initialization steps, close the connection before letting the exception bubble up, or ensure the connection is discarded:
  ```kotlin
  private val connection: Connection by lazy {
      val conn = DriverManager.getConnection(dbUrl)
      try {
          conn.autoCommit = true
          conn.createStatement().use { stmt ->
              stmt.execute("PRAGMA journal_mode=WAL;")
              stmt.execute("PRAGMA synchronous=NORMAL;")
              stmt.execute("PRAGMA busy_timeout=10000;")
          }
          conn
      } catch (e: Exception) {
          try { conn.close() } catch (_: Exception) {}
          log.error("Failed to initialize SQLite database connection properly", e)
          throw e
      }
  }
  ```
