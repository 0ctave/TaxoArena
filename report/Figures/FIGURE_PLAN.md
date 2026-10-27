# Figure plan — superseded

This plan was drafted 2026-07-31 against the first four domains of the
settled batch and is **superseded** by
`docs/figure-table-review-2026-07-31.md`, which reviews every placed
figure and table against the completed batch and specifies the current
visualisation set. The withdrawal of the pilot (Run A) and the
twelve-model campaign the same day voided this plan's numbers (F2's
97:51 sign test, F1's 102/105) and its orphan-restoration section.

## Current state (2026-07-31, end of day)

Placed data figures, all settled-batch or offline-valid, each generated
by an assert-before-draw `make_<name>.py` beside its PDF:

| figure | where | claim |
|---|---|---|
| `settled_validity_scatter` | 5_Results `sec:res-correctness` | 196/200 monotonicity; misses at the smallest gaps |
| `tie_signature` | 5_Results `sec:res-tie-signature` | 13.0%→24.0% abstention doubling, 8/8 domains, both arms |
| `rubric_reach` | 5_Results `sec:res-offsubject` | rubric applied far outside its pool; the judge does not care |
| `budget_vs_resolution` | 5_Results `sec:res-cost` | identification free (7–10), resolution out of reach (~143 vs 1.6–5.1) |
| `rubric_specificity_null` | 5_Results `sec:res-rubric-null` | rubrics cell-specific vs randomised null (offline; replaces the two-panel version whose panel (b) drew pilot verdicts) |
| `rank_recovery_grid` | 5_Results `sec:res-runs` | the batch on one page: 45/64 cells white; each column reproduces its published rho |
| `discordance_split` | 5_Results `sec:res-c5` | RQ2's two effects kept apart: 8 tie slopes + the 11/26 split with exact CI |
| `leaf_size_hist` | 5_Results `sec:res-construction` | leaf-size distribution of the frozen tree |
| `frozen_tree` | App. G | icicle overview of the frozen taxonomy |
| `tree_full` | App. G | all 87 leaves, labelled, one page |
| judge example (`judge_example.tex`) | App. B | one real induced judge, generated from the snapshot |

TikZ schematics: three in 3_Method; the design schematic
(`fig:design-schematic`, shared-triples fact) in 4_Experimental_Design.

Retired 2026-07-31 (pilot/12-model era; recover from git history if
ever needed): `verdict_mechanism`, `trace_strata`, `rho_levels`,
`screen_vs_arena`, `domain_screen`, `routing_slopegraph`,
`rubric_specific_not_decisive` (two-panel version).

Held, unplaced: `routing_provenance.pdf` — current data but its
"on-subject" convention (leaf-dominant) disagrees with the chapter's
anchor-level 77.8%; reconcile conventions before placing or retire.

V-5 and V-8 were built and placed 2026-07-31 (evening); nothing from the
review's recommended set remains open.

Conventions unchanged: `make_<name>.py`, `matplotlib.use("Agg")`, real
data only, assert every published number before drawing, raise and emit
no PDF on mismatch; `\graphicspath{{Figures/}}`; schematics are TikZ,
data figures are generated PDFs; no BT confidence intervals anywhere.
