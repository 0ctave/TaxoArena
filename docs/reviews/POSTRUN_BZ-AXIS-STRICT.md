# POSTRUN review: BZ strict axis gate (benchzoom 5ad3885 bracket, d92e406 code, 8f59e5c calibration)

Reviewer: adversarial-reviewer, 2026-10-15. Authority: author_decisions/2026-10-14.md D-2026-10-14-1/-2, 2026-10-13.md
D-1..4. Read only. Zero LLM calls. No write to E:/benchzoom_cache/strictcal (sites.jsonl sha256 5a6d5248... before and
after) or to the benchzoom tree (`git status --short | wc -l` = 0 after every step). E:/benchzoom_demo/axis_v1 intact
(`sha256sum -c SHA256SUMS.txt | grep -vc ': OK$'` = 0). axis_v2 does not exist.

## Verdict

- **Build: MERGEABLE (opt-in), as committed.** The default `split_rule="gap"` and the kappa-3 path are bit-identical,
  the full suite is green (617 passed, 0 failed, my run), M1 is fixed, and the execution graph is accurate.
- **Calibration: STOP CONFIRMED, mechanically and without ambiguity.** I recomputed every C1/C2/C3 cell from the cache
  with my own decision code, and the result matches the record to the digit at all 5 q. C1 fails at every q, so the
  selection has only one reading.
- **Is this a credible granular map for D-2026-10-13-1? NO.** No strict map exists, by design, because of the STOP.
  Beyond that, the calibration itself shows two substantive defects of the combined rule that a new q or a looser bar
  would not fix (H1, H2 below). The K3 maps (axis_v1) remain a size-floor bisection (prior review, H1).

## Per-claim table (deciding claims)

| # | claim | my number | status | sev |
|---|---|---|---|---|
| 1 | bracket committed before code and runs | 5ad3885 16:33; first code edit scratch 16:45; calibration launch 16:53 (meta.json mtime); code commit 18:31; bracket edits insertion-only (`git diff 5ad3885 8f59e5c -- docs/identifiable_splits.md \| grep -c '^-[^-]'` = 0) | CONFIRMED | - |
| 2 | records computed by the committed script / library | 853/853 records carry blob f21a478 = `git hash-object examples/strict_calibration.py` (LF; working tree is LF, autocrlf true, no CRLF rendering differs); `meta_now()` at HEAD == meta.json (all lib fingerprints + compute pin) | CONFIRMED | - |
| 3 | 850/850 sets, C0 3/3 bit-identical, one cut per C3 set | 850 plan keys + 3 `C0\|N2\|320\|s` keys; C0 records == main k=0 builds (3/3); cut_fp identical across 5 seeds 180/180 | CONFIRMED | - |
| 4 | C1 worst N2 n=320: 0.24/0.15/0.11/0.07/0.06 | 24/15/11/7/6 of 100; all other cells to the digit (incl. N3 640 2/30 at q=1.00) | CONFIRMED | - |
| 5 | C2 1.000 everywhere | 100/100, 60/60, 30/30 x3 at every q (truth_ari >= 0.8 and split) | CONFIRMED (non-discriminating, M2) | - |
| 6 | C3 N2 640 26/30 at q<=0.95, >=29/30 at 0.98/1.00 | 26/30 at 0.90 and 0.95; 27/30 at 0.80; 29/30 at 0.98 and 1.00; N2 320 27/30 at 0.80, then 29/30 | CONFIRMED | - |
| 7 | selection = STOP | C1 FAIL at each q; selection rule has one reading | CONFIRMED | - |
| 8 | leaf reasons correct | my first-failing-step tally equals the surface table (e.g. N2 320 q=0.80 tie 76 / split 24; P2 320 unstable 5) | CONFIRMED | - |
| 9 | fixture spectrum matches real nodes | own recompute from the K3 pickles (132 nodes): slope k2-20 0.63, k2-50 0.75, top-10 0.34, rbar 0.60, lambda1/lambda2 median 1.34 (p10 1.12, p90 1.72); fixture B n=300: 0.62/0.75/0.31/0.60, l12 1.12 | CONFIRMED on summary stats; lead ratio NOT matched by B (disclosed) | LOW |
| 10 | own-seed recompute: tie nulls and re-cuts | 8/8 sites re-read with the record's seed are bit-identical; with my seed (s+777777) the cut is identical 8/8, re-cut counts differ by at most 1, and 3 of 4 q=1.00 false splits FLIP to "tie" at q=1.00 (all 4 still split at 0.95) | CONFIRMED (repro); see H3 | MEDIUM |
| 11 | default + kappa-3 bit-identical | golden test in my suite run; inertness records k3 math 66/66, mmlu_pro 147/147 (frame equality), depth-1 tie null + AR_v 7/7 and 14/14 equal | CONFIRMED (records read, not re-run) | - |
| 12 | M1 fixed, suite green | 617 passed, 4 deselected (slow), 0 failed, 729 s | CONFIRMED | - |
| 13 | execution graph accurate | step-table spans gates.py 587-609, 613, 614, 617-625, 628-630, 633-643, 646-663, 666-672, 675-707, 710-779 and tree.py 23-32 all match the code; strict section matches the code paths | CONFIRMED | - |
| 14 | false-split control (the re-cut halves false splits; T1/T3 basis) | the re-cut passes **100% of tie-beaten no-structure nodes**: N2/N3/B/E1.4, every cell, every q, "unstable" = 0; the only "unstable" leaves are P2 (true structure) 5/30 + 1/30 | REFUTED (the conjunction is vacuous on the false-split path) | HIGH |

## Defects / findings

- **H1 (HIGH, the false-split control is vacuous).** Across all no-structure fixtures, tie-beaten nodes pass the 90%
  re-cut every time (e.g. N2 320: 24/24 at q=0.80, 6/6 at q=1.00; B 320 29/29; E1.4 320 47/47). The two conjuncts are
  strongly dependent: a sample axis that beats the tie null is, on the same rows, also re-cut-stable. So the rule
  "tie null AND 90% rebuilds" behaves exactly like the tie null alone on false splits, and the re-cut only costs power
  on true weak structure (P2). T1's "cut by roughly half by the re-cut" was wrong for this reason, not because of
  noise. Fix: any new registration must drop the claim that the re-cut controls false splits. A stability check can
  only add protection if it uses rows the cut never saw (fresh or split-half data: cut on half A, test on half B).
- **H2 (HIGH, the gate thresholds the sample lead ratio and cannot tell a tied population apart in the band where
  most real nodes lie).** The decision tracks the sample lambda1/lambda2 (lam12). In the band [1.25, 1.45), at
  q=1.00, tied N2 splits 4/6, matched bulk B 12/22, E1.4 39/55. In [1.15, 1.25): N2 6/50, B 3/30, E1.4 4/13. Below
  1.15 nothing splits at q=1.00. Every one of the 12 q=1.00 false splits has lam12 between 1.17 and 1.39. Of the 132
  real K3 nodes, 74 lie in [1.15, 1.45) and 19 below 1.15. On the same rows, the rule cannot separate "a unique axis in
  the population" from "a tie with a sampling gap" there. Caveat: the N2 count in the top band is small (6). The tie
  null is also anti-conservative on its own hypothesis: the node beats all 50 draws in 14/230 N2 sets, against 1/51
  under exchangeability (binomial p = 0.0002). Option (b), tightening the tie null, does not remove this. The gap is
  a plug-in bias: setting s[0] := s[1] on the sample spectrum erases the node's own sampling gap. Fix: either a null
  that reproduces the sampling distribution of lam12 under a tied population (a parametric bootstrap from the tied
  population, re-estimating s[0] := s[1] inside each draw), or an honest split-half protocol.
- **H3 (MEDIUM, seed dependence at q=1.00).** 3 of the 4 re-read q=1.00 false splits flip to "tie" under another
  build seed. The max of 50 draws is a noisy threshold. C3 still passes (29/30) only because most N2 sets are robust
  leaves. Fix: report decision agreement across seeds for the tie-beaten subset, not for all sets.
- **M1 (MEDIUM, C1 has no operating characteristic; the registration has no Support section).** With per-cell point
  bars on 100/100/30/60/30 sets, a rule whose true false-split rate is 0.03 in every cell passes C1 with probability
  0.45 (0.02: 0.73, 0.04: 0.21). At q=1.00 the pooled C1 is 12/320 = 0.0375 (CP95 0.020-0.065). So the STOP at
  q=1.00 is consistent with a true rate below 0.05, while q <= 0.98 is not (pooled 20/320 = 0.0625 at 0.98). This does
  NOT change the verdict: the registered rule binds. Fix: a new registration states the OC curve and a pooled or
  CP-based C1. Note that H1/H2 make the distinction moot for "credible map".
- **M2 (MEDIUM, C2 is non-discriminating).** The planted shift of 3-4 sqrt(lambda1) along a random direction gives
  AR ~0.95 and ARI 1.000 in every cell at every q. C2 never constrained q and says nothing about power at real effect
  sizes (P2 recovery is 0.833 at n=320). Fix: bind C2 at delta 2 / 2.5.
- **M3 (MEDIUM, test gap on the null's defining line).** Own mutant R1 (`s[0] = s[1]` removed in `tie_null_axis`)
  SURVIVES all 85 tests that reference the tie null (tests/test_axis.py, test_axis_map.py, test_identifiable_map_m3.py,
  test_strict_gate.py). The calibration's AST pin would refuse it, but library use is unguarded. Fix: a known-answer
  test (a 2-row-rank fixture whose tie draws are isotropic in the top-2 plane, or a pinned draw-median golden).
- **L1 (LOW).** The inertness JSONs pin `im.script_sha()`, which is identifiable_map.py (d45d416 = its LF blob), not
  strict_inertness.py (6f6421a). strict_inertness.py mtime 17:30 is before the runs, so this is plausible but
  unpinned. Fix: pin the script's own blob.
- **L2 (LOW, hand-back framing).** The RENDER hand-back says "the 90% rebuild bar named in D-2026-10-14-2 corresponds
  to q = 0.90". It does not: the 90% is the re-cut subsample fraction and m/K = 9/10, both fixed. q is the tie
  quantile. The committed records do not repeat the error. Fix: correct it in the brief to the author.
- **L3 (LOW).** docs/execution_graph.md does not record the STOP outcome. This is accurate as an algorithm description
  ("no default q until selected").

## Own mutants (deciding paths; sandbox copies only)

| id | change | result | decisive |
|---|---|---|---|
| R1 | gates.tie_null_axis: `s[0] = s[1]` -> `s[0] = s[0]` | SURVIVED (85 passed) | yes (M3) |
| R2 | strict_decision: `td != "split"` -> `td == "leaf"` (straddle counted as beaten) | killed | yes |
| R3 | recut_match: min over children -> child 0 only | killed | yes |

## Which nodes still look arbitrary (K3 seed-0 ids; for post 1)

- Sample lam12 < 1.15, so no unique leading direction even in the sample (19). MATH: 30, 14, 23, 27, 12, 4 (the
  Intermediate Algebra subject, n=879; its depth-1 strict read is leaf "tie"), 13. MMLU-Pro: 96, 63, 49, 84, 28, 22,
  64, 16, 69, 103, 70, 43.
- Sample lam12 in [1.15, 1.45) (74 nodes): accepted at fixture-like rates whether or not the population has a lead
  (H2). These splits are reproducible on their rows, but they cannot be called identifiable.
- MATH depth-1 node 5: re-cut 8/10, so "unstable" under the strict gate (inertness record, q=0.95 thresholds,
  descriptive).

## Must be fixed before post 1

1. Do not present any map as "identifiable/reproducible splits" beyond what D-2026-10-13-1 literally licenses. The
   K3 map's splits are reproducible regions of a continuum along a sample axis. Splits with lam12 < 1.45 are
   arbitrary in the sense of H2.
2. Author decision on the STOP. Options (a) a looser C1 bar or (b) more draws do not address H1/H2. A credible
   strict rule needs a split-half or fresh-row stability check, or a null that re-samples the tied population
   (H2 fix), registered with an OC curve (M1) and a binding C2 at real effect sizes (M2).
3. Add the R1 known-answer test (M3) before any further real build.

## Commands (compact)

```
# recompute (own decision code; read only):   scratchpad/strictrev/recompute.py  -> all cells to the digit, C0 3/3
# exchangeability + recut|tie-beaten:          scratchpad/strictrev/ranks.py, reasons.py
# lam12 bands vs real nodes:                   scratchpad/strictrev/zone.py (real lam12 from strict/spectra.json; medians re-derived by spec.py)
# spectrum match (own, from K3 pickles):       scratchpad/strictrev/spec.py
# own-seed re-reads (8 sites x 2 seeds, venv): scratchpad/strictrev/ownseed.py, cmpown.py -> REPRO 8/8 True
# meta pins at HEAD:   PYTHONPATH=src:examples .venv/Scripts/python.exe -c "...sc.meta_now()==meta.json" -> True
# blob:                git hash-object examples/strict_calibration.py -> f21a4780... (= 853/853 records)
# suite:               PYTHONPATH=src .venv/Scripts/python.exe -m pytest -q  -> 617 passed, 4 deselected
# mutants:             scratchpad/strictrev/mut.sh (copies under scratchpad/strictrev/mut/)
# C1 OC:               scipy binom over cells [100,100,30,60,30], bar floor(0.05 n): p=.03 -> 0.452
```
scratchpad = C:/Users/octav/AppData/Local/Temp/claude/Z--FAC-TUBerlin-THESIS-TaxoArena/7c10e5cb-d16b-4a0e-864a-f3a6151d835b/scratchpad
