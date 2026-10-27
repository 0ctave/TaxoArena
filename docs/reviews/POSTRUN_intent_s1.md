# POSTRUN review: INTENT-TRANSFER-S1 readout (blob 4e9d9d05, main cdddc896; DATA_ROOT .claude/worktrees/intent-s1-run). Zero calls.

Reviewer: adversarial-reviewer, 2026-10-03. Prior reviews: READY_intent_s1.md and READY_intent_s1_delta.md.
Objects read (read-only, `mode=ro&immutable=1`; the run's snapshots.db -wal is 0 bytes; no java running):
experiment_results/intent_transfer/s1_outcome.txt and s1_items.csv, ops_20261003/readout.log and build_m_af_g.log, the
run's snapshots.db rows by Snapshot ID, intent_emb_qwen3.db, intent_transfer_corpora_v1.db.

## Verdict

**VALID.** Every deciding number reproduces to the printed digit (table). The outcome was written once. C-2 holds: M-AF
reproduces 0.834 / 0.692. N1 is correctly not triggered, so the positive branch may be written, with the qualifiers W-1
to W-3 below. F-S1b FIRED, but only against a label-conditioned comparator (W-4). M-AF-g's 4 leaves are a real outcome
of the recipe, not a setup fault (Q-1).

## Deciding numbers (own script `is1/post.py`: own flatLeaf, majority, NMI (sklearn), DP, LCA, Mantel; S0.skmeans / c4_variants / comp_weights reused)

| Readout | Outcome | Mine | Status |
|---|---|---|---|
| P0 | HOLDS, 160/160 nodes, 0 queryIds sets differ | ids equal, 0 differ | CONFIRMED |
| flatLeaf in s1_items.csv | - | 4,946/4,946 (M-AF), 6,672/6,672 (C-AF) agree | CONFIRMED |
| T-C1 MASSIVE | D1 +0.00037 (0.76126 - 0.76090), spread_K 0.01874, delta_c 0.01745; TOST [-0.00371, +0.00444] | +0.00037, 0.01874, 0.01745 (GATE: sup 0.85908, km 0.78927); TOST from the printed SE_total: [-0.00371, +0.00445] | CONFIRMED, EQUIVALENT |
| T-C1 CLINC | D1 +0.00718 (0.92862 - 0.92143), spread_K 0.01068, delta_c 0.01246; TOST [+0.00440, +0.00997] | +0.00718, 0.01068, 0.01246; [+0.00440, +0.00996] | CONFIRMED, EQUIVALENT (not GAIN: 0.00718 < bar 0.01068) |
| T-C1b | P_tree 0.87242 / 0.94140; D13' -0.03558 / -0.04032 | P_tree 0.87242 / 0.94140; D13' = P_tree - printed P(KC_0) = -0.03559 / -0.04031 (rounding; KC from G13, not re-fit) | CONFIRMED, FAILED x2 |
| T-C2 MASSIVE | D2 +0.06319 (0.67043 - 0.60724); spread_o 0.00000 | +0.06319; M-o1 0.67033 - 0.60714 = +0.06319; M-o2 +0.06319 | CONFIRMED (spread vacuous: W-2) |
| T-C7 | D7 -0.00892 (0.69119 - 0.70011); ceiling 0.83426, floor 0.69243, delta 0.03546; spread 0.01428 | identical to 5 dp | CONFIRMED, EQUIVALENT; **C-2: 0.834 / 0.692 reproduced** |
| T-C9 | thr 0.01650, abstained 627, D9 +0.36709 | 0.01650, 627, +0.36709 | CONFIRMED, HELD |
| T-C8 | +0.07258 [+0.06313, +0.08198] / +0.07689 [+0.06939, +0.08408]; P_flat 0.78104 / 0.82674; P_descent 0.70845 / 0.74985; 0 unrouted | identical, CI with the same bootstrap streams | CONFIRMED, HELD x2 |
| T-C4 | r +0.1688 / +0.1651, p 0.00010 | r identical; own 2,000-permutation p 0.0005 = 1/2001 (no draw at or above r) | CONFIRMED (HELD; DESCRIPTIVE-ONLY per N2) |
| N1 | no LOSS flag | T-C1 MASSIVE D +0.00037 > -0.01874; T-C7 -0.00892 > -0.01920; no joint LOSS | CONFIRMED, positive branch not blocked |
| Support | n / G 4,946 / 4,923; 6,672 / 6,672; 3,222 / 3,207 | as in READY_intent_s1 | CONFIRMED |

Bootstrap SEs other than T-C8's were taken as printed. TOST intervals were recomputed from those SEs.

## Write-once and console

There is exactly one `outcome written` line in readout.log. s1_outcome.txt and s1_items.csv share mtime
2026-10-03 04:05:52, and no other `s1_*` file exists under either data root (count 0). The code writes with mode `x`
after an `lexists` refusal. The outcome header carries blob 4e9d9d05 = the cdddc896 tree entry. Pins were re-checked
after the run and are OK (console). D-1 is a console gap.

## Q-1: M-AF-g (4 leaves): a real result, not a setup fault

Inputs are correct. 9,826 TRAIN + 1,676 GATE rows, 0 EVAL. "All 9826 requested embeddings are already cached" from the
pinned gemma working copy; slice 768 = EMBED-DIM-SLICE's d_g* 768; dimension check passed; pins OK; GATE descent
acceptance 1,676/1,676.

The construction runs. The root split k=3 is accepted (z 45). The 5,837-item child never clears the qwen3-calibrated
bar ("NO-SPLIT reason=min-pair sep=0.0152 / 0.0140 bar=0.0250"). The other split proposals are rejected on dJ < 0.
Leaf sizes: 1,139 / 1,416 / 1,475 / 5,837.

Reading: the AF recipe's separation bar (0.025, calibrated at qwen3 256) does not transfer to gemma at 768. Its rows
(k = 4 matched k-means, km NMI 0.42) say nothing about gemma's intent resolution. Their "EQUIVALENT" must never be quoted
as embedder parity (registered: gemma rows descriptive).

## Predictions (re-scored from the rule; the outcome's lines agree)

- P1 leaves: M-AF 84 vs [25, 50] MISSED high; C-AF 139 vs [60, 110] MISSED high; M-AN 82 and C-AN 131 HELD. The design
  prior under-predicted the AF leaf count at about 10-13k TRAIN items. Leaves scale with TRAIN size (SPLIT-RATIO): about
  9.9k TRAIN gave 84 leaves, close to af_clean_s42's 82 on MMLU-Pro.
- Numeric bands: 8 of 13 HELD (counted). Misses: P1 x2; P3 CLINC -0.04032, just below -0.040; P4 +0.063 > +0.050;
  P7 MASSIVE +0.0726 > +0.060.
- P8: r 0.17 / 0.17 against points 0.35 / 0.30 (about half). P9 event false (MASSIVE slope -0.011).
- Briers as printed (P0 0.0100 ... P9 0.6400).

## Registrar's wording (like with like on label information)

- **W-1 (positive branch, may be written as registered).** It compares label-free with label-free (AF tree vs k-means at
  matched k), so the comparison is like with like. Append: "(leaves 84 / 139; one draw; qwen3 256; RAW)".
- **W-2 (T-C2 HELD).** Write: "HELD on the interval; the spread clause was vacuous: the order-shuffle arms rebuild M-AF's
  leaf partition (M-o2 identical, M-o1 near-identical; spread_o 0.00000), as E1-REPLICATES found (061a2418 B-1)". The
  tree's hierarchy beats average-link on the same leaves (DP 0.670 vs 0.607; random p95 0.298). Both sides are label-free.
- **W-3 (T-C7 R).** The printed R (tree -0.009, km +0.054) uses the registered floor at K = 60, while the clusterers have
  84 cells. That is not like with like for R. At the floor at k = L (0.61670, descriptive, mine) R is 0.342 for the tree
  and 0.383 for k-means. The verdict is EQUIVALENT under either floor (delta 0.0355 or 0.0544). Quote R only with its floor.
- **W-4 (T-C1b / F-S1b).** The comparator is label-conditioned: gold coarse labels, k_c prototypes per class. Write: "on
  known answers the label-free tree's coarse filing (0.872 / 0.941) lies below label-conditioned per-class prototypes
  (0.908 / 0.982; -3.6 / -4.0 pp) and at or above one supervised centroid per class (0.867 / 0.855)". Never write "the
  tree files below an unsupervised comparator".
- **W-5 (T-C9).** The margin abstention works on tree leaves (D9 +0.367). It is not tree-specific: D9(tree) - D9(km) is
  +0.014 (descriptive).
- **W-6 (T-C8).** flatLeaf beats descent by 7.3 / 7.7 pp. Same tree, same label map, both routings label-free. T-C8b is
  NOT HELD: the gap does not differ between corpora.
- **W-7 (T-C4).** HELD is DESCRIPTIVE-ONLY (N2). r is about 0.17 on both corpora, half the prediction.
- **W-8 (anchored arms).** The scenario and domain anchors of M-AN and C-AN carry label information. Their EQUIVALENT
  rows against unsupervised k-means are not label-free parity and stay out of the positive sentence (memory:
  anchored-tree comparisons).

## Defects (LOW; none moves a verdict)

- D-1: readout.log has no `--run` start line or rc line; only the dry-run has them. FIX: log start, end and rc for every mode.
- D-2: the SUPPORT line prints "Kish DEFF nan, n_eff nan" for T-C9 and T-C2. The measured value is 1.0093 (variants /
  EVAL). FIX: pass the components into support_line.
- D-3 (carried from delta D-2): the M-AF-s2 / M-AF-g rows print no ceiling, floor or delta.

## Commands

```
sed -n p experiment_results/intent_transfer/s1_outcome.txt ; ls --time-style=full-iso (both outputs) ; grep -c "outcome written" readout.log
python is1/post.py      # P0, M-o1/M-o2 partitions, M-AF-g leaf sizes; T-C1, T-C1b P_tree, T-C2 (x3 arms), T-C4, T-C7 (+ floor at k=L), T-C8 (+CI), T-C9
grep "NO-SPLIT\|GROW\|cached\|SLICE" ops_20261003/build_m_af_g.log
git ls-tree cdddc896 tools/analysis/intent_transfer_s1.py      # 4e9d9d05
```
