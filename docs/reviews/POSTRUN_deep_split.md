# POSTRUN — DEEP-SPLIT-COMPARE (lane r2; zero calls)

Outcome of record: `experiment_results/archv2/rp12_r2/deep_split_compare_outcome.txt` (untracked; 273 lines, 33,959 B, LF, 0 CR;
sha256 75ded557518ad7b4f877f82efe32693707e2635276a1d3130adfcde7e0c9208f; blob:ae3156f9d672600e8acf980197024c3fa215d145; mtime
2026-10-02 03:31:26). Script: blob:31af4cea (outcome line 2 = main's `git hash-object`; merged as dab5a621). Registration: prog
L23125-L23314 plus brackets. Prior reviews: READY_deep_split_delta.md and READY_deep_split_full.md (C1-C4). Adversarial reviewer,
2026-10-02. Zero calls.

## Verdict: VALID, with two wording conditions (W1, W2) the registrar must carry

All six clauses, F-RULE and the consequence reproduce. I re-derived every deciding number to the digit in two ways: from the
outcome's own printed lines (the C1 hand checks) and with an independent read-only re-fit. Wording conditions:

- **W1 (HIGH): C-AB HELD is knife-edge on its spread conjunct, and A has no seed replication.** D_AB = +0.013357 against
  spread_B = 0.012543, a margin of +0.000814 (about 5 of 6,139 items). The registrar must write: "C-AB HELD at a margin of
  0.0008 over B's five-seed spread (0.0125); A is one construction, and its construction-seed variance is unmeasured and
  in no bar" (the orchestrator's Q2 ruling). This clause must never be read as seed-free.
- **W2 (HIGH; C2 applied): the consequence's attribution "label information below depth 2" is contradicted in substance by
  the registered descriptive bridge.** Quote C-DB HELD, D_DB +0.0349 [+0.0254, +0.0444], beside two numbers:
  - P(B-gt_0) - P(D_0) = +0.0028 [-0.0015, +0.0069] (outcome line 221). B-gt fits label-free k-means at k_a on
    class-defined fit sets and reproduces KC.
  - G13-BREAKDOWN's depth-2 D(2) = -0.0023 [-0.0108, +0.0064] (line 21). With one cell per anchor, the tree's frontier files
    like the class means.

  My own descriptive computation (not of record; same bootstrap) gives P(B-gt_0) - P(B_0) = +0.0376 [+0.0285, +0.0472]
  (MMLU +0.0541 [+0.0413, +0.0673]). So B-gt carries 108% of D_DB, and label ownership below depth 2 adds
  D - B-gt = -0.0028 [-0.0069, +0.0015]. The label information that buys filing lies in **which TRAIN items each anchor's
  cells are fit on**: the depth-2 fit-set membership, where F-tree is class-pure for 10,021 / 12,334 = 0.8125 of items. It
  does not lie in prototype ownership below depth 2.

  The registered criterion stands and the consequence prints as registered (C-7: B-gt is descriptive and is not promoted).
  The registrar's bracket should read: "C-DB HELD; the descriptive bridge B-gt places the edge in depth-2 fit-set membership,
  not label ownership below depth 2. SPLIT-VMF is not indicated (F-RULE fired; C-AB HELD). HYB-LC as drafted (label
  ownership) is not indicated by this result. The knob it points to is fit-set membership." The follow-up choice is the
  research lead's and the author's.

## Per-claim table

| # | Claim (outcome) | Result | Mine (independent re-fit / hand) | Sev |
|---|---|---|---|---|
| 1 | P_A 0.8119; P(B_s), P(C_s), P(D_s) lines | CONFIRMED | 0.811859; B 0.798501 / 0.790194 / 0.785959 / 0.788891 / 0.788402; C 0.800782 / 0.787913 / 0.794592 / 0.789379 / 0.792474; D 0.833360 / 0.839388 / 0.834012 / 0.844600 / 0.841342: all round to the printed digits | - |
| 2 | C1 hand checks from the printed P lines | CONFIRMED | D_AB 0.8119-0.7985 = +0.0134; D_AC 0.8119-0.8008 = +0.0111; D_DB 0.8334-0.7985 = +0.0349; spread_B 0.7985-0.7860 = 0.0125; spread_C 0.8008-0.7879 = 0.0129; spread_KC 0.8446-0.8334 = 0.0112: all = printed | - |
| 3 | D_AB +0.0134 [+0.0069, +0.0203]; C-AB HELD | CONFIRMED, W1 | +0.013357 [+0.006891, +0.020260]; > spread_B 0.012543 by 0.000814 | HIGH (wording) |
| 4 | D_AC +0.0111 [+0.0039, +0.0180]; C-AC UNDETERMINED | CONFIRMED | +0.011077 [+0.003899, +0.018037]; below spread_C 0.012869 by 0.001792 | - |
| 5 | D_DB +0.0349 [+0.0254, +0.0444]; bar 0.0125; C-DB HELD | CONFIRMED, W2 | +0.034859 [+0.025366, +0.044390]; bar max(0.012543, 0.011240) | HIGH (wording) |
| 6 | C-AB-M UNDETERMINED (seed-fragile); C-AC-M REVERSED (seed-fragile); C-DB-M HELD | CONFIRMED | MMLU: +0.005175 [-0.004881, +0.015199]; -0.010063 [-0.019015, -0.000574]; +0.049741 [+0.036452, +0.063401]. "Seed-fragile" correct: \|D_AC-M\| 0.0101 < C's MMLU spread 0.0201 | - |
| 7 | F-RULE FIRES; consequence = label-information sentence only | CONFIRMED | lower ends +0.0069 and +0.0039 both > -0.0108; C-AB and C-AC not REVERSED, so the split-rule sentence is correctly absent (C-AC-M is not a trigger) | - |
| 8 | Denominators and DEFF | CONFIRMED | n 6,139, 5,628 components, mean size 1.0908, Kish 1.3043 (= Support (a)); MMLU 3,478 / 3,386. Measured DEFF C-AB 1.071, C-AC 1.158, C-DB 1.223 (transported 1.341 / 1.341 / 1.214); MDE80 0.0097 / 0.0100 / 0.0139 printed beside each statistic. C-DB's MDE exceeds the registered 0.0111 because discordance is 0.125 vs 0.08 planned; D_DB still clears its effective bar 0.0139 | - |
| 9 | Predictions table | CONFIRMED | 23 bands re-scored by hand: 17 HELD, 6 FAILED (P(B_0) 0.7985 < 0.800; D_AB 0.0134 > 0.012; D_DB 0.0349 > 0.032; P(C-BIC_0)-P(C_0) -0.0192 < -0.015; P(C-32_0)-P(C_0) -0.0124 < -0.010; R3 k_a = 1 range 0.0609 > 0.005). Verdict-probability lines: C-AB HELD (prior 0.10), C-AC-M REVERSED (0.15), F-RULE FIRES (0.45) | - |
| 10 | Outcome = console; written once | CONFIRMED | console (275 lines) minus its 2 console-only lines (`[DSC] cost:`, `[DSC] wrote`) is `cmp`-identical to the whole outcome file (verdicts included); 1 file named `deep_split_compare_outcome*` under the repo (`find ... \| wc -l` = 1); write path `open(..., "x")`; no `--out` used | - |
| 11 | Preconditions | CONFIRMED | POOL rc 0 (pin 79d48f4b, -wal 0 B); I0-I5, I1, depth 2, I2, I3 and I4 PASSED; check_sides passed; 0 empty-named or dropped cells and 0 non-converged GMMs in the deciding arms; admitted PIDs = ollama (idle) plus the run's own python | - |

## Defects / carried conditions

- W1, W2: above; the registrar's wording.
- C1 (carried, HIGH for any future edit): the selftest does not separate B from C item-wise or C_0 from C_1. Not a validity
  defect here: rows 1-2 verify those exact quantities on the run.
- C3 / C4 (LOW): `--out` was not used; NOTE not triggered (only one consequence fired), so C4 is moot for this outcome.
- Descriptive, for the record: R3 "k_a = 1 within 0.005" FAILED at 0.0609. In unsplit anchors B and C use the F-tree mean
  where A uses the leaf vmfMu, and filing competes over all cells. C-BIC and C-32 fall below C (both FAILED bands).

## Commands

```
cmp <(tr -d '\r' < scratchpad/deep_split_run.log | grep -v '^\[DSC\] cost: \|^\[DSC\] wrote ') experiment_results/archv2/rp12_r2/deep_split_compare_outcome.txt   # IDENTICAL
find . -name "deep_split_compare_outcome*" | wc -l                                  # 1
sha256sum / git hash-object <outcome> ; git hash-object tools/analysis/deep_split_compare.py   # 75ded557... / ae3156f9 ; 31af4cea
python scratchpad/dsc/repro.py   # (main; read-only; no pool check; 1 python besides a peer selftest) GB.load_objects -> load_anchors ->
                                 # identity_arms -> fit_arms; own contrasts, spreads, G.boot intervals, MMLU stratum, B-gt bridge, Kish, F-tree purity; 66 s
```
