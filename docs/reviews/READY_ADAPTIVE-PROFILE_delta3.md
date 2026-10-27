# DELTA READY review: ADAPTIVE-PROFILE, the [AP-DENOM] fix (POSTRUN_ADAPTIVE-PROFILE R-1..R-4), adversarial reviewer, 2026-10-09

Reviewed: `git diff edb060b9..7279bf43` on branch `ap-denom-fix` (worktree `.claude/worktrees/ap-denom-fix`): 1 file
(`git diff --name-only edb060b9 7279bf43 | wc -l` = 1), `tools/analysis/adaptive_profile.py` +157 / -18.
Blob: blob:7d05a59ebff456fb042b1d79f965dec09bf2d567 (`git rev-parse` = `git hash-object`), sha256-lf16:7c5bdf53d38bedb7 (LF, of record);
the worktree holds the CRLF rendering, sha256-crlf16:fd61ad0fdcb0e4a2 (3,159 CR). Parent blob aff80c1d (= main). Code outside the delta:
cited from READY_ADAPTIVE-PROFILE_delta2.md and POSTRUN_ADAPTIVE-PROFILE.md, not re-derived. Authority: D-2026-10-09-1 (defab40c),
recorded prog L25394-L25401 (edb060b9). Zero calls.

## VERDICT: NOT READY (one BLOCKER, small; code fix of R-1..R-4 CONFIRMED)

R-1, R-2 and R-4 are closed, and so is R-3's dry-run line. One condition is not met: the registrar's record of D-2026-10-09-1
(L25397) requires the re-run's outcome FILE to carry the deviation line, and the script does not print it (B-1). The outcome file
is write-once (`U.write_outcome`, built from `lines` only, L1576), so the line cannot be added after the run. The fix is a few lines;
after it, a delta READY of the B-1 fix alone (no regression of R-1..R-4 is owed if the diff touches only the header).

## Per-claim table (deciding claims only)

| # | claim (builder) | reviewer's evidence | status | sev |
|---|---|---|---|---|
| 1 | R-1: TRAIN components counted from the data, independent of train_unit | `train_denoms` = `V.complete_items(K_tr, models)` and `train_meta[i][0]`; `build_ud` L540/L549 (v2_declared_cells) builds D.T from the same `complete_items(K_tr, models)` and D.comp from `train_meta[i][0]`, so it equals `len(set(D.comp[k] for k in D.T))` | CONFIRMED | - |
| 2 | R-4: TRAIN and GATE checks before the marker | `between` is called by `union_route_common.read_views` L202-203, before `open_tw("eval")` L206 and `G.read_marker` L224; `check_train` and `[AP-GATE-DENOM]` are now inside `between` | CONFIRMED | - |
| 3 | R-2: selftest runs the real unit ("item") | `_unit` patches `cfg_factory` with `V.PRECONDITIONS["train_unit"]`; run_e2e asserts n_units = n_train (1,101) != comp_train (934) | CONFIRMED | - |
| 4 | R-3: real --dry-run prints the TRAIN line from the data | own real `--dry-run` (busy.ps1 rc 1): rc 0, 66 lines, POOL pv2_1575de61bb20e977 first; "TRAIN DENOMINATOR (structural, pre-key; ...): 11841 items / 10781 components (registered 11841 / 10781)"; eval view "NOT opened" | CONFIRMED (to the digit; = POSTRUN claim 1) | - |
| 5 | Selftest 13/13 | own run on a `git archive` copy (E:): "[AP] selftest: 13 / 13 passed", 7 min 50 s | CONFIRMED | - |
| 6 | Decisive mutants die | X61, X62, X100, X102, X107 KILLED; X00 SURVIVED (own re-run) | CONFIRMED | - |
| 7 | No unrelated path; pinned modules untouched; train_unit stays "item" | 1 file changed; `PRECONDITIONS` untouched (v2_declared_cells not in the diff) | CONFIRMED | - |
| 8 | Nothing written; views unchanged | gen view c2930c609c67d6c7, eval view e35b751887820583: own sha256 before = after; `find experiment_results/archv2/adaptive_profile -type f \| wc -l` = 1 (the incident marker) before and after | CONFIRMED | - |
| 9 | D-2026-10-09-1 honoured | the registrar's L25397 reading: "the re-run's outcome file and outcome section carry the line 'DECLARED DEVIATION D-2026-10-09-1: second EVAL read after the refused attempt of 2026-10-09 (aff80c1d)'". `git show 7279bf43:<path> \| grep -c "DECLARED DEVIATION"` = 0; `grep -c "D-2026-10-09-1"` = 1 (docstring L226 only) | REFUTED | BLOCKER (B-1) |
| 10 | Backup | `sha256sum -c SHA256SUMS` in E:/TaxoArena_backup_20261009_ap_denom_fix: 27 OK, 0 not OK | CONFIRMED | - |

## Own mutants (sandbox copy E:/TaxoArena_tmp/rev_ap, appended to the MUTANTS table; run with `--mutants --only`)
- R01 `train_denoms` over a roster missing one model: KILLED (decisive: the key-complete rule).
- R02 `check_train` compares items only: KILLED (decisive: the incident's form at the comparison site).
- R03 `structural_train` roster = the whole registry (non-ACTIVE kept): SURVIVED. Not decisive. The fixture registry has no non-ACTIVE
  model, so the mutant is equivalent on the fixture. On real data it could only lower the count, and that refuses (fail-closed).
  The real dry-run's 11841 / 10781 shows that the shipped form is the right one. LOW (L-1).

## Defects and fixes
- **B-1 BLOCKER (builder).** Print the registrar's deviation line into `lines` in `run()` right after `U.header(...)`, verbatim:
  `DECLARED DEVIATION D-2026-10-09-1: second EVAL read after the refused attempt of 2026-10-09 (aff80c1d)`, plus its authority
  (defab40c; prog L25394-L25401). Add a run_e2e assertion that the line appears in the outcome file's bytes by value, and a mutant
  that drops it (must die). Do not print it in `--dry-run`, or print it there as "(will be printed by --run)", so that the dry-run
  shows it. Then a delta READY on the new blob.
- **L-1 LOW (builder, optional).** Add a non-ACTIVE model to the fixture registry so that R03 dies. No effect on the run.
- **Operator conditions for the re-run (unchanged from the record).** Clear the marker
  `experiment_results/archv2/adaptive_profile/adaptive_profile.READ_STARTED` by path only after the B-1 delta READY. Its copy is in
  E:/TaxoArena_backup_20261009_adaptive_profile_incident; log the clearance. busy.ps1 must exit 1 first. Launch directly.

## Run commands (ONLY after the B-1 fix and its delta READY; blob to be re-pinned)
```
powershell -NoProfile -File E:/TaxoArena_tmp/busy.ps1                      # must exit 1
python tools/analysis/scratch_dir.py --run -- python tools/analysis/adaptive_profile.py --selftest
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 python tools/analysis/adaptive_profile.py --dry-run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena
# clear the marker (operator, logged), then:
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 python tools/analysis/adaptive_profile.py --run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena
# back up outcome + export to E:/TaxoArena_backup_<date>_adaptive_profile with SHA256SUMS; never commit
```

## Commands (read-only; zero calls)
```
git diff --name-only edb060b9 7279bf43 | wc -l                                   # 1
git rev-parse 7279bf43:tools/analysis/adaptive_profile.py ; git hash-object <wt path>   # 7d05a59e both
git show 7279bf43:<path> | sha256sum ; | sed 's/$/\r/' | sha256sum                # 7c5bdf53d38bedb7 ; fd61ad0fdcb0e4a2
sed -n 171,230p tools/analysis/union_route_common.py ; sed -n 537,549p tools/analysis/v2_declared_cells.py   # between < eval open < marker; D.T rule
git archive 7279bf43 -- . ':!*.db' ':!*.npz' | tar -x -C E:/TaxoArena_tmp/rev_ap      # sandbox (+ R01-R03 appended)
python tools/analysis/scratch_dir.py --run -- python tools/analysis/adaptive_profile.py --selftest              # 13 / 13
python tools/analysis/scratch_dir.py --run -- python tools/analysis/adaptive_profile.py --mutants --only X00 X61 X62 X100 X102 X107 R01 R02 R03
   # 7 of 8 KILLED; X00 SURVIVED; R03 SURVIVED (equivalent on the fixture)
busy.ps1 -> 1 ; python tools/analysis/adaptive_profile.py --dry-run --data-root <main>   # rc 0, 66 lines (E:/TaxoArena_tmp/rev_ap/ap_dry.log)
sha256sum gen_view_REG.db eval_view_REG.db (before / after all three dry-runs)    # EQUAL
git show 7279bf43:<path> | grep -c "DECLARED DEVIATION" ; grep -c "D-2026-10-09-1"     # 0 ; 1 (docstring)
```
