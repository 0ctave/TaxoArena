# Report Visualization Plan (2026-07-23)

Design-first plan: formats, placement, and rationale are fixed now; data is filled in
once the arena runs exist. Ranking criteria: (a) carries a headline claim (RQ1/RQ2
first, DQ1 second, mechanism third); (b) data already on disk vs pending arena runs;
(c) information density vs an equivalent table. No LaTeX is modified by this plan.

Data availability legend: **[avail]** = producible today from
`experiment_results/thesis_canonical/seed_42_determinism_C/` (+ seeds 137/2048 reruns)
or `tuning/combined_ledger.csv`; **[pending: X]** = requires run X to exist first.

---

## A. Ranked candidates

### 1. RQ1 forest plot -- arena BT ranking vs MMLU-Pro accuracy (selected node)
- **Type:** dot-with-CI forest plot, two aligned columns.
- **Placement:** Ch6 subsec. `res-c1` (Main Condition C1); the figure IS the RQ1 headline,
  accompanied by a compact table of tau / pairwise-winner accuracy / top-k Jaccard.
- **Shows:** y-axis = 12 models sorted by MMLU-Pro held-out accuracy on the selected Math
  node. Left column: BT log-strength theta with query-level bootstrap 95% CI (2,000
  resamples); right column: MMLU-Pro accuracy (binomial CI). Connecting light lines make
  rank inversions visible as crossings. Three seeds: mean dot + small per-seed ticks.
- **Why:** one glance answers RQ1 -- agreement is visible as parallel ordering, every
  inversion is an identifiable model pair. A tau number alone cannot show *which* pairs
  disagree. Highest-value figure in the thesis.
- **Data:** [pending: C1 arena run on selected Math node, seeds {42,137,2048}] --
  `ratings.db` BT vectors + `mmlu_pro_dataset_cache_v2.db` held-out accuracy.
- **Effort:** M.

### 2. RQ2 paired dumbbell -- adapted vs canonical tau per selected node
- **Type:** paired dumbbell/slopegraph with bootstrap CI on Delta-tau.
- **Placement:** Ch6 sec. `res-rq2`; replaces nothing (section is a stub), carries RQ2.
- **Shows:** one row per selected node (and per seed, small multiples if 2 nodes):
  tau_canonical (vermillion dot) -> tau_adapted (blue dot) connected by a segment;
  right margin: Delta-tau with its bootstrap CI as a small horizontal interval crossing
  a zero reference line. Secondary panel row for Delta-rho.
- **Why:** RQ2 is literally "is the blue dot right of the vermillion dot, and does the
  CI exclude zero" -- the figure makes the claim falsifiable at a glance.
- **Data:** [pending: C1 run + C2 re-aggregation of the same verdict set by MMLU-Pro label].
- **Effort:** S (once #1's data loader exists).

### 3. Pipeline overview diagram
- **Type:** two-lane block diagram (construction lane / arena lane), vector drawing.
- **Placement:** Ch3 `fig:pipeline-overview` -- replaces the existing fbox placeholder;
  caption already written in `3_System_Architecture.tex`.
- **Shows:** upper lane: corpus -> embedding (d=256 MRL) -> 14 anchor seeding -> six-phase
  loop (fit / trickle / split / topology / converge) -> frozen snapshot. Lower lane:
  held-out queries -> read-only routing -> scheduler -> dual-call judge -> BT per leaf ->
  upward aggregation -> post-hoc oracle comparison. The four SQLite stores as interface
  artefacts between lanes; the information-separation boundary drawn as a dashed wall
  (answer keys never cross into the lower lane until validation).
- **Why:** the only figure referenced by existing text; identified as missing in
  `report-quality-style-analysis.md` item 4.6. Anchors the whole architecture chapter.
- **Data:** none (structural). **Effort:** M.

### 4. DQ1 baseline comparison -- taxonomy quality vs k-means / HAC / random null
- **Type:** table (primary) + adjacent dot plot: one panel per metric, four conditions
  as dots on a common scale.
- **Placement:** Ch6 subsec. `res-baselines`; table carries exact values, dot plot the
  gestalt "above the random floor, competitive with flat clustering".
- **Shows:** rows = {TaxoArena, k-means, HAC-Ward, random null}; columns = Dendrogram
  Purity, Weighted Leaf Purity, Spherical Silhouette, Dasgupta Cost, Sackin, Routing ECE
  (mean +- sd over 3 seeds). Dot plot: metric on x, condition as labeled dot.
- **Why:** DQ1 is a prerequisite gate for RQ1/RQ2; a reader must see the induced DAG
  is not vacuous. Table dominates (6 metrics x 4 conditions is table-shaped); the dot
  plot earns its space only if metric scales allow a shared normalized axis -- else
  keep table only.
- **Data:** TaxoArena side [avail]: `validation/MAIN_taxonomy_quality.csv`,
  `MAIN_routing_calibration.csv`, ledger columns. Baselines [pending: baseline runs
  (k-means/HAC/random) on identical split + embeddings].
- **Effort:** S (table) / M (with plot).

### 5. Induced-DAG excerpt with a real cross-link bridge
- **Type:** DAG diagram (subgraph, ~12-18 nodes), tree edges solid, cross-link dashed.
- **Placement:** Ch3 sec. `arch-dag` (accompanies Node Types) or Ch6 construction
  summary; second missing figure from quality analysis item 4.6.
- **Shows:** root -> two anchor domains (the real pair from an accepted bridge, e.g. the
  host and target domains in `bridge_candidates.csv` rows with `accepted=true`) -> their
  children down to one bridged node with two parents. Node annotation: label, query
  count, residual count (from final iteration of `dag_snapshots.jsonl`); the cross-link
  edge annotated with captured-residual count. Everything else elided as "...".
- **Why:** the polyhierarchy claim ("concept-level bridge between two domains") is the
  most distinctive structural result; a real excerpt proves it exists without the
  full-DAG hairball. Uses real node ids/labels -- no fabrication.
- **Data:** [avail] final-iteration `dag_snapshots.jsonl` (parentIds/childIds/isBridge,
  directQueries, residualQueries) + `bridge_candidates.csv` (captures, accepted) +
  `validation/bridge_nodes.csv`, `bridge_residuals.csv` (ResidualDomains mix).
- **Effort:** M (graphviz/tikz from a small extraction script).

### 6. Construction convergence trajectory -- GED, structure counts, residual mass
- **Type:** small-multiples line plot, 3 stacked panels sharing the iteration x-axis.
- **Placement:** Ch6 sec. `res-construction-summary`; the section's spine.
- **Shows:** x = iteration 1..15. Panel a: derived GED to previous iteration (node +
  relation adds/removes, cross-links counted), with the 5-iteration zero-GED quiescence
  streak shaded and the freeze iteration marked. Panel b: node / leaf / bridge counts.
  Panel c: total residual-pool mass (sum of residualQueries). One line per seed (3
  thin lines + mean), same color per quantity across panels.
- **Why:** demonstrates the convergence criterion of `dag-logic-and-math.md` sec. 9
  actually bites, and that residual mass is a stabilizing measurement, not runaway
  failure. Replaces several sentences of assertion with evidence.
- **Data:** [avail] `dag_snapshots.jsonl` (15 iterations; GED derived by diffing node
  and edge sets between consecutive iterations). Seeds 137/2048: [pending: rerun of the
  canonical construction per seed -- cheap, ~2.5 min each].
- **Effort:** M.

### 7. Proposal-gate accept/reject scatter -- Delta-J vs threshold
- **Type:** scatter with a reference line, log-symmetric y-axis.
- **Shows:** x = pi_S (site mass share), y = Delta-J; marker shape by edit type (split /
  cross-link / shrink), fill = accepted, hollow = rejected; the effective threshold
  theta*pi_S drawn per edit type (0 for splits, +eps*pi for cross-links, -eps*pi for
  shrink). Rejected cross-links hugging the line illustrate the mass-scaled bar.
- **Placement:** App. dag-formalism (proposal gate section) or Ch6 construction summary.
- **Why:** the gate is the thesis's central structural-integrity mechanism; this shows
  it as a measured decision boundary rather than a described one. Mechanism rank, but
  data is already on disk.
- **Data:** [avail] `headless_run.log` `[ACCEPTED|REJECTED PROPOSAL]` lines (187 in
  seed_42): Delta J, effThreshold, pi_S. NOTE: values are locale-formatted with decimal
  commas ("0,00804") -- parser must map comma to dot.
- **Effort:** S.

### 8. Migration flow heatmap -- canonical -> adapted anchor assignment
- **Type:** 14x14 heatmap, sequential single-hue, diagonal visually de-emphasized
  (separate muted encoding) so off-diagonal migration pops; row-normalized %.
- **Placement:** Ch6 sec. `res-rq2` opening (the migration volume RQ2 depends on), or
  sec. `res-trickle`.
- **Shows:** rows = canonical MMLU-Pro domain, cols = adapted anchor; cell = share of
  the row's queries. Direct-label cells >= 2%. NOT a Sankey: 14x14 flows cross into a
  hairball; the heatmap holds the same matrix legibly (must-consider Sankey evaluated
  and rejected, see cut list).
- **Why:** RQ2 is only meaningful if migration volume is non-trivial (selection rule
  (iii) in Ch5); this shows where mass moves (e.g. Business -> Other/Economics) and
  grounds the "adapted partition" concept in one picture.
- **Data:** [avail] `validation/MAIN_migration_flow_matrix.csv`. NOTE: header contains
  "Other" twice (15 data columns for 14 domains) -- resolve/verify the duplicate column
  before plotting.
- **Effort:** S.

### 9. Ch1 routing micro-example -- two-model slopegraph
- **Type:** slopegraph (4 domain rows, two model columns), explicitly labeled
  "illustrative values". NOT a radar (see cut list).
- **Placement:** Ch1 subsec. `routing-example`, accompanying (not replacing) the text.
- **Shows:** left axis Model A, right axis Model B; four lines (Math .91/.54, Physics
  .88/.50, History .55/.92, Philosophy .51/.90) crossing at the middle; a horizontal
  dashed line at the shared aggregate 0.72 both models collapse to. The X-shaped
  crossing is the "equal on average, opposite at the margin" claim drawn.
- **Why:** the thesis's motivating intuition in one glance; a reader who sees only one
  figure of Ch1 sees the scalar-fallacy argument.
- **Data:** the numbers already printed in `1_Introduction.tex` (synthetic, declared as
  such -- no fabrication of empirical data). **Effort:** S.

### 10. Budget-fidelity curve -- tau vs cumulative logical comparisons
- **Type:** line plot, 2 lines (adaptive vs random scheduler), x = B_logical, y =
  tau against the post-hoc oracle, per-seed thin lines + mean.
- **Placement:** Ch6 sec. `res-budget` (or App. tuning-protocol, since the scheduler is
  a demoted, optional diagnostic).
- **Shows:** how quickly each scheduler's interim ranking reaches its final agreement;
  vertical marks where leaves enter CONVERGED. Expressed in B_logical (not API calls)
  per Ch3 Limitation 5.
- **Why:** carries the optional scheduler diagnostic; only figure that justifies the
  "budget efficiency" design goal. Ranked below DQ1 because the RQ is demoted.
- **Data:** [pending: C1 arena run + random-scheduler ablation run; needs per-round BT
  snapshots from `ratings.db`]. **Effort:** M.

### 11. C3 vs C1 -- judge-design contribution
- **Type:** dumbbell per metric (tau, pairwise-winner accuracy): generic-template judge
  (green) vs reference-informed judge (blue), bootstrap CIs.
- **Placement:** Ch6 subsec. `res-c3`.
- **Shows:** whether leaf-specific reference-informed rubrics move rank agreement, with
  overlap of CIs visible; same visual grammar as #2 so the two ablations read alike.
- **Why:** isolates Contribution 2's judge-design component; the only evidence against
  "any generic judge would do".
- **Data:** [pending: C3 arena run (second judge pass, same snapshot/pools)]. **Effort:** S.

### 12. Leaf-size distribution histogram
- **Type:** histogram of leaf query counts (final snapshot), log-x if skewed; vertical
  line at minClusterSize=50; per-seed overlaid steps.
- **Placement:** Ch6 subsec. `res-structural-metrics`.
- **Shows:** that the birth-floor/survival-floor mechanism yields arena-viable leaves
  (median ~90) and how much mass sits near the floor (sparse-leaf risk, Ch3 Limitation 6).
- **Why:** directly supports the "granular but not starved" leaf claim and the
  arena's ~10-queries-per-leaf feasibility argument in Ch5.
- **Data:** [avail] final iteration of `dag_snapshots.jsonl` (directQueries of leaves).
- **Effort:** S.

### 13. Calibration sweep small multiples -- L9 factors vs headline construction metrics
- **Type:** small-multiples dot plot grid: 4 factor columns (descentMargin,
  minClusterSize, secondaryMassFloor, routingBeamGamma) x 2-3 metric rows (Weighted
  Leaf Purity, Routing ECE, BridgeCount); each panel = metric vs factor level, one dot
  per run, seed as marker shade. NOT parallel coordinates (see cut list).
- **Placement:** App. tuning-protocol (hyperparameter provenance), referenced from Ch5.
- **Shows:** which factors the construction is sensitive to and why the canonical
  values were chosen; flat panels are evidence of robustness.
- **Data:** [avail] `tuning/combined_ledger.csv` (factors + all metric columns).
- **Effort:** M.

### 14. Proposal-gate flow diagram
- **Type:** compact flowchart (snapshot -> tentative apply -> no-edge early exit ->
  re-route -> Delta-J vs theta*pi_S -> commit/restore), with the three theta rows
  (split 0 / cross-link +eps / shrink -eps) as a mini-table inside the figure.
- **Placement:** App. dag-formalism proposal-gate section (third missing figure from
  quality analysis item 4.6); Ch3 references it.
- **Why:** the measured-not-predicted edit discipline is hard to hold in prose across
  three edit types; one diagram replaces a page of re-explanation.
- **Data:** none (structural; mirrors `dag-logic-and-math.md` sec. 8). **Effort:** S.

### 15. Routing reliability diagram (ECE)
- **Type:** binned reliability diagram: x = predicted routing confidence bin, y =
  empirical top-1 correctness; diagonal reference; bar underlay for bin mass; ECE and
  Brier printed in-panel.
- **Placement:** Ch6 subsec. `res-structural-metrics`, next to the ECE scalar.
- **Shows:** where the ~0.25 ECE comes from (over- vs under-confidence by bin) -- a
  scalar ECE hides the direction of miscalibration.
- **Why:** DQ1 diagnostic depth; moderate rank because it needs an export change.
- **Data:** [pending: per-bin export -- `MAIN_routing_calibration.csv` currently holds
  scalars only; add a bins CSV to the validation exporter, then rerun construction].
- **Effort:** S (plot) + S (exporter change).

### 16. Arena state-machine diagram
- **Type:** two small state diagrams (per-pair: UNSEEN->INFORMATIVE->RESOLVED/EXHAUSTED;
  per-leaf: INITIALISING->ACTIVE->CONVERGED/BUDGET_EXHAUSTED) with entry conditions as
  edge labels.
- **Placement:** Ch3 Stopping and Convergence subsection, accompanying (not replacing)
  Table `tab:states` -- the quality analysis notes the table "wants a diagram companion".
- **Why:** lowest headline value but very cheap; improves Ch3's arena-dominance balance.
- **Data:** none (structural). **Effort:** S.

---

## B. Conventions

**Color / encoding (fixed across all figures).**
- Condition palette (validated CVD-safe, Okabe-Ito subset, all six checks pass):
  **adapted / C1 = blue `#0072B2`**, **canonical / C2 = vermillion `#D55E00`**,
  **generic judge / C3 = green `#009E73`**. Never reassign these three meanings.
- Model identity is NEVER 12 hues: models are y-axis rows with direct labels (forest
  plots, dumbbells). Seeds {42,137,2048} = lightness/alpha variants of one hue plus a
  mean marker, never three new hues.
- Sequential (heatmaps, magnitudes) = single-hue blues, light->dark. Diverging
  (Delta-tau, Delta-J) = blue / neutral gray midpoint / vermillion. No rainbows.
- One y-axis per plot -- no dual-axis charts; use stacked panels with a shared x.
- Grayscale-print safety: every hue distinction is doubled by marker shape, line
  style, or direct label (the thesis may be printed B/W).

**Sizing for LaTeX A4.**
- Full-width figures: 5.9 in wide (~\textwidth at typical A4 thesis margins), heights
  2.4-4.0 in; small multiples max 3 columns. Fonts: 9 pt labels / 8 pt ticks via
  rcParams so figure text matches the 11 pt body without \resizebox scaling. Export
  vector PDF only (pdf backend, embedded fonts); no PNG rasters except the DAG excerpt
  if graphviz-rendered (then 300 dpi minimum, prefer PDF there too).

**Tooling.**
- Python + matplotlib + pandas only (stdlib json for JSONL); no seaborn or styling
  dependencies. One script per figure in `tools/figures/fig_<nn>_<slug>.py`, plus one
  shared `tools/figures/common.py` (palette constants, rcParams, data-root resolution,
  decimal-comma log parser). DAG excerpt (#5) and the two structural diagrams (#3,
  #14) via graphviz DOT emitted by a script, or hand-tikz if visual control demands it.

**Reproducibility.**
- Every script reads exclusively from `experiment_results/<run>/...` and
  `tuning/combined_ledger.csv` via a `--run-dir` argument (default: the canonical
  seed-42 dir), writes to `report/Figures/fig_<nn>_<slug>.pdf`, and is deterministic
  (no random jitter without a fixed seed). A `tools/figures/make_all.py` regenerates
  every figure; figure PDFs are build artefacts traceable to the reproducibility
  tuple (corpusVersion, snapshotId, runId) named in each caption.

---

## C. Cut list -- tempting but rejected

1. **Full-DAG rendering (~100 nodes, all edges):** an unlabelable hairball; the bridge
   excerpt (#5) proves the interesting property with 15 nodes.
2. **Radar chart for the Ch1 micro-example:** area distortion and axis-order artifacts;
   the slopegraph (#9) shows the same crossing honestly.
3. **14x14 migration Sankey:** 196 potential crossing flows; the heatmap (#8) is the
   same matrix without occlusion.
4. **Residual-mass "439->285->94" trajectory across design revisions:** development
   history of superseded implementations, not a property of the evaluated system --
   belongs in `docs/` changelog prose, not a results figure (within-run residual
   trajectory is already panel c of #6).
5. **Per-leaf 12-model BT heatmap across all ~60 leaves:** per-leaf estimates are
   noisy at ~10 held-out queries; readers would over-read cell differences the CIs
   don't support. Anchor-level (#1) is the defensible resolution.
6. **t-SNE/UMAP scatter of all query embeddings colored by domain:** projection
   artifacts invite over-interpretation of cluster shapes the 256-d geometry does not
   guarantee; every structural claim is already carried by measured scores.
