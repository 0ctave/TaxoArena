# POSTRUN review: BZ axis rule (benchzoom bb8af2d..3b7886e), calibration STOP, no map

Reviewer: adversarial reviewer, 2026-10-13. Reviewed: benchzoom master `3b7886e` (code `0428800`, snapshots `8085733`,
`3b7886e`; design bracket `bb8af2d`). Authority: author_decisions/2026-10-13.md D-2026-10-13-1..3, D-2026-10-12-2/-13-2.
Zero LLM calls, zero writes to the benchzoom tree, the cache or E:/benchzoom_demo (mutants ran in a scratch copy, so the
running driver's code pins (`check_meta`) were not disturbed).

## Verdict

- **Build: MERGEABLE as opt-in** (already on master). The default `gap` and `identifiable` paths are bit-identical:
  the three goldens reproduce from `git archive dc895fc src`, and so does **my own fifth fixture**. 556 passed. Of my 8
  mutants, 7 were killed; the survivor is not decisive.
- **Calibration: STOP CONFIRMED.** The script's own `select()` on my snapshot gives STOP under both readings. My own
  decision code reproduces the deciding cells to the digit, and so do my own seeds (independent halving code).
  `kappa` stays None. No real build was run: 0 files under E:/benchzoom_demo are newer than the design bracket, and 0
  have "axis" in the name.
- **Plain answer to D-2026-10-13-1: there is NO credible granular map yet.** No axis tree exists. The rule is
  uncalibrated, and two of its criteria fail for reasons that more compute will not fix:
  - **A3 at d=4096:** the 2-means axis sits at the null.
  - **A7 at n=160:** the size floor makes the decision depend on the build seed.
- **Which nodes look arbitrary.** This comes from my relabel of the dc895fc identifiable trees with the axis labeller
  (exploratory; these are not axis trees):
  - Grab-bag children that the names do not cover: engineering 524 "laplace transform / power factor (weak)" (cov
    0.06); MATH Prealgebra 666 "positive integers / frac right (weak)" (0.06); health "nerve / true"; business
    "following / marketing".
  - Format children (passage, vignette) fall back to TF-IDF names and are stamped "(weak)" with coverage 0.00, even
    where the name's tokens are in 98% of the child (see M2).

## Deciding claims

| # | claim (builder) | mine | status | sev |
|---|---|---|---|---|
| C1 | A3 el2 n=1000 d=4096 primary 0/200 at every kappa | 0/200 at every kappa, 0 undecided; own seeds (12 data sets, own halving code): median/m0 0.57-1.31, so 0/12 above 1.5 m0 | CONFIRMED | - |
| C2 | PC1 variant 2/200 at kappa 1.5, 0 above | 2/200 (38 undecided) at 1.5; 0/200 (1 undecided) at 2; 0 at 3/4/6 | CONFIRMED | - |
| C3 | A7 pl3 n=160 d=512 23/50; el2 n=160 d=64 43/50; el3 n=160 44-45/50 | 23/50; 43/50; el3 d64 45/50, d512 44/50 (45 at kappa 6) | CONFIRMED | - |
| C4 | A7 at n=160 is caused by the floor, not the gate | without the floor: pl3 50/50 at every kappa (49 at kappa 4); own seeds: the 5 build-seed cuts scatter 70-91 around 80, so only 6/20 nodes are seed-identical | CONFIRMED | - |
| C5 | A1 "iso n=320 d=64 19/200 false splits, 33 undecided" (RENDER bullet A1, given as the primary) | primary: 2/200 split, 12 undecided; **19/200, 33 undecided is the PC1 variant** (partial_2.md L67 says so) | PARTLY (mislabelled in hand-back) | LOW |
| C6 | A7 "at kappa 1.5 and 2 also fails at n=320 (iso d=64 47/50; el2 d=512 33/50)" | iso d=64: 47/50 at 1.5, 50/50 at 2; el2 d=512: 30/50 at 1.5, 33/50 at 2 | PARTLY (values from different kappas merged) | LOW |
| C7 | Low d, n<=1000: false splits <= 0.01 at d=64, 0 at d=512; A3 1.00 at n=1000 | iso max 2/200 (n=320, k=1.5) at d=64; 0/200 in all d=512 cells; A3 el2/el3/el5 200/200 at d=64/512 | CONFIRMED | - |
| C8 | Dip labels sensible | kappa 3, accepted splits: planted delta>=3, n>=320, d<=512: 200/200 "distinct" in every cell; elongated r>=2, n=1000: 0/200 "distinct" (all continuum). n>=3000 not cached (A6 UNDETERMINED there) | CONFIRMED (n<=1000) | - |
| C9 | Inertness goldens (gap 63e4b0a19160c4ae, ident 49a7c53be0b8a1ae / de30eaae39fc95a8) | identical from `git archive dc895fc src` and from 3b7886e; own fixture (depth 2, 200/leaf, dim 48, seed 77): gap 9c283159d59bca27, ident dd06ad31ba73e940 on both | CONFIRMED | - |
| C10 | 556 passed, 4 deselected | 556 passed, 4 deselected, 690 s | CONFIRMED | - |
| C11 | threshold fixed on synthetic before any real build | bracket bb8af2d 13:44, then cache meta 14:33, then code 0428800 18:15 (cache code-pinned; driver3 ran under `check_meta` without REFUSED); real builds: none (count 0) | CONFIRMED (vacuously for the real part) | - |
| C12 | names from question text only | `name_inputs` passes `items["question"]`; Atlas.fit `items["text"]` is the question (options formatted separately, data.py L107); relabel spot check: name grams found in questions (q-share > 0 for every word of 10 MMLU-Pro + 5 MATH nodes) | CONFIRMED | - |
| C13 | format tags correct | spot checks on real trees: health f_vignette 0.01/0.60 ("year old / examination shows"); history f_passage 0.01/0.93 (m2 "question refers to"); MATH f_diagram 0.01/0.47 (asy); MATH f_latex_env 0.02/0.59 (pmatrix); business f_numeric_opts 0.71/0.00 ("rate / year"). All plausible; P8's four M2 splits recur and are tagged where present | CONFIRMED (spot) | - |
| C14 | execution graph accurate | sync test passes; spot checks: labeller rng [seed,u,1] = tree.py L274; extension on the SAME stream = gates.py `halve`; `tie_null_axis` not called by bisect/build_map/Atlas (grep) | CONFIRMED (spot) | - |

## Defects

- **H1 (A7 / floor; registrar):** at n_v near 160 the build seed decides through the floor of 80 (C4). This is a
  property of the rule as it would run on real nodes, not an artefact of the criterion.
  - Fix: make size eligibility seed-free. Decide on n_v alone (for example n_v >= 160 with the cut accepted when
    min child >= 80 - slack), or take the floor from a seed-independent cut.
  - Do not exempt n=160 from A7. That would only hide the seed-dependence.
- **H2 (A3 / d=4096; author):** the primary fails at d=4096 as P2 predicted. PC1 has no kappa that passes both A1
  (kappa 1.5: 19/200 at iso n=320 d=64) and A3 (kappa >= 2: 0/200). So for either statistic the only way out is a NEW
  registration: A3 at d=4096 for n >= 3000, or a fixture with a realistic spectrum. Note that in this fixture the
  tangent-noise norm 64 exceeds base_norm 40 (bracket 12.1). Whether that represents real 4096-d embeddings is
  unexamined.
- **M1 (A1 large n undetermined):** 9/15 iso cells are incomplete. The pilot's 1.58 m0 null at n=12,000 d=64 is still
  unresolved, and the n=12,000 cells at d=512/4096 are skipped by driver3. Any later "kappa=k" needs these cells, or
  a re-registration.
- **M2 (names of format nodes):** `_log_odds_z` uses token counts, so a child of long passages dilutes its own
  defining phrase below z 1.96. Example: history passage child n=240, "question refers information" in 98% vs 0%,
  goes to fallback. The fallback then gets name_cov_any 0 and "(weak)", which misreports it.
  - Fix: compute coverage for fallback names too, and use document-frequency (share) log-odds under "cover".
- **M3 (carried, not done):** the 90% half-sample replicates (review M3) and the per-node tie-null export are still
  missing. They are required before any real axis map.
- **L1:** hand-back mislabels (C5, C6). The numbers in partial_2.md are right.
- **L2:** own mutant R6 survives (`kappa_candidate` UND -> continue). It feeds `predictions` only, not `select`.
  Non-decisive; add a unit test.
- **L3:** A7 has 50 nodes per cell, so a pass at 0.95 (>= 48/50) has CP95 lower bound 0.86. It cannot certify 0.95.
  Moot now (the failures are far below); size it before any re-run.

## Own mutants (scratch copy of 3b7886e; tests test_axis, test_axis_names, test_identifiable, graph sync)

| id | change | result | decisive |
|---|---|---|---|
| R1 | `_inside` -> False (no undecided band) | killed | yes |
| R2 | AxisGate passes on `dec != "leaf"` (undecided passes) | killed | yes |
| R3 | drop SizeGate from the axis gate | killed | yes |
| R4 | calibration `decision` drops the child-size floor | killed | yes (A7) |
| R5 | `_cell_verdict` fails only on >1 failing cell | killed | yes |
| R6 | `kappa_candidate` continues past an UNDETERMINED kappa | SURVIVED | no (predictions only) |
| R7 | `name_inputs` option-leak refusal removed | killed | yes |
| R8 | f_numeric_opts threshold 0.8 -> 0.5 | killed | no |

## Pins (LF = `git rev-parse 3b7886e:<p>` = `git hash-object <p>`; working tree clean, no CRLF)
gates.py fe864583c5fe; atlas.py 77b0ad879c9b; tree.py a7285147083b; examples/axis_calibration.py 8d4c14704c00;
examples/identifiable_map.py 55c634a77493; docs/axis_calibration_partial_2.md d87555532a08. Cache snapshot read:
sites.jsonl copied at 12,287 lines (driver3 still appending; 61/62 present cells complete; iso n=160 d=4096 at 87/200).
mmlu_pro_scores.parquet sha256 49ee92df8b83e834..., mtime 2026-10-10 (unchanged by this review).

## Commands (scratch = session scratchpad)
```
cp E:/benchzoom_cache/axiscal/sites.jsonl scratch/ ; python scratch/rc.py scratch   # own decision code: C1-C8
PYTHONPATH=src python -c "...ac.select(sites,[])"                                   # -> STOP {'a':{'STOP'},'b':{'STOP'}}
python scratch/own.py   # own seeds [777,n,d,s], own halving loop (SphericalKMeans2.centroids), 5 build-seed cuts (C1, C4)
git archive dc895fc src | tar -x -C scratch/old ; scratch/gold.py on old and new src  # C9
PYTHONPATH=src python -m pytest -q -p no:cacheprovider                              # C10: 556 passed, 4 deselected
python scratch/spot.py  # label_tree(AtlasConfig(split_rule='axis'), name_texts=question, options) on identifiable_v1 seed0 pickles (C12, C13, M2)
scratch/mut.sh R1..R8   # sandbox mutants
find E:/benchzoom_demo -type f -newermt '2026-10-13 13:44' | wc -l   # 0 ; find ... -iname '*axis*' | wc -l  # 0
```
