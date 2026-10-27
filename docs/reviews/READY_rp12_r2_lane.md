# READY_rp12_r2_lane: rp12-r2-lane 189ca607 (base main 1f671215) for ARCH-V2-E-T-R2

Reviewer: adversarial-reviewer, 2026-10-01. Zero calls, no construction, no DB opened by any check below (selftests use temp
dirs; ConfigParsesTest only parses TOML text). Registration: section "## Registered 2026-10-01 (before any code or call) —
ARCH-V2-E-T-R2: ..." (prog L22417-L22434) with the C-G-1 brackets (L22436-L22443).

## VERDICT

- **MERGEABLE** (by path, 38 files: 10 under tools/analysis/, 28 under experiment_configs/rp12_r2/; nothing else).
- **R2 B0 READY** (the four R2 builds B0, B0', o1, o2 from ONE pinned commit), under conditions C-1..C-3 below.
- **FLAT R2: NOT READY, census OWED** (fail-closed as built: lane r2 has snapshot / leaves / fit_n = None and refuses).

## Per-claim table (deciding claims only)

| # | claim | result | evidence (command id below) | sev |
|---|---|---|---|---|
| 1 | R1 objects byte-identical | CONFIRMED: 0 of 38 changed paths under experiment_configs/rp12/; 0 under src/; 0 outside tools/analysis + rp12_r2 (counts) | K1 | - |
| 2 | R1 default commands unchanged | CONFIRMED: `rp12_build_configs --check` OK (27); defaults resolve to the old paths (g11/g13 OUT_DEFAULT, g12 CONFIG_DEFAULT, G14 OUT_DIR asserted in selftests); h9 no-flag byte-identical to base blob 2b77fcd4 (7/7 in the branch worktree); v2_declared_cells refuses --lane without --tree-cells | K2, K3 | - |
| 3 | R2 TOMLs = R1 except lane paths | CONFIRMED: 28 of 28 (27 generated + sitenull) equal R1's bytes after dropping the one `# LANE R2` line and mapping rp12_r2 -> rp12; 0 CR in all 28; `--check --lane r2` OK (27) | K4, K2 | - |
| 4 | lane isolation (paths, pointers, snapshot ids) | CONFIRMED on every readout entry: selftests pass and exercise refusals; own mutants M1-M5, M7 killed; G12 main's guard executed by hand (both crossings refuse); absolute worktree paths refuse in lane r2 | K3, K5, K6 | - |
| 5 | "contains the merged EMD by construction" | PARTLY: the branch descends from 1f671215 (merge-base = 1f671215; main has 0 commits past it), so any merge contains EMD; but NO tool checks that the build commit contains 1f671215: g10's D-8 checks only that a pair shares one commit. The pin is the operator's (C-1) | K1, K7 | MEDIUM |
| 6 | ConfigParsesTest passes on the new TOMLs | CONFIRMED for the 24 R2 member TOMLs (tests 9 / failures 0 / errors 0, fresh run 09:31, 9 tasks executed; walk is recursive over *.toml, 237 files). The 3 graft templates (*.toml.tmpl) are NOT parsed by it (C-3) | K8 | LOW |
| 7 | FLAT's R2 census is owed | CONFIRMED: set_lane("r2") -> T2 run rp12_r2/B0/mmlu_pro_lb, pointer rp12_r2, census None; check_census and require_preconditions refuse; main() reaches set_lane (stubbed dry_run printed the r2 T2) | K3, K6 | - |

## Pins (LF of record; `git hash-object` in the branch worktree = `git rev-parse 189ca607:<path>` for all 10; 0 CR)

flat_v2 eb9b1986; g10_compare e5fa7e34 (supersedes READY blob 1f1e20a9: the delta adds lane_guard, write_pointer/g10
guards and the --pointer default only; no compare function touched); g11_reader b86832e3 (PAIRING_PIN re-pinned to
35214b3f = rp12_pairing at tip); g12_site_null 0cf5b091; g13_comparator 61d83ec7; h9_stability 0814869f;
rp12_build_configs d87c9337; rp12_lane ac25b152; rp12_pairing 35214b3f; v2_declared_cells c5b90278 (all `blob:` prefixes).

## Own mutants (deciding paths)

| id | change | result | decisive |
|---|---|---|---|
| M1 | rp12_lane.require: `inside` clause disabled | killed (rp12_lane 2 fails, g10 15/16) | yes |
| M2 | lane_of case-sensitive | killed (rp12_lane) | no |
| M3 | require_snapshots never refuses | killed (rp12_lane, build_configs, g10) | yes |
| M4 | g10 lane_guard: own-pointer check off | killed (g10 15/16) | yes |
| M5 | build_configs: r2 outputDir uses R1 root | killed (build_configs 2 fails) | yes |
| M6 | g12 main(): lane_check call removed | **SURVIVED** (10/10) -> D-2 | no (default config is lane-aware) |
| M7 | g10 write_pointer: lane_guard removed | killed (g10 15/16) | yes |
| M8 | flat_v2 main(): set_lane(a.lane) removed | **SURVIVED** (13/13) -> D-1 | yes for FLAT R2 (would read R1's T2 and census, write R1's outcome path) |

Builder selftests at tip: rp12_lane PASS, rp12_build_configs PASS, g10 16/16, g11 8/8, g12 10/10, g13 7/7, rp12_pairing 5/5,
h9 7/7, flat_v2 13/13, v2_declared_cells 100 checks 0 failed, mutants 22/22.

## Conditions

- **C-1 (BLOCKER for any R2 build; the operator's pin).** Merge by path on main as ONE commit M (`git checkout 189ca607 --
  <the 38 paths>`, `git commit -F <msg> -- <the 38 paths>`). Then, each printed by count before B0:
  (a) `git merge-base --is-ancestor 1f671215 M` rc 0 (EMD merge) and `git merge-base --is-ancestor 12ceb48c M` rc 0 (g10-r2);
  (b) `git diff --name-only 189ca607 M -- tools/analysis experiment_configs/rp12_r2 | wc -l` = 0 (the reviewed blobs);
  (c) `git diff --name-only 1f671215 M -- src build.gradle.kts settings.gradle.kts | wc -l` = 0 (the engine is exactly
  EMD-merged main's); PIN = M (if main has moved, PIN = M still, never a later tip);
  (d) `git worktree add --detach <wt> M`; in it `rp12_build_configs.py --check` and `--check --lane r2` both OK (27), and
  `git status --porcelain | wc -l` = 0; B0, B0', o1, o2 all from this one worktree (D-8);
  (e) after the builds: every R2 run_manifest.json (24 members + 3 grafts = 27) has `commit` = M and `dirty_src` false
  (count 27/27; g10's pairwise D-8 check alone does not prove this).
- **C-2 (before FLAT R2 --run).** A reviewed delta pins R2's T2 census (snapshot from the R2 pointer, leaves, fit_n) AND
  adds a main()-level test for lane r2 (D-1). Until then FLAT R2 stays refused, as built.
- **C-3 (before the R2 graft runs).** After `--fill --lane r2`, the three filled graft TOMLs are parsed (re-run
  ConfigParsesTest, which now walks them) before launch.
- Readouts run either from the pinned worktree's tools or with the run dirs copied byte-identically into main's
  experiment_results/archv2/rp12_r2/; lane r2 refuses absolute worktree paths (shown, K6), fail-closed.
- Registrar: bracket the registration's INSTRUMENT pin of g10_compare (1f1e20a9 -> e5fa7e34, lane guards only, this review).

## Defects

- D-1 MEDIUM: flat_v2 main()'s `set_lane` is untested (M8). Fix: selftest calling `main(["--dry-run","--lane","r2"])` with
  dry_run stubbed, asserting T2["run"] and OUTCOME under rp12_r2. Lands with C-2.
- D-2 LOW: g12 main()'s lane_check untested (M6); the refusals work (K6). Fix: selftest calling main with crossed --config.
- D-3 LOW: rp12_lane.rel does not normalise `..`: `experiment_results/archv2/rp12_r2/../rp12/B0/bbh` is classed r2. Fix:
  `posixpath.normpath` in rel().
- D-4 LOW: in lane r1 an absolute path to an R2 object outside ROOT (e.g. a worktree) is lane None and accepted (lane r2 is
  safe via `inside`). Fix: classify on the path suffix after the last `experiment_results/archv2/` / `experiment_configs/`.
- D-5 LOW: flat_v2 `--dry-run --tree-snapshot <id>` is not passed through require_snapshots; exploratory (printed only),
  but the C-2 census pin must take its snapshot from the R2 pointer, not from an override.
- D-6 LOW: ConfigParsesTest is a size>30 presence check; it does not assert that rp12_r2 files were among those parsed
  (they are, by the recursive walk; count 24 of 237).

## Commands (K-ids)

```
K1  git diff --name-only 1f671215..189ca607 | grep -c '^experiment_configs/rp12/'            -> 0
    ... | grep -c '^experiment_configs/rp12_r2/' -> 28 ; grep -c '^tools/analysis/' -> 10 ; grep -vc -e tools/analysis -e rp12_r2 -> 0
    ... | grep -c '^src/' -> 0 ; git merge-base rp12-r2-lane main -> 1f671215 ; git log --oneline 1f671215..main | wc -l -> 0
K2  (branch worktree) python tools/analysis/rp12_build_configs.py --check -> OK (27 files); --check --lane r2 -> OK (27 files)
K3  (branch worktree) python tools/analysis/<t>.py --selftest for t in rp12_lane rp12_build_configs g10_compare g11_reader
    g12_site_null g13_comparator rp12_pairing h9_stability flat_v2 v2_declared_cells ; git status --short | wc -l -> 0
K4  scratchpad/tomlcmp.py: for each of 28 rp12_r2 files, git show 189ca607:<f> minus '# LANE R2' line, rp12_r2->rp12,
    == git show 1f671215:<rp12 path>  -> 28 / 28 equal; b'\r' count 0 in all 28
K5  scratchpad/m (git archive 189ca607 tools experiment_configs src data_v2/manifests): mut.py M1-M8, one edit at a time,
    restored after each
K6  scratchpad/m: g12 main(['--dry-run','--lane','r2','--config',<R1 sitenull>]) and (['--dry-run','--config',<R2 sitenull>])
    -> both [RP12-LANE] REFUSED; flat_v2.main(['--dry-run','--lane','r2']) with dry_run stubbed -> T2 run
    experiment_results/archv2/rp12_r2/B0/mmlu_pro_lb/seed_42, census None, outcome under rp12_r2/flat_v2;
    rp12_lane.guard('r2', [<abs .claude/worktrees/X/.../rp12_r2/...>]) -> REFUSED (outside roots);
    lane_of('experiment_results/archv2/rp12_r2/../rp12/B0/bbh') -> 'r2' (D-3)
K7  sed -n '/^def precondition/,/^def g10/p' g10_compare.py: compares ca == cb only; R1 manifest keys commit, dirty_src present
K8  (branch worktree) ./gradlew.bat test --offline --no-daemon --tests taxonomy.runner.ConfigParsesTest -> BUILD SUCCESSFUL;
    TEST-taxonomy.runner.ConfigParsesTest.xml tests=9 failures=0 errors=0; find experiment_configs/rp12_r2 -name '*.toml' | wc -l -> 24;
    gradlew --stop; git status --short | wc -l -> 0
```
