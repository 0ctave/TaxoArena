# DELTA READY review: WIN-MAP under the official MATH scorer (D-2026-10-08-5; D-2026-10-09-2 one refit), adversarial reviewer, 2026-10-09

Reviewed: branch `win-map-official` (worktree `.claude/worktrees/win-map-official`), tip a8717f45. Its parent 2320b671 copies in three
paths by path, and they are byte-equal to 7e2673d4 (`git rev-parse` of READY_WIN-MAP.md 32360e19, READY_WIN-MAP_delta.md 507356e7,
win_map.py 74f2e234). edb060b9 is an ancestor. `git diff --name-only edb060b9 a8717f45` gives exactly those 3 paths. The delta is
`git diff 2320b671 a8717f45` (+698 / -64), win_map.py only.
Blob: blob:80f5cb1f343de1f0df74e39499c953f00fed232d (`rev-parse` = `hash-object`), sha256-lf16:8f754f5df9a2ea46 (worktree is LF, 0 CR;
sha256-crlf16:32b963ad68e17890). Code outside the delta: cited from READY_WIN-MAP.md / _delta.md, not re-derived. Zero calls.

## VERDICT: NOT READY: the registration gate only. Code CONFIRMED.
The record says (prog L25073 bracket, L25398): "(b)-(g) are to be RE-DERIVED under the official refit by a registrar's insertion
before the delta READY; until then no verdict line here binds the run". That insertion does not exist (`wc -l` of the programme =
25,401; the last section is L25394, and no later bracket exists at L25073). Nothing in the code blocks the run.
READY follows the insertion below without a further code review, provided its planning POINT values equal the code's SUPPORT
constants (WF1 0.0363 / 0.102; WF2 0.0143 / 0.040; RS1 0.0280 / 0.078; L276). If the registrar changes a point value, a builder delta
of `SUPPORT` / `support_lines` and a delta READY are owed.

## Per-claim table (deciding claims only)
| # | claim | reviewer's evidence | status | sev |
|---|---|---|---|---|
| 1 | Every key read is official (no overlay) | `train_block` reads with overlay False. `Scorer` rebinds `V.read_key` inside `run()`: union_cells_io L187 calls `V.read_key(..., True, ...)` by module attribute, the seam forces `self.OVERLAY` (False), it refuses any order other than (response_lite, False) then (response, True), and it refuses on overlay rows > 0. Post-check: identity of both K objects. Own re-run: S01-S04, S07, S08 KILLED by value | CONFIRMED | - |
| 2 | ONE refit on TRAIN; identities against it (D-2026-10-09-2) | `P_off = V.fit(D, V.train_full(D))` (G3 guard); `w_id`: run_boot P0 == P_off, R_AF / B == plain recomputation from the written document (tol 1e-9), G_AF = R_AF - B, fits == B + 2; MATH-FIX targets 0.6201 / 0.6049 / 8d68018c removed (frozen policy only descriptive and roster); refit sha printed and written "xb". S09, M31, M34 KILLED | CONFIRMED | - |
| 3 | H decides nothing | H matrix used only in `h_points` / `h_lines` after the waterfall; own W09 (H as the TRAIN key of D) and W10 (H as the EVAL key) KILLED; S21 KILLED | CONFIRMED | - |
| 4 | Deviation and scorer header | real dry-run: line 3 is the scorer line with 6b010fa6...; then "DECLARED PRE-RUN DEVIATION D-2026-10-09-2 ..." and the D-5 disclosure | CONFIRMED | - |
| 5 | Selftest 12/12; mutants 105/105 | own selftest "12 / 12 passed"; own subset C00 SURVIVED, S01 S02 S03 S04 S07 S08 S09 S21 M31 M34 KILLED | CONFIRMED (subset) | - |
| 6 | Real --dry-run | own (busy.ps1 rc 1): rc 0, 35 lines; POOL pv2_1575de61bb20e977 first; H TABLE = pin, 23832 rows; frozen 8d68018c = pin; EVAL 5907 / 5404 (registered); per source MATH 390; "nothing written"; `experiment_results/archv2` holds no win_map entry (`grep -c` 0); views EQUAL before / after | CONFIRMED | - |
| 7 | Support re-derivation (builder's note) | recomputed below: point values, SE(G_AF) band [0.00567, 0.00823], extreme corner 0.179, WF2 extreme 0.0184 reproduce to the digit. The builder's "realistic" WF1 band keeps SE(G_AF) at its point; with the band's upper end, realistic MDE80 is 0.142, not 0.122 (still < 0.17) | PARTLY | LOW |
| 8 | Support gate | registrar's insertion absent (see verdict) | NOT MET | BLOCKER (registration) |

## Own mutants (sandbox E:/TaxoArena_tmp/rev_wm; appended to MUTANTS)
- W01: the refit document maps an absent cell (-1) to the last model: SURVIVED, not decisive. The fixture has no TRAIN-empty AF-U
  cell. On the real data, the frozen policy has 123 cells with 0 None, and cell mass does not depend on the scorer. If an absent
  cell did occur, W-ID's plain recomputation would refuse (fail-closed). LOW (L-1).
- W09: the H key as the TRAIN key of D: KILLED (decisive).
- W10: the H key as the EVAL key of D: KILLED (decisive).

## What the registrar must insert (Support (b)-(g) under the official refit; reviewer's re-derivation, planning, no EVAL statistic)
Inputs: Support L25073 (pre-deviation); UNION-AF-ROUTE two-stage SE(G_AF) 0.707pp, DEFF 1.595 (D-PR-1). s = 390 / 5,907 = 0.0660 (EVAL
MATH items, structure only, real dry-run). The H table (pin 6b010fa6, all sides, 1,324 MATH questions): official any-solved 0.5702,
so D_any <= 0.430 (H proxy 0.221). The frozen best single is Qwen2.5-72B-Instruct, with an H-proxy MATH drop of 0.566 (D_B > D_any
moves the denominator UP).
- (b) DEFF: WF1 1.595, TRANSPORTED (same 5,907 / 5,404, the same two-stage bootstrap, the policy refit per replicate in the same form; only the
  scorer of the 390 MATH items changes); WF2 1.10 (planning); RS1 2.0 DECLARED.
- (c) n_eff: 3,388 / 4,913 / 5 (unchanged).
- (d) SE(G_AF): planning 0.00707. i.i.d. variance 0.185 +/- s gives the band [0.00567, 0.00823]. Denominator O_adj - B = 0.195 + s(D_B - D_any).
  This is at least 0.195 - 0.0660 x 0.430 = 0.1666 on the H-table bound, and at least 0.129 at the unreachable corner (D_any = 1).
  SE(rho): point 0.0363; worst reachable 0.00823 / 0.1666 = 0.0494; corner 0.0638. WF2: SE(lambda) = 0.0043 / (0.30 + s(D_B - D_any)):
  point 0.0143; worst reachable 0.0043 / 0.2716 = 0.0158. RS1: 0.0280.
- (e) MDE80: WF1 point 0.102, worst reachable 0.138, corner 0.179; WF2 point 0.040, worst 0.044; RS1 0.078.
- (f) WF1 SCOREABLE (predicted rho 0.08 lies 0.17 below 0.25; MDE80 <= 0.138 on every value the H table allows; the corner, 0.179, needs
  D_any = 1 on EVAL against an all-sides official any-solved of 0.570, and is disclosed as unreachable, not powered); WF2 SCOREABLE;
  RS1 SCOREABLE on its DECLARED SD (unchanged).
- (g) Every word is reachable at infinite budget. rho is bounded by the policy fitted on TRAIN only (the ONE official refit; G3 guard).
  O_adj <= B gives WF1 NOT EVALUABLE. The measured sd_rho, sd_lam, DEFF and n_eff are printed beside the planned values (support_lines).
  The bound uses an all-sides table, not EVAL: an assumption, stated as such.

## Defects and fixes
- **G-1 BLOCKER (registrar).** Insert (b)-(g) above (or the registrar's own figures) at L25073 / a new record. Then a pin-check delta
  READY follows: the insertion's point values against `SUPPORT` L276. No code change is needed if they match.
- **L-1 LOW (builder, optional).** Add a TRAIN-empty AF-U cell to the fixture so that W01 dies.
- **L-2 LOW (builder).** The PIN line's label reads "sha256-crlf16/working-tree bytes" but prints the LF value (8f754f5d; the worktree
  is LF). Relabel it "working-tree bytes".

## Run commands (ONLY after G-1 and the pin-check READY; launch directly)
```
powershell -NoProfile -File E:/TaxoArena_tmp/busy.ps1                       # must exit 1
python tools/analysis/scratch_dir.py --run -- python tools/analysis/win_map.py --selftest
python tools/analysis/win_map.py --dry-run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena
python tools/analysis/win_map.py --run     --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena
# back up outcome, official policy json, parquet + README to E:/TaxoArena_backup_<date>_win_map with SHA256SUMS; never commit
```

## Commands (read-only; zero calls)
```
for p in READY_WIN-MAP.md READY_WIN-MAP_delta.md win_map.py: git rev-parse 7e2673d4:<p> 2320b671:<p>   # equal
git diff --name-only edb060b9 a8717f45                                           # 3 paths, all of the copied build
git rev-parse a8717f45:tools/analysis/win_map.py ; git hash-object <wt path>      # 80f5cb1f both; LF 8f754f5df9a2ea46
git archive a8717f45 -- . ':!*.db' ':!*.npz' | tar -x -C E:/TaxoArena_tmp/rev_wm  # + W01 W09 W10
scratch_dir.py --run -- python tools/analysis/win_map.py --selftest              # 12 / 12
scratch_dir.py --run -- python tools/analysis/win_map.py --mutants --only C00 S01 S02 S03 S04 S07 S08 S09 S21 M31 M34 W01 W09 W10   # 12 of 13 KILLED (W01)
busy.ps1 -> 1 ; python tools/analysis/win_map.py --dry-run --data-root <main>    # rc 0, 35 lines (E:/TaxoArena_tmp/rev_wm/wm_dry.log)
python (H table csv): official any 0.5702 over 1,324 q; H any 0.7915; per-model drops   # D_any bound
python (frozen policy 8d68018c json): 123 cells, 0 None, best single Qwen2.5-72B-Instruct
python: s 0.06602; SE(G_AF) [0.00567, 0.00823]; den_min 0.1666; SE 0.0494; MDE 0.138; corner 0.0638 / 0.179; WF2 0.0158 / 0.0443
```
