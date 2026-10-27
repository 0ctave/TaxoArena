# POSTRUN delta review: benchmark-zoom post figures v5 (benchzoom 435904b on 5c2063c; post dir uncommitted draft)

Reviewer: adversarial-reviewer, 2026-10-10. Delta on POSTRUN_BENCHZOOM-POST-FIGURES.md (b7ff8d85). Zero LLM calls, light CPU.
Read-only on every source; figures/ sha256 identical before and after my selftest run.

## Verdict: NOT FIGURES-READY (one MEDIUM, G1); FIGURES-READY once G1 is fixed. G2-G5 are LOW (text/comment edits).

F1-F8 of the prior review are all CLOSED in substance. The fix for F1 caused a new defect (G1): Figure 1, the hook,
now leaves 2 of Llama-3.3-70B's 13 certified subjects (history, philosophy) unnamed.

## Per-claim table (deciding claims)

| # | Claim | My check | Result | Sev |
|---|---|---|---|---|
| 1 | F1: every figure text >= 10 px at 720 px | (a) the gate formula, pt x 170/72 x 720/W on the saved PNG width: fig3 13.7, fig2 16.9, depth_support 13.0, signal 13.0, MATH sunburst 13.5, MMLU sunburst 13.1 (blog_v5 json `readability`; make_figures selftest prints 13.7 / 16.9). (b) Independent pixel check: ascender-to-descender band heights of text lines, measured in the PNGs and scaled to 720: captions 11.6 px (depth_support, signal), fig3 image line 11.0-13.9, fig2 footer 17.1, MMLU caption 12.3-13.0. That is consistent with a 13 px em (DejaVu glyph extent is about 0.9 em). (c) Visual read of all 6 images downscaled to 720 px: every label is legible | CONFIRMED | - |
| 2 | Gate not vacuous | text_artists covers titles, ax.texts, legends, axis labels and the in-view tick labels. Own mutants M1-M3 all killed (below) | CONFIRMED | - |
| 3 | fig3 numbers unchanged vs outcome.txt | sha256 fc715e4d... = pin. Every plotted value is found by grep in outcome.txt: 22 strings (6 Brier arms, 5 intervals x 3, +0.002925), each count >= 1. The 4 point gains are C minus the arm: 0.002910 / 0.001898 / 0.001802 / 0.003547, by my own subtraction. The values I read off the 720 px render match the prior review's rows 1-3 | CONFIRMED | - |
| 4 | Demo numbers unchanged (blog_v5 vs v4 summary.json) | blog_v5 json `demos`, `label` and `read` == blog_v4 (python equality). Own read of the v4 summary.json: MATH d1 483/47, d2 not_testable 414, d3/d4 0; MMLU d1 322/109, d2 276/3, d3 not_testable 2; 41 of 69 >= 0.975; QwQ-32B excluded. Chance: 40.955 [30, 52] and 31.17 [21.975, 43], 200 reps. The images show the same | CONFIRMED | - |
| 5 | figures/ = blog_v5 | `sha256sum -c` of blog_v5_SHA256SUMS: 5/5 OK; the 4 PNGs in figures/ have the same sums | CONFIRMED | - |
| 6 | F2: Figure 5 caption matches the image | caption: hatched MATH d2 414, MMLU d3 2 "not testable", deeper bars "not reached". Image (v5): the same labels. "0 / 414" occurs 0 times as caption text (grep) | CONFIRMED | - |
| 7 | F3/F4: fig3 says "EVAL side", panel (b) has its own row labels, all text left of zero | visual read, plus the selftest asserts it (lab1/lab2, x < 0, ha=right) | CONFIRMED | - |
| 8 | F5: "not reached" in the image | depth_support v5: MATH d3/d4 and MMLU d4 say "not reached" | CONFIRMED | - |
| 9 | Every referenced image exists | 6 unique `figures/<file>` refs in article.md, 6/6 exist (the 7th grep hit is the bare word "figures/" in a comment) | CONFIRMED | - |
| 10 | F6/F8: stale comments gone, placeholders filled | {{FIG_*}} placeholders: 0. The remaining {{...}} are the author's A3/A4 and {{N}}. The comments are stale again: see G3 | PARTLY | LOW |
| 11 | Captions match images (Fig 1, 3) | see G1, G2, G4 | PARTLY | MED/LOW |
| 12 | Regression | benchzoom pytest 294 passed / 4 deselected; selfcheck criteria 174a86ce OK, library blobs OK; make_figures --selftest OK; benchzoom tree clean (0 lines); 435904b touches 4 files, none of them application.yml / .env / .gitignore (grep -c = 0) | CONFIRMED | - |

## Defects and fixes

- **G1 (MEDIUM, Figure 1 hook: certified subjects unnamed).**
  - What happens: `declutter` keeps the innermost labels first, but it still hides depth-1 declared-subject labels that collide with each other. In sunbursts_MMLU-Pro.png, 11 of the 14 subjects are named. Two coloured (certified) wedges carry no name. From profiles.csv, Llama certified nodes 8 = history (d +0.33) and 12 = philosophy (d +0.25). computer science (node 4, not certified) is also unnamed.
  - Why it matters: the caption says "13 certified cells", and the reader can count 13 coloured wedges but can name only 11. The ring labels on the MATH sunburst are complete (7/7).
  - Fix: never hide a depth-1 label. Options: hide the colliding cluster labels instead; abbreviate ("history" and "philos." fit); or draw the colliding subject names outside the ring with a leader line. Then assert in test_blog_v5 that every depth-1 label is visible.
- **G2 (LOW, alt text stale).** article.md L61 alt text says "Two MMLU-Pro sunbursts side by side". The image is now stacked. Write "one above the other".
- **G3 (LOW, provenance comments stale; F6 recurrence).**
  - L66, L359, L365, L387, L517, L524 still say figures/ = blog_v4, and L524 says "sha256 E:/benchzoom_demo/blog_v4_SHA256SUMS.txt, 4/4 equal". That is false now: figures/ = blog_v5 (5/5 against blog_v5_SHA256SUMS).
  - L365 says "The v4 image still labels those bars 'not tested'". L39 and L193 still say "re-render owed".
  - Fix: point the comments at blog_v5 / 435904b and delete the owed-work clauses.
- **G4 (LOW, fig3 caption and alt text, panel (b)).** Both say "each other reader minus the strict read ... All four lie below zero". Panel (b) draws five rows. Its top row is X = benchmark level C at +0.000961, above zero. Fix: add "the top row repeats the deciding difference against the benchmark level (above zero)".
- **G5 (LOW, wording).** The ENG report says "every script now refuses to save a figure below 10 px". make_figures.save writes the .svg and .png first and refuses afterwards (L263-L268), so an undersized file stays on disk. blog_figures refuses before writing (L385-L389). Fix: check readability before savefig (use `saved_width`), or reword the claim.

## Own mutants (deciding path: the readability gate and declutter, examples/blog_figures.py, test_blog_v5.py)

- M1 `readability` min -> max: killed (3 failed). Decisive.
- M2 `declutter` never hides a label (`if False:`): killed (2 failed).
- M3 `MIN_PX = 10.0 -> 5.0`: killed (1 failed). Decisive.
- After each mutant: `git checkout --`. The tree is clean (0 lines).

## Pins (LF, `git hash-object`; the working tree equals HEAD)

- benchzoom examples/blog_figures.py: fc323348
- tests/test_blog_v5.py: 89cdcee1
- post dir make_figures.py: 44ff834f
- article.md: 4bb5af2f (reviewed rendering; the post dir is uncommitted)

## Commands

```
sha256sum -c blog_v5_SHA256SUMS.txt (in E:/benchzoom_demo/blog_v5) -> 5 OK; sha256sum figures/*.png -> same 4 sums
PIL: resize each figures/*.png to 720 px wide (scratchpad/v5/) -> visual read of all 6
scratchpad/bands.py <png> y0 y1 x0 x1 -> dark-row band heights scaled to 720 px (11.0-17.1 px on the caption lines)
grep -c <22 plotted values> experiment_results/archv2/adaptive_profile/outcome.txt -> each >= 1; sha256 fc715e4d
python: blog_v4 vs blog_v5 blog_figures.json demos/label/read == ; v4 summary.json read_by_depth, per_model, excluded
python: mmlu_pro_v4 profiles.csv (Llama certified nodes 1-3, 5-14) x tree.csv depth-1 labels -> 8 history, 12 philosophy
grep -o "figures/[A-Za-z0-9_.-]*" article.md | sort -u -> 6 files exist; grep -n "blog_v4\|side by side\|All four" article.md
make_figures.py --selftest -> SELFTEST OK 13.7 / 16.9 px; depth_calibration_v2.py --selfcheck -> 174a86ce OK
benchzoom .venv pytest -q -> 294 passed, 4 deselected; git status --short | wc -l -> 0
git show 435904b --name-only --format= | grep -c . -> 4; ... | grep -ci "application.yml\|\.env\|gitignore" -> 0
```
