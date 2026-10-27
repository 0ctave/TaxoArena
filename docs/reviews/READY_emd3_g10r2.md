# READY review 2026-10-01: eval-metric-det3 b2e1aed (EVAL-METRIC-DETERMINISM) and g10-r2 acb993c (ARCH-V2-E-T-R2 comparator)

Adversarial-reviewer. Zero calls, no construction. JVM: two Gradle runs (`--no-daemon`) in throw-away detached worktrees,
removed afterwards; `gradlew --stop` reports no daemon. HEAD of main 174b4abf; ledger unchanged (v323). Registrations: EMD
prog L20311-L20389; ARCH-V2-E-T-R2 prog L22417-L22434 (both _as_of 174b4abf). Prior review: READY_backfill_2026-09-30.md
(b938c14) B-EM-1 / B-EM-2. Its M1 (scope) and M2 (E1-E4 static reading) are CONFIRMED there on the same four blobs, and
they are not re-derived here.

## VERDICT

| branch | READY? | MERGEABLE? |
|---|---|---|
| eval-metric-det3 b2e1aed (BASE 2f080e0, FIX 6569cd3) | **READY for the five-leg run** (B-EM-1 and B-EM-2 discharged) | **NOT YET, by registration.** L20382 says merge only on "DONE, MERGEABLE" after the legs. The merge is clean: `git diff --name-only 2f080e0 main -- src build.gradle.kts` = 0 lines. Condition C-EM-2 applies. |
| g10-r2 acb993c (one file, g10_compare.py blob:1f1e20a9) | READY as R2's G10 comparator | **MERGEABLE** by path (clean `merge-tree` onto main) under C-G-1 |

**Does EMD fix the RP12 G10 drift?** YES at code level, NOT yet shown by a run on the RP12 arms. On the R1 artefacts,
apply g10-r2's transforms (A2 TOML sha stripped, A4 membership as sets). What still differs across all 7 B0/B0' pairs is then
exactly:
- A3: one file, MAIN_taxonomy_quality.csv, rows TotalDasguptaCost, SphericalSilhouette and DendrogramPurity;
- A4: snapshot metrics totalDasguptaCost, tripletAccuracy and sphericalSilhouette.

Every one of these is produced by generateReport through the four canonicalised sites (E1-E4). Nothing else differs.

**Does EMD leave the per-node queryId order unchanged?** YES:
- the src/main diff is the 3 metric files only;
- every sort returns a NEW list (`sortedWith`, `sorted`, `flatMap`), so `leaf.queries` is never mutated;
- TaxonomyOperations.kt and GraphNode.kt are untouched.

This is what C3 requires. So A4's stored order stays thread-dependent, and R2 needs ruling (A). g10-r2 implements it.

**Can R2 proceed? Must EMD's five-leg run come first?** YES, the five-leg run comes first. R2's D-8 (L22422) requires all four
builds from ONE commit that contains the MERGED EMD, and EMD merges only on DONE. The order is:
1. EMD five-leg window (rule 7).
2. EMD outcome DONE.
3. Merge by path (C-EM-2).
4. Registrar records ruling (A) and this READY.
5. g10-r2 merged.
6. One pinned commit containing both.
7. B0, B0', o1, o2 builds.
8. G10.

R2-2 (the MMLU-GOLD-GEOMETRY post-run review) gates G12's read, not the builds. The EMD legs and the R2 builds never share a
rule-7 window.

## Per-claim table (deciding claims)

| # | claim | mine | status | sev |
|---|---|---|---|---|
| E1 | FIX suite 515 tests, 2 failures = the two known | 515 / 2 failed / 0 err / 0 skipped; failures MrlRoutingTest.testMrlConfigDefaults, TraceEnvelopeUnwrapTest "no model has a wholly blank trace column"; golden 8/8 pass (fresh detached worktree at 6569cd3, `cleanTest test --offline --no-build-cache --no-daemon`, 2 m 20 s) | CONFIRMED | — |
| E2 | golden on BASE 2f080e0: 7/8 fail, TDC sampled among them (C2 non-vacuity) | 8 tests / 7 failed; tdcSampledPermutationInvariant FAILS, so does tripletAccuracyPermutationInvariant; only mainFixtureIsNonDegenerate passes | CONFIRMED | — |
| E3 | X1 = 3 = X1_DECLARED_COUNT | `grep -rlaF canonicalByRawText build/classes/kotlin/main`: FIX 3 (AdditionalMetricsKt, HierarchicalMetricsKt, TaxonomyMetrics), BASE 0 | CONFIRMED | — |
| E4 | scope: src/main = 3 metric files + test A; harness commits touch no src/tools/configs | `diff --name-status 2f080e0 6569cd3` = 3 M + 1 A; `6569cd3..b2e1aed` = 17 files, all under experiment_results/eval_metric_det/, 0 under src/tools/experiment_configs/build files; blobs = READY_backfill's (c908caf5, 4af03144, 930adb43, 45d8f0ab) | CONFIRMED | — |
| E5 | B-EM-1 (1)-(6): BASE/FIX re-cut, -PjvmThreads=12 in every leg, TC witness required and equal, X1 re-measured, V2 pins re-read | emd_common BASE 2f080e0 / FIX 6569cd3; legs check out 6569cd3, never the tip (EMD_STEPS L31-L37); legrun bootRun carries -PjvmThreads=12; leg_check TC = every [THREAD-CAP] line `requested=12 availableProcessors=12`; compare requires equality across 5 legs; ThreadCap.kt at BASE prints that line; build.gradle.kts at BASE has jvmThreads (count 9). Main's inputs now: ag_news_smoke_cache_v1.db e3415684… (1,748,992 B), -wal 0 B (e3b0c442…), embeddings_cache.db 52229e1e… = AG_BASE / EMB_BASE | CONFIRMED | — |
| E6 | harness selftest 184/184, mutants 97/97 killed | 184 of 184 (12 s); `emd_mutants.py`: 97 run, 97 killed, baseline PASS (18 m 38 s); worktree clean afterwards (0 porcelain lines) | CONFIRMED | — |
| E7 | EMD canonicalises the RP12 drift sources | R1 data, after the R2 transforms: residual = TDC/TA/SS (A4) + TDC/SS/DP rows (A3) only, 7/7 pairs; 9 of 10 (graft 14 of 15) validation files byte-equal per pair | CONFIRMED (code + R1 artefacts; the run is R2's G10) | — |
| G1 | A2: only split_v2.configSha256Lf stripped | R1 gate_ids: raw equal 0/6, stripped equal 6/6; own mutant G1 (drop all split_v2) killed | CONFIRMED | — |
| G2 | graft pair: A1/A2 N/A, A3-A5 compared; member without dag_snapshots refuses | R1: graft_flatleaf has no dag_snapshots.jsonl / gate_ids.json in B0 and B0'; `unionSnapshots` line count 1 in both graft config.toml, 0 in all 12 member TOMLs; own G2 (is_graft always True) killed | CONFIRMED | — |
| G3 | A4: queryIds per node as a set, everything else exact | R1 rows through `membership_as_sets` + `strip_stamp_toml`: graph equal in 7/7 pairs, residual only the three metric keys; 0 of 439 nodes carry a duplicate queryId; own G3 (childIds also sorted) and G4 (set transform removed) killed; selftest 15/15 | CONFIRMED | LOW (D-G-2) |
| S | Support (EMD) non-vacuous | DEFF N/A declared (byte/bit compares). 0.05^(1/9) = 0.7169 (the registered 0.717); 1 - 0.2^(1/3) = 0.4152 (the registered 0.415); margin 2.8 x 0.292 = 0.818 -> 1.0%. R2's G10 is a deterministic set readout (Support (b)-(f) carried over) | CONFIRMED | — |

## Pins (LF of record; the working tree's CRLF beside where it differs)

- FIX 6569cd31ead59b2f822ab5c2b91347443e1cd378; BASE 2f080e079f79c62c3a38337005438c6a310be81b.
- AdditionalMetrics.kt blob:c908caf5 lf16:2367a3bbb940f3c0 crlf16:8716440189285fb8.
- HierarchicalMetrics.kt blob:4af03144 lf16:85f75032350c6688 crlf16:5b59ef521698ee50.
- TaxonomyMetrics.kt blob:930adb43 lf16:45a1931d95dceadb crlf16:b0a2ce4c6132d985.
- EvalMetricDeterminismTest.kt blob:45d8f0ab lf16:46aa0389e67c7df4 crlf16:b79f0b5fc34ab819.
- Harness at b2e1aed. The working tree is LF, identical to the blobs:
  - emd_common.py 2ba97aad (lf16 c583e0d113b40101);
  - emd_compare.py ef20e6ee (e5ba1be781c25fe3);
  - emd_leg_check.py 19df579f (a0060fc00d3503e7);
  - emd_legrun.cmd a9c70e83 (bcc8c6b35899861d; LF, no labels or goto; selftest T11d executes it);
  - emd_prep.py c4a447d3 (a65ffbae9c4f15c3);
  - emd_selftest.py cbf5bfb1 (c48554cfcc60a773);
  - emd_mutants.py 5c78e40a (b3ca61954a39017a);
  - emd_w1.ps1 369de961 (796ce2dc95eb97e8);
  - EMD_STEPS.txt daf060fe (d9d74a8852685245).
- g10_compare.py blob:1f1e20a9bdd5c82040222afdc91bd5dc98fe4d75, lf16:ccf1942ef4b17c4d. The working tree is LF (0 CR lines).

## Defects and conditions

- **C-EM-1 (condition, rule 7).** The five legs plus the suite plus the golden-on-BASE run take one W1-W5 window of about 25 min, with:
  - no RP12 build or construction running;
  - no pool reader;
  - no other heavy process (Ollama idle at review time).
- **C-EM-2 (condition, merge).** Merge by path, in one commit, only on DONE, MERGEABLE (C1, C2, C3 HELD; V1-V10 and TC met). Re-check:
  - `git diff --name-only 2f080e0 main -- src/main` = 0 at merge time (else re-run);
  - `git diff --name-only 2f080e0 6569cd3` unchanged;
  - the ancestry check after the commit.
  The harness stays an experiment_results/ record, not part of the src merge.
- **D-EM-3 (LOW, comment).** emd_common.py L32 still says "RE-MEASURE OWED at FIX". The value of record (3) is now measured (E3). Fix: one insertion bracket at the next harness touch; not before the legs (it would move a pinned blob).
- **D-EM-4 (LOW, scope disclosure, carried from registration (g)).** The latent order-dependent writers stay out of scope:
  - bridge TopRepresentativeQueries;
  - KappaShrinkageMean;
  - partition ties;
  - the ARI / edgeF1 / hF1 snapshot fields.
  On R1 these were equal in 7/7 pairs. R2's G10 is their only test on the v2 arms. A G10 R2 FAILED on one of them is a new source (F2 of R2), not EMD's F1.
- **C-G-1 (condition, record).** The orchestrator's ruling (A) on R2-1 exists only in the brief and in acb993c's message. Before any R2 build, the registrar records it in the programme, pre-data, insertion only, and clears R2-1.
- **D-G-2 (LOW).** `membership_as_sets` uses `sorted(set(...))`, which also discards multiplicity. A node that gained a duplicate queryId would pass A4. On R1, 0 of 439 nodes have one. Fix (optional, consistent with ruling (A), "order stripped"): compare `sorted(queryIds)` as a multiset, and add a selftest case `[3,1,2,2]` vs `[3,1,2]` -> FAILED. Otherwise the outcome discloses "set, multiplicity not compared".

## Own mutants (deciding paths)

- H1 emd_compare `c1_held = n_c1 == 0` -> `<= 1`: KILLED (3 mismatches). Decisive (C1).
- H2 emd_leg_check TC `all(` -> `any(`: KILLED (1). Decisive (TC).
- H3 emd_compare V3 without `x1[P] == 0`: KILLED (1). Decisive (the execution discriminator).
- G1 strip_gate_toml drops all of split_v2: KILLED (14/15). Decisive (A2).
- G2 is_graft_toml returns True: KILLED (6/15). Decisive.
- G3 membership_as_sets also sorts childIds: KILLED (14/15). Decisive (A4 stays exact).
- G4 set transform removed from A4: KILLED (14/15). Decisive.

## Commands (repo root Z:\FAC\TUBerlin\THESIS\TaxoArena; bash; scratch = session scratchpad)

```
git diff --name-status 2f080e0 6569cd3; git diff --name-status 6569cd3 b2e1aed | wc -l    # 4; 17 (all experiment_results/eval_metric_det/)
git diff --name-only 2f080e0 main -- src build.gradle.kts | wc -l                         # 0
git merge-tree --write-tree main acb993c4 && echo clean                                    # clean
git worktree add --detach .claude/worktrees/rev-emd3-fix 6569cd3; ./gradlew.bat cleanTest test --offline --no-build-cache --no-daemon   # XML: 515/2
git worktree add --detach .claude/worktrees/rev-emd3-base 2f080e0; git show 6569cd3:src/test/.../EvalMetricDeterminismTest.kt > <base>/...;
  ./gradlew.bat cleanTest test --offline --no-build-cache --no-daemon --tests taxonomy.EvalMetricDeterminismTest       # 8/7 failed
grep -rlaF canonicalByRawText build/classes/kotlin/main | wc -l                          # FIX 3, BASE 0
sha256sum ag_news_smoke_cache_v1.db* embeddings_cache.db                                  # = AG_BASE / EMB_BASE
python emd_selftest.py --selftest --work <scratch>; python emd_mutants.py                 # 184/184; 97/97 killed
python scratch/r1check.py   # g10r2 transforms on rp12-b0-run/snapshots.db (immutable=1; -wal 0 B; sha256 9b60cf65... before = after)
for m in ...; cmp B0/$m/.../validation/*.csv B0p/...                                      # 1 differing file per pair (quality CSV)
python tools/analysis/g10_compare.py --selftest                                           # 15/15; mutants G1-G4 via scratch copies
python -c "print(0.05**(1/9), 1-0.2**(1/3), 2.8*0.292)"                                   # 0.7169 0.4152 0.8176
```
Main's DBs are unchanged (mtimes: embeddings_cache.db 09-23 14:33, snapshots.db 09-23 04:34, ag_news_smoke_cache_v1.db 09-27 16:25).
Both review worktrees were removed; `git worktree list | grep -c rev-emd3` = 0.
