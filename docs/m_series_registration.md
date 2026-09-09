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

## OUTCOMES (2026-09-09; outputs experiment_results/m1_online_replay_output.txt, m2_match_budget_output.txt)

- **M2 — REGISTERED CLAIM PASSES, and the curve says something sharper: budget buys
  stability, the judge buys accuracy.** At 2,000 matches rho >= 0.93 in 100% of draws for
  every Mistral run (x12, R2-all, R2-live); at 1,000 matches 97–100%; at 500, 88–98%.
  The Mistral board plateaus at rho = 0.951 from ~1,000 matches onward — 36,871 verdicts
  do not raise it, and the top-4 stays at 3 violations with gemini first in 0% of draws.
  Confidence weighting lifts the plateau to 0.958. The reasoning judge on the R3 sample
  reaches 0.965 at 500 matches and 0.974 at 1,980, with gemini first in 86% of draws at
  500 and 100% at the full sample — i.e. 500 reasoning-judge matches beat 36,871 Mistral
  matches. Deployment reading: ~1,000–2,000 matches for a 12-model board; beyond that,
  spend on the judge, not on matches.

- **M1 — PRIMARY FAILS (kappa = 30: hierarchical WORSE than global, −0.008 log-loss,
  CI excludes 0); secondary (a) ANCHOR beats global (+0.006, CI excludes 0); (b)
  CELL-only much worse (−0.025) as predicted; (c) router utility: hierarchical correct-pick
  0.851 vs global 0.844 (130:73, p = 0.0001) PASS but small.** 14,659 decisive second-half
  verdicts, 8,217 key-decidable. Win-prediction accuracy 0.83–0.84 for every predictor
  (most matches are lopsided). The by-anchor breakdown shows why the leaf-level prior
  hurts: it helps in History/Engineering/Law and hurts in Physics/CS/Biology — thin
  cells (Physics has 93 evaluated verdicts) inject noise that kappa = 30 does not shrink
  away. POST-HOC (labelled): kappa = 200 makes hierarchical a TIE with global (+0.0006
  [−0.0004, +0.0016]) — stronger shrinkage removes the harm but yields no gain; the
  anchor level is where the online signal lives, which is what the ladder (anchor knee)
  and the strata design already said. My ordering prediction (hier > anchor > global >
  cell) was wrong; the actual is anchor > global ≈ hier(200) > hier(30) > cell.
  THE NUMBER THAT MATTERS FOR THE ROUTER VISION: the cell-ORACLE ceiling — argmax of
  per-leaf KEY accuracy, which no key-free router can see — picks the correct model on
  87.0% of key-decidable matches vs 84.4% for the global best-model rule. On this
  12-model roster a PERFECT cell-level router gains 2.6 points over "always pick the
  best"; the achievable key-free version gains 0.7. Routing value on a homogeneous LLM
  roster is small; it has to come from heterogeneous rosters (tools, specialists, cost
  tiers) — as argued in the design note, now with a measured ceiling.
