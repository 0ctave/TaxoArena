# READY (delta) — COVERAGE-AUDIT: coverage_audit.py after the D-1 fix

Reviewer: adversarial-reviewer, 2026-10-04. Zero calls, no key, no statistic computed. Delta review of
`git diff aa5ddf04 3754315b -- tools/analysis/coverage_audit.py` (194 changed lines) plus regression. Prior review:
`READY_cell_flips_coverage.md` (NOT READY on D-1; everything else there CONFIRMED and not re-derived here). Brackets: B-4 and B-5 / B-1
in prog L24160 / L24162 (098c3f84; B-5 ruling 0af808b2, flagged for the author at checkpoint H).

Pins: coverage_audit.py **blob:75f65a27a2d2346f06e8411fd4fb02fdaa8130d4** (LF; sha256-lf16 e4c588f35fb80c3d = the worktree bytes, so
there is no CRLF variant in the worktree; the main checkout's CRLF rendering must be named beside it at the run). Unchanged:
union_cells_io.py 92a04543, union_af_route.py bf3f17db. cell_flips.py e485af5e (test-only `_RNG` hook + `st_seeds`, behaviour
identical) is NOT merged; the run blob of record stays 998d39a7.

## Verdict: READY

No conditions on the code. Before `--run`, the run-operator prints the main checkout's pin of coverage_audit.py (blob 75f65a27).

## Per-claim table

| # | claim | mine | verdict | sev |
|---|---|---|---|---|
| 1 | Mirrored K_0 decides CV1 (B-4) | `cells["K_0"] = mirrored(...)` on EVAL AND TRAIN; IFEVAL rows → its one centroid by source (refuses unless exactly 1); every other row argmax over the centroids with the one-cell one masked to −inf. This is B-4's text. `diff = f_AF − f_K0` uses the mirrored arm; the CV1 header names it. V32 / V33 / V34 / V35 killed; my S3 (CV1 read from the nearest-of-all D) killed | CONFIRMED | — |
| 2 | One-cell set read from the object, not hard-coded | `man["single"]` of the sha-pinned manifest 53021e26: `{'IFEVAL': {... 'cell': 'IFEVAL:n00000001', 'source': 'IFEVAL'}}`; ksrc IFEVAL 1. With an absent key the mirror would silently equal nearest-of-all (it prints "none"); the pin prevents that on the real object, and my S1 (key ignored) is killed by e2e | CONFIRMED | LOW (note) |
| 3 | Beside lines descriptive | D_X nearest-of-all (+ interval and the word its rule would give) and D_X without IFEVAL for both filings; 5,745 items on the real set (5,907 − 162); none feeds `cv1`, F-CV or rule 8. V36 / V39 killed; my S2 (D_all from the mirrored arm) killed | CONFIRMED | — |
| 4 | CV-R2 / CV-R3 (B-5) | dominance from the TRAIN rows filed by each arm's own rule, including the mirrored rule for "K_0" (V35 killed); ties and empties unchanged (V01 / V02) | CONFIRMED | — |
| 5 | Seeds pinned (B-1) | e2e oracle redraws default_rng(20261004) component and (20261005) i.i.d. streams by loops and matches the printed intervals and DEFF; asserts the RP_ seeds; V37 / V38 killed (my R3 class) | CONFIRMED | — |
| 6 | Selftest | 5 / 5 (re-run) | CONFIRMED | — |
| 7 | Mutants | 44 / 44 KILLED, control survived (re-run); own S1-S3 3 / 3 KILLED | CONFIRMED | — |
| 8 | Dry-run read-only | rc 0; POOL line first (rc 0); manifest = pin; eval_view e35b7518 before = after; 5,907 / 5,404; per-member n unchanged; mtimes/sizes of policy, cell TSVs, bundle, embeddings_cache.db, multicorpus_cache_v1.db equal before/after; no coverage_audit output under experiment_results/archv2; no coverage_audit_* left in E:/TaxoArena_tmp | CONFIRMED | — |
| 9 | Fixture discriminates | asserts D(mirrored) ≠ D(nearest of all), X_IFEVAL differs, D_ex ≠ D; 12 MATH TRAIN rows near IFEVAL make nearest-of-all dominance differ | CONFIRMED | — |

## Own mutants (delta; 3)

S1 `single = []` (mirror vacuous): KILLED, decisive. S2 D_all from the mirrored arm: KILLED, non-decisive (a beside line). S3 CV1 word
from D_all: KILLED, decisive.

## Notes for the registrar and post-run reviewer

- The outcome's X_m table and occupancy TSV now carry four arms ("K_0" = mirrored, "K_0 all" = registered nearest of all). Words about
  CV1 quote the mirrored D_X; the nearest-of-all and IFEVAL-excluded values are descriptive (B-4), as in UNION-AF-ROUTE Q1.
- B-5 (CV-R2) is the orchestrator's ruling, pending the author at checkpoint H; if the author reverses it, the result is re-read under
  construction-member dominance, whose X is printed per arm (descriptive, no interval).
- Support unchanged (DEFF 1.102 transported; SE 0.00432; TOST reach 0.0093), re-derived in the prior review. The post-run must re-measure
  DEFF on the mirrored D_X.

## Plain-form run (run-operator, from the MAIN checkout after the merge)

```
python tools/analysis/coverage_audit.py --dry-run
python tools/analysis/coverage_audit.py --run
```

## Commands

```
git diff aa5ddf04 3754315b -- tools/analysis/coverage_audit.py ; git rev-parse 3754315b:tools/analysis/coverage_audit.py   # 75f65a27
git show 3754315b:tools/analysis/coverage_audit.py | sha256sum                    # e4c588f35fb80c3d = worktree bytes
python tools/analysis/coverage_audit.py --selftest      # 5/5
python tools/analysis/coverage_audit.py --mutants       # 44/44, control survived
python scratchpad/rvcf/own_mut2.py                      # S1-S3 3/3 killed
python tools/analysis/coverage_audit.py --dry-run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena   # rc 0
python -c "json.load(inputs_manifest.json)['single']"   # IFEVAL, cell IFEVAL:n00000001
stat before/after (diff empty); ls E:/TaxoArena_tmp | grep -c coverage_audit_   # 0
```
