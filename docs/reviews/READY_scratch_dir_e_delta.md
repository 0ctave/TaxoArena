# Delta READY: scratch-dir-e 26378771..6c477f0d (D-1/D-2/C-1/C-2 of READY_scratch_dir_e), 2026-10-04, zero calls

**VERDICT: NOT MERGEABLE yet. MERGEABLE after D-4 (a 3-line selftest fix, verified below) and D-5 (a refusal to mark a
non-empty dir). One delta review of scratch_dir.py covers both.**
- The D-1 guards hold: 11/11 guard mutants were killed in a closed sandbox, with no real marker and no real deletion.
- C-1 and C-2 are CONFIRMED.
- The selftest is RED in this shell, because TMPDIR leaks past the fixtures (D-4).

Reviewed blob: scratch_dir.py LF fc534611 (working tree identical). The reverted scripts are dataset_survey d83f3824 and
supergpqa_stage0 35b11858, both equal to their READY pins. `git merge-tree --write-tree main 6c477f0d` gives 29498a32, rc 0.

## Safety first: what I verified before any mutant ran (by reading the code)
- **Real paths the selftest touches.** C10 purges `_SYSTEM_TEMP`, the drive root of `root`, `REPO_ROOT` and its parent, all with `dry_run=True`.
  C6 and C8 delete only inside fixtures under `root = mkdtemp(dir=base())`. `REPO_ROOT` comes from `__file__`, so it is the copy's location.
  No mutant (theirs or mine) touches `dry_run`. Only those rules make "delete nothing real" hold.
- **Hole found (D-4).** The children get TMP and TEMP set to a fixture, but **not TMPDIR**. `tempfile` reads TMPDIR first, and Git Bash
  exports it (`TMPDIR=C:\Users\octav\AppData\Local\Temp`). So the C11 child-1 still resolves the REAL system temp. That case cannot mark or delete anything real: its base candidate is the fixture `SYS2`, and C5 and C11 child 2 set `_SYSTEM_TEMP` explicitly. But the commit's claim "every child gets TMP/TEMP = a fixture" is false in the agents' shell, and C11 fails there.
- **My harness (closed sandbox; the builder's harness is not committed).**
  - Layout: `subst H:` onto a scratchpad dir. Copy at `H:\w\repo\tools\analysis\scratch_dir.py`, so REPO_ROOT, its ancestor and the drive root are all inside H:. Env: `TMP=TEMP=H:\sys`, `TAXOARENA_TMP=H:\base`, TMPDIR either `H:\sys` or removed.
  - Abort if, after any run, a marker appears at any of: the real Temp, `C:\`, `E:\`, `Z:\`, the repo root, `C:\Users\octav`, `experiment_results`, `E:\TaxoArena_tmp\gradle`.
  - Also abort if any real-Temp entry older than 2 h, any `E:\TaxoArena_tmp` entry older than 30 min, or any `E:\` top-level name is lost.
  - Result: no abort in 4 harness runs (19 selftest executions).

## Per-claim table
| # | Claim | Result | Evidence | Sev |
|---|---|---|---|---|
| 1 | selftest C1-C11 passes | REFUTED in Git Bash; CONFIRMED without TMPDIR | Sandbox with TMPDIR=H:\sys: rc 1, `AssertionError: H:\base\...\SYS2` (C11). The same run with TMPDIR removed: `SELFTEST OK: 11 checks`. With TMPDIR added to the 3 child envs (C5, C11 x2), it passes with TMPDIR set and unset. | HIGH (D-4) |
| 2 | 22/22 mutants killed | PARTLY; I re-ran the 11 guard mutants (G1-G11) | G1-G11 implemented from the docstring table: **11/11 killed**, each by its intended check (C10/C5/C11/C6). M1-M11 are unchanged code since my first review, so not re-run. | - |
| 3 | no stray marker on real paths | CONFIRMED | `find /e -maxdepth 3`, `find <Temp> -maxdepth 3` (sandbox excluded), `find <repo> -maxdepth 4`, and `C:\`, `C:\Users\octav`, `Z:\` checked: exactly one marker, `E:/TaxoArena_tmp/.taxoarena_scratch`. | - |
| 4 | D-1 guards refuse forbidden or unmarked roots | CONFIRMED | Code read (forbidden(): system temp, drive root, repo root, ancestors, `TaxoArena_backup_*`; marker check; both checked before any scandir). G1-G7 are killed with the right refusal messages. | - |
| 5 | D-1: only scratch dirs ever get marked | REFUTED (residual) | base() marks ANY non-forbidden TAXOARENA_TMP, even a non-empty dir. Sandbox demo: `TAXOARENA_TMP=H:\demo\outputs` (holding a 3-day-old `run_of_record/outcome.txt`) plus one `import scratch_dir` writes the marker; then `--purge-stale --all --root H:\demo\outputs` gives `removed 1`, so the outputs are gone. Needs a wrong env AND `--all`. Without `--all` only dead-pid py_/run_ dirs and gradle/ children go. | MEDIUM (D-5) |
| 6 | D-2 default purge spares other agents' entries | CONFIRMED (function); CLI untested | G10 killed (C6). O2 (the CLI passes `all_entries=True` always) **survived**: no check runs the CLI default on a marked root. | LOW (D-6) |
| 7 | C-1 reverts | CONFIRMED | The 2 diffs restore `import tempfile`. The blobs equal the READY_w0_delta2 pins. 34 scripts stay edited. | - |
| 8 | C-2 Gradle | CONFIRMED (my run) | No java live. `.\gradlew.bat test --offline` on 6c477f0d: 553 tests, 2 failed (MrlRoutingTest.testMrlConfigDefaults, TraceEnvelopeUnwrapTest blank-trace = the 2 known). `E:/TaxoArena_tmp/gradle` holds 0 entries afterwards. C: Temp Kotlin-test dirs 16 -> 16. `--stop` done. | - |

## Own mutants (sandbox)
- O1: purge does not skip the marker entry. KILLED (C6 tally).
- O2: CLI `--all` is ignored and everything is purged. SURVIVED (D-6). Not decisive: the function path is guarded by G10.
- O3: base() marks a forbidden env before redirecting it. KILLED (C11).

## Defects and fixes
- **D-4 (HIGH):** add `TMPDIR=<fixture>` wherever a child env sets TMP/TEMP:
  - C5: `TMPDIR=fake_sys`;
  - C11 child 1: `TMPDIR=sys2`;
  - C11 child 2: `TMPDIR=fake_sys`.
  Restate the docstring's SAFETY line as "TMPDIR/TMP/TEMP". Verified: with this 3-line sed patch the selftest passes with TMPDIR set and unset.
- **D-5 (MEDIUM):** base() writes the marker only into a dir it has just created, or one that is empty. An existing non-empty unmarked TAXOARENA_TMP is redirected to its `TaxoArena_tmp` subdir, with a warning. E:/TaxoArena_tmp is already marked, so this does not affect it. Add a selftest check (a non-empty unmarked env dir stays unmarked) and a mutant.
- **D-6 (LOW):** add a CLI check: `--purge-stale --root <marked fixture>` without `--all` keeps a foreign old entry.
- **D-3 (LOW, carried):** junction fixture and non-mp child check; still not done.
- **Incident follow-up (author):** the deleted Temp entries cannot be restored here. Separately, the ckd_* hand-made files of another agent in E:/TaxoArena_tmp seen at 03:52 (ckd_patch1-4.py, ckd_base_src/ ...) were gone at 04:31. They were young, so neither the old nor the new default purge removes them. The cause is UNDETERMINED (possibly their owner).

## Merge instructions
After D-4 and D-5 are fixed and delta-READY'd: on main, `git merge --no-ff scratch-dir-e` (the trial merge is clean; main's
build.gradle.kts is unchanged since the base). Commit by paths only.

## Commands
```
git diff 26378771 6c477f0d --stat -> scratch_dir.py, dataset_survey.py, supergpqa_stage0.py
python -c "import os,tempfile;print(os.environ.get('TMPDIR'))" -> C:\Users\octav\AppData\Local\Temp  (Git Bash)
subst H: <scratchpad>\sbx\drive ; harness.py (copies to H:\w\repo\tools\analysis; env TMP/TEMP=H:\sys, TAXOARENA_TMP=H:\base; abort guards above)
  python harness.py sd_new.py base            -> rc 1 C11 (TMPDIR set)
  NO_TMPDIR=1 python harness.py sd_new.py     -> base OK 11 checks; G1..G11 rc 1 (11/11); O1 rc1, O2 rc0, O3 rc1; "no violation"
  python harness.py sd_fix.py base (+NO_TMPDIR) -> OK both
sandbox demo: TAXOARENA_TMP=H:\demo\outputs import -> marker; --purge-stale --all --root H:\demo\outputs -> removed 1
find /e -maxdepth 3 -name .taxoarena_scratch -> 1 (E:/TaxoArena_tmp); Temp/repo -> 0
.\gradlew.bat test --offline -> 553 / 2 failed (known); .\gradlew.bat --stop; subst H: /D
```

---
# Delta-2 READY: 6c477f0d..6b63f362 (D-4, D-5), 2026-10-04, zero calls

**VERDICT: MERGEABLE.**
- D-4 and D-5 are CONFIRMED.
- Selftest 13/13 (C0-C12).
- 18 of 19 mutants killed in a sandbox. The builder's set is 11 guard mutants plus D4a, D4b and D5; the other 5 are mine. The survivor is O2 (D-6, LOW, carried).
- No real marker and no real deletion.

Reviewed blob: scratch_dir.py LF 71f99ae6 (working tree identical; the only file in the delta).
Trial merge: `git merge-tree --write-tree main 6b63f362` gives f91afb00, rc 0.

**Safety, by reading the code before any run.**
- **Children.** All 12 `subprocess.run` calls in selftest() pass `env=cenv(...)`. cenv sets TMP, TEMP and TMPDIR to a fixture. C9's multiprocessing workers inherit that env. `envx` (L57) is now dead code (LOW).
- **run_wrapped** sets TAXOARENA_TMP/TMP/TEMP/TMPDIR (L457).
- **The selftest process itself, with Git Bash TMPDIR/TMP/TEMP inherited.** `_SYSTEM_TEMP` is the real Temp. It is touched only by C10 `refused()`, together with the drive root, REPO_ROOT and its parent. Every one of those calls passes `dry_run=True` (L616). C6 and C8 delete inside fixtures only. No mutant touches `dry_run`.
- **D-5.** `_claim` refuses an existing non-empty unmarked dir, so a wrong TAXOARENA_TMP is never marked; its TaxoArena_tmp subdir is used instead. E:/TaxoArena_tmp is already marked, so this does not affect it.

**Sandbox (`subst H:` onto a fresh scratchpad dir).**
- Layout: copy at `H:\w\repo\tools\analysis`. TMP and TEMP are `H:\sys`, TAXOARENA_TMP is `H:\base`.
- Two modes for TMPDIR:
  - (a) `H:\sys`: all three redirected together.
  - (b) GITBASH: TMPDIR on a separate `H:\gitbash_tmp` holding `keep.txt`. This simulates an inherited Git Bash TMPDIR that differs from TMP/TEMP.
- Abort guards as in delta 1, plus "gitbash_tmp unchanged".
- Results:
  - Base: OK, 13 checks, in both modes.
  - Mode b, all mutants: G1-G11 killed; O1, O3 killed; D4a killed (C7 `False`); D4b killed (C0 resolves `H:\gitbash_tmp`, so the guard fires); D5 killed (C12); O4 killed (C12; my mutant: claim also refuses an already-marked dir); O2 survived.
  - Mode a, re-run of G8, G9, D4a, D4b, D5, O4: all killed.
- "HARNESS DONE; no violation" in all 3 harness runs.

**Markers after the runs:** `find /e -maxdepth 3`, `find <Temp> -maxdepth 3` (sandbox excluded), `find <repo> -maxdepth 4`, and `C:\`, `C:\Users\octav`, `Z:\` checked. Exactly 1 marker: `E:/TaxoArena_tmp/.taxoarena_scratch`. `subst H: /D` done.

**Carried, LOW, do not block:**
- D-6: the CLI default (without `--all`) is untested; O2 survives.
- D-3: no junction fixture and no non-mp child check.
- `envx` is dead code.
- Incident follow-up for the author: the ckd_* files, as recorded in delta 1.

**Merge:** on main, `git merge --no-ff scratch-dir-e`, then commit by paths only. Never stage application.yml/.env/.gitignore. Gradle was unchanged since my delta-1 run (553 tests / 2 known failures).
