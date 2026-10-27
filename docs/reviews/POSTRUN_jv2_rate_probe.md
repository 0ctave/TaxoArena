# POST-RUN review: JV2-RATE-PROBE (run of record b0c231c, 2026-09-26, 398 calls)

## VERDICT: VALID

Every per-step figure, every decision and every score in the outcome file (sha256 59a3b863...) reproduces to the printed digit. The recomputation used copies of the probe DB and its journal (mode=ro, immutable=1). C0 V1-V4 all HOLD, so the probe is not void, and V5 HOLDS. There is no BLOCKER and no HIGH.

Four defects are recorded, all disclosure or scope items. Only D1 (MEDIUM) touches the record of record: the outcome omits the C6 wording. The registrar must supply it in the outcome section, because the outcome file is write-once. D2 (MEDIUM) is a carry-forward. D3 and D4 are LOW.

Reviewer: adversarial-reviewer. Zero calls. Nothing in the repo was written except this file.
- The originals were never opened. I copied them to the scratchpad `pr\` directory and read only the copies.
- Before and after this review: sha256 661cfbda.../69f8b3d7... unchanged, and the `ls --full-time` listing is identical (`diff` reads STAT-EQUAL).
- Working tree = HEAD blob for all 4 committed probe artefacts (`git hash-object` = `git rev-parse HEAD:<path>`).
- The E: backup has identical sha256 on all 5 files, pilot_guard.json included.

## 1. Recomputation (scripts `pr\recompute.py` and `pr\valid.py`, my own code; no probe function imported)

Definitions:
- latency = t_end - t_reserve;
- p95 = nearest rank, i.e. the ceil(0.95 n)-th smallest value;
- wall = the sum over launch segments of (max t_end - min t_reserve);
- rate = invocations / wall x 60.

| step | N | inv | HTTP | 429 | exh | wall s | rate /min (mine = printed) | median / p95 / max s (mine = printed) | p95 / p95(S1) | max in flight (measured from attempt send/end) | adm (a)(b)(c) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S1 | 1 | 24 | 24 | 0 | 0 | 37.600 + 35.608 = 73.209 | 19.67 | 2.898 / 4.148 / 4.240 | exempt | 1 | Y Y exempt |
| S2 | 2 | 36 | 36 | 0 | 0 | 54.600 | 39.56 | 2.877 / 3.894 / 4.749 | 0.939 | 2 | Y Y Y |
| S3 | 4 | 48 | 48 | 0 | 0 | 38.478 | 74.85 | 3.147 / 3.708 / 4.027 | 0.894 | 4 | Y Y Y |
| S4 | 8 | 64 | 64 | 0 | 0 | 27.809 | 138.09 | 3.185 / 4.155 / 4.200 | 1.002 | 8 | Y Y Y |
| S5 | 12 | 76 | 76 | 0 | 0 | 22.452 | 203.10 | 3.231 / 3.861 / 4.973 | 0.931 | 12 | Y Y Y |
| S6 | 12 | 150 | 150 | 0 | 0 | 42.831 | 210.13 | 3.188 / 4.090 / 4.791 | 0.986 | 12 | Y Y Y |

Other per-step readings:
- **Tokens and bytes.** Median completion tokens are 235.0 / 238.5 / 249.5 / 254.0 / 248.5 / 247.5. Median user bytes are 2634.0 in every step. Unparsed (vote INVALID) is 0 of 398. Every finish_reason is `stop`, every outcome RETURNED, every status 200, and attempt_no has a maximum of 1.
- **Pilot 12** (launch k = 1): median 2.933 s, p95 4.240 s, 19.15/min, median tokens 239.0. This equals the PILOT file.
- **429 share and CP95.** The 429 share is 0 in every step. CP95 at 0 of n (1 - 0.05^(1/n)) is 0.1173 / 0.0798 / 0.0605 / 0.0457 / 0.0387 / 0.0198, equal to the printed values.

| quantity | mine | printed | agreement |
|---|---|---|---|
| C1 ratios vs the previous admissible step (bar 1.3) | S2 2.0112, S3 1.8920, S4 1.8449, S5 1.4708: all qualify | N* = 12, knee none | EXACT |
| N* (ramp; S6 admissible) | 12 | 12 | EXACT |
| G = rate(S5) / rate(S1) | 10.3256 | 10.326 | EXACT |
| rate(S6) / rate(S1) | 10.6828 | 10.683 | EXACT |
| C3 S3 HTTP overhead | (48 - 48) / 48 = 0.000 | 0.000 | EXACT |
| V5 / P5: median user bytes; median completion tokens over 398 (band 254 +-30% = [177.8, 330.2]) | 2634.0; 248.0 | same | EXACT; the bytes leg is an identity by construction (READY F6) |
| P1: (i) N* in {1, 2}; (ii) rate(S3) < 35 | False; False | FAILED | EXACT |
| P2 | no inadmissible step | UNDETERMINED (R5) | EXACT |
| P3: S1 median in [3.0, 4.5] and 0 exhausted | 2.898, so False; 0 exhausted | FAILED | EXACT (pilot segment 2.933 and run segment both < 3.0) |
| Falsifier: rate(S3) >= 50; share <= 2% literal; 0 exhausted; p95 <= 1.5 x 4.148 = 6.222 | 74.85 True; 0.0000 True; 0 True; 3.708 True | FIRED | EXACT |

**D1 branches (READY condition C7).**
- **S1 wall = SUM of segments.** The pilot segment is 37.600 s (12 calls) and the run segment 35.608 s (12 calls), sum 73.209 s, giving 19.67/min. The script prints this value (operator deviation 3, CONFIRMED). The rejected one-span reading, 95.1 s across the 22 s gap between launches, would give 15.13/min and G = 13.42. The printed G therefore uses the registered A5 (vi) definition.
- **RC5 (a) S6-drop branch (not triggered).** Had S6 been inadmissible, N* would have dropped to 8, the largest qualifying step below S5, with G = 138.09 / 19.67 = 7.02.
- **Falsifier bar.** The bar is 50 and S3 read 74.85. The mutant bar of 35 would give the same verdict here, so the D1 mutant is not decisive on these data.
- **B1 exhausted bar.** 0 exhausted anywhere, so the branch is moot.
- **Margins.** No decision sits near its bar. The worst margins are C1 at S5 (1.47 against 1.3) and (c) at S4 (1.002 against 1.5).

**Support, post-run.**
- The declared DEFF is n per step, so n_eff = 1 per step (6 regime observations).
- There are 0 429 events in 398 attempts, so there are no clusters to measure and Kish is not defined, as registered.
- The MDE is unchanged: P(<= 1 of 48 | p = 0.10) = 0.0403.
- The 2% bar stays a screening threshold. At 0 of 150, S6's CP95 is 1.98%, exactly the bound, not below it.
- The outcome prints all of the above, and it reproduces.

## 2. Validity

| # | claim | result | command / evidence | mine vs claimed | sev |
|---|---|---|---|---|---|
| V-1 | ledger == journal, 398 <= 400 | CONFIRMED | valid.py | Journal: 398 invocations, 398 resolutions (all RETURNED), 0 unresolved, all on day 2026-09-26. Day ledger: pilot#1 12 + run#2 386 = 398. Journal http_attempts 398 = attempt rows 398. The cap trigger is at 400 | - |
| V-2 | every body distinct and equal to the plan | CONFIRMED | valid.py | Recomputing the script's digest formula over the DB rows (idx, step, size_class, body_sha) plus the seed and targets gives b2177cd172eacab59df2e72b6276fe25768c8fc610d623e5051e90b96f09f86f = meta plan_sha = the READY's pin. 398 distinct body_sha. The journal payload_sha256 multiset equals the DB's, and 398/398 match by JV2RP-<idx>. Classes q10/q50/q90 = 134/132/132 | - |
| V-3 | script pin | CONFIRMED | meta, launch table, `git rev-parse HEAD:` | script_blob 5f075d18 in meta and in both launch rows = HEAD blob = the working-tree hash-object. judge_v2/pool.py is e9bc770f (unchanged) | - |
| V-4 | no api-key or host in any output | CONFIRMED | a scan of the 14 files in experiment_results/jv2_rate_probe plus the day ledger plus the decompressed content_zlib of all 398 rows, against 12 needles derived from the .env values (full values, endpoint host and its first label, key prefix8/suffix8), printing names only | 0 hits. The attempt table stores header NAMES plus x-ratelimit-* VALUES only. The one `x-ratelimit-key` value (27 chars, 1 distinct) contains no needle and is contained in none | LOW (D4) |
| V-5 | X1 / X2 exclusivity | CONFIRMED | x1 table (14 rows, ok = 1, x2_ok = 1); run.log / pilot_stdout.log | "0 python/java process(es) besides this one" at the launch and at all 14 step boundaries. Day ledger 09-26 has 0 JUDGEBENCH-REASONING-SIDE rows. The C2 operator check prints 398 for 2026-09-26 and exits 1 | LOW (D3) |
| V-6 | pool / content guard | CONFIRMED | launch.gate_hits; dry-run transcript | gate_hits 0 on both launches. The dry-run prints "pool: none (SYNTHETIC-DEV ...)" and "content gate hits 0". No reserved, EVAL or TRAIN item is posted. pool.py is unchanged | - |
| V-7 | pilot guard PASS | CONFIRMED | pilot_guard.json (E: backup sha 7e478f0c = local); invocation rows of launch 1 | 12/12 RETURNED, 0 unparsed, 0 length or content_filter, 0 raised | - |
| V-8 | A4 qualifier verbatim | CONFIRMED | the outcome line vs QUALIFIER_A4 (script L171) and RC3 (programme L20294) | byte-equal | - |
| V-9 | concurrency as registered | CONFIRMED | max in flight measured from attempt t_send / t_end | 1 / 2 / 4 / 8 / 12 / 12. Mean in flight 1.95 / 3.92 / 7.68 / 10.85 / 11.31 (S2-S6). Reserve-to-send overhead median 0.6 ms | - |

## 3. The operator's deviations

1. **M2: archv2_pilot/selftest.py rc 1. CONFIRMED date-dependent, not caused by the merge.**
   - Mechanism: the selftest's `TODAY = "2026-09-25"` (L126) is passed as the launch day to `ACC.wrap_call(..., "cap", TODAY, ...)` (L886) without a `clock=` argument. `wrap_call` then defaults to `local_day()` = `time.strftime` (accounting.py L136-138, L385-390), which raises SystemExit DAY ROLLOVER on any local date other than 2026-09-25.
   - The two logs are identical modulo the temp-dir name and its derived sha: normalised diff = 0 lines.
     - post-merge: op\incident\archv2_pilot_m2_rc1.txt;
     - pre-merge 7c6c588: op\archv2_base_0926.txt.
     - Both show 148 PASS / 0 FAIL, then the rollover exit.
   - The merge's only diff in the archv2 or ledger area is `git diff --stat 7c6c588 HEAD -- tools/analysis/archv2_pilot/ tools/analysis/accepted_tests_ledger.py`: 1 insertion, the CEILINGS line.
   - Consequence: M2 on 09-26 proves identity for the first 148 checks only; the remaining 134 of 282 did not execute. Inertness for them rests on the READY's execution on 09-25 (row 19: 282/0 before and after).
   - The fix IS needed before any future archv2 use, i.e. any READY or M-check that cites this selftest. As written, the selftest can never pass again. Fix: pass `clock=lambda: TODAY` at L886 (and at every other clock-less `wrap_call` / `PL.launch` path that reaches a send), or derive the fixture day from the injected clock. It is a selftest-only change, so the pinned judge_v2 / archv2 runtime blobs are untouched. The owner is the engine-coder, with its own small READY.
2. **C6 gap. CONFIRMED.**
   - The outcome file has 0 occurrences of "reachable", "4 x rate", "false-stop" and "8-16" (grep -c on each).
   - Reachability as I recompute it: 4 x rate(S1) = 4 x 19.67 = 78.68 >= 50, and S3 carried 0 HTTP 429s. The falsifier was REACHABLE on the day, so its FIRED reading is evidence.
   - The (c) false-stop rate did not bite: every step's p95 ratio is <= 1.002.
   - See D1.
3. **S1 wall. CONFIRMED.** The sum of the two segments gives 19.67/min, as printed (section 1).
4. **pilot_guard.json.** Gitignored: `.gitignore:124:*.db.*` per `git check-ignore -v`. It was not committed, and it is present in the E: backup with sha 7e478f0c = local. The same rule matches the committed jv2_rate_probe.db.invocations.db, which was therefore force-added. That is consistent and not a defect. The PILOT file carries the same guard figures.

## 4. Scope: what N* = 12 / G = 10.3 does and does NOT license

The measurement:
- ONE run, 2026-09-26 00:23:20-00:33:09 local = 2026-09-25 22:23-22:33Z.
- grok-4-1-fast-non-reasoning ONLY. Registration 1.13: "Anything about the reasoning deployment ... It has its own quota and is not probed". The DB meta judge is grok-4-1-fast-non-reasoning, and so is every row.
- Synthetic K46-sized bodies, rr's fixed-N transport with 6 attempts and Retry-After ignored.
- Night conditions: the S1 median was 2.898 s, faster than K46's own morning regime of 3.51 s. That speed is what failed P3.

The latency regime of record comes from K46 run2 (READY row 22): the share of latencies > 10 s is 0.0-2.3% in 05-09Z and 10.2% / 82.4% / 87.8% in 10Z / 11Z / 12Z. The probe sampled 22Z, an hour the K46 record never covered.

**N* = 12 is a LOWER BOUND, not a limit.** The ramp tops out at 12 (Support (g): "G is capped by the ramp at N = 12"), and knee = none. The rate headers show the probe never approached the quota:
- `x-ratelimit-limit-requests` 500 and `-limit-tokens` 500000, which agrees with the author's portal reading;
- `remaining-requests` minimum 488;
- `remaining-tokens` minimum 485,567.

Per request, the limiter charged 967-1,523 tokens (median 1,164 in S1). That is the prompt estimate, not max_tokens 8192. At 210/min this is about 245k TPM on the prompt side, about 50% of 500k, before completion tokens. These readings are DESCRIPTIVE (A4).

S6 lasted 42.8 s. The registration's "sustained window of about 1-4 min" was not reached, because the 150 calls fixed by the registration last under 60 s at this rate. Nothing is shown about a limiter window of 1 minute or longer, or about hours of posting. See D2.

It LICENSES:
- "On the night of 09-25/26, alone on the non-reasoning deployment, 12 in flight under rr ran 210 calls/min for 43 s with 0 429s and no latency degradation (p95 / p95(S1) <= 1.002)."
- "The 09-16 regime was back that night" (the falsifier FIRED and was reachable).
- "The deployment's configured limits are 500 RPM / 500k TPM" (headers, matching the portal).
- The JV2-PARALLEL-POSTING build decision (moot: Amendment 24 already decided it).

It does NOT license:
- **Daytime runs.** Nothing was measured at 10-12Z, where K46 saw 82-88% of latencies above 10 s, and 09-24 saw 429s at about half the 09-23 clean rate (L20210 (e2); shared-capacity throttling). Throughput is latency-bound: at a 16 s median, N = 12 gives about 45/min, not 210. Whether 429s return at that load is unmeasured.
- **The reasoning deployment.** Not probed. The quota figure applies to both deployments by the author's reading, but shared-capacity 429s and latency are unmeasured.
- **The pooled poster.** It honours Retry-After, makes 1 attempt per rr call, halves its bound on 429s or timeouts, and paces by the --max-rpm token bucket (A4, F3: "does not transfer as-is"). The probe observed 0 429s, so it says nothing about how that machinery behaves under throttling.
- **Any other day** (the ~10x swing within 8 days, 0.2).
- **A sustained window**, as above.

**Gate (3) first live pooled run: my recommendation (the registrar's to register, citing JV2-RATE-PROBE).**
- **Daytime (any hour in 06-20Z):** `--post-workers 8 --max-rpm 60`, pilot 12 at N = 8.
  - 60 is the top of the orchestrator's candidate ladder 20 / 30 / 40 / 60.
  - It is 29% of the 210/min measured clean, 12% of the 500 RPM quota, and about 90k TPM, i.e. 18% of 500k.
  - N = 8 is a measured-clean step; it sustains 60/min up to about 8 s latency and degrades gracefully above that.
  - 58/min ran clean on 09-23 in daytime, while 09-24 throttled near 29/min. The pool's Retry-After handling and halving, not the probe, are the protection there.
- **Night (about 20-06Z):** `--post-workers 12 --max-rpm 120`.
  - N = 12 is the largest measured; 120 is 57% of 210/min and 24% of the RPM quota.
  - Register it only after a daytime or night first run at 60 with 0 exhausted and 429 share <= 2%.
- **Never** a --post-workers above 12 (unmeasured), and never a --max-rpm above 210 (the largest rate observed).
- Keep --request-timeout-s at 120 and --breaker-k at 8 (defaults).
- The run's own pilot at that N is the day's check. N* = 12 is not.

## 5. JudgeBench implications

- **No posting on 09-26.** The probe day is 09-26: the day ledger has 398 JV2-RATE-PROBE calls, and the C2 operator check exits 1. JudgeBench must not post on 09-26 (A6). judgebench_side.py still does NOT refuse a probe day by code: it checks only PILOT_TEST = "ARCH-V2-PILOT-K46" (L174, L951-L958). The operator check is the only barrier.
- **Earliest day.** The earliest day is 2026-09-27. The C2 check for 2026-09-27 prints 0 and exits 0 as of this review. The 09-27 day cap is fresh (1,400 calls at size 350, well inside 14,000; the day cap counts invocations, not cce).
- **G arm** (non-reasoning, --workers 4, rr at fixed N, the same transport as the probe). S3 is the direct analogue: 74.85/min, HTTP overhead 0.000 against JB's 10% margin (770 / 700), 0 exhausted. That was at NIGHT.
  - The probe gives no reason to change --workers 4 (it answers open item 3: no change).
  - It gives no daytime assurance either. On a 429-heavy start, stop early rather than burn the per-arm cap (the L20210 (e5) recommendation stands).
- **S1 reasoning arm** (700 calls x 10 cce = 7,000 cce). Its deployment was NOT probed, so nothing here licenses its --workers 4. At a 30-90 s reasoning latency, 4 in flight is about 3-8 calls/min, far below the RPM and TPM quota. The binding risk is shared-capacity 429s and the day's latency, both unmeasured.
  - Given the 7,000 cce at stake, JB's own pilot at N = 4 on the S1 arm is the only evidence. Its HTTP-attempt cap should be read at the pilot, before the run.

## Defects

**D1 (MEDIUM, disclosure; READY C6 not met in the file).** The outcome omits:
- the reachability wording, "reachable on the day: 4 x rate(S1) = 78.68 >= 50, 0 HTTP 429 in S3";
- the (c) no-degradation false-stop rate beside N* ("8-16% at S2, READY a34642c").

The outcome file is write-once, so do not rewrite it. Fix: the registrar's outcome section of record in docs/judge_v2_program.md and the JV2-RATE-PROBE.json record carry both lines, citing this review. Substance is unaffected: the falsifier was reachable, and no false stop occurred.

**D2 (MEDIUM, scope carry-forward).** Four limits must travel with any use of N* or G:
- N* = 12 is a ramp-capped lower bound (knee none, remaining-requests >= 488);
- S6 sustained 42.8 s, not the registered "about 1-4 min";
- the run was a single night (22Z) sample on the non-reasoning deployment only;
- the result does not transfer to the pool (A4).

Fix: gate (3)'s registration and JudgeBench's launch READY quote section 4 of this review. Neither may cite "G ~ 10" as a daytime or pooled expectation.

**D3 (LOW, vacuity of X1).** `process_snapshot()` (data_v2/build.py L78-95) returns [] when PowerShell prints nothing, e.g. when it fails with an empty stdout. That result reads as "0 processes -> OK", so it fails open. Only an exception is recorded ("sampling failed").
- The 14 samples here all read 0. That is plausible at 00:24 local, and the READY's X1 mutant was killed with a stub, but the log cannot distinguish a genuine 0 from an empty snapshot. The probe's own PID is excluded before counting.
- Fix, for future users of process_snapshot: fail closed when the snapshot does not contain the caller's own PID.

**D4 (LOW, disclosure).** The committed probe DB stores the opaque `x-ratelimit-key` header value (27 chars, 1 distinct). It is not the api-key and not the host (scan: 0 of 12 needles), but it is a limiter identifier committed to the record. Fix: optional; drop it from future header capture, or record it as "names only".

**Carry-forward, not a probe defect: archv2_pilot/selftest.py date pin** (section 3, item 1). It must be fixed before any READY or M-check cites it.

## Scores of record (reviewed)

- C0: HELD (V1-V4 HELD).
- V5 / P5: HELD.
- C1: N* = 12.
- C2: G = 10.326, so "build" (superseded for the build decision by Amendment 24).
- C3: 0.000.
- P1: FAILED.
- P2: UNDETERMINED.
- P3: FAILED (2.898 s).
- P4 readout: headers present, 10 names.
- Falsifier: FIRED, and reachable.

All CONFIRMED.

## Evidence

The scratchpad is `C:\Users\octav\AppData\Local\Temp\claude\Z--FAC-TUBerlin-THESIS-TaxoArena\7c10e5cb-d16b-4a0e-864a-f3a6151d835b\scratchpad\`:

- `pr\recompute.py`: per-step figures, C1, G, P1-P3, the falsifier and the D1 branches.
- `pr\valid.py`: plan sha, journal and ledger.
- `pr\stat_before.txt`: the originals' stat.
- `pr\jv2_rate_probe.db` and `pr\jv2_rate_probe.db.invocations.db`: the copies.
- The operator logs, read from `op\`.
