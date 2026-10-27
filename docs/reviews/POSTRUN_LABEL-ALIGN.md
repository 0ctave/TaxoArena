# POSTRUN review: LABEL-ALIGN (M3; do the axis leaves follow the declared fine labels? EXPLORATORY, labels only)

Authority: D-2026-10-22-2 (TaxoArena 875253bc). Reviewer: adversarial reviewer, 2026-10-23. Zero LLM calls. No response
file was opened by me: my allow-list audit (below) shows exactly which files were read. Reviewed: benchzoom branch `label-align`
(local, 0 remote branches contain c3bb8f9), 36b29be..c3bb8f9 on master 8610a5d (= merge-base). The run of record is at 32d85f7.
Script LF blob `634158a5` (= `git rev-parse 32d85f7:examples/label-align.py`; `meta.json` dirty ""). Power ran from blob
`2546197f` (= the 36b29be blob; untracked at the time, head 8610a5d). Tip blobs: script `3dfcee6f`, plan `a1a41a6c`,
test `566c810d`. The working tree is LF: `git hash-object` = the committed blob, and no CRLF rendering differs.
Outputs: `E:/benchzoom_demo/followups/label-align` (summary.txt sha256 d5700d64…; SHA256SUMS f102d005…).

## Verdict

**OUTCOME CONFIRMED (exploratory). The word "V5 INDICATED" stands. MERGEABLE (3 new files, src untouched).**
- Every deciding number reproduces from my own loaders and sklearn/scipy primitives, without the builder's functions.
  The cAMI point values agree to the 4th decimal, E0 to the 5th, and purity/cNMI to the 4th.
- My bootstrap uses its own seed, so the SEs differ within Monte Carlo error: 0.0042 / 0.0049 / 0.0050 against the
  builder's 0.0043 / 0.0051 / 0.0048. My z values are +57.0 / +44.7 against the builder's +55.0 / +45.3.
- The plan was committed before any real-data statistic. The word follows the pre-specified rule, both arms are
  powered, no response-bearing file was opened, and the branch touches only its own files.
- Substance: within the declared anchors, the leaves partly rebuild MMLU subject and MMLU-Pro src. On MATH they are
  nearly orthogonal to level. The non-ceiling-adjusted AMI does not produce this contrast: MATH has the HIGHEST
  attainable value (below).

## Per-claim table (deciding claims; WORK = PRIMARY)

| # | Claim (builder) | Own result | Verdict | Sev |
|---|---|---|---|---|
| 1 | Plan + runner 36b29be committed before any alignment statistic | Branch created 23:57:55. Plan commit 00:22:05, pin commit 32d85f7 00:22:14. Outputs mtime 00:24:58, so the run started about 00:22:30 (147.7 s). Before 00:22:05 there are only fixture selftests (00:18:05, 00:18:33, 00:20:15) and `--power` at 00:20:43, which forms marginals only (`margins()` L750-760 never builds the joint). Reflog: 3 commits, no amend or reset after creation. Plan diff 36b29be..c3bb8f9: 0 deleted lines, the [P1] bracket inserted. Script diff after the run: docstring and selftest only | CONFIRMED | - |
| 2 | Comparators all REPRODUCED (n 4,914/14,042/11,994; WORK 2,949/8,428/7,197; leaves 36/100/80; cells 35/57/91; 35/91 V2 cell sizes; 184 n_subjects; 11/20 cells ≥ 160) | Own loaders: all equal. WORK id-list shas equal the pins (math 5e66112a, mmlu_pro 5c05640d). The MMLU split was re-implemented: work 0ad5fd11, vault d3a0b5ce. n_subjects equal on 184/184 nodes. Cells ≥ 160: 11 / 20. Stronger than the size check: item-level fine label equals the V2 pickle's `fine` on 4,914/4,914 (MATH) and 11,994/11,994 (MMLU-Pro) | CONFIRMED | - |
| 3 | Deviation: MMLU-Pro src taken from the TIGER parquet instead of the scores parquet | Inert. TIGER src equals the record reader's src (V2 `fine`, built from the scores parquet) on 11,994/11,994 items. TIGER category equals the item category on all items | CONFIRMED | - |
| 4 | MATH WORK cAMI 0.0287 (SE 0.0043), 7 anchors, 36 leaves, 35 labels | 0.0287 (SE 0.0042), E0 0.02011, cNMI 0.0408, purity 0.3303 (null 0.2990, 200 draws) | CONFIRMED | - |
| 5 | MMLU WORK cAMI 0.3963 (SE 0.0051); 15 informative anchors, 8,222 items; engineering (87, 1 leaf) and geography (119, 1 label) excluded | 0.3963 (SE 0.0049), E0 0.01650, purity 0.7797 (null 0.4997). Same two excluded anchors (my anchor = the tree's own depth-1 node, 1:1 with the 17 subcategories). Keeping them gives 0.3950 | CONFIRMED | - |
| 6 | MMLU-Pro WORK cAMI 0.3207 (SE 0.0048), 14 anchors, 80 leaves, 91 labels | 0.3207 (SE 0.0050), E0 0.02884, purity 0.6018 (null 0.4188) | CONFIRMED | - |
| 7 | Rule (plan §4, both arms z > 2): MMLU−MATH +0.3676 z +55.0; MMLU-Pro−MATH +0.2921 z +45.3 → V5 INDICATED | +0.3676 (SE 0.0064, z +57.0); +0.2921 (SE 0.0065, z +44.7). Arithmetic from the run's SEs: sqrt(0.0051²+0.0043²) = 0.00667 → z 55.1; sqrt(0.0048²+0.0043²) = 0.00644 → z 45.3. Strict z > 2 on both arms gives INDICATED | CONFIRMED | - |
| 8 | Power: planned MDE80 0.0291/0.0297, realised 0.019/0.018, against Δ* 0.10 | Planned: 2.8416 × sqrt(0.009018² + 0.004878²) = 0.02913 and 2.8416 × sqrt(0.009018² + 0.005259²) = 0.02966. Realised 0.0190 / 0.0183; mine 0.0183 / 0.0186. No DEFF is named (D2). Re-measured proxy: DEFF 1.21 (MATH) and 1.99 (MMLU-Pro), from the rebuild spread over sub90 trees. At DEFF 2: z 39.0 / 32.0, MDE80 0.027 / 0.026. At DEFF 4: z 27.6 / 22.7 | CONFIRMED (Support re-derived) | LOW |
| 9 | ALL secondary gives the same word | Mine (B 300): z +77.1 / +55.4; builder +76.7 / +62.0. INDICATED either way | CONFIRMED | - |
| 10 | Guard: forbidden opens 0, vault reads 0, LLM calls 0 | Builder's `--check` loaders run under my allow-list audit hook plus wrapped parquet readers: 20 distinct data paths opened (37 audit entries, counting the wrapped-reader duplicates), all read-only. They are the MATH/cais/TIGER item parquets, 3 axis pickles, the C-M1 tree.csv, 2 V2 tree.csv, 2 vault id lists, the HF token file and 2 temp dirs. No response-bearing file. The axis pickles' item frames hold only id/text/question/subject/options. The guard is a deny-list (D1) | CONFIRMED | LOW |
| 11 | P1-P4 HELD | 0.0287 < 0.05; 0.3963 > 0.20; 0.3207 > 0.10; word = INDICATED | CONFIRMED | - |
| 12 | Selftest 76/76; mutants 48/48; full pytest 886 passed / 1 skipped | Selftest re-run: 76 PASS, 0 FAIL. Branch test 1 passed; execution-graph sync 33 passed (venv). Builder's full-suite log: 886 passed, 1 skipped, 4 deselected (slow/network markers); not re-run, src diff 0 files (D4). Own mutants 7/8 killed, control passes | CONFIRMED | - |
| 13 | X35 incident: fixture files were written under the output folder; folder removed; files of record unchanged | All 5 output files and SHA256SUMS carry the run's mtime 00:24:58 and match the run's own SHA256SUMS (5/5 OK). SHA256SUMS_all 9/9 OK before and after my runs. The output folder lists 9 entries (no `x/`). Backup: SHA256SUMS_all 12/12 OK, SHA256SUMS 5/5 | CONFIRMED | - |

## Descriptive checks (spot; not deciding)
- Construction robustness (cAMI on WORK, other axis_v1 builds):
  - MATH seeds 1-4 are identical to seed 0 (0.0287). sub90 reps: 0.0260-0.0308, SD 0.0020.
  - MMLU-Pro seeds 1-4: 0.3207-0.3226. sub90 reps: 0.3005-0.3123, SD 0.0048. They have fewer leaves (67-71), so the
    level sits lower.
  - No MMLU rebuilds exist.
- Ceiling: the block-aligned (sorted pairing) cAMI under the real WORK marginals is MATH 0.740, MMLU 0.614 and
  MMLU-Pro 0.667. The observed value is 4% / 64% / 48% of it. The marginals favour MATH, so "AMI not ceiling-adjusted"
  cannot have produced the contrast. The builder's planted rho 0.5 says the same (MATH 0.162 > MMLU 0.126).
- One-anchor identity: own pooled cAMI = sklearn AMI (arithmetic) to 8e-16.

## What the result licenses, and what it does not
- **Licenses** (exploratory, WORK, item labels only): within every declared anchor, the axis partition overlaps the
  declared fine label strongly on MMLU (subject) and MMLU-Pro (src), and barely on MATH (level). By the pre-specified rule
  a label-orthogonal V5 is the indicated next variant, if one is wanted.
- **Does not license:**
  - (a) That label re-discovery CAUSES the smaller MMLU/MMLU-Pro gain. No response was read, and alignment is not
    gain.
  - (b) That a V5 would gain anything.
  - (c) A like-for-like dataset contrast. MATH's fine label is a difficulty tag; the others are topical/source labels.
    The arms therefore confound dataset with label kind, and nothing here says the MATH leaves are orthogonal to a
    topical sub-label, because MATH has none declared.
  - (d) Anything on the vault or on fresh items.
  - (e) A registered result.

## Defects (none blocking)
- D1 LOW: the open guard is a deny-list. "Forbidden opens 0" certifies the 14 listed roots only. Mutant R7 removes the
  `E:/benchzoom_cache/hf` root and the selftest does not notice. Not decisive, because my allow-list audit found no
  response-bearing open. Fix: write the list of opened data paths into `meta.json` (an allow-list record), or assert
  `FORBIDDEN_ROOTS` against a registered set in the selftest.
- D2 LOW: plan §5 (Support) names no DEFF and no source. The item bootstrap ignores tree-construction variance and
  content twins. My re-measured proxy is DEFF ≤ 2.0; the weaker arm keeps z > 2 for any DEFF below (45.3/2)² ≈ 513. Fix: in later plans, state a
  rebuild-spread DEFF beside the bootstrap SE.
- D3 LOW: the deviation's comparator (91 cell sizes) cannot detect src swaps within a category. My item-level check
  closes this here. Fix: compare against the V2 pickle's `fine` item by item, which reads no response file.
- D4 LOW: `pytest_full.txt` (01:07:25) does not record the HEAD it ran on. Fix: print `git rev-parse HEAD` into the log.
- Note: the ALL secondary reads vault items' item-side labels (level/subject/src). These are metadata, not
  responses, and the trees of record were built on all items. "Vault reads 0" refers to responses.

## Own mutants (sandbox copies under `E:/TaxoArena_tmp/label_align_review/mut/<id>`; OUT and SANDBOX redirected; `--selftest`)
R0 control → passes. R1 `z > Z_LINE` → `abs(z) > Z_LINE` → killed (S7 arm below MATH), decisive. R2 informative `and` → `or`
→ killed (S5), decisive. R3 Hbar = max(hl, hf) → killed (S1 sklearn AMI), decisive. R4 z denominator = max(sa, sb) → killed
(S7 z 1.9), decisive. R5 blocks ignore the WORK mask → killed (S1 analyse(work)), decisive. R6 half-size bootstrap → killed
(S6), not decisive. R7 drop the `E:/benchzoom_cache/hf` forbidden root → SURVIVED (D1), not decisive. R8 UNDERPOWERED flag
inverted → killed (S7), not decisive. Output files of record: 9/9 OK after the mutant run.

## Commands (scratch scripts in the session scratchpad `…/scratchpad/la/`; all reads `rb`/parquet, no writes outside E:/TaxoArena_tmp)
```
git -C benchzoom_wt_label-align diff --name-status master...HEAD | wc -l        # 3 (all A); -- src | wc -l -> 0
git log --format='%h %cd' ; git reflog label-align ; ls -la --time-style=full-iso E:/benchzoom_demo/followups/label-align
git rev-parse 32d85f7:examples/label-align.py ; git hash-object examples/label-align.py ; file examples/label-align.py
python -I indep.py 1000        # own loaders + sklearn mutual_info_score / expected_mutual_information / scipy entropy;
                               # item-level V2 `fine` equality; pinned id shas; cAMI, SE (B 1000 within anchor), z, MDE80
python -I robust.py            # axis_v1 seeds 0-4 + sub90 reps 1-5; block-aligned ceiling; purity null (200)
python -I extra.py             # DEFF proxy from sub90 spread; z/MDE80 at DEFF 1-4; excluded-anchor sensitivity
PYTHONPATH=src python audit_check.py   # builder --check under an allow-list audit hook + wrapped parquet readers
python examples/label-align.py --selftest   # 76 PASS / 0 FAIL (TMP/TEMP/TMPDIR -> E:/TaxoArena_tmp/label_align_review)
python -I mutants_review.py    # R0-R8 above
.venv/Scripts/python -m pytest -q tests/test_label_align.py tests/test_execution_graph_sync.py   # 1 + 33 passed
sha256sum -c SHA256SUMS_all (outputs 9/9 before and after; backup 12/12)
```
