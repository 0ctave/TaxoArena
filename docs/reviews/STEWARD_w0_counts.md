# STEWARD w0 counts: RP03/04 steward half, the 422 residual file, the K46 census, WAL tails (2026-09-27)

Data-steward. Zero calls. Base: HEAD 6254bbc. Every DB was opened `mode=ro&immutable=1`. The sha256 of every object was equal before and after: eval_view e35b7518..., K46 store 44724d25..., REG corpora c8afeaa6... / 21d79e8c.... No verdict column was selected anywhere. Aggregates only; the one per-item file holds ids and no key (W11). Scripts are in the session scratchpad and are not committed.

## 1. RP03/04 steward_bracket (V2-DECLARED-CELLS HYGIENE leg U; ruling R4 (iii))

- **variant_rule = UNUSABLE_CELL** (R4 (iii) default). A (model, item) cell with more than one response row is unusable. An item is scored only if every roster cell is usable.
- **Coverage, leg U, EVAL of pv2_1575de61bb20e977.** Key-free: `SELECT model,item_id,COUNT(*) FROM response WHERE corpus_version='mc6-2026-09-11' AND model IN (<18 ACTIVE>) GROUP BY model,item_id`.
  - 6,153 items / 5,642 components.
  - 4,428 multi-response cells.
  - Scored N **5,907 in 5,404 components (Kish 1.3115)**. For comparison, AGREE would give 6,153 / 5,642 (Kish 1.3036).
  - 14 strata have >= 120 key-complete items (IFEval plus 13 MMLU-Pro). No stratum drops below 120 through coverage. Lowest: computer science 128, IFEval 162, health 165 of 204.
- **Coverage, leg U, TRAIN** (gen_view, the reader's `--dry-run` at db10f08): 12,351 items; 9,085 multi cells; 11,841 key-complete under UNUSABLE_CELL.
- **Coverage, leg M, EVAL of pv2_41dbd3dbcd399df0** (the same dry-run: pre-key cell lists, history excluded by name):
  - key-complete K12 3,351 / K37 3,350 of 3,492;
  - scored over the 13 categories: K12 3,244 / K37 3,243;
  - multi cells: K37 3,771 / K12 1,221;
  - every category stays >= 120; the smallest are computer science 128/128 and health 165/204 (19% of health is lost to multi-response cells).
- **The 422 residual items inside pv2_41dbd3dbcd399df0: 23** (all MMLU-Pro). All 422 lie in pv2_1575 EVAL, and 420 of them are in leg U's scored 5,907. So NO_RESIDUAL n = 5,907 - 420 = 5,487.

## 2. residual_file

`experiment_configs/v2_residual_band15_19_eval_422.txt`: 422 ids, sorted, v2 item_id space ("i:<stem_key>"), with 6 `#` header lines.
- **sha256-bytes (LF, of record) b35b3e03b9bcda48b5f447e76249d2184b418a711920b9e80224d16ff50cee90**; the CRLF rendering is 9d66ec944b62f1b7bc1a7003fbe4d190a5549221b601da052b4fa5f2690dda81; blob 7a3b0440ffcbaab76d5cf90f1c617d222691b6f8.
- **Derivation.** The pinned passage_closure (blob 003d5d4e) ran through `data_v2.split.load_corpora` on the sealed REG corpora, with `_channel` wrapped to keep its band pairs. The residual is the P pairs with a longest unmasked run of 15-19 tokens whose ends are on different sides of EVAL (EVAL x TRAIN/GATE); the file holds their EVAL ends.
- **Acceptance.** Every figure reproduces the record exactly:
  - U 840 excluded (digest e3d291d0...);
  - P 2,710 / O 62 / D 1, equal to `closure_edge` as sets; edge-set sha16 a4c613ed2d4957ad;
  - band totals P 2,773 / O 59;
  - cross-boundary P: 1,142 pairs, 422 EVAL items; pairs by source BBH 1,096 / MMLU-Pro 28 / MATH 12 / GPQA 4 / IFEval 2 (items 386 / 23 / 9 / 2 / 2);
  - O: 20 pairs / 19 items. These are NOT in the file; 19 of them are O-only, so P and O together cover 441.

## 3. census_bracket (K46-KEY-READ Support (a)/(f); READY e451753 D5)

**What was read.** Store `schedule` only (run_id, match_id, draw_index, variant_id, stem_key, contestants, reference_row_id, reference_vintage). **No vote, combined, match_status, verdict or finish_reason column was joined or selected.**

**What was joined from the view.** `open_eval("arena")`:
- `SELECT model,seen_ck,is_correct FROM response WHERE corpus_version='mmlu-pro-v2' AND model IN (<contestants>) AND seen_ck IN (<scheduled variants>)`;
- `SELECT variant_id,vintage,source_key,correct FROM reference WHERE corpus_version='mmlu-pro-v2' AND vintage='grok-reasoning-v0' AND variant_id IN (<ONE variants>)`.

**Joined counts.**
- 2,664 matches; 4,491 sides, each with exactly one row (0 refused).
- 174 ONE references, 0 null.
- Key-decidable = exactly one side correct.

| class | anchor | v0 (reference.correct) | key-decidable / scheduled |
|---|---|---|---|
| ONE | health | 1 | 248 / 309 |
| ONE | health | 0 | 26 / 83 |
| ONE | math | 1 | 258 / 401 |
| ONE | math | 0 | 12 / 25 |
| **ONE** | | | **544 / 818** |
| NONE | health | n/a | 658 / 940 |
| NONE | math | n/a | 600 / 906 |
| **NONE** | | | **1,258 / 1,846** |

**Per CK-CLOSE component.** DEFF bracket = [1, Kish m] (rho 0 to 1).

| class | components | Kish m (bar m) | max | DEFF bracket | n_eff | stem clusters (Kish m) |
|---|---|---|---|---|---|---|
| ONE | 160 (mean 3.40) | 4.934 | 9 | [1, 4.934] | [110.3, 544] | 161 (4.890) |
| NONE | 360 (mean 3.49) | 4.968 | 9 | [1, 4.968] | [253.2, 1,258] | 363 (4.936) |

ONE's component-size distribution: 1:26, 2:42, 3:51, 4:6, 5:4, 6:3, 7:10, 8:13, 9:5.

**Arithmetic for the registrar's pre-read line** (point 0.86, n 544). The SE is 0.01488 x sqrt(DEFF):

| DEFF | SE | MDE80 | n_eff |
|---|---|---|---|
| 1 | 0.0149 | 0.0417 | 544 |
| 2.0 | 0.0210 | 0.0589 | 272 |
| 4.934 | 0.0330 | 0.0925 | 110 |

The break-even DEFF for the 0.060 distance is 2.075. The registered n of 390 (share 0.477) is superseded by the counted 544 (share 0.665). Which DEFF inside the bracket is declared is the registrar's call.

## 4. WAL tails (embedder prerequisites)

The data-steward writes no DB, so the checkpoint was run on scratch copies only.

**Backup.** The originals (db, -wal, -shm) were copied byte-exact, sha-verified, to `experiment_results/_backup/wal_tails_2026-09-27/`. That directory is untracked and not in git; E: is the same physical disk. Originals are unchanged.

**Three views**, each a per-table row count plus sha16 over the sorted repr(rows):
- (a) the original, read with `immutable=1`;
- (b) a scratch copy read with `mode=ro` (WAL-inclusive);
- (c) a scratch copy after `wal_checkpoint(TRUNCATE)`, read with `immutable=1`.

Results:
- **nomic** `embeddings_cache_nomic-embed-text_latest.db` (-wal 4,647,392 B). (a) embeddings 11,722 vs (b) 11,769 (47 rows live only in the WAL); queries 8,299 in both. (c) equals (b); integrity ok.
- **20NG** `twenty_newsgroups_cache_v1.db` (-wal 708,672 B). (a) shows 3 tables. (b) shows 11 tables, including **reserved_pool 5,076**, reserved_pool_meta 1 and corpus_registry 1, which are absent under immutable. (c) equals (b); integrity ok.
- **ag_news** `ag_news_smoke_cache_v1.db` (-wal 206,032 B). (a) shows 3 tables. (b) includes **reserved_pool 600**, reserved_pool_meta 1 and corpus_registry 1. (c) equals (b); integrity ok.

**State.** For all three, the backup, the audit and the proof on copies are DONE. The in-place checkpoint at the canonical paths is NOT DONE: it is the coordinator's step, as in the precedent at prog L14016. The coordinator should re-assert view (b) before the write and view (a) = (b) after it. Until then, any immutable reader of 20NG or ag_news sees no reserved_pool table, and the nomic reader misses 47 vectors. The gemma cache (-wal 4,643,272 B) was not in this brief.
