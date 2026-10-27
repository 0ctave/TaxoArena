# POSTRUN review: BZ-GRANULARITY-WORK (EXPLORATORY, WORK split only)

Authority: `docs/agents/author_decisions/2026-10-20.md` D-2026-10-20-3 / -4. Reviewer: adversarial reviewer, 2026-10-20.
Zero API calls. The vault guard was never armed: in my reproduction `VaultGuard.arm` and `.open` were replaced by a
sentinel that raises, and it never fired. Reviewed: benchzoom `examples/granularity_work.py` and
`tests/test_granularity_work.py`, commits ca361d9..0aba06e. Run of record: script LF blob `b5874a2c` at 19250ae.
0aba06e adds 10 docstring lines only (LF blob `7afb0a8a`; tests LF blob `ff640a87`; the working tree equals HEAD,
`git diff` shows 0 lines). Outputs: `E:/benchzoom_demo/granularity_work/{math,mmlu_pro}`.

## Verdict

**VALID as exploratory output.** The harness is sound: no fold leakage, no vault row read, the meter's own readers,
and every deciding number reproduces (max gap 4.9e-7 on MATH, 2.1e-6 on MMLU-Pro). Four of the six claim groups may
go into post 1 as exploratory, worded as below. **SOLID vs CONTINUUM is REFUTED as a contrast** (HIGH): its SE treats
items as the sampling unit, but the claim is about splits. At the split level the 3 SOLID splits are indistinguishable
from any 3 of the 29 splits. **"Single-split gains sum +0.060" must not be quoted** (MEDIUM): the node contrast is not
local to its split.

## Per-claim table (deciding claims)

| # | Claim | Own result | Verdict | Sev |
|---|---|---|---|---|
| 1 | MATH G(L3a\|L2) +0.124 SE 0.035 | +0.12405 SE 0.03497 (own cluster SE 0.0350); DEFF 1.001 (2,946 clusters / 2,949 items); n_eff 2,947; MDE80 = 2.80 x SE = 0.098; z 3.55; per-seed +0.106..+0.150 | CONFIRMED | - |
| 2 | no fold leakage | 0 content clusters split across folds in 5 seeds x 2 datasets; fold sizes 586-593 / 1,428-1,448; tests X1/X2/X11 killed | CONFIRMED | - |
| 3 | no vault row touched | arm/open sentinel never raised; Y = `guard.masked()[fit]`, reads 0; n = 2,949 / 7,197 = WORK; E: listing of 4,123 files (path, size, mtime) identical before and after (`diff` 0 lines) | CONFIRMED | - |
| 4 | same backbone, shrinkage and tau^2 selection as the meter | `l2_contexts` = `M.backbone` + `M.contexts` + `M.step(rule "cv")`; `step2d` = `M.step` on a shared label (tests pass, 20/20 + 19/19); L3a\|L2 tau^2 per fold {0.02, 0.04} (vault fit: 0.04) | CONFIRMED | - |
| 5 | SOLID (3) -0.001 vs CONTINUUM (26) +0.042 per item-split, diff -0.043 SE 0.009 | point estimate reproduced; **split-level jackknife SE 0.028** (z 1.55); permuting which 3 of 29 splits are SOLID gives P(diff <= obs) = **0.32** (3,654 relabelings); the SOLID splits rank 12, 14 and 24 of 29 by per-item gain; 13 of 29 splits have per-item gain <= 0 | REFUTED as a contrast | HIGH |
| 6 | single-split gains sum +0.060 vs full +0.124 | G_node includes items OUTSIDE the split: the split's reader gets its own tau^2, which moves the category-cell offsets outside s. CONTINUUM inside +0.0935, outside **-0.0336** (max \|outside item pi\| 5.58); inside-only sum over all splits +0.093 | PARTLY (definition defect) | MEDIUM |
| 7 | depth curve over L2: 0 / +0.055 / +0.133 / +0.154 / +0.124 | reproduced to 1e-6; d1 = 0 by construction (category is part of L2); **d4 - d5 = +0.030 SE 0.009** (finest level loses); d3 - d2 = +0.078 SE 0.028 | CONFIRMED (add d4 > d5) | MEDIUM (wording) |
| 8 | after difficulty + length +0.109 SE 0.032; 19/36 leaves positive | +0.1093 SE 0.0316; L3a - (L3a+diff+len) = +0.015 SE 0.008. Per-model difficulty alone removes nothing (+0.125). The **leaf-mean-difficulty control removes 27%: +0.090 SE 0.028**, difference +0.034 SE 0.009. 19/36 positive (all 19 stay positive by construction of the count); the top 5 leaves carry +0.110 of +0.124 | CONFIRMED, incomplete | MEDIUM |
| 9 | synthetic difficulty-only: 6% left at MATH size, 43% at MMLU-Pro, difficulty-matched null weak (53%) | meta.json: MATH +diff 0.057, +leafdiff 0.107, null_dec 0.532; MMLU-Pro 0.431 / 0.079 / 0.882. One strength (synthetic G +3.88 = 31x the real effect), one functional form (per-model quadratic in b), 1 seed, R 20 | CONFIRMED as stated; narrow calibration | MEDIUM |
| 10 | pruning: collapsed - full -0.013 SE 0.024 | taken from pruned.csv (0.1107 - 0.1241 = -0.0133); nested pass not re-run (spot check only) | CONFIRMED (internal) | LOW |
| 11 | MMLU-Pro: all depths <= 0 over L2, +0.168 SE 0.055 over L1 | L3a\|L2 -0.0098 SE 0.0212 (DEFF 1.03, n_eff 7,002, MDE80 0.059: powered null); depths -0.010 / -0.011 / -0.002 / -0.010, d1 0. L3a\|L1 +0.1682 SE 0.0555. **But L2\|L1 (the declared source label) = +1.043 SE 0.120**: the leaves recover about 1/6 of it | CONFIRMED (needs the L2\|L1 context) | MEDIUM (wording) |
| 12 | damped-Newton fallback leaves converged values unchanged (8 MMLU-Pro, 0 MATH) | by construction the library value is returned when finite and stationary. Own check: damped = library to 2.8e-8 on 376 random converged fits; damped stationary (scaled gradient 1.1e-9) on the 24 where the library is singular. My no-nest re-runs: 0 fallbacks on both datasets, so the 8 are in nested inner fits only and touch only MMLU-Pro claim 10-type numbers | CONFIRMED | - |
| 13 | the mutant incident left nothing behind | `find E:/benchzoom_demo E:/benchzoom_cache -newermt 13:21` = only granularity_work/{math,mmlu_pro}; `sha256sum -c` 10/10 in each dir; backup 22/22 (SHA256SUMS_backup) and 10/10 in each dir; no stray python processes (all 16 running were my own runs) | CONFIRMED | - |

## Sentences allowed in post 1 (each labelled "exploratory, work split only")

- A1 (claim 1): "On the work split (5 content-grouped folds x 5 seeds, leaves built on all items' text), the axis
  leaves add +0.12 x 10^-3 nats per cell over subject x level (SE 0.035). The registered held-out read gave +0.26
  (SE 0.063)."
- A2 (claim 7): "The gain appears at depth 2-3 and peaks at depth 4 (+0.15, SE 0.036); the finest level gives back
  about 0.03 (SE 0.009)." Do not write "deeper is better".
- A3 (claims 8, 9): "Controlling for each model's difficulty curve and item length leaves +0.11 (SE 0.032).
  Controlling for each leaf's average difficulty leaves +0.09 (SE 0.028). On synthetic difficulty-only data of the
  same size, the difficulty control removes about 94% of a pure difficulty effect." Never on MMLU-Pro (the control
  removes only 57% at 23 models). Do not cite the difficulty-matched null as evidence.
- A4 (claim 5, replacing the contrast): "No single split reaches 2 SE. The gain sits in a handful of splits
  (Prealgebra, Counting & Probability, Geometry, Algebra; the top 5 leaves carry almost all of it). The three splits
  with a clear text axis add nothing measurable, but three splits are too few to compare them with the rest."
- A5 (claim 10): "Pruning the tree to the splits that pay off in nested cross-fitting does not improve it
  (collapsed - full -0.013, SE 0.024)."
- A6 (claim 11): "On MMLU-Pro the leaves add nothing over subject x source at any depth (-0.010, SE 0.021). Over
  subject alone they add +0.17 (SE 0.055), about a sixth of what the declared source label adds (+1.04)."
- NOT allowed: "SOLID splits carry less gain than continuum regions (-0.043, SE 0.009)"; "single-split gains sum to
  +0.06 of +0.12"; "19 of 36 leaves survive the controls" as evidence (half the leaves are positive under noise too).

## Defects

- D1 (HIGH): the SOLID - CONTINUUM SE (`mark_table`) is item-clustered, but the marks are fixed per split. Fix:
  split-level inference (permute marks over splits, or jackknife over splits) and print it beside the item SE.
- D2 (MEDIUM): `node_labels` leaves the outside of s as category cells, yet each reader selects its own tau^2, so
  outside items carry nonzero pi. Fix: offsets only inside s, with the outside held at the L2 eta, or report the
  inside-only sum.
- D3 (MEDIUM): the control calibration uses one strength at 31x the real effect and one functional form. Fix:
  calibrate at the real-size G and with a leaf-mean (step) difficulty form, and quote leafdiff beside diff+len.
- D4 (LOW): own mutant G1 survives (diff-bin edges taken from all rows rather than `c.fit`). It is non-decisive: the
  edges come from LOMO b, so no response leaks.
- D5 (LOW): the summary line "still positive after difficulty+length 19" cannot exceed the positive count, so it
  reads like a test. Fix: print the after-control positive count unconditionally.

## Own mutants (sandbox git copy of 0aba06e, TMP redirected; control 20/20 pass)

G1 `diff_bins` edges from all rows: survived (non-decisive). G2 `leafdiff_k` always 10: killed. G3 per-item value =
seed 0 only (no seed averaging): killed.

## Commands

```
git archive 0aba06e -> scratch sbB; git init; pytest tests/test_granularity_work.py tests/test_meter_axis.py (39 passed); --selftest PASS/PASS
scratchpad/drv.py <ds> <w> sbB: load_real + group_folds cluster check + run_dataset(n_seeds 5, R 1, nest False), vault arm/open -> raise
scratchpad/ana.py <ds>: record vs reproduction (controls/depth/nodes/marks), own cluster SE, DEFF, MDE80, paired diffs, inside/outside node pi, split jackknife
python on nodes.csv: split-level permutation (itertools.combinations 29 choose 3; mmlu 20,000 draws)
scratchpad/l2l1.py <ds>: G(L2|L1), G(L1|L0) on the same folds (MATH 0.456 / 0.993; MMLU-Pro 1.043 / 1.845)
damped vs irt.fit_theta_slope on 400 random fits; find -printf '%p %s %T@' before/after (4,123 files, diff 0)
sha256sum -c SHA256SUMS (math, mmlu_pro, backup dirs) and SHA256SUMS_backup (22/22)
```
