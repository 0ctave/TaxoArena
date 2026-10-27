# DELTA READY 1: JV2-PARALLEL-POSTING on tip 5ece92f (adversarial-reviewer, 2026-09-25; zero calls)

Follows the NOT READY review d32fa75 (docs/reviews/READY_jv2_parallel_posting.md, fix list F1-F6).

VERDICT: READY. The branch is mergeable by path, subject to the merge procedure in section 5. F1-F6 are closed. EC1-EC5 pass. P-c is HELD: 0 surviving mutants after the delta. The falsifier (R4) is NOT FIRED.

Object: branch worktree-agent-a22e907c054aec66f in worktree Z:\FAC\TUBerlin\THESIS\TaxoArena\.claude\worktrees\agent-a22e907c054aec66f. Chain: aae49ff -> 8a3da23 (F1-F5, pool.py re-pinned in pilot.py) -> 94a93ac (test only: RC1b holds the 429 for 250 ms) -> 5ece92f (pool_inertness discriminator (e)). `git status --short | wc -l` = 0.
`git diff --name-only aae49ff 5ece92f` = 4 paths: archv2_pilot/pilot.py, judge_v2/pool.py, judge_v2/pool_inertness.py, judge_v2/pool_selftest.py.
`git diff --name-only 94a93ac 5ece92f` = pool_inertness.py only, so the builder's runs at 94a93ac used the same pool.py.
Main: f447fbb. `git diff --name-only 86e88d2 main -- tools/analysis/{judge_v2,data_v2,archv2_pilot,archv2_pilot_k46.py,rejudge_reasoning.py} | wc -l` = 0.
Reviewer scratch: ...\scratchpad\jv2pp_review\ (rc_probe3.py, delta_runs.sh, delta_out.txt, d_py_1..5.txt, d_O_1..5.txt, d_inert.txt, d_pilot_all.txt, d_jv2.txt, legA2 = `git archive main` at f447fbb). Builder logs: ...\scratchpad\rcx\.

## 1. Pins of record at 5ece92f

Three kinds, per CONTEXT rule 8. blob = `git rev-parse 5ece92f:<path>`. sha256-lf16 is taken over the blob bytes (LF, the rendering of record). sha256-crlf16 is taken over the CRLF rendering, which is what the worktree holds (`git ls-files --eol`: i/lf w/crlf). All re-derived by the reviewer.

| path | blob | sha256-lf16 | sha256-crlf16 | vs aae49ff |
|---|---|---|---|---|
| tools/analysis/judge_v2/pool.py | blob:e9bc770fb16aafa0256e10adbd18c91da237e61e | 978ad89c8632a1b2 | e426aa010d5f1796 | CHANGED (was a7fdd8a2) |
| tools/analysis/archv2_pilot/pilot.py | blob:c0565b57ab1f276048d380a70c6f030f980e2b22 | 8029c6f5e3bf5998 | 4652c4a5df63a357 | CHANGED (was 72fb233a) |
| tools/analysis/judge_v2/writer.py | blob:0c9c57c335151ff198ea45c8bc98ffbd9c23adf2 | f3e2d1cf7447d8ca | de1495810a956e73 | unchanged |
| tools/analysis/archv2_pilot/accounting.py | blob:dd777f32f07b90a90911e71e18ce5560daf7c932 | 3012d9bbd2b2e36a | f727d3ad26612f1f | unchanged |
| tools/analysis/archv2_pilot/selftest.py | blob:82ee9cde74c196970b16d12a57d685bc21ef3e1d | 8e23ad5f15833b23 | 9e8649b7ff55845e | unchanged |
| tools/analysis/archv2_pilot_k46.py | blob:91dc8f577a755192d8d44b53050be60c37ef62ec | a9ffee1fb0353a3b | 1a994badea4531af | unchanged |
| tools/analysis/judge_v2/pool_selftest.py | blob:318c9acaa01afd3b475698312d5d82dc4b8f0ba0 | 90b2fd48d954d356 | c84a1772f015bcee | CHANGED |
| tools/analysis/judge_v2/pool_inertness.py | blob:993c5c6800892900ed63f5c0526c1f57f381dece | c7a6b683145589a5 | 04b54940adc2cf0a | CHANGED |

- ARCHV2_PILOT PACKAGE lf16 (`archv2_pilot.common.package_lf16()` at 5ece92f, CRLF folded) = 00bce6429d6dea64 (was 92fa31eb02aedd94; main carries 098302869a14bd65).
- In-code pin: pilot.py L187 `POOL_BLOB_JV2PP = "blob:e9bc770f..."  # sha256-lf16:978ad89c8632a1b2`. It sits under an insertion-only [RE-PINNED] bracket; the a7fdd8a2 line above it is kept as the record of the build. The value equals the pool.py blob in the table: CONFIRMED.
- Unchanged: `_base.py` 6f25e4ce, `data_v2/verdicts.py` 10138042, `rejudge_reasoning.py` 1339592a.
- The programme does NOT yet carry these pins (`grep -c e9bc770f docs/judge_v2_program.md` = 0). This is merge step 5.4.

## 2. Per-claim table

| # | claim | command | got | verdict |
|---|---|---|---|---|
| D-1 | F1: grants respect the cap and the pause | rc_probe3.py against 5ece92f's RateControl (clock co_names = time.perf_counter) | A (max_rpm 10, scale 0.01, 8 workers, x20): worst window > 10 in 0/20, min gap 0.06019 s against the 0.060 interval. B (4 workers queued, 429 with RA 30, x10): grants inside the pause [0,0,0,0,0,0,0,0,0,0]; the build gave [3,4,4,3,4,3,4,4,3,4]. C (RC1 geometry, x20): 0 runs with a grant inside the pause; the build gave 8/20. D (abort with 8 workers, x10): 0 grants after abort() in 10/10 | CONFIRMED |
| D-2 | F2: rc_wire 20/20 under python and 20/20 under -O, 8/8 mutants killed | builder's summary.txt (40 lines rc=0, "16 checks, 0 failed", "8 listed, 8 KILLED"), plus my runs: `pool_selftest.py --only rc_wire,i3b,f4`, 5 under python and 5 under -O | Mine: 10/10 runs with 22 checks and 0 failed, 9 mutants listed and 9 KILLED each time (rc_wire 8 + I3b abort_ignored). RC1 (0, 1, 13); RC1b 0 inside, min gap >= interval, witness waiting >= 3; RC3 strict gap. Combined with the builder: 30/30 python, 25/25 -O, 0 failures | CONFIRMED |
| D-3 | full pool_selftest: 103 checks, 0 failed, 37/37 mutants, python and -O | builder's full_py.txt / full_O.txt: count of PASS lines = 103, FAIL = 0 in each; tail "37 listed, 37 KILLED in every trial"; headers `-O False` / `-O True` | as claimed | CONFIRMED on the logs; NOT re-executed in full (the coordinator's subset instruction, rule 7). The changed parts (rc_wire, I3b, F4) were re-executed (D-2) |
| D-4 | judge_v2 selftest 174/174 under both | builder's jv2_py/jv2_O; mine `python tools/analysis/judge_v2/selftest.py` (d_jv2.txt) | ALL PASS (174 checks) | CONFIRMED (python re-executed; -O from the log; writer.py is unchanged since the first review, where I ran -O) |
| D-5 | archv2 selftest `--part all --main-ref HEAD` 282/0 | mine (d_pilot_all.txt, 4 min 21 s) | 282 checks, 0 failed | CONFIRMED |
| D-6 | EC1 16/16; leg B executed the new code | mine: `pool_inertness.py --leg-a-root legA2` (`git archive main` at f447fbb; main's writer blob 6db4ab32) | 16 of 16 PASS. Discriminator (e): leg B imported pool.py at HEAD blob e9bc770f with {PoolAborted 3, abort_ev 6, live_guard_reasons 3, pace_lock 2}, and leg B' printed the `[RATE] live guard:` line and time_scale. The store differs only in writer_blob / pins_json (pool.py B blob e9bc770f). Journal bytes 9d453855, ledger 913933479d32c767 and bodies 20a0ca29 are all equal. The SCOPE (F5) line prints the manifest differences (judge_v2_pins, archv2_pilot_lf16 098302869a14bd65 -> 00bce6429d6dea64) | CONFIRMED |
| D-7 | F3: no attempt after Ctrl-C; the wire stays installed until the last worker leaves | read pool.py close() / _enter_send / _leave_send / acquire _check_abort; I3b in my 10 runs | I3b: "0 stub receipts after it (0 of 4), 4 unresolved, ledger == journal, wire uninstalled by the last worker"; abort_ignored KILLED 10/10 | CONFIRMED |
| D-8 | F4: the live guard is printed every run and both branches are executed | F4 (1)-(4) in my 10 runs; `grep -rnE "^MUTANT[A-Z0-9_]*\s*=" judge_v2 archv2_pilot data_v2 archv2_arena` = 14 switches, 0 of them non-None by default | Refused under TIME_SCALE 0.001 and under a MUTANT at 1.0 (0 invocations, 0 requests). Admitted at 1.0 with no switch. The wire backstop refuses non-loopback at 0.5, admits at 1.0, and admits loopback at 0.5. Not vacuous: no production default trips the guard, and the refusal branch is executed | CONFIRMED |
| D-9 | F5: EC1 scope disclosed | d_inert.txt SCOPE line | printed with both manifest keys and their values | CONFIRMED |
| D-10 | F6: pins re-derived | section 1 | all equal the builder's (pool e9bc770f / 978ad89c8632a1b2; pilot c0565b57 / 8029c6f5e3bf5998; package 00bce6429d6dea64; writer 0c9c57c3 unchanged) | CONFIRMED |
| D-11 | the builder's extra F3 finding: an interrupt uninstalled the wire while workers were retrying, so they fell back to rr's own retry loop | `git show aae49ff:tools/analysis/judge_v2/pool.py` L730-L732 (`ex.shutdown(wait=False)` then `wire.uninstall()` straight away) together with L590-L598 (a running worker's retry loop calls transport.send -> rr.call_judge_full -> the now-real urlopen, which has rr's 6 attempts and sleeps, with no body check and no HTTP count) | a real defect in the build, now closed by the deferred uninstall (D-7) | CONFIRMED (by reading and by I3b) |

## 3. Rulings on the builder's deviations

1. Clock is time.perf_counter, not time.monotonic: ACCEPTED. monotonic ticks at 15.6 ms on this Windows Python. Every rate-control time (pause, grant, burst, raise, abort) uses `_now()`; `grep -n monotonic pool.py` finds only comments. The stub's receipt clock was switched too, so it is consistent.
2. RC1's 429 moved to the 4th slot: ACCEPTED. It gives the main thread reservations to make during the pause, which makes the check stronger. The measurement is client-side, as F2 (b) required.
3. "Live" means rr.call_judge_full AND a non-loopback host, plus a wire-level refusal: ACCEPTED. The PostingPool check can be bypassed by wrapping rr, but the wire backstop refuses ANY non-loopback urllib request under a selftest setting (F4 (4), executed). Residual, LOW: the sequential path (workers 1, no rate flag) is not pooled, so it carries no live guard over the MUTANT switches. That is the pre-existing pattern of the project, unchanged by this build.
4. install() refuses while a previous wrapper is installed; new printed lines (live guard, [POOL] INTERRUPTED): ACCEPTED. It is fail-closed, and the lines are printed on every pooled run (rule 11).
5. EC1 went from 15 to 16 (discriminator (e)): ACCEPTED. It is required by the inertness-vacuity rule for a changed pool.py, and it is executed (D-6).
6. Two inherent races (a grant just before a 429 or abort leaves just after it; an attempt in flight completes after Ctrl-C, bounded by the 120 s timeout and never re-sent): ACCEPTED. They are exactly the irreducible race named in the first review's F1 wording and are disclosed in the pool.py bracket.
7. Rule-7 overlap with d9bm_run.py: DISCLOSED, not a defect of this build. The builder's rule7() gate (rcx/all.sh) checks only at the START of each step, so a foreign process that starts mid-step overlaps. The same happened once in MY run: python 37560 appeared during my first python run (18:10:37-18:11:16; "foreign-at-end 1" in delta_out.txt), while every start gate had been clean. Our steps are scratch-only (temp fixtures, a localhost stub, zero DB of record) and affect only CPU timing. Whether a D9/D9b leg's admitted-PID list must record the overlap is for that test's reviewer. The builder's overlap times are in rcx/summary.txt; mine are 18:10:37-18:11:16. A future gate should also sample at step end (as delta_runs.sh does) and print the result.

Carried from the first review, unchanged: D1-D3 and D5-D9 ACCEPTED. D8 (hot -journal after a crash) keeps its condition that the first live run's launch READY names the data-steward's recovery step. A-E5.1 and A-E5.2 are now CONFIRMED (D-1, D-2). A-E5.3-A-E5.6 CONFIRMED.

Predictions: P-a HELD and P-b FAILED (both scored at d32fa75). P-c HELD: 0 surviving mutants after the delta (37/37 in the builder's full logs; 9/9 in each of my 10 subset runs). Falsifier R4 NOT FIRED.

## 4. Remaining notes (no blocker)

- LOW: the full 103-check selftest was not re-executed by the reviewer (rule-7 window; the coordinator's subset instruction). Coverage: the builder's full logs under python and -O, plus my re-execution of every changed section.
- LOW: at the default --max-rpm 20 the pool is capped near 1.17x the sequential rate. Gate (3) makes the first live N > 1 run register its own --max-rpm, citing JV2-RATE-PROBE.

## 5. Merge procedure (updates section 6 of the first review)

1. Preconditions, each shown by its command and printed in the merge record:
   - F5 lifted (38ec2f3).
   - VIEWS-AUDIT-STAGE not landed (queue state "drafted" at this review). If it lands first, rebase and take a delta READY.
   - `git diff --name-only 86e88d2 main -- tools/analysis/judge_v2 tools/analysis/data_v2 tools/analysis/archv2_pilot tools/analysis/archv2_pilot_k46.py tools/analysis/rejudge_reasoning.py | wc -l` = 0. Otherwise rebase and take a delta READY.
   - No judge_v2 poster and no JudgeBench runner running: `tasklist | grep -ciE python` = 0 for posters, and no `.judgebench_side_ledger.lock` in the main ledger directory.
   - No rule-7 leg running (no git write touches src/ inside a window).
   - The unfinished-store list is unchanged: re-run scratchpad\jv2pp_review\scan_v2.py. Expected: K46 run2 complete (5328/5328); the two retired stores have 0 verdicts.
2. Merge BY PATH the 8 paths from 5ece92f, no others:
   `git checkout 5ece92f -- tools/analysis/archv2_pilot/accounting.py tools/analysis/archv2_pilot/pilot.py tools/analysis/archv2_pilot/selftest.py tools/analysis/archv2_pilot_k46.py tools/analysis/judge_v2/pool.py tools/analysis/judge_v2/pool_inertness.py tools/analysis/judge_v2/pool_selftest.py tools/analysis/judge_v2/writer.py`
   Then, for each path, require `git hash-object <path>` = the blob in section 1 (LF rendering, blob kind). If the working tree converts to CRLF, also print `sha256sum` against the crlf16 column.
   Then `git commit -- <the 8 paths>`: never -A, never reset, and `git show --name-only HEAD | wc -l` must show exactly the 8.
   Then `git merge-base --is-ancestor <parent> HEAD`.
3. Post-merge, on main, with no foreign java/python:
   - `python tools/analysis/archv2_pilot/selftest.py --part all` WITHOUT --main-ref must pass K2 (main now carries writer 0c9c57c3 and pool.py e9bc770f): 282/0.
   - `python tools/analysis/judge_v2/selftest.py`: 174/174.
   - `python -c "import sys; sys.path.insert(0,'tools/analysis'); from archv2_pilot import common as C; print(C.package_lf16())"` on main = 00bce6429d6dea64.
4. Registrar, in the merge record: record the pins of section 1 (all three kinds) in docs/judge_v2_program.md. Mode JV2-PARALLEL-POSTING becomes the admitted K2 mode; MAIN-B653B0A is RETIRED. K46's run2 store REFUSES any relaunch (writer_blob / script_blob), which is intended. K46's `--analyze` is reproducible only from a checkout of 86e88d2.
5. Gate (3) unchanged. The first live use at N > 1, or rate-flagged at N = 1, is registered as that run's own launch parameter (--post-workers, --max-rpm, --request-timeout-s, --breaker-k), citing JV2-RATE-PROBE. Its pilot 12 runs at N. Its launch READY names D8's data-steward recovery step and checks that the `[RATE] live guard:` line reads "LIVE, ADMITTED" with time_scale 1.0 and no switches.

VERDICT: READY.
