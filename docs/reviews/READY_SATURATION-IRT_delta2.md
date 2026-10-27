# DELTA READY review 2: SATURATION-IRT, the D-2026-10-08-5 scorer delta

Reviewed: `git diff da50fe86..04b1e5aa -- tools/analysis/saturation_irt.py` (+308 / -32), branch `worktree-wf_d795fd62-e28-5`,
tip 04b1e5aa (one commit on main 62d269af; `merge-base --is-ancestor 62d269af 04b1e5aa` OK; `git diff --name-only 62d269af 04b1e5aa | wc -l` = 1).
Blob: blob:436f57f550f15ddf0933d157be9154dce843d72a (`git hash-object` = `git rev-parse 04b1e5aa:<path>`; LF, `grep -c $'\r'` = 0),
sha256-lf16:34be9e5d2d830c79 (= the builder's), sha256-crlf16:f9a06fcbe1c94b79. Replaces READY blob:077eaf00.
Prior reviews: `READY_SATURATION-IRT.md` (0cd7fb5e), `READY_SATURATION-IRT_delta.md`; claims there on untouched code are cited, not re-derived.
Authority: D-2026-10-08-5 (docs/agents/author_decisions/2026-10-08.md, 5211616a); deviations (1)-(4), prog L25322 as of bb5eb124.

## VERDICT: NOT READY / BLOCKED (B1, B2). The scorer change itself is CONFIRMED.

## Per-claim table (deciding claims only)

| # | claim | reviewer's evidence | status | sev |
|---|---|---|---|---|
| 1 | MATH scored by the official `is_correct`, no MATH-FIX overlay | The key SELECT is now `model, legacy_qid, source, is_correct` and `K[q][m] = int(c)`. Above the SELFTEST marker, `mathfix` occurs only at L19/L41/L48/L1151, all docstring or comment (my count). `ingest._union_responses` L141-L146: `is_correct` = `eval_results.is_correct`, mathfix a separate column. X32 (COALESCE overlay) KILLED; my R1 (MATH-only CASE overlay in the SQL) KILLED | CONFIRMED | - |
| 2 | H table pinned; refuses on any other sha before the pool read | Real CSV (my script): sha256 6b010fa60dde727816b91196d2cb3045094082c3800fe738adebe21d19eeb1d1 = `H_SHA` (full hex); CR 0; header `question_id,model,H,route`; 23,832 rows; 1,324 qids x 18 models (1,324 each); H 1 = 7,126; imported = 2,335; imported with H 0 = 0; dup 0. On the real `--dry-run`, `load_h` ran first and passed: the refusal came from the busy check that follows it, not from HSHA. X74-X77 KILLED | CONFIRMED | - |
| 3 | Scorer header line = deviation (1), verbatim | `scorer_line` text = the L25322 wording with `MATH-FIX beside: no`. Selftest asserts it is line 3 of the outcome file and of the dry-run. X84 and X85 KILLED | CONFIRMED | - |
| 4 | H lines are descriptive (deviation (4)) | `h_lines` output is placed after SUPPORT. No verdict or prediction function reads `hl` (code read of `run`: `vl` is computed before `h_lines`) | CONFIRMED | - |
| 5 | Selftest 16/16 | Re-run in a scratch sandbox: 16 / 16 (run_e2e 36 s, hrefusals 5.9 s) | CONFIRMED | - |
| 6 | Mutants 93/93 KILLED; X00 survives | Re-run in 10 chunks (`--only X0..X9`): `grep -c 'KILLED ('` = 93; SURVIVED only X00; NOT APPLIED none | CONFIRMED | - |
| 7 | Regression: the prior review's decisive mutants still die | Y4 (k_b by floor) KILLED. **Y2 (top 4 ranked by micro instead of macro; decisive for SI2 / SAT4) SURVIVES at 436f57f5.** At 077eaf00 it is KILLED by `run_e2e` (same harness, archive of da50fe86) | REFUTED | BLOCKER (B1) |
| 8 | Real `--dry-run` runs read-only | It cannot run. With busy.ps1 = 1 in my shell, the script's own check refused 400+ consecutive times (01:29-02:00). The cause is deterministic: busy.ps1 (mtime 2026-10-08 16:27) matches `saturation_irt` in python command lines, which includes the script's own process. Proof: a python process with `saturation_irt` in argv gets busy.ps1 rc 0; the control gets rc 1; plain busy.ps1 gives 1 both before and after. The multicorpus sha ad66e30a0eb4abd6 is EQUAL before and after, and no output dir exists | REFUTED (not executable) | BLOCKER (B2) |

Reviewer's mutants (sandbox; control X00 SURVIVED):
- R1: MATH-only overlay `CASE WHEN source='MATH' AND is_correct_mathfix IS NOT NULL ...` in the SQL. KILLED. Decisive (D-5).
- R2: SAT4_H read on the official MATH matrix. KILLED. Not decisive (descriptive line).
- R3: consistency check keeps only the route half (drops `off == 1 and hv != 1`). KILLED. Not decisive.
- R4: the `H_SHA` constant changed by one hex digit. SURVIVES the selftest, because the fixtures carry their own sha. The real dry-run guards it (claim 2). LOW L-2.
- Y2 / Y4: regression of the prior decisive mutants (claim 7).

## Defects

- **B1 BLOCKER (test power lost on a SCORED criterion's population).** The old oracle keyed MATH by MATH-FIX, so macro and micro top-4
  differed on a fixture. Keyed by the official verdict, the macro and micro top-4 coincide on all three e2e fixtures (strong / struct /
  noise). "Top 4 by macro" (theta_top4, used by SI2 NEFF and SAT4) is therefore no longer guarded. The code at L796 is unchanged and
  correct, but the suite no longer sees this mutant class. Fix: make at least one fixture's micro top-4 SET differ from its macro top-4
  (unequal N per source and one model strong on the large source only), assert that inequality in run_e2e as `moved` does for H, add Y2
  as an X mutant (X94) and show it KILLED.
- **B2 BLOCKER (operational; environment interaction).** `busy_check` runs busy.ps1, whose pattern now lists `saturation_irt` (this was the prior
  C1's request), so the script always sees itself and refuses with REFUSE.BUSY. That holds in `--dry-run`, `--pilot` and `--run`.
  Fix (builder; keep fail-closed): exclude the script's own PID and its parent chain from the check. For example, pass `-ExcludePid
  <os.getpid()>` through a busy.ps1 parameter (a programme-level change to busy.ps1, which is not this branch's file), or do an
  in-script process scan with the same pattern minus its own PID and ancestors. Add a selftest: the real busy.ps1 invoked from a process
  named `saturation_irt` must return free when nothing else runs. I did not bypass the guard. Other scripts in busy.ps1's list
  that call busy.ps1 on themselves (win_map, cert_split_dip, gap_fix, ...) should be checked for the same self-match.
- **C1 CONDITION (deviation (2)).** No registrar's record pins 6b010fa6 yet (`git grep -c 6b010fa6 docs/judge_v2_program.md` = 0 at
  9af2c14a). The `--pilot` ALSO prints the SENSITIVITY H lines (`run` builds `hl` for the pilot as well). So neither `--pilot` nor
  `--run` may start before that record, not only `--run`.
- **C2 CONDITION.** The H/views consistency check (`h_benches`: route imported iff official 1) first executes on real data at the
  H line. In `--run` that comes after the full bootstrap (about 3.5-4.5 h). The pilot exercises it first, so the pilot is mandatory before
  `--run`, and a REFUSE.HTABLE in the pilot stops the line.
- **L-1 LOW.** The docstring at L41/L44 still reads "MATH-FIX overlay ... MATH-FIX for MATH". The DELTA bracket at L45 supersedes it;
  keep both, but add "[superseded by the DELTA below]" inline.
- **L-2 LOW.** R4: the pinned `H_SHA` is not asserted by any selftest. Add a literal below the SELFTEST marker (as REAL_DB_LABELS does)
  and assert `H_SHA ==` that literal.
- **L-3 LOW.** The tolerance change `< 5e-5` to `<= 5.0001e-5` is test-only and acceptable (it rounds the printed 4-dp value).

## Commands (read-only; busy.ps1 checked before every pool-touching step; zero calls)
```
git diff --name-only 62d269af 04b1e5aa | wc -l                       # 1
git hash-object .claude/worktrees/wf_d795fd62-e28-5/tools/analysis/saturation_irt.py   # 436f57f5...
git show 04b1e5aa:tools/analysis/saturation_irt.py | sha256sum        # 34be9e5d2d830c79 ; | sed 's/$/\r/' -> f9a06fcbe1c94b79
python tools/analysis/scratch_dir.py --run -- python tools/analysis/saturation_irt.py --selftest            # 16/16 (worktree)
for p in X0..X9: scratch_dir.py --run -- python tools/analysis/saturation_irt.py --mutants --only $p      # 93 KILLED, X00 SURVIVED
scratch_dir.py --run -- python E:/TaxoArena_tmp/rev_irt/own_mut.py      # R1-R3 KILLED, R4 SURVIVED
scratch_dir.py --run -- python E:/TaxoArena_tmp/rev_irt/prior_mut.py    # new blob: Y2 SURVIVED, Y4 KILLED
(git archive da50fe86 -> E:/TaxoArena_tmp/rev_irt/old) prior_mut_old.py; y2trace.py  # old blob: Y2 KILLED in run_e2e; new: run_e2e ok
python - (CSV read) experiment_results/math_scorer_h/math_h_table.csv  # sha = H_SHA; 23,832 / 1,324 x 18 / H 7,126 / imported 2,335
E:/TaxoArena_tmp/rev_irt/dry.sh, dry2.sh  # busy.ps1 rc 1 -> --dry-run --data-root Z:/... -> "REFUSED: rule 7 ... exited 0" (400+ times)
python -c "subprocess.run(['powershell','-NoProfile','-File',busy.ps1])" saturation_irt  # rc 0 ; same with other_name -> rc 1
sha256sum multicorpus_cache_v1.db  before/after                       # ad66e30a0eb4abd6 EQUAL
```

## Run commands (after B1 and B2 are fixed, a delta READY on the new blob, and the registrar's H-pin record; operator; busy.ps1 = 1 first)
```
python tools/analysis/scratch_dir.py --run -- python tools/analysis/saturation_irt.py --selftest
python tools/analysis/saturation_irt.py --dry-run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena
python tools/analysis/saturation_irt.py --pilot 3 --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena   # only after the H-pin record (C1)
python tools/analysis/saturation_irt.py --run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena       # detached + Monitor; after the pilot (C2)
```
