# POST-RUN review: OOS-TREE-CELLS (--run, main, blob 74a5cbf0)

Reviewer: adversarial-reviewer, 2026-10-03. Run from main after merge 665b817d and brackets 93f4c359; `git hash-object
tools/analysis/oos_tree_cells.py` = 74a5cbf00832cd66e2d78bbd31bb59c11dbc14e1 (LF) = the READY blob (READY_oos_tree_cells.md). Zero calls.
Run log: scratchpad otc_run.log (57 lines; operator launched 17:40 with no java.exe). Data root .claude/worktrees/intent-s1-run, read
`mode=ro&immutable=1`.

## Verdict

**VALID.** The deciding numbers reproduce to the printed digit. The AUROCs were recomputed by my own rank AUROC from the scores CSV.
I rebuilt T and C-AN from the raw DBs and the snapshot graphs; my scores differ from the CSV by at most 5.0e-9. The SE gap with my own
bootstrap stream is 2e-5. The outcome was written once and equals the console line for line. **OT1 EQUIVALENT, F-OT NOT FIRED.**
Wording conditions W-1..W-6 below. The decisive one is W-1: **EQUIVALENT within the margin, with the tree measurably below k-means**.

## Per-claim table

| claim (outcome) | mine | status |
|---|---|---|
| identity: A(T) 0.96776, A(K_0) 0.96999, S0 per seed 0.97437 / 0.97263 / 0.97601 / 0.97446 / 0.97649, A(a) 0.97640 | CSV: same to 5 dp. T rebuilt from raw (own read, slice 256, renormalised, leaf vmfMu): max abs diff to the CSV 5.0e-9 | CONFIRMED |
| K_s A 0.96999 / 0.97166 / 0.97412 / 0.97319 / 0.97566; mean 0.97292; var_seed 4.804e-6 | same from the CSV (own AUROC); var 4.804e-6 | CONFIRMED |
| Delta_T -0.00516; SE_boot 0.00072; SE_total 0.00121; 90% [-0.00715, -0.00316]; 95% [-0.00754, -0.00278] | Delta -0.00516. Own stream (B 2,000, items = components since Kish = 1): SE_boot 0.00074, SE_total 0.00123, 90% [-0.00718, -0.00314], 95% [-0.00756, -0.00275] | CONFIRMED (gap 2e-5, from the stream) |
| OT1 EQUIVALENT; F-OT NOT FIRED | the 90% interval lies inside (-0.010, +0.010), with 0.00285 to spare at the lower end. DIFFERENT is impossible because |Delta| < 0.010 | CONFIRMED |
| Support: DEFF 1.0000 measured, n_eff 6,672 / 1,350; EQ reach 0.00698, DIFF reach 0.01102, MDE80 0.00340; registered SE 0.0012 -> 0.00121 measured | own: 0.00695 / 0.01103 / 0.00344 at my SE. The transported SE was accurate. The seed term (0.00098) dominates the bootstrap term (0.00072) | CONFIRMED |
| descriptive: A(T)-A(c) +0.00585, A(T)-A(d) +0.04020, A(T)-A(a) -0.00863, A(T)-A(b) -0.00601, A(T)-S0 mean -0.00703, A(C-AN) 0.96826 (A(C-AN)-A(T) +0.00050) | identical from the CSV; C-AN rebuilt from raw at slice 512: diff 5.0e-9 | CONFIRMED |
| FPR95 T 0.2052 (thr 0.72968), K_0 0.1985, C-AN 0.1881 | own GATE floor(0.05 n) threshold: same | CONFIRMED |
| P1 Delta_T in [-0.008, +0.004] HELD; Briers 0.0400 / 0.0324 / 0.0004; P2 HELD | HELD (closed interval), same Briers; P2 0.96826 in [0.950, 0.975] | CONFIRMED |
| write-once | outcome.txt (43 lines, sha256 dcec3bdf...) and oos_tree_scores.csv (sha256 fe8ebb9e...; 6,672 EVAL_IN + 1,350 EVAL_OOS + 2,333 GATE_IN rows) were both created at 17:40:33 by mode x. The console carries one outcome block and one "wrote" line, and its 43 lines equal the file (`diff` shows only the console's cp1252 rendering of the em dash on line 2) | CONFIRMED |
| hygiene | pins re-checked before and after (487e0093 / 9e100e04); fit audit: 16 fits (15 TRAIN, 1 GATE), 0 EVAL, 0 OOS | CONFIRMED |

Spot check (robustness, not deciding). I re-fitted k = 139 myself (ITS.skmeans, seeds 0-4) on my own TRAIN matrix: 13,491 rows in
DB order, against the script's 13,487 kept rows. Per seed I get 0.97405 / 0.97400 / 0.97209 / 0.97282 / 0.97313, mean 0.97322, so
Delta would be -0.00546. Per-seed k-means AUROCs move by up to 0.004 with 4 rows and the row order. The 5-seed mean moves by 0.0003,
and the status and sign do not change. Seed 0, which is T-C6's seen reading (-0.00222), was the script's lowest K seed.

## Wording the registrar must use (conditions)

- **W-1 (OT1; decisive).** Write: "EQUIVALENT within +/-0.010 AUROC, and below: label-free C-AF tree cells (139 leaves) detect
  out-of-scope queries 0.0052 AUROC below flat spherical k-means at matched k (Delta_T -0.00516, 90% [-0.00715, -0.00316]; the 95%
  interval [-0.00754, -0.00278] excludes 0) (CLINC oos_plus, qwen3 256 RAW, one draw, 5 k-means seeds)".
  - **Never** write "equal", "matches", "as good as", "no worse", "parity" without "within 0.010", or "the tree's cells are
    equivalent" without "and below".
  - Explain that F-OT stays NOT FIRED only because the registered DIFFERENT needs |Delta| > 0.010. The gap is real, but it is below
    the registered relevance margin. So "abstention on flat cells only" is lifted to "the tree's cells abstain within 0.010 of flat
    cells, measurably below them".
- **W-2 (the seen point).** T-C6's single-seed -0.0022 was against K's lowest seed. The 5-seed gap is more than twice as large. P1 is
  HELD only because its band [-0.008, +0.004] is wide; it held at -0.00516, not at the predicted -0.002. Disclose that the seen point
  understated the gap.
- **W-3 (label-free peers, descriptive).** "The tree's cells exceed kNN at the registered k = 10 by +0.0059 (pct 95% [+0.0039,
  +0.0078]) and a marginal Mahalanobis ellipsoid by +0.040". OOS-BASELINES W-2 (i) must stand beside it: kNN at k = 1 reaches 0.97707
  (descriptive), above A(T) 0.96776. Never "tree cells beat neighbourhood density".
- **W-4 (labelled and K-150, descriptive).** The tree trails the labelled centroid (a) by -0.0086 and class Mahalanobis (b) by -0.0060,
  and S0's K-150 by -0.0070. K = 150 is the gold intent count, a label-derived integer (OOS-BASELINES W-2 (ii)). Use the asymmetry
  qualifier; these are not like-for-like contrasts. FPR95: T 0.205 vs K_0 0.199 vs S0 0.158 (descriptive; the tree is worse at the
  operating point too).
- **W-5 (C-AN).** A 0.96826, +0.0005 over T. It differs from T in label information (gold coarse anchors) AND slice (512 vs 256)
  (bracket OT-R5). It is never quoted as an anchoring effect or as label-free.
- **W-6 (scope).** The registered WILL-NOT-SHOW list in full: one CLINC draw, qwen3 256 RAW, oos_plus; no other corpus or embedder;
  no MMLU-Pro; no published-CLINC comparability.

## Defects

None on the deciding path. These are carried from READY: D-1 (after_check and the OOS guard are untested), D-4 (the CSV is written
after the outcome; both exist here) and D-5 (no rc line in the script; the operator's log has it).

## Commands

```
git hash-object tools/analysis/oos_tree_cells.py ; sha256sum experiment_results/oos_tree_cells/* ; ls -la --time-style=full-iso experiment_results/oos_tree_cells/
diff <(grep -v '^\[' otc_run.log) experiment_results/oos_tree_cells/outcome.txt   # only line 2 (em dash encoding)
grep -c "^OOS-TREE-CELLS outcome" otc_run.log ; grep -c "wrote " otc_run.log   # 1 ; 1
python scratchpad/otc/post.py    # own rank/weighted AUROC on every CSV column; own-stream bootstrap (seed 777, B 2,000) with var_seed/5;
                                 # own FPR95; T and C-AN rebuilt from intent_emb_qwen3.db + snapshots.db by Snapshot ID (diff 5.0e-9)
python scratchpad/otc/post_k.py  # k = 139 refit, seeds 0-4, own TRAIN matrix (spot check)
```
