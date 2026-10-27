# POSTRUN review — CONSTRUCTION-ARMS (2026-10-05)

Reviewed: outcome `E:/TaxoArena_backup_2026-10-05_construction_arms/construction_arms_outcome.txt` (sha256
6a47712d0dc4b276..., 165 lines; equal to lines 27-191 of `E:/TaxoArena_tmp/ca_run.log`, rc 0; the only byte
difference is the console rendering of the em dash in line 1). Script blob:5d08a5dfb8c0cb0b5330512259b4732aa4af2dd2
(LF, of record; `git rev-parse HEAD:<path>` at 0765e2c5 and `git hash-object` agree; 0 CR bytes), the blob the
READY delta (dfa26a41) passed. Registration prog L24757-L24772 with brackets c9752a77 and 1713fc3f. Zero calls.

## VERDICT: VALID. C-CA NO-ARM-WINS (correctly derived); F-CA NOT FIRED. Words need two additions (W-1, W-2)

Data object right: MASSIVE EVAL 4,946 / 4,923 components, CLINC 6,672 / 6,672, TRAIN 9,870 / 13,487, L 84 / 139,
m_min 55, engine knobs maxK 4 / eps unset / bar 0.025 / mult 1.0; I1-I3 reproduced; TRAIN-only audit printed;
intent DB pins OK before and after. I refit arm 1, GMM-BIC and WARD on both corpora with the pinned module's own
functions and re-ran the registered bootstrap with the same RNG consumption order: every deciding point AND
both bounds reproduce to the 5th digit (table). Matched L holds (every deciding fit reaches 84 / 139).

## Per-claim table (deciding claims)

| # | claim (outcome) | result | mine vs claimed | sev |
|---|---|---|---|---|
| 1 | WARD (c) MASSIVE D +0.05216 [+0.02512, +0.09468], spread_1 0.10797 -> fails | CONFIRMED to the digit | recheck: +0.05216 [+0.02512, +0.09468], spread 0.10797. Fails ONLY the spread conjunct | - |
| 2 | WARD (c) CLINC D +0.02740 [+0.01535, +0.03957], spread 0.02323 -> clears | CONFIRMED to the digit | identical; margin over spread +0.0042 | - |
| 3 | WARD (a) +0.00761 [-0.01179, +0.02788] / -0.00098 [-0.02085, +0.01710] | CONFIRMED to the digit | identical | - |
| 4 | GMM-BIC (a) +0.00423 / +0.01667; (c) -0.00142 / -0.14832 [-0.17021, -0.12859] | CONFIRMED to the digit | identical (intervals too) | - |
| 5 | BISECT-SKM (a) -0.03802 / +0.00056; (c) +0.01290 / -0.02119 | CONFIRMED (points) | partA.py from the printed seed values: same to the 5th digit (bounds not refit) | - |
| 6 | C-CA NO-ARM-WINS; F-CA not fired | CONFIRMED by hand | only WARD (c) CLINC clears both conjuncts; no (j, r) clears on both corpora | - |
| 7 | P3 FAILED (GMM D_c CLINC -0.148 outside [-0.06, +0.02]); P4 FAILED (WARD D_c MASSIVE +0.052 outside [-0.03, +0.04]); P8 MASSIVE FAILED (+0.041 outside [-0.15, +0.03]); other bands HELD; P5 Brier 0.0100, P7 Brier 0.0900 | CONFIRMED | (0.10-0)^2 = 0.01; (0.70-1)^2 = 0.09 | - |
| 8 | realised Support: e.g. WARD (c) MASSIVE SE 0.01889, item SD 0.00385, DEFF_total 24.28, n_eff 204, MDE80 0.1238 / joint 0.1316; deciding joint MDE 0.1322 vs registered 0.076 | CONFIRMED (arithmetic) | 1.0093 x (0.01889/0.00385)^2 = 24.3; 4946/24.28 = 204; 0.10797 + 0.84 x 0.01889 = 0.1238; + 1.25 x = 0.1316; seed-corrected sqrt(0.00385^2 + 1.25 x (0.01889^2 - 0.00385^2)) = 0.02103 | see W-2 |
| 9 | "the GMM is much worse on CLINC leaves" (reading) | CONFIRMED as REAL under the registered rule; NOT a numerical fit failure | see G below | - |

## Task answers

**A. Did any arm come close? Yes, WARD on (c).** It cleared 3 of 4 conditions: lower bound > 0 on both corpora, and
D > spread on CLINC (by 0.004). It fails only on the MASSIVE spread conjunct, and that spread (0.108) is set by ONE
arm-1 seed. Arm 1 seed 2 on MASSIVE keeps a rule-refused leaf of 1,621 TRAIN items. That leaf receives 18.3% of
EVAL, at accuracy 0.284, and gives the seed (c) 0.686 against 0.777-0.794 for the other four. Leave-one-seed-out:
dropping seed 2 gives spread 0.0166 and WARD D +0.032, which would clear. Dropping any other seed leaves spread
≥ 0.106. In the other direction: WARD is one seed-free fit. On the five 90% TRAIN subsamples its (c) is MASSIVE 0.809
(range 0.006) and CLINC 0.860 (range 0.011). Against arm 1's mean that is +0.042 / +0.020, and the CLINC figure is
BELOW the 0.023 spread. So the near-win is fragile both ways. "Clearly beats" does not hold; "close on (c)" does.
Nothing else came close. The best (a) margin is GMM CLINC +0.017 against a spread of 0.060. BISECT (a) MASSIVE is
-0.038 and (c) CLINC -0.021, upper bounds < 0, but not below -spread.

**G. GMM-BIC's CLINC (c) loss (-0.148) is real, not a degenerate-covariance failure.** Evidence:
(i) Tiny leaves are negligible. Leaves under 10 items: 0/3/0/1/0 per seed, and one size-1 leaf in seed 1 (the
outcome's "min 1"). EVAL filed to them: ≤ 0.09%.
(ii) At the root the k = 8 fit has minimum per-component diagonal variance 5.3e-5 to 1.2e-4, against reg_covar
1e-6 (median 1.4e-3). There is no collapse.
(iii) The mechanism is that BIC does not select k. Root BIC falls monotonically from k = 1 to k = 8 (-12.01M to
-12.60M), so the rule runs to the cap: 14-15 of 22-23 CLINC splits are 8-way (outcome histograms). With L = 139
tight against 150 intents, 22 eight-way splits spend the leaf budget unevenly. The result is 12-15 leaves of
≥ 200 TRAIN items, holding 19-26% of EVAL at accuracy 0.32-0.38, and leaves of 15-30 items elsewhere. Only
109-117 of 150 intents own a leaf majority, against 134-137 for arm 1 and 137 for WARD.
(iv) The loss is fine-level only. GMM (a) is +0.017 on CLINC. On MASSIVE (60 intents, L = 84, slack) the same
lopsidedness costs nothing (D_c -0.001).
The right words: "a property of BIC-to-cap selection at matched L, not a numerical failure".

**S. Stability (b) and OOS (d) are descriptive.** Seed pairs, resolved-in-both [coverage]:
- MASSIVE: arm 1 0.024 [0.76], BISECT 0.087 [1.00], GMM 0.100 [0.34], 1K 0.070 [0.29].
- CLINC: arm 1 0.037 [0.60], BISECT 0.008 [1.00], GMM 0.068 [0.29], 1K 0.056 [0.29].

All-triplet figures for multiway arms are inflated by unresolved shares (arm 1 0.23 / 0.36, GMM 0.54 / 0.61), so
only the binary arms compare cleanly. On 90% subsamples WARD is the least stable resolved arm (0.224 / 0.167,
against BISECT 0.092 / 0.047). Its point (c) is stable (S above), but its topology is not. HDBSCAN is not a usable
partition at min_cluster_size 55 (4 / 27 leaves, noise 0.68 / 0.74). P6 HELD (-0.044 / +0.090).
OOS AUROC: every |D| for arms 2-4 is ≤ 0.006. WARD +0.006 [+0.005, +0.008], GMM -0.005, BISECT +0.000. P7 TRUE.

**E. Engine rows and disclosed differences.** M-AF DP is 0.67043 on its own tree and 0.59905 on the common
hierarchy, with (c) 0.78104. C-AF is 0.47730 / 0.55634, with (c) 0.82674 and AUROC 0.96776. The common hierarchy
moves the engine's DP by -0.071 (MASSIVE) and +0.079 (CLINC), so arm 1 minus engine (+0.041 / -0.051) changes sign by
corpus (P8 MASSIVE FAILED). Difference (vi) as bracketed matches the run exactly: arm 1 children MASSIVE
{2:11-30, 3:13-22, 4:9-12} at depth 4.13-4.52, CLINC {2:28-38, 3:12-23, 4:18-28} at depth 4.21-4.57; engine
{2:70, 3:5, 4:1} 6.08 and {2:123, 3:6, 4:1} 6.72. Descriptive: WARD's (c) also exceeds the engine row's (c) by
+0.038 / +0.040. That is item-level and single-fit, and not a registered comparison.

## Defects / words (none changes the verdict)

- **W-1 (HIGH; words; registrar).** The record must carry the near-miss. Add: "WARD (c) cleared the interval
  conjunct on both corpora and the spread conjunct on CLINC (+0.027 vs 0.023). It failed only MASSIVE's spread
  (0.108), which one arm-1 seed carries (seed 2: a 1,621-item rule-refused leaf, 18.3% of EVAL at 0.284). Without
  that seed it would clear. WARD's own 90%-subsample (c) puts its CLINC margin below the spread." Fix: bracket the
  outcome with this sentence. Do not write "Ward beats" or "no rule matters".
- **W-2 (MEDIUM; Support; registrar).** The realised deciding joint MDE80 is 0.132, against 0.076 registered.
  MASSIVE (c) was planned at spread 0.0315 and realised 0.108, so the test was weaker than registered on exactly the
  cell that came close. Fix: print realised beside registered in the record. The verdict line DESCRIPTIVE-ONLY
  stands.
- **W-3 (MEDIUM; words).** Write GMM-BIC's CLINC (c) loss as "BIC runs to the k = 8 cap; unbalanced leaves at matched
  L (109-117 of 150 intents own a leaf)". Never write "the GMM fit failed" or "degenerate covariances" (refuted, G).
- **L-1 (LOW; code-read, descriptive).** `engine_readout` files the engine row by `leaf_mu` and takes TRAIN
  majorities from re-routed TRAIN (`flat_leaf`), whereas the arms use member centroids and membership. The asymmetry
  is small and descriptive only. Fix: state it beside the engine rows.
- **L-2 (LOW).** The empty-slice RuntimeWarning at script L1195 is HDBSCAN on mmlu (1 leaf, noise 1.0, resolved n/a).
  It is harmless.

## Corrected words of record

"No split rule clearly beats the engine-like spherical k-means at matched leaves (C-CA NO-ARM-WINS; not parity; no
TOST). The nearest is WARD on leaf filing accuracy: +0.052 [+0.025, +0.095] MASSIVE and +0.027 [+0.015, +0.040]
CLINC. It is above arm 1's seed spread on CLINC only, and the MASSIVE spread is carried by one arm-1 seed. GMM-BIC
loses 0.148 on CLINC fine filing because BIC runs to the k = 8 cap at matched L, not through a numerical failure.
Arm 1 is a stand-in, not the engine (differences (i)-(vi))."

## Commands (all read-only; zero calls; outputs under E:, never committed)
```
sed -n 27,191p E:/TaxoArena_tmp/ca_run.log | diff - <outcome>       # line 1 em-dash rendering only
python partA.py          # D and spreads for all 20 (r, corpus, arm) cells from the printed seeds
python tools/analysis/scratch_dir.py --run -- python recheck.py     # 1m37s, 18 workers: refits, registered
   # bootstrap (default_rng(20261006), components then SEEDED draws), LOO spreads, leaf diagnostics, WARD 90%
   # subsamples, GMM root BIC k1..8 and variances; intent pins OK
git rev-parse HEAD:tools/analysis/construction_arms.py; git hash-object <same>   # both 5d08a5df
```
Backup: E:/TaxoArena_backup_2026-10-05_construction_arms/SHA256SUMS.txt 6/6 OK (outcome; postrun_review/
recheck.py 18ea5515..., recheck.log e96464f4..., partA.py 45a290a4..., ca_run.log 5d3b6098..., ca_dry.log b92ea81d...).
