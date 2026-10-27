# POSTRUN HARNESS-EXTRACTOR (incident: `--run` rc 1), 2026-10-09

Verdict: **INVALID (no outcome; failed precondition of the code, not a result)**. Nothing was written and no judge call was posted.
Relaunch needs the builder's fix (F-1, F-2), then a delta READY that includes the schema check S-1. HX rank lines: none exist, so
there is nothing to recompute.

Script blob:a7ebea9f on HEAD 9f5fb487 equals the READY delta3 blob. Backup E:/TaxoArena_backup_20261009_harness_extractor_incident
(`sha256sum -c` 3/3 OK).

## Per-claim table

| # | claim (operator) | mine | verdict | sev |
|---|---|---|---|---|
| 1 | `--run` crashed at L688: `sqlite3.OperationalError: no such column: f.is_correct_mathfix` | hx_run.log traceback: main L1084 -> run L1051 `read_inputs(full=True)` -> L688. Real schema (`sqlite_master`, mode=ro&immutable=1): `eval_results_mathfix (question_id INTEGER, model_name TEXT, is_correct INTEGER, PRIMARY KEY (question_id, model_name))` | CONFIRMED | HIGH |
| 2 | The selftest fixture builds the wrong column (L1274), so the selftest and mutants could not see it | L1274 `CREATE TABLE eval_results_mathfix (question_id INTEGER, model_name TEXT, is_correct_mathfix INTEGER)`. The wrong name occurs 9 times (`grep -c` on the whole file): L23, L37, L49 docstrings; L270 KEY_SEAL; L688 SQL; L738 message; L1274 fixture; L1970-1971 mutant labels | CONFIRMED | HIGH |
| 3 | `--dry-run` never reaches the path | L686 `if full:` guards the MATH-FIX SELECT. dry-run rc 0, 39 lines | CONFIRMED | - |
| 4 | Nothing written; DB unchanged | `experiment_results/hf_blog/harness_extractor` absent; `find E:/TaxoArena_tmp/blog -name 'harness*' \| wc -l` = 0; multicorpus_cache_v1.db sha256 ad66e30a0eb4abd6 (= the operator's); .db-wal 0 bytes; mtime 2026-09-13 | CONFIRMED | - |
| 5 | No one-read marker consumed | the script has no READ_STARTED marker (`grep -n -i marker`: SELFTEST/MUTANTS markers only). Pool paeec is id-disjoint, and no split word is claimed. A relaunch needs no deviation | CONFIRMED | - |

## Defects and fixes

- **F-1 (HIGH, builder).** L688: select `f.is_correct` (alias it `AS mf` if wanted). Fix the fixture L1274 to the real schema `(question_id, model_name, is_correct, PRIMARY KEY (question_id, model_name))`. Also fix the docstrings and the L738 message.
  - KEY_SEAL (L270) already carries `is_correct`, so the seal still covers the corrected column. Keep `is_correct_mathfix` out of it, or leave it in harmlessly. A mutant must show the seal refuses the corrected SELECT before unseal.
- **F-2 (HIGH, builder).** Add a mutant or selftest case that fails if the fixture schema differs from the real one. Better, use S-1.
- **S-1 (MEDIUM, process; this review's own gate).** Before any READY on a reader:
  - Run, in the dry-run, a SCHEMA CONFORMANCE check: `PRAGMA table_info` on every table and column that the `--run` SELECTs name, against the real DB (mode=ro&immutable=1). This reads no key values.
  - The dry-run must print one line per column, with a count of the columns it checked.
  - Four READY reviews (base, delta, delta2, delta3) passed a fixture that had invented the column. A fixture written by the builder is a presence check of the builder's own belief. It is not evidence about the database.
- **L-1 (LOW).** The operator's relaunch must re-run the selftest, the mutants and the dry-run on the fixed blob and pin the new blob (LF). The outputs are write-once, and none exist, so no deviation is needed.

## Commands

```
sed -n 680,695p tools/analysis/harness_extractor.py; sed -n 1268,1280p tools/analysis/harness_extractor.py
grep -c 'is_correct_mathfix' tools/analysis/harness_extractor.py          # 9
python -c "sqlite3 ... mode=ro&immutable=1 ... select sql from sqlite_master where name='eval_results_mathfix'"
sha256sum multicorpus_cache_v1.db | cut -c1-16                            # ad66e30a0eb4abd6
ls experiment_results/hf_blog/harness_extractor                           # No such file or directory
find E:/TaxoArena_tmp/blog -name 'harness*' | wc -l                       # 0
tail -20 E:/TaxoArena_tmp/op_20261009/hx_run.log                          # traceback L1084 -> L1051 -> L688
```
