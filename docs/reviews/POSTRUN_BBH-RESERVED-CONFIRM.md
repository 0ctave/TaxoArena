# POSTRUN review: BBH-RESERVED-CONFIRM, the one-time sealed read (registration 26edca97; open at F 54ed9bf)

Reviewer: adversarial-reviewer, 2026-11-10. Authority: D-2026-11-10-1 (4c45716e) on top of D-2026-11-07-1. Zero LLM calls.
The side is spent. The reviewer read the RESERVED responses, texts and vectors with its own code; no repository module was
imported. The reviewer did not re-run `open` or `freeze` and wrote nothing under E:/benchzoom_demo/followups/bbh-reserved-confirm:
the sha256 and `ls --full-iso` of that directory are equal before and after (`before_outdir.*`). Scratch:
E:/TaxoArena_tmp/postrun-bbh-reserved-confirm. Backup: E:/TaxoArena_backup_2026-11-10_postrun-bbh-reserved-confirm (13 files + SHA256SUMS,
13 / 13 OK; SHA256SUMS sha256 5d9f0113d22ba433...).

## Verdict

**OUTCOME CONFIRMED**, every deciding number reproduced to the digit. G4 not fired (it has no line: D1). T1 not fired.
**C1 HELD. C2 HELD. C3 UNDETERMINED.** F1 not fired. Predictions: 7 of 8 HELD (P5 FAILED); Brier 0.0704 at the registered
confidences (P5 0.68). There is no BLOCKER. Three LOW defects (D1-D3) and three wording conditions (W1-W3) apply to the record.
- The executed code was F, 54ed9bfff765b02dcbcd893fe51248122d66aca4. Its manifest has 31 files, sha256 de21fc92f33abceb22d63eb3d72062ea1d71836211b8aad8f14530c5e405cecc (= the READY pin).
  Changed blobs (git LF, 0 CR, no CRLF rendering in the working tree): examples/bbh-reserved-confirm.py blob:5e0dfca320132455a1bde8e05db9dd280cdc7c70 and
  tests/test_bbh_reserved_confirm.py blob:dedcabd6708b668da0c36aa240275d4c006711e5. F is local and not in master.
- The words are robust. Each word is the same under the registered stream, an independent stream, the percentile interval, the one-stage SE
  and a linearised cluster SE (row 13).

## Per-claim table (deciding claims)

| # | claim (run) | reviewer's number / evidence | state | sev |
|---|---|---|---|---|
| 1 | Executed code = F; the code check passed; modules after the check 0 | OPENED.json code.head = F. Its 31-blob manifest re-hashes to de21fc92...; all 31 blobs equal `git rev-parse F:<path>`, and all 31 working blobs equal the manifest (0 / 0 differ). OPENED.json exists, so `open_refusals` (flag, constants, registration, code check, FREEZE_SHA) passed, because it raises before the ledger. The outcome line "modules executed after the code check: 0" is computed by `cc.after_lines` (cs carries `modules`; not the literal default). HEAD = F; porcelain 0 now. The author's go 13:15:35, the FREEZE_SHA bracket d7707017 at 13:32:01 and F at 13:24:28 all precede OPENED at 12:44:32Z (13:44:32 +0100). OP4 count on main = 1 | CONFIRMED | - |
| 2 | `open` ran exactly once | The output directory has 5 entries (`ls -1 \| wc -l`): freeze, OPENED.json, outcome.txt, outcome.json, SHA256SUMS. `outcome_REFUSED*` count 0 (`grep -c`). OPENED.json is mode x (a second open refuses before any read). `sha256sum -c` OK 2 / 2. op8_open.log (CR stripped, minus `exit=0`) equals outcome.txt | CONFIRMED | - |
| 3 | Roster 342, n 2,304 | KEPT 342, ids sha256 71c12468cd49b0dca1004233ea0ee7fae393eb06039b7114d1af37e0ba192b9c (= registration, full). Split LF pins 3d4d644a7ac34d22 / 9ef05cc2cfe34c91; WORK 3,457, RESERVED 2,304, overlap 0. Values: WORK 1,182,294, RESERVED 787,968 (= 2,304 x 342), NaN 0, binary, duplicate rows 0. Off-majority rows on KEPT models: 0 (all 251 belong to one excluded model). Census text sha256 mismatches 0. Pins items ddccfd20, census.json 48be6018, npz 0e9ef33a, freeze 5320b328 | CONFIRMED | - |
| 4 | The frozen object is WORK-only and is the one scored | Own refit on WORK: BS 225 (internlm/internlm2_5-20b-chat), and the DEC / FAM / PLACEBO / AFI policies and 5 FKI policies are all equal to the frozen ones. Own placebo `default_rng([20261106, 8])` equals placebo_all. The FKI centroids equal unit sums of WORK rows (max diff 0). Each AF descent-table centroid equals the unit sum of its subtree's WORK rows (max diff 5.6e-17; 21 internal nodes, 22 leaves). Descent reproduces the tree's WORK filing 3,457 / 3,457. RESERVED rows reach 22 of 22 leaves | CONFIRMED | - |
| 5 | RESERVED clusters 1,829 (Kish 3.385) | Own union-find (cos >= 0.98 on 4,096-d, UNION census group): RESERVED 1,829 clusters, Kish 3.385, largest 31; WORK 2,662, Kish 4.416. Clusters spanning more than one subtask: 0 / 0, so the stratum convention is moot | CONFIRMED | - |
| 6 | Accuracies on RESERVED | BS 0.7591; DEC 0.8116; FAM 0.8116; PLACEBO 0.7313; FKI 0.8107; AFI 0.7964; ORACLE 1.0000 (all equal) | CONFIRMED | - |
| 7 | T1 not fired | G_PLACEBO -2.7778pp; SE2 1.3193pp; [-5.36, -0.19] (hi < 0, and T1 needs lo > 0); DEFF 3.39; n_eff 679; MDE80 3.69. Differences from outcome.json: point, SE2, one-stage, i.i.d. and percentile all 0.00 | CONFIRMED | - |
| 8 | G4 (evaluated first) | No line in the outcome (D1). In the code (L545-547), `verdicts()` raises before T1. A raise would have produced outcome_REFUSED_* (count 0). Own SE2 values G_DEC 1.1730 / G_AFI 1.2634 / G_PLACEBO 1.3193 / L 0.9148pp are finite and > 0, so G4 did not fire | CONFIRMED | LOW (D1) |
| 9 | C1 HELD | G_DEC +5.2517pp; SE2 1.1730pp; [+2.95, +7.55]; DEFF 3.06; n_eff 753; MDE80 3.28pp. Difference from the run: 0 on every field | CONFIRMED | - |
| 10 | C2 HELD | G_AFI +3.7326pp; SE2 1.2634pp; [+1.26, +6.21]; DEFF 3.55; n_eff 650; MDE80 3.54pp. Difference 0 | CONFIRMED | - |
| 11 | C3 UNDETERMINED (gated on C1 HELD) | L = AFI - 0.5 DEC - 0.5 BS = +1.1068pp; SE2 0.9148pp; [-0.69, +2.90]; DEFF 4.88; n_eff 472; MDE80 2.56pp. Difference 0. C1 is HELD, so C3 is evaluated. S 0.7107, percentile [0.1818, 1.0962], nonpos 2 (equal). RM5 (point instead of interval) turns C3 into HELD, so the interval decides | CONFIRMED | - |
| 12 | F1 does not fire (point) | G_DEC point +5.25 > 0. Consistent with C1 HELD (rule [R-7]) | CONFIRMED | - |
| 13 | The words are robust to the SE used | With an independent stream ([424242, 1] / [424242, 2]), SE2 is 0.997-1.035 x the run's. Intervals: G_DEC [+2.88, +7.63], G_AFI [+1.24, +6.23], L [-0.68, +2.89], placebo [-5.40, -0.16]: the same words. One-stage (RESERVED clusters only), L [-0.06, +2.27] and G_AFI [+2.14, +5.32]; linearised, L [-0.11, +2.33]: the same words. Percentile: C1 +1.93 and C2 +0.57 lower bounds, L [-1.13, +2.49]: the same words | CONFIRMED | - |
| 14 | DEFF re-measured from the RESERVED clusters (rule 8, post-run) | The two-stage DEFF2 = (SE2 / SE_iid)^2 = 3.06 / 3.55 / 4.88, against the plan's 3.42 / 3.39 / 4.14. SE = SD_row x sqrt(DEFF2 / 2,304): 0.3219 x sqrt(3.06 / 2304) = 1.173pp (plan 1.34); 0.3220 x sqrt(3.55 / 2304) = 1.263pp (plan 1.23); 0.1987 x sqrt(4.88 / 2304) = 0.915pp (plan 0.917). One-stage DEFF from the RESERVED clusters alone: 0.96 / 1.46 / 2.06 (bootstrap), 0.98 / 1.54 / 2.26 (linearised). So the WORK refit carries 0.69 / 0.59 / 0.58 of SE2^2. C3 realised: \|L\| 1.11 < MDE80 2.56, consistent with the registered DESCRIPTIVE-ONLY | CONFIRMED | - |
| 15 | Predictions: points in range for P2 / P4 / P8; Brier | P2 +5.25 in [3.66, 7.10] (also in the unrounded [3.665, 7.096]); P4 S 0.7107 in [0.70, 1.30]; P8 +1.107 in [1.05, 3.40] (also in the unrounded [1.046, 3.397]); `score_preds` uses the point (L573-578). P1, P3, P6, P7 HELD; P5 FAILED (C3 not HELD). Brier per prediction 0.0004 / 0.04 / 0.0004 / 0.0196 / **0.4624** / 0.0004 / 0 / 0.04, mean **0.0704**. Sensitivity with P5 at 0.82: 0.0967 (beside; decides nothing) | CONFIRMED | LOW (D2) |
| 16 | Side prints (decide nothing) | FKI: G_FKI +5.1562 [+3.05, +7.26]; L_FKI +2.5304 [+1.29, +3.77]; S_FKI point 0.9818 (difference 0; the S_FKI percentile is not recomputed, a spot check). G_FAM +5.2517 (FAM = DEC row for row: their picks coincide on the merged families). Twins: 561 of 2,304 RESERVED rows have a WORK cosine twin; G_DEC without them +6.3110pp (equal). Top-3 contributions and LOSO [+4.22, +5.58] equal | CONFIRMED | - |

Not applicable here: McNemar-established counts (no judged pair and no wrong-direction count) and within-anchor nulls (the placebo is the
registered L2 design over all 5,761 items). Criterion substitution: none. C1-C3 read G_DEC, G_AFI and L on AFI (C4), and FKI stays beside.

## Defects and conditions (each with its fix)

- **D1 LOW: G4 prints nothing.** "Evaluated FIRST" leaves no line in the outcome, so its pass is implied only by the outcome
  existing. Fix: the registrar records "G4 not fired (POSTRUN: SE2 1.17 / 1.26 / 1.32 / 0.91pp, all finite and > 0)". Future runners should print a
  G4 line.
- **D2 LOW: no Brier score in the outcome**, although P5's registered text names one ("the Brier score use[s] 0.68"). Fix: the
  registrar records Brier 0.0704 (8 predictions, 7 HELD), with the 0.82 sensitivity 0.0967 beside.
- **D3 LOW: the "SE2 of L by the identity" line cannot disagree.** On the same replicates, L = 0.5 G_AFI + 0.5 M holds exactly, so that
  line is a tautology (0.9148 = 0.9148). The informative comparison is the realised 0.9148 against the planning 0.9173. Fix: record that comparison. No
  code change is owed.
- **W1 (wording; MEDIUM if breached): twins.** 561 of 2,304 RESERVED rows (24.3 %) have a WORK cosine twin >= 0.98. The side
  stays "sealed" (ND-1-group-disjoint by construction), never "content-closed", "clean", "disjoint" or "held-out". The gains are not carried by the twins. Descriptive
  only: twin-free G_DEC +6.31, G_AFI +5.45, L +2.29pp; twin rows only G_DEC +1.96, G_AFI -1.60, L -2.58pp. The twin-free L
  (+2.29) is a post hoc subset. It is never quoted as a C3 reading or as "half recovered".
- **W2 (wording): C3.** UNDETERMINED, at a registered DESCRIPTIVE-ONLY Support. Under the registration ("never cited as 'the
  anchor-free tree does not recover half of the declared gain'") and D-2026-11-10-1 ("C3 only if HELD"), C3 is not cited. S 0.71 is
  descriptive. M = AFI - DEC = -1.52pp [-3.23, +0.20] is beside only.
- **W3 (wording; LOW): C2's reach.** Stage 1 keeps the cells fixed, as registered, so SE2 is conditional on the one frozen tree: tree-construction
  variance is not in it. Cite "the anchor-free tree fitted on the 3,457 WORK texts (22 leaves, chosen by the recipe)", not anchor-free trees in general.
- **Citable as registered (D-2026-11-10-1):** C1, for key result 1's BBH part, as a second roster on a sealed side: "a per-subtask policy fitted on
  WORK beats the best single model on BBH's sealed RESERVED side, 342 KEPT models: G_DEC +5.25pp [+2.95, +7.55], n 2,304 (1,829
  content clusters)". C2, for the framing's last clause, on this corpus and roster: "G_AFI +3.73pp [+1.26, +6.21]".

## Reviewer's checker mutants (each must make the recomputation disagree with the run)

| id | change (in a copy of recompute.py) | result | decisive |
|---|---|---|---|
| RM1 | AF descent argmax -> argmin | killed: G_AFI point off by 7.42pp; C2 UNDETERMINED, C3 FAILED | yes |
| RM2 | bootstrap unstratified (one stratum) | killed: SE2 off (G_DEC by 0.13pp); points equal | yes |
| RM3 | cluster cos threshold 0.98 -> 0.97 | killed: RESERVED 1,638 clusters (Kish 4.595); SE2 off | yes |
| RM4 | placebo stream [20261106, 8] -> [.., 3] | killed: placebo labels != frozen; G_PLACEBO off by 0.83pp | yes |
| RM5 | C3 read on the point instead of the interval | killed: C3 HELD (!= UNDETERMINED) | yes |

## Commands (scripts and logs in the backup above)

```
python -I recompute.py            # recompute.log: pins, split, roster, values, texts, clusters, own policies vs frozen, AF
                                  # table check, points, two-stage bootstrap on the registered streams [20261106,7] / [..,9]
                                  # re-implemented + independent streams [424242,1/2], linearised SE, words, predictions,
                                  # Brier, twins; COMPARISON vs outcome.json: point / se_iid / SE2 / one-stage / pct diffs 0.00
python -I twins_side.py           # twins_side.log: twin-free / twin-only points; SD_row x sqrt(DEFF2/n) arithmetic vs plan
bash mutants.sh                   # RM1-RM5, mut_RM*.log: 5 / 5 killed
python -c "...OPENED.json..."     # manifest 31 files -> de21fc92...; blobs vs F 0 differ; working vs manifest 0 differ
git rev-parse HEAD; git status --porcelain --untracked-files=all | wc -l   # 54ed9bf...; 0
tr -cd '\r' < <file> | wc -c      # confirm 0, test 0;  git diff --numstat f307079 54ed9bf  # 1/1, 2/2
git merge-base --is-ancestor 54ed9bf master   # exit 1 (local, not merged)
ls -1 <outdir> | wc -l; ls -1 <outdir> | grep -c REFUSED                 # 5; 0
diff <(head -n -2 op8_open.log | tr -d '\r') <(tr -d '\r' < outcome.txt)   # equal
sha256sum <outdir>/* | diff - before_outdir.sha                           # unchanged after the review
git show main:docs/judge_v2_program.md | awk '<section>' | grep -c 5320b328...   # 1 (OP4)
```
At most 3 BLAS threads and one process at a time. No python or java process was left (`tasklist` count 0 / 0). Ledger unchanged (v430).
