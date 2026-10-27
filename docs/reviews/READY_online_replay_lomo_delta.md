# READY (delta) review: ONLINE-REPLAY-LOMO stage 1, 69cd6d4c..aa5f2625

Reviewer: adversarial-reviewer, 2026-10-03. Zero calls. Delta review of `git diff 69cd6d4c aa5f2625` against
READY_online_replay_lomo.md (NOT READY on blob 8fe228eb). I do not re-derive what that review CONFIRMED (H1, H2, H5, D1, D2, S, G).
Reviewed blob: `tools/analysis/online_replay_lomo.py` **blob:fb3a956369ad2e921b61202d4d9ff460c53eab03** (`git hash-object`, LF;
0 CR bytes in the working tree; sha256-lf16:b61015a3d05c1028). aa5f2625 touches 1 path
(`git show --name-only --format= 69cd6d4c..aa5f2625 | sort -u` = the script only); +391 / -69 lines.

## Verdict: READY, conditional on the registrar's pre-data brackets below (R-1..R-7)

C-1, C-2 and C-3 are fixed as asked, and the identities reproduce on the real inputs in the real dry-run. Code reading confirms
the deciding OL1 word is computed from the symmetric comparator. My mutant D3 shows the selftest does not guard that line
(condition L-1, not blocking). One descriptive line is mislabelled (L-2, not blocking).

## Per-claim table

| # | claim (builder) | mine | status | sev |
|---|---|---|---|---|
| C-1 | the online mean starts at the true TRAIN mean (r x vmfMu, n = TRAIN count); routing before the stream is unchanged; the unit start is printed beside | `replay()` L527 `mbar = mu0 * A["r"][keep][:, None]`; `U = mu0` (direction unchanged, so I3 holds). Tree: r = \|sum\| / count over af_cells TRAIN rows; IFEVAL uses all its TRAIN rows. Dry-run: **r median 0.691** (min 0.527 = IFEVAL; my own number is 0.527, n 325), n / directQueries 0.975, K_0 r median 0.693. Before the run I found 122-leaf median 0.691: equal. 0 bundle TRAIN items lack an af cell, so [ORL-INIT] does not fire. M45 / M46 / M47 (= my O3) / M52 KILLED | CONFIRMED | - |
| C-2 | the deciding batch files by nearest cell over all six members; mirrored and split-only printed beside | `batch={"tree": efl_all, "km": kfl_all}`, `diff = online - W["batch"][arm]`, `ol1=ol1_of(st)`. Dry-run: symmetric **P_fl 0.7265** (my independent 0.7265) and **P(US_0, nearest of all) 0.7289** (= UNION-AF-ROUTE outcome.txt line 209, read by me). Mirrored 0.7346 / 0.7368 are still identity-checked. M48 / M49 / M53 / my D2 KILLED; **my D3 (OL1 word from the mirrored stat) SURVIVED** | CONFIRMED (by reading; test gap L-1) | LOW |
| C-3 | the deciding churn is the five-member graft before vs after (means only); all-cells churn and BUFFER CAPTURE printed beside; F-OL attributed to the mean refit | `churn = after_mean != before` decides. `churn_all` goes to `ol2_all` (descriptive). The capture line prints only when `ol2_all` is NOT-STABLE and `ol2` is not. F-OL text: "on the means-only churn ... replay -X". e2e_absorb (capture only: STABLE, capture line, F-OL NOT FIRED) and e2e_motion (mean refit: NOT-STABLE, F-OL FIRES) pass. M16 / M44 / M50 / M51 KILLED | CONFIRMED | - |
| D-4 / D-5 | OL2 range printed; transductive EVAL and the 15 / 14 multi-class residual disclosed | the lines are present in `outcome_lines`. The range is printed from the measured `ein` (2,661-5,977 per the prior review's count) | CONFIRMED | - |
| T | selftest 15; mutants 59 / 59, including O1-O8 except O6 | **SELFTEST PASSED (15 cases)**, rc 0. **MUTANTS 59 of 59 KILLED, control SURVIVED**, rc 0. O1 / O2 / O4 / O5 / O7 / O8 KILLED inside the suite; O3 = M47 KILLED. O6 was left out correctly (equality with an order statistic has measure zero) | CONFIRMED | - |
| DR | real --dry-run | no java.exe (`tasklist` count 0; I polled every 5 min while a gemma-own-bar `gradlew test` ran). rc 0; POOL line first; B0-2 rc 0. Manifest 53021e26… has 18 + 11 files EQUAL. GATE 2,028. Bundle rows reproduced to 5.55e-17. I3 6,139/6,139; 0.7346 / 0.7265 / 0.7368 / 0.7289; K_0 labels 12,334/12,334. 123 cells per arm. 12 threshold lines, identical to the first dry-run. No statistic printed. DB sizes and mtimes unchanged (diff empty). Output dir absent; worktree status clean | CONFIRMED | - |

## Own mutants on the delta (3)

D1 the unit-start replay printed beside uses n = directQueries (the first build's n) instead of the TRAIN count: SURVIVED (not decisive; see L-2).
D2 symmetric-batch identity check skipped: KILLED.
**D3 OL1 word computed from the mirrored stat (`ol1=ol1_of(st_mir)`): SURVIVED (decisive line; the code is correct as read; see L-1).**

## Conditions

- **L-1 (LOW; not blocking):** no fixture gives different OL1 words under the symmetric and the mirrored comparators. Fix: in
  e2e_broad (or a variant), assert `T["ol1"] == ol1_word(st)` on a case where `ol1_word(st_mir)` differs, which kills D3. If it is
  not fixed before the run, the post-run review must recompute the OL1 word from `online_ok - batch_ok` in the items CSV, which
  it will do anyway.
- **L-2 (LOW, descriptive):** the "unit-start" lines are labelled "the first build's rule", but they use n = TRAIN count; the
  first build used n = directQueries (the oracle's `unit` path uses directQueries; their equality in the selftest is a discrete
  coincidence, D1). Fix: relabel the line "unit-start, n = TRAIN count", or use `n_dq` there.

## Registrar brackets needed pre-data (R-1..R-7; proposed wording)

- **R-1 OL-R1 (YES):** "OL1's batch arm files by flatLeaf over all six members' cells; the one-cell IFEVAL cell (unit mean of
  its TRAIN rows) is reachable by any item: the same rule as the online arm (batch P_fl(AF-U) 0.7265; P(US_0) 0.7289). The mirrored
  by-source filing (0.7346 / 0.7368, UNION-AF-ROUTE C-S1) and D over the five split members' replays are DESCRIPTIVE. A cell's
  online count n is its TRAIN count (af_cells.tsv / K_0 fit labels), not directQueries."
- R-2 OL-R2 (YES, LOW): "tau_oos = sort(max-cos)[floor(0.05 n)] and tau_m = sort(margin)[floor(0.20 n)] on the five in-members'
  GATE items against that arm's five-member cells before the stream, per arm; an item is buffered iff max-cos < tau_oos or
  margin < tau_m (strict)."
- **R-3 OL-R3 (YES):** "The stream is one fixed order per replay (numpy default_rng(20261003), fresh per replay; a permutation of
  m's TRAIN, then of m's EVAL). A cell's online mean starts at the true mean of its unit TRAIN rows: direction vmfMu (tree) or the
  K_0 centre, length r = |sum| / n (median 0.691). A filed item updates mbar += (x - mbar) / (n + 1), n += 1; routing uses
  mbar / |mbar|. The unit-start replay is DESCRIPTIVE."
- R-4 OL-R4 (YES, LOW): "The buffer is clustered by g13_breakdown.ukm_fit, seed 0, at k = min(L_m, buffer size); an empty buffer
  makes no cell. Buffer cells are provisional and uncertified."
- **R-5 OL-R5 (YES):** "Naming: an existing cell keeps its batch name unless one class of m's absorbed TRAIN items strictly
  exceeds the cell's batch majority count (AF-U: round(profile_size x leaf_purity); K_0: the TRAIN count of its majority class).
  The incumbent keeps a tie. A buffer cell takes the TRAIN majority of the buffered TRAIN items its fit assigns to it (tie: the
  smaller class name); a buffer cell with no TRAIN item is <empty> and never correct. EVAL labels never name a cell."
- **R-6 OL-R8 (YES):** "OL2's churn is the share of the in-members' EVAL items whose cell differs between flatLeaf over the five
  members' cells before the stream and over the same cells with their online-updated means after it. Buffer cells are not part of
  the five-member graft, so F-OL fires only on this churn. All-cells churn (moves into buffer cells) is DESCRIPTIVE, printed as
  BUFFER CAPTURE when it alone exceeds 0.020. The 95% upper bound is the percentile upper of the whole-component bootstrap
  (B 2,000). If STABLE and NOT-STABLE both held, the reader refuses ([ORL-OL2-BOTH]); this is not an outcome. OL2's per-replay
  n is 2,661-5,977, not 'about 5,100'; it is still SCOREABLE."
- R-7 OL-R9 (YES, LOW): "Numeric bands HELD iff the point lies in the closed interval. P2 'per replay' is HELD iff all six churn
  points (means-only) lie in [0.000, 0.015]. P3 is the numpy median of the six AUROCs. Brier is scored over the named outcomes,
  with GAIN 0.00 implied for OL1."
- No bracket: OL-R6, OL-R7, OL-R10, OL-R11.

## Launch (after R-1..R-7 are committed)

From main after the merge (`Z:\FAC\TUBerlin\THESIS\TaxoArena`), no env prefix: `python tools/analysis/online_replay_lomo.py --run`
(from the worktree instead: add `--data-root Z:/FAC/TUBerlin/THESIS/TaxoArena`). Never beside a construction (rule 7). Write the
outputs once and never commit them: pin by sha256 and back up to E:.

## Commands

```
git hash-object tools/analysis/online_replay_lomo.py          # fb3a9563 (worktree, aa5f2625); grep -c $'\r' = 0
git show --name-only --format= 69cd6d4c..aa5f2625 | sort -u   # 1 path
python tools/analysis/online_replay_lomo.py --selftest         # SELFTEST PASSED (15 cases)
python tools/analysis/online_replay_lomo.py --mutants          # 59 of 59 KILLED; control SURVIVED
python $TEMP/orl/delta_mut.py                                  # D1 SURVIVED, D2 KILLED, D3 SURVIVED
python $TEMP/orl/sym.py ; IFEVAL r one-liner                   # 0.7265 symmetric; IFEVAL r 0.527 n 325
sed -n 209p experiment_results/archv2/union_af_route/outcome.txt   # P(US_s) nearest-of-all 0.7289 ...
python tools/analysis/online_replay_lomo.py --dry-run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena   # rc 0, java count 0
ls -l --time-style=full-iso *.db* before/after -> diff empty; worktree git status --porcelain = 0 lines
```
