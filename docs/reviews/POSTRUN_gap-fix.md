# POSTRUN review: GAP-FIX (parts a and b), 2026-10-06

Reviewed: the run of record under tools/analysis/gap_fix.py blob:7c0691e8444848f3669e46d33adbfa2b7af31a20 (LF; `git rev-parse
HEAD:tools/analysis/gap_fix.py` = `git hash-object` of the working file; merged by path 02f85eaf; READY ccdc2ce1). Outputs (not
committed) in experiment_results/gap_fix/, sha256 equal to the operator's report and to E:/TaxoArena_backup_2026-10-06_gap_fix
(`sha256sum -c SHA256SUMS.txt`: 9 / 9 OK). Registration: prog "## Registered 2026-10-06 (before any code or call) — GAP-FIX: ..."
L24842-L24854 with its brackets; registrar's READY record L24890-L24896 (conditions R-C1..R-C4, post-run duties PR-1..PR-4). Zero calls.

## VERDICT: VALID, with the words corrected (W-1, W-2)

GF1 = PARTIAL is reproduced to the digit by an independent re-implementation. CLOSED is refuted. That part is SCOREABLE.
PARTIAL rather than OPEN is DESCRIPTIVE-ONLY on the registered verdict line (f): |D_R| falls short of the OPEN bar by 0.0009,
about 3 questions. I_R > 0 is real, but two thirds of it come from re-centring at T 0, which moves no fit item. The five Lloyd
passes alone add +0.0044 [+0.0000, +0.0087]. The run cannot claim "the refinement moved it" for the passes.

## Data object
af_clean_s42; held-out = the p2dca21ab5f4ef3ae judgeable side, 3,445 questions in 3,445 stem_key twin groups (Kish 1.0000; my count);
fit set 8,125; labelled TRAIN corpus from FG.corpus_for; V0..V4 read from the pinned state files (sha-checked by v_parts). The
denominator is the registered 3,445 (Support (a)); no judge verdict enters.

## Per-claim table (deciding claims; mine = E:/TaxoArena_tmp/postrun_gapfix/recompute_a.py, independent Lloyd/M1/bootstrap)
| # | claim | reported | mine | state | sev |
|---|---|---|---|---|---|
| 1 | identity T / V0 hits, spread_V | 2504 / 2652 / 0.0305 | 2504 / 2652 / 0.0305 (V0..V4 2652, 2647, 2559, 2664, 2610) | CONFIRMED | - |
| 2 | D_T | -0.0430 [-0.0557, -0.0293] | -0.0430 [-0.0557, -0.0293]; alt seed B 4000 [-0.0552, -0.0302] | CONFIRMED | - |
| 3 | D_R (WP, T 5) | -0.0296 [-0.0412, -0.0168], 2550 hits | -0.0296 [-0.0412, -0.0168], 2550; alt [-0.0415, -0.0174] | CONFIRMED | - |
| 4 | I_R | +0.0134 [+0.0046, +0.0218] | +0.0134 [+0.0046, +0.0218]; alt [+0.0046, +0.0224] | CONFIRMED, see W-2 | MEDIUM |
| 5 | GF1 PARTIAL (PR-3 hand check) | PARTIAL | CLOSED needs UB(D_R) >= 0: -0.0168, fails. OPEN needs UB < 0 (holds) and 0.0296 > 0.0305 (fails). So PARTIAL | CONFIRMED; OPEN-vs-PARTIAL descriptive-only (W-1) | MEDIUM (words) |
| 6 | FAILS (rule 8): CLOSED refuted | UB(D_R) -0.0168 < 0 | same | CONFIRMED | - |
| 7 | F-GF not fired | not fired | follows from 5 | CONFIRMED | - |
| 8 | held-out moved WP5 vs T; fit moved | 0.1071; 0.0164 | 0.1071; 0.0164 | CONFIRMED | - |
| 9 | PR-4 WP-A = WP at T 5 | WPA_5 line | the WPA_5 hits equal WP_5 on all 4 trees (2550 / 2520 / 2619 / 2529), and so do the intervals and moved shares | CONFIRMED | - |
| 10 | P1-P6 scoring | all HELD; Brier P3 0.4200, P5 0.1225, P6 0.1600 | arithmetic re-done: 0.1^2+0.5^2+0.4^2 = 0.42; 0.35^2; 0.4^2. -1.395 < -1.534 / 2 | CONFIRMED (P6 words: W-2) | LOW |
| 11 | (b) identity KI1 / U2 / RP2 | REPRODUCED | -0.024800 / -0.45pp [-1.31, +0.41] / -0.004423 equal to the record (RESP-PROFILE-INFO outcome bracket; KEY-INFO-V2; UNION-AF-ROUTE) | CONFIRMED (spot check) | - |
| 12 | (b) readings NEITHER / K0-BETTER / NOT FIRED; P7 HELD x3 | as quoted | the rules were applied to the printed points, intervals and spread_K. KI1's CI contains 0. RP2's CI [-0.0039, -0.0008] excludes 0 and D < -0.000861. The bands hold. Not re-fitted (about 1 CPU-h; descriptive) | CONFIRMED (spot check) | - |

## Support (PR-1, PR-2), realised
- PR-1 DEFF: the measured Kish mean twin-group size is 1.0000 (3,445 groups / 3,445), so n_eff = 3,445. SE(D_R) is measured from the
  discordance 0.1388: sqrt(0.1388 / 3,445) = 0.00635 (tool) and sqrt((0.1388 - 0.0296^2) / 3,445) = 0.00633 (mine). MDE80 is
  0.0178 / 0.0177, against the registered 0.00663 / 0.0186. The bar for OPEN stays spread_V 0.0305 and does not change with n.
- PR-2: the measured I_R discordance is 0.0656, against the declared 0.10. SE(I_R) is 0.00436 and MDE80 0.0122 (registered 0.0151).
  94 held-out items that did NOT change leaf still changed hit, which confirms GF-B3: re-labelling cells moves hits.

## Defects / words owed
- W-1 (MEDIUM, words): "GF1: PARTIAL" must not be read as "the gap is shown to be smaller than the bar". Verdict line (f) declared
  OPEN-vs-PARTIAL DESCRIPTIVE-ONLY. |D_R| 0.0296 falls 0.0009 short of 0.0305, about 3 of 3,445 questions, and at WP_10 / conv it is
  0.0299. Fix: quote "GF1 PARTIAL: CLOSED refuted (UB(D_R) -0.0168 < 0; scoreable); not OPEN only by 0.0009 under the bar 0.0305
  (descriptive-only boundary)".
- W-2 (MEDIUM, interpretation of I_R and P6): T is filed by the tree's stored leaf_mu. Every WP / GL arm is filed by renormalised
  means of the flatLeaf-filed fit set. At T 0 no fit item moves (fit moved 0.0000), yet 9.23% of held-out items change leaf and
  M1 rises by +0.0090 [+0.0015, +0.0163] (WP_0 - T, 2535 vs 2504 hits). The five passes add only +0.0044 [+0.0000, +0.0087]
  (alt seed [-0.0003, +0.0090]; 15 hits). The re-draws show the same pattern: the T 0 share of I_R(T 5) is +0.0102 of +0.0116
  (af_s137), +0.0151 of +0.0174 (af_s2048) and +0.0134 of +0.0204 (af_s42_o1). On af_s137 the "would read CLOSED" is already
  met at T 0. On af_s2048 D_T's CI contains 0 ([-0.0238, +0.0038]), so no gap was shown to close. I_R as registered (M1(T-WP) -
  M1(T)) is computed correctly, so this is not a code defect and GF1 does not change. Fix (words of record): "I_R +0.0134
  [+0.0046, +0.0218], of which +0.0090 is the T 0 re-centring (centroids recomputed from the fit set, no item moved) and +0.0044
  [+0.0000, +0.0087] the five within-parent passes (not shown > 0)". P6 HELD is quoted with "carried mainly by the T 0
  re-centring". The re-draw "GF1 rule would read CLOSED" lines are not quoted without this qualifier and af_s2048's null D_T.
- D-3 (LOW): the GF1 PARTIAL line of the outcome prints each failed condition with its value ("upper bound of D_R -0.0168 >= 0",
  "|D_R| 0.0296 > 0.0305"). It reads as false inequalities. Fix in a later round: print "fails" beside each condition. The
  outcome file is write-once and stays as is.
- D-4 (LOW): the first --dry-run crashed with cp1252 UnicodeEncodeError on stdout and wrote nothing. Fix: reconfigure stdout to utf-8 in main().
- D-5 (LOW): (b) RuntimeWarning overflow in np.exp(alpha) (resp_structure_common.py:144). 0 of 2000 replicates were
  non-converged and the gated R2_int is finite (+0.054836). Fix: clip alpha before exp. Nothing to do for this run.

## Registrar duties
1. Outcome section + results JSON + ledger chip: "GAP-FIX VALID: GF1 PARTIAL (CLOSED refuted, scoreable; not OPEN by 0.0009,
   descriptive-only); F-GF NOT FIRED", with W-1 and W-2 as the quoting qualifiers. Ledger row: replace the PLAN chip.
2. FLAT-MIX-MMLU's LIMITATION sentence stays unbracketed (F-GF not fired). T-4's mechanism stays open. Add W-2's finding as
   descriptive: the stored leaf_mu vs fit-set means accounts for +0.0090 of M1 on af_clean_s42.
3. Re-draws (id-disjoint only): quote only with W-2's qualifier and af_s2048's null D_T.
4. (b): descriptive, own-source subset SEEN. Quote KI1 NEITHER / RP2 K0-BETTER / U2 NOT FIRED as "under source-gated filing
   (legitimate only when the source is known at query time)". No registered verdict moves.
5. Carry D-1 of READY_gap-fix (decide() fixture for 0.0186 < |D_R| <= 0.0305) and D-3..D-5 to the next code round. The PR-3
   hand check above stands in for D-1 on this run.

## Commands
```
git rev-parse HEAD:tools/analysis/gap_fix.py ; git hash-object tools/analysis/gap_fix.py         # both 7c0691e8...
sha256sum experiment_results/gap_fix/gap_fix_{a_outcome.txt,a_arms.csv,b_outcome.txt}            # = report
(cd E:/TaxoArena_backup_2026-10-06_gap_fix && sha256sum -c SHA256SUMS.txt)                         # 9/9 OK
powershell -NoProfile -File E:/TaxoArena_tmp/busy.ps1  -> rc 1 before each recompute
PYTHONIOENCODING=utf-8 OMP/OPENBLAS/MKL=1 python tools/analysis/scratch_dir.py --run -- python E:/TaxoArena_tmp/postrun_gapfix/recompute_a.py
  # uses gap_fix only for data plumbing (tree_data, v_parts, FM.partition_assign/cell_ids); own parent-subtree masks, own
  # Lloyd WP x5 from z0 = argmax(X leaf_mu^T), own cell-majority M1, own percentile bootstrap (seed 20260926 B 1000; alt seed 7 B 4000)
  # -> n 3445, groups 3445, Kish 1.0; hits T 2504 V0 2652 WP0 2535 WP5 2550; spread_V 0.0305; D_T/D_R/I_R as table;
  #    WP0-T +0.0090 [+0.0015,+0.0163]; WP5-WP0 +0.0044 [+0.0000,+0.0087]; unmoved-but-changed-hit 94
grep -n 'IDENTITY' experiment_results/gap_fix/run_a.log                                          # 4 trees REPRODUCED
grep -o '0\.004423' docs/judge_v2_program.md ; grep 'KI1 K0-BETTER' ... ; grep 'D_K -0.45pp' ...  # (b) identity = record
```
Own mutants: none (post-run; no code change). Data object read-only: the tool's own sha before == after on gen/eval views (run_b.log).
