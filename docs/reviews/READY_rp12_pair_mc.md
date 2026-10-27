# READY_rp12_pair_mc: review of rp12-pair-mc 9e53dbf (from main 672923b; commits 12e1abb, 26908cd, 9e53dbf)

Reviewer: adversarial-reviewer, 2026-10-01. Zero calls. No readout was read and no statistic was computed. The only data opened
were B0's committed engine CSVs (census: item counts by side, no correctness column) and, read-only (`mode=ro&immutable=1`),
the pinned B0 worktree's snapshots.db (-wal 0 bytes) plus embeddings_cache.db (worktree, and main's for a count of rows only).
Size and mtime were identical before and after. Prior reviews READY_rp12_et2 (9c41554) and READY_rp12_et3 (92afcc3) are cited,
not re-derived.

## VERDICT

- **MERGEABLE (3/3).** The diff touches 7 files, all under tools/analysis (557+/48-). 0 files under src/, gradle, docs/,
  report/, *.db, application.yml, .env or .gitignore. main has 0 commits past 672923b, so this is a fast-forward, clean by path.
  12e1abb carries the same blobs as rp12-et4 ed7e6d4 (4/4 files equal).
- **B0-4 (c) g13 bundle, (d) g11 --dry-run, (e) g10 --write-pointer: READY**, from the merged main tools, on conditions
  C-1..C-3. The acceptance lines of (c) and (d) in READY_rp12_et2 are RESTATED in C-1, because the exclusion changes them.
- **FLAT: READY after its census pin**, on conditions F-2..F-4. The pin is T2 leaves = 74 and fit_n = 6,993 (my census, below),
  written in a reviewed delta after (e).
- **B0′, o1, o2 may start once (c)-(f) are COUNTED as restated here**, built from the same pinned worktree 6d04e84 (D-8; C-3).
  They do not wait for FLAT, G12 or the wording fix D-1.

## Per-claim table (deciding claims only)

| # | claim | result | evidence (mine) | sev |
|---|---|---|---|---|
| 1 | B0's readout holds 19 multi-class items of 8,186 keys | PARTLY | Held-out file: 19 of 8,186 (EVAL 14, GATE 5). **The TRAIN file adds 15 of 12,349**, which the operator's count omits: 34 in all. Corpus tuples (both files): MATH+MMLU_PRO_LB 30, MMLU_PRO_LB x2 2, x3 2. The two grafts have identical exclusion sets | LOW |
| 2 | registered 6,153 / 5,642 are the counts before the exclusion | CONFIRMED | Real data through the reviewed functions: EVAL before 6,153 / 5,642, after **6,139 / 5,628**. 14 components are lost entirely. The side export has EVAL 6,153, GATE 2,033, TRAIN 12,351 (sha256-lf 47e9048bb09a6910) | - |
| 3 | 1% bar (integers, EVAL before) | CONFIRMED | 14 / 6,153 = **0.2275%**, so the bar does not fire (100·14 = 1,400 ≤ 6,153). RE (`>` -> `>=`) KILLED | - |
| 4 | G11 / G13 compare the registered counts before the exclusion; both readouts must exclude the same EVAL items | CONFIRMED | RA (c_b without the excluded components) KILLED; RF (n_b post-exclusion) KILLED; RB (bundle c_before from kept items only) KILLED; RG (g13 "excluded item still scored" check removed) KILLED | - |
| 5 | Support after the exclusion | CONFIRMED | n 6,153 -> 6,139. With DEFF fixed (n/G 1.091 registered; 6,139/5,628 = 1.0908), SE scales by sqrt(6153/6139) = 1.0011 and the MDE moves by 0.1%. Most the exclusion can move P_fl, D_fd or D13: 14/6,153 = 0.23pp. **SCOREABLE unchanged** | - |
| 6 | G14 ruling (b): multi-class items keep P1's modal cell; the identity reproduces RP03's +2.67pp on the full set; no bar | CONFIRMED | v2_declared_cells net change vs main = the load refusal of `<multi-class>` + selftest only (leg_u is unchanged, so the declared arm is RP03's). Selftest 97 checks / 22 of 22 mutants; the identity REPRODUCED with 2 such items scored. RC (TRAIN modal cells read from the held-out rows) KILLED | - |
| 7 | the printed exclusion line names the readouts that exclude | REFUTED | rp12_pairing L184 still prints "every per-item pairing readout: G11 D_fd, G13 D13, **G14**". g11 render reuses it, so the write-once G11 outcome would state a false exclusion (D-1) | MEDIUM |
| 8 | F-1: FLAT's T2 = B0 MMLU_PRO_LB through the pointer; census printed; leaves / fit_n owed | CONFIRMED | RH (pointer entry ignored) KILLED. Census on the real object: snapshot 20261001_070346_Headless_Run_Auto_ge (snapshots.db graph) gives 135 nodes, **74 leaves**, **6,993 root ids**; all 6,993 ids have a queries row with **6,993 distinct distilled texts**, in both DBs, so both fit_set asserts hold. load_T on the run dir (main and worktree) gives iteration 15, 135 nodes, 74 leaves, dim 512. This equals the steward's [ITEM-CENSUS] "6993 texts" | - |
| 9 | D-12: G12 refuses a TOP family whose depths are not [1] | CONFIRMED (root case) / PARTLY | The root-site fixture refuses. **RD (`!= [1]` -> `1 not in`) SURVIVED 8/8**: mixed depths [1, 2] are untested. G-1 item 3 of READY_rp12_et3 still gates (D-2) | LOW |
| 10 | D-13 / D-14 / D-15 / D-16 closed | CONFIRMED | et3's survivors re-run: RV8 KILLED 11/12, RV10 KILLED 6/8, D14 KILLED 11/12; g11 prints "NOT COMPUTED (no pre-data definition; R-1, 390f9c6)" | - |

Selftests at 9e53dbf: rp12_pairing 4/4, g11 7/7, g13 6/6, flat_v2 13/13, g10 12/12, g12 8/8, v2_declared_cells PASS (97 checks,
22/22 mutants). g11's PAIRING_PIN = blob 5fc484deb237…, which is the tip's rp12_pairing blob. Own mutants: 7 on deciding paths
(RA, RB, RC, RE, RF, RG, RH): 7 killed. RD survived and is not decisive. Plus 3 re-runs of et3 (RV8, RV10, D14): all killed.
After every mutant: `git status --porcelain` = 0 lines.

## Conditions

- **C-1 ((c) and (d), restated acceptance; the operator counts each line).**
  - (c) The `--g13-bundle` output must print:
    `MULTI-CLASS ITEMS EXCLUDED ... EVAL 14, GATE 5, TRAIN 15`, then 34 `excluded` key lines, then
    `DENOMINATORS: EVAL 6139 items in 5628 components after the exclusion (before 6153 / 5642; registered 6153 / 5642); EVAL
    excluded 14 of 6153 = 0.2275%`.
    The bundle json must carry n_eval 6,139, n_eval_before_exclusion 6,153, n_components_before_exclusion 5,642,
    multiclass_excluded_eval/gate/train = 14/5/15, and `<no-routing-row>` 0 among EVAL.
    The rest of READY_rp12_et2 (c) stands.
  - (d) g11 `--dry-run` must print flatLeaf and descent EVAL items 6,139 each, same set True, and
    `multi-class items EXCLUDED: EVAL 14 [...], GATE 5 [...]` for both, with identical key lists. No statistic.
  - Any other number is a STOP.
- **C-2 (registrar, before any G11 / G13 outcome; pre-readout).** Bracket the orchestrator's MC-EXCLUDE ruling and ruling (b)
  into the programme and the ARCH-V2-E-T record. `grep -c -i 'multi-class' docs/judge_v2_program.md` finds no such bracket
  today. The bracket must say three things:
  - the population is EVAL 6,139 / 5,628 (registered 6,153 / 5,642 before);
  - G13's KC_0 fit also loses the 15 TRAIN multi-class items (not named in the ruling);
  - B0-4 (c) and (d) read as in C-1.
- **C-3 (B0′, o1, o2).** These start only after (c)-(f) are counted and the pointer is written once. They are built from the
  pinned worktree 6d04e84 (D-8), never from main's new tip; the merged code is Python only, so G10's commit key is unaffected.
  Rule 7, THREAD-CAP and the B0-2 guard bind as for B0.
- **F-2 (FLAT dry-run, after (e)).** It must print the [D-10] T2 stamp line of READY_rp12_et3 F-1, then
  `T2 census (F-1; ...): snapshot 20261001_070346_Headless_Run_Auto_ge, leaves 74, root fit ids 6993; pinned leaves None, fit_n None`.
  FM reads snapshots.db from DATA_ROOT. If main's snapshots.db lacks the B0 snapshot, set TAXOARENA_DATA_ROOT to the pinned
  worktree; its embeddings_cache.db gives the same 6,993 texts.
- **F-3.** A reviewed delta sets `T2 leaves=74, fit_n=6993`. Any other census value is a STOP for the registrar.
- **F-4.** Rule 7: FLAT is a pool reader, never beside B0′/o1/o2 constructions.

## Defects (each with its fix)

- **D-1 MEDIUM (before any G11 / G13 --run).** rp12_pairing `exclusion_lines` (L184) prints G14 as an excluding readout.
  - Fix: print "G11 D_fd, G13 D13 (G14: disclosure only, ruling (b))".
  - Update the two selftest asserts (rp12_pairing L589, g11 L396) and re-pin g11 PAIRING_PIN.
  - (c) and (d) may run on 9e53dbf, because no outcome file carries the line.
- **D-2 LOW (g12).** Add a fixture with a non-site depth-1 anchor whose depth-2 site children join TOP (depths [1, 2]). That
  kills RD. G-1 item 3 of READY_rp12_et3 remains the gate.
- **D-3 LOW (docs).** The rp12_pairing docstring P2 (L14) still says rows with different true_key REFUSE. Add an insertion
  bracket pointing to the MC-EXCLUDE delta.
- **D-4 LOW (record).** The B0_run root-cause line counts the held-out file only (19). The registrar records 34 = 19 held-out
  (EVAL 14, GATE 5) + 15 TRAIN.

## Pins (9e53dbf; LF of record, CRLF = this Windows worktree's rendering)

| path | blob | sha256-lf16 | sha256-crlf16 |
|---|---|---|---|
| tools/analysis/rp12_pairing.py | 5fc484deb237 | 4b47859356078bee | bdbbf567bb28734d |
| tools/analysis/g11_reader.py | 45b468fbd0aa | 7262d7a58cb101fb | 0156fef239bececd |
| tools/analysis/g13_comparator.py | 80830134b3ba | e4ce7ea517607b2f | ac577cc81331fb60 |
| tools/analysis/v2_declared_cells.py | 9b6b90a29e29 | 5bfcd136c877aa68 | 4d8a460c3699c7d6 |
| tools/analysis/flat_v2.py | 67e85a3e21af | 2d5147fa398a299b | 48175a1945454c25 |
| tools/analysis/g10_compare.py | 6ee50a6fa945 | 63194c1c482cdf34 | 5edec2291b972523 |
| tools/analysis/g12_site_null.py | ada3afecf8f3 | 442feb577cb43400 | 120f9102351d9a7b |

B0 graft CSVs (main = worktree, sha256 of file). The leaves CSV is the same in both grafts (211519e9159f7e1d).

| graft | queries | train |
|---|---|---|
| flatLeaf | 5146fb357421d1b7 | ef3eceebd2e3c5d8 |
| descent | 68ea58f12c07f3d9 | 4bc6b20cd75d4085 |

## Commands (reviewer's own)

```
git worktree add --detach .claude/worktrees/rv-rp12-pair-mc 9e53dbf; git merge-base --is-ancestor 672923b 9e53dbf   # yes
git diff --name-only 672923b..9e53dbf | wc -l                                                      # 7
git diff --name-only 672923b..9e53dbf | grep -c -E '^src/|gradle|application.yml|\.env|\.gitignore|report/|\.db$|^docs/'  # 0
git log --oneline 672923b..main | wc -l                                                            # 0
for f in flat_v2 g10_compare g11_reader g12_site_null; do git rev-parse ed7e6d4:tools/analysis/$f.py 12e1abb:tools/analysis/$f.py; done  # equal x4
for s in rp12_pairing g11_reader g13_comparator flat_v2 g10_compare g12_site_null v2_declared_cells; do python tools/analysis/$s.py --selftest; done
scratchpad/census.py: RP.sides(EP.DEFAULT_SIDE); RP.item_cells/split_items/multi_by_side on both grafts' queries+train CSVs
  -> held 8186 (multi 19), train 12349 (multi 15); EVAL 6139/5628 after, 6153/5642 before; excl 14/5/15; same sets in both grafts
scratchpad/t2census.py: snapshots.db (worktree, immutable) graph of 20261001_070346_Headless_Run_Auto_ge -> 135 nodes, 74 leaves,
  6993 root ids; queries(id, distilled_text) in worktree and main embeddings_cache.db (immutable) -> 6993 rows, 6993 distinct
python -c "AF.load_tree(<B0>/mmlu_pro_lb/seed_42)" (main and worktree) -> iter 15, 135 nodes, 74 leaves, dim 512
stat -c '%n %s %Y' on the three DBs before and after: identical
scratchpad/mut.py, mut2.py: one in-place replace (anchor count == 1), --selftest, restore; RA RB RC RE RF RG RH RV8 RV10 D14
  killed, RD survived; git status --porcelain = 0 after each
grep -n 'G13 D13, G14' tools/analysis/rp12_pairing.py   # L184 (D-1)
grep -c -i 'multi-class' docs/judge_v2_program.md        # 0 (C-2)
git rev-parse 9e53dbf:<p>; git show 9e53dbf:<p> | sha256sum; sha256sum < <worktree p>
```
