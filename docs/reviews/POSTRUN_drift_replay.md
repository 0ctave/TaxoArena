# POSTRUN: DRIFT-REPLAY, the readout of drift_replay.py --run

Reviewed: outcome `experiment_results/archv2/drift_replay/outcome.txt` (sha256 cf732363e94696bc..., 157 lines; never committed),
run by blob:a59389e2 drift_replay.py (LF; = HEAD e304ffe9 blob, `git hash-object` on the working tree and on `HEAD:` both a59389e2;
the READY delta's blob, 8b303773). Registration prog L24639-L24651 with brackets 7b31d00c / 598f5230 (record L24714-L24741).
Logs `E:/TaxoArena_tmp/dr_dry.log` (rc 0, no EVAL read), `dr_run.log` (= outcome line for line except the console em-dash and
the two trailer lines). Data object: union EVAL 5,907 items / 5,404 components, pool pv2_1575de61bb20e977 (content-closed,
CK-CLOSE-v2, residual disclosed); GATE 2,033 (levels, tau); TRAIN 12,334 bundle rows (reference occupancy). Structure-only:
no key, no verdict, so check 3 (wrong(established)) does not apply. 0 calls. THE SHIFT IS SYNTHETIC (streams resampled from one
EVAL set by the registered mixing rule; no real traffic, no temporal order, no new domain).

## Verdict: VALID (registered criteria reproduce to the digit), with WORD CONDITIONS W-1..W-5 binding the registrar's text

DR0 CALIBRATED, DR2 OCC-BETTER, DR1 NEITHER, F-DR NOT FIRED: all reproduced by my re-execution of the merged blob's own
functions on the same objects (every deciding digit equal). DR2's word SURVIVES an honest item/component-level interval, but the
printed stream interval (+/-0.018) is a Monte-Carlo interval conditional on these 5,907 items and on GATE and is about 5x too
narrow for any statement about the items; it must never be quoted alone (W-1).

## Per-claim table (deciding claims, plus the descriptive numbers the words rest on)

| # | claim (outcome) | mine | status | sev |
|---|---|---|---|---|
| 1 | DR0 FAR AF-U OCC-CHI 0.0325 (39/1200), OOS-RATE 0.0058 (7/1200) -> CALIBRATED | 0.0325 / 0.0058 (re-execution) | CONFIRMED | n/a |
| 2 | DR2 D_det +0.3942 = 0.6075 - 0.2133, stream bootstrap [+0.3767, +0.4125] | +0.3942 (own mean of the det arrays), [+0.3767, +0.4125], SE 0.0092 (own stratified analytic 0.0095) | CONFIRMED | n/a |
| 3 | DR1 D_arm -0.0080, [-0.0403, +0.0320] -> NEITHER | -0.0080, [-0.0403, +0.0320] | CONFIRMED | n/a |
| 4 | per-member DR2 BBH +0.09, GPQA +0.57, IFEVAL 0, MATH +0.675, MMLU_PRO +0.03, MUSR +1.0 | identical | CONFIRMED | n/a |
| 5 | DEFF_reuse 33.321, n_eff 36 (registered 1.5 / 800) | (0.0531/0.0092)^2 = 33.3; 1200/33.3 = 36 | CONFIRMED | n/a |
| 6 | the stream interval as the width of D_det | item-level two-stage (EVAL items resampled within member, fresh stream children, KM seeds resampled; B 200): SD 0.0470; component-level two-stage: SD 0.0486, pct [+0.3156, +0.4867], basic [+0.302, +0.473], normal on the point with the MC term sqrt(0.0486^2+0.0092^2) [+0.297, +0.491]; with GATE components also resampled (levels refitted, tau fixed): SD 0.0651, pct [+0.195, +0.436] | PARTLY: OCC-BETTER survives in every variant (lower bound >= +0.195); width understated 5.3x (EVAL) to 7.1x (with GATE) | HIGH (words) |
| 7 | component bootstrap (run) [+0.3050, +0.4925], SD 0.0531 | own fixed-children replica (same protocol, my rng) SD 0.0492, [+0.3125, +0.4909] | CONFIRMED | n/a |
| 8 | SUPPORT AS REALISED (e) MDE80 DR2 0.0258 | from the stream SE; honest MDE80 2.80 x 0.0486 = 0.136 (EVAL comp), 0.182 (with GATE); DEFF 27.9 / 50.1, n_eff 43 / 24; DR2 still SCOREABLE (0.45 > 0.182) | REFUTED (label) | MEDIUM |
| 9 | Support (b) DEFF 1.5 "declared pilot assumption" | realised 33 (run) / 28-50 (mine): the Support's own (g) ("the 5,907 items, not R, bound what is shown") implied an item term that does not shrink with R; the READY gate did not re-derive it | REFUTED (pre-data) | MEDIUM (process) |
| 10 | Support (a) "Kish mean cluster size 1.09" | 1.09 is the plain mean 5,907/5,404; Kish 1.311 (the outcome prints 1.311); same as ESCALATION-CURVE D-1 | REFUTED (label) | LOW |
| 11 | D_arm width | comp two-stage SD 0.0239, pct [-0.0640, +0.0273]; with GATE SD 0.0426, [-0.105, +0.067] | CONFIRMED NEITHER; no equivalence | n/a |
| 12 | P1 OCC-CHI 0.0325 HELD; P1 OOS-RATE 0.0058 FAILED | 0.0325 in [0.03, 0.10] (edge); 0.0058 < 0.03 | CONFIRMED | n/a |
| 13 | P2 x3 HELD, P3 HELD, P5 HELD (+0.2950, band edge 0.30) | 0.6075, 0.2133, +0.3942, -0.0080, +0.2950 in their bands | CONFIRMED | n/a |
| 14 | P4 delay s 0.40 120 HELD; P4 DET s 0.05 0.0275 FAILED | 120 in [30, 150]; 0.0275 < 0.05 | CONFIRMED | n/a |
| 15 | Briers DR0 0.0800, DR2 0.0378, DR1 0.1400 | 0.2^2+0.2^2; 0.15^2+0.12^2+0.03^2; 0.3^2+0.2^2+0.1^2 | CONFIRMED | n/a |
| 16 | "detection driven by members whose cells are source-pure" (brief's proposed word) | AF-U's 33 bins are ALL pooled rare bins; share of the member's EVAL items in bins >= 90% that member (my threshold): MUSR, MATH, GPQA, IFEVAL, BBH 0.000, MMLU_PRO 0.190. Per-member DET is monotone in the shift's non-centrality in AF-U's pooled bins, lambda = w s^2 sum_b (q_mb - Q_b)^2 / Q_b (EVAL-internal, approximate): MUSR 81.6 (DET 1.00), IFEVAL 49.5 (1.00), GPQA 35.7 (0.845), MATH 24.2 (0.675), BBH 5.1 (0.09), MMLU_PRO 1.2 (0.035); retained 3-41% of the source-oracle lambda | REFUTED (word) | HIGH (words) |

## Defects and word conditions (bind the registrar's outcome text; the outcome file stays as written)

- **W-1 (HIGH) DR2 width.** Quote: "DR2 OCC-BETTER on synthetic source-mix shifts: D_det +0.39 (DET 0.61 vs 0.21, s 0.20, AF-U);
  item-level 95% about [+0.30, +0.49] (EVAL components resampled with fresh streams, B 200), [+0.20, +0.44] with the GATE
  calibration also resampled; the registered stream interval [+0.377, +0.413] is Monte-Carlo only, conditional on these
  5,907 items and on GATE." Realised DEFF 28-50, n_eff 24-43, MDE80 0.14-0.18 (not 0.0258). No word changes; the width does.
  Most of the item variance is GPQA's ~34 EVAL items (member SD 0.28 of D_det; /6 = 0.047, the whole pooled SD).
- **W-2 (HIGH) per-member reading.** Not "source-pure cells". Word: "the advantage is carried by the SMALL members (MUSR,
  MATH, GPQA; IFEVAL ties at 1.00 vs 1.00), whose s 0.20 shift multiplies their share (x6.0, x3.8, x35; IFEVAL x8.1); per-member
  DET is ordered by the shift's non-centrality in the pooled bins, and on the two large members OCC-CHI detects 0.09 (BBH, x1.5)
  and 0.035 (MMLU_PRO, x1.1) against the source oracle's 0.99 and 0.425. The pooled bins are not source-pure; the unevenness
  is chiefly the relative size of a synthetic shift, a property of the mixing rule, not of the cells."
- **W-3 (HIGH) OOS-RATE is one-sided.** The OOS detector alarms only on MORE OOS flags; shifts toward members whose EVAL OOS
  rate is at or below the pooled 0.0444 (BBH 0.000, MUSR 0.000, MATH 0.031; MMLU_PRO 0.047 marginal) are invisible to it by
  construction (OOS DET <= 0.005 for each of the four at every s). Registered (g)'s caveat ("OCC-BETTER is the expected reading,
  not evidence for cells") applies to those four directions. The two directions OOS can see: IFEVAL 1.00 vs 1.00 (tie),
  GPQA 0.845 vs 0.275. State this beside OCC-BETTER.
- **W-4 (MEDIUM) P1 OOS FAILED = conservative, unequal operating points.** OOS-RATE ran at FAR 0.0058 vs OCC-CHI 0.0325:
  h = 20 flags is a discrete level (GATE alarming 0.024, not 0.05) and EVAL's OOS rate 0.0444 sits below GATE's p5 rate.
  This cannot overturn DR2: even full OOS detection of GPQA at a matched FAR gives D_det >= 0.394 - (1 - 0.275)/6 = +0.273.
  P1 OCC-CHI HELD at the band edge and "informed by the pre-data emulation (median 0.025)"; Brier printed, not credited.
- **W-5 (MEDIUM) DR1 and P4.** DR1: "AF-U cells detect the shift no better than matched-k k-means (OCC-CHI DET 0.61 vs 0.62,
  seed range 0.55-0.65; D_arm -0.008, 95% [-0.064, +0.027] at item level), despite AF-U's source-conditioned [SC] advantage on
  a source shift; no equivalence is claimed (none registered; registered DESCRIPTIVE-ONLY at the prediction)". P3 HELD is a point
  statement (the item-level interval exceeds its band). P4: delay HELD; at s 0.05 OCC-CHI DET 0.0275 is no higher than its own
  unshifted FAR 0.0325, i.e. no detection at s 0.05 (source oracle 0.595).
- **D-1 (MEDIUM) Support as realised.** The realised line prints MDE80 from the stream SE next to DEFF 33; future readers
  should print the MDE from the component SE (fix in any successor: `2.80 * cb["d2"]["se"]`). Process: the READY gate accepted
  DEFF 1.5 for a design whose item term does not shrink with R (Support (g) said so); re-derive item-reuse DEFF pre-data.
- **D-2 (LOW)** Kish 1.09 in Support (a) is the plain mean; Kish 1.311 (bracket like ESCALATION-CURVE D-1).

## Commands (read-only; 0 calls; no DB written: listings of data_v2/REG_ARCHV2-SPLIT-2_* and root *.db identical before/after
(`diff` LISTINGS_EQUAL); eval_view sha EQUAL before/after printed twice by the module's own check)

```
git hash-object tools/analysis/drift_replay.py ; git show HEAD:tools/analysis/drift_replay.py | git hash-object --stdin   # a59389e2 both
sha256sum experiment_results/archv2/drift_replay/outcome.txt                                                             # cf732363...
diff <(tr -d '\r' < outcome.txt) <(tr -d '\r' < E:/TaxoArena_tmp/dr_run.log)                                             # em-dash + 2 trailer lines only
python tools/analysis/scratch_dir.py --run -- python dr_postrun.py 200   # D.prepare/eval_structure/arms_from/simulate re-executed;
   # REPRO lines rows 1-4; ITEM_2stage, COMP_2stage, COMP_fixedchildren, COMP_2stage_GATEtoo (rng 424242, B 200 each) rows 6, 7, 11
python tools/analysis/scratch_dir.py --run -- python dr_purity.py         # row 16: bin purity, lambda vs source oracle (AF-U, KU0, KU3)
```
Scripts, log and JSON: `E:/TaxoArena_backup_2026-10-05_drift_replay/postrun/` (dr_postrun.py, dr_purity.py, dr_postrun.log,
dr_postrun_res.json). Backup `E:/TaxoArena_backup_2026-10-05_drift_replay`: outcome.txt, drift_replay.READ_STARTED,
dr_dry.log, dr_run.log + postrun/, SHA256SUMS.txt 8 entries, `sha256sum -c` 8/8 OK.

Own mutants: none (post-run numbers review on an unchanged, reviewed blob; selftest/mutants confirmed in 8b303773).
