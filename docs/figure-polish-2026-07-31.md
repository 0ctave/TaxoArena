# Figure polish pass — 2026-07-31

Scope: the ten generated data figures in `report/Figures/`. Every figure was
rendered to PNG (`pdftoppm -r 110`), read, fixed where needed, regenerated,
and re-read. All assert-before-draw checks are untouched and all scripts
still print their verification lines. No `.tex` file was edited; caption
changes the coordinator must apply are listed per figure and collected at
the end. The mid-pass examiner figure review was folded in; its in-scope
priority fixes (1, 2, 3, 4, 5, 7) are all addressed below.

Color policy applied: one accent hue, muted blue `#3B6EA5` (light tint
`#A9C4E0`), used only where it carries the figure's core claim, always
redundantly encoded (position/shape/printed value), grayscale-safe.

---

## 1. settled_validity_scatter (Fig 5.2) — CHANGED

Defects found (from render):
- The four miss labels ("physics/psychology/law/law") were placed with one
  shared offset; the misses cluster at gap 0.098–0.157, y −0.01…−0.76, so
  the labels stacked on top of each other (reviewer priority 3).
- Undecidable pairs were hollow circles — the filled/hollow channel that
  figs 5.3/5.5 use for *arm identity* (reviewer priority 7).
- "agreement with the key" floated without indicating it names the +y
  direction.

Changes:
- Miss labels now sit in a stacked column in the empty lower-middle region
  (x = 0.26, y = −0.05…−0.95), each with a thin leader line to its point.
- The four misses are drawn as accent-blue dots with white edge (redundant:
  they remain the only filled points at y ≤ 0, and each is labelled).
- Undecidable pairs are now small light-grey diamonds (shape + value
  channel), freeing filled-vs-hollow for arm identity document-wide.
- Direction cue: "↑ agreement with the key".

Verification: re-rendered; no label overlap, misses clearly visible, counts
line unchanged ("verified: 224 pairs, 200 decidable, 196 recovered, 4
misses").

CAPTION CHANGE REQUIRED (fig:settled-validity, 5_Results.tex ~l.244):
- "Filled points are the $200$ key-decidable pairs; hollow points the $24$
  undecidable ones" → e.g. "Black points are the $200$ key-decidable
  pairs; small grey diamonds the $24$ undecidable ones."
- "The four misses --- labelled ---" → "The four misses --- in blue,
  labelled ---".

## 2. tie_signature (Fig 5.3) — CHANGED

Defects found:
- x-label printed a literal backslash: "tie rate (\%)".
- x-axis ran to −5 (implying negative tie rates) because domain labels
  were drawn at negative data coordinates.
- Right-margin ratio labels trailed each arrow at varying x — ragged.
- History's ratio printed 1.4× while Table 5.4 says 1.5 (reviewer
  priority 2: the table's ratio column is the quotient of the
  0.1pp-rounded rates; the figure divided unrounded rates).
- Pooled row not separated from the eight domain rows.

Changes:
- Label fixed to "tie rate (%)".
- Domain names moved to y-tick labels (outside the axes); x-axis now
  starts at 0 with ticks 0–30.
- Ratio labels aligned in a fixed column at x = 31.2.
- Ratio computation harmonized with tab:tie-by-key:
  `round(mu,1)/round(md,1)`. I verified this rule reproduces all nine
  table rows (2.1, 2.5, 1.7, 1.5, 2.0, 1.9, **1.5**, 1.3, 1.8) exactly.
- Light rule above the pooled row; pooled tick label bold.

Verification: re-rendered; history now reads 1.5×, all ratios match
Table 5.4; assertion line unchanged. No caption change needed (caption
already says "right-margin labels giving the cell-scoped ratio").

## 3. budget_vs_resolution (Fig 5.6) — CHANGED

Defects found:
- Dots within a domain row overprinted (near-identical per-pair values);
  the count "one dot per cell" was not visually recoverable.
- The identification annotation was checked against history/cs rows: it
  ends at x ≈ 2.5, the nearest dots start at x ≈ 2.9 — no collision, left
  in place. The empty middle band is the figure's argument — kept.

Changes:
- Deterministic vertical stagger: per domain, sorted values get cycling
  offsets (0, ±0.13, ±0.26). Dots are now individually countable.

Verification: re-rendered; beeswarm-like rows, no cross-row ambiguity,
assertion line unchanged. No caption change needed.

## 4. rank_recovery_grid (Fig 5.1) — CHANGED

Defects found (reviewer priority 4):
- Sign was carried only by grey value (dark −, light +) and the printed
  digit; +1 and +2 had the *same* fill, so the +2 psychology cell was not
  visually distinct and the mirror-image +/− row pattern didn't pop.
- Undecidable circles were tiny (ms 2.6) and nearly invisible on dark
  cells (grey 0.45 on grey 0.25).

Changes:
- Diverging fill within the one-accent policy: negative = dark grey
  (unchanged), +1 = light blue `#A9C4E0`, +2 = deep blue `#3B6EA5` with
  white text. Redundant: every displaced cell still prints its signed
  offset, so sign and magnitude survive grayscale printing.
- Circles enlarged to ms 3.4 and drawn white on dark fills.
- In-figure legend line updated: "white = arena rank equals key rank;
  displaced cells print the signed offset (blue +, dark −); ∘ = in an
  undecidable pair there".

Verification: re-rendered; the gpt-4o (+) and arx_0314 (−) mirror rows now
read at a glance; +2 clearly distinct; circles visible everywhere;
assertion line unchanged ("every domain's grid reproduces its published
rho; 45 of 64 cells white").

CAPTION CHANGE RECOMMENDED (fig:rank-recovery-grid, 5_Results.tex ~l.165):
after "White is exact agreement ($45$ of $64$ cells)", add a clause such
as "; blue cells are displaced up, dark cells down, and the single $+2$
(psychology) carries the deeper blue."

## 5. discordance_split (Fig 5.5) — CHANGED

Defects found:
- Panel (b) x-label was clipped at the PDF's right edge (matplotlib
  under-measures the long one-line mathtext label under bbox_inches=tight).
- Panel (b) was the reviewer's "weakest panel in the thesis" (priority 1):
  a single count on an axis running −20…+40, labels floating free.
- Panel (a)'s eight slopes were unlabelled.

Changes:
- Panel (b) rebuilt as a plain two-bar comparison: cell-scoped-only = 11
  (filled dark bar), generic-only = 26 (hollow bar — arm identity keeps
  the filled/hollow convention), exact binomial 95% CI whisker on the
  generic-only count, dotted "even split" rule at n/2 with an in-panel
  note carrying p = 0.020. No negative axis. Count labels placed clear of
  the whisker; "even split" label gets a white backing so the dotted rule
  doesn't strike through it.
- Two-line x-label (fixes the clipping).
- Panel (a): the two extreme domains (law, physics) are named next to
  their generic-arm endpoints.

Verification: re-rendered; nothing clipped, no collisions; assertion line
unchanged ("discordant 11/26, p=0.020"). Checked the existing caption
(5_Results.tex ~l.571): it describes the split and the interval
generically and still matches the new panel — NO caption change strictly
required. Optional: add "(bars)" or mention that the extreme domains are
labelled in panel (a).

## 6. rubric_specificity_null (Fig 5.8) — NO CHANGES

Read the render: dashed-vs-solid CDFs, marked medians, interpreted zero
line, p-value annotation — all clean, fonts consistent. The reviewer's
"annotate n = 13 on the null curve" is already satisfied: the label
attached to the dashed curve reads "13 size-matched RANDOM cells … (7 of
13 above zero)". Left untouched.

## 7. rubric_reach (Fig 5.4) — CHANGED

Defects found:
- Panel (b): the zero line struck through the italic group label
  "agreement with the key" (verified in a 220 dpi zoom).
- The two "difference" rows — the rows the claim rests on — had the same
  visual weight as the component rows (reviewer's explicit fix).

Changes:
- Both group labels get a white backing box drawn above the zero line.
- Each difference row is promoted: light shaded band behind the row,
  heavier CI rule (1.7 vs 1.1), slightly larger square marker.

Verification: re-rendered; difference rows clearly dominant, no
line-through-text; the long VERIFIED block of published values prints
unchanged. No caption change needed (panel (a) untouched).

## 8. leaf_size_hist (Fig 5.7) — CHANGED

Defects found (reviewer priority 5):
- Cluttered: four annotation blocks + dashed floor + median line + IQR
  band + hatched bar, with two long diagonal leader lines crossing the
  plot body; the 396-query tail compressed the body into the left third
  of a linear axis; in-figure two-line title (no other figure has one).

Changes:
- Log-scale x with log-spaced bins; the first bin [50, 55) is by
  construction exactly the below-floor leaf (asserted:
  `counts[0] == len(below) == 1` — an added check, nothing weakened).
- Cut to two annotations: (i) the below-floor leaf (now also naming the
  dashed floor, replacing the rotated side label), (ii) the 396 outlier
  and its power consequence. IQR band and its annotation removed — the
  caption already states IQR [71, 118].
- In-figure title removed for style consistency with the other figures.
- Median line kept with its small "median 88" tag (it gives "4.5× the
  median" its scale).

Verification: re-rendered twice (first pass had an arcing leader line —
straightened to a short horizontal leader to the floor line); body of the
distribution now fills the width; VERIFIED block prints unchanged.

CAPTION CHANGE REQUIRED (fig:leaf-size-hist, 5_Results.tex ~l.718): the
removed title line carried a fact the caption does not: add "Counts are
the construction assignment, not the arena's routing" (the caption
already names the frozen snapshot). Optionally note "log-scale axis"
(also stated in the axis label itself).

## 9. frozen_tree (Fig G.1) — NO CHANGES

Verified in render + 300 dpi zoom: the "ran as an arena (8 of 14)" legend
renders, and exactly the 8 arena anchors (Math, Physics, History,
Psychology, Engineering, Computer science, Law, Philosophy) are bold with
a black tick bar. Row heights, per-anchor leaf/query counts, and the
depth headers all render cleanly.

## 10. tree_full (Fig G.2) — NO CHANGES

Page size confirmed exactly 393.17 × 543.6 pt. Zoomed the longest label
("…Thermodynamic and Kinetic Gas Properties in Astrophysical and
Terrestrial Systems", Physics) at 300 dpi: it ends with margin to spare;
nothing clips at any edge. Fonts left at 5.2 pt per the page-fit
constraint.

---

## Caption changes for the coordinator (.tex, not edited by me)

1. **fig:settled-validity** — "hollow points the 24 undecidable ones" →
   "small grey diamonds the 24 undecidable ones"; "The four misses ---
   labelled" → "The four misses --- in blue, labelled".
2. **fig:rank-recovery-grid** — add the blue-up / dark-down clause and
   that the single +2 carries the deeper blue.
3. **fig:leaf-size-hist** — add "Counts are the construction assignment,
   not the arena's routing" (fact lost with the removed in-figure title).
4. **fig:discordance-split, fig:tie-signature** — checked; existing
   wording still matches the new drawings, no change required.

## Reviewer items outside this pass's scope (for the coordinator)

- Fig 3.1 lane tinting / loop label, Fig 3.3 feedback-arrow routing,
  Fig 4.1 top-third trim: TikZ/.tex diagrams, not generated figures.
- G.2 subset lifted into §5.3.1 as an inset: .tex layout decision.
- Bold one-line takeaway at the head of long captions: .tex.
- make_routing_provenance.py remains on hold (convention conflict);
  make_judge_example.py (text) and make_granularity_flat.py (deliberately
  empty) untouched per instructions.

## Scripts changed

- report/Figures/make_settled_validity_scatter.py
- report/Figures/make_tie_signature.py
- report/Figures/make_budget_vs_resolution.py
- report/Figures/make_rank_recovery_grid.py
- report/Figures/make_discordance_split.py
- report/Figures/make_rubric_reach.py
- report/Figures/make_leaf_size_hist.py

(unchanged: make_rubric_specificity_null.py, make_frozen_tree.py,
make_tree_full.py)

All seven regenerated PDFs verified by re-render; every script's
assert-before-draw checks and printed verification lines are intact.
