# POSTRUN: ESCALATION-CURVE, the readout of escalation_curve.py --run

Reviewed: outcome `experiment_results/archv2/escalation_curve/outcome.txt` (sha256 0573ff5d3f9da048..., 124 lines; never
committed), run by blob:0acfb0cc (LF; the READY's blob, merged 4636f50d), escalation_rc blob:8f99db7d (C-EC2). Registration
prog L24653-L24665 with its C-EC1/C-EC2 brackets (7b31d00c); disclosure L24618-L24623. READY: `READY_drift_escalation.md` (ec880315).
Data object: union EVAL 5,907 key-complete items / 5,404 components of pool pv2_1575de61bb20e977 (content-closed, CK-CLOSE-v2,
residual disclosed); TRAIN 11,841 (policy fit); GATE 2,033 (ECDFs), 1,944 key-complete (c*). Key-scored end to end: no judge
verdict, so check 3 (wrong(established)) does not apply. Bill: 0 calls.

## Verdict: VALID

EC1 = ORDERING-INFORMATIVE, reproduced to the digit by a full re-execution (byte-identical outcome) and by my own curve/ECDF
code on the captured per-item inputs. F-EC NOT FIRED. P1-P4 HELD as printed. Conditions on the WORDS (W-1..W-3) and the
disclosure (W-4) below. These bind the registrar's outcome text; the outcome file stays as written.

## Per-claim table (deciding claims plus the descriptive numbers the words rest on)

| # | claim (outcome) | mine | status | sev |
|---|---|---|---|---|
| 1 | A_E(AF-U) +0.00659 | +0.00659 (own sort, own ECDF, own grid; nominal-c form also +0.00659) | CONFIRMED | n/a |
| 2 | two-stage 95% [+0.00310, +0.01007], SE2 0.00178 | from the 2,000 captured replicates: SE2 0.00178, iid 0.00162 -> [+0.00310, +0.01007]; pct [+0.00254, +0.00937] | CONFIRMED | n/a |
| 3 | independent cross-check of the interval | own one-stage component bootstrap, policy frozen (B 400, rng 20261005): SE 0.00155, pct [+0.00349, +0.00939] | CONFIRMED (lower bound > 0 either way) | n/a |
| 4 | EC1 ORDERING-INFORMATIVE; rule 8 not refuted | lower bound +0.00310 > 0 | CONFIRMED | n/a |
| 5 | realised DEFF 1.202, n_eff 4,915, MDE80 0.00497 | (0.00178/0.00162)^2 = 1.207 (unrounded 1.202); 5,907/1.202 = 4,915; 2.80 x 0.00178 = 0.00497 | CONFIRMED | n/a |
| 6 | Support: DEFF 1.302 (transported), SE <= 0.0036, MDE80 0.0100 | realised SE is half the planning bound; the bound held (conservative); EC1 resolved although registered DESCRIPTIVE-ONLY at the prediction | CONFIRMED (non-vacuous) | n/a |
| 7 | Support (a) "Kish mean cluster size 1.09" | 1.09 is the plain mean 5,907/5,404 = 1.093; Kish sum n^2/sum n = 1.311 (the outcome prints 1.311) | REFUTED (label) | LOW |
| 8 | KM-U A_E +0.00603 [+0.00343, +0.00862] | own +0.00603 (seeds +0.00366/+0.00635/+0.00637/+0.00692/+0.00683); SE2 0.00133 | CONFIRMED | n/a |
| 9 | AF-U - K_0 +0.00212 [-0.00159, +0.00582] | own +0.00212; SE2 0.00189 | CONFIRMED | n/a |
| 10 | AF-U - KM-U (NOT printed) | own +0.00056, one-stage pct [-0.00185, +0.00280] (SE 0.00120) | NEW, descriptive | n/a |
| 11 | max D_E +0.01249 at 0.38 | +0.01249 at 0.38 | CONFIRMED | n/a |
| 12 | c* 0.69, EVAL gain +0.00237 [-0.00435, +0.00909] | own gain at 0.69 +0.00237; SE2 0.00343 | CONFIRMED | n/a |
| 13 | gain over no escalation, best point (not printed) | +0.00491 at coverage 0.58, chosen on EVAL (post hoc, no interval) | NEW, descriptive | n/a |
| 14 | P1 band HELD; Brier 0.6050 | 0.00659 in [0.003, 0.013]; (1-0.45)^2 + 0.55^2 + 0 = 0.6050 | CONFIRMED | n/a |
| 15 | P2/P3/P3c/P4 HELD | 0.00212 in [-0.006, 0.006]; 0.01249 in [0.008, 0.020]; 0.38 in [0.35, 0.75]; 0.00237 in [-0.004, 0.012] | CONFIRMED | n/a |
| 16 | EC1 words "beats random escalation across the coverage range" | pointwise D_E intervals include 0 for c >= 0.80 (0.80, 0.85, 0.90, 0.95); the area is a grid mean | PARTLY (overreach) | MEDIUM |
| 17 | non-blind disclosure on every prediction line | only the P1 Brier line prints "informed"; P1 band, P2, P3, P3c and P4 lines print none (5 of 6 lines) | PARTLY | MEDIUM |
| 18 | identity, parity, hook, G3, view shas | all REPRODUCED/EQUAL in both the run and my re-execution; 0 REFUSED/VOID/Traceback in ec_dry.log, ec_run.log | CONFIRMED | n/a |

## Defects and conditions

- **W-1 (MEDIUM; words).** EC1's sentence must read "on average over the coverage grid", not "across the coverage range":
  the pointwise D_E interval excludes 0 only for c in 0.05..0.75 and includes it at c >= 0.80. Fix: the registrar's
  outcome text uses the corrected sentence below. The outcome file stays write-once.
- **W-2 (MEDIUM; words, size and use).** "Beats random escalation" must be quoted beside its size and beside the no-escalation
  baseline. A_E is +0.0066, about 0.7pp of accuracy averaged over the grid (95% [+0.31, +1.01]pp), with a peak of +1.25pp at c 0.38.
  Escalation itself does not beat keeping the cell policy. The gain over no escalation is NEGATIVE for c < 0.30, because the
  best single (0.6049) is worse than the AF-U policy (0.6201). The GATE-chosen operating point gains +0.24pp [-0.44, +0.91]pp,
  and even the EVAL-chosen best point is only +0.49pp (post hoc). So the run delivers no usable operating-point gain.
- **W-3 (MEDIUM; attribution).** It is a margin/OOS property, not a tree property. The registration's WILL NOT SHOW already
  excludes a tree-specific gain, and the run supports that. The label-free U-global k-means at matched k (KM-U) gives +0.0060.
  AF-U - KM-U = +0.0006 [-0.0019, +0.0028] (one-stage, frozen policy, my readout, descriptive), and AF-U - K_0 = +0.0021
  [-0.0016, +0.0058]. Each seen single-component ordering has a LARGER area than the registered combination
  (AF-U margin +0.0076, OOS +0.0085, fragility +0.0102). These curves were seen, so they are descriptive and carry no
  interval. The min(F_m, F_oos) combination therefore adds nothing over its own components. The words must not say the
  combined ordering is the best ordering.
- **W-4 (MEDIUM; disclosure).** C-EC1 scoped the "informed" qualifier to P1 and P3. But the registration's header
  "PREDICTIONS (informed by the seen component curves ...)" governs all four. P2 (AF-U - K_0) rests on the seen margin/OOS
  curves of BOTH arms, and P4 (gain over no escalation) on the seen tables' gain column. Fix: every prediction line in the
  outcome record, the results JSON and the ledger chip carries "informed by the seen component curves": P1 band, P1 EC1
  probabilities, P2, P3 point, P3 coverage, P4. All HELD readings are readings of an informed forecast, not blind confirmations.
- **D-1 (LOW).** Support (a) labels 1.09 as "Kish mean cluster size". Fix: a registrar bracket saying 1.09 is the plain mean and
  the Kish size is 1.311. The DEFF/n_eff arithmetic is unaffected, because it uses the measured DEFF.
- **D-2 (LOW; successor note).** The c* interval holds GATE fixed, so threshold variability is outside it (registered, as RC R7).
  The realised SE2 of 0.00343 is twice the area's, so any operating-point claim needs about 4x the items.

**Corrected words (licensed):** "On the union EVAL items (5,907 / 5,404 components), escalating the lowest-u items (combined
margin/OOS ordering) to the best single model beats random escalation on average over the coverage grid by +0.66pp of accuracy
(two-stage 95% [+0.31, +1.01]pp; EC1 ORDERING-INFORMATIVE, predictions informed by the seen component curves). The size is small,
and it equals a label-free k-means partition's (+0.60pp; difference +0.06pp [-0.19, +0.28]pp), so it is a property of the
margin/OOS ordering on any centroid partition, not of the tree. It yields no usable operating point: the GATE-chosen coverage
0.69 gains +0.24pp [-0.44, +0.91]pp over no escalation, and below coverage 0.30 escalation loses accuracy."

Own mutants: none. The post-run review touches no code, blob 0acfb0cc is unchanged since READY ec880315 (own 8/8 killed
there), and both deciding paths re-executed byte-identically.

## Registrar duties
1. Outcome section: EC1 ORDERING-INFORMATIVE, with the corrected words (W-1..W-3). KM-U and AF-U - KM-U go beside it.
2. The "informed" qualifier goes on all six prediction lines (W-4), extending C-EC1 by a bracket.
3. Bracket Support (a) Kish (D-1). Bracket the realised support: DEFF 1.202, n_eff 4,915, MDE80 0.0050 vs the registered 0.0100.
4. Records, INDEX, queue, ledger chip ("ORDERING-INFORMATIVE, small; = k-means; no operating-point gain"). Pin the outcome
   sha256 0573ff5d...; backup E:/TaxoArena_backup_2026-10-05_escalation_curve (SHA256SUMS.txt, 8 files, `sha256sum -c` OK).

## Commands
```
sha256sum experiment_results/archv2/escalation_curve/outcome.txt   # 0573ff5d...; git hash-object tools/analysis/escalation_curve.py -> 0acfb0cc
diff <(sed 's/\r$//' E:/TaxoArena_tmp/ec_run.log) outcome.txt     # only 2 encoding lines + 2 console-only lines differ
grep -c -i 'REFUSED\|VOID\|Traceback' E:/TaxoArena_tmp/ec_{dry,run}.log   # 0 / 0
python <scratch>/ec_recompute.py > E:/TaxoArena_tmp/ec_postrun_recompute.txt
  # re-executes run() with outcome/marker redirected to a review subdir (outcome sha256 = 0573ff5d..., byte-identical);
  # captures GATE ECDF inputs, margins/OOS, u, U.interval replicates; own ECDF/u (asserted equal), own curve, own SE/DEFF,
  # own one-stage component bootstrap (AF, AF-KMU, AF-K0); Kish from own cluster sizes; view shas c2930c60 / e35b7518 unchanged
# script + output + rerun files: E:/TaxoArena_backup_2026-10-05_escalation_curve (SHA256SUMS.txt; sha256sum -c: 8 OK)
```
