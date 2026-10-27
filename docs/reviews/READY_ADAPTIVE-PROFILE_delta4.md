# DELTA READY review 4: ADAPTIVE-PROFILE, the B-1 / L-1 fix (READY_ADAPTIVE-PROFILE_delta3), adversarial reviewer, 2026-10-09

Reviewed: `git diff 7279bf43..ab7448c3` on branch `ap-denom-fix` (worktree `.claude/worktrees/ap-denom-fix`): 1 file
(`git diff --name-only 7279bf43 ab7448c3 | wc -l` = 1), tools/analysis/adaptive_profile.py +52 / -1; parent of ab7448c3 = 7279bf43.
Blob: blob:f23193bb808cefe74642ce8fd400d67ff9335d74 (`git rev-parse` = `git hash-object <wt path>`), sha256-lf16:8d35e9db59c4fed4 (LF, of
record); the worktree holds the CRLF rendering, sha256-crlf16:abc5409efd486631 (= the LF blob with CR added); `status --porcelain | wc -l` = 0.
Code outside the delta (R-1..R-4) is cited from READY_ADAPTIVE-PROFILE_delta3.md (CONFIRMED there), not re-derived.
Authority: D-2026-10-09-1 (defab40c), prog L25394-L25401 (edb060b9). Zero calls.

## VERDICT: READY (one LOW condition, test harness only; does not block the marker clearance or --run)
B-1 is CLOSED: `run()` prints the registrar's L25397 line verbatim into `lines` (hence into the write-once outcome file) right after
`U.header`, followed by its authority line; the dry-run shows it prefixed. L-1 is CLOSED (X114 = R03 killed).

## Per-claim table (deciding claims only)
| # | claim (builder) | reviewer's evidence | status | sev |
|---|---|---|---|---|
| 1 | Deviation line verbatim = prog L25397 | code L333 `DEVIATION_LINE` byte-equal to the quoted text in L25397; authority shas checked: defab40c = first commit of author_decisions/2026-10-09.md; 980c3982:adaptive_profile.py = aff80c1d; edb060b9 = the recording commit | CONFIRMED | - |
| 2 | It enters the write-once outcome file as a header line | `say(DEVIATION_LINE)` / `say(DEVIATION_AUTH)` follow `U.header(say, ...)` in run() (L1532-1533); `say` appends to `lines`; both precede the write-once existence check, load_h, DENOMINATORS and any read | CONFIRMED | - |
| 3 | Selftest asserts it from a literal, by bytes, in position | run_e2e: `DEV_TEXT` literal; `raw.splitlines().count(...) == 1`; previous line `  threads: `; before the scorer line and DENOMINATORS; authority line by value; dry_run: prefixed form after threads, bare form absent | CONFIRMED | - |
| 4 | Selftest 13 / 13 on the commit blob | own run on a `git archive ab7448c3` copy (E:/TaxoArena_tmp/rev_ap3c): "[AP] selftest: 13 / 13 passed", rc 0 | CONFIRMED | - |
| 5 | Mutants 114 / 114 KILLED | own on a sandbox of the commit blob: X00 SURVIVED; X61 X62 X99 X108 X110 X111 X112 X113 X114 KILLED; **X109 NOT APPLIED (2 matches)**: its target `of 2026-10-09 (aff80c1d)"` also occurs in the DELTA 2026-10-09c docstring (L247), added AFTER the table ran on blob 8ce1b1cb. On the commit blob the full table exits 1 | PARTLY | LOW (L-A1) |
| 6 | The behaviour X109 targets is tested | own R06 = X109 re-targeted on the constant's whole assignment (wrong sha 7279bf43): KILLED | CONFIRMED | - |
| 7 | Real --dry-run | own (busy.ps1 rc 1, from the worktree): rc 0, 67 lines, POOL pv2_1575de61bb20e977 first; line 14 "DEVIATION HEADER (printed by --run into the outcome file, verbatim): DECLARED DEVIATION D-2026-10-09-1: ... (aff80c1d)"; "TRAIN DENOMINATOR ...: 11841 items / 10781 components (registered 11841 / 10781)"; eval view "NOT opened by --dry-run" | CONFIRMED (to the digit) | - |
| 8 | Nothing written; views and marker unchanged | gen view c2930c609c67d6c7, eval view e35b751887820583: sha256 before = after; `find experiment_results/archv2/adaptive_profile -type f \| wc -l` = 1 (the incident marker) before and after | CONFIRMED | - |
| 9 | L-1: non-ACTIVE fixture model | build_base appends ("mc6", V.EXCLUDED, "EXCLUDED") after asserting none was present; X114 (= R03) KILLED | CONFIRMED | - |

## Own mutants (sandbox E:/TaxoArena_tmp/rev_ap3 = git archive ab7448c3 + rows appended below the SELFTEST marker)
- R04 deviation line with a trailing space (not verbatim): KILLED (decisive: the whole-line byte check).
- R05 deviation lines moved after load_h (after the scorer / H lines; still in the file): KILLED (decisive: header position).
- R06 X109 re-targeted on the constant only (wrong attempt sha): KILLED (decisive: the literal is independent of the constant).

## Defects and conditions
- **L-A1 LOW (builder, test harness only).** X109's target string matches twice above the SELFTEST marker on the commit blob (the
  docstring quotes it), so `--mutants` on f23193bb reports "NOT APPLIED" and exits 1. Re-target X109 on the whole assignment
  `DEVIATION_LINE = "DECLARED DEVIATION ... (aff80c1d)"` (as R06). The run is not affected: R06 shows the wrong-sha case dies. If
  fixed, the change sits below the marker only (the MUTANTS table): re-pin the blob; no further review owed.
- **Operator (unchanged from the record).** Clear the marker `experiment_results/archv2/adaptive_profile/adaptive_profile.READ_STARTED`
  by path, after this READY is committed and busy.ps1 exits 1; its copy is in E:/TaxoArena_backup_20261009_adaptive_profile_incident;
  log the clearance (D-2026-10-09-1). The outcome section of record must also carry the deviation line (L25397; the registrar's).

## Run commands (from the worktree `.claude/worktrees/ap-denom-fix`, blob f23193bb, or main after a merge that keeps the blob; launch directly)
```
powershell -NoProfile -File E:/TaxoArena_tmp/busy.ps1                      # must exit 1
python tools/analysis/scratch_dir.py --run -- python tools/analysis/adaptive_profile.py --selftest        # 13 / 13
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 python tools/analysis/adaptive_profile.py --dry-run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena
   # rc 0, 67 lines; DEVIATION HEADER line; TRAIN 11841 / 10781
# operator: clear the marker by path (logged), busy.ps1 again -> 1, then:
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 python tools/analysis/adaptive_profile.py --run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena
# check: the outcome file's 2nd header block line is "DECLARED DEVIATION D-2026-10-09-1: ..."; back up outcome + export to
# E:/TaxoArena_backup_<date>_adaptive_profile with SHA256SUMS; never commit
```

## Commands (read-only; zero calls)
```
git diff --name-only 7279bf43 ab7448c3 | wc -l ; git log -1 --format=%P ab7448c3                 # 1 ; 7279bf43
git rev-parse ab7448c3:tools/analysis/adaptive_profile.py ; git hash-object <wt path>            # f23193bb both
git show ab7448c3:<path> | sha256sum ; | sed 's/$/\r/' | sha256sum ; sha256sum <wt path>         # 8d35e9db59c4fed4 ; abc5409efd486631 ; abc5409efd486631
git show ab7448c3:<path> | awk '/^# ══ SELFTEST/{exit} {print}' | grep -c 'of 2026-10-09 (aff80c1d)"'   # 2 (L247 docstring, L333)
git log --format=%h -- docs/agents/author_decisions/2026-10-09.md | tail -1 ; git rev-parse 980c3982:<path>   # defab40c ; aff80c1d
git archive ab7448c3 -- . ':!*.db' ':!*.npz' ':!report' | tar -x -C E:/TaxoArena_tmp/rev_ap3c   # commit blob as is
scratch_dir.py --run -- python tools/analysis/adaptive_profile.py --selftest                      # 13 / 13 (rev_ap3c)
scratch_dir.py --run -- python tools/analysis/adaptive_profile.py --mutants --only X00 X61 X62 X108 X109   (rev_ap3, + R04-R06)
   # X00 SURVIVED; X61 X62 X108 KILLED; X109 NOT APPLIED (2 matches)
   --only X110 X111 X112 | X113 X114 X99 | R04 R05 R06                                           # 9 of 9 KILLED (3 partitions)
busy.ps1 -> 1 ; (worktree) python tools/analysis/adaptive_profile.py --dry-run --data-root <main>    # rc 0, 67 lines (rev_ap3/ap_dry.log)
sha256sum data_v2/REG_ARCHV2-SPLIT-2_*/{gen,eval}_view_REG.db (before / after)                   # EQUAL
find experiment_results/archv2/adaptive_profile -type f | wc -l (before / after)                 # 1 / 1
```
