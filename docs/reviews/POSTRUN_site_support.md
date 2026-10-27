# POSTRUN review — SITE-SUPPORT (zero calls)

Reviewer: adversarial-reviewer, 2026-10-04. Registration prog L24349-L24360 (_as_of 61d1c5bf, heading "## Registered 2026-10-04
(before any code or call) — SITE-SUPPORT: ..."), brackets SS-R1/R2/R4, D-3, D-10, P-1..P-3. READY: `docs/reviews/READY_zero_call_trio.md`.
Run: `tools/analysis/site_support.py` blob:4612345c (LF; `git hash-object` = HEAD blob, merged e8504eb2), zc_common blob:c912dccf.
Outcome `E:/TaxoArena_backup_2026-10-04_site_support/site_support_outcome.txt` sha256 60d4cb39... (matches SHA256SUMS.txt, written by
the run). Site-null CSV blobs 8ed1b699 / 7ac6510d / 264f4cd9 / fd998a79 re-hashed = the pinned ones.

## Verdict

**VALID**, with corrected words on SB2 (C-SB2) and the P1 qualifier (C-P1). SB1 NOT-SHOWN and F-SS FIRED stand, unchanged under
P-1 and P-2. SB2 RECURS stands as a live classification. Its registered null is a **floor**, though, not a test of tree-specific
structure: random-subset TBE is exactly 0 for 98.1% of draws, and the criterion reduces to "median real-site TBE > 0". This differs
from HF2 CLINC (POSTRUN_granularity_gt.md D-1). There the criterion could not be met at all. Here a real site can score 0 (1 of
264 does), and RECURS would fail if the four trees shared no clusters. So SB2 is informative, but only against "the four re-draw trees
are mutually unrelated".

## Per-claim table (deciding claims)

| # | claim (outcome) | reviewer's number | status | sev |
|---|---|---|---|---|
| 1 | \|C\| = 2,772; 264 sites (48 cert / 216 uncert); 4 roots skipped (smaller side < 20) | 2,772; 264 (48/216) from own loader (snapshots.db immutable, intersection of root member sets) | CONFIRMED | - |
| 2 | depth x size strata: cuts on log\|S\| at n = 62.0/91.0/128.0/215.4; 11 strata, 10 with both classes; per-stratum gaps as printed | identical cuts, counts and all 10 gaps to 4 dp (3:q2 0/9 dropped) | CONFIRMED | - |
| 3 | G (w = min) = -0.0173 | -0.0173 (own `gap`) | CONFIRMED | - |
| 4 | one-sided within-stratum permutation p = 0.7657, perm SD 0.0235 | exact replica of the stream (RandomState(20261004), keys sorted by str, site order tree x node): **0.7657 / 0.0235**. Own independent RNG: 0.7659 (another order: 0.7739; MC SE about 0.004) | CONFIRMED | - |
| 5 | SB1 NOT-SHOWN; F-SS FIRED | G <= 0 under all weightings: min -0.0173, harmonic -0.0196, n-weighted -0.0411. Depth-only -0.0239. Size-only +0.0070 (not the registered strata) | CONFIRMED | - |
| 6 | SB2: median TBE 0.6293 vs median p97.5 0.0000; 263/264 above | 0.6293 vs 0.0000; 263/264 (own RNG, 200/site); random TBE max 0.037, 98.14% exactly 0; real TBE = 0 at 1 site | CONFIRMED number; word **PARTLY** (C-SB2) | MEDIUM |
| 7 | Support as realised: SD 0.2383, SE 0.0434, n_eff 203, MDE80 0.1078 (declared DEFF 1.3) | 0.2383, 0.0434, 203, 0.1078 reproduce; measured DEFF in P-3 | CONFIRMED arithmetic | - |
| 8 | P1 \|C\| 2,772 in [1,500, 3,000] HELD | number confirmed; the outcome prints a bare "HELD", and the bracket requires "observed at the dry-run, before the run" | PARTLY (C-P1) | LOW |
| 9 | P2 FAILED (Brier 0.2025); P3 occurred (Brier 0.0400) | (0.45-0)^2 = 0.2025; (0.8-1)^2 = 0.0400 | CONFIRMED | - |

## Check 1: stratification and the w = min weight

- The script uses depth {0-1, 2, 3, >=4} (its own `depth_stratum`, not cert_align_size's `>=5`), as registered. Size quintiles are on
  n = |S| (SS-R2), pooled over the four trees. The stratum keys of the permutation are the keys of G.
- Weights w_h = min(n_c,h, n_u,h), as registered. Several strata carry w = 1-3 (0-1:q4 7/1, 2:q3 1/3, >=4:q3 1/18), so G is
  driven by 2:q4 (w 8, +0.089), 3:q3 (w 9, -0.053), >=4:q2 (w 9, -0.018) and 3:q4 (w 6, -0.052). The harmonic and n weights keep the
  sign negative (row 5): the verdict does not depend on the weight.
- Descriptive: the raw gap is **+0.1238** (cert 0.7108 vs uncert 0.5870). Certified sites sit higher and are larger, and the
  depth x size stratification removes the whole raw advantage. This is the size/depth confound the registration aimed at, not an
  artefact of the weight.

## Post-run duties

- **P-1 (children-TBE; D-3).** For each site, the mean TBE of its children that have >= 20 items and smaller side >= 20 on C:
  262 sites (48 cert). Cert 0.5343 vs uncert 0.3933. Stratified G **-0.0351**, own-RNG p 0.907; size-weighted children G -0.0345.
  **No sign change**: F-SS holds for both the own-cluster and the children reading of D-3.
- **P-2 (tree x depth x size strata; D-4).** G **-0.0132**, own-RNG p 0.712, 23 strata with both classes. **No word change**
  (NOT-SHOWN).
- **P-3 (DEFF from the cache; cluster = tree x depth-1 subtree).** There are only **8 clusters** (two depth-1 subtrees per tree;
  sizes 29-39). ANOVA ICC 0.127 with m_w 33.3 gives DEFF **5.11** for a mean TBE (n_eff 52, SE 0.0860, MDE80 0.214). The
  cluster-robust / iid variance ratio for the cert-uncert contrast is **0.27** (n_eff 991, SE 0.0196, MDE80 0.049). The contrast is
  mostly within-cluster, but CR variance with 8 clusters is unreliable. The declared 1.3 lies between the two. **DEFF is not
  identifiable at 8 clusters**: report it as UNDETERMINED, between 0.27 and 5.1, never as 1.3 confirmed. The direct measured scale is the
  within-stratum permutation SD of G, 0.0235, which gives an MDE80 of 2.487 x 0.0235 = 0.058. No reading changes SB1, because G < 0
  and F-SS rests on the sign. The registered verdict line (DESCRIPTIVE-ONLY at the +0.08 prediction) is kept as registered.
  Caveat: the permutation treats nested sites as exchangeable within strata. That is anti-conservative for a positive G and
  irrelevant at G < 0.

## SB2: informative or vacuous (the brief's question)

- Mechanism. delta(s, B) = min over the nodes of B of |S symmetric-difference b|, with no complement and no singleton clusters. For
  a random S of size m and a node of size k, the expected overlap is mk/|C|. delta then stays above p - 1 for almost every node, so
  max(0, 1 - delta/(p-1)) clamps to 0. Normalising by p - 1 is the Lemoine construction, which makes random branches score about 0 by
  design. The p97.5 of 0.0000 therefore comes from the TBE null itself, not from a code fault: draws are not inert (max 0.037, 1.86%
  non-zero).
- Live, not vacuous. A real site can score 0 (1 of 264 does), and SB2 would read NOT-RECURS if the median site had no
  near-match in any other tree. Unlike HF2 CLINC, the criterion can be reached in both directions, so SB2 stays EVALUATED.
- Weak. Any partition of C with geometric coherence would clear the floor, so the word cannot carry "tree-specific" or "certified"
  structure. **Reviewer's structure-aware null (descriptive, not registered):** random unions of the same tree's leaves (on C), filled
  to the site's size, 50 per site. Median p97.5 **0.486** vs real median 0.629. **167/264** sites clear their own p97.5: all 91 at
  depth <= 3, but only 76/173 at depth >= 4; 38/48 certified and 129/216 uncertified. (MC: 164/264 on another site order.) This
  null is harsh for deep sites, which are often 1-3 leaves.

## Defects and conditions

- **C-SB2 (MEDIUM, words).** Quote SB2 as: "RECURS against the registered random-subset null, which is a floor (median p97.5 =
  0.0000; 263 of 264 sites above their own p97.5; 98.1% of random-subset TBE values are exactly 0). It shows only that the four
  re-draw trees are not mutually unrelated, not that their sites recur beyond any coherent partition. Beside it (reviewer,
  descriptive): 167 of 264 sites clear a same-tree leaf-union null (all 91 at depth <= 3, 76 of 173 at depth >= 4)." Fix for future
  TBE tests: register a structure-aware null (leaf-union or k-means-hierarchy sites against the trees) as the deciding reference.
- **C-P1 (LOW).** Record P1 as "HELD (|C| = 2,772 observed at the dry-run, before the run; not a prediction tested by the run)",
  per the SS-R1 bracket. The script prints a bare HELD.
- **C-F-SS (LOW, words).** F-SS is quoted with D-3's scope: "on own-cluster TBE (children-TBE G -0.0351, P-1: same sign)".
- **C-DEFF (LOW).** Quote P-3 as "DEFF UNDETERMINED at 8 clusters (ANOVA 5.11 for a mean; CR-ratio 0.27 for the contrast);
  measured permutation SD of G 0.0235 (MDE80 0.058)". The declared 1.3 is neither confirmed nor refuted.
- No BLOCKER. Nothing was written to a DB of record: snapshots.db was opened `mode=ro&immutable=1`, and its mtime/size
  1791039429/1097515008 were the same before and after.

## Commands

```
git hash-object tools/analysis/site_support.py tools/analysis/zc_common.py experiment_results/anchorfree/redraw/site_null_af_*.csv
OMP/OPENBLAS/MKL_NUM_THREADS=1 python E:/TaxoArena_tmp/ss_review/ss_recompute.py > ss_recompute.out   # 13 s, single thread
  # own loader + TBE + strata + G(min/harm/n) + own-RNG perm + P-1 + P-2 + P-3 (ANOVA ICC, CR ratio) + random-subset SB2
  # + leaf-union null + exact replica of the script's permutation stream (REPLICA p 0.7657 permSD 0.0235)
stat -c '%Y %s' snapshots.db   # before = after
cd E:/TaxoArena_backup_2026-10-04_site_support && sha256sum -c SHA256SUMS.txt   # 4 files OK
```
Backup additions (appended to the run's SHA256SUMS.txt): site_support_run.log 59c071bd..., ss_recompute.py cdc3df30...,
ss_recompute.out abf043ac....
