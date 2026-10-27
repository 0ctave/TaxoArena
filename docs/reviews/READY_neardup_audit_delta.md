# Delta READY review: NEARDUP-AUDIT (adversarial reviewer, 2026-10-04; zero calls)

Delta: `git diff d6e8038f..f7502b80` on branch `neardup-audit`. One file changed (`--name-only | wc -l` = 1):
`tools/analysis/neardup_audit.py`, +82/-17, now blob:4122ba72 / sha256-lf16:19703e43d4ab6dc2 /
sha256-crlf16:4ba2a8971f5f764d (LF of record; `git ls-files --eol` = i/lf w/lf; the dry-run prints the same pins).
Prior review: `docs/reviews/READY_neardup_audit.md` (blob 2c21f715). Its CONFIRMED rows on code this delta does not touch
(positives 70/70, tiers, denominators, hygiene, write-once, loaders) are cited, not re-derived. Registrar's CP bracket:
ec9c0966, prog L24172-L24178.

## VERDICT: READY (delta). C-1..C-4 closed. C-5 (O4: the 512 slice is never exercised by the selftest; check the
## PIN line "sliced 512") and C-6 (SCOREABLE iff n_dec >= 47) still bind the post-run review.

Launch (plain form), from the worktree:
`TAXOARENA_DATA_ROOT=Z:/FAC/TUBerlin/THESIS/TaxoArena python tools/analysis/neardup_audit.py --run`
(after the merge, from main: `python tools/analysis/neardup_audit.py --run`). `E:/TaxoArena_backup_2026-10-04_neardup_audit`
does not exist now (`ls -d` fails).

## Per-claim table

| # | claim | reviewer check | status | sev |
|---|---|---|---|---|
| C-2a | CP implementation | `cp_upper(x, n)` = `beta.ppf(0.975, x+1, n-x)`, 1 at x = n: the exact two-sided 95% upper bound. Closed form 1 - 0.025^(1/n) agrees to 4 dp at x = 0 (n 30/37/46/70: 0.1157/0.0949/0.0771/0.0513); Beta(0.975; 4, 37) = 0.2039 (3/40), Beta(0.975; 4, 67) = 0.1202 (3/70). n = the PLAIN-flagged pairs (`flag.sum()`), not all positives (D3 killed) | CONFIRMED | - |
| C-2b | the switch fires only on a zero-width bootstrap | `degenerate = hi == lo`; `hi_decide = cp_hi if degenerate else hi`. Sweep over singleton clusters (this object: Kish m 1.000), n 37..70, k 0..n: zero width in exactly 68 cases = k in {0, n}, 0 cases elsewhere. At k = n the point is 1 > 0.10, so the verdict is LOSES whichever bound is used: the switch can only change the word at 0 misses | CONFIRMED | LOW (see N-1) |
| C-2c | the registrar's "word unchanged at n_dec >= 37" | max CP upper at 0 misses over n 37..70 = 0.0949 <= 0.10, so BLOCKS-WELL under either bound; the n < 37 case (F7 0/30, CP 0.116, UNDETERMINED) cannot arise here (n_dec >= 37, B-5) | CONFIRMED | - |
| C-2d | CP printed beside, divergence named | "ND1 CLOPPER-PEARSON", "ND1 DECIDING UPPER BOUND", "bootstrap-only verdict / CP-upper verdict ... THE TWO DIFFER (named)" lines; FAILS-rule line uses `hi_decide` | CONFIRMED | - |
| C-1 | primary-leaf-only interval and verdict | same `cluster_boot` over the deciding EVAL ids on `~in_prim[flag]`; verdict uses CP when its own interval is degenerate (same rule); "R1-DEPENDENT" printed on a difference (F8: 6/51 = 0.118 LOSES vs ND1 BLOCKS-WELL) | CONFIRMED | - |
| C-3 | P3 scored on the registered unweighted fraction | `preds` P3 = `res["frac_unw"]`; EVAL-weighted printed as "R4 reading (descriptive)"; F6b pins 0.0200 HELD vs 0.1091 | CONFIRMED | - |
| C-4 | upper bound pinned to the digit | F3 3/40 asserts "[95% 0.000, 0.175]"; O1 (97.5 -> 95) now killed (3 FAIL) | CONFIRMED | - |
| S | selftest | 61 ok / 0 FAIL (`grep -c "^  FAIL "` = 0) under `python`; PASSED under `python -O` | CONFIRMED | - |
| MU | mutants | builder 26/26 reproduced as 24 reconstructions (M1-M11, M14, M16-M18 with M9 inverted; C2a, C2b, C2c, C1a, C1b) plus my prior decisive O1, O2, O3, O6: 24/24 killed. Own delta mutants D1-D3: 3/3 killed | CONFIRMED | - |
| H | regression of hygiene | dry-run on scratch copies: 70 pairs / 70 ids, EXACT 37 / SAME-OPTIONS 33 / STEM-ONLY 0, Kish m 1.000, SE 0.0204 (0.057), same as the reviewed blob; DB size + mtime unchanged (`cmp` equal); scratch removed (count of `ndrev`/`neardup_` under E:/TaxoArena_tmp = 0) | CONFIRMED | - |

## Own delta mutants (deciding paths)
- D1 `hi_decide = max(cp_hi, hi)` (CP decides whenever it is larger): killed (F3).
- D2 primary-only interval over ALL positives, not the PLAIN-flagged ones: killed (F1).
- D3 CP denominator = all positives (`len(pos)`): killed (F1 0/56 vs 0/46).

## Notes (no fix required before launch)
- N-1 (LOW) The bracket's wording is "DEGENERATE (0 misses)"; the code's test is zero width, which also holds at
  all-miss (k = n_dec). Same verdict (LOSES on the point), so the registrar may add "(or all misses; same word)" when the
  outcome is recorded.
- N-2 (LOW) CP is a pairs bound; the CP line prints the Kish m beside it ("valid as an exact bound only at Kish m 1.000").
  The post-run confirms m = 1.000 on the deciding pairs.
- The prior review's C-5 and C-6 stand (header).

## Commands (compact)
```
git -C .claude/worktrees/neardup-audit diff d6e8038f..f7502b80 --name-only | wc -l      # 1
git -C .claude/worktrees/neardup-audit hash-object tools/analysis/neardup_audit.py      # 4122ba72...
python tools/analysis/neardup_audit.py --selftest ; python -O ... --selftest              # 61 ok, 0 FAIL; PASSED
python -c "beta.ppf(0.975,x+1,n-x) vs 1-0.025**(1/n)"                                      # table in C-2a
sweep: cluster_boot(range(n), [1]*k+[0]*(n-k)) for n 37..70, k 0..n; count hi==lo off {0,n} # 0 (68 at {0,n})
harness.py on a scratch copy in E:/TaxoArena_tmp/ndrevd_* (removed): 27 mutants, 27 killed, file restored PASSED
stat size+mtime of the 3 DBs before/after TAXOARENA_DATA_ROOT=<main> ... --dry-run; cmp  # equal
```
