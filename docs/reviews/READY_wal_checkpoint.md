# READY review: tools/ops/wal_checkpoint.py (branch ops-wal-checkpoint, tip fa3c8c61)

Reviewer: adversarial reviewer, 2026-10-03. Zero judge calls. No real DB opened: every run used temp roots
or a scratch fake repo; the one real-CLI run refused at the process check, before any open.

**Reviewed blob:** `blob:07485391f009a5ccd3c30b1ee0b994b916c61cbd` (`git hash-object`; file is ASCII with LF
only, so the working tree and the LF blob are the same; no CRLF rendering). Tip fa3c8c61 is one file, +588,
parent a1c65848 (`merge-base --is-ancestor` OK). Python 3.11.1, SQLite 3.39.4.

## Verdict: READY to merge, with conditions C1-C2 before it goes on the allow-list; C3 is the author's call

Read line by line against the four threats in the brief, the deciding paths are correct: the bare-name and
allow-list check, the java/gradle refusal, the exclusive-open probe, verifying the backup before the
checkpoint, the TRUNCATE result check plus the -wal size check while the connection is still open, and the
per-table diff. I found no path that writes to a DB off the list, gets out of the repo root, or changes
content without refusing. The weakness is the selftest: 8 of my 8 mutants on guard lines survive (table
below). The guards are in the code but nothing pins them, so a later edit could drop one without any test
failing. For a tool that runs unattended under an allow rule, that has to be fixed (C1).

## Per-claim table (deciding claims)

| Claim | Result | Mine vs claimed | Sev |
|---|---|---|---|
| Selftest S1-S21 passes | CONFIRMED | `SELFTEST PASS (0 failed)`, 41 `ok` lines | - |
| Mutants 27/27 killed | PARTLY | builder's 27 not re-run whole (the mutation script is not committed); 3 re-applied (M7, M23, M24) are all killed. But 8/8 of MY mutants on other guard lines SURVIVE, so "27/27" overstates what the selftest covers | MEDIUM |
| Only allow-listed names at the repo root | CONFIRMED | `ratings.db`, `../snapshots.db`, `C:snapshots.db`, `snapshots.db.`, `snapshots.db ` (trailing space), `SNAPSHOTS.DB`, `snapshots.db::$DATA`, `snapshots.db:x`, `intent_emb_..db`, `intent_emb_x.db\n`, `EMBEDD~1.DB`: all REFUSED, exit 2 | - |
| Symlink / outside-root refused | PARTLY | code is correct by reading (L88, L93), but untested: os.symlink fails here (WinError 1314, no privilege) and R1/R2 survive. A HARDLINK at the root to an outside DB is ACCEPTED (B; resolve() cannot see it). Making one needs write access to the root, and a checkpoint does not change content | LOW |
| Refuses while java is running | CONFIRMED | real tasklist: 464 processes, java.exe present -> `REFUSED: forbidden process running: java.exe`, rc 2; fake-root db sha256 unchanged, no `experiment_results/` created | - |
| -wal is 0 bytes while the connection is open | CONFIRMED | L289-292 sit inside the `try`, before `con.close()`; M23 (drop it) is killed by S21 | - |
| Backup made and verified before the checkpoint | CONFIRMED | L247-260: sha of source, copy and source again all equal, before BEFORE and before any connection to the live file. BEFORE reads a scratch copy of the backup, which also proves the backup opens | - |
| Content changes refused | CONFIRMED | S15/S18 (M12, M13 killed per the builder; S15 passes here) | - |
| Every failure prints REFUSED, exit 2 | REFUTED | non-Refused exceptions escape as a traceback with exit 1: a non-SQLite file -> `DatabaseError` (D); a rowid table whose SQL contains the text "without rowid" -> `OperationalError: incomplete input` (E); also a locked DB at `connect`/`PRAGMA` (timeout 0), OSError on copy or disk full. All of these happen BEFORE the checkpoint or leave it fail-closed (no OK line), but they leave a backup directory without before.json | MEDIUM |
| S1 "result=(0, N, N) with N > 0" (docstring) | REFUTED (wording) | the test asserts only N == N; SQLite 3.39 returns (0, 0, 0). The real proof is `imm_count == 40` after the run, and that is sound | LOW |

## Own mutants (scratch copy of the blob, selftest re-run)

- R1 drop `is_symlink` refusal (L88): SURVIVED. Decisive (root escape)
- R2 drop `pr.parent != root_r` (L93): SURVIVED. Decisive (backstop for R1)
- R3 drop the second probe before connect (L275): SURVIVED. Not decisive alone (busy_timeout 0 + the (0,x,x) check still apply)
- R4 drop the second process check (L274): SURVIVED. Not decisive alone
- R5 drop the source re-hash `== src_sha2` (L256): SURVIVED. Not decisive (the probe excludes writers)
- R6 drop the disk check (L238): SURVIVED. Not decisive
- R7 ignore the tasklist return code (L103): SURVIVED. Decisive (a failed tasklist gives an empty list, which S10 catches only if stdout is empty)
- R8 drop `javaw.exe` from FORBIDDEN_PROCS: SURVIVED. Decisive (a JVM would be let through)
- Builder's M7 (probe share mode 3), M23 (in-connection -wal check), M24 (PASSIVE): KILLED (S11 / S21 / S1)

## Defects and fixes

- **C1 (MEDIUM, before allow-listing)**: add selftest cases that kill R1, R2, R7, R8, R3 and R4. R1/R2:
  monkeypatch `Path.is_symlink` / `Path.resolve` (no symlink privilege on this machine), or `os.symlink`
  with a skip that is reported as SKIPPED and counted. R7: inject a `subprocess.run` stub with rc != 0. R8:
  `procs=lambda: ["javaw.exe"]`. R3/R4: `procs`/`probe` stubs that pass on the first call and refuse on the
  second. Re-state the mutant count with these included, and commit the mutation script so the count can
  be re-run.
- **C2 (MEDIUM)**: wrap the body of `run` in `except (sqlite3.Error, OSError, subprocess.SubprocessError)`
  so it prints `[wal-ckpt] REFUSED: <type>: <msg>; backup at <bdir or none>` and exits 2. Add one case
  (garbage file named snapshots.db -> REFUSED, exit 2). In `table_hashes`, refuse when a WITHOUT ROWID
  match yields an empty pk list, instead of emitting `ORDER BY ` with nothing after it.
- **C3 (AUTHOR)**: `Bash(python tools/ops/wal_checkpoint.py:*)` allows whatever file sits at that RELATIVE
  path in the current directory. Any agent that can edit the file, or that runs from a worktree holding a
  modified copy, gets arbitrary code under the allow. Pair the allow with a deny on Edit/Write of
  `tools/ops/wal_checkpoint.py`, or have the tool check its own blob against a pinned value. Also note that
  a checkpoint moves the whole-file shas of DBs of record (embeddings_cache.db is one); pins must stay per
  table (the tool's before.json/after.json are those pins).
- **D4 (LOW)**: every run, dry runs included, leaves a full copy in `experiment_results/_backup/` (up to
  1.9 GB for multicorpus_cache_v1.db) with no retention. This is fail-closed (the 2.2x disk check refuses
  first) but fills the disk if run unattended many times. Document it, or prune old `wal_ckpt_*` folders
  only after an OK.
- **D5 (LOW)**: hardlinks are not detected. `os.stat(p).st_nlink > 1` -> refuse would close this cheaply.
- **D6 (LOW)**: fix the S1 docstring ("N > 0" is not what is asserted).

## Commands

```
git -C .claude/worktrees/wal-ckpt hash-object tools/ops/wal_checkpoint.py   # 07485391...
git -C .claude/worktrees/wal-ckpt show fa3c8c61:tools/ops/wal_checkpoint.py | git hash-object --stdin  # same
git show fa3c8c61 --name-only --format= | wc -l                             # 1 file
python tools/ops/wal_checkpoint.py --selftest | grep -E "FAIL|SELFTEST"     # PASS (0 failed); 41 ok
python -c "import wal_checkpoint as w; w.check_processes(w.list_processes())"   # REFUSED java.exe (real tasklist)
scratch fake repo: python tools/ops/wal_checkpoint.py --db snapshots.db     # REFUSED java.exe rc=2; sha256sum -c OK
scratch adv.py: symlink (WinError 1314), hardlink (DRY-RUN accepted), 9 name tricks (REFUSED),
  garbage db (DatabaseError traceback), 'without rowid' text (OperationalError traceback)
scratch mutants R1-R8: str.replace on the blob (each anchor count == 1), python m.py --selftest -> rc 0 = SURVIVED
```
