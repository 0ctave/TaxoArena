# POSTRUN review: BZ-TREE-VARIANTS-WORK (EXPLORATORY, WORK split only)

Authority: `docs/agents/author_decisions/2026-10-20.md` D-2026-10-20-5 (79b1ff2d). Reviewer: adversarial reviewer,
2026-10-21. Zero API calls. BZ-METER reserved responses never read: in my reproduction `VaultGuard.arm` and `.open`
were replaced by a raising sentinel and it never fired; `guard.reads == 0` both datasets. Reviewed: benchzoom
975e66b..46b4155 (plan `docs/tree_variants_work.md` LF blob `00c4313f`; script `examples/tree_variants_work.py` LF blob
`7fc4b73d` = the run's `script_blob`, unchanged 5cc8daf..46b4155; tests LF blob `ea691af9`; benchzoom working tree
clean, `git status --short | wc -l` = 0). Outputs `E:/benchzoom_demo/tree_variants_work/{math,mmlu_pro}`.

## Verdict

**VALID as exploratory output.** Every deciding number reproduces (max gap 4.9e-7 MATH, 3.8e-7 MMLU-Pro); plan and
brackets precede every variant number; the superseded centred V3/V4 could not have been scored; folds are identical
across variants; V1b is exactly V0 cut at depth 4; nesting respects the declared cells.

**Freezing V1b for the fresh confirmation is DEFENSIBLE, with conditions (C1-C3 below), but the WORK margin is not
evidence that V1b beats V0.** The V1b - V0 contrast is a re-reading of a contrast already seen on these items
(POSTRUN_BZ-GRANULARITY-WORK claim 7: d4 - d5 on |L2 = +0.030 SE 0.009; per-item correlation with the C1 contrast
0.93), and 120% of it comes from the 294 WORK items under the two depth-5 splits V1b removes. Adjusted for the
effective selection set (cuts d2, d3, d4 + V1..V4) the margin stays above a max-T line (2.65 vs 2.30, adjusted
p 0.019), optimism-corrected +0.019 (2.08 paired SE). V1b = "V0 minus two splits", a cheap, nested, deterministic
choice; the fresh data is the test.

## Per-claim table (deciding claims)

| # | Claim | Own result | Verdict | Sev |
|---|---|---|---|---|
| 1 | plan before any build; P1-P3 before any variant number | plan 975e66b 23:16:54 touches 1 file; first build record 23:23:53 (V0), last 23:46:43; P1/P2 in 8aa1597 23:23:44, P3 in 7f9ec9f 23:31:25; first scores 23:56:10 / 23:57:42; plan edits insertion-only (`git diff --numstat 975e66b 46b4155` = 89 / 0) | CONFIRMED | - |
| 2 | superseded centred V3/V4 never scored | every script version before 5cc8daf (8aa1597, 7f9ec9f, f0a4e38: `grep -c 'vault_reads=int'` = 1 each) builds `meta` with `vault_reads=` AND `**g.info`, which holds `vault_reads` (granularity_work L910): TypeError in `cmd_score` BEFORE `run_scores`. 5cc8daf (23:50:52) postdates the move to `_superseded_centred/` (23:31:32). Scored V3/V4 records: blob 3b11cd77 (=7f9ec9f), cos-to-original 0.991; superseded: blob 65a3a733, cos 0.814, 35/44 leaves. An ad-hoc scoring outside `cmd_score` is not excludable from files | CONFIRMED (via cmd_score) | LOW |
| 3 | identical folds across variants | all variants scored inside one `_variant_task` per (seed, fold) on the same `te`; each of 5 seeds partitions 2,949 / 7,197 items (fold sizes 586-593 / 1,428-1,448); fallback 0/0 | CONFIRMED | - |
| 4 | MATH C1: V0 +0.109(0.032), V1 +0.043, V1b +0.134(0.035), V2 +0.000, V3 +0.071, V4 +0.002 | +0.10932(0.03159), +0.04337(0.01911), +0.13403(0.03481), +0.00041(0.00123), +0.07139(0.02926), +0.00175(0.00116) | CONFIRMED | - |
| 5 | V0 reproduces GRANULARITY-WORK (G\|L2 +0.124 SE 0.035, C1 +0.109 SE 0.032, d4 +0.154) | +0.12405, C1 +0.10932 SE 0.03159, d4 +0.1542, d5 +0.1241 (= the 4759e014 reference to the digit); V0 pickle sha = AXIS_PINS | CONFIRMED | - |
| 6 | V1b - V0 +0.025, paired SE 0.009, 2.65 SE | own cluster SE (independent code): +0.02470 SE 0.00933, z 2.648. DEFF 1.000 (2,946 clusters / 2,949 items), n_eff 2,949, MDE80 = 2.80 x 0.00933 = 0.0261: the margin is AT the MDE80 | CONFIRMED | - |
| 7 | 2.33 = selection line for 5 variants | Bonferroni one-sided 0.05/5 = 2.326, correct for 5 comparisons vs V0; max-T (multiplier bootstrap, 20k) for the same 5 = 2.185 (conservative as stated) | CONFIRMED | - |
| 8 | "beyond selection noise" | the set was not 5: depth 4 came from the d1..d5 curve on the same items. Effective set {c2, c3, c4=V1b, V1..V4}: max-T line 2.297 (Bonferroni 2.498), adjusted p 0.019; two-stage winner's-curse optimism (stage 1 argmax depth on \|L2, stage 2 argmax C1; 4k cluster bootstraps) +0.0053 -> corrected margin +0.0194 (2.08 SE); plan-only optimism +0.0018. All of the margin from the 2 removed depth-5 splits (294 WORK items, 120%) | PARTLY | MEDIUM |
| 9 | V1b is V0 truncated, no rebuild | `v1b()` = `cut(W["V0"], 4)` in code; own partition from node rows at depth <= 4 identical; MATH: 2 depth-4 nodes with children (2+2), 36 -> 34 leaves; MMLU-Pro: 6, 80 -> 74 | CONFIRMED | - |
| 10 | residualisation removes feature directions, no response info | features from question/options text only (`gates.format_features`, length, TeX count); log: max \|corr\| 0.504 -> 9.6e-16 projected -> 0.003 after 3 alternations (MATH); 0.324 -> 0.009 (MMLU-Pro); linear only (non-linear style not removed) | CONFIRMED | - |
| 11 | nesting respects cells | 0 nodes at depth >= 1 span two declared cells (V2, V4, both datasets); cells = meter L2 (cmd_score refusal passed); 5 of 35 MATH cells split (Algebra L3-5, Int. Algebra L4-5), 15 of 91 MMLU-Pro | CONFIRMED | - |
| 12 | MMLU-Pro all ~0; V2 +0.026, margin 1.75 SE, partly the L2 re-read (d2 +0.027) | +0.02577, diff +0.03530 SE 0.02019 (z 1.749); V2 cut2 +0.0266; V1b - V0 +0.0008 SE 0.0075 | CONFIRMED | - |
| 13 | MATH V2 null | see "MATH V2" below: mostly a floor/construction artefact, weakly informative | PARTLY | LOW |

## MATH V2: floor artefact or topic-vs-level evidence?

30 of 35 cells are unsplit (24 below 2 x 80; 6 eligible cells the rule declined), so V2 = L2 on 2,140 of 2,949 WORK
items and contributes zero there by construction; the +0.011 G|L2 is the harness's L2 re-read (V2 cut2 +0.0116; the
artefact exists on MATH too, SE 0.004). In the 809 WORK items of the 5 split cells, the within-cell splits add
+0.0001 (SE 0.0025) over the re-read, while V0's level-crossing leaves earn +0.0048 (SE 0.017) more than V2 on |L2 and
+0.0146 (SE 0.016) on C1 on the same items. Reading: within-level axis splits at this floor carry nothing measurable;
the null does NOT separate topic from level (L2 already holds level for every variant, and V2 leaves of ~100 WORK items
per (model, leaf) are shrunk away). Quote it as "nesting cannot be tested at floor 80 on MATH", not as evidence.

## Defects

- D1 (MEDIUM): summary.txt / plan Section 7 table say the V1b margin is "beyond selection noise" against 2.33. Fix:
  bracket `[P4]` with the effective-set numbers (max-T 2.30, adjusted p 0.019, corrected +0.019, 2.08 SE) and the
  0.93 correlation with the already-seen d4 - d5 contrast; the plan's own "NOT a clean selection" paragraph stays.
- D2 (MEDIUM): call V1b "V0 with the two depth-5 splits removed" in any registration; the whole margin is those
  294 items. Name both depth-5 split ids in the fresh registration.
- D3 (LOW): mutants R5 (unpaired SE in `aggregate`) and R6 (`ADJ_Z` 2.33 -> 1.645) survive the 12 tests. Fix: a test
  pinning `pair_se` against an explicit cluster formula on a fixture with correlated variants, and `ADJ_Z ==
  round(norm.ppf(1 - 0.05/5), 2)`.
- D4 (LOW): the L2 re-read artefact (G(cells | L2) > 0: MATH +0.012 SE 0.004, MMLU-Pro +0.027 SE 0.016) inflates any
  variant whose leaves nest in L2; a future nested variant must be scored net of its own cut-at-cells.

## Conditions on freezing (for the fresh-data registration)

- C1: primary G(V1b | L2 + diff + len) on fresh MATH under the 3-SE rule; V0 (same pinned pickle, uncut) as the
  pre-declared secondary, so the conclusion does not hinge on the WORK-selected cut.
- C2: the V1b - V0 contrast is DESCRIPTIVE-ONLY on fresh data: corrected effect ~+0.019 vs MDE80 ~0.026 at WORK size
  (DEFF 1.00; scale by sqrt(2,949 / n_fresh)).
- C3: MMLU-Pro: freeze nothing (best margin z 1.75 < every selection line; mostly the re-read).
Recommended: primary tree MATH V1b (axis_v1 seed-0 cut at depth 4, 34 leaves); secondary V0 (36 leaves). Not V2/V4.

## Mutants (sandbox `git archive 46b4155`; TMP/TEMP/TMPDIR redirected; 12 tests + --selftest)

R1 CUT_V1B 4->5: killed (decisive) · R2 centring reading of residualise: killed · R3 nesting refusal disabled: killed
(decisive) · R4 C1 parents o_dl->pL2 (criterion substitution): killed (decisive) · R5 unpaired SE: SURVIVED (decisive;
covered by my reproduction, D3) · R6 ADJ_Z 1.645: SURVIVED (D3).

## Commands

```
git log --format='%h %ci %s' 975e66b^..46b4155; git diff --numstat 975e66b 46b4155 -- docs/tree_variants_work.md
git hash-object examples/tree_variants_work.py tests/test_tree_variants_work.py docs/tree_variants_work.md
ls -la --time-style=full-iso E:/benchzoom_demo/tree_variants_work/{_work,_work/_superseded_centred,math,mmlu_pro}
for c in 8aa1597 7f9ec9f f0a4e38; do git show $c:examples/tree_variants_work.py | grep -c 'vault_reads=int'; done
sha256sum -c SHA256SUMS (math, mmlu_pro: OK); sha256sum -c SHA256SUMS_backup (60/60 OK)
scratch rev.py: load_real + work_paths + V0 cuts c1..c4, TV.variant_task x 25 (8 workers), per-item PI -> rev_<ds>.pkl
scratch anal.py: own cluster SE vs variants.csv, DEFF/MDE, max-T (Gaussian multiplier, 20k), two-stage cluster
  bootstrap (4k), V2 split-cell decomposition; extra.py: corr(L2, C1 contrasts) 0.927, removed-split share 1.204
scratch chk_struct.py: V1b partition from node rows, nesting span count, build blobs, superseded records
E: listing (path, size, mtime) of benchzoom_demo, benchzoom_cache, backup: 4,244 files, diff before/after = 0 lines
pytest tests/test_tree_variants_work.py (12 passed, .venv); --selftest PASS
```
