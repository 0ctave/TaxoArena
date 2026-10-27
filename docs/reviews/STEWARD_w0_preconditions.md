# STEWARD w0 preconditions (data-steward, 2026-09-29; zero calls; read-only; HEAD e09e551)

Discharges the steward items of READY_w0_delta1 (fd6a349) and the registrar's record L21867-L21892 (e09e551).

## 1. RP06 C6-1 D3 — R512 re-draw dag_snapshots archived
Inputs = the files cert_redraw_r512.py (w0-rp06-cert-redraw) pins (untracked; sha256 equal to its S137/S2048 `jsonl.lf` pins):
- experiment_results/dimsweep2/bareq512_s137/seed_137/dag_snapshots.jsonl 6,738,074 B, mtime 2026-09-09 15:41:22, sha256 8da4e1ef92f72de126b532d5d052d7b3ade9bd590fccebe3d006300c5d86c0a0 (diagnostics/ copy byte-identical)
- experiment_results/dimsweep2/bareq512_s2048/seed_2048/dag_snapshots.jsonl 9,393,737 B, mtime 2026-09-09 16:03:14, sha256 ab36d2fcc255a35a3e93862598e36a9b7f8d80df80c3018464899562c1ee6abe (diagnostics/ copy byte-identical)
Archive: `Z:/FAC/TUBerlin/THESIS/TaxoArena_data/evidence_2026-09-25/redraw_r512_dag_snapshots/{bareq512_s137,bareq512_s2048}/dag_snapshots.jsonl` (cp -p) + `SHA256SUMS` (sha256 of SHA256SUMS 9e8e70453df94dbfe1290f17639d190bd10ee877560f131e6d1daf764057eb66); `sha256sum -c SHA256SUMS` OK x2. Same physical disk as the repo (guards deletion only). The site-null CSVs are tracked (not archived).

## 2. RP05 VA_FIT_SIZES (ruling 12)
Command: `TAXOARENA_DATA_ROOT=<main> python tools/analysis/flat_generality.py --dry-run` in worktree w0-rp05-flat-generality @ 5ab4d89 (V_A readings {assign nearest, fit_filing declared_label, heldout_anchor all_components_nearest}; "dry-run complete: zero measures on real data, nothing written"; pool p2dca21ab5f4ef3ae guard agreed).
Tree o0_clean_s42, O's depth-1 order Math, Physics, Economics, Other, Health, Chemistry, History, Psychology, Engineering, Biology, Business, Computer science, Law, Philosophy:
`VA_FIT_SIZES = {"o0_clean_s42": (944, 905, 587, 647, 504, 792, 267, 558, 656, 423, 542, 286, 666, 348)}`
Sum 8,125 = fit_n (every fit text filed; 0 excluded). Each exceeds its leaf count [11, 9, 5, 6, 5, 6, 3, 8, 5, 6, 7, 5, 5, 3].

## 3. SuperGPQA ruling 21 (presence only; no correctness read)
Command: `TAXOARENA_DATA_ROOT=<main> python tools/analysis/supergpqa_stage0.py --dry-run` in worktree w0-rp11-supergpqa-stage0 @ 639e60f (script blob:35b11858; "no stored correctness read").
All 49 whitelisted zero-shot files: records 26,529, present 26,529 of 26,529 uuids, 0 missing, 0 duplicate, 0 foreign -> complete on the full corpus 49/49. The post-exclusion population (26,529 - 1,251 = 25,278 uuids) is a subset, so presence there is also 49/49.
**Models whose completeness differs between post-exclusion and full corpus: 0 of 49.** (R3's duplicate-conflict half is --run's; with 0 duplicates it has nothing to check.)
Also from the same dry-run: A3 PASS; A4b identity PASS (1,251 = 370 EVAL / 881 TRAIN, equal to the pinned set; 20NG / ag_news readable, 0 collisions); A5 PASS (steward confirmation below); A6 PASS, 10 scored disciplines, scored EVAL 7,396 (= STAGE0b Support (a)).
A5 (C11-1) confirmed by the steward: both cards' front matter `license: odc-by` (SuperGPQA README sha256 0d670692...b083a; Records README sha256 fa79ea43...f7b2; retrieved 2026-09-27).

## 4. DATASET-SURVEY table (B2)
File: experiment_configs/dataset_survey_table_w0_steward.csv (sha256 2684ccf9d9e0ea398866c23b47865021c6482dc1e6db15c21e6d1503d57611cf, LF). SuperGPQA row only: models PASS 49, support PASS 10, closure PASS, key PASS (answer_letter presence), licence PASS odc-by; scoring_protocol / metric_granularity / cot_extraction REPORTED; dominance UNVERIFIED (needs correctness).
Validated by importing dataset_survey.read_table / c2 / c1 at 639e60f (no --analyze, nothing written): table accepted (value-vs-status C11-2 check passes); C2 SuperGPQA = ADMIT; C1 = FAILED as of now (126 cells of the other 14 candidates missing).
HAZARD: `--analyze` is WRITE-ONCE; running it on this table records C1 FAILED of record. The other 14 candidate rows are owed before --analyze.
