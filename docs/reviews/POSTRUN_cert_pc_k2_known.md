# POSTRUN review: CERT-PC-K2-KNOWN (arm + readout at 8419d4ce, cert_pc_k2_known.py 15717e13)

Reviewer: adversarial-reviewer, 2026-10-03. Prior review: READY_cert_pc_k2_known.md (NOT READY on D-1; C-1 owed a delta review before launch).
Data root .claude/worktrees/rp12-r2-run at 8419d4ce (`git rev-parse`). Blobs there by `git hash-object` (LF): cert_pc_k2_known.py 15717e13, SNBST
3401d4d7, build.gradle.kts 07451aa1, cert_pc_k2.py 38fb0dfc. Ops 38b32f13 + 4c76baf4 (branch cert-pc-k2-known, logs ops_20261003/, 10 files).
The outputs are untracked and write-once, sha256-16: outcome.txt 27061cd4a163024d (133 lines); kk_sites.csv 691f83bc4cab19d2; arm/sites.csv 0737058e5ccc7406;
arm/replicates.csv cecf4ccb5cc5063b; site_labels.tsv 8e122edd... (= pin); stage0.tsv 0c32bb81... (= pin). The backup E:\TaxoArena_backup_2026-10-03_cert_pc_k2_known
passes `sha256sum -c` (9/9 OK), and all 9 files `cmp` equal to the run copies. Zero calls. My only DB read was rp12-r2-run/embeddings_cache.db, opened `mode=ro&immutable=1`.

## Verdict

**VALID. KK1 (n 486) NO-CONTROL and KK2 (n 441) NO-CONTROL: G-KS gives NOT-A-CONTROL on all three pairs. F-KK NOT FIRED. IDENTITY reproduced (= PC1);
C0 comparable 33/33.** Every deciding number reproduces to the digit from the arm's own outputs. All 34 declared statistics reproduce from an independent
numpy recompute on the cache (max |diff| 1.1e-15). Under the registration this is **a registered non-outcome: "nothing about the certificate"** (prog L24046 as
bracketed; the readout prints the same sentence). It is the second k = 2 positive control that failed to qualify (after CERT-PC-K2). The Q-KK1 ruling was not
exercised: readings A and B are both NO-CONTROL, with 0 gated pairs.

## Per-claim table (deciding claims)

| # | claim (outcome) | my number | status | sev |
|---|---|---|---|---|
| 1 | IDENTITY 0.107803, k_d 0, p95 / max 0.041626 / 0.042414 = PC1 | recount from replicates.csv: k 0, p95 0.041626, max 0.042414; numpy 0.107803; the transcript's IDENTITY line comes before the 33 `[PKK] site` lines | CONFIRMED | - |
| 2 | STRONG full (n 1254) CERTIFIED, k_d 14, p_d 15/301 = 0.0498 | k 14 (#{SN >= 0.119598}); p95 0.119418; null median 0.113552, min 0.101754; reached 300; C0 p95 0.000475 < p95 | CONFIRMED | - |
| 3 | G-KS STRONG NOT-A-CONTROL: margin 0.000180 vs sample SD 0.002022 (pop. SD 0.001808, word unchanged) | 0.119598 - 0.119418 = 0.000180; SD over the five n-486 statistics: ddof 1 0.002022, ddof 0 0.001808 | CONFIRMED | - |
| 4 | MID full NOT CERTIFIED k_d 172; EDGE full NOT CERTIFIED k_d 298 | k 172 (p95 0.111782 > 0.105456); k 298 (p95 0.081670 > 0.070390); margins -0.006326 / -0.011280 | CONFIRMED | - |
| 5 | per pair and size: n 486 0/5 for all three; n 441 STRONG 2/5 (MIXED), MID 0/5, EDGE 0/5; NOT EVALUABLE 0 | k at n 486: STRONG 26/23/31/22/42, MID 135/130/119/111/114, EDGE 201/195/224/201/219; n 441: STRONG 21/6/20/12/23 (d2, d4 certified), MID 86/70/71/45/77, EDGE 166/106/141/126/142 | CONFIRMED | - |
| 6 | KK1 = KK2 = NO-CONTROL (A and B); F-KK NOT FIRED | 0 of STRONG / MID gated, so NO-CONTROL under the ruling and under reading B | CONFIRMED | - |
| 7 | C0 comparable 33/33 | C0 p95 recount = the arm's c0_p95 to the bit, 33/33 (0.000347-0.001810, all far below null p95); declared > C0 max on 33/33 (largest C0 max 0.004313) | CONFIRMED | - |
| 8 | predictions: P1 STRONG FAILED, MID / EDGE HELD; P2 Brier 0.81 / 0.64 / 0.09; P3 NO-CONTROL Brier 0.9750; P4 0.116337 FAILED; P5 yes, Brier 0.0225 | 0.1196 < 0.12; P2 0.9^2, 0.8^2, 0.3^2; P3 0.55^2 + 0.10^2 + 0.15^2 + 0.80^2 = 0.9750; P4 = the 8th of 15 sorted n-486 null p95 = 0.116337; P5 0.15^2 | CONFIRMED | - |
| 9 | data object / instrument | status COMPLETE, arm certKnownPair, snapshot 20261001_094311, reps 300, slice 512, sepBar 0.0145, dropTop 0, whiten false, mcs 55, c0Seed 20261002, threads 12; site sha = pin; 67 arm series (34 SN + 33 C0), reps 0..299 in order; emb hashes before == after (17c31d55... both) | CONFIRMED | - |
| 10 | console = outcome; write-once | 132 of 133 outcome lines appear verbatim in 08_analyze.txt (CR stripped). The remaining one is the registration line (em-dash encoding). The selftest ran 15/15 first. My second `--analyze` REFUSED ("outcome.txt exists: the outcome is write-once"), and the md5s of outcome, csv and arm/* are unchanged | CONFIRMED | - |
| 11 | C-1 (READY D-1) fixed before launch | diff 14ae100a..8419d4ce = exactly the D-1 fix (constant, 3 selftest calls pinned `ruling=None`, a new case on the ruled default, M79 / M80). My re-run: selftest 15/15, mutants 80/80 with M79 / M80 KILLED and M0 SURVIVED; READY R1 now passes. **No delta review was committed before launch** (PROC-1) | CONFIRMED (fix) / REFUTED (process) | MEDIUM |

## C-4: re-derivation and Support after the run

DEFF 1.0: no item clustering enters an exceedance count of independently seeded replicates; that is the structure of the object, as in CERT-PC-K2 POSTRUN C-4. n_eff 300 per site; SE at
the bar 0.0126; MDE80 0.0352. Deciding counts beside them: STRONG full p_d 0.0498, which is 0.0002 from the bar, well inside one SE. A re-draw of the null could flip this site either way,
but G-KS fails on its margin clause regardless, because 0.000180 is less than 0.002022. MID full p_d 0.575 and EDGE full 0.993 are far from the bar. Full counts at n 486: certified 0 / not 15 / C0 0 / degenerate 0.
At n 441: 2 / 13 / 0 / 0. EDGE is descriptive throughout.

## C-5: wording carried

STRONG and MID share law (224 / 243 law items at n 486), so they are not two independent controls. The draws overlap at about chance (n 486: 177-220 of 486), and n 441 partly re-reads n 486.
Stage 0 ran before the ruling (L24049): the selection is mechanical, and P1's STRONG part was determined pre-arm.

## Descriptive (no criterion; DESCRIPTIVE label binding)

| site family (n 441-486 unless stated) | declared 2-way statistic | plain site-null median / p95 | declared / null median |
|---|---|---|---|
| STRONG chemistry+law | 0.119-0.126 | 0.101-0.112 / 0.119-0.127 | |
| MID engineering+law | 0.100-0.109 | 0.092-0.106 / 0.109-0.117 | all 33 KK sites: 0.89-1.20 |
| EDGE economics+physics | 0.067-0.073 | 0.068-0.078 / 0.081-0.087 | |
| CERT-PC-K2 (within one category) | 0.014-0.019 | - / 0.067-0.071 | |
| CERT-PC-SIZE all-category n 486 (14-way) | 0.104-0.118 | - / 0.054-0.057 | |
| IDENTITY root n 6,993 (14-way) | 0.107803 | 0.040512 / 0.041626 | 2.66 |

## The key reading: what may be written (binds the record)

- **W-1 Scope (exact).** "On R2's B0 MMLU_PRO_LB member (draw 5a3e756 TRAIN; qwen3 512-slice; sepBar 0.0145; 300 reps), no chosen pair qualified as a
  known-strength k = 2 control (G-KS NOT-A-CONTROL 3/3): only chemistry+law certified at full size (k_d 14, p 0.0498), and its margin over the null p95
  (0.00018) was below the subsampling SD (0.0020). KK1 and KK2 NO-CONTROL; F-KK not fired; a registered non-outcome about the certificate."
- **W-2 The proposed sentences are NOT licensed.** (i) "The certificate's k = 2 null is demanding enough that genuinely distinct binary structure only
  marginally certifies" is a statement about the certificate's sensitivity. NO-CONTROL was registered to say nothing about the certificate, and Support (f) /
  G-KS exist to stop exactly this inference. It also equates label-distinct with geometrically distinct. Chemistry vs law separates by 0.120 in this space, at
  the level of the 14-way root's average 0.108. The plain null measures something narrower than "distinctness" (W-3). One STRONG site at p 0.0498, within one SE of the bar,
  is one borderline site, not a pattern. (ii) "G12's 0/60 is uninformative about split quality" does not follow from (i) and is broader. G12's sites have
  their own nulls (0.054-0.070), their splits (0.036-0.040) lie below them, and nothing here was measured on a routed anchor.
- **W-3 What IS licensed (descriptive, labelled as such).** "For merged two-category sites the plain site null is large: p95 0.081-0.127 (n 441-1282),
  about twice the all-category null at the same n (0.054-0.057) and above the within-category null (0.067-0.071). The declared 2-way category statistics sit at
  0.89-1.20 of their null median: at the level that the splitter's optimised split of a Gaussian moment-matched to the same site produces. The registered P4 band
  (0.045-0.075) assumed the all-category null and FAILED by 0.04." Mechanism, a HYPOTHESIS not tested here: the plain null preserves the site's own covariance,
  including its elongation along the between-category axis. The instrument documents this (SeparationNullBySizeTest L1667-L1670: "the plain within-node null is
  inflated by the structure under test"). At k = 2 the plain certificate therefore asks for separation beyond a same-covariance Gaussian (non-Gaussian / bimodal
  structure), not for separation as such. The deflated null built for this question was not registered here (KK-4). Testing it needs its own registration (below).
- **W-4 CERT-PC-SIZE W-2.** It stands as worded ("0 of 60 not explained by n alone"), within its scope of declared 14-way structure. This test neither extends it to k = 2
  nor weakens it. The F-KK clause that would have overturned its k = 2 reading did not fire. May be added: "two k = 2 positive controls from declared labels
  (CERT-PC-K2, CERT-PC-K2-KNOWN) failed to qualify; k = 2 sensitivity of the plain site null on this member remains UNDETERMINED".
- **W-5 G12's 0 of 60.** Unchanged: F-TAX N-1 and F2 stand. Neither the K2-SENSITIVE reading ("the tree's depth-1 splits are weaker than that") nor
  the K2-SIZE-LIMIT reading ("possibly a sensitivity limit at k = 2") is available. Do not write "uninformative", "too demanding" or "insensitive".
- **W-6 Predictions.** P1 STRONG FAILED (pre-arm), MID / EDGE HELD; P2 Brier 0.8100 / 0.6400 / 0.0900; P3 NO-CONTROL, Brier 0.9750; P4 FAILED (0.116337);
  P5 HELD (Brier 0.0225).

## Defects

- **PROC-1 (MEDIUM, process; validity unaffected).** READY was NOT READY with C-1 owed a delta review before launch. The operator launched at 8419d4ce without a
  committed delta review. This review does it retrospectively (claim 11: the fix is exact, selftest and mutants pass). The ruling was not exercised (A = B), so the
  outcome cannot depend on it. Record it; do not repeat it.
- **ENV-1 (HIGH, environment, now).** C: has 0 bytes free (`df -h /c`: 931G used of 931G). My first `--analyze` re-run failed its selftest with "database or disk is
  full" (temp on C:). Gradle, temp files and every selftest are at risk. Free space before the next run. This review set TEMP to Z: for the write-once check.
- Suggested follow-up (research lead, zero calls, its own registration): the DEFLATED site null (already in the instrument) on the same 33 KK sites and the
  G12 TOP sites. It would test W-3's mechanism directly.

## Commands (compact)

```
git -C rp12-r2-run rev-parse --short HEAD (8419d4ce); git hash-object <4 blobs>; git diff 14ae100a 8419d4ce (D-1 fix only)
python cert_pc_k2_known.py --selftest (15/15); --mutants (80/80, M79/M80 KILLED, M0 SURVIVED)   [cert-pc-k2-known worktree, blob 15717e13]
python (stdin) recompute: sha256 of outputs; hashes before == after; 67 series x 0..299; numpy declared 34/34 (1.1e-15); k / p95 / C0 recount
python Z:/FAC/TUBerlin/THESIS/_ar_tmp/pr_kk.py   # G-KS margins + SDs (ddof 1/0), per-size counts, P4 median, C0 33/33, declared/null-median 0.89-1.20
grep -F -x -c -f outcome.txt <(tr -d '\r' < ops_20261003/08_analyze.txt)   # 132 of 133 (registration line: em-dash encoding)
TEMP=Z: python cert_pc_k2_known.py --analyze (rp12-r2-run)   # REFUSED write-once; md5 of outcome/csv/arm/* unchanged
cd E:/TaxoArena_backup_2026-10-03_cert_pc_k2_known && sha256sum -c SHA256SUMS.txt (9 OK); cmp vs run copies (9 equal)
grep -n "inflated by the structure under test" src/test/kotlin/taxonomy/SeparationNullBySizeTest.kt   # L1667-L1670
```
