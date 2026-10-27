# POST-RUN review: FITSET-FAITHFUL stage 0 (adversarial-reviewer, 2026-10-03; zero calls)

Run: main at 3945326f merge + e50105a6 brackets; `tools/analysis/fitset_faithful.py` blob:ed34306596ef63ba2d4b59bc24d54fad0eb8149a
(LF; `git hash-object` on main = the READY pin). Outcome `experiment_results/archv2/rp12_r2/fitset_faithful_s0_outcome.txt`,
108 lines, 19,305 B, sha256-16 f726c7534e9825ae, mtime 2026-10-03 14:33:35. READY: `docs/reviews/READY_fitset_faithful.md`.

## Verdict: VALID. FF1 HELD (no knife-edge of either kind); FF2 UNDETERMINED; F-FF does not fire. Wording W-1..W-5 below binds the registrar

## Per-claim table

| # | claim (outcome) | result | mine (own refit, own naming/filing, read-only) | sev |
|---|---|---|---|---|
| 1 | P_A 0.8119, P(A-refit) 0.8374 | CONFIRMED | 4,984 / 6,139 = 0.811859; 5,141 / 6,139 = 0.837433 | - |
| 2 | FF1 D +0.0256 [+0.0193, +0.0320] | CONFIRMED | 157 / 6,139 = +0.025574 [+0.019306, +0.031960] (GB.stat, B 2,000, seed 20260929); 264 gained / 107 lost items; my independent refit = the script's arm_refit item for item | - |
| 3 | D > spread_B 0.012543; HELD | CONFIRMED | 157 vs 77 items: margin 80 items (0.0130); C-2 exact-bar knife-edge (D = 77/6,139) not reached | - |
| 4 | C-1 pipeline offset applied | CONFIRMED, not triggered | A0 (A's own vmfMu via the common rule) 4,987 = 0.812347; D' = P(A-refit) - P(A0) = 154 / 6,139 = +0.025086 [+0.018763, +0.031589], DEFF 1.066: also HELD. D = 157 lies outside the knife-edge set {78, 79, 80}; F-FF upper +0.0320 is far above (0, +0.000489] | - |
| 5 | FF2 rho +0.2351 [-0.1301, +0.5441], m 32; UNDETERMINED | CONFIRMED | own residual-regression partial Spearman on ranks: +0.2351 [-0.1301, +0.5441], m 32 | - |
| 6 | F-FF does not fire | CONFIRMED | upper +0.0320 > 0 | - |
| 7 | Support printed beside the statistic | CONFIRMED | SE 0.00320, DEFF 1.052 (measured; transported 1.223), n_eff 5,837, MDE80 0.0090, discordance 0.060; effective bar max(0.0090, 0.012543) = 0.012543; D exceeds bar + measured MDE80 (0.0215) | - |
| 8 | MMLU_PRO_LB stratum +0.0446 [+0.0344, +0.0555] (desc.) | CONFIRMED | 155 / 3,478 = +0.044566 | - |
| 9 | Bookkeeping: 0 leaves without items; 0 fallback names; 3 naming changes | CONFIRMED | 0 empty leaves (own count); 3 changes (FF info) | - |
| 10 | P1, P2, P4 HELD | CONFIRMED | +0.0256 in [-0.005, +0.035]; +0.2351 in [-0.10, +0.65]; +0.0446 in [0, +0.05] | - |
| 11 | Console = outcome; write-once | CONFIRMED | all 108 outcome lines appear in the 110-line console; only the console has the `cost` and `wrote` lines; mode "x" + exists-refusal (READY #7); one outcome file | - |
| 12 | No writes to DBs of record | CONFIRMED | sizes and mtimes of mmlu_pro_dataset_cache_v2.db, multicorpus_cache_v1.db and every root -wal (0 B) match the pre-run listing in the READY session | - |
| 13 | Rule 7: java PIDs 31012 / 58076 | CONFIRMED benign | created 14:19:52 / 14:20:04 (before the run); 31012 command line = GradleDaemon, 58076 = KotlinCompileDaemon; neither is a construction, site null or pool writer (the DB mtimes in #12 agree) | LOW (disclose) |

## Where the effect sits (descriptive; needed for the wording)

- 155 of the net 157 items come from MMLU_PRO_LB true-class items; the other sources net +2 (BBH and MUSR at P 1.000 under
  both arms; MATH, GPQA, IFEVAL mixed). Split-anchor true-class items +155 (n 4,924), unsplit +2 (n 1,215).
- Not uniform: MMLU-Pro chemistry -0.0526, economics -0.0200, math -0.0153, business -0.0128; largest gains computer science
  +0.1667, physics +0.1473, other +0.1372, engineering +0.1336.
- The bridge's per-anchor partial rho (B-gt_0 - B_0) is +0.416 [+0.073, +0.672]: DESCRIPTIVE, never scored, k-means arms.

## Wording for the registrar (binding)

- **W-1 (scope, every sentence).** "Re-estimating the leaf MEANS of B0 (lane r2, one construction) on the TRAIN items of each
  anchor's declared class, with B0's 133 leaves and topology fixed". Never "a construction with declared fit sets" (S1,
  unregistered), never "the tree's splits", never "label-free". It is an anchored-tree variant that USES MORE TRAIN LABELS than
  A (fit-set membership below depth 2); nothing about anchor-free trees, label-free cells or RP13.
- **W-2 (FF1).** "FF1 HELD: the class-pure refit files EVAL better than A as built, D +0.0256 (157 / 6,139 items), 95%
  [+0.0193, +0.0320], above the transported bar spread_B 0.012543 (B's five-seed spread; A's own construction-seed spread is
  unmeasured and A-refit is deterministic). Against A filed by the same common rule (C-1), D' +0.0251 [+0.0188, +0.0316]:
  held as well." The HELD is carried by MMLU-Pro (155 of 157 net items); say so beside it.
- **W-3 (confounds, carried verbatim).** (1) fit-set size vs purity are not separated by FF1 (declared sets differ in size
  from routed sets); (2) the motivating evidence is k-means, and this is a means re-estimation on fixed topology, not a
  construction; (3) anchored trees only, added TRAIN-label use.
- **W-4 (FF2).** "FF2 UNDETERMINED: partial rho +0.235, 95% [-0.130, +0.544] (m 32; SE_z 0.189; DESCRIPTIVE-ONLY at the
  prediction, rho-MDE 0.48)". Never "the gain tracks impurity"; the per-anchor mechanism is not established. The bridge rho
  +0.416 is descriptive (k-means arms) and is not set against FF2.
- **W-5 (consequence).** F-FF does not fire: checkpoint D's #8' keeps design status as a hypothesis for S1; it is not
  evidence that S1 would gain (WILL-NOT-SHOW). S1 and the A replicates remain the author's.

## Defects

None against the run. D-1 (LOW, disclose): two IDE daemons were alive at launch; both are benign (#13).

## Commands

```
python scratchpad/ffrev/post_ff.py   # main checkout, read-only loads via FF._hooks + GB.load_objects + DSC.load_anchors:
  # own refit (nearest leaf in the anchor, normalised means, unsplit = class mean), own TRAIN-majority naming (tie by name),
  # own filing; P_A, P_R, A0; D, D' with GB.stat; gain/loss; equality with FF.arm_refit; split/unsplit and MMLU split;
  # FF2 by residual regression on ranks with Fisher z
python - <console> <outcome>          # line-set comparison: 0 outcome lines missing from the console
sha256sum <outcome>; ls -la --time-style=full-iso <main>/*.db-wal <main>/mmlu_pro_dataset_cache_v2.db <main>/multicorpus_cache_v1.db
Get-CimInstance Win32_Process -Filter "Name='java.exe'"   # 31012 GradleDaemon, 58076 KotlinCompileDaemon, both 14:19-14:20
```
