# POSTRUN: EMBEDDER-CROSS-FLAT E1 readout (e1_readout.py --run; E1-ROUTE)

Adversarial-reviewer, 2026-10-02. Zero calls. Run from main, script **blob:88f7990c** (LF; `git rev-parse main:tools/analysis/e1_readout.py`
= the outcome's [SCRIPT] line), after the author's WAL checkpoint. Outcome `experiment_results/e1_route/e1_readout_outcome.txt`
(148 lines, LF, sha256-16 0bc3bdf1383e5e66) and `e1_readout_partitions.csv` (23 lines, sha256-16 e519403ce07a6e77), both untracked,
mtime 12:50:07. READY: READY_e1_readout.md (bcb7f2f8). Pre-data brackets D1 / D2 / D5 (D3 noted): 09299c3a, committed 04:38:45,
before the run (prog L23555-L23559).

## VERDICT

**VALID.** For N-raw (PRIMARY): FLAT C1 FAILED, C2 FAILED, **L1 FIRES on M1 AND M2**; **FILING HELD-WORSE -0.0456 [-0.0617, -0.0294]**
(n 3,445 paired); **F-E1 FIRES**; P3 FIRES (Brier 0.2025); P4 HELD (Brier 0.16 on HELD-WORSE); P7 FIRED (Brier 0.16). N-card (SECONDARY,
D3 majority) is printed and scores nothing. My independent recompute reproduces the deciding numbers to the printed digit.
Scope of every sentence: one corpus (MMLU-Pro), one draw per arm, the content-closed af_clean_s42 TRAIN, R256.

## Per-claim table (deciding claims)

| # | claim (outcome) | mine | status | sev |
|---|---|---|---|---|
| 1 | FILING b 327, c 484, diff -0.0456, Wald [-0.0617, -0.0294], SE 0.00823 | my own code (corpus by SQL from the frozen p2dca file + eval_question_link + mmlu_pro ORDER BY id; leaf vmfMu from snapshots.db; unit 256-slices by text; argmax routing; first-seen majority over the 8,324 train texts; Wald): b 327, c 484, -0.0456, [-0.0617, -0.0294], SE 0.00823 | CONFIRMED to the digit | - |
| 2 | top-1 N-raw 0.6813, af_clean_s42 0.7269 (identity 0.727 [0.712, 0.741]) | 0.6813 / 0.7269 | CONFIRMED | - |
| 3 | exact McNemar p 3.919e-08 (beside) | scipy binomtest(327, 811): 3.919e-08 | CONFIRMED | - |
| 4 | C1: T - V0 = -0.0438, spread_V 0.0136, CI [-0.0572, -0.0299] -> FAILED; L1 on M1 | from the CSV: 0.681277 - 0.725109 = -0.043832; spread max V0 0.725109 - min V4 0.711466 = 0.013643; -0.0438 < -0.0136 and hi < 0 -> fires | CONFIRMED (arithmetic from the CSV; V fits not re-run) | - |
| 5 | C2: -1.026 x1e-3, spread_V 0.262, CI [-1.733, -0.321] -> FAILED; L1 on M2 | 11.653160 - 12.679217 = -1.026057; spread 12.679217 - 12.416732 = 0.262485; fires | CONFIRMED (arithmetic) | - |
| 6 | DEFF 1.0000, n_eff 3,445 | re-measured: 3,445 held-out texts, 3,445 distinct stem_key groups, Kish m-bar 1.0 -> DEFF 1, n_eff 3,445 | CONFIRMED | - |
| 7 | Support (filing): realised discordance 0.2354, SE 0.00823, MDE80 0.0230; tag SCOREABLE | 811 / 3,445 = 0.2354; 2.80 x 0.00823 = 0.0230; \|P4 -0.04\| > max(0.0185, 0.0230). The planned d 0.15 was optimistic (SE 0.00660 planned vs 0.00823 realised, +25%); the verdict leg is the interval, which excludes 0 by 0.0294 | CONFIRMED | - |
| 8 | Support (L1): M1 bar max(0.0186, 0.0136, 0.0195) = 0.0195; M2 bar max(1.000, 0.262, 1.009) = 1.009 | M1 clears by 0.0243; **M2 clears by 0.017 x1e-3 (thin)**: -1.026 against the tightened bar 1.009 (registered bar 1.000: by 0.026) | CONFIRMED; M2 margin THIN | LOW |
| 9 | console = outcome, written once | run log lines 1-148 == outcome (diff, CR stripped); log line 149 "outcome written (write-once)"; 1 "REFUS" line in the log = the expected DISCRIMINATOR REFUSE (0.9603); write path is mode `x` behind a refuse-if-exists precheck (M15 / ST-F, READY) | CONFIRMED | - |
| 10 | inputs unchanged | [PIN before] == [PIN after] for all 11 pins; the corpus DB now sha256-16 cdf3a47888017a1a (= the pin, mtime 12:47 = the checkpoint, before the run) and 0 sidecars beside it (count), so N-1 (plain mode=ro open) left nothing | CONFIRMED | - |
| 11 | P4 HELD; D5 | -0.0456 inside [-0.08, 0.00]; not on an endpoint, so D5 did not bind | CONFIRMED | - |

## Conditions from the READY, applied

- **D1 / D2 / D5 brackets (09299c3a):** pre-data, before the run. The outcome follows them: top-1 = M1 per question from the 8,324 train
  texts, each tree in its own embedder; the Wald interval decides and the exact p is printed beside it; D5 did not bind.
- **D3:** N-card's numbers carry "D3 majority, 8,242 of 8,324; not FLAT verbatim" (the outcome prints the line). N-card is never F-E1 / P / reading.
- **R-2 (applied below in the wording):** FLAT-GENERALITY's k = 2 is on M1 only (af_s42_o1 is not independent of af/seed_42, and the
  re-draws are id-disjoint only). N-raw's L1 fires on M1 AND M2, so the printed reading-table sentence is true on M1 only. On M2 no qwen3
  re-draw fired (FLAT-MIX-MMLU's af_clean_s42 did).
- **R-3 / R-4 (LOW, builder):** not acted on. They are moot for this run, because the pins compare equal and the hygiene counts are 0 / 0 / 0 in the run. Both stay open for any reuse of the script.

## Defects / notes

- **D-PR-1 (LOW, registrar):** never quote the bare reading-table sentence. Use the qualified wording below.
- **D-PR-2 (LOW, descriptive):** N-raw's V2 hit max_iter (200, converged False; N-card's V3 likewise). Neither is an extreme of its
  spread (M1 and M2 extremes are V0 / V4 for N-raw), so neither moved a spread or a verdict. Report it beside the spreads.
- **D-PR-3 (note, interpretation; DESCRIPTIVE-ONLY):** the flat vMF fitted in nomic space (V0 M1 0.7251) is within 0.002 of the qwen3 tree
  (0.7269). The filing loss therefore goes with the nomic TREE, not with the nomic space's flat partition. One draw per arm does not
  separate an embedder effect on construction from draw-to-draw variation of the construction (Support (g); RP36).
- **Note (rule 7, operator):** an IDE Gradle daemon was alive during the run. The readout is not a construction, and the pins compare equal. The operator log should say the daemon ran no construction.

## Registrar's wording (proposed; insertion only)

"E1 (EMBEDDER-CROSS-FLAT E1-minimal; 2026-10-02, 0 calls; post-run review VALID). This is one label-free anchor-free nomic-embed-text build
(N-raw, raw protocol, 84 leaves) on af_clean_s42's content-closed TRAIN (8,125 fit texts), compared with af_clean_s42 (qwen3, 82 leaves) on the
3,445 held-out questions of p2dca (content-closed under stem_key at norm-v1). FILING is HELD-WORSE: flatLeaf top-1 0.6813 against 0.7269,
paired difference -0.0456, Wald 95% [-0.0617, -0.0294] (b 327, c 484; DEFF 1 measured, n_eff 3,445, realised MDE80 0.0230). F-E1 FIRES.
The framing's planned SQ5 word "the method's" is overturned for the tree-FILING clause on MMLU-Pro (one corpus, one draw per arm). No
recorded number moves, and this is not a scored embedder contrast. FLAT at the tree's own k: C1 and C2 FAILED; L1 FIRES on M1 (-0.0438
[-0.0572, -0.0299], spread_V 0.0136) and on M2 (-1.026 [-1.733, -0.321] x1e-3, spread_V 0.262; the margin over the tightened bar 1.009 is
thin, 0.017). Reading: the purity loss appears in 2 of 3 qwen3 anchor-free re-draws (on M1 only; af_s42_o1 not independent; id-disjoint
re-draws) and in the one nomic draw. The nomic draw also loses on M2, which no qwen3 re-draw did. P3 FIRES, P4 HELD, P7 FIRED. N-card
(SECONDARY, D3 majority 8,242 of 8,324) reads alike and is not scored. DOES NOT SHOW: an embedder contrast as a scored test,
embedder (in)variance in general, another corpus, or whether the loss is the embedder's or the draw's."

## Commands (bash; R = repo root, S = scratchpad)

```
git rev-parse main:tools/analysis/e1_readout.py; git show -s --format='%h %ci' 09299c3a   # 88f7990c; 04:38:45 (run 12:50)
diff <(tr -d '\r' < S/e1r_run.log | head -148) <(tr -d '\r' < R/experiment_results/e1_route/e1_readout_outcome.txt)   # equal
python S/rv/post.py      # held-out 3,445 / train 8,324; m-bar 1.0; M1 0.7269 / 0.6813; b 327 c 484; -0.0456 [-0.0617, -0.0294]; p 3.919e-08
python -c "<CSV arithmetic>"   # -0.043832, 0.013643, -1.026057, 0.262485
sha256sum R/mmlu_pro_dataset_cache_v2.db; ls R/mmlu_pro_dataset_cache_v2.db-* | wc -l   # cdf3a478…; 0
```
