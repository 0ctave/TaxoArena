# POSTRUN_PLANTED-POWER: adversarial post-run review (benchzoom `planted-power`, 35b2724..7e7773a)

2026-10-28. Authority D-2026-10-27-2 (TaxoArena 2e2513a5). EXPLORATORY build, MATH WORK rows only, simulated responses.
Reviewer: zero LLM calls; vault / reserved reads 0 (one WORK load through the guarded `fc.load_math_pro("math")`,
vault reads 0, to refit the generator); at most 3 compute processes, BLAS 1. Outputs of record unchanged: 8 pinned files
sha256-equal before and after, `sha256sum -c SHA256SUMS` 397/397, 0 files newer than SHA256SUMS_all. Reviewer scripts
(not committed) in `E:/TaxoArena_tmp/review_planted_power/`, sha256-16 below.

Object: plan cffa234 (2026-10-27 15:41:22), code 81b49a1 (17:25:16), runner `blob:f9a7997381fd64742ee56e9309b8d008385b90b1`
(LF; the working file is LF, `git hash-object` = tip blob 9d01b785, so there is no CRLF rendering), tip 7e7773a (plan
[P1] + 8 docstring lines; `git diff 81b49a1..7e7773a -- examples/` is the docstring only). Outputs: design 17:26:03,
repro 17:44:04, replicates 17:48:30 to 08:12:43, analyze 08:13; all 390 replicates plus design / repro / analyze carry
f9a79973 @ 81b49a1, dirty "".

## Verdict

**OUTCOME CONFIRMED (exploratory, with qualifiers Q1-Q5). MERGEABLE.** The branch adds 3 new files; 0 files under
`src/` or `docs/execution_graph.md` (`git diff --name-only 35b2724..7e7773a -- src docs/execution_graph.md | wc -l` = 0);
`git merge-tree --write-tree master planted-power` is clean onto master 452f365. Before anyone quotes the result:
quote it per Q1 and Q3, and add an insertion-only [P2] bracket.

Rule words after review:
- Reproduction: **REPRODUCED** (confirmed to the digit).
- `METER SE (pre-specified rule, MATH, NONE + C1 0.10, 4 readers)`: **NOT CALIBRATED**, confirmed as computed. The
  printed worst pair (RND at TREE_010, 2.332) is inflated by degenerate replicates (Q1). In substance the word is
  **NOT CALIBRATED on the 9 degeneracy-free pairs at C1 0.10**: ratios 1.382-1.648, every bootstrap lower bound >= 1.09,
  worst non-degenerate pair K at TREE_010, 1.648.
- PR1 HELD; PR2 HELD (near-forced, Q1); PR3 FAILED; PR4 FAILED; PR5 HELD; PR6 HELD: all confirmed.

## Per-claim table (deciding claims)

| # | claim (builder) | reviewer's number / check | verdict | sev |
|---|---|---|---|---|
| C1 | REPRODUCED: per-item max abs diff 0 (V0, KM0, RND0, L3k); C1(V0) +0.1093 SE 0.0316 | repro.json: maxdiff 0 x4, clusters equal, reference math.npz sha matches FLAT-COMPARE SHA256SUMS (re-checked: OK). In addition, 2 stored replicates (NONE r000, TREE_010 r000) re-run from design.npz: `array_equal` True for all 4 readers | CONFIRMED | - |
| C2 | generator and planted fields as in plan 3.1-3.3 | generator refitted on WORK: eta0 max abs diff 0.0; template = WORK NaN pattern, 0 responses; parts and clusters equal. Fields rebuilt from `[PP_SEED,1,code]` with the reviewer's own w0-weighted projections (in a different order): max abs (own - stored) 5.8e-12 / 5.2e-12 / 3.4e-11 (TREE / FLAT / KNN); weighted cell means <= 1e-12 before scaling; RMS 1; 0 values off the observed cells | CONFIRMED | - |
| C3 | truths: T_att(matched; s) = target; T_or | own continuous-tau^2 reference reader (scipy bounded search) and own 40-NN: max abs (own - recorded) 1.2e-6 over 12 cells x 4 readers; T_or equal to 4 decimals in all 12 | CONFIRMED | - |
| C4 | the planted truth is recovered at infinite replicates (brief) | fixture (900 items, 30 models, 12 V0 cells): exact-likelihood Monte Carlo of the reference reader with real Bernoulli draws gives 0.1007 +- 0.0004 vs T_att 0.1000, and 0.3006 +- 0.0008 vs 0.3000 (4,000 draws each) | CONFIRMED for the truth; the meter's reading of it: Q3 | - |
| C5 | the null has 0 planted effect | NONE: s 0, T_or 0, T_att 0 in design.json; `simulate()` adds no field for NONE; NONE r000 re-run bit-exact; mean G at NONE -0.0019 to -0.0029 | CONFIRMED | - |
| C6 | the ratio uses the SE the meter reports | replicate SE = `crossfit.paired_delta`(per-item values, content clusters) x 1e3, the same form as `meter.contrast_stats` `se_x1e3`; own cluster-robust SE: max abs dSE 1.4e-17, max abs dG 0 (390 x 4) | CONFIRMED (for the one-seed meter; Q2) | - |
| C7 | 16 ratios 1.32-2.33; matched V0 1.63 [1.36, 1.85], K 1.55 [1.24, 1.83], N 1.38 [1.12, 1.61] | 1.322-2.332, identical to 3 decimals; the bootstrap reproduced exactly on the same stream; an alternative seed with an interpolated bootstrap moves the bounds by <= 0.06 | CONFIRMED | - |
| C8 | rule word NOT CALIBRATED | 16/16 pairs out of band; but P(CALIBRATED) is about 0.004 at the realised degenerate shares even if the SE were exact (Q1) | CONFIRMED, near-forced | HIGH (Q1) |
| C9 | false positives 0/60 for every reader under both rules | 0/60 3-SE and 0/60 [R2] (own level_word logic, leave-one-out q95); Wilson upper bound 0.06 | CONFIRMED | - |
| C10 | power at C1 0.10, matched reader, 3-SE / [R2]: 0.62/0.50, 0.62/0.60, 0.84/0.64; 1.00 at 0.30 | 31/25, 31/30, 42/32 of 50; 20/20 at 0.30 | CONFIRMED | - |
| C11 | bias: matched mean G / T_att 1.03-1.29; 5-33% of T_or | 1.031-1.290; 0.052-0.333 | CONFIRMED | - |
| C12 | PR1-PR6 | own scoring: HELD, HELD, FAILED (0.62 / 0.62 / 0.84), FAILED (all 9 above 1.0), HELD (max RND rate 0, max abs mean G 0.0035), HELD | CONFIRMED | - |
| C13 | the plan preceded every statistic | plan 15:41 < trial design 15:56 < code 17:25 < design 17:26 < first replicate 17:48; the code did not change after any output (all at f9a79973) | CONFIRMED (disclosure Q5) | LOW |
| C14 | selftest 39/39; mutants 68/68 + 5/5; ruff clean | selftest re-run 39/39 (sandbox); `pytest tests/test_planted_power.py -m "slow or not slow"`: 3 passed; ruff: all checks passed; own mutants 3/3 killed (below). Full suite not re-run (the branch only adds new files) | CONFIRMED | - |
| C15 | backup: 403 files, 397/397 and 402/402 | 403 files; `sha256sum -c` 397 OK and 402 OK; SHA256SUMS byte-identical to the output's | CONFIRMED | - |

## Qualifiers and defects (each with its fix)

- **Q1 HIGH: the CALIBRATED arm was nearly unreachable.** The ALL-replicates ratio counts the degenerate replicates
  (G = 0, SE = 0) in the mean SE. With degenerate share d, the ratio is inflated by about 1/sqrt(1 - d) before any
  error in the SE: V0 at NONE 1.257, RND at NONE 1.309, RND in the 0.10 cells 1.291-1.313. At the realised shares
  (NONE 22 / 17 / 6 / 25 of 60; RND 21 / 20 / 20 of 50), P(CALIBRATED | the non-degenerate SE is exact, pairs
  independent) = 0.004; without degeneracy it would be 0.675 (per pair 0.973 at R 50, 0.984 at R 60). The selftest's
  own fixture ("1.398 out of band, non-degenerate 0.997 in band") shows the choice was deliberate. It is pre-specified,
  so the word stands, but the 16-pair word and PR2 say nothing beyond the 9 degeneracy-free pairs.
  Fix: quote "x1.38-1.65 on the 9 degeneracy-free pairs at C1 0.10 (bootstrap lower bounds 1.09-1.36)"; mark the NONE
  and RND ratios "degeneracy-inflated (non-degenerate 0.91-1.69)"; do not quote "worst x2.33". Any future rule: compute
  the ratio on the non-degenerate replicates with the degenerate count beside it, and state P(CALIBRATED | calibrated)
  for the whole family in the support section.
- **Q2 LOW (was a candidate MEDIUM; resolved by the reviewer's run): one fold seed vs the 5-seed meter of record.**
  Fold seeds 1-4 were re-run on TREE_010 r000-r011 (240 tasks). Factor = (5-seed ratio) / (1-seed ratio), R 12, bootstrap:
  V0 1.15 [0.82, 1.45], K 1.04 [0.77, 1.40], N 1.54 [0.85, 2.63], RND 1.73 [1.03, 3.63]. The between-seed correlation of
  G is 0.85 / 0.70 / 0.75 / 0.03, and the 5-seed SE is 10-16% below the 1-seed SE. So averaging over seeds does not
  shrink the understatement, and the result extends to the 5-seed meter at least for V0 and K. Fix: write "one-fold-seed
  meter (5-seed check: factor about 1 or above)".
- **Q3 MEDIUM: T_att is a reference scale, not "what an ideal reader could attain".** On MATH the meter reads 1.03-1.29x
  T_att. On the reviewer's fixture it reads below it: TREE_010 0.048 +- 0.010 of 0.100, TREE_030 0.257 +- 0.018 of
  0.300, null V0 -0.022 (R 150). The truth itself is right (C4), so PR4's failure is about how the meter relates to a
  fixed-tau^2 reference reader, and that relation depends on the design. Fix: call T_att "the fixed-tau^2 reference
  reader"; read "C1 0.10" in the power curves as "a planted effect the meter reads as 0.11-0.13 on MATH". The fixture
  also reproduces the direction of the SE result independently (V0 ratio 1.31 at TREE_010, 1.39 at TREE_030, R 150;
  degenerate count not tracked).
- **Q4 LOW:** the report's "a lower bound on the understatement" holds only in expectation over item sets; the plan's
  section 7 wording ("understates the sampling SD even without item sampling") is the defensible one. Fix: use the
  plan's wording.
- **Q5 LOW: two steps are not disclosed in [P1].** A trial `--design` ran at 15:56 (after the plan, before the code
  commit; numbers identical to the run of record; `E:/TaxoArena_tmp/planted_power/trial`), and a partial `--analyze`
  ran mid-run on 11 replicates (`.../acheck`, 18:14). Neither was followed by a code change, so there is no forking
  path. Fix: one disclosure line in [P2].

## What it licenses / does not license

Licenses (exploratory; MATH WORK; responses simulated from a WORK-fitted backbone plus a planted field; items fixed):
- the meter's content-cluster SE of C1 understates the response-redraw SD of its own estimate by x1.38-1.65 for V0, K
  and N at a planted effect of the record's reading scale (Q2: the 5-seed meter is no better);
- no false positive at the null in 60 draws for any reader under either rule;
- matched-structure detection at C1 0.10: 0.62 / 0.62 / 0.84 (3-SE). The matched structure is planted exactly, so
  this is a best case;
- WORK-side selection only: grounds to plan future registrations with a cell-aware or inflated SE, and to size n with
  a design effect of about 1.9-2.7 (ratio squared).

Does not license: switching any deciding estimator. The meter SE stays the deciding SE wherever it is registered
(D-2026-10-27-5 B, "Meter SE, cell-aware beside", stands until the author changes it), and no recorded verdict is
re-read with an inflated SE. It also does not license: any statement about fresh data, the vault or the reserved side
(no item sampling; the generator is not the real data-generating process); MMLU or another benchmark; T_att as an
attainability bound; a calibration statement for the NONE or RND pairs.

## Own mutants (sandbox copies of `examples/`, TMP / TEMP / TMPDIR / BZ_SANDBOX redirected; killed = exit != 0 or a FAIL line)

Y0 control (unmutated): 39/39 PASS. Y1 PR4 upper bar 1.0 -> 1.3: killed (S6 predictions branches), decisive (would turn
PR4 into HELD). Y2 mean SE -> RMS SE: killed (S6 ratio = SD / MEAN SE), decisive. Y3 mean SE over non-zero SEs only:
killed (S6 ALL replicates), decisive for 7 of 16 pairs.

## Commands (all read-only on the outputs of record; scripts in E:/TaxoArena_tmp/review_planted_power)

```
git -C benchzoom_wt_planted-power log --format='%h %cd %s' --date=iso-strict master..planted-power ; git diff --name-status 35b2724..7e7773a
git rev-parse 81b49a1:examples/planted-power.py ; git hash-object examples/planted-power.py ; git merge-tree --write-tree master planted-power
python -I recompute.py      # 1e475dc96b5a180c: 390 replicate files -> G/SE (own cluster SE), ratios, bootstrap, det3, [R2], rule, PR1-PR6
python -I designcheck.py    # b102e4fa865651fd: T_att (continuous tau^2, own 40-NN) and T_or vs design.json (its b-proxy orth check is void: b has ties)
python -I gencheck.py       # e282ab4970399ee8: WORK refit eta0 = stored; fields rebuilt from seeds; orthogonality with the exact b
python seedcheck.py NONE,TREE_010 1 0 ; python seedcheck.py TREE_010 12 1,2,3,4   # a67b411e131be953 (2 workers)
python -I seedanalysis.py TREE_010   # e49b69edfff43361: 5-seed vs 1-seed ratios
python -I fixture.py 150 TREE_030,TREE_010,NONE   # c8fcf4fae18bdb46: exact-likelihood reference-reader MC; meter on a fixture
python -I mut/make.py ; examples/planted-power.py --selftest per Y0-Y3   # 759bc11c41fea17a
pytest tests/test_planted_power.py -m "slow or not slow"  -> 3 passed ; ruff check -> all passed
sha256sum -c pre_sha.txt (8 OK) ; sha256sum -c SHA256SUMS (397 OK) ; backup: 403 files, 397 OK, 402 OK
```
