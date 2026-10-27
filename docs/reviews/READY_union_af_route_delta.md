# READY (delta) — UNION-AF-ROUTE reader, union-af-route 2db6e35c..fb6e6ee9

Reviewer: adversarial-reviewer, 2026-10-02. Zero calls, no JVM, no construction. Delta review of the C-1..C-4, D-4 and D-5
fixes asked by `docs/reviews/READY_union_af_route.md`. Everything that review CONFIRMED on code this delta does not touch is
cited, not re-derived. D-3 is bracketed by the registrar (09299c3a) and is not reviewed here.

## Verdict

**READER READY for `--run`**, which closes C-1..C-4. The build preconditions P1-P6 of the first review still bind, and P2 (the
author checkpoints `mmlu_pro_dataset_cache_v2.db-wal`) still blocks the build. The order holds: build, then `--dry-run`, then
`--build-inputs`, then `--dry-run`, then `--run`.

## Pins (LF of record)

| file | blob (LF) | sha256-lf16 / sha256-crlf16 | working tree |
|---|---|---|---|
| tools/analysis/union_af_route.py | a99bcee5de3ff1d6ae08b2910c19cc3bb0f02716 | b2a4ef5e56714765 / 5db984c42255a43f | LF |
| tools/analysis/v2_declared_cells.py (1d98888f → f0f56805) | f0f568057995b5d0231da6e3d0d48755a7cf8386 | 9604636e5a4b9770 / 0ea9e645d34687cb | LF |

Delta: 2 files, +140 / −19. In v2_declared_cells.py it is +5 lines: one docstring bracket and the `cfg.pre_eval` call.

## Per-claim table

| # | claim | my result | verdict | sev |
|---|---|---|---|---|
| C-4 | R10 runs BEFORE the EVAL view / the B1 marker | In v2_declared_cells f0f56805, `cfg.pre_eval(cfg, pol, psha, say)` sits at L1161-L1162, after the B3 policy write and sha line (L1159) and before `--- EVAL (eval_view ...` (L1165) and `G.read_marker(cfg.mark_u ...)` (L1208). make_cfg wires `cfg.pre_eval = r10_check`, and rp13_tail refuses if `r10_line` is absent. The run_e2e case asserts the R10 line sits in the pre-EVAL part. The refusals case asserts no READ_STARTED and the policy file present on an R10 refusal. My O6 (pre_eval unwired in make_cfg) is KILLED | CONFIRMED | — |
| C-4b | The stricter R10 (9 keys) does not trip on real data | On the real files, leg U's policy holds all 9 R10_KEYS. G14's committed tree-run policy (the closest analogue to RP13's run) equals it on all 9 → 0 differing keys | CONFIRMED | — |
| C-1 | One true_source_domain pick refuses | new refusals case. My O1 (R10_KEYS = best_single only) is now KILLED (builder's X58 also) | CONFIRMED | — |
| C-2 | The extra-arm B3 re-fit mismatch refuses | new refusals case (tamper after r10_check). My O2 (`if False and {k: nn(v)` in vdc) is now KILLED (builder's V07) | CONFIRMED | — |
| C-3 | Identity: point equal, interval end differs → refuses | new refusals case. My O4 (`if got[0] != ident[0]`) is now KILLED (builder's X59) | CONFIRMED | — |
| D-4 | Disclosure line printed | `U2.D4_DISCLOSED` line in u_lines; asserted in branches and run_e2e; X60 KILLED | CONFIRMED | — |
| D-5 | Policy at scratch/, --run refuses unless ignored AND untracked | REG policy = `.../union_af_route/scratch/union_af_route_train_policy.json`; `git check-ignore -v` → `.gitignore:77:scratch/` (rc 0); .gitignore not edited by the delta (2 files changed). The refusal sits in run() before any read; X61 KILLED. My O7 (drop the untracked clause) SURVIVED, because the selftest stubs `_IGNORED`. I executed the REAL `_git_ignored` on the repo instead: the scratch policy path gives True, the tracked-and-ignored `.claude/agents/adversarial-reviewer.md` gives False, the non-scratch policy path gives False. All three branches are correct | CONFIRMED (survivor covered by direct execution) | LOW |
| INERT | Hooks absent = c5b90278 | selftest case `vdc_inert` passes on f0f56805 (G14 outcome line for line, policy key for key, against `git show c5b90278`). V06 KILLED by it (the case discriminates); V08 (pre_eval not called) KILLED | CONFIRMED | — |
| S | Selftest / mutants | re-run: `selftest: 10 / 10 passed`; `MUTANTS: 70 of 70 KILLED; control survived; survivors none` (rc 0) | CONFIRMED | — |
| DRY | The dry-run refuses AF-U ABSENT | run against main's data: POOL line first; AK-IDENTITY reproduced (+0.0738 / +0.0656 / 0.0414 / 0.0233); `REFUSED: AF-U build outputs ABSENT (16 of 16)`, rc 1; no `experiment_results/archv2/union_af_route/` created; the listing of the 25 root *.db / -wal files is identical before and after | CONFIRMED | — |

## Own mutants (delta; via the builder's harness with `U.MUTANTS` swapped in memory)

| id | change | result | decisive |
|---|---|---|---|
| O1 | R10_KEYS = ("best_single",) | KILLED (refusals) | yes |
| O2 | vdc: extra-arm B3 re-fit check disabled | KILLED (refusals) | yes |
| O4 | identity compares the point only | KILLED (refusals) | yes |
| O6 | make_cfg: `cfg.pre_eval = None` | KILLED (run_e2e, refusals) | yes |
| O7 | `_git_ignored`: untracked clause dropped | SURVIVED (stubbed in selftest); the real function executed correctly on 3 real paths | no |

## Defects

- **L-1 (LOW, optional)**: add a selftest case that calls the real `_git_ignored` on a temporary git repo (a tracked file
  matched by an ignore pattern returns False), so that O7 is killed by the suite rather than by the reviewer's direct run.
  This does not gate the run.

## Commands

```
git diff 2db6e35c fb6e6ee9 -- tools/analysis/v2_declared_cells.py ; git diff --stat 2db6e35c fb6e6ee9      # 2 files
git show fb6e6ee9:tools/analysis/v2_declared_cells.py | grep -n "pre_eval\|B3 FROZEN\|--- EVAL (eval_view\|read_marker"
git check-ignore -v experiment_results/archv2/union_af_route/scratch/union_af_route_train_policy.json      # .gitignore:77 scratch/
python -c "R10_KEYS on v2_declared_cells_U_train_policy.json vs v2_declared_cells_G14_train_policy.json"  # 0 differing
(worktree) python tools/analysis/union_af_route.py --selftest     # 10 / 10
(worktree) python tools/analysis/union_af_route.py --mutants      # 70 of 70 KILLED
python scratchpad/rp13m/own_mutants2.py / own_mutants3.py          # O1 O2 O4 O6 killed; O7 survived
python -c "U._git_ignored(<scratch path> / <tracked ignored file> / <non-scratch path>)"   # True / False / False
TAXOARENA_DATA_ROOT=<main> TAXOARENA_RESULTS_ROOT=<main> python tools/analysis/union_af_route.py --dry-run   # rc 1, AF-U ABSENT
```
