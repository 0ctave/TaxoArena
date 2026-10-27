# Related work for TaxoArena (literature scan, 2026-10-02)

Scope: papers closest to the thesis's five sub-questions (SQ1 USE / routing gain, SQ2 TRUST / judge,
SQ3 TAXONOMY, SQ4 PRICE, SQ5 INVARIANCE). Read-only scan; nothing run. Context read:
`docs/agents/KNOWLEDGE.md`, `docs/agents/plans/2026-10-01_checkpoint_B.md`.

**Verification marks.**
- **[V]** the arXiv/ACL/publisher abstract page was fetched and the claims below were read from it.
- **[S]** found and confirmed by web search (title, authors, venue, id agree across several hits); the
  abstract was not opened, so the summary is based on search snippets.
- No paper is listed from memory alone. Anything I could not confirm is in the "Not verified" section at the end.

Papers from before 2018 (Banerjee et al. 2005, Liu et al. 2008, Dasgupta 2016) fall outside the 2018-2026
window. They are listed because they are the canonical references for methods the thesis already uses.

---

## 1. LLM routing and per-query / per-category model selection (SQ1)

**Huot, F., Kaisers, M., Lapata, M. (2026). When is Routing Meaningful? Diversity and Robustness in Language
Model Societies.** arXiv:2607.09197. https://arxiv.org/abs/2607.09197 [V]
- What it does: argues that two things besides accuracy and cost decide whether routing is meaningful. The
  actors must behave differently, and the router must be stable, meaning surface variants of a query go to the
  same actor. It adapts Hierarchic Social Entropy (HSE) to measure diversity and adds a perturbation-robustness
  metric. Findings: fewer than 10 agents recover most of a pool's diversity; kNN routers gain accuracy but
  collapse under perturbation, while prompted routing stays stable.
- Thesis part: SQ1 and SQ5.
- Borrow: this is the closest external statement of two thesis results: "routing gains are small and
  concentrated", and "a label-free cell is a surface-sensitive address" (SQ5 C4/F4, SLOTSWAP).
  - Report an HSE-style diversity number for the roster per cell. This tells whether a zero gain on MMLU-Pro
    means "no diversity" or "router failure".
  - Report the thesis's perturbation sensitivity S in their robustness-metric form so the two are comparable.
  - Warning: their kNN-collapse result predicts that embedding-cell routers are fragile. That fits the
    thesis's SLOTSWAP mechanism.

**Ong, I., Almahairi, A., Wu, V., Chiang, W.-L., Wu, T., Gonzalez, J. E., Kadous, M. W., Stoica, I. (2024).
RouteLLM: Learning to Route LLMs with Preference Data.** arXiv:2406.18665. https://arxiv.org/abs/2406.18665 [S]
- What it does: binary strong/weak routers (matrix factorisation, BERT classifier, similarity-weighted BT)
  trained on about 80k Chatbot Arena preferences plus augmentation. Reports more than 2x cost savings at matched
  quality on MT-Bench, MMLU and GSM8K.
- Thesis part: SQ1, SQ4.
- Borrow: the cost-quality curve and its metrics (APGR, call-performance threshold) as a secondary readout for
  the per-cell policy. The similarity-weighted BT router is a per-query BT. It is the natural continuous
  counterpart of the thesis's per-cell BT, and a good baseline for "cells vs no cells".

**Hu, Q. J., Bieker, J., Li, X., et al. (2024). RouterBench: A Benchmark for Multi-LLM Routing System.**
arXiv:2403.12031. https://arxiv.org/abs/2403.12031 [S]
- What it does: 405k precomputed inference outcomes across models and tasks, so routers can be evaluated
  offline. Also gives a theoretical frame (non-decreasing convex hull of cost-quality points; oracle router).
- Thesis part: SQ1, SQ4.
- Borrow: the "zero-router" baseline, a convex-hull mix of single models. The thesis's "best single model"
  comparator is a special case of it. Also the oracle upper bound, as a ceiling for G_tree +2.62pp.

**Huang, Z., et al. (2025). RouterEval: A Comprehensive Benchmark for Routing LLMs to Explore Model-level
Scaling Up in LLMs.** Findings of EMNLP 2025; arXiv:2503.10657. https://arxiv.org/abs/2503.10657 [S]
(Lead-author list not fetched; the search confirmed the title, venue and id.)
- What it does: 200M performance records across more than 8,500 LLMs and 12 evaluations. A capable router
  shows "model-level scaling up" as candidates grow, but all existing routers fall well short of the oracle.
- Thesis part: SQ1.
- Borrow: the oracle-vs-router gap framing. Warning: oracle gains grow with pool size, so "small gain on the
  roster measured" must keep its roster qualifier. The thesis already does this.

**Li, H., Zhang, Y., Guo, Z., et al. (2026). LLMRouterBench: A Massive Benchmark and Unified Framework for LLM
Routing.** arXiv:2601.07206. https://arxiv.org/abs/2601.07206 [V]
- What it does: 400k instances, 21 datasets, 33 models. Under unified evaluation many routers perform
  similarly, and several commercial and recent routers fail to beat simple baselines consistently. The gap to
  the oracle is mostly model-recall failure. A curated small ensemble shows diminishing returns. The choice of
  embedding backbone has limited influence on routing effectiveness.
- Thesis part: SQ1, SQ5.
- Borrow:
  - Direct external support for "simple declared-label policy is as good as the tree" (M = -0.05pp).
  - The embedding-backbone result is a useful contrast with SQ5. Routing accuracy can be embedder-insensitive
    while fine partitions are embedder-sensitive. The thesis can state both: invariance of the decision, and
    non-invariance of the address.

**Lee, J. (2026). Most of the LLM Routing Gap Is Task Type.** arXiv:2608.23023.
https://arxiv.org/abs/2608.23023 [V]
- What it does: 14 models, 294 questions, 3 languages, 7 task types. Task type explains 21 of 29 improvable
  questions. A static task-type routing table beats the best single model: 262 vs 245 correct at $3.33 vs $7.69.
  The residual after task-type and language routing (6 questions) is smaller than the 5.37% run-to-run scoring
  noise.
- Thesis part: SQ1, SQ2 (noise floor).
- Borrow: this is almost exactly the thesis's "declared cells" design (S1), at small scale.
  - Agreement: declared categories capture most of the gain. The thesis's M ≈ 0 (tree vs declared labels)
    says the same at much larger n.
  - Borrow their framing that the residual must be compared with the retest noise floor. The thesis has a
    5.7% judge test-retest figure (DECOMP), and the RP21 v2 retest floor is pending.
  - Caveat: n = 294, single author, no CIs reported in the abstract. Cite as corroborating, not as evidence.

**Zhang, Y., Adeshina, S., Guan, S., Ganesh, A., Han, Z., Ioannidis, V. N., Rangwala, H., Karypis, G. (2026).
Scalable Prompt Routing via Fine-Grained Latent Task Discovery.** arXiv:2603.19415.
https://arxiv.org/abs/2603.19415 [V]
- What it does: discovers fine-grained task types by graph-based clustering of prompts, then trains a
  classifier and a mixture-of-experts quality head per task type. Across 10 benchmarks and 11 frontier models it
  beats the strongest single model at less than half its cost.
- Thesis part: SQ1, SQ3.
- Borrow: the closest competitor to "tree cells as routing units". It claims discovered fine tasks do help.
  The thesis's G13 FAILED / M ≈ 0 says label-free cells do not beat declared labels.
  - Run (or at least discuss) their cluster-then-route recipe as an external arm on the thesis's content-closed
    split, with the label-conditioned prototype baseline the thesis already has.
  - Note: their gain is reported vs the best single model, not vs a declared-category policy. That is the
    comparison the thesis adds.

**Moayeri, M., Balachandran, V., Chandrasekaran, V., Yousefi, S., Fel, T., Feizi, S., Nushi, B., Joshi, N.,
Vineet, V. (2024). Unearthing Skill-Level Insights for Understanding Trade-Offs of Foundation Models.**
arXiv:2410.13826 (ICLR 2025). https://arxiv.org/abs/2410.13826 [S]
- What it does: parses skills from model rationales across 46k instances and 12 benchmarks to form "skill
  slices". Models whose overall accuracy differs by 0.4% differ by ±18-19% on individual skills. Routing each
  instance to the model strongest on its skills gives +3% accuracy.
- Thesis part: SQ1, SQ3.
- Borrow: an LLM-labelled alternative cell definition with a reported routing gain (+3%) of the same order as
  the thesis's +2.6pp. Useful as a magnitude anchor ("a few points"), and as a non-embedding cell baseline.

**Okamoto, M., Erol, A. K., Matlin, G. (2026). Trust by Design: Skill Profiles for Transparent, Cost-Aware
LLM Routing (BELLA).** arXiv:2602.02386 (MLSys YPS 2025). https://arxiv.org/abs/2602.02386 [V]
- What it does: extracts skills from critiques, clusters them into skill matrices, and optimises model choice
  under budget with natural-language rationale. Demonstrated on financial reasoning.
- Thesis part: SQ1, SQ4. Minor. Cite for "interpretable routing cells" if needed.

## 2. LLM-as-a-judge: reference guidance, over-reliance, biases, stability (SQ2)

**Zheng, L., Chiang, W.-L., Sheng, Y., et al. (2023). Judging LLM-as-a-Judge with MT-Bench and Chatbot
Arena.** NeurIPS 2023 D&B; arXiv:2306.05685. https://arxiv.org/abs/2306.05685 [S]
- What it does: the founding paper. It names position, verbosity and self-enhancement biases and limited
  reasoning. It proposes swap-order and reference-guided judging (the judge first solves, or is given a
  reference, for math). GPT-4 agrees with humans above 80%.
- Thesis part: SQ2.
- Borrow: cite as the origin of the dual-order TIE-on-flip rule and of reference-guided grading.
  - Their reference-guided gain on math is the qualitative claim that the thesis quantifies conditionally:
    0.92 accuracy when the reference is right, 0.26 when it is wrong, 16 points lost without a reference.

**Wang, P., Li, L., Chen, L., Cai, Z., Zhu, D., Lin, B., Cao, Y., Liu, Q., Liu, T., Sui, Z. (2023). Large
Language Models are not Fair Evaluators.** arXiv:2305.17926 (ACL 2024). https://arxiv.org/abs/2305.17926 [S]
- What it does: swapping the order of two answers lets Vicuna-13B beat ChatGPT on 66 of 80 queries. Proposes
  multiple-evidence calibration, balanced position calibration and human-in-the-loop calibration.
- Thesis part: SQ2. Borrow: the canonical position-bias citation and the balanced-position calibration the
  thesis implements.

**Shi, L., Ma, C., Liang, W., Ma, W., Vosoughi, S. (2025). Judging the Judges: A Systematic Study of Position
Bias in LLM-as-a-Judge.** IJCNLP-AACL 2025; arXiv:2406.07791. https://arxiv.org/abs/2406.07791 [S]
- What it does: 15 judges, 22 tasks, about 40 answer models, more than 150k instances. Defines repetition
  stability, position consistency and preference fairness. Position bias is weakly tied to length and strongly
  driven by the quality gap between answers.
- Thesis part: SQ2.
- Borrow: the three metrics give standard names for the thesis's flip rate and retest floor.
  - Their finding that position bias grows as the quality gap shrinks predicts that flips/TIEs concentrate in
    near-tie matches. Check this on the K46 store before attributing TIEs to reference quality.

**Dubois, Y., Galambosi, B., Liang, P., Hashimoto, T. (2024). Length-Controlled AlpacaEval: A Simple Way to
Debias Automatic Evaluators.** arXiv:2404.04475 (COLM 2024). https://arxiv.org/abs/2404.04475 [S]
- What it does: fits a GLM of judge preference on length difference (and other mediators) and predicts the
  preference at zero length difference. Win rate swings from 22.9% to 64.3% with a verbosity instruction alone.
- Thesis part: SQ2 (verbosity mechanism; the record's length-matched refits).
- Borrow: the thesis's "+0.39 logit per 1k chars" length effect and its length-matched refits are a GLM
  length control. Cite LC-AlpacaEval as the established method and report the thesis numbers in their
  counterfactual-zero-length form.

**Lee, D., Hwang, Y., Kang, T., Lee, M., Chae, Y., Jung, K. (2026). Judging Against the Reference: Uncovering
Knowledge-Driven Failures in LLM-Judges on QA Evaluation.** arXiv:2601.07506.
https://arxiv.org/abs/2601.07506 [V]
- What it does: a swapped-reference framework that replaces the gold with a wrong entity, creating
  reference-belief conflicts. Grading reliability drops sharply across many judges, because judges fall back on
  parametric knowledge and ignore the given reference. Prompt fixes do not cure it.
- Thesis part: SQ2. This is the nearest published result to the thesis's conditional fidelity (0.92 vs 0.26).
- Borrow: the controlled swapped-reference design. The thesis observes wrong references naturally; a small
  swapped-reference arm would separate "judge follows the reference" from "judge follows its own belief".
- Tension to state: they find judges *ignore* a wrong reference (they over-rely on parametric knowledge). The
  thesis finds the judge *follows* a wrong reference (0.26; "agreeing with the reference beats being right
  2.7:1", CONSENSUS-FIT).
  - The difference is plausibly regime: their wrong entity conflicts with easy, known facts; the thesis's hard
    MMLU-Pro/GPQA items are ones the judge cannot solve.
  - Worth one sentence; ideally test it by splitting the thesis's wrong-reference items by judge solve-rate.

**Kranti, C., Vajjala, S. (2026). LLM Judges Can Be Too Generous When There Is No Reference Answer.**
arXiv:2607.12885. https://arxiv.org/abs/2607.12885 [V]
- What it does: without a reference, judges over-credit incorrect answers. Adding the reference flips
  correct/incorrect decisions by up to 85% in some settings, and these flips mostly agree with humans. Three
  languages.
- Thesis part: SQ2, directly relevant to the v2 recipe's no-reference branch (69.3% of K46 matches; RP20).
- Borrow: their "calibrate the judge on reference-aware samples before deploying reference-free" protocol is a
  ready design for RP20. Their direction (no reference means too generous) is a falsifiable prediction for the
  no-reference branch's TIE/win structure.

**Tan, S., Zhuang, S., et al. (2025). JudgeBench: A Benchmark for Evaluating LLM-based Judges.** ICLR 2025;
arXiv:2410.12784. https://arxiv.org/abs/2410.12784 [S]
- What it does: response pairs labelled by objective correctness on hard knowledge, reasoning, math and code
  items. Strong judges (GPT-4o) are barely above chance; the best reaches 64%. A judge's ability to verify is
  highly correlated with its ability to solve.
- Thesis part: SQ2.
- Borrow: the solve-verify correlation explains why a perfect reference buys 16.4pp (ORACLE). The judge
  cannot grade what it cannot solve, so the reference supplies the missing solve. Cite as the external version
  of the thesis's reference-correctness interaction.

**Stephan, A., Zhu, D., Aßenmacher, M., Shen, X., Roth, B. (2024/2025). From Calculation to Adjudication:
Examining LLM Judges on Mathematical Reasoning Tasks.** arXiv:2409.04168. https://arxiv.org/abs/2409.04168 [V]
- What it does: judge accuracy correlates strongly with candidate-model task performance, so judges favour
  stronger models' outputs whether or not they are correct. Simple surface features (POS tags) predict 70-75%
  of judge decisions. Judges identify the better model in aggregate but fail per item.
- Thesis part: SQ2. Borrow: a warning that matches the frontier-order residual (selective abstention plus
  length). Aggregate model order can look right while per-item fidelity is poor. Report both.

**Bellibatlu, R. R., Raff, E., Zhang, W. (2026). JudgeSense: A Benchmark for Prompt Sensitivity in
LLM-as-a-Judge Systems.** arXiv:2604.23478. https://arxiv.org/abs/2604.23478 [V]
- What it does: 25 judges, 6 providers, 4 tasks, 880 items. Rewording the judge prompt costs agreement on all
  four tasks. Within a family, parameter count does not predict stability. Judges inside agent frameworks lose
  self-agreement faster than cross-wording agreement.
- Thesis part: SQ2 (template sensitivity), SQ4 (retest).
- Borrow: separate within-template retest from cross-template agreement. The thesis's v1/v2 recipes are "never
  joined" (S4); JudgeSense's metric gives the language for why.

**Haldar, R., Hockenmaier, J. (2025). Rating Roulette: Self-Inconsistency in LLM-As-A-Judge Frameworks.**
Findings of EMNLP 2025; arXiv:2510.27106. https://arxiv.org/abs/2510.27106 [V]
- What it does: LLM judges have low intra-rater reliability across runs; in the worst case scores are "almost
  arbitrary".
- Thesis part: SQ2/SQ4. Borrow: a citation for the test-retest floor (DECOMP 5.7%) and for why RP21's retest
  leg is needed.

**Gema, A. P., et al. (2024/2025). Are We Done with MMLU?** arXiv:2406.04127 (NAACL 2025).
https://arxiv.org/abs/2406.04127 [S]
- What it does: estimates that 6.49% of MMLU questions contain errors (57% in Virology). Releases MMLU-Redux
  (5,700 re-annotated items).
- Thesis part: SQ2 (reference correctness; checker tables).
- Borrow: gold labels are themselves imperfect. The thesis's "reference right/wrong" split depends on gold. Cite
  this and, if MMLU-Pro overlaps MMLU-Redux items, use Redux labels as a robustness check on the 0.92/0.26 split.

## 3. Arena / leaderboard evaluation, Bradley-Terry, categories (SQ1, SQ2)

**Chiang, W.-L., Zheng, L., Sheng, Y., Angelopoulos, A. N., et al. (2024). Chatbot Arena: An Open Platform
for Evaluating LLMs by Human Preference.** ICML 2024 (PMLR 235); arXiv:2403.04132.
https://arxiv.org/abs/2403.04132 [S]
- What it does: crowdsourced pairwise battles, BT leaderboard with bootstrap CIs, active sampling, and topic
  analysis showing prompts are diverse and discriminative.
- Thesis part: SQ1/SQ2. Borrow: the BT-with-sandwich/bootstrap CI convention and the category leaderboards.
  The thesis's per-cell BT is a category leaderboard with declared cells. Cite as the standard and contrast:
  the thesis uses a reference-guided LLM judge instead of crowd votes.

**Li, T., et al. (8 authors) (2024). From
Crowdsourced Data to High-Quality Benchmarks: Arena-Hard and BenchBuilder Pipeline.** arXiv:2406.11939.
https://arxiv.org/abs/2406.11939 [S] (search confirmed "Tianle Li and 7 others"; full author list not fetched)
- What it does: clusters Arena prompts into topics, scores prompts on 7 quality criteria with an LLM, and
  keeps hard, discriminative ones (500 prompts). Arena-Hard-Auto gives 3x MT-Bench's separation and 98.6%
  correlation with human ranking.
- Thesis part: SQ1/SQ3. Borrow: topic clustering is used here for *selection* (separability), not as
  evaluation cells. Their "separability with confidence" metric is a candidate cell-quality readout: does a
  cell separate the roster?

**Frick, E., Chen, C., Tennyson, J., Li, T., Chiang, W.-L., Angelopoulos, A. N., Stoica, I. (2025).
Prompt-to-Leaderboard (P2L).** arXiv:2502.14855. https://arxiv.org/abs/2502.14855 [S]
- What it does: an LLM maps a prompt to a vector of BT coefficients, giving a per-prompt leaderboard. It is
  used for routing; the P2L router reached #1 on Chatbot Arena in January 2025.
- Thesis part: SQ1. This is the limit of cell-conditional evaluation where every prompt is its own cell.
- Borrow: P2L is the strongest "no discrete cells" baseline. The thesis's cells sit between one global BT and
  P2L. Discuss where declared cells fall on that continuum. P2L's routing gain over the best single model is
  the natural external number.

**Singh, S., Nan, Y., Wang, A., D'Souza, D., Kapoor, S., Üstün, A., Koyejo, S., Deng, Y., Longpre, S., Smith,
N. A., Ermis, B., Fadaee, M., Hooker, S. (2025). The Leaderboard Illusion.** arXiv:2504.20879.
https://arxiv.org/abs/2504.20879 [S]
- What it does: undisclosed private testing, selective reporting, unequal data access and silent deprecation
  distort Chatbot Arena. Arena-data access gives up to 112% relative gains on ArenaHard.
- Thesis part: SQ1/SQ2 (methodology). Borrow: supports the thesis's pre-registration, frozen-pool and
  write-once outcome discipline. Cite as the motivation for the pool/split hygiene rules.

**Boubdir, M., Kim, E., Ermis, B., Hooker, S., Fadaee, M. (2023). Elo Uncovered: Robustness and Best
Practices in Language Model Evaluation.** GEM workshop @ EMNLP 2023; arXiv:2311.17295.
https://arxiv.org/abs/2311.17295 [S]
- What it does: Elo violates reliability and transitivity for constant-skill LLMs; ratings are volatile and
  hyperparameter-sensitive.
- Thesis part: SQ1/SQ2. Borrow: justification for batch BT (MLE) over online Elo.

**Chatzi, I., Straitouri, E., Thejaswi, S., Gomez Rodriguez, M. (2024). Prediction-Powered Ranking of Large
Language Models.** NeurIPS 2024; arXiv:2402.17826. https://arxiv.org/abs/2402.17826 [V]
- What it does: combines a small set of human comparisons with many LLM-judge comparisons to produce rank-sets
  with coverage guarantees. Rank-sets from LLM judges alone are often inconsistent with human preferences.
- Thesis part: SQ2. This is highly actionable.
- Borrow: the thesis has a small set of verifiable gold outcomes (checkers, gold answers) and a large judged
  set. Prediction-powered inference (PPI) is the principled way to combine them into rank-sets that carry the
  judge's error. It turns "fidelity tracks reference correctness" into calibrated leaderboard intervals.

**Miller, E. (2024). Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations.**
arXiv:2411.00640. https://arxiv.org/abs/2411.00640 [S]
- What it does: super-population framing, clustered SEs for non-independent questions, paired differences,
  power analysis.
- Thesis part: all SQs (DEFF, two-stage intervals, MDE80). Borrow: the standard citation for the record's
  DEFF/Kish and two-stage practice. The thesis's components-clustered intervals are exactly this.

**Llewellyn, M., Thornton, I., Bishop, J., Gray, A. (2025/2026). Correcting Prompt Dependence in LLM
Benchmarks: A Bayesian Hierarchical Model with Embedding-Space Clustering.** arXiv:2510.05709 (ICML 2026
workshop). https://arxiv.org/abs/2510.05709 [V]
- What it does: benchmark metrics misstate uncertainty because prompts are correlated. A Bayesian hierarchical
  model with embedding-space clusters corrects this: MAE improves 4-73%, and the method recovers the latent
  clustering.
- Thesis part: SQ1/SQ3. Borrow: an alternative to DEFF that uses embedding clusters as random effects. It is
  also an external use of "embedding cells" whose value is variance accounting rather than routing, a possible
  framing for what the tree *does* buy.

## 4. Automatic taxonomy / topic discovery and hierarchy evaluation (SQ3)

**Tamkin, A., et al. (2024). Clio: Privacy-Preserving Insights into Real-World AI Use.** arXiv:2412.13678.
https://arxiv.org/abs/2412.13678 [S]
- What it does: LLM-summarised facets of about 1M Claude conversations, embedded and k-means clustered, then
  LLM-built hierarchical cluster trees.
- Thesis part: SQ3. Borrow: the industrial reference point for "embed, cluster, then build a hierarchy over
  queries". Clio's hierarchy is descriptive, with no certification. The thesis's site-null certificate and
  G12 result (no depth-1 site certified) speak to how far such trees can be trusted.

**Wan, M., Safavi, T., et al. (2024). TnT-LLM: Text Mining at Scale with Large Language Models.**
arXiv:2403.12173 (KDD 2024). https://arxiv.org/abs/2403.12173 [S]
- What it does: zero-shot multi-stage LLM taxonomy generation, then LLM labelling to train lightweight
  classifiers. Applied to Bing Copilot user intent and domain.
- Thesis part: SQ3. Borrow: an LLM-generated taxonomy as an alternative arm to embedding splits, evaluated by
  label accuracy and relevance with human raters. Their evaluation protocol (LLM raters plus human agreement)
  is a template if the thesis evaluates cell names.

**Grootendorst, M. (2022). BERTopic: Neural topic modeling with a class-based TF-IDF procedure.**
arXiv:2203.05794. https://arxiv.org/abs/2203.05794 [S]
- What it does: embed, reduce with UMAP, cluster with HDBSCAN, label with c-TF-IDF; supports hierarchical
  topic merging.
- Thesis part: SQ3. Borrow: the de facto practitioner baseline. Adding BERTopic (with its hierarchical topics)
  as a flat/hierarchical comparator next to flat vMF and class-conditioned k-means would pre-empt the obvious
  reviewer question.

**Zeng, Z., Wang, Y., Hajishirzi, H., Koh, P. W. (2025). EvalTree: Profiling Language Model Weaknesses via
Hierarchical Capability Trees.** arXiv:2503.08893. https://arxiv.org/abs/2503.08893 [S]
- What it does: builds a hierarchical capability tree over benchmark instances (each node has an NL capability
  and an instance subset) and extracts low-accuracy nodes as a weakness profile. Evaluated on MATH and
  WildChat; weakness-guided data collection gives 2.5x the gain of generic guidance.
- Thesis part: SQ3/SQ1. This is the closest published analogue to "a tree over benchmark queries used to
  condition evaluation".
- Borrow: their evaluation of the *tree* is by downstream usefulness (does a node predict low accuracy on new
  items?), not by gold-hierarchy agreement. This gives a tree-quality criterion that fits the thesis's
  "cells are useful iff they change a decision".

**Dasgupta, S. (2016). A cost function for similarity-based hierarchical clustering.** STOC 2016, pp. 118-127.
DOI 10.1145/2897518.2897527 [S] (pre-2018; canonical)
- What it does: scores a hierarchy by summing w(i,j)·|leaves(lca(i,j))| over pairs, so similar pairs should be
  split late. Minimising it is NP-hard.
- Thesis part: SQ3. Borrow: a label-free, objective measure of hierarchy quality that can be computed for the
  tree, for a flat partition (as a 2-level tree) and for gold hierarchies (MASSIVE scenario/intent, CLINC
  domain/intent) on the same similarity graph. This is the cleanest "tree vs flat k-means vs gold" scalar.

**Moseley, B., Wang, J. (2017). Approximation Bounds for Hierarchical Clustering: Average Linkage, Bisecting
K-means, and Local Search.** NeurIPS 2017.
https://papers.nips.cc/paper/6902-approximation-bounds-for-hierarchical-clustering-average-linkage-bisecting-k-means-and-local-search [S]
- What it does: under the dual (revenue) form of Dasgupta's objective, average linkage is a 1/3-approximation,
  while bisecting k-means (top-down splits) can be arbitrarily bad.
- Thesis part: SQ3. A warning that applies directly: the thesis's construction is a top-down divisive
  splitter. Top-down 2-means-type splitting has provably poor worst-case hierarchy quality. Average-linkage HAC
  is the theoretically safe baseline and should appear in the tree-vs-flat audit.

**Cohen-Addad, V., Kanade, V., Mallmann-Trenn, F., Mathieu, C. (2018/2019). Hierarchical Clustering:
Objective Functions and Algorithms.** SODA 2018 / JACM 2019; arXiv:1704.02147.
https://arxiv.org/abs/1704.02147 [S]
- What it does: an axiomatic treatment of admissible hierarchy cost functions (Dasgupta's is admissible) and
  analysis of algorithms under a hierarchical stochastic block model.
- Thesis part: SQ3. Borrow: their HSBM "ground-truth hierarchy" setting is a synthetic testbed where the
  construction should recover a planted tree. That would be a positive control for the certificate.

**Kobren, A., Monath, N., Krishnamurthy, A., McCallum, A. (2017). A Hierarchical Algorithm for Extreme
Clustering (PERCH).** KDD 2017; arXiv:1704.01858. https://arxiv.org/abs/1704.01858 [S]
- What it does: online hierarchical clustering with rotations. Under separability it gives perfect dendrogram
  purity regardless of arrival order. It popularised **dendrogram purity** as the evaluation of trees against
  flat gold labels.
- Thesis part: SQ3 and part 8. Borrow: dendrogram purity is the standard metric for "tree against gold
  labels". It complements the thesis's purity-at-matched-k and P_fl filing rate, and is directly computable on
  CLINC150/Banking77/MASSIVE.

## 5. Spherical clustering and cluster significance / certification (SQ3)

**Banerjee, A., Dhillon, I. S., Ghosh, J., Sra, S. (2005). Clustering on the Unit Hypersphere using von
Mises-Fisher Distributions.** JMLR 6:1345-1382. https://jmlr.org/papers/v6/banerjee05a.html [S] (pre-2018;
canonical)
- What it does: EM for vMF mixtures, a κ approximation for high dimension, and spherical k-means as the
  equal-κ hard-assignment limit.
- Thesis part: SQ3. Borrow: the reference for the thesis's vMF splits and the flat vMF comparator. Note the
  stated equivalence: spherical k-means equals vMF with equal κ and weights. Any FLAT comparison should say
  which of these it uses.

**Liu, Y., Hayes, D. N., Nobel, A., Marron, J. S. (2008). Statistical Significance of Clustering for
High-Dimension, Low-Sample Size Data (SigClust).** JASA 103:1281-1293. [S] (pre-2018) and
**Huang, H., Liu, Y., Yuan, M., Marron, J. S. (2015). Statistical Significance of Clustering using Soft
Thresholding.** JCGS; arXiv:1305.5879. https://arxiv.org/abs/1305.5879 [S]
- What they do: test a 2-means split against a single-Gaussian null whose covariance eigenvalues are estimated
  (soft-thresholded in high dimension), using Monte Carlo from the null.
- Thesis part: SQ3. This is the direct ancestor of the site-null certificate.
- Borrow: the null is a fitted *anisotropic* Gaussian, not an isotropic one. That mirrors the thesis's own
  finding that the isotropic null ceiling (0.02) is far below the within-domain null (0.068-0.130). Cite
  SigClust as precedent for "the null must carry the data's covariance spectrum".

**Kimes, P. K., Liu, Y., Hayes, D. N., Marron, J. S. (2017). Statistical Significance for Hierarchical
Clustering (SHC).** Biometrics 73(3):811-821. DOI 10.1111/biom.12647 [S]
- What it does: sequential Monte Carlo testing down a hierarchy, with SigClust-type nulls at each node and
  family-wise error control.
- Thesis part: SQ3. This is the closest method to the thesis's per-site nulls with hierarchical BH over nested
  sites.
- Borrow: cite as prior art and compare error-control choices (their FWER vs the thesis's per-family FDR q =
  0.05). Their sequential "stop descending once a node fails" rule is a principled alternative to testing all
  sites.

**Grabski, I. N., et al. (2023). Significance analysis for clustering with single-cell
RNA-sequencing data (sc-SHC).** Nature Methods 20. https://www.nature.com/articles/s41592-023-01933-9 [S] (title/venue from search; authors from memory, re-check)
- What it does: extends SHC to count data with a parametric null and multiple-testing control. Shows that
  standard pipelines over-cluster.
- Thesis part: SQ3. Borrow: an external result that most fine clusters from standard pipelines are not
  significant. This supports the thesis's G12 reading that no depth-1 site is certified.

**Gao, L. L., Bien, J., Witten, D. (2024). Selective Inference for Hierarchical Clustering.** JASA
119(545):332-342; arXiv:2012.02936. DOI 10.1080/01621459.2022.2116331 [S] and
**Chen, Y. T., Witten, D. M. (2023). Selective inference for k-means clustering.** JMLR 24(152):1-41.
https://jmlr.org/papers/v24/22-0371.html [S]
- What they do: exact selective p-values for a mean difference between two clusters, conditioning on the
  clustering having produced them. They control selective Type I error where naive tests are badly inflated.
- Thesis part: SQ3. Borrow / warning: the thesis's site null re-runs the split on null draws, which already
  accounts for selection (a parametric bootstrap of the whole procedure). Selective inference is the analytic
  alternative.
  - Cite both to say why a naive separation test after splitting would be invalid, and why the Monte Carlo site
    null avoids that.
  - Caveat to check: Gao et al. assume isotropic Gaussian noise with known σ (Yun & Barber 2023 relax this; not
    fetched). The thesis's anisotropy finding is a reason the Monte Carlo route was needed.

**Cai, X., et al. (2021). Isotropy in the Contextual Embedding Space: Clusters and
Manifolds.** ICLR 2021. https://openreview.net/forum?id=xYGNO86OWDH [S] (title/venue from search; author list from memory, re-check) and
**Ethayarajh, K. (2019). How Contextual are Contextualized Word Representations?** EMNLP 2019;
https://aclanthology.org/D19-1006/ [S]
- What they do: contextual embeddings are globally anisotropic (a narrow cone), but are more isotropic within
  local clusters after centring.
- Thesis part: SQ3, SQ5. Borrow: the theoretical backdrop for why isotropic nulls are too lenient and why
  centring or per-domain nulls change the answer.

**Steck, H., Ekanadham, C., Kallus, N. (2024). Is Cosine-Similarity of Embeddings Really About Similarity?**
WWW 2024 Companion; arXiv:2403.05440. https://arxiv.org/abs/2403.05440 [S]
- What it does: shows analytically that cosine similarities of learned embeddings can be arbitrary, because of
  rescaling freedoms and regularisation.
- Thesis part: SQ5. A warning: embedder-dependence of fine structure is expected, not anomalous. Cosine
  geometry is not identified across models.

**Petukhova, A., Matos-Carvalho, J. P., Fachada, N. (2024/2025). Text Clustering with Large Language Model
Embeddings.** arXiv:2403.15112. https://arxiv.org/abs/2403.15112 [S]
- What it does: compares embedders × clustering algorithms on text datasets. k-means with strong LLM embeddings
  is consistently good. Introduces k-LLMmeans (LLM-summarised centroids).
- Thesis part: SQ3/SQ5. Borrow: external evidence that plain k-means is a hard baseline on modern embeddings.
  This is consistent with the thesis's G13 FAILED.

## 6. Intent discovery and out-of-scope detection (SQ3, SQ5)

**Larson, S., et al. (2019). An Evaluation Dataset for Intent Classification and Out-of-Scope Prediction
(CLINC150).** EMNLP-IJCNLP 2019, pp. 1311-1316. https://aclanthology.org/D19-1131/ [S]
**Casanueva, I., Temčinas, T., Gerz, D., Henderson, M., Vulić, I. (2020). Efficient Intent Detection with Dual
Sentence Encoders (BANKING77).** NLP4ConvAI 2020; arXiv:2003.04807. https://aclanthology.org/2020.nlp4convai-1.5/ [S]
**FitzGerald, J., et al. (2023). MASSIVE: A 1M-Example Multilingual NLU Dataset with 51 Typologically-Diverse
Languages.** ACL 2023; arXiv:2204.08582. https://aclanthology.org/2023.acl-long.235/ [S]
- The three corpora of record. Cite them for gold hierarchies: MASSIVE has 18 scenarios over 60 intents;
  CLINC150 has 10 domains over 150 intents plus an OOS set; Banking77 is a flat set of 77 fine intents.
  Banking77 has no gold upper level, so tree-vs-gold there can only be leaf-level.

**Podolskiy, A., Lipin, D., Bout, A., Artemova, E., Piontkovskaya, I. (2021). Revisiting Mahalanobis Distance
for Transformer-Based Out-of-Domain Detection.** AAAI 2021, 35(15):13675-13682; arXiv:2101.03778.
https://ojs.aaai.org/index.php/AAAI/article/view/17612 [S]
- What it does: Mahalanobis distance on fine-tuned transformer features is a strong OOD detector across intent
  datasets, especially CLINC150.
- Thesis part: SQ3 ("routes nowhere", AUROC 0.97). This is the baseline the thesis's OOS result must be
  compared against.
- Borrow: report the thesis's AUROC next to a Mahalanobis-to-nearest-class-mean baseline on the *same frozen
  embedder* (no fine-tuning) and next to a max-cosine-to-prototype baseline.
  - Without these, AUROC 0.97 cannot be credited to the tree's anchors/gates rather than to the embedding
    geometry. Published supervised CLINC150 OOS numbers are already high, so the comparison is what carries
    the claim.

**Zhang, H., Xu, H., Lin, T.-E. (2021). Deep Open Intent Classification with Adaptive Decision Boundary
(ADB).** AAAI 2021, 35(16):14374-14382; arXiv:2012.10209. https://arxiv.org/abs/2012.10209 [S]
- What it does: learns a spherical decision boundary per known class around a centroid. Anything outside every
  ball is "open/unknown".
- Thesis part: SQ3. ADB is conceptually the same mechanism as "routes nowhere" (no leaf accepts the query).
  Cite as prior art and as a labelled-upper-bound comparator.

**Zhang, H., Xu, H., Lin, T.-E., Lyu, R. (2021). Discovering New Intents with Deep Aligned Clustering.**
AAAI 2021, 35(16):14365-14373. https://ojs.aaai.org/index.php/AAAI/article/view/17689 [S]
- What it does: semi-supervised new-intent discovery on Banking77/CLINC150. It pretrains on known intents,
  then runs k-means with aligned pseudo-labels.
- Thesis part: SQ3. Borrow: standard intent-discovery metrics (NMI, ARI, ACC with Hungarian matching). The
  thesis's purity/filing metrics should be accompanied by NMI/ARI so readers can place them against this
  literature.

**Zhang, Y., Wang, Z., Shang, J. (2023). ClusterLLM: Large Language Models as a Guide for Text Clustering.**
EMNLP 2023, pp. 13903-13920; arXiv:2305.14871. https://aclanthology.org/2023.emnlp-main.858/ [S]
- What it does: LLM triplet feedback fine-tunes the embedder for clustering, and LLM pairwise judgments choose
  the *granularity* (number of clusters). 14 datasets, including Banking77, CLINC and MASSIVE; about $0.6 per
  dataset.
- Thesis part: SQ3/SQ5. Borrow: the finding that "fine structure depends on the embedder, the corpus and the
  prompt" is ClusterLLM's motivating premise: granularity is a user preference, not a property of the
  embedding. Their pairwise-granularity step is a cheap way to ask which level the user means.

**Anderson, G., Hart, E., Gkatzia, D., Beaver, I. (2024). An Open Intent Discovery Evaluation Framework.**
SIGDIAL 2024, pp. 760-769. DOI 10.18653/v1/2024.sigdial-1.64 [V]
- What it does: a modular discovery pipeline (choose a technique per stage, plus human-readable labels) and
  guidance on matching dataset traits to techniques.
- Thesis part: SQ3. Minor; cite for evaluation-protocol context.

## 7. Embedding-model sensitivity: prompts, Matryoshka truncation, quantisation, MTEB (SQ5)

**Muennighoff, N., Tazi, N., Magne, L., Reimers, N. (2023). MTEB: Massive Text Embedding Benchmark.** EACL
2023; arXiv:2210.07316. https://aclanthology.org/2023.eacl-main.148/ [S] and **MMTEB (2025)**,
arXiv:2502.13595. https://arxiv.org/abs/2502.13595 [S]
- What they do: 8 task types, 58 datasets (MMTEB: many more, multilingual). No embedder dominates all tasks.
  The clustering subset (v-measure on k-means) includes intent-like sets.
- Thesis part: SQ5. Borrow: "no single embedder dominates" is the prior for embedder non-invariance. Cite
  qwen3/nomic/gemma MTEB clustering scores next to the thesis's purity results to show whether MTEB clustering
  rank predicts the thesis's rank. If it does not, that is a useful negative.

**Zhang, Y., Li, M., Long, D., et al. (2025). Qwen3 Embedding: Advancing Text Embedding and Reranking Through
Foundation Models.** arXiv:2506.05176. https://arxiv.org/abs/2506.05176 [S]
**Google (Gemma team) et al. (2025). EmbeddingGemma: Powerful and Lightweight Text Representations.**
arXiv:2509.20354. https://arxiv.org/abs/2509.20354 [S] (author list not fetched; re-check before citing)
**Nussbaum, Z., Morris, J. X., Duderstadt, B., Mulyar, A. (2024). Nomic Embed: Training a Reproducible Long
Context Text Embedder.** arXiv:2402.01613. https://arxiv.org/abs/2402.01613 [S]
- The three embedders of record; cite their model cards and reports for the instruction/prefix protocols.
  - Qwen3 uses task instructions on queries.
  - nomic uses `search_query:` / `clustering:` style prefixes.
  - EmbeddingGemma uses task prompts and claims its lead persists under weight quantisation and output
    truncation (MRL).
- Borrow: the "card-conformant" secondary protocol should cite exactly these documents. Note that
  EmbeddingGemma's robustness-under-truncation claim is about MTEB averages. The thesis's SQ5 tests the finer
  property that partitions are preserved, and finds they are not.

**Kusupati, A., Bhatt, G., Rege, A., et al. (2022). Matryoshka Representation Learning.** NeurIPS 2022;
arXiv:2205.13147. https://arxiv.org/abs/2205.13147 [S]
- What it does: trains nested prefixes of an embedding to be useful at every size.
- Thesis part: SQ5 (dimension cut; the record's 512-dim promotion). Borrow: the reason prefix truncation is
  legitimate for MRL-trained models (qwen3, gemma, nomic v1.5) and the comparison point that truncation was
  validated on retrieval/classification, not on fine partition stability.

**Tsukagoshi, H., Sasano, R. (2025). Redundancy, Isotropy, and Intrinsic Dimensionality of Prompt-based Text
Embeddings.** Findings of ACL 2025; arXiv:2506.01435. https://arxiv.org/abs/2506.01435 [V]
- What it does: keeping only the first 25% of dimensions costs little. For classification and *clustering*,
  even fewer than 0.5% of dimensions lose little, while retrieval and STS are more sensitive. Clustering
  embeddings have lower intrinsic dimension and lower isotropy.
- Thesis part: SQ5. This is directly relevant and partly in tension with the thesis.
- Borrow / reconcile: they find clustering scores are robust to aggressive truncation; the thesis finds fine
  partitions move. The likely reconciliation is granularity: MTEB clustering is scored at the gold level (few
  coarse classes), while the thesis audits fine leaves.
  - Worth one explicit sentence and, cheaply, a readout at the gold level under truncation, to show both hold.
  - Their low-isotropy finding also bears on the null design.

**Su, H., Shi, W., Kasai, J., et al. (2023). One Embedder, Any Task: Instruction-Finetuned Text Embeddings
(INSTRUCTOR).** Findings of ACL 2023; arXiv:2212.09741. https://aclanthology.org/2023.findings-acl.71/ [S]
- What it does: instruction-conditioned embeddings across 330 tasks. Reports robustness to instruction
  paraphrase on average.
- Thesis part: SQ5 (instruction prompts). Tension: INSTRUCTOR reports instruction robustness on averages; the
  thesis finds prompt-dependence of fine structure. Same reconciliation as above: averages vs partitions.

**(authors not fetched) (2025). Out-of-the-Box Conditional Text Embeddings from Large Language Models.**
arXiv:2504.16411. https://arxiv.org/abs/2504.16411 [S] (title and id from search only; re-check authors)
- What it does: shows that prompt wording ("Express ..." vs "This text ...") changes conditional embedding
  quality. Only the search snippet was seen.
- Thesis part: SQ5. Borrow: an external citation that template wording moves embedding geometry.

**Quantisation.** I found no peer-reviewed paper that tests the effect of embedding quantisation on
*clustering/partition stability*. The available evidence is retrieval-focused: arXiv:2505.00105
"Optimization of embeddings storage for RAG systems using quantization and dimensionality reduction
techniques" [S, abstract not opened] reports int8 near-lossless and binary losing 7-11% on retrieval. The
EmbeddingGemma report claims MTEB robustness to weight quantisation. **Gap:** the thesis's quantisation
invariance test on partitions appears to be novel. State that carefully, with this caveat.

## 8. Online / streaming hierarchical clustering and taxonomy evolution

**Monath, N., Kobren, A., Krishnamurthy, A., Glass, M., McCallum, A. (2019). Scalable Hierarchical
Clustering with Tree Grafting (Grinch).** KDD 2019, pp. 1438-1448; arXiv:2001.00076.
https://arxiv.org/abs/2001.00076 [S]
- What it does: online non-greedy hierarchy maintenance with rotate and graft operations under general
  linkages.
- Thesis part: part 8 (newcomer placement; tree updates). Borrow: graft/rotate as the minimal edit operations
  for updating a frozen tree when new queries arrive, as an alternative to a full rebuild.

**Monath, N., Zaheer, M., McCallum, A. (2023). Online Level-wise Hierarchical Clustering.** KDD 2023.
DOI 10.1145/3580305.3599455 [S] (abstract page returned 403; authors and venue from Semantic Scholar/ACM
listing)
- Thesis part: part 8. Cite as the current state of online HAC.

**Rajagopalan, A., Vitale, F., Vainstein, D., Citovsky, G., Procopiuc, C. M., Gentile, C. (2021).
Hierarchical Clustering of Data Streams: Scalable Algorithms and Approximation Guarantees.** ICML 2021, PMLR
139. http://proceedings.mlr.press/v139/rajagopalan21a.html [V]
- What it does: hyperplane-based streaming hierarchies with an invariance property and approximation
  guarantees for Dasgupta-type objectives.
- Thesis part: part 8 and SQ3. Borrow: their arrival-order invariance property is the streaming analogue of
  the thesis's G10/G15 reproducibility and order-stability.

**Li, Y., Ma, T., Ye, Y. (2026). EvoTaxo: Building and Evolving Taxonomy from Social Media Streams.**
arXiv:2603.19711. https://arxiv.org/abs/2603.19711 [V]
- What it does: LLM-driven taxonomy evolution. Posts become proposed edits to the taxonomy; edits are
  validated with semantic+temporal clustering and concept memory banks for stability.
- Thesis part: part 8. Borrow: the "propose an edit, then validate it" loop, where the validation is a
  stability check. This mirrors the thesis's propose-then-certify construction loop. Cite as the LLM-era
  analogue.

---

## Most actionable improvements / comparisons (ranked)

1. **Add the missing OOS baselines next to AUROC 0.97** (Podolskiy 2021; ADB 2021). Use Mahalanobis-to-class-mean
   and max-cosine-to-prototype on the same frozen embedder and the same CLINC150 OOS split. This costs zero
   calls and a little CPU. Without it, "routes nowhere" cannot be credited to the tree.
2. **One tree-quality scalar against flat and gold:** Dasgupta cost (or its revenue dual) plus dendrogram purity
   (PERCH). Compute it for the tree, average-linkage HAC, bisecting spherical k-means, flat vMF (as a 2-level
   tree) and the gold hierarchies on MASSIVE/CLINC150. Moseley & Wang predict that top-down 2-means splitting is
   the weakest family, so include average-linkage HAC as the theoretically safe baseline. Report NMI/ARI
   alongside purity so intent-discovery readers can place the numbers.
3. **Combine gold and judge with prediction-powered inference** (Chatzi et al. 2024). The thesis's checker/gold
   subset plus the judged set gives rank-sets that carry the judge's conditional error (0.92/0.26). This turns
   the SQ2 finding into a usable, calibrated leaderboard instead of only a caveat.
4. **Swapped-reference arm for SQ2** (Lee et al. 2026), split by judge solve-rate (JudgeBench). It would decide
   whether the judge follows a wrong reference (thesis) or overrides it (Lee et al.), and in which regime.
   Priced in calls, so it falls under the 4k-match rule.
5. **Pre-specify the no-reference prediction for RP20** from Kranti & Vajjala 2026: without a reference the judge
   is too generous, so expect more wins for wrong answers and fewer TIEs. Adopt their reference-aware
   calibration step as the remedy to test.
6. **External routing baselines:** a per-prompt BT (P2L-style or RouteLLM SW-ranking) and a cluster-then-route
   recipe (Zhang et al. 2026). Report them against the declared-label policy and the best single model, with
   the oracle ceiling (RouterBench/RouterEval) and an HSE diversity figure per cell (Huot et al.). This places
   +2.6pp on a known scale.
7. **Reconcile truncation and prompt invariance with MTEB-style claims.** Rerun the SQ5 readout at the
   *gold-level* granularity under dimension cut and prompt change (zero calls). Expected result: coarse is
   invariant (as in Tsukagoshi & Sasano 2025, EmbeddingGemma, INSTRUCTOR) and fine is not (as in the thesis).
   That turns an apparent contradiction into the thesis's sharpest SQ5 sentence.
8. **Cite SHC (Kimes et al. 2017) and SigClust as the certificate's lineage.** Discuss FWER-sequential vs
   per-family FDR over nested sites, and the anisotropic-null point. Optionally add an HSBM planted-hierarchy
   positive control (Cohen-Addad et al.) to show the certificate *can* certify a real split.

## Where prior work contradicts or already answers a thesis question

- **"Do learned cells beat declared categories for routing?"** This is largely answered "no, task type carries
  most of the gap" (Lee 2026, small n). LLMRouterBench finds simple baselines hard to beat. The thesis's M ≈ 0
  and G13 FAILED agree. Zhang et al. 2026 and Moayeri et al. 2024 claim gains from discovered/skill cells, but
  vs the best single model, not vs a declared-category policy. The thesis's comparison is the stricter one.
- **"Is the reference-guided judge trustworthy?"** Partly answered. Judges cannot verify what they cannot solve
  (JudgeBench; Stephan et al.). The thesis's 0.92/0.26 split is the quantitative version.
  - **Contradiction:** Lee et al. 2026 find judges *ignore* conflicting references; the thesis finds the judge
    *follows* a wrong reference. This is plausibly regime-dependent (easy known facts vs hard items) and must
    be stated.
- **"Is embedding fine structure invariant to truncation and prompts?"** Prior work says embeddings are highly
  redundant and clustering survives extreme truncation (Tsukagoshi & Sasano 2025), and that instructions are
  robust (INSTRUCTOR). This *appears* to contradict SQ5. It does not if the difference is granularity (gold
  level vs fine leaves); the thesis should show this explicitly (item 7).
- **"Are fine clusters real?"** Single-cell work (sc-SHC) and SigClust consistently find standard pipelines
  over-split. The thesis's "no top-level split certified" is in line with that literature, not an anomaly. The
  thesis's extra finding (declared level IS geometric, H 0.29 vs p95 0.026, yet uncertified by the
  construction) is the part prior work does not cover.
- **"Is k-means a weak baseline?"** No. Petukhova et al. and MTEB practice show k-means on strong embeddings is
  hard to beat, consistent with G13.
- **Embedder choice for routing:** LLMRouterBench reports limited influence of the embedding backbone on routing
  effectiveness. That is compatible with SQ5 if decisions are stable while addresses move. Worth testing
  directly (same policy, three embedders).

## Not verified / caveats

- Author lists not opened (re-check before citing): RouterEval (2503.10657), EmbeddingGemma (2509.20354),
  2504.16411, Arena-Hard (2406.11939, beyond Tianle Li), Cai et al. ICLR 2021, Grabski et al. 2023,
  TnT-LLM and Clio beyond the first authors. Page ranges and DOIs for pre-2018 items are from search listings.
- Monath, Zaheer, McCallum (KDD 2023): the ACM page returned 403. Title, authors and venue come from search
  listings only.
- Yun & Barber (2023) on selective inference with unknown variance is mentioned in passing and was not fetched.
- The "Online level-wise" and "Hierarchical Level-Wise News Article Clustering via Multilingual Matryoshka
  Embeddings" (arXiv:2506.00277) hits were seen in search only. The latter could be relevant to MRL + hierarchy
  but was not read, so it is not listed above.
- Every 2026 arXiv preprint above (Huot, Lee, Zhang, Lee et al., Kranti, JudgeSense, EvoTaxo, Okamoto) is
  unrefereed at the time of writing.
