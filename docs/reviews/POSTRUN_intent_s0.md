# POSTRUN review — INTENT-TRANSFER-S0 (run 6d04e84 on 8999678)

Reviewer: adversarial-reviewer, 2026-10-01. Zero calls; no JVM; nothing written to any DB (sha256 of all four DBs equal before and after my
script). Registration `docs/judge_v2_program.md` L22092-L22134 ("## Registered 2026-09-29 (before any code or call) — INTENT-TRANSFER-S0: ..."),
brackets L22146-L22158 (C-1, C-4 B2/B3/B7, Hanley-McNeil) and L22230-L22240 (emb pins), _as_of 6d04e84.

## Verdict

**VALID.** Every deciding number reproduces to the printed digit from the pinned DBs with an independently written script;
every criterion word and every falsifier fire/non-fire follows the registered logic. C1a HELD (3 of 3, all nomic), C1b NOT FIRED,
C2 HELD, C3 HELD, C4 FAILED, F4 FIRED; F1, F1', F2, F3 NOT FIRED. Valid under the registrar's wording conditions W-1..W-5 below.

## Data object

| item | value | check |
|---|---|---|
| script | `tools/analysis/intent_transfer_s0.py` blob:f662ceb19738f515972871f5963f5dcfc764a271 (LF; `git hash-object`) | = READY_emb_pace pin (L22230ff) and the outcome header |
| ingest DB | sha256-bytes 487e0093719c184c… | `sha256sum` = pins file |
| emb DBs | qwen3 9e100e04…, nomic 4aafd6c7…, gemma b187b82f… | `sha256sum` = pins file; no -wal/-journal sidecars (`ls` count 0) |
| rows | 53,454; side/stem_key/hash_side re-derived with `split_side` for every row: **0 mismatches**; every OOS row side EVAL | own script |
| denominators | EVAL in-scope MASSIVE 4,946 / CLINC 6,672 / Banking77 3,908; OOS 1,350; CLINC GATE 2,333; TRAIN 9,870 / 13,487 / 7,885 | = outcome |
| vectors | 56,350 texts read (kept items + 3,222 C4 variants; the 1,000 D5 pairs not needed), 0 missing per embedder | own script |
| run commit | 6d04e84 touches 5 files, all under experiment_results/ (`git show --stat`, full, not piped) | |
| outcome vs log | `diff` of s0_run.log L14ff against s0_outcome.txt: 1 line differs (console rendering of the em dash only) | |

## Deciding claims

| claim | outcome | mine | status | sev |
|---|---|---|---|---|
| C1 massive fine D(nomic) | -0.06521, basic [-0.07370, -0.06137], bar 0.02463 -> WORSE | -0.06521, basic [-0.07387, -0.06161] (own B 1,000, own seed), bar 0.02463 -> WORSE | CONFIRMED | - |
| C1 clinc fine D(nomic) | -0.02539 [-0.02972, -0.02400], bar 0.00968 -> WORSE | -0.02539 [-0.02989, -0.02400] -> WORSE | CONFIRMED | - |
| C1 banking77 fine D(nomic) | -0.05443 [-0.06237, -0.05140], bar 0.01648 -> WORSE | -0.05443 [-0.06229, -0.05186] -> WORSE | CONFIRMED | - |
| C1 fine D(gemma) M / C / B | +0.03340 BETTER / -0.00691 NEITHER / +0.05628 BETTER | +0.03340 / -0.00691 / +0.05628, same words | CONFIRMED | - |
| C1a | HELD, 3 of 3, all nomic | 3 of 3 nomic; still HELD on the 2 R-1-SCOREABLE corpora alone (MASSIVE nomic DESCRIPTIVE-ONLY: spread 0.02463 > 0.020) | CONFIRMED | - |
| C1b coarse D | nomic M -0.01164 / C -0.09114; gemma M +0.13529 / C -0.04216; all NEITHER/BETTER -> NOT FIRED | identical points; bars 0.03858 / 0.13023 / 0.04419 / 0.13622 | CONFIRMED (see W-2) | - |
| C-1 basic interval used | basic decides, percentile descriptive | code `basic_ci` = [2D - q97.5, 2D - q2.5] feeds `c1_status`; the percentile rule gives the SAME 10 statuses (own run, "pct-rule"), so C-1 decides no word here | CONFIRMED | - |
| C2 AUROC | 0.97437 [0.97043, 0.97813] | 0.97437 (sklearn `roc_auc_score`); own component bootstrap [0.97016, 0.97802], SE 0.00206 | CONFIRMED | - |
| C2 FPR95 | 0.1578 at GATE thr 0.74326 (GATE TPR 0.9503) | 0.1578, thr 0.74326, GATE TPR 0.9503, EVAL TPR 0.9601 | CONFIRMED | - |
| C3 rho M / C / B | 0.2705 [-0.0154, 0.5102] / 0.4107 [0.2652, 0.5405] / 0.3945 [0.1741, 0.5834]; cells 57/145/76 | 0.2705 [-0.0196, 0.5097] / 0.4107 [0.2570, 0.5488] / 0.3945 [0.1692, 0.5799]; 57/145/76 | CONFIRMED | - |
| C4 S | 0.75978 [0.74566, 0.77419], n 3,222 | 0.75978, own bootstrap [0.74556, 0.77440]; n 3,222 | CONFIRMED | - |
| C4 construction | 4,946 EVAL, 3,310 with a slot, -56 no alternative, -32 TRAIN collision, 0 unchanged, 0 mismatch = 3,222 | own B7 implementation (regex parse, TRAIN inventory per (intent, slot type), seed 4104): same counts; variant item list **equal** to s0_c4_variants.csv (3,222 ids, in order) | CONFIRMED | - |
| C4 support | clusters 3,207, DEFF 1.0093, n_eff 3,192, SE 0.00748, MDE80 0.02094 | 3,207, Kish 1.0093 (own, from the originals' components), n_eff 3,192, SE 0.00744, MDE80 0.0208; upper(S) 0.774 is 2.6pp under 0.80 -> FAILED is not a power artefact; seeds 1-4 S 0.739-0.772 all < 0.80 | CONFIRMED | - |
| F-lines map | F1<-C1a FAILED, F1'<-C1b FIRES, F2<-C2 FAILED, F3<-C3 FAILED, F4<-C4 FAILED | code `criteria_lines` matches the registration's FALSIFIERS; only F4 fires | CONFIRMED (wording: D-1) | MEDIUM |
| P5 Brier | C4 HELD p 0.85, outcome NO, Brier 0.7225; mean of 7 = 0.2218 | (0.85-0)^2 = 0.7225; mean (0.2025+0.1225+0.1600+0.1225+0.0625+0.7225+0.1600)/7 = 0.22179 | CONFIRMED, honest | - |

Support (re-derived from cluster sizes): measured Kish DEFF 1.0093 / 1.0000 / 1.0015 (declared 1.05, conservative); C1 measured SE
0.00134-0.00481 (declared 0.004); C3 SE_z 1/sqrt(54) = 0.1361, 1/sqrt(142) = 0.0839, 1/sqrt(73) = 0.1170 = outcome. Descriptive lines D1-D6,
supervised-centroid / kNN-1 stability and co-filing: NOT recomputed (spot check only: P6 D4 0.8436 - 0.7663 = +0.0773 = outcome).

## Defects

- **D-1 (MEDIUM, record wording).** Each F-line prints the falsifier's trigger as an assertion after its status: "F1: NOT FIRED -- C1a FAILED: ...",
  "F1': NOT FIRED -- C1b FIRES: ...". In this outcome the ONLY line containing "C1a FAILED", "C1b FIRES", "C2 FAILED" or "C3 FAILED" is the
  NOT-FIRED F-line (grep count 1 each, all F-lines), so a phrase grep reads a non-fire as a fire. The outcome file is write-once: not fixable in
  place. Fix: the registrar quotes F-lines only as "F1 (fires iff C1a FAILED): NOT FIRED"; for the next script, print
  `"%s (fires iff %s): %s"` with the trigger in parentheses and the consequence text only on a FIRED line.
- **D-2 (LOW).** The outcome's DOES NOT SHOW line is a digest of the registered one (drops "CLINC OOS has documented mislabels", "a low H is the
  designer's hierarchy", "qwen3 without an instruction"). Fix: the registrar quotes the registration's DOES NOT SHOW, not the outcome's.
- **D-3 (LOW, descriptive).** "near-copies clinc: 1110 of 8022 EVAL items" counts the 1,350 OOS rows in the EVAL denominator (6,672 + 1,350);
  the other corpora count in-scope only. Fix: the registrar states the denominator as "8,022 EVAL incl. 1,350 OOS".

## Registrar's wording conditions

- **W-1 (C1a).** "Fine structure is embedder-dependent against gold labels on 3 of 3 corpora": the dependence is TWO-SIDED, not "qwen3 best".
  nomic is WORSE at fine on all three (D -0.065 / -0.025 / -0.054); gemma is BETTER on MASSIVE (+0.033 fine, +0.135 coarse) and Banking77
  (+0.056) and NEITHER on CLINC. P2's "qwen3 BETTER than both" resolved NO. MASSIVE's nomic line is R-1 DESCRIPTIVE-ONLY; C1a holds on CLINC
  and Banking77 alone.
- **W-2 (C1b).** "NOT FIRED" is carried by the k-means seed spread at the coarse K (CLINC K 10: bar 0.130 / 0.136), not by a small D:
  nomic's coarse D on CLINC is -0.091 with its basic CI wholly below 0, gemma's -0.042 likewise, MASSIVE nomic -0.012 likewise. With a bar of
  MDE80 only, C1b would FIRE on CLINC. Write "not fired (coarse differences lie inside the coarse k-means seed spread)", never "coarse holds",
  "coarse is embedder-independent" or parity (registration (g) and "a non-fire is never parity").
- **W-3 (C2).** AUROC 0.974 [0.970, 0.978], FPR95 0.158, on CLINC OOS (one curated set) with K 150 qwen3 seed 0; label-free k-means scores
  equal the supervised-centroid AUROC 0.976 to 0.002. No sentence about OOS on real traffic, capability text or MMLU-Pro cells. P3 FAILED in
  the favourable direction (predicted A 0.88, FPR95 0.45).
- **W-4 (C3).** HELD on CLINC and Banking77 only; MASSIVE's interval spans 0 ([-0.015, 0.510]: "not shown positive", registered THIN).
  rho 0.27-0.41 is a positive sign, not a usable per-cell diagnostic.
- **W-5 (C4 / F4).** F4 FIRED with its registered consequence, quoted verbatim from the registration ("every filing rate of record (81.6%)
  carries 'surface-sensitive, untested on capability text'"). Print beside it, from the same outcome: supervised TRAIN-centroid label
  stability 0.834 and kNN-1 0.829 under the same swaps (only 3pp above the 0.80 bar: the swap moves gold-label filing in ~17% of
  variants; descriptive, not recomputed here), random same-intent co-filing 0.692. The instability therefore belongs to the embedding geometry under slot-value swaps at least
  as much as to label-free cells; do not write "label-free cells are unstable whereas declared cells are stable". S by slots in the item:
  1 slot 0.774 (n 2,094), 2 slots 0.732 (850), 3+ 0.737 (278): every stratum below 0.80.
- P5's Brier 0.7225 is honest (p 0.85 on an event that did not occur) and stays in the mean 0.2218; no prediction is re-scored.

## Commands

```
sha256sum intent_transfer_corpora_v1.db intent_emb_*.db ; ls intent_*-wal intent_*-journal   # pins equal; 0 sidecars
git hash-object tools/analysis/intent_transfer_s0.py                                          # f662ceb1...
git show 6d04e84 --stat                                                                       # 5 files, experiment_results/ only
diff <(sed -n '14,$p' experiment_results/intent_transfer_s0/s0_run.log) experiment_results/intent_transfer/s0_outcome.txt
python <scratchpad>/rv_s0post/rv.py   # own: split re-derivation, own skmeans (k-means++ on 1-cos, seeds 0-4) + sklearn NMI/AUROC,
                                      # own component bootstrap (B 1,000 C1, 1,000 C2, 2,000 C3/C4, own seeds), own B7 variants, PRE/POST sha
for p in "C1a FAILED" "C1b FIRES" "C2 FAILED" "C3 FAILED" "C4 FAILED"; do grep "$p" s0_outcome.txt | grep -c '^F'; done   # 1 each (D-1)
```
