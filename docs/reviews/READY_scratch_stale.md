# Delta READY: scratch-stale c4e7499b..2cc68e9a (STALE-LIVE fix to scratch_dir --purge-stale), 2026-10-04, zero calls

**VERDICT: NOT MERGEABLE yet. MERGEABLE after S-1, a one-line floor fix with one selftest check; a trivial delta re-check.**
- The three new rules are correct in code and tested:
  - staleness = the newest mtime inside a dir;
  - a live owner file protects its dir;
  - the 24 h floor.
- Safety holds: nothing in the selftest or the mutants can purge a real path.
- But `--days nan` defeats the 24 h floor. A dir 0 seconds old was purged in the sandbox.

Reviewed blob: scratch_dir.py LF 643d5e1e (working tree identical; the only file changed). The base is 71f99ae6 (MERGEABLE in
READY_scratch_dir_e_delta, delta 2), which equals main's copy. `git merge-tree --write-tree main 2cc68e9a` gives df8f04e9, rc 0.
No Gradle was run (the CERT-K2-DEFLATED arm is running, and the delta touches no Kotlin or Gradle file).

## Safety first (code read before any run)
- **Real paths.** C13 (new) purges `sb = <root>/S`, a fixture under `root = mkdtemp(dir=base())`. Its `days=0` is floored to 1, and the fixture is the only target. The real-path purges are unchanged: C10 `refused()` on the system temp, drive root, REPO_ROOT and its parent, all `dry_run=True`. All 12 child spawns still use `cenv` (TMP/TEMP/TMPDIR on fixtures). No mutant touches `dry_run`.
- **The builder's incident attribution.** Mutant G6 ran a zero-age `--all` purge on `dirname(REPO_ROOT)` = E:/TaxoArena_tmp, because the copy sat under the real base. That is consistent with the ckd_* loss I recorded in delta 1, and it is the class that a closed sandbox prevents. My harness places REPO_ROOT, its ancestor and the drive root all inside a `subst H:` drive.
- **PID reuse is conservative.**
  - `_owner_alive` and `_owner_pid` use the pid only. The start epoch is written but never compared.
  - A reused pid therefore reads as alive, and the dir is KEPT; reuse can never cause a purge.
  - An unreadable or garbage owner file is treated as alive (`return True`), so it is kept too.
- **No owner file plus fresh content is kept.** Without an owner file the age test always runs, now also for dead-pid py_/run_ dirs (N4). A dir whose newest file is under 24 h old is kept. C13 shows this for `fresh_inside` (no owner, `--all`) and for a dead-pid py_ dir with 10-minute-old content. An unfinished scan (the cap) returns None, which counts as young.
- **Residuals.**
  - Staleness is write-time (mtime) only. A process that only READS files in an ownerless dir for more than 24 h is not protected.
  - On Windows, an open handle makes rmtree fail part-way, so such a dir can be left half-deleted. (LOW, S-3)

## Per-claim table
| # | Claim | Result | Evidence | Sev |
|---|---|---|---|---|
| 1 | selftest 14/14 (C0-C13) | CONFIRMED | Sandbox with TMPDIR on a separate `H:\gitbash_tmp` (simulated Git Bash) and with all 3 redirected: `SELFTEST OK: 14 checks` both times. | - |
| 2 | 31/31 mutants | CONFIRMED for the 25 I re-ran (the other 6 are carried) | My implementations: G1-G11, D4a, D4b, D5 and N1-N6 all killed (G10 re-anchored to `if pid is None and not all_entries`). N1 C13 (fresh_inside removed); N2 C13 (owned removed); N3 C13; N4 C13; N5 C1 (owner file missing); N6 C13 (cap). M1-M11: code untouched by this delta, not re-run, carried. | - |
| 3 | nothing younger than 24 h is ever purged | REFUTED | `days = max(float(days), MIN_AGE_DAYS)` with `days=nan` gives `max(nan, 1.0) = nan`, so `limit = nan` and `m >= limit` is False: every entry with a known mtime and a dead owner is purged at any age. Sandbox: dead-pid py_ dir with a file written 0 s earlier, `purge_stale(days=float('nan'))` gives `removed 1`, dir gone. The CLI accepts it: `--purge-stale --days nan --dry-run` gives `removed 1`. | MEDIUM (S-1) |
| 4 | live owner file protects | CONFIRMED (top level) | Code plus C13 `owned` kept (N2 killed). | - |
| 5 | conservative branches tested | PARTLY | My extra mutants P1 (gradle/ owner check dropped), P2 (unreadable owner treated as dead) and P3 (`--run` dir gets no owner file) all SURVIVED. All three sit on the keep side; P3 is also covered by the `run_<pid>` name while the wrapper lives. O2 (CLI `--all` default) still survives. | LOW (S-2) |
| 6 | no stray markers | CONFIRMED | `find /e -maxdepth 3`, Temp `-maxdepth 3` (sandbox excluded), repo `-maxdepth 4`, `C:\`, `C:\Users\octav`, `Z:\`: exactly 1 marker, `E:/TaxoArena_tmp/.taxoarena_scratch`. Harness abort guards: no violation in 4 runs. | - |

## Defects and fixes
- **S-1 (MEDIUM):** floor bypass by NaN.
  Fix: `days = float(days); days = days if days >= MIN_AGE_DAYS else MIN_AGE_DAYS`. NaN fails `>=`, so it gets the floor.
  Also write the young test fail-closed: `if m is None or not (m < limit)`.
  Add a C13 line: `purge_stale(days=float('nan'))` keeps `half_day`. Add a mutant that restores `max()`.
- **S-2 (LOW):** add fixtures for an unreadable owner file (kept), a gradle/ child with a live owner (kept) and the `--run` dir's owner file. Optionally compare the owner's start epoch with the process creation time; not needed, because the current behaviour already keeps.
- **S-3 (LOW):** document that staleness is write-time only and that a locked file leaves a dir part-deleted. Optionally skip a dir if any file inside cannot be opened for delete, before rmtree.
- Carried LOW: D-3, D-6 (O2), dead `envx`.

## Merge instructions
After S-1 (and its check) is fixed: on main, `git merge --no-ff scratch-stale` (trial merge clean), committing by paths only.
Until then, nobody runs `--purge-stale` (the builder's own rule).

## Commands
```
git diff c4e7499b 2cc68e9a --stat -> scratch_dir.py only; git rev-parse c4e7499b:tools/analysis/scratch_dir.py = 71f99ae6 (= main)
subst H: <scratchpad>\sbx3\drive ; harness3.py (copy at H:\w\repo\tools\analysis; TMP/TEMP=H:\sys; TMPDIR=H:\gitbash_tmp (GITBASH=1) or H:\sys;
  TAXOARENA_TMP=H:\base; abort on a marker at real Temp/C:\/E:\/Z:\/repo/C:\Users\octav/experiment_results/E:\TaxoArena_tmp\gradle,
  any loss of old real-Temp or E:\TaxoArena_tmp entries, any E:\ top-level change, any change in H:\gitbash_tmp)
  GITBASH=1 python harness3.py sd4.py   -> base OK 14; G1-G11, O1, O3, D4a, D4b, D5, O4, N1-N6 rc 1; O2, P1, P2, P3 rc 0; "no violation"
  python harness3.py sd4.py base N1..N6 P1..P3 -> same
python -c "...purge_stale(days=float('nan'), root=H:\nan\base)" -> removed 1 (0-s-old dir gone); CLI --days nan --dry-run -> removed 1
python -c "print(max(float('nan'),1.0))" -> nan
find ... -name .taxoarena_scratch -> only E:/TaxoArena_tmp; subst H: /D
```
