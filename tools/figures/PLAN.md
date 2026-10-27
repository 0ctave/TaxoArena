# TaxoArena Visualization Program — Figure Specification

(Agent-designed 2026-09-07 from the committed campaign record: ledger, blog drafts,
all outcome files. Palette machine-validated for CVD. This file is the build spec
for figures/blog and figures/paper; one fig_*.py per figure + shared style.py.)

## Series-wide conventions [CONV]
- Model colors are fixed identities across ALL figures. Frontier-4 carry hue; the
  tail carries a gray ramp + direct labels. Red is NEVER a model color — reserved
  for the diverging negative pole and wrong-sign marks.
- Two-flavor uncertainty: thick whisker = match-level SE; thin extended whisker =
  query-level SE (match SE x sqrt(deff), per-stratum deff from H6b).
- Provenance badges: filled square REGISTERED (#2F6B4F) vs hollow EXPLORATORY
  post-hoc (#9A6A1F), top-right of every inferential figure.
- Footer line (7pt muted): n, test, data file.

## Figure catalog (blog)
- P1-F1 [S] Ranking-recovery slopegraph — arena vs GT rank, 12 rows; left column
  positions by BT theta on a TRUE log-odds scale (top-4 physically crowd); only
  the two crossings get saturated strokes; bracket the top-4 with the 40-49%
  tie-rate note. Header: rho=0.951, tau=0.848, 9,144 = 4% of exhaustive.
  Data: ratings_x12.db + reserved GT. Social-card crop 2:1.
- P1-F2 [A] Matches-per-cell-pair histogram, log-y; rules at mean 1.6 / median 1 /
  p90 5; stat tile "9,144 / 227,000 ~ 4%". Census — no uncertainty needed.
- P2-F1 [A] 87-leaf radial tree; leaf dot area ~ question count; HOLLOW dots =
  leaves founded by splits the honest null cannot certify; the 6 profile-split
  anchors get a subtle accent arc; label ~10 curated evocative leaves only.
- P2-F2 [A/S] The two nulls: observed split separations vs n (log-x); isotropic
  p95 curve + within-node null band (data swap when the re-derivation lands) +
  bar 0.025 rule; three-zone background wash; open markers where null censored.
- P2-F3 [S?] Bar-collapse: stacked shared-x panels (NOT dual axis): leaf count
  94/90 -> 87 -> 19-20 -> 16 over bar {0.015, 0.025, 0.045, 0.07}; below,
  held-out Top-1 with the n=20 seed-floor ribbon; washes rhyme with P2-F2.
- P3-F1 [A] Double-count mechanism: annotated 3-step flow with a worked match,
  erroneous +0.5 in red; caption: 7 conservation tests guard it.
- P3-F2 [A] Blast radius strip plot: pooled-path deltas hugging 0 vs 22 per-leaf
  |dtheta| dots to 0.43 (13 rank-changers red-ringed); the unrepairable-design
  limitation as a weighted text block.
- P4-F1 [A] Campaign map: timeline-grid of every experiment with type/outcome
  chips (ledger palette verbatim); nulls at EQUAL weight; p-values as text.
- P4-F2 [S?] The peek that lied: running (cell-generic) diff vs % collected,
  peek at ~17% flagged (-1.1pp, opposite sign), freeze commit as lock glyph at
  x=0, pointwise 95% band = the lesson.
- P5-F1 [S?] Rubric specificity gradient, two panels (different samples never
  share an axis silently): A cell-vs-generic dumbbells (Mistral +1.5pp p=1e-4,
  grok +2.4pp p=0.021); B placebo trilogy random 74.9 -> cell 77.0 (p=0.006) +
  shared-subset ladder 76.2 <= 76.4 <= 77.9 "monotone, as registered".
- P5-F2 [A] Cross-family scatter: Mistral vs grok theta on the identity line, SE
  crosshairs, the one adjacent swap labeled; stat tile 97.8%.
- P5-F3 [B] Per-anchor rubric gain dot plot (qual filled / quant hollow), wide
  CIs shown, loud EXPLORATORY tag; cut before diluting its warnings.
- P6-F1 [S] ATLAS heatmap 12x20: ROW-CENTERED deltas (not raw theta) + left
  marginal mean-theta strip; diverging blue/red, gray midpoint; SE-aware dot in
  cells with |delta| < 2 SE; Business columns dagger = pilot-disclosed; rows by
  mean theta, split-anchor sub-columns bracketed; header carries the guarantee
  (240 cells at SE <= 0.15; deff disclosure).
- P6-F2 [S] Verbosity bias: A scatter mean length vs arena-minus-GT residual
  (r=+0.37, thin gray fit, three protagonists labeled, beta_len annotation);
  B small-multiple slopegraphs for x12 AND R2 "all -> length-matched" with a GT
  reference column (the gemini-over-iask crossing appears twice); C (paper) the
  failed length-instruction dumbbell "NOT SUPPORTED — not promptable-away".
- P6-F3 [A] Registered-question deltas: per-model math-lawpsych, filled R2 vs
  hollow x12 (pairs coincide = reproduced at 4x data), GT-sign glyphs, frontier
  block isolated; both SE flavors.
- P6-F4 [A] Observed LRT 60.24 vs BOTH permutation nulls (match-level and
  question-level histograms, same hue two steps); p=0.001/0.002 as text.
- P6-F5 [B] Design-effect dumbbells per stratum, rule at 0.15, median 2.0x /
  worst 3.7x.

## Paper mapping
PF-1 pipeline schematic (SVG/TikZ, the only non-matplotlib item; the "GT enters
once, at the end" arrow drawn OUTSIDE the loop) - PF-2=P1-F1 - PF-3=P2-F2 -
PF-4=P2-F3 + mcs side panel - PF-5=P6-F1 with cell numbers - PF-6=P6-F3 + the 4
registered contrasts (2 OK / 2 wrong-sign at equal weight; Business hatched) -
PF-7=P5-F1 - PF-8=P6-F2 three-panel - PF-9 tree-vs-DAG: E1 observed-vs-null +
E2 forest (P-T +0.019, B-T +0.005, D -0.0141 CI [-0.0244, -0.0037]) - PF-10 H1
null forest (deliberately boring, appendix) - PF-11=P6-F5 - PF-12=P4-F2.

## Signature three
1. P6-F1 atlas (row-centering + marginal strip is the load-bearing decision)
2. P6-F2 verbosity (the generalizable finding; panel C = most quotable line)
3. P1-F1 slopegraph (true log-odds spacing makes tier-compression geometric)
Runner-up bar-collapse excluded: it needs P2-F2 context; signatures stand alone.

## Honesty devices
Dual-SE whiskers; registered/exploratory badges; disclosed peeks PLOTTED as data
(the 17% peek point, Business daggers, round-38 tick); wrong signs at full
weight; no significance stars anywhere — nulls shown as histograms + observed
rule; empirical seed-floor bands over parametric CIs; censoring as open markers;
footers with n / test / data file; scope-limit captions (E2 edge-bridges-only;
one-benchmark transfer caveat on the slopegraph).

## Tech
matplotlib-only (radial tree = manual polar recursion; campaign map = patches).
tools/figures/style.py = rcParams + palettes + dual_se_errorbar() + badge();
fig_*.py read ONLY committed artifacts; build_all.py; deterministic, no network.
Palette (light-surface, validator-passed): gemini #2a78d6, iask #eb6834, gpt-4o
#1baf7a, arx #4a3aa7, deepseek #e87ba4, Qwen72B #eda100, L3.1-70B #008300,
tail-5 gray ramp #4a4a48 / #6b6a67 / #898781 / #a5a49e / #c3c2b7. Direct-label
ALWAYS (three hues are sub-3:1 on light). Sequential blue ramp #cde2fb->#0d366b;
diverging blue/red with gray mid #f0efec. Figures render on a fixed near-white
#fcfcfb card in BOTH blog themes (the dark-variant palette FAILS validation —
do not ship dark PNGs). Fonts: Public Sans (bundle TTFs), IBM Plex Mono for
ticks/footers. Blog: 8in @ 200dpi PNG + 1200x600 social crops for P1-F1/P6-F2.
Paper: PDF fonttype 42, 6.5in/3.2in widths, minimum 6pt.

## Anti-catalog (do NOT build)
12-line spaghetti atlas - bar charts of BT strengths (arbitrary zero) - a
p-value chart of the confirmation chain - dual-axis leaf/Top-1 overlay -
UMAP/t-SNE of embeddings as "proof" of structure (argues against the series'
own lesson) - any agreement pie.

## Build order
Signature three -> P2-F2 + P2-F3 as a designed pair -> P4-F2, P5-F1 -> paper
extras (PF-1 SVG last). P2-F2's within-node band is blocked on the frozen-
artifact null re-derivation: build against the within_node_null_splits.csv
schema now so the refresh is a pure data swap.
