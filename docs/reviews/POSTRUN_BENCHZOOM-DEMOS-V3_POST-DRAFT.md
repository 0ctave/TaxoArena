# POSTRUN review: benchzoom demos v3 (e149e19) + post draft docs/drafts/hf/benchmark-zoom/article.md (2026-10-10)

Reviewer: adversarial-reviewer. Zero LLM calls, no refit, read-only on E:/benchzoom_demo and every record. benchzoom
working tree clean before and after (`git status --short | wc -l` = 0 both times). The draft is uncommitted (`?? docs/drafts/hf/`).
Prior review: POSTRUN_BENCHZOOM-DEMOS-V2-RUN.md (14d4281a); v2 numbers it CONFIRMED are not re-derived.

## Verdict
- **benchzoom e149e19 (H1, M1, L1-L3): fixes CONFIRMED; MERGEABLE as committed (local master, not pushed).** One new
  HIGH on the same counting path (D2: MATH depth-2 "0 of 414 tests" is a structural zero, not 414 tests).
- **Post draft: NOT READY for publication.** 2 HIGH (D1, D2), 10 MEDIUM (D3-D12). Every registered number matches its
  record to the printed digit; the defects are wording, omitted qualifiers and the demo-figure wiring.

## Per-claim table (deciding claims)
| # | Claim | Own number | Verdict | Sev |
|---|---|---|---|---|
| 1 | H1: d1 tests incl. declared subjects; MATH 483/47, 414/0, d3-4 untested; MMLU 322/109, 276/3, 2/0 | own descent + own BH from atlas.json: MATH {1:483, 2:414} cert {1:47}; MMLU {1:322, 2:276, 3:2} cert {1:109, 2:3}; deepest-certified MATH {0:52, 1:17}, MMLU {0:2, 1:19, 2:2} | CONFIRMED to the digit | - |
| 2 | M1: 60/207 vs 41.0 (30-52, max 57); 66/138 vs 31.2 (22-43, max 46) | own reimplementation of `_raw_leaf_offsets`: 60 / 66 observed; own null, default_rng(20261010), 200 reps: MATH 41.7 [32.0, 53.0] max 64 (2/200 >= 60); MMLU 31.0 [22, 41] max 46 | CONFIRMED within redraw noise; MATH tail reaches 60 (D5) | - |
| 3 | L1: max SD 1.290 (Kimi-K2, Precalculus) RMS 0.959 (1.34); MMLU 0.640, SD/RMS 4.30; max ratio MATH 3.22 | 1.290 / 0.959 / 1.34; 0.640 / 0.149 / 4.30; 3.22 | CONFIRMED | - |
| 4 | L2 caption below; L3 no item text, ids hashed | sunburst/map captions below (math_v3 gemini PNG viewed); v3 atlases 0 non-empty texts, all ids `h:`; v2 atlas still has text (L10) | CONFIRMED | - |
| 5 | Re-render from v2 fits, v2 untouched | v2 atlas/summary sha256 6e5fb3a5 / 17f02c88 / 7c678ab1 / eb905851 = `rerendered_from` | CONFIRMED | - |
| 6 | pytest 283/4 desel., ruff, mypy, `--selfcheck` OK, src/ untouched | 283 passed / 4 deselected; ruff clean; mypy 13 files; selfcheck criteria 174a86ce OK; `git diff --name-only f7cb79e e149e19 \| grep -c ^src/` = 0 of 9 files | CONFIRMED | - |
| 7 | LF pins zoom_demo 84c7ec51, rerender 32dc2f0a, blog_figures 69aae248 | HEAD = working tree = LF rendering for all three | CONFIRMED | - |
| 8 | blog_figures.json numbers | equal to both v3 summary.json (depth rows, chance block); sunburst pairs = most-certified / top-accuracy-with-none (ties: L6) | CONFIRMED | - |
| 9 | Draft registered numbers: AP1, Brier arms, AP2-AP4, E-A, uncertified +0.002925, d*=7, 260/4,104, 0.5485, MDE80 0.000253, second stream, H line, deviation line verbatim | all equal ADAPTIVE-PROFILE.json numbers_of_record / prog L25429-L25439; 0.000961/0.148555 = 0.65% | CONFIRMED | - |
| 10 | SATURATION-IRT, CERT-SPLIT-DIP, NESTING, TREE-CUT, GAP-FIX-CC, HIER-FAIR-BACKOFF, UNION-AF-ROUTE numbers | all equal their results JSON (SAT4, NEFF x6, tau 0.8824 [0.8036, 0.9219] 9/153, MDE80 0.0945; 60/60, 0/300 CP 0.0122, 0/70, 15/15, curve 3/27/30; V90 0.3807-0.6592; D_cut x3; D_R x3; -0.530pp [-0.944, -0.106], MDE80 0.61, HB3 +0.29 [-0.42, +0.99]; -1.15 [-2.19, -0.12], -0.45 [-1.31, +0.41]) | CONFIRMED (wording defects D6-D9) | - |
| 11 | Draft demo numbers vs v3 summary | 47/483, 109/322, 0/414, 3/276, 17/21 models, 52/69, 41/69 >= 0.975, 23-103 errors, QwQ 0.120: equal. Chance column 42 (32-52) / 31 (21-39) is the old reviewer's null, NOT the v3 artefact 41.0 (30-52) / 31.2 (22-43) | PARTLY (D4) | MED |
| 12 | "draft leads with the registered result" | visible text opens with the MMLU-Pro demo, unlabelled except in an HTML comment | REFUTED (D3) | MED |
| 13 | Snippet runs | ran on an offline fixture (FakeHub BBH, 2 models x 600 items; Precomputed vectors in place of the embedder; `.show()` not called): metric_table, Atlas.fit, profile, `to_frame().query("certified")`, plotly Figure, `sensitivity("acc")` (role sensitivity, official acc_norm) all OK; `SentenceTransformerEmbedder()` downloads all-MiniLM-L6-v2 at construction (offline: OSError) | CONFIRMED with L2/L3 | LOW |

## Defects (ranked) and fixes
- **D1 HIGH (headline setting omitted).** TL;DR b1 and L128-129 say profiles predict "answers to unseen questions". The
  registration (prog L25137) declares the "new model on calibrated items" setting: EVAL item difficulties are fitted on the
  other 17 models' answers TO THE EVAL ITEMS. Fix: "...predicted whether it answers a question it was not fitted on (the
  question's difficulty comes from the other 17 models' answers to it)"; same clause at L108-110.
- **D2 HIGH (structural zero printed as tests; H1-class).** MATH tau_2 = 0, so all 6 depth-2 nodes x 69 models have
  d = 0 and SE = 0 exactly (raw offsets up to 1.87 logit); no z is computable, yet `summarize` counts them `refused_bh` and
  the table (L330), depth_support.png ("0 / 414") and README print "0 of 414 tests". MMLU d3 (tau_3 = 0, "0 / 2") is
  the same. The draft then explains rarity by diffuse signal (L353-355), which on MATH is a property of the prior
  estimate. Fix: table and figure "0 of 414: not testable (the depth-2 spread was estimated at 0, so every depth-2
  offset is shrunk to 0)"; in examples/zoom_demo.py count SE == 0 / tau == 0 as its own refusal ("tau = 0") instead of
  refused_bh, with a test (examples only; src and calibration pins untouched).
- **D3 MED.** Hook (L40-44) is the illustrative demo with no visible label, and "a map of 30 small topic cells" hides that
  8 of 14 categories stayed whole (depth-1 leaves hold 7,146 of 11,994 items; 12 depth-2 nodes). Fix: "In an
  illustrative demo on public data (not one of our registered tests)..."; "split 6 of the 14 categories, 30 cells in all".
- **D4 MED.** Chance column (L348-349) and figures_plan FIG_SPREAD use 41.6/30.8 [32-52]/[21-39]; the shipped figure and
  summary say 41.0 (30-52) and 31.2 (22-43). Fix: "about 41 (30 to 52)", "about 31 (22 to 43)", source = v3 summary.json.
- **D5 MED (overclaim).** "more going on below the categories than noise", "the signal there looks real" (L56, L353):
  the null is a Rasch parametric bootstrap with the fit held fixed; excess spread can equally be Rasch misfit
  (discrimination, guessing; the post's own limitation L425). MATH excess is thin (own stream: max 64, 2/200 >= 60).
  Also only split categories enter (MATH 3 of 7, MMLU 6 of 14). Fix: "exceeds what a no-structure Rasch model gives in
  the 3 / 6 categories the map split; this demo cannot tell topic-specific ability from Rasch misfit".
- **D6 MED.** TL;DR b4 "k-means hierarchies and flat k-means did at least as well as the engine's tree" contradicts
  TREE-CUT P5 (tree ahead of bisecting k-means +0.0059/+0.0088/+0.0007 purity, descriptive) quoted at L285. Fix: "flat
  k-means beat the tree on partition quality and in the headline test; a same-shape k-means hierarchy routed no worse
  (descriptive); bisecting k-means was within 0.01 purity of the tree".
- **D7 MED.** Box "Registered predictions that failed" omits FAILED AP P4, HB P1, HB P4, SAT P2, GAP-FIX-CC P6 and
  includes SAT P1, recorded HELD (band [0.86, 0.97] held; modal word KEEPS missed). Fix: list every FAILED prediction of
  the tests the post quotes (or title "Selected ..." and say how selected); SAT P1: "the word we gave 0.70 did not occur;
  tau fell inside our band".
- **D8 MED.** L227-229: H line framed as "inside the official interval"; record C-2 / does_not_show: the SI1 word is not
  scorer-robust (H reads on the KEEPS side). Fix: "under an alternative MATH scorer tau is 0.92, above the bar: the word
  depends on the MATH scorer". Curve "20%: 0.90" is 0.8954, below the bar: print 0.895 (and 0.882 / 0.909 / 0.935).
- **D9 MED.** "Benchmarks saturate differently" + NEFF table: MATH's low NEFF (0.369) is not saturation; under the
  official scorer MATH SAT4 = 0.0000 and official credits 9.6% of cells vs 29.6% under H (prog L25379). Fix: one
  sentence "low NEFF can mean too hard as well as too easy; MATH under the official scorer is the too-hard case
  (H 0.584)"; put the H value in the visible table row.
- **D10 MED (unmeasured property).** Heading "Strict certificates are conservative", L193 "right tool ... claim", L411
  "safe to claim": the record says the rule LOSES and certification COSTS ~0.002 Brier; its false-claim rate on real
  data was never measured, and BH runs within one model's sibling family only (no correction across models, levels,
  4,104 pairs). Fix: heading "The strict rule was the weakest finer reader"; "`certified` = passed the registered
  per-family test (BH q 0.05 among siblings), not a calibrated error rate, not the best predictor".
- **D11 MED (figure wiring).** figures_plan and the draft still block on a re-render that is done, and do not map the v3
  files: FIG_DEPTH says "deepest certified cell per model, mark the 41 ceiling models" but depth_support.png plots
  tests/certified per depth; FIG_HOOK is one sunburst, the output is a pair. sunbursts_MATH-MC.png (gemini-3.1-pro 0.995,
  grey) carries no ceiling line, so grey reads as "no deviation" rather than "unresolvable". Fix: map FIG_DEPTH ->
  depth_support.png (caption rewritten + D2 note), FIG_SPREAD -> signal_vs_chance.png, FIG_HOOK -> sunbursts_MMLU-Pro.png;
  add the ceiling line (and QwQ exclusion to the MMLU pair) to blog_figures.py captions in a new write-once dir.
- **D12 MED.** L418 "closed it negative": PROFILE-TREE-ROBUST / KEY-SUBANCHOR-SCALE are [P-FAM] (2,811 judged
  questions); KEY-SUBANCHOR-SCALE records "prediction NOT shown to fail, closed for TAXONOMY reasons". Fix: drop the
  characterisation; keep only {{AUTHOR_WORDING_PFAM}}.
- **L1** MATH demo embedded "question only" (summary `embedded_text`) vs method step 1 "question and options": say so at L319.
- **L2** Snippet default embedder is all-MiniLM-L6-v2 (downloaded at construction), not the demos' qwen3-embedding: add a comment.
- **L3** UNDETERMINED offline: OLL details repo for "meta-llama/Meta-Llama-3.1-8B-Instruct"; the demo used "meta-llama/Llama-3.1-8B-Instruct": use that id.
- **L4** L296 "there was no difference" -> "no difference was detected (realised MDE80 1.01 points)".
- **L5** L163: add that the refused first attempt had read the EVAL key once (record D-2026-10-09-1 question).
- **L6** Sunburst contrast ties broken by order (MMLU: Llama-3.3-70B = R1-Distill-7B at 13; MATH: 4-way tie at 5): state the tie rule.
- **L7** API/README line pins cite f7cb79e; README changed in e149e19: re-pin.
- **L8** AP3/AP4 rows of the C-1 table lack "confirmatory of a seen pattern" (box mentions it): add to the Status cell.
- **L9** Demo-dir depth_histogram.png: caption still above (L2 applied to sunburst/map only), legend overlaps the d1 bars. Cosmetic.
- **L10** E:/benchzoom_demo/math_v2/atlas.json still holds item text: never share v2 dirs.

## Own mutants (deciding paths; 3, all on a clean tree, reverted with `git checkout --`)
| id | change | result | decisive |
|---|---|---|---|
| X1 | summarize: skip `kind == "subject"` before `tried += 1` (H1 revert) | killed (5 failed) | yes |
| X2 | raw_above_noise_null: null_hi percentile 97.5 -> 95 | killed (1 failed) | yes |
| X3 | rerender_demo: above-noise identity check -> `if False:` | killed (1 failed) | yes |

## Commands (compact)
```
cd Z:/FAC/TUBerlin/benchzoom; git status --short | wc -l   # 0 before/after
.venv/Scripts/python.exe -m pytest -q; -m ruff check .; -m mypy; examples/depth_calibration_v2.py --selfcheck
git diff --name-only f7cb79e e149e19 | grep -c '^src/'      # 0 (of 9)
git rev-parse HEAD:<f>; git hash-object <f>; tr -d '\r' < <f> | git hash-object --stdin
python: own descent over atlas.json tree/offsets (enter kind=='subject'; certify iff se<0.2 and own BH q .05 over siblings with finite se>0)
python: own one-Newton-step leaf offsets (theta+D[cat]-b_lomo; item-weighted SD vs RMS) -> 60/66; own null default_rng(20261010) x200
python: MATH depth-2 nodes 8,9,10,11,14,15: max|d| 0.0, se 0.0..0.0, max|raw| 1.87
python: results JSON numbers_of_record / criteria / predictions for the 8 records; prog sed -n 25429,25439p, 25135,25138p, 25379p
fixture: FakeHub (tests/test_sources.py) BBH 2 models x 3 subtasks x 200; snippet lines verbatim except files= and Precomputed
sha256sum E:/benchzoom_demo/{math,mmlu_pro}_v2/{atlas,summary}.json
```
