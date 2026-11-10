# DELTA READY review for the one-time opening: BBH-RESERVED-CONFIRM, the constants commit (benchzoom `bbh-reserved-prep` 727cc67..f307079)

Reviewer: adversarial-reviewer, 2026-11-07. Authority: D-2026-11-07-1 on top of D-2026-11-06-3. Zero LLM calls. The reviewer
read both repositories and every data file read-only, and wrote only this file. The reviewer did not pass the opening flag,
did not construct the sealed reader, and did not run `freeze` or `open` for real.

Range: benchzoom dc31b5a ([P5] plan bracket, 08:19:07) and then f307079 (the constants commit, 08:53:54). That is 3 files,
0 under `src/`, not in master (`merge-base --is-ancestor f307079 master` exits 1). TaxoArena: the registration is 26edca97
(prog L25897-L26018).

Reviewed blobs (LF, from `git hash-object`, equal to `HEAD:`):
- `examples/bbh-reserved-confirm.py` blob:192e52390ef183b0c3d3e2013b34d492ff206530 (LF working tree, 0 CR);
- `tests/test_bbh_reserved_confirm.py` blob:7c11abdc20dfe3e3eeb19fca2e6fe324ceec67f0 (LF);
- `docs/bbh-reserved-prep.md` blob:3beef8b6b08fcfb1a26b1333e3342600dce31a18 (LF).
These are unchanged since the registration's Instrument: `bbh_reserved_common.py` fe5530b0, `bbh-reserved-tree.py` cc955d59, and
`bbh-reserved-prep.py` dafd9eda (its CRLF working-tree rendering is aaad88f4, with 1,919 CR).

## Verdict

- **`freeze --roster 342 --text work` at f307079: READY**, one time, under OP1-OP2 below. `freeze` runs the same `work_side`
  as the dry run, which this review observed (rows 5-9). It reads no RESERVED response and constructs no reader. It must
  print sha256 `5320b3283434ea0511a4df0bd8fb1fac9b574a0c61257debed15692b13b21b82`.
- **`open`: NOT READY at f307079.** It refuses by construction: with the module's `Reg()`, `FREEZE_SHA` is PENDING, and
  L796 raises before L822 (the frozen-bytes check) and before L824 (`SealedReader(`).
- **`open` on the FREEZE_SHA commit F: READY iff every one of OP3-OP8 holds.** Registration condition (4) leaves this
  check to the reviewer. If any step fails, `open` is NOT READY and F needs a delta review. This review cannot give the
  author's go (O3, OP5), which is a separate gate.
- **Conditions of the prior delta.**
  - D2 (MEDIUM): carried as a written operator step, with a precomputed manifest pin (OP3, OP6).
  - D3 (LOW): carried. The measured residual is 0 (row 12).
  - D4 (LOW): checked by hand at OP4.
  - D5 (LOW): read "(by construction; Q1)", next to the reviewer's own count (row 8).
- **Support:** present and NON-VACUOUS. It is unchanged by the delta and re-derived here (row 14).

## Per-claim table (deciding claims)

| # | claim | reviewer's number / evidence | state | sev |
|---|---|---|---|---|
| 1 | The constants equal the registration | REG_COMMIT = 26edca97428a8538b9eae60b8eea8a2f331593d8 (full sha; on main). REG_ROSTER 342; REG_TEXT "work"; FREE_ARM "AFI" (unchanged); FREEZE_SHA PENDING; R342_SHA = the registration's full ids sha. The reviewer's own parse of the section at 26edca97 matches PREDICTIONS[342] 8 of 8 and SUPPORT_PLAN 5 of 5 (n 2,304; 5.38 / 1.34; DEFF2 3.42; 4.91 / 1.23; 2.22 / 0.92 = 0.9173). The seeds are 20261106 with streams 7 / 8 / 9, and B 2,000 | CONFIRMED | - |
| 2 | The delta is the constants only (plus selftest and docstring) | AST of the runner (109 top-level nodes): only the module docstring, REG_COMMIT, REG_ROSTER, REG_TEXT and `selftest` differ from 727cc67. The plan is +14 / -0 (insertion only; [P5] is committed before f307079). The test file changes 58 / 9 lines | CONFIRMED | - |
| 3 | The registration check passes | The heading regex (U+2014) matches 1 line at 26edca97, 0 at its parent and 1 at main; `merge-base --is-ancestor` exits 0. The dry run's 3 git calls into TaxoArena (`rev-parse --verify`, `merge-base --is-ancestor`, `show <sha>:docs/judge_v2_program.md`) are all read-only | CONFIRMED | - |
| 4 | Dry run: code state head f307079, 31 files, manifest 2c1d180c..., 0 findings | Own observed run and plain CLI run: the same line. The reviewer recomputed the manifest from `git rev-parse HEAD:<path>` (31 of 31 equal): sha256 2c1d180cea44e4077cd37f945b5376059c0da18e639b852c6bb2babfdeeeb935 | CONFIRMED | - |
| 5 | The frozen object's sha256 is 5320b328... (as before) | 5320b3283434ea0511a4df0bd8fb1fac9b574a0c61257debed15692b13b21b82. The observed run (3 BLAS threads), the plain CLI (default, 1 thread) and the builder's dry_A agree in all 18 log lines, with CR stripped. The sha is thread-invariant from 1 to 3 | CONFIRMED | - |
| 6 | No sealed reader was constructed | The reviewer's tripwire on `SealedReader.__init__` fired 0 times; the one on `_read_and_score` fired 0 times; the class counter is 0. The observers were armed to raise | CONFIRMED | - |
| 7 | No RESERVED response was read | The reviewer's `pandas.read_parquet` wrapper sits below the runner's audit and refuses unfiltered or RESERVED-filtered reads before they run. It saw 343 reads over 342 files (342 with the score column); 1,185,751 ids requested and returned. RESERVED ids in a filter: 0. RESERVED rows returned: 0. Non-WORK rows: 0. Unfiltered: 0. Direct pyarrow `read_table` / `ParquetFile` / `dataset` calls: 0. The ids come from the split files, with the pins 3d4d644a / 9ef05cc2 checked by the reviewer | CONFIRMED | - |
| 8 | Vectors and texts are WORK only (D5) | One `load_vectors` call over 3,457 texts, all carrying a WORK census text_sha256 (3,454 distinct). None of these hashes appears among the RESERVED items' census hashes. The npz members read were `X`, `keys` and `name`, once each (Q1: the whole `X` is decompressed) | CONFIRMED (Q1) | LOW (E4) |
| 9 | No writes | Python-level write-opens: 0 (only the `nul` device, from `platform`'s `cmd /c ver`). fs events: 0. `find -newer` gives 0 files under E:/benchzoom_demo, 0 under E:/benchzoom_cache and 0 in the worktree. Porcelain is 0. The TaxoArena `.git/index` and HEAD stats are unchanged. The npz and items.csv sha256 are unchanged. 0 OPENED / freeze / outcome files exist, and the output directory is absent | CONFIRMED | - |
| 10 | `open` refuses without the flag | Real CLI, 3 forms, each exit 1. Two print "opened only with --open-sealed-reserved" (with and without `--registration`); the third (`--text all`) refuses at the CLI check. Structurally, with the module's constants, nothing reaches L824 (row "open" above) | CONFIRMED | - |
| 11 | C1 on the final tip: a modified copy of any executed module refuses | Sandbox clone at f307079, the real `code_check()`. Control: PASS (2c1d180c). Each of the 31 manifest files, edited and uncommitted: REFUSED 31 of 31. Also REFUSED: an untracked `examples/` file; a lazily importable non-manifest module (`meter_axis.py`); a staged edit; an `--assume-unchanged` edit (porcelain 0, caught by the blob comparison). A COMMITTED edit PASSES (manifest 88277c9c): D2 | CONFIRMED (D2) | MEDIUM (E1) |
| 12 | D3 residual | No module was executed after the check on the WORK path (the after-set is a subset of the manifest). Every lazy import of a repository module in the executed modules resolves under `examples/` or `src/`, which porcelain covers whole | CONFIRMED | LOW (E2) |
| 13 | Tests and mutants: selftest 157 / 0; pytest 15; mutants 14 of 14 | Builder's K1-K14 re-run: 14 of 14 killed, controls C0 / C0s pass. Prior review's RV1-RV4 re-run at f307079: 4 of 4 killed, RV0 passes. FREEZE_SHA-commit rehearsal: selftest 157 PASS / 0 FAIL; the test file 15 passed; 0 real-data opens under the reviewer's tripwire. The tree and prep selftests are not re-run (their blobs are unchanged; DELTA row 15). The full suite is the builder's log (1049 / 1 / 0), taken as given | CONFIRMED | - |
| 14 | Support (R342) | SE = SD_row x sqrt(DEFF2 / 2,304): 0.348 x sqrt(3.42 / 2,304) = 1.341pp; 0.320 x sqrt(3.39 / 2,304) = 1.227pp. The identity gives SE_L = sqrt(0.5 x 1.2267^2 - 0.25 x 1.3387^2 + 0.5 x 1.0364^2) = 0.9173pp. n_eff 673.7 / 679.6 / 556.5. MDE80 3.75 / 3.44 / 2.57pp. C1 and C2 SCOREABLE, C3 DESCRIPTIVE-ONLY (2.22 < 2.57); power 0.980 / 0.979 / 0.677. All equal the registration | CONFIRMED | - |
| 15 | The FREEZE_SHA commit can be pinned now | Rehearsal clone: the 3 prescribed replacements (OP3), committed. Numstat is 1 / 1 confirm and 2 / 2 test. Blobs: confirm 5e0dfca320132455a1bde8e05db9dd280cdc7c70, test dedcabd6708b668da0c36aa240275d4c006711e5. Real `code_check()`: PASS, manifest 31 files, sha256 **de21fc92f33abceb22d63eb3d72062ea1d71836211b8aad8f14530c5e405cecc** | CONFIRMED | - |

## Defects and conditions (each with its fix)

- **E1 MEDIUM (= DELTA D2; carried, not fixed):** the code check certifies "committed", not "reviewed". A committed extra
  byte passes with a new manifest (OM8: 60b51432; OM9: 23d89cba). Fix: OP3 and OP6 below compare the manifest with the pin
  de21fc92... A `--manifest` flag in code would change the pins and need a new review. This step is enough.
- **E2 LOW (D3):** the "modules executed after the code check" line is printed after the sealed read. Its measured
  residual is 0 and is covered by porcelain (row 12). Fix: OP8 reads that line and requires 0.
- **E3 LOW (D4):** the runner does not count the FREEZE_SHA bracket. Fix: OP4, a count by hand.
- **E4 LOW (D5):** the dry run's and freeze's "RESERVED texts read 0; RESERVED vectors read 0" are literals. Read them
  as "(by construction; Q1)". The reviewer's count is row 8.
- **E5 LOW (prescription, not a defect):** the test asserts `FREEZE_SHA == "PENDING"` (L96, L98), so F must touch 2 files.
  F may carry nothing else: no plan bracket and no docstring edit, because the plan and the test file are in the manifest.
  Record the freeze in the TaxoArena bracket.
- **E6 LOW:** `test_predictions_and_support_equal_the_registration` checks a hard-coded copy, not the registration text.
  The reviewer's own parse (row 1) closes the gap for these constants. No fix is owed.
- **E7 (the reviewer's harness, no product defect):** the first tripwire (`trip.py`) lacked a `__main__` guard. Under it,
  the tree selftest's 2-worker spawn pool hung. The rehearsal pytest was re-run under `trip2.py`: 15 passed. The hung
  pair, PID 276224 and its launcher 286328 (idle, about 31 s CPU), could not be killed: the permission was denied. Kill
  it by PID.
- **Q1 (carried):** the seal is API-level. The whole npz `X` is decompressed, and parquet filters are applied inside
  pyarrow.

## Run-operator steps (written; every count must match exactly; otherwise STOP and get a delta review)

- **OP1 freeze at f307079.**
  - Preconditions: the worktree HEAD is f30707931f8f182de1f5ecd0a5053ad413f3c874; `git status --porcelain | wc -l` is 0;
    no other python or java process; `E:/benchzoom_demo/followups/bbh-reserved-confirm` is absent;
    OMP / OPENBLAS / MKL are unset.
  - Command, from the worktree: `Z:/FAC/TUBerlin/benchzoom/.venv/Scripts/python.exe examples/bbh-reserved-confirm.py freeze --roster 342 --text work`.
  - Accept iff its line prints sha256 5320b3283434ea0511a4df0bd8fb1fac9b574a0c61257debed15692b13b21b82, code head
    f307079..., manifest sha256 2c1d180c..., registration 26edca97..., and `sha256sum` of `freeze_R342_work.json` is the
    same. On any other sha, stop: write nothing more and pin nothing.
- **OP2** Back up the freeze file to `E:/TaxoArena_backup_<date>_bbh-reserved-confirm/` with SHA256SUMS.
- **OP3 F (builder).** F is one commit on `bbh-reserved-prep` (`git rev-list --count f307079..F` = 1) made of exactly
  three replacements of `"PENDING"` by `"5320b328...b82"`:
  - confirm L252, `FREEZE_SHA = "PENDING"` (the rest of the line unchanged);
  - test L96, `conf.FREEZE_SHA == "PENDING"`;
  - test L98, `(REGISTRATION, 342, "work", "PENDING")`.

  Checks: `git diff --name-only f307079 F | wc -l` = 2; `git rev-parse F:examples/bbh-reserved-confirm.py` = 5e0dfca3...;
  `F:tests/test_bbh_reserved_confirm.py` = dedcabd6...
- **OP4 (D4)** On TaxoArena: `git show main:docs/judge_v2_program.md | LC_ALL=C awk '/^## Registered 2026-11-07 .*BBH-RESERVED-CONFIRM:/{s=1;next} /^## /{s=0} s' | grep -c 5320b3283434ea0511a4df0bd8fb1fac9b574a0c61257debed15692b13b21b82` >= 1.
- **OP5** The author's go (O3) is written verbatim to `docs/agents/author_decisions/<date>.md` before anything below.
- **OP6 (D2)** At F, run `reserved --dry-run --roster 342 --text work`. It must exit 0 and print: head F; manifest 31 files
  sha256 de21fc92f33abceb22d63eb3d72062ea1d71836211b8aad8f14530c5e405cecc; findings 0; FREEZE_SHA 5320b328...; the frozen
  object in memory 5320b328...; sealed reader constructed 0.
- **OP7** Immediately before `open`: HEAD = F; porcelain 0; no foreign python or java process; the output directory holds
  only `freeze_R342_work.json`, and its sha256 = FREEZE_SHA.
- **OP8 `open`, once.** The exact command, from `Z:/FAC/TUBerlin/benchzoom_wt_bbh-reserved-prep`:
  `Z:/FAC/TUBerlin/benchzoom/.venv/Scripts/python.exe examples/bbh-reserved-confirm.py open --roster 342 --text work --registration 26edca97428a8538b9eae60b8eea8a2f331593d8 --open-sealed-reserved`.
  - Afterwards: outcome.txt / outcome.json / SHA256SUMS, or one `outcome_REFUSED_<UTC>.txt` (recorded and never retried).
  - The line "modules executed after the code check" reads 0; porcelain is 0.
  - Back up the output with SHA256SUMS. The POSTRUN re-measures DEFF from the RESERVED clusters.

## Own mutants and controls (sandbox clones under E:/TaxoArena_tmp/review-bbh-reserved-open only)

| id | change | result | decisive |
|---|---|---|---|
| OM6x31+4 | each executed module (31), plus untracked, lazily imported, staged and assume-unchanged edits, uncommitted at f307079 | killed (REFUSED 35 of 35) | yes |
| OM7 | control: F as prescribed (OP3) | PASS, manifest de21fc92; selftest 157 / 0; pytest 15 passed | control |
| OM8 | F plus one committed docstring byte (common module) | SURVIVES `code_check` (manifest 60b51432); killed by OP6 | yes (E1) |
| OM9 | F with FREEZE_SHA one hex digit off | SURVIVES `code_check` (manifest 23d89cba; confirm blob 251df238); killed by OP3 / OP6; `open` would also refuse at "!= FREEZE_SHA" before L824 (selftest Y10) | yes |

## Commands (scripts and logs: E:/TaxoArena_backup_2026-11-07_review-bbh-reserved-open, 37 files + SHA256SUMS, its sha256 a92715f1f867c878..., 37 / 37 OK)

```
git diff --numstat 727cc67..f307079; python -I asteq.py        # 3 files; runner nodes: docstring, 3 constants, selftest
git show 26edca97[^|main]:docs/judge_v2_program.md | LC_ALL=C.UTF-8 grep -cP '^## Registered \d{4}-\d{2}-\d{2} .*\x{2014} BBH-RESERVED-CONFIRM:'   # 1 / 0 / 1
python -I reg_vs_code.py                                        # constants, PREDICTIONS 8/8, SUPPORT 5/5 vs the section at 26edca97
python -I observe_dry.py <out> 3                                 # observed real dry run, 373.7 s; post_proof.py -> proof_summary.log
python examples/bbh-reserved-confirm.py reserved --dry-run --roster 342 --text work   # plain CLI; diff vs observed / dry_A: equal
python examples/bbh-reserved-confirm.py open ... (3 forms, no flag)                    # exit 1 x3 (noflag.log)
find /e/benchzoom_demo /e/benchzoom_cache -newer marker | wc -l  # 0 (both runs); worktree 0; porcelain 0
bash c1_battery.sh   # om6.log: MANIFEST CASES 31 REFUSED 31; + 4 REFUSED; committed edit PASS 88277c9c
bash rehearsal.sh; trip2.py pytest ...; rehearsal_om89.log      # de21fc92; 157/0; 15 passed; OM8 60b51432, OM9 23d89cba
python -I mutants_c_rerun.py; python -I mutants_rv_rerun.py rv_spec_1_4.json rv_f307079 --jobs 1   # 14/14; RV1-RV4 4/4
```
At most 3 processes ran at a time, with single-threaded BLAS except the one observed dry run (3 threads). No other agent's
process was running at the dry runs.
