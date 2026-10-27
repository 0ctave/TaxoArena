# DELTA CHECK 4 — ARCH-V2-PILOT-K46 D-4 fix, branch archv2-k46-preanalyze @ 788ea85 (parent 586c0d2; NOT MERGED)

Reviewer: adversarial-reviewer, 2026-09-25. Zero judge calls. Not touched: the posting worktree, the run2 store, `--analyze`. The selftest was run once under python and once under -O, as the coordinator allowed.

## VERDICT

**READY for `--analyze` under A1-A6 of delta READY 3 (0c10ea2), with A2's pins updated below.** D-4 is FIXED and D-5 is DISCLOSED. No new defect.

## Checks

| # | claim | status | evidence |
|---|---|---|---|
| 1 | the change touches only 3 files | CONFIRMED | `git diff --name-only 586c0d2 788ea85` gives analysis.py, outcome.py, selftest.py (3). `git diff --name-only 5e9de0f 788ea85` gives the same 3, so pilot.py, accounting.py, archv2_pilot_k46.py and judge_v2 are the posting build's |
| 2 | with no C1 reading, `falsifier_lines` prints "FALSIFIER NOT READ (no C1 reading: ...); no planning consequence is stated"; wired into both C0 branches | CONFIRMED | analysis.py: the guard is `c1_has_reading(c0_pass, words)`, the same predicate P3 uses. outcome.py calls it at L278 (C0 FAIL, `c0_pass=False`), at L429 (C0 (d)-void, `c0_pass=False`) and at L490, the final call (default `c0_pass=True`; K7 words give no reading) |
| 3 | with a reading, FIRED / NOT FIRED unchanged | CONFIRMED | My own table, 8 cases, through `falsifier_lines` at 788ea85: P EXCL gives NOT FIRED; M EXCL gives FIRED; both give FIRED; UNRESOLVED gives NOT FIRED; K7 words give NOT READ; C0 FAIL with no words or with 'M EXCLUDED' gives NOT READ; c0_pass=True with no words gives NOT READ. 0 wrong. NOT READ lines state no planning consequence ("stands" / "overturns" absent) |
| 4 | D-5 disclosed on the F8 line | CONFIRMED | outcome.py: "[D-5: this count can only print 0: require_inside REFUSES the analysis on any such row before this line; it witnesses the check, it does not measure]" |
| 5 | tests 268/0, python and -O; branch FALSIFIER.NOT_READ executed | CONFIRMED | worktree: `selftest.py --part all` gives "268 checks, 0 failed" under python and under -O. "EVERY registered print branch executed (62 branches)" PASS, with FALSIFIER.NOT_READ in the list. The 5 D-4 checks PASS: units, K7 end to end, C0 FAILED partial cache, C0 (d) void, and MUTANT falsifier_not_fired_no_reading killed |
| 6 | MY source-edit mutant R-D4: the guard narrowed to `if not c0_pass` (the K7 branch regresses) | KILLED | LF archive of 788ea85, source edited (confirmed applied). My table: 2 wrong (K7, and c0_pass=True with no words, both print NOT FIRED). The suite's `part_l7_units` fails 1 of 23 ("D-4 the falsifier without a C1 reading (K7; ...)"). The end-to-end K7 check in part_forced_zero also targets it |

## A2, updated pins (blob = `git hash-object` = `git rev-parse 788ea85:<path>`; the working tree is CRLF)

| file | blob (LF) | sha256-lf16 | sha256-crlf16 (working tree) |
|---|---|---|---|
| tools/analysis/archv2_pilot/analysis.py | f7ff9bdb2edafbe207d2c379999561f8b06044c2 | 8117b3e56148362e | df0d9d274e2581ff |
| tools/analysis/archv2_pilot/outcome.py | f7a0108eda9cfe82d475817b1f0d836805751de1 | c37fdbcf80642263 | 21af9270128bfa35 |
| tools/analysis/archv2_pilot/selftest.py | cc419ea303c99d94c6fd820e8d06a5be51889256 | b4cdf92d544e30d4 | c35611f0ee786801 |

- **A2 now reads:** run from worktree Z:\FAC\TUBerlin\THESIS\TaxoArena\.claude\worktrees\agent-a2f4fe2a50e2ff614 at HEAD **788ea857794d1034c1170198429ac9cd154bdc91** with a clean tree, or from an equal-blob checkout, e.g. main after a merge of this branch; F5-safe, no judge_v2 file.
- The header must print archv2_pilot lf16 **098302869a14bd65** (verified with `C.package_lf16()` at 788ea85) and "judge_v2 pins (MAIN-B653B0A) EQUAL".
- The 586c0d2 pins and lf16 0fa589da9b13bee5 are SUPERSEDED.

## A1 and A3-A6: UNCHANGED

- **A1** posting has exited, run complete; a rollover relaunch only from 5e9de0f.
- **A3** the command, word for word as in 0c10ea2: TAXOARENA_DATA_ROOT = main; `--store` = main's pilot_k46_verdicts_run2.db; `--expect-payload-anchor 02f9f17b...`; `--rubric-sha256 67f843eb...`; a NEW `--out`; `--workers`. The disclosure line now reads "this analysis's archv2_pilot lf16 098302869a14bd65 (DIFFERS ...)".
- **A4** is DISCHARGED by option (a) of D-4 (this fix). No registrar bracket is needed.
- **A5** after a crash, a new `--out`, with the aborted files disclosed.
- **A6** the F5 freeze and L6' stand. The post-run review re-measures DEFF, n_eff and MDE and applies the F3 ruling.

Scratch (session k37/): `mrepo4/tools/analysis/own_d4.py`; selftest outputs `st788.txt`, `st788O.txt`.

---

# DELTA READY 3 — ARCH-V2-PILOT-K46 pre-analyze change (L7'), branch archv2-k46-preanalyze @ 586c0d2 (b49715b + 586c0d2, from 5e9de0f; NOT MERGED)

Reviewer: adversarial-reviewer, 2026-09-25. Zero judge calls.

What I did not touch:
- the posting worktree agent-a572e076e3586743c and its branch;
- the run2 store and its journal;
- the record's `--analyze`.

The posting process (PID 53840, `--run --go`, started 07:15) was left running. The only process I stopped was my own hung probe (PID 53176): it lacked a `__main__` guard under Windows spawn, which was my fault, not the build's.

## VERDICT (first)

**READY for `--analyze`, under conditions A1-A6 below.** It runs after posting has ended, FROM THIS BRANCH'S WORKTREE (or an equal-blob checkout).

- No BLOCKER, no HIGH.
- **The crux holds, proved across REAL versions and not with a patched lf16.** I posted on a fixture store with the 5e9de0f code, then analysed that same store with the 586c0d2 code:
  - the store is READ, not refused;
  - the C1 point, interval and reading are identical to the digit to the 5e9de0f analysis;
  - the store files are sha-identical before and after.
- A `--run` relaunch from 586c0d2 IS REFUSED ("the recipe identity differs ... script_blob"). The same relaunch from 5e9de0f is admitted.
- One MEDIUM remains: deviation 4, the K7 falsifier line. It needs a registrar bracket or a code fix before `--analyze` (A4).

## Identity (blob = `git hash-object` = `git rev-parse 586c0d2:<path>`; the working tree is CRLF)

| file | blob (LF) | sha256-lf16 | sha256-crlf16 (working tree) |
|---|---|---|---|
| tools/analysis/archv2_pilot/analysis.py | 79823c7db18daffea3aa68c541bc542b84c808a4 | 981da3e9e5ebbc1d | e3d7a42b4908fb65 |
| tools/analysis/archv2_pilot/outcome.py | 569ac328940018ebf5c1f563ff2a6e00b408b05d | 248b15b124db62e5 | e146aefe90352df8 |
| tools/analysis/archv2_pilot/selftest.py | eb3c61fee638d83f1f9cf7d31c86d79f8e13f248 | 57ff4c1a2ca260e8 | 271243e1d5e3bacc |

- HEAD 586c0d2044698dd27fdb3f0e835cdfd52b9e931f. `git status --short | wc -l` = 0.
- `git diff --name-only 5e9de0f 586c0d2 | wc -l` = 3.
- package_lf16 0fa589da9b13bee5 (= the builder's).
- archv2_pilot_k46.py, pilot.py, accounting.py and judge_v2 are unchanged from 5e9de0f, so the CLI, the transport, the accounting and the pins are those of READY 1f58df5.

## Per-claim table

| # | claim | status | command / evidence | got vs claimed | sev |
|---|---|---|---|---|---|
| 1 | `--analyze` never compares script_blob; only `JudgeWriter.open` (`--pilot` / `--run`) does | **CONFIRMED by a cross-version execution** | `xver.py` (fixture; fake call): POST with mrepo2 = LF archive of 5e9de0f (script_blob `blob:026dc2bd...+archv2_pilot:15e00bb7ee690594`; pilot 24 + run 694, store 718/718). Then `analyze_old` (5e9de0f) and `analyze_new` (586c0d2, package 0fa589da9b13bee5) on the SAME store: both C0 PASS; beta 0.8200993327553086; interval (-0.5304545467676611, 2.1706532122782782); 'UNRESOLVED AT THIS n'; the C1 file's point / bootstrap / READING lines identical (4 of 4). The store's 4 files are sha-identical before and after each analysis. Static: `grep script_blob\|package_lf16\|IDENTITY\|JudgeWriter` in outcome.py finds only the new DISCLOSURE line (L185-L192) | as claimed | - |
| 1a | a relaunch after a rollover must come ONLY from 5e9de0f | CONFIRMED | same probe: `--run` relaunch with 586c0d2's script_blob is **REFUSED** ("[JUDGE-V2] relaunch ... REFUSED: the recipe identity differs ... script_blob"); with 5e9de0f's it is ADMITTED, posted 0 | - | - |
| 1b | the disclosure line never gates | CONFIRMED by my mutant | N9 (a `C.need` on lf16 equality) is KILLED: the builder's check runs analyze with `package_lf16` patched and crashes on the refusal | - | - |
| 2 | F2 DEFF = Var_q / Var_m, own i.i.d. match bootstrap, stream deff/mboot, same B; decides nothing | CONFIRMED; value checked my own way | `deff_own.py` (fixture, B = 200): Var_q (C1's records) 1.0122; builder's match bootstrap 1.0288, so DEFF **0.984** (my recomputation Var_q / V1 = 0.984). My OWN i.i.d. draws (own numpy stream), per-match inner clusters: 0.9955, DEFF 1.017. My own draws with inner clusters = the ORIGINAL question (the alternative to deviation 1): 0.9732, DEFF 1.040. The three agree within Monte Carlo noise. At B = 24 the same fixture printed 0.418, which is pure noise | - | see D-1 |
| 2a | C1 inert under the DEFF | CONFIRMED independently | old vs new code (row 1): C1 identical. workers 1 vs 3 (586c0d2): the C1 file byte-identical and the DEFF dict equal | - | - |
| 2b | the units are per anchor, n = the usable dual-order matches | CONFIRMED | my mutant N1 (units pooled across anchors) is KILLED by 586c0d2's check ({history 359, math 359} vs {181, 178}) | - | - |
| 3 | F3 P3 exactly per the ruling (programme L18077-L18082) | CONFIRMED on 7 cases | my table through `p3_lines`: P EXCL → HELD / HELD; M EXCL → FAILED / FAILED; both → HELD / FAILED; UNRESOLVED → FAILED / HELD; K7 → UNDETERMINED / UNDETERMINED; C0 FAIL (words empty) → U / U; C0 FAIL with words → U / U. 0 wrong. My mutants N3 (P3a HELD on UNRESOLVED) and N4 (the reading ignores C0, i.e. the C0 (d)-void branch) are KILLED | - | - |
| 3a | deviation 4: under K7 the falsifier reads "NOT FIRED" | CONFIRMED as a DEFECT | `falsifier_lines(['UNDETERMINED (3 ...)'])` prints "FALSIFIER NOT FIRED ... ruling 3 (a)'s planning on the M / X columns stands". The ruling says "P3b FAILED if and only if the FALSIFIER FIRES" and "BOTH UNDETERMINED iff C1 gives no reading". Under K7 there is no reading, so the falsifier is NOT READ, and "stands" asserts an outcome the data did not give | - | **D-4 MEDIUM** |
| 4 | G1: P5 = journal + prior | CONFIRMED | my mutant N5 (prior added twice) is KILLED by the builder's end-to-end prior-3 check (721 = 718 + 3) | - | - |
| 5 | G2: my probe added (T2, T3) | CONFIRMED present | the builder's claim; its killing checks pass in the 263 | - | - |
| 6 | F4 verbatim | CONFIRMED | analysis.py `F4_TEXT` equals the text recorded in 1f58df5 / 286a1b0 F4. It prints beside C1 (outcome L387) and C1b (L477), plus the analysis's own reference-class counts and the system-turn sha comparison | - | - |
| 7 | F8 board / loaded counts, print-only (deviation 5) | CONFIRMED print-only, and VACUOUS for the board | my mutant N8 (n_out_board forced to 0) SURVIVES 263/0: `require_inside` refuses before the line on any non-zero count, so the printed number can only ever be 0. The loaded count is a real count | - | D-5 LOW |
| 8 | tests | CONFIRMED | worktree, python and -O: `--part all` 263/0; stage1 24/0; supply 30/0; judge_v2 "ALL PASS (174 checks)"; lint_opens 252 files 0 findings. Scratch baseline for my mutants (LF archive of 586c0d2): 263/0 | equal | - |
| 9 | 11 hook + 11 source mutants killed | NOT re-run one by one | My 6 source mutants: N1, N3, N4, N5 KILLED by check; N9 KILLED by crash; N8 SURVIVES (D-5). In the earlier deltas I verified that mutants are applied to the source and not only through hooks | 5 of 6 | - |

## Rulings on the deviations

- **1, the DEFF definition** (inner clusters = one per drawn match, same B): **ACCEPTED, disclosed.**
  - It is the natural match-level counterpart of C1's (question, copy) form. On the fixture, clustering the inner bootstrap by original question instead moved DEFF by 0.06 at B = 200, inside the Monte Carlo noise.
  - The outcome must print the Monte Carlo precision beside DEFF. With B = 2,000 on each side, SD(ln DEFF) ≈ sqrt(2/1999 + 2/1999) = 0.045, so DEFF x/÷ 1.09 (95%). DEFF stays a MEASUREMENT that decides nothing.
- **2, runtime about +45%, unmeasured at scale: ACCEPTED.**
  - Use `--workers`. Workers 1 vs 3 gave a byte-identical C1 file and an equal DEFF on the fixture.
  - Both bootstraps run BEFORE the C1 file is written, and the record files are write-once. A crash mid-analysis therefore needs a NEW `--out` name, and the aborted attempt is disclosed (A5).
- **3, "HELD / FAILED" for P3 vs "NOT HELD" elsewhere: ACCEPTED.** The ruling orders "HELD / FAILED explicitly". The internal hit tag `PRED.P3b.NOT_HELD` is cosmetic.
- **4, the K7 falsifier line: NOT ACCEPTED as printed.** See D-4 and condition A4.
- **5, F8 print-only: ACCEPTED**, with D-5 disclosed. The board count is a presence check that can only print 0. The binding check is `require_inside`, which refuses.

## Defects

- **D-4 MEDIUM.**
  - Under K7 (non-finite replicate or point), the outcome would print "FALSIFIER NOT FIRED ... planning ... stands" while P3a / P3b read UNDETERMINED. This contradicts the ruling's "P3b FAILED iff the falsifier fires".
  - Fix, either of:
    - (a) code: `falsifier_lines` returns "FALSIFIER NOT READ (C1 gives no reading: <words>)" when `c1_has_reading` is False, plus a check under a K7 world. This needs a short delta check before `--analyze`.
    - (b) a registrar bracket BEFORE `--analyze`: "if K7 fires, the FALSIFIER line is read NOT READ, whatever the instrument prints", applied by the post-run review.
  - The C0-fail and C0 (d)-void branches return before the falsifier line, so they are not affected.
- **D-5 LOW.** The F8 board count is vacuous (above). Disclose it in the outcome, or drop the number and print "require_inside PASSED".
- **D-6 INFO.** The F4 constant quotes 1,846 / 2,664 from the dry-run. The line beside it prints this analysis's own counts. If they ever differ, the analysis's counts govern.

## HOW `--analyze` IS RUN

- **A1. When.** Only after the posting process has EXITED and its transcript shows the run complete.
  - A "DAY ROLLOVER" stop is relaunched ONLY from the posting worktree at 5e9de0f (L5'). Never from this branch: I proved the relaunch refuses.
  - `--analyze` on a store with pending slots writes `_PARTIAL` with C0 FAIL and no reading. That is safe, but do not do it on purpose.
- **A2. From where.** The worktree Z:\FAC\TUBerlin\THESIS\TaxoArena\.claude\worktrees\agent-a2f4fe2a50e2ff614.
  - `git rev-parse HEAD` = 586c0d2044698dd27fdb3f0e835cdfd52b9e931f; `git status --short` empty.
  - The header must print `archv2_pilot lf16 0fa589da9b13bee5` and `judge_v2 pins (MAIN-B653B0A) EQUAL`.
  - A merge of this branch to main first is admissible: it touches only archv2_pilot, not judge_v2, so it is F5-safe. Then run from main with the same three blobs. This READY pins the blobs, not the checkout.
- **A3. The command** (PowerShell):
  ```
  $env:TAXOARENA_DATA_ROOT = 'Z:\FAC\TUBerlin\THESIS\TaxoArena'
  python tools/analysis/archv2_pilot_k46.py --analyze --store Z:\FAC\TUBerlin\THESIS\TaxoArena\experiment_results\archv2\pilot_k46\pilot_k46_verdicts_run2.db --expect-payload-anchor 02f9f17be2ee3bb3f534b7f4ee1845133acf03960604702390b395272fdae815 --rubric-sha256 67f843eb7a632ae5bd411a9debcbaf9dedccd362e0c8355c366c6d85cb89b1dc --out Z:\FAC\TUBerlin\THESIS\TaxoArena\experiment_results\archv2\pilot_k46\archv2_pilot_k46_outcome.txt --workers 6
  ```
  - `--store` is named because DEFAULT_STORE resolves under the checkout it runs from (F7).
  - The `--out` name is proposed; the registrar may name another, but it must be a NEW path (write-once).
  - The header must print the code-identity DISCLOSURE: the store's script_blob `blob:026dc2bd...+archv2_pilot:15e00bb7ee690594`, the manifest's lf16 15e00bb7ee690594, and this analysis's 0fa589da9b13bee5, reading "DIFFERS ... does not compare".
  - C0 (f) must read "journal ... + prior (retired stores) 24".
- **A4.** D-4 is resolved by (a) with a delta check, or by (b) the registrar's bracket, BEFORE the command.
- **A5.** A crash or kill mid-analysis: rerun with a new `--out`, and disclose the aborted files. Never delete them.
- **A6.** Unchanged: the F5 freeze (no judge_v2 commit to main until the outcome is written), and L6' (the retired evidence untouched). The post-run review re-measures and records DEFF, n_eff and MDE (the F2 deviation of 286a1b0 stands), and applies the F3 ruling whatever the code prints.

## What this review does not show

- Any number on the run2 store (not opened).
- The wall time at real scale.
- The builder's 22 hook / source mutants individually.

Probes (session scratchpad k37/):
- `xver.py` (post / analyze_old / analyze_new / relaunch) and `xver3.py` (workers);
- `deff_own.py`;
- `m4.py` / `mutants4.out` (N1, N3, N4, N5, N8, N9);
- scratch repos `mrepo2` (5e9de0f), `mrepo3` (586c0d2).

---

# DELTA READY 2 — ARCH-V2-PILOT-K46 transport fix, branch pilot-k46-generic-rubric @ 5e9de0f (chain 64ff708 -> 5e9de0f; NOT MERGED)

Reviewer: adversarial-reviewer, 2026-09-25. Zero judge calls. Read-only on record data.

Occasion: the pilot 12 on 64ff708 FAILED its gate. The K46 path never called `rejudge_reasoning.load_env()`, so `rr.AZURE_ENDPOINT` stayed None. All 24 invocations raised "ValueError: unknown url type: 'None'", and none reached the network. The journal and the day ledger booked 24.

## VERDICT (first)

**READY for the pilot 12 (store run2) and the run, under launch conditions L1'-L7' below.** This replaces L1-L6 of 286a1b0.

- No BLOCKER. No HIGH.
- The fix is structural and fail-closed. I verified it by execution: my own mutants, two probes, and the record-mode dry-run.
- The C0 (f) change (journal + prior) is ACCEPTED as the registered criterion applied across two stores. It still needs a registrar bracket BEFORE the pilot (condition L1').
- Open from 286a1b0, and still to be settled before `--analyze` and never between the pilot and the run: F2, F3, F4, F5. This review adds G1 (P5's `posted` omits the prior 24).

## Identity (blob = `git hash-object` = `git rev-parse 5e9de0f:<path>`; the working tree is CRLF, so both renderings are given)

| file | blob (LF) | sha256-lf16 | sha256-crlf16 (working tree) |
|---|---|---|---|
| tools/analysis/archv2_pilot/accounting.py | 2e6542ceed6e5f44bab47cd5d1e21537636ab360 | 84a7cf1cd70bae07 | e7fc4d8a134cf6a2 |
| tools/analysis/archv2_pilot/outcome.py | f107ecf00d087c18b37ff3a4f7036c1eb2cfdc37 | e12a97a12a41a583 | 35a491ab28c2ec34 |
| tools/analysis/archv2_pilot/pilot.py | 0784c07512a68b17c9b5f4e8aa208a58f5c5cc70 | fcf327bfddfbd6fb | e4f5edc3873cd172 |
| tools/analysis/archv2_pilot/selftest.py | e2d49501f796079dfd5bf48657bb9c9f0eb4c70f | 46925be7575894ec | a10e1e6a7faadf17 |
| tools/analysis/archv2_pilot_k46.py | 026dc2bd4d7de58cc0195bca1fc710d42e4eb19a | 6da0dbceff58433a | e306f7256d3fcbff |

- The other 7 package / support files are unchanged from 286a1b0's table. `git diff --name-only 64ff708 5e9de0f | wc -l` = 5.
- HEAD 5e9de0f50941a3ab22231018a1d450b6233fdbf9. `git status --short | wc -l` = 0.
- Printed script_blob: `blob:026dc2bd4d7de58cc0195bca1fc710d42e4eb19a+archv2_pilot:15e00bb7ee690594` (= the builder's).
- judge_v2 pins (MAIN-B653B0A): EQUAL at today's main.

## Per-claim table

| # | claim | status | command / evidence | got vs claimed | sev |
|---|---|---|---|---|---|
| 1 | load_transport reads the DATA ROOT's .env through rr.load_env, swapping rr.ROOT and restoring it | CONFIRMED | pilot.py `data_root()` = TAXOARENA_DATA_ROOT, else the main checkout, else C.ROOT; `load_transport` swaps `rr.ROOT` inside try/finally. The dry-run printed "credentials loaded from Z:\...\TaxoArena\.env". rr.load_env (L63-L78) sets only TOKEN, AZURE_ENDPOINT and AZURE_KEY, so PROVIDER, JUDGE_MODEL and MAX_TOKENS from `configure_rr` are untouched. The worktree has NO .env (`ls` fails), so a mis-rooted load fails closed | as claimed | - |
| 2 | the preflight refuses a None / empty endpoint, key or deployment, http, or no host; it runs first in launch() and in --dry-run, before any write | CONFIRMED | In `launch`: after `posting_day_ok` (pure) and before check_store_path, the prior read, the journal open, the store and the ledger. In the CLI: before the plan, for every mode but --analyze. Builder part_transport: 8 refusals, including the literal 'None' URL. Under `-O`, rr.load_env's assert vanishes, so the preflight is the binding guard | - | - |
| 2a | MY MUTANT T1: preflight moved after `Journal.open` | KILLED by the suite (2 failures) | scratch repo = LF archive of 5e9de0f (own git, branch main); baseline 221/0. Under T1 the no-go launch is not refused, and a journal file is written before the refusal | - | - |
| 2b | MY MUTANT T2: preflight skipped when mode == "run" | SURVIVES the suite (221/0); KILLED by my probe | `probe_transport.py` (fixture): pilot passes; then the endpoint is set to None and `launch(..., "run")` is called. Baseline: REFUSED "TRANSPORT PREFLIGHT", store / journal / ledger sha-identical before and after. T2: NOT refused, 694 fake posts. In PRODUCTION T2 stays guarded by the CLI's own preflight (archv2_pilot_k46.py, before `PL.launch`), but the suite tests the launch path in mode pilot only | - | G2 LOW |
| 2c | MY MUTANT T3: load_env reads the worktree root (`data_root` = C.ROOT) | SURVIVES the suite (221/0); KILLED by my probe | Probe (a): `data_root()` with TAXOARENA_DATA_ROOT set. Baseline True; T3 False. Fail-closed today because the worktree has no .env | - | G2 LOW |
| 3 | the key is never printed or logged | CONFIRMED by count | Static: `grep -E 'AZURE_KEY\|api-key'` over the pilot package, the CLI and judge_v2 finds only the preflight's None/empty test, which prints the field NAME. Dynamic: the 3 secret values of main's .env (AZURE_GROK_API_KEY, AZURE_AI_API_KEY, HUGGINGFACE_TOKEN; values read in-process, never printed) were searched byte-wise in 35 files: both dry-run transcripts, every file of pilot_k46/ and the incident copy (store, journal, launch.json, guard file, PILOT.txt), my selftest / mutant outputs, and the 11 package sources. **0 hits.** `call_judge_full` sends the key only as a request header; HTTPError / URLError strings carry no header, and the journal's RAISED note is `str(e)[:200]` | 0 of 3 x 35 | - |
| 3a | "only the host and deployment are printed" | CONFIRMED | "TRANSPORT PREFLIGHT: OK (endpoint host=octave-boelle-student-4735-resou.services.ai.azure.com, deployment=grok-4-1-fast-non-reasoning)" | the Azure resource host goes into transcripts of record | G4 INFO |
| 4 | the retired store is refused; the default is run2 | CONFIRMED | `check_store_path` (basename match) in the CLI before transport and in `launch`; DEFAULT_STORE is `.../pilot_k46_verdicts_run2.db` under C.ROOT (the WORKTREE, F7 of 286a1b0), so `--store` is still named | - | - |
| 5 | PRIOR_JOURNALS pins the retired journal (995087c3...), whose 24 count journal-side | CONFIRMED on data | sha256 of main's `experiment_results/archv2/pilot_k46/pilot_k46_verdicts.db.invocations.db` = 995087c316036df717471c909f94bc19c088485676b4610ff1a085e2eea80375 (= the incident copy). Read `immutable=1`: 24 invocations, all 2026-09-25, 24 distinct slots, 24 RAISED "ValueError: unknown url type: 'None'", 0 unresolved. The retired store has 24 attempts (all ValueError) and 0 verdicts. ValueError is not retried by call_judge_full, so 24 = 24 requests constructed, 0 sent. main day_calls_2026-09-25.json: INDUCE-3 2 + K46 24 | 24 | - |
| 5a | the budget becomes 5,352 of 8,000 and 2,676 of 4,000 matches | CONFIRMED | dry-run: "(i) own 24 (journal 0, store 0, ledgers 24) + 5328 = 5352 of 8000 \| (ii) matches 2676 of 4000 \| (iii) day 2026-09-25: 26 + 5328 = 5354 of 14000 -> OK" | as claimed | - |
| 5b | builder: prior-journal selftest (a new store's pilot refuses "AHEAD" without the prior; wrong sha refused; with it, ledger == new journal + 3, no catch-up row) | CONFIRMED by the suite, 221/0 | - | - | - |
| 5c | C0 (f): P5 uses the same count | **PARTLY** | outcome.py L433-L434 passes `inv` (the run2 journal only) as P5's `posted`, while C0 (f) uses inv + prior | P5 would print 5,328 where C0 (f) prints 5,352 | G1 LOW |
| 6 | the dry-run reproduces, and the shas are unchanged | CONFIRMED to the digit | See the list below | - | - |
| 7 | tests 221 / 24 / 30 / 174 / lint 0 | CONFIRMED | worktree, python and -O: `--part all` 221/0, stage1 24/0, supply 30/0, judge_v2 "ALL PASS (174 checks)", lint_opens 252 files 0 findings | equal | - |

**Claim 6, the dry-run in detail.**
- Before the run:
  - exclusive-open probe: 12 files FREE, 0 busy;
  - processes: an idle Gradle daemon and an idle KotlinCompileDaemon (started 05:23, parent the Gradle daemon), no construction, no python reader.
- The dry-run itself: 9 m 30 s, rc 0. It printed, in this order: the credentials line, then "TRANSPORT PREFLIGHT: OK", then the plan.
- Values, all equal to 286a1b0's:
  - anchors 959a0c45df04ff4ecf086047314a44b10fb2b9f40ccaf773a7b530393981007f;
  - order 89219fc998782da42d8251dcbe540c39adbeecf843654a6fc96d2ab49cf4e208;
  - PAYLOAD ANCHOR 02f9f17be2ee3bb3f534b7f4ee1845133acf03960604702390b395272fdae815;
  - roster 3a3204cc...; EMPTY 0; SHORT 70 / 4,491; ONE 818 / NONE 1,846; leak scan 0 / 5,328;
  - streams log 0ef92c85....
- No write to record: sha, size and mtime taken before and after on 19 files (the 5 SPLIT-2 DBs, both stage-1 records, the day ledger, the 5 retired pilot_k46/ files, the 5 incident copies, the run2 path's directory state). **19 of 19 identical, 0 new.** No run2 store was created.

## Rulings

- **PRIOR_JOURNALS: ADMISSIBLE. It is the honest option for an append-only ledger.**
  - The day ledger already carries the 24 (atl rows are never deleted or reconciled downward: `reconcile` refuses "AHEAD").
  - Only two states were possible without the mechanism:
    - a new store's launch REFUSES forever ("AHEAD", proved by the builder's check and by the design of reconcile);
    - or someone deletes a ledger row, which is forbidden.
  - Pinning the retired journal by sha256 keeps the 24 attributable to their own store. They are read-only (`immutable=1`), refused if altered, and refused if any is unresolved.
  - Condition: the retired files stay where they are, byte-identical (L6'). The PRIOR path is `experiment_results/archv2/pilot_k46/...invocations.db` in the MAIN checkout, not the incident copy.
- **C0 (f): ACCEPTED as the registered criterion, NOT a substitution, but it must be bracketed.**
  - Registered text: "(f) posted calls <= 8,000 and the day ledger agrees", where posted = logical `call_judge_full` invocations (CANARY D2's unit), and "errored calls are counted in the day ledger" (L15925 / L16949).
  - With two stores, "posted" is the sum over both journals. ledger == journal(run2) + prior is that same equality, not a new statistic.
  - Because the CODE changed the formula, the registrar records it by insertion BEFORE the pilot 12 (the C-7 rule: disclosed, never silent).
  - The outcome must print both terms. It does: "journal invocations %d + prior (retired stores) %d".
- **Do the 24 count against the ceiling? YES.** The registration's unit is the invocation, not the network request. The amendment puts errored invocations "on the day ledger inside the 8,000" (L16949). The cost is 24 of the 2,672 margin, leaving 2,648. Excluding them would need a second, non-registered unit ("sent requests"), which the journal cannot witness: it books before the post, by design (K1).

## Findings (new in this delta)

- **G1 LOW.** P5's `posted` (outcome.py L434) is the run2 journal only; C0 (f) and the ceiling use + prior. Fix: pass `inv + prior["invocations"]`. Land it AFTER the run and BEFORE `--analyze`, with F2 and F3, under one delta check. Never between the pilot and the run (script_blob identity).
- **G2 LOW.** The suite exercises the preflight only on the pilot path with an explicit data root, so my mutants T2 and T3 survive 221/0. My probe kills both. Add it to the selftest (same timing as G1).
- **G3 INFO.** The preflight is static: it proves the endpoint, key and deployment are present and well-formed, not that they are VALID.
  - A wrong key or deployment gives HTTP 401 / 404. That raises (not retried), books 24 RAISED invocations and FAILS the gate again, safely. The pilot 12 is the only live transport test, as registered.
  - Each such failure costs 24 of the remaining margin (2,648 after this incident). A retired run2 store would need the same PRIOR treatment by a new build and a new delta check.
- **G4 INFO.** The Azure resource host is printed into transcripts of record. It is not a secret. Say so if the transcripts are published.

## Why the original READY (286a1b0) missed this (a lesson for the record)

1. **The dry-run's scope stops at the payload bytes.**
   - It builds and hashes every payload, scans leaks and counts the budget, but it never constructs a request.
   - The transport lives in module globals of rejudge_reasoning (AZURE_ENDPOINT / AZURE_KEY), set only by `load_env()`.
   - `payload.configure_rr()` / `verify_rr_config()` check PROVIDER, JUDGE_MODEL, MAX_TOKENS and TEMPERATURE, not the endpoint. Every one of those checks passed on a process that could not post.
2. **Every probe of mine replaced `call_full` with a fake.**
   - The write-ahead journal, the rollover and the kill probes all ran on a fake. So the one line that differs between the fake and the real path (`urllib.request.Request(AZURE_ENDPOINT, ...)`) was never executed.
   - My "does not show" said "the behaviour of the real provider". It did not name the posting process's CONFIGURATION as unverified, and it is a different thing: it is checkable at zero calls.
3. **A zero-call static check would have found it.** On the posting path (archv2_pilot_k46.py -> pilot.launch -> judge_v2.writer -> rr.call_judge_full):
   - at 64ff708, `git grep -n load_env 64ff708 -- tools/analysis/archv2_pilot tools/analysis/archv2_pilot_k46.py tools/analysis/judge_v2` finds 3 lines, all in judge_v2/induce_run{,_2,_3}.py, the OTHER runners; the K46 path's own modules (archv2_pilot*, judge_v2 payload / writer / loader / _base) held **0**;
   - every tools/analysis/*.py that calls `call_judge_full(` itself also calls load_env (a per-file check at 5e9de0f: 0 without). The pilot is the one runner that posts through an injected callable, so the rule "whoever calls call_judge_full loads the env" silently did not apply to it.
   - A presence check ("configure_rr is called") passed where a COUNT check (the call sites that fill the transport globals) would have failed. This is rule 10's pattern applied to code.
4. **Proposed standing check for every READY of a posting instrument**, zero calls:
   - (a) name the function that fills the transport globals, and count its call sites on the posting path (required >= 1);
   - (b) the dry-run executes the SAME transport preflight the launch executes, and prints its line;
   - (c) the READY lists "real transport configuration" and "real provider behaviour" as separate items, the first verified, the second left to the pilot.
   - The fix at 5e9de0f implements (b). (a) and (c) are the reviewer's, and are applied here.

## Launch conditions (replace L1-L6 of 286a1b0)

- **L1' Registrar bracket BEFORE the pilot 12:**
  - C0 (f) = "ledger == journal(run2) + prior(retired, sha256 995087c3...)";
  - the incident's 24 invocations count against the 8,000 (budget 5,352 / 8,000; 2,676 / 4,000 matches);
  - the retired store and the run2 store of record.
- **L2' Identity.** Run from Z:\FAC\TUBerlin\THESIS\TaxoArena\.claude\worktrees\agent-a572e076e3586743c.
  - `git rev-parse HEAD` = 5e9de0f50941a3ab22231018a1d450b6233fdbf9 and `git status --short` empty, at every launch.
  - No change to tools/analysis/archv2_pilot* until the run has finished posting.
  - No commit touching tools/analysis/judge_v2/* reaches main until the outcome is written (F5).
- **L3' Day.** 2026-09-25 or later, with main's ledger. The JUDGEBENCH check must print 0 before EVERY launch or relaunch (JB is READY as of f9a199c and posts only after the K46 run of record):
  `python -c "import json,os,time;p=r'Z:\FAC\TUBerlin\THESIS\TaxoArena\experiment_results\day_calls_%s.json'%time.strftime('%Y-%m-%d');r=json.load(open(p)) if os.path.exists(p) else [];print(sum(str(x.get('test','')).upper().startswith('JUDGEBENCH') for x in r))"`
- **L4' Pilot 12** (PowerShell):
  ```
  $env:TAXOARENA_DATA_ROOT = 'Z:\FAC\TUBerlin\THESIS\TaxoArena'
  python tools/analysis/archv2_pilot_k46.py --pilot 12 --go --store Z:\FAC\TUBerlin\THESIS\TaxoArena\experiment_results\archv2\pilot_k46\pilot_k46_verdicts_run2.db --expect-payload-anchor 02f9f17be2ee3bb3f534b7f4ee1845133acf03960604702390b395272fdae815 --expect-order-sha 89219fc998782da42d8251dcbe540c39adbeecf843654a6fc96d2ab49cf4e208 --rubric-sha256 67f843eb7a632ae5bd411a9debcbaf9dedccd362e0c8355c366c6d85cb89b1dc
  ```
  - Required lines before any post:
    - "transport: credentials loaded from Z:\FAC\TUBerlin\THESIS\TaxoArena\.env";
    - "TRANSPORT PREFLIGHT: OK (endpoint host=octave-boelle-student-4735-resou.services.ai.azure.com, deployment=grok-4-1-fast-non-reasoning)";
    - "prior journals (retired stores; counted on the journal side): 24 invocation(s) {"2026-09-25": 24}".
  - Any other value: stop.
- **THE PILOT-12 GATE.** The run may start only when ALL of the following hold:
  - `[PILOT-GUARD] PASS: pilot matches 12, cached order verdicts 24 of 24, ... unusable 0, foreign rows 0`;
  - `<run2 store>.pilot_guard.json` exists;
  - `[JOURNAL] ... journal invocations N + prior 24 = ledger N+24`;
  - main's ledger shows ARCH-V2-PILOT-K46 = 24 + N.
  - A FAIL (including HTTP 401 / 404, G3) goes to the registrar. It is never relaunched into run2 without a ruling.
- **L5' Run:** the same line with `--run` in place of `--pilot 12`.
  - "DAY ROLLOVER" is a clean stop: relaunch the same line on the new day after L3'.
  - Any other refusal (ACCOUNT REFUSED, pins DIFFER, recipe identity differs, TRANSPORT PREFLIGHT REFUSED) goes to the registrar.
- **L6' The retired evidence.** Do not move, open read-write, or delete these before the outcome is written (PRIOR_JOURNALS reads the first by sha; the second is the backup):
  - experiment_results/archv2/pilot_k46/pilot_k46_verdicts.db*;
  - experiment_results/archv2/pilot_k46_incident_2026-09-25/.
  - Both sets are byte-identical today: store 84f00117..., journal 995087c3..., launch.json 7f685fef..., guard 4f392a27..., PILOT.txt fa725750....
- **L7' Before `--analyze`** (not covered by this READY):
  - F2 (the measured DEFF), F3 (the P3b scoring) and G1 (P5 + prior), in one code delta with its own check;
  - F4's disclosure in the outcome record;
  - G2's probe added to the selftest.

## What this review does not show

- That the endpoint, key and deployment are ACCEPTED by the provider. Only the pilot shows that (G3).
- Any judged number.
- The behaviour of a relaunch into run2 after a transport failure.

Probe scripts (session scratchpad k37/):
- mutants: `m3.py`, output `mutants2.out`;
- `mrepo2/tools/analysis/probe_transport.py`. Its closing VERDICT line mislabels the baseline; read its (a) and (b) lines;
- dry-run transcript: `dryrun2.txt`;
- snapshots: `before2.json` / `after2.json`;
- `excl_probe.py`.

---

# DELTA READY — ARCH-V2-PILOT-K46 at k = 37, branch pilot-k46-generic-rubric @ 64ff708 (2fe8420 merge + 1f84bf3 + 64ff708; NOT MERGED)

Reviewer: adversarial-reviewer, 2026-09-25. Zero judge calls. Read-only on record data. This is the first independent review of the build since 65a9173 (fb3a893 K1-K10, 98d521b re-pin, edc09f9 k 37, and the three commits above were never reviewed), so it covers the whole delta. Record checked: programme L15913-L15955, L15975-L15983, L16074-L16090, L16787-L16992 (0761cfa), L16994-L17006, L17610-L17700 (c09440e).

## VERDICT (first)

**READY for the pilot 12 and the run, under launch conditions L1-L6 below.** No BLOCKER and no HIGH. Four MEDIUM findings: F1 is a launch condition. F2 and F3 must be settled before `--analyze`, and must NOT land in code between the pilot and the run, because `script_blob` is in the store's recipe identity (`writer.IDENTITY_KEYS`) and a relaunch then REFUSES. F4 is a disclosure owed by the registrar's outcome. Every builder number reproduced to the digit.

## Identity (hash kinds named; the working tree is CRLF (`git ls-files --eol`: w/crlf), so both renderings are given; blob = `git hash-object`, equal to `git rev-parse 64ff708:<path>` for all 12)

| file | blob (LF) | sha256-lf16 | sha256-crlf16 (working tree) |
|---|---|---|---|
| tools/analysis/archv2_pilot/__init__.py | 64fc4a4e3e50b55f5968ff3ef767fc6d8eb2e168 | 3d61dd2b7ceaa68c | e33ab3d9b8bb1641 |
| tools/analysis/archv2_pilot/accounting.py | a9cf15a7e969554630a1d6afcc449455c028b728 | 8ec08fa2a2a689ab | e1db0f3af5268535 |
| tools/analysis/archv2_pilot/analysis.py | 0724140d63844b0cd98ad70f62b3d956b8998515 | 94b3cd2ccb5bff62 | a53be326a4e0b401 |
| tools/analysis/archv2_pilot/common.py | 467d0efb4bc13b386f655a7980b830a78f44280f | e7dc47adc40fb081 | 9ef19dd64d9131c3 |
| tools/analysis/archv2_pilot/outcome.py | 5bf34a6d97a723403681d07945df88cc975e8376 | b9e5fab1527c4ae3 | 44e5ba3a479160bf |
| tools/analysis/archv2_pilot/pilot.py | 5acecdaf2551009b51640d420b53704950b1cec6 | b783d66478b38968 | 85e31c89f448d5fe |
| tools/analysis/archv2_pilot/selftest.py | b33269be3bd1e4ceb3d261fb0a5ad3c77ddad74b | b078afcdcb9c8d3f | c995060462f60c95 |
| tools/analysis/archv2_pilot/stage1.py | cfae76b06fb74919ee7b10b9dbad94817403a787 | 1e81e58fc7dfc4bb | b9291bf6a70e4802 |
| tools/analysis/archv2_pilot/supply.py | 22fc9a059f8082202579cf1a60999e200764a1eb | f449b422b3475432 | ac1b2105e6397ce0 |
| tools/analysis/archv2_pilot_k46.py | 47ca2286f6d4042b2cf9772769652f89fd6476df | 3cbea5f5cb032179 | ff59486df495a3cf |
| tools/analysis/rubric_value_contrast.py (imported; GENERIC_RUBRIC L69) | 9e1541a7bdf1260268c850ccac81db4570c064e4 | adc15a4a89454038 | 9a54b76ce2812610 |
| tools/analysis/accepted_tests_ledger.py (main's) | a4a1d7eedc0846ba601a8aba557166447f22d2e5 | b108bb76600151f1 | 3147e6cdeab6773a |

- HEAD 64ff7084e53f5a8f9801b5dd9a805ba8276d6e87. `git status --short | wc -l` = 0.
- Printed code identity (dry-run L2): `blob:47ca2286f6d4042b2cf9772769652f89fd6476df+archv2_pilot:f720dcf26d576a95`. Frozen instrument lf16 876d01413318bd7b.
- judge_v2, 7 files, blob (LF). Worktree = main (f9a199c) = b653b0a: _base 6f25e4ce, payload 4b0af34d, leakage d4c4d6b3, combiner 19c7c566, writer 6db4ab32, induction 147e6874926b65393037cdcacd0e29aa308651ef, loader da4fcbbf.
- Main since b653b0a: `git diff --name-only b653b0a main | grep -vc '^docs/'` = 0.

## Per-claim table

| # | claim | status | command / evidence | got vs claimed | sev |
|---|---|---|---|---|---|
| 1 | the merge 2fe8420 brought in only main's side | CONFIRMED | `diff <(git diff --name-only edc09f9 2fe8420) <(git diff --name-only 39c81c0 b653b0a)` is empty (23 = 23). `git diff --name-only b653b0a 2fe8420` = the 7 branch files only. `git diff edc09f9 2fe8420 -- <those 7>` is empty. | a pure union; induction.py 19eb10fa -> 147e6874 as the builder lists | - |
| 2a | 1f84bf3 / 64ff708 touch only the pilot package | CONFIRMED | `git diff --stat 2fe8420 64ff708`: accounting, outcome, pilot, selftest, archv2_pilot_k46.py (5 files); `git diff --name-only 64ff708 main \| grep -v '^docs/'` = the 8 branch files | no src/, config, .env or .gitignore | - |
| 2b | every k = 37 amendment item is implemented (checked against L16787-L16992, not the builder's list) | PARTLY | Roster rule, the 9, registry 47 / 46 ACTIVE / QUARANTINED, sha, ARENA12: pilot.py L99-L108 / L468-L473; C0 (b) out-of-roster (scheduled + cached) and EMPTY = 0: outcome.py L190-L203; C0 (h): dry-run; exact M from k (`exact_bar_M`, compared unrounded); C1b P 0.3556 / M 1.0878 from L12, memo bars not printed (no executable token 0.38 / 0.85 / 1.36 / 1035 / 2.05 / 2.0484 in the 6 modules, tokenize scan; the only `46` is `active_n = 46`, correct); C1c rungs (12, 20, 28, 37), B_rungs 200; C2 EMPTY / SHORT (< 40, raw zlib output before robust_trace, short non-empty separately, denominators); K8 thin at > 2% (>= 14 of 666); arx_0314 DISCLOSURE beside C1 (L341) and C1b (L423); roster sha in the manifest (pilot.py L1186) and the outcome (L284); P2b [0.6, 1.3], P4 [1,540, 2,664] with t = 0. **NOT implemented: Support (b) "The measured question-clustered DEFF is printed post-run (K10 (a))" (L16893)** | `grep -n -i deff archv2_pilot/*.py` gives 1 line, analysis.py L334 "DEFF: not applicable". `n_eff(questions) = q_used` (L330) is the K10 (a) mislabel of 65a9173, still unfixed | F2 MEDIUM |
| 2c | P3 scoring | PARTLY | analysis.py L464-L465: P3b is "HELD" iff the reading is 'M EXCLUDED' | the registered 0.13 is the forecast probability OF 'M EXCLUDED' (declared model, L16921-L16924), so a 13% event would be scored as a held prediction | F3 MEDIUM |
| 3a | the slot is GENERIC_RUBRIC, 81 chars, sha256-text 67f843eb..., record mode refuses any other text | CONFIRMED | `PL.load_generic_rubric(record=True)` gives 67f843eb7a632ae5bd411a9debcbaf9dedccd362e0c8355c366c6d85cb89b1dc, 81, "Grade the response based on domain correctness, precision, and logical reasoning." Record branch: sha + length `need`s (pilot.py L395-L398); `check_rubric_args` refuses the INDUCE-1 arguments; `load_rubric(record=True)` refuses first | equal | - |
| 3b | `build_system(slot)` = STACK-NORUBRIC's system turn, sha d0c524bb... | CONFIRMED, and stronger than claimed | Own script: sha256-text of `P.build_system(rub)` = d0c524bbd66b5a5e9781f049c93584401f27ed503742c687733afa03a2a7171e. **Against the MEASURED arm, not only the live code**: `stack_norubric.db` (opened `mode=ro&immutable=1`), `SELECT arm, sys_sha, count(*) ... GROUP BY arm, sys_sha` gives norubric d0c524bbd66b5a5e on **944 of 944** rows (sys_sha = sha256[:16], stack_norubric.py L320) | byte-identical to the turn that was judged | - |
| 3c | persona GENERIC_SYSTEM 3a5e223c... | CONFIRMED | sha256-text 3a5e223c26f32c8e68a1a40b05f1fc9e63a36434eb9613830f5641c06253ddb9; `payload.FIXED_SYSTEM_PERSONA == rvc.GENERIC_SYSTEM` True | equal | - |
| 3d | the "unmeasured on E-J's layer" caveat is disclosed | PARTLY | It is in the record (L17002; L17696 NOT SHOWN), NOT in the instrument's output. `grep -i unmeasured archv2_pilot/*.py` = 0. The header prints "(= STACK-NORUBRIC's measured combination: True)", which is true of the system turn only. The user turn is E-J's (stem-only query; reference as letter + option text). **1,846 of 2,664 matches (69.3%) carry NO reference** (dry-run, loader line), whereas every one of STACK-NORUBRIC's 944 measured rows had one (`stack_norubric.build` returns "no reference" and skips) | disclosure owed | F4 MEDIUM |
| 4a | the induction.py layer-identity pin | RULING: **KEEP** | pilot.py L83 `from judge_v2 import induction as JI` runs the module's top level in the posting process; `judge_v2._base.pin_table()` (L139-L142) writes induction.py into the store's pins and the launch manifest. Dropping the pin would leave an executed, recorded file unchecked, which is the K2 class | - | - |
| 4b | the 7-file check against main (deviation 1) | ACCEPTED, with a condition | `judge_pins_ok` requires live = pin = `git rev-parse main:<f>` for each of the 7; all 7 EQUAL at f9a199c. It runs at the header, at every launch (L1126) AND at `--analyze` (outcome.py L152) against LIVE main | a judge_v2 merge to main before the outcome voids C0 (c) after the spend | F5 MEDIUM (L5) |
| 5a | the rollover fix: a clean stop before the journal row and the post | CONFIRMED by execution, plus my own mutants | Scratch copy of 64ff708 (`git -c core.autocrlf=false archive`, LF, own repo with branch main): baseline 199/0. **R1** check moved after the post: KILLED (the journal holds 4, not 7). **R2** finally `ACC.append` without `day=` (the JB D1 class): KILLED by the relaunch leg. **R4** journal row dated by the live clock: KILLED. **R3** production default clock made constant (`else (lambda: day)`): **SURVIVES 199/0**, because every selftest launch passes `today=` or `clock=` | the production path is untested by the suite | F6 LOW |
| 5b | the production default clock stops at midnight | CONFIRMED by my probe | `probe_prod_clock.py`: `launch(today=None, clock=None)`, only `accounting.time.strftime` rolls over after 5 posts. Baseline: "DAY ROLLOVER" after 5; journal {25: 5} = ledger {25: 5}. Under R3: NO STOP, 24 posts booked to the 25th | the probe kills R3 | - |
| 5c | "there was no double count before the fix" | CONFIRMED | `git show 1f84bf3:.../pilot.py`: L1117 `ok_day, day = posting_day_ok(cfg, today)`, L1203 `wrap_call(..., day, ...)`, L1209 `ACC.append(..., day=day)`; accounting.py L246/L249 `journal.pending(..., day)`. The same `day` reaches journal and ledger, so `reconcile` agrees per day. The pre-fix defect was MIS-DATING (posts after midnight booked to the start day), not a double count. The builder's L1120 / L1216 are the 64ff708 lines | as claimed | - |
| 5d | K1 write-ahead (65a9173 HIGH), never re-reviewed | CONFIRMED by a hard-kill probe | `probe_k1_kill.py`: `os._exit` after the 9th post returns. Relaunch: "reconciled after crash: 9", invocation 9 ORPHAN, 16 posted. Fake posts 9 + 16 = 25 = journal 25 = ledger 25; store attempts 24; guard PASS | the 65a9173 flaw is gone | - |
| 6 | the record-mode dry-run reproduces at 64ff708 (TAXOARENA_DATA_ROOT = main) | CONFIRMED to the digit | Exclusive-open probe (CreateFileW, share 0) on the 5 SPLIT-2 files + embeddings_cache/snapshots/snapshots_frozen (+ -wal/-shm): 12 FREE, 0 busy. Processes: 2 foreign `--selftest` (admitted, W2); 29 GB free RAM. Run 10 m 45 s, rc 0. Diff against the builder's 1f84bf3 transcript: only the header join (fixed in 64ff708) and path spelling | see the table below | - |
| 7a | the pilot uses main's day ledger; today = 2 | CONFIRMED | dry-run: "ledger of record: Z:\...\TaxoArena\experiment_results\day_calls_2026-09-25.json", "(iii) day 2026-09-25: 2 + 5328 = 5330 of 14000"; the file holds 1 row (ARCH-V2-INDUCE-RUBRIC-3, 2 calls); K9 refuses any other directory | equal | - |
| 7b | the pilot refuses on a day carrying a JUDGEBENCH row | **REFUTED** | `grep -n -i judgebench archv2_pilot/*.py` = 1 line, a docstring (accounting.py L25). `guard_day` (L68-L99) checks (i) own, (ii) matches, (iii) the day total only. JB's own runner refuses a K46 day, but not the reverse (JB review D4 (a)). JB is now READY (f9a199c) | a condition, not code | F1 MEDIUM (L3) |
| 8 | launch line and the pilot-12 gate | CONFIRMED with conditions | The CLI posts only with `--go`; a record launch needs `--expect-payload-anchor` and `--expect-order-sha` (L1133); the first launch must be the pilot; `--run` needs `<store>.pilot_guard.json` and 24/24 usable pilot slots. `DEFAULT_STORE` is under the WORKTREE (`C.ROOT`), so name `--store` | see L1-L6 | F7 LOW |
| 9 | tests | CONFIRMED | `selftest.py --part all` 199 checks / 0 failed (python and -O); `--part stage1` 24/0 and `--part supply` 30/0 (both); `judge_v2/selftest.py` "ALL PASS (174 checks)" (both); `lint_opens.py --root .` 252 files, 0 findings, 17 allowlisted (both) | 199 / 24 / 30 / 174 / 0 as claimed | - |
| 10 | no write to record | CONFIRMED | sha256 + size + mtime of the 5 SPLIT-2 DBs, both stage-1 records, and day_calls_2026-09-25.json (main and worktree copies) before and after the dry-run: 9 of 9 identical. 0 -wal / -journal / -shm beside the SPLIT-2 DBs. No `experiment_results/archv2/pilot_k46` was created (count 0) | - | - |

### The dry-run, reproduced (64ff708) against the builder's (1f84bf3)

| item | reproduced | builder |
|---|---|---|
| C0 (b) roster | 37; sha 3a3204cc35cf600495506e6e1f545ab379707b26c16371df78ce654837846f91; dropped 36e10ea298adf62d78bd88f0ba5caaa5146507644d4cd55238c11040c9ce29b4; EMPTY 0; SHORT 70 of 4,491 cells; out-of-roster scheduled 0 | same |
| independent (own SQL, `immutable=1`; own seeds) | registry 47, 46 ACTIVE, 1 QUARANTINED (Meta-Llama-3-70B-Instruct); the 9 ACTIVE; the same two shas; ARENA12 12 in / 0 dropped; seeds anchors 1224499560724031674 (= 65a9173's); the pilot's 2 of the 7: health, math | - |
| C0 (c) | judge_v2 pins (MAIN-B653B0A) EQUAL | EQUAL |
| C0 (g) | anchors sha 959a0c45df04ff4ecf086047314a44b10fb2b9f40ccaf773a7b530393981007f; order sha 89219fc998782da42d8251dcbe540c39adbeecf843654a6fc96d2ab49cf4e208; questions = schedule digest 38a44632ad22d4378e7cb089ff71191141d44a40bc6c8d1810a5dbdd9abaceb9; trim digest e3b0c442... (empty) | same |
| C0 (h) | 2,664 = 2 x 2 x 666, t = 0; ARENA12 pairs kept 132 of 132 | same |
| schedule | health 204 questions, 161 used (uses 7 / 8 / 9); math 405, all used (3 / 3 / 4); exhausted 0 / 0; K8 mask cells lost 0 / 0; not thin | - |
| loader | 2,664 -> 2,664; reference ONE 818 / NONE 1,846; excluded 0 | same |
| leak scan | 5,328 of 5,328; hits 0 | same |
| PAYLOAD ANCHOR | 02f9f17be2ee3bb3f534b7f4ee1845133acf03960604702390b395272fdae815 | same |
| accounting | (i) 0 + 5,328 = 5,328 of 8,000; (ii) 2,664 of 4,000; (iii) 2 + 5,328 = 5,330 of 14,000 | same |
| streams log | 3 streams, sha256 0ef92c859bc632ac17b8179357c6a2a90b65a97cb83e1717e76db88113e54064 | same |

Support (rule 8), re-derived from the amendment's constants: ln(37/12) = 1.126011; Var_boot = [(0.22^2 + 0.20^2)/2] / 1.267901 = 0.034861; SE_boot 0.18671; SE_dec 0.23422; x 1.25 = 0.29278; MDE 0.81978; separation 0.99294 > MDE, so SCOREABLE reproduces. DEFF: "not applicable; the interval is the question-clustered bootstrap", declared (2296877), non-vacuous. The measured cluster structure is heavier than planned on health: 1,332 matches on 161 questions (uses 7-9) against the planning Kish 6.5 (204 questions). The verdict line tolerates SE_dec up to 1.51 x plan. The post-run review re-measures this; not re-derived here.

## Defects (by severity)

- **F1 MEDIUM, operational: no JUDGEBENCH refusal in the pilot.**
  - Claim 7b is REFUTED. atl.append has no cross-test lock (JB review D9), so a JB post on a pilot day can lose a ledger row. C0 (f) then fails after the spend.
  - Fix, either of:
    - (a) `guard_day` refuses when the posting day's ledger holds any row whose test starts with JUDGEBENCH. This is a code change: it must land before the pilot, with a delta check.
    - (b) Launch condition L3 at EVERY launch and relaunch, plus the JB D4 (a) ordering: JB posts only after the pilot's run of record has finished posting.
  - This review accepts (b).
- **F2 MEDIUM: an amendment item is not implemented.**
  - The measured question-clustered DEFF is not printed post-run (L16893, K10 (a)), and `n_eff(questions) = q_used` is still mislabelled.
  - Fix, either of:
    - add it to `support_lines`: DEFF = question-clustered over match-level bootstrap variance of beta-hat, n_eff = n / DEFF, printed beside SE_dec and MDE. Land it AFTER the run and BEFORE `--analyze`; `--analyze` does not check script_blob. The hunk needs its own delta check.
    - the registrar records a deviation: the post-run review computes DEFF from the store.
  - Never between the pilot and the run.
- **F3 MEDIUM: P3b is scored HELD when the 13% event 'M EXCLUDED' occurs.**
  - The registrar rules before `--analyze`: either score P3 as a probabilistic forecast (print the realised reading beside 0.79 / 0.13, no HELD / NOT HELD), or read P3b as "not M EXCLUDED" (0.87).
  - The code follows after the run, as for F2.
- **F4 MEDIUM, disclosure.**
  - The outcome of record must say, beside C1 and C1b: "system turn byte-identical to STACK-NORUBRIC's measured norubric arm (944 of 944 rows, sys_sha d0c524bbd66b5a5e); the user turn is E-J's; 1,846 of 2,664 matches (69.3%) carry no reference, a branch STACK-NORUBRIC never measured; GENERIC_SYSTEM + GENERIC_RUBRIC on E-J's layer is UNMEASURED."
  - The instrument's "(= STACK-NORUBRIC's measured combination: True)" is not to be quoted without it.
  - Both rungs share the same reference branch per question, so the NONE share is not a rung-specific bias. Descriptive only.
- **F5 MEDIUM, operational.** C0 (c) at `--analyze` re-reads LIVE main. No commit touching tools/analysis/judge_v2/* may reach main between the pilot launch and the written outcome (condition L5).
- **F6 LOW.**
  - The suite never runs the production default clock: my mutant R3 survives 199/0.
  - My probe (`today=None`, `accounting.time` rolled) kills it and shows the baseline stops.
  - Add it as a selftest check, never between the pilot and the run.
- **F7 LOW.** `DEFAULT_STORE` resolves to the worktree. The launch lines name the main checkout's path.
- **F8 LOW.** C0 (b) counts scheduled and cached out-of-roster rows. "loaded" and "board" are implied by construction and not counted separately.
- **F9 INFO.** The pilot guard fails on ANY unusable verdict (INVALID, content_filter), as registered.
  - At P5's 1% per call, P(>= 1 in 24) = 1 - 0.99^24 = 0.214.
  - A FAIL has no in-store recovery (verdict rows are append-only). The next step is the registrar's (e.g. a new store, disclosed, with the posts on the ledger).
- **F10 INFO.** analysis.py's module docstring (L23-L25) still describes k 46 bars. It is superseded by its own bracket (L43-L46). No executable k-46 value remains.

## Launch conditions (the pins and lines for the registrar)

- **L1 Identity.** Run from Z:\FAC\TUBerlin\THESIS\TaxoArena\.claude\worktrees\agent-a572e076e3586743c.
  - `git rev-parse HEAD` = 64ff7084e53f5a8f9801b5dd9a805ba8276d6e87 and `git status --short` empty, at every launch.
  - Nothing in tools/analysis/archv2_pilot* changes until the run has finished posting.
- **L2 Posting day.** 2026-09-25 or later, with main's ledger. The header must print "ledger directory: Z:\FAC\TUBerlin\THESIS\TaxoArena\experiment_results".
- **L3 JB check, before EVERY launch or relaunch; it must print 0:**
  `python -c "import json,os,time;p=r'Z:\FAC\TUBerlin\THESIS\TaxoArena\experiment_results\day_calls_%s.json'%time.strftime('%Y-%m-%d');r=json.load(open(p)) if os.path.exists(p) else [];print(sum(str(x.get('test','')).upper().startswith('JUDGEBENCH') for x in r))"`
- **L4 Pilot 12** (PowerShell):
  ```
  $env:TAXOARENA_DATA_ROOT = 'Z:\FAC\TUBerlin\THESIS\TaxoArena'
  python tools/analysis/archv2_pilot_k46.py --pilot 12 --go --store Z:\FAC\TUBerlin\THESIS\TaxoArena\experiment_results\archv2\pilot_k46\pilot_k46_verdicts.db --expect-payload-anchor 02f9f17be2ee3bb3f534b7f4ee1845133acf03960604702390b395272fdae815 --expect-order-sha 89219fc998782da42d8251dcbe540c39adbeecf843654a6fc96d2ab49cf4e208 --rubric-sha256 67f843eb7a632ae5bd411a9debcbaf9dedccd362e0c8355c366c6d85cb89b1dc
  ```
- **THE PILOT-12 GATE.** The run may start only when ALL of the following hold:
  - the launch printed `[PILOT-GUARD] PASS: pilot matches 12, cached order verdicts 24 of 24, ... unusable 0, foreign rows 0`;
  - `<store>.pilot_guard.json` exists;
  - `[JOURNAL] ... journal invocations N = ledger N` (N >= 24; N > 24 only with the ERRORED count printed);
  - main's day ledger gained exactly N rows' worth for ARCH-V2-PILOT-K46.
  - A FAIL stops the test and goes to the registrar (F9).
- **L5 Run:** the same line with `--run` in place of `--pilot 12`.
  - A "DAY ROLLOVER" stop is a clean stop. Relaunch the same `--run` line on the new day after L3.
  - Other stops: `[ACCOUNT] REFUSED`, a pin DIFFER, or "the recipe identity differs". Do not relaunch after any of these; they go to the registrar.
  - No commit to main touching tools/analysis/judge_v2/* until the outcome is written (F5).
- **L6 Before `--analyze`** (not covered by this READY):
  - F2 and F3 are resolved, the code by a delta check;
  - F4's disclosure text is in the outcome record;
  - the post-run review re-measures DEFF, n_eff and MDE from the store.

Record pins for the registrar:
- eval_view e35b7518878205837bfd16266dfdd8a6e76a226ed67957796d1d33cb72b5e369 (sha256 of the bytes);
- stage-1 record experiment_results/archv2/stage1_anchor_draw_2/archv2_stage1_anchors_2.json, sha256-lf 777e2f6a4cd8ee0d1ce92659f8c3ad4f72a45319d166135dd918575d0ace5e43;
- GENERIC_RUBRIC 67f843eb7a632ae5bd411a9debcbaf9dedccd362e0c8355c366c6d85cb89b1dc;
- persona 3a5e223c26f32c8e68a1a40b05f1fc9e63a36434eb9613830f5641c06253ddb9;
- system turn d0c524bbd66b5a5e9781f049c93584401f27ed503742c687733afa03a2a7171e (all three sha256-text);
- the digests and the payload anchor in the table above.

## What this review does not show

- Any judged number.
- The behaviour of the real provider under the pilot. A fake call_full was used in every probe.
- K4-K8 beyond the builder's selftest mutants, which all pass. My independent probes were K1 and the rollover.
- The measured cluster DEFF.
- That GENERIC_RUBRIC performs on E-J's layer as it did under STACK-v2.

Probe scripts (session scratchpad k37/): `excl_probe.py`, `snap.py` (before.json / after.json), `indep.py`, `mutants.py` (mutants.out), `mrepo/tools/analysis/probe_prod_clock.py`, `mrepo/tools/analysis/probe_k1_kill.py`, `dryrun.txt`.

---

# READY review — ARCH-V2-STAGE1-ANCHOR-DRAW, the supply-json builder, ARCH-V2-PILOT-K46 (branch archv2-pilot-k46 @ 62e2688)

Reviewer: adversarial-reviewer, 2026-09-24. Zero judge calls. Nothing was run on the split of record, and nothing was posted. The work was selftests, mutants, fixture probes and reading the code. The DBs of record and the ledgers are unchanged: size, mtime and sha256 were taken before and after, and `diff` printed IDENTICAL. The records checked are `eval_view_REG.db`, `gen_view_REG.db`, the two corpus_v2 DBs, the split DB, and `day_calls_2026-09-24.json` in both main and the worktree.

## VERDICTS (first)

| tool | verdict |
|---|---|
| ARCH-V2-STAGE1-ANCHOR-DRAW (`archv2_stage1_anchor_draw.py`, `archv2_pilot/stage1.py`, `common.py`) | **READY** |
| supply-json builder (`archv2_supply_json.py`, `archv2_pilot/supply.py`) | **READY as a tool.** Use is restricted by ruling R-G22 below: the 7-anchor file never feeds D1-full or the stop. |
| ARCH-V2-PILOT-K46 (`archv2_pilot_k46.py`, `archv2_pilot/{pilot,analysis,outcome,accounting}.py`) | **NOT READY.** Two HIGH conditions (K1, K2). One registered precondition is unmet: the rubric artefact's shas are not in the programme. Four choices change registered quantities and need registrar rulings (K5, K6, K7, K8). |

## Identity (hash kinds named; the working tree is LF for all 12 files per `git ls-files --eol`, so no CRLF rendering exists)

- Commit 62e2688 adds exactly 12 files and modifies none. Proved by count with `git diff --diff-filter=AM --name-status 53eccb6 62e2688 | awk '{print $1}' | sort | uniq -c`, which prints `12 A`. `git diff --name-only 53eccb6 62e2688 -- tools/analysis/judge_v2 tools/analysis/archv2_arena tools/analysis/accepted_tests_ledger.py | wc -l` prints 0.
- archv2_pilot package_lf16 (the builder's composite: sha256 over rel NUL LF-bytes, 8 files) = **8d391ed8d8089270**. Reproduced with `C.package_lf16()`.
- Frozen instrument lf16 **876d01413318bd7b**, reproduced with `g22.instrument_lf16()` over the 11 `INSTRUMENT_FILES`.
- judge_v2 at 62e2688: the 7 live blobs equal f5bbbda's and main's. `pin_table()` computes them live (`git_blob_lf`), and `judge_pins_ok()` returns (True, {}).
- accepted_tests_ledger.py is blob:4e9db106c2ebeaea8674b2a5a6227f1d9b838ccf (unchanged).

| file | blob (LF) | sha256-lf16 |
|---|---|---|
| tools/analysis/archv2_pilot/__init__.py | a44f421f642aab07606ef9d2695d429852e7d8a1 | 8b4f24b93d2f9d51 |
| tools/analysis/archv2_pilot/accounting.py | 1ca7cfda2dbd21046e0f1a45533dfd526de7d4b2 | fbe59bc79203850b |
| tools/analysis/archv2_pilot/analysis.py | 493095fe9cba7ed789e485bf4a95aceb12ac83f7 | 00ede202fc372361 |
| tools/analysis/archv2_pilot/common.py | a3346c6a95e5b9adaef973f2863174da204c1837 | 4f9d7165a3f70cf2 |
| tools/analysis/archv2_pilot/outcome.py | 1ef003b560ea6a6d019eb05cae1750360e5ee628 | a9a5b4990b887265 |
| tools/analysis/archv2_pilot/pilot.py | b34d60895e5f67de18533a581c678e7aadff9ef8 | eaaab46d39d98b6b |
| tools/analysis/archv2_pilot/selftest.py | 8ca87487f1e5e43d01ea09f6d7d9529e4240480b | deb859bfd7ac7dba |
| tools/analysis/archv2_pilot/stage1.py | 480bc77b5a3c29b8685029f3aff3445a84fcb49f | 9e8f268acb15e7af |
| tools/analysis/archv2_pilot/supply.py | e3574a86fff4cf71d337045f74a970792568686a | 31953ded1e3c54fd |
| tools/analysis/archv2_pilot_k46.py | 11553a5819f59e195e9187f96693be6f53c56fe9 | 21ca445fe99b6457 |
| tools/analysis/archv2_stage1_anchor_draw.py | da2754d3bc4cde1bd6d01df62f29d1b3d3f4e07b | 2a862038322b1f30 |
| tools/analysis/archv2_supply_json.py | 4b6587463ec111eb5d64fb37275413926fddf1db | 12ab9ed7cc83eedc |

The READY for the stage-1 draw and the supply builder certifies these blobs. For the pilot, the K1/K2 fixes change pilot.py, accounting.py and outcome.py, so a delta READY must name the new blobs.

## Tests run (all synthetic; fixture under %TEMP%; fake call_full)

| run | got | builder claimed |
|---|---|---|
| `python tools/analysis/archv2_pilot/selftest.py` | 67 checks, 0 failed | 67/67 |
| same under `python -O` | 67, 0 failed | 67/67 |
| `archv2_stage1_anchor_draw.py --selftest` (python and -O) | 16, 0 failed | 16 |
| `archv2_supply_json.py --selftest` (python and -O) | 22, 0 failed | 22 |
| `archv2_pilot_k46.py --selftest` (python and -O) | **67**, 0 failed | **65**. The gap is 2 and changes no verdict. The report's figure is stale. |
| `python tools/analysis/judge_v2/lint_opens.py --root <worktree>` | 239 .py files, **0 findings**, 10 allowlisted | none |
| the 10 mutants (cv_filter_dropped x2, a 14-anchor stage-1 file, the rubric sha missing, trim_arena12, cap_off, anchors_from_14, the cap at 7,990+24, refit_pair, unseal_early) | all REFUSED; the PASS lines were counted from the full output | "every requested mutant refused" |

Independent re-derivation, in a script separate from the package:
- Seeds sha256(master|name)[:8] big-endian: stage1-anchors 10949444882593111949; anchors 1224499560724031674; questions 18033762649409511210; trim 6354789372005434991; boot 15875202509651165824; rungs 16435287616356325748.
- The stage-1 draw, reimplemented (sort by (-count, name), 7 groups of 2, `rng.choice` per group, PCG64): **0 mismatches over 300 synthetic count vectors** against `stage1.draw`.
- The pilot's 2-of-7 draw is identical to `PL.draw_pilot_anchors`.

## Per-claim table

| # | claim | status | evidence (command / probe) | got vs claimed | sev |
|---|---|---|---|---|---|
| 1a | 46 models; Meta-Llama excluded; ARENA12 inside | CONFIRMED in code, UNDETERMINED on data (not run on record) | `roster_of`: ACTIVE of mmlu-pro-v2, `need(len==46)`, `need(quarantined not in active)`, `need(ARENA12 ⊆ active)`; the selftest refuses a 16-roster and a missing ARENA12 name | on data the dry-run is the witness (C0 (b)) | — |
| 1b | 2 of the registered 7 | CONFIRMED | `draw_pilot_anchors` takes `rng.choice(7,2,replace=False)` on the sorted 7 from `stage1.verify`, which requires exactly 7 that reproduce under `choose_strata`; `check_pilot_anchors` re-derives in a fresh Streams; mutant anchors_from_14 is REFUSED | the same draw independently | — |
| 1c | all pairs, N 2, filtered | CONFIRMED, with a deviation (K8) | `schedule_anchor` is `design.schedule_stratum` call for call, plus the variant mask; the selftest proves identity when every question is judgeable | the eligible set is narrowed by the mask (K8) | MEDIUM |
| 1d | TRIM never touches ARENA12; total ≤ 4,000 | CONFIRMED | candidates exclude pairs with both members in ARENA12; post-check `arena_pairs <= kept_keys`; `need(len(kept) <= cap)`; mutants trim_arena12 and cap_off REFUSED; t is equal per anchor (selftest: 2 x t removed, 2 anchors) | — | — |
| 1e | every random stream pinned | CONFIRMED | anchors, questions, trim, boot, rungs, plus named derived streams (`boot/rep%04d/k%02d/<a>/qboot`, `boot/point/*`, `boot/integrated/s*/*`, `c3/*`), all from the master; the log sha is printed; the fixture outcome shows 143 streams | — | — |
| 2 | the key stays sealed until C1 is written | **PARTLY** | `unseal_key` (response.is_correct) is gated on the C1 file, and mutant unseal_early is refused. BUT `outcome.analyze` calls `PL.load_plan`, then `LD.load_matches`, BEFORE C1. The loader reads `gt_raw, answer_text, is_correct, is_correct_mathfix` (loader.py L316) into `loaded.materials` for the C0 (d) leak re-scan. The key is therefore in the analysis process before C1 is written. The C1 path does not use it (by reading: C1 takes only `rows_b`, `plan.free["A"]`, rosters), but no witness proves that | K4 | MEDIUM |
| 3 | C1 exactly as amended | CONFIRMED on formula and readings; one defect | `beta_of` = [ln nu46 − ln nu12]/ln(46/12); `c1_interval`: SE_dec = sqrt(SE_boot² + 0.20²/2), interval ±1.96 SE_dec; `c1_readings`: P EXCLUDED iff lo > 1.06, M EXCLUDED iff hi < 2.05, both printable, else UNRESOLVED. The bootstrap resamples questions within each anchor from one "boot" stream, and every replicate refits both sub-boards. DEFECT: non-finite replicates are dropped (K7) | the formula matches the amendment's text word for word | MEDIUM (K7) |
| 4 | C1b / C3 print ruling 3's items with "planning scale only" | CONFIRMED for C3; PARTLY for C1b | C3: per fold and pooled (b0,b1), wrong(all) and wrong(established) (McNemar on the anchor's judged questions via `AD.mark_established`), ddev vs 3.84, frozen/LOAO ratio at k 46 AND k 12, 1.24 beside, monotonicity count, status word forced UNDETERMINED; FROZEN_LABEL on the frozen lines. C1b: the label is present, BUT its bar comparison uses the key-blind level against bars from a key-informed L12 (K5), and its interval is the unwidened bootstrap interval although the amendment says "the same widened interval" (K6) | — | MEDIUM |
| 5a | pilot ceiling 8,000; the 4,000-match rule; the day cap 14,000 | CONFIRMED pre-launch | `guard_day` prints all three on every launch and refuses on a breach (7,990+24 REFUSED; ledger > store REFUSED; day 13,990+20 REFUSED) | — | — |
| 5b | ledger row appended in a `finally` | CONFIRMED, but it does not hold the ledger | `launch` L682-688: `posted = a1 - a0` from store attempt rows | see 5c | — |
| 5c | **does the pilot reproduce INDUCE C1 (post then crash, unledgered)?** | **YES, REPRODUCED** | Probe `scratchpad/k46/probe_ledger.py`, fixture, fake call; results below | 1 orphan post per crash; the day ledger short by the whole launch on a hard kill; C0 (f) then FAILS for good | **HIGH (K1)** |
| 6a | date guard | CONFIRMED | `posting_day_ok`, string compare against 2026-09-25; the selftest refuses 2026-09-24 | — | — |
| 6b | no `--go`, nothing posted | CONFIRMED | selftest: 0 fake calls, no store created; a run without --go reads read-only only | — | — |
| 6c | pilot before run | CONFIRMED | the first launch must be the pilot; the run needs `.pilot_guard.json` and the pilot slots complete | — | — |
| 6d | write-once files | CONFIRMED, with a defect | the manifest, guard file, outcome and C1 file are all mode x. The FAILED guard name is second-granular (`time.time()` as int). Probe: a second pilot launch within the same second died on WRITE-ONCE after it had posted | K3 | LOW |
| 6e | the pilot guard counts errored jobs | CONFIRMED; stricter than registered and unrecoverable | Probe `probe_pilot_err.py`: one transport error in the pilot 12. Launch 1: guard FAIL (cached 23, errored 1). The relaunch re-posts the slot (cached 24/24), but `errored_attempts` stays 1 forever (append-only attempt rows), so the store can never PASS, and `--run` is REFUSED ("no PASSED pilot guard file") | K3 | MEDIUM |
| 7 | loader only through judge_v2 / open_eval; every count filtered on corpus_version | CONFIRMED | Free data is read via `data_v2.views.open_eval("arena", …)` (an admitted stage) and payloads via `judge_v2.loader.load_matches` (`open_eval("judge")`). `grep -n SELECT` over the package: every item, variant, response and reference query names `corpus_version`; `pool` is by scope; `side` is keyed by item_id (one row per item). Distinct-id asserts exist, and mutant cv_filter_dropped is REFUSED in both builders. Lint: 0 findings | — | — |
| 8 | Support (registered, amended) | CONFIRMED by re-derivation | Re-derived below: SE 0.2083 → 0.26 with ×1.25, MDE 0.728, M bar 2.0484, P–M 0.99 | reproduces to 2 decimals | — |
| 9 | frozen files untouched; judge_v2 untouched | CONFIRMED | counts above | — | — |
| 10 | the pilot can run with the ruled rubric artefact | **REFUTED as built** | The pilot pins `judge_v2/induction.py` blob:ae17ba25 (f5bbbda). The INDUCE-RUBRIC-1 branch that mints the artefact changes induction.py to blob:0de6153f61c5c4c2dc0c84b81fc097e282487862 (`git rev-parse archv2-induce-rubric-1:tools/analysis/judge_v2/induction.py` at 23e56e7 and at fc8cfac). After that merge `judge_pins_ok()` is False, and the header, launch and C0 (c) all refuse. The registered C0 (c) text ("pins equal f5bbbda's") conflicts with the ruling that replaces the induction.py pin (L15969 bracket) | K2 | **HIGH** |
| 11 | registered precondition: the artefact_sha256 and rubric_sha256 named in the programme before the READY | **NOT MET** | `grep -n artefact_sha256 docs/judge_v2_program.md`: no pilot pin; INDUCE-RUBRIC-1 is NOT READY (6b65efe) and has not run | — | BLOCKER for a pilot READY (not a code defect) |

### Probe 5c, raw (fixture store; pilot then run; `posted(by fake)` = the fake call_full's own counter, i.e. real HTTP posts)

```
after Ctrl-C at post 5       posted(by fake)    5 | store attempts    4 verdicts    4 | test ledger rows    4 | day ledger total    4
after clean pilot            posted(by fake)   25 | store attempts   24 verdicts   24 | test ledger rows   24 | day ledger total   24
[run, os._exit at post 60]   exit=9
state                        posted(by fake)   60 | store attempts   58 verdicts   58 | test ledger rows   24 | day ledger total   24
after resumed run            posted(by fake)  664 | store attempts  662 verdicts  662 | test ledger rows  628 | day ledger total  628
analyze → (f) FAIL: posted calls (attempt rows, errors included) 662 <= 8000; the ledgers' rows 628 (equal: False) → C0: FAIL -> UNDETERMINED BY VALIDITY
```

- The attempt row is written only after `call_full` returns (`VerdictStore.drain`: `res = poster(slot)` then `record_attempt`). So a KeyboardInterrupt or a kill in that window leaves a post with no row, and it is re-posted on relaunch. Here: 2 orphan posts, one per crash.
- A hard kill skips the `finally`. Every post of that launch is then missing from the day ledger: 34 here, up to the whole launch (≤ 8,000) in the real run.
- The next launch is admitted with no reconciliation. `own = max(store 58, ledger 24)` covers (i), but (iii) reads the day file and is short by 34. The resumed launch appends only its own delta, so the gap is permanent.
- The pilot's own C0 (f) then voids the whole run after all its calls are spent.
- Ceiling: the orphan posts are counted nowhere. The author's hard 8,000 is exceeded by the number of crashes when the schedule is at the cap.
- This machine crashed today (resume note 2026-09-24).

### Support re-derivation (rule 8; from the amendment's stated CVs, not copied)

- ln(46/12) = 1.34373. Per-anchor CV 0.22 (k 12) and 0.19 (k 46); the 2-anchor mean gives CV/√2 = 0.1556 and 0.1344; correlation between rungs ≈ 0.
- Var(β̂)_boot = (0.1556² + 0.1344²)/1.34373² = 0.04226/1.80561 = 0.02340, so SE_boot = 0.1530.
- SE_dec = sqrt(0.02340 + 0.20²/2) = sqrt(0.04340) = **0.2083** (registered 0.21). With ×1.25: **0.2604** (0.26). MDE = 2.80 × 0.2604 = **0.729** (0.73).
- M bar = ln(1035/66)/ln(46/12) = 2.75245/1.34373 = **2.0484** (registered 2.05). P bar = 1.06. Separation 0.99 > MDE: **SCOREABLE reproduces.**
- The DEFF source is declared (no transport; the interval is the question-clustered bootstrap). The 0.20 and the CVs are DEV, not of record, as the amendment says.
- C1b illustrative bars from L12 = 0.1078 (G22_nu_grok.txt L32, verified): P = 0.1078 × 3.8333^1.06 = 0.4479; M = 0.1078 × 1035/66 = 1.6905 (registered 0.45 / 1.69).

## Defects and conditions (pilot)

- **K1 HIGH — write-ahead invocation record; the ledger cannot miss a post (the INDUCE C1 flaw, reproduced).**
  - Wrap `call_full` inside the pilot (new files only: pilot.py / accounting.py; no frozen or judge_v2 edit).
  - Before each post, append one line (match_id, order, payload_sha, "PENDING") to a write-ahead journal `<store>.invocations.jsonl`, with flush + fsync.
  - Count posts in a holder that the `finally` reads.
  - At EVERY launch, before the guard, reconcile: journal lines vs store attempt rows vs ledger rows for the test. A journal line with no attempt row is an orphan: it is counted as posted (ceiling, match rule, day cap) and disclosed. If the ledger is behind the journal, append a catch-up row labelled "reconciled after crash", or REFUSE until the operator does. Never launch silently on a mismatch (the INDUCE ruling 1 (b) equality).
  - `guard_day`'s own = max(journal, store, ledger).
  - C0 (f) compares ledger == journal and prints the orphans.
  - Witnesses:
    - the KeyboardInterrupt probe must show ledger == journal == fake posts;
    - the os._exit probe's relaunch must refuse or reconcile to 60;
    - the resumed run's C0 (f) must PASS with orphans disclosed.
- **K2 HIGH — the induction.py pin.**
  - The pilot's `JUDGE_V2_F5BBBDA["judge_v2/induction.py"]` (ae17ba25) must become the INDUCE-RUBRIC-1 replacement blob that its delta READY names (currently blob:0de6153f61c5c4c2dc0c84b81fc097e282487862 at 23e56e7; hash kind blob, LF).
  - The registrar brackets C0 (c) ("pins equal f5bbbda's, induction.py replaced per L15969") BEFORE the change. The pilot then gets a delta READY after INDUCE merges and its artefact exists.
  - Until then the pilot refuses at the header (fail-closed, correct), so it cannot run.
- **K3 MEDIUM — pilot-guard recovery.**
  - An errored attempt in the pilot 12 makes the store permanently un-passable (probe). The registrar rules the guard's treatment of errored jobs. Proposal: PASS iff every pilot slot carries a usable verdict, unusable 0, foreign 0; errored attempts counted and printed, and REFUSED above a registered bound. Otherwise the documented recovery is a new store, disclosed, with the old store's posts on the ledger.
  - Fix the FAILED-file name: use a launch counter, not an int timestamp.
- **K4 MEDIUM — the key in process before C1.**
  - After the C0 (d) re-scan, clear `loaded.materials` and drop `loaded` before any C1 code.
  - Add a witness: C1's inputs (rows_b, answers, rosters) contain no is_correct / gt field (count 0), and the materials dict is empty (count) when C1 starts.
  - The registrar records that the judged path's leak material is not a "key read" in the registration's sense (the launch processes read it by construction, days before C1).
- **K5 MEDIUM — C1b's bars and P2b are not definition-matched (builder's choice 5; changes a registered quantity).**
  - L12 of record (0.1078) comes from G22's nu leg: "called non-frontier edges", zero-gap edges dropped and frontier banded BY THE KEY (918 of 924 edges at k 12).
  - The pilot's level nu_2(46) is key-blind (all edges, no band), yet `level_lines` compares it with the L12 bars ("BELOW / BETWEEN / ABOVE").
  - P2b ("the level on the control's definition") is scored on the key-blind value.
  - The 14-anchor projection multiplies a key-informed L12 by a key-blind exponent.
  - The registrar rules which value C1b compares and P2b scores. The code then compares only the matched value (`res[k_hi]["matched_nu"]`, computed after the unseal) with the L12 bars and prints the key-blind level as "definition differs from L12".
- **K6 MEDIUM — the C1b interval (builder's choice 6; changes a registered quantity).**
  - The amendment says "the same widened interval". 0.20 is an SD of exponents, not of levels, so no level constant exists.
  - The code prints the bootstrap percentile interval labelled only "bootstrap 95%".
  - The registrar rules: register a level constant, or record the unwidened interval. The line must then say "NOT widened for the anchor draw".
- **K7 MEDIUM — one-sided exclusion in C1 (builder's choice 7a).**
  - nu_2(12) = 0 gives β = +∞, and `c1_interval` drops it. That removes only upper-tail replicates, which shrinks SE_boot and pulls the upper end down, toward "M EXCLUDED" (the FALSIFIER).
  - Practically rare (it needs zero called edges on both anchors at k 12), but it is unguarded.
  - Fix: C1 reads UNDETERMINED if any replicate is non-finite (count printed; the branch executed). The registrar records the rule.
  - C1c's one sub-roster per rung (choice 7b): admissible, descriptive, disclosed.
- **K8 MEDIUM — the variant mask (builder's choice 2; changes the registered eligible set).**
  - A question is eligible for a pair only if both models answered it under ONE variant. This is forced by the loader, but it narrows "the anchor's EVAL questions on which the two answers disagree".
  - The dry-run prints no count of the (pair, question) cells lost to the mask. Add it per anchor, beside the exhausted-pair count, and have the registrar record the deviation before the run with that count.
- **K9 MEDIUM — the ledger path.**
  - `DEFAULT_LEDGER_DIR = <ROOT of the script>/experiment_results`, and `day_calls_*.json` is git-tracked. Launched from a worktree, the guard reads the worktree's copy: identical today, divergent after main's next append. The guard line prints only the basename.
  - Print the absolute path, and refuse unless it resolves to the main checkout's `experiment_results` (or a path the registration names).
- **K10 LOW.**
  - (a) Rule 8 post-run: print a measured DEFF for the deciding statistic: question-clustered vs match-level bootstrap variance (`edges_fast(deff=True)` exists) and n_eff = n/DEFF. "n_eff(questions) = q_used" is a mislabel.
  - (b) The persona text sha is not printed (registration: "its text sha printed").
  - (c) `load_rubric` refuses on negative substrings only; require the positive "REGISTERED ARCH-V2-INDUCE-RUBRIC-1" label and `manifest.population.corpus_version == mmlu-pro-v2` (C4 ruling (6)). The shas pin the content anyway.
  - (d) M bar 2.05 vs the exact 2.0484: an upper end in [2.0484, 2.05) reads "M EXCLUDED" with M inside the interval. As registered, it is printed beside; the registrar may prefer the exact value.
  - (e) A launch that crosses midnight is appended to the later day as one row.
  - (f) The roster check does not assert that Meta-Llama is present as QUARANTINED, nor the registry total 47.
  - (g) C3's "IDENTIFIED" is sign-blind (the G22 D1 lesson). The established b1 is printed beside, which is acceptable because C3 decides nothing.

## The builder's 10 choices — rulings (reviewer) / passed to the registrar

| # | choice | ruling | registered quantity changed? |
|---|---|---|---|
| 1 | the filter compares option CONTENT, not letter | ADMISSIBLE. It is the faithful reading of "answers disagree" under MIXED orderings, and equal to the letter rule on a fixed ordering; A (agreement) uses the same strings. Disclose | no |
| 2 | judgeable under ONE variant | FORCED but narrows the eligible set → **REGISTRAR** (K8), with the lost-cell count printed first | **yes** |
| 3 | the trim counts excluded (MIXED) matches | ADMISSIBLE. The cap is on scheduled matches ("NEVER exceeded"; "excluded pairs counted"); conservative. Disclose | no |
| 4 | pilot 12 = the first 12 LOADED | ADMISSIBLE. A guard over excluded matches would post nothing (vacuous). Disclose | no |
| 5 | L12 key-informed vs C1 key-blind | **REGISTRAR** (K5): the C1b bars, P2b scoring, the projection | **yes** |
| 6 | C1b: no registered widening constant | **REGISTRAR** (K6) | **yes** |
| 7 | zero-nominal replicates excluded; one sub-roster per rung | 7a: fail-closed fix + **REGISTRAR** record (K7); 7b ADMISSIBLE | 7a yes (C1's interval) |
| 8 | stratification on item counts, sentinels included | ADMISSIBLE: it is the ruling's words ("EVAL item count", pool n_items 3,749 of record; sentinels are never scheduled, having no ACTIVE response). The judgeable counts are printed beside; the draw is never redrawn | no |
| 9 | accounting in a new module | ADMISSIBLE: atl blob 4e9db106 is pinned by other READYs and was left untouched. It inherits K1 | no |
| 10 | the store read through archv2_arena.ro | ADMISSIBLE: pool_guard's open_ro, `mode=ro&immutable=1`, refuses a non-empty -wal/-journal, and the schema_id is checked. The crash probe resumed cleanly (no hot journal left) | no |

## R-G22 — how the owed G22 re-run uses `--only-anchors` (reviewer's ruling; the registrar records it)

- **Frozen `design.choose_strata` does not refuse.** `if n >= len(names): return names`. On the 7-anchor supply file, D1-full (strata=14) silently gets the 7, and the stop leg (on D1-full's part) gets 7 strata with stage 1 = all 7 (projection factor 1). Nothing refuses.
- **(a) The 7-anchor file** (`--only-anchors`) is admissible ONLY in an invocation restricted to 7-strata designs: `--leg designs --designs D1-stage1` (D1-stage1 reads exactly the registered 7, as ruled). D4 is also a 7-strata design (MEMO_DESIGNS D4 strata=7). On the 7-file it would read the registered 7 instead of its own stratified draw from 14. Not ruled: the default is D4 on the 14-file with its own stream, unless the registrar rules otherwise before the run.
- **(b) D1-full (and D2) run ONLY on the full 14-anchor supply file**, in a separate invocation with its own token and master, both disclosed. The post-run review counts strata per design part from the printed "%d strata" line and voids any D1-full part with fewer than 14.
- **(c) The stop leg cannot read the registered 7 as its stage 1** with the frozen instrument. `stop_leg` draws `stop/stage1-strata` from D1-full's 14, and feeding it the 7-file breaks stage 2. Ruling 2 (a) (53eccb6) requires the registered set, so the stop leg waits for the NEW registered re-binding and delta READY (C6/D8 of 47fd0d6). No stop-leg re-run on the frozen instrument is a stage-1 reading.
- **(d) The count kind** (`items` vs `judgeable`) is the registrar's to name for the re-run. The builder refuses to choose, correctly. For a supply of questions a design can JUDGE, "judgeable" is the substantive one; "items" includes routing-only sentinels.

## What this review does not show

- Any number on the split of record: the stage-1 counts, roster names, the variant-mask loss, the schedule size (P4) and the exclusion counts are all unread by rule.
- That ARENA12's names match the v2 registry: the dry-run's C0 (b) is the witness.
- The INDUCE artefact's content or compatibility beyond the API check: `load_artefact` / `rubric_sha256` / `corpus_type` / `artefact_id` are unchanged at 23e56e7.
- Wall time of the B 2,000 analysis at k 46.

Probe scripts: `scratchpad/k46/probe_ledger.py`, `probe_c0f.py`, `probe_pilot_err.py` (session scratchpad, fixture only).
