# RERUN READY: the LCB-STAGE0 build window after the 2026-09-25 11:50 incident; the guard fix at 6b9fc7c

Reviewer: adversarial-reviewer. Zero calls; no outcome read. Branch worktree-agent-adb18465164aaf122, NOT MERGED.

Objects:
- the incident, recorded at b3e8c94 (`experiment_results/lcb_stage0/window/`);
- the fix, 6b9fc7c278121868cb79477a9e12803b36830a3a (parent b3e8c94).

## VERDICT: READY for the rerun of the build window, under steps R1-R11 below

## Why my delta READY (1ceafae) did not catch this, for the record

- I checked the guard as a unit: one fetch per fetcher in a fresh process (the Gradle test), plus javap.
- I noted that it runs "inside fetchLiveCodeBench, after Spring start-up", but I did NOT walk the runner's call sites for a SECOND fetch in the same JVM. Nor did I read the `catch (_: Throwable) { null }` at HeadlessBenchmarkRunner L918-L922, which turned the second refusal into a null. That null reached the non-hoisted fetch at L1344, which failed loudly.
- My statement "It passes on the build worktree as it stands" was true only for the first call.
- The lesson I apply below: a guard placed on a code path is reviewed against EVERY invocation of that path in one process, by call-site count, not only against its unit test.

## 1. The fix: correct and complete for this toml

### Call-site walk, done by me

`grep -n "fetchDataset(" src/main/kotlin/taxonomy/runner/HeadlessBenchmarkRunner.kt` finds 4 sites:

| site | purpose | under the LCB toml |
|---|---|---|
| L521 | the construction fetch, under `runPipeline` | the first check (cold) |
| L681 | only with `regenerateSplit && !runPipeline` | NOT reached |
| L918 | the trickle's hoisted fetch, under `runTrickle` | same process, same dir: passes ("same process, already checked") |
| L1344 | only when `hoistedFullByDomain` is null | NOT reached now |

- The baseline trickles (L942 / L952 / L962) and union routing (`unionSnapshots` empty) reuse the hoisted map, and are off under this toml anyway (runBaselines false).
- L516-L519: `downloadDataset()` (which calls fetchDataset) runs only if `isDatasetDownloaded()` is false. That is `getDbCount(livecodebench) > 0` (MMLUDatasetFetcher L205-L215), which is true on the construction DB (741 rows), so it is not reached.
- Other fetchDataset callers in src/main: E2BridgeRunner, E2FusionRunner, TuiGateway, MMLUCacheRunner. None runs under this toml.
- The site null (SeparationNullBySizeTest) constructs fetchers only as the splitter argument and calls no fetchDataset (`grep` = 0). It never reaches the guard, which is why L5 still protects it.

### The fix itself

- `lcbWorkDirGuard` (MMLUDatasetFetcher.kt a2a85c03):
  - refuses a `.git` directory on EVERY call;
  - runs the cold-cache check on the FIRST call of the process;
  - records the canonical (working dir, cache path) pair in `LcbWorkDirGuardState`;
  - on later calls, asserts the same pair and returns.
- A refused check records nothing.
- javap on the build worktree's compiled classes (MMLUDatasetFetcher.class, compiled 11:55:58): both constructors and `static {}` hold **0** references to LcbWorkDirGuardState, lcbWorkDir and user.dir.

### Tests (my own runs, in a throw-away worktree of 6b9fc7c; `--no-build-cache`, compileKotlin executed)

- **Targeted Gradle: 45/45, 0 failures.** Same 9 classes as before; LiveCodeBenchDatasetTypeTest now has 8 tests.
- **My mutant, a different one from the builder's "warm check every call":** record `LcbWorkDirGuardState.checked` BEFORE the warm check. Under it, a refused first check would still arm the "already checked" path, and a second fetch in the same process would pass a warm cache.
  - KILLED by exactly one test: "a fresh process with a warm cache is refused()". 8 tests, 1 failed. The failing test asserts that a refused check records nothing.
- Both throw-away worktrees were removed, and `git worktree list` shows neither.

### Residual (LOW, not gating)

- The `catch (_: Throwable) { null }` at L909 and L922 stays. For LCB it can now only swallow a non-guard failure of the hoisted fetch, and L1344 would then re-fetch and fail loudly. Disclose it; do not change it inside D9's pinned bytes.

## 2. The rerun procedure

- **R1. Stop the idle JVMs first.** Two are alive at 12:04:
  - PID 51100, a Gradle daemon started 11:48:46 (the window's);
  - PID 5488, a Kotlin compile daemon started 11:54:34.
  - Run `.\gradlew.bat --stop` from the old build worktree. Then confirm that the process list holds no java.exe (L4.1).
- **R2. Keep the aborted object; do not delete or open it read-write.**
  - The LCB construction DB `Z:\FAC\TUBerlin\THESIS\TaxoArena_data\lcb\lcb_v6_construction_2a94f2dbf91b4371.db` is now:
    - file sha256 358192eece73f5796b79...;
    - with a NON-EMPTY `-wal` of 152,472 bytes, sha256 bb8e70034e844725...;
    - plus a `-shm`.
  - Print the full sha256 of all three files.
  - Rename ALL THREE together, without any SQLite open, to `lcb_v6_construction_2a94f2dbf91b4371.aborted_build_20260925_1150.db`, with the matching `-wal` and `-shm` names.
  - Copy the three renamed files to `E:\TaxoArena_backup_2026-09-25\lcb_window_incident\` and append their shas to that SHA256SUMS.
  - It is never checkpointed. The rename keeps it byte-identical as evidence.
- **R3. Restore the ingest-time construction DB. Do NOT re-create it.**
  - Copy `E:\TaxoArena_backup_2026-09-25\lcb\lcb_v6_construction_2a94f2dbf91b4371.db` to the original path.
  - Require all three:
    - its sha256 = **fbd9613996afef3e62b768594d80f20ffa2c942d31403c665b31bc2818b80dc9** (the backup's SHA256SUMS and the committed construction_manifest.json "sha256"; I recomputed the backup file: fbd96139...);
    - no `-wal` or `-journal` beside it;
    - its `livecodebench` table-sha = 2a94f2dbf91b4371... (the manifest).
  - Why restore:
    - `ingest --construction` is write-once. The DB name, `lcb_gate_ids.json`, the filled toml and construction_manifest.json all exist and are committed, so a re-run refuses by design.
    - The restored bytes are the exact object the committed manifest pins.
    - The build writes `reserved_pool` rows into this DB (P1). A second build on the written copy would start from a state the first run never saw.
    - Pin the restored DB as above, before the build. After the build, record its new sha and table-shas (the rerun's own written state), as the first window did.
- **R4. A FRESH worktree on a SHORT path.** My own long-path `git worktree add` under the scratchpad failed with "Could not reset index file". From the main checkout:
  - `git worktree add --detach .claude/worktrees/lcb-build-2 6b9fc7c278121868cb79477a9e12803b36830a3a`
  - Then check each of these:
    - `git -C .claude/worktrees/lcb-build-2 rev-parse HEAD` = 6b9fc7c...;
    - `test -f .claude/worktrees/lcb-build-2/.git` (a file);
    - `ls .claude/worktrees/lcb-build-2/embeddings_cache.db* snapshots.db*` finds nothing. The only root DB is the tracked `snapshots_frozen.db`; `git ls-files | grep -cx "embeddings_cache.db\|snapshots.db"` = 0.
    - `git -C .claude/worktrees/lcb-build-2 status --short | wc -l` = 0.
- **R5. Nothing may run inside lcb-build-2 before the build: no Gradle `test`, no selftest, no dry-run.**
  - Executed: a targeted Gradle test run in a fresh worktree of 6b9fc7c CREATED `embeddings_cache.db` (+ -wal/-shm), `ratings.db`, `mmlu_pro_dataset_cache_v2.db` and `snapshots_test.db` at the worktree root. That is exactly how the first build worktree came to hold a pre-existing cache.
  - Run the build via bootRun only. The build compiles from source in the fresh worktree.
- **R6. Pre-flight.** Run L5 unchanged in lcb-build-2, then L6 (main-cache pins in both views) and L7 (embed check, from lcb-build-2).
- **R7. Build from lcb-build-2** with the committed filled toml `experiment_configs/lcb_stage0/lcb_af_bareq512_s42.toml` (its `corpusDbPath` is the absolute restored DB) and its own `-Dranking.db.path`. The build log must show all of:
  - `[LCB] working-dir guard passed: '...\lcb-build-2' ... (first check of this process)`;
  - `[LCB] fetched 741` (= n_train 630 + n_gate 111);
  - `[LCB] working-dir guard: same process, already checked` at the trickle;
  - 0 held-out members;
  - the MAIN trickle completing;
  - exit 0.
  - A guard refusal, or any exit != 0 before the snapshot is saved, is a FAILED PRECONDITION: stop and report. It is not the arm's result, and there is no third run without a new ruling.
  - A build that completes is the arm's result (L9).
- **R8. After the build.**
  - Checkpoint lcb-build-2's `embeddings_cache.db` and `snapshots.db` (a read-write open and close) before any reader (L8).
  - Pool_guard on the GATE export, as registered.
  - Run the site null FROM lcb-build-2 with the registered command. It writes to lcb-build-2's `experiment_results/lcb_stage0/`.
- **R9. Pins, then the analysis.**
  - Record the `--pins` JSON: dag_snapshots.jsonl, snapshots.db, the checkpointed embeddings_cache.db and the site-null CSV, all from lcb-build-2, plus the rerun's snapshot id.
  - `analysis.py --build-dir .claude/worktrees/lcb-build-2 --run-dir .claude/worktrees/lcb-build-2/experiment_results/lcb_stage0/lcb_af_bareq512_s42/seed_42 --snapshot-id <rerun id> --site-null <lcb-build-2 csv> --pins <json>`.
- **R10. The aborted tree is NOT admissible.**
  - It is snapshot 20260925_115023_Headless_Run_Auto_ge (11 nodes, dag_snapshots sha256 35a92b94...). It sits in the old worktree's untracked outputDir, in the incident copy committed at b3e8c94, and in the E: copy. It is kept as evidence and never deleted.
  - It is never an input of the analysis, never compared with the rerun tree to choose anything, and never used for any decision.
  - The outcome carries a DISCLOSURES line:
    - the aborted window at 11:48-11:50, its snapshot id and sha;
    - the cause (the guard re-ran at the trickle's second fetch; the refusal was swallowed at L922 and surfaced at L1344);
    - that the construction DB was restored to fbd96139 from the L3 backup;
    - that the rerun used a fresh worktree at 6b9fc7c.
  - It must also say that the TRAIN texts were embedded twice, locally, by the same Ollama model (no call cost), and that only the rerun's cache is read.
  - The old build worktree agent-adb18465164aaf122 is left as it is: warm cache (630 rows), untracked outputDir. It is not reused and not cleaned.
- **R11. Scope.** Nothing in R1-R10 touches main's caches, src/ or the programme. The only git writes are the registrar's records and this review.

## 3. The D9 pins move to 6b9fc7c: CONFIRMED

- `git diff --name-only a62c7e0 6b9fc7c -- src/main build.gradle.kts settings.gradle.kts gradle.properties gradle/ config/` lists exactly the 4 files.
- Main has not moved these paths since a62c7e0 (count 0).

Pins (git blob / sha256 of the LF text / sha256 of the CRLF text, first 16 hex; the worktree files are CRLF):

| file | blob | lf16 | crlf16 |
|---|---|---|---|
| TaxonomyConfig.kt | 2825b12d | 61f67a71d6ca9cd3 | 1860445fcb273875 |
| CorpusRegistry.kt | 5b1bbb3a | f8f39d7aca0b4666 | 6f71693dda26d859 |
| CorpusSource.kt | 817b1417 | 00af04220803814c | af3dde076e7df6bf |
| **MMLUDatasetFetcher.kt** | **a2a85c03** | **7a408454036d3886** | **728648dbb035e98f** |
| Test file: LiveCodeBenchDatasetTypeTest.kt | c53115cd | ad91e165d79bc7e2 | 7de60afaeb0a91c5 |

- D9 leg B = 6b9fc7c. The 4497373 pins of my delta section are superseded for MMLUDatasetFetcher.kt only.
- Discriminator D9-R1 gains one identifier, **LcbWorkDirGuardState ≥ 1**.
- Build-worktree counts at 6b9fc7c:

| identifier | count |
|---|---|
| LIVECODEBENCH | 4 |
| fetchLiveCodeBench | 2 |
| lcbWorkDirGuard | 1 |
| LcbWorkDirGuardState | 2 |

- Leg A must read 0 for all four.
- D9 must run on these exact bytes; any later src/main byte change voids it.

## 4. L4.1-L4.7 for the rerun: unchanged, plus two additions

- **L4.1a (JVM hygiene).** At window open, after R1, the process list holds no java.exe. A Gradle or Kotlin daemon left by an earlier session counts as a foreign JVM, even when idle.
- **L4.1b (no foreign selftest or dry-run during the window).**
  - Before the window opens, the orchestrator announces a CPU and tool freeze to every agent lane. Suspended for the window: selftest, --dry-run, Gradle and pool_guard runs, except those of this window.
  - The run-operator prints the process list (python.exe / java.exe with command lines) before each leg.
  - A foreign python or java process other than the K46 poster makes the next leg WAIT until it exits. It is never killed by the operator.
  - An overlap that happened mid-leg is recorded in the window log with its PID and wall time. It is a disclosure, not a failed precondition, unless it opened a DB of this window. The first window's foreign selftest is disclosed the same way.

L4.2-L4.7 stand as written. L5-L10 stand, with R4-R9 above applying them to lcb-build-2.

## Commands (this ruling)

| check | command |
|---|---|
| fix diff | `git diff 4497373 6b9fc7c -- src/main` |
| call sites | `grep -n "fetchDataset(" .../HeadlessBenchmarkRunner.kt`; `sed -n` L505-L530, L670-L690, L895-L930, L1336-L1352 |
| compiled-class checks | `javap -c -p taxonomy.dataset.MMLUDatasetFetcher`; `grep -rlaF <id> build/classes/kotlin/main \| wc -l` |
| my mutant | throw-away worktree `.claude/worktrees/rv-mut-lcb` at 6b9fc7c, `.\gradlew.bat test --offline --no-build-cache --tests taxonomy.dataset.LiveCodeBenchDatasetTypeTest` (8 tests, 1 failed: the named test) |
| baseline | throw-away `rv-base-lcb`, the 9 targeted classes: 45 / 0 / 0; it created the root caches noted in R5 |
| hashes | `sha256sum` of the E: backup (fbd96139...), the written DB (358192ee...) and its -wal (bb8e7003...) |
| processes | `Get-CimInstance Win32_Process` |

---

# L4 RULING: the LCB-STAGE0 build window beside the PILOT-K46 run of record, 2026-09-25

Reviewer: adversarial-reviewer. Zero calls; read-only. This ruling was requested on the author's instruction "do both, start the LCB build now and register parallel posting".

## VERDICT: SAFE, under the replacement L4 below

## Facts I checked myself

Process list, read with `Get-CimInstance Win32_Process` at about 11:36:

| PID | what | started | working set |
|---|---|---|---|
| 53840 | the K46 poster: ONE python.exe, `archv2_pilot_k46.py --run --go --store ...\pilot_k46_verdicts_run2.db ...` | 07:15:04 | 130 MB |
| 41172 | Ollama | - | 65 MB |
| 53176 | a scratchpad `xver2.py`, reading a temp repo copy | - | - |

- No java.exe was running.
- Free RAM: 27.3 GB of 63.1 GB.
- The poster's store and invocations DB were last written at 11:35:42, so it is live.

## (a) Shared resources

None are shared in a way that is unsafe for either record.

**What the pilot reads and writes:**
- the SPLIT-2 eval_view;
- the pool pv2_41dbd3dbcd399df0;
- main's `experiment_results/day_calls_2026-09-25.json`;
- its run2 store, its journal and its invocations DB under main's `experiment_results/archv2/pilot_k46/`.

**What the LCB window touches:**
- the construction DB under TAXOARENA_LCB_ROOT, which is outside the repo;
- the build worktree's own cache DBs, which are relative to that worktree's root: embeddings_cache.db, snapshots.db and the ratings DB set by `-Dranking.db.path`;
- the build worktree's `experiment_results/lcb_stage0/**`, which receives the outputDir and the site-null CSV;
- the gate-id export and the config it reads.

None of these is a path the pilot opens. Checks by path:

- **pool_guard.**
  - Every read goes through `mode=ro&immutable=1` (L150-L161), and the tool writes nothing.
  - With `--pool <id> --db <LCB construction db> --id-file <export>` it opens only the named DB.
  - It reads `experiment_configs/reserved_pools.json` read-only. The LCB pool has no entry there, by registration H5.
  - It opens snapshots.db only on `--export-snapshot`, which the window does not use.
  - It touches no reserved-pool state of main and no view of SPLIT-2.
- **Ollama.** The pilot's judge is grok via the remote API, and it makes no Ollama call. Only the LCB embeddings use the local Ollama server.
- **Day ledger.** `grep -rn "day_calls" src/main/kotlin` = 0 hits, and embed_context_check.py writes no ledger. The window adds no ledger row and makes no judge call, so the 8,000 ceiling and the day cap are untouched.
- **Git.** The window writes no file under main's src/ or experiment_results/. The F5 freeze of judge_v2 on main is not touched.

## (b) Rule 7's intent

- **The pilot is not a long CPU run** for this purpose. It posts sequentially, is API-bound, and has a 130 MB working set.
- **The pilot does not read any pool that the LCB window uses.** Its pool pv2_41db... and the LCB GATE pool are disjoint objects in disjoint DBs.
- **The LCB window is not a reader of the pilot's pool.**

The residual risks are machine-level, not record-level:

1. **Memory pressure or a crash.** Record: the PC crash of 2026-09-24; the site-null heap incident. The pilot's store is journal-backed. The K1 hard-kill probe in the K46 READY found journal = ledger with 1 orphan, so a crash costs time, not the record.
2. **Disk contention during the E: backup.** E: is the same physical disk. The cost is latency only.
3. **The W1 exclusive-open probe as written ("every pool DB FREE")** would report the pilot's eval_view as held. That is not a breach, but it must be re-scoped. See L4.2 below.

## (c) REPLACEMENT TEXT FOR L4

L4 as recorded is SUPERSEDED. Replacement:

> L4. The rule-7 build window of LCB-STAGE0 MAY run CONCURRENTLY with the ARCH-V2-PILOT-K46 run of record (the single poster process, PID printed at window open) and with no other long CPU process, provided:
>
> - (L4.1) at window open the process list shows no java.exe, no Gradle daemon of another worktree, no construction, no SPLIT-DRAW, no site null and no induction or selftest run other than this window's; the pilot poster is the only admitted foreign process, and its PID and command line are printed beside every leg;
> - (L4.2) the W1 exclusive-open probe is taken over the objects THIS window touches: the LCB construction DB, the build worktree's embeddings_cache.db and snapshots.db, and main's embeddings_cache.db and snapshots.db (L6). Every one of them must be FREE. The pilot's SPLIT-2 eval_view, pool DB, run2 store and day ledger are EXCLUDED from the probe, and they must NOT be opened by any step of the window;
> - (L4.3) at least 12 GB of free RAM before each leg (embed check, build, site null), printed with the site null's [SITENULL-HEAP] estimate. A leg that would start below 12 GB waits; it never starts;
> - (L4.4) the window does not start while the pilot is in its pilot-guard, analysis (--analyze) or outcome-writing step. It opens only while the poster is in steady posting: its store mtime advanced within the last 60 s at window open;
> - (L4.5) poster health is recorded, not traded: the poster's committed-verdict count is printed at window open and after each leg. If the poster process EXITS during the window, or the store mtime stalls for more than 10 minutes, the run-operator stops the window at the next leg boundary (a leg in progress runs to completion; a site null is never killed mid-write) and reports to the orchestrator. Neither event is an outcome of either test;
> - (L4.6) the E: backup (L3 and the window's backup step) runs BEFORE the build leg and never overlaps the site null;
> - (L4.7) L5, L6, L7, L8 (with the guard line), L9 and L10 stand unchanged. In particular the L5 shell pre-flight and the L6 main-cache pins, in both read modes before and after the window, are the protection that the main embeddings_cache.db is never written. Nothing in this concurrency relaxes them.

No latency trigger is registered. The poster's calls per minute do not enter any K46 criterion: calls are sequential, and each verdict is independent of wall time. A slowdown therefore cannot change either record, and pausing the window on a throughput drop would guard nothing. The stall and exit conditions in L4.5 cover the only failure that matters: a dead poster.

## What this ruling does NOT show

- That the pilot's own guards or outcome are valid. That is its own post-run review.
- That the machine will not crash. L4.3 bounds the risk, and the journal bounds the cost.
- Anything about D9's legs. Those are a separate window after this one, per the D9 ruling.

---

# DELTA READY: LCB-STAGE0-INTERACTION fixes at 4497373 (parent ed948d6), 2026-09-25

Reviewer: adversarial-reviewer. Zero LLM calls. No LCB outcome value was read. Not run on real data: the draw, the ingest, the build, the analysis. My only real-data read was a key count, already reported in the first review; nothing new was read in this delta. Scripts ran on a `git archive 4497373` copy in the session scratchpad (`rv_lcb/base2`), with `python -B`. All 10 package files have blobs equal to 4497373. The build worktree stayed clean (`git status --short | wc -l` = 0). Branch worktree-agent-adb18465164aaf122, NOT MERGED.

## VERDICT

| # | object | verdict |
|---|---|---|
| (1) | the analysis of record (`analysis.py`, after the window, under L10 as amended below) | **READY**. No BLOCKER or HIGH remains. Three LOW test gaps remain (E1-E3); none changes a number or a verdict. |
| (2) | the rule-7 BUILD WINDOW on the new Kotlin blob (MMLUDatasetFetcher.kt 70eedfdf, with the `lcbWorkDirGuard`) | **READY**, with L5 UNCHANGED and one line added to L8 (below). |
| (3) | the four src/main blobs at 4497373 as the pins of the D9 byte-inertness legs (A = a62c7e0, B = 4497373) | **CONFIRMED**. |

## Pins (4497373; LF of record; CRLF shown where the worktree file is CRLF)

**The four src/main files (the D9 pins).** `git diff --name-only a62c7e0 4497373 -- src/main build.gradle.kts settings.gradle.kts gradle.properties gradle/ config/` lists exactly these four:

| file | blob | sha256-lf16 | sha256-crlf16 |
|---|---|---|---|
| TaxonomyConfig.kt | 2825b12d | 61f67a71d6ca9cd3 | 1860445fcb273875 |
| CorpusRegistry.kt | 5b1bbb3a | f8f39d7aca0b4666 | 6f71693dda26d859 |
| CorpusSource.kt | 817b1417 | 00af04220803814c | af3dde076e7df6bf |
| MMLUDatasetFetcher.kt | 70eedfdf | 14cfc139d63030d9 | 3e511013801eba99 |

**Changed Python files and test** (`git diff --stat ed948d6 4497373` = 6 files):

| file | blob | sha256-lf16 |
|---|---|---|
| analysis.py | e3144692 | 404d6a957771b30c |
| stats.py | 813d2d6d | 59914c65e5d1c352 |
| selftest.py | 0f4ba49b | 2f9e78e442e454a5 |
| fixture.py | 10437edb | a27f797caad7caf4 |
| LiveCodeBenchDatasetTypeTest.kt | e72de809 | e95d8a7d5e5c4d05 |

Unchanged since ed948d6: draw.py, ingest.py, common.py, download.py, embed_context_check.py, `__init__.py`, the template, and the manifests (pins as in the review below).

## Per-claim table

| # | builder's claim | result | command / evidence | got vs claimed | sev |
|---|---|---|---|---|---|
| T1 | selftest 321 checks / 43 refusals under python and -O | CONFIRMED | `python -B selftest.py`; `python -B -O selftest.py` (prints "python -O: True") | 321 / 43, SELFTEST OK in both | - |
| T2 | ruling cross-check exact on 10 worlds per family | CONFIRMED | `selftest.py --quick --ruling-crosscheck <scratchpad>/lcb_s0/rule --xc-worlds 10` | 10/10 on every field in base / twins / slope / slope2. The det floor and the `safe_after` parameter leave the ruling's path unchanged | - |
| T3 | targeted Gradle 42/42 | CONFIRMED, executed | `.\gradlew.bat test --offline --rerun --tests <9 classes>`. My first run was entirely UP-TO-DATE; the `--rerun` re-executed the tests (XML timestamps 06:28Z) | 42 tests, 0 failures, 0 errors; LiveCodeBenchDatasetTypeTest 5 (4 + the D7 guard test); `:compileKotlin UP-TO-DATE`, so the classes are those of the current sources | - |
| T4 | all 32 mutants killed by a named check | PARTLY | `rv_lcb/mutants2.py`: my 19 (X-support-fit-true re-applied to the new call) plus 15 of my own on D1-D8. I did NOT re-run the builder's 13 | my 19: **19/19 KILLED** by named checks, including the 5 former survivors. My 15: **12 KILLED, 3 SURVIVED** (E1-E3). D1-unknown-ignored was applied on a unique context string, since the first string matched 2 sites | LOW |
| D1 | every leaf queryId resolved; refuse on unresolved ids, a count mismatch, or 0 members | CONFIRMED | analysis.py L370-L391. Selftest refusals "resolve to no TRAIN text" (mismatched id space) and "needs every member resolved and > 0" (empty tree). Mutants D1-count-ignored and D1-unknown-ignored KILLED. `rv_lcb/heldprobe.py` puts a GATE text in a leaf and gets "1 GATE / EVAL texts are members of a leaf (TRAIN-ONLY violated)"; an unknown id gets "resolve to no TRAIN text" | - | - |
| D2 | tree and input pins; site-null snapshot_id match; `--pins`; re-hash before the write | CONFIRMED | load_tree / load_inputs pins; `read_site_null` refuses any other snapshot_id; `check_expected_pins`; `main()` re-hashes the build inputs and the site-null CSV before `write_outcome`. Mutants D2-sitenull-id-unchecked, D2-pins-ignored and D2-tree-pin-unprinted KILLED | the pre-write re-hash in `main()` is not executed by any test: nothing changes during a dry run. It is inert-when-equal code; noted, not a defect | - |
| D3 | FIT PATH for all 6 fits, with the reference path beside | CONFIRMED | `fit_path` covers primary, Delta-D, S1, S2, S3 and GATE. Selftest: six objects, 3 of 6 engaged in the fixture (my first review's count), reference printed. Mutants D3-no-reference and D3-GATE-path-dropped KILLED. The builder's statement is corrected in stats.py L246 | - | - |
| D4 | single-contrast MDE and its status printed | CONFIRMED | analysis.py: `v_n10` = the median over two-n=10 pairs, `mde80_single` at the measured DEFF and informative n, SCOREABLE iff K <= 4 and < 10pp. Mutants D4-recomputed-literal and D4-status-bar-12pp KILLED. D4-status-K-ignored SURVIVED (E2) | - | LOW |
| D5 | the new tests | CONFIRMED | B4-X2-own and B4-RREP-own now KILLED ("observed X2 at the family-majority labelling", "R-REP's GATE estimates at the family-majority labelling") | - | - |
| D6 | the new tests | PARTLY | X-support-fit-true KILLED ("a non-converged primary fit reads UNDETERMINED (STOP)"). X-S2-empty KILLED. D6-S2-temp-ignored SURVIVED (E3) | - | LOW |
| D7 | det floor, stop field, bound-stop test; engine guard | CONFIRMED | B1-bound-dropped now KILLED ("stop tol, a 47.50"). D7-det-floor-removed KILLED ("stop non-finite, a nan"). D7-stop-bound-mislabelled KILLED. Gradle: the guard test refuses a `.git` directory and a warm `queries` table, and passes a cold worktree | javap on the compiled MMLUDatasetFetcher: the constructors reference `lcbWorkDir` 0 times and `user.dir` 0 times. `user.dir` appears only in `fetchLiveCodeBench$suspendImpl` (1). The field has no initialiser code. Equal to the builder's statement | - |
| D8 | DISCLOSURES block | CONFIRMED | render(): the EVAL-at-ingest read, the one-shot limit, SAFE_AFTER and the (vii) drops. Mutant D8-disclosures-dropped KILLED | - | - |

## Ruling: support block fed the recomputation-done status (D4 deviation), ACCEPTED

The registered support condition reads "measured family DEFF <= 1.3, **or the recomputation done**" (L17816; section 5, "If the measured family DEFF > 1.3, every SE and MDE below is recomputed BEFORE any verdict is read"). It is a condition on reading the verdict: the verdict may only be read after the SEs and MDEs are restated at the measured DEFF. It is NOT a condition that the single-contrast class stay SCOREABLE. Section 5 keeps G1 and G2 SCOREABLE as aggregate tests whatever that class's status is.

Feeding the single-contrast status to the support block would turn a GO or STOP into UNDETERMINED whenever a DESCRIPTIVE-ONLY contrast lost its class. That is an unregistered criterion (C-7). The builder's reading is the registered one.

What this acceptance does and does not settle:
- The builder's `recomputed` is True whenever the two MDEs are finite. The support item therefore certifies the recomputation, a presence check, and not a cell. That is acceptable ONLY because the numbers it certifies are printed beside it: RECOMPUTATION line, MDE80 single contrast and median pair, status. The spy test proves the item is wired to the computed value and is not a literal (mutant D4-recomputed-literal KILLED).
- CONDITION for the outcome. When the status reads DESCRIPTIVE-ONLY, the outcome text may make no single-contrast claim. render() currently makes none, since the reversal list is a descriptive list. The post-run review checks this in the outcome text.

## (2) The build window on the new Kotlin: READY, L5 UNCHANGED

- The guard is in the LCB branch only (`fetchLiveCodeBench` L1070). It is inert on existing arms: the field has no initialiser code (javap above), and the D9 byte run is the proof of record.
- It passes on the build worktree as it stands:
  - `.git` is a file;
  - its embeddings_cache.db has 0 rows in `embeddings` and `queries`, read through a non-immutable read-only open that includes the 37,112-byte -wal.
- **The guard does NOT replace L5.** It runs inside `fetchLiveCodeBench`, AFTER Spring start-up, where EmbeddingCache has already opened `./embeddings_cache.db` read-write. A launch from the main checkout would be refused, but only after the main cache was opened. It also does not cover the site-null task, which never calls the fetcher.
- L5 (the shell pre-flight BEFORE the JVM) therefore stays exactly as written, and so does L6 (the main-cache pins before and after).
- **L8 gains one line:** the build log must show `[LCB] working-dir guard passed: '<the build worktree>' ...` before `[LCB] fetched N`. The guard refusing is a failed precondition, never the arm's result (L9 does not apply to a guard refusal).

## (3) The D9 pins: CONFIRMED

- The four src/main blobs at 4497373 are the ones in the table above. The precondition holds: `git diff --name-only a62c7e0 4497373 -- src/main build.gradle.kts settings.gradle.kts gradle.properties gradle/ config/` = exactly those 4 files.
- The main checkout has not moved these paths since a62c7e0: the same diff against main counts 0.
- The arm TOML ag_news_smoke_s42.toml is blob efd82bda at a62c7e0, at 4497373 and on main.
- The ruling's KDoc item is done: the `fetchLiveCodeBench` KDoc is directly above the function (L1067-L1069). The optional `user.dir` move is also done.
- Discriminator in the build worktree's compiled classes (`grep -rlaF <id> build/classes/kotlin/main | wc -l`, compiled from the current sources per `:compileKotlin UP-TO-DATE`):

| identifier | count | ruling's minimum |
|---|---|---|
| LIVECODEBENCH | 4 | >= 3 |
| fetchLiveCodeBench | 2 | >= 1 |
| lcbWorkDirGuard | 1 | >= 1 |

- These counts match the builder's 4 / 2 / 1. They are a witness from this worktree only; D9-R1 must re-count them in the fresh leg-B worktree and read 0 / 0 / 0 in leg A.
- Any later byte change to any src/main file on the branch voids these pins (ruling Q3).

## Findings (all LOW; none gates (1)-(3))

- **E1.** A GATE text among the leaf members is never exercised by the selftest. Mutant D1-held-ignored (`held = []`) SURVIVED the selftest. It is still refused, by the count check: `heldprobe.py` on that mutant gives "TRAIN members 632 vs distinct leaf queryIds 633". So the protection holds twice, but its positive branch is untested. Fix: add a fixture with one GATE text as a member and assert the "TRAIN-ONLY violated" refusal.
- **E2.** The "K <= 4" leg of the SCOREABLE rule is untested. The fixture has K = 4, and mutant D4-status-K-ignored SURVIVED. Structurally K <= 4 at TRAIN 633-642 (DEV draws), since K = 5 needs >= 650. Fix: a crafted K = 5 case.
- **E3.** The S2 test cannot tell "n = 10" from "n = 10 and temp 0.2": every fixture n = 10 model has temp 0.2, and mutant D6-S2-temp-ignored SURVIVED. The code is correct. The real roster has 3 n = 10 files at temp 0.6, so the mutant would give S2 9 models instead of 6. Fix: add one n = 10, temp 0.6 model to the fixture.
- **E4 (note).** `stats.SAFE_AFTER` is now bound as a default argument, so reassigning the module constant at run time no longer changes the path. Callers must pass `safe_after=`. This is correct as written; my first-review scripts that reassigned the constant apply to ed948d6 only.

## Launch conditions: amendments to L1-L10 below (insertion)

- **L8 + guard.** Add the `[LCB] working-dir guard passed` line, as in (2).
- **L10 superseded.** The analysis of record may run after the window, with these requirements:
  - `--pins <json>` carries the run-operator's post-window record of dag_snapshots.jsonl, snapshots.db, the checkpointed build embeddings_cache.db and the site-null CSV;
  - `--site-null` is given;
  - B = 2000.
- The post-run review re-checks:
  - the sealed EVAL DB sha;
  - the RECOMPUTATION line;
  - that no single-contrast claim appears when the status is DESCRIPTIVE-ONLY.

## Commands

All under the session scratchpad `rv_lcb/`, on base2 = `git archive 4497373`:

| step | command |
|---|---|
| selftest | `selftest.py` and `python -O selftest.py` |
| cross-check | `selftest.py --quick --ruling-crosscheck ../lcb_s0/rule --xc-worlds 10` |
| mutants | `mutants2.py` (34 mutants), plus the D1-unknown-ignored re-run on a unique string |
| D1 probes | `heldprobe.py base2 held`, `heldprobe.py mut2/D1-held-ignored held`, `heldprobe.py base2 unknown` |
| compiled-class checks | `javap -c -p taxonomy.dataset.MMLUDatasetFetcher` on the worktree classes |
| Gradle | `.\gradlew.bat test --offline --rerun --tests <9 classes>` in the build worktree; the worktree stayed clean, and only its embeddings_cache.db -shm mtime moved |

---

# READY review: LCB-STAGE0-INTERACTION, build ed948d6 (parent 6af3a85)

Reviewer: adversarial-reviewer, 2026-09-25. Zero LLM calls. No LiveCodeBench outcome value was read: no graded_list, no pass@1, no outcome DB (none exists yet). Not run: the record draw, the outcome or construction ingest, embeddings, the build, the site null, the analysis on real data. Nothing in the build worktree or any DB of record was written. My scripts ran on a `git archive ed948d6` copy in the session scratchpad (`rv_lcb/base`, blobs equal to ed948d6 for all 10 package files) with `python -B`.

Objects reviewed:
- Registration: docs/judge_v2_program.md L17702-L17982 (a62c7e0).
- Orchestrator decisions: A1-A8.
- Pre-data amendment: L18102-L18373 (01a506e), with its 11 line brackets.
- Build: branch worktree-agent-adb18465164aaf122, NOT MERGED (`merge-base --is-ancestor ed948d6 main` is false). 21 files changed a62c7e0..ed948d6: `git diff --name-only a62c7e0 ed948d6 | grep -c '^docs/'` = 0, and the count for application.yml / .env / .gitignore = 0. Main has changed none of these 21 paths, and no `src/` file, since a62c7e0 (both counts 0).

## VERDICT

| step | verdict |
|---|---|
| 1. One-shot record draw (`draw.py --seed "LCB-STAGE0-SPLIT:cc7a6d7f..." --registration LCB-STAGE0-INTERACTION`) | **READY** |
| 2. Outcome ingest (`ingest.py --outcomes`) and construction ingest (`ingest.py --construction`) | **READY**, under L1-L3 below |
| 3. Rule-7 build window (embed check, build, site null from the worktree) | **READY**, under L4-L9 below |
| 4. The analysis of record (`analysis.py`, after the window) | **NOT READY** until D1 (HIGH) and D2-D4 (MEDIUM) are fixed and a delta review passes. None of these fixes touches the draw, the ingest or the build. |

## Pins (hash kind named; the LF rendering is of record; the worktree files are LF unless a CRLF value is shown)

tools/analysis/lcb_stage0 at ed948d6:

| file | blob | sha256-lf16 |
|---|---|---|
| analysis.py | 5553e76a | e2a955a3a47a3b8e |
| stats.py | 31490553 | 7dd2f4e5303066e4 |
| selftest.py | 2fb5095a | 78544af355bdb527 |
| fixture.py | 3369c11e | 64735d943b082741 |
| ingest.py | 4a43de63 | 61cd03e7f42169df |
| draw.py | ed5801a8 | 23618585ef34e575 |
| common.py | 022f11bf | a890323a74b2bd9b |
| download.py | d72b5d00 | 226beb86ea23515f |
| embed_context_check.py | a3e41e16 | b7547057b0d6a20f |
| \_\_init\_\_.py | a861097a | 758ab9c9ca3225fb |

Other files:
- Template: lcb_af_bareq512_s42.toml.template, blob af49d40a, sha256-lf16 e362ac6f8a95a3cd.
- Kotlin, working tree CRLF:
  - TaxonomyConfig.kt: blob 2825b12d, lf16 61f67a71d6ca9cd3, crlf16 1860445fcb273875.
  - CorpusRegistry.kt: blob 5b1bbb3a, lf16 f8f39d7aca0b4666, crlf16 6f71693dda26d859.
  - CorpusSource.kt: blob 817b1417, lf16 00af04220803814c, crlf16 af3dde076e7df6bf.
  - MMLUDatasetFetcher.kt: blob 3ca53697, lf16 85f89ad295a19b2f, crlf16 32972bc7236ea0e0.
- Tests:
  - LiveCodeBenchDatasetTypeTest.kt: blob 45aa0c80.
  - LcbStage0ConfigTest.kt: blob 9cb34d12.
  - PinnedPoolsReproduceTest.kt: blob 9cfcd2fc, crlf16 28ef77e617995245.
- Pinned closure modules. The blob is the same in the worktree, at ed948d6 and on main:
  - split_side: blob:05224b5a.
  - passage_closure: blob:003d5d4e.
  - content_closure: blob:1533cb5a.
  - pool_guard: blob:6521b51a.
- Committed manifests (file sha256; LF, no CRLF rendering):
  - ingest_texts_manifest.json: 7ec76d95d8d8856782848c519d8691f20bad138f148a2085142e8e0637701182.
  - roster.tsv: c332b558a5faced19041dc1f30b9c1c1130020644059fbf7a6706135c8133610.
  - download_manifest.json: sha256-lf16 0de7b77d1b21cd6f, which equals the texts manifest's download_manifest_sha256.
- Texts DB (file sha256), under TAXOARENA_LCB_ROOT:
  - lcb_v6_texts_7d2f4cad635b254d.db = 5f8ae5d8acbfa4dcf97cf6fb329cc51af4cb7c108be4299b52fc01838cf689be.
  - Table-sha, my own recomputation (read-only, immutable=1): problem 1,055 rows 7d2f4cad635b254d, roster 74 rows 1e92d878ec12d13b, meta 15 rows e66f5ced18f3540c, M_texts 26.
- Superseded DB: lcb_v6_texts_7d2f4cad635b254d.superseded_6af3a85.db = f0f56aec...
  - Its problem table is the SAME: 7d2f4cad635b254d.
  - Its roster table is c88a229f and its meta has 14 rows, M_texts 25.
- Main-checkout caches, baseline for the window:
  - embeddings_cache.db: 804,462,592 bytes, mtime 2026-09-23 14:33:13; -wal 0 bytes; embeddings 39,631 / queries 31,986 / gmm_vectors 0 rows (immutable read). These equal the data-steward's figures.
  - snapshots.db: mtime 2026-09-23 04:34:26; -wal 0 bytes.

## Per-claim table

| # | claim | result | command / evidence | got vs claimed | sev |
|---|---|---|---|---|---|
| B1a | marginal rank-1 fit: 41-node GH, EM + Newton M-step, prior SD 1.0 on log s around roster mean; converged iff max\|grad\|<1e-6 and \|a\|, s <= 50 | CONFIRMED (code + execution) | stats.py L240-L405 read. Selftest checks: finite-difference gradient of the independently written penalised likelihood (`pen_marginal`); pihat equals E[pi \| Y] by direct quadrature; 41 nodes. Mutants: prior removed / gradient-only / centred at 0 KILLED ("finite-difference gradient ~ 0"); tolerance 1e-3 and 1e-5 KILLED ("marginal fit converges under the ruled rule"); GH 21 KILLED; fit_null = joint KILLED | as claimed | - |
| B1b | cross-check reproduces the ruling's per-world JSON EXACTLY on 200/200 worlds | CONFIRMED | `selftest.py --quick --ruling-crosscheck <scratchpad>/lcb_s0/rule --xc-worlds 50` (ruling scripts rsim 5d961f33, mml 53e94bb5, agg 006f865c, conv_side 115a2111 = the ruling's printed prefixes) | 50/50 on each of base / twins / slope / slope2 for convergence, iterations + max s, p_T, X2 + p_X2, joint convergence; 499 checks, SELFTEST OK | - |
| B1c | every consumer reads the same fit; joint fit a diagnostic | CONFIRMED | analysis.py L336-L367, L409, L424, L435-L446: TRAIN, S1-S3 and GATE call fit_null; Z1/Z2, Delta-D and the common null reuse the primary fm; the joint fit only feeds `joint_p_T` | - | - |
| B1d | SAFE_AFTER fallback "engaged in one planted fixture fit and never in the ruling's worlds" | REFUTED on both counts; consequence ruled below (Deviation 1) | `rv_lcb/safe_after.py ruling`; `rv_lcb/dry_safe.py`; a scan of all 27 ruling JSONs (3,850 worlds) for mmlp1_iters > 1000 | Ruling worlds: engaged in 1 of 3,850 (null_slope_2 world 133, 2,294 iterations). The outcome is identical there: same iterations, \|dpihat\| 1.4e-13, p_T 0.70615 both ways. Fixture: engaged in **3 of 6** fits (Delta-D K=4 at 1,022 iterations, S1 at 1,030, GATE at 1,036), not 1 | LOW (claim) |
| B2 | apply_roster gives M = 26 (16/9/1); texts DB 5f8ae5d8, roster c332b558, manifest 7ec76d95; old files REPLACED and named in `supersedes` | CONFIRMED | my application of D4 (i)-(vii) by name to roster.tsv (74 files, 73 folders, 35 eligible): drops Opus-4 / Sonnet-4 (iv), Exp (N=10)\_1\_ (ii), Thinking-12-19 (v), O3-Mini Low/Med and O4-Mini Low/Medium (iii), QwQ-32B_temp (i); 0 duplicate kept shas. `grep -o '"question_id"' \| wc -l` on the (N=10) \_10\_ file = 880 (a key count, no value read). sha256sum of all three artefacts. supersedes shas = `git show 6af3a85:<file> \| sha256sum` (b51a3d48, a5d64a3d) and the old DB f0f56aec | 26 = 16 n=1 / 9 n=10 / 1 n=4. n=10 files: 6 at temp 0.2, 3 at 0.6, so S2 = 6 models and the n=10 pair class = 36 | - |
| B3 | precedence UNDETERMINED > TREE=FORMAT > {GO, SSP, STOP}; "tree = format" printed in every outcome | CONFIRMED | stats.decide L748-L762; render L547. Mutants: swap UND/TF KILLED ("UNDETERMINED over TREE=FORMAT (Q3)"); GO over TF KILLED ("TREE=FORMAT over GO"); annotation dropped KILLED; GO without G2 KILLED | - | - |
| B4 | p_T / p_X2 at the family-majority labelling; own-region values beside | CONFIRMED in code, PARTLY tested | run_null L626-L648 read. Mutant "T at own region" KILLED ("T is taken at the family-majority labelling"). Mutants "observed X2 at own-region clusters" and "R-REP GATE at own regions" **SURVIVED** | see D5 | MEDIUM |
| B5a | analysis.py readers verified by sha | PARTLY | texts DB (file sha vs manifest), TRAIN+GATE DB (file sha vs manifest) and split TSV (committed blob + sha) are verified. The BUILD inputs (dag_snapshots.jsonl, snapshots.db, the build worktree's embeddings_cache.db) and the site-null CSV are verified by nothing, and the outcome names none of them | see D2 | MEDIUM |
| B5b | "eval_sealed" appears nowhere in analysis.py | CONFIRMED | `grep -c eval_sealed` = 0 in analysis.py, stats.py, fixture.py, draw.py and common.py; only ingest.py (the writer) and selftest.py name it. Audit-hooked dry-run: every DB analyse() opens is texts / train_gate / the build's snapshots and embeddings, all mode=ro&immutable=1 | - | - |
| B5c | main embeddings_cache.db and snapshots.db refused | CONFIRMED (by path) | guard_not_main L101-L105; selftest refusal "MAIN checkout" | the refusal is by path only (see L5) | - |
| B5d | write-once outcome | CONFIRMED | write_outcome opens with "x" and dies if the file exists; selftest refusal; main() refuses B != 2000 or a missing site-null CSV without --partial | - | - |
| B5e | dry-run on a planted-interaction fixture reads GO | CONFIRMED | `audit_open.py analysis.py --dry-run` | GO; tree = format: no; T 1847.8 (own 1857.5), p_T 0.0050 at B 199; X2 260, p 0.0050 | - |
| B5f | every verdict, prediction and falsifier branch executed both ways | PARTLY | s_analysis drives Q1-Q8 and F1-F4 HELD/FAILED(/UNDETERMINED) and all 5 verdicts, but only through crafted results (score/render). Mutant "support gets converged = True" **SURVIVED**: the analyse()-level path "primary fit does not converge -> UNDETERMINED" is never executed; with that mutant it would read STOP. Mutant "S2 roster filter matches nothing" **SURVIVED** | see D6 | LOW |
| B6 | pointer fixed; LeetCode id-order disclosure | CONFIRMED | `grep -rn L17966 tools/analysis/lcb_stage0/*.py \| wc -l` = 0 (6af3a85 had it at stats.py L585); L17973 at stats.py L750; texts manifest "surrogate_order" states string order ('100' < '3000' < '99') | - | - |
| T1 | selftest 277 checks / 38 refusals under python and -O | CONFIRMED | `python -B selftest.py` and `python -B -O selftest.py` (first line prints "python -O: True") | 277 / 38, SELFTEST OK in both; 19 s each | - |
| T2 | targeted Gradle 41/41 | CONFIRMED (my own run) | `.\gradlew.bat test --offline --tests` for CorpusIds, LiveCodeBenchDatasetType, PinnedPoolsReproduce, SplitTextClosure, AnchorFreeInertness, ConstructionOrderInertness, ConfigParses, LcbStage0Config, TopicPartitionConfig; XML timestamps 04:57Z | 41 tests, 0 failures, 0 errors, 0 skipped | - |
| H2/R4 | the draw re-derived by an independent implementation | CONFIRMED on DEV seeds; the record-seed R4 is still owed after the draw | `rv_lcb/indep_draw.py` (sha256 34ffdbba...) is my own tokeniser, 8-shingles, df with a mask at df > 6, diagonal runs >= 13 shingles, the D-edge regex, union-find, component id, modal stratum and the rank / round-half-up rule. It shares only split_side.stem_key. Run on the REAL texts DB (texts only) against draw.run with DEV seeds DEV-RV-LCB-1/2/3 | P edges 91 (equal sets), D 0, band 134, 986 components / 49 multi / largest 8 / Kish 1.2142. Sides agree 1,055/1,055 on all 3 seeds; realised EVAL 309/318/310, GATE 106/104/103. Stored surrogate, stem_key, item, format and stratum: 0 mismatches of 1,055 | - |
| R1 | the draw is one-shot and refuses a second run | CONFIRMED (with a limit) | draw.run L280-L282: split_manifest.json present -> die BEFORE the rank is computed (L288); selftest refusal "R1"; dirty-paths check; only the exact (registration, seed) pair is admitted | The guard is the file's presence in THIS checkout's manifests/, so another checkout could run it again. The output is byte-deterministic given texts DB 5f8ae5d8 and the seed, so a re-run cannot re-draw | LOW |
| H6/P2 | no stage-0 process opens an in-flight object or a main-checkout DB | CONFIRMED for draw --dry-run and analysis --dry-run | `audit_open.py` (sys.addaudithook on open and sqlite3.connect). draw --dry-run: the only DB opened is the texts DB, mode=ro&immutable=1; no rank with the seed of record. analysis --dry-run: temp fixture only | 0 main-checkout paths in either run | - |
| Support | registration Support section non-vacuous; SE re-derived | CONFIRMED | own arithmetic: sqrt(1.1 x .10 x 8 / 630) = 0.03737 -> 10.46pp; K3 9.06; K6 v.25 20.26; v .0675 K4 8.60, K3 7.45; v .195 14.61 / 12.66; floor 6.31 / 7.73 at DEFF 1.0. CP: 18/1500 [0.0071, 0.0189]; 9/600 [0.0069, 0.0283]; 6/300 [0.0074, 0.0430]; 2/300 [0.0008, 0.0239]; 1/300 [0.0001, 0.0184]; P(X >= 18) = 0.2503. DEFF source named (a declared pilot assumption, synthetic 1.00-1.04, Kish 1.214 upper bound); n_eff 573-630 | all equal to the digit | - |
| Inert | DatasetType.LIVECODEBENCH "proved by a byte-inertness run WITH an execution discriminator" (P1 / A5) | SUBSTITUTED | LiveCodeBenchDatasetTypeTest: ordinals and offsets unchanged (structural) + the new branch executed on a temp Design N DB (the discriminator). No before/after construction run was made (6af3a85 and ed948d6 commit messages; no artefact) | a structural proof replaces the registered byte-inertness run | MEDIUM (gates the merge to main, not the window) |

## Deviations: rulings

**1. SAFE_AFTER = 1000 exact-curvature fallback: ACCEPTABLE. It does not change the estimator the ruling fixed. It changes only whether the algorithm reaches that estimator. Conditions are in D3.**

What changes and what does not:
- The objective is unchanged: the penalised marginal log-likelihood.
- The gradient that decides convergence is unchanged. It is exact (Fisher identity plus the prior's exact derivative; the mean term cancels).
- The convergence rule is unchanged.
- The branch alters only the Newton curvature used for the M-step after 1,000 EM iterations. Every fit that reads "converged" is therefore a stationary point of the ruled objective.

Evidence, all synthetic:
- **The one engaged ruling world is identical.** In null_slope_2 world 133, the build path, the build with SAFE disabled and mml.py all converge in 2,294 iterations. max s is 5.32336 on all three, max\|pihat diff\| is 1.4e-13, and p_T is 0.7061469 on the same 2,000 permutations. Size is therefore unchanged where the ruling measured it: 1/3,850 engaged, and identical there.
- **In the dry-run fixture the branch is load-bearing.** The fixture has M 29 and a strong planted interaction (tau 1.2). On Delta-D, S1 and GATE, the ruling's reference path (prior curvature 1/(sd² s²) throughout) does NOT converge in 5,000 iterations: max\|grad\| 10.0, 11.6 and 4.85, a 2-cycle. The SAFE path converges (< 1e-6) at a HIGHER penalised log-likelihood:
  - -10531.054 vs -10531.114;
  - -11440.320 vs -11440.456;
  - -1931.017 vs -1931.165.
  - Consequence: the rendered outcome changes on 4 lines. Delta-D converged True vs False; S1 computed vs "did not converge"; R-REP computed vs "not computed"; Q5 HELD vs UNDETERMINED.
  - The PRIMARY fit (72 iterations) and the verdict (GO) are the same either way.
- **I found no null world where it engages outside the ruling's one.** 0/6 all-binary null worlds and 0/12 near-zero-slope null worlds (`safe_size.py`, `safe_after.py cons`). Engagement tracks misspecification (strong interaction), not the null, so it cannot inflate G1's size in any world I could construct.

Reading: where the ruling's reference code would print "not converged" (support fails, or a sensitivity or R-REP goes missing), the build reaches the ruled estimator. That is the ruled estimand, reached by a safer step, not a different estimator. But the branch is not the rare curiosity the commit describes, and it is currently disclosed only for the primary fit (D3).

**2. The 6af3a85 ingest artefacts REPLACED, not bracketed: ACCEPTABLE.** Rule 3 (insertion only) governs recorded sentences in the files of record. The replaced files are machine manifests on an unmerged branch, and git keeps 6af3a85's bytes. The new texts manifest's `supersedes` block names all three old shas: I verified b51a3d48 and a5d64a3d by `git show 6af3a85:<path> | sha256sum`, and f0f56aec on the kept, renamed DB. Nothing consumed the old artefacts: split_manifest.json is absent in manifests/ (`ls`, 3 files), and the problem table, the only draw input, is byte-identical (7d2f4cad in both DBs, my recomputation).

Two conditions:
- Keep the superseded DB. Include it in the E: backup.
- A checkout of 6af3a85 now fails its texts-DB sha check (the file name was reused). That is fail-closed, and acceptable.

**3. DEFF recomputation "met by construction": PARTLY ACCEPTED.**
- What holds:
  - G1 is a family-block permutation test, valid at any family DEFF.
  - G2's SE_k are family-clustered by formula (the selftest checks this against a direct loop).
  - The SUPPORT line prints the measured DEFF (median, q90, max), n_eff and MDE80 at the measured DEFF.
  - So the verdict needs no recomputation.
- What does not hold: the registration also requires that "every SE and MDE below is recomputed" when DEFF > 1.3, and "below" includes the single-contrast SCOREABLE class (two n=10 models, 8.6pp at DEFF 1.1). The analysis prints only the median-v MDE. That class stays under 10pp only while DEFF <= 1.49 at K = 4 (and <= 1.98 at K = 3), at n = 630 and v = 0.0675. The outcome must print it (D4).
- The support condition passed as a literal True (analysis.py L375) is a presence check. Acceptable only with D4's printed numbers beside it.

**4. Points left to the build:**
- **EVAL is not routed in stage 0: ACCEPTABLE**, deferred to stage 1. Stage 0 reads no EVAL outcome, and EVAL regions decide nothing here. Condition: the tree must be pinned in the outcome (D2), so that stage 1 routes EVAL through the identical frozen tree.
- **Boards on informative TRAIN at own regions: ACCEPTABLE.** Section 4's data object is the informative TRAIN set, and the ruling puts the boards at own regions. The render labels them "informative TRAIN problems".
- **Q1 purity: ACCEPTABLE.** It is computed over all TRAIN problems at their routed depth-1 ancestor. HELD needs exactly 2 depth-1 cells with distinct majority formats and purity >= 0.90, a faithful reading of "the depth-1 split = input format". State "routed" in the outcome.
- **Z1 median-date split: ACCEPTABLE.** The median is taken over the informative TRAIN contest dates ([:10]), with a date <= median going to half 0, fixed before the data.

## CK-CLOSE-v1 conditions (the registrar's open item)

- Sentinels: N/A. There are none; all 1,055 problems are keyed.
- Global closure: computed over the whole universe before the draw.
- Family closure: whole components per side. content_closure.assert_content_disjoint runs on the three side pairs, and the "straddle" die is executed on every DEV draw above.
- Within-held-out twins: clustered, never dropped (reserved_clusters; families are the analysis cluster).

The four conditions hold by construction. The words "content-closed under CK-CLOSE-v2" are allowed only after the record-seed R4 (L2).

## Hunt results

- **EVAL outcomes into TRAIN decisions.** analyse() never opens the sealed DB. The audit hook confirms it, and the source count is 0. Two EVAL reads remain, both inside `ingest --outcomes`:
  - the pass@1 == mean(graded_list) assertion, which can only abort;
  - the (vii) matrix leg, which hashes full graded matrices, EVAL included, to drop an identical-matrix model. That is a roster decision informed by EVAL values, but only on exact identity.
  - Rating: LOW, disclose it (D8).
- **EVAL texts into the construction.** None. The construction DB holds TRAIN and GATE only (selftest), and GATE is declared as reservedPoolFile. EVAL texts sit in a separate DB that nothing in stage 0 reads. analyse() reads EVAL texts only to hash them for the held-out membership check.
- **One-shot draw.** CONFIRMED, with the limit noted at R1.
- **Separate embeddings cache.** NOT ENFORCED BY ANY CODE.
  - The TOML has no cache path. EmbeddingCache and the site null open `embeddings_cache.db` relative to the working directory.
  - So the separation is entirely the operator's `cd`. A launch from the main checkout would write the main embeddings_cache.db queries table and more (the CONSTRUCTION-WRITES-CACHE-DBS gotcha).
  - The analysis-side guard refuses only by path. This is a presence-only protection: L5 makes it fail-closed at launch, and D7 asks for an engine-side refusal before the merge.
  - The build worktree's own embeddings_cache.db has 0 rows in every table but a 37,112-byte -wal (Gradle test residue; my test run touched only its -shm). analysis.open_ro REFUSES a non-empty -wal, so a checkpoint is required after the build (L8).

## Defects

**D1 HIGH: the TRAIN-ONLY / held-out membership check in analysis.py is vacuous under an id mismatch.**
- analysis.py L292-L304 counts GATE/EVAL texts whose `q_`+sha256(text)[:16] appears among the leaf queryIds. It never checks that the leaf queryIds resolve to known texts at all.
- Executed: with the fixture's member ids hashed from a different string (`FX.qid` patched), dry_run returned heldout_members 0, routing "0 / 0 = nan", verdict GO, and no refusal.
- The 20NG precedent (topic_partition.py L353) dies when leaf queryIds match no ingest text.
- Fix:
  - Refuse unless every distinct leaf queryId maps to a TRAIN text (unknown = 0).
  - Refuse unless train_members equals the number of distinct leaf queryIds and is > 0.
  - Print both counts.
  - Add a selftest mutant with mismatched ids that must be refused.

**D2 MEDIUM: the outcome does not name or pin its tree or its build inputs.**
- render() prints the pool id but not:
  - the snapshot id or the sha256 of dag_snapshots.jsonl (last line) or of the snapshot graph;
  - the sha256 of the build worktree's embeddings_cache.db (after checkpoint);
  - the site-null CSV sha, or a check that its snapshot_id column equals --snapshot-id;
  - the texts, TRAIN+GATE and split_side shas.
- Fix: print all of them in the outcome header; refuse on a site-null snapshot_id mismatch.
- This is also the condition for Deviation 4a (stage 1 must route EVAL through the same tree).

**D3 MEDIUM: SAFE_AFTER engagement is printed for the primary fit only.**
- R["fit"]["safe_mstep"] is rendered. S1/S2/S3 notes, GATE (R-REP) and Delta-D carry no flag, and those are the fits where it engaged in the fixture.
- Fix:
  - Print "exact-curvature M-step engaged: yes/no" for every fit object.
  - Where it engages, also print whether the reference path (SAFE_AFTER disabled) converges on that object, and its p_T or statistic, so the outcome shows both.
  - Correct the builder's statement ("one fixture fit, never in the ruling's worlds" -> 3 fixture fits; 1 of 3,850 ruling worlds, identical outcome).

**D4 MEDIUM: the DEFF > 1.3 recomputation is not complete (Deviation 3).**
- Fix: print, at the measured DEFF and the informative n, MDE80 for:
  - (i) the SCOREABLE single-contrast class (two n=10 models, their measured median v, K);
  - (ii) the median pair.
- Print the SCOREABLE / DESCRIPTIVE-ONLY status of the single-contrast class beside them.
- Replace the literal True at analysis.py L375 with that computed status.

**D5 MEDIUM: B4's X2 half and R-REP half are untested.**
- The mutants "observed X2 from own-region clusters" and "R-REP GATE at own regions" SURVIVED the selftest.
- The selftest's p_X2 check compares p_X2 with the observed X2 that run_null itself returned.
- Fix: construct a world where a split family changes a reversal; assert out["X2"] == g2_all at the family-majority labelling and != the own-region value; the same for r_rep.

**D6 LOW: two analyse()-level paths are never executed.**
- The path "primary fit does not converge -> UNDETERMINED": the mutant passing converged = True to support_block SURVIVED, and under it a non-converging fit would read STOP.
- The S2 roster count: the mutant making S2 empty SURVIVED; S2 would print "did not converge (fewer than 2 models)".
- Fix:
  - Add an analyse() run with fit_null forced non-converged, asserting UNDETERMINED.
  - Assert S2's M equals the count of n=10, temp-0.2 models (6 at the real roster).

**D7 LOW: guard gaps.**
- The selftest's "\|a\| > 50: not converged" case passes by NaN, not by the bound: base and the bound-dropped mutant both return a[3] = nan at 16 iterations. The bound clause of the convergence rule is therefore never exercised by a finite crossing (mutant SURVIVED).
- The engine-side refusal to build from the main checkout is absent (see Hunt).
- Fix:
  - A finite-crossing test case.
  - In fetchLiveCodeBench, refuse when user.dir is the main checkout (`.git` is a directory, not a worktree file) or when ./embeddings_cache.db holds rows at start. Required before the Kotlin merges.

**D8 LOW: disclose the (vii) matrix-leg EVAL read and the R1 file-presence limit in the outcome's disclosure list.**

**D9 MEDIUM (merge gate, not window gate): the inertness proof form was substituted.**
- The registration (P1 / A5) demands a byte-inertness run with an execution discriminator (CONTEXT rule 11). The build offers a structural proof plus the executed new branch.
- Either run one registered existing arm before and after, with a discriminator (rule 11), or obtain a registrar ruling accepting the structural proof, BEFORE the Kotlin merges to main.
- The build window runs this branch's code, so the window is not gated by D9.

## Reviewer's mutants (19; each is one edit in a scratch copy, run against the build's own `selftest.py --quick`; rv_lcb/mutants.py sha256 d3d07804...)

KILLED by a named check (14):

| mutant | named check that killed it |
|---|---|
| B1 prior removed (PRIOR_SD 1e6) | "finite-difference gradient ~ 0 at the optimum" |
| B1 prior dropped from the gradient only | the same |
| B1 prior centred at 0 | the same |
| B1 tolerance 1e-3 | "marginal fit converges under the ruled rule (max_grad 9.72e-04)" |
| B1 tolerance 1e-5 | the same (9.20e-06) |
| B1 GH 21 nodes | "41-node Gauss-Hermite on N(0, 1)" |
| B1 fit_null = joint | "fit_null is the marginal fit" |
| B3 UNDETERMINED/TREE=FORMAT swapped | "UNDETERMINED over TREE=FORMAT (Q3)" |
| B3 GO before TREE=FORMAT | "TREE=FORMAT over GO" |
| B3 annotation dropped | "UNDETERMINED" |
| B4 observed T at own region | "T is taken at the family-majority labelling" |
| GO without G2 | "STOP-SUB-PRACTICAL" |
| alpha_G1 0.05 | "branch Q3a -> FAILED" |
| GATE share 0.15 | "draw.draw == the independent re-derivation" |

SURVIVED (5), each carried as a defect:

| mutant | defect |
|---|---|
| B1 bound dropped | D7 |
| B4 observed X2 at own-region clusters | D5 |
| B4 R-REP GATE at own regions | D5 |
| support gets converged = True | D6 |
| S2 filter empty | D6 |

## Launch conditions

- **L1.** Draw from the build worktree only, at a clean tree (the R1 dirty-paths check runs). Commit the four manifest outputs by path before `--outcomes`, which refuses otherwise.
- **L2.** Record-seed R4, after the draw and before any "content-closed" wording: an independent re-derivation (e.g. rv_lcb/indep_draw.py with the record seed) must reproduce the committed split_side.tsv on 1,055/1,055 rows.
- **L3.** Back up TAXOARENA_LCB_ROOT (both texts DBs included) to E: with SHA256SUMS before `--outcomes`. Record the sha of lcb_v6_eval_sealed_*.db in the manifest; re-check it at the post-run review.
- **L4.** Hold the window only under the programme's clarified condition: after the PILOT-K46 run and every SPLIT-2 view reader, with PID 53020 resolved, and W1-W5 met.
- **L5.** Pre-flight in the shell, fail-closed. From the build worktree:
  - `test -f .git` must be true (a worktree .git FILE);
  - `pwd -W` must differ from Z:/FAC/TUBerlin/THESIS/TaxoArena;
  - ./embeddings_cache.db must hold 0 rows in embeddings and queries.
  - Abort otherwise.
- **L6.** Before and after the window, take the main embeddings_cache.db per-table pins in both views (mode=ro&immutable=1 and mode=ro) and the snapshots.db mtime/size. They must be identical to the baseline above (39,631 / 31,986 rows, mtime 2026-09-23 14:33:13, -wal 0).
- **L7.** Run embed_context_check.py first; it must print no truncation.
- **L8.** The build log must show:
  - the "[LCB] fetched N" line with N = n_TRAIN + n_GATE from construction_manifest.json;
  - the TRAIN-ONLY guard at 0 held-out members;
  - its own -Dranking.db.path.
  - Afterwards, checkpoint the build worktree's embeddings_cache.db and snapshots.db (a read-write open and close) before any analysis read. The analysis refuses a non-empty -wal.
- **L9.** Never re-run a failed build: the failure is the arm's result.
- **L10.** The analysis waits for D1-D5 and a delta review.

## Commands (reproduction)

All scripts are under the session scratchpad `rv_lcb/`, run with `python -B`, on `git archive ed948d6` extracted to `rv_lcb/base`.

| step | command |
|---|---|
| selftest | `selftest.py` and `python -O selftest.py` |
| cross-check | `selftest.py --quick --ruling-crosscheck <scratchpad>/lcb_s0/rule --xc-worlds 50` |
| SAFE_AFTER | `safe_after.py ruling`; `dry_safe.py`; `safe_size.py 0 6`; `NFLAT=2 FLATS=0.01 safe_after.py cons 0 12` |
| draw re-derivation | `indep_draw.py` |
| open audit | `audit_open.py base/tools/analysis/lcb_stage0/draw.py --dry-run --dev-seeds 3` and `audit_open.py base/tools/analysis/lcb_stage0/analysis.py --dry-run` |
| mutants | `mutants.py` |
| Gradle | `.\gradlew.bat test --offline --tests <9 classes>` in the build worktree |

TAXOARENA_LCB_ROOT listing was identical before and after my reads (`ls -la | diff`); the build worktree's git status stayed clean (0 lines).
