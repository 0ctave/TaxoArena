# DELTA review: BZ-AXIS-CONFIRM-MMLU second fetch-incident fix (benchzoom afa554c..751d7bc)

Reviewer: adversarial reviewer, 2026-10-22, TaxoArena HEAD 0e1333c2; benchzoom master 751d7bc (7c6ffb2 code/tests/graph,
751d7bc census bracket [C-6]); benchzoom tree clean (`git status --porcelain --untracked-files=no` = 0 lines). Zero LLM
calls. No HELM prediction / stat / score read, no tinyBenchmarks file, no vault. The 7 fetched parts were opened only for
their `model_name` column (the id read-back check). Prior review DELTA_BZ-AXIS-CONFIRM-MMLU-FETCH.md (0e1333c2): what it
CONFIRMED on untouched code is not re-derived.

Reviewed blobs (751d7bc; `git hash-object` = LF of record = `HEAD:<path>`; working tree CRLF, `--no-filters` beside):
`examples/axis_confirm_mmlu.py` 01e40f15 (crlf d41262e8); `examples/fetch_zoom_data.py` 6681ab0f (crlf 71875016);
`src/benchzoom/sources.py` b82f1811 (crlf 5acfc6fe); `examples/update_graph_manifest.py` add481b0 (crlf 4f111391);
`tests/test_helm_part_names.py` 404c1a33 (crlf e631d049); `docs/axis_confirm_mmlu_census.md` ed7adf51 (crlf bf64641e);
`docs/execution_graph.md` fd151316 (crlf be715d69).

## Verdict

**CORRECT: the fetch may re-run** (`axis_confirm_mmlu.py fetch --registration <READY1 file>`). **READY-1 stands with no
new commit of the READY1 file** (row 6). Conditions: FC3 (operator, LOW). FC1/FC2 of the prior delta carry unchanged.

## Per-claim table (deciding claims)

| # | claim | reviewer's number / finding | state | sev |
|---|---|---|---|---|
| 1 | `helm_part_name` / `helm_part_model` are an exact inverse; all 80 census ids give Windows-legal names | own script over the 80 `per_model` keys of `census_instances/instances.json`: 80/80 `windows_legal_name(name)` True and `helm_part_model(helm_part_name(m)) == m`; 0 case-insensitive name collisions (NTFS is case-insensitive); 5 renamed, exactly the 5 the doc names (nova lite/micro/pro `:` -> `%3A`, text-bison/unicorn `@` -> `%40`); fuzz 20,000 random ids over printable + `éü@:~%`: every accepted name legal and inverted exactly; non-canonical names (`%3a` lower hex, `a%2`, `a:b`, `.parq`, `%2D`, `CON`) all refused | CONFIRMED | - |
| 2 | the 7 parts already fetched keep their names and read back with the right ids | `helm_parts/`: 8 entries, 7 `*.parquet`; `axis_confirm_mmlu.helm_part_files(<real dir>)` = 7 ids, each name == `<id>.parquet`, each id in the census (80) and in the roster (79), each part's `model_name` the matching HELM name (`01-ai_yi-34b` -> `01-ai/yi-34b`, ... `allenai_olmo-7b` -> `allenai/olmo-7b`) | CONFIRMED | - |
| 3 | no other path uses an id as a file name | MMLU-confirm path (`axis_confirm_mmlu`, `fetch_zoom_data.run_helm`, `mmlu_confirm_census`, `mmlu_confirm_items`, `mmlu_confirm_build`, `sources`): every writer grepped (`to_parquet/to_csv/write_text/open(...)/f"..."` paths): only fixed names, `d.name` (source dirs), `calibration_synthetic_<blob>`, `tree.csv`, `mmlu_<rule>_seed<k>.pkl`; `_GcsFiles` caches nothing on disk; `helm_failures.csv` / `helm_models.csv` carry ids as values. Off path: `run_oll` / the cap fetcher use `slug = m.replace("/", "__")` (HF ids, not called by `run_fetch`) -> LOW L1 | CONFIRMED (path) | - |
| 4 | synthetic gate on runner blob 01e40f15 byte-identical to the record; `synthetic_refusal` accepts it | own re-run (4 BLAS threads) into `E:/TaxoArena_tmp/delta_mmlu_fetch2/syn`: SYNTHETIC GATE: PASSED; 4 outcome.json `cmp`-identical to the record `calibration_synthetic/` AND to the builder's `calibration_synthetic_01e40f15f483/` (a0d7fd1a, 20f6133c, 921dfc15, 5f3d14d4); gate.txt 56ae24db = the builder's, differs from the record only by the added line "runner blob 01e40f15..."; 4/4 meta `runner_blob` = 01e40f15f483...; `synthetic_refusal(<mine>, runner_blob())` None, `(<builder dir>, runner_blob())` None; a foreign blob refuses | CONFIRMED | - |
| 5 | full suite passes | benchzoom .venv at 751d7bc, OMP/BLAS 1 thread, TMP in sandbox: **810 passed, 1 skipped, 4 deselected** (638.8 s; = the builder's [C-6] count; 792 + 18 new); benchzoom tree still clean (0 porcelain lines) | CONFIRMED | - |
| 6 | READY-1 still holds | READY1 file: 0 porcelain lines, last commit 62ca27c1; `ready1_gate(<file>)` None, `fetch_zoom_data._registration_ok(<file>)` True; the delta touches no gate, `read_allowed`, PINS or REGISTRATION_COMMIT (diff) | CONFIRMED | - |
| 7 | commit hygiene, record edits insertion-only | 7c6ffb2 6 paths, 751d7bc 1 path (`--name-only | wc -l`); 0 of 7 is application.yml / .env / .gitignore; census doc 22 ins / 0 del; execution_graph 20 / 1 (the one deletion is the code-map row of `helm_correct_index`, line numbers moved by the insertion; manifest hashes refreshed, sync test in suite) | CONFIRMED | - |

## Defects / conditions

- **FC3 (LOW, operator)** the incident stub `helm_parts/amazon_nova-lite-v1` is still in place: 0-byte `:$DATA` plus an
  alternate data stream `0.parquet.tmp` of 3,417,462 bytes (PowerShell `Get-Item -Stream *`). It has no `.parquet`
  suffix, so `helm_part_files` (`glob("*.parquet")`) never sees it and the re-run writes `amazon_nova-lite-v1%3A0.parquet`
  beside it; harmless to the fetch and to `load_real`. [C-6] says the operator moves it aside: do so before the re-run
  (or after it, before WORK), and record it in the fetch log.
- **L1 (LOW, off path)** `run_oll` and the cap-fetcher name parts `m.replace("/", "__")`; an id with `:` would hit the
  same WinError 87. Not on the BZ-AXIS-CONFIRM-MMLU path (HF repo ids carry no `:`). Fix when next touched: reuse
  `quote(..., safe="-_.")` there.
- Carried unchanged to READY-2: C1 (re-run synthetic at the READY-2 blob; D1 enforces it), C2, C3.

## Own mutants (sandbox clone E:/TaxoArena_tmp/delta_mmlu_fetch2/mut at 751d7bc, PYTHONPATH = clone src verified by `benchzoom.__file__`; tests = test_helm_part_names + test_axis_confirm_mmlu + test_fetch_more, baseline 134 passed 1 skipped)

X1 writer keeps `f"{m}.parquet"` (builder M1 replay): killed, 1 failed (decisive). X2 reader validates the name but keys
by `p.stem` (builder M2 variant): killed, 1 failed (decisive). X3 `helm_part_model` canonical check disabled: killed, 6
failed (decisive). 3/3 killed; clone restored (`git status --short` 0 lines). Builder's 16 mutants (13 killed, 3
equivalent, listed in the test file) taken as reported; the equivalences M4/M8/M9 read correct from the code.

## Commands

```
git -C benchzoom diff afa554c..751d7bc [--numstat|--name-only]; git show <c> --name-only --format= | wc -l
git hash-object [--no-filters] <7 paths>; git rev-parse HEAD:<path>
python -I scratchpad/names.py        # rows 1-2: 80 ids, inverse, collisions, renamed 5, fuzz, refusals, 7 parts read back
grep -n "to_parquet|to_csv|write_text|open(|/ f\"" <MMLU-confirm examples + sources>    # row 3
OMP/BLAS=4 .venv/Scripts/python examples/axis_confirm_mmlu.py synthetic --out E:/TaxoArena_tmp/delta_mmlu_fetch2/syn
cmp x4 vs calibration_synthetic/ and calibration_synthetic_01e40f15f483/; sha256sum + diff gate.txt   # row 4
python -c "A.synthetic_refusal(...); A.ready1_gate(READY1); F._registration_ok(READY1)"            # rows 4, 6
OMP/BLAS=1 TMP=E:/TaxoArena_tmp/delta_mmlu_fetch2/tmp .venv/Scripts/python -m pytest -q -p no:cacheprovider  # row 5
powershell Get-Item -LiteralPath <stub> -Stream *                                                    # FC3
python -I E:/TaxoArena_tmp/delta_mmlu_fetch2/mut.py                                                  # X1-X3
```
