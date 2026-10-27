# POST-RUN REVIEW: MIX-LRT-SITE (run from main 5e57cd2 / dd2477e, mix_lrt_site.py blob:3e6a682c) (adversarial reviewer, 2026-09-26, zero calls, read-only)

## VERDICT

**VALID. Every printed number reproduces to the digit.** Recomputed from the 33 state chunks with my own JSON code, and independently from the pinned inputs with my own PCA, k = 1 likelihood, generator and fits: 282 observed LRs agree with the state to at most 4.1e-14 relative, and 60 null draws at the deciding sites agree to at most 5.5e-14.

The outcome of record is **C1 FAILED [FAILED-ALL-CERTIFY]**. Reading (R-d) applies, F1 FIRES, and L6 closes NEGATIVE for the LR / BIC half.

Wording conditions (section 4):

- **W1:** (R-d)'s sentence of record stands as registered, but it must carry a scope qualifier. The failure shows that this LR cannot see modes. It does not show that there are none.
- **W2:** P5a and P5b are HELD **by degeneracy** (kappa = 0 and superset = 1 because the LR says yes everywhere), and must be written so.

**Null calibration: "every site certifies" is a real finding, not a bug.** The finding is that the question embeddings are non-Gaussian at every node; it is not evidence of modes.

- The null does what it is registered to do: it is calibrated for "one Gaussian with the site's own mean and covariance, projected to the sphere".
- That H0 is false at every node, including the terminal leaves. My reviewer-only leaf null gives 56 of 56 leaves with n >= 110 "certified" (frozen 25/25, af_clean_s42 31/31, B 49).
- So the rejection is not about the split.
- Sphere curvature does NOT explain it:
  - It would inflate the null LR, which makes certification harder, not easier.
  - The real-site null medians (90.5-144.9) sit near the flat 10-d level (about 106 on the READY's fixture), so the inflation seen on the fixture (about 206) is not present at these sites.
- What differs from the null:
  - marginal skewness, 2-4x the null's (mean |skew| per PC 0.19-0.30 against 0.06-0.09);
  - clumping (median nearest-neighbour cosine 0.64-0.68 against 0.59-0.60).
- What does not differ:
  - tail weight (Mardia kurtosis 115-117 against a null of about 114);
  - separation of the fitted components (1.6-2.0 total-SD for the observed fits against 1.0-1.8 for the null draws' fits).

## 1. Per-claim table

| # | Claim as printed | Result | Mine (script) | Sev |
|---|---|---|---|---|
| 1 | Inputs, identity, state | CONFIRMED | 33 chunks, one meta_sha 70e9632c..., script blob 3e6a682c in every chunk and in meta. All 5 [SCRIPT] lines (dry-run + 3 run passes + analyze) print blob:3e6a682c / lf16 565c05b6bcffd856 / crlf16 bdd041ed7fc5859a. The dry-run's 6 [PIN table/row] lines equal mine (`diff` empty). [PIN] before == after on all 4 logged passes. Output sha256: outcome 306d7a30e06cf246, sites.csv 9906438791617970, meta 70e9632cb6ad1067, plan dfb5781d69337353 (= the relay). State and DBs unchanged by this review (sha256 of all 37 files and `ls --full-iso` of the DBs, before and after) | - |
| 2 | n00000013: LR 1158.042, 0/199, q 0.005, CP [0, 0.0184] | CONFIRMED | post_state.py: LR 1158.042, B 199, f 0, admitted 199, exceedances 0, q 0.0050, CP [0.0000, 0.0184]. Null median 109.6, p95 149.9, max 175.8; observed / max null 6.59 | - |
| 3 | n00000014: LR 1117.622, 0/199, q 0.005 | CONFIRMED | LR 1117.622, B 199, f 0, 0 exceedances, q 0.0050, CP [0, 0.0184]. Null median 110.5, p95 141.6, max 163.1; ratio 6.85 | - |
| 4 | n00000055: LR 350.783, 0/199, q 0.005 | CONFIRMED | LR 350.783, B 199, f 0, 0 exceedances, q 0.0050, CP [0, 0.0184]. Null median 117.0, p95 147.4, max 180.2; ratio 1.95 | - |
| 5 | No escalation, B 199 | CONFIRMED | q 0.005 < 0.02 at all three, so the band [0.02, 0.10] was never entered. B_admitted = 199 on all 282 rows (sites.csv); f = 0 on all 282; VOID 0 | - |
| 6 | C1 FAILED [FAILED-ALL-CERTIFY]; no MC-MARGINAL | CONFIRMED | n00000014 and n00000055 both at q 0.005 <= 0.05. No CP interval contains 0.05 (upper bound 0.0184) | - |
| 7 | D1 66/66, 69/69, 60/60, 87/87 | CONFIRMED | same; 282/282 | - |
| 8 | D2 2x2, Jaccard, kappa 0.000, superset 1.000 | CONFIRMED | frozen [6,60,0,0] 0.091; af_clean [14,55,0,0] 0.203; o0 [11,49,0,0] 0.183; af_bareq512 [10,77,0,0] 0.115; kappa 0.000 on all four (degenerate: one rater is constant); superset 1.000 | - |
| 9 | D3 +0.0000 | CONFIRMED | 1.0000 - 1.0000; J +0.0196, MDE 0.198 | - |
| 10 | D4 dBIC > 0 on 0.742 / 0.855 / 0.783 / 0.920 | CONFIRMED | 49/66, 59/69, 47/60, 80/87; dICL > 0 on 46 / 55 / 41 / 79; the J cross-tabs are identical to the printed ones | - |
| 11 | D5 -0.13731 / +0.31190 / -0.24245; defined at 33 / 49 / 36 / 47 | CONFIRMED | Leaf medians over 3 / 3 / 2 leaves: 1.19199 / 1.07818 / 0.84311. Descriptive: the median per-point gain over the leaves exceeds the median over the sites on every tree (1.056 vs 0.966; 1.210 vs 0.964; 1.144 vs 0.940; 1.507 vs 1.158) | - |
| 12 | D6 DROPPED, D7 87/87 | CONFIRMED | plan.json legs_desc [] | - |
| 13 | P1 FAILED; P2 HELD; P3 HELD; P4 FAILED x4; P6 FAILED; P7a FAILED; P7b FAILED; F1 FIRES | CONFIRMED | From the numbers above: P4 66 > 60, 69 > 63, 60 > 55, 87 > 80; P6 needs >= 90% on every tree and gets 74.2 / 85.5 / 78.3 / 92.0 | - |
| 14 | P5a HELD (kappa 0.000 in [-0.05, 0.35]); P5b HELD (1.000 in [0.60, 1.00]) | PARTLY | The arithmetic is right, but both are forced: with 69/69 LR-certified, kappa is identically 0 and the superset share is identically 1 whatever J does. The registered interval scoring holds by letter; in substance they are uninformative | MEDIUM (W2) |
| 15 | P8 FAILED (72.3 > 60) | CONFIRMED | Sum of per-cell p10 CPU over obs + draws = 72.346 min (leaves 0.049; all cells 72.395; chunk cpu_s total 73.14 = the relayed "measured 73.1"). Post-drop PROJECTION 72.3 + 3.8 + 0.6 = 76.7 < 80; measured total 73.1 < 80 | - |
| 16 | Readings: only (R-d) | CONFIRMED | (R-a)-(R-c) need C1 HELD; (R-e) needs "no Philosophy site certifies"; (R-f) needs CS not certifying | - |
| 17 | R7: eigengaps at the 282 observed sites; tie-gap rule | CONFIRMED, NOT TRIGGERED | post_indep.py (thin SVD of each site): minimum relative gap p5 8.32e-3 (frozen n00000011), p10 1.475e-4 (af_bareq512_s42 n00000074), p20 1.58e-3 (af_clean_s42 n00000045), all >= 1e-10. The deciding sites' 597 draws were covered in the delta READY (min 4.47e-4) | - |

## 2. Independent recompute (own code; members and vectors through the script's read-only loaders only)

- **post_state.py** (JSON only) checks every (site, b) cell: present exactly once, b = 0..198 contiguous, no duplicates. It also covers q, CP, D1-D5, the CPU sums, and the sites.csv agreement: 282 rows, max |LR diff| 0.0, max |q diff| 0.0.
- **post_indep.py** checks the observed p10 LR at all 282 sites with thin-SVD PCA, its own k = 1 MLE and sklearn with the SeedSequence(20260926, (tree, row)) state. Max relative difference against the state: 2.7e-14 / 1.5e-14 / 1.6e-14 / 4.1e-14.
- It also recomputes null draws b 0-19 at each deciding site with its own generator (mu + Z diag(s/sqrt(m)) V^T, normalised, then three states). Max relative difference: 5.5e-14 / 4.9e-14 / 4.1e-14.

## 3. Null calibration: artefact or finding?

| diagnostic (reviewer-only, descriptive) | observed | the site's own null | reading |
|---|---|---|---|
| observed LR / max of 199 null LRs, all 282 sites | min 1.18 (o0 n00000040), median 2.86-4.02 by tree, max 114.6 | 1 by definition at the max | every site clears its null max; the smallest margin is 18% |
| z of observed vs null | min 5.0, median 21.9-33.0 | - | not a borderline effect |
| null LR median, per site | - | 90.5-144.9 | near the flat 10-d level; curvature inflation is small here |
| **leaves n >= 110, their own withinNodeCloud null, B 49** | **56 of 56 "certified"**; observed / max null median 2.1, min 1.28 | - | the Gaussian null fails inside the terminal cells too: the LR tests Gaussianity, not the split |
| Mardia kurtosis, p = 10 (Gaussian 120) | sites median 112.9-115.0; deciding 115.4 / 115.9 / 116.9 | deciding draws median 114.0 / 113.8 / 114.7 | NOT heavy tails (both are light-tailed, from the sphere) |
| mean abs skewness per PC (deciding sites) | 0.30 / 0.19 / 0.20 (max 1.27) | 0.09 / 0.08 / 0.06 | asymmetric texture |
| nearest-neighbour cosine, median (deciding) | 0.677 / 0.673 / 0.643; near-copies at cos >= 0.98: 9 / 7 / 0; exact duplicates 0 | 0.586 / 0.600 / 0.595; 0 near-copies | clumpier than a Gaussian; not duplicate-driven (n00000055 has none and certifies) |
| fitted 2-component structure (deciding) | weights 0.47/0.53, 0.74/0.26, 0.38/0.62; mean separation 1.73 / 2.00 / 1.60 total-SD | null fits 1.0-1.8 total-SD | the observed fits are not better-separated modes than the null's; the LR gain comes from shape |

Conclusion:

- The run is correct.
- The null is correctly implemented and correctly calibrated for its registered H0.
- H0 (a single site-covariance Gaussian, projected) is false everywhere at p = 10, because question embeddings are skewed and clumpy at every scale, leaves included.
- A 2-component Gaussian mixture absorbs that shape, so the LR has no power to separate a real two-mode split (CS contamination) from a single topic (Philosophy).
- This is exactly the "texture" branch the registration anticipated in (R-d).
- It is not a null-calibration bug. It IS a null-model mismatch in the sense that the Gaussian null is the wrong H0 for a mode question. A texture-preserving null (a bootstrap or a within-leaf null) would be needed, and none is registered.

## 4. Wording

- **W1 (R-d, MEDIUM).** The registered sentence stands as the reading of record:
  - "question embeddings carry non-Gaussian texture at every node; a Gaussian mixture LR cannot separate modes from texture here; L6 CLOSES NEGATIVE for its LR / BIC half: 'the certificate is geometric, not modal'".
  - Its first two clauses are directly supported (282/282 sites; 56/56 leaves, reviewer-only).
  - The quoted phrase "the certificate is geometric, not modal" must carry this qualifier beside it wherever it is written: "(i.e. the Gaussian-mixture LR / BIC gives no modal support for the J certificate: it rejects its Gaussian site null at every site of all four trees and at every leaf tested, so it cannot discriminate; this is not evidence that the certified splits lack modes; the dip half is unexplored)".
  - The READY's D2 curvature disclosure is registered beside (R-e) / (R-f) only and is NOT required beside (R-d). Curvature inflates the null, the conservative direction for an all-certify result, and the measured null medians show little inflation. Write that as a sentence rather than omitting it silently.
- **W2 (P5, MEDIUM).** "P5a HELD, P5b HELD (by degeneracy: LR certifies 69 of 69 on af_clean_s42, so kappa is 0 and the superset share is 1 by construction; uninformative)".
- **W3 (LOW).** "All sites certify" is always written with its denominators: 66/66, 69/69, 60/60, 87/87, p = 10, B = 199, q = 0.005 at the floor for every site. D1-D6 are nested and DESCRIPTIVE-ONLY.

## 5. Talk words

**MAY say:**

> "We tested whether a Gaussian-mixture likelihood ratio (1 vs 2 full-covariance components in each split's top-10 PCA subspace, calibrated against the same Gaussian site null) could tell a contaminated split from a genuine topic. It could not. It certified every split on all four trees (282 of 282, each at the minimum p-value 1/200), including the Philosophy sites it should have left uncertified, and a reviewer check found it rejects the same null inside the leaves too. The embeddings are non-Gaussian everywhere (skewed and clumpy), so a mixture LR measures texture, not modes. It cannot discriminate. The size-matched J site null remains the certificate, and its certified splits are a strict subset of the LR's (6/66, 14/69, 11/60, 10/87)."

Short form: "A Gaussian-mixture LR certifies every split, so it cannot discriminate; the matched J site null (splitter-statistic null) remains the discriminating certificate." Always add "on these embeddings, at p = 10" and "zero judge calls, geometry of construction members only".

**MUST NOT say:**

- that the J certificate "is not modal" or that certified splits "have no modes": the test lacks power to show either way;
- that the J null is "validated", "calibrated" or "correct" by this test: nothing here scores J against truth, and kappa = 0 is degenerate;
- "a mode test" of anything;
- that the LR is anti-conservative or buggy: it is calibrated for its H0;
- anything about p = 5 / p = 20 (DROPPED);
- a within-tree dimension contrast from af_bareq512_s42 (D7);
- a transfer claim (D3 MDE 0.198);
- "held-out" or "clean" about frozen or af_bareq512_s42 without the CONTEXT rule-12 qualifiers;
- that the dip test was done.

## 6. Defects

- **D1 MEDIUM:** P5a and P5b are held by degeneracy (W2).
- **D2 MEDIUM:** "geometric, not modal" needs the W1 qualifier.
- **D3 LOW:** the outcome prints the projection "post-drop 76.7" only through the [COST] parts. The measured 72.3 (p10) / 73.1 (all) is the figure to set against 80; the analysis prints the p10 figure and the plan the projection.
- **D4 LOW (disclosure):** the leaf null and the shape diagnostics are the reviewer's, reviewer-only and not registered. They support the reading; they are not outcomes.
- No BLOCKER. No HIGH.

## 7. Commands (session scratchpad `delta1\`; one single-threaded python process at a time; nothing written outside the scratchpad)

- `python post_state.py`: post_state.log
- `python post_indep.py`: post_indep.log, rc 0, about 3 min
- `python post_dup.py`: post_dup.log
- The inline sites.csv check and the CPU split (commands in this session's transcript)
- `sha256sum experiment_results/mix_lrt_site/state/* experiment_results/mix_lrt_site/*.*` before and after: identical
- `ls -la --time-style=full-iso embeddings_cache.db* snapshots*.db*` before and after: identical, -wal 0 bytes
- Run logs read: scratchpad `mix_run2\` (dryrun, run_1-3, loop, analyze)
