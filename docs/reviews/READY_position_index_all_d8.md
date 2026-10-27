# READY delta check: POSITION-INDEX-ALL D8 / D4 / item 5.2 fix (adversarial reviewer, zero calls, read-only)

VERDICT: **READY-WITH-CONDITIONS** (C1-C4 below), for the run of `tools/analysis/position_index_all.py` at commit 817c70d (branch `vote-frame-pia-d8`, parent abf4db5).

## Identity (hash kinds named)

| file | blob | sha256-lf16 | sha256-crlf16 | vs main |
|---|---|---|---|---|
| tools/analysis/position_index_all.py @817c70d | blob:9c2ae4198971a0bd8984ed863f9fa20fd9aedf44 | 8939144e5ce87636 | 6f6694eac5a176f8 | replaces the rr3 READY blob:31299cf31e134e05657798f528954f578975d286 |
| tools/analysis/vote_frame_cert.py | blob:8e1fbf6a7d557c2a82f5769ecea89c1d03f10705 | 72ceddfe919a982e (= VFC_PIN_LF) | - | byte-identical to main |
| tools/analysis/tie_mechanics.py | blob:7f88d2ac581679aea33a2a25dc088883785fca86 | - | - | byte-identical to main |
| tools/analysis/pool_guard.py | blob:6521b51ac0fce04063563f9e6dcf42554ad86591 | - | - | byte-identical to main (the immutable guard of d30c19e) |
| rejudge_grok.py / rejudge_reasoning.py | blob:939de7c7... / blob:1339592a... | - | - | byte-identical to main |

Commands used:
- `git rev-parse 817c70d:<f>` against `git rev-parse main:<f>`;
- `git show 817c70d:tools/analysis/position_index_all.py | sha256sum` (LF), and the same piped through `sed 's/$/\r/'` (CRLF);
- `git diff --name-only abf4db5 817c70d | wc -l` = **1**, proved by COUNT;
- `git diff --stat`: 108 insertions, 5 deletions.

## 1. Does the diff touch only what is claimed? CONFIRMED

The whole `git diff abf4db5 817c70d` was read. It changes five things.
- **Docstring bracket:** one insertion-only [CORRECTED] bracket.
- **FAMILY_MAP:** the two Kotlin entries gain `tables=("judge_calls",)` (L159-L162).
- **`readable_matches()`:** new (L265-L276). It uses `vfc.long_key_fn` over the registered pair and requires exactly one row in each order. It returns None for WIDE tables.
- **`extract()`:**
  - a `tc` dict per table;
  - two counters on existing `continue`s (outside the subset; without a corpus or judge);
  - `tc["entered"] += 1` after `recs.append`;
  - a `[COUNTS]` note per table.
- **Selftest:** 3 fixtures (a two-table Kotlin-like cache, a no-judge cache, an arena13-like cache with unpaired selfref / t0a and 4 unresolvable labels) and 7 checks.

Nothing changes in `plan()`, the statistics, the criteria, the predictions or the write path. The worktree is clean (`git status --short` is empty).

## 2. Selftest and mutants

**Selftest.** `python position_index_all.py --selftest` and `python -O ...` on an archive of 817c70d (scratch `pia_d8/tree`):
- both print **"SELFTEST PASS: 52 checks, 0 failed; 1 INFO line"**;
- `grep -c "\[FAIL\]"` gives 0 and 0;
- `grep -c "\[PASS\]"` gives 52 and 52.

**Builder's mutate6.** Run from a COPY of the harness (`pia_d8/mutate6.py`, sha256 076eb37b... identical to the builder's), against the archive, never the worktree.
- Baseline: vote_frame_cert 240/0, tie_mechanics 29/0, position_index_all 52/0.
- **8 of 8 KILLED.** Originals restored byte-identical.

**My mutants** (`pia_d8/mutrev.py`, `mutrev2.py`; 13 applied; the file was restored and the blob re-checked as 9c2ae419 afterwards):

| mutant | result |
|---|---|
| R1 Kotlin board restricted to the WRONG table (verdicts) | KILLED (static FAMILY_MAP check) |
| R2 [COUNTS] `read` taken from `readable`, not from the reader's set | KILLED |
| R3 `readable` counted BEFORE the pairing rule (any order present) | **SURVIVED** |
| R4 `readable` ignores the duplicate rule (>= 1 each) | **SURVIVED** |
| R5 outside-subset drops not counted | **SURVIVED** |
| R6 outside-subset drops counted as no-judge | **SURVIVED** |
| R7 ENTERED printed as the cumulative record count | KILLED |
| R8 `dropped_unresolved` sign flipped | KILLED |
| R9 `table_counts` keyed by a constant | KILLED |
| R10 pair filter removed in `readable_matches` | SURVIVED: EQUIVALENT (the ==1 / ==1 test still requires both pair values) |
| R11 unit pair widened in `readable_matches` only | SURVIVED: not a realistic defect (the reader is unchanged) |
| R11b the READER handed the unpaired arm (ensemble, selfref) | KILLED (4 checks, including 5.2) |
| R12 no-judge counted but the record still entered | KILLED |

**What the four real survivors mean:**
- **R3 / R4:** no fixture has an incomplete or duplicate match key.
- **R5 / R6:** no check reads `outside_subset`.

These are gaps in DESCRIPTIVE counters; no statistic reads them. On the real data they cannot bite:
- the certificate shows `single_order_keys` 0 and `duplicate_keys` 0 on every entered LONG table;
- bfcl's outside-subset count was verified independently: 608 paired mids, of which 458 are in the deciding subset (`stratum='headline'` and `nj` empty), so 150 are outside, as printed.

Severity LOW; condition C4.

## 3. The `--dry-run` on the real caches

Command: `TAXOARENA_DATA_ROOT=Z:/FAC/TUBerlin/THESIS/TaxoArena python position_index_all.py --dry-run`, run from the 817c70d archive. The log is `pia_d8/dry.log` (176 lines, sha256-16 2904892a87117c79).

Hygiene:
- **Rule 7:** only the Gradle daemon and the Kotlin compile daemon were running (no construction, test JVM or site null).
- **No write:** sha256, size and mtime of the 62 caches, both pool DBs, the certificate JSON and ratings_x12.db were identical before and after (`snap.py`, twice: `SNAP-IDENTICAL`, `SNAP2-IDENTICAL`). Every -wal beside them is 0 B, and there is no -journal.

**P-C2: CONFIRMED.** Line 1 is `[POOLS]`. It names:
- `p2035adddedd1becb: check of record ... over the 228 ids`;
- `p2dca21ab5f4ef3ae verified by pool_guard.assert_pool_of_record`;
- `paeec37aa28063c75 verified by pool_guard.assert_pool_of_record`.

It also prints `"p2dca21ab5f4ef3ae"` and `"p8a29d8f3ff75aa55"` WITH quote characters as "not a pool of record; printed, not asserted". These come from escalate_llama_law.db's run_meta (`pool="..."`, `clean_pool="..."`). They are cosmetic only, because pools are printed, not asserted, for index entry. LOW.

Line 2 is the header, with LF sha 8939144e5ce87636. Line 3: `[CERT] ... HELD (sha256_16 c68a655ac64ae06d; certificate script LF 72ceddfe919a982e)`.

**Plan:**
- **ENTERED 50 caches.** Every one enters exactly ONE table (0 caches with more than one; regex over the ENTERED lines).
- **EXCLUDED 12 caches:**
  - 6 `_backup/` copies by prefix;
  - the RX copy (class UNCERTIFIABLE);
  - rubric_contrast (UNCERTIFIABLE);
  - leaf_powered and refgated (NOT-DUAL-ORDER);
  - **UNASSIGNED:** rubric_j6.db (named in the ruling at L13743) and **agent/bfcl_final_state_swap.db (not named in that ruling; LISTED, not silent)**.

**[COUNTS] for the tables that matter** (read / readable / dropped-unresolved / outside subset / no corpus or judge / ENTERED):

| table | read | readable | dropped unresolved | outside subset | no corpus / judge | ENTERED | expected |
|---|---|---|---|---|---|---|---|
| board/kotlin_c0d3f708 judge_calls | 9123 | 9123 | 0 | 0 | 0 | **9123** | 9,123 (verdicts skipped) |
| kotlin_ae92da30 judge_calls | 600 | 600 | 0 | 0 | 0 | **600** | 600 |
| arena13 verdicts | 1800 | 1800 | 0 | 0 | 0 | **1800** | 1800, all (ensemble, reversed) |
| newcomer_placement verdicts | 800 | 800 | 0 | 0 | 0 | **800** | 800 dual mids |
| newcomer_placement_steps verdicts | 400 | 400 | 0 | 0 | 0 | **400** | 400 |
| placebo verdicts | 599 | 599 | 0 | 0 | 0 | **599** | 599 |
| bfcl_judged_pilot verdicts (probe skipped) | 608 | 608 | 0 | 150 | 0 | **458** | BFCL_C1 n = 458 |

**Across all 50 tables:**
- sum of read 118,983; sum of ENTERED **118,833**;
- the difference, 150, is exactly bfcl's outside-subset count.

**Totals and double entry.** Checked by calling `plan()` and `extract()` from the archive (read-only; the snapshot is identical afterwards):
- `len(recs)` = **118,833**, equal to the sum of ENTERED;
- per-table record counts equal their ENTERED value for 50 of 50 tables;
- **0 duplicate (cache, table, row) keys**;
- **0 caches contributing more than one table**;
- Kotlin records are `judge_calls` 9,123, all with presentation_order pair (1, 2);
- arena13 records number 1,800, all with the arm pair (ensemble, reversed); no selfref, t0a or t0b row enters.

Content distinctness among ENTERED caches: 50 caches, 50 distinct sha256_16 values, so 0 collisions (the ruling-(1) belt). The earlier raw-text check found 0 shared raw responses across the non-_backup certified units (abf4db5 item 5.4).

The dry-run prints the FAMILY TABLE (B = 200), so the statistic is visible before `--run`. This is not new in this delta and not in its scope; stated only.

## 4. The recorded run conditions 5.1-5.7, checked against the dry-run

| item | verdict | evidence |
|---|---|---|
| 5.1 the contestant caches are read transposed | MET | the four enter as CERTIFIED-CONTESTANT with 0 unresolved drops. The frame was verified in abf4db5; the reader (vfc blob 8e1fbf6a) is unchanged |
| 5.2 arena13 is the (ensemble, reversed) pair only | MET | 1800 records, all with the (ensemble, reversed) arm pair; fixture plus mutant R11b KILLED |
| 5.3 names are keyed by basename; NEW / GEM at run time | MET for this dry-run | the four are entered at their certified paths; `dropped for an unresolved label 0` on all four is the run-time proof that the current NEW / GEM constants resolve every label |
| 5.4 `_backup/` excluded; 0 collisions | MET | 6 excluded by prefix, 1 by class; 50 of 50 distinct sha |
| 5.5 exclusions by class | MET | rubric_contrast and the RX copy UNCERTIFIABLE; leaf_powered and refgated NOT-DUAL-ORDER |
| 5.6 Kotlin: one table | MET (D8 fixed) | judge_calls only, 9,123 and 600 entered; verdicts skipped and listed |
| 5.7 bfcl: one table | MET | `tables=("verdicts",)`; probe skipped; 458 entered |

## Conditions for the run

- **C1.** Run blob:9c2ae4198971a0bd8984ed863f9fa20fd9aedf44 (sha256-lf16 8939144e5ce87636), merged to main by pathspec. The run's header must print LF 8939144e5ce87636. vote_frame_cert.py must stay blob:8e1fbf6a (VFC_PIN_LF 72ceddfe919a982e).
- **C2.** The run's `[POOLS]` line must match P-C2 as above. Its `[COUNTS]` notes must reproduce this dry-run exactly: 50 tables, ENTERED sum 118,833, and the table above (Kotlin 9123 / 600, arena13 1800, newcomer 800 / 400, placebo 599, bfcl 608 / 150 / 458), with every `dropped for an unresolved label` equal to 0. Any difference is a failed precondition, not an outcome.
- **C3.** The registrar records `experiment_results/agent/bfcl_final_state_swap.db` as a third UNASSIGNED cache beside rubric_j6 (L13743 names rubric_j6 and rk1b_cards only). It is listed, not silent; no code change.
- **C4 (not blocking this run; before any reuse or edit of these counters).** Add fixtures that kill R3 / R4 (a LONG table with an incomplete key and with a duplicate key) and R5 / R6 (an asserted `outside_subset` count). The counters are descriptive; on the real data the pairing rule is inert (0 single-order keys, 0 duplicate keys) and bfcl's 150 was verified independently.

## Defects

| id | severity | defect | fix |
|---|---|---|---|
| E1 | LOW | Mutants R3-R6 survive: `readable_matches`' pairing rule and the `outside_subset` counter are untested | C4 |
| E2 | LOW | `[POOLS]` prints quoted pool strings from escalate_llama_law's run_meta as "not a pool of record" (p8a29 among them) | cosmetic; note it in the outcome, or strip quotes in a later delta |
| E3 | LOW | bfcl_final_state_swap.db is UNASSIGNED without a ruling naming it | C3 |

No BLOCKER. No HIGH.

## What this check does not show

- It re-derives no family statistic (s, DEFF, MDE). Those are the run's and the post-run review's job.
- It does not re-run mutate4, mutate5 or mutate_rr on the final file. The builder ran them on the pre-final file; mutate6 and my 13 mutants cover this delta's hunks only.
- It does not re-verify pool_guard beyond its execution witnessed on line 1.
- It does not check the qid mapping or clustering of any cache (unchanged by this delta).
