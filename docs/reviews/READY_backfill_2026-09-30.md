# READY backfill 2026-09-30: e1-route 6b3f0b1, lcb-resim 35e5cce, eval-metric-det2 77f7cb8

Adversarial-reviewer, 2026-09-30. Zero calls; no JVM, no Gradle, no real run. The PC crashed at about 03:49 and the
engine-coder died without a hand-back. HEAD of main is 1d822bd; ledger v319, unchanged. Registrations: E1-ROUTE
prog L22182-L22206, LCB-STAGE0-POWER-RESIM L22208-L22228, EVAL-METRIC-DETERMINISM L20311-L20389 plus the registrar's
note at L22178 (all _as_of 1d822bd). One heavy process was running during this review (PID 42324,
`intent_transfer_s0.py --embed qwen3 --go`, on Ollama), so no Gradle suite was run (rule: one heavy process at a time).

## VERDICT

| branch | complete? | mergeable? | READY? |
|---|---|---|---|
| e1-route 6b3f0b1 | YES (1 commit on 7ea9ec1; worktree clean; 0 of 3,335 tracked files zero-filled; all blobs hash-verified) | NOT YET (clean `merge-tree` onto 1d822bd; blocked by B-E1-1) | **NOT READY**: B-E1-1 and B-E1-2 |
| lcb-resim 35e5cce | YES (1 commit; worktree clean; 0 zero-filled) | MERGEABLE by path (one new file; clean `merge-tree`) | **READY** under C-LR-1..4 |
| eval-metric-det2 77f7cb8 | Kotlin + test COMPLETE (patch-id = eef090a's, 9975e9d1); harness NOT re-cut; **worktree CORRUPT** (index "bad signature"; 1,524 of 3,335 tracked files zero-filled, including the 3 metric files and the test) | NOT MERGEABLE until the legs are DONE (registration: merge on DONE) | **NOT READY**: B-EM-1 and B-EM-2 |

## Per-claim table (deciding claims only)

| # | claim | mine | status | sev |
|---|---|---|---|---|
| E1 | launcher blob 7eaba3b1, selftest 9/9 | blob 7eaba3b1 (LF, no CR); 9/9 on the branch AND on main's rendering (embedder_arms 2073d131) | CONFIRMED | — |
| E2 | C2: every change to a member of P is caught by (v) | a WAL-tail write into a source DB whose -wal/-shm existed BEFORE the launch: **rc 0, no PIN BREACH** (probe P-E1a). `view()` records sidecar NAMES only; the registration requires their ABSENCE before and after. On main now: -wal (0 B) + -shm beside embeddings_cache.db and both source per-model DBs (mtime 10:55 today) | REFUTED | BLOCKER (B-E1-1) |
| E3 | L1 is one short construction, at most 2 iterations | no L1 TOML declared or committed; the docstring's L1 example is `experiment_configs/anchorfree/redraw/af_clean_s42.toml` itself: numIterations = 50, **outputDir = experiment_results/anchorfree/redraw/af_clean_s42 (the tree of record's directory)** | REFUTED | BLOCKER (B-E1-2) |
| E4 | P is the set of files the JVM would open | the JVM's cwd is `root` (bootRun workingDir = rootDir; the relative DBs `embeddings_cache.db` and `mmlu_pro_dataset_cache_v2.db` open there); P is hashed under `TAXOARENA_DATA_ROOT`. If the two differ, C2 is vacuous for the main cache and the source DBs. A worktree holds none of these DBs, so L1 can only run from the main checkout, i.e. after the src/main merge | PARTLY | HIGH (C-E1-3) |
| E5 | D-EP-3: E1 pins embedder_cross_flat 7868e858 and embedder_arms 2073d131 | branch rendering: 0546800f / f8581aab (the E0b pins); main 1d822bd: 2073d131 / 7868e858 | CONFIRMED only after merging to main | HIGH (C-E1-4) |
| E6 | R2 inert when absent; the src/main diff = 3 declared files | `git diff --name-only 7ea9ec1 6b3f0b1 -- src/main` = 3 (EmbeddingCache, DiagnosticsBundle, HeadlessBenchmarkRunner); absent -> `explicitFileManifest(null,null)` = {} -> no key, no write (read); a source sha without the file REFUSES (check) | CONFIRMED (static; suite not re-run) | — |
| L1 | blob 8622ff95 / sha256-lf16 25da71cd, LF; selftest 9/9 | same; 9/9 in 21 s | CONFIRMED | — |
| L2 | imports the tag's code unedited | tag = 3bcc9ab; stats 813d2d6d, analysis e3144692, fixture 10437edb at the tag and in lcb-build-2 (LF-hashed; 0 of 2,833 zero-filled; clean); `load_tag` checks the three blobs + HEAD = 3bcc9ab | CONFIRMED | — |
| L3 | identity gate T 96.689 / p_T 0.0300 | the gate compares the tag's printed T/p_T to "96.689"/"0.0300" AND re-runs the captured object through the G1-only path, exact float equality; fail-closed (selftest refuses the record's numbers on the fixture). The real-data reproduction is the operator's dry-run | CONFIRMED (code) / UNDETERMINED (real data) | — |
| L4 | 10-world timing dry-run; refuse above 60 min | dry-run times 10 worlds at tau 0.20 in ONE process and projects `per x 2000 / procs`; refuses at > 60.0 min (selftest: 36.0 s ok, 36.1 s refused). Two gaps: (a) the machine has 12 physical / 24 logical cores, so the 20-process projection assumes linear scaling to 20 and understates the wall by up to about 20/13 = 1.5x; (b) `--run` does not re-check the gate | PARTLY | MEDIUM (C-LR-2) |
| L5 | power(0.20) = share of the 400 worlds | `summarise` divides by all 400 (fit refusals count as non-rejections), as registered | CONFIRMED | — |
| M1 | EMD src/main scope = the 3 files; the test is status A; tools/experiment_configs 0; arm TOML efd82bda at BASE and FIX | 3 / A / 0 / efd82bda at both (BASE 1d822bd, FIX 77f7cb8) | CONFIRMED | — |
| M2 | E1-E4 at exactly the four sites, canonical order + tie rule | read: sortedWith(rawText, then element-wise Double.compare, then length), stable, before distinctBy (TDC, TA, SS); DP sorts keys, groups `toSortedMap()`, nodeToLabels in canonical key order. assignedNodeByText is structural (depth ties go to the first node in child order) | CONFIRMED (static) | — |
| M3 | "8/8 pass on FIX, 7/8 FAIL on BASE 8bf15da" | measured at eef090a on 8bf15da, NOT re-run on 1d822bd (the message is eef090a's, cherry-picked); the worktree that would re-run it is corrupt | UNDETERMINED | HIGH (in B-EM-2) |
| M4 | five legs with the same -PjvmThreads (L22178) | harness exists only UNTRACKED in the OLD worktree eval-metric-det (emd_*.py/.cmd, 9 files); `emd_common.py` pins BASE = 8bf15da, FIX = eef090a; `emd_legrun.cmd` bootRun carries **no -PjvmThreads** (grep = 0 in the harness); 8bf15da's build.gradle.kts has no jvmThreads (count 0); 1d822bd's has it (L34-L53) | REFUTED | BLOCKER (B-EM-1) |

## Pins (LF of record; CRLF beside where the working tree is CRLF)

- e1-route: tools/analysis/e1_route_launch.py blob:7eaba3b1 (the working tree is LF).
- lcb-resim: tools/analysis/lcb_power_resim.py blob:8622ff95661f35214791752b9469088aca090432, sha256-lf16:25da71cdec382bef (the working tree is LF, 0 CR).
- eval-metric-det2 FIX 77f7cb8. AdditionalMetrics.kt blob:c908caf5, sha256-lf16:2367a3bbb940f3c0, sha256-crlf16:8716440189285fb8. HierarchicalMetrics.kt blob:4af03144, lf16:85f75032350c6688, crlf16:5b59ef521698ee50. TaxonomyMetrics.kt blob:930adb43, lf16:45a1931d95dceadb, crlf16:b0a2ce4c6132d985. EvalMetricDeterminismTest.kt blob:45d8f0ab, lf16:46aa0389e67c7df4. BASE 1d822bd, src/main tree 201a6595.

## Defects and conditions

- **B-E1-1 (BLOCKER).** Sidecar blindness. Fix `e1_route_launch.py` in two places:
  (1) REFUSE before any copy or launch when any member of P has a -wal, -shm or -journal file. This is the registered
  "absence"; W1's exclusive-open probe gives the same result operationally.
  (2) Make `view()` record each sidecar's size and sha256.
  Then add a selftest case that kills P-E1a, and re-run L0 and the four C5 mutants.
- **B-E1-2 (BLOCKER).** Declare and commit the L1 TOML: a copy of af_clean_s42.toml with numIterations <= 2 and its own
  outputDir outside every object of record. Also make the launcher REFUSE a config whose outputDir is
  experiment_results/anchorfree/redraw/af_clean_s42. The real E1 builds keep their own EMBEDDER-CROSS-FLAT configs.
- **C-E1-3 (HIGH).** Make the launcher REFUSE unless normcase(realpath(DATA_ROOT)) == normcase(realpath(root)), the JVM's
  cwd. L1 and L2 run from the main checkout after the by-path merge of the 3 src/main files, build.gradle.kts, the test
  and the launcher. The suite must be green in a clean worktree before that merge (`.\gradlew.bat test --offline`; 2 known
  environmental failures). EmbeddingCacheManifestTest must be run and not skipped.
- **C-E1-4 (HIGH, D-EP-3).** E1's READY pins embedder_cross_flat blob:7868e858 and embedder_arms blob:2073d131. That holds
  only when the launcher runs from main at or after 1d822bd, never from the e1-route worktree (0546800f / f8581aab).
- **C-E1-5 (MEDIUM).** The launcher uses subprocess.call and captures nothing. The operator tees the JVM transcript and
  scores C3 from it (vmfMu cos >= 0.99, vector length, misses = 0). Misses > 0 VOIDS the leg.
- **C-LR-1 (condition).** The operator uses `--tag-root` and `--build-dir` .claude/worktrees/lcb-build-2 (3bcc9ab, clean,
  not crash-damaged). Before the dry-run, confirm `git -C <tag-root> status --porcelain` = 0 lines. `load_tag` does not
  pin common.py (blob 022f11bf at the tag) (LOW).
- **C-LR-2 (MEDIUM).** Admit `--run` only when the same-session dry-run has rc 0 AND its projected wall x 1.5 (the
  12-physical-core factor) <= 60 min. Otherwise run the dry-run's 10 worlds at the planned `--procs` and re-project.
  Without that re-check, the 60-min refusal can be vacuous.
- **C-LR-3 (LOW, test gap).** Own mutant M-L2 (the Wilson denominator changed to the non-refused worlds) SURVIVED the
  selftest. Add a store with refusals to the --analyze case.
- **C-LR-4 (scheduling).** 20 processes is one heavy process. It must not run beside an RP12 build or window, a
  construction, a site null or the running Ollama embed, and it stays within the ~22-thread cap.
- **B-EM-1 (BLOCKER).** Re-cut the harness, commit it or pin it by blob, and review it before the READY:
  (1) `emd_common.py` BASE = 1d822bd56792dc87b5452a3c2bdbad836a8226fd and FIX = 77f7cb840872d19a0982fd7dd1de8fa5de35ee09.
  (2) `EMD_STEPS.txt` worktree commits updated the same way.
  (3) `emd_legrun.cmd` bootRun adds `-PjvmThreads=12` in all five legs.
  (4) `emd_leg_check.py` requires the witness "[THREAD-CAP] ... availableProcessors=12" in each leg, equal across the five
  legs.
  (5) X1_DECLARED_COUNT is re-measured at FIX.
  (6) The V2 input pins are re-read, or the D9b values are confirmed unchanged.
  The harness selftest and mutants are re-run.
- **B-EM-2 (BLOCKER).** The worktree .claude/worktrees/eval-metric-det2 is unusable: a corrupt index and 1,524
  zero-filled tracked files. Remove it (`git worktree remove --force`) and re-add it at 77f7cb8. The commit is intact:
  11 of 11 delta blobs re-hash to their ids, and `rev-list --objects | cat-file --batch-check` reports 0 missing
  objects on all three deltas. `git fsck` itself aborts on the corrupt worktree index. Then run the FIX suite
  (`cleanTest test --offline --no-build-cache`) and the golden test on BASE 1d822bd, and record the pass/fail counts
  (registered: TDC fails on BASE; the other per-metric results are printed). This must happen outside any RP12 window and
  with no other heavy process.
- **C-ALL (rule 7).**
  - E1 L1 is a construction and a pool reader: one W1-W5 window with a backup first.
  - The EMD legs take one window of about 25 min.
  - The LCB resim is a heavy CPU process.
  - None of the three may overlap an RP12 build or window, or each other.
  - The E1 src/main merge is a git write under src/, so it happens outside every window (W5).
  - All three WAIT while PID 42324 runs.

## Own mutants and probes

- P-E1a: a WAL-tail write into a protected source DB that had pre-existing sidecars. SURVIVED (rc 0): DECISIVE (B-E1-1).
- M-E1-2: the `--dir-file` target check removed. Survived. Not decisive: the default path cannot equal a scratch file
  outside e1_route_work.
- M-E1-3: sidecars never viewed. KILLED.
- M-L2: the Wilson denominator changed to the non-refused worlds. SURVIVED. Not decisive at <= 20 refusals: it moves the
  interval, not the point (C-LR-3).
- EMD: no mutant run, because Gradle was barred by the running heavy process. The registered V3/X1 and C2 non-vacuity
  legs carry this.

## Commands (repo root Z:\FAC\TUBerlin\THESIS\TaxoArena; bash)

```
git merge-base main <b>; git diff --name-status <mb> <b>; git merge-tree --write-tree main <b>
git show eef090a | git patch-id --stable; git show 77f7cb8 | git patch-id --stable      # both 9975e9d1...
git -C .claude/worktrees/<w> status --porcelain                                        # det2: "index file corrupt"
python $TMP/zscan.py <worktree> <commit>   # counts tracked files that are all-NUL: det2 1524/3335; e1 0/3335; lcb 0/3334; lcb-build-2 0/2833
for o in $(git rev-list --objects --no-object-names <mb>..<tip>); do git cat-file blob $o | git hash-object --stdin --no-filters; done   # 11/11 equal
git rev-parse {main,6b3f0b1}:tools/analysis/embedder_arms.py {main,6b3f0b1}:tools/analysis/embedder_cross_flat.py
python tools/analysis/e1_route_launch.py --selftest     # branch 9/9; main-rendering copy (git archive 1d822bd tools/analysis) 9/9
python scratchpad/e1m/probe_wal.py                      # "rc=0 refused=False breach_reported=False"
grep -n "numIterations\|outputDir" experiment_configs/anchorfree/redraw/af_clean_s42.toml   # 50; .../redraw/af_clean_s42
grep -n "workingDir = rootDir" build.gradle.kts; ls -la embeddings_cache*.db-*        # sidecars present on 3 members of P
python tools/analysis/lcb_power_resim.py --selftest     # 9/9, 21 s
git rev-parse lcb-stage0-outcome-of-record:tools/analysis/lcb_stage0/{stats,analysis,fixture}.py
Get-CimInstance Win32_Processor  -> NumberOfCores 12, NumberOfLogicalProcessors 24
git diff --name-only 1d822bd 77f7cb8 -- src/main build.gradle.kts ... | wc -l          # 3
grep -n "jvmThreads" <old worktree>/experiment_results/eval_metric_det/harness/*       # 0 hits; emd_common BASE=8bf15da FIX=eef090a
```
