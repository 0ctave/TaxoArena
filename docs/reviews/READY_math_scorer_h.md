# READY review: math_scorer_h.py (H sensitivity table, D-2026-10-08-5)

Reviewer: adversarial-reviewer, 2026-10-08. Zero judge calls. Read-only on every DB.
Reviewed: branch `worktree-wf_d795fd62-e28-3` tip 36535c68 (parent bb5eb124, ancestry checked),
`tools/analysis/math_scorer_h.py` blob:3ab51e3f (LF; the worktree file is LF, so there is no separate CRLF rendering).
Definition of record: prog L25321 (paragraph "H, THE SENSITIVITY LINE", section L25317-L25327, _as_of bb5eb124);
authority docs/agents/author_decisions/2026-10-08.md D-2026-10-08-5 (5211616a).

## Verdict

**READY** for `--run` from main, after a merge by path. Conditions: none blocking. LOW items L-1..L-3 go to the registrar.

## Deciding claims

| # | Claim (builder) | Mine | Status | Sev |
|---|---|---|---|---|
| 1 | Copied objects equal the pinned sources (10 objects); source pins fe1ce919c29a5ec3 / b22251009ac14ab5; math_fix blob:c44a2618 | Source sha256-lf16 fe1ce919c29a5ec3 (CRLF 38486ef3b7341e49) and b22251009ac14ab5, both equal to the record. math_fix.py in main = blob:c44a2618, last touched 10a3413f (the only commit), so the pilot used the same helper. Leg A passes. | CONFIRMED | - |
| 2 | The implementation equals the definition on the real data | I imported the PINNED SOURCE `math_scorer_analyse.h_score` (not the copy) and scored all 23,832 rows. Builder `build_table` vs source: **0 mismatches** in (H, route). | CONFIRMED | - |
| 3 | Data object: 23,832 MATH rows, 18 models x 1,324, no Llama-3-70B, unique keys | 23,832 rows; 23,832 distinct (qid, model); 18 x 1,324 (check_counts passed); -wal size 0, no -journal | CONFIRMED | - |
| 4 | Official 2,335; H 7,126 (= pilot summary.json) | 2,335 / 7,126; MATH-FIX 7,516 (pilot 7,516); H < official on 0 rows | CONFIRMED to the digit | - |
| 5 | 13 route counts equal the pilot's | 13 routes, sum 23,832 (table below) | CONFIRMED | - |
| 6 | Table sha256-lf16:6b010fa60dde7278 (dry-run) | My own render from the source's h_score, bytes equal to builder's `render_csv`: sha256 6b010fa60dde727816b91196d2cb3045094082c3800fe738adebe21d19eeb1d1 | CONFIRMED | - |
| 7 | Official scorer read is eval_results.is_correct, no overlay (C-7) | QUERY reads `e.is_correct` from eval_results only; no eval_results_mathfix join; mutant O2 (substitute mathfix) killed | CONFIRMED | - |
| 8 | Selftest 5/5 | 5/5 legs pass, run under scratch_dir (entries under E:/TaxoArena_tmp 191 before and after) | CONFIRMED | - |
| 9 | "2 real rows state 11x+6y+5z+86=0" for 2060129 | 1 row by an exact match on a stated candidate after whitespace removal (Qwen2.5-32B, official 0, H 0). The second row may use another spelling. Descriptive only. | PARTLY | LOW |
| 10 | DB not written | size and mtime of multicorpus_cache_v1.db identical before and after my full read | CONFIRMED | - |

Routes (real DB): answer_line:num 1, answer_line:str 39, answer_line:unitprefix 17, boxed:eqn 4, boxed:num 73,
boxed:paren 18, boxed:str 4,504, boxed:unitprefix 14, final:num 1, final:str 110, final:unitprefix 10, imported 2,335, none 16,706.

Per-model accuracy (n = 1,324 each; official = eval_results.is_correct, MF = eval_results_mathfix.is_correct, H):

| model | official | MATH-FIX | H |
|---|---|---|---|
| Llama-3.1-70B-Instruct | 371 (0.280) | 512 (0.387) | 504 (0.381) |
| Falcon3-10B-Instruct | 343 (0.259) | 373 (0.282) | 366 (0.276) |
| Qwen2.5-Math-7B-Instruct | 329 (0.248) | 747 (0.564) | 741 (0.560) |
| Yi-1.5-34B-Chat-16K | 249 (0.188) | 297 (0.224) | 286 (0.216) |
| Mistral-Small-Instruct-2409 | 240 (0.181) | 270 (0.204) | 265 (0.200) |
| Llama-3.2-3B-Instruct | 206 (0.156) | 243 (0.184) | 235 (0.177) |
| Phi-3.5-mini-instruct | 198 (0.150) | 264 (0.199) | 255 (0.193) |
| c4ai-command-r-plus-08-2024 | 146 (0.110) | 171 (0.129) | 165 (0.125) |
| Mixtral-8x7B-Instruct-v0.1 | 108 (0.082) | 133 (0.100) | 124 (0.094) |
| OLMo-2-1124-7B-Instruct | 81 (0.061) | 189 (0.143) | 173 (0.131) |
| Qwen2.5-Coder-7B-Instruct | 45 (0.034) | 500 (0.378) | 489 (0.369) |
| Qwen2.5-72B-Instruct | 16 (0.012) | 773 (0.584) | 765 (0.578) |
| Llama-3.3-70B-Instruct | 3 (0.002) | 626 (0.473) | 612 (0.462) |
| DeepSeek-R1-Distill-Llama-8B | 0 (0.000) | 262 (0.198) | 131 (0.099) |
| DeepSeek-R1-Distill-Qwen-32B | 0 (0.000) | 191 (0.144) | 93 (0.070) |
| Qwen2.5-32B-Instruct | 0 (0.000) | 792 (0.598) | 766 (0.579) |
| Qwen2.5-7B-Instruct | 0 (0.000) | 648 (0.489) | 634 (0.479) |
| internlm2_5-20b-chat | 0 (0.000) | 525 (0.397) | 522 (0.394) |
| total | 2,335 | 7,516 | 7,126 |

Power/Support (check 8): not applicable. This is a per-row input table that decides nothing (record item (4)); no criterion is read from it.

## Own mutants (deciding path = the table bytes and the scorer read)

- O1 `REF_FIX.update({2060129: "1x+..."})` placed AFTER COPY END (an Expr node, invisible to leg A's Assign scan): killed (leg D). Decisive.
- O2 QUERY reads `eval_results_mathfix.is_correct` as the official verdict (scorer substitution): killed, but only by an OperationalError (the leg-E fixture has no mathfix table). Decisive. See L-2.
- O3 sort key (model, qid): killed (leg E sha). Decisive.
Builder's 30 mutants were not re-run (first review; claims 1-8 above are verified independently instead).

## Defects (none blocking)

- L-1 (LOW, registrar). The recorded rule `.replace("1x","x")` makes a correct 11x+6y+5z+86=0 for 2060129 uncreditable. I found at least 1 real row (the builder says 2). The rule also strips a leading "." from the answer line (S25). Both are implemented as recorded, which is correct under C-7. Fix: the registrar discloses this beside the H pin. Any correction is a new definition and needs its own record.
- L-2 (LOW). The leg-E fixture has no `eval_results_mathfix` table, so an overlay substitution is killed by a crash, not by a value assertion. Fix (optional): add a mathfix table with values that differ from is_correct, and assert the official credits.
- L-3 (LOW). `experiment_results/math_scorer_h/` is not git-ignored (`git check-ignore` exit 1). Outputs must stay untracked; commit by path only.

## Commands

```
git hash-object tools/analysis/math_scorer_h.py                      # 3ab51e3f (worktree tip 36535c68)
git hash-object tools/analysis/math_fix.py; git log --oneline -- tools/analysis/math_fix.py   # c44a2618; 10a3413f only
python -c sha256(lf/raw) E:/TaxoArena_tmp/math_audit/math_scorer_{analyse,audit}.py          # fe1ce919c29a5ec3/38486ef3b7341e49; b22251009ac14ab5
powershell -File E:/TaxoArena_tmp/busy.ps1                           # exit 1 before every DB read
python tools/analysis/scratch_dir.py --run -- python tools/analysis/math_scorer_h.py --selftest   # 5/5
python <scratchpad>/rv_h.py <worktree>   # imports E: math_scorer_analyse.h_score (source) + builder module;
   # left-joins eval_results_mathfix (0 missing); per-row compare (0 mismatches); independent CSV render + sha;
   # per-model official/MF/H; DB size+mtime before/after
<scratchpad>/mut/O{1,2,3}.py --selftest under scratch_dir             # rc 1, all three
```

## Run (2026-10-08, after this READY and the merge f4f7e0a0; busy.ps1 exit 1 just before)

`python tools/analysis/math_scorer_h.py --run` from main, script blob:3ab51e3f (sha256-lf16:88b83cb8345eb107; the
working-tree file is LF, so the CRLF rendering is identical). Wrote `experiment_results/math_scorer_h/math_h_table.csv`
(960,786 bytes; 0 CR; 23,833 lines = header + 23,832 rows; 18 models x 1,324 rows by awk count) and `math_h_table.meta.json`.
- **Table sha256-lf 6b010fa60dde727816b91196d2cb3045094082c3800fe738adebe21d19eeb1d1** (sha256-lf16:6b010fa60dde7278),
  equal to the dry-run's and to my independent render. Meta sha256 68b9eef28158241629f889bcdabaf612e72bbd72fdad1f402b19669ce013cc5f.
- Official 2,335, H 7,126 (H beyond official 4,791). The routes are as in the table above. Per-model H in the CSV equals the H column above for all 18 models.
- Backup: E:/TaxoArena_backup_20261009_math_scorer_h_table (SHA256SUMS, `sha256sum -c` OK). The outputs are untracked and not committed.
- Owed by the registrar: the pin of record of this sha, with L-1 disclosed (record item (2), before any consumer --run).
