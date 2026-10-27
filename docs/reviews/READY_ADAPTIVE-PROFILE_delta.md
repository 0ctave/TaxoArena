# READY (delta) review: ADAPTIVE-PROFILE (tools/analysis/adaptive_profile.py)

Reviewed: branch `worktree-wf_11776b0c-a8a-2` tip d998b511, file blob:37b9b29315d5b4b594052b1a17c3503c03347f79 (LF, of record;
sha256-lf16:d26a7fff2ddc1f3a; the worktree holds the CRLF rendering, sha256-crlf16:e0572cc5a340ff80; `git hash-object` = committed blob).
Delta: `git diff 58acd976 d998b511` (1 file, +185 / -32). 58acd976 is the cherry-pick of the reviewed 6555d5e7: its blob is
7e2949bb, the blob READY f4dd6292 reviewed, so the base is the reviewed code. Rulings: prog "## Registrar's record 2026-10-08 ...
rulings GAP-FIX-CC P-1 ..., the R1 twin rule ..., and ADAPTIVE-PROFILE D-3" L25212-L25219 (_as_of 6098f22f).
Zero calls. Read-only: selftest and mutants in the scratch_dir sandbox; one real --dry-run (pool reader, busy.ps1 exit 1 immediately before).
Code that the delta does not touch was confirmed in READY f4dd6292 (rows 1-4, 6, 8, 10, 13). It is not re-derived here.

## VERDICT: READY (the run command and conditions are below)

## Per-claim table (deciding claims of the delta)

| # | Claim | My evidence | Result | Sev |
|---|---|---|---|---|
| 1 | B1 / R1 ruling: no pre-read refusal; EVAL-side twins are counted | `between()` now only `say`s the count and hits R1.EVAL_SIDE. Real dry-run: "R1 twin items by split side ...: {'EVAL': 115, 'GATE': 47, 'TRAIN': 265} (--run REFUSES if any is a scored EVAL item)". X60 (re-aimed: refuse an UNSCORED EVAL-side twin) is the ruling's required mutant and was KILLED in my own run | CONFIRMED | - |
| 2 | Refusal iff a twin is among the SCORED EVAL items, after the read and before any fit | The post-read `if tw_e:` (tw_e = D.E items & twins) refuses before the Kg / core() calls. `refusals` plants 1 scored EVAL twin plus 1 unscored: refused with "[R1-EVAL] 1 scored EVAL item(s)"; no AP1 or BRIER line, no outcome. X72 (refuse on the EVAL-side set) KILLED; my Z2 (refuse only at >= 2 scored twins) KILLED | CONFIRMED | - |
| 3 | EVAL denominator as ruled: 5,907 / 5,404, not 5,792 | Real dry-run: "EVAL 5907 items / 5404 components (scored ONCE) x 18 models". REG and [AP-DENOM] are unchanged by the delta. Support is unchanged, as the ruling says, so it is not recomputed (f4dd6292 row 10) | CONFIRMED | - |
| 4 | D-2: F_bis SE gate tested | New case `bis_gate`: >= 3 planted models with a certified F_bis child at SE >= 0.20 are not descended into, and one at SE < 0.20 is; F_bis Brier equals the rule's at 0.20 and differs from the ungated rule's (non-vacuous). The review's Y2 (= X73, s_max inf) is now KILLED in my run. My Z3 (F_bis gate at s_max + 0.05) SURVIVED: no planted F_bis SE lies in [0.20, 0.25). X74 (0.30) is killed per the builder | PARTLY | LOW (D-1) |
| 5 | L-1: one-member family certifies iff \|z\| > 1.96 strict at q 0.05 | `certify` gets a one-member branch at q == Q_SINGLE (0.05). Hand cases z 1.95998 / 1.96 not certified, 1.9601 and -1.9601 certified; q 0.10 BH. X77 (>=) KILLED. The registration ties "single-sibling threshold \|z\| > 1.96" to q = 0.05; at the grid's other q (descriptive only), BH at n = 1 is the reading I ACCEPT. My Z1 (1.96 also at q 0.01) SURVIVED: the q 0.01 one-member path has no hand case (descriptive grid only) | CONFIRMED (reading accepted) | LOW (D-2) |
| 6 | L-2 disclosed in every dry-run and run | `denominators()` prints "DISCLOSED (L-2, READY f4dd6292) ..." in both modes; seen in the real dry-run and required in run_e2e | CONFIRMED | - |
| 7 | D-3: P9 "NOT SCORED (leg not built; declared deviation)" and the af_clean_s42 WILL-NOT-SHOW clause | pred_lines and all_lines carry the ruled words; run_e2e `need`s both | CONFIRMED | - |
| 8 | Selftest 12/12 | My run: 12 / 12 passed in 70 s (sandbox) | CONFIRMED | - |
| 9 | Mutants: the delta's decisive ones plus my 3 | X00 SURVIVED (control); X60, X72, X73, X77 KILLED; my Z2 KILLED, Z1 and Z3 SURVIVED (both non-decisive: the descriptive grid, and F_bis is secondary). I did not re-run the full 82: the 70 old anchors sit on code the delta does not touch, and run_mutants refuses an anchor that does not apply | PARTLY | LOW |
| 10 | Real dry-run read-only, zero calls | rc 0. gen_view sha256 before = after (c2930c60...); eval_view "NOT opened"; experiment_results/archv2/adaptive_profile absent before and after; mtimes of embeddings_cache.db and multicorpus_cache_v1.db unchanged (diff empty) | CONFIRMED | - |
| 11 | Pins / hygiene | The delta touches 1 path (`git diff --name-only 6098f22f d998b511` = 1 line). Main moved to 58580670 (1 commit, 1 path, 0 under tools/analysis/), so the merge has no conflict. The dry-run header pins blob 37b9b293 / lf16 d26a7fff / crlf16 e0572cc5, equal to the builder's | CONFIRMED | - |

## Defects and fixes (none blocks)

- **D-1 (LOW): F_bis gate constant is checked only coarsely.** Z3 survives because no planted F_bis SE lies in [0.20, 0.25).
  Fix (optional): plant one certified F_bis child with SE in (0.20, 0.22) that must not be descended into.
- **D-2 (LOW): the q 0.01 one-member path has no hand case.** Z1 survives (descriptive grid only). Fix (optional): add a q 0.01
  case at z 2.0 (must not certify: p 0.0455 > 0.01).
- **D-3 (LOW, text): stale docstring.** LAUNCH SEQUENCE step 2 still says "the EVAL-twin pre-check". Fix: "the EVAL-side twin
  count". Cosmetic; it does not touch any deciding path.
- **C-1 (condition): run from MAIN after merging d998b511** (main 58580670 does not yet carry adaptive_profile.py; the merge is
  conflict-free). Pin the merged blob as 37b9b293. If the run is made from the worktree instead, pass `--data-root Z:/FAC/TUBerlin/THESIS/TaxoArena`.
- **C-2 (condition): the scored set's twin count is known only after the read.** The ruling says it is 0 (WIN-MAP 12f42190 row 8).
  If it is not 0, --run refuses (a failed precondition, not an outcome) and the case goes back to the registrar.

## Commands

```
git rev-parse d998b511:tools/analysis/adaptive_profile.py 58acd976:tools/analysis/adaptive_profile.py   # 37b9b293 / 7e2949bb (= reviewed)
git diff 58acd976 d998b511 -- tools/analysis/adaptive_profile.py                                         # the delta read in full (35 KB)
python tools/analysis/scratch_dir.py --run -- python tools/analysis/adaptive_profile.py --selftest       # 12 / 12, 70 s
python tools/analysis/scratch_dir.py --run -- python <scratchpad>/own_mut.py   # AP.MUTANTS := X00, Z1-Z3, X60, X72, X73, X77
  Z1 'q == Q_SINGLE' -> 'q <= Q_SINGLE' S (non-decisive) | Z2 'if tw_e:' -> 'if len(tw_e) > 1:' K (decisive)
  Z3 F_bis stops_rule(..., c["s_max"] + 0.05, ...) S (non-decisive) | X60 K | X72 K | X73 (= Y2) K | X77 K | X00 S
powershell -File E:/TaxoArena_tmp/busy.ps1   # rc 1 (an earlier poll gave 0: a gap_fix_cc --mutants sandbox run; waited)
python tools/analysis/adaptive_profile.py --dry-run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena   # from the worktree; rc 0
  -> "EVAL 5907 items / 5404 components"; "R1 ... 471 ids / 427 ... -> 427 v2 items"; by side EVAL 115 / GATE 47 / TRAIN 265
  -> gen_view sha EQUAL before/after; eval_view NOT opened; "DISCLOSED (L-2 ...)"
ls -la --time-style=full-iso embeddings_cache.db multicorpus_cache_v1.db  (before vs after: diff empty)
git diff --name-only 6098f22f 58580670 | grep -c tools/analysis/   # 0
```

Run (busy.ps1 must exit 1 first; a pool reader; OMP/OPENBLAS/MKL_NUM_THREADS=1), from MAIN after the merge of d998b511:
`python tools/analysis/adaptive_profile.py --dry-run`, then `python tools/analysis/adaptive_profile.py --run`.
From the worktree instead, add `--data-root Z:/FAC/TUBerlin/THESIS/TaxoArena` to both.
