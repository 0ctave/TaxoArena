# POST-RUN review: JUDGE-SOLVED-SPLIT (zero calls)

**Object reviewed**
- Outcome: `experiment_results/archv2/judge_solved_split/outcome.txt`, sha256 9d41dbac64790cc4579873387c78db87d0e8b547c7c9e94a977b532bcdf4643d (106 lines).
- Marker: `judge_solved_split.READ_STARTED`, sha256 615ceade….
- Run provenance: from main at merge e051e017, script blob:c1f36f794d9d83ece13f5ecf2d553bdb6dbf0869 (LF; `git hash-object` in main), `k46_key_read.py` blob:c6a6729b….
- READY review: `docs/reviews/READY_judge_solved_split.md`, conditions C1-C4.
- Registration: prog L23437-L23462.
- Reviewer: no judge calls, every DB opened read-only.

## VERDICT: VALID. JS1 UNDETERMINED; F-JS NOT FIRED; DESCRIPTIVE-ONLY by both the registered and the measured support

## Per-claim table

| claim (outcome) | reviewer (own script, read-only, independent of the script's row logic) | result |
|---|---|---|
| JS1 Delta_S +0.0196 on 414 (226 / 188), 122 components, Kish 4.850 | +0.0196; acc 0.9292 / 226 and 0.9096 / 188; 122 components (1 shared by both arms) | CONFIRMED |
| 95% percentile [-0.0472, +0.0802] (B 2,000, default_rng(42), components jointly) **decides** | [-0.0472, +0.0802], digit-exact. Seeds 1 / 7 / 2026 give [-0.0414, +0.0810], [-0.0416, +0.0800], [-0.0455, +0.0818]: the interval contains 0 under every seed | CONFIRMED |
| normal [-0.0435, +0.0827], SE 0.0322 (descriptive) | [-0.0435, +0.0827], SE 0.0322; FORMS AGREE | CONFIRMED |
| JS1 -> UNDETERMINED; READING "not shown either way at n = 414"; F-JS NOT FIRED | follows from the interval and the registered rule | CONFIRMED |
| measured DEFF 1.334 (analytic), n_eff 169.4 / 140.9, MDE80 0.0901 | 1.334; 169.4 / 140.9; 0.0901 | CONFIRMED |
| convention B (beside) -0.0251 on 218 / 173 | 0.9633 / 218 vs 0.9884 / 173, -0.0251 | CONFIRMED |
| TIE share 0.0354 (solved) / 0.0798 (unsolved), reference right | 0.0354 / 0.0798 | CONFIRMED |
| JS2: solved 0.2000 on 5 (2 variants); unsolved 0.2593 on 27 (7 variants) | 0.2000 / 5 / 2; 0.2593 / 27 / 7 | CONFIRMED |
| uncovered 0.9082 on 98, 29 qids (never counted as unsolved) | 0.9082 / 98 / 29 | CONFIRMED |
| P1, P2a, P2b, P3a, P3b HELD; Brier 0.0650 | all five points lie inside their intervals. P3b sits ON its endpoint (0.20 in [0.20, 1.00]; inclusive by reading (b)). Brier 0.15² + 0.05² + 0.20² = 0.0650 | CONFIRMED |

Wrong(established) does not apply: no model edge is computed.

## Run integrity
- **Console vs outcome.** After CR stripping, `jss_run.log` equals `outcome.txt` except for its one extra final line, "OUTCOME written write-once: …", which the script prints after the write.
- **Written once.** The directory holds exactly 2 files (`ls | wc -l` = 2): the marker, mtime 03:53:12.694, and the outcome, 03:53:12.753. The marker precedes the outcome. There is no `_VOID` file.
- **Writing is mode x.** The write uses mode x (READY row 10), so a second write would have refused.
- **Guards in the outcome.** Both identity blocks read PASS (2 lines). `MUTANT None` is printed. Store, eval view and grok.db each print "AFTER … EQUAL".
- **DB hashes now.** I re-hashed the three DBs: 44724d25 / e35b7518 / 0f2d96d4, the pins.

## Conditions from the READY review, applied
- **C3 (support).**
  - Measured: DEFF 1.334, the analytic DEFF of the difference on the 414.
  - Transported plan: DEFF 2.727, a single proportion on the 544 measured as a bootstrap ratio.
  - So the plan was conservative. The measured MDE80 is 0.0901, against the planned 0.121.
  - |Delta_S| 0.0196 < 0.0901, so JS1 is DESCRIPTIVE-ONLY at the observed point, as at the prediction.
  - The interval was reachable only for |Delta_S| > about 1.96 × 0.0322 = 0.063.
  - Both DEFFs must be quoted with their names, never as one number.
- **C4 (qids).** Quote **98 uncovered matches on 29 qids**. The dry-run's "absent 31" counts every ONE qid, including 2 with no key-decidable match.
- **C2 (test gap).** Still open for any future delta. It did not bear on this run: the identity checks passed, the shas were equal and the join had 0 disagreeing rows.

## Observations (descriptive; for the registrar's wording, not criteria)
- **W1. Convention B's sign is the opposite of A's** (-0.0251 vs +0.0196). Unsolved items carry more than twice the TIE share (0.0798 vs 0.0354). Convention A counts a TIE as wrong, so A's small positive point is carried by ties, not by wrong committed picks.
  - Neither convention decides anything beyond the registered A interval.
  - No sentence may say "the judge is more accurate on items it solves".
- **W2. JS2 does not show the pattern the Krumdick reconciliation predicts.** Solved scores 0.20 on 5 matches (1 key-correct, 2 variants); unsolved scores 0.26 on 27 (7 variants). With 9 variants this is descriptive only and supports no direction.

## Wording the registrar must use
"JS1 UNDETERMINED: on 414 covered reference-right key-decidable ONE matches (226 judge-solved / 188 unsolved; 122 CK-CLOSE components; convention A), Delta_S = +0.0196, 95% percentile interval [-0.0472, +0.0802] (B 2,000, seed 42). Not shown either way at n = 414; never 'judge ability makes no difference' and never parity. Measured support: analytic DEFF 1.334, SE 0.0322, MDE80 0.090, DESCRIPTIVE-ONLY. F-JS NOT FIRED. JS2 (descriptive, 9 variants): 0.20 on 5 solved vs 0.26 on 27 unsolved. 98 uncovered matches on 29 qids, outside JS1 / JS2. Convention B beside: -0.0251 (W1)."
Predictions: 5 / 5 HELD (P3b on its endpoint); Brier 0.0650. Use the split word "content-closed under CK-CLOSE-v2 (residual disclosed)". The P-FAM bracket goes on the JUDGE-2x2 comparators.

## Commands
```
git hash-object tools/analysis/judge_solved_split.py tools/analysis/k46_key_read.py      # c1f36f79, c6a6729b (main)
diff <(tr -d '\r' < scratch/jss_run.log) experiment_results/archv2/judge_solved_split/outcome.txt   # only the final "OUTCOME written" line
ls experiment_results/archv2/judge_solved_split | wc -l   # 2 ; ls --full-time (marker before outcome)
sha256sum <store> <eval_view> <grok.db>                     # pins unchanged
scratch/indep.py -> rows.pkl ; scratch/post.py rows.pkl     # independent JS1/JS2/JS3/DEFF/seeds recompute
grep 'IDENTITY: PASS\|IDENTITY GATE: PASS\|AFTER .*EQUAL\|MUTANT None' outcome.txt
```
