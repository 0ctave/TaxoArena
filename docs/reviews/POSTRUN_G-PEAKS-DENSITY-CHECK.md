# POSTRUN review: G-peaks density check (exploratory, not registered)

Reviewer: adversarial-reviewer, 2026-10-11, read-only. Authority: author_decisions/2026-10-09.md D-2026-10-11-3 / -5.
Object: E:/benchzoom_demo/density_check (SHA256SUMS.txt verifies 16/16 OK); benchzoom master 6ade538 (untouched).
Scratch: E:/TaxoArena_tmp/density_check_review (rev.py sha256 89bf5636..., src.py 3ef26094..., rev.log 6e097c68...).
The reviewer read the parquet columns id, text, options, subject and src. These are item metadata, not
model or score columns, and no response column was read. Zero LLM calls; 1 thread.

## Verdict: PARTLY CONFIRMED
Concentrations do exist inside some big unsplit leaves. But "11 leaves beyond null" (path P) overstates them:
- On P, the null condition is VACUOUS: no null ever fires, so "beyond null" here just means "has a stable peak" (11 = 11).
- Stability depends on the perturbation.
- The peaks vanish at min_samples 30.
- The strongest peaks rediscover MMLU's original sub-subjects (`src`).

The U path is not evidence: its own nulls fire at 0.90-0.99. It is fit to go to the registered held-out test only
with the fixes D1-D5 below.

## Per-claim table (deciding claims)
| # | Claim | Reviewer's number | Status | Sev |
|---|---|---|---|---|
| C1 | No score/response column read | 1 parquet read (L74, column projection + assert), 1 npz, 1 json (grep: 3 opens across both scripts). The atlas keys `correct`/`models`/`offsets`/`lomo` are parsed by json.load and popped before any access | CONFIRMED ("dropped unread" is really "parsed, never accessed") | LOW |
| C2 | Table counts (P 30/14/11/11/11; U 30/30/29/16/16; null any-peak 0.00 / 0.90 / 0.99 / 0.94; median 2 (1-3), 43% (13-95%); U median 4 (2-8), 99%; 9 both / 18 either; depth>=3: 8 leaves, n 157-265, 0 beyond; ARI P-U 0.00-0.56) | recomputed from leaves.csv / perm_null.csv: all agree to the digit | CONFIRMED (arithmetic only) | - |
| C3 | Path-P nulls never produce a peak | Gaussian, uniform-density ellipsoid and t(3) with matched covariance: any-peak 0.00 on all 4 leaves (20 draws each, own seeds) | CONFIRMED, and it makes the null leg VACUOUS (D1) | HIGH |
| C4 | P peaks are not artefacts of local clumpiness | Clump null (Neyman-Scott, clumps of 10, within-clump share w of the covariance). At w=0.2 (1-NN distance 0.28-0.32 vs real 0.30-0.32) any-peak is 0.1 / 0.8 / 0.3 (chem / phil / econ) and max share 0.14-0.61; false-peak rate 0.0 / 0.0 / 0.1. math:10 at w=0.05: fpr 0.3. The rule passes mainly through its share condition, and a bulk peak inflates that (D2) | PARTLY | MEDIUM |
| C5 | chemistry (mmlu_pro:3) has 3 stable peaks, 87 / 309 / 89 | Exact PCA solver gives 87 / 309 / **61**; 80% subsamples x10 give match >= .5 shares 1.0 / 1.0 / **0.5**; ms30, mcs x2 and raw-4096 all give 0 peaks | PARTLY: the acid/base 87 and the 309 peaks reproduce; the de Broglie peak is REFUTED as stable | MEDIUM |
| C6 | philosophy (mmlu_pro:12): 2 stable peaks, truth tables (32) | 443 / 32 reproduce. Truth tables match 0.76-1.00 across ms 5/20/30 and PCA 10/20/50, and 1.00 at 80% subsamples. **The other "peak" is the bulk (443/499 = 89%)** | CONFIRMED for the truth tables; "2 peaks" REFUTED as 2 concentrations (it is 1 plus the bulk) | MEDIUM |
| C7 | MATH Intermediate Algebra (math:10) is beyond null on both paths | Sizes 29 / 56 / 51 vs the claimed 27 / 55 / 50. 80% subsamples give match shares **0.6 / 0.4 / 0.4**, so no peak reaches 0.7; ms30 gives 0 peaks; clump null fpr 0.3 at w=0.05 | REFUTED as stable (the topics read coherent) | HIGH |
| C8 | economics (mmlu_pro:5), incl. econometrics (84) | Sizes reproduce exactly. Econometrics matches 1.0 at 80% subsamples, 0.92-0.98 at PCA 10/20/50, 1.0 at mcs x2; it is **83/84 `src`=ori_mmlu-econometrics with recall 83/84**. The 140 peak gives 0.9 at subsamples but 0.22-0.25 at PCA 10/20 | CONFIRMED for econometrics (a source subject); PARTLY for the 140 peak | MEDIUM |
| C9 | Peaks robust to HDBSCAN settings | min_samples 30 leaves 0 peaks in 3/4 leaves; mcs x2 leaves 0 in 2/4; raw 4096-d leaves 0 in 2/4 | REFUTED as "robust"; the peaks are band-limited density bumps | MEDIUM |
| C10 | Keyword labels match member questions | 5 random members of each of 11 peaks read. These match: acid/base, de Broglie, truth tables, econometrics, macro/monetary, complex modulus, inequality minima, conics. "gas laws (309)" is a mixed physical-chemistry peak (electronegativity, osmotic pressure, calorimetry, oxidation state). math:10 peak0 keywords carry single-item noise ("dogie, milk"). The philosophy bulk keywords are meaningless | PARTLY | LOW |
| C11 | Some peaks are template/source families | Truth tables: 53% of members have a cos>0.9 neighbour (leaf 10%); chem 87: stemez 83%; econometrics: src purity 99% | CONFIRMED, and more general than claimed (D4) | MEDIUM |
| C12 | U-path peaks (16 beyond null) | not re-run. Their own null any-peak rates are 0.90 / 0.99 / 0.94 and the output is a ~99% partition | UNDETERMINED; not evidence of concentrations | MEDIUM |

The prior run's own stability test (5 x 90% subsamples plus mcs x0.7/x1.3) is milder than the reviewer's
(10 x 80% subsamples plus ms 5/20/30, PCA 10/20/50, mcs x2, raw). The reviewer used own seeds (base 20261011) and
an exact PCA solver (svd_solver=full); the original used the randomized default with random_state=0. Its peak sizes
are therefore solver-dependent: chemistry's third peak is 61 vs 89.

## Defects and fixes
- D1 (HIGH) Path-P null leg is vacuous (no draw of 5 null families ever fires). Fix: add a null that preserves local
  clumpiness, e.g. a Neyman-Scott clump null with clump size and spread fitted to the leaf's 1-NN and 10-NN distance
  distributions. Report its any-peak rate beside every "beyond null". Add a positive control (a planted 5% cluster) to
  show the pipeline has power.
- D2 (MEDIUM) The false-peak rule's share term uses the largest stable peak, which can be the bulk (philosophy 89%,
  business 428/631 = 68%). That makes the null comparison trivially easy. Fix: exclude peaks over ~50% of n ("bulk")
  from both the peak count and the share term; report concentrations = non-bulk stable peaks.
- D3 (HIGH) Stability depends on the perturbation and the solver (math:10 fails at 80%; chem peak 2 differs by solver).
  Fix: register stability as 80% subsamples x >=10 plus min_samples {5,10,20} plus PCA dims {20,30,50}, and require
  >= 0.7 across the union of perturbations. Fix svd_solver="full".
- D4 (MEDIUM) Strong peaks rediscover the `src` sub-subjects (econometrics 83/84; formal_logic 32/98). Fix: in the
  registered test, add a `src`-subject baseline arm (item metadata, not a score). G-peaks must beat "split the leaf by
  `src`" to count as discovering structure.
- D5 (LOW) C1 wording: "dropped unread" should say "parsed by json.load, popped before any access". To be strict,
  stream-parse only `items`/`tree`.
- D6 (MEDIUM) Report the U-path counts as descriptive only; drop them from the "18 leaves beyond null on at least one path".

## Overall plain verdict
Real concentrations: philosophy truth tables (32), economics econometrics (84), chemistry acid/base (87) and the
309-item physical-chemistry peak. These are CONFIRMED stable on the reviewer's perturbations and are not reproduced by
the Gaussian, uniform or heavy-tailed nulls. Two of them are original-source subjects or templates.
- math:10 is REFUTED as stable, and chemistry's de Broglie peak is REFUTED as stable.
- The headline "11 leaves beyond null" is not supported as stated: the null leg removed 0 leaves.
Of 4 leaves re-checked, 3 hold at least one stable non-bulk concentration on path P.

## Commands
```
sha256sum -c E:/benchzoom_demo/density_check/SHA256SUMS.txt                      # 16 OK
grep -n "read_parquet\|read_table\|pq\.\|open(\|np.load" density_check.py perm_null.py   # 3 opens (L70, L74, L79)
python - (pandas on leaves.csv / perm_null.csv)                                   # C2 counts
E:/TaxoArena_tmp/density_check_review/rev.py  > rev.log                          # C3-C11 (leaves mmlu_pro:3,12,5; math:10)
E:/TaxoArena_tmp/density_check_review/src.py                                     # C8/C11 src purity and recall
```
