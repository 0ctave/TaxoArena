# POSTRUN review: MMLU-GAP-BASELINE (cause 1, sharper declared baseline; EXPLORATORY, WORK rows only)

Authority: D-2026-10-22-1 (`docs/agents/author_decisions/2026-10-22.md`). Reviewer: adversarial reviewer, 2026-10-22.
Zero LLM calls. No vault or reserved response was read. My MMLU load asserted `guard.reads == [0, 0]` at the end; MATH
went through `granularity_work.load_real` with the guard never armed (reads 0). Reviewed: benchzoom branch
`gap-baseline` (local, no remote), 0ccc014..9ea1d87 on master dfeb0aa. Run of record = script LF blob `e567860a` (HEAD
49b18c0); math_hx ran at `a6eda6cd` (HEAD c578c3c). Tip blob `2e6068c5` differs only in the docstring (one hunk,
L39-L77). Outputs: `E:/benchzoom_demo/mmlu_gap_work/baseline` (summary.txt sha256 156b59cf…; SHA256SUMS 13/13 OK).

## Verdict

**CONFIRMED (exploratory), with two MEDIUM qualifications on the reading (D1, D2).**
- Every deciding number reproduces to the printed digit.
- The deciding per-item arrays reproduce to at most 1.9e-15 from my own wiring: library primitives only, not the
  builder's script.
- The plan preceded every statistic, the word follows the pre-specified rule, and hygiene is clean.

**My cause verdict: SUPPORTED, carried by the share arm alone.**
- The share gap is established at B3 (z −4.02) and closes at matched granularity (B2 z +0.72, B4 k=35 z +0.23).
- The gain arm cannot discriminate (D1).
- The WORK gain gap the question starts from is not established in either harness: H-X z −1.60, and the record's own
  WORK comparators give z −0.95.
- Cause 1 therefore explains the **share** gap, not a WORK gain gap.

## Per-claim table (deciding claims)

| # | Claim (builder) | Own result | Verdict | Sev |
|---|---|---|---|---|
| 1 | Plan 0ccc014 committed before any statistic | Plan commit 0ccc014 at 12:15:21. Files under `mmlu_gap_work/` or `TaxoArena_tmp/mmlu_gap/` not newer than 12:15:21: **0** (find count). Output dir created 12:23:18. MATH part started ≈12:23:20 (log mtime 12:32:52 − 572 s), after runner c578c3c (12:23:10). Plan diff 0ccc014..9ea1d87 = one appended `[P1]` hunk | CONFIRMED | - |
| 2 | MMLU H-R B3 reproduces C-M1 WORK +0.0765 SE 0.0361 | Own re-aggregation of `parts/mmlu_hr.npz`: 0.0764891961 / 0.0360662673. `support_recut.json` draw 0: 0.07648919607361708 / 0.036066267266545 (gap < 1e-15). H-R B1 also equals the record's C-M2 (0.79786 / 0.13121) | CONFIRMED | - |
| 3 | MATH H-X L2 reproduces +0.124 SE 0.035 | Per-seed `leaf\|L2` and `leaf\|L1` equal GRANULARITY-WORK `seeds.csv` to 6 dp (5/5 seeds each). Own recompute: +0.124052 SE 0.034974, max per-item gap 1.2e-15. Run with the raw `fit_theta_slope` (no fallback wrapper), so "fallback 0" is confirmed too | CONFIRMED | - |
| 4 | MATH L0 +0.8665 (0.0875); L2 share 0.143 (0.030); L2a +0.856 / 0.987 | Own: L0 +0.8665 SE 0.0875; L2 share 0.1432 SE 0.0301; L2a +0.8556 SE 0.0875, share 0.9875 SE 0.0162; G(L2a\|L0) +0.5880. Per-item gaps ≤ 1.2e-15 | CONFIRMED | - |
| 5 | MMLU H-X B0 +3.004 (0.185), n 8,425, 79 models, 8,375 clusters | Own: +3.0042 SE 0.1850. Same n, models and cluster partition (bijection over 8,375 clusters). Per-item gap 1.1e-15 | CONFIRMED | - |
| 6 | MMLU H-X B2 +0.4996 (0.0523), share 0.166 (0.011); 34 cells; parse 1/14/6/4/32 | Own regex parse: 1/14/6/4/32, 34 cells. Own: +0.4996 SE 0.0523, share 0.1663 SE 0.0109, G(B2\|L0) +3.2506. Per-item gap 1.9e-15 | CONFIRMED | - |
| 7 | MMLU H-X B4 primary k=35 +0.452 (0.052), share 0.150 (0.010); seeds 0.39-0.50 | My merges, built from the plan text, equal the builder's recorded merges (5/5 seeds). Own: +0.4521 SE 0.0519, share 0.1505 SE 0.0101. Per seed +0.4600 / +0.4504 / +0.3875 / +0.5018 / +0.4607. Per-item gaps ≤ 1.3e-15 | CONFIRMED | - |
| 8 | MMLU H-X B3 +0.0575 (0.0227), share 0.019 (0.007) | Own: +0.0575 SE 0.0227, share 0.0191 SE 0.0068. Per-item gap 1.5e-15 (B1 too: +0.7884 / 0.2624) | CONFIRMED | - |
| 9 | z and word: M-B2 +5.97 / +0.72, M-B4 +5.24 / +0.23, gap −1.60 / −4.02 → SUPPORTED (UNINFORMATIVE) | Own z from my own rows: +5.970 / +0.724; +5.243 / +0.230; −1.595 / −4.024. The committed rule prints SUPPORTED + flag. Forking check: share-only or an AND rule gives **SUPPORTED with the gap established** (no flag); gain-only gives SUPPORTED + flag. The word is the same under every metric choice | CONFIRMED | - |
| 10 | "At ~35 cells MMLU's absolute gain is about 4 times larger" | 4.03x (B2) and 3.64x (B4). The gain scale differs by dataset: G(leaves\|L0) is 3.004 vs 0.867 (3.5x). The raw ratio mostly restates that scale; the share is the scale-free comparison | PARTLY (D2) | MEDIUM |
| 11 | MMLU-Pro L0 +1.241 (0.147); L1 +0.168 / 0.136; L2 −0.010 / −0.008 | Re-aggregated from the npz to the digit. L1 and L2 per-seed values equal GRANULARITY-WORK `mmlu_pro/seeds.csv` to 6 dp. L0 is descriptive (spot check only) | CONFIRMED | - |
| 12 | Within-category B4 k=35 +0.403 (0.048), share 0.134 (0.011) | Values reproduce, but the SE omits the merge-seed Monte Carlo error. Per-seed shares 0.081-0.197 (SD 0.051), so the MC SE is 0.023 and the total SE **0.025**, 2.4x the reported 0.011. For the deciding B4 primary k=35 the total SE is 0.012; z_share +0.225, word unchanged | PARTLY (D3) | LOW |
| 13 | Selftest 29/29; mutants 24/24 killed, control passes | Own re-run of an unmutated sandbox copy: 29 PASS, 0 FAIL, exit 0. `mutants.log` read whole: X1-X24 killed, X0 survives. Own mutants below | CONFIRMED | - |
| 14 | At most 3 processes, BLAS 1 | Fold-completion cadence: MATH in triples, MMLU in triples, MMLU-Pro in pairs (2 workers). MMLU-Pro (13:15:27-13:19:25) overlapped the single-process H-R (13:14:37-13:28:41): 3 processes in total | CONFIRMED | - |
| 15 | Read-only dirs untouched; outputs, backup, sync test | Files newer than 12:00: `mmlu_confirm` 0, `benchzoom_cache` 0. `mmlu_pro_more`: 30 newer files, all the live run's (0 named `*gap*`). Backup `SHA256SUMS_all` 18/18 OK and its full-tree sha256 listing equals the outputs. `test_execution_graph_sync` 33 passed; the guard's MODULES are `benchzoom.*` only and the branch touches 2 files (docs + example), so no graph entry is due. ruff clean. Worktree porcelain 0 lines | CONFIRMED | - |

**Support** (re-measured from the cache's own clusters):

| Dataset | Items / clusters | DEFF | n_eff |
|---|---|---|---|
| MMLU, H-X | 8,425 / 8,375 | 1.004-1.008 | 8,354-8,395 |
| MATH | 2,949 / 2,946 | 1.000-1.001 | about 2,947 |
| MMLU-Pro | 7,197 / 7,085 | 1.02-1.03 | 7,002-7,047 |

MDE80 = 2.80 x the SE of the MMLU−MATH difference:

| Comparison | Gain MDE80 | Share MDE80 |
|---|---|---|
| B2 | 0.176 | 0.090 |
| B4 | 0.175 | 0.089 |
| B3 | 0.117 | 0.086 |

All SEs are item-clustered with the roster fixed: the 79-, 69- and 23-model rosters enter no SE.

## Defects

- **D1 MEDIUM: the gain arm of the rule is near-vacuous at matched granularity.**
  - To "reach" MATH L2 on the gain, MMLU needs a gain ≥ −0.0018 (B2) or ≥ −0.0011 (B4). Any non-negative gain passes.
  - The gain contrast's MDE80 (0.176) exceeds MATH's whole gain (0.124).
  - The UNINFORMATIVE flag catches this only at B3 (bar +0.041).
  - The design came from the spec (gain OR share). The builder disclosed it in part ("readers should weigh the share
    reading").
  - Fix: state the result as "SUPPORTED on the share: B3 BELOW z −4.02; B2 and B4 REACH, z +0.72 / +0.23; the gain arm
    cannot discriminate". In any re-use, use a share-only equivalence margin fixed in advance instead of "within 2 SE".
- **D2 MEDIUM: the reading's "absolute gain about 4 times larger" is scale-confounded** (row 10). Fix: drop it, or quote
  it only beside G(leaves|L0) (3.004 vs 0.867). The share is exactly that normalisation.
- **D3 LOW: the B4 family SEs omit the merge-seed MC error** (row 12). Fix: report sqrt(SE_item² + SD_seed²/5). No word
  changes.
- **D4 LOW: matched granularity is by cell count, not by cell size or tree resolution.**
  - Items per cell: MMLU B2 248, B3 148; MATH L2 84.
  - Leaves per baseline cell: MMLU has 100 leaves (B2 2.9 per cell, B3 1.75). MATH has 36 leaves for 35 L2 cells (1.03).
    MMLU-Pro has 80 leaves for 91 cells (0.88).
  - MMLU leaves vs subjects (labels only): item-weighted subject purity 0.785; 43% of leaves are ≥ 0.9 pure; a subject
    spans a median of 4 leaves.
  - So "the leaves rediscover the subjects" holds predictively (share 0.019 over B3) but not as a partition.
  - Fix: add these to the caveats.
- **D5 LOW: the MMLU ladder wiring has no synthetic test** (the builder disclosed this gap).
  - Own mutants M1-M3 all SURVIVE the selftest.
  - Values on that path are checked only by the real run and by this review's recompute (rows 5-8, where they agree).
  - Fix: a selftest on a CData fixture asserting B2's parent (L1), B4 primary's parent (L0) and B2's cell key
    (subcategory x level).
- **D6 LOW: `parts/math_hx.json` carries no code state** (the field arrived in 49b18c0).
  - Blob `a6eda6cd` for that part rests on timing: commit c578c3c 12:23:10 < run start ≈12:23:20, and run end 12:32:52
    < commit 49b18c0 12:33:43.
  - The timing is consistent, and rows 3-4 confirm the values independently.
- **COSMETIC:**
  - The sensitivity block's flag says "in H-X" although its B3 comes from H-R (disclosed).
  - The report omits L2a_meter (+0.134, share 0.155), which is in `summary.txt`.

**Context (not a defect of this run):** MATH's registered L3a|L2, +0.259 SE 0.063, is 2.1x its WORK cross-fit value,
+0.124 SE 0.035. The vault/registered gain gap (MATH +0.259 vs MMLU vault +0.117) is therefore partly MATH's own
registered-vs-WORK difference, which this analysis does not address.

## Own mutants (deciding MMLU wiring; sandbox copies under `E:/TaxoArena_tmp/rev_gap_mut/`, `--selftest`, TMP redirected)

| id | change (one line) | result | decisive |
|---|---|---|---|
| M0 | control (unmutated copy) | 29 PASS / 0 FAIL | - |
| M1 | B2 reader parent "L1" → "L0" (`mmlu_baselines`) | SURVIVED (29/29 PASS) | yes (M-B2 value); only the recompute guards it |
| M2 | B4 primary parent "L0" → "L1" | SURVIVED (29/29 PASS) | yes (M-B4 value) |
| M3 | B2 cell key `subcat\|level` → `level` (5 cells) | SURVIVED (29/29 PASS) | yes (M-B2 value) |

## Commands (read-only on outputs and caches; at most 3 processes, BLAS 1; scripts in the reviewer's scratchpad)

```
git -C Z:/FAC/TUBerlin/benchzoom_wt_gap_baseline log --format='%h %cd %s' --date=iso master..HEAD ; git show --name-status --format= <c>   (4 commits, 2 paths)
git diff -U0 49b18c0 9ea1d87 -- examples/mmlu_gap_baseline.py | grep '^@@'      -> one hunk, docstring L39-L77
find E:/TaxoArena_tmp/mmlu_gap E:/benchzoom_demo/mmlu_gap_work ! -newermt '2026-10-22 12:15:21' | wc -l   -> 0
find E:/benchzoom_demo/mmlu_confirm -newermt '2026-10-22 12:00' | wc -l -> 0 ; E:/benchzoom_cache -> 0 ; both also 0 after my runs
python rev_gap.py math|mmlu   own wiring: own folds, own scipy clusters, own regex B2 parse, own merges, own item_pi, M.backbone/M.contexts/M.step
python -I rev_cmp.py math|mmlu   per-item max |diff| vs the builder's npz; cluster bijection; merges equality
python -I rev_agg.py   own cluster SE, delta-method ratio SE, z, DEFF, n_eff, MDE on parts/*.npz (all 4 parts)
python -I rev_mc.py    merge-seed MC error of the B4 families
python -I rev_labels.py   labels only: leaf/subject purity, leaf-string vs anc-leaf bijection (100/100/100), reads [0, 0]
sha256sum -c SHA256SUMS (13/13) ; sha256sum -c SHA256SUMS_all in the backup (18/18)
pytest tests/test_execution_graph_sync.py (33 passed) ; ruff check examples/mmlu_gap_baseline.py (clean)
```
