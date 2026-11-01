# READY review: fresh-cont-select (benchzoom `fresh-cont-select` b546270..a71c79d; c98534d2 F2's per-reader cont selection; prepare only)

Reviewer: adversarial-reviewer, 2026-10-30. Authority: D-2026-10-28-1/-2, D-2026-10-29-1/-2/-3 (BZ-AXIS-CONFIRM-FRESH
drafted, NOT registered; prepare only). The reviewer made zero LLM calls and computed no fresh-item statistic. Read-only
on both repositories except this file. The reviewer's reruns read WORK rows through TAU-CONT-ALL's loaders and wrote only
to `E:/TaxoArena_tmp/review_fcs/`.

Reviewed blobs. All are LF: `git ls-files --eol` shows `i/lf w/lf` for all 4 files and the files hold 0 CR bytes, so no
CRLF rendering exists.
- `examples/fresh_cont_select.py`: `blob:38d1cb6eac6bba71`, sha256-lf16:3176d188e3a7b944, at tip a71c79d. The run of
  record used `blob:3939032f` at 7bbc08d (sha256-lf16:a7a367fd62c6d824, as in the plan's [P1]). The two differ by 11
  docstring lines inserted at L45 and nothing else.
- `tests/test_fresh_cont_select.py`: `blob:f3f4ba43`.
- `examples/fresh_cont_select_mutants.json`: `blob:82e1675e`.
- `docs/fresh-cont-select.md`: `blob:e1bf3909`. The plan fcb7d91 (23:08) touches only this file and precedes the code
  7bbc08d (00:19). Later edits are insertion only: +18 / -0, the [P1] bracket.

## Verdict

- **READY**, for this piece of the pipeline: the library that the FRESH runner will import for every tau^2. It is not a
  generation go, which stays the author's (roster, serving, cap and go are OPEN).
  - Conditions C1-C4 bind the FRESH runner's READY.
  - D1 (MEDIUM) should be fixed in the runner branch or in a delta to this module before the runner's READY. It moves no
    number of record.
- **Merge: MERGEABLE (fast-forward)**, `merge_ok: true`.
  - master is still b546270, and it is an ancestor of the tip.
  - `merge-tree` is clean against `fresh-rule-a` (f40e3ac) and `fresh-math-pipeline-4` (745586b), with 0 overlapping
    paths.
  - The 4 paths are all new (`A`); `src/` has 0 diff lines; no `.py` file outside the branch imports the module (grep
    count 0). The change is inert, and `docs/execution_graph.md` needs no update.
- **Support section:** N/A. This is engineering with no deciding statistic. BZ-AXIS-CONFIRM-FRESH carries its own
  Support section.

## Per-claim table (deciding claims)

| # | claim | reviewer's number / evidence | state | sev |
|---|---|---|---|---|
| 1 | MATH: per-task tau^2 2,350 / 2,350 `==`; summary equal; 188 arrays at max\|diff\| 0.0; fallbacks equal; guard 0 | Own driver `rev_repro.py` at tip a71c79d, whole tree clean (porcelain 0), 3 workers, 889 s. The comparison is the reviewer's own code, with the builder's `compare_part` run beside it. Result: 2350/2350, 25/25 tasks, key-set mismatches 0, arrays 188/188 equal (max 0.0), summary and fallback equal, guard [0] before and [0] after. WORK n = 2,949, 69 models, 16 partitions | CONFIRMED | - |
| 2 | MMLU-Pro: same | Own driver, 2 workers, 999 s: 2350/2350, 188/188 (0.0), summary and fallback equal, guard [0] / [0]. n = 7,197, 23 models | CONFIRMED | - |
| 3 | MMLU: same | Own driver, 3 workers, 3,316 s: 2350/2350, 188/188 (0.0), summary and fallback equal, guard [0, 0] / [0, 0]. n = 8,425, 79 models; at 0: 130; golden point taken: 1,020 | CONFIRMED | - |
| 4 | COUNT: through cont = made, 1,150 = 1,150 (chain 75, control 50, cell 875, field 150); f2 1,200 library-checked 1,200 | On each rerun the ledger shows made cont {cell 875, chain 75, control 50, field 150}, through cont equal, mismatch 0, lib_f2 1200 of f2_made 1200. **Independent "made"**, derived from the reference's own key sets (the `cont:` keys plus `l2c:L2\|L1`, and the `f2:` keys plus the other `l2c:` keys): 1,150 and 1,200, i.e. 46 and 48 per task. This equals `expect_counts(16, 25)`. The reproduction's COUNT is therefore non-vacuous (see D1 for the library default) | CONFIRMED | - |
| 5 | No continuous choice at 0.32 | bound {} on all three reruns (0 of 1,150 each). At 0: MATH 121, MMLU-Pro 144, MMLU 130. Golden point taken: 1,029, 1,006 and 1,020 | CONFIRMED | - |
| 6 | The rule = draft D (prog L25742) and TAU-GRID's run-of-record objects | My AST segments of `Criterion`, `select`, `golden`, `select_cont`, `make_grids` and `NotConverged` are equal in d89d8ea1 and the tip (6/6). Their sha256-16 equal the module's pins. Constants 0.32 / 1e-7 / 200. g4 has 30 points. `meter._select` = first `argmin`, so ties go to the smallest tau^2. The bracket is clipped to [0, 0.32]. The golden point is kept only if strictly lower. The tau-cont-all harness c5ace4e1 is the run-of-record 15c4e95f plus 8 docstring lines | CONFIRMED | - |
| 7 | Reference = TAU-CONT-ALL's run of record | `parts/{math,mmlu_pro,mmlu}.{json,npz}` sha256 equal their SHA256SUMS. SHA256SUMS sha256 c5ee2b4ce39884da, the pin in POSTRUN_TAU-CONT-ALL L14. Clusters and leaves equal this load. 0 files under the reference dir or `E:/benchzoom_cache` are newer than the 01:48 marker (no writes during the reruns) | CONFIRMED | - |
| 8 | Selftest 14/14 | 14 PASS, 0 FAIL, exit 0, 73 s, sandbox | CONFIRMED | - |
| 9 | Mutants 82/82 killed, both controls pass | My own runner `mutrun.py builder`, at most 2 at once: each spec is applied once (exactly one occurrence in the tip blob) to a sandbox copy, with TMP / TEMP / TMPDIR / BZ_SANDBOX redirected; the pool specs (X0p, X48) ran alone. Result: 82 of 82 KILLED, and X0 and X0p pass. None of the 84 logs shows an import, permission or missing-file error. The first failures match the builder's table (X25 ValueError, X48 KeyError (1, 0), X66 FileExistsError, X69 SENTINEL) | CONFIRMED | - |
| 10 | Tests: suite 994 passed, 1 skipped; targeted (slow incl.) 52 | Suite: 994 passed, 1 skipped, 11 deselected, 0 failed (1,073 s); worktree porcelain 0 afterwards. Targeted (`-m ""`, 4 files): 52 passed | CONFIRMED | - |
| 11 | Zero LLM calls; no fresh data | Ollama `server.log` [GIN] lines dated 2026/10/29-30: 175 lines at 04:00 (151 `/api/show`, 15 `/api/tags`, 9 `/api/version`; metadata from other agents), 0 chat / generate / embed (the same grep counts 3,213 such calls on earlier days). The module and test hold 0 matches for requests/urllib/http/socket/openai/ollama/azure/anthropic. The loaders are TAU-CONT-ALL's WORK loaders; there is no fresh-item path | CONFIRMED | - |
| 12 | Every tau^2 through cont, "by a COUNT per reader family" (F2) | Proven on TAU-CONT-ALL's chain with an independent expectation (row 4). The library's default `verify()` cannot see a bypass (D1). The FRESH chain is not built (C1, C2) | PARTLY | MEDIUM |
| 13 | Consistent with the FRESH draft and D-2026-10-29-3 | Draft D's rule, the factor-2 beside regime and the "at the bound" note are implemented as worded. The module has nothing on thinking, extraction, roster or temperature (grep 0), so there is no conflict with D-2026-10-29-3. "Every tau^2" is still the registrar's reading (C4) | CONFIRMED | - |

Scope note. The reproduction compares the adapter with TAU-CONT-ALL's `run_reader`, and both call the same pinned
TAU-GRID functions. It therefore proves that the wrapper is faithful (the sums, kinds, families, ledger and outputs per
context), not that the rule is correct. The rule's correctness rests on S1/S2 (an independent criterion and a dense scan
in the bracket) and on POSTRUN_TAU-GRID / POSTRUN_TAU-CONT-ALL.

## Own mutants (sandbox copies; `mutrun.py own`; control C0 passes)

| id | change | result | decisive |
|---|---|---|---|
| O1 | import-time `check_rule_pins()` removed | SURVIVED (S0 calls it explicitly) | no (D2) |
| O2 | `family_of` keeps primes (`L2'` becomes cell) | SURVIVED | no (D3) |
| O3 | the criterion includes the main (outer-test) context, both regimes | KILLED (library tau refusal, lab2d) | yes |
| O4 | the cont criterion includes the outer-test context (cont only) | KILLED (S2) | yes |
| O5 | the factor-2 beside value one grid step up in cont selections | KILLED (S2) | no |
| O6 | the reproduction's `expect` derived from the ledger itself (vacuous COUNT) | KILLED (S7 COUNT end to end) | yes |
| O7 | f2 taus not compared in (T) | KILLED (S7) | yes |
| O8 | the field library check compares the module with itself | KILLED (S5) | yes |

## Defects

- **D1 (MEDIUM; vacuity).** `Ledger.verify()` with no `expect` is near-tautological.
  - Both counters are incremented inside `step`, so a tau^2 chosen outside `step` appears in neither.
  - Fixture demo `vacuity.py`: two readers went through `step(cont)` and a third was chosen by `meter.step` directly.
    `verify()` prints "all: through cont 2 / made 2 EQUAL" and passes. `verify(expect=…)` built from the reader list
    refuses with "cont field: made 1, expected 2".
  - S6's "bypass" case (`record_made` without `record_cont`) is a state the real path cannot reach.
  - Fix: make `expect` required (refuse on None). Document that it comes from the instrument's reader list, never from
    the ledger (the O6 form).
- **D2 (LOW).** The plan's "REFUSES to import on a change" is not tested (O1 survives).
  - Fix: S0 imports a sandbox copy with one pinned object edited and asserts that the import raises `Refused`.
- **D3 (LOW).** `family_of`'s prime stripping is untested (O2 survives), and any partition reader whose name starts
  with "N" is filed as a field (`NMF|C1` gives field).
  - Fix: add `L2'|L1'` (chain) to S6. List the field readers explicitly (N, N', N512, N512', N_A, N512_A) and refuse
    unknown names.
- **D4 (LOW).** `code_state`'s dirty check is a path list that omits 4 transitive example imports: `axis_marks`,
  `zoom_demo`, `fetch_zoom_data`, `mmlu_confirm_census`.
  - Fix: `git status --porcelain -- src examples docs/fresh-cont-select.md`.
  - The record is unaffected: the reviewer's reruns ran on a whole-tree-clean a71c79d.

## Conditions for the FRESH runner's READY

- **C1.** The COUNT on its run of record must use an `expect` derived from the instrument's reader list: every arm under
  both rules, tau_L1 and tau_L2, and the factor-2 beside chain. The count must equal the number of tau^2 keys in its
  outputs (D1; this is also the builder's own condition).
- **C2.** The cont chain must not take `gw.l2_contexts`' internal factor-2 L1/L2 (`c.eta["L1"/"L2"]`, `tau_ref`) as
  parents. It must re-select L1|L0 and L2|L1 through `step`, as TAU-CONT-ALL's `_task` does. Those library selections
  are S-TAU tau^2 that the COUNT cannot see.
- **C3.** Explicit families via `family_of` (after the D3 fix), not inference from the input.
- **C4.** "Every tau^2" (draft D) stays the registrar's reading (c98534d2 F2). This code does not decide it.

Reviewer's process note. During the targeted tests, the slow selftest's 2-worker pool overlapped the reviewer's 2-worker
MMLU-Pro rerun for about 10 s, so up to 4 worker processes ran. Results are unaffected.

## Commands (scripts in `E:/TaxoArena_tmp/review_fcs/`, outputs `out/`, logs `mutlogs/`)

```
cd benchzoom_wt_fresh-cont-select; git diff --name-status b546270..a71c79d; git diff b546270..a71c79d -- src | wc -l   # 4 A; 0
git ls-files --eol <4 files>; git hash-object <4 files>; git diff -U0 7bbc08d a71c79d | grep '^@@'      # LF; docstring-only delta
git diff --numstat fcb7d91 a71c79d -- docs/fresh-cont-select.md                                      # 18 0
grep -rln fresh_cont_select --include=*.py . | grep -v <own 2 files> | wc -l                         # 0 importers
python pins.py tg_d89d8ea1.py tg_tip.py                                    # 6/6 equal, sha16 = RULE_SOURCE_SHA16
cd E:/benchzoom_demo/followups/tau-cont-all; sha256sum parts/*; sha256sum SHA256SUMS                  # = entries; c5ee2b4c
PYTHONPATH=src python examples/fresh_cont_select.py --selftest  (TMP/TEMP/TMPDIR/BZ_SANDBOX = review_fcs/sand)   # 14 PASS
python rev_repro.py math 3; python rev_repro.py mmlu_pro 2; python rev_repro.py mmlu 3                                 # out/<ds>_review.json
python vacuity.py                                                                                      # D1 demo
MUT_W=2 python mutrun.py own; MUT_W=2 python mutrun.py builder                                         # mutants
pytest -m "" tests/test_{fresh_cont_select,tau_cont_all,tau_grid,execution_graph_sync}.py; pytest tests   # 52; 994/1/11
grep '2026/10/29\|2026/10/30' %LOCALAPPDATA%/Ollama/server.log | grep GIN | awk -F'|' '{print $NF}' | sort | uniq -c
find E:/benchzoom_cache E:/benchzoom_demo/followups/tau-cont-all -newer marker_0148 | wc -l         # 0
git -C benchzoom merge-tree --write-tree fresh-cont-select <fresh-rule-a | fresh-math-pipeline-4>    # clean
```
