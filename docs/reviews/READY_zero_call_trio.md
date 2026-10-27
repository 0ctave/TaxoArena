# READY review: SITE-SUPPORT, TREE-LIKE, SCALE-AGREE (zero-call trio), 2026-10-04

Reviewed: branch `zero-call-trio`, tip 98af68f9 (parent 404d286d); registrations 633255f2, prog L24349 / L24362 / L24375
(headings verified by `grep -n`; no later bracket on the three ids: grep of the ids past L24386 returns nothing). Zero calls.
Reviewer runs: selftests, the builder's 70 mutants, 8 of my own, all five real dry-runs (no java running; `tasklist` count 0).
No --run, no TBE / z / AMI computed on real data.

## Verdicts

| test | verdict | conditions before `--run` |
|---|---|---|
| SITE-SUPPORT | **READY** (code 4612345c) | C-SS1 registrar bracket on SS-R1 / SS-R2 / SS-R4; run in a pool slot (rule 7); post-run duties P-1..P-3 |
| TREE-LIKE | **READY-WITH-CONDITIONS** (code 82f79b9d) | **C-TL1 (BLOCKER before --run)**: registrar wording bracket (D-2); C-TL2 bracket TT-R1 / TT-R4; heavy process, never beside a construction or another heavy job (about 4.6 h) |
| SCALE-AGREE | **NOT READY** (code 86c9f0aa) | D-1: the deciding interval treats a 5 x 5 crossed seed design as 25 independent pairs; registrar bracket of Support (b)-(d) + code fix + delta review |

## Pins (LF of record; working tree is LF, so CRLF is a rendering only)

| file | blob (LF) | sha256-lf16 | sha256-crlf16 | match commit msg |
|---|---|---|---|---|
| zc_common.py | c912dccf | 8fe96303de21504e | 7892e4331d16dc8c | yes |
| site_support.py | 4612345c | 3c049176bd4afebb | cd0fa610f54f42ae | yes |
| tree_like.py | 82f79b9d | ad23dd9ba2cf3f43 | 01b78434db6816e6 | yes |
| scale_agree.py | 86c9f0aa | 81024f6ca9bc85a2 | 19929c5a4de353dd | yes |

`git hash-object` = `git rev-parse HEAD:<path>` for all four; worktree clean.

## Per-claim table (deciding paths)

| # | claim | builder | reviewer | status | sev |
|---|---|---|---|---|---|
| 1 | SS deciding C (four trees' member sets) | 2,772 | 2,772 (independent script, immutable ro) | CONFIRMED | - |
| 2 | SS literal pool reading of C | 3,073 | 3,073; the 301 extra items are held by 0 / 1 / 2 / 3 trees: 15 / 54 / 129 / 103 | CONFIRMED | - |
| 3 | SS surviving sites | 264 (48 cert / 216 uncert), 4 roots skipped | 264 (48 / 216); skipped {p < 20: 4}; per tree cert/uncert 13/55, 11/52, 9/56, 15/53 | CONFIRMED | - |
| 4 | SS pool-reading roots become artefact sites | "p about 100, TBE 0" | root on C_pool 2,921-2,937 of 3,073 -> p 136-152 (survive the skip rule) | PARTLY (p is 136-152) | LOW |
| 5 | SS members on their pool's TRAIN side | all | 0 off-side in each of the 4 trees | CONFIRMED | - |
| 6 | SS Support (d)-(e) | SE 0.0365, MDE80 0.091 | 0.20 x sqrt(1/50+1/180) x sqrt(1.3) = 0.20 x 0.15986 x 1.1402 = 0.03646; 2.487 x 0.03646 = 0.0907; DESCRIPTIVE-ONLY at +0.08 holds | CONFIRMED (DEFF 1.3 declared, unmeasured: P-3) | - |
| 7 | TT identity precondition | max dev 2.2e-16 | 2.2e-16 on my dry-run; withinNodeCloud body identical in fixture blob 0b6e176f and HEAD blob 3401d4d7 (20-line diff empty) | CONFIRMED | - |
| 8 | TT census, pins | 9,870 / 13,487 TRAIN; 6 PIN OK | same | CONFIRMED | - |
| 9 | TT price | about 4.3 h | 4.6 h on my dry-run (machine shared with mutants) | PARTLY | LOW |
| 10 | TT positive reading means "hierarchy beyond covariance" | registration | a FLAT 27-cluster vMF mixture (no hierarchy; d 256, n 600) gives z(delta_rel) = -6.15 against the same null | REFUTED as worded (D-2) | HIGH |
| 11 | SA Support (b)-(d): DEFF 1.0, n_eff 25, SE 0.004 | registration | 25 pairs = 5 qwen3 seeds x 5 gemma seeds, crossed; n_eff is between 5 and 25; at n_eff 5: SE 0.02/sqrt(5) = 0.0089, MDE80 2.8 x 0.0089 = 0.025 (< 0.04, so SCOREABLE survives) | REFUTED (source of DEFF) | HIGH |
| 12 | SA MMLU common texts | 11,753 (vs 11,687 planned) | 11,753 (EVAL 3,524 / GATE 1,175 / TRAIN 7,054), descriptive | CONFIRMED | - |
| 13 | selftests | 9 / 57 / 32 / 27 OK | 9 / 57 / **34** / 27 OK (rc 0) | CONFIRMED (tree_like count in msg is 32) | LOW |
| 14 | builder mutants | 70 / 70 killed | 7 + 24 + 21 + 18 = 70 / 70 killed, 0 SURVIVED (grep -c) | CONFIRMED | - |
| 15 | no write to any DB; nothing written by dry-runs | yes | `stat` of 18 DB files (incl. -wal / -shm) identical before / after all dry-runs; 0 outcome dirs on E: | CONFIRMED | - |
| 16 | write-once | pre-check + mode x + SHA256SUMS | code read; M17 / T15 / S11 killed in my re-run | CONFIRMED | - |

Every scored statistic is null-relative: SB1 against a within-stratum permutation null, SB2 against random subsets of C,
TL0 / TL1 as z against the moment-matched Gaussian null (control against its own null), SC1 against the q4-vs-q8 normaliser.
MMLU-Pro SCALE-AGREE curves are RAW (no q8 copy exists), labelled descriptive. All DBs are read through staged copies on E:
(`zc_common.stage_db`, copy hashed before the checkpoint; source stat compared around the copy).

## Rulings on the builder's readings

- **SS-R1 ACCEPTED**: C = the intersection of the four trees' member sets (2,772) is of record. The literal pool reading
  (3,073) adds 301 TRAIN texts that at least one tree never placed (15 placed by none); every S of a tree that misses them
  is penalised, and the four roots survive as {placed, unplaced} artefact sites (p 136-152). Same definition as
  anchor_free_redraw (d) (L36: "the intersection of their member id sets"). Bracket must say that this reading decides P1
  (2,772 in [1,500, 3,000] HELD; 3,073 would be FAILED); both are printed.
- **SA-R3 ACCEPTED**: native is deciding (TL1's convention; DATA OBJECTS lists native and 256), 256-d printed beside.
  Bracket must also note that the label-side counterpart (GOLD-LEVEL-EMB EMBEDDER, prog L23377) compared qwen3 at 1024,
  a width SC1 does not print: the "counterpart" is not width-matched (D-9).
- **TT-R1 ACCEPTED**: the stored outputs of the compiled Kotlin method (mix_lrt_site blob e2d28a73, JVM_FIXTURE, two
  synthetic sites, class compiled from blob 0b6e176f) meet "validated against the Kotlin generator on one site". The
  generator is linear in the centred rows and blind to the data, so a synthetic site tests identity as well as a real one,
  and the method body is unchanged at HEAD (row 7). No new JVM run is needed. Bracket: "two JVM-fixture sites" in place of
  "one site".
- Readings needing a registrar bracket before `--run` (deciding path): SS-R1, SS-R2 (quintiles on |S|), SS-R4 (one-sided,
  certified higher: the registration does not state the direction; it is the only reading coherent with "G > 0 AND p <=
  0.05"), TT-R1, TT-R4 (control scales fixed pre-data), SA-R1 (TRAIN rows only, not the 57,350 texts), SA-R3, SA-R5 (den =
  mean over the 25 q4-q8 pairs). **SA-R4 (t(24) interval) REJECTED**: see D-1. Descriptive readings SS-R3, TT-R2, TT-R3
  (Khrulkov = max four-point / diam), TT-R5, SA-R2 confirmed as built; a one-line registrar note is enough.

## Defects

- **D-1 (HIGH, SCALE-AGREE, blocks READY).** The 25 slopes come from a crossed 5 x 5 design: pair (s, t) shares qwen3
  seed s with four other pairs and gemma seed t with four others, and the q4 seed s also enters den(k). The t(24)
  interval `mean +/- T24 x SD / 5` treats them as independent. When seed main effects dominate, the variance of the mean
  is understated up to 5x (SE up to 2.24x too small), and the deciding clause "interval wholly below 0" is
  anti-conservative. Registration Support (b) "DEFF 1.0 (seed pairs independent given texts)" is false by construction.
  Fix: registrar bracket of (b)-(d) (n_eff between 5 and 25; worst-case SE 0.0089, MDE80 0.025, still SCOREABLE at
  -0.04). Deciding interval: a seed bootstrap that resamples the 5 qwen3 seeds (numerator and den together), the 5 q8
  seeds and the 5 gemma seeds independently with replacement (B 2,000, fixed seed, percentile 95%), or the crossed-ANOVA
  SE (MS_A + MS_B - MS_E) / 25 with t(4). t(24) printed beside. Then a delta review with one mutant that reverts to t(24).
- **D-2 (HIGH, TREE-LIKE, C-TL1).** z(delta_rel) < -2 against the Gaussian null does not separate hierarchy from flat
  clustering: a star of clusters is already close to 0-hyperbolic. My synthetic flat 27-cluster mixture reads z = -6.15,
  and MASSIVE / CLINC are known to cluster. TL1 TREE-LIKE is therefore near-certain and cannot carry "hierarchy beyond its
  covariance" or the P3 / D6 hierarchy wording. The F-TL direction (NOT-TREE-LIKE) stays sound. Fix, pre-data (one of):
  (a) wording bracket: TREE-LIKE = "Gromov-tree-like relative to the Gaussian null; a flat cluster structure qualifies;
  no hierarchy claim"; no code change, READY stands on 82f79b9d; or (b) add a descriptive flat control (27-component
  1-level vMF mixture, the same kappa rule, its own null) beside TL0, printed, followed by a delta review. A criterion
  change (TREE-LIKE requires z below the flat control) is the author's / registrar's call.
- **D-3 (MEDIUM, SITE-SUPPORT).** TBE(s) scores the recurrence of node s's own cluster, which the PARENT's split creates.
  cert_site_p95 certifies s's split into children (CERT-ALIGN-SIZE's Y is the children's NMI). The registration and the
  record's (d) convention both use the node set, so the code is faithful. Fix: bracket the word ("the certified site's
  own cluster recurs"); post-run duty P-1.
- **D-4 (MEDIUM, SITE-SUPPORT).** The registered permutation pools the four trees within depth x size strata, so the null
  does not hold the tree fixed (CERT-ALIGN-SIZE used tree x size). Per-tree certification rates on the survivors are
  0.19 / 0.17 / 0.14 / 0.22. Post-run duty P-2.
- D-5 (LOW, TREE-LIKE): a 4.6 h single process with no checkpoint; a crash loses the run (nothing is written early, so
  write-once is not at risk). Schedule it alone.
- D-6 (LOW): the commit message gives the tree_like selftest as 32 checks; the code pins and prints 34.
- D-7 (LOW): SS-R1 text says "p about 100"; it is 136-152 (row 4).
- D-8 (LOW, descriptive arms): embeddings_cache.db carries no pin (sha256 printed: b0e88d3a6e207bc0 at this review). It is
  rewritten by constructions, so the --mmlu arms must print it again and run outside any construction window.
- D-9 (LOW, SCALE-AGREE): the SC1 widths are not width-matched to F-GL (qwen3 1024); see SA-R3.
- D-10 (LOW, SITE-SUPPORT): SB2 (Lemoine's random expectation) is a weak bar; RECURS is expected. The outcome already
  prints the count of sites above their own p97.5; quote SB2 with that count.

## Post-run duties (SITE-SUPPORT reviewer)

- P-1: compute children-TBE (mean TBE of s's children on C, same skip rules) and its stratified G beside the registered G,
  descriptive; flag if the sign differs.
- P-2: recompute G and p within tree x depth x size strata; flag if the SB1 word would change.
- P-3: measure DEFF from the cache's own clustering (cluster = tree x depth-1 subtree; between-cluster ICC of TBE) and
  print n_eff and MDE80 beside G, against the declared 1.3.

## Own mutants (8; all on deciding paths, all decisive; harness `zc_common.run_mutants`, sandboxed)

R1 TBE denominator p for p-1: killed. R2 SB2 subsets with replacement: killed. R3 certified flag inverted in G: killed.
R4 TL1 counted on z(mean delta): killed. R5 control kappa from 2 x theta3 (weaker gate): killed. R6 null from uncentred
rows: killed. R7 AMI average_method max: killed. R8 normaliser from the diagonal q4-q8 pairs only: killed. 8 / 8.

## Commands

```
W=.claude/worktrees/zero-call-trio; D=Z:/FAC/TUBerlin/THESIS/TaxoArena
git hash-object $W/tools/analysis/<f>.py ; git rev-parse zero-call-trio:tools/analysis/<f>.py      # pins (4 files)
python E:/TaxoArena_tmp/rv_trio/ss_indep.py                         # rows 1-5: |C| 2772 / 3073, 264 (48/216), roots p 136-152
python $W/tools/analysis/<f>.py --selftest                          # 9 / 57 / 34 / 27 OK, rc 0
python $W/tools/analysis/<f>.py --mutants                           # 7/7, 24/24, 21/21, 18/18; grep -c SURVIVED = 0 each
python E:/TaxoArena_tmp/rv_trio/my_mutants.py                       # R1-R8 8/8 killed
python $W/tools/analysis/site_support.py --dry-run --data-root $D   # pool line OK; |C| 2772; 264 sites; strata counts
python $W/tools/analysis/tree_like.py --dry-run [--mmlu] --data-root $D   # identity 2.2e-16; 4.6 h; mmlu 7,054 texts, 0.9 h
python $W/tools/analysis/scale_agree.py --dry-run [--mmlu] --data-root $D # pins OK; 0.6 h; mmlu 11,753, 0.2 h
python E:/TaxoArena_tmp/rv_trio/flat_ctrl.py                        # D-2: flat 27-cluster mixture z(delta_rel) -6.15
stat -c '%n %s %Y' <18 DB files> before/after; diff -> identical    # row 15
git cat-file -p 0b6e176f | awk '/private fun withinNodeCloud/,/^    }$/' vs 3401d4d7 -> identical (20 lines)   # row 7
```

## Run commands (after the registrar's brackets; from main after the merge, default data root)

```
python tools/analysis/site_support.py --run          # pool slot; no construction / site null running
python tools/analysis/tree_like.py --run             # after C-TL1; alone (heavy, about 4.6 h)
python tools/analysis/tree_like.py --run --mmlu      # descriptive; pool slot
python tools/analysis/scale_agree.py --run           # ONLY after D-1 is fixed and delta-reviewed
```

## Delta review 2026-10-04: SCALE-AGREE D-1 fix (tip 3374d4f9; registrar brackets 5312852a on main)

**Verdict: SCALE-AGREE READY** (code blob 92131d5b). Condition P-SA1 is post-run. No new registrar bracket is owed: the
fix implements the 5312852a bracket as written (seed bootstrap, B 2,000, fixed seed, percentile; t(4) / t(24) descriptive).

Scope: `git diff 98af68f9 3374d4f9 -- tools/analysis/` touches scale_agree.py only (+151 / -30). site_support, tree_like and
zc_common are byte-identical to the blobs reviewed above (`--stat` empty), so the earlier CONFIRMED rows stand. The
branch was rebuilt on main (98af68f9 -> ece82f30); `git diff --stat ece82f30 3374d4f9` = scale_agree.py only.

| # | check | reviewer | status |
|---|---|---|---|
| 1 | resampling unit matches the crossed design | `seed_boot`: per draw, a (qwen3), b (gemma), c (q8) are each `randint(0,5,5)`, drawn independently; numerator `A[k, a_i, b_j]`, den `Nm[k, a_i, c_j]`, so the qwen3 seeds are tied across numerator and den; the slope of the mean normalised curve (= mean of the per-pair slopes, since den is common) | CONFIRMED |
| 2 | no other decision path uses t(24) | `decreases(` is called once, in `sc1_corpus`, with `bhi`; the 256-d alternative prints `bhi`; P1 uses the mean; `hi` (t(24)) appears only in the printed beside-intervals (L342, L494). grep of `"hi"` / `decreases(` / `T24` on the blob: 1 decision call | CONFIRMED |
| 3 | pins | `git hash-object` = `git rev-parse 3374d4f9:tools/analysis/scale_agree.py` = 92131d5b; sha256-lf16 d18bf94ea1bbffa2, sha256-crlf16 952970538193c3ea (this worktree checkout is CRLF; the LF blob is of record); matches the commit message | CONFIRMED |
| 4 | bracket text = code | 5312852a SA-R4 bracket: "qwen3 seeds (numerator and den together), q8, gemma independently, B 2,000, fixed seed, percentile" = BOOT_B 2000, BOOT_SEED 20261004, percentiles [2.5, 97.5] | CONFIRMED |
| 5 | selftest | 33 / 33 OK (rc 0) | CONFIRMED |
| 6 | builder mutants | 26 / 26 killed; 0 SURVIVED, 0 NOT APPLIED (grep -c) | CONFIRMED |

Own mutants (3): X1 gemma seeds tied to the qwen3 draw (pairs resampled, not crossed): killed. X3 bootstrap curve not
divided by den*: killed. **X2 decision reads the crossed-ANOVA bound `ahi` instead of `bhi`: SURVIVED.** No fixture puts
the two bounds on opposite sides of 0, so the selftest would not notice a swap to the other (descriptive) interval.

- DD-1 (LOW, post-run P-SA1): from the printed SC1 lines, the post-run reviewer confirms that each corpus's
  DECREASES / does-not-decrease word follows `rho <= -0.7 AND bootstrap upper < 0`, not the ANOVA or t(24) bound. A
  fixture with bootstrap hi < 0 < ANOVA hi would close X2. That is optional, not a READY condition, because the word is
  checkable from printed numbers.
- DD-2 (LOW, disclosure): with only 5 levels per factor, the percentile bootstrap shrinks each factor's variance by about
  (n-1)/n = 0.8 (SE about 0.89x). The crossed-ANOVA t(4) interval printed beside is the conservative check. Quote it if
  the two intervals disagree in sign.

```
git diff --stat 98af68f9 3374d4f9 -- tools/analysis/ ; git diff 98af68f9 3374d4f9 -- tools/analysis/scale_agree.py
git hash-object $W/tools/analysis/scale_agree.py ; git rev-parse 3374d4f9:tools/analysis/scale_agree.py      # 92131d5b
python $W/tools/analysis/scale_agree.py --selftest      # 33 OK
python $W/tools/analysis/scale_agree.py --mutants       # 26/26; grep -c SURVIVED 0
python E:/TaxoArena_tmp/rv_trio/my_mu_delta.py          # X1 killed, X2 SURVIVED, X3 killed
```

Run command (after merging scale_agree.py blob 92131d5b; no pool read): `python tools/analysis/scale_agree.py --run`
(the descriptive `--run --mmlu` is a pool reader: run it in a pool slot).
