# Figures plan v2 — designed and built

> **STATUS: SUPERSEDED (2026-07-30) by `figures-plan-v3.md`**, which cut `margin_crossings`,
> `trace_strata` and `rho_gt_dissociation`, replaced panel (b) of
> `rubric_specific_not_decisive`, and rebuilt three scripts that this plan wrongly described
> as colour-free. 12 figures here; 8 there.
>
> Its six Δρ pairs and six screen p-values are superseded twice over (noted 2026-07-31):
> the screen values are the 11-model band, and the arena values are the M = 12 batch,
> which is no longer the results. See `docs/newlogic-rerun-record.md`.

Status: written 2026-07-30 on branch `tree-only`. **Supersedes `docs/figures-plan.md`
(2026-07-28)** in full; see §4 for what changed and why. No `.tex` was edited and nothing
was committed. Every figure specified below as buildable **has been built**: the generator
scripts are in `report/Figures/make_*.py` and each has produced its `.pdf`.

## 0. The rules these figures were built under

1. **Real data only.** Every plotted number comes from a database, CSV, or stored artifact
   on disk. The one synthetic figure in the thesis is the routing micro-example, which
   declares itself synthetic in its own caption; no second illustrative figure was added.
2. **Verify before plotting.** Every generator recomputes what it is about to draw from
   the primary source, asserts it against the registered value, prints what it verified,
   and `raise`s before any drawing on mismatch. Three of the eleven scripts caught a real
   convention problem this way during development (§3.4).
3. **Conventions are stated, never implied.** Each script carries a `CONVENTIONS` header
   block naming roster, split, tie policy, sampler, and estimator; each caption draft
   repeats the ones a reader needs to interpret the number.
4. **Grayscale- and colourblind-safe.** No figure uses colour at all. Everything is
   encoded by position, marker shape (filled circle / open square / open triangle), line
   style (solid / dashed / dotted), and greyscale fill. Deuteranopia is therefore not a
   consideration: there is no hue pair to survive.
5. **No Bradley–Terry confidence intervals anywhere.** The 1/K² recompute is outstanding,
   so every stored BT SE is the clamp constant. Where an interval appears it is a Wilson
   binomial interval on a proportion, and it says so.

### The three rosters, never blurred

| name | size | where it appears |
|---|---|---|
| **pilot** | 8 models, Run A, carries the capture-gap defect | `verdict_mechanism`, `trace_strata`, `rubric_specific_not_decisive` panel (b) |
| **12-model length-matched band** | the roster all six paired arenas ran on | `margin_crossings`, `screen_vs_arena`, `rho_gt_dissociation`, `rho_levels` |
| **11-model length-matched band** | the roster the registered domain screen ran on | `domain_screen`, and the screen column of `screen_vs_arena` |

The 11- and 12-model bands **share only eight models**. The centrepiece figure reads a
screen computed on one roster against arenas run on the other; that mismatch is stated in
its caption and in its script header, and it is a standing limitation of the design rather
than a presentation choice.

### Δρ convention, fixed everywhere

Δρ = ρ(MAIN) − ρ(C5). **Positive favours per-leaf judging.** ρ is Spearman between the
Bradley–Terry strengths fitted on that condition's verdicts and each model's ground-truth
accuracy over the questions that arena actually judged. Decisive threshold |Δρ| ≥ 0.007 =
two Spearman grid steps at M = 12 (one step = 6/(12·143) = 0.0035). Both tie conventions
are shown on every figure where a ρ appears.

---

## 1. Main-text figures (9: 7 new, 2 kept)

The centre of gravity is the judge result (three figures) and the six-domain
screen-versus-arena pattern (three figures). Construction gets exactly one.

I stopped at nine rather than padding to twelve. Every candidate that would have taken it
to twelve is in §3 with the specific thing that would make it buildable — three of them
need one registered number each, not new data.

---

### M1 — Routing micro-example slopegraph *(KEPT, already exists)*

- **Question:** why a scalar leaderboard destroys exactly the information a router needs.
- **Placement:** §1.1 `sec:motivation`, at `fig:routing-slopegraph`.
- **Type:** two-column slopegraph. Chosen because the crossing *is* the argument, and a
  slopegraph makes a crossing unmissable.
- **Data:** the synthetic values stated at `1_Introduction.tex:74–77`.
- **Generator:** `report/Figures/make_routing_slopegraph.py` → `routing_slopegraph.pdf`
- **Caption (existing, must survive):** the declaration "Values are synthetic and
  illustrative, not empirical" is load-bearing and must not be edited away. M2 is the
  empirical companion; the two should be read together.

---

### M2 — The same crossing, on real models *(NEW)*

- **Question:** does the micro-example's crossing actually happen, or is it a teaching
  device? Three of the arena roster's 66 pairs are level in aggregate and reverse at the
  margin.
- **Placement:** §1.1 `sec:motivation`, immediately after `fig:routing-slopegraph`, at the
  paragraph beginning "Per-domain rankings of real models do differ in practice"
  (`1_Introduction.tex:158–172`).
- **Type:** three small-multiple slopegraphs sharing one accuracy axis, with each model's
  aggregate accuracy drawn as a dotted horizontal line. Same visual grammar as M1 on
  purpose — the reader has just learned to read it, and the point is that the synthetic
  picture recurs unchanged in the data.
- **Data:** `model_domain_scores.csv`, `split = reserved`, column `acc`
  (written by `tools/analysis/export_gt_scores.py` from `eval_results.is_correct`).
- **Verified:** all three published swings reproduce exactly — 21.6 / 19.8 / 15.7 — and
  the selection rule returns exactly three pairs of 66.
- **Generator:** `report/Figures/make_margin_crossings.py` → `margin_crossings.pdf`
- **Caption draft:** "Three of the 66 pairs on the twelve-model length-matched band are
  within three accuracy points of one another in aggregate (dotted lines) yet reverse by
  at least five points on two different MMLU-Pro domains. Reserved (held-out) split,
  ground truth only — no judge verdict enters this figure, so no tie convention applies.
  Accuracy is the `acc` column, in which an unparsed prediction counts as incorrect; the
  ranking is identical under `acc_parsed` but the swing magnitudes are not. Both
  thresholds were chosen after the scores were seen and are stated so the count can be
  recomputed (`tools/analysis/export_gt_scores.py`)."

---

### M3 — The frozen instrument *(NEW — the one construction figure)*

- **Question:** what is the artifact that every arena result is attributed to? One frozen
  tree, 14 anchors, 87 leaves, sized cells — shown before the reader is asked to trust
  anything measured on it.
- **Placement:** §3.1.2 `sec:arch-taxonomy`, after "The resulting frozen artifact … has
  154 nodes, 87 leaves" (`3_System_Architecture.tex:73–76`).
- **Type:** icicle. Chosen over a node-link tree because the two facts that matter are
  *depth* and *how much query mass sits where*, and an icicle encodes both on orthogonal
  axes with no edge crossings at 154 nodes. A node-link diagram at this size is a hairball.
- **Data:** `snapshots.db`, snapshot `20260727_042523_Headless_Run_Auto_ge` (opened
  read-only), cross-checked against the `totalNodes` / `leafNodes` / `maxDepth` /
  `avgLeafDepth` that five of the six arena runs independently recorded in
  `*_secured/MAIN_thesis_metrics.csv`.
- **Verified:** 154 nodes, 87 leaves, max depth 6, 14 anchors, mean leaf depth 3.62069,
  9,141 routed queries; leaf masses are disjoint and sum to the corpus total; all five
  secured runs agree with the snapshot.
- **Generator:** `report/Figures/make_frozen_tree.py` → `frozen_tree.pdf`
- **Caption draft:** "The frozen construction artifact (snapshot 20260727\_042523): 154
  nodes, 87 leaves, maximum depth 6, mean leaf depth 3.62, 9,141 routed queries. Width is
  routed query mass; children are drawn in the snapshot's own order, not sorted by mass.
  Shading only separates adjacent anchor subtrees and encodes no quantity. The six anchors
  marked with a rule above them ran as arenas (Section~\ref{sec:res-runs}). No model data
  and no judge verdict enters this figure."

---

### M4 — What decides a verdict *(NEW; absorbs the old F4 and F6a)*

- **Question:** RQ1. What is the judge actually responding to? Answer correctness — and,
  on half of the pilot's comparisons, the mere presence of response text.
- **Placement:** §5.2.1 `sec:res-correctness`, replacing `tab:tie-by-key`; panel (b) also
  serves §5.2.3 `sec:res-capture-gap` and can be cross-referenced from there rather than
  duplicated.
- **Type:** two dot-plot panels. Panel (a) is a dumbbell over three answer-key subsets
  because the *tripling between subsets* is the event, not any single rate; panel (b) is
  two proportions with Wilson intervals plus a span annotation, because the finding is the
  size of a gap (+11.8 pp) that the key does not explain.
- **Data:** `experiment_results/arena_math_frozen/seed_42/judging/{MAIN,GENERIC_JUDGE}_verdicts.csv`
  — the run *as executed*. Panel (b) must not be recomputed from `eval_results` as it
  stands today: the corpus was repaired on 2026-07-26 and now stores text for all eight
  pilot models, so the defect is no longer visible there.
- **Verified:** tie rates 131/1160, 49/129, 148/447 (MAIN) and 127/1160, 42/129, 156/447
  (rubric-free); key agreement 914/1029 = 88.8% and 913/1033 = 88.4%; mixed-format pairs
  896 of 1,736; judge takes the text-bearing side 863/868 = 99.4% (rubric-free 874/880 =
  99.3%) against the key's 593/677 = 87.6%; excess +11.8 pp.
- **Generator:** `report/Figures/make_verdict_mechanism.py` → `verdict_mechanism.pdf`
- **Caption draft:** "Run~A, pilot roster (8 models, capture-gap defect), 1,736
  comparisons per arm. (a) The tie rate roughly triples exactly where the answer key stops
  discriminating: 11.3\% where exactly one response is correct, 38.0\% where both are and
  33.1\% where neither is. The cell-scoped rubric (filled) and the rubric-free judge
  (open) behave alike. (b) On the 896 mixed-format pairs — 52\% of all comparisons — the
  judge takes the side that has response text on 863 of 868 decided comparisons, while the
  key says that side is right on only 593 of 677. Intervals are Wilson binomial 95\%; no
  Bradley--Terry standard error appears. Aggregate key agreement on decidable, non-tied
  comparisons is 88.8\% (MAIN) and 88.4\% (rubric-free), and half of that support is
  format-decided."

---

### M5 — The trace inversion, before and after capability control *(KEPT, already exists)*

- **Question:** does reasoning text help the judge match the key? No — agreement is
  highest where neither side reasons, and the inversion strengthens once capability is
  matched.
- **Placement:** §5.2.2 `sec:res-trace-inversion`.
- **Type:** two dot-with-Wilson-interval panels.
- **Data:** Run A verdict CSVs plus the pilot's static 4-traced / 4-stub classification.
- **Generator:** `report/Figures/make_trace_strata.py` → `trace_strata.pdf`
  (verified: reproduces 97.0% vs 83.2% at matched capability and all published stratum
  counts; re-run 2026-07-30, still passes).
- **Caption:** existing draft stands. It must keep the sentence that trace presence and
  capability are collinear on the pilot roster and that panel (b) is the control for
  exactly that.

---

### M6 — The rubric is specific, and it is not decisive *(NEW; merges the old F11 and the
generic-judge result)*

- **Question:** the two halves of link 2→3 in one place. Cell-scoped rubrics really are
  specific to their cells (the premise holds), and swapping them for a rubric-free judge
  changes almost no winners (the consequence does not follow).
- **Placement:** §5.3.2 `sec:res-rubric-null` for panel (a); §5.2.4
  `sec:res-generic-judge` for panel (b). If the two sections must each own a figure, split
  it; as one figure it makes the argument the thesis actually makes.
- **Type:** panel (a) is a pair of ECDFs, chosen over box plots because the arms are
  unbalanced (87 vs 13) and a box plot on n = 13 hides how few points there are — the ECDF
  shows every cell as a step. Panel (b) is a 3×3 cross-tabulation drawn as a shaded
  matrix, chosen because the *whole* joint distribution of the two arms' choices is the
  evidence: the arms disagree constantly about ties (41 + 59 + 32 + 65) and almost never
  about winners (3 + 7).
- **Data:** `build/rubric_null/measures_all.json` (per-cell specificity, treatment arm
  `leaf-87` and size-matched null arm `random-cell`) and the Run A verdict CSVs.
- **Verified:** leaf-87 median 0.138 with 81/87 positive; random-cell median 0.012 with
  7/13 positive; terms present in ≥90% of rubrics: 0 (leaf) vs 6 (random); Mann–Whitney
  U one-sided asymptotic p = 1.210e-6; 10 winner flips of 1,736, and 1,301/1,311 = 99.2%
  agreement where both arms decided.
- **Generator:** `report/Figures/make_rubric_specific_not_decisive.py` →
  `rubric_specific_not_decisive.pdf`
- **Caption draft:** "(a) Per-cell rubric specificity — a rubric's content-term overlap
  with its own cell's queries minus its overlap with other cells' — for the frozen
  artifact's 87 induced cells against 13 size-matched random cells induced by the
  identical procedure. The within-arm subtraction cancels the vocabulary-breadth confound;
  raw own-cell overlap is not comparable across arms. Mann--Whitney $U$, one-sided,
  \emph{asymptotic} method: $p = 1.21\times10^{-6}$ (the exact method gives
  $6.0\times10^{-8}$). Arms are unbalanced by design: the null arm cost 13 inductions, and
  the registered arm-size control gives 0.134 on a 13-leaf subsample and 0.138 on a
  200-draw bootstrap. (b) The same 1,736 comparisons of Run~A (pilot roster, 8 models)
  judged with and without the cell rubric. The two arms disagree about \emph{ties} 197
  times and about \emph{winners} 10 times; of the 1,311 comparisons both arms decided,
  99.2\% agree. Lexical measures only — no embeddings, no additional judge calls."

**Caveat that must travel with M6:** `tools/analysis/rubric_specificity_null.py` and
`build/rubric_null/` are untracked in version control. Until they are committed this
result is one clean checkout from being unsupported.

---

### M7 — The domain-reordering screen *(NEW)*

- **Question:** where could a partition detect anything at all? This is the offline,
  judge-free screen that selected the six arena domains.
- **Placement:** §5.4.4 `sec:res-law`, replacing the fourteen-row table.
- **Type:** horizontal dot plot ordered by p, with the size-matched null's 5th-percentile-
  to-median band drawn behind each observed ρ. Chosen because "reorders" is a claim about
  a value's position *relative to its own null*, and the null differs per domain with n;
  putting the null behind each row makes the comparison local instead of asking the reader
  to hold fourteen p-values in mind.
- **Data:** `mmlu_pro_dataset_cache_v2.db` `eval_results`, reserved split, 11-model band,
  1,500-draw size-matched permutation null, seed 42.
- **Verified:** all fourteen n, ρ and p reproduce the registered arm (B) of
  `tools/analysis/domain_reorder_screen.py` exactly.
- **Generator:** `report/Figures/make_domain_screen.py` → `domain_screen.pdf`
  (runtime ≈ 2 min; 21,000 permutation draws)
- **Caption draft:** "Offline domain screen on the eleven-model length-matched band,
  reserved split: each domain's within-domain ground-truth ranking against the band's
  global ranking, with a 1,500-draw size-matched permutation null (seed 42) behind it.
  Eight of fourteen domains reorder at $p<0.05$; Mathematics orders identically to the
  global ranking ($\rho = 1.000$, $p = 1.000$), which is why it was designated the
  pre-registered null arm. Ground truth only: no judge verdict enters this figure, so no
  tie convention applies. The screen uses MMLU-Pro's native labels, not induced cells --
  it bounds what any partition could show. The six domains marked $\bullet$ ran as arenas;
  note that they ran on the \emph{twelve}-model band, which shares eight models with the
  eleven-model band screened here."

---

### M8 — Screen versus arena, six domains *(NEW — the centrepiece)*

- **Question:** RQ2. Does removing the partition change the ranking, and does the offline
  screen predict where it will? The screen's verdict and the arena's verdict come apart.
- **Placement:** §5.2.7 `sec:res-c5`, replacing `tab:c5-rho` and carrying the six-domain
  result the chapter is built around.
- **Type:** dumbbell per domain on a Δρ axis, grouped by the screen's verdict, with the
  |Δρ| < 0.007 band shaded and both tie conventions as the dumbbell's two ends. Chosen
  because the dumbbell's *length* is the convention sensitivity and its *position* is the
  effect, so the figure cannot be read as claiming more precision than the pipeline has —
  which a single point per domain would.
- **Data:** the six `ratings_*_paired.db` stores plus `eval_results`; the screen column is
  recomputed from `eval_results` under the registered 14-domain RNG walk.
- **Verified:** all twelve Δρ values reproduce the registered table exactly
  (law +0.0000/+0.0210, philosophy +0.0490/+0.0420, history +0.0105/+0.0105,
  psychology +0.0210/+0.0210, math −0.0637/−0.0070, engineering +0.0035/−0.0035), and all
  six screen p-values reproduce (0.008 / 0.046 / 0.003 / 0.000 / 1.000 / 0.706).
- **Generator:** `report/Figures/make_screen_vs_arena.py` → `screen_vs_arena.pdf`
- **Caption draft:** "$\Delta\rho = \rho_{\mathrm{MAIN}} - \rho_{\mathrm{C5}}$ on six
  paired arenas, twelve-model length-matched band, both tie conventions (filled circle:
  ties half-weighted; open triangle: ties dropped). Positive favours per-leaf judging. The
  shaded band is the pre-registered decisive threshold $|\Delta\rho| < 0.007$, two
  Spearman grid steps at $M = 12$. Domains are grouped by the offline screen's verdict and
  the screen's permutation $p$ is given at the right; the screen ran on the
  \emph{eleven}-model band, which shares eight models with the twelve-model band the
  arenas ran on. Mathematics was designated the null arm in advance and returned the
  largest effect in the arena, in the direction favouring the partition-free condition.
  Engineering, also a clean null by the screen, sits inside the threshold and changes sign
  with the tie convention. No Bradley--Terry standard errors are shown: every stored BT SE
  in this pipeline is the clamp constant pending the $1/K^2$ recompute."

---

### M9 — The two outcome measures dissociate *(NEW)*

- **Question:** are ρ-against-ground-truth and per-verdict key agreement measuring the
  same thing? No. Philosophy's rank agreement favours per-leaf judging by seven decisive
  thresholds while its key agreement favours the partition-free arm.
- **Placement:** §5.2.7 `sec:res-c5`, immediately after M8, or at the head of §5.5
  `sec:res-summary` as the reason the chapter refuses a single verdict.
- **Type:** 2-D scatter with each domain drawn as a vertical segment spanning the two tie
  conventions. Chosen because the claim is about the *joint* behaviour of two outcomes,
  which only a scatter shows, and because the segment keeps the convention sensitivity
  visible in the same mark.
- **Data:** the six paired stores plus `eval_results`.
- **Verified:** all twelve Δρ values and all twelve key-agreement percentages reproduce
  the registered table (math 94.2/94.7, law 88.0/86.2, philosophy 92.9/94.2,
  history 83.3/79.4, psychology 85.2/84.3, engineering 89.0/88.5); 24 assertions in total.
- **Generator:** `report/Figures/make_rho_gt_dissociation.py` → `rho_gt_dissociation.pdf`
- **Caption draft:** "The two outcome measures do not move together. Horizontal:
  agreement with the MMLU-Pro key, MAIN minus C5, over decidable, non-tied comparisons
  only ($n = 209$--$1{,}216$ per condition). Vertical: $\Delta\rho$ under both tie
  conventions, drawn as a segment whose ends are the two conventions. Twelve-model
  length-matched band, six paired arenas. Philosophy sits in the upper-left quadrant: the
  rank statistic favours per-leaf judging by seven decisive thresholds while the
  higher-powered per-verdict statistic favours the partition-free arm. A verdict that
  rests on $\Delta\rho$ alone is a verdict about which of two outcome measures was
  chosen."

---

## 2. Appendix figures (3: 1 new, 2 kept)

### A1 — Leaf-size distribution *(KEPT, already exists)*

- **Question:** how uniform are the cells the arena judges within?
- **Placement:** Appendix A, beside the birth-constraint discussion.
- **Data:** the frozen snapshot's leaf `queryIds`.
- **Generator:** `report/Figures/make_leaf_size_hist.py` → `leaf_size_hist.pdf`
  (verified: 87 leaves, median 88, IQR [71, 118], min 54, max 396, exactly one leaf below
  the birth floor n_min = 55; re-run 2026-07-30, still passes).

### A2 — The ρ levels behind the paired contrasts *(NEW)*

- **Question:** why does this thesis quote only paired within-run contrasts? Because the
  levels move far more than the contrasts do.
- **Placement:** Appendix, next to the numerics appendix, referenced from §5.2.6
  `sec:res-tie-policy` and from M8's caption.
- **Type:** two dumbbell panels, one per tie convention, sharing a ρ axis, with each
  arena's verdict and leaf count in the row label. Chosen because it is the *same* mark as
  M8 read on the absolute scale — the reader can see directly that M8's whole x-range is
  narrower than the spread between two adjacent rows here.
- **Data:** the six paired stores plus `eval_results`.
- **Verified:** every one of the twelve registered Δρ values is reproduced *as the
  difference between two plotted levels* — i.e. the assertion is on exactly the quantities
  being drawn. The 24 fitted ρ span 0.785–0.965 (spread 0.180) while the largest paired
  contrast is 0.064.
- **Generator:** `report/Figures/make_rho_levels.py` → `rho_levels.pdf`
- **Caption draft:** "The absolute $\rho$ levels the main-text contrasts are differences
  of. Twelve-model length-matched band, six paired arenas, per-leaf (filled circle) and
  partition-free (open square), (a) ties half-weighted, (b) ties dropped. The 24 fitted
  values span $\rho = 0.785$ to $0.965$ while the largest paired MAIN-vs-C5 contrast is
  $0.064$; the ground-truth vector also differs between panels' rows, because each arena
  judged a different question set. Levels are therefore not comparable across rows and
  only the within-domain, within-run contrast is quoted anywhere in this thesis. No
  Bradley--Terry standard errors: verdict and leaf counts are given instead."

### A3 — Granularity flatness *(KEPT AS A REFUSAL — do not "fix")*

`report/Figures/make_granularity_flat.py` deliberately recomputes, prints what does and
does not reproduce, and **exits non-zero without emitting a PDF**, because the published
centred-residual quartet reproduces under no single convention. I re-ran it on 2026-07-30
and confirmed it still refuses. Leave it refusing. If the centring convention is ever
pinned down, the script already contains the working panel (a).

---

## 3. Not buildable — and exactly what would fix each

### 3.1 Within-domain vs between-domain between-cell ρ — **HELD, two independent reasons**

The brief flagged that this result has no permutation null yet. Building it turned up a
second problem, which is the stronger one.

- The **within-domain arm reproduces exactly**: median 0.907, IQR [0.852, 0.945], 293
  leaf pairs, on the 12-model band, reserved split, leaves labelled by majority category,
  cells filtered to ≥ 12 covered questions.
- The **between-domain arm does not reproduce**. Published: median 0.937, IQR
  [0.911, 0.959], 91 pairs. I obtain **0.9422, IQR [0.9161, 0.9632]** and could not
  recover the published value under any of ten convention combinations tried: 11-model vs
  12-model band; reserved / non-reserved / full corpus; domain accuracy over all covered
  questions vs only leaf-assigned questions vs only questions inside size-qualifying
  leaves; index-based vs `numpy.percentile` quartiles. The 91 pairs are C(14,2), so the
  cell definition is not in doubt — something in the accuracy computation is.
- **To unblock:** (i) recover the script that produced the published between-domain row
  and name its convention, and (ii) run the permutation null the comparison needs. With
  both, the figure is a two-ECDF or two-box panel and takes an hour. Without either, this
  is the exact situation `make_granularity_flat.py` exists to refuse.

### 3.2 Per-domain tie profiles across the six paired arenas — **needs one registration**

Fully computable and I have the numbers, but there is nothing registered to assert
against, and the pattern **does not** replicate the pilot's, so it cannot ship as a
confirmation figure without an interpretation I am not in a position to supply. What the
six arenas actually show (MAIN, tie rate by key subset):

| domain | exactly one correct | both correct | neither correct |
|---|---|---|---|
| math | 8% (103/1306) | 39% (447/1136) | 16% (32/198) |
| law | 17% (232/1348) | 25% (142/565) | 20% (120/586) |
| philosophy | 11% (47/415) | 25% (175/687) | 33% (72/217) |
| history | 14% (48/347) | 19% (166/861) | 17% (41/240) |
| psychology | 11% (133/1177) | 21% (332/1557) | 20% (115/566) |
| engineering | 9% (23/269) | 34% (130/377) | 23% (33/146) |

The pilot's clean "one-correct ≪ both ≈ neither" tripling holds for the *both-correct*
subset everywhere but not for *neither-correct*, which is often close to the one-correct
rate. **To unblock:** register the expected pattern (or register this table as the
result), then the figure is six small multiples of the M4(a) mark.

### 3.3 The Run B "repair by construction" panel — **not recoverable from disk**

The old plan's F6(b) wanted per-model stored-response length for the 12-model band beside
the pilot's, to show the format artifact controlled by construction. The corpus was
repaired on 2026-07-26, so `eval_results` now stores text for all eight pilot models
(median lengths 230–1,413 characters). The pilot's zero-length side **no longer exists in
the database** and can only be shown from the run-as-executed verdict CSVs, which is what
M4(b) does. The within-roster length/accuracy correlations the old plan quoted
(r = +0.286 vs +0.597) are not registered anywhere I could find. **To unblock:** register
those two correlations against a named split and roster; the panel is then a scatter.

### 3.4 Deliberately excluded, per the brief

- Redundancy percentages (72.2% / 42.2%) — irreproducible.
- Correctness-blind ρ magnitudes (0.74–0.76) — unresolved between two computations on the
  same verdicts.
- Leaf-level between-cell agreement quoted as 0.922 — holds only under the
  construction-assignment convention, which the number is never shipped with.
- The centred-residual quartet — see A3.
- **Any** Bradley–Terry confidence interval or error bar, anywhere, until the 1/K²
  recompute lands. The three figures that could have used one (M8, M9, A2) are built on
  ρ and proportions precisely so that nothing in this plan waits on it.

### 3.5 Convention traps the build actually hit

Recorded because each one silently produced a *plausible wrong number* first:

1. **The screen's p is RNG-stream-dependent.** Looping only the six arena domains instead
   of all fourteen moves law from p = 0.008 to p = 0.006. Both scripts that touch the
   screen now walk all fourteen domains in sorted order from one `random.seed(42)`, and
   say why in the header.
2. **Scale-then-subtract ≠ subtract-then-scale.** Computing accuracy differences in
   percentage points rather than fractions changes the third published swing from 15.7 to
   15.8. `make_margin_crossings.py` keeps fractions and scales last.
3. **Mann–Whitney has two p-values here.** Asymptotic gives 1.21e-6 (the registered
   value); exact gives 6.0e-8. `make_rubric_specific_not_decisive.py` pins the method and
   the caption names it.
4. **"99.4% winner agreement" has two denominators.** Non-flip rate over all 1,736
   comparisons = 99.4%; agreement over the 1,311 both arms decided = 99.2%. M6's caption
   gives the counts so the reader can form either.

---

## 4. What changed from `docs/figures-plan.md`, and why

`figures-plan.md` was written on 2026-07-28, before the five non-Math paired arenas
finished. Its centre of gravity is a single Math C5 comparison (F7) with law pending as
F12. The six-domain result now exists and it is the thesis's main finding, so the plan is
rebuilt around it rather than patched.

| change | why |
|---|---|
| **F7 (Math C5) + F12 (law, PENDING) → M8, one six-domain figure** | The six-domain pattern *is* the result. Two single-domain figures would show the same data while hiding the thing that matters — that the screen does not predict the arena. F12's "PENDING" slot is closed. |
| **F9 (screen) kept as M7 but re-typed** | Old spec called out law and Math by name in the caption; now all fourteen rows carry their own null band and the six arena domains are marked, so the reader can check the screen's calibration rather than take two examples on trust. |
| **NEW: M9, the outcome dissociation** | Did not exist in the old plan; the GT-agreement-vs-Δρ dissociation only became visible once six domains were in. It is the strongest single argument against reading Δρ as *the* verdict. |
| **F4 + F6(a) → M4, one figure** | Both were about Run A's verdict mechanism and shared a roster and a caveat. Merged; the aggregate 88.8%/88.4% moved into the caption where it belongs as context, not a panel. |
| **F11 (rubric overlap, "optional") + the generic-judge result → M6, promoted to main text** | The old plan had the specificity premise as an optional figure and the 99.4% winner agreement as prose. Together they are a complete link-2-holds / link-3-does-not argument, which is worth a main-text figure. Also: the old F11's numbers (0.200 / 0.138 medians) are the *raw own-cell overlap*, which has the vocabulary-breadth confound; M6 plots the within-arm specificity that cancels it. |
| **F6(b) dropped** | Not recoverable from the repaired corpus — see §3.3. |
| **F8 (sampler × tie convention strip) → folded into A2** | The old F8 needed `ratings_math12.db` vs `ratings_math12_shuffled.db` and a sampler attribution I could not verify from disk ("confirm which store carries which sampler before labelling" was an open item in the old plan and is still open). A2 makes the same point — absolute ρ is not stable, only paired contrasts are — from six domains and two tie conventions, all of which *are* verified. |
| **F10 (granularity) → stays refusing** | Unchanged verdict, re-confirmed by re-running the script. |
| **F2 (tree) → M3, unchanged in intent, changed in numbers** | The old spec's caption carried J = 0.253129 and "certified at iteration 10" from `freeze_mcs55`. M3 reads the snapshot the *arenas* actually used and cross-checks it against what five arena runs recorded, so the figure and the results it supports cannot drift apart. J and the certificate belong in the appendix text, not on this figure. |
| **F3 (information-flow diagram) dropped** | It is a structural diagram with no data, and §3.2's prose plus `tab:info-separation` already carry it. Spending a main-text slot on a box-and-arrow restatement was the weakest item in a plan whose budget is now needed for six domains. If the examiner asks for it, it is a TikZ figure and costs nothing in verification. |
| **NEW: M2, the real-model crossings** | The old plan had the synthetic slopegraph alone in Chapter 1. Leading with a synthetic figure and never showing the real one is exactly the criticism the thesis pre-empts elsewhere; M2 closes it with three verified pairs. |
| **A-2, A-3, A-4 (gate flowchart, gate scatter, calibration sweep) dropped** | All three are construction-side. The brief caps construction at one main-text figure and these add three appendix figures to support an argument the thesis reports as, at best, coherent rather than beneficial. They remain buildable from `proposals.csv` and `combined_ledger.csv` if the appendix is expanded. |
| **Scripts moved from `tools/analysis/` to `report/Figures/`** | Matches the three generators already living there (`make_trace_strata.py`, `make_leaf_size_hist.py`, `make_granularity_flat.py`) and keeps each figure's generator beside its PDF. Analysis tools stay in `tools/analysis/`; figure generators are not analysis tools, they are verified renderers of results those tools established. |
| **Every script is standalone** | No shared style module. A figure generator that depends on a helper is a figure that can change without its script changing. The ~15-line style block is duplicated deliberately. |

---

## 5. Build manifest

| figure | generator | output | verification |
|---|---|---|---|
| M1 | `make_routing_slopegraph.py` | `routing_slopegraph.pdf` | synthetic, declared |
| M2 | `make_margin_crossings.py` | `margin_crossings.pdf` | 3 swings + selection count |
| M3 | `make_frozen_tree.py` | `frozen_tree.pdf` | 5 structural values × 6 sources |
| M4 | `make_verdict_mechanism.py` | `verdict_mechanism.pdf` | 6 tie counts, 2 agreements, 3 mixed-pair counts |
| M5 | `make_trace_strata.py` | `trace_strata.pdf` | stratum counts + matched-capability panel |
| M6 | `make_rubric_specific_not_decisive.py` | `rubric_specific_not_decisive.pdf` | 2 medians, 2 positive counts, 2 ≥90% counts, p, flips |
| M7 | `make_domain_screen.py` | `domain_screen.pdf` | 14 × (n, ρ, p) |
| M8 | `make_screen_vs_arena.py` | `screen_vs_arena.pdf` | 12 Δρ + 6 screen p + roster identity |
| M9 | `make_rho_gt_dissociation.py` | `rho_gt_dissociation.pdf` | 12 Δρ + 12 agreements |
| A1 | `make_leaf_size_hist.py` | `leaf_size_hist.pdf` | 87 leaves, median, IQR, min, max, floor count |
| A2 | `make_rho_levels.py` | `rho_levels.pdf` | 12 Δρ, asserted on the plotted levels |
| A3 | `make_granularity_flat.py` | *(none, by design)* | refuses; exits non-zero |

All eleven emitting scripts were re-run end to end on 2026-07-30 and all passed their
assertions. `make_domain_screen.py` takes about two minutes; the rest are seconds each.
