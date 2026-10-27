# Delta review 3: CANARY-EPOCH2-RUNG at 9e345f5, the ceiling amendment CEILING-2 only (adversarial reviewer, 2026-09-24, zero calls, read-only; no pool DB opened)
**READY-WITH-CONDITIONS**: CANARY-EPOCH2-RUNG, tools/analysis/canary_baseline.py sha256-lf16 32236c62be50038c (blob:71d3f308c9b19d452e2276a1f0bbb230efaefb25), with tools/analysis/accepted_tests_ledger.py sha256-lf16 47008504f09aa473 (blob:4e9db106c2ebeaea8674b2a5a6227f1d9b838ccf), for the pass-4 resume `--pass 4 --run --go` (the 3 missing matches, 8720, 879 and 9136, about 6 calls).

This review supersedes the verdicts on ccc145d0009e1a65 and 96d27df4561a2fe3 further down, for this instrument version. Their findings, conditions and the P6 printing rule stand.

Amendment reviewed: CANARY-EPOCH2-RUNG-CEILING-2 (docs/judge_v2_program.md L15843-L15848, 64cf3a1), the author's decision, budget only: 1,248 -> 1,260.

| # | claim | verdict | command | result |
|---|---|---|---|---|
| 1 | the diff 0a59225..9e345f5 is exactly the ceiling change | CONFIRMED | `git diff --stat` and the full diff read | 2 files, 5 insertions, 5 deletions: `CEILINGS` CANARY 1248 -> 1260 (TRACE 2184 unchanged); `EPOCH2_CEILING` 1260; `EPOCH2_REGISTERED_CALLS` still 1200 (P6 unchanged); the two selftest probes moved to 1,262 and +62. Nothing else. The pins are LF in the worktree (working-tree sha256 = LF sha256) |
| 2 | the payload is AST-unchanged | CONFIRMED | ast.dump over 7d9a4e2e / e9f50b0e / 71d3f308 | 23 defs AST-identical to 7d9a4e2e, including all 12 payload-path functions. Against 0a59225 the only def that changed is selftest_epoch2, and the only constant that changed is EPOCH2_CEILING. Not re-executed against the pool: the pool DBs are closed to readers by the split-draw constraint |
| 3 | selftests pass | CONFIRMED | `python [-O]` on canary_baseline.py --selftest-epoch2, canary_baseline_selftest.py, trace_truncation.py --selftest | rc 0 in all 6 runs; epoch 2: 61 checks OK |
| 4 | resume accounting 1246 + 6 = 1252 of 1260 | CONFIRMED | day_calls_2026-09-24.json (JSON read); pass 3 / pass 4 caches opened mode=ro&immutable=1 after an empty-sidecar check | CANARY ledger rows 24 + 2 + 571 + 23 + 2 + 24 + 567 + 33 = 1,246; caches 300 + 297 rows; 1,246 + 6 = 1,252 <= 1,260 |

Conditions:
1. Merge by path, byte-identical: blob:71d3f308 and blob:4e9db106.
2. The resume is a single `--pass 4 --run --go`. Its window is measured from pass 4's persisted start (D2): gap 1,093 s, WITHIN. Retry room after the 6 calls is 8 calls. If it runs out, do not amend a third time: close with 297 via `--analyze-epoch2` (rung INVALID, C2 UNDETERMINED BY VALIDITY), as the amendment's alternative states.
3. No dry-run while the split draw holds the pools (the dry-run reads mmlu_pro_dataset_cache_v2). The resume itself reads the pool DB through build_jobs, so it too waits until the split draw releases the pools, under rule 7.
4. `--analyze-epoch2` only after pass 4 holds 300 rows or is closed as above. P6 is printed per the rule in delta review 2 (cached calls against 1,200; posted calls and the 429 retries beside it).

# Delta review 2: CANARY-EPOCH2-RUNG at 0a59225, the ceiling amendment only (adversarial reviewer, 2026-09-24 14:05, zero calls, read-only)
**READY-WITH-CONDITIONS**: CANARY-EPOCH2-RUNG, tools/analysis/canary_baseline.py sha256-lf16 ccc145d0009e1a65 (blob:e9f50b0ea8f97d7b057868d0412e867df0bb691b), with tools/analysis/accepted_tests_ledger.py sha256-lf16 18568f97cda93099 (blob:23b0cd7869fc3e403fbac7d52d4fe3cf8cd46106), for `--pass 4 --pilot 12 --go` then `--pass 4 --run --go`. The first pass-4 launch must START before 15:47:56 on 2026-09-24.

This review supersedes the verdict on 96d27df4561a2fe3 further down for this instrument version; every finding and condition below it stands.

## Amendment reviewed
CANARY-EPOCH2-RUNG-CEILING-1 (docs/judge_v2_program.md L15764-L15770, 8983990): the author's decision, budget only. The ceiling goes from 1,200 to 1,248 calls; no criterion, bar, payload, schedule or analysis changes.

## Per claim (the pins are both LF in the worktree: working-tree sha256 = LF sha256)
| # | claim | verdict | command | mine vs claimed |
|---|---|---|---|---|
| 1 | the diff 1138e45..0a59225 is exactly the described change | CONFIRMED | `git diff --stat 1138e45 0a59225` (whole diff read) | 2 files, 7 insertions, 6 deletions: `CEILINGS["CANARY-EPOCH2-RUNG"]` 1200 -> 1248 (TRACE 2184 unchanged); `EPOCH2_CEILING` 1248; new `EPOCH2_REGISTERED_CALLS = 1200` used only by P6; the two selftest probes moved to 1,250 and +50. Nothing else |
| 2 | payload AST-unchanged; only epoch2_readout and selftest_epoch2 changed | CONFIRMED | ast.dump over 7d9a4e2e / 6642a91d / e9f50b0e | 23 defs AST-identical to 7d9a4e2e, and all 12 payload-path functions. Defs changed against 1138e45: exactly epoch2_readout and selftest_epoch2. Constants changed or added: EPOCH2_CEILING and EPOCH2_REGISTERED_CALLS only. By execution: 300 of 300 payloads and 600 of 600 bodies equal blob 7d9a4e2e's |
| 3 | selftests pass under python and -O | CONFIRMED | `python [-O] canary_baseline.py --selftest-epoch2`; `canary_baseline_selftest.py`; `trace_truncation.py --selftest` (it imports the changed ledger module) | rc 0 in all 6 runs; epoch 2: 61 checks OK |
| 4 | the pass-4 dry-run is GO, 622 + 600 = 1,222 of 1,248, anchors reproduce | CONFIRMED | delta2/cb_dry2.py 4 (the branch source, the BRANCH ledger module loaded explicitly and asserted to read 1,248; every connect ro-immutable) | [RUNG] gap 990 s, WITHIN; pre-flight would GO; anchor 3501e6aef27aad68, order 20b51354c05c5ad4; [ACCOUNT] (i) own 622 (cache 600, ledger 622) + 600 = 1222 of 1248, (ii) 611 of 4,000 matches, (iii) 4,060 + 622 + 2,178 + 600 = 7,460 of 14,000 -> OK; [PIN] UNCHANGED; the day ledger's pass-3 rows sum to 24 + 2 + 571 + 23 + 2 = 622. sha256 of pass3.db and of day_calls_2026-09-24.json identical before and after; no pass4.db created |

## P6 under the registration: how it must be printed
P6 is registered as "fingerprint azure:grok-4-1-fast-non-reasoning on 1,200 of 1,200; INVALID or unusable 0 [0, 3]". Its object is the fingerprint on the calls that RETURNED A VERDICT, one per (match, order) over 2 passes x 300 matches. A call that failed with HTTP 429 returned no model field and no verdict, so it has no fingerprint to score.

The builder is right to decouple P6 from the ceiling. Keeping `s["calls"] == EPOCH2_CEILING` would have scored FAILED against 1,248, a number the registration never contained.

**Ruling:** P6 is scored on the cached calls: 2 x rows over passes 3 + 4, against the registered 1,200. It is NOT scored on the posted calls. The record must print both, beside each other, in this form:

"P6 HELD/FAILED: fingerprint on X of 1,200 verdict-bearing calls (cached, 2 x 600 rows), foreign none; unusable U; POSTED N calls (day ledger), of which N - 1,200 errored (HTTP 429 / transport) with no verdict and no fingerprint, under the amended ceiling 1,248 (CANARY-EPOCH2-RUNG-CEILING-1)."

The instrument prints the cached count in the P6 line and the ledger count in the ACCOUNTING line. The registrar joins them in the outcome record. No code change is needed.

The posted excess is NOT an unusable verdict: errored calls are never cached, rule 10 concerns deterministic content-filter refusals, and they do not count in P6's "0 [0, 3]".

## Defects (new)
- **E1 LOW (a margin, not a defect):** only 26 calls of retry room remain (1,248 - 1,222). Pass 3 needed 22.
  - A pass-4 relaunch that would pass 1,248 is REFUSED, not trimmed.
  - The fallback is registered in the amendment: `--analyze-epoch2`, with the rung INVALID if pass 4 is partial (D1 fix) or `--no-rung` if pass 4 never started. C2 UNDETERMINED either way.
  - The run-operator must not raise the ceiling again without a new amendment.
- **E2 LOW:** the P6 value string prints only the cached count. It is covered by the printing rule above.

## Conditions (added to those of the 1138e45 review, which all stand)
1. Merge to main by path, byte-identical: canary_baseline.py blob:e9f50b0e (sha256-lf16 ccc145d0009e1a65) and accepted_tests_ledger.py blob:23b0cd78 (sha256-lf16 18568f97cda93099). The ledger module is shared with trace_truncation.py; TRACE's ceiling is unchanged.
2. From main, `--dry-run --pass 4` must reproduce anchor 3501e6aef27aad68 and order 20b51354c05c5ad4, [RUNG] WITHIN, pre-flight would GO, and [ACCOUNT] (i) 622 + 600 = 1222 of 1248.
3. The pass-4 pilot must START before 15:47:56. `--run` follows immediately; after the pilot, its window is measured from pass 4's persisted start. Run `--analyze-epoch2` only when pass 4 holds 300 rows, or when pass 4 is abandoned with the reason logged (D10).
4. If the 26-call margin runs out: stop, do not amend again, and record per the amendment's fallback.
5. The outcome record prints P6 in the form ruled above.

Scratch: scratchpad/paid_ready/delta2/ (e2*.log, base*.log, tt*.log, cb_dry2.py, cb_dry2_4.log).

# Delta review: CANARY-EPOCH2-RUNG at 1138e45 (adversarial reviewer, 2026-09-24, zero calls, read-only; supersedes the NOT READY of 7b102ad, kept verbatim below inside a fence)
**READY-WITH-CONDITIONS**: CANARY-EPOCH2-RUNG, tools/analysis/canary_baseline.py sha256-lf16 96d27df4561a2fe3 (blob:6642a91db120eaed866b6f39ba723d40fadfad22), for `--pass 3 --pilot 12 --go` -> `--pass 3 --run --go` -> `--pass 4 --pilot 12 --go` -> `--pass 4 --run --go` under the conditions below.

- D1 (HIGH) is fixed, verified by execution in fresh directories: with pass 3 complete, the outcome of record is now written in all four pass-4 states.
- D2-D8 are fixed. 20 of the 21 fix-related mutants I ran are KILLED under both python and -O; the exception is M31, explained below.
- The payloads are still byte-identical to the pass-2 script of record (300 of 300), and both anchors reproduce.
- New finding D10 (MEDIUM): the D1 fix lets an `--analyze-epoch2` run while pass 4 is still in progress close the record, and with it the rung. It is carried as run condition 3, not a block.

## Identity (every pin names its kind; LF is the rendering of record; the worktree is LF: working-tree sha256 = LF sha256)
| object | blob | sha256-lf16 | sha256-crlf16 (for reference) |
|---|---|---|---|
| tools/analysis/canary_baseline.py @1138e45 | 6642a91db120eaed866b6f39ba723d40fadfad22 | 96d27df4561a2fe3 | (the working tree is LF) |
| tools/analysis/canary_baseline_selftest.py @1138e45 | abf72936422ddbf26a8f57eeb65f3af2078cdb59 | 8efbb91f7c750cf4 | |
| tools/analysis/accepted_tests_ledger.py (unchanged; = main ca417f8) | 7fb20f64c387723a7214d3698e37b5401c70a82c | 831af6b1f0ee4697 | |
| tools/analysis/trace_truncation.py (unchanged; = main ca417f8) | f6dfb4b2aec6db4c58a81fdec57b3ff8c1a67b79 | 633384b658105e1f | |
Command: `git rev-parse 1138e45:<path>`; `git show 1138e45:<path> | sha256sum`; `git -C <main> rev-parse main:<path>`. 1138e45 touches exactly these 2 files (`git show --stat`: 2 files changed).

## Constraint honoured: TRACE-TRUNCATION was posting throughout
Neither experiment_results/multicorpus/trace_truncation.db nor any day_calls_*.json was opened. The dry-runs ran with TRACE_CACHES = [] and LEDGER_DIR = a temp directory holding only a copy of the closed night_calls_2026-09-23.json. The [DBGUARD] lines list 5 distinct files, all ro-immutable: mmlu_pro_dataset_cache_v2.db, grok-reasoning.db, rubric_ladder.db, and canary_baseline_pass1.db / pass2.db. `grep -c trace_truncation` over both logs is 0 in the connect lists. The accounting printed (4,060 + 0 + 0 + 600 = 4,660) therefore EXCLUDES TRACE's posts by construction. It is not the number of record for the launch (condition 5).

## Per-claim (the builder's claims)
| # | claim | verdict | command / script | mine vs claimed |
|---|---|---|---|---|
| 1 | selftests pass under python and -O | CONFIRMED | `python [-O] canary_baseline.py --selftest-epoch2`; `python [-O] canary_baseline_selftest.py` | epoch 2: rc 0 / rc 0, 61 checks OK, 41 of 41 branches. Base: rc 0 / rc 0, 0 bare `assert` left (`grep -cE '^\s*assert '` = 0), 50 ensure() uses. M6c (write-once bypass) is now KILLED under -O too (it survived before) |
| 2 | D1: the outcome is written in all four pass-4 states | CONFIRMED | delta/cb_partial_rung_fresh.py (the fixed code, a FRESH temp directory per run) | pass 4 at 12 rows: rc 0 WRITTEN, with or without --no-rung. Pass 4 at 0 rows: rc 0 WRITTEN, with or without --no-rung. In all four: ALARM STATE: NO ALARM, "(C2) ... UNDETERMINED BY VALIDITY (INVALID; pass-4 rows 12 / 0)". Pass 4 ABSENT without --no-rung: rc 2, partial file only (correct: pass 4 may still run). ABSENT with --no-rung: rc 0, rung ABSENT, C2 UND |
| 3 | my rc 3 came from write-once reruns in the same directory | CONFIRMED | same, fresh directories | my 7b102ad script reused one directory across its --no-rung False/True runs. Fresh directories give rc 0 in every written case |
| 4 | D2: the window is measured from pass 4's persisted start | CONFIRMED | code `pass4_start()`; M22 (return "now" instead) KILLED; M5a and M5b KILLED | first pass-4 launch: measured from now. Once a pass-4 cache exists: from run_meta 'started'. The analysis uses max(first row, started) - last3 |
| 5 | D3-D8 | CONFIRMED | mutants M24 C0 (a) literal True, M28 verify_set no-op, M26 errors not counted, M29 --pilot any N, M30 --override-guard allowed, M27 regex reverted: all KILLED under both modes | C0 (a) recomputes set_hash; verify_set raises SystemExit; the gate regex reads a verdict line after a blank line |
| 6 | M5b, M10, M15, M17 now KILLED | CONFIRMED | delta/mutants_delta.py (a copy of 1138e45's tools/analysis, the baseline selftests rc 0 first) | all KILLED under both modes; also M2, M5a, M6b, M6c, M7c, M18, M22-M30 |
| 7 | M20 is equivalent | CONFIRMED | 138 x 300 = 41,400 is not a multiple of 1,000, so `>=` and `>` agree at n = 300 | SURVIVED as expected |
| 8 | M6d survives (the ledger's "x" creation mode) | CONFIRMED | | ruled below |
| 9 | the payload code is AST-identical to 7d9a4e2e | CONFIRMED (and more) | ast.dump over module-level defs | 23 defs AST-identical (the builder says 17), including all 12 payload-path functions and every module constant. By execution: 300 of 300 per-match payloads (system, both user turns, reference) and 600 of 600 posted body dicts identical to blob 7d9a4e2e's own build_jobs |
| 10 | anchors reproduce | CONFIRMED | delta/cb_dry_delta.py 3 / 4 | anchor 3501e6aef27aad68, posting order 20b51354c05c5ad4, 600 payloads, scan PASS, [PIN] UNCHANGED at start and end, pass-3 pre-flight would GO (26/300), pass-4 pre-flight REFUSES (pass 3 missing), rc 0 / rc 0 |
| 11 | no write to any file of record | CONFIRMED | `sha256sum -c` on pass 1 / pass 2 / canary_set.json: OK; no canary_baseline_pass3.db and no canary_epoch2_outcome.txt exist | 0 writes |

M12 (accounting from the cache only) is now KILLED by the canary selftest; it still survives the TRACE selftest (TRACE's D2 debt, unchanged, not in scope). M31 (ensure() turned into a no-op) SURVIVES. That is inherent: a correct program never trips ensure(), and the fixture has no negative control. M6c now being KILLED under -O shows ensure() does run. LOW, documented.

## Rulings asked for
**(a) "Every epoch-2 posting launch is refused once the outcome exists" (the [RECORD] refusal): CORRECT under ruling 6.**
- The outcome is write-once and is the record of C1 and C2. Any call posted after it can enter no registered readout, so it would be spend without a reading.
- Ruling 6 already says a pass 4 that does not run, or does not complete, leaves C2 UNDETERMINED BY VALIDITY. It never allows reopening a written outcome.
- The refusal also stops a pass 4 from running after a `--no-rung` declaration.

The hazard is the ORDER of operations. That is D10:
- **D10 MEDIUM (new, from the D1 fix):** a pass-4 cache with ANY row count now makes the outcome writable. So an `--analyze-epoch2` run between pass 4's pilot and its `--run` writes the record with the rung INVALID at 12 rows. From then on the refusal above blocks pass 4 permanently: I executed the 12-row case (rc 0, WRITTEN), and M25 shows the refusal fires.
- Registration C0 requires only that pass 4 START within 2 h. Its later launches measure from that start (D2), so a pass 4 in progress is still admissible and must not be closed by a readout.
- Fix, queued and not blocking: write an incomplete pass 4 of record only when the 2 h window from pass 3's last row has expired, or under an explicit `--rung-abandoned "<reason>"` flag. Until then, run condition 3.

**(b) M6d, the ledger's "x" creation mode: NO FIX NEEDED BEFORE THE RUN.**
- "x" versus "w" differs only when two processes create the SAME day file in the same instant. M6d survives because no single-process test can reach that case.
- The real exposure is wider. `accepted_tests_ledger.append` reads, writes a tmp file and os.replace()s it with no lock. Two concurrent posters (TRACE and CANARY) can therefore lose a ledger row; the caches stay correct, and max(cache, ledger) then under-counts only errored calls.
- Both are closed by the standing condition that CANARY never posts while TRACE is posting. Queue ACCEPTED-LEDGER-LOCK: an exclusive lock file around read-append-replace, and a two-process selftest.

## Conditions for the pilot and the run
1. Merge to main by path, byte-identical to the pins above: canary_baseline.py blob:6642a91d / sha256-lf16 96d27df4561a2fe3 and canary_baseline_selftest.py blob:abf72936 / sha256-lf16 8efbb91f7c750cf4. accepted_tests_ledger.py is already on main at blob:7fb20f64.
2. **Only after TRACE-TRUNCATION's last launch has returned** (the one-poster rule; M6d and the ledger lock): from main, `--dry-run --pass 3` reproduces anchor 3501e6aef27aad68 and order 20b51354c05c5ad4, [PIN] UNCHANGED, pre-flight would GO, and [ACCOUNT] (iii) = 4,060 + TRACE's posted calls as read from its cache and ledger + 600 <= 14,000.
3. Sequence, never interleaved with a readout:
   - `--pass 3 --pilot 12 --go`, the guard read, then `--pass 3 --run --go`.
   - Immediately, `--pass 4 --pilot 12 --go` and `--pass 4 --run --go`. The FIRST pass-4 launch must fall within 7,200 s of pass 3's last row.
   - `--analyze-epoch2` ONLY when pass 4 holds 300 rows. Or, if pass 4 was not started in the window, `--analyze-epoch2 --no-rung`. Or, if pass 4 is abandoned (a fingerprint stop, a failed pilot), only after the run-operator records the reason in the run log (D10).
   - Never `-O`, `--override-guard`, another `--maxtok` or `--temperature`.
4. An errored pilot match fails the pilot's guard (D6). If the pilot is relaunched, the run-operator records the first launch's error count from its "done:" line: the relaunch cannot see it, and the ledger keeps it.
5. The outcome's ACCOUNTING line is read against the day ledger after both tests have finished (the dry-run's 4,660 excludes TRACE by construction). The post-run reviewer runs the full-payload scan over the stored bodies and re-measures the DEFF from the caches' own cluster sizes (Kish 1.160).
6. Queued, not blocking: D10 (the `--rung-abandoned` guard), ACCEPTED-LEDGER-LOCK.

Scratch: scratchpad/paid_ready/delta/ (e2*.log, base*.log, mutants_delta.py / extra_mutants.py / mutants_delta.out, cb_partial_rung_fresh.py / .log, cb_dry_delta.py, cb_dry_delta3.log, cb_dry_delta4.log, ast_cmp_delta.py).

## The review of 7b102ad (NOT READY at e1ed7466917bd8fb), kept verbatim; fenced so that the gate reads only the verdict above
~~~text
# Review before posting: CANARY-EPOCH2-RUNG at 252f765 (adversarial reviewer, 2026-09-24, zero calls, read-only)
**NOT READY**: CANARY-EPOCH2-RUNG, tools/analysis/canary_baseline.py sha256-lf16 e1ed7466917bd8fb (blob:4d48f1a9f634d309b5bd6b889f38a8cbda91fb27). One HIGH defect: a failed rung blocks the registered alarm C1 from ever being written of record.

- Everything about what the instrument POSTS is right. Payloads are identical to the pass-2 script of record on 300 of 300 matches. The anchors reproduce, the caches of record are pinned and untouched, C1 is an exact integer rule under convention A, and the A/B branch works.
- The defect sits in how the outcome is WRITTEN. If pass 4 exists but is incomplete or empty, `--analyze-epoch2` cannot write the outcome of record in any mode. I executed four scenarios; 0 outcomes were written. The registration and ruling 6 say that in that case C1 is recorded and C2 reads UNDETERMINED BY VALIDITY.
- The fix is small, but it changes the sha. The gate stays shut until a delta review of the fix.

Registration: docs/judge_v2_program.md L14931-L14970 (fad9ea2). Rulings: L15188-L15206 (b0b5d0d), choices 6 and 7 and the accounting file. Dry-runs recorded: L15302-L15318 (4). Scratch: scratchpad/paid_ready/ (cb_dry3.log, cb_dry4.log, cb_dry.py, ast_cmp.py, cb_partial_rung.py / .log, guard_branches*.log, mutants.out).

## Identity (every pin names its kind; LF is the rendering of record; the worktree files are LF)
| object | blob | sha256-lf16 | sha256-crlf16 (for reference) |
|---|---|---|---|
| tools/analysis/canary_baseline.py @252f765 | 4d48f1a9f634d309b5bd6b889f38a8cbda91fb27 | e1ed7466917bd8fb | 18c8e13c95f5784f |
| tools/analysis/accepted_tests_ledger.py @252f765 | 7fb20f64c387723a7214d3698e37b5401c70a82c | 831af6b1f0ee4697 | 95d19cb5cd9af67f |
| tools/analysis/canary_baseline_selftest.py @252f765 | 14aee2f3270b42a165f86f1884bc848efe02388b | 0092b08b723d8fe9 | ea45ef2096fde08e |
| pass-2 script of record | 7d9a4e2e7bd11ef662ec813c99f19a2ff1561875 | d62dc048ba6e9cf9 (the record's pin) | |
| caches of record (sha256 of the file) | | pass 1 5142795bdc8c5a8e..., pass 2 9e2f4b7cb2b30b3a... (`sha256sum -c` OK before and after my runs) | |

## Per-claim table
| # | claim | verdict | command / script | mine vs claimed | sev |
|---|---|---|---|---|---|
| 1 | the selftests pass under python and -O | CONFIRMED (epoch 2) / PARTLY (base) | `python [-O] canary_baseline.py --selftest-epoch2`; `python [-O] canary_baseline_selftest.py` | epoch 2: rc 0 / rc 0, 36 checks OK, 41 of 41 branches, both modes. Base: rc 0 / rc 0, 28 OK lines, but it is assert-based, so under -O it checks nothing (M6c is KILLED under python and SURVIVES under -O; pre-existing, queued CANARY-SELFTEST-ASSERTS) | LOW (D5) |
| 2 | dry-run anchors and counts | CONFIRMED | cb_dry.py 3 / 4 (the branch source executed with ROOT = main; helpers LF-identical to main, checked by `tr -d '\r' \| sha256sum`) | anchor 3501e6aef27aad68 = 3501e6aef27aad68; posting order 20b51354c05c5ad4 = 20b51354c05c5ad4; 300 matches (150 / 150), 600 payloads, 14 system prompts; pass-3 pre-flight "would GO" (the 1 -> 2 floor 26/300); pass-4 pre-flight REFUSES (pass 3 missing); accounting (iii) 4060+0+0+600 = 4660; [DBGUARD] 8 connects, all ro-immutable | - |
| 3 | passes 1 and 2 closed and sha-pinned | CONFIRMED | code L344-L348, L511-L526; the dry-run's [PIN] lines at start and end; `sha256sum -c` | 5142795b... / 9e2f4b7c... = the pins; `open_cache(1\|2)` refuses (selftest); a tampered cache refuses (selftest) | - |
| 4 | the payload code is AST-identical to the pass-2 script of record 7d9a4e2e | CONFIRMED | ast_cmp.py (`git show <blob>`, ast.dump) | build_jobs, configure_rr, payload_body, protocol, freeze_set, set_hash, strata_of, pool_qids, current_meta, temp_label, cache_path and check_fingerprint are AST-IDENTICAL; module constants unchanged; changed only analyze, dry_run, open_cache and run. By EXECUTION (cb_dry.py loads blob 7d9a4e2e and builds its payloads): 300 of 300 matches identical (system, both user turns, reference), 600 of 600 posted body dicts identical, and the anchor from the old script's payloads is 3501e6aef27aad68. The inputs are unchanged since pass 2 (grok-reasoning.db mtime 09-10, mmlu_pro_dataset_cache_v2.db 09-19, rubric_ladder.db 09-08; pass 1 vs pass 2 ref_letter / ref_correct identical 300 of 300) | - |
| 5 | every connect is immutable except the new caches | CONFIRMED | code L471-L501; the dry-run [DBGUARD] line; selftest (a read-write open of pass 1 refuses; a non-empty -wal refuses) | 8 of 8 connects are ro-immutable in the dry-run | - |
| 6 | the D2 write-once fix | CONFIRMED | code L980-L986, L1380-L1386; mutants M6b and M6c | `--analyze` and `--analyze-epoch2` open the outcome with mode "x" | - |
| 7 | C1 under convention A, exact integer comparison | CONFIRMED | L1252 `D*1000 >= 138*n`; M2 (C1 decided under B) KILLED; guard_branches G7 / G7b | A counts 5 unusable pass-3 rows as differences (A 5/300, B 0/295); an unusable row in BOTH passes still counts; M20 (`>=` to `>`) is an EQUIVALENT mutant at n = 300 (138 x 300 = 41,400 is not a multiple of 1,000) | - |
| 8 | the A/B disagreement branch | CONFIRMED | the selftest case A 42/300 ALARM vs B 32/290; M2 KILLED | "A AND B DISAGREE ... CONVENTION A DECIDES: ALARM" | - |
| 9 | the 7,200 s rung window | PARTLY | M5a (pre-flight) KILLED; M5b (analysis) SURVIVED; G8 / G8b executed | the analysis reads pass 4's start against pass 3's last row: 7,201 s gives INVALID and 7,199 s gives VALID (executed). But the PRE-FLIGHT measures from NOW at EVERY pass-4 launch, relaunches included (D2) | MEDIUM (D2) |
| 10 | C1 is recorded when the rung does not complete (registration C0; ruling 6) | REFUTED | cb_partial_rung.py (a scratch copy of the branch, temp fixtures) | pass 4 PARTIAL (12 rows): `--analyze-epoch2` returns rc 2 (partial file only), and `--no-rung` exits "[RUNG] --no-rung was given but a pass-4 cache exists". Pass 4 EMPTY (created, 0 rows): the same two results. Outcome of record written in 0 of 4 runs | HIGH (D1) |
| 11 | Support (a)-(f) | CONFIRMED (numbers) | own bootstrap over the pass 1 / pass 2 caches (B 2000, seed 42) | floor 26/300 = 0.0867 (convention A = B, 0 unusable); SE_boot 0.0170, binomial 0.0162, DEFF 1.093, n_eff 275; registered SE 0.01627 x sqrt(1.09) = 0.01699, MDE 0.0476; distance 0.051: SCOREABLE (thin). Kish 1.1600, not the registration's 1.14 (sizes 260 x 1, 18 x 2, 1 x 4; already bracketed in the script) | LOW |
| 12 | the accounting guard reads the posting-date ledger and both caches; "larger of cache and ledger" | CONFIRMED | accepted_tests_ledger.py; M1 / M13 KILLED, M12 SURVIVED | see READY_trace_truncation.md, "Ruling on the accounting reading": max() is the right reading; a sum double-counts every cached call; the residual is the crash case | LOW |
| 13 | no write to any DB of record | CONFIRMED | size and mtime of all 340 DB files and sidecars before and after, `diff` rc 0; `sha256sum -c`; no canary_baseline_pass3.db and no day_calls_*.json created | 0 changes | - |

## Mutants (mutants.py; the unmutated baseline passes first)
KILLED: M1 ledger check (iii) skipped; M2 C1 decided under B; M5a pass 4 allowed after 2 h (pre-flight); M6b epoch-2 outcome write-once bypassed; M6c base `--analyze` write-once bypassed (python only; survives -O); M6e ledger overwritten; M13 ledger-only accounting; M18 foreign fingerprint allowed.
SURVIVED: M5b the analysis's 2 h check removed; M7c key-side token in the template not refused; M10 convention A ignores unusable rows (the branch that DECIDES C1); M12 cache-only accounting; M15 C0 (b) (the 26/300 floor) not checked in the analysis; M17 the pass-3 pilot guard removed; M6d ledger created in mode "w"; M20 (equivalent).
Executed on the unmutated code, every substantive survivor's guard FIRES: G7 / G7b (convention A), G8 / G8b (the rung gap), G9 (template token), M15 (a 25/300 floor fails C0), and M17 / M17b (2 of 12 INVALID in the pilot: the pilot refuses, then `--run` refuses: "2 of 12 cached matches are invalid ... 16.7% > 5%"). The survivors are test debt (D3).

## Defects
- **D1 HIGH: a partial or empty pass 4 makes C1 unrecordable.** `epoch2_compute`: `complete = r3 complete and ((r4 complete) or (not r4 and no_rung))`. `analyze_epoch2` then refuses `--no-rung` whenever a pass-4 cache FILE exists. Four paths produce such a cache: `open_cache()` creates the file before the first post, so a fingerprint stop at pass 4's first call leaves 0 rows; a pass-4 pilot that fails its guard leaves 12 rows; a pass-4 `--run` refused by the window re-check (D2) leaves 12 rows; an operator abort. In each case the pass-3 alarm (600 paid calls) can be recorded only by moving the pass-4 cache aside, which is unregistered and makes the readout print "pass 4 not run" falsely. **Required fix:** when pass 3 is complete, write the outcome of record whether pass 4 is absent, empty or incomplete; rung INVALID, C2 UNDETERMINED BY VALIDITY, and the pass-4 row count printed. Keep `--no-rung` as a declaration only when the file is absent. Add selftest cases for 0 and 12 pass-4 rows (outcome written, C1 read, C2 UND).
- **D2 MEDIUM: the pass-4 window is re-measured from now at every launch.** `preflight_epoch2(meta, 4, now=time.time())` runs before the pilot AND before `--run` and any relaunch. The registration defines the rung by pass 4's START ("pass 4 starts <= 2 h after pass 3's last row"), and the analysis reads it that way (max(first row, `started`) - last3). A pilot at 1 h 55 m followed by `--run` at 2 h 01 m is refused, which leaves a partial pass 4 and so D1. **Required fix:** if the pass-4 cache already holds rows, test its `started` (run_meta) against pass 3's last row instead of now; add a selftest case.
- **D3 MEDIUM (test debt).** The survivors above. The most important is M10: the convention-A unusable branch decides C1 and is never exercised by the selftest. Fix together with D1 and D2 (the sha moves anyway): cases for unusable rows under A and B, a failing pass-3 pilot, the analysis's rung gap, the C0 (b) floor, and a key token in the template.
- **D4 LOW (a check that passes without checking).** C0 (a) in `epoch2_compute` is the literal `True` ("verified by freeze_set()"), and `freeze_set` verifies the set hash with `assert`, so under `python -O` a tampered canary_set.json passes and C0 (a) still prints PASS. Fix: recompute set_hash(ms) in C0 (a); raise SystemExit in freeze_set. Until then: never run with -O.
- **D5 LOW (pre-existing, queued CANARY-SELFTEST-ASSERTS).** canary_baseline_selftest.py is assert-based; under -O it prints 28 OK lines and checks nothing (M6c survives -O).
- **D6 LOW.** The canary pilot guard (`cached_guard`) counts cached rows only, so an errored (uncached) pilot match is invisible to it; TRACE counts errors. Fix: count `err` in the pilot's guard, as TRACE does.
- **D7 LOW.** `--override-guard` is still honoured on passes 3 and 4. C0 (e) would then void C1, but the calls are spent. `--pilot N` accepts any N (the registration says 12). Condition: never `--override-guard`; always `--pilot 12`.
- **D8 LOW.** The gate regex `^\s*` consumes a preceding blank line, so a correct READY is refused unless its verdict line sits directly under the title (READY_trace_truncation.md D13; the same code at L608-L629). This file follows that layout. Fix: `^[ \t]*`.
- **D9 LOW.** Registration Support (a) says Kish 1.14; the measured value is 1.160 (the script prints the correction). Nothing moves (C1's point decides).

## What must happen before a READY (delta review, zero calls)
1. The builder fixes D1 and D2 (and, since the sha moves, D3, D4 and D8), commits on the branch, and reports the new blob and sha256-lf16.
2. The delta review then does five things. It diffs against 252f765 by path. It checks that the payload functions are still AST-identical to 7d9a4e2e (ast_cmp.py). It re-runs the dry-runs, which must reproduce anchor 3501e6aef27aad68 and order 20b51354c05c5ad4. It re-runs cb_partial_rung.py, which must write the outcome of record in all four scenarios with C2 UND BY VALIDITY. And it re-runs the mutants M5b, M10, M15 and M17, which must now be KILLED.

## Conditions for the pilot and the run (after the READY that follows the fix)
1. Merge to main byte-identical to the pins the delta READY names (canary_baseline.py, accepted_tests_ledger.py blob:7fb20f64 / sha256-lf16 831af6b1f0ee4697, canary_baseline_selftest.py), by path.
2. From main: `--dry-run --pass 3` reproduces the anchor and order above, [PIN] UNCHANGED at start and end, and pre-flight "would GO".
3. Pass 3: `--pass 3 --pilot 12 --go`, read the guard, then `--pass 3 --run --go`. Pass 4 (the rung): `--pass 4 --pilot 12 --go` immediately after pass 3's last row, then `--pass 4 --run --go`, all inside 7,200 s of pass 3's last row. Never `--override-guard`, never `-O`, never another `--maxtok` or `--temperature`.
4. Do NOT run TRACE-TRUNCATION concurrently. Each guard reads the other test's cache through its immutable DB guard, so a transient non-empty -journal from the other writer is a refused precondition mid-run. It would also dilute "same session".
5. The outcome record prints the three accounting numbers against the day ledger; the post-run reviewer runs the full-payload scan over the stored bodies and re-measures the DEFF from the caches' own cluster sizes (Kish 1.160).
~~~
