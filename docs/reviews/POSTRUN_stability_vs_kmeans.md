# POSTRUN review — STABILITY-VS-KMEANS (2026-10-05)

Reviewed: outcome `E:/TaxoArena_backup_2026-10-05_stability_vs_kmeans/stability_vs_kmeans_outcome.txt`
(sha256 eb1118a764da53bb..., 41 lines, equal to lines 2-42 of `E:/TaxoArena_tmp/svk_run.log`, rc 0). Script
blob:a67bbf0a673cffabd7dccdced95b23b11a4ac01b (LF, of record; `git rev-parse 6cd3509f:<path>` and `git hash-object`
of the working file both give it), the blob the READY delta (6bb2cfc3) passed. Registration prog L24625-L24637 with
the B-1 brackets (05987e4c). Zero calls.

## VERDICT: VALID. ST1 NEITHER (correctly derived); F-ST FIRED. The F-ST attribution clause must be bracketed (W-1)

The data object is right: |C| 2,772, the four re-draw trees, M_r 8125/8126/8130/8133, k_r 82/79/81/81,
m_r 68/63/65/68, and the identity check OK. My own scripts reproduce every deciding point to the digit and the
bounds to within 0.002. The ST1 word follows from the four upper bounds. What does not stand is the outcome's
explanation of why F-ST fired (W-1).

## Per-claim table (deciding claims)

| # | claim (outcome) | result | mine vs claimed | sev |
|---|---|---|---|---|
| 1 | tree mean 0.0683, BKM 0.0570, D_BKM +0.0113 | CONFIRMED to the digit | recheck.py: tree all 0.0683, BKM 0.0570, D +0.0113 | - |
| 2 | KM-AL 0.2814, D_KM-AL -0.2131 | CONFIRMED to the digit | 0.2814, -0.2131 | - |
| 3 | RB: tree 0.0244, D_RB_BKM -0.0320, D_RB_KM-AL -0.2562 | CONFIRMED to the digit | 0.0244; -0.0320; -0.2562. The six tree RB values equal the bracket's (0.0329 ... 0.0091) | - |
| 4 | option (b): tree 0.1401, D +0.0830 (BKM) / -0.1415 (KM-AL) | CONFIRMED to the digit | strict convention 0.1401; +0.0830; -0.1415 | - |
| 5 | bounds: BKM D [-0.0249, +0.0419], D_RB [-0.0589, -0.0047]; KM-AL D [-0.2650, -0.1580], D_RB [-0.2990, -0.2042] | CONFIRMED (to within 0.002) | boot.py: own re-draw + seed bootstrap, other RNG, triplets fixed (triplet SD 0.0006-0.0009). BKM D [-0.0257, +0.0420], D_RB [-0.0588, -0.0061]; KM-AL D [-0.2636, -0.1589], D_RB [-0.2979, -0.2048]. LOO -0.0104/+0.0128/+0.0159/+0.0271 and -0.2373/-0.2120/-0.1998/-0.2032, equal to the digit | - |
| 6 | ST1 NEITHER (C-2) | CONFIRMED by hand | the four upper bounds: BKM D +0.0419 (>= 0), BKM RB -0.0047, KM-AL D -0.1580, KM-AL RB -0.2042. Not all < 0, so not MORE-STABLE. The D lower bounds are -0.0249 and -0.2650, none > 0, so not LESS-STABLE. NEITHER. Only the BKM D clause blocks; it misses by +0.042, not at the margin | - |
| 7 | P1 HELD; P2 FAILED (both bands); P4 HELD; P5 HELD | CONFIRMED | 0.2814 in [0.18, 0.40]; -0.2131 in [-0.33, -0.10]; 0.0570 not in [0.10, 0.35]; +0.0113 not in [-0.28, -0.03]; 0.0005 in [0, 0.05]; 0.0939 in [0.03, 0.20]; -0.2144 in [-0.30, 0] | - |
| 8 | P3 Brier 0.9150 | CONFIRMED | 0.65^2 + 0.70^2 + 0.05^2 = 0.9150 | - |
| 9 | P6 (C-1; not printed) | SCORED BY HAND: FAILED | D_RB_KM-AL -0.2562 in [-0.37, -0.14]: HELD. D_RB_BKM -0.0320 not in [-0.32, -0.07]: FAILED. P6 is FAILED (one of two bands) | MEDIUM (registrar) |
| 10 | F-ST text: "0.0684 vs 0.3243 is attributed to the unlike data and shape of that comparison" | REFUTED by the run's own numbers | see W-1 | HIGH (wording) |
| 11 | "realised design effect (SD ratio)^2 977.33" | PARTLY (descriptive) | this is (bootstrap SD / triplets-only SD)^2 (0.0181/0.0006)^2 ~ 910 at the printed digits. It measures the re-draw and seed clustering against iid triplets. It is not the registration's DEFF (6 pairs -> n_eff). See C-3 | LOW |

## C-3 realised Support for the RB clause (and beside D)
The reported SE is the bootstrap SD; MDE80 = 2.80 x SD; n_eff = 2 (4 re-draws).
- D_RB: BKM SD 0.0137, MDE80 0.038; KM-AL SD 0.0225, MDE80 0.063. Registered: 0.0299 / 0.084.
- D: BKM SD 0.0181, MDE80 0.051; KM-AL SD 0.0262, MDE80 0.073. Registered: 0.0333 / 0.093.
- Registration-sense DEFF re-measured for BKM D: sqrt((0.0248^2 + 0.0209^2) / n) = 0.0181 gives n = 3.2 pairs, DEFF
  6/3.2 = 1.9 (declared 3.0, so conservative). For KM-AL the 150 crossed values are dominated by seed noise
  (SD 0.079) that averages away, so the two-term formula does not apply. The bootstrap SD (0.0262) is the SE.
- Every realised SE is below the registered one, so the test was not underpowered. D_BKM +0.0113 lies 0.06 above the
  bar and on the wrong side of the predicted -0.15. A tree advantage over BKM on all triplets of more than about
  0.03 (point minus MDE) is excluded at these four re-draws.
- L-1 caveat on BKM D_RB: with the (n-1)/n lattice understatement (SD x sqrt(4/3) = 0.0158), the normal upper bound
  is about -0.001. That clause clears 0 only marginally (it does not decide ST1).

## Defects / wording duties

**W-1 (HIGH, wording; registrar's bracket) the F-ST attribution clause is contradicted by the run.**
F-ST's registered text attributes SITE-SUPPORT's 0.0684 vs 0.3243 "to the unlike data and shape of that comparison".
The run shows that neither data nor shape explains it:
- Matching shape moves KM-AL by 0.0005 (P4).
- Matching data moves it by about 0.01 (C-only binary 0.2918 against matched 0.2814).
- Against matched, shape-matched KM-AL the trees stay far more stable: D -0.213, D_RB -0.256, both intervals
  clear of 0.
What F-ST does establish:
- (i) About 0.07 of the trees' advantage was unresolved-vs-unresolved credit (B-1).
- (ii) The ~0.21-0.26 gap is a property of the baseline's construction, not of the tree: a TOP-DOWN bisecting
  k-means at the same data, leaf count and shape is as stable as the trees.
Fix: bracket the clause so that it reads: "SITE-SUPPORT's 0.0684 vs 0.3243 is not read as a tree property. On
matched data and shape the gap persists against agglomerative-on-centroids k-means but vanishes against bisecting
k-means. It reflects the baseline construction, and about 0.07 of it is unresolved-triplet credit."

**W-2 (HIGH, wording) per-baseline words of record.**
- **BKM (bisecting k-means), the deciding arm: the tree is NOT shown more stable.**
  - On all triplets: D +0.011 [-0.025, +0.042]. The point is on the wrong side and the trees are, if anything,
    slightly less stable.
  - Counting both-unresolved as disagreement: +0.083 [+0.058, +0.108]. Descriptive, but this interval excludes 0
    against the tree.
  - On triplets resolved in both: -0.032 [-0.059, -0.005]. This is a SELECTIVE comparison. The trees resolve
    about 88% of triplets jointly (unresolved 0.08-0.10 each, 0.072 in both), against 99.9% for BKM. The triplets
    the trees leave out are the ones they disagree on (depth row U 0.209). It must never be quoted alone as "more
    stable on resolved triplets" without the coverage gap.
  - By depth (descriptive): the trees match BKM at depth 1 (0.020 vs 0.023), are worse at depth 2 (0.084 vs
    0.033), and similar below.
  - Word: "On MMLU-Pro the anchor-free trees are as stable as bisecting spherical k-means at matched data, leaf
    count and shape, not more; their edge on jointly resolved triplets is bought by leaving about 12% of triplets
    unresolved."
- **KM-AL: the tree IS more stable, but against a weak baseline.** D -0.213 [-0.265, -0.158] and D_RB -0.256.
  - The orchestrator asked whether this is average-link chaining. Chaining is present but is NOT the cause
    (post-hoc, descriptive, recheck.py).
    - KM-AL's root split on af_clean_s42 peels off only 1-6 of 82 leaves (0.1%-5.9% of C). That is chaining-like
      (cf. GRANULARITY-GT C-1, although that one was item-level).
    - On the same k-means leaves, Ward linkage gives balanced root splits (16-40 of 82 leaves, 27%-51% of C) and the
      same baseline disagreement, 0.2807 (D -0.212). Complete linkage gives 0.3512 (D -0.283).
    - The instability therefore comes from agglomerating flat k-means centroids under any of the three linkages,
      concentrated in the upper levels (KM-AL depth 1 0.437, depth 2 0.480). It is not specific to average-link
      chaining.
  - Word: "The trees are more stable than agglomerative hierarchies built on flat k-means centroids (average, Ward or
    complete linkage; D about -0.21 to -0.28), but this is not a tree property: bisecting k-means matches them."
    The Ward and complete figures are post-hoc, not registered: quote them as "descriptive, review diagnostic".
- **MASSIVE (descriptive, one pair, no interval over re-draws).** Tree more stable than BKM: D -0.18 (conditional
  bootstrap [-0.29, -0.10]). The MASSIVE BKM baseline (0.276) is about 5x the MMLU-Pro one (0.057). This may be a
  corpus contrast, but one pair cannot carry it. Quote it only with "one pair, descriptive", never as a counterweight
  to the deciding MMLU-Pro NEITHER.

**C-1 (registrar) P6 FAILED** (row 9). P2 FAILED and P6 FAILED share one cause: BKM is far more stable (0.057) than
predicted (0.22).

**L-2 (LOW) SHA256SUMS.txt.** It already existed (operator, 04:59) with the correct outcome hash. I added the two
review scripts under `postrun_review/` and rewrote the file with three lines; `sha256sum -c` passes for all three.

## Commands
```
git rev-parse 6cd3509f:tools/analysis/stability_vs_kmeans.py; git hash-object tools/analysis/stability_vs_kmeans.py   # a67bbf0a both
sed -n '2,42p' E:/TaxoArena_tmp/svk_run.log | diff - <outcome> && echo LOG_EQ_OUTCOME                                  # equal
python tools/analysis/scratch_dir.py --run -- python E:/TaxoArena_tmp/svk_postrun/recheck.py   # points (rows 1-4), linkage diagnostic (W-2)
python tools/analysis/scratch_dir.py --run -- python E:/TaxoArena_tmp/svk_postrun/boot.py      # bounds + LOO (row 5)
cd E:/TaxoArena_backup_2026-10-05_stability_vs_kmeans && sha256sum -c SHA256SUMS.txt          # 3 OK
```
Scripts backed up: `E:/TaxoArena_backup_2026-10-05_stability_vs_kmeans/postrun_review/{recheck,boot}.py`. Both import
the reviewed blob's loaders (staged copies, read-only). They ran while `drift_replay.py --mutants` (synthetic) was
active; no construction ran.
