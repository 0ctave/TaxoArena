# CERT-UNDER-FILTER: post-run numbers review (adversarial reviewer, 2026-09-23)

Zero judge calls. Read-only. The instrument was not imported: the BT fit (MM, prior 0.5 per observed pair, tol 1e-12, 2000 iter), the McNemar test, the filter, the R draws, the bootstraps and the C3 likelihood are the reviewer's own code, in the session scratchpad `cert_post/` (`recompute.py`, `analyse.py`, `mc.py`, `c3.py`, plus the seed and exclusion variants; outputs `analyse_K20.out`, `armseed.out`, `armseed_excl.out`, `ctrl.out`).

- **Object.** `experiment_results/x12_crossdomain/stack_v2_promptv2_x12all.db`: 9,142 valid verdicts on 2,811 qids; the -wal is absent and there is no -journal. `mmlu_pro_dataset_cache_v2.db` (-wal 0 B) and `snapshots.db` (-wal 0 B) were read with no -journal present. Every open used `mode=ro&immutable=1` after a check that the -wal and -journal were empty.
- **Routing.** Routing is `bareq512_s42_reserved_leaf_assignments.csv` on snapshot 20260909_212117. The routed set equals pool p2dca21ab5f4ef3ae (3,445 questions). The cache's own `anchor` column agrees with the routed anchor on 9,142 of 9,142 rows.
- **DB state.** The x12 cache sha256 (eb0bec27...), the sizes and the mtimes of all three DBs and their sidecars are byte-identical before and after this review (`cert_post/db_before.txt` and `db_after.txt`, empty `diff`).
- **Rule 7.** No construction, site null or Gradle worker was running. The only JVMs were an idle GradleDaemon (PID 49416) and a KotlinCompileDaemon (PID 5940), found with `Get-CimInstance Win32_Process`.
- **Identity.** Outcome at b4b1688: `git hash-object` gives 91ad6fa8df9565a123b195e6997bb81b746142e2, and sha256 of the file and of `git show b4b1688:<path>` is 0a50f05ae38fc3c5... (the file is LF). Instrument: blob f7d59019c3d65128687df46aebdcb798b43c3062. It carries sha256-lf16:0db2026f17b559a1 and sha256-crlf16:b144a7d4377acfd3, and the working tree holds the CRLF rendering (see D-7).

## Per-claim table

| # | claim (as printed) | reviewer's number | verdict | command / script |
|---|---|---|---|---|
| 1a | G2: filter A 6,066/9,142; B 5,276/8,352; AGREE 3,076, DISAGREE 5,276, UND 790 | identical | CONFIRMED | recompute.py |
| 1b | G1: U 920 edges / 809 established / 26 wrong(established); 60 wrong on all labels | 920 / 809 / 26; 60 | CONFIRMED | recompute.py |
| 1c | W_U 26(26); on the 13 remaining anchors: 752 established edges, W_U 26 | 26; 752; 26 | CONFIRMED | analyse.py (1) |
| 1d | W_F 17(17) | 17 | CONFIRMED | analyse.py |
| 1e | W_R draws: 23 28 20 21 24 26 27 22 25 20 24 28 21 28 24 21 24 25 25 27; mean 24.15 | identical, draw by draw | CONFIRMED | analyse.py |
| 1f | ΔW = 17 − 24.15 = −7.15 | −7.15 | CONFIRMED | analyse.py |
| 1g | per-anchor d_a +0.65 −0.65 −0.20 −0.15 +0.45 −1.55 −1.30 −0.55 −1.35 +0.10 +0.50 −0.10 −3.00 | identical (Bio, Chem, CS, Econ, Eng, Health, Hist, Law, Math, Other, Phil, Phys, Psych) | CONFIRMED | analyse.py |
| 2a | C1 interval: 13-anchor cluster bootstrap, B 2000, seed 42, SE 3.606, [−14.22, −0.08]; percentile [−14.80, −0.65] | SE 3.606; [−14.22, −0.08]; [−14.80, −0.65] | CONFIRMED (to the digit) | analyse.py |
| 2b | robustness to the cluster-bootstrap seed and B (descriptive) | B 2000, seeds 1-20: SE 3.470-3.632, upper end −0.35 to −0.03, **crosses 0 on 0 of 20** (percentile upper end 0 of 20). B 20,000, seeds 1-20: upper end −0.25 to −0.12, 0 of 20. Seed 42 at B 200,000: SE 3.557, upper end −0.177. The seed-42 / B-2000 SE (3.606) sits ABOVE the bootstrap limit (√13 × sd_pop = 3.559), so the recorded figure is the conservative one | CONFIRMED robust to this seed | analyse.py (2) |
| 2c | robustness to the ARM question-bootstrap stream (Random(42), 300 boards per anchor, fixed by R4 through build()) (descriptive) | 20 alternate arm seeds: W_F 16-19, ΔW −8.05 to −4.75, 21-seed mean −6.56 (sd 1.06). **Interval upper end ≥ 0 on 15 of 20 alternate seeds**; HELD on 6 of 21 (seed 42 included) | NEW FINDING (D-1) | recompute_seed.py; armseed.out |
| 2d | small-cluster conventions (descriptive) | unbiased cluster SE √13 × sd(ddof 1) = 3.704, giving [−14.41, **+0.11**]; with t₁₂ 2.179, [−15.22, **+0.92**], two-sided p 0.078. Wilcoxon on the 13 d_a: p 0.094; sign test 9 negative / 4 positive, p 0.27 | NEW FINDING (D-3) | analyse.py (2) |
| 3a | "mean over the 20 draws" is registered | YES: K = 20, Random(1000 + k), k = 1..20 (registration L13249-L13251) | CONFIRMED | programme |
| 3b | Monte-Carlo error of mean W_R | sd of W_R across draws 2.681, so MC SE 0.599. Per-anchor MC variance Σ var(W_R,a)/20 = 0.282, which is 2.2% of the bootstrap variance 13.0 | quantified | analyse.py (3) |
| 3c | does the interval include the R-draw variance? | IMPLICITLY yes: each d_a carries its own anchor's MC error, so resampling anchors captures it; the bootstrap does not treat mean W_R as fixed per anchor. An explicit two-stage bootstrap (anchors × draws, 20,000 reps) gives SE 3.646 and upper end **−0.004** at seed 42 (+0.014 / −0.039 / −0.008 at seeds 1 / 2 / 3). Adding the MC variance in quadrature, which double counts it, gives 3.645 and −0.006. With 200 draws: mean W_R 24.77, ΔW −7.77, [−15.00, −0.54]. Over 10 disjoint 20-draw blocks ΔW runs −8.60 to −7.15; **the registered block is the least favourable of the 10**; 1 of 10 blocks crosses 0 (+0.024) | PARTLY: the SE understates by 1.1% (3.606 vs 3.646) and the verdict survives at seed 42 by 0.004 edges | mc.py (K = 200) |
| 4a | Business removed (convention A, 195 kept rows < the 200 floor), as registered | R2(a) and R4(c): an anchor below build()'s floor under ANY arm leaves C1-C3. Business is 295 rows on U, 195 under F_A and 171 under F_B | CONFIRMED as registered | analyse.py |
| 4b | C1 with Business kept (descriptive) | A: ΔW −7.30 (17 − 24.30), SE 3.517, [−14.19, −0.41]. B: −4.20, [−12.50, +4.10] | reported | analyse.py (4) |
| 4c | convention B: ΔW −3.80 (24 − 27.80), SE 4.154, [−11.94, +4.34], UNDETERMINED, decides nothing | identical; paired counts 8 / 8; DEFF 1.389 | CONFIRMED | analyse.py |
| 5a | C3 U: 752 edges, 26 events, b0 −2.6417, b1 +2.2274, ddev 5.41, cluster P 0.0267 (600 reps, seed 11) → UNDETERMINED (the two tests disagree) | b0 −2.6417, b1 +2.2274, ddev 5.406, P 0.0267 | CONFIRMED | c3.py (own likelihood, Nelder-Mead from 5 starts) |
| 5b | C3 F: 17 events, b0 −2.0041, b1 −0.2511, ddev 0.01, P 0.7167 → UNDETERMINED; P5 HELD | b1 −0.2511, ddev 0.010, P 0.7167 | CONFIRMED. Note: all 20 R_A draws have b1 between +0.90 and +5.64; F's −0.25 lies outside that range (D-6) | c3.py |
| 5c | C3 F_B: b1 +1.1791, ddev 0.12, P 0.4283 | identical | CONFIRMED | c3.py |
| 5d | C2: U widener + decline 610 / 1 / nominal 1.08; F_A 586 / 1 / 1.11 (primary pair); P4 HELD | 610 / 1 / 1.08; 586 / 1 / 1.11 | CONFIRMED | c3.py |
| 5e | Support: SE_iid 2.889, DEFF 1.558, n_eff 482.8, MDE 10.10, boundary edges 44 | 2.889 / 1.558 / 482.8 / 10.10 / 44 | CONFIRMED (arithmetic) | analyse.py |
| 5f | (L-d) DEFF re-measured FROM THE CLUSTER SIZES | 13 clusters; established edges per anchor 59/58/59/57/53/54/53/58/63/58/59/61/60; Kish m 57.99; ANOVA ICC of d_e 0.0112. **DEFF = 1 + (m − 1) ICC = 1.636, n_eff 459.5.** SE = 2.889 × √1.636 = 3.695 gives an upper end of **+0.09**. Both DEFFs are below the registered break-even of 1.82 | reported (D-3) | analyse.py |
| 5g | paired edge counts: wrong in F and not in the R majority 3; right in F and wrong in the R majority 8 | 3 / 8; exact binomial p 0.227. U→F transitions on the 752: wrong→right 11, right→wrong 2, wrong→wrong 15 | CONFIRMED | analyse.py |
| 5h | P1 17 in [6, 22]; P2 24.15 in [24, 38]; P3 −7.15 in [−26, −6]; P4; P6 17 zero-kept edges, 0 disconnect | all HELD as printed. P2 holds by 0.15 and P3 by 1.15. Across the 20 alternate arm seeds P2 fails on 6 (mean W_R < 24) and P3 fails on 6 (ΔW > −6) | CONFIRMED (fragile) | armseed.out |
| 5i | witness 43 / 43 / 43; single immutable open of the stack cache | a count check on the outcome text: `grep -c "EXECUTION WITNESS: c3_fit calls 43; fits 43"` = 1; `grep -c "stack cache opened exactly once"` = 1; the connection log lists 4 connects, of which the eval DB's first (pool_guard) is plain `mode=ro` (the known L4) | CONFIRMED on the text (not re-executed) | grep |
| 6 | reading: "no adverse selection bias; the filter moves edges toward the key" | leave-one-anchor-out on the 12-anchor bootstrap (B 2000, seed 42): **8 of 13 intervals contain 0**. Dropping Psychology gives −4.15 [−9.00, +0.70]; Health −5.60 [−12.33, +1.13]; Math −5.80 [−12.63, +1.03]; History −5.85 [−12.69, +0.99]. Psychology's d_a of −3.00 (W_F 1 vs mean W_R 4.00, W_U 4) is 42% of ΔW. Edge-level 3 vs 8, p 0.23; 2 edges go right→wrong under F | REFUTED as worded (D-2) | analyse.py (6) |
| 7 | D8: bareq512_s42 anchor map (id-disjoint only) | lists from the SPLIT-FOLLOWUPS review pickles (`split_followups_review/a3/a4/a5.pkl`). The 28 induction-exposed: 27 in x12's 2,811 judged, 80 verdict rows (Law 13, Health 8, Biology 3, Philosophy 2, Other 1). The 70 norm-v1 twins: 65 judged, 193 rows. The 37 exact: 33 judged, 97 rows. The 26 labelling ids: 26 judged, 79 rows. The 14 ladder twins (the STACK-v2 rubric corpora that judged these verdicts): 14 judged, 40 rows. Union: 74 qids, 69 judged, 201 of 9,142 rows. Descriptive, excluding those 201 rows: ΔW at arm seed 42 is −3.45 [−12.70, +5.80]; the 21-seed mean is −4.90 (HELD 0 of 21) against −6.56 on the full data. Anchor-matched random exclusions of 69 judged qids (10 sets × 5 arm seeds) shift ΔW by −1.56 ± 1.66, range −4.37 to +0.06; the exposed exclusion's +0.96 ranks above all 10 controls (about 1 in 11) | UNDETERMINED: exposure is not shown to drive C1; the data path does touch it | recompute_excl*.py, recompute_ctrl.py, ctrl.out |

## Defects

**D-1 (HIGH): C1's HELD is a property of one Monte-Carlo stream.** The direction of each arm edge is the majority sign over 300 question-bootstrap boards drawn from `random.Random(42)`. Ruling R4 fixes that seed through build(), so the verdict of record stands. But 21 established edges have F-arm p in [0.35, 0.65] and 8 have p in [0.45, 0.55], and under the 20 alternate arm streams W_F moves between 16 and 19. The interval's upper end is ≥ 0 on 15 of 20 alternate streams; across the 21 streams ΔW has mean −6.56 and sd 1.06. The cluster-bootstrap seed is not the fragility: 0 of 40 alternate bootstrap seeds cross 0. The arm stream is.

FIX: the sentence of record says "HELD at the registered seeds; marginal", with the 15/20 figure. Future registrations that count majority signs should either average p over several bootstrap streams or carry the stream's variance into the interval.

**D-2 (HIGH): the outcome's reading claims more than C1 licenses.** "No adverse selection bias" is the registration's HELD gloss, but what C1 shows is narrower: a net count difference whose 95% interval ends 0.08 edges below 0.

- One anchor (Psychology, −3.00) carries 42% of the effect.
- 8 of 13 leave-one-anchor-out intervals contain 0.
- At the edge level the count is 3 vs 8 (p 0.23), and the filter turns 2 established edges from right to wrong relative to U.
- F's b1 collapses to −0.25 while every R draw keeps b1 ≥ +0.90 (D-6).

FIX: the reading becomes "net, the filter's selection points fewer established edges against the key than random selection at equal support (ΔW −7.15 of 752; HELD by the registered interval, marginal)". Drop "no adverse selection bias" and drop any per-edge or per-anchor reading.

**D-3 (MEDIUM): the deciding interval sits on conventions that the record should name.**

- The bootstrap SE of a sum over 13 resampled clusters is biased low by √(12/13). With the unbiased cluster SE the upper end is +0.11; with t₁₂ it is +0.92 (p 0.078).
- DEFF measured from the cluster sizes (ICC, L-d) is 1.636, against the ratio form's 1.558, and at that DEFF the upper end is +0.09.
- The outcome's "measured DEFF 1.558 is within the registered break-even 1.82" is computed against the PREDICTED |ΔW| of 16. The observed |ΔW| of 7.15 is below the MDE (10.10), so at the observed effect the design had about 50% power and could only return a margin of this size.

None of this changes the registered verdict (z × bootstrap SE at seed 42 is the registered rule).

FIX: print these three lines beside C1 in the record.

**D-4 (LOW): R-draw Monte-Carlo error.** The draw count is registered (K = 20). The MC SE of mean W_R is 0.60. The cluster bootstrap includes the R-draw variance implicitly, and the explicit two-stage SE is 3.646 against 3.606 (+1.1%), which leaves the upper end at −0.004 at seed 42. The registered block of 20 draws is the least favourable of 10 disjoint blocks; with 200 draws ΔW is −7.77 [−15.00, −0.54].

FIX: state it beside C1. The conclusion does not move.

**D-5 (LOW): predictions P2 and P3 hold at their edges** (by 0.15 and 1.15). Each fails on 6 of 20 alternate arm streams.

FIX: score them "HELD (at the edge)".

**D-6 (MEDIUM, descriptive; not a C3 defect):** under F the agreement slope of the wrong-direction likelihood is b1 −0.25 (ddev 0.01). All 20 same-support random draws keep b1 between +0.90 and +5.64. The filter's selection removes the A-dependence on which the deployed widener's (b0, b1) rests. C1 HELD discharges the L95 precondition on direction only, as registered. This is a further reason why making the filtered schedule the default under the current widener parameters is not supported by this run.

**D-7 (LOW, record): the registrar's L14493 is wrong about the working tree.** The ruling says "the main working tree is LF, `git hash-object` = the blob". The working-tree file holds 2,421 CR bytes, and its sha256-16 is b144a7d4377acfd3, which is the CRLF rendering; `core.autocrlf=true`, so `git hash-object` normalises and cannot show the rendering. The outcome's own line 3, "working tree CRLF (sha256-crlf16:b144a7d4377acfd3)", is correct.

FIX: a bracket at L14493.

**D-8 (LOW, latent, no consequence here): the routing parser.** `rubric_512.primary_routing` parses `bareq512_s42_reserved_leaf_assignments.csv`, whose weight is written with a decimal comma and unquoted (`0,000000`), so each row splits into 7 fields. DictReader then reads `weight` as the integer part only ("0" / "-0" / "-1"), and the "max weight" rule falls back to file order. On this file the file-first leaf equals the true maximum-weight leaf on all 410 multi-row qids, and the cache's anchor column agrees on 9,142 of 9,142 rows. The rule works because of how the file is sorted, not because it reads the weight.

FIX: queue a parser fix (read fields 4 and 5 as one decimal) with a count check.

## Checks that pass without checking (item 8)

- **The C1 gate.** Its only stochastic check is the cluster bootstrap. The arm-stream Monte Carlo, which moves the verdict (D-1), has no check.
- **The break-even line.** "Within the registered break-even 1.82" is evaluated against the prediction (16), not the observation (7.15), so it reassures about the wrong quantity (D-3).
- **Checks confirmed as count checks, not presence checks:** G1 / G2 / G3, the witness 43/43/43, and the per-anchor floor list.

## Verdict

**NUMBERS CONFIRMED.** Every printed figure reproduces to the digit from independent code: W_U, W_F, the 20 W_R draws, ΔW, SE 3.606, both intervals, the d_a, the paired counts, the Support block, C2, C3, and convention B.

**C1 HELD STANDS AS REGISTERED, BUT IT IS MARGINAL.** It is robust to the cluster-bootstrap seed and to B (0 of 20 seeds cross 0 at B 2,000 and at B 20,000). It is not robust to:

- the arm bootstrap stream (15 of 20 cross);
- small-cluster conventions (+0.11 / +0.92);
- the ICC DEFF (+0.09);
- leave-one-anchor-out (8 of 13 cross).

**READING REFUTED as worded (D-2).**

## Proposed sentence of record

"CERT-UNDER-FILTER (zero calls; x12 board of record, 752 established edges in 13 anchors, Business below the 200-row floor under the deployed filter and removed as registered; recomputed to the digit by the reviewer): under convention A the filter's selection points W_F = 17 established edges against the key, against a mean of 24.15 over 20 same-support random draws. ΔW is −7.15, and the registered 13-anchor cluster-bootstrap interval is [−14.22, −0.08] (SE 3.606; measured DEFF 1.56 to 1.64, n_eff 460 to 483, MDE 10.1), so C1 HELD. It is marginal: the interval's upper end stays below 0 for all 20 alternate cluster-bootstrap seeds at both B 2,000 and B 20,000, but crosses 0 for 15 of 20 alternate arm question-bootstrap streams (ΔW −4.75 to −8.05, mean −6.56), under a small-cluster t interval (+0.92), and in 8 of 13 leave-one-anchor-out fits. Psychology carries −3.00 of the −7.15, and at the edge level the split is 3 vs 8 (p 0.23). Convention B reads UNDETERMINED (−3.80 [−11.94, +4.34]). The L95 precondition is discharged on direction only, at the registered seeds; under F the widener's agreement slope is not identified (b1 −0.25, ddev 0.01, against b1 > +0.90 in all 20 random draws)."

## What this run does not show

1. That the filter has no adverse selection on any edge or anchor. Two established edges go right→wrong under F, 3 are wrong in F and not in the R majority, and 4 of 13 anchors have d_a > 0.
2. A direction effect robust to the Monte-Carlo stream that fixes the edge signs (15 of 20 alternate streams read UNDETERMINED).
3. That the deployed widener's (b0, b1) is valid under the filtered schedule. C3 is descriptive, and F's b1 is −0.25.
4. Safety at the operating point (C2 is descriptive: 1 wrong(established) against a nominal of 1.11).
5. Anything about x20, the merged board, grok's board or newcomers.
6. That split exposure (the 74 twin / induction / labelling / ladder qids, 201 rows) is neutral or drives the result. Excluding it moves ΔW by +0.96 against anchor-matched random controls at −1.56 ± 1.66; that is undetermined, and the ID-ONLY chip stays.
7. A per-anchor or per-edge claim of any kind.
