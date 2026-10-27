# READY review: GAP-FIX (adversarial; zero calls; nothing run beyond --selftest / --mutants / --dry-run and a label-free structural check)

Reviewed: branch gap-fix, tip 8f57e85e (parent 0910e947 = main HEAD at review time; `merge-base --is-ancestor 0910e947 8f57e85e` true),
one file added (`git show 8f57e85e --name-only --format= | wc -l` = 1: tools/analysis/gap_fix.py).
Registration: docs/judge_v2_program.md L24842-L24854 (_as_of 9bff7e39), "## Registered 2026-10-06 (before any code or call) — GAP-FIX: ...".

## VERDICT: READY (no blocker)

Conditions on the run (operator): R-C1 `busy.ps1` exit 1 immediately before each `--run` (both parts are pool readers, rule 7); one part per
process (`--run --part a`, then `--run --part b`); R-C2 part (b) launched DETACHED (about 1 CPU-h) and polled; R-C3 the run is accepted only if
the IDENTITY lines read REPRODUCED ((a): T 2504 / V0 2652 of 3445, D_T -0.0430 [-0.0557, -0.0293], spread_V 0.0305, M2(T) +12.785; (b): KI1 /
U2 / RP2 as built); a refusal is a failed precondition, not an outcome; R-C4 outputs pinned by sha256 and backed up to
E:/TaxoArena_backup_<date>_gap_fix with SHA256SUMS.txt, never committed.
Post-run checks owed (post-run reviewer): PR-1 re-measure Kish / DEFF from the outcome's twin-group line (dry run: 3,445 groups, Kish 1.0000) and
print n_eff and the measured MDE80 beside D_R (registered SE 0.00663, MDE 0.0186); PR-2 set the measured I_R discordance beside the declared
0.10 (see GF-B3); PR-3 if GF1 reads OPEN or PARTIAL with 0.0186 < |D_R| <= 0.0305, re-check the word by hand (D-1); PR-4 read the WP-A line
(must equal WP at T 5, see GF-B1).

## Pins (LF of record)
| object | pin | how shown |
|---|---|---|
| tools/analysis/gap_fix.py @ 8f57e85e | blob:7c0691e8444848f3669e46d33adbfa2b7af31a20, sha256-lf16:8a15aecbe985cd97 (sha256-crlf16:2b3e4b16b66ffd32 beside; the worktree file is LF, 0 CR bytes) | `git hash-object`, `git ls-tree`; `git show 8f57e85e:<path> \| sha256sum`; `sed 's/$/\r/' \| sha256sum`; dry-run [SCRIPT] line |
| imports flat_mix_mmlu 555ae3ac, flat_generality d16f1042, key_info_v2 37f5935c, resp_profile_info 1817ec8a, union_route_common d5473976, union_af_route bf3f17db | equal at 4c764a1e (registration parent) and 0910e947; verified on import by verify_imports (dry-run [PIN] lines) | `git rev-parse <c>:tools/analysis/<f>.py` |
| V state (20 part files, 4 trees) | all 20 sha256 equal to the script's pins (dry-run [PIN] lines) | dry-run (a) |

## Per-claim table (deciding claims)
| # | claim | reviewer's result | verdict | sev |
|---|---|---|---|---|
| 1 | GF1 coded as the one registered clause (CLOSED iff UB(D_R) >= 0 AND I_R > 0 AND LB(I_R) > 0; OPEN iff UB(D_R) < 0 AND \|D_R\| > 0.0305; else PARTIAL); FAILS and F-GF as registered | gf1 / gf1_refuted / gf1_lines read; decide() passes bar = REG_A bar_open 0.0305 (constant, not re-measured: no self-calibration); X01-X07, X22 killed; own R1 SURVIVED (test gap only, D-1) | CONFIRMED (code); test gap | MEDIUM |
| 2 | D_R = M1(T-WP_5) - M1(V0), I_R = M1(T-WP_5) - M1(T as built), paired per held-out question | decide() read; X08/X09 killed; own R7 (share vs WP_0) killed | CONFIRMED | - |
| 3 | Interval = FLAT-MIX-MMLU C1's (FM.twin_boot_ci, B 1000, seed 20260926, whole stem_key groups, percentile) | paired_m1 calls flat_mix_mmlu.twin_boot_ci unchanged (blob 555ae3ac), same call as FM.paired L1003; X10 killed; own R6 (seed 1) killed | CONFIRMED | - |
| 4 | LLOYD-WP as registered: centroid = renormalised mean of current TRAIN members, emptied leaf keeps last centroid, each item to nearest centroid among leaves of its CURRENT leaf's parent's subtree, T = 5; held-out filed flatLeaf to refined centroids over ALL leaves | refine / centroids / lloyd_step / leaf_parent_masks read; OWN independent re-implementation on the REAL fit sets (no labels): partition at T 5 equal for 8125/8125, 8126/8126, 8130/8130, 8133/8133 items, WP, WP-A and GL each; own R2 (no renormalisation), R3 (mask transposed), R4 (extra pass) killed | CONFIRMED | - |
| 5 | Reading of "current leaf's parent" (per pass vs as built) | on the real data WP and WP-A differ for 0 fit items on all 4 trees at T 5: the reading does not matter (GF-B1) | CONFIRMED (moot) | LOW |
| 6 | Hygiene: refinement fits on the fit set only; held-out never in a centroid; labels only in m1_block, keys only in m2_block; fit/EVAL overlap 0 | dry-run (a): fit sets 8125 / 8126 / 8130 / 8133 = asserted; exact overlap 0 and stem_key overlap 0 on all 4 trees; X26, X27, X31 killed | CONFIRMED | - |
| 7 | Identity precondition before any verdict ((a) T/V0 hits, D_T and CI, spread_V, M2(T); (b) KI1/U2/RP2) | run_tree_a / identity_b refuse otherwise; X23, Y08 killed | CONFIRMED | - |
| 8 | Support NON-VACUOUS and its arithmetic reproduces | sqrt(0.1533/3445) = 0.006671 (registered uses recorded 0.00663; 2.8 x 0.00663 = 0.01856 -> 0.0186); sqrt(0.10/3445) = 0.005388 -> 0.00539, x 2.8 = 0.01509 -> 0.0151; DEFF 1.0, source FLAT-MIX-MMLU; measured Kish 1.0000 (3,445 groups / 3,445 questions, dry run) -> n_eff 3,445; SCOREABLE CLOSED-vs-not (0.030 > 0.0186) reproduces; CLOSED reachable at infinite n | CONFIRMED (one premise false, GF-B3) | LOW |
| 9 | (b) gating: own-source nearest leaf, identity with AF-U's recorded cell, TRAIN unchanged, cells fixed before any key | gate_core / afu_gate / run_b read; dry-run (b): 5,991 re-filed, identity held on all, 162 one-cell kept, 191 of 5,907 scored items change cell = R-KI1's 191 (223 on the 6,153-item side export); Y01-Y03 killed; own R5 (gate by recorded cell's source) killed | CONFIRMED | - |
| 10 | Selftest 63 + 27 checks pass | `--selftest` rc 0, "  ok  " lines counted: 90 (`grep -c`) | CONFIRMED | - |
| 11 | Mutants 46/46 killed | re-run: "MUTANTS: 46 of 46 killed"; `grep -c KILLED` 46, `grep -c SURVIVED` 0 | CONFIRMED | - |
| 12 | Dry runs clean, write nothing | busy.ps1 exit 1 before each; (a) rc 0, pool line p2dca first; (b) rc 0, B0-2 pool line first, gen/eval view sha256 EQUAL before/after; `ls -l --full-iso` of all root *.db* + both V-state dirs: md5 of the listing identical before/after; experiment_results/gap_fix absent after; worktree `status --porcelain` 0 lines | CONFIRMED | - |

## Own mutants (sandboxed copies under scratch_dir's E: dir; full part selftest each, not --only)
| id | change | result | decisive |
|---|---|---|---|
| R1 | decide(): OPEN bar 0.0305 -> MDE80 0.0186 | SURVIVED | yes: P2's predicted D_R -0.030 lies in (0.0186, 0.0305], exactly where the word would flip PARTIAL -> OPEN (D-1) |
| R2 | centroids: raw mean, no renormalisation | KILLED | yes |
| R3 | WP mask transposed (mask.T[z]) | KILLED | yes |
| R4 | one extra pass (loop from t = 0) | KILLED | yes |
| R5 | (b) gate by the recorded cell's source, not the declared source | KILLED | descriptive part |
| R6 | twin-bootstrap seed 20260926 -> 1 | KILLED | yes (interval digits) |
| R7 | P1 held-out share against WP_0, not T | KILLED | no (P1) |

## Defects and brackets
- D-1 MEDIUM (test gap; the code at blob 7c0691e8 is correct): no fixture drives decide() with UB(D_R) < 0 and 0.0186 < |D_R| <= 0.0305, so a
  wrong bar in decide() survives (R1). Fix: add one planted A-VERDICT case (D_R about -0.025, UB < 0 -> PARTIAL) through decide(), and a
  mutant like R1. Not a run condition (decide() reads bar_open 0.0305 from REG_A, read here); PR-3 covers the run.
- GF-B1 LOW, bracket: the registration's "ITS CURRENT LEAF'S PARENT'S SUBTREE" is read per pass (the builder's reading); WP-A is printed beside.
  On the real fit sets the two readings give identical partitions at T 5 on all four trees (0 differing items), so the registrar may record
  the per-pass reading of record without a ruling that could move the outcome.
- GF-B2 MEDIUM, bracket owed BEFORE the run: the registration's parenthetical "(the parent's and every ancestor's membership is unchanged)" is
  NOT implied by its operative clause when parents nest: an item whose parent is an ancestor of another leaf's parent can move into that
  deeper subtree. Under WP at T 5 the number of fit items whose parent changes is 65 / 39 / 169 / 190 (af_clean_s42 / af_s137 / af_s2048 /
  af_s42_o1; of 8,125 / 8,126 / 8,130 / 8,133). The tool follows the operative clause. Registrar: bracket that the operative clause governs
  (recommended; the topology is kept in both readings), or rule the strict sibling-only reading (then a code change and a delta review).
- GF-B3 LOW, bracket: Support (d)'s "discordance at most the held-out leaf-change share" is false in principle: M1 re-derives each cell's
  majority label from the label set after refinement, so an unmoved held-out item can change its hit. The SE(I_R) 0.00539 is a planning
  number only (I_R DESCRIPTIVE-ONLY on its MDE; the deciding LB(I_R) comes from the bootstrap); the tool prints the measured discordance.
- GF-B4 LOW, readings to record: P5 uses the MEASURED D_T,M2 = M2(T) - M2(V0) as the base, not the recorded -1.534e-3 (the M2(V0) digit is not
  in the identity check; print both); R-A1 starts from the flatLeaf filing of the fit set, not the graph's queryIds membership (agreement
  printed, descriptive); P1 / P4 / P6 as in the docstring (P1 against T as built; P4 GL at T 5; P6 I_R(T 5) > 0 on each re-draw).
- D-2 LOW: part (b)'s header (resp_structure_common.prelude, not this blob) labels the LF sha256 "sha256-crlf16/working-tree bytes"; quote the
  pins from this review / the (a) [SCRIPT] line, not that label.
- DISCLOSURE: the reviewer's structural check computed TRAIN-side move shares (no labels, no held-out, no statistic): af_clean_s42 at T 5,
  WP 0.0164, GL 0.1682 of the fit set. P1 (held-out) was registered before; nothing was changed.

## Commands (cwd = main checkout unless noted)
```
git merge-base --is-ancestor 0910e947 8f57e85e; git show 8f57e85e --name-only --format= | wc -l          # 1
git hash-object .claude/worktrees/gap-fix/tools/analysis/gap_fix.py; git ls-tree 8f57e85e tools/analysis/gap_fix.py
git show 8f57e85e:tools/analysis/gap_fix.py | sha256sum ; ... | sed 's/$/\r/' | sha256sum                   # lf16 / crlf16
for f in <6 imports>; do git rev-parse 4c764a1e:tools/analysis/$f.py 0910e947:tools/analysis/$f.py; done
python tools/analysis/scratch_dir.py --run -- python tools/analysis/gap_fix.py --selftest     (worktree)    # rc 0; 90 ok
python tools/analysis/scratch_dir.py --run -- python tools/analysis/gap_fix.py --mutants      (worktree)    # 46 of 46
powershell -NoProfile -File E:/TaxoArena_tmp/busy.ps1                                                        # exit 1
python .claude/worktrees/gap-fix/tools/analysis/gap_fix.py --dry-run --part a|b --data-root <main>         # rc 0 each
ls -l --time-style=full-iso *.db* experiment_results/flat_mix_mmlu/state experiment_results/flat_generality/state/* | md5sum   # before = after
scratch: struct_check.py (own Lloyd loops on the real fit sets vs gap_fix.refine; parent-change counts), my_mutants.py (R1-R7);
         under the session scratchpad, not committed
```
