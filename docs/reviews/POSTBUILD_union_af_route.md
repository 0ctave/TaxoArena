# POSTBUILD — UNION-AF-ROUTE (RP13): AF-U build validity + C-M2 (real dry-run of the mirrored reader)

Reviewer: adversarial-reviewer, 2026-10-03. Zero calls, no JVM, no construction. Objects: the AF-U outputs copied to main,
`experiment_results/archv2/union_af_route/AF-U/` (built in rp13-afu-run2 at 1075b506; ops c23fe5cd, log ops_20261003b/), and
the inputs under `.../union_af_route/inputs/` (built by reader blob f569d6f4). Reader under review: union-af-mirror b1262ecc,
union_af_route.py blob bf3f17dbdc42dbfc6803687d8739d459fc1ed75d (sha256-lf16 50524cdfedde3256 / sha256-crlf16
d7d1c978e5f72f0e). No JVM was running at review time.

## Verdict

**The build is VALID under the amendment (L23660-L23667).** C-M1 is closed (b1262ecc changes tests only) and C-M2 is closed
(real dry-run rc 0; full mutants 93/93). **The reader's `--run` MAY GO** once union-af-mirror b1262ecc is merged into main by
path (union_af_route.py only), with the command at the end. The `queries` deviation is benign for RP13, but the worktree DB
copies must never be promoted to main (D-PB-1).

## Per-claim table

| # | claim | my result | verdict | sev |
|---|---|---|---|---|
| B1 | ifeval S1-S6 | `single_evidence('ifeval','IFEVAL')` (bf3f17db, ROOT = main) gives root n00000001, best 0.02111, n 325, 15 rows, cell IFEVAL:n00000001; it matches the declaration single_cell_members.json (sha256-lf16 ce4249af0862d0bb) | CONFIRMED | — |
| B2 | D-8: one commit | All 7 run_manifests (6 members + graft) carry commit 1075b506 with dirty False / dirty_src False. Each member's split_v2.config_sha256_lf equals the LF sha of main's TOML (6/6); the graft's equals the filled TOML, which is byte-equal in main and worktree | CONFIRMED | — |
| B3 | The graft omits IFEVAL | Filled TOML: 5 unionSnapshots = the members' logged `Snapshot ID:` values; corpora = BBH, MATH, MUSR, GPQA, MMLU_PRO_LB. The leaves CSV has 122 leaves (MMLU_PRO_LB 69, BBH 36, MATH 10, GPQA 4, MUSR 3), equal to each member's last-snapshot leaf count. IFEVAL rows: 0 in the graft queries, 0 in the train queries | CONFIRMED | — |
| B4 | 1,139-row `queries` deviation | My diff of main's queries (immutable) against a scratch copy of the worktree DB + its -wal: **+1,139 new rows** (BBH 1,031, MATH 64, MUSR 41, GPQA 3; IFEVAL none, since its build refused before saveSnapshot); 0 removed; **10,888 existing rows changed** (6,973 ground_truth_category + query_id, e.g. 'Math' → 'MMLU_PRO_LB/math'; 3,915 query_id only), which the operator's count-only delta did not show. All 1,139 new texts already have a main embedding (no embedding call; embeddings 39,631 unchanged). Cause: the text-keyed last-writer rewrite (memory shared-query-cache-categories / construction-writes-cache-dbs). READY's "expected 0" was the reviewer's error: B0 was also built from worktree copies (rp12-r2-run), so main never received its texts. No RP13 reader reads `queries` (grep over the reader chain: 0). Main is unchanged (operator's hashes; my DB listing before and after the dry-run, identical) | EXPLAINED, benign for RP13 | MEDIUM (D-PB-1) |
| B5 | 123 leaves vs 124 distinct AF cells | inputs/af_cells.tsv: 18,504 items, 124 distinct = 123 leaf cells (MMLU_PRO_LB 69, BBH 36, MATH 10, GPQA 4, MUSR 3, IFEVAL 1) + `<no-routing-row>` (2 items). inputs_manifest counts: no_row_train 2, no_row_eval 0 (G14 also had 2 TRAIN items fitted as their own cell, 0 EVAL). Per R1 they are fitted as their own TRAIN cell and never enter EVAL scoring | CONFIRMED (benign) | — |
| B6 | The outputs copied to main are byte-equal | Walking rp13-afu-run2/experiment_results/archv2/union_af_route/AF-U: 164 files, all present in main and sha256-equal (0 missing, 0 differing), plus the filled graft TOML (`cmp` equal). "165" = 164 + the TOML | CONFIRMED | — |
| B7 | IFEVAL merge rows | manifest `single.IFEVAL.merged` = 216 held-out (162 EVAL + 54 GATE), 325 TRAIN (= n_site), name IFEVAL/ifeval (IFEVAL has one declared class) | CONFIRMED | — |
| C-M1 | O15 killed | b1262ecc = +16 test lines in single_e2e, no code change (AST: functions changed vs 1075b506 are only `_fx_full, ak_compute, ak_lines, run, single_lines, st_single_e2e` + new `ak_mirrored`, `_oracle_ak_mirror`, all reviewed in READY_union_af_mirror). Mutant table: `O15 ... KILLED` | CONFIRMED | — |
| C-M2a | Full mutants | `MUTANTS: 93 of 93 KILLED; control survived; survivors none` (on bf3f17db); selftest 12/12 | CONFIRMED | — |
| C-M2b | Real dry-run (mirrored reader) | rc 0, run against main's data: POOL line first; AK-IDENTITY reproduced; ONE-CELL IFEVAL verified; D-8 1075b506; leaves total 123; inputs manifest (sha256-lf 53021e26…) with 18 AF-U files and 11 inputs EQUAL to their pins; B0-2 pool check rc 0; leg U dry-run (gen_view TRAIN 12,358, GATE 2,033, EVAL 0; EVAL from side export 6,153 / 5,642); "no key column selected; nothing written; no statistic of AF-U printed". File count under union_af_route/ was 195 before and after; root DB listing unchanged | CONFIRMED | — |
| C-M2c | Inputs built by f569d6f4 are valid for bf3f17db | AST: build_inputs, merged_validation, af_cells, k_cells, us_fit, single_evidence, load_inputs and afu_state are identical in both blobs. `--run` re-derives the K cells (R4) and refuses on any difference | CONFIRMED | — |

## Defects

- **D-PB-1 (MEDIUM, data hygiene)**: rp13-afu-run2's embeddings_cache.db (+ its -wal tail) carries 10,888 rewritten
  categories (MMLU-Pro bare categories → `MMLU_PRO_LB/<domain>`) and 1,139 new rows. It must never replace main's copy, which
  would break p2dca category readers (the shared-category gotcha). Delete the worktree copies, or label them non-promotable in
  the operator log. Future construction READYs should expect a NON-zero `queries` delta for any union build made from a
  worktree copy, and diff rows, not counts.
- **L-PB-2 (LOW)**: the operator's acceptance step compared counts and a hash only. The row-level diff above should be pasted
  into the operator log (registrar).

## `--run` (may go)

1. Merge union-af-mirror b1262ecc into main by path: `tools/analysis/union_af_route.py` (blob bf3f17db) only.
2. From the MAIN checkout, with no construction or other pool reader running (rule 7):
   `python tools/analysis/union_af_route.py --run`
   This does one EVAL key read (B1 marker) and writes the outcome once to experiment_results/archv2/union_af_route/outcome.txt.
   The policy goes to scratch/ (git-ignored, never committed).
3. Then the post-run review: recompute G_AF, D_K, M_AF and the mirrored D_AU / D_AUs from the printed means; re-measure DEFF.

## Commands

```
for m in ifeval gpqa musr math bbh mmlu_pro_lb graft_flatleaf: run_manifest commit/dirty/anchor_free/config_sha256_lf   # all 1075b506, False
python: config_sha256_lf == sha256-lf(main TOML) (6/6); graft TOML cmp main vs worktree (equal)
grep "Snapshot ID" member logs == filled unionSnapshots; leaves CSV Counter (122); IFEVAL rows in graft CSVs (0, 0)
python: walk worktree AF-U vs main, sha256 per file -> 164/164 equal
python: queries main(immutable) vs scratch copy of worktree DB+wal -> new 1139 / gone 0 / changed 10888 (6973 cat+qid, 3915 qid)
python: af_cells.tsv distinct 124 (= 123 leaves + <no-routing-row> x2); inputs_manifest counts
(worktree union-af-mirror b1262ecc) python tools/analysis/union_af_route.py --selftest   # 12/12
(worktree) python tools/analysis/union_af_route.py --mutants                             # 93 of 93 KILLED
TAXOARENA_DATA_ROOT=<main> TAXOARENA_RESULTS_ROOT=<main> python tools/analysis/union_af_route.py --dry-run   # rc 0, nothing written
python ast: functions identical between 1075b506 and b1262ecc for the inputs path
```
