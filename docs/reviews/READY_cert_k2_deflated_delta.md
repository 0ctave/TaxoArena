# Delta READY review — CERT-K2-DEFLATED amended build (bc4a3ef0 -> 1d282351)

Reviewer: adversarial-reviewer, 2026-10-04. Zero calls. Scope: `git diff bc4a3ef0..1d282351` (4 files, +710/-186) and
regression. Record: amendment 26605924 (L24127, L24129, L24132-L24138), the DF-J disclosure 156a9790 (L24132, L24133,
L24137, L24138), and the prior review READY_cert_k2_deflated.md (a45b4c10). Anything that review CONFIRMED on code this delta
does not touch is cited, not re-derived.
Pins (LF of record = `git rev-parse 1d282351:<path>` = `git hash-object`; CRLF working tree via `--no-filters`):
- cert_k2_deflated.py blob:f5f7f178 sha256-lf16:b2044a79edd823ca (working tree LF)
- CertK2DeflatedArmTest.kt blob:e0f326e1 sha256-lf16:fd316d03478301d4 (working tree LF)
- SeparationNullBySizeTest.kt blob:cb91cdcd sha256-lf16:ef5cc8a1af871499; CRLF working tree blob 25079655, sha256-crlf16:53c42ac4a4212bfb
- build.gradle.kts blob:9a70c27e sha256-lf16:1942055e3949d011; CRLF working tree blob c9b1c786, sha256-crlf16:f284a2569005e616
- site file (97 sites, 55,164 rows) sha256 00c002394ed99431b0189e5c00c6b7c265a53f6133f6d50197fa0ca8362c0110: reproduced by my dry-run

## VERDICT: READY (B-1 of a45b4c10 resolved by option (b)); conditions C-1..C-3 below are reading and process conditions, with no code change owed

The control is what the amendment registers, and DF1 is one exhaustive rule matching L24133 cell by cell. On a pure elongation
the control does what it is for: the pair reads ELONGATION-CONFOUNDED. DEFL-SENSITIVE cannot be reached on this data. That is
SEEN PRE-ARM and disclosed (DF-J, 156a9790): F-DF is the only live deciding question, and it is still open.

## Per-claim table

| # | claim | result | reviewer's number vs claimed | sev |
|---|---|---|---|---|
| 1 | control = TRAIN-only median cut on the first principal axis of each deciding n-486 site; ties to the lower half | CONFIRMED | ec_cut: SVD of the site's 486 centred unit rows (PKK.load_vectors, 512 slice, L2-normalised, the same rows as the declared routine; the declared check matches 63 records). The ids are the KK sites' TRAIN ids. Lower median at rank (n-1)//2, so pc_lo ≥ half. MY INDEPENDENT recompute (numpy eigh of the scatter, my own cut): labels agree 486/486 on all 10 sites | - |
| 2 | same deflated null, fresh seeds | CONFIRMED | the arm runs EC_* through the unchanged dflDeflatedSite (deflation on the control's OWN between-centroid axis, tag SNDF, base 20261004, seed id = the EC site name); dflEcError checks names, ids = source, labels, ≥ half, ≠ declared or its complement (9 refusal fixtures, 5/5 class tests run) | - |
| 3 | control declared statistics and margins (deciding, clause (b)) | CONFIRMED to the digit | STRONG: declared 0.121796/0.122262/0.118862/0.124375/0.120776 vs cut 0.114274/0.114332/0.112621/0.116341/0.114157; margin 0.007269 > SD 0.002022. MID: cut 0.102809/0.105915/0.106902/0.109471/0.106914; margin -0.000274 < SD 0.002416. The cut agrees with the declared split on 467/486 (STRONG) and 482-484/486 (MID) | - |
| 4 | DF1 one exhaustive rule as L24133 | CONFIRMED | 16/16 pair-word combinations equal my independent coding of L24133; 72/72 (count, control count, margin) cases of the pair rule equal L24133; NOT EVALUABLE via Q-K1 over(); DF1b prints "DEFL-CERTIFIED, ELONGATION-UNCONTROLLED", INSENSITIVE stands | - |
| 5 | DEFL-SENSITIVE reachable? | IMPOSSIBLE (disclosed) | with MID's margin false, no admissible MID word gives SENSITIVE-PAIR (enumerated). That is impossible at ANY budget, not underpowered. Recorded pre-run (156a9790): P2's 0.15 is settled | - (C-1) |
| 6 | the control flags a pure elongation (my synthetic check, 60 reps, n 486, dim 256, 5 draws each) | CONFIRMED | unimodal strong: k_decl 0×5, k_ctrl 0×5, margin -0.002356 vs SD 0.003216 -> ELONGATION-CONFOUNDED. Unimodal mild: k 0×5 and 0×5, margin -0.002765 vs SD 0.000926 -> ELONGATION-CONFOUNDED. BUT a well-separated BIMODAL population (two clusters ±0.12 on one axis, sd 0.06, sizes 262/224) also reads ELONGATION-CONFOUNDED (margin -0.001137 vs SD 0.001089) | MEDIUM (C-2) |
| 7 | DEGENERATE = NOT EVALUABLE for every site class; DF0 NOT EVALUABLE fails the gate | CONFIRMED | site_word returns NOT EVALUABLE (DEGENERATE) when reached < 20; df0 = one(...) and valid iff VALID-NULL (N16 kills "NE passes") | - |
| 8 | inertness: 169 members; the new code ran | CONFIRMED | my own compile of fac3d50b vs 1d282351: 169/169 identical, 15 added (adds dflEcError); other classes 40 byte-identical + 9 javap-identical, 0 different; +1 class $DflSite. javap counts dflEcError 2, certK2Deflated 37. Executed: CertK2DeflatedArmTest 5/5 (the amended site check calls dflEcError) | - |
| 9 | tests 558, 2 known failures | CONFIRMED | `gradlew test --offline` in the worktree: 558 completed, 2 failed = MrlRoutingTest, TraceEnvelopeUnwrapTest; worktree git status clean afterwards | - |
| 10 | selftest 13/13; mutants 115/115 | CONFIRMED | re-run --selftest 13/13; --mutants 115 of 115 killed, M0 SURVIVED. Own delta mutants: Y1 pair rule ignores the control KILLED (decisive); Y2 margin vs the cut's SD KILLED (decisive); Y3 upper median in ec_cut KILLED (decisive). Kotlin 10/10 not re-run (the delta's Kotlin is a structure check, covered by the 9 refusal fixtures plus my javap) | - |
| 11 | dry-run: 97-site pin, wall, no DB write | CONFIRMED | --dry-run --data-root rp12-r2-run rc 0; 00c00239 "= the pin"; wall about 50 min (1503 s × 26,070,519 / 13,029,360 = 50.1 min); embeddings_cache.db sha256 afe21525… before = after | - |

## Conditions (no code change owed)

- **C-1 (reading; recorded by DF-J).** DF1 can only read DEFL-INSENSITIVE (F-DF fires), MIXED, ELONGATION-CONFOUNDED or NOT
  EVALUABLE. The post-run review checks that no outcome prose implies a SENSITIVE reading was possible. The STRONG pair's
  SENSITIVE-PAIR word is descriptive only.
- **C-2 (MEDIUM; for the registrar's outcome wording).** In my synthetic check the margin rule also rejects a genuine,
  well-separated bimodal population: the PC1 median cut matches or beats the true labels on J. So ELONGATION-CONFOUNDED is "not
  informative" in BOTH directions (L24133 already says this). It must never be worded as evidence AGAINST two-category structure,
  nor as "the declared split is an elongation". The MID declared split is 482-484/486 identical to its PC1 cut (descriptive,
  pre-arm).
- **C-3 (PROCESS, HIGH for every agent using E:/TaxoArena_tmp).** During this review a peer's
  `scratch_dir.py --purge-stale` (the marker E:/TaxoArena_tmp/.taxoarena_scratch was written 04:15, and a nested
  E:/TaxoArena_tmp/TaxoArena_tmp/ was created 04:20) DELETED my live temp entries minutes old: the base export, the dry-run log,
  a running mutant log, and the older `sdv/`. This is the D-1 hazard of READY_scratch_dir_e.md, live in the field. I redid the
  lost steps; logs moved to the session scratchpad. FIX: no `--purge-stale` on the shared base until D-1 merges; the run-operator
  keeps the arm's outputs under experiment_results/ (never in the scratch base).
- Carried over from a45b4c10: C-3 (path checkout, not merge), C-5 (blindness at print level). C-4 X6 is fixed per the commit; not re-tested.

## Launch sequence (run-operator; rule-7 heavy process; about 50 min at 12 threads)
1. W1-W5 (no java, no construction / site null / pool reader, ≥ 12 GB RAM free; foreign processes WAIT). No `--purge-stale`
   anywhere during the window (C-3).
2. In .claude/worktrees/rp12-r2-run (clean tracked tree at 8419d4ce):
   `git checkout 1d282351 -- build.gradle.kts src/test/kotlin/taxonomy/SeparationNullBySizeTest.kt src/test/kotlin/taxonomy/CertK2DeflatedArmTest.kt tools/analysis/cert_k2_deflated.py`;
   `git hash-object tools/analysis/cert_k2_deflated.py` = f5f7f178.
3. `python tools/analysis/cert_k2_deflated.py --selftest` (13/13), then `--mutants` (115/115, M0 survives).
4. `$env:TAXOARENA_DATA_ROOT='<main checkout>'; python tools/analysis/v2_union_pool.py --dry-run` (rc 0; pool sha256-lf16 79d48f4b36434a55); `Remove-Item Env:TAXOARENA_DATA_ROOT`.
5. `--dry-run`: 00c00239 "= the pin"; MARGIN lines as row 3; LAUNCH FROM = this checkout, with no preview note.
6. `--prepare`; `--hashes before`.
7. `.\gradlew.bat certK2Deflated --console=plain --offline --no-daemon -PjvmThreads=12 -PnullReps=300 "-DsnapshotId=20261001_094311_Headless_Run_Auto_ge" "-DsliceDim=512" "-DsepBar=0.0145" "-DdropTop=0" "-Dwhiten=false" "-DsiteLabels=experiment_results/cert_k2_deflated/site_labels.tsv" "-DoutDir=experiment_results/cert_k2_deflated/arm"`;
   then `.\gradlew.bat --stop`; java count 0.
8. `--hashes after`; `--analyze`; then `--replication`. Back up to E:/TaxoArena_backup_2026-10-04_cert_k2_deflated with SHA256SUMS.txt; never commit the outputs.

## Commands
```
python tools/analysis/cert_k2_deflated.py --selftest                     # 13/13
python tools/analysis/cert_k2_deflated.py --mutants                      # 115 of 115 killed, M0 SURVIVED
python tools/analysis/cert_k2_deflated.py --dry-run --data-root .claude/worktrees/rp12-r2-run   # rc 0; 00c00239 = pin
python <scratchpad>/ckd_d_ec.py        # independent eigh PC1 cut: 486/486 x10; margins 0.007269 / -0.000274; SDs 0.002022 / 0.002416
python - (enumeration)                 # df1_definite 16/16, pair rule 72/72 vs L24133; SENSITIVE unreachable with MID margin false
python <scratchpad>/ymut.py            # Y1-Y3 KILLED
git archive 1d282351 / fac3d50b -> E:/TaxoArena_tmp/ckd_d_{branch,base}; temporary ReviewEcControlDemoTest (export only) -> row 6;
  compileTestKotlin (base); javap -p -c "#N"-normalised member compare -> row 8
.\gradlew.bat test --offline (worktree)  # 558 completed, 2 failed (the two known); .\gradlew.bat --stop; java count 0
```
