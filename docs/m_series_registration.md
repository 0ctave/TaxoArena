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

## M3 — synthetic arena: how far and how cheap does one-by-one insertion scale? (registered 2026-09-09)
Roster: the 46 models with >= 95% coverage of the 12,118 keyed questions (Meta-Llama-3-70B-
Instruct excluded). Verdict oracle: ORACLE = the key (winner = the correct model when exactly
one is correct, TIE otherwise); NOISY = ORACLE with each decidable verdict flipped with
probability 0.12 (Mistral's measured 12% error on decidable pairs) and each non-decidable
match decided by a coin flip with probability 0.8 (real judges tie 13–20%, not 60%).
Protocol: base board of 8 models (seeded random subset), 100 matches per pair on random
questions; then models inserted ONE AT A TIME in random order with ADAPTIVE PLACEMENT — 4
anchors chosen sequentially by bisection of the current board (each anchor gets b matches),
then a full BT refit; per-model budget b x 4 in {25, 50, 100} (100 / 200 / 400 matches per
newcomer). Recorded at roster sizes 8, 16, 24, 32, 46: the newcomer's rank error vs the
key-accuracy rank (median over the insertions in that band), Spearman rho of the whole
board vs key accuracy, and the matches spent. Five seeds. Also a JOINT baseline: the same
total budget spread round-robin over all pairs.
REGISTERED: (i) under ORACLE the median matches-to-place a newcomer within ±1 rank stays
<= 400 from roster 16 through 46 (placement cost does not grow with the roster); (ii) rho
at roster 46 with 400 matches per model is >= 0.95 under NOISY; (iii) the NOISY multiplier
on matches for the same rank error is <= 3x. Predictions: (i) holds; (ii) holds; (iii) ~2x.

## AUDIT — do other snapshots store a pool that is not their own split? (registered)
For every snapshot in snapshots.db and snapshots_frozen.db: the stored reserved list's pool
id vs the "Reserved pool '...' active" line in the snapshot's own captured log trace (or run
log when present). Report every mismatch. Prediction: only 20260727_042523 (the freeze run,
concurrent sweeps) is inconsistent; sweep snapshots built alone are consistent.

## OUTCOMES (2026-09-09; outputs experiment_results/m1_online_replay_output.txt, m2_match_budget_output.txt)

- **M3 — (i) PASS, (ii) PASS, (iii) FAIL; the scaling answer is "placement cost is flat,
  rank resolution is not".** 46 models, 11,436 keyed questions, 5 seeds
  (experiment_results/m3_synthetic_arena_output.txt).
  ORACLE judge, 400 matches per newcomer: median newcomer rank error 0 / 0 / 1 / 1 at roster
  16 / 24 / 32 / 46 — clause (i) holds (≤ 400 matches place a newcomer within a median of
  ±1 rank at every size) — but "within ±1" falls 98% → 88% → 72% → 61%: the cost in MATCHES
  is flat, the difficulty in RANKS grows because adjacent models get closer as the roster
  fills (a fixed θ precision buys fewer rank positions). NOISY judge (12% flips, coin-flip
  non-decidables), 400 per newcomer: board rho 0.947 → 0.955 → 0.969 → 0.975 as the roster
  grows — clause (ii) PASSES (0.975 ≥ 0.95 at 46), and MORE MODELS HELP under a noisy judge
  (more nearby anchors), while under the oracle rho is flat at ~0.99. Clause (iii) FAILS:
  the noisy judge needs > 4x the matches of the oracle for the same rank error at roster
  46 (NOISY@400 median error 2.0 vs ORACLE@100 1.5); prediction "~2x" was optimistic — noise
  compounds with roster density. Joint round-robin at the same total budget (18,400
  matches): rho 0.994 oracle / 0.971 noisy vs sequential insertion 0.989 / 0.975 — one-by-one
  insertion costs nothing at the board level. Deployment reading: ~400 matches per new
  model at any roster size; expect ±1–2 rank uncertainty at 46 models with a Mistral-class
  judge and ±1 with a key-like verifier; the judge, not the roster, is what sets the bill.

- **AUDIT — prediction correct: only the frozen snapshot is inconsistent.** 132 snapshot rows
  (snapshots.db + snapshots_frozen.db), 65 checkable against a run log: 63 OK, 2 MISMATCH —
  both are 20260727_042523_Headless_Run_Auto_ge (present in both DBs). Every sweep and
  promoted build stores its own split; every seed-42 build since 2026-09-08 (adaptive,
  nomic, the wrong-split promoted build) produced p8a29, so p2dca was never a seed-42 split
  of the current dataset. experiment_results/snapshot_pool_audit.txt.

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
