# archive/

This folder holds files that are no longer part of the active TaxoArena workspace: one-off
exploration and calibration configs and their run output, superseded database backups, stale
run logs, and obsolete scratch artefacts.

## Nothing here was deleted

Every entry was **moved**, not removed. The original relative path is preserved underneath
`archive/`, so `archive/experiment_configs/mcs28_test.toml` was previously
`experiment_configs/mcs28_test.toml`. `ARCHIVE_MANIFEST.md` lists every entry with its
original path, size, last-modified date, and the reason it was archived.

Files that git tracked were moved with `git mv`, so their history is intact and the rename is
staged. Untracked files were moved with a plain move. **No commit was made** — `git status`
shows the renames and the new untracked `archive/` tree, and you can undo the whole operation
with `git reset` plus the restore step below.

## How to restore a file

Look the file up in `ARCHIVE_MANIFEST.md`, then move it back to its original path. For a
tracked file:

```sh
git mv archive/experiment_configs/mcs28_test.toml experiment_configs/mcs28_test.toml
```

For an untracked file or a directory:

```sh
mv archive/experiment_results/mcs28_test experiment_results/mcs28_test
```

On Windows, `mv` from Git Bash occasionally fails with "Permission denied" on directories.
PowerShell's `Move-Item -LiteralPath <src> -Destination <dst>` works in those cases.

To restore everything at once, move each top-level entry in `archive/` back to the repository
root, merging directories rather than replacing them (`experiment_configs/`,
`experiment_results/`, `logs/`, `benchmark_backups/` and `tuning/` all still exist in the
working tree and only had a subset of their contents archived).

## What was deliberately *not* archived

The reference check kept several things that look obsolete but are still load-bearing:

- **`ratings_{law,philosophy,history,psychology,math,engineering}_paired.db`** and
  **`{law_baseline,philosophy,history,psychology,engineering}_secured/`** — read directly by
  `report/Figures/make_rho_levels.py`, `make_screen_vs_arena.py` and `make_frozen_tree.py`.
- **`experiment_results/arena_math_frozen/`** — read by `make_verdict_mechanism.py` and
  `make_rubric_specific_not_decisive.py`.
- **All of `docs/`** — every document is indexed from `docs/README.md`, and several are the
  frozen record of a specific run cited by the thesis.
- **All of `tools/`**, `config/`, `src/`, `report/` and the Gradle files.
- Configs cited by a surviving config's provenance header (`canonical_baseline.toml`,
  `mcs30_eps02_tree*.toml`, `mcs30_eps02_test.toml`, `thesis_canonical.toml`,
  `smoke_arena_v2.toml`) and the result directories they name.
