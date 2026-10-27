# POST-RUN REVIEW — ARCH-V2-PILOT-K46 (k = 37), run2 79fad3a, --analyze of record 0bfa148

Reviewer: adversarial-reviewer, 2026-09-25. Zero judge calls.

Everything below was read-only:
- store `experiment_results/archv2/pilot_k46/pilot_k46_verdicts_run2.db`, sha256 44724d25aa8653b49cef5ea85e99016f4e27f1c99819edc62073416eeec27793;
- journal `...run2.db.invocations.db`, sha256 466c0f57237f0d3950434f7a3024b2be50d4a5d74580a70093ff3b230c60649a;
- the retired journal (995087c3...);
- the eval view (e35b7518...);
- the STACK-NORUBRIC and STACK-v2 grok caches.

Each was opened `mode=ro&immutable=1`. The committed output and record files are unchanged: `git status --short experiment_results/archv2/pilot_k46/ | wc -l` = 0. Scripts are in the session scratchpad `postrun/`.

## VERDICT (first)

**VALID. C1's reading "P EXCLUDED" STANDS as printed.** Every C1 number reproduces to the digit, and the reading is robust to every check below.

Two items are owed as disclosures in the outcome of record; neither is a defect of validity:
- F-1: the DEFF's Monte Carlo precision, supplied here;
- F-2: the position bias of the reference-NONE branch.

The predictions P1, P2, P2b, P3a, P3b, P4 and P5 are HELD as scored. The FALSIFIER did not fire.

What this does NOT decide: the board size. That is the author's decision, beside the simulator and the memo.

## Numbers of record (reproduced; how is in the next section)

| quantity | value | reproduced by |
|---|---|---|
| board | 2,664 scheduled matches; 2,661 usable (A 1,039 / B 1,022 / TIE 600; INVALID 3); health 1,332, math 1,329; tie share 0.2255 | own SQL + own combiner (`board.py`) = the store's `match_status` view |
| nu_2(37), per anchor | 0.9874; health 1.0129 (called 356 of 666), math 0.9620 (440 of 666) | the instrument's edges_fast on the REVIEWER'S board, registered stream `boot/point/k37`: to the digit |
| nu_2(12), per anchor | 0.1299; health 0.1326 (30 of 66), math 0.1272 (43 of 66) | same, `boot/point/k12`: to the digit |
| beta-hat | 1.8014 | ln(0.98742 / 0.12986) / ln(37/12): to the digit |
| C1 bootstrap | B 2,000, 0 non-finite; SE_boot 0.2240; SE_dec = sqrt(0.2240^2 + 0.20^2/2) = 0.2649 | recomputed from c1_boot.records.jsonl (the manifest's sha matches, 2,000 lines). Replicates 0-3 re-run from the registered stream "boot" on my board: equal to 1e-12 |
| interval, reading | [1.2821, 2.3207]; lower 1.2821 > 1.06, so P EXCLUDED; upper 2.3207 >= exact M 2.052941, so not M EXCLUDED | own arithmetic |
| measured DEFF | Var_q 0.050196 / Var_m 0.046542 = **1.0785** | own recomputation from both records files. Match replicates 0-2 re-run from the registered stream "deff/mboot" in the plan's order (order_sha 89219fc9...): equal to 1e-12 |
| DEFF, MC precision (**the missing statement**) | SD(ln DEFF) = 0.0447 (normal theory, B 2,000 x 2) or **0.0532** (kurtosis-adjusted: kurtosis 4.19 / 3.46); **DEFF 1.08, 95% MC interval [0.97, 1.20]**; the bootstrap-of-replicates interval is [0.969, 1.199] | `recstats.py`. The interval CONTAINS 1: the measured question clustering of beta-hat is indistinguishable from none at this B |
| n_eff | 2,661 / 1.0785 = **2,467.3** (MC range 2,223-2,738), n = usable dual-order matches | - |
| MDE (80%) | 2.80 x 0.2649 = **0.742**; with the 1.25 transport inflation 0.927; the P-M separation 0.9929 exceeds both: SCOREABLE at the measured support (planning 0.2928 / 0.82) | - |
| C1b | matched beta 2.0183 [1.4939, 2.5428]; matched level 0.9036 (between P 0.3556 and M 1.0878) | taken from the outcome, not recomputed |
| C1c | slope 1.810 [1.521, 2.410] | taken from the outcome, not recomputed |
| accounting | journal 5,328 (5,328 RETURNED, 0 unresolved, all 2026-09-25) + prior 24 (retired: 24 RAISED) = 5,352 = ledger ARCH-V2-PILOT-K46 rows 24 + 24 + 5,304; store 5,328 attempts (0 errored, max attempt_no 1) = 5,328 verdicts; day total 5,354 of 14,000 | own SQL + day_calls_2026-09-25.json |

## Predictions under the F3 ruling (programme L18077-L18082) and the owed checks

- **P3a HELD** (C1 reads "P EXCLUDED"; forecast 0.79). **P3b HELD** (C1 does NOT read "M EXCLUDED"; forecast 0.87).
  - Both are exactly as the instrument printed.
  - P3b FAILED iff the falsifier fires. It did not fire (upper 2.3207 >= 2.052941).
- P1: C0 PASS. P2: 1.801 in [1.4, 2.4]. P2b: 0.9036 in [0.6, 1.3]. P4: 2,664 in [1,540, 2,664], t = 0.
- **G1 CONFIRMED:** P5's posted = 5,352 = journal 5,328 + prior 24 <= 8,000. Unusable 3 of 5,328 order verdicts = 0.056% <= 1%.
- **F4 text:** printed VERBATIM beside C1 and C1b, with the analysis's own counts (NONE 1,846 of 2,664 = 69.3%; system turn d0c524bb... EQUAL).
- **Code-identity line:** "DIFFERS ... does not compare" is printed: store script_blob `...+archv2_pilot:15e00bb7ee690594`, analysis lf16 098302869a14bd65. As ruled in 0c10ea2 / 7090a32.
- **The pilot-12 incident is CARRIED:** the 24 phantom invocations appear in C0 (f) ("+ prior (retired stores) 24"), in P5 and on the ledger. The retired journal is sha-pinned at 995087c3 and read here.

## Validity

1. **Counts:** see the accounting row. No orphan, no RAISED, no retry, no -wal / -journal beside the store.
2. **The 3 INVALID order verdicts** (K46-07c87066... order 1; K46-3f81c7a4... order 2; K46-b8a42bc8... order 2):
   - finish_reason 'stop', 306-365 completion tokens.
   - The raw JSON stops inside the "comparison" or "critique_b" field, with no verdict key. All three are arithmetic self-corrections in math questions ("wait, ... is 1/4*2/3 really 1/6?").
   - All three are reference NONE. Each voids its match: 3 of 2,664, dropped from C1's board as registered.
   - 0.056% is far below P5's 1%.
3. **Order balance:**
   - FIRST 2,679 vs SECOND 2,215 of 4,894 decisive order votes. FIRST share **0.5474 [0.5333, 0.5614]** (Clopper-Pearson; p = 3.5e-11 against 0.5).
   - The recipe's measured record: STACK-NORUBRIC norubric arm (same system turn) 0.5229 [0.4999, 0.5459]; STACK-v2 grok session of record 0.5273 [0.5104, 0.5440].
   - **Split by the reference branch:** reference ONE 0.5083 (762 / 737, inside the recipe's range); **reference NONE 0.5647** (1,917 / 1,478), which is ABOVE the measured range.
   - So the excess position preference lives in the branch STACK-NORUBRIC never measured (F4).
   - The dual order with TIE on flip neutralises it by construction. Match-level flips are 507 of 2,664 (0.190); ties in both orders 93; combined TIE 600. It costs decisiveness, not direction.
   - Both rungs use the same recipe, so it does not enter beta asymmetrically by design. It is DESCRIPTIVE, not a validity failure.
4. **TIE 431 order votes** (8.1%). Combined TIE 600 = 93 double TIE + 507 flips. Both are inside the recipe's mechanics; the tie share of the board is 0.2255.

## Sanity of the substance

- **Anchor draw (2 anchors).**
  - Per-anchor beta: health **1.8057** (bootstrap SE 0.278; unwidened [1.261, 2.350], P excluded alone); math **1.7968** (SE 0.436; [0.942, 2.652], NOT P excluded alone).
  - The two points differ by 0.009, far inside the registered between-anchor SD 0.20. The reading rests on the 2-anchor mean, as registered.
  - The widening constant can grow before the reading changes: P EXCLUDED survives any between-anchor SD up to **0.431**, 2.16 x the registered DEV constant 0.20.
  - The anchor-to-anchor variance itself is NOT estimable from 2 anchors (Support (g), structural).
- **Inner Monte Carlo seed.**
  - The point uses one inner seed (B_inner 300). Over 21 inner seeds (records c1_integrated) beta ranges [1.7045, 2.3803], median 1.9430. The lowest lower end is 1.7045 - 1.96 x 0.2649 = **1.185 > 1.06**, and no seed gives M EXCLUDED. The reading holds for EVERY inner seed.
  - The C1 bootstrap is shifted upward (mean 1.916, percentile [1.529, 2.396]). The percentile form gives the same reading.
  - Independent fit, my own MM Bradley-Terry with my own question bootstrap (different draws), same nominal definition: nu_2(37) 0.9601, nu_2(12) 0.1185, beta **1.858**. Inside the inner-seed spread.
- **arx_0314, leave-out: DESCRIPTIVE, DECIDES NOTHING** (`arxout.py`).
  - Setup: arx_0314 removed from both rungs (k 36 vs k 11; 2,517 usable matches); reviewer-named streams; B 400.
  - Results: nu_2 0.9060 / 0.0868; beta **1.978**; SE_boot 0.212; SE_dec 0.255; [1.478, 2.477]. Lower > 1.06 (P excluded); upper >= that pair's exact M 2.0566 (not M excluded).
  - The same reading without the model. Its presence moves the point by about -0.18, inside the inner-seed spread.
- **The throughput slowdown** (the order-verdict latency median rose from 3.3-4.0 s to 10.3 s in the last decile, from about index 4,800):
  - response_model is grok-4-1-fast-non-reasoning on all 5,328 rows, no change.
  - The last 200 order verdicts are the highest match_ids: posting runs in id order, so effectively a random subset.
  - Their ORDER-level TIE share is 0.035 (7), against 0.083 elsewhere. That is Fisher p 0.012 overall and p 0.017 against the same pairs' other verdicts. Among the 5,129 overlapping 200-windows it sits at the 1.9th percentile. Read post hoc: one window chosen because it was slow.
  - At the MATCH level, which is what C1 reads, the 100 usable matches touched carry 21 combined TIEs (0.21 against 0.2255): neutral.
  - Removing them moves beta by -0.12 +- 0.10 (5 inner seeds; `slowsens.py`), inside MC noise. Verdict-neutral for C1; disclosed (F-3).

## Findings

- **F-1 MEDIUM (disclosure owed; A3 / delta READY 3 ruling on deviation 1).** The outcome prints DEFF 1.079 with NO MC precision. Supplied here: SD(ln DEFF) 0.0447 normal-theory, 0.0532 kurtosis-adjusted, 95% MC [0.97, 1.20], containing 1; n_eff MC range 2,223-2,738. The registrar records it beside the outcome's DEFF line by insertion, and the outcome file is not edited. The DEFF decides nothing.
- **F-2 LOW (disclosure).** The position preference is above the recipe's measured range in the reference-NONE branch (0.565 vs 0.52-0.53). It is neutralised by dual order, and it is part of F4's "UNMEASURED" branch. Record it with F4.
- **F-3 LOW (disclosure).** The slowdown's last 200 order verdicts carry fewer order-level ties (post hoc, p about 0.01-0.02). Match-level and C1 are neutral.
- **F-4 LOW (record hygiene).** The ledger's two 24-call rows carry the SAME label "pilot#1 ARCH-V2-PILOT-K46-run1": the retired store's and run2's pilots share RUN_ID. They are distinguishable only by ts (06:06:10 vs 07:14:34). The registrar's record should name them.
- **F-5 INFO.** C1 is P-excluded only on the 2-anchor mean; math alone is not (SE 0.44). The registered design reads the mean, so this is not a defect. Any sentence of the form "each anchor shows a super-P exponent" is refused.
- **F-6 INFO.** The inner-seed MC noise of the point beta (about 0.15 SD at B_inner 300) is of the same order as SE_boot's sampling part. It is inside the bootstrap SE, because every replicate redraws inner streams. Any stage-1 design at this B_inner should expect it.

## Prior results touched

- **ARCH-V2-PILOT-K46** (results record, ledger row): run and outcome VALID; the reading P EXCLUDED; predictions all HELD.
- **The board-size question, ruling 3 (a) / the memo / the simulator:** the falsifier did NOT fire, so planning on the M / X columns stands. beta-hat 1.80 sits beside the memo's exponents, deciding no size.
- **ARCH-V2-G22 (L12 0.1078):** used for the C1b bars only.
- **GROK-CALIB:** the frozen pair was transported, with the planning-scale label printed.
- **STACK-NORUBRIC:** system turn identity; the position-share comparison (F-2).
- **Stage 1:** REUSE CONDITION (v) is unchanged. These verdicts are stage-1 data only if stage 1's roster sha256-text = 3a3204cc...6f91.

## What this does NOT show

- A board size, which is the author's.
- A 14-anchor nominal as measured (Support (g)).
- The between-anchor variance.
- GENERIC_SYSTEM + GENERIC_RUBRIC's accuracy on E-J's layer: there is no key-based quality readout here, and C3 decides nothing.
- Any frontier order.
- That the order-level tie dip at the slowdown has a cause.

Scripts (session scratchpad `postrun/`):
- `board.py`: own board and combiner.
- `repro.py`: point reproduction plus the independent Bradley-Terry fit.
- `reps.py`, `mreps.py`: replicate reproduction.
- `recstats.py`: SE, interval, DEFF, MC precision, per-anchor results.
- `arxout.py`: arx_0314 leave-out.
- `validity.py`: counts, INVALID, position balance, throughput.
- `slowsens.py`: the slowdown sensitivity.
