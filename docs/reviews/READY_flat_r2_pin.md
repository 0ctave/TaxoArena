# READY_flat_r2_pin: delta review of branch flat-r2-pin (tip 58997ba2, base main 80f96e9f)

Reviewer: adversarial reviewer, 2026-10-01. Zero calls. The delta is 1 file (`tools/analysis/flat_v2.py`, +42/-6;
`git diff --name-only 80f96e9f..58997ba2 | wc -l` = 1). Blob 13fc9de7fd547514c7705f68ab3ce6a6a095204c (LF; the
branch worktree's `git hash-object` gives the same value, so the CRLF rendering does not differ).

## Verdict
**MERGEABLE. FLAT R2 READY** (zero-call FLAT lane r2), under operator conditions OC-1 and OC-2. No blockers.
Clean merge onto current main bf32edf8 (`git merge-tree --write-tree main 58997ba2`). main's commits since 80f96e9f
touch none of flat_v2.py, flat_mix_mmlu.py, pool_guard.py or the R2 objects_of_record.json (count 0).

## Deciding claims
| # | Claim (builder) | Reviewer | Status | Sev |
|---|---|---|---|---|
| C1 | T2 R2 snapshot = B0/mmlu_pro_lb entry of experiment_configs/rp12_r2/objects_of_record.json | entry snapshot_id = 20261001_094311_Headless_Run_Auto_ge (namespaces [MMLU_PRO]); the file is unchanged by the delta | CONFIRMED | - |
| C2 | leaves 74 | 74 nodes with no childIds of 135 nodes; all 135 reachable from rootId | CONFIRMED (to the digit) | - |
| C3 | fit_n 6993 (root region's distinct query ids) | union of queryIds over all nodes = 6,993; root's own queryIds 0; leaf queryIds 7,437 with 6,993 distinct (overlapping leaves) | CONFIRMED (to the digit) | - |
| C4 | fit ids resolve to 6,993 distinct texts | on the R2 worktree's **own** embeddings_cache.db (the one FLAT R2 reads under DATA_ROOT): 6,993 rows, 0 missing, 6,993 distinct distilled_text, both WAL-hidden and checkpointed copies, identical texts | CONFIRMED. The builder measured main's DB (descriptive); I re-measured on the R2 DB | - |
| C5 | D-1: a main()-level `--dry-run --lane r2` test kills M8 | M8 (main's `set_lane(a.lane)` -> `pass`) gives selftest 12/13: killed | CONFIRMED | - |
| C6 | selftest passes | `flat_v2.py --selftest` gives 13 / 13 passed at 58997ba2 | CONFIRMED | - |
| C7 | R2's snapshots.db does not hold the R1 snapshot (lane-specific DATA_ROOT) | R2 snapshots.db: 234 rows, 0 rows with id 20261001_070346_Headless_Run_Auto_ge | CONFIRMED | - |
| C8 | lane r1 untouched | the diff changes only set_lane's r2 branch, one new constant and the selftest; R1 constants unchanged (selftest L764 asserts them; the `--dry-run` with no `--lane` leg asserts the R1 T2/snapshot/OUTCOME) | CONFIRMED | - |

## Own mutants (deciding paths; each one temporary edit, restored, blob re-hashed 13fc9de7 after)
- M8 L995 `set_lane(a.lane)` -> `pass`: 12/13, killed, decisive (the D-1 claim).
- MA L160 leaves 74 -> 73: 12/13, killed, decisive.
- MB L160 fit_n 6993 -> 6992: 12/13, killed, decisive.
- MC L160 R2 snapshot -> R1 snapshot 20261001_070346 (same counts): 12/13, killed, decisive (the counts are equal across lanes, so the snapshot id is the only discriminator, and it is tested).

## Defects
- D-1 LOW: the docstring cites "main's embeddings_cache.db ... 6,993 rows", but FLAT R2 reads the R2 worktree's DB
  under DATA_ROOT. Not deciding: C4 shows the R2 DB gives the same 6,993/6,993. Fix (optional, insertion only): cite
  the R2 DB and this review.

## Operator conditions (rule 7; for the FLAT R2 run, not for the merge)
- **OC-1** `TAXOARENA_DATA_ROOT` = `.claude/worktrees/rp12-r2-run` (absolute path). main's snapshots.db does not hold
  20261001_094311, and the R2 snapshots.db does not hold R1's, so the wrong root fails closed ("snapshot ... not in").
- **OC-2** The R2 worktree's `embeddings_cache.db-wal` is 4,152,992 bytes (sha 1a0aa62a..., mtime 10:06:54).
  `pool_guard.open_ro` REFUSES any non-empty -wal, so FLAT R2 stops before the census until it is emptied. Do it with
  no writer in lane r2 (no readout, no build). Preferred: checkpoint a backed-up copy and point FLAT at it, or
  checkpoint in place once lane r2 is idle (`PRAGMA wal_checkpoint(TRUNCATE)`). Then confirm the -wal is 0 bytes and
  re-pin the DB sha. On my scratch copy the checkpoint moved 0 frames (`(0,0,0)`), and the 6,993 texts are identical
  with and without the WAL. So the tail does not carry FLAT's rows, but the guard still refuses on size alone.
  snapshots.db-wal is already 0 bytes.
- **OC-3** FLAT R2's own `--dry-run --lane r2` must print `[F-3] T2 census equals the pin: snapshot
  20261001_094311_Headless_Run_Auto_ge, leaves 74, root fit ids 6993` before any `--run`.

## No writes to DBs of record
R2 snapshots.db sha 9e5536e5...b82 and embeddings_cache.db 70e6865f...762 / -wal 1a0aa62a...5b8, with sizes and
mtimes, are identical before and after the copies. All reads ran on scratch copies (`immutable=1`). The checkpoint
ran on the scratch copy only.

## Commands
```
git diff --name-only 80f96e9f..58997ba2 | wc -l          # 1
git rev-parse 58997ba2:tools/analysis/flat_v2.py         # 13fc9de7...; worktree git hash-object: same
python -c "...objects_of_record.json entries['B0/mmlu_pro_lb']['snapshot_id']"  # 20261001_094311_Headless_Run_Auto_ge
sha256sum + cp rp12-r2-run/{snapshots.db, embeddings_cache.db, embeddings_cache.db-wal} -> scratch; sha256sum again (equal)
python (scratch, file:snapshots_r2.db?mode=ro&immutable=1): json graph of the snapshot -> nodes 135, leaves (no childIds) 74,
  reachable 135, union queryIds 6993, root own 0, leaf qids 7437 / distinct 6993; R1 snapshot rows 0; total rows 234
python (scratch emb copy): queries.distilled_text for the 6993 ids, immutable (WAL hidden) and after
  PRAGMA wal_checkpoint(TRUNCATE) -> (0,0,0): 6993 rows, 0 missing, 6993 distinct, texts identical
cd .claude/worktrees/flat-r2-pin && python tools/analysis/flat_v2.py --selftest   # 13 / 13 passed
mutants M8/MA/MB/MC by sed on L995/L160, restore by cp, each: 12 / 13 passed; final git hash-object 13fc9de7, status clean
git merge-tree --write-tree main 58997ba2                # clean
```
