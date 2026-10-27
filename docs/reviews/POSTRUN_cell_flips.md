# POSTRUN — CELL-FLIPS: the readout of cell_flips.py --run

Reviewer: adversarial-reviewer, 2026-10-04. Zero calls. Object: `experiment_results/archv2/cell_flips/cell_flips_outcome.txt` (363 lines,
sha256 0338331407639ecf1431bdf9415722f0b27d0d0bef703b87122ec63490b14c06) + `cell_flips.READ_STARTED` (sha256 c2c1b08c…e046), written
03:00:06-03:00:09 by cell_flips.py blob:998d39a7 (LF; main working tree is CRLF, sha256-crlf16 e102c995724718f9), union_cells_io.py
blob:92a04543, from main after the merge (02:57:39) and the pre-data brackets 098c3f84 (02:59:33). Console: scratchpad `cf_run.log`.
Registration prog L24143-L24154 with the B-1 / B-2 brackets; READY: `READY_cell_flips_coverage.md`.

## Verdict: VALID

Chips: **CF1 FLIPS-EXIST (7 of 101 TESTED AF-U cells, BH q 0.05)**; **F-CF NOT FIRED**. P1 TESTED FAILED (structural, B-2), P1 FLIP
FAILED (7 outside [0, 6]), P2 HELD (4), P3 HELD (3), P4 HELD (0.5861). Brier CF1 0.1225. Two qualifiers travel with the words:
- **(Q1) Concentration.** 5 of the 7 AF-U flips are BBH cells won by internlm2_5-20b-chat, and each is a near-pure BBH TASK: the two
  movie_recommendation cells (39/39, 36/36 items), hyperbaton (40/41), date_understanding (33/36), logical_deduction 3/5/7 objects (41/41).
  The declared arm finds the same phenomenon: 3 of its 4 flips are BBH tasks won by internlm (hyperbaton, movie_recommendation,
  logical_deduction_three_objects); 125 of the 273 AF-U flip items sit in a declared flip cell. 7 cells = 6 distinct phenomena
  (movie_recommendation is split in two).
- **(Q2) Not source-level.** It is not "BBH has a different winner": at the SOURCE level (6 cells, TRAIN pick per source from the frozen
  policy's `true_source`, same bootstrap rule, my descriptive check) BBH pooled internlm − g = +0.0286 over 1,716 items, p 0.0086 >
  0.05/6 = 0.0083: 0 source flips. In the 18 AF-U BBH cells whose TRAIN pick is NOT internlm, internlm − g = −0.054 (929 items). The
  winner changes by BBH task, which declared task cells already show.
- What the tree adds beyond declared labels (descriptive, 3 cells): a date_understanding sub-cell (AF-U D +0.222, n 36; the declared
  date_understanding cell D +0.078, p 0.113), an MMLU-Pro psychology sub-cell (Llama-3.3-70B, D +0.132, n 53; declared psychology picks
  Llama-3.1-70B, D +0.013, p 0.33) and a physics sub-cell (Qwen2.5-32B, D +0.296, n 27; declared physics D 0.000, p 0.525).

## Per-claim table (my number against the outcome's)

| # | claim | outcome | mine (independent loop: own D_c, bootstrap on the B-1 streams, BH, tau) | verdict | sev |
|---|---|---|---|---|---|
| N | set, g | 5,907 / 5,404; g Qwen2.5-72B-Instruct | 5,907; g = also the EVAL-best (0.6049) | CONFIRMED | — |
| CF1 | AF-U TESTED / FLIP | 101 / 7; 273 items (0.0462) | 101 / 7; 273 | CONFIRMED | — |
| flips | 7 AF-U D_c, p | e.g. n00000067 +0.2222 p 0.00010 … n00000223 +0.2963 p 0.00290 | all 7 identical to 4 dp / 5 dp | CONFIRMED | — |
| BH | 7th threshold | — | 7 × 0.05/101 = 0.00347 ≥ p_(7) 0.00290; p_(8) fails | CONFIRMED | — |
| K_0 | TESTED / FLIP | 94 / 3 (all BBH, internlm), 167 items | 94 / 3, 167 | CONFIRMED | — |
| decl | TESTED / FLIP | 44 / 4, 303 items | 44 / 4, 303 | CONFIRMED | — |
| tau | medians | AF-U 0.5861 (42), K_0 0.6198 (45), declared 0.6203 (44) | same | CONFIRMED | — |
| W | written once | mode "x"; one READ_STARTED marker | 363 outcome lines all in the console (one differs only by the em-dash's console encoding); console-only: the OUTCOME line; 0 Traceback / REFUSED | CONFIRMED | — |
| pre | brackets before run | — | 098c3f84 02:59:33 < marker 03:00:06 | CONFIRMED | — |

## Support re-measured (beside the deciding statistic)

Per-TESTED-cell DEFF median 0.974 (AF-U) / 0.981 / 0.991 against the planning 1.10 (one-stage; the two-stage 1.595 does not apply: frozen
policy). AF-U median n 45, n_eff 46.2, median SE(D_c) 0.0627 (registered 0.083 at n 48, conservative). MDE at the first BH rejection:
3.29 × 0.0627 = 0.207 (registered 0.27). The flips have D_c 0.13-0.30; the smallest surviving (+0.132, n 53, p 0.0003) is below the
first-rejection MDE and survives on BH's step-up. Kish: 1.3115 is Σn²/Σn; the registered 1.09 is 5,907/5,404 (B-1).

## Disclosures that bind the wording

- **B-2 / D-4 (K_0 not like with like).** K_0 files EVAL items by TRUE source (mirrored, as registered) while AF-U's flatLeaf searches
  all leaves; K_0's 3 flips and 94 TESTED are no comparator of AF-U's 7 / 101: never "the tree finds more flips than k-means". All 3 K_0
  flips are BBH/internlm too.
- **No arm ranking.** AF-U 7, declared 4, K_0 3 are counts over different m (101 / 44 / 94), cell sizes (median n 45 / 75 / 44) and BH
  bars; more AF-U flips are partly smaller, more numerous cells splitting one task (movie_recommendation twice).
- **P1 TESTED FAILED is structural** (knowable at registration; B-2). P1 FLIP 7 > 6 FAILED.
- Keyed correctness only; one draw; the union roster.

## Registrar's wording (proposed)

"CELL-FLIPS, content-closed v2 union split, 0 calls: with the TRAIN-chosen best single model (Qwen2.5-72B-Instruct) and frozen TRAIN
cell picks, **7 of 101 TESTED AF-U cells are BH-surviving flips on EVAL (q 0.05; 273 of 5,907 items, 4.6%): CF1 FLIPS-EXIST, F-CF not
fired.** The flips **concentrate**: 5 of 7 are BBH task cells (movie_recommendation twice, hyperbaton, date_understanding, logical
deduction) won by internlm2_5-20b-chat, the same reordering the declared task cells show (3 of the 4 declared flips; descriptive), and
not a source-level one (BBH pooled +2.9pp, not BH-surviving over 6 sources; descriptive). Three AF-U flips have no declared-cell
counterpart (a date_understanding sub-cell, MMLU-Pro psychology and physics sub-cells; descriptive). K_0 (3) and declared (4) are
descriptive, and K_0 files by true source (D-4): no ranking of arms. Median Kendall tau of the 18-model order within AF-U cells (n ≥ 50)
against the global order 0.586 (42 cells). Predictions: P1 TESTED (structural) and P1 FLIP FAILED; P2, P3, P4 HELD; Brier 0.1225."
Not licensed: "the tree discovers order changes the labels miss" (4 of 7 coincide with declared BBH task flips; the 3 others are
descriptive and single-draw); "BBH has a different winner"; any AF-U vs K_0 or declared count comparison; judged orders.

## Defects

None on the deciding path. D-3 (Kish label, LOW) from the READY stands as bracketed.

## Commands

```
sha256sum experiment_results/archv2/cell_flips/*            # 03383314… / c2c1b08c…
git hash-object tools/analysis/cell_flips.py tools/analysis/union_cells_io.py   # 998d39a7 / 92a04543
python scratchpad/rvcf/post_cf.py   # key via U.eval_set (marker in a removed E:/TaxoArena_tmp/postcf_* dir); own D_c / bootstrap (B-1
                                    #   streams) / BH / tau per arm + a 6-cell source arm (seed 20261013); flip-cell declared composition;
                                    #   BBH pooled and non-internlm-pick BBH cells
python: every outcome line in cf_run.log (362 exact + 1 encoding-only); grep -c 'Traceback\|REFUSED' = 0
git log -1 --format=%cI 098c3f84 (02:59:33) < READ_STARTED mtime (03:00:06)
E:/TaxoArena_backup_2026-10-04_cell_flips: outcome + READ_STARTED + SHA256SUMS.txt (sha256sum -c OK)
```
