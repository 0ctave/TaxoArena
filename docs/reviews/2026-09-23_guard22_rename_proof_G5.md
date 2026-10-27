# G5 addendum: GUARD-22-RENAME-PROOF, independent recomputation of C1 (adversarial-reviewer, 2026-09-23, zero calls)

Parent READY: `docs/reviews/READY_guard22_rename_proof.md` (55c4c10). Evidence: the run-operator's files in the session scratchpad
`C:\Users\octav\AppData\Local\Temp\claude\Z--FAC-TUBerlin-THESIS-TaxoArena\7c10e5cb-d16b-4a0e-864a-f3a6151d835b\scratchpad\g22_*`.
All reads were read-only. The reviewer ran no Gradle and no JVM.

VERDICT: **C1 HELD (CONFIRMED independently). P1-P4 HELD. C2 HELD.** The registrar may write the outcome, then G6, then the three on-pass brackets, then the merge, in that order.

## Per-claim table

| claim | status | command | got vs claimed |
|---|---|---|---|
| the script run is the READY's | CONFIRMED | `sha256sum g22_proof.sh` | e42f3e75a7e0a18c = e42f3e75a7e0a18c |
| C1 byte identity | CONFIRMED | `sha256sum g22_legA.csv g22_legB.csv`; `cmp`; python `open(..,'rb').read()` equality | both aec4b517829a376f84ea2f333a0bc07d8aaae39be8c05e5c05f0271d6ed9a665; cmp silent; 16869 = 16869 bytes, `a==b` True |
| the CSV is not trivially identical (for example, empty) | CONFIRMED | csv.DictReader on legA | 87 rows, 87 distinct site_null_p95 values, feasibility OK 86 / DEGENERATE 1, cert_site 10, cert_deflated 33, trunk 3; snapshot 20260917_161817 on 87/87; reps 24 on 87/87 |
| R2 exit | CONFIRMED | `.rc`; `BUILD SUCCESSFUL in 7m 5s` / `in 6m 46s` in the logs | 0 / 0 |
| R3 task executed | CONFIRMED | `grep -c -x '> Task :siteNull'` | 1 / 1; no FROM-CACHE/UP-TO-DATE on :siteNull |
| R4 heap | CONFIRMED | `grep -F '[SITENULL-HEAP]'`; `diff` of the two lines | both `sliceDim=512 largest site n=8133 live=24 -> peak live 5.00 GB; budget 0.90 * maxMemory(6.44 GB) = 5.80 GB`; identical; REFUSING 0 / 0 |
| R5 SEPBAR, reps=24, no sepBar | CONFIRMED | `grep -c -F` of the full line | 1 / 1 |
| R6 site count | CONFIRMED | `grep -c -F '87 accepted split sites, reps=24 per site per arm.'` | 1 / 1 |
| R7 not skipped | CONFIRMED | XML attributes | `tests="1" skipped="0" failures="0" errors="0"` on both. The one `SKIPPED` word in each log is `:checkKotlinGradlePluginConfigurationErrors SKIPPED`, a Gradle housekeeping task, not the arm |
| R8 CSV shape | CONFIRMED | wc / python | 88 lines, 87 rows at reps 24, on each leg; CSVs written 14:18:15 (A) and 14:25:27 (B), after each leg started (14:11:10 / 14:18:41) |
| R9 discriminator, from sources other than the operator's table | CONFIRMED | leg logs; class-file token count and mtime now | Leg A log: `> Task :compileTestKotlin UP-TO-DATE`, i.e. against HEAD classes that this reviewer counted before the run at 0 renamed tokens (`guardDim` 1, mtime 05:07:49). Leg B log: `> Task :compileTestKotlin` executed. The main `build/classes/.../SeparationNullBySizeTest.class` has mtime 14:18:45, inside leg B and before its :siteNull started, and holds **14** renamed tokens now. The worktree's G2 classes hold 14 too. `.disc` 0 / 14 agrees |
| R13 / P4 restore | CONFIRMED | `git hash-object F`; `git status --porcelain F \| wc -l`; `git rev-parse HEAD:F`; `g22_phaseB.txt` RESTORE line | c0d89121 / 0 / c0d89121 now; RESTORE line shows the index blob c0d89121 |
| W1 at 3 points | CONFIRMED | `grep -c '^FREE'` / `HELD` in g22_probe{1,2,3}*.txt | 7/0, 7/0, 7/0 |
| W5 HEAD:src fixed | CONFIRMED | P0 lines of phases A and B; `git rev-parse HEAD:src` now | 910a5719 at all points; no WINDOW VIOLATION line |
| "HEAD moved only through docs/ commits" | PARTLY | `git log --name-only ea09f3bd..HEAD` | c33b404 (14:17:33, during leg A) touched `tools/analysis/results_index.py`; 70203ea (14:27:44, after the restore) touched two `tools/analysis/bfcl_*.py`. Neither touches src/ or build files, and the legs do not read tools/, so there is no effect. The claim as worded is wrong, LOW |
| P3 wall time | HELD | `.wall` | 426 s (7.1 min) / 407 s (6.8 min), both within [4, 12]; asymmetry 19 s = 4.7% of the shorter, under 40% |

## Ruling on the admitted selftest overlap (PID 41880)

The process was `tools/analysis/cert_under_filter.py --selftest`, run from the `cert-under-filter` worktree (the file is not in the main checkout). Its docstring (L15) says the selftest runs on "synthetic fixtures under tempfile.mkdtemp(); opens NO" DB of record. Its `sqlite3.connect` is wrapped and logged (L182-L200), and its selftest DBs are `tmp/eval_syn.db` and `:memory:` (L1413-L1420). W1 printed FREE on all 7 files at 14:25:38 while it ran.

It overlapped about the last 14 s of leg B (it started 14:25:13; the CSV was written 14:25:27) and none of leg A.

It affects NOTHING beyond P3:
- C1 is a byte comparison. Each replicate's seed is a function of (seedBase, siteId, rep) only, and `awaitAll` fixes the order. The two CSVs are in fact identical, so there is no difference that could be attributed to it.
- R2-R9 are counts, and no timing enters them.
- P3 holds even with the overlap charged to leg B.

## Residuals (not blocking)

- LOW: main `build/classes` still holds leg B's renamed compilation (14 tokens, mtime 14:18:45) until the operator's recompile. This is not a stale-class hazard: the source hash has changed back, so the next compile of the test source set recompiles.
- LOW: in W2, probes 1 and 3 list three `bash.exe` wrappers whose command lines are truncated in the probe file, so their identity is not shown. Most likely the pattern matched the probing shell's own command line, which contains the literal pattern. W1 (FREE 7/7 at every point) is the deciding test under the READY's ruling, so this is non-blocking. For the next window, print `CommandLine` untruncated (`Format-List` or `-Width 4000`).
- LOW: the coordinator's "only docs/ commits" wording (row above).
- D8 stands as written. With no A/A control it restricts only how a FAIL may be worded; this is a PASS.
- D1 (87 sites, not 97) and D9 (`"ready"` null) remain for the registrar under G6.
