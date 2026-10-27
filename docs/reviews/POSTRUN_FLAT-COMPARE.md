# POSTRUN review: FLAT-COMPARE (M1; axis tree V0 vs within-anchor k-means, size-matched random cells, text-kNN field; EXPLORATORY, WORK only)

Authority: D-2026-10-22-2 (TaxoArena 875253bc; the author's words "go ahead, and run the flat clustering comparison too").
Reviewer: adversarial reviewer, 2026-10-23. Zero LLM calls. Max 7 of my processes at a time (6 workers + 1), BLAS 1 thread each.
Reviewed: benchzoom branch `flat-compare` (local; 0 remote branches contain 8b937da), d9144ae..8b937da on master 8610a5d
(= merge-base). Run of record at 8177915, runner LF blob `86bddccd` (all 3 parts and `--analyze`; `dirty` ""). Tip LF blobs:
runner `da00fcda`, plan `7067fe89`, test `efedca42`. The working tree is LF (0 CR bytes) and `git hash-object` equals the tip
blob for all 3 files, so no CRLF rendering differs. Outputs `E:/benchzoom_demo/followups/flat-compare`: summary.txt sha256
3174c132…, SHA256SUMS 9/9 OK, checked before and after my runs.

## Verdict

**OUTCOME CONFIRMED (exploratory). The words stand: K1 KILLED; K2 KILLED on MATH only; V0 vs random: MATH and MMLU
"TEXT STRUCTURE BEATS SIZE ALONE", MMLU-Pro "NOT DISTINGUISHABLE (UNDERPOWERED)". MERGEABLE: 3 new files, src untouched.**
- Every deciding number reproduces to the printed digit. My statistics code run on the builder's per-item arrays (Phase A)
  gives the same numbers. My own harness driver, built from library primitives (Phase B), reproduces every per-item array
  to <= 1.4e-17 on all 3 datasets: V0, L3k, controls, KM through the builder's partition function, and RND written from the
  plan text alone.
- An independent spherical k-means with its own streams gives the same K1 legs. MATH: D_km -0.1762 SE 0.0386. MMLU:
  -0.0048 SE 0.0151. Both REACH.
- Conditions on use (not on the merge): D1 (wording in the hand-back), D2 (SE-convention sensitivity of the descriptive
  MMLU V0-vs-random word).

## Per-claim table (deciding claims)

| # | Claim (builder) | Own result | Verdict | Sev |
|---|---|---|---|---|
| 1 | Plan d9144ae (00:08:27) and [P1] 04c9f78 (00:12:19) committed before any statistic on responses | Branch created 23:58:03. Reflog shows 4 commits, no amend or reset. The builder's first scratch file is 00:19:18 (synthetic selftest). `find` over E:/TaxoArena_tmp and E:/benchzoom_demo, 21:00 to 00:08:27, finds 0 flat-compare files. Runner committed 01:09:04; math.npz mtime 01:15:22 (342 s harness, so started after the commit). Plan diff d9144ae..8b937da: 0 deleted lines. Runner diff 8177915..8b937da: +9 docstring lines, 0 deleted | CONFIRMED | - |
| 2 | Branch touches only its own files | `git diff --name-only master..flat-compare \| wc -l` = 3 (plan, runner, test); 1843 insertions, 0 deletions; src 0 files | CONFIRMED | - |
| 3 | Reproduction first: all REPRODUCED; per-item diff to gap-baseline 0.0 | MATH G(V0\|L2) 0.12405 SE 0.03497; C1 0.10932 SE 0.03159. MMLU 0.05749 SE 0.02274. MMLU-Pro -0.00981 SE 0.02116 / -0.00953 SE 0.01961. All within half a unit of the record's last decimal. Per-item max \|diff\| = 0 on all 3; clusters equal | CONFIRMED | - |
| 4 | Readouts C1: MATH V0 / KM / RND / L3k +0.109 / +0.275 / -0.005 / +0.350; MMLU +0.044 / +0.052 / -0.000 / +0.106; MMLU-Pro -0.010 / +0.002 / -0.006 / +0.069 | MATH +0.1093 / +0.2745 / -0.0053 / +0.3499; MMLU +0.0435 / +0.0521 / -0.0004 / +0.1064; MMLU-Pro -0.0095 / +0.0022 / -0.0056 / +0.0689; SEs equal to 4 dp | CONFIRMED | - |
| 5 | K1 KILLED: k-means reaches V0 on MATH and MMLU; MATH beats V0 by 4.6 paired SE | MATH D_km -0.1652 SE 0.0358 (items 0.0346, MC 0.0092), z -4.61. MMLU -0.0085 SE 0.0147, z -0.58. Reach on both. Independent k-means: MATH -0.1762 (0.0386), MMLU -0.0048 (0.0151). Because D < 0 on both legs, the word holds under ANY SE | CONFIRMED | - |
| 6 | K2 KILLED on MATH only | MATH: arm A +0.2450 >= 3 x 0.0459 = 0.1376; arm B +0.0067 < 0.0102, so it FIRES. MMLU: arm A +0.0705 >= 0.0583; arm B +0.0165 >= 0.0106 (1.56 SE), so it does not fire. Same under V0-leaf SEs (MATH A z 4.01, B z 0.44; MMLU A fails at z 2.44) | CONFIRMED | - |
| 7 | V0 vs random: MATH +0.115 (3.6 SE), MMLU +0.044 (2.4 SE) BEATS; MMLU-Pro NOT DISTINGUISHABLE (UNDERPOWERED) | +0.1146 / 0.0316 (3.63); +0.0439 / 0.0180 (2.44); -0.0039 / 0.0197, MDE80 0.0561 > C1(V0) -0.0095. My own random cells: MATH +0.1162 (3.59 SE), MMLU +0.0437 (2.44 SE) | CONFIRMED (MMLU see D2) | MED |
| 8 | Brier / AUROC move the same way | Brier spot check (descriptive): MATH C1 V0 / KM / L3k +0.0457 / +0.1045 / +0.1364; MMLU +0.0102 / +0.0144 / +0.0346. AUROC not recomputed (P arrays not saved; descriptive only) | CONFIRMED (spot) | - |
| 9 | Power (plan §7) and realised MDE80s | Planning MDE80s re-derived, (c + 0.8416) x SE: 0.0534 / 0.0424 / 0.1652 / 0.1498 / 0.0645 / 0.0424 / 0.0824 / 0.0654, all as printed. Realised: K1 0.0660 / 0.0270; K2-A 0.1762 / 0.0746; K2-B 0.0187 / 0.0195; RND 0.0897 / 0.0511 / 0.0561. The MMLU K1 leg detects 62% of C1(V0) at 80% (68% power at half). The MATH K2-B bound: V0 residual upper 95% +0.027 = 22% of G(V0\|L2) | CONFIRMED | LOW (D5) |
| 10 | DEFF / n_eff columns (MATH C1(V0) 1.05 / 2,805; MMLU 2.06 / 4,099) | DEFF_cell reproduces: 1.05 / 1.06 / 1.03 / 1.03 (MATH) and 2.06 / 2.01 / 2.04 / 1.86 (MMLU). But n_eff = n_ITEMS / DEFF_CELL mixes units: in cells it is 193,555 (MATH) and 323,856 (MMLU). Re-measured from the cache's own content clusters (2,946 / 8,375 / 7,085 for 2,949 / 8,425 / 7,197 items): item-level DEFF 1.001 / 1.006 / 1.027, n_eff 2,947 / 8,372 / 7,006 | PARTLY | LOW (D3) |
| 11 | Vault / reserved reads 0; zero LLM calls | My own loads: guards [0] (MATH, MMLU-Pro) and [0, 0] (MMLU) at load and at end. Builder logs: 0 on all parts. Partitions read the TEXT embeddings of all items (4,914 / 14,042 / 11,994, vault items' text included, exactly as V0's own construction did); no response. E:/benchzoom_cache: 1,235 files, mtime/size listing identical before and after (diff 0 lines) | CONFIRMED | - |
| 12 | Selftest 7/7; mutants 56/56; suite 889 passed | Control selftest 7/7 PASS. Branch test + execution-graph sync: 37 passed, 1 deselected (slow). Own mutants 7/7 killed (below). Full suite not re-run: src diff is 0 files | CONFIRMED | - |
| 13 | Backup 19/19; outputs 9/9 | `sha256sum -c` 19/19 OK (SHA256SUMS_backup 75f6ad75…); outputs 9/9 OK | CONFIRMED | - |
| 14 | Hand-back: "k-means and the kNN reader both beat V0" | The kNN field beats V0 on all 3 (L3k-V0 +0.2406 / +0.0629 / +0.0784; z 4.44 / 2.97 / 2.40). k-means beats V0 on MATH only; MMLU is a tie (0.6 SE, V0 lead 95% upper bound +0.020) and MMLU-Pro is a tie (0.8 SE) | PARTLY | MED (D1) |

Partition checks: k_a = V0's leaf count per anchor over all items (sums 36 / 100 / 80). Every builder KM partition is a
spherical-Lloyd fixed point (share of items whose own centroid is nearest = 1.0000 on all 15). The summed-cosine objective
of KM is above V0's: MATH 3263-3264 vs 3234, MMLU 9057-9061 vs 8971, MMLU-Pro 7465-7469 vs 7403; mine falls in the same
ranges. Random cells have exactly V0's WORK sizes per anchor. MATH KM WORK cells range 38-147 against V0's 45-138, so the
"ungated" caveat does not explain MATH.

## Defects

- **D1 (MEDIUM, wording):** the hand-back's AUTHOR DECISIONS line says "k-means and the kNN reader both beat V0".
  Fix in the registrar's record: "k-means REACHES V0 on MMLU (-0.0085 SE 0.0147) and beats it on MATH (-0.165, 4.6 SE);
  the text-kNN field beats V0 on all three". The plan's [P2] reading (1) is already correct.
- **D2 (MEDIUM, SE convention; not a re-decision):** the pre-specified SE is clustered by content cluster. That is
  practically item-iid (item DEFF 1.00), and it ignores the dependence that shared estimated cell offsets induce among
  items of one cell. Clustering by V0 leaf (sensitivity, my code) inflates the SEs x1.3-1.8. K1 and K2 are unchanged.
  MATH V0-vs-random falls to 2.02 SE. **MMLU V0-vs-random falls to 1.51 SE, which would read NOT DISTINGUISHABLE.** "4.6
  SE" becomes 3.41 SE. C1(V0) itself is 1.9 SE (MATH) and 1.5 SE (MMLU) under leaf clustering. Fix: quote the MMLU
  random-cells word only together with this sensitivity, and pre-specify a cell-aware SE (leaf or two-way clustering, or
  a partition-level bootstrap) in any registration built on M1.
- **D3 (LOW):** the n_eff column divides the item count by a cell-level DEFF. Fix: print n_eff in cells
  (n_cells / DEFF_cell), or the item-level DEFF from cluster sizes beside it.
- **D4 (LOW, disclosed):** the [P1](d) flag prints "(arm A UNDERPOWERED)" on MMLU although arm A holds; its condition is
  "the leg did not fire". Fix in any reuse: condition the flag on arm A failing. No word changes.
- **D5 (LOW):** plan §7 names no DEFF and no source for it. Its planning SEs are content-cluster SEs of record, so the
  DEFF is implicitly about 1, and the re-measured 1.001-1.027 confirms that. §7 (i) calls KILLED "the informative
  direction", which is backwards in principle: a reach-within-1-SE rule is where an underpowered leg drifts. Here KILLED
  is informative only because MATH reads D = -4.6 SE and the MMLU leg's MDE80 is 62% of C1(V0). Fix: state DEFF, its
  source, and the KILLED direction's power in any registration.

## What the result licenses / does not license

Licenses (WORK items, exploratory, the same items on which TREE-VARIANTS retained V0, so that selection favours V0):
- After L2, difficulty deciles and length deciles, a flat within-anchor spherical k-means at V0's resolution on the same
  512-d text vectors predicts at least as well as the axis tree on MATH and MMLU, and better on MATH.
- On MATH the text-kNN field carries V0's information: V0's residual is +0.0067, with a 95% upper bound of +0.027.
- On MMLU, V0 keeps a residual of +0.0165 (1.56 SE) beyond the field.
- The axis leaves carry real text structure on MATH: they beat size-matched random cells at 3.6 SE, and at 2.0 SE under
  leaf clustering.

Does not license:
- Any fresh, vault or registered statement.
- Replacing V0 in BZ-AXIS-CONFIRM-FRESH or switching estimators (the author's call).
- "k-means beats V0" on MMLU or MMLU-Pro.
- "The axis rule carries no signal".
- k-means at its own best k, or D1's cross-fitted k.
- Any attribution of the field's lead to method rather than to 4096-d vs 512-d vectors.
- Any MMLU-Pro reading beyond descriptive (V0's own C1 there is -0.0095).
- Reopening any closed line.

## Own mutants (copies under E:/TaxoArena_tmp/review_flat-compare/mut/<id>, sandboxed TMP/TEMP/BZ_SANDBOX; runner `--selftest`)

R0 control passes 7/7 · R1 K2 arm A divides by arm B's SE: killed (S6), decisive · R2 MC term without /sqrt(seeds):
killed (S3), decisive · R3 k_a = V0's total leaves in every anchor: killed (S2), decisive · R5 rnd UNDERPOWERED flag
reversed: killed (S6), not decisive · R6 K1 leg with the single-arm SE of C1(V0): killed (S6), decisive · R7 D_km sign
flipped in PAIRED: killed (cell-vs-item consistency guard, ValueError), decisive · R8 k-means cells not offset by anchor:
killed (S2), decisive. 7/7 killed.

## Commands / scripts (E:/TaxoArena_tmp/review_flat-compare; sha256 prefixes)

```
phaseA.py (3850d186)  python -I phaseA.py   # own CR SE / MC / rules on the builder's parts/*.npz (read-only) -> phaseA.log
phaseB.py (6f6cefb4)  python -I phaseB.py {math|mmlu_pro|mmlu} 6   # own driver: gw.load_real / T.load_dataset /
                      # axis_confirm_mmlu.load_real + mgb.mmlu_gdata; own anc from the pinned pickle; gw.group_folds,
                      # gw.l2_contexts, gw.reader, gw.item_pi, M.step("field_txt"); own KM (KMr) and RND (RNDr, RNDp);
                      # guards asserted 0 -> phaseB_<ds>.{npz,json,log} (562 s / 152 s / 1433 s)
phaseC.py (1b4d7d89)  python -I phaseC.py <ds>   # array agreement, own arms, DEFF two ways, leaf / 2-way SE -> phaseC_<ds>.log
rmutants.py (e02006d0) python -I rmutants.py     # -> rmutants.log
git -C <wt> diff --name-only master..flat-compare | wc -l      # 3
git -C <wt> diff 04c9f78 8b937da -- docs/flat-compare.md | grep -c '^-[^-]'   # 0
find E:/benchzoom_cache -type f -printf '%T+ %s %p\n' before/after; diff | wc -l   # 0
venv pytest -q tests/test_flat_compare.py tests/test_execution_graph_sync.py   # 37 passed, 1 deselected
```
