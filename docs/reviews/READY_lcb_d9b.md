# READY review: LCB-D9B-BYTE-INERTNESS (2026-09-25, zero calls)

## VERDICT: NOT READY. One blocker (B1). Everything else is READY as pinned below.

- **B1 (HIGH, BLOCKER).** V10's "listed in SHA256SUMS with its own sha256" is a PRESENCE check in `d9b_aux.py`. The code tests `h in sums`: the list's sha256 appearing anywhere in the file. It does not check that the list's own path is listed with that sha256.
  - In the expected data the check is vacuous for most of A's and A2's lists. The 8 per-identifier lists of A and A2 are all empty, so they share one sha256 (e3b0c442...). legA_all.txt and legA2_all.txt are expected to be byte-identical (same commit).
  - Proved by execution: V10 reads **MET with only 4 of the 15 lists named in SHA256SUMS** (script below).
  - This is below ruling A4's bar: "V10 NOT MET (VOID) iff ... a list is not in SHA256SUMS with its own sha256". It is also below the file's own docstring.
  - **Required change R5:** parse SHA256SUMS into {normalised path: sha256}. Normalise by stripping a leading `*`, a leading `./` and backslashes. Require the entry `classlists/leg<L>_<id>.txt` to exist and to equal that list's sha256.
  - **Tests for R5:** (a) the 4-of-15 case gives NOT MET; (b) the path present with a wrong sha256 gives NOT MET; (c) the full set gives MET.
  - Re-pin d9b_aux.py and run_tests.py / run_tests.out afterwards. A delta check by the reviewer on the diff of d9b_aux.py alone is enough; nothing else needs re-review.

Pre-patch pins (the registrar's record item 1, f13736a) re-derived: 4 of 4 equal (d9b_compare_prepatch.py 0f82fa76..., d9b_aux_prepatch.py 58510ea5..., d9b_prep.py 8cc3eb84..., run_tests_prepatch.py e116091a...). R1-R4 are implemented as ruled: `diff d9b_compare_prepatch.py d9b_compare.py` and `diff d9b_aux_prepatch.py d9b_aux.py` show only the R1 / R2 / R3 / R4 hunks, plus docstrings and the `num()` helper.

## Pins of record (post-patch instrument; kinds per CONTEXT rule 8)

Location: `C:\Users\octav\AppData\Local\Temp\claude\Z--FAC-TUBerlin-THESIS-TaxoArena\7c10e5cb-d16b-4a0e-864a-f3a6151d835b\scratchpad\` (`$SPR`), subdirectories `d9b\` (`$SPB`) and `d9\` (`$SP`). All files are LF on disk unless marked. The gate checks sha256 of the file bytes (`Get-FileHash`).

| file | sha256-lf (= file bytes unless noted) | blob (LF bytes) | lines |
|---|---|---|---|
| d9b\d9b_compare.py | c1e0dc170b3c0783d614699c1928497dfa114408c13c749a6af4c3d9f6140d20 | blob:10521c50b492704fc0d6c1d75f346776a16c35e1 | 454 |
| d9b\d9b_aux.py | 28200e475d62247878d61fa10ba3e45e7b285d138d2d03544602e718344c31e7 (**to be re-pinned after R5**) | blob:929807289bd73e159d32b89ea3227f48af659d2e | 134 |
| d9b\d9b_prep.py | 8cc3eb84e92aa00a4b4bbd9cff88a27baa62cf9027c092ce2c1769c73cb7fab7 | blob:d0b75bb238fbfcc5887d1818e23efe81edffba3f | 174 |
| d9b\run_tests.py | 2538445080724523550c8cd9d67f3beb0b5e4115b5b6ce67127ab068d59c9ddb (**re-pin after R5**) | blob:1cae7bf8af9040bc61101d4da1a98a1c9e443480 | 511 |
| d9b\run_tests.out | **CRLF on disk** (356 CR): sha256-crlf16:4387296017ee8b8a (file bytes 4387296017ee8b8a3238c6a770c8e73f461426aaea9b99921f61aeb7030a6788); sha256-lf a4215dfeca838fa3a2d87daad3388ff87e1867bb931075ca90ffbf678ac30879 (of record) | blob:a2eb5d8ae80fd66094ba476b371e34275fb06196 (LF); blob:5483483225b4b01c4ec9e4268f4029f6f6eba55f (CRLF bytes, --no-filters) | 356 |
| d9\d9_legrun.cmd (reused) | **CRLF on disk** (36 CR): sha256-crlf16:e986bb848ebf3b98 (file bytes e986bb848ebf3b986c535c48bd1abb1034d8f6f2fad83a9f4e2f421af478ca60, the gate's value); sha256-lf 884f6cc41adb6911779a3a61de4c54f69ab26ef4b49ba6c828ea4c5be0fc3acc | blob:8a67bcbff7767246279eed3ea35642d42ce41952 (LF); blob:170a0c980d392f97b54994f0e1001972b6b856f1 (CRLF bytes) | 36 |
| d9\d9_leg_check_v2.py (reused) | b2d1ae8df0d1bd354e87e0d3bf9a32c3744cf2e73a49259d6b0eb97f6e037bfd | blob:e5f2ff7a785c982abbe4877f3a686b9ea21ac224 | 132 |
| d9\probe_lcb.toml (reused) | 617bd50b30aa4fdbfd00077393b5363517c13f88bc1e3858c1421417d08b297b | blob:e78bbaaaca47497fc47ba135622f6fe57b2821af | 67 |
| d9\pins.py (operator's L6 pin reader, informational) | 8dd4dfd96e6ea601841d4924531873fd74ac752d1449e04ebd643b95e8872a85 | blob:bdb548e0... | 17 |
| d9\w1.ps1 (operator's W1 probe, informational) | 0f68ce4b2a230757399773d5ace60812c8b9c58083dd6e60ee9fabc83d9d44ec | blob:ab0412fc... | 5 |

Command: `for f in ...; do sha256sum < $f; tr -d '\r' < $f | sha256sum; tr -d '\r' < $f | git hash-object --stdin; git hash-object --no-filters $f; done`. All values equal the relayed pins (c1e0dc17 / 10521c50, 28200e47 / 92980728, 8cc3eb84 / d0b75bb2, 25384450 / 1cae7bf8, 43872960 / a4215dfe, e986bb84, b2d1ae8d, 617bd50b).

Arm and commits: arm TOML blob:efd82bdacc06144439280d3b76923d38527bd7ae at a62c7e0, 6b9fc7c and main (`git rev-parse <c>:experiment_configs/topic_partition/ag_news_smoke_s42.toml`, 3 of 3). `git diff --name-only a62c7e0 6b9fc7c -- src/main build.gradle.kts settings.gradle.kts gradle.properties gradle/ config/` = exactly the four files. The same diff a62c7e0..main = 0 lines (HEAD f13736a).

## Per-claim table

| # | claim | status | command / script | got vs claimed | sev |
|---|---|---|---|---|---|
| 1a | C1' object list = registration (17 byte + 4 declared-drop + FILE-SET + 2 tables = 24) | CONFIRMED | read d9b_compare.py L54-L74 against programme L19674-L19678 word for word; module asserts `len(BYTE)==17`, 13 manifest keys, `len(OBJECTS)==24` | 17 byte paths, the 13 keys, 3 rows, 4 ledger columns, wall_ms, created_at: identical to the registration; EXCLUDED = the 2 headless_run.log + performance_report.json | - |
| 1b | nothing dropped beyond the declared list | CONFIRMED in code; test gap | reading, plus my mutation M1 / M6 / M9 (below) | the pinned lists are exact. An over-drop of a ledger column (M1 +RoutingECE) or an iteration_metrics column (M6 +mass), or a set-valued pool readout (M9), still passes 108/108 | LOW (D2) |
| 1c | verdict mapping 0 / 3 / 6 / 2 with A1 (mixed cell exits 3, F2 ALSO FIRED, [LIMIT]) | CONFIRMED | d9b_compare.py L386-L419; T12a-k; my mutation M2 (pre-R1 branch) | killed by T12f, T12g, T12j; no exit-4 branch; `else` raises Refuse | - |
| 1d | P6 per A2: DIFFERS on A/B and A/A2; bounds on A/B, A/A2, B/A2; relative to leg A's TDC; both sources | CONFIRMED | p6_score L226-L264; my mutation M3 (B/A2 relative to the pair's first leg) | killed by T15i; 22 clause-instances = 2 sources x (2 DIFFERS + 3 pairs x 3 bounds) | - |
| 1e | A3 refusals read VOID (exit 2) and name file and leg (R3) | CONFIRMED | normalised_in L168-L173; T7h, T8c, T9e, T10e | exit 2, nothing written | - |
| 1f | verdict mode with a missing readout | PARTLY | verdict() opens both JSONs without catching OSError / ValueError | traceback (exit 1), not a message with exit 2; still a non-verdict, so VOID | LOW (D3) |
| 2 | C1' / C2 are reachable: no compared object is known to be non-deterministic | CONFIRMED on 4 runs; residual latent paths disclosed | my own `four.py` (independent implementation of the D9b normalisation; not an import of d9b_compare) over copies of REF (main 09-22, commit 89495507), A' (incident pseudoroot), A and B (run_20260925b evidence + pool_copy_A/B) | **24 of 24 objects have 1 distinct value over the 4 runs** (6 pairs). TDC takes 4 distinct values (2.2410760E8 / 2.2409421E8 / 2.2377814E8 / 2.2376869E8), DP 4 distinct values, SS 2 | see D5 |
| 2a | the parallel append order of reassignQueries reaches no kept field | CONFIRMED for this arm | code read at HEAD (= a62c7e0 on src/main: `git diff --name-only a62c7e0 HEAD -- src/main` = 0) | SeparationJ sorts (`queryWeights.entries.sortedBy`, StatisticsUtils L260); routing CSVs iterate testQueries sequentially (no async in BatchTrickleEvaluator / runner writers); ledger ECE / Brier / ESS come from the eval routing; dag_snapshots carries counts. **Latent, inactive here:** MAIN_bridge_quality.csv `TopRepresentativeQueries = b.queries.take(10)` (HeadlessBenchmarkRunner L2600; 0 bridges on this arm, the file has 3 lines); KappaShrinkageMean sums over `getAllQueriesInRegion()` (ConcurrentHashMap key order, L2796-L2815; 0.0 in 4 of 4 runs because SmallLeafFraction = 0); PARTITION tie-breaks in buildLeafProfiles (weights 1.0) | LOW (D5) |
| 2b | reserved_pool_meta is rewritten by each leg (so the table comparison is not simply inherited from the input) | CONFIRMED | read-only select on my copies | created_at 1790098224612 / 1790342459721 / 1790344339821 / 1790344397259 (REF / A' / A / B); other columns equal; reserved_pool 600 rows, 1 digest | - |
| 3 | validity bars reachable at the predictions | CONFIRMED except V10 | D9 values: `grep '^\[V8\|^\[V4\|^\[V7' run_20260925b\d9_disc.txt`; S6/S7 probe lines; my V11 run | V1 4 files / 0 moved; V2 main AG 7cf2082f / 7eea2abd, sizes 1,622,016 / 206,032, mtimes 2026-09-22 19:30:24.276 / .616 (the baseline); emb 804,462,592 B, -wal 0 B; V3 A 0/0/0/0, B 4/2/1/2 (D9); V4 PASS both; V5 refusal True (B) / no-enum True (A); V6 PASS; V7 0/0; V8 11,133 / 10,825 ms and 58 / 41 s vs 480 s; V11 **MET executed** (`d9b_aux.py v11 <git show 6b9fc7c:arm> probe_lcb.toml`: 68 lines, 2 differ, keys datasetType / outputDir); V10 reachable, but its hash clause is vacuous (B1) | BLOCKER via B1 |
| 4 | three-leg procedure (A2 as "A" into $ST\a2; shared daemons; class lists before removal; rule 7; main never written; -shm expected to move) | CONFIRMED with ordering conditions | d9_legrun.cmd (label A or B only; stage from argument 3); d9_leg_check_v2.py (A branch, V4 from the root given; misses to <stage>\d9_misses_A.txt); d9b_prep.py (P1-P4; creates a2, aa2, classlists); d9b_aux classlists writes $ST\classlists\legA2_* | consistent with A5. Conditions are in the step list: both compares run BEFORE any probe; the leg-A root is the SAME literal in S5' and S5b' (verdict refuses otherwise); V10 runs BEFORE S11; the S8 append is UTF-8 | MEDIUM (D4, procedural) |
| 5 | run_tests.py: 108 of 108 | CONFIRMED | run on an ISOLATED COPY (`$SPR\rev_d9b\harness\`: the four .py files and copies of evidence_A/B, pool_copy_A/B, the misses files, the A' pseudoroot and probe_lcb.toml) | "108 of 108 cases as expected; 0 mismatches"; the case-name list equals the builder's run_tests.out case for case | - |
| 5a | my mutations (10) | 7 killed, 3 survive | `$SPR\rev_d9b\harness\mut.py`, `mut2.py` | killed: M2 (pre-R1 branch; T12f/g/j), M3 (P6 relative on the first leg; T15i), M4 (row drop ignores terminators; T7f), M5 (+exit_reason manifest drop; module assert), M7 (+question_count pool drop; T10d), M8 (pre-R4 all-lines count; T16a/c), M10 (leg-A identity check removed; T12h). Survived: M1, M6, M9 (D2) | LOW |
| 6 | no write to evidence or to main | CONFIRMED | sha256 of all 139 files under d9\run_20260925b and d9\incident_legA_void_20260925 before and after my session: identical (`cmp`); `sha256sum -c SHA256SUMS` in run_20260925b: 82 OK; main AG DB / -wal sha, size and mtime unchanged; no -shm or -wal created under the evidence (the pseudoroot's -wal is R0 evidence) | - |
| 7 | Support: non-vacuous; DEFF | CONFIRMED | registration Support (a)-(g) | DEFF not applicable and DECLARED (deterministic byte count, n = 1 pair per contrast); no SE to re-derive; the MDE is the resolution (1 byte); (g) carries the reachability check, which I extended in claim 2. SCOREABLE stands | - |
| 8 | V10 SHA256SUMS clause | REFUTED | `$SPR\rev_d9b\harness\v10st\`: 15 lists, SHA256SUMS naming 4 of them; `python d9b_aux.py v10 <st>` | **"[V10] MET", rc 0**, against ruling A4 (NOT MET) | **BLOCKER (B1)** |

## Defects

- **B1 (HIGH, BLOCKER).** See the verdict. Fix: R5 as stated there.
- **D2 (LOW, tests).** The drop lists are exact in code, but no test pins them.
  - Mutations M1 (+RoutingECE in the ledger drop), M6 (+mass in the iteration_metrics drop) and M9 (reserved_pool compared as a set, so a duplicated row is invisible) survive 108/108.
  - Fix, optional before the run: one test asserting CSV_DROP / ROW_DROP / JSON_DROP / POOL_DROP / EXCLUDED equal the registration's literal lists; one loop mutating EVERY kept ledger column, iteration_metrics column and manifest key (each must read DIFFERS); one duplicated reserved_pool row (must read DIFFERS).
  - The sha256 pin makes an over-drop after the READY detectable. Not blocking.
- **D3 (LOW).** `--verdict` gives a traceback, not an INSTRUMENT REFUSAL, when a readout is missing or corrupt. The outcome is VOID either way. Fix: catch OSError / ValueError and raise Refuse.
- **D4 (MEDIUM, procedural; written into the step list below).** Four conditions:
  - (a) S5' and S5b' run BEFORE S6' / S7'. The verdict's leg-A identity check refuses if leg A's AG copy or outputs moved between the two readouts.
  - (b) The leg-A root argument must be the identical string in S5' and S5b'. `roots[0]` is compared literally.
  - (c) V10 runs before S11. After the worktrees are removed, a missing list cannot be recaptured.
  - (d) The S8 append to `$ST\d9_disc.txt` must be UTF-8 or ASCII (python, or `Add-Content -Encoding ascii`), never `>>` / `Out-File` in Windows PowerShell 5.1, which write UTF-16LE. d9b_aux v10 reads that file as UTF-8, and a UTF-16 tail puts NULs and a BOM into it.
- **D5 (LOW, disclosure for the outcome; not a drop).** Three order-dependent writers exist in the code but are inactive on this arm, so none of them is plausibly non-deterministic at this arm:
  - bridge TopRepresentativeQueries (0 bridges);
  - KappaShrinkageMean (0 small leaves);
  - PARTITION tie-breaks.
  - The 4 runs show them constant. If leg B's change created a bridge or a small leaf, the DAG and counts would differ anyway (a genuine S_AB entry).
- **D6 (LOW, carried from D9 D5).** Legs A, B and A2 share the Gradle daemon started by A, and its Kotlin daemon. compileKotlin runs in each fresh build/ (V3 and V4 separate the class dirs); bootRun forks its own JVM. No effect expected; record the daemon lines per leg.

## Exact step list (PowerShell unless marked; replaces the builder's S0'-S12 where they differ)

Variables:
- `$SPR` = `C:\Users\octav\AppData\Local\Temp\claude\Z--FAC-TUBerlin-THESIS-TaxoArena\7c10e5cb-d16b-4a0e-864a-f3a6151d835b\scratchpad`;
- `$SP` = `$SPR\d9`;
- `$SPB` = `$SPR\d9b`;
- `$ST` = `$SPB\run_d9b_1` (fresh, created by d9b_prep, never by hand; not run_20260925 / run_20260925b);
- `$W` = `Z:\FAC\TUBerlin\THESIS\TaxoArena\.claude\worktrees`;
- `$M` = `Z:\FAC\TUBerlin\THESIS\TaxoArena`.

- **S0'. Pins and hygiene.**
  - `Get-FileHash` (SHA256) on d9b_compare.py, d9b_aux.py (the R5 pin), d9b_prep.py, d9_legrun.cmd (CRLF bytes e986bb84...), d9_leg_check_v2.py, probe_lcb.toml: each must equal the table above.
  - `Get-CimInstance Win32_Process -Filter "Name='java.exe' or Name='python.exe'"` must be empty. If not, WAIT, never kill.
  - Free RAM must be at least 12 GB.
  - Print main's L6 pins in both views (pins.py), plus sizes, mtimes and sha256 of main's AG DB, -wal, embeddings_cache.db (+ -wal) and snapshots.db.
  - W1 (w1.ps1) must show main's embeddings_cache.db and ag_news_smoke_cache_v1.db FREE.
- **S1. Worktrees.**
  - `git -C $M worktree add --detach .claude/worktrees/d9b-legA a62c7e0ddb7a47f6ba691450c0cdd643cbdbe76d`
  - then `d9b-legB` at `6b9fc7c278121868cb79477a9e12803b36830a3a`;
  - then `d9b-legA2` at `a62c7e0ddb7a47f6ba691450c0cdd643cbdbe76d`.
  - Print the environment variable names. Run nothing inside any worktree before S3'.
- **S2. Copies (the rule-7 window opens).**
  - `python $SPB\d9b_prep.py $M $W\d9b-legA $W\d9b-legB $W\d9b-legA2 $ST`
  - It must end `[V2] PASS` and `[D9B-PREP] created ...\a2, ...\aa2, ...\classlists`.
  - Expected: AG copy e3415684318c937c..., embeddings copy 52229e1ebfdda76e..., in all three legs.
- **S3'. Leg A.**
  - `cmd /c "$SP\d9_legrun.cmd" A "$W\d9b-legA" "$ST"`
  - `python $SP\d9_leg_check_v2.py A $W\d9b-legA $ST\legA_bootrun.log $ST`: must print ALL VALIDITY CHECKS PASS, with V3 0/0/0/0.
  - `python $SPB\d9b_aux.py classlists A $W\d9b-legA $ST`.
- **S4'. Leg B.** Check RAM first (at least 12 GB).
  - `cmd /c "$SP\d9_legrun.cmd" B "$W\d9b-legB" "$ST"`
  - The checker with B. V3 must be at least 3/1/1/1; predicted 4/2/1/2.
  - `python $SPB\d9b_aux.py classlists B $W\d9b-legB $ST`.
- **S4b. Leg A2, as "A" into $ST\a2.** Check RAM first (at least 12 GB).
  - `cmd /c "$SP\d9_legrun.cmd" A "$W\d9b-legA2" "$ST\a2"`
  - `python $SP\d9_leg_check_v2.py A $W\d9b-legA2 $ST\a2\legA_bootrun.log $ST\a2`: must pass with V3 0/0/0/0, and V4's jar token must name the d9b-legA2 classes dir.
  - `python $SPB\d9b_aux.py classlists A2 $W\d9b-legA2 $ST`.
- **S5'. C1' (before any probe).**
  - `python $SPB\d9b_compare.py $W\d9b-legA $W\d9b-legB $ST A B --misses $ST\d9_misses_A.txt $ST\d9_misses_B.txt`
  - Exit 0 = HELD; 3 = FAILED; 2 = VOID.
- **S5b'. C2.**
  - `python $SPB\d9b_compare.py $W\d9b-legA $W\d9b-legA2 $ST\aa2 A A2 --misses $ST\d9_misses_A.txt $ST\a2\d9_misses_A.txt`
  - Use the SAME literal `$W\d9b-legA` as in S5'.
- **S5c. Verdict.**
  - `python $SPB\d9b_compare.py --verdict $ST\d9b_compare.json $ST\aa2\d9b_compare.json $ST\d9b_verdict.txt`
  - Exit 0 / 3 / 6 / 2; P6 is printed and scored (descriptive).
- **S6'. Probe B and V11.**
  - `python $SPB\d9b_aux.py v11 <file holding git show 6b9fc7c:experiment_configs/topic_partition/ag_news_smoke_s42.toml> $SP\probe_lcb.toml`: must be MET.
  - `cmd /c "$SP\d9_legrun.cmd" B "$W\d9b-legB" "$ST" probe "$SP\probe_lcb.toml"`
  - The check one-liner of the delta READY on `$ST\probeB.log`: exit != 0, refusal True, no-enum False.
- **S7'. Probe A (MANDATORY, ruling A5).**
  - `cmd /c "$SP\d9_legrun.cmd" A "$W\d9b-legA" "$ST" probe "$SP\probe_lcb.toml"`: exit != 0 and `No enum constant`.
  - A missing S7' = V5 NOT MET (VOID) and P7 UNDETERMINED.
- **S8. Discriminator record.** Append the S6' / S7' lines to `$ST\d9_disc.txt` in UTF-8 (python `open(...,"a",encoding="utf-8")` or `Add-Content -Encoding ascii`). Never `>>` or `Out-File`.
- **S9. Stop the JVMs (the rule-7 window closes).** `.\gradlew.bat --stop` from d9b-legB. No java.exe may remain.
- **S10. Evidence.**
  - Copy each leg's outputDir, headless_run.log, transcript and `git status --short` into `$ST\evidence_A`, `evidence_B` and `evidence_A2`.
  - Then (Git bash) `cd $ST && find . -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS`. This covers classlists\, a2\, aa2\ and the pool copies.
- **S10b. V10, BEFORE any removal.**
  - `python $SPB\d9b_aux.py v10 $ST`: must be MET (path-bound after R5).
  - Print the non-.class hits (disclosed, per A4).
- **S11. Remove the three worktrees.** `git worktree remove --force` for each; G5 fallback `rm -rf` + `git worktree prune`. `git worktree list` must name none of them.
- **S12. V9.**
  - Main's embeddings_cache.db and snapshots.db must equal S0' in both views.
  - Main's AG DB must be 1,622,016 B, sha256 7cf2082f..., mtime 2026-09-22 19:30:24.276; its -wal 206,032 B, sha256 7eea2abd..., mtime unchanged.
  - The -shm mtimes are EXPECTED to move ((v)).
  - Hand `$ST` to the post-run reviewer.

The scoring stays the registration's. DISCHARGED needs exit 0 at S5c AND V1-V11 met, and the verdict script does not check V1-V11.

## Reviewer's evidence (scratchpad, not committed)

- `$SPR\rev_d9b\four.py`: independent 4-run compare. Its output is claim 2.
- `$SPR\rev_d9b\harness\run_tests_mine.out`: my 108/108.
- `$SPR\rev_d9b\harness\mut.py`, `mut2.py`: 10 mutations.
- `$SPR\rev_d9b\harness\v10st\`: the B1 reproduction.
- `$SPR\rev_d9b\evidence_before.sha`, `evidence_after.sha`: 139 files, identical.

## What this review does not show

- That the legs will pass V1-V11, or that C1' and C2 will hold. Four runs make a floor, not a proof of determinism: SphericalSilhouette varied in 1 of 4.
- The mechanism of the declared drift.
- Anything about DendrogramPurity, SphericalSilhouette or TotalDasguptaCost beyond P6 (descriptive).
- Anything about the LCB stage-0 analysis.
