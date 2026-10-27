# POST-RUN review: FITSET-INTENT (adversarial-reviewer, 2026-10-03; zero calls)

Run: main, `tools/analysis/fitset_intent.py` blob:eaa29686f0e783d0d6e8d59797e36a2a3e74f1f4 (LF; `git hash-object` on main = the
READY pin), after brackets f1f916d4. Outcome `experiment_results/intent_transfer/fitset_intent_outcome.txt`: 90 lines, 12,018 B,
sha256-16 064964ea4ef1b862, mtime 2026-10-03 18:24:25. Console: scratchpad `fi_run.log` (95 lines). READY: `READY_fitset_intent.md`.
Data object: intent-s1-run snapshots M-AN 20261002_213331 (82 leaves) and C-AN 20261002_214129 (131 leaves); EVAL MASSIVE
4,946 items / 4,923 components, CLINC 6,672 / 6,672; TRAIN 9,870 / 13,487.

## Verdict: VALID. FI1 UNDETERMINED on both corpora; READING NOT-SHOWN; F-FI FIRES. CLINC's interval lies wholly BELOW 0. The wording W-1..W-5 below binds the registrar

## Per-claim table (mine = own refit, own naming, own filing; S1's reviewed readers and its seed-0-4 k-means fits; read-only)

| # | claim (outcome) | result | mine | sev |
|---|---|---|---|---|
| 1 | MASSIVE P(A) 0.8049, P(A-refit) 0.8097 | CONFIRMED | 0.804893 / 0.809745 | - |
| 2 | MASSIVE D +0.0049 [-0.0006, +0.0103] | CONFIRMED | +0.004852 (net +24 items: 105 gained, 81 lost) [-0.0006, +0.0103] (S1.boot, B 2,000, seed 20261093) | - |
| 3 | MASSIVE spread_K 0.037606 | CONFIRMED | seeds 0-4 0.7525 / 0.7901 / 0.7622 / 0.7596 / 0.7776; spread 186 / 4,946 = 0.037606 (it equals the discordance, also 186 items, by coincidence: two separate computations) | - |
| 4 | CLINC P(A) 0.7851, P(A-refit) 0.7587 | CONFIRMED | 0.785072 / 0.758693 | - |
| 5 | CLINC D -0.0264 [-0.0333, -0.0192] | CONFIRMED | -0.026379 (net -176 items: 222 gained, 398 lost) [-0.0333, -0.0192] (seed 20261094) | - |
| 6 | CLINC spread_K 0.052908 | CONFIRMED | 0.6829 / 0.7358 / 0.7182 / 0.6866 / 0.7202; 353 / 6,672 = 0.052908 | - |
| 7 | FI1 words, READING, F-FI | CONFIRMED | MASSIVE: lo < 0, so UNDETERMINED. CLINC: hi < 0, but D > -spread_K (-0.0264 > -0.0529), so not REVERSED and UNDETERMINED. Both are UNDETERMINED, so NOT-SHOWN and F-FI FIRES | - |
| 8 | Support beside FI1 | CONFIRMED | SE 0.00274 / 0.00365; bootstrap DEFF 0.991 / 0.963; Kish 1.0093 / 1.0000 from the cluster sizes (re-measured; transported 1.052 conservative); n_eff 4,992 / 6,930; MDE80 0.0077 / 0.0102; discordance 0.0376 / 0.0929 | - |
| 9 | Identity | CONFIRMED | Snapshot IDs and leaf counts; descent ACCEPTED 1676/1676, 2332/2332; D_fd +0.02467 / +0.08019, D1 +0.00714 / +0.00706, delta_c 0.01966 / 0.01414 = S1's printed values (B-1 aggregate form); P(A) = S1.t_c8 P_flat 0.80489 / 0.78507; my P(A) from my own filer agrees | - |
| 10 | Bookkeeping | CONFIRMED | 0 / 2 leaves with no item (n00000154, n00000353; READY #3); naming changes 3 / 11; 28 refit fits audited TRAIN-only | - |
| 11 | Predictions | CONFIRMED | P1 MASSIVE +0.0049 HELD, CLINC -0.0264 FAILED; HELD-any did not occur, Brier 0.0625; P2 MASSIVE 0.0376 HELD, CLINC 0.0929 FAILED (above 0.08) | - |
| 12 | Console = outcome; written once | CONFIRMED | all 90 outcome lines are in the console. Only the console has the 4 pin lines and the `wrote` line. 1 `wrote` line. 1 file named fitset_intent_outcome* under the repo (find, depth 4). Mode "x" (READY #10). Pins re-checked after the run: OK | - |

## Is the bar attainable? (Check 8)

- It is not impossible. D is bounded by 1 - P(A): 0.195 on MASSIVE, 0.215 on CLINC. Both bounds are above spread_K (0.0376 / 0.0529).
- It is unattainable for effects of the predicted size at ANY n. spread_K is k-means' seed spread, which does not shrink with n
  (registered (g)). The realised bars are 2.5x and 5.3x the planning bars (0.015 / 0.010).
- What a HELD needed: D > 0.0376, i.e. more than 186 net items on MASSIVE (observed +24). What a REVERSED on CLINC needed:
  D < -0.0529, i.e. more than 353 net items lost (observed -176).
- The bar is the dominant term: MDE80 is 0.0077 / 0.0102. The registered verdict line (DESCRIPTIVE-ONLY at the prediction) is
  therefore realised, and more strongly than planned.
- An UNDETERMINED here means "below another arm's seed variability". It does not mean "no effect".

## Where it sits (descriptive)

- CLINC losses are concentrated in two anchors: Work -0.1159 (n 690) and Auto And Commute -0.0939 (n 724). Meta is -0.0380.
  Utility +0.0101 and 4 more anchors are slightly positive.
- MASSIVE is mixed: Music +0.0752, General +0.0312; Qa -0.0310, Play -0.0205.
- The CLINC trees have 11 naming changes, and some refit cells are fitted on 1-9 items (Meta, Travel, Utility, Banking). This
  is consistent with confound (1), size vs purity. It is not tested.

## Wording for the registrar (binding)

- **W-1 (scope, every sentence).** "Re-estimating the leaf MEANS of S1's anchored trees M-AN (82 leaves) and C-AN (131 leaves)
  on the TRAIN items of each anchor's declared coarse class; leaves and topology fixed; one draw; qwen3 512". It is anchored
  trees only, with ADDED TRAIN-label use. Never "label-free"; never "a construction with declared fit sets".
- **W-2 (MASSIVE).** "FI1 MASSIVE UNDETERMINED: D +0.0049, 95% [-0.0006, +0.0103] (net +24 / 4,946 items), below the in-run bar
  spread_K 0.0376 (k-means k = 82, seeds 0-4)."
- **W-3 (CLINC: must not read only "not shown").** "FI1 CLINC UNDETERMINED under the registered bar, but the refit HURTS: D -0.0264,
  95% [-0.0333, -0.0192] (net -176 / 6,672 items), interval wholly below 0. It is not REVERSED only because |D| is below the
  k-means seed spread 0.0529." Write beside it: losses concentrated in Work and Auto And Commute (descriptive). Never "no
  effect", never "parity".
- **W-4 (reading, F-FI).** "NOT-SHOWN; F-FI fires. On known-answer intent corpora the class-pure leaf-mean refit does not
  reproduce FITSET-FAITHFUL's stage-0 gain: flat within noise on MASSIVE, and worse than as built on CLINC. FITSET-FAITHFUL's
  sentence keeps 'mostly MMLU-Pro' as a scope limit, and adds: 'on CLINC (C-AN) the same refit lowers fine filing (interval
  below 0)'." Carry the four confounds of f1f916d4 (B-2) verbatim.
- **W-5 (bar).** Quote both UNDETERMINED words with the bar: "the in-run bar (k-means seed spread 0.038 / 0.053) does not shrink
  with n and was 2.5x / 5.3x the planning bar; FI1 was DESCRIPTIVE-ONLY at the prediction". P1 and P2 FAILED on CLINC
  (D -0.0264 outside [-0.005, +0.020]; discordance 0.0929 > 0.08).

## Defects

- None against the run.
- D-1 (LOW, carried from READY D-1..D-3; test gaps only): no action needed for the record.

## Commands

```
git hash-object tools/analysis/fitset_intent.py      # eaa29686 on main
sha256sum / ls --full-iso / wc -l <outcome> <console>; find <repo> -maxdepth 4 -name 'fitset_intent_outcome*' | wc -l   # 1
python - <console> <outcome>    # 0 outcome lines missing from the console; extras = 4 pin lines + 1 wrote line
tasklist java.exe (none); python scratchpad/fir/post.py   # own refit/naming/filing; P_A, P_R, D, net items, CI (S1.boot, same seeds),
                                                          # SE, DEFF, discordance, k-means seeds 0-4 precision and spread_K
```
