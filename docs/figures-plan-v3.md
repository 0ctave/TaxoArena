# Figures plan v3 — cut to eight, rebuilt to be read cold

> **The figure set is CURRENT. Every Δρ and screen p in it is not (2026-07-31).**
>
> M6 `screen_vs_arena` and A2 `rho_levels` are specified against the M = 12 batch, which is
> superseded — its bootstrap starved every cell but one in every domain and three runs had
> unequal arms. The results are the five revised-scheduler runs: philosophy +0.0490,
> history +0.0140, engineering +0.0105, psychology +0.0070, mathematics −0.0070, identical
> under both tie conventions except mathematics (0.0000 dropped). See
> `docs/newlogic-rerun-record.md`.
>
> Three consequences for M6. Its "all twelve Δρ reproduce the registered table exactly"
> line is a reproduction check against a superseded batch, not a stability claim. Its six
> screen p-values (0.008 / 0.046 / 0.003 / 0.000 / 1.000 / 0.706) are the **superseded
> 11-model band**; the 12-model values the thesis quotes are 0.011 / 0.053 / 0.009 / 0.000
> / 0.289 / 0.817. And the figure now has to plot two batches or name the one it plots —
> philosophy, the screen's false negative, holds at +0.0490 under both, which is the
> figure's strongest single point and the one that does not depend on the choice.

> **CURRENT — this is the authoritative figure set. Two corrections, 2026-07-30 (later
> same day).**
>
> 1. **Six paired arenas -> eight.** The plan says "six domains" throughout (M6's grouping,
>    A2, and every "four of four" / "six of six" count in the M6 section). There are eight:
>    physics (+0.0140/+0.0140, screen p 0.004) and computer science (running) are missing.
>    **M6 `screen_vs_arena` is the centrepiece and must be rebuilt on the eight-run set**,
>    and its concordance counts recomputed — the screen flags four of the domains that ran,
>    and philosophy met both conventions **without being flagged**, so the figure must not
>    read as a clean predictor. A2 `rho_levels` needs the same rebuild.
> 2. **The `trace_strata` "ACTION REQUIRED IN .tex" warning is already resolved.** The
>    sections saying `6_Results.tex` still carries `\includegraphics{trace_strata}` and
>    "the document will not compile" are stale — the float is gone and `trace_strata.pdf`
>    is absent from `report/Figures/`. The surviving `trace-strata` references in the
>    Results chapter are all `tab:trace-strata`, a **table**. Ignore those two passages.
>
> Still open, and correctly flagged in the plan: `fig:granularity-flat` has a stub float
> with a `\label` in the Results chapter and is referenced, but
> `make_granularity_flat.py` deliberately refuses to plot. Either cut the float and its
> reference, or make the refusal explicit in the text.

Status: written 2026-07-30 on branch `tree-only`. **Supersedes `docs/figures-plan-v2.md`
(2026-07-30)** in full, which superseded `docs/figures-plan.md`. No `.tex` was edited and
nothing was committed.

The brief for this pass was the author's own verdict on the v2 set: *"not very clear and
hard to understand"*, with a request to rethink which figures are necessary at all. Every
v2 PDF was rendered to PNG and looked at as a reader would meet it — cold, in print, with
only a caption for help — before anything was decided.

**Count: 11 figures → 8.** Six main-text, two appendix. Three figures were deleted
outright and one panel was replaced. Every surviving script still recomputes its numbers
from the primary store and `raise`s before drawing on mismatch; all eight were re-run to
completion on 2026-07-30 and all eight pass.

---

## 0. What changed at a glance

| v2 figure | v3 |
|---|---|
| `routing_slopegraph` | **KEPT**, rebuilt — was in **full colour**, now greyscale |
| `margin_crossings` | **CUT** |
| `frozen_tree` | **KEPT**, rebuilt — vertical icicle → horizontal, readable anchor names |
| `verdict_mechanism` | **KEPT**, rebuilt — rates drawn as lengths, findings in the panel titles |
| `rubric_specific_not_decisive` | **KEPT**, panel (b) replaced — 3×3 cross-tab → one proportional bar |
| `domain_screen` | **KEPT**, rebuilt — finding in the title, axis says what "high" means |
| `screen_vs_arena` | **KEPT**, rebuilt — screen verdict made the dominant structure |
| `rho_gt_dissociation` | **CUT** |
| `trace_strata` | **CUT** — see §1.2, this is the one to argue about |
| `leaf_size_hist` | **KEPT**, rebuilt — was in **colour**, now greyscale |
| `rho_levels` | **KEPT**, rebuilt — the level-vs-contrast point now drawn, not just captioned |
| `make_granularity_flat.py` | **STILL REFUSES**, untouched, verified still exiting 1 |

Three v2 scripts asserted in their own headers that "no figure uses colour at all". That
was false: `routing_slopegraph`, `trace_strata` and `leaf_size_hist` were all built with a
blue/orange pair and had not been reworked when that claim was written. Two of the three
survive and are now genuinely greyscale; the third was cut.

---

## 1. What was cut, and why

The test applied to each figure: **does it carry an argument the prose cannot?** A figure
was cut if it (a) restated a small table, (b) showed a result the text states in one
sentence, (c) needed three sentences of caption to become legible, or (d) duplicated
another figure's job.

### 1.1 `margin_crossings` — CUT (duplication, and dominated by a better figure)

Three of the roster's 66 model pairs are level in aggregate and reverse at the margin. The
figure was three small slopegraphs deliberately drawn in the same visual grammar as
`routing_slopegraph`, sitting two paragraphs after it in §1.1.

- **Criterion (d).** It makes the same argument as the figure immediately above it. A
  reader who understood the first does not need the second; a reader who did not will not
  be helped by a repetition with harder labels.
- **It is dominated by `domain_screen`.** The empirical claim "the aggregate ranking is not
  the per-domain ranking" is made far better, later in the thesis, by the screen: *eight of
  fourteen* domains reorder the ranking at *p* < 0.05, each against its own size-matched
  permutation null. That is the whole corpus with an error model. `margin_crossings` is
  three pairs out of 66, selected by two thresholds chosen after the scores were seen (its
  own caption said so). Chapter 1 should forward-reference the screen instead.
- It was also the least legible survivor of the v2 set: the headline number ("21.6-point
  swing") was never defined on the figure, each model's aggregate accuracy was a dotted
  line so faint it read as a rule, and only two of four endpoints per panel were labelled.
- **What replaces it:** one sentence of prose. "On the twelve-model band, three of the 66
  pairs sit within three accuracy points of one another in aggregate yet reverse by at
  least five points across two MMLU-Pro domains (reserved split, `acc` column; both
  thresholds chosen post hoc)." The numbers are already computed and reproduce exactly.

### 1.2 `trace_strata` — CUT. **This is the call to argue with me about.**

It is one of only three figures currently wired into the `.tex` (`6_Results.tex:261`), so
cutting it is not free. Three independent reasons, in increasing order of force:

1. **Criterion (a): it is six proportions.** Panel (a) is three rates for each of two judge
   arms. That is a table.
2. **Criterion (d): it duplicates `verdict_mechanism` panel (b), using the identical
   partition.** Both scripts define `TRACED` and `STUB` as the *same* four-and-four split
   of the pilot roster. `trace_strata`'s "no-trace × no-trace" stratum and
   `verdict_mechanism`'s "the side without response text" are the same four models. Both
   figures therefore say: *the judge's agreement with the key tracks surface form, not
   correctness.* `verdict_mechanism` says it on 868 and 677 comparisons with a 99.4 % vs
   87.6 % gap. `trace_strata`'s decisive panel says it on **n = 33**, with a Wilson
   interval running from 84.8 % to the ceiling.
3. **The label is wrong under the thesis's own corrected story.** "No-trace" implies a
   model that answered tersely without reasoning. What actually happened is the capture-gap
   defect: those four models had **no persisted response text at run time**, so the judge
   saw a synthesised stub. `verdict_mechanism` names this correctly and makes it the
   subject. `trace_strata` frames the same artifact as a finding about *reasoning*, which
   is a stronger and less supportable claim — especially given the roster's trace/capability
   collinearity (per `docs` memory: AUC 0.982), which panel (b) is supposed to control for
   but can only control for down to n = 33.

**What replaces it:** two sentences in §5.2.2, quoting the matched-capability numbers with
their intervals and the n, and stating plainly that the stratum carrying the inversion has
33 comparisons in it. If the author wants the inversion to remain a figure, my counter-offer
is to keep it *only* if the roster is widened so the matched-capability arm is not n = 33 —
otherwise the figure invites more confidence than the data supports.

**ACTION REQUIRED IN `.tex` (I could not do it):** `report/03_Content/6_Results.tex:261`
still has `\includegraphics{trace_strata}`. The PDF is deleted, so **the document will not
compile until that float is removed.** Lines 261–270 (`fig:trace-strata`) must go, together
with any `\ref{fig:trace-strata}`.

### 1.3 `rho_gt_dissociation` — CUT (criterion (c), one point carries it)

A 2-D scatter of six domains: Δρ against MAIN−C5 answer-key agreement. The argument —
"the two outcome measures do not move together" — rests entirely on Philosophy sitting in
one quadrant.

- The reader must learn a measure used nowhere else in the figure set (per-verdict key
  agreement in percentage points, MAIN minus C5) in order to read one point.
- It needs quadrant labels in two corners plus a caption explaining what an upper-left
  position means before it says anything. That is criterion (c) exactly.
- The claim is one sentence and belongs in the Discussion as a limitation: "In Philosophy
  the rank statistic favours per-leaf judging by seven decisive thresholds while the
  higher-powered per-verdict statistic favours the partition-free arm; a verdict resting on
  Δρ alone is partly a verdict about which outcome measure was chosen."

I deliberately did **not** fold this second measure into `screen_vs_arena` as an extra
column. The centrepiece has exactly one comparison to make and adding a second outcome axis
would blunt it.

### 1.4 `rubric_specific_not_decisive` panel (b) — REPLACED, not cut

The v2 panel was a 3×3 cross-tabulation of the two judge arms' choices, drawn as a shaded
matrix. That is a small table with a border, and worse, it puts the eye in the wrong place:
the largest cell is 1,171 while the finding is the smallest cell, 10.

It is now **one proportional bar over all 1,736 comparisons**, partitioned into four
exhaustive, disjoint classes (asserted to sum to 1,736): both arms picked the same winner
(1,301 / 74.9 %), both tied (228 / 13.1 %), one tied (197 / 11.3 %), **winner flipped
(10 / 0.6 %)**. The flip class is a black sliver 0.6 % wide with a leader label. The
negative result is now the thing you cannot miss, which is the opposite of what the matrix
did.

---

## 2. The rules the survivors were rebuilt under

1. **Real data only.** Every plotted number comes from a database, CSV or stored artifact
   on disk. The single synthetic figure declares itself synthetic twice — in the axis label
   and in its caption.
2. **Verify before plotting.** Unchanged from v2 and not weakened anywhere. No assertion
   was relaxed to make a plot work. Two scripts gained *additional* assertions
   (`frozen_tree`: routed-query total and anchor-leaf sum; `rubric_*`: the four-class
   partition sums to 1,736).
3. **Greyscale only.** No hue anywhere. Identity is carried by position, marker shape
   (filled circle / open square / open triangle), line style, greyscale fill and hatch.
4. **Every figure must be readable without the body text.** Concretely, for each survivor:
   axes state their unit *and* what "high" means; marks are labelled directly rather than
   through a legend; the comparison the figure exists to make is the loudest thing in it;
   the *reading* is annotated, not just the data (threshold lines say "not decisive",
   null bands say what they are, the failed prediction is pointed at by name).
5. **Short in-figure titles state the finding.** Every survivor now carries a headline
   sentence. Titles are not captions and do not replace them.
6. **No Bradley–Terry confidence intervals anywhere.** The 1/K² recompute is outstanding;
   every stored BT SE is the clamp constant. Where an interval appears it is a Wilson
   binomial interval on a proportion and it says so on the figure.
7. **Both tie conventions shown wherever a ρ appears.** Δρ = ρ(MAIN) − ρ(C5); positive
   favours per-leaf judging; decisive threshold |Δρ| ≥ 0.007 = two Spearman grid steps at
   M = 12 (one step = 6/(12·143) = 0.0035).

### The rosters, never blurred

| name | size | where it appears |
|---|---|---|
| **pilot** | 8 models, Run A, carries the capture-gap defect | `verdict_mechanism`, `rubric_*` panel (b) |
| **12-model length-matched band** | the roster all six paired arenas ran on | `screen_vs_arena`, `rho_levels` |
| **11-model length-matched band** | the roster the registered domain screen ran on | `domain_screen`, and the screen column of `screen_vs_arena` |

The 11- and 12-model bands **share only eight models**. `screen_vs_arena` reads a screen
computed on one roster against arenas run on the other; that is stated in its in-figure
subtitle, in its script header and in its caption. It is a standing limitation of the
design, not a presentation choice.

---

## 3. Main-text figures (6)

### M1 — Routing micro-example slopegraph — §1.1 `fig:routing-slopegraph`

- **Carries:** why a scalar leaderboard destroys exactly the information a router needs.
- **Data:** the synthetic values at `1_Introduction.tex:74–77`, identical to Table 1.1.
- **Generator:** `report/Figures/make_routing_slopegraph.py`
- **What changed:**
  - **It was in colour** (`#2a78d6` / `#eb6834`). Now black only: Model A solid + filled
    circle, Model B dashed + open square, with name *and* value at both ends of both lines.
  - Title states the finding rather than naming the chart type.
  - The aggregate reference line is annotated with its *reading* ("both models score 0.72
    in aggregate: one number, no way to tell them apart"), not just its value.
  - Each column now says what a router should do there ("route here to A" / "to B"), which
    is the point of the example and was previously left to the body text.
  - "SYNTHETIC ILLUSTRATION — not a measurement" now sits in the y-axis label, so it
    travels with the figure even if the caption is skimmed.
  - Added a cheap assertion that the two models really are level in aggregate — the whole
    micro-example depends on it and nothing checked it before.
- **Caption draft:** "A synthetic two-domain micro-example. Model A and Model B score the
  same 0.72 averaged over all fourteen MMLU-Pro domains, yet their ranking reverses between
  Mathematics and History; a scalar leaderboard can represent the average and not the
  reversal. **Values are synthetic and illustrative, not empirical**; the same numbers
  appear in Table~1.1. No roster, no judge verdict and no tie convention apply. The
  empirical form of this claim is Figure~\ref{fig:domain-screen}, where eight of MMLU-Pro's
  fourteen domains reorder the ranking of a real eleven-model band."

### M2 — The frozen instrument — §3.1.2 `sec:arch-taxonomy`

- **Carries:** what the artifact is that every arena result is attributed to, before the
  reader is asked to trust anything measured on it.
- **Data:** `snapshots.db`, snapshot `20260727_042523_Headless_Run_Auto_ge` (read-only),
  cross-checked against the `totalNodes`/`leafNodes`/`maxDepth`/`avgLeafDepth` that five of
  the six arena runs independently recorded in `*_secured/MAIN_thesis_metrics.csv`.
- **Verified:** 154 nodes, 87 leaves, max depth 6, 14 anchors, mean leaf depth 3.6206897,
  9,141 routed queries; leaf masses disjoint and summing to the corpus total; anchor leaf
  counts summing to 87; all five secured runs agree.
- **Generator:** `report/Figures/make_frozen_tree.py`
- **What changed:**
  - **Rotated from a vertical icicle to a horizontal one.** The fourteen anchor names were
    rotated 90° and stranded at the bottom of the figure, five depth-rows away from the
    blocks they named. They are now horizontal row labels sitting against their own rows.
  - Each row carries its own leaf count and routed-query count in the right margin, so the
    figure answers "how big is Philosophy?" without a table.
  - Shading now fades with depth (redundantly with column position) instead of alternating
    between neighbours, so the ragged right edge reads as "shallower" at a glance. The
    convention header was updated to say so — the previous header claimed the shading
    encoded nothing.
  - The two axes are labelled with what they mean ("14 anchors", "row height ∝ routed
    queries") and the ragged edge is explained on the figure ("a row that stops short has
    no deeper cells: mean leaf depth 3.62, maximum 6").
  - Arena anchors are bold **and** carry a rule, so the marking is not weight-only.
- **Caption draft:** "The frozen construction artifact (snapshot 20260727\_042523): 154
  nodes, 87 leaves, maximum depth 6, mean leaf depth 3.62, 9,141 routed queries. Rows are
  the fourteen depth-1 anchors and row height is routed query mass; columns are depth, so a
  row that stops short has no cells below that depth. Children are drawn in the snapshot's
  own order, not sorted by size. Shading fades with depth and encodes no quantity. The six
  anchors marked with a rule ran as arenas (Section~\ref{sec:res-runs}). No model data and
  no judge verdict enters this figure, so no roster and no tie convention apply."

### M3 — What decides a verdict — §5.2.1 `sec:res-correctness` (+ §5.2.3)

- **Carries:** RQ1. The judge responds to answer correctness — and, on half the pilot's
  comparisons, to the mere presence of response text.
- **Data:** `experiment_results/arena_math_frozen/seed_42/judging/{MAIN,GENERIC_JUDGE}_verdicts.csv`,
  the run *as executed*. Panel (b) must never be recomputed from `eval_results` as it stands
  today: the corpus was repaired on 2026-07-26 and now stores text for all eight pilot
  models, so the defect is no longer visible there.
- **Verified:** tie counts 131/1160, 49/129, 148/447 (MAIN) and 127/1160, 42/129, 156/447
  (rubric-free); key agreement 914/1029 = 88.8 % and 913/1033 = 88.4 %; mixed-format pairs
  896 of 1,736; judge takes the text-bearing side 863/868 = 99.4 % (rubric-free
  874/880 = 99.3 %) against the key's 593/677 = 87.6 %; excess +11.8 pp.
- **Generator:** `report/Figures/make_verdict_mechanism.py`
- **What changed:**
  - Panel (a) was a dumbbell of dots. The quantity is a **rate**, so it is now drawn as a
    **length**: the tripling is a bar-length comparison instead of a gap the eye has to
    measure. Every bar carries its rate in bold.
  - The event is the *ratio*, so the ratio is now drawn — a bracket spanning the three
    strata labelled "×3.4 more ties once the key stops separating the two answers".
  - Both panel titles now state the finding with its direction, not the chart's subject.
  - Panel (a)'s x-axis says what it measures in plain words ("comparisons the judge refused
    to decide") and what high means.
  - Panel (b)'s truncated axis is now declared on the axis label ("axis starts at 85 %"),
    which the v2 version did not do.
  - The rows are relabelled "what the JUDGE did" vs "what the KEY says", which is the
    comparison, rather than two neutral descriptions.
  - The one marker a reader must decode (rubric-free arm) is keyed once, in clear space,
    instead of two leader lines into a crowded row.
- **Caption draft:** "Run~A, pilot roster (8 models, capture-gap defect), 1,736 comparisons
  per arm. (a) The tie rate roughly triples exactly where the answer key stops
  discriminating: 11.3\% where exactly one response is correct (1,160 pairs), 38.0\% where
  both are (129) and 33.1\% where neither is (447). The rubric-free judge (open squares)
  behaves alike: 10.9 / 32.6 / 34.9\%. (b) On the 896 mixed-format pairs --- 52\% of all
  comparisons --- the judge takes the side that has response text on 863 of 868 decided
  comparisons (99.4\%), while the key says that side is right on only 593 of 677 (87.6\%).
  Whiskers are Wilson binomial 95\% intervals; no Bradley--Terry standard error appears
  anywhere in this thesis. Aggregate key agreement on decidable, non-tied comparisons is
  88.8\% (MAIN) and 88.4\% (rubric-free), and roughly half of that support is
  format-decided. No $\rho$ appears here, so no tie convention applies."

### M4 — The rubric is specific, and it is not decisive — §5.3.2 (a) and §5.2.4 (b)

- **Carries:** both halves of link 2→3. Cell-scoped rubrics really are specific to their
  cells (the premise holds), and swapping them for a rubric-free judge changes almost no
  winners (the consequence does not follow).
- **Data:** `build/rubric_null/measures_all.json` (arms `leaf-87` and `random-cell`) and the
  Run A verdict CSVs.
- **Verified:** leaf-87 median 0.138 with 81/87 positive; random-cell median 0.012 with
  7/13 positive; terms present in ≥90 % of rubrics: 0 (leaf) vs 6 (random); Mann–Whitney U
  one-sided asymptotic p = 1.210 × 10⁻⁶; the four-class partition sums to 1,736 and
  same + flip = 1,311; 10 flips.
- **Generator:** `report/Figures/make_rubric_specific_not_decisive.py`
- **What changed:**
  - **Panel (b) replaced entirely** — see §1.4.
  - Panels are now stacked vertically. Side by side, an ECDF and a matrix were competing
    for the same eye at the same size; stacked, each panel gets the full width and the
    two-step argument ("premise holds" → "consequence does not follow") reads top to bottom.
  - Panel titles now state the two halves of the argument in those words.
  - The zero point is explained on the x-axis label ("0 = the rubric says no more about its
    own cell than about any other"), which is the only way the ECDF means anything.
  - The two curves are labelled **on themselves**, with their above-zero counts, instead of
    through a line-glyph key parked in the corner.
- **Caption draft:** "(a) Per-cell rubric specificity --- a rubric's content-term overlap
  with its own cell's queries minus its mean overlap with other cells' --- for the frozen
  artifact's 87 induced cells against 13 size-matched random cells induced by the identical
  procedure. The within-arm subtraction cancels the vocabulary-breadth confound; raw
  own-cell overlap is not comparable across arms. Median 0.138 (81 of 87 above zero) against
  0.012 (7 of 13). Mann--Whitney $U$, one-sided, \emph{asymptotic} method:
  $p = 1.21\times10^{-6}$ (the exact method gives $6.0\times10^{-8}$). Arms are unbalanced
  by design: the null arm cost 13 inductions, and the registered arm-size control gives
  0.134 on a 13-leaf subsample and 0.138 on a 200-draw bootstrap. Lexical measures only ---
  no embeddings, no additional judge calls, and no model data, so no roster applies to this
  panel. (b) The same 1,736 comparisons of Run~A (pilot roster, 8 models) judged with and
  without the cell rubric, partitioned exhaustively into four disjoint classes that sum to
  1,736: both arms picked the same winner (1,301), both tied (228), exactly one tied (197),
  and the winner flipped (10). The arms therefore disagree about \emph{ties} 197 times and
  about \emph{winners} 10 times; of the 1,311 comparisons both arms decided, 99.2\% agree."

- **Standing caveat, carried forward from v2:** `tools/analysis/rubric_specificity_null.py`
  and `build/rubric_null/` are **untracked in version control**. Until they are committed
  this result is one clean checkout from being unsupported.

### M5 — The domain-reordering screen — §5.4.4 `sec:res-law`

- **Carries:** where a partition could detect anything at all. This is the offline,
  judge-free screen that selected the six arena domains.
- **Data:** `mmlu_pro_dataset_cache_v2.db` `eval_results`, reserved split, 11-model band,
  covered pool 3,436 questions, 1,500-draw size-matched permutation null, seed 42.
- **Verified:** all fourteen n, ρ and p reproduce arm (B) of
  `tools/analysis/domain_reorder_screen.py` exactly. Runtime ≈ 2 min (21,000 draws).
- **Generator:** `report/Figures/make_domain_screen.py`
- **What changed:**
  - The title now states the finding ("Eight of MMLU-Pro's fourteen domains rank the models
    differently from the corpus as a whole"). v2's title was a conventions dump.
  - The x-axis now says what high means: "ρ = 1: the domain orders the eleven models exactly
    as the corpus does. Further LEFT = more reordering." Without that line, a reader cannot
    tell which end of the axis is the interesting one — and this axis runs 0.90–1.01, which
    is deeply counter-intuitive for a "reordering" figure.
  - The two verdict blocks are separated by a blank row and named **in the gap**, with their
    counts ("8 of 14", "6 of 14"), instead of by a dashed rule and two labels floating in
    the left margin.
  - The grey null band is keyed once below the last row with a real swatch, in words a
    reader can act on: "what a random question set of the same size does: 5th percentile to
    median of 1,500 draws".
  - Column headers ("permutation p", "questions") added to the right margin, which was
    previously two unlabelled number columns.
- **Caption draft:** "Offline domain screen on the eleven-model length-matched band,
  reserved split (3,436 covered questions): each domain's within-domain ground-truth ranking
  against the band's global ranking, with a 1,500-draw size-matched permutation null
  (seed 42) drawn behind it. Eight of fourteen domains reorder at $p<0.05$; Mathematics
  orders identically to the global ranking ($\rho = 1.000$, $p = 1.000$), which is why it
  was designated the pre-registered null arm. $n$ ranges from 114 (History) to 393
  (Mathematics). Ground truth only: no judge verdict enters this figure, so no tie
  convention applies. The screen uses MMLU-Pro's native labels, not induced cells --- it
  bounds what any partition could show. The six domains marked $\bullet$ ran as arenas; note
  that they ran on the \emph{twelve}-model band, which shares eight models with the
  eleven-model band screened here. The permutation $p$ is stream-dependent: all fourteen
  domains must be walked in sorted order from one \texttt{seed(42)}, and looping over only
  the six arena domains moves Law from $p = 0.008$ to $0.006$."

### M6 — Screen versus arena, six domains — §5.2.7 `sec:res-c5` **(the centrepiece)**

- **Carries:** RQ2. Does removing the partition change the ranking, and does the offline
  screen predict where it will?
- **Data:** the six `ratings_*_paired.db` stores plus `eval_results`; the screen column is
  recomputed from `eval_results` under the registered 14-domain RNG walk.
- **Verified:** all twelve Δρ reproduce the registered table exactly (law +0.0000/+0.0210,
  philosophy +0.0490/+0.0420, history +0.0105/+0.0105, psychology +0.0210/+0.0210,
  math −0.0637/−0.0070, engineering +0.0035/−0.0035) and all six screen p reproduce
  (0.008 / 0.046 / 0.003 / 0.000 / 1.000 / 0.706).
- **Generator:** `report/Figures/make_screen_vs_arena.py`
- **What changed:**
  - **The screen verdict is now the dominant structure.** In v2 the grouping was a thin
    dashed rule with the group names in the *right* margin, past two other number columns —
    so the one comparison the figure exists to make was the last thing the eye found. The
    two blocks are now separated by a blank row and named in bold **in the gap**, at the
    left, in the words of the claim: "SCREEN SAID a partition could matter here (p < 0.05)"
    / "SCREEN SAID there was nothing to find".
  - **Rows are ordered by Δρ within each block**, not by screen p. The v2 ordering was
    neither sorted by effect nor by p and looked arbitrary.
  - **The failed pre-registered prediction is pointed at by name.** Mathematics now carries
    an on-figure callout: "Mathematics was the pre-registered NULL arm. It returned the
    largest effect in the set, and against the registered direction." A reader should not
    have to reach the caption to learn that the registered null arm failed.
  - The x-axis now states both directions in plain words ("RIGHT: judging inside leaf cells
    ranks models better. LEFT: ignoring the partition does."), replacing "positive favours
    per-leaf judging" which requires knowing what MAIN and C5 are.
  - The two tie markers are keyed once below the axis with the reading attached ("the bar
    joining them is the whole tie-convention effect") rather than by two leader lines that
    only annotated one row.
  - The shaded band is labelled with what it means and where it came from.
- **Honesty note on the headline (please read before writing the caption).** The brief
  states the screen "matches the sign of Δρ in six of six tested". I did not put that on the
  figure, because the figure cannot support it as stated:
  - Law is **+0.0000** under ties-half-weighted. A zero has no sign, so "matches the sign"
    is doing generous work there.
  - "Does not reorder" is a null verdict and predicts no sign at all, so Mathematics and
    Engineering cannot *match* a sign — at best they fail to contradict one.
  - Under the pre-registered threshold, three of the four flagged domains are decisive under
    **both** conventions (philosophy, psychology, history), Law is decisive under one, and
    Engineering is inside the band under both and flips sign with the convention.
  The in-figure headline is therefore the strongest claim the data actually carries:
  *"Where the offline screen said a partition could matter, per-leaf judging never ranked
  worse."* Four of four, no sign inversions, and it does not smuggle in a prediction the
  null verdict never made. If "six of six" is to appear in the thesis it should appear in
  prose with the Law-zero and null-arm caveats attached.
- **Caption draft:** "$\Delta\rho = \rho_{\mathrm{MAIN}} - \rho_{\mathrm{C5}}$ on six paired
  arenas, twelve-model length-matched band, both tie conventions (filled circle: ties
  half-weighted; open triangle: ties dropped); the bar joining them is the entire effect of
  the tie convention. Positive favours per-leaf judging. Verdict counts per domain are given
  in the row labels (1,452--6,588). The shaded band is the pre-registered decisive threshold
  $|\Delta\rho| < 0.007$, two Spearman grid steps at $M = 12$. Domains are grouped by the
  offline screen's verdict and the screen's permutation $p$ is given at the right; the screen
  ran on the \emph{eleven}-model band, which shares eight models with the twelve-model band
  the arenas ran on, and that mismatch is a limitation of the design. All four screen-flagged
  domains have $\Delta\rho \ge 0$ under both conventions. Mathematics was designated the null
  arm in advance and returned the largest effect in the set, in the direction favouring the
  partition-free condition; Engineering, also a clean null by the screen, sits inside the
  threshold and changes sign with the tie convention. No Bradley--Terry standard errors are
  shown: every stored BT SE in this pipeline is the clamp constant pending the $1/K^2$
  recompute."

---

## 4. Appendix figures (2)

### A1 — Leaf-size distribution — Appendix A, beside the birth-constraint discussion

- **Carries:** the cells the arena judges within are far from equal, so per-cell power is
  not uniform across the tree.
- **Data:** the frozen snapshot's leaf `queryIds`.
- **Verified:** 87 leaves, median 88, IQR [71, 118] (exclusive quantile method — the
  convention that yields the published values), min 54, max 396, exactly one leaf below the
  birth floor n_min = 55.
- **Generator:** `report/Figures/make_leaf_size_hist.py`
- **What changed:**
  - **It was in colour** (blue bars, orange exception bar, orange floor line, blue IQR
    band). Now greyscale: grey bars, a **hatched** exception bar, black median and dashed
    floor lines, light grey IQR band.
  - The title states the finding rather than the row count.
  - The right tail was previously unexplained — five bars sitting alone past 300 with a
    small "max 396". It now carries the reading: "the largest leaf holds 396 queries —
    4.5× the median, so the arena's per-cell power is far from uniform across the tree".
    That is the reason the figure is in the thesis and it was not stated anywhere on it.
  - "IQR [71, 118]" replaced with "middle half of the leaves: 71 to 118 queries".
  - x-axis relabelled to say explicitly that these are construction assignments, not the
    arena's routing.
- **Caption draft:** "Leaf sizes in the frozen artifact (snapshot 20260727\_042523): 87
  leaves, median 88 queries, middle half 71--118, minimum 54, maximum 396. Sizes are the
  construction assignment, not the arena's routed assignment. The hatched bar is the single
  leaf below the birth floor $n_\mathrm{min} = 55$, which fell there through later merges
  rather than being born under it. No model data and no judge verdict enters this figure."

### A2 — The ρ levels behind the paired contrasts — Appendix, referenced from §5.2.6 and M6

- **Carries:** why this thesis quotes only paired within-run contrasts — because the levels
  move far more than the contrasts do.
- **Data:** the six paired stores plus `eval_results`.
- **Verified:** every one of the twelve registered Δρ is reproduced *as the difference
  between two plotted levels*, so the assertion is on exactly the quantities being drawn.
  The 24 fitted ρ span 0.785–0.965 (spread 0.180); the largest paired contrast is 0.0637.
- **Generator:** `report/Figures/make_rho_levels.py`
- **What changed:**
  - **The point of the figure is now drawn.** v2 stated "the 24 fitted values span 0.785 to
    0.965 while the largest paired contrast is 0.064" in the caption only — the reader had
    to hold two numbers in mind and imagine the comparison. There is now a span arrow
    labelled "these 24 fitted levels span 0.180" and, directly beneath it on the same axis,
    a solid black bar exactly 0.064 wide labelled "largest MAIN-vs-C5 contrast in the
    thesis: 0.064". The three-to-one ratio is a visual fact, not an arithmetic one.
  - The figure title states the conclusion in one sentence.
  - The x-axis says what high means.
- **Caption draft:** "The absolute $\rho$ levels the main-text contrasts are differences of.
  Twelve-model length-matched band, six paired arenas, per-leaf (filled circle) and
  partition-free (open square), (a) ties half-weighted, (b) ties dropped. Verdict and leaf
  counts are in the row labels. The 24 fitted values span $\rho = 0.785$ to $0.965$ (a range
  of 0.180) while the largest paired MAIN-vs-C5 contrast anywhere in this thesis is 0.064,
  drawn to scale beneath the range; the ground-truth vector also differs between rows,
  because each arena judged a different question set. Levels are therefore not comparable
  across rows and only the within-domain, within-run contrast is quoted anywhere. No
  Bradley--Terry standard errors: verdict and leaf counts are given instead."

### A3 — Granularity flatness — **STILL A REFUSAL, do not "fix"**

`report/Figures/make_granularity_flat.py` deliberately recomputes, prints what does and
does not reproduce, and **exits non-zero without emitting a PDF**, because the published
centred-residual quartet reproduces under no single convention. Re-run and confirmed still
refusing on 2026-07-30 (exit 1). All four *observed* between-cell medians reproduce exactly
(0.929 / 0.922 / 0.922 / 0.905); it is the centring convention that is unrecoverable. Leave
it refusing.

---

## 5. Consequences for the `.tex` (I edited none of it)

1. **`6_Results.tex:261–270` must be deleted.** `trace_strata.pdf` no longer exists; the
   float and its `\label{fig:trace-strata}` will break the build. Replace with the two
   sentences described in §1.2.
2. Only three of the eleven v2 figures were ever wired in (`routing_slopegraph`,
   `trace_strata`, `leaf_size_hist`). The six main-text figures still need
   `\begin{figure}` environments at the placements listed above; the caption drafts here are
   ready to paste.
3. `fig:granularity-flat` is referenced at `6_Results.tex:1220` but has no PDF and should
   not get one — see A3.

## 6. Still not buildable (carried forward unchanged from v2 §3)

- **Within-domain vs between-domain between-cell ρ** — HELD. The within-domain arm
  reproduces exactly (median 0.907, IQR [0.852, 0.945], 293 leaf pairs); the between-domain
  arm does not (published 0.937, obtained 0.9422) under any of ten convention combinations,
  and the comparison has no permutation null. Two independent blockers.
- **Per-domain tie profiles across the six paired arenas** — computable, but nothing is
  registered to assert against and the pattern does not replicate the pilot's.
- **Run B "repair by construction" panel** — the pilot's zero-length side no longer exists
  in the repaired corpus and the quoted length/accuracy correlations are not registered.

**Deliberately not visualised, per the brief:** redundancy percentages (72.2 % / 42.2 %);
correctness-blind ρ (0.74–0.76); leaf-level 0.922 on re-routed assignments; the
centred-residual quartet; the within-domain vs between-domain leaf comparison.

---

## 7. Verification log, 2026-07-30

All eight generators re-run from a clean invocation after the rework. Every one recomputes
its numbers from the primary store and raises before drawing on mismatch; no assertion was
weakened, and two scripts gained assertions.

| script | result |
|---|---|
| `make_routing_slopegraph.py` | PASS |
| `make_frozen_tree.py` | PASS |
| `make_verdict_mechanism.py` | PASS |
| `make_rubric_specific_not_decisive.py` | PASS |
| `make_leaf_size_hist.py` | PASS |
| `make_rho_levels.py` | PASS |
| `make_domain_screen.py` | PASS (≈2 min, 21,000 permutation draws) |
| `make_screen_vs_arena.py` | PASS (≈2 min) |
| `make_granularity_flat.py` | REFUSES, exit 1, as designed |
