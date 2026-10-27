"""CONSTRUCTION-ARMS readout (docs/judge_v2_program.md, "## Registered 2026-10-05 (before any code or call) — CONSTRUCTION-ARMS: once
the greedy top-down shape and the leaf count are held fixed, does the split rule matter? Python approximations of top-down construction
(kappa-selected spherical k-means as the control; bisecting spherical k-means; diagonal GMM with per-node BIC; Ward cut top-down; HDBSCAN
descriptive) on MASSIVE, CLINC and the MMLU-Pro common set C, 5 seeds (zero calls; CPU; no Kotlin engine change; no certificate)",
L24757-L24772, registration commit 8f97b8b4, _as_of parent 85c82b4d). ZERO LLM / judge / embedding calls; CPU only; no JVM.

WORDS OF RECORD (registered, printed beside the verdict): every arm is an APPROXIMATION of top-down construction, the control included
(arm 1 stands in for the engine's vMF k-means; it is NOT the engine); a win means "worth a faithful engine arm", never "the engine should
change"; a non-win is not parity (no TOST).

LAUNCH SEQUENCE (zero calls; temp only under E: via scratch_dir; one heavy process; the C leg is a POOL READER under rule 7: run it in a pool
slot, never beside a construction or site null):
  python tools/analysis/scratch_dir.py --run -- python tools/analysis/construction_arms.py --selftest    # fixtures, values asserted
  python tools/analysis/scratch_dir.py --run -- python tools/analysis/construction_arms.py --mutants     # sandbox copies, table printed
  python tools/analysis/construction_arms.py --dry-run --mmlu-root <main checkout> [--data-root <S1 root>]
        # pool line FIRST, pins, census, L, m_min, |C|, TRAIN sizes, root-split timings and the COST ESTIMATE; no EVAL row read; 0 files
  python tools/analysis/construction_arms.py --run --mmlu-root <main checkout> [--data-root <S1 root>] [--workers 20] [--out <path>]
        # the readout of record: WRITE-ONCE outcome (mode x) + SHA256SUMS.txt, default
        # E:/TaxoArena_backup_<date>_construction_arms/construction_arms_outcome.txt; an existing path REFUSES before any read; the outcome
        # is NEVER committed (sha256-pin it, back it up)
  --data-root  INTENT-TRANSFER-S1's build root (intent_transfer_corpora_v1.db, intent_emb_qwen3.db, snapshots.db, run dirs);
               default env TAXOARENA_DATA_ROOT, else <main checkout>/.claude/worktrees/intent-s1-run
  --mmlu-root  snapshots.db / mmlu_pro_dataset_cache_v2.db / embeddings_cache.db / site-null CSVs (site_support's data root); default
               the main checkout (the part of this path before /.claude/worktrees/)
  --workers N  process pool for the fits (each process single-threaded: OMP / OPENBLAS / MKL = 1); default 1; REFUSES N > 22 (machine cap)

INSTRUMENT (imported UNCHANGED, LF blobs asserted at every entry point; another blob REFUSES):
  granularity_gt.py blob:bcb4240d (load_all: pins strict, census, M-AF / C-AF by the run log's Snapshot ID checked against the re-derived
      build; random_shape_dps = the GR2 matched-shape instrument; band, brier) and through it intent_transfer_s1.py blob:4e9d9d05
      (dendrogram_purity UNCHANGED, flat_leaf, majority, side_rows / fit_idx = the TRAIN-ONLY guard, make_arm, load_raw, sliced) and
      intent_transfer_s0.py blob:f662ceb1 (skmeans, unit, auroc, kish, pin_check);
  stability_vs_kmeans.py blob:a67bbf0a: the BASELINES seam (BaselineSpec; fit_bisecting with a pluggable split rule = arm 2), draw_triplets,
      load_mmlu (site_support's member sets, C, qwen3 256 vectors through staged copies);
  site_support.py blob:4612345c (triplet_topo; the pool guard of record printed FIRST through load_all); oos_tree_cells.py blob:caaced4a
      (paired_boot: the stratified component bootstrap of (d)); zc_common.py blob:c912dccf; cert_align_size.py blob:80f7bb78.
  CA-R0 the registration names oos_tree_cells blob 74a5cbf0; main carries caaced4a since f460d72c (the temp-on-E switch; the only change
      is `import tempfile; import scratch_dir`, git diff 665b817d f460d72c); caaced4a is pinned.

ARMS (registered; every arm fits on TRAIN only (C on MMLU-Pro) and reads no label; seeds 0-4 for arms 1-3):
  BRACKETED (registrar c9752a77, pre-data; the author's "F2 + F1" after READY_construction_arms c0e8feb1 NOT READY on B-1):
  (1) ENGINE-SKM (control; F2, ENGINE-LIKE SKM): best-first; node rule (EngineRule): kmax = min(maxK, floor(n / m_min), cap); for k = 2..kmax
      in order, spherical k-means (n_init 5, seed s); a candidate with a child < m_min stops the loop; J_k = ccs (port of
      StatisticsUtils.chanceCorrectedSeparation(List<ClusterStats>), L193-L219); k = 2 always kept; k > 2 kept iff J_k - J_kept >= marginalEps
      (negative = the bar), else stop (engine_select = performVmfKMeans L350-L398); COARSENING (coarsen = TaxonomySplitter L339-L381): under-
      floor fragments dropped while k > 2 and >= 2 survivors, then the weakest pair (two-cluster ccs) below bar x proposalAcceptMultiplier
      merged while k > 2, re-routing after each move; GATE (L425-L451): split iff every child >= m_min and every pair's ccs >= that level.
      maxK, marginalEps, proposalSeparationBar, proposalAcceptMultiplier and m_min are copied from the build TOMLs (absent keys =
      TaxonomyConfig.kt defaults 4 / -1.0 / - / 1.0) and printed (expected 4 / unset / 0.025 / 1.0 / 55).
      CA-R11 re-routing after a coarsening move sends EVERY node row to the nearest renormalised remaining child mean (routeToVmfs routes all
      targetQueries; the bracket's "re-route its items" read as the Kotlin does).
      REMAINING DIFFERENCES FROM THE ENGINE (words of record, printed beside every arm-1 line): (i) spherical k-means n_init 5 for vMF EM
      with the maximin init; (ii) the fixed qwen3 256-d slice for the per-node PCA (splitDim, splitWhiten); (iii) re-routing by the nearest
      renormalised child mean for the vMF posterior; (iv) no dJ / bootstrap acceptance, no sibling merger, no fixed-point iteration, no
      site null, no certificate; (v) best-first to exactly L with counted forced 2-means splits for the engine's own stopping.
  (1K) KAPPA-SKM (DESCRIPTIVE ONLY, the registered rule kept): for k = 2..min(8, cap), spherical k-means (n_init 5); k admissible iff every
      child has >= m_min TRAIN items AND min pairwise 1 - cos of child mean directions >= 0.025; the k maximising the size-weighted mean
      Banerjee kappa (ties smaller k); every readout, never in C-CA; its bootstrap seed draw comes after GMM-BIC's.
  (2) BISECT-SKM: stability_vs_kmeans.fit_bisecting (the seam: LARGEST live cluster by TRAIN count, ties earliest created; a split leaving a
      side empty marks the cluster unsplittable) with split = spherical 2-means n_init 5 (split_skm2).
  (3) GMM-BIC: best-first; node rule: diagonal GaussianMixture(k, reg_covar 1e-6, n_init 3) for k = 1..min(8, cap, n), minimum BIC (ties
      smaller k); k = 1 (or a fit predicting < 2 non-empty components) -> no split.
  (4) WARD: scipy linkage(TRAIN, ward) (Euclidean on the renormalised slice); the top L - 1 merges give L leaves (binary; seed-free).
  (5) HDBSCAN (DESCRIPTIVE ONLY): sklearn HDBSCAN(min_cluster_size = m_min) on TRAIN; leaves = its selected clusters + ONE noise leaf
      (under the root); hierarchy = the condensed tree's cluster ancestry of the selected clusters; never in the deciding criterion.
  EXPANSION (arms 1, 3): best-first; the largest leaf (TRAIN count; ties to the earliest node) that the arm's rule will split is split next,
      k capped at L - (current leaves) + 1; when no leaf is splittable by the rule and leaves < L, the largest leaf is FORCE-split by
      spherical 2-means (n_init 5, seed s); forced splits counted per arm x seed; forced share > 0.5 -> "rule mostly inactive".
      Arm 2's best-first is the seam's fit_bisecting (its rule always splits: forced share 0 by construction). A deciding arm that does
      not reach L leaves REFUSES (matched L is registered).
  FILING (every arm): EVAL items to the nearest leaf centroid (renormalised mean of the leaf's TRAIN members; HDBSCAN's noise leaf has no
      centroid). The engine rows file by flatLeaf (leaf vmfMu).
  m_min = minClusterSize copied from the builds' TOMLs (MASSIVE / CLINC: the M-AF / C-AF run dirs' diagnostics/config.toml; C: the four
      re-draw TOMLs experiment_configs/anchorfree/redraw/*.toml); all must agree per leg, else REFUSE; printed.
  KOTLIN DISTANCE OF THE OLD ARM 1 (now arm 1K; kept for the record): the engine's k-selection is StatisticsUtils.performVmfKMeans
      (src/main/kotlin/taxonomy/utils/StatisticsUtils.kt L340-L401): vMF EM per k = 2..maxK (maxK 4, TaxonomyConfig.kt L352), deterministic
      maximin init (no seed), on PCA-projected vectors (32 / 64 / 128 dims by node size, TaxonomySplitter.kt L138-L151); k grows while the
      chance-corrected separation improves by >= marginalEps (= the bar 0.025) and no cluster falls under minClusterFrac; then the
      splitter's floor (minClusterSize, L211-L214), the coarsening / min-pair gate at the bar (L280-L330) and the dJ / z acceptance.
      Kappa there is correctedKappa (Banerjee closed form + Newton refinement, StatisticsUtils.kt L24-L36) and scores the vMF density,
      it is not the k-selection objective. Arm 1 shares the floor, the 0.025 pairwise bar and the vMF/kappa family; it differs in: no
      PCA (256-d), hard spherical k-means with k-means++ seeds (n_init 5), k up to 8, k chosen by maximum size-weighted Banerjee kappa
      (closed form), no dJ / z gate, no merges / re-routing, best-first order instead of the engine's iteration loop. The engine rows
      (M-AF, C-AF, the four re-draw trees) are printed beside so the distance is measured.

READOUTS AND CRITERIA (registered):
  (a) DP_coarse (BRACKETED F1): S1.dendrogram_purity on ONE COMMON HIERARCHY per arm x seed: scipy linkage(method 'ward', Euclidean) on the
      arm's renormalised TRAIN leaf centroids (the filing centroids, one unweighted point per leaf; common_hier), identical for arms 1-4,
      1K, HDBSCAN (noise leaf outside the linkage, under the root) and the engine rows (their vmfMu); EVAL filed as registered, vs the coarse
      gold. Each arm's own-hierarchy DP is DESCRIPTIVE (a-own) with its GR2 print; the GR2 p97.5 for (a) places the same leaves at random
      on the common tree (granularity_gt.random_shape_dps, default_rng(20261004)); the number of distinct draw values is printed and "null
      degenerate (flat)" flagged when it is 1 (C-3). Children histograms and mean leaf depths printed for every arm x seed and the engines. The bootstrap uses dp_fast, asserted equal to S1.dendrogram_purity on every fit at the point (refuse otherwise).
  (c) LEAF FILING ACCURACY (fine): share of EVAL items whose fine gold equals the majority TRAIN fine gold of their leaf (S1.majority;
      ties to the smallest label id = code of the sorted label strings).
  D_jr = mean over arm j's seeds - mean over arm 1's seeds (WARD: its one fit); spread_1r = range of arm 1's five seed values.
  INTERVAL (crossed and paired): percentile bootstrap, B 2,000, numpy default_rng(20261006) (CA-R1: a fresh stream per corpus, MASSIVE then
      CLINC); per replicate, in this order: the EVAL CK-CLOSE components resampled once (rng.integers(G, size=G), as S0.comp_weights) and
      shared by all arms (paired over items), then five seed indices rng.integers(0, 5, 5) for ENGINE-SKM, BISECT-SKM, GMM-BIC (then arm 1K) in that
      order (crossed: independent per arm; arm 1's draw is shared by its three comparisons); WARD and HDBSCAN have no seed draw.
      Bounds np.percentile(., [2.5, 97.5]); the bootstrap SD is the SE reported.
  C-CA (THE ONE DECIDING CRITERION): ARM-WINS iff some (j, r), j in {BISECT-SKM, GMM-BIC, WARD}, r in {(a), (c)}, has on BOTH MASSIVE and
      CLINC D_jr > spread_1r AND the 95% lower bound > 0 (the winning pairs named); NO-ARM-WINS otherwise (exhaustive, exclusive).
      FAILS (rule 8) and F-CA (fires iff ARM-WINS) printed; ARM-1-AHEAD per (j, r, corpus) iff D < -spread AND upper bound < 0 (descr.).
  SUPPORT printed beside: n, components, Kish, SE(D) (bootstrap SD), the item-only SD (components resampled, seeds fixed), the realised
      seed term sqrt(var_j/5 + var_1/5), DEFF_total = Kish x (SE / SE_item)^2, n_eff = n / DEFF_total, MDE80 per corpus = spread + 0.84 SE,
      joint = spread + 1.25 SE, the registered (a)-(g) values and the verdict line (f).
  DESCRIPTIVE: (b) seed-pair triplet disagreement (10 pairs, arms 1-3; 100,000 triplets on TRAIN, RandomState(20261004) via
      stability_vs_kmeans.draw_triplets; on C site_support's first draw), all-triplets AND resolved-in-both, unresolved shares beside; 90%
      TRAIN-subsample stability for EVERY arm (subsample s = sorted default_rng(20261004 + 100 + s).choice(n, floor(0.9 n)), s 0-4; arms 1-3
      fitted with seed s on subsample s; disagreement over the 10 subsample pairs on the triplets whose three items lie in both); (d) CLINC
      OOS AUROC (max-cos to the arm's leaf centroids; in-scope EVAL vs every kept EVAL OOS row) with D vs arm 1 and oos_tree_cells'
      paired stratified component bootstrap; the C leg (DP vs the MMLU-Pro category, in-sample on C; (b)); HDBSCAN everywhere with its noise
      share; the engine rows; forced-split counts; leaf-size distributions.
  IDENTITY PRECONDITIONS (refuse, nothing written): I1 DP(M-AF) 0.67043, DP(C-AF) 0.47730; I2 A(C-AF) 0.96776; I3 |C| = 2,772. I3 at load;
      I1 / I2 right after EVAL is unlocked and before any arm readout.
  PREDICTIONS P1-P8 (bands closed; Brier for P5 / P7) printed with HELD / FAILED.

BUILDER'S READINGS (printed; the registrar confirms or brackets BEFORE --run):
  CA-R0 oos_tree_cells blob (above). CA-R1 one default_rng(20261006) per corpus and the draw order above. CA-R2 node seeds: the rule's
  k-means / GMM at node id c and k use seed s x 1000003 + 17 c + k (restart r of n_init: skmeans seed x 16 + r); the forced split slot 9.
  CA-R3 "largest" = TRAIN count, ties to the smaller node id; a forced split that leaves a side empty marks the leaf unforceable. CA-R4 GMM:
  a best-BIC fit whose prediction has < 2 non-empty components is "not split by the rule". CA-R5 HDBSCAN: selected cluster of label j =
  the lowest common ancestor (condensed cluster tree) of its members' fall-out clusters, verified to hold exactly label j's members (else
  the selected clusters hang flat under the root, printed); the noise leaf is a leaf (also in (b)). CA-R6 subsample stream and the
  "both subsamples" triplet mask (above). CA-R7 the MMLU-Pro category of a C item = the category of the FIRST mmlu_pro row (by id) whose
  text hashes to the item's q_ id (the row site_support.text_of_qid reads); conflicting duplicates counted and printed. CA-R8 the re-draw
  engine rows on C file by flatLeaf to the trees' leaf vmfMu, the hierarchy = BFS first-parent over childIds. CA-R9 identity first:
  the TRAIN matrices are frozen (fit_idx audit) before EVAL is unlocked; the fits read only those matrices. CA-R10 P3's forced share =
  forced / (forced + rule splits), mean over seeds, scored on MASSIVE and CLINC (C printed); P6 scored on MASSIVE and CLINC (event: both
  bands HELD and arm 1's unresolved share above BISECT-SKM's on both); P5 Brier = (0.10 - [ARM-WINS])^2 (restated) (the two-outcome sum beside).

DELTA (after READY c0e8feb1; bracket c9752a77): F2 (EngineRule, ccs, engine_select, coarsen, min_pair_sep; knobs from the TOMLs), arm 1K,
  F1 (common_hier, shape_stats, (a-own) + GR2 on both trees), C-1 kill tests for R1 / R2 / R6 / R7, C-2 seed-corrected SE (x 1.25) printed
  with the anti-conservative note, C-3 joint both-resolved coverage + distinct-draw count / degenerate flag, C-4 C-leg disclosure; Support
  (e)-(g), the verdict line and P2-P5 restated as bracketed; P8 on the common construction.
SELFTEST (130 value checks, about 15 s; numbers of the first build below kept for the record) (103 value checks, about 12 s): SELFTEST_DOC below; value-asserting, end-to-end through main(["--run"]) on planted worlds whose
  answers are known in closed form (E1 ARM-WINS, E2 NO-ARM-WINS, E3 one corpus only + the no-OOS skip path, E4 lower bound > 0 but
  D <= spread, E6 matched-L refusal) and the REAL arms + REAL loaders on on-disk fixture roots (E5).
MUTANTS (2026-10-05; `--mutants --jobs 12`: copies in a scratch sandbox, TMP / TEMP / TMPDIR / TAXOARENA_TMP inside it, the replacement
  applied above the MUTANTS list only; the no-op control C0 SURVIVED): DELTA 74 / 74 KILLED (first build 55 / 55). Delta mutants: X56 engine
  maxK 8 | X57 increment always accepted | X58 increment loop without the stop | X59 coarsening merge dropped | X60 min-pair gate dropped |
  X61 ccs pairFrac n_c^2 | X62 fragment absorption dropped | X63 common hierarchy average-link | X64 (a) on the own hierarchy | X65 seed
  correction 1.0 | X66 C-4 disclosure unprinted | X67 arm 1K in C-CA | X68 P8 vs the engine's own tree | X69 = reviewer R1 centroids not
  renormalised | X70 = R2 control dropped from the matched-L refusal | X71 = R6 GMM spherical | X72 = R7 arm-1K kappa unweighted | X73
  coverage printed as the unresolved share | X74 degenerate flag never raised. First-build table:
  X01 C-CA either corpus | X02 D >= spread | X03 lb >= 0 | X04 spread conjunct dropped | X05 interval conjunct dropped | X06 first winner
  only | X07 HDBSCAN deciding, WARD dropped | X08 D sign | X09 spread = SD | X10 spread from arm j (wrong population) | X11 seeds paired |
  X12 seeds not resampled | X13 components not resampled | X14 percentiles 5/95 | X15 bootstrap seed + 1 | X16 seed draw order | X17 leaf
  majority from EVAL (wrong side) | X18 DP fine | X19 dp_fast without the child term | X20 min kappa | X21 kappa floor dropped | X22 bar
  dropped | X23 kappa cap ignored | X24 GMM max BIC | X25 GMM k = 1 never compared | X26 smallest first | X27 forced not counted | X28 cap
  off by one | X29 inactive threshold 0.9 | X30 Ward replay | X31 identity not refused | X32 I2 ignored | X33 I3 ignored | X34 write-once
  pre-check dropped (the refusal must precede any read) | X35 F-CA FIRES unprinted | X36 FAILS unprinted | X37 P5 wrong event | X38 open
  bands | X39 ARM-1-AHEAD without the interval | X40 workers cap removed | X41 L check removed | X42 code pins unchecked | X43 dry run
  unlocks EVAL | X44 support on the first corpus only | X45 unresolved = topology 0 | X46 subsample 1.0 | X47 WARD seeded | X48 matched-L
  refusal dropped | X49 item-only SD from crossed replicates | X50 arms fitted on EVAL | X51 P7 skip line dropped | X52 subsample
  unresolved = topology 0 | X53 seed pairs first pair only | X54 P6 event without the unresolved conjunct | X55 GMM cap ignored.
  First pass 26 / 49 applied-and-killed (the harness counted the mutant list's own literals; X17, X25 (equivalent as written), X34, X45,
  X48 survived); fixed by head-only replacement, X25 re-stated, new checks (TRAIN-majority unit, loader-call count before the write-once
  refusal, brute-force (b) topologies, E6, the prediction-branch unit); second pass X15 / X23 survived (literal stream in the independent
  loop; the cap read on the cached table), fixed.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"

import argparse        # noqa: E402
import collections     # noqa: E402
import contextlib      # noqa: E402
import datetime        # noqa: E402
import functools       # noqa: E402
import io              # noqa: E402
import json            # noqa: E402
import math            # noqa: E402
import re              # noqa: E402
import sqlite3         # noqa: E402
import subprocess      # noqa: E402
import sys             # noqa: E402
import time            # noqa: E402
import warnings        # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import zc_common as ZC                 # noqa: E402  (imports scratch_dir: temp on E:, removed at exit)
import scratch_dir                     # noqa: E402
import granularity_gt as GG            # noqa: E402
import stability_vs_kmeans as SVK      # noqa: E402
import site_support as SSUP            # noqa: E402
import oos_tree_cells as OTC           # noqa: E402
import cert_align_size as CA           # noqa: E402

import numpy as np                     # noqa: E402

S1 = GG.S1
S0 = GG.S0
SPL = GG.SS                            # split_side
SRC = os.path.dirname(os.path.abspath(GG.__file__))
TAG = "[CONSTRUCTION-ARMS]"
REG = ("docs/judge_v2_program.md L24757-L24772 (registration commit 8f97b8b4, _as_of parent 85c82b4d), \"## Registered 2026-10-05 "
       "(before any code or call) \u2014 CONSTRUCTION-ARMS: ...\"")
PINNED_CODE = {"granularity_gt.py": "bcb4240de6963fd24960b58ce5143087ba7a5025",
               "intent_transfer_s1.py": "4e9d9d05fbdf14d0a85966b4c897cfbfd779186d",
               "intent_transfer_s0.py": "f662ceb19738f515972871f5963f5dcfc764a271",
               "stability_vs_kmeans.py": "a67bbf0a673cffabd7dccdced95b23b11a4ac01b",
               "site_support.py": "4612345ce9c5fbc39bfaf9f520127ccf683e1591",
               "oos_tree_cells.py": "caaced4a9156262f2f94fdef1a1c2ac01fa654b8",
               "zc_common.py": "c912dccfb19960d256344180814788b424d8cd16",
               "cert_align_size.py": "80f7bb788f4feac0538eb1826e3febdfd79fa81d"}
CORPORA = ("massive", "clinc")
ENGINE = {"massive": "M-AF", "clinc": "C-AF"}
L_REG = {"massive": 84, "clinc": 139, "mmlu": 81}
C_REG = 2772
IDENTITY = {"dp_massive": "0.67043", "dp_clinc": "0.47730", "A_T": "0.96776", "C": C_REG}
DIM = 256
SEEDS = (0, 1, 2, 3, 4)
KMAX = 8                               # GMM-BIC's k range
MAXK_ENGINE = 4                        # arm 1 (F2): TaxonomyConfig.kt L352 maxK, not overridden by the M-AF / C-AF TOMLs
COMMON_LINK = "ward"                   # F1: the one common hierarchy over every arm's leaves (scipy linkage on the leaf centroids)
SEED_CORR = len((0, 1, 2, 3, 4)) / float(len((0, 1, 2, 3, 4)) - 1)   # C-2: n / (n - 1) = 1.25
SEP_BAR = 0.025
N_INIT_SKM = 5
N_INIT_GMM = 3
REG_COVAR = 1e-6
FORCE_SLOT = 9
B_BOOT = 2000
SEED_BOOT = 20261006
N_RANDOM = 200
SEED_RANDOM = 20261004
TRIPLETS = 100_000
SEED_TRIP = 20261004
SUB_FRAC = 0.9
SUB_BASE = 20261004 + 100
MAX_WORKERS = 22
CONTROL = "ENGINE-SKM"
DECIDING = ("BISECT-SKM", "GMM-BIC", "WARD")
SEEDED = ("ENGINE-SKM", "BISECT-SKM", "GMM-BIC", "KAPPA-SKM")        # bootstrap seed draws in this order (arm 1K drawn last)
ALL_ARMS = ("ENGINE-SKM", "BISECT-SKM", "GMM-BIC", "WARD", "HDBSCAN", "KAPPA-SKM")
DESCRIPTIVE_ARMS = ("HDBSCAN", "KAPPA-SKM")
READOUTS = ("a", "c")
RNAME = {"a": "(a) DP_coarse (common hierarchy)", "c": "(c) leaf filing accuracy (fine)"}
INACTIVE = 0.5
OUTCOME = "construction_arms_outcome.txt"
REDRAW_TOMLS = ("af_clean_s42.toml", "af_s137.toml", "af_s2048.toml", "af_s42_o1.toml")
# registered support (quoted, not re-derived)
REG_SE = {("a", "massive"): 0.0110, ("a", "clinc"): 0.0156, ("c", "massive"): 0.0099, ("c", "clinc"): 0.0158}       # restated c9752a77
REG_MDE_JOINT = {("a", "massive"): 0.045, ("a", "clinc"): 0.075, ("c", "massive"): 0.044, ("c", "clinc"): 0.076}
REG_SUPPORT = ("registered Support (a)-(g) as RESTATED by the registrar's bracket (c9752a77): MASSIVE 4,946 EVAL / 4,923 components (Kish "
               "DEFF 1.0093), CLINC 6,672 / 6,672 (1.0000); item SE transported (a) 0.0069 / 0.0033, (c) 0.0049 / 0.0042; seed term MASSIVE "
               "0.00858 (transported), CLINC 0.01523 (planning spread 0.056, declared); SE(D) (a) 0.0110 / 0.0156, (c) 0.0099 / 0.0158; "
               "seed-corrected seed term 0.0096 / 0.0170; DEFF_total (a) 2.57 / 22.3, (c) 4.12 / 14.1; n_eff (a) 1,925 / 299, (c) 1,200 / 472; "
               "joint MDE80 (a) 0.045 / 0.075, (c) 0.044 / 0.076 (deciding about 0.076); floor about 0.075 with 5 seeds")
VERDICT_LINE = ("VERDICT LINE (registered (f), restated): the largest predicted |D_jr| under the restated P2-P4 (0.03, GMM-BIC D_a) lies 0.03 "
                "from the bar 0, below the MDE80 0.076: DESCRIPTIVE-ONLY at the prediction; C-CA is scored as registered; NO-ARM-WINS is not parity")
ARM1_WORDS = ("arm 1 = ENGINE-LIKE SKM, NOT the engine: (i) spherical k-means n_init 5 for vMF EM / maximin init; (ii) fixed qwen3 256-d slice "
              "for the per-node PCA; (iii) re-routing by the nearest renormalised child mean for the vMF posterior; (iv) no dJ / bootstrap "
              "acceptance, sibling merger, fixed-point iteration, site null or certificate; (v) best-first to exactly L with counted forced "
              "2-means splits for the engine's own stopping")
WORDS = ("WORDS OF RECORD (registered, bracketed): every arm is an APPROXIMATION (arm 1 is a stand-in, NOT the engine); a win means \"worth a "
         "faithful engine arm\", never \"the engine should change\"; a non-win is not parity (no TOST); " + ARM1_WORDS)
NOT_SHOW = ("WHAT THIS RESULT WILL NOT SHOW (registered): anything about the engine itself (every arm is an approximation; the engine rows "
            "are descriptive); parity of any two rules (no TOST; NO-ARM-WINS is not \"the rule does not matter\"); a certificate or site-null "
            "property; MMLU-Pro EVAL, routing or judged value; other embedders, slices, draws or leaf counts; HDBSCAN in any deciding sense.")
P1 = {("a", "massive"): (0.62, 0.50, 0.72), ("a", "clinc"): (0.44, 0.33, 0.55),
      ("c", "massive"): (0.72, 0.60, 0.82), ("c", "clinc"): (0.85, 0.75, 0.93)}
P_D = {"BISECT-SKM": {"a": (0.00, -0.04, 0.04), "c": (0.00, -0.03, 0.03)},         # P2-P5 restated (informed), c9752a77
       "GMM-BIC": {"a": (-0.03, -0.10, 0.03), "c": (-0.02, -0.06, 0.02)},
       "WARD": {"a": (0.015, -0.03, 0.06), "c": (0.005, -0.03, 0.04)}}
P_PRED = {"BISECT-SKM": "P2", "GMM-BIC": "P3", "WARD": "P4"}
P3_FORCED = (0.40, 0.00, 0.90)
P5_WIN = 0.10
P6_BAND = (0.03, -0.05, 0.10)
P7_PROB, P7_MARGIN = 0.70, 0.010
P8_BAND = (-0.05, -0.15, 0.03)
F5 = "%+.5f"


class Refused(SystemExit):
    pass


def refuse(msg):
    print("%s REFUSED: %s" % (TAG, msg))
    raise Refused("%s REFUSED: %s" % (TAG, msg))


def f5(x, fmt=F5):
    return "n/a" if x is None or not np.isfinite(x) else fmt % x


def check_code_pins(pinned=None):
    got = {}
    for name, want in sorted((pinned or PINNED_CODE).items()):
        b = ZC.git_blob(os.path.join(SRC, name))
        got[name] = b
        if b != want:
            refuse("%s is blob:%s, the instrument of record is blob:%s (imported unchanged)" % (name, b, want))
    return got


def main_checkout():
    p = os.path.abspath(ZC.ROOT).replace("\\", "/")
    k = p.find("/.claude/worktrees/")
    return p[:k] if k >= 0 else p


# ================================================================================================ split rules and fits
def skm_best(Xs, k, seed_int, n_init=N_INIT_SKM):
    """Spherical k-means (intent_transfer_s0.skmeans, unchanged), best of n_init restarts by sum of max-cos; restart r seeds seed x 16 + r.
    -> (labels, centroids)."""
    best = None
    for r in range(n_init):
        Cm = S0.skmeans(Xs, k, seed_int * 16 + r)
        sim = Xs @ Cm.T
        obj = float(sim.max(axis=1).sum())
        if best is None or obj > best[0]:
            best = (obj, np.argmax(sim, axis=1), Cm)
    return best[1], best[2]


def split_skm2(Xs, seed_int):
    """Arm 2's split rule through the seam (stability_vs_kmeans.fit_bisecting split=): spherical 2-means, n_init 5 -> labels in {0, 1}."""
    if len(Xs) < 2:
        return np.zeros(len(Xs), dtype=np.int64)
    return skm_best(Xs, 2, seed_int)[0]


def kappa_banerjee(rbar, d):
    if rbar >= 1.0 - 1e-12:
        return 1e4
    return float(rbar * (d - rbar * rbar) / (1.0 - rbar * rbar))


def node_seed(seed, c, k):
    return int(seed) * 1000003 + 17 * int(c) + int(k)


def _relabel(lab):
    u, inv = np.unique(lab, return_inverse=True)
    return inv.astype(np.int64), len(u)


def ccs(X, lab):
    """StatisticsUtils.chanceCorrectedSeparation (StatisticsUtils.kt L193-L219), on the rows X grouped by lab: 1 - wWithin / E[wWithin],
    wWithin = sum_c (n_c^2 - |sum_c|^2), wTotal = n^2 - |sum|^2, E = wTotal x sum_c n_c (n_c - 1) / (n (n - 1)); 0 on degenerate input."""
    groups = [X[lab == v] for v in np.unique(lab)]
    groups = [g for g in groups if len(g)]
    n = float(sum(len(g) for g in groups))
    if not groups or n < 2:
        return 0.0
    tot = np.zeros(X.shape[1])
    ww, pf = 0.0, 0.0
    for g in groups:
        sm = g.sum(0)
        tot += sm
        ww += len(g) * len(g) - float(sm @ sm)
        pf += len(g) * (len(g) - 1.0)
    wt = n * n - float(tot @ tot)
    exp = wt * pf / (n * (n - 1.0))
    return 0.0 if exp <= 1e-10 else 1.0 - ww / exp


def engine_select(sizes, deltas, min_size, eps, kmax):
    """performVmfKMeans' k loop (StatisticsUtils.kt L350-L398): k = 2..kmax ascending; a candidate with a cluster < min_size stops the
    loop; k = 2 is always taken; a larger k is taken iff its separation gains >= eps over the current best, else the loop stops.
    sizes / deltas: {k: ...}. -> chosen k or None."""
    best, bd = None, None
    for k in range(2, kmax + 1):
        if k not in sizes or min(sizes[k]) < min_size:
            break
        if best is None:
            best, bd = k, deltas[k]
        elif deltas[k] - bd >= eps:
            best, bd = k, deltas[k]
        else:
            break
    return best


def route(Xs, lab):
    """routeToVmfs (TaxonomySplitter.kt L264-L280): every node row to the argmax dot with the children's mean directions."""
    vs = sorted(set(lab.tolist()))
    mu = S0.unit(np.vstack([Xs[lab == v].mean(0) for v in vs]))
    return np.argmax(Xs @ mu.T, axis=1).astype(np.int64)


def coarsen(Xs, lab, m_min, bar):
    """The splitter's stabilisation loop (TaxonomySplitter.kt L339-L381): under-floor fragments dropped and re-routed (k > 2, >= 2
    survivors), else the weakest pair (pairwise ccs) below the bar merged and re-routed while k > 2. -> routed labels 0..k-1."""
    lab = route(Xs, _relabel(lab)[0])
    while True:
        lab = _relabel(lab)[0]
        k = int(lab.max()) + 1
        sizes = np.bincount(lab, minlength=k)
        if (sizes < m_min).any():
            if k <= 2:
                break
            surv = [v for v in range(k) if sizes[v] >= m_min]
            if len(surv) < 2:
                break
            keep = np.isin(lab, surv)
            mu = S0.unit(np.vstack([Xs[lab == v].mean(0) for v in surv]))
            lab = np.argmax(Xs @ mu.T, axis=1).astype(np.int64)
            del keep
            continue
        weak, wi, wj = np.inf, -1, -1
        for i in range(k):
            for j in range(i + 1, k):
                m = (lab == i) | (lab == j)
                sp = ccs(Xs[m], lab[m])
                if sp < weak:
                    weak, wi, wj = sp, i, j
        if wi >= 0 and weak < bar and k > 2:
            lab = route(Xs, np.where(lab == wj, wi, lab))
            continue
        break
    return _relabel(lab)[0]


def min_pair_sep(Xs, lab):
    k = int(lab.max()) + 1
    out = np.inf
    for i in range(k):
        for j in range(i + 1, k):
            m = (lab == i) | (lab == j)
            out = min(out, ccs(Xs[m], lab[m]))
    return out


ENGINE_DEFAULTS = dict(maxK=4, eps=-1.0, bar=0.025, mult=1.0)     # TaxonomyConfig.kt maxK 4, marginalEps -1.0, multiplier 1.0


class EngineRule(object):
    """Arm 1 (F2, engine-like; author's choice after READY_construction_arms B-1): spherical k-means (n_init 5) stands in for the vMF EM
    for k = 2..min(maxK 4, cap); k chosen by engine_select (separation increment >= the bar 0.025, minSize = int(n x m_min / n));
    the splitter's floor pre-check (TaxonomySplitter.kt L211-L214), the coarsening loop and the min-pair gate (L425-L451) at the bar.
    Not modelled: the PCA projection, soft EM, the dJ / z acceptance, merges and re-trickle."""

    def __init__(self, m_min, bar=SEP_BAR, kmax=MAXK_ENGINE, n_init=N_INIT_SKM, eps=None):
        self.m_min, self.bar, self.kmax, self.n_init = m_min, bar, kmax, n_init
        self.eps = bar if eps is None else eps          # marginalEps; negative in the TOML = barFor (the bar)
        self.cache = {}

    def table(self, c, Xs, seed):
        if c not in self.cache:
            n = len(Xs)
            min_size = self.m_min                       # registered: actualMaxK with minSize = m_min
            tab = {}
            for k in range(2, min(self.kmax, n // min_size) + 1):
                lab, _cm = skm_best(Xs, k, node_seed(seed, c, k), self.n_init)
                tab[k] = (lab, np.bincount(lab, minlength=k), ccs(Xs, lab))
            self.cache[c] = (min_size, tab, {})
        return self.cache[c]

    def __call__(self, c, Xs, cap, seed):
        if len(Xs) < 2 * self.m_min:
            return None
        min_size, tab, memo = self.table(c, Xs, seed)
        kmax = min(self.kmax, cap)
        if kmax not in memo:
            k = engine_select({j: t[1] for j, t in tab.items()}, {j: t[2] for j, t in tab.items()}, min_size, self.eps, kmax)
            res = None
            if k is not None and tab[k][1].min() >= self.m_min:
                lab = coarsen(Xs, tab[k][0], self.m_min, self.bar)
                if lab.max() >= 1 and np.bincount(lab).min() >= self.m_min and min_pair_sep(Xs, lab) >= self.bar:
                    res = lab
            memo[kmax] = res
        return memo[kmax]


class KappaRule(object):
    """Arm 1K (DESCRIPTIVE; the registered kappa rule kept after F2): the per-node table is computed once (the cap only shrinks) and read under the current cap."""

    def __init__(self, m_min, bar=SEP_BAR, kmax=KMAX, n_init=N_INIT_SKM):
        self.m_min, self.bar, self.kmax, self.n_init = m_min, bar, kmax, n_init
        self.cache = {}

    def table(self, c, Xs, cap, seed):
        if c not in self.cache:
            n, d = Xs.shape
            tab = {}
            for k in range(2, min(self.kmax, cap) + 1):
                if n < k * self.m_min:
                    tab[k] = (False, -np.inf, None)
                    continue
                lab, _cm = skm_best(Xs, k, node_seed(seed, c, k), self.n_init)
                sizes = np.bincount(lab, minlength=k)
                if sizes.min() < self.m_min:
                    tab[k] = (False, -np.inf, None)
                    continue
                means = np.vstack([Xs[lab == j].mean(0) for j in range(k)])
                r = np.linalg.norm(means, axis=1)
                mu = means / np.where(r > 0, r, 1.0)[:, None]
                cs = mu @ mu.T
                sep = min(1.0 - cs[i, j] for i in range(k) for j in range(i + 1, k))
                if sep < self.bar:
                    tab[k] = (False, -np.inf, None)
                    continue
                score = float(sum(sizes[j] * kappa_banerjee(float(r[j]), d) for j in range(k)) / n)
                tab[k] = (True, score, lab)
            self.cache[c] = tab
        return self.cache[c]

    def __call__(self, c, Xs, cap, seed):
        tab = self.table(c, Xs, cap, seed)
        best = None
        for k in sorted(tab):
            ok, sc, lab = tab[k]
            if k <= cap and ok and (best is None or sc > best[0]):
                best = (sc, lab)
        return None if best is None else best[1]


class GmmRule(object):
    """Arm 3's node rule (registered): diagonal GMM, k = 1..min(8, cap, n) by minimum BIC (ties smaller k); k = 1 -> no split."""

    def __init__(self, kmax=KMAX, n_init=N_INIT_GMM, reg=REG_COVAR):
        self.kmax, self.n_init, self.reg = kmax, n_init, reg
        self.cache = {}

    def table(self, c, Xs, cap, seed):
        if c not in self.cache:
            from sklearn.mixture import GaussianMixture
            tab = {}
            for k in range(1, min(self.kmax, cap, len(Xs)) + 1):
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    gm = GaussianMixture(n_components=k, covariance_type="diag", reg_covar=self.reg, n_init=self.n_init,
                                         random_state=node_seed(seed, c, k) % (2 ** 32)).fit(Xs)
                    tab[k] = (float(gm.bic(Xs)), gm.predict(Xs).astype(np.int64))
            self.cache[c] = tab
        return self.cache[c]

    def __call__(self, c, Xs, cap, seed):
        if len(Xs) < 2:
            return None
        tab = self.table(c, Xs, cap, seed)
        ks = [k for k in sorted(tab) if k <= cap]
        if not ks:
            return None
        kb = min(ks, key=lambda k: (tab[k][0], k))
        if kb == 1:
            return None
        lab, m = _relabel(tab[kb][1])
        return lab if m >= 2 else None


def best_first(X, L, seed, rule, kind):
    """The registered EXPANSION (arms 1 and 3). -> H."""
    n = len(X)
    rows = {0: np.arange(n)}
    parent = {}
    live, dead = [0], set()
    nid, forced, rsplits = 1, 0, 0
    while len(live) < L:
        cap = L - len(live) + 1
        order = sorted(live, key=lambda c: (-len(rows[c]), c))
        chosen = None
        for c in order:
            if len(rows[c]) < 2:
                continue
            lab = rule(c, X[rows[c]], cap, seed)
            if lab is not None:
                chosen = (c, lab, False)
                break
        if chosen is None:
            for c in order:
                if len(rows[c]) < 2 or c in dead:
                    continue
                lab = split_skm2(X[rows[c]], node_seed(seed, c, FORCE_SLOT))
                if lab.min() == lab.max():
                    dead.add(c)
                    continue
                chosen = (c, lab, True)
                break
        if chosen is None:
            break
        c, lab, isf = chosen
        for v in sorted(set(lab.tolist())):
            rows[nid] = rows[c][lab == v]
            parent[nid] = c
            live.append(nid)
            nid += 1
        live.remove(c)
        forced += int(isf)
        rsplits += int(not isf)
    leaves = sorted(live)
    pos = {c: i for i, c in enumerate(leaves)}
    lab = np.empty(n, dtype=np.int64)
    for c in leaves:
        lab[rows[c]] = pos[c]
    nm = {c: ("N%06d" % c) for c in rows}
    return dict(kind=kind, lab=lab, nL=len(leaves), leaves=[nm[c] for c in leaves], parent={nm[c]: nm[p] for c, p in parent.items()},
                root=nm[0], forced=forced, rule_splits=rsplits, noise=None)


def svk_to_H(h, kind):
    """stability_vs_kmeans Hier {lab, L, internal: [(frozenset of leaf idx, rank)]} -> H (parent = smallest containing internal set)."""
    nL = int(h["L"])
    sets = sorted({frozenset(s) for s, _r in h["internal"] if 0 < len(s) < nL}, key=lambda s: (len(s), sorted(s)))
    names = ["I%04d" % i for i in range(len(sets))]
    leaves = ["L%04d" % j for j in range(nL)]
    parent = {}

    def up(S, strict_self=None):
        for i, T in enumerate(sets):
            if S < T:
                return names[i]
        return "ROOT"
    for j in range(nL):
        parent[leaves[j]] = up(frozenset([j]))
    for i, S in enumerate(sets):
        parent[names[i]] = up(S)
    nsplit = len(sets) + 1 if nL > 1 else 0
    return dict(kind=kind, lab=np.asarray(h["lab"], dtype=np.int64), nL=nL, leaves=leaves, parent=parent, root="ROOT", forced=0,
                rule_splits=nsplit, noise=None)


def fit_engine(X, L, seed, m_min, info=None):
    e = dict(ENGINE_DEFAULTS, **((info or {}).get("eng") or {}))
    eps = e["eps"] if e["eps"] >= 0 else e["bar"]
    return best_first(X, L, seed, EngineRule(m_min, bar=e["bar"] * e["mult"], kmax=e["maxK"], eps=eps), "ENGINE-SKM")


def fit_kappa(X, L, seed, m_min, info=None):
    return best_first(X, L, seed, KappaRule(m_min), "KAPPA-SKM")


def fit_bisect(X, L, seed, m_min=None, info=None):
    return svk_to_H(SVK.fit_bisecting(X, L, seed, split=split_skm2), "BISECT-SKM")


def fit_gmm(X, L, seed, m_min=None, info=None):
    return best_first(X, L, seed, GmmRule(), "GMM-BIC")


def fit_ward(X, L, seed=None, m_min=None, info=None):
    """Ward linkage (Euclidean) on all rows, read top-down: the first n - L merges make the L leaves, the last L - 1 merges the hierarchy."""
    from scipy.cluster.hierarchy import linkage
    n = len(X)
    if n < L or L < 2:
        refuse("WARD: %d rows < L %d" % (n, L))
    Z = linkage(np.asarray(X, dtype=np.float64), method="ward")
    uf = np.arange(2 * n - 1)
    for j in range(n - L):
        uf[int(Z[j, 0])] = n + j
        uf[int(Z[j, 1])] = n + j

    def find(x):
        r = x
        while uf[r] != r:
            r = uf[r]
        while uf[x] != r:
            uf[x], x = r, uf[x]
        return r
    roots = np.array([find(i) for i in range(n)])
    active = sorted(set(roots.tolist()))
    if len(active) != L:
        refuse("WARD replay left %d clusters, expected %d" % (len(active), L))
    name = {a: "W%07d" % a for a in active}
    for j in range(n - L, n - 1):
        name[n + j] = "w%07d" % j
    parent = {}
    for j in range(n - L, n - 1):
        parent[name[int(Z[j, 0])]] = name[n + j]
        parent[name[int(Z[j, 1])]] = name[n + j]
    pos = {a: i for i, a in enumerate(active)}
    return dict(kind="WARD", lab=np.array([pos[r] for r in roots], dtype=np.int64), nL=L, leaves=[name[a] for a in active],
                parent=parent, root=name[2 * n - 2], forced=0, rule_splits=L - 1, noise=None)


def fit_hdbscan(X, L=None, seed=None, m_min=55, info=None):
    """DESCRIPTIVE arm (5): selected clusters as leaves + one noise leaf, hierarchy = the condensed tree's cluster ancestry (CA-R5)."""
    from sklearn.cluster import HDBSCAN
    from sklearn.cluster._hdbscan import _tree as HT
    n = len(X)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        h = HDBSCAN(min_cluster_size=int(m_min), copy=True).fit(np.asarray(X, dtype=np.float64))
    labels = np.asarray(h.labels_, dtype=np.int64)
    ct = HT._condense_tree(h._single_linkage_tree_, int(m_min))
    cpar = {}
    fall = np.full(n, -1, dtype=np.int64)
    for rec in ct:
        p, c, sz = int(rec["parent"]), int(rec["child"]), int(rec["cluster_size"])
        if c >= n:
            cpar[c] = p
        else:
            fall[c] = p
    croot = int(ct["parent"].min()) if len(ct) else n

    def chain(x):
        out = [x]
        while x in cpar:
            x = cpar[x]
            out.append(x)
        return out
    js = sorted(set(labels.tolist()) - {-1})
    sel, flat = {}, False
    for j in js:
        mem = np.nonzero(labels == j)[0]
        fc = sorted(set(fall[mem].tolist()))
        anc = chain(fc[0])
        for x in fc[1:]:
            ax = set(chain(x))
            anc = [a for a in anc if a in ax]
        sel[j] = anc[0] if anc else croot
    # verification: the points falling out inside sel[j]'s subtree are exactly label j's members
    sub = {}
    for p_ in range(n):
        if fall[p_] >= 0:
            for a in chain(int(fall[p_])):
                sub.setdefault(a, []).append(p_)
    for j in js:
        if sorted(sub.get(sel[j], [])) != sorted(np.nonzero(labels == j)[0].tolist()):
            flat = True
    leaves = ["H%04d" % j for j in range(len(js))]
    parent = {}
    if flat or not js:
        for lf in leaves:
            parent[lf] = "HROOT"
    else:
        keep = set()
        for j in js:
            keep.update(chain(sel[j])[1:])
        for i, j in enumerate(js):
            parent[leaves[i]] = ("C%d" % cpar[sel[j]]) if sel[j] in cpar else "HROOT"
        for a in keep:
            if a == croot:
                continue
            parent["C%d" % a] = ("C%d" % cpar[a]) if (a in cpar and cpar[a] != croot) else "HROOT"
        for k_ in list(parent):
            if parent[k_] == "C%d" % croot:
                parent[k_] = "HROOT"
    lab = np.empty(n, dtype=np.int64)
    pos = {j: i for i, j in enumerate(js)}
    noise = None
    if (labels == -1).any():
        noise = len(leaves)
        leaves.append("HNOISE")
        parent["HNOISE"] = "HROOT"
    for i in range(n):
        lab[i] = pos[labels[i]] if labels[i] >= 0 else noise
    return dict(kind="HDBSCAN", lab=lab, nL=len(leaves), leaves=leaves, parent=parent, root="HROOT", forced=0, rule_splits=0, noise=noise,
                flat=bool(flat), n_clusters=len(js), noise_share=float(np.mean(labels == -1)))


ArmSpec = SVK.BaselineSpec          # (name, fit, contraction): the seam's registry entry type
ARMS = collections.OrderedDict([
    ("ENGINE-SKM", ArmSpec("ENGINE-SKM", fit_engine, "best-first, engine-like k (maxK 4, separation increment; control)")),
    ("KAPPA-SKM", ArmSpec("KAPPA-SKM", fit_kappa, "arm 1K (descriptive): the registered kappa rule, k up to 8 by max weighted kappa")),
    ("BISECT-SKM", ArmSpec("BISECT-SKM", fit_bisect, "stability_vs_kmeans.fit_bisecting, split = spherical 2-means n_init 5")),
    ("GMM-BIC", ArmSpec("GMM-BIC", fit_gmm, "best-first, diagonal GMM per-node BIC")),
    ("WARD", ArmSpec("WARD", fit_ward, "Ward linkage cut top-down at L (seed-free)")),
    ("HDBSCAN", ArmSpec("HDBSCAN", fit_hdbscan, "HDBSCAN condensed tree (descriptive)")),
])


# ================================================================================================ hierarchy utilities
def node_leafsets(H):
    """node name -> frozenset of leaf indices under it (leaves, internal nodes, root)."""
    out = {}
    for j, lf in enumerate(H["leaves"]):
        x = lf
        out.setdefault(x, set()).add(j)
        while x in H["parent"]:
            x = H["parent"][x]
            out.setdefault(x, set()).add(j)
    out.setdefault(H["root"], set(range(H["nL"])))
    return {k: frozenset(v) for k, v in out.items()}


def dp_struct(H):
    nodes = sorted(set(H["parent"]) | set(H["parent"].values()) | set(H["leaves"]) | {H["root"]})
    ix = {x: i for i, x in enumerate(nodes)}
    Am = np.zeros((len(nodes), H["nL"]))
    for j, lf in enumerate(H["leaves"]):
        x = lf
        Am[ix[x], j] = 1.0
        while x in H["parent"]:
            x = H["parent"][x]
            Am[ix[x], j] = 1.0
    Ch = np.zeros((len(nodes), len(nodes)))
    for c, p in H["parent"].items():
        Ch[ix[p], ix[c]] = 1.0
    roots = [ix[x] for x in nodes if x not in H["parent"]]
    return dict(Am=Am, Ch=Ch, roots=roots, nL=H["nL"])


def dp_fast(st, leaf_idx, cls, K, w=None):
    """Heller-Ghahramani dendrogram purity, vectorised; equal to S1.dendrogram_purity (asserted on every fit)."""
    LC = np.bincount(np.asarray(leaf_idx) * K + np.asarray(cls), weights=w, minlength=st["nL"] * K).reshape(st["nL"], K)
    V = st["Am"] @ LC
    P = V * (V - 1.0) / 2.0
    own = P - st["Ch"] @ P
    tot = V.sum(axis=1)
    m = tot > 0
    num = float((own[m] * V[m] / tot[m][:, None]).sum())
    den = float(sum(P[r].sum() for r in st["roots"]))
    return num / den if den > 0 else float("nan")


def dp_s1(H, leaf_idx, cls):
    return S1.dendrogram_purity(H["parent"], H["leaves"], [H["leaves"][j] for j in leaf_idx], list(cls))


def common_hier(H, cent):
    """F1: one common hierarchy over the arm's leaves, the same procedure for every arm (and the engine rows): scipy linkage
    (COMMON_LINK, Euclidean) on the renormalised leaf centroids, each leaf one point; HDBSCAN's noise leaf hangs under the root."""
    from scipy.cluster.hierarchy import linkage
    valid = [j for j in range(H["nL"]) if j != H.get("noise") and (H["lab"] == j).any()]
    leaves = list(H["leaves"])
    parent = {}
    if len(valid) < 2:
        for j in range(H["nL"]):
            parent[leaves[j]] = "KROOT"
        root = "KROOT"
    else:
        Z = linkage(np.asarray(cent[valid], dtype=np.float64), method=COMMON_LINK)
        m = len(valid)
        name = [leaves[j] for j in valid] + ["K%05d" % t for t in range(m - 1)]
        for t, row in enumerate(Z):
            parent[name[int(row[0])]] = name[m + t]
            parent[name[int(row[1])]] = name[m + t]
        root = name[2 * m - 2]
        for j in range(H["nL"]):
            if j not in valid:
                parent[leaves[j]] = root
    return dict(kind=H["kind"] + "/common", lab=H["lab"], nL=H["nL"], leaves=leaves, parent=parent, root=root, noise=H.get("noise"),
                forced=H.get("forced", 0), rule_splits=H.get("rule_splits", 0))


def shape_stats(H):
    """Children histogram (internal nodes) and mean leaf depth of an arm's OWN hierarchy (printed beside the readouts)."""
    kids = collections.Counter(H["parent"].values())
    hist = collections.Counter(kids.values())
    dep = []
    for lf in H["leaves"]:
        d, x = 0, lf
        while x in H["parent"]:
            x = H["parent"][x]
            d += 1
        dep.append(d)
    return dict(sorted(hist.items())), float(np.mean(dep)) if dep else float("nan")


def leaf_centroids(X, H):
    C = np.zeros((H["nL"], X.shape[1]))
    for j in range(H["nL"]):
        m = H["lab"] == j
        if m.any():
            C[j] = X[m].mean(0)
    return S0.unit(C)


def file_items(Xq, H, cent):
    valid = np.array([j for j in range(H["nL"]) if j != H.get("noise") and (H["lab"] == j).any()], dtype=np.int64)
    if len(valid) == 0 or len(Xq) == 0:
        return np.full(len(Xq), -1, dtype=np.int64), np.full(len(Xq), np.nan)
    sim = Xq @ cent[valid].T
    return valid[np.argmax(sim, axis=1)], sim.max(axis=1)


def leaf_majority(H, tr_fine):
    return S1.majority(list(tr_fine), list(H["lab"]), H["nL"])


def clusters_rows(H, rows, n_universe):
    """TRAIN-row-id clusters of every node (leaves, internal, root excluded) with 2 <= size < n_universe."""
    ls = node_leafsets(H)
    by_leaf = [rows[H["lab"] == j] for j in range(H["nL"])]
    out = set()
    for node, S in ls.items():
        if node == H["root"]:
            continue
        mem = frozenset(int(x) for j in S for x in by_leaf[j])
        if 2 <= len(mem) < n_universe:
            out.add(mem)
    return out


def topo_of(cl, n, trip):
    return SSUP.triplet_topo(sorted(cl, key=lambda c: sorted(c)), _IdentityIdx(n), trip).astype(np.int8)


class _IdentityIdx(object):
    def __init__(self, n):
        self.n = n

    def __len__(self):
        return self.n

    def __getitem__(self, q):
        return q


def conv(a, b, mask=None):
    """-> (all-triplets disagreement, resolved-in-both disagreement, both-resolved share) on the masked triplets."""
    if mask is not None:
        a, b = a[mask], b[mask]
    if len(a) == 0:
        return float("nan"), float("nan"), float("nan")
    rb = (a != 3) & (b != 3)
    return float(np.mean(a != b)), (float(np.mean(a[rb] != b[rb])) if rb.any() else float("nan")), float(np.mean(rb))


def sub_rows(n, s):
    return np.sort(np.random.default_rng(SUB_BASE + s).choice(n, int(math.floor(SUB_FRAC * n)), replace=False))


# ================================================================================================ fit orchestration
def _fit_job(spec):
    arm, X, L, seed, m_min, info = spec
    t0 = time.time()
    H = ARMS[arm].fit(X, L, seed, m_min, info)
    H["secs"] = time.time() - t0
    return H


def fit_jobs(world, legs):
    specs, keys = [], []
    for leg in legs:
        Wc = world[leg]
        X, L, mm = Wc["Xtr"], Wc["L"], Wc["m_min"]
        n = len(X)
        for arm in ALL_ARMS:
            seeds = SEEDS if arm in SEEDED else (None,)
            for s in seeds:
                specs.append((arm, X, L, s, mm, dict(leg=leg, sub=None, eng=Wc.get("eng"))))
                keys.append((leg, arm, "full", s))
            for s in SEEDS:
                r = sub_rows(n, s)
                specs.append((arm, X[r], L, s if arm in SEEDED else None, mm, dict(leg=leg, sub=s, eng=Wc.get("eng"))))
                keys.append((leg, arm, "sub", s))
    order = sorted(range(len(specs)), key=lambda i: -len(specs[i][1]) * (3 if specs[i][0] in ("GMM-BIC", "ENGINE-SKM", "KAPPA-SKM") else 1))
    return [specs[i] for i in order], [keys[i] for i in order]


def run_fits(world, legs, workers, out):
    specs, keys = fit_jobs(world, legs)
    t0 = time.time()
    if workers <= 1:
        res = [_fit_job(s) for s in specs]
    else:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=workers) as ex:
            res = list(ex.map(_fit_job, specs, chunksize=1))
    F = {}
    for k, H in zip(keys, res):
        F[k] = H
    out("FITS: %d fits (%s) in %.1f s wall with %d worker(s); CPU seconds summed %.1f" % (
        len(res), ", ".join(legs), time.time() - t0, workers, sum(h.get("secs", 0.0) for h in res)))
    return F


# ================================================================================================ statistics
def clears(s):
    return bool(s["D"] > s["spread"]) and bool(s["lo"] > 0)


def ahead(s):
    return bool(s["D"] < -s["spread"]) and bool(s["hi"] < 0)


def cca_decide(stats):
    """stats[(j, r)][corpus] = dict(D, spread, lo, hi). -> (word, winners, fails {(j, r): [(corpus, reasons)]})."""
    winners, fails = [], collections.OrderedDict()
    for j in DECIDING:
        for r in READOUTS:
            per = stats[(j, r)]
            ok = [clears(per[c]) for c in CORPORA]
            if all(ok):
                winners.append((j, r))
            else:
                why = []
                for c in CORPORA:
                    s = per[c]
                    rs = []
                    if not bool(s["D"] > s["spread"]):
                        rs.append("D <= spread")
                    if not bool(s["lo"] > 0):
                        rs.append("lower bound <= 0")
                    if rs:
                        why.append((c, rs))
                fails[(j, r)] = why
    return ("ARM-WINS" if winners else "NO-ARM-WINS"), winners, fails


def spread5(v):
    v = np.asarray(v, dtype=np.float64)
    return float(v.max() - v.min()) if len(v) == len(SEEDS) else float("nan")


def bootstrap_corpus(vals_w_fn, comp, B, seed, arms_present):
    """The registered crossed / paired bootstrap. vals_w_fn(w) -> {r: {arm: np.array over seeds (len 5, or 1 for WARD / HDBSCAN)}}.
    -> reps {(j, r): array}, item {(j, r): array} for j in DECIDING + HDBSCAN."""
    rng = np.random.default_rng(seed)
    _u, cc = np.unique(comp, return_inverse=True)
    G = int(cc.max()) + 1
    comp_list = [j for j in DECIDING + DESCRIPTIVE_ARMS if j in arms_present]
    reps = {(j, r): np.empty(B) for j in comp_list for r in READOUTS}
    item = {(j, r): np.empty(B) for j in comp_list for r in READOUTS}
    for b in range(B):
        w = np.bincount(rng.integers(G, size=G), minlength=G)[cc].astype(np.float64)
        idx = {a: rng.integers(0, len(SEEDS), size=len(SEEDS)) for a in SEEDED}
        v = vals_w_fn(w)
        for r in READOUTS:
            v1 = v[r][CONTROL]
            m1 = float(v1[idx[CONTROL]].mean())
            for j in comp_list:
                vj = v[r][j]
                mj = float(vj[idx[j]].mean()) if j in SEEDED else float(vj.mean())
                reps[(j, r)][b] = mj - m1
                item[(j, r)][b] = float(vj.mean()) - float(v1.mean())
    return reps, item


def pct(x):
    x = np.asarray(x, dtype=np.float64)
    if len(x) == 0 or not np.all(np.isfinite(x)):
        return float("nan"), float("nan")
    lo, hi = np.percentile(x, [2.5, 97.5])
    return float(lo), float(hi)


def sd1(x):
    x = np.asarray(x, dtype=np.float64)
    return float(np.std(x, ddof=1)) if len(x) > 1 and np.all(np.isfinite(x)) else float("nan")


# ================================================================================================ readouts
def fit_readout(Wc, H):
    """Per fit: filing, DP (S1 and dp_fast, asserted equal), leaf filing accuracy, OOS scores (CLINC)."""
    cent = leaf_centroids(Wc["Xtr"], H)
    filed, s_in = file_items(Wc["Xev"], H, cent)
    Hc = common_hier(H, cent)
    st = dp_struct(Hc)
    ok = filed >= 0
    dp = dp_s1(Hc, filed[ok], Wc["ev_coarse"][ok]) if ok.any() else float("nan")
    dpf = dp_fast(st, filed[ok], Wc["ev_coarse"][ok], Wc["Kc"]) if ok.any() else float("nan")
    if np.isfinite(dp) and abs(dp - dpf) > 1e-10:
        refuse("dp_fast %.12f != S1.dendrogram_purity %.12f on a %s fit" % (dpf, dp, H["kind"]))
    dp_own = dp_s1(H, filed[ok], Wc["ev_coarse"][ok]) if ok.any() else float("nan")
    maj = leaf_majority(H, Wc["tr_fine"])
    correct = np.array([bool(f >= 0 and maj[f] is not None and maj[f] == g) for f, g in zip(filed, Wc["ev_fine"])])
    r = dict(H=H, Hc=Hc, st=st, filed=filed, ok=ok, dp=dp, dp_own=dp_own, fa=float(correct.mean()) if len(correct) else float("nan"),
             correct=correct, s_in=s_in, shape=shape_stats(H))
    if Wc.get("Xoos") is not None:
        r["s_oos"] = file_items(Wc["Xoos"], H, cent)[1]
        r["A"] = S0.auroc(s_in, r["s_oos"]) if ok.all() else float("nan")
    return r


def random_shape(Wc, fr, n_random):
    """GR2 instrument on the deciding (common) hierarchy. -> (p97.5, median, number of distinct draw values)."""
    H = fr["Hc"]
    ok = fr["ok"]
    if not ok.any():
        return float("nan"), float("nan"), 0
    leaf_ids = [H["leaves"][j] for j in fr["filed"][ok]]
    rnd = GG.random_shape_dps(H["parent"], H["leaves"], leaf_ids, list(Wc["ev_coarse"][ok]), n_random, SEED_RANDOM)
    return ((float(np.percentile(rnd, GG.Q_RANDOM)) if rnd else float("nan")), (float(np.median(rnd)) if rnd else float("nan")),
            len(set(round(x, 12) for x in rnd)))


def random_shape_own(Wc, fr, n_random):
    """GR2 on the arm's OWN hierarchy, for (a-own) (descriptive)."""
    return random_shape(Wc, dict(fr, Hc=fr["H"]), n_random)


def engine_readout(Wc):
    T = Wc["T"]
    fl = S1.flat_leaf(T, Wc["Xev"])
    leaf_ids = [T["leaves"][j] for j in fl]
    dp = S1.dendrogram_purity(S1.tree_parent_restricted(T), T["leaves"], leaf_ids, list(Wc["ev_coarse"]))
    trl = S1.flat_leaf(T, Wc["Xtr"])
    maj = S1.majority(list(Wc["tr_fine"]), list(trl), len(T["leaves"]))
    fa = float(np.mean([maj[f] is not None and maj[f] == g for f, g in zip(fl, Wc["ev_fine"])]))
    Hs = dict(kind="engine", lab=trl, nL=len(T["leaves"]), leaves=list(T["leaves"]), parent={}, root="-", noise=None)
    He = common_hier(Hs, S0.unit(np.asarray(T["leaf_mu"], dtype=np.float64)))
    dpc = S1.dendrogram_purity(He["parent"], He["leaves"], leaf_ids, list(Wc["ev_coarse"]))
    tp = S1.tree_parent_restricted(T)
    out = dict(dp=dp, dp_common=dpc, fa=fa, L=len(T["leaves"]),
               shape=shape_stats(dict(parent=tp, leaves=list(T["leaves"]))))
    if Wc.get("Xoos") is not None:
        out["A"] = S0.auroc((Wc["Xev"] @ T["leaf_mu"].T).max(1), (Wc["Xoos"] @ T["leaf_mu"].T).max(1))
    return out


def identity_check(world, ident, out):
    bad = []
    got = {}
    for c in CORPORA:
        got["dp_" + c] = "%.5f" % world[c]["engine"]["dp"]
        if got["dp_" + c] != ident["dp_" + c]:
            bad.append("I1 DP(%s) %s != %s" % (ENGINE[c], got["dp_" + c], ident["dp_" + c]))
    a = world["clinc"]["engine"].get("A")
    got["A_T"] = "n/a" if a is None else "%.5f" % a
    if got["A_T"] != ident["A_T"]:
        bad.append("I2 A(C-AF) %s != %s" % (got["A_T"], ident["A_T"]))
    out("IDENTITY PRECONDITIONS: I1 DP(M-AF) %s (of record %s), DP(C-AF) %s (of record %s); I2 A(C-AF) %s (of record %s); I3 |C| %d (of "
        "record %d): %s" % (got["dp_massive"], ident["dp_massive"], got["dp_clinc"], ident["dp_clinc"], got["A_T"], ident["A_T"],
                             world["mmlu"]["nC"], ident["C"], "REPRODUCED" if not bad else "MISMATCH"))
    if bad:
        refuse("IDENTITY PRECONDITION FAILED (%s): the inputs do not reproduce the numbers of record; no readout is written" % "; ".join(bad))


def corpus_block(Wc, F, B, n_random, boot_seed):
    leg = Wc["name"]
    R = dict(name=leg, n=len(Wc["ev_coarse"]), G=int(len(np.unique(Wc["comp"]))), kish=S0.kish(Wc["comp"]), L=Wc["L"])
    fr = {a: [fit_readout(Wc, F[(leg, a, "full", s)]) for s in (SEEDS if a in SEEDED else (None,))] for a in ALL_ARMS}
    for a in DECIDING + (CONTROL,):
        for x in fr[a]:
            if x["H"]["nL"] != Wc["L"]:
                refuse("%s on %s reached %d leaves, not the registered L = %d (matched leaf count)" % (a, leg, x["H"]["nL"], Wc["L"]))
    R["fr"] = fr
    R["vals"] = {r: {a: np.array([x["dp" if r == "a" else "fa"] for x in fr[a]]) for a in ALL_ARMS} for r in READOUTS}
    R["spread"] = {r: spread5(R["vals"][r][CONTROL]) for r in READOUTS}
    arms_present = [a for a in ALL_ARMS if all(np.isfinite(R["vals"][r][a]).all() for r in READOUTS)]

    def vals_w(w):
        o = {r: {} for r in READOUTS}
        for a in ALL_ARMS:
            da, dc = [], []
            for x in fr[a]:
                ok = x["ok"]
                ww = w[ok]
                da.append(dp_fast(x["st"], x["filed"][ok], Wc["ev_coarse"][ok], Wc["Kc"], ww) if ok.any() else np.nan)
                dc.append(float((w * x["correct"]).sum() / w.sum()))
            o["a"][a], o["c"][a] = np.array(da), np.array(dc)
        return o
    reps, item = bootstrap_corpus(vals_w, Wc["comp"], B, boot_seed, arms_present)
    R["stats"] = {}
    for (j, r), x in reps.items():
        vj, v1 = R["vals"][r][j], R["vals"][r][CONTROL]
        D = float(vj.mean() - v1.mean())
        lo, hi = pct(x)
        seed_term = math.sqrt((np.var(vj, ddof=1) / len(vj) if len(vj) > 1 else 0.0) + np.var(v1, ddof=1) / len(v1))
        se, si = sd1(x), sd1(item[(j, r)])
        se_corr = math.sqrt(si ** 2 + max(0.0, se ** 2 - si ** 2) * SEED_CORR) if np.isfinite(se) and np.isfinite(si) else float("nan")
        R["stats"][(j, r)] = dict(D=D, spread=R["spread"][r], lo=lo, hi=hi, se=se, se_item=si, se_corr=se_corr, seed_term=seed_term)
    R["random"] = {a: [random_shape(Wc, x, n_random) for x in fr[a]] for a in ALL_ARMS}
    R["random_own"] = {a: [random_shape_own(Wc, x, n_random) for x in fr[a]] for a in ALL_ARMS}
    R["engine"] = Wc["engine"]
    if Wc.get("Xoos") is not None:
        R["oos"] = oos_block(Wc, fr, B)
    return R


def oos_block(Wc, fr, B):
    names, sc = [], {}
    for a in ALL_ARMS:
        for i, x in enumerate(fr[a]):
            if "A" in x and np.isfinite(x["A"]):
                k = "%s#%d" % (a, i)
                names.append(k)
                sc[k] = {"in": x["s_in"], "oos": x["s_oos"]}
    draws = OTC.paired_boot(Wc["C"], {"in": Wc["ev_rows"], "oos": Wc["oos_rows"]}, sc, names, B)
    A = {a: np.array([x.get("A", np.nan) for x in fr[a]]) for a in ALL_ARMS}
    d1 = np.mean(np.vstack([draws["%s#%d" % (CONTROL, i)] for i in range(len(fr[CONTROL]))]), axis=0)
    out = {"A": A, "D": {}, "ci": {}}
    for a in ALL_ARMS:
        if a == CONTROL or not np.all(np.isfinite(A[a])):
            continue
        da = np.mean(np.vstack([draws["%s#%d" % (a, i)] for i in range(len(fr[a]))]), axis=0)
        out["D"][a] = float(A[a].mean() - A[CONTROL].mean())
        out["ci"][a] = pct(da - d1)
    out["n_in"], out["n_oos"] = len(Wc["ev_rows"]), len(Wc["oos_rows"])
    return out


def triplet_block(Wc, F):
    """(b): seed pairs (arms 1-3, full fits) and subsample pairs (every arm), both conventions, unresolved shares."""
    leg = Wc["name"]
    n = len(Wc["Xtr"])
    trip = Wc["trip"]
    allrows = np.arange(n)
    out = {"seed": {}, "sub": {}, "unres": {}, "unres_sub": {}}
    for a in ALL_ARMS:
        if a in SEEDED:
            tp = [topo_of(clusters_rows(F[(leg, a, "full", s)], allrows, n), n, trip) for s in SEEDS]
            prs = [conv(tp[i], tp[k]) for i in range(5) for k in range(i + 1, 5)]
            out["seed"][a] = (float(np.mean([p[0] for p in prs])), float(np.nanmean([p[1] for p in prs])), float(np.mean([p[2] for p in prs])))
            out["unres"][a] = float(np.mean([np.mean(t == 3) for t in tp]))
        else:
            t0 = topo_of(clusters_rows(F[(leg, a, "full", None)], allrows, n), n, trip)
            out["unres"][a] = float(np.mean(t0 == 3))
        tps, ins = [], []
        for s in SEEDS:
            r = sub_rows(n, s)
            tps.append(topo_of(clusters_rows(F[(leg, a, "sub", s)], r, n), n, trip))
            m = np.zeros(n, dtype=bool)
            m[r] = True
            ins.append(m[trip].all(axis=1))
        prs = [conv(tps[i], tps[k], ins[i] & ins[k]) for i in range(5) for k in range(i + 1, 5)]
        out["sub"][a] = (float(np.mean([p[0] for p in prs])), float(np.nanmean([p[1] for p in prs])), float(np.mean([p[2] for p in prs])))
        out["unres_sub"][a] = float(np.mean([np.mean(t[m] == 3) for t, m in zip(tps, ins)]))
    return out


def mmlu_block(Wm, F):
    leg = "mmlu"
    out = {"dp": {}, "engine": {}}
    for a in ALL_ARMS:
        vals = []
        for s in (SEEDS if a in SEEDED else (None,)):
            H = F[(leg, a, "full", s)]
            ok = np.array([j != H.get("noise") for j in H["lab"]])
            vals.append(dp_s1(H, H["lab"][ok], Wm["cat"][ok]) if ok.any() else float("nan"))
        out["dp"][a] = np.array(vals)
    for t, e in Wm["engines"].items():
        fl = np.argmax(Wm["Xtr"] @ e["leaf_mu"].T, axis=1)
        out["engine"][t] = (S1.dendrogram_purity(e["parent"], e["leaves"], [e["leaves"][j] for j in fl], list(Wm["cat"])), len(e["leaves"]))
    return out


def fit_summary(F, leg, L):
    rows = {}
    for a in ALL_ARMS:
        hs = [F[(leg, a, "full", s)] for s in (SEEDS if a in SEEDED else (None,))]
        sh = [h["forced"] / float(h["forced"] + h["rule_splits"]) if (h["forced"] + h["rule_splits"]) else 0.0 for h in hs]
        sizes = np.concatenate([np.bincount(h["lab"], minlength=h["nL"]) for h in hs])
        rows[a] = dict(leaves=[h["nL"] for h in hs], forced=[h["forced"] for h in hs], rule=[h["rule_splits"] for h in hs],
                       share=float(np.mean(sh)), sizes=(int(sizes.min()), float(np.median(sizes)), int(sizes.max())),
                       inactive=bool(np.mean(sh) > INACTIVE), noise=[h.get("noise_share") for h in hs], flat=[h.get("flat") for h in hs])
    return rows


def compute(world, F, B, n_random):
    R = {"corpora": {}, "trip": {}, "fits": {}}
    for k, c in enumerate(CORPORA):
        R["corpora"][c] = corpus_block(world[c], F, B, n_random, SEED_BOOT)
    for leg in CORPORA + ("mmlu",):
        R["trip"][leg] = triplet_block(world[leg], F)
        R["fits"][leg] = fit_summary(F, leg, world[leg]["L"])
    R["mmlu"] = mmlu_block(world["mmlu"], F)
    R["mmlu"].update(m_min=world["mmlu"]["m_min"], L=world["mmlu"]["L"], nC=world["mmlu"]["nC"])
    stats = {(j, r): {c: R["corpora"][c]["stats"][(j, r)] for c in CORPORA} for j in DECIDING for r in READOUTS}
    R["word"], R["winners"], R["fails"] = cca_decide(stats)
    R["stats"] = stats
    R["B"], R["n_random"] = B, n_random
    return R


# ================================================================================================ render
def band(x, b):
    return GG.band(x, b[1], b[2])


def render(R, meta):
    L = []
    L.append("CONSTRUCTION-ARMS readout (%s); mode --run; %s; date %s; ZERO calls; 0 CCE" % (REG, meta["pins"], datetime.date.today().isoformat()))
    if meta.get("fixture"):
        L.append("FIXTURE PARAMETERS (selftest; NOT OF RECORD): %s" % meta["fixture"])
    for k in ("imports", "pool", "data", "census", "mmin", "audit", "identity"):
        for ln in (meta.get(k) or []):
            L.append(ln)
    L.append("BUILDER'S READINGS (CA-R0..CA-R10, see the script docstring; the registrar confirms or brackets): CA-R1 one default_rng(%d) "
             "per corpus, draw order components -> ENGINE-SKM / BISECT-SKM / GMM-BIC seed indices; CA-R2 node seeds s x 1000003 + 17 c + k; "
             "CA-R5 HDBSCAN LCA reading; CA-R9 identity first, fits on frozen TRAIN matrices" % SEED_BOOT)
    L.append("INTERVAL: percentile bootstrap B %d, crossed (seeds resampled per arm) and paired (EVAL components shared); WARD seed-free" % R["B"])
    # fits
    for leg in CORPORA + ("mmlu",):
        for a in ALL_ARMS:
            fs = R["fits"][leg][a]
            L.append("FITS %s %-10s leaves %s; forced splits %s; rule splits %s; forced share %.3f%s; leaf sizes min %d / median %.1f / max %d%s"
                     % (leg, a, fs["leaves"], fs["forced"], fs["rule"], fs["share"], " -> rule mostly inactive" if fs["inactive"] else "",
                        fs["sizes"][0], fs["sizes"][1], fs["sizes"][2],
                        ("; noise share %s; flat %s" % (["%.4f" % x for x in fs["noise"] if x is not None], fs["flat"])) if a == "HDBSCAN" else
                        (" [%s]" % "arm 1 = ENGINE-LIKE SKM, not the engine (differences (i)-(v), WORDS OF RECORD)" if a == CONTROL else
                         (" [arm 1K, DESCRIPTIVE]" if a == "KAPPA-SKM" else ""))))
    # readouts and stats
    for c in CORPORA:
        Rc = R["corpora"][c]
        for r in READOUTS:
            for a in ALL_ARMS:
                L.append("READOUT %s %s %-10s per seed %s mean %s%s" % (
                    c, RNAME[r], a, " / ".join(f5(x, "%.5f") for x in Rc["vals"][r][a]), f5(float(np.mean(Rc["vals"][r][a])), "%.5f"),
                    (" spread_1 %s [arm 1 = ENGINE-LIKE SKM, not the engine]" % f5(Rc["spread"][r], "%.5f")) if a == CONTROL else
                    (" [arm 1K, DESCRIPTIVE]" if a == "KAPPA-SKM" else "")))
    for (j, r), per in R["stats"].items():
        for c in CORPORA:
            s = per[c]
            L.append("D %s %s %-10s D %s 95%% [%s, %s] spread_1 %s SE %s -> %s" % (
                c, RNAME[r], j, f5(s["D"]), f5(s["lo"]), f5(s["hi"]), f5(s["spread"], "%.5f"), f5(s["se"], "%.5f"),
                "CLEARS both conjuncts" if clears(s) else "fails"))
    L.append("C-CA (THE ONE DECIDING CRITERION; point AND interval in one clause): %s%s" % (
        R["word"], ("; winning (j, r): " + ", ".join("%s %s" % (j, RNAME[r]) for j, r in R["winners"])) if R["winners"] else ""))
    if R["word"] == "ARM-WINS":
        L.append("FAILS (rule 8): NO-ARM-WINS is refuted by %s (both conjuncts on both corpora)" % ", ".join("%s %s" % (j, r) for j, r in R["winners"]))
        L.append("F-CA FIRES: a generic split rule beats the kappa-selected spherical control at matched greedy shape and leaf count, on both "
                 "intent corpora, by more than the control's seed spread; consequence: a faithful engine arm for the winning rule becomes a "
                 "candidate for a NEW registration with its own go; never an engine change from this result")
    else:
        L.append("FAILS (rule 8): ARM-WINS is refuted at the planned n: for every (j, r) at least one corpus fails a conjunct: %s" % "; ".join(
            "%s %s: %s" % (j, r, ", ".join("%s (%s)" % (c, " and ".join(rs)) for c, rs in why)) for (j, r), why in R["fails"].items()))
        L.append("F-CA NOT FIRED (C-CA NO-ARM-WINS; not parity)")
    L.append(WORDS)
    for (j, r), per in R["stats"].items():
        for c in CORPORA:
            if ahead(per[c]):
                L.append("ARM-1-AHEAD (descriptive): %s %s %s (D %s < -spread %s, upper bound %s < 0)" % (
                    j, RNAME[r], c, f5(per[c]["D"]), f5(per[c]["spread"], "%.5f"), f5(per[c]["hi"])))
    # support
    L.append(REG_SUPPORT)
    worst = 0.0
    for c in CORPORA:
        Rc = R["corpora"][c]
        for (j, r), s in Rc["stats"].items():
            if j not in DECIDING:
                continue
            deff = Rc["kish"] * (s["se"] / s["se_item"]) ** 2 if s["se_item"] and np.isfinite(s["se_item"]) and s["se_item"] > 0 else float("nan")
            mde1 = s["spread"] + 0.84 * s["se"]
            mdej = s["spread"] + 1.25 * s["se"]
            worst = max(worst, mdej) if np.isfinite(mdej) else worst
            L.append("SUPPORT %s %s %-10s n %d, components %d, Kish %.4f; SE(D) %s (registered %.4f); seed-corrected SE %s (seed variance x "
                     "n/(n-1) = 1.25; the percentile interval is anti-conservative on the seed axis); item-only SD %s; seed term %s; DEFF_total "
                     "%s; n_eff %s; MDE80 per corpus %s; joint %s (registered %.3f)" % (
                         c, r, j, Rc["n"], Rc["G"], Rc["kish"], f5(s["se"], "%.5f"), REG_SE[(r, c)], f5(s["se_corr"], "%.5f"), f5(s["se_item"], "%.5f"),
                         f5(s["seed_term"], "%.5f"), f5(deff, "%.2f"), f5(Rc["n"] / deff if deff and np.isfinite(deff) else float("nan"), "%.0f"),
                         f5(mde1, "%.4f"), f5(mdej, "%.4f"), REG_MDE_JOINT[(r, c)]))
    L.append(VERDICT_LINE + "; realised deciding joint MDE80 (max over the deciding cells) %.4f" % worst)
    # descriptive
    for c in CORPORA:
        Rc = R["corpora"][c]
        for a in ALL_ARMS:
            L.append("DESCRIPTIVE GR2 %s %-10s common-hierarchy DP vs 200 matched-shape random trees: %s" % (c, a, "; ".join(
                gr2_text(x["dp"], p, nd) for x, (p, _m, nd) in zip(Rc["fr"][a], Rc["random"][a]))))
            L.append("DESCRIPTIVE (a-own) %s %-10s own-hierarchy DP vs its GR2: %s; children histogram %s; mean leaf depth %s" % (
                c, a, "; ".join(gr2_text(x["dp_own"], p, nd) for x, (p, _m, nd) in zip(Rc["fr"][a], Rc["random_own"][a])),
                " | ".join(str(x["shape"][0]) for x in Rc["fr"][a]), " / ".join("%.2f" % x["shape"][1] for x in Rc["fr"][a])))
        for da in DESCRIPTIVE_ARMS:
            hs = Rc["stats"].get((da, "a"))
            if hs:
                hc = Rc["stats"][(da, "c")]
                L.append("DESCRIPTIVE %s %s: D(a) %s [%s, %s], D(c) %s [%s, %s] vs arm 1 (never in C-CA)" % (
                    da, c, f5(hs["D"]), f5(hs["lo"]), f5(hs["hi"]), f5(hc["D"]), f5(hc["lo"]), f5(hc["hi"])))
        e = Rc["engine"]
        L.append("ENGINE ROW %s (%s, descriptive): DP_coarse own tree %.5f (I1), on the common hierarchy %.5f, leaf filing accuracy %.5f, "
                 "%d leaves%s; children histogram %s, mean leaf depth %.2f; arm 1 (common) minus engine (common) DP %s" % (
                     c, ENGINE[c], e["dp"], e["dp_common"], e["fa"], e["L"], (", OOS AUROC %.5f" % e["A"]) if "A" in e else "",
                     e["shape"][0], e["shape"][1],
                     f5(float(np.mean(Rc["vals"]["a"][CONTROL])) - e["dp_common"])))
    oo = R["corpora"]["clinc"].get("oos")
    if oo:
        L.append("DESCRIPTIVE (d) CLINC OOS AUROC (in-scope EVAL %d vs OOS %d): %s" % (oo["n_in"], oo["n_oos"], "; ".join(
            "%s %s" % (a, f5(float(np.mean(oo["A"][a])), "%.5f")) for a in ALL_ARMS)))
        L.append("DESCRIPTIVE (d) D_AUROC vs arm 1 (paired stratified component bootstrap): %s" % "; ".join(
            "%s %s [%s, %s]" % (a, f5(d), f5(oo["ci"][a][0]), f5(oo["ci"][a][1])) for a, d in oo["D"].items()))
    for leg in CORPORA + ("mmlu",):
        T = R["trip"][leg]
        L.append("DESCRIPTIVE (b) %s seed pairs (all-triplets / resolved-in-both [joint both-resolved coverage]; unresolved share): %s" % (
            leg, "; ".join("%s %s / %s [cov %.4f] (unres %.4f)" % (a, f5(T["seed"][a][0], "%.4f"), f5(T["seed"][a][1], "%.4f"), T["seed"][a][2],
                                                                   T["unres"][a]) for a in SEEDED)))
        L.append("DESCRIPTIVE (b) %s 90%%-subsample pairs (all-triplets / resolved-in-both [joint both-resolved coverage]; unresolved share): %s" % (
            leg, "; ".join("%s %s / %s [cov %.4f] (unres %.4f)" % (a, f5(T["sub"][a][0], "%.4f"), f5(T["sub"][a][1], "%.4f"), T["sub"][a][2],
                                                                   T["unres_sub"][a]) for a in ALL_ARMS)))
    M = R["mmlu"]
    L.append("DESCRIPTIVE C leg (MMLU-Pro C, in-sample, DP vs category; no EVAL): %s" % "; ".join(
        "%s %s" % (a, " / ".join(f5(x, "%.4f") for x in M["dp"][a])) for a in ALL_ARMS))
    L.append("DESCRIPTIVE C leg engine rows (flatLeaf on C): %s" % "; ".join("%s DP %.4f (%d leaves)" % (t, v[0], v[1]) for t, v in M["engine"].items()))
    fm = R["fits"]["mmlu"]
    L.append("DISCLOSURE C leg (C-4): m_min x L = %d x %d = %d %s |C| %d, so the m_min floor %s; forced-split share ENGINE-SKM %.3f, GMM-BIC "
             "%.3f%s" % (M["m_min"], M["L"], M["m_min"] * M["L"], ">" if M["m_min"] * M["L"] > M["nC"] else "<=", M["nC"],
                         "makes L unreachable by arm 1's rule alone: arm 1 reaches L mostly by forced spherical 2-means and is there mostly "
                         "BISECT-SKM" if M["m_min"] * M["L"] > M["nC"] else "does not by itself bind L",
                         fm["ENGINE-SKM"]["share"], fm["GMM-BIC"]["share"],
                         " (rule mostly inactive)" if fm["ENGINE-SKM"]["inactive"] else ""))
    L += prediction_lines(R)
    L.append(NOT_SHOW)
    return L


def gr2_text(dp, p, nd):
    return "DP %s p97.5 %s %s (%d distinct draws%s)" % (f5(dp, "%.5f"), f5(p, "%.5f"), "ABOVE" if (np.isfinite(dp) and dp > p) else "not above",
                                                      nd, "; null degenerate (flat)" if nd == 1 else "")


def prediction_lines(R):
    L = []
    C_ = R["corpora"]
    for (r, c), b in P1.items():
        x = float(np.mean(C_[c]["vals"][r][CONTROL]))
        L.append("P1 arm 1 %s %s %s in [%.2f, %.2f]: %s" % (RNAME[r], c, f5(x, "%.5f"), b[1], b[2], band(x, b)))
    for j in DECIDING:
        for r in READOUTS:
            b = P_D[j][r]
            for c in CORPORA:
                x = R["stats"][(j, r)][c]["D"]
                L.append("%s %s D_%s %s %s in [%+.3f, %+.3f]: %s (restated, informed)" % (P_PRED[j], j, r, c, f5(x), b[1], b[2], band(x, b)))
    for c in CORPORA:
        x = R["fits"][c]["GMM-BIC"]["share"]
        L.append("P3 GMM-BIC forced-split share %s %.4f in [%.2f, %.2f]: %s" % (c, x, P3_FORCED[1], P3_FORCED[2], band(x, P3_FORCED)))
    L.append("P3 (C, printed, not scored) GMM-BIC forced-split share mmlu %.4f" % R["fits"]["mmlu"]["GMM-BIC"]["share"])
    win = bool(R["word"] == "ARM-WINS")
    bs = (P5_WIN - (1.0 if win else 0.0)) ** 2
    L.append("P5 C-CA ARM-WINS %.2f / NO-ARM-WINS %.2f: outcome %s; Brier (p_ARM-WINS - [ARM-WINS])^2 = %.4f (two-outcome sum %.4f)" % (
        P5_WIN, 1 - P5_WIN, R["word"], bs, 2 * bs))
    ev = []
    for c in CORPORA:
        T = R["trip"][c]
        x = T["seed"][CONTROL][0] - T["seed"]["BISECT-SKM"][0]
        un = bool(T["unres"][CONTROL] > T["unres"]["BISECT-SKM"])
        h = band(x, P6_BAND)
        ev.append(bool(h == "HELD") and un)
        L.append("P6 (descriptive) %s arm 1 minus BISECT-SKM seed-pair all-triplet disagreement %s in [%.2f, %.2f]: %s; unresolved share arm 1 "
                 "%.4f > BISECT-SKM %.4f: %s" % (c, f5(x, "%+.4f"), P6_BAND[1], P6_BAND[2], h, T["unres"][CONTROL], T["unres"]["BISECT-SKM"],
                                                 "TRUE" if un else "FALSE"))
    L.append("P6 overall: %s" % ("HELD" if all(ev) else "FAILED"))
    oo = C_["clinc"].get("oos")
    if oo and oo["D"]:
        e7 = all(abs(oo["D"][a]) <= P7_MARGIN for a in DECIDING if a in oo["D"])
        L.append("P7 (descriptive) every |D_AUROC| (arms 2-4 vs arm 1) <= %.3f: %s; Brier %.4f" % (P7_MARGIN, "TRUE" if e7 else "FALSE",
                                                                                            GG.brier(P7_PROB, e7)))
    else:
        L.append("P7 (descriptive) NOT SCORED: no OOS rows")
    for c in CORPORA:
        x = float(np.mean(C_[c]["vals"]["a"][CONTROL])) - C_[c]["engine"]["dp_common"]
        L.append("P8 (descriptive) %s arm 1 minus the engine row DP_coarse (both on the common construction) %s in [%.2f, %.2f]: %s" % (c, f5(x), P8_BAND[1], P8_BAND[2], band(x, P8_BAND)))
    return L


# ================================================================================================ loading
def toml_params(paths):
    """m_min and arm 1's engine knobs copied from the build TOMLs (absent keys = the TaxonomyConfig.kt defaults); all paths must agree."""
    import tomllib
    vals = {}
    for p in paths:
        if not os.path.isfile(p):
            refuse("%s absent (m_min and the engine knobs are copied from the build TOMLs)" % p)
        with open(p, "rb") as fh:
            t = tomllib.load(fh)
        if "minClusterSize" not in t or "proposalSeparationBar" not in t:
            refuse("%s lacks minClusterSize / proposalSeparationBar" % p)
        vals[p] = (int(t["minClusterSize"]), int(t.get("maxK", ENGINE_DEFAULTS["maxK"])), float(t.get("marginalEps", ENGINE_DEFAULTS["eps"])),
                   float(t["proposalSeparationBar"]), float(t.get("proposalAcceptMultiplier", ENGINE_DEFAULTS["mult"])))
    if len(set(vals.values())) != 1:
        refuse("the build TOMLs disagree on (minClusterSize, maxK, marginalEps, bar, multiplier): %s" % vals)
    v = list(vals.values())[0]
    return v[0], dict(maxK=v[1], eps=v[2], bar=v[3], mult=v[4])


def eng_text(e):
    return "maxK %d, marginalEps %s, proposalSeparationBar %.3f, proposalAcceptMultiplier %.2f" % (
        e["maxK"], ("%.3f" % e["eps"]) if e["eps"] >= 0 else "unset (-> the bar)", e["bar"], e["mult"])


def mmlu_categories(ss_ctx, C_list):
    con = ZC.open_ro(ss_ctx.stage("mmlu_pro_dataset_cache_v2.db")["path"], TAG)
    want = set(C_list)
    first, conflict = {}, set()
    try:
        for _i, t, cat in con.execute("SELECT id, question, category FROM mmlu_pro ORDER BY id"):
            if t is None:
                continue
            q = CA.qid(t)
            if q in want:
                if q not in first:
                    first[q] = cat
                elif first[q] != cat:
                    conflict.add(q)
    finally:
        con.close()
    miss = [q for q in C_list if q not in first]
    if miss:
        refuse("%d C items have no mmlu_pro category (first %s)" % (len(miss), miss[:3]))
    return [first[q] for q in C_list], len(conflict)


def bfs_tree(g):
    parent, seen, q = {}, {g["root"]}, [g["root"]]
    while q:
        x = q.pop(0)
        for c in sorted(g["byid"][x].get("childIds") or []):
            if c not in seen:
                seen.add(c)
                parent[c] = x
                q.append(c)
    leaves = sorted(i for i in seen if not (g["byid"][i].get("childIds") or []))
    return parent, leaves


def load_mmlu_leg(args, out_lines, mmin=None):
    ss_ctx = args.get("ss_ctx") or SSUP.Ctx(data_root=args["mmlu_root"], triplets=args.get("triplets", TRIPLETS), kmeans=False)
    ctx = args.get("svk_ctx") or SVK.Ctx(data_root=args["mmlu_root"], triplets=args.get("triplets", TRIPLETS), ss_ctx=ss_ctx,
                                         dim=args.get("dim", DIM))
    lines = []
    W = SVK.load_mmlu(ctx, lines)
    out_lines.extend(lines)
    C_list = W["C"]
    cats, nconf = mmlu_categories(ctx.ss, C_list)
    engines = {}
    for t in W["trees"]:
        g = W["T"][t]["g"]
        parent, leaves = bfs_tree(g)
        mu = [g["byid"][lf].get("vmfMu") for lf in leaves]
        if all(m is not None and len(m) == W["dim"] for m in mu):
            engines[t] = dict(parent=parent, leaves=leaves, leaf_mu=S0.unit(np.array(mu, dtype=np.float64)))
    mm_t, eng = toml_params([os.path.join(args.get("cfg_root", ZC.ROOT), "experiment_configs", "anchorfree", "redraw", t) for t in REDRAW_TOMLS])
    if mmin is None:
        mmin = mm_t
    rs = np.random.RandomState(SEED_TRIP)
    trip = SVK.draw_triplets(len(C_list), args.get("triplets", TRIPLETS), rs)
    return dict(name="mmlu", nC=len(C_list), C=C_list, Xtr=W["XC"], cat=S0.codes(cats), ncat=len(set(cats)), nconf=nconf, engines=engines,
                L=args.get("L", {}).get("mmlu", L_REG["mmlu"]), m_min=mmin, trip=trip, eng=eng)


def load_intent(args, out):
    """granularity_gt.load_all unchanged (pins strict, census, trees checked), plus the CLINC EVAL OOS vectors (S1.load_raw)."""
    data_root = args["data_root"]
    snap = os.path.join(data_root, "snapshots.db")
    Ld = GG.load_all(data_root, args.get("pins_file"), snap, out=out)
    CS = Ld["W"]["CS"]
    dim = max(T["d"] for T, _ in Ld["trees"].values())
    Cc = CS["clinc"]
    oos_texts = set(Cc.text[i] for i in np.nonzero(Cc.kept & Cc.oos & (Cc.side == SPL.EVAL))[0])
    if oos_texts:
        Ld["W"]["vecs"]["qwen3"].update(S1.load_raw(Ld["emb"], oos_texts, dim))
    return Ld


def assemble_world(Ld, args, out):
    """TRAIN matrices (S1.fit_idx: TRAIN only) and the engine trees; EVAL is NOT read here."""
    world = {}
    S1.STATE["gate_frozen"] = False
    for c in CORPORA:
        n = ENGINE[c]
        A = S1.make_arm(Ld["W"], n, *Ld["trees"][n])
        L = args.get("L", {}).get(c, L_REG[c])
        if A["L"] != L:
            refuse("%s has %d leaves, the registered L for %s is %d" % (n, A["L"], c, L))
        if A["T"]["d"] != args.get("dim", DIM):
            refuse("%s slice %d != the registered %d" % (n, A["T"]["d"], args.get("dim", DIM)))
        tr = S1.fit_idx(A["C"], A["side"], S1.side_rows(A["C"], A["side"], A["have"], SPL.TRAIN), (SPL.TRAIN,), "CONSTRUCTION-ARMS %s TRAIN" % c)
        rd = os.path.join(S1.run_dir(S1.ARMS[n]["slug"], args["data_root"]), "diagnostics", "config.toml")
        mm_t, eng = toml_params([rd])
        mmin = args.get("m_min", {}).get(c) or mm_t
        world[c] = dict(name=c, A=A, C=A["C"], T=A["T"], L=L, m_min=mmin, tr_rows=tr, Xtr=A["X"][tr], eng=eng)
    return world


def unlock_eval(world, out):
    """GATE-before-EVAL respected: EVAL rows are requested only after every TRAIN matrix is frozen."""
    S1.STATE["gate_frozen"] = True
    for c in CORPORA:
        Wc = world[c]
        A, C = Wc["A"], Wc["C"]
        ev = S1.eval_rows(A)
        lab_c = np.concatenate([C.coarse[Wc["tr_rows"]], C.coarse[ev]]).astype(str)
        lab_f = np.concatenate([C.fine[Wc["tr_rows"]], C.fine[ev]]).astype(str)
        uc, cc = np.unique(lab_c, return_inverse=True)
        uf, cf = np.unique(lab_f, return_inverse=True)
        ntr = len(Wc["tr_rows"])
        Wc.update(ev_rows=ev, Xev=A["X"][ev], ev_coarse=cc[ntr:].astype(np.int64), ev_fine=cf[ntr:].astype(np.int64),
                  tr_fine=cf[:ntr].astype(np.int64), Kc=len(uc), comp=C.comp[ev])
        oos = np.nonzero(C.kept & C.oos & (A["side"] == SPL.EVAL) & A["have"])[0]
        if c == "clinc":
            Wc.update(oos_rows=oos, Xoos=A["X"][oos] if len(oos) else None)
            if not len(oos):
                Wc["Xoos"] = None
        Wc["engine"] = engine_readout(Wc)
        rs = np.random.RandomState(SEED_TRIP)
        Wc["trip"] = SVK.draw_triplets(len(Wc["Xtr"]), Wc.get("n_trip", TRIPLETS), rs)


def load_world(args, out_lines, out):
    """Real loader: the C leg FIRST (pool line first), then the intent corpora. Returns the world with TRAIN only."""
    mm = load_mmlu_leg(args, out_lines, args.get("m_min", {}).get("mmlu"))
    for ln in out_lines:                    # the pool guard's line is the first data line
        out(ln)
    if mm["nC"] != args.get("identity", IDENTITY)["C"]:
        refuse("I3 |C| = %d != %d (SS-R1 of record)" % (mm["nC"], args.get("identity", IDENTITY)["C"]))
    Ld = load_intent(args, out)
    world = assemble_world(Ld, args, out)
    world["mmlu"] = mm
    world["_Ld"] = Ld
    for c in CORPORA:
        world[c]["n_trip"] = args.get("triplets", TRIPLETS)
    return world


# ================================================================================================ modes
def default_out():
    return ZC.default_out("construction_arms", OUTCOME)


def resolve_args(ns, ov=None):
    ov = dict(ov or {})
    mc = main_checkout()
    a = dict(data_root=os.path.abspath(ns.data_root or os.environ.get("TAXOARENA_DATA_ROOT") or os.path.join(mc, ".claude", "worktrees", "intent-s1-run")),
             mmlu_root=os.path.abspath(ns.mmlu_root or mc), workers=int(ns.workers or 1), out=ns.out or default_out(),
             cfg_root=ZC.ROOT, identity=IDENTITY, B=B_BOOT, n_random=N_RANDOM, triplets=TRIPLETS)
    a.update(ov)
    if a["workers"] < 1 or a["workers"] > MAX_WORKERS:
        refuse("--workers %d outside 1..%d (the author's machine cap)" % (a["workers"], MAX_WORKERS))
    return a


_LOAD = {"world": load_world}


def run(args, out=print):
    path = args["out"]
    sums = os.path.join(os.path.dirname(os.path.abspath(path)), "SHA256SUMS.txt")
    for p in (path, sums):
        if os.path.lexists(p):
            refuse("%s exists: the outcome of record is WRITE-ONCE" % p)
    pins = check_code_pins(args.get("pinned"))
    if not args.get("skip_heavy"):
        S1.check_heavy()
    del S1.FIT_LOG[:]
    meta_lines = []
    world = _LOAD["world"](args, meta_lines, out)
    unlock_eval(world, out)
    idl = []
    identity_check(world, args["identity"], idl.append)
    for ln in idl:
        out(ln)
    F = run_fits(world, CORPORA + ("mmlu",), args["workers"], out)
    R = compute(world, F, args["B"], args["n_random"])
    Ld = world.get("_Ld")
    if Ld is not None:
        S0.pin_check(Ld["db"], "ingest_db", True, pins_file=args.get("pins_file"), label="ingest (after)")
        S0.pin_check(Ld["emb"], "emb", True, sub="qwen3", pins_file=args.get("pins_file"), label="intent_emb_qwen3.db (after)")
    me = os.path.abspath(__file__)
    meta = {"pins": ZC.pins_line(me),
            "imports": ["IMPORTS (LF blobs asserted): " + ", ".join("%s blob:%s" % kv for kv in sorted(pins.items()))],
            "pool": [ln for ln in meta_lines],
            "data": ["DATA: S1 root %s; MMLU root %s" % (args["data_root"], args["mmlu_root"])],
            "census": ["CENSUS %s: EVAL n %d in %d components (Kish %.4f); TRAIN %d; L %d; OOS rows %s" % (
                c, len(world[c]["ev_rows"]), len(np.unique(world[c]["comp"])), S0.kish(world[c]["comp"]), len(world[c]["Xtr"]), world[c]["L"],
                len(world[c]["oos_rows"]) if c == "clinc" else "-") for c in CORPORA] +
                      ["CENSUS mmlu: |C| %d, categories %d (conflicting duplicates %d), L %d" % (
                          world["mmlu"]["nC"], world["mmlu"]["ncat"], world["mmlu"]["nconf"], world["mmlu"]["L"])],
            "mmin": ["m_min (minClusterSize from the build TOMLs): massive %d, clinc %d, mmlu %d" % (
                world["massive"]["m_min"], world["clinc"]["m_min"], world["mmlu"]["m_min"])] +
                    ["ARM 1 ENGINE KNOBS (from the build TOMLs; registered expectation 4 / unset / 0.025 / 1.0): %s" % "; ".join(
                        "%s %s" % (leg, eng_text(dict(ENGINE_DEFAULTS, **(world[leg].get("eng") or {})))) for leg in ("massive", "clinc", "mmlu"))],
            "audit": ["TRAIN-ONLY fit audit (S1.fit_idx): " + "; ".join("%s %d rows sides %s" % (w, n, "/".join(s)) for w, _c, n, s in S1.FIT_LOG)],
            "identity": idl, "fixture": args.get("fixture")}
    lines = render(R, meta)
    h, _s = ZC.write_once(path, "\n".join(lines) + "\n", TAG)
    for ln in lines:
        out(ln)
    out("%s outcome written: %s (sha256 %s); WRITE-ONCE, never committed" % (TAG, path, h))
    return R, lines, path


def root_timings(Wc, out):
    X = Wc["Xtr"]
    n = len(X)
    t = {}
    t0 = time.time()
    e = dict(ENGINE_DEFAULTS, **(Wc.get("eng") or {}))
    EngineRule(Wc["m_min"], kmax=e["maxK"]).table(0, X, 0)
    t["ENGINE-SKM"] = time.time() - t0
    t0 = time.time()
    KappaRule(Wc["m_min"]).table(0, X, KMAX, 0)
    t["KAPPA-SKM"] = time.time() - t0
    t0 = time.time()
    split_skm2(X, 0)
    t["BISECT-SKM"] = time.time() - t0
    t0 = time.time()
    GmmRule().table(0, X, KMAX, 0)
    t["GMM-BIC"] = time.time() - t0
    m = min(n, 3000)
    sub = X[np.random.default_rng(0).choice(n, m, replace=False)]
    t0 = time.time()
    fit_ward(sub, min(Wc["L"], m - 1))
    t["WARD"] = (time.time() - t0) * (n / float(m)) ** 2
    t0 = time.time()
    fit_hdbscan(sub, m_min=Wc["m_min"])
    t["HDBSCAN"] = (time.time() - t0) * (n / float(m)) ** 2
    return t


def cost_estimate(world, legs, workers, out, timings=None):
    tot = 0.0
    lines = []
    for leg in legs:
        Wc = world[leg]
        t = timings[leg] if timings else root_timings(Wc, out)
        lev = math.ceil(math.log2(max(2, Wc["L"]))) + 1
        per = {"ENGINE-SKM": t["ENGINE-SKM"] * lev * 1.5, "KAPPA-SKM": t["KAPPA-SKM"] * lev * 1.5, "BISECT-SKM": t["BISECT-SKM"] * lev * 1.5, "GMM-BIC": t["GMM-BIC"] * lev * 1.5,
               "WARD": t["WARD"], "HDBSCAN": t["HDBSCAN"]}
        legsum = sum(per[a] * (5 + 5 * SUB_FRAC) for a in SEEDED) + sum(per[a] * (1 + 5 * SUB_FRAC ** 2) for a in ("WARD", "HDBSCAN"))
        tot += legsum
        lines.append("COST %s: n_TRAIN %d, L %d, root timings (s) %s; per fit estimate (s) %s; leg CPU about %.0f s" % (
            leg, len(Wc["Xtr"]), Wc["L"], ", ".join("%s %.1f" % kv for kv in t.items()), ", ".join("%s %.0f" % kv for kv in per.items()), legsum))
    n_fits = len(legs) * (len(SEEDED) * 10 + 2 * 6)
    readout = 2 * 17 * N_RANDOM * 0.03 + 2 * 17 * B_BOOT * 0.0005 + 3 * 42 * 2.0
    wall = tot / max(1, min(workers, n_fits)) + readout
    lines.append("COST ESTIMATE: 0 judge / LLM / embedding calls, 0 CCE; %d fits; fits about %.0f CPU-s (%.1f CPU-h) single-threaded; readout "
                 "(random-shape DP, bootstrap, triplets) about %.0f s; wall about %.0f min with %d worker(s) (%.0f min with 20)" % (
                     n_fits, tot, tot / 3600.0, readout, wall / 60.0, workers, (tot / min(20, n_fits) + readout) / 60.0))
    nmax = max(len(world[leg]["Xtr"]) for leg in legs)
    lines.append("MEMORY: WARD's condensed distances %.2f GB per full-TRAIN Ward fit (largest leg, n %d; %.2f GB per 90%% subsample); at most "
                 "6 Ward fits per leg; with %d worker(s) peak about %.1f GB" % (nmax * (nmax - 1) / 2 * 8 / 1e9, nmax,
                                                                           (0.9 * nmax) ** 2 / 2 * 8 / 1e9, workers,
                                                                           min(workers, 6) * nmax * (nmax - 1) / 2 * 8 / 1e9 + 0.2 * workers))
    for ln in lines:
        out(ln)
    return tot, wall


def dry_run(args, out=print):
    out("%s DRY RUN: zero calls; nothing written; no EVAL row read. %s" % (TAG, REG))
    out(ZC.pins_line(os.path.abspath(__file__)))
    pins = check_code_pins(args.get("pinned"))
    out("IMPORTS (LF blobs asserted): " + ", ".join("%s blob:%s" % kv for kv in sorted(pins.items())))
    if not args.get("skip_heavy"):
        S1.check_heavy()
    meta_lines = []
    world = _LOAD["world"](args, meta_lines, out)
    out("I3 |C| = %d (of record %d): OK" % (world["mmlu"]["nC"], args["identity"]["C"]))
    for c in CORPORA:
        out("%s: TRAIN %d rows (EVAL locked), L %d, m_min %d, engine %s %d leaves slice %d" % (
            c, len(world[c]["Xtr"]), world[c]["L"], world[c]["m_min"], ENGINE[c], len(world[c]["T"]["leaves"]), world[c]["T"]["d"]))
    out("mmlu: |C| %d, categories %d (conflicting duplicates %d), L %d, m_min %d, engine rows %s" % (
        world["mmlu"]["nC"], world["mmlu"]["ncat"], world["mmlu"]["nconf"], world["mmlu"]["L"], world["mmlu"]["m_min"],
        ", ".join("%s %d leaves" % (t, len(e["leaves"])) for t, e in world["mmlu"]["engines"].items())))
    out("ARM 1 ENGINE KNOBS (from the build TOMLs; registered expectation 4 / unset / 0.025 / 1.0): %s" % "; ".join(
        "%s %s" % (leg, eng_text(dict(ENGINE_DEFAULTS, **(world[leg].get("eng") or {})))) for leg in ("massive", "clinc", "mmlu")))
    if bool(S1.STATE.get("gate_frozen")):
        refuse("dry run: EVAL was unlocked (must not happen)")
    cost_estimate(world, CORPORA + ("mmlu",), args["workers"], out, args.get("timings"))
    out("%s DRY RUN complete: no EVAL row read; 0 files written" % TAG)
    return 0


# ================================================================================================ selftest
SELFTEST_DOC = """SELFTEST (value-asserting; fixtures under scratch_dir on E:):
  U-units: skm_best restart choice; kappa_banerjee; KappaRule (planted k, floor, bar, cap); GmmRule (planted k, single blob -> None, cap);
  best_first (largest first, skip unsplittable, forced count, cap, shortfall); the seam (fit_bisect through fit_bisecting: L leaves, all rows);
  fit_ward == scipy fcluster maxclust; HDBSCAN leaves == sklearn labels, noise leaf; dp_fast == S1.dendrogram_purity == brute force
  (weighted); leaf filing accuracy ties; cca_decide every branch (numpy bools, == boundaries, one corpus, mixed pairs, several winners);
  bootstrap == an independent loop on the same stream; band / Brier; sub_rows; conv conventions.
  E2E (main(["--run"]) on planted worlds, ARMS patched through the seam with oracle fits whose accuracy is known in closed form):
  E1 ARM-WINS (BISECT-SKM (c) and WARD (c) named; F-CA FIRES; FAILS names the refutation); E2 NO-ARM-WINS (clones; ARM-1-AHEAD printed
  for GMM-BIC); E3 one corpus only -> NO-ARM-WINS; E4 lower bound > 0 but D <= spread -> NO-ARM-WINS; every D, spread, bound against an
  independent recomputation; P-lines by value. E5 the REAL arms and REAL loaders on on-disk fixture roots (granularity_gt-style S1 root with
  OOS rows + stability_vs_kmeans' MMLU world): identity reproduced, output sane, write-once refusal, dry-run writes nothing and never
  unlocks EVAL, the process pool equals the serial fits. Refusals: I1, I2, I3, existing outcome, code pin, workers > 22, L mismatch."""


class _Fail(Exception):
    pass


def _chk(cond, msg):
    if not bool(cond):
        raise _Fail(msg)


def _brute_dp(parent, leaves, leaf_of, cls, w=None):
    """Independent DP: mean over same-class item pairs (copies by integer weight) of the class share in the LCA's subtree."""
    items = []
    for i, (lf, c) in enumerate(zip(leaf_of, cls)):
        items += [(lf, c)] * (1 if w is None else int(w[i]))

    def anc(x):
        out = [x]
        while x in parent:
            x = parent[x]
            out.append(x)
        return out
    A = {lf: anc(lf) for lf in set(leaves)}
    under = collections.defaultdict(collections.Counter)
    for lf, c in items:
        for a in A[lf]:
            under[a][c] += 1
    num, den = 0.0, 0
    for i in range(len(items)):
        for k in range(i + 1, len(items)):
            if items[i][1] != items[k][1]:
                continue
            a1 = A[items[i][0]]
            s2 = set(A[items[k][0]])
            lca = next(x for x in a1 if x in s2)
            tot = sum(under[lca].values())
            num += under[lca][items[i][1]] / float(tot)
            den += 1
    return num / den if den else float("nan")


# ---------------------------------------------------------------------------------------------- planted worlds (in memory)
_ORACLE = {}


def _oracle_fit(X, L, seed, m_min=None, info=None, arm=None):
    """Fixture-only fit: leaves = fine classes of the planted world; merges m(seed) disjoint class pairs (2i, 2i + 1) into one leaf and
    halves m other classes so the leaf count stays L; hierarchy = coarse groups. Accuracy (c) = 1 - m / F exactly (equal class sizes)."""
    spec = _ORACLE.get((info["leg"], arm)) or _ORACLE[(info["leg"], "ENGINE-SKM")]      # arm 1K defaults to arm 1's plant
    gold = _ORACLE[(info["leg"], "_gold")]
    cg = _ORACLE[(info["leg"], "_coarse_of")]
    rows = np.arange(len(gold)) if info.get("sub") is None else sub_rows(len(gold), info["sub"])
    g = gold[rows]
    m = spec["merges"][0 if seed is None else seed]
    F = int(gold.max()) + 1
    leaf_of_class = {}
    leaves = []
    for c in range(F):
        if c < 2 * m and c % 2 == 1:
            leaf_of_class[c] = leaf_of_class[c - 1]
            continue
        leaf_of_class[c] = len(leaves)
        leaves.append(c)
    lab = np.array([leaf_of_class[int(x)] for x in g], dtype=np.int64)
    halves = [c for c in range(F - 1, 2 * m - 1, -1)][:m]
    nxt = len(leaves)
    for c in halves:
        idx = np.nonzero(g == c)[0]
        lab[idx[::2]] = nxt
        leaves.append(c)
        nxt += 1
    names = ["O%03d" % j for j in range(len(leaves))]
    parent = {nm: "G%d" % cg[c] for nm, c in zip(names, leaves)}
    for gg in set(cg.tolist()):
        parent["G%d" % gg] = "OROOT"
    fz = spec.get("forced", (0, 0))
    return dict(kind=arm, lab=lab, nL=len(leaves), leaves=names, parent=parent, root="OROOT", forced=fz[0], rule_splits=fz[1], noise=None)


def _planted_corpus(rng, name, n_coarse, n_fine, n_tr, n_ev, dim, oos=0):
    F = n_coarse * n_fine
    ax = np.eye(dim)
    Xtr, Xev, gtr, gev = [], [], [], []
    for c in range(F):
        base = ax[c % dim] * 3.0 + ax[(F + c // n_fine) % dim] * 1.0
        Xtr.append(base + 0.15 * rng.standard_normal((n_tr, dim)))
        Xev.append(base + 0.15 * rng.standard_normal((n_ev, dim)))
        gtr += [c] * n_tr
        gev += [c] * n_ev
    Xtr, Xev = S0.unit(np.vstack(Xtr)), S0.unit(np.vstack(Xev))
    gtr, gev = np.array(gtr), np.array(gev)
    coarse_of = np.array([c // n_fine for c in range(F)])
    nev = len(gev)
    comp = np.arange(nev)
    comp[1::7] = comp[0::7][:len(comp[1::7])]          # some duplicate components (Kish > 1)
    Wc = dict(name=name, L=F, m_min=3, Xtr=Xtr, tr_fine=gtr.astype(np.int64), Xev=Xev, ev_fine=gev.astype(np.int64),
              ev_coarse=np.zeros(nev, dtype=np.int64), Kc=1, comp=comp, ev_rows=np.arange(nev))
    # the planted worlds decide on (c) in closed form: one coarse class makes every common-hierarchy DP 1.0, so (a) never clears
    # (D = 0) and its GR2 null is degenerate (flat flag exercised); (a) itself is value-tested against brute force in E5
    # engine row: a tree with leaves = fine classes under coarse groups, vmfMu = class means
    leaves = ["e%03d" % c for c in range(F)]
    tparent = {lf: "g%d" % coarse_of[c] for c, lf in enumerate(leaves)}
    for g in range(n_coarse):
        tparent["g%d" % g] = "eroot"
    mu = S0.unit(np.vstack([Xtr[gtr == c].mean(0) for c in range(F)]))
    Wc["T"] = dict(leaves=leaves, tparent=tparent, leaf_mu=mu, d=dim)
    if oos:
        Xo = S0.unit(rng.standard_normal((oos, dim)))
        Wc["Xoos"] = Xo
        Wc["oos_rows"] = np.arange(nev, nev + oos)
        Wc["C"] = type("Cfx", (), {})()
        Wc["C"].comp = np.concatenate([comp, np.arange(10 ** 6, 10 ** 6 + oos)])
    else:
        Wc["Xoos"] = None
        Wc["oos_rows"] = np.zeros(0, dtype=np.int64)
    _ORACLE[(name, "_gold")] = gtr
    _ORACLE[(name, "_coarse_of")] = coarse_of
    return Wc


def _planted_world(seed=5, n_trip=4000, oos=40):
    rng = np.random.default_rng(seed)
    W = {"massive": _planted_corpus(rng, "massive", 5, 2, 30, 20, 24),
         "clinc": _planted_corpus(rng, "clinc", 6, 2, 30, 20, 24, oos=oos)}
    mm = _planted_corpus(rng, "mmlu", 2, 2, 25, 1, 24)
    Wm = dict(name="mmlu", nC=len(mm["Xtr"]), C=list(range(len(mm["Xtr"]))), Xtr=mm["Xtr"], cat=(mm["tr_fine"] // 2).astype(np.int64), ncat=2,
              nconf=0, engines={"t0": dict(parent=mm["T"]["tparent"], leaves=mm["T"]["leaves"], leaf_mu=mm["T"]["leaf_mu"])}, L=4, m_min=3)
    W["mmlu"] = Wm
    for leg in ("massive", "clinc", "mmlu"):
        W[leg]["trip"] = SVK.draw_triplets(len(W[leg]["Xtr"]), n_trip, np.random.RandomState(SEED_TRIP))
    for c in CORPORA:
        W[c]["engine"] = engine_readout(W[c])
    return W


def _plant(merges, forced=None):
    """merges: {leg: {arm: [m per seed] or [m]}} -> patched ARMS (oracle fits through the seam)."""
    for leg, d in merges.items():
        for arm, m in d.items():
            _ORACLE[(leg, arm)] = dict(merges=m, forced=(forced or {}).get((leg, arm), (0, 1)))
    patched = collections.OrderedDict()
    for a in ALL_ARMS:
        patched[a] = ArmSpec(a, functools.partial(_oracle_fit, arm=a), "oracle (fixture)")
    return patched


_LOADS = []


def _run_planted(merges, td, tag, forced=None, B=300, oos=40, mmlu_mmin=3):
    W = _planted_world(oos=oos)
    W["mmlu"]["m_min"] = mmlu_mmin
    ident = dict(dp_massive="%.5f" % W["massive"]["engine"]["dp"], dp_clinc="%.5f" % W["clinc"]["engine"]["dp"],
                 A_T=("%.5f" % W["clinc"]["engine"]["A"]) if "A" in W["clinc"]["engine"] else "n/a", C=W["mmlu"]["nC"])
    saved = (dict(ARMS), _LOAD["world"], unlock_eval.__code__)
    ARMS.clear()
    ARMS.update(_plant(merges, forced))

    def loader(args, ml, out):
        _LOADS.append(tag)
        return W
    _LOAD["world"] = loader
    globals()["unlock_eval"] = lambda world, out: None
    try:
        out = os.path.join(td, tag, OUTCOME)
        buf = []
        rc = main(["--run", "--out", out], _ov=dict(B=B, n_random=20, identity=ident, skip_heavy=True, fixture="planted %s" % tag),
                  _out=buf.append)
        return rc, buf, out, W
    finally:
        ARMS.clear()
        ARMS.update(saved[0])
        _LOAD["world"] = saved[1]
        globals()["unlock_eval"] = _unlock_eval_real


def _brute_topo(H, rows, trip):
    """Independent triplet topology: clusters = every non-root node's row set (walk of the parent map); 0 ab|c, 1 ac|b, 2 bc|a, 3 none."""
    rows = np.asarray(rows)
    kids = collections.defaultdict(list)
    for c_, p_ in H["parent"].items():
        kids[p_].append(c_)
    pos = {lf: j for j, lf in enumerate(H["leaves"])}

    def mem(x):
        if x in pos:
            return set(rows[H["lab"] == pos[x]].tolist())
        out = set()
        for k_ in kids[x]:
            out |= mem(k_)
        return out
    cls = [mem(x) for x in set(H["parent"]) if x != H["root"]]
    res = []
    for a, b, c in trip.tolist():
        ab = any(a in S and b in S and c not in S for S in cls)
        ac = any(a in S and c in S and b not in S for S in cls)
        bc = any(b in S and c in S and a not in S for S in cls)
        k = int(ab) + int(ac) + int(bc)
        res.append(3 if k != 1 else (0 if ab else (1 if ac else 2)))
    return np.array(res)


def _line(buf, prefix):
    ls = [ln for ln in buf if ln.startswith(prefix)]
    _chk(len(ls) == 1, "expected one line %r, got %d" % (prefix, len(ls)))
    return ls[0]


def _dline(buf, c, r, j):
    ln = _line(buf, "D %s %s %-10s" % (c, RNAME[r], j))
    m = re.search(r"D ([+-]\d\.\d{5}) 95% \[([+-]\d\.\d{5}|n/a), ([+-]\d\.\d{5}|n/a)\] spread_1 (\d\.\d{5})", ln)
    _chk(m, "unparsed D line %r" % ln)
    return float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)), ln


def _indep_acc(W, c, m):
    """Independent (c) for the oracle with m merges: 1 - m / F (equal EVAL class sizes)."""
    F = int(W[c]["ev_fine"].max()) + 1
    return 1.0 - m / float(F)


def _indep_boot_c(W, c, merges, B):
    """Independent re-implementation of the registered bootstrap for readout (c) of BISECT-SKM vs ENGINE-SKM (same stream)."""
    rng = np.random.default_rng(20261006)    # the registered stream, literal (not the module constant)
    comp = W[c]["comp"]
    _u, cc = np.unique(comp, return_inverse=True)
    G = int(cc.max()) + 1
    F = int(W[c]["ev_fine"].max()) + 1
    g = W[c]["ev_fine"]

    def corr(m):        # correct iff the class is not a dropped (odd) member of a merged pair
        return np.array([not (x < 2 * m and x % 2 == 1) for x in g], dtype=np.float64)
    out, item = [], []
    for _b in range(B):
        w = np.bincount(rng.integers(G, size=G), minlength=G)[cc].astype(np.float64)
        ik = rng.integers(0, 5, size=5)
        ib = rng.integers(0, 5, size=5)
        rng.integers(0, 5, size=5)          # GMM-BIC
        rng.integers(0, 5, size=5)          # arm 1K (drawn last)
        vk = [float((w * corr(merges["ENGINE-SKM"][s])).sum() / w.sum()) for s in ik]
        vb = [float((w * corr(merges["BISECT-SKM"][s])).sum() / w.sum()) for s in ib]
        out.append(np.mean(vb) - np.mean(vk))
        item.append(np.mean([float((w * corr(m)).sum() / w.sum()) for m in merges["BISECT-SKM"]])
                    - np.mean([float((w * corr(m)).sum() / w.sum()) for m in merges["ENGINE-SKM"]]))
    lo, hi = np.percentile(out, [2.5, 97.5])
    return lo, hi, float(np.std(out, ddof=1)), float(np.std(item, ddof=1))


def _st_units(ok):
    rng = np.random.default_rng(1)
    # skm_best: best restart = max objective (two planted directions)
    X = S0.unit(np.vstack([np.eye(4)[0] + 0.05 * rng.standard_normal((20, 4)), np.eye(4)[1] + 0.05 * rng.standard_normal((20, 4))]))
    lab, _ = skm_best(X, 2, 3)
    _chk(len(set(lab[:20].tolist())) == 1 and len(set(lab[20:].tolist())) == 1 and lab[0] != lab[20], "skm_best planted split")
    ok()
    # ccs == brute 1 - mean within-pair dissimilarity / mean all-pair dissimilarity (unit rows)
    Xc = S0.unit(rng.standard_normal((30, 5)))
    lc = rng.integers(0, 3, 30)
    Dm = 1.0 - Xc @ Xc.T
    iu = np.triu_indices(30, 1)
    same = lc[iu[0]] == lc[iu[1]]
    _chk(abs(ccs(Xc, lc) - (1.0 - Dm[iu][same].mean() / Dm[iu].mean())) < 1e-10, "ccs == brute chance-corrected separation")
    ok()
    # engine_select: performVmfKMeans' k loop
    sz = {2: [9, 9], 3: [9, 9, 9], 4: [9, 9, 9, 9]}
    _chk(engine_select(sz, {2: 0.30, 3: 0.31, 4: 0.50}, 5, 0.025, 4) == 2, "engine_select: gain < eps stops the loop (no look-ahead)")
    ok()
    _chk(engine_select(sz, {2: 0.30, 3: 0.34, 4: 0.35}, 5, 0.025, 4) == 3 and engine_select(sz, {2: 0.3, 3: 0.34, 4: 0.40}, 5, 0.025, 4) == 4,
         "engine_select: k grows by the separation increment")
    ok()
    _chk(engine_select(sz, {2: 0.3, 3: 0.34, 4: 0.40}, 5, 0.025, 3) == 3, "engine_select: kmax (cap) respected")
    ok()
    _chk(engine_select({2: [9, 9], 3: [9, 9, 2], 4: [9, 9, 9, 9]}, {2: 0.3, 3: 0.9, 4: 0.95}, 5, 0.025, 4) == 2
         and engine_select({2: [2, 9]}, {2: 0.5}, 5, 0.025, 4) is None, "engine_select: an under-minSize candidate stops the loop")
    ok()
    # EngineRule on planted clusters
    X3 = S0.unit(np.vstack([np.eye(8)[i] * 2 + 0.1 * rng.standard_normal((30, 8)) for i in range(3)]))
    r = EngineRule(10)(0, X3, KMAX, 0)
    _chk(r is not None and len(set(r.tolist())) == 3, "EngineRule: 3 planted clusters -> k 3")
    ok()
    X6 = S0.unit(np.vstack([np.eye(8)[i] * 2 + 0.1 * rng.standard_normal((30, 8)) for i in range(6)]))
    r6 = EngineRule(10)(0, X6, KMAX, 0)
    _chk(r6 is not None and len(set(r6.tolist())) == 4, "EngineRule: maxK 4 on 6 planted clusters (%s)" % (None if r6 is None else len(set(r6.tolist()))))
    ok()
    er = EngineRule(10)
    r8 = er(0, X3, KMAX, 0)
    r2 = er(0, X3, 2, 0)
    _chk(len(set(r8.tolist())) == 3 and r2 is not None and len(set(r2.tolist())) == 2, "EngineRule cap 2 on the cached table")
    ok()
    _chk(EngineRule(40)(0, X3, KMAX, 0) is None, "EngineRule floor 40 > the smaller child -> no split")
    ok()
    e256 = np.zeros(256)
    e256[0] = 1.0
    Xn = S0.unit(e256 + 0.05 * rng.standard_normal((300, 256)))      # one isotropic 256-d blob: any 2-cut has ccs about 0.007 < 0.025
    _chk(EngineRule(10)(0, Xn, KMAX, 0) is None, "EngineRule: min-pair gate rejects a cut through one 256-d blob")
    ok()
    # coarsening: a weak pair merged; an under-floor fragment absorbed
    E2 = np.eye(256)
    Xa = S0.unit(np.vstack([E2[0] + 0.05 * rng.standard_normal((60, 256)), E2[0] + 0.05 * rng.standard_normal((60, 256)),
                            E2[1] + 0.05 * rng.standard_normal((60, 256))]))
    la = np.repeat([0, 1, 2], 60)
    ca = coarsen(Xa, la, 5, 0.025)
    _chk(len(set(ca.tolist())) == 2 and len(set(ca[:120].tolist())) == 1 and ca[0] != ca[120], "coarsen merges the pair below the bar")
    ok()
    Xf = S0.unit(np.vstack([np.eye(6)[0] + 0.01 * rng.standard_normal((30, 6)), np.eye(6)[1] + 0.01 * rng.standard_normal((30, 6)),
                            np.eye(6)[2] + 0.01 * rng.standard_normal((3, 6))]))
    cf = coarsen(Xf, np.repeat([0, 1, 2], [30, 30, 3]), 5, 0.025)
    _chk(len(set(cf.tolist())) == 2 and len(cf) == 63, "coarsen absorbs an under-floor fragment (k 3 -> 2, rows re-routed)")
    ok()
    # C-1 R1: filing to the RENORMALISED leaf mean (an item closer in cosine to a diffuse leaf)
    ct = 0.3
    st_ = math.sqrt(1 - ct * ct)
    Xd = np.array([[1.0, 0, 0], [1.0, 0, 0], [0, ct, st_], [0, ct, -st_]])
    Hd = dict(kind="T", lab=np.array([0, 0, 1, 1]), nL=2, leaves=["a", "b"], parent={"a": "r", "b": "r"}, root="r", noise=None)
    xq = np.array([[0.6, 0.7, math.sqrt(1 - 0.36 - 0.49)]])
    _chk(file_items(xq, Hd, leaf_centroids(Xd, Hd))[0].tolist() == [1], "filing: the diffuse leaf wins in cosine (renormalised centroid)")
    ok()
    # C-1 R6: diagonal covariance (an elongated blob is ONE diagonal Gaussian; a spherical GMM would split it)
    Xe = np.column_stack([rng.normal(0, 3, 300)] + [rng.normal(0, 0.1, 300) for _ in range(4)])
    _chk(GmmRule()(0, Xe, KMAX, 0) is None, "GmmRule diagonal: an elongated blob is not split")
    ok()
    # F1: the common hierarchy is Ward on the leaf centroids, identical for any own shape over the same leaves
    Hm = dict(kind="T", lab=np.repeat(np.arange(4), 5), nL=4, leaves=["p", "q", "r", "s"], parent={x: "R" for x in "pqrs"}, root="R", noise=None)
    Hb = dict(Hm, parent={"p": "u", "q": "v", "r": "u", "s": "v", "u": "R", "v": "R"})
    cm = S0.unit(np.array([[1, 0, 0], [0.9, 0.1, 0], [0, 1, 0], [0, 0.9, 0.2]], dtype=float))
    Pm, Pb = common_hier(Hm, cm)["parent"], common_hier(Hb, cm)["parent"]
    _chk(Pm == Pb and Pm["p"] == Pm["q"] and Pm["r"] == Pm["s"] and Pm["p"] != Pm["r"], "common hierarchy: shape-free, Ward on centroids")
    ok()
    _chk(shape_stats(Hm) == ({4: 1}, 1.0) and shape_stats(Hb) == ({2: 3}, 2.0), "shape_stats: children histogram and mean depth")
    ok()
    _chk("null degenerate (flat)" in gr2_text(0.5, 0.4, 1) and "flat" not in gr2_text(0.5, 0.4, 7), "GR2 degenerate-null flag")
    ok()
    _chk(abs(kappa_banerjee(0.5, 10) - 0.5 * (10 - 0.25) / 0.75) < 1e-12 and kappa_banerjee(1.0, 10) == 1e4, "kappa_banerjee")
    ok()
    # KappaRule: three planted directions of 30 -> k 3; floor 40 -> None; cap 2 -> 2 children
    X3k = S0.unit(np.vstack([np.eye(6)[i] * 2 + 0.1 * rng.standard_normal((30, 6)) for i in range(3)]))
    r = KappaRule(10)(0, X3k, KMAX, 0)
    _chk(r is not None and len(set(r.tolist())) == 3, "arm 1K KappaRule picks k = 3 on 3 planted clusters")
    ok()
    _chk(KappaRule(40)(0, X3k, KMAX, 0) is None, "arm 1K KappaRule floor 40 > every child -> no split")
    ok()
    kr2 = KappaRule(10)
    r8 = kr2(0, X3k, KMAX, 0)
    r2 = kr2(0, X3k, 2, 0)                    # the cached table read under a shrunken cap (the best-first flow)
    _chk(len(set(r8.tolist())) == 3 and r2 is not None and len(set(r2.tolist())) == 2, "arm 1K KappaRule cap 2 on the cached table")
    ok()
    Xnk = S0.unit(np.vstack([np.eye(6)[0] + 0.002 * rng.standard_normal((30, 6)), np.eye(6)[0] + 0.002 * rng.standard_normal((30, 6))]))
    _chk(KappaRule(5, bar=0.025)(0, Xnk, KMAX, 0) is None, "arm 1K KappaRule separation bar rejects near-identical directions")
    ok()
    kr = KappaRule(10)
    t = kr.table(0, X3k, KMAX, 0)
    best_k = max((k for k in t if t[k][0]), key=lambda k: (t[k][1], -k))
    _chk(len(set(kr(0, X3k, KMAX, 0).tolist())) == best_k and best_k == 3, "arm 1K KappaRule argmax kappa among admissible")
    ok()
    # C-1 R7: the stored kappa score is the SIZE-WEIGHTED mean of the children's Banerjee kappa
    for k_, (okk, sc_, lab_) in t.items():
        if okk:
            sz_ = np.bincount(lab_, minlength=k_)
            rr_ = [float(np.linalg.norm(X3k[lab_ == j].mean(0))) for j in range(k_)]
            want = sum(sz_[j] * kappa_banerjee(rr_[j], X3k.shape[1]) for j in range(k_)) / float(len(X3k))
            _chk(abs(sc_ - want) < 1e-9 and abs(sc_ - np.mean([kappa_banerjee(x, X3k.shape[1]) for x in rr_])) > 1e-6 or len(set(sz_.tolist())) == 1,
                 "arm 1K kappa score size-weighted (k %d)" % k_)
    ok()
    Xu = S0.unit(np.vstack([np.eye(6)[0] * 2 + 0.05 * rng.standard_normal((80, 6)), np.eye(6)[1] * 2 + 0.6 * rng.standard_normal((20, 6))]))
    tu = KappaRule(10).table(0, Xu, 2, 0)
    okk, sc_, lab_ = tu[2]
    sz_ = np.bincount(lab_, minlength=2)
    rr_ = [float(np.linalg.norm(Xu[lab_ == j].mean(0))) for j in range(2)]
    _chk(okk and sz_.min() != sz_.max() and abs(sc_ - sum(sz_[j] * kappa_banerjee(rr_[j], 6) for j in range(2)) / 100.0) < 1e-9
         and abs(sc_ - np.mean([kappa_banerjee(x, 6) for x in rr_])) > 1e-3, "arm 1K: unequal children, weighted != unweighted kappa")
    ok()
    # GmmRule
    Xg = np.vstack([np.eye(5)[i] * 4 + 0.3 * rng.standard_normal((40, 5)) for i in range(3)])
    g = GmmRule()(0, Xg, KMAX, 0)
    _chk(g is not None and len(set(g.tolist())) == 3, "GmmRule BIC picks 3 blobs")
    ok()
    _chk(GmmRule()(0, 0.3 * rng.standard_normal((80, 5)), KMAX, 0) is None, "GmmRule single blob -> k 1 -> no split")
    ok()
    gr = GmmRule()
    g8 = gr(0, Xg, KMAX, 0)
    g2 = gr(0, Xg, 2, 0)
    _chk(len(set(g8.tolist())) == 3 and g2 is not None and len(set(g2.tolist())) == 2, "GmmRule cap 2 on the cached table")
    ok()
    # best_first order, forced, cap, shortfall
    calls = []

    def rule_small(c, Xs, cap, seed):       # splits only nodes with < 50 rows, into 2
        calls.append((c, len(Xs), cap))
        return (np.arange(len(Xs)) % 2) if len(Xs) < 50 else None
    Xb = S0.unit(np.vstack([np.eye(6)[0] * 3 + 0.2 * rng.standard_normal((60, 6)), np.eye(6)[1] * 3 + 0.2 * rng.standard_normal((20, 6))]))
    H = best_first(Xb, 4, 0, rule_small, "T")
    _chk(H["nL"] == 4 and H["forced"] == 1 and H["rule_splits"] == 2, "best_first: one forced split of the root, then rule splits")
    ok()
    _chk(calls[0] == (0, 80, 4) and calls[1][1:] == (60, 3) and calls[2][1:] == (20, 3), "best_first: largest first, cap L - leaves + 1 (%s)" % calls[:3])
    ok()
    Hs = best_first(np.ones((3, 6)) / math.sqrt(6), 5, 0, lambda c, Xs, cap, s: None, "T")
    _chk(Hs["nL"] < 5, "best_first: shortfall when nothing is splittable")
    ok()
    # the seam: fit_bisect == best_first with the always-2 rule
    Xs_ = S0.unit(rng.standard_normal((90, 8)))
    hb = fit_bisect(Xs_, 6, 2)
    hf = best_first(Xs_, 6, 2, lambda c, Xx, cap, s: None, "B")
    _chk(hb["nL"] == 6 and hf["forced"] == 5, "seam fixture shapes")
    ok()
    P1_ = {frozenset(np.nonzero(hb["lab"] == j)[0].tolist()) for j in range(6)}
    _chk(len(P1_) == 6 and sum(len(s) for s in P1_) == 90, "fit_bisect partitions all rows")
    ok()
    # ward == fcluster maxclust
    from scipy.cluster.hierarchy import linkage, fcluster
    Xw = S0.unit(rng.standard_normal((60, 5)))
    hw = fit_ward(Xw, 7)
    fc = fcluster(linkage(Xw, "ward"), 7, "maxclust")
    _chk({frozenset(np.nonzero(hw["lab"] == j)[0].tolist()) for j in range(7)} == {frozenset(np.nonzero(fc == v)[0].tolist()) for v in set(fc)},
         "WARD leaves == scipy fcluster maxclust")
    ok()
    _chk(len(set(hw["parent"].values())) == 6, "WARD: L - 1 internal merges")
    ok()
    # hdbscan
    Xh = np.vstack([np.eye(4)[i] * 5 + 0.2 * rng.standard_normal((40, 4)) for i in range(3)] + [rng.uniform(-8, 8, (6, 4))])
    hh = fit_hdbscan(Xh, m_min=10)
    from sklearn.cluster import HDBSCAN
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        sl = HDBSCAN(min_cluster_size=10, copy=True).fit(Xh).labels_
    _chk(hh["n_clusters"] == len(set(sl.tolist()) - {-1}) and (hh["noise"] is not None) == bool((sl == -1).any()), "HDBSCAN leaves == sklearn")
    ok()
    _chk(abs(hh["noise_share"] - float(np.mean(sl == -1))) < 1e-12 and not hh["flat"], "HDBSCAN noise share, LCA verified")
    ok()
    # dp_fast == S1 == brute (weighted)
    for trial in range(4):
        Hh = best_first(S0.unit(rng.standard_normal((40, 4))), 6, trial, lambda c, Xs, cap, s: None, "T")
        lf = rng.integers(0, 6, 25)
        cl = rng.integers(0, 3, 25)
        w = rng.integers(0, 3, 25).astype(float)
        a1 = dp_fast(dp_struct(Hh), lf, cl, 3, w)
        a2 = S1.dendrogram_purity(Hh["parent"], Hh["leaves"], [Hh["leaves"][j] for j in lf], list(cl), w)
        a3 = _brute_dp(Hh["parent"], Hh["leaves"], [Hh["leaves"][j] for j in lf], list(cl), w)
        _chk(abs(a1 - a2) < 1e-12 and abs(a1 - a3) < 1e-12, "dp_fast == S1 == brute (%r %r %r)" % (a1, a2, a3))
        ok()
    # leaf majority ties to the smallest code
    Ht = dict(lab=np.array([0, 0, 1, 1]), nL=2)
    _chk(leaf_majority(Ht, [5, 2, 7, 7]) == [2, 7], "majority ties to the smallest label id")
    ok()
    # cca_decide
    def S(D, sp, lo, hi=1.0):
        return dict(D=np.float64(D), spread=np.float64(sp), lo=np.float64(lo), hi=np.float64(hi))
    base = {(j, r): {c: S(0.0, 0.01, -0.01) for c in CORPORA} for j in DECIDING for r in READOUTS}
    w_, win, fl = cca_decide(base)
    _chk(w_ == "NO-ARM-WINS" and win == [] and len(fl) == 6, "C-CA NO-ARM-WINS on nulls")
    ok()
    b2 = dict(base)
    b2[("WARD", "a")] = {c: S(0.05, 0.01, 0.01) for c in CORPORA}
    _chk(cca_decide(b2)[:2] == ("ARM-WINS", [("WARD", "a")]), "C-CA ARM-WINS names (WARD, a)")
    ok()
    b3 = dict(base)
    b3[("GMM-BIC", "c")] = {"massive": S(0.05, 0.01, 0.01), "clinc": S(0.05, 0.01, -0.001)}
    _chk(cca_decide(b3)[0] == "NO-ARM-WINS", "C-CA needs BOTH corpora")
    ok()
    b4 = dict(base)
    b4[("BISECT-SKM", "a")] = {c: S(0.01, 0.01, 0.01) for c in CORPORA}
    _chk(cca_decide(b4)[0] == "NO-ARM-WINS", "C-CA strict D > spread (equality fails)")
    ok()
    b5 = dict(base)
    b5[("BISECT-SKM", "a")] = {c: S(0.05, 0.01, 0.0) for c in CORPORA}
    _chk(cca_decide(b5)[0] == "NO-ARM-WINS", "C-CA strict lower bound > 0 (zero fails)")
    ok()
    b6 = dict(base)
    b6[("BISECT-SKM", "a")] = {"massive": S(0.05, 0.01, 0.01), "clinc": S(0.0, 0.01, -0.01)}
    b6[("BISECT-SKM", "c")] = {"massive": S(0.0, 0.01, -0.01), "clinc": S(0.05, 0.01, 0.01)}
    _chk(cca_decide(b6)[0] == "NO-ARM-WINS", "C-CA: the SAME (j, r) on both corpora")
    ok()
    b7 = dict(base)
    b7[("BISECT-SKM", "c")] = {c: S(0.05, 0.01, 0.01) for c in CORPORA}
    b7[("GMM-BIC", "a")] = {c: S(0.05, 0.01, 0.01) for c in CORPORA}
    _chk(cca_decide(b7)[1] == [("BISECT-SKM", "c"), ("GMM-BIC", "a")], "C-CA names every winner")
    ok()
    b8 = dict(base)
    b8[("WARD", "c")] = {c: S(0.05, 0.01, float("nan")) for c in CORPORA}
    _chk(cca_decide(b8)[0] == "NO-ARM-WINS", "C-CA nan bound fails")
    ok()
    _chk(ahead(S(-0.05, 0.01, -0.1, -0.01)) and not ahead(S(-0.05, 0.01, -0.1, 0.0)) and not ahead(S(-0.01, 0.01, -0.1, -0.01)), "ARM-1-AHEAD")
    ok()
    _chk(GG.band(0.5, 0.5, 0.6) == "HELD" and GG.band(0.6, 0.5, 0.6) == "HELD" and GG.band(0.61, 0.5, 0.6) == "FAILED", "closed bands")
    ok()
    _chk(band(0.5, (0.55, 0.5, 0.6)) == "HELD" and band(0.6, (0.55, 0.5, 0.6)) == "HELD" and band(0.6000001, (0.55, 0.5, 0.6)) == "FAILED",
         "band() wrapper closed at both ends")
    ok()
    # leaf filing accuracy reads the TRAIN majority (leaf 0: TRAIN majority 1, its EVAL items are 0 -> wrong)
    e = np.eye(3)
    Wt = dict(Xtr=np.vstack([e[0], e[0], e[0], e[1], e[1]]), tr_fine=np.array([1, 1, 0, 2, 2]), Xev=np.vstack([e[0], e[0], e[1]]),
              ev_fine=np.array([0, 0, 2]), ev_coarse=np.array([0, 0, 1]), Kc=2)
    Hx = dict(kind="T", lab=np.array([0, 0, 0, 1, 1]), nL=2, leaves=["a", "b"], parent={"a": "r", "b": "r"}, root="r", noise=None)
    fx_ = fit_readout(Wt, Hx)
    _chk(abs(fx_["fa"] - 1.0 / 3) < 1e-12 and fx_["filed"].tolist() == [0, 0, 1], "leaf filing accuracy = TRAIN-majority 1/3")
    ok()
    r_ = sub_rows(101, 3)
    _chk(len(r_) == 90 and len(set(r_.tolist())) == 90 and np.array_equal(r_, sub_rows(101, 3)) and not np.array_equal(r_, sub_rows(101, 4)),
         "sub_rows: floor(0.9 n), deterministic per s")
    ok()
    a_ = np.array([0, 1, 3, 3, 2], dtype=np.int8)
    b_ = np.array([0, 2, 3, 1, 2], dtype=np.int8)
    al, rb, rs = conv(a_, b_)
    _chk(abs(al - 0.4) < 1e-12 and abs(rb - 1.0 / 3) < 1e-12 and abs(rs - 0.6) < 1e-12, "conv: all 2/5, resolved-in-both 1/3")
    ok()
    # bootstrap == independent loop on the same stream
    comp = np.array([0, 0, 1, 2, 3, 4, 5, 5])
    vals = {"a": {a: np.array([0.1, 0.2, 0.3, 0.4, 0.5]) if a in SEEDED else np.array([0.7]) for a in ALL_ARMS},
            "c": {a: np.array([0.5, 0.5, 0.5, 0.5, 0.9]) if a in SEEDED else np.array([0.2]) for a in ALL_ARMS}}
    vals["a"]["BISECT-SKM"] = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    reps, _item = bootstrap_corpus(lambda w: vals, comp, 50, 7, ALL_ARMS)
    rng2 = np.random.default_rng(7)
    exp = []
    for _b in range(50):
        rng2.integers(6, size=6)
        ik, ib = rng2.integers(0, 5, 5), rng2.integers(0, 5, 5)
        rng2.integers(0, 5, 5)
        rng2.integers(0, 5, 5)
        exp.append(vals["a"]["BISECT-SKM"][ib].mean() - vals["a"]["ENGINE-SKM"][ik].mean())
    _chk(np.allclose(reps[("BISECT-SKM", "a")], exp), "bootstrap: crossed seed draws, order components -> KAPPA -> BISECT -> GMM")
    ok()
    _chk(np.allclose(reps[("WARD", "c")], [0.2 - vals["c"]["ENGINE-SKM"][rng_i].mean() for rng_i in _kappa_idx(comp, 50, 7)]),
         "bootstrap: WARD has no seed draw, arm 1 resampled")
    ok()


def _st_predlines(ok):
    """Every prediction print branch on a synthetic result whose words are known (P6 event both ways, P7 both ways, P8, P3)."""
    def R_(unk, unb, dk, db, auroc_d):
        trip = {c: {"seed": {CONTROL: (dk, 0.0), "BISECT-SKM": (db, 0.0), "GMM-BIC": (0.0, 0.0)},
                    "unres": {CONTROL: unk, "BISECT-SKM": unb, "GMM-BIC": 0.0}} for c in CORPORA}
        stats = {(j, r): {c: dict(D=0.0, spread=0.1, lo=-0.1, hi=0.1) for c in CORPORA} for j in DECIDING for r in READOUTS}
        corp = {c: {"vals": {r: {CONTROL: np.array([0.6] * 5)} for r in READOUTS}, "engine": {"dp": 0.5, "dp_common": 0.62},
                    "oos": ({"D": {a: auroc_d for a in DECIDING}} if c == "clinc" else None)} for c in CORPORA}
        fits = {leg: {"GMM-BIC": {"share": 0.95}} for leg in CORPORA + ("mmlu",)}
        return dict(corpora=corp, stats=stats, fits=fits, word="NO-ARM-WINS", trip=trip)
    L1 = prediction_lines(R_(0.3, 0.1, 0.05, 0.0, 0.005))
    _chk(_line(L1, "P6 overall") == "P6 overall: HELD", "P6 HELD when both conjuncts hold")
    ok()
    L2 = prediction_lines(R_(0.1, 0.3, 0.05, 0.0, 0.02))
    _chk(_line(L2, "P6 overall") == "P6 overall: FAILED" and _line(L2, "P6 (descriptive) massive").endswith("FALSE"), "P6 FAILED on the unresolved conjunct")
    ok()
    _chk("<= 0.010: TRUE; Brier %.4f" % ((0.7 - 1) ** 2) in _line(L1, "P7 ") and "<= 0.010: FALSE; Brier %.4f" % (0.7 ** 2) in _line(L2, "P7 "), "P7 both ways")
    ok()
    _chk(_line(L1, "P8 (descriptive) massive").endswith("-0.02000 in [-0.15, 0.03]: HELD"), "P8 by value")
    ok()
    _chk(_line(L1, "P3 GMM-BIC forced-split share massive").endswith("0.9500 in [0.00, 0.90]: FAILED"), "P3 forced share band")
    ok()


def _kappa_idx(comp, B, seed):
    rng = np.random.default_rng(seed)
    G = len(np.unique(comp))
    out = []
    for _b in range(B):
        rng.integers(G, size=G)
        out.append(rng.integers(0, 5, 5))
        rng.integers(0, 5, 5)
        rng.integers(0, 5, 5)
        rng.integers(0, 5, 5)
    return out


def _st_e2e_planted(ok, td):
    KAP = [1, 1, 2, 1, 1]
    # ---- E1: BISECT-SKM oracle and WARD oracle win on (c) on both corpora
    mer = {leg: {"ENGINE-SKM": KAP, "BISECT-SKM": [0] * 5, "GMM-BIC": KAP, "WARD": [0], "HDBSCAN": [1]} for leg in ("massive", "clinc", "mmlu")}
    rc, buf, out, W = _run_planted(mer, td, "E1", forced={("massive", "ENGINE-SKM"): (4, 1)}, mmlu_mmin=30)
    _chk(rc == 0 and os.path.isfile(out), "E1 ran and wrote the outcome")
    ok()
    txt = open(out, encoding="utf-8").read().splitlines()
    for c in CORPORA:
        F = int(W[c]["ev_fine"].max()) + 1
        D, lo, hi, sp, _ln = _dline(txt, c, "c", "BISECT-SKM")
        expD = _indep_acc(W, c, 0) - np.mean([_indep_acc(W, c, m) for m in KAP])
        _chk(abs(D - expD) < 1e-5 and abs(sp - 1.0 / F) < 1e-5, "E1 %s D(c) %.5f vs independent %.5f; spread %.5f" % (c, D, expD, sp))
        ok()
        elo, ehi, esd, eitem = _indep_boot_c(W, c, {"ENGINE-SKM": KAP, "BISECT-SKM": [0] * 5}, 300)
        _chk(abs(lo - elo) < 1e-5 and abs(hi - ehi) < 1e-5 and lo > 0, "E1 %s interval == independent loop" % c)
        ok()
        sup = _line(txt, "SUPPORT %s c BISECT-SKM" % c)
        m_ = re.search(r"SE\(D\) (\d\.\d{5}) .*item-only SD (\d\.\d{5})", sup)
        _chk(m_ and abs(float(m_.group(1)) - esd) < 1e-5 and abs(float(m_.group(2)) - eitem) < 1e-5,
             "E1 %s SE(D) %s / item-only SD %s == independent %.5f / %.5f" % (c, m_ and m_.group(1), m_ and m_.group(2), esd, eitem))
        ok()
        Dw, low, _hw, spw, _l = _dline(txt, c, "c", "WARD")
        _chk(abs(Dw - expD) < 1e-5 and low > 0 and abs(spw - sp) < 1e-12, "E1 %s WARD D(c)" % c)
        ok()
        Dg = _dline(txt, c, "c", "GMM-BIC")[0]
        _chk(abs(Dg) < 1e-12, "E1 %s GMM clone D 0" % c)
        ok()
    cca = _line(txt, "C-CA (THE ONE DECIDING CRITERION")
    _chk(cca.split(": ", 1)[1].startswith("ARM-WINS") and "BISECT-SKM (c) leaf filing accuracy" in cca and "WARD (c) leaf filing accuracy" in cca
         and "GMM-BIC" not in cca, "E1 C-CA ARM-WINS naming BISECT-SKM (c) and WARD (c): %s" % cca)
    ok()
    _chk(_line(txt, "F-CA ").startswith("F-CA FIRES") and "NO-ARM-WINS is refuted by" in _line(txt, "FAILS (rule 8)"), "E1 F-CA FIRES / FAILS")
    ok()
    _chk("rule mostly inactive" in _line(txt, "FITS massive ENGINE-SKM") and "rule mostly inactive" not in _line(txt, "FITS clinc ENGINE-SKM"),
         "E1 forced share 0.8 -> rule mostly inactive (massive only)")
    ok()
    p5 = _line(txt, "P5 ")
    _chk("outcome ARM-WINS" in p5 and "= %.4f" % ((0.10 - 1) ** 2) in p5, "E1 P5 Brier on ARM-WINS")
    ok()
    for c in CORPORA:
        x = np.mean([_indep_acc(W, c, m) for m in KAP])
        ln = _line(txt, "P1 arm 1 %s %s" % (RNAME["c"], c))
        _chk(("%.5f" % x) in ln and ln.endswith(GG.band(x, P1[("c", c)][1], P1[("c", c)][2])), "E1 P1 (c) %s by value" % c)
        ok()
        ln2 = _line(txt, "P2 BISECT-SKM D_c %s" % c)
        dd = _indep_acc(W, c, 0) - x
        _chk(((": %s (restated, informed)" % GG.band(dd, -0.03, 0.03)) in ln2), "E1 P2 D_c %s band" % c)
        ok()
    _chk("I1 DP(M-AF)" in _line(txt, "IDENTITY PRECONDITIONS") and _line(txt, "IDENTITY PRECONDITIONS").endswith("REPRODUCED"), "E1 identity line")
    ok()
    _chk(any(ln.startswith("SUPPORT massive c BISECT-SKM") for ln in txt) and any(ln.startswith("VERDICT LINE") for ln in txt), "E1 support")
    ok()
    sup = _line(txt, "SUPPORT clinc c WARD")
    _chk(re.search(r"seed term 0\.\d{5}", sup) and "n 240" in sup, "E1 support: n and seed term printed (%s)" % sup)
    ok()
    _chk(_line(txt, "P7 ").startswith("P7 (descriptive) every |D_AUROC|"), "E1 P7 scored (OOS present)")
    ok()
    _chk("(1 distinct draws; null degenerate (flat))" in _line(txt, "DESCRIPTIVE GR2 massive ENGINE-SKM"), "E1 C-3 degenerate GR2 null flagged (one coarse class)")
    ok()
    dl = _line(txt, "DISCLOSURE C leg")
    _chk("m_min x L = 30 x 4 = 120 > |C| 100" in dl and "mostly BISECT-SKM" in dl, "E1 C-4 disclosure (floor binds): %s" % dl)
    ok()
    for c in CORPORA:
        for j in DECIDING:
            for r in READOUTS:
                sl = _line(txt, "SUPPORT %s %s %-10s" % (c, r, j))
                m_ = re.search(r"SE\(D\) (\d\.\d{5}) .*seed-corrected SE (\d\.\d{5}) .*item-only SD (\d\.\d{5})", sl)
                se_, sc_, si_ = float(m_.group(1)), float(m_.group(2)), float(m_.group(3))
                _chk(abs(sc_ - math.sqrt(si_ ** 2 + max(0.0, se_ ** 2 - si_ ** 2) * 1.25)) < 2e-5 and sc_ >= se_ - 1e-5,
                     "C-2 seed-corrected SE %s %s %s" % (c, r, j))
        ok()
    # write-once: a second run over the same path refuses before any read
    # (b) by an independent brute-force topology on the oracle fits (state of the E1 plant)
    for c in CORPORA:
        Wc = W[c]
        n = len(Wc["Xtr"])
        tp = [_brute_topo(_oracle_fit(Wc["Xtr"], Wc["L"], s, info=dict(leg=c, sub=None), arm="ENGINE-SKM"), np.arange(n), Wc["trip"]) for s in SEEDS]
        un = np.mean([np.mean(t == 3) for t in tp])
        dis = np.mean([np.mean(tp[i] != tp[k]) for i in range(5) for k in range(i + 1, 5)])
        ln = _line(txt, "DESCRIPTIVE (b) %s seed pairs" % c)
        cov = np.mean([np.mean((tp[i] != 3) & (tp[k] != 3)) for i in range(5) for k in range(i + 1, 5)])
        _chk(("ENGINE-SKM %.4f / " % dis) in ln and ("[cov %.4f] (unres %.4f)" % (cov, un)) in ln,
             "E1 %s (b) arm-1 seed pairs %.4f cov %.4f unres %.4f in %s" % (c, dis, cov, un, ln))
        ok()
        ws = []
        for s in SEEDS:
            r = sub_rows(n, s)
            m = np.zeros(n, dtype=bool)
            m[r] = True
            msk = m[Wc["trip"]].all(axis=1)
            t = _brute_topo(_oracle_fit(Wc["Xtr"][r], Wc["L"], None, info=dict(leg=c, sub=s), arm="WARD"), r, Wc["trip"])
            ws.append(np.mean(t[msk] == 3))
        ln2 = _line(txt, "DESCRIPTIVE (b) %s 90%%-subsample pairs" % c)
        _chk(("WARD" in ln2) and (re.search(r"WARD \d\.\d{4} / (\d\.\d{4}|n/a) \[cov \d\.\d{4}\] \(unres %.4f\)" % np.mean(ws), ln2)),
             "E1 %s (b) WARD subsample unres %.4f in %s" % (c, np.mean(ws), ln2))
        ok()
        tb = [_brute_topo(_oracle_fit(Wc["Xtr"], Wc["L"], s, info=dict(leg=c, sub=None), arm="BISECT-SKM"), np.arange(n), Wc["trip"]) for s in SEEDS]
        unb = np.mean([np.mean(t == 3) for t in tb])
        p6 = _line(txt, "P6 (descriptive) %s" % c)
        _chk(p6.endswith("TRUE" if un > unb else "FALSE"), "E1 %s P6 unresolved conjunct by value (%.4f vs %.4f)" % (c, un, unb))
        ok()
    del _LOADS[:]
    rc2, buf2, _o, _W = _run_planted(mer, td, "E1")
    _chk(rc2 != 0 and any("WRITE-ONCE" in ln for ln in buf2) and not _LOADS, "E1 write-once refusal BEFORE any read (loads %s)" % _LOADS)
    ok()
    # ---- E2: all clones (NO-ARM-WINS) + GMM worse -> ARM-1-AHEAD
    mer2 = {leg: {"ENGINE-SKM": KAP, "BISECT-SKM": KAP, "GMM-BIC": [3] * 5, "WARD": [1], "HDBSCAN": [1]} for leg in ("massive", "clinc", "mmlu")}
    rc, buf, out, W = _run_planted(mer2, td, "E2")
    txt = open(out, encoding="utf-8").read().splitlines()
    cca = _line(txt, "C-CA (THE ONE DECIDING CRITERION")
    _chk(cca.endswith(": NO-ARM-WINS") and _line(txt, "F-CA ").startswith("F-CA NOT FIRED"), "E2 NO-ARM-WINS, F-CA NOT FIRED")
    ok()
    _chk("m_min x L = 3 x 4 = 12 <= |C| 100" in _line(txt, "DISCLOSURE C leg") and "does not by itself bind" in _line(txt, "DISCLOSURE C leg"),
         "E2 C-4 disclosure (floor does not bind)")
    ok()
    fl = _line(txt, "FAILS (rule 8)")
    _chk("ARM-WINS is refuted at the planned n" in fl and fl.count("D <= spread") >= 6, "E2 FAILS lists every (j, r)")
    ok()
    _chk(any(ln.startswith("ARM-1-AHEAD (descriptive): GMM-BIC (c) leaf filing accuracy (fine) massive") for ln in txt), "E2 ARM-1-AHEAD GMM")
    ok()
    _chk(not any(ln.startswith("ARM-1-AHEAD (descriptive): BISECT-SKM") for ln in txt), "E2 no ARM-1-AHEAD for the clone")
    ok()
    _chk("outcome NO-ARM-WINS" in _line(txt, "P5 ") and ("= %.4f" % (0.10 ** 2)) in _line(txt, "P5 "), "E2 P5 Brier on NO-ARM-WINS")
    ok()
    # ---- E3: BISECT oracle on massive only
    mer3 = {"massive": {"ENGINE-SKM": KAP, "BISECT-SKM": [0] * 5, "GMM-BIC": KAP, "WARD": [1], "HDBSCAN": [1]},
            "clinc": {"ENGINE-SKM": KAP, "BISECT-SKM": KAP, "GMM-BIC": KAP, "WARD": [1], "HDBSCAN": [1]},
            "mmlu": {"ENGINE-SKM": KAP, "BISECT-SKM": KAP, "GMM-BIC": KAP, "WARD": [1], "HDBSCAN": [1]}}
    rc, buf, out, W = _run_planted(mer3, td, "E3", oos=0)
    txt = open(out, encoding="utf-8").read().splitlines()
    _chk(_line(txt, "P7 ") == "P7 (descriptive) NOT SCORED: no OOS rows" and "I2 A(C-AF) n/a" in _line(txt, "IDENTITY"), "E3 skip path: P7 NOT SCORED")
    ok()
    _chk(_line(txt, "C-CA (THE ONE DECIDING CRITERION").endswith(": NO-ARM-WINS"), "E3 one corpus only -> NO-ARM-WINS")
    ok()
    _chk(_dline(txt, "massive", "c", "BISECT-SKM")[4].endswith("CLEARS both conjuncts") and _dline(txt, "clinc", "c", "BISECT-SKM")[4].endswith("fails"),
         "E3 massive clears, clinc fails")
    ok()
    # ---- E4: lower bound > 0 but D <= spread
    K4 = [1, 1, 1, 1, 3]
    mer4 = {leg: {"ENGINE-SKM": K4, "BISECT-SKM": [0] * 5, "GMM-BIC": K4, "WARD": [1], "HDBSCAN": [1]} for leg in ("massive", "clinc", "mmlu")}
    rc, buf, out, W = _run_planted(mer4, td, "E4")
    txt = open(out, encoding="utf-8").read().splitlines()
    for c in CORPORA:
        D, lo, hi, sp, ln = _dline(txt, c, "c", "BISECT-SKM")
        F = int(W[c]["ev_fine"].max()) + 1
        _chk(lo > 0 and D <= sp and abs(sp - 2.0 / F) < 1e-5 and abs(D - 1.4 / F) < 1e-5, "E4 %s lb > 0, D <= spread" % c)
        ok()
    _chk(_line(txt, "C-CA (THE ONE DECIDING CRITERION").endswith(": NO-ARM-WINS") and "BISECT-SKM c: massive (D <= spread)" in _line(txt, "FAILS"),
         "E4 NO-ARM-WINS on the spread conjunct alone")
    ok()
    # ---- E6: a deciding arm short of L (oracle with 4 merges on F = 10 keeps only 8 leaves) -> REFUSED, nothing written
    mer6 = {leg: {"ENGINE-SKM": KAP, "BISECT-SKM": [4] * 5, "GMM-BIC": KAP, "WARD": [1], "HDBSCAN": [1]} for leg in ("massive", "clinc", "mmlu")}
    rc, buf, out, W = _run_planted(mer6, td, "E6")
    _chk(rc != 0 and not os.path.exists(out) and any("not the registered L" in ln for ln in buf), "E6 matched-L refusal")
    ok()
    # ---- E7: the CONTROL alone short of L -> REFUSED
    mer7 = {leg: {"ENGINE-SKM": [4] * 5, "BISECT-SKM": KAP, "GMM-BIC": KAP, "WARD": [1], "HDBSCAN": [1]} for leg in ("massive", "clinc", "mmlu")}
    rc, buf, out, W = _run_planted(mer7, td, "E7")
    _chk(rc != 0 and not os.path.exists(out) and any("ENGINE-SKM on massive reached 8 leaves" in ln for ln in buf), "E7 control matched-L refusal")
    ok()


# ---------------------------------------------------------------------------------------------- on-disk fixture roots (real loaders)
def _fx_intent_root(td):
    """granularity_gt.build_fixture_root's world plus CLINC OOS rows (is_oos 1) and run-dir config.toml files (minClusterSize 4)."""
    import contextlib as _cl
    II = GG.II
    rng = np.random.default_rng(11)
    dim = 16
    rows_m, vm = GG._fx_rows(rng, "massive", 3, 4, 24, dim)
    rows_c, vc = GG._fx_rows(rng, "clinc", 4, 3, 22, dim)
    k = 90000
    for j in range(60):
        text = "clinc fixture oos item %d" % j
        sk = SPL.stem_key(text)
        side = SPL.side_of_hash(SPL.side_hash(sk))
        rows_c.append({"item_id": "clinc:o:%05d" % j, "corpus": "clinc", "orig_split": "oos", "orig_idx": str(k + j), "text": text,
                       "coarse": "oos", "fine": "oos", "is_oos": 1, "annot": None, "stem_key": sk, "hash_side": side, "side": side,
                       "drop_reason": None})
        vc[text] = rng.normal(size=dim).astype(np.float32)
    vecs = dict(vm)
    vecs.update(vc)
    os.makedirs(td, exist_ok=True)
    db = os.path.join(td, II.DB_NAME)
    with _cl.redirect_stdout(io.StringIO()):
        II.write_db(db, rows_m + rows_c, [])
    emb = os.path.join(td, "intent_emb_qwen3.db")
    con = sqlite3.connect(emb)
    con.execute("PRAGMA journal_mode=DELETE")
    con.execute("CREATE TABLE embeddings (query TEXT PRIMARY KEY, vector BLOB)")
    con.executemany("INSERT INTO embeddings VALUES (?, ?)", [(t, v.astype(">f4").tobytes()) for t, v in sorted(vecs.items())])
    con.commit()
    con.close()
    CS = S0.load_corpora(db)
    con = II.open_db_ro(db)
    items = II.rows_from_db(con)
    con.close()
    D_ex = S1.EX.derive(items)
    snap = os.path.join(td, "snapshots.db")
    con = sqlite3.connect(snap)
    con.execute("PRAGMA journal_mode=DELETE")
    con.execute("CREATE TABLE snapshots (id TEXT PRIMARY KEY, graph TEXT, settings TEXT)")
    leaves_n = {}
    for c, n in ENGINE.items():
        a = S1.ARMS[n]
        C = CS[c]
        side = S1.arm_sides(C, 1)
        Rm, _have = S1.raw_matrix(C, vecs, dim)
        X = S1.sliced(Rm, 8)
        g, s = GG._fx_graph(C, X, side, 8)
        sid = "fx_%s" % a["slug"]
        con.execute("INSERT INTO snapshots VALUES (?, ?, ?)", (sid, json.dumps(g), json.dumps(s)))
        rd = S1.run_dir(a["slug"], td)
        os.makedirs(os.path.join(rd, "validation"), exist_ok=True)
        os.makedirs(os.path.join(rd, "diagnostics"), exist_ok=True)
        open(os.path.join(rd, "headless_run.log"), "w").write("x - Successfully generated and saved snapshot. Snapshot ID: %s\n" % sid)
        open(os.path.join(rd, "validation", "MAIN_routing_diagnostics.txt"), "w").write("")
        T = S1.tree_of(g, s)
        leaves_n[c] = len(T["leaves"])
        open(os.path.join(rd, "dag_snapshots.jsonl"), "w").write(json.dumps({"nodes": [{"id": i, "isLeaf": i in T["leaves"]} for i in T["nodes"]]}) + "\n")
        d = D_ex[(c, 1)]
        man = {"intent_build": {"arm": n, "n_train": sum(1 for r in d["rows"] if r["side"] == SPL.TRAIN),
                                "n_gate": sum(1 for r in d["rows"] if r["side"] == SPL.GATE)}}
        json.dump(man, open(os.path.join(rd, "diagnostics", "run_manifest.json"), "w"))
        open(os.path.join(rd, "diagnostics", "config.toml"), "w").write("minClusterSize        = 4\nproposalSeparationBar = 0.025\n")
    con.commit()
    con.close()
    pins = os.path.join(td, "pins.json")
    json.dump({"schema": II.PINS_SCHEMA, "raw": {}, "ingest_db": II.file_sha(db), "emb": {"qwen3": II.file_sha(emb)}}, open(pins, "w"))
    cen, _bad = GG.census(CS)
    return dict(root=td, pins=pins, census=cen, leaves=leaves_n, CS=CS, vecs=vecs, dim=8)


def _fx_mmlu_root(td):
    rng = np.random.RandomState(3)
    X = SVK._planted_vectors(rng, "planted")
    trees = [SVK._planted_tree(t) for t in range(4)]
    ctx, universe = SVK._fix_world(td, trees, X, triplets=2000)
    con = sqlite3.connect(os.path.join(td, "mmlu_pro_dataset_cache_v2.db"))
    for j, t in enumerate(universe):
        cat = ("cat%d" % ((j // 15) // 2)) if j < SVK.NC_FIX else "priv"
        con.execute("UPDATE mmlu_pro SET category = ? WHERE question = ?", (cat, t))
    con.commit()
    con.close()
    cfg = os.path.join(td, "cfg", "experiment_configs", "anchorfree", "redraw")
    os.makedirs(cfg)
    for t in REDRAW_TOMLS:
        open(os.path.join(cfg, t), "w").write("minClusterSize        = 6\nproposalSeparationBar = 0.025\n")
    return ctx, os.path.join(td, "cfg")


def _st_e2e_real(ok, td):
    saved_n = dict(GG.REGISTERED_N)
    try:
        fx = _fx_intent_root(os.path.join(td, "s1"))
        for k_ in CORPORA:
            GG.REGISTERED_N[k_] = fx["census"][k_]
        mctx, cfg = _fx_mmlu_root(os.path.join(td, "mm"))
        # independent identity values: granularity_gt's own compute on the same root (I1); an inline max-cos AUROC (I2)
        Ld = GG.load_all(fx["root"], fx["pins"], os.path.join(fx["root"], "snapshots.db"), out=lambda s: None)
        Rg = GG.compute(Ld, boot_b=5, n_random=3, out=lambda s: None)
        Cc = fx["CS"]["clinc"]
        T = Ld["trees"]["C-AF"][0]
        ins = np.nonzero(Cc.kept & ~Cc.oos & (Cc.side == SPL.EVAL))[0]
        oos = np.nonzero(Cc.kept & Cc.oos & (Cc.side == SPL.EVAL))[0]

        def vx(i):
            return S0.unit(np.array([fx["vecs"][Cc.text[i]][:8]], dtype=np.float64))[0]
        a_t = S0.auroc([float(np.max(T["leaf_mu"] @ vx(i))) for i in ins], [float(np.max(T["leaf_mu"] @ vx(i))) for i in oos])
        ident = dict(dp_massive="%.5f" % Rg["corpora"]["massive"]["dp_tree"], dp_clinc="%.5f" % Rg["corpora"]["clinc"]["dp_tree"],
                     A_T="%.5f" % a_t, C=SVK.NC_FIX)
        _chk(len(oos) > 5, "fixture carries EVAL OOS rows (%d)" % len(oos))
        ok()
        ov = dict(B=60, n_random=5, triplets=2000, identity=ident, skip_heavy=True, fixture="real-arms fixture roots", dim=8,
                  L={"massive": fx["leaves"]["massive"], "clinc": fx["leaves"]["clinc"], "mmlu": 6}, svk_ctx=mctx, ss_ctx=mctx.ss,
                  cfg_root=cfg, pins_file=fx["pins"])
        argv = ["--data-root", fx["root"], "--mmlu-root", os.path.join(td, "mm")]
        # dry run: writes nothing, never unlocks EVAL, prints the cost estimate and the pool line first after the header
        buf = []
        before = set(os.listdir(td))
        S1.STATE["gate_frozen"] = False
        rc = main(["--dry-run"] + argv, _ov=dict(ov, timings={leg: {a: 0.01 for a in ALL_ARMS} for leg in ("massive", "clinc", "mmlu")}),
                  _out=buf.append)
        _chk(rc == 0 and set(os.listdir(td)) == before and not S1.STATE["gate_frozen"], "dry run: 0 files, EVAL locked")
        ok()
        _chk(any(ln.startswith("COST ESTIMATE: 0 judge") for ln in buf) and any(ln.startswith("POOL READER") for ln in buf), "dry run cost + pool")
        ok()
        pidx = [i for i, ln in enumerate(buf) if ln.startswith("POOL READER")][0]
        cidx = [i for i, ln in enumerate(buf) if "census" in ln][0]
        _chk(pidx < cidx, "dry run: the pool line precedes the intent loading")
        ok()
        out = os.path.join(td, "E5", OUTCOME)
        buf = []
        rc = main(["--run", "--out", out] + argv, _ov=ov, _out=buf.append)
        _chk(rc == 0 and os.path.isfile(out), "E5 real arms ran (rc %r): %s" % (rc, buf[-3:]))
        ok()
        txt = open(out, encoding="utf-8").read().splitlines()
        _chk(_line(txt, "IDENTITY PRECONDITIONS").endswith("REPRODUCED"), "E5 identity reproduced through the real loaders")
        ok()
        g2 = _line(txt, "DESCRIPTIVE GR2 massive WARD")
        _chk("null degenerate" not in g2 and re.search(r"\((\d+) distinct draws\)", g2) and int(re.search(r"\((\d+) distinct draws\)", g2).group(1)) > 1,
             "E5 live GR2 null not flagged: %s" % g2)
        ok()
        _chk("maxK 4, marginalEps unset (-> the bar), proposalSeparationBar 0.025, proposalAcceptMultiplier 1.00"
             in _line(txt, "ARM 1 ENGINE KNOBS"), "E5 engine knobs copied from the TOMLs and printed")
        ok()
        w = _line(txt, "C-CA (THE ONE DECIDING CRITERION").split(": ", 1)[1]
        _chk(w.startswith("ARM-WINS") or w == "NO-ARM-WINS", "E5 one of the two words")
        ok()
        # independent recomputation of a deciding D on the real fits: refit (deterministic) and score by brute force
        world = load_world(dict(resolve_args(_ns(["--run"] + argv), ov)), [], lambda s: None)
        unlock_eval(world, lambda s: None)
        for c in CORPORA:
            Wc = world[c]
            v = {}
            for a in ("ENGINE-SKM", "WARD"):
                vals = []
                for s in (SEEDS if a in SEEDED else (None,)):
                    H = ARMS[a].fit(Wc["Xtr"], Wc["L"], s, Wc["m_min"], None)
                    mu = np.vstack([Wc["Xtr"][H["lab"] == j].mean(0) for j in range(H["nL"])])
                    mu = mu / np.linalg.norm(mu, axis=1, keepdims=True)
                    fl = np.argmax(Wc["Xev"] @ mu.T, axis=1)
                    from scipy.cluster.hierarchy import linkage as _lk
                    Z = _lk(mu, method="ward")
                    nm = ["x%d" % j for j in range(H["nL"])] + ["z%d" % t for t in range(H["nL"] - 1)]
                    par = {}
                    for t, row in enumerate(Z):
                        par[nm[int(row[0])]] = nm[H["nL"] + t]
                        par[nm[int(row[1])]] = nm[H["nL"] + t]
                    vals.append(_brute_dp(par, nm[:H["nL"]], [nm[j] for j in fl], list(Wc["ev_coarse"])))
                v[a] = vals
            D, _lo, _hi, sp, _ln = _dline(txt, c, "a", "WARD")
            _chk(abs(D - (np.mean(v["WARD"]) - np.mean(v["ENGINE-SKM"]))) < 1e-5 and abs(sp - (max(v["ENGINE-SKM"]) - min(v["ENGINE-SKM"]))) < 1e-5,
                 "E5 %s D(a) WARD and spread == brute-force recomputation" % c)
            ok()
        # the process pool equals the serial fits
        F1 = run_fits({"mmlu": world["mmlu"]}, ("mmlu",), 1, lambda s: None)
        F2 = run_fits({"mmlu": world["mmlu"]}, ("mmlu",), 2, lambda s: None)
        _chk(all(np.array_equal(F1[k]["lab"], F2[k]["lab"]) and F1[k]["parent"] == F2[k]["parent"] for k in F1), "pool == serial fits")
        ok()
        # refusals
        for lab_, key, val in (("I1", "dp_massive", "0.00000"), ("I2", "A_T", "0.00000")):
            b2 = []
            o2 = os.path.join(td, "R" + lab_, OUTCOME)
            rc = main(["--run", "--out", o2] + argv, _ov=dict(ov, identity=dict(ident, **{key: val})), _out=b2.append)
            _chk(rc != 0 and not os.path.exists(o2) and any("IDENTITY PRECONDITION FAILED" in ln and lab_ in ln for ln in b2), "%s refusal" % lab_)
            ok()
        b3 = []
        o3 = os.path.join(td, "RI3", OUTCOME)
        rc = main(["--run", "--out", o3] + argv, _ov=dict(ov, identity=dict(ident, C=ident["C"] + 1)), _out=b3.append)
        _chk(rc != 0 and not os.path.exists(o3) and any("I3" in ln for ln in b3), "I3 refusal")
        ok()
        b4 = []
        rc = main(["--run", "--out", os.path.join(td, "RL", OUTCOME)] + argv, _ov=dict(ov, L=dict(ov["L"], massive=ov["L"]["massive"] + 1)),
                  _out=b4.append)
        _chk(rc != 0 and any("registered L" in ln for ln in b4), "L mismatch refusal")
        ok()
        b5 = []
        rc = main(["--run", "--out", os.path.join(td, "RP", OUTCOME)] + argv, _ov=dict(ov, pinned=dict(PINNED_CODE, **{"site_support.py": "0" * 40})),
                  _out=b5.append)
        _chk(rc != 0 and any("instrument of record" in ln for ln in b5), "code pin refusal")
        ok()
        b6 = []
        rc = main(["--run", "--workers", "23", "--out", os.path.join(td, "RW", OUTCOME)] + argv, _ov=ov, _out=b6.append)
        _chk(rc != 0 and any("machine cap" in ln for ln in b6), "workers > 22 refusal")
        ok()
    finally:
        GG.REGISTERED_N.clear()
        GG.REGISTERED_N.update(saved_n)
        S1.STATE["gate_frozen"] = False


def _ns(argv):
    return build_parser().parse_args(argv)


def selftest():
    n = [0]

    def ok():
        n[0] += 1
    t0 = time.time()
    with scratch_dir.scratch("construction_arms_st") as td:
        try:
            _st_units(ok)
            _st_predlines(ok)
            _st_e2e_planted(ok, td)
            _st_e2e_real(ok, td)
        except _Fail as e:
            print("%s SELFTEST FAILED after %d checks: %s" % (TAG, n[0], e))
            return 1
    print("%s SELFTEST OK: %d value checks in %.1f s" % (TAG, n[0], time.time() - t0))
    return 0


# ================================================================================================ mutants (sandbox copies only)
MUTANTS = [
    ("X01", "C-CA on either corpus (any instead of all)", "            ok = [clears(per[c]) for c in CORPORA]\n            if all(ok):",
     "            ok = [clears(per[c]) for c in CORPORA]\n            if any(ok):"),
    ("X02", "C-CA D >= spread", "    return bool(s[\"D\"] > s[\"spread\"]) and bool(s[\"lo\"] > 0)\n\n\ndef ahead",
     "    return bool(s[\"D\"] >= s[\"spread\"]) and bool(s[\"lo\"] > 0)\n\n\ndef ahead"),
    ("X03", "C-CA lower bound >= 0", "    return bool(s[\"D\"] > s[\"spread\"]) and bool(s[\"lo\"] > 0)\n\n\ndef ahead",
     "    return bool(s[\"D\"] > s[\"spread\"]) and bool(s[\"lo\"] >= 0)\n\n\ndef ahead"),
    ("X04", "C-CA spread conjunct dropped", "    return bool(s[\"D\"] > s[\"spread\"]) and bool(s[\"lo\"] > 0)\n\n\ndef ahead",
     "    return bool(s[\"D\"] > 0) and bool(s[\"lo\"] > 0)\n\n\ndef ahead"),
    ("X05", "C-CA interval conjunct dropped", "    return bool(s[\"D\"] > s[\"spread\"]) and bool(s[\"lo\"] > 0)\n\n\ndef ahead",
     "    return bool(s[\"D\"] > s[\"spread\"])\n\n\ndef ahead"),
    ("X06", "C-CA first winner only", "                winners.append((j, r))\n", "                winners.append((j, r)) if not winners else None\n"),
    ("X07", "C-CA HDBSCAN deciding / WARD dropped", "DECIDING = (\"BISECT-SKM\", \"GMM-BIC\", \"WARD\")",
     "DECIDING = (\"BISECT-SKM\", \"GMM-BIC\", \"HDBSCAN\")"),
    ("X08", "D sign flipped", "        D = float(vj.mean() - v1.mean())", "        D = float(v1.mean() - vj.mean())"),
    ("X09", "spread = SD instead of range", "    return float(v.max() - v.min()) if len(v) == len(SEEDS) else float(\"nan\")",
     "    return float(v.std(ddof=1)) if len(v) == len(SEEDS) else float(\"nan\")"),
    ("X10", "spread from the arm j's seeds (wrong population)", "    R[\"spread\"] = {r: spread5(R[\"vals\"][r][CONTROL]) for r in READOUTS}",
     "    R[\"spread\"] = {r: spread5(R[\"vals\"][r][\"BISECT-SKM\"]) for r in READOUTS}"),
    ("X11", "seeds paired (arm j reuses arm 1's draw)", "                mj = float(vj[idx[j]].mean()) if j in SEEDED else float(vj.mean())",
     "                mj = float(vj[idx[CONTROL]].mean()) if j in SEEDED else float(vj.mean())"),
    ("X12", "seeds not resampled", "            m1 = float(v1[idx[CONTROL]].mean())", "            m1 = float(v1.mean())"),
    ("X13", "components not resampled (weights 1)", "        w = np.bincount(rng.integers(G, size=G), minlength=G)[cc].astype(np.float64)\n        idx",
     "        w = np.ones(len(cc)) + 0 * np.bincount(rng.integers(G, size=G), minlength=G)[cc]\n        idx"),
    ("X14", "percentiles 5 / 95", "    lo, hi = np.percentile(x, [2.5, 97.5])", "    lo, hi = np.percentile(x, [5.0, 95.0])"),
    ("X15", "bootstrap seed + 1", "SEED_BOOT = 20261006", "SEED_BOOT = 20261007"),
    ("X16", "seed draw order GMM before BISECT", "SEEDED = (\"ENGINE-SKM\", \"BISECT-SKM\", \"GMM-BIC\", \"KAPPA-SKM\")",
     "SEEDED = (\"ENGINE-SKM\", \"GMM-BIC\", \"BISECT-SKM\", \"KAPPA-SKM\")"),
    ("X17", "leaf majority from EVAL labels", "    maj = leaf_majority(H, Wc[\"tr_fine\"])\n    correct",
     "    maj = S1.majority(list(Wc[\"ev_fine\"]), list(filed), H[\"nL\"])\n    correct"),
    ("X18", "DP on the fine level", "    dp = dp_s1(Hc, filed[ok], Wc[\"ev_coarse\"][ok]) if ok.any() else float(\"nan\")",
     "    dp = dp_s1(Hc, filed[ok], Wc[\"ev_fine\"][ok]) if ok.any() else float(\"nan\")"),
    ("X19", "dp_fast drops the child subtraction", "    own = P - st[\"Ch\"] @ P", "    own = P"),
    ("X20", "kappa rule picks min kappa", "            if k <= cap and ok and (best is None or sc > best[0]):",
     "            if k <= cap and ok and (best is None or sc < best[0]):"),
    ("X21", "kappa rule floor dropped", "                if sizes.min() < self.m_min:", "                if sizes.min() < 1:"),
    ("X22", "kappa rule separation bar dropped", "                if sep < self.bar:", "                if sep < -1.0:"),
    ("X23", "kappa rule cap ignored", "            if k <= cap and ok and (best is None or sc > best[0]):",
     "            if ok and (best is None or sc > best[0]):"),
    ("X24", "GMM max BIC", "        kb = min(ks, key=lambda k: (tab[k][0], k))", "        kb = max(ks, key=lambda k: (tab[k][0], k))"),
    ("X25", "GMM k = 1 never compared (range from 2)", "            for k in range(1, min(self.kmax, cap, len(Xs)) + 1):",
     "            for k in range(2, min(self.kmax, cap, len(Xs)) + 1):"),
    ("X26", "best-first smallest first", "        order = sorted(live, key=lambda c: (-len(rows[c]), c))", "        order = sorted(live, key=lambda c: (len(rows[c]), c))"),
    ("X27", "forced splits not counted", "        forced += int(isf)", "        forced += 0"),
    ("X28", "cap L - leaves (off by one)", "        cap = L - len(live) + 1", "        cap = L - len(live)"),
    ("X29", "rule mostly inactive at >= 0.5 of the forced share... threshold 0.9", "INACTIVE = 0.5", "INACTIVE = 0.9"),
    ("X30", "WARD cut at L - 1 merges replayed wrong (n - L + 1)", "    for j in range(n - L):\n        uf[int(Z[j, 0])] = n + j",
     "    for j in range(n - L + 1):\n        uf[int(Z[j, 0])] = n + j"),
    ("X31", "identity I1 not refused", "    if bad:\n        refuse(\"IDENTITY PRECONDITION FAILED", "    if False:\n        refuse(\"IDENTITY PRECONDITION FAILED"),
    ("X32", "identity I2 clause ignored", "    if got[\"A_T\"] != ident[\"A_T\"]:", "    if False:"),
    ("X33", "I3 not refused", "    if mm[\"nC\"] != args.get(\"identity\", IDENTITY)[\"C\"]:", "    if False:"),
    ("X34", "write-once dropped (mode w, no pre-check)", "        if os.path.lexists(p):\n            refuse(\"%s exists: the outcome of record is WRITE-ONCE\" % p)",
     "        if False:\n            refuse(\"%s exists: the outcome of record is WRITE-ONCE\" % p)"),
    ("X35", "F-CA FIRES line unprinted", "        L.append(\"F-CA FIRES: a generic", "        0 and L.append(\"F-CA FIRES: a generic"),
    ("X36", "FAILS unprinted on NO-ARM-WINS", "        L.append(\"FAILS (rule 8): ARM-WINS is refuted", "        0 and L.append(\"FAILS (rule 8): ARM-WINS is refuted"),
    ("X37", "P5 Brier on the wrong event", "    bs = (P5_WIN - (1.0 if win else 0.0)) ** 2", "    bs = (P5_WIN - (0.0 if win else 1.0)) ** 2"),
    ("X38", "bands open", "    return GG.band(x, b[1], b[2])", "    return \"HELD\" if (b[1] < x < b[2]) else \"FAILED\""),
    ("X39", "ARM-1-AHEAD without the interval", "    return bool(s[\"D\"] < -s[\"spread\"]) and bool(s[\"hi\"] < 0)", "    return bool(s[\"D\"] < -s[\"spread\"])"),
    ("X40", "workers cap removed", "    if a[\"workers\"] < 1 or a[\"workers\"] > MAX_WORKERS:", "    if a[\"workers\"] < 1:"),
    ("X41", "L check removed", "        if A[\"L\"] != L:", "        if False:"),
    ("X42", "code pins unchecked", "        if b != want:\n            refuse(\"%s is blob:%s", "        if False:\n            refuse(\"%s is blob:%s"),
    ("X43", "dry run unlocks EVAL", "    if bool(S1.STATE.get(\"gate_frozen\")):\n        refuse(\"dry run", "    unlock_eval(world, out)\n    if False:\n        refuse(\"dry run"),
    ("X44", "first corpus only in the support MDE", "    for c in CORPORA:\n        Rc = R[\"corpora\"][c]\n        for (j, r), s in Rc[\"stats\"].items():",
     "    for c in CORPORA[:1]:\n        Rc = R[\"corpora\"][c]\n        for (j, r), s in Rc[\"stats\"].items():"),
    ("X45", "triplet unresolved share counts topology 0", "            out[\"unres\"][a] = float(np.mean([np.mean(t == 3) for t in tp]))",
     "            out[\"unres\"][a] = float(np.mean([np.mean(t == 0) for t in tp]))"),
    ("X46", "subsample fraction 1.0", "SUB_FRAC = 0.9", "SUB_FRAC = 1.0"),
    ("X47", "WARD gets a seed draw of its own (seeded)", "SEEDED = (\"ENGINE-SKM\", \"BISECT-SKM\", \"GMM-BIC\", \"KAPPA-SKM\")",
     "SEEDED = (\"ENGINE-SKM\", \"BISECT-SKM\", \"GMM-BIC\", \"WARD\", \"KAPPA-SKM\")"),
    ("X48", "matched-L refusal for deciding arms dropped", "            if x[\"H\"][\"nL\"] != Wc[\"L\"]:", "            if False:"),
    ("X55", "GMM cap ignored", "        ks = [k for k in sorted(tab) if k <= cap]", "        ks = [k for k in sorted(tab)]"),
    ("X49", "item-only SD from the crossed replicates", "                item[(j, r)][b] = float(vj.mean()) - float(v1.mean())",
     "                item[(j, r)][b] = mj - m1"),
    ("X50", "arms fitted on EVAL (wrong split side)", "        X, L, mm = Wc[\"Xtr\"], Wc[\"L\"], Wc[\"m_min\"]",
     "        X, L, mm = Wc.get(\"Xev\", Wc[\"Xtr\"]), Wc[\"L\"], Wc[\"m_min\"]"),
    ("X51", "P7 NOT SCORED line dropped (skip path)", "        L.append(\"P7 (descriptive) NOT SCORED: no OOS rows\")",
     "        pass"),
    ("X52", "subsample unresolved share from topology 0", "        out[\"unres_sub\"][a] = float(np.mean([np.mean(t[m] == 3) for t, m in zip(tps, ins)]))",
     "        out[\"unres_sub\"][a] = float(np.mean([np.mean(t[m] == 0) for t, m in zip(tps, ins)]))"),
    ("X53", "seed-pair disagreement over the first pair only", "            prs = [conv(tp[i], tp[k]) for i in range(5) for k in range(i + 1, 5)]",
     "            prs = [conv(tp[i], tp[k]) for i in range(5) for k in range(i + 1, 5)][:1]"),
    ("X54", "P6 event ignores the unresolved conjunct", "        ev.append(bool(h == \"HELD\") and un)",
     "        ev.append(bool(h == \"HELD\"))"),
    ('X56', 'engine maxK 8', 'MAXK_ENGINE = 4 ',
     'MAXK_ENGINE = 8 '),
    ('X57', 'engine increment always accepted', '        elif deltas[k] - bd >= eps:',
     '        elif deltas[k] - bd >= -1.0:'),
    ('X58', 'engine increment loop does not stop (look-ahead)', '            best, bd = k, deltas[k]\n        else:\n            break',
     '            best, bd = k, deltas[k]\n        else:\n            continue'),
    ('X59', 'coarsening merge dropped', '        if wi >= 0 and weak < bar and k > 2:',
     '        if False:'),
    ('X60', 'min-pair gate dropped', 'and min_pair_sep(Xs, lab) >= self.bar:',
     'and True:'),
    ('X61', 'ccs pairFrac uses n_c^2', '        pf += len(g) * (len(g) - 1.0)',
     '        pf += len(g) * len(g)'),
    ('X62', 'coarsening fragment absorption dropped', '            if len(surv) < 2:\n                break',
     '            if True:\n                break'),
    ('X63', 'common hierarchy average-link instead of Ward', 'COMMON_LINK = "ward"',
     'COMMON_LINK = "average"'),
    ('X64', '(a) scored on the own hierarchy (F1 undone)', '    dp = dp_s1(Hc, filed[ok], Wc["ev_coarse"][ok]) if ok.any() else float("nan")',
     '    dp = dp_s1(H, filed[ok], Wc["ev_coarse"][ok]) if ok.any() else float("nan")'),
    ('X65', 'seed-corrected SE factor 1.0', 'SEED_CORR = len((0, 1, 2, 3, 4)) / float(len((0, 1, 2, 3, 4)) - 1)',
     'SEED_CORR = 1.0'),
    ('X66', 'C-4 disclosure unprinted', '    L.append("DISCLOSURE C leg (C-4)',
     '    0 and L.append("DISCLOSURE C leg (C-4)'),
    ('X67', 'arm 1K enters C-CA', 'DECIDING = ("BISECT-SKM", "GMM-BIC", "WARD")',
     'DECIDING = ("BISECT-SKM", "GMM-BIC", "WARD", "KAPPA-SKM")'),
    ('X68', "P8 against the engine's own tree", 'C_[c]["engine"]["dp_common"]',
     'C_[c]["engine"]["dp"]'),
    ('X69', 'R1 filing centroids not renormalised', '    return S0.unit(C)\n\n\ndef file_items',
     '    return C\n\n\ndef file_items'),
    ('X70', 'R2 control dropped from the matched-L refusal', '    for a in DECIDING + (CONTROL,):\n        for x in fr[a]:',
     '    for a in DECIDING:\n        for x in fr[a]:'),
    ('X71', 'R6 GMM covariance spherical', 'covariance_type="diag"',
     'covariance_type="spherical"'),
    ('X72', 'R7 arm 1K kappa unweighted', 'sizes[j] * kappa_banerjee(float(r[j]), d) for j in range(k)) / n)',
     'kappa_banerjee(float(r[j]), d) for j in range(k)) / k)'),
    ('X73', 'joint coverage printed as the unresolved share', 'f5(T["seed"][a][1], "%.4f"), T["seed"][a][2],',
     'f5(T["seed"][a][1], "%.4f"), T["unres"][a],'),
    ('X74', 'degenerate-null flag never raised', '"; null degenerate (flat)" if nd == 1 else "")',
     '"")'),
]


def run_mutants(jobs=8, out=print):
    """Every mutant: a copy of this script with one replacement in a scratch sandbox (TMP / TEMP / TMPDIR / TAXOARENA_TMP inside it), its
    --selftest run in a subprocess; KILLED iff rc != 0. A no-op control C0 must SURVIVE first. Never touches a real path."""
    from concurrent.futures import ThreadPoolExecutor
    me = os.path.abspath(__file__)
    src = open(me, encoding="utf-8").read()
    cut = src.index("\nMUTANTS = [")
    head, rest = src[:cut], src[cut:]
    allm = [("C0", "no-op control (must survive)", "TAG = \"[CONSTRUCTION-ARMS]\"", "TAG = \"[CONSTRUCTION-ARMS]\"")] + MUTANTS
    res = {}
    with scratch_dir.scratch("construction_arms_mutants") as box:
        def one(m):
            mid, desc, old, new = m
            cnt = head.count(old)
            if cnt != 1:
                return mid, desc, "NOT APPLIED (%d occurrences)" % cnt, ""
            d = os.path.join(box, mid)
            os.makedirs(os.path.join(d, "tmp"))
            p = os.path.join(d, os.path.basename(me))
            with open(p, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(head.replace(old, new) + rest)
            env = dict(os.environ)
            env["PYTHONPATH"] = HERE + os.pathsep + env.get("PYTHONPATH", "")
            env["ZC_REPO_ROOT"] = ZC.ROOT
            for v in ("TMP", "TEMP", "TMPDIR", "TAXOARENA_TMP"):
                env[v] = os.path.join(d, "tmp")
            try:
                cp = subprocess.run([sys.executable, p, "--selftest"], env=env, capture_output=True, text=True, timeout=3600,
                                    encoding="utf-8", errors="replace")
                rc, tail = cp.returncode, ((cp.stdout + cp.stderr).strip().splitlines() or [""])[-1]
            except subprocess.TimeoutExpired:
                rc, tail = "timeout", "timeout"
            return mid, desc, ("killed" if rc != 0 else "SURVIVED"), tail[:150]
        with ThreadPoolExecutor(max_workers=jobs) as ex:
            for mid, desc, v, tail in ex.map(one, allm):
                res[mid] = (desc, v, tail)
                out("  %-4s %-62s %s  (%s)" % (mid, desc[:62], v, tail[:100]))
    k = sum(1 for m in MUTANTS if res[m[0]][1] == "killed")
    out("MUTANTS: %d / %d killed; control C0 %s" % (k, len(MUTANTS), res["C0"][1]))
    return 0 if (k == len(MUTANTS) and res["C0"][1] == "SURVIVED") else 1


# ================================================================================================ main
def build_parser():
    ap = argparse.ArgumentParser(description="CONSTRUCTION-ARMS readout (zero calls)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--mutants", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--run", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--data-root")
    ap.add_argument("--mmlu-root")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--jobs", type=int, default=8)
    return ap


def main(argv=None, _ov=None, _out=None):
    ns = build_parser().parse_args(argv)
    if ns.selftest:
        return selftest()
    if ns.mutants:
        return run_mutants(ns.jobs)
    if _out is None:
        args = resolve_args(ns, _ov)
        if ns.dry_run:
            return dry_run(args)
        run(args)
        return 0
    buf = io.StringIO()                     # selftest: printed refusals of the imported guards are captured too
    rc = 0
    with contextlib.redirect_stdout(buf):
        try:
            args = resolve_args(ns, _ov)
            if ns.dry_run:
                rc = dry_run(args, _out)
            else:
                run(args, _out)
        except SystemExit as e:
            _out("%s REFUSED (exit): %s" % (TAG, e))
            rc = 2
    for ln in buf.getvalue().splitlines():
        _out(ln)
    return rc


_unlock_eval_real = unlock_eval

if __name__ == "__main__":
    sys.exit(main())
