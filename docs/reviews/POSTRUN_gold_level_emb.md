# POST-RUN review: GOLD-LEVEL-EMB (--run, main, blob 86765764)

Reviewer: adversarial-reviewer, 2026-10-02. Run from main at merge 9b86d32d, after brackets d1abedce.
`git hash-object tools/analysis/gold_level_emb.py` = 867657643886b5efff37bd7dec0a813bdace6e33 (LF). READY: docs/reviews/READY_oos_gold.md.
Zero calls.

## Verdict

**VALID.** Recomputed from nmi_gold.csv, every coarse D and seed term matches the outcome to 1e-5. All 16 statuses come out the same,
and so do the four family verdicts, the reading (MIXED), F-GL (FIRED) and F-GL' (NOT FIRED). Every status stays the same with SE_boot
scaled anywhere from 0 to 3 times its value.

I also rebuilt five NMI values of record from the raw DBs: my own sqlite read, my own slice and renormalisation, my own side masks and
sklearn NMI. The k-means is S0's skmeans, shared. All five agree within 3.5e-7.

The outcome was written once and equals the console line for line. The checks the READY review set (C-4, C-6, R-2) are applied below.
Conditions on the wording: W-1..W-6.

## Per-claim table

| claim | mine | status |
|---|---|---|
| C-4 identity counts: q4 130 NMI + 32 H, q8 15, qcard 15, g 40 + 8 H, gcard 15, nomic 50; max deviation <= 4.98e-7 | outcome lines 8-13 carry exactly these counts, all REPRODUCED. The six lines were counted, not just read. | CONFIRMED |
| C-6 nomic_selection.json | Written once, 10:17:18 (outcome and CSVs 10:20:48), sha256 ab3b3855..., which equals the outcome's line. Its script_blob_lf is 86765764. The two earlier refusals (gold_run_refused1/2.log, 4 lines each) stopped at the heavy-process guard (java alive) before any pin or read, and wrote nothing. Nothing was moved aside. | CONFIRMED |
| GB2 ordering | Console line 35 (selection written) comes before any nomic EVAL read. The eval_idx guard would have refused otherwise. | CONFIRMED |
| d_n* = 256 | GATE scores 0.8210009 / 0.8196263 / 0.8212751 for 256 / 512 / 768. The maximum is at 768; 0.8212751 - 0.8210009 = 0.00027, within the 0.001 tie, so the smaller d (256) is taken (EDS rule). | CONFIRMED |
| denominators MASSIVE 4,946 / 4,923 (Kish 1.0093), CLINC 6,672 / 6,672, Banking77 3,908 / 3,905 | Equal to my SQL in the READY review (row 8). nmi_gold.csv: 18 coarse keys x 30 seeds, 4 identity keys x 5, 33 fine keys x 5 = 725 rows. | CONFIRMED |
| GL1 D and SE_total, 16 statuses | Recomputed from the CSV (D, var of the per-seed differences / 30) with the printed SE_boot. Every D and seed term equal to 1e-5; SE_total equal (n* MASSIVE 0.00610 vs 0.00611, q4096 CLINC 0.00642 vs 0.00641: rounding of the printed SE_boot). | CONFIRMED |
| families DIM UNDETERMINED, QUANT INVARIANT, PROMPT NOT-INVARIANT, EMBEDDER NOT-INVARIANT; MIXED; F-GL FIRED (PROMPT, EMBEDDER); F-GL' NOT FIRED | Same. Robust to SE_boot x0..x3, because the seed term dominates every contrast (0.0040-0.0069, against SE_boot 0.0010-0.0040). | CONFIRMED |
| margin 0.05 sensitivity: DIM, QUANT, PROMPT INVARIANT; EMBEDDER NOT-INVARIANT | Same. PROMPT INVARIANT at 0.05 hangs on gcard-g768 MASSIVE, whose lower 90% bound -0.04972 clears -0.05 by 0.0003. | CONFIRMED (fragile) |
| raw NMI spot checks (coarse, EVAL in-scope) | q8 CLINC s17 0.513840; gcard MASSIVE s22 0.758868; n*@256 CLINC s29 0.475979; qcard CLINC s11 0.551866; q256 MASSIVE s13 0.678404. All equal to nmi_gold.csv within 3.5e-7. | CONFIRMED |
| GL2 fine D (descriptive) | All 24 equal to 1e-5 from the CSV. | CONFIRMED |
| write-once | outcome.txt (192 lines, sha256 7e00d7d9...), nmi_gold.csv (6c24845b...), h_gold.csv (c7b014c1...) created by mode x. The console's outcome block occurs once and equals the file (192 of 192). Pins unchanged before and after. The fit audit shows 752 TRAIN fits, 0 with an EVAL row, 0 OOS rows. | CONFIRMED |
| Support after the run | DEFF is Kish 1.0093 / 1.0000 (measured). SE_total measured 0.0045-0.0074, against planned 0.0062-0.0085. The verdict lines are re-stated at the measured SE in the outcome. | CONFIRMED |

## Predictions re-scored (all agree with the outcome)

- P1 numeric. The 8 new contrasts: 6 HELD (q8 x 2, qcard MASSIVE, gcard MASSIVE, n* x 2) and 2 FAILED (qcard CLINC -0.0345 below
  -0.030; gcard CLINC +0.0316 above +0.010). The 8 SEEN contrasts: 5 HELD and 3 FAILED (q256 MASSIVE, q512 MASSIVE, g768 MASSIVE). None
  of the SEEN results counts as a confirmation.
- P2 Brier: DIM UNDETERMINED (p 0.30), 0.4900 on that event; QUANT INVARIANT 0.0625; PROMPT NOT-INVARIANT 0.2025; EMBEDDER
  NOT-INVARIANT 0.0100.
- P3 reading MIXED (p 0.17): Brier sum 1.1348. F-GL fired (p 0.95): Brier 0.0025.
- P4 (GL2): fine DIM all 9 EQUIVALENT is true (0.1600); fine g768 DIFFERENT on MASSIVE and Banking77 is true (0.0225, SEEN).
- P5 (GL3): H(g768) > H(q) at every slice on MASSIVE is true (0.0025, SEEN). |H(q8) - H(q1024)| <= 0.02 on both corpora is false
  (0.6400): CLINC -0.0359; the H intervals are wide.

## Wording the registrar must use (conditions)

- W-1 (scope). "k-means (K = gold coarse count) against the gold coarse labels of MASSIVE and CLINC (EVAL in-scope rows), 30 seeds;
  qwen3-embedding slices, Q8_0, CARD prompts, embeddinggemma 768, nomic at its GATE-selected 256". Nothing about trees, leaves,
  construction or MMLU-Pro. The registered WILL-NOT-SHOW list is quoted in full.
- W-2 (F-GL). "F-GL FIRED through PROMPT and EMBEDDER: the gold coarse level is not invariant to prompt or embedder here. The
  literature's reconciliation must name those two families, not the level." The reading is MIXED, so no reading-table sentence is
  written; the families are recorded joined: DIM UNDETERMINED / QUANT INVARIANT / PROMPT NOT-INVARIANT / EMBEDDER NOT-INVARIANT.
  Never use the TRANSFORMATION or NO-LEVEL-ADVANTAGE sentence (neither fired).
- W-3 (R-2, DIM). "DIM UNDETERMINED: all 6 statuses are on contrasts whose 5-seed points were seen before registration (G-4). The
  30-seed points are new data. 4 of 6 are EQUIVALENT; q256 MASSIVE (D -0.0217) and q4096 CLINC (D +0.0244) are NEITHER." Never write
  "slice-invariant" or any parity for DIM. Disclose that the seen 5-seed MASSIVE q256 point (-0.049) shrank to -0.022 at 30 seeds:
  the registration's prior (coarse moves with the slice) rested on seed noise at 5 seeds.
- W-4 (QUANT). "Within 0.025 NMI at the gold coarse level, qwen3 Q4_K_M and Q8_0 (1024 RAW) are equivalent on MASSIVE (D -0.0054,
  90% [-0.0135, +0.0027]) and CLINC (D -0.0058, 90% [-0.0138, +0.0023])." This is new data (P2 p 0.75). The H difference on CLINC
  (-0.036) is descriptive only.
- W-5 (PROMPT). Three of the four statuses are DIFFERENT, with mixed signs: qwen3 CARD on CLINC -0.034; gemma CARD on MASSIVE -0.041
  and on CLINC +0.032. qwen3 CARD on MASSIVE is NEITHER (+0.025). Word it as "the card prompt moves the coarse readout by up to 0.04
  NMI, in no consistent direction", never as "CARD helps" or "CARD hurts". The 0.05 sensitivity (INVARIANT) holds by 0.0003 and is
  never quoted as a finding.
- W-6 (EMBEDDER). NOT-INVARIANT through nomic@256 on both corpora (-0.047 / -0.069; new data) and gemma 768 on MASSIVE (+0.106; a seen
  contrast, 5-seed +0.086). gemma on CLINC is NEITHER (-0.022). F-GL' is NOT FIRED. Do not write "which embedder is better"
  (registered as not shown). GL2 (fine) is descriptive only: DIM and QUANT EQUIVALENT on all 3 corpora, PROMPT and EMBEDDER
  NOT-INVARIANT. It may be printed beside, never as a test of the granularity claim.

## Defects

None on the deciding path. Disclosure for the record: the coarse 30-seed spreads (up to 0.13 NMI) dominate every SE (seed term
greater than SE_boot in 16 of 16), so the coarse k-means readout is seed-volatile at small K. The 5-seed coarse points of record
(EMBED-DIM-SLICE, S0 C1) should be quoted with that spread beside them.

## Commands

```
git hash-object tools/analysis/gold_level_emb.py; sha256sum experiment_results/gold_level_emb/*; ls -la --time-style=full-iso experiment_results/gold_level_emb/
grep -n "REFUS|wrote|NOMIC SELECTION" scratchpad/gold_run.log scratchpad/gold_run_refused{1,2}.log; python - : outcome lines vs the log (block equal, once)
python - : nmi_gold.csv -> D, var(a-b, ddof 1)/30, SE_total with the printed SE_boot (and x0..x3), statuses at 0.025 / 0.05, families; fine D; D5 vs D30 for the seen contrasts
python - : 5 coarse NMIs rebuilt (own sqlite '>f4' read, first d coords L2-renormalised, own TRAIN/EVAL masks, ITS.skmeans, argmax filing, sklearn NMI)
```
