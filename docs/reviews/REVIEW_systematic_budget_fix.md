# REVIEW: systematic_budget.py fix (branch systematic-budget-fix: 911776a, 9bc0cf9, bccd1f7), 2026-09-23

adversarial-reviewer. Zero calls, no DB opened (every execution below ran under a Python audit hook that raises on
`sqlite3.connect` and on any `.db` open), no real script run, nothing merged or stashed. Scratch:
`C:\Users\octav\AppData\Local\Temp\claude\Z--FAC-TUBerlin-THESIS-TaxoArena\7c10e5cb-d16b-4a0e-864a-f3a6151d835b\scratchpad\rev\`.

## VERDICT
- **911776a + bccd1f7 together: MERGEABLE-WITH-CONDITIONS** (conditions M1-M3 below; none is a code change to this branch).
- **9bc0cf9: MERGEABLE, still independent.** `git merge-tree --write-tree --merge-base 911776a 3c2f4be 9bc0cf9` -> exit 0 (tree f033c73, 1 file);
  `git merge-tree --write-tree --merge-base 9bc0cf9 911776a bccd1f7` -> exit 0 (tree 09d8e07: 911776a+bccd1f7 without 9bc0cf9 applies clean and keeps the nested `mcnemar_p`).
- 911776a alone (first pass): NOT MERGEABLE (unregistered verdict rule); superseded by bccd1f7.

## Blob pins (LF `git hash-object`; CRLF working-tree rendering beside it)
| object | LF blob | CRLF / on disk |
|---|---|---|
| before = main checkout `tools/analysis/systematic_budget.py` == `3c2f4be:` | 57fefec541ffc72d74197eb5927c21fe32b52332 | df48806979985048a196085e2bd9e81ffddf561b |
| after = `bccd1f7:tools/analysis/systematic_budget.py` | 54ca7b22bf3274ac47da7ec10be948e41aafd50c | 79585a8d25a1d7d94d3530986d412c88d063e0ff |
| `bccd1f7:tools/analysis/calibration_status.py` | bcde544100aa17daf0eb027078ca89e10e5810a2 | |
| `bccd1f7:tools/analysis/unfiltered_adopt.py` (3c2f4be: 54a9fd41f5cae22176ef652dd81b651c80d43dec) | 447126f5484008074577a283461be250f13e367b | |
| file of record `experiment_results/x12_crossdomain/systematic_budget.txt` | 67e34282b7043a63d42e869a74cc4de327d24420 | CRLF blob 6edfc0ef6f46c96d5c6ad6c769648da6705b1f4f; on-disk sha256 c4c26a4d53a0cf80e4e24309cc8286eb07c521c24a27dd28a9981e5a3d3c5bb9, 6,122 B, 2026-09-14 23:05:08 |

## Per condition / claim
| # | item | result | command / script | got vs claimed | sev |
|---|---|---|---|---|---|
| C1 | criterion (1) prints FRAMEWORK L101's word, never "MET" | **CONFIRMED** | `branches_v3.py` on the bccd1f7 blob, both `--edges` values: 1 vs 1.27, 6 vs 1.27, 3 vs 1.27 -> `UNDETERMINED (nominal < 3)`; 12 vs 5.00 -> `UNDETERMINED (power: ... P = 0.005)`; 12 vs 10.00 -> `NOT DETECTABLY MISCALIBRATED (Poisson P = 0.303)`; 20 vs 10.00 -> `MISCALIBRATED (Poisson P = 0.003)`; EMPTY called set -> `UNDETERMINED (nominal < 3)`, "0(0) of 0 called vs 0.00 nominal = -". Lines containing " MET" (MISCALIBRATED excluded): 0 of 14 runs; "PASS in aggregate" in output: 0 of 14. `git show bccd1f7:tools/analysis/systematic_budget.py` grep for `"MET`, `MET"`, ` MET `, `NOT MET`, `p_pois`: 0 hits. The only verdict source is `status_word(lo_nom, lo_wrong)` at L352. | all four L101 words + empty case, as claimed | - |
| C2 | wrong(established) on the line | **CONFIRMED** | L348-355: `established([wrong edges of lo_called], K, anchor_qs)` via the module's `mcnemar_edge`; fixture with half the called wrong edges marked established prints 1(1), 3(2), 6(3), 12(6), 20(10). The x12 figure 3(2) is NOT reproduced here (no DB); the real-data run checks it. | as claimed | - |
| C3 | harness unfiltered call works; branches exercised; re-pin | **CONFIRMED** | `rev_harness3.py` (engine-coder's harness3.py under the audit hook; `sb_v3.py` == 54ca7b2, `sb_old.py` == 57fefec): old 8db1c079cd328793, new **8c55eea94202ffda**, 1 hunk `@@ -32 +32,7 @@`, 101 of 102 old lines identical; fixture 915 all / 872 filtered; unfiltered run completes, 98 lines, heading "915 unfiltered edges". Four words covered by `branches_v3.py` above. `sb_realdiff.py` after-pin re-pinned to 54ca7b2 and now asserts `calibration_status` resolves in the worktree with blob bcde544 (wrapper sha256 0bcbebfa070442c6...). | reproduces to the digit | - |
| N1 | status_word moved verbatim | **CONFIRMED** | `3c2f4be:unfiltered_adopt.py` L151-157 vs `calibration_status.status_word`: source text identical, `ast.dump` identical; grid of 840 (nominal incl. 2.9999999 / 3.0 / 8.99 / 9.0 / 9.0000001, observed 0-59): 0 differ, all 4 words produced. | as claimed | - |
| N2 | unfiltered_adopt output byte-identical before/after | **CONFIRMED (stubbed)** | `ua_run.py A|B {0,1}`: dir A = 3c2f4be unfiltered_adopt + systematic_budget; dir B = the three bccd1f7 files; `load_edges` stubbed with a 14-anchor fixture, `CACHE` redirected to a tmp dir (hook refuses any real `.pkl`), BOOT_REPS 40 on both, `elapsed` line masked. `cmp`: seed 0 22b4458e406626bd == 22b4458e406626bd (104 lines); seed 1 865b36f90fbaa793 == 865b36f90fbaa793 (107 lines). The L376 `.split(" (")[0]` path executed. Only the nominal < 3 branch was reached at the two call sites; the other three are covered by N1 on the identical function. | byte-identical | - |
| N3 | no circular import | **CONFIRMED** | AST top level of `calibration_status.py`: the only import is `from scipy.stats import poisson`. | - | - |
| N4 | "the rule has one home" | **PARTLY** | `git grep -n "def status_word" bccd1f7 -- tools`: 3 definitions. `cert_corpus.py:260` (different strings, `poisson.sf`) and `frontier_fit.py:157` (emits "DETECTABLY MISCALIBRATED"; boundary `p < 0.05`, so P == 0.05 exactly goes the other way from L101's "> 0.05"). Pre-existing, disclosed in the commit message, not introduced here. | 1 home of 3 | LOW (registrar) |
| W1 | wording "can no longer be printed" | **CONFIRMED, landed** | bccd1f7 docstring L26 | - | - |
| W2 | wording "before any DB is opened" | **CONFIRMED, landed** | bccd1f7 L477 comment | - | - |
| R1 | --edges refusal before any DB; bogus value rejected | **CONFIRMED (re-executed on bccd1f7)** | `branches_v3.py`: argv [] -> SystemExit(str), pool_guard calls 0, non-.py files opened []; `--edges bogus` -> exit 2 | - | - |
| R2 | 9bc0cf9 McNemar de-dup inert | **CONFIRMED** (first pass) | `dedup.py`: same statements, same order; 400 random inputs (56 with n > 1024), 0 mismatches | - | - |

## Residual defects (none blocks the code merge)
- **D1 MEDIUM (registrar).** `unfiltered_adopt.py` L362-368 (bccd1f7 numbering) scores UNFILTERED-ADOPT (d) by the substring `for e in all_edges if e["anchor"] != A_`; bccd1f7's systematic_budget.py contains it 0 times (`grep -c`). Executed: the dir-B run prints "(d) ... checked on the file as it stands: absent" -> NOT MET, which is FALSE once `--edges unfiltered` exists. The record must say (d) is scored by re-reading the `--edges unfiltered` output against 646 / 3(2) / 1.28 / 70.2% (judge_v2_program L3692), not by this grep.
- **D2 MEDIUM (record).** Side files `x12_crossdomain/grok_calib_systematic_budget.txt` and `judge_wiring/board_systematic_budget.txt` still print "PASS in aggregate" and will change their criterion-(1) block on any re-run of `grok_calib.item26_criteria` (callers grok_calib.py:413, judge_wiring.py:965).
- **D3 LOW.** The DESCRIPTIVE uncalled-edges line prints a raw wrong count without its established count (CONTEXT section 3).
- **D4 MEDIUM (pre-existing, not this branch).** `stack_judge.open_cache()` opens the x12 verdict cache read-write and commits a `CREATE TABLE IF NOT EXISTS`; the real-data wrapper stamps the cache before and after.
- **N4** above (three `status_word` definitions).

## Conditions for the merge (M1-M3)
- **M1.** The registrar records D1 and D2 before any re-run of `unfiltered_adopt.py`, `grok_calib.py` analyze or `judge_wiring.py --analyze-board`.
- **M2.** No file of record is regenerated by the new code until the real-data before/after below passes (1 hunk, criterion (1) only; file-of-record sha256 unchanged; the x12 line reads `UNDETERMINED (nominal < 3)` with `3(2) of 663 called vs 1.27 nominal`).
- **M3.** `--edges unfiltered` runs only as UNFILTERED-ADOPT criterion (d), registered, never as a side effect (FRAMEWORK L358; judge_v2_program L3692 "(d) pending Block 4").

## Real-data procedure (next rule-7 window; NOT run)
No `git stash` (`refs/stash` is shared across worktrees). Wrapper `scratchpad\rev\sb_realdiff.py`:
- asserts the source blob (before 57fefec from the MAIN checkout; after 54ca7b2 from the worktree) and the file-of-record sha256 c4c26a4d...;
- loads every dependency from the main checkout (asserts none resolves under `.claude`); for "after" asserts `calibration_status` is the worktree's, blob bcde544;
- sets `OUT` and `OUT_UNFILTERED` to scratchpad paths BEFORE `main`; runs `main()` / `main("filtered")`; captures stderr (the ACTIVE EDGE SET banner) beside the output;
- re-asserts the file of record and the absence of `systematic_budget_unfiltered.txt`; stamps the verdict cache before and after.

```
python <scratchpad>\rev\sb_realdiff.py before
python <scratchpad>\rev\sb_realdiff.py after
python <scratchpad>\rev\sb_realdiff.py compare     # no DB; requires exactly one replace hunk at the criterion-(1) line
```
Expected after-side: 891 edges, b0 -3.2326 / b1 +3.3133; LOAO 663 called, 3(2) wrong, nominal 1.27, `UNDETERMINED (nominal < 3)`; descriptive 48.7 vs 44 over 891, 228 uncalled.
