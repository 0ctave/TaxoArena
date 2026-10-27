# READY (full first review) — DEEP-SPLIT-COMPARE: tools/analysis/deep_split_compare.py

Reviewed blob: `blob:31af4ceaa35fadfaf0bd43acc2a237d85c8ca30e` (LF; worktree file has 0 CR bytes; sha256-lf16 4b1fbeb8f53874d4),
branch `deep-split` tip dc7a7674, not merged into main. Registration: prog L23125-L23314 with its brackets, plus the registrar's
record at L23424-L23429 (_as_of main 06268781). This review covers what READY_deep_split_delta.md (same blob) did not: the
analysis paths, M01-M43, the denominators, the intervals and DEFF, leakage and label information, and write-once. The pinned
readers (g13_breakdown c29fa1c3, g13_comparator 61d83ec7, rp12_pairing 35214b3f, and through them rp12_lane ac25b152 and
flat_mix_mmlu 555ae3ac) are taken as reviewed in READY_g13_breakdown.md / POSTRUN_g13_breakdown.md. Main holds the same five
blobs (`git hash-object`). Adversarial reviewer, 2026-10-02. Zero calls. No arm was fitted on real data: no pre-run peek.

## Verdict

**READY WITH CONDITIONS C1-C4.** None of them blocks the `--run`. Every deciding path matches the registration on inspection.
Two of my 8 mutants on deciding paths SURVIVED: D_DB taken against C_0, and C's comparator taken at seed 1. The code at those
lines is correct (L611-L612, L628), but the selftest cannot see the error. C1 is the gating substitute for them.

- **C1 (HIGH; post-run gate):** the post-run reviewer checks, to 4 digits from the outcome's own printed lines, that
  D_AB = P_A - P(B_0), D_AC = P_A - P(C_0), D_DB = P(D_0) - P(B_0), and that spread_B, spread_C and spread_KC equal max - min of
  the printed seed lines. Before any re-run or later edit of this script, add one fixture where B differs from C item-wise and
  C_1 differs from C_0, so Y5 and Y7 die.
- **C2 (MEDIUM; reading, no code change):** C-DB's sentence says "label information below depth 2". D (KC) differs from B in
  three ways: (i) depth-2 fit-set membership (class labels vs F-tree), (ii) k allocation (k_c vs k_a; both total 133), and
  (iii) label ownership. Only (iii) is "below depth 2". The registration names B-gt as the descriptive bridge. The registrar
  must quote C-DB beside (a) the point P(B-gt_0) - P(B_0) (derivable from the printed P lines; the script prints only
  P(B-gt_0) - P(D_0) with an interval) and (b) G13-BREAKDOWN's depth-2 D(2) -0.0023 [-0.0108, +0.0064], which bounds (i).
  This applies the anchored-tree lesson: A, B and C are like-for-like (same anchors, label-free below depth 2); D is not.
- **C3 (LOW):** run without `--out`. Write-once is per path (`open(..., "x")` and the exists check at L978). `--out` accepts any
  path inside lane r2, so a second outcome file under another name is possible.
- **C4 (LOW; registrar to confirm):** the L23242 bracket says both consequence sentences print when F-RULE fires and C-AB or
  C-AC is REVERSED, "the label-information sentence with its C-DB condition as written". The code prints the label sentence
  only when C-DB is HELD (L782) and the NOTE only when both sentences actually print (L793). The NOTE text omits "recorded
  joined". I read the code as conformant; the wording of record is the registrar's.
- Correction to READY_deep_split_delta.md C2: this script's outcome does not read `headless_run.log`. R5 prints the
  manifests' duration_ms only (L879-L882); the log reader is g13_breakdown's own and is not rendered here. Running from main
  changes only where the outcome lands.

## Per-claim table (deciding claims)

| # | Claim | Result | Evidence / number | Sev |
|---|---|---|---|---|
| 1 | Arms A, B, C, D as registered | CONFIRMED | A = bundle eval_fl (I1 0.8119); B = FM.spherical_kmeans (k-means++, seeded, max_iter 300) on F-tree(a) at k_a, normalised mean at the 20 k_a = 1 anchors (L386-L409); C = PCA d16 centred, unwhitened, then GaussianMixture(diag, k-means++, n_init 1, 200 iter, reg 1e-6, random_state s), hard argmax, 512-d normalised member means, empty components dropped and counted (L412-L480); D = identity_arms' KC_s | - |
| 2 | Filing and naming common to B and C: argmax cos over ALL cells; name = TRAIN majority of cosine-filed TRAIN items; an empty cell takes its anchor's class, counted | CONFIRMED | `name_and_file` L483-L496; EVAL enters only as `Xe` for filing; M04 (oracle), M05 (likelihood filing) and M06 (EVAL naming) KILLED | - |
| 3 | TRAIN-only fits; no EVAL or GATE in a fit | CONFIRMED | every fit indexes `o["Xt"]` through ftree / gt / banc; B-anc nearest anchor from `Xt @ amu` (L334); check_sides inside load_objects; M01 and M37 KILLED | - |
| 4 | Criteria C-AB / C-AC / C-DB (interval AND point beyond spread; C-DB bar max(spread_B, spread_KC)) | CONFIRMED | `v_spread` L261-L267, called at L669-L671; M09, M11 and M12 KILLED; own Y1 (>=) and Y3 (spread_C from B) KILLED | - |
| 5 | -M clauses: MMLU_PRO_LB, interval alone, "seed-fragile" when \|D\| < stratum spread (C-DB-M: max of B and KC) | CONFIRMED | L660-L675 and L757-L773; M13, M14 and M39 KILLED; own Y4 KILLED | - |
| 6 | F-RULE fires iff BOTH lower ends > -0.0108 | CONFIRMED | `f_rule` L279-L281 on R1 lo's; REG frule -0.0108 asserted; M15, M16 and M17 KILLED; own Y2 KILLED | - |
| 7 | Consequences and NOTE | CONFIRMED with C4 | L781-L794; M18 KILLED | LOW |
| 8 | Comparator of record s = 0; spreads over all 5 seeds | PARTLY | code correct (L627-L628); M07 and M19 KILLED; own **Y7 (C_1 as comparator) SURVIVED** and **Y5 (D_DB vs C_0) SURVIVED**: fixtures H / P give B = C item-wise | HIGH (C1) |
| 9 | Denominators = Support (a) | CONFIRMED | real dry-run (delta review): EVAL 6,139 / 5,628, MMLU 3,478 / 3,386, TRAIN 12,334, R3 strata equal; R3 refuses unless equal (`check_r3_support`) | - |
| 10 | Intervals: whole-component percentile bootstrap, B 2,000, seed 20260929; strata re-index their own components | CONFIRMED | GB.stat to G.boot (g13_comparator L204-L211); strata call `GB.stat(v, comp[m])`; M08 and M38 KILLED | - |
| 11 | Measured DEFF, n_eff and MDE printed beside each deciding statistic (check 8) | CONFIRMED | `support_line` L712-L716: DEFF = boot SE^2 / (var(diff)/n) (GB.stat L308-L311) beside the transported value; own Y8 (print transported) KILLED. Registered SE / MDE arithmetic re-derived in the delta review (to the digit) | - |
| 12 | Label-information table printed in the outcome header | CONFIRMED | LABEL_INFO L806-L816 = the registration's table (C-BIC row added: k by BIC) | - |
| 13 | Like-for-like (anchored-tree lesson) | PARTLY | A / B / C share the anchors and the F-tree (A's output; favours A, disclosed); D also differs at depth 2 membership and in k allocation, see C2 | MEDIUM (C2) |
| 14 | Predictions: every PRED band and probability line scored | CONFIRMED | 23 PRED keys = the registration's numeric predictions (D and A times are "seen", not predicted); `pred_line` NaN gives NOT SCORED (M41 KILLED) | - |
| 15 | Write-once | CONFIRMED with C3 | exists check before any fit (L978), `open(outp, "x")` (L1007), POOL line first in the file; M22 and M23 KILLED | LOW |
| 16 | M01-M43 really kill | CONFIRMED | `--mutants`: 48 of 48 KILLED, control survived; the harness requires each target exactly once (L1653); the registration's 8 required mutants are M01-M08 | - |
| 17 | Selftest | CONFIRMED | 10 / 10 passed | - |

Own mutants (8; full selftest, each from a clean exec of the blob with one edit):
- Y1 `v_spread` HELD at d >= bar: KILLED (boundaries).
- Y2 `f_rule` >=: KILLED (boundaries).
- Y3 spread_C from B's seeds: KILLED (summarize).
- Y4 C-DB-M stratum spread without KC: KILLED (summarize).
- **Y5 D_DB = D0 - C0: SURVIVED, decisive (C1).**
- Y6 C fit set = GT class: KILLED (e2e_H, P, S).
- **Y7 C comparator = C_1: SURVIVED, decisive (C1).**
- Y8 support prints the transported DEFF: KILLED (branches).
- Y0 control: SURVIVED.

## Defects

- D-1 (HIGH) = C1: no fixture separates B from C item-wise or C_0 from C_1. Fix: in fixture S, or a new one, give C a
  different partition from B on at least one item, and C_1 a different one from C_0; assert D_DB and D_AC by hand.
- D-2 (MEDIUM) = C2: the decomposition D_DB = (D - B-gt) + (B-gt - B) carries no interval for its second term. Fix (optional,
  next edit): add `P(B-gt_0) - P(B_0)` to `desc_diff`. Until then the registrar quotes the point from the printed P lines.
- D-3 (LOW) = C3: `--out` permits a second outcome path. Fix: refuse `--out` with `--run`, or run without it.
- D-4 (LOW) = C4: NOTE wording. Fix: the registrar's reading; optionally add "recorded joined".

## The --run (after the merge; rule 7 first: no construction or site null, no other pool reader)

```
git merge-base --is-ancestor dc7a7674 main && git hash-object tools/analysis/deep_split_compare.py    # must print 31af4cea...
cd Z:/FAC/TUBerlin/THESIS/TaxoArena && PYTHONIOENCODING=utf-8 TAXOARENA_DATA_ROOT='Z:\FAC\TUBerlin\THESIS\TaxoArena' \
  python tools/analysis/deep_split_compare.py --run --lane r2        # no --out; writes experiment_results/archv2/rp12_r2/deep_split_compare_outcome.txt (mode x)
```

## Commands

```
git hash-object .claude/worktrees/deep-split/tools/analysis/deep_split_compare.py        # 31af4cea (LF)
for f in g13_breakdown g13_comparator rp12_pairing rp12_lane flat_mix_mmlu v2_union_pool; do git hash-object tools/analysis/$f.py; done   # main = worktree
sed -n 23125,23314p docs/judge_v2_program.md                                               # registration read against L245-L918 of the script
python tools/analysis/deep_split_compare.py --selftest      # (worktree) 10 / 10
python tools/analysis/deep_split_compare.py --mutants       # (worktree) 48 of 48 KILLED; control survived
python <scratch>/dsc/own_mut_full.py                        # Y0 SURVIVED; Y1-Y4, Y6, Y8 KILLED; Y5, Y7 SURVIVED
grep -n "headless_run" tools/analysis/deep_split_compare.py # selftest fixture only (L1087, L1416, L1764); render reads man[...]["ms"]
```
