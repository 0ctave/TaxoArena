# READY re-review: SPLIT-EXPOSURE-SENSITIVITY at d3270d5 (adversarial reviewer, 2026-09-23, zero calls, read-only)

**VERDICT: READY** for `--run` in one rule-7 window of 3.5 h at 8 workers.

- On the real data, the dry-run passes C0 on **13 of 13** cells, exits **rc=0**, and prints "C0 SUMMARY: PASS 13 of 13 built cells; C0 UNDETERMINED (BY VALIDITY) 0; removal-stage failures 0".
- Every connection-attempt count (A4) is 0. There are 0 refused `.env` reads and 0 other refusals, on the C0 runs and on the removal runs alike.
- The previous review's findings are fixed: D1 and D2 are verified by execution on real data, D3-D5 and D6 by execution on synthetic fixtures.
- **D8 (MEDIUM) is found here and does not block.** The audit hook does not refuse os.replace, os.rename, os.remove or os.truncate. The 7 originals and their helpers reach no such call (count 0). Fix it or record it as a documented limit before the run (condition 2).

Previous review: docs/reviews/READY_split_exposure_sensitivity.md (f33ca79, NOT READY at 4934a28). Registration L14701-L14756 (46889ea); evidence L14829-L14841; rulings L14867-L14881 (a4d736a).

## Identity (pins with their kinds; LF is the rendering of record; both files are LF in the working tree)
- tools/analysis/split_exposure_sensitivity.py: **blob:145749acd2f9b6e4aaf0ba579747ad98311bf24a / sha256-lf16:aae4bce3f9be1cbd** (`git hash-object`; `git show d3270d5:<path> | sha256sum`). Matches the brief.
- tools/analysis/split_exposure_child.py: **blob:a8df433ec75952759f385a478b64a093613251d8 / sha256-lf16:23a719ffe6c6eac0**. Matches the brief.
- Branch worktree-agent-a25e9d1b2b909850c at d3270d5 (on 4934a28). `git diff --stat 751cf57 d3270d5 -- tools/analysis` lists only these 2 files, so they are mergeable by path.
- The 7 originals and 9 pinned helpers are identical in main and in the worktree. Checked by blob and by sha256-lf16 against HELPER_PINS / ROUTE_A_SPECS:
  - judge_free_tests 9307ca71, pool_guard 6521b51a, prompt_v2 52b36965, rejudge_grok 939de7c7, rejudge_reasoning 1339592a, rejudge_reference 7640f800, rubric_p8 2eda08ff, rubric_value_contrast 9e1541a7, split_side 05224b5a.
  - Originals as in f33ca79.
  - cert_under_filter.py is blob:f7d59019... / sha256-lf16:0db2026f17b559a1.

## Hygiene of this review (rule 7)
- Window 21:00:38-21:27:36. No construction, no site null, and CERT-DIRECTION-STREAM not started.
- Running alongside: another agent's vote_frame_cert mutation runs (about 13 python processes under scratchpad eng_fixes_vfc/, synthetic, admitted). They load the CPU, so the timings below are conservative.
- The dry-run ran from main through temporary untracked copies of the two d3270d5 files. It was removed afterwards together with its .pyc: `git status --short tools/` prints 0 lines, and no split_exposure python process is alive.
- Fingerprints (size, mtime_ns, sha256_16) of all 15 input DBs, plus every -wal/-journal/-shm in their directories: **IDENTICAL before and after** (`diff` empty, 33 lines). The -wal files are 0 bytes.
- The instrument's own checks agree: 15 route files unchanged; its inputs before/after unchanged.
- snapshots_frozen.db and twenty_newsgroups_cache_v1.db were never opened.

## Selftest
- `--selftest` passes under python and under `python -O`: rc 0 both, "58 of 58 required", 26-27 s.
- The new negative controls are all UNDETERMINED (BY VALIDITY): dbapi2, subclass, open_write, raw_socket, dotenv, unpinned_helper.

## C0 per cell, real-data dry-run at d3270d5
My independent recomputation is from f33ca79 (indep.py, indep_ladder.py). The inputs are unchanged since then; the fingerprints are identical to that snapshot.

| cell | C0 at d3270d5 | my recomputation | A4 attempts / .env / other refusals | k (matches / questions) | hazard lines printed |
|---|---|---|---|---|---|
| a-E28 RUBRIC-512 | PASS +1.8, 42:25, p 0.0498, n 946 | 946, 42:25 | 0 / 0 / 0 | 7 / 7 | (c), (d) 0 of 784 outside |
| a-E70 | PASS | same | 0 / 0 / 0 | 20 / 19 | (d) 0 of 784 |
| b-E28 RUBRIC-512-SS | **PASS** +1.0, 35:26, p 0.31, n 946 | 946, 35:26 | 0 / 0 / 0 | 7 / 7 | (c), (d) 0 of 784 |
| b-E70 | **PASS** | same | 0 / 0 / 0 | 20 / 19 | (d) 0 of 784 |
| c-E28 RUBRIC-512-R | **PASS** 0.842 / 0.842, 24:24, n 946 | 946, 24:24 | 0 / 0 / 0 | 7 / 7 | (c), (d) 0 of 784 |
| c-E70 | **PASS** | same | 0 / 0 / 0 | 20 / 19 | (d) 0 of 784 |
| d-E28 LEAF-POWERED | PASS -0.3, 9:7, n 786 | 786, 9:7 | 0 / 0 / 0 | 8 / 4 | (c), (d) 0 of 506 |
| d-E70 | PASS | same | 0 / 0 / 0 | 22 / 13 | (d) 0 of 506 |
| e-LADDER | **PASS** -0.3, 35:38, p 0.68, n 967 | 967, 35:38 | 0 / 0 / 0 | 2 / 2 | (a), (d) 0 of 787 |
| e-STACK (v1) | PASS 0.843, n 944 | 796/944 | 0 / 0 / 0 | 3 / 3 | (a), (d) 0 of 782 |
| e-STACKv2 | PASS 0.865, n 944 | 817/944 | 0 / 0 / 0 | 3 / 3 | (a), (d) 0 of 782 |
| e-J6 | PASS -1.8, 23:40, p 0.043, n 944 | 944, 23:40 | 0 / 0 / 0 | 3 / 3 | (a), (d) 0 of 783 |
| f-CERT | PASS W_F 17, W_R 24.15, Delta_W -7.15, [-14.22, -0.08], 13 anchors, 752 edges, SE 3.606, HELD (366 s) | per READY 751cf57 | in-process; cert's log shows 4 connects, stack cache once, all immutable | 201 / 69 | (a), (b), (d) 0 of 2811 |

- All four hazards (a)-(d) print in the header with the cells each one touches, and again beside those cells.
- The A4/.env/refusal columns: `grep -c` of the line "outbound connection attempts 0 (must be 0) | .env reads refused 0 ... | other refused operations 0" returns 12 of the 12 "outbound connection attempts" lines. Each line sums over the cell's full child and its removal child, so the 3 removal runs per cell are covered too (task 3).
- The "local modules pinned" count per consumer ranges from 3 to 10, and no D5 refusal occurred.
- The connection logs are as in f33ca79, all immutable. SS and R each open the same 5-6 DBs once; LADDER opens rubric_ladder and ratings_x12 twice.
- Removal fidelity and the null were verified at f33ca79, with my own code, on the same engine. The only change since is in the child's guards; the removal and null code (draw_removals, mapper, evaluate_cell core) is unchanged apart from the stage labels. **Not re-run on real data:** removal fidelity for SS, R and LADDER, and the 3-draw null reproduction; the dry-run executed their removal path (3 runs each, 0 refusals).

## D3/D4 by execution (adv_route_rr.py: my f33ca79 originals plus new ones, run through the builder's make_route_cell / evaluate_cell at d3270d5)

| original | f33ca79 (4934a28) | d3270d5 |
|---|---|---|
| second connection INSERT | refused | refused |
| `sqlite3.dbapi2.connect` write | **landed**, detected afterwards | refused (readonly), no write |
| `sqlite3.Connection` subclass direct | **landed**, detected afterwards | refused by the audit hook, no write |
| `connect(..., factory=C)` | refused | refused |
| `open(side, "w")` | **undetected, scored** | refused by the audit hook; no file |
| urllib to a local listener | refused, counted | refused, counted |
| raw `_socket` connect | **bypassed** | refused (audit socket.connect); listener accepted 0 |
| key read from a file not named .env | scored | scored, 0 attempts (documented: readable, never sent) |
| two headline lines | refused (A6) | refused (A6) |
| row_factory assignment | fails closed | fails closed (documented) |
| **new** `shutil.copy(src, DB)` | - | refused (open for writing); DB unchanged |
| **new** `connect("file:DB?mode=rw", uri=True)` + INSERT | - | redirected to immutable; readonly; no write |
| **new** `sqlite3.Connection("file:DB?mode=rw&x=?mode=ro&immutable=1", uri=True)` (passes the hook's endswith test) | - | readonly (the later mode=ro wins); no write |
| **new** `os.replace(src, DB)` | - | **the DB was REPLACED** (its table list became ['quirk']); detected only afterwards by the fingerprint (cell UNDETERMINED) |
| **new** `os.remove(file)` | - | **the file was deleted, undetected; the cell scored FLAGGED** |
| **new** `os.truncate(file, 0)` | - | **the file was truncated to 0, undetected; the cell scored** |

## Defects
- **D8 MEDIUM (new).** The audit hook refuses write-opens, but not the file-system events that destroy without opening: os.rename / os.replace, os.remove / os.unlink, os.truncate, os.rmdir, shutil.rmtree, os.link / os.symlink, os.chmod, os.utime.
  - An original could replace or delete a DB of record. A replacement is caught only after the fact by the A3 fingerprint; a delete or truncate of an unopened file is not caught at all.
  - Real exposure is nil. Over the 7 originals and 8 of the 9 helpers, the count of `os.(replace|rename|remove|unlink|truncate|rmdir|link|symlink|chmod|utime)|shutil.(move|rmtree|copy)` is 0. pool_guard has 6, all at L494-L668 in its export and selftest paths, which no analyze() path reaches.
  - Fix: add these events to `_audit` as refusals, plus one selftest negative control (os.replace).
  - Alternatively, record them as a documented limit beside "native code" in the docstring.
- **D9 LOW.** The `_immutable_or_memory` test is a suffix match: a URI whose query ends in "?mode=ro&immutable=1" but carries mode=rw earlier passes the hook. SQLite's last-wins parsing made it read-only in my test, so no write landed; the check is still a string pattern, not a parse. Fix: parse the query with urllib.parse and require mode=ro and immutable=1 with no other mode.
- D1-D6 of f33ca79: **all FIXED**, each verified by execution as stated above.

## Runtime and memory (d3270d5, --workers 1, under the concurrent vote_frame_cert mutation load)

| part | measured | CPU for the full run | wall at 8 workers |
|---|---|---|---|
| CERT C0 | 366 s | - | - |
| CERT replicates | 386.1 s each (418 s at f33ca79) | 201 x 386 s = 21.6 CPU-hours | about 2.7 h (2.9 h at the f33ca79 rate) |
| RUBRIC-512 / -SS / -R, LEAF-POWERED, J6 | 0.1 s per run | about 2 min each per 1,001 runs | together about 10-15 min |
| LADDER | 2.7 s per run | about 45 min | (in the line above) |
| STACK / STACK-v2 | 0.5-0.7 s per run, child peak 868 MB | about 10 min each | (in the line above) |
| **Whole run** | | | **about 2.9-3.1 h** |

- **The 3.5 h window stands**, with 12 GB free (8 STACK chunks at about 0.87 GB, about 7 GB peak).
- Do not share the window with CERT-DIRECTION-STREAM: 16 CPU-bound workers on 12 physical cores, and neither run is resumable. Unless both PIDs are admitted under W1-W5, use back-to-back windows.

## Conditions
1. Run from the merged main (the paths above) at these two pins, in one 3.5 h window, W1-W5 enforced, ≥ 12 GB free, CERT-DIRECTION-STREAM not concurrent.
2. D8: extend the hook, or record it as a documented limit with the registrar's acceptance. The run does not wait on it: no real code path reaches those calls. If the code changes, the pins change and need a short re-check (selftest plus dry-run C0 13 of 13).
3. Post-run review: re-measure the null SD, DEFF, n_eff and MDE per cell against the registered support word, and print them beside each cell's deciding statistic.

Scratch (session scratchpad ses_ready/rr/ and ses_ready/): dry.out, dry.err, fp_before.txt, fp_after.txt, selftest.out, selftest_O.out, adv_route_rr.py.
