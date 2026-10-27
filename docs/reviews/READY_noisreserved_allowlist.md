# READY review: NOISRESERVED-TEST-ALLOWLIST (adversarial-reviewer, 2026-09-25, zero calls)

## VERDICT: READY (MERGEABLE by path; no merge condition; F3 is a pre-existing gap, DISCLOSED, recommended as its own queue item)

Object: branch small-fixes, commit ae1b2438533a87f53eedbb433171bc4c40ddc47d, one file (`git diff ae1b243~1 ae1b243 --name-only | wc -l` = 1):
`src/test/kotlin/taxonomy/dataset/NoIsReservedInSourceTest.kt`
- before: blob:ed65aa27bbd74b4a23194b63dc02c6ebf9751c8c (= main HEAD 52474d6's blob, `git rev-parse main:<path>`)
- after:  blob:b765bd1bb3631f102a5b64dc855af987c4c93ac4 / sha256-lf16:a558ca073900efb2 (LF, rendering of record) / sha256-crlf16:c4f6edc35c5b7ef4 (the autocrlf working-tree rendering)
Record: docs/judge_v2_program.md L18093 ("KNOWN PRE-EXISTING RED ON main"); F5 freeze LIFTED (same line's bracket).

## MERGE PROCEDURE (by path, the one file, blob b765bd1b)
1. Rule 7: no foreign java / python process (PID 37772 waived), no construction.
2. On main: `git rev-parse HEAD:src/test/kotlin/taxonomy/dataset/NoIsReservedInSourceTest.kt` must print ed65aa27... (base unchanged; no 3-way needed). If it differs, STOP: re-review.
3. `git checkout ae1b243 -- src/test/kotlin/taxonomy/dataset/NoIsReservedInSourceTest.kt` (branch tip 8fe1802 carries the same blob: `git diff ae1b243 8fe1802 --name-only | grep -c NoIsReserved` = 0).
4. `git hash-object src/test/kotlin/taxonomy/dataset/NoIsReservedInSourceTest.kt` must print b765bd1bb3631f102a5b64dc855af987c4c93ac4.
5. `git commit -m "..." -- src/test/kotlin/taxonomy/dataset/NoIsReservedInSourceTest.kt` (pathspec commit; shared index), then `git merge-base --is-ancestor 52474d6 HEAD`.
6. Post-merge check on main: `.\gradlew.bat cleanTest test --offline --no-build-cache --tests taxonomy.dataset.NoIsReservedInSourceTest` -> 2 tests / 0 failures. It MUST be cleanTest + --no-build-cache (F3): a plain `test` can report UP-TO-DATE without scanning.
7. Merge ordering: any later change to data_v2/common.py, gates.py or ingest.py that edits one of the 6 allowlisted texts turns this test red through the stale-entry assertion, by design; that change carries its allowlist update by record.

## Per-claim table

| # | claim | result | command / evidence | got vs claimed | sev |
|---|---|---|---|---|---|
| 1 | exactly 7 hits on main, at common.py L67, gates.py L867 L932, ingest.py L104 L141 L160 L168 | CONFIRMED | python replay of the test's scan rule (scratchpad rv/replay.py) over main's WORKING TREE (tracked + untracked, as the test walks it) and over the small-fixes worktree | TOTAL 7 / 7, same lines, both trees | - |
| 1b | data_v2 files identical main vs branch | CONFIRMED | `git rev-parse HEAD:<f>` vs `ae1b243:<f>`: common 462ffef3, gates 28876ea9, ingest fd76b439 each equal; `git diff ae1b243 HEAD --name-only -- tools/analysis/data_v2 \| wc -l` = 0 | 0 differing | - |
| 2 | common.py L67 is a non-reader | CONFIRMED | L67-L71 read in full: a comment block (starts `#`) documenting the retirement and its two locks; skipped by nothing only because L67 lacks "legacy" and the "documented" words | comment | - |
| 3 | gates.py L867, L932 are selftest fixture DDL | CONFIRMED | L860-L867 `_fixture(root)` "Two tiny source DBs ... written as NEW files in a temporary data root" via `ro.create_new`; L932 inside the same function's multicorpus fixture `executescript` | fixture DDL, no DB of record | - |
| 4 | ingest.py L104 / L141 read the flag only to write retired_legacy_flag | CONFIRMED | L101-L107, L136-L147: the column lands in the dict key `legacy_is_reserved`; L344-L349: `INSERT INTO response VALUES` (15 columns, no flag; DDL L202-L207 has no flag column) then `INSERT INTO retired_legacy_flag VALUES (?,?)` | only sink = retired_legacy_flag | - |
| 5 | ingest.py L160 / L168 are manifest lines naming the pointer table as NOT read | CONFIRMED | L155-L174 `SPECS[...]["excluded_tables"]`; `tables_read` (L158, L167) does not name active_reserved_pool | manifest, non-reader | - |
| 6 | no reader of the retired table / column anywhere else | CONFIRMED (by count) | `git grep -n "retired_legacy_flag\|legacy_is_reserved\|guard_retired\|RETIRED_NAMES" HEAD -- tools src scripts`: 20 lines, all in data_v2 common/gates/ingest/split/views; the only reads of the table are gates.py selftest checks; split.py L139 and gates.py L147 call guard_retired | 0 readers feeding a view or verdict | - |
| 7 | "guard_retired keeps it out of every view" | PARTLY | common.py L75-L80: guard_retired only refuses a `response` table carrying a column in RETIRED_NAMES (`retired_legacy_flag`, `legacy_is_reserved`); it does not inspect views, other tables, or a bare `is_reserved` column. "Out of every view" is carried by guard_retired PLUS gates.py selftest (5) L1122-L1146 (response tables of the corpus / gv / ev DBs carry no retired column; the retired table exists only in the corpus DB; split.py and views.py never name RETIRED_NAMES; the guard REFUSES a probe) | substance holds, attribution overstated | LOW (F1) |
| 8 | allowlist is line-level: exact trimmed text + exact per-file count, no file / dir / regex exemption | CONFIRMED with qualifier | diff read in full: `allowlistedLines: Map<Pair<path, trimmed line>, Int>`, 6 distinct keys, counts 1,1,1,2,1,1 = 7; matching by `Pair(it.rel, it.text)` equality (text = `line.trim()`, untruncated); `allowlistedFiles` unchanged (5 entries); no regex added. Qualifier: keys are TEXT, not line numbers (F2) | 7 / 7 | - |
| 9 | an extra copy of an allowed line fails | CONFIRMED | mutant M5 (third copy of the count-2 ingest line, new function in ingest.py) under `cleanTest test --offline --no-build-cache --tests ...NoIsReservedInSourceTest` | 2 tests / 1 failure, message lists ingest.py:104, :141, :152 | - |
| 10 | a new hit still fails | CONFIRMED | M1 (MY mutant: new reader `SELECT question_id, is_reserved FROM eval_results` in data_v2/gates.py): FAIL naming gates.py:861 only. M2 (allowed ingest manifest text copied into data_v2/common.py, a different file): FAIL naming common.py:72 only. M6 (builder's a: tools/analysis/zz_mutant_reader.py): FAIL naming that file only. M7 (new src/main/kotlin/taxonomy/ZzMut.kt): FAIL naming it only | 4 / 4 killed | - |
| 11 | stale-entry assertion fires | CONFIRMED | M4 (common.py L67 edited to drop the token): FAIL "allowlisted lines whose count no longer matches ... common.py: expected 1, found 0" | killed | - |
| 12 | whitespace / indentation move of an allowed line | CONFIRMED PASS (acceptable) | M3 (gates.py L867 re-indented and moved down one line): 2 / 0 | passes, as intended by trimmed-text keys | - |
| 13 | old test red on exactly the 7 lines | CONFIRMED | blob ed65aa27 restored into the throwaway tree, same command | 2 / 1, 7 hit lines, the 7 recorded | - |
| 14 | new test green | CONFIRMED | same command at ae1b243 | 2 / 0 | - |
| 15 | full suite 451, 2 known worktree failures | CONFIRMED | `cleanTest test --offline --no-build-cache` in a throwaway detached worktree at ae1b243; XML totals | 451 tests, 2 failures: MrlRoutingTest.testMrlConfigDefaults, TraceEnvelopeUnwrapTest "no model has a wholly blank trace column" | - |
| 16 | main's DBs unchanged | CONFIRMED | `find . -maxdepth 1 -name "*.db*" -printf "%p %s %T@"` before / after all runs, `diff` empty | 33 of 33 entries identical (size, mtime) | - |
| 17 | caching gap (plain test serves mutant a) | CONFIRMED, PRE-EXISTING; mechanism restated | build.gradle.kts L28-L31, L47-L77: the `test` task declares no input for tools/**, scripts/**, report/Figures/**; plain `gradlew test --tests ...` then M6 applied then plain again: `> Task :test UP-TO-DATE`, BUILD SUCCESSFUL, 9 up-to-date. It is Gradle's UP-TO-DATE check, not only the build cache; ae1b243 does not touch build.gradle.kts (1 file changed) | gap exists before and after this change | MEDIUM (F3, pre-existing) |
| 18 | scope: scan rule, directories, second test unchanged | CONFIRMED | diff hunks: `tokens` untouched, `allowlistedFiles` untouched, `isComment` untouched, `scan` filter logic byte-unchanged (only return type String -> Hit, text no longer truncated before matching; printing still `take(120)`), the 8 `scan(...)` calls untouched, second @Test untouched | - | - |

## Defects

- F1 LOW (wording, test KDoc L29-L30 and record L18093): "common.guard_retired keeps it out of every v2 view" overstates guard_retired, which checks only the `response` table's columns against RETIRED_NAMES. The substance holds through the pair guard_retired + gates.py --selftest (5). Fix (optional, not a merge condition): a dated bracket on L18093 naming both locks; the KDoc may be amended in a later test-only commit.
- F2 LOW (inherent to text keys; accepted): the allowlist pins text and count per file, not line numbers. A line moved or re-indented passes (M3; desirable). A SWAP passes: delete one of the two ingest.py SELECT-tail lines and add identical text in a new reader in ingest.py; and the key sees only the SELECT tail, not its head line (L103 / L140, no token). The protection there is gates.py selftest (5) and the response DDL, not this test. Disclose; no fix.
- F3 MEDIUM, PRE-EXISTING (not a defect of this change): the Gradle `test` task has no declared input over the scanned non-classpath trees (tools/**, scripts/**, report/Figures/**), so after a python-only edit `gradlew test` reports `:test UP-TO-DATE` and the scan never runs. RECOMMENDATION: DISCLOSE in this READY, do NOT make it a merge condition; register a separate queue item (build.gradle.kts, e.g. `inputs.files(fileTree("tools") { include("**/*.py", "**/*.ps1") }, fileTree("scripts") { include("**/*.py") }, fileTree("report/Figures") { include("**/*.py") }).withPathSensitivity(PathSensitivity.RELATIVE)` on the `test` task) with its own review: it changes the up-to-date behaviour of all 451 tests and is outside a test-only change. Until then every gate that relies on this test runs `cleanTest test --no-build-cache` (or `--rerun-tasks`). Note the red on main since d98b247 could have been masked by the same mechanism.
- F4 LOW, PRE-EXISTING (out of scope): the scan skips every line containing "legacy", so a reader of `legacy_is_reserved` / `retired_legacy_flag` is invisible to this test by construction (it is covered by gates.py selftest (5) for split.py and views.py only). Noted; no fix here.
- F5 INFO: on an over-count (M5) the failure lists every copy of the key, not the new one; adequate.

## Hygiene
- Rule 7: before each Gradle run only PID 37772 (waived) plus my own Gradle / Kotlin daemons (started 20:35:57 / 20:36:06 by my first run); daemons stopped after the runs.
- All Gradle runs in a throwaway detached worktree at ae1b243 (removed and pruned afterwards); the small-fixes worktree untouched (`git status --porcelain | wc -l` = 0, tip 8fe1802).
- Mutant script and replay: scratchpad rv/mut.py, rv/replay.py; logs rv/M1.log ... M7.log, old.log, base.log, cacheA.log, cacheB.log, full.log.
