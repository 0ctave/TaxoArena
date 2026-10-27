# POST-RUN review: OOS-BASELINES (--run, main, blob 7e74108d)

Reviewer: adversarial-reviewer, 2026-10-02. Run from main after merge 9b86d32d and brackets d1abedce; `git hash-object
tools/analysis/oos_baselines.py` = 7e74108dedcb2d921be0da4cf8ddc842deb24d72 (LF). READY: docs/reviews/READY_oos_gold.md. Zero calls.
GOLD-LEVEL-EMB was running during this review: none of its outputs or logs were read.

## Verdict

**VALID.** Every deciding number is reproduced to the printed digit by my own code: my own AUROC, my own sqlite read, my own slicing, my
own Ledoit-Wolf, kNN and Mahalanobis, and my own bootstrap stream. All four statuses, both readings and F-OB come out the same. The
outcome was written once, and it is identical line for line to the console. Conditions on the wording: W-1..W-5 below.

## Per-claim table

| claim (outcome) | mine | status |
|---|---|---|
| S0 A per seed 0.97437 / 0.97263 / 0.97601 / 0.97446 / 0.97649; mean 0.97479; var_seed 2.329e-6 | same from oos_scores.csv (rank AUROC); var 2.3293e-6 | CONFIRMED |
| A(a) 0.97640, Delta +0.00161, OB-a EQUIVALENT (90% [+0.00031, +0.00290]) | (a) rebuilt from intent_emb_qwen3.db: A 0.97640, max abs score diff to the CSV 5.0e-9; own-stream bootstrap SE_total 0.00080, 90% [+0.00030, +0.00291] EQUIVALENT | CONFIRMED |
| A(b) 0.97378, Delta -0.00101, OB-b EQUIVALENT (90% [-0.00260, +0.00057]); LW shrinkage 0.025790 | rebuilt with my own LW: shrinkage 0.025790, A 0.97378, diff 5.0e-9; SE_total 0.00098, 90% [-0.00262, +0.00059] EQUIVALENT | CONFIRMED |
| A(c) 0.96191, Delta -0.01288, OB-c S0-BETTER (95% [-0.01523, -0.01053]) | own kNN k 10: A 0.96191; SE_total 0.00119, S0-BETTER | CONFIRMED |
| A(d) 0.92757, Delta -0.04722, OB-d S0-BETTER (95% [-0.05206, -0.04239]); shrinkage 0.006225 | rebuilt: shrinkage 0.006225, A 0.92757, diff 5.0e-9; SE_total 0.00245, S0-BETTER | CONFIRMED |
| READING CELLS-ADD / COMPETITIVE; F-OB NOT FIRED | follows from the four statuses in the registered order | CONFIRMED |
| DEFF 1.0000 (Kish 1.0000 on both strata), n_eff 6,672 / 1,350 | READY row 1: own SQL gives 6,672 / 6,672 and 1,350 / 1,350 components | CONFIRMED |
| SE_total measured 0.00079 / 0.00096 / 0.00120 / 0.00247 (planned 0.00288 / 0.00288 / 0.00288 / 0.00377 bracketed); MDE: EQ reach 0.00804 / 0.00761 / 0.00702 / 0.00387; DIFF reach 0.01066 / 0.01081 / 0.01101 / 0.01208 | own stream 0.00080 / 0.00098 / 0.00119 / 0.00245 (gaps of 2e-5 or less, all from the stream). Every status lies far from its boundary: the nearest is OB-c, where 0.01288 > 0.010 and its 95% interval is 0.0105 from 0 | CONFIRMED |
| FPR95 s0 0.1578, a 0.1504, b 0.1511, c 0.2659, d 0.3681 (descriptive) | same, with the same GATE thresholds | CONFIRMED |
| descriptive: c_k1 0.97707, c_k5 0.96737, c_k25 0.94900, c_k50 0.93509; b_unshrunk 0.97346; d_unshrunk 0.92800 | same from the CSV; own kNN k 1: 0.97707 | CONFIRMED |
| write-once | outcome.txt (64 lines, sha256 0f9869f7...) and oos_scores.csv (10,356 lines = header + 6,672 + 1,350 + 2,333; no duplicate (id, role); sha256 41c735da...) both created 08:04:23 by mode x. The console's outcome block occurs once and equals the file line for line (64 of 64) | CONFIRMED |
| pins | "pins re-checked before and after, unchanged" (ingest 487e0093, qwen3 9e100e04); fit audit: 27 fits (21 TRAIN, 6 GATE), 0 EVAL, 0 OOS rows | CONFIRMED |

## Predictions re-scored (all agree with the outcome)

- P1 (OB-a EQUIVALENT, p 0.95): event true, Brier 0.0025. Delta_a +0.00161 had already been seen, so this is no confirmation.
- P2 Delta_b -0.00101 in [-0.006, +0.018]: HELD. Status EQUIVALENT. Brier sum 0.9350 (EQUIVALENT 0.6400).
- P3 Delta_c -0.01288, outside [-0.006, +0.008]: FAILED (the prediction was too optimistic for kNN). Status S0-BETTER, which had p 0.03.
  Brier sum 1.3508.
- P4 Delta_d -0.04722 in [-0.080, 0.000]: HELD. Status S0-BETTER. Brier sum 0.2350.
- P4' LIKE-FOR-LIKE reading CELLS-ADD (p 0.02): Brier sum 1.5754. LABEL reading COMPETITIVE (p 0.19): Brier sum 1.0062.
- P5 FPR95: (a) HELD, (b) HELD, (c) 0.2659 FAILED, (d) HELD. These are descriptive.
- P6 SE_total(OB-a) 0.00079 < 0.0015: event true, Brier 0.0900.

## Wording the registrar must use (conditions)

- W-1 (scope, every sentence). "Flat spherical k-means cells (K = 150) on qwen3-embedding 256-d RAW vectors of the CLINC150 intent
  corpus (oos_plus OOS pool, 1,350 rows; S0's CK-CLOSE-v1 hash sides)". Never "the tree", "leaves", "the taxonomy" or "TaxoArena
  cells". No result here credits or debits a tree, MMLU-Pro, capability text or any other embedder. The registered WILL-NOT-SHOW list
  is quoted in full.
- W-2 (CELLS-ADD, not over-read). Use: "on this embedding, label-free k-means no-match (mean A 0.97479 over 5 seeds) beats the two
  registered label-free peers: kNN at the registered k = 10 by 0.0129 AUROC (95% [-0.0152, -0.0105]), and a single marginal
  Mahalanobis ellipsoid by 0.0472 (95% [-0.0521, -0.0424])". Both of the following must stand beside that sentence:
  - (i) kNN at k = 1 (descriptive, never selected) reaches A 0.97707, +0.0023 over the S0 mean. The kNN gap depends on k, so the claim
    is never "cells beat neighbourhood density" in general.
  - (ii) S0 reads K = 150 = the number of gold intents (the asymmetry). At K 100 and K 50 (seed 0, descriptive) S0 reaches 0.96529 and
    0.94509, the second below kNN k = 10 (0.96191). So the lead over kNN is conditional on that one label-derived integer.
  The OB-d result may be worded as "the OOS signal is not carried by the embedder's global in-scope ellipsoid", and only on this
  embedding and corpus.
- W-3 (COMPETITIVE). Use: "equivalent within 0.010 AUROC to a labelled nearest-centroid detector (A 0.97640) and a labelled
  class-Mahalanobis detector (A 0.97378) on the same embedding", with the asymmetry qualifier: (a) and (b) read 150 TRAIN class labels;
  S0 reads none but K. Never "matches" or "as good as supervised". The labelled centroid's point is higher: +0.0016, with a 95%
  interval of [+0.00006, +0.00315] that excludes 0. So the claim is parity within the margin, not "no worse".
- W-4 (F-OB). NOT FIRED. S0 C2 HELD and F2 NOT FIRED stand, and no recorded number is revised. Published CLINC150 numbers are at most
  "indicative", with the registered sentence beside them.
- W-5 (record). Prediction tallies are numeric 2 HELD of 3 (P2, P4; P3 FAILED) and P5 3 of 4. Disclose that the CELLS-ADD outcome had
  a prior of 0.02.

## Defects

None on the deciding path. LOW, carried from the READY review: the discarded c2 nomic / gemma fits appear in the fit audit (27 = 22
identity fits + 4 baseline TRAIN reference sets + 1 GATE threshold set); this is descriptive only.

## Commands

```
git hash-object tools/analysis/oos_baselines.py; sha256sum experiment_results/oos_baselines/*; ls -la --time-style=full-iso experiment_results/oos_baselines/
python - : outcome.txt lines vs the run log (64 of 64 present; the block occurs once and is equal)
python scratchpad/oosgold/post.py : rank AUROC of every CSV column; own-stream paired bootstrap B 2,000 (seed 12345) with var_seed/5;
  own FPR95; (a), (d), kNN k 10 / 1 rebuilt from intent_emb_qwen3.db and the ingest DB (mode=ro&immutable=1), first 256 coords renormalised,
  own Ledoit-Wolf formula
python - (post.py prefix) : (b) rebuilt with the class means and own LW on pooled residuals (shrinkage 0.025790, A 0.97378)
```
