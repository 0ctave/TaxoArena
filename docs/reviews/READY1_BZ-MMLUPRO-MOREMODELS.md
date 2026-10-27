REVIEW: READY-1
REGISTRATION: BZ-MMLUPRO-MOREMODELS
REGISTRATION-COMMIT: f53ec853
VERDICT: READY

# READY-1 review (pre-data): BZ-MMLUPRO-MOREMODELS

Reviewer: adversarial reviewer, 2026-10-22, TaxoArena `_as_of 70c674dd`; benchzoom master 9f6182f (= branch
mmlupro-moremodels; tree clean, `git status --porcelain --untracked-files=no` = 0 lines). Zero LLM calls. No accuracy,
gain or item statistic computed by me (score column read for domain {0,1} only). Prior review:
READY_BZ-MMLUPRO-MOREMODELS.md (5109ef9c). Not touched: E:/benchzoom_cache/mmlu_confirm.

Reviewed blobs (benchzoom 9f6182f; `git hash-object` = LF of record; = the census / gate blobs named in the census doc):
`examples/mmlupro_more.py` blob:fc8f5adc; `examples/mmlupro_more_census.py` blob:be4196e5; `tests/test_mmlupro_more.py`
blob:a8def42b; `docs/mmlupro_more_parts_SHA256SUMS.txt` blob:d2a0e1d4 (LF content sha256 4e23857f = E: parts_SHA256SUMS).

## Verdict

**READY** (READY-1): authorises the WORK mode ([A1] re-cut, weak-half freeze, dress rehearsal) on the census roster of
**320** new models only. No vault read: needs READY-2 with SECTION_SHA pinned after [A1] (runner fail-closed, PENDING).

**Ruling on Hermes-3 (reviewer's call): KEEP (343 kept / 320 new), disclosed.** Rule (2) conditions on "a GATED details
dataset". That object did not occur: the Hub's public dataset listing (which lists gated repos) holds no
`open-llm-leaderboard/NousResearch__Hermes-3-Llama-3.1-8B-details`; the only repo is the org-less
`open-llm-leaderboard/Hermes-3-Llama-3.1-8B-details`, `gated=auto`, exactly as the kept parts of record (e.g.
`NousResearch__Hermes-3-Llama-3.1-70B-details` gated=auto). The anonymous API answers 401 for the org-prefixed name and
for a made-up name alike (= not found). So the logged GatedDatasetError was the not-found text ("private or gated repo")
mislabelled. Outcome-blind: the choice reads no value of the part. The literal alternative (342 / 319, ids_sha af0da1af)
is saved in census.json `literal_rule2` (recomputed, equal). Registrar brackets the ruling (D1).

## Per-claim table (deciding claims)

| # | claim | reviewer's number / finding | state | sev |
|---|---|---|---|---|
| 1 | S8 348; 23 cached in S8 (QwQ-32B not); 325 to fetch; 320 new parts; 5 excluded by name | own script (no benchzoom code): selection 21a5625d, S8 348 / 282 families; cached 24, 23 in S8, {Qwen/QwQ-32B} not; `oll_parts` 24 files, 23 in S8 = cached-in-S8; 320 new parts, all map to S8-minus-cached; missing = Qwen2-57B-A14B, dbrx-instruct, Phi-3-small-128k, Phi-3-small-8k, Mixtral-8x22B-Instruct-v0.1 | CONFIRMED | - |
| 2 | kept 343 / new 320, ids_sha f7fd0db5; literal 342 / 319 af0da1af | 343 / 320 f7fd0db5; 342 / 319 af0da1af | CONFIRMED (digit) | - |
| 3 | the 5 exclusions are outcome-blind and real | failures.csv 16 rows; Hub listing: no repo for Qwen2-57B-A14B (only -Instruct) nor dbrx-instruct; Phi-3-small-8k/128k and Mixtral-8x22B repos have 0 `mmlu_pro` paths (recursive tree); no model reached 5 attempts (max 2) | CONFIRMED | LOW (D2: label) |
| 4 | item join 12,032 = 11,994 + 38 mixed on every part, 0 doc_hash diffs | all 343 parts: 12,032 rows, unique ids, item set = the 11,994 of `mmlu_pro_scores.parquet` (49ee92df), extras = the 38 mixed ids exactly (0 of them in the item set), score in {0,1}, doc_hash equal on every item: 0 failures | CONFIRMED | - |
| 5 | part pins | sha256 of 343 parts recomputed = parts_SHA256SUMS (343 lines, 0 mismatches); SUMS 4e23857f, census.json 2dcc243f = runner PINS; roster / cap-3 ids_sha pinned in `read_census` (mutant R3 killed) | CONFIRMED | - |
| 6 | M1 disclosure: parts written after the registration, download began before READY | registration commit 2026-10-21T21:28:52Z: new parts 120 before, **200 after**; 23 of record before; max mtime 2026-10-22T02:13:19Z < census run 02:56Z < census commit 9f6182f 03:14:52Z: none later than the census. Hermes part 02:09:37Z (final launch, after c8673dc) | CONFIRMED; disclosure stands as M1 + [C-4] | - |
| 7 | cap-3 (C-P5) 335 / 312 new / 307 present, ids_sha 417e474c | own lowest-sha256-per-`family` on S8: 335 / 312 / 307 / 417e474c | CONFIRMED (digit) | - |
| 8 | reasoning list: regex gives the frozen 7 on S8; 5 in the new roster | 7 / 0 false positives; 5 in roster; the 2 out (R1-Distill-Qwen-32B, -Qwen-7B) are cached. C-P4 = 315 models | CONFIRMED | - |
| 9 | synthetic gate PASSED on blob fc8f5adc | re-run (4 BLAS threads) into E:/TaxoArena_tmp/ready1_more_review/syn: gate.txt 2811755a, null 53c4d116, planted 0c5adc38 BYTE-IDENTICAL to the record; null C-P1 DEGENERATE g 0 SE 0, planted SUPPORTED g +13.5763 SE 1.7413 | CONFIRMED | LOW (D4) |
| 10 | READY-1 gate tied to f53ec853; work and vault gated first, then the synthetic gate on the current blob | `ready1_refusal` strict header, tracked + unmodified, prefix f53ec853 + `registration_commit_refusal`; `main` checks ready1 then `synthetic_refusal(runner_blob())`; `load_more` re-checks. Mutants R4 (prefix), R5 (synthetic skip) killed. This file passes `ready1_gate` (command below) | CONFIRMED | - |
| 11 | suite | `tests/test_mmlupro_more.py` 69 passed (14.9 s); full suite at 9f6182f, 1 BLAS thread, TMP in sandbox: **879 passed, 1 skipped, 4 deselected** (638 s); benchzoom tree clean after (0 porcelain lines) | CONFIRMED | - |
| 12 | Support at the census n | carried SE 0.0183, MDE80 0.0703 < 0.10: SCOREABLE stands. Constant-ICC transport to 320 models: DEFF 1 + 0.005714 x 319 = 2.82, SE 0.0183 x sqrt(2.82/1.1257 x 23/320) = 0.0078, MDE80 0.030 (carried SE conservative). [A1] re-measures | CONFIRMED | - |

## Own mutants (sandbox copy E:/TaxoArena_tmp/ready1_more_review/mut; test file only)

R1 roster_matrix part-sha check off: killed (decisive). R2 roster_matrix NaN / non-binary check off: killed (decisive).
R3 read_census ids_sha check off: killed (decisive). R4 REGISTRATION-COMMIT prefix check off: killed (decisive).
R5 synthetic_refusal skipped in main: killed (decisive). R6 weak half `<` -> `<=`: killed (decisive). R7 C-P1 subset
all -> cap3: killed (decisive). R8 load_more N_CAP3 count check off: **survived** (not decisive: the cap-3 list is
ids_sha-pinned and a subset of the roster, so the count is implied; D3).

## Defects / conditions

- **D1 (LOW, registrar)** Bracket the Hermes ruling (KEEP, 343 / 320) by insertion, citing this review; the literal
  342 / 319 stays as the census.json alternative, no re-run.
- **D2 (LOW, label only)** Qwen2-57B-A14B and dbrx-instruct are excluded as "(2) gated"; the same mislabel applies (no
  repository under either name). Correct reason: no details repository (no part, rule (3)/(4)). Count unchanged;
  registrar notes it in the same bracket.
- **D3 (LOW)** Add a test for the `load_more` cap-3 count refusal (R8), or drop the redundant check. Not before WORK.
- **D4 (LOW, inherited)** The null fixture is DEGENERATE (tau^2 = 0, g = SE = 0): it cannot produce a false SUPPORTED
  by construction; the gate discriminates only through the planted fixture. Registered as AXIS_FIXTURES unchanged.
- **D5 (MEDIUM, future fetches; not this census)** benchzoom c8673dc `_hub_call` tests `RepositoryNotFoundError` in the
  MRO before gating, but `huggingface_hub.errors.GatedRepoError` SUBCLASSES `RepositoryNotFoundError` (venv 0.26.5): a
  truly gated, unaccepted repo is now reported FileNotFoundError and the org-less fallback is tried. Fix: test
  `GatedRepoError` by name first. Hermes is unaffected (its org-prefixed repo is absent from the public listing).
- **C1** WORK mode only; the vault read needs READY-2, SECTION_SHA, and the [A1] condition-(f) record.

## Commands (all read-only on records; zero LLM calls)

```
S=<scratchpad>/rc.py; .venv/Scripts/python.exe -I $S   # roster 348/23/325/320/5; 343/320 f7fd0db5; 342/319 af0da1af;
   # cap3 335/312/307 417e474c; reasoning 7/5; parts 343 join-fail 0 sha-mismatch 0; new before/after reg 120/200; max mtime 02:13:19Z
git show HEAD:docs/mmlupro_more_parts_SHA256SUMS.txt | sha256sum      # 4e23857f; sha256sum census.json 2dcc243f
git hash-object examples/mmlupro_more.py examples/mmlupro_more_census.py tests/test_mmlupro_more.py   # fc8f5adc be4196e5 a8def42b
curl https://huggingface.co/api/datasets?author=open-llm-leaderboard&search=<name>   # Hermes-3-Llama-3.1-8B: only org-less (auto)
curl https://huggingface.co/api/datasets/open-llm-leaderboard/<repo>/tree/main?recursive=true   # 0 mmlu_pro paths (3 rule-(3) models)
python examples/mmlupro_more.py synthetic --out E:/TaxoArena_tmp/ready1_more_review/syn; sha256sum */gate.txt */*/outcome.json
pytest -q tests/test_mmlupro_more.py   # 69 passed;  mutants R1-R8 via scripted single-line replace in the copy
record dir E:/benchzoom_demo/mmlu_pro_more: 23 files, sha256-of-sha256s 6445777d before and after this review
```
