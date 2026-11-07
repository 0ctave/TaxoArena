# POSTRUN review: ROSTER-STRUCTURE-METER (lead #6; roster size and strong-model concentration of the meter's cell structure; exploratory, WORK rows only)

Authority: D-2026-11-06-3 (`docs/agents/author_decisions/2026-11-06.md`), leads file `docs/agents/plans/2026-11-06_leads.md`
"### 6. ROSTER-STRUCTURE-METER (rank 6)" (b42d58ef). Reviewer: adversarial reviewer, 2026-11-07. I made zero LLM calls.
What I read: the run's saved parts, summaries and logs (`E:/benchzoom_demo/followups/roster-structure-meter{,_rerun}/`;
`np.load` / `json.load` only; part mtimes the same before and after), NEST-METER's parts npz (sha256 = its SHA256SUMS),
`weak_half.json` (sha256 1308ca67 = the pin), the builder's scratch area `E:/TaxoArena_tmp/roster-structure-meter/`.
Vault / RESERVED / sealed rows I read: 0 (no loader called by me). At most 3 processes, BLAS 1. My scripts are in the
scratchpad `.../7c10e5cb-.../scratchpad/rsm/` (`recompute.py`, `repro.py`, `fragility.py`, `own_mutants.py`). My
sandboxes are in `E:/TaxoArena_tmp/rsm_review_20261107/`. Nothing was deleted.

Reviewed: benchzoom branch `roster-structure-meter` (worktree `Z:/FAC/TUBerlin/benchzoom_wt_roster-structure-meter`), 4d08a3d..9b65440.
It adds 4 new files (`git diff --name-only master...HEAD | wc -l` = 4; `grep -c '^src/'` = 0, so `docs/execution_graph.md`
owes nothing). Merge base = master = 4d08a3d (fast-forward). No other local branch touches the 4 paths. The pending
review-fixes 06456b2 changes `examples/nest-meter.py`, which is one of the runner's DEPS; it inserts selftest and docstring
lines only (+50 / -0), so no conflict and no run path changes.
- Pins at the tip (LF of record; `git rev-parse 9b65440:<path>`; 0 CR bytes in each working file, `git ls-files --eol`
  w/lf, so there is no separate CRLF rendering): plan `blob:2200b675` (sha256-lf16:e090437f63d531e0), runner `blob:d78996c4`
  (sha256-lf16:4f3d30765fb61d50), mutant spec `blob:d0b83dca` (sha256-lf16:980915047d5834ae), tests `blob:098421fd`
  (sha256-lf16:8c76d51209bc7b97). Run of record: runner `blob:d5d99e1e` (sha256-lf16:069e89a70e252534) = `1074ea6:` (all
  three parts, `--analyze` and the second run; part records `code_at_start` = `code` = {d5d99e1e, 1074ea6, dirty ''}).
  Plan at the run = `c39fcd3` `blob:b71ab989`. The tip runner is AST-identical to d5d99e1e outside the module docstring
  (`ast.dump` equal). The tip's edits are insertions only (`git diff --numstat`: plan 79 / 0, runner 10 / 0).

## Verdict

- **ROSTER-STRUCTURE-METER: OUTCOME CONFIRMED (exploratory; WORK rows only; one V0 per dataset; MMLU-Pro one fold seed),
  with qualifiers Q1-Q2 (MEDIUM) and Q3-Q8 (LOW).** Every deciding number reproduces from the saved per-item arrays with
  my own code: all 25 E points and SE_word, all 5 C_str points and SE_word, and every one of the 30 words, the 17
  UNDERPOWERED flags, the 4 meter-beside flips and the 10 prediction scores (largest |difference| 4.4e-16). The
  reproduction comparisons and the second-run comparison reproduce byte for byte.
- **Two hand-back sentences are not licensed as worded.** "the 23-vs-320 difference on record is not a roster-size
  effect" is REFUTED as worded (Q1). "small rosters read more structure in the same models" is PARTLY right (Q2): the
  numbers are right, the reading is not.
- **MERGEABLE: YES**, as a fast-forward of 4 new files with 0 `src/` changes. The qualifiers go into an insertion-only
  bracket [P2] of the plan, or into the registrar's record verbatim. No rerun is needed. No BLOCKER. AUTHOR DECISIONS
  NEEDED: none.

## Per-claim table (deciding claims; G x 1e-3 nats per cell; SE_word = SE_leaf (+) draw MC (E) or (+) model term (C_str))

| # | Claim (builder) | Own result | Verdict | Sev |
|---|---|---|---|---|
| 1 | The plan c39fcd3 came before every statistic on responses | reflog: branch reset at 4d08a3d 14:18:49, c39fcd3 14:49:33 (plan only), 1074ea6 16:26:49, 9b65440 03:11:26. The first real part (MATH) started at about 16:27:07: part written 16:45:38, harness 1,109 s, load 2 s, `head` 1074ea6 in its record. Before 16:27 the scratch area holds selftest logs, debug scripts and string patches only. The only scratch files that mention a loader are `patch2.py` / `patch3.py`, which edit the runner text and read no data. | CONFIRMED (artefact evidence) | - |
| 2 | Data object: WORK rows only; 0 vault / reserved / sealed reads | n 2,949 x 69 / 3,457 x 128 / 7,197 x 320 (+ REC23 23). `guard_reads_end` [0] / [0] / [0, 0]. BBH `reserved_reads` 0, `work_values` 442,496 = 3,457 x 128, nan 0. Roster ids_sha: MMLU-Pro f7fd0db5 (= the plan's), BBH c47b3eb5. The axis pickle and marks are sha-pinned in each record. | CONFIRMED in the guard's sense (Q7) | LOW |
| 3 | REPRODUCED (bit-equal) on all three datasets (RN, RN23, RW) | own byte comparison (dtype, shape, `tobytes`): MATH FULL cont L1\|L0 and L2\|L1 = NEST-METER, leaf and clusters equal; BBH the same; MMLU-Pro REC23 the same; RW: 160 WEAK models = weak_half.json's list, median 0.29936 equal | CONFIRMED; the MMLU-Pro scope is narrower than the hand-back's wording (Q5) | LOW |
| 4 | The second run is bit-equal (2,249 arrays, records, summary, readouts) | own: 2,249 / 2,249 arrays byte-equal; part records equal outside the volatile fields; summary.txt 887b1a22 and readouts.csv 04eb65b2 equal in both runs (meta.json differs: timestamps, not in the plan's list). `sha256sum -c`: run 9 / 9, rerun 9 / 9, backup 30 / 30 (31 files including SHA256SUMS; `record/` = the output directory, `find \| sort` diff empty) | CONFIRMED | - |
| 5 | Of the 30 worded cells, 6 HIGHER, 0 LOWER / STRONG / WEAK, 24 NEITHER (17 UNDERPOWERED); meter SE beside 4 of 30 | own recomputation from the npz (own CR1 cluster SE, own sets from the plan's permutation stream and the median of `acc`, both = the json): identical words and flags | CONFIRMED | - |
| 6 | L3a\|L2: no fit effect of roster size detected (15 cells) | MMLU-Pro E: R 160 -0.0006 (0.0023), R 80 -0.0057 (0.0031), R 40 -0.0025 (0.0064), R 20 -0.0040 (0.0151), R 10 -0.0089 (0.0580), R 5 +0.1550 (0.1840). MATH and BBH as in [P1]. All 15 NEITHER. | CONFIRMED | - |
| 6b | "on WORK, the 23-vs-320 difference on record is not a roster-size effect (P3 failed)" | At R 20, E's ±2 SE_word interval is [-0.034, +0.026]; DEFF_leaf 2.92, n_eff 2,464, MDE80 0.058. It contains -0.024, the WORK-side gap implied by the record (my arithmetic: granularity_work's 23-model -0.010, as quoted in the plan, minus this FULL +0.0142; two different runs). The 23 of record are not a random draw. P3 FAILED is a point outcome: G_own +0.0111 vs G_full +0.0152, ratio 0.735. | REFUTED as worded (Q1) | MEDIUM |
| 7 | L2\|L1: 6 HIGHER (z 3.35-7.27): MMLU-Pro R <= 40, MATH R 34 / 17 | MMLU-Pro +0.1917 (0.0572), +0.4083 (0.1027), +0.9341 (0.2076), +2.3350 (0.5546); MATH +0.4300 (0.0979), +1.3990 (0.1925) | numbers CONFIRMED; reading PARTLY (Q2, Q4) | MEDIUM |
| 8 | C_str MMLU-Pro L3a\|L2 +0.0600 (SE 0.0234, z 2.56), NEITHER (U); the meter SE beside reads STRONG | +0.0600; SE_word 0.0234 (items 0.0180 (+) model 0.0151); DEFF_leaf 2.17, n_eff 3,314, 80 leaves; MDE80 0.0900 > max(+0.0442, 0.0158); meter-beside z 3.09 STRONG. Descriptive spot checks: C_info +0.4609 (SE_leaf 0.1385), Spearman +0.256, Q1-Q4 -0.0294 / -0.0022 / +0.0238 / +0.0647 | CONFIRMED; "the strong half carries more" = by point only (Q3) | LOW |
| 9 | 6 of 10 predictions HELD (P4-P6, P8-P10); P1-P3 and P7 FAILED | own scoring against plan section 8: P1 (E(R 5) +0.1550 > 0), P2, P3 (0.735 > 0.5) and P7 (6 HIGHER) FAILED. P4 +0.0600, P5 0.1338 > 0.1211, P6 0.0051 < 0.1019 with -0.2757, P8 -0.0184, P9 5 / 5 NEITHER, P10 +0.0314 HELD. | CONFIRMED | - |
| 10 | Mutants 115 / 115 killed | r1 (copy d2cafbaf): 113 / 115. r2 (copy f70700f4 = d5d99e1e minus the docstring table: `diff` shows one insertion hunk) killed X11, X12 and X13, and the controls pass. The r1 -> r2 change is the S4 block only and adds checks. Own mutants: 8 / 8 killed, control passes (below). | CONFIRMED | - |
| 11 | The suite passes: 1,038 passed, 1 skipped, 15 deselected, 0 failed | `suite.log`: those counts (972.86 s); 1,034 at master (D-2026-11-06-1) + 4 new fast tests = 1,038. Own run of `tests/test_roster_structure_meter.py` including slow: 5 passed (108.8 s). I did not rerun the full suite: the delta changes no `src/`. | CONFIRMED (log + own module run) | - |

## Qualifiers and defects (each with its fix)

- **Q1 (MEDIUM): the P3 / 23-vs-320 wording.** The plan's own section 9 rule, fixed before the data, says a NEITHER reads
  "not detected at 3 SE (MDE80 x)", never "no roster effect". The hand-back's "is not a roster-size effect" breaks that
  rule. E(20) cannot exclude a fit effect of the size of the WORK-side gap implied by the record, and the record's 23 are
  a specific roster, not a random 20. [P1]'s "reads 0.73 ... of the full fit's leaf structure" is a point ratio with E's
  SE 0.0151 against G_full 0.0152. **Fix:** quote "at the leaf level no fit effect of roster size is detected at 3 SE_word
  (MMLU-Pro R 20: E -0.0040, SE_word 0.0151, MDE80 0.058; random 20-model draws); the record's 23-vs-320 gap is not
  reproduced as a size reading; composition (which 23) is untested (REC23 reproduction-only)". Never quote "is not a
  roster-size effect" or the 0.73 without its SE.
- **Q2 (MEDIUM): "small rosters read more structure".** E compares a sub-roster's own fit, read against its OWN backbone
  (LOMO difficulties from R_k - 1 models), with the full fit on the same models. L1|L0 grows the same way, descriptively:
  MMLU-Pro +0.02 at R 160 up to +3.95 at R 5, MATH up to +2.38 at R 8. That fits a larger gain over a weaker backbone,
  not more cell structure. **Fix:** quote "the label-level gain G(L2|L1) that a small roster's own fit reads exceeds the
  full fit's reading of the same models (6 cells HIGHER); the mechanism (a weaker backbone) is untested". Registrar note:
  this implies that label-level meter gains are not comparable across roster sizes. That is a caveat for any small-roster
  G (for example R 5 designs), stated as a WORK-side, exploratory reading.
- **Q3 (LOW): C_str wording.** "the strong half carries more leaf structure" holds by point only. The word is NEITHER (U)
  at 3 SE_word. STRONG appears only under the meter SE beside, which is not the word's SE (C-7: the beside SE is never
  the word). **Fix:** prefix "by point", as [P1] already does.
- **Q4 (LOW): 2 of the 6 HIGHER words rest on a 5-draw MC term.** The multiple of the MC term at which |z| falls to 3:
  MMLU-Pro L2|L1 R 40 x1.25, MATH L2|L1 R 34 x1.62; the other four x1.92-4.52. Under chi-square with 4 df, P(true sigma >=
  1.25 s) = 0.37 and P(>= 1.5 s) = 0.22. MMLU-Pro's four HIGHER cells come from the same 5 nested permutations, so they are
  not independent. The plan's section 11 says the draw term is noisy. **Fix:** quote "6 HIGHER (4 robust to a 1.9x larger
  draw term; nested draws)".
- **Q5 (LOW): MMLU-Pro reproduction scope.** RN23 checks REC23's arrays and RW checks the WEAK list. The 320-model arm
  that produces every MMLU-Pro statistic has no external comparator; it has only the second run, which uses the same code.
  **Fix:** quote "REPRODUCED (bit-equal) per the plan's section 6 checks", not "all three match NEST-METER".
- **Q6 (LOW): the clean-tree pin is partial.** `DEPS` omits four modules that every part executes at import time:
  `reread-steps.py` (tau-grid, module level), `label-align.py` (bbh-work, module level), `mmlu_gap_baseline.py`
  (flat-compare, tau-grid) and `mmlu_confirm_items.py` (tau-cont-all). There is no impact here: the branch changes only
  its 4 files, the worktree is clean (`git status --porcelain` 0 lines), and RN is bit-equal. **Fix** (next runner):
  check the dirty state over all of `examples/` + `src`, or over the `__file__` of every loaded module.
- **Q7 (LOW): vault rows in memory.** `swap_roster` takes `roster_matrix(d0.ids, ...)`, which covers every meter row
  including the vault rows, and seals it in a VaultGuard (reads 0, never armed). It calls `read_census` / `roster_matrix`
  directly, not `load_more`'s READY-1 gate (plan section 2 discloses this). **Fix:** build the census matrix on the WORK
  ids only, so vault values never enter the process. "Read 0" holds in the VaultGuard sense, the convention of record.
- **Q8 (LOW): Support.** Section 9 is present, with its source (PLANTED-POWER x1.4-1.65) and MDE80, and the MATH and BBH
  arithmetic reproduces (0.035 x 1.4-1.65 = 0.049-0.058; x 3.8416 = 0.19-0.22). MMLU-Pro's planned upper end 0.025 is not
  derivable: 0.017-0.018 x sqrt(2,880 / 7,197) x 1.4-1.65 = 0.0151-0.0188. The draw MC term was not planned, and it
  dominates at small R (MATH L2|L1 R 8: MC 0.645 vs items 0.253). The realised SE_leaf / SE_content of G(FULL|ALL) is 1.93
  for MATH (above the plan), 1.51 for MMLU-Pro and 1.46 for BBH. **Fix:** none owed for this readout; carry both points
  into any registration that reuses the design.
- The builder's ruff note is confirmed: 10 findings (for example B007 at L2043), none of which changes behaviour.

## Own mutants (sandbox copies of examples/ + src/; `--selftest` with BZ_MUTANT_NO_POOL=1; 3 at a time; ~94 s each)

| id | change | result | decisive |
|---|---|---|---|
| O0 | control (unmutated) | passes | - |
| O1 | E draws unpaired (`full` rotated by one draw) | killed (S5) | yes (E words) |
| O2 | `dstat` item term from draw 0 only | killed (S2) | yes (E SE) |
| O3 | reproduction word with `any` over the lines | killed (S4) | yes (withhold gate) |
| O4 | reproduction pairs `REF_KEYS[:1]` (L2\|L1 dropped) | killed (S4) | yes |
| O5 | `check_guard` with `all` instead of `any` | killed (S7) | yes (guard) |
| O6 | E MDE80 on SE_items (no MC) | killed (S6) | flag only |
| O7 | STRONG / WEAK split at the mean, not the median | killed (S1) | yes (C_str) |
| O8 | `set_mean` divides by the set size (unobserved cells as 0) | killed (S2) | yes |

## Commands (outputs in the per-claim table)

```
git -C <wt> log --format='%h %ad' --date=iso-strict -3; git -C <wt> reflog --date=iso | head
git -C <wt> diff --name-only master...HEAD | wc -l          # 4;  ... | grep -c '^src/'  # 0
git -C <wt> diff --numstat c39fcd3 9b65440 -- docs/roster-structure-meter.md   # 79 0
git -C <wt> rev-parse 1074ea6:examples/roster-structure-meter.py              # d5d99e1e...
git -C <wt> ls-files --eol <4 paths>; tr -cd '\r' < <path> | wc -c            # w/lf, 0
python -I scratchpad/rsm/recompute.py   # every E / C_str point + SE_word + word + flag vs the json; predictions
python -I scratchpad/rsm/repro.py       # RN / RN23 / RW bytes vs NEST-METER; 2,249 arrays rerun; summary / readouts sha
python -I scratchpad/rsm/fragility.py   # SE ratios, MC multipliers, chi2(4), E(20) interval vs the record gap
sha256sum -c SHA256SUMS                 # run 9/9, rerun 9/9, backup 30/30
python -I scratchpad/rsm/own_mutants.py # O0-O8 (log E:/TaxoArena_tmp/rsm_review_20261107/own_mutants.log)
PYTHONPATH=src .venv/Scripts/python.exe -m pytest tests/test_roster_structure_meter.py -m "slow or not slow"  # 5 passed
diff mut/r2/X0/examples/roster-structure-meter.py <(git show 1074ea6:examples/roster-structure-meter.py)  # 1 hunk at L44
grep -nE "_load_module|^import (mmlu_gap_baseline|mmlu_confirm_items)" examples/{tau-grid,bbh-work,flat-compare,tau-cont-all}.py
```
