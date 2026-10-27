# READY review: CONSTRUCTION-ARMS (zero calls)

Reviewer: adversarial-reviewer, 2026-10-05, main at 8f97b8b4. Registration prog L24757-L24772 (_as_of 8f97b8b4, heading
"## Registered 2026-10-05 (before any code or call) — CONSTRUCTION-ARMS: ..."). Build: branch construction-arms, tip ea17b4ee,
`tools/analysis/construction_arms.py` blob:3ed4e9dac8e2c0ae3ad6922e8352c7f2063ad16a = sha256-lf16:16b2e5375e551d15 (LF; the
worktree file has 0 CR bytes, so no CRLF rendering differs). EVAL was NOT read by the reviewer: every number below is on TRAIN
(in-sample) or on fixtures.

## VERDICT: NOT READY

The code builds what the registration says, and the selftest, the 55 mutants, the dry-run, the pins and CA-R0 all reproduce.
What blocks READY is the design of readout (a). The registered control does not hold the shape fixed: arm 1 (KAPPA-SKM) builds a
shallow multiway tree, while arms 2 and 4 build deep binary ones. DP_coarse rewards the binary shape on its own, by about as much
as the gaps that would decide C-CA. On TRAIN, (WARD, (a)) already clears the spread conjunct on both corpora (+0.064 vs spread
0.014; +0.104 vs 0.056). So the likely ARM-WINS would come from shape rather than from the split rule. Readout (c) has no shape
term and is not affected. The fix has to be registered before any EVAL is read (B-1).

## Per-claim table (deciding claims)

| # | claim | reviewer's evidence | verdict | sev |
|---|---|---|---|---|
| 1 | selftest 103 checks | `--selftest` under scratch_dir: "SELFTEST OK: 103 value checks in 11.5 s", rc 0 | CONFIRMED | - |
| 2 | mutants 55/55, no-op survives | `--mutants --jobs 12`: "MUTANTS: 55 / 55 killed; control C0 SURVIVED" | CONFIRMED | - |
| 3 | dry-run clean | rc 0; pool line first; census 4946/4923, 6672/6672; TRAIN 9,870 / 13,487; L 84/139/81; m_min 55 (all legs); \|C\| 2772; "no EVAL row read; 0 files written"; DB mtimes unchanged (2026-10-02/03) after all reviewer runs | CONFIRMED | - |
| 4 | cost 126 fits, ~19 min with 20 workers, ~8.4 GB | dry-run prints 126 fits, 11,748 CPU-s, 18 min, 8.4 GB. Measured fit times are below the estimate (KAPPA 46-68 s per fit vs estimated 335-452 s), so the estimate is conservative | CONFIRMED | - |
| 5 | CA-R0: oos_tree_cells 74a5cbf0 -> caaced4a is a scratch_dir import only | `git diff 665b817d f460d72c`: exactly one changed line (`import tempfile` -> `import tempfile; import scratch_dir`); HEAD blob caaced4a | CONFIRMED | - |
| 6 | the 8 imported blobs are the pinned ones | worktree `git hash-object` = main `HEAD:` for all 8 | CONFIRMED | - |
| 7 | arms = registration (code read) | KappaRule: k 2..min(8, cap), floor m_min, min pairwise 1-cos >= 0.025, size-weighted Banerjee kappa, ties to the smaller k. GmmRule: diag, reg 1e-6, n_init 3, min BIC over k 1..8. Bisect through the SVK seam with skm n_init 5. Ward on the Euclidean renormalised slice, first n-L merges. HDBSCAN m_min. Filing to the renormalised TRAIN leaf mean | CONFIRMED in code, but R6 and R7 survive (C-1) | MEDIUM |
| 8 | arm 1 is a faithful-enough stand-in for the engine's vMF k-means (brief item 1) | Kotlin: `performVmfKMeans` (StatisticsUtils.kt L340-L401) grows k while the chance-corrected separation improves by >= marginalEps, with maxK 4 (TaxonomyConfig.kt L352; not overridden in the m_af / c_af TOMLs) and a deterministic maximin init. Arm 1 instead takes the max size-weighted kappa over k <= 8, and kappa rises with k, so it takes the largest admissible k. Measured on TRAIN, seed 0: arm 1's children histogram is M {2:6, 3:7, 5:2, 7:1, 8:7} and C {2:18, 3:7, 4:8, 5:4, 6:1, 7:2, 8:7}; mean leaf depth 2.5 / 2.8. Engine M-AF {2:70, 3:5, 4:1}, depth 6.1; C-AF {2:123, 3:6, 4:1}, depth 6.7. The docstring's description of the Kotlin is accurate | REFUTED for shape: it shares only the floor, the 0.025 bar and the kappa family; its branching is not the engine's | BLOCKER (with B-1) |
| 9 | matched L holds for every arm (brief item 2) | 15/15 reviewer fits reach exactly L (KAPPA s0/s1, GMM s0, BISECT s0, WARD on M/C/C-leg). Forced splits on the intent corpora: KAPPA 0/0 (s0), 0/4 (s1); GMM 0/0. WARD is exact by construction (replay refuses otherwise). Code refuses nL != L for DECIDING + control, but dropping the control from that check survives (R2) | CONFIRMED (one guard untested, C-1) | MEDIUM |
| 10 | readout (a) compares split rules "at matched greedy shape" | Same KAPPA leaves, own hierarchy vs a Ward-on-leaf-centroids binary hierarchy (TRAIN DP_coarse, mean of 5 seeds): M 0.5486 -> 0.5945, C 0.4292 -> 0.5098. Random placement of the same KAPPA leaves (median of 20): KAPPA shape 0.2297 / 0.1684 vs BISECT shape 0.2469 / 0.1813, so the shape alone is worth +0.017 / +0.013. TRAIN D_a vs arm 1: BISECT +0.0218 / +0.0530, WARD +0.0641 / +0.1042; arm-1 spread 0.0136 / 0.0561. The same differences against arm-1 leaves binarised: BISECT -0.024 / -0.028, WARD +0.018 / +0.024 | REFUTED: (a) is confounded by branching, and the confound is decisive on the TRAIN proxy | BLOCKER (B-1) |
| 11 | Support arithmetic (Support (b)-(g)) | re-derived: sigma_seed 0.01356 / 0.01520; seed term 0.00858 / 0.00961; SE(D) 0.0110 / 0.0102 / 0.0099 / 0.0105; DEFF_total 2.57 / 9.55 / 4.12 / 6.25; n_eff 1,925 / 699 / 1,200 / 1,068; joint MDE80 0.045 / 0.048 / 0.044 / 0.049; floor 0.042 / 0.047. Every figure reproduces. DEFF source named (Kish, measured). Realised arm-1 spread on TRAIN is 0.056 on CLINC, against 0.035 transported | CONFIRMED (non-vacuous); the floor is likely higher than registered | LOW |
| 12 | crossed / paired interval (SCALE-AGREE lesson) | arm j's and arm 1's seeds are resampled independently, components are shared across arms, and arm 1's draw is shared across its 3 comparisons (each comparison is marginal, so this is fine). It does not repeat SCALE-AGREE's D-1. But a with-replacement bootstrap of 5 seeds has variance (n-1)/n = 0.8 of s^2/n, so the seed SD is understated by about 11% | PARTLY | MEDIUM (C-2) |
| 13 | B-1 lesson on unresolved triplets (STABILITY-VS-KMEANS) | `conv` prints all-triplets (both-unresolved counts as agreement) and resolved-in-both, with each arm's unresolved share. It computes the joint both-resolved coverage (third return value) and then drops it | CONFIRMED as registered | LOW (C-3) |
| 14 | GR2 random-tree null not degenerate (HF2) | DP_coarse under leaf permutation can move through cross-leaf pairs. On TRAIN, CLINC and MASSIVE: 20/20 distinct draw values for KAPPA, BISECT, WARD and GMM; p97.5 well below the tree. Degenerate only for a flat hierarchy (HDBSCAN's flat fallback), where every draw equals the tree | CONFIRMED live for the deciding arms; flat case unflagged | LOW (C-3) |
| 15 | like with like, label status | every fit receives only (X, L, seed, m_min, info{leg, sub}); gold labels are read only in `unlock_eval` and the scorer; same Xtr, filing rule and L on every side; all arms [LF]. The m_min floor binds only arm 1 (a rule property): GMM leaves go down to 15 / 21 rows (50 of 139 below 55 on CLINC), BISECT to 19 / 31 | CONFIRMED [LF]; leaf-size asymmetry disclosed | LOW |
| 16 | C leg | 81 x 55 = 4,455 > \|C\| 2,772, so arm 1 cannot reach L = 81 by its rule. Forced share KAPPA 47/59 = 0.80 (s0) and 49/61 (s1), GMM 32/52 = 0.62. "rule mostly inactive" by construction | descriptive; needs a disclosure | LOW (C-4) |

## Own mutants (sandbox copy under E:/TaxoArena_tmp, TMP/TEMP/TMPDIR inside; selftest as the killer)

R1 centroids not renormalised in `leaf_centroids` (filing): SURVIVED, decisive (filing feeds (a) and (c)) | R2 control dropped
from the nL == L refusal: SURVIVED, decisive guard | R3 `clears` uses the upper bound: killed | R4 force-split the smallest
leaf: SURVIVED, not decisive on the intent corpora (forced 0-4 per fit) | R5 kappa bar on the max pair: killed | R6 GMM
covariance spherical: SURVIVED, decisive for arm 3's identity | R7 kappa unweighted mean over children: SURVIVED, decisive
for arm 1's identity | R8 Ward -> average linkage: killed. **3 / 8 killed**; control C0 SURVIVED.

## Defects and fixes

- **B-1 (BLOCKER; registrar bracket before any EVAL read; then delta code + delta review).** C-CA's readout (a) is confounded by
  the arms' branching: arm 1 is multiway and shallow (k up to 8, depth ~2.5), arms 2 and 4 are binary and deep (~7-8).
  On the TRAIN proxy the confound alone is enough to make (WARD, (a)) clear both conjuncts (row 10). This is also where arm 1
  is furthest from the engine (row 8). Fix: pick one, pre-data:
  (F1) score (a) shape-matched: hierarchise every arm's leaves by one common rule (e.g. Ward on leaf centroids) and decide on
  that DP; keep the own-hierarchy DP descriptive.
  (F2) bring arm 1 closer to the engine: maxK 4 with the engine's increment rule (grow k while the min-pair or chance-corrected
  separation gains >= 0.025), then re-measure its branching against M-AF / C-AF.
  (F3) demote (a) to descriptive and decide C-CA on (c) alone (3 chances; leaf partitions are shape-free).
  Whichever is chosen, print each arm's children histogram and mean depth beside the readouts.
- **C-1 (MEDIUM; code + tests).** Add checks that kill R1 (a two-leaf unit where the item is closer in cosine to the diffuse
  leaf), R2 (the control alone short of L must refuse), R6 (GMM's covariance_type is asserted, e.g. via a planted
  anisotropic blob where diag and spherical BIC differ) and R7 (a planted node where weighted and unweighted kappa choose
  different k). R4 is optional (needs a fixture with two forceable leaves of different size).
- **C-2 (MEDIUM; print only).** Print beside SE(D) a seed-term-corrected SE (seed variance x n/(n-1) = 1.25) and say that the
  percentile interval is anti-conservative on the seed axis. The spread conjunct usually binds, but it does not for an arm
  with large seed variance (e.g. GMM).
- **C-3 (LOW; print only).** Print the joint both-resolved coverage from `conv` beside every resolved-in-both figure (SVK W-2).
  Print, per arm x seed, the number of distinct random-tree DP values, flagging "null degenerate (flat)" when it is 1.
- **C-4 (LOW; disclosure).** On the C leg, arm 1 reaches L = 81 mostly by forced 2-means: m_min x L exceeds |C|. Say so beside
  the C-leg line. Arm 1 there is mostly BISECT.

## Commands (reviewer; scripts kept under E:/TaxoArena_tmp/ca_review/)

```
python tools/analysis/scratch_dir.py --run -- python tools/analysis/construction_arms.py --selftest        # 103 OK
python tools/analysis/scratch_dir.py --run -- python tools/analysis/construction_arms.py --mutants --jobs 12 # 55/55, C0 survived
python tools/analysis/scratch_dir.py --run -- python tools/analysis/construction_arms.py --dry-run --mmlu-root Z:/FAC/TUBerlin/THESIS/TaxoArena --workers 20   # rc 0
git hash-object tools/analysis/construction_arms.py; git show ea17b4ee:tools/analysis/construction_arms.py | sha256sum   # 3ed4e9da; 16b2e537...
tr -cd '\r' < tools/analysis/construction_arms.py | wc -c                                                  # 0
git diff 665b817d f460d72c -- tools/analysis/oos_tree_cells.py | grep -E '^[+-]'                           # one line changed (CA-R0)
python E:/TaxoArena_tmp/ca_review/rev1.py   # TRAIN only: fits, children hist, depth, forced, leaf sizes; engine hist; SHAPE / PURESHAPE (rows 8-10, 14-16)
python E:/TaxoArena_tmp/ca_review/rev2.py   # TRAIN only: KAPPA / BISECT seeds 0-4 + WARD; in-sample DP, spread, binarised-KAPPA D (row 10)
python E:/TaxoArena_tmp/ca_review/mkmut.py; python E:/TaxoArena_tmp/ca_review/mut/construction_arms.py --mutants --jobs 9    # R1-R8
grep -n -E "maxK|marginalEps" src/main/kotlin/taxonomy/config/TaxonomyConfig.kt; sed -n 340,401p src/main/kotlin/taxonomy/utils/StatisticsUtils.kt
ls -l --time-style=full-iso embeddings_cache.db snapshots.db mmlu_pro_dataset_cache_v2.db .claude/worktrees/intent-s1-run/snapshots.db   # unchanged
```

## Brackets owed (registrar)

1. B-1: the chosen fix (F1 / F2 / F3) for readout (a), recorded before any EVAL read. If C-CA's readouts change, Support (e)-(f)
   and P2-P5 are re-stated for the new deciding set.
2. Disclosure of row 8 under WORDS OF RECORD: arm 1 differs from the engine in branching (k up to 8 by max kappa vs maxK 4 by
   separation increment).
3. Realised CLINC arm-1 seed spread on TRAIN is 0.056 (registered E[spread] 0.035): the floor in Support (g) is likely higher.

---

## DELTA REVIEW 2026-10-05: build 0a6808b5 (blob:5d08a5df), brackets c9752a77 (prog L24757-L24780, _as_of c9752a77)

Scope: `git diff ea17b4ee..0a6808b5` (1 file, construction_arms.py, +580/-130; ea17b4ee is an ancestor). Code the delta does not
touch is covered by the first review above. As before, the reviewer read no EVAL rows; every real-data number below is on TRAIN
(in-sample).

### VERDICT: READY (delta). B-1 discharged by F2 + F1; C-1..C-4 discharged. Two wording brackets are owed (below); neither blocks the run.

| # | check | evidence | verdict | sev |
|---|---|---|---|---|
| D-a | pins | `git hash-object` = `HEAD:` = blob:5d08a5dfb8c0cb0b5330512259b4732aa4af2dd2; `git show 0a6808b5:<path>` piped to sha256sum = sha256-lf16:1056698311cb9f52 (LF, of record). The worktree file has 0 CR bytes; the commit's sha256-crlf16:439e598d03c2ef2a is the CRLF rendering beside it. The 8 imports are untouched (the diff touches 1 file). Kotlin blobs named in the bracket match HEAD: TaxonomySplitter 08f0020e, StatisticsUtils a5f5b1b7, TaxonomyConfig 0443443a | CONFIRMED | - |
| D-b | selftest / mutants / dry-run | "SELFTEST OK: 130 value checks"; "MUTANTS: 74 / 74 killed; control C0 SURVIVED"; dry-run rc 0: 156 fits, ~22 min with 20 workers, 8.4 GB, knobs printed for all 3 legs (maxK 4, marginalEps unset -> bar, bar 0.025, multiplier 1.00), "no EVAL row read; 0 files written" | CONFIRMED | - |
| D-c | F2 = TaxonomySplitter (item 1) | Line by line: `ccs` = chanceCorrectedSeparation(List<ClusterStats>) (wWithin, pairFrac, wTotal, 1e-10 guard). `engine_select` = the performVmfKMeans k loop (break on a cluster < minSize, k=2 always kept, increment >= eps, else break). The 2*m_min threshold and the floor pre-check match L211. `coarsen` = the stabilisation loop: route all rows, drop under-floor while k > 2 and >= 2 survivors, merge the weakest pair < acceptEps while k > 2, re-route after every move. The final floor check and the min-pair gate are at acceptEps. eps = marginalEps, or barFor when negative (adaptiveBars empty in the TOMLs -> proposalSeparationBar), the nominal bar, not times the multiplier, as in Kotlin. Residual differences are (i)-(v) as worded, plus one negligible one: Kotlin's minSize = toInt(n x m_min / n) can truncate to m_min - 1 | CONFIRMED | - |
| D-d | F2 on real TRAIN (5 seeds per corpus) | children hist MASSIVE {2:11-30, 3:13-22, 4:9-12}, depth 4.13-4.52; CLINC {2:28-38, 3:12-23, 4:18-28}, depth 4.21-4.57. Engine: M-AF {2:70, 3:5, 4:1}, depth 6.1; C-AF {2:123, 3:6, 4:1}, depth 6.7. Forced 0-1 per fit; nL = L in 10/10; leaf min 55-56. C leg (s0): forced 49 / 76 = 0.64, "rule mostly inactive" (the C-4 line prints it) | closer to the engine, but NOT "mostly binary" as Support (g) says | LOW (bracket W-1) |
| D-e | F1 per the bracket (item 2) | `common_hier`: scipy linkage 'ward' (Euclidean) on the renormalised filing centroids, one unweighted point per leaf. The noise leaf (and any empty leaf) hangs under the root. The same function serves every arm, 1K, HDBSCAN and the engine rows (leaf vmfMu, flatLeaf filing). The (a) point, the dp_fast bootstrap and GR2 all read Hc; own-hierarchy DP is kept as (a-own) | CONFIRMED | - |
| D-f | (a) still discriminates (item 3) | Planted world (12 fine / 4 coarse, 24-d), common-hierarchy DP: pure leaves 1.000; leaves mixing coarse groups 0.445; leaves mixing only within coarse groups 1.000 (fine mixing correctly leaves coarse DP unchanged; (c) drops to 0.504). TRAIN common-hierarchy DP, real arms: MASSIVE ENGINE-SKM 0.5917 (range 0.0271, 5 seeds), BISECT 0.5408 (2 seeds), WARD 0.6243, 1K 0.5691; CLINC 0.4828 (range 0.0524), 0.4948, 0.5164, 0.5035. Own mutant D1 (C-CA over (c) only) is KILLED, so the (a) branch of C-CA is under test. The planted e2e worlds' single coarse class is a fixture choice, not a neutralisation of (a) | CONFIRMED: (a) is live; the criterion has not silently become (c) alone | - |
| D-g | C-1 | builder X69-X72 = R1/R2/R6/R7 are killed among the 74; my own re-run of R1, R2, R6, R7 on blob 5d08a5df: all 4 killed | DISCHARGED | - |
| D-h | C-2 | se_corr = sqrt(SE_item^2 + 1.25 x (SE^2 - SE_item^2)) printed beside SE(D) with the anti-conservative sentence; registered seed terms 0.0096 / 0.0170 quoted. Restated Support re-derived: CLINC sigma 0.02408, seed term 0.01523, SE(D) 0.0156 / 0.0158, DEFF 22.3 / 14.1, n_eff 299 / 472, joint MDE80 0.0755 / 0.0758, floor 0.075. Every figure reproduces | DISCHARGED | - |
| D-i | C-3 / C-4 | coverage (conv's 3rd value) printed as "[cov]" on the seed and subsample lines; distinct-draw count + "null degenerate (flat)" in gr2_text (killed by X73/X74); C-4 disclosure line computed from m_min, L, \|C\| | DISCHARGED | - |

Own delta mutants (sandbox copy under E:/TaxoArena_tmp, TMP inside; selftest as the killer): D1 C-CA decided on (c) only: killed |
D2 coarsen without its initial re-route: SURVIVED. Not decisive and near-equivalent: spherical k-means labels already equal the
argmax to their renormalised means at convergence, so it differs only for an unconverged restart (LOW, optional unit) | D3 merge
requires k > 3: killed. Re-runs R1, R2, R6, R7: killed. **6 / 7 killed**; C0 survived.

### Brackets owed (registrar; pre-data, before --run)
- **W-1 (LOW, wording).** Support (g)'s "F2 makes arm 1 mostly binary" is refuted on TRAIN: arm 1 splits 2-, 3- and 4-way in
  roughly comparable numbers (depth ~4.3, against the engine's 6.1 / 6.7, which is about 90% binary). Restate (g) with the
  measured histogram. The likely cause is difference (ii) (256-d against the per-node PCA) together with (iv) (no dJ / z
  acceptance). F1 keeps (a) free of shape whatever the histogram.
- **W-2 (disclosure).** The reviewer has now SEEN TRAIN in-sample values of the redefined (a) on the new arm 1 (row D-f): WARD
  minus ENGINE-SKM +0.033 (MASSIVE; spread 0.027) and +0.034 (CLINC; spread 0.052); BISECT -0.051 / +0.012 (2 seeds). These
  numbers are in-sample, so they are not the EVAL readout. Add them to the bracket's DISCLOSURE beside the row-10 numbers.

### Commands (delta)
```
git diff --stat ea17b4ee..0a6808b5; git merge-base --is-ancestor ea17b4ee 0a6808b5
git hash-object tools/analysis/construction_arms.py; git show 0a6808b5:tools/analysis/construction_arms.py | sha256sum   # 5d08a5df; 10566983...
python tools/analysis/scratch_dir.py --run -- python tools/analysis/construction_arms.py --selftest   (also --mutants --jobs 12; --dry-run --workers 20)
python E:/TaxoArena_tmp/ca_review/rev3.py      # planted (a) discrimination; TRAIN-only F2 fits, histograms, common-hierarchy DP (D-d, D-f)
python E:/TaxoArena_tmp/ca_review/mkmut2.py; python E:/TaxoArena_tmp/ca_review/mut2/construction_arms.py --mutants --jobs 8   # D1-D3, R1/R2/R6/R7
sed -n 128,460p src/main/kotlin/taxonomy/operations/TaxonomySplitter.kt; sed -n 185,225p src/main/kotlin/taxonomy/utils/StatisticsUtils.kt
```
