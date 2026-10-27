# Evaluating an induced hierarchy when ground truth is partial or absent (2026-10-04)

Literature note for the author. Zero calls. Nothing was run, built, registered or committed. Written at HEAD bd5ca001.
This note extends `2026-10-04_testing_logic_review.md` ("TLR") and does not repeat it. TLR's rows 1-14 and its tests
T1-T5 are taken as given: T1-T5 are now registered as ROUTE-SOURCE-NULL, KNN-ROUTE, KEY-INFO-V2, CERT-PLANTED and
GRANULARITY-GT. Downstream utility is covered there (T1-T3), so this note treats it only in passing.

**Citation marks.** [V] = paper opened in this pass. [S] = title, authors and venue confirmed from search listings in this
pass. "unverified" = written from memory; check it before citing.

## 0. The one fact that organises everything below

The record's site null is a parametric bootstrap of the SigClust type. Its source is `SeparationNullBySizeTest.siteNull`
(docstring at L1647ff). For each site it:
1. moment-matches a Gaussian to the site's own mean and covariance;
2. projects that Gaussian to the sphere;
3. re-runs the production `splitSingleNode` on draws from it;
4. compares the site's `dasguptaDeltaNorm` with the p95 of the draws.

The literature has known since SigClust what goes wrong with this design. If the null covariance is estimated from the
site, it contains the between-cluster axis. The null then reproduces the split, and the test loses power. That is the
record's PLAIN null: NO-CONTROL on merged pairs, p95 0.081-0.127 (CERT-PC-K2-KNOWN). If the null instead removes the cut
axis, any cut along a high-variance direction passes. That is the record's DEFLATED null: ELONGATION-CONFOUNDED, with
controls passing 5/5 (CERT-K2-DEFLATED).

SigClust's established middle path has three parts:
- estimate a **background noise** level robustly from the whole data, not from the site;
- shrink the leading eigenvalues towards that level (hard thresholding in Liu et al. 2008; likelihood-based **soft
  thresholding** in Huang et al. 2015, which fixed hard thresholding's inflated type-I error when a few eigenvalues are
  large);
- simulate the cluster index under the shrunk covariance.

The record has run neither this arm nor a selective-inference arm. A second lesson matters just as much. Clustering a
training set, filing held-out items into the clusters and then testing their mean difference is **anti-conservative**. The
hypothesis is still a function of the data (Gao, Bien, Witten 2024, Fig. 2 [V]). So "certify a site on GATE/EVAL items
filed by the tree" is not a valid repair, and no test should be registered in that form.

## 1. Methods, ranked by value to the thesis

Value means how far the result could move an SQ3 sentence (certificate, hierarchy, addresses). Every row needs zero LLM
calls. "Machine" means site-null or construction time under rule 7. "CPU" means the single-threaded lane.

| # | Method | Question it answers for this tree | Key citations | Cost | Zero-call on existing snapshots and embeddings? | Proposal |
|---|---|---|---|---|---|---|
| 1 | **Selective inference after clustering** (difference of child means, conditioned on the clustering having produced those children) and **SigClust with background noise and soft thresholding** | Is a split more than the splitter cutting one cloud? Does a third null with a background covariance have usable k = 2 sensitivity where plain (conservative) and deflated (anti-conservative) fail? | Gao, Bien, Witten, *JASA* 119:332-342 (2024) [V]: §4.1 Monte Carlo p-value for **any** clustering algorithm, §4.2 known non-spherical Σ, §4.3 plug-in σ; Chen & Witten, *JMLR* 24(152) (2023) [S]; Yun & Barber, *EJS* 17:1923-1946 (2023), unknown variance [S]; González-Delgado et al., arXiv:2310.11822, general dependence, k-means and HAC, R `PCIdep` [S]; Liu, Hayes, Nobel, Marron, *JASA* 103:1281-1293 (2008) [S]; Huang, Liu, Yuan, Marron, *JCGS* (2015), arXiv:1305.5879 [S]; review: Enjalbert Courrech, *Int. Stat. Rev.* (2025) [S] | CPU, roughly 6-12 h for the full grid; coder about 1 day | Yes. TRAIN vectors (512-d slice), CERT-PLANTED's planted grid, G12's 60 sites | **T-A SI-NULL-TRIAD** (§2) |
| 2 | **Bootstrap / transfer support per site** (phylogenetic clade support), **consensus trees**, and **tree distances** (Robinson-Foulds on cluster sets, triplet distance, information-based generalised RF) | Does a site recur when the tree is rebuilt on another TRAIN draw? Does the certificate predict recurrence? This is a label-free check of the certificate's *validity*, the counterpart of CERT-ALIGN-SIZE that does not inherit TLR issue 5. | Felsenstein 1985, *Evolution* 39:783-791 (unverified); Lemoine et al., *Nature* 556:452-456 (2018), transfer bootstrap expectation (TBE) for large trees [S]; Suzuki & Shimodaira, *Bioinformatics* 22:1540-1542 (2006), multiscale AU p-values [S]; Robinson & Foulds 1981, *Math. Biosci.* 53:131-147 (unverified); Smith, *Bioinformatics* 36:5007-5013 (2020) [S]; Critchlow, Pearl, Qian 1996, *Syst. Biol.* (unverified); Margush & McMorris 1981, majority-rule consensus (unverified) | CPU, under 1 h | Yes. The four MMLU-Pro re-draw trees (af_clean_s42, af_s137, af_s2048, af_s42_o1) with their site-null CSVs (about 270 sites, plain and deflated flags) | **T-B SITE-SUPPORT** (§2) |
| 3 | **Prediction strength / split stability against a generator reference** | Does an independent sample of a site's population reproduce its split *more than a single moment-matched cloud does*? TLR row 8 is cell-wise Jaccard across bootstrap builds; this is per split, needs no builds, and is calibrated. | Tibshirani & Walther, *JCGS* 14:511-528 (2005) [S]; Lange et al. 2004 and Hennig 2007 (TLR [S]); Ben-David, von Luxburg, Pál 2006 (TLR [S]): stability is not correctness. A unique principal axis is stable under k = 2 even for one Gaussian, so a generator reference is required. | CPU, about 2-4 h | Yes. The TRAIN and GATE halves of each site, with the splitter replica from T-A | **T-C PS-SITE** (§2) |
| 4 | **Gold-based taxonomy-induction metrics** that score the hierarchy rather than a cut: hierarchical F-measure (best node anywhere), taxonomic precision/recall over semantic cotopy, ancestor-F1 and edge-F1, cumulative Fowlkes-Mallows B_k per level | Is the tree right *somewhere* in its depth for each gold class (finer, coarser or mixed)? Does its nesting agree with the gold nesting? GR1 (best cut) and GR2 (dendrogram purity) are already registered; this adds node-level and edge-level credit. | Larsen & Aone, KDD 1999 [S]; Zhao & Karypis, *DMKD* (2005), tree FScore (unverified details); Dellschaft & Staab, ISWC 2006, LNCS 4273:228-241 [S]; Velardi, Faralli, Navigli, *Comput. Linguist.* 39(3):665-707 (2013), cumulative FM [S]; Bordea, Lefever, Buitelaar, SemEval-2016 Task 13 (TExEval-2) [S]; Mao et al., ACL 2018, ancestor-F1 [S]; Fowlkes & Mallows 1983, *JASA* 78:553-569 (unverified); Kobren et al., KDD 2017, dendrogram purity [S] | CPU, about 1 h | Yes. M-AF / C-AF, the two gold levels; MMLU-Pro AF trees against the 14 categories | **T-D HIER-F** (§2) |
| 5 | Sequential hierarchical significance (test down the tree, stop at the first non-significant node, FWER control) | Is the record's hierarchical BH over nested sites the right multiplicity frame? | Kimes, Liu, Hayes, Marron, *Biometrics* 73:811-821 (2017), `sigclust2` [S]; Meinshausen, *Biometrika* 95:265-278 (2008) [S]; Yekutieli 2008, hierarchical FDR (unverified) | trivial on T-A's p-values | Yes | Add an SHC-style FWER column to T-A; descriptive |
| 6 | Objective-based internal quality (Dasgupta cost; admissible costs; Moseley-Wang revenue) at the tree level, against average-link and matched-shape random trees | Is the whole tree a good hierarchy of the similarity graph, beyond the per-split gain? | Dasgupta, STOC 2016:118-127 [S]; Cohen-Addad, Kanade, Mallmann-Trenn, Mathieu, *J. ACM* 66(4):26 (2019) [S] | CPU minutes | Yes | Low value: the construction already optimises a Dasgupta-type statistic, so this is circular. Descriptive only, beside GR2. |
| 7 | MDL / Bayesian evidence of the hierarchy (BHC, Bayesian rose trees, nested SBM, hierarchical map equation) | Is the tree a shorter code than flat k at the same fit? | Heller & Ghahramani 2005 (TLR [S]); Blundell, Teh, Heller, UAI 2010 (unverified); Peixoto, *PRX* 4:011047 (2014) (unverified); Rosvall & Bergstrom, *PLoS ONE* 2011 (unverified) | CPU, coder 1-2 days | Partly. The likelihood family must be vMF or Gaussian. | **Do not register.** It is the same likelihood-ratio family as MIX-LRT-SITE (GMM LR/BIC half CLOSED NEGATIVE), and FLAT-MIX-MMLU already answers the flat-vs-tree code question. |
| 8 | Tree edit distance between trees | How far apart are two builds? | Zhang & Shasha 1989, *SIAM J. Comput.* 18:1245-1262 (unverified) | CPU | Yes | Dominated by #2. Internal nodes are unlabelled, so edit costs are arbitrary; matching on cluster sets (RF/TBE) is the standard choice. |
| 9 | Dip test on the projection onto the child-centroid direction | Is the split bimodal along its own axis? | Hartigan & Hartigan 1985 (unverified); Kalogeratos & Likas, NIPS 2012, dip-means (unverified) | CPU | Yes | The axis is data-chosen, so a naive dip p-value double-dips. Run it only through T-A's generators. The dip half of L6 is OPEN; this is its valid form. |
| 10 | Data thinning / data fission (split each observation, not the item set) | Is there a valid "cluster on one part, test on the other" route? | Neufeld, Dharamshi, Gao, Witten, *JMLR* 25(57) (2024) [S]; Leiner et al., data fission, *JASA* (unverified) | CPU | Formally needs a known Gaussian Σ. Embeddings have neither a known Σ nor Gaussian noise. | Note only. It is the only *valid* train/test analogue, and its assumptions fail here. |

**Downstream utility** (Kosmopoulos et al. 2015 and von Luxburg et al. 2012, both TLR [S]) remains the deciding criterion
for "good cells". It is covered by ROUTE-SOURCE-NULL, KNN-ROUTE and KEY-INFO-V2. The methods above answer a narrower
question: is the *structure* real and reproducible? They cannot license "useful".

## 2. Top four tests, specified for registration

Shared settings:
- **Embeddings:** qwen3, 512-d slice of record, RAW.
- **Data:** TRAIN-side items only. No EVAL item enters a fit, and no item is filed and then tested (§0).
- **Seeds:** fixed now. Seed base 20261004; every random draw is `base + index`.
- **Scratch and outputs:** under `E:/TaxoArena_tmp` via `scratch_dir.py`; outputs pinned by sha256 and never committed.
- **Compute:** CPU lane single-threaded; no construction.
- **Splitter replica:** a numpy replica of the splitter at the site's k on the splitter's 128-d PCA projection, called the
  "proxy". It must reproduce the persisted child memberships of G12's 60 sites at ≥ 99% item agreement, or the run
  refuses. Disclose that the PCA basis is held fixed (conditioning on it is an approximation).

### T-A SI-NULL-TRIAD (rank 1): a third and fourth null for the k = 2 sensitivity question

- **Question.** Does a null whose covariance is not taken from the site certify planted 2-way structure without
  certifying structureless clouds?
- **Arms.**
  - **P**: the plain site null of record. Its certification counts are read from CERT-PLANTED's output when that run
    exists. If T-A runs first, P is recomputed on the same grid by the proxy and flagged.
  - **S**: SigClust-soft. Background σ²_b = MAD² of all centred TRAIN coordinates of the *whole corpus*, then soft
    thresholding of the site's eigenvalues (Huang et al. 2015 algorithm). Statistic: the 2-means cluster index of the proxy
    at k = 2. 1,000 simulations per site.
  - **G**: Gao-type selective p-value by importance-sampling Monte Carlo (§4.1), with the proxy as the clustering
    function, N = 2,000. Two covariance variants: Σ = σ²_b I, and Σ = the S arm's thresholded matrix. For k > 2 children,
    every sibling pair is tested and combined by Holm. The pair choice is not data-driven, so no extra conditioning is
    needed.
- **Grids.**
  - (i) **SIZE:** 50 draws from each site's own moment-matched generator, at n 486 and 441, three anchors (CERT-PLANTED's
    math, physics, economics).
  - (ii) **POWER:** CERT-PLANTED's planted grid verbatim (δ ∈ {0, 0.5, 1, 2}, 5 subsamples, random u and assignment).
- **Criteria.**
  - SA1, size: an arm is SIZE-OK iff its rejection rate on grid (i) is ≤ 0.10 at α 0.05 (upper 95% Clopper-Pearson
    ≤ 0.15).
  - SA2, deciding: an arm is K2-SENSITIVE iff it is SIZE-OK AND δ = 2 certifies ≥ 4 of 5 in ≥ 2 of 3 anchors.
  - Readings:
    - THIRD-NULL-WORKS iff S or G is K2-SENSITIVE while P is not.
    - NO-NULL-WORKS iff no SIZE-OK arm reaches δ = 2.
    - Otherwise MIXED.
- **Descriptive only:** the arms' verdicts on G12's 60 real sites, never a certificate of record. Real sites carry
  non-Gaussian texture, under which G's null of equal means is false for almost any cut. Report each arm's δ\*.
- **Falsifier** of "a background-covariance null resolves k = 2 sensitivity": NO-NULL-WORKS, or every sensitive arm fails
  SA1.
- **Support.** With 5 binary outcomes per anchor and 50 per size cell, SA1's upper bound is ±0.10. Register SA2 as a
  classification (SCOREABLE).
- **Caveat to print.** G's p-value is valid for the *proxy's* selection event, not the engine's z-gate plus epoch
  schedule. If the proxy fails the 99% identity check, G is NOT EVALUABLE.

### T-B SITE-SUPPORT (rank 2): do certified sites recur across re-draws?

- **Object.**
  - The four AF MMLU-Pro re-draw trees and their persisted site-null CSVs.
  - The common item set C is the intersection of the four TRAIN sides (expected roughly 2,000-2,500 items; print it). Each
    site is restricted to C.
  - A site is skipped if it has fewer than 20 items in C, or if its smaller side would have fewer than 20.
- **Statistic.** For a site s of tree A (item set S ⊂ C, p = min(|S|, |C| - |S|)), the transfer index δ(s, B) is
  min over nodes b of B of |S Δ b|. TBE(s) = mean over the other three trees of max(0, 1 - δ/(p - 1)). The binary
  Felsenstein support (exact recurrence) is printed beside it.
- **Readings.**
  - SB1, deciding: G = mean TBE(certified at plain p95) - mean TBE(uncertified), in depth × size strata (CERT-ALIGN-SIZE's
    strata). One-sided within-stratum permutation, 10,000 draws. SUPPORT-TRACKS-CERT iff G > 0 AND p ≤ 0.05; otherwise
    NOT-SHOWN. Repeat for the deflated flag (SB1d, descriptive).
  - SB2, deciding: real-site TBE against random subsets of C of the same size, 200 per site (Lemoine's random
    expectation). The median real-site TBE must be above the random p97.5.
  - Descriptive: normalised RF and sampled triplet distance (10⁵ triplets) between each pair of trees, against spherical
    k-means at matched k, seeds 0-4, cut into an average-link hierarchy; a majority-rule consensus of the four trees; and
    the overlap of that consensus with the certified trunks.
- **Falsifier** of "certification marks reproducible structure": SB1 NOT-SHOWN with G ≤ 0.
- **Scope words.** Three of the four draws are id-disjoint only. This is a structural readout with no EVAL claim. The
  pools are opened read-only.

### T-C PS-SITE (rank 3): split prediction strength against the generator

- For each site with ≥ 2 × 55 items in both halves, split the site's TRAIN items into two random halves, 20 repeats.
- Run the proxy on each half and compute prediction strength: the minimum over clusters of the co-assignment rate of
  half-B pairs under half-A's centroids (Tibshirani & Walther).
- Reference: PS from 100 draws of the site's moment-matched generator. Report PS(site) - p95 of PS(generator).
- Readings:
  - PC1: the certified-vs-uncertified difference in that margin, under the T-B strata and permutation. Deciding.
  - PC2, descriptive: the rank correlation between the margin and T-B's TBE.
- PC1 is SCOREABLE only if the generator margin is computable (≥ 20 non-degenerate generator draws per site, the record's
  usability floor).
- Falsifier of the stability reading: PC1 NOT-SHOWN. Report it beside SB1, never alone, because stability is not
  correctness.

### T-D HIER-F (rank 4): node-level and edge-level gold credit (an addendum beside GRANULARITY-GT)

- **Objects.** M-AF (84 leaves) and C-AF (139) on their EVAL sides, scored against both gold levels. Also the four MMLU-Pro
  AF re-draw trees, scored on their TRAIN sides against the 14 categories (a recovery check, TLR §1).
- **Metrics.**
  - Hierarchical F: Σ_c (n_c/n) max over nodes F(c, node), where the max ranges over every node, not a cut.
  - Taxonomic P/R/F: each item's gold path against its leaf's ancestor path; Dellschaft-Staab cotopy on item ancestor
    sets.
  - Ancestor-F1 on gold-class pairs: is the LCA depth in the tree consistent with the gold nesting?
  - The cumulative Fowlkes-Mallows curve B_k against the gold intent partition, over k from 2 to the leaf count.
- **Arms.** Average-link and bisecting spherical k-means hierarchies on the same TRAIN (5 seeds), and 200 random trees of
  matched shape (GRANULARITY-GT's arms, reused).
- **Readings.**
  - HF1, deciding per corpus: tree hierarchical F minus average-link, scored on the interval and against the bisecting seed
    spread.
  - HF2: tree hierarchical F above the random p97.5.
- **Falsifier** of "the tree carries the gold hierarchy beyond its leaves": HF2 fails on both corpora.
- **Note.** HF credits a tree that is finer than gold, coarser than gold, or both, at the node where each class sits.
  That repairs TLR §1 issue 3 without a single-cut assumption.

## 3. What the literature says about the certificate, in one paragraph

No published significance method escapes the choice of null covariance. SigClust's history is the plain-vs-deflated
dilemma written down. Selective inference corrects for the *selection* of the clusters, but its null (equal child means
under a Gaussian with known Σ) is false for any skewed or elongated unimodal cloud. On real embeddings it would certify
texture, as DEFLATED does. Its gains are exactness under its model and a principled conditioning. It does not settle which
Σ is right. The literature's practical answer is a **background-noise covariance** (SigClust-soft), plus **support values
across rebuilds** as an orthogonal, model-free check (TBE, pvclust). T-A and T-B are those two answers. If both fail, the
honest sentence is "the certificate's k = 2 sensitivity cannot be established with Gaussian-reference nulls on these
embeddings", which is a method limitation the thesis can state with citations.

## 4. Limits of this note

- No number here is new.
- G's validity rests on the proxy matching the engine.
- T-B's common set shrinks with every added re-draw.
- "Unverified" citations need their pages opened.
- Costs are estimates for the cost-estimator to replace.
- The author decides registration order. T-A and T-B are independent and need no machine time; CERT-PLANTED (machine)
  feeds T-A's P arm.
