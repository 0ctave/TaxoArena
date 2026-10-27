# Budget minimum for a calibration status beyond UNDETERMINED (arena specialist, zero calls, no record written)

Sources: FRAMEWORK L61-L63 (Stage 3), L95-L99 (Stage 6), L101 (status rule), L255 (Limits); `calibration_status.status_word()`; GROK-CALIB (P:L3914); CERT-UNDER-FILTER (P:L14649, b4b1688/3905a71); `ktd_check.txt` L162; `budget_lomo.txt`; multi_corpus_design L250; arena.md; SYNTHESIS §1, §5, R11, R12. Figures not in the record are marked **(arith.)**. All edge counts are keyed MMLU-Pro-style edges (pairs × anchors) with frontier-internal and key-tied edges dropped (factor 2,538/2,660 = 0.954, merged board).

## 0. What "beyond UNDETERMINED" means

`status_word(nominal, observed)` returns UNDETERMINED whenever nominal < 9, **whatever is observed**. So the chance of getting past UNDETERMINED is P(nominal ≥ 9). Nominal is Σ(1−c~) over called edges and is computed without the key. That makes it a property of the design, and it can be forecast at zero calls. The 0.79 quoted in SYNTHESIS is a different quantity: the conditional power, once nominal ≥ 9, to call MISCALIBRATED against a true 2x (P(Pois(18) ≥ 15)).

Once nominal ≥ 9, the likely word is **MISCALIBRATED on the all-label count**:
- The widener's recorded ratios are 1.7-2.5x all-label and 0.9-1.7x established (GROK-CALIB 2(1)/1.11; LOMO 3(2)/1.18).
- At nominal 9, P(MISCALIBRATED | 1.8x) = 0.65 (arith.).
- The registration must fix which count feeds `status_word` (the record's precedent is all-label). It must also name what MISCALIBRATED does to ORDERED-JUDGED; my suggestion is withdrawal to BANDED-JUDGED with the measured ratio printed.

## 1. The unknown that sets every price: nominal per anchor, ν(k)

The record gives two Mistral points, and they are not like-for-like:
- **x12:** k = 12, LOAO nominal 1.27 over 14 anchors, so ν = 0.091.
- **Merged board:** k = 20, per-anchor widener + decline nominal 2.18 over 2,538 edges, so ν = 0.156.

These points give three readings of how ν scales with the roster size k (arith.):

| reading | rule | MMLU-Pro, 46 models × 14 anchors (13,825 edges) | A-union, 18 models × 52 strata (7,591) |
|---|---|---|---|
| P: ν ∝ k^1.06 (fitted through the two points) | nominal ≈ 0.0078 per model-anchor slot | **5.3** | 7.2 |
| M: nominal per edge constant at 0.00086 (merged) | ∝ edges | **11.9** | 6.5 |
| X: nominal per edge constant at 0.00138 (x12) | ∝ edges | **19.1** | 10.5 |

The A-union board (about 159k calls) reaches 9 only under reading X. **Its P(leave UNDETERMINED) is nearer 1/3 than 0.8.** Arena §5 sized it on the x12 rate alone. That was my error, and this table corrects it.

## 2. The levers

**(1) Models per cell.** Calls per edge are 2N whatever k is, so a bigger roster is cheaper per edge only because N can fall. The Bradley-Terry SD of θ_a − θ_b scales about as 1/√(N(k−1)), per model's matches. The filter's equivalence (ARENA-V3-COMPILED: board rho 0.986 against 0.972 at 58% of the calls) puts x12's s = 0.248 at N(k−1) ≈ 64 filtered. So N ≈ 64/(k−1):

| k | N needed | calls per edge | matches per unit nominal, reading P / M (arith.) |
|---|---|---|---|
| 18 | 4 | 8 | 4,390 / 4,880 |
| 46 | 2 | 4 | 5,500 / 2,440 |

Under reading P the price per unit nominal is flat in k: nominal and matches both grow ∝ k. Under reading M, 46 models is 2x cheaper. **A large roster is never dearer, and it is the only lever that multiplies edges without new corpora.** The ceiling is supply. P gives 0.0078 nominal per model-anchor slot, so 9 needs about 1,150 slots. Every keyed stratum the programme has gives about 1,130: MMLU-Pro 46 × 14 = 644, plus BBH/MuSR 18 × 27 = 486. That is nominal about 9.0 **at best** (arith.).

**(2) Matches per edge.** The bar to call is |m| ≥ 1.96√(s² + τ(A)²), using GROK-CALIB's unfiltered τ = 0.098 / 0.263 / 0.508 / 0.707 at A = 0.3 / 0.6 / 0.8 / 0.9. The reuse DEFF is taken at the implied ICC 0.085 (arena §2.1) (arith.):

| design | reuse per question | DEFF | s | bar at A = .3 / .6 / .8 / .9 |
|---|---|---|---|---|
| x12, k 12, N 10 | 2.7 | 1.14 | 0.248 | 0.52 / 0.71 / 1.11 / 1.47 |
| k 46, N 1 | 4.2 | 1.27 | 0.305 | 0.63 / 0.79 / 1.16 / 1.51 |
| **k 46, N 2** | 8.4 | 1.63 | 0.244 | **0.52 / 0.70 / 1.10 / 1.47** |
| k 46, N 3 | 12.6 | 1.99 | 0.220 | 0.47 / 0.67 / 1.09 / 1.45 |

- Above A ≈ 0.6, τ sets the bar and N does not matter; this is M2's flatness. The edges that carry the nominal sit there.
- **N = 2 reproduces x12's bar at every A.** N = 1 raises the low-A bar by 21% and is admissible only if G22 shows ν and utility hold.
- At the measured CERT ICC of 0.0112 (DEFF 1.64 at Kish m 58), N = 2 gives s = 0.215, which is better.
- N = 10 (FRAMEWORK L63, "DESIGN as a cap") must be re-registered as the deployed density. Otherwise the calibration covers a schedule that is never shipped.

**(3) Which strata.**
- Drop MATH and IFEval: the filter is inert there, and they would need a separate fit.
- Drop GPQA: its three strata are prompt variants of about 198 items, one family under CK-CLOSE-v1, so their errors are replicas.
- Keep BBH (24 strata) and MuSR (3) only as a **reserve stage**. They exist for 18 models only, carry about 72 EVAL questions per stratum at f 0.30 (below MMLU-Pro's calibration-cell support of 201), and need their own (b0, b1). Summing their nominal with MMLU-Pro's is a registered pooled claim with corpus-specific parameters (guard 12).
- **MMLU-Pro with 46 models carries the certificate alone under readings M and X, and not under P.**

**(4) Filter and π.**
- In a fixed-N design the filter does not cut the calls per pair. What it does is make N = 2 informative (the 58% equivalence), and it defines the deployed estimand.
- Its standing risk: b1 is not identified under the filter on x12 (−0.25, Δdev 0.01; CERT C3). The 46-model board has about 16x x12's 752 established edges (arith.), so a power failure would be cured, but a structural one would not.
- The AGREE audit adds **nothing to the status** because it is fitted separately. Price it as a fixed slice under its own Support section (e.g. 600 matches, 1,200 calls), not as a rate: π = 0.10 would add about 5.5k calls to D1 (arith.).

**(5) Reuse cap r ≤ 4.** On MMLU-Pro at f 0.30 there are about 3,450 judgeable EVAL questions, so the cap allows at most 13,800 matches in total. At N = 2 that is at most 6,900 edges (k ≈ 32), and nominal would be 3.6 / 5.7 / 9.1 (arith.). **Under the cap, nominal 9 is out of reach except under reading X.** The cap is an efficiency heuristic, not a validity guard: the clustered bootstrap prices reuse into s. My recommendation for the calibration board is r ≈ 8.4, with the measured DEFF printed. G24's falsifier "DEFF > 1.6" was set for r ≤ 4 (predicted 1.19-1.34); at r 8.4 the prediction is 1.63, so the bar must be re-registered. The alternative is raising f to about 0.6, which is the tree specialist's and the author's decision.

**(6) Sequential designs.** Nominal needs no key, but the LOAO widener and the decline both use it. The stop statistic is therefore:
- **key-blind nominal:** c~ under the FROZEN GROK-CALIB unfiltered (b0, b1) = (−3.3172, +3.3001), no decline, computed from verdicts and free A only;
- the key join stays sealed until the registered decision is recorded.

A verdict-measurable stopping time does not change the key's conditional law given the verdicts, so it is not optional stopping on the test statistic (G22 must confirm this). Epoch boundaries are guard checkpoints only. Two alternatives are rejected:
- a group-sequential Poisson test on the observed count: it reads the key mid-run and has no alpha-spending in the rule;
- splitting anchors into question halves to double the slots: it makes correlated replicas, as the Llama-3.1-70B residue shows.

**(7) Lower registered bars.** Two claims are cheaper than the full status word, and neither is "calibrated". Powers are arith., one-sided 95%.

| claim | pass iff | power | what it buys |
|---|---|---|---|
| rate UB ≤ 2.5% (the certificate's own per-edge promise) | CP UB on wrong(est)/called ≤ 0.025 | 0.81 at 600 called (p 0.5%, DEFF 2) | weak: the raw certificate's 0.95-1.08% passes too |
| **rate UB ≤ 1%** | CP UB ≤ 0.01 | 0.82 at 1,000 called (p 0.3%, DEFF 1) or 2,000 (DEFF 2) | separates the v2 certificate from the raw rate; GROK-CALIB's 2/667 already reads UB 0.94% on the old recipe |
| **ratio UB ≤ 4x** | Poisson 95% UB(w)/nominal ≤ 4 | 0.81 at nominal 4.5 against a true 1.8x; 0.92 at nominal 6 | "not the raw 7-10x", at half the nominal of the status word |

A rate UB of ≤ 0.5% is out of reach (power 0.38-0.66 even at 5,000 called edges).

## 3. Candidate designs

LLM time is at 25-40 calls/min (SYNTHESIS §5). Every design needs fresh reasoning reference solves for its EVAL questions (≤ 3,450 for MMLU-Pro; their throughput is unmeasured). All are above the 4,000-match rule except D4.

| design | matches / calls | LLM h | nominal P/M/X | what it can reach (power) | risks |
|---|---|---|---|---|---|
| D0 A-union (proposal) | 79,600 / 159,000 | 66-106 | 7.2 / 6.5 / 10.5 | status word only under X, P ≈ 1/3; ratio UB ≤ 4x | R11 reuse 12; 8 inert strata; dominated by D1 |
| D4 no-go | 3,990 / 7,980 (20 models × 7 anchors × N 3) | 3.3-5.3 | 1.1 / 1.1 / 1.8 | rate UB ≤ 2.5% (≥ 0.94); ≤ 1% (0.5-0.8); status UNDETERMINED | one DEFF on the wrong indicator decides the 1% bar |
| D1 stage 1 | 13,826 / 27,650 (46 models × 7 anchors × N 2) | 11.5-18.4 | 2.6 / 5.9 / 9.5 | rate UB ≤ 1% (≥ 0.87); ratio ≤ 4x under M/X; status under X only | b1 under the filter |
| **D1 full** | 27,650 / 55,300 (46 × 14 × N 2) | 23-37 | 5.3 / 11.9 / 19.1 | ratio UB ≤ 4x under all three (≥ 0.85); status word under M/X (P ≥ 0.8 there) | ν(k) reading; non-Llama roster excludes the record's residue model; long CoT responses (tokens not priced) |
| D2 all keyed | ~40,000 / ~80,000 (D1 + BBH/MuSR 27 × 153 × N 3) | 33-53 | 9.0 / 15.3 / 24.5 | status word under M/X; ≈ 0.5 under P, the supply ceiling | pooled corpus-specific fits; BBH support below 201 |

## 4. Recommended start

**Stage 0 (0 calls): G22 plus the replay.**

**Stage 1:** D1 on 7 of 14 anchors, drawn at random by a registered seed and stratified by anchor size. The run is 46 models, N = 2, filtered, reuse ≈ 8.4, a fixed 600-match AGREE slice, and the G24 pilot inside it. Then the key-blind look:
- frozen nominal ≥ 9 + margin (the margin is set by G22): stop, unseal, and read the status word;
- projected 14-anchor nominal ≥ 4.5: run stage 2;
- otherwise: stop and publish the rate UB ≤ 1%.

**Stage 2:** the other 7 anchors. At the key-blind look, stage 3 (BBH/MuSR) runs only if the projected total crosses 9 with it. If not, stop with the ratio UB ≤ 4x.

**Ceiling:** 80k calls. **Expected:** 55k calls under M/X, 28k if X holds strongly. **One go covers the registered envelope.**

## 5. What G22 must confirm before any go

1. **Validity leg as registered:** 733/7 on 891 edges, the LOAO counts, and a Δdev range covering 2.26 and 4.47.
2. **ν(k, N) at zero calls:** subsample rosters of 8/12/16/20 models on the merged Mistral board (k ≤ 12 on grok_calib), and N of 2/3/5/full. Fit the exponent with a CI. If the CI reaches ≥ 0.9, only the ratio and rate claims are plannable.
3. **P(nominal ≥ 9) ≥ 0.8** for the chosen design at the fresh split's actual EVAL supply per anchor. That supply is known after the split and before any verdict.
4. **b1 identified in ≥ 80% of simulated re-draws under the filter.** If not, the fallback (binned gate or raw certificate) is named in advance.
5. **The key-blind stop:** P(MISCALIBRATED | calibrated simulated judge) ≤ 0.05; also the map from frozen-parameter nominal to LOAO-refit nominal.
6. **Overdispersion of wrong(established) across models and anchors** (the Poisson assumption; the residue is one model). Also the DEFF of the wrong indicator, which gives n_eff for the rate UB.
7. **DEFF at reuse 8.4,** with G24's bar re-registered to match.
8. **The 46-model roster:** extraction coverage D_c ≥ 0.95 per anchor; the frontier band taken from key tiers; A on the EVAL side.

## What this does NOT show

- ν(k) rests on two points, and they are not like-for-like (LOAO widener against in-sample widener + decline). All three readings are arithmetic, not measurements.
- The 58% filter equivalence is a board-rho result, not an s result. The ICC of 0.085 is implied, not measured per cell.
- No design here orders the frontier. No design transfers a nominal confidence off its roster, judge or schedule, and a non-Llama roster's rate says nothing about Llama-3.1-70B.
- Token cost, reference throughput and CPU time for B ≥ 2,000 on 46-model fits are unpriced (cost-estimator).
- The key-blind stop's validity is argued here, not simulated.
