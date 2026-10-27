# POSTRUN review: SCALE-AGREE (scale_agree.py blob 92131d5b), 2026-10-04

Registration prog L24375-L24386 (633255f2) with brackets at L24378 / L24379 / L24381 (P-SA1) / L24382; READY
`docs/reviews/READY_zero_call_trio.md` delta 981c2903. Zero calls. Reviewer: read-only, light CPU only (TREE-LIKE
was the one heavy process on the machine; rule 7); no JVM, no refit of the 25 x 8 deciding AMI grid.

## Verdict

**VALID** as a mechanical readout: SC1 **FAILED** (massive no, clinc no), F-SC **FIRED**. Conditions on the words:

- **C-SA1 (HIGH, words): the "agreement INCREASES with k" reading is NOT reportable as a finding.** A null with
  no scale-dependent divergence at all (an isotropic cloud; gemma = the same points plus scale-uniform noise; the
  normaliser = the same points plus tiny noise) produces the same rising normalised curve (slope +0.039 to +0.052
  per log2 k, rho +0.43 to +0.74; the MASSIVE curve shape to two digits). The q4-vs-q8 division does not centre the
  statistic at 0 under "no scale dependence": coarse k-means bisections of a weakly clustered cloud are fragile
  under ANY non-shared distortion, while the q4-q8 copy shares almost all of it. Word: "SC1 FAILED; the normalised
  AMI slope is positive on both corpora, which the instrument also produces under a scale-uniform null, so neither
  'fine diverges' nor 'fine agrees more' is supported label-free." On the real arms the k = 2 point is capped by gemma's own
  seed instability (self-AMI 0.21 MASSIVE / 0.24 CLINC), which the qwen3-only normaliser does not divide out.
- **C-SA2 (MEDIUM, words): F-SC FIRED stands, with that qualifier.** "Coarse holds, fine diverges has no
  label-free support FROM THIS INSTRUMENT"; the instrument is biased against DECREASES at low k, so the failure
  is not evidence against the reconciliation either. Not "refuted".
- **C-SA3 (MEDIUM, words): SC2 / P2 are DEGENERATE.** k* = 2 for all 10 pair-corpora is the grid floor
  (left-censored: "k* <= 2"); every pair's normalised AMI at k = 2 is below 0.8 and so is the null's. P2's
  Brier 0.3025 is printed but uninformative; record P2 as "not scoreable (censored at the grid floor)".
- **C-SA4 (LOW, disclosure): first attempt killed.** A first launch was killed by a tool time limit at about 1 h
  before any output; the run of record started 19:38:31 (`chain_sa_tl.log`; scratch run dir
  `run_66844_20261004193831`) and ended rc 0 at 21:01:02. No partial outcome existed: `run()` refuses if the
  outcome or SHA256SUMS exists (L557-L561), and the write-once write succeeded.
- **C-SA5 (LOW, support): realised DEFF exceeds the bracket's worst case on MASSIVE.** Bootstrap SE 0.0161 /
  0.0063 (DEFF 5.64 / 4.55 vs the bracketed worst case 5); MDE80 0.045 on MASSIVE is above |prediction| 0.04.
  Not decisive: the observed interval [+0.0077, +0.0694] excludes 0 and the prediction on the positive side.

## Per-claim table (deciding claims)

| # | claim | run prints | reviewer | status | sev |
|---|---|---|---|---|---|
| 1 | script of record | blob 92131d5b, lf16 d18bf94e, crlf16 95297053 | `git hash-object` 92131d5b = HEAD blob; working tree sha256 952970538193c3ea = the CRLF rendering; tree clean (0 lines of status) | CONFIRMED | - |
| 2 | data object | massive 9,870 / clinc 13,487 TRAIN rows; 6 arm pins + ingest PIN OK | matches SA-R1 (TRAIN, in-scope; not the 57,350); pins printed OK by the script's own refuse-on-mismatch path | CONFIRMED | - |
| 3 | SC1 massive slope / rho | +0.0463 / +0.762 | +0.0463 / +0.762 from the printed mean curve (OLS slope of the mean = mean of the 25 slopes, den common) | CONFIRMED to the digit | - |
| 4 | SC1 clinc slope / rho | +0.0812 / +1.000 | +0.0812 / +1.000 | CONFIRMED to the digit | - |
| 5 | raw (un-normalised) direction | not printed | raw AMI(qwen3, gemma) = norm x den: massive slope +0.0551 rho +0.786; clinc +0.0870 rho +0.976 (the normaliser does not create the rise) | CONFIRMED (descriptive) | - |
| 6 | seed-bootstrap intervals | massive [+0.0077, +0.0694]; clinc [+0.0678, +0.0924] | NOT recomputed: needs the per-seed-pair AMI grid (not saved; refit = about 72 min of full CPU at native). Code read: a tied across num and den, b and c independent, percentile 2.5/97.5 on centred log2 k; independent `_ref_boot_hi` in the selftest (prior review) | UNDETERMINED (deferred, heavy); den and the curve at k = 2, 4, 8 reproduced to the digit (table below) | LOW |
| 7 | P-SA1: word follows rho AND the bootstrap bound | "does not decrease" both | `sc1_corpus` passes `bhi` (seed_boot) to `decreases(rho, ci_hi)`; t(24)/t(4) are print-only. On these data every bound is positive and rho > -0.7, so the word is identical under all three bounds (no sign disagreement; DD-2 clause not triggered) | CONFIRMED | - |
| 8 | SC1 = FAILED, F-SC FIRED | FAILED / FIRED | follows from 3, 4, 7 | CONFIRMED (words per C-SA1/C-SA2) | HIGH (words) |
| 9 | normaliser unbiased in k (duty 2) | assumed by the registration | REFUTED by a scale-uniform null and by gemma's own k = 2 instability (self-AMI 0.21 / 0.24; tables below); AMI itself is chance-adjusted (expected 0 for independent partitions at any k), so the bias is not chance MI but k-means fragility at coarse k under non-shared distortion | REFUTED | HIGH |
| 10 | SC2 k* | 2 for every pair | grid floor; censored; also 2 under the null | DEGENERATE | MEDIUM |
| 11 | robustness of "not decreasing" | - | dropping k = 2: massive slope +0.0232 rho +0.643; clinc +0.0316 rho +1.000; dropping k <= 4: massive +0.0042 rho +0.429 (flat), clinc +0.0208 rho +1.000. No subset decreases; MASSIVE's rise is carried by k = 2..8 | CONFIRMED (descriptive) | - |

## Scale-uniform null (duty 2; synthetic, n 3,000, 3 seeds/side, the script's own skmeans and sklearn AMI)

| d, noise gemma, noise q8 | normalised curve k = 2..256 | slope | rho |
|---|---|---|---|
| 8, 0.08, 0.01 | 0.50 0.69 0.86 0.91 0.93 0.90 0.88 0.81 | +0.0388 | +0.429 |
| 8, 0.15, 0.01 | 0.34 0.60 0.60 0.73 0.78 0.75 0.67 0.55 | +0.0266 | +0.310 |
| 16, 0.05, 0.005 | 0.52 0.66 0.68 0.86 0.89 0.93 0.91 0.86 | +0.0522 | +0.738 |
| MASSIVE native (run) | 0.51 0.72 0.89 0.89 0.93 0.92 0.91 0.91 | +0.0463 | +0.762 |

Not calibrated to the real arms (an existence proof that the null slope is > 0, not an estimate of it).

## Within-arm self-stability on the real arms (duty 2; k = 2, 4, 8 only; 5 seeds, the run's seeds; ro/immutable reads)

| corpus k | self qwen3 | self q8 | self gemma | AMI q4-q8 (run den) | AMI q-g | norm, registered (run) | norm by sqrt(self q x self g) |
|---|---|---|---|---|---|---|---|
| massive 2 | 0.5074 | 0.6187 | **0.2129** | 0.5822 (0.5822) | 0.2975 | 0.5110 (0.5110) | 0.9054 |
| massive 4 | 0.6883 | 0.6346 | 0.5890 | 0.6845 (0.6845) | 0.4900 | 0.7158 (0.7158) | 0.7696 |
| massive 8 | 0.7022 | 0.6753 | 0.7686 | 0.6835 (0.6835) | 0.6061 | 0.8868 (0.8868) | 0.8250 |
| clinc 2 | 1.0000 | 1.0000 | **0.2391** | 0.9747 (0.9747) | 0.1843 | 0.1891 (0.1891) | 0.3769 |
| clinc 4 | 0.6113 | 0.7377 | 0.6462 | 0.6774 (0.6774) | 0.5165 | 0.7624 (0.7624) | 0.8217 |
| clinc 8 | 0.7432 | 0.6827 | 0.7366 | 0.6903 (0.6903) | 0.5956 | 0.8629 (0.8629) | 0.8051 |

(1) Independent partial recompute of the deciding grid: den(k) and the registered normalised AMI at k = 2, 4, 8
reproduce the run to the digit on both corpora (6 of 16 deciding-curve points). (2) gemma's OWN k = 2 split is
seed-unstable (self-AMI 0.21 / 0.24; qwen3 0.51 / 1.00), so AMI(qwen3, gemma) at k = 2 is capped by gemma's
instability, which the q4-q8 normaliser (qwen3-only) never sees. Under a both-arm self-stability normaliser the
MASSIVE head is 0.91 / 0.77 / 0.83 (not rising); CLINC still rises 0.38 / 0.82 / 0.81 from k = 2. The full 8-k curve
under that normaliser needs k = 16..256 fits (heavy): DEFERRED, not run while TREE-LIKE holds the machine.

## Defects and fixes

- D-1 (HIGH) normaliser not null-centred in k (row 9). Fix (any SCALE-AGREE successor, new registration): centre
  SC1 on a within-arm null, e.g. normalise by sqrt(self-stability(qwen3) x self-stability(gemma)) per k, or compare
  the slope against a distortion null with the arms' kNN overlap; until then words per C-SA1.
- D-2 (MEDIUM) k* grid floor (row 10). Fix: report k* as censored when it equals min(K_GRID); a successor adds k = 1-free
  coarse points or a threshold relative to the null curve.
- D-3 (LOW) deciding bootstrap not re-derivable from the outcome (row 6): the per-seed-pair AMI grid is not printed or
  stored. Fix: a successor writes the 8 x 25 AMI grids for (qwen3, gemma) and (q4, q8) beside the outcome on E:.

## Registrar duties

R-SA1 enter SC1 FAILED, F-SC FIRED with the C-SA1/C-SA2 words; R-SA2 P1 FAILED (Brier 0.3600), P2 NOT SCOREABLE
(censored), P3 does not hold (Brier 0.4900; descriptive); R-SA3 disclose the killed first attempt (C-SA4);
R-SA4 Support: realised DEFF 5.64 / 4.55 (bootstrap), MDE80 0.045 / 0.0177; P-SA1 discharged; R-SA5 256-d line
stays NOT of record (FAILED, rho +0.548 / +1.000).

## Outcome and backup

`E:/TaxoArena_backup_2026-10-04_scale_agree/scale_agree_outcome.txt` sha256 2a1fa578c6c35139 (13,220 B), written by the
script with `SHA256SUMS.txt`; `sha256sum` re-check equal. Never committed. Log `E:/TaxoArena_tmp/scale_agree_run.log`
(UTF-16LE).

## Commands

```
git hash-object tools/analysis/scale_agree.py; git show HEAD:tools/analysis/scale_agree.py | git hash-object --stdin
iconv -f UTF-16LE -t UTF-8 E:/TaxoArena_tmp/scale_agree_run.log ; cat E:/TaxoArena_tmp/chain_sa_tl.log
sha256sum E:/TaxoArena_backup_2026-10-04_scale_agree/scale_agree_outcome.txt ; cat .../SHA256SUMS.txt
python E:/TaxoArena_tmp/sa_review_recompute.py      # rows 3-5, 11 (polyfit on log2 k, spearmanr, raw = norm x den)
python E:/TaxoArena_tmp/sa_review/synth.py 8 0.08 0.01 | 8 0.15 0.01 | 16 0.05 0.005   # duty-2 null (1 thread)
OMP_NUM_THREADS=2 python E:/TaxoArena_tmp/sa_review/stab.py 2,4,8   # within-arm self-stability, ro/immutable reads
sed -n 238,300p tools/analysis/scale_agree.py ; sed -n 353,362p (P-SA1: decreases(rho, bhi))
```

## P-SA2 recompute (2026-10-06; reviewer; zero calls; discharges P-SA2 and row 6)

**Verdict: CONFIRMED.** Both deciding crossed-seed bootstrap intervals reproduce to the 4th digit from an independent refit and an
independent bootstrap; row 6 moves UNDETERMINED -> CONFIRMED. SC1 FAILED, F-SC FIRED and the C-SA1 / C-SA2 words stand.

Data object: MASSIVE 9,870 / CLINC 13,487 TRAIN rows (census reprinted); staged copies on E: of intent_transfer_corpora_v1.db and
intent_emb_{qwen3,qwen3_q8,gemma}.db, sha256 = TL.INGEST_PIN / TL.PINS (asserted); DBs of record size/mtime equal before and after.
Instrument reused (not re-implemented, so the partitions are the run's): `intent_transfer_s0.skmeans` at the pinned blob f662ceb1
(TL.its_module refuses otherwise), float32 -> unit float64 as `intent_matrices`/`width_views`, seeds 20261004 + s, native width.
Own code: 240 fits (2 corpora x 3 arms x 8 k x 5 seeds, 20 workers, 256 s wall), AMI grids, curve, slope, rho, and a bootstrap
written apart from `seed_boot` (explicit per-draw means over (a_i, c_j) and (a_i, b_j), slope by np.polyfit; draws a, b, c from
RandomState(seed)). The 8 x 5 x 5 AMI grids are now saved (closes D-3 for this run).

| # | quantity | run prints | P-SA2 recompute | status |
|---|---|---|---|---|
| 6a | den(k), both corpora, 8 k | as outcome L12 / L28 | identical to 4 d.p. at all 16 points | CONFIRMED |
| 6b | normalised curve, both corpora, 8 k | as outcome L14 / L30 | identical to 4 d.p. at all 16 points (k = 16..256 newly reproduced) | CONFIRMED |
| 6c | mean slope / rho | +0.0463 / +0.762; +0.0812 / +1.000 | +0.0463 / +0.762; +0.0812 / +1.000 | CONFIRMED |
| 6d | MASSIVE bootstrap (B 2000, seed 20261004) | [+0.0077, +0.0694], SD 0.0161 | [+0.0077, +0.0694], SD 0.0161 | CONFIRMED to the digit |
| 6e | CLINC bootstrap (B 2000, seed 20261004) | [+0.0678, +0.0924], SD 0.0063 | [+0.0678, +0.0924], SD 0.0063 | CONFIRMED to the digit |
| 6f | MC tolerance, 200 other seeds, B 2000 | - | MASSIVE lo +0.0084 (SD 0.0019, range +0.0027..+0.0123), hi +0.0690 (SD 0.0005); CLINC lo +0.0683 (SD 0.0004), hi +0.0927 (SD 0.0003). Printed bounds inside 1 MC SD (MASSIVE lo 0.4 SD) | CONFIRMED |
| 6g | B 20,000 (seed 1) | - | MASSIVE [+0.0081, +0.0691] SD 0.0162; CLINC [+0.0682, +0.0927] SD 0.0063 | CONFIRMED |
| 6h | SC1 word robust to the bootstrap seed | does not decrease (both) | lower bound > 0 in 200/200 seeds on both corpora; rho > 0; DECREASES needs rho <= -0.7 AND hi < 0: fails on both clauses everywhere | SC1 FAILED stands |
| 6i | Support (C-SA5) | DEFF 5.64 / 4.55; MDE80 0.0450 / 0.0177 | at B 20,000: DEFF 5.70 / 4.54 (naive SE 0.0068 / 0.0030), n_eff 4.4 / 5.5 seed pairs, MDE80 0.0453 / 0.0177 | CONFIRMED (MC-level gap) |

C-SA1 / C-SA2 check (descriptive; not of record). Over the FULL grid (the review deferred k = 16..256) the both-arm self-stability
normaliser AMI(q, g) / sqrt(self q x self g) gives MASSIVE 0.905 0.770 0.825 0.871 0.897 0.898 0.898 0.885 (slope +0.0088,
rho +0.190: flat) and CLINC 0.377 0.822 0.805 0.895 0.926 0.961 0.968 0.967 (slope +0.0639, rho +0.952: still rising from
gemma's unstable k = 2, self 0.239). k = 2, 4, 8 equal the review's table. Under neither normaliser does agreement decrease, and
the rise is normaliser-dependent on MASSIVE: the C-SA1 word "SC1 FAILED; the normalised AMI slope is positive on both corpora,
which the instrument also produces under a scale-uniform null, so neither 'fine diverges' nor 'fine agrees more' is supported
label-free" stands unchanged; C-SA2's "not refuted" qualifier stands.

Defects: none new. D-3 discharged for this run by the saved grids (the successor fix stays). Note for the registrar: the brief
named `E:/TaxoArena_backup_2026-10-05_scale_agree`; the only scale_agree backup dir is `..._2026-10-04_scale_agree` (count 1 by
`ls -d E:/TaxoArena_backup_*scale_agree* | wc -l`), which is the one updated.

Backup (`E:/TaxoArena_backup_2026-10-04_scale_agree`, SHA256SUMS.txt now 8 lines, `sha256sum -c` 8/8 OK): psa2_recompute.py
d82a40b803c140f7, psa2_selfstab.py 53e8353f687e0db2, psa2_boot_output.txt e436c6906903ea47, psa2_selfstab_output.txt
19745bb40788f9ee, psa2_fit.log bcab392fb6c57f12, psa2_ami_grids_massive.npz 1051f63ebc8cbf3e, psa2_ami_grids_clinc.npz
b2d07f8fc7eb86db; outcome 2a1fa578c6c35139 unchanged. Partitions (240 .npy) left in E:/TaxoArena_tmp/psa2/lab (not backed up).

```
powershell -NoProfile -File E:/TaxoArena_tmp/busy.ps1            # exit 1 (free) before launch
python E:/TaxoArena_tmp/psa2/psa2_recompute.py prep              # stage + pins + census + size/mtime check
Start-Process python psa2_recompute.py fit 20                    # detached; fit.log 240/240, FIT DONE
python E:/TaxoArena_tmp/psa2/psa2_recompute.py boot              # rows 6a-6i
python E:/TaxoArena_tmp/psa2/psa2_selfstab.py                    # C-SA1 rider
git hash-object tools/analysis/scale_agree.py                    # 92131d5b (reviewed blob, unchanged)
```
