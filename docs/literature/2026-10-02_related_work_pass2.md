# Related work for TaxoArena, pass 2: verification, close reading, gaps (2026-10-02)

Follows `docs/literature/2026-10-02_related_work.md` (pass 1). Read-only; nothing run, zero calls.
Context: `docs/agents/KNOWLEDGE.md`, `docs/agents/plans/2026-10-01_checkpoint_B.md`.

**Marks (stricter than pass 1).**
- **[V]** the abstract page (arXiv / ACL / JMLR / NeurIPS) was opened in this pass and the bibliographic data
  below were read from it.
- **[V\*]** as [V], and the full text (arXiv HTML or PDF) was also opened for the numbers quoted. Numbers taken
  from HTML went through a summarising fetch. Re-check them against the paper's table before they go into the
  thesis. The Podolskiy et al. table is the exception: it was read from the raw PDF text.
- **[S]** confirmed by search listings only (title, authors, venue agree). The abstract was not opened.
- Nothing is cited from memory. Every arXiv id from 2026 is an unrefereed preprint.

Thesis results mapped (the caller's list): routing gain small and BBH-carried, tree cells ≈ declared domains
(+2.62 vs +2.67pp); judge 0.92 / 0.26 by reference correctness; no-reference costs 16pp, mostly as TIEs (82/97),
2.9pp on matches decisive in both arms; false template sentence equivalent within ±4pp; anchored tree −2.2pp vs
class-conditioned k-means, lead over unsupervised k-means comes from the anchors; 0/60 top-level sites certified;
exact reproduction and order stability; OOS AUROC 0.974 label-free; margin predicts purity; slot swaps move 24%;
fine structure depends on embedder × corpus × prompt; gemma's edge survives dimension and quantisation; card
prompts flip MASSIVE/CLINC to qwen3 and Banking77 to gemma; LCB power 0.22.

---

## 1. Verification of pass 1 (the 30 most relevant entries)

| Pass-1 entry | Status now | Corrections |
|---|---|---|
| Huot, Kaisers, Lapata 2026, arXiv:2607.09197 | [V\*] | Authors and title hold. Details in §2.1. |
| LLMRouterBench, arXiv:2601.07206 | [V\*] | Full author list: Hao Li, Yiqun Zhang, Zhaoyan Guo, Chenxu Wang, Shengji Tang, Qiaosheng Zhang, Yang Chen, Biqing Qi, Peng Ye, Lei Bai, Zhen Wang, Shuyue Hu. "Simple baseline" = **Best Single model**. |
| Lee 2026, arXiv:2608.23023 | [V] | Holds. Author: Janghoon Lee. Abstract states "fitted and scored on the same 294 questions with no holdout". Pass 1 missed that caveat; it is stronger than "no CIs". |
| Zhang et al. 2026, arXiv:2603.19415 | [V] | Holds (8 authors as listed in pass 1). |
| RouterEval, arXiv:2503.10657 | [V] | Authors: Zhongzhan Huang, Guoming Ling, Yupei Lin, Yandong Chen, Shanshan Zhong, Hefeng Wu, Liang Lin. The arXiv page shows no venue. "Findings of EMNLP 2025" stays [S]. |
| RouterBench, arXiv:2403.12031 | [V] | Full authors: Qitian Jason Hu, Jacob Bieker, Xiuyu Li, Nan Jiang, Benjamin Keigwin, Gaurav Ranganath, Kurt Keutzer, Shriyash Kaustubh Upadhyay. The abstract does not state the "non-decreasing convex hull" frame, so that detail stays [S]. |
| RouteLLM, arXiv:2406.18665 | [V] | Holds. Use "M Waleed Kadous" as on arXiv. No venue on the arXiv page. |
| Moayeri et al. 2024, arXiv:2410.13826 | [V] | Authors and numbers hold (18% / 19%, +3%). ICLR 2025 is not on the arXiv page, so the venue stays [S]. |
| P2L, arXiv:2502.14855 | [V] | Holds (7 authors). The "power law scaling" claim is also in the abstract. |
| Zheng et al. 2023, arXiv:2306.05685 | [V] | Full authors: Lianmin Zheng, Wei-Lin Chiang, Ying Sheng, Siyuan Zhuang, Zhanghao Wu, Yonghao Zhuang, Zi Lin, Zhuohan Li, Dacheng Li, Eric P. Xing, Hao Zhang, Joseph E. Gonzalez, Ion Stoica. NeurIPS 2023 D&B. |
| Wang et al. 2023, arXiv:2305.17926 | [V] | Holds (66/80). The arXiv page shows no venue. "ACL 2024" stays [S]. |
| Shi et al., arXiv:2406.07791 | [V\*] | **Author list corrected:** Lin Shi, Chiyu Ma, Wenhua Liang, **Xingjian Diao**, Weicheng Ma, Soroush Vosoughi. AACL-IJCNLP 2025 (v9). |
| Dubois et al. 2024, arXiv:2404.04475 | [V] | Holds. COLM 2024. The abstract's number is Spearman with Chatbot Arena **0.94 → 0.98**. The "22.9% → 64.3%" figure is not in the abstract; mark it [S] or drop it. |
| Lee, Hwang, Kang, Lee, Chae, Jung 2026, arXiv:2601.07506 | [V\*] | Holds; v2 dated 2026-06-10. Details in §2.2. |
| Kranti & Vajjala 2026, arXiv:2607.12885 | [V\*] | Holds. The setting is **pointwise** QA (TyDi QA, MATA; English, Arabic, Telugu), not pairwise. |
| JudgeBench, arXiv:2410.12784 | [V] | Full authors: Sijun Tan, Siyuan Zhuang, Kyle Montgomery, William Y. Tang, Alejandro Cuadron, Chenguang Wang, Raluca Ada Popa, Ion Stoica. ICLR 2025. The abstract says GPT-4o is "slightly better than random". The "best reaches 64%" figure and the solve/verify correlation are not in the abstract, so they stay [S]. |
| Chatzi et al. 2024, arXiv:2402.17826 | [V] | Holds. NeurIPS 2024. |
| Miller 2024, arXiv:2411.00640 | [V] | Holds (single author). |
| Tsukagoshi & Sasano 2025, arXiv:2506.01435 | [V] | Holds. Findings of ACL 2025. |
| EmbeddingGemma, arXiv:2509.20354 | [V] | **Author list:** 89 authors, first Henrique Schechter Vera, Sahil Dua, Biao Zhang, Daniel Salz, Ryan Mullins … Cite "Schechter Vera et al. 2025". The quantisation/truncation claim is in the abstract. |
| Kusupati et al. 2022 (MRL), arXiv:2205.13147 | [V] | 11 authors (Kusupati, Bhatt, Rege, Wallingford, Sinha, Ramanujan, Howard-Snyder, Chen, Kakade, Jain, Farhadi). NeurIPS 2022 is not on the arXiv page, so it stays [S]. |
| "Out-of-the-Box Conditional Text Embeddings", arXiv:2504.16411 | [V] | Authors: **Kosuke Yamada, Peinan Zhang**. **Claim dropped:** the abstract (PonTE, unsupervised conditional embeddings) says nothing about wording sensitivity ("Express …" vs "This text …"). Do not cite it for prompt sensitivity. Use Kostiuk & Enevoldsen 2026 (§3) instead. |
| Petukhova et al., arXiv:2403.15112 | [V] | Venue: **Int. J. Cognitive Computing in Engineering 6:100–108 (2025)**. **Claims dropped:** k-LLMmeans is not in this paper, and the abstract does not say "k-means is consistently good". What it does say is that larger dimensionality and summarisation "do not consistently enhance clustering". The "k-means is hard to beat" support now comes from Avengers (§3). |
| ClusterLLM, arXiv:2305.14871 | [V] | Holds (Yuwei Zhang, Zihan Wang, Jingbo Shang; EMNLP 2023; $0.6 per dataset). |
| Podolskiy et al. 2021, arXiv:2101.03778 | [V\*] | Holds (AAAI 2021). Table in §2.6. Note: all the strong numbers use **encoders fine-tuned on in-domain labels**. |
| SHC, Kimes, Liu, Hayes, Marron | [V] | Abstract read on arXiv:1411.5259 (2014): Monte Carlo sequential testing with FWER control. Biometrics 73(3) 2017 stays [S]. |
| SigClust soft thresholding, Huang, Liu, Yuan, Marron | [V] | arXiv:1305.5879; **JCGS 24(4):975–993 (2015)**. Key content in §2.5. Liu et al. 2008 JASA stays [S]. |
| Gao, Bien, Witten, arXiv:2012.02936 | [V] | Holds. JASA 2024 from pass 1 stays [S]. The abstract adds that the inflation persists **even with sample splitting**. |
| Chen & Witten 2023, JMLR 24(152) | [V] | Holds. |
| sc-SHC, Grabski et al. 2023 | [S] (Nature page blocked) | **Authors confirmed via search:** Isabella N. Grabski, Kelly Street, Rafael A. Irizarry. Nature Methods 20(8):1196–1202. DOI 10.1038/s41592-023-01933-9. |
| Moseley & Wang 2017 | [V] | **Claim narrowed:** average linkage has a small constant approximation ratio and bisecting k-means does poorly, *but the authors also give divisive algorithms with constant guarantees*. So the warning is "bisecting k-means", not "top-down" in general. |
| PERCH, arXiv:1704.01858 | [V] | **Title corrected:** "**An Online** Hierarchical Algorithm for Extreme Clustering". KDD 2017 stays [S]. |
| Cai et al. ICLR 2021 (isotropy) | [S] (OpenReview blocked) | Not re-verified; keep out of the main text, or re-check before citing. |

Net: no pass-1 paper turned out to be fictitious. Two claims are dropped (2504.16411's wording sensitivity;
Petukhova's k-LLMmeans and the k-means claim). Two summaries are narrowed (Moseley & Wang; Dubois). Five author
lists or titles are corrected (Shi, EmbeddingGemma, RouterEval, 2504.16411, PERCH).

---

## 2. Close reading of the nearest works

### 2.1 Routing usefulness

**Huot, Kaisers, Lapata (2026), "When is Routing Meaningful? Diversity and Robustness in Language Model
Societies", arXiv:2607.09197 [V\*].**
- **Method.**
  - *Diversity:* Hierarchic Social Entropy over actors. Each actor is a 0/1 correctness vector over prompts;
    distance between actors is 1 − cosine; Shannon entropy of the hierarchical clustering of actors is
    integrated over all thresholds. HSE is 0 when all actors behave identically.
  - *Robustness:* the share of perturbed variants routed to the **same actor** as the original. Perturbations
    are character, word, syntax, paraphrase and rambling. 0 means random routing, 1 means fixed routing.
- **Setup.** EmbedLLM (112 models, 36,054 questions) and RouterBench (11 models, 36,497 queries). Routers:
  random, prompted LLM, and kNN-1/3/10.
- **Numbers.**
  - Diversity plateaus at about 9 agents (EmbedLLM) and 4 (RouterBench). The default pool has HSE 1.62; a
    synthetic subject-specialist society has 3.91.
  - kNN-10 reaches 0.65 accuracy on specialist societies, but robustness collapses to near zero.
  - Prompted routing stays stable, and its robustness rises 0.24 → 0.53 on max-HSE subsets.
  - Robustness is roughly flat across perturbation levels (0.589–0.744).
- **Against the thesis.**
  - *Agrees.* Accuracy and "meaningfulness" diverge. Their mechanism is "a surface reformulation shifts the
    query embedding across a domain boundary". That is the thesis's SLOTSWAP mechanism almost word for word:
    24% of queries move, mostly low-margin ones (M1 origin margin).
  - *Complements.*
    - Their robustness is measured on the **routed actor**. The thesis's S 0.760 is measured on the **cell**.
      A moved query whose old and new cells pick the same model costs nothing. So a decision-level robustness
      readout is the right comparator (zero calls; §5 item 3).
    - HSE on the roster's correctness matrix, per corpus, is the natural label-free predictor of "will routing
      pay here". It would test the reading that MMLU-Pro gives zero because the frontier roster is
      undifferentiated there.
  - *Caveat.* Their kNN collapse shows on synthetic specialist societies. On real pools the effect is smaller.

**LLMRouterBench (Li et al. 2026), arXiv:2601.07206 [V\*].**
- **Setup.** 400k instances, 21 datasets (including BBH, MMLU-Pro, GPQA and MATH, all thesis corpora), 33
  models, 10 routers.
- **Numbers.**
  - Many routers tie. Several, including commercial ones, fail to beat **Best Single** (OpenRouter −24.7% vs
    Best Single in the cost setting).
  - The oracle gap is mainly *model-recall failure*. On queries that 3 or fewer models solve (11.9% of the
    test set), Avengers gets 24.6% and EmbedLLM 23.2%.
  - Swapping gte-qwen2-7B for nli-bert-base or all-MiniLM-L6 makes no significant difference.
  - Gains come mostly from small → moderate pools.
  - The clustering router Avengers ties the neural routers, and Avengers-Pro nearly dominates the cost frontier.
- **Against the thesis.**
  - *Agrees* on "small, concentrated gains" and "best single is a hard baseline".
  - The embedder-insensitivity of **routing accuracy** coexists with the thesis's embedder-sensitivity of **fine
    partitions**. These are compatible only if decisions are stable while addresses move. The thesis can show
    this directly with item 3.
  - *Complements.* Model-recall failure is the per-query version of "gain is BBH-carried": the gain sits where
    a minority model is right.

**Lee (2026), "Most of the LLM Routing Gap Is Task Type", arXiv:2608.23023 [V].**
- **Setup and numbers.** 14 models × 294 questions, matrix run twice. 5.37% of model-question pairs change
  between the two identical runs. 29 questions are improvable under a "correct in both runs" rule; a static
  task-type table recovers 21 of them. 262/294 at $3.33 vs Best Single 245 at $7.69.
- **Against the thesis.** *Agrees* (declared type ≈ most of the gain; the thesis's tree ≈ declared, +2.62 vs
  +2.67). But it has **no holdout**: everything is fitted and scored on the same 294 questions. The thesis's
  TRAIN → content-closed EVAL design is strictly stronger. Cite as corroboration only. Borrow the
  "correct-in-both-runs" rule as a robustness variant of the gain (zero calls where the thesis has repeat draws).

**Zhang et al. (2026), arXiv:2603.19415 [V]** (graph clustering of prompts → latent tasks → MoE quality heads;
10 benchmarks, 11 frontier models).
- **Against the thesis.** *Apparent contradiction:* they claim that fine discovered tasks help. But their
  comparison is against the strongest single model and "existing baselines", **not against a declared-task
  table**. The thesis's tree-vs-declared M = −0.05pp answers the question they do not ask.
- **Sentence:** "Discovered fine-grained task types have been reported to beat the strongest single model
  [Zhang et al. 2026]. On our roster, cells from a label-free tree route no better than the declared domains
  (+2.62 vs +2.67pp), so the discovered structure adds nothing beyond the declared labels here."

**Further routing work found in this pass (details in §3):** Avengers (k-means routing, robust across
algorithms and K); the Routing Plateau (routers converge far below the oracle); the co-failure ceiling;
selection-valid oracle diagnostics; routing oracles under stochastic decoding.

### 2.2 Reference-guided judging: reconciling 0.26 with "judges ignore wrong references"

**Lee, Hwang, Kang, Lee, Chae, Jung (2026), "Judging Against the Reference", arXiv:2601.07506 [V\*].**
- **Setup.** NQ-Open, PopQA, SciQ (1,000 each) and FreshQA (452); 13 judges (GPT-4o/4.1/5, Llama-3.x, Qwen-2.5/3).
  The gold is swapped for an incorrect entity (random, plausible, popularity-based, or agreeing with the
  judge's own belief), with matched candidates.
- **Numbers.**
  - Random swap on NQ-Open: GPT-4o 96.5 → 59.3%; Llama-3.3-70B 97.6 → 64.2%. On SciQ, Qwen-2.5-32B falls
    95.0 → 45.7%.
  - Plausible swaps hurt much less (96.3 → 92.8%).
  - When the swapped reference **agrees with the judge's belief**, the gap disappears (GPT-4o about 98%).
  - The vulnerability grows with entity popularity and is small on fast-changing facts (FreshQA).
  - Chain-of-thought makes it **worse**.
- **Mechanism.** The judge overrides the reference when its parametric knowledge is strong.

**Krumdick, Lovering, Reddy, Ebner, Tanner (2025), "No Free Labels: Limitations of LLM-as-a-Judge Without
Human Grounding", arXiv:2503.05061 (v4 2026-09-28) [V\*]** (new in this pass).
- **Setup.** BFF-Bench (160 expert finance questions) plus CMT-Bench; 1,200 responses, 3,600 expert labels;
  judges GPT-4o, Llama-3.3-70B, Phi-4, Qwen-2.5-7B, Yi-1.5-34B.
- **Numbers** (Cohen's κ with experts):

  | Reference | κ |
  |---|---|
  | Human | 0.69 |
  | Self | 0.61 |
  | Random | 0.50 |
  | None | 0.46 |
  | **Deliberately wrong** | **0.21** |

  - With a wrong reference, false negatives are high: the judge follows the wrong reference and fails correct
    answers. It overrules the reference only inconsistently.
  - With self-references on questions GPT-4o itself got wrong, pairwise agreement drops 0.86 → 0.16.
- **Against the thesis.** *Agrees directly.* A wrong reference is worse than none, and the judge follows it.
  This is the thesis's 0.26 (and CONSENSUS-FIT's 2.7:1) in another domain.

**Reconciliation (the key SQ2 contradiction).** The two papers bracket a single variable: does the judge
independently know the answer?
- Lee et al.'s conflicts are on popular, stable, easy facts (baseline accuracy about 96%). There the judge's
  belief is strong and wins.
- Krumdick et al.'s items are hard expert questions. There the reference is the judge's only belief and wins.
- The thesis's MMLU-Pro and GPQA items are in the second regime. JudgeBench [V] says strong judges are near
  chance on hard pairs, which is consistent with this.

Suggested sentence:
> "Whether a judge follows or overrides a wrong reference depends on whether it can solve the item itself.
> Judges override swapped references on popular, well-known facts [Lee et al. 2026] but follow wrong references
> on hard expert questions [Krumdick et al. 2025]. Our 0.26 fidelity under wrong references places MMLU-Pro and
> GPQA in the second regime."

Testable at zero calls **if** the judge model's own solves are cached. Split the wrong-reference matches by
whether the judge's own solve is correct. Prediction: fidelity under a wrong reference is well above 0.26 where
the judge solves the item, and near or below 0.26 where it does not. Without cached judge solves this costs
calls (one solve per item, not per match), so a cost-estimator pass is needed first.

**Kranti & Vajjala (2026), arXiv:2607.12885 [V\*].**
- **Setup.** Pointwise; TyDi QA and MATA; judges Gemini-3.1-Flash-Lite, Qwen3-32B, Gemma3-27B.
- **Numbers.** Without a reference the judges over-credit. Adding the reference flips verdicts at rates of
  0.12–0.37 (English), 0.07–0.60 (Arabic) and 0.69–0.85 (Telugu). Human alignment rises 0.34 → 0.86.
  Reference position also matters (0.05–0.15).
- **Against the thesis.** *Complements, does not contradict.* In a **pairwise, dual-order, TIE-on-flip**
  protocol, "too generous" becomes "both answers look acceptable". That makes the verdict order-sensitive, and
  under the flip rule it becomes a TIE.
  - So the thesis's finding that no-reference costs 16pp **mostly as TIEs** (82/97), while decisive-both-arms
    lose only 2.9pp, is the pairwise face of Kranti & Vajjala's pointwise over-crediting.
  - Sentence: "Without a reference the judge does not mostly pick the wrong answer; it stops deciding, as
    pointwise over-crediting [Kranti & Vajjala 2026] predicts for a protocol that converts order-inconsistent
    verdicts into ties."
- Their position-of-reference effect is relevant to the RP20 template result (a false reference sentence is
  equivalent within ±4pp). The thesis can say that a false *mention* of a reference does not move verdicts,
  whereas reference *content* does.

**JudgeBench [V]; Stephan et al. 2024, arXiv:2409.04168 [V, pass 1]; Zheng et al. 2023 [V].** Unchanged from
pass 1, except that the solve/verify correlation stays [S] (§1). Zheng et al. is the origin of
reference-guided grading for math.

### 2.3 Position bias, ties, abstention

**Shi et al. (2025), arXiv:2406.07791 [V\*].**
- **Metrics.** Repetition stability (RS), position consistency (PC), preference fairness (PF, from −1 to +1).
- **Numbers.**
  - GPT-4: PC about 0.82–0.83, RS about 0.97. Claude-3.5-Sonnet: PC 0.82/0.76. Gemini-1.5-Pro: PC 0.62/0.84.
  - PC rises with the **answer-quality gap** (parabolic shape).
  - Length has a very weak relation to position bias.
  - Common practice is "inconsistency-as-a-tie", which is the thesis's convention.
- **Against the thesis.**
  - *Agrees.* Position inconsistency concentrates on near-equal pairs. That predicts that the 82 matches which
    became TIEs without a reference are the low-gap ones. Testable at zero calls on the K46 store, using
    correctness pairs or length difference as the gap proxy.
  - *No contradiction with the verbosity result:* Shi et al. find length does not drive *position* bias. The
    thesis's +0.39 logit per 1k characters is a *preference* (content) effect. State the distinction in one
    clause.
  - **Adopt** the RS / PC / PF names. The thesis already has RS (DECOMP 5.7% retest) and PC (the flip rate).

**Wang et al. (2023), arXiv:2305.17926 [V].** The origin of balanced position calibration (aggregating over
orders), which the thesis implements as dual order. Cite it.

**Zhao, Wang, Chen (2026), "Debiasing as a Measurement Intervention: Calibrated Ties and Resolution Loss in
LLM-as-a-Judge Evaluation", arXiv:2609.12439 [V\*]** (new).
- **What it does.** Debiasing instructions suppress citation bias (worse-cited wins fall from up to 50.5% to
  0%) but convert validated moderate-gap decisions into **Tie**.
- **Tie typology.** A tie can be a correct equivalence, a calibrated soft boundary, or resolution-destroying.
  TRACE-style decoupling recovers 96.5–100% resolution.
- **Against the thesis.** *Directly complements* the 82/97 finding. It supplies the vocabulary: removing the
  reference is a *resolution loss*, not mainly an accuracy loss.
  - Sentence: "Most of the cost of removing the reference is resolution, not direction: 82 of 97 lost matches
    become ties, in Zhao et al.'s [2026] sense of resolution-destroying ties."
  - Single-group preprint dated 2026-09-11; cite as framing only.

**Jung, Brahman, Choi (2024), "Trust or Escalate: LLM Judges with Provable Guarantees for Human Agreement",
arXiv:2407.18370 [V]** (new).
- **What it does.** Selective evaluation: the judge abstains below a calibrated confidence. Over 80% human
  agreement at about 80% coverage on Chatbot Arena.
- **Against the thesis.** The thesis's TIE-on-flip is an *uncalibrated* abstention rule. Jung et al. give the
  principled version, with a coverage/risk guarantee.
  - The frontier-order residual ("selective abstention + length", ORACLE) should be framed with this
    coverage-vs-agreement trade-off.
  - Zero-call adoption: report the thesis's fidelity as a risk-coverage curve, with TIE as abstention.

### 2.4 Tree vs flat clustering

- **Moseley & Wang (2017) [V].** Under the revenue form of Dasgupta's objective, average linkage is a small
  constant approximation and bisecting k-means is poor; good divisive algorithms exist. *Relevance:* the
  thesis's −2.2pp against class-conditioned k-means is a filing metric, not a hierarchy objective. A
  Dasgupta-revenue comparison (tree vs average-linkage HAC vs gold hierarchy, on the same similarity graph)
  separates "a bad hierarchy" from "a good hierarchy that files badly". Zero calls, CPU.
- **Avengers (Zhang et al. 2025), arXiv:2505.19797 [V\*]** (new; AAAI 2026 per the GitHub README [S]).
  - **Setup.** Embed with gte-qwen2-7B → k-means (default K = 64) → per-cluster model scores → routing plus
    repeated-sampling vote; 10 ~7B models, 15 datasets.
  - **Ablations.** Across K-Means, hierarchical, GMM, spectral and BIRCH, performance is 70.04–70.71. Across
    five embedders it is 70.28–70.70. It beats GPT-4.1 for K from about 14 to 140.
  - **Routing alone.** The HTML reports Best Single 69.59 vs 70.54. The voting step carries much of the
    headline. Re-check the table before quoting.
  - **Against the thesis.** *Agrees:* for routing, the partition algorithm and the embedder barely matter. That
    is exactly why the tree's cells and the declared domains give the same gain. It also supplies the external
    "k-means is a hard baseline" citation that Petukhova et al. turned out not to support. Adopt a K-sweep
    k-means routing baseline (§5 item 8).
- **PERCH (Kobren et al. 2017) [V].** Dendrogram purity, unchanged from pass 1. Note that the abstract says
  PERCH is "comparable or better than flat clustering". So tree vs flat being a near tie is normal in this
  literature.

### 2.5 Certification: SigClust, SHC, selective inference, stability

- **Huang, Liu, Yuan, Marron (2015), JCGS 24(4):975–993 [V].** The original SigClust eigenvalue estimate
  gives **severe type-I inflation when a few eigenvalues are very large**; soft thresholding fixes it.
  - *Relevance.* Embedding spectra are spiked (low isotropy; Tsukagoshi & Sasano [V]). An isotropic or
    under-fitted null *over-certifies*. The thesis certifies **nothing** (0/60), so its null is not on the
    over-certifying side.
  - The open question the thesis must address is **power**: MMLU-GOLD-GEOMETRY shows the declared level is
    geometric (H 0.29 vs p95 0.026), yet the construction certifies none of it. Suggested sentence (with one
    clause added if the positive control is run):
    > "The certificate is conservative by construction: SigClust-type nulls fitted to a spiked spectrum
    > over-certify unless the spikes are carried in the null [Huang et al. 2015]. Ours carries them and
    > certifies no top-level site, although the declared level is measurably geometric (H 0.29 vs p95 0.026).
    > The certificate therefore bounds false discovery, not recall."
  - Positive control (CPU only): put the *declared* level through the same site null. If it is not
    certified, the 0/60 is a power statement.
- **SHC, Kimes et al. [V via arXiv:1411.5259].** Sequential Monte Carlo testing down the tree, with FWER
  control. The thesis uses hierarchical BH (FDR) over nested sites. Cite SHC as the closest prior art. Note
  that SHC's sequential stop ("do not descend below a failed node") would give the same 0 top-level result with
  fewer tests.
- **sc-SHC, Grabski, Street, Irizarry (2023) [S].** Standard pipelines over-cluster; significance-aware
  clustering fixes it. This supports the reading that "no certified split" is not an anomaly.
- **Gao, Bien, Witten [V]; Chen & Witten 2023 [V]; Yun & Barber (2023), "Selective inference for clustering
  with unknown variance", EJS 17(2):1923–1946, arXiv:2301.12999 [S]** (new).
  - Gao et al. show that naive tests after clustering are invalid *even with sample splitting*.
  - Yun & Barber relax the known-variance assumption.
  - *Relevance:* the thesis's site null re-runs the whole split procedure on null draws, which is a parametric
    bootstrap of the selection. Selective inference is the analytic alternative. Cite both to justify the
    choice. Do not claim the Monte Carlo null is "exact".
- **Mourer, Forest, Lebbah, Azzag, Lacaille (2023), "Selecting the Number of Clusters K with a Stability
  Trade-off", PAKDD 2023, arXiv:2006.08530 [V]** (new).
  - Principle: "a good clustering should be stable, and within each cluster there should exist no stable
    partition."
  - *Relevance:* this is the stability twin of the thesis's two properties. The tree reproduces exactly and is
    order-stable (between-cluster stability), and no site is certified (no stable within-cell partition). Cite
    it as a stability-based reading of the same stopping rule.

### 2.6 OOS detection on CLINC150

**Podolskiy et al. (2021), arXiv:2101.03778 [V\*]**, Table 2. CLINC150 has 15K train IND, 4.5K test IND and 1K
test OOD. All encoders are **fine-tuned on in-domain intent labels**. Mean of 10 runs:

| Method (CLINC150) | AUROC | AUPR-OOD | FPR@95 (OOD) |
|---|---|---|---|
| BoW + MSP | 91.5 | 66.7 | 31.7 |
| CNN + Mahalanobis | 95.2 | 76.2 | 16.4 |
| BERT-base + Mahalanobis | 97.3 | 88.6 | 10.9 |
| RoBERTa + MSP | 97.1 | 91.2 | 11.6 |
| RoBERTa + Mahalanobis | **98.4** | 94.5 | 6.8 |

The paper also describes **marginal Mahalanobis** (one ID centroid, no class labels; Kamoi & Kobayashi 2020,
[S] via Podolskiy). That is the label-free analogue of the thesis's abstention.

Related baselines:
- Zhou, Liu, Chen (2021), "Contrastive Out-of-Distribution Detection for Pretrained Transformers", EMNLP 2021,
  arXiv:2104.08812 [V]: contrastive fine-tuning plus Mahalanobis, "near-perfect" OOD detection.
- Zhan et al. (2021), "Out-of-Scope Intent Detection with Self-Supervision and Discriminative Training", ACL
  2021, arXiv:2106.08616 [V]: synthetic outliers.
- ADB (Zhang, Xu, Lin 2021) [S].

**Against the thesis.**
- *Complements, with a strong positioning.* A **label-free, frozen-embedder** abstention at AUROC 0.974 sits
  between supervised fine-tuned BERT-base Mahalanobis (97.3) and RoBERTa Mahalanobis (98.4), and well above
  BoW MSP (91.5).
- Two caveats must be stated:
  1. The thesis's "curated OOS" must be Larson et al.'s OOS split for the numbers to be comparable. If it is
     not, the comparison is only indicative.
  2. 0.974 cannot be credited to the tree until a marginal-Mahalanobis or max-cosine-to-centroid score on the
     *same frozen embedder* is reported. If that baseline also gives about 0.97, the credit belongs to the
     embedder geometry.
- Sentence (only after the baseline): "Label-free abstention on a frozen embedder reaches AUROC 0.974 on
  CLINC150 OOS, within about one point of supervised, fine-tuned Mahalanobis detectors (97.3–98.4)
  [Podolskiy et al. 2021]; a label-free marginal-Mahalanobis score on the same embedder reaches X."

### 2.7 Embedders: truncation, quantisation, prompts

- **Tsukagoshi & Sasano (2025) [V].** Clustering and classification survive truncation to under 0.5% of
  dimensions; clustering embeddings have lower intrinsic dimension and are less isotropic.
  - *Agrees* with the thesis's dimension check (gemma's edge survives truncation).
  - The apparent tension with "fine structure moves" is about granularity: MTEB clustering is scored at the
    gold level. Pass-1 item 7 stands: report the gold-level readout under truncation next to the fine one.
- **EmbeddingGemma (Schechter Vera et al. 2025) [V].** The lead persists under quantisation and truncation on
  MTEB. *Agrees* with "gemma's edge survives dimension and quantisation checks". The thesis extends the claim
  from benchmark averages to gold-label partition geometry. Partition-level quantisation tests still appear
  unpublished (pass-1 gap stands, [S]).
- **Kostiuk & Enevoldsen (2026), "One prompt is not enough: Instruction Sensitivity Undermines Embedding Model
  Evaluation", arXiv:2605.22544 [V]** (new).
  - Setup: 6 models, 11 datasets, 15 prompts per dataset. A single default prompt misstates the score
    distribution, and under adversarial prompt choice **any model can be promoted to first place**.
  - *Agrees directly* with "card prompts flip MASSIVE/CLINC to qwen3 and Banking77 to gemma". It also replaces
    the dropped 2504.16411 citation.
  - Sentence: "Embedder rankings under instruction prompts are not identified by a single prompt [Kostiuk &
    Enevoldsen 2026]; our card-prompt flips are an instance, so we report the RAW protocol as primary and the
    card protocol as a sensitivity."
  - Adopt (zero calls, local embedding compute): a small prompt distribution, for example 5 paraphrases of the
    card instruction per corpus, and report the purity spread rather than two points.
- **INSTRUCTOR (Su et al. 2023) [S].** Average-level instruction robustness. The tension is resolved by
  Kostiuk & Enevoldsen.
- **Hanley & Durumeric (2025), "Hierarchical Level-Wise News Article Clustering via Multilingual Matryoshka
  Embeddings", ACL 2025, arXiv:2506.00277 [V]** (new). Different MRL prefixes encode different granularities
  (story, narrative, theme). *Complements:* if MRL prefixes carry coarse structure first, truncation should
  preserve declared-level geometry and move fine leaves. That is a mechanism for the expected coarse-invariant /
  fine-variant split. Their models were trained for this, so for qwen3 and gemma it is a hypothesis.

---

## 3. Papers pass 1 missed (11)

| # | Paper | Mark | Why it matters |
|---|---|---|---|
| 1 | Krumdick, Lovering, Reddy, Ebner, Tanner (2025). No Free Labels: Limitations of LLM-as-a-Judge Without Human Grounding. arXiv:2503.05061 | [V\*] | A wrong reference gives κ 0.21, below no reference (0.46); judges follow wrong references. The external twin of 0.26, and half of the reconciliation (§2.2). |
| 2 | Zhang, Li, Wang, … Hu (2025). The Avengers: A Simple Recipe for Uniting Smaller Language Models to Challenge Proprietary Giants. arXiv:2505.19797 | [V\*] | k-means cluster routing; insensitive to algorithm, K and embedder. External support for "the partition does not matter for routing" and for k-means as the baseline. |
| 3 | Lu, Zhang, Zhang, Yu, Wang, Chen, Xing (2026). The Routing Plateau: Understanding the Accuracy Limits of LLM Routers. arXiv:2606.07587 | [V] | 300K queries; routers including kNN converge to a narrow band far below the oracle; more data, bigger encoders and fine-tuning add only +1.24pp. Supports "small gains" as a property of query-only routing. |
| 4 | J. Chen (2026). When Does Combining Language Models Help? A Co-Failure Ceiling on Routing, Voting, and Mixture-of-Agents Across 67 Frontier Models. arXiv:2606.27288 | [V] | Accuracy ≤ 1 − β (β = all-models-wrong rate); combining rarely beats the single best "without a strong query-level routing signal". A zero-call ceiling the thesis can compute per corpus. |
| 5 | Shihab, Al Ahsan, Swaqeeb (2026). Opportunity Is Not Realizability: Selection-Valid Diagnostics for Multi-LLM Routing. arXiv:2608.08265 | [V] | Choosing the best fixed model on the same examples invalidates paired inference. Oracle potential is 9.7–30.7pp, but routers recover 7.5–14.4% of it. The thesis selects Best Single on TRAIN and scores on EVAL, so cite this to show the design is selection-valid. |
| 6 | T.-R. Chen (2026). What Does a Routing Oracle Measure Under Stochastic Decoding? (v1 title: "How Much of the Routing Gap Is Real?"). arXiv:2607.03436 | [V] | The oracle gap depends on coupling, scorer and finite draws; 11 models × 30 draws on GSM8K / MATH-500 / GPQA-D. Methods support for treating single-draw gains with care (with Lee 2026's 5.37%). |
| 7 | Zhao, Wang, Chen (2026). Debiasing as a Measurement Intervention: Calibrated Ties and Resolution Loss in LLM-as-a-Judge Evaluation. arXiv:2609.12439 | [V] | Tie typology and resolution loss; frames the 82/97 TIE result. |
| 8 | Jung, Brahman, Choi (2024). Trust or Escalate: LLM Judges with Provable Guarantees for Human Agreement. arXiv:2407.18370 | [V] | Calibrated judge abstention with guarantees; frames TIE-on-flip as abstention, reported as risk-coverage. |
| 9 | Kostiuk & Enevoldsen (2026). One prompt is not enough: Instruction Sensitivity Undermines Embedding Model Evaluation. arXiv:2605.22544 | [V] | Prompt choice can reorder any embedder leaderboard; directly supports the SQ5 card-prompt flips. |
| 10 | Mourer, Forest, Lebbah, Azzag, Lacaille (2023). Selecting the Number of Clusters K with a Stability Trade-off: an Internal Validation Criterion. PAKDD 2023; arXiv:2006.08530 | [V] | Stability reading of "stable cells, no stable sub-partition" (§2.5). |
| 11 | Card, Henderson, Khandelwal, Jia, Mahowald, Jurafsky (2020). With Little Power Comes Great Responsibility. EMNLP 2020, pp. 9263–9274 | [V] | The standard NLP power citation for "LCB inconclusive at power 0.22". |

Also relevant, lower priority:
- Niu et al. (2026), "Routing with Generated Data: Annotation-Free LLM Skill Estimation and Expert Selection",
  arXiv:2601.09692 [V]. Label-free routing via generated queries, using hierarchical clustering (CASCAL).
- Jitkrittum et al. (2025), "Universal Model Routing for Efficient LLM Inference" (UniRoute),
  arXiv:2502.08773 [V]. Cluster-based routing with excess-risk bounds.
- Hu (2026), "Oracle Gap and Signal Fidelity", arXiv:2607.17531 [V].
- Hanley & Durumeric (2025) [V] (§2.7).
- Yun & Barber (2023) [S] (§2.5).

---

## 4. Per thesis section: what to cite, how to position, contradictions

### SQ1 USE (routing gain)
- **Cite:** LLMRouterBench; Routing Plateau; Avengers; Lee 2026 (corroborating, no holdout); Huot et al.;
  co-failure ceiling (Chen 2026); Opportunity-vs-Realizability; Zhang et al. 2026; Moayeri et al.; P2L;
  RouteLLM; RouterBench.
- **Position:** "Small, concentrated gains from query-only routing are the norm under unified evaluation
  [LLMRouterBench; Routing Plateau]. Our contribution is the *stricter comparator*: a TRAIN-fitted per-cell
  policy scored on content-closed EVAL against both Best Single (selection-valid, [Shihab et al. 2026]) and a
  declared-label policy, which published discovered-task routers do not report [Zhang et al. 2026; Moayeri et
  al. 2024]."
- **Contradiction to address:** discovered fine tasks help [Zhang et al. 2026; Avengers]. Sentence: "Reported
  gains from discovered clusters are measured against the strongest single model; against a declared-domain
  table, our label-free cells add nothing (+2.62 vs +2.67pp), consistent with the insensitivity of
  cluster routers to the partition algorithm [Avengers]."
- **MMLU-Pro zero:** frame with HSE / co-failure: an undifferentiated frontier roster leaves nothing to route.
  Compute it (§5 item 4) before writing the sentence.

### SQ2 TRUST (judge and reference)
- **Cite:** Zheng 2023 (reference-guided grading; dual order); Wang 2023 (balanced position); Shi 2025 (PC/RS/PF;
  gap-driven); Krumdick 2025; Lee et al. 2026; Kranti & Vajjala 2026; JudgeBench; Stephan 2024; Zhao 2026
  (ties); Jung 2024 (abstention); Chatzi 2024 (PPI); Haldar & Hockenmaier 2025 and JudgeSense (pass 1).
- **Position:** "Fidelity is conditional on the reference: 0.92 when it is right, 0.26 when it is wrong. A
  wrong reference is worse than none, as in expert domains [Krumdick et al.]. Without a reference the judge
  mostly abstains (TIE) rather than errs."
- **Contradictions:**
  1. Judges ignore wrong references [Lee et al. 2026] vs the thesis's 0.26. Use the reconciliation sentence in
     §2.2.
  2. Without a reference the judge is too generous [Kranti & Vajjala] vs the thesis's "TIE, not wrong winner".
     Use the pointwise → pairwise sentence in §2.2.
  3. The RP20 template result (false sentence ≈ equivalent) vs reference-position sensitivity [Kranti &
     Vajjala]. Sentence: "Position and presence of reference *content* move verdicts; a false claim that a
     reference exists, with no content, does not (equivalent within ±4pp)."

### SQ3 TAXONOMY (tree vs k-means; certificate; stability)
- **Cite:** SigClust (Liu 2008 [S]; Huang 2015 [V]); SHC (Kimes [V]); sc-SHC [S]; Gao 2024 / Chen & Witten 2023 /
  Yun & Barber 2023; Mourer 2023; Moseley & Wang 2017; Dasgupta 2016 [S]; PERCH; Avengers; EvalTree, Clio,
  TnT-LLM, BERTopic (pass 1, [S]); Rajagopalan 2021 (order invariance, [V] in pass 1).
- **Position:** "A reproducible, order-stable filer whose structure is not certified and whose filing is beaten
  by label-conditioned prototypes. The lead over unsupervised k-means is the anchors'. This matches the
  over-clustering literature [sc-SHC; SigClust] and the insensitivity of cluster routers to the partition
  [Avengers]."
- **Contradictions:**
  1. PERCH and the hierarchical-clustering literature present trees as competitive with flat clustering; here
     the tree loses 2.2pp to class-conditioned k-means. Sentence: "The comparator is label-conditioned; against
     unsupervised k-means the anchored tree leads, and that lead is attributable to the anchors, not to the
     hierarchy."
  2. Certificate power. The declared level is geometric yet uncertified. Use the §2.5 sentence, ideally with
     the positive control.

### SQ5 INVARIANCE (embedders, prompts, perturbations, OOS)
- **Cite:** Huot 2026 (routing robustness); Kostiuk & Enevoldsen 2026; Tsukagoshi & Sasano 2025;
  EmbeddingGemma; MRL; Hanley & Durumeric 2025; MTEB/MMTEB (pass 1, [S]); Steck 2024 (cosine, [S]);
  Podolskiy 2021; Zhou 2021; Zhan 2021; ADB [S]; Larson 2019 [S]; ClusterLLM.
- **Position:** "Addresses are not invariant; decisions may be. Fine partitions move with embedder × corpus ×
  prompt, as prompt-sensitivity studies predict [Kostiuk & Enevoldsen], while coarse structure and routing
  outcomes are embedder-insensitive [Tsukagoshi & Sasano; LLMRouterBench; Avengers]. Surface perturbations move
  low-margin queries across cell boundaries, the mechanism Huot et al. identify for kNN routers."
- **Contradictions:**
  1. Truncation-robust clustering [Tsukagoshi & Sasano] vs fine instability. This is a granularity difference;
     show the gold-level readout.
  2. Instruction robustness on averages [INSTRUCTOR, S] vs card flips. Resolved by Kostiuk & Enevoldsen.
  3. OOS: supervised detectors reach 97–98 AUROC. Without a same-embedder label-free baseline the 0.974 cannot
     be credited to the tree (§2.6).

### Methods / statistics
- **Cite:** Miller 2024 (clustered SEs, power); Card et al. 2020 (power); Shihab et al. 2026 (selection-valid
  inference vs Best Single); T.-R. Chen 2026 and Lee 2026 (single-draw noise; 5.37% retest); Llewellyn et al.
  2025 (embedding-cluster random effects); Chatzi 2024 (PPI); Gao / Chen & Witten (selection after clustering).
- **Position:** "Two-stage, components-clustered intervals with measured DEFF [Miller]; Best Single is chosen
  on TRAIN, which avoids the selection-on-test bias [Shihab et al.]; null results are stated with their power
  [Card et al.]: LCB inconclusive at power 0.22."

---

## 5. Methods and baselines to adopt, ranked by value per cost

| # | Action | Cost | Value | Section |
|---|---|---|---|---|
| 1 | **Same-embedder OOS baselines** on CLINC150 (Larson split): marginal Mahalanobis (label-free), class Mahalanobis (labelled upper bound), max-cosine to k-means centroids. Report next to 0.974 and the Podolskiy table. | zero-call, CPU minutes | High: decides whether 0.974 credits the tree or the embedder | SQ5 |
| 2 | **Split wrong-reference matches by the judge's own solve** (right/wrong) to test the Lee-vs-Krumdick reconciliation. | zero-call if judge solves are cached; otherwise paid, one solve per item (price it first; the 4k rule applies to matches, not solves) | High: turns the main SQ2 contradiction into a result | SQ2 |
| 3 | **Decision-level robustness for SLOTSWAP** (Huot metric): share of swapped queries whose *routed model* is unchanged, next to the cell-level S 0.760. | zero-call | High: supports "addresses move, decisions stay" | SQ5/SQ1 |
| 4 | **HSE and the co-failure ceiling (1 − β) per corpus** from the existing correctness matrix. | zero-call | Medium-high: explains the MMLU-Pro zero and the BBH concentration with a label-free predictor | SQ1 |
| 5 | **Position consistency by quality gap on the K46 store** (Shi): are the 82 new TIEs low-gap pairs? Report RS / PC / PF. | zero-call | Medium-high: grounds "resolution loss" | SQ2 |
| 6 | **Certificate positive control:** put the declared level (and a planted split) through the site null. | CPU only, no calls; one null run at a time | Medium-high: turns 0/60 into a stated power property | SQ3 |
| 7 | **Prompt distribution for embedders** (5 card-instruction paraphrases per corpus; report the purity spread). | zero-call; local embedding compute | Medium: SQ5 claim as a distribution, per Kostiuk & Enevoldsen | SQ5 |
| 8 | **Avengers-style k-means routing baseline** with a K sweep (about 14–140) on TRAIN → EVAL, scored like G14. | zero-call (reuses outcome matrix) | Medium: places tree / declared / flat clusters on one axis | SQ1/SQ3 |
| 9 | **Gold-level vs fine-level readout under truncation** (pass-1 item 7). | zero-call | Medium: dissolves the Tsukagoshi tension | SQ5 |
| 10 | **Risk-coverage curve** with TIE as abstention (Jung et al.). | zero-call | Medium-low: framing | SQ2 |
| 11 | **PPI rank-sets** combining gold or checker outcomes with judged matches (Chatzi). | zero-call | Medium: calibrated leaderboard; larger write-up effort | SQ2 |
| 12 | **Dasgupta revenue and dendrogram purity:** tree vs average-linkage HAC vs gold. | zero-call, CPU | Medium-low: answers "is it a bad hierarchy or a bad filer" | SQ3 |
| 13 | **Swapped-reference arm** (Lee et al. design) on thesis items. | **paid**; likely near or above the 4,000-match rule, so it needs the author's go | High scientifically, but item 2 may answer it for free | SQ2 |

---

## 6. Not verified / caveats
- [S] only: SigClust (Liu et al. 2008); Biometrics venue for SHC; JASA venue for Gao et al.; sc-SHC (Nature
  page blocked); Cai et al. ICLR 2021; Yun & Barber 2023 (search listing plus EJS PDF link, not opened); ADB;
  Larson 2019; INSTRUCTOR; MTEB/MMTEB; Dasgupta 2016; Cohen-Addad et al.; Kamoi & Kobayashi 2020 (only via
  Podolskiy et al.); the Avengers AAAI-2026 venue (from the GitHub README title in search).
- Venues not shown on arXiv pages (keep [S]): RouterEval (EMNLP Findings), Moayeri (ICLR 2025), Wang et al.
  (ACL 2024), MRL (NeurIPS 2022), PERCH (KDD 2017).
- HTML-derived numbers (Huot, LLMRouterBench, Lee et al., Krumdick, Kranti, Shi, Avengers) came through a
  summarising fetch. Check them against the paper's tables before quoting. The Avengers "routing alone"
  comparison especially needs checking.
- arXiv:2607.03436 changed its title between versions; cite the v3 title with the version.
- Pass-1 entries not re-opened here (Stephan, JudgeSense, Rating Roulette, Llewellyn, Okamoto, EvoTaxo,
  Rajagopalan, Anderson) keep their pass-1 marks.
