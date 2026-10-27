# DEEP-SPLIT-COMPARE: draft registration (zero calls; design only; NOT REGISTERED)

Tree-construction specialist, 2026-10-02, at HEAD 74683c20, ledger v341 (unchanged by this file). The author's go
(2026-10-02): "yes register the deep split comparison". Read-only: nothing was built, fitted or scored. The only quantities
computed for this draft are STRUCTURE COUNTS and DENOMINATORS (anchors, leaves per anchor, child counts, TRAIN rows per
anchor under three membership rules, EVAL rows / components per stratum) from committed files (bundle npz, member
`dag_snapshots.jsonl` last lines, graft_flatleaf train CSV). No correctness column of any arm was read and no fit was run.
For the registrar to append verbatim (or amend pre-data) at the END of `docs/judge_v2_program.md`; queue id proposed:
DEEP-SPLIT-COMPARE.

## 0. What the record already says (not re-derived)

- G13 (FAILED, VALID): D13 = P_fl - P(KC_0) = 0.8119 - 0.8334 = -0.0215 [-0.0301, -0.0125]; spread_KC 0.0112; 6,139 EVAL /
  5,628 CK-CLOSE components; DEFF 1.214 (`experiment_results/archv2/rp12_r2/g13_outcome.txt`).
- G13-BREAKDOWN (`docs/agents/results/G13-BREAKDOWN.json`; outcome 7f7b0fe3, POSTRUN ec557e60; correction ff9c5221):
  C-a1 HELD, D13_MMLU -0.0446 [-0.0566, -0.0321] (MMLU_PRO_LB 3,478 / 3,386; DEFF 1.046); C-a4 HELD, Delta -0.0192
  [-0.0292, -0.0089] (the loss opens below the anchors; D(2) -0.0023 UNDETERMINED, never parity); C-M UNDETERMINED,
  degenerate (KC-relabel = KC item-wise: KC's naming rule is not its edge); descent filing costs 11.5pp (D13_desc -0.1152),
  flatLeaf is the filing of record; C-b1 / C-b2 compare an ANCHORED tree with UNSUPERVISED k-means and are NOT evidence of
  discovered structure (ff9c5221 bracket). Measured DEFFs: 1.214 (tree vs KC), 1.341 (tree vs U-global), 1.449 (tree vs
  U-source), 1.147 (Delta). KC fit median 0.108 s single thread (seen).
- Lesson anchored-tree-comparisons (memory note of 2026-10-02): compare like with like; state each side's label information.
- MIX-LRT-SITE closed the GMM LR / BIC as a SITE CERTIFICATE (CONTEXT §5). Arm C below uses a GMM as a PARTITION RULE read
  by filing precision; it certifies nothing and does not reopen that line (stated in the registration).

Structure of B0 (lane r2, pinned commit M 2703f2c2; counted for this draft from the six member snapshot last lines):
52 depth-2 anchors (labels = the 52 declared classes, one-to-one), 133 leaves. Leaves per anchor k_a: 1 (20 anchors), 2 (17),
3 (4), 5 (5), 6 (2), 7 (3), 9 (1); 32 split anchors hold 113 leaves. Internal nodes below depth 2: 79 binary, 1 ternary
(IFEVAL). Max union depth 7 (MMLU_PRO_LB/math). Per source k_a sums 74 / 36 / 9 / 6 / 5 / 3 (MMLU / BBH / MATH / MUSR / IFEVAL /
GPQA).

## 1. Registration text (for the registrar)

## Registered <date> (before any code or call) — DEEP-SPLIT-COMPARE: holding B0's anchors and depth-2 frontier fixed, does a different label-free split rule below depth 2 (flat spherical k-means; PCA-GMM) file EVAL better than the vMF construction, and how much of class-conditioned k-means' edge is label information below depth 2? (zero calls; no build; CPU re-split from committed TRAIN vectors)

QUESTION AND KIND. Readout only: 0 LLM calls, 0 builds, 0 embedding calls. G13-BREAKDOWN located the tree's loss to KC below
depth 2 (C-a4 HELD), mostly on MMLU-Pro (C-a1 HELD). This test asks whether the SPLIT RULE used below depth 2 is the cause
(a label-free rule recovers the gap) or LABEL INFORMATION below depth 2 is (only the class-conditioned reference recovers
it). Revises nothing: G13, G13-BREAKDOWN, G11 stand as recorded.

OBJECTS (lane r2, pinned commit M 2703f2c2; committed files only; no DB opened).
 - Bundle `experiment_results/archv2/rp12_r2/B0/readouts/g13_bundle_flatleaf.{npz,json}` (eval_X / train_X 512-d qwen3 slice,
   eval_y, train_y, eval_comp, eval_fl, leaf_major, classes, item ids; 6,139 EVAL / 12,334 TRAIN after the multi-class
   exclusion 14 / 15); sha256 printed.
 - Tree: the six member `.../B0/<member>/seed_42/dag_snapshots.jsonl` LAST lines (ids, parentIds, childIds, depth, isLeaf,
   vmfMu); union id "<SOURCE>:<member id>", union depth = member depth + 1.
 - TRAIN depth-2 membership: `.../B0/graft_flatleaf/seed_42/validation/MAIN_union_routing_train_queries.csv` (leaf_id per
   TRAIN item; its depth-2 ancestor).
 - Timing: `.../B0/*/seed_42/diagnostics/run_manifest.json` duration_ms (seen in G13-BREAKDOWN; copied, not re-scored).
 - Readers reused, blob-pinned: `g13_comparator.py` 61d83ec7 (kc_correct, boot, check_sides), `flat_mix_mmlu.py` 555ae3ac
   (spherical_kmeans, kmeanspp), `g13_breakdown.py` c29fa1c3 (identity block, strata). New script TO BE BUILT:
   `tools/analysis/deep_split_compare.py --lane r2`; write-once outcome
   `experiment_results/archv2/rp12_r2/deep_split_compare_outcome.txt` (mode x); stdout UTF-8 (G13-BREAKDOWN E-1).

HYGIENE. Split draw 5a3e756, union pool pv2_1575de61bb20e977 (content-closed under CK-CLOSE-v2, residual disclosed).
`pool_guard.py --pool pv2_1575de61bb20e977` printed in the dry-run (a reader: rule 7, no construction or site null beside it).
Every fit (k-means, PCA, GMM, naming) is TRAIN-only (12,334 items); the script asserts no EVAL and no GATE item id in any fit
(check_sides). CPU lane single-threaded (OMP / OPENBLAS / MKL = 1), one heavy process.

THE ARMS. Common to all: the 52 depth-2 cells are B0's; every EVAL item is filed by flatLeaf = argmax cos(x, cell centroid)
over ALL cells of the arm (no anchor or source oracle); a cell is NAMED by the TRAIN-majority class of the TRAIN items the
same flatLeaf rule files into it (a cell with no TRAIN item takes its anchor's class; count printed). Fit set of a depth-2
cell a (F-tree, primary): the TRAIN items whose graft_flatleaf leaf lies under a. In the 20 anchors with k_a = 1 the cell
centroid is the normalised mean of F-tree members (B, C) or the anchor leaf's vmfMu (A).
 (A) B0 as built (R2's tree on lane r2; NOT bareq512_s42): the vMF construction (z-gate acceptanceZ 2.0, ascending-k
     first-accept, minClusterSize 55, slice 512), leaves = the 133 snapshot leaves, filing = P_fl of record (0.8119). One
     construction (seed 42); no seeds.
 (B) Flat spherical k-means per depth-2 cell: in each split anchor a, spherical k-means (k-means++ init, seed s) on F-tree(a)
     in 512-d at k = k_a (the tree's leaf count under a; 133 cells in total, per source 74 / 36 / 9 / 6 / 5 / 3); no minimum
     cell size.
 (C) PCA-GMM per depth-2 cell: in each split anchor a, PCA fitted on F-tree(a) (centred, unwhitened) to d = 16 dims (33 parameters per diagonal component, below the smallest planned cell of 59.4 items), then a
     Gaussian mixture with DIAGONAL covariance, k = k_a (matched), sklearn GaussianMixture(covariance_type='diag',
     init_params='k-means++', n_init=1, max_iter=200, reg_covar=1e-6, random_state=s); the hard partition of F-tree(a) by
     maximum responsibility defines the cells; each cell's centroid = normalised mean of its members in 512-d; EVAL filed by
     cosine flatLeaf like A and B (so the arm changes the PARTITION RULE only, not the filing geometry). An empty
     component is dropped and counted.
 (D) KC, the reference: class-conditioned spherical k-means, k_c = number of B0 leaves whose TRAIN majority is c
     (g13_comparator.kc_correct as recorded; P(KC_0) 0.8334).
 Seeds s = 0..4 for B, C, D; s = 0 is each arm's comparator of record; spread = max - min over s.

 DESCRIPTIVE ARMS (never deciding): B-gt = B with fit set = TRAIN items of a's declared class (the engine bootstrap's
 seeding; bridges B and D: differs from D only in k allocation, k_a vs k_c, and naming); B-anc = B with fit set = TRAIN items
 whose nearest anchor vmfMu is a (membership from the depth-2 frontier alone; the counts below show it is a poor partition
 for spread classes, e.g. MMLU_PRO_LB/math 418 vs F-tree 747); B-bis = bisecting spherical k-means to k_a leaves, always
 splitting the largest cell (binary and hierarchical like the tree, without its gate); C-32 / C-64 = C at d = 32 / 64 (65 / 129 parameters per component: thin cells, sensitivity only);
 C-BIC = C with k per anchor chosen by BIC over 1..2k_a+1 (total k printed against 133).

LABEL INFORMATION PER ARM (the lesson anchored-tree-comparisons; stated in the outcome's header).
 | arm | depth-2 cells | partition below depth 2 | cell naming | k |
 |---|---|---|---|---|
 | A | B0's anchors, seeded from TRAIN ground truth ("Seeding GMMs with 100% ground-truth data") | label-free vMF splits | TRAIN majority | its own |
 | B, C, B-bis | inherited from A (F-tree) | label-free | TRAIN majority | k_a from A |
 | B-anc | inherited (anchor vmfMu) | label-free | TRAIN majority | k_a from A |
 | B-gt | TRAIN class labels | label-free | TRAIN majority | k_a from A |
 | D (KC) | TRAIN class labels | TRAIN class labels (one class per prototype) | owned class | k_c from A's leaf names |
 All arms inherit the anchors; none uses labels to PARTITION below depth 2 except D; every arm reads TRAIN labels to NAME its
 cells (filing precision is undefined otherwise). F-tree also inherits A's leaf geometry through which anchor a TRAIN item is
 filed to: the depth-2 cells are A's, by design ("holding the depth-2 frontier fixed"), which favours A if anything.

READOUTS. All differences item-paired on the 6,139 EVAL items; 95% percentile intervals, whole CK-CLOSE components resampled,
B 2,000, seed 20260929 (G13's machinery).
 R1 OVERALL: P_A, P(B_s), P(C_s), P(D_s) with spreads; D_AB = P_A - P(B_0); D_AC = P_A - P(C_0); D_DB = P(D_0) - P(B_0);
    D_DC = P(D_0) - P(C_0) (descriptive); D13 re-printed as the identity.
 R2 PER SOURCE: the same contrasts per source (stratum intervals: components within the source); MMLU_PRO_LB SCOREABLE as in
    C-a1; BBH, MATH, MUSR, IFEVAL, GPQA DESCRIPTIVE-ONLY. Also per source the share of D_DB and of D13.
 R3 PER DEPTH (descriptive): every contrast stratified (i) by the subtree depth of the item's TRUE-class anchor (union depth
    2 = unsplit anchor, 3..7) and (ii) by k_a of that anchor (1 / 2-3 / 4-7 / >= 8); label-defined strata, independent of
    any arm's output. Also (iii) by the depth of A's flatLeaf leaf (G13-BREAKDOWN's strata; output-defined, printed beside).
 R4 SOFT-ASSIGNMENT ENTROPY for C (descriptive): for each EVAL item in a split anchor, the within-anchor GMM responsibilities
    of the anchor its filed cell belongs to; H in nats and H / log k_a; mean, median, share with max responsibility > 0.9;
    per source and per k_a stratum; TRAIN beside EVAL.
 R5 FIT TIME (descriptive, an order of magnitude only): time.perf_counter around each arm's fits (vectors already in memory),
    seeds 0-4, single thread; median and max; A's build time copied from the manifests (12 JVM threads, end-to-end). Machine
    state printed. Never a general cost ratio (G13-BREAKDOWN W6).

IDENTITY PRECONDITIONS (refuse on any miss, before any new number prints).
 I1 P_fl 0.8119, P(KC_s) 0.8334 / 0.8394 / 0.8340 / 0.8446 / 0.8413, D13 -0.0215 [-0.0301, -0.0125] reproduced to the
    printed digits.
 I2 52 anchors with labels = the 52 classes; 133 leaves; k_a per anchor and per source sums 74 / 36 / 9 / 6 / 5 / 3 as in
    the table of section 4 of the draft; child counts 79 x 2 + 1 x 3.
 I3 F-tree covers all 12,334 TRAIN items; per-anchor F-tree counts equal the draft's table (section 4) exactly.
 I4 B at k_a = 1 everywhere would reproduce the NCC-on-F-tree point (asserted as a code path, printed).

CRITERIA (one clause each way; otherwise UNDETERMINED; never read as parity: no TOST registered). Spread bar = the
comparator's spread (for D_DB the larger of spread_B and spread_KC).
 C-AB (SCOREABLE; INTERVAL AND POINT jointly, G13's form): HELD (the vMF construction beats flat spherical k-means at
      matched cells within the same anchors) iff D_AB's interval lies wholly above 0 AND D_AB > spread_B; REVERSED iff wholly
      below 0 AND D_AB < -spread_B.
 C-AC (SCOREABLE; same form against C_0 and spread_C).
 C-DB (SCOREABLE; same form): HELD (label information below depth 2 buys filing over a label-free split at matched cells)
      iff D_DB's interval lies wholly above 0 AND D_DB > max(spread_B, spread_KC); REVERSED iff wholly below 0 AND
      D_DB < -max(spread_B, spread_KC).
 C-AB-M, C-AC-M, C-DB-M (SCOREABLE; MMLU_PRO_LB only; the INTERVAL decides, C-a1's form; the stratum spread printed beside
      and the word "seed-fragile" appended if |D| < that spread): HELD / REVERSED as above on the interval alone.
 The six clauses are read separately; no family-wise correction (disclosed).
 DESCRIPTIVE-ONLY: R2 for the five other sources; R3; R4; R5; D_DC; every descriptive arm.

FALSIFIER. H-RULE: "a better label-free split rule below the anchors closes the G13 gap". F-RULE fires (H-RULE falsified at
this n) iff the 95% intervals of BOTH D_AB and D_AC lie wholly above -0.0108 (= -|D13| / 2): neither label-free rule
recovers half the gap. If F-RULE fires and C-DB HELD, the gap is attributed to label information below depth 2, and the
split-criterion follow-up (SPLIT-VMF in `docs/agents/plans/2026-10-02_g13_breakdown.md` §2) is not worth an engine change;
if C-AB or C-AC REVERSED, the split rule is implicated and SPLIT-VMF becomes the next registration.

SUPPORT (real n; planning discordances; DEFF transported from G13-BREAKDOWN's measured values; the run prints the measured).
 (a) Denominators: EVAL 6,139 items / 5,628 components; MMLU_PRO_LB 3,478 / 3,386; TRAIN 12,334. R3 strata (true-anchor
     k_a): 1: 1,215 / 1,002; 2-3: 2,066 / 1,834; 4-7: 2,465 / 2,421; >= 8: 393 / 380. True-anchor subtree depth 2..7: 1,215 /
     1,284 / 944 / 1,916 / 387 / 393 EVAL items.
 (b) SE = sqrt(disc / n x DEFF); MDE80 = 2.80 SE.
     C-AB: disc 0.08, DEFF 1.341 (tree vs k-means): SE 0.0042, MDE80 0.0117 (DEFF 1.449: 0.0044 / 0.0122).
     C-AC: disc 0.10, DEFF 1.341: SE 0.0047, MDE80 0.0131.
     C-DB: disc 0.08, DEFF 1.214 (KC side): SE 0.0040, MDE80 0.0111.
     MMLU (DEFF 1.046 measured in C-a1): C-AB-M disc 0.12: SE 0.0060, MDE80 0.0168; C-AC-M disc 0.14: SE 0.0065, MDE80 0.0182;
     C-DB-M disc 0.12: SE 0.0060, MDE80 0.0168.
 (c) Spread bars (planning): spread_B 0.008 [0.004, 0.016]; spread_C 0.012 [0.006, 0.025]; spread_KC 0.0112 (measured).
     Effective bar = max(MDE80, spread).
 (d) VERDICT LINES at the predictions: C-AB UNDETERMINED likely (|0.003| against 0.0117); C-AC UNDETERMINED likely (0.004
     against 0.0131); C-DB SCOREABLE, thin (0.018 against 0.0112); C-DB-M SCOREABLE (0.035 against 0.0168); C-AB-M, C-AC-M
     reachable only if the true effect exceeds 0.017-0.018. F-RULE is knife-edge at the predicted point (needs D_AB's lower
     end > -0.0108, i.e. point > about -0.0026 at SE 0.0042).
 (e) STRUCTURAL LEG: spread clauses do not shrink with n; A has no seed replication here (its construction-seed variance is
     not measured: a disclosed asymmetry, see "will not show").

PREDICTIONS (priors; P_A 0.8119 and P(D_0) 0.8334 are seen).
 B: P(B_0) 0.815 [0.800, 0.830]; D_AB -0.003 [-0.018, +0.012]; spread_B 0.008 [0.004, 0.016]; C-AB HELD 0.10, REVERSED 0.25,
    UNDETERMINED 0.65. Reason: within F-tree cells a flat k-means and the tree's greedy binary vMF splits optimise nearly the
    same objective; a class tail inside another anchor's cell is a minority there and cannot get its own named cell
    unless it forms a majority cluster, which KC achieves by owning the tail.
 C: P(C_0) 0.808 [0.790, 0.825]; D_AC +0.004 [-0.012, +0.020]; spread_C 0.012 [0.006, 0.025]; C-AC HELD 0.15, REVERSED 0.10.
 DB: D_DB +0.018 [+0.005, +0.032]; C-DB HELD 0.60, REVERSED 0.03.
 MMLU: D_AB-M -0.005 [-0.030, +0.020] (C-AB-M REVERSED 0.25); D_AC-M +0.005 [-0.020, +0.030] (C-AC-M HELD 0.15, REVERSED
    0.15); D_DB-M +0.035 [+0.015, +0.055] (C-DB-M HELD 0.65).
 F-RULE fires 0.45.
 Descriptive: P(B-gt_0) - P(D_0) -0.003 [-0.010, +0.004]; P(B-anc_0) - P(B_0) -0.020 [-0.050, 0.000]; P(B-bis_0) - P(B_0)
    -0.002 [-0.010, +0.006]; C-BIC total k 133 -> [90, 260], P(C-BIC_0) - P(C_0) 0.000 [-0.015, +0.015]; C-32 level with C [-0.010, +0.010]; C-64 below C by 0.005
    [-0.005, +0.020] (thin cells). R3: D_DB concentrated in k_a >= 4 strata (share 0.8 [0.5, 1.1]); in
    the k_a = 1 stratum all arms within 0.005 of each other. R4: mean H / log k_a 0.08 [0.02, 0.25] (diagonal GMM posteriors
    in 16-d are near-hard), share with max responsibility > 0.9 0.80 [0.55, 0.95]. R5: B fit per seed 0.05-1 s, C 0.5-20 s,
    D 0.108 s (seen), A 155 s members + 77.7 s graft at 12 threads (seen).

WHAT THIS RESULT WILL NOT SHOW (fixed before data). Anything about anchor-free trees (UNION-AF-ROUTE / RP13 owns that); that
the tree is needed for filing (G13 stands); parity of any two arms (no TOST); A's construction-seed variance (one build; the
seed floor of record is bareq's 2.6pp Top-1, another tree and metric, not transported); any split rule other than the four
arms at k matched to A (C-BIC and B-bis are descriptive); any certificate (no site null; MIX-LRT-SITE not reopened); any
routing or judging value (G14 owns routing); anything for another draw, recipe, embedder or slice; a wall-clock ratio beyond
this machine, thread count and language; a held-out claim beyond CK-CLOSE-v2's content-closure; that the vMF construction's
z-gate or minClusterSize is the cause (not varied here; GATE-LOOSE is a separate knob).

COST AND CONSEQUENCE. 0 calls, 0 cce, 0 builds. CPU: B, B-gt, B-anc, B-bis 4 x 5 seeds x 32 anchors of small spherical
k-means; C, C-32, C-64 3 x 5 seeds x 32 GMMs; C-BIC 5 seeds x 258 candidate GMMs; D reused (5 fits); about 60 bootstraps of
B 2,000: about 10-30 min single thread (estimate; the cost-estimator re-prices; the run prints its own). Agent time:
engine-coder about 3 h (deep_split_compare.py importing the pinned readers; dry-run printing I1-I4, the pins and the
denominators; selftest mutants at least: EVAL id in a fit, F-tree replaced by GT membership in B, k_a off by one, filing
restricted to the true anchor (oracle), C filing by likelihood instead of cosine, naming read from EVAL, a C spread taken over
fewer than 5 seeds, MMLU stratum leaking components across sources); reviewer READY; one run-operator pass; reviewer
post-run; registrar. Lane: CPU; it reads the pool (pool_guard), so no construction or site null runs beside it.
Consequence: decides whether the next construction knob is the split rule (SPLIT-VMF) or label ownership (HYB-LC), both
drafted unregistered in `docs/agents/plans/2026-10-02_g13_breakdown.md` §2.

## 2. Open questions

- Q1 (registrar, LOW): the brief calls arm A "the tree of record"; in KNOWLEDGE §1 the tree of record is bareq512_s42. The
  registration names A as "B0 of lane r2 (R2's tree)" to avoid the clash.
- Q2: A's construction-seed variance. Measuring it needs B0 rebuilds at other seeds (minutes each per the manifests, but a
  construction under rule 7); not in this test; a candidate add-on if C-AB lands near its bar.
- Q3: whether to keep C-BIC (it adds the largest CPU share; descriptive only).

## 3. Commands that verify this draft's inputs (read-only)

```
git cat-file -t 2703f2c2
git rev-parse HEAD:tools/analysis/g13_comparator.py HEAD:tools/analysis/flat_mix_mmlu.py HEAD:tools/analysis/g13_breakdown.py
python -c "import numpy as np;z=np.load('experiment_results/archv2/rp12_r2/B0/readouts/g13_bundle_flatleaf.npz');print(z['eval_X'].shape,z['train_X'].shape)"
python -c "import sklearn;print(sklearn.__version__)"     # 1.8.0 at drafting
python tools/analysis/pool_guard.py --pool pv2_1575de61bb20e977   # at run time only (a reader)
```

## 4. Structure table (counted for this draft; I2 / I3 check it)

Columns: source, anchor (= class), k_a (leaves under it), subtree max union depth, TRAIN under F-tree (primary), TRAIN under
B-anc (nearest anchor vmfMu), TRAIN in the class (B-gt / D fit set).

| source | anchor | k_a | maxd | F-tree | B-anc | class |
|---|---|---|---|---|---|---|
| MMLU_PRO_LB | math | 9 | 7 | 747 | 418 | 793 |
| MMLU_PRO_LB | physics | 7 | 6 | 798 | 691 | 778 |
| MMLU_PRO_LB | other | 7 | 5 | 514 | 438 | 555 |
| MMLU_PRO_LB | psychology | 7 | 5 | 543 | 516 | 476 |
| MMLU_PRO_LB | economics | 6 | 5 | 479 | 474 | 504 |
| MMLU_PRO_LB | biology | 6 | 5 | 470 | 395 | 381 |
| MMLU_PRO_LB | health | 5 | 5 | 461 | 395 | 410 |
| MMLU_PRO_LB | chemistry | 5 | 5 | 826 | 743 | 676 |
| MMLU_PRO_LB | computer science | 5 | 5 | 456 | 445 | 243 |
| MMLU_PRO_LB | law | 5 | 5 | 626 | 557 | 578 |
| MMLU_PRO_LB | history | 3 | 4 | 254 | 259 | 238 |
| MMLU_PRO_LB | engineering | 3 | 4 | 430 | 424 | 580 |
| MMLU_PRO_LB | business | 3 | 4 | 466 | 469 | 467 |
| MMLU_PRO_LB | philosophy | 3 | 4 | 294 | 278 | 298 |
| IFEVAL | ifeval | 5 | 4 | 297 | 290 | 325 |
| MATH | Intermediate Algebra | 2 | 3 | 154 | 172 | 166 |
| MATH | Algebra | 2 | 3 | 151 | 201 | 177 |
| MATH | Precalculus / Number Theory / Prealgebra / Geometry / Counting & Probability | 1 each | 2 | 69 / 122 / 72 / 126 / 102 | 88 / 153 / 167 / 140 / 192 | 80 / 91 / 110 / 80 / 69 |
| MUSR | team_allocation / murder_mysteries / object_placements | 2 each | 3 | 150 / 148 / 156 | 150 / 149 / 156 | 150 / 148 / 156 |
| GPQA | Biology / Physics / Chemistry | 1 each | 2 | 97 / 192 / 256 | 94 / 194 / 136 | 64 / 137 / 130 |
| BBH | 12 anchors with k_a = 2 (tracking_shuffled_objects_seven_objects, sports_understanding, temporal_sequences, logical_deduction_five_objects, formal_fallacies, date_understanding, disambiguation_qa, web_of_lies, movie_recommendation, ruin_names, salient_translation_error_detection, object_counting) | 2 each | 3 | 197 / 155 / 150 / 232 / 150 / 146 / 149 / 150 / 150 / 150 / 150 / 150 | 158 / 161 / 150 / 170 / 171 / 147 / 150 / 152 / 159 / 151 / 151 / 150 | 160 / 149 / 150 / 170 / 150 / 142 / 148 / 150 / 150 / 150 / 150 / 150 |
| BBH | 12 anchors with k_a = 1 (tracking_shuffled_objects_five_objects, hyperbaton, geometric_shapes, boolean_expressions, tracking_shuffled_objects_three_objects, causal_judgement, logical_deduction_three_objects, logical_deduction_seven_objects, snarks, penguins_in_a_table, reasoning_about_colored_objects, navigate) | 1 each | 2 | 120 / 152 / 150 / 150 / 151 / 104 / 140 / 99 / 109 / 88 / 153 / 150 | 159 / 153 / 151 / 155 / 151 / 104 / 146 / 155 / 108 / 88 / 160 / 150 | 156 / 150 / 150 / 150 / 151 / 103 / 145 / 155 / 107 / 88 / 150 / 150 |

Smallest planned cell (F-tree n / k_a over split anchors): IFEVAL 297 / 5 = 59.4 items, against 33 parameters per
diagonal component at d = 16 (primary), 65 at d = 32 and 129 at d = 64 (C-32 / C-64 are therefore sensitivity only).
