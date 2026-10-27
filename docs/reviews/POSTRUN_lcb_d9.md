# Post-run review: LCB-D9-BYTE-INERTNESS rerun under DELTA READY 1 (2026-09-25)

Reviewer: adversarial-reviewer. Zero LLM calls. Nothing built or run. Every evidence file was read only; main's DBs were read by file hash only.

Scope:
- Delta READY 1: docs/reviews/READY_lcb_d9_delta1.md (5f7e383).
- Registrar record: 8e649b8, programme L19540-L19585.
- Base READY: bf3fa81.
- Registration: docs/judge_v2_program.md L18662-L18872 (C1 L18838-L18843, Support (g) L18857, P1-P5 L18860-L18864, V8 L18836).

Evidence (session scratchpad `d9\`):
- `run_20260925b\`: d9_compare.txt, aa\d9_compare.txt, d9_disc.txt, the leg and probe logs with their exit files, evidence_A\, evidence_B\, SHA256SUMS;
- `ops_20260925b\`;
- `incident_legA_void_20260925\pseudoroot\` (the A' leg of R9), with SHA256SUMS_R0.

The worktrees d9-legA and d9-legB no longer exist: `git worktree list` names neither.

## VERDICT: VALID. C1 FAILED as registered. R9 reads NON-DETERMINISM. The change is NOT implicated. D9 stays OPEN. No merge on this run.

- **The run is VALID.** Every validity check passes (V2-V9 under DEV-V8, DEV-CAP and DEV-INSTR). The S6' probe PASSES on B, and the S7' control gives `No enum constant` on A.
- **C1 FAILED** (exit 3). 2 of 21 files differ: `validation/MAIN_taxonomy_quality.csv` and `tuning_ledger.csv` (without CommitSHA). The other 19 files, the file set and both reserved_pool* tables are EQUAL.
- **R9 (A/A', same commit a62c7e0, byte-identical inputs) differs in the SAME 2 files and the SAME 3 fields.** The registered interpretation (Support (g); R9 of 8e649b8) therefore applies: the reading is NON-DETERMINISM, the failure is not attributed to the change, and D9 stays open under a new registration.
- **Code-level cause, found at a62c7e0 and unchanged at 6b9fc7c and at HEAD 8e649b8:**
  - the parallel query reassignment appends to `leaf.queries` in thread-completion order;
  - three evaluation metrics iterate that list in order:
    - TotalDasguptaCost samples 5,000 pairs BY INDEX from it;
    - DendrogramPurity and SphericalSilhouette sum over it in floating point.
  - None of the 4 `src/main` files changed by a62c7e0..6b9fc7c is on this path.
- **This was on the record before D9 was registered.** FRAMEWORK.md L297 (since 8d77f7b, 2026-09-15) reads "Stage 2 determinism | P7-FIX | UPHELD | 3/3 byte-identical DAG; quality CSV drift 0.58%". campaign_review_2026-09-10.md L252 (appended 2026-09-14) says `MAIN_taxonomy_quality.csv` "differs across all three post-fix builds ... no gate can see it".
  - C1 as registered was therefore UNREACHABLE AT ANY BUDGET for this arm: impossible, not underpowered.
  - Support (g), the READY bf3fa81 and the delta READY 5f7e383 all missed this. The last two are this role's misses.

## Per-claim table

| # | claim (operator) | verdict | command / script | got vs claimed | sev |
|---|---|---|---|---|---|
| 1 | V3 A 0/0/0/0; B 4/2/1/2 | UNDETERMINED independently; CONFIRMED as transcribed | `run_20260925b\d9_disc.txt` L2, L17. The class dirs were removed with the worktrees; S0' hash-verified the checker `d9_leg_check_v2.py` b2d1ae8d (LF). | d9_disc: A 1,319 class files {0,0,0,0}; B 1,320 {LIVECODEBENCH 4, fetchLiveCodeBench 2, lcbWorkDirGuard 1, LcbWorkDirGuardState 2} = claimed. Not re-countable after the worktrees were removed (D8). | LOW |
| 2 | V4 PASS both legs | CONFIRMED | `grep -a -c "[BOOT] TaxoAdapt starting"`, `grep -a -o "jar=[^ ]*"`, `grep -a -n "> Task :bootRun"` on `leg{A,B}_bootrun.log` (UTF-8 via cmd, not UTF-16: first bytes 53 74 / 43 6f) | each leg: 2 [BOOT] lines, 2 of 2 jar tokens = the leg's own `.../worktrees/d9-leg{A,B}/build/classes/kotlin/main/`; `> Task :bootRun` at L24, a [BOOT] line after it (L25) | - |
| 3 | V6 incl. exit 0 | CONFIRMED | `cat leg{A,B}_exit.txt`; `grep -a -c -F` of the 3 sanity strings in evidence_{A,B}\headless_run.log; run_manifest | EXIT 0 / EXIT 0; BUILD SUCCESSFUL at L782 in both; Fetched x2, POOL p18579549e6d95873 x2, SPLIT-SIDE x1 in both; exit_reason completed; manifest commit a62c7e0 / 6b9fc7c, dirty_src False | - |
| 4 | V7 0 misses | CONFIRMED | `grep -a -c 'Computing and caching embeddings for'` = 0 and 0; "All 1400 requested embeddings are already cached" in both | 0 / 0 | - |
| 5 | V8 ceiling (DEV-V8) | CONFIRMED | run_manifest duration_ms; Gradle line; iteration_metrics line count | A 11,133 ms / 58 s; B 10,825 ms / 41 s; 11 lines = 10 data rows each; all under 8 min | - |
| 6 | S6' probe PASS on B | CONFIRMED | refusal string searched with CR/LF stripped; `grep -a -c "No enum constant"`; probe exit files | probeB: EXIT 1, refusal at char 9,100: "[LCB] refusing to build LIVECODEBENCH: '...d9-legB\embeddings_cache.db' table 'embeddings' holds 39631 rows (a warm cache)...", no-enum 0 | - |
| 7 | S7' control on A: no-enum | CONFIRMED | same | probeA: EXIT 1, `No enum constant` x1, refusal absent | - |
| 8 | C1 FAILED, exit 3; 19/21 + pool EQUAL | CONFIRMED to the digit | my `postrun_d9\recompute.py`: my own sha256 + CSV/JSON drop on evidence_A / evidence_B. Evidence = run output: `sha256sum -c SHA256SUMS` gives 82 OK, 0 not-OK; the evidence hashes equal d9_compare's A 609713d827bccba2 / B 0a9fa8f119cd1fbe. | A vs B differing = 2 (MAIN_taxonomy_quality.csv, tuning_ledger.csv); 24 / 24 files in each leg | - |
| 8a | differing values | CONFIRMED to the digit | `postrun_d9\ledger.py`: column diff of tuning_ledger.csv; the 4 quality CSVs printed | DP A 0.6867787184488087 vs B 0.6867787184488154; SS 0.12807057880923325 vs 0.12807057880923328; TDC 2.2377813825989264E8 vs 2.2376868581711334E8. SeparationJ, WeightedLeafPurity and NormalisedSackinIndex are EQUAL. tuning_ledger differs ONLY in those 3 columns (+ CommitSHA, dropped). | - |
| 9 | R9: A/A' differs in the same two files | CONFIRMED | recompute.py (A' = the pseudoroot; SHA256SUMS_R0 re-checked, 0 not-OK) | A' vs A differing = 2, the same 2 files. DP 0.6867787184488174 vs ...087; TDC 2.2409421312346172E8 vs 2.2377813825989264E8 (0.141%); SS equal (...325 both) = claimed | - |
| 9a | (added) the 2026-09-22 cold reference | - | recompute.py with REF = main `experiment_results/topic_partition/ag_news_smoke_s42` | REF vs A differing = 2, the same 2 files. MAIN_taxonomy_quality.csv has 4 DISTINCT sha256 over 4 runs (A', A, B, REF); every other file has 1 distinct value over the 4 runs. | - |
| 10 | P4 HELD 0/0 | CONFIRMED | claim 4 | 0 / 0 | - |
| 11 | P5 FAILED as registered | CONFIRMED | claim 5 | both legs < 1 min under every reading (11.1 s / 58 s; 10.8 s / 41 s); cause: warm cache (P4 = 0) | - |
| 12 | main DBs unchanged S0'->S12 | CONFIRMED | my `sha256sum` + `ls -l --time-style=full-iso` in main at review time; ops_20260925b\S0p.txt and S12_V9.txt | ag 7cf2082f... 1,622,016 B, mtime 2026-09-22 19:30:24.276; -wal 7eea2abd... 206,032 B; embeddings 52229e1e... 804,462,592 B, mtime 2026-09-23 14:33:13.182, -wal 0 B; snapshots.db 1,065,541,632 B, mtime 2026-09-23 04:34:26.590, -wal 0 B. All equal to the baseline. Table pins equal in both views at S0' and S12. | - |
| 13 | -shm mtime touched | CONFIRMED; the cause is the operator's own reads | S0p `[FILE] embeddings_cache.db-shm mtime 15:22:06` (printed before S0''s own mode=ro pin read at 15:46:21); S12 shows 15:46:30; now 15:55:29 (after S12's mode=ro read at 15:55:21) | each -shm bump comes seconds after a `[PIN mode=ro]` read by the operator's pins.py; content pins unchanged | LOW (D3) |
| 14 | foreign processes (rule-7 overlap) | CONFIRMED present; NO EFFECT possible | `grep -n "[PROC]\|python"` over ops_20260925b | PID 48696 `archv2_pilot/selftest.py --main-ref HEAD` at S2_pre and S2_post (15:47); PID 11276 `rc_probe.py` at S9. S3_pre has no [PROC]; S4_pre and S6_pre have only the Gradle daemon 44084 and the Kotlin daemon 14180. No foreign process overlapped a leg. The legs read only their own worktree copies (V2: e3415684 / 52229e1e in both legs). | LOW (D4) |
| 15 | shared Gradle / Kotlin daemons across legs | CONFIRMED; no effect on outputs | legA log: "Starting a Gradle Daemon"; legB log: no daemon line; S4_pre PIDs 44084 / 14180; `> Task :compileKotlin` executed (not UP-TO-DATE) in both | B reused A's daemons. The compile ran in each leg's own build/ (V3 separates them); bootRun is a forked JVM. The drift exists in A/A' without any B involvement. | LOW (D5) |
| 16 | probe TOML LF vs CRLF | CONFIRMED benign | python: CR-stripped unified diff of `git show 6b9fc7c:experiment_configs/topic_partition/ag_news_smoke_s42.toml` (blob efd82bda = the arm pin) vs probe_lcb.toml | exactly 2 lines differ (datasetType AG_NEWS -> LIVECODEBENCH; outputDir -> experiment_results/d9_probe_B). S6_tomldiff.txt's 67-line diff is a rendering artefact; the $ST copy is byte-equal to $SP\probe_lcb.toml. | LOW (D6) |

Scripts (scratchpad `postrun_d9\`): `recompute.py` (4-way per-file hashes with my own drop logic), `ledger.py` (tuning_ledger column diff).

## The non-determinism: code-level cause (a62c7e0; blobs unchanged to 6b9fc7c and to HEAD)

Proof that the path is untouched by the change:
- `git diff --name-only a62c7e0 6b9fc7c -- src/main | wc -l` = 4: TaxonomyConfig.kt (enum constant appended), CorpusRegistry.kt (offset appended), CorpusSource.kt (one `when` branch), MMLUDatasetFetcher.kt (+99: `lcbWorkDirGuard`, `fetchLiveCodeBench`, `LcbWorkDirGuardState`). All four sit on the dataset-type branch, which AG_NEWS never reaches.
- `git diff --name-only a62c7e0 HEAD` over TaxonomyMetrics.kt, AdditionalMetrics.kt, HierarchicalMetrics.kt, StatisticsUtils.kt, TaxonomyOperations.kt, GraphNode.kt and HeadlessBenchmarkRunner.kt = 0 files.

The chain:
1. **Source of the order.** `TaxonomyOperations.reassignQueries` (L278 ff.) splits the embeddings into chunks and runs each chunk as `async(Dispatchers.Default)`. Under `synchronized(leaf.queryWeights)` it does `leaf.queries.add(emb)` (L309; also L336, L348). `GraphNode.queries` is `Collections.synchronizedList(ArrayList())` (GraphNode.kt L41). The MEMBERSHIP and the weights are deterministic; the list ORDER is thread-completion order. Every caller: TaxonomyEngine L396; TaxonomyMerger L855, L874, L898, L905; TaxonomyOperations L698, L913, L942.
   - dag_snapshots.jsonl carries counts only (`directQueries`, `subtreeQueries`, `residualQueries`; 144 keys each), not the query order. That is why it is byte-identical while the order varies.
   - P7-FIX (cd037c0, 2026-09-10; `utils/OrderedSums.kt`) ordered the construction-path reductions. It did not touch the evaluation metrics: `grep -c -E 'orderedSum|sorted'` = 0 in AdditionalMetrics.kt and in HierarchicalMetrics.kt.
2. **How the order reaches the report.** `TaxonomyMetrics.generateReport` (TaxonomyMetrics.kt L113 ff.) fills `queryToEmbeddings` (a LinkedHashMap, L123) and `queryToLeavesList` by iterating `leaf.queries`. `uniqueQueryTexts = queryToEmbeddings.keys.toList()` (L186), so the report inherits the thread order.
3. **TotalDasguptaCost** (TaxonomyMetrics L314 -> AdditionalMetrics.kt L100-L149).
   - `points` keeps the input order. m = 1,400 gives C(m,2) = 979,300 pairs, above `maxPairs` = 5,000, so the SAMPLED branch runs: `Random(0)` draws INDICES i, j.
   - The same seed over a permuted list therefore picks different pairs, and the output is a different Monte-Carlo estimate. This is SAMPLING noise, not rounding.
   - Observed: 4 runs, CV 0.085%, range 0.151%; A-B 0.0042%, A'-A 0.141%, REF-A 0.147%.
4. **DendrogramPurity** (TaxonomyMetrics L274 -> HierarchicalMetrics.kt L98 ff.). The computation is exact over all same-label pairs, but `pureSum += match/seen` accumulates in `queryAssignments.keys` order (queryToPrimaryLeaf, a LinkedHashMap in `leaf.queries` order), so floating-point summation order varies. Observed range 8.8e-15, about 80 ulp.
5. **SphericalSilhouette** (TaxonomyMetrics L282 -> StatisticsUtils.kt L564 ff.). `queries = depthLeaves.flatMap { it.queries }` gives `silhouetteSum` in list order. Observed spread 2.8e-17 (1 run of 4 differs).
6. **Why the other fields are equal:**
   - WeightedLeafPurity uses integer counts;
   - NormalisedSackin is structural;
   - SeparationJ is computed on `corpusByText` and was equal in 4 of 4 runs. I did not audit why.
7. **Same mechanism, not measured here:** `computeTripletAccuracy` (AdditionalMetrics.kt L235, `Random(seed)` at L248) samples the same order-dependent list. It is not in the C1 CSV.

Empirical support: 3 runs at a62c7e0 on byte-identical input copies (the A' leg; the new A; and, on another commit with an identical `src/main` (89495507), the 09-22 REF) give 3 distinct TDC values. So the drift is run-to-run, and it needs no change and no input difference.

The delta READY's D4 guess ("input-state dependence", cold vs warm) is SUPERSEDED: REF(cold)-A, 0.147%, is the same size as A'-A (warm/warm), 0.141%.

The mechanism was identified by reading the code. It was NOT proven by an instrumented run. The fix in follow-up B below would test it.

## What D9 can and cannot conclude

CAN (descriptive, not C1):
- **Inertness on the deterministic outputs.** The change is shown inert on every compared output that is deterministic in 4 of 4 runs:
  - 19 of 21 files;
  - the C1-R2 file set;
  - reserved_pool (600 rows) and reserved_pool_meta;
  - within the two failing files, the rows SeparationJ, WeightedLeafPurity and NormalisedSackinIndex, and every tuning_ledger column except DP, SS, TDC and CommitSHA.
- **The drifting metrics.** The A-B distance (TDC 0.0042%, DP 6.7e-15, SS 2.8e-17) lies inside the A/A' distance (TDC 0.141%, DP 8.7e-15, SS 0). This is n = 1 pair each and is descriptive only.
- **The probe.** The new classes EXECUTED (V3; S6' refusal text only 6b9fc7c can produce). The AG_NEWS path at 6b9fc7c reached `bootRun` and wrote all 24 outputs.

CANNOT:
- **"C1 HELD".** C1 is FAILED as registered (the count of differing files is 2) and stays FAILED.
- **"C1 held on 19 files" as the D9 outcome.** Restricting C1 to the 19 files after seeing the data is CRITERION SUBSTITUTION (C-7). It must be labelled SUBSTITUTED and never promoted to DISCHARGED.
- **"The change moved the numbers".** R9 plus the code cause rule this out as the reading of the failure.

Can C1 be read at all?
- It is read as registered: FAILED.
- Under the registered interpretation, R9 converts that into "non-determinism; D9 open".
- C1 is uninformative about the change on 2 of its 21 objects, because those objects are non-deterministic by construction. As registered, C1 could never have HELD on this arm (see D1).

Scoring as registered:
- P1 FAILED.
- P2 HELD (p18579549e6d95873 in both legs).
- P3 HELD as transcribed (A 0/0/0; B 4/2/1).
- P4 HELD (0/0).
- P5 FAILED (warm cache).
- FALSIFIER: FIRED on its trigger (C1 FAILED). Its "overturns the channel audit" consequence is NOT supported: the registered A' arbitration reads non-determinism.
- Merge: none (L18868: "On C1 FAILED: no merge").

## Defects

- **D1 (HIGH, registration defect; owned by the D9 registration, READY bf3fa81 and delta READY 5f7e383): C1 was unreachable at any budget as registered.**
  - Its denominator includes MAIN_taxonomy_quality.csv and tuning_ledger.csv. The record already showed both drifting run-to-run: FRAMEWORK.md L297 (8d77f7b, 2026-09-15) "quality CSV drift 0.58%"; campaign_review_2026-09-10.md L252 (2026-09-14).
  - Support (g) called determinism "AN ASSUMPTION" without checking the record's own determinism row.
  - `grep -n -i -E "P7|campaign_review|evaluation path|cd037c0"` over the registration span L18662-L18872 gives 0 hits; `grep -c "taxonomy_quality"` in READY_lcb_d9.md gives 0.
  - Fix: a registrar bracket at L18857 (g) and on the D4 disclosure in L19558 ("input-state dependence" SUPERSEDED: run-to-run non-determinism; the code cause per this review). D9b below.
- **D2 (MEDIUM, engine; pre-existing, OPEN since 2026-09-14 and ungated): three evaluation metrics depend on the order of a list filled by parallel routing.** The sampled TDC carries real estimator noise (0.1-0.6%), not only rounding. Fix: follow-up B, as its own registered change.
- **D3 (LOW): the main embeddings_cache.db-shm mtime is bumped by the operator's own `[PIN mode=ro]` reads** (S0' 15:46:21 -> shm 15:46:30; S12 15:55:21 -> 15:55:29). Content is unchanged. Fix: file-level pins with `immutable=1` only, or record the -shm as expected-to-move.
- **D4 (LOW): foreign processes in the rule-7 window.**
  - `archv2_pilot/selftest.py --main-ref HEAD` ran at S2. It is a --selftest and admitted under W1-W5 while FREE; W1 was FREE.
  - `rc_probe.py` ran at S9. It is not a --selftest and is not admitted by rule 7.
  - Neither overlapped S3 or S4, and the legs read only their own copies. So there was no effect, but it is a rule-7 deviation to record.
- **D5 (LOW): legs A and B shared a Gradle daemon and a Kotlin compile daemon** (against the spirit of the "cold compile" at L18757). compileKotlin executed in both legs, and V3 separates the class dirs. No effect.
- **D6 (LOW): S6_tomldiff.txt compared the LF probe against a CRLF rendering**, giving 67 differing lines. The CR-stripped diff has exactly the 2 registered lines. Fix: compare CR-stripped, or against `git show`.
- **D7 (LOW): S9's first `gradlew --stop` ran from the wrong directory** ("'gradlew.bat' n'est pas reconnu"). The second attempt stopped 1 daemon. The Kotlin daemon 14180 was still alive at S9.
- **D8 (LOW): V3 cannot be re-derived after the run.** The worktrees were removed at S12 and no class-file list was kept. Fix for D9b: save `grep -rlaF` file NAMES per identifier into evidence before removal.

## Recommended follow-up (the smallest honest close; zero calls)

**A. D9b, a new registration (recommended now).**
- C1' = byte identity, A vs B, on:
  - the 19 deterministic files;
  - the file set;
  - both reserved_pool* tables;
  - MAIN_taxonomy_quality.csv and tuning_ledger.csv with the 3 DECLARED-NON-DETERMINISTIC fields dropped (DendrogramPurity, SphericalSilhouette, TotalDasguptaCost). Their exclusion is justified by the record (FRAMEWORK L297; R9; this review's code cause), not by this run's A/B values.
- Run on FRESH legs (new A and B worktrees, fresh $ST), under the delta READY 1 procedure unchanged except for:
  - the compare's drop list;
  - D8's class-list preservation;
  - D6's CR-stripped TOML diff.
- A fresh pair is required: the drop list is chosen AFTER seeing this run, so scoring it on these outputs would be C-7 (SUBSTITUTED).
- Optional descriptive rows: the 3 dropped fields for A and B beside the A/A' spread; no bar.
- Cost, measured on this run:
  - S2 copies about 1 min (15:46:21 -> 15:47);
  - leg A 59 s and leg B 42 s (START-END in the exit files; each includes a compileKotlin);
  - compare under 1 min;
  - probes 5 s each;
  - total about 4-5 CPU-minutes of active machine time inside a 15-minute rule-7 window;
  - 0 calls, 0 cce, no author decision (no merge until C1' HELD).

**B. EVAL-METRIC-DETERMINISM, a separate registered engine change (queue it; not a D9 prerequisite).**
- Sort `points` by rawText before sampling in `computeTotalDasguptaCost` and `computeTripletAccuracy`.
- Iterate `queryAssignments` / `queries` in sorted rawText order in `dagDendrogramPurity` and in the silhouette block, or sort `uniqueQueryTexts` and `queryToPrimaryLeaf` once in generateReport.
- It changes every future TDC, DP and SS value (a different sample), so it needs its own golden test, a 3-replicate byte-identity check of MAIN_taxonomy_quality.csv, and a disclosure that post-fix values are not comparable digit-for-digit with prior ones.
- Cost: engine-coder about 1 h; `gradlew test --offline` about 1 min; 3 AG smoke replicate builds about 3 min CPU; 0 calls. After B, a D9-style C1 on the full 21 files becomes reachable.

**C. N-replicate A/A vs A/B distribution: NOT recommended.** D9 is a byte test of a dataset-branch change, not a test of TDC. A distributional test on a Monte-Carlo estimator answers a different question.

## Prior recorded numbers that may carry this jitter

- **On disk:**
  - `find experiment_results -name MAIN_taxonomy_quality.csv -not -path "*/_backup/*" | wc -l` = 149 files across 29 run families. The largest are h9_sweep 34, anchorfree 20, hygiene 12, multicorpus 10, dimsweep 10, splitratio 8, perf_replay 8. 17 are git-tracked (`git ls-files | grep -c`).
  - tuning_ledger.csv copies: 13 tracked.
  - The same metrics appear in `*_thesis_metrics.csv/json` (tracked: arena_math_frozen, arena_math_paired) and in the snapshot metadata (TaxonomySnapshotManager stores dendrogramPurity, sphericalSilhouette and totalDasguptaCost per snapshot).
  - The `*_BASELINE_taxonomy_quality.csv` files (cal_iso: KMEANS, WARD, RANDOMNULL) use the same metric code. Whether their leaf.queries order is also thread-dependent is NOT verified.
- **In the prose record:** `git grep -l` for DendrogramPurity / TotalDasguptaCost / Dasgupta over docs/ and report/ finds no numeric TDC, DP or SS value except the D9 records themselves and the P7 caveat. The thesis appendix C (C_Metric_Definitions.tex L109-L119) only DEFINES the sampled estimator.
- **Magnitude:**
  - TDC: CV 0.085% on the AG smoke (m = 1,400; 4 runs, range 0.151%). On bareq512 (hygiene labelfree10/11/12, recomputed here: 6.32024797272398E10 / 6.3315516862810326E10 / 6.2952338063323456E10) the CV is 0.29% and the range 0.577% (the record's 0.58%).
  - DP: about 1e-14 absolute. SS: about 1e-16 or less.
  - Consequence: any cross-build comparison or Pareto decision that relies on a TDC difference smaller than about 0.6% (tools/tuning/pareto.py minimises TotalDasguptaCost) is within noise. Only a DP or SS difference in the last 2 digits is noise.
  - Builds before cd037c0 also had STRUCTURAL non-determinism, so their metric differences mix both sources.
- **Nothing recorded is revised by this review.** The registrar may add a dated bracket on FRAMEWORK L297, naming the code cause and TDC as a sampled estimator with a seed-fixed but order-dependent sample.

## What this review does not show

- The V3 class counts, by my own count (the worktrees are gone; transcribed from the pinned checker's output).
- The mechanism by an instrumented run (it is identified in code and consistent with 4 runs; follow-up B would demonstrate it).
- That SeparationJ is deterministic in general (equal in 4 of 4 runs here).
- That the cal_iso baseline quality CSVs carry the jitter.
