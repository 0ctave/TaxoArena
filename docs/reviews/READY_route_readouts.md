# READY review: ROUTE-SOURCE-NULL, KNN-ROUTE, KEY-INFO-V2 (zero calls)

Reviewer: adversarial-reviewer, 2026-10-04. Branch `zero-call-route-readouts`, tip `c9b982d9` (parent `b66b075d`).
Registrations prog L24265-L24276 / L24278-L24289 / L24291-L24302 (_as_of b66b075d); record L24259-L24263; [SC] bracket
L23680-L23681. Full first review (2,938 new lines). Zero calls; nothing run on EVAL; no Gradle (Python only).

## Verdict

**READY, all three**, under conditions C1-C5 (registrar brackets before `--run`; C1 also binds the post-run review).
No BLOCKER. Run order: sequential, one at a time, never beside a construction (each `--run` is a pool reader, rule 7).

## Pins (LF rendering of record; `git rev-parse c9b982d9:<path>`, CR count 0 in every blob, so CRLF = n/a in git)

| file | blob (LF) | sha256-lf16 (dry-run identity line) |
|---|---|---|
| tools/analysis/union_route_common.py | d54739769d38a3a402e2deaab9e45109cd86de4e | 893e67a4c0d7aaa1 |
| tools/analysis/route_source_null.py | 9fc280effe0d1cc3ca6f32a01d9f175d80d0b2d6 | e5f523ebade10995 |
| tools/analysis/knn_route.py | ec5fbc418ed8b33728367a614c18b3abf8df832d | 667a0d16c0f85d37 |
| tools/analysis/key_info_v2.py | 37f5935c7e64d95110193cce575b25b128529f53 | 2559584d94b8b17b |

Reused, pinned at import and re-printed by the dry-runs: escalation_rc 8f99db7d, union_cells_io 92a04543, union_af_route
bf3f17db, free_tests_f4_f7 f0749d61 (KI only). The three scripts do not pin union_route_common's blob (identity line printed
instead): LOW, acceptable because the outcome header carries it.

## Per-claim table (deciding claims only)

| # | claim | result | mine vs claimed | sev |
|---|---|---|---|---|
| 1 | Builder reading KNN R1: the neighbour pool is the 11,841 key-complete scored TRAIN items, not 12,334 | CONFIRMED (set, not just arithmetic) | key-complete 11,841 is a strict SUBSET of the 12,334 bundle TRAIN rows: kc∩bundle 11,841, kc−bundle 0, bundle−kc 493. 12,334 is UNION-AF-ROUTE's AK filing fit set (outcome L204), not a keyed set; AF-U's routing policy is fitted on the same 11,841 (outcome L38, L107), so kNN vs AF-U is like with like | bracket (C3) |
| 2 | KNN R5: [KN1-OVERLAP] refuses instead of choosing | CONFIRMED, inert on these data | overlap needs spread_K < 0.5pp. spread_K is a function of the K0..K4 points, fixed by [B3] (policies = frozen file) at 0.6271−0.6213 = 0.00576 (UNION-AF-ROUTE L174). CELLS-ADD needs D_N < −0.00576; the TOST needs lo90 > −0.005, so D_N > −0.005. Disjoint. Refusing on a co-fire is the right fail-closed form | LOW, bracket (C4) |
| 3 | KI R1: KI = 18 × loo_imp mean, EVAL held out | CONFIRMED | free_tests_f4_f7.loo_imp L147-L156: a q not in `fit` takes the held-out branch (marg = S/N, cell = csum/cn, else marg). key_info_v2 calls it with qs = EVAL, fit = TRAIN, so the leave-one-out branch never fires. It returns imp/len(models), and ×18 = the registered sum. [KI-F6] checks every arm and every RWS draw to 1e-9. My mutant R1 (point KI fitted on TRAIN+EVAL) is KILLED by [KI-F6]. The registration's "leave-one-out" is inert; the held-out design is the stronger one (loo_imp's own docstring) | bracket (C5) |
| 4 | RSN: the G_SRC +1.01pp and D_S +0.51pp points were seen; only the interval and the RWS band are new | CONFIRMED, plus more seen | From the UNION-AF-ROUTE arm table (outcome L154-L165): G_SRC = 0.6150−0.6049 = +1.01pp; D_S = 0.6201−0.6150 = +0.51pp. Also seen: G_declared−G_SRC = 0.6316−0.6150 = +1.66pp, every G_K,s, G_AF, and spread_K 0.58pp (KNN). P1's bands [+0.4, +2.0] and [−0.6, +1.2] contain the seen points, so P1 is NOT a prediction. At D_S +0.51pp, ABOVE-SOURCE needs the realised SE_2stage ≤ 0.51/1.96 = 0.26pp, against the registered 0.44pp. So in practice RS1 is decided by the RWS band: SOURCE-EXPLAINED iff G_AF lies inside it | HIGH (disclosure), bracket (C2) |
| 5 | Identity gates reproduce UNION-AF-ROUTE | CONFIRMED (targets) | COMMON.identity = outcome L154-L159 / L169-L170 to the digit: best 0.6049, TRUE source 0.6150, AF 0.6201, K0 0.6271, C1 +2.67 [+1.46, +3.89], G_AF +1.52 [+0.14, +2.91]. The gate runs before any new number (selftest refusals for each arm digit and each interval end; C06-C08, X14/X33/X17 killed). The real reproduction happens in `--run` (refuses otherwise) | — |
| 6 | Like with like: SRC = 6 source cells; RWS within source; kNN with no cells; K_0 | CONFIRMED, with D-4 asymmetry undisclosed | frozen policy true_source has 6 keys (BBH, GPQA, IFEVAL, MATH, MMLU_PRO, MUSR). RWS profile and blocks run over scored TRAIN items per stratum source (C02/C04, R5 killed). KNN-SC searches TRAIN rows of the item's own source only (X17 killed). K_s = the frozen K0..K4 (B3). **But** AF-U files by flatLeaf over ALL grafted leaves (UNION-AF-ROUTE D-4, L177): 223 of 6,139 bundle EVAL items and 311 of the 11,841 scored TRAIN items sit in another source's leaf, while SRC, RWS, KNN-SC and K_s file by true source. No outcome prints this (grep D-4 / asymmetr: 0 hits in the four files) | HIGH (C1) |
| 7 | TRAIN-only fits | CONFIRMED | every policy goes through V.fit on TRAIN weights (C05 killed). kNN neighbours are X[D.T] only. TS clusters TRAIN correctness only. The KI marginal and cells come from TRAIN (X09 killed; my R1 killed). The KI pre-pass runs inside `between`, after the TRAIN key and before eval_view opens (X21/X22 killed) | — |
| 8 | Write-once | CONFIRMED (main path); VOID path untested | outcome and marker are checked before any read (X15/X35 killed); G.write_once mode "x"; a second `--run` is refused and the outcome is unchanged (run_e2e). My R3 (`if not ok_sha:` → `if False:` in write_outcome) **SURVIVED**: the _VOID branch is never executed by any selftest | MEDIUM (D3) |
| 9 | Support | CONFIRMED (arithmetic reproduces) | RSN/KNN: SE = (0.41+1.31)/(2×1.96) = 0.4388pp; MDE80 = 2.8×0.4388 = 1.229pp; n_eff 5907/2.867 = 2060.3. The DEFF source is UNION-AF-ROUTE U2 measured 2.867 (outcome L176) ✓. TOST reach 0.5−1.645×0.44 = −0.224 ✓. Wholly-above reach 1.96×0.44 = 0.862 ✓. KI: n_eff 5907/1.6 = 3691.9 (registered 3,690); SE 0.10/√3690 = 0.001646; MDE80 0.00461 ✓. DEFF 1.6 is declared as a pilot assumption (U1 1.595, an accuracy contrast, not Brier). Per-item SD 0.10 is an unsourced planning value. The pre-pass and the run print the realised SE / DEFF / n_eff / MDE beside the statistic | LOW (D5) |
| 10 | No write to DBs of record | CONFIRMED (dry-runs) | gen_view sha256 c2930c60… EQUAL before/after in each dry-run; eval_view not opened. size/mtime of 322 *.db files under data_v2, union_af_route and root: unchanged after all reviewer reads (diff empty) | — |

## Selftests, mutants, dry-runs (re-run by me, temp on E: via scratch_dir)

- Selftests: RSN 5/5, KNN 6/6, KI 6/6 (rc 0).
- Builder mutants: RSN 41/41 KILLED, KNN 44/44 KILLED, KI 33/33 KILLED; no survivors, none not applied (control X00 survived in each).
- My mutants (deciding paths): R1 KI point fitted on TRAIN+EVAL: KILLED, decisive. R2 D_N point on KNN-ALL: KILLED, decisive.
  R4 KNN-SC replicates on ALL neighbours: KILLED, decisive. R5 RWS EVAL all to block 0: KILLED, decisive. R3 VOID branch disabled:
  SURVIVED, not decisive (D3).
- Real dry-runs (worktree, `--data-root` = main): all three print the POOL line first; B0-2 rc 0; manifest 53021e26 equal; frozen policy
  8d68018c equal; TRAIN 12,351 / key-complete 11,841; eval_view NOT opened; nothing written.
- Vector preflight (mine; the dry-run does not read vectors): union_af_route._TV on all 18,504 AF-cell items. 2 have no text:
  i:1c0e11e5… and i:e62c06a0…, both TRAIN, `<no-routing-row>`, NOT key-complete, NOT in the bundle, so neither is scored. The
  other 18,502 read fine. The 12,334 bundle TRAIN rows equal the reader's unit rows (max |Δ| 0.0). [KNN-VEC] will pass.

## Defects and conditions

- **C1 (HIGH; registrar bracket before `--run`, post-run duty).** The D-4 filing asymmetry is undisclosed in all three readouts.
  AF-U files EVAL across all grafted leaves (223 / 6,139 bundle EVAL cross-source), while every [SC] comparator files by true source.
  Per D-4 the asymmetry runs against AF-U. So it favours SOURCE-EXPLAINED (F-RS), CELLS-UNNEEDED (F-KN) and NOT-BEYOND (F-KI): the
  falsifier-firing words. Fix: bracket it on the three registrations. The post-run review recomputes the cross-source count on the
  scored 5,907 and prints the direction beside any falsifier that fires. (A code print line is optional; it would need a re-pin.)
- **C2 (HIGH; bracket).** RSN pre-seen data. P1 (G_SRC, D_S) is NOT SCORED. P2's probabilities were set with the D_S point
  knowable. ABOVE-SOURCE is reachable only if the realised SE ≤ 0.26pp, so RS1 effectively reads the RWS band. The bracket also lists
  G_declared−G_SRC +1.66pp and the G_K,s as seen (descriptive). The builder's disclosure in c9b982d9 (SEEN DATA) is correct but
  incomplete. KNN: G_AF and spread_K are seen. They are inputs, not predictions.
- **C3 (LOW; bracket).** KNN "TRAIN 12,334 keyed rows" reads "the 11,841 key-complete scored TRAIN items (a subset of the 12,334
  bundle rows; 493 bundle rows are not key-complete)".
- **C4 (LOW; bracket).** KN1's exclusivity rests on spread_K ≥ 0.5pp. It holds at 0.00576 (deterministic under B3), so
  [KN1-OVERLAP] is inert.
- **C5 (LOW; bracket).** KI's "leave-one-out" reads as loo_imp's held-out branch (fit = TRAIN, scored = EVAL); KI = 18 × loo_imp mean.
- **D3 (MEDIUM; fix in a later delta, not blocking).** The _VOID branch of write_outcome is never executed. Add a selftest that stubs
  V.after_sha → False and asserts that `*_VOID.txt` exists, that outcome.txt is absent, and that the run refuses.
- **D4 (LOW).** Every refusal after the marker (DENOM, B3, IDENTITY, HOOK, KNN-VEC, KI-F6/MURPHY) burns the write-once slot. The
  vector read is the only post-marker step that needs no EVAL key. My preflight shows it passes. Next time, put it in `--dry-run`
  (memory note dry-run-skips-transport).
- **D5 (LOW).** KI Support (d): the SD of 0.10 is unsourced. The pre-pass's realised SE (printed before the eval view opens) is the
  check. The post-run review must re-measure DEFF from the run's two-stage / i.i.d. ratio and print n_eff and the MDE beside D.
- **L (LOW).** The RWS profile carries foreign-cell blocks (311 scored TRAIN items whose AF leaf is another member's), so RWS cell
  counts per source exceed AF-U's leaf counts. This is printed by design and the null stays within-source.

## Commands

```
git rev-parse c9b982d9:tools/analysis/<f>.py ; git show c9b982d9:tools/analysis/<f>.py | tr -cd '\r' | wc -c    # pins, CR=0
python tools/analysis/scratch_dir.py --run -- python tools/analysis/<t>.py --dry-run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena
python tools/analysis/scratch_dir.py --run -- python tools/analysis/<t>.py --selftest | --mutants      # in the worktree
scratchpad/setcheck.py   # gen_view (guarded opener, dry form): TRAIN 12351, kc 11841; kc∩bundle 11841, kc−bundle 0, bundle−kc 493;
                         # scored TRAIN cross-source AF leaf 311; the two textless items: TRAIN, no-routing-row, not kc
bundle npz + af_cells.tsv: cross-source filed EVAL 223 / 6139, TRAIN 374 / 12334 (classes[y] source vs cell member)
scratchpad/veccheck.py   # union_af_route._TV on 18,502 items: all read; bundle TRAIN rows equal (max diff 0.0)
scratchpad/my_mutants.py <t>   # R1-R5 via union_route_common.run_mutants
outcome.txt (UNION-AF-ROUTE, sha256 e50a8e0f…) L154-L176: arm table, U1, spread_K, U2 DEFF 2.867
free_tests_f4_f7.py L131-L157: loo_imp held-out branch
find data_v2 experiment_results/archv2/union_af_route . -maxdepth 3 -name '*.db*' -printf '%p %s %T@\n'   # before / after: equal
```
