# READY review (pre-data): BZ-MMLUPRO-MOREMODELS (draft blob 19cbde62, LF; commit 5f64b3b8)

Reviewer: adversarial reviewer, 2026-10-21, `_as_of ca7728d7`. Zero runs, zero LLM calls; no compact part opened.
Read: the draft; author decisions 2026-10-21 D-2/D-3; benchzoom 450b86e (`src/benchzoom/sources.py` blob 67752ddc,
`examples/fetch_zoom_data.py` f39c27d8, `examples/launch_oll_more.py` cefb38ed; LF, working tree = HEAD); the pinned
contents parquet (revision 9c09a7ca, 4,576 rows); `oll_parts_more/selection_cap8_raw0.12.csv` (sha256 21a5625d...);
BZ-METER-AXIS `outcome.json`.

## Verdict

**READY WITH EDITS (registration text; READY-1 still needs the census, code and synthetic gate).** Edits M1-M7 go in
as `[D<n>]` brackets before the registration commit. The selection rule must be replaced by the code's rule at cap 8
(M2): the draft's cap-3 set is NOT a subset of what is being downloaded.

## Cap reconciliation (the deciding object)

- Draft rule literal (bf16 > fp16 precision, `Base Model` literal family, cap 3 by lowest sha256(fullname)):
  452 after (1)-(3), 356 after (4)-(5), 281 Base Model values (228 self), **335 at cap 3, 312 after dropping the 24
  cached**; cap 1/2/5 -> 262/295/322 after (7). All registrar counts reproduce to the unit.
- Downloaded set S8 = `oll_select_models(contents, min_raw=0.12, family_cap=8)`: **348 selected, 282 families**;
  identical to the on-disk selection CSV (set equality True). Only 7 families exceed 3 in S8 (Mistral-7B-v0.1 8,
  Mixtral-8x7B-v0.1 5, Qwen2.5-7B 5, Meta-Llama-3.1-8B 4, Meta-Llama-3-8B 4, Bielik-11B-v2 4, gemma-2-2b 4).
- **Draft cap-3 subset of S8: NO, 2 missing**: `HuggingFaceH4/zephyr-7b-alpha`, `teknium/OpenHermes-2.5-Mistral-7B`
  (Mistral-7B-v0.1 family; the code kept 8 of 16 at evenly spread raw ranks, the draft's sha pick lands on 2 others).
  Registering the draft rule would need 2 post-hoc fetches; not proposed.
- Further rule differences draft vs code: precision (code: latest Submission Date first, then bf16 > fp16) picks
  float16 for 5 selected models where the draft picks bfloat16 (Qwen2.5-0.5B-Instruct, Llama-3.1-Tulu-3-8B,
  Meta-Llama-3-8B-Instruct, Phi-3-mini-4k-instruct, Mistral-Small-Instruct-2409): the downloaded parts are those
  rows' runs; `Flagged` is not tested by the code (0 flagged among S8, so no effect); placeholder families ("Removed",
  "None", empty) are the model's own name in the code (282 vs 281 families). Pre-cap sets are equal (356 = 356).
- **Decision: register cap 8 = the downloaded set (code rule verbatim, blob 67752ddc, selection CSV sha256
  21a5625d...).** Reasons: it is the object actually read; a cap-3 rule inside S8 (lowest sha256 per code family: 335
  selected, 312 new) is reachable but adds a second post-download rule for no SE gain (the SE is item-clustered;
  families are not the cluster unit), and the cap at 8 trims one family only (Mistral-7B-v0.1 16 -> 8). The cap-3
  subset is kept as a SENSITIVITY with no word (M3). Disclose: the within-family pick uses `MMLU-PRO Raw` ranks, an
  aggregate of outcomes on these same items (vault included); it touches 8 models of one family.

## Reviewer question Q2 settled

- **Cap: 8 (above).** Self-referencing `Base Model` (228 of 356 = self) makes any cap a light cluster trim; say so.
- **Reasoning regex: keep `(?i)(r1|qwq|reason|think)` as the derivation, register the frozen list it yields on S8:
  7 names** (Qwen/QwQ-32B-Preview, cognitivecomputations/Dolphin3.0-R1-Mistral-24B, deepseek-ai/DeepSeek-R1-Distill-
  {Llama-70B, Llama-8B, Qwen-14B, Qwen-32B, Qwen-7B}); 0 false positives on S8. Math-tuned instruct models (Qwen2.5-Math,
  AceMath, OpenMath2, MetaMath) are not long-CoT reasoning-tuned and stay in; print them as a descriptive list.

## Per-claim table (deciding claims)

| # | claim | reviewer's number | state | sev |
|---|---|---|---|---|
| 1 | selection counts 452 / 356 / 281 / 335 / 312; cap 1/2/5 262/295/322 | identical (draft rule literal) | CONFIRMED | - |
| 2 | the frozen roster = the cap-3 rule | download uses cap 8 (348 / 325 to fetch); cap-3 set not inside it (2 missing) | REFUTED | HIGH (M2) |
| 3 | "frozen roster committed in the census before any download"; "no per-item details file opened before READY" | the fetch started 2026-10-21 18:01 (benchzoom 450b86e, log fetch_more_20261021_180104.log); 89 parts written at review time; the fetcher parsed each details file into a compact per-item part and logged per-model accuracy (= the public aggregate); no meter or item-level reader is known to have opened a part | REFUTED (procedure) | HIGH (M1) |
| 4 | DEFF 1.13, n_eff 4,134 "measured on this corpus's own cache" | outcome.json mmlu_pro L3a-L2: deff 1.125713, n_eff 4,134.27, se 0.0183072, mde80 0.0702997 (23-model roster) | CONFIRMED (numbers) | - |
| 5 | SE 0.0183 carried with no roster credit; MDE80 0.0703 | 3.84 x 0.0183 = 0.07027; credit arithmetic 0.0183 x sqrt(23/312) = 0.00497. DEFF = (SE/SE_cell_iid)^2 is cross-model within-item correlation and GROWS with the roster: constant-ICC (rho 0.00571) gives DEFF 2.85, SE 0.0078, MDE80 0.030 at 325 models: still below 0.0183, so the carried SE is conservative, but "DEFF 1.13 / n_eff 4,134" is not the roster's | PARTLY | MEDIUM (M5) |
| 6 | SCOREABLE; structural leg PASSES | MDE80 0.0703 < 0.10; SUPPORTED reachable at infinite n iff g >= 0.10 (leaves cross `src` within category) | CONFIRMED | - |
| 7 | roster disjoint from the 24 cached | 23 of the 24 cached are in S8 and skipped (`--skip-parts-dir`); QwQ-32B not in S8; 325 fetched | CONFIRMED | - |
| 8 | (8) missing / under-99% details dropped | failures.csv: 2 gated (Hermes-3-Llama-3.1-8B, Qwen2-57B-A14B), 3 transient (retried). Items per part 12,032 = 11,994 + the 38 mixed-version ids (`mmlu_pro_mixed_version_items.csv`), as for the parts of record | PARTLY (gated undefined) | MEDIUM (M4) |

## Edits required (insertion brackets)

- **M1** Hygiene, by insertion: "the download and compact-part writing ran before READY (started 2026-10-21 18:01,
  benchzoom 450b86e, D-2026-10-21-2's stream-and-delete), contrary to this draft's 'READY-1 authorises the download';
  the fetcher computed per-model accuracy only (logged; equal in kind to the public `MMLU-PRO Raw`); no item-level
  statistic, meter, WORK or vault reader opens a part before READY-1". The census pins the sha256 of EVERY part (and
  SHA256SUMS) before READY-1; the READY-1 review compares mtimes of parts against the census commit.
- **M2** Replace SELECTION RULE (4) and (6) by the code's rule verbatim: one row per fullname = latest Submission Date
  (empty = earliest; ties bfloat16 > float16 > eval_name); family = `Base Model`, placeholder/empty = own name;
  **cap 8**, the kept = evenly spread `MMLU-PRO Raw` ranks weakest..strongest (`_family_spread`); `Flagged` not tested
  (0 among S8). Pin: sources.py blob 67752ddc, selection CSV sha256 21a5625d7c9b4f9d..., 348 selected. Roster about 325
  less (8). Replace "312" by the census count throughout (C-P1, Support (a), cost).
- **M3** Add C-P5 (sensitivity, no word): C-P1 on the cap-3 subset of S8 (lowest sha256(fullname) per code family;
  335 selected, 312 new), list frozen in the census.
- **M4** Rule (8): a gated or unreachable details dataset after the last launch before the census = missing; the
  failure list is frozen in the census; no launch after the census adds a model.
- **M5** Support (b)-(c): DEFF source = `E:/benchzoom_demo/meter_axis_v1/outcome.json`
  `datasets/mmlu_pro/stats/all_models/L3a-L2`; state it is the 23-model value, roster-dependent (about 2.8 at 325
  models under constant ICC), and that the carried SE 0.0183 stays conservative; [A1] and the post-run re-measure DEFF,
  n_eff and MDE80 on this roster and print them beside C-P1.
- **M6** C-P4: the frozen 7-name list (above) is the registered object; the regex is its derivation.
- **M7** Replace Q1 with D-2026-10-21-3 verbatim ("Allow, as a 4th opening (Recommended)"; limited to this test).

## Commands (all read-only)

```
python -I scratchpad/cap.py    # oll_select_models caps 1/2/3/5/8/inf; draft-literal rule; subset test; regex hits
python -I scratchpad/cap2.py   # families >3 in S8; precision differences (5); Flagged 0; math-tuned list
python -I scratchpad/oc.py     # outcome.json mmlu_pro L3a-L2 deff 1.125713 n_eff 4134.27 se 0.0183072 mde80 0.0703
sha256sum E:/benchzoom_cache/hf/oll_parts_more/selection_cap8_raw0.12.csv   # 21a5625d...
cat failures.csv; grep -c "done (" fetch_more_*.log (89); ls *.parquet | wc -l (89); wc -l mixed_version_items.csv (39 = 38 + header)
```
Own mutants: none (no deciding code exists; registration precedes code).
