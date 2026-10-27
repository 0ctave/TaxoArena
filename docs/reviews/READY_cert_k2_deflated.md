# READY review — CERT-K2-DEFLATED (branch cert-k2-deflated, tip bc4a3ef0)

Reviewer: adversarial-reviewer, 2026-10-04. Zero calls. Registration: prog L24123-L24141 (fac3d50b) plus the registrar's
pre-data brackets a4965da8 (L24126 R-1, L24129 IDENTITY / DEGENERATE warning only, L24132 DF0 scope).
Reviewed blobs (LF of record; `git hash-object`, and `--no-filters` for the CRLF working-tree rendering):
- tools/analysis/cert_k2_deflated.py blob:0ab1b167 sha256-lf16:6cc0b9033529d24e (the working tree is LF)
- src/test/kotlin/taxonomy/SeparationNullBySizeTest.kt blob:a65b6ca1 sha256-lf16:2316a5a8d76504ba; CRLF working tree
  blob ad5a53b3, sha256-crlf16:cd09039a6be8ff63 (= the builder's "SNBST sha256 cd09039a": that is the CRLF rendering)
- src/test/kotlin/taxonomy/CertK2DeflatedArmTest.kt blob:d1f5fc36 (LF in the working tree)
- build.gradle.kts blob:0ad3e35c sha256-lf16:261953e153537aa5; CRLF working tree blob 28337adc, sha256-crlf16:e485f27ce1058ff6

## VERDICT: NOT READY (one BLOCKER: what the result may be read as; the build itself is sound)

The code does what the registration says, and it is byte-exact. The KK and K2 sites match the files of record; the site file
reproduces pin 251b4f20; the arm is the existing deflation code with the fresh seed base 20261004; the 169 existing members are
bytecode-identical and the new code demonstrably executed; selftest 12/12; mutants 85/85; K18 is truly equivalent.
**B-1:** the registered READING of the deciding outcome is not licensed. The deflated null deflated-null-certifies a median cut of a
**unimodal** elongated Gaussian (k 0 of 60) that the plain null rejects (k 30 and 60 of 60). So DEFL-SENSITIVE is predicted by
elongation along the declared axis alone. It cannot be read as "two-category structure certifies" or as support for W-3's
covariance-inflation hypothesis, and DF0 (random relabellings, declared statistic about 0) cannot detect this failure mode. Only
the refuting direction (F-DF) is informative.
**Path to READY:** the registrar's pre-data bracket per B-1 option (a), plus a delta review (≤ 3 mutants), or option (b) (the
author's or registrar's choice).

## Per-claim table (deciding claims)

| # | claim | result | reviewer's number vs claimed | sev |
|---|---|---|---|---|
| 1 | deflated null = the existing variant (cpcDeflate, k-1 dims, mean kept), FRESH seeds | CONFIRMED | dflDeflatedSite = cpcDeclaredSite's deflated branch verbatim (cpcMoments -> cpcDeflate -> cpcSiteArm), only tag SNDF and base 20261004 differ; CertK2DeflatedArmTest asserts equality with cpcSiteArm(SNDF, 20261004) and inequality with base 88820260908 (4/4 run in my build) | - |
| 2 | KK / K2 rows = the files of record byte for byte; 87-site pin 251b4f20 | CONFIRMED | my dry-run: KK sha 8e122edd, K2 efcc4e99 (rebuilt, and compared with the on-disk files, which are present: sha256 8e122edd42a044ad / efcc4e99cf5eed50); site file 87 sites, 50,304 rows, sha256 251b4f201ee7… = the pin; declared check IDENTITY abs diff 3.33e-16, 63 sites max 4.98e-07 ≤ 5e-07 | - |
| 3 | 20 NC sites: seeds 1-10, size-matched, never the source or its complement | CONFIRMED | Python relabel + Kotlin dflSiteError (15 refusal fixtures); groups 262/224 and 191/295 = the sources' | - |
| 4 | DF0 gate is a meaningful null check | PARTLY (bracketed L24132) | 11 of 20 NC sites have declared < 0 (STRONG s1,2,4,5,7,8,9; math s1,2,3,9): a replicate that does not split scores 0.0 ≥ declared, so k = 300 whatever the null. DF0 can fire only through the other 9 sites, and only if ≤ 14 of 300 replicates clear about 0. It detects collapse, not calibration (C-2) | MEDIUM |
| 5 | DF1 at n 486 on STRONG and MID; DF1b; DF2; F-DF exactly as registered | CONFIRMED (code) | size_word 4-of-5 / ≤ 1; df1 both pairs; F-DF iff DEFL-INSENSITIVE; NOT EVALUABLE under ANTI-CONSERVATIVE; my mutants X1-X3 killed | - |
| 6 | the DEFL-SENSITIVE reading ("covariance-inflation hypothesis SUPPORTED; declared two-category structure deflated-null certified") | REFUTED as a licensed reading | reviewer's demo (synthetic, 60 reps, n 486, dim 256): unimodal cloud, median cut on its long axis. Strong: declared 0.058139, plain k 30/60 (p95 0.0779), deflated k 0/60 (p95 0.0107, reached 60/60). Mild: declared 0.015159, plain k 60/60 (p95 0.0209), deflated k 0/60 (p95 0.0107, reached 60/60) | BLOCKER (B-1) |
| 7 | no deflated result is ever worded "certified" | CONFIRMED | wording_violations scans every outcome line before the write (M78/M79 killed; my X4, the registration's own wording "structure certifies once", is KILLED by the scan). replication.txt is not scanned but holds no "certif" literal | - |
| 8 | the earlier deflated columns are read only after the run | CONFIRMED | read_record refuses defl*; --replication refuses without outcome.txt and df_sites.csv (M63 killed). R-1 is true: KK arm sites.csv has 34 rows, 0 non-empty defl cells. pk2_sites.csv's defl_k column is parsed into memory and dropped, never printed (C-5) | LOW |
| 9 | inertness: 169 members identical; proof of execution | CONFIRMED | my own compile of fac3d50b vs bc4a3ef0 (git archive to E:): main class 169/169 identical, 14 added; other classes 40 byte-identical, 9 javap-identical, 0 different; 1 new class $DflSite. Branch javap counts certK2Deflated 37, dflSiteError 2, dflDeflatedSite 2, dflSeedBase 3, 20261004 1 (= the builder's). Executed: CertK2DeflatedArmTest 4/4; `gradlew certK2Deflated` with no props runs exactly 1 testcase and refuses "-DsnapshotId is required"; nullBySize excludes it (build.gradle.kts L240) | - |
| 10 | K18 (tag SNDF -> SND) is EQUIVALENT | CONFIRMED | the tag enters only registry keys and log labels (runReplicate). The splitter sorts targetQueries by queryId first (unique 0..n-1), so rawText never breaks a tie. runVmfEm has no randomness; the only splitter RNG is seeded by n and depth (L527). The statistic is node.dasguptaDeltaNorm. The mutant's survival is itself an equality on the fixture | - |
| 11 | Support: DEFF 1.0 by construction, SE 0.0126, MDE80 0.0352 | CONFIRMED | sqrt(0.05·0.95/300) = 0.01258; 2.8 × 0.01258 = 0.03523. Source: no item resampling (CERT-PC-K2-KNOWN C-4). Non-vacuous as arithmetic; B-1 is a validity defect, not a power one | - |
| 12 | wall about 46 min, heap 0.45 GB | CONFIRMED | 1503 s × 23,708,559 / 13,029,360 = 45.6 min; peak 0.45 GB (live 12, n max 1282) | - |
| 13 | selftest 12/12; mutants 85/85 (M0 survives) | CONFIRMED | re-run: 12/12; 85 of 85 killed, M0 SURVIVED | - |

## Defects and fixes

- **B-1 (BLOCKER; the registrar's, pre-data).** DEFL-SENSITIVE does not separate "two distinct categories" from "one elongated
  mode". The deflated null removes exactly the axis the declared cut separates on, so any cut along a high-variance axis
  certifies (row 6). FIX, option (a), cheap: bracket the READING pre-data and reword SENT_SUPPORTED to match. Suggested text:
  "DEFL-SENSITIVE is also what elongation along the declared axis alone produces (reviewer's unimodal demo, READY_cert_k2_deflated
  row 6). It shows the deflated null does not demand more than the declared axis's own spread; it does NOT support the
  covariance-inflation hypothesis over 'elongation only', and it licenses no statement about two-category structure." F-DF and its
  REFUTE sentence stay unchanged (the informative direction). The WOULD (if DEFL-SENSITIVE) line at L24139 needs the same bracket.
  Then update the selftest needle, run M22/M23 plus one mutant on the new sentence, and send it for a delta review. Option (b),
  more work: add an elongation-cut control (per NC source, a size-matched median cut along the source population's PC1, or on a
  withinNodeCloud Gaussian twin) as a gate before DF1. This needs a new site-file pin, Kotlin additions and a delta review.
  AUTHOR / REGISTRAR DECISION: (a) or (b).
- **C-1 (MEDIUM).** DEGENERATE is a warning only (L24129). This conflicts with CERT-PC-SIZE Q-2 (L23771, "a collapsed null
  certifies nothing"): a deciding KK subsample whose deflated null reaches < 20 of 300 can count as DEFL-CERT. FIX: in the
  post-run reading, name every DEFL-CERT deciding subsample with reached < 20 and do not use it as evidence. The registrar may
  re-rule this pre-data.
- **C-2 (MEDIUM).** DF0 arithmetic (row 4). FIX: the outcome / record should state "11 of 20 NC sites cannot DEFL-CERT (declared
  < 0)". P4's Brier score is not a calibration score of the deflated null.
- **C-3 (LOW, operational).** rp12-r2-run (at 8419d4ce) does not merge bc4a3ef0 cleanly: CONFLICT in build.gradle.kts and SNBST.
  CERT-PC-K2-KNOWN reached main by squash, so the histories differ. `git diff 8419d4ce fac3d50b` over src, build.gradle.kts, the
  imported cert_*.py, g12_site_null.py, data_v2.py and experiment_configs/rp12_r2 is EMPTY, so a path checkout of the four files
  gives exactly the branch's content (launch step 2).
- **C-4 (LOW).** Own mutant X6 (replication guard checks outcome.txt only) SURVIVED. Non-decisive: analyze writes both files in
  one pass. X5 (relabel on unsorted ids) SURVIVED as an equivalent mutant: the labels dicts are id-sorted, and the run is also
  guarded by pin 251b4f20.
- **C-5 (LOW).** Blindness holds at the print level only. pk2_sites.csv rows (with defl_k) are parsed and then dropped.

## Own mutants (6 Python; Kotlin K18 checked by reading plus its survival)
X1 DF2 ungated: KILLED (decisive) · X2 DF1b ungated: KILLED (decisive) · X3 size_word substring count ("not DEFL-CERT" counted):
KILLED (decisive) · X4 SUPPORTED sentence worded "structure certifies": KILLED by the wording scan (decisive) · X5 relabel on
unsorted ids: SURVIVED, equivalent, pin-guarded (non-decisive) · X6 replication guard's CSV leg removed: SURVIVED (non-decisive).

## Launch sequence (run-operator; ONLY after B-1 is resolved; rule-7 heavy process, about 46 min, 12 threads)
1. W1-W5: no java (`Get-Process java` empty), no construction, site null or pool reader; ≥ 12 GB RAM free; foreign python
   processes WAIT, they are never killed. Temp: CKD_TMP defaults to E:/TaxoArena_tmp.
2. `cd .claude/worktrees/rp12-r2-run` (clean tracked tree at 8419d4ce), then
   `git checkout <reviewed tip> -- build.gradle.kts src/test/kotlin/taxonomy/SeparationNullBySizeTest.kt src/test/kotlin/taxonomy/CertK2DeflatedArmTest.kt tools/analysis/cert_k2_deflated.py`.
   Check that `git hash-object tools/analysis/cert_k2_deflated.py` equals the delta-reviewed blob.
3. `python tools/analysis/cert_k2_deflated.py --selftest` (12/12 or the fixed count), then `--mutants` (all killed; M0 survives).
4. `$env:TAXOARENA_DATA_ROOT='<main checkout>'; python tools/analysis/v2_union_pool.py --dry-run` (rc 0; pool sha256-lf16
   79d48f4b36434a55); then `Remove-Item Env:TAXOARENA_DATA_ROOT`.
5. `python tools/analysis/cert_k2_deflated.py --dry-run`: site file 251b4f20 "= the pin"; declared check 63 sites max ≤ 5e-07;
   LAUNCH FROM = this checkout, with no "preview" note.
6. `--prepare`, then `--hashes before`.
7. `.\gradlew.bat certK2Deflated --console=plain --offline --no-daemon -PjvmThreads=12 -PnullReps=300 "-DsnapshotId=20261001_094311_Headless_Run_Auto_ge" "-DsliceDim=512" "-DsepBar=0.0145" "-DdropTop=0" "-Dwhiten=false" "-DsiteLabels=experiment_results/cert_k2_deflated/site_labels.tsv" "-DoutDir=experiment_results/cert_k2_deflated/arm"`
   then `.\gradlew.bat --stop`; java count 0.
8. `--hashes after`; `--analyze`; only then `--replication`. Back up to E:/TaxoArena_backup_2026-10-04_cert_k2_deflated with
   SHA256SUMS.txt; never commit the outputs.

## Commands (all read-only on DBs of record; temp under E:/TaxoArena_tmp, removed afterwards)
```
python tools/analysis/cert_k2_deflated.py --selftest                       # 12/12
python tools/analysis/cert_k2_deflated.py --mutants                        # 85 of 85 killed; M0 SURVIVED
python tools/analysis/cert_k2_deflated.py --dry-run --data-root .claude/worktrees/rp12-r2-run   # rc 0; 251b4f20 = pin
sha256sum rp12-r2-run/embeddings_cache.db before == after (afe21525…, mtime 1790843339 unchanged); -wal 0 bytes
python E:/TaxoArena_tmp/ckd_rev_mut.py                                     # X1-X6 (above)
git archive bc4a3ef0 / fac3d50b -> E:/TaxoArena_tmp/ckd_rev_{branch,base}; gradlew test --tests *CertK2DeflatedArmTest*
  (4/4) + temporary ReviewElongationCutDemoTest (export only, never in a worktree; output row 6); gradlew compileTestKotlin
  (base); javap -p -c, "#N" normalised, member-split compare (row 9); gradlew certK2Deflated without props (1 testcase,
  refused); gradlew --stop; java count 0
python: csv KK arm sites.csv defl* non-empty cells = 0 (R-1); headers of pk2_sites.csv / kk_sites.csv only
git diff --stat 8419d4ce fac3d50b -- src build.gradle.kts tools/analysis/{cert_pc_k2_known,cert_pc_k2,cert_pc_size,cert_positive_control,g12_site_null,data_v2}.py experiment_configs/rp12_r2   # empty
git merge-tree --write-tree --name-only 8419d4ce bc4a3ef0                  # CONFLICT build.gradle.kts, SNBST
git ls-files --eol; git hash-object [--no-filters] <4 paths>               # pins above
```
