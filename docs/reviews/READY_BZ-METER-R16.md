# Delta READY review: BZ-METER [R16] (D1 widened tau grid), 2026-10-11

Reviewer: adversarial-reviewer. Scope: `git diff e6d420d..72a7e66` in benchzoom (6a2455d build + 72a7e66 registration),
plus regression of the prior decisive mutants. Authority: author_decisions/2026-10-09.md D-2026-10-11-9; the WIDEN
ruling is the main session's (technical), not the author's. Prior reviews: READY_BZ-METER-BUILD.md (e3d24fbd, C1-C4,
D1-D6), POSTRUN_BZ-METER.md (6c16ff8a, P1-P4). What those reviews CONFIRMED on untouched code is not re-derived.
Zero LLM calls. Zero vault response reads by the reviewer (the dry-run reports 0; sha256 only on files).

## Verdict: READY (with conditions C1'-C6). C1 of the build review (D1) is CLOSED by [R16].

All five acceptance checks hold: the grid in code equals the bracket, REG_BLOB is the LF blob of the file at HEAD,
the D2/D3 tests kill M6/M3 without the manifest, the Support re-cut reproduces to the digit, and the real dry-run
reads 0 vault responses and writes nothing. New finding F1 (MEDIUM, undisclosed): with the widened grid, the
runner's own `--calibrate synthetic` **null** fixture (category planted, cat_sd .25) flips L1|L0 from SUPPORTED
(old grid) to INCONCLUSIVE. The builder strengthened the *test* fixture for the same reason but not the runner's
calibration fixture, and reported only the planted-L2 miss (which is grid-independent: identical words on both grids).
No real-data predicted word changes. F1 needs a written decision before `--calibrate` runs (C5), because calibration
outputs are write-once in the default `--out`.

## Per-claim table (deciding claims)

| # | Claim | Mine | Result | Sev |
|---|---|---|---|---|
| 1 | `TAU_GRID` = {0,.0025,.005,.01,.02,.04,.08,.16,.32} in code = Section 2 [R16] = Section 6 [R16] = graph | meter.py L66; reg L88-89, L328-331; graph L425 and Docs-vs-code 24: identical | CONFIRMED | - |
| 2 | Only `TAU_GRID` changed under src/ | diff of meter.py: docstring [R16], 2 comment lines, the grid; no other line. grid used only at meter.py L283-290 (S-TAU), L460 meta | CONFIRMED | - |
| 3 | REG_BLOB 0a2806f5... (LF; same `--no-filters`) | `hash-object` = `--no-filters` = `rev-parse HEAD:` = 0a2806f5c355f535ee7d697158fdb1621fa817b8; file has 0 CR, so the CRLF rendering does not differ; dry-run prints "OK" | CONFIRMED | - |
| 4 | Registration insertion only | `diff ... \| grep '^-'` = 3 lines; each is a prefix of its replacement line (re-wrap only) | CONFIRMED | - |
| 5 | D2 test kills M6 | M6 (`score_lines` groups -> arange): 1 failed (test_twin_clusters_reach_the_outcome), 36 passed | CONFIRMED | - |
| 6 | D3 test kills M3 (no longer only by manifest) | M3 (`L3k\|C` reader fk -> fl in meter.DECIDING), test_meter.py alone: killed by test_deciding_reader_map | CONFIRMED | - |
| 7 | Support re-cut: MATH L3k\|C +0.435 SE .069; L3t\|L2 +0.019; L1 +1.040; MMLU-Pro L3k\|C +0.082 | +0.4354 / .0688; +0.019; +1.040; +0.082; all 32 table rows (g, SE, DEFF, n_eff, vault SE = SE x sqrt(n_work/n_vault), MDE80 = 3.84 x vault SE) reproduce to the printed digit | CONFIRMED | - |
| 8 | P4/P5/P6 ranges = point +- 2.5 vault SE | P4 MATH -0.018..0.056; P5 MATH 0.224..0.646, MMLU-Pro -0.026..0.190; P6 8.94-13.51, 2.16-3.95, 1.00-2.19, 0.67-1.97, -0.05-0.18; "g + 2 SE = 0.049", "3 SE = 0.129": reproduce; runner PREDICTIONS carry them | CONFIRMED | - |
| 9 | Readers the old top bound: MATH L1 4/5, L2 2/5, L2a 5/5, fk/fk0/fk1 5/5, L2c1 1/5; MMLU-Pro L2 1/5; max selected .16 | fold counts reproduce exactly; max selected .16 (MATH L2a); max moment .136; top .32 does not bind | CONFIRMED | - |
| 10 | Old SE of MATH L3k\|C .042 | [R14] JSON: .0422 (g .3745); z on vault SE 7.2 -> 5.2 | CONFIRMED | - |
| 11 | "one MMLU-Pro moment tau (fk1) differs at the 7th significant digit" | fk1 differs in 3 of 5 folds; fold 0 0.0060662026 vs 0.0060661843 (rel 3e-6, the 5th significant digit). Moment path does not read the grid; contrast rows equal to 3 dp (max abs diff 1e-4 in an n_eff) | PARTLY | LOW |
| 12 | Dry-run 0 vault reads, nothing written; C2 counts 1960/1960, 4625/4654 | rc 0; "DRY-RUN OK: 0 vault response reads; nothing written"; C2 lines as claimed; 4 vault/atlas files pass `sha256sum -c` after; files newer than the marker: 0 under E:/benchzoom_demo, 0 in the repo; `meter_v1` absent before and after; tree clean | CONFIRMED | - |
| 13 | Tests 445 passed 4 deselected; ruff; mypy 15 files; manifest OK | identical | CONFIRMED | - |
| 14 | D4: planted L2 not recovered by `--calibrate synthetic`, "already true under the old grid" | planted words identical on both grids (L2\|L1 g +0.044 SE .20 NOT SUPPORTED). **But the null run changes**: L1\|L0 SUPPORTED (g 2.60 SE .70, tau .04) -> INCONCLUSIVE (g 2.55 SE .91, tau .08); L3t\|L2, L3k\|C NOT SUPPORTED -> DEGENERATE | PARTLY (incomplete) | MEDIUM |
| 15 | Commit hygiene | `--name-only \| wc -l`: 6a2455d 4 files, 72a7e66 3 files; no config/.env/.gitignore | CONFIRMED | - |

Mutants (own, deciding paths; sandbox copy of HEAD; test_meter.py only; baseline 37 passed):
- M6: `score_lines` passes `np.arange(len(Y))` instead of `d.groups`. Killed. Decisive (C2 SE).
- M3: the DECIDING reader of L3k|C changed from `fk` to `fl`. Killed. Decisive (DEGENERATE word).
- R1: `contrast_stats` ignores `groups` (passes `paired_delta(pi, arange)`). Killed by test_twin_clusters. Decisive (SE).

## Defects

- F1 MEDIUM (claim 14). The widened grid lowers the power of the runner's synthetic calibration: null-fixture
  L1|L0 (category effect planted) goes from SUPPORTED to INCONCLUSIVE, because SE rises 30% with tau .08. Together
  with the grid-independent planted-L2 miss, 2 of the 4 planted level effects across the two fixtures are now
  missed (old grid: 1 of 4). The real-data deciding lines are far from this regime (WORK z: MATH L1 8.6, L3k|C 5.2 on
  vault SE), so no predicted word changes. Fix (registrar, before C4 starts): either (a) one bracket stating the
  expected [R16] calibration words, including null L1|L0 INCONCLUSIVE and planted L2|L1 NOT SUPPORTED, as fixture
  power and not a stop (new REG_BLOB, delta review of that line), or (b) strengthen `--calibrate synthetic`'s fixture
  the way `PLANTED` was strengthened in the tests (meter_test.py L798-799; a new commit and a delta review).
- F2 LOW (claim 11). Fix the [R16] wording ("fk1 in 3 of 5 folds, relative 3e-6") at the next bracket. Cosmetic.
- D4 (build review) stays open: the calibration words are still not a gate. F1 makes that matter for the operator.
- D5 is closed by Section 6 [R16] ("underpowered at delta_min", MDE80 .166). D6 is partly done (cosmetic).

## Conditions (replace C1-C4 of READY_BZ-METER-BUILD)

- C1' CLOSED: D1 is settled by [R16], and Section 6 names the binding readers.
- C2: after the run, each `outcome.json` must show n_clusters 1960 (MATH) and 4625 (MMLU-Pro). The D2 test now pins
  this path and the dry-run prints it. Any other count makes the run INVALID.
- C3: use the default `--out` E:/benchzoom_demo/meter_v1 only (absent now).
- C4: run from a clean tree at 72a7e66, or at the commit that settles C5 if it is (b) or a re-pinned (a), with no
  edits between steps, in this order:
```
cd Z:/FAC/TUBerlin/benchzoom; export PYTHONPATH=src; git status --porcelain | wc -l          # 0
.venv/Scripts/python examples/meter_test.py --dry-run          # "registration ... OK", C2 1960/1960 and 4625/4654, "DRY-RUN OK: 0 vault response reads"
.venv/Scripts/python examples/meter_test.py --calibrate synthetic   # read the words against C5
.venv/Scripts/python examples/meter_test.py --calibrate work        # harness PASSED
(cd E:/benchzoom_demo/research_probes && sha256sum -c vault/SHA256SUMS.txt) > E:/benchzoom_demo/pre_vault_sums.txt   # 2 x OK, record
ls -A E:/benchzoom_demo/meter_v1 | grep -v '^calibration' | wc -l   # 0: no outcome/meta before the read, record
.venv/Scripts/python examples/meter_test.py --vault            # once
sha256sum -c E:/benchzoom_demo/meter_v1/SHA256SUMS; backup + SHA256SUMS per the bulky-outputs rule
```
- C5 (from F1; blocks `--calibrate synthetic`): the registrar picks F1 (a) or (b) in writing, or records that the
  calibration words are informational and lists the expected words above. The operator must not treat null L1|L0
  INCONCLUSIVE or planted L2|L1 NOT SUPPORTED as an unregistered stop, or as a pass.
- C6: the post-run review re-measures DEFF from the vault cluster sizes (29 twin pairs on MMLU-Pro) beside each
  deciding statistic. The Support vault-SE factor uses n_scored, not clusters (sqrt(4654/4625) = 1.003, immaterial).

## Commands

```
git -C benchzoom diff e6d420d..HEAD -- src examples docs tests; ... -- docs/meter_registration.md | grep '^-'      # 1,2,4
git hash-object / --no-filters / rev-parse HEAD:docs/meter_registration.md; grep -c $'\r'                      # 3
PYTHONPATH=src .venv/Scripts/python -m pytest -q; ruff check .; mypy src; examples/update_graph_manifest.py --check   # 13
scratch run.sh <id> <file> <old> <new> (copy of git archive HEAD; BENCHZOOM_METER_RUNNER on the copy)          # 5,6,mutants
inline python over support_meter_stau_r16/support_meter_stau.json (sha256sum -c OK) and support_meter_stau/ ([R14]):
  g, se, deff, n_eff, se*vault_se_factor, x3.84, g+-2.5 vault SE, Counter of tau2_per_fold, moment diffs          # 7-11
sha256sum vault/*.json + 2 atlases > pre.sha; touch marker; meter_test.py --dry-run; sha256sum -c pre.sha;
  find E:/benchzoom_demo -newer marker -type f | wc -l (0); find repo -newer marker (0); ls meter_v1 (absent)    # 12
meter_test.py --calibrate synthetic --out <scratch> on the HEAD copy and on a copy with the [R1] grid; diff words # 14
git show --name-only --format= 6a2455d | wc -l (4); 72a7e66 (3)                                                  # 15
```
Evidence: `E:/TaxoArena_tmp/bzmeter_review_r16/` (run.sh, mutant outputs, dryrun.txt, pre.sha, 4 calibration outcome.txt).
