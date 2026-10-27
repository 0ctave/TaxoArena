# Response structure as a second ground truth: the model × item matrix (2026-10-04)

Literature note for the author. Zero LLM or judge calls. Nothing was registered, built or committed, and no code or record
file was changed. As of HEAD bd5ca001. It builds on `docs/agents/KNOWLEDGE.md`, the testing-logic review (bd5ca001), memo v3,
related work pass 2, and the results JSONs CELL-FLIPS, UNION-AF-ROUTE and V2-DECLARED-CELLS. It also reads the registrations of
KNN-ROUTE (prog L24278-L24289) and KEY-INFO-V2 (L24291-L24302), so that no test proposed here duplicates them.

**Citation marks.** [V] means the abstract page was opened in this pass. [S] means the title, authors and venue were confirmed
from search listings only. "unverified" means the item is from memory and must be checked before it is cited.

**Why this angle.** The testing-logic review found that declared-label agreement can serve as a recovery check but not as a
validity test. The model × item correctness matrix gives a second ground truth that depends on neither text embeddings nor
declared labels. Two items are "the same kind" if the same models get them right. This is the construct a per-cell evaluation
needs: cells should group items on which the roster behaves alike.

## 0. Feasibility descriptives (not of record)

This is a read-only `immutable=1` pass over `multicorpus_cache_v1.db`, which holds 21,606 items × 18 models with no missing
cells (`eval_results`, with `eval_results_mathfix` overriding MATH). It covers all items, across both split sides. It computed
no cell, tree or label quantity, so no registered statistic was previewed. Items on which all 18 models agree are 11.5% of the
union, ranging from 4.3% (GPQA) to 24.3% (MuSR). An item's 18-bit pattern is therefore informative but noisy.

Raw PCA on centred items puts 40.8% of the variance on PC1 (a general factor). The remaining components are 6.6%, 5.3% and
4.7%. **Rasch-residual parallel analysis** compares a JML 1PL fit with ten parametric bootstrap replicates from that fit.
- On the union, the top 5 residual eigenvalues are 0.136 / 0.093 / 0.086 / 0.067 / 0.064, against a null p95 of about 0.062.
- In every source, at least 2 residual dimensions exceed the null: IFEval 2, BBH 4, the other sources ≥ 5.

Caveat: a 1PL fit leaves 2PL discrimination and the MC guessing floor (GPQA 1/4, MMLU-Pro 1/10) in the residual, and both
inflate these counts. A 2PL or 3PL null is needed before any dimension count is quoted. Even so, the matrix plausibly has
structure beyond "difficulty × general ability" in every source, so a second ground truth is not trivially one-dimensional.

**One structural point, at zero cost.** Every unidimensional IRT model (1PL, 2PL or 3PL) makes P(correct) monotone in a
single θ. Every item, and so every cell, then orders the models the same way. **A cell-level ranking flip is impossible under
any 1-D IRT model.** The 7 BH-surviving CELL-FLIPS cells are therefore direct evidence of multidimensional response structure,
or of a 1-D misfit from guessing or ceiling effects, provided they survive a 3PL check. This gives CELL-FLIPS a psychometric
reading it currently lacks. It also makes "do cells carry interaction structure, not just difficulty?" the right question.

## 1. Literature by strand

**(a) IRT for LLM benchmarks.**
- Rodriguez et al., ACL 2021 [S], build 2PL/IRT leaderboards. Vania et al., ACL 2021 [S], compare test sets by IRT
  discrimination.
- tinyBenchmarks (Polo et al., ICML 2024, arXiv:2402.14992 [S]) uses IRT item embeddings, clusters them for anchor items,
  and reaches about 2% error with 100 MMLU items.
- Truong et al., ICML 2025, arXiv:2503.13335 [S], predict IRT difficulty from question text (amortised calibration).
- Fluid Benchmarking (Hofmann et al., COLM 2025, arXiv:2509.11106 [S]) does adaptive testing on IRT.
- PSN-IRT (Zhou et al., AAAI 2026, arXiv:2505.15055 [V]) audits 41,871 items in 11 benchmarks.
- The decisive caveat for this thesis is Jiang et al., arXiv:2607.15190 [V]. Scalable estimators give *unreliable item-level
  and ranking inferences with small or non-normal model sets*. With 18 models, item-level parameters are weak. Every test
  below therefore aggregates to cells, fixes θ on TRAIN, and uses null partitions to absorb item noise.

**(b) Capability factors.**
- Burnell et al., arXiv:2306.10062 [S]: on HELM, 3 factors (comprehension, reasoning, language modelling) explain 82% of the
  variance across 29 models.
- Ruan, Maddison & Hashimoto, NeurIPS 2024, arXiv:2405.10938 [S]: 3 PCs explain about 97% of the variance (general, reasoning,
  programming), and PC1 alone about 80%.
- Ilić, arXiv:2310.11616 [S]: a g factor of about 85% on the Open LLM Leaderboard.
- Haznitrama et al., arXiv:2609.36515 [V]: across 1,618 models × 456 benchmarks, g explains at most 70.8%. Content-similar
  benchmarks do not necessarily cluster, and factors are "partially idiosyncratic and not identifiable in practice".

All of these factor *benchmarks* (benchmark-level scores). None factors *items within a benchmark*, which is the tree's
granularity. That gap is the thesis's opening.

**(c) Multidimensional IRT and joint embeddings.**
- CAIMIRA (Gor et al., EMNLP 2024, arXiv:2410.06524 [S]) computes multidimensional item relevance and difficulty from the
  question-text embedding, which generalises to unseen items.
- JE-IRT (Yao et al., arXiv:2509.22888 [V]) finds that response-derived item directions align with semantics. Its learned
  "LLM-internal taxonomy" only *partially* aligns with human subject categories, and it finds cross-subject ability axes.
- Chen et al., arXiv:2510.00844 [V], use MoE-parameterised MIRT for routing and benchmark prediction.
- Textbook MIRT: Reckase 2009 (unverified). Parallel analysis: Horn 1965 (unverified).

**(d) Clustering items by response pattern; text vs response alignment.**
- Anchor Points (Vivek et al., EACL 2024 [S]) clusters items by the correlation of model confidences across models and picks
  medoids.
- ECC (Wu, Silwal & Zhang, arXiv:2605.17110 [V]) *calibrates semantic embeddings with model-comparison evidence*. Its clusters
  beat human-label baselines by 17.6pp and pure embedding clusters by 18.0pp on capability ranking. It is the closest prior
  work to "a tree whose cells are checked against response structure". It also suggests that embedding-only cells are
  measurably mis-aligned with response structure.
- JE-IRT and Haznitrama (above) point the same way: partial alignment at best.

**(e) Redundancy and item selection.**
- metabench (Kipnis et al., ICLR 2025, arXiv:2407.12844 [S]) reduces six leaderboard benchmarks to below 3% of their items.
- Perlitz et al., NAACL 2024 [S], study efficient benchmarking and reliability on HELM.
- tinyBenchmarks and Anchor Points (above).

Cells are natural *strata* for this. No paper found tests a taxonomy's cells as sampling strata against IRT anchors.

**(f) Routing on response patterns.**
- Shnitzer et al., NeurIPS 2023 workshop / COLM 2024, arXiv:2309.15789 [S], route with per-model kNN correctness predictors
  on sentence embeddings.
- EmbedLLM (Zhuang et al., ICLR 2025, arXiv:2410.02223 [S]).
- IRT-Router (Song et al., ACL 2025, arXiv:2506.01048 [S]): 20 LLMs, 12 datasets.
- Chen et al. 2025 [V]; ECC [V]; "When simple kNN beats complex learned routers", arXiv:2505.12601 [S, authors unchecked].

KNN-ROUTE (registered) already covers kNN and a correctness-partition [TS] ceiling. What remains open is a parametric
IRT-from-text router as a cell-free comparator.

## 2. Ranked table

Shared settings: everything below is zero-call, uses CPU only, and is a POOL READER (rule 7, never inside a construction). The
object is the content-closed v2 union split (draw 5a3e756, pool `pv2_1575de61bb20e977`, TRAIN 12,334 / EVAL 5,907 in 5,404
components, 18 models) with AF-U, K_0 s0-4, SRC, RWS (200) and declared as built for ROUTE-SOURCE-NULL / KEY-INFO-V2. Label
status follows the review: AF-U, K_0, SRC and RWS are [SC], declared is [DECL], and anything fitted on correctness is [TS].

| # | Test | Question for the tree | Lit. anchor | Distinct from registered? | Cost | Value |
|---|---|---|---|---|---|---|
| 1 | **RESP-PROFILE-INFO**: cell-explained *interaction* (Rasch-residual) variance vs RWS / K_0 | Do cells carry *which-model* structure beyond difficulty and beyond source? | ECC, JE-IRT, CAIMIRA | Yes. KEY-INFO-V2's Brier mixes the difficulty main effect with the interaction; this isolates the interaction, the only routing-relevant part | coder ~3 h, CPU < 30 min | High |
| 2 | **CELL-STRATA-EVAL**: stratified-by-cell item sampling vs random vs IRT anchors, leave-one-model-out | Do cells cut evaluation cost (SQ4 PRICE)? | tinyBenchmarks, Anchor Points, metabench | New use; nothing in the record | coder ~4 h, CPU ~1 h | High |
| 3 | **TEXT-RESP-ALIGN**: within-source Mantel (embedding cosine vs residual-pattern similarity) and AMI(tree, response partition) vs RWS / K_0 | Is the text geometry aligned with response structure at all, and is the tree better aligned than k-means? | JE-IRT, Haznitrama, ECC | Yes. KNN-ROUTE's TS arm is a routing ceiling, not an alignment measure | coder ~3 h, CPU ~1 h | Med-high |
| 4 | **CELL-DIFFICULTY**: η² of IRT difficulty by cell vs RWS; difficulty-composition share of per-cell accuracy spread; 3PL check of CELL-FLIPS | Are cells difficulty strata? Are flips multidimensional? | Rodriguez, Truong, Vania | Yes | coder ~3 h, CPU minutes | Medium |
| 5 | Item audit: negative or near-zero 2PL discrimination (fit on TRAIN); rate at low-filing-margin vs high-margin items | Is label or key noise concentrated at tree boundaries (review issue 4)? | PSN-IRT; Gema et al. 2025 [S, in review] | Yes | coder ~2 h | Medium |
| 6 | IRT-from-text router (ridge from the 256-d slice + source one-hot to MIRT item parameters, TRAIN), as a descriptive arm beside KNN-ROUTE | Is a cell-free parametric router better than cells? | IRT-Router, CAIMIRA, Chen 2025 | Partly (KNN-ROUTE answers the cell question) | coder ~4 h | Med-low |
| 7 | Cell-level factor map: cells' 18-model profiles projected on TRAIN MIRT ability directions; cophenetic fit of the tree to profile distance | Does the hierarchy organise capability factors? | Burnell, Ruan | Overlaps review row 6 (Profile-Mantel) | ~2 h | Low-med |
| 8 | Dimensionality per source with a 2PL/3PL parallel-analysis null | How many response dimensions exist (the upper bound on what any cell set can carry)? | Horn (unverified), Jiang 2026 | Descriptive prerequisite of 1 and 3 | ~1 h | Prereq |

Ranking logic. Test 1 answers the question the thesis's framing ("cell-conditional evaluation") actually rests on, and it does
so with a second ground truth. Test 2 is the only route to a positive SQ4 tree result found so far. Test 3 tests the geometry
itself. Test 4 is a cheap diagnostic that turns CELL-FLIPS into a mechanism statement.

## 3. Top four, specified for registration

**Common to all four.** Objects and hygiene as in §2. A B0-2 pool check precedes every run. Outputs go to E: pinned by sha256
and are never committed, and temp files go through `scratch_dir.py`. The identity precondition is that the declared arm
reproduces C1 +2.67pp and AF-U reproduces G_AF +1.52pp. Model abilities θ (and, for test 1, MIRT directions) are fitted on
TRAIN only and frozen. EVAL item parameters are estimated with θ fixed, item by item (ridge λ fixed now at 1.0), so they never
see cells. Two-stage bootstrap runs over CK-CLOSE components with B 2,000, and seeds 0-4. MATH correctness comes from
`eval_results_mathfix`, as the union readers do. IRT model: 3PL with the guessing floor fixed at 1/options for MC sources
(GPQA, MMLU-Pro) and 0 elsewhere. This is not estimated, because 18 models cannot identify it (Jiang 2026).

**T-R1 RESP-PROFILE-INFO.**
- Residual: on EVAL, e_im = (y_im − P̂_im) / sqrt(P̂(1−P̂)), with P̂ from the 1-D 3PL (TRAIN θ, EVAL item b and a). This removes
  each item's difficulty and discrimination, and each model's general ability.
- Statistic, per arm: R²_int = 1 − Σ(e_im − ē_c(i),m)² / Σ e_im². Here ē_c,m is the **TRAIN** mean residual of model m in cell
  c (TRAIN residuals from the same fit; shrunk toward 0 by n_c / (n_c + 20), with the shrinkage constant fixed now). The
  statistic is out-of-sample by construction.
- Arms: AF-U, K_0 s0-4, SRC, RWS 200, declared [DECL, reference].
- RP1 (deciding): BEYOND-SOURCE iff R²_int(AF-U) > RWS p97.5; NOT-BEYOND otherwise.
- RP2: D = R²_int(AF-U) − mean R²_int(K_0). AF-BETTER or K0-BETTER needs the 95% interval to exclude 0 AND |D| > spread_K;
  NEITHER otherwise.
- Descriptive:
  - R²_int(SRC) and R²_int(declared), whose share of R²_int(declared) is the source share.
  - The same statistic on the raw y, which approximates KEY-INFO-V2's quantity. The difference between raw and residual is
    the difficulty-carried share.
- Support: a planning SD of the per-item residual contribution is needed. Compute it on a TRAIN-half pre-pass before EVAL. RP1
  is a percentile classification with a Monte Carlo SE printed.
- Falsifier: RP1 NOT-BEYOND. Cells then carry no which-model information beyond random within-source cells once difficulty is
  removed. Any cell routing gain is difficulty composition or source, and "cell-conditional evaluation" must say so.
- Prediction: R²_int is small everywhere (< 0.03), given that the general factor is removed and items are 18-bit. RP1
  BEYOND-SOURCE 0.55. The BBH cells carry most of it, as in CELL-FLIPS.

**T-R2 CELL-STRATA-EVAL.**
- Task: for each held-out model m (leave-one-model-out over 18), estimate m's EVAL accuracy from n sampled EVAL items,
  n ∈ {50, 100, 200, 400}, fixed now, with n 100 deciding.
- Arms:
  - RAND: simple random sampling.
  - STRAT-AF: proportional allocation over AF-U cells, with the cell-weighted estimator.
  - STRAT-K0 (s0-4).
  - STRAT-SRC.
  - IRT-ANCHOR (tinyBenchmarks-style): k-means on EVAL item IRT embeddings estimated from the *other 17* models, with
    n anchors as medoids weighted by cluster size. This is [TS] but contains no outcome of m.
  - STRAT-AF+IRT: tinyBenchmarks' gp-IRT correction on STRAT-AF samples.
- Repetitions: 500 sample draws per (m, n, arm).
- Metric: MAE over models and draws.
- CS1 (deciding): STRAT-AF beats RAND iff its MAE ratio < 1 with a 95% interval (bootstrap over models × draws, clustered by
  model) wholly below 1.
- CS2: STRAT-AF vs STRAT-K0 and vs STRAT-SRC, like with like ([SC]). AF-BETTER requires the interval to exclude 0 AND exceed
  spread_K.
- IRT-ANCHOR is a [TS] ceiling and is never ranked against the others.
- Falsifier: CS2 shows STRAT-AF ≤ STRAT-SRC. Then tree cells add nothing to sampling efficiency beyond source strata, and an
  SQ4 "tree cuts evaluation cost" sentence is off the table.
- Note: stratification gains are bounded by the between-cell variance of item accuracy, which links T-R2 to T-R4's η².
  Neyman allocation is a descriptive arm.

**T-R3 TEXT-RESP-ALIGN.**
- Object: TRAIN only (12,334), so that it also informs construction.
- (a) Mantel. Within each source, on 20,000 random item pairs per source (seed fixed), compute Spearman ρ between the cosine in
  AF-U's 256-d slice and the Pearson correlation of the two items' 18-d residual vectors (residuals from T-R1's fit, TRAIN
  side).
  - Pairs are restricted to the same difficulty decile, which removes the trivial "similar difficulty ⇒ similar pattern" path.
  - Null: 1,000 within-source, within-decile permutations of item labels.
  - Noise ceiling: the same ρ between a model-split-half pattern correlation (9 vs 9 models, 20 random splits) and the full
    one, reported beside.
- (b) Partition alignment.
  - PR: spherical k-means of TRAIN residual vectors within source, at AF-U's per-source k (seeds 0-4).
  - Statistic: AMI(PR, AF-U) against AMI(PR, K_0 s0-4) and AMI(PR, RWS 200).
- TA1 (deciding): ALIGNED iff the pooled within-source ρ exceeds its permutation p97.5; NOT-ALIGNED otherwise.
- TA2: TREE-BETTER-ALIGNED iff AMI(PR, AF-U) − mean AMI(PR, K_0) > spread over PR seeds × K seeds AND AMI(PR, AF-U) > RWS
  p97.5. TREE-NOT-BETTER otherwise.
- Falsifier: TA1 NOT-ALIGNED. Text geometry then carries no response structure beyond difficulty, and any routing value of
  embedding cells comes through source or difficulty.
- Prediction: TA1 ALIGNED, but with ρ small (about 0.05-0.10; cf. ECC's large calibration gains and JE-IRT's "partial").
  TA2 TREE-NOT-BETTER 0.65, consistent with U2 and T-C1's tree ≈ k-means.

**T-R4 CELL-DIFFICULTY.**
- (a) η²_b: the share of the variance of EVAL item difficulty b_i (3PL, θ fixed from TRAIN) explained by cell, using TRAIN-side
  cell means (out-of-sample, as in T-R1). Arms: AF-U, K_0, SRC, RWS, declared.
- (b) Composition share: for each model, the variance across AF-U cells of its EVAL cell accuracy, split into the part
  predicted by the 1-D 3PL (difficulty composition) and the residual (interaction). Report the median over models.
- (c) CELL-FLIPS check: for each of the 7 BH-surviving AF-U flip cells, test whether the flip survives the 1-D 3PL expectation.
  A parametric bootstrap from the fitted 1-D model (1,000 replicates) gives the probability that a flip of the observed size
  arises under 1-D. A flip cell is MULTIDIM iff p < 0.05 after BH.
- CD1 (deciding): DIFFICULTY-STRATA iff η²_b(AF-U) > RWS p97.5 AND the median composition share > 0.5. Otherwise
  NOT-DIFFICULTY-STRATA.
- CD2 (descriptive count): the number of the 7 flip cells that are MULTIDIM.
- Falsifier of the CELL-FLIPS reading "cells where the roster order changes": CD2 = 0. The flips are then reproducible as
  guessing or ceiling effects under one dimension.
- Prediction: CD1 DIFFICULTY-STRATA 0.6 (MMLU-Pro and MATH cells differ strongly in difficulty). CD2 ≥ 4 of 7 (BBH template
  cells won by internlm look genuinely multidimensional).

## 4. What this note does not show

No number of record is new. §0 is a feasibility descriptive over both split sides that computes no cell quantity. The IRT
parameters on 18 models are weak at the item level (Jiang 2026 [V]), so every test aggregates to cells and calibrates against
null partitions. A response-pattern ground truth is roster-specific: with a different 18 models the "same kind of item"
changes, which is the analogue of embedder dependence under SQ5. Response-built partitions are [TS] and stay ceilings. [S]
citations need their abstract pages opened before they enter the thesis.
