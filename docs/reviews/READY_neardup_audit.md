# READY review: NEARDUP-AUDIT (adversarial reviewer, 2026-10-04; zero calls)

Reviewed: branch `neardup-audit` tip d6e8038f (one file: `git show d6e8038f --name-only --format= | wc -l` = 1),
`tools/analysis/neardup_audit.py` blob:2c21f715 / sha256-lf16:18f45ff376dfc426 / sha256-crlf16:3f2cf7155904da4d
(LF of record; `git ls-files --eol` = i/lf w/lf, so the working tree is the LF rendering). Registration prog
L24169-L24181 `_as_of` fac3d50b. Imported pins verified by the script and by `git hash-object`: content_closure.py
1533cb5a, flat_mix_mmlu.py 555ae3ac, split_side.py 05224b5a, pool_guard.py 6521b51a.

## VERDICT: READY, with conditions C-1..C-6 (none blocks the launch; C-1..C-3 bind the post-run review)

Launch (plain form): from the worktree
`TAXOARENA_DATA_ROOT=Z:/FAC/TUBerlin/THESIS/TaxoArena python tools/analysis/neardup_audit.py --run`
(or after the merge, from the main checkout: `python tools/analysis/neardup_audit.py --run`). Before launch: the
registrar brackets B-1..B-5 below go in (pre-data); `E:/TaxoArena_backup_2026-10-04_neardup_audit` must still not exist.

## Per-claim table (deciding claims)

| # | claim | builder | reviewer (own command) | status | sev |
|---|---|---|---|---|---|
| 1 | positives (CK-CLOSE-v1 stem_key twins, EVAL x TRAIN members) | 70 pairs / 70 EVAL ids | 70 pairs / 70 EVAL ids / 70 distinct members (own script, `split_side.stem_key` directly, not `ck_key`) | CONFIRMED | - |
| 2 | tiers | EXACT 37 / SAME-OPTIONS 33 / STEM-ONLY 0 | 37 exact; the 33 non-exact are ALL norm-v1-equal texts (case/whitespace) whose option SET equals the EVAL row's in permuted order (ordered match 0, unordered 33); stem-only 0 | CONFIRMED (label: "same option set, order permuted") | LOW |
| 3 | denominators | EVAL 3,445; members 8,278; leaves 87 | 3,445 / 8,278 / 87; member listings sum 8,782 (499 members in >1 leaf, max 3) | CONFIRMED | - |
| 4 | power at 70 pairs | SE 0.0204, MDE80 0.057 | sqrt(0.03 x 0.97 x 1.000 / 70) = 0.02039, x2.8 = 0.0571; measured Kish m 1.000 (all 70 clusters size 1; dry-run line) | CONFIRMED | - |
| 4b | registered support | SE 0.0153, MDE80 0.043 (DEFF 1.2, n 150) | sqrt(0.0291 x 1.2 / 150) = 0.01526, MDE 0.0427; at declared 1.2 with n 70: 0.0223 / 0.0625 | CONFIRMED (arithmetic); n SHORT (B-1) | - |
| 5 | ND1 verdict rule | point > 0.10 LOSES; hi <= 0.10 BLOCKS-WELL; else UNDETERMINED | code L381-L386 matches the verbatim criterion; boundary mutants M1, M2, O2, O3 killed | CONFIRMED | - |
| 6 | TREE-BLOCK vs PLAIN | miss = PLAIN-flagged positive whose member is not listed in the EVAL item's filed leaf | `in_block = mem[pm, filed[pe]]` over `ps >= TAU`; M3, M4, M5, M6, O6 killed | CONFIRMED | - |
| 7 | R1 (multi-leaf in each block; primary-only sensitivity) | as docstring | implemented as written; 6 of the 70 positives' members are multi-leaf, so R1 vs primary-only can move BLOCK-LOSS by up to 6/70 = 0.086; the sensitivity prints a point only | PARTLY (C-1) | MEDIUM |
| 8 | R3 (refuse if no positive reaches cos 0.95) | refuse, nothing written | refusal at L468-L469 before any write; M16 killed. STRUCTURAL: the 37 EXACT twins share one text-keyed vector (cos 1), so n_dec is in [37, 70] and R3 cannot fire on this object | CONFIRMED | - |
| 9 | R4 (P3 = EVAL-weighted block size / 8,278) | reading "where the registration is silent" | the registration is not silent: its parenthetical is "mean leaf size / 8,278" = the UNWEIGHTED mean, 100.94 / 8,278 = 0.0122 (R1 listings); the script scores the EVAL-weighted value and prints the literal one without HELD/FAILED | PARTLY, SUBSTITUTION RISK (C-3) | MEDIUM |
| 10 | ND1 interval | percentile cluster bootstrap B 2,000 | correct as registered, but anti-conservative at this n: degenerate [0, 0] at 0 misses; at 3/70 hi = 0.100 (BLOCKS-WELL) vs Clopper-Pearson 0.120; at 1/47 hi 0.064 vs CP 0.113 (table below) | PARTLY (C-2) | MEDIUM |
| 11 | write-once to E: | mode 'x' + pre-checks; OUT_DIR on E: | `open(path, "x")`, existence refused in main() and write_outputs(); M10 killed; OUT_DIR absent now (`ls -d` fails) | CONFIRMED | - |
| 12 | hygiene: no write to DBs of record | copies to E:/TaxoArena_tmp, immutable reads | sha256 + size + mtime of the three DBs identical before/after the dry-run (`cmp` equal); no -wal/-journal present; scratch dir removed (`ls E:/TaxoArena_tmp | grep -c neardup_` = 0); `snapshots_frozen` occurs once in the file (docstring L27) | CONFIRMED | - |
| 13 | selftest | 56 asserts by value | 56 ok / 0 FAIL under `python` and `python -O` (`grep -c "^  FAIL "` = 0) | CONFIRMED | - |
| 14 | mutants | 20/20 killed | 15 builder mutants reproduced (M1-M11, M14, M16-M18): 15 killed (M16 by crash, rc 1). Own 7: 5 killed, 2 SURVIVED (O1, O4) | PARTLY (C-4, C-5) | LOW |

Bootstrap vs exact bound at singleton clusters (own script on `cluster_boot`, seed 20261004):

| n_dec | misses | point | boot 95% | ND1 | CP upper |
|---|---|---|---|---|---|
| 70 | 0 / 2 / 3 / 4 | 0 / .029 / .043 / .057 | [0,0] / [0,.071] / [0,.100] / [.014,.114] | BW / BW / BW / UND | .051 / .099 / .120 / .140 |
| 56 | 2 / 3 | .036 / .054 | [0,.089] / [0,.125] | BW / UND | .123 / .149 |
| 47 | 1 / 2 | .021 / .043 | [0,.064] / [0,.106] | BW / UND | .113 / .145 |

## Own mutants (deciding paths)
- O1 upper percentile 97.5 -> 95 (a 90% interval decides): SURVIVED; decisive (the upper bound decides ND1).
- O2 BLOCKS-WELL tested on lo: killed. O3 LOSES tested on hi: killed. O5 unit-norm removed: killed.
- O4 DIM 512 -> 4096 (R4096 instead of R512): SURVIVED; not decisive (fixtures use vectors of length dim, so the
  slice is never exercised; the run's PIN line prints "sliced <DIM>").
- O6 tree block on vmfMu filing: killed. O7 P2 scored on tree recall: killed.
- Builder M12, M13, M15, M19, M20 not re-run (non-deciding: seed list, line presence, P2 bound, assemble, tier).

## Conditions / defects (each with its fix)
- C-1 (MEDIUM) R1 sensitivity carries a point only. Fix (post-run, no code change needed): the post-run reviewer
  recomputes the primary-only BLOCK-LOSS with the same cluster bootstrap and verdict; if it differs from the R1
  verdict, the outcome is reported "R1-dependent" in the record. (Optional code fix before launch: print the
  primary-only interval and verdict; that is a new blob and needs a delta review.)
- C-2 (MEDIUM) percentile bootstrap degenerate/anti-conservative at n_dec 37-70 (table). The registered bootstrap
  stays deciding; the post-run prints the exact Clopper-Pearson upper bound beside (valid here: Kish m 1.000, every
  cluster size 1) and flags any verdict that differs. A 3/70 read (hi 0.100) is a knife edge and must be named.
- C-3 (MEDIUM) R4 vs the registered parenthetical "mean leaf size / 8,278". Fix: registrar bracket (B-3) records R4
  as the builder's reading BEFORE the run; the post-run reports P3 under both, the literal (unweighted 0.0122,
  in [0.01, 0.04]) labelled the registered statistic and the EVAL-weighted labelled "R4 reading". Neither is deciding.
- C-4 (LOW) O1 survives: no selftest pins the interval's upper bound to the digit. Fix: the post-run reviewer
  recomputes the ND1 interval independently to the digit (required anyway); optionally add an assertion on the F3
  upper bound in a later blob.
- C-5 (LOW) O4 survives: the 512 slice is never exercised by the selftest. Fix: the post-run checks the outcome's
  PIN line reads "full dim 4096, sliced 512" (the dry-run printed exactly that).
- C-6 (support, binds the post-run) n_dec is in [37, 70]. SCOREABLE iff 2.8 x sqrt(0.0291 / n_dec) <= 0.07, i.e.
  n_dec >= 47 at the measured DEFF 1.000 (>= 56 at the declared 1.2). The script prints the realised SE and MDE
  but no SCOREABLE / DESCRIPTIVE-ONLY word: the post-run applies this line and prints n_eff and MDE beside ND1.

## Registrar brackets needed (pre-data, insertion only)
- B-1 SHORTFALL: positives 70 pairs over 70 EVAL ids (70 distinct members), against the planning 150 pairs / 135
  ids. Realised support at n 70: SE 0.0204, MDE80 0.057 (measured DEFF 1.000), vs registered 0.0153 / 0.043; at the
  declared 1.2: 0.0223 / 0.0625. Still SCOREABLE at n_dec 70 (gap 0.07); see C-6 for n_dec < 70.
- B-2 TIERS: the registration's cumulative "exact (37 ids), norm-v1 (70 ids), stem-only" is implemented as the
  disjoint EXACT 37 / SAME-OPTIONS 33 / STEM-ONLY 0. The STEM-ONLY tier is EMPTY: every non-exact twin is a
  case/whitespace variant carrying the same option set in permuted order, so P2's stated mechanism ("stem-only
  variants fall below 0.95") has no object on this pool.
- B-3 READINGS fixed before data (docstring of blob 2c21f715): R1 (multi-leaf members in each listed block;
  primary-only = sensitivity), R2 (unweighted unit mean of listed members), R3 (refusal if no positive is
  PLAIN-flagged), R4 (P3 EVAL-weighted; the literal unweighted value printed beside, C-3), R5, R6.
- B-4 DEFF: declared 1.2 (pilot assumption); measured from the object's own cluster sizes = 1.000 (all clusters
  size 1; dry-run Kish line). The measured value is of record (R6).
- B-5 STRUCTURE: the 37 EXACT twins share a text-keyed vector (cos 1), so n_dec >= 37 and R3 cannot fire; ND1
  measures, for the twins, whether a member files (flatLeaf on member means) into a leaf that lists it, as
  registration SUPPORT (g) states.

## Commands (compact)
```
git -C .claude/worktrees/neardup-audit hash-object tools/analysis/{neardup_audit,content_closure,flat_mix_mmlu,split_side,pool_guard}.py
git -C .claude/worktrees/neardup-audit ls-files --eol tools/analysis/neardup_audit.py      # i/lf w/lf
python tools/analysis/neardup_audit.py --selftest  |  python -O ... --selftest              # 56 ok, 0 FAIL, both
stat + sha256sum of the 3 DBs > before.txt; TAXOARENA_DATA_ROOT=<main> python ... --dry-run; same > after.txt; cmp  # equal
dry-run: 70 pairs / 70 ids; EXACT 37, SAME-OPTIONS 33, STEM-ONLY 0; Kish m 1.000; SE 0.0204 (0.057); vectors 11,686, dim 4096 sliced 512
indep.py (scratchpad; mode=ro&immutable=1; split_side.stem_key): pairs 70, ids 70, members 70; tiers EXACT 37,
  same-set-permuted 33, ordered 0, stem-only 0; multi-leaf 499 (6 among the positives' members); leaf sizes sum 8,782,
  mean 100.94, min 55, max 420; unweighted mean/8,278 0.0122; SE/MDE at (1.2,150) (1.0,70) (1.2,70)
harness.py on a scratch copy under E:/TaxoArena_tmp/ndrev_* (removed; count 0): 22 mutants, 20 killed, O1 O4 survived
cluster_boot vs scipy beta.ppf(0.975, k+1, n-k) for n in 37/47/56/70, k 0-5 (table above)
```
