# Review: HF post 1 draft v5 (benchmark-zoom/article.md) against the BZ-METER record, 2026-10-11

Reviewer: adversarial-reviewer. Authority: D-2026-10-11-9 (author_decisions/2026-10-09.md). Object: the untracked
`docs/drafts/hf/benchmark-zoom/article.md` (34,109 bytes, 380 lines, mtime 2026-10-11 22:08) and the figures from
`make_meter_figures.py` (LF blob 4c79be88; untracked, so LF = working tree). Record: benchzoom master e1fb080
(clean, `git status --short | wc -l` = 0), registration LF blob a192f65d (= working tree), run of record
`E:/benchzoom_demo/meter_v1` (outcome.json sha256 af1f8045... reproduced), POSTRUN_BZ-METER-v1.md (cae33666).
Zero LLM calls. Nothing under meter_v1 or benchzoom was written.

## Verdict: NOT READY-FOR-AUTHOR (1 HIGH, 5 MEDIUM; all are text fixes). After H1 and M1-M5: READY-FOR-AUTHOR with A1-A4.

The core is right. Every deciding number recomputes to the digit from outcome.json / gate.txt. The state of record
(HARNESS FAILED, every level not measured) is stated correctly and is never softened. No WORK number is promoted.
The defects are one blog-rule breach of the registration, two factual errors about the record, and three places
where the text says more than the source does.

## Per-claim table (deciding claims)

| # | Claim (line) | Result | Mine vs claimed | Sev |
|---|---|---|---|---|
| 1 | State HARNESS FAILED; no null, no real-label read (L34, L46, L185-193) | CONFIRMED | outcome.json `state` "HARNESS FAILED", note "no null and no real-label read ([R7])" | - |
| 2 | MATH harness G -0.0167, SE 0.0075, \|G\|/SE 2.226 / -2.23, n 1,960, 69 models (L31, L35, L164) | CONFIRMED to the digit | -0.016671466 / 0.007490941 = -2.2255; cells 69 x 1960 = 135,240 (comment) | - |
| 3 | MMLU-Pro passed by tau^2 = 0, G = SE = 0, 4,654 items, 4,625 clusters, 107,042 cells (L165, L167) | CONFIRMED | outcome.json; 23 x 4654 = 107,042 | - |
| 4 | "about a sixth" of delta_min (L169) | CONFIRMED (number); wording LOW (L4) | 0.016671 / 0.10 = 0.167 | LOW |
| 5 | Split 2,949 / 7,197; vault 1,965 / 4,797; dropped 5 / 143 at cos >= 0.98; scored 1,960 / 4,654 (L116-118) | CONFIRMED | 4914-1965 = 2949; 11994-4797 = 7197; reg Sections 3, 7.1, 7.2 | - |
| 6 | Synthetic gate table z 6.16 / 7.12 / 5.51 / 6.48, L3t DEGENERATE, unplanted NOT SUPPORTED (L144-147) | CONFIRMED to the digit, in the run of record itself | `meter_v1/calibration_synthetic/gate.txt`, all 8 lines + "PASSED" | - |
| 7 | Verdict rules: 3 SE, > q95, >= 0.10; 10 tests; FWER <= 1.35% (L127-133) | PARTLY | reg Section 5 [R2], [R5] match; NOT SUPPORTED's q95 clause and INCONCLUSIVE omitted (L2); shuffle scope misstated (L3) | LOW |
| 8 | [R17] slope on pure Rasch: holds at 16 models, not at 64 (L86-89) | CONFIRMED | reg L512-L522 (+4.75..+7.44 / -1.82..+0.72) | - |
| 9 | Predictions P4 / P5 (L228-231) | PARTLY | P5 words right ([R16]); P4 MMLU-Pro is DEGENERATE, which reg [R3] says "confirms nothing", not "adds nothing of interest" (L5) | LOW |
| 10 | "The vault has now been opened once for each benchmark" (L198, L324) | REFUTED | POSTRUN_BZ-METER-v1 "Reviewer disclosure": cmd A re-opened the vault matrices once per dataset (harness contrast only) -> opened twice per dataset (M1) | MEDIUM |
| 11 | Pockets paragraph in post 1 (L316-319) | REFUTED vs blog rule | reg Section 9 blog rules: "No region, skill phrase, demand scale or pocket appears in post 1 (post 2)" (H1) | HIGH |
| 12 | Profile figures in the main body (L202-220) | REFUTED vs reg Section 8 | Section 8: bars of a non-SUPPORTED level "move to an appendix labelled 'not supported by the meter'"; the text admits this ("appendix material") yet keeps them in the body (M2) | MEDIUM |
| 13 | "all three [rules] were fixed before the run" (L217-220) | REFUTED for the pair rule | the smallest/largest-of-one-family rule is the figure script's (written after the run, script docstring L31-35); only the declared-order and no-call-out rules are reg Section 8 (M3) | MEDIUM |
| 14 | UNION-AF-ROUTE "MMLU-Pro only", "hand-built text maps", "point the same way" (L233-237) | REFUTED | UNION-AF-ROUTE is the six-source v2 union (5,907 / 5,404, 18 models), an anchor-free algorithmic tree; U3b -1.15pp [-2.19, -0.12] is ROUTING accuracy vs declared labels; TREE-CUT compares the tree with k-means, not with declared labels. Numbers right, framing wrong (M4) | MEDIUM |
| 15 | Fig 2 alt text "smallest ... flatter, largest ... steeper" (L80) | CONFIRMED as fact, REFUTED vs [R17] | v: gemma-3-1b +0.621, 27b -0.348; Qwen2.5-1.5B +0.244, 72B -0.413 (profile_work CSVs). [R17]: "No sentence about a model's sensitivity to difficulty is made from v_j" (M5) | MEDIUM |
| 16 | ADAPTIVE-PROFILE: Brier 0.147595 vs 0.148555, D_C +0.000961 [0.000784, 0.001137], bar 0.0005, MDE80 0.00025, 0.65%, 11,841 / 5,907 / 5,404 / 106,326, C-1 table, +0.002925, 5 failed predictions, d* 7, second read (L245-270) | CONFIRMED | results JSON numbers_of_record + prog L25429-L25439; arm B (Rasch only) is not a finer reader, so "every other finer reader" holds | - |
| 17 | TREE-CUT "about 3 points ... all three content-closed trees" (L235-237) | CONFIRMED | D_cut -0.02976 / -0.02626 / -0.03154, CUT-WORSE 3 of 3 | - |
| 18 | Ledger: no BZ-METER / G-PEAKS row; ADAPTIVE-PROFILE L158 (L16-17) | CONFIRMED | `grep -c -E 'BZ-METER\|G-PEAKS' docs/test_ledger.html` = 0; ADAPTIVE-PROFILE at L158 | - |
| 19 | Snippet runs (L277-296) | CONFIRMED on a fixture, except the network adapter | every line after `from_open_llm_leaderboard` ran under the slope default with 2 models (`from_csv` stand-in, 240 items, offline MiniLM): metric_table, fit, predict_proba(heldout=True) -> Series(240), profile -> empty certified table, plot_sunburst plotly -> Figure. `from_open_llm_leaderboard` (gated, network) NOT run. `examples/synthetic_demo.py` rc 0 (at --null-reps 19) | - |
| 20 | Figures: ladder labelled registered; profiles/slope "exploratory, WORK split"; [R17] label; pin | CONFIRMED | figures viewed; `make_meter_figures.py --selftest` SELFTEST OK; outcome sha matches the pin | - |
| 21 | README facts: 69 EEE / 23 OLL / 2024-06..2025-03; QwQ 0.120 vs 0.10; 41 of 69 >= 0.975; slope default bit-identical off; meter opt-in | CONFIRMED (spot) | README blob 6b21170a, L47-L73, L159-L168, L241-L244 | - |

## Defects (ranked) and exact fixes

- **H1 HIGH: pockets in post 1.** Delete the paragraph "**Density pockets were tried.** ..." (L316-319) with its
  comment. If the author wants it, it goes to post 2 (reg Section 9). The "Post 2" line (L313-314) may stay.
- **M1 MEDIUM: vault opened twice, not once.** L198: replace "The vault has now been opened once for each benchmark."
  with "The vault has now been opened by the run once for each benchmark, and once more by the post-run reviewer, who
  recomputed only the leak check." L324: replace "It has now been opened once per benchmark." with "It has now been
  opened twice per benchmark (the run and the review's recomputation of the leak check)."
- **M2 MEDIUM: Section 8 placement.** Move Figures 3-4 and the L217-220 paragraph into a final section
  "## Appendix: per-model profiles (not supported by the meter; exploratory, WORK split)"; keep one sentence in the
  body pointing to it. Or drop them (author decision already listed).
- **M3 MEDIUM: pair rule not pre-registered.** L217-220: "Two rules shape these figures, both fixed before the run:
  every category and finer cell is shown in the benchmark's own order, never sorted by estimate, and no model is
  singled out as strongest or weakest. The two models shown were chosen after the run by a fixed rule: the smallest
  and largest of one model family." (Disclose too that the MATH family was chosen because its members sit in the
  sub-0.95 subset: script docstring L33-34.)
- **M4 MEDIUM: UNION-AF-ROUTE framing.** Replace L233-237 with: "Two earlier registered tests looked at text-built
  maps. On the six Open LLM Leaderboard benchmarks, cells of an embedding-built tree routed questions to models 1.15
  points worse than the benchmarks' declared labels (95% interval [-2.19, -0.12], descriptive). On MMLU-Pro, the
  programme's tree, cut at each depth, matched subject labels on unseen items about 3 points of purity worse than a
  flat k-means of the same size, on all three content-closed trees." Keep L238. Drop "point the same way" and
  "hand-built".
- **M5 MEDIUM: [R17] in the Fig 2 alt text, and Fig 2 itself.** Alt text: replace "the smallest model ... a flatter
  line and the largest a steeper one, each with a narrow band" with "one line per model, each with a band from its
  interval". Fig 2 is not a Section 8 object, and it draws exactly the reading [R17] bars. The author should decide
  whether to keep it or to replace it with a schematic using illustrative v values (no WORK estimate).
- **L1 LOW: title.** It asks a question the post says it cannot answer, and "14 subjects" fits only MMLU-Pro (A1).
  Example: "We built a meter for how finely a benchmark can be read. Its first run stopped at its own leak check."
- **L2 LOW (L129-131):** "NOT SUPPORTED if the gain is not above its shuffled 95th percentile, or is clearly below the
  minimum; INCONCLUSIVE otherwise."
- **L3 LOW (L127):** "shuffled 200 times (categories across all items; finer labels, leaves and text within category)".
- **L4 LOW (L169):** "smallest gain the meter is meant to detect" -> "smallest gain we decided in advance to care about".
- **L5 LOW (L228-229):** "We expected the tree leaves not to be supported on MATH and not to be measurable on MMLU-Pro
  (the fitting side chose no leaf variance there)."
- **L6 LOW (L124-125):** "averaged over (model, item) cells" -> "averaged over models for each vault item, then over
  items". **L7 LOW (L141):** the second fixture also planted a difficulty slope. **L8 LOW (L174-176):** "That looks
  like mild overfitting; it is not evidence of a leak." **L9 LOW (L31):** alt text "whose 95% interval ends outside
  the grey pass zone" -> "a red point just outside the grey pass zone (plus or minus 2 SE)". **L10 LOW (L47):** the
  slope is "a measurement fix, not a level" (reg Section 5): "its own test was one of the tests that did not run".
- **L11 LOW (comments):** L298 and the source list item 4: the snippet now ran on a fixture (row 19); keep "the
  leaderboard adapter was not run (gated download)".

## Commands (read-only; scratch in the session scratchpad)
```
sha256sum E:/benchzoom_demo/meter_v1/outcome.json; cat outcome.json harness.json calibration_synthetic/gate.txt
python: -0.016671466101615063/0.007490941015157564; 69*1960; 23*4654; 0.016671/0.10; 0.000961/0.148555
benchzoom: git log --oneline -5; git status --short | wc -l (0); git hash-object docs/meter_registration.md README.md
sed -n 46,242p / 403,659p docs/meter_registration.md (Sections 0-5, 7-9, 11, [R17]); README L20-35, L44-75, L84-250
python: results JSONs ADAPTIVE-PROFILE / UNION-AF-ROUTE / TREE-CUT-GRANULARITY (criteria, numbers_of_record); prog L25133-25145, L25428-25440
grep -c -E 'BZ-METER|G-PEAKS' docs/test_ledger.html (0); grep -n ADAPTIVE-PROFILE docs/test_ledger.html (L158)
python: profile_work_{math,mmlu_pro}.csv v / theta of the pairs; L1 intervals crossing 0: MATH 11/14, MMLU-Pro 27/28
snip.py (snippet on make_planted -> from_csv stand-in, HF_HUB_OFFLINE=1); python examples/synthetic_demo.py --out <scratch> --null-reps 19 (rc 0)
git hash-object make_meter_figures.py (4c79be88); python make_meter_figures.py --selftest (SELFTEST OK); figures viewed
```
