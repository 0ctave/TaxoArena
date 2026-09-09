# M-series — measurement / router tests on existing verdicts (registered 2026-09-09, before running)

Zero judge calls. Inputs: the R2 profile run's match_history (36,871 verdicts in id = time
order; experiment_results/x12_profile/ratings_x12p.db), its live export (27,657 rows with
per-verdict confidence), x12's match_history (9,144), the R3/J1 caches, the key
(eval_results.is_correct), and the frozen tree (leaf -> anchor).

## M1 — online replay: does the cell profile predict who wins next?
The router's core claim, measured on real verdicts in arrival order. Replay R2's matches;
every 500 matches refit from all verdicts so far: GLOBAL BT theta; CELL BT theta per leaf
(fallback to global when a model has < 5 matches in the leaf); ANCHOR BT theta per anchor
(same fallback); HIERARCHICAL theta = global + n/(n+kappa) * (cell − global) with kappa = 30
(shrinkage toward the global board by the model's match count in the cell). Predict each
match in the next block with P(A wins) = sigmoid(theta_A − theta_B).
Evaluation on the SECOND HALF of the stream (first half = warm-up), decisive verdicts only:
log-loss and Brier of the win prediction; and the ROUTER-UTILITY metric on key-decidable
matches — does argmax-theta pick the model the key says is right? Reported with the
cell-oracle ceiling (argmax of per-leaf key accuracy, which no key-free router can see).
REGISTERED PRIMARY: HIERARCHICAL beats GLOBAL on second-half log-loss — paired 2,000-fold
match bootstrap of the difference with the CI excluding 0. SECONDARY (a) ANCHOR vs GLOBAL,
(b) CELL-only vs GLOBAL (expected WORSE: thin cells), (c) router-utility: hierarchical
correct-pick rate > global's (McNemar p < 0.05). DESCRIPTIVE: confidence-gated updates
(train only on verdicts with confidence >= 0.85), and the gain by anchor.
Predictions: hierarchical > anchor > global > cell-only on log-loss; the router-utility
gain over global is small (< 2 points) because one model dominates most cells; the gain
concentrates in the anchors with the strongest measured interaction (Math, Law, Psychology).

## M2 — match-budget curve: how few matches still give the board?
For x12 (9,144 verdicts, Mistral) and R2-live (27,657, Mistral) and the R3 sample under
the reasoning judge (1,980): draw random subsets of size {250, 500, 1,000, 2,000, 4,000,
all} 200 times each, fit BT, report Spearman rho vs key accuracy (12 models) and top-4
pairwise violations vs GT — median and 5th percentile over draws; with and without
confidence weighting (live R2 only). REGISTERED CLAIM: at 2,000 matches, rho >= 0.93 in
>= 95% of draws for the Mistral runs (the "2k matches for a 12-model board" number
stated in the match-budget analysis). Descriptive: the budget at which the top-4 order
first matches the reasoning judge's full-sample order.

## OUTCOMES
(filled after the run)
