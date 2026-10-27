# Review: BENCHZOOM-EXECUTION-GRAPH (benchzoom 9a08f54, parent 6ade538)

Adversarial reviewer, 2026-10-11. Read-only on benchzoom (status count 0 before and after, `git status --short | wc -l`);
scratch E:/TaxoArena_tmp/graph_review. Zero LLM calls, <= 4 threads.

## Verdict: NOT ACCURATE (close). The maths and defaults are right; the guard and four statements need fixing

The maths, defaults, branch order and line numbers match the code. Every deciding equation was recomputed
independently and agrees to the digit. All four mermaid blocks parse and render. The sync guard catches each covered
change and lets a docs-only edit through. The verdict is NOT because of two things: (1) the guard does not cover code
that the documented algorithm depends on (5 of my 7 mutants survived, 2 of them change what the algorithm computes);
(2) four statements are wrong or leave out a branch. With G1 and T1-T3 fixed (T4 and T5 are LOW), the doc is
ACCURATE. No change to `src/` is needed.

## Deciding claims

| # | claim | my result | status | sev |
|---|---|---|---|---|
| 1 | src/ untouched; 5 files changed | `git diff --name-only 6ade538 9a08f54 -- src \| wc -l` = 0; all files = 5 | CONFIRMED | - |
| 2 | tau_l^2 moments (plain / centred), gate z vs z_{1-a}, posterior d | independent re-implementation of doc §3.4 on a 7-node tree, 400x6 synthetic: tau code = indep (0.168756 plain, 0.186328 centred, with and without gate_alpha 0.05), max abs diff of d = 0.0 | CONFIRMED | - |
| 3 | BH step-up (ties included, NaN outside m) | own BH vs `bh_reject`, 2,000 random families with NaNs: 2000/2000 identical | CONFIRMED | - |
| 4 | one-child rule 1.96 iff q == 0.05, else z_{1-q/2} | 1.96; q=0.1 -> 1.644854 = norm.isf(0.05) | CONFIRMED | - |
| 5 | separation early stop at 15th exceedance, sep_p 16/301 | limit floor(0.05*301-1+1e-9) = 14; 16/301 = 0.0532 > 0.05 | CONFIRMED | - |
| 6 | one-SE rule strict, both finite | delta = se: no descent; se = inf: no descent | CONFIRMED | - |
| 7 | cluster SE = sd/sqrt(n) with one item per group | 0.1345265755 = 0.1345265755 | CONFIRMED | - |
| 8 | D8: tau = 0 and q=None -> certified with sign 0; q=0.05 -> never | certified [0 1 1 1 1 1 1], sign all 0; q=.05 all 0 | CONFIRMED | - |
| 9 | step table file:line (65 objects) | AST spans: every row starts at the object's first line and ends at its end_lineno (combined rows such as `moment_factor, moment_matched` 57-71 cover both) | CONFIRMED | - |
| 10 | mermaid parses | mermaid-cli 12.0.0 (npx): 4/4 rc 0, 0 "syntax error" in the SVG files, node counts 27/16/28/18 match the sources | CONFIRMED (the writer had not checked) | - |
| 11 | sync test: covered change fails, docs-only passes | 23/23 pass; my R5 (`se<s_max` -> `<=`) and R6 (default h_min 1.0 -> 2.0) KILLED; a prose edit of a doc copy -> `--check --doc` rc 0 "manifest OK" | CONFIRMED | - |
| 12 | "the guard fails as soon as the algorithm changes" (README Contributing, doc Sync rule) | R1, R2, R3, R4, R7 SURVIVE (see mutants) | REFUTED as worded | HIGH |
| 13 | §3.1 / D5 "subject = task only when >1 task (`_items_frame`); single-task import has no subject" | true for lm-eval / leaderboard / inspect only. `from_eee` (sources.py:996) sets subject = evaluation_name and drops it only if <= 1 unique; `from_csv` (1214-1215) keeps a user-given subject even for one task | REFUTED | MEDIUM |
| 14 | §3.4 "Centring (option): ... raw uses g'" | `g_l[j]` is replaced, so d, dc, g[u] and r_par all use g' (profile.py:270-272, 296, 306-310), not only raw | PARTLY | MEDIUM |
| 15 | pipeline graph covers the orchestration branches | embedder AND prebuilt tree: X and coords are computed but bisect is skipped (atlas.py:116-122); the graph routes every embedder path through bisection | PARTLY | MEDIUM |
| 16 | calibration pins | `depth_calibration_v2.py --selfcheck`: criteria 174a86ce OK, library blobs OK | CONFIRMED | - |
| 17 | ruff / mypy on the new files | "All checks passed!" / "no issues found in 2 source files" | CONFIRMED | - |

## Mutants (own; mutated copy of the package placed first on PYTHONPATH, loaded path asserted; `update_graph_manifest.py --check`)

| id | change | result | decisive |
|---|---|---|---|
| R1 | `Tree.max_depth` max -> min (sets fit_offsets' depth loop and `_paths`) | SURVIVED | yes |
| R2 | `Tree.leaves` `is_leaf` -> `not is_leaf` (drives `leaf_of_items`, hence `make_folds`) | SURVIVED | yes |
| R3 | `from_eee` subject drop `<= 1` -> `<= 2` (a §3.1 / D5 claim) | SURVIVED | no (doc claim already wrong, T1) |
| R4 | `inspect_value_to_float` P 0.5 -> 0.4 (a §3.1 claim) | SURVIVED | no |
| R5 | `adaptive_read` `se[c] < s_max` -> `<=` | KILLED (adaptive_read) | yes |
| R6 | `fit_offsets` default `h_min` 1.0 -> 2.0 | KILLED (fit_offsets) | yes |
| R7 | `Node.n` -> len - 1 (sunburst n, Fingerprint n) | SURVIVED | no |

The writer's 7 mutants are reproduced by the committed test file (23 passed in 10.3 s, venv python).

## Defects and fixes

- **G1 (HIGH) The guard has coverage gaps.** COVERED fingerprints only `Tree.leaf_of_items` from tree.py's classes. It
  leaves out `Tree` (max_depth, leaves, path), `Node`, `GateContext`, `NodeOffsets`, `Fingerprint`, `CrossFit`,
  `CrossFitRead`, `Precomputed`, `export._f/_arr`, `inspect_value_to_float`, `from_eee`, `from_csv`, `_build_lm`.
  Fix: in `examples/update_graph_manifest.py`, fingerprint the whole algorithm modules (`benchzoom.tree`, `gates`,
  `irt`, `profile`, `crossfit`, `atlas`, `embed`, `data`, `export`, `plot`) with the same docstring-free AST dump of
  `inspect.getsource(module)`. Keep the per-object entries so the failure names the changed object. Add the
  sources.py objects behind §3.1's claims (`inspect_value_to_float`, `from_eee`, `from_csv`, `_build_lm`), or drop
  those claims. Add R1 and R2 to `E2E` in `tests/test_execution_graph_sync.py`.
- **T1 (MEDIUM) The subject claim is wrong for two adapters.** Rewrite the §3.1 bullet and D5 like this: "lm-eval,
  leaderboard and inspect (`_items_frame`): subject = task iff >1 task. EEE: subject = the sample's
  `evaluation_name`, dropped iff <= 1 distinct (one benchmark can carry a subject level). CSV: a given `subject`
  column is kept, else task iff >1 task. `Atlas.fit` uses whatever `subject` column the items frame has."
- **T2 (MEDIUM) The centring description stops at raw.** In §3.4, replace "raw uses g'" with "g' replaces g
  everywhere downstream: raw, the posterior d, the sibling contrast dc and r". In the Stage B flowchart, label PS
  "d = g' / (h + 1/tau^2) (g' = g when not centred)".
- **T3 (MEDIUM) One orchestration branch is missing.** In the pipeline graph, add the edge "embedder given AND tree
  given -> X, coords computed, bisection skipped (tree.n_items must equal n_items)". Add the refusals of `Atlas.fit`:
  no embedder and no tree; embedder row count != n_items; prebuilt tree that does not cover the items.
- **T4 (LOW) The import node shows the wrong call.** Pipeline node B reads "Imported.benchmark() ->
  Benchmark.from_frames". The fit path is `Atlas.fit(imp.items, imp.scores)`, which calls `from_frames` itself
  (atlas.py:104); `Imported.benchmark` is a separate helper. Relabel B.
- **T5 (LOW) Smaller omissions.** (a) Crossfit's own RuntimeWarning for unconverged fold fits (crossfit.py:208-209)
  is missing from Stage C. (b) The refusal "every item must be filed to a leaf" in `make_folds` is
  missing. (c) `CachedEmbedder` refuses a cache written under another name or width. (d) `fit_offsets` refuses
  `gate_alpha` outside (0,1), and `adaptive_read` refuses an unknown `certify`. (e) Edge case: a 15th exceedance
  exactly on draw 300 is not flagged `sep_p_lower_bound` (same refusal). Add a line each.
- **N1 (note) The manifest script needs the package installed.** It runs only where `benchzoom` is installed, e.g.
  the venv; system Python raised ModuleNotFoundError. The README Contributing section could say "with the dev venv
  active".

Checked and matching: Stage A (candidate rule, largest cell with ties to the lowest id, degenerate and refused cells
never retried, Size -> Separation -> Dip, the null construction, the J formula, dip details); Rasch (priors, clipped
Newton, closed-form shift, tol and maxit, LOMO warm start, fit_theta does not warn); certification (z = 0 at SE = 0,
SE(d) used for s_max even under contrast, forced subject entry); crossfit (folds by majority leaf with ties to the
smaller id, rng [seed, 7], round robin with a carried counter, held-out difficulty, eta, the assertion, node_deltas
filter, CrossFitRead stop and stop_depth, cache key); exports and plots. The docs-vs-code items spot-checked
(D3, D7 at defaults.md:144 of 6ade538, D8, D13, D14) are as stated.

## Commands

```
git -C Z:/FAC/TUBerlin/benchzoom diff --name-only 6ade538 9a08f54 -- src | wc -l          # 0
python E:/TaxoArena_tmp/graph_review/lines.py         # AST spans vs step table, 65 objects
PYTHONPATH=src python E:/TaxoArena_tmp/graph_review/num.py   # tau / BH / 1.96 / limit / one-SE / SE / D8
.venv/Scripts/python -m pytest -q -p no:cacheprovider tests/test_execution_graph_sync.py   # 23 passed
.venv/Scripts/python E:/TaxoArena_tmp/graph_review/mut.py    # R1-R7
.venv/Scripts/python examples/update_graph_manifest.py --check --doc E:/.../doc_copy.md   # prose edit -> rc 0
npx -y @mermaid-js/mermaid-cli -i gN.mmd -o gN.svg   # N=0..3, rc 0, grep -c 'syntax error' = 0
.venv/Scripts/python examples/depth_calibration_v2.py --selfcheck   # criteria 174a86ce OK
git hash-object docs/execution_graph.md   # LF 91504eb1 = blob in 9a08f54 (working tree identical, no CRLF variant)
git hash-object examples/update_graph_manifest.py   # 5067e513 = blob
git hash-object tests/test_execution_graph_sync.py  # a6ad660f = blob
```
