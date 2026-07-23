# TaxoArena Thesis — Gap and Contradiction Report

Scope: `report/03_Content/1_Introduction.tex` … `8_Conclusion.tex`, plus appendices
`7_Appendix_TuningProtocol.tex`, `8_Appendix_JudgeGeneration.tex`,
`9_Appendix_MetricDefinitions.tex`, `10_Appendix_ModelRoster.tex`,
`11_Appendix_DAGConstructionFormalism.tex`, `0_Appendix.tex`, `main.tex`.
"Current implementation" refers to the implementation as of 2026-07-23 (EMA removed;
temperature-1 vMF softmax with `membershipFloor=0.10`; chance-corrected separation
score replacing Dasgupta delta and JS-divergence gates; unconditional passthrough
collapse below depth 1; iteration-1 trickle skip; Banerjee+Hornik–Grün+Newton–Raphson
kappa with parent-anchored EB blend; fixed 256-dim fit with PCA-projected 32/64/128
split clustering; canonical config `separationEpsilon=0.01, minClusterSize=50,
maxDepth=8, membershipFloor=0.10, maxLeafAssignments=5, numIterations=35`;
domain-granularity Routing ECE; GED-based Stabilizer with streak-of-5).

Severity legend: **HIGH** = must fix before submission; **MED** = should fix; **LOW** = polish.

---

## 1. Critical Contradictions (must fix before submission)

### 1.1 [HIGH] 42 of ~60 cited bibliography keys do not exist in `Bibliography.bib`
- Location: `report/05_Literature_and_Index/Bibliography.bib` (24 entries) vs. citations across all content chapters.
- Full missing list: arena2025categories, balduzzi2018melo, chen2016bladechest, chen2023frugalgpt, chen2024verbosity, chiang2024chatbotarena, databricks2025memalign, deng2024contamination, elo1978rating, fuzzyhc1969, haidemariam2025turn, heckel2019activeranking, herbrich2007trueskill, huang2020corel, huang2025thinkj, jamieson2011activeranking, joshy2024openskill, kosmopoulos2015hmetrics, li2024verbosity, li2026agencybench, liang2022holistic, liu2024probabilistic, meimandi2025positioning, ong2024routellm, ostasiewicz2022evaluation, polyhierarchy2006, pwc2025survey, raju2024constructing, shukla2025evaluating, simmering2025benchmarks, somerstep2025uniroute, suzgun2022bigbench, wataoka2025selfpreference, weng2011bayesian, white2024livebench, wissuchek2025agentic, yan2025evaluation, zhang2018taxogen, zheng2023judging, zheng2024judging, zhu2023hitin, zhuang2024embedllm.
- Fix: add all missing entries. While doing so, check whether `zheng2023judging` and `zheng2024judging` are the same paper (the MT-Bench/Chatbot-Arena judging paper is NeurIPS 2023) — Ch. 2 cites both keys for what appears to be the same self-agreement result.

### 1.2 [HIGH] Exclusive vs. multi-assignment routing during construction
- Locations: `1_Introduction.tex:238-240` ("During construction each query is assigned exclusively to one sibling per depth, keeping the vMF and NiW distribution fits statistically clean"); `1_Introduction.tex:259-261` ("Unlike the exclusive routing used during construction…"); `2_Literature.tex:309-312` ("query assignment during distribution fitting remains exclusive, so that the concentration estimates at each node stay clean"); `11_Appendix_DAGConstructionFormalism.tex:107` ("construction routing is exclusive") and `:516-521` ("Primary assignment … remains exclusive at every depth").
- Current implementation admits *every* child whose posterior responsibility ≥ `membershipFloor` (0.10) — weighted multi-membership during construction, real normalized trickle weights feeding leaf memberships. The "exclusive routing keeps the fits clean" argument, used as a differentiator against soft clustering in Ch. 2 and part of Contribution 1, is no longer true as stated.
- Fix: rewrite around the actual mechanism; if a "primary leaf" (argmax) concept survives, state precisely what is exclusive (primary-path bookkeeping) vs. weighted (fitting).

### 1.3 [HIGH] Construction stopping: "no early-stopping gate" vs. GED Stabilizer streak
- Locations: `4_Methodology.tex:194-199` ("there is no structural early-stopping gate in construction, and the structural edit distance … is reported as a convergence *diagnostic* … rather than a stopping criterion"); `11_Appendix:194-197` ("Construction termination is budget-based rather than criterion-based"); `3_System_Architecture.tex:298-301` (Phase 6).
- Current implementation has a GED-based Stabilizer tracking consecutive no-structural-change iterations (streak of 5). If the streak *terminates* construction early, all three passages are false; if it only flags, the passages should still mention the streak mechanism (text describes a per-iteration edit distance of "node-level events", not GED, and no streak counter).
- Fix: verify in code and make all three passages agree, including the streak length.

### 1.4 [HIGH] Bridge coherence gate: 0.70 in one section, 0.92 in another
- `11_Appendix:435-437` ("coherence gate rejecting edges where the resulting secondary membership would push $L'$'s internal coherence below $0.70$") vs. `:585-588` (same gate, "below the \texttt{fusionSimilarityThreshold} (default $0.92$)"). Same Source-B gate, two thresholds, same appendix.
- Fix: pick the code's value; use one number/parameter in both places.

### 1.5 [HIGH] Escape-valve unit mismatch: logical comparisons vs. judge calls
- `3_System_Architecture.tex:490-491` ("$B_{\max}$ total **logical comparisons**") vs. `4_Methodology.tex:192-193` ("$B_{\max}$ total **judge calls**"). Factor-2 difference under dual-call; Limitation 5 (`3_…:697-707`) already standardizes on $B_{\text{logical}}$.
- Fix: use $B_{\text{logical}}$ in both chapters.

### 1.6 [HIGH] Upward aggregation: Intro promises fractional 1/k; Ch. 3/4 make primary-path primary
- `1_Introduction.tex:259-264` ("verdicts attributed fractionally ($1/k$ per leaf …) **when aggregating upward through the DAG**") vs. `3_…:523-531` and `4_…:201-215` (primary-path convention is the primary analysis; fractional weighting only a sensitivity check). The Intro conflates leaf-level 1/k verdict weighting for multi-assigned held-out queries (`3_…:391-396`) with leaf→ancestor aggregation.
- Fix: separate the two mechanisms in the Intro, matching Ch. 3.

### 1.7 [MED] Residual nodes: "excluded from arena evaluation" vs. "evaluable membership"
- `3_…:354-358` (Residual node type "excluded from arena evaluation") vs. `11_Appendix:419-425` and `:573-578` (Source-A bridges give "the residual node evaluable membership").
- Fix: state the actual rule ("excluded unless Source-A bridging assigns secondary members…").

### 1.8 [MED] Two incompatible construction-routing descriptions *within* Appendix 11
- `:101-104` (Phase 3: routes "using NiW posterior predictive scores under a dynamic-temperature softmax") vs. `:460-470` (softmax "combining the vMF concentration term with the NiW posterior predictive"). NiW-only vs. vMF×NiW product — contradictory even before implementation drift; both stale (see §2).

### 1.9 [MED] Symbol collision: Δρ = migration *rate* and Δρ = fidelity *difference*
- `11_Appendix:181-186` ("migration rate $\Delta\rho_{D_k}$" — a set-size ratio) vs. the RQ2 metric $\Delta\rho=\rho_{\text{adapted}}-\rho_{\text{canonical}}$ (`1_Intro:291-293`, `4_Meth:221-224`, `5_Exp:34`). Appendix 7:29 also lists "$\Delta\rho_{\text{total}}$" as a Pareto tuning objective — ambiguous between the two senses; if it were the fidelity metric, tuning on it would contradict the no-leakage claim at `7_…:90-94` (presumably it is migration volume — say so).
- Fix: rename the migration rate (e.g. $m_{D_k}$); disambiguate $\Delta\rho_{\text{total}}$.

### 1.10 [MED] DQ1 metric list disagrees between Intro and Ch. 5
- `1_Intro:299-301` lists five diagnostics (no Dendrogram Purity) vs. `5_Exp:40-41` and `:297-300` list six (with it). Fix: align.

### 1.11 [MED] RQ2's primary metric is Spearman-based while Ch. 5 demotes Spearman
- `1_Intro:290-293` / `5_Exp:33-34` (Δρ, a Spearman difference) vs. `5_Exp:310-316` ("Kendall τ is the preferred primary rank-agreement statistic … Spearman ρ retained only for continuity"). Fix: define RQ2 on Δτ (Δρ secondary), or justify the asymmetry.

### 1.12 [MED] Footnote says "four diagnostic bridge-export parameters" but lists three
- `5_Exp:71-76` (`secondaryMassFloor`, `bridgeSupportFloor`, `bridgeSupportRelFraction`). Fix count or add the fourth.

### 1.13 [LOW] Domain count / roster consistency (recorded, no action)
- "14 domains" consistent throughout; no "13" anywhere; "Other" never discussed — one sentence in §5.3 should state whether the incoherent "Other" category is kept as a geometric anchor. 12-model roster consistent; 2,640 = 66×20×2 correct (`5_Exp:167-169`); seeds {42,137,2048} consistent; d/N arithmetic (5.12, N≈26) correct.

---

## 2. Stale Mechanism Descriptions vs. Current Implementation (by chapter)

### Chapter 1 — Introduction
- **[HIGH] :233-236** — "recursively split under a **Dasgupta cost oracle**~\parencite{dasgupta2016cost}". Gate is now the chance-corrected separation score $s = 1 - W_{\text{obs}}/\mathbb{E}[W_{\text{rand}}]$, $W(S)=|S|^2-\|\sum x\|^2$. Rename; cite Dasgupta only as related work.
- **[HIGH] :238-240** — exclusive construction routing (§1.2).
- **[MED] :245-247** — "unified separation threshold governing splitting, merging, and passthrough-collapse": direction right (one score now gates splitting, merging, distinctness, residual-split viability), but passthrough collapse is now *unconditional* below depth 1 — drop it from the list.
- **[HIGH] :342-346** — thesis-structure paragraph promises Ch. 4 formalises "the Dasgupta cost oracle, the **dynamic-temperature trickle-routing softmax**" — both gone, and Ch. 4 only summarises construction (defers to Appendix 11). Rewrite.

### Chapter 2 — Literature Review
- **[MED] :384-387** — "normalised cost-delta threshold used as a split-acceptance criterion … adaptation introduced in this thesis": criterion replaced; keep the honest framing but describe the new score.
- **[MED] :309-312** — exclusive-fitting differentiation from soft clustering (§1.2); the argument must be rebuilt on membershipFloor (bounded soft membership is closer to the fuzzy literature than admitted).
- **[LOW] :407-413** — synthesis names "(Dasgupta cost)" as the derived splitting requirement; update or soften.

### Chapter 3 — System Architecture
- **[HIGH] :108-110** (tab:requirements) — "Dasgupta cost delta as acceptance oracle". Stale.
- **[HIGH] :243-244** — "TaxonomySplitter: … via Dasgupta delta". Stale.
- **[HIGH] :280-289, :293-295** — migration "during the first construction iteration" / "cross-domain migration in the first pass only". Current: iteration 1 skips trickle reassignment entirely (GT bootstrap kept, weight 1.0; `enableGtWarmStart` off); geometric reassignment starts at iteration 2. Rewrite; redefine when the adapted partition diverges.
- **[HIGH] :195-198, :383-393** — held-out routing "using NiW posterior predictive scores" with `deltaAssign` nats walk breadth and `assignmentCosineGap`·κ_eff leaf qualification. Current: single `membershipFloor` (admission, cumulative-path bound, residual trigger); no κ-adaptive margin, no deltaAssign. Rewrite. (Whether arena-time routing still differs from construction-time — the NiW-vs-vMF asymmetry story — must be re-verified against code.)
- **[MED] :296-298** — Phase-5 operation list survives, but the named gates behind merge/collapse changed (unified score; unconditional passthrough).
- **[MED] :678** — "$\delta_{\text{drift}} = 0.02$" appears nowhere else in the document; verify it still exists in code, else delete.

### Chapter 4 — Formal Foundations
- **[HIGH] :11-13, :97-99, :265-269** — "Dasgupta splitting oracle … dynamic-temperature trickle-routing softmax". Stale.
- **[HIGH] :91-96** — "softmax over the **combined vMF/NiW score** … at evaluation time NiW posterior predictive alone". Construction half definitely stale (temperature-1 softmax of each child's own vMF log-density + membershipFloor); evaluation half needs code verification.
- **[HIGH] :171-172** — "distinct from the centroid \texttt{emaAlpha} of Section~\ref{sec:meth-vmf}". emaAlpha removed; delete the sentence. (Note: `sec:meth-vmf` does resolve — it lives in Appendix 11:212 — so this is stale content, not a broken ref.)
- **[MED] :192-193** — B_max "judge calls" (§1.5).
- **[MED] :253-256** — "checked via the Dasgupta split test" → rename.

### Chapter 5 — Experimental Setup
- **[HIGH] :78-101 (tab:hyperparams)** — contains four removed parameters (line 90 τ=1.5; line 91 γ; line 92 assignmentCosineGap 0.15; line 93 deltaAssign 1.0; line 95 emaAlpha 0.7) and **omits membershipFloor=0.10 entirely** (absent from the whole thesis). Line 89's ε=0.01 matches the canonical `separationEpsilon` but should be renamed. Regenerate from current `TaxonomyConfig`; consider noting code defaults differ (epsilon 0.04, minClusterSize 25, maxDepth 12) for reproducibility.
- **[MED] :116-118** — bridging pointer to `sec:meth-topology` is sound only after that appendix section is rewritten off the κ-scaled margin.

### Appendix 7 — Tuning Protocol
- **[HIGH] :10-19** — L9($3^4$) factors: `minClusterSize`, `routingSoftmaxTau`, `assignmentCosineGap`, `deltaAssign` — **three of four no longer exist**, breaking the provenance claim that the canonical config "is the output of" this protocol (`5_Exp:69-71`). Re-describe the tuning actually performed on the current parameter set (see `tuning/runs/`), or scope the L9 sweep as historical.
- **[HIGH] :87-94** — γ/τ_eff standalone ablation (A11) of a removed mechanism.
- **[MED] :102-123 (tab:ablations)** — A6 (deltaAssign×assignmentCosineGap) and A11 ablate removed knobs; A2 should mention Newton–Raphson + EB blend; A5's ε levels have changed semantics.
- **[MED] :77-84 (tab:tab-locked)** — verify `defaultKappaPrior=10.0` and `effectiveSupportFloor=2.0` still exist under the new kappa scheme.

### Appendix 9 — Metric Definitions
- **[MED] :116-132 (Routing ECE)** — generic per-decision ECE tied to "the trickle-routing softmax of Section~\ref{sec:meth-routing}". Current: **domain granularity** — leaf memberships aggregated to depth-1 ancestors, real normalized trickle weights, category-string label space. Rewrite definition to match.
- **[LOW] :34-53** — Total Dasgupta Cost is the genuine LCA metric and can stay; but ":50-53" contrasts with "the per-split δ_Dasgupta acceptance test", which no longer exists; and "dataset-independent" is a wording error (means "configuration-comparable").

### Appendix 11 — DAG Construction Formalism (largest stale surface)
- **[HIGH] :100-113** — Phase 3: NiW dynamic-temperature routing, exclusive single-child, δ_mig migration. All stale.
- **[HIGH] :143-191** — migration section: NiW scoring, δ_mig margin, "applied only in the first construction iteration". Contradicts iteration-1 skip; rewrite (RQ2's adapted-partition definition depends on it).
- **[HIGH] :227-262** — kappa: shrinkage matches, but omits the up-to-5 Newton–Raphson steps on $A_d(\kappa)=\bar r$, and describes "d/N>10 ⇒ NiW dominates + warning" instead of the parent-anchored EB blend ramping linearly in ρ=d/n from 0 (ρ≤2) to 1 (ρ≥10). Recast the d=256/n_min=50 rationale (:253-260, :313-320): at ρ≈5.1 the blend weight is ≈0.39, i.e. leaves are *partially* prior-anchored, not "comfortably below" a warning regime.
- **[HIGH] :264-295** — NiW's routing role must be re-verified (current construction routing is vMF-only); **:291-295 (emaAlpha EMA "stabiliser") must be deleted** — parameter removed, claim empirically false (amplifies oscillation).
- **[HIGH] :356-394** — old $\delta_{\text{Dasgupta}} = (N_R W_L + N_L W_R)/(N W_{\text{total}})$ formula; replace with the chance-corrected separation score and note it also gates merging/distinctness/residual-split viability. Also: split clustering runs in **PCA-projected 32/64/128 dims by cluster size** — nowhere mentioned; qualify the repeated "same 256-dimensional geometry" claims (fit fixed at 256; split proposals in a PCA subspace).
- **[HIGH] :395-457, :458-546** — `assignmentCosineGap`·κ_eff (coerced [1,100]), `deltaAssign`, `routingSoftmaxTau`, `tauKappaScalingFactor`, the depth-stratified residual gate (0.999/0.80, branching-factor scaled, `enableResidualRouting`) — all replaced by the single `membershipFloor=0.10`. Full rewrite; bridge Source-A/B structure may survive but its admission gate is the floor (":539-540 the sole basis for the bridges" is stale).
- **[MED] :547-600** — "vMF Jensen–Shannon divergence below ε_sep" merge gate and "JS below ε AND count below n_min" passthrough gate: both stale; passthrough now unconditional below depth 1 (a wrapper separates no pair — marginal improvement exactly 0; worth stating). The old text also compared a JS divergence against a normalized cost delta with the same ε — dimensionally incoherent; the unified-score rewrite resolves this.
- **[LOW] :335-337** — "(A1, Section~\ref{sec:exp-tuning-protocol})" — A1 is in `sec:appendix-ablations`.
- **[OK]** — no stale "macro-concept decomposition" text exists; ":388 always proposes exactly two children" is consistent; consider adding "oversized children are re-evaluated on the next iteration".

---

## 3. Broken / Dangling References

- **[HIGH] `app:numerics`** — referenced 8× (`1_Intro:206,346`; `4_Meth:19,127,152,280`; `11_App:262,288`), never defined; no numerics appendix file exists. Promised: log-Bessel/Debye, NiW update algebra + Student-t predictive, KDE bandwidth, full Fisher information matrix. Write it or repoint.
- **[HIGH] `app:graphnode-schema`** — `3_Arch:323`, never defined.
- **[HIGH] `app:infra`** — `3_Arch:649`, never defined. (Possibly the same intended infra appendix as graphnode-schema.)
- **[MED] `REPRODUCIBILITY.md`** does not exist at repo root, but `5_Exp:75-76` claims commit SHA and lockfile are recorded there.
- **[MED] Judge template placeholder** — `8_App:29-32` is a TODO comment ("insert the JudgePrompts.kt … once finalized"); `5_Exp:159-160` claims "the full structural template is given in Appendix~\ref{app:judge-generation}".
- **[MED] Figure 3.1** — placeholder `\fbox` (`3_Arch:148-168`), `\includegraphics` commented out.
- **[LOW] Chapter-vs-appendix wording** — `sec:meth-vmf`, `sec:meth-split`, `sec:meth-routing`, `sec:meth-topology`, `sec:meth-migration` now live in Appendix 11 but are referenced as "Section~…" from chapters (e.g. `4_Meth:172`, `5_Exp:117`); compiles, but prose will render appendix numbers — audit wording.
- **[LOW] Label reuse** — Intro's "Scope and Validity" is labeled `sec:info-separation` (`1_Intro:304`) while the actual protocol is `sec:exp-info-separation`/`tab:info-separation` in Ch. 5; refactor hazard.
- **[VERIFIED OK]** — `tab:info-separation` exists (`5_Exp:231`); all other `\ref` targets resolve; deleted files (`Guidelines.tex`, old appendices 1–6) are not referenced by `0_Text.tex`/`0_Appendix.tex`.

---

## 4. Gaps and Unfulfilled Promises

### 4.1 [HIGH] Chapters 6–8 are skeletons
- `6_Results.tex` (43 lines): intro paragraph + 13 empty (sub)section headings. Owed content promised elsewhere: construction summary; DQ1 vs. tab:baselines; structural/calibration metrics; trickle-test diagnostic (`1_Intro:355`); RQ2 C1-vs-C2; RQ1 C1; C3; judge reliability (Cohen's κ, Δ_verbosity); **aggregation-convention sensitivity** (`3_Arch:528-531`, `4_Meth:212-215`); **realised call counts** (`5_Exp:172-173`); **budget-fidelity curve** (`4_Meth:243-246`); ablations A1–A11; optional diagnostics (C4, verbosity probe).
- `7_Discussion.tex` (25 lines): all eight sections empty; owed: RQ answers, construct validity, selected-domain scope restatement (`5_Exp:60`).
- `8_Conclusion.tex` (5 lines): two empty sections; `sec:future-work` referenced from `3_Arch:80` and `5_Exp:60`; Intro promises future work on router deployment, multi-corpus transfer, online domain discovery (`1_Intro:360-362`).

### 4.2 [MED] BT complete-separation regularisation promised, never delivered
- `2_Literature.tex:629-633`: "the regularisation strategy used to handle this case is specified in Chapter~\ref{ch:methodology}". Chapter 4's BT section (`4_Meth:102-133`) contains none. Add the actual strategy or soften the promise.

### 4.3 [MED] Arena metrics claimed "already formalised" but only named
- `9_App:5-10` claims pairwise-winner accuracy and top-k Jaccard are formalised in `sec:meth-bt`/`sec:meth-validation`; `4_Meth:240-243` only names them. **Judge Cohen's κ** (`5_Exp:304-305`) and **Δ_verbosity** (one parenthetical, `7_App:174-177`) are never defined. Also `5_Exp:303-305` lists Δ_verbosity as a headline metric while `5_Exp:183-185` and Appendix 7 call the probe optional — decide its status.

### 4.4 [MED] Arena stopping constants never given values
- $f^*$, $R_{\text{stable}}$, $B_{\max}$, $U_{\min}$ are defined symbolically (Ch. 3 tab:states, `4_Meth` stopping) but valued nowhere; Ch. 5 gives only $B_{ij}=20$ and 10 rounds. The Intro promises Ch. 5 specifies "DAG **and arena** hyperparameters" (`1_Intro:347-352`). Add an arena-hyperparameter table. Appendix 7's Pareto objectives (Brier score, no-match rate, borderline rate, κ-shrinkage mean, small-leaf fraction, assignment-cap rate) also need one-line definitions.

### 4.5 [MED] `membershipFloor` absent from the entire document; depth-convention hazard
- The current router's single parameter appears nowhere, while four removed parameters are documented in detail. Add it (value 0.10; three roles). Related: implementation ECE aggregates "to **depth-1** ancestors" while the thesis fixes anchors at **depth 0** throughout — if code depths are root=0/anchors=1, every "depth-0 anchor" statement and "below depth 1" passthrough language is off by one relative to code. Pick one convention, state it once.

### 4.6 [LOW] Split-protocol: two-way vs. three-way, asserted vs. realised
- `4_Meth:34-48` formalises only $\mathcal{Q}_{\text{con}}/\mathcal{Q}_{\text{eval}}$ (two-way); `5_Exp:129-147` asserts a 60/15/25 three-way split, with a footnote conceding the runner default is 70/30 and the tuning partition is not materialised; `1_Intro:322-324` advertises the three-way partition unconditionally. Align (and give the tuning subset a symbol in Ch. 4's notation), or materialise the split.

### 4.7 [LOW] Selected-node specifics
- "one or two ex-ante-selected nodes (Math)" — fix the number/name once the run exists. Verify "Math (1,079 queries after deduplication)" (`5_Exp:126`) against the dataset cache (MMLU-Pro math is ~1,351 raw).

---

## 5. Minor Terminology and Claim-Hygiene Issues

- **[MED] "Dasgupta cost" naming.** Legitimate remaining uses: the Ch. 2 review of Dasgupta (2016) and the whole-tree Total Dasgupta Cost metric (Appendix 9, genuinely the canonical LCA-size cost). Everywhere the split/merge *gate* is called "Dasgupta" overclaims once the gate is the chance-corrected separation score, which has **no** Dasgupta optimality interpretation. Ch. 2's disclaimer style (`:384-387`) is the right template; apply it to the new score.
- **[MED] "vMF JS divergence."** `11_App:551-553, 559-561` present it as well-defined; no closed form exists for vMF JS — the code quantity was a symmetrized-KL surrogate and is **no longer a gate for anything**. If mentioned at all, name it as a surrogate and note the absence of a closed form.
- **[MED] EMA "stabiliser" claim** (`11_App:291-295`) is empirically false (oscillation amplification, hence removal). Delete; optionally report the negative result as a design lesson in the Discussion.
- **[LOW] "Residual" has two senses** — retained *queries* ("residual hits", `11_App:502-514`) vs. residual *nodes* (no-query leaves, `3_Arch:354-358`); Source-A "residual bridges" mixes both. Define or rename.
- **[LOW] "Migration"** may no longer exist as a distinct mechanism (no δ_mig, iteration-1 skip); either retire the term or redefine as "any anchor change relative to the GT bootstrap" — RQ2's framing depends on this.
- **[LOW] Ch. 4 self-description** in the Intro roadmap (`1_Intro:341-346`) doesn't match Ch. 4's actual summary-only role.
- **[LOW] "frontier models now score between 97% and 99% on MMLU"** (`2_Lit:66-68`) — verify; commonly reported frontier scores are ~88–92%.
- **[LOW] "Mistral-Large-3, accessed via an Azure OpenAI endpoint"** (`5_Exp:66-67`) — Mistral models are served via Azure AI Foundry/MaaS, not the Azure OpenAI endpoint; verify against client config.
- **[LOW] tab:rq-map RQ1 wording** "agree with the **precomputed** MMLU-Pro model ranking" (`5_Exp:24-25`) invites a leakage misreading; say "computed post hoc on held-out queries".
- **[LOW] `sec:appE-pipeline`** label is a relic of an older appendix ordering; rename.

## Suggested Fix Order
1. Bibliography (§1.1). 2. Missing appendices/placeholders (§3). 3. One mechanism-rewrite pass with the code open (membershipFloor routing, separation-score gates, unconditional passthrough, kappa NR+EB, iteration-1/migration semantics, delete EMA) — touching Intro Contribution 1, Ch. 2, Ch. 3 §§3.3/3.5/3.6, Ch. 4 summary, Ch. 5 tab:hyperparams, Appendices 7/9/11. 4. Internal contradictions (§1.2–1.12). 5. Fill Chapters 6–8 against the promise inventory (§4.1).

---

## Fix Status (2026-07-23)

Applied directly to the `.tex`/`.bib` sources; full document recompiled cleanly (pdflatex + biber), all `\ref` targets resolve.

### §1 Critical contradictions
- **§1.1 (bibliography)** — **fixed** (in two passes). Pass 1: 38 of 42 missing keys added to `Bibliography.bib` with web-verified metadata; `zheng2024judging` confirmed identical to `zheng2023judging` (Zheng et al., NeurIPS 2023) and all `.tex` citations consolidated onto `zheng2023judging`; 3 keys unresolvable (`liu2024probabilistic`, `simmering2025benchmarks`, `yan2025evaluation`). Pass 2 (author-requested trim, see "Bibliography trim" below): the 3 dangling citations were replaced/rephrased in the `.tex` sources, the unverified long tail was eliminated, and redundant citation stacks were collapsed. **Final state: 46 entries, one-to-one with citations, zero undefined-citation warnings.** Remaining `% TODO verify` annotations are metadata notes only: `arena2025categories` (thesis-prose specifics unconfirmed against the post), `databricks2025memalign` (key year vs. 2026 post date), `polyhierarchy2006` (key year vs. 2005 standard), `somerstep2025uniroute` (key name vs. actual authors Jitkrittum et al.; entry metadata correct).

### Bibliography trim (2026-07-23, second pass)
Before: 62 entries (58 cited + 6 uncited legacy − consolidations). After: **46 entries**, every entry cited, every citation resolvable.

Removed keys and justification:
- `wang2022hgclr`, `mialon2023gaia`, `cobbe2021gsm8k`, `park2023generative`, `wei2022cot`, `shinn2023reflexion` — uncited anywhere in the document (legacy entries).
- `schick2023toolformer` — citation stack collapsed at 1_Intro (tool-dispatch sentence now cites `yao2023react` alone).
- `haidemariam2025turn` — unverified-year scene-setting cite; sentence is elaboration of the preceding `wissuchek2025agentic`-sourced claim, citation dropped (1_Intro:10-16).
- `yan2025evaluation` (dangling) + `shukla2025evaluating` (unverified TechRxiv) — 1_Intro:42 rephrased as the thesis's own diagnosis (substantiated by the following sourced subsections); 1_Intro:71 aggregation-bias claim re-supported by `raju2024constructing` (rankings not stable across domains).
- `simmering2025benchmarks` (dangling) — saturation claim at 1_Intro:55 re-supported by `boubdir2024elo`, which supports the same claim in Ch. 2.
- `li2026agencybench` — tangential support for the human-annotation-cost claim (1_Intro:108); replaced by `zheng2023judging`, whose motivation section makes exactly this argument.
- `li2024verbosity` (tentative mapping) — both verbosity-bias cites (1_Intro:119, 2_Lit:482) collapsed onto the verified, peer-reviewed `chen2024verbosity` (EMNLP 2024).
- `dubois2024alpacafarm`, `wang2023large` — verbosity-bias stack at 3_Arch:707 collapsed onto `chen2024verbosity`.
- `ostasiewicz2022evaluation` (year-mismatched regional journal) — logistic-Elo formula cite (2_Lit:591) re-supported by `boubdir2024elo`.
- `joshy2024openskill` — software name-drop; Weng–Lin stack (2_Lit:648) collapsed onto the canonical `weng2011bayesian` (JMLR).
- `meimandi2025positioning` (unverifiable "positioning" framing) — sentence removed at 2_Lit:772-775, following sentence adjusted ("This line of work carries a common dependency…"); no factual claim left unsupported.
- `liu2024probabilistic` (dangling) — the "represents any pairwise stochastic preference relation" claim is from Chen & Joachims (2016) itself, already cited in the same sentence; second citation dropped (2_Lit:722).

Rephrased sentences: `1_Introduction.tex:10-16` (agentic-turn passage, citation dropped), `1_Introduction.tex:39-43` (evaluation-gap diagnosis, citation dropped), `2_Literature.tex:720-722` (blade-chest representational claim, redundant cite dropped), `2_Literature.tex:772-776` (Meimandi sentence removed, connective adjusted).

Unverified keys kept (all load-bearing, sole support for substantive named-system discussions; annotations retained in the .bib): `arena2025categories` (Arena category-pipeline discussion — genuinely tentative match), plus the three metadata-only notes listed under §1.1.

### Presentation trims (2026-07-23, author-requested)
- **Ch. 3 tab:requirements removed** — traceability boilerplate restating Ch. 2 conclusions and Ch. 3 section content; nothing referenced it. Replaced by a single prose sentence mapping gaps to components. `tab:components` and `tab:states` kept (component index and load-bearing state machine, respectively).
- **Figure 3.1 placeholder reduced** — vertical padding cut from 2×3 cm to 2×0.6 cm, width 0.92→0.8\textwidth, caption condensed to the two-lane essentials.
- **Ch. 5 tab:hyperparams moved to Appendix 7** (next to the tuning protocol that produced the values, which are pending calibration anyway); Ch. 5 keeps a pointer sentence + the manifest footnote. `tab:rq-map`, `tab:info-separation`, `tab:arena-conditions` kept in-chapter (they are the pre-registration core of the experimental design); `tab:baselines` kept for now — first candidate to move/cut if the DQ1 baselines are not run.
- **§1.2 (exclusive vs. multi-assignment)** — **fixed.** Intro Contribution 1, Intro arena paragraph, Ch. 2 §overlapping-taxonomies, App11 §polyhierarchy and §routing all rewritten: fitting uses normalized soft weights over the membershipFloor-admitted set; "primary" (argmax) is a bookkeeping convention for aggregation.
- **§1.3 (construction stopping)** — **fixed.** Verified in code (`TaxonomyEngine` + `TaxonomyStabilizer`): the GED streak **does** stop construction early — relative GED (per-iteration node/edge adds+deletes over current edge count) ≤ `gedThreshold` (0.005) for 5 consecutive iterations, after a minimum iteration count (max(5, 0.8·domains)), gated by `enableEarlyStopping` (true in canonical config). 4_Meth stopping section, App11 quiescence section, and 3_Arch Phase 6 all now state this consistently, including the streak length.
- **§1.4 (bridge coherence 0.70 vs 0.92)** — **fixed.** Both App11 places now use `fusionSimilarityThreshold` at the canonical run value 0.90 (from `thesis_canonical.toml` / run logs); Ch. 5 tab:hyperparams and App7 tab:tab-locked updated 0.92 → 0.90.
- **§1.5 (B_logical)** — **fixed.** 4_Meth now says "logical comparisons" with pointer to the B_logical/B_API distinction in §sec:arch-limits; 3_Arch already used logical comparisons.
- **§1.6 (1/k conflation)** — **fixed.** Intro now separates leaf-level 1/k verdict weighting for multi-assigned held-out queries from primary-path leaf→ancestor pooling.
- **§1.7 (residual nodes)** — **fixed.** 3_Arch Residual node type: "excluded unless Source-A bridging assigns evaluable secondary membership."
- **§1.8 (two routing descriptions in App11)** — **fixed** by the unified membershipFloor/vMF rewrite of Phase 3 and §routing.
- **§1.9 (Δρ collision)** — **fixed.** Migration rate renamed $m_{D_k}$ (App11); App7 Pareto objective renamed "total migration volume $m_{\text{total}}$" with explicit disambiguation from the RQ2 fidelity metric.
- **§1.10 (DQ1 lists)** — **fixed.** Intro diagnostics list now matches Ch. 5's six metrics (adds Dendrogram Purity, Total Dasgupta Cost).
- **§1.11 (RQ2 metric)** — **fixed.** RQ2 defined on Kendall-based Δτ (Δρ secondary) in Intro RQ2, 4_Meth aggregation, 5_Exp tab:rq-map, and App11 migration section.
- **§1.12 (footnote count)** — **fixed** ("three diagnostic bridge-export parameters").
- **§1.13 ("Other" category)** — **fixed.** One sentence added in Ch. 5 §Datasets: "Other" kept as a geometric anchor, not an arena selection candidate.

### §2 Stale mechanism descriptions
- **Ch. 1** — fixed: separation-score contribution wording (:233-236), soft-membership wording (:238-240), threshold list without passthrough-collapse (:245-247, now "splitting, merging, sibling distinctness, residual-split viability"), roadmap paragraph (:342-346, Ch. 4 described as summary + appendix deferral).
- **Ch. 2** — fixed: :66-68 MMLU claim corrected to ~88–92%; :309-312 floor-bounded soft membership (honest about proximity to fuzzy literature); :384-387 new score described with no-Dasgupta-interpretation disclaimer; :407-413 synthesis softened.
- **Ch. 3** — fixed: tab:requirements row, TaxonomySplitter row, migration/six-phase-loop passage (iteration-1 skip, emergent migration, adapted-partition definition), Phase 6 early stopping, held-out routing (data-flow item 4 and arena startup both now membershipFloor + maxLeafAssignments), δ_drift=0.02 removed (not in code).
- **Ch. 4** — fixed: intro and construction summary rewritten (kappa pipeline incl. NR + EB blend, iteration-1 skip, chance-corrected score, single routing distribution — no NiW evaluation-time asymmetry, per `TaxonomyArenaService` which reuses the trickler read-only); emaAlpha sentence deleted; "Dasgupta split test" renamed; chapter summary updated.
- **Ch. 5 tab:hyperparams** — fixed: four removed parameter rows deleted (τ, γ, assignmentCosineGap, deltaAssign, emaAlpha), membershipFloor=0.10 row added (three roles named), ε renamed "Unified separation threshold", fusion 0.90, calibration footnote + `% TODO(calibration)` added. (Code-default divergence note — code defaults ε=0.04, minClusterSize=25, maxDepth=12 — not added; can be added when values are frozen.)
- **App 7** — fixed: L9 sweep scoped as historical (three of four factors since removed), γ/A11 marked historical, A6 marked historical (rows retained), A2 description updated to NR + shrinkage + EB blend, `% TODO(calibration)` markers for the successor tuning study. A5's changed ε-level semantics **not** annotated (deferred — pending calibration). tab:tab-locked verified: `defaultKappaPrior=10.0`, `effectiveSupportFloor=2.0` still exist in `TaxonomyConfig`.
- **App 9** — fixed: Routing ECE rewritten at domain granularity (normalized leaf trickle weights aggregated onto depth-1 domain ancestors, MMLU-Pro category label space); Total Dasgupta Cost kept, contrast sentence fixed, "dataset-independent" wording corrected.
- **App 11** — fixed: Phase 3/4/5/6 walkthrough, migration section (iteration-1 skip, no δ_mig), quiescence (early stopping + streak), kappa (NR + EB blend ramp, honest ρ≈5.1 ⇒ α≈0.39 statement in both places), NiW demoted to auxiliary/diagnostic, EMA passage replaced with the negative-result statement, split section rewritten around the chance-corrected score incl. PCA 32/64/128 subspace honesty, polyhierarchy + routing sections rewritten under membershipFloor, topology section (merge under unified score, "vMF JS divergence" renamed symmetrised-KL surrogate and marked historical, redundant single-child removal stated structurally with `% TODO(calibration)`), A1 cross-ref fixed to sec:appendix-ablations. "Oversized children re-evaluated next iteration" note **not** added (split-population dynamics in flux).

### §3 Broken / dangling references
- **app:numerics** — **fixed.** New `report/04_Appendix/12_Appendix_Numerics.tex` created from code: (a) Debye log-Bessel + Lanczos log-Gamma + Bessel ratio (`StatisticsUtils`), (b) diagonal NiW updates + Student-t predictive + diagnostic role (`TaxonomyFitter`), (c) Silverman KDE bandwidth + valley weight (`BtMatchScheduler`), (d) observed Fisher information with rank-completion inversion and 1/K correction (`BtMmFitter`). `\input` added to 0_Appendix.tex; all 8 refs resolve.
- **app:graphnode-schema** — **fixed** (removed; GraphNode principal fields named inline in 3_Arch §DAG data model).
- **app:infra** — **fixed** (removed; replaced by a short inline parenthetical incl. manifest.json).
- **REPRODUCIBILITY.md** — **fixed.** Footnote now points to the `manifest.json` emitted per run (verified fields: runId, snapshotId, models, seed, testRatio, conditions, timestamps, logical comparisons, judge API calls). Note: the manifest does **not** record a commit SHA/lockfile; the original claim was dropped rather than softened.
- **Judge template placeholder (8_App)** — **deferred** (template text pending finalisation of `JudgePrompts.kt`).
- **Figure 3.1 placeholder** — **deferred** (figure asset not yet produced).
- **Section-vs-Appendix wording** — **fixed** in Ch. 5 and App 9 (all chapter-side refs to `sec:meth-*` now name Appendix~app:dag-formalism); 4_Meth's only such ref was deleted with the emaAlpha sentence.
- **Label collision** — **fixed.** Intro's Scope section relabelled `sec:intro-scope`; `sec:appE-pipeline` renamed `sec:app-dag-pipeline`; no dangling refs (verified by compile).

### §4 Gaps and unfulfilled promises
- **§4.1 (Ch. 6–8 skeletons)** — **deferred** (results not yet available; explicitly out of scope per author instruction).
- **§4.2 (BT complete-separation regularisation)** — **deferred** (arena-side but requires deciding/implementing the actual strategy; not covered by current code reading).
- **§4.3 (arena metrics only named)** — **deferred** (pending results chapter work; Δ_verbosity status decision open).
- **§4.4 (arena stopping constants unvalued)** — **deferred** (values not yet frozen; arena hyperparameter table pending).
- **§4.5 (membershipFloor absent)** — **fixed** (documented with value and three roles in Ch. 5 table, Ch. 3, Ch. 4, App 11). Depth-convention statement (root=0 vs anchors: code seeds anchors at depth 1 under a root node) — **deferred**; ECE text now says "depth-1 domain ancestors" consistent with code, but a single document-wide convention statement is still owed.
- **§4.6 (split-protocol two- vs three-way)** — **deferred** (pending materialisation of the tuning split).
- **§4.7 (selected-node specifics)** — **deferred** (pending the final run).

### §5 Terminology / claim hygiene
- **"Dasgupta cost" naming** — **fixed** everywhere the gate was meant; Dasgupta (2016) kept as related work and as the whole-tree metric.
- **"vMF JS divergence"** — **fixed** (named a symmetrised-KL surrogate, no closed form, historical, gates nothing).
- **EMA stabiliser claim** — **fixed** (deleted; negative result stated in App 11; optional Discussion write-up deferred with Ch. 7).
- **"Residual" two senses** — **fixed** (terminology sentence in App 11 routing section; residual-node rule in Ch. 3).
- **"Migration"** — **fixed** (redefined as emergent anchor change relative to the GT bootstrap; adapted partition defined at construction end).
- **Ch. 4 self-description in roadmap** — **fixed.**
- **MMLU 97–99%** — **fixed** (~88–92%, verified via current reporting; existing cite retained).
- **Mistral-Large-3 / Azure** — **fixed** (repo uses langchain4j `AzureOpenAiChatModel` against an Azure AI deployment: now "deployed on Azure AI and accessed through the Azure OpenAI-compatible client").
- **"precomputed" RQ1 wording** — **fixed** ("computed post hoc on held-out queries").
- **sec:appE-pipeline relic** — **fixed** (renamed).
