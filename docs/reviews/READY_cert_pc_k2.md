# READY review: CERT-PC-K2 (branch cert-pc-k2, tip 85fc338a)

Reviewer: adversarial-reviewer, 2026-10-03. Registration prog L23901-L23913 (d50c47d4). Precedent: READY_cert_pc_size.md (fc1d1fe5),
POSTRUN_cert_pc_size.md (541fde40). Zero calls. My only DB read: rp12-r2-run/embeddings_cache.db `mode=ro&immutable=1` (its -wal 0 bytes)
for the texts of the 2,088 anchor ids and the 6,993 root ids. The worktree was left clean (`git status --untracked-files=all` 0 lines).
**Gradle was NOT run by me**: foreign java ran throughout (another agent's `gradlew test` in worktrees/gemma-own-bar, PIDs 14644 / 62244 / 64112).
The bytecode check below was done on the compiled classes on disk. Suite and arm results are read from the builder's fresh XMLs (named as such).

## Verdict

**READY for the arm launch (rule-7 window)**, conditions C-1..C-5. The deciding paths reproduce. Populations, twin collapse, allocation,
draw, the site file byte-for-byte, the gate-first anchor verdict and PK1 / PK2 all match. The Support arithmetic reproduces.
The 135 pre-existing members of SeparationNullBySizeTest disassemble identically. D-1 of CERT-PC-SIZE is CLOSED: --analyze rebuilds the
file from the pinned labels and refuses on any byte difference, and it also checks the sha pin. The registration has one factual error
(D-1 here, MEDIUM): chemistry also meets the stated eligibility rule. The anchors were named pre-data, so this is a registrar bracket, not a blocker.

## Pins (blob = `git hash-object` = `git rev-parse 85fc338a:<path>`, the LF rendering; the stored blobs hold 0 CRLF)

| file | blob of record (LF) | working-tree CRLF rendering (`--no-filters`) |
|---|---|---|
| tools/analysis/cert_pc_k2.py | 38fb0dfcde9b | same (LF on disk) |
| src/test/kotlin/taxonomy/SeparationNullBySizeTest.kt | e2c65729bc8d | 7ed1e068206d (2,876 CRLF) |
| src/test/kotlin/taxonomy/CertPcK2ArmTest.kt | db452e66d993 | same |
| build.gradle.kts | 2ef48e97f88c | 6fcdba6faf33 (555 CRLF) |
| tools/analysis/cert_pc_size.py (imported, pinned in code) | de39c6488e0d | - |
| tools/analysis/cert_positive_control.py (imported via PCS) | e0751d7c6fe5 | - |

Inputs: the CPC label file is sha256 c0a20662... (6,993 ids). The K2 site file SITES_SHA256 is efcc4e99cf5eed50d04249a28e7aa896b1518f39088102e25055e6a3f65393bb
(31 sites, 20,898 rows).

## Per-claim table (deciding claims)

| # | claim | my number / evidence | status | sev |
|---|---|---|---|---|
| 1 | additions only | numstat vs 328857f6: 30/0, 109/0, 186/0, 1271/0 | CONFIRMED | - |
| 2 | populations 266/238, 489/316, 248/530 (ori/added) | own script from the label file: economics 266/238, physics 248/530; math raw 489/317 + 3 no-src, 316 after the twin collapse | CONFIRMED | - |
| 3 | PK-1 one math twin (q_dd452b7d... twin of q_92ffd944..., both scibench-stat) | split_side.stem_key over the cache texts: exactly 1 group in the 3 anchors. It is also the ONLY stem-key group among all 6,993 root ids. 6,989 ids carry src; minus the twin = 6,988 = the registration's "kept TRAIN items" | CONFIRMED | - |
| 4 | "the only categories with >= 486 TRAIN items and >= 100 in each family" (registration) | chemistry: 109 ori_mmlu / 567 added = 676, which also qualifies. biology 381, business 96 ori, engineering 42 ori and psychology 476 do not | REFUTED (registration text) | MEDIUM (D-1) |
| 5 | allocations (added/ori) | econ 230/256 (486), 208/233 (441); math 191/295, 173/268; physics 331/155, 300/141 (own largest-remainder code, ties by name) | CONFIRMED | - |
| 6 | site file byte-for-byte = SITES_SHA256 (closes CPS D-1) | own independent rebuild (own allocate/draw re-implemented, random.Random(d), families sorted, IDENTITY rows = sorted root ids): sha256 efcc4e99...65393bb, 20,898 rows, 31 sites. IDENTITY section = CPS site file (231db2e0...) line for line (6,993 = 6,993) | CONFIRMED | - |
| 7 | the readout refuses a non-registered site file | the code does the rebuild compare (L480-L483) and the pin (L477); builder M37 / M38 KILLED in my re-run, and selftest case s21 exercises the rebuild alone with the pin overridden | CONFIRMED | - |
| 8 | economics overlap disclosure | n 486 pairwise 468-470 of 486 (chance 468.6); n 441 383-390; same-seed 441-in-486 431-435. math 283-302 / 227-250 / 380-387; physics 294-310 / 239-254 / 400-408. The readout prints the DISCLOSED line for economics only (486 > 0.9 x 504) | CONFIRMED | LOW (D-3) |
| 9 | 135/135 pre-existing members javap-identical; 13 new; 0 new class files | my javap -p -c (#N normalised, constant comments kept): base = rp12-r2-run's classes compiled 2026-10-02 20:39 from the same SNBST blob 3e9dd8ad; branch = cert-pc-k2's classes compiled 17:36:12, after the source mtime 17:35:58 and unchanged since. Main class 135/135 identical, 13 new (pk2SiteError, certPcK2 + 11 locals/lambdas). Other 46 class files: 38 byte-identical, 8 javap-identical, 0 different | CONFIRMED | - |
| 10 | the new code executed | builder's XMLs, all written after the compile: CertPcK2ArmTest tests=2 failures=0 (15:36:59Z); build/test-results/certPcK2 holds one testcase `certPcK2 - declared two-family ...` with "REFUSING: -DsnapshotId is required". javap of the branch class names certPcK2 40x and pk2SiteError 2x. The body past the prologue first runs in the arm, where the IDENTITY gate and the readout's rebuild / k / C0 recounts discriminate | CONFIRMED (builder's run, not re-run) | LOW |
| 11 | other tasks unaffected | gradle diff: certPcK2 is a copy of certPcSize (3 lines differ: name, oom path, filter); nullBySize excludes `*certPcK2*`; `test` excludes SNBST (L89); none of the siteNull / withinNull / isoNullByDim / certPcSize filters matches the new method name | CONFIRMED | - |
| 12 | Kotlin arm = certPcSize's arm except the site check | body diff vs certPcSize: tag, task name, pk2SiteError in place of the PS_ checks and the 14-category check, a group_sizes column, arm= in status. cpcDeclaredSite / cpcRelabelNull / pcsC0Seed are unchanged (inside the 135). Groups are ordered added, ori_mmlu (sorted labels) = the readout's gs | CONFIRMED | - |
| 13 | gate-first anchor verdict = CPS Q-1/Q-2 | selftest `helpers` equates anchor_verdict and subsample_status with PCS's on all 4^5 patterns; M3-M6, M24-M28 KILLED | CONFIRMED | - |
| 14 | PK1 from n 486, PK2 from n 441; F-PK iff PK1 K2-NOT | L584-L612; M13, M16, my R5 KILLED | CONFIRMED | - |
| 15 | Support (d)-(e) | sqrt(0.05 x 0.95 / 300) = 0.012583 -> 0.0126; 2.80 x SE = 0.035233 -> 0.0352; DEFF 1.0, source: independently seeded replicates, no item resampling (as CPS POSTRUN C-4) | CONFIRMED | - |
| 16 | selftest 11/11; -O refused (CPS D-4) | re-run 11/11; `python -O ... --selftest` -> "REFUSED: python -O strips the selftest's asserts" | CONFIRMED | - |
| 17 | mutants 60/60, M0 survived | re-run: 60 of 60 KILLED, M0 SURVIVED (harness valid) | CONFIRMED | - |
| 18 | full suite 544 / 2 allowed | builder's XMLs (108 files, 15:36:56-15:38:51Z, after the compile): 544 tests, 2 failed = MrlRoutingTest, TraceEnvelopeUnwrapTest (the known two). Not re-run (foreign java) | CONFIRMED (builder's run) | LOW |
| 19 | IDENTITY p95/max = PC1 (CPS D-2 fixed) | L532-L535; M34 / M35 KILLED | CONFIRMED | - |

## Builder's points for the registrar

- **Q-K1 (PK-6), ruling owed pre-data.** Read literally, "K2-NOT iff 0" counts a NOT EVALUABLE anchor as not certified, so F-PK could
  fire on unevaluable anchors. That contradicts the gate-first logic (CPS Q-2). The builder prints the registered word only when it is
  invariant to the NE anchors (word(c) == word(c + e)); otherwise PK reads NOT EVALUABLE. This rule only withholds. It equals the
  literal rule when e = 0, and when e > 0 it never prints a word the literal rule would not. Cases: (c, e) = (2, 1) gives K2-CERTIFIABLE;
  (0, >=1) and (1, >=1) give NOT EVALUABLE. Recommend adoption (M11 / M12 / my R3 KILLED).
- **PK-1 (items vs ids).** Confirmed (claim 3). One math pair collapsed to the smaller id. IDENTITY keeps all 6,993 ids (= PC1 / CPS). Record it.
- **PK-7 (P2 at n 486).** The registration names no size for P2. Scoring at the deciding size is the natural reading; record it.

## Own mutants (deciding paths; temporary copies in tools/analysis, removed; worktree status 0 after)

R1 assemble's cache twin guard removed: SURVIVED (not decisive: the site file is pinned and rebuilt from TWINS; my claim 3 verifies the pin; D-2) |
R2 reached counts zeros: KILLED | R3 PK-6 returns the optimistic word: KILLED | R4 P1 Brier one term: KILLED | R5 PK1/PK2 sizes swapped: KILLED.

## Defects

- **D-1 (MEDIUM, registration text).** The eligibility sentence is false: chemistry (109 / 567) meets ">= 486 and >= 100 per family".
  Fix (registrar, pre-data): bracket L23904 by insertion: "chemistry also qualifies (109 / 567 = 676); not an anchor of this test; the three
  anchors stand as named". Adding chemistry would change PK1's denominator and its ">= 2 of 3" rule, which needs a new pre-data amendment.
  That choice belongs to the registrar or the author; it does not belong in the readout.
- **D-2 (LOW).** The selftest does not exercise assemble()'s cache twin check (R1 survives). Fix: a selftest case that calls the twin
  comparison with a stubbed cache_texts returning a second twin. The real-data check stands, verified independently here.
- **D-3 (LOW, disclosure).** Economics's 5 n-486 subsamples share 468-470 of 486 items, so its "4 of 5" is close to one draw read five
  times. math and physics share 58-64% pairwise. n 441 is not independent of n 486 (380-435 of 441 shared). The readout prints this. The record must word it.

## Conditions

- **C-1 (operator).** Launch only from a checkout whose six blobs equal the pins above (`git hash-object`). The data root is rp12-r2-run,
  now detached at 88bbf560 with 39 untracked files. They overlap 85fc338a's tree in 0 paths (`comm -12`). If a main merge tip is used instead, re-count the overlap.
- **C-2 (registrar, before launch).** Rule Q-K1, and record PK-1 and PK-7 as readings. Bracket D-1.
- **C-3 (operator).** --dry-run and --prepare must print site sha256 efcc4e99...65393bb, twins = the pin, and populations = registered.
- **C-4 (post-run).** Re-derive every K2 site's k_d, C0 p95 and reached count from replicates.csv. Print n_eff 300 and MDE80 0.0352
  beside the deciding counts, with the full anchor counts (certified / not / C0 / degenerate). Print IDENTITY = PC1 (0.041626 / 0.042414).
- **C-5 (post-run wording).** Carry D-3: economics is about 1 effective subsample, and PK2 is a partly overlapping re-read of PK1.

## Launch sequence (run-operator; data root = checkout = Z:\FAC\TUBerlin\THESIS\TaxoArena\.claude\worktrees\rp12-r2-run)

1. Machine free: no java (cert_pc_k2's heavy_check refuses otherwise), no construction, no site null, no pool reader. Back up as usual.
2. `git -C .claude/worktrees/rp12-r2-run checkout --detach 85fc338a` (or the main merge tip carrying the pins; C-1). No git write under src/ after this.
3. Sidecars: embeddings_cache.db-wal 0 bytes (now 0). Remove a -shm only on a FREE exclusive-open probe.
4. TAXOARENA_DATA_ROOT unset. `python tools/analysis/cert_pc_k2.py --selftest` (11/11) and `--mutants` (60/60, M0 survived). Never use -O.
5. `TAXOARENA_DATA_ROOT='Z:\FAC\TUBerlin\THESIS\TaxoArena' python tools/analysis/v2_union_pool.py --dry-run` -> rc 0, pool file
   sha256-lf16 79d48f4b36434a55. Then `echo ${TAXOARENA_DATA_ROOT-unset}` prints unset.
6. `python tools/analysis/cert_pc_k2.py --dry-run --data-root Z:\FAC\TUBerlin\THESIS\TaxoArena\.claude\worktrees\rp12-r2-run`. Expect:
   snapshot 20261001_094311_Headless_Run_Auto_ge, root n 6993; twins = the pin; populations 266/238, 489/316, 248/530; the allocations
   of claim 5; site sha = SITES_SHA256; heap fits 6g; pool sha = the stamp's; "LAUNCH FROM" with no preview warning.
7. `--prepare --data-root <same>` (prints efcc4e99..., C-3), then `--hashes before --data-root <same>`.
8. The rule-7 window opens (W1-W5: probe FREE, admitted PIDs printed, >= 12 GB free RAM, no git write under src/).
9. From PowerShell in rp12-r2-run, run the printed COMMAND:
   `.\gradlew.bat certPcK2 --console=plain --offline --no-daemon -PjvmThreads=12 -PnullReps=300 "-DsnapshotId=20261001_094311_Headless_Run_Auto_ge" "-DsliceDim=512" "-DsepBar=0.0145" "-DdropTop=0" "-Dwhiten=false" "-DsiteLabels=experiment_results/cert_pc_k2/site_labels.tsv" "-DoutDir=experiment_results/cert_pc_k2/arm"`
   About 31 min (2 x CPS's 926 s); budget the window at 35-40 min. The IDENTITY line must read declared 0.107803 k 0 before any K2 site runs.
10. `.\gradlew.bat --stop` from PowerShell in the same directory. Then `--hashes after --data-root <same>`. The window closes.
11. `python tools/analysis/cert_pc_k2.py --analyze` from rp12-r2-run (selftest first; outcome.txt and pk2_sites.csv are write-once). Outputs
    are never committed: sha256-pin them and back them up to E:/TaxoArena_backup_<date>_cert_pc_k2 with SHA256SUMS.txt (emb_hashes_before/after.json included).

## Commands (compact)

```
git hash-object <4 files>; git rev-parse 85fc338a:<f>; git hash-object --no-filters <f>; python CRLF count (blob 0; wt SNBST 2876, gradle 555)
git diff --numstat 328857f6 85fc338a                      # 30/0 109/0 186/0 1271/0
python scratchpad/rv_k2.py    # labels sha c0a20662; per-category family counts (chemistry 109/567); stem-key groups (anchors 1, root-wide 1);
                              # populations; allocations; independent site rebuild sha efcc4e99...; overlaps
python (IDENTITY rows of rebuilt file == rp12-r2-run cert_pc_size/site_labels.tsv 231db2e0...: 6993 == 6993 True)
python scratchpad/rv_javap.py # rp12-r2-run classes (3e9dd8ad) vs cert-pc-k2 classes: 135/135 identical, 13 new; 38 + 8 identical, 0 different
grep test-results/{test,certPcK2}/*.xml                   # ArmTest 2/0; certPcK2 REFUSING -DsnapshotId; 544 tests, 2 known failures
python tools/analysis/cert_pc_k2.py --selftest (11/11); python -O ... --selftest (REFUSED); --mutants (60/60, M0 SURVIVED)
python scratchpad/rv_mut.py   # R1 SURVIVED, R2-R5 KILLED
comm -12 <(rp12-r2-run untracked, 39) <(git ls-tree -r --name-only 85fc338a) | wc -l   # 0
powershell Get-CimInstance Win32_Process java.exe         # gemma-own-bar gradle test: Gradle not run here
```
