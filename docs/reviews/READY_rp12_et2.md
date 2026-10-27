# READY delta review: rp12-et2 (ARCH-V2-E-T), tip ec6987f from 225e4fd

Reviewer: adversarial reviewer, 2026-09-30. Zero calls. No production DB read, nothing constructed. Detached worktree
`.claude/worktrees/rv-rp12-et2` at ec6987f. Scope: `git diff 225e4fd..ec6987f` (5 commits, 41 files) against READY_rp12_et
(03760e2) C-0..C-7 / D-1..D-7, the registration L22028-L22060 and the registrar's record L22136-L22144. What 03760e2 CONFIRMED on
untouched code (claims 1-6, 10; Support arithmetic claim 5) is cited, not re-derived. Pool files e20f3b8 taken as given (C-1 done).

## VERDICT

- **MERGEABLE: all 5 commits** (04ff6c4, e8ff15e, bf2964b, faa7ec3, ec6987f). 0 path overlap with main since 225e4fd;
  `git merge-tree` clean; 0 of 41 files match application.yml / .env / .gitignore / report/ / *.db / docs/.
- **B0 (the six B0 member builds + the B0 flatLeaf and descent grafts, then STOP): READY WITH CONDITIONS B0-1..B0-4.**
  B0-1 and B0-2 are registrar brackets that must be committed before the first member build.
- **B0', o1, o2: NOT READY** until the C-2 proof below is complete (any missing or miscounted line = failed precondition).
- Owed before readouts (not before B0): G10 D-8, R-1 (G11), FLAT D-10, G12 site-null config (own review).

## Decisions asked

- **DEV-1 (MMLU-Pro member = MMLU_PRO_LB on multicorpus_cache_v1.db with pv2_1575): ADMISSIBLE, but a change to the registered
  HYGIENE line, so a pre-data registrar bracket (B0-1), never silent.** Own count on the side export (blob 716b3b84): MMLU-Pro
  EVAL 3,492 and GATE 1,157 are identical on both routes (all carry the mc6 tag); TRAIN is **7,001 items via the mmlu_pro
  table vs 6,994 via MMLU_PRO_LB** (the 7 mmlu-pro-v2-only items are all TRAIN). Both files carry the same 8,186 global
  reserved keys. So the EVAL denominator, the leakage guard and G12's m (14 declared MMLU-Pro domains) are unchanged. What moves:
  the member's TRAIN input shrinks by 7 items (0.10%), far below FLAT's MDE 0.0215 and every G11/G13 MDE, so no Support line
  moves. The reason holds on code read: one `corpusDbPath` per config, so a mixed graft cannot load both tables.
  **pv2_41's file no longer guards any RP12 construction** (0 RP12 TOMLs name it; `v2ForeignMembers` is empty). It still guards
  FLAT's EVAL side only: flat_v2 R1 reads its judgeable EVAL ids, and `engine_pool()` refuses on another pool id or side-export sha.
  FLAT reads no T2 stamp, so nothing ties T2 to pv2_1575 (D-10).
- **R-1 (G11 attenuation slope): NOT defined in the registration.** `grep -n -i "attenuation slope"` shows the span names it once
  (L22037). The only definition of record is ROUTING-ATTENUATION (L3777-L3785): the slope of C_19 on C_0 over judged per-cell
  contrasts under simulated misrouting. The framing (L70) quotes it as "between 0.80 and 0.68". Its inputs (judged cell
  contrasts) do not exist in this zero-call build. **The registrar must bracket either a definition (verdict store, misrouting
  model at 1 - P_fl, grain) or "not computed" before the G11 outcome is written.** It is descriptive, so it moves no verdict and
  does not block B0. g11_reader prints it as OWED, which is correct.
- **G10 declared exclusions:**
  - ACCEPTED: READY C-4's list; manifest config_path / config_sha256 and the stamp's configSha256Lf (B0p differs from B0 only in
    outputDir: own diff over 7 pairs, 1 line each); proposal_memo_digest_ms (a timing).
  - NOT covered (D-8): the manifest also carries commit, branch, dirty, dirty_src(_files), dirty_other(_files) and dirty_files
    (DiagnosticsBundle L79-L98), and A5 compares them. If main's HEAD moves between B0 and B0' (any docs commit), G10 reads
    FAILED and the lane STOPS on a non-construction field.
  - Snapshot config / settings carry no output path (EffectiveConfig and SnapshotSettings: 0 path fields), so A4 is safe.
  - The starved-pass count prints "NOT RECORDED by the engine" (D-9 LOW).
- **KA3 by source scan: ACCEPTABLE ONLY as a regression tripwire, never as execution evidence.** Own RV7 (a semantic mutant the
  scan does not see): drop `lines.forEach { log.warn(it) }` in assembleUnion, so no [SPLIT-V2] UNION member line is printed.
  It SURVIVES the 11 V2 / runner / RP12 test classes (executed, XMLs re-written). Only C-2's COUNTED lines show that the graft
  ran its v2 path.

## Per-claim table (deciding claims only)

| # | claim | result | reviewer's evidence | sev |
|---|---|---|---|---|
| 1 | C-0: 24 member TOMLs + 3 graft templates from one recipe = bareq512_s42 geometry, labelling / judge OFF, v2PoolFile + pool pv2_1575, 12 threads; B0p = B0 up to outputDir; o1/o2 add shuffle seed 1/2 | CONFIRMED | `--check` OK (27 files); geometry block `diff` against the promoted TOML from `dagMode` on (comments stripped): 0 lines; counts: 27/27 labelling false, 27/27 judgeInduction false, 0 files lack -PjvmThreads=12, 0 name Meta-Llama-3-70B, shuffle seed 1 x6 / 2 x6; B0 vs B0p diff = outputDir only (7 pairs); descent template differs only in rule and outputDir. RV5 (mcs 55->56 in the generator) KILLED (--check exit 1, 27 defects; selftest FAIL) | - |
| 2 | DEV-1 admissible (same 3,492 EVAL) | PARTLY | EVAL 3,492 = 3,492, GATE 1,157 = 1,157; TRAIN 7,001 vs 6,994 (not stated by the builder). Admissible by bracket (B0-1) | HIGH (process) |
| 3 | D-2 allow-list; D-7 union config sha; D-1 log text; KA2 extraction | CONFIRMED (code read + suite) | checkUnionMembers refuses any foreign pool not on (pool, sha) list; activateUnion stamps LF sha of the graft TOML; builder mutants E1-E9 not re-run (suite green covers the tests that killed them) | - |
| 4 | Suite | CONFIRMED | `gradlew test --offline --no-build-cache --rerun-tasks`: **507 tests, 2 failed** = the allowed MrlRoutingTest / TraceEnvelopeUnwrapTest; equals builder | - |
| 5 | Python selftests | CONFIRMED | rp12_build_configs PASS; g10 11/11; g11 6/6; flat_v2 11/11; g13 6/6; rp12_pairing 3/3 | - |
| 6 | G11 reader = registration (verdict clauses, paired same-draw component bootstrap B 2,000, 6,153/5,642 refusal, DEFF/n_eff/MDE printed) | CONFIRMED | code read L96-L148; RV1 (`>=` -> `>` at the bar) KILLED; RV2 (count refusal off) KILLED; RV3 (unpaired D draws) KILLED. D-11: "Kish mean" prints Σm²/n, not the registered n/G 1.091 | LOW |
| 7 | G10 comparator = registration (declared set, stamp S1-S4, pointer file write-once) | PARTLY | RV4 (`held = False` dropped on a diff) KILLED (6/11). D-8 (git-state keys) is a false-FAIL path; RV6 (exclude `commit`) SURVIVED (no test pins that the key is compared, or its handling) | MEDIUM |
| 8 | Registered precondition "pool_guard.py --pool pv2_1575… before and after every build" is executable | REFUTED | `experiment_configs/reserved_pools.json` holds 2 pools, 0 pv2 ids; pool_guard hashes legacy id lists (L235-L238), a different scheme from pv2_ (sha256 of EVAL component ids). As written it can only refuse. The e20f3b8 run.log never called it | HIGH (B0-2) |
| 9 | C-5 / C-6 / D-3..D-6 fixes | CONFIRMED (selftests + builder's mutants R1-R8, H1-H6 by their tests passing; RA4/RA5/RA6 now have killing cases) | - | - |
| 10 | Pins (LF of record; worktree CRLF, autocrlf) blob / sha256-lf16 / sha256-crlf16 | CONFIRMED = builder's | g10_compare a6d6e8c4 / 06a3be79eece4972 / 98916a40b75cca6b; g11_reader cd78ff4d / cb79be00f6476953 / 2fb4d90118a77446; flat_v2 65d12abd / 576af317b9e47259 / a9a93367bc78ee02; g13_comparator 03584cc3 / 5f391683f5d27972 / 535312c1c05f99a4; rp12_pairing f8e8db87 / 7ce8e2cb482431ce / 03f8ec8759eae33d (= g11's PAIRING_PIN); v2_declared_cells b97af783 / 2a83cba7b0e368f7 / 9de4be9c519256c2; rp12_build_configs 6a0247a3 / d28437f74202f958 / 24fc8588a9c1daec; V2EnginePool.kt a70379e3 / dbbd9531cf4a179f; HeadlessBenchmarkRunner.kt 7641007b / 73621e7095abdab4; UnionRoutingExport.kt a3f3e34d / e8124ce77c94e4bb; MMLUDatasetFetcher.kt d424284a / 3184340572500321; B0/mmlu_pro_lb.toml 5e11d95a / 042618d69590b7db; B0 graft_flatleaf.tmpl 13523baf / cfb50ac2d79f9cce; graft_descent.tmpl c258a881 / fb19b2b85ff57224. Pool file on main: blob 1597fb0d, sha256-lf16 79d48f4b36434a55 (working tree = LF) | - |

## Reviewer's mutants (one edit each, reverted; `git status --porcelain | wc -l` = 0 after)

| id | change | result | decisive |
|---|---|---|---|
| RV1 | g11 verdict `fl_lo >= BAR` -> `>` | KILLED (5/6) | yes (G11 boundary) |
| RV2 | g11 compute: registered-count refusal disabled | KILLED (5/6) | yes (denominator) |
| RV3 | g11 boot_both: D drawn on independent resamples | KILLED (5/6) | yes (paired interval) |
| RV4 | g10: a byte difference no longer sets FAILED | KILLED (6/11) | yes (G10 verdict) |
| RV5 | rp12_build_configs geometry mcs 55 -> 56 | KILLED (--check exit 1; selftest FAIL) | yes (recipe drift) |
| RV6 | g10 MANIFEST_EXCLUDED += "commit" | SURVIVED | no; shows D-8's keys are unpinned |
| RV7 | runner L1213 `lines.forEach { log.warn(it) }` removed (graft prints no member line) | SURVIVED (11 classes executed) | yes for C-2: only the counted lines prove the graft |

## Conditions for B0 (all before the first member build unless named)

- **B0-1 (registrar, pre-data):** bracket DEV-1 into HYGIENE. MMLU-Pro member = MMLU_PRO_LB on multicorpus_cache_v1.db under
  pv2_1575de61bb20e977; EVAL 3,492 / GATE 1,157 unchanged; TRAIN 6,994 items (vs 7,001); pv2_41's file is kept for FLAT's
  held-out only; the C-2 wording "MMLU-Pro admitted on its stamp, pv2_41" is superseded (six "== the file's").
- **B0-2 (registrar, pre-data):** replace the unexecutable pool_guard precondition with the pv2 form, run before AND after every
  build (a pool reader, outside the construction window):
  - `python tools/analysis/v2_union_pool.py --dry-run` must print the first line "pool pv2_1575de61bb20e977 recomputed … expected
    pv2_1575de61bb20e977" and "every check passed".
  - `sha256sum` of the committed file must be 79d48f4b36434a55… (LF).
  - 0-byte -wal / -journal beside the DBs read.
- **B0-3 (operator):**
  - `rp12_build_configs.py --check` exit 0 (27 files).
  - `git status --porcelain --untracked-files=no -- src build.gradle.kts` = 0 lines; the commit printed and kept for G10 (D-8).
  - Rule 7 W1-W5; backup with per-table hashes (embeddings_cache.db queries + reserved_pool_meta, snapshots.db, multicorpus DB).
- **B0-4 = the C-2 proof. It must print, and be COUNTED; any missing or miscounted line stops the lane before B0' / o1 / o2.**
  - (a) Each of the 6 member builds:
    - `[THREAD-CAP]` with availableProcessors = 12.
    - `[SPLIT-V2]` with one-to-one TRAIN and RESERVED hold and "0 TRAIN rows share a stem key with the 8186 global reserved keys".
    - `[TRAIN-ONLY] global reserved keys installed: 8186`; TrainOnlyGuard 0 EVAL members.
    - A stored non-null buildStamp with poolId pv2_1575de61bb20e977 and enginePoolSha256Lf = 79d48f4b36434a55….
    - The manifest carries split_v2 and dirty_src = false; 0 labelling and 0 judge calls.
    - MMLU_PRO_LB only: its TRAIN item count printed (expected 6,994; the DEV-1 census) with its TRAIN row count.
  - (b) Fill both graft templates with `--fill` (write-once, no placeholder left). Each graft (flatLeaf, descent) must print:
    - **exactly 6** `[SPLIT-V2] UNION member … == the file's` lines and **0** "foreign" lines;
    - `[TRAIN-ONLY] union graft: global reserved keys installed: 8186 (pv2_1575de61bb20e977)`;
    - the `[POOL-PIN]` line;
    - a union snapshot with a non-null buildStamp whose configSha256Lf = the LF sha of the filled TOML;
    - a manifest carrying split_v2 and union_routing_item_key = true.
  - (c) `rp12_pairing --g13-bundle` must give EVAL **6,153 items / 5,642 components**, the GATE rows dropped,
    `<no-routing-row>` by side with **0 among EVAL**, and the `<unrouted>` tie count.
  - (d) `g11_reader.py --dry-run` on both readouts must show the same item set, 6,153 / 5,642, and no statistic.
  - (e) `g10_compare.py --write-pointer` once, after B0.
  - (f) The pv2 guard of B0-2 again; the DB hashes compared with the backup (the reserved_pool_meta rewrite reported, not
    treated as a breach).

## Defects owed before their readouts (each with its fix)

- **D-8 MEDIUM (before G10 is scored).** A5 compares git-state keys. Fix in g10: compare commit, branch and dirty_* by rule. Both
  runs need dirty_src = false AND `git diff --quiet <cA> <cB> -- src build.gradle.kts settings.gradle.kts gradle` (printed), or
  the commits must be equal. Also assert that each B0/B0' TOML pair differs only in the outputDir line (count = 1). Add a
  selftest that kills RV6.
- **D-9 LOW.** The starved-pass count is not recorded by the engine. The registrar notes "NOT RECORDED" as the descriptive
  print, or it is derived from proposals.csv by a reviewed delta.
- **D-10 MEDIUM (in the FLAT T2 delta).** flat_v2 must refuse unless T2's stamp is poolId pv2_1575de61bb20e977 with
  enginePoolSha256Lf 79d48f4b…. ENGINE_POOL_SHA_LF stays pv2_41's file sha 8f1ed122bfb45e43… (the held-out file), not pv2_1575's.
- **R-1 (registrar, before the G11 outcome).** Bracket the attenuation slope: either a definition or "not computed".
- **D-11 LOW.** g11 labels Σm²/n as "Kish mean". Print n/G (1.091 registered) and name the Σm²/Σm bound beside it, as flat_v2 D-6.
- **G12 (own review before the site null).** No site-null config is on the branch. It must run on B0's MMLU_PRO_LB member (from
  the multicorpus DB) and print m ≤ 15 against 14 declared domains.

## Commands (reviewer's own)

```
git worktree add --detach .claude/worktrees/rv-rp12-et2 ec6987f
git diff --name-only 225e4fd..ec6987f | wc -l                                             # 41
git diff --name-only 225e4fd..ec6987f | grep -c -E "application.yml|\.env|\.gitignore|report/|\.db$|^docs/"   # 0
comm -12 <(git diff --name-only 225e4fd..ec6987f|sort) <(git diff --name-only 225e4fd..HEAD|sort) | wc -l      # 0; merge-tree clean
./gradlew.bat test --offline --no-build-cache --rerun-tasks                                # 507 completed, 2 failed (allowed)
for s in rp12_build_configs g10_compare g11_reader flat_v2 g13_comparator rp12_pairing; do python tools/analysis/$s.py --selftest; done
python tools/analysis/rp12_build_configs.py --check                                         # OK (27 files)
python - side export 716b3b84 rows[2:]: Counter((side, source, mc6-tag, v2-tag)) for MMLU_PRO -> EVAL 3492 / GATE 1157 / TRAIN 6994 mc6 + 7 v2-only
grep -rl Meta-Llama-3-70B experiment_configs/rp12 | wc -l (0); grep -L PjvmThreads=12 ... | wc -l (0); diff B0/<m> B0p/<m> (outputDir only)
python reserved_pools.json keys with 'pv2' -> [] (2 pools); grep -n -i "attenuation slope" docs/judge_v2_program.md
git rev-parse ec6987f:<p>; git show ec6987f:<p> | sha256sum; sha256sum < <worktree p>
mutants RV1-RV6: python in-place replace (assert count==1) or sed on a line -> selftest/--check -> restore; RV7: sed L1213 ->
  gradlew test --tests 'taxonomy.dataset.V2*' --tests 'taxonomy.runner.*' --tests 'taxonomy.service.V2*' (BUILD SUCCESSFUL; 11 XMLs re-written)
```
