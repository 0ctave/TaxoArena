# F-series — free tests on existing data (registered 2026-09-08, before running)

Motivated by the D1 / ladder / J-series results. Zero judge calls; every input is a
committed artifact or a local cache. Harness: tools/analysis/free_tests_f.py.

## F1 — certified-vs-uncertified split of the rubric ladder
Data: leaf-rubric verdicts = x12 MAIN (Mistral, cell rubric) and anchor-rubric verdicts =
rubric_ladder.db arm 'anchor', paired on the same matches (the ladder's own pairing);
key-decidable matches only (eval_results.is_correct differs between the two contestants);
ties count as wrong (ladder convention). Certification = docs/data/site_null_frozen.csv
(6 certified sites: Chemistry, Math, Business, Engineering, Biology depth-1; one depth-4
Math site).
Strata: CERTIFIED-STRICT = the leaf's whole anchor->leaf path consists of certified splits
(i.e. depth-2 leaves under the five certified anchors); CERTIFIED-IMMEDIATE = the leaf's
own parent split is certified (adds the depth-4 site's leaves); UNCERTIFIED = the rest.
REGISTERED PRIMARY: leaf-over-anchor gain (correct-verdict rate difference) is POSITIVE in
CERTIFIED-STRICT with McNemar p < 0.05, AND exceeds the gain in UNCERTIFIED (difference
of paired gains, 2,000-fold question bootstrap CI excluding 0). Immediate definition is
the secondary. Power is limited (certified questions are a minority of the 2,000 ladder
matches); a null with a wide CI is reported as underpowered, not as "no effect".
Prediction: the ladder's leaf ~ anchor null was driven by uncertified leaves; certified
leaves show a positive gain.

## F2 — keyed capability profile: embedding cells vs MMLU-Pro categories
Data: eval_results.is_correct for every model with >= 95% coverage of the 12,118 keyed
questions; partitions: (a) MMLU-Pro category (14); (b) frozen-tree depth-1 anchor
(14; train side from the snapshot's leaf queryIds joined by TEXT via embeddings_cache
queries.raw_text -> eval_results.question_text, reserved side from
reserved_leaf_assignments.csv primary leaf); (c) frozen-tree leaf (87); (d) the 20
strata (strata_profile_v1.json). Statistic per (model, partition): leave-one-question-out
Brier score of predicting the model's correctness from its cell accuracy, relative to
the model's marginal accuracy (improvement > 0 = the partition carries information;
LOO penalises many-cell partitions automatically, so k need not be matched).
REGISTERED PRIMARY: mean improvement over models is larger for ANCHORS than for
CATEGORIES (paired over questions, 2,000-fold bootstrap CI excluding 0), on ALL
questions AND on the DISAGREEMENT subset (questions whose anchor != category).
SECONDARY: leaves (c) and strata (d) vs categories, same statistic. Prediction: anchors
~= categories overall (they share ~72% of assignments) but anchors win on the
disagreement subset; leaves beat categories only if sub-anchor cells are informative —
given the ladder and P2, I predict leaves do NOT beat categories on LOO Brier.

## F3 — judge confidence calibration
Data: R2 live verdicts (27,657) with per-verdict confidence (mean of the two orders);
key-decidable decisive verdicts; correctness = verdict matches the key.
Statistics: reliability table (10 bins), ECE, and AUC of confidence for verdict
correctness with a 2,000-fold bootstrap CI.
REGISTERED: confidence is INFORMATIVE iff AUC's CI excludes 0.5 and ECE < 0.10.
Descriptive: a confidence-weighted BT board (weight = confidence) vs the raw board —
rho vs GT and top-4 violations. Prediction: weakly informative (AUC 0.55-0.60),
over-confident (ECE > 0.10 given the prompt's "default to 0.7-0.85" instruction), and
the weighted board changes nothing in the top cluster.

## OUTCOMES (2026-09-08; harness tools/analysis/free_tests_f.py; output experiment_results/free_tests_f_output.txt)

- **F1 — direction as predicted, UNDERPOWERED as registered.** CERT-STRICT n = 48:
  leaf 0.792 vs anchor 0.750 (gain +0.042; discordant 2:0, McNemar p = 0.50);
  CERT-IMMEDIATE n = 20: +0.150 (3:0, p = 0.25); UNCERTIFIED n = 899: −0.009 (30:38,
  p = 0.40). Certified-minus-uncertified gain +0.051, question-bootstrap 95%
  [+0.001, +0.120] (strict); +0.159 [+0.009, +0.330] (immediate). Both CIs exclude 0 at
  the edge but the McNemar clause fails on 2:0 / 3:0 discordant pairs — the frozen tree
  simply has too few certified leaves (6 certified sites) for the ladder's 2,000 matches
  to say more. Reported as UNDERPOWERED, not as a null: the hypothesis that the ladder's
  leaf ~ anchor result was driven by uncertified leaves is alive and is exactly what the
  certified-leaf ladder (test 5, on a D2 tree with 17-18 certified sites) is for.

- **F2 — PRIMARY FAILS; secondaries WIN; prediction reversed.** Corrected run (see data
  note): 7,754 keyed questions (6,734 train-side, 1,020 reserved after the 46-model
  coverage intersection), anchor != category on 25.8%. Mean LOO Brier improvement over
  the marginal (x1000): category +10.53, anchor +10.67, stratum +11.59, leaf +13.68.
  anchor − category +0.14 [−0.53, +0.83] TIE on all questions and +0.44 [−2.14, +2.89]
  TIE on the disagreement subset → the registered "anchors beat categories" claim FAILS:
  at the same coarse granularity the embedding axis carries no more information about
  model correctness than the hand labels. But stratum − category +1.06 [+0.30, +1.81] and
  leaf − category +3.15 [+2.07, +4.20] WIN on all questions (ties on the 1,998-question
  disagreement subset, underpowered). I predicted leaves would NOT beat categories;
  they do, by ~30% of the labels' own improvement. Reading: sub-anchor cells DO resolve
  capability structure the 14 labels miss — the profile claim survives at stratum/leaf
  granularity, not at anchor granularity — even though the ladder found no rubric value
  below anchors. Capability structure and rubric-relevant structure are different things.

- **F3 — confidence INFORMATIVE; prediction wrong.** n = 12,782 key-decidable decisive
  verdicts: accuracy 0.881, mean confidence 0.909; ECE 0.039 (well calibrated, monotone
  reliability table: bin 0.80–0.85 → 0.727 correct, bin 0.95–1.00 → 0.960); AUC 0.752
  [0.738, 0.764]. Predicted weakly informative/over-confident; it is neither.
  Confidence-weighted board: rho 0.951 → 0.958, top-4 unchanged (3 violations) — the
  confidence field is a usable per-verdict weight but does not touch the frontier cluster.

DATA NOTE (found by F2's first run, which is VOID and superseded): `eval_results.
question_text` is stored PER ROW, and the ingested file of Meta-Llama-3-70B-Instruct
carries wrong question texts on 8.4% of its rows (every other model: 0.1%). A text→id
join over eval_results therefore maps ~half of train questions to a wrong id (the first
F2 run showed 49.5% anchor/category disagreement and an inflated advantage for embedding
cells). Verified consequences: NONE for the campaign — that model is excluded by the
standing rule; matching every eval row to its true MMLU-Pro row by its OPTIONS (5
duplicate option-sets in 11,995 rows) shows the question text wrong for 18/11,580 ids
(4 in the reserved pool), and the R2 judge saw the true question in 2,755/2,884 cases
(3 wrong, 126 unmatched by option formatting). Rule added to memory: cross the
mmlu_pro↔eval id spaces by the options key, never by eval_results.question_text.
