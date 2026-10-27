# Label-free tests on the embedding space itself (2026-10-04)

Literature scan for the author. Zero calls. Nothing run, built, registered or committed. As of HEAD bd5ca001.
Read first: `docs/agents/KNOWLEDGE.md`, `2026-10-04_testing_logic_review.md`, memo v3, and the results JSONs GOLD-LEVEL-EMB,
GEMMA-OWN-BAR, E1-SPLIT-DRAWS, CERT-K2-DEFLATED and CERT-PC-SIZE.
**Citation marks.** [V] = abstract or proceedings page opened in this pass. [S] = title, authors and venue agree across search
listings, but the abstract was not opened. "unverified" = from memory; check before citing.

## 0. What the record already says, and the one design rule that follows

- **Geometry already measured** (EMBEDDER-CROSS-FLAT E0b, printed and not scored; MMLU-Pro, 8,125 fit texts, 256-d):

  | Space | Anisotropy (mean pairwise cosine) | Participation ratio (PR) | Mutual kNN@10 vs qwen3 | Linear CKA vs qwen3 |
  |---|---|---|---|---|
  | qwen3_raw | 0.270 | 90.8 | (reference) | (reference) |
  | gemma_raw | 0.319 | 97.7 | 0.395 | 0.590 |
  | nomic_raw | 0.449 | 86.4 | 0.376 | 0.586 |
  | gemma_card | 0.648 | 45.7 | not copied | not copied |
  | nomic_card | 0.595 | 62.5 | not copied | not copied |

  Source: `experiment_results/embedder_cross_flat/e0b_*_outcome.txt`. The **"centred" anisotropy** printed beside these rows is
  close to 0 by construction for every space. After centring, the pairwise dot products of n vectors sum to -Σ‖x‖², so the
  mean is about -1/(n-1). That column carries no information. Use IsoScore or the top-PC variance share instead.
- **Prompts compress the space.** The card prompts roughly halve the PR (gemma 97.7 → 45.7). This matches Tsukagoshi & Sasano
  (ACL Findings 2025, arXiv:2506.01435) [V]: embeddings made with clustering or classification prompts have lower intrinsic
  dimension and are less isotropic than those made with retrieval prompts. GOLD-LEVEL-EMB's PROMPT NOT-INVARIANT is the
  label-side image of the same effect.
- **Gemma does not split** (GEMMA-OWN-BAR). The root separation is 0.42x its own moment-matched null p95. That null p95 is
  *higher* for gemma at 768-d than for qwen3 at 256-d, which is opposite to what the width-only D1 rule predicts.
  CERT-K2-DEFLATED: the deflated null tracks the variance of the cut axis.
  Both point the same way: **the record's nulls already match second moments** (the site null is a Gaussian with the
  population's mean and covariance, projected to the sphere). Anything a covariance determines is therefore invisible to the
  certificate. This includes anisotropy, PR, whitening, linear CKA and the size of a cut along a high-variance axis. All of
  these move the *bar* and the *null*. None of them is structure.
- **Design rule for every test below.** Split statistics into two kinds and treat them differently:
  - **(A) Second-moment descriptors** (spectrum, PR, IsoScore, intrinsic dimension). These explain bar and null magnitudes,
    and are reported only as descriptions.
  - **(B) Beyond-second-moment structure** (modality, tree-likeness, hubness, multi-scale agreement). These are scored only
    *relative to the moment-matched Gaussian null of record* (same generator as SeparationNullBySizeTest's siteNull arm).
  Without that null, high-dimensional artefacts read as structure. Three known ones: Hopkins is near 1 for almost any
  high-dimensional data (Wright, *R Journal* 2022, "Will the Real Hopkins Statistic Please Stand Up?") [S]. Sparse
  high-dimensional data tends toward ultrametricity (Murtagh, *J. Classification* 21:167-184, 2004) [V]. Hubness grows with
  intrinsic dimension (Radovanović et al., *JMLR* 11:2487-2531, 2010) [V].

**Substrate (zero calls; all read-only, `mode=ro&immutable=1`).**
- `intent_emb_{qwen3, qwen3_q8, qwen3_card, gemma, gemma_card, nomic}.db`: 57,350 texts each, one text set (sha256
  0ba7eb3c…), covering MASSIVE, CLINC and Banking77.
  - The card prompts are an intent instruction for qwen3 and "task: clustering" for gemma.
  - **q4 vs q8 is a ready-made noise floor**: same model and prompt, different quantisation.
- MMLU-Pro: `embeddings_cache.db` (qwen3) and `experiment_results/embedder_cross/*.db` (gemma and nomic, raw and card,
  11,687 texts).
- Anything that feeds a bar is TRAIN-only (rule 1). Reading `embeddings_cache.db` makes the test a pool reader under rule 7.

## 1. Methods, ranked

Value: how far the result could move a thesis sentence. Cost is CPU unless marked. Every row is zero-call and feasible on the
DBs above.

| # | Method | Question it answers here | Kind | Cost | Record items | Key citations |
|---|---|---|---|---|---|---|
| 1 | **Spectrum census.** Eigen-spectrum, PR, IsoScore, top-PC share, TwoNN and MLE intrinsic dimension (global, plus per anchor / per gold class), per embedder × prompt × width × corpus | Why does gemma not split, and why does the gemma null p95 exceed qwen3's? Is "embedder-dependent structure" just a different spectrum? | A | minutes | GEMMA-OWN-BAR P1 / W-2, D1 bar rule, E1-SD N_e1sd1, GOLD-LEVEL-EMB PROMPT | TwoNN (Facco et al., *Sci. Rep.* 7:12140, 2017) [V]; MLE (Levina & Bickel, NIPS 2004) [V]; IsoScore (Rudman et al., ACL Findings 2022) [V]; Tsukagoshi & Sasano 2025 [V] |
| 2 | **Modality against the moment-matched null.** Projected dip on the 2-means axis and top PCs (dip-means style), with selection replayed in the null; folding test as a second statistic | Are certified or declared splits *gaps* (modes) or cuts along elongated axes? Closes the open **dip half of L6** | B | CPU hours | L6 dip half (CONTEXT §5), MIX-LRT-SITE, CERT-K2-DEFLATED DF2, CERT-PC-SIZE | Hartigan & Hartigan, *Ann. Stat.* 13:70-84, 1985 [V]; dip-means (Kalogeratos & Likas, NIPS 2012) [V]; folding test (Siffer et al., KDD 2018) [V]; Adolfsson et al., *Pattern Recognit.* 88:13-26, 2019 [V] |
| 3 | **Tree-likeness against the null.** Gromov δ_rel (sampled 4-point), an ultrametricity index, cophenetic correlation of average-link | Does this corpus have hierarchical structure *at all* in this embedder, beyond a Gaussian with the same covariance? | B | CPU hours (δ is O(n⁴); sample 10⁵-10⁶ quadruples) | P3 / D6 hierarchy wording, T-C2, GRANULARITY-GT GR2 | δ_rel (Khrulkov et al., CVPR 2020) [V]; Murtagh 2004 [V]; Chourasia, Ali, Patterson, arXiv:2512.20926 (δ, ultrametricity, NJ on LLM embeddings; preprint) [V]; Sokal & Rohlf 1962 [S] |
| 4 | **Multi-scale cross-space agreement.** Mutual kNN at k ∈ {10, 50, 200, 1000}, AMI between k-means partitions at k ∈ {2, 4, …, 256}, debiased CKA, orthogonal Procrustes; q4/q8 as the floor | Is structure shared across embedders and prompts at coarse scale and divergent at fine scale? At which k does "embedder-dependent" start? | B (relative) | minutes to an hour | GOLD-LEVEL-EMB EMBEDDER / PROMPT NOT-INVARIANT, E1-SPLIT-DRAWS, SQ5 | CKA (Kornblith et al., ICML 2019) [V]; CKA caveats (Davari et al., ICLR 2023) [V]; mutual kNN (Huh et al., ICML 2024) [V], with the scale caveat that k must grow with n (arXiv:2604.18572) [S] |
| 5 | **Hubness.** k-occurrence skewness, hub share, before and after mutual-proximity or f-norm | Do a few hub items dominate neighbourhoods, inflating leaf sizes and kNN routing? | B | minutes | KNN-ROUTE (registered), leaf-size skew | Radovanović et al. 2010 [V]; Feldbauer & Flexer, *KAIS* 59:137-166, 2019 [V]; Nielsen & Hansen, NLDL 2024 (Sentence-BERT) [V] |
| 6 | **Whitening / all-but-the-top sensitivity.** Separation and gold AMI after removing the top-m PCs or whitening (the engine already has `whiten` and `dropTop` flags) | Is gemma's weak separation a few dominant directions swamping the rest? | A→B | CPU; a site null costs machine time | GEMMA-OWN-BAR (width-only bar untested), siteNull `-Dwhiten` | Mu & Viswanath, ICLR 2018 [V]; Su et al., arXiv:2103.15316 [V]; Mickus et al., ACL 2024 (isotropy is incompatible with clusters) [V]; Parupudi, arXiv:2606.29571 (top-direction share predicts the best metric) [V] |
| 7 | **Local intrinsic dimension (LID) per cell / anchor** | Do anchors that split have lower LID than anchors that stall? | A | minutes | G12 0 of 60, CERT-ALIGN-SIZE strata | Levina & Bickel 2004 [V]; Amsaleg et al., KDD 2015 (LID) unverified |
| 8 | **Density / multi-scale.** HDBSCAN cluster persistence and stability over min_cluster_size | Is there density structure at any scale? | B (needs the null) | CPU | N1 algorithm sensitivity | Campello et al., PAKDD 2013 [S] |
| 9 | **Gap statistic** with the moment-matched reference instead of the uniform box | Number of clusters under a fair reference | B | CPU | duplicates the J null | Tibshirani, Walther & Hastie, *JRSS-B* 63:411-423, 2001 [V] |
| 10 | **Hopkins** | Clustering tendency | (B) | trivial | none: about 1 in high dimension | Lawson & Jurs, *JCICS* 30:36-41, 1990 [S]; Wright 2022 [S] |
| 11 | **Hyperbolic embedding distortion** (Poincaré / h-MDS fit) | Low-distortion tree embedding? | B | GPU or CPU, days of agent time | redundant with #3 | Sala et al., ICML 2018 [V]; HypHC (Chami et al., NeurIPS 2020; relaxes Dasgupta's cost, the same family as the record's separation statistic) [V] |

Rows 9-11 are low priority. Row 9 duplicates what the J null already does. Row 10 is uninformative in high dimension. Row 11 is
costly and answers row 3's question less directly. Hierarchical *concepts* do have geometric signatures inside LLMs (Park,
Choe, Jiang, Veitch, ICLR 2025) [V], but that is in the model's residual stream, not in a pooled embedding. Do not cite it as
evidence that query embeddings are tree-like.

## 2. The top four, specified for registration

**Shared settings.**
- **Arms.** qwen3 (q4), qwen3_q8, qwen3_card, gemma, gemma_card and nomic on MASSIVE and CLINC (intent DBs). Add qwen3,
  gemma_raw and nomic_raw on MMLU-Pro TRAIN of draw 5a3e756.
- **Widths.** Each arm at 256-d (MRL-valid slice; renormalised by the readers' rule) and at native width.
- **Null.** The moment-matched spherical Gaussian (siteNull's generator, re-implemented in numpy). It is validated against
  the Kotlin generator on one site before use, and that check is an identity precondition. B = 200 null draws.
- **Inputs.** Labels are never read except in the positive controls named below. Seeds are fixed now.

**G1 GEO-SPECTRUM** (row 1, with 6 and 7 as descriptive columns). *Question:* is the embedder dependence of splitting a
spectrum effect?
- Compute, per arm × width × corpus (and per MMLU-Pro B0 anchor): PR, IsoScore, top-1 and top-10 PC shares, TwoNN ID (with
  the 10% tail discarded, as Facco et al. recommend), MLE ID at k = 20, and the LID distribution.
- **Scored prediction GS1.** Across the 2 existing moment-matched null p95s from GEMMA-OWN-BAR (gemma 768, qwen3 256) and the
  new numpy nulls on the same roots for all arm × width cells, log(null p95) falls as PR rises (Spearman ρ ≤ -0.6, CI by
  bootstrap over cells).
- **GS2.** gemma at 256-d has a null p95 within ±15% of qwen3 at 256-d. If so, GEMMA-OWN-BAR's 0.0437 bar is a *width*
  effect, and the 768-d build was the wrong comparison.
- **Falsifier.** GS1 fails, so the bar inflation is not a spectrum property, and W-2 (k-way null vs min-pair gate) becomes the
  leading explanation.
- **Ties.** GEMMA-OWN-BAR P1 / W-2 / the width-only bar 0.0109, and the D1 bar rule.
- **Cost.** CPU about 1 h; coder about 3 h.

**G2 MODAL-SPLIT** (row 2). *Question:* do certified splits sit on density gaps, or on elongated axes only?
- **Sites.**
  - G12's 14 TOP sites and their 60 depth-1 sites, with members as the site null read them.
  - Positive control: the declared 14-category MMLU-Pro partition at n 486 (certified 5 of 5 in CERT-PC-SIZE).
  - Negative control: the PC1 median cut used in CERT-K2-DEFLATED.
- **Statistic.** The Hartigan dip of the projection onto the 2-means axis, with the 2-means fit *repeated inside every null
  draw*. A projection chosen to look bimodal has a biased dip, so the selection must be replayed in the null. Second
  statistic: the folding test.
- **Criteria.**
  - **MS0 (size).** The moment-matched null is rejected in ≤ 1 of 20 Gaussian self-draws.
  - **MS1.** The positive control is rejected (p < 0.05) in ≥ 4 of 5.
  - **MS2 (deciding).** The share of G12 sites with p_dip < 0.05 after BH within family. A share above the null's 5% means
    "certified splits have modal support". A share inside it means "the certificate is geometric, not modal", now *with* a
    texture-robust test. A univariate dip is insensitive to heavy tails and skew, the texture that made the GMM LR reject
    everywhere (MIX-LRT-SITE).
- **Falsifier.** MS1 fails, so the dip has no power at depth-1 sizes, and L6 stays OPEN with a power statement.
- **Ties.** L6 dip half; CERT-K2-DEFLATED's "axis variance, not structure".
- **Cost.** CPU about 2 h. It reads embeddings_cache.db, so it is a pool reader (rule 7); outside any construction window.

**G3 TREE-LIKE** (row 3). *Question:* does the space have hierarchy beyond its covariance?
- **Samples.** Per arm × corpus: 2,000 TRAIN points, 5 subsamples.
- **Statistics.**
  - δ_rel = 2δ / diam over 10⁶ sampled quadruples (Khrulkov's estimator), on angular distance.
  - Ultrametricity index: the share of triangles whose two largest sides agree within 2%.
  - Cophenetic correlation of average-link.
- **Readout.** Each statistic as a z-score against the moment-matched null.
- **Controls.**
  - Positive: a planted 3-level hierarchical vMF mixture with the arm's spectrum.
  - Negative: the null itself.
- **Criteria.**
  - **TL1 (deciding).** z(δ_rel) < -2 (more tree-like than the null) in ≥ 4 of 5 subsamples, per arm.
  - **TL2.** The ordering across arms agrees with the order of tree leaf counts the record already has (qwen3 M-AF 84 leaves
    > gemma 4; descriptive).
- **Falsifier of P3 / D6 hierarchy wording.** TL1 fails for qwen3 on MASSIVE and CLINC, which have known two-level gold. Then
  any tree hierarchy is imposed by the algorithm, not found. That outcome would make GRANULARITY-GT GR2's random-tree
  comparison the only defensible hierarchy claim.
- **Cost.** CPU about 3 h; coder about 4 h.

**G4 SCALE-AGREE** (row 4). *Question:* at what scale do embedders agree?
- **Pairs.** All pairs of the intent arms on the same 57,350 texts (MMLU-Pro on 11,687).
- **Statistics.**
  - Mutual kNN overlap at k ∈ {10, 50, 200, 1000}.
  - AMI between spherical k-means partitions at k ∈ {2, 4, 8, 16, 32, 64, 128, 256}, 5 seeds per side.
  - Debiased linear CKA.
- **Normalisation.** Each pair's curve is divided by the **q4-vs-q8 curve**, the same-model floor, so 1 means "as similar
  as a requantised copy".
- **Criteria.**
  - **SA1 (deciding).** Normalised AMI(qwen3, gemma) decreases with k: Spearman over k ≤ -0.7, with the slope's CI below 0
    over seeds.
  - **SA2.** The k at which normalised AMI drops below 0.8 (k\*) is reported per pair. It is compared with the gold coarse
    and fine class counts (MASSIVE 18 / 60; CLINC 10 / 150).
  - **SA3.** Prompt pairs (qwen3 vs qwen3_card) agree more than embedder pairs at every k (descriptive).
- **Falsifier.** SA1 fails (agreement flat or rising in k), so the record's "coarse holds, fine diverges" reconciliation has
  no label-free support. This gives GOLD-LEVEL-EMB's F-GL a label-free counterpart.
- **Cost.** CPU about 1 h. No pool read for the intent DBs.

## 3. What this scan does not show

No number here is new except the E0b geometry copied above. Second-moment descriptors (A) explain thresholds. They never show
structure, and the J certificate is blind to them by design. Every (B) test is only as fair as the moment-matched null.
Its numpy re-implementation must reproduce the Kotlin generator before any readout. Tree-likeness of a pooled embedding is not
evidence that the *construction's* tree is right; G3 tests whether there is anything to find. Embedder ranking stays the
author's (D3). The [S] and unverified citations need their pages opened before they enter the thesis.
