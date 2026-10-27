# READY review: rp12-et (ARCH-V2-E-T engineering), tip 32a0eff from 32c4c72

Reviewer: adversarial reviewer, 2026-09-30. Zero calls. No production DB was read and nothing was constructed. The review ran
in its own detached worktree `.claude/worktrees/rv-rp12` at 32a0eff. Registration of record: programme L22028-L22060, with the
rulings at L22019-L22026 (_as_of 44ab46f).

## VERDICT

| commit | what | MERGEABLE | notes |
|---|---|---|---|
| 5fad38c | engine pool file (gen + loader), stamp, global closure, TrainOnlyGuard | YES | leakage paths fail closed (claims 1-3) |
| 9723e32 | h9_stability --baseline (G15) | YES | C-3: the G15 scope needs a ruling (on the union it is vacuous) |
| c2c0a8a | g13_comparator (G13) | YES | D-5 LOW (boundary untested) |
| 530b60f | v2_declared_cells --tree-cells (G14) | YES | C-5 (<no-routing-row> among scored EVAL) |
| 668bec2 | flat_v2 (FLAT) | YES | preconditions owed by design; C-6 |
| ca8d483 | union graft pool file + graft wiring | YES | graft path UNEXECUTED (KA3 survives); C-2 |
| 32a0eff | item key + pairing builders | YES | export TRAIN path UNEXECUTED (KA2 survives); D-4 MEDIUM |

- **B1/B2 pool-file generation run (v2_engine_pool.py, v2_union_pool.py): READY**, subject to C-1.
- **RP12 build (B0, B0', o1, o2): NOT READY.** No build TOML exists on the branch or on main (`git grep -l v2PoolFile
  32a0eff -- experiment_configs` gives 0, and 0 on main). It becomes READY on a delta review of the build configs (C-0) that
  also sets the staged B0 proof (C-2) and carries the G15 scope ruling (C-3).

## Per-claim table (deciding claims only)

| # | claim | result | reviewer's evidence | sev |
|---|---|---|---|---|
| 1 | Nothing reaches construction outside TRAIN: `splitByV2Pool` TRAIN ids equal the file's train_ids one-to-one; EVAL, GATE and the negative-id sentinels among them are reserved | CONFIRMED | Code read. The split is by the export's per-item side (item = `i:`+stem_key), so twins cannot straddle sides. The TRAIN one-to-one is checked both ways. There are 3 FATALs (unlisted row, GLOBAL CLOSURE, reserved row with no key), and the after-construction and saveSnapshot guards add `withGlobal`. KA1 (reserved-unkeyed check removed) is KILLED, so the two-language key agreement is tested | - |
| 2 | GATE is reserved, not a slice of TRAIN (a semantic change from the legacy `finishSplit`) | CONFIRMED, matches the design | The v2 design has GATE as held back from construction (prog L15164; L17733 H5: "GATE is routed statelessly"). `Split.gate` has no consumer (`EpochGate.NONE`; the only reader is the gate_ids.json writer). The consequence is D-1 | - |
| 3 | Inertness with v2PoolFile, stamp and global keys absent, where the proof executes the new code | CONFIRMED | V2SplitInertnessTest G1-G5 carry base goldens and execution discriminators: the `consultations()` counter moves on the absent path, the serializer descriptor holds `buildStamp`, and G4 counts ≥3 predicate reads. V2RoutingItemKeyTest is byte-equal to base 32c4c72's inline strings, with a source scan. The full suite ran with `--no-build-cache --rerun-tasks`: **502 tests, 2 failed**, and those 2 are the allowed ones (MrlRoutingTest, TraceEnvelopeUnwrapTest). This equals the builder's count. The new classes all pass: V2EnginePoolTest 11/11, V2SplitInertness 5/5, V2PoolConfig 4/4, V2UnionPool 4/4, V2RoutingItemKey 4/4 | - |
| 4 | Pool ids and denominators: union EVAL 6,153 / 5,642; MMLU-Pro EVAL 3,492 / 3,400 | CONFIRMED to the digit | Own script on the committed side export (blob 716b3b84): the mc6 EVAL components give **pv2_1575de61bb20e977, 5,642 comps, 6,153 items**; mmlu-pro-v2 gives **pv2_41dbd3dbcd399df0, 3,400, 3,492**. The Kish means are 1.0906 and 1.0271, against the registered 1.091 and 1.027. mc6's MMLU_PRO EVAL items are the same 3,492 as mmlu-pro-v2's (intersection 3,492). The 7 items tagged mmlu-pro-v2 only are all TRAIN. Global reserved keys = non-TRAIN items = **8,186** (6,153 EVAL + 2,033 GATE; TRAIN 12,358) | - |
| 5 | Support arithmetic (check 8) | CONFIRMED, with 1 LOW | Every SE and MDE reproduces: 0.00574, 0.00554, 0.00497, 0.00768, 0.01258; MDE 0.0161 / 0.0155 / 0.0139 / 1.73pp / 1.11pp / 0.0215 / 0.84e-3 / 0.0352. D-6: for FLAT M1 the ICC-1 bound with variable sizes is Σm²/Σm = **1.071**, not 1.027. At 1.071 the SE is 0.00783 and the MDE 0.0219. This does not move the effective bar (spread_V 0.0305) | LOW |
| 6 | P1 modal cell; P2 fl = top1 at item level | CONFIRMED (a reading) | P2 is the engine's `top1` = leaf TRAIN-majority == declared key. This is the column MC-ROOT's 81.58% reports ("union Top-1"; domain acc is 81.12%, docs/multi_corpus_design.md L421), so it is not C-7. P1 is deterministic, but `<unrouted>` (0x3C) sorts before every label and so wins every tie. A routed row on a profile-less leaf also becomes `<unrouted>` (D-3) | LOW |
| 7 | P6 `<no-routing-row>` | PARTLY | The filled count is printed only as a total, not by side. An EVAL item of G14's 5,907 scoring set in that cell gets a synthetic cell's policy, with no refusal (C-5) | MEDIUM |
| 8 | Graft wiring (activateUnion, member check) and the flag-on TRAIN routing | UNDETERMINED (unexecuted, as declared) | KA3 (the graft never loads v2PoolFile) SURVIVES the runner and V2 tests. KA2 (TRAIN routing keeps the reserved ids) SURVIVES. Behind KA2, the builders' side refusal catches an EVAL item on a TRAIN row, but not a GATE item (RA4 survives, D-4) | MEDIUM |
| 9 | G13 verdict = registration (lo>0 AND D13>spread; hi<0 AND D13<-spread) | CONFIRMED | Code read. RA5 (`>` to `>=`) survives. D13 and spread_KC are both multiples of 1/6,153, so the two can tie (D-5) | LOW |
| 10 | Pins (LF of record; the worktree renders CRLF, core.autocrlf true) | CONFIRMED | Pins as blob / sha256-lf16 / sha256-crlf16. Tools: v2_engine_pool.py 435ee57c / 7d7d83a4aa35e60c / e9123a8696a96c38; v2_union_pool.py 57339d46 / 244df16933fb60ef / 54467d0ded415729; g13_comparator.py c5d0c465 / a0aba1b4cf25d1cd / b4626488aadd406f; flat_v2.py f3e1ecbb / 20d73f1c28530357 / 470c9033801f7c3d; h9_stability.py 2781d094 / 2ef89c3c175d2756 / 66e076d7c881fb6c; v2_declared_cells.py e3baaf38 / 7dba5eacaa684768 / c6550d14d286d3aa; rp12_pairing.py d14aab7d / 84e7600df08cdcdc / d351d363e4d776ec. Kotlin: V2EnginePool.kt f26b9aa0 / 17b922376cdfbaf7; TrainOnlyGuard.kt 8b4f5132 / a8224359cbf6c859; MMLUDatasetFetcher.kt db3e06d1 / 1da853c256e638f7; HeadlessBenchmarkRunner.kt a993a336 / 682de97bb08c6a2f; UnionRoutingExport.kt 9096ee18 / 8574604dae419be0. The imported bases are unchanged: flat_mix_mmlu 555ae3ac, cert_resolution dbe9425d, h9 base 2b77fcd4, v2_declared_cells base f7f30ebe. All tool pins equal the builder's messages | - |
| 11 | Hygiene | CONFIRMED | 25 files; 0 match application.yml / .env / .gitignore / report/ / *.db; 0 under docs/ (`--name-only \| grep -c`). There is 0 path overlap with main since 32c4c72, so the branch merges without conflict. The worktree shows 0 untracked outputs after the suite, and the main DB mtimes are unchanged | - |
| 12 | Python selftests | CONFIRMED | v2_engine_pool 12/12, v2_union_pool 8/8, g13 6/6, flat_v2 9/9, h9 6/6 (no-flag byte-equal to base), rp12_pairing 3/3, v2_declared_cells 93 checks + 22/22 mutants | - |

## Reviewer's mutants (one edit each, reverted; `git status` clean after)

| id | change | result | decisive |
|---|---|---|---|
| KA1 | MMLUDatasetFetcher: `reservedUnkeyed` check disabled | KILLED (V2EnginePoolTest L178) | yes: the two-language key |
| KA2 | runner exportUnionRouting: TRAIN filter `it.id !in reservedIdSet` -> `true` | SURVIVED | no (a downstream refusal catches EVAL); shows the path is unexecuted |
| KA3 | runner assembleUnion: `v2Union = null` (no member check, no global keys, no union stamp) | SURVIVED | yes for C-2: only the operator's printed lines can show the graft ran |
| RA4 | rp12_pairing split_items: TRAIN rows of GATE items accepted | SURVIVED | yes (D-4): the only guard against GATE entering the KC / G14 fits |
| RA5 | g13_verdict: `d > spread_kc` -> `>=` | SURVIVED | LOW (a tie is possible) |
| RA6 | flat_v2 v2_sets: GATE admitted to the held-out set | SURVIVED | LOW (the held-out comes from eval_ids only) |

## Defects and conditions (each with its fix)

- **C-0 (BLOCKER for the build, not for merge).** No RP12 build TOMLs exist: six members, the graft, B0', o1, o2. Fix: commit
  them for a delta review. They need the bareq512 geometry with labelling / judge induction OFF; `v2PoolFile` set (pv2_41 for
  the MMLU-Pro member, pv2_1575 for the other five and the graft); `pool` = the v2 id; the graft with
  `unionRootRouting = flatLeaf` AND a descent graft/export, both with `unionRoutingItemKey = true` (G11's D_fd needs both
  rules per item); `-PjvmThreads=12`.
- **C-1 (pool-file run).** This is a pool reader, run in a rule-7 window. Run `--dry-run` first, then the write-once run.
  The first printed line must be the pool id. The Kotlin loader (L1-L5) must accept both files before any build, and must
  print global reserved keys = **8,186** for each file. pv2_41 must print eval/gate/train id counts consistent with 3,492
  EVAL items. Commit both files by path and pin them (blob + sha256-lf16).
- **C-2 (staged end-to-end proof, before B0' / o1 / o2).** Build B0's six members and graft B0 first, then stop. Every
  member build must print: the `[SPLIT-V2]` split line (one-to-one hold); `[TRAIN-ONLY] global reserved keys installed:
  8186`; and a non-null stored buildStamp. The graft must print six `[SPLIT-V2] UNION member` lines. Five must say "== the
  file's". The MMLU-Pro line must say "admitted on its stamp", pool pv2_41dbd3dbcd399df0, and its stamp's
  `enginePoolSha256Lf` must equal the committed pv2_41 file's LF sha. The operator compares that sha, because the code does
  not (D-2). The graft must also print `[TRAIN-ONLY] union graft: global reserved keys installed: 8186`. The union snapshot
  must carry a non-null buildStamp, and the manifest must carry `split_v2` and `union_routing_item_key`. Then run
  `rp12_pairing --g13-bundle`, which must yield EVAL **6,153 items in 5,642 components** (it refuses otherwise). The run must
  report GATE rows dropped, and `<no-routing-row>` by side with 0 among EVAL. The graft is the only execution of KA3 and KA2's
  code: a missing line is a failed precondition, and the other three builds wait.
- **C-3 (pre-data ruling, registrar / orchestrator).** G15's depth-1 anchors on the federated union are the six corpus roots.
  Their mass shares are fixed by the TRAIN counts, so drift is ≈0 and the readout is VACUOUS (check 5). Two things must be
  ruled before o1/o2 run: which members' depth-1 anchors are read (all six, max over members, is the faithful reading; the
  builder proposes MMLU-Pro only), and whether o1/o2 rebuild all six members. `--baseline` takes one member per call.
- **C-4 (before G10 is scored).** No G10 comparator exists for the v2 artefact set, and the "pointer file" is undefined. The
  timestamp fields to exclude, listed here as the registration asks: snapshots.id, snapshots.timestamp, snapshots.log_uuid;
  manifest started/finished_at_millis and duration_ms; reserved_pool_meta.created_at; headless_run.log;
  performance_report.json. **D-7 MEDIUM:** `activateUnion` stamps `configSha256Lf = null`, so G10's leg "stamp equals the
  TOML" cannot be checked on the union snapshot. Fix: pass the graft TOML's LF sha.
- **C-5 (before G14 is read).** Print `<no-routing-row>` by side. If any item of the 5,907 scoring set lands in it, refuse
  (or bracket before reading).
- **C-6 (FLAT dry-run).** R1 reads judgeable EVAL ids, not items. The dry-run must print ids vs 3,492 items and 3,400
  components; a gap over 5% is bracketed before any read (the registration's rule). ENGINE_POOL_SHA_LF and T2 are set by a
  reviewed delta.
- **C-7 (G11).** No G11 reader exists. The engine's MAIN_union_routing.csv aggregates count EVAL+GATE rows (v2 GATE sits in
  `split.test`) and twins as rows, so they are never G11. Fix: an item-level reader on the keyed CSVs (EVAL only, 6,153 /
  5,642 refusal, D_fd paired flatLeaf vs descent, component bootstrap B 2,000), with its own READY before G11 is scored.
- **D-1 LOW.** The legacy id-list pool that a v2 build records holds EVAL+GATE. A reader keyed on that legacy id reads GATE as
  EVAL. Fix: state it in the stamp or the log; never use that id as an EVAL pool.
- **D-2 MEDIUM.** `checkUnionMembers` admits any foreign-pool member of the same draw on its stamp. It checks neither the pool
  id nor the engine-pool sha. Fix: an allow-list (pv2_41 plus its file's LF sha) in the graft TOML. Until then, C-2's
  comparison stands in for it.
- **D-3 LOW.** P1's tie rule favours `<unrouted>`. Fix: print the number of ties involving `<unrouted>`.
- **D-4 MEDIUM.** RA4. Fix: a selftest case with a GATE item on a TRAIN row, which must refuse. Also make g13 `load_bundle`
  refuse GATE items among the TRAIN items, as it does for EVAL.
- **D-5 LOW.** RA5. Fix: add a boundary case at D13 == spread_KC (UNDETERMINED). **D-6 LOW:** the FLAT DEFF bound (claim 5).

## Commands (reviewer's own)

```
git worktree add --detach .claude/worktrees/rv-rp12 32a0eff
./gradlew.bat test --offline --no-build-cache --rerun-tasks   # 502 run, 2 failed (allowed); XML parsed per class
for s in v2_engine_pool v2_union_pool g13_comparator flat_v2 h9_stability rp12_pairing v2_declared_cells; do python tools/analysis/$s.py --selftest; done
python - (side export LF, rows[2:]) -> pv2 = 'pv2_'+sha256('\n'.join(sorted EVAL comps with corpus tag))[:16]; Counter by side/corpus; Kish
git rev-parse 32a0eff:<path>; git show 32a0eff:<path> | sha256sum; sha256sum < <worktree path>
git diff --name-only 32c4c72..32a0eff | grep -c -E "application.yml|\.env|\.gitignore|report/|\.db$"   # 0 of 25
git grep -l v2PoolFile 32a0eff -- experiment_configs | wc -l                                           # 0
mutants: python in-place replace (assert count==1) -> selftest / gradlew test --tests 'taxonomy.dataset.V2*' --tests 'taxonomy.runner.*' --tests 'taxonomy.service.V2*' -> git checkout -- <file>
```
