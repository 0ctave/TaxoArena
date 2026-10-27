# Post-run review 2026-09-24: CANARY-EPOCH2-RUNG

adversarial-reviewer, zero calls, single process, read-only. Every cache was opened `file:...?immutable=1` (the stack_judge import ran under a connect guard that refuses any non-ro open). The four caches' sha256 and mtimes are identical before and after: pass1 5142795bdc8c5a8e, pass2 9e2f4b7cb2b30b3a, pass3 a45e966d2fc1f7e0, pass4 4612ee6a4466918b. The committed blobs at HEAD (d8ad315 for pass 3, a1d27e9 for pass 4) hash the same. Scratch scripts are in the session scratchpad: `recompute.py`, `payload.py`, `interp.py`. The reviewer wrote nothing except this file.

## VERDICT

**NUMBERS CONFIRMED. The outcome MAY BE RECORDED, with three insertions (D1, D3, D4). There is no BLOCKER.** Every printed figure reproduces to the digit from the caches: d32, d43, Δ, the seed-42 intervals, the halves, C3, C4, the Kish factor, the measured DEFF and the MDE. Nothing sits near a bar at any of 220 bootstrap seeds. The retried pass-4 rows carry the planned payloads byte for byte, and each was written once. The 52 excess calls reconcile exactly with the day ledger, but the ruled P6 sentence misdescribes 18 of them (D1).

**Sentence of record:** On the frozen 300-match canary, epoch 2 reads NO ALARM (d32 21/300 = 0.070 against the 0.138 bar, under both conventions). The same-session rung disagrees on 28/300 = 0.093 [0.060, 0.127], and Δ = −0.023 [−0.057, +0.010] contains zero at every bootstrap seed. The six pairwise disagreements over four passes (0.067–0.093) show no elapsed-time gradient, and the pass labels are exchangeable within match (p = 0.20). At this resolution, the canary measures retest noise and no drift.

## Chips

C0 PASS · RUNG VALID (start 1,093 s, last row 5,744 s, window 7,200 s) · C1 NO ALARM 0.0700 (A = B) · C2 DESCRIPTIVE d43 0.0933 [0.060, 0.127], Δ −0.0233 [−0.057, +0.010], Δ contains 0 at 220/220 seeds · C3 0/218, 0/210 adjacent (non-adjacent 1/212, 1/214, 1/214: 2 matches) · C4 75/900 = 0.083 (descriptive) · P1–P6 HELD · FALSIFIER NOT FIRED · P6 CORRECTED WORDING (D1)

## Per-claim table

| # | claim | verdict | got vs claimed | command / script | sev |
|---|---|---|---|---|---|
| 1 | d32 = 21/300 = 0.0700, conv. A and B; halves 11/150, 10/150 | CONFIRMED | 21/300 A, 21/300 B (0 pairs dropped), 11/150 contested, 10/150 cross | `recompute.py` (winner column; A: unusable in either pass = disagreement; B: pairs usable in both) | - |
| 2 | d32 interval [0.039, 0.101], SE 0.0159 at seed 42, B 2000 | CONFIRMED to the digit | script's RNG scheme, seed 42: SE 0.0159, [0.0388, 0.1012]. Own numpy bootstrap, 200 seeds × 2000: SE 0.0160 (range 0.0153–0.0167), Wald [0.0387, 0.1013], percentile [0.040, 0.103]; analytic cluster-robust SE 0.0160 | `recompute.py` | - |
| 3 | d43 = 28/300 = 0.0933 [0.060, 0.127], SE 0.0172; halves 16/150, 12/150 | CONFIRMED to the digit | seed 42: SE 0.0172, [0.0597, 0.1270]. 200 seeds: SE 0.0173 (0.0164–0.0181), [0.0595, 0.1272]; upper limit ranges 0.1255–0.1288 | `recompute.py` | - |
| 4 | Δ = d32 − d43 = −0.0233 [−0.057, +0.010], SE 0.0171, paired, question-clustered | CONFIRMED | seed 42: SE 0.0171, [−0.0569, +0.0102]. 200 seeds: SE 0.0166 (0.0159–0.0173), integrated [−0.0559, +0.0092]; the upper limit stays in +0.0078..+0.0106 and **never crosses 0**. Seed 42 has the largest Δ SE of the 21 seeds the script prints (its extra seeds give 0.0162–0.0170), so the printed interval is the widest (conservative) | `recompute.py` | LOW (D5) |
| 5 | Alarm line 0.138 = 0.087 + 3 SE at n = 300 | CONFIRMED | Pass-2 record L9983: floor 26/300 = 0.087, SE 0.0170, DEFF 1.09, "floor + 3 SE = 0.138 at n = 300". Recomputed: d21 = 26/300 = 0.08667; SE at seed 42 0.0170 (seeds 42–62: 0.0163–0.0173), DEFF 1.093; 0.08667 + 3 × 0.0170 = 0.1376 → 0.138 (integrated 0.1371). The registration's arithmetic sqrt(0.087 × 0.913/300) × sqrt(1.09) = 0.01699 reproduces. The instrument compares integers, 21 × 1000 ≥ 138 × 300 → false. Point 0.070 is 6.8 pp below the bar | `recompute.py`; `sed -n 9983p docs/judge_v2_program.md` | - |
| 6 | Floor 0.087 is the recorded pass 1 → 2 figure; C0(b) 26/300 | CONFIRMED | 26/300 from the pinned pass-1 and pass-2 caches (shas equal the pins) | `recompute.py` | - |
| 7 | Support: Kish 1.160, DEFF 1.17, n_eff 256.6, MDE 0.0446 | CONFIRMED (seed 42) | Kish 1.1600 (279 q; sizes {1: 260, 2: 18, 4: 1}); binomial 0.0147; DEFF 1.169; n_eff 256.6; MDE 0.0446. At d43: DEFF 1.047, n_eff 286.7, MDE 0.0481 (not printed). Across seeds, DEFF(d32) runs 1.08–1.29 | `recompute.py` | LOW (D5) |
| 8 | C3 reversals 0/215 (1,2), 0/218 (2,3), 0/210 (3,4) | CONFIRMED, registered form | Same counts. The registration counts adjacent pairs only; the non-adjacent pairs give (1,3) 1/212, (1,4) 1/214, (2,4) 1/214, from 2 matches: 8320 [gemini, gemini, TIE, gpt-4o] and 7954 [arx_0314, TIE, gpt-4o, TIE] | `recompute.py`, `interp.py` | MEDIUM (D4) |
| 9 | C4 pooled 75/900 = 0.0833 beside 0.116 | CONFIRMED | 26 + 21 + 28 = 75 | `recompute.py` | - |
| 10 | C0(c) fingerprint {'azure:grok-4-1-fast-non-reasoning': 1200}; finish all stop; unusable 0 | CONFIRMED | 600 + 600 providers, all `azure:grok-4-1-fast-non-reasoning`; finish {'stop': 600} per pass; invalid 0; vote INVALID 0; 1,200 response ids, all distinct, none NULL | `payload.py`, `interp.py` | - |
| 11 | Rung VALID: pass 4 started 1,093 s after pass 3's last row (13:47:56); first row 1,127 s | CONFIRMED | pass 4 run_meta started 14:06:09; first row 14:06:43; last row 15:23:40 = 5,744 s, also inside 7,200 s | `payload.py` | LOW (D8) |
| 12 | Retried pass-4 rows byte-identical to the planned payloads (postscan: 0 differences) | CONFIRMED independently | (a) Payload anchor sha256 over (match id \| system \| user1 \| user2), in set order, recomputed from the CACHED user bodies plus system texts rebuilt with `stack_judge.system_for` (14 systems, 0 system_sha16 mismatches) = **3501e6aef27aad68 for pass 3 and for pass 4**. This equals the pre-call dry-run anchor in `dry_run_pass3.log` L10 and in all three pass-4 dry runs. (b) Pass-3 vs pass-4 bodies for all 300 matches (13 pass-3 and 17 pass-4 retried matches, disjoint sets): 0 differ. (c) sha16(body) = stored user*_sha16 on all 1,200 | `payload.py`; anchor snippet in the session record | - |
| 13 | Retried rows in the right order and written once | CONFIRMED | post_index = set position on 300/300 in both passes; ts puts the retried rows in their resume launches (pass 4: 14:59:11 onward, the last 3 at 15:20–15:23). Written once: the "ok" counts per launch add to exactly 300 (pass 3: 11 + 1 + 276 + 11 + 1; pass 4: 12 + 271 + 14 + 3), equal to 300 rows under PRIMARY KEY match_id, and `run()` posts only ids not already cached. Per-row script_sha16_lf: pass 3 96d27df4561a2fe3 × 300; pass 4 ccc145d0009e1a65 × 297, 32236c62be50038c × 3. Every one is a READY'd version, and (a) shows the payloads are identical | `payload.py`; logs | - |
| 14 | P6 in the ruled form: 1,200 verdict-bearing, 1,252 posted, 52 "errored with no verdict and no fingerprint" | PARTLY | Day ledger (`day_calls_2026-09-24.json`): 9 CANARY entries, sum 1,252 (pass 3: 24+2+571+23+2 = 622; pass 4: 24+567+33+6 = 630); day total 3,430 = 2,178 TRACE + 1,252; 4,060 + 1,252 + 2,178 = 7,490 ✓. Per-launch excess (posted − 2 × ok): 2 + 0 + 19 + 1 + 0 + 0 + 25 + 5 + 0 = 52 ✓. But `one()` posts order 1 and then order 2, and drops the match on any exception, while errored matches number 1 + 12 + 1 + 17 + 3 = 34. **So 52 = 34 calls that ended HTTP 429 plus 18 order-1 calls that returned HTTP 200 with a verdict and were discarded because the same match's order-2 call hit 429.** The fingerprints of those 18 were checked in flight (`check_fingerprint` runs before the order-2 post; a foreign one would have stopped the run) but never recorded | logs; `canary_baseline.py` L902-L914; `rejudge_reasoning.py` L111-L164 | MEDIUM (D1) |
| 15 | C0(e) pass-3 pilot guard PASS, 0 of 12 | PARTLY | 0 of 12 in the cache is true. The first pilot launch FAILED its runtime guard (1 of 12, match 4653, HTTP 429, D6) and passed on relaunch (`pass3_pilot12.log`). C0(e) reads only the cache, where errored jobs never land, so it cannot see this | logs; `canary_baseline.py` L1228-L1229 | LOW (D3) |
| 16 | Old-cache pins unchanged around every launch | CONFIRMED | pass1 5142795b…, pass2 9e2f4b7c… equal the pins now; the [PIN] lines before and after in all 9 launch logs | sha256sum; logs | - |
| 17 | P1–P5 HELD | CONFIRMED | 0.0700 ∈ [0.050, 0.125]; NO ALARM; 0.0933 ∈ [0.045, 0.120]; −0.0233 ∈ [−0.040, +0.050]; 0/0 | `recompute.py` | - |

## Defects

- **D1 MEDIUM: the P6 ruling's clause is false for 18 of 52 calls.** The ruling (L15784; READY L44) says "N − 1,200 errored (HTTP 429 / transport) with no verdict and no fingerprint". The truth: 34 calls errored with HTTP 429; 18 order-1 calls returned HTTP 200, and their verdicts were discarded because order 2 of the same match failed. The fingerprint was checked in flight and not recorded. The P6 score is unaffected: it is on the 1,200 cached calls, HELD. Fix: the registrar's outcome writes, "POSTED 1,252 calls (day ledger); 52 without a cached verdict = 34 HTTP 429 (after 6 attempts each inside call_judge_full) + 18 order-1 calls answered HTTP 200 and discarded because their match's order-2 call failed (fingerprint checked in flight, not recorded); under the amended ceiling 1,260 (CEILING-2)." Do not copy the ruled clause verbatim; insert a bracket at L15784.
- **D2 LOW: call units.** "Posted calls" counts `call_judge_full` invocations, not HTTP requests. Each of the 34 errored invocations made 6 HTTP attempts (≥ 204 HTTP 429 responses in total), and successful invocations may hide retries on 408/429/5xx/timeouts. The amendments also mix units: CEILING-1's "22 HTTP 429 retries" is excess calls (14 errored matches); CEILING-2's "20 retries" is errored matches (30 excess calls); the operator line of 13:48:17 says "29 HTTP-429-errored pass-3 calls" beside its own "22 errored". Fix: a bracket naming the unit (logical calls; excess = 22 pass 3, 30 pass 4).
- **D3 LOW: C0(e) cannot fail on errored pilot jobs**, which is the class "a pilot whose errored jobs vanish from the guard". The runtime guard did count the error (D6) and refused, the relaunch healed it, and the operator logged the first-launch count as READY L127 requires. Fix: the outcome record inserts "pass-3 pilot first launch REFUSED by its guard (1 of 12, HTTP 429, match 4653); relaunched, 12 of 12 cached, 0 unusable".
- **D4 MEDIUM (interpretation): "decisive verdicts never reverse" is true only for adjacent pairs.** Over four passes, 2 of 300 matches carry two different decisive winners (8320, 7954). Of the 149 pairwise disagreements over the six pairs, 146 involve a TIE and 3 are reversals. P5 is registered on (2,3) and (3,4) only and stays HELD, but the pass-2 reading "churn lives only at the tie boundary" must be qualified as "adjacent passes only; 2 matches reverse through a TIE". Fix: a descriptive insertion beside C3.
- **D5 LOW: DEFF and the intervals are printed at seed 42 only**, despite the D-1 lesson. Measured DEFF(d32) spans 1.08–1.29 over 200 seeds. Seed 42 gives the largest Δ SE of the script's 21 seeds. No reading changes: the integrated intervals are in rows 2–4. Fix: in future readouts, print the across-seed range of the SE and the DEFF.
- **D6 LOW: the postscan's producer is not committed.** `postscan.log` cannot be reproduced from the record. Row 12 substitutes an independent proof. Fix: commit the scan snippet or cite this review.
- **D7 LOW: the posting-order sha16 20b51354c05c5ad4 is vacuous on resumes.** It is computed over the full set list, so every launch prints the same value. This is the same class as TRACE-TRUNCATION D-e (already queued).
- **D8 LOW: the rung-validity check tests only the start of pass 4.** 3 of 300 pass-4 matches (8720, 879, 9136) were judged at 15:20–15:23, after CEILING-2 and the split draw, under a third script version. They still fall within 7,200 s of pass 3's last row. The registration's "same process chain" is not machine-checked. Descriptive disclosure only.
- **D9 LOW: "A and B agree" carries no information here.** With 0 unusable rows in 1,200, the two conventions are identical by construction. This says nothing about sensitivity to the choice of convention.

## Interpretation (Q5, DESCRIPTIVE ONLY)

- **The premise needs a correction.** d32 is not week-apart: pass 2 ran 09-22 10:54–11:01 and pass 3 ran 09-24 12:48–13:47, about 50 h apart. The 6-day figure is d21 = 0.087.
- **Disagreement by gap:**

  | gap | pair | disagreement |
  |---|---|---|
  | ~1.3 h | (3,4) | 28 = 0.093 |
  | ~2 d | (2,3) | 21 = 0.070 |
  | ~2 d | (2,4) | 26 = 0.087 |
  | ~6.4 d | (1,2) | 26 = 0.087 |
  | ~8.5 d | (1,3) | 28 = 0.093 |
  | ~8.5 d | (1,4) | 20 = 0.067 |

  Disagreement shows no monotone trend with elapsed time; the same-session pair ties for the highest.
- **Exchangeability null.** Pass labels were permuted within each match (20,000 permutations; this preserves each match's own verdict distribution). The observed d34 − mean(other five) is +3.8 matches, one-sided p = 0.20, and the null d34 is 24.8 ± 3.2 against an observed 28. The four passes behave as exchangeable draws.
- **Reading.** The canary measures per-match retest (sampling) noise of about 0.07–0.09. It shows no drift at this resolution: Δ ± ~3.3 pp, MDE ≈ 4.5 pp. A same-session paired design gets no lower floor than the across-day one, so it must budget the same ~0.08. Only 43 of 300 matches (14.3%: 22 contested, 21 cross) ever change across the four passes, so the noise lives in a fixed minority of tie-boundary matches, not spread across the set.

## Does not show

- It does not show that the judge is free of drift smaller than ~4.5 pp (the MDE). Drift that moves the same unstable matches in the same way as noise is indistinguishable here.
- It does not show that C2 tests anything. C2 is DESCRIPTIVE-ONLY by registration and bounded by the frozen set; Δ's sign is not established at any seed.
- It does not show that decisive verdicts never reverse (D4).
- It does not show that the 52 excess calls all failed (D1), or that the posted count equals HTTP requests (D2).
- It does not show convention sensitivity (D9), or the fingerprints of the 18 discarded HTTP-200 calls beyond the in-flight check (D1).
- It does not show a floor for any other set, judge, prompt, or the per-call retest rate (DECOMP's 5.7% is a different quantity).
- It does not show a pooled alarm rule: C4 is descriptive, and its pooling is not registered.
