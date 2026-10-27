# READY (delta) — UNION-AF-ROUTE C-S1 / C-S2 mirrored filing: union-af-mirror 85a6b2fc

Reviewer: adversarial-reviewer, 2026-10-03. Zero calls, no JVM, no construction. Brackets of record: prog L23098 (C-S1) and
L23664 (C-S2); registrar's record L23669-L23674 (d3653625). The delta is `git diff d3653625 85a6b2fc` = union_af_route.py only,
+173 / −12. Everything outside AK1/AK2 filing is cited from READY_union_af_single_cell.md, not re-derived. **The AF-U build is
running** (3 java.exe), so nothing under experiment_results/archv2/union_af_route/ was read, and no pool reader ran (rule 7).

## Verdict

**READY for `--run`, on two conditions.** C-M1: add one assertion that kills O15. C-M2: after the build, the real dry-run and
the full mutant re-run, both deferred here because the construction is running. The mirrored rule is implemented as the
bracket says, and every deciding read uses the mirrored values.

## Pin (LF of record; working tree LF, clean)

tools/analysis/union_af_route.py: blob a3a31fa16de958c479c62aeb42b4abc94fe0a74c, sha256-lf16 040b247d0908f86e /
sha256-crlf16 b90cd5b517858493 (from f569d6f4). union_af_route_ops.py 5a020d29 and v2_declared_cells.py f0f56805 are
unchanged.

## Per-claim table

| # | claim | finding | verdict | sev |
|---|---|---|---|---|
| M1 | Is the AK1 refit at k = L − 1 what the bracket means? | The bracket: "in U_s and US_s that source's EVAL items are filed by source to its single centroid (k = 1), and that centroid is excluded from every other item's nearest search". The L23098 one-cell bracket adds: "U_s (AK1) counts its one cell in AF-U's total k". A global fit at k = L on all TRAIN has no "single centroid" of a source, so neither clause is defined there. The only reading that meets both clauses is k = L − (one-cell count) on the other sources' TRAIN, plus a k = 1 centroid of the one-cell source, for a total of L. It also mirrors AF-U exactly: the split members never saw the one-cell items. `ak_mirrored` does this, naming the one-cell source by its TRAIN majority (`GB.majority(yt[m])`; my O14 leak mutant is KILLED). The bracket does not spell out the refit → registrar note L-M1 | CONFIRMED (the only coherent reading) | LOW |
| M2 | AK2 mirrored: one-cell items go to their own centroid; no other item can reach it | `S = np.where(isin(csrc, single), -inf, Xe @ C.T)`, then one-cell items are set to `names[csrc == so][0]` (k = 1). X80 / X82 KILLED | CONFIRMED | — |
| M3 | Spreads, verdicts, F-AK and predictions read the mirrored values | In `ak_compute` the override of `ug_ok` / `us_ok` comes BEFORE `p_u`, `p_us`, `spread_au/aus`, `AK1/AK2` stats, `p_u0/p_us0`, `d_au/d_aus` and `by_source`. `ak_lines`' verdicts read `R["AK1"]`/`R["AK2"]` and `R["spread_*"]`; F-AK reads `st2["hi"] <= R["spread_aus"]`; `PRED_AK` reads `R[key]`. The registered values live only in `R["reg"]` and are printed as DESCRIPTIVE. single_e2e asserts the mirrored D/P/spread and the AK2 verdict against an independent loop oracle (`_oracle_ak_mirror`), plus that mirrored ≠ registered (non-vacuous). **Gap:** my O15 (F-AK reads `R["reg"]["spread_aus"]` when mirrored) SURVIVED; the code reads the mirrored spread (inspection), but no test pins it → C-M1 | CONFIRMED (code); test gap | MEDIUM |
| M4 | The registered nearest-of-all value is printed as DESCRIPTIVE | Two "DESCRIPTIVE (the registered nearest-of-all ...)" lines with P per seed, spread and D with its interval; X84 KILLED; X79 (nearest-of-all decides) KILLED | CONFIRMED | — |
| M5 | Nothing changes without a one-cell source | `single=()` skips the `if single:` block and the rest of ak_compute is unchanged. AK-IDENTITY on the real B0 bundle through the new blob reproduces D_U +0.0738, D_Us +0.0656, spread_U 0.0414, spread_US 0.0233. ak_e2e and run_e2e pass | CONFIRMED | — |
| M6 | C-S2 disclosure | "Like with like holds IN k ... In FILING, AF-U's by-source filing IS MIRRORED in AK1 / AK2 only ...; U2 / U3a's K_s files every item by its true source as registered ...; No wider like-with-like claim". It matches the L23664 bracket. X83 KILLED | CONFIRMED | — |
| S | Selftest 12/12; mutants 92/92 | Selftest re-run: 12 / 12. Mutants: I re-ran the six new ones (X79-X84, all KILLED) plus mine. The full 92-mutant suite (about 1 h of CPU) was NOT re-run while the construction holds the machine (CPU lane paused, KNOWLEDGE §2) → C-M2 | PARTLY (deferred) | — |
| D | Dry-run | NOT run: it is a pool reader (B0-2 check) and reads AF-U under experiment_results/archv2/union_af_route/ while the build writes it (rule 7; the brief) → C-M2 | DEFERRED | — |

Own mutants (≤ 3 for a small delta, plus one): O13 (AK1 mirrored refit at k = L) KILLED; O14 (one-cell AK1 name from the EVAL
majority, a leak) KILLED; O15 (F-AK reads the registered spread when mirrored) SURVIVED, decisive → C-M1.

## Conditions

- **C-M1 (MEDIUM, before `--run`)**: in single_e2e, assert that the F-AK line prints the mirrored spread
  (`"<= the measured spread_AUs %.4f" % o["spread_us"]` or the NOT FIRED form) and that its word equals the hand rule on the
  mirrored interval and spread. If the fixture's mirrored and registered spread_AUs coincide to 4 dp, choose a fixture seed
  where they differ. Re-run single_e2e and O15. This is a one-line delta; a reviewer spot check suffices.
- **C-M2 (after the build, before `--run`)**: run the full `--mutants` (expect 92/92) and the real `--dry-run` from main once
  the construction has ended (POOL line first; ONE-CELL members as declared; AK-IDENTITY; no refusal beyond the expected
  inputs-absent one).
- **L-M1 (LOW, registrar)**: one bracket line in L23098 naming the implementation reading: "AK1's U_s at
  k = L − (one-cell count) on the other sources' TRAIN, each one-cell source at its own k = 1 centroid".

## Commands

```
git diff --stat d3653625 85a6b2fc ; git show 85a6b2fc:tools/analysis/union_af_route.py | awk '/^def ak_compute/,/^def ak_identity_strings/'
sed -n 23098p / 23669,23674p docs/judge_v2_program.md                       # bracket text
(worktree union-af-mirror) python tools/analysis/union_af_route.py --selftest      # 12 / 12
python scratchpad/rp13m/own_mutants5.py      # O13 O14 killed, O15 survived; X79-X84 killed
python -c "U._ROOT[0]=<main>; U.ak_identity(print)"                         # B0 AK-IDENTITY reproduced (no one-cell path)
tasklist /FI "IMAGENAME eq java.exe"                                        # 3 JVMs: build running -> dry-run and full mutants deferred
```
