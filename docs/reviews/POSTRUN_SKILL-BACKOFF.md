# POSTRUN review: SKILL-BACKOFF (test 2: per-cell skill estimates with and without back-off; exploratory, WORK rows)

Authority: D-2026-11-03-1 (`docs/agents/author_decisions/2026-11-03.md`; test 2 of D-2026-11-02-1), exploratory WORK-row
readout, zero LLM calls, no reserved/vault side (D-2026-10-20-4), CPU only. Reviewer: adversarial reviewer, 2026-11-03.
Zero LLM calls by me. Responses read by me: the run's saved per-item arrays, and WORK rows loaded through NEST-METER's
loaders (the runner's `load_real`, guard printed: [0] / MMLU [0, 0] at the end of every load) for the MATH re-fit and the
4-dataset fold/cell recount. RESERVED / vault rows read by me: 0. At most 3 processes, BLAS 1. Scripts, mutant sandboxes,
pytest basetemp: `E:/TaxoArena_tmp/review_skill-backoff/`. Writes elsewhere: 0 (`find E:/benchzoom_demo E:/benchzoom_cache
<worktree> -newer <stamp> -type f | wc -l` = 0 after each of my loads; worktree `git status --porcelain | wc -l` = 0).

Reviewed: benchzoom branch `skill-backoff` (local; worktree `Z:/FAC/TUBerlin/benchzoom_wt_skill-backoff`), f9a8985..73fde4e:
4 new files (`git diff --name-only f9a8985 73fde4e | wc -l` = 4; `... -- src | wc -l` = 0, so `docs/execution_graph.md`
owes nothing); master = f9a8985 = the branch base (fast-forward).
- Pins at tip (LF of record; `git hash-object` of the working file = `git rev-parse 73fde4e:<path>`; 0 CR bytes in each
  working file (`tr -cd '\r' | wc -c`), so there is no separate CRLF rendering): plan `blob:a682dfab` (sha256-lf16:8b03e095b8906e44),
  runner `blob:a09bebfa` (sha256-lf16:c6df5560c8c10476), mutant spec `blob:bd063ea3` (sha256-lf16:6e9802ebaf309436), tests
  `blob:e18d3222` (sha256-lf16:5ce3e48f5720b6bf). Run of record: runner `blob:729a93b5` at HEAD bbda88e, `dirty ""` in
  `code_at_start` and `code` of all four parts and in meta.json `analyze_code`; tip runner AST-identical to 729a93b5
  outside the module docstring (`ast.dump` equal; `git diff --numstat bbda88e 73fde4e`: runner 9/0, plan 47/0).
- Outputs: `sha256sum -c SHA256SUMS` 11/11 OK (summary.txt 4a4c64c2); backup `E:/TaxoArena_backup_2026-11-03_skill-backoff`:
  24 files = 23 listed + SHA256SUMS, 23/23 OK, parts' hashes equal to the output dir's.

## Verdict

- **SKILL-BACKOFF: OUTCOME CONFIRMED (exploratory, WORK rows, the four rosters, V0's leaf granularity), with qualifiers
  Q1-Q3 (MEDIUM) and Q4-Q7 (LOW).** All 64 words (8 contrasts x 2 regimes x 4 datasets) and the 4 B_lab words recomputed from
  the saved per-item arrays with my own CR1, seed pairing and Monte Carlo term: 0 mismatches. An independent
  re-implementation of plan sections 3-4 (my own folds, recursion, inner-fold tau choice, log-loss) reproduces the run's
  per-item losses on MATH bit-equal for 19 primary units and to 1e-13 for 3 secondary units. P1-P10 re-scored identically.
- **merge_ok: YES (MERGEABLE)**, fast-forward, 4 new files, 0 `src/`. The corrections below go into a plan bracket [P3]
  (insertion only) and the registrar's record; no rerun is needed.
- No BLOCKER. AUTHOR DECISIONS NEEDED: none.

## Per-claim table (deciding claims; WORK: MATH 2,949 x 69, MMLU-Pro 7,197 x 23, BBH 3,457 x 128, MMLU 8,425 x 79)

| # | Claim (builder) | Own result | Verdict | Sev |
|---|---|---|---|---|
| 1 | Plan a629375 preceded every statistic on responses; the resumed run is one code state | a629375 01:25:46, plan only, parent f9a8985 (reflog: worktree born at f9a8985 00:56, then only a629375, 8e7e925, bbda88e, 73fde4e). Pre-plan scratch `time_backbone.py` 00:59, `time_task.py` 01:07, `plan_sim.py` 01:15: synthetic `rng.random` matrices only, no loader call (read whole). Output dir born 12:16:08, after bbda88e 12:15:58. Of 2,101 npz in the builder's scratch, 0 are > 500 kB (all fixtures). All four parts and analyze at blob 729a93b5 / bbda88e / dirty "". [P1] committed in 8e7e925 (11:28, 16/0 insertion only), before the run | CONFIRMED | - |
| 2 | Code implements the plan; bbda88e changed no deciding path | bbda88e: 6 hunks, the docstring (L44) and 5 inside `selftest()` (`git diff -U0 8e7e925 bbda88e \| grep '^@@'`). My re-implementation from the plan text (own `group_folds` with streams [20261021, s] and [20261103, 1, s, f]; root / label LIGHT / tau recursion; collapsed = parent; tau grid with inf, ties to the smaller; clip 1e-6; per-item mean over observed models; mean over 5 fold seeds) matches the run's npz on MATH: max \|diff\| **0.0** for LABELS, TREE-RAW, TREE-BL, TREE-BO, KF-BO x5, RND-BO x5, BKMA-BO x5 (primary). For LABELS-b, TREE-RAW-b and TREE-BO-b (backbone `meter.backbone`, my offsets) it is **9.9e-14**. Not re-fitted: BKMA-BL and BKMA-SM (descriptive), and the other datasets' fits (same code path) | CONFIRMED | - |
| 3 | tau chosen on inner folds of the training rows only | My refit asserts that no outer test row is in any inner fit or score row. The losses are bit-equal, so the run's choice is the inner-only choice. MATH primary tau* lists equal: TREE-BO 11 x 500, 13 x 1000, 1 x inf (median 1000); RND-BO 22 at 1000, 96 inf (median inf); KF-BO median 100; BKMA-BO median 500, 15 at 1000 | CONFIRMED | - |
| 4 | Every test item's cell was seen in training ("unseen 0 for every arm") | My folds x every arm's leaf cells (V0 leaf; NEST-METER's KF_s / RND_s / BKMA_s@L, which every arm's leaf equals) on **all four** datasets and 25 tasks: 0 test items and 0 (item, model) pairs whose cell has no training answer. Min WORK cell: TREE 44-55, KF 17-50, RND 44-55, BKMA 23-39. The run's own count is not pinned by its selftest (R2, Q5) | CONFIRMED | - |
| 5 | Partitions = NEST-METER's (RP 18/18 on all four) | NEST-METER's SHA256SUMS 11/11 OK. Its clusters and leaf arrays equal the run's and my load's (4/4). TREE@L = V0 leaf (4/4). BKMA_s chain ends = BKMA@L (5/5, MATH). KF / RND / BKMA nested in the label (MATH 15/15). MATH losses fitted on NEST-METER's own stored KF_s / RND_s cells are bit-equal to the run's | CONFIRMED | - |
| 6 | Words of record (hand-back table and [P2]) | Every D, SE_content, SE_leaf, SE_label, z and word to its printed digit. Max gap vs readouts.csv is 4.6e-6 scaled (the csv's 6 significant digits). E.g. MATH Z_bo +10.2755, SE_word 1.6016 [content], z 6.42 BETTER; MMLU V_tree +15.1429, SE_word 3.1795 [leaf], z 4.76 BETTER; MMLU-Pro Z_bo +1.1674, SE_word 0.4726, z 2.47 NEITHER | CONFIRMED | - |
| 7 | P1 FAILED, P2-P9 HELD, P10 FAILED | Re-scored from the npz (taus from the part JSONs; MATH taus also from my refit): identical. P7 also holds 3/3 without BBH (Q6) | CONFIRMED | - |
| 8 | Z_bo by size: S vs L 18.28 / 5.91, 1.74 / 0.90, 8.08 / 0, 6.93 / 0.74 | Identical, items and leaves per bin as printed | CONFIRMED | - |
| 9 | Support beside every word | DEFF, n_eff and MDE80 recomputed (MATH Z_hier: DEFF 1.12, n_eff 2,624, MDE80 0.752; Z_hier MDE80 0.75 / 2.13 / 0.78 / 4.54). The planning simulation (section 10) understated the leaf DEFF on MMLU-Pro: realised 9.2-13.6 for arm vs LABELS, against SE_leaf about 2 x SE_content planned. The words use the realised SEs | CONFIRMED | - |
| 10 | 0 LLM calls; vault / reserved 0 | Runner: 0 matches for HTTP / LLM clients (grep count). `guard_reads_end` [0] in every part ([0, 0] MMLU); NEST-METER's loaders and guards as CONFIRMED in POSTRUN 2f84191d | CONFIRMED | - |
| 11 | Tests and mutants: 1034 passed; 7 + 1 skill-backoff; S1-S8; 116/116 | Mine: `tests/test_skill_backoff.py` incl. slow, 8 passed; `--selftest` rc 0, S1-S8 PASS. Full suite not re-run (0 `src/` files changed; builder's suite.log 14:17 is after tip 13:59). Mutant logs: r2 112 killed, r3 4 killed, controls survive | CONFIRMED | - |
| 12 | RA (BBH, beside) REPRODUCED 5.6e-17 | Read from the part JSON only, not recomputed (beside, non-deciding) | UNDETERMINED | LOW |

## Own mutants (sandbox copies under `E:/TaxoArena_tmp/review_skill-backoff/mut/<id>`; the copy's `--selftest`)

| id | change | result | decisive |
|---|---|---|---|
| R0 | control (unmutated) | passes | - |
| R1 | inner folds not content-grouped | killed (S3) | yes |
| R5 | outer folds not stratified by label | killed (S3) | yes |
| R6 | BKMA-BO without its internal split nodes (= BKMA-BL) | killed (S4) | yes |
| R2 | unseen-cell count over all rows (test included) | SURVIVED | no: my recount gives 0 on all four |
| R3 | `nest-meter.cstat`: the partition-seed MC term dropped | SURVIVED | no: my recompute carries the MC term and matches. NEST-METER's own X26/X27 kill it upstream |
| R4 | `nest-meter.cstat`: seeded A side reads seed 0 only | SURVIVED | no: same as R3 (NEST-METER's X28 covers the B side) |

## What the run licenses (exploratory, WORK side; selection caveats of plan section 12)

- Licensed: on MATH, BBH and MMLU, shrinking per-model leaf rates toward the label predicts held-out WORK responses better
  than the raw leaf rates (Z_bo BETTER; MMLU-Pro z 2.47 NEITHER). Which hierarchy the estimates back off along (V0 vs
  nested bisecting k-means) is not detected (Z_hier NEITHER; MDE80 0.75 / 2.13 / 0.78 / 4.54). Flat KF vs nested BKMA is not
  detected (Z_nest NEITHER). Random cells of V0's sizes carry nothing. The backbone dwarfs every cell effect (B_lab
  +47 to +207, z >= 9.7).
- Not licensed: any fresh, vault or registered claim; "equal" hierarchies; "k-means cells beat the tree's cells" (Q3); "the
  tree's internal levels help" (Q2); a general "raw leaf rates are unusable" (Q1); any per-cell board, interval or profile
  (closed line PROFILE-TREE-ROBUST / KEY-SUBANCHOR-SCALE); replacing V0 for BZ-AXIS-CONFIRM-FRESH.

## Qualifiers and defects (each with its fix; all for a [P3] bracket and the registrar's record)

- **Q1 MEDIUM, reading (1) generalises from MATH.** "the raw V0 leaf rate is not a usable skill estimate on its own" holds
  on MATH only (V_raw -10.03, z -5.8). It is BETTER on MMLU (+12.60, z 3.84; label SE beside NEITHER) and NEITHER on
  MMLU-Pro (+9.50) and BBH (-2.01). Fix: "on MATH the raw leaf rate is worse than the label rate; on MMLU better (label SE
  NEITHER); NEITHER on MMLU-Pro and BBH."
- **Q2 MEDIUM, back-off = shrinkage toward the label, not the hierarchy.** Label-only shrinkage TREE-BL - TREE-RAW
  (descriptive) is at least Z_bo: MATH +10.69 vs +10.28; MMLU-Pro +1.73 (SE_word 0.32) vs +1.17 (NEITHER); BBH equal; MMLU
  +1.97 vs +2.55. The internal levels of a hierarchy shrunk at one common tau cost on MATH and MMLU-Pro, by point and
  descriptively: TREE-BO - TREE-BL -0.41 (SE_word 0.15) / -0.57 (0.30); BKMA-BO - BKMA-BL -0.49 (0.20) / -0.59 (0.27). On MMLU
  they read +0.57 (0.30) / +0.12 (0.35). Z_hier and Z_nest therefore compare hierarchies through a multi-level, one-tau
  shrinkage whose internal levels are not shown to help (TREE-BACKOFF C-1). Fix: readings (1) and (2) carry this sentence;
  "nesting adds nothing detectable" reads "is not detected under one common tau".
- **Q3 MEDIUM, V_kf BETTER on MATH and MMLU-Pro is thin, and it is not a cells comparison.** KF cells cross V0 leaves, so
  SE_word's clusterings do not contain KF's own cell dependence. With SE clustered by KF_s cell, or two-way by V0 leaf x
  KF_s (max over s, MC term added), z is 3.11 (MATH) and 3.03 (MMLU-Pro): still >= 3, by 0.11 and 0.03 SE. The label SE
  beside reads NEITHER on both. "V_kf BETTER, V_tree NEITHER" also compares one-level shrinkage (KF-BO) with four-level
  shrinkage at one tau (TREE-BO). Fix: [P3] states the KF-cell z and the depth difference; no "k-means cells better" reading.
- **Q4 LOW, label-SE disagreements in the secondary are not stated.** [P2] lists them for the primary only. In the
  secondary, the label SE beside reads NEITHER at 6 BETTER words: MATH V_kf-b; MMLU-Pro V_bkma-b and V_kf-b; MMLU V_tree-b,
  V_bkma-b and V_kf-b. Fix: one sentence in [P3].
- **Q5 LOW, selftest gaps (R2-R4).** Fix (new commit, selftest only, no rerun): an S3 fixture with a leaf wholly in one
  test fold, asserting unseen > 0. An S5 by-hand value of `cstat` with seeded arms that differ by seed (pins the MC term
  and the A-side pairing inside this runner's own selftest).
- **Q6 LOW, P7's BBH cell is zero by construction.** BBH's L bin is 862 items / 6 single-leaf labels where every arm is
  LABELS, so Z_bo = 0 there. P7 holds 3/3 without BBH. Fix: say so beside P7.
- **Q7 LOW, [P1](b) weakens RA's sha check** to a beside DISCREPANCY instead of a refusal. RA is beside-only and its sha
  matched in the run. No action beyond the record.

## Commands (reviewer scripts in `E:/TaxoArena_tmp/review_skill-backoff/`; Python = benchzoom `.venv`, `-I` where no import)

```
git -C <wt> log --format='%h %ad %s' --date=iso master..HEAD ; git -C <wt> reflog --date=iso ; git -C <wt> diff --numstat a629375 8e7e925 -- docs/skill-backoff.md
git -C <wt> diff -U0 8e7e925 bbda88e -- examples/skill-backoff.py | grep '^@@' ; git -C <wt> diff --name-only f9a8985 73fde4e -- src | wc -l   # 0
ls -la --time-style=full-iso E:/benchzoom_demo/followups/skill-backoff E:/TaxoArena_tmp/skill-backoff ; find E:/TaxoArena_tmp/skill-backoff -name '*.npz' -size +500k | wc -l   # 0
sha256sum -c SHA256SUMS (outputs 11/11; backup 23/23; nest-meter 11/11)
python -I recompute_npz.py      # 64 words + B_lab from the npz: 0 word mismatches, max scaled gap 4.6e-6 -> recompute_npz.log
python -I bins_preds.py         # bins, P1-P10, V_tree-b / V_tree 0.691 / 0.016 / 0.407 / 0.087 -> bins_preds.log
python -I kf_cluster_se.py      # Q3: V_kf z by KF_s cell 3.11 / 3.06 / 1.15 / 4.95; two-way 3.11 / 3.03 / 1.15 / 4.89
PYTHONPATH=<wt>/src REVIEW_DS=math python refit_math.py    # 3 workers; max |mine - run| 0.0 primary, 9.9e-14 secondary -> refit_math.log
PYTHONPATH=<wt>/src python unseen_all.py math mmlu_pro bbh mmlu   # unseen 0 / 0 on all four -> unseen_all.log
python rev_mutants.py           # R0-R6 -> rev_mutants.json, mutsand/<id>/selftest.log
PYTHONPATH=src python -m pytest tests/test_skill_backoff.py -m "slow or not slow" --basetemp=<scratch>   # 8 passed
PYTHONPATH=<wt>/src python <wt>/examples/skill-backoff.py --selftest   # rc 0, S1-S8 PASS (sandbox TMP)
```
