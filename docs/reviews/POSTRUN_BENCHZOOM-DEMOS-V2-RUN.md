# POSTRUN review: benchzoom v2 zoom demos (run of ea0c265, README tip f7cb79e) — 2026-10-10

Reviewed: benchzoom `master` 6ea6266..f7cb79e (ea0c265 code/tests, f7cb79e README + two launch-line docstrings), outputs
`E:/benchzoom_demo/{math_v2,mmlu_pro_v2}` and their run logs. Authority: D-2026-10-10-1/-2
(`docs/agents/author_decisions/2026-10-09.md`). Prior reviews cited, not re-derived: POSTRUN_BENCHZOOM-ZOOM-DEMOS.md (F1-F11),
POSTRUN_BENCHZOOM-DEMOS-V2.md (D1-D5), POSTRUN_BENCHZOOM-CROSSFIT-DEPTH.md (C1-C3), READY_BENCHZOOM-CALIB-SCRIPT-V2.md.
Illustrative demos, not registered results: checks 3 (McNemar) and 8 (Support) do not apply. Zero LLM calls, no Ollama,
nothing written in benchzoom or E:/benchzoom_*. Scratch: E:/TaxoArena_tmp/bz_demos_v2run_review/.

## Verdict

- **DEMO NUMBERS: CONFIRMED.** Every deciding number recomputes to the digit from atlas.json and the raw score parquets,
  including an independent re-implementation of the strict read (BH among siblings, SE < s_max, forced subject entry).
- **QwQ-32B: EXCLUDED AND DISCLOSED.** 0 QwQ in the atlas models, profiles.csv, node_spread.csv or file names; the reason is in
  LABEL.txt, summary.json `excluded_models`, every figure caption and the README.
- **F1-F11: CLOSED.** D1: closed (strict read only, crossfit labelled experimental and unused, consistent with D-2026-10-10-1).
- **BLOG: NOT BLOG-READY, one condition (H1).** The quotable `headline` in both summary.json files says the read made
  "0 tests at d1 (0 certified)" and that depth 1 was "never tested", while the same summary has 47 (MATH) and 109 (MMLU)
  depth-1 certifications. My re-implemented read makes 483 and 322 depth-1 BH tests. The depth_histogram legend, printed on
  the published figure, repeats "declared subjects entered untested". The README text itself is correct. M1 is recommended
  before publication; L1-L5 are optional.
- **CODE: MERGEABLE (local).** pytest 272 passed / 4 deselected; ruff and mypy clean; calibration pins unchanged.

## Per-claim table (deciding claims)

| claim (builder) | mine | status | sev |
|---|---|---|---|
| atlas scores = raw parquet (both demos) | max abs diff 0.0, 0 NaN mismatches; MATH 69 x 4,914; MMLU 23 x 11,994 | CONFIRMED | - |
| MATH: 52 certify nothing, 17 certify 47 | own read: {0: 52, 1: 17}; depth 1 47/483, nodes 7/7 | CONFIRMED | - |
| MATH: tau_2 = 0, 0/414 depth-2 certified, depths 3-4 never tested | tau [0, .246, 0, .168, .168]; 414 tests, 0 certified; d3/d4 0 tests | CONFIRMED | - |
| MATH ceiling 41/69 >= .975 (47 >= .95), chance .25, 0 of 41 certified | from parquet 41/47/51/18; errors 23-103; disagree 14-128; ceiling models with a cert 0; options modal 4 | CONFIRMED | - |
| MMLU deepest certified depth 0/1/2 = 2/19/2; 109/322; 3/276 | own read: {0: 2, 1: 19, 2: 2}; d1 109/322 (13/14 nodes); d2 3/276 (3/12) | CONFIRMED | - |
| within-cat unshrunk SD > noise RMS 60/207 (MATH), 66/138 (MMLU); max/mean 1.29/0.36, 0.64/0.17 | own one-step raw offsets: 60/207, 1.290 (Kimi-K2-Thinking, Precalculus)/0.364; 66/138, 0.640 (R1-Distill-7B, business)/0.167 | CONFIRMED (numbers); see M1, L1 | - |
| headline "the read made 0 tests at d1 (0 certified) ... depth(s) [1, 3, 4] never tested" (MATH; MMLU "[1, 4]") | 483 (MATH) and 322 (MMLU) depth-1 BH tests, 47 and 109 certified (`adaptive_read` tests subject children; only ENTRY is forced) | REFUTED | HIGH (H1) |
| MATH tree byte-identical to v1; MMLU same structure, two p-values differ | `cmp` identical; MMLU: node 19 sep_p 8/301 -> 7/301, node 39 reps_done 19 -> 18 (one p-value, one rep count) | PARTLY (wording); cause UNDETERMINED | LOW (L4) |
| pytest 272/4; ruff, mypy clean | 272 passed, 4 deselected (133.7 s); "All checks passed!"; mypy 13 files OK | CONFIRMED | - |
| calibration pins unchanged | LF `git hash-object` = 6ea6266 blob for depth_calibration_v2.py b5094b6b, depth_calibration.py ff3aee1e, atlas 7a0b5c2a, profile 514538f5, crossfit 39bc296e; 0 of the 9 changed files is a pinned file (`grep -c` = 0); working tree clean, so no CRLF rendering differs | CONFIRMED | - |
| runs used ea0c265; f7cb79e docs only | `git diff ea0c265 f7cb79e --stat`: README + 3 and 2 lines of module docstrings (launch lines) | CONFIRMED | - |
| no raw outputs / GPQA text | 0 output-type keys in the v2 dirs; 0 files with "gpqa" in the v2 dirs; 0 data files tracked; the 7 "gpqa" diff lines are all docstrings/README | CONFIRMED | - |
| mmlu_pro_scores.parquet unchanged by the F9 refetch | sha256 49ee92df.. = backup `_bak_pre_f9` | CONFIRMED | - |
| 22/22 mutants killed | own O1-O3 below; O1 shows the tests ENSHRINE H1 | PARTLY | MEDIUM (in H1) |

Own mutants (sandbox `git archive f7cb79e`, TMP redirected; tests/test_demos_v2.py + tests/test_zoom_demo.py, base 34 passed):
- O1 count subject children as tests in `summarize` read_ref (= the H1 correction): 2 FAILED (test_summary_counts_match_recount
  36 vs 24, test_read_refusal_se_boundary 5 vs 3). The tests pin the wrong semantics, and test_demos_v2 L125 hard-codes
  `depth=1 ... tested=0` for the MATH shape. Decisive.
- O2 `raw_above_noise` threshold `sd > rms` -> `sd > 0.8*rms`: killed (1 failed).
- O3 headline within-category rows `n_leaves >= 2` -> `>= 1`: SURVIVED (row count and mean not pinned). Not decisive (descriptive).

## Defects and fixes

- **H1 HIGH (blog).** `read_ref` skips `kind == "subject"` nodes, so `tested` counts ENTRY tests only. v2 reuses it under the
  words "tests at dN (k certified)" and "never tested". The result is self-contradictory: headline[0] reports 47 / 112
  certified offsets at depth 1, and headline[1] reports 0 tests there. The depth_histogram legend "declared subjects
  entered untested" is wrong in the same way: subjects are BH-tested, only their entry is unconditional. The README
  says the headline sentences are the quotable ones. Fix: in `read_by_depth`, count certification tests including
  subjects (483 / 322 at d1), or rename the field "entry tests" and add a depth-1 line ("declared subjects: entered
  without an entry test; 483 tests, 47 certified"). Change the legend to "declared subjects entered regardless of
  their test". Update test_demos_v2 L125-134 and the v1 tests O1 broke. Then re-render (write-once: new dir, e.g.
  `*_v2b`).
- **M1 MEDIUM (unsupported as read).** The README says "the unshrunk leaf offsets are not [small]: their SD exceeds its
  own noise RMS in 60 of 207 ... and 66 of 138". It gives no chance rate. The statistic is a population SD (ddof 0, item
  weights) against the RMS SE, so under no structure it exceeds the RMS SE in a sizeable share of rows. My null
  (y ~ Bernoulli at the fitted category level, same cells, 200 reps): MATH 41.6 rows expected [95% 32-52, max 55];
  MMLU 30.8 [21-39, max 43]. Both observed counts beat the null, so the sentence survives in aggregate. But about 42
  of MATH's 60 rows are expected by chance. Fix: print the null expectation beside each count (or report the excess:
  ~18 and ~35 rows).
- **L1 LOW.** "Per model the unshrunk SD reaches 1.29 logit (MATH-MC)": that row (Kimi-K2-Thinking, Precalculus, a ceiling
  model) has noise RMS 0.959 (ratio 1.35). The max is mostly noise picked from 207 rows. Fix: report the max of SD/RMS,
  or drop the max.
- **L2 LOW (figure).** The sunburst axes title overprints caption lines 3-4 (seen on math_v2 gemini-3.1-pro-preview), so the
  settings line is unreadable there. Fix: `fig.subplots_adjust(top=...)`, or put the caption below the plot.
- **L3 LOW.** The demos write atlas.json with `include_text=True`. MATH ids carry the problem text, so F10's hashing is
  not exercised by the demos. This is acceptable: it is not GPQA and nothing is committed. Before any atlas.json is
  shared, write it with `include_text=False`.
- **L4 LOW.** The MMLU map's separation null is not reproducible across runs (one sep_p, one early-stop rep count),
  and the cause is unknown. Gate decisions are identical. Fix: test the determinism of the null (rerun the map twice
  on the same input) and disclose it if threads cause it.
- **L5 LOW.** F9's metric rows on the cached-parts path are inferred from `LEADERBOARD_METRICS`, not recorded at fetch time.
  The `why` field discloses this honestly. Raw `acc` was verified directly in the v1 review.

## Commands

```
python E:/TaxoArena_tmp/bz_demos_v2run_review/check.py   # parquet vs atlas, bands/ceiling, own strict read per depth, raw leaf SD + 200-rep null
cmp math/tree.csv math_v2/tree.csv ; python (column diff mmlu_pro vs mmlu_pro_v2 tree.csv)   # identical ; sep_p node 19, reps node 39
git diff --name-only 6ea6266 f7cb79e | grep -c -E "atlas.py|profile.py|crossfit.py|irt.py|tree.py|synthetic.py|depth_calibration"  # 0
git hash-object <pinned files> vs git rev-parse 6ea6266:<file>                          # all equal
.venv/Scripts/python -m pytest -q ; ruff check --no-cache . ; mypy src                   # 272 passed/4 desel; clean; clean
git ls-files | grep -ciE '\.(parquet|db|npz|jsonl|png)$|gpqa'                            # 0
grep -rl '"<resps>"|"output"|"messages"|"answer_attribution"|"arguments"' v2 dirs | wc -l ; grep -rli gpqa v2 dirs | wc -l   # 0 ; 0
grep -o QwQ mmlu_pro_v2/{profiles.csv,node_spread.csv,atlas.json,summary.json,LABEL.txt} | wc -l   # 0,0,0,3,1
sha256sum hf/mmlu_pro_scores.parquet hf/_bak_pre_f9/mmlu_pro_scores.parquet             # equal
sandbox mutants O1-O3 (git archive f7cb79e, sed one line each, pytest the two demo test files)   # O1 2F, O2 1F, O3 survived
```
