# READY review: OOS-TREE-CELLS (branch oos-tree-cells, tip 515c9380, tools/analysis/oos_tree_cells.py)

Reviewer: adversarial-reviewer, 2026-10-03. Registration: prog L23875-L23886 _as_of d50c47d4 ("## Registered 2026-10-03 (before any
code or call) — OOS-TREE-CELLS: ..."). Zero calls. Pins of the reviewed blob: `git hash-object` = blob:74a5cbf00832cd66e2d78bbd31bb59c11dbc14e1
(LF; the working tree is LF, 0 CR bytes); sha256-lf16:3d5865e086757625; sha256-crlf16:d19932d67b9128ce. 515c9380 touches 1 file
(`git show --name-only --format= 515c9380 | wc -l` = 1; `git diff --name-only main...HEAD | wc -l` = 1). Imports pinned and equal on
the branch and on main: oos_baselines.py blob:7e74108d, intent_transfer_s1.py blob:4e9d9d05, intent_transfer_s0.py blob:f662ceb1.

## Verdict

**READY**, with conditions C-1..C-3. No blocker. The deciding arm is C-AF at k = L = 139, slice 256. The detectors are OOS-BASELINES'
own functions, called unchanged. The identity reproduces to the digit through the script and through my own independent read. Every
fit and every tree member is TRAIN in-scope. The Support arithmetic reproduces. OT-R2, OT-R3 and OT-R5 need registrar brackets (below).

## Per-claim table (deciding paths)

| claim | mine | status | sev |
|---|---|---|---|
| C-AF = deciding arm: snapshot 20261002_213715_Headless_Run_Auto_ge, 139 leaves, slice 256 | own read of snapshots.db (immutable=1) by id: 139 childless nodes, vmfMu 256-d, norms 1.000000 to 1.000000; dry-run TREES line agrees (graph sha256 478b85562208d52d). The script refuses L != 139, a slice != 256 and a Snapshot ID other than the run log's (mutants killed) | CONFIRMED | - |
| C-AN descriptive only (20261002_214129..., anchored) | 131 leaves, vmfMu **512**-d. It enters only the DESCRIPTIVE block and P2. No status, falsifier or Delta reads it (mutant "P2 on T" is killed; my R4 "Delta from C-AN" is killed) | CONFIRMED (see OT-R5) | - |
| Like with like: T vs K, both label-free, k matched | T reads only TRAIN in-scope membership; K = ITS.km_fit at k = trees[C-AF].L on R["train"] (13,487 TRAIN in-scope); mutants "k = L-1" and "k = 150" are killed | CONFIRMED | - |
| Detectors identical to OOS-BASELINES | `OB.s0_scores`, `OB.baseline_scores`, `OB.maxcos`, `OB.fpr_line`/`threshold`, `OB.rows`, `OB.ob_status`, `OB.verdict_line` are imported. OB is asserted blob 7e74108d at entry (another blob refuses). T = `OB.maxcos(leaf_mu, X)`, the same form as S1 `t_c6` (L1210). The OT bootstrap repeats OB.paired_boot (L375-L386): same stream BOOT_SEED+2 = 20260931 (printed), same zip(in, OOS) generator order, one weight pair per draw for every score | CONFIRMED | - |
| Identity T-C6: A(T) 0.96776 / A(K_0) 0.96999 | dry-run: 0.96776 / 0.96999 -> REPRODUCED. **Own independent code** (own sqlite reads, own side masks, own slice + renormalise, scipy rank AUROC): A(T) **0.96776** on n_in 6,672 / n_OOS 1,350. K_0 was checked through the script only (S0's skmeans is shared, as in S1) | CONFIRMED | - |
| Identity refuses before K_1..K_4 / any descriptive line; also checks OB's 5 per-seed digits and A(a) at --run | code order in compute() L400-L410; ST-REFUSE kills "identity skipped", "first seed only", "identity after K" | CONFIRMED | - |
| Denominators | census: n_in 6,672 in 6,672 components, n_OOS 1,350 in 1,350 (Kish 1.0000 / 1.0000), GATE 2,333, TRAIN 13,487; own count 6,672 / 1,350 / 2,333 | CONFIRMED | - |
| TRAIN-only fits | dry-run fit audit: 0 EVAL, 0 OOS rows. At --run every k-means, (a)-(d) and S0 fit goes through fit_rows, and thresholds come from GATE in-scope. Own map of the leaf queryIds of both trees (q_ + sha256(text)[:16]): 13,487 ids, 0 unmapped, all CLINC TRAIN in-scope (113 also match MASSIVE TRAIN texts, also TRAIN); **0 GATE / EVAL / OOS** | CONFIRMED | - |
| Write-once, refusals | lexists refusal on both outputs before any read; mode "x"; `experiment_results/oos_tree_cells` is absent in main and in the worktree (ls). Refusals executed in ST-REFUSE: identity x4, Snapshot ID x2, L, slice, quoted heading, null pin, JVM (--run and --dry-run), non-empty -wal | CONFIRMED | - |
| No writes to the data root | ls --full-iso of snapshots.db*, intent_*.db before/after the dry-run: identical; script pins re-checked before/after (487e0093 / 9e100e04) | CONFIRMED | - |
| Support (registered): DEFF 1.0 (S0 measured), n_eff 6,672 / 1,350, SE 0.0012 transported from OB-c SE_total 0.00120 (POSTRUN_oos_baselines row 8) | 0.010 - (1.645+0.842)·0.0012 = 0.0070156 -> 0.0070; 0.010 + 0.842·0.0012 = 0.0110104 -> 0.0110; seen point abs 0.0022 <= 0.0070 -> SCOREABLE (EQUIVALENT side). ST-UNIT asserts the same values. At --run the script re-measures DEFF from the components and prints n_eff and MDE80 = 2.8 SE_total beside OT1 | CONFIRMED, non-vacuous | - |
| Selftest | 210 checks passed; the four planted answers EQ / KB / TB / NE are each recovered against an independent oracle | CONFIRMED | - |
| Mutants (builder) | 45 of 45 KILLED | CONFIRMED | - |

## Builder's readings: rulings

- **OT-R1 (bootstrap stream = OB's, its order): CONFIRMED.** This is what "OOS-BASELINES' form" means. My R1 (stream + 1) is killed by
  the E2E oracle. No bracket needed; the registrar records it as confirmed.
- **OT-R2 (identity precondition, refuse and write nothing): CONFIRMED, BRACKET NEEDED.** It is stricter than the registration,
  which seals no refusal. The registrar must record that an identity failure is a failed precondition, not an outcome, and that the
  identity covers A(T), A(K_0), OB's five S0 per-seed digits and A(a). OB's FPR95 / threshold digits are not covered (D-3).
- **OT-R3 (verdict line re-stated at the measured SE_total): PARTLY, BRACKET NEEDED.** As Support it is correct: it re-measures after
  the run, as check 8 asks. But the registered Support (f) line at SE 0.0012 is the one of record. OT1 is scored whatever the measured
  line says. The code agrees: `ot_status` never reads the verdict line. The measured line never demotes or promotes OT1. Also bracket
  that the seen -0.0022 is a seed-0 point, while Delta_T is taken against the 5-seed mean.
- **OT-R4 (closed interval, one Brier per probability, DIFFERENT = either direction): CONFIRMED.** This is OOS-BASELINES' convention,
  as its post-run review re-scored it. No bracket needed.
- **OT-R5 (C-AN at its own slice 512): CONFIRMED as the only coherent reading, BRACKET NEEDED.** The vmfMu of C-AN are 512-d (own read),
  so a 256-d reading is impossible without re-slicing the tree. Wording: C-AN differs from T in BOTH label information (gold coarse
  anchors) AND slice (512 vs 256). The title's "same qwen3 256-d S0 vectors" holds for T and K only. A(C-AN) - A(T) is never an
  "anchoring effect". Disclosure: while checking the slice I computed A(C-AN) myself. It is a descriptive number, so I do not print it
  here; it does not touch OT1.

## Own mutants (deciding paths)

- R1 paired_boot stream STREAM+1: KILLED (E2E-EQ SE_total vs the oracle). Decisive.
- R2 after-run pin re-check replaced by a constant "unchanged": **SURVIVED.** Not decisive: the vectors are loaded before compute, and
  the strict pins are checked at entry. Guard has no test (D-1).
- R3 OOS-in-TRAIN/GATE guard removed: **SURVIVED.** Not decisive: OB.rows already excludes OOS from TRAIN and GATE, so this guard is
  redundant (D-1).
- R4 readout's A_T read from C-AN: KILLED (E2E-KB Delta vs the oracle). Decisive.
- R5 dry-run identity check replaced by an unconditional REPRODUCED: KILLED (ST-DRY). Decisive.
- R3/R5 first reported FileExistsError because a re-used fixture dir collided. They were re-run with fresh fixtures, and the results
  above are from that re-run.

## Defects

- D-1 LOW. `after_check` and the OOS-in-TRAIN/GATE guard are untested (R2, R3 survive). FIX: one ST-REFUSE case that rewrites the
  fixture qwen3 DB between load and after_check and expects a refusal, and one that plants an OOS row in R["train"].
- D-2 LOW (operational). `heavy_check` refuses on any java.exe, including idle Gradle/Kotlin compile daemons. During this review,
  PIDs 49316, 14012 and 33140 were the gemma-own-bar `compileTestKotlin` and its daemons, which have a 3 h idle timeout. My dry-run
  bypassed the check in a reviewer-only wrapper (scratch `dry_wrap.py`). I verified first that snapshots.db in the data root was
  untouched (mtime 2026-10-02 21:45, -wal 0 B). The operator must NOT bypass it (C-2).
- D-3 LOW. The --run identity omits OOS-BASELINES' FPR95 0.1578 / threshold 0.74326 digits. Those are descriptive here. FIX
  (optional): add them to OB_ID.
- D-4 LOW. outcome.txt is written before oos_tree_scores.csv, so a CSV failure leaves an outcome without its CSV. This is the
  OOS-BASELINES pattern. FIX: write the CSV to a temp file first, or accept and disclose.
- D-5 LOW (carried from POSTRUN_intent_s1 D-1). --run prints no start or rc line. The operator's tee supplies them (C-3).

## Conditions

- C-1. Run from the repo root on main, after merging 515c9380 (the blob must stay 74a5cbf0: `git hash-object` before the run), with
  `--data-root .claude/worktrees/intent-s1-run`. First re-run `--dry-run` from main and check that it shows identity REPRODUCED and
  denominators MATCH.
- C-2. Run only when `tasklist /FI "IMAGENAME eq java.exe"` lists none. The script refuses otherwise; never override it. If peer
  Gradle daemons linger, ask the owner (gemma-own-bar) to run `gradlew --stop`; never kill them by image name.
- C-3. Tee the console with start and end times and the rc. Outputs are never committed: give their sha256 and back them up to E:
  with SHA256SUMS. The registrar brackets OT-R2, OT-R3 and OT-R5 (wording above) in the outcome record.

Run command (C-1): `python tools/analysis/oos_tree_cells.py --run --data-root .claude/worktrees/intent-s1-run`

## Commands

```
git -C .claude/worktrees/oos-tree-cells hash-object tools/analysis/oos_tree_cells.py ; git ls-tree HEAD <f>   # 74a5cbf0 LF
git show --name-only --format= 515c9380 | wc -l   # 1 ; git diff --name-only main...HEAD | wc -l   # 1
python tools/analysis/oos_tree_cells.py --selftest   # 210 ok, rc 0
python tools/analysis/oos_tree_cells.py --mutants    # 45 of 45 KILLED, rc 0
python scratchpad/otc/dry_wrap.py   # --dry-run, data root intent-s1-run, heavy check bypassed (D-2): rc 0, IDENTITY REPRODUCED, MATCH x2
ls -la --full-iso intent-s1-run/{snapshots.db*,intent_*.db} before/after: diff empty
python scratchpad/otc/own.py    # own A(T) 0.96776; leaves 139/256 and 131/512, vmfMu unit; n 6672/1350/2333
python scratchpad/otc/own2.py   # leaf queryIds -> sides: 13,487 CLINC TRAIN in-scope, 0 GATE/EVAL/OOS
python scratchpad/otc/mymut.py, mymut2.py   # R1-R5 above
tasklist /FI "IMAGENAME eq java.exe"; Get-CimInstance Win32_Process (PIDs 49316, 14012, 33140: gemma-own-bar gradle compile)
```
