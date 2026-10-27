# READY review: G-peaks v2 closure note (benchzoom 779811d), pre-data

Reviewer: adversarial reviewer, 2026-10-11. Zero LLM calls; synthetic data only; benchzoom read-only (nothing modified).
Object: `docs/peaks_v2_closure.md` (779811d), against rule `docs/peaks_tune_rule.md` (28e62b9 + [T1] at 186045d),
bench `examples/peaks_tune.py` (186045d), outputs `E:/benchzoom_demo/peaks_tune/`. Authority D-2026-10-11-7.

## Verdict: CHANGES (wording only; the outcome of record stands)

The outcome **NO DETECTOR MEETS THE TARGET (0/40 eligible)** is CONFIRMED: from the bench's own work units to the digit,
and again on the reviewer's own seeds (all 40 candidates, 0/60 at the deciding 5% plant). No v2 registration exists, and
none may be written from this bench. The closure note needs edits E1-E4 before it can be quoted. E5 and E6 are
conditions on any future bench version (option a).

## Per-claim table (deciding claims)

| # | Claim | Reviewer's number | Status | Sev |
|---|---|---|---|---|
| 1 | Rule committed before any comparison | 28e62b9 12:56:44. leaf_stats.json 13:00:06 (stats only). Bench commit 186045d 13:36:51. meta.json 13:36:59. PILOT 13:37:13. Full table 13:41:56. [T1] diff 28e62b9..186045d has 0 deleted lines (insertion only). Rule blob in meta = HEAD LF blob eea8af2a; bench blob ac88e016 = HEAD; peaks a062f093 = HEAD | CONFIRMED | - |
| 2 | 0 of 40 eligible; outcome NO DETECTOR | Recount of 450 p0 work units: no candidate reaches the 48/60 recovery bar, so the outcome holds whatever the null bars or ranking code do. summary.decision: ranked [], selected None, outcome matches | CONFIRMED | - |
| 3 | 5% realistic plant: 38/40 at 0/60, best 2/60 (two H-leaf) | 38/40 at 0; best 2 = H(d30,0.015,5,leaf)/S0 and H(d30,0.025,5,leaf)/S0 | CONFIRMED (digit) | - |
| 4 | 3%: 0/60 everywhere; 10%: at most 5/60; t0.45 best 13/30; v1 plant H-leaf 28/30, K d10 17/30 | 0 / 5 / 13 / 28 / 17 | CONFIRMED (digit) | - |
| 5 | Own seeds (points 77770001, detector 77770002; 30 leaves x 2 draws, all 40 candidates) | 5%: 0/60 for all 40 (bench: max 2). 3%: max 1/60. 10%: max 3/60. t0.45: max 16/30 (H 0.015,5,leaf/S0). K(d10,0.1)/S50: 0/0/0 on G/E/C. H-leaf S0 C-null 21-45/60 | CONFIRMED (replicates) | - |
| 6 | Wilson upper of 0/60 = 0.060 | 3.8415/63.84 = 0.0602 | CONFIRMED | - |
| 7 | "no real data was read for tuning" | False as worded. Real embeddings entered as summary statistics (leaf_stats.json from v1 prep pickles; src-subset ratios, rule §1) | REFUTED (wording) | MEDIUM |
| 8 | Reading / option (c): "not detectable at realistic tightness" | A known-centre likelihood-ratio oracle recovers 60/60 at 3%, 5% and 10% and 30/30 at t0.45 (median max Jaccard 1.000; the Bayes rule at prior f also gets 60/60). The plant is identifiable from the data; what failed is the detector family. A reviewer descriptive (sample-PCA-50 whitened HDBSCAN leaf, NOT a candidate) also recovers 0/30, but the plant's 10-NN purity is 0.42 against a 0.05 base rate | PARTLY (overreach) | MEDIUM |
| 9 | "HDBSCAN eom fires 18-100%; leaf 45-77% on the clump null" | eom worst null per candidate: S0 0.50-1.00, S50 0.117-0.55 (H(0.015,5,eom)/S50 7/60). Leaf C-null: S0 24-46/60 (0.40-0.77), S50 5-33/60 (0.083-0.55) | PARTLY (overbroad) | LOW |
| 10 | Pinned library untouched; graph unchanged | `git diff 9e3937f 779811d --name-only` = 6 files (whole list), none under src/. meta lib blobs pinned | CONFIRMED | - |
| 11 | Tests | venv: test_peaks + test_peaks_tune 74 passed (43 + 31) | CONFIRMED | - |
| 12 | Leakage | No detector ran on real points. No score or response was read. Real data entered only as eigenvalues, d1/d10, families, (s, w) and src-subset geometry (see E6) | CONFIRMED with E6 | LOW |
| 13 | Verdict ordering (rule §5 step 5) | 0 eligible means step 3 "no detector meets the target"; fresh and power are None (summary keys). No second candidate was promoted | CONFIRMED | - |

Power and Support (check 8): no deciding inference is drawn, so there is no DEFF. The bench cell n is 60 draws on 30 leaves,
2 per leaf, so it is clustered by leaf. That does not matter here: the outcome is 0-2/60 against a 48/60 bar, and the gap
is far beyond any clustering correction (even n_eff = 30 leaves gives 0/30 with a Wilson upper of 0.114).

Own mutants: none were run. Every deciding path ends at "no candidate reaches 48/60 recovery". That result is
recomputed from raw units and replicated on fresh seeds, so a mutant of the eligibility, ranking or confirmation code
cannot change the outcome. The builder's 29/29 bench mutants and 5/5 C5 mutants are taken as reported (not re-run).

## Defects and exact edits (benchzoom `docs/peaks_v2_closure.md`; insertion bracket or in-place, author's choice)

- **E1 (MEDIUM, claim 7).** Replace "Zero LLM calls; no real data was read for tuning." with: "Zero LLM calls. No detector
  ran on real points. Real leaves entered only as summary statistics (`leaf_stats.json`, sha256 f6f5eea0...: n, top-50
  eigenvalues, d1/d10, template families, clump (s, w)) and the plant was anchored on MMLU-Pro `src`-subset variance
  ratios and offsets (rule §1)."
- **E2 (MEDIUM, claim 8).** Add to "What this does NOT show": "That the realistic plant is undetectable in principle. A
  known-centre likelihood-ratio oracle recovers it in 60/60 draws at 3/5/10% (reviewer, READY_G-PEAKS-V2-CLOSURE). The
  failure belongs to the 40 tuned configurations, not to the information in the points." Reword option (c) to: "close
  G-peaks as 'not detected by the tuned density detectors at realistic tightness'."
- **E3 (LOW, claim 9).** Replace the last Numbers bullet's tail with: "HDBSCAN eom fires 50-100% (S0) / 12-55% (S50) under
  its worst null. HDBSCAN leaf fires 40-77% (S0) / 8-55% (S50) on the clump null. No null-clean candidate (19 at <= 6/60
  under every null) recovers any 5% plant."
- **E4 (LOW).** Disclose the pilot. Add: "A `--pilot` run (`tune_table_PILOT.txt`, 13:37:13, 8 draws per cell) preceded
  the full run (13:41:56). It used the same pinned rule and bench blobs, and nothing changed between the two runs." Also regenerate
  `SHA256SUMS` with `sha256sum` (the hand-written file lists leaf_stats.json twice).
- **E5 (condition on option a).** A new bench must commit its rule before any comparison, as 28e62b9 did. It must name
  every family added after this review's descriptive (whitened coordinates, anisotropic or sub-space plants) as post hoc.
  It must also keep the 60/60 known-centre oracle as a printed ceiling column, so that "undetectable" and "undetected"
  stay separate.
- **E6 (condition on any v2 registration).** The bench was tuned on the eigen and clump statistics of the same 30 leaves,
  and on `src`-subset geometry. If v2 later scores src-matched pockets (D-2026-10-11-6 naming) on these leaves, it must
  disclose that the plant was anchored on the labels it then reads.

## Commands (reviewer; read-only; scripts in session scratchpad)

```
git -C benchzoom log --format='%h %ci %s' -5; git diff 28e62b9 186045d -- docs/peaks_tune_rule.md | grep -c '^-[^-]'   # 0
git hash-object docs/peaks_tune_rule.md examples/peaks_tune.py src/benchzoom/peaks.py   # = meta.json identity
ls -la --time-style=full-iso E:/benchzoom_demo/peaks_tune/ ; sha256sum tune_table.txt tune_summary.json leaf_stats.json
recount.py  : unpickle 450 p0 units -> per-candidate recovery/FP counts; compare to tune_table.txt and summary.decision
ownseed.py  : T.point_set / own plant with seeds [77770001,...], T.detect_all key [77770002,...], all 40 candidates,
              kinds 0-6; oracle score log N(x;c,t ev) - log N(x;0,ev), max Jaccard over top-k and Bayes rule at prior f
whiten.py   : descriptive only, HDBSCAN leaf on sample-PCA-50 standardized scores, 1 draw/leaf; 10-NN plant purity
.venv/Scripts/python.exe -m pytest -q tests/test_peaks_tune.py tests/test_peaks.py   # 74 passed
git diff 9e3937f 779811d --name-only   # 6 files, none in src/
```
