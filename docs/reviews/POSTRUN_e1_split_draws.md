# POSTRUN review: E1-SPLIT-DRAWS (ops d0c58b11; readout blob 3318a16a, merged 13a03abc)

Reviewer: adversarial reviewer, 2026-10-03. Zero calls. Registration L23831-L23859, with the L1-L3 brackets in the registrar's
record L23861-L23868 (the L3 bracket sits in L23857). READY: docs/reviews/READY_e1_split_draws.md (C1 met: CP-0 and CP-1 ran
through tools/ops/wal_checkpoint.py, each after `gradlew --stop`, with content=UNCHANGED; D3 met: reserved_test_queries.json
restored to sha256 8bf21fe9...).

## VERDICT

**VALID.** SD1 = **NEITHER**. F-SD **FIRES**, on its spread clause only; its sign clause did not fire. P1 FAILED, P2 FAILED, P3
occurred, P4 = NEITHER, P5 = FIRED. My independent recomputation reproduces every deciding number to the 4th decimal, including b
and c. N_e1sd1's 28 leaves are a construction outcome under the recipe's gates. I found no sign of a fault (section N1).

## Per-claim table (my number vs the outcome's)

| claim | outcome | mine (independent script: own salted side, own nearest-leaf + TRAIN majority, raw blobs read mode=ro&immutable=1) | state |
|---|---|---|---|
| split 1 | n 3,598; N 0.5545 / Q 0.7268; b 252, c 872; G -0.1723 [-0.1897, -0.1549] | identical; SE 0.00886 | CONFIRMED |
| split 2 | n 3,522; N 0.6860 / Q 0.7354; b 360, c 534; G -0.0494 [-0.0660, -0.0328] | identical; SE 0.00845 | CONFIRMED |
| split 3 | n 3,500; N 0.6503 / Q 0.7297; b 286, c 564; G -0.0794 [-0.0955, -0.0633] | identical; SE 0.00822 | CONFIRMED |
| Gbar, spreads | Gbar -0.1004; spread_N 0.1315 (0.6860 - 0.5545); spread_Q 0.0086 (0.7354 - 0.7268) | identical | CONFIRMED |
| SD1 | clause 1 YES (3 of 3 below 0); clause 2 NO (-0.1004 >= -0.1315) -> NEITHER | identical | CONFIRMED |
| F-SD | sign clause NO (no G_k >= 0); spread clause YES (0.1004 <= 0.1315) -> FIRES | identical | CONFIRMED |
| Identity (E1 pair) | 0.7269 / 0.6813, b 327 / c 484, n 3,445; G_E1 -0.0456 [-0.0617, -0.0294] | HELD; same as my READY arithmetic | CONFIRMED |
| Leaves | N 28 / 80 / 71; Q 80 / 87 / 72 | read from the last dag_snapshots line: identical; final iterations N 17 / 16 / 13, Q 23 / 15 / 13 | CONFIRMED |
| Support | DEFF (Kish m-bar) 1.0295 / 1.0250 / 1.0331; n_eff 3,495 / 3,436 / 3,388; discordance 0.312 / 0.254 / 0.243; MDE80 0.0248 / 0.0237 / 0.0230 | 2.80 x SE reproduces; m-bar as in my READY check | CONFIRMED |
| Brier | P3 0.0900; P4 0.6278; P5 0.3600 | (0.7-1)^2 = 0.09; 0.55^2 + 0.57^2 + 0.02^2 = 0.6278; 0.6^2 = 0.36 | CONFIRMED |
| Console vs outcome | readout_run.log | `diff` (CR stripped): the outcome = the console minus 3 lines (the step stamp, "outcome written (write-once)", rc=0); 119 vs 122 lines | CONFIRMED |
| Write-once | open(..., "x") (R16 KILLED at READY); one outcome file, 16:59 | sha256 052dfcd1...a99b == E:/TaxoArena_backup_2026-10-03_e1sd/SHA256SUMS.txt. A probe re-run of --run was refused by the permission system: write-once rests on code and mutant, not on a re-execution | CONFIRMED (by code + sha) |
| DB of record | --verify rc 0 (both caches equal the backup table by table; only the 3 e1sd pools added, rows 3,503 / 3,452 / 3,410 == the files' judgeable ids) | read in run.log; embeddings_cache.db whole-file sha moved (52229e1e -> b0e88d3a) at the CP-1 checkpoint, per-table content UNCHANGED | CONFIRMED |
| Per-build launcher lines (P re-hash, (9), (10)) | builds rc 0 | NOT READ: my read of the six *_run.log was refused by the permission system. Not deciding: the readout re-ran check_run_dir on all six (pool, gate, closedByContent 0, config blob, [TRAIN-ONLY]) plus the guards and hygiene (fit texts 8,171 / 8,247 / 8,269, held-out in the fit 0) | UNDETERMINED (non-deciding) |

## N1. The N_e1sd1 outlier: construction outcome, not a fault

Evidence against a fault:
- exit completed, rc 0;
- the fixed-point certificate converged at iteration 17 (edits and trickle delta 0);
- [POOL] closedByContent 0 and sizes == the split;
- the embedder guard ADMITS on its own nomic_raw vectors (20 sites, min 0.9998) and both discriminators REFUSE;
- hygiene 0;
- the log's only "error" match is the ECE metric line;
- the config blob is the declared 4fac964f;
- the nomic pin is checked.

The mechanism is in proposals.csv and iteration_metrics.csv. Growth stalls at iteration 7 (27 leaves, J 0.1187; N_e1sd2 reaches
0.2583, N_e1sd3 0.2367). The large sites keep returning NO_PROPOSAL `min_pair_sep_below_bar` (sep 0.0095-0.0215 against bar
0.025), and later GROW proposals fail the z-gate (dJ < 0).

Result, in my assignment of distinct TRAIN texts:
- one leaf of 1,268 texts mixes health / biology / psychology (purity 0.315);
- one of 902 mixes chemistry / engineering / physics (0.569);
- TRAIN majority share is 0.554 (Q_e1sd1: 0.733);
- only 11 of 14 categories are ever a leaf majority (Q: 14).

So this is a coarse tree produced by the recipe's separation bar 0.025, which was tuned on qwen3, applied to nomic geometry
on this split. That is the split-sensitivity of the nomic construction, which is what the test measures. It cannot be removed post
hoc. A rebuild would test reproducibility only: E1-REPLICATES already found construction effectively deterministic at a fixed
split. It is optional and not needed for validity.

## N2. What the registrar may and may not write (registered text plus the L3 bracket)

MAY write (verbatim numbers):
- "SD1 NEITHER (K = 3; one recipe, one corpus). On each of the 3 content-closed re-draws the nomic_raw anchor-free tree files worse
  than qwen3: per-split paired Wald intervals wholly below 0 (G -0.1723, -0.0494, -0.0794; P3's event occurred). The spread clause
  fails: Gbar -0.1004 lies inside spread_N 0.1315, which is set by N_e1sd1 (28 leaves, top-1 0.5545)."
- "F-SD FIRED on its spread clause (abs(Gbar) <= max spread), not on its sign clause (no G_k >= 0)." With no BETTER verdict, the L3
  bracket keeps the registered sentence, so the E1 bracket reads verbatim: "at this split only; not stable across 3
  content-closed re-draws". Add a W-line beside it: "the sign was negative on all three re-draws. What was not stable is the
  magnitude, driven by the nomic construction's split sensitivity (spread_N 0.1315 vs spread_Q 0.0086)."
- Spread clause DESCRIPTIVE-ONLY, as registered (Support (f)): SD1 is thin, and K = 3 is named.

MAY NOT write:
- "WORSE", "consistently worse (established)", "F-E1 extends to 3 splits", or "the E1 loss replicates" as a verdict;
- any re-scoring without split 1. The leave-one-out Gbar -0.0644 is post hoc and stays out of the record, or appears only
  labelled post hoc and descriptive;
- "the E1 loss is a split artefact" or "nomic is no worse": the loss is larger on the re-draws (Gbar -0.1004 vs E1 -0.0456),
  and there is no TOST;
- "the -0.040 magnitude confirmed": P1 FAILED (G_1 and G_3 outside [-0.065, -0.015]; Gbar outside [-0.060, -0.020]);
- "the gap is stable" or "separable from split-draw variation";
- anything about routing, judging, arena pools, the p2dca 3,445, or another embedder, corpus or recipe.

Design note for the record (a W-line, not a re-scoring): the registered spread clause measures spread_N on the same builds that
produce G_k. A single coarse nomic build therefore enlarges both G_1 and spread_N, and turns three negative intervals into
NEITHER. This was foreseeable from Support (f)/(g) ("only a gap well beyond the true between-split range is reachable").

## DEFECTS

- PR-1 (LOW): ops run.log step 1 first called `gradlew.bat` without a path (rc 1, "not recognised"), then retried successfully;
  the java check before CP-0 was empty. No effect.
- PR-2 (LOW, scope): the per-build launcher logs were not read by me (permission refusal). Covered by the readout's
  check_run_dir and by --verify. Nothing in them can change the verdict.

## Commands

```
python scratchpad/post.py   # own split + nearest-leaf + TRAIN majority + Wald + spreads + F-SD + N_e1sd1 composition (ro/immutable)
diff <(tr -d '\r' < e1sd_readout_outcome.txt) <(tr -d '\r' < ops_20261003/readout_run.log)   # 3 added console lines only
sha256sum e1sd_readout_outcome.txt ; grep e1sd_readout_outcome E:/TaxoArena_backup_2026-10-03_e1sd/SHA256SUMS.txt   # equal
python -c "csv iteration_metrics.csv / proposals.csv per build (leaves, J, reasons)"; fixed_point_certificate.txt x6
tr -d '\r' < ops_20261003/run.log   # CP-0/CP-1 wal-ckpt OK content=UNCHANGED; verify rc 0; D3 restore sha 8bf21fe9
```
