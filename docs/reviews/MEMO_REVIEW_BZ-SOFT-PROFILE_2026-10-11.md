# Adversarial review: research memo 2026-10-11 (benchzoom post 1, design D1 / draft BZ-SOFT-PROFILE)

Reviewer: adversarial-reviewer, 2026-10-11. Zero paid calls, zero Ollama calls, zero vault responses read.
Object: `docs/drafts/hf/benchmark-zoom/research_memo_2026-10-11.md` (uncommitted draft, 206 lines) and the probes in
`E:/benchzoom_demo/research_probes/` (SHA256SUMS.txt: 29 lines, `sha256sum -c` reports 0 failures).

## Verdict: NEEDS REVISION (registration text NOT READY)

The memo's own numbers reproduce to the digit and the vault is respected by every probe. But the central claim of D1
(below category there is a real, continuous, TOPICAL signal that a soft text reader finds) fails a null that keeps what
the question conditions on. Most of the text-kNN gain comes back from neighbours chosen by difficulty b and text length
alone, with no topic information. On MATH the declared `level` column beats the text kNN outright. The registration also
predicts from a backbone that D1 does not use (C-7), and its Support SE belongs to a different statistic.

## Per-claim table (deciding claims; WORK side, 5 folds, log-loss gain x1e-3 per model x item cell, item-clustered SE)

| # | Claim (memo) | Memo | Reviewer | Status | Sev |
|---|---|---|---|---|---|
| 1 | Category over M0: MMLU-Pro / MATH / MATH<.95 | +2.52 / +0.82 / +2.46 | +2.52 (.20) / +0.82 (.07) / +2.46 (.22) | CONFIRMED | - |
| 2 | Text kNN over category (M3-M1) | +0.53 / +0.86 / +2.60 | +0.53 (.06) / +0.86 (.07) / +2.60 (.23) | CONFIRMED | - |
| 3 | Leaves over category (M2-M1) | +0.02 / +0.24 / +0.73 | +0.02 / +0.24 / +0.73 | CONFIRMED | - |
| 4 | Slope correction: M5, M5g, null M5 (vs M0) | 9.39/8.38/5.87; 3.73/3.82/2.97; 11.23/-/9.52 | identical | CONFIRMED | - |
| 5 | M6_3-M5 real vs null | 3.58 vs 2.84; 0.16 vs 0.18 | 3.57 vs 2.84; 0.16 vs 0.18 | CONFIRMED (rounding) | - |
| 6 | kNN survives the slope (M7-M5) | +0.89 / +0.63 / +1.94 | +0.887 (.096) / +0.634 (.048) / +1.948 (.149) | CONFIRMED | - |
| 7 | kNN null = 0.00 shows the signal is topical below category | "null 0.00" | the null (random unit vectors) is vacuous for this question; see R1 | REFUTED as evidence | BLOCKER |
| 8 | Text kNN gain is text structure (vs non-text neighbours, over global slope M5g) | implied | MMLU-Pro: text kNN +0.961 (.087); b-nbrs +0.705 (.334); length-nbrs +0.531 (.063); b+len +0.793 (.335); **text after b+len +0.256 (.029)**. MATH: +1.037 / +0.672 / +0.689 / +1.009; **text after b+len +0.365 (.025)**. MATH<.95: +3.169 / +2.058 / +2.135 / +3.106; text after b+len +1.117 (.077) | PARTLY: 27-35% of the gain is text-specific | BLOCKER |
| 9 | Below-category MATH signal is continuous, so needs a soft reader | implied | declared category x `level` offset over M5g: +1.525 (.092), above text kNN +1.037; **text kNN over level +0.160 (.016)**; MATH<.95: level +4.458, kNN over level +0.488 | REFUTED for MATH | HIGH |
| 10 | C1 predictions: kNN over "category+2PL" 0.9 / 0.6 / 1.9 | M7-M5 (per-CATEGORY slope) | D1 uses a GLOBAL slope: kNN over M5g = 0.961 / 1.037 / 3.169 | SUBSTITUTED backbone (C-7) | HIGH |
| 11 | Support: WORK SE 0.06-0.07, vault MDE 0.2-0.25, predictions >= 3x MDE | 0.06-0.07 is the SE of M3-M1 | SE of M7-M5: .096 / .048 / .149; x sqrt(WORK/vault)=1.225 gives vault SE .118 / .059 / .183; MDE80 = 2.8 SE gives .33 / .16 / .51. MMLU-Pro prediction 0.9 = 2.7x MDE (not >= 3x). DEFF and its source: absent | REFUTED (arithmetic) | HIGH |
| 12 | "Global 2PL slope" | named 2PL | M5/M5g = a model-specific slope on item difficulty (eta + v_j (b_i - mean b)). That is a person-discrimination term, not the item discrimination a_i of a 2PL. No item-2PL arm and no guessing floor (MATH-MC 4 options, MMLU-Pro 10, log-likelihood) were tested | MISNAMED; alternative untested | HIGH |
| 13 | Vault untouched by the probes | yes | every response read goes through `work_mask` (p1_analyze L77-89 asserts it, p2 L24, p3 L86, p4 L54). The tree is text-only (`Atlas.fit` calls `bisect(X, ...)`). Vault json and v2 atlases are unchanged before and after my run (sha) | CONFIRMED | - |
| 14 | The vault keeps a later test uncontaminated | yes | the vault responses were already read by the v2-v4 demo atlases (fitted on all 4,914 / 11,994 items) and by G-PEAKS on the same data, and those informed the design. The vault is id-disjoint, not content-closed: 140 / 4,797 MMLU-Pro vault items have a WORK twin at cosine >= 0.98 (94 at >= 0.995); MATH 3 / 1,965 | PARTLY | MEDIUM |
| 15 | P1: skill phrases double J and silhouette, so they make better labels | all leaves | holds on MATH only (J .044 to .071, .032 to .068). MMLU-Pro physics J FALLS .035 to .024; MMLU-Pro math .023 to .039. Better separation does not mean a better label (non sequitur) | PARTLY | MEDIUM |
| 16 | 11/13 MATH and 20/28 MMLU-Pro leaves refused (descriptive spot check) | - | MATH 11 separation + 2 size of 13; MMLU-Pro 20 separation + 8 size + 2 none of **30**. The two denominators differ | PARTLY | LOW |
| 17 | MATH tau per depth [0,.246,0,.168,.168] (spot check) | - | math_v4 summary.json identical | CONFIRMED | - |
| 18 | ADAPTIVE-PROFILE: flat beats bisection; certification costs about 0.002 Brier | registered | AP4 F_flat KMEANS-BETTER, uncertified path +0.002925. But the data object is the TaxoArena v2 union EVAL (18 models), not EEE MATH or OLL MMLU-Pro | CONFIRMED, different data object | LOW |
| 19 | Literature: EvalTree, ADeLe, metabench, Burnell et al. | no links given | the methods exist and are broadly described correctly (EvalTree: LLM capability annotations, then recursive k-means with silhouette-chosen k; ADeLe: 18 demand rubrics on 0-5 levels; metabench and Burnell: a few-factor structure). "EvalTree validated on a single model with synthetic weaknesses" could not be verified without web access | UNDETERMINED | LOW |

## Defects and fixes (ranked)

- R1 BLOCKER: the null does not preserve what the question conditions on (check 4). Random vectors give neighbours
  that share nothing, so a 0.00 null is guaranteed. The question is whether text adds anything beyond difficulty,
  format and annotations. Controls that keep difficulty and length remove 65-73% of the gain (row 8).
  FIX: make the deciding contrast text-kNN over [M5g + b-neighbour field + length-neighbour field], plus `level` for
  MATH and `src` for MMLU-Pro if the author adopts it as an anchored level. Use the random-vector null only as a
  harness check. Re-cut the predictions from that contrast: WORK +0.26 (MMLU-Pro), +0.37 (MATH), +1.12 (MATH<.95),
  and on MATH over level only +0.16.
- R2 BLOCKER for the post's thesis: "below category the detail is real, continuous and topical" does not survive R1.
  On MATH the strongest finer reader is a declared column (level, which is label information; the anchored-tree rule
  applies). FIX: the post claims only what survives R1. The granularity meter shows category, then declared annotation,
  then text residual, each with a difficulty-preserving null.
- R3 HIGH (C-7): C1 predictions come from M7-M5 (per-category slope), but D1 specifies a global slope. FIX: name ONE
  backbone in the registration (M5g if D1). Re-derive the predictions on it (rows 8 and 10). C2 must name the
  backbone the leaves reader uses.
- R4 HIGH: Support. FIX: use the SE of the deciding contrast (for R1's contrast: .029 / .025 / .077 on WORK, vault
  about .036 / .031 / .094, MDE80 about .10 / .09 / .26). State DEFF against the cell-iid SE and its source (this
  WORK cache, measured). Drop the "at least 3x MDE" sentence unless it reproduces.
- R5 HIGH: measurement model. "2PL" is the wrong name for a person slope. FIX: rename it ("model-specific
  discrimination slope"). Before calling Rasch-plus-slope the backbone, compare it with an item-2PL (a_i) and a
  3PL with c fixed at 1/options (MATH-MC chance .25; MMLU-Pro .10 under log-likelihood). A guessing floor may explain
  part of the slope and part of the b-neighbour gain (row 8). Prediction, CPU only.
- R6 HIGH: the C5 null permutes answers within model x category, which destroys item difficulty b. False flags are
  easier to control under that null than under a realistic one. FIX: use a parametric bootstrap from the fitted
  backbone (b, theta, slope and category offsets kept; region effects zero). Separately, the default view "top and
  bottom 2-3 regions per model" is a winner's-curse display whatever the flags say. FIX: show regions only when
  flagged, with selection-adjusted intervals (or the region's rank interval). MATH: 41/69 models at .975 or above
  have per-region h near 0, so the view is empty for most models; say so.
- R7 MEDIUM: vault wording. FIX: call it "held out from these probes, id-disjoint; responses previously seen by the
  demo atlases and G-PEAKS". Run CK-CLOSE (or drop WORK neighbours at cosine >= 0.98 to a vault item) before scoring,
  and disclose the 140 twins.
- R8 MEDIUM: P1. FIX: state the MMLU-Pro physics reversal. Label quality is decided by the name-recovery check, not by J.
- R9 LOW: MATH<.95 subset is chosen on accuracy over the whole WORK set, test folds included. FIX: freeze the model list
  from WORK accuracy before the vault opens and print it in the registration. Also fix the 11/13 vs 20/28 denominators,
  and add citations with URLs, verifying the EvalTree "single model, synthetic weaknesses" sentence against the paper.
- R10 MEDIUM, realism: D1 with regions, Ollama labels and five criteria is not a 4-5 day post once R1-R6 are applied.
  Cheaper option (not considered by the memo): post 1 = a measurement fix (slope, or 3PL if R5 favours it) +
  categories + declared annotations + a granularity meter with honest nulls, reporting the text residual as small and
  real. No regions, no labels, CPU only, about 2 days. Regions and skill phrases (and D4) go to post 2.

## Missing modalities

Item-level discrimination and guessing (R5). The declared annotation columns (MATH `level`, MMLU-Pro `src`) as a
reader arm. Option-format neighbours: MMLU-Pro embeds question + options, and under log-likelihood scoring format
neighbours can carry model-specific bias, which is not a skill. Length as a confound (row 8).

## Commands (all read-only on data; output to stdout)

```
sha256sum -c E:/benchzoom_demo/research_probes/SHA256SUMS.txt | grep -vc OK      # 0 failures; wc -l gives 29 entries
python: json.load(p3_predict_{math,mmlu_pro}{,_NULL}.json) -> gain_ll_vs_M0/M1 *1e3   # rows 1-6, to the digit
grep -n "work_mask\|benchmark.Y" scripts/p1_analyze.py p2_lowrank.py p3_predict.py p4_beyond_slope.py   # row 13
benchzoom src/benchzoom/atlas.py L116-120: tree = bisect(X, ...)  (text-only)                          # row 13
reviewer script (scratchpad rev_p3.py; imports p3_predict.group_offset/knn_offset/ridge_logit_step unchanged;
  same folds, seed 11, KNN 40, LAM 20, LOMO b as p3):
  M5g = eta1 + global slope;  text kNN = p3.knn_offset(M5g);  b-nbrs: per model j, the 40 training items in the
  category nearest in |B[:,j]| (model j's own LOMO b, self excluded);  length-nbrs: nearest in len(format_item);
  stacked arms fit the next field on the previous residual;  level: p3.group_offset(cat|level) over M5g.
  python rev_p3.py mmlu_pro ; python rev_p3.py math                                                   # rows 6, 8-11
  vault json + v2 atlas sha256 before and after: identical (UNCHANGED)
twins: per category, max cosine of each item to WORK items (self excluded), thresholds .95/.98/.995       # row 14
pandas: tree.csv leaf rows, gate_refused_by counts; summary.json tau_per_depth                             # rows 16-17
```
Caveat: the b-neighbour arm alone has a large SE on MMLU-Pro (.334; a few items with extreme held-out b). The stacked
contrast (text after b+len, SE .029) is stable and is the one the findings rely on.
