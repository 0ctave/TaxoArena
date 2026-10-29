# POSTRUN review: GUARDS-FRESH-TAU (rule-A leakage guards R7/R8 in fresh-rules, half-leg fixture V5 in tau-grid; EXPLORATORY engineering, WORK rows only)

Authority: D-2026-10-27-2 (TaxoArena 2e2513a5, `docs/agents/author_decisions/2026-10-27.md`, item 0 of the main session's
reading). Reviewer: adversarial reviewer, 2026-10-28. Zero LLM calls. Vault/reserved reads 0: I loaded no response
matrix (inputs: splits.json, `_work/*.pkl` with `model_responses_read False`, the recorded part JSON/npz, the selftest
fixtures). One selftest at a time (+ its own 2-worker pool briefly), BLAS 1; read-only helper scripts of seconds.
Reviewed: benchzoom branch `guards-fresh-tau` (local; `git branch -r --contains` 0), 35b2724..61b149c.
- Plan 6d671ca (15:39:23) -> code f483194 (15:57:45) -> records 61b149c (23:48:05). First output `mutants/base.json`
  16:06:20, last `SHA256SUMS` 23:29:22. Before the plan: base selftests (15:32) and `probe_leaves.py` (15:35), both on the
  synthetic fixture only. No statistic on responses came before the plan.
- Code of record f483194 (LF; 0 CR bytes in every file, so there is no CRLF rendering): fresh-rules `blob:c872b725`
  (sha256-lf16:0a12ba74203faa6c), tau-grid `blob:50b0a182` (a3c0af9a9c6ae434), runner `blob:16b46824` (ed2e310a044d5cd1),
  specs `blob:5e9d44f3` (778f56767b899835). Every campaign result carries these blobs; base results carry
  `blob:f525a403` / `blob:601416f5` (= `git rev-parse 35b2724:<path>`).
- Tip 61b149c (what a merge carries): fresh-rules `blob:aa4ea09c` (3c466e9071c5f536), tau-grid `blob:6ae91e19`
  (8f6835e6660d5557), runner `blob:dc7035a1` (69940b36c3050fad), test `blob:85cbac01` (a4d6407d01b7f564), plan
  `blob:4f82e58b` (4ada85818253d067). f483194 -> 61b149c adds +44 / +21 / +38 lines and deletes 0. The ASTs of all
  169 / 109 / 90 top-level statements are identical with docstrings stripped, so the tip runs the code of record.
- Outputs `E:/benchzoom_demo/followups/guards-fresh-tau`: `sha256sum -c SHA256SUMS` 11/11. Backup: 12/12, and its
  SHA256SUMS is `cmp`-identical to the original.

## Verdict

**GUARDS CONFIRMED AS SPECIFIED (exploratory engineering); MERGEABLE (merge_ok YES).** H2 is closed only for the named
mutants.
- **Rule words after review:**
  - W-H2: H2 CLOSED. This is CONFIRMED under the pre-specified rule. **In substance it is PARTLY closed**: the same leak
    moved to the point of use survives (M1, M2; H1 below).
  - W-C2: C2 CLOSED.
  - W-INERT: INERT ON THE RECORD.
  - W-SELFTEST: SELFTESTS PASS.
  - OVERALL: GUARDS READY FOR REVIEW. Reviewed; it stands with the H1 qualifier.
- No BLOCKER for the merge. The branch changes examples, docs and one test only. No `src/` change. No analyze, statistic
  or word path changes. The guards only add refusals.
- H1 (HIGH) and M-1 (MEDIUM) are **conditions before any registered reuse of the rule-A code** (BZ-AXIS-CONFIRM-FRESH,
  rule A as its secondary readout).

## Deciding claims

| # | claim (builder) | my check / number | result | sev |
|---|---|---|---|---|
| 1 | the branch touches only its own files; no `src/` change, so `docs/execution_graph.md` is unchanged | `git diff --name-only 35b2724..61b149c`: `wc -l` 8, `grep -c ^src/` 0. Three docs: numstat x/0 (insertion only). The 4 deleted lines in fresh-rules.py are 2 code lines that became guarded, 1 docstring line and the block count 9->10. execution_graph.md names neither script (`grep -c` 0) | CONFIRMED | - |
| 2 | the plan precedes every statistic | git times against output mtimes (header). Plan diff 6d671ca..61b149c: +37/-0 ([P1] only) | CONFIRMED | - |
| 3 | base reproduction: R7, R8, V5 SURVIVE; both controls pass | my own harness (literal strings of the two prior reviewers' runners, sandbox copies, serial): base fresh control 9/9, R7 SURVIVED 9/9, R8 SURVIVED 9/9; base tau control 66 PASS, V5 SURVIVED 66/0 | CONFIRMED | - |
| 4 | at the new code R7, R8 and V5 are killed by the new checks | my harness at the tip: R7 killed, rc 1, "REFUSED [H2]: the pool parent's leaves are not the rule-A record's own leaves (630 of 630 ...)". R8 killed, "REFUSED [H2]: the rule-A build includes 270 fresh item(s)". V5 killed, 3 FAIL: "S5 word half straddle", "... reverse", the MAP rule line. Controls 10/10 and 69/0 | CONFIRMED | - |
| 5 | campaign counts fresh 122/122, tau 77/78 (X40 equivalent), guards 15/15 | Statuses re-derived from all 223 sandbox `out.log` + rc: 0 inconsistent, the same counts, survivors only tau X40. Specs vs the 4 original runners (by ast): 105 + 78 entries, 0 missing / extra / literal mismatch. Every old string occurs exactly once at the tip | CONFIRMED (from the logs; I re-ran only R7, R8, V5 and the controls) | - |
| 6 | dry check: 65 evaluations, 0 refusals; per split pool 2,064, fresh 885, A build 4,029, overlap 0; R7 control rows 1,883/1,690/1,559/1,573/1,867 of 2,064; R8 5/5 | Recomputed with pickle/numpy only, no fresh-rules code: every count equal to the digit. Also A fresh_ids = F_s (5/5), pool ⊂ A build (5/5), build ∪ F = B0 ids (5/5), sub25/sub50/fresh ∩ pool 0, 40 bootA resamples ∩ split-0 pool 0 (sizes 883-888). 7/7 input pins equal `SHA256SUMS_backup`; inputs unchanged (size, mtime, sha) | CONFIRMED (L-1: 5 of the 65 checks are tautological) | LOW |
| 7 | re-analysis: NEW = BASE byte for byte (6 texts); vs the recorded files 5 identical, fr summary 1 line (L35, the [P2] label of f3b16fb) | My loader (git-show modules at 35b2724 / 61b149c): 6/6 base = tip. vs recorded: 5 sha-equal; fr_summary 1 line, L35 "SD over splits" -> "split-seed mean of SE_cc in parentheses". Tip summary sha 8aad88873a92e18f equals the builder's sha_new. Same texts with an `h2_guard` key injected into every part. Recorded dirs unchanged | CONFIRMED | - |
| 8 | the analyze, statistic and word paths are untouched | AST base -> tip: fresh-rules changes only `build_record`, `pool_for`, `part_split`, `part_boot`, `selftest`, + 3 new guards; tau-grid changes only `selftest` | CONFIRMED | - |
| 9 | recorded SHA256SUMS 25 + 25 verify before and after | `sha256sum -c`: fresh-rules 19 + 6, tau-grid 10 + 15, all OK. 0 files under either recorded dir modified on 2026-10-27 or after (`find -newermt` 0) | CONFIRMED | - |
| 10 | selftests 10/10, 69/0, 12/12; suite 900 passed / 1 skipped / 7 deselected | Logs: 10/0, 69/0, 12/0. My controls: as row 4. `pytest tests/test_guards_fresh_tau.py tests/test_tau_grid.py`: 5 passed, 1 deselected (the slow one = my 10/10 control). Full suite read from the builder's log only (rc 0, 835 s, AST-identical code), not re-run | CONFIRMED / full suite PARTLY | LOW |
| 11 | existing behaviour is unchanged on the selftest fixtures | Base vs tip control sandboxes, all 29 shared build pickles and part JSONs compared field by field: equal except the script blob (meta) and timings. Tip adds only the `h2_guard` key, the S10 `world_leak` files and their log lines. tau-grid: 0 base lines missing at the tip; +323 lines = the two new fixtures | CONFIRMED | - |

## Own mutants (sandbox copies `E:/TaxoArena_tmp/review_guards-fresh-tau/mut/20261027T235430/<camp>_<key>_<id>`; tracked files never edited)

| id | change | result | decisive |
|---|---|---|---|
| R7 / R8 / V5 (base) | the prior reviewers' literal strings on 35b2724 | SURVIVED x3; controls pass | yes (discriminator) |
| R7 / R8 / V5 (tip) | the same strings at 61b149c | killed x3 by the new refusals / fixtures | yes |
| M1 | `part_split`: the guard checks `v0a_old`, but `pool_residuals` is passed B0's (fresh-text) leaves | **SURVIVED** (10/10). Not equivalent: NA\|L2+V0A per item moves up to 0.085 | yes (H1) |
| M2 | the same in `part_boot` (bootA / bootA2) | **SURVIVED**. Not equivalent: bootA G(N\|L2+V0) replicates move up to 4.08 | yes (H1) |
| M3 | rule-A scored cells V0A read from B0's leaves at the fresh rows | **SURVIVED**. Not equivalent: A:C1(V0) becomes B's; 270/270 cells differ | yes (M-1) |
| M4 | `build_record` builds on all items whatever `build_ids` says | killed ("REFUSED [H2]: the rule-A record's build includes 270 fresh item(s)") | yes |

## Defects (each with its fix)

- **H1 (HIGH; condition before any registered reuse of rule A).** G-POOL validates a variable, not the leaves that are
  actually used. `check_pool_parent(v0a_old, ...)` is called, and then `pool_residuals(..., v0a_old)` is called
  separately, so a leak at the use site passes (M1, M2). S10 never asserts what reached `pool_residuals`. The run of
  record is clean on this path: POSTRUN_FRESH-RULES-SIM row 5 rebuilt the pool from scratch, with max|diff| <= 9e-17 on
  NA and V0A\|L2+NA. Fix: in S10, spy on `pool_residuals` during `run_part("split0")`, `("bootA")` and `("bootA2")`.
  Assert that its leaves argument equals the A record's own leaf at every pool row. Have `check_pool_parent` return the
  validated leaves, and make that return value the only argument passed on. Re-run M1 and M2; both must be killed.
- **M-1 (MEDIUM; same condition).** Rule A's scored cells are not guarded (M3). This lies outside H2's named scope
  (build and pool), but it is the same class: fresh text deciding rule-A cells. The record is clean: in all 15 designs (5
  splits x phi 0.25/0.50/1.00) the recorded V0A and KA0-4 cells equal the A record's own `fresh_leaf` / `fresh_K` at the
  scored ids. B0's leaves match on only 16-221 of the rows, so this check discriminates. Fix: G-CELLS in `part_split`
  (V0A / KA = `cells_for(recA)` at the scored ids, refusing otherwise), plus an S10 check on the stored
  `phi*:cell:V0A`. Re-run M3; it must be killed.
- **L-1 (LOW).** "65 guard evaluations, 0 refusals" overstates the evidence. The 5 G-SCORED checks of `fresh` against
  the pool are true by construction (the pool is the complement of fresh). G-POOL clause (f) on the record compares the
  record's leaves with themselves. What carries information: G-BUILD x5, G-POOL (a)-(e) x5, sub25/sub50 x10, bootA x40,
  and the two negative controls. Fix: say this in the record line.
- **L-2 (LOW).** G8, G15 and G16 die by a KeyError crash, not by S10's own comparison: `h2_refuses` lets non-SystemExit
  exceptions escape, and `pool_for` is given an empty `res`. Fix: catch `Exception` in `h2_refuses` (return False), or
  pass a minimal non-empty `res`.
- **L-3 (LOW).** The code of W-H2 / W-C2 checks only "killed". The plan's W-H2 also requires P2's kill reasons. Not
  decisive here: P2 HELD, and my row 4 shows the reasons. Fix: AND `predictions()["P2"] == "HELD"` into both words.
- **L-4 (LOW, record).** The base campaign file's `code` field names the worktree blobs (disclosed). New part JSONs gain
  `h2_guard`; analyze ignores it (row 7). Master moved to 6ab459b: `git merge-tree --write-tree 6ab459b 61b149c` is clean
  (tree 4b80d8f4), and master's 6 changed files share none with the branch. Run the full suite on the merge commit.

## What it licenses (WORK-side engineering only)

- fresh-rules' rule-A code now refuses, at run time and in its selftest, these leaks:
  - a fresh item in the A build (R8, M4);
  - pool-parent leaves that are not the A record's own, read where `v0a_old` / `v0a_boot` are computed (R7, R7b);
  - a foreign or wrong-split record, an empty pool, a pool id outside the build;
  - scored rows in the pool.
- tau-grid's selftest now separates the MAP half leg from a one-step read (V5, V5b).
- The FRESH-RULES-SIM and TAU-GRID records are unchanged and the guards are inert on their recorded inputs.

## What it does not license

- Any new or changed number or word of FRESH-RULES-SIM or TAU-GRID: nothing was re-run. POSTRUN_FRESH-RULES-SIM H1 (the
  transport refuted as planning n\*) stands.
- That rule A is leak-free: M1, M2 and M3 survive. No registered reuse of rule A before H1 and M-1 are fixed.
- Any switch of a deciding estimator, of `meter.TAU_GRID`, or of the tau^2 fit.
- Anything about fresh data, the vault or a reserved side: none was read.

## Commands (scripts and logs in `E:/TaxoArena_tmp/review_guards-fresh-tau`; benchzoom venv; BLAS 1)

```
git diff --name-only 35b2724..61b149c | wc -l -> 8; ... | grep -c '^src/' -> 0; git diff --numstat 35b2724..61b149c / f483194..61b149c
git rev-parse {35b2724,f483194,61b149c}:<path>; git hash-object <path>; tr -cd '\r' < <path> | wc -c -> 0; git show <rev>:<path> | sha256sum
git log --format='%h %ad' --date=iso 35b2724..61b149c; ls --time-style=full-iso <outputs>; grep -c -i 'fresh-rules|tau-grid' docs/execution_graph.md -> 0
python ast_cmp.py 35b2724 61b149c ...; python ast_cmp.py f483194 61b149c ...     # changed top-level defs (docstrings stripped)
python dry_indep.py   -> dry_indep.log    # pins, per-split counts, B0-vs-A rows, scored/boot disjointness (pickle/numpy only)
python reanalyze.py   -> reanalyze.log    # 6 texts: base vs tip vs recorded; h2_guard injected; recorded dirs snapshot
python specs_cmp.py; python camp_cmp.py   # specs literal vs 4 original runners; 223 campaign statuses from out.log + rc
python mut.py base new -> mut_run.log     # C0/R7/R8 fresh, C0/V5 tau on base and tip; M1-M4 at the tip (serial)
python fixture_cmp.py <mutroot>; python equiv.py; python cells_rec.py -> cells_rec.log
sha256sum -c SHA256SUMS (fresh-rules 19, _boot2 6; tau-grid 10, _all 15; outputs 11; backup 12); find <recorded dirs> -newermt 2026-10-27 | wc -l -> 0
PYTHONPATH=src pytest -q tests/test_guards_fresh_tau.py tests/test_tau_grid.py -> 5 passed, 1 deselected; git status --porcelain | wc -l -> 0
git merge-tree --write-tree 6ab459b 61b149c -> 4b80d8f4 (clean); git diff --name-only 35b2724 6ab459b | grep -c 'fresh-rules|tau-grid|guards' -> 0
```

The ledger, the programme and benchzoom master were not touched by this review.
