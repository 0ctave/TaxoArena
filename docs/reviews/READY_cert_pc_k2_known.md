# READY review: CERT-PC-K2-KNOWN (branch cert-pc-k2-known, tip 14ae100a)

Reviewer: adversarial-reviewer, 2026-10-03. Registration: prog L24036-L24052 (56093589). Registrar's pre-data brackets: 65e5c0d7
(Q-KK1 L24046 / L24048 / L24050, Q-KK2 L24044, stage-0 disclosure L24049; record L24087-L24091). Precedents: READY_cert_pc_k2.md and
POSTRUN_cert_pc_k2.md. Zero calls. My only DB read was rp12-r2-run/embeddings_cache.db, opened `mode=ro&immutable=1` (-wal 0 bytes; mtime 2026-10-01
10:28 unchanged). Its per-table hashes after my reads == CERT-PC-K2's emb_hashes_after.json (`RO.table_shas`). The worktree status was 0 lines
before and after. Gradle was run by me: no foreign java ran (`Get-Process java` count 0), and `.\gradlew.bat --stop` afterwards stopped 1 daemon.

## Verdict

**NOT READY at 14ae100a: one BLOCKER, D-1.** The readout does not apply the registrar's Q-KK1 ruling. `Q_KK1_RULING = None` (L178), so whenever
reading A (STRONG + MID, the ruling) and reading B (EDGE in when gated) differ, KK1 prints WITHHELD. In that case F-KK reads "NOT FIRED" and P3 is not scored,
and outcome.txt is write-once. The case is realistic: EDGE's statistic, 0.068-0.072 at n 486, sits at the size where the null p95 is expected to be
(P4 band 0.045-0.075). EDGE would probably pass G-KS at full size and then fail at n 486, which gives A K2-SENSITIVE, B K2-SIZE-LIMIT, KK1 WITHHELD.
Everything else on the deciding paths reproduces: stage 0, the selection, the site file, the stage-0 file, G-KS, the subsampling, the inertness
(155/155) and the execution proof. **It becomes READY after C-1 passes a delta review** (constant + 2 selftest cases + mutant table; re-pin).

## Pins (blob = `git rev-parse 14ae100a:<f>` = `git hash-object <f>`, the LF rendering)

| file | blob (LF) | sha256-lf16 | working-tree CRLF rendering |
|---|---|---|---|
| tools/analysis/cert_pc_k2_known.py | 1383acfb4507 | 6184c9408e99f2ce | same (0 CRLF) |
| src/test/kotlin/taxonomy/SeparationNullBySizeTest.kt | 3401d4d73084 | 8c3984c4173a93b6 | 595847477f87 (3,230 CRLF) |
| src/test/kotlin/taxonomy/CertKnownPairArmTest.kt | a7f1078bdda9 | a87daaf2238a93f7 | same |
| build.gradle.kts | 07451aa19ba2 | 973d17f480ba1e27 | same |
| tools/analysis/cert_pc_k2.py (imported, blob-pinned in code) | 38fb0dfcde9b | 102e7ea58fa90e17 | ec1a3deaea36 (1,271 CRLF) |
| tools/analysis/cert_pc_size.py (imported via K2) | de39c6488e0d | 2c1d05b62ccd7ad5 | 73287862718b |

Input pins (reproduced by my independent rebuild and by the builder's dry-run): STAGE0_SHA256 0c32bb81...be755aa (49 rows); SITES_SHA256
8e122edd42a044ad04d79bc2519ef78305bd976632473d98500b9021a4aa3b77 (34 sites, 24,592 rows); CPC labels c0a20662....

## Per-claim table (deciding claims)

| # | claim | my number / evidence | status | sev |
|---|---|---|---|---|
| 1 | additions only, 4 paths | numstat 7a1a8655..14ae100a: 30/0, 162/0, 207/0, 1825/0; no application.yml / .env / .gitignore | CONFIRMED | - |
| 2 | population = registered class counts (6,988; twin dropped) | own script from the label file: 6,993 ids, 6,989 with src, minus q_dd452b7d = 6,988; all 14 counts equal REG_COUNTS | CONFIRMED | - |
| 3 | TRAIN only | the 6,993 ids are the B0 root region (PCS.assemble checks labels = root; READY_cert_pc_size / _k2 CONFIRMED). Stage 0, the draw and the routine check read only these ids and CERT-PC-K2's TRAIN site file. No GATE / EVAL id is read | CONFIRMED | - |
| 4 | 49 eligible pairs (combined >= 972, each >= 100) | own enumeration: 49 | CONFIRMED | - |
| 5 | STRONG chemistry+law 0.119598 (margin 0.0141); MID engineering+law 0.105456 (0.0113); EDGE economics+physics 0.070390 (8.95e-05) | own numpy (own formula, own SQL join, immutable): identical to 6 dp, margins identical; runner-up for EDGE history+math 0.069520. Python vs Kotlin agree to 1e-15, so the 8.95e-05 margin is decided | CONFIRMED | - |
| 6 | routine check | dry-run: IDENTITY \|diff\| 3.33e-16; 30 K2 sites max 9.99e-16 (tolerance 1e-9); mine: IDENTITY 0.10780301021353633 | CONFIRMED | - |
| 7 | site file = SITES_SHA256 | own rebuild (own allocate / draw, random.Random(d), categories sorted, IDENTITY = sorted root ids): sha 8e122edd...4aa3b77, 24,592 rows | CONFIRMED | - |
| 8 | stage-0 file = STAGE0_SHA256 | builder's dry-run "= the pin". My own floats give e9358d2d... because `%r` differs in the last bit (expected; my statistics agree to 1e-15). --analyze re-derives the rule from the file (M44 / M45 / M46 KILLED) | CONFIRMED (pin via dry-run) | LOW |
| 9 | n 486 / 441 subsampling | allocations chem 262 / law 224, 238 / 203; eng 243 / 243, 221 / 220; econ 191 / phys 295, 173 / 268 (own). Subsample statistics at n 486: STRONG 0.119-0.124, MID 0.103-0.109, EDGE 0.069-0.072. Pairwise overlap at n 486 177-200 / 192-220 / 154-196 of 486 (about chance) | CONFIRMED | - |
| 10 | G-KS = registration + Q-KK2 | gks(): status CERTIFIED (subsample_status: n >= 110, reached >= 20, C0 p95 < null p95, (k+1)/301 <= 1/20, i.e. k <= 14) AND margin > sample SD; population SD printed beside with a WOULD-CHANGE flag. M2, M4-M9 KILLED; my R3 KILLED. Descriptive: sample SD at n 486 0.0020 / 0.0024 / 0.0014 | CONFIRMED | - |
| 11 | KK1 counts only STRONG and MID (Q-KK1 ruling, 65e5c0d7 L24046) | reading A implements the ruling exactly (NO-CONTROL iff STRONG or MID is NOT-A-CONTROL = `len < 2` over the 2). But the DECIDING word uses Q_KK1_RULING = None: WITHHELD when A != B, and then F-KK reads NOT FIRED and P3 is NOT SCORED. My R1 (set "EDGE-DESCRIPTIVE") fails 2 of 14 selftest cases, both of which assert the unruled behaviour | REFUTED (as wired) | BLOCKER (D-1) |
| 12 | 155 pre-existing members identical, vs main | javap -p -c (#N normalised): base = gemma-own-bar classes (SNBST blob 0833e99c = main's; src/ of d9f43d19 = main's, `git diff --stat` empty; compiled 19:08:15 > source 19:01:38); branch compiled 20:07:32 > source 20:07:08. 155/155 identical, 14 new (kkpSiteError, certKnownPair + 12 locals / lambdas). Other 49 class files: 40 byte-identical, 9 javap-identical, 0 different | CONFIRMED | - |
| 13 | merges cleanly with main (GEMMA-OWN-BAR, CERT-PC-K2) | `git diff 7a1a8655 main -- build.gradle.kts src/ cert_pc_k2.py cert_pc_size.py` empty; `git merge-tree --write-tree main(61c5a7c2) cert-pc-k2-known` rc 0, tree 02e8f813 | CONFIRMED | - |
| 14 | the new code executed | my `gradlew cleanTest test --offline`: 553 tests, 2 failed = MrlRoutingTest, TraceEnvelopeUnwrapTest (the known two). CertKnownPairArmTest tests=3 failures=0 (18:30:05Z). My `gradlew certKnownPair`: one testcase, `certKnownPair - ...`, printing "[PKK] REFUSING: -DsnapshotId is required", so the task selects exactly the new method. javap names certKnownPair 39x and kkpSiteError 3x | CONFIRMED | - |
| 15 | other tasks unaffected | nullBySize excludes `*certKnownPair*`; `test` excludes SNBST; "certKnownPair" contains none of siteNull / withinNull / isoNullByDim / certPositiveControl / certPcSize / certPcK2 / gemmaOwnBar | CONFIRMED | - |
| 16 | Support (b)-(f) | sqrt(0.05 x 0.95 / 300) = 0.012583, so 0.0126; 2.8 x SE = 0.035233, so 0.0352; 1/301 = 0.0033 is 0.0467 below the bar (> MDE). DEFF 1.0, source: a permutation-null count from independently seeded replicates, no item resampling (as CERT-PC-K2 POSTRUN C-4). SCOREABLE for STRONG / MID, EDGE DESCRIPTIVE-ONLY = the Q-KK1 ruling | CONFIRMED | - |
| 17 | selftest 14/14; -O refused | re-run 14/14; `python -O` REFUSED | CONFIRMED | - |
| 18 | mutants 78/78, M0 survived | re-run: 78 of 78 KILLED, M0 SURVIVED | CONFIRMED | - |
| 19 | no write to a DB of record; dry-run writes nothing | cache mtime / -wal / per-table hashes unchanged; worktree status 0 after dry-run, selftest and mutants | CONFIRMED | - |

## Own mutants (temporary edits of cert_pc_k2_known.py, restored; blob 1383acfb after)

R1 Q_KK1_RULING = "EDGE-DESCRIPTIVE" (fix check): selftest 12/14, so the fix also needs test edits (D-1) | R2 `reached` counts x >= 0.0
(the degenerate gate becomes vacuous): KILLED (10/14), decisive | R3 the G-KS SD also takes in the full site's statistic: KILLED (7/14), decisive.

## Defects

- **D-1 (BLOCKER).** The readout ignores the Q-KK1 ruling (65e5c0d7). Fix: set `Q_KK1_RULING = "EDGE-DESCRIPTIVE"` (L178). In the two selftest
  cases that now fail ("G-KS ... NO-CONTROL" and "Q-KK1: readings A / B, WITHHELD, both rulings, EDGE not gated"), pass `ruling=None`
  explicitly where WITHHELD is meant, and add one case on the default that asserts the ruled word (A K2-SENSITIVE with EDGE NOT-CERTIFIED gives KK1
  K2-SENSITIVE, F-KK NOT FIRED, P3 scored; MID NOT-A-CONTROL with EDGE gated gives NO-CONTROL). Add a mutant "default ruling None" that must be KILLED. Update
  the docstring's KK1 line (L21-L22) and KK-7 to "ruled 65e5c0d7: STRONG and MID only".
- **D-2 (MEDIUM, wording, post-run).** STRONG and MID share law (224 / 243 law items at n 486), so KK1's two deciding pairs are not independent.
  A K2-SENSITIVE reading rests on about 1.5 independent categories' worth of structure, not 2. The readout prints the shared category; the record must word it.
- **D-3 (LOW).** The stage-0 pin is shown only through the builder's routine (`%r` floats). An independent recompute matches each statistic to 1e-15,
  not the bytes. That is acceptable: --analyze re-derives the selection from the file and KK-0 (iii) ties each full-site statistic to the arm within 1e-9.

## Conditions

- **C-1 (builder, then a delta review, before launch).** D-1 on the branch, a new tip, new pins for cert_pc_k2_known.py. Delta review = the diff, the selftest,
  the mutants, my R1 (it must then pass) and the new mutant.
- **C-2 (operator).** Launch only from a checkout whose blobs equal the C-1 pins (`git hash-object`), with SNBST 3401d4d7, the arm test a7f1078b and gradle 07451aa1
  unchanged. rp12-r2-run is now at 85fc338a with 47 untracked paths, 0 of them in 14ae100a's tree (`comm -12`). Re-count against the C-1 tip. `src/main` is identical between
  85fc338a and 14ae100a.
- **C-3 (operator).** --dry-run / --prepare print the selection = SELECTION, stage-0 0c32bb81..., site 8e122edd..., the routine check <= 1e-9, and the pool file
  sha256-lf 79d48f4b36434a55 "= the stamp's".
- **C-4 (post-run).** Re-derive k_d, null p95, C0 p95 and reached from replicates.csv for all 34 sites. Print the G-KS margin against the sample SD and the population SD, and n_eff 300 /
  SE 0.0126 / MDE80 0.0352 beside KK1. Give full counts per pair and size (certified / not / C0 / degenerate), with EDGE marked descriptive.
- **C-5 (post-run wording).** D-2, and the stage-0 disclosure (L24049): P1's STRONG part FAILED pre-arm, and the selection is mechanical, so there is no freedom.

## Launch sequence (run-operator; data root = checkout = Z:\FAC\TUBerlin\THESIS\TaxoArena\.claude\worktrees\rp12-r2-run; after C-1)

1. Machine free: no java (heavy_check refuses), no construction, no site null, no pool reader. Back up as usual.
2. `git -C .claude/worktrees/rp12-r2-run checkout --detach <C-1 tip or its main merge tip>` (C-2). No git write under src/ after this.
3. Sidecars: embeddings_cache.db-wal 0 bytes. Remove a -shm only on a FREE exclusive-open probe.
4. TAXOARENA_DATA_ROOT unset. `python tools/analysis/cert_pc_k2_known.py --selftest` (all pass) and `--mutants` (all KILLED, M0 SURVIVED). Never use -O.
5. `TAXOARENA_DATA_ROOT='Z:\FAC\TUBerlin\THESIS\TaxoArena' python tools/analysis/v2_union_pool.py --dry-run` -> rc 0, pool file sha256-lf16
   79d48f4b36434a55; then `echo ${TAXOARENA_DATA_ROOT-unset}` prints unset.
6. `python tools/analysis/cert_pc_k2_known.py --dry-run --data-root Z:\FAC\TUBerlin\THESIS\TaxoArena\.claude\worktrees\rp12-r2-run`. Expect: routine
   check IDENTITY ~3e-16, 30 K2 sites ~1e-15; populations = registered; 49 eligible; the selection of claim 5 "(= the pin)"; stage-0 and site sha
   "(= the pin)"; heap fits 6g; pool "= the stamp's"; "LAUNCH FROM" with no preview warning.
7. `--prepare --data-root <same>` (writes stage0.tsv + site_labels.tsv, mode x), then `--hashes before --data-root <same>`.
8. The rule-7 window opens (W1-W5: probe FREE, admitted PIDs printed, >= 12 GB free RAM, no git write under src/).
9. From PowerShell in rp12-r2-run, run the printed COMMAND:
   `.\gradlew.bat certKnownPair --console=plain --offline --no-daemon -PjvmThreads=12 -PnullReps=300 "-DsnapshotId=20261001_094311_Headless_Run_Auto_ge" "-DsliceDim=512" "-DsepBar=0.0145" "-DdropTop=0" "-Dwhiten=false" "-DsiteLabels=experiment_results/cert_pc_k2_known/site_labels.tsv" "-DoutDir=experiment_results/cert_pc_k2_known/arm"`
   About 25 min estimated; budget the window at 40-70 min. The IDENTITY line must read declared 0.107803 k 0 before any KK site runs.
10. `.\gradlew.bat --stop` from PowerShell in the same directory; then `--hashes after --data-root <same>`. The window closes.
11. `python tools/analysis/cert_pc_k2_known.py --analyze` from rp12-r2-run (selftest first; outcome.txt and kk_sites.csv are write-once). The header must read
    "ruling: EDGE-DESCRIPTIVE". Outputs are never committed: sha256-pin them and back them up to E:/TaxoArena_backup_<date>_cert_pc_k2_known with SHA256SUMS.txt
    (emb_hashes_before/after.json included).

## Commands (compact)

```
git diff --numstat 7a1a8655 14ae100a; git rev-parse 14ae100a:<f>; git hash-object [--no-filters] <f>; python CRLF count
python scratchpad/rv_kk.py     # labels; populations 6,988; IDENTITY; 49 eligible; selection + margins; allocations; n486/441 stats + SDs;
                               # independent site rebuild sha 8e122edd...; stage-0 own-float sha (differs only by %r)
python tools/analysis/cert_pc_k2_known.py --dry-run --data-root <rp12-r2-run>   # rc 0; all "= the pin"; routine 3.3e-16 / 1.0e-15
python tools/analysis/cert_pc_k2_known.py --selftest (14/14); python -O ... (REFUSED); --mutants (78/78, M0 SURVIVED)
python scratchpad/ar_kk_mut.py # R1 12/14 (D-1), R2 KILLED, R3 KILLED; blob 1383acfb after
python scratchpad/ar_kk_javap.py   # gemma-own-bar (main SNBST 0833e99c) vs branch classes: 155/155 identical, 14 new; 40 + 9 identical, 0 diff
gradlew.bat cleanTest test --offline   # 553 tests, 2 known failures; CertKnownPairArmTest 3/0
gradlew.bat certKnownPair --offline    # 1 testcase certKnownPair, "[PKK] REFUSING: -DsnapshotId is required"; gradlew --stop (1 daemon)
git merge-tree --write-tree main cert-pc-k2-known   # rc 0, 02e8f813; git diff 7a1a8655 main -- build.gradle.kts src/ (empty)
RO.table_shas(rp12-r2-run cache) == cert_pc_k2/emb_hashes_after.json (True); comm -12 rp12-r2-run untracked vs 14ae100a tree (0)
```
