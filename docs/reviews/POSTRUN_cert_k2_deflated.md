# POST-RUN review — CERT-K2-DEFLATED (arm + --analyze + --replication; zero calls)

Reviewer: adversarial-reviewer, 2026-10-04. Run: rp12-r2-run @ 8419d4ce plus a path checkout of 1d282351 (script blob:f5f7f178,
SNBST blob:cb91cdcd, arm test blob:e0f326e1; matching READY_cert_k2_deflated_delta.md). Ops commit ca17f3de (logs
experiment_results/cert_k2_deflated/ops_20261004/). Outputs on E:\TaxoArena_backup_2026-10-04_cert_k2_deflated: SHA256SUMS.txt
verifies 9/9 at the backup and 9/9 against the run directory. outcome.txt sha256 4d7533be…, df_sites.csv 4e5e6718…,
arm/replicates.csv 15b5b2d9…, arm/sites.csv b7366892…, replication.txt fdc7eb54…; site_labels.tsv 00c00239 = the pin.

## VERDICT: VALID. DF0 VALID-NULL · DF1 ELONGATION-CONFOUNDED (not informative) · DF1b descriptive · DF2 DISCRIMINATING (scope W-2) · F-DF NOT FIRED

## Recompute (my own script from arm/replicates.csv and arm/sites.csv, read-only)

| # | quantity | arm / outcome | reviewer | agree |
|---|---|---|---|---|
| 1 | integrity | 97 sites in sites.csv, 96 null sites | 96 × 300 reps in order, all arm SNDF; defl_dims = 1 everywhere; k and reached recounts: 0 mismatches | yes |
| 2 | IDENTITY | 0.107803 | 0.107803, n 6993, no null | yes |
| 3 | DF0 | 0/20 DEFL-CERT, 0 NOT EVALUABLE, reached 300/300 | 0/20; 11 of 20 have declared < 0 (cannot pass); minimum reached 300 -> VALID-NULL (collapse excluded; not a calibration test, L24132) | yes |
| 4 | KK pairs n 486 / 441 | STRONG, MID, EDGE 5/5 DEFL-CERT at both sizes | k = 0 on all 30; declared 0.0670-0.1256 vs deflated p95 0.0473-0.0622 (maximum replicate ≤ 0.0677) | yes |
| 5 | EC controls | STRONG 5/5, MID 5/5 DEFL-CERT | k = 0 on all 10; declared 0.1028-0.1163 vs p95 0.0554-0.0622 | yes |
| 6 | margin (b) | STRONG 0.007269 > SD 0.002022; MID -0.000274 < SD 0.002416 | same to the digit (arm declared values) | yes |
| 7 | DF1 / DF1b | ELONGATION-CONFOUNDED (both pairs: the control is AT-SIZE) / "DEFL-CERTIFIED, ELONGATION-UNCONTROLLED" | same by L24133 (control 5/5 > 3, so clause (a) fails for both pairs; the margin alone would not rescue STRONG) | yes |
| 8 | DF2 | 0/3 -> DISCRIMINATING | K2 subsamples k = 300 on all 30 (every replicate ≥ the declared 0.0139-0.0190); deflated p95 0.0617-0.0691 | yes |
| 9 | full sites | KK d0 k 0 ×3; K2 d0 k 300 ×3 | same (KK p95 0.0335-0.0479; K2 p95 0.0551-0.0639) | yes |
| 10 | P1 | median 0.055472, FAILED vs [0.085, 0.118] | 0.0554719 (my linear p95 matches the arm's to 5e-10) | yes |
| 11 | Brier | P2 0.7650 (4-way, re-stated; SENSITIVE was settled pre-run, DF-J); P3 0.3750; P4 0.0025; P5 0.0900 ×2 | same | yes |
| 12 | replication | 30/30 word agreement | true, but uninformative: old and fresh k are both 300 on all 30 (W-4) | yes |
| 13 | deflated / plain p95 (descriptive, read post-run from the two outcomes of record) | n/a | KK subsamples 0.438-0.610; K2 subsamples 0.899-1.017 | n/a |

Write-once and console: one "wrote" line; the outcome and the CSV were created in the same second (05:33); --analyze ran its
selftest first (13/13). All 163 outcome lines appear in 08_analyze.txt; the one byte difference is the registration line's
em-dash in the cp1252 console (cosmetic). Wording: 0 occurrences of "certif" outside "DEFL-CERT" / "deflated-null certif…" /
"certificate" / the plain-null phrase in outcome.txt and replication.txt. Arm transcript: BUILD SUCCESSFUL 21m29s; 96 site lines;
THREAD-CAP 12; heap 0.39 GB; no REFUSED, OOM or exception. embeddings_cache.db per-table hashes before = after.
Ops log: W1-W5 recorded (java 0, probe FREE, RAM 26.5 GB, no --purge-stale).

## Findings (what may and may not be said)

- **W-1 (DF1; binding).** "Under the deflated site null (fresh seeds, 300 reps), every declared merged-pair subsample is
  deflated-null certified (k 0 of 300, 5 of 5 at n 486 and n 441, STRONG, MID and EDGE). So is the median cut on the first
  principal axis of each STRONG and MID subsample (k 0 of 300, 5 of 5). DF1 reads ELONGATION-CONFOUNDED: not informative." It
  supports neither W-3's covariance-inflation hypothesis nor two-category structure. F-DF did not fire, so the hypothesis is NOT
  REFUTED either. Do not write "the hypothesis survived a test": DEFL-SENSITIVE was unreachable before the run (DF-J).
- **W-2 (DF2; the coordinator's question).** DISCRIMINATING is true as registered: the deflated null does not deflated-null
  certify every declared partition. It does NOT license "the deflated null discriminates real from spurious structure". The ratios
  in row 13 explain DF2 mechanically. Deflation lowers the null only as much as the deflated axis carried variance: to 44-61% of
  the plain p95 on merged pairs, where the declared axis is the dominant one (the PC1 cut agrees with the declared split on
  467-484 of 486), and to 90-102% on source splits, where the axis carries almost none. The deflated null and the declared
  statistic both track the variance along the cut axis. So it passes any cut along a dominant axis (the EC controls; my synthetic
  unimodal and bimodal checks in READY_cert_k2_deflated_delta row 6, k 0 in every draw) and rejects any cut along a weak axis
  (the source splits' J 0.014-0.019 is 22-28% of the deflated p95). What separates the two cases is axis variance, not discrete
  structure. Licensed: "the deflated null certifies cuts along high-variance axes, whether or not the population has discrete
  structure there, and does not certify low-variance source-family splits." L24134's caveat stands (nothing about source-family
  structure).
- **W-3 (G12's 0 of 60).** Nothing is licensed beyond the registered WOULD NOT and the outcome's "the deflated null does not
  demand more than the cut axis's own spread". In particular, NOT: "G12's splits are real but under-certified", "the plain null is
  too demanding", or that G12's TOP splits would pass under deflation. A data-driven split is the splitter's own high-separation
  cut, which is the class W-2 shows the deflated null passes by construction. So passing it would be evidence of nothing, and the
  deflated null is not a candidate supplementary certificate for data-driven sites (an instrument statement, licensed by the EC
  controls). The plain J site null stays the certificate of record. CERT-PC-K2-KNOWN W-5 and F-TAX N-1 / F2 stand.
- **W-4 (replication).** 30/30 agreement is a ceiling effect (k = 300 in both draws); report it as "both deflated draws place
  every replicate above the source-split statistic", not as a replication of a discriminating result. KK has no earlier deflated
  values (R-1).
- **W-5 (DF0).** VALID-NULL rules out a collapsed deflated null (reached 300/300 on every site, so no DEGENERATE site anywhere).
  It is not a calibration result: 11 of 20 controls could not pass.
- **PROC-1 (LOW).** In rp12-r2-run the path checkout left the four files STAGED in that worktree's index (A/M). The next
  operator there should run `git restore --staged --worktree` on them, or keep the index state deliberate, before any other path
  checkout. No commit was made there.

## Registrar's wording (verbatim proposal)
CERT-K2-DEFLATED (zero calls; VALID; draw 5a3e756 TRAIN, B0 MMLU_PRO_LB, qwen3 512, sepBar 0.0145, 300 reps, deflated seed base
20261004): IDENTITY reproduced (0.107803). DF0 VALID-NULL, 0 of 20: the deflated null did not collapse (reached 300/300); not a
calibration test, since 11 of 20 controls could not pass. DF1 ELONGATION-CONFOUNDED: STRONG and MID are deflated-null certified
5 of 5 at n 486 (k 0 of 300). So are their PC1 median-cut controls (5 of 5, k 0). STRONG margin 0.007269 > SD 0.002022; MID
-0.000274 < SD 0.002416. Not informative about two-category structure or the covariance-inflation hypothesis; F-DF NOT FIRED (not
refuted, not supported; DEFL-SENSITIVE was unreachable pre-run, DF-J). DF1b DEFL-CERTIFIED, ELONGATION-UNCONTROLLED (descriptive).
DF2 DISCRIMINATING, 0 of 3 (k 300 of 300): the deflated null certifies cuts along high-variance axes, with or without discrete
structure, and not the low-variance source-family splits. Its p95 is 0.44-0.61 of the plain p95 on merged pairs and 0.90-1.02
on source splits. This is axis variance, not structural discrimination. Nothing about source-family structure, and nothing about
G12's 0 of 60 beyond 'the deflated null does not demand more than the cut axis's own spread'. The deflated null is not a
candidate certificate for data-driven sites; the plain J site null remains the certificate of record. P1 FAILED (0.0555 vs
[0.085, 0.118]); P2 Brier 0.765 (re-stated; SENSITIVE settled pre-run); P3 0.375; P4 0.0025; P5 HELD ×2 (0.09 each).
Replication 30/30 (both draws k 300: a ceiling, not a replication of discrimination).

## Commands
```
sha256sum -c E:/TaxoArena_backup_2026-10-04_cert_k2_deflated/SHA256SUMS.txt (backup and run dir: 9/9 OK)
python (own): replicates.csv/sites.csv -> k, reached, words, DF0/DF1/DF2, margins, P1, Brier (rows 1-11); np.percentile check
python (own): df_sites defl_p95 / plain null_p95 of record (kk_sites.csv, pk2_sites.csv) -> row 13
python (own): outcome.txt lines vs ops_20261004/08_analyze.txt (163 lines, 1 encoding-only difference)
grep -aoi 'certif' outcome.txt replication.txt (filtered to the allowed forms -> 0); grep of 07_arm_transcript.txt / ops_log.txt
```
