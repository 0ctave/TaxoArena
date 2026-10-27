# READY REVIEW — TOPIC-PARTITION-20NG-T1B-NULL addendum readout

adversarial-reviewer, 2026-09-23. Branch `tp20-t1b-null-readout` @ `e97bdfb`, `tools/analysis/topic_partition_t1b_null.py` (796 lines; LF sha16 79b3338d31df6593, blob 956c6d02; CRLF rendering 4b917e1590728d61). Zero calls. The T1b CSV was not read, no real DB was opened, and neither `--dry-run` nor `--run` was executed. [Not written to docs/ by the reviewer: docs/ was dirty (a registrar's edit), so the text was handed back and is committed by the coordinator by path.]

**VERDICT: READY-WITH-CONDITIONS.** The conditions are operational; no code change is required. All defects are LOW.

## Per-claim table

| # | claim | result | evidence | got vs claimed |
|---|---|---|---|---|
| 1 | File sha | CONFIRMED | `git hash-object` → blob 956c6d02; `sha256sum` → 79b3338d31df6593…; `file`: ASCII, no CRLF | LF 79b3338d31df6593 = claimed. The CRLF value 4b917e1590728d61 matches what the selftest prints. One file, 796 lines; worktree clean. |
| 2 | Selftest is safe (sqlite guard, no real DB, no writes outside mkdtemp) | CONFIRMED by execution | `audit_selftest.py`: `--selftest` run under `sys.addaudithook`, logging every open, sqlite3.connect, socket and subprocess; PYTHONDONTWRITEBYTECODE=1 | RC 0; "SELFTEST OK: 78 checks (pinned 78); 39 of 39". Writes outside tempdir: **0** (143 inside). sqlite3.connect to a non-fixture path: **0**. Sockets 0, subprocesses 0. The only non-temp read is a .kt source read at import by a transitive module. Worktree still clean; no __pycache__. |
| 3 | The guard refuses a non-fixture DB | CONFIRMED | mutant M0 points the fixture snap_db at a scratch file outside the mkdtemp roots | KILLED: "AssertionError: selftest opened a non-fixture DB" |
| 4 | Four target strings verbatim, whole-line, once each; L128 unchanged; blob | CONFIRMED | AST-extract TARGETS / NON_TARGET vs topic_partition_outcome.txt; `git hash-object` + `git ls-files -s`; `wc -l`; `grep -c $'\r'` | L226 / L238 / L120 / L220 / L128 each equal and each occurring once. Blob 90632b36bed0… equals the index. 243 lines, 0 CR. All four targets appear verbatim in ruling (5). POINTER_4 equals ruling (3)'s text once line wrapping is removed. |
| 5 | A1's jsonl leg can pass on the REAL input (the guard is not one that can never pass) | CONFIRMED | last line of ng_af_bareq512_s42/seed_42/dag_snapshots.jsonl, read as text | iteration 15; 197 nodes; 97 sites; 100 leaves (isLeaf equals the childIds rule); 0 one-child nodes; leaf dims [512]; root [n00000001]; depth-1 sites [n00000004, n00000005]. All jsonl-side clauses pass. |
| 6 | The .out ordering guard can pass on the REAL input | CONFIRMED | Kotlin prints [SITENULL-HEAP] at SeparationNullBySizeTest.kt L1741 and [SEPBAR] at L1769; live .out grepped | Last heap line L72 (maxMemory 15.03 GB = 14 GiB); last SEPBAR L76 (bar 0.0145, sliceDim 512). The earlier run (L1-L42) has no heap line. No OutOfMemoryError anywhere. |
| 7 | CSV schema and cert-flag parsing match the writer | CONFIRMED statically | Kotlin writer L1925-L1937 | Columns snapshot_id, node_id, depth, n, observed_sep, site_null_p95, cert_site_p95, reps. The flag is a Kotlin Boolean written "true"/"false"; reps=$r → "300"; ids are quoted, which DictReader handles. |
| 8 | snapshots.db leg | UNDETERMINED by execution (not opened, per instruction); CONFIRMED by precedent | topic_partition.py L322-L324 ran the same equality for this arm when the outcome of record was written; snapshots.db mtime 04:34 is unchanged since; snapshots.db-wal is 0 B | — |
| 9 | C2 leakage impossible on any branch | CONFIRMED, with one LOW (D5) | grep of production code L1-L515 for stratif / permut / OLS / HC1 / NMI / 101 / 85 / ng_af_s42 | Hits only in the docstring, in the TARGETS constant (compared, never printed) and in the never_touch path list. No code reads T1's CSV. Mutant M21 (append "T1 16/101" to A4) KILLED. |
| 10 | No T1/T1b pooling | CONFIRMED | T1's CSV and .out paths appear only in `never_touch()` | — |
| 11 | Write-once | CONFIRMED | selftest scenarios; mutants M14 (x→w), M19 (exists-check off), M20 (both off) | All KILLED. A second run is refused; tampering is refused; an outcome path equal to the outcome of record is refused and that file stays at 243 lines. |
| 12 | The 39-branch set covers A1-A4, AF1, AF2, AP1-AP5 | CONFIRMED | REQUIRED_BRANCHES L103-L110 | Every criterion, falsifier and prediction has every registered branch (AP5 correctly has no UNDETERMINED). BRANCHES == REQUIRED_BRANCHES is asserted. |
| 13 | "26 mutants, two equivalent survivors" | PARTLY | scratch mutate.py / mutate2.py, 23 mutants | M1 (A4 `<`→`<=`) and M2 (AP2 `<=`→`<`) survive and are equivalent: 0.158×97 = 15.33, 0.08×97 = 7.76 and 0.22×97 = 21.34 are not integers, so no k/97 sits on a bound. M11 and M12 survive and are equivalent under the guard. **Two survivors are NOT equivalent: M3 (AP1 `<=140`→`<140`) and M18 (root-id clause dropped).** See D1. |
| 14 | Numpy hygiene | CONFIRMED | `grep "is True\|is False"` | 7 hits, all in selftest asserts on values already passed through tribool()/bool(). None in production code. Every verdict goes through tribool; the numpy cases are asserted (L727-L731). |
| 15 | Support section arithmetic (ruling (1)) | CONFIRMED | by hand | SE sqrt(0.144×0.856/97) = 0.0356 ✓. MDE 2.80×sqrt(0.1275×(1/97+1/101)) = 2.80×0.0508 = 0.142 ✓. No DEFF claimed; A3 and A4 DESCRIPTIVE-ONLY; A1 and A2 deterministic flag reads. Non-vacuous. |
| 16 | Wilson rendering | CONFIRMED | Wilson by hand for k=12, n=97 | [0.0722, 0.2039] = the builder's "0.124 [0.072, 0.204]" |

## Rulings on the six deviations

1. **Last line of the jsonl: ACCEPT.** The file has 15 lines, iterations 1..15 in strict order. Its top-level keys are only ['iteration', 'nodes'], so it holds no snapshot id to select by. Its mtime (04:34) matches the snapshot stamp 043423. The last line is the final tree; consensus_tree.last_snapshot and topic_partition use the same rule. Ruling (6) asks for "the snapshot whose id equals …", which the file cannot express. The mandatory leaf-set equality plus the orphan check against the CSV's pinned snapshot_id form a double binding and conform to the ruling. An earlier build appended to the file would change the last line and fail the leaf-set check. That is a refusal, not a mis-read.
2. **Extra provenance checks: ACCEPT.** On the real inputs none refuses a correct run (rows 5-6). The heap-before-SEPBAR order is Kotlin's own (L1741 < L1769). sliceDim is [512]. There are no duplicate ids by construction. The root and depth-1 sites are exactly n00000001 / n00000004 / n00000005. The CSV and DB legs are not executed on real inputs here; the dry-run proves them (condition C2).
3. **--record-a1-failed: ADMISSIBLE WITH CONDITIONS.** It changes no score and cannot turn FAILED into HELD (mutant M15 killed). It protects the write-once file from a mistaken or guard-bug A1 failure. The risk is selective non-recording: CONTEXT §4 rule 2 makes UNDETERMINED a registered outcome, and AF2 (programme L11563) is a registered outcome. Conditions C3 and C4 below.
4. **AP1 wall time: ACCEPT.** The registered 90-140 min (point 108) comes from T1's null at "53.3 min" (programme L11493). That figure is Gradle's own `BUILD SUCCESSFUL in 53m 18s` (sitenull_ng_af_s42.out L188), which also includes daemon start-up, so the bound and the reading use the same measure. Start-up is negligible here: every task was UP-TO-DATE and only "Starting a Gradle Daemon" ran. The reading is 2h 14m 29s = 134.5 min, so AP1 will read HELD, 5.5 min inside the bound; start-up time could never have made it FAILED. (LOW D2: AP1 does not check that the heap was 14 g; the line is printed but not tested.)
5. **Informational prints: ACCEPT.** The blob is labelled informational and the line rule decides. The observed ≥ p95 comparison is printed beside the flag, and the CSV flag decides, exactly as Kotlin computes it (`certSite = plainUsable && obs >= ps[1]`, L1873). A disagreement between the two would be visible but would not decide anything.
6. **A4 rendering: ACCEPT.** "[lo, hi; Wilson, nominal]" fills in ruling (4)'s "<share> [Wilson, nominal]" placeholder, so it is not a deviation. The "A4 (…; DESCRIPTIVE-ONLY): HELD/FAILED --" prefix is the registered scoring word, and the point estimate decides (`share < 0.158`). The sentence never prints 16, 101, 85 or "16/101" as T1 figures.

## Defects (all LOW; none blocks)

- **D1 LOW, two non-equivalent mutants survive.** M3: AP1's boundary at exactly 90.0 or 140.0 min is untested. M18: the `roots != [ROOT_ID]` leg is untested (only a wrong depth-1 id is driven). Fix: add a fixture where "BUILD SUCCESSFUL in 2h 20m 0s" gives HELD, and one where a root id n00000002 gives REFUSED; raise SELFTEST_CHECKS to 80.
- **D2 LOW, AP1's "at 14 g" is shown but not checked.** Fix: parse maxMemory from the heap line and require 14 GiB (15.03 GB).
- **D3 LOW, the post-write byte check only prints.** The docstring (L49) says the outcome of record is unchanged "after it", but main() prints the sha after the write without comparing it. Fix: compare against main_bytes and refuse or flag, or drop the words "after it".
- **D4 LOW, selftest asserts vanish under `python -O` / PYTHONOPTIMIZE.** This includes guarded_connect, and the count still reaches 78, so the selftest would pass vacuously. PYTHONOPTIMIZE is unset here. Fix: use explicit `if not …: raise`.
- **D5 LOW, guard (2)'s L128 refusal echoes the changed line with %r.** With --record-a1-failed, arbitrary text from the outcome of record (e.g. T1 counts) could land in the addendum file. Fix: print a sha16 of the line, not the line.
- **D6 LOW, the selftest leaves about 40 t1b_null_selftest_* dirs in %TEMP%.** Fix: shutil.rmtree in a finally block.
- **D7 cosmetic, the protected-path refusal is tagged WRITE:REFUSED_EXISTS.**

## Conditions for the run-operator

- **C1:** Run from the MAIN checkout after the merge, because ROOT defaults to the script's own checkout and the worktree has none of the inputs. Run with PYTHONDONTWRITEBYTECODE=1.
- **C2:** Run `--dry-run` first. Require GUARD (1) PASS with "orphans CSV->site 0 / site->CSV 0" and "snapshots.db leaf set 100 = jsonl's"; this is the only execution of the CSV and DB legs on real inputs. Then require GUARD (2) PASS with blob 90632b36bed0 True, and GUARD (3) PASS.
- **C3:** Tee the stdout of `--run` to a log file.
- **C4:** If `--run` prints "NOT WRITTEN: A1 FAILED", stop. Whether to pass --record-a1-failed is the registrar's decision after review, not the operator's. No second null run without a registered bracket.
- **C5:** The post-run numbers review re-derives k, the Wilson interval, the three A2 rows and the bands from the CSV independently.

Scratch harnesses: `scratchpad/audit_selftest.py`, `mutate.py`, `mutate2.py`.
