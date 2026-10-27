# PIN-CHECK DELTA READY: WIN-MAP under the official refit (G-1 met), adversarial reviewer, 2026-10-09

Reviewed: the registrar's Support insertion, prog section "## Registrar's record 2026-10-09 (insertion only; zero calls; nothing run;
pre-data) — WIN-MAP Support (b)-(g) re-derived under the ONE official refit ..." L25412-L25418 (78f9bc2e; `wc -l` of the programme =
25,418), against `SUPPORT` / `support_lines` of tools/analysis/win_map.py on branch `win-map-official`, tip a8717f45.
Blob: blob:80f5cb1f343de1f0df74e39499c953f00fed232d (`git rev-parse a8717f45:<path>` = `git hash-object <wt path>`),
sha256-lf16:8f754f5df9a2ea46 (LF, of record). The worktree holds the LF rendering (its sha256 = 8f754f5d; `status --porcelain | wc -l` = 0);
the CRLF rendering would be sha256-crlf16:32b963ad68e17890. The code is unchanged since READY_WIN-MAP_official_delta.md (69032fdb), whose
code findings (rows 1-6, own mutants W01/W09/W10) are cited and not re-derived. Zero calls.

## VERDICT: READY (conditions L-1, L-2 carried; L-3, L-4 new, all LOW; none blocks the run)
The condition set by READY_WIN-MAP_official_delta.md ("READY follows the insertion without a further code review, provided its planning
POINT values equal the code's SUPPORT constants") is met to the digit. No builder delta is owed.

## Per-claim table (deciding claims only)
| # | claim | reviewer's evidence | status | sev |
|---|---|---|---|---|
| 1 | Blob pinned is the reviewed one | rev-parse = hash-object = 80f5cb1f; lf16 8f754f5df9a2ea46 | CONFIRMED | - |
| 2 | POINT values = SUPPORT (L276-277) | code: wf1 se 0.0363 mde 0.102 deff 1.595 n_eff 3388; wf2 0.0143 / 0.040 / 1.10 / 4913; rs1 sd 0.05 se 0.0280 mde 0.078 deff 2.0 n_eff 5; record L25414: identical | CONFIRMED | - |
| 3 | SE re-derived from DEFF and n (check 8) | own: SE(G_AF) = sqrt(0.185/5,907) x sqrt(1.595) = 0.00707; band sqrt((0.185 -/+ 0.0660)/5,907) x sqrt(1.595) = [0.00567, 0.00823]; SE(rho) 0.00707/0.195 = 0.03626; MDE80 0.1016 -> 0.102 | CONFIRMED (to the digit) | - |
| 4 | WF1 worst reachable / corner | own: 0.195 - 0.0660 x 0.430 = 0.16662; 0.00823/0.1666 = 0.04940, x2.8 = 0.1383; corner 0.00823/0.129 x 2.8 = 0.1786 | CONFIRMED (0.0494 / 0.138 / 0.179) | - |
| 5 | Builder's "realistic" upper corrected to 0.142 | own: 2.8 x 0.00823 / 0.162 = 0.1422 | CONFIRMED | - |
| 6 | WF2 point / worst | own: 0.0043/0.30 = 0.01433, MDE80 0.040; 0.0043/0.27162 x 2.8 = 0.0443 | CONFIRMED (0.0143 / 0.040 / 0.044) | - |
| 7 | RS1 | own: 1.2533 x 0.05 / sqrt(5) = 0.028025; x2.8 = 0.0785 | CONFIRMED (0.0280 / 0.078) | - |
| 8 | n_eff | own: 5,404/1.595 = 3,388.1; 5,404/1.10 = 4,912.7; 10/2 = 5 | CONFIRMED (arithmetic) | - |
| 9 | Verdict words SCOREABLE x3; reachable at infinite budget | WF1 margin 0.17 > worst reachable MDE80 0.138 (corner 0.179 disclosed unreachable: needs D_any = 1 vs all-sides any-solved 0.570); WF2 0.25 > 0.044; RS1 on declared SD; (g) every word reachable | CONFIRMED | - |
| 10 | s = 390 / 5,907 | own: 0.06602 | CONFIRMED | - |

## Defects and conditions (LOW; builder, optional before the run; if not fixed, the POSTRUN review reads them as disclosed)
- **L-1 (carried, 69032fdb).** Add a TRAIN-empty AF-U cell to the fixture so that W01 dies.
- **L-2 (carried, 69032fdb).** The PIN line's label "sha256-crlf16/working-tree bytes" prints the LF value (harmless here: the worktree is LF).
- **L-3 (new).** `support_lines` L798 still brackets (b)-(g) as "the PRE-DEVIATION (MATH-FIX, frozen-policy) planning values; their
  re-derivation ... binds over these". After L25412 the printed point values ARE the re-derived ones, and the (f) line prints only
  "beyond MDE 0.102", not the registered worst reachable 0.138. The outcome file is write-once, so this text would be of record.
  Fix: bracket text "(b)-(g): the registrar's re-derivation under the official refit, prog L25412-L25418 (point values; WF1 worst
  reachable MDE80 0.138, corner 0.179 unreachable; WF2 worst 0.044)". No statistic changes; a one-string delta, re-pin only.
- **L-4 (new, record convention).** SE(G_AF) is derived from N = 5,907 items x DEFF 1.595, while n_eff divides the 5,404 components by
  the same DEFF (5,907 / 1.595 = 3,703 would be the matching n_eff). n_eff enters no SE or MDE here and the measured n_eff is printed
  beside it; the registrar may bracket the convention. Not decisive.

## Run commands (from the worktree `.claude/worktrees/win-map-official`, blob 80f5cb1f, or main after a merge that keeps the blob; launch directly)
```
powershell -NoProfile -File E:/TaxoArena_tmp/busy.ps1                       # must exit 1
python tools/analysis/scratch_dir.py --run -- python tools/analysis/win_map.py --selftest     # 12 / 12
python tools/analysis/win_map.py --dry-run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena      # rc 0, 35 lines, POOL pv2_1575de61bb20e977 first
python tools/analysis/win_map.py --run     --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena
# back up outcome, official policy json, parquet + README to E:/TaxoArena_backup_<date>_win_map with SHA256SUMS; never commit
```
If L-3 is applied, the blob changes: the operator re-pins it (hash-object) and the selftest must still read 12 / 12; no further review
is owed for a string-only change confined to the support_lines bracket.

## Commands (read-only; zero calls)
```
git rev-parse a8717f45:tools/analysis/win_map.py ; git hash-object <wt>/tools/analysis/win_map.py       # 80f5cb1f both
git show a8717f45:tools/analysis/win_map.py | sha256sum ; | sed 's/$/\r/' | sha256sum                 # 8f754f5df9a2ea46 ; 32b963ad68e17890
git -C .claude/worktrees/win-map-official status --porcelain | wc -l                                     # 0
git show a8717f45:tools/analysis/win_map.py | sed -n 276,277p ; sed -n 795,800p                          # SUPPORT ; L-3 bracket
sed -n 25412,25418p docs/judge_v2_program.md ; wc -l docs/judge_v2_program.md                             # insertion ; 25,418
python: sqrt(.185/5907)*sqrt(1.595)=.00707; band .00567/.00823; .00707/.195=.03626; .195-.066*.43=.16662; .00823/.1666=.0494 (x2.8 .1383);
        .00823/.129*2.8=.1786; 2.8*.00823/.162=.1422; .0043/.30=.01433; .0043/.27162*2.8=.0443; 1.2533*.05/sqrt(5)=.02802 (x2.8 .0785);
        5404/1.595=3388.1; 5404/1.1=4912.7; 390/5907=.06602
```
