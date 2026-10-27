# READY review: GRANULARITY-GT + HIER-F addendum (one readout)

Reviewer: adversarial-reviewer, 2026-10-04. Zero calls. Branch `granularity-gt` tip dd991a81 (parent 75aec903, fork
b66b075d; 633255f2 is NOT an ancestor, the branch adds one new file only). Reviewed blob
`tools/analysis/granularity_gt.py` **blob:bcb4240de6963fd24960b58ce5143087ba7a5025 (LF)**, working tree LF (0 CR bytes;
`git hash-object` = blob), sha256-lf16:3a9a38fc29c8012b. Instrument `intent_transfer_s1.py` blob:4e9d9d05 (LF), equal on
main and branch. Registrations: prog L24317-L24328 (GRANULARITY-GT, b66b075d) and L24430-L24441 (HIER-F, 633255f2),
headings re-grepped on main at 780d4837.

## VERDICT: READY (blob bcb4240d), on conditions

- **R-1 (registrar, pre-data, before the run)**: brackets B1-B5 below. B1-B3 touch deciding paths or scored predictions;
  the run may go once B1-B3 are bracketed (or the registrar states it accepts the builder's readings verbatim).
- **R-2 (post-run reviewer duty, HIGH)**: recompute GR1/HF1 `spread_B` from the per-seed prints and the two percentile
  intervals with an independent component bootstrap; the selftest does not pin these (mutants R1-R3, R9 survive).
- Run from the worktree (or main after a merge that keeps the blob); temp under E:/TaxoArena_tmp (scratch_dir imported).

## Deciding claims

| # | claim | my evidence | result | sev |
|---|---|---|---|---|
| 1 | Data object: M-AF / C-AF chosen by the run log's single `Snapshot ID:`, not the latest row | logs: 1 distinct ID each (20261002_211806 / 20261002_213715); snapshots.db holds 219 rows, last 20261002_214525; neither tree is the last row | CONFIRMED | - |
| 2 | Trees: 84 / 139 leaves, D_max 8, k_d M [2,6,12,24,46,66,80,84], C [3,6,13,26,50,86,123,139] | own walk over `parentIds` (not the S1 BFS): identical to the digit; 76 / 130 internal nodes (near-binary: fan-out 2 on 70/76, 123/130), multi-parent 0 | CONFIRMED | - |
| 3 | EVAL census 4,946 / 4,923 (MASSIVE), 6,672 / 6,672 (CLINC); within 5% of registered | own count on arm sides salt 1: identical | CONFIRMED | - |
| 4 | Support (registered): DEFF 1.0093 (Kish, S0), n_eff ~4,900, SE 0.35/sqrt(4,900) = 0.0050, MDE80 0.014 | own Kish from component sizes: M 1.0093 (max comp 2), n_eff 4,900.4, SE 0.00500, MDE 0.0140; C Kish 1.0000, n_eff 6,672, SE 0.00428, MDE 0.012 (CLINC's carried 1.0093 is conservative) | CONFIRMED arithmetic; SD 0.35 source unnamed (D3) | MEDIUM |
| 5 | Verdict lines: GR1 / HF1 DESCRIPTIVE-ONLY at the prediction; GR2 / HF2 SCOREABLE (percentile) | 0.01 < 0.014 MDE; run prints realised Kish, n_eff, bootstrap SE, MDE80 beside D1 and D, MC SE beside p97.5 | CONFIRMED (non-vacuous; post-run DEFF re-measured by construction) | - |
| 6 | Level-wise AMI and best cut vs both gold levels (G1, G3) | code L291-L308, L703-L708: tree cuts d = 1..D_max, shallow leaf stays itself, AMI = sklearn (ST-AMI, M01-M03 killed); coarse decides, fine DESCRIPTIVE | CONFIRMED | - |
| 7 | Comparators cut at the tree's k_d (avg-link replay, bisecting seeds 0-4, matched-shape random trees) | L338-L376 (replay of last L-1 merges; frontier = undo last k-1 merges); L387-L422; L429-L437. Own mutants R4 (k off by one), R6 (euclidean) KILLED | CONFIRMED; matched-k is a READER'S choice the text does not fix (B1) | HIGH (bracket) |
| 8 | GR1 rule and spread_B on the coarse best cut | code L565-L578 verbatim to the text; executed on the selftest fixtures: spread_B = coarse range (0.3787 / 0.0404 / 0.2975 / 0.0772) and differs from the fine range (0.0687 / 0.0785) | CONFIRMED by execution; untested by the selftest (R1 survives) | HIGH (R-2) |
| 9 | GR2: DP coarse vs 200 matched-shape permutations, p97.5 strict | L731-L741; M10-M15 killed; R5 (items shuffled instead of leaves) KILLED | CONFIRMED | - |
| 10 | HF = sum_c (n_c/n) max over every node F(c, v); taxonomic P/R; ancestor-F1; FM level-wise | L470-L553: F = 2 n_cv/(n_v + n_c) over the full node set incl. leaves and root; H01-H17 killed | CONFIRMED (H2-H4 are readings, DESCRIPTIVE: B4) | LOW |
| 11 | HF1 per corpus, D on fine gold, spread_B = bisecting fine-HF range | L783-L795; fixture execution: HF spread = fine range (0.0467 / 0.0450) not coarse (0.2558 / 0.0036) | CONFIRMED by execution; R2, R3 survive | HIGH (R-2) |
| 12 | HF2 read on fine gold | text lists "the coarse gold level" under DESCRIPTIVE (L24435): fine is the only deciding level; supported | CONFIRMED | LOW (B2) |
| 13 | GG-1: P1 "GR1 NEITHER 0.6" names no outcome of GR1's overall rule; printed NOT SCORED | L24325 overall outcomes are TREE-BETTER / AVG-BETTER / MIXED; NEITHER is per-corpus only; render L914 prints NOT SCORED; M42 killed | CONFIRMED defect of the registration | MEDIUM (B3) |
| 14 | HIER-F P1 "HF1 NEITHER 0.60" scored per corpus (two Briers) | HF1 has no overall rule (L24435); render L973-L975 | CONFIRMED as a reading; needs a bracket | MEDIUM (B3) |
| 15 | MMLU-Pro re-draw arm not built; HF P3 NOT EVALUATED | registered DESCRIPTIVE (L24432, L24435); render L978; no pool reader in the blob | CONFIRMED; omission of a registered descriptive arm | LOW (B5) |
| 16 | TRAIN-only fits; EVAL after the freeze | every fit through S1.fit_idx (refuses EVAL/GATE/OOS/dropped); M18/M19 killed; EVAL texts in TRAIN texts = 0 (both corpora) | CONFIRMED; R7 (unlock before the TRAIN phase) survives, no leak path (train_phase never reads EVAL) | LOW |
| 17 | Write-once outcome + SHA256SUMS, nothing written by dry-run | pre-check L1013-L1015, mode `x` L1034/L1036; M31/M32 killed; dry-run printed "0 files written" | CONFIRMED | - |
| 18 | No writes to DBs of record | pins re-hashed after the readout (strict); dry-run PIN OK on ingest 487e0093... and intent_emb_qwen3 9e100e04...; snapshots.db mtime Oct 2 21:45 unchanged, -wal 0 bytes | CONFIRMED | - |
| 19 | "Same TRAIN items" for avg-link / bisecting | MASSIVE: comparators fit on 9,870 TRAIN ROWS = the tree's 9,826 texts + 44 duplicate-text rows (CLINC 13,487 = 13,487) | PARTLY | LOW (D2) |

## Registrar brackets needed (pre-data; nothing has run)

- **B1 (HIGH, deciding)**: GR1's comparator best cut = max over the tree's k_d (matched-size cuts, G1); the avg-link
  best over every k in 2..L is DESCRIPTIVE. The text says "best-cut AMI per level" only; an all-k reading could flip GR1.
- **B2 (LOW)**: HF2 on the fine gold (H1); the coarse HF DESCRIPTIVE.
- **B3 (MEDIUM, scored predictions)**: GG-1: choose (a) P1's event = "NEITHER on both corpora" (overall MIXED by double
  NEITHER), or (b) NOT SCORED as printed. HIER-F P1 "HF1 NEITHER 0.60": per-corpus event, two Briers (H5).
- **B4 (LOW)**: H2 (node labels = TRAIN plurality), H3 (ancestor-F1 by best-F-node containment), H4 (B_k for avg-link
  and bisecting seed 0; the tree at its k_d only) as the readings of record for the DESCRIPTIVE metrics.
- **B5 (LOW)**: the MMLU-Pro re-draw arm (HIER-F DESCRIPTIVE, P3) not built: NOT EVALUATED; any later build is a
  separate pool-reader step under rule 7.

## Defects (with fixes)

- **D1 (HIGH, test gap, carried as R-2)**: the selftest asserts D1, DP and p97.5 against independent computations but
  not `spread_B` (GR1, HF1) nor `lo` / `hi`. Fix (optional now; a new blob needs a delta review): add E2E asserts of
  spread_B against an independent coarse / fine-HF range and of the interval against a re-implemented bootstrap at
  B 60. Otherwise the post-run reviewer recomputes both (R-2).
- **D2 (LOW)**: MASSIVE comparators weight 44 duplicate-text TRAIN rows twice; the tree's build deduplicated them.
  Effect on an average-link / bisecting hierarchy over 9,826 points is negligible (identical vectors merge at distance 0);
  disclose in the outcome note or dedupe by text.
- **D3 (MEDIUM, Support source)**: the planning SD 0.35 is called "pilot" but no pilot exists; DEFF has its source
  (Kish, S0, re-measured here). The run's bootstrap SE replaces it; the registrar should name it a planning assumption.
- **D4 (LOW, interpretability)**: under a leaf permutation the leaf nodes' item sets are unchanged, so HF2 measures
  only classes whose best node is internal. Print (DESCRIPTIVE) the count of fine classes whose best node is internal
  for the tree and the random median; the post-run reviewer should report it from the run.
- **D5 (LOW)**: the trees are near-binary (internal 76 vs 83, 130 vs 138 for a binary tree), so the node-count advantage
  of the binary comparators in max-over-nodes HF is small; no action needed.

## Mutants

Builder suite re-run: **69 of 69 KILLED** (47 GR + 22 HF). Selftest: **OK, 264 value checks** (docstring says 201: stale count, LOW).
Own mutants, full selftest each:
- R1 spread_B from bisecting FINE best cut: SURVIVED (decisive; code correct by execution, row 8)
- R2 HF spread_B from bisecting COARSE HF: SURVIVED (decisive; code correct by execution, row 11)
- R3 HF1 bootstrap on coarse gold (point on fine): SURVIVED (decisive; code L789-L790 reads gf / Kf)
- R4 matched-k off by one in frontier_cut: KILLED
- R5 HF2 null shuffles items instead of leaves: KILLED
- R6 average-link euclidean: KILLED
- R7 EVAL unlocked before the TRAIN phase: SURVIVED (not decisive; no EVAL read in train_phase)
- R8 P3 event on the fine best depth: KILLED
- R9 GR1 bootstrap keeps the point's best cut (not re-chosen): SURVIVED (decisive for the interval; code L719-L721 re-chooses as G4 states)

## Commands (no java running at each step; one foreign python, a peer's selftest, light)

```
git rev-parse granularity-gt; git show dd991a81:tools/analysis/granularity_gt.py | git hash-object --stdin   # bcb4240d
git -C .claude/worktrees/granularity-gt hash-object tools/analysis/granularity_gt.py tools/analysis/intent_transfer_s1.py
git diff --name-only main...granularity-gt | wc -l                         # 1 (the script only)
python tools/analysis/granularity_gt.py --selftest                         # SELFTEST OK: 264 value checks (8 s)
python tools/analysis/granularity_gt.py --mutants                          # 69 of 69 KILLED (55 s)
python tools/analysis/granularity_gt.py --dry-run --data-root ../intent-s1-run   # PIN OK x2; census; snapshots; k_d; 0 files written
python E:/TaxoArena_tmp/rv_ggt/kd.py          # own k_d / leaves / fan-out from parentIds, immutable=1
python E:/TaxoArena_tmp/rv_ggt/tr.py          # TRAIN rows vs build texts (9,870 / 9,826), EVAL-TRAIN text overlap 0, Kish / n_eff / SE / MDE
python E:/TaxoArena_tmp/rv_ggt/spread_chk.py  # fixture run(): spread_B coarse / HF fine by execution
python E:/TaxoArena_tmp/rv_ggt/mymut.py       # R1-R9
grep -ao 'Snapshot ID: *[A-Za-z0-9_]*' .../s1/{m_af,c_af}/seed_42/headless_run.log | sort | uniq -c
```

Run command of record (plain form, from the worktree root `.claude/worktrees/granularity-gt` once R-1 is bracketed):
`python tools/analysis/granularity_gt.py --run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena/.claude/worktrees/intent-s1-run`
(default out-dir E:/TaxoArena_backup_<date>_granularity_gt; write-once; outputs never committed).
