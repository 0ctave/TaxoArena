# POSTRUN review: BZ identifiable map (benchzoom cbebff8, 919702f, 25811cb, dc895fc on 7314a1e)

Reviewer: adversarial reviewer, 2026-10-13. Zero judge calls, zero model responses read. Authority: author decisions
2026-10-13 D-2026-10-13-1 and D-2026-10-12-2. Data objects: E:/benchzoom_cache (META columns of
hf/mmlu_pro_scores.parquet and eee/math_mc_scores.parquet, emb/*qwen3-embedding-8b-q8_0.npz) and the pickled trees
E:/benchzoom_demo/identifiable_v1/_work/{mmlu_pro,math}_seed{0,1,2}.pkl (SHA256SUMS.txt verifies: OK).
Pins (LF = `git hash-object`; the working tree is clean, so CRLF = LF): gates.py 16155dcd, tree.py 5c2296ee,
atlas.py 55feeeb3, examples/identifiable_map.py 1d44a3fc (= HEAD dc895fc blobs).

## Verdict
- **Build (opt-in rule): MERGEABLE as opt-in.** The default is bit-identical, the tests pass, and the deciding code
  reproduces.
- **Calibration STOP: CONFIRMED.** pi_star = 0.80 is the design prior (7314a1e, 01:17) and was never changed. The real
  builds started at 04:14, after 919702f (03:57).
- **Rendered map: VALID as an exploratory object, but NOT a credible granular map for D-2026-10-13-1.**
  - 7 of 14 MMLU-Pro categories stay unsplit, including the two largest.
  - MMLU-Pro math is a leaf only because of the seed-0 draw (H1).
  - For physics, philosophy, computer science, Intermediate Algebra and Number Theory, no k-means partition with k
    from 2 to 6 reaches PS 0.80 (M1). Splitting them would therefore be a declared resolution, not identifiability.
  - The MMLU-Pro names are partly made from the answer options (H3).
- **Author's remark ("the separation bar might not be the same thing"): borne out, and it applies to the new bar as
  well.** PS with k = 2 penalises items near the boundary, so a continuum with a reproducible axis still scores below
  0.80 (H2). The new gate partly brings back a separation requirement.

## Per-claim table (deciding claims)
| # | claim | builder | reviewer (own command) | status | sev |
|---|---|---|---|---|---|
| 1 | default path bit-identical | golden 63e4b0a1/9756e26e | own fixtures (seeds 5 and 11, dims 24 and 32; Atlas seed 3, bisect seed 7): old src (git archive 7314a1e = 9a42c49 src, diff empty) vs HEAD give 5128a032/693a4743 and 3e389433/f1b3575d, identical | CONFIRMED | - |
| 2 | tests, ruff, mypy | 506 passed, 4 deselected | 506 passed, 4 deselected (752 s); ruff clean; mypy clean on 15 files | CONFIRMED | - |
| 3 | thresholds fixed before the real render | prior 0.80, STOP | design 7314a1e 01:17 → code cbebff8 02:19 → calibration 919702f 03:57 → builds 04:14 (.err mtimes) → 25811cb 04:47. `pi_star`/`min_child` defaults added once in the log (`git log -p` shows a single + line each). The calibration script reads no real data (only 2 path mentions, both the identcal cache) | CONFIRMED | - |
| 4 | calibration C1: isotropic noise never identifiable | 0 in every cell | own seeds: iso n=1000 d=512 0/40 at 0.70 and at 0.80 (median 0.500, max 0.504); iso n=320 d=64 0/40 (median 0.495) | CONFIRMED | - |
| 5 | C3 cells reproduce | el3 n=1000 d=512: median 0.766, 0.98 at 0.70, 0.10 at 0.80; el3 d=64: 0.876, 0.95 at 0.80; el5 n=12000 d=64: 35/50 distinct | own seeds: el3 d=512 0.769, 38/40, 6/40; el3 d=64 0.865, 38/40 at 0.80; el5 n=12000 d=64 identifiable 10/10, distinct 5/10 | CONFIRMED (inside binomial noise) | - |
| 6 | STOP holds without the missing cells | C3 fails at every pi | the C3 label part fails at every pi (el5 n=12000 is labelled continuum in only 5/10 of my runs); every criterion is a conjunction over cells | CONFIRMED | - |
| 7 | MMLU-Pro counts | 17/34 split, 13 distinct / 4 continuum, 31 leaves, depth 4, 7/14 categories, 7 leaves with PS in [0.70, 0.80) | from seed0.pkl: 17/34, 13/4, 31, 4, 7/14, 7 | CONFIRMED | - |
| 8 | MATH counts | 6/13, 2/4, 13 leaves, depth 3, 5/7 | 6/13, 2/4, 13, 3, 5/7 | CONFIRMED | - |
| 9 | deciding PS values | math 0.76, physics 0.51, biology 0.76, psychology 0.72, Intermediate Algebra 0.50, Algebra 0.81, Geometry 0.81, business 0.97 | recomputed at HEAD with node_rng(0, id, STREAM_IDENT): equal to the full float (math 0.7613669338709419; physics 0.5094183493058091; Intermediate Algebra 0.504607132059448; ...) | CONFIRMED | - |
| 10 | the trees are the code that ran (fingerprint disclosure) | library unchanged since launch | children of all 23 accepted splits (17 MMLU-Pro, 6 MATH) recomputed at HEAD (split, then orient_split): 23/23 row-identical. The build_script blob c1122053 is in no commit | CONFIRMED (L1) | LOW |
| 11 | the split decision is stable | "MMLU-Pro math 0.76 at seed 0, splits at seeds 1 and 2" | own rng streams s1-s6: math 0.833, 0.840, 0.7995, 0.819, 0.825, 0.856, so it passes in 5 of 6; Geometry 0.724 at s5; Algebra 0.802-0.846 (thin margin); biology and psychology 0 of 6 | REFUTED as a stable verdict | HIGH (H1) |
| 12 | seed agreement 12/17 (MMLU-Pro), 6/6 (MATH) | as stated | stability.csv: both seeds 12, neither 2; child Jaccard ≥ 0.8: 12; MATH 6/6. The replicates use the SAME rows, so this measures k-means determinism, not resampling | CONFIRMED (number); weaker than it reads | MEDIUM (M3) |
| 13 | no responses read | META columns only | `pq.read_table(columns=META)` followed by a column-equality refusal; the selftest asserts that modelA is not loaded; manifest `model_responses_read: False` | CONFIRMED | - |
| 14 | names LLM-free | keyword pair + medoid | grep for openai/azure/anthropic/requests/httpx/mistral finds 0 in gates.py and tree.py; atlas.py has 3 hits, all the word "LLM-free"; the script has 2 hits, the decision text and the embedder's cache key name | CONFIRMED | - |
| 15 | names match the member questions (spot check: all 46 named children) | (design §7: question text, no options) | the MMLU-Pro names are computed on question + options. "cm cm", "nm nm", "volts volts", "amp amp", "days days" occur in 0.00 of the member stems. Share of members containing either name gram: median 0.095 on stems (MMLU-Pro), 0.23 with options, MATH 0.265; 20/46 children < 0.10 on stems | REFUTED | HIGH (H3) |
| 16 | execution graph accurate | spans + manifest | `update_graph_manifest.py --check` gives "manifest OK"; the step-table spans match (atlas 130/147/219/233, tree 170/205, gates 202/246). L103 and L651 say "keywords on raw text (no options)": true for Atlas.fit, false for the rendered maps | PARTLY | MEDIUM (in H3) |

## Defects (fix each)
- **H1 HIGH: the gate's verdict near pi_star depends on its own rng at R = 20.** The largest MMLU-Pro node is a leaf
  because of the seed-0 draw (it passes on 5 of 6 other streams).
  - Fix: R ≥ 100, or decide on the PS pooled over the seeds.
  - Print PS ± its rng SE, and mark nodes within 2 SE of pi_star UNDECIDED rather than leaf.
- **H2 HIGH (design): PS with k = 2 is not "identifiable" for continua.**
  - Boundary mixing caps PS even when the axis reproduces. Synthetic: el3 d=512 n=1000 has median PS 0.769 with
    axis_cos 0.8-0.98. Real: biology has axis_cos 0.906, psychology 0.856 and math 0.929, yet each has PS below 0.80.
    Physics is 0.57 and Intermediate Algebra 0.39.
  - So the bar is partly a soft gap bar again.
  - Fix (author decision): decide on axis reproducibility (axis_cos or full-vs-half ARI) against an isotropic or
    spectrum-matched null calibrated on synthetic data first. Keep PS as descriptive.
- **H3 HIGH: the MMLU-Pro names are made from the option lists, against design §7.**
  - The script passes the embedded string (`items["text"]` = format_item(question, options)) to build_map, at
    identifiable_map.py L183.
  - Fix: label on `items["question"]`; drop bigrams whose two tokens are equal ("cm cm", from numerals that were
    stripped); rank by coverage times exclusivity, not by the z of rare grams; print each name's member coverage.
  - Re-render.
- **M1 MEDIUM: a k = 2 bisection refuses symmetric multi-way structure.**
  - Synthetic, groups shifted 6 SD along orthonormal directions:
    - 3 equal clusters: PS ≥ 0.80 in 6/20 seeds at d = 64 and 4/20 at d = 512, while the gap test calls them distinct
      8/8;
    - 4 equal clusters: 3/20 and 1/20;
    - asymmetric 50/25/25: 20/20 at both dimensions.
  - The real refusals are NOT explained by this. A k-means PS over halvings with k = 2..6 gives a maximum of:
    physics 0.544, philosophy 0.751, computer science 0.608, Intermediate Algebra 0.528, Number Theory 0.672, other
    0.785.
  - Disclose: a refusal means "no reproducible bisection", not "no identifiable sub-groups".
- **M2 MEDIUM: several splits follow the presentation format, not the topic.**
  - MATH Prealgebra child n=195: an [asy] diagram in 47% of items vs 1% in its sibling.
  - Geometry "label / pair": 45% vs 19%.
  - History n=240: the "This question refers to the following information" template in 98% vs 1%.
  - Health "year old": clinical vignettes in 60% vs 1%.
  - Fix: flag a split as "format" when one template gram covers > 80% of a child and < 10% of its sibling.
- **M3 MEDIUM: the seed replicates reuse the same rows, so the child Jaccard of about 1.0 is k-means determinism.**
  Fix: half-sample or bootstrap replicates.
- **L1 LOW: the builds were launched before 25811cb, and the recorded script blob is not in git** (disclosed).
  Mitigated by rows 9-10 above.
- **L2 LOW: the partial calibration prints NOT CONFIRMED or FAIL for criteria whose cells did not run.**
  - P4: every value run is 0.0 < 0.90, yet the line says NOT CONFIRMED.
  - "C2-H FAIL: 10/10".
  - C5 FAIL, though C5 was never reached.
  - Fix: print UNDETERMINED (cells missing).
- **L3 LOW: own mutants R6 and R7 survive tests/test_identifiable.py; the naming rules are untested** (non-decisive).

## Which nodes look arbitrary (plain reading)
- **Credible: about 10 of the 17 MMLU-Pro splits.**
  - The law subtree (constitutional / property / criminal / evidence; child Jaccard ≥ 0.99).
  - Business (calculation vs marketing).
  - Engineering (electrical vs heat transfer; the names are poor).
  - Chemistry → "mathrm mol / atm atm" (thermodynamics).
  - History (prehistory vs source passages).
  - In MATH: Precalculus (trigonometry vs matrices) and Counting & Probability.
- **Arbitrary or unstable:**
  - economics and its child (child Jaccard 0.42 and 0.11; not split in seed 1);
  - health "year old / examination shows" (split in neither replicate, Jaccard 0.29);
  - history "following information" (a template; split in neither replicate);
  - law "character evidence / probable cause" (Jaccard 0.44);
  - chemistry "cm cm / nm nm" (the name comes from option units);
  - MATH Prealgebra and Geometry (the [asy] format);
  - the duplicated "fee simple / life estate" at depths 2 and 3.
- **Not split, and by this instrument not identifiable at k ≤ 6:** physics, philosophy, computer science, other,
  Intermediate Algebra, Number Theory.
- **Not split, but by a hair or by chance:** MMLU-Pro math (H1); biology and psychology (axis reproducible, PS
  below 0.80 because of H2).

## Own mutants (scratch copy of src; runs tests/test_identifiable.py)
R1 `_ps_one_way` min→mean killed (decisive) · R2 PS_r min→max over the two directions killed (decisive) · R3 `>=`→`>` at pi_star killed (decisive) · R4 orient `g1 > g0`→`<` killed · R5 labeller rng STREAM_GATE→STREAM_IDENT killed · R6 stop-word root share 0.5→0.9 SURVIVED (non-decisive) · R7 z ≥ 1.96 filter dropped SURVIVED (non-decisive).

## Commands (scratch scripts; read-only on caches and pkls; no writes under E:/benchzoom_*)
```
git -C benchzoom log --format='%h %ad %s' --date=iso 7314a1e..HEAD; ls --time-style=full-iso _work/*.err
git archive 7314a1e src | tar -x -C old; PYTHONPATH={old,HEAD}/src python golden.py          # row 1
.venv/Scripts/python -m pytest -q; ruff check .; mypy src; python examples/update_graph_manifest.py --check
python counts.py      # pkl → candidates/splits/kinds/leaves/depth per seed               # rows 7-8
python psp.py 14      # prediction_strength(X[rows], node_rng(s,id,2), SphericalKMeans2(10,100), 20), s=0..6  # rows 9, 11
python splitchk.py    # SphericalKMeans2.split(node_rng(0,id,0)) + orient_split vs pkl children  # row 10
python synth.py / synth2.py / el5.py   # own-seed iso, el3, el5 (+SeparationGate), k3/k4/k3asym   # rows 4-6, M1
python psk.py 12      # k-means PS over 10 halvings, k=2..6, on 10 real nodes                     # M1
python names.py {question,text}   # member coverage of each name gram, [asy]/template shares      # row 15, M2
bash mut.sh           # R1-R7
```
