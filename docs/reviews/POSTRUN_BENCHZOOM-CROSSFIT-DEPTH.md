# POSTRUN review: benchzoom cross-fitted zoom depth + depth calibration (D-2026-10-10-1)

Reviewer: adversarial-reviewer, 2026-10-10. Object: benchzoom `master` cd911f2 (parent f077a4a, base d872d24), local
only. Read-only on benchzoom (`git status --short | wc -l` = 0 before and after; HEAD unchanged). Scratch:
`E:/TaxoArena_tmp/bz_crossfit_review/` (scripts + 220 run JSONs; not committed). Zero LLM calls, no Ollama.
Synthetic data only; this is a library calibration, not a registered TaxoArena readout.

## Verdict
- **cf1 (cross-fit, 1 SE, the library default): NOT RELIABLE.** CONFIRMED (V1 FAIL), recomputed to the digit and
  replicated with an independent generator, seeds and fold seed.
- **cf2 (cross-fit, 2 SE): RELIABLE on the calibration report's criteria V1-V3**, CONFIRMED and replicated, including
  under the harder null asked for (unequal sub-cell difficulty, no model-specific effect). Conditions C1-C3 below must
  go into any adoption text. Whether to adopt it in the demos is the author's call (D-2026-10-10-1). On MATH it changes
  nothing (C3). On MMLU-Pro, expect roughly 1 in 5 null models to show a spurious zoom (C1).
- Leakage: **none found** in the fit (L1-L4 below; 3 own mutants, all killed).

## Per-claim table (deciding claims)
| # | claim (builder) | reviewer number | status | sev |
|---|---|---|---|---|
| 1 | cf1 V1 FAIL: dense null 9.02% [5.93, 11.91] mmlu 0.3; 7.42% math 0.5; 7.21% mmlu 0.5 | 184/2040 = 9.02% [5.98, 12.21]; 227/3060 = 7.42%; 147/2040 = 7.21% (counts to the digit, CI within bootstrap noise). Own generator: mmlu hard_d03 13.33% [9.36, 17.16], math hard_d05 10.00% [8.92, 11.01], mmlu base_d03 8.82% [6.08, 11.52] | CONFIRMED | - |
| 2 | cf2 V1 pass, worst 1.42% (upper 2.06%) | 29/2040 = 1.42% [0.83, 2.01]. Own cells, worst: mmlu hardnull_nosubj 3.48% [2.61, 4.38], mmlu hard_d03 3.09% [1.86, 4.61], ceilnull 2.46% [1.27, 3.80]; all <= 5% with upper <= 8% | CONFIRMED (letter); PARTLY in substance (C1) | HIGH |
| 3 | V2 detection, dense: cf1 115/1080, 183/720, 864/1080, 532/720; cf2 36, 64, 540, 330; reg 0, 0, 152, 104 | identical counts. Own (cf2 vs reg): math base_d03 35/1080 vs 0; math hard_d03 42/1080 vs 0; mmlu base_d03 57/720 vs 0; mmlu hard_d03 70/720 vs 7; math hard_d05 479/1080 vs 117; mmlu hard_d05 275/720 vs 113 (own V2 decided by count; no seed-bootstrap CI computed) | CONFIRMED | - |
| 4 | V3 held-out loss never worse than category-only | builder cache: max (rule - cat)/SE over every cell and cf1/cf2/cf1_lfo = -0.92 (never positive). Own: every cf1/cf2 - cat <= 0 (largest gain -3.81e-4 log-loss, mmlu hard_d05 cf1) | CONFIRMED | - |
| 5 | no leakage: model's own held-out answers do not enter its prediction; fold hyperparameters are not estimated on held-out items | L1-L4 all pass (below) | CONFIRMED | - |
| 6 | pins: meta.json lib LF shas; script blob ff3aee1e | `git hash-object` at HEAD: crossfit fb1aa05d, synthetic c037405c, profile 147bf8d2, irt 0964c8c4 = meta.json; script ff3aee1e = commit message (LF; working tree LF) | CONFIRMED | - |
| 7 | pytest 206 passed, 4 deselected | 206 passed, 4 deselected (80.8 s, `-p no:cacheprovider`, no bytecode) | CONFIRMED | - |

## Leakage probes (own script `leak.py`, math shape, 12 models, K=5, fold seed 11)
- L1: flip model j's own fold-k answers. j's fold-k eta is bit-equal at every depth, and j's eta elsewhere moves (not vacuous).
- L2: flip ALL models' fold-k answers. tau[k] and theta[k] are bit-equal; the other folds' tau move. The shrinkage scale and abilities of fold k never see fold k.
- L2b: under that flip, the change in fold-k eta is constant across depths (range 4.4e-16). Only the held-out difficulty
  (an item property, from the other models' answers) moved; the offsets did not.
- L3: flipping another model's fold-k answers moves j's fold-k eta (the expected item-difficulty path; non-vacuity).
- L4: the folds do not depend on Y (`make_folds` takes no scores; folds are identical under L1/L2 changes).
- Own mutants (scratch copies of `src/benchzoom`, run against `leak.py`):
  MA `fit_offsets(tree, Y, ...)` (offsets see the held-out fold): killed (L1, L2), decisive.
  MB held-out difficulty computed from all models including j: killed (L1), decisive.
  MC `fit_theta(Y[:, j], ...)` (ability fitted on the held-out fold): killed (L1, L2), decisive.
- Remaining non-nesting, disclosed by the builder: the shipped cf read chooses the depth on all items' out-of-fold
  losses. `cf1_lfo` masks fold k's losses, but fold k' (k' != k) predictions were fitted using fold k's answers. LOW.

## Own calibration (`mycal.py`, `analyze.py`, `cond2.py`)
Own generator: Rasch. Sub-cell difficulty is a node mean ~N(0, nb^2) added at every node of depth >= 2, plus item noise
N(0, 1.3^2). Subject offsets are N(0, 0.25^2), and nothing is model-specific below the subjects. Seeds 900000+, fold
seed 3 (the builder used 0), 20 seeds per cell, demo shapes. Cells:
- hardnull: nb 1.0.
- ceilnull: theta mean 1.5 (a ceiling regime).
- base_d03: leaf-only nb 0.5 plus dense mirrored plants E 0.3.
- hard_d03 / hard_d05: hardnull plus dense mirrored plants.
- hardnull_nosubj (mmlu only): subject offsets off, so there is no model effect at all.

"Gate open" means tau(depth 2) > 0 in the full fit or in any fold. With tau = 0 the child offsets are exactly 0, and no
rule can descend.

| cell (unplanted models) | gate open | cf1 all seeds | cf2 all seeds | cf2 open seeds only | cf2 models with any zoom, open seeds | cf3 open | reg |
|---|---|---|---|---|---|---|---|
| math hardnull / ceilnull | 0/20, 0/20 | 0/4140, 0/4140 | 0, 0 | n/a | n/a | n/a | 0 |
| mmlu hardnull | 9/20 | 9.64% [5.11, 14.64] | 2.17% [0.98, 3.41] | 60/1242 = 4.83% [3.62, 6.12] | 53/207 = 25.6% | 0.81% | 1/2760 |
| mmlu ceilnull | 9/20 | 9.17% | 2.46% [1.27, 3.80] | **68/1242 = 5.48% [4.51, 6.36]** | 61/207 = 29.5% | 1.61% | 1/2760 |
| mmlu hardnull_nosubj | 20/20 | 16.59% | 3.48% [2.61, 4.38] | 3.48% | 90/460 = 19.6% | 0.33% | 3/2760 |
| mmlu hard_d03 | 16/20 | 13.33% | 3.09% [1.86, 4.61] | 3.86% [2.57, 5.45] | 55/272 = 20.2% | 0.49% | 9/2040 |
| math hard_d05 | 20/20 | 10.00% | 1.24% | 1.24% | 37/1020 = 3.6% | 0.03% | 0 |

The builder's cache shows the same pattern. Conditional on gate-open seeds, cf1 runs at 13.9-15.6% per pair
(mmlu null 43/276; math dense_0.3 115/765) and cf2 at 1.96-2.54%. In math dense_0.3, 15 of 20 seeds have the gate
closed and contribute 0/0 to every rule.

## Defects / conditions
- **C1 HIGH: the V1 denominator is diluted by gate-closed seeds.** When tau(depth 2) = 0, no rule can zoom, yet those
  seeds still count as "pass" decisions: math pure null 0/8280 reached; own math nulls 0/40 open. The real MMLU-Pro demo
  has tau(depth 2) = 0.12 (`E:/benchzoom_demo/mmlu_pro/summary.json`), so the gate is open there. In that regime cf2's
  per-pair false-zoom rate on a pure-Rasch null is 3.5-5.5%, with ceilnull above the 5% point bar, and 20-30% of null
  models show at least one zoom. Fix:
  - print V1 conditional on tau(depth 2) > 0 beside the all-seed rate, plus a per-model any-zoom rate;
  - adoption text must state the per-model rate;
  - se_mult = 3 holds open-gate per-pair <= 1.61%, at the cost of detection (mmlu hard_d05 79/720 vs reg 113/720, so it no longer beats strict at 0.5).
- **C2 HIGH (upstream, `profile.fit_offsets`): a pure-Rasch null opens the gate.** With difficulty heterogeneity and no
  model effect at all (nosubj), the gate opens in 20/20 seeds, with tau 0.03-0.05 at depth 1 and 0.05-0.10 at depth 2
  (`mech.py`). 18-41% of the depth-2 step-offset variance is common-mode, because tau and D are not centred across
  models. These artefacts improve out-of-fold loss, so V3 cannot catch them. The cross-fit rule turns an
  estimator artefact into zooms; the registered read is protected by BH (3/2760). Fix: estimate tau from
  model-centred raw offsets (or centre D per node across models), then re-run both calibrations.
- **C3 MEDIUM: cross-fit is a no-op on the MATH demo.** The MATH demo has tau(depth 2) = 0
  (`E:/benchzoom_demo/math/summary.json`), so no cross-fit read can descend below the subjects there. The math null
  cells pass by construction (0 reached decisions). Any "adopted in the demos" statement must say so.
- D4 LOW: mirrored plants make unplanted models null only to first order. In real data a large effect in one model
  shifts the others' leave-one-model-out difficulty by about -E/(M-1); the builder's exploratory run saw 47/560 such
  zooms. These are real relative deviations, not false zooms, but users will read them as fingerprints. Disclose in
  docs/defaults.md.
- D5 LOW: the depth choice is not fully nested (see the leakage section). It is disclosed; V3 is unaffected in sign.
- Choosing cf2 after cf1 failed is a selection. The 2-SE line was declared secondary before the runs, and the independent
  replication above removes the multiplicity concern for V1/V2 on these generators. One generator family (Rasch plus
  one 2PL null) remains a limitation.

## Commands
```
cd Z:/FAC/TUBerlin/benchzoom && git status --short | wc -l   # 0 before/after; HEAD cd911f2
git hash-object src/benchzoom/{crossfit,synthetic,profile,irt}.py examples/depth_calibration.py   # vs meta.json lib_lf_sha
PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python -m pytest -q -p no:cacheprovider          # 206 passed, 4 deselected
S=E:/TaxoArena_tmp/bz_crossfit_review; PY=Z:/FAC/TUBerlin/benchzoom/.venv/Scripts/python
$PY $S/recompute.py      # builder cache 520 runs: V1/V2 counts to the digit, V3 max t -0.92
python $S/perseed.py; python $S/cond.py   # per-seed planted/unplanted zooms; gate-open conditional rates (builder cache)
$PY $S/leak.py           # L1-L4; PYTHONPATH=$S/mut/{A,B,C} $PY $S/leak.py for the mutants
$PY $S/mycal.py 20 18; $PY $S/diag.py 20 18; $PY $S/analyze.py; $PY $S/cond2.py; $PY $S/mech.py
```
