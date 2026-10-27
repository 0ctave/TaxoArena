# READY e1-route2 (tip 4968a290): E1-ROUTE re-cut, delta review against READY_backfill_2026-09-30 (b938c14)

Adversarial-reviewer, 2026-10-01. Zero calls; no JVM, no Gradle, no construction. Registration: E1-ROUTE prog L22182-L22206
(_as_of 28b4032b); E1 = EMBEDDER-CROSS-FLAT L21705-L21730. main HEAD now c6ee6155 (1 commit ahead of the branch, one review
file only: `git diff --name-only e1-route2...main` = 1 line, 0 under src/ or tools/analysis/). Ledger unchanged (v331).

## VERDICT

- **e1-route2 4968a290: MERGEABLE by path** (7 files: build.gradle.kts, the 3 src/main files, EmbeddingCacheManifestTest.kt,
  tools/analysis/e1_route_launch.py, experiment_configs/e1_route/L1_short_af_clean_s42.toml). `git merge-tree` clean.
- **E1-ROUTE L0/L1/L2: READY** under C-E1R-1..6. B-E1-1, B-E1-2, C-E1-3, C-E1-4 of b938c14 are CLOSED.
- **E1 (EMBEDDER-CROSS-FLAT N-raw, N-card via the route): READY, conditional** on E1-ROUTE C1-C5 HELD after L1/L2
  (the registration's own gate) and on C-E1R-4 (E1's two configs declared). F1 of E1-ROUTE firing = E1 stays NOT READY.

## Per-claim table (deciding claims only)

| # | claim | mine | status | sev |
|---|---|---|---|---|
| D1 | B-E1-1 (1): any -wal/-shm/-journal beside a member of P or the DIR file under test REFUSES before copy and launch | code L250-L256, called L327 before `before`, before the dry-run return; selftest b1 = 54/54 refusals (9 sites x 3 kinds x run/dry); my real-SQLite probe P1 (P-E1a re-run: sidecars left by a held WAL reader, the "JVM" writes a WAL frame): rc 2, `REFUSED: (B-E1-1) 2 sidecar(s)`, 0 launches | CONFIRMED | - |
| D2 | B-E1-1 (2): view() records sidecar size + sha256; a WAL-tail write is a breach | probe P2 (no sidecars before; WAL frame written, main file bytes unchanged, handle held): PIN BREACH rc 2; P3 (write + checkpoint into main cache, sidecars gone after): PIN BREACH; P4 (a `mode=ro` open that leaves sidecars): PIN BREACH; P5 control: rc 0 | CONFIRMED | - |
| D3 | B-E1-2: L1 TOML = af_clean_s42.toml with exactly numIterations 2 and its own outputDir | `diff` of af_clean_s42.toml against the L1 file below `# ---- BASE ----`: exactly 2 lines (L44 outputDir, L78 numIterations); outputDir experiment_results/e1_route/L1_short, absent on disk, 0 tracked files under it; the launcher refuses af_clean_s42.toml itself (selftest b2) | CONFIRMED | - |
| D4 | C-E1-3: data root must equal the JVM cwd | check_data_root L201 (normcase+realpath equality, sub-dir refused, case/trailing-sep admitted); bootRun `workingDir = rootDir`; `ranking.db.path`, `taxoadapt.llm.embedding-model`, both taxoarena.* properties forwarded (build.gradle.kts L341-L350) | CONFIRMED | - |
| D5 | C-E1-4: code pins 2073d131 / 7868e858 unchanged, enforced | `git rev-parse` on branch and main: 2073d131 / 7868e858; ro.git_blob_lf of main's CRLF working files: same; refusal on a wrong blob or a foreign imported module (selftest c4) | CONFIRMED | - |
| D6 | selftest 15/15 | 15/15 (worktree, 1.1 s) and 15/15 on a scratch copy | CONFIRMED | - |
| D7 | suite 519, 2 known failures; EmbeddingCacheManifestTest 4/4 executed | from the worktree's own XMLs (102 files, 17:32:50-17:33:49Z): 519 tests, 2 failures = MrlRoutingTest.testMrlConfigDefaults, TraceEnvelopeUnwrapTest blank-trace; 0 err, 0 skipped; Manifest test 4/4, 0 skipped; EvalMetricDeterminismTest (from main's merge) present, 8/8, so the merged tree was tested; new identifier `embeddingCacheSourceSha256` in compiled EmbeddingCache classes (count 3). Not re-run by me | CONFIRMED (artefacts) | - |
| D8 | C4 inert when absent; src/main diff = the declared files | `git diff --name-status main e1-route2` = 7 files (3 src/main as declared); absent -> explicitFileManifest(null,null) = {} -> false, no key (test 1); runner has exactly 1 call site (test 4) | CONFIRMED | - |
| D9 | builder's 24/24 mutants | not re-run; my own 4 on deciding paths all KILLED (below) | CONFIRMED (spot) | - |
| D10 | E1 filing Support (EMBEDDER-CROSS-FLAT (d)/(e)) | sqrt(0.15/3,445) = 0.006599; x2.80 = 0.01848 = 0.0185; DEFF 1.0 (singleton twin groups, measured); P4 -0.04 beyond the bar: SCOREABLE reproduces | CONFIRMED | - |

## Pins (LF of record; working tree CRLF beside)

e1_route_launch.py blob:ba865deb, sha256-lf16:1093170354dc0662, sha256-crlf16:d10a92c834b1e89d (worktree CRLF; CRLF blob
0a9ce184). L1 TOML blob:073a7ddf, lf16:4cc5f2576711c8ab (worktree LF). EmbeddingCache.kt blob:2e2b125e lf16:ccd5f66291c0263d
crlf16:60939f556771adfb. DiagnosticsBundle.kt blob:3a544b1d lf16:973ff9e3071e1a7d crlf16:2056559de9e88282.
HeadlessBenchmarkRunner.kt blob:b7559c73 lf16:48682e1e48d886c3 crlf16:fb146e55705806f7. EmbeddingCacheManifestTest.kt
blob:a8d74266 lf16:d9548591f7a390f7 crlf16:08085a19e78680fc. build.gradle.kts blob:11235f68 lf16:4c3b2ba21acf1f37.
Pins file embedder_cross_arm_pins.json blob:c7eb60fd (main working tree = HEAD).

## Main checkout state (decides the operator's first step)

`ls` of every member of P (count by script, all 8 + 3 suffixes): **6 sidecars**, all beside 3 members:
embeddings_cache.db, embeddings_cache_nomic-embed-text_latest.db, embeddings_cache_embeddinggemma_latest.db, each with
-wal **0 B** and -shm **32,768 B** (not 0 B as the brief says). snapshots_frozen.db and the 4 DIR files: none. Exclusive-open
probe (FileShare None): all 7 files FREE now. embeddings_cache.db-shm mtime 2026-10-01 09:11:49: a non-immutable reader
opened the main cache today. The launcher will REFUSE (B-E1-1, "6 sidecar(s)") on every leg until they are gone.

## Defects and conditions

- **C-E1R-1 (BLOCKING for L0-L2 on main; operator).** The 6 sidecars. In one rule-7 window, after the by-path merge and the
  backup: (a) exclusive-open probe FREE on the 3 DBs and their sidecars, no admitted reader of them running (a JVM or any
  `mode=ro` open without immutable=1 recreates them); (b) require every -wal = 0 B (no uncommitted frames). If any -wal > 0:
  STOP, do not checkpoint (a write to a DB of record), hand to the data-steward; (c) record sha256 of the 3 DB files, MOVE (not
  delete) the 6 sidecars to the dated backup folder, re-hash: equal; (d) immediately run `--selftest` and the launcher
  `--dry-run`, which must print "(B-E1-1) no -wal / -shm / -journal beside any of the 9 hashed files". Never remove a sidecar
  that appears AFTER a leg: that is a C2 FAIL by the registration, scored as such.
- **C-E1R-2 (HIGH).** L0, L1, L2 and E1 run only from the main checkout after the merge (C-E1-3 refuses elsewhere), with
  main's tools/analysis at 2073d131 / 7868e858 (the launcher refuses otherwise).
- **C-E1R-3 (MEDIUM).** `launch_cmd` has no `--no-daemon`: after L1 a Gradle daemon java.exe remains (blocks the next Ollama
  run; inflates the "java PIDs after" line). Operator: run `gradlew --stop` after each leg, or the builder adds
  `--no-daemon` (one token; re-run selftest). C1's "no new java.exe" is printed, not enforced: the operator scores it.
- **C-E1R-4 (HIGH, E1).** The launcher refuses af_clean_s42.toml, which EMBEDDER-CROSS-FLAT names as E1's config. E1's two
  configs (N-raw, N-card) must be committed and declared before E1: af_clean_s42.toml with ONLY outputDir changed, two distinct
  outputDirs outside every object of record (the registrar records this as a non-treatment key).
- **C-E1R-5 (carried C-E1-5, MEDIUM).** subprocess.call captures nothing: the operator tees the JVM transcript and scores C3
  from it (vmfMu cos >= 0.99, vector length, misses = 0; misses > 0 VOIDS the leg).
- **C-E1R-6 (LOW).** C3's "manifest source sha256 = the pin" is true by construction (the launcher passes the pin); it proves
  forwarding only. The substance is (ii)'s copy hash. Word C3's fourth check accordingly.
- **Note (static, not a defect).** In the JVM, main's embeddings_cache.db is opened by EmbeddingCache only without the property
  (DB_OF_RECORD) and by ModelEvalLoader.fetchEmbeddingHits (eval-import path); ReservedPool.save writes the corpus DB
  mmlu_pro_dataset_cache_v2.db (not in P). So C2 is plausibly reachable; the registration's (g) leg stays UNDETERMINED until L1.

## Own mutants (scratch copy of tools/analysis, one edit at a time, bytes restored)

- Ma: the sidecar refusal only on NON-EMPTY sidecars. KILLED (13/15). Decisive (the main checkout's 0 B -wal).
- Mb: the sidecar pre-check skipped on --dry-run. KILLED (14/15). Decisive.
- Mc: the breach comparison ignores the sidecar view. KILLED (14/15). Decisive (P2/P4 class).
- Md: the outputDir check drops the members of P. KILLED (14/15). Not decisive.

## Commands (bash; repo root Z:\FAC\TUBerlin\THESIS\TaxoArena; W = .claude/worktrees/e1-route2)

```
git diff --name-status main e1-route2; git merge-tree --write-tree main e1-route2; git diff --name-only e1-route2...main
git rev-parse {main,e1-route2}:tools/analysis/{embedder_arms,embedder_cross_flat}.py      # 2073d131 / 7868e858 x2
python -c "...ro.git_blob_lf('tools/analysis/embedder_arms.py')..."                       # main CRLF working files: same
git show e1-route2:<L1 toml> | sed -n '/^# ---- BASE ----$/,$p' | tail -n +2 | diff <(git show main:<af_clean_s42.toml>) -   # 2 lines
cd W; python tools/analysis/e1_route_launch.py --selftest                                 # 15/15
python scratchpad/probe.py <scratch tools/analysis>    # P1 rc2 B-E1-1 0 launches; P2/P3/P4 PIN BREACH; P5 rc0
python scratchpad/mut.py                               # Ma-Md KILLED
python (xml.etree over W/build/test-results/test/*.xml)  # 519 / 2 fail / 0 err / 0 skip; Manifest 4/4; EMD 8/8
grep -c embeddingCacheSourceSha256 W/build/classes/kotlin/main/taxonomy/dataset/EmbeddingCache*.class
grep -n 'systemProperty\|workingDir' W/build.gradle.kts                                  # L341-L350 forwards
python (count sidecars over the 8 members of P in main)                                  # 6: -wal 0 B, -shm 32768 B
powershell [IO.File]::Open(p,'Open','Read','None') on the 3 DBs + sidecars              # 7/7 FREE
python (git rev-parse HEAD:<f>; sha256 of LF and CRLF renderings)                        # pins above
```
