# READY review: CERT-POSITIVE-CONTROL (declared-site arm + cert_positive_control.py)

Reviewer: adversarial-reviewer, 2026-10-02. Branch cert-positive-control, tip b5653fb7 (worktree .claude/worktrees/cert-positive-control,
base 2daeae31; 4 files, 1,822 insertions, 0 deletions). Registration prog L23464-L23488 with the D-I1 bracket inside L23470; record
section L23616-L23620 (re-read whole). Zero calls; no site null run; no DB of record opened by the reviewer.
Pins (LF of record, `git hash-object` == `git rev-parse HEAD:<path>` for all four):
- cert_positive_control.py blob:a2b80ed206c18ccd8b669dc1ec8d170b1788037a, sha256-lf16:c4631fa19382243e (working tree LF).
- SeparationNullBySizeTest.kt blob:50c4b0ef5601ca093b873d65eaa1bdf2d040b5b4, sha256-lf16:aeae5078b711947e; working tree is the CRLF
  rendering sha256-crlf16:b8bca40c7d8b6ab4 (raw blob 50572763).
- CertPositiveControlArmTest.kt blob:fb800b4b6dfd69a6fc4399a9f3f1cb254e8c3a9b, sha256-lf16:0ea377bb91d279f1 (working tree LF).
- build.gradle.kts blob:82d0552e131ec04adb145dac2b5310b3cedf3494, sha256-lf16:b9fb7875a279f2e4; working tree CRLF sha256-crlf16:b6d3bc039939ec7a.
- Imported pins verified at HEAD: g12_site_null.py 0cf5b091, cert_resolution.py dbe9425d, mmlu_gold_geometry.py 5ab1c878;
  G12_sites.csv 21f110af (main and branch; 60 data rows).

## Verdict

**READY for the arm launch (rule-7 window)**, conditions C-3 (launch flags and checkout, below) and C-4 (post-run counts).
**--analyze waits on C-1** (gaps in the readout selftest; a selftest-only delta review). **Merge to main waits on C-2** (nullBySize
inertness). D-I1: the registrar's live-form bracket (L23470) is UPHELD, not overruled. K11 ruled EQUIVALENT at k = 2 (confirmed by
execution) and fail-closed at k >= 3. CR-1..CR-6 accepted (CR-2 as a disclosed reading). Registrar bracket owed: R-1 (sidecar wording).

## Per-claim table (deciding claims)

| # | claim | my number / evidence | status | sev |
|---|---|---|---|---|
| 1 | the live I-1 leg runs the production splitter (execution discriminator) | KR1 `val accepted = true` (splitSingleNode not called) KILLED: the "routine identity" test fails at ArmTest L75 (k = 2 expected). The clean run passes 7/7 with accepted, k = 2, routed children = the planted clusters, persisted > 0.5; dasguptaDeltaNorm is written only by TaxonomySplitter L411. The compiled class carries the new members (javap count 4); compileTestKotlin EXECUTED on every mutant leg, --no-build-cache | CONFIRMED | - |
| 2 | the routine == the splitter's statistic | declaredSiteStatistic body = TaxonomySplitter L408-L410 verbatim; dimForDepth is depth-free (EmbeddingSlice.width); the bit test is strict: KR3 (within-child summation order reversed) KILLED at L76 | CONFIRMED | - |
| 3 | K11 (children hash-set order) equivalent at k = 2 | KR2 (descending id order) SURVIVED, compileTestKotlin executed; analytic: accumulators start at 0.0 and two-term IEEE sums commute. At k >= 3 the sort is load-bearing: ids "n%08d" from one AtomicLong, children created sequentially in routedClusters order (Splitter L472-L478), live leg single-threaded, so (length, id) restores the order. A wrong order can only flip last bits -> refusal, never a false PASS | CONFIRMED (EQUIVALENT k = 2; fail-closed k >= 3) | - |
| 4 | K10 (live recomputed := persisted) "equivalent" | NOT equivalent: it makes the ARM's live gate vacuous. It survives because the unit test applies the routine to r.groups itself (L78), which guards the routine, not the arm's gate | REFUTED (wording) | LOW (D-5) |
| 5 | siteNull task byte-identical | build.gradle.kts numstat 30 / 0, one hunk @@ -290,6 +290,36 @@ after the siteNull block; its filter "*SeparationNullBySizeTest*siteNull*" does not match the new method ("site nulls", with a space; case-sensitive). Kotlin 443 / 0, hunks only at the import (L15) and after the last member (L2035) | CONFIRMED | - |
| 6 | "flag absent: every existing path inert" | REFUTED for `nullBySize`: its filter "*SeparationNullBySizeTest*" includes the new method, which refuses (error) where the existing methods skip by Assumption. Executed: `gradlew nullBySize --tests *certPositiveControl*` -> 1 test, FAILED "[CPC] REFUSING: -DsnapshotId is required" | REFUTED | MEDIUM (C-2) |
| 7 | C0 failing takes precedence | analyze: `if not comparable -> NOT EVALUABLE` before the p_d branch; "reaches" = `>=`; selftest k_d = 0 with C0 p95 == null p95 -> NOT EVALUABLE; builder's M4, M5 KILLED (re-run) | CONFIRMED | - |
| 8 | Support: DEFF 1.0 (by construction: independent seeded replicates; source G12 Support), n_eff 300, SE 0.0126, MDE80 0.0352, SCOREABLE | recomputed SE 0.012583, MDE80 0.035233, certify side 0.01477; 0.60 - 0.05 = 0.55 > 0.0352; CERTIFIED reachable (k_d <= 14, floor 1/301) | CONFIRMED (non-vacuous) | - |
| 9 | selftest 19/19, mutants 26/26 | re-run: 19/19; 26/26 KILLED, M0 survived. `python -O --selftest`: 18/19 (in the main --analyze case `assert main([...]) == 0` is stripped, so main never runs). Fail-closed: --analyze under -O refuses on the red selftest; production asserts before L794: 0 | PARTLY | LOW (D-3) |
| 10 | the readout's I-1 live gate is tested | own mutants: R1 (live rows == 60 dropped), R2 (>= 1 accepted -> >= 0), R9 (live mismatch ignored) all SURVIVED; R3 (I-2 reads the G12-k column) and R7 (live without bracket) KILLED; R4, R8 (Kotlin recount cross-checks off) SURVIVED; R5 (p_d <= -> <) SURVIVED = equivalent (k+1 = 15.05 impossible); R6 (null p95 on the unsorted list) SURVIVED (fixture replicates are sorted) | PARTLY | MEDIUM (C-1) |
| 11 | heap fits 6g | Kotlin guard 12 x 6,993 x (5.5 x 512 + 384) x 8 = 2.15 GB vs 0.90 x 6 GiB = 5.80 GB; Python rule 2.48 GiB (7 x D model) | CONFIRMED | - |
| 12 | data object | member root region = label set (refuses otherwise), 14 categories, TRAIN-only + gtc cross-check (M19/M20 KILLED); G12_sites.csv blob 21f110af, 60 rows; siteNull's site filter, splitter (canonicalConfig(55), NoLlm), seeds 20260908 / 88820260908 and generator reused verbatim (cpcSeed/cpcSiteArm vs runArm L1845-L1858) | CONFIRMED | - |
| 13 | SEEN root statistic 0.1078 | not recomputed (a pre-run disclosure, not deciding; recomputing needs a full snapshot parse in the data root) | UNDETERMINED (descriptive) | - |

CR rulings. CR-1 CONFIRMED (corpus domain via query_id; the gtc cross-check and the TRAIN side both refuse). CR-2 ACCEPTED as a
reading (no-src items pooled; the 55 threshold counted WITHIN the anchor, the only reading under which the children are the
anchor's; PC3 is DESCRIPTIVE-ONLY, so no criterion moves). CR-3 CONFIRMED (row 7). CR-4 CONFIRMED (the 3-way Brier uses the
registered 0.85 / 0.12 / 0.03; the P1 interval is unscored when NOT EVALUABLE, M18 KILLED). CR-5 CONFIRMED (the three registered
sites decide and refuse on a mismatch; R3 KILLED). CR-6 CONFIRMED (C0 seed 20261002 fixed in code before any null ran).
D-I1. Upheld: the registered form cannot pass (the snapshot keeps the final, re-routed regions). The live form tests the same claim
on the same code path, bit for bit (rows 1-3). It does not show that G12's persisted values came from this code; I-2 (exact k on
three TOP sites) is the bridge to G12 and stays a refuse-gate.

## Defects and fixes

- **C-1 (MEDIUM; before --analyze; selftest-only delta review)**: add selftest refusal cases for the live leg (59 I1_LIVE rows;
  0 accepted; one "false" row) and a fixture whose SN replicates are not in sorted rep order; R1, R2, R9 and R6 must then be KILLED.
  Fix D-3 in the same edit: `rc = main(["--analyze"]); if rc != 0: raise AssertionError(rc)`; re-run under `python -O`.
- **C-2 (MEDIUM; before merging to main; does not touch the run)**: make the new @Test skip outside its own task. The
  certPositiveControl task sets `systemProperty("cpcArm", "1")`; the method starts with
  `Assumptions.assumeTrue(System.getProperty("cpcArm") == "1")`; inside the task a missing input still REFUSES. Re-show
  `gradlew nullBySize --tests *certPositiveControl*` -> SKIPPED, with the siteNull block unchanged.
- **C-3 (operator; launch)**: the printed COMMAND does not carry the I-1 flags. Append
  `"-Di1Form=live" "-Di1Bracket=docs/judge_v2_program.md L23470"` (without them the arm refuses at I-1 by design).
  rp12-r2-run is detached at 2703f2c2 (an ancestor of b5653fb7) and lacks G12_sites.csv. 604 of its 626 untracked files are tracked
  at b5653fb7, all 604 hash-identical, so `git checkout` refuses until exactly those 604 paths are removed (the checkout rewrites
  them identically). Do this BEFORE the window opens (it is a git write under src/).
- **C-4 (post-run review)**: print the I-1 live accepted count out of 60, and the number of accepted sites with k >= 3 that match
  bit for bit (the execution test of the K11 sort). Print the root's plain-null p50 / p95 beside the root row of G12's
  site_null_B0_mmlu_pro_lb.csv (same seeds: a free identity).
- **D-5 (LOW)**: K10. Recompute the live statistic in the arm loop (`declaredSiteStatistic(r.groups, dim)`), not only inside
  cpcLiveIdentity, so the run's gate is not the helper's own comparison. Optional; does not block.
- **R-1 (registrar, LOW)**: the record says "EMPTY -wal/-shm". On disk the four -wal files are 0 bytes and the four -shm files are
  32,768 bytes each (snapshots, embeddings_cache, multicorpus_cache_v1, mmlu_pro_dataset_cache_v2; dated 2026-10-02 08:14). The
  operator's rule should read: any -wal > 0 bytes = failed precondition; a -shm (a 32 KiB index) is removed only when the
  exclusive-open probe reads FREE.

## Launch sequence (run-operator; from the data-root checkout .claude/worktrees/rp12-r2-run)

1. Machine free: no java, no construction, no other site null, no pool reader (GOLD-LEVEL-EMB finished). Back up as usual.
2. Bring rp12-r2-run to b5653fb7 (C-3: remove the 604 identical untracked paths; `git checkout --detach b5653fb7`; `git status`
   shows 22 untracked; `git hash-object` of the four pinned files = the pins above). No git write under src/ after this step.
3. Sidecars: quote their sizes; every -wal must be 0 bytes; remove a -shm only on a FREE exclusive-open probe (R-1).
4. `python tools/analysis/cert_positive_control.py --selftest` (19/19) and `--mutants` (26/26).
5. `python tools/analysis/v2_union_pool.py --dry-run` (rc 0; pool file sha256-lf16 79d48f4b36434a55); it must have exited.
6. `python tools/analysis/cert_positive_control.py --dry-run`. Expect n 6,993, 14 categories, PC3 14/14, I-1 preview 6/60,
   I-2 chemistry k 300 / math k 292 / history k 97, heap fits 6g, pool sha = the stamp's, LAUNCH FROM = this checkout.
7. `--prepare`, then `--hashes before`.
8. Rule-7 window opens (W1-W5: exclusive-open probe FREE, admitted PIDs printed, >= 12 GB free RAM, no git write under src/).
9. The printed COMMAND (`.\gradlew.bat certPositiveControl --console=plain --offline --no-daemon -PjvmThreads=12 -PnullReps=300 ...`)
   with `"-Di1Form=live" "-Di1Bracket=docs/judge_v2_program.md L23470"` appended. About 130 min (n^2-scaled from G12; unsourced).
10. `.\gradlew.bat --stop`; `--hashes after`; the window closes.
11. `--analyze` only after C-1's delta review. It refuses on a REFUSED or partial arm, a hash change, a label sha mismatch, a
    different instrument, or an identity failure.

## Commands (compact)

```
git -C <cpc> diff 2daeae31 HEAD --numstat; git diff 2daeae31 HEAD -- build.gradle.kts | grep '^@@'      # 30/0, one hunk
git hash-object <4 files> == git rev-parse HEAD:<file>; sha256sum (CRLF) vs git cat-file -p HEAD:<f> | sha256sum (LF)
python tools/analysis/cert_positive_control.py --selftest   # 19/19 ; python -O ... --selftest  # 18/19
python tools/analysis/cert_positive_control.py --mutants    # 26/26, M0 survived
python scratchpad/rv_mut.py, rv_mut2.py                     # R0..R9 (table rows 9-10)
.\gradlew.bat test --offline --no-build-cache --tests taxonomy.CertPositiveControlArmTest   # 7/7 clean (before and after mutants)
  KR1 accepted:=true KILLED (L75) | KR2 descending child order SURVIVED (k = 2) | KR3 reversed within-child order KILLED (L76)
  each leg: compileTestKotlin executed; source restored, cmp equal, blob 50c4b0ef re-hashed
.\gradlew.bat nullBySize --offline --tests *certPositiveControl*   # 1 test FAILED "[CPC] REFUSING: -DsnapshotId is required"
.\gradlew.bat --stop                                                # "1 Daemon stopped"; no java left
rp12-r2-run: untracked ∩ tracked@b5653fb7 = 604, hash-identical 604, different 0; ls -la *.db-wal *.db-shm (0 / 32768)
```
