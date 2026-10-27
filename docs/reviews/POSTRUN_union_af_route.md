# POSTRUN — UNION-AF-ROUTE (RP13): the readout of union_af_route.py --run

Reviewer: adversarial-reviewer, 2026-10-03. Zero calls, no JVM. Object: `experiment_results/archv2/union_af_route/outcome.txt`
(232 lines, sha256 e50a8e0fa267db967981fb03320902c238fff505f00b1088d49c3c3a6596cd08), written by blob bf3f17db at main
c6ef6370 from the inputs under `.../inputs/` (POSTBUILD_union_af_route.md). Console: scratchpad `rp13_run.log`.
Registrations: prog L22627-L22653 and L23093-L23116, with the one-cell amendment L23660-L23667 and the C-S1/C-S2 brackets
(L23098, L23664; d3653625, committed 15:16, before the run at 15:51).

## Verdict: VALID

Every deciding number reproduces from my own scripts. The outcome was written once; the console carries every outcome line.
The chips: **U1 HELD (thin)**; **U2 / F-TAX L-1 NOT FIRED (by support)**; **U3a and U3b NOT EQUIVALENT**; **AK1 and AK2
UNDETERMINED**; **F-AK FIRES (not better), under the mirrored rule**; F-U1 not fired. Two qualifiers must travel with the words:
- **(Q1)** F-AK's fire depends on C-S1: under the registered nearest-of-all rule (descriptive) it would miss by 0.0002.
- **(Q2)** U3b is a measured LOSS against declared labels, not parity and not "no difference".

## Per-claim table (my number against the outcome's)

| # | claim | outcome | mine (independent) | verdict | sev |
|---|---|---|---|---|---|
| N | Deciding set | 5,907 / 5,404; AK 6,139 / 5,628, TRAIN 12,334 | 5,907 / 5,404 from eval_view `response` (mc6, roster 18, UNUSABLE_CELL, MATH-FIX overlay, all 18 cells usable); bundle 6,139 / 5,628 / 12,334 | CONFIRMED | — |
| A | Arm accuracies | best 0.6049, declared 0.6316, AF 0.6201, K0-K4 0.6271 / 0.6227 / 0.6213 / 0.6259 / 0.6262 | identical to 4 dp (frozen scratch policy sha 8d68018c… × af_cells / k_cells × key) | CONFIRMED | — |
| I | IDENTITY C1 | +2.67pp [+1.46, +3.89] | C1 point 0.02675 | CONFIRMED | — |
| U1 | G_AF | +1.52pp (0.01524), two-stage [+0.14, +2.91] → HELD | 0.01524 | CONFIRMED; **thin**: the percentile interval beside, [−0.03, +2.73], reaches 0; SE_2stage 0.00707 vs 0.00610 registered; MDE80 1.98pp > the observed 1.52 | LOW |
| U2 | D_K, spread_K | −0.45pp (−0.00450) [−1.31, +0.41]; spread 0.58pp; G_K +1.97pp | −0.00450; spread 0.00576; G_K 0.01974 | CONFIRMED → NOT FIRED; "by support" holds (abs 0.45 ≤ bar 1.22) | — |
| U3 | M_AF; Holm | M_AF −1.15pp (−0.01151) [−2.19, −0.12]; TOST p U3a 0.104 / U3b 0.613; U3a first at 95% [−1.31, +0.41] leaves ±1 → both NOT EQUIVALENT (Holm stops) | M_AF −0.01151; −0.01151 ± 1.96 × 0.00528 = [−2.186, −0.116] | CONFIRMED | — |
| AK1 | mirrored, decides | P(U_s) 0.7329 / 0.7162 / 0.7317 / 0.7122 / 0.7390, spread 0.0269, D_AU +0.0018 [−0.0084, +0.0122] → UNDETERMINED | same P_s and spread; D +0.0018, my bootstrap [−0.0086, +0.0121] | CONFIRMED | — |
| AK2 | mirrored, decides | P(US_s) 0.7368 / 0.7288 / 0.7423 / 0.7312 / 0.7452, spread 0.0165, D_AUs −0.0021 [−0.0115, +0.0077] → UNDETERMINED | same P_s and spread; D −0.0021 [−0.0117, +0.0078] | CONFIRMED | — |
| F-AK | upper ≤ measured spread_AUs | +0.0077 ≤ 0.0165 → FIRES (not better) | +0.0078 ≤ 0.0165, margin 0.009 | CONFIRMED | — |
| F-AK reg | registered rule, descriptive | D_AUs +0.0057 [−0.0041, +0.0157], spread 0.0155 | +0.0057 [−0.0038, +0.0157], spread 0.0155: upper > spread by **0.0002**, so it would NOT fire | CONFIRMED → (Q1) | MEDIUM (wording) |
| AK1 reg | descriptive | D_AU +0.0197 [+0.0082, +0.0314], spread 0.0275 | — | UNDETERMINED by spread under either rule | — |
| P_fl | descriptive | 0.7346 | 0.7346 | CONFIRMED | — |
| W | Written once | `OUTCOME written write-once` (mode "x"); one READ_STARTED marker (policy sha 8d68018c…, = the B3 line) | all 232 outcome lines are present in the console; the 45 console-only lines are the header (copied into the outcome as "  \| " pre-lines); no Traceback / REFUSED; policy ignored and untracked (`git ls-files … \| grep -c scratch` = 0) | CONFIRMED | — |

## Support re-measured (beside the deciding statistics)

- U-block "DEFF" (two-stage var / i.i.d. var, as in G14): U1 1.595, D_K 2.867, M_AF 2.761, against 1.392 transported from G14.
  n_eff 3,704 / 2,061 / 2,139; MDE80 1.98 / 1.22pp. My one-stage cluster bootstrap over EVAL components gives DEFF 1.03 /
  0.99 / 1.02, so the inflation is the TRAIN policy-refit variance, not item clustering.
- AK DEFF measured 1.102 / 1.080 (mine 1.100 / 1.101) against 1.341 / 1.449 transported; MDE80 0.0148 / 0.0138. The bars are
  spread-bound (0.0269 / 0.0165).

## Predictions (re-scored; all as printed)

U1 +1.52 in [+1.2, +3.6]: HELD. U2 D_K −0.45 in [−0.8, +1.0]: HELD. spread_K 0.58 in [0.2, 1.0]: HELD. U3b M_AF −1.15 outside
[−1.0, +0.6]: **FAILED**. Leaves 123 outside [70, 110]: **FAILED** (scored with the one cell, per the L22649 bracket; 122 split
leaves would fail too). The seven AK numeric predictions are all HELD (P_fl 0.7346, P(U_0) 0.7329, P(US_0) 0.7368, D_AU +0.0018,
spread_AU 0.0269, D_AUs −0.0021, spread_AUs 0.0165). Verdict probabilities, observed: U1 HELD (0.85); L-1 not fired (fires
0.10); U3a NOT EQ (EQ 0.45); U3b NOT EQ (EQ 0.40); AK1 UNDETERMINED (0.65); AK2 UNDETERMINED (0.55); F-AK FIRES (0.70).

## Disclosures that bind the wording

- **D-4**: K_s files by true source while AF-U's flatLeaf searches all leaves, which pushes D_K DOWN. The D_K of −0.45pp is
  therefore not evidence that AF routes worse than k-means; its interval covers 0 in any case.
- **C-S1 (mirrored filing; the one-cell amendment)**: IFEVAL is one cell, filed by source on both sides of AK1/AK2. Per-source
  D for IFEVAL is 0.0000 (it has one declared class). F-AK FIRES under the mirrored rule fixed pre-data; the registered rule's
  descriptive value misses by 0.0002 (Q1).
- **Q2 (over-reading)**: U3b's two-stage 95% interval lies wholly below 0. AF-U's label-free cells route **1.15pp below**
  declared labels. That is a measured shortfall, recorded descriptively (no registered criterion scores a loss; U3b is a TOST),
  and never parity, equivalence or "matches declared labels". The anchored B0 tree's M was −0.05pp [−0.69, +0.59] (G14, of
  record, a different recipe; never ranked).
- The F-TAX bracket of 2026-10-01: L-1 not fired by support, so "a filing device only (N-1 fired) (lever leg not fired, by
  support)"; never "no lever".

## Registrar's wording (proposed)

"UNION-AF-ROUTE (RP13), content-closed v2 union split, 0 calls: a fresh anchor-free federated tree (AF-U; 123 cells, IFEVAL one
cell under the author's one-cell amendment) routes the 18-model roster **above the best single model, U1 HELD: G_AF +1.52pp,
two-stage 95% [+0.14, +2.91] (thin; percentile [−0.03, +2.73]; 5,907 items / 5,404 components)**. It does **not** route
equivalently to declared labels: **U3b NOT EQUIVALENT, M_AF −1.15pp [−2.19, −0.12], a measured shortfall against declared
labels** (descriptive). Against per-source k-means at matched counts, **U2 / F-TAX L-1 not fired by support** (D_K −0.45pp
[−1.31, +0.41], spread_K 0.58pp; filing asymmetry D-4 against AF), and U3a NOT EQUIVALENT. On filing, the anchor-free tree is
**not better than unsupervised k-means: AK1 / AK2 UNDETERMINED** (D_AU +0.0018 [−0.0084, +0.0122]; D_AUs −0.0021 [−0.0115,
+0.0077]; 6,139 / 5,628), and **F-AK FIRES (not better)**: AK2's upper bound 0.0077 ≤ the seed spread 0.0165, under the mirrored
one-cell filing bracketed pre-data (C-S1; the registered nearest-of-all value, descriptive, would miss by 0.0002). F-TAX reads
'a filing device only (N-1 fired) (lever leg not fired, by support)'. Predictions: U3b and LEAVES FAILED; the others HELD."
Not licensed: parity with declared labels; 'the tree beats k-means'; 'no lever'; anything for MMLU-Pro alone; any ranking
against the anchored recipe.

## Defects

- **D-PR-1 (LOW)**: the two-stage SEs exceeded the transported ones (U1 0.71 vs 0.61; paired 0.44 / 0.53 vs 0.33). The Support
  sections of future G14-machinery registrations should transport the two-stage DEFF of a TREE arm (here 1.6-2.9), not
  G14's declared-arm 1.392.
- D-PB-1 of POSTBUILD still stands: the worktree DB copies must never be promoted.

## Commands

```
python scratchpad/rp13m/recompute_u.py    # eval_view response x frozen policy x cell files: 5907/5404; arms to 4 dp; G_AF .01524 D_K -.00450 M_AF -.01151 spread .00576; one-stage DEFF
python scratchpad/rp13m/recompute_ak.py   # bundle + FM.spherical_kmeans, own naming/filing/bootstrap: AK1/AK2 mirrored and AK2 registered
sha256sum outcome.txt ; cat union_af_route.READ_STARTED ; sha256sum scratch/union_af_route_train_policy.json (= B3 8d68018c…)
python: every outcome line present in rp13_run.log (0 missing; 45 console-only header lines); grep Traceback/REFUSED (0)
git log -1 --format=%cI d3653625 (15:16) < outcome mtime (15:51)
```
