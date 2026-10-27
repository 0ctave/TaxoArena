# READY review: branch emb-target2 (789471d C-ET-1/3/4, f667d6b C-ET-5), delta on READY_emb_target (6202766)

Adversarial reviewer, 2026-09-29. Zero calls, no real embed, no Ollama contacted, no DB of record opened (probes on
scratch fixtures only). Worktree `.claude/worktrees/emb-target2`, tip f667d6b on 380e965; main is still 380e965
(`git log 380e965..main` empty), so a by-path merge is conflict-free. Delta review: `git diff 380e965..f667d6b` (9 files,
+432/-9); what READY_emb_target CONFIRMED on untouched code is cited, not re-derived.

## VERDICT

| commit | MERGEABLE | READY for |
|---|---|---|
| 789471d (embedder_arms, flat_mix_mmlu arm-copy gate, flat_generality re-pin, arm pin file) | MERGEABLE | READY-WITH-CONDITIONS for the three writes, all `--target-dir experiment_results/embedder_cross --go`: (1) `--embed-missing gemma_raw --expect-missing 3504`, (2) `--embed-card gemma_card`, (3) `--embed-card nomic_card` (conditions W-1..W-5). C-ET-1 CLOSED, C-ET-3 and C-ET-4 CLOSED in mechanism; C-ET-2 still open (LOW). |
| f667d6b (JVM `-Dtaxoarena.embeddingCacheFile`) | MERGEABLE (inert with the property absent) | Not needed by writes 1-3. NOT READY for E1 N-card through a DIR file (C-ET2-1 HIGH). |

## PINS (LF of record = `git rev-parse f667d6b:<f>` = `git hash-object`; the working tree is CRLF except the .json)

| file | blob | sha256-lf16 | sha256-crlf16 |
|---|---|---|---|
| tools/analysis/embedder_arms.py | c8940349ea410eef0bb69c30ecea81a0e4208820 | 1c432baba8779fd3 | ff1eea4df8457a45 |
| tools/analysis/flat_mix_mmlu.py | 555ae3ac31b2f27ea040e4bb6a9b20be0eeeecd2 | b80cec50c2eef49d (= FLAT_MIX_PIN) | 57413483afaf7aa1 |
| tools/analysis/flat_generality.py | 0acfb5402dce62b76f70c8664abd0e5e9c40b92c | 351edd080847a9c6 | e3eb58a353754326 |
| experiment_configs/embedder_cross_arm_pins.json | b475ec2a74bc5c52813d2d4ad54833233fe70055 | 5057a9890aed9de0 (wt is LF) | ec0c79c42a5b1f0e |
| src/main/kotlin/taxonomy/dataset/EmbeddingCache.kt | 08128b984bdc6cf7daecfd85634ecbd854b660c4 | f525dfefeb2ee6e6 | 617d42bcebf56e3a |
| src/main/kotlin/taxonomy/diagnostics/DiagnosticsBundle.kt | a53780f9f6c9a0e0476735e00d31f03d877c97be | 1d119d04b795cd9e | 297fff2e7a0ae094 |
| src/main/kotlin/taxonomy/runner/HeadlessBenchmarkRunner.kt | d3f9f5e5d54ac18d5d177ab6e9478f3481ad681f | f040ed3eb854b23b | 421178bf5a4e0cc3 |
| build.gradle.kts | 982cbbba2daee3e5be7d5eb141526e12f0d64ddf | e6e7e5f35122b65e | eeedbd769d32f5d1 |
| src/test/kotlin/taxonomy/dataset/EmbeddingCacheExplicitFileTest.kt | f2b41c1153043f251bcadfc386624fb06020c372 | 6fa65b3bd427d0cd | 932a6466bda5c0df |

All Kotlin pins equal f667d6b's commit message. Hygiene: `git diff --name-only 380e965..f667d6b | grep -cE "application.yml|\.env|\.gitignore"` = 0; `| grep -c experiment_results/` = 0.

## PER-CLAIM TABLE (deciding claims only)

| # | claim | my result | status | sev |
|---|---|---|---|---|
| 1 | Selftests / mutants | embedder_arms 86 checks rc 0; mutants 61/61 KILLED (`grep -c SURVIVED` = 0); flat_mix 103 checks, 46/46 KILLED; flat_generality 95 checks, 40/40 KILLED; flat_generality --inertness "INERTNESS PROVED" vs c5cc7934 | CONFIRMED | - |
| 2 | Absent --target-dir inert (embedder_arms) | `--inertness` rc 0, INERT, leg B executed new code (check_target_flag 11, run_embed 10, resolve_target 10, target_dir None) | CONFIRMED | - |
| 3 | C-ET-1: exclusive create closes the race | raw: `_copy_exclusive` opens `xb`; card: `open(path,"xb")` under --go before any post, after the dry-run return (embed_card L1103-L1112). Selftest plants a file during parity (raw) and after the check (card): REFUSED, planted bytes intact, no further posts; mutants ET1 'wb'/'ab' KILLED | CONFIRMED (closes C-ET-1) | - |
| 4 | C-ET-3: flat_mix `--embedding-cache-file <DIR copy>` refuses; open_arm_reader is the only E0b entry | FT-EMBGUARD/EA-TREADER refuse a card file, a provenance-adjacent file, any file under DATA_ROOT/experiment_results/embedder_cross, and `main --dry-run` on the DIR copy. Own PM1 (admission compare replaced by `ARM_COPY_ADMITTED is None`: any token admits ANY arm file) SURVIVED both selftests: no check that a token for path A refuses path B. Exposure nil today (token set only inside configure_arm_copy's own call, cleared in finally) | CONFIRMED; test gap | LOW |
| 5 | C-ET-4: registrar pin, committed all-null, every read refuses | pin file: 4 arms, sha256 null, schema v1; registrar_pin refuses absent/other schema/null/mismatch (EA-TREADER, EA-PINFILE; mutants ET4 x5 KILLED) | CONFIRMED | - |
| 6 | flat_mix change breaks no existing pinned read | Only flat_generality pins flat_mix by blob (`git grep -c cdb354f f667d6b -- tools` = 2 lines, both the bracketed old pin in flat_generality); re-pin equals the LF sha. is_arm_copy on the real main-root paths (no DB opened): embeddings_cache.db, the root nomic and gemma files -> False (the P-2 (vi) legs of embedder_guard and RP07's root reads unaffected); DIR files -> True | CONFIRMED | - |
| 7 | FLAT-GENERALITY record (61c99ad) unaffected | 0 files of the record touched. BUT the committed state metas carry script 44ca378e + flat_mix cdb354f1; at f667d6b `ensure_meta` on a copy of state/af_clean_s42/meta.json REFUSES ("differs from this script's meta"); the only differing keys are those two pins. The outcome stands; a re-run/--analyze of that state is reproducible only at 61c99ad/380e965 (fail-closed, not silent); results JSON state "done", no owed step | PARTLY (record intact; reproduction route moves) | LOW |
| 8 | f667d6b byte-identical with the property absent | resolveCacheFile(m, null) == cacheFileFor(m) (test, 7 tags); own KM1 (absent branch returns the absolute path) KILLED. No -D forwarded by bootRun when absent; HeadlessBenchmarkRunner writes no manifest key when absent: by inspection only, own KM2 (key written unconditionally) SURVIVED the suite subset (no test). cardReadOnly false unless a model tag itself ends "__card" | CONFIRMED (manifest leg by inspection) | LOW |
| 9 | Card file read-only for vectors in the JVM | 4/4 new tests pass; a miss REFUSES, model calls 0; raw-named twin embeds (discriminator) | CONFIRMED | - |
| 10 | JVM on an explicit (pinned) file | Own probe (temporary test, deleted): a Python-made card file (rollback journal, like write_vectors) opened by EmbeddingCache for a pure HIT (0 misses): sha256 344e877d... -> 4396dc7b..., -wal and -shm created (journal_mode=WAL + CREATE TABLE IF NOT EXISTS gmm_vectors on init). Pointing the JVM at the registrar-pinned DIR copy changes it on open, not only on putQuery; resolveCacheFile checks name + existence, no pin, no provenance, no DIR; the manifest records the path, not a sha | REFUTES any E1 N-card use of the DIR copy | HIGH |
| 11 | Suite | `gradlew test --offline`: 474 tests, 2 failed = the two allowed (MrlRoutingTest.testMrlConfigDefaults, TraceEnvelopeUnwrapTest blank trace) | CONFIRMED | - |
| 12 | Stray DBs / tests near main | Worktree root holds embeddings_cache.db (+wal/shm), ratings.db, mmlu_pro_dataset_cache_v2.db, snapshots_test.db: all ignored, all row counts 0 (corpus_registry 1), mtime 15:22-15:23 = the suite's cwd (pre-existing Spring-context behaviour, not this branch). The K7 stray gemma DB is gone (`ls *.db*` in the worktree lists none). Main root: 21 DB entries' size+mtime identical before/after my full suite (diff empty); main gemma DB mtime 11:52 as the builder said. `git status --porcelain` in the worktree = 0 lines after my probes | CONFIRMED | - |

## OWN MUTANTS (4)

- KM1 resolveCacheFile(null) returns absolute path -> KILLED (absent-property test). decisive (claim 8).
- KM2 manifest key written even when the property is absent -> SURVIVED; not decisive (correct by inspection; LOW gap).
- PM1 flat_mix gate admits any arm file while any token is set -> SURVIVED; not decisive today (LOW gap, E0b condition).
- PR1 (probe, not a mutant) JVM open of a pinned card file -> file changed: decisive for C-ET2-1.

## DEFECTS / CONDITIONS

- W-1 (condition, writes 1-3): the operator's zero-call dry run of each write precedes its --go; write 1's `--expect-missing`
  equals the missing count that dry run prints (3504 per run log 532dd1d; not recomputed here: a pool reader). A mismatch stops.
- W-2 (condition): DIR today holds exactly 1 entry, `gemma_raw_embed_missing.log` (12:30, the connect-guard REFUSAL fixed in
  w0-delta3; ignored by .gitignore:91); no copy, no provenance. List DIR before and after each write: after = + the arm file +
  its provenance only. A failed card --go leaves a partial card file without provenance: the rerun REFUSES; remove it by hand,
  logged.
- W-3 (condition): no -wal/-shm beside the gemma source (main root today: none); one heavy process at a time; rule 7 window
  (needed_texts reads the pool); run from main after the merge (ARM_PINS_FILE resolves to the script's repo).
- W-4 (condition): the registrar fills `embedder_cross_arm_pins.json` by insertion from each run's printed sha256-after,
  checked against the provenance; never commit the DIR .db (C-ET-2 LOW, unchanged: `.gitignore:145` un-ignores it).
- W-5 (carried): C8-4 LOW, Y8-H LOW from READY_w0_delta3 (not re-derived).
- C-ET2-1 (HIGH, E1 N-card only): the JVM mutates any file it opens. Fix: never point `-Dtaxoarena.embeddingCacheFile` at a
  DIR copy; a pre-step copies the pinned DIR file to a per-run working file after checking its sha256 against the registrar
  pin, the JVM reads the working file, the manifest records the working file's source sha256 (add it to
  recordEmbeddingCacheFile), and the pinned DIR copy's sha256 is re-checked after the run. Needs its own registration + READY.
- C-ET2-2 (LOW): add a test that a HeadlessBenchmarkRunner manifest carries no `embedding_cache_file` key when the property is
  absent (kills KM2).
- C-ET2-3 (LOW): add to FT-EMBGUARD a case with ARM_COPY_ADMITTED naming path A while configure_embedding is given arm file B:
  REFUSED (kills PM1).
- C-ET2-4 (LOW, record): note in FLAT-GENERALITY's record that its state dirs re-verify only at 61c99ad/380e965.
- NOTE: main's embeddings_cache.db-shm mtime 2026-09-29 14:52 (a non-immutable WAL reader before this review; not this
  branch; pool_guard's -wal check stays the gate).

## E0b (EMBEDDER-CROSS-FLAT reader, not built): its build must satisfy

1. Every non-qwen3 arm is read only through `embedder_arms.open_arm_reader(FM, arm, DIR)`; qwen3 with no flag (R2).
2. It runs only after the registrar has filled all 4 pins; with any null it REFUSES (shown by execution on the committed file).
3. The nomic_raw DIR copy exists (a 4th write, `--embed-missing nomic_raw --expect-missing <its dry-run count> --target-dir
   DIR --go`: same code path as write 1, same W-conditions).
4. Its READY shows by execution that `flat_mix --embedding-cache-file <DIR file>` REFUSES and carries C-ET2-3's test.
5. No JVM read of a DIR file (C-ET2-1); the vmfMu/embedding guard on every arm; fit on TRAIN only (split rule 1; pool guard).
6. A Support section (deciding denominator, DEFF with its source, n_eff, SE arithmetic, MDE vs the bar) that reproduces.

## COMMANDS (compact)

```
cd .claude/worktrees/emb-target2; export TAXOARENA_DATA_ROOT=<scratch>/nodata OMP/OPENBLAS/MKL_NUM_THREADS=1
python tools/analysis/embedder_arms.py --selftest|--inertness|--mutants      # 86 ok; INERT; 61/61, grep -c SURVIVED 0
python tools/analysis/flat_mix_mmlu.py --selftest|--mutants                  # 103 ok; 46/46
python tools/analysis/flat_generality.py --selftest|--mutants|--inertness    # 95 ok; 40/40; INERTNESS PROVED
<scratch>/pm1: copy of tools/analysis + src/main + pin file, PM1 applied; both selftests PASSED (SURVIVED)
./gradlew.bat test --offline --tests EmbeddingCacheExplicitFileTest (KM1: 1 of 4 failed; KM2 with DiagnosticsBundleTest: PASS); reverted
temporary src/test/kotlin/zzreview/ZzReviewCardProbeTest.kt (deleted): ZZPROBE before=344e877d... after=4396dc7b..., +wal/+shm
./gradlew.bat test --offline                                                 # 474 completed, 2 failed (allowed)
ls -la --time-style=full-iso <main>/*.db *.db-* before/after the suite: diff empty (21 entries)
python -c "flat_generality.ensure_meta(<copy of state/af_clean_s42/meta.json dir>, SF_TREE, sf_spec())"   # REFUSED: differs
python -c "flat_mix_mmlu.is_arm_copy(...)" on the main-root paths (no DB opened)                         # False x3, DIR True
git rev-parse f667d6b:<f>; git hash-object <f>; git show f667d6b:<f> | sha256sum (| sed 's/$/\r/' for crlf16)
git check-ignore -v --no-index experiment_results/embedder_cross/<files>; git ls-files experiment_results/embedder_cross (0)
```
Reviewer's own side effect, reverted: a mis-rooted probe path wrote Z:\c\...\fgmeta\meta.json (12 entries, all created
15:32:42 by this review; removed; `ls /z/c` = absent). No repo file, no DB touched.
