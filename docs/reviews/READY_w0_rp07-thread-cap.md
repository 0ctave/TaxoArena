# READY review: rp07-thread-cap (THREAD-CAP, plan R-F, RP07) at 87c3670 — 2026-09-27

## VERDICT: NOT READY (at 87c3670). The tool is NOT MERGEABLE until H1 and H2 are fixed; after that a delta-READY is enough

What is wrong:
- **H1 (HIGH), the cap has a hole on both governed tasks.** `bootRun` and `siteNull` each depend on a Spring Boot AOT task: `processAot` and `processTestAot` respectively. Both are JavaExec forks, and neither is capped. The reviewer saw it happen. During `bootRun -PjvmThreads=12`, the new line itself printed `[THREAD-CAP] requested=none availableProcessors=24` from the `processAot` fork, which runs `Application.main`, before bootRun's own fork. Registered question: "can every JVM the programme forks (siteNull, bootRun constructions) ... be held to at most 12". As built, the answer is no.
- **H2 (HIGH), the siteNull print is not on every run.** Registered CHANGE (2) says "print on EVERY run, pass or fail". The siteNull line sits after two `Assumptions` (SeparationNullBySizeTest.kt L1671 and L1674). A run with no cache DB or no snapshot is SKIPPED with no `[THREAD-CAP]` line. That is the silent-SKIP mode of the T1b incident. Reviewer mutant X4 (delete that print) survives the builder's 20 legs, the reviewer's 12 legs and the whole suite.
- **B4 / C4 are not READY either way.** The Ollama route was to be "declared before the READY" and is still undeclared (M2).

What is confirmed:
- The pins hold, 6 of 6.
- The change is insertion-only: 229 lines added, 0 removed.
- 20 of 20 proof legs and 9 of 9 builder mutants reproduce.
- The suite gives 453 tests with exactly the 2 known environmental failures.
- The flag reaches BOTH real forks at EXECUTION time (a new reviewer leg, X1).
- With the flag absent, nothing changes (inertness I0 reproduced).

Reviewer: adversarial-reviewer.
- Zero judge or Azure calls.
- No site null, no construction, no Ollama.
- No DB opened by the reviewer. Main's DB mtimes are unchanged (embeddings_cache.db 2026-09-23 14:33, ratings.db 2026-08-08, snapshots_frozen.db 2026-08-02).
- Single-threaded python (OMP / MKL / OPENBLAS = 1). Gradle ran with `--max-workers` 2 to 4. The reviewer's full suite ran with `JAVA_TOOL_OPTIONS=-XX:ActiveProcessorCount=12 --no-daemon` (requested; not witnessed inside the test JVM).
- Scratch: `scratchpad/w0_logs/rp07-review/`.

## Object
- Worktree `.claude/worktrees/w0-rp07-thread-cap`, branch `w0-rp07-thread-cap`, tip 87c3670, parent 4f5e03d.
- `git status --short | wc -l` = 0, before and after every reviewer leg and mutant.
- `git diff 4f5e03d 87c3670 --name-only | wc -l` = 6.
- The commit has 0 paths matching application.yml, .env, .gitignore or report/ (counted with `grep -c`).
- Main is now at 114f80f. `git diff 4f5e03d HEAD --name-only | grep -c` on the 3 modified paths = 0. No other `w0-*` branch touches them (per-branch count 0). A merge by path is clean.

Pins below are recomputed with `git show 87c3670:<path>` and `git hash-object`. The LF rendering is the rendering of record. The working tree is CRLF for three of the files.

| path | blob | sha256-lf16 | sha256-crlf16 | result |
|---|---|---|---|---|
| build.gradle.kts | 29e4ad51e93a033e168c55de43d2dc9d1c60cb86 | 38779ff4b641de26 | 69cfe88b457a97ab (wt) | CONFIRMED |
| src/main/kotlin/taxonomy/runner/ThreadCap.kt | 812fbc6b84a1f1e0b0539582eab657a45062591c | e4a281160d18a4a8 | d25adc2660535edb | CONFIRMED |
| src/main/kotlin/taxonomy/Application.kt | dbfb25610a28a7f69563df2bce4c5dbb683a80f5 | 6d9ff623e9414b17 | 45edf266c5c20b7e (wt) | CONFIRMED |
| src/test/kotlin/taxonomy/SeparationNullBySizeTest.kt | c98a21410d87d206dc3c7d4b42b9c4f4d86acb93 | e6b174396cb83aa1 | 0224aa28c2712a81 (wt) | CONFIRMED |
| src/test/kotlin/taxonomy/ThreadCapProbe.kt | 98536615c0f64057a02686ab945918695f59eca8 | f6d422050a3a3bfb | 49c7642b774378f6 | CONFIRMED |
| src/test/kotlin/taxonomy/runner/ThreadCapTest.kt | bca1b09fada431291447ad446216ff41d226dee7 | aa249d1b540b6dbc | 81b717c0aaf7f849 | CONFIRMED |

## Per-claim table

| # | claim | verdict | command / evidence | got vs claimed |
|---|---|---|---|---|
| 1 | Fail-closed `-PjvmThreads`, refused at configuration time (0 / 25 / abc on the probe, siteNull and bootRun) | CONFIRMED | reviewer copy `run_proof.sh` (sha256-lf16:ae43f3451e0c93c3; only `L=` differs) → `proof_review.log` | 9/9 refusals vs 9/9. Extra reviewer refusals `''`, `012`, `-3`, `99`, `1.5`: 5/5 (`review_legs.log`) |
| 2 | Capped at 12 and at 8, both fork kinds: availableProcessors = N, commonPool = N-1, Dispatchers.Default peak = N | CONFIRMED | `proof_review.log` | 12/11/12 and 8/7/8, exactly as claimed |
| 3 | Boundaries 24 and 1 admitted | NOT CLAIMED; reviewer CONFIRMED | `review_legs.log` A24x, A1x, A1t | 24/23/24; 1/1/peak 2 (max(2, N)) |
| 4 | No flag: requested=none, no cap argument, peak 24 | CONFIRMED | P0t, P0x | as claimed |
| 5 | Task-graph wiring (`-m`) of the real siteNull and bootRun | CONFIRMED | W12 and W0 legs | 4/4 |
| 6 | The flag survives to EXECUTION on the real tasks; the M9 rationale holds | CONFIRMED (reviewer leg) | `exec_view.init.gradle` (sha256-lf16:f21427dc04cc6cc5): a doFirst prints `allJvmArgs` and throws before the fork | siteNull and bootRun at 12 carry `-Dtaxoarena.jvmThreads=12 -XX:ActiveProcessorCount=12`; with no flag, `none` (4/4) |
| 7 | "every JVM the programme forks (siteNull, bootRun)" held to <= 12 | **REFUTED** | `aot_view.init.gradle` (sha256-lf16:38cec2e559d263e8) with `-m`; X1-bootRun-12 output | `processTestAot` (siteNull's dependency) and `processAot` (bootRun's) are `javaFork=true` with cap args `none`. Live witness printed during `bootRun -PjvmThreads=12`: `[THREAD-CAP] requested=none availableProcessors=24 heapEstimate=n/a budget=16.94GB` → **H1** |
| 8 | Inertness I0: with no flag, the full fork args of siteNull and bootRun are identical to 4f5e03d | CONFIRMED | reviewer I0 leg; `fullargs_after.txt` identical to the builder's | 6 lines, cmp identical. The AOT forks are not in I0 (they get no args today); extend I0 after the H1 fix |
| 9 | Changed code ran (class discriminator) | CONFIRMED | `grep -c -a` on the classes | ThreadCap.class 11, ApplicationKt.class 1, SeparationNullBySizeTest.class 1, as claimed. The siteNull print was never EXECUTED (see 11) |
| 10 | Builder mutants 9/9 killed | CONFIRMED | reviewer copy `run_mutants_copy.sh` (sha256-lf16:b20a3a9c4c7e54e5) → `mutants_rerun.log` | 9/9 killed; restored blob 29e4ad51, cmp equal |
| 11 | The `[THREAD-CAP]` line prints "on EVERY run, pass or fail" (CHANGE 2, C3) | **PARTLY / REFUTED for siteNull** | source L1668-L1743; reviewer mutant X4 | Nothing is printed on the two Assumption-skip paths (L1671, L1674). X4 survives every leg and the suite → **H2** |
| 12 | Full suite 453 tests, only the 2 known environmental failures | CONFIRMED | `./gradlew.bat test --offline --no-daemon --rerun-tasks` with the cap via JAVA_TOOL_OPTIONS; XML sum | tests 453, failures 2 (MrlRoutingTest.testMrlConfigDefaults, TraceEnvelopeUnwrapTest blank-trace), errors 0, skipped 0. The builder's `full_suite.log` does not itself print the count |
| 13 | run_mutants.sh sha256-lf16:9a602196610bae9c | **REFUTED** (LOW) | `tr -d '\r' < run_mutants.sh \| sha256sum` | ad7443ee5ea3306c; the builder's own `mutants.log` prints ad7443ee5ea3306c. run_proof.sh ac2daf613b6cb16b CONFIRMED |
| 14 | langchain4j 1.8.0 Ollama request carries no options (route (i) needs a patched client) | CONFIRMED | `javap -p dev/langchain4j/model/ollama/EmbeddingRequest.class` from langchain4j-ollama-1.8.0.jar | fields: `model`, `input` only |
| 15 | B1 reference CSV aec4b517...a665 available | CONFIRMED, but volatile | `sha256sum scratchpad/g22_legA.csv g22_legB.csv` | both aec4b517829a376f84ea...; 88 lines (87 sites). They exist ONLY in the session Temp scratchpad → M3 |
| 16 | B1 / B2 / B4 not run; C1 / C2 / C4 unscored | CONFIRMED | no siteNull, construction or Ollama output in the logs; main DB mtimes unchanged | — |

## Reviewer mutants (5 of the reviewer's own; `review_mutants.sh` sha256-lf16:cd503e569434d2bf → `review_mutants.log`)

Each mutant is scored against three things: the builder's 20 legs (reviewer copy), the reviewer's 12 legs, and ThreadCapTest. All four files were restored with cmp equal to blobs 29e4ad51 / 812fbc6b / dbfb2561 / c98a2141. Porcelain 0.

| mutant | builder 20 legs | reviewer 12 legs | ThreadCapTest | result |
|---|---|---|---|---|
| X2 bound `<= 24` → `<= 23` (refuses 24) | survives | killed (A24x) | pass | killed only by the reviewer's legs |
| X3 regex refuses 1 (`^([2-9]\|[1-9][0-9])$`) | survives | killed (A1x, A1t) | pass | killed only by the reviewer's legs |
| X4 siteNull `[THREAD-CAP]` print deleted | survives | survives | pass | **SURVIVES** (H2) |
| X5 `requested() ?: "none"` → `"none"` | survives | survives | FAILED | killed by the unit test only |
| X6 Application.kt print deleted | survives | survives | pass | **SURVIVES** (it would be caught at B2 as C3 FAILED; nothing now) |

## Defects

- **H1 HIGH: uncapped AOT forks in the governed tasks' dependency chain.**
  - Problem: `processAot` (bootRun) and `processTestAot` (siteNull, and the threadCapProbe) are Spring Boot `ProcessAot` / `ProcessTestAot` JavaExec forks. They run whenever their inputs change, which includes the first bootRun or siteNull after the merge, and they fork at 24 processors. `processAot` runs `Application.main`. Live witness above (claim 7).
  - FIX: in build.gradle.kts, `tasks.withType<org.springframework.boot.gradle.tasks.aot.ProcessAot>().configureEach { applyThreadCap() }` and the same for `ProcessTestAot`. The simpler alternative is `tasks.withType<JavaExec>().configureEach` plus `tasks.withType<Test>().configureEach`, which also closes M1.
  - Re-proof: the AOT-VIEW leg must show the flag at 12 and `none` when absent. I0 must be extended to both AOT tasks (identical with no flag). A new mutant that drops the AOT wiring must be killed.
  - The scope widens beyond "siteNull, bootRun" only in letter, not in intent. The registrar notes it in a bracket.
- **H2 HIGH: the siteNull line is not printed on the skip paths (CHANGE 2 "EVERY run"; rule 11).**
  - FIX: print `ThreadCap.line(null, (maxMemory*0.90).toLong())` as the FIRST statement of the siteNull test, before the Assumptions, and keep the guard-site line with the heap estimate.
  - Re-proof: prove it by execution with a zero-replicate leg in a directory with no `embeddings_cache.db`. A fresh worktree has none until the suite creates one; the rp07 worktree now has a 4 KB stub. The line must print and the test must SKIP. No replicate runs and no DB of record is opened. The orchestrator must admit this leg explicitly, because it invokes the siteNull task.
  - X4 must then be killed.
- **M1 MEDIUM: a valid `-PjvmThreads` is silently ignored by every other fork.**
  - Affected tasks: withinNull, nullBySize, isoNullByDim, routeReserved, placementReplay, calibration, trainOnlyAudit, judgeWiring, matchFilterPlan, randomCellRubrics, test. None of them prints a line or refuses.
  - FIX: either the withType wiring above, or refuse the property on tasks that do not honour it. Until then those tasks are forbidden during the capped wave unless they run with `JAVA_TOOL_OPTIONS=-XX:ActiveProcessorCount=12 --no-daemon`.
- **M2 MEDIUM: the Ollama route is undeclared, although the registration requires it "before the READY".** B4 / C4 are NOT READY.
  - Reviewer's recommendation to the registrar: route (ii), process affinity of the Ollama server. It needs no engine code and no DB-of-record path.
  - Route (i) needs a patched client (claim 14). Route (iii) stays REFUSED until EMBEDDER-PLUMBING merges.
  - B4 then needs its own witness procedure (affinity mask printed, OS peak CPU) in a delta-READY.
- **M3 MEDIUM: the B1 reference exists only in the volatile session scratchpad** (`scratchpad/g22_legA.csv` and `g22_legB.csv`).
  - FIX before B1: copy one of them to a durable backup location outside experiment_results' tracked files, with sha256 aec4b517829a376f84ea2f333a0bc07d8aaae39be8c05e5c05f0271d6ed9a665 printed before and after.
- **M4 MEDIUM (forward, disclose): the cap changes the heap guard's live count.**
  - The guard computes `live = min(reps, availableProcessors)`, so the cap halves the live count, while the 0.90 coefficient was calibrated only at 24 cores.
  - Example: T1b at 12 would be estimated at 3.64 GB and ADMITTED on a 6g heap. That admission is an extrapolation, not calibrated.
  - B1 is unaffected: af_bareq512_s42 goes from 5.00 to 2.50 GB.
  - A capped run of a previously refused arm needs its own heap check.
- **L1 LOW:** the pin for run_mutants.sh is wrong in the report (claim 13). Correct it in any record.
- **L2 LOW: the builder's full suite ran uncapped** (the `test` fork sees 24 processors) under the wave's "no JVM run beyond a unit-test compile". The reviewer's run was capped via JAVA_TOOL_OPTIONS.
- **L3 LOW:** add the boundary legs (=24 admitted, =1 admitted with peak 2) to the proof script. They are the only kills for X2 and X3.
- **L4 LOW, deviations to be bracketed by the registrar (accepted by the reviewer):**
  - bootRun prints `heapEstimate=n/a` with budget = maxMemory;
  - a refusal fails every Gradle task (fail-closed; stricter);
  - the two probe tasks and the init scripts are outside the declared scope;
  - there is no in-JVM refusal when requested and availableProcessors differ (the probe asserts it; not registered).
- **L5 INFO: two `[THREAD-CAP]` lines can appear in one bootRun log.** Whenever processAot is out of date, a bootRun log holds two lines: the AOT fork's line and the application's. For C3 and the B2 witness, the application's line is the one that counts. After the H1 fix, both must read N.

## Reachability, support, hygiene
- C1-C4 are exact comparisons (bytes, counts, a witness value). All are reachable at the planned legs.
- The Support section declares DEFF NOT APPLICABLE (exact byte comparisons). That is correct for an engineering test: no estimate, no SE, SCOREABLE.
- C1 also carries the code drift since 1e0afab (as registered). The new siteNull print adds stdout only and does not change the CSV writer.
- Data and pool hygiene: no pool, cache or snapshot DB was read by this build's proof or by this review. SuperGPQA is not touched. No aggregate was opened.

## Merge + run procedure (after H1 and H2 are fixed and a delta-READY confirms them)
1. **Merge.** The coordinator merges by path: the 6 files, plus the H1/H2 delta. Check with `git merge-base --is-ancestor <prev HEAD> HEAD`. No JVM may run in main during the pathspec commit.
2. **Before any B leg:**
   - backup of the output dirs and the cache DBs;
   - the M3 durable copy of the reference;
   - a W1-W5 rule-7 window announced (exclusive-open probe FREE, >= 12 GB free RAM, admitted PIDs printed, no src/ git write).
3. **B1:** `./gradlew.bat siteNull --console=plain --offline --no-build-cache -PjvmThreads=12 "-PnullReps=24" "-DsnapshotId=20260917_161817_Headless_Run_Auto_ge" "-DsliceDim=512" "-DdropTop=0" "-Dwhiten=false" "-DoutCsv=<scratch path>"`.
   - `-DoutCsv` is mandatory: the default writes the tracked `docs/data/site_null_frozen.csv`.
   - C1 = cmp against aec4b517...a665 AND the application's `[THREAD-CAP]` line reads `requested=12 availableProcessors=12`.
   - Every `[THREAD-CAP]` line in the log is printed, including the processTestAot one.
4. **B2:** A12a, A12b and A8 under the D9b procedure with `-PjvmThreads=12 / 12 / 8`, compared by d9b_compare.py (sha256-lf16:55b961cac7165688, CONFIRMED on main HEAD; blob 209eb2e6). MAIN_taxonomy_quality.csv is excluded (EVAL-METRIC-DETERMINISM).
5. **B3:** already executed. Re-run it on the merged tree together with the boundary legs.
6. **B4:** only after M2's route is declared by the registrar and a delta-READY. Never write to a DB of record.
7. Other Gradle forks stay forbidden during the wave until M1 is closed, unless they run with JAVA_TOOL_OPTIONS and `--no-daemon`.
