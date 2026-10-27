# POST-RUN review: HIER-FAIR-BACKOFF + BACKOFF-ROBUST, TREE-CUT-GRANULARITY + NESTING (adversarial; zero calls; read-only)

Reviewed outcomes (write-once, never committed; equal to the backups, `sha256sum -c SHA256SUMS.txt` 4/4 and 3/3 OK):
- `experiment_results/archv2/hier_fair_backoff/outcome.txt` sha256 0214a5025bc933e5... (127 lines; marker READ_STARTED 8a738a3e...),
  backup E:/TaxoArena_backup_20261008_hier_fair_backoff (outcome, run log, dry-run log, marker).
- `experiment_results/tree_cut_granularity/tree_cut_granularity_outcome.txt` sha256 264788bdc781b2ab... (130 lines), backup
  E:/TaxoArena_backup_20261008_tree_cut_granularity (outcome, run log, dry-run log). Run log = outcome + 2 RuntimeWarning lines
  (3PL `exp` overflow, R2_int only, 3PL converged True on every tree) + the write line (`diff`).
Scripts: hier_fair_backoff.py blob:6d3e86b5 and tree_cut_granularity.py blob:c80c3c10 (LF; `git hash-object` on the working tree =
`git rev-parse HEAD:<path>` = READY 17c34de9's pins; the outcome headers print the same blobs, lf16 83e64294 / b1c3d18d).
Registrations prog L24974-L24987, L24989-L25000, L25002-L25014, L25016-L25027 (`_as_of` e83b59d5); READY conditions C1-C3 and D-shm
(READY_hier-fair-backoff_tree-cut-granularity.md L48-L51), carried at prog L25155.

## VERDICT
- **HIER-FAIR-BACKOFF: VALID.** HB1 = **KMEANS-BETTER** (D_final -0.530pp, 95% [-0.944, -0.106]); HB2 = **NEITHER** (D_gain +0.125pp
  [-0.283, +0.541]); PARITY REFUTED (sign word; SCOREABLE leg); TREE-BETTER and DIVIDEND-TREE refuted; F-HB FIRES as registered.
  Word carries qualifier W-1 (the sign words are DESCRIPTIVE-ONLY by the registered Support (f), and |D_final| 0.53pp sits below its
  own measured MDE80 0.61pp).
- **BACKOFF-ROBUST: VALID.** R1 = **ROBUST** (TAU200 and NO-XSRC both (KMEANS-BETTER, NEITHER)); F-BR NOT FIRED. Qualifier W-2.
- **TREE-CUT-GRANULARITY: VALID.** TC = **CUT-WORSE** (3 of 3 trees); rule 8 not refuted; F-TC NOT FIRED.
- **NESTING: VALID.** NV = **NON-NESTED** (6 of 6 cells; min V90 over 30 seed values 0.3807 vs bar 0.10); F-NV NOT FIRED.
Every deciding number reproduces to the printed digit under my own code (below). No blocker.

## Per-claim table (deciding claims)
| # | claim (outcome) | reviewer's number | verdict | sev |
|---|---|---|---|---|
| 1 | HFB data object: TRAIN-CV 11,841 items / 10,781 components; GATE 1,944; roster 18 (no Llama-3-70B); GATE∩TRAIN 0 | own filter on the captured TRAIN key (all 18 models present, AF cell, not pseudo, vector): 11,841 / 10,781; GATE 1,944; overlap 0; Llama-3-70B absent | CONFIRMED | - |
| 2 | folds (salt FOLDS-1) sizes 1234/.../1179; xsrc 311, per fold 20/40/.../31 | own sha256(component+salt) mod 10: identical 10 sizes; xsrc 311, identical per-fold | CONFIRMED | - |
| 3 | tau* per fold, AF-U and BC0-BC4 (median AF-U 100) | own node aggregation (parent walk) + own top-down shrinkage + own GATE argmax: all 60 tau* identical | CONFIRMED | - |
| 4 | TRAIN-CV accuracies TF .63145, TB .63618, TB200 .63609, BCF_s, BCB_s, BCB200_s | own columns: all 18 values identical to 5 dp | CONFIRMED | - |
| 5 | HB1 D_final -0.00530 [-0.00944, -0.00106], 90% [-0.00901, -0.00180] -> KMEANS-BETTER | own two-stage bootstrap (components, then seeds), default_rng(20261008), B 2,000: identical to 5 dp. rng 1: [-0.00951, -0.00090]; rng 2: [-0.00924, -0.00101]: the word holds under 3 streams; per-seed D 5/5 negative | CONFIRMED | - |
| 6 | HB2 D_gain +0.00125 [-0.00283, +0.00541] -> NEITHER | identical; rng 1/2 also NEITHER | CONFIRMED | - |
| 7 | Measured support D_final: SE 0.00217, SEc 0.00164, DEFF 1.762 (reg 1.61), n_eff 6,119 (reg 6,696), MDE80 0.61pp (reg 0.55) | own: 0.00217 / 0.00164 / 1.762 / 6,119 / 0.608pp. D_gain DEFF 1.290 (reg 1.56), n_eff 8,356, MDE80 0.589pp. Kish component size 1.3336 (mean 1.0983 = reg (a)). TOST at measured SE needs 2.487 x 0.217 = 0.540 <= 0.55: PARITY stays SCOREABLE | CONFIRMED | - |
| 8 | Rule 8 / F-HB: PARITY refuted, F-HB FIRES | follows from HB1 = KMEANS-BETTER (registered clause, L24981/L24983) | CONFIRMED; qualifier W-1 | MEDIUM (words) |
| 9 | R1 ROBUST: TAU200 D_final -0.00522 [-0.00947, -0.00097]; NO-XSRC -0.00513 [-0.00943, -0.00069] (n 11,530 / 10,474) | identical to 5 dp; words (KMEANS-BETTER, NEITHER) on both legs; R1 ROBUST | CONFIRMED | - |
| 10 | BACKOFF-ROBUST support: TAU200 SE 0.00220 (reg 0.00147), DEFF 2.074, MDE80 0.62pp (reg 0.41) | own: 0.00220 / 2.074 / 0.616pp. The registered SCOREABLE status of TAU200 (predicted 0.45 > MDE80 0.41) does not survive: observed 0.52pp < measured 0.62pp | CONFIRMED number; W-2 | MEDIUM |
| 11 | Descriptive per source (MMLU_PRO -0.755pp [-1.28, -0.23], BBH NEITHER, IFEVAL +2.71pp, NON_BBH -0.547pp) | spot check: all 8 subsets identical to 5 dp | CONFIRMED (spot) | - |
| 12 | HB3 (EVAL, descriptive) D_final +0.288pp, D_gain +0.538pp | arithmetic from the printed arm points: +0.00287 / +0.00536 (rounding of 5-dp arms); EVAL not re-read | spot check | - |
| 13 | TCG data objects: 3 trees 80/87/72 leaves; held-out 3,598/3,522/3,500 in 3,546/3,479/3,442 stem_key groups; fit 8,171/8,247/8,269; hygiene 0/0/0 | pinned loader (load_real) + own structure: same L_d per depth, same used depths [2-7]/[2-7]/[2-6], same group counts | CONFIRMED | - |
| 14 | D_cut -0.02976 [-0.03826, -0.02089]; -0.02626 [-0.03434, -0.01886]; -0.03154 [-0.03969, -0.02288] | own cut map, own nearest-leaf filing, own M1 (majority = first-inserted on ties, the registered score_cells rule), own stem_key-group bootstrap rng 20261008: identical to 5 dp on all 3 trees; rng 7 within 0.0007 | CONFIRMED | - |
| 15 | spread_KM 0.01232 / 0.00592 / 0.01046; bar 0.01232 / 0.00830 / 0.01046; TC1 CUT-WORSE x3 -> TC CUT-WORSE | identical; |D_cut| exceeds also the realised MDE80 (0.0124 / 0.0113 / 0.0120) | CONFIRMED | - |
| 16 | NV1: 30 V90 values; NON-NESTED 6/6; IDENTITY tree V90 0 | own V90: all 30 values identical to 4 dp; own tree-primary-leaf V90 0.0000 in 6/6 cells (BKM identity not re-run) | CONFIRMED | - |
| 17 | READY conditions: C1 [SCRIPT] blob c80c3c10 in dry-run AND run; C2 no [HFB-CV-DENOM]; C3 D1/D2/D4 printed | `grep -n "\[SCRIPT\]"` both logs = pin; `grep -ci refused` HFB logs 0; outcome prints "DESCRIPTIVE NOT DONE", KEY 46 models / 10,925, KWF = K_s cells | CONFIRMED | - |
| 18 | No write to a DB of record | gen_view c2930c60 / eval_view e35b7518 sha before = after; embeddings_cache, multicorpus, mmlu_pro_dataset_cache_v2 size+mtime unchanged; only `mmlu_pro_dataset_cache_v2.db-shm` mtime moved (D-shm, known, READY row 16) | CONFIRMED | LOW |

## Defects / qualifiers
- **W-1 (MEDIUM; registrar, words).** HB1's KMEANS-BETTER is reached by the registered clause and F-HB fires by its registered "iff",
  but the registered Support (f) classed HB1's sign words DESCRIPTIVE-ONLY, and the measured MDE80 (0.61pp) exceeds |D_final| 0.53pp.
  The outcome prints the verdict line and the FIRES line on separate lines with no qualifier beside the word. Fix: record
  "HB1 KMEANS-BETTER [DESCRIPTIVE-ONLY by Support (f); 0.53pp < measured MDE80 0.61pp; robust to 3 bootstrap streams, 5/5 seeds,
  TAU200, NO-XSRC and the symmetric cross-source removal (W-3)]; PARITY REFUTED (SCOREABLE)". The SCOREABLE finding of record is
  the refutation of PARITY; F-HB's withdrawal of "the tree's hierarchy routes better" stands as registered.
- **W-2 (MEDIUM; registrar).** BACKOFF-ROBUST's TAU200 planning SE 0.147pp (pilot fixed-tau interval) understated the measured 0.220pp by
  1.50x; the TAU200 sign word, registered "SCOREABLE (narrowly)", is not SCOREABLE at the measured support. R1 ROBUST still follows (no word
  changed). Quote R1 as "ROBUST (each leg below its measured MDE80)". Future registrations: take the transported SE from the two-stage
  (seed-and-component) interval, not a component-only one.
- **W-3 (LOW; descriptive, reading aid).** NO-XSRC removes AF-U's 311 cross-source filings only; BC_s (nearest centroid over all leaves)
  files 410-421 TRAIN items into another source's leaf. Removing both sides' (n 11,122): D_final -0.602pp [-1.042, -0.158], KMEANS-BETTER;
  D_gain NEITHER. The asymmetry does not carry the word.
- **W-4 (LOW).** Support under-statements without word consequence: HFB D_final DEFF 1.762 vs 1.61; TCG realised SE 0.0040-0.0044 vs
  registered 0.0030 (1.35-1.47x; Kish m-bar 1.025-1.033 vs DEFF 1.0); NV across-seed SD up to 0.054 vs 0.045. Each word clears its
  realised MDE80.
- **W-5 (LOW).** HFB's deciding leg re-reads the pilot's 11,841 TRAIN items (registered: NOT an independent replication). The pilot's
  D_final -0.059pp moved to -0.530pp under the new fold salt and the GATE tau rule; P1 FAILED. Quote with the registered "not an
  independent replication" sentence. HB3 (EVAL, unseen) reads +0.29pp NEITHER (descriptive): the sign does not transfer to EVAL.
- **W-6 (LOW; carried).** 3PL `exp` overflow RuntimeWarning in the TCG run log, R2_int only (descriptive); D-shm unchanged (READY row 16).
- Independence note: the TCG KM arm was refitted with the registered fitter (CA.skm_best); an independent sklearn KMeans (seed 0, 10
  restarts, unit rows, own tie rule) gives D < 0 at 16 of 17 tree-depths and 0.00000 at Q_e1sd3 d6; not deciding.

## Commands (all read-only; busy.ps1 exit 1 before each; scratch E:/TaxoArena_tmp/postrun_hier, never committed)
```
sha256sum -c SHA256SUMS.txt   (both backup dirs); sha256sum experiment_results/{archv2/hier_fair_backoff,tree_cut_granularity}/*
git hash-object tools/analysis/{hier_fair_backoff,tree_cut_granularity}.py ; git rev-parse HEAD:<same>   -> 6d3e86b5 / c80c3c10
grep -n "\[SCRIPT\]" tcg_dryrun.log tcg_run.log ; grep -ci refused hfb_*.log ; diff tcg_run.log tree_cut_granularity_outcome.txt
python hier_fair_backoff_postrun.py      (sha256-16 52bb62570ef6859f): pinned prepare()+read_views(between=capture) then raise
   BEFORE the eval view (no marker; asserted); own folds, node stats, shrinkage, tau*, columns, two-stage bootstrap x3 streams, DEFF
python hier_fair_backoff_postrun_symm.py (c8c9faa1d03af48c): W-3
python tree_cut_granularity_postrun.py    (9eea3fc867e46921): own M1 (alphabetical ties) + sklearn leg -> D_cut -0.02954/-0.02630/-0.03023, same words
python tree_cut_granularity_postrun_v2.py (b3a5fd8e8cf14fec): registered tie rule -> every number identical to the outcome
before/after: sha256sum gen_view_REG.db eval_view_REG.db; ls -l --time-style=full-iso <cache DBs and sidecars>; diff -> only the -shm line
outputs: hfb_postrun.out 870625dc384e5bab, hfb_symm.out f418b0bb655688d9, tcg_postrun.out 1a93255c1c8030e4, tcg_postrun_v2.out 8ddfa5e81ead4de1
```
