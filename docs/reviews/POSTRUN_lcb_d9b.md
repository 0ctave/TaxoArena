# Post-run review: LCB-D9B-BYTE-INERTNESS (2026-09-25, zero calls)

Reviewer: adversarial-reviewer. Zero LLM calls. Nothing built or run except my own read-only scripts. No evidence DB was opened in place: the four pool copies were first copied to `$SPR\postrun_d9b\cp_*\ag.db`, and only those copies were opened, with `mode=ro&immutable=1`. Main's DBs were read by file bytes only (`stat` + `sha256sum`).

## VERDICT: D9 DISCHARGED. The run is VALID. S5c exited 0. C1' HELD (0 of 24). C2 HELD (0 of 24). V1-V11 are all MET. P6 FAILED on its B/A2 TDC bound, which is descriptive and carries no bar on D9. The four src/main blobs of 6b9fc7c are MERGEABLE to main BY PATH, under the conditions in section "Merge".

- S_AB = {} and S_AA = {}. The branch that fires is DISCHARGED. F1 does not fire and F2 does not fire.
- The words of record (registration L19684) are the declared-drop words only. They are in section "Words of record".
- Nothing blocks the verdict. Defects D1-D6 below are LOW: disclosures and hygiene, none of them touching a criterion.

Authority:
- Registration: docs/judge_v2_program.md L19642-L19714 (ab8aee9).
- Rulings A1-A5: L19802-L19850 (f13736a).
- READY: docs/reviews/READY_lcb_d9b.md (d984724) plus delta 1 (89befc6); the registrar's READY record f447fbb, L19852-L19895.
- Step list: S0'-S12 of d984724, with the delta's S0' pins.

Evidence:
- `$SPR` = `C:\Users\octav\AppData\Local\Temp\claude\Z--FAC-TUBerlin-THESIS-TaxoArena\7c10e5cb-d16b-4a0e-864a-f3a6151d835b\scratchpad`.
- `$ST` = `$SPR\d9b\run_d9b_1`: 124 files, of which SHA256SUMS is one and lists the other 123.
- `$SPR\d9b\ops_d9b_1`: 28 files. They are outside $ST, so I froze them myself: `$SPR\postrun_d9b\ops_d9b_1.sha256`, 28 lines, sha256 82052e2e6144f560....
- My script: `$SPR\postrun_d9b\mine.py`, sha256-lf a33b30dace9836e5..., blob:5135958c1f4c7f62f142f5614045426d9febc968. The file has LF endings and no CR, so this is the rendering of record.

## Per-claim table (operator's claims)

| # | claim | verdict | command / script | mine vs claimed |
|---|---|---|---|---|
| 1 | SHA256SUMS: 123 OK | CONFIRMED | `cd $ST && sha256sum -c SHA256SUMS \| grep -c ': OK$'` gives 123; `find . -type f \| wc -l` gives 124 (123 plus SHA256SUMS itself); `find . -name '*-shm' -o -name '*-wal' -o -name '*-journal' \| wc -l` gives 0 | 123 = 123. I re-ran it after my own work: still 123 OK, 124 files |
| 2 | C1' HELD (0/24) | CONFIRMED, independently | mine.py. It uses its own normalisations, not d9b_compare's code. It reads the S10 evidence copies `evidence_{A,B,A2}\outputDir` and the private pool copies. The table's 21 files use a CSV re-serialisation. The run_manifest drops the 13 keys and re-dumps sorted. Pool tables are read in PK scan order | 0 of 24; S_AB = []. All 24 objects have 1 distinct value over A, B and A2 |
| 3 | C2 HELD (0/24) | CONFIRMED, independently | the same run | 0 of 24; S_AA = []; also S_B/A2 = [] |
| 3a | the evidence copies are what the compare saw | CONFIRMED | the sha256 prefix of `evidence_{A,B,A2}\outputDir\seed_42\dag_snapshots.jsonl` and `diagnostics\proposals.csv` is 61a91c4f1807f94c / 251947bf3c2fc76e in all three legs. These equal the byte digests d9b_compare printed in `d9b_compare.txt` and `aa2\d9b_compare.txt`. The FILE-SET digest (…a72b02fdd254) and the reserved_pool digest (61dfe77a253869d9) also equal mine | equal |
| 3b | the two leg-A pool copies (S5' and S5b') agree | CONFIRMED | mine.py `[POOL-X]` | reserved_pool 600 rows and meta 1 row, identical |
| 4 | S5c exit 0 | CONFIRMED | `ops_d9b_1\s5c_verdict.txt` last line `rc=0`; `s5_c1.txt` / `s5b_c2.txt` `rc=0` | 0 |
| 5 | leg checks: A and A2 0/0/0/0 at 1319 classes; B 4/2/1/2 at 1320 | CONFIRMED | `d9_disc.txt`, `a2\d9_disc.txt`; recount from the lists: `grep -c '\.class$' classlists\leg*_*.txt` | A 0/0/0/0 of 1319; A2 0/0/0/0 of 1319; B 4/2/1/2 of 1320. `diff legA_all legB_all` gives exactly one line, `+ taxonomy/dataset/LcbWorkDirGuardState.class`. legA_all = legA2_all (sha256 4902217e...) |
| 6 | V10 MET, V11 MET | CONFIRMED | see V10 / V11 below | MET / MET |
| 7 | probes: B refuses; A prints "No enum constant" | CONFIRMED | `tr -d '\r\n' < probeB.log \| grep -oF '[LCB] refusing to build LIVECODEBENCH' \| wc -l` and the same for `No enum constant` | B: refusal 1, no-enum 0, EXIT 1. A: refusal 0, no-enum 1, EXIT 1 |
| 8 | main DBs unchanged apart from the -shm mtime | CONFIRMED, with a correction | my own `stat` + `sha256sum` now, against s0.txt / s12.txt | AG DB 1,622,016 B 7cf2082f…, -wal 206,032 B 7eea2abd…, both mtimes unchanged. embeddings_cache.db 52229e1e… and snapshots.db 390c313e…, sizes and mtimes unchanged. The L6 pins in both views are equal at S0' and S12 (embeddings 39,631 / queries 31,986 / snapshots 207, same sha16). **Two** -shm mtimes moved, not one: embeddings_cache.db-shm (15:55:29 to 18:11:13) and snapshots.db-shm (14:18:50 to 18:04:41, then 18:11:24). Both -shm contents are unchanged (fd4c9fda…). This is D1 |
| 9 | P6 FAILED descriptively: B/A2 0.639% vs 0.6%; TDC A 2.2284566e8, B 2.2248550e8, A2 2.2390910e8 | CONFIRMED | mine.py P6 block, in both sources | A 2.2284566454962477E8, B 2.2248549838590908E8, A2 2.239090965798335E8. The relative differences, all of A: A/B 0.161621%, A/A2 0.477206%, B/A2 **0.638827%**. They are identical in the quality CSV and in the ledger's last row (1 row per ledger) |
| 10 | about 33 min of rule-7 waits | UNDETERMINED (immaterial) | the captures start at S0' 18:04:13 and hold no wait log | not in the evidence; the captured window runs S0' 18:04:13 to S12 about 18:11 |

## V1-V11 (scored against the registration's text)

| V | text (short) | verdict | evidence (mine) |
|---|---|---|---|
| V1 | `git diff --name-only A B -- src/main build.gradle.kts settings.gradle.kts gradle.properties gradle/ config/` = exactly the four files; the arm TOML = efd82bda at A, B and main | MET | I re-ran it at HEAD f447fbb: 4 lines (TaxonomyConfig.kt, CorpusRegistry.kt, CorpusSource.kt, MMLUDatasetFetcher.kt). The blobs at 6b9fc7c are 2825b12d / 5b1bbb3a / 817b1417 / a2a85c03, equal to the registration. `git rev-parse {a62c7e0,6b9fc7c,main}:experiment_configs/topic_partition/ag_news_smoke_s42.toml` gives efd82bda 3 times |
| V2 | input copies byte-identical across the three legs | MET | d9b_prep.txt: AG copy e3415684318c937c… and embeddings copy 52229e1ebfdda76e… in A, B and A2, `[V2] PASS`. The $ST copies are in SHA256SUMS with those exact values (verified OK) |
| V3 | A and A2 0/0/0/0; B >= 3/1/1/1 | MET | A 0/0/0/0, A2 0/0/0/0, B 4/2/1/2. Recounted from the class lists (claim 5) |
| V4 | each leg's [BOOT] jar token names its own worktree's classes dir, >= 1 after `> Task :bootRun` | MET, per leg | My awk over each transcript found 1 start line after bootRun in each of legA_bootrun.log (d9b-legA), legB_bootrun.log (d9b-legB) and a2\legA_bootrun.log (d9b-legA2), each naming its own `build/classes/kotlin/main/`. The line after it is `[BOOT] corpusDbPath …`, which is not a start line |
| V5 | probe B exit != 0 AND the [LCB] line AND no "No enum constant"; control A "No enum constant" | MET | claim 7. probeB_exit.txt `EXIT 1`; probeA_exit.txt `EXIT 1`. S7' was run, as ruling A5 made mandatory |
| V6 | all three legs: BUILD SUCCESSFUL, no BUILD FAILED, last EXIT 0, the Fetched / [POOL] / [SPLIT-SIDE] lines, exit_reason completed | MET, per leg | my counts over the CR-stripped transcripts. A: SUCCESSFUL 1, FAILED 0, Fetched 2, POOL 2, SPLIT 1. B: 1/0/2/2/1. A2: 1/0/2/2/1. Exit files `EXIT 0` in all three. run_manifest exit_reason `completed` in all three, with commit a62c7e0 / 6b9fc7c / a62c7e0 and dirty False |
| V7 | embedding misses printed per leg and equal | MET | d9_misses_A.txt / d9_misses_B.txt / a2\d9_misses_A.txt each hold `0` |
| V8 (DEV-V8) | duration_ms and Gradle time each under 8 min; duration_ms > 0; >= 1 iteration_metrics row; the 1-min floor NOT applied | MET | duration_ms 10,471 / 10,192 / 11,041. Gradle 58 s / 41 s / 34 s. 10 iteration rows each |
| V9 | after the window, main's embeddings_cache.db and snapshots.db equal the L6 baseline in both views; AG DB and -wal unchanged in size, mtime and sha256; worktrees removed only after the evidence | MET | claim 8 (S0' = S12 = my re-hash now). `git worktree list \| grep -c d9b` gives 0; `ls .claude/worktrees \| grep -c d9b` gives 0. The class lists were written 18:06:41-18:09 and SHA256SUMS at 18:10:47. V10 (s10b_v10.txt) ran at 18:10:52, before the S12 capture at 18:11:32. The files still hold worktree content, so they were taken before S11. The -shm moves are D1 |
| V10 (A4 + R5) | 15 lists exist, each in SHA256SUMS under its own path with its own sha256; .class count = V3 count; non-.class hits disclosed | MET | My own check: for each of the 15 `classlists\leg{A,B,A2}_{LIVECODEBENCH,fetchLiveCodeBench,lcbWorkDirGuard,LcbWorkDirGuardState,all}.txt`, `grep -F "./<path>" SHA256SUMS` finds exactly one entry and its sha256 equals the file's. `grep -cF classlists/ SHA256SUMS` gives 15. The .class counts equal V3 (0/0/0/0 ×2, 4/2/1/2, 1319/1320/1319). Non-.class hits: 0 in all 15. s10b_v10.txt: 123 entries parsed, 0 unparsed, none listed twice, `[V10] MET` |
| V11 | the probe TOML differs from the arm TOML in exactly 2 lines (datasetType, outputDir), CR-stripped | MET | `diff <(tr -d '\r' < ops_d9b_1\arm_6b9fc7c.toml) <(tr -d '\r' < d9\probe_lcb.toml)` gives 2 hunks, L22 datasetType and L29 outputDir. arm_6b9fc7c.toml has blob efd82bda, and its LF sha256 b1884736… equals `git show 6b9fc7c:…ag_news_smoke_s42.toml \| sha256sum` |

**Leg B executed the changed code. This is the discriminator, and it is not vacuous.**
- (a) V3/V10: B's classes dir holds the 4/2/1/2 identifier-bearing classes plus the new LcbWorkDirGuardState.class. A and A2 hold none of them.
- (b) V4: the leg-B bootRun JVM loaded `d9b-legB/build/classes/kotlin/main/`. Its run_manifest records commit 6b9fc7c, dirty False.
- (c) The probe on the same classes dir took the new branch: `IllegalStateException: [LCB] refusing to build LIVECODEBENCH: '…d9b-legB\embeddings_cache.db' table 'embeddings' holds 39631 rows`. So both the DatasetType.LIVECODEBENCH constant and the lcbWorkDirGuard ran.
- (d) compileKotlin ran in every leg, not UP-TO-DATE and not FROM-CACHE (transcript L6 in all three). The probes reused those classes (UP-TO-DATE), as designed.
- (e) `-Dranking.db.path` reached each JVM: DB-GUARD printed `ratings_d9_A.db` in A and A2 and `ratings_d9_B.db` in B.
- Limit: on the AG_NEWS arm itself, the changed code executes only on its common paths (config parse, registry). The LCB-only branches run only in the probe. That is what the registration asks the discriminator to show.

**The discharge rule.** S5c exited 0 and V1-V11 are all MET, so D9 is **DISCHARGED**.

## P1-P8

| P | registered | verdict | value |
|---|---|---|---|
| P1 | C1' 0 of 24 | HELD | 0 |
| P2 | C2 0 of 24 | HELD | 0 |
| P3 | A 0/0/0/0; A2 0/0/0/0; B 4/2/1/2 | HELD | exact |
| P4 | embedding misses 0 in all three legs | HELD | 0/0/0 |
| P5 | pool id p18579549e6d95873 in all three legs | HELD | the transcripts have `[POOL] recorded p18579549e6d95873` twice each. The distinct `reserved_pool.pool_id` and `reserved_pool_meta.pool_id` in my copies of A, B and A2 are p18579549e6d95873 (600 rows; ag_news, 2000, seed 42, 0.3, 600, 4) |
| P6 | per ruling A2: DIFFERS on A/B and A/A2; the three bounds on all three pairs, relative to A's TDC, in both sources | **FAILED** (descriptive; no bar on D9) | DIFFERS: A/B yes, A/A2 yes (both sources). TDC bound 0.6%: A/B 0.1616% holds; A/A2 0.4772% holds; **B/A2 0.6388% FAILS in both sources**. It also fails of B (0.6399%) or of A2 (0.6358%), so the choice of denominator is immaterial. DP <= 1e-13: max 2.0e-15, holds. SS <= 1e-15: max 2.8e-17, holds. That makes 22 clause-instances, 20 hold and 2 fail, which matches the verdict script's own P6 line. **No bar on D9**: the registration says "(descriptive block, no bar on D9)" (L19701). Ruling A2(d) says "P6 stays DESCRIPTIVE with no bar on D9". The verdict script returned rc 0 while printing P6 FAILED |
| P7 | S6' B refuses with the [LCB] line (exit 1); S7' A prints "No enum constant" (exit 1) | HELD | claim 7 |
| P8 | duration_ms in [5,000, 60,000]; Gradle <= 120 s | HELD | 10,471 / 10,192 / 11,041 ms; 58 / 41 / 34 s |

**What the TDC spread says about the record's 0.6%.**
- The 0.6% figure comes from one place: the RANGE of 3 bareq512 builds, 0.577%. It appears in FRAMEWORK.md L297 ("quality CSV drift 0.58%") and campaign_review L252. The EVAL-METRIC-DETERMINISM draft (L19716-L19730, "DISCLOSURE") turns it into a decision margin: "any cross-build comparison or Pareto decision that relies on a TotalDasguptaCost difference smaller than about 0.6% is within noise".
- A range is not a bound. It grows with the number of replicates.
- On this arm, the D9 review measured 4 runs at CV 0.085% and range 0.151%. D9b's 3 same-input builds give CV 0.332% and range 0.640%.
- The 6 AG smoke values I can recover from the record give CV 0.292% and range 0.723%. Those are D9b's three plus D9's 2.2409421e8 / 2.2377814e8 / 2.2376869e8 (L19587-L19640).
- So a single pairwise difference between two builds has SD about √2 × 0.29% ≈ 0.41%. Its two-sided 95% noise band is about ±0.8%, not 0.6%.
- Consequence: the draft's "about 0.6%" is **anti-conservative**. Pareto or cross-build TDC differences between 0.6% and roughly 0.8-1% are also within noise.
- tools/tuning/pareto.py has NO noise floor at all. `grep -n "TotalDasguptaCost\|noise" tools/tuning/pareto.py` shows only the objective list at L110 / L113. TDC is minimised raw, so the "floor" exists only in the draft's prose.
- Fix, carried to EVAL-METRIC-DETERMINISM's registration (MEDIUM for that item, not for D9b):
  - state the noise as a CV with its n and its source, never as a range;
  - raise the interim margin to at least 1%, or state it as 2.8 × CV;
  - until the fix lands, make pareto.py either refuse or flag TDC-decided dominance below that margin.
- The DP and SS last-digit statement (1e-15 / 1e-17 scale) holds.

## Deviations: can any of them affect validity?

| deviation | effect on validity | evidence | severity |
|---|---|---|---|
| sha256sum instead of Get-FileHash at S0' | none. The two tools compute the same function on the same bytes. But the S0' pin check is **not captured** in ops (s0.txt holds W1 / RAM / main pins only) | I re-hashed now: d9b_compare 55b961ca…, d9b_aux ca9becec…, d9b_prep 8cc3eb84…, d9_legrun.cmd e986bb84… (CRLF file bytes), d9_leg_check_v2 b2d1ae8d…, probe_lcb 617bd50b…, pins.py 8dd4dfd9…, w1.ps1 0f68ce4b…. All equal the READY pins. All mtimes are 15:29-17:13, before S0' at 18:04 | LOW (D2) |
| pins.py quoting slip | none. The first two calls opened `…\TaxoArena$f` and failed with `unable to open database file`. The reruns produced the pins | `ls -la Z:\FAC\TUBerlin\THESIS \| grep -F 'TaxoArena$'` gives 0 lines, so no stray file was created | none |
| `cmd //c` failed from bash; leg.ps1 wrapper | **none. The exact registered arguments reached d9_legrun.cmd.** leg.ps1 (5 lines, LF, sha256 59e77ed1…, blob:017f5e61…) forwards only L, Root, Stage and optionally `probe <toml>`. It does this as `cmd /c "\"$SP\d9_legrun.cmd\" $L \"$Root\" \"$Stage\""`, which is the registered `cmd /c "$SP\d9_legrun.cmd" A "$W\d9b-legA" "$ST"`. The gradle command line is hard-coded in the pinned d9_legrun.cmd (e986bb84, unchanged) | every degree of freedom is verified from the outputs. L: log names legA / legB / a2\legA and DB-GUARD `ratings_d9_{A,B,A}.db`. Root: the V4 jar tokens and the manifest commit per leg. Stage: logs in $ST and $ST\a2 only. Config: the task graph line `bootRun --args=--config experiment_configs/topic_partition/ag_news_smoke_s42.toml` in all three legs, and `--config …\d9\probe_lcb.toml` in both probes. --no-build-cache / --offline come from the pinned cmd. Weakness: leg.ps1 was not pinned before the run, and its invocation lines are not captured beyond `[LEG.PS1] rc=1` for the probes | LOW (D3) |
| shared daemons (D6) | none | leg A's transcript alone has "Starting a Gradle Daemon". prelegs.txt at 18:06:45 / 18:07:46 / 18:08:40 shows only daemon 50964 and Kotlin daemon 51024, both started by A (none at 18:05:18). compileKotlin ran in each fresh build/. The class lists show no cross-contamination (B +1 class; A = A2) | none (as ruled) |
| evidence layout mirrors D9 | none. A2's files are in $ST\a2 as ruling A5 requires. evidence_A2 holds `legA_bootrun.log` because A2 ran as "A" | layout checked | none |
| probe-B output saved outside $ST | none for scoring. V5 / P7 are scored from `$ST\probeB.log`, which is hashed. `ops_d9b_1\probeB_outputDir` (7 files) is not in SHA256SUMS | now frozen in my ops_d9b_1.sha256 | LOW (D4) |
| ops logs outside $ST | none for C1' / C2. V9's baseline (s0.txt / s12.txt) and the S5 rc captures live only in ops, which no SHA256SUMS covers | frozen in `$SPR\postrun_d9b\ops_d9b_1.sha256` (28 files) | LOW (D4) |
| **not disclosed by the operator:** a foreign python.exe during leg B | none on outputs (C1' / C2 identical). It is a rule-7 hygiene point | prelegs.txt at 18:07:46 shows `36376 python.exe … rc_probe3.py`. That file (`$SPR\jv2pp_review\rc_probe3.py`) was created at 18:07:34.53. Leg B ran 18:06:59.61-18:07:41.06, so the overlap is at most about 7 s, at the end of leg B's bootRun. It is a CPU-only RateControl probe: no DB, no sqlite, no file reads beyond an import from a worktree. The operator did apply W-rule WAIT: the next check, at 18:08:40, was clean before A2 started at 18:08:41 | LOW (D5) |

## Defects

- **D1, LOW (record accuracy).** "Main DBs unchanged apart from the -shm mtime" should read: two -shm mtimes moved (embeddings_cache.db-shm and snapshots.db-shm). The contents are unchanged. The snapshots.db-shm move happened at 18:04:41, during S0' itself (the operator's own mode=ro pin read), not inside a leg. Registration item (v) names only embeddings_cache.db's -shm. The step list's S12 says "The -shm mtimes are EXPECTED to move" (plural). V9 is decided on content pins, so it is MET either way. Fix: the outcome states both.
- **D2, LOW.** The S0' Get-FileHash / sha256sum pin check and the S0' process check have no capture in ops_d9b_1. I re-hashed the pins and they are equal, with mtimes before the run. prelegs.txt at 18:05:18 shows no [PROC]. Fix: the outcome cites this review's re-hash.
- **D3, LOW.** leg.ps1 was an unpinned wrapper, and its call lines are not captured. It is verified by outputs (above). Fix: record leg.ps1's pin (sha256-lf 59e77ed1ab09f872…, blob:017f5e61798ddb77b2157a6b59cf452de253dffb) in the outcome.
- **D4, LOW.** ops_d9b_1 (including probeB_outputDir) is not covered by any SHA256SUMS. Frozen here: `$SPR\postrun_d9b\ops_d9b_1.sha256`, sha256 82052e2e6144f56003986236c1023883bf841088dce661446a3e880806725906. Fix: keep $ST and ops_d9b_1 until the outcome is recorded, as with E2's v10st.
- **D5, LOW.** An undisclosed foreign CPU-only python process (rc_probe3.py) overlapped at most the last ~7 s of leg B. No effect on the compared bytes. Fix: the outcome discloses it with the timestamps above.
- **D6, LOW (scope, the registration's D5 disclosure confirmed).** The order-dependent writers were inactive in all three legs: BridgeCount 0, KappaShrinkageMean 0.0, SmallLeafFraction 0.0. The tree has 10 leaves and 18 nodes in all three. The identity covers what this small arm exercises.

## Words of record

The registration allows exactly this (L19684):

> "byte-inert on every compared field except DendrogramPurity, SphericalSilhouette and TotalDasguptaCost, which are declared non-deterministic and NOT tested"

Qualified with the object, as follows. The four src/main blobs of 6b9fc7c (2825b12d / 5b1bbb3a / 817b1417 / a2a85c03) against a62c7e0 are byte-inert on every compared field except DendrogramPurity, SphericalSilhouette and TotalDasguptaCost, which are declared non-deterministic and NOT tested. The evidence is the AG_NEWS smoke construction (arm efd82bda, pool p18579549e6d95873, id-disjoint only), 24 objects, one A/B pair and one A/A2 determinism pair (C1' 0/24, C2 0/24). Never "byte-inert" alone.

What D9b does NOT show:
- anything about DP, SS or TDC under the change (they are dropped; P6 is n = 1 pair per contrast and descriptive);
- determinism beyond one A/A2 pair (a low-frequency non-determinism can hide: SphericalSilhouette varied in 1 of 4 earlier runs);
- the MMLU-Pro offset-0 path, a union run, the TUI or the site-null harness;
- that fetchLiveCodeBench or lcbWorkDirGuard behave correctly beyond the one probe refusal (the LCB window's job);
- anything about the three src/test files or the experiment_configs/lcb_stage0 files, which are not D9's object;
- the mechanism of the TDC / DP / SS drift (EVAL-METRIC-DETERMINISM);
- anything about arms with bridges or small leaves (D6).

## Merge: what unblocks, and the procedure I would require

**Unblocked:** the merge of the LCB Kotlin into main. That is the four src/main files, the three src/test files, and `experiment_configs/lcb_stage0/{lcb_af_bareq512_s42.toml, .toml.template, lcb_gate_ids.json}` from lcb-build-2 at 087e43d. The registration's merge conditions are checked now:
- `git diff --name-only a62c7e0 6b9fc7c -- src/main` gives exactly the 4 files. MET.
- There is no src/main byte change on the branch after 6b9fc7c: `git diff --name-only 6b9fc7c 087e43d -- src/main` gives 0. The tree ids agree: src/main 98b29c3a at both 6b9fc7c and 087e43d; src/test 32e859f4 at both. MET (Q3).
- Main has not moved on the merge paths since a62c7e0. `git diff --name-only a62c7e0 main -- src/main build.gradle.kts settings.gradle.kts gradle.properties gradle/ config/` gives 0. `-- src/test` gives 0. main:src/main = a62c7e0:src/main = d7768281. main:src/test = 2ee562cb. build.gradle.kts is 17b0b865 on all four. The test-read files tools/analysis/pool_guard.py and topic_partition/ng_af_bareq512_s42.toml are unchanged since a62c7e0. So the tested code is exactly what lands.
- The full main-vs-087e43d diff on the merge paths is 10 entries: A ×3 configs, M ×4 src/main, A ×2 plus M ×1 src/test.

**Conditions (all required):**
1. **Atomic, in ONE commit.** Commit src/main (4), src/test (3) and experiment_configs/lcb_stage0 (3) together. **Never the toml without the Kotlin.** On main, ConfigParsesTest (L33-L48) walks every `experiment_configs/**/*.toml`, and `datasetType = "LIVECODEBENCH"` is an unknown value there. The src/main files may land without the toml, but the tests reference the template, so keep all 10 together.
2. **Protect first.** Tag 087e43d before anything else (e.g. `lcb-kotlin-d9b-discharged`). At present only branch lcb-build-2 holds it: `git tag --points-at 087e43d` gives none. 3bcc9ab is already tagged `lcb-stage0-outcome-of-record`.
3. **By path, from the main checkout:** `git checkout 087e43d -- <the 10 explicit paths>`, then `git add <10 paths>`, then `git commit -- <10 paths>`. No merge commit, no directory copy with delete, no `git add -A`. Verify `git diff --cached --name-only | wc -l` is 10 and that nothing else is staged: the index is shared. Never touch config/application.yml, .gitignore, .env or report/.
4. **Blob and tree checks after the commit.**
   - `git rev-parse HEAD:src/main` = 98b29c3a887ca7427aa8771dce36844ab43a0f6e.
   - `git rev-parse HEAD:src/test` = 32e859f43c89d7abd33609f10bfa112c10817e0d.
   - Every one of the 10 blobs = `git rev-parse 087e43d:<path>`.
   - `git diff --name-only a62c7e0 HEAD -- src/main` = exactly the 4 files.
   - `git merge-base --is-ancestor <parent> HEAD`, and the peer commits are still reachable (the 2026-09-23 orphaning hazard).
5. **Tests before the commit, in a CLEAN worktree** of main + the 10 paths, never in the main checkout: `.\gradlew.bat test --offline`.
   - ConfigParsesTest walks the working tree, so main's untracked `experiment_configs/smoke12_preflight.toml` and `reserved_pool_frozen_pf844849e133cda4e_20ng.json` would contaminate the run.
   - Required: ConfigParsesTest (the new toml parses, and so does every other committed toml under the new DatasetType), LiveCodeBenchDatasetTypeTest, LcbStage0ConfigTest and PinnedPoolsReproduceTest all green. The failures must be at most the two known worktree environmental ones (MrlRoutingTest defaults, TraceEnvelopeUnwrapTest blank-trace), named.
   - Print the XML totals (tests / failures / errors) beside the commit.
   - Guard against the tests-write-to-production-DBs hazard: sha256 and mtime of main's embeddings_cache.db, snapshots.db and ag_news_smoke_cache_v1.db(-wal) before and after the suite. The LCB tests use `Files.createTempDirectory`, which I read, but the whole suite runs.
6. **Rule 7.** The compile and test JVM run inside an announced window, with no other Gradle worker and no pool reader. No git write touches src/ during another agent's window.
7. **One merge at a time** (the registration: "the orchestrator's merge, one at a time"). The registrar's outcome section "## LCB-D9B-BYTE-INERTNESS (2026-09-25, 0 calls) — DISCHARGED …" should precede the merge commit or be in it. It must carry the declared-drop words, the D1-D6 disclosures and P6 FAILED (descriptive).
8. **Voiding clause.** Any later src/main byte change on the LCB line before the merge voids this discharge (Q3). Re-check condition 4's tree id immediately before committing.

## Commands (reproducible, all read-only)

- `python $SPR\postrun_d9b\mine.py`: C1' / C2 / P6 on the evidence copies and private pool copies. Output: 24 rows, distinct = 1 each; `S_AB = [] S_AA = [] S_BA2 = []`; `C1' HELD (0 of 24) C2 HELD (0 of 24)`; the P6 lines as quoted.
- `cd $ST && sha256sum -c SHA256SUMS | grep -c ': OK$'` gives 123.
- The V10 loop, the V4 awk, the V6 greps, the V1 `git diff`, the main `stat` + `sha256sum` and the merge-path `git diff` / `rev-parse` calls, as quoted in the tables.
