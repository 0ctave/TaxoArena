# READY review: JV2-RATE-PROBE (branch jv2-rate-probe, tip 261ce02)

## VERDICT: READY. MERGEABLE by path, with the 3-way merge on the ledger module. Launch conditions C1-C8 below. No blocker.

Posting on 2026-09-25 was admissible under the registration (X2 OK, K46 had 0 unresolved, and the day cap fit at 5,354 + 400 = 5,754 of 14,000). It is no longer feasible, because this review closes at 23:58 local. The first possible posting day is therefore 2026-09-26, which is also JudgeBench's earliest day. Under A6 the orchestrator must give that day to one test or the other (C2).

Reviewer: adversarial-reviewer. Zero judge calls. The branch was not modified. No DB of record was opened read-write. The dry-run's before/after sha256 and mtime are equal (see item 9).

## Pins of record

Hash kinds are named per CONTEXT rule 8. The LF rendering is the rendering of record.

| path | blob (LF, of record) | sha256-lf16 | sha256-crlf16 | worktree rendering |
|---|---|---|---|---|
| tools/analysis/jv2_rate_probe.py (NEW) | blob:5f075d18f1e04638d5b33b3e35c4077066a21d6d | 553fd699a7bbe279 | f1191d61bba8e6c5 | LF |
| tools/analysis/jv2_rate_probe_selftest.py (NEW) | blob:7c6fd9c97f9560c0610fe75097efd6c29c43dc51 | d37df4ab2e7be3e1 | e81c3aca6979e1b7 | LF |
| tools/analysis/accepted_tests_ledger.py (+1 line) | blob:b90e64dc93458daeb6102d47279bfd7640c3e9e0 | e0ca9d9ade161f7f | f3611719d7fdb00e | CRLF (file sha256 = crlf16) |
| tools/analysis/judge_v2/pool.py (unchanged) | blob:e9bc770fb16aafa0256e10adbd18c91da237e61e | 978ad89c8632a1b2 | e426aa010d5f1796 | CRLF |

- Branch tip: 261ce02ef71e7f5485487fc136181573553651b6. Merge base with main: 7e71cbafd3279074a92590c48acd5fd39218a8d0.
- `git diff --stat main...jv2-rate-probe`: 3 files, +2,803 / -0.
- `git diff --stat cd57564 261ce02`: only the 2 probe files. The RC patch is Python-only.
- The ledger module on main is blob:fabb66a8b3d73a3c31053170145c3be7b8e54975, the same as the merge base (`git log 7e71cba..main -- tools/analysis/accepted_tests_ledger.py` returns 0 commits, main at 93cc7de). The branch diff against the base is exactly the one line `CEILINGS["JV2-RATE-PROBE"] = 400 ...`.
- Plan sha (for --expect-plan-sha): b2177cd172eacab59df2e72b6276fe25768c8fc610d623e5051e90b96f09f86f. It is unchanged from the pre-patch plan, as RC0 expected. I recomputed it from the 398 bodies with my own json.dumps and got an equal value.
- K46 run2 store (read from a copy only; see item 3):
  - posted-body q10 / q50 / q90 = 4,581 / 5,369 / 6,805 bytes;
  - median completion_tokens 254.0;
  - the system turn sha256 d0c524bbd66b5a5e9781f049c93584401f27ed503742c687733afa03a2a7171e is identical on all 5,328 bodies and equals the launch manifest's value;
  - template sha256:0d064ee2..., rubric sha256:67f843eb....

## Per-claim table

| # | claim | result | command / evidence | mine vs claimed | sev |
|---|---|---|---|---|---|
| 1 | selftest 132 checks / 0 failed, 30/30 mutants killed (25 by check, 5 by exception), python and -O | CONFIRMED | `python tools/analysis/jv2_rate_probe.py --selftest` (252 s); `python -O ... --selftest` (253 s) in the branch worktree | 132/0 and 30/30 under both; the 5 killed by exception are ledger_skip, inflight_over, optimize_ok, x2_off and x1_off | - |
| 2 | real dry-run at 0 calls: preflight OK, LIVE ADMITTED, plan sha b2177cd1..., <= 398 of ceiling 400, X1/X2 OK on 09-25, (iii) 5,354 + 400 = 5,754 | CONFIRMED | `python tools/analysis/jv2_rate_probe.py --dry-run` (branch worktree, 23:0x on 09-25); log in scratchpad rp/dryrun.txt | every figure equal; urlopen invoked 0 times; content gate 0 hits on 398 stems against 11,609 MMLU-Pro keys and 20,535 union keys | - |
| 3 | K46 quantiles, system-turn equality, median tokens | CONFIRMED | my own script on COPIES of pilot_k46_verdicts_run2.db and its .launch.json (opened mode=ro in the scratchpad); originals sha256 44724d25... / 466c0f57... unchanged | 4,581 / 5,369 / 6,805; 254.0; system sha d0c524bb on 5,328 of 5,328 bodies; body keys model / max_tokens / messages (no temperature) | - |
| 4 | the probe's bodies: exact size targets, K46's system turn, cap 8192, model, no temperature, all distinct | CONFIRMED | built the plan through build_plan and checked all 398 bodies independently (json parse, sha, lengths) | 0 defects of 398; classes q10/q50/q90 = 134/132/132; 398 distinct bodies; every user turn carries its "(item i)" tag and the key's final line | - |
| 5 | admissibility (a) as amended by A3 (inadmissible iff share > 2% AND > 1 HTTP 429), (b) 0 exhausted, (c) p95 <= 1.5 x p95(S1), S1 exempt, S6 not exempt, no cap, an aborted step inadmissible | CONFIRMED at the boundaries | rp/bnd.py (pure calls to admissible / decide / score) | 1/25 admitted; 2/26 refused; 2/100 = 2.00% admitted; 2/99 refused; 3/150 admitted; 4/199 refused; 1 exhausted refused; p95 = 1.5 x 3.7 (float) admitted; 6.0000001 vs 6.0 refused; S1 at p95 100 s admitted; S6 at 6.01 refused; aborted refused | - |
| 6 | C1 literal 1.3x rule; RC5 (a) S6 drop to the largest step below N*'s that qualified, else S1; G from the ramp step | CONFIRMED | rp/bnd.py | S2 = 1.3x exactly qualifies; S2 at 1.299x not, then S3 >= 1.3x S2 gives N* = 4 and G = 2.0; S6 inadmissible drops to 1 (S2 unqualified), 2 (S2 qualified), 8 (N* 12, S4 qualified) or 4 (S4 at 1.2x unqualified); S6 admissible keeps 12 | - |
| 7 | falsifier literal: rate(S3) >= 50, share <= 2% literal, 0 exhausted, p95 <= 1.5 x p95(S1) | CONFIRMED | rp/bnd.py | 50.0 fires, 49.99 does not; 1/50 = 2.00% fires; 1/49 = 2.04% does not; 1 exhausted does not | - |
| 8 | P1 (i)+(ii) and R4 (ii) NOT OBSERVED when S3 is not posted; P2 at the first inadmissible step, UNDETERMINED if none; P3 [3.0, 4.5] and 0 exhausted | CONFIRMED | rp/bnd.py | P2 at exactly 10% HELD; P3 at median 4.5 HELD; S1 inadmissible at 3/27 gives N* = 1 and P2 scored at S1 (11.1%, HELD) | - |
| 9 | the dry-run writes nothing | CONFIRMED | sha256 + `ls --full-time` before/after of the K46 run2 store (4 files), day_calls_2026-09-25.json, mmlu_pro_dataset_cache_v2.db(-shm/-wal), multicorpus_cache_v1.db(-shm/-wal) | `diff` equal on both; experiment_results/jv2_rate_probe absent after the run; branch worktree `git status --short` 0 lines | - |
| 10 | the preflight prints booleans plus the deployment name only; no key, host or URL | CONFIRMED | a script read .env and tested `host in dryrun.txt` and `key in dryrun.txt`, printing booleans only | host False; key False; key[:8] False | - |
| 11 | wire counter: every HTTP attempt recorded, 429s visible | CONFIRMED | my mutant W1 (the HTTPError branch stops appending its record) | KILLED, 6 failing checks | - |
| 12 | api-key never recorded | CONFIRMED | my mutant K1 (the request headers stored into the attempt row) | KILLED ("wire: the key is not in the probe DB") | - |
| 13 | my other mutants | PARTLY | rp/mut.py (in-memory source mutation; the whole TESTS list; 12 mutants) | KILLED: C1 compared against S1 instead of the previous step; send-time rollover removed; p95 rank off by one; X1 admits every posting script. SURVIVED: see D1 | MEDIUM |
| 14 | F6: V5's bytes leg cannot fail | CONFIRMED | plan-level median over the 398 slots | median user bytes 2,634 = K46 q50 user bytes (5,369 - 2,735) exactly; the cyclic classes make any other median impossible. V5 / P5 are carried by the completion-token leg alone (band 254 +-30% = [177.8, 330.2]); that leg can fail | LOW (disclosure) |
| 15 | Support section present, arithmetic reproduces | CONFIRMED | recomputed | CP upper at 0 of n: 0.1173 / 0.0798 / 0.0605 / 0.0457 / 0.0387 / 0.0198 (cp_upper equals 1 - 0.05^(1/n) to 4 dp); MDE P(<= 1 of 48 given p = 0.10) = 0.0403; A3 disclosure 0.080 -> 0.293 (S1), 0.023 -> 0.113, 0.0064 -> 0.040. DEFF: NO SOURCE, declared = n per step, n_eff = 1; no SE claimed. NON-VACUOUS as a screening rule | - |
| 16 | day cap: 5,354 used + 400 fits within 14,000 | CONFIRMED | read day_calls_2026-09-25.json | ARCH-V2-PILOT-K46 5,352 + ARCH-V2-INDUCE-RUBRIC-3 2 = 5,354; 5,754 of 14,000. The atl (iii) combined statement stays <= 14,000: 7,892 with the probe planned; 9,432 if JudgeBench's full 1,540 follows a full probe | - |
| 17 | K46 0 unresolved | CONFIRMED | K46 run2 journal copy | 5,328 invocations, 5,328 resolutions (all RETURNED) | - |
| 18 | ledger module not in K46's pin set (R7) | CONFIRMED | grep of archv2_pilot/pilot.py and outcome.py: K2 / judge_pins_ok pin judge_v2/* files only; `grep -rn fabb66a8 tools/` finds only .pyc files | 0 runtime pins of accepted_tests_ledger.py | - |
| 19 | F8 inertness: every atl.guard caller's (iii) line gains "+ JV2-RATE-PROBE 0"; nothing else changes | CONFIRMED BY EXECUTION | scratch worktree at main 7c6c588: 8 atl-importing selftests run, then the 3 blobs applied and the 8 re-run (rp/st_base, rp/st_patched) | identical rc on all 8: archv2_pilot 282/0, judgebench_side rc 0, pool_selftest 103/0 with 37/37 mutants killed, induce_run_3 556 ALL PASS, canary epoch2 PASS, trace PASS; induce_run and induce_run_2 rc 1 with identical last lines (F7). Execution witness: "JV2-RATE-PROBE" occurs 0 times in every baseline log and 4 / 11 / 29 / 14 times in the patched judgebench / induce3 / canary / trace logs | - |
| 20 | F7 pre-existing | CONFIRMED | baseline at main | induce_run_selftest refuses on "the induction prompt constants are not the registered ones"; induce_run_2_selftest on "INDUCTION_VERSION jv2-induce-5 is not the registered jv2-induce-4"; identical after the patch | LOW (known red) |
| 21 | Gradle 451 tests / 2 known, run at cd57564 | NOT RE-RUN; inert by count | the patch cd57564..261ce02 is Python-only (2 files); the only Gradle scanner of tools/analysis/*.py is NoIsReservedInSourceTest, and `grep -cE` on its 6 tokens in the 3 merged paths gives 0/0/0 | - | - |
| 22 | K46 run2 latency figures (builder: median 3.63 s, p95 10.68 s, 5.46% > 10 s) | PARTLY | my script on the journal copy (resolution.ts - invocation.ts, nearest-rank) | median 3.634, p95 10.708 (gap +0.03 s), 5.50% > 10 s (gap +0.04 pp). The tail is a regime, not noise: the share > 10 s is 0.0-2.3% in the hours 05-09Z and 10.2% / 82.4% / 87.8% in 10Z / 11Z / 12Z; P(next > 10 s given > 10 s) = 0.754 against 0.055 unconditional | LOW |

## Reachability (the registrar's practice)

Scope: after A2 as revised and A3, on a day like 09-25, from K46 run2's journal (a copy).

Model: no degradation. Each step's invocation latencies are drawn from K46. The step's rate is simulated with N servers plus 12 ms of reservation overhead. The script's own `admissible` / `decide` / `score` are executed. There are no 429s: 09-25 read "mostly 200" and K46 has no HTTP-level record. Script rp/sim_rp.py and rp/sim2.py; R = 20,000 for the whole day and 10,000 per regime.

| null (no degradation) | P(S1 adm.) | P(S2 adm.) | P(reach S3 adm.) | P(falsifier fires) | P(N* = 1) | P(P1 HELD) | mean rate S1 / S3 |
|---|---|---|---|---|---|---|---|
| whole-day iid mixture | 1 (exempt) | 0.571 | 0.446 | 0.255 | 0.499 | 0.440 | 13.4 / 49.1 |
| contiguous timeline (block) | 1 | 0.968 | 0.924 | 0.884 | 0.058 | 0.039 | 16.3 / 62.7 |
| morning regime 05-09Z (median 3.51 s) | 1 | 0.916 | 0.891 | 0.873 | 0.085 | 0.086 | 16.2 / 62.0 |
| late 10-12Z (median 5.43 s) | 1 | 0.841 | 0.800 | 0.000 | 0.177 | 0.206 | 6.9 / 25.4 |
| degraded 11-12Z (median 16.46 s) | 1 | 0.910 | 0.885 | 0.000 | 0.091 | 0.115 | 3.4 / 13.1 |

Reading:

1. **S1.** S1 is admissible with probability 1 on latency, because it is exempt from (c). The F1 vacuity is removed.
   - On 429s: S1 is refused iff it carries 2 or more HTTP 429s among its roughly 24 attempts. P = 0.024 / 0.083 / 0.383 / 0.708 at a per-attempt 429 rate of 1% / 2% / 5.5% / 10%.
   - On a 09-24-like day (22% or more) S1 is refused with probability 0.98. That is the registered behaviour.
2. **(c) under a stationary regime.** At 1.5 x p95(S1), (c) stops the ramp at S2 without any degradation 8-16% of the time. It stops it before S5 13-21% of the time. P1 then HOLDS 9-21% of the time with no limiter effect.
   - The whole-day iid figure (P reach S3 = 0.446) mixes a 3.5 s regime and a 17 s regime that no 15-minute probe spans, so it is pessimistic. The contiguous-timeline figure (0.924) is the realistic one.
   - This is disclosed, not a defect: the factor is the registered one, as ruled on O2.
3. **The falsifier is reachable only on a fast, 429-free day.**
   - Under perfect 4x scaling, rate(S3) is about 4 x rate(S1). The falsifier's 50/min therefore needs rate(S1) >= 12.5/min, i.e. a mean invocation latency of 4.8 s or less. K46's whole-day mean is 4.595 s, the knife edge.
   - Its literal share <= 2% on 49 or more attempts needs ZERO HTTP 429s in S3: P = 0.62 / 0.38 at 1% / 2% per attempt.
   - On a slow day (late / degraded rows) P(fires) = 0.000 under perfect scaling, so a NOT FIRED there carries no information (condition C6).
   - This is not structural impossibility (0.87 in the morning regime), but it is reachable only on the day's conditions.
4. **V5.**
   - The bytes leg cannot fail (claim 14).
   - The completion-token leg is real. K46's unparsed share is 3 of 5,328 = 0.056%, so the pilot-12 guard's void risk is P(>= 1 of 12) = 0.7%.
5. **P1 (ii).** On a slow day, rate(S3) < 35/min holds from latency alone (degraded: rate(S3) is about 13/min). P1 then mostly FAILS on (i), because scaling makes N* = 12 (N* = 12 in 70.5% of degraded draws). Disclosed.

## Defects

**D1 (MEDIUM, test gap; the code is correct by my execution).** Four of my non-equivalent mutants survive the selftest (rp/muts.txt):

- F_rate_bar_35: the falsifier fires at >= 35/min instead of 50. No check exercises the falsifier's rate bar.
- WALL_one_span: S1's wall taken as one span over the pilot and the run launches, not as the sum of the segments (A5 (vi)). This changes rate(S1), and with it G and C1.
- B1_exhausted_bar_1: (b) admits 1 exhausted invocation. Mostly masked by (a), but not in S6 when an exhausted invocation's earlier attempts were 5xx.
- AB_exhausted_not_accumulated: the within-step 3-exhausted abort. Near-equivalent, because 10 HTTP 429s fire first.

The real code is right at each of these points:
- 49.99 does not fire and 50.0 does (bnd.py);
- the S1 wall over two launches one hour apart = 96 s and rate 15.0/min (sum of segments; direct step_stats call);
- 1 exhausted is inadmissible (bnd.py).

Two further survivors are equivalent and not defects:
- PG_raised_vanish: `returned == 12` already excludes a raised invocation;
- V3_unresolved_ignored: the outcome of record is written only when `complete`, which already requires 0 unresolved.

**Fix (recommended, not required before the launch):** add the three checks to the selftest. This changes only the selftest blob, not the script or the plan sha. The post-run review must recompute rate(S1) from the probe DB per launch segment and the falsifier from its bar (C7).

**D2 (MEDIUM, disclosure).** Falsifier reachability depends on the day (reading 3). → condition C6.

**D3 (LOW).** The 10-HTTP-429 within-step abort counts only the CURRENT launch's wire records (`Wire.count_429`). After a relaunch in the middle of a step, the 429s of the earlier launch are not counted toward the abort threshold; exhausted invocations are counted from the DB. Admissibility (a) reads all attempts from the DB, so no decision changes; only when the abort fires. Disclose if a step spans two launches.

**D4 (LOW).** In a launch, the [OPT] line prints before the TRANSPORT PREFLIGHT line. Registration 1.2 says the preflight is "printed before anything else". Nothing is read or written between the two lines, and the dry-run prints the preflight first. No fix required.

**D5 (LOW).** A date change inside the milliseconds between a pilot reservation and its send leaves a NOT_SENT pilot slot that is never re-posted. The pilot guard then reads 11 of 12 RETURNED, fails, and voids the probe (V4). → condition C3.

**D6 (INFO).** The within-step 3-exhausted abort is almost always pre-empted by the 10-HTTP-429 abort: 3 exhausted invocations take 18 attempts, 3 or more of them 429. Registered as written; no change.

No BLOCKER and no HIGH. Also checked, with no finding:
- the wire refuses a body whose sha differs from the slot's before it leaves (body_unchecked is killed; `_send` also asserts rr.payload_bytes);
- temperature is absent on all 398 bodies;
- the journal is v2 with max_inflight 12, a per-step launch_bound = N, and cap 400; ledger == journal at the start (reconcile) and the end (check_equal); the append is under POOL.LedgerLock;
- the outcome is write-once (mode "x"); --run refuses without the pilot PASS file; -O refuses;
- X1 runs at the launch and at every step boundary, is recorded before refusal, and is re-read by V1;
- X2 refuses a JudgeBench day at the launch and at every boundary, and --analyze re-reads every posting day, so a JudgeBench row added later voids the probe (V1).

## Merge procedure (orchestrator; by path; never `git add -A`, never a bare `git commit`)

On main (HEAD 93cc7de or later), with no foreign staged file (`git diff --cached --name-only` empty or unrelated, and `git commit -- <paths>` in any case):

1. `git show 261ce02:tools/analysis/jv2_rate_probe.py > tools/analysis/jv2_rate_probe.py`
2. `git show 261ce02:tools/analysis/jv2_rate_probe_selftest.py > tools/analysis/jv2_rate_probe_selftest.py`
3. Do the 3-way merge of the ledger module (R7, "never by path restore"):
   - `git show 7e71cba:tools/analysis/accepted_tests_ledger.py > $T/base.py`
   - `git show 261ce02:tools/analysis/accepted_tests_ledger.py > $T/theirs.py`
   - `git show HEAD:tools/analysis/accepted_tests_ledger.py > $T/ours.py`
   - `git merge-file -p $T/ours.py $T/base.py $T/theirs.py > tools/analysis/accepted_tests_ledger.py` (exit 0, no conflict)
4. Check the ledger blob:
   - `git hash-object tools/analysis/accepted_tests_ledger.py` must print b90e64dc93458daeb6102d47279bfd7640c3e9e0 while main's blob is fabb66a8.
   - If main's blob has moved, the result will differ. It is then accepted only if `git diff HEAD -- tools/analysis/accepted_tests_ledger.py` is exactly +1 / -0, that line.
5. `git add tools/analysis/jv2_rate_probe.py tools/analysis/jv2_rate_probe_selftest.py tools/analysis/accepted_tests_ledger.py`, then `git commit -m "..." -- <the same 3 paths>`.
6. Check the merged blobs:
   - `git rev-parse HEAD:tools/analysis/jv2_rate_probe.py` = 5f075d18f1e04638d5b33b3e35c4077066a21d6d;
   - `...jv2_rate_probe_selftest.py` = 7c6fd9c97f9560c0610fe75097efd6c29c43dc51;
   - `...accepted_tests_ledger.py` = b90e64dc (or the step-4 exception);
   - `...judge_v2/pool.py` = e9bc770fb16aafa0256e10adbd18c91da237e61e;
   - `git show --name-only --format= HEAD | wc -l` = 3.
7. Ancestry: `git merge-base --is-ancestor <READY commit> HEAD` exits 0.

Post-merge, on main (run-operator; zero calls):

- M1: `python tools/analysis/jv2_rate_probe.py --selftest` and `python -O tools/analysis/jv2_rate_probe.py --selftest` must give 132 checks / 0 failed and 30/30 killed.
- M2: re-run the atl-importing selftests on main, and require the same rc and the same counts as rows 19 and 20:
  - archv2_pilot/selftest.py (282/0);
  - judgebench_side.py --selftest (rc 0);
  - judge_v2/pool_selftest.py (103/0, 37/37);
  - judge_v2/induce_run_3_selftest.py (556 ALL PASS);
  - canary_baseline.py --selftest-epoch2;
  - trace_truncation.py --selftest;
  - induce_run_selftest.py and induce_run_2_selftest.py must FAIL IDENTICALLY to pre-merge (F7).
- M3: BEFORE any JudgeBench launch, re-run JudgeBench's dry-run on main (`--dry-run --arm both --size 350`, 0 calls). Every anchor of the dry350 record (programme L20109) must be unchanged:
  - SYSTEM 3760f988...81da;
  - payload anchors G 742b02ec...793d and S1 b536f9fd...bfdf9;
  - schedule set b9e4a23b...54cc; pilot set 2bee205c...66c7;
  - payload sets G 832e54a9...a1a0 and S1 1806a6be...707b;
  - payload_body source 907366e47c3f5ce9.

  The only expected difference is the text "+ JV2-RATE-PROBE 0" in the [ACCOUNT] (iii) line (F8). The archv2_pilot K2 pins cover judge_v2/* only and are unaffected (row 18); its selftest passes on the merged tree (row 19).

## Launch steps (run-operator)

Run everything from the MAIN checkout after the merge, under plain `python`, never -O. All four steps run on ONE local day D.

0. Rule 7 / X1:
   - `powershell -NoProfile -Command 'Get-CimInstance Win32_Process | ? { $_.Name -match "python|java" } | % { "$($_.ProcessId) $($_.CommandLine)" }'`: no posting script, no JudgeBench process.
   - The day-D ledger has no JUDGEBENCH-REASONING-SIDE row.
1. `python tools/analysis/jv2_rate_probe.py --dry-run`. It must print:
   - the TRANSPORT PREFLIGHT line first (booleans only);
   - `script: ... blob:5f075d18f1e04638d5b33b3e35c4077066a21d6d / sha256-lf16:553fd699a7bbe279`;
   - K46 4581 / 5369 / 6805 and 254.0;
   - system turn d0c524bb... = K46's: True;
   - content gate 0 hits;
   - X1 OK; X2 OK for day D;
   - (iii) day-D total + 400 <= 14,000;
   - plan sha256 b2177cd172eacab59df2e72b6276fe25768c8fc610d623e5051e90b96f09f86f;
   - urlopen invoked 0 time(s).

   Any difference in the blob or the plan sha: STOP.
2. `python tools/analysis/jv2_rate_probe.py --pilot --expect-plan-sha b2177cd172eacab59df2e72b6276fe25768c8fc610d623e5051e90b96f09f86f` must print [PILOT-GUARD] PASS. Read experiment_results/jv2_rate_probe/JV2_RATE_PROBE_PILOT.txt.
3. `python tools/analysis/jv2_rate_probe.py --run --expect-plan-sha b2177cd172eacab59df2e72b6276fe25768c8fc610d623e5051e90b96f09f86f`, on the same day D.
4. `python tools/analysis/jv2_rate_probe.py --analyze` writes the outcome of record (write-once) or the _partial file.

The script blob is pinned in the probe DB's meta at the FIRST launch (the pilot). Any later launch under another blob is refused by open_db.

## Conditions

**C1 (pins).** Launch only at the pins above (blob 5f075d18; plan sha b2177cd1...f86f), from main after the merge and after M1. The outcome's header `script blob` must read 5f075d18....

**C2 (A6, day choice).** 09-25 is past. The probe and JudgeBench never post on the same day. JudgeBench's runner does NOT enforce the reverse direction: judgebench_side.py refuses only an ARCH-V2-PILOT-K46 row (its L174 PILOT_TEST); a JV2-RATE-PROBE row is not checked (verified by grep). OPERATOR CHECK before ANY JudgeBench launch on day D, which must print 0 and exit 0:

```
python -c "import json,os,sys; d=sys.argv[1]; p='experiment_results/day_calls_%s.json'%d; rows=json.load(open(p,encoding='utf-8')) if os.path.exists(p) else []; n=sum(int(r['calls']) for r in rows if r.get('test')=='JV2-RATE-PROBE'); print('JV2-RATE-PROBE calls on',d,':',n); sys.exit(1 if n else 0)" <D>
```

A JudgeBench row added on a probe day after the probe also VOIDS the probe at --analyze (V1).

**C3 (window).** Start the pilot only if the whole probe can finish before local midnight: expected 10-15 min at a 3.5 s latency plus 5 x 60 s gaps, and up to about 40 min on a slow day. Do not start the pilot after 23:00 local.
- A rollover stop splits the ramp across days. The relative bar (c) then compares against an S1 measured on another day, and both days become probe days (A6).
- If that happens anyway, the outcome discloses the split beside N*.

**C4 (K46).** K46 run2's journal has 0 unresolved (re-checked by the launch's k46_idle).

**C5 (day cap).** Read at the launch: day-D total + 400 <= 14,000. The account() line prints it.

**C6 (falsifier reachability, the outcome's wording).** The outcome records, beside the falsifier, whether it was reachable on the day: 4 x rate(S1) >= 50 and 0 HTTP 429 in S3. If 4 x rate(S1) < 50, the falsifier is recorded as "NOT FIRED (not reachable on the day: 4 x rate(S1) = x < 50)" and is DESCRIPTIVE, not evidence for P1. Beside N*, print the no-degradation false-stop rate of (c) from this review (8-16% at S2).

**C7 (post-run review).** Recompute from the probe DB (mode=ro, a copy):
- every per-step figure;
- rate(S1) as the SUM of its pilot and run segments;
- nearest-rank p95;
- the falsifier's four clauses;
- the S6 drop per RC5 (a);
- F6's bytes leg as an identity (median = 2,634 by construction).

This covers D1's untested branches.

**C8 (A4 qualifier).** The outcome carries the A4 qualifier verbatim (asserted by the selftest), and any use of N* by JV2-PARALLEL-POSTING gate (3) carries it too.

## Evidence

All files are in the session scratchpad `C:\Users\octav\AppData\Local\Temp\claude\Z--FAC-TUBerlin-THESIS-TaxoArena\7c10e5cb-d16b-4a0e-864a-f3a6151d835b\scratchpad\`:

- Dry-run and state: `rp\dryrun.txt`, `rp\stat_before.txt` / `rp\stat_after.txt`, `rp\sha_before.txt` / `rp\sha_after.txt`.
- Selftests: `selftest_O.txt` (the -O selftest), `rp\st_base\*`, `rp\st_patched\*` (the atl importers before / after the merge).
- Scripts: `rp\sim_rp.py`, `rp\sim2.py` (reachability), `rp\bnd.py` (boundaries), `rp\mut.py`, `rp\muts.txt` (mutants).
- `rp\k46\` holds the copies of the K46 run2 store, journal and manifest.

The scratch worktree .claude/worktrees/rp-review-main was created at main 7c6c588 and removed after use (`git worktree list` then shows 0 lines for it).
