# Figure plan

Drafted 2026-07-31, against the 8-model RESOLVED batch (math, physics, law,
engineering complete; psychology running; philosophy, history, CS queued).

Conventions already in force, which every new script must follow:

- `report/Figures/make_<name>.py`, matplotlib with `matplotlib.use("Agg")`,
  output `<name>.pdf` beside the script.
- **Real data only.** Read from the project databases, assert every published
  number before drawing, raise and emit no PDF on mismatch. This is what
  `make_leaf_size_hist.py` does and it is the reason the existing figures can
  be trusted.
- `\graphicspath{{Figures/}}` is set in `01_Document_administration/c_Commands.tex`,
  so `\includegraphics{name}` needs no path.
- Schematics are inline TikZ (three already in `3_Method.tex`); data figures are
  generated PDFs. Keep that division.

---

## 1. Current state

| figure | placed? | where |
|---|---|---|
| `verdict_mechanism` | yes | `5_Results.tex:304` |
| `leaf_size_hist` | yes | `5_Results.tex:640` |
| `rubric_specific_not_decisive` | yes | `5_Results.tex:1028` |
| `domain_screen` | **orphaned** | — |
| `frozen_tree` | restored 2026-07-31 | App. G, `G_Frozen_Taxonomy.tex` |
| `rho_levels` | **orphaned** | — |
| `routing_slopegraph` | **orphaned** | — |
| `screen_vs_arena` | **orphaned** | — |

Chapters with no figures at all: Background (2), Experimental Design (4),
Discussion and Conclusion (6).

Five orphans lost their float wrappers during the chapter restructure. Their
generator scripts still run. Re-placing them is section 4 below and costs
nothing but the float.

---

## 2. New figures

Six proposed. Each entry gives the argument the figure has to carry, why the
chosen encoding beats the obvious alternative, the exact placement anchor, the
data source, and whether it can be built before the batch finishes.

### F1 — `validity_scatter` : the arena tracks the key wherever the key can see

**Carries:** the central RQ1 claim. 102 of 105 key-decidable model pairs
recovered across four domains, one configuration, no per-domain tuning.

**Encoding.** One point per (domain, model pair): x = the key's accuracy gap
`|p_a - p_b|`, y = the arena's Bradley-Terry score difference `theta_a - theta_b`,
signed consistently so that agreement means the point sits in the upper-right or
lower-left quadrant. Filled markers where the key decides the pair, hollow where
it cannot. Shade the undecidable band `|p_a - p_b| <= 2*sqrt(...)` in grey.
Colour by domain. Label the three misses.

**Why this and not a bar chart of 97.1%.** A bar chart asserts the number; the
scatter lets the reader verify it and shows three further things for free: the
relationship is monotone rather than merely rank-consistent, the three failures
all sit at the smallest gaps where the key itself is nearly indifferent, and the
grey band makes the "we only claim decidable pairs" boundary a visible property
of the data rather than a caveat in the prose. It is the single most economical
defence of the thesis's main claim.

**Placement:** `5_Results.tex`, section 5.2.1 `sec:res-correctness` (opens
line 177). Insert the float after the paragraph that states the decidability
criterion, before line 256.

**Data:** `experiment_results/r8/<domain>/ratings_r8_<domain>.db:match_history` (condition MAIN) for theta;
`mmlu_pro_dataset_cache_v2.db:eval_results` for the key. Same BT fitter as the
service (MM, Jeffreys prior at strength 0.5).

**Build gate:** buildable now with 4 domains; regenerate at 8. Prefer 8 — the
point density is what makes the figure work.

---

### F2 — `rubric_vs_generic` : the rubric loses at item level and ties at rank level

**Carries:** RQ2. Identical rankings (drho = 0.0000 in every domain), but on the
same decidable comparison the generic MT-Bench prompt beats the domain rubric
97 to 51, pooled p = 0.0002, and the direction holds in all four domains.

**Encoding.** Two panels.
(a) Slope chart: for each domain a line from rubric agreement to generic
agreement (79.3 -> 82.7, 80.2 -> 83.4, 66.9 -> 69.7, 74.0 -> 76.5). Four lines,
all sloping the same way.
(b) Diverging horizontal bars, one row per domain plus a pooled row: rubric-only-
correct to the left, generic-only-correct to the right, with a binomial CI on
the pooled row.

**Why.** The slope panel makes replication across four independent domains
immediately legible — four parallel lines is an argument a table of eight
numbers cannot make at a glance. The diverging panel supplies the item-level
magnitude and the significance that the aggregate rho cannot express, since rho
is saturated. Together they say precisely what the result is: no effect on the
ranking, a real effect on the verdicts.

**Placement:** `5_Results.tex`, section 5.2.6 `sec:res-c5` (opens line 498).

**Caution — this result contradicts a section title.** Section 5.2.4 is called
"Rubric-Scoped and Rubric-Free Judges Reach the Same Verdict"
(`5_Results.tex:410`). At item level they do not: they disagree on 15-21% of
comparisons and the disagreements break systematically toward the generic
prompt. The title needs to become a rank-level claim, e.g. "Rubric-Scoped and
Rubric-Free Judges Produce the Same Ranking". Fix this when F2 lands.

**Data:** both conditions of `experiment_results/r8/<domain>/ratings_r8_<domain>.db`, joined on
(eval_question_id, model_a, model_b), restricted to key-decidable comparisons.

**Build gate:** buildable now; regenerate at 8. The pooled n roughly doubles,
which is the difference between a suggestive result and a solid one.

---

### F3 — `cell_budget_and_uncertainty` : why per-cell profiles cannot be claimed

**Carries:** the pre-registered Link 3 premise fails, and — critically — the
per-cell scatter that looks like sub-domain specialisation is indistinguishable
from sampling noise. Per-cell fits reorder 9/11 math cells and 9/10 physics
cells, but Cochran's Q finds no significant heterogeneity anywhere
(p = 0.064, 0.502, 0.682, 0.137).

**Encoding.** Two panels sharing the causal story.
(a) Strip or dot plot, log x-axis: comparisons per model pair achieved in each
cell, grouped by domain, with a vertical rule at the ~143 the resolution
criterion requires. Every cell sits 30-90x short; none qualifies.
(b) Caterpillar: per-cell BT score of the top model with 95% CI, cells sorted,
pooled estimate as a horizontal line. Every interval crosses the line.

**Why.** This is the figure that protects the thesis. A reader who sees only the
per-cell point estimates will conclude specialisation is real; panel (b) shows
the intervals swallow the differences, and panel (a) explains why in one number.
Presenting the caution visually is far more credible than a sentence conceding
it, and it forecloses the obvious hostile reanalysis.

**Placement:** `5_Results.tex`, section 5.3.4 `sec:res-granularity`, "Link 3's
Premise Fails, and It Was Pre-Registered" (opens line 1116).

**Data:** `match_history` grouped by `node_id`; CIs by bootstrap over
comparisons within cell (1000 resamples, percentile method) — state the method
in the caption, since the BT SE is unreliable at these counts and diverges in
cells where a model went undefeated.

**Build gate:** buildable now; regenerate at 8.

---

### F4 — `rank_recovery_grid` : the whole batch on one page

**Carries:** the breadth claim — 8 models x 8 domains, one configuration.

**Encoding.** Heatmap, models (rows, ordered by pooled key accuracy) x domains
(columns). Cell colour = signed rank displacement between arena and key;
annotate with the arena rank. Diverging colormap centred at zero, so a mostly
white grid *is* the result. Mark undecidable cells with a hatch.

**Why.** Eight per-domain slopegraphs would not fit and would not be compared;
one grid makes the pattern and its exceptions visible together, and the hatching
keeps the decidability caveat attached to the evidence rather than to a footnote.

**Placement:** `5_Results.tex`, section 5.1 `sec:res-runs` (opens line 62), as
the chapter's orienting figure — or section 5.4 `sec:res-summary` (line 1462) if
you would rather it close than open. Prefer 5.1: it tells the reader what the
evidence base is before any argument is made on it.

**Build gate:** **needs all 8 domains.** Do not build a 4-column version.

---

### F5 — `design_schematic` : split, routing, and what the two arms share

**Carries:** the experimental design, and specifically the fact that C5 replays
MAIN's triples under MAIN's cells — so it varies the rubric and nothing else.

**Encoding.** Inline TikZ, left to right: 12,118 questions with eval coverage ->
70/30 split -> 8,673 construction (tree induction + hyperparameter tuning, drawn
as one box to make the shared use explicit) and 3,445 held-out -> routing ->
cells -> the two arms drawn as two rubrics reading *the same* triple set.

**Why here and why TikZ.** Experimental Design currently has no figure, and the
one thing reviewers have repeatedly misread is what C5 isolates. A schematic
that draws the shared triples answers that before the prose has to. It is
structure, not data, so it follows the Method chapter's TikZ convention.

**Placement:** `4_Experimental_Design.tex`, immediately after the 70/30 split
description. Note the open `% TODO(author)` at line 398 asking for C5 to be
renamed — resolve the naming first, then draw the box with the final name.

**Build gate:** buildable now; only the counts are fixed, and they are settled.

---

### F6 — `judge_verdict_composition` : where the verdicts go

**Carries:** the denominator behind every agreement figure — of all comparisons,
what fraction the key can decide (53-57%), what fraction the judge ties
(16-20%), and how the decidable remainder splits into agreement and
disagreement.

**Encoding.** Stacked horizontal bars, one per domain, segments: key-undecidable
/ judge tie on decidable / judge agrees / judge disagrees.

**Why, and whether to include it at all.** This is the figure that makes the
79.3% and the 55.7% the same number seen two ways, which is exactly the
confusion the agreement-metric defect created. Include it if the reviewer
audience is likely to challenge the denominator; **cut it** if the figure count
is getting heavy, since the caption of F1 can carry the same point in a
sentence. Lowest priority of the six.

**Placement if kept:** `5_Results.tex`, section 5.2.1, directly after F1.

**Build gate:** buildable now.

---

## 3. Priority

1. **F1** — the main claim, and nothing else currently visualises it.
2. **F3** — protects against the strongest available criticism.
3. **F2** — the sharpest new finding.
4. **F5** — cheap, and Experimental Design has nothing.
5. **F4** — high value, blocked on the batch.
6. **F6** — optional.

---

## 4. Re-place the five orphans

No new work; each needs a float restored in the section that now owns its
content.

| figure | restore to | anchor |
|---|---|---|
| ~~`frozen_tree`~~ | done — now opens App. G | — |
| `routing_slopegraph` | 5.3.2 `sec:res-adapted-partition` | line 885 |
| `domain_screen` | 5.3.6 `sec:res-law` | line 1309 |
| `screen_vs_arena` | 5.3.6 `sec:res-law`, after `domain_screen` | line 1309 |
| `rho_levels` | 5.2.5 `sec:res-rho-stability` | line 476 |

**Check `rho_levels` before restoring it.** Section 5.2.5 concerns the stability
of rho, and the `% TODO(author)` at `4_Experimental_Design.tex:67` records that
the rho threshold was **withdrawn** after two identical-configuration runs
disagreed. If the figure draws that threshold it must be regenerated or dropped,
not merely re-placed. The other four are safe.

---

## 5. Resulting inventory

| chapter | figures |
|---|---|
| 1 Introduction | 0 (fine) |
| 2 Background | 0 — acceptable for a master's thesis; add nothing merely to fill |
| 3 Method | 3 TikZ (existing) |
| 4 Experimental Design | **F5** |
| 5 Results | `verdict_mechanism`, `leaf_size_hist`, `rubric_specific_not_decisive`, + 4 restored orphans, + **F1 F2 F3 F4** (+ F6 optional) |
| 6 Discussion and Conclusion | 0 — it argues from Chapter 5's figures; cross-reference rather than duplicate |
| App. G The Frozen Taxonomy | **built** — `frozen_tree` (orphan restored) + `tree_panels_1..4` + `tree_table` |

Eleven to thirteen figures total, ten of them in Results. That distribution is
right for a thesis whose contribution is empirical.

---

## 6. Build order

Nothing final should be generated from four domains. Build the scripts now
against the four completed domains so the code is debugged and the assertions
are written, then regenerate every figure once `BATCH COMPLETE` appears — the
assert-before-draw convention means a script that silently changes meaning when
the data grows will fail loudly instead.

F5 is the exception: its numbers are fixed and it can be drawn and placed today.
