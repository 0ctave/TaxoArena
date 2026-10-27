# READY (delta 2) — ADAPTIVE-PROFILE: the D-2026-10-08-5 scorer delta

Reviewer: adversarial-reviewer, 2026-10-09. Zero calls. Read-only (views opened `mode=ro&immutable=1`, sha256 equal before/after).
Reviewed: branch `worktree-wf_d795fd62-e28-7` tip ca9dc87b (contains main 9af2c14a: `merge-base --is-ancestor` rc 0);
`tools/analysis/adaptive_profile.py` blob:aff80c1d0798b49baec676db4576d1f9c7d3c8a5 = sha256-lf16:f35a50f400ec9216
(sha256-crlf16:a38dc2aaca9c2c8a; the worktree holds the LF rendering). Parent of record blob:37b9b293 (READY cc49fc6a).
Authority: docs/agents/author_decisions/2026-10-08.md D-2026-10-08-5 (5211616a); programme L25317-L25327 (bb5eb124).
Delta scope: `git diff 37b9b293 aff80c1d` = 1 file, +489 / -27; all 27 deleted lines read (docstring, two imports moved
above the SELFTEST marker, the `read_views` call wrapped in `with Scorer`, the run() return, clone/_oracle fixture lines).
Everything else CONFIRMED by cc49fc6a / f4dd6292 is not re-derived here.

## VERDICT: READY (code), with one --run precondition (C-1)

The official `is_correct` is the only key on every deciding path; MATH-FIX overlay rows read = 0 is enforced by a count
refusal; H is a descriptive line read from the pinned table, refused on any other sha. Pinned modules unchanged.

## Per-claim table (deciding claims only)

| # | claim (builder) | mine | verdict | sev |
|---|---|---|---|---|
| 1 | official key, no overlay, on TRAIN / GATE / EVAL | seam rebinds `V.read_key` (V = UAR.V is the one module object in union_route_common L64, escalation_curve via U); calls pinned read_key with overlay False; X83 (overlay kept) KILLED, own O1 (H key returned as official) KILLED | CONFIRMED | - |
| 2 | exactly 3 reads, GATE by identity, overlay rows 0 | `gate_key` returns read_key's K unchanged (escalation_curve L528-L537), so `is` holds; X92, X93 KILLED; the printed "0 / 0 / 0" is a literal but guarded by the count refusal | CONFIRMED | LOW (L-1) |
| 3 | union_cells_io L187 not reached | L187 lies in `_eval_set_open` (L169), called only at L164; adaptive_profile reaches UCI only via `cell_member` (L1368) and `kish` (U L378); a 4th read would be refused by `scorer_keys` | CONFIRMED | - |
| 4 | no MATH-FIX-bound identity (the WIN-MAP B1 class) | `b3_check` (refit == frozen 8d68018c) count in adaptive_profile.py = 0 (grep -c over the whole file); the frozen policy is only sha-checked as a file (U.frozen_policy) | CONFIRMED | - |
| 5 | H table pin | main checkout: sha256 6b010fa60dde7278...eb1d1, 0 CR bytes (LF), 23,832 rows, 18 models, H credits 7,126, imported 2,335 = meta.json and math_scorer_h READY f4f7e0a0 | CONFIRMED | - |
| 6 | header line = registrar's deviation (1) | L25322 text vs `scorer_line(REG)`: identical, "MATH-FIX beside: no"; printed before DENOMINATORS in the real dry-run | CONFIRMED | - |
| 7 | H join cannot fail on real data (not claimed; my check) | views: columns legacy_qid, source present in response_lite and response; source 'MATH' rows gen 16,560 + eval 7,272 = 23,832, distinct (legacy_qid, model) = rows (no multi row: AP-SCORER usable-cell refusal cannot fire, rule UNUSABLE_CELL); missing in H 0 / 0; id-space (imported iff is_correct 1) mismatches on the gen view 0 / 16,560; EVAL side not read by me (sealed key) | PARTLY (EVAL id-space UNDETERMINED, fail-closed) | LOW (L-2) |
| 8 | selftest 13 / 13 | rerun on blob aff80c1d under scratch_dir: 13 / 13, rc 0 | CONFIRMED | - |
| 9 | mutants 99 / 99, X00 survives | re-ran decisive X00 (SURVIVED), X83, X88, X91, X92, X93, X94: 6 / 6 KILLED; the other 92 taken from the builder's log (not re-run) | CONFIRMED (decisive subset) | - |
| 10 | real --dry-run read-only | rc 0, 63 lines; POOL line first; H TABLE + scorer line before DENOMINATORS; TRAIN 11,841, EVAL 5,907 / 5,404, GATE 1,944 as registered; eval view not opened; gen view sha before = after; `experiment_results/archv2/` entries matching adaptive_profile: 0 | CONFIRMED | - |
| 11 | criteria / Support / denominators unchanged | denominators printed identical to READY cc49fc6a; no change to core(), rule, constants (deleted-line list above) | CONFIRMED | - |

Own mutants (3, on the delta's paths):
- O1 `Scorer.read_key` returns KH (H leaks into the deciding key): KILLED (AssertionError). Decisive.
- O2 `h_key` keeps the official value (vacuous H line): KILLED. Not decisive (descriptive line).
- O3 `load_h` header check dropped (`rows[0] != H_HEAD` removed): SURVIVED. Not decisive (the sha pin fixes the bytes, header included).

## Defects / conditions

- **C-1 (precondition of --run; registrar):** H table sha256-lf 6b010fa60dde727816b91196d2cb3045094082c3800fe738adebe21d19eeb1d1
  pinned in a registrar's record (deviation (2), L25322). `grep -c 6b010fa6 docs/judge_v2_program.md` = 0 at 9af2c14a.
  Fix: registrar record before the operator's --run. The --dry-run may run now.
- **C-2 (operator):** the script is NOT on main (`git cat-file -e 9af2c14a:tools/analysis/adaptive_profile.py` fails;
  READY cc49fc6a's "run from main after merge" never happened). Run from the worktree with `--data-root` the main checkout,
  or merge blob aff80c1d by path first and run from main. Either way the dry-run prints blob:aff80c1d; refuse on any other.
- **L-1 LOW:** the "overlay rows read 0 / 0 / 0" line in run() is a literal. Guarded by `scorer_keys` (refuses on any
  overlay row; X93 killed), and read_views prints the computed per-read counts. Fix (optional): format the counts from `sc.calls`.
- **L-2 LOW:** an EVAL-side id-space mismatch would refuse [AP-H-JOIN] AFTER the write-once marker is written, so a
  descriptive line could burn the run slot. Evidence against it: 0 / 16,560 on TRAIN+GATE, full key coverage on EVAL.
  Fix (optional): run the H join's id-space check on the EVAL rows before the marker, or accept as is.
- **L-3 LOW:** O3 survives (the header check is untested). Fix: one refusal case with a wrong header and a re-pinned sha.
- **L-4 LOW (reviewer's own process):** my gen-view id-space count (claim 7) ran while busy.ps1 returned 0. The matching
  process was a peer's sandboxed `harness_extractor.py --selftest`, not a pool reader. The real dry-run and the structural
  view read ran with busy.ps1 rc 1. Disclosed.

## Run commands (operator; rule 7: `powershell -NoProfile -File E:/TaxoArena_tmp/busy.ps1` must exit 1 before each)

```
cd Z:/FAC/TUBerlin/THESIS/TaxoArena/.claude/worktrees/wf_d795fd62-e28-7
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 python tools/analysis/adaptive_profile.py --dry-run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena
# after C-1 (registrar pin of 6b010fa6...) only:
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 python tools/analysis/adaptive_profile.py --run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena
# back up experiment_results/archv2/adaptive_profile/ + E:/TaxoArena_tmp/blog/profiles/adaptive_profile_fingerprints*.* to E:/TaxoArena_backup_20261009_adaptive_profile with SHA256SUMS
```

## Commands that show each result

```
git merge-base --is-ancestor 9af2c14a ca9dc87b; git rev-parse ca9dc87b:tools/analysis/adaptive_profile.py   # aff80c1d
git diff 37b9b293 aff80c1d | grep '^-' | grep -v '^---' | wc -l                                               # 27, all listed
python tools/analysis/scratch_dir.py --run -- python tools/analysis/adaptive_profile.py --selftest              # 13 / 13
IDS=X00,X83,X88,O1 | X91,X92,X93,O2 | X94,O3  python scratch_dir.py --run -- python E:/TaxoArena_tmp/rev_ap_delta/own_mut.py
python tools/analysis/adaptive_profile.py --dry-run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena               # log E:/TaxoArena_tmp/rev_ap_delta/dry.log
sha256sum experiment_results/math_scorer_h/math_h_table.csv; grep -c $'\r' <same>                              # 6b010fa6..., 0
sqlite3 file:<view>?mode=ro&immutable=1: PRAGMA table_info; SELECT source,COUNT(*) ...; (legacy_qid,model) of source='MATH' vs H keys
grep -c b3_check tools/analysis/adaptive_profile.py                                                            # 0
grep -n _eval_set_open tools/analysis/union_cells_io.py                                                        # L164 (caller), L169 (def)
grep -c 6b010fa6 docs/judge_v2_program.md                                                                      # 0 -> C-1
```
