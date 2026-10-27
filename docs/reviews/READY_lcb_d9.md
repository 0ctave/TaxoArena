# READY review: LCB-D9-BYTE-INERTNESS (the procedure), 2026-09-25

Reviewer: adversarial-reviewer. Zero LLM calls. Nothing was built or run on the legs.

Record:
- Registration: docs/judge_v2_program.md L18662-L18872 (9981bb7).
- Leg B re-pinned to 6b9fc7c at L19241-L19271 (5bfce6c).
- The legs: A = a62c7e0ddb7a47f6ba691450c0cdd643cbdbe76d, B = 6b9fc7c278121868cb79477a9e12803b36830a3a.
- The arm: experiment_configs/topic_partition/ag_news_smoke_s42.toml, blob efd82bda.

## VERDICT: READY, as the procedure S0-S12 below with the three pinned helpers. Two conditions:

1. **The foreign CPU job must end first.** At 15:09, `arxout.py` was running: PID 51368 plus 4 multiprocessing workers, owner unknown. The window opens only when the process list shows no python.exe or java.exe other than this procedure's.
2. **The legs run after the LCB rerun window, which is DONE** (087e43d, recorded b42d68b). The LCB analysis of record runs AFTER D9.

## Pins

**Helper scripts** (session scratchpad `C:\Users\octav\AppData\Local\Temp\claude\Z--FAC-TUBerlin-THESIS-TaxoArena\7c10e5cb-d16b-4a0e-864a-f3a6151d835b\scratchpad\d9\`; LF; sha256):

| script | sha256 | role |
|---|---|---|
| d9_prep.py | 58b0ec87e9477876577e6b2033d797be5e5ead471c3b1080991615d12380a14e | V1 precondition; V2 copies and the declared pool schema |
| d9_leg_check.py | 9ee6d43d82813d93ae11442d03739947184a48f8c25e0e2d56381de080754a50 | V3 class counts, V4 [BOOT] line, V6 sanity and Gradle exit, V7 misses, V8 wall time |
| d9_compare.py | 8636b21591e70a76c1d1a8d52d28ba6a59cfe238db49b4720e99355a438138a8 | C1 over the 21 files, the file set (R2), and the reserved_pool* readout |

The operator re-hashes them before use (S0) and refuses on a mismatch.

**Code pins, leg B** (blob): TaxonomyConfig.kt 2825b12d, CorpusRegistry.kt 5b1bbb3a, CorpusSource.kt 817b1417, MMLUDatasetFetcher.kt a2a85c03. Checked by d9_prep V1: A..B differs in exactly these four files, and main has not moved them since A (count 0).

**Input baseline** (my read-only file hashes at 15:06-15:10, no SQLite open on main's files):

| main file | size | sha256 | note |
|---|---|---|---|
| ag_news_smoke_cache_v1.db | 1,622,016 | 7cf2082f... | = the registrar's baseline |
| ag_news_smoke_cache_v1.db-wal | 206,032 | 7eea2abd... | = the registrar's baseline |
| embeddings_cache.db | 804,462,592 | 52229e1ebfdda76e... | -wal 0 bytes; = the LCB rerun window's E: backup SHA256SUMS |

**Predicted copy hashes** (d9_prep executed by me into two scratch directories, then deleted):
- the checkpointed AG copy: **e3415684318c937c8e9073e1eb189c1f5a89006c0444794c20cf7b79ba527430** (1,748,992 bytes);
- the embeddings copy: 52229e1e...

## Checks I executed

| check | result | evidence |
|---|---|---|
| d9_prep V1 against the real repo | PASS | the 4-file diff; TOML efd82bda at A, at B and on main; main unmoved |
| d9_prep refuses a non-worktree leg | REFUSED | "git -C ... rev-parse HEAD failed" |
| d9_prep copy path on the real main files | V2 PASS | 3.7 s; both copies equal; main's size, mtime and sha256 unchanged, re-checked inside the script |
| d9_compare on two copies of the 2026-09-22 reference output | HELD | 0 differences, exit 0 |
| d9_compare, after mutating leg B | FAILED | 2 differences, exit 3 |
| d9_compare, after changing one reserved_pool row | FAILED | the pool row is detected, 3 differences |
| d9_leg_check on the 6b9fc7c classes, with a UTF-16 transcript naming its own root | PASS | counts 4 / 2 / 1 / 2 |
| d9_leg_check with the leg A bar and a foreign [BOOT] path | VOID | exit 1 |

The mutation of leg B in the d9_compare run:
- dropped fields changed only (run_manifest `duration_ms` and `commit`; iteration_metrics `wall_ms`; reserved_pool_meta `created_at`): these did NOT count;
- one byte appended to `validation/bridge_nodes.csv`: counted;
- one extra file under `judging/`: counted (reading R2).

## (b) Neither leg can write main's DBs of record. How this is guaranteed

1. **Every DB path the engine opens is relative to the JVM's working directory, which `bootRun` pins to `rootDir`** (build.gradle.kts L259-L260, identical at A and B). The worktree root is therefore the leg's own directory. The relative paths are:
   - `embeddings_cache.db` (EmbeddingCache.kt L41; ModelEvalLoader L47);
   - `snapshots.db` (TaxonomySnapshotManager L288);
   - `ratings.db` or `-Dranking.db.path`, forwarded to the forked JVM (build.gradle.kts L273);
   - the TOML's `corpusDbPath = "ag_news_smoke_cache_v1.db"`.
2. **No absolute path to the main checkout exists in the code or the committed config.** `git grep "TAXOARENA_DATA_ROOT\|Z:/\|FAC/TUBerlin\|user.home" 6b9fc7c -- src/main build.gradle.kts` = 0 hits. The committed config/application.yml carries no DB path. Main's uncommitted edits to it are LLM pacing only, and fresh worktrees do not see them.
3. **Main's files are touched only by d9_prep, and only by `shutil.copyfile`, a read.** The script refuses a non-empty main `-wal`/`-journal` on embeddings_cache.db. It re-checks size, mtime_ns and sha256 of all three main files after copying. Only the scratch COPY is ever opened by SQLite. Main's `-shm` is never copied.
4. **S12 re-verifies** main's embeddings_cache.db, snapshots.db and ag_news_smoke_cache_v1.db (+ -wal) against the baseline (V9).

Residual: a leg writes its OWN copies (queries table, reserved_pool rows, a -wal). That is by design; d9_compare reads them through a second copy.

## Findings on the registration (none blocks the run)

- **G1 (MEDIUM): V6's `exit_reason completed` is not evidence of success.**
  - `DiagnosticsBundle.close("completed")` sits in a `finally` (HeadlessBenchmarkRunner at 6b9fc7c, the try/finally ending L1031), so it runs whether or not the construction succeeded.
  - Executed evidence: the FAILED LCB build of 11:50 (exit 1) wrote `"exit_reason": "completed"` (incident outputDir_copy/seed_42/diagnostics/run_manifest.json).
  - d9_leg_check therefore ALSO requires `BUILD SUCCESSFUL` and no `BUILD FAILED` in the transcript, and the operator records the process exit code.
  - The registrar should record this as a reading of V6.
- **G2 (LOW): an AG copy made without its -wal would silently lose the 2026-09-22 reserved_pool writes.**
  - Main's AG -wal holds committed frames: the checkpointed copy grows from 1,622,016 to 1,748,992 bytes.
  - The registered copy of DB and -wal together, followed by a checkpoint of the COPY, is necessary, not just prudent.
- **G3 (LOW): the embedding-miss prediction P4 = 0 is supported.**
  - My read-only immutable read of main's embeddings_cache.db (-wal 0) finds all 2,000 AG texts as keys.
  - This was a review read, outside the instrument, which reads only copies.
  - The 2026-09-22 run itself missed 1,400 (they were computed then).
- **G4 (LOW): run the two legs from ONE shell session with an identical environment.**
  - Neither leg needs `.env`: lcb-build-2, a fresh worktree without `.env`, built exit 0.
  - S1 prints the names of the AZURE_*, OLLAMA* and TAXOARENA_* variables once.
- **G5 (LOW): removing a worktree can fail on Windows path length** ("Filename too long", my own removal of rv-mut-lcb). S11 gives the fallback.

## The operator procedure

Run from PowerShell in the main checkout unless stated. Set `$SP` to the scratchpad d9 directory and `$ST` to a NEW stage directory, e.g. `$SP\run_20260925`, which must not exist.

**S0. Pins and hygiene.**
- `Get-FileHash $SP\d9_*.py -Algorithm SHA256`: must equal the three pins above.
- `Get-CimInstance Win32_Process -Filter "Name='java.exe' or Name='python.exe'"` must be empty. If not, WAIT; never kill.
- Free RAM must be at least 12 GB.
- Print main's L6 pins in both views (embeddings / queries row sha, as the LCB windows did).

**S1. Two throw-away worktrees on short paths.** Do not use or touch lcb-build-2 or agent-adb18465164aaf122.
- `git worktree add --detach .claude/worktrees/d9-legA a62c7e0ddb7a47f6ba691450c0cdd643cbdbe76d`
- `git worktree add --detach .claude/worktrees/d9-legB 6b9fc7c278121868cb79477a9e12803b36830a3a`
- Print the env variable names (G4). Run nothing inside either worktree before S3 (the lcb-build-2 lesson: a Gradle test run creates root DBs).

**S2. Copies and precondition.**
- `python $SP\d9_prep.py Z:\FAC\TUBerlin\THESIS\TaxoArena Z:\FAC\TUBerlin\THESIS\TaxoArena\.claude\worktrees\d9-legA Z:\FAC\TUBerlin\THESIS\TaxoArena\.claude\worktrees\d9-legB $ST`
- It must end `[V2] PASS`. It refuses otherwise, and the run stops.
- Expected: AG copy e3415684..., embeddings copy 52229e1e...

**S3. Leg A.**
- `Set-Location .claude\worktrees\d9-legA; .\gradlew.bat bootRun --console=plain --offline --no-build-cache "-Dranking.db.path=ratings_d9_A.db" --args="--config experiment_configs/topic_partition/ag_news_smoke_s42.toml" *> $ST\legA_bootrun.log; "EXIT $LASTEXITCODE" | Out-File -Append $ST\legA_exit.txt`
- Then `python $SP\d9_leg_check.py A <legA root> $ST\legA_bootrun.log $ST`. It must print `ALL VALIDITY CHECKS PASS`.
- Leg A's class counts must be 0 / 0 / 0 / 0, and the exit must be 0.

**S4. Leg B.** The same as S3, from d9-legB, with `ratings_d9_B.db`, `legB_*` and the letter B. Class counts must be at least 3 / 1 / 1 / 1; predicted 4 / 2 / 1 / 2.

**S5. C1, BEFORE any probe.**
- `python $SP\d9_compare.py <legA root> <legB root> $ST`
- It writes `$ST\d9_compare.txt`. Exit 0 = C1 HELD; exit 3 = C1 FAILED, an outcome and not a crash. The [V7] line must read EQUAL.

**S6. The R3 probe on leg B.**
- Copy the arm TOML to `$SP\probe_lcb.toml`, changing ONLY `datasetType = "LIVECODEBENCH"` and `outputDir = "experiment_results/d9_probe_B"`. Diff the two files: exactly 2 lines.
- From d9-legB: `.\gradlew.bat bootRun --console=plain --offline "-Dranking.db.path=ratings_d9_probeB.db" --args="--config $SP\probe_lcb.toml" *> $ST\probeB.log; "EXIT $LASTEXITCODE" | Out-File -Append $ST\probeB_exit.txt`
- PASS = exit != 0, AND a line CONTAINING `[LCB] refusing to build LIVECODEBENCH` (reading R1; expected: the warm-cache refusal, since the leg's embeddings copy holds 39,631 rows), AND no `No enum constant`.
- Check: `python -c "import sys;r=open(sys.argv[1],'rb').read();t=r.decode('utf-16') if r[:2]==bytes([255,254]) else r.decode('utf-8','replace');print('refusal', '[LCB] refusing to build LIVECODEBENCH' in t, 'no-enum', 'No enum constant' in t)" $ST\probeB.log`

**S7. Optional negative control.** The same probe from d9-legA (`ratings_d9_probeA.db`, `$ST\probeA.log`). The expected line CONTAINS `No enum constant` and names LIVECODEBENCH.

**S8. Discriminator record.** Concatenate the S3 and S4 leg-check output (`$ST\d9_disc.txt`, appended by the helper) and the S6/S7 probe lines into `$ST\d9_disc.txt`.

**S9. Stop the JVMs.** `.\gradlew.bat --stop` from d9-legB. The process list must hold no java.exe.

**S10. Save the evidence.** Copy to `$ST\evidence_A\` and `$ST\evidence_B\`:
- each leg's outputDir;
- its headless_run.log;
- its bootRun transcript;
- `git -C <leg> status --short`, which lists the files the run wrote.
Hash them into `$ST\SHA256SUMS`.

**S11. Remove both worktrees.**
- `git worktree remove --force .claude/worktrees/d9-legA` (then legB).
- If that fails ("Filename too long"): from Git bash, `rm -rf` the directory, then `git worktree prune`.
- `git worktree list` must name neither.

**S12. V9.**
- Main's embeddings_cache.db must have size 804,462,592, the baseline mtime, and sha256 52229e1e..., with -wal 0.
- Main's snapshots.db: size and mtime unchanged.
- Main's ag_news_smoke_cache_v1.db and -wal: equal to the INPUT BASELINE in size, mtime and sha256.
- Main's L6 pins in both views are equal to S0.
- Nothing from the legs is committed except the registrar's readout. `$ST` is handed to the adversarial-reviewer for the independent recomputation of C1.

**Wall time.** About 15-20 min, of which the two cold compiles and builds take about 8-10 min.

## Rule-7 conditions

- **One window** for S2-S9. Every rule-7 condition applies, with the pool probe scoped to this window's objects:
  - W1: main's embeddings_cache.db and ag_news_smoke_cache_v1.db must be FREE for an exclusive open at S0 and S12. The legs' copies are private.
  - At least 12 GB of free RAM.
  - Admitted PIDs printed.
  - No git write to src/.
- **Nothing else CPU-heavy.** No other java or python job, and the current `arxout.py` job must have ended. Following L4.1b, a foreign process makes the next step WAIT and is recorded, never killed. A foreign process that opened main's embeddings_cache.db or ag_news_smoke_cache_v1.db during S2 or S12 is a failed precondition: re-run S2 into a new `$ST`.
- **Ordering of record:** K46 done → LCB rerun window done (087e43d) → **D9 (this)** → the LCB analysis of record → the post-run reviews → merges behind F5.
- The LCB analysis may not start before S12 ends, because it reads lcb-build-2's caches and must not overlap a long CPU run.
