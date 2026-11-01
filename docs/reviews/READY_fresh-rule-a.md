# READY_fresh-rule-a: adversarial READY review of benchzoom `fresh-rule-a` (bd10e42..3bfc34f)

Reviewer: adversarial-reviewer, 2026-10-30. EXPLORATORY ENGINEERING, PREPARE ONLY (D-2026-10-28-1 / -2,
D-2026-10-29-1 / -2 / -3); BZ-AXIS-CONFIRM-FRESH is drafted, NOT registered. Branch `fresh-rule-a`, worktree
`Z:/FAC/TUBerlin/benchzoom_wt_fresh-rule-a`, tip 3bfc34f. The code of record is f40e3ac. The tip adds docstrings only:
the AST with docstrings stripped is equal for all 3 scripts. Base and master are b546270 (an ancestor of the tip).
Reviewer bill: 0 LLM calls, 0 embeddings, no fresh item scored.

## Verdict

- **READY**, for the rule-A assignment library `examples/fresh_rule_a.py` (blob d3e72dd4, LF) to be imported by the FRESH
  runner ahead of a later generation go. Conditions C1-C4 below are due at the runner's own READY. Nothing runs on
  fresh data before then.
- **H1 CLOSED and M-1 CLOSED, as specified.** At the base, M1, M2 and M3 survive. At the tip, M1 and M2 are killed by
  `REFUSED [H1]` and M3 by `REFUSED [M-1]`; all six results are my own re-runs. The pool_parent wrapper meets H1 in
  substance: the spied token is the issued object, and its values equal the A record's leaf at every pool row.
- **NEW N1 (MEDIUM), the same class as H1, one argument over.** G-USE checks the row COUNT of the pool data handed to
  `pool_residuals`, not which rows they are. A same-size pool with one fresh row swapped in passes every guard (own
  mutant O4: SURVIVED; 30 rule-A stats move).
  - N1 bars reuse of fresh-rules' rule-A pool path.
  - The FRESH test has no rule-A pool (N_A := N', record 2026-10-27 C(ii)), and the WORK record re-computes
    byte-identical. So N1 does not touch the library or this READY.
- **MERGEABLE (merge_ok YES).** Fast-forward onto master b546270. 0 `src/` paths (`git diff --name-only | grep -c ^src/`
  = 0). execution_graph.md names neither script (count 0). Inert on the record: 19 of 19 items, re-run by me.

## Deciding claims

| # | claim (builder) | my check / number | result | sev |
|---|---|---|---|---|
| 1 | base discriminator: X0 passes; M1, M2, M3 SURVIVE; R7, R7b, R8, M4 killed | My re-run with the runner's `--ids` (sandbox `FRA_TMPROOT`): X0 control passes; M1 / M2 / M3 SURVIVED (rc 0, 10/10). base.json: R7, R7b, R8, M4 killed. The specs are byte-equal to POSTRUN_GUARDS-FRESH-TAU's own `mut.py` strings for M1-M4, R7, R8 | CONFIRMED | - |
| 2 | tip: M1, M2 killed by REFUSED [H1]; M3 by REFUSED [M-1] | My re-run: X0 passes. M1 and M2 die with "REFUSED [H1]: pool_residuals reads only the leaves returned by pool_parent ... got ndarray". M3 dies with "REFUSED [M-1]: ... (68 of 68 scored rows differ ...)" | CONFIRMED | - |
| 3 | H1 fix = the reviewer's: spy at pool_residuals over split0..4, bootA, bootA2; the validated value is the only one passed on | S10 `use_ok`: one call per rule-A part; `pr[2] is pp[2]` (the issued token object); dtype, shape and values equal the record's leaf at every pool row; token rows equal the pool rows. `check_pool_parent` is kept, wrapped by `pool_parent` (tests and the recorded dry check use its counts) | CONFIRMED in substance (literal wording substituted, disclosed); see N1 | - |
| 4 | tip campaign 45/47 killed, G13 / G14 NOT APPLIED, H6 / H7 killed; lib 28/28; proof 13/13 | Statuses counted from tip / lib / proof.json (Counter). Old-string counts at f40e3ac AND at 3bfc34f: every spec occurs exactly once, except G13 / G14 (count 0 at both). The campaigns are reproducible at the tip | CONFIRMED (from the logs; I re-ran X0 / M1-M3 x 2 and 5 own) | - |
| 5 | the library reproduces every recorded rule-A assignment (5 x 885 x 6) | Own script (`libcheck.py`; pickles sha-checked against `SHA256SUMS_backup`): **0 of 26,550** cells differ. Split nodes 24 / 23 / 24 / 24 / 22; build ∩ fresh 0 in each split | CONFIRMED | - |
| 6 | pinned V0 freezes in rule mode, 29 nodes, k_of 9/3/4/6/4/7/3 = 36 | Read from the tree alone, with no library code: k_of Alg 9, C&P 3, Geo 4, IA 6, NT 4, Prealg 7, Precalc 3 = 36. 29 split nodes, all binary. `freeze_v0`: 29 reproduced, self-route 1.0; **0 fallback and 0 clipped nodes**, so fresh routing is t = x·u > 0. pkl sha c2003c59 checked | CONFIRMED | - |
| 7 | `kmeans_k` on the 4,914 items at that k_of = B0's K | 5 of 5 seeds byte-equal. B0's k_of equals the pinned V0's. B0's tree leaf partition equals the pinned V0's (same 4,914 items), so B0's K is K_A | CONFIRMED | - |
| 8 | inert, 19 of 19: 118 / 118 arrays, r00 / r01 equal, re-analysis equal except L35 | My `--inert --out <sandbox>`, 1,549 s, serial: 19 yes / 0 NO. 118 / 118 arrays identical. json diff []. Replicates []. Guards: 20 evaluations, 0 refusals. Negatives: M3 15/15 (169-806 rows), R7 5/5, raw 5/5. Spies: 3 / 3 / 7. Vault reads 0. The recorded dir is unchanged (file-list hash 65eb0c5a before = after, 236 files; sums 19 + 6 OK) | CONFIRMED | - |
| 9 | selftests 10/10, 6/6, 6/6; suite 991 passed / 1 skipped / 11 deselected | Re-run: 10/10 (138.1 s), 6/6 (14.5 s), 6/6 (0.3 s). Targeted `test_fresh_rule_a.py` + `test_guards_fresh_tau.py`: 8 passed, 2 deselected. Full suite at the tip: 991 passed, 1 skipped, 11 deselected, 0 failed (1,040 s) | CONFIRMED | - |
| 10 | zero LLM calls; no fresh item read, embedded or assigned | 0 network or client identifiers in the 6 files (grep). Ollama `server.log` 2026/10/29-30: 151 GIN lines, **0** chat / generate / embed (show / tags / version only, from peers). `load_vectors` refuses a missing text (embeds nothing). 0 references to the fresh list in the new code. My only fresh-list read: the id column and the set of 7 subject labels (equal to V0's depth-1 labels); no statistic | CONFIRMED | - |
| 11 | plan before code; deviations bracketed | bd10e42 23:11 < f40e3ac 23:57 < first output 00:00. Plan numstat 46/0 (insertion only). [P1] lists 3 deviations, but not UNIT_TOL (D5) | PARTLY | LOW |

## Own mutants (sandbox copies under `E:/TaxoArena_tmp/review_fresh-rule-a/runner/own/`; tracked files never edited)

| id | change | result | decisive |
|---|---|---|---|
| O1 | lib `check_cells` compares `np.sort(got)` with `np.sort(w)` (a row permutation passes) | **SURVIVED** (6/6) | yes (C1) |
| O2 | lib `check_cells` ignores the id-to-row map (`r = arange`) | killed (REFUSED [RULE-A] G-CELLS, 10 of 10) | yes |
| O3 | lib `kmeans_k` seed `int(s) + 1` (K_A at seeds 1..5) | **SURVIVED** (6/6); only the one-time `--inert` item lib_b0_k would see it | yes (C2) |
| O4 | `part_split`: `pool_residuals(subset_g(g, sort(old[1:] + fresh_all[:1])), token)` (same size, one fresh row in) | **SURVIVED** (10/10). Not equivalent: 30 rule-A stat points of split0 move (A:C1(N) 45.2402 -> 45.4805) | yes (N1) |
| O5 | fresh-rules `check_scored_cells` multiset compare | **SURVIVED** (10/10) | yes (C1) |

## Defects

- **N1 (MEDIUM; bars reuse of fresh-rules' rule-A pool path, not this READY).** G-USE validates the leaves but not the
  rows they are fitted with. `use_pool_leaves` compares `len(token.rows)` with `len(g_old.cat)`; GData carries no ids,
  so the token's `rows` never meet the rows that `subset_g` handed to `pool_residuals`. S10 checks only the length
  (`pr[1] == len(rows_)`). Fix: let `pool_residuals(g, token)` do `subset_g(g, token.rows)` itself, so the validated
  rows are the fitted rows, and kill O4.
- **C1 (MEDIUM; due at the FRESH runner's READY).** Neither G-CELLS fixture set pins row alignment (O1, O5 survive).
  Every edit fixture writes a new value (max + 1), so it changes the multiset as well. Fix: add a fixture in both
  selftests that swaps two scored rows with different cells; expect "(2 of n".
- **C2 (MEDIUM; same).** The selftest does not pin `kmeans_k`'s seed mapping (O3 survives). L4 compares assign_k with
  brute force on the labels kmeans_k itself returned. Fix: a known answer in the selftest:
  `kmeans_k(...)[s] == flat_compare.kmeans_partition(X, anc, k_of, s)` for s = 0..4, or pin the sha of B0's K labels in
  the runner.
- **C3 (LOW; same).** Three fields are present but never enforced:
  - `freeze_v0(tree_sha=...)` is stored, never verified;
  - `EMB_DIM = 512` is never used, so the build dimension is not enforced;
  - `V0_K_OF_MATH` is checked only in the proof.
  Fix: a `freeze_pinned_v0()` that verifies the `AXIS_PINS["math"]` pkl sha, dim 512 and k_of == (9,3,4,6,4,7,3), or
  make these runner-READY checks.
- **C4 (LOW; words, S3).** G-DISJOINT is id-only and vacuous on the real namespaces. Old ids are
  `math_mc_level1:<question text>` and fresh ids are `train/<subject>/<n>`, so 0 hits are possible. The content closure
  is the list's own `--freeze` twin re-check (stem_key exact + Jaccard ≥ 0.8 against MATH test, EEE and MATH-Hard).
  The message "items the frozen objects have never seen" claims more than the check does. Fix: call it "id-level". Then
  either key a content check on `split_side.stem_key` / `text_sha256`, or have the runner require list v3 sha 169f99b7.
- **D5 (LOW, record).** An unbracketed plan deviation. Plan §2b says |norm - 1| > 1e-6, but the code has
  `UNIT_TOL = 1e-3`. There is no consequence: the raw 512-prefix norms of the 4,914 items are 0.32-0.40, so
  |norm - 1| ≥ 0.60. Fix: a [P3] bracket.
- **L1 (LOW, disclosed).** Four kills are crashes, not comparisons: X77, L17, L22, P10. G-CELLS in fresh-rules compares
  the record with itself, so a forged record passes (the builder discloses this). The runner's `check_cells` must
  compare with `rule_a_cells` output computed independently of the scorer's input.

## What it licenses / does not

- **Licenses:**
  - `fresh_rule_a` as the FRESH runner's V0_A routing and K_A nearest-centroid functions, with C1-C4 owed at the
    runner's READY;
  - H1 / M-1 closed for the named mutants;
  - fresh-rules inert on its record.
- **Does not license:**
  - any fresh-item read, embedding, tree or statistic;
  - the FRESH runner itself, the F4 identity check or the F2 cont selection;
  - reuse of fresh-rules' rule-A pool path before N1 is fixed;
  - any change of a number or word of FRESH-RULES-SIM, TAU-GRID or GUARDS-FRESH-TAU.
- D-2026-10-29-3 (thinking on for reasoning-only models; the MATH sign-off) concerns the pipeline only. Nothing in this
  branch touches serving, thinking or extraction: no conflict.

## Pins (git blobs, LF; working tree 0 CR bytes in every file, so there is no CRLF rendering)

| file | tip 3bfc34f (sha256-lf16) | code of record f40e3ac |
|---|---|---|
| examples/fresh_rule_a.py | d3e72dd4 (efbd2141260e5c4f) | 731818dc |
| examples/fresh-rules.py | 9380bc3b (2b9be7a62109fae2) | 3d31c61a (base b546270: aa4ea09c) |
| examples/fresh-rule-a-proof.py | 37d53e9f (eeef9bed8827a498) | cd1e27fe |
| examples/fresh-rule-a_mutants.json | e40d0918 (3a7567bf5bbe55d9) | e40d0918 |
| tests/test_fresh_rule_a.py | ff82f54b (32776fb6798770ec) | ff82f54b |
| docs/fresh-rule-a.md | 49b08aa0 (b3920daaed80e333) | cf1798b7 |

Builder outputs: `E:/benchzoom_demo/followups/fresh-rule-a`. SHA256SUMS: 12/12 OK (sha256 a618007f637d5242). The backup
`SHA256SUMS_backup` is 13/13 OK and its `SHA256SUMS` is cmp-identical.

## Commands (benchzoom venv, `PYTHONPATH=src`, BLAS threads 1, `FRA_TMPROOT=E:/TaxoArena_tmp/review_fresh-rule-a/runner`)

```
git rev-parse HEAD:<f> / f40e3ac:<f>; git hash-object <f>; tr -cd '\r' < <f> | wc -c          # pins
python astcmp.py f40e3ac 3bfc34f <3 scripts>                                                    # AST equal x3
python speccount.py                                    # old-string counts at f40e3ac and 3bfc34f (G13/G14 = 0)
python examples/fresh-rule-a-proof.py --selftests --out $R/out                                  # 10/10, 6/6, 6/6
python examples/fresh-rule-a-proof.py --mutants base --ids X0 M1 M2 M3 --out $R/out             # X0 ok, 3 SURVIVED
python examples/fresh-rule-a-proof.py --mutants tip  --ids X0 M1 M2 M3 --out $R/out             # X0 ok, 3 killed
python ownmut.py O1 O2 O3 O4 O5                                         # own mutants (runner's run_one, sandbox)
python libcheck.py                                    # 0/26,550; pinned 29 nodes, k_of, kmeans_k = B0 K, B0 = V0
python examples/fresh-rule-a-proof.py --inert --out $R/out_inert                                # 19 yes / 0 NO
find fresh-rules -type f -printf '%p %s %T@\n' | sort | sha256sum                       # 65eb0c5a before = after
pytest tests/test_fresh_rule_a.py tests/test_guards_fresh_tau.py; pytest (full)                 # 8 passed; 991/1/11
grep '\[GIN\] 2026/10/(29|30)' server.log | grep -c '/api/(chat|generate|embed)'                # 0 of 151
```
Scripts and logs: `E:/TaxoArena_tmp/review_fresh-rule-a/` (not committed).
