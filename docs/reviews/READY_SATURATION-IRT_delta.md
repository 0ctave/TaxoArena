# DELTA READY review: SATURATION-IRT (HF post 1), after B1

Reviewed: `git diff f2fbb6d5..da50fe86` on branch `worktree-wf_42805bc7-f2d-3` (tip da50fe86; `merge-base --is-ancestor d999e689 da50fe86` OK).
The diff touches 1 file: `tools/analysis/saturation_irt.py`, +58 / -5 (`git diff --stat`, and `--name-only | wc -l` = 1). The worktree is clean.
Blob: blob:077eaf0056b29834e8887d30d3c187a4af25d0ba (`git hash-object`; LF; `grep -c $'\r'` = 0) / sha256-lf16:f66f2a15b1d367fa /
sha256-crlf16:aa11c1f900c43366, as the dry-run prints them. Prior full review: `docs/reviews/READY_SATURATION-IRT.md` (0cd7fb5e).
Claims 1-4 and 6-17 of that review are CONFIRMED on code that this delta does not touch; they are cited, not re-derived.

## VERDICT: READY (blob 077eaf00), conditions C1-C2 below. B1 is fixed.

## Per-claim table (deciding claims only)

| # | claim | reviewer's evidence | status | sev |
|---|---|---|---|---|
| 1 | Data keyed on `MMLU_PRO`. `MMLU_PRO_LB` remains only as a display word | Whole-file grep finds 14 `MMLU_PRO_LB` hits. Above the SELFTEST marker they are only: docstring L71/L73/L90/L125, and the print strings L663 / L690 / L697 (SI2 / P3 / P4). Code keys: L198 `SOURCES`, L199 `MMLU` = `MMLU_PRO`. Fixture `_spec` L1262 / L1277 moved to `MMLU_PRO` | CONFIRMED | - |
| 2 | The real `--dry-run` passes REFUSE.SOURCES and prints the prior review's numbers | Run by me (busy.ps1 exit 1 first). R1 471 / 427 (MMLU_PRO 179, BBH 2, MATH 2, GPQA 288). 589 collapsed (MMLU_PRO 216, MATH 13, GPQA 358, BBH 2). Kept 11,637 / 5,757 / 1,309 / 756 / 546 / 541 = 20,546. k_b 1,164 / 576 / 131 / 76 / 55 / 54. Pool 5,642 / 6,153. Roster 18; Llama-3-70B ACTIVE False. Rows 272,520 / 116,388. Last line "DRY-RUN: no key column was selected". Every number matches the prior review to the digit | CONFIRMED | - |
| 3 | Read-only | multicorpus sha256 ad66e30a0eb4abd6 before and after (my sha256sum, and the script's own BEFORE / AFTER line). gen_view c2930c60 and eval_view e35b7518 EQUAL to before. The output dir `experiment_results/hf_blog/saturation_irt` and `E:/TaxoArena_tmp/blog/irt` do not exist after the run (`ls`: no such file) | CONFIRMED | - |
| 4 | Selftest 15/15, including `labels` | Re-run in the scratch sandbox: 15 / 15 passed (labels 0.7 s) | CONFIRMED | - |
| 5 | Mutants 73/73 killed; X00 survives | Re-run: `grep -c 'KILLED ('` = 73. `grep SURVIVED` gives 2 lines: X00 and the summary line. NOT APPLIED = 0. Summary: "73 of 73 KILLED; control SURVIVED; survivors none" | CONFIRMED | - |
| 6 | `labels` is independent of SOURCES | `REAL_DB_LABELS` is a literal below the marker, so mutants (which edit above it) cannot move it. My Z3 (the original B1 state: SOURCES and MMLU both `_LB`, so fixtures and code agree with each other) is KILLED, so the test now sees the class it missed | CONFIRMED | - |

Reviewer's mutants (sandbox; control X00 SURVIVED; 5 of 5 KILLED):
- Y2: top 4 by micro, not macro. KILLED. Decisive (prior review, re-run as regression).
- Y4: k_b by floor, not half-up. KILLED. Decisive (prior review, re-run as regression).
- Z1: SOURCES order swapped (MMLU_PRO <-> BBH; changes the [R-e] bootstrap draw order). KILLED. Decisive for the seed of record.
- Z2: source refusal by count only (`len(srcs) != len(SOURCES)`; a wrong label passes). KILLED. Decisive: this is the B1 class.
- Z3: the original B1 state (both constants `_LB`). KILLED. Decisive.

## Defects / conditions
- **C1 (= prior D2, MEDIUM, operator).** busy.ps1's pattern still does not include `saturation_irt`; the regex in
  `E:/TaxoArena_tmp/busy.ps1` was read whole. For the 2-2.5 h run window, add it to the pattern, or the orchestrator rules that the
  one-thread overlap is acceptable. Launch only on exit 1. At the start of this review busy.ps1 exited 0 (gap_fix_cc.py --run was
  live). The dry-run was run only after it exited 1.
- **C2 (= prior D3, LOW).** The COST line still prints "CPU about 3.5-4.5 h" (confirmed in my dry-run), while the docstring says
  2-2.5 h. This does not decide anything, because the pilot re-times the run. Make them agree when convenient.
- Prior D4 (items JSON release label), D5 (registrar: P5 vacuous) and D6 (print the cross-source collapse count) are still open,
  all LOW, none blocking. D6 is visible in the dry-run: MATH 13 dropped, the 13 cross-source groups.
- No new defects in the delta.

## Commands (read-only; busy.ps1 exit 1 checked before the DB read)
```
W=.claude/worktrees/wf_42805bc7-f2d-3
git -C $W diff f2fbb6d5..da50fe86 --name-only | wc -l          # 1
git -C $W hash-object tools/analysis/saturation_irt.py          # 077eaf00...
git -C $W merge-base --is-ancestor d999e689 da50fe86            # OK
grep -n 'MMLU_PRO' $W/tools/analysis/saturation_irt.py           # display-only _LB above marker
python tools/analysis/scratch_dir.py --run -- python tools/analysis/saturation_irt.py --selftest   # 15/15
python tools/analysis/scratch_dir.py --run -- python tools/analysis/saturation_irt.py --mutants    # 73/73, X00 survived
python tools/analysis/scratch_dir.py --run -- python E:/TaxoArena_tmp/rev_satirt_delta/my_mut.py  # Y2 Y4 Z1 Z2 Z3 killed
powershell -NoProfile -File E:/TaxoArena_tmp/busy.ps1           # 0 at start (gap_fix_cc --run), 1 before the dry-run
sha256sum multicorpus_cache_v1.db                               # ad66e30a0eb4abd6 before / after
python tools/analysis/saturation_irt.py --dry-run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena    # rc 0, lines above
```

## Run command (operator; from the worktree, or from main after the merge without --data-root)
```
powershell -NoProfile -File E:/TaxoArena_tmp/busy.ps1   # must exit 1 (C1)
python tools/analysis/saturation_irt.py --pilot 3 --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena
python tools/analysis/saturation_irt.py --run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena   # back up outputs to E:/TaxoArena_backup_<date>_saturation_irt
```
