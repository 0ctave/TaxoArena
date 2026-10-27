# POSTRUN review: benchmark-zoom post figures (benchzoom 5c2063c; post dir docs/drafts/hf/benchmark-zoom/, uncommitted draft)

Reviewer: adversarial-reviewer, 2026-10-10. Zero LLM calls, light CPU. Read-only on every source.

## Verdict: NOT FIGURES-READY

All plotted numbers are CONFIRMED to the digit, the registered and illustrative labels are honest, and no figure shows question text.
Two things block it:
- **F1 (HIGH).** The registered headline figure (fig3) and the pipeline (fig2) cannot be read at blog width.
- **F2 (MEDIUM).** The Figure 5 markdown caption contradicts the v4 image.

FIGURES-READY once F1 and F2 are fixed. F3-F8 are LOW and can be fixed in the same pass.

## Per-claim table (deciding claims)

| # | Claim | Source checked | Result | Severity |
|---|---|---|---|---|
| 1 | fig3 Brier arms A .147595, C .148555, E .146657, D_7 .145645, F_flat .145008, F_bis .146753 | outcome.txt L83 (sha256 fc715e4d..., matches the pin) + ADAPTIVE-PROFILE.json `Brier_arms` | CONFIRMED, digit for digit | - |
| 2 | fig3 (b): D_C +0.000961 [+0.000784, +0.001137]; D_7 -0.001950 [-0.002257, -0.001643]; E -0.000938 [-0.001430, -0.000457]; F_bis -0.000842 [-0.001090, -0.000613]; F_flat -0.002587 [-0.002998, -0.002189] | outcome L84, L88-90, L116; JSON | CONFIRMED, incl. every 95% bound; the selftest asserts the drawn segment ends | - |
| 3 | fig3 (a): point gains C-X 0.002910 / 0.001898 / 0.001802 / 0.003547; uncertified path +0.002925 | subtraction of the L83 values; outcome L137 (s_max 0.20, q none) = JSON `uncertified_path_gain` | CONFIRMED. The only interval drawn in (a) is the strict read's, which is of record | - |
| 4 | fig3 labels: AP2 / AP3 DESCRIPTIVE-ONLY, E descriptive, AP4 "scoreable narrowly", "seen pattern", C-1, D-2026-10-09-1 | outcome L88-90; POSTRUN_ADAPTIVE-PROFILE_run2 C-1 | CONFIRMED. "Weakest finer reader" is the wording POSTRUN_BENCHZOOM-DEMOS-V3_POST-DRAFT L70 prescribed | - |
| 5 | Demo PNGs in figures/ = blog_v4 | sha256 of the 4 PNGs vs E:/benchzoom_demo/blog_v4_SHA256SUMS.txt | CONFIRMED, 4/4 identical | - |
| 6 | depth_support: MATH 47/483, depth 2 not testable 414; MMLU 109/322, 3/276, depth 3 not testable 2 | math_v4 and mmlu_pro_v4 summary.json `read_by_depth`; blog_figures.json | CONFIRMED | - |
| 7 | signal_vs_chance: MATH 60/207 vs 41.0 (30-52); MMLU 66/138 vs 31.2 (22-43), 200 reps | blog_figures.json `chance` (40.955 [30, 52]; 31.17 [21.975, 43]) | CONFIRMED | - |
| 8 | Sunburst titles: Llama-3.3-70B 0.533 / 13; Yi-1.5-34B 0.453 / 0; command-a-reasoning 0.896 / 5; gemini-3.1-pro 0.995 / 0; 41 of 69 models >= 0.975; QwQ-32B excluded | summary.json `accuracy.per_model`, `excluded_models`; profiles.csv certified counts | CONFIRMED. 13 ties with R1-Distill-7B and 5 is a 3+-way tie, as disclosed. All certified cells are at depth 1 | - |
| 9 | Labels honest: in-image "illustrative demo, not a registered result" on all 4 demo PNGs; fig2 "schematic, no data"; fig3 "Registered result (ADAPTIVE-PROFILE)" | visual read of all 6 PNGs | CONFIRMED | - |
| 10 | "Not testable (tau = 0)" correct | tau_per_depth: MATH d2 0.0, MMLU d3 0.0; not_testable 414 / 2 | CONFIRMED. MATH d3/d4 and MMLU d4 say "not tested" although they were not reached (F5) | LOW |
| 11 | No question text in any figure | visual read: ring labels are 3-token cluster keywords ("defendant man tria", "pmatrix mathbf beg") and declared subject names | CONFIRMED | - |
| 12 | Readable at blog width | pixel widths vs a ~720 px column (scale shown) | REFUTED for fig3 (2106 px, x0.34) and fig2 (2076 px, x0.35); PARTLY for depth_support (x0.41) and the sunbursts (x0.48) | HIGH (F1) |
| 13 | article.md references each existing file | `grep -n 'figures/' article.md` (6 refs) vs `ls figures` (8 files) | CONFIRMED for all 6 primary figures. fig2_pipeline.png and fig3_adaptive_profile.svg are alternates and are not referenced | - |
| 14 | Snippet runs | own run: the article's code block, verbatim except `files=` (offline FakeHub, 2 models x 4 BBH subtasks x 120 items) and `.show()` -> `.write_html` | CONFIRMED: SNIPPET OK, every call returned. `query("certified")` came back empty (F7) | LOW |
| 15 | Regression | benchzoom pytest; depth_calibration_v2 --selfcheck; make_figures --selftest; git status | CONFIRMED: 289 passed / 4 deselected; selfcheck OK (criteria 174a86ce, library blobs OK); SELFTEST OK; benchzoom tree clean at 5c2063cc | - |

## Defects and fixes

- **F1 (HIGH, readability).**
  - Measurements at a ~720 px column:
    - fig3 is 12.5 in at 170 dpi, shown at x0.34. Annotations (7 pt) and the in-image caption (6.8 pt) render at about 5.5 px. The y tick labels (8 pt) render at about 6.4 px.
    - fig2 is 15.5 in wide, shown at x0.35. Its body text (7.8 pt) renders at about 6.4 px.
  - Fix fig3: stack the panels vertically, or draw them at figsize about 8 x 7 in. Use at least 10 pt for every annotation and tick label. Move the long caption into the markdown. In the image, keep one line of at least 9 pt: "Registered result (ADAPTIVE-PROFILE). Gain vs benchmark level only (C-1). Declared deviation D-2026-10-09-1".
  - Fix fig2: draw a 2 x 3 grid (or figsize about 9 in) with at least 11 pt body text.
  - depth_support: raise the bar labels and the caption to at least 9 pt.
  - Sunbursts: drop the empty bottom third (about 30% of the height). Fix the overlapping ring labels: "polynomial roots o" sits on "roots polynomial r", and the centre model name sits on the wedge labels. Using "theta" only in the centre would fix the latter.
  - The make_figures selftest must still pass. Re-render the demo figures into a new write-once dir (blog_v5) and re-sum it.
- **F2 (MEDIUM, caption contradicts image).**
  - article.md L339-341 (Figure 5) says: 'The MATH "0 / 414" bar at depth 2 and the MMLU-Pro "0 / 2" bar at depth 3 are not tests'. The v4 image no longer prints "0 / 414" or "0 / 2". It prints "not testable (tau = 0; 414 pairs)" and "(2 pairs)", hatched.
  - Fix: 'The hatched bars (MATH depth 2, 414 pairs; MMLU-Pro depth 3, 2 pairs) are not tests: the fitted spread there is zero.'
- **F3 (LOW, split word).** The fig3 suptitle says "predicts held-out correctness". Write "predicts correctness on the EVAL side" (S3 / rule 12). The pool is content-closed under CK-CLOSE-v2 with a disclosed residual, so "EVAL" is the safe word.
- **F4 (LOW, fig3 panel b).** The shared y axis labels row 1 "Adaptive strict read" while the point plotted there is X = C. The in-plot text crosses the zero line. Fix: give panel (b) its own y labels ("benchmark level C (AP1)", ...), or set `sharey=False`, and put the text left of zero.
- **F5 (LOW, depth_support).** MATH d3/d4 and MMLU d4 are labelled "not tested". No model reached them: tau is non-zero there and all pairs exist. Fix: write "not reached".
- **F6 (LOW, stale comments in article.md).** Some HTML comments still describe the work as undone:
  - L55: "PNG copy owed"
  - L100: "SVG not drawn"
  - L170: "make_figures.py not written"
  - L336: "in-image caption lacks it"
  - L341: "still print 0 / 414"
  - L55, L336, L341, L360 cite blog_v3 paths.
  - Fix: point the comments at blog_v4 and drop the stale clauses before publication.
- **F7 (LOW, snippet usability).** In the fixture run, the 2-model example returned no certified cells even though structure was planted (120 items per subtask). The cause is UNDETERMINED: plausibly SE > s_max 0.20 at this n. A reader copying the snippet may get an empty frame. Fix: add a comment saying the strict read needs many items per cell and several models, and that an empty frame is a valid "nothing certified".
- **F8 (LOW, writer-owned placeholders).** These remain: {{FIG_PIPELINE_ALT}}, {{FIG_AP_ALT}}, {{FIG_AP_CAPTION}}, {{BENCHZOOM_INSTALL}}. Not a figure defect, but publication needs them filled. The figures_plan "Brier per arm" panel was not drawn (declared deviation). The differences panel carries the same information, so it is acceptable.

## Commands

```
sha256sum experiment_results/archv2/adaptive_profile/outcome.txt            # fc715e4d... = pin
grep -n 'BRIER\|^AP[1-4]\|DESCRIPTIVE: Brier\|SENSITIVITY' .../outcome.txt   # L83-90, L116, L137
python -c "...json.load(ADAPTIVE-PROFILE.json)['numbers_of_record']"
cd E:/benchzoom_demo; cat blog_v4_SHA256SUMS.txt; sha256sum <post>/figures/*.png   # 4/4 equal
python: summary.json read_by_depth / tau_per_depth / accuracy.per_model / excluded_models; profiles.csv certified groupby model
python: PIL sizes of figures/*.png -> 2106/2076/1751/1494/1483/1071 px
scratchpad/snip/run_snip.py: article code block extracted by regex, files=FakeHub(...) injected, HF_HUB_OFFLINE=1 -> "SNIPPET OK"
benchzoom/.venv python -m pytest -q   -> 289 passed, 4 deselected
benchzoom/.venv python examples/depth_calibration_v2.py --selfcheck -> criteria 174a86ce OK; library blobs OK
benchzoom/.venv python make_figures.py --selftest -> SELFTEST OK (1 interval in (a), 5 in (b), caption, 4 refusals)
cd benchzoom; git status --short | wc -l -> 0
```
