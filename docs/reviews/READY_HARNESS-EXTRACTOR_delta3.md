# DELTA READY review 3: HARNESS-EXTRACTOR, delta 3 (D-3 / T-1; registrar S-1 and ruling F-H-SUPPORT), adversarial reviewer, 2026-10-09

Reviewed: `git diff 70dd5a83..215bcfcb` on branch `hx-r4` (worktree `.claude/worktrees/hx-r4`): 1 file
(`git diff --name-only 70dd5a83 215bcfcb | wc -l` = 1), tools/analysis/harness_extractor.py +184 / -21; parent of 215bcfcb = 70dd5a83;
worktree `status --porcelain | wc -l` = 0.
Blob: blob:a7ebea9f368056a631085f61bde410ee05efbf1a (`rev-parse` = `hash-object`), sha256-lf16:5309823ce516e62c (LF, of record); the
worktree holds the CRLF rendering, sha256-crlf16:07514ba69955a46c. Code outside the delta is cited from READY_HARNESS-EXTRACTOR.md,
_delta.md and _delta2.md (69032fdb; B-2 CONFIRMED there). Authority: prog L25412-L25418 (78f9bc2e). Zero calls.

## VERDICT: READY (conditions L-H1, L-H2 LOW and L-A carried; none blocks the run)

## Per-claim table (deciding claims only)
| # | claim (builder) | reviewer's evidence | status | sev |
|---|---|---|---|---|
| 1 | SUPPORT_PLAN = S-1 (d)-(f) | code rows: HX1 0.0420 / 0.118, HX2 0.0420 / 0.118, HX3 0.0658 / 0.184, HX4 0.0095 / 0.027, HX5 0.0072 / 0.020; own: 0.03374 x sqrt(2,056/1,324) = 0.04204 (x2.8 0.1177); x sqrt(2,056/541) = 0.06577 (x2.8 0.1842); sqrt(0.099/1,324) x sqrt(1.2) = 0.00947; 2.8 x 0.0095 = 0.0266; 2.8 x 0.0072 = 0.0202; floor 2.8 x 0.0337 = 0.0944 | CONFIRMED (to the digit) | - |
| 2 | Plan words computed, not typed | `plan_word`: SCOREABLE iff \|pred - bar\| >= MDE80: HX1 0.50 >= 0.118 S; HX2 0.07 < 0.118 "DESCRIPTIVE-ONLY (by support)"; HX3 0.03 < 0.184 D; HX4 0.079 >= 0.027 S; HX5 0.40 >= 0.020 S = record (f) | CONFIRMED | - |
| 3 | DEFF / n_eff fields for HX1-HX3 | printed "carried by the transported realised SD" / "not entering" = the registrar's DEFF note (L25415); HX4 1.2 / 1,103, HX5 3.0 / 1,727 unchanged | CONFIRMED | - |
| 4 | HX2 word and F-H qualified; F-H decides nothing | HX2 line "-> %s (descriptive-only by support)"; F-H lines "FALSIFIER F-H (descriptive-only by support; decides nothing): ..." both ways | CONFIRMED | - |
| 5 | New "FALSIFIER OF RECORD" line (beyond the brief) | `fired = h1["word"] == "RANKS-HOLD"` = F-HX's registered rule (L109 "F-HX fires iff HX1 reads RANKS-HOLD") and = the existing F-HX branch; F-H not read. It is the printed form of the ruling's "F-H takes no part"; no other aggregate exists (no `fired` field in the figure JSON or elsewhere). Accepted | CONFIRMED | - |
| 6 | T-1: H03 / H04 die | own: H01 H03 H04 KILLED; pure / verdicts fixtures: non-first pair tau-b 0.7647 at shift 2, NaN pair at shift 0.5; rule8 == (word == RANKS-HOLD) | CONFIRMED | - |
| 7 | X15 dies on run_e2e alone ("shift2" fixture) | own (builder's helper, E:/TaxoArena_tmp/hx_e2e_only.py, on the sandbox copy): X00 SURVIVED; X02, X13, X15 "KILLED by run_e2e only" | CONFIRMED | - |
| 8 | Selftest 9 / 9 | own on `git archive 215bcfcb` (E:/TaxoArena_tmp/rev_hx3): "[HX] selftest: 9 / 9 passed", rc 0 | CONFIRMED | - |
| 9 | Mutants (regression + D-3) | own: X00 SURVIVED; X02 X13 X15 X83 X84 H01 H03 H04 X85-X98 KILLED (22 of 22 builder rows run) | CONFIRMED (subset of 101) | - |
| 10 | Real --dry-run; nothing written | own (busy.ps1 rc 1, from the worktree): rc 0, 39 lines, "POOL paeec37aa28063c75 verified" first; rule-7 line exit 1 with the own-chain PIDs; `grep -c "^HX\|RULE 8\|PREDICTION\|FALSIF"` = 0; multicorpus_cache_v1.db ad66e30a0eb4abd6 and checker_answers_v2.db 6cfaf74d647829d1 EQUAL before / after (the -wal is 0 bytes) | CONFIRMED | - |

## Own mutants (sandbox E:/TaxoArena_tmp/rev_hx3, appended to MUTANTS)
- H05 plan word judged against SE instead of MDE80 (HX2 would read SCOREABLE): KILLED (decisive: the support word).
- H06 falsifier of record requires HX1 stable (S_w gate added): KILLED (decisive: the POINT decides, not S_w).
- H07 HX2 planned point 0.98 (margin clears MDE80): KILLED (decisive: the word is value-checked, not only computed).
Result line: "[HX] mutants: 25 of 25 KILLED; control SURVIVED; survivors none; not applied none".

## Defects and conditions (LOW; builder, optional; if not fixed, read as disclosed by the POSTRUN review and the post)
- **L-H1.** The blog figure JSON (`figure_payload` "words") carries the HX2 and HX3 words bare, without "(descriptive-only by support)".
  The ruling allows the post's "two careful scorers agree" headline only with that qualifier (L25417). Fix: emit e.g.
  `HX2=dict(word=..., support="descriptive-only by support")` (and HX3 alike). Not deciding; the outcome file is qualified.
- **L-H2.** The "RULE 8 (HX2, HX-R5)" line prints "... is not refuted" for a DESCRIPTIVE-ONLY word without the qualifier. Fix: append
  "(descriptive-only by support)". Not deciding.
- **L-A (carried).** Launch directly, not through a wrapper whose command line matches busy.ps1.
- **Branch.** `hx-r4` has diverged from main (docs only moved on main): merge, do not rebase-rewrite; re-check the blob after the merge.

## Run commands (from the worktree `.claude/worktrees/hx-r4`, blob a7ebea9f, or main after a merge that keeps the blob; launch directly)
```
powershell -NoProfile -File E:/TaxoArena_tmp/busy.ps1                        # must exit 1
python tools/analysis/scratch_dir.py --run -- python tools/analysis/harness_extractor.py --selftest      # 9 / 9
python tools/analysis/harness_extractor.py --dry-run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena       # rc 0, 39 lines
python tools/analysis/harness_extractor.py --run     --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena
# back up outcome + figure json to E:/TaxoArena_backup_<date>_harness_extractor with SHA256SUMS; never commit
```

## Commands (read-only; zero calls)
```
git diff --name-only 70dd5a83 215bcfcb | wc -l ; git log -1 --format=%P 215bcfcb       # 1 ; 70dd5a83
git rev-parse 215bcfcb:<path> ; git hash-object <wt path>                               # a7ebea9f both
git show 215bcfcb:<path> | sha256sum ; | sed 's/$/\r/' | sha256sum ; sha256sum <wt>     # 5309823ce516e62c ; 07514ba69955a46c ; 07514ba69955a46c
git archive 215bcfcb -- . ':!*.db' ':!*.npz' ':!report' | tar -x -C E:/TaxoArena_tmp/rev_hx3     # + H05-H07
scratch_dir.py --run -- python tools/analysis/harness_extractor.py --selftest           # 9 / 9
scratch_dir.py --run -- python tools/analysis/harness_extractor.py --mutants --only X00 X13 X15 X83 X84 H01 H03 H04 X85 ... X98 X02 H05 H06 H07
   # 25 of 25 KILLED; control SURVIVED (rev_hx3/mut.log)
(cd tools/analysis) scratch_dir.py --run -- python E:/TaxoArena_tmp/hx_e2e_only.py      # X02 X13 X15 KILLED by run_e2e only; X00 SURVIVED
busy.ps1 -> 1 ; (worktree) python tools/analysis/harness_extractor.py --dry-run --data-root <main>   # rc 0, 39 lines (rev_hx3/hx_dry.log)
sha256sum multicorpus_cache_v1.db experiment_results/multicorpus/checker_answers_v2.db (before / after)   # EQUAL
python: 0.03374*sqrt(2056/1324)=.04204 (x2.8 .1177); *sqrt(2056/541)=.06577 (x2.8 .1842); sqrt(.099/1324)*sqrt(1.2)=.00947; 2.8*.0337=.0944
```
