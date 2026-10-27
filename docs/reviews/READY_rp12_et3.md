# READY_rp12_et3: delta review of rp12-et3 a3d55e7 (from 3002aec; commits 1896db6, a3d55e7)

Reviewer: adversarial-reviewer, 2026-09-30. Zero calls. No production DB opened (the G12 dry-run was run against a
nonexistent `--snapshot-db`; it refused at P1 before any open). Delta review: prior review READY_rp12_et2 (9c41554) and
the registrar's record L22160-L22170 (390f9c6) are cited, not re-derived.

## VERDICT

- **MERGEABLE** (2/2 commits: 1896db6, a3d55e7). 5 files, 563+/12-; 0 under src/, gradle, docs/, report/, *.db,
  application.yml, .env, .gitignore; 0 files shared with 3002aec..HEAD (clean by path). No src change, so the gradle suite
  is not re-run (it cannot move).
- **D-8 CLOSED** (with LOW D-13 / D-14 test gaps, not blocking). The commit precondition, the TOML-pair rule (count = 1
  outputDir) and RV6 are all in place. Checked on the real committed pairs: 7/7 B0 vs B0p pairs return [] (the six
  members, and the flatLeaf graft template with its snapshot ids filled in).
- **D-10 CLOSED; D-11 CLOSED.** D-9 stays open (LOW, "NOT RECORDED by the engine").
- **FLAT: READY once B0 exists**, on one condition, F-1: a reviewed delta sets `T2` (run, snapshot, leaves, fit_n) to B0's
  MMLU_PRO_LB member, and its `--dry-run` prints the `[D-10] T2 stamp: pool pv2_1575de61bb20e977, engine pool sha256(LF)
  79d48f4b36434a55, namespaces ['MMLU_PRO'], side export 47e9048bb09a6910 ...` line. This delta is a small one; `--run`
  refuses until it lands (`require_preconditions`).
- **G12: READY-after-B0**, under conditions G-1..G-3 below. Nothing may launch before the first dry-run has printed every
  line in G-1.

## Per-claim table (deciding claims only)

| # | claim | result | evidence (mine) | sev |
|---|---|---|---|---|
| 1 | G10 refuses on different commits | CONFIRMED | selftest d8 exact message; RV8-control | - |
| 2 | G10 refuses on a missing commit | PARTLY | code `if not ca or ca != cb` correct; **RV8 (`not ca` dropped) SURVIVED 12/12**: untested (D-13) | LOW |
| 3 | TOML pair: only outputDir (count 1) + graft member ids | CONFIRMED | RV9 (`!= 1` -> `> 1`) KILLED 11/12; RV13 (quoted-line exemption outside unionSnapshots) KILLED 11/12; real pairs 7/7 [] | - |
| 4 | the same rule holds on every TOML form | PARTLY | an inline `unionSnapshots = ["A"]` never resets `in_snaps`, so a later `models` entry differing is ACCEPTED (my fixture: []); an inline list that differs is refused. Unreachable on the committed templates (multi-line) (D-14) | LOW |
| 5 | RV6 killed (commit is a compared A5 key) | CONFIRMED | d8 asserts `"commit" not in MANIFEST_EXCLUDED` plus the A5 value | - |
| 6 | D-10: flat_v2 refuses unless T2 stamp = pv2_1575 / 79d48f4b / ["MMLU_PRO"] / CK-CLOSE-v2 / the side export read now | CONFIRMED | RV11 (side-export check off) KILLED 11/12. Engine side: `V2EnginePool.activate` stamps `namespacesOf(loaded)` = the pool file's keys; pv2_1575's file has `MMLU_PRO: 0`, so the MMLU_PRO_LB member stamps ["MMLU_PRO"] (no false refusal). Both pool files pin side export sha256-lf 47e9048b... | - |
| 7 | ENGINE_POOL_SHA_LF = pv2_41's file 8f1ed122... (held-out), not pv2_1575's | CONFIRMED | selftest recomputes both LF shas from the committed files; 12/12 | - |
| 8 | D-11: g11 prints n/G (1.091) and names Σm²/Σm | CONFIRMED | fixture 6153/5642 = 1.0906 asserted; selftest 6/6 | - |
| 9 | G12 config = registration (B0 MMLU_PRO_LB, pv2_1575, 300 reps, 12 threads, m ≤ 15 vs 14, sliceDim 512, sepBar 0.0145) | CONFIRMED | .sitenull values equal B0/mmlu_pro_lb.toml (`embeddingSliceDim 512`, `proposalSeparationBar 0.0145`, `splitDropTopPcs 0`, `splitWhiten false`, mcs 55 = harness siteMcs); `siteNull` task forwards every -D/-P used; cert_resolution family rule (blob dbe9425d) matches g12's walk | - |
| 10 | G12 site rule = the harness's (childIds ≥ 2 and dasguptaDeltaNorm > 0) | PARTLY | code equal to SeparationNullBySizeTest L1707; **RV10 (`>= 2` -> `>= 1`) SURVIVED 7/7**: the fixture has no one-child node with Δ > 0 (D-15) | LOW |
| 11 | G12 "top family m" = the registration's family of depth-1 sites | PARTLY | if the ROOT is a site, TOP = {root}: my fixture prints `m = 1`, depths [0], and "reachable"; the 14 depth-1 sites fall in family `root`. That is a vacuous PASS of the support bar (D-12). The precedent multicorpus/site_null_mmlu_pro_lb_s42.csv has 0 depth-0 rows and 14 depth-1 rows (66 sites), so it is probably inert, but it is not checked | MEDIUM |
| 12 | G12 refuses owed pointer / stamp mismatch / pv2_41 member / existing outCsv / bad keys | CONFIRMED | RV12 (pointer-stamp equality off) KILLED 6/7; live `--dry-run` -> `[G12] REFUSED: P1: the pointer file ... is owed` | - |
| 13 | G12 heap line = "the harness's own rule" | PARTLY | g12 uses 7·D + 384; the harness guard uses 5.5·D + 384 (L1767). g12's estimate is conservative (larger), so it can only ask for more heap. It is descriptive: the harness's own `[SITENULL-HEAP]` line decides | LOW |
| 14 | g11 attenuation wording matches R-1 | REFUTED | g11 L191 still prints "OWED ... the registrar defines it before G11 is scored"; R-1 rules "NOT COMPUTED (no pre-data definition)", never defined after data (D-16) | LOW |

Selftests at a3d55e7: g10 12/12, g11 6/6, flat_v2 12/12, g12 7/7, g13 6/6, rp12_pairing 3/3, rp12_build_configs PASS,
`--check` OK (27 files). The builder's mutant claims were not re-run; my own mutants: 6, of which 4 were killed and 2
survived (RV8, RV10). Neither survivor is decisive.

## Conditions

- **F-1 (FLAT, after B0).** Covered in the verdict above.
- **G-1 (G12 first dry-run, after B0 and after `g10_compare.py --write-pointer`; zero calls; from the pinned worktree).** It
  must print, in order:
  1. `POOL pv2_1575de61bb20e977 (G12 site null, dry-run: counts only, NO statistic, nothing launched)`;
  2. `[G12] P1-P2 member B0/mmlu_pro_lb = snapshot <id>; stamp pool pv2_1575de61bb20e977, engine pool sha256(LF)
     79d48f4b36434a55, namespaces ['MMLU_PRO']: equal to the pointer entry`. The `<id>` must equal the pointer entry and
     B0's `seed_42` manifest;
  3. `[G12] P3 sites S (by depth: d1 ...); families F; TOP family m = M, depths [1]`. **depths must be exactly [1]** (D-12)
     and **M ≤ 15**. The expected value is M = 14 (every declared domain split at depth 1; precedent 14). Also printed:
     `P3 m = M <= 15 (declared MMLU-Pro domains 14): the top family is reachable at 300 reps`;
  4. `[G12] P4 heap: largest site n N, live replicates 12, peak X GB -> fits the 6g default` (or the named -DsiteNullHeap);
  5. no P5 refusal (outCsv absent);
  6. `[G12] COMMAND: .\gradlew.bat siteNull --console=plain --offline -PjvmThreads=12 -PnullReps=300 "-DsnapshotId=<id>"
     "-DsliceDim=512" "-DsepBar=0.0145" "-DdropTop=0" "-Dwhiten=false"
     "-DoutCsv=experiment_results/archv2/rp12/g12/site_null_B0_mmlu_pro_lb.csv"`. It carries no -DembeddingCacheFile (qwen3
     of record).
  - If depths ≠ [1], or M > 15, or M < 14: STOP. That goes to a registrar bracket before any launch (M > 15 is the registered
    UNDETERMINED-by-support; depths [0] is D-12).
- **G-2 (launch).** Rule 7 (W1-W5, one heavy process, never beside a construction or a pool reader). The harness log must
  show `[EMB-CACHE] ... embeddings_cache.db (absent -> default)`, the THREAD-CAP line with availableProcessors 12, the
  `[SITENULL-HEAP]` pass, the EmbedderReadGuard pass, and `[SEPBAR] proposalSeparationBar=0.0145`. It must print a site
  count equal to G-1's S.
- **G-3 (before G12 is read).** cert_resolution's identity check PASS with multi-parent sites 0, and its top-family m equal
  to G-1's M.

## Defects (each with its fix; none blocks the merge)

- **D-12 MEDIUM (G12, before the first dry-run is accepted).** g12 does not refuse when a depth-0 root is a site, so TOP
  collapses to m = 1. Fix: in `dry_run`, refuse (or print "UNDETERMINED: the registered top family is not the depth-1
  family") unless `sorted({depth of TOP members}) == [1]`, and add a root-site fixture. Until it lands, G-1 item 3 is the
  gate.
- **D-13 LOW (g10).** Add a selftest in which both manifests lack `commit` (kills RV8).
- **D-14 LOW (g10).** `toml_pair_diff`: reset `in_snaps` when the `unionSnapshots` line itself closes with `]`, or refuse any
  inline unionSnapshots. Add the inline-plus-models fixture.
- **D-15 LOW (g12).** Add a one-child node with Δ > 0 to `_graph` (kills RV10).
- **D-16 LOW (g11, before the G11 outcome).** L191 and its docstring and selftest must say "NOT COMPUTED (no pre-data
  definition; R-1, 390f9c6)".
- **D-9 LOW.** Remains open as registered.
- **Note (heap coefficient).** g12's 7·D is not the harness's 5.5·D. Rename it "conservative estimate (7·D; harness 5.5·D
  decides)", or align the two.

## Pins (a3d55e7; LF of record, CRLF = this Windows worktree's rendering)

| path | blob | sha256-lf16 | sha256-crlf16 |
|---|---|---|---|
| tools/analysis/g10_compare.py | 09ba5996a6b9 | 940d40624a444d37 | abc48211f3d6b9d9 |
| tools/analysis/g11_reader.py | 65e70236a8de | 93ec7d093e809c7b | e5ec1fb0c6dfb432 |
| tools/analysis/flat_v2.py | 827b66df7e1f | 160df7c18f872215 | 0ffa4b5472137720 |
| tools/analysis/g12_site_null.py | 56125af2d33d | d217b8c3e42810e5 | 30ed0cf43f5ea64b |
| experiment_configs/rp12/B0/g12_site_null.sitenull | 8aebf8757b5e | c85f08fcc85d4a95 | 5d231021278e9358 |

## Commands (reviewer's own)

```
git worktree add --detach .claude/worktrees/rv-rp12-et3 a3d55e7
git merge-base --is-ancestor 3002aec a3d55e7                                            # yes
git diff --name-only 3002aec..a3d55e7 | wc -l                                           # 5
git diff --name-only 3002aec..a3d55e7 | grep -c -E "^src/|gradle|application.yml|\.env|\.gitignore|report/|\.db$|^docs/"  # 0
comm -12 <(git diff --name-only 3002aec..a3d55e7|sort) <(git diff --name-only 3002aec..HEAD|sort) | wc -l               # 0
for s in g10_compare g11_reader flat_v2 g12_site_null rp12_build_configs g13_comparator rp12_pairing; do python tools/analysis/$s.py --selftest; done
python tools/analysis/g12_site_null.py --dry-run --snapshot-db NONEXISTENT.db            # REFUSED P1 (pointer owed)
python: g10.toml_pair_diff(B0/<f>, B0p/<f>) for the 7 committed pairs -> [] x7; graft tmpl with __SNAP_*__ filled per arm -> [];
  inline unionSnapshots + differing models entry -> [] (D-14)
python: g12.sites_and_families(_graph() with root dasguptaDeltaNorm 0.3) -> TOP m 1, depths [0] (D-12)
python: Counter(depth) of experiment_results/multicorpus/site_null_mmlu_pro_lb_s42.csv -> d1 14, d2 25, d3 22, d4 4, d5 1; d0 0
grep -n "namespacesOf\|fun activate" src/main/kotlin/taxonomy/dataset/V2EnginePool.kt; python json pv2_1575 namespaces -> MMLU_PRO: 0
sed -n 1685,1790p src/test/kotlin/taxonomy/SeparationNullBySizeTest.kt; grep -n 'register<Test>("siteNull")' -A45 build.gradle.kts
mutants RV8-RV13: python in-place replace (assert count == 1) -> --selftest -> restore (RV8 confirmed by hand: 12/12, rc 0);
  git status --porcelain | wc -l = 0 after each
git rev-parse a3d55e7:<p>; git show a3d55e7:<p> | sha256sum; sha256sum < <worktree p>
```
