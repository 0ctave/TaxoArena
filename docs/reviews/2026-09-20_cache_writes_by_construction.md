# Cache writes by a construction and by a site null: K-SELECTION post-run review defect 7

data-steward, 2026-09-20. Zero calls. Every database opened `mode=ro` (embeddings_cache.db additionally in the `immutable=1` view and as a scratch copy with its WAL, see 2.2); nothing under the repo root written except this file. Engine read at HEAD 3227e37 (`src/main/kotlin`, `src/test/kotlin`). Objects: `embeddings_cache.db` (393,478,144 B, mtime 2026-09-19 16:29:42.085; `-wal` 4,161,232 B at 16:29:42.100), `mmlu_pro_dataset_cache_v2.db` (974,917,632 B, mtime 16:30:10.107; `-wal` 0 B at 16:58:06.75), the four K-SELECTION build logs (`experiment_results/anchorfree/redraw/kselect/{i2,af_clean_s42_k105,af_s137_k105,af_s2048_k105}.build.out`), `chain.log`, `experiment_configs/reserved_pool_frozen_p2dca.json`.

Question (docs/reviews/2026-09-19_k_selection_post.md defect 7; docs/judge_v2_program.md K-SELECTION outcome ~L9576): both files' mtimes moved inside the R3' window; pool_guard passes; no content sha was pinned; "no write to a DB of record" UNDETERMINED for the chain.

Short answer. A construction WRITES to both files by design, on every run, with zero calls and with the cache warm: (a) `embeddings_cache.db.queries` receives one `INSERT OR REPLACE` per distinct tree text at snapshot save (8,125 / 8,125 / 8,126 / 8,130 rows for I2 / R1' / R2' / R3'); (b) `mmlu_pro_dataset_cache_v2.db.reserved_pool_meta` receives one `INSERT OR REPLACE` per build at split time (`created_at` = now, seed / test_ratio NULL on the reserved-file path), plus an `INSERT OR IGNORE` into `reserved_pool` that adds nothing for a known pool. A site null opens the dataset cache read-write for six `CREATE TABLE IF NOT EXISTS` (no-ops) and the embedding cache read-only. On disk: the pool of record is set-equal to the frozen JSON (3,445 = 3,445, 0 / 0 differences); `embeddings` is unchanged in count and content hash between the main-file and WAL-inclusive views (20,710 rows); `queries` holds MMLU-Pro categories for all 11,769 MMLU-Pro texts with no union-style residue; the three `reserved_pool_meta` rows the chain rewrote carry its timestamps to the second. Verdict per file in section 2.

## 1. Write inventory, per file, per stage (file:line at HEAD 3227e37)

### 1.1 Construction: HeadlessBenchmarkRunner, `runPipeline = true`, `runBenchmark = false`, `runTrickle = true`, `runBaselines = false`, `enableLabeling = false`, `judgeInduction = false` (the four kselect TOMLs, e.g. `experiment_configs/anchorfree/redraw/kselect/af_s2048_k105.toml`)

`mmlu_pro_dataset_cache_v2.db` (the eval / dataset cache; also `reserved_pool`):

| stage | code | statement | effect on an existing DB |
|---|---|---|---|
| Spring start, bean `ModelEvalStore` | `ModelEvalStore.kt:53` URL `jdbc:sqlite:<db>?journal_mode=WAL&synchronous=NORMAL&busy_timeout=10000`; `:59-61` one shared read-write connection, autocommit | `PRAGMA journal_mode=WAL` (driver, on connect) | no-op: file header bytes 18/19 are 2/2 (already WAL) |
| same, `initSchema()` `:129-200` | `CREATE TABLE IF NOT EXISTS eval_results` `:134`, `CREATE INDEX IF NOT EXISTS` x2 `:153,:155`, `CREATE TABLE IF NOT EXISTS eval_question_link` `:159`, index `:168`, `ReservedPool.ensureSchema` `:172` (`ReservedPool.kt:44-77`: `reserved_pool`, `idx_reserved_pool_q`, `reserved_pool_meta`), `CREATE TABLE IF NOT EXISTS corpus_registry` `:177`, `INSERT OR IGNORE INTO corpus_registry` `:189-197` | all no-ops on the existing schema; `INSERT OR IGNORE` on the existing `MMLU_PRO` primary key dirties no page | none |
| Spring start, bean `MMLUDatasetFetcher` | `MMLUDatasetFetcher.kt:52` same URL form; `initDatabase()` `:117-185`: six `CREATE TABLE IF NOT EXISTS` (`mmlu_pro`, `mmlu_original`, `arc`, `twenty_newsgroups`, `ag_news`, `eval_question_link`) | no-ops | none |
| split (start of the build) | `HeadlessBenchmarkRunner.kt:526-535` -> `splitByReservedFile` `MMLUDatasetFetcher.kt:796-817` (R1', I2: reservedPoolFile = the frozen p2dca JSON) or `splitTrainTest` `:729-784` (R2' seed 137, R3' seed 2048) -> `recordPool` `:820-851` -> `ReservedPool.save` `ReservedPool.kt:127-181` | `INSERT OR IGNORE INTO reserved_pool` (judgeable ids) `:141-153`; `INSERT OR REPLACE INTO reserved_pool_meta (pool_id, dataset, corpus_size, seed, test_ratio, domains, question_count, domain_count, created_at)` `:154-172`; one committed transaction `:173` | `reserved_pool`: no row added when the pool is already recorded; `reserved_pool_meta`: THE ROW IS REWRITTEN ON EVERY BUILD (`created_at` = now; `seed`, `test_ratio` NULL on the file path, `:815`; the seed and ratio on the seed path, `:782`). Also rewrites the root file `reserved_test_queries.json` `:762` / `:814` (a file, gitignored L139, not a DB) |
| TRAIN-ONLY guard after construction | `HeadlessBenchmarkRunner.kt:591` `evalStore.getReservedQuestionTexts(pool)` | SELECT | none |
| snapshot save | `TaxonomySnapshotManager.kt:614` `getReservedQuestionTexts` | SELECT | none |
| trickle validation (`runTrickle`) | `HeadlessBenchmarkRunner.kt:917-928` `fetchDataset` (SELECT), `runHeadlessTrickle` | reads only; the ingestion writers `saveBatch` `ModelEvalStore.kt:229` / `saveLinks` `:270` are reached only from `ModelEvalLoader.kt:268-269`, whose callers are the TUI (`TuiGatewayImpl.kt:865,886`); `recordReservedPool` `:299` is reached from the union graft `HeadlessBenchmarkRunner.kt:1117` and from `loadSnapshot` `TaxonomySnapshotManager.kt:796`, neither on this path | none |
| JVM exit | shutdown hooks `ModelEvalStore.kt:113-122`, `MMLUDatasetFetcher.kt:103-112` close the two shared connections | SQLite checkpoint-on-close of the WAL when the closing connection is the last one and obtains the exclusive lock: backfills the split-time frames into the main file (page 1 change counter + the `reserved_pool_meta` leaf page(s)), then deletes or truncates the `-wal` | this is the main-file write that moves the mtime; content = the split-time transaction |

`embeddings_cache.db` (the query / embedding cache):

| stage | code | statement | effect on an existing DB |
|---|---|---|---|
| Spring start, bean `EmbeddingCache` | `EmbeddingCache.kt:39-44` file chosen by embedding model (`embeddings_cache.db` for qwen3), URL with `journal_mode=WAL`; `:53-57` ONE lazy shared read-write connection, autocommit; `initDatabase()` `:67-117`: `CREATE TABLE IF NOT EXISTS embeddings / gmm_vectors / queries` `:72-103`, two `ALTER TABLE queries ADD COLUMN` `:106,:109` that throw "duplicate column" and are swallowed | no-ops | none. NOTE `EmbeddingCache` has NO shutdown hook (contrast the other three stores): its WAL is never checkpointed at exit |
| phase 1 precompute | `TaxonomyEngine.kt:104` `embeddingCache.precompute(allTexts)` -> `EmbeddingCache.kt:302-335` | `INSERT OR REPLACE INTO embeddings` `:342` ONLY for texts with no cached vector (`:304`), after an embedding call | none when the cache is warm: all four build logs print `All 8125/8125/8126/8130 requested embeddings are already cached on disk.` (i2.build.out L72, af_clean L72, af_s137 L73, af_s2048 L73) |
| routing / trickle | `TaxonomyService.kt:121,141`, `TaxonomyArenaService.kt:382,404` `getOrCreate` -> `EmbeddingCache.kt:286-300` | `INSERT OR REPLACE INTO embeddings` on a cache miss only | none: every one of the 11,769 distinct `mmlu_pro` texts has an `embeddings` row (section 2.2) |
| snapshot save | `HeadlessBenchmarkRunner.kt:604` -> `TaxonomySnapshotManager.saveSnapshot` `:533-663` -> `:542 persistence.save` -> `TaxonomyPersistence.kt:92-96` | `INSERT OR REPLACE INTO queries (id, raw_text, distilled_text, ground_truth_category, query_id)` `EmbeddingCache.kt:122` for EVERY distinct `rawText` in the tree (`q_<sha256[:16]>` id), one autocommit transaction per row | THE WRITE OF RECORD: ~8.1k rows rewritten per build with the values the MMLU_PRO loader carries (pretty-cased category, eval question id). Idempotent for an MMLU_PRO build over MMLU_PRO-written rows; NOT idempotent across corpora (the text-keyed, last-writer-wins hazard: `HeadlessBenchmarkRunner.kt:1174-1177` records the 2026-09-11 incident where an MMLU_PRO run rewrote MMLU_PRO_LB categories) |
| `gmm_vectors` | `putGmmVectors` `EmbeddingCache.kt:189` | no caller in `src/main` | none (table has 0 rows) |
| JVM exit | no hook | the `-wal` keeps whatever the last auto-checkpoint (1,000-page threshold, driver default) did not backfill; the next read-write opener that closes last backfills it | mtime of the main file moves at the auto-checkpoint(s) inside `persistence.save`, not at exit |

Timeline check on R3' (af_s2048_k105.build.out): split `[POOL] recorded p19d9f473b5a610a0` 16:28:17.335; `dag_snapshots.jsonl` 16:29:40.58 (save begins); `embeddings_cache.db` main 16:29:42.085 and `-wal` 16:29:42.100 (the `queries` rewrite, auto-checkpointed once past 1,000 pages, 26 live frames left in the WAL); `[POOL-PIN] snapshot stores ... p19d9f473b5a610a0` 16:29:42.508; snapshot saved 16:29:42.789; hooks closed 16:30:05.700-.717 (`snapshots.db` main 16:30:05.707 = its checkpoint-on-close); chain `BUILD exit 0` 16:30:06; `SITENULL start` 16:30:07; `snapshots.db-wal` truncated 16:30:10.009; `mmlu_pro_dataset_cache_v2.db` main 16:30:10.107. The dataset-cache main-file write therefore lands 4.4 s after the build JVM's own hooks and 2.5 s after the site-null JVM started: it is the checkpoint of the split-time frames (content = R3''s `reserved_pool_meta` row, section 2.1), most plausibly performed by the site-null JVM's fetcher connection on close (1.2) after the build's close did not backfill (not the last handle, or the exclusive lock not obtained). Which process performed the checkpoint is not decidable from mtimes and is content-irrelevant: the WAL is now 0 bytes and the main file's content is enumerated below.

### 1.2 Site null: `gradlew siteNull` (`build.gradle.kts:184-202` -> `SeparationNullBySizeTest.kt:1643`)

| file | code | statement | effect |
|---|---|---|---|
| `embeddings_cache.db` | `SeparationNullBySizeTest.kt:1710-1711` `SQLiteConfig().setReadOnly(true)`; also `:1645` existence check | SELECT vectors by id | none (SQLITE_OPEN_READONLY; a read-only connection cannot checkpoint or truncate) |
| `snapshots.db` / `snapshots_frozen.db` | `:1648 loadFrozenGraph` -> `:1304-1307`, read-only | SELECT | none |
| `mmlu_pro_dataset_cache_v2.db` | `:1659 MMLUDatasetFetcher(config, "")` (second argument = `hfToken`; `dbPath` defaults to `mmlu_pro_dataset_cache_v2.db`, `MMLUDatasetFetcher.kt:28-29`); `isTest` `:54-55` is true under the Gradle worker so `connection` `:66-69` opens a FRESH read-write connection per call, closed by `.use` (`:119`) | `PRAGMA journal_mode=WAL` + six `CREATE TABLE IF NOT EXISTS` | no content; on close (last connection) SQLite checkpoints any frames another process left in the `-wal` and deletes / truncates it. The site null is thus a journal-touching reader of the dataset cache, not a writer |

`isoNullByDim`, `withinNull` and the other harness arms use the same three handles (`:300, :606, :1157, :1251, :1369`): same inventory.

## 2. Did the 2026-09-19 chain (15:26-16:58) change content?

### 2.1 `mmlu_pro_dataset_cache_v2.db`: CHANGED, in `reserved_pool_meta` only; the pool of record CONFIRMED unchanged

Read `file:...?mode=ro&immutable=1` (the `-wal` is 0 bytes, so the immutable and WAL-inclusive views coincide). `PRAGMA page_size 4096, page_count 238017, freelist_count 240, schema_version 16`. Tables and counts: `active_reserved_pool` 1 (legacy, physically present, unread), `ag_news` 2,000, `arc` 0, `corpus_registry` 1 (`MMLU_PRO, mmlu_pro, 0, MC_LETTER`), `eval_question_link` 12,257, `eval_results` 560,379 (47 models; 12,118 distinct question_id; the legacy `is_reserved` column and `idx_eval_reserved` still exist physically), `mmlu_original` 0, `mmlu_pro` 12,000 (11,769 distinct texts), `reserved_pool` 146,568 rows over 48 pools, `reserved_pool_meta` 49 rows, `twenty_newsgroups` 0.

Pool of record: `SELECT domain, question_id FROM reserved_pool WHERE pool_id='p2dca21ab5f4ef3ae'` = 3,445 rows; the frozen JSON has 3,599 ids of which 3,445 > 0; set difference JSON - DB = 0, DB - JSON = 0 (denominator: the 3,445 judgeable ids; sentinels are never stored). K-SELECTION's own pools: `pd610c9ad05255f16` 3,448 rows, `p19d9f473b5a610a0` 3,446 rows = the build logs' "3448 / 3446 judgeable ids"; both were first recorded by REDRAW R2 / R3 (same seeds) on 2026-09-17/18, and `INSERT OR IGNORE` cannot alter an existing row.

The chain's writes, to the second (`created_at` -> local time), against the build logs:

| pool | `reserved_pool_meta` now | build log line |
|---|---|---|
| p2dca21ab5f4ef3ae | dataset `mmlu_pro`, corpus_size 12000, seed NULL, test_ratio NULL, 3445 / 14, created_at 2026-09-19 15:28:18 | af_clean_s42_k105 L30 `15:28:18.971 [POOL] recorded p2dca21ab5f4ef3ae (file reserved_pool_frozen_p2dca.json ...)`; I2 had written the same row at 15:26:28 (i2 L32) and R1' overwrote it |
| pd610c9ad05255f16 | `mmlu_pro`, 12000, seed 137, 0.3, 3448 / 14, 2026-09-19 15:58:14 | af_s137_k105 L31 `15:58:14.556` |
| p19d9f473b5a610a0 | `mmlu_pro`, 12000, seed 2048, 0.3, 3446 / 14, 2026-09-19 16:28:17 | af_s2048_k105 L31 `16:28:17.335` |

So the chain rewrote three `reserved_pool_meta` rows (the same three REDRAW had rewritten on 09-17/18; the p2dca row is rewritten by every clean build, and its original 2026-07 provenance -- seed 42, ratio 0.3 -- is not recoverable from this table; it lives in the frozen JSON and the record). Every other table has no write path on the construction or site-null path (section 1) and the pool rows are set-equal to the frozen JSON. Pre-chain per-table hashes do not exist (the README's whole-file sha256 of 2026-08-02, `docs/README.md:81-82`, pre-dates every construction since and is a byte hash, so it cannot serve), so "unchanged" for `eval_results`, `eval_question_link`, `mmlu_pro`, `corpus_registry`, `ag_news` rests on the absence of a write path plus the counts and hashes now pinned in section 3, not on a before/after comparison.

### 2.2 `embeddings_cache.db`: CHANGED in bytes, CONTENT-IDEMPOTENT for the rows it holds; `embeddings` CONFIRMED unchanged

Three views were compared: (i) `mode=ro&immutable=1` (main file only), (ii) `mode=ro` (WAL-inclusive through the existing `-shm`), (iii) a scratch copy of main + `-wal` without `-shm`, so SQLite rebuilt the wal-index from the frames with checksum validation. `PRAGMA page_size 4096, page_count 96064, freelist_count 94, schema_version 7`. Tables: `agent_ratings` 0, `embeddings` 20,710 (all vectors 16,384 B = 4,096 float32), `gmm_vectors` 0, `match_history` 0, `queries` 18,741, `sqlite_sequence` 0. All three views agree on every count and on every content hash; rows added / removed / changed between (iii) and (i): 0 / 0 / 0.

The WAL itself (parsed byte-wise): header checksum valid, little-endian, checkpoint sequence 864, 1,010 frames of which 26 are salt-valid AND checksum-chain-valid (6 commit frames; pages 1, 22705, 23211, 43630, 43659, 43725, 43786, 44023, 47472, 48448, 51743, 51785, 52416, 83505, 83911, 83913, 95527, 96059), 984 stale. Of the 26 live frames, 25 differ from the corresponding main-file page and yet the replayed content equals the main-file content: they are the last six `INSERT OR REPLACE INTO queries` transactions of the R3' save, which deleted and re-inserted rows with identical values (page layout changes, logical rows do not). A later checkpoint will copy those 18 pages into the main file and move any whole-file sha256 without moving any table hash: this is the journal touch the pin must survive.

Content state of `queries`: 54 distinct `ground_truth_category` values; the 14 MMLU-Pro categories in pretty case (Math 1,346 ... History 381), 39 union keys (`BBH/*`, `MATH/*`, `GPQA/*`, `MUSR/*`, `IFEVAL/ifeval`, `MMLU_PRO_LB/chemistry` 1, `MMLU_PRO_LB/engineering` 33). All 11,769 distinct `mmlu_pro` texts are present (0 absent), every one carries its own `mmlu_pro.category` in pretty case (the case-sensitive comparison flags all 11,769 as `business` vs `Business`; case-insensitively 0 differ), 0 MMLU-Pro texts carry a union-style key, `query_id` is never -1 and equals a linked eval `question_id` for 11,494 / 11,769 (the remainder are sentinel ids for unlinked texts). The 34 `MMLU_PRO_LB/*` rows are texts that do not occur in `mmlu_pro` (union-only copies): residue of the 09-10/11 union builds, untouched by this chain. All 3,445 pool texts also have `queries` rows (written by earlier builds on other splits; the table is a text -> metadata map, not a membership record, so this is not a TRAIN-ONLY fact).

`embeddings`: 20,710 rows in every view, sha256 over (query, vector bytes) ordered by query = `785e90c378e6808433b90fcd1046710784ba48d8fd37b900d0eb3b7113681fc2`; the only insert path is a cache miss (1.1) and all four logs report a warm cache; all 11,769 MMLU-Pro texts have a vector, so the trickle could not miss either. CONFIRMED unchanged by the chain (by write-path exclusion plus the log lines; no pre-chain hash exists). [STALE AS OF 2026-09-23 (registrar, insertion only): both tables have grown through later builds and the WAL was checkpointed; the counts of record are embeddings 39,631 (sha256 641ff6fad35bd1af...) and queries 31,986 (sha256 cdeca05e573e2578...), see docs/judge_v2_program.md L14004-L14032.]

Verdict for defect 7: the mtime moves are the two writes the engine makes by design (`queries` rewrite at snapshot save; `reserved_pool_meta` rewrite at split, checkpointed at the next last-connection close). "No write to a DB of record" is FALSE as a sentence about these two files and always was; the sentence that holds is "no change to any table the record reads for its numbers": `reserved_pool` p2dca set-equal to the frozen JSON, `embeddings` unchanged, `queries` MMLU-Pro rows carrying the MMLU-Pro values (and the last six rewrites provably identical), no union-side row touched by an MMLU_PRO build. The one field the chain overwrote irreversibly, `reserved_pool_meta.created_at` (and seed / test_ratio -> NULL for p2dca), is read by no analysis of record (the programme cites `reserved_pool_meta` once, at L5440, for union stratum supports, which are `question_count` per pool and unchanged).

## 3. The pin for the next construction READY

Pin per-table content, not the file: a WAL checkpoint, a `-wal` truncation or an `INSERT OR REPLACE` of identical rows moves the byte hash without moving a table hash. Read BOTH views and refuse if they differ (a live WAL tail that `immutable=1` would hide). Command (Python, any cwd, no tool file needed):

```
python - <<'PY'
import sqlite3, hashlib
ROOT = "Z:/FAC/TUBerlin/THESIS/TaxoArena"
PIN = {  # (table, order-by): rows ordered by primary key, sha256 over repr(row)
  f"{ROOT}/mmlu_pro_dataset_cache_v2.db": [("reserved_pool","pool_id, question_id"), ("reserved_pool_meta","pool_id"),
      ("eval_results","question_id, model_name"), ("eval_question_link","question_id"), ("mmlu_pro","id"),
      ("corpus_registry","source"), ("ag_news","id")],
  f"{ROOT}/embeddings_cache.db": [("embeddings","query"), ("queries","id"), ("gmm_vectors","id")],
}
for db, tabs in PIN.items():
    for view in ("mode=ro&immutable=1", "mode=ro"):
        c = sqlite3.connect(f"file:{db}?{view}", uri=True)
        for t, order in tabs:
            h = hashlib.sha256(); n = 0
            for row in c.execute(f'SELECT * FROM "{t}" ORDER BY {order}'):
                h.update(repr(row).encode()); h.update(b"\n"); n += 1
            print(f"{db.rsplit('/',1)[1]:32s} {view:20s} {t:20s} n={n:>8} sha256={h.hexdigest()}")
        c.close()
PY
```

Reference values as of 2026-09-20 (both views identical; these are the post-chain state and the baseline for the next build):

| file | table | n | sha256 |
|---|---|---|---|
| mmlu_pro_dataset_cache_v2.db | reserved_pool | 146,568 | 28d9798780ef1f5359dbba33601c4ec7527d8bd701ed062f88efddd90eea6e9c |
| | reserved_pool_meta | 49 | abc139e7e4171e2bbfa131cd754b28d7a715d3888edbb9be72fc5efb6d613455 |
| | eval_results | 560,379 | a94aedd601c9a6848b4442370577423ffef77b5aaf96f74a679db3e0df5177ee |
| | eval_question_link | 12,257 | 0d57b5d16dacc6bdec1eaf7b15616054d9711f40aa7e48ab810a3c500e908872 |
| | mmlu_pro | 12,000 | dee480a9b27272108b189b6fd458c0fdd901f677e6e56406425f94b2a974a83e |
| | corpus_registry | 1 | bbd4811d24257ee35df3bb9bf90a38506fe9480a904f588ff528541a48107264 |
| | ag_news | 2,000 | 7eb1c9dfd76b97fe5094ccc743ad5d74dccd5148867a42b3711edc9e53099a20 |
| embeddings_cache.db | embeddings | 20,710 | 785e90c378e6808433b90fcd1046710784ba48d8fd37b900d0eb3b7113681fc2 |
| | queries | 18,741 | c123ca739cd4d8b0917d69e7caf3e7fb950254c687cb8b5c90aec42cb67c0a2d | [STALE AS OF 2026-09-23 (registrar, insertion only): both tables have grown through later builds and the WAL was checkpointed; the counts of record are embeddings 39,631 (sha256 641ff6fad35bd1af...) and queries 31,986 (sha256 cdeca05e573e2578...), see docs/judge_v2_program.md L14004-L14032.]
| | gmm_vectors | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |

Expected movement after one MMLU_PRO construction with a warm cache, to be written into the READY as the acceptance rule: every hash above UNCHANGED except (a) `reserved_pool_meta` (exactly the build's own pool row: `created_at` inside the build window, seed / test_ratio per the split path; `n` +1 only for a never-recorded pool) and (b) `reserved_pool` `n` + judgeable ids only for a never-recorded pool; `queries` unchanged for an MMLU_PRO build (the rewrite is idempotent) and CHANGED for any union or leaderboard build on the texts it shares with MMLU-Pro (the 2026-09-11 hazard; then the READY must list the rewritten (text, category) pairs). A whole-file sha256 (README L81-82 style; today `85fc5bc387efd095eb42d99b565a6fecff2e8848baa15ea82fb24a7fe9cccf35` and `4f65414f7625a1e7da44cc599bbf4a951e8866f472fa9532f09ee103953efa73`) is NOT a pin: it moves on every build and on every checkpoint. Also pin the root `reserved_test_queries.json` pool id: it is the split transport, rewritten by every build, and today hashes to R3''s `p19d9f473b5a610a0` (3,599 ids), not to p2dca; a build that must judge on p2dca takes `reservedPoolFile`, never this file.

Reader hazard to carry: `immutable=1` ignores the WAL. Today the embedding cache's 26 live frames are content-identical to the main file, so both views agree; after a build whose last `queries` rewrites are NOT idempotent (a union build), an `immutable=1` reader would read the pre-build categories for up to ~1,000 pages of rows while the engine reads the post-build ones. The audit rule is: if `-wal` is non-empty, read both views and report the delta; the standing `EmbeddingCache` design (no shutdown hook, `EmbeddingCache.kt:53-65` vs the hooks at `ModelEvalStore.kt:113`, `MMLUDatasetFetcher.kt:103`, `TaxonomySnapshotManager.kt:331`) guarantees a tail can be left behind.

## 4. `.gitignore` and the `!experiment_results/**/*.db` negation

Both files live at the repo root, not under `experiment_results/`. `git check-ignore -v` resolves both to `.gitignore:58 *.db`; `git ls-files --error-unmatch` reports neither is known to git. The negation at L145 re-includes only `experiment_results/**/*.db`, so it does not reach them; the only root-level negation is `!/snapshots_frozen.db` (L158). Consequence: there is no git-tracked copy of either cache to diff against, and no pre-chain reference exists anywhere on disk (the `.claude/worktrees/*` copies are 09-07/09-08 and 09-16 forks, `archive/mmlu_pro_dataset_cache_v2.db.bak-*` are 2026-07-26/27, `TaxoArena-kselect/` holds 4 KB / 77 KB stubs). The negation therefore does not matter for defect 7; the per-table pin in section 3 is the reference from now on.

Backup status (steward's list): `embeddings_cache.db` and `mmlu_pro_dataset_cache_v2.db` are gitignored and have NO current backup (latest July / early-September forks only, none with today's `reserved_pool` or `queries` content). Recommended: a dated copy of both into `experiment_results/_backup/` (which is untracked and already holds the 09-19 verdict-cache backups) before the next construction, taken with no JVM running, copying `-wal` alongside or after a clean close.

## 5. What this does not show

Byte-level identity of the ~8.1k `queries` rows each build rewrote before the last auto-checkpoint (no pre-chain hash; the six live-WAL rewrites are the only ones proven identical); the exact process that checkpointed the dataset cache at 16:30:10 (build hooks vs site-null fetcher close; content-irrelevant); the pre-chain value of the p2dca `reserved_pool_meta` row (rewritten by every clean build since the reserved-file path exists). Nothing here reopens any K-SELECTION number: the readouts read snapshots, CSVs and the pool rows, all of which are unchanged or set-equal to the record.
