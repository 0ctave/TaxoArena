# POSTRUN review: benchzoom EEE adapter + zoom demos (MATH-MC, MMLU-Pro)

Reviewer: adversarial-reviewer, 2026-10-10. Read-only on benchzoom master d872d24 (on 42698d2, on d7dfb51). Authority:
D-2026-10-09-4 (`docs/agents/author_decisions/2026-10-09.md` L18-19). These are illustrative demos, not registered
results, so there is no criterion, Support section or McNemar step to check (checks 3 and 8 do not apply). Scratch:
E:/TaxoArena_tmp/bz_demo_review (eee_check.py, thr.py, oll_check.py, oll_hash.py, oll_prompt.py, atlas_check.py).

## Verdict
- **CODE: MERGEABLE** (local only). pytest 167 passed / 4 deselected; ruff and mypy clean; working tree clean.
  The two commits touch exactly 11 code/doc/test files (`git diff --name-only d7dfb51 d872d24 | wc -l` = 11) and
  no data.
- **DEMO NUMBERS: VALID AS COMPUTED.** Every summary.json number I checked recomputes from atlas.json and profiles.csv
  to the digit, and the per-model accuracies recompute exactly from the raw downloads.
- **REPORT / README / FIGURES: NOT BLOG-READY.** Two descriptive sentences are refuted (F1, F2), one count is wrong
  (F4), the depth-histogram label misleads (F3), and one artefact model drives the MMLU-Pro "differ most" panel (F5).
  Conditions for blog use: fix F1-F6.

## Deciding claims
| claim | builder | mine | status | sev |
|---|---|---|---|---|
| EEE per-model acc, 3 models, from raw *_samples.jsonl | Llama-3.2-1B 0.331, gemini-3.1-pro 0.995 | 1626/4914=0.330891, 4891/4914=0.995319, gpt-oss-20b 4859/4914=0.988807; parquet equal to 1e-12 | CONFIRMED | - |
| EEE common set | 69 x 4,914, nothing dropped | 69 files, 1 distinct sample_id set of 4,914; 0 null is_correct | CONFIRMED | - |
| mean(is_correct) = reported acc | <=1.1e-16 | max_abs_diff_reported 1.11e-16 | CONFIRMED | - |
| OLL MMLU-Pro acc, 3 models, from raw samples (field `acc`) | parquet | Qwen2.5-32B 0.566533, QwQ-32B 0.119727, gemma-2-9b 0.387694 on 11,994; max abs diff to parquet 0.0 | CONFIRMED | - |
| 38 mixed-version items dropped | 24 x 11,994 | 0 of the 38 in parquet; doc_hash on those items splits the 24 runs into 4 vintages (2024-06, 08, 09-10, 2024-12..2025-03) | CONFIRMED | - |
| summary tree / tau / cert-per-depth / read refusals (both demos) | as reported | identical from atlas.json + profiles.csv | CONFIRMED | - |
| per-category accuracy, sd_ability, node spread | MATH ~2.4, MMLU 0.64-1.10 | MATH 2.359-2.488, MMLU 0.642-1.103; accuracy diff 0.0; spread diff 0.0 | CONFIRMED | - |
| "47 of 69 models >= 0.975" | 47 | **41** (47 is the count at >= 0.95; 51 >= 0.90; 18 < 0.90 confirmed) | REFUTED | MEDIUM |
| "tau = 0 at depth 2, so every below-subject offset shrank to zero" (README L56-57) | - | tau = [0, 0.246, **0**, **0.168, 0.168**]; depths 3-4 were never tested (tested = 0); per-model leaf_sd up to 0.163 | REFUTED | HIGH |
| "within a category the spread across sub-cells per model is at most 0.064, below its noise 0.085-0.125" | 0.064 | 0.064 is the max over categories of the mean across models. The per-model max is 0.163 (MATH, Qwen3.5-0.8B, Intermediate Algebra) and 0.189 (MMLU, R1-Distill-7B, business); leaf_sd > leaf_se_rms in 49 (MATH) and 38 (MMLU) (model, category) rows | REFUTED | HIGH |
| "every model's read stops at the subject" / "22 of 24 stop at the category" | 69/69; 22/24 | 52 of 69 MATH models and 2 of 24 MMLU models have **no** certified node. All 47 MATH certifications fall on 17 models, all with accuracy < 0.95; 0 of the 41 models at >= 0.975 | PARTLY (true of `stop_depth`, misleading as English) | HIGH |
| no raw outputs or GPQA text in artefacts | none | 0 keys resps/output/messages/arguments/answer_attribution in E:/benchzoom_demo; 0 "gpqa" hits in outputs or cache CSVs | CONFIRMED | - |
| every figure labelled as a demo | yes | write_demo refuses a title without DEMO; spot-checked math depth_histogram, gemini sunburst and mmlu differ_most | CONFIRMED (spot check) | - |

## Defects (ranked) and fixes
- **F1 HIGH.** README L56-57 and the hand-back say the depth-2 tau = 0 shrank *every* below-subject offset to zero. It
  did not: tau_3 = tau_4 = 0.168. The top-down read stops at depth 2 and never tests depths 3-4. Fix: "tau_2 = 0,
  so the read stopped at depth 2; depths 3-4 (tau 0.17) were never tested".
- **F2 HIGH.** The within-category spread sentence reports a mean over models as a per-model bound. It is also
  circular: leaf_sd is computed on SHRUNK offsets and compared with unshrunk SEs, so shrinkage alone makes it small.
  Fix: drop the sentence, or report per (model, category) with raw offsets against their SEs (49 / 38 rows exceed).
- **F3 HIGH (figure).** The right panel of depth_histogram.png ("depth the certified read stops") puts all
  339,066 MATH (model, item) pairs at depth 1. But 52 of 69 models certify nothing: they "enter" the declared subjects
  by construction (enter_subjects). The same holds for "read stops at the subject for all 69". Fix: plot
  "certified depth" (0 = nothing certified) separately from entered-uncertified, and reword both summaries.
- **F4 MEDIUM.** "47/69 >= 0.975" should be 41/69. It appears in README L58, in the 42698d2 message and in both
  hand-backs. The causal sentence "the zoom refuses to resolve the frontier below the subject" understates the
  problem: the frontier gets no certification even AT the subject (0 of 41).
- **F5 MEDIUM (blog).** QwQ-32B is an artefact run. It is the only model whose prompt ends in `<think>\n`; its
  log-likelihood argmax is option index 1 or 9 on 1,961 of the first 2,000 items; its accuracy 0.120 is about chance
  (0.10). It is the leftmost and strongest column of differ_most.png. Without it the node spread falls: biology
  0.323->0.188, physics 0.241->0.120, math 0.317->0.206, law 0.257->0.168, and the top-15 ranking changes. Fix: drop
  QwQ from the MMLU-Pro demo (refit) or exclude it from sunburst picks and the panel, with the reason printed.
- **F6 MEDIUM (blog).** Run settings differ across models and no figure says so.
  - MATH: gpt-oss-120b ran at low reasoning effort (0.975) and gpt-oss-20b at high (0.989), so the size order is
    inverted. max_tokens is 8192 for 4 models, 16384 for 14 and unset for 51. Platforms: sglang 55, vllm 7,
    openrouter 7.
  - MMLU-Pro: each model runs with its own chat template and system prompt, and the scoring is 5-shot
    log-likelihood, which handicaps reasoning models. Runs span 2024-06 to 2025-03.
  - Fix: one caption line, "scores as run by each source harness; settings differ by model". Pick a single setting
    for gpt-oss, or show both.
- **F7 MEDIUM (blog).** MATH-MC is 4-option multiple choice (4,884 of 4,914 items have 4 options; chance 0.25).
  Llama-3.2-1B (0.331) is near the floor. The 41 models at >= 0.975 make 23-103 errors each and disagree pairwise
  on 14-128 items. The "frontier example" therefore cannot show frontier granularity. This bears on the author's
  "enough granularity" wish: MATH-MC gives it only for the 18 models below 0.90.
- **F8 LOW.** differ_most.png orders rows by the raw method-of-moments spread but colours them by the SHRUNK offset.
  Rows 39 and 40 (depth 4, s = 0.25 / 0.22) show near-blank because tau_3 = 0. Fix: colour by raw offset, or order
  by sd_d.
- **F9 LOW.** `mmlu_pro_metrics.csv`, listed in FILES, does not exist: `ls E:/benchzoom_cache/hf/*.csv` shows 2
  files, because `metric_rows` is empty on the cached-parts path. The metric provenance of the OLL table (`acc`) is
  therefore unrecorded. I verified the field directly. Fix: always write the metric row.
- **F10 LOW.** EEE math-mc sample_ids embed the problem text (`math_mc_level1:<problem>`, median 157 chars), so
  `to_json(include_text=False)` still publishes the text through the ids. GPQA is covered: the guard matches
  task = "gpqa-diamond". The hazard applies to other licensed sets. Fix: hash ids when include_text=False.
- **F11 LOW.** from_eee sets `subject = evaluation_name`, which for math-mc is the difficulty "Level 1-5", not a
  subject. The demo overrides it by joining hendrycks_math. Fix: say so in the docstring and README.

## Commands (all read-only; outputs in scratch)
```
python E:/TaxoArena_tmp/bz_demo_review/eee_check.py     # raw jsonl -> acc per model, id sets, nulls, run settings
python E:/TaxoArena_tmp/bz_demo_review/thr.py           # >=0.975 = 41, >=0.95 = 47; top-model error and disagreement counts
python E:/TaxoArena_tmp/bz_demo_review/oll_check.py     # raw OLL samples -> acc on 11,994 vs parquet (maxdiff 0); QwQ argmax
python E:/TaxoArena_tmp/bz_demo_review/oll_hash.py      # doc_hash vintages on the 38 mixed items
python E:/TaxoArena_tmp/bz_demo_review/oll_prompt.py    # per-model prompt hash/template; <think> suffix only QwQ
python E:/TaxoArena_tmp/bz_demo_review/atlas_check.py   # summary.json vs atlas.json/profiles.csv; leaf_sd per model
grep -o '"[a-z_]*resps[a-z_]*"\|"output"\|"messages"\|"answer_attribution"\|"arguments"' -r E:/benchzoom_demo | wc -l  # 0
cd Z:/FAC/TUBerlin/benchzoom && .venv/Scripts/pytest.exe -q -p no:cacheprovider   # 167 passed, 4 deselected
.venv/Scripts/ruff.exe check --no-cache . ; .venv/Scripts/mypy.exe --cache-dir E:/... src  # clean; git status --short | wc -l = 0
```
