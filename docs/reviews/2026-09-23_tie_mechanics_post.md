# TIE-MECHANICS: post-run numbers review (adversarial reviewer, zero calls, read-only)

- Registration: `docs/judge_v2_program.md` L12911-L13030 (3c2fcab). READYs 14edeb4 -> bc2ea7b -> 776a2dd.
- Instrument: `tools/analysis/tie_mechanics.py`, git blob 7f88d2ac581679aea33a2a25dc088883785fca86, the same at HEAD as at merge 8cd0f0e (`git diff --quiet 8cd0f0e HEAD --` exit 0). sha256[:16] LF d6a1a0409a0fc06e, CRLF working tree 4a18124878801487, matching the outcome header.
- Outcome at eb6fc9c: `experiment_results/x12_crossdomain/tie_mechanics_outcome.txt`. Hash kinds: 1a8d802e...73d1c6 (the brief's figure) is the sha256 of the **CRLF working-tree rendering**. The committed LF bytes hash to sha256 2b28ee178c4664777a0b46d4c0553f0313f79089273fced1cffc8e769259a370, git blob a2df609de26fd8b0117b7bfa8fa12b483f83dfb4. `tr -d '\r' | sha256sum` gives 2b28..., the same as `git show eb6fc9c:<path> | sha256sum`.
- Caches, before and after this review: pass 1 sha256 5142795bdc8c5a8ec8d09a3a4f9cd6c84de206834aeab7ca11cea4761000690c, pass 2 sha256 9e2f4b7cb2b30b3a2a7abf897c8bb531d5c6c14eebd21668ed6ab3d747132c4e. Both are unchanged and have no -wal or -shm (`ls | grep -c` = 0). I opened them only as `file:...?mode=ro&immutable=1`.
- Operator logs (`scratchpad/tie_mechanics_run/`): run.log is identical to the outcome except for its `[WRITTEN]` line (diff after stripping CR). cache_before and cache_after are identical. Selftest: 29 checks, 0 failed. Error or traceback lines: 0.
- Rule 7: the running processes are an idle Gradle daemon, a Kotlin compile daemon, and `cert_under_filter.py --selftest` (admitted under W1-W5). No construction or site null was running. The review reads only the two canary caches.
- My scripts are in `C:/Users/octav/AppData/Local/Temp/claude/Z--FAC-TUBerlin-THESIS-TaxoArena/7c10e5cb-d16b-4a0e-864a-f3a6151d835b/scratchpad/tie_post/`: `load.py`, `counts.py`, `nulls.py`, `hetero.py`, `support.py`, `c23.py`, `c3strat.py`. They do not import tie_mechanics or vote_frame_cert.

## Per-claim table

| # | claim (outcome) | mine | command | verdict |
|---|---|---|---|---|
| 1a | 300 rows and 300 distinct ids per pass; same pair, qid and match set | 300/300; the same id set; pair+qid equal on 300 of 300 | counts.py | CONFIRMED |
| 1b | the stored winner equals combine(vote1, swap(vote2_raw)) on every row (the frame) | 300/300 in pass 1 and 300/300 in pass 2; the `flip` column is consistent on 300/300 | counts.py | CONFIRMED |
| 1c | R1: 26 changes (16 TIE->dec, 10 dec->TIE), 215 decisive-both, 0 reversals, T 59/600, 23 keep-changed | 26 (16/10), 215, 0, 59/600, 23 | counts.py | CONFIRMED to the digit |
| 1d | n2 = 10, n1 = 39 | n2 10, n1 39; distribution d = 0/1/2: 251/39/10 | counts.py | CONFIRMED |
| 2a | E0 2.856 (closed form), SD0 1.528 | E0 2.856427, SD0 1.527589; the pmf sums to 1 | nulls.py (exact closed form) | CONFIRMED |
| 2b | P0(n2 >= 10) = 0.0001 | 0.000104680 | nulls.py | CONFIRMED |
| 2c | region: upper n2 >= 7 (P0 0.0146), no lower region (P0(0) 0.0423) | upper >= 7 (P0 0.014618; >= 6 gives 0.05052); P0(0) 0.042176 > 0.025 | nulls.py | CONFIRMED |
| 2d | the pmf over 0..12 (closed form) | identical to 4 dp | nulls.py | CONFIRMED |
| 3 | the reading: "within-match dependence ... more often than independent per-call change allows (a property of the judge on these matches)" | see section 3. The rejection is absorbed completely by the predetermined match covariate "pass-1 verdict TIE vs decisive": the stratified exact null gives E0 7.12, p 0.103, region >= 12, so 10 lies OUTSIDE | hetero.py | **PARTLY (overclaims)** |
| 4a | Kish 1.160 (1:260 / 2:18 / 4:1, sum n^2 348) | 1.160, 348, clusters {1:260, 2:18, 4:1}, 279 questions | counts.py | CONFIRMED (the REGISTRATION's (a) 342 / 1.14 and "21 questions carry two matches" are wrong: see D-5) |
| 4b | DEFF 1.09 measured (clustered bootstrap, B 2000, seed 42) | verdict-change indicator: 1.077 / 1.066 / 1.067 (B 20000; seeds 42, 1, 2). Implied by the printed SEs: (0.0170/0.0162)^2 = 1.10. The DEFF of the DECIDING indicator (double change): 0.999 / 0.974 / 0.993 | support.py | PARTLY: the number reproduces within bootstrap noise, but it is the DEFF of a different statistic (D-3) |
| 4c | n_eff 274 | 300/1.09 = 275.2. The printed "300 / 1.09 = 274" uses the unrounded DEFF (about 1.094) and does not reproduce as printed | arithmetic | PARTLY (display, D-7) |
| 4d | MDE 6.22 (Poisson), 6.50 with the DEFF carried; distance 7.14; margin 0.64; SCOREABLE | Poisson mu80 9.0754, excess 6.2190; x sqrt(1.09) = 6.493; distance 7.1436. **Margin robustness**: Kish 1.16 as the DEFF gives MDE 6.70, margin 0.45; the double-change DEFF (about 1.0) gives margin 0.92; the break-even DEFF is 1.319. Under the alternative that matches a conditional-on-T test (the exponentially tilted conditional null), MDE = 5.45 (mean 8.31), margin 1.69, and power at mean 10 is 0.947 (Poisson 0.870) | support.py | CONFIRMED (SCOREABLE survives every DEFF source considered; the Poisson family is the wrong but conservative alternative, D-4) |
| 5a | C2: E_rev 0.2164 (pooled), 0.2018 per order; P(0) 0.805; exp(-2.9) 0.055 | positional pooled 0.2164, per order 0.2018, **contestant-frame pooled 0.2518** (P(0) 0.777); exp(-2.9) 0.0550 | c23.py | CONFIRMED to the digit; the pooled matrix mixes frames (D-6) |
| 5b | C3: E[verdict changes] 37.38 = 37.16 + 0.216; share 0.9942 against 26/26 observed | 37.38, 37.16, 0.9942 (contestant pooled 0.9934; per order 0.9946) | c23.py | CONFIRMED |
| 5c | C4: n2 10 of 279, T 57/558, E0 2.865, p 0.0001, region >= 7 | 279, T 57, n2 10, E0 2.86535, P 9.84e-5, region >= 7 | nulls.py | CONFIRMED |
| 5d | P1 10 in [8, 12]; P2 39 in [35, 43]; P3 p <= 0.001; P4 E_rev in [0.02, 1.0] with P(0) >= 0.37; P5 >= 0.90 | 10, 39, 1.05e-4, 0.20 to 0.25 in every frame (P(0) >= 0.777), 0.9934 to 0.9946 | above | CONFIRMED: P1-P5 HELD |
| 5e | the consequence: no match-level floor from 0.098 or 0.057 by independence arithmetic; TRACE-TRUNCATION does not re-price | the pooled-rate independence arithmetic over-predicts the match-level change count (37.2 to 38.3 against the observed 26). But the SAME arithmetic, stratified by pass-1 configuration, predicts 25.2 against 26 (in-sample) | c3strat.py | CONFIRMED for the pooled rates 0.098 and 0.057 named; the "anywhere in the record" clause of the FALSIFIER is broader than the evidence (D-2) |
| 6a | the R1 gate compares rather than prints | L225-L232: `miss` is computed and raises SystemExit | read | CONFIRMED (a real gate) |
| 6b | the pass-2 sha256 is checked | L204: pass 2 sha256 is **printed, not compared** (the cfg carries `cache1_sha256` only); the value is correct (checked by me) | read + sha256sum | PARTLY (D-8) |
| 6c | schema identity | real, except for the {provider1, provider2} exemption, which is admitted only when absent from pass 1 (selftest-covered) | read | CONFIRMED |
| 6d | the pool guard line | `assert_pool_of_record` runs on the run path (pool_check defaults True; False only inside the selftest). L189 prints "passed" unconditionally, even when pool_check is False, but no CLI path reaches that. The guard certifies the pool registry and the set hash; it does not check that the 279 qids are pool members (that rests on the set hash) | read | CONFIRMED on the run path; LOW (D-9) |
| 6e | a selftest proving that C1 discriminates dependence from independence | the fixtures are i.i.d. at a COMMON rate (reads HELD) and a both-cells co-change pair (reads FAILED). There is **no heterogeneous-but-independent fixture**, which would also read FAILED | read L516ff | the construct-validity gap behind D-1 |

## 3. Is the null the right one? (the reviewer's unregistered analysis, DESCRIPTIVE)

The exact conditional null makes all 600 cells exchangeable, so it tests **independence and a common per-call rate jointly**. The per-cell change rate is 10.6 times higher in pass-1-TIE matches: 46/150 = 0.307 against 13/450 = 0.029 in pass-1-decisive matches. Exact stratified nulls (the convolution of per-stratum closed forms, n2 = 10):

| stratification (all but the last are fixed before pass 2 or symmetric) | E0 | P0(n2 >= 10) | region | 10 is |
|---|---|---|---|---|
| none (registered) | 2.856 | 0.0001 | >= 7 | INSIDE |
| pass-1 verdict TIE / decisive | 7.120 | **0.103** | >= 12 | **OUTSIDE** |
| pass-1 cell configuration (decisive / flip / one-TIE / both-TIE) | 7.568 | 0.145 | >= 12 | OUTSIDE |
| pass-2 verdict TIE / decisive (the symmetric choice) | 6.580 | 0.057 | >= 11 | OUTSIDE |
| pair_kind x pass-1 state | 7.313 | 0.124 | >= 12 | OUTSIDE |
| pass-1 mean confidence quartile | 4.856 | 0.0068 | >= 9 | INSIDE |
| anchor / ref_correct / pair_kind alone | 2.75 / 2.82 / 3.02 | 0.0001 / 0.0001 / 0.0002 | >= 7 | INSIDE |
| cell-level: pass-1 cell vote TIE? (MC 200k) | 3.381 | 0.0004 | >= 8 | INSIDE |
| (endogenous) joint pass-1 x pass-2 state | 11.96 | 0.91 | >= 17 | OUTSIDE (conditions on the outcome; not a valid test, shown for bounds) |

- A cell-level covariate does not absorb the excess, but the match's pass-1 state does. So change propensity is shared at the **match** level. With 2 cells per match and 1 retest, "two calls dependent given the match" and "calls independent given a match-level propensity that varies across matches" are observationally equivalent. A two-class mixture (8% of matches at per-call change 0.62, the rest at 0.053, cells independent within a class) reproduces 251/39/10 exactly: the d-distribution has 2 degrees of freedom and the mixture is saturated. **C1 cannot, in principle, separate dependence from heterogeneity.**
- Residual, 3 events: in the pass-1-decisive stratum, n2 = 3 against E0 0.17 (P0 0.0003; within the low-confidence decisive half, 3 against 0.43, P0 0.004). All three are (A,A) -> (TIE,TIE). This is a within-stratum co-change signal, but it rests on 3 events and cannot exclude finer heterogeneity: those matches may be latent near-ties whose pass-1 decisiveness was a draw. DESCRIPTIVE.
- Of the 10 double changes, 6 are pass-1-TIE matches that stay TIE. In 4 of those 6, both orders swap position preference together ((A,B) <-> (B,A) contestant, i.e. both calls favour the first-shown answer in one pass and the second-shown in the other): (A,B) <-> (B,A) twice, and (TIE,B) -> (A,TIE) twice. The other 4 double changes move both cells to or from TIE. This is noted, not tested.

## Defects

- **D-1 HIGH (the reading overclaims; C-7 flavour: the reading substitutes a mechanism for the tested joint hypothesis).** "within-match dependence ... more often than independent per-call change allows (a property of the judge on these matches)" claims more than C1 licenses. C1 rejects independence **at a common per-call rate**. Stratified by the pass-1 verdict state alone, n2 = 10 is outside the rejection region (p 0.103). FIX: the registrar inserts a bracket after the reading: "[QUALIFIED 2026-09-23 by the post-run review: C1 rejects the joint model (independent per-call change at ONE common rate). It does not separate within-match dependence from match-level heterogeneity of change propensity; stratified by pass-1 TIE/decisive state, n2 = 10 lies outside the stratified region (p 0.10). The accurate reading is 'the two orders of a match co-change: change propensity is a match-level quantity'.]" C1 FAILED stands as scored. Its content is "match-level co-change", not "judge-internal dependence".
- **D-2 MEDIUM (the FALSIFIER's scope).** "forbids deriving any match-level floor from a per-call rate by independence arithmetic anywhere in the record" is broader than the evidence. Independence arithmetic at ONE POOLED rate fails: it predicts 37.2 to 38.3 verdict changes against 26. Independence at state-conditional rates (pass-1 configuration) predicts 25.2 against 26 (in-sample, descriptive). FIX: narrow it to "from a single pooled per-call rate (0.098, 0.057)". The TRACE-TRUNCATION "NO RE-PRICE FROM THIS TEST" stands, because it names exactly those pooled rates.
- **D-3 MEDIUM (the DEFF source is a different statistic).** Support (b) measures the DEFF of the verdict-change indicator (26/300), not of the deciding double-change indicator (10/300), which is about 0.97-1.00. The registration named this source, so this is not a builder substitution, but the DEFF is not the deciding statistic's. Carrying any DEFF onto an exact permutation null over cells is also heuristic, because the null has no cluster term. The effect is conservative here (margin 0.64 against 0.92 at the correct DEFF). FIX: future registrations measure the DEFF on the deciding indicator and state it as the source.
- **D-4 LOW (MDE family).** The Poisson alternative is overdispersed against a conditional-on-T count: the null variance is 2.33 at a mean of 2.86, and n2 <= 29. The tilted conditional alternative gives MDE 5.45 against 6.22. Conservative, so SCOREABLE stands. FIX: note the conservative direction in the record.
- **D-5 LOW (registration Support (a) arithmetic).** The registration's "21 questions carry two matches, sum n^2 342, Kish 1.14" is wrong: the clusters are 18 x 2 + 1 x 4, sum n^2 348, Kish 1.160 (C4's stated reason repeats the 21). The outcome prints the correct 1.160 without flagging the gap. FIX: an insertion bracket at the registration's (a).
- **D-6 LOW (C2 frame mixing).** The "pooled" transition matrix pools order-1 contestant labels with order-2 POSITIONAL labels (vote2_raw). Its A->B / B->A cells therefore mix contestant and position semantics. In the contestant frame the pooled E_rev is 0.2518, not 0.2164. P4 holds in every frame. FIX: print the contestant-frame pooled figure beside it.
- **D-7 LOW (display).** "(c) n_eff = 300 / 1.09 = 274" does not reproduce as printed (275.2). The code divides by the unrounded DEFF, about 1.094. FIX: print the DEFF to 3 dp.
- **D-8 LOW (printed, not compared).** The pass-2 sha256 is printed, never asserted (cfg has no `cache2_sha256`). Its value is correct (9e2f4b7c...). FIX: pin and compare both.
- **D-9 LOW (pins name no hash kind).** The brief's outcome sha256 1a8d802e... is the CRLF rendering. The LF bytes are sha256 2b28ee17..., blob a2df609d... (rule 8). L189's "[POOL] ... passed" prints even when the guard is skipped (selftest only). FIX: name the kind in the record's pin; print "[POOL] SKIPPED (selftest)" on that path.
- **D-10 MEDIUM (selftest construct gap).** No fixture is heterogeneous but independent, so the selftest cannot show that C1 FAILS on heterogeneity alone. This is the defect that lets D-1 pass unnoticed. FIX: for any successor, add the fixture, with its expected reading, before any re-use of the instrument.

## Proposed sentence of record

"TIE-MECHANICS (zero calls; caches pass 1 5142795b / pass 2 9e2f4b7c, re-counted by the reviewer to the digit): of 300 canary matches, n2 = 10 changed BOTH order votes between passes, given T = 59 changed cells of 600. The exact conditional null under independent change at ONE common per-call rate gives E0 2.856, SD0 1.528, P0(n2 >= 10) = 0.0001 (region n2 >= 7), so C1 FAILED as registered; P1-P5 HELD; SCOREABLE (MDE 6.22-6.70 by DEFF source, distance 7.14). C1 shows that change propensity is a match-level quantity (the two orders co-change); it does not separate within-match dependence from heterogeneity of change rates across matches: stratified by pass-1 TIE/decisive state (per-cell change 0.307 vs 0.029), n2 = 10 lies outside the stratified region (p 0.10). Consequence: no match-level floor may be derived from a single pooled per-call rate (0.098, 0.057) by independence arithmetic (it predicts 37 verdict changes against the observed 26); TRACE-TRUNCATION does not re-price from this test."

## What this run does not show

- That the two calls of a match are dependent **given** the match: this is not separable from match-level rate heterogeneity at 2 cells x 1 retest.
- A mechanism: position preference, answer similarity or content. The 4-of-6 position-preference co-swaps among the pass-1-TIE double changes are a lead, not a result.
- That "0 reversals" is a judge property: structurally undetectable (no lower region; C2 P(0) 0.78-0.82).
- That state-conditional independence arithmetic is invalid (it fits in-sample: 25.2 against 26).
- The within-decisive-stratum excess (3 against 0.17) as a finding: 3 events, unregistered.
- Anything about another judge, corpus or set, or any fidelity or accuracy number.

## Verdict

NUMBERS CONFIRMED to the digit: R1, n2, n1, T, E0, SD0, the tail, the region, C2-C4, P1-P5, Kish, and the MDE arithmetic; the DEFF reproduces within bootstrap noise. C1 FAILED stands as registered. The READING is PARTLY (D-1 HIGH: it claims dependence where the test shows match-level co-change, dependence or heterogeneity). The CONSEQUENCE is CONFIRMED for the pooled rates named. The FALSIFIER's "anywhere in the record" should be narrowed (D-2). Nothing blocks recording the outcome, provided the D-1 bracket is inserted with it.
