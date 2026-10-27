# READY review — STABILITY-VS-KMEANS (2026-10-05)

Reviewed: branch `stability-vs-kmeans` tip 174347a1 (parent chain contains registration 8e681387), one file
`tools/analysis/stability_vs_kmeans.py` blob:b278a7a9095f24a8c39689928a287a2c9b4d84ed (LF rendering, of record;
sha256-lf16:629aee8561ad4028, sha256-crlf16:018a0141f6fe78b9 beside). Registration prog L24625-L24637 (_as_of 8e681387).
Imports pinned and checked: site_support blob:4612345c, intent_transfer_s0 blob:f662ceb1. Zero calls.

## VERDICT: NOT READY (one BLOCKER, B-1; registration-level, fixable pre-data)

The code implements the registration faithfully and its numbers reproduce; the blocker is that the registered
shape match does not do what the registration says it does ("(ii) SHAPE ... removed here"), and the residue biases the
deciding D_b toward the predicted MORE-STABLE by about 0.07, i.e. 0.8 x the registered MDE80 (0.093) and above the
structural floor (0.049). It can change the ST1 word if a baseline mean lands low in P2's band (0.10-0.14).

## Per-claim table (deciding claims)

| # | claim | result | mine vs claimed | sev |
|---|---|---|---|---|
| 1 | baselines fitted on M_r, at k_r, collapsed to tree r's internal count on C | CONFIRMED | code L711 (fit on W["X"][t], k W["k"][t]); dry-run k_r 82/79/81/81, m_r 68/63/65/68, \|M_r\| 8125/8126/8130/8133; seed-0 kept/available on af_clean_s42 KM-AL 68/80, BKM 68/79 (no shortfall) | - |
| 2 | bootstrap: re-draws paired (shared pos and triplet weights by both arms), seeds crossed (outer-product weights on the 5x5 matrix), triplets resampled | CONFIRMED | own loop in registration order on synthetic R4/S5/N3000, 120 reps: max \|diff\| 9.8e-8 (D both arms), 9.3e-8 (tree); point 2.6e-8 (float32 V) | - |
| 3 | ST1 one clause (MORE iff both ub < 0; LESS iff any lb > 0; else NEITHER); FAILS; F-ST; MASSIVE descriptive, fixed pair, P5 on KM-AL | CONFIRMED | st1_decide L396-402; massive_block resample_redraws=False, line labelled "conditional on the one pair; no interval over re-draws" | - |
| 4 | no leakage | CONFIRMED | no EVAL read (members asserted on pool TRAIN side; MASSIVE members TRAIN rows, `question, side` only); labels never selected; dry-run prints no D (grep 'D_\|ST1 ' = 1 line, the disclaimer); no prior outcome on E: (ls, 0 dirs); first-draw tree term is the registration's disclosed informed look | - |
| 5 | identity: 0.0684 / 0.3243 and six pairs 0.0787/0.0883/0.1000/0.0481/0.0593/0.0357 | CONFIRMED to the digit | dry-run OK; outcome file sha256 60d4cb396f917be0 grep: same six 'trip' values, 'mean triplet 0.0684', '0.3243' | - |
| 6 | SVK-R1: deciding triplets = first RandomState(20261004) draw; identity replays the second | CONFIRMED | site_support.descriptive_lines L442-445 (first draw -> "tree pairs on C", the six Support (b) values) and L470 (second draw -> k-means line) | - |
| 7 | Support: SE 0.0333, MDE80 0.093, floor 0.049, DEFF 3.0 declared with its source, SCOREABLE | CONFIRMED | SD(six) 0.02476; SE sqrt(0.0248^2/2+0.040^2/2) = 0.03328; MDE 0.0932; floor 2.80 x 0.0248/sqrt2 = 0.0491 | - |
| 8 | shape match removes defect (ii) (unresolved-vs-unresolved scored as agreement) | REFUTED | see B-1 | BLOCKER |
| 9 | selftest 87/87; mutants 46/46, C0 survives | CONFIRMED | re-run: "SELFTEST OK: 87"; "46 / 46 killed", C0 SURVIVED | - |
| 10 | no writes to DBs of record; commit hygiene | CONFIRMED | mtime/size of snapshots.db, embeddings_cache.db, mmlu_pro_dataset_cache_v2.db, intent_emb_qwen3.db, s1 snapshots.db identical before/after dry-run (diff empty); -wal 0 bytes; commit 174347a1 `--name-only | wc -l` = 1 | - |

## Defects

**B-1 (BLOCKER) the registered shape match leaves the trees about 8x less resolved than the baselines.**
On the deciding (first) draw, 100,000 triplets on C:
- unresolved share, trees: af_clean_s42 0.0806, af_s137 0.1021, af_s2048 0.0986, af_s42_o1 0.0995;
- the collapsed baselines (seed 0, af_clean_s42): KM-AL 0.0009, BKM 0.0003.
- Unresolved in BOTH trees of a pair: 0.0665/0.0610/0.0580/0.0818/0.0780/0.0852 (mean 0.072), against 0.008-0.010 if
  independent. Those triplets score as agreement. A baseline pair can get at most about 0.001 of this credit.
- Source: about half come from multi-leaf items (318-339 C items sit in more than one leaf, SVK-R7; a partition never
  has these; unresolved triplets with a multi-leaf item 0.045-0.051), and about half from polytomies. Contracting the
  LOWEST edges puts the baselines' polytomies where triplets seldom fall; the trees' sit higher.
- Resolved-in-both tree disagreement: 0.0329/0.0352/0.0410/0.0125/0.0156/0.0091. The trees stay stable on resolved
  triplets. So the bias does not create a tree advantage, but it inflates the deciding one by up to about 0.07.
- The reviewer computed only the trees' topologies (already disclosed in the registration) and the unresolved share of
  one seed-0 fit per baseline. No baseline disagreement and no D_b was computed, so any amendment stays uninformed.

FIX (pre-data, the registrar's insertion-only bracket, then the engine-coder). Choose one:
- (a) Minimal, and it can only make MORE-STABLE harder to reach: add the conjunct ST1-RB. MORE-STABLE also requires the
  95% upper bound of D_b^RB < 0 for both baselines. D_b^RB uses, per pair, the resolved-in-both disagreement
  (sum w*(a != b & both resolved) / sum w*(both resolved), on the same replicate's weights, pos and seed counts).
  LESS-STABLE and NEITHER stay as registered.
- (b) Report D_b under two conventions, both-unresolved = agreement (as registered) and both-unresolved = disagreement,
  and require both upper bounds < 0.

Either way, the outcome must print the unresolved and both-unresolved shares per arm. The registration's sentence
"(ii) SHAPE ... removed here" must be bracketed as not achieved by the internal-count collapse.

**M-1 (MEDIUM) the per-re-draw m_r is not discriminated by the selftest.** My mutant R5 (every re-draw collapsed to tree
0's m) SURVIVED: the fixture trees share one m_r, while the real ones differ (68/63/65/68). The code is correct by
inspection (L546 uses W["m"][t]). Fix: give one fixture tree a different internal count and add R5 to MUTANTS.

**L-1 (LOW) bootstrap over 4 units.** A percentile bootstrap over 4 re-draws lives on a lattice and understates the
variance by about (n-1)/n. The registration acknowledges this and prints the leave-one-out values beside. The outcome
must print the LOO range beside the interval, as the code already does. No change needed.

**Readings for the registrar's bracket before --run.**
- SVK-R1: CONFIRMED as the only reading consistent with "the same index list" whose six values are Support (b).
- SVK-R2: seeds resampled per re-draw and shared by its copies in the multiset. Acceptable. The alternative,
  independent draws per copy, is equally defensible and must be fixed now.
- SVK-R3, R4, R6: acceptable.
- SVK-R7: acceptable, but it is half the source of B-1 and must be named in that bracket.
- SVK-R5: acceptable.

## Own mutants (sandbox via zc_common.run_mutants, TMP/TEMP/TMPDIR in the sandbox; 7/8 killed)
- R1 crossed seed matrix not transposed when r > q: killed (decisive).
- R2 collapse keeps m_r + 1: killed (decisive).
- R3 k_r = leaves + 1: killed (decisive).
- R4 C items mapped to wrong fit rows: killed (decisive).
- R5 every re-draw collapsed to tree 0's m: SURVIVED (decisive path; M-1).
- R6 seed counts reused across re-draws: killed.
- R7 interval on -baseline reps instead of D: killed (decisive).
- R8 baselines fitted on 255 coordinates: killed.

## Commands (busy.ps1 exit 1 = free before running; all temp under E:/TaxoArena_tmp)
```
git rev-parse stability-vs-kmeans:tools/analysis/stability_vs_kmeans.py      # b278a7a9...
git -C .claude/worktrees/agent-abbb652bb87b018d5 hash-object tools/analysis/stability_vs_kmeans.py   # same; status --short | wc -l = 0
git show 174347a1 --name-only --format= | wc -l                              # 1
python tools/analysis/scratch_dir.py --run -- python tools/analysis/stability_vs_kmeans.py --selftest   # 87 OK
python tools/analysis/scratch_dir.py --run -- python tools/analysis/stability_vs_kmeans.py --mutants    # 46/46, C0 SURVIVED
python tools/analysis/stability_vs_kmeans.py --dry-run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena    # identity OK, 30 s, est. 4 min
sha256sum E:/TaxoArena_backup_2026-10-04_site_support/site_support_outcome.txt; grep 'trip 0\.' / 'mean triplet'
ls -l --time-style=full-iso <5 DBs> before/after | diff                       # MTIME_SAME
E:/TaxoArena_tmp/svk_review/my_mutants.py   (R1-R8 via ZC.run_mutants)
E:/TaxoArena_tmp/svk_review/boot_check.py   (independent bootstrap loop, registration order)
E:/TaxoArena_tmp/svk_review/overlap.py, unres_src.py   (unresolved / both-unresolved shares, multi-leaf source; trees + one seed-0 fit each)
```
Re-review after the fix: a delta review of the bracket and the code diff, re-running the selftest, the mutants, R5 and
the B-1 shares.

## DELTA REVIEW 2026-10-05 — fix tip 96ea8650, blob a67bbf0a; brackets 05987e4c (ledger v393)

Reviewed `git diff 174347a1..96ea8650`. One file (`tools/analysis/stability_vs_kmeans.py`), +269/-92. Pins:
- blob:a67bbf0a673cffabd7dccdced95b23b11a4ac01b, the LF rendering, of record;
- sha256-lf16:5c38f16c67067202, with sha256-crlf16:c828548555108def beside;
- the worktree's hash-object equals the blob; `status --short | wc -l` = 0.

What the prior section CONFIRMED on code this delta does not touch is not re-derived: fits, collapse, triplet draws,
identity, and the MASSIVE loading.

### VERDICT: READY for blob a67bbf0a, with conditions C-1..C-3 on the post-run review (none changes a deciding computation)

| # | check | result | evidence | sev |
|---|---|---|---|---|
| 1 | MORE-STABLE needs both upper bounds < 0 on D_b AND on D_b^RB, from one bootstrap | CONFIRMED | `st1_decide(lo, hi, hi_rb)`: both `all(...)` conjuncts. LESS-STABLE reads the D_b lower bound only, as bracketed. bootstrap() scores all/rb/strict from the SAME `M[:, j]` (one triplet-weight draw), the same pos and the same cnt, inside one replicate loop. NaN in RB -> `nan < 0` False -> not MORE-STABLE (fails closed) | - |
| 2 | RB per pair, correct | CONFIRMED | V = [NUM; DEN; BU] rows, one per hierarchy pair (each tree pair; each crossed seed pair). rb = NUM/DEN per pair on the replicate weights, then combine() averages per pair with the seed-count weights. Registered all = NUM + (1 - DEN - BU) (both resolved and differ, OR exactly one unresolved), equal to the old `!=`. strict = NUM + 1 - DEN. Float32 matmul on integer sums < 2^24, divided in float64 | - |
| 3 | nothing else changed | CONFIRMED | 25 hunks: docstring; SELFTEST_CHECKS; pair_vectors / conventions / bootstrap / st1_decide; massive_block prints; analyse (LOO via `["all"]`, the unresolved and RB lines, option (b), ST1 / FAILS text); dry-run timing matrix x3; the rest is selftest and fixtures. No change to fits, on_C, draws, identity or loading | - |
| 4 | dry-run identity | CONFIRMED | 0.0684 / 0.3243 and the six pair values OK. k_r 82/79/81/81 and m_r 68/63/65/68, as before. grep 'D_\|ST1 ' = 1 line (the disclaimer). DB mtimes unchanged (diff empty) | - |
| 5 | selftest 99/99; mutants 57/57, C0 survives; R5 = X47 | CONFIRMED | re-run: "SELFTEST OK: 99"; "57 / 57 killed", C0 SURVIVED (`grep -c SURVIVED` = 1, the control) | - |
| 6 | ST1-RB Support (bracket): SD 0.0135, SE 0.0299, MDE80 0.084, floor 0.027 | CONFIRMED | six RB values: mean 0.02438, SD 0.013547. sqrt(0.0135^2/2+0.040^2/2) = 0.029852. 2.80 x SE = 0.0836. 2.80 x 0.0135/sqrt2 = 0.0267 | - |

Own delta mutants (sandbox, `zc_common.run_mutants`): 3 of 4 killed.
- D1 ST1 fed `hi` in place of `hi_rb`: SURVIVED (decisive wiring; C-2).
- D2 registered D = strict convention: killed.
- D3 RB counts both-unresolved as agreement: killed.
- R5 (= X47): killed.

### Conditions (post-run review and registrar)
- **C-1 (MEDIUM) P6 is not printed.** No P6 band line exists (`grep -n P6` = 0 hits in the blob).
  - Fix: the registrar scores P6 by hand from the printed points, HELD iff the point lies in the closed band:
    D_RB_KM-AL in [-0.37, -0.14] and D_RB_BKM in [-0.32, -0.07], both on the "ST1-RB INPUT" lines.
  - P3 is already scored on the joined word.
- **C-2 (MEDIUM) the selftest does not check the analyse() wiring of the RB conjunct** (D1 survives). The units test
  st1_decide alone, and the RB fixture world never passes through main(). The code is correct by inspection.
  - Fix: the post-run reviewer re-derives the ST1 word by hand from the four printed upper bounds on the ST1 line.
  - If the blob is ever edited: add an end-to-end world where D_b clears 0 and D_b^RB does not, and add D1 to MUTANTS.
- **C-3 (LOW) no realised RB Support line.** The RB bootstrap SD (the SE reported) is printed. The post-run review prints
  MDE80 = 2.80 x that SD beside the RB clause, with n_eff 2 and the re-measured DEFF.

### Commands
```
git rev-parse stability-vs-kmeans{,:tools/analysis/stability_vs_kmeans.py}; git diff 174347a1 96ea8650 [--stat | grep '^@@']
python tools/analysis/scratch_dir.py --run -- python tools/analysis/stability_vs_kmeans.py --selftest|--mutants
python tools/analysis/stability_vs_kmeans.py --dry-run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena
E:/TaxoArena_tmp/svk_review/my_mutants2.py (D1-D3, R5); DB mtime diff before/after: empty
```
