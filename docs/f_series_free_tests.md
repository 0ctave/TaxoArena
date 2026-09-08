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

## OUTCOMES
(filled after the run)
