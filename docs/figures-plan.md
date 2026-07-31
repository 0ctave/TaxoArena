# Figures and tables plan — six-chapter thesis

> **STATUS: SUPERSEDED (2026-07-30) by `figures-plan-v2.md`, then by `figures-plan-v3.md`.**
> The current set is 8 figures (6 main + 2 appendix). Go to v3.

Status: written 2026-07-28 against branch `tree-only`, after the six-chapter restructure
(`docs/thesis-plan-v2.md`). This plan **supersedes `docs/report-visualization-plan.md`
(2026-07-23)** in full: that plan predates the restructure and is built around metrics and
runs that no longer exist (three-seed conventions, RQ2 Δτ dumbbells, DQ1 baseline runs,
a C2 condition that was cut). No `.tex` was edited in producing this plan.

**Conventions this plan enforces on every spec below:**

1. **No invented numbers.** Every figure names its data source on disk; anything whose data
   does not exist is marked **PENDING** with the producer named.
2. **Every judge-derived Spearman ρ is shown under both tie conventions** (ties
   half-weighted / ties dropped), per rule D5. GT-only ρ (domain screen, granularity) has
   no judge ties and carries no tie convention; the caption says so explicitly instead of
   silently omitting it.
3. **Three rosters, never blurred.** Every figure states which roster its data comes from:
   *pilot* (8 models, Run A, capture-gap defect), *length-matched band* (12 models, Run B),
   *corrected band* (11 models, domain screen / Run C). Where a figure's roster does not
   match the run it informs (the screen's 11-band vs Run B's 12), the caption carries the
   mismatch, matching the `\todo` at `10_Appendix_ModelRoster.tex:65-68`.
4. **The three irreproducible figures are not visualized:** the redundancy percentages
   (72.2% / 42.2%), the correctness-blind ρ magnitude (0.74–0.76 vs recomputed 0.90–0.93 —
   only the *direction* and the tie-rate tripling may be shown), and leaf-level
   between-cell agreement presented as 0.922 without its assignment convention (0.922 holds
   on construction assignments; 0.884 on re-routed reserved-only; any figure uses the
   construction-assignment convention and names it in the caption).
5. **Construction gets at most ONE main-text visual** (the tree/certificate). Everything
   else construction-related goes to the appendices.
6. **No score-trajectory / ribbon figures.** `rank_history.csv` is half-wired: `scores` is
   zeroed in all rows and `comparisons` reads 0.0 for early rounds
   (`docs/arena-math-findings.md`, "Data and defects"). Orderings are recoverable;
   trajectories are not. Do not plan around this file.

---

## (a) Inventory of current visuals

"Placeholder" = `\fbox{\parbox{...}}` stub with a caption but no graphic.

### Main text

| # | file:line | label | what it shows | verdict | reason |
|---|---|---|---|---|---|
| I1 | `report/03_Content/1_Introduction.tex:92` | `fig:routing-slopegraph` | Placeholder. Synthetic two-model slopegraph, declared illustrative | **REWORK → F1** | Prose still references it (`:90`); cheap, pedagogically right, must stay declared-synthetic |
| I2 | `report/03_Content/3_System_Architecture.tex:89` | `tab:requirements-evidence` | R1–R4 evidence rows with caveats | **KEEP** | Carries §3.1; note the `\todo` at `:84-87` — two R1 values rest on a superseded tree and must be re-derived or left flagged |
| I3 | `report/03_Content/4_Methodology.tex:397` | `tab:meth-assumptions` | Assumptions / failure modes / diagnostics | **KEEP** | Prose table, current, load-bearing for Ch6 reading |
| I4 | `report/03_Content/5_Experimental_Design.tex:17` | `tab:rq-map` | RQ → condition → metric → link | **KEEP** | Matches the reframed RQs |
| I5 | `report/03_Content/5_Experimental_Design.tex:140` | `tab:info-separation` | Data access by pipeline phase | **KEEP** | The answer-key-blind design made concrete; F3 (diagram) complements, does not replace |
| I6 | `report/03_Content/5_Experimental_Design.tex:185` | `tab:model-roster-pilot` | Pilot roster with format + accuracy | **KEEP** | Carries the format/capability collinearity the capture-gap section needs |
| I7 | `report/03_Content/5_Experimental_Design.tex:255` | `tab:arena-conditions` | C1 / C3 / C5 deltas | **KEEP** | Current after the C2 cut |
| I8 | `report/03_Content/6_Results.tex:83` | `tab:tie-by-key` | Tie rate by key-discriminability | **REWORK → absorbed into F4** | The tripling is the headline result; a 3×2 table under-sells it; exact counts move to F4's caption/appendix |
| I9 | `report/03_Content/6_Results.tex:160` | `tab:trace-strata` | Agreement by trace stratum, both conditions | **REWORK → absorbed into F5** | Duplicates the adjacent placeholder figure; keep the counts (hits/n, ties) available in appendix numerics if the figure replaces the table |
| I10 | `report/03_Content/6_Results.tex:194` | `fig:trace-strata` | Placeholder. Dot-with-CI by stratum + capability-gap panel | **REWORK → F5** | Right design already sketched in the stub; build it |
| I11 | `report/03_Content/6_Results.tex:261` | `tab:capture-survives` | 3×3 agreement by stratum × GT-gap, with counts | **KEEP** | Compact, exact cell counts matter; F5 panel B plots its `<20pp` column but the full grid stays tabular |
| I12 | `report/03_Content/6_Results.tex:379` | `tab:c5-rho` | Run B MAIN vs C5 ρ under both tie conventions | **REWORK → absorbed into F7** | This is exactly the tie-policy-sensitivity figure the thesis needs; four numbers annotated on a figure beat a table here; keep the table only if F7 is not built |
| I13 | `report/03_Content/6_Results.tex:510` | `fig:leaf-size-hist` | Placeholder. Leaf-size histogram with floor line | **DROP from main text → appendix A-1** | Violates the one-construction-visual rule; F2 (tree) encodes leaf mass; the histogram survives in Appendix A where the birth-floor discussion lives |
| I14 | `report/03_Content/6_Results.tex:574` | `tab:rubric-null` | Four pre-registered discriminators, leaf vs random cells | **KEEP** | Directional-prediction table; a figure adds nothing over four rows with fixed predicted directions |
| I15 | `report/03_Content/6_Results.tex:639` | `tab:granularity` | Median between-cell ρ at 14/88/87/152 cells | **KEEP** | Exact medians and pair counts; F10 carries the distributions (IQR overlap) the medians cannot |
| I16 | `report/03_Content/6_Results.tex:714` | `fig:granularity-flat` | Placeholder. Box plots + centred residuals | **REWORK → F10** | The stub's design is right; the caption's own sentence ("the overlapping interquartile ranges, not the medians, carry the result") demands a figure |

### Appendix

| # | file:line | label | what it shows | verdict | reason |
|---|---|---|---|---|---|
| I17 | `report/04_Appendix/11_Appendix_DAGConstructionFormalism.tex:56` | `tab:pipeline` | Phase / class / output table | **KEEP** | Appendix-appropriate |
| I18 | `report/04_Appendix/11_Appendix_DAGConstructionFormalism.tex:698` | `fig:proposal-gate-flow` | Placeholder. Flowchart of the **lexicographic** (ΔJ, Δ\|V\|) gate | **REWORK → A-2** | The caption describes the *legacy* acceptance arm; the frozen rule is the z-gate `ΔJ > max(τ, 2·SE_paired(ΔJ))` (`thesis-plan-v2.md` Part II, App A corrections). Redraw around the z-gate or it diagrams a rule the artifact did not use |
| I19 | `report/04_Appendix/11_Appendix_DAGConstructionFormalism.tex:714` | `fig:proposal-gate-scatter` | Placeholder. ΔJ vs Δ\|V\| accept/reject scatter | **REWORK → A-3** | Data exists (`proposals.csv` has `dJ, SE_dJ, z, dV, decision`); replot in the gate's own units (ΔJ vs SE, z=2 boundary) so it shows *why* the gate is SE-denominated |
| I20 | `report/04_Appendix/7_Appendix_TuningProtocol.tex:8` | `tab:hyperparams` | Canonical hyperparameters | **KEEP** | Current (mcs=55, bar=0.025, acceptanceZ row present) |
| I21 | `report/04_Appendix/7_Appendix_TuningProtocol.tex:112` | `tab:pareto-gates` | Hard/soft selection gates | **KEEP** | Carries the routing-ECE discrepancy footnote |
| I22 | `report/04_Appendix/7_Appendix_TuningProtocol.tex:148` | `tab:tab-locked` | Locked parameters | **KEEP** (candidate to merge into I20) | Low cost |
| I23 | `report/04_Appendix/7_Appendix_TuningProtocol.tex:182` | `fig:calibration-sweep` | Placeholder. L9 small multiples over four live factors | **REWORK → A-4** | Data exists: `tuning/combined_ledger.csv` carries the four **live** factors (`proposalSeparationBar, descentMargin, minClusterSize, membershipFloor`) plus WLP/ECE/leaf-count columns. Drop the "seed encoded by marker shade" clause from the caption — the sweep is single-seed screening (seed 42) and no multi-seed convention exists |
| I24 | `report/04_Appendix/7_Appendix_TuningProtocol.tex:205` | `tab:ablations` | Ablation matrix with status prose | **KEEP** | Honest about void/historical rows |
| I25 | `report/04_Appendix/10_Appendix_ModelRoster.tex:35` | `tab:model-roster` | Run B roster from the manifest | **KEEP** | Current; retains the 5-shot / provenance / near-clone flags |

---

## (b) The proposed figure set

**Main-text figures: 12 planned = 10 buildable today + 1 foldable (F8) + 1 PENDING (F12).**
Within the ~15 budget with headroom for Run C surprises. Kept main-text tables (from the
inventory): I2, I3, I4, I5, I6, I7, I11, I14, I15.

All plotting scripts should live under `tools/analysis/` (see feasibility, §e). All judge
figures must render the tie convention in the axis/legend, not only the caption.

---

### Chapter 1 — Introduction

**F1 — Routing micro-example slopegraph** *(rework of I1, keeps `fig:routing-slopegraph`)*
- **Question answered:** why a scalar leaderboard destroys exactly the information a
  router needs — two identical aggregates, mirror-image profiles.
- **Type:** two-column slopegraph, four crossing lines (Math, Physics, History,
  Philosophy), dashed horizontal line at the shared 0.72 aggregate.
- **Data:** the synthetic values stated at `1_Introduction.tex:74-77`. **Declared
  illustrative in the caption** — this declaration already exists and must survive.
- **Roster:** none (synthetic).
- **Caption draft:** "Illustrative routing micro-example: Models A and B share an
  aggregate accuracy of 0.72 (dashed) while their per-domain profiles are mirror images.
  Values are synthetic and illustrative, not empirical."

### Chapter 3 — Method

**F2 — The frozen instrument: tree with certificate** *(the ONE construction visual)*
- **Question answered:** what the instrument is — one certified artifact, 14 anchors,
  87 leaves, sized cells — before the reader is asked to trust results attributed to it.
- **Type:** icicle (or horizontal-tree) plot of the 154-node tree: depth on one axis,
  segment width ∝ query mass, colored by top-level anchor; the single below-floor leaf
  outlined; a small stat block (154 nodes / 87 leaves / depth 6 / J = 0.253129 /
  CERTIFIED at iteration 10) set into the figure.
- **Data:** final iteration of
  `experiment_results/freeze_mcs55/seed_42/dag_snapshots.jsonl` (per-iteration `nodes`
  list) or the frozen snapshot in `snapshots.db`; certificate values from
  `experiment_results/freeze_mcs55/seed_42/fixed_point_certificate.txt`.
- **Roster:** none (construction only; no model data).
- **Caption draft:** "The frozen construction artifact: 154 nodes, 87 leaves, maximum
  depth 6, J = 0.253129, certified fixed point at iteration 10. Segment width is routed
  query mass; the one leaf ending below the birth floor n_min = 55 is outlined
  (Section 3.1.3)."

**F3 — Information-flow diagram: offline re-judging and the answer-key wall**
- **Question answered:** what this arena actually is (it re-judges stored responses) and
  where the answer-key-blind boundary sits — the two facts later results are
  unintelligible without.
- **Type:** two-lane block diagram (construction lane: corpus → embeddings → anchors →
  loop → frozen snapshot + rubrics; arena lane: held-out queries → read-only routing →
  scheduler → dual-call judge → BT per leaf → pooled roll-up), the four SQLite stores as
  interface artifacts, and a dashed wall showing eval-set answers crossing only into
  post-hoc validation. Annotate on the judge box: "sees options block; 94.8% of traces
  state their own answer" — the answer-key-blind ≠ answer-blind distinction drawn, not
  just stated.
- **Data:** structural (no run data). Contents cross-checked against
  `tab:info-separation` and `4_Methodology.tex:6-23`.
- **Caption draft:** "Offline re-judging: no response is generated during a run. Stores
  are drawn as the interfaces between construction and arena; ground-truth answers for
  held-out queries (red path) reach only the post-hoc validation stage. The judge is
  answer-key-blind but not answer-blind: it sees the options and responses that state
  their own selection."

### Chapter 5 — Results (the centre; six figures + one pending)

**F4 — What decides the verdict: agreement with the key, and the tie-rate tripling**
*(absorbs I8)*
- **Question answered:** RQ1's "what decides the verdicts" — the judge tracks answer
  correctness, and abstains precisely where the key stops discriminating.
- **Type:** two panels. (a) GT-agreement on decidable non-tied items, MAIN vs
  GENERIC_JUDGE, dots with binomial CI (88.8% / 88.4% — the 0.4-pt rubric effect visible
  as overlap). (b) Tie rate by subset (exactly-one-correct ~11% / both-correct 38.0% /
  neither-correct 33.1%), grouped by condition — the tripling is the visual event.
  Annotate n per subset (1160 / 129 / 447).
- **Data:** `experiment_results/arena_math_frozen/seed_42/judging/MAIN_verdicts.csv` and
  `GENERIC_JUDGE_verdicts.csv` — columns `CorrectA, CorrectB, Winner` suffice; no DB join
  needed (avoids the id-space hazard, rule D2).
- **Roster:** **pilot (8 models, Run A)** — caption must carry the capture-gap
  qualification: "half of the decidable support is format-decided (Section 5.1.4)".
- **Tie policy:** not applicable (proportions, not ρ); ties are the *object* of panel b.
- **Caption draft:** "The judge decides on answer correctness (Run A, pilot roster).
  (a) Agreement with the MMLU-Pro key where exactly one response is correct; the
  cell-scoped rubric moves it by 0.4 points. (b) The tie rate roughly triples exactly
  where the key stops discriminating — the signature of a correctness-driven verdict.
  Half of panel (a)'s support is format-decided (Section 5.1.4)."

**F5 — The trace inversion, before and after capability control** *(rework of I10,
absorbs I9; I11 stays as the exact-count table)*
- **Question answered:** does reasoning text help the judge match the key? No — agreement
  is highest with no reasoning at all, and the inversion *strengthens* at matched
  capability.
- **Type:** two panels of dot-with-CI. (a) Agreement by trace stratum
  (trace×trace 84.2/82.5 · mixed 89.4/88.8 · none 92.9/94.7), one series per condition;
  tie counts as small secondary marks (74 vs 17 — the independent corroboration).
  (b) The same three strata restricted to GT-gap < 20pp, MAIN
  (83.2 / 74.6 / 97.0), showing the 13.8-pt within-format gap.
- **Data:** Run A verdict CSVs (as F4) + the static model→format classification of
  `tab:model-roster-pilot` (4 traced / 4 stub); per-pair GT gap computed from per-model
  accuracy over the 241 judged questions, derivable from the verdict rows' own
  `CorrectA/CorrectB` fields (no external join).
- **Roster:** **pilot (8 models)**; caption states trace presence and capability are
  collinear in this roster and that panel (b) is the control for exactly that.
- **Caption draft:** "Reasoning text makes the judge worse at matching the key (Run A,
  pilot roster). (a) Agreement by trace stratum: highest where neither response carries
  reasoning, lowest where both do; tie counts (small marks) corroborate independently.
  (b) The inversion strengthens at matched capability (GT gap < 20 pp): 97.0% vs 83.2%.
  Exact cell counts in Table `tab:capture-survives`."

**F6 — The capture gap: format-decided comparisons, and the repair by construction**
- **Question answered:** what the pilot defect was, how big (half of all comparisons),
  and how Run B removes it by roster construction rather than post-hoc correction.
- **Type:** two panels. (a) Run A roster: per-model GT accuracy (y) vs stored-response
  length (x; stubs at 0), 8 points in two non-overlapping clusters — collinearity drawn;
  inset or annotation: on mixed pairs the judge takes the side with text 99.4% of the
  time vs GT 87.6% (+11.8pp excess), and mixed pairs are 50% of all comparisons.
  (b) Run B roster: accuracy vs median response length, 12 points, annotation
  r = +0.286 within-roster vs +0.597 across all 36 valid models.
- **Data:** panel (a): `tab:model-roster-pilot` values; lengths and accuracies verifiable
  from `mmlu_pro_dataset_cache_v2.db` (`eval_results` per `model_name` — no cross-space
  join). Mixed-pair rates recomputable from Run A verdict CSVs. Panel (b):
  `mmlu_pro_dataset_cache_v2.db` per-model median `model_output` length and accuracy for
  the 12 manifest models
  (`experiment_results/arena_math_paired/seed_42/manifest.json`).
- **Roster:** **both, explicitly side by side** — that is the figure's point. Label
  panels "pilot (8, as run, defective)" / "length-matched band (12, Run B)".
- **Caption draft:** "The capture-gap artifact and its repair. (a) Pilot roster: stored
  response length and capability are collinear — four models had no persisted text, the
  judge takes the side with text on 99.4% of mixed pairs, and mixed pairs are half of all
  Run A comparisons. (b) Run B's length-matched band controls the artifact by
  construction: length and accuracy are near-uncorrelated within the roster (r = +0.286
  vs +0.597 corpus-wide)."

**F7 — MAIN vs C5, the same data under both tie conventions** *(absorbs I12; the
honest-visual centrepiece of RQ2)*
- **Question answered:** does removing the partition change the ranking? The answer
  depends on how a tie is scored — and showing both readings *is* the result.
- **Type:** two aligned panels over identical verdicts. (a) Primary outcome: Spearman ρ
  vs GT accuracy — two rows (ties half-weighted / ties dropped), each row a MAIN dot and
  a C5 dot connected (dumbbell); right margin: Δρ against a shaded decisive band
  |Δρ| ≥ 0.007 (two grid steps at M = 12). Values annotated: 0.887/0.951 (+0.064) and
  0.916/0.923 (+0.007). (b) Secondary/high-power outcome: per-verdict key agreement
  94.2% (SE 0.7) vs 94.7% (SE 0.6) with CIs — visibly indistinguishable.
- **Data:** `experiment_results/arena_math_paired/seed_42/judging/{MAIN,C5}_verdicts.csv`
  (2,640 + 2,638 verdicts, 12 models confirmed), recomputed under both tie conventions by
  a small script (see §e, script S1); cross-check against
  `validation/{MAIN,C5}_thesis_metrics.json` and the values in `tab:c5-rho`.
- **Roster:** **length-matched band (12 models, Run B)**. Math is the pre-registered null
  arm; caption says so.
- **Tie policy:** both, as the panel structure — this figure exists to show the
  convention dependence.
- **Caption draft:** "Run B, Math (12-model length-matched band): the partition-free arm
  against per-leaf judging on an identical 250-question set. (a) Spearman ρ against
  ground truth under both tie conventions; the apparent generic-arm advantage is nine
  decisive thresholds under half-weighted ties and exactly one under dropped ties —
  nothing changes between rows except how a tie is scored. (b) The high-power statistic
  sees nothing (94.2% vs 94.7%). Math was designated the null arm in advance."

**F8 — What moves ρ: sampler × tie convention** *(foldable into F7 as a third strip if
the figure count runs tight)*
- **Question answered:** why this thesis refuses three-decimal absolute ρ — a single
  nominal condition spans 0.860–0.916 across defensible analysis choices.
- **Type:** dot strip: four points (2 samplers × 2 tie conventions) for the 12-model Math
  per-leaf arm on one ρ axis, with the M = 12 Spearman grid step (0.0035) drawn as a
  scale ruler beside the spread.
- **Data:** `ratings_math12.db` (centrality sampler) and `ratings_math12_shuffled.db` /
  `experiment_results/arena_math_12model/` + `arena_math_paired/` exports; recomputed
  under both tie conventions via script S1.
- **Roster:** **length-matched band (12 models)**.
- **Caption draft:** "Two runs of the same nominal condition (12-model Math per-leaf arm)
  under two query samplers and two tie conventions span ρ = 0.860–0.916. The ruler shows
  the Spearman grid step at M = 12; absolute ρ from this pipeline is not stable at
  three-decimal precision, and only paired within-run contrasts are quoted."

**F9 — The domain-reordering screen: law reorders, Math does not**
- **Question answered:** where an arena could detect anything at all — the offline screen
  that made Math the null arm and law the test.
- **Type:** per-domain dot plot (14 rows, sorted by p): observed within-domain-vs-global
  GT rank correlation as a dot, the permutation null's p5–median band behind it; domains
  clearing the null highlighted; law (n=287, ρ=0.955, p=0.008) and Math (n=393, ρ=1.000,
  p=1.000) called out. Annotate n per domain.
- **Data:** `tools/analysis/domain_reorder_screen.py` over
  `mmlu_pro_dataset_cache_v2.db` (verified runnable today; currently prints tables —
  needs a CSV/JSON export flag, script S2). 1,500-draw size-matched null, seed 42.
- **Roster:** **corrected band (11 models)** — and the caption must carry the standing
  roster-mismatch caveat: the band contains `arx_0314` and is not a subset of Run B's 12
  (`10_Appendix_ModelRoster.tex:60-68`).
- **Tie policy:** none — GT-only ρ, no judge verdicts involved; caption states this.
- **Caption draft:** "Offline domain screen at the 11-model band (1,500-draw size-matched
  permutation null, seed 42): within-domain ground-truth ranking against the global
  ranking. Law reorders (p = 0.008 at full 287-question coverage); Math orders
  identically to the global ranking (ρ = 1.000), which is why it is the pre-registered
  null arm. Ground-truth only — no judge verdict enters this figure. The screen uses
  MMLU-Pro's native labels, not induced cells: it bounds what a partition could show."

**F10 — Discriminative flatness across granularities** *(rework of I16; I15 keeps the
exact medians)*
- **Question answered:** link 3's premise — do finer cells carry different true rankings?
  The IQRs overlap across an eleven-fold change in cell count and across two routers.
- **Type:** two panels. (a) Box/violin of between-cell pairwise Spearman at 14 / 88 / 87 /
  152 cells (the 88 vs 87 pair is the router control — label it). (b) Centred residuals
  per granularity with the mechanical centring null −1/(C−1) drawn per group.
- **Data:** `tools/analysis/discriminative_flatness.py` over
  `mmlu_pro_dataset_cache_v2.db` + `reserved_leaf_assignments.csv` /
  snapshot assignments — must be extended to dump the per-cell-pair ρ distribution, not
  just medians (script S3). Reproduce the published row values (0.929 / 0.922 / 0.922 /
  0.905) before plotting.
- **Roster:** **pilot 8-model roster for the headline panels** (that is the published
  table's roster). The 11-band re-derivation (0.973 / 0.936) is flagged "not re-derived,
  do not cite" in `arena-math-findings.md:838-842` — do **not** add it to the figure
  until B4 of `thesis-plan-v2.md` is done.
- **Convention guard:** leaf-level values computed on **construction assignments over the
  full corpus** — the convention named in `6_Results.tex:687-691`; caption must name it
  (rule 4 above).
- **Tie policy:** none — GT-only; caption states this.
- **Caption draft:** "Between-cell agreement of ground-truth model rankings across an
  eleven-fold change in granularity (pilot roster, construction-assignment convention).
  The overlapping interquartile ranges, not the medians, carry the result; the 88- and
  87-leaf columns differ only in router. Right: residuals after centring each model's
  global mean, against the mechanical null −1/(C−1). Ground-truth only; no verdicts."

**F11 — The rubric is read, not decisive** *(optional; build if Ch5 §res-generic-judge
feels number-heavy in review)*
- **Question answered:** the mechanism behind the 99.4% winner agreement — the judge
  reproduces the rubric's vocabulary while deciding the same thing anyway.
- **Type:** paired distribution plot (box or ECDF) of per-rationale rubric-vocabulary
  overlap: MAIN 0.200 [0.115, 0.280] vs GENERIC 0.138 [0.077, 0.200]; annotation strip:
  "winner flips: 10 of 1,736".
- **Data:** rationale text is in the Run A verdict CSVs (`Rationale` column); leaf
  rubrics in `snapshots.db` (snapshot `20260727_042523`). Needs a small recompute script
  (S4) replicating the overlap measure of `arena-math-findings.md:190-208`.
- **Roster:** **pilot (8 models, Run A)** — verdict-agreement results are
  format-robust only in the sense stated in §res-generic-judge; caption carries Run A.
- **Caption draft:** "The judge reads the rubric and decides the same thing anyway
  (Run A). Rationale–rubric vocabulary overlap under MAIN sits 45% above the GENERIC
  baseline that never sees the rubric — yet the two arms flip only 10 winners in 1,736
  comparisons. Lexical overlap shows reproduction, not application."

**F12 — PENDING: the law arena (Run C), same design as F7**
- **Status: PENDING — produced by Run C**, currently executing
  (`experiment_results/arena_law_paired/seed_42/` holds diagnostics only as of
  2026-07-28; verdict and validation exports appear when it completes;
  `ratings_law_paired.db` is live).
- **Question answered:** the partition tested where it has something to be right about —
  law is the domain the screen selects.
- **Type:** identical layout to F7 (dumbbell per tie convention + high-power panel), with
  the decisive band at M = 11: grid step 6/(11·120) = 0.0046, so |Δρ| ≥ 0.009
  (pre-registered, `6_Results.tex:53-59`).
- **Data (when it exists):**
  `experiment_results/arena_law_paired/seed_42/judging/{MAIN,C5}_verdicts.csv` +
  `validation/*_thesis_metrics.json`, recomputed under both tie conventions via S1.
- **Roster:** **corrected band (11 models)** per `6_Results.tex:49-51`.
- **Caption draft (placeholder):** "Run C, law (11-model band): per-leaf against
  partition-free judging on an identical question set, under both tie conventions,
  against the pre-registered decisive threshold |Δρ| ≥ 0.009. [PENDING Run C.]"
- **Guard:** if Run C aborts or its comparison graph stays unidentified (the current log
  shows `[ARENA-BT] fit is NOT identified` warnings in early rounds), the figure slot is
  filled by a stated-in-text absence, not by a partial-run figure.

### Appendix figures

**A-1 — Leaf-size histogram** *(relocated I13)*: histogram of the 87 leaf populations,
floor line at n_min = 55, median 88 and IQR [71, 118] marked, the one below-floor leaf
highlighted. Data: final iteration of
`experiment_results/freeze_mcs55/seed_42/dag_snapshots.jsonl`. Placement: Appendix A,
next to the birth-constraint discussion. No roster.

**A-2 — Proposal-gate flowchart, corrected** *(rework of I18)*: redraw around the frozen
rule — snapshot → tentative apply → re-route → paired bootstrap SE(ΔJ) →
`ΔJ > max(τ, 2·SE)` → commit/restore — with the legacy lexicographic arm shown only as a
labelled historical branch, if at all. Structural; no data.

**A-3 — Acceptance gate in its own units** *(rework of I19)*: scatter of ΔJ vs
SE_paired(ΔJ) for all logged proposals of the canonical run, log-log, z = 2 boundary
drawn, marker by edit type, fill by decision; the 13.1× p10–p90 SE spread visible as the
x-range. Data: `experiment_results/freeze_mcs55/seed_42/diagnostics/proposals.csv`
(columns `iter,type,site_id,site_label,dJ,SE_dJ,z,dV,decision,reason,n_site` — verified).
Caption should note the gate's two empirical corroborations were tested and refuted
(§res-construction), so the figure shows coherence, not benefit.

**A-4 — Calibration-sweep small multiples** *(rework of I23)*: grid of the four live
factors × {WeightedLeafPurity, RoutingECE (flag the aggregation discrepancy), LeafCount},
one dot per L9 run. Data: `tuning/combined_ledger.csv` (live-factor columns verified
present). Single seed; remove the multi-seed caption clause.

---

## (c) Placement — section and anchor sentence

| fig | lands in | anchor phrase (quote from current text) |
|---|---|---|
| F1 | §1.1, `subsec:routing-example` | "Figure~\ref{fig:routing-slopegraph} draws this crossing directly." (`1_Introduction.tex:90`) |
| F2 | §3.1.1, `sec:arch-taxonomy`, directly after the artifact paragraph | "The resulting frozen artifact --- the single construction every result in this thesis is attributed to --- has 154 nodes, 87 leaves…" (`3_System_Architecture.tex:73-76`) |
| F3 | §3.2.1, `sec:arch-overview` | "**The arena does not query models.** … No response is produced during a run." (`4_Methodology.tex:6-11`) |
| F4 | §5.2.1, `sec:res-correctness`, replacing `tab:tie-by-key` | "the tie rate roughly triples exactly where the answer key stops discriminating." (`6_Results.tex:80-81`) |
| F5 | §5.2.2, `sec:res-trace-inversion`, replacing `tab:trace-strata` + stub | "Agreement with the answer key is \emph{highest} where neither response carries any reasoning and \emph{lowest} where both do." (`6_Results.tex:156-158`) |
| F6 | §5.2.3, `sec:res-capture-gap`, panel (b) beside "The repair" paragraph | "Half the pilot arena was decided by which side had text at all." (`6_Results.tex:238-239`); "Run~B is on the repaired corpus and on a length-matched band, so the format artifact is controlled by construction" (`:293-295`) |
| F7 | §5.2.5, `sec:res-c5`, replacing `tab:c5-rho` | "Half-weighting ties puts the generic arm ahead by nine times the decisive threshold. Dropping tied comparisons collapses the gap to exactly the threshold." (`6_Results.tex:395-397`) |
| F8 | §5.2.6, `sec:res-tie-policy` | "Two runs of the same nominal condition … span $0.860$ to $0.916$ across the combinations of query sampler and tie convention." (`6_Results.tex:429-431`) |
| F9 | §5.3.4, `sec:res-law` | "\textbf{law} reorders ($n = 287$, $\rho = 0.955$, $p = 0.008$) and \textbf{Math} does not ($n = 393$, $\rho = 1.000$, $p = 1.000$)." (`6_Results.tex:738-740`) |
| F10 | §5.3.3, `sec:res-granularity`, replacing the stub at `:714` | "It does not fall. Interquartile ranges overlap throughout." (`6_Results.tex:657`) |
| F11 | §5.2.4, `sec:res-generic-judge` | "the rubric \emph{is} read." (`6_Results.tex:311-312`) |
| F12 | §5.2.5 / §5.3.4, at the `\todo` | "Insert its results in Sections~\ref{sec:res-c5} and~\ref{sec:res-law} when it completes" (`6_Results.tex:53-55`) |
| A-1 | Appendix A, size-floor discussion | "The size floor is a birth constraint." (`3_System_Architecture.tex:204`) — appendix restatement |
| A-2 | Appendix A, acceptance-gate section | "Figure~\ref{fig:proposal-gate-flow} summarises this procedure" (`11_App…tex:695-696`) — after the gate text is corrected to the z-rule |
| A-3 | Appendix A, same section | "the gate operating as a measured decision boundary on the canonical run's proposals." (`11_App…tex:711-712`) |
| A-4 | Appendix B (merged tuning appendix) | "Figure~\ref{fig:calibration-sweep} summarises the sensitivity of the headline construction metrics" (`7_App…tex:179-180`) |

---

## (d) Drop list

| visual | file:line | reason for dropping |
|---|---|---|
| `fig:leaf-size-hist` (main text) | `6_Results.tex:510` | Violates the one-construction-visual rule; F2 encodes leaf mass; survives as appendix A-1 |
| `tab:tie-by-key` | `6_Results.tex:83` | Absorbed into F4; counts go to F4 caption |
| `tab:trace-strata` | `6_Results.tex:160` | Absorbed into F5; hits/n and tie counts preserved via `tab:capture-survives` and F5 annotations (or an appendix-numerics table if the examiner wants every n) |
| `tab:c5-rho` | `6_Results.tex:379` | Absorbed into F7 with values annotated; keep only if F7 is not built |
| `fig:proposal-gate-flow` as captioned | `11_App…tex:698` | Diagrams the legacy lexicographic gate the frozen artifact did not use; replaced by A-2 (z-gate) |
| `fig:proposal-gate-scatter` as captioned | `11_App…tex:714` | ΔJ-vs-Δ\|V\| axes bury the point; replaced by A-3 (ΔJ vs SE, z = 2 boundary) |
| `fig:calibration-sweep` seed-shade clause | `7_App…tex:186-195` | Multi-seed encoding for a single-seed sweep; A-4 keeps the grid, drops the clause |
| Everything in `docs/report-visualization-plan.md` not re-specified here | — | Predates the restructure. Specifically dead: the RQ2 adapted-vs-canonical Δτ dumbbell (premise refuted under pre-registration), the DQ1 baseline dot plot (k-means/HAC/random runs never executed, metrics cut), the three-seed forest-plot convention (seed 42 only), the C2 re-aggregation visuals (condition cut), any BT trajectory/ribbon figure (`rank_history.csv` scores column is zeroed), and any BT-CI display predating the 1/K² variance correction (all prior SEs were the floor constant) |
| Any redundancy-percentage visual (72.2% / 42.2%) | — | Irreproducible; thesis asserts no redundancy percentage |
| Any correctness-blind ρ magnitude visual (0.74–0.76) | — | Unresolved between two computations on the same verdicts; only direction + tie behaviour may be shown (already inside F4 panel b's logic) |

---

## (e) Feasibility notes

### Buildable today, data verified on disk

| fig | source verified | missing piece |
|---|---|---|
| F1 | synthetic values in `1_Introduction.tex:74-77` | plotting only |
| F2 | `freeze_mcs55/seed_42/dag_snapshots.jsonl` (keys `iteration`, `nodes` verified), `fixed_point_certificate.txt` (values verified: iter 10, 1.11e-16, CERTIFIED true) | new script `tools/analysis/plot_tree.py`; must verify per-node fields (parent/label/mass) on first read |
| F3 | structural | drawing only (TikZ or SVG) |
| F4, F5 | `arena_math_frozen/seed_42/judging/{MAIN,GENERIC_JUDGE}_verdicts.csv` — header verified: `…CorrectA,CorrectB,GroundTruth,Winner,Confidence,…,PositionFlip,TieSource,Rationale` | new script `tools/analysis/judge_mechanism_figs.py`; trace classification is the static 4/4 split of `tab:model-roster-pilot`; per-model accuracy from the verdicts' own Correct fields — **no DB join** (rule D2) |
| F6 | roster values in `.tex`; lengths/accuracy re-derivable from `mmlu_pro_dataset_cache_v2.db` per `model_name`; Run B manifest at `arena_math_paired/seed_42/manifest.json` | small query + plot; no cross-id-space join needed |
| F7 | `arena_math_paired/seed_42/judging/MAIN_verdicts.csv` (2,640 rows, 12 models — verified) and `C5_verdicts.csv`; `validation/*_thesis_metrics.json` for cross-check | **script S1** (`tools/analysis/tie_policy_rho.py`): refit BT / compute ρ under both tie conventions from a verdicts CSV; must reproduce `tab:c5-rho`'s four values before any figure ships |
| F8 | `ratings_math12.db`, `ratings_math12_shuffled.db`, `experiment_results/arena_math_12model/`, `arena_math_paired/` | S1 applied to both runs; confirm which store carries which sampler before labelling |
| F9 | `tools/analysis/domain_reorder_screen.py` runs live against the DBs (verified by execution) | **script S2**: add `--csv` export + plot; pin the 1,500-draw / seed-42 configuration that produced the published row |
| F10 | `tools/analysis/discriminative_flatness.py` exists (header verified, both rosters coded); `reserved_leaf_assignments.csv` (3,863 rows) | **script S3**: extend to dump per-cell-pair ρ (distribution), not medians only; reproduce 0.929/0.922/0.922/0.905 first; 11-band values remain do-not-cite until B4 |
| F11 | `Rationale` column in Run A verdict CSVs; rubrics in `snapshots.db` snapshot `20260727_042523` | **script S4**: replicate the overlap measure; must reproduce 0.200 / 0.138 medians before plotting |
| A-1 | as F2 | same script as F2 |
| A-3 | `freeze_mcs55/seed_42/diagnostics/proposals.csv` header verified (`dJ,SE_dJ,z,dV,decision`) | plot only |
| A-4 | `tuning/combined_ledger.csv` — live-factor columns verified (`proposalSeparationBar,descentMargin,minClusterSize,membershipFloor` + WLP/DP/ECE/LeafCount) | plot only; filter to the live-factor sweep rows (`stage == screen` vs later stages — inspect before use) |

### Pending / blocked

- **F12 (law):** blocked on Run C completing (`arena_law_paired/seed_42/` has only
  diagnostics + log as of this writing; the run is live). Producer: the running
  `HeadlessBenchmarkRunner` law config; consumer: S1.
- **F10 at the corrected roster:** blocked on B4 of `thesis-plan-v2.md` (re-derive
  flatness at the 11-band with the script committed). Until then the figure is
  pilot-roster-only, stated.
- **I2's R1 rows (within-node nulls):** the *table* ships flagged; if a figure of the
  two nulls vs the 0.025 bar is ever wanted, it is blocked on B2 (re-derive on the frozen
  mcs=55 artifact) — not planned here.
- **Any BT confidence-interval visual:** blocked on B1 (recompute every SE post-1/K²
  correction from stored verdicts). F7/F12 deliberately use ρ + proportions, not BT CIs,
  so nothing in this plan waits on B1 — but nothing in this plan may add BT error bars
  until B1 is done.

### Cross-cutting build notes

1. **Verification-before-plot rule:** every recompute script (S1–S4) must first reproduce
   the corresponding published number(s) from the `.tex`/findings doc and fail loudly on
   mismatch — this project's history (rule D2, the two screen reversals) is the argument.
2. **Joins:** all query-level joins go through query text or stay inside a single export
   file; `mmlu_pro.id` is never joined to `question_id` (`eval-id-space-repair`).
3. **Roster labels in the plotting code, not just captions:** each script takes an
   explicit roster list (the three lists are in
   `tools/analysis/discriminative_flatness.py` and the run manifests) and writes the
   roster name into the figure margin, so a regenerated figure cannot silently switch
   rosters.
4. **Un-tracked artifacts:** `tools/analysis/rubric_specificity_null.py` and
   `build/rubric_null/*` support I14 and are untracked (B3 in `thesis-plan-v2.md`);
   commit them before I14 is final. New scripts S1–S4 must be committed with the figures
   they produce.
5. **latexmk is unusable here (no perl):** figures should be produced as standalone PDFs
   by the Python scripts and `\includegraphics`'d, not TikZ-compiled inside the document
   loop, except F3/A-2 which are pure diagrams and may be TikZ.
