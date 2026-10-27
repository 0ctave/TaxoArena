# POSTRUN review: BZ axis maps at kappa = 3 (benchzoom 6eb484c..3c87621; outputs E:/benchzoom_demo/axis_v1)

Reviewer: adversarial-reviewer, 2026-10-14. Zero LLM calls; text/embeddings only; every input opened read-only.
Reviewed blobs (LF, `git hash-object`): `examples/identifiable_map.py` blob:cef9440a45d5 (= the build pickles'
`script.git_hash_object_lf`), `examples/axis_map.py` blob:f4e5523a0dc6. `src/` unchanged over 6eb484c..3c87621
(`git diff --name-only 6eb484c..3c87621 -- src | wc -l` = 0). SHA256SUMS: 97 lines, 0 not OK (`sha256sum -c | grep -vc ': OK$'`).

## Verdict

- **Build: VALID as built.** kappa, width, floor and cut are the registered ones; every deciding number I recomputed
  reproduces (to the digit for counts, within Monte Carlo error for AR_v); default `gap` bit-identical on my fixture.
- **Credible granular map for D-2026-10-13-1: NO, not as "reproducible splits".** It meets the letter of D-1
  (14 of 14 and 7 of 7 categories split, leaves 83-329), but the axis gate refuses nothing on real data. It refused
  0 of 96 (MMLU-Pro) and 0 of 36 (MATH) tested nodes. Even the tie null (no preferred axis) has median AR 0.209-0.68,
  above L = 0.0895 at every node. So the map is a **size-floor bisection along the leading 2-means axis**. The
  evidence that a split is real is the 90% replicates and the tie null, which are export-only. On those, 8 nodes
  fail both checks and 11 more reproduce in at most 1 of 5 replicates (list below).
- **Before post 1 (conditions):** H1 (say what the gate does and does not certify; mark or collapse the arbitrary
  nodes), H2 (names), M1 (suite green). With those, it can be shown as an *exploratory* map with stability marks.
  It cannot be shown as a map of identifiable sub-domains.

## Per-claim table (deciding claims)

| # | claim | my number | claimed | status | sev |
|---|---|---|---|---|---|
| C1 | kappa = 3 from the committed calibration and D-2026-10-14-1, not tuned on real data | config `kappa 3.0` in all 7 manifests; calibration 6eb484c 07:41, first build after da3bf22 13:40; no real build at another kappa on E:/benchzoom_demo (`grep '"kappa"'` -> only 3.0) | same | CONFIRMED | - |
| C1b | kappa matters to the map | no: every tested node has its 99% lower bound lo > L for kappa < **5.16** (MMLU-Pro) / **4.35** (MATH), so readings a and b give the same tree | (implied) | NEW (see H1) | HIGH |
| C2 | 512-d MRL prefix + renorm, min_child 80 | manifest `embedding_width 512, mrl_prefix_renorm`; `min_child 80`; my own `X[:, :512]` renorm gives cuts **identical** at 15 of 15 sampled split nodes; leaf min 84 / 83; floor rule (n >= 160 and n x share >= 80) matches `axis_admissible` at 96/96 and 36/36 | same | CONFIRMED | - |
| C3 | node decisions (AR_v vs L) | own halvings, own spherical 2-means, own seed, 16 nodes: decision agrees 16/16; AR_v within 2 SE_MC at 15/16; MATH node 30 is 0.129 vs 0.223 stored (3.2 SE; top-2 eigenvalue ratio 0.973, a near-tie). Share medians within 0.012 | 0.223 etc. | CONFIRMED (1 noisy) | LOW |
| C4 | tree counts and leaf sizes | 147/80 and 66/36 nodes/leaves; leaf min/median/max 84/144.5/329 and 83/134.5/224; parent n = sum of children at every node; leaf sums 11,994 / 4,914; 80/80 and 36/36 leaves `size` | same | CONFIRMED | - |
| C5 | stability counts (tree.csv) | seeds 65/66, 29/29; reps 5/5: 51/66, 20/29; rep child-Jaccard min/median 0.157/0.876, 0.239/0.701; beyond tie p95: 53/66, 22/29 | same | CONFIRMED to the digit | - |
| C6 | stability with own seeds | own per-node 90% re-cut (5 draws, seed 20261014, clip implemented): min child-J >= 0.8 at 58/66 and 24/29; worst 0.554 (MMLU-Pro 67) and 0.514 (MATH 14). The builder's whole-corpus replicates are lower (51/66, 20/29) because parent membership changes cascade | - | CONFIRMED (local cut stable; cascade is the instability) | - |
| C7 | tie null | own implementation (20 draws x R 40, own seed) on 4 nodes: med/p95 0.486/0.730 (stored 0.498/0.721), 0.254/0.443 (0.225/0.391), 0.548/0.847 (0.542/0.816), MATH 30 0.392/0.689 (0.422/0.728); beyond/within agrees 4/4; tie p95 > L at 96/96 and 36/36 (m3.txt) | same | CONFIRMED | - |
| C8 | dip labels | own split-dip (R 40, own 2-means + diptest 0.11.0) on 10 nodes: kind agrees 10/10 (e.g. law 0.007 vs 0.013, cs node 75 0.028 vs 0.022, heat 0.013 vs 0.033, Precalculus 0.11) | same | CONFIRMED | - |
| C9 | format tags | own regexes: tagged numeric-options (nodes 2, 11, 55, 75), vignette (7, 32) and diagram (MATH 6) shares match **exactly**; Precalculus pmatrix child: "pmatrix" substring in 0.536 of its items vs stored f_latex_env 0.58 (my regex failed through the shell; substance consistent); f_passage not re-derived. 27/28 small mismatches on *untagged* features come from my simplified unit and environment regexes | same | CONFIRMED (spot) | - |
| C10 | names from question text only, covering their questions | code: `name_inputs` passes `items.question`; it is REFUSED when that equals the embedded text with options present. Spot 10 + 10: own coverage = stored 10/10 MMLU-Pro and 7/10 MATH (the 3 gaps come from my tokenizer keeping digits). But coverage is low: MMLU-Pro children median cov_any **0.178**, 77/132 < 0.20, 28/132 < 0.10; MATH median 0.212, 17/58 < 0.10 | "names LLM-free" | PARTLY (source CONFIRMED; covering REFUTED for most) | HIGH |
| C11 | default `gap` bit-identical | own fixture (planted 600 + elongated 500, d 48, seeds 0 and 3): tree-frame sha256/16 `d2ede35580429c23` / `143137fa14fc6f36`, the same with src at 3b7886e (last reviewed) and at 3c87621. This covers ae7a9c2's src change, which no committed review covered | same | CONFIRMED | - |
| C12 | tests | full suite at 3c87621 (.venv): **594 passed, 1 FAILED** (`test_identifiable_map_script_selftest`, "order/workers"); it fails with and without OMP=4 | 595 passed at cb81ddc; later only test_axis_map re-run | REFUTED in reviewer env | MEDIUM |
| C13 | execution graph | prose sentence accurate (export/render only, decides nothing); `update_graph_manifest --check` -> OK; ruff clean | same | CONFIRMED | - |

Own mutants (sandbox copy of examples/ + tests/test_axis_map.py; 5, deciding paths of the render):
R1 beyond `>`->`>=` killed (decisive); R2 untested-leaf size `<`->`<=` killed; R3 `not-reproducible`->`size` killed
(decisive: it would hide a gate refusal); R4 seed agreement counts splits only, killed; R5 child-J `min`->`max` killed.

## Nodes that look arbitrary (cut not distinguishable from a tie AND not reproduced 5/5)
- MMLU-Pro: 49 "number / total" (344), 61 "pressure / gas" (250), 67 "ideal gas / following data" (218), 70 "plants /
  plant" (208), 71 "older / risk" (215).
- MATH: 13 "draw cycle / label asy" (265), 30 "begin align / end align" (288; AR_v 0.223 is BELOW its tie median
  0.42), 34 "nw label / square units" (256).
- Reproduced in <= 1 of 5 replicates (beyond tie but cascade-unstable): MMLU-Pro 27, 51, 59, 75, 77, 87 (also seeds
  2/4), 89; MATH 32 "asy unitsize" (1/5), 37 "average / students" (1/5).

## Defects and fixes
- **H1 (HIGH) The axis gate does not discriminate on real data.** It refuses 0/132 tested nodes, the tie-null
  median exceeds L everywhere, and kappa is irrelevant below 4.35. The tree's shape comes from the 160/80 floor and
  the held-out share median. *Fix:* in every output and in post 1, call the gate "rejects only near-isotropic
  nodes" and never "reproducible axis". Make the 90% replicate count and the tie null the shown marks. Either collapse
  the 8 nodes above (and the <= 1/5 nodes) or draw them as unstable. Making either mark deciding needs a
  re-registration (author decision).
- **H2 (HIGH) Names do not describe their nodes.** 77/132 MMLU-Pro children are named by grams that cover under 20%
  of their own items. 10 children are named exactly as their parent (MMLU-Pro 16, 28, 29, 32, 40, 45, 46; MATH 11, 13,
  26). There are function-word names ("explain / does", "following / real", "correct / statements", "according /
  claims") and markup names ("begin pmatrix", "asy unitsize", "draw cycle"). *Fix:* show the medoid snippet when
  cov_any < 0.20; drop a child name equal to its parent's; add LaTeX/asy commands and question boilerplate ("following",
  "statements", "does", "explain") to the naming stop list (labels only, no tree change). Or wait for the D-2026-10-13-2
  Kotlin labeller, with these keyword names kept as its audit.
- **M1 (MEDIUM) Suite not green; the worker-count claim is not bitwise.** `cmd_tienull` with workers=1 runs in-process
  with the parent's BLAS threads, while workers >= 2 force 1 thread, so the exact-dict compare fails. The real runs
  used workers 5 and 10, so the stored values are deterministic. *Fix:* pin BLAS to 1 thread on the workers=1 path
  (threadpoolctl) or compare at a tolerance, then re-run the full suite at the tip (the builder skipped this after
  d39fd04..3c87621).
- **M2 (MEDIUM) Record gaps.** K = 5 replicates is the engineer's choice, not registered. The identifiable_splits.md
  M3 bracket still says "Not done: ... any real build". *Fix:* the registrar records K = 5 as an engineer choice and
  the builds (pins: SHA256SUMS, backup E:/TaxoArena_backup_20261014_bz_axis_v1) by insertion.
- **L1** The axis build logs (_work/*_axis_seed*.log) print the identifiable rule's STATUS ("pi_star = 0.80 ...
  919702f"); logs only, the outputs carry the right status. *Fix:* rule-specific STATUS in `cmd_build`.
- **L2** The hand-back's tree.txt paste has "7x.x" placeholders; post 1 must use the file (its sha is in SHA256SUMS).
- **L3** Whole-corpus replicates are uniform, not stratified (disclosed); my per-node re-cut shows the local cut is
  stable, so replicate failures mainly come from parent membership cascading.

## Commands / scripts (scratchpad, read-only inputs)
```
git -C benchzoom diff --name-only 6eb484c..3c87621 -- src | wc -l            # 0
git hash-object examples/identifiable_map.py examples/axis_map.py         # cef9440a45d5 / f4e5523a0dc6
python (tree.csv): raw axis decision 96/96, 36/36 split; R=100 everywhere; lo/m0 min 5.16 / 4.35; leaf sums; floor rule
own_axis.py <ds> sample      # own truncation + 2-means halvings + own cut on 8 nodes per map
own_axis.py <ds> resample    # own per-node 90% re-cut, 5 draws, child Jaccard
own_tie.py mmlu_pro 1,70,15 ; own_tie.py math 30                          # own tie null
own_labels.py <ds> <nodes>   # own split-dip, format shares, name coverage, parent-name duplicates
golden.py with PYTHONPATH=<3b7886e src> vs src                            # default gap sha equal
.venv python -m pytest -q    # 594 passed, 1 failed (test_identifiable_map_script_selftest)
update_graph_manifest.py --check -> manifest OK; sha256sum -c SHA256SUMS.txt | grep -vc ': OK$' -> 0
```
