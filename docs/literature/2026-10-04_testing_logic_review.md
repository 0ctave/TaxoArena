# Testing-logic review: is ground-truth agreement the right test for the tree? (2026-10-04)

Methodological review for the author. Zero calls; nothing run, built, registered or committed. As of HEAD feac5b3d.
Sources: `docs/agents/KNOWLEDGE.md`, memo v3 (`docs/agents/plans/2026-10-03_reframing_memo_v3.md`), the two literature notes
of 2026-10-02 / 10-03, and the results JSONs named in the brief (numbers quoted from `numbers_of_record`). Filing code read:
`tools/analysis/deep_split_compare.py` docstring (P_fl definition), the RP13 instrument (prog L22633).

**Citation marks.** [V] = verified in pass 2 (abstract page opened). [S] = confirmed in this pass from search listings only
(title, authors, venue agree; abstract not opened). "unverified" = from memory, check before citing.

**Label-status legend.** Memo v3's four tags, plus three this review needs: **[SC]** source-conditioned (the benchmark of
origin is used at construction or filing), **[TS]** task-supervised (uses TRAIN model-correctness), **[OR]** oracle (uses EVAL
outcomes; an upper bound only). Comparisons across tags are ceilings or floors, never method rankings (memory
anchored-tree-comparisons).

---

## 1. Verdict on ground-truth comparison

**Verdict: GT agreement is a valid *recovery check* and an invalid *validity test* for this tree.** It can show that the
embedding geometry carries a declared distinction, and on known-answer corpora that the construction recovers designed
structure. It cannot show that the cells are good for routing, evaluation or organisation. The thesis's own purposes put the
deciding criterion on task-grounded metrics, scored against matched null partitions. The record has these on MMLU-Pro
(F6 key information, the site-value gate) but not on the content-closed v2 union, where the SQ1 claims live.

What the GT metrics in use measure:

- **P_fl** (filing precision; G13, DSC, AK, FITSET, OL1, OS1). A cell is named by the TRAIN-majority declared class, and an
  EVAL item scores 1 iff its class equals that name. This is the accuracy of a "cluster, then label by majority"
  nearest-centroid classifier. Four properties follow:
  - It is **asymmetric in granularity**. A tree finer than the labels is never penalised: each sub-cell inherits the
    majority name. A tree coarser than the labels is penalised for every merged class. So "right at a different
    granularity" counts as right only when the tree is finer. A coarser true structure is scored as error.
  - It **grows with k** (purity bias; Amigó et al. 2009, *Inf. Retrieval* 12:461-486 [S]). Matched k neutralises this, and
    the record matches k everywhere. That is correct and should be stated as the reason.
  - It **ignores the hierarchy above the leaves**. Only T-C2 (dendrogram purity, MASSIVE) and T-C4 (Mantel) touch it.
  - It **ignores which errors are near misses**. Filing a "physics" item into a "chemistry" cell costs the same as filing
    it into "law".
- **NMI_fine** (T-C1). Symmetric, but not chance-corrected. At matched k this is acceptable. AMI (Vinh, Epps, Bailey 2010,
  *JMLR* 11:2837-2854 [S]) is the standard form and costs nothing extra.
- **Prototypes / KC** (G13, T-C1b, DSC C-DB). These are [LC] arms scored against the labels they were fitted on. They are
  ceilings, and the record already reads them that way.
- **OOS AUROC** (OOS-BASELINES, OT1). Here the "label" is CLINC's curated out-of-scope set: a designed artefact with
  documented mislabels. It is fine as a recovery check, but says nothing about traffic.

The five issues the author asked about:

1. **Circularity with anchored trees.** On [AN] trees depth-2 is the declared class, so P_fl is largely NCC accuracy by
   construction. G14 (+2.62pp) equalling declared (+2.67pp) is close to an identity, not a finding. **FITSET-FAITHFUL is
   circular in the same way**: it re-estimates leaf means on declared classes and scores agreement with those classes, so
   a gain on MMLU-Pro (FF1 +0.0256) is the expected direction under the metric and carries no information about cell
   quality. The informative half is the CLINC loss (FI1 -0.0264), where label fitting *lowered* label agreement. DSC C-DB
   (+0.0349) has the same structure.
2. **A label-status inconsistency in memo v3 (new).** AF-U is a *federated* build: one anchor-free tree per source on that
   source's TRAIN, grafted under a union root. IFEVAL enters as one cell, its source (prog L22633; L23660ff). The benchmark
   of origin is therefore used at construction. By the memo's own legend ("[LC] ... or source-conditioned") AF-U is
   [SC], the same status as K_0. Yet the memo tags AF-U [LF] and K_0 [LC]. Two consequences:
   - U1's "+1.52pp from a label-free tree" is not established as label-free. No source-only policy arm exists on v2, so
     the share of the gain that source identity alone buys is unknown. On the older multi-corpus union, MC-ROUTER found
     routing by source recovered +4.0 of the +5.0pp that domain routing did (different split; history, not evidence).
   - AF-U vs K_0 (U2, ESCALATION-RC, COVERAGE-AUDIT) is like with like, both [SC]. It is not "cross".

   The intent-corpus trees (M-AF, C-AF) are single-corpus and genuinely [LF].
3. **Granularity mismatch.** The intent corpora have two gold levels (MASSIVE scenario / intent; CLINC domain / intent).
   T-C1 scores only the fine level, at the tree's leaf count. A tree whose *internal* cut matches the coarse gold has no
   credit anywhere in the record. The tree's distinctive object is the hierarchy, and the GT tests mostly flatten it away.
4. **Label noise.** MMLU carries an estimated 6.49% erroneous items (Gema et al., "Are We Done with MMLU?", NAACL 2025,
   arXiv:2406.04127 [S]). Benchmark test sets average 3.3% (Northcutt, Athalye, Mueller, NeurIPS D&B 2021 [S]).
   - In *paired* contrasts, noise common to both arms attenuates differences; it does not bias them. Most record contrasts
     are 0.002-0.04, so a ceiling below 1 matters little.
   - The danger is noise **correlated with geometry**. Ambiguous or mislabelled items sit at boundaries, and boundaries are
     exactly where trees and k-means differ. No record test can separate "the tree is wrong" from "the label is wrong" at a
     boundary item. FF2's UNDETERMINED correlation is a symptom of this.
5. **Multiple valid taxonomies and benchmark labels as artefacts.** Several legitimate clusterings exist on the same data
   (Hennig 2015, *Pattern Recognition Letters* 64:53-62 [S]). Clustering should be judged by its end use (von Luxburg,
   Williamson, Guyon 2012, PMLR 27:65-79 [S]). Class labels are one such clustering among several, not the truth (Färber
   et al., MultiClust@KDD 2010 [S]). The record shows this concretely:
   - MMLU-Pro's 14 categories are geometric (CERT-POSITIVE-CONTROL 0.1078 vs null max 0.0424).
   - Its source-family split is not (CERT-PC-K2 statistic below its null minimum).
   - The union's "declared" (source, domain) classes partly encode *format*. BBH's 36 AF-U cells follow its task templates,
     and 5 of 7 CELL-FLIPS flips are BBH template cells.

   So agreeing with declared labels partly rewards recovering templates. A tree that ignored templates for capability
   structure would score lower and could still be the better evaluation instrument.

**What GT agreement licenses.** (a) "The geometry carries distinction X" (necessary for a tree to stand in for labels where
labels are missing). (b) "The construction recovers designed structure on known-answer corpora." (c) Like-with-like method
contrasts *on the recovery task* (T-C1, AK).

**What it cannot license.** "Better cells for routing / evaluation", "a right taxonomy", any claim about the hierarchy above
the leaves, and any claim about structure the labels do not encode. The newly registered CERT-ALIGN-SIZE is a GT test of the
certificate (alignment with declared categories). It inherits issue 5: a certified site that aligns with templates rather
than categories reads as misaligned.

---

## 2. Missing metrics and comparators, ranked

Value = how much the result could move a thesis sentence. Cost is CPU / machine / agent time; every row is zero-call.

| # | Metric or comparator | Question it answers | Fits the data at zero calls? | Cost | Record items it tests | Closest prior work |
|---|---|---|---|---|---|---|
| 1 | **Source-only policy + random-within-source cells at AF-U's per-source size profile** [SC] | How much of U1's +1.52pp is beyond source identity? | Yes: union EVAL keyed correctness, 18 models, G14 reader | CPU minutes; coder ~3 h | U1, memo §1 "[LF] +1.52pp", change 4 | MC-ROUTER (history); random-grouping null as in STABLE-CELL-SET |
| 2 | **Cell-free kNN routing** (k fixed pre-data) and a **correctness-pattern partition** [TS] ceiling | Do cells add anything over raw neighbourhoods? What is the best any embedding partition could do? | Yes: TRAIN 12,334 keyed vectors, 256-d slice | CPU < 1 h; coder ~3 h | U1, U3b, change 4, framing "cell-conditional" | Huot et al. 2026 kNN routers [V]; LLMRouterBench [V]; Avengers [V]; EmbedLLM (Zhuang et al., arXiv:2410.02223) [S]; tinyBenchmarks (Polo et al., arXiv:2402.14992; clusters items on IRT correctness embeddings) [S] |
| 3 | **Key information on v2** (LOO Brier resolution of cell-conditional per-model correctness; Murphy reliability term) | Does knowing the cell predict *which models* are right, across all 18? Are TRAIN cell accuracies calibrated on EVAL? | Yes: F6 machinery exists (`free_tests_f4_f7.loo_imp`) | CPU; coder ~2-3 h | U2 (UNDETERMINED by routing argmax), CELL-FLIPS, SQ1 framing | Murphy 1973, *J. Appl. Meteor.* 12:595-600 [S]; record F6 / site-value gate |
| 4 | **Planted-structure certificate control** (synthetic 2-way shift of known size inside an anchor; power curve over δ) | k = 2 sensitivity of the plain site null, free of label artefacts | Yes: TRAIN vectors; site null is machine time (rule 7) | ~8 site nulls, ~2-4 h machine | change 10, CERT-PC-K2 / K2-KNOWN / K2-DEFLATED (all non-outcomes) | SigClust (Huang et al. 2015) [V]; Domino's planted-slice evaluation (Eyuboglu et al., ICLR 2022, arXiv:2203.14960) [S] |
| 5 | **Granularity-aware GT**: level-wise AMI, best tree cut vs each gold level, homogeneity / completeness; random tree at matched shape; average-link and bisecting k-means hierarchies | Is the tree right at a different granularity? Is the hierarchy (not only the leaves) better than generic ones? | Yes: MASSIVE / CLINC gold levels, M-AF / C-AF snapshots | CPU; coder ~3 h | T-C1, T-C2, P3, D6 bullet 2 | Vinh et al. 2010 [S]; dendrogram purity (Heller & Ghahramani, ICML 2005) [S]; Fowlkes & Mallows 1983 (unverified) |
| 6 | **Profile-Mantel**: tree LCA distance vs distance between cells' 18-model accuracy profiles, against random trees at matched shape | Does the hierarchy organise model behaviour (the only route to a roll-up-reporting claim)? | Yes: AF-U cells, union keyed matrix | CPU; ~2 h | P3, change "roll-up", CELL-FLIPS tau | cophenetic correlation (Sokal & Rohlf 1962, *Taxon* 11:33-40) [S]; T-C4 machinery |
| 7 | **Oracle headroom**: per-question oracle and EVAL cell-oracle [OR]; co-failure ceiling | What share of the reachable gain do cells realise? | Yes | CPU minutes | U1, C1 framing | Shihab et al. 2026 [V]; Chen 2026 co-failure [V]; ROUTER-REGRET-MMLU (history) |
| 8 | **Cell-wise bootstrap Jaccard stability** (TRAIN resampling) | Are individual cells reproducible beyond fixed-split determinism? | k-means cheap; tree needs one build per resample | tree: machine, 10+ builds; k-means: CPU | P1 "stable addresses" | Hennig 2007, *CSDA* 52:258-271 [S]; Lange et al. 2004, *Neural Comput.* 16:1299-1323 [S]; caveat: Ben-David, von Luxburg, Pál 2006, COLT [S] (stability ≠ correctness) |
| 9 | **Risk-coverage curve / AURC** for the routed policy under margin abstention | Is there any coverage point where abstention pays? | Yes (ESCALATION-RC gave one point) | CPU minutes | change 9 | Jung et al. 2024 [V] |
| 10 | **Hierarchical (LCA) F1 of filing** | Are filing errors near misses in the gold hierarchy? | Yes, on intent corpora | CPU | T-C1b reading | Kosmopoulos et al. 2015, *DMKD* 29:820-865 [S] |
| 11 | HDBSCAN / GMM / BERTopic cells | Algorithm sensitivity | Yes | CPU | N1 | Campello et al. 2013, PAKDD [S]; BERTopic [S]; Avengers says the algorithm barely matters [V] |
| 12 | Silhouette per level, compactness | Internal geometry | Yes (SphericalSilhouette exists; run-to-run drift known) | trivial | none decisive | biased toward k-means' own objective; low value |
| 13 | Semantic coherence (c-TF-IDF distinctiveness, NPMI of top terms) | Are cells nameable? | Yes, LLM-free | CPU | I1 only | Chang et al. 2009, NIPS [S] (likelihood ≠ interpretability) |
| 14 | Label propagation | Semi-supervised ceiling | Yes, but [LC] | CPU | none new | Zhou et al. 2004 (unverified) |

Of the author's list, two are low priority. **Topic models** are low because Avengers already shows insensitivity to the
partition algorithm [V]. **Difficulty partitions** matter only in the [TS] form of row 2: cells built from correctness
patterns cannot file an EVAL item without its outcomes, unless items are filed through embedding neighbours.

**Most likely to change conclusions: rows 1, 2 and 4.**
- Row 1 can move SQ1's only label-free routing claim into "source does it".
- Row 2 can make cells unnecessary for routing, which reframes changes 1 and 4 and puts the framework's value in reporting
  and filing discipline only.
- Row 4 is the only route out of three consecutive non-outcomes on certificate power.

Rows 3, 5 and 6 are where a positive tree result could still appear. They are the fair tests of what the tree is for.

---

## 3. Tests specified for pre-registration

All five share these settings unless stated otherwise:
- **Objects.** Content-closed v2 union split (draw 5a3e756, pool `pv2_1575de61bb20e977`, B0-2 pool check); EVAL 5,907
  items / 5,404 components (routing) or 6,139 / 5,628 (filing); 18-model keyed correctness; AF-U as built
  (`experiment_results/archv2/union_af_route/inputs/`).
- **Statistics.** Two-stage bootstrap over CK-CLOSE components, B 2,000. The Support line is computed before data. Seeds
  0-4 for every seeded arm.
- **Policy.** Every policy is fitted on TRAIN by G14's reader with backoff unchanged.
- **Identity precondition.** The declared arm reproduces C1 +2.67pp [+1.46, +3.89] and AF-U reproduces G_AF +1.52pp, else
  the run refuses.

**T1 ROUTE-SOURCE-NULL** (row 1).
- Arms:
  - SRC: the 6-cell policy (best model per source).
  - RWS_r: within each source, a random partition of TRAIN items at AF-U's per-source leaf count *and* size profile;
    EVAL is filed by source, then to a random cell drawn with the TRAIN size weights. 200 draws.
  - AF-U.
- Criterion: D_S = G_AF - G_SRC, with the null band = the central 95% of G_RWS - G_SRC. Readings:
  - ABOVE-SOURCE iff the 95% interval of D_S is wholly > 0 AND G_AF > the 97.5th percentile of G_RWS.
  - SOURCE-EXPLAINED iff G_AF lies inside the RWS band AND D_S's interval contains 0.
  - Otherwise UNDETERMINED.
- Also report G_SRC - G_best and G_declared - G_SRC, descriptive.
- Falsifier of the memo's sentence: SOURCE-EXPLAINED means "+1.52pp" is rewritten as source identity, and AF-U is tagged
  [SC] everywhere.
- Support note: D_S's SE should be about 0.4-0.5pp (U2's interval). Register the MDE first. If it is about 1.2pp, a small
  D_S is DESCRIPTIVE-ONLY.

**T2 KNN-ROUTE** (row 2).
- Arms:
  - KNN_k: for each EVAL item, the k nearest TRAIN items in AF-U's 256-d slice. Pick the model with the highest mean keyed
    accuracy among them, backing off to the best single when the leader's margin is below one SE. k ∈ {25, 50, 100}, fixed
    now, with k = 50 deciding.
  - AF-U.
  - K_0.
  - TS: a ceiling. TRAIN items are clustered by their 18-model correctness vectors (spherical k-means at AF-U's k), and EVAL
    items are filed by the majority TS cell of their k = 50 TRAIN neighbours.
- Like with like: KNN uses no source information. This is [LF] against AF-U [SC], so KNN vs AF-U is reported as a floor
  only. KNN restricted to the item's own source ([SC]) decides against AF-U.
- Criterion: D_N = G_KNN-SC - G_AF. Readings:
  - CELLS-ADD iff the interval is wholly < 0 AND |D_N| > spread_K.
  - CELLS-UNNEEDED iff a TOST at ±0.5pp is inside, or the interval is wholly > 0.
  - Otherwise UNDETERMINED.
- TS - G_declared is reported as the [TS] ceiling, never a ranking.
- Falsifier of framework change 4's "route on tree or k-means cells": CELLS-UNNEEDED.

**T3 KEY-INFO-V2** (row 3).
- Metric: the key-only LOO Brier gain over the marginal, per item, summed over the 18 models (F6's estimator, `loo_imp`),
  with Murphy's resolution and reliability terms printed beside.
- Arms: AF-U, K_0 (s0-4), SRC, RWS (200 draws), declared.
- Criteria:
  - KI1: D = KI(AF-U) - KI(K_0) against spread_K, scored like G13 (interval AND point).
  - KI2: KI(AF-U) above the RWS p97.5. This is the only like-with-like test of task information *beyond source*.
- Falsifier: KI2 fails, so AF-U carries no correctness information beyond random within-source cells, and "cell-conditional
  evaluation" on [LF]/[SC] cells is unsupported beyond source.
- Why: argmax routing discards 17 of 18 models' signal. U2 was UNDETERMINED at MDE80 of about 2pp, and Brier resolution
  is far more powerful on the same items.

**T4 CERT-PLANTED** (row 4).
- Object: the TRAIN items of three B0 MMLU-Pro anchors (math, physics, economics: CERT-PC-K2's), subsampled to n 486 and
  n 441.
- Plant: draw a random unit direction u in the 512-d slice (seeded, fixed now) and a random half-split. Shift each half by
  ±δ·s·u, where s is the item cloud's SD along u. Renormalise.
- Grid: δ ∈ {0, 0.5, 1, 2} (δ = 0 is the size check). 5 subsamples per cell.
- Instrument: the plain J site null of record, 300 reps.
- Criterion: the power curve, i.e. the share certified per δ.
  - SENSITIVE-AT-δ\* is the smallest δ with ≥ 4 of 5 certified.
  - SIZE-OK iff δ = 0 certifies ≤ 1 of 15.
- Falsifier: δ = 2 certifies ≤ 1 of 5, giving "insensitive to strong 2-way structure at depth-1 sizes".
- Report δ\* against the separation statistics of G12's 14 TOP splits, converted to the same scale. This is what turns
  "0 of 60" into a sentence.
- Random u and random assignment avoid both CERT-PC-K2's label-artefact problem and CERT-K2-DEFLATED's elongation
  confound.
- Machine time under rule 7, one site null at a time. Back up first.

**T5 GRANULARITY-GT** (row 5, with row 6 as an optional descriptive arm).
- Object: the MASSIVE (M-AF, 84 leaves) and CLINC (C-AF, 139 leaves) trees as built; EVAL 4,946 / 6,672; both gold levels.
- Arms (all [LF]): the tree's cuts at every depth; an average-link hierarchy and a bisecting spherical k-means hierarchy on
  the same TRAIN; 200 random binary trees with the tree's leaf set, shape preserved by randomly permuting leaves (matched
  shape).
- Metrics: AMI of each cut to each gold level; best-cut AMI per level; homogeneity / completeness at the leaf level;
  dendrogram purity.
- Criteria:
  - GR1: best-cut AMI(tree, coarse gold) - best-cut AMI(average-link, coarse gold), interval AND spread over the five
    bisecting seeds.
  - GR2: DP(tree) above the random-tree p97.5.
- Falsifier of P3 / D6's hierarchy wording: GR2 fails (the hierarchy is no better than a random arrangement of the same
  leaves). GR1 decides whether "right at a different granularity" can be written.

---

## 4. Claims in memo v3 this review weakens

1. **§1 and §2 SQ1: "an [LF] anchor-free tree gives a thin +1.52pp".** AF-U is federated per source, so it is [SC] by the
   memo's own legend. The sentence needs "[SC]" and stays open until T1. ESCALATION-RC's "K_0 is [LC], cross" should read
   "like with like ([SC] both)".
2. **§3 change 4, "[LF] tree or k-means cells only where [declarations] do not [exist]".** No [LF] cell set was tested on
   the union. Both arms used source declarations. The evidence for routing on genuinely label-free cells is zero.
3. **§3 change 11 / FF1, "refit helps on MMLU-Pro".** The metric rewards label fitting by construction. FF1 is a property
   of P_fl, not evidence of better cells. Keep only the CLINC loss as informative, and say why.
4. **D6 bullet "an anchored tree routes as declared labels do".** This is near-tautological: depth-2 is the declared
   class. Add "by construction" or drop it from the evidence list.
5. **§2 SQ3 online (OL1 -3.9pp, OS1 -3.3pp).** These are P_fl losses against batch-named declared classes. "Online filing
   trails a rebuild" is a label-agreement statement, and its routing or decision consequence is unmeasured. The memo should
   not read them as a routing cost.
6. **D6 "On MASSIVE and CLINC a label-free tree partitions equivalently to k-means".** True at the fine gold level and at
   leaf k only. It says nothing about the hierarchy (T-C2 is the only hierarchy readout: one corpus, interval only). Add
   "at the leaf level, against fine gold".
7. **Change 10 / certificate.** The three k = 2 controls all used declared labels as "known structure". Their failures
   are as consistent with "declared sub-structure is not geometric" as with low power. Write k = 2 sensitivity as
   untestable with declared-label controls until a planted control (T4) runs.

## 5. What this review does not show

No number here is new. Every proposed test can come out in the tree's favour. The [SC] reading of AF-U is a status
correction, not a measured loss. Whether source alone carries the +1.52pp is unknown until T1. Citations marked [S] need
their abstract pages opened before they enter the thesis.
