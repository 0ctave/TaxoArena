# DELTA review: BZ-AXIS-CONFIRM-MMLU fetch-incident fix (benchzoom 0086e9e..afa554c)

Reviewer: adversarial reviewer, 2026-10-22, TaxoArena HEAD 62ca27c1; benchzoom master afa554c (f44c4e0 code/tests/docs,
afa554c census bracket [C-5]); tree clean (`git status --porcelain --untracked-files=no` = 0 lines). Zero LLM calls. No
HELM prediction / stat / score file, no tinyBenchmarks file, no vault read by me; no HELM object fetched by me (the
not-one-correct count is recomputed from the builder's census OUTPUT, not from HELM). Prior review:
READY1_BZ-AXIS-CONFIRM-MMLU.md (62ca27c1); what it CONFIRMED on untouched code is not re-derived.

Reviewed blobs (afa554c; `git hash-object` = LF of record; working tree CRLF, `--no-filters` beside):
`examples/axis_confirm_mmlu.py` 167e5807 (crlf 25014ca4); `examples/fetch_zoom_data.py` 23e5e8de (crlf d1537076);
`examples/mmlu_confirm_census.py` 04feff1b (crlf 78bbdb3a); `examples/mmlu_confirm_items.py` f57d8d5e (crlf 52eee327);
`src/benchzoom/sources.py` a36a7614 (crlf 9d86c073); `tests/test_axis_confirm_mmlu.py` 09d6eec6 (crlf 7a9c27d1);
`tests/test_fetch_more.py` febb2211 (crlf 15f03d62); `docs/axis_confirm_mmlu_census.md` 950fd98b (crlf ad54c43c).

## Verdict

**CORRECT: the fetch may re-run** (`axis_confirm_mmlu.py fetch --registration <READY1 file>`). **READY-1 stands with no
new commit of the READY1 file**: the gate opens on it as committed (row 8), and nothing in the delta changes what READY-1
authorised (fetch + WORK only; vault needs READY-2). This file is the record that READY-1's authorisation carries to
the blobs above. The single condition is FC1 below (informational, for the fetch operator).

## Per-claim table (deciding claims)

| # | claim | reviewer's number / finding | state | sev |
|---|---|---|---|---|
| 1 | rule "!= 1 correct reference -> excluded for all models" is result-independent, counted from instances.json only | `helm_correct_refs` reads reference `tags` only; census `run_instances` reads id, input text, reference texts/tags; `read_allowed` unchanged by the delta (not in the diff); census output `files_read` = [run_spec.json, instances.json]. The rule never reads a prediction, stat or score; in `helm_run_frame` the score of such an instance is set NaN, not read into any decision | CONFIRMED | - |
| 2 | 4 items (vault 1, WORK 3), ids_sha c8c2edad | own script on `census_correct/instances.json` (sha256 b28eefae = doc): union of per-model `not_one_correct_ids` over roster 79 = 4, ids_sha c8c2edad68c5...; over all 80 = same 4; each item carried by 80/80 models; 4 HELM instances each with 2 correct refs, 0 unjoined. Against the census id lists: vault {international_law/51}, WORK {elementary_mathematics/113, high_school_macroeconomics/183, sociology/197}, 0 in the 83 near-dup drops -> kept vault 5,531 - 1 = **5,530** | CONFIRMED (digit) | - |
| 3 | the re-run census reproduces every other census number | new vs record `census_instances/instances.json` (2a4534fa): every shared top-level key equal except `per_model`, whose only differing fields (80/80 models) are the two NEW fields `not_one_correct_ids`, `not_one_correct`; roster 79 ids_sha 9a2afba1; 79 x 14,042 matched, 0 unmatched; by-order groups equal; E5 (iv) [], E5 (vi) []; jamba 13,259. Corroboration of D6: `answer_agree` = 14,038 for 79/79 in the RECORD census, i.e. the 4 D6 disagreements are exactly these 4 (-1 never equals a cais key) | CONFIRMED | - |
| 4 | census and fetch share `helm_correct_index`; runner refuses on a mismatch | census `run_instances` and `helm_run_frame` both call `benchzoom.sources.helm_correct_index` (diff); `helm_matrix` unions `not_one_correct_rows` over every part into `gone` = dup-excluded U noc, NaN'd for every model, and `excluded_ids` feeds `build_cdata` for HELM AND tinyBenchmarks; `load_real` `_pin("not_one_correct_ids", ...)` under `check`, default True, and both callers (L1083, L1087) use the default. Mutants M1, M2, M5, M6 killed | CONFIRMED | - |
| 5 | fetch exits 1 on any roster failure or 0 parts | `run_helm`: roster model not listed -> failed; per-model exception -> failed; `if failed or not meta: return 1`; `main` returns it, `sys.exit(main())`; `run_fetch` passes `--roster census_instances/instances.json --roster-sha PINS["roster"]` and returns rc != 0 before the tinyBenchmarks fetcher. Tests L808-L880 cover failure, 0 parts, roster-not-listed, empty roster. Mutant M3 killed | CONFIRMED | - |
| 6 | D1-D5 done | D1 `synthetic_refusal` binds the gate dir `calibration_synthetic_<blob[:12]>` + meta `runner_blob` == current blob; the record dir (no suffix) can never satisfy it; a foreign blob refuses ("not run by runner blob ..."). D2 `CLEAN_CODE` adds fetch_zoom_data.py and mmlu_confirm_build.py. D3 `commit_prefix=REGISTRATION_COMMIT` in `ready1_gate` and in the fetcher's `_registration_ok` (803c5b04 still passes the history check alone, so the prefix is what refuses; mutant M4 killed). D4 `GUARD_SUBSTITUTION` constant, written into the vault meta; [A1] disclosure still owed (READY-2 C3). D5 [C-1] bracket | CONFIRMED | - |
| 7 | synthetic gate on runner blob 167e5807 byte-identical to the record | own re-run, 4 BLAS threads, into E:/TaxoArena_tmp/delta_mmlu_fetch/syn: 4 outcome.json `cmp`-identical to the e46fc38 record (a0d7fd1a, 20f6133c, 921dfc15, 5f3d14d4); gate.txt 4bd9ad44 = the builder's, differs from the record d482f304 only by the line "runner blob 167e5807..."; every meta `runner_blob` = 167e5807; `synthetic_refusal(<my out>, runner_blob())` = None | CONFIRMED | - |
| 8 | READY-1 gate still opens on the committed READY1 file | READY1 file: 0 porcelain lines, last commit 62ca27c1; header REGISTRATION-COMMIT f53ec853 = runner `REGISTRATION_COMMIT` = fetcher `MMLU_REGISTRATION_COMMIT`; `ready1_gate(<file>)` None; `_registration_ok(<file>)` True | CONFIRMED | - |
| 9 | full suite passes | benchzoom .venv, OMP/BLAS 1 thread, TMP in sandbox: **792 passed, 1 skipped, 4 deselected** (620.6 s; benchzoom tree still clean, 0 porcelain lines; builder at f44c4e0: 792 passed, 1 skipped, 4 deselected); targeted files 116 passed, 1 skipped (mutant baseline) | CONFIRMED | - |
| 10 | census doc edits insertion-only | `git diff 0086e9e..afa554c --numstat`: census doc 70 ins / 0 del; execution_graph.md 19 / 0. Commit hygiene: 0 of the 10 changed paths is application.yml / .env / .gitignore | CONFIRMED | - |
| 11 | Support after the exclusion | kept vault 5,530: SE 0.0183072 x sqrt(4,654/5,530) = 0.01679, MDE80 0.0645 < 0.10, n_eff 5,530/1.1257 = 4,912; stress 0.0374 / MDE80 0.144: unchanged at 4 d.p. from READY-1 row 10. SCOREABLE stands | CONFIRMED | - |

## Defects / conditions

- **FC1 (LOW, operator)** the incident run left `E:/benchzoom_cache/mmlu_confirm/tinyb/tinybench_mmlu_scores.parquet`
  (written while HELM had 0 parts). The re-run overwrites it atomically (`_write_atomic_parquet`) only if HELM exits 0;
  if HELM fails again the stale file stays and `load_real` would read it. Fix: none needed for the fetch; the WORK-mode
  operator confirms the file's mtime postdates a HELM exit 0 in the log (or deletes it before the re-run).
- **FC2 (LOW)** `helm_matrix` coverage now counts matched pairs (incl. the 4 NaN items) instead of finite scores; the
  E5 (v) threshold 13,902 is a matching threshold, so this is the registered reading, and it matches the census
  `matched` (14,042). No fix; noted so the WORK log's "matched" is not read as "scored".
- Carried unchanged to READY-2: C1 (now mechanically enforced by D1: re-run synthetic at the READY-2 blob), C2, C3
  (+ disclose GUARD_SUBSTITUTION and the 4-item exclusion, vault n 5,530).

## Own mutants (sandbox clone E:/TaxoArena_tmp/delta_mmlu_fetch/mut at afa554c, PYTHONPATH = clone src, verified by `benchzoom.__file__`; tests = test_axis_confirm_mmlu + test_fetch_more, baseline 116 passed 1 skipped)

M1 `gone = excluded | noc` -> `excluded` (noc items stay scored): killed (decisive). M2 `helm_run_frame` keeps the
score of a not-one-correct instance: killed (decisive). M3 `if failed or not meta` -> `if not meta` (roster failure
exits 0): killed (decisive). M4 `ready1_gate` without `commit_prefix`: killed (decisive). M5 census uses its own rule
(first correct ref, diverging from the fetch): killed (decisive). M6 drop the `not_one_correct_ids` pin in `load_real`:
killed (decisive). 6/6 killed; clone restored (`git status --short` 0 lines).

## Commands

```
git -C benchzoom diff 0086e9e..afa554c --numstat; git hash-object [--no-filters] <8 paths>
sha256sum E:/benchzoom_demo/mmlu_confirm/{census_correct/*,census_instances/instances.json,_runlog/fetch.log}
python -I scratchpad/noc.py; python -I scratchpad/noc2.py   # new-vs-record census diff; unions 4/4, c8c2edad; vault 1 / WORK 3
.venv/Scripts/python examples/axis_confirm_mmlu.py synthetic --out E:/TaxoArena_tmp/delta_mmlu_fetch/syn; cmp x4 + gate.txt
python -c "A.ready1_gate(READY1); F._registration_ok(READY1); A.synthetic_refusal(syn, A.runner_blob())"
.venv/Scripts/python -m pytest -q (OMP/BLAS 1 thread, TMP sandbox)     # row 9
python -I scratchpad/mut.py                                             # M1-M6
```
