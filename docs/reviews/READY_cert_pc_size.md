# READY review: CERT-PC-SIZE (branch cert-pc-size, tip 88bbf560)

Reviewer: adversarial-reviewer, 2026-10-02. Registration prog L23722-L23750 (02256ca6); registrar's Q-1 / Q-2 rulings
94fae9d5 (bracket at PS1 L23736, record L23767-L23772). Precedent: READY_cert_positive_control(.md, _delta.md), POSTRUN_cert_positive_control.md.
Zero calls. My only DB reads: the builder's --dry-run against rp12-r2-run (read-only; every -wal 0 bytes before and after).
The worktree was restored after the base compile (blobs re-hashed, `git status` 0 entries); gradle daemon stopped ("1 Daemon stopped", no java left).

## Verdict

**READY for the arm launch (rule-7 window)**, conditions C-1..C-4 below. The deciding paths (allocation and draw, the per-subsample
status, the gate-first size verdict, the IDENTITY precondition) reproduce, and the Support arithmetic reproduces. The 121 existing
members are bytecode-identical. One MEDIUM guard gap (D-1): the readout does not check the site file against the registered draw.
The READY covers it with a pin (C-2), so it does not block.

## Pins (blob = `git hash-object`, equal to `git rev-parse 88bbf560:<path>` for all four)

| file | blob of record | raw working-tree rendering (`--no-filters`) |
|---|---|---|
| tools/analysis/cert_pc_size.py | de39c6488e0d | same |
| src/test/kotlin/taxonomy/SeparationNullBySizeTest.kt | 3e9dd8ad348c | 53ce13aa43b6 (differs) |
| src/test/kotlin/taxonomy/CertPcSizeArmTest.kt | 92d0f25c2a75 | same |
| build.gradle.kts | d0024882a489 | aeb65b157813 (differs) |
| tools/analysis/cert_positive_control.py (imported, pinned) | e0751d7c6fe5 at 88bbf560 | - |

The stored blobs carry CR on every line (`git cat-file -p 88bbf560:<f> | grep -c $'\r'` = the line count), as cert_positive_control.py
already does. The pins are the blobs of record. Site file (C-2): sha256 231db2e0e11974b28f19244753a1c0a1a5b5c4f96ff695fead2599fe78cfe737, 16 sites, 12,948 rows.

## Per-claim table (deciding claims)

| # | claim | my number / evidence | status | sev |
|---|---|---|---|---|
| 1 | additions only | numstat 30/0, 144/0, 209/0, 1026/0; `grep -c '^-[^-]'` over the Kotlin + gradle diff = 0 | CONFIRMED | - |
| 2 | 121 of 121 pre-existing members disassemble identically; 14 new | my compile at 88bbf560~1 vs 88bbf560 (twice: full `--rerun-tasks` and incremental), `javap -p -c` with #N normalised and the constant comments KEPT: 121/121 identical, 14 new (all pcs*/certPcSize*); 47 vs 47 class files, 38 byte-identical, 8 lambda classes javap-identical, 0 javap-different | CONFIRMED | - |
| 3 | the new code executed | CertPcSizeArmTest 5/5 and CertPositiveControlArmTest 7/7 (fresh XML 18:22Z); `gradlew certPcSize` with no -D: one test selected, "[PCS] REFUSING: -DsnapshotId is required". The method's subsample branch first runs in the arm itself. There, the IDENTITY gate and the readout's k / C0 recounts discriminate | CONFIRMED (prologue + helpers; body at run) | LOW |
| 4 | siteNull / nullBySize unaffected | `nullBySize --tests *certPcSize*` and `siteNull --tests *certPcSize*` both say "No tests found"; the siteNull/withinNull/isoNullByDim/CPC members are inside the 121 identical; `test` excludes `**/SeparationNullBySizeTest*` (L89) | CONFIRMED | - |
| 5 | PCS-1 allocation and draw | independent script from the CPC labels (sha c0a20662, N 6,993, 14 groups): allocations n486 [26 32 47 17 35 40 29 17 40 56 39 21 54 33] min 17, n441 min 15, n264 min 9; site file sha 231db2e0... = the builder's | CONFIRMED | - |
| 6 | registered sizes | G12_sites.csv TOP n (14): median 486, nearest-rank p25 441 (4th of 14), min 264 | CONFIRMED | - |
| 7 | PCS-2 root-order population, PC1's groups | code L2519-L2528; ArmTest "identity by construction" (raw bits + plain null equal); runtime IDENTITY refuses unless 0.107803 / k 0 | CONFIRMED | - |
| 8 | PCS-3 seeds | plain: base 20260908, keyed by site name; deflated: 88820260908; C0: cpcSeed(20261002, name, 0); 15 distinct (ArmTest test 5); IDENTITY seeded by n00000001 (= PC1's) | CONFIRMED | - |
| 9 | C0 per subsample | 300 Fisher-Yates size-matched relabellings (cpcRelabelNull, unchanged); comparable iff C0 p95 < null p95 (L489; M7 kills `>`) | CONFIRMED | - |
| 10 | DEGENERATE / INFEASIBLE | reached = #(sepKway > 0) < 20, siteNull's own floor (L1918-L1927); n < 110; R7 (`>= 0`) KILLED | CONFIRMED | - |
| 11 | PCS-5 gate first; Q-2 degenerate counts toward it | size_verdict L363-L372 = the registrar's bracket at L23736 word for word; M5, M6, M38 KILLED | CONFIRMED | - |
| 12 | PCS-6 / PCS-7 | P1 / P2 NOT SCORED when NOT EVALUABLE (M15, M16); n 264 never decides (M13) | CONFIRMED | - |
| 13 | Support (d)-(e) | sqrt(0.05 x 0.95 / 300) = 0.012583 -> 0.0126; MDE80 0.03523 -> 0.0352; DEFF 1.0, source: independent seeded replicates (CPC Support), no item resampling | CONFIRMED | - |
| 14 | Support (e) operating points | binomial(300): P(k <= 14) 0.9999 at p 0.015 -> P(>= 4 of 5) 1.0000; at 0.085 P(k <= 14) 0.0075 -> P(<= 1 of 5) 0.9994; at 0.05, 0.145 / 0.237 | CONFIRMED | - |
| 15 | selftest 11/11; mutants 42/42 (M0 survived) | re-run: 11/11; 42 of 42, M0 SURVIVED | CONFIRMED | - |
| 16 | full suite 531 / 2 allowed | `gradlew test --offline`: 531 tests, 2 failed = MrlRoutingTest.testMrlConfigDefaults, TraceEnvelopeUnwrapTest (the two known); 104 XML files | CONFIRMED | - |
| 17 | the readout refuses any site file other than the registered draw | R1: analyze() on a fixture drawn with seeds 6-10 COMPLETED (CERTIFIED-AT-SIZE). It checks the arm-read sha against the file on disk, never the draw | REFUTED | MEDIUM |
| 18 | wall bound "under about 24 min" | CPC end-to-end was 33m55s (ops log 1597e801: 10:32:28 -> 11:06:24); the 24.2 min is an in-arm partial | PARTLY | LOW |

## Own mutants (deciding paths; scratch copies in tools/analysis, removed; worktree status 0 after)

R1 site file drawn with unregistered seeds -> analyze completes: SURVIVED (decisive; D-1) | R2 C0 compared with the deflated p95:
KILLED | R5 IDENTITY tolerance to 4 dp: KILLED | R6 P1 Brier one-term: KILLED | R7 reached counts zeros: KILLED.

## Defects

- **D-1 (MEDIUM)**: the readout does not bind the site file to the registered draw (R1). Fix: add the constant
  `SITES_SHA256 = "231db2e0e11974b28f19244753a1c0a1a5b5c4f96ff695fead2599fe78cfe737"` and refuse in analyze() when s_sha differs.
  The alternative fix is to rebuild build_site_bytes() from the pinned labels and compare. Until then, C-2 covers it.
- **D-2 (LOW)**: IDENTITY's null p95 / max are only printed beside PC1's (0.041626 / 0.042414), although they use the same seeds,
  so equality is a free identity. Fix: refuse on DIFFERENT. Otherwise C-3.
- **D-3 (LOW)**: the wall bound understates the run (claim 18). Budget the window at about 35-40 min (the registration's estimate).
- **D-4 (LOW)**: `python -O ... --selftest` also prints 11/11, because the asserts are stripped. Under -O, --analyze's selftest gate is
  therefore vacuous. Never run with -O (operator), or turn the asserts into raises.
- **D-5 (LOW, disclosure)**: the same-seed draws are not independent across sizes. PS_n441_d{1..5} share 233/207/251/260/224 of their
  441 items with PS_n486_d{same}, where chance predicts about 31. PS2 is therefore not an independent replicate of PS1. Print this in
  the outcome / record.

## Conditions

- **C-1 (operator)**: launch only from a checkout whose blobs equal the pins above, cert_positive_control.py = e0751d7c included
  (`git hash-object` of the 5 files). If main's merge tip is used rather than 88bbf560, re-count the overlap between rp12-r2-run's
  untracked files and the tip's tree. It must be 0: at 88bbf560 `comm -12` over the full `--untracked-files=all` list (31) gives 0.
- **C-2 (operator + post-run)**: `--prepare` must print site sha256 231db2e0e119...; the outcome's "site file sha256" must equal it.
- **C-3 (post-run)**: print IDENTITY plain p95 / max beside PC1's 0.041626 / 0.042414 (expected equal: same seeds), and D-5's overlap.
- **C-4 (post-run)**: re-derive every subsample's k_d, C0 p95 and reached count from replicates.csv. Print n_eff (300 per subsample),
  the MDE beside the deciding counts, and Q-1's full counts (certified / not / C0 / degenerate).

## Launch sequence (run-operator; data root = checkout = Z:\FAC\TUBerlin\THESIS\TaxoArena\.claude\worktrees\rp12-r2-run)

1. Machine free: no java, no construction, no other site null, no pool reader. Back up as usual. rp12-r2-run is at 416ac436 with
   31 untracked files and no modified ones.
2. `git -C .claude/worktrees/rp12-r2-run checkout --detach <merge tip carrying the pins, or 88bbf560>` (C-1). No git write under src/ after this.
3. Sidecars: every -wal 0 bytes (now: embeddings_cache, multicorpus_cache_v1, snapshots = 0). Remove a -shm only on a FREE exclusive-open probe.
4. Make sure TAXOARENA_DATA_ROOT is UNSET in the shell. Then `python tools/analysis/cert_pc_size.py --selftest` (11/11) and `--mutants` (42/42, M0 survived). No -O (D-4).
5. Run the union pool check ONLY under the variable, scoped to that one command (rp12-r2-run has no data_v2/; CPC ops c7cf3116 / d7f34193):
   `TAXOARENA_DATA_ROOT='Z:\FAC\TUBerlin\THESIS\TaxoArena' python tools/analysis/v2_union_pool.py --dry-run` -> rc 0, pool file sha256-lf16 79d48f4b36434a55.
   Then confirm the variable is unset (`echo ${TAXOARENA_DATA_ROOT-unset}`). cert_pc_size.py defaults --data-root to that variable,
   so a leftover value would point the snapshot and embedding reads at main.
6. `python tools/analysis/cert_pc_size.py --dry-run --data-root Z:\FAC\TUBerlin\THESIS\TaxoArena\.claude\worktrees\rp12-r2-run`.
   Expect: snapshot 20261001_094311_Headless_Run_Auto_ge, root n00000001 n 6993, allocations min 17/15/9, site sha 231db2e0..., heap fits 6g,
   pool sha = the stamp's, and "LAUNCH FROM" this checkout with no preview warning.
7. `--prepare --data-root <same>` (prints 231db2e0..., C-2), then `--hashes before --data-root <same>`.
8. The rule-7 window opens (W1-W5: exclusive-open probe FREE, admitted PIDs printed (idle Ollama as in CPC), >= 12 GB free RAM,
   no git write under src/).
9. From PowerShell in rp12-r2-run, run the printed COMMAND:
   `.\gradlew.bat certPcSize --console=plain --offline --no-daemon -PjvmThreads=12 -PnullReps=300 "-DsnapshotId=20261001_094311_Headless_Run_Auto_ge" "-DsliceDim=512" "-DsepBar=0.0145" "-DdropTop=0" "-Dwhiten=false" "-DsiteLabels=experiment_results/cert_pc_size/site_labels.tsv" "-DoutDir=experiment_results/cert_pc_size/arm"`
   About 35-40 min (D-3). The IDENTITY line must read declared 0.107803 k 0 before any subsample runs.
10. `.\gradlew.bat --stop` from PowerShell in the same directory (in CPC, cmd lost the cwd). Then `--hashes after --data-root <same>`. The window closes.
11. `python tools/analysis/cert_pc_size.py --analyze`, run from rp12-r2-run (it reads experiment_results/cert_pc_size/ relative to the
    script and does not read --data-root). It runs the selftest first and writes outcome.txt and pcs_sites.csv write-once.
    Outputs are never committed: sha256-pin them and back them up to E:/TaxoArena_backup_<date>_cert_pc_size with SHA256SUMS.txt.

## Commands (compact)

```
git hash-object <4 files> ; git rev-parse 88bbf560:<f> ; git hash-object --no-filters <f> ; git cat-file -p 88bbf560:<f> | grep -c $'\r'
git diff 88bbf560~1 88bbf560 --numstat ; ... -- SeparationNullBySizeTest.kt build.gradle.kts | grep -c '^-[^-]'      # 0
python scratchpad/rv_pcs.py      # labels sha, allocations, site sha 231db2e0..., G12 TOP median 486 / p25 441, PS2-in-PS1 overlaps
gradlew compileTestKotlin (branch, --rerun-tasks) ; base SNBST.kt (50c4b0ef) + CertPcSizeArmTest moved out -> compile ; restore ; compile
python scratchpad/rv_javap2.py base vs branch / branch2   # 38 identical, 8 javap-identical, main 121/121 + 14 new
gradlew test --tests taxonomy.CertPcSizeArmTest --tests taxonomy.CertPositiveControlArmTest   # 5/5, 7/7
gradlew certPcSize   # [PCS] REFUSING: -DsnapshotId is required ; gradlew nullBySize|siteNull --tests '*certPcSize*'  # No tests found
gradlew test --offline --continue   # 531, 2 failed (the known two) ; gradlew --stop  # 1 Daemon stopped
python tools/analysis/cert_pc_size.py --selftest (11/11) ; -O --selftest (11/11, vacuous) ; --mutants (42/42, M0 survived)
python scratchpad/rv_mut.py (R2 R5 R6 R7 KILLED) ; python scratchpad/rv_r1.py (R1: ANALYZE COMPLETED on seeds 6-10)
python -c binomial(300) operating points ; cert_pc_size.py --dry-run --data-root <rp12-r2-run> (TAXOARENA_DATA_ROOT unset)
comm -12 <(rp12-r2-run untracked, 31) <(git ls-tree -r --name-only 88bbf560) | wc -l   # 0
```
