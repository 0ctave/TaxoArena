# POSTRUN_FRESH-SIZE: adversarial review of the size/power readout for BZ-AXIS-CONFIRM-FRESH (benchzoom fresh-size b86c014..4676efb)

Reviewer: adversarial-reviewer, 2026-10-28. Authority: D-2026-10-28-1 (with D-2026-10-27-4/-5). Zero LLM calls; read-only on
both repos except this file. Object: benchzoom branch `fresh-size` (plan aa05068 -> code be75cf3 -> run 4676efb), outputs
`E:/benchzoom_demo/followups/fresh-size` (SHA256SUMS 54d0509b..., 5/5 OK), inputs = FRESH-DESIGN-SURFACE parts
(SHA256SUMS sha256 5aa498d2..., 65/65 OK after the run: nothing of record was written).

## Verdict

**NUMBERS CONFIRMED (exploratory planning readout, with qualifiers M-1, M-2); MERGEABLE (fast-forward onto master b86c014).**
Every MDE80 in the hand-back table, every T1/T2 row and every projection value reproduces from the design-surface parts with
my own code to machine precision. No n* is claimed. Two MEDIUM readings must be carried with the numbers: the central
n-exponent 0.5 is above every measured trend at the briefed rosters (M-1), and the serving question is framed on random
subsets of the EEE roster that do not describe either serving option (M-2). Neither changes a number; both change how the
roster-vs-n sentence and the author question may be worded.

## Per-claim table (deciding claims)

| # | claim | mine | status | sev |
|---|---|---|---|---|
| 1 | 15 cells of the n 7,058 table, cell central [band] / meter central | 225 projection values (50 rows x anchor/central/band lo/hi/trend) equal to projection.csv, max rel diff 2.1e-16; all 15 hand-back cells equal at 3 decimals | CONFIRMED | - |
| 2 | T2 at n 2,949 (e.g. R 69 P 0.310/0.182 ... G(V0\|L2+N) 0.125/0.082) | real_config.csv 300/300 rows equal (max rel diff 0); C3's five meter MDE80 equal | CONFIRMED | - |
| 3 | T1 800 rows; reproduces power.csv 180/180 | T1 800/800 (cell and meter, defined counts equal); my T2 vs power.csv in-range 180/180, diff 0 | CONFIRMED | - |
| 4 | cell vs meter columns | cell = `se_cell` (V0' leaf clustered; two-way + MC for D_K), meter = `se` (SE_cc + MC); DEFF0 = (cell/meter)^2; labelled "clustered (SUBSTITUTED), lower bound for rule B" in every file | CONFIRMED (C-7 disclosed) | - |
| 5 | projection: a 0.5 central / 0 edge, DEFF none/measured/linear, band = envelope x (1 -/+ e) | m0 50.4164, m1 79.2502, e_cell 0.09326 (G 58.49), e_cc 0.01303 (G 2,946); beta at R 69 P 0.224, D_K 0.120, D_N 0.219, G(N) 0.201, G(V0) 0.143 (44 pts; R 69's n 2,949 level is one design, 1 draw, so no pseudo-replication); R 35/18: 60 pts, G(V0) beta -0.067/-0.107 | CONFIRMED | - |
| 6 | EXTRAPOLATION label throughout | projection.csv 50/50, summary PROJ lines 50/50, SENS 30/30 "extrapolated"; GRID 0/15 (header says "projected"); hand-back table header unlabelled | PARTLY (L-3) | LOW |
| 7 | no n* | "NO n* IS LICENSED" printed; the n_eq row is an items-equivalent under a 0.5 and no DEFF growth, not an n* | CONFIRMED (L-5) | - |
| 8 | roster: R 69 -> 35 x1.34-1.60 (measured) | 1.342-1.603; R 18 1.923-2.507; R 10 3.056-4.329; b 0.433-0.759 (R 35/18/10) | CONFIRMED | - |
| 9 | n: 2,949 -> 7,058 x0.63-0.68 central, 0.57-1.29 band | 0.631-0.680; 0.572-1.286 (R 69/35/18) | CONFIRMED (numbers) | - |
| 10 | "So R 35 at 7,058 ≈ R 69 at 2,949" | central 0.854-1.068 (P2 prints 0.86-1.07, L-2); band [0.77-0.94, 1.65-1.84]; under each cell's measured trend 1.24-1.95 | PARTLY (M-1) | MEDIUM |
| 11 | central assumption contradicted for P and G(V0\|L2+N) | true, but incomplete: measured exponent below 0.5 in 15/15 briefed cells (cell -0.63..+0.43, meter -0.38..+0.48); negative in 9/15 (cell); trend above band high for P and G(V0) at R 69/35/18 and D_N at R 69 (0.2154 vs 0.2153) | PARTLY (M-1, L-4) | MEDIUM |
| 12 | S-RES x1.4 / 1.4-2.0 / 3.9-4.4; S-PP x1.38-1.65; coverage P 1.24/1.03 | factors equal to POSTRUN_FRESH-RULES-SIM M1 and POSTRUN_PLANTED-POWER Q1; R 69 central S-RES P 0.295, D_K 0.139-0.199, G(V0) 0.325-0.367; coverage recomputed | CONFIRMED | - |
| 13 | roster-subset CV 0.14-0.38 (R 18/35), meter 0.06-0.40, R 10 0.23-0.48 | 0.144-0.377, 0.064-0.397, 0.226-0.480 (bracketing floors 32/50) | CONFIRMED | - |
| 14 | "At R <= 10 every contrast's MDE80 (0.24-0.72) exceeds the draft distances" | R 10 roster-mean central 0.243-0.717, band low all above distance: true for the mean; per random R 10 roster, G(N\|L2+V0) central 0.246 and 0.217 < 0.25 in 2 of 5 draws; R 5 range is 0.30-1.06 | PARTLY (M-2) | MEDIUM |
| 15 | tests: suite 943/1/0, selftest 46/46, mutants 70/70 | suite 943 passed / 1 skipped / 0 failed (10 deselected); selftest 46/46; builder campaign re-run in my sandbox 70/70 killed, control passes; own R0-R8 below | CONFIRMED | - |
| 16 | pins / hygiene | run at runner blob:e9903362 (LF, 0 CR; HEAD be75cf3, dirty ""); tip blob:8eae9bcb differs by a 9-line docstring insertion only; 3 files touched (count), plan edits insertion-only (67+49 / 0 deletions); plan 12:25:53 < code 12:46:43 < run 12:46:52 < P2 13:03:44; backup 5/5 + 8/8 OK, byte-equal; benchzoom remotes 0 | CONFIRMED | - |

## Defects (each with a fix)

- **M-1 (MEDIUM, reading).** The central a = 0.5 is not seen anywhere in the measured range at R 69/35/18: every measured
  1,500 -> 2,949 exponent is below 0.5 (cell max +0.43, meter max +0.48), and at R 69 four of five cell trends are negative.
  "R 35 at 7,058 ≈ R 69 at 2,949" is therefore an assumption-driven statement (central only); under the band it is
  0.77-1.84x, under the measured trends 1.24-1.95x. The hand-back drops P2's "centrally". Fix: any copy reads "under the
  central assumption a = 0.5, which no briefed cell's measured trend reaches; band 0.77-1.84x; trend 1.24-1.95x".
- **M-2 (MEDIUM, author question framing).** The R <= 10 and R >= 35 figures are random subsets of the 69 EEE models (41 at
  >= 0.975). The 9 local Ollama twins are a different, quantized, mostly sub-ceiling roster (SPEC section 6) and the record
  API providers cannot reproduce the 69 (SPEC section 5: 62 self-hosted by Writer), so neither option is measured. Which
  models matter: CV 0.23-0.48 at R 10, and 2 of 5 random R 10 rosters bring G(N|L2+V0) below its distance. Fix: relay the
  serving question with this caveat; "every contrast exceeds" holds for the roster-mean SE (4 of 5 contrasts robust
  across the 5 draws), not for an arbitrary 10-model roster.
- **L-1 (LOW, hand-back only).** "The planted-power factor x1.38-1.65 applies on top": k was measured on the meter SE; P2 and
  the plan say whether the cell SE absorbs it is not measured (coverage sqrt(DEFF0)/k at R 69 P 1.24/1.03). Fix: "applies
  to the meter SE".
- **L-2 (LOW).** P2 "ratio 0.86-1.07": recomputed 0.854-1.068 (G(V0|L2+N) 0.10663 / 0.12483); hand-written, not in
  summary.txt. Fix: bracket to 0.85-1.07.
- **L-3 (LOW).** GRID rows (15) print n 7,058 values with only "projected" in the header; the hand-back table has no
  EXTRAPOLATION / "scenario band, not a confidence interval" label. Fix: the registrar copies the table with that label.
- **L-4 (LOW).** P2 names the trend-above-band rows for P and G(V0|L2+N) at R 69; D_N at R 69 is also above (marginally).
- **L-5 (LOW).** n_eq 5,309-7,576 (R 35) rests on a 0.5 and no DEFF growth, both contradicted in range; quote only with
  both assumptions, never as a required n.
- **L-6 (LOW).** n1 = 7,058 items is used as independent; SPEC 3b has 6,968 twin clusters (Kish 1.030, SE <= x1.015) and
  "usable" after answering may be fewer. Negligible against the band; state it in the Support section.
- **L-7 (LOW, not decisive).** Own mutant R4 survived (beta_points' defined filter not pinned by the selftest); equivalent on
  the run of record (0 undefined active-level points with DEFF > 0 out of 10 undefined).

## Conditions for the registrar (BZ-AXIS-CONFIRM-FRESH)

- C-1: the registration names WHICH cell-aware SE decides (the draft's rule-B resampling SE_cell [E1] or the clustered
  form); this table is the clustered form, a lower bound; under S-RES G(V0|L2+N) at R 69, n 7,058 is 0.325-0.367 vs 0.062.
- C-2: P's bar under the cell-aware SE is fixed in the registration (still 3 SE as drafted here).
- C-3: no n*; DEFF in the Support section is measured on the fresh data (SPEC 3b: no transported DEFF).

## Own mutants (sandbox copies under E:/TaxoArena_tmp/rv_fresh-size/mut; killed = exit != 0 or a SELFTEST FAIL)

R0 control: passes. R1 G_CELL at n1: killed (S2 projection). R2 cell band high with e_cc: killed (S1 project cell).
R3 DEFF0 not squared: killed (S1). R4 beta points without the defined filter: SURVIVED (equivalent on record data; L-7).
R5 n statement over the meter SE: killed (S2 statements). R6 roster statement over the meter SE: killed (S2 statements).
R7 distance word on the SE scale: killed (S2 distance words). R8 m1 = m0 (no DEFF growth): killed (S1). Decisive: R1-R3,
R5-R8 (all killed).

## Commands (reproduce)

```
# inputs and outputs
(cd E:/benchzoom_demo/followups/design-surface && sha256sum -c SHA256SUMS | grep -c OK; sha256sum SHA256SUMS)   # 65; 5aa498d2...
(cd E:/benchzoom_demo/followups/fresh-size && sha256sum -c SHA256SUMS)                                          # 5/5 OK
# independent recompute from parts/R*_d*.json (own code; cell means over defined draws, log-log interpolation at m*,
# projection, band, trend, levers, n_eq, T1/T2/power.csv cross-checks)
python <scratch>/rv/recompute.py ; python <scratch>/rv/compare.py   # 225 values, max rel diff 2.1e-16; T1 800, T2 300, power 180: diff 0
python <scratch>/rv/spread.py      # roster CV; power_central diff 3e-16; EXTRAPOLATION 50/50
python <scratch>/rv/r10draws.py    # per-roster R 10 / R 18 projected MDE80 vs distance
python <scratch>/rv/r4.py          # R4 equivalence: 10 undefined active-level points, 0 with DEFF > 0
# code and tests (worktree Z:/FAC/TUBerlin/benchzoom_wt_fresh-size, PYTHONPATH=src, TMP/TEMP/TMPDIR -> E:/TaxoArena_tmp/rv_fresh-size/sb)
python examples/fresh-size.py --selftest            # SELFTEST SUMMARY: 46 of 46 PASS
python -m pytest -q tests/test_fresh_size.py        # 2 passed
python -m pytest -q -p no:cacheprovider tests       # 943 passed, 1 skipped, 10 deselected (895 s)
python <scratch>/rv/bmut.py rv                      # builder campaign in my sandbox: control passes, killed 70 of 70
python <scratch>/rv/rvmut.py                        # own mutants R0-R8
git diff --name-only b86c014..4676efb | wc -l       # 3
git diff --numstat aa05068..4676efb -- docs/fresh-size.md   # 67 0 / 49 0 (insertion only)
git rev-parse be75cf3:examples/fresh-size.py        # e9903362 (= meta.json script_blob_lf); tip 8eae9bcb (docstring +9)
git -C Z:/FAC/TUBerlin/benchzoom remote -v | wc -l  # 0
```
(`<scratch>` = C:/Users/octav/AppData/Local/Temp/claude/Z--FAC-TUBerlin-THESIS-TaxoArena/7c10e5cb-d16b-4a0e-864a-f3a6151d835b/scratchpad; not of record.)
