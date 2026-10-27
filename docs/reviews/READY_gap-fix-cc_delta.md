# Delta READY review: GAP-FIX-CC builder delta (ruling P-1, P-2, P-3, C-2)

Reviewed: `git diff 6098f22f..886b81c7` (branch `worktree-wf_11776b0c-a8a-3`). The commit touches 1 file
(`git show 886b81c7 --name-only --format= | wc -l` = 1), which is `tools/analysis/gap_fix_cc.py`, going from blob:b83d2790 to
**blob:41aa53aa** (sha256-lf16:42099acec10bf68a; the working tree is LF, so the CRLF rendering sha256-crlf16:a1f70a13837b2f53
is printed by the tool only). `gap_fix.py` stays blob:7c0691e8 and `flat_mix_mmlu.py` stays blob:555ae3ac; neither is touched.
Prior reviews: READY 3968447d, POSTRUN 443cf9ff. What they CONFIRMED on code this delta does not touch is cited, not re-derived:
Support (SE 0.00630, MDE80 0.0176, DEFF 1.0 from GAP-FIX PR-1), I-2, hygiene and the nomic gate. Ruling of record: prog
L25212-L25219 (P-1 option (b)). Zero calls, read-only.

## Verdict

**READY** (no blocker). Conditions:
- **D-1 (LOW, registrar, record only):** the declarations to bracket are B-7 (the VOID class) and B-8 (VOID-TREE scoring),
  plus D-2 and D-3 below. None of them can change today's outcome, because the real dry-run shows no VOID-TREE and exactly one
  replacement.
- **Run (after the registrar merges blob:41aa53aa by path):** first `busy.ps1` must exit 1. The run is then the command in the
  block below. `experiment_results/gap_fix_cc/` is absent today, so the write-once guard does not trip.

## Per-claim table (deciding paths)

| # | claim | result | mine vs claimed | sev |
|---|---|---|---|---|
| 1 | P-1 rule as ruled: slot j starts at seed j; a B6-VOID seed is replaced in its slot by the lowest unused seed of 5..9; the replacement is printed; 5..9 exhausted gives VOID-TREE, which drops out | CONFIRMED | `fit_v_rule` L405-L430 by reading. The C-VSEED orders are checked by value (0 -> 5; 0+5 -> 6; 0+5+2 -> 6, 7; V3 -> 5; V1+V3 -> 5, 6; 4+5..8 -> 9; 0+5..9 -> VOID-TREE; a non-B6 refusal stops the run). The ruling's required mutant ("any seed other than the next unused one") is V01 / V02 / V03, all KILLED | - |
| 2 | real data: only Q_e1sd2 V0 changes (seed 0 -> seed 5); the other 34 fits stay unchanged | CONFIRMED | real `--dry-run`: `VFIT Q_e1sd2 V0: seed 0 B6-VOID -> seed 5 OK REPLACED (ruling P-1)` (converged True, iters 182). All other 34 VFIT lines are `seed j B6 OK` with j = slot. Summary: `35 slots fitted, 1 by a ruling P-1 replacement; VOID-TREE 0`. 35 VFIT lines counted (`grep -c '^VFIT '`) | - |
| 3 | P-2: the dry-run fits V0-V4 on the real fit sets, label-free, and writes nothing | CONFIRMED | the dry-run log prints 35 VFIT lines and `zero measures, nothing written`; no M1, GF1 or D_T line. A size+mtime list of the 413 *.db / -wal / -journal files under main (maxdepth 4) taken before and after is identical (`diff` empty) | - |
| 4 | P-3: every refusal names the tree | CONFIRMED | `named()` wraps the guard path (admit), run_core's per-tree loop and dry_core's structure and V-fit loops. Tests p3a-p3d cover --run and --dry-run. V14, V15 and V16 are KILLED | - |
| 5 | C-2: R2 and R5 tests | CONFIRMED | C-RENDER checks R2 by value (a NO-GAP CLOSED tree with LB <= 0 gives `2 of 2`, FIRES) and R5 in both directions. The prior review's mutants R2 and R5 are both KILLED | - |
| 6 | VOID-TREE is not GAP-SHOWN, NOT SCORED in P2/P3, outside P5; GF1-CC words unchanged | CONFIRMED | `leg_rows` sets gap=False; `aggregate` and `closed_refuted` filter on gap; P5 uses `live`. V10, V11 and V12 are KILLED. The run path is exercised end to end in C-E2E-VOID (b): the run completes, MIXED on the other two, and the arms CSV holds 6 trees | - |
| 7 | inertness without a VOID: exactly seeds 0-4 are tried | CONFIRMED | C-VSEED `log == [0,1,2,3,4]`, plus the real fitter on a regular set. On real data, 34 of 35 slots try only their own seed (row 2) | - |
| 8 | selftest 663 / 663 | CONFIRMED | my run: `SELFTEST: 663 checks passed` (73 s, under scratch_dir) | - |
| 9 | mutants 69 / 69 killed | CONFIRMED | my run: `MUTANTS: 69 of 69 killed`, 0 SURVIVED (`grep -c SURVIVED` = 0, whole log) | - |
| 10 | pins | CONFIRMED | `git hash-object` gives 41aa53aa…; LF sha256 first 16 = 42099acec10bf68a, the same for the committed blob and the working file. The dry-run prints the same `[SCRIPT]` line; gap_fix.py is printed as blob:7c0691e8 (verified) | - |
| 11 | B-7: a seed is VOID iff vmf_em refuses citing FM.B6 (three cases) | PARTLY | in `flat_mix_mmlu.py`, vmf_em has three B6 refusal lines (L403, L413, L429) and **four** causes. The Degenerate path at L403 covers both a one-member cell (rbar outside (0,1)) and an **underflowing ive** (`log_cd`). B-7 does not list the ive underflow | LOW |
| 12 | the ruling's "if 5-9 are all VOID for a slot" | PARTLY | as built, the pool is shared across slots. A later slot can therefore become VOID-TREE when 5-9 are *used* (for example 9 taken OK by an earlier slot), even though 5-9 are not all VOID for that slot. This follows "lowest seed not yet used on that tree", but the ruling does not word this case. It is unreachable today (1 replacement) | LOW |
| 13 | prior POSTRUN: "15 of 35 stop at max_iter 200" | spot check, descriptive | I count 14 `converged False` among the 35 slots; seed 5 converged. On the 34 seeds shared with the earlier run the count is 14, against the earlier 15. No criterion reads convergence | LOW |
| 14 | the ADAPTIVE-PROFILE EVAL denominator (in the brief) | N/A | this delta touches only gap_fix_cc.py; the ADAPTIVE-PROFILE delta is a separate review | - |

## Own mutants (deciding paths; 3)

| id | change | result | decisive |
|---|---|---|---|
| O1 | the V dict records `seed=s0` (the slot seed), not the seed actually fitted | KILLED (assertion) | yes: it hides the replacement in the outcome |
| O2 | VOID-TREE `return` changed to `break` (the slot is skipped, the others kept) | KILLED (an UnboundLocalError crash; also loud in production) | yes |
| O3 | a CC-leg VOID-TREE is not dropped but passed on to tree_arms | KILLED (rc 1) | yes |

## Defects / fixes

- **D-1 (LOW, registrar):** bracket B-7 and B-8 into the record as builder declarations. No registered word changes.
- **D-2 (LOW, builder or registrar):** B-7 should list the fourth B6 path (ive underflow in `log_cd`, raised as Degenerate and
  refused at L403 citing B6). Fix: one sentence in the docstring / record. It needs no code change, because `is_b6_void`
  classifies on FM.B6 text and so already covers this path.
- **D-3 (LOW, registrar):** word the shared-pool case (row 12) in the P-1 bracket: "a slot that finds 5-9 all used (VOID or
  taken) makes the tree VOID-TREE". This is the built behaviour.

## Commands

```
cd .claude/worktrees/wf_11776b0c-a8a-3
git diff 6098f22f..886b81c7 --stat ; git show 886b81c7 --name-only --format= | wc -l          # 1 file
git hash-object tools/analysis/gap_fix_cc.py ; git show 886b81c7:tools/analysis/gap_fix_cc.py | sha256sum   # 41aa53aa / 42099acec10bf68a
python tools/analysis/scratch_dir.py --run -- python tools/analysis/gap_fix_cc.py --selftest     # 663 passed
python tools/analysis/scratch_dir.py --run -- python tools/analysis/gap_fix_cc.py --mutants      # 69 of 69 killed
python tools/analysis/scratch_dir.py --run -- python <scratch>/ownmut.py E:/TaxoArena_tmp/rev_gfc_own   # O1-O3 KILLED
powershell -File E:/TaxoArena_tmp/busy.ps1 ; echo $?                                             # 1 (after the mutants ended)
find <main> -maxdepth 4 (*.db|*-wal|*-journal) -printf '%p %s %T@' > before/after ; diff          # 413 files, identical
python tools/analysis/scratch_dir.py --run -- python tools/analysis/gap_fix_cc.py --dry-run --nomic-leg e1-guard \
       --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena                                               # rc 0; 35 VFIT; 1 replaced; VOID-TREE 0
grep -n 'B6' tools/analysis/flat_mix_mmlu.py                                                    # refusal paths L403/L413/L429
# RUN OF RECORD (after the merge by path; busy.ps1 exit 1 first; one reader):
#   main:     python tools/analysis/gap_fix_cc.py --run --nomic-leg e1-guard
#   worktree: python tools/analysis/gap_fix_cc.py --run --nomic-leg e1-guard --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena
```
