# POSTRUN WIN-MAP (declared pre-run deviation D-2026-10-09-2: one official refit), 2026-10-09

Verdict: **VALID**. Words: WF1 REALISATION-GAP (HELD), WF2 LUCK-MATERIAL (HELD), F-WM NOT FIRED, RS1 UNSTABLE-MAP (RS1 FAILS, rule 8;
no region captioned). Every deciding point reproduces to the digit. My independent two-stage intervals land on the same side of
every bar.

Object: `experiment_results/archv2/win_map/win_map_outcome.txt` sha256 79392b32... (123 lines); official policy 3d114b24...; backup
E:/TaxoArena_backup_20261009_win_map (`sha256sum -c` 8/8 OK). Script blob:80f5cb1f on HEAD equals the merge 6353b5f6 and the pin-check
READY. Zero calls.

## Per-claim table (deciding claims)

| # | claim (outcome) | mine (independent) | verdict | sev |
|---|---|---|---|---|
| 1 | Data object: EVAL 5907 / 5404 comps, TRAIN 11841, 18 models; c_i = 0 on 552 EVAL items | Export parquet, rows with full correctness: EVAL 5907, TRAIN 11841. Side export: EVAL components 5404, TRAIN 10781. Own c_i from options_json (multicorpus_cache_v1.db mode=ro&immutable=1): 552 zero. Correctness equals AP's separately captured key on every cell | CONFIRMED | - |
| 2 | Official refit: best single Qwen2.5-72B; 123 cell picks (policy 3d114b24) | own TRAIN argmax refit (sorted-roster tie-break): best single Qwen2.5-72B-Instruct; 0 of 123 cell picks differ from the JSON | CONFIRMED | - |
| 3 | O_q 0.9059, O_adj 0.8598, R_AF 0.595395, B 0.567462 | 0.9059 / 0.8598 / 0.595395 / 0.567462 (own know-rates per declared cell on TRAIN, own q_mi, own adj product) | CONFIRMED | - |
| 4 | **WF1 rho 0.0956 [0.0459, 0.1356]; upper < 0.25 -> REALISATION-GAP** | point 0.0956. Own two-stage (stratified component draws on TRAIN with a refit per replicate, then EVAL; default_rng(424242), B 2000): [0.0456, 0.1319], SD 0.0222 (printed SD 0.0225). The upper bound sits 0.11 below the bar | CONFIRMED | - |
| 5 | **WF2 lambda 0.1362 [0.1216, 0.1536]; lower > 0.10 -> LUCK-MATERIAL** | point 0.1362. Own interval [0.1225, 0.1515], SD 0.0072 (printed 0.0081). The lower bound sits about 2.7 SD above 0.10 | CONFIRMED | - |
| 6 | F-WM NOT FIRED (rho point < 0.25) | 0.0956 < 0.25 | CONFIRMED | - |
| 7 | **RS1 median ARI 0.6161 < 0.80 -> UNSTABLE-MAP; seed SD 0.0534** | Own UMAP (umap-learn 0.5.12, cosine, n_neighbors 30, min_dist 0.1, seeds 0-4) + KMeans k 20 (n_init 10, seeds 0-4) on the script's own map rows (20108 x 512). The rows are the data object: the published 2-D coordinates match the parquet exactly (max\|diff\| 0.0), and ARI of partition (0,0) against the parquet region is 1.0. 250 pairs: median 0.6161, SD 0.0534 | CONFIRMED | - |
| 8 | RS2: 4 of 20 STABLE, licensed captions 0 under UNSTABLE-MAP | follows from RS1 by rule (caption needs STABLE-MAP). Table not re-derived | spot check | - |
| 9 | Support measured: SE(rho) 0.0225, MDE80 0.0629; SE(lambda) 0.0081 | own SDs 0.0222 / 0.0072. The registrar's re-derived Support (L25412-L25418) holds: WF1 MDE80 0.102 (worst 0.138) is beside a realised margin of 0.15 at the point. RS1 realised SD 0.0534 against the declared 0.05 | CONFIRMED | - |

Wrong(established) and tie conventions: NOT APPLICABLE (keyed correctness). Own mutants: none (post-run numbers review, no code delta).

## Conditions and defects

- **C-1 (MEDIUM, reading condition).** WF1 and WF2 rest on O_adj, which is model-based (independent know/guess across models, k per
  declared cell from TRAIN). Every sentence must carry "luck-adjusted under the independence assumption" (registered disclosure).
  - Descriptive companions that must stay beside REALISATION-GAP:
    - rho_raw 0.0825
    - on MMLU-Pro, R_AF 0.5424 < B 0.5592: the router loses to the best single model on the largest source
    - under H, rho -0.0082 (sensitivity; decides nothing)
- **C-2 (MEDIUM, reading condition).** RS1 FAILS. The map ships uncaptioned, and the post must say that the regions are not seed-stable.
  - The ARI across k-means seeds alone, at a fixed UMAP seed, is 0.7667 (descriptive). Much of the instability is therefore k-means at k 20, not only UMAP.
- **L-1 (LOW).** The outcome's SUPPORT block labels (b)-(g) "PRE-DEVIATION". The registrar's insertion L25412 binds, and its point values are unchanged. The record should cite L25412, not the printed block.
- **L-2 (LOW).** P4 lambda band [0.20, 0.50] FAILED: lambda 0.136. P2 O_cell FAILED: 0.636. As printed.

## Commands (scripts: E:/TaxoArena_backup_20261009_postrun_review, SHA256SUMS.txt)

```
sha256sum -c SHA256SUMS.txt      # WIN-MAP backup: 8/8 OK; outcome 79392b32, policy 3d114b24
python E:/TaxoArena_tmp/wm_review/wm.py   # (38f7afcf) parquet + side export + af_cells + options_json(ro,immutable) ->
  # EVAL 5907 TRAIN 11841; c=0 552; refit == JSON (0/123); POINT O_q 0.9059 O_adj 0.8598 R_AF 0.595395 B 0.567462
  # rho 0.0956 lambda 0.1362; two-stage rho [0.0456, 0.1319] SD 0.0222; lambda [0.1225, 0.1515] SD 0.0072
python E:/TaxoArena_tmp/wm_review/rs1.py  # (3b80dd70) published coords max|diff| 0.0; ARI(0,0) vs parquet 1.0;
  # RS1 pairs 250 median ARI 0.6161 SD 0.0534
```
