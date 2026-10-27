# READY review: JV2-PARALLEL-POSTING on its rebased tip aae49ff (adversarial-reviewer, 2026-09-25; zero calls)

VERDICT: NOT READY. A delta is required in `judge_v2/pool.py` `RateControl.acquire` and in the rc_wire tests, then a delta READY.
Why: EC2 fails at this review. RC1 (the whole-pool pause) and RC3 (max_rpm) fail intermittently. Both come from ONE real defect in the limiter: a worker takes a future token slot and sleeps, and on waking it sends without re-checking the pause or the actual time of the previous send. This is not a test-tolerance problem. It lets queued workers post INSIDE a 429 pause, which is exactly the Azure throttling behaviour the amendment exists to prevent. R2 counts intermittent failures as failures.

Object: branch worktree-agent-a22e907c054aec66f, tip aae49ff (86e88d2 -> 7594243 -> aae49ff). The worktree is at Z:\FAC\TUBerlin\THESIS\TaxoArena\.claude\worktrees\agent-a22e907c054aec66f. Record: docs/judge_v2_program.md, registration L19096-L19239 (bf9d80b) and BUILT record L19378-L19432.
Reviewer scratch: C:\Users\octav\AppData\Local\Temp\claude\Z--FAC-TUBerlin-THESIS-TaxoArena\7c10e5cb-d16b-4a0e-864a-f3a6151d835b\scratchpad\jv2pp_review\ (rc_probe.py, rc_probe2.py, the prototype fixpkg/, inert_rev.txt, rcwire_1..6.txt, i4_i12.txt, jv2_selftest_rev.txt, jv2_selftest_O.txt, pilot_all_rev.txt, scan_v2.py).
Rule 7: every test over 30 s ran with 0 java/python processes (`tasklist | grep -ciE "java|python"` = 0 before each). Every test used a temp fixture or a localhost stub. No DB of record was opened read-write. The only DBs of record opened were in the store scan below, with `mode=ro&immutable=1`, and none had a -wal or -journal file.

## 1. Identity and pins (gate kind: blob and sha256-lf16; the LF rendering is of record; the worktree files are CRLF, sha256-crlf16 printed)

| check | command | got | claimed | result |
|---|---|---|---|---|
| tip / chain | `git log --format='%h %p'` | aae49ff <- 7594243 <- 86e88d2 | same | CONFIRMED |
| range-diff | `git range-diff 9a29715..5373858 86e88d2..aae49ff` | `1: 8fcf7cd = 1: 7594243`, `2: 5373858 = 2: aae49ff` | both '=' | CONFIRMED |
| backup ref | `git rev-parse backup/jv2-pp-pre-rebase-5373858` | 537385864a371c28... | 5373858 | CONFIRMED |
| paths vs main | `git diff --name-only 86e88d2 aae49ff \| wc -l` | 8 (archv2_pilot/{accounting,pilot,selftest}.py, archv2_pilot_k46.py, judge_v2/{pool,pool_inertness,pool_selftest,writer}.py) | 8 | CONFIRMED (none of config/application.yml, .env, .gitignore, report/) |
| D1 base dropped safely | `git diff --name-only 9a29715 86e88d2 -- tools/analysis/{judge_v2,data_v2,archv2_pilot,archv2_pilot_k46.py,archv2_stage1_anchor_draw.py,rejudge_reasoning.py} \| wc -l` | 0 | identical blobs | CONFIRMED |
| main drift since 86e88d2 on those paths | same command, `86e88d2 HEAD` (HEAD d7eca94) | 0 | - | no rebase needed today |
| worktree clean | `git status --short \| wc -l` | 0 | - | CONFIRMED |
| judge_v2/pool.py | `git rev-parse aae49ff:<p>`; `git cat-file -p <blob> \| sha256sum` | blob:a7fdd8a2 / sha256-lf16:588360a0eae82b3d (worktree sha256-crlf16:b8d1d617f28c3786) | a7fdd8a2 / 588360a0 | CONFIRMED |
| judge_v2/writer.py | same | blob:0c9c57c3 / sha256-lf16:f3e2d1cf7447d8ca (crlf16 de1495810a956e73) | 0c9c57c3 / f3e2d1cf | CONFIRMED |
| accounting.py / pilot.py / selftest.py / archv2_pilot_k46.py / pool_selftest.py / pool_inertness.py | same | dd777f32/3012d9bb, 72fb233a/727a26f7, 82ee9cde/8e23ad5f, 91dc8f57/a9ffee1f, ee4e4ace/2697ba64, 3c7a352a/2fc77838 (blob/lf16) | equal to 5373858's | CONFIRMED (the blob at aae49ff equals the blob at 5373858 for all 8) |
| unchanged pins | same | _base.py 6f25e4ce, data_v2/verdicts.py 10138042, rejudge_reasoning.py 1339592a (= main) | unchanged | CONFIRMED |

## 2. Per-claim table

| # | claim | command / script | got | claimed | verdict | sev |
|---|---|---|---|---|---|---|
| C1 | EC1 byte-inertness at --workers 1 (no rate flag), 15/15, with the 4 execution discriminators and the positive control | my own leg A: `git archive 86e88d2 tools/analysis src/main/kotlin/taxonomy/service/TaxonomyArenaService.kt` extracted, then `python tools/analysis/judge_v2/pool_inertness.py --leg-a-root <that>` (12.7 s) | 15 of 15 PASS. Bodies are byte-identical (28, log sha 20a0ca29...). The dump differs only in 2+2 run_meta lines (writer_blob, pins_json; inside pins_json only writer.py changed and pool.py was added). Journal byte-identical (28672 B, 9d453855...). Ledger byte-identical (913933479d32c767). stdout differs by +1 line, `[POOL] workers 1 (sequential path)`. Discriminators: (a) leg A 0 / leg B >0; (b) leg B's writer `__file__` is in the worktree, blob 0c9c57c3; (c) store writer_blob 0c9c57c3; (d) the [POOL] line was printed. Positive control w=4: projection equal, journal v2, launch_bound [(4,)]. I13 on the real legs: REFUSED | 15/15 | CONFIRMED | - |
| C1a | EC1 covers "the build invoked with --workers 1" | read pool_inertness.py L80-L180 | The legs drive a REPLICA of pilot.launch's accounting sequence (Journal.open -> reconcile -> begin_launch -> writer.create -> wrap_call -> writer.run -> append). They do not drive pilot.launch. Through pilot.launch at workers 1 the driver manifest ALSO differs, in `judge_v2_pins` (W._pins() adds pool.py) and in `archv2_pilot_lf16`. These are provenance differences by design, but 2.4 does not enumerate them | - | PARTLY (disclosure) | LOW |
| C2 | pool_selftest: 94 checks, 1 FAIL (RC3), 34/34 mutants killed | relayed log pool_selftest.txt L153: `FAIL RC3 ... \| (11, 10, 12, None)` (token times 11 in one scaled window, stub receipts 10) | 1 FAIL | 1 FAIL | CONFIRMED (the log) | - |
| C3 | RC1 and RC3 fail intermittently | `python tools/analysis/judge_v2/pool_selftest.py --only rc_wire`, 6 runs (rcwire_1..6.txt, 26-27 s each) | RC1 FAIL in runs 1 and 6 (2/6); RC3 0/6 | builder: 8 runs, RC1 3, RC3 2 | CONFIRMED (both flake; combined 14 runs: RC1 5, RC3 2) | BLOCKER for EC2 |
| C4 | CAUSE (builder): acquire spaces the SCHEDULED slots exactly one interval apart, and the recorded times carry wake jitter | rc_probe.py part A: a RateControl alone, max_rpm 10, scale 0.01, 8 threads, 12 tokens, x20 | Minimum recorded gap between consecutive tokens 0.046 s against the 0.060 s interval (recorded times closer than the interval). In addition, the scheduled slots put 11 into a half-open window in 20/20 runs, by float accumulation of `bucket_next += interval` (t10 - t0 < 0.6). | scheduled slots spaced exactly, jitter on the record | CONFIRMED, plus a second cause (float accumulation on the schedule itself) | MEDIUM alone (at real scale the excess is at most +1 request inside a window that is shorter than 60 s by about 16 ms) |
| C5 | NEW, the reviewer's: the whole-pool pause (A-E5.1, "holds every worker's next attempt") is NOT honoured by workers already queued at the bucket | rc_probe.py part B: 4 threads looping `wait_gate(); acquire()` at max_rpm 20, scale 0.01; `on_failure("429", 30)` injected at 0.3 s (scaled pause 0.300 s); x10 | Tokens taken INSIDE the pause, per run: [3,4,4,3,4,3,4,4,3,4], so 10/10 runs violate. Mechanism: `wait_gate()` runs BEFORE `acquire()`, and `acquire()` sleeps to a pre-assigned slot and never re-reads `pause_until`. At real scale (max_rpm 20, interval 3 s, N 8) up to N-1 = 7 requests go out in the ~21 s after a 429, whatever Retry-After says | - | REFUTES A-E5.1 as built | HIGH |
| C6 | RC1's flake is the same defect, not test tolerance | rc_probe2.py: RC1 geometry (max_rpm 6000, scale 0.1, 4 threads, 20 ms "requests"), x20 | 8/20 runs take a token 15-16 ms AFTER the pause was set. That is the Windows timer quantum inside acquire's `Event.wait`, after the gate had already passed. RC1's window starts at the 429 receipt + 30 ms, and the pause is set at about +20 ms (the stub's delay), so +16 ms lands inside the window | builder: cause not stated | CONFIRMED (one root cause for RC1 and RC3) | HIGH |
| C7 | the fix works (reviewer's prototype, NOT applied to the branch) | fixpkg/judge_v2/pool.py = aae49ff's pool.py with acquire replaced (section 4 F1), same probes (rc_probe_fix.py, rc_probe2_fix.py) | part A: minimum recorded gap 0.062 >= 0.060; worst window <= 10 in 20/20. Part B: 0 tokens inside the pause in 10/10 runs. RC1 geometry: 0/20 | - | CONFIRMED (prototype) | - |
| C8 | P-b: an I4 or I12 mutant survives at the first review | `pool_selftest.py --only i4,i12` (217 s) | 11 checks, 0 failed; 3 mutants listed, 3 KILLED in every trial | predicted >= 1 survivor | P-b FAILED | - |
| C9 | EC4: judge_v2 selftest 174, lint 0 | `python tools/analysis/judge_v2/selftest.py` and `python -O ...` | ALL PASS (174 checks), both python and -O; lint_opens 255 files, 0 findings, 17 allowlisted | 174 / 0 | CONFIRMED | - |
| C10 | EC4: archv2_pilot `--part all --main-ref HEAD` 282/0 | `python tools/analysis/archv2_pilot/selftest.py --part all --main-ref HEAD` (4 min 26 s) | 282 checks, 0 failed | 282/0 | CONFIRMED (without --main-ref it refuses at K2 by design until the merge) | - |
| C11 | EC3: E-8 order invariance 100/100 | relayed log L271, L352 | 100 of 100 cells; bind_shift killed 80/80 | 100/100 | CONFIRMED on the log, NOT re-executed (the delta READY re-runs the full selftest) | - |
| C12 | EC5: the dry-run prints the preflight, the [POOL] line and max_inflight, and posts nothing | pilot selftest log L531-L532, L537 (fixture, launch without --go); read archv2_pilot_k46.py L155-L183 (the CLI dry-run: load_transport -> transport_preflight -> ... -> PL.pool_line) | present in the fixture and in the CLI code path | - | CONFIRMED in the fixture; the CLI dry-run on the view of record is the first live run's own READY (gate 3) | - |
| C13 | EC2 under python AND -O | pool_selftest logs: `-O False` only; no `assert` in pool/writer/accounting/pilot (`grep -cE "^\s*assert "` = 0) | -O never run for pool_selftest | required | UNDETERMINED (owed at the delta) | LOW |
| C14 | transport preflight present; every posting instrument loads .env from TAXOARENA_DATA_ROOT | read archv2_pilot_k46.py L155-L158 (`PL.load_transport(); PL.transport_preflight()` before plan/store/journal/ledger, the dry-run included); pilot.py L1162-L1172 (`data_root()` = TAXOARENA_DATA_ROOT, else the main checkout); launch() runs `transport_preflight` first at every workers (diff L1291-L1295), and the I5 mutants preflight_after_pool / preflight_skipped_pooled are killed (log) | present, unchanged from main, ordered before the pool | - | CONFIRMED | - |
| C15 | the wire wrapper sees rr's attempts | rejudge_reasoning.py L127: `urllib.request.urlopen(...)` looked up at call time (module attribute, not a from-import); L142-L163 catches HTTPError / URLError / TimeoutError / ConnectionError only, so PoolRetry(RuntimeError) passes through | rr makes one attempt and never sleeps on the pooled path | A-E5.5 | CONFIRMED (by reading) | - |
| C16 | unsealed judge_v2 verdict DBs at merge (R1 / 2.6) | scan_v2.py: os.walk of the main checkout and worktrees, 2,875 .db seen, 1,974 opened `mode=ro&immutable=1` (pool / cache / >300 MB excluded), stores = a run_meta table carrying writer_blob | 3 distinct stores, each present in main and in this worktree (sha256-equal for run2: 44724d25... and journal 466c0f57...): pilot_k46_verdicts_run2.db 5328/5328 slots with a verdict (COMPLETE); pilot_k46_verdicts.db (main + the incident copy) 0/5328, RETIRED by name (pilot.check_store_path / RETIRED_STORE_NAMES). No -wal or -journal on any. None other | expected: none besides K46's | CONFIRMED | - |
| C17 | E-6: LedgerLock shares JudgeBench's protocol | `git show worktree-agent-a908ab11f8ceee064:tools/analysis/judgebench_side.py` L879-L901 vs pool.py L753-L777 | same file name, O_CREAT\|O_EXCL, 0.2 s poll, 120 s refusal, remove on exit | - | CONFIRMED | - |
| C18 | KeyboardInterrupt "does not wait" | read pool.py `close(interrupted=True)`: `ex.shutdown(wait=False, cancel_futures=True)` cancels only the queued futures. A running `_send` keeps its retry loop (up to 6 attempts, backoff up to 60 s, timeout 120 s), and concurrent.futures joins its worker threads at interpreter exit | after Ctrl-C, up to N workers may keep POSTING retries, and the process may not exit for minutes. The ORPHAN accounting holds (posts counted at reserve), but the pacing intent does not | - | by READING, NOT EXECUTED | MEDIUM |
| C19 | TIME_SCALE / MUTANT are SELFTEST-ONLY module globals | read pool.py L98-L99; PostingPool prints `cfg.line()`, which omits time_scale | a non-unity TIME_SCALE in a live process would shorten every pause and bucket interval silently (rule 11: a guard prints its inputs on every run) | - | CONFIRMED (by reading) | MEDIUM |

## 3. Rulings on the open items (by name)

- D1 (base import 9a29715): ACCEPTED. Moot after the rebase: 86e88d2 carries the same blobs (count 0 above), so the branch carries no file that is not on main except its own 8.
- D2 (launch_bound + invocation_launch_bound): ACCEPTED as disclosed. It strengthens E-2: the launch's N is enforced in the database. Reconcile resolves prior unresolved rows before begin_launch, so the whole-journal unresolved count is the launch's.
- D3 (pool.py pinned through writer._pins(), _base untouched): ACCEPTED. _base.py stays blob 6f25e4ce (verified). The live pin table consumers on the branch are writer._pins, pilot.judge_pins_ok and pilot.launch's manifest, all switched (`grep -rn "pin_table()"`). CONSEQUENCE, recorded: after the merge, mode MAIN-B653B0A is retired and K46's `--analyze` cannot be re-executed from main; reproduce it from 86e88d2 (F5 already ordered it before the merge).
- D5 (NotSent error row at a send-time rollover): ACCEPTED as disclosed. It is the conservative direction: the invocation was journaled and ledgered, and the store shows an errored attempt, so no denominator loses it. It can make a pilot guard fail on a rollover, which is a correct refusal.
- D6 (RATE STOP = the 3rd exhaustion WHILE at bound 1): ACCEPTED as the registrar-recorded reading. The breaker (K 8 consecutive 429 / timeout / network) usually trips first, because two back-to-back exhaustions are 12 consecutive 429s. This is by reasoning, not by execution.
- D7 (--post-workers): ACCEPTED (the driver's --workers belongs to --analyze).
- D8 (hot -journal after a crash): ACCEPTED as disclosed, with a CONDITION on live use. A hot -journal beside a store or journal of record is a FAILED PRECONDITION. Recovery is the data-steward's (backup, a read-write open and close, re-verify), never the operator's. The first live run's launch READY must name that step. The 25/50 count was NOT re-executed here.
- D9 (synchronous=OFF on stress-harness scratch connections; TIME_SCALE): ACCEPTED for the harness, WITH FIX F4 (TIME_SCALE must be printed and fail closed in a launch).
- A-E5.1 (Retry-After both forms, 3 s floor, full-jitter backoff, ONE 429 pauses the WHOLE pool): PARTLY. The parse, the floor and the backoff ceilings are CONFIRMED (the code; RC1 unit checks in the log). "The whole pool" is REFUTED for workers queued at the bucket (C5, C6). Fix F1.
- A-E5.2 (global token bucket, capacity 1, default 20): PARTLY. It is global (the bucket_per_worker mutant is killed), but the spacing is by schedule, not by the actual send (C4). Fix F1. NOTE, not a defect: at the default 20 rpm the pool is capped at 20 attempts/min against the 17.1/min sequential bound (2.8), which is 1.17x at most. The first live N > 1 must register its --max-rpm from the probe (gate 3).
- A-E5.3 (halve on exhaustion / timeout / 3 429s in 30 s, hold 10 s; +1 per clean 60 s): CONFIRMED by reading (pool.py L427-L486) and by the relayed mutants no_halving, no_raise and raise_unbounded.
- A-E5.4 (timeout 120 s; breaker K 8): CONFIRMED by reading. LOW: the breaker also counts "network" failures, beyond the recorded wording "timed out or got 429". This is the conservative direction; bracket the wording.
- A-E5.5 (the pool owns retries; one rr attempt; every HTTP attempt journaled and capped; the ledger stays in invocation units): CONFIRMED (C15; RC2 in the log). Recorded consequence: the HTTP cap is the journal's invocation cap (8,000), so a 429-heavy run can stop at the HTTP-ATTEMPT CAP before all its invocations are posted. This is by design and conservative.
- A-E5.6 (a rate flag at workers 1 means POOLED, journal v2, not claimed inert): CONFIRMED (the driver and pilot.launch code; the pilot selftest log L537; begin_launch refuses a pooled launch on a v1 journal).

## 4. Required fix list (for the engine-coder; branch worktree-agent-a22e907c054aec66f)

F1 [BLOCKER] Rewrite `RateControl.acquire` (pool.py L395-L407) so that the ACTUAL grant instants respect the cap and the pause. Serialise the token takers on a dedicated lock that on_failure never takes. Grant a token only when `now >= pause_until` AND `now - last_grant >= interval`, both re-read after EVERY wake. Record `last_grant = now` at the grant, and take the attempt_times entry from the same value. The prototype below was verified in C7 (0/10 and 0/20 violations; minimum gap 0.062 s against 0.060 s):
```
def acquire(self):
    interval = 60.0 / self.cfg.max_rpm * self.time_scale
    with self.pace_lock:                       # new: threading.Lock(); self.last_grant = -1e18 in __init__
        while True:
            with self.lock:
                t = max(self.pause_until, self.last_grant + interval)
            if t > self._now():
                self._wait_until(t); continue
            with self.lock:
                now = self._now()
                if now >= self.pause_until and now - self.last_grant >= interval:
                    self.last_grant = now; self.attempt_times.append(now); return
```
Optional: also return early (raise PoolRetry or a stop) when breaker_msg is set or an abort flag is raised (F3). WORDING BRACKET (the registrar's): the guarantee is "at most max_rpm attempts LEAVE THE CLIENT in any 60 s window, and no attempt leaves while a pause is in force". An attempt that already left before the 429 was received cannot be recalled (the irreducible in-flight race). Arrival times at Azure also carry network jitter.

F2 [BLOCKER] Tests (pool_selftest.py rc_wire / rc_units):
 (a) RC3, strict on the client side: min gap of `attempt_times` >= interval, and the worst half-open window <= max_rpm. Keep the stub-receipt check with its +1.
 (b) RC1, measured client-side: record the monotonic instant each pause is SET (add it to `pauses`) and require 0 grants in (set, pause_until). Do not use a 30 ms margin on stub receipts.
 (c) NEW RC1b: a 429 injected while >= 3 workers are queued at a BINDING max_rpm (e.g. max_rpm 20 at scale 0.01, 8 workers) gives 0 grants inside the pause.
 (d) NEW mutants, killed in EVERY trial (R2): `gate_before_bucket_only` (aae49ff's acquire) and `bucket_by_schedule` (spacing by pre-assigned slot).
 (e) Repeat rc_wire >= 20 times under python and >= 20 under -O with 0 failures, and print the per-run counts.

F3 [MEDIUM] Interrupt: on KeyboardInterrupt set an abort flag (in `close(interrupted=True)` or in the writer's except) that `_send`'s retry loop and `acquire` check, so no HTTP attempt leaves after Ctrl-C. Selftest: interrupt with N in flight and a stub scripted to 429, and require 0 stub receipts after the interrupt instant (I3's harness).

F4 [MEDIUM] Rule 11: the `[RATE] config` line prints `time_scale`. PostingPool (or pilot.launch) REFUSES `TIME_SCALE != 1.0` and any non-None MUTANT / MUTANT_POOL (pool, writer, accounting, pilot) when the transport wraps `rejudge_reasoning.call_judge_full`. Verify both branches BY EXECUTION.

F5 [LOW] Disclosure for EC1: 2.4 is scored on the harness's replica of launch's accounting sequence. Through pilot.launch at workers 1 the driver manifest ALSO differs in `judge_v2_pins` (+pool.py) and `archv2_pilot_lf16`, by design. Either enumerate these two in the READY text, or add a pilot.launch no-rate workers-1 leg on the fixture that compares the manifest with exactly those two keys differing.

F6 [LOW] After F1-F4: re-derive every pin (pool.py blob, POOL_BLOB_JV2PP in pilot.py, pilot.py's own blob, the archv2_pilot package lf16, and any other changed file), each as blob:/sha256-lf16:, with sha256-crlf16 beside it because the worktree is CRLF. The registrar records a pin bracket before the delta READY names them.

## 5. What the delta READY re-executes

The full pool_selftest under python AND -O (EC2: 0 failed checks, every mutant killed in every trial, the new ones included). rc_wire x20 under each. pool_inertness EC1 against a fresh `git archive` of main's tip (discriminators (a)-(d), the positive control). judge_v2 selftest under python and -O. archv2_pilot `--part all --main-ref HEAD`. The pins of F6. P-c scored there (0 surviving mutants after the delta).

Predictions at THIS review:
- P-a is HELD, with one qualification: EC3 comes from the relayed log and was not re-executed. EC1 was re-executed (15/15). EC4 was re-executed (174 / 174 under python and -O, lint 0, 282/0). EC5 holds in the fixture.
- P-b is FAILED: I4 and I12 give 3 of 3 mutants killed, re-executed.
- P-c is PENDING.
- The falsifier R4 is NOT FIRED: no mutant survives and EC1 has no byte difference beyond the enumerated lines. The build's FAILED check sits in the rate control, which R4's "surviving mutant" does not cover. EC2 simply does not pass yet.

## 6. Merge procedure (after the delta READY; the gates of 2.10 and THE ITEM are unchanged)

1. Preconditions, each shown by its command:
   - F5 lifted (38ec2f3, done).
   - VIEWS-AUDIT-STAGE not landed: queue state "drafted" at this review. If it lands first, rebase and take a delta READY.
   - `git diff --name-only 86e88d2 main -- tools/analysis/judge_v2 tools/analysis/data_v2 tools/analysis/archv2_pilot tools/analysis/archv2_pilot_k46.py tools/analysis/rejudge_reasoning.py | wc -l` = 0. Otherwise rebase and take a delta READY.
   - No judge_v2 poster and no JudgeBench runner running: tasklist shows no python, and no `.judgebench_side_ledger.lock` exists in the main ledger directory.
   - The unsealed-store list of C16 is unchanged: re-run scan_v2.py.
2. Merge BY PATH, only the 8 paths, from the delta tip: `git checkout <delta-tip> -- <8 paths>`. Then `git hash-object` each path and require it to equal `git rev-parse <delta-tip>:<path>` (LF rendering; state the CRLF sha where the working tree differs). Then `git commit -- <8 paths>`. Never -A, never reset. Then `git merge-base --is-ancestor <parent> HEAD`.
3. Post-merge, on main: `python tools/analysis/archv2_pilot/selftest.py --part all` WITHOUT --main-ref must pass K2 (main now carries writer 0c9c57c3 or its delta successor, and pool.py). Also run `python tools/analysis/judge_v2/selftest.py`.
4. Intended consequences, recorded: K46's run2 store REFUSES any relaunch (writer_blob / script_blob; R1). Mode MAIN-B653B0A is RETIRED.
5. Gate (3) stands. The first live use at N > 1, or rate-flagged at N = 1, is registered as that run's own launch parameter, with --max-rpm / --request-timeout-s / --breaker-k citing JV2-RATE-PROBE, and its pilot 12 runs at N.

## 7. Defects list (severity)

- HIGH / BLOCKER: C5 + C6. acquire ignores a pause that starts while a worker is queued at the bucket. At real scale up to N-1 posts go out inside a 429 cool-down. Fix F1, tests F2.
- MEDIUM, and BLOCKER for EC2 through its flake: C4. Bucket spacing is by schedule, with float accumulation and wake jitter. Fix F1.
- MEDIUM: C18. Retries continue after Ctrl-C (by reading). Fix F3.
- MEDIUM: C19. TIME_SCALE / MUTANT are not printed and not fail-closed in a live launch. Fix F4.
- LOW: C1a. The EC1 scope disclosure. Fix F5.
- LOW: C13. -O never run for pool_selftest.
- LOW: the A-E5.4 wording (network failures count toward the breaker).
- LOW: the pins must be re-derived after the delta (F6).

VERDICT: NOT READY. It becomes READY after F1 + F2 (blockers) and F3 + F4, re-executed per section 5 in a delta READY. F5 and F6 are disclosure and pinning, required in the delta record.
