# READY review: CERT-PLANTED (branch cert-planted, tip 8db7be3d; base 5312852a; amendment 2fc67857)

Reviewer: adversarial-reviewer, 2026-10-04. Zero calls. No null drawn: the planted statistic comes from the dry-run and my own
re-computation. The null comparators are CERT-PC-K2's committed SN replicates and a deterministic eigen proxy (no simulation).
Registration: docs/judge_v2_program.md L24304-L24315 (`_as_of` 4d2c5e41; heading "## Registered 2026-10-04 (before any code or
call) — CERT-PLANTED: ...").

## Verdict: NOT READY (one blocker; it needs a registrar bracket and a decision, no code change unless delta_dec moves)

The build is correct and inert. The plant implements the registered delta to the digit, the pins reproduce, the merge onto main is
clean and the suite passes. What is wrong is Support (f), the claim that delta 8 "sits about 1.8 x the plain-null p95, so the
predicted p_d there is about 1/301". The comparator in that claim (the delta-0 null p95, about 0.068) is not the null that a delta-8
site faces. The arm moment-matches each PL site's null to its own PLANTED rows: `cpcDeclaredSite(... vectors = cplUnit(planted
rows) ...)` -> `cpcMoments` -> `withinNodeCloud` (a Gaussian with the full sample covariance of those rows). So the planted
direction's inflated variance s^2 (1 + delta^2) is inside the null. The null grows with delta, and at delta 8 the planted
direction is the null's top eigen-direction. Rule: arithmetic that does not reproduce = NOT READY.

## Per-claim table (deciding claims only)

| # | claim | my number | verdict | sev |
|---|---|---|---|---|
| 1 | planted rows = unit(X +/- delta s u), u = Random(20261004+d) gauss, halves = Random(20261104+d) shuffle, s = SD ddof 0 (CPL-2/3) | own independent port from the cache (immutable=1) and CERT-PC-K2's site_labels.tsv: all 210 planted statistics equal the dry-run's, 0 of 210 differ > 1e-6 | CONFIRMED | - |
| 2 | dry-run pins: sites 14c626d5... (211 sites, 104,328 rows), vectors 2135279e... (199,342,080 B) | dry-run at 8db7be3d, data root rp12-r2-run: both "= the pin"; CERT-PC-K2 draw efcc4e99 rebuilt; cache sha256 afe21525..., mtime unchanged before/after | CONFIRMED | - |
| 3 | delta 8 above the plain-null p95 of about 0.068 | delta-8 planted statistic 0.0835-0.1475 at n 486 (0.0857-0.1526 at n 441); 30 of 30 delta-8 sites exceed their own population's delta-0 SN p95 (CERT-PC-K2 arm, 0.0667-0.0712) | CONFIRMED literally | - |
| 3b | Support (f): delta 8 = 1.8 x the null p95 -> p_d about 1/301; P2 delta 8 14 [10, 15] | wrong comparator (above). Top-eigen proxy (2/pi) lambda1/tr of the planted rows: delta 0 0.029-0.037, delta 8 0.056-0.100 (1.7-3.3 x). Calibrated two ways on the delta-0 null (SN p95 - proxy0 added, or SN p95 x proxy/proxy0), delta 8 at n 486 certifies 3/3/3 of 5 (additive: CP1 MIXED, delta* 10) or 0/0/0 (multiplicative: CP1 INSENSITIVE, F-CP fires). P2's 14 [10, 15] falls outside both | REFUTED (Support f/g) | BLOCKER |
| 4 | Support (b)-(e): DEFF 1.0 by construction, n_eff 300 per site, SE 0.0126, MDE80 0.0352 | sqrt(0.05 x 0.95 / 300) = 0.012583; 2.8 x 0.012583 = 0.03523 | CONFIRMED per site | - |
| 4b | deciding units: 5 subsamples per category | economics n 486: pairwise overlap 468-470 of 486 (dry-run OVERLAP line), so about 1 effective subsample; u_d is shared by the 3 categories of one draw (CPL-2). Support (c) gives n_eff per site only, not for the deciding count | PARTLY | MEDIUM |
| 5 | Kotlin additions only and inert | merged probe (main 61d1c5bf + 8db7be3d) against main, both compiled --no-build-cache: 1,336 main classes byte-identical; 50 pre-existing nested SeparationNullBySizeTest$* identical under javap -c -p (cp indices normalised); outer class 184 of 184 pre-existing members identical, 17 new (all cpl*/certPlanted/CplCheck) | CONFIRMED | - |
| 5b | execution discriminator | CertPlantedArmTest 4/4 executed (test-results XML); `gradlew certPlanted` without inputs ran the new @Test: "[CPL] REFUSING: -DsnapshotId is required" | CONFIRMED | - |
| 6 | selftest / mutants | selftest 14/14; --mutants 83 of 83 killed, M0 survived (sandbox via scratch_dir, OMP 1; worktree clean after) | CONFIRMED | - |
| 7 | suite | merged probe `gradlew test --offline --no-build-cache`: 565 tests, 2 failed = MrlRoutingTest.testMrlConfigDefaults + TraceEnvelopeUnwrapTest blank-trace (the known two); CertK2DeflatedArmTest 5/5 | CONFIRMED | - |
| 8 | merges cleanly onto main | `git merge-tree --write-tree main cert-planted`: clean at 61d1c5bf and again at 4d2c5e41. a29895dd (cert-k2-deflated) is already an ancestor of the base 5312852a, so there is no EOF conflict; dfl* and cpl* both present in the merged file | CONFIRMED | - |
| 9 | pins (LF of record) | cert_planted.py blob 028f05a2, sha256-lf16 9138d36ccaee91cf (crlf16 c60a425b945e7ce4); SeparationNullBySizeTest.kt blob abd9c533 lf16 1270d4cb61da9d5e (crlf16 d9c6063184dd1fa1); CertPlantedArmTest.kt blob ab2620c6 lf16 52955bd02720c829 (crlf16 43316b12d2ee0d7c); build.gradle.kts blob 2225cb6c lf16 a8b7358240b74f38 (crlf16 f0eaa1231c2fad06); worktree LF (0 CR lines) | CONFIRMED | - |
| 10 | launch sequence (rule 7) | sandbox of rp12-r2-run's HEAD 8419d4ce plus the docstring's path checkout: compiles, CertPlantedArmTest 4/4. Order: selftest -> union pool dry-run (reader) -> dry-run -> prepare -> hashes before -> arm (12 threads, 6g, --no-daemon) -> --stop -> hashes after -> analyze (hash equality refused otherwise) | CONFIRMED, notes L-2 | LOW |

## Own mutants (deciding paths)

- X1 Kotlin, certPlanted body L3726 `vectors = ids.map { cplUnit(rows.getValue(it)) }` -> `vecById.getValue(it)` (null
  moment-matched to the UNPLANTED cache rows, i.e. the very comparator Support (f) assumed): SURVIVED (CertPlantedArmTest 4/4; no
  test calls the @Test body; analyze checks only the declared statistic, k and reached, never the null's input). DECISIVE.
- X2 Python `DELTA_DEC = "8"` -> `"10"`: KILLED (3 selftest cases fail). Decisive, killed.

## Defects and fixes

- B-1 BLOCKER (Support f/g, P2/P3 calibration). Registrar bracket, pre-data, on L24311/L24312. The comparator is the null
  moment-matched to the planted rows, which grows with delta; print the proxy figures above. Then choose, and the choice is the
  orchestrator's or the author's (FLAG): (a) keep delta_dec 8 and restate P2/P3 honestly (MIXED is the modal reading under the
  optimistic proxy); or (b) re-anchor CP1/F-CP at delta 12 (proxy: 5/5/5 additive) and extend the grid (e.g. 16, 20) so that
  delta* stays bracketed. That means new pins and a delta review. The test stays a valid classification either way:
  INSENSITIVE then reads "the plain (moment-matched) null absorbs a planted 2-way shift of that size", and the F-CP wording
  should say moment-matched.
- M-1 MEDIUM (X1). Either extract the PL input selection into an internal `cplSiteInputs(...)` covered by CertPlantedArmTest, or
  write `null_trace` (sum ||centered||^2 of the rows the null used) per site to sites.csv and have analyze recompute it from the
  planted rows and refuse a mismatch. If neither is done before --run, it becomes post-run duty P-CPL1: per cell, the median null
  p95 at delta 12 must exceed delta 0's (the proxy predicts about 0.11-0.18 vs about 0.068). A flat null p95 across delta means
  the comparator was the cache rows.
- M-2 MEDIUM (Support c). Bracket n_eff of the deciding count: economics' 5 subsamples are about one population and u_d is shared
  across categories. "4 of 5 in 2 of 3" is closer to 2-3 effective units than 15.
- L-1 LOW. Support (a) still reads "deciding units ... at delta = 2" (analyze prints delta 8): bracket.
- L-2 LOW. The LAUNCH note's CertK2DeflatedArmTest precondition is stale (the file is absent in rp12-r2-run; the base already
  holds a29895dd). rp12-r2-run's src/main stays at 8419d4ce (no JoinCardinalityGuard: not on the arm's path, and the same
  instrument as CERT-PC-K2's run). Preferred: merge to main first, then path-checkout from main; disclose in the ops log.
- L-3 LOW. COST says "4-6 h"; the dry-run estimates about 88 min (3.5 x CERT-PC-K2's 1503 s, an upper bound because IDENTITY's
  n 6,993 null is counted 3.5 times). Budget a window of about 2 h.

## Commands (all read-only on DBs of record; scratch on E:/TaxoArena_tmp/cpl_rev, not committed)

```
powershell -File E:/TaxoArena_tmp/busy.ps1                           # gated every Gradle step (rc 1 = free)
cd .claude/worktrees/cert-planted                                       # HEAD 8db7be3d, clean
python tools/analysis/scratch_dir.py --run -- python tools/analysis/cert_planted.py --dry-run --data-root ../rp12-r2-run
python tools/analysis/scratch_dir.py --run -- python tools/analysis/cert_planted.py --selftest     # 14/14
python tools/analysis/scratch_dir.py --run -- python tools/analysis/cert_planted.py --mutants      # 83/83, M0 survived
recompute.py: own port (u, halves, s, plant, chanceCorrectedSeparation) on the cache (?mode=ro&immutable=1)
  + CERT-PC-K2 arm/replicates.csv SN quantiles + eigvalsh of the planted covariance -> proxy (2/pi) l1/tr
proxy.py: 210 of 210 cells equal the dry-run (|diff| <= 1e-6); 30/30 delta-8 > delta-0 p95; additive / multiplicative counts
git merge-tree --write-tree --name-only main cert-planted              # rc 0 (61d1c5bf and 4d2c5e41)
git worktree add --detach E:/TaxoArena_tmp/cpl_merge <commit-tree of the merge tree>; ... cpl_main 61d1c5bf; ... cpl_launch 8419d4ce
  + git checkout 8db7be3d -- <the docstring's 6 paths>
gradlew compileTestKotlin (cpl_main) / gradlew test (cpl_merge: 565, 2 known) / gradlew certPlanted (no inputs: REFUSING)
gradlew test --tests taxonomy.CertPlantedArmTest (cpl_launch 4/4; X1 4/4 = survived; restored, sha equal); gradlew --stop
javap_cmp.py: javap -c -p, re.sub('#\d+','#'), per-member compare main vs merge
X2: sed DELTA_DEC "10" on a copy, CPL_SRC_DIR/PYTHONPATH = the worktree's tools/analysis, --selftest rc 1
for f in <4 paths>: git rev-parse HEAD:f; git hash-object f; git show HEAD:f | sha256sum; ... | sed 's/$/\r/' | sha256sum
```
