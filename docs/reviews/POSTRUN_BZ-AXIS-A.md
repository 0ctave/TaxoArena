# POSTRUN review: BZ axis map option A (benchzoom 99308e8 + 09de2d6; TaxoArena axis-a-labels ab9b6f98; E:/benchzoom_demo/axis_v1_A)

Reviewer: adversarial-reviewer, 2026-10-20. Authority: author_decisions/2026-10-20.md D-2026-10-20-2. Zero API calls. I wrote nothing
to E:/benchzoom_demo, the backup or the benchzoom tree (`git status --short | wc -l` = 0 before and after). Outputs are intact:
`sha256sum -c SHA256SUMS.txt | grep -vc ': OK$'` = 0 in axis_v1_A, in axis_v1 and in the backup, and the backup is byte-equal
to the outputs (a diff of the two sha lists = 0 lines).

## Verdict

- **Marks: VALID** (descriptive, as labelled). I recomputed lambda1/lambda2 by my own SVD from the axis_v1 seed-0 pickles and the
  512-d vectors, and took the tie and replicate inputs from the m3 exports, not from the render's columns. MMLU-Pro 16/66 SOLID and
  MATH 3/29 match to the digit, along with every sub-count. The rule was committed before any name existed.
- **Labels: USABLE FOR DISPLAY, WITH CONDITIONS (C1-C3).** The pipeline is sound: prompts carry question text only, all 190
  calls are recorded, the token totals match to the digit, no key leaked, and the tree is unchanged. The names themselves are a
  mixed result. Of 16 nodes I spot-checked, 5 describe their questions and separate them from the sibling, 1 does so partly, and
  10 are wording-only sibling pairs, exact duplicates or topic overclaims. The names must never be shown without the keyword
  column and the mark.
- **Branch axis-a-labels: MERGEABLE.** It fast-forwards from main (0 commits on main since base e40b6e5b). It touches 4 files,
  none of them application.yml, .env, .gitignore or report/. The suite gives 569 tests with 2 failures, which are the known two.
  bootRun's main class resolves to `taxonomy.ApplicationKt`.

## Per-claim table (deciding claims)

| # | claim | my number | status | sev |
|---|---|---|---|---|
| 1 | MMLU-Pro 16/66 SOLID | 66 splits (non-root internal), 16 SOLID; depth 1 5/14; failing: l12<1.45 45, tie WITHIN 13, reps<5 15; median l12 1.345 | CONFIRMED | - |
| 2 | MATH 3/29 SOLID | 29 splits, 3 SOLID; depth 1 1/7; l12 24, tie 7, reps 9; median 1.304 | CONFIRMED | - |
| 3 | l1/l2 equals strict-review spectra.json | own SVD vs A tree.csv lam12: max abs diff 6.9e-15 (mmlu) / 8.4e-15 (math); vs spectra.json r12 95/95 nodes, max 8.4e-15; marks 0 disagreements | CONFIRMED | - |
| 4 | rule committed before names | 99308e8 committed 12:32:18; marked render 12:34:52 (after 09de2d6 12:34:48, render-only change); labeller_input 12:35:03; dry 12:36:30; labels_raw 12:37:40 (math) / 12:38:40 (mmlu) | CONFIRMED | - |
| 5 | tree identical to axis_v1 | the 84/85 common columns of tree.csv are equal frame-wise (`DataFrame.equals`), 66/147 nodes; A adds only lam1/lam2/lam12/mark/mark_fails; labeller_input pickle sha = the seed-0 pickle; leaf membership 11,994/11,994 and 4,914/4,914 equal the pickle's leaves; node n/parent/children 147/147, 66/66 | CONFIRMED | - |
| 6 | prompts carry question text only | 5,072 + 1,441 sample lines: each is an item `question` or a fragment of one (1 + 32 cut at blank lines), 0 unexplained; options of 25+ chars that appear in prompts but in no question: 0; "gpqa": 0; labeller_input text_field = question, all 16,908 match `items.question` | CONFIRMED | - |
| 7 | no API key anywhere | the 84-char key from the root .env (never printed) occurs in 0 files of axis_v1_A, 0 of the backup (logs included), 0 lines of `git log -p main..ab9b6f98`, 0 lines of the benchzoom 0297313..HEAD patches | CONFIRMED | - |
| 8 | 190 calls, 637,086 prompt / 5,761 completion tokens | 132+58 records = labels_raw `calls`; the per-record sums equal the headers: 433,725+203,361 = 637,086; 4,253+1,508 = 5,761; failed attempts 0; labelled 132/132, 58/58 | CONFIRMED | - |
| 9 | transport swap keeps the semantics | same deployment Mistral-Large-3 and api 2024-02-15-preview as application.yml L120/L128/L130; the system message is built exactly as in production (`systemPrompt` + `buildAzureSchemaInstruction`, ArcTaxonomyLLMClient L548-550); 1 distinct system string; temperature omitted on both paths; prompt from the unchanged `generateLabelsPostPass`. Differences: non-streaming, timeout 90 s vs 45 s, its own retry instead of the pacer (no semantic effect) | CONFIRMED | - |
| 10 | suite status | `gradlew test --offline` in the worktree: 569 tests, 2 failed = MrlRoutingTest.testMrlConfigDefaults and TraceEnvelopeUnwrapTest (the known two); FixedTreeLabelRunnerTest 4/4 pass; benchzoom test_axis_marks + test_axis_map + test_execution_graph_sync: 45 passed | CONFIRMED | - |
| 11 | bootRun main class resolves | `gradlew resolveMainClassName --offline` exit 0, build/resolvedMainClassName = taxonomy.ApplicationKt | CONFIRMED | - |
| 12 | names describe the node and separate it from its sibling | 16 nodes: 5 good, 1 partial, 10 flagged (table below) | PARTLY | MEDIUM |

Name spot-check. Term counts are node / sibling, regex over the node's questions.

| node | LLM name (kw) | evidence | read |
|---|---|---|---|
| mmlu 69 / 70 | "Biological Mechanism Explanation and Validation" / "Comparative Functional Biology Explanations" (does/statements; plants) | `plant` 1/233 vs 45/208. The real split is plant vs non-plant and neither name says so | WORDING-ONLY pair (tie WITHIN parent) |
| mmlu 127 / 128 | "Historical Primary Source Contextual / Motive Analysis" | `united states\|america` 43/124 vs 6/112. The split is US vs rest of the world; "contextual" vs "motive" has no support | WORDING-ONLY pair |
| mmlu 17 / 18 | "Applied / Fundamental Physics Problem Solving" | `heat\|lens\|focal\|temperature` 220/655 vs 3/644. The split is thermo+optics vs mechanics+E&M | WORDING-ONLY pair |
| mmlu 132 | "Admissibility of Hearsay in Tort Claims" | `hearsay` 0/98; admissibility/objection/testimony 46/98 vs 1/122; the sample includes defamation, insurance and jury instructions | OVERCLAIM ("hearsay", "tort") |
| mmlu 121 | "Exclusion Criteria in Social Sciences" | EXCEPT/"is not" format 8/152 vs 15/90; the sample is mixed geography, politics and sociology | OVERCLAIM (names a format the node does not have) |
| math 30 / 43 | "Algebraic Equation Solving Techniques" on parent AND child (kw begin align) | `begin{align` 15/288, 15/137: a format keyword, and an identical name on two levels | DUPLICATE |
| math 34 / 56 | "Composite Geometric Region Area Analysis" on parent and child | parent == child identical (2 of 58 MATH names; MMLU-Pro 0) | DUPLICATE (counted with the above) |
| mmlu 60 | "Time Series Econometrics and VAR Modeling" | sample = OLS, acf/pacf, MA(1); strict time-series terms 9/85 vs 0/408 | GOOD topic, "VAR" over-specific |
| mmlu 72 | "Metabolic Pathways and Nutrient Biochemistry" | `metabol\|vitamin\|nutri\|diet` 43/208 vs 12/215 | PARTLY |
| mmlu 97 | "Contract Formation and Breach Conditions" | `contract` 119/177 vs 15/156 | GOOD |
| math 55 | "Conic Section Parameter Extraction" (kw asy unitsize) | sample: foci, parabola, ellipse, conic classification | GOOD (content, not the keyword format) |
| math 65 | "Combinatorics and Probability Fundamentals" | `probab` 20/91 vs 0/110; `how many` 65/91 vs 24/110 | GOOD |
| math 57 | "Integer Side Triangle Area Problems" | `triangle` 108/149 vs 19/107 | GOOD ("integer side" unverified) |

Tally: 16 node names checked. Good: 60, 97, 55, 65, 57. Partly: 72. Flagged: 69, 70, 127, 128, 17, 18, 132, 121, 30, 43.
Every wording-only pair sits under a CONTINUUM REGION parent, as option A predicts. The LLM writes a contrast where the map has a continuum.

## Defects / conditions

- **C1 (MEDIUM, display).** Wording-only sibling pairs read as distinct topics. Fix: always render the `kw:` column beside the LLM
  name. Under a CONTINUUM REGION parent, add a footnote that sibling names describe regions of one continuum, not distinct topics.
  Never show a name alone in a slide or the thesis.
- **C2 (MEDIUM, display).** There are 2 parent==child duplicate names in MATH (nodes 30/43, and the Composite Geometric Region Area
  Analysis pair 34/56). Fix: show the child as "(same as parent)" or relabel only those 2 nodes with the sibling context. That is a paid
  re-call of 2 nodes and the author's choice; otherwise disclose it.
- **C3 (MEDIUM, overclaim).** Nodes 132 and 121 name content the node lacks. Fix: flag them in tree_labelled.txt (for example
  "name not supported: hearsay 0/98"), or rely on C1's keyword column and disclose. A name-coverage readout per node would make
  this a count rather than my spot-check: the share of the node's questions that contain the name's content words, against the
  sibling. It is LLM-free and could reuse gate_name_cov.
- **L1 (LOW).** Two nodes sit on the bar. MMLU-Pro node 52 has l12 1.4485, prints "1.45" and is CONTINUUM. MATH node 10 has
  1.4507, prints "1.45" and is SOLID. Fix: print 3 decimals in tree.txt and tree_labelled.txt.
- **L2 (LOW).** The bar 1.45 was set after the strict review's spectra (median 1.34, p90 1.72) had been seen. The rule is blind to
  the names, not to the lambda distribution. This is already covered by "descriptive, not a registered result". Keep that wording;
  SOLID counts are not evidence.
- **L3 (LOW).** Domain anchors come from a question-to-category map in which the last writer wins. 4 MMLU-Pro question texts carry
  more than 1 category, so an economics node's prompt read "Economics, Math". Cosmetic. Fix: key CategoryFetcher by row, or
  disclose.
- **L4 (LOW, inherited).** SOLID inherits the strict review's H1 and H3: the 90% re-cut does not separate false splits, and the tie
  null is anti-conservative. The lambda1/lambda2 conjunct carries most of the discrimination. The summary line already says "not an
  identified or fresh-data-reproducible split". Keep it on every figure.

Own mutants: none. The marks were recomputed by independent code from separate inputs (SVD on raw vectors, m3 exports), which
proves more than mutating the builder's rule. The builder's 13 mutants were not re-run; the 45 tests pass.

## Pins (LF renderings; the working tree equals the blob, 0 CR bytes)

benchzoom examples/axis_marks.py a49d1f09662189d352a63d611abefba537efd115 (09de2d6 = HEAD 567841c for this path).
TaxoArena ab9b6f98: FixedTreeLabelRunner.kt a08b250562450bdec9d7064d75c73ea9f721cca5; FixedTreeLabelMain.kt
b7cda7eb9667a0ff1e1bdb93e5ab31ae719e7d43; FixedTreeLabelRunnerTest.kt 28509437346ecbffb8402dcb4965c89707aa4aa1.
Outputs: mmlu_pro/tree.csv c11ad481..., labels_raw.json 3ac4e1fe...; math/tree.csv 7fcc1e22..., labels_raw.json 7bd41048...
(SHA256SUMS.txt).

## Commands (scratchpad = C:/Users/octav/AppData/Local/Temp/claude/.../scratchpad/axisA)

```
python axisA/marks.py strict/spectra.json        # own SVD l12 + m3 tie/reps -> counts, lam diffs, membership, pickle sha
python -I axisA/prompts.py ; python -I axisA/p2.py  # sample lines == item questions; option leak; tokens; calls
python -I axisA/spot.py [show]                    # name spot-check term counts + samples
pandas: axis_v1/{ds}/tree.csv[common] .equals(axis_v1_A/{ds}/tree.csv[common])   -> True, diff cols []
grep -rlF "$KEY" axis_v1_A backup | wc -l = 0 ; git log -p main..HEAD | grep -cF "$KEY" = 0
git diff --name-only main...axis-a-labels | grep -c -E '^(config/application.yml|\.env|\.gitignore|report/)' = 0 ; merge-tree clean
gradlew.bat resolveMainClassName --offline (exit 0) ; gradlew.bat test --offline -> XML sum 569 tests / 2 failures / 0 errors
benchzoom .venv: pytest tests/test_axis_marks.py tests/test_axis_map.py tests/test_execution_graph_sync.py -> 45 passed
find axis_v1_A -printf '%T+ %p' (mtimes) ; git log --date=iso (commit times)
```
