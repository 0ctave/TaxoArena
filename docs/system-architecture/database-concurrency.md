# Database Concurrency, Schema, & SQLite WAL Operations

This document details the database storage architecture of **TaxoArena**, focusing on SQLite concurrent operations, Write-Ahead Logging (WAL) configuration, and the connection synchronization patterns that prevent write collisions.

---

## 1. Storage Layout & SQLite WAL Configuration

TaxoArena uses SQLite for local storage, maintaining separate files to isolate concerns:
*   `embeddings_cache.db`: Caches high-dimensional query embeddings to avoid redundant API cost.
*   `ratings.db`: Stores match history, pairwise model statistics, and Bradley-Terry states.
*   `snapshots.db`: Persists historical DAG topological snapshots.

### The Concurrent Writer Problem
SQLite uses database-level locking. If multiple threads attempt to write to the database concurrently, SQLite rejects concurrent access and throws `SQLITE_BUSY` ("database is locked") errors.

### Write-Ahead Logging (WAL) Mode
To maximize reading throughput during active benchmarking, TaxoArena enables **Write-Ahead Logging (WAL)**:

```sql
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
```

#### Impact
*   **Reader-Writer Separation**: In WAL mode, writes are written to a separate WAL log file rather than directly modifying the main database file. This allows reading threads to query the database concurrently without blocking or being blocked by active write transactions.
*   **Performance**: Commit operations are significantly faster as they write sequentially to the log file.

---

## 2. Connection Synchronization & Locking Patterns

Even with WAL mode enabled, SQLite allows only one writing transaction at a time. Concurrent write-write attempts will still collide. TaxoArena enforces strict transactional safety using two programming patterns:

### Pattern 1: Single-Threaded Write Dispatcher
All database write transactions are executed on a dedicated, single-threaded coroutine dispatcher context:

```kotlin
private val dbWriteDispatcher = newSingleThreadContext("DB-Write")

// Usage in TaxonomyBenchmarkService:
withContext(dbWriteDispatcher) {
    rankingService.saveBtState(state, snapshotId)
}
```

By routing all database write functions through a single-threaded queue, we guarantee that no two threads attempt to write to the database file at the same time, eliminating write-write collisions.

### Pattern 2: Connection Timeouts & Busy Retries
If the database file is accessed by external visualization tools or parallel background tasks, we configure a busy retry timeout:

```sql
PRAGMA busy_timeout = 30000;
```

This instructs SQLite to wait for up to $30$ seconds (busy-retrying) for any lock to clear before throwing an error.

---

## 3. Core Leaderboard Database Schema

Below is the SQL schema defined in [TaxonomyRankingService](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/service/TaxonomyRankingService.kt) to manage evaluation states:

```sql
-- Tracks pairwise contest statistics at specific nodes
CREATE TABLE IF NOT EXISTS node_pair_stats (
    snapshot_id TEXT NOT NULL,
    node_id TEXT NOT NULL,
    model_a TEXT NOT NULL,
    model_b TEXT NOT NULL,
    wins_a REAL DEFAULT 0.0,
    wins_b REAL DEFAULT 0.0,
    ties INTEGER DEFAULT 0,
    total_comparisons INTEGER DEFAULT 0,
    position_flips INTEGER DEFAULT 0,
    last_updated INTEGER,
    PRIMARY KEY (snapshot_id, node_id, model_a, model_b)
);

-- Stores fitted Bradley-Terry log-strength parameters
CREATE TABLE IF NOT EXISTS node_bt_states (
    snapshot_id TEXT NOT NULL,
    node_id TEXT NOT NULL,
    bt_scores TEXT NOT NULL,       -- JSON mapping: modelId -> log-strength
    std_errors TEXT NOT NULL,      -- JSON mapping: modelId -> standard error
    fit_version INTEGER,
    total_comparisons INTEGER,
    last_fit_at INTEGER,
    PRIMARY KEY (snapshot_id, node_id)
);

-- Caches individual LLM pairwise verdicts to prevent re-evaluation
CREATE TABLE IF NOT EXISTS match_history (
    snapshot_id TEXT NOT NULL,
    domain TEXT NOT NULL,
    query TEXT NOT NULL,
    model_a TEXT NOT NULL,
    model_b TEXT NOT NULL,
    winner TEXT NOT NULL,
    confidence REAL,
    tie_source TEXT,
    PRIMARY KEY (snapshot_id, domain, query, model_a, model_b)
);
```

These tables are managed using standard Java Database Connectivity (JDBC) connections, wrapped in connection-closing templates:

```kotlin
private inline fun <T> withConn(block: (Connection) -> T): T {
    val conn = DriverManager.getConnection(dbUrl)
    return conn.use(block)
}
```

This guarantees connections are returned to the OS, preventing connection leaks.

---

## 🔗 Related Code References
*   [TaxonomyRankingService](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/service/TaxonomyRankingService.kt): Contains the schema definitions and JDBC transaction templates.
*   [TaxonomyPersistence](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/service/TaxonomyPersistence.kt): Manages snapshot serializations and DB initializations.
