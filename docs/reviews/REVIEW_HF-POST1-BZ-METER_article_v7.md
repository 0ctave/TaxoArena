# Review: HF post 1 draft v7 (benchmark-zoom/article.md, rebuilt on BZ-METER v2) against the v2 record, 2026-10-12

Reviewer: adversarial-reviewer. Authority: D-2026-10-11-9, D-2026-10-12-1/-2. Object: untracked
`docs/drafts/hf/benchmark-zoom/article.md` (413 lines) + six `figures/meter_*.png` from `make_meter_figures.py`
(LF blob f0e7d296; CRLF/working-tree sha256 24f29321...b80d). Record: benchzoom master 9a42c49 (porcelain 0 before and
after; the brief's "e1fb080" is the older tip of the v5 review), registration LF blob 5c457088 (= working tree, [R18]),
`E:/benchzoom_demo/meter_v2` (outcome.json sha256 7bca5558...bc47 reproduced; SHA256SUMS 11/11 OK), gate.txt,
POSTRUN_BZ-METER-v2 (31c875f6), READY_BZ-METER-R18 (82371943). meter_v1 outcome af1f8042... unchanged. Zero LLM calls.
Taken as given from REVIEW_HF-POST1-BZ-METER_article_v5 (CONFIRMED there, text unchanged): ADAPTIVE-PROFILE paragraph and
C-1 table, UNION-AF-ROUTE / TREE-CUT wording (M4 applied), README dataset facts (spot re-checked, below).

## Verdict: NOT READY-FOR-AUTHOR (0 HIGH, 4 MEDIUM, 9 LOW; all text/figure fixes). After M1-M4: READY-FOR-AUTHOR with A1-A4.

Every number in the BZ-METER body traces to outcome.txt / gate.txt / the registration to the printed digit (script
below: of all decimals in L29-L260 only 1.35 and 5.2 are not literal, both correct arithmetic). Every verdict word,
the depth, the slope word and both harness words match the run and the [R2]/[R4]/[R18] rules. F1, F3, E2 and the
[R17] v_j label are applied. Blog rules of reg S9: no region/skill/demand/pocket; WORK numbers labelled; strict read
secondary; demo numbers said to move. The snippet runs on a fixture. The defects are one factual overclaim, one heading
that reframes undecided/unmeasurable words as "does not add", one "read once" that the post itself contradicts, and a
figure whose footer (carrying the pair-rule disclosure) is clipped.

## Per-claim table (deciding claims)

| # | Claim (line) | Result | Mine vs claimed | Sev |
|---|---|---|---|---|
| 1 | Harness: MATH -0.0005 (0.0015) 0/20; MMLU-Pro -0.0057 (0.0020) 0/20; passed (L179-182) | CONFIRMED | OT L4-L5 | - |
| 2 | Slope +4.934 (0.341) q95 +0.547; +8.927 (0.477) q95 +0.234; HELD; z 14.5/18.7; 9x / 38x (L90-98) | CONFIRMED | OT L8, L51, L82; 4.934/0.341 = 14.47, 8.927/0.477 = 18.71; 9.02x, 38.15x | - |
| 3 | 22-model slope +12.242 q95 +1.937 (secondary) (L99-101) | CONFIRMED (numbers) / REFUTED (inference) | OT L29; "null is larger on a smaller roster" contradicted by MMLU-Pro 23 models q95 0.234 < MATH 69 models 0.547 (M1) | MEDIUM |
| 4 | MATH L1 +1.129 (0.122), L2 +0.452 (0.068), L3k\|C +0.394 (0.084) SUPPORTED; L3t +0.058 (0.011) NOT SUPPORTED, z 5.2, g+2SE 0.080 (L191-212) | CONFIRMED | OT L9-L12; 0.0577/0.0111 = 5.20; 0.0577+0.0222 = 0.0799; rule (2) precedes BELOW INTEREST ([R2]) | - |
| 5 | MMLU-Pro L1 +2.220 (0.210), L2 +1.265 (0.203) SUPPORTED; L3t DEGENERATE; L3k\|C +0.042 (0.050) INCONCLUSIVE, MDE80 0.190 (L191-223) | CONFIRMED | OT L52-L55 | - |
| 6 | Depth MATH L3, MMLU-Pro L2; "three levels / two levels" (L38-40, L197) | CONFIRMED | OT L48, L80; [R4] L3t/L3k siblings | - |
| 7 | "Every shuffled-label q95 at most 0.005" (L201) | PARTLY | max q95 = +0.0051 (MATH L2\|L1, OT L10) (L1) | LOW |
| 8 | Descriptive L2\|C1 +0.350 (0.064); L3k0-L2 +0.492 (0.086); 22-model L3t +0.176 (0.034) SUPPORTED secondary (L206, L211, L215) | CONFIRMED | OT L28, L27, L19; reading licensed by [R9] (z 5.4) | - |
| 9 | 9 of 10 P held; P4 MATH 0.058 > 0.056; P6 secondary miss scored by reviewer; no falsifier (L51, L227-230) | CONFIRMED | OT L85-L99; PR2 F2; [R16] P6 ranges all contain the g's | - |
| 10 | Synthetic gate z 6.16/7.12/5.51/6.48, slope INCONCLUSIVE/HELD, L3t DEGENERATE; fixtures 1500/16/6x4, leaves random (L161-170) | CONFIRMED | gate.txt L1-L11; reg S11 [R17] | - |
| 11 | Verdict rules, FWER 1.35%, R = 200, 0.10 (L147-157) | CONFIRMED | reg S5 [R2], [R5], S4.1 | - |
| 12 | Leak power ~+0.03 / ~+0.08 WORK (L186) | CONFIRMED | RR18 row 10: shifts +0.0294 / +0.0811 from eps 0 to the first failing eps .1 | - |
| 13 | Split 2,949 / 7,197; dropped 5/1,965, 143/4,797 at cos >= 0.98 (L138-140) | CONFIRMED | reg S3, S7.2; 1965-5 = 1960, 4797-143 = 4654 | - |
| 14 | 35 / 91 finer cells (L124, L247) | CONFIRMED | profile CSVs: 44 = 2+7+35, 107 = 2+14+91 cells | - |
| 15 | "read it once on items it had never been fitted on" (L37) | REFUTED by the post's own L42, L339 | two runs opened the vault (v1 harness, v2 read) + two reviewer reads (M3) | MEDIUM |
| 16 | Section heading "What does not add, honestly" (L255) | REFUTED vs F1/F3/[R3] | lists a detected gain (MATH leaves), a DEGENERATE (confirms nothing) and an INCONCLUSIVE (undecided) under "does not add" (M2) | MEDIUM |
| 17 | Figures: values, words, labels, pin, selftest | CONFIRMED, except clipping | `--selftest` SELFTEST OK; pin matched; all six viewed; meter_profile_mmlu_pro_finer.png footer cut at the right edge (M4) | MEDIUM |
| 18 | Snippet runs (L302-321) | CONFIRMED on a fixture, except the gated adapter | every line after `from_open_llm_leaderboard`, verbatim, on a 240-item 2-model `from_csv` stand-in, HF offline: metric_table, fit (slope default True), predict_proba(heldout=True) -> Series(240) in [0.43, 0.79], profile -> empty certified table, plot_sunburst -> plotly Figure. Adapter not run (gated) | - |
| 19 | README facts (69 EEE, 23 OLL 2024-06..2025-03, 41/69 >= 0.975, QwQ 0.120 vs 0.10, slope off bit-identical, meter opt-in) | CONFIRMED (spot) | README L48-L72, L241-L244; atlas.py L52 | - |

## Defects (ranked) and exact fixes

- **M1 MEDIUM, L99-L101 (overclaim).** "The null is larger on a smaller roster" is contradicted by the primary pair:
  MMLU-Pro (23 models) q95 +0.234 < MATH (69 models) +0.547. Replace with: "Within MATH, the null is larger on the
  22 models below the ceiling (a secondary line): its 95th percentile is +1.937, against a slope gain of +12.242. That
  subset is chosen by accuracy, and across benchmarks the null does not simply grow as the roster shrinks (MMLU-Pro,
  23 models: +0.234), so this is not a roster-size experiment." Same in make_meter_figures.py docstring ("the null
  q95 grows as the roster shrinks"); the PNG footer itself is fine.
- **M2 MEDIUM, L255 (F1/F3/[R3]).** Rename "What does not add, honestly" to "What the meter did not support, or could
  not decide". Keep the bullets as written (they carry the right words).
- **M3 MEDIUM, L37 (contradicted by L42/L339).** Replace "and read it once on items it had never been fitted on" with
  "and computed its registered statistics once, on items it had never been fitted on".
- **M4 MEDIUM, meter_profile_mmlu_pro_finer.png.** The footer is clipped at the right edge ("declared order;",
  "smallest and", "not registere..."): the pair-rule disclosure (v5 M3) is unreadable. The readability gate checks
  font size only. Fix: wrap the footer to the figure width (or `bbox_inches="tight"`), and add a selftest assert that
  every text artist's window extent lies inside the figure bbox; add that mutant to MUTANTS; re-render.
- **L1 L201:** "at most 0.005" -> "at most 0.0051".
- **L2 L50 (TL;DR), L34 (Fig 1 caption) (RR18 E3):** "beat a no-slope null" -> "beat a within-category no-slope Rasch null".
- **L3 L2 title, L31/L107 alt text (CONTEXT rule 12; reg S7.5):** "held-out meter" / "held-out gain" name the vault
  unqualified. The author's own D-2026-10-11-9 says "held-out granularity meter", so the title is A1: suggest
  "A meter read on reserved items"; alt text "gain on the reserved items".
- **L4 L353:** "had it reviewed before any data" -> "had it reviewed before the reserved items were read again"
  (READY_BZ-METER-R18 used WORK runs).
- **L5 L252-253 (v5 M3):** add "chosen after the first run" to the pair-rule sentence; drop "where intervals are
  informative" (unsourced) or replace with "away from the ceiling".
- **L6 L145:** "clustered by item" -> "clustered by item, near-duplicate reserved items sharing a cluster (MMLU-Pro
  4,625 clusters for 4,654 items)" (reg S3 [R10]; OT L52).
- **L7 Fig 1 vs reg S5 figure spec:** the slope sits as a rung of the level ladder; the spec puts it in a separate
  panel ("a measurement fix, not a granularity level") and adds hollow "over L1" bars and a 22-model inset. Minimum fix
  (caption): "The slope rung is a measurement fix, not a level of detail; the layout is the post's rendering of the
  registered values (the run's own figure is meter_v2/meter_figure.png)."
- **L8 L247-248:** the finer profiles are cited by repo path, which will not resolve on HF; embed them (or link the
  /blog/assets path). MATH finer figure: subject labels overprint whiskers (cosmetic).
- **L9 (outside the article; registrar):** README L241-L244 still says the meter "has not been read on its held-out
  vault yet", and the post sends readers to the README. BZ-METER also still has no ledger row
  (`grep -c BZ-METER docs/test_ledger.html` = 0).

No finding: leakage of WORK numbers into prose (none; the only WORK numbers are the labelled +0.03/+0.08 and 1/30);
[R17] wording (L103-105, Fig 2 caption, PNG notes); no region/skill/pocket sentence (the C-1 table's k-means cells were
accepted by v5 row 16).

## Author decisions (carried, none new)
A1 title (see L3); Fig 2 panel (a) keep/drop (v5 M5; its legend prints WORK v values, labelled); pair rule accept or
replace (v5 M3); placeholders [A4] install, thumbnail, HF username.

## Commands (read-only; scratch in the session scratchpad)
```
sha256sum E:/benchzoom_demo/meter_v2/outcome.json (7bca5558...bc47); cd meter_v2; sha256sum -c SHA256SUMS | grep -c ': OK$' (11 of 11)
sha256sum E:/benchzoom_demo/meter_v1/outcome.json (af1f8042...); cat -n outcome.txt calibration_synthetic/gate.txt
benchzoom: git log --oneline -1 master (9a42c49); git status --short | wc -l (0 before, 0 after); git hash-object docs/meter_registration.md (5c457088)
sed -n 82,293p; 485,505p; 506,640p; 668,680p docs/meter_registration.md (S1-S5, S6 [R18], S7-S9, S11 [R17])
python: every decimal in article L29-L260 (comments stripped) vs outcome.txt+gate.txt (exact or rounding) -> only 1.35, 5.2 not literal
python: 4.934/0.341; 8.927/0.477; 4.934/0.547; 8.927/0.234; 0.0577/0.0111; 0.0577+2*0.0111; profile CSV cell counts 44 / 107
git hash-object make_meter_figures.py (f0e7d296); sha256sum (24f29321...); python make_meter_figures.py --selftest (SELFTEST OK); figures sha256 6/6 unchanged after
Read figures/meter_{ladder,slope,profile_math,profile_math_finer,profile_mmlu_pro_finer}.png (clipping in mmlu_pro_finer footer)
snip_v7.py: fixture.csv (240 items, the snippet's 2 model names) -> article snippet verbatim with from_csv in place of the adapter; HF_HUB_OFFLINE=1 -> SNIPPET OK
grep -c BZ-METER docs/test_ledger.html (0); grep results JSONs ADAPTIVE-PROFILE/UNION-AF-ROUTE/TREE-CUT-GRANULARITY for every cited number (all present; 11,841 in prog L25432)
README L44-L75, L236-L246; author_decisions 2026-10-12.md L5-L11, 2026-10-09.md L58-L62
```
