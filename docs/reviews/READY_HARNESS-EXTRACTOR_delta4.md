# READY HARNESS-EXTRACTOR delta 4 (POSTRUN F-1 / F-2 / S-1), 2026-10-10

**Verdict: READY** for the `--run` of `tools/analysis/harness_extractor.py` at **blob:4107eb0b9ed20e48ab5ee9cdca818db3405de33d**
(sha256-lf16:05ab8b87bbb49869; working tree CRLF sha256-crlf16:e3adab1d1d42c915), branch `hx-r5` tip 65be3d11. The script must be
merged by path to main first. Zero judge calls, nothing written by this review. This is a delta review of `git diff 4a3294d7..65be3d11`,
which touches 1 file (`--name-only | wc -l` = 1). Code the delta does not touch stays as confirmed by READY delta3 (1b7a603a).

Conditions:
- C1 Merge by path. The operator re-pins the merged blob (LF), and the identity line must read blob:4107eb0b.
- C2 Run from main as in the LAUNCH SEQUENCE: busy.ps1 exit 1, then selftest, mutants, `--dry-run` and `--run`.
  - The dry-run must print 15 `schema:` lines and the `SCHEMA CONFORMANCE (S-1): 15 columns in 4 tables named by 6 statements` line.
  - The dry-run must print `R1: 471 ... / 427`, `rows per model: MATH [1324], IFEVAL [541]` and the multicorpus sha256 EQUAL.
- C3 Back up the outputs to E:/TaxoArena_backup_<date>_harness_extractor with SHA256SUMS. Never commit them.

## S-1: SQL identifiers of the --run path, listed independently and checked against the real schemas

I read `read_inputs` L713-L830. Every `execute` in it goes through `RUN_SQL` (L306-L316). Outside the SELFTEST block, no other statement
on a data DB exists: `awk 'NR<1200 && /execute|connect\(|open_ro/'` lists L673/L695 (schema_check) and L738-L819 (RUN_SQL only).

The two modules that issue SQL of their own are covered as follows:
- `pool_guard.assert_pool_of_record` is the module of record. Its queries are mode-independent and already ran in the dry-run.
- In `math_fix` and `math_scorer_h`, SQL lives only in `run()` (L112) and `main()` (L273). Neither is called: the script uses only
  `MSH.h_score`, `labelled`, `modes`, `region`, `REF_FIX` and `mf`.

Real schemas (my own python, `mode=ro&immutable=1`, `PRAGMA table_info` + `sqlite_master`):

| statement | table.column read | real (cid, type) | present |
|---|---|---|---|
| q | corpus_questions.question_id, source, upstream_id, text, target | 0 INT, 1 TEXT, 2 INT, 5 TEXT, 7 TEXT | yes |
| ev_dry / ev | eval_results.question_id, model_name, model_output, is_correct (+ corpus_questions.source join) | 0, 1, 7 TEXT, 8 INT | yes |
| mf | eval_results_mathfix.question_id, model_name, **is_correct** | 0, 1, 2 INT (`CREATE TABLE eval_results_mathfix (question_id INTEGER, model_name TEXT, is_correct INTEGER, PRIMARY KEY (question_id, model_name))`) | yes |
| ck_count / ck | math_checker_answers_v2.question_id, model_name, non_terminated | 0, 1, 11 INT | yes |

My list has 15 columns in 4 tables. It equals the script's `RUN_COLUMNS`, its hand-written `REAL_READS` oracle (L2247-L2250) and the
15 `schema:` lines of the real dry-run, column for column and cid for cid.

The invented name `is_correct_mathfix` now occurs 12 times (`grep -n`, the whole file): L164 (DELTA note), L1405-L1449 (the
fixture's `schema_drift` option), L2297-L2326 (st_schema), L2624-L2626 (mutant labels). None of these is on the run path.

Key coverage, checked without reading any scorer value (pair counts only):
- MATH pairs without Meta-Llama: 23,832 in eval_results and 23,832 in eval_results_mathfix.
- MATH pairs missing in mathfix: 0. Missing in checker_answers_v2: 0. ck rows: 23,832 (= 18 x 1,324).
- So REFUSE.MF and REFUSE.NT cannot fire on key absence.

## Per-claim table (deciding claims)

| # | claim (builder) | mine | verdict | sev |
|---|---|---|---|---|
| 1 | F-1: the MATH-FIX SELECT reads `f.is_correct` | RUN_SQL["mf"] L312. The real column exists (cid 2). EXPLAIN-compiled on the real DB in the dry-run (G2) | CONFIRMED | - |
| 2 | F-2: fixture tables are built from the real DDL; st_schema (a) asserts sqlite_master + PRAGMA equality for 5 tables | `_real_ddl` L1386-L1400 reads sqlite_master only. My mutant R2 (fixture drops the mathfix PK) is killed by `schema` | CONFIRMED | - |
| 3 | S-1 in dry-run and run: 15 lines + count line, 15/15 present | My real dry-run: rc 0, 55 lines, `grep -c '^  schema: '` = 15, count line L24. The run and the dry-run call the same `schema_check` (L733) before the first row read | CONFIRMED | - |
| 4 | Selftest 10/10 with `--data-root`; fails closed without it | 10/10 (rc 0). Without `--data-root`: rc 1, failing run_e2e, refusals, dry_run, schema and branches. There is no fallback | CONFIRMED | - |
| 5 | Mutants 117/117 killed, control survived, none not applied | My run: `117 of 117 KILLED; control SURVIVED; survivors none; not applied none` | CONFIRMED | - |
| 6 | Multicorpus sha unchanged; nothing written | sha256 ad66e30a0eb4abd6 before = after (my sha256sum, and the script's own BEFORE/AFTER line). checker_answers_v2 6cfaf74d647829d1 before = after. The out dir and blog dir are absent. mtime is still Sep 13 | CONFIRMED | - |
| 7 | R1 471/427, roster 18, 1324/541 per model | dry-run L26, L28, L30 | CONFIRMED | - |
| 8 | Every full-path line runs on the real-schema fixture | stdlib `trace --count` over run_e2e, refusals and dry_run: 0 non-`refuse` lines unexecuted in L720-L1160. The full-only branches are no longer reachable only by the real run | CONFIRMED | - |
| 9 | Pins | `git hash-object` = 4107eb0b. `git show HEAD:… \| sha256sum` = 05ab8b87bbb49869 (LF). The working file = e3adab1d1d42c915 (CRLF). The identity line agrees | CONFIRMED | - |

**Ruling on the declared deviation.** The selftest and the mutants now open the real DBs for schema only. They read sqlite_master,
PRAGMA and EXPLAIN through `pool_guard.open_ro` (immutable) and read no row. **ACCEPTED.** This is the remedy S-1 and F-2 asked for.
A fixture checked only against the builder's own belief is the defect class that four READYs missed.

The cost is that the selftest is no longer hermetic: it needs the main data root. It fails closed without it (claim 4).

**Duplicate-row fixture with the PK dropped:** accepted. This is defence in depth for a row the real table cannot hold.

## Own mutants (3; the delta is about 400 lines, all on the S-1 deciding path)

- **R1** `ev` reads `e.pred` (a real column of different meaning) and RUN_COLUMNS is left unchanged. KILLED by the selftest (run_e2e).
  The real `schema_check` REFUSES at G3: `the statements read [('mc','eval_results','pred')] but RUN_COLUMNS declares [('mc','eval_results','is_correct')]`.
  Decisive: drift between the SQL and the declaration is caught on the real DB.
- **R2** The fixture DDL drops `PRIMARY KEY` from eval_results_mathfix. KILLED (`schema`). Decisive for F-2.
- **R3** schema_check compiles on a raw `sqlite3.connect(path)` instead of `PG.open_ro`. **SURVIVED** (selftest and real check both pass). Not decisive; see D1.

## Defects

- **D1 (LOW, not blocking).** `mc_before = G.sha256_file(...)` (L735) is taken after `schema_check` (L733). Nothing tests that
  schema_check opens its connections read-only (R3 survives). A write by the schema check would therefore escape the BEFORE/AFTER sha guard.
  - Today it opens through `PG.open_ro` (immutable), and PRAGMA and EXPLAIN do not write. So there is no live defect.
  - Fix (next delta, optional): move the `mc_before` line above the schema_check loop.
  - Also add a st_schema case that monkeypatches `sqlite3.connect` to raise for non-URI paths during schema_check.
- No other defect found.

## Commands (logs backed up to E:/TaxoArena_backup_20261009_hx_r5_ready_review, SHA256SUMS 8/8 OK)

```
git -C .claude/worktrees/hx-r5 diff 4a3294d7..HEAD --name-only | wc -l                      # 1
git hash-object tools/analysis/harness_extractor.py                                          # 4107eb0b...
python - <<EOF  (sqlite3 file:...?mode=ro&immutable=1: PRAGMA table_info + sqlite_master for the 4 tables; pair-coverage LEFT JOINs, no scorer column)
grep -n 'is_correct_mathfix' tools/analysis/harness_extractor.py                             # 12 lines, none on the run path
powershell -NoProfile -File E:/TaxoArena_tmp/busy.ps1; echo $?                               # 1 (before selftest and dry-run)
python tools/analysis/scratch_dir.py --run -- python tools/analysis/harness_extractor.py --selftest --data-root <main>   # 10/10
python tools/analysis/scratch_dir.py --run -- python tools/analysis/harness_extractor.py --selftest                      # rc 1 (fail-closed)
python tools/analysis/scratch_dir.py --run -- python tools/analysis/harness_extractor.py --mutants --data-root <main>    # 117/117
python tools/analysis/scratch_dir.py --run -- python -m trace --count --missing --coverdir E:/TaxoArena_tmp/rv_hx5_cov \
    tools/analysis/harness_extractor.py --selftest --only run_e2e refusals dry_run --data-root <main>   # 0 unexecuted non-refuse lines L720-L1160
python tools/analysis/scratch_dir.py --run -- python E:/TaxoArena_tmp/rv_hx5/mut.py           # R1 killed, R2 killed, R3 survived
python tools/analysis/harness_extractor.py --dry-run --data-root <main>                      # rc 0, 55 lines, 15 schema lines
sha256sum multicorpus_cache_v1.db experiment_results/multicorpus/checker_answers_v2.db       # ad66e30a.. / 6cfaf74d.. before = after
```

## Run commands (the operator's, from main after the merge by path)

```
powershell -NoProfile -File E:/TaxoArena_tmp/busy.ps1; echo $?        # must be 1
python tools/analysis/scratch_dir.py --run -- python tools/analysis/harness_extractor.py --selftest
python tools/analysis/scratch_dir.py --run -- python tools/analysis/harness_extractor.py --mutants
python tools/analysis/harness_extractor.py --dry-run
python tools/analysis/harness_extractor.py --run
```
