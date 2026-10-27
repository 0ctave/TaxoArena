# Delta READY review 1: LCB-D9-BYTE-INERTNESS, after the instrument VOID at S3 (2026-09-25)

Reviewer: adversarial-reviewer. Zero LLM calls. No leg built or run by me. Main's DBs read by file hash only.

Scope:
- READY of record: docs/reviews/READY_lcb_d9.md (bf3fa81).
- Registrar record: 22cb37e (programme L19434-L19457, readings R5-R8).
- Registration: docs/judge_v2_program.md L18662-L18872 (V3-V8 at L18831-L18836, P5 at L18864).
- The operator's run: S0-S3 on 2026-09-25 15:19-15:22. Leg A (a62c7e0) exit 0, BUILD SUCCESSFUL in 58s. d9_leg_check.py (sha256 9ee6d43d, file bytes CRLF) returned VOID.
- Evidence dir: scratchpad `d9\incident_legA_void_20260925\`, `d9\ops_20260925\`, `d9\run_20260925\`.

Scratchpad root: `C:\Users\octav\AppData\Local\Temp\claude\Z--FAC-TUBerlin-THESIS-TaxoArena\7c10e5cb-d16b-4a0e-864a-f3a6151d835b\scratchpad`.

## VERDICT: READY for the rerun

The rerun is READY as the amended step list below. It needs:
- fresh worktrees;
- a fresh `$ST`;
- the two new pinned files, `d9_leg_check_v2.py` and `d9_legrun.cmd`.

The registrar records deviations DEV-V8, DEV-CAP, DEV-INSTR and DEV-INC, plus reading R9, before the rerun's S0. Neither C1 nor V3, V6 or V7 is weakened. The proof that leg B EXECUTED the changed code is unchanged (V3 class counts and the R3 probe) and tightened (V4 now also requires the bootRun JVM's own [BOOT] line).

## Per-claim table

| # | claim | verdict | command / evidence | number got vs claimed | sev |
|---|---|---|---|---|---|
| 1 | V4: the [BOOT] line is broken, so `jar=` lands on the next line | CONFIRMED | Python decode of `legA_bootrun.log` (UTF-16LE with BOM, sha256 32871118..., 793 CRLF lines; byte-identical to `run_20260925\legA_bootrun.log` by `cmp`) | breaks at 1-based lines 16->17 (processAot JVM, pid 52524) and 33->34 (bootRun JVM, pid 48144). The operator's "15->16, 32->33" are 0-based. | LOW (numbering only) |
| 1a | cause: PowerShell `*>` wraps at the console width | CONFIRMED | See the mechanism note below the table. | as claimed | - |
| 1b | the jar in V4 is the expected one | CONFIRMED | v2 re-join (T1 below) | 2 of 2 [BOOT] lines give `file:/Z:/FAC/TUBerlin/THESIS/TaxoArena/.claude/worktrees/d9-legA/build/classes/kotlin/main/` = expected, case-insensitive and in fact exact | - |
| 2 | V8: the helper measures a different quantity from the registered "per-leg build wall time" | REFUTED as a mismatch; CONFIRMED as unreachable | See the V8 note below the table. | duration_ms 10,445 ms; Gradle 58 s; START-END 58 s; all < 60 s | HIGH (registration defect: the bar is impossible for a warm leg) |
| 3 | all other checks pass (V3 0/0/0/0, V6, V7 0 misses) | CONFIRMED | `ops_20260925\S3_legcheck.txt`; re-run by v2 (T1) | V3 {0,0,0,0} over 1,319 class files. V6: Fetched x2, POOL x2, SPLIT-SIDE x1, exit_reason completed, BUILD SUCCESSFUL, EXIT 0. V7: 0 misses, cache-hit ['1400']. All equal. | - |
| 4 | main DBs unchanged | CONFIRMED | my `sha256sum` and `ls --full-time` at review time | ag 7cf2082f... 1,622,016 B, mtime 2026-09-22 19:30:24.276; -wal 7eea2abd... 206,032 B; embeddings 52229e1e... 804,462,592 B, mtime 2026-09-23 14:33:13.182, -wal 0 B; snapshots.db 1,065,541,632 B, mtime 2026-09-23 04:34:26. All equal to the baseline. | - |
| 5 | the evidence copy is the leg's output | CONFIRMED | `find . -type f -exec sha256sum` in the worktree outputDir and in `outputDir_copy`, then `diff` | 24 / 24 files identical | - |
| 6 | leg B was never run | CONFIRMED | `ls d9-legB/build` | no build dir. Its root holds only the d9_prep copies (ag 1,748,992 B, embeddings 804,462,592 B) and snapshots_frozen.db. | - |

**Mechanism for 1a.**
- Host: PowerShell 5.1.26100.9444, `$Host.UI.RawUI.BufferSize.Width` = 120.
- A native command's stderr line becomes an ErrorRecord, and `*>` writes it word-wrapped at 120 columns:
  - the bootRun line is 54 + 95 = 149 characters;
  - the processAot line is 70 + 95 = 165 characters (it carries the `.\gradlew.bat : ` prefix and the NativeCommandError block);
  - both break at the last space before column 120.
- Stdout lines are not wrapped: lines of 148 and 1,771 characters are intact in the same file.
- The ErrorRecord's own "Au caractere ..." line is hard-wrapped at 119.
- The same [BOOT] line captured by bash or cmd redirection is a single line in `experiment_results/anchorfree/af.build.out` (2 occurrences) and in `redraw/af_clean_s42.build.out`. There the jar path is 23 characters shorter (the main root) and the file is not UTF-16.
- Source: Application.kt L18-L22 at a62c7e0 and at 6b9fc7c emits ONE `System.err.println`.

**V8 note (claim 2).**
- The registration defines the quantity by the 2026-09-22 run's run_manifest `duration_ms`:
  - L18689: "Its recorded build took 114,618 ms (run_manifest.json `duration_ms`), about 2 minutes from boot to exit";
  - L18787: "a build of about 2 min: 114.6 s at 09-22";
  - P5, L18864: "(2026-09-22: 114.6 s)".
- `d9_leg_check.py` measured exactly that quantity.
- What fails is the BAR. The 114.6 s run computed 1,400 embeddings (G3 of bf3fa81). This leg had 0 misses, which is P4's registered prediction.
- Every candidate reading of "build wall time" is below the 1-minute floor:
  - run_manifest duration_ms: 10,445 ms;
  - Gradle "BUILD SUCCESSFUL in 58s";
  - the leg.ps1 START 15:20:12 to END 15:21:10: 58 s.
- So V8's floor cannot hold for a warm-cache leg of this arm at any budget. The instrument would VOID every correct rerun: V8 is impossible, not underpowered.

## Defects

**D1 (HIGH): V8's registered bar [1, 8] min is unreachable for this arm.**
- The floor was calibrated on a cold-embedding run (114.6 s, including 1,400 embedding computations), while P4 registers 0 misses.
- P5 inherits the same defect: "each leg's build wall time is within [1, 8] min".
- Fix: deviation DEV-V8 (below). Score P5 as registered, FAILED if the legs are warm; do not reinterpret it.
- **The READY bf3fa81 should have caught this.** It established P4 = 0 itself (G3) and did not connect it to V8 or P5. This is my defect.

**D2 (MEDIUM): V4 in `d9_leg_check.py` v1 is not robust to the capture method the READY prescribed.**
- The READY prescribed `*>` in PowerShell 5.1 (S3).
- The READY's own test used a synthetic UTF-16 transcript with the line unbroken, never a PowerShell-captured one.
- Fix: DEV-CAP (capture by cmd) AND a wrap-tolerant V4 (v2). Either alone would have passed this leg; both are required so that neither is a single point of failure.

**D3 (MEDIUM): reading R5 names three conjuncts for V6 ("BUILD SUCCESSFUL", no "BUILD FAILED", recorded exit 0), but v1 enforces only the first two.**
- The exit code was recorded (EXIT 0) but read by no check.
- Fix: v2 reads the LAST `EXIT <n>` in `<stage>\leg<L>_exit.txt` and requires 0 (tests T9 and T9b).

**D4 (MEDIUM, descriptive; registered risk (g) made concrete): two C1 metrics depend on input state.**
- Leg A (warm cache, a62c7e0) was compared with the 2026-09-22 reference output (cold cache, commit 89495507).
- `git diff --name-only 89495507 a62c7e0 -- src/main | wc -l` = 0, and 89495507 is an ancestor of a62c7e0.
- They differ in 2 of the 21 C1 objects (my read-only script using d9_compare's own BYTE / CSV_DROP / JSON_DROP lists):
  - `validation/MAIN_taxonomy_quality.csv`: DendrogramPurity 0.6867787184488174 vs 0.6867787184488098, TotalDasguptaCost 2.2409421312346172E8 vs 2.2410760359757888E8;
  - `tuning_ledger.csv` without CommitSHA: the same two values.
- The other 19 are equal.
- `computeTotalDasguptaCost` (AdditionalMetrics.kt L100-L149 at a62c7e0) samples 5,000 pairs by index with a fixed seed. A different point order (cold compute vs cache read) therefore changes the estimate. That is a plausible mechanism, NOT verified.
- Both D9 legs start from byte-identical warm copies, so C1 is not biased by this. But if the metric is run-to-run non-deterministic, C1 FAILS on MAIN_taxonomy_quality.csv for a reason unrelated to the change.
- Fix: reading R9 (below). The incident leg A is a free A' leg: same commit, identical input copies e3415684 / 52229e1e.

**D5 (LOW): S2's first attempt refused because `$ST` (`run_20260925`) already existed.**
- Refusal at `ops_20260925\S2_prep.txt`, rc 1.
- The operator re-ran S2 (S2b, V2 PASS). This was correct fail-closed behaviour, but the READY said only "must not exist".
- Fix: the amended S2 says it explicitly: do NOT create `$ST`; d9_prep creates it.

**D6 (LOW): S9's criterion "no java.exe" was not met at S12.**
- `S12_V9.txt` at 15:21:59 lists PID 29384 (Gradle daemon JVM) and PID 57664 (Kotlin compile daemon, kotlin-compiler-embeddable 2.1.10).
- My process query at review time shows none.
- Fix: S0 of the rerun re-checks the list and WAITS. The Kotlin daemon is not stopped by `gradlew --stop`, and it exits on idle.

**D7 (LOW): S6's refusal check is a plain substring search, so a PowerShell capture could split the needle across lines.**
- Fix: capture the probe through `d9_legrun.cmd ... probe`, and search the text with CR and LF removed (the command is in S6' below).

## The new instrument

### `d9_leg_check_v2.py` (scratchpad `d9\`; v1 kept untouched and re-hashed: 9ee6d43d...)

Pins:
- file bytes = LF rendering; 7,238 B; 0 CR;
- sha256 **b2d1ae8df0d1bd354e87e0d3bf9a32c3744cf2e73a49259d6b0eb97f6e037bfd**;
- blob:e5f2ff7a785c982abbe4877f3a686b9ea21ac224;
- no CRLF rendering exists in the working file.

Changes against v1 (v1's V3, V6 sanity strings and V7 code are carried verbatim):
- **V4:**
  - every `[BOOT] TaxoAdapt starting` occurrence is re-joined with up to 3 continuation lines, with no separator inserted (a PowerShell word-wrap keeps its trailing space);
  - its `jar=` token must equal the leg's own `file:/<root>/build/classes/kotlin/main/`;
  - at least one occurrence must FOLLOW `> Task :bootRun`, i.e. come from the JVM that wrote the outputs (processAot also prints one);
  - an unrecoverable token is VOID.
- **V6:** adds R5's third conjunct, the last `EXIT` in `<stage>\leg<L>_exit.txt` = 0.
- **V8 (DEV-V8):**
  - the floor is NOT applied;
  - the 8-minute ceiling is applied to BOTH `duration_ms` and the Gradle "BUILD SUCCESSFUL in ..." time;
  - the construction must have run: `duration_ms` > 0 and at least 1 data row in `diagnostics/iteration_metrics.csv`;
  - both times and "below the registered floor: True/False" are printed.

Tests: `d9v2test\run_tests.py` (sha256 5b3e55f2...), output `d9v2test\run_tests.out`, **18 of 18 as expected, 0 mismatches**. Each VOID case fails on exactly the check it targets; I read each case's printed lines.

| test | input | expected | got |
|---|---|---|---|
| T0 | v1 on the incident transcript | VOID | VOID (V4 [] and V8) |
| T1 | **v2 on the incident transcript** (PowerShell-wrapped, UTF-16) + the real leg-A root | PASS | **PASS** (V4 2 tokens, both = expected, 1 after bootRun; V8 10,445 ms / 58.0 s / 10 rows) |
| T2 | unwrapped, cmd-style UTF-8 transcript | PASS | PASS |
| T3 / T3b | wrong jar (d9-legB) in the bootRun line / in the processAot line only | VOID | VOID (V4 FAIL) |
| T4 / T4b | `BUILD FAILED` appended / no `BUILD SUCCESSFUL` | VOID | VOID (V6 NOT SUCCESSFUL) |
| T5 | fetch line removed from headless_run.log (fake root, transcript re-pointed) | VOID | VOID (Fetched x0) |
| T5c | the same fake root, unmutated (control) | PASS | PASS |
| T6 | the bootRun JVM's [BOOT] removed (only processAot's remains) | VOID | VOID (V4: 0 after bootRun) |
| T7 | no [BOOT] start line | VOID | VOID |
| T8 | jar token hard-wrapped mid-path | VOID | VOID (fail-closed) |
| T9 / T9b | recorded EXIT 1 / no exit file | VOID | VOID |
| T10 / T11 | duration_ms 480,001 / Gradle 8m 1s | VOID | VOID |
| T11b | Gradle 7m 59s | PASS | PASS |
| T12 | iteration_metrics header only | VOID | VOID (0 rows) |

### `d9_legrun.cmd` (scratchpad `d9\`; the capture wrapper)

Pins:
- file bytes = CRLF rendering; 1,879 B; 36 CR;
- sha256 **e986bb848ebf3b986c535c48bd1abb1034d8f6f2fad83a9f4e2f421af478ca60**;
- LF rendering sha256 884f6cc41adb6911779a3a61de4c54f69ab26ef4b49ba6c828ea4c5be0fc3acc;
- blob:8a67bcbff7767246279eed3ea35642d42ce41952 (of the LF rendering).

What it runs:
- `call .\gradlew.bat <the registered arguments, unchanged> > <log> 2>&1`, from the leg root.
- It writes START / `EXIT <rc>` / END to the exit file and exits with the Gradle exit code.
- It refuses:
  - a leg other than A or B;
  - a missing stage dir;
  - an existing log or exit file;
  - a bad 4th argument.

Executed from PowerShell 5.1 against a stub `gradlew.bat` that echoes its argv, prints a 180-character stderr line and exits with `%STUBRC%`:
- the argv reached gradlew exactly as registered: `bootRun --console=plain --offline --no-build-cache "-Dranking.db.path=ratings_d9_A.db" --args="--config experiment_configs/topic_partition/ag_news_smoke_s42.toml"`;
- the probe form, `bootRun --console=plain --offline "-Dranking.db.path=ratings_d9_probeB.db" --args="--config <SP>\d9\probe_lcb.toml"`, also reached it as registered;
- the 180-character stderr line was captured on ONE line, as UTF-8;
- `$LASTEXITCODE` = 0 / 3 / 1 for stub exits 0 / 3 / 1;
- refusals exited 2 (existing log, bad argument, missing stage).

## Deviations and readings the registrar must record (before the rerun's S0)

- **DEV-V8 (from D1).** V8 "per-leg build wall time in [1, 8] min" is read as:
  - the ceiling of 8 min on run_manifest `duration_ms` AND on the Gradle "BUILD SUCCESSFUL in" time;
  - plus the construction ran (`duration_ms` > 0, at least 1 data row in `iteration_metrics.csv`);
  - the floor is NOT applied, because it is unreachable at warm cache under every reading (incident leg A: 10,445 ms / 58 s / 58 s; the floor was calibrated on the cold 114,618 ms run).
  - Both legs' observed values are disclosed in the outcome.
  - P5 is scored AS REGISTERED: FAILED if either leg is below 1 min, with the cause stated. It is a prediction, not a validity check.
- **DEV-CAP (from D2 and D7).** S3, S4, S6 and S7 capture through `d9_legrun.cmd` (cmd redirection) instead of PowerShell `*>`. The bootRun commands are unchanged byte for byte in their arguments.
- **DEV-INSTR (from D2 and D3).** `d9_leg_check_v2.py` (b2d1ae8d...) replaces `d9_leg_check.py` (9ee6d43d...) for the rerun. V4 is wrap-tolerant and requires the bootRun JVM's line; V6 enforces R5's exit conjunct; V8 follows DEV-V8. V3, V6's sanity strings and V7 are unchanged. `d9_prep.py` and `d9_compare.py` are unchanged.
- **DEV-INC.** The 15:20-15:21 leg A is an INSTRUMENT VOID (a failed precondition), not an outcome:
  - leg B was never run, and no C1 was computed;
  - main was unchanged (claim 4);
  - evidence is in `incident_legA_void_20260925\` (log sha256 32871118...).
- **R9 (reading, from D4; descriptive, NOT C1).**
  - After S5, `d9_compare.py` runs on (the incident leg A pseudo-root, the new leg A) into `$ST\aa`: an A/A' comparison on identical inputs and the same commit.
  - If C1 FAILS and A/A' differs in the same file(s), the reading is non-determinism under (g), and D9 stays open under a new registration.
  - If A/A' is equal, a C1 failure reads the change.
  - The warm-leg vs 2026-09-22 cold-reference difference in DendrogramPurity and TotalDasguptaCost is disclosed as an input-state dependence of two quality metrics, not a D9 result.
  - In the `$ST\aa` output, the `[V7] ... NOT EQUAL (VOID)` line is an artefact: there are no misses files in that directory. It is ignored there.

## Rerun: fresh worktrees and a fresh $ST are REQUIRED

Why:
- **Leg A's worktree** holds `build/` (so no cold compile, against registration L18757), its outputs, an appended tuning_ledger.csv, and private DB copies the run wrote (ag -wal 8,272 B, embeddings -wal 4,136,512 B, ratings_d9_A.db, snapshots.db). A second run there would not start from inputs identical to leg B's.
- **`run_20260925`** holds the VOID leg's files. d9_prep refuses an existing stage, and `d9_legrun.cmd` refuses an existing log.

## Amended step list

Run from PowerShell. Set:
- `$SP` = the scratchpad `d9` directory;
- `$ST` = `$SP\run_20260925b`, NOT created by hand;
- `$W` = `Z:\FAC\TUBerlin\THESIS\TaxoArena\.claude\worktrees`.

**R0. Preserve the A' material, before any removal.**
```
New-Item -ItemType Directory $SP\incident_legA_void_20260925\pseudoroot\experiment_results\topic_partition
Copy-Item -Recurse $SP\incident_legA_void_20260925\outputDir_copy $SP\incident_legA_void_20260925\pseudoroot\experiment_results\topic_partition\ag_news_smoke_s42
Copy-Item $W\d9-legA\ag_news_smoke_cache_v1.db, $W\d9-legA\ag_news_smoke_cache_v1.db-wal $SP\incident_legA_void_20260925\pseudoroot\
git -C $W\d9-legA status --short > $SP\incident_legA_void_20260925\legA_status_R0.txt
```
- This is a file copy only: no SQLite open, and no java.exe may be running.
- Hash the copied files into `$SP\incident_legA_void_20260925\SHA256SUMS_R0`.

**R1. Remove the old worktrees.**
- `git worktree remove --force` for d9-legA, then d9-legB.
- G5 fallback: `rm -rf` then `git worktree prune`.
- `git worktree list` must name neither.

**S0'. Pins and hygiene.**
- `Get-FileHash` must match these file-byte sha256 values:

| file | sha256 | rendering |
|---|---|---|
| d9_prep.py | 58b0ec87... | CRLF |
| d9_compare.py | 8636b215... | LF |
| d9_leg_check_v2.py | b2d1ae8d... | LF |
| d9_legrun.cmd | e986bb84... | CRLF |

- v1 is not used.
- The process list must hold no java.exe or python.exe: WAIT, never kill (D6).
- Free RAM must be at least 12 GB.
- Print main's L6 pins in both views.
- Confirm that `git diff --name-only a62c7e0 HEAD` over the four pinned files is 0 (0 at review time, HEAD 86e88d2).

**S1. Fresh worktrees.** The same commands as in the READY: d9-legA at a62c7e0, d9-legB at 6b9fc7c. Print the environment variable names.

**S2. Copies.**
- `python $SP\d9_prep.py <main> $W\d9-legA $W\d9-legB $ST` must end `[V2] PASS`.
- Expected: ag copy e3415684..., embeddings copy 52229e1e....

**S3'. Leg A.**
```
cmd /c "$SP\d9_legrun.cmd" A "$W\d9-legA" "$ST"
"PS LASTEXITCODE $LASTEXITCODE"
python $SP\d9_leg_check_v2.py A $W\d9-legA $ST\legA_bootrun.log $ST
```
- The checker must print `ALL VALIDITY CHECKS PASS`.
- V3 must read 0 / 0 / 0 / 0.

**S4'. Leg B.** The same as S3', with `B` and `d9-legB`. V3 must read at least 3 / 1 / 1 / 1 (predicted 4 / 2 / 1 / 2).

**S5. C1.** Unchanged: `python $SP\d9_compare.py $W\d9-legA $W\d9-legB $ST`. Exit 0 is C1 HELD; exit 3 is C1 FAILED.

**S5b (R9, descriptive).**
```
New-Item -ItemType Directory $ST\aa
python $SP\d9_compare.py $SP\incident_legA_void_20260925\pseudoroot $W\d9-legA $ST\aa
```
This is recorded as the A/A' result, never as C1.

**S6'. The probe.**
- Create `probe_lcb.toml` as in the READY: exactly 2 lines differ from the arm TOML.
- Run: `cmd /c "$SP\d9_legrun.cmd" B "$W\d9-legB" "$ST" probe "$SP\probe_lcb.toml"`.
- Check:
```
python -c "import sys;r=open(sys.argv[1],'rb').read();t=(r.decode('utf-16') if r[:2]==bytes([255,254]) else r.decode('utf-8','replace')).replace('\r','').replace('\n','');print('refusal','[LCB] refusing to build LIVECODEBENCH' in t,'no-enum','No enum constant' in t)" $ST\probeB.log
```
- PASS requires all three:
  - `probeB_exit.txt` EXIT is not 0;
  - the refusal line is present;
  - there is no `No enum constant`.

**S7'.** Optional: the same from leg A with `A`. Expected: `No enum constant`.

**S8-S12.** As in the READY. The discriminator record appends the v2 lines and the probe lines to `$ST\d9_disc.txt`. S12 V9 re-hashes main against claim 4's values.

## What this review does not show

- That the rerun's legs will pass, or that C1 will hold.
- That DendrogramPurity and TotalDasguptaCost are run-to-run deterministic. R9 measures that.
- That `d9_legrun.cmd` behaves identically with the real Gradle. It was executed against a stub. The real transcript is checked by v2, which PASSES on either capture form (T1, T2).
