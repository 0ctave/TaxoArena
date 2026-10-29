# POSTRUN review: DESIGN-SURFACE (FRESH-DESIGN-SURFACE; SE structure vs fresh items per leaf and roster; EXPLORATORY, MATH WORK only, rule B)

Authority: D-2026-10-27-2 (TaxoArena 2e2513a5, `docs/agents/author_decisions/2026-10-27.md`, incl. the main session's
reading). Reviewer: adversarial reviewer, 2026-10-27. Zero LLM calls. My WORK load read no vault / reserved response
(guard reads 0 at start, 0 at end). At most 3 processes, BLAS 1 (mutants: harness + 2 workers).
Reviewed: benchzoom branch `design-surface` (local), 35b2724..2c8dc80, 4 files, all added (2,556+ / 0-), none under
`src/`. Master is now 6ab459b (6 files of embed2-work / tau-cont-all, none shared): `git merge-tree --write-tree` clean,
not a fast-forward.
- Plan 47d387e (15:41:51); runner + test + draw table cf91977 (17:50:11); run of record 2c8dc80 (23:42:22).
- Run of record: runner `blob:abcabdb57fa4ad8bdf084ba58e3cbd48feffd5af` (LF; sha256-lf16:1387287b7c74983c); all 26 parts
  and 4 builds carry head cf91977, `dirty ""`, tau-grid blob 601416f5, fresh-rules blob f525a403 (= master's).
- Tip 2c8dc80: runner `blob:c975920f` (sha256-lf16:18a0d3f0bce22390; cf91977..2c8dc80 adds 9 docstring lines only), plan
  `blob:7e581266` (5194cfdd64a78f75; 47d387e..2c8dc80 deletes 0 lines), test `blob:e8f7180c` (a3745239aa966537), draw
  table `blob:a5d04869` (sha256 c4d960a4... = the runner's pin). 0 CR bytes in all four: no CRLF rendering.
- Outputs `E:/benchzoom_demo/followups/design-surface`: summary.txt sha256 1f12a55bedbd0e00, SHA256SUMS 5aa498d2847baa6a,
  `sha256sum -c` 65/65; backup `E:/TaxoArena_backup_2026-10-27_design-surface` 99/99 on SHA256SUMS_all, 100 files.

## Verdict

**OUTCOME CONFIRMED (exploratory), with qualifiers.** **merge_ok: yes (MERGEABLE).** No BLOCKER; conditions C1-C4.
- **Rule words after review:** NEST RULE **KILLED** (stands; qualifier C1). PD1 HELD (restates a record, L1), PD2 HELD
  (on its DEFF leg; the rho leg does not discriminate, C2), PD3 HELD, PD4 FAILED.
- **Recomputation.** Every per-design statistic from the parts npz with my own SE code (cluster-robust G/(G-1), two-way
  leaf x K_q averaged over q, MC over 5 partition seeds), leaves and K from the build pickles mapped by my own WORK load:
  25 parts x 8/7 levels x 4 floors x 6 contrasts, max |mine - json| g 0, SE_cc 5.6e-17, SE_cell 4.4e-16, DEFF 9.8e-15,
  m 0. The nest word, PD1-PD3, the roster ratios and the 36 MDE80 cells at R 69 recomputed from those numbers: all equal.
- **The deciding harness, from outside.** S-REPRO covers only the factor-2 mode. I compared the deciding cont mode at
  (n 2,949, R 69, f 80) with TAU-CONT-ALL's cont arrays (`tau-cont-all/parts/math.npz`, sha256 bf5cee9f = its
  SHA256SUMS; harness re-derived from library primitives in POSTRUN_TAU-CONT-ALL 1d23c3c7): 11 arrays, max |diff| 0.
  The nest arm has no outside comparator; it rests on selftest S3 (nest = V0 on a depth-2 tree; null-cell task check;
  planted depth-2 positive control) and mutants X21-X25.

## Per-claim table (deciding claims; x 1e-3 nats per cell)

| # | claim (builder) | mine | status | sev |
|---|---|---|---|---|
| 1 | S-REPRO: g2 = FLAT-COMPARE per item, six digits | 11 arrays max\|diff\| 0; npz sha 6ee133a5 = SHA256SUMS; clusters equal; own SE: +0.1093 (0.0316), +0.2745 (0.0462), +0.3499 (0.0596), -0.1652 (0.0358), +0.0067 (0.0102), +0.2450 (0.0459) | CONFIRMED | - |
| 2 | items per leaf m = fresh items per V0'_f leaf | m = n / leaves occupied by the scored rows: equal (0 diff); e.g. (300, f20) 301 / 109.2 = 2.76, C_total 121 | CONFIRMED | - |
| 3 | rosters and draws frozen before statistics | draw table committed 17:50:11, first part 18:30:23; WORK-ids sha = table's; each part's rows = the table's masks and roster = the frozen prefix (25/25) | CONFIRMED | - |
| 4 | floors 80/50/32/20 -> 36/58/83/121 leaves | pickle sha = sidecar (4/4); leaves recounted | CONFIRMED | - |
| 5 | NEST RULE KILLED | 24 levels, D <= SE at 24, D < 0 at 21, max z +0.436; lowest (300, f20, m 2.7576): D -0.1154, SE 0.0825, z -1.40, DEFF_cc 0.9987, n_eff 301, MDE80 0.1960 | CONFIRMED (word); C1 | MEDIUM |
| 6 | PD1 HELD | SE_cc of P (R 69, f 80) 0.0323 (n 2,949) vs 0.0171 (885) | CONFIRMED; L1 | LOW |
| 7 | PD2 HELD | rho_69 0.03989 (141 points, R^2 0.009); DEFF_cell 3.377 vs 1.462 | CONFIRMED by letter; C2 | MEDIUM |
| 8 | PD3 HELD | 0.2213 / 0.0323 = 6.847 | CONFIRMED | - |
| 9 | roster: x1.6 / x2.3-2.4 / x3.6-4.0 / x5.6-6.9 at R 35/18/10/5 | 1.57-1.60 / 2.27-2.40 / 3.62-3.96 / 5.64-6.85 (5 FRESH contrasts) | CONFIRMED | - |
| 10 | MDE80 at (n 2,949, R 69): D_K 0.150, D_N 0.187, G(N\|L2+V0) 0.157, G(V0\|L2+N) 0.125, P 0.310 / 0.182 | equal; whole R 69 table (6 n x 6 columns) equal at 3 decimals | CONFIRMED (numbers); reading PARTLY, C3 | MEDIUM |
| 11 | SE of P not monotone in n (f 80) | 0.041 / 0.030 / 0.038 / 0.028 / 0.017 / 0.027 / 0.033 / 0.032 | CONFIRMED | - |
| 12 | DEFF_cell grows with m: P 0.96-1.71 (m < 10) vs 2.15-3.38 (m >= 40) | m < 10 over all 14 R-69 cells: 0.96-2.06 (the three 221-level cells 1.81-2.06); 0.96-1.71 on the rule-grid levels only. Spearman(DEFF, m), 32 cells: P +0.70, D_K +0.63, G(N\|L2+V0) +0.73, G(V0\|L2+N) +0.56, D_N -0.29 (p 0.11) | PARTLY; L2 | LOW |
| 13 | constant-rho DEFF form: R^2 <= 0.32 at R 69 | P 0.009, D_K -0.28, D_N -0.33, G(N\|L2+V0) 0.32, G(V0\|L2+N) -0.49 | CONFIRMED (4 of 5 at or below 0.01) | - |
| 14 | F1 extrapolation "not credible" | power.csv prints 40 "EXTRAPOLATED (F1)" rows (P both SEs, D_K, G(V0\|L2+N)): GM ratio in band, point ratios 0.28-90.6, R^2 0.26-0.37 | CONFIRMED in [P2]; C4 | MEDIUM |
| 15 | plan preceded every statistic | plan 15:41 < code 17:50 < builds 17:58-18:12 (text only) < parts 18:30-23:19 < analyze 23:20; 0 of 100 output files older than cf91977; synthetic timing probe 15:36 (no response) | CONFIRMED; L3 | LOW |
| 16 | scope; no src change; graph | 4 added files, `src/` 0; execution_graph.md untouched, correct (its sync test fingerprints src modules; examples-only precedent fresh-rules / tau-cont-all) | CONFIRMED | - |
| 17 | guards | vault_reads 0 in 26/26 parts; my load 0 / 0 | CONFIRMED | - |
| 18 | selftest 18/18; mutants 72/72 | my sandbox control 18/18 PASS; pytest test_design_surface + test_execution_graph_sync 35 passed; own mutants 5/7 killed, 2 survivors non-decisive (L6) | CONFIRMED | - |

## Conditions and defects (each with its fix)

- **C1 (MEDIUM, nest word qualifier).** The SUPPORTED arm had no power for the gain the plan named. The plan's Support
  expected a NEST SE below 0.017 at the lowest level; the run measured 0.0825 (x4.9). MDE80 of the 2-SE leg is 0.196,
  five to ten times the 0.02-0.04 the plan names. Even with single-draw noise, power at a gain of 0.04 is <= 0.07. So
  KILLED rests on negative point estimates (21 of 24), not on a test that could have said SUPPORTED. What the numbers
  carry is the one-sided bound at the lowest level: D + 1.645 SE = +0.020 (single-draw SE). Over the 24 levels it runs
  from -0.011 to +0.093. Fix: copy the word as "KILLED (SUPPORTED leg MDE80 0.196 at m 2.76; nesting gain at the lowest
  level below +0.020, one-sided 95%)". Never copy it as "nesting does not help" without that qualifier. "Trails K'
  everywhere" is true of point estimates only: NEST-K z < -2 at 4 of 24 levels.
- **C2 (MEDIUM, PD2 rho leg non-discriminating).** The DEFF form is a slope through the origin, and x = m - 1 > 0 at
  every point. So rho_69 > 0 holds whenever the (m-1)-weighted mean DEFF exceeds 1, with or without growth (R^2 0.009).
  PD2 is carried by its two-point DEFF leg (3.377 vs 1.462). Fix: record "PD2 HELD (DEFF leg; rho leg not
  discriminating)". The growth evidence is the rank correlation in row 12: it holds for 4 of 5 contrasts and not for D_N.
- **C3 (MEDIUM, reading (5), MDE vs the draft's distances).** The F rows print only the clustered cell SE. That is not
  the deciding SE: D-2026-10-27-5 B (dcbac271, 16:19, after the plan, before the code) makes the meter SE primary. It is
  not the declared rule-B SE_cell either: that one is a resampling SE, here SUBSTITUTED. Corrected MDE80 at
  (2,949, R 69, m* 50.42), under the meter SE (my interpolation, same rule): D_K 0.129, D_N 0.175, G(N|L2+V0) 0.129,
  G(V0|L2+N) 0.082, P 0.182. The pattern is the same as under the cell SE: below 0.17 / 0.25 / 0.25, above 0.062 / 0.10.
  Under the declared resampling SE_cell (POSTRUN_FRESH-RULES-SIM M1: f x1.4-2.0 for D_K), D_K's MDE80 becomes 0.18-0.30,
  above 0.17. So for D_K, "below the draft's distance" does not survive under the cell-aware SE. All of these numbers
  come from one design (the WORK set itself) and contain no rebuild variance, so for rule B they are lower bounds. Fix:
  the record quotes MDE80 under the meter SE, with the cell form beside it labelled "clustered (SUBSTITUTED), lower bound".
- **C4 (MEDIUM, extrapolated rows).** The out-of-sample check passes on a geometric mean whose individual points span
  0.28 to 90.6 (vacuity class: a band on an average). F1's R^2 is 0.26-0.37. Fix: the registrar labels the 40
  EXTRAPOLATED rows NOT CREDIBLE and never quotes them. No n* and no row at 5,000 or 10,000 is licensed.
- **L1.** PD1 and PD2 restate records rather than predict: the 885 level is FRESH-RULES-SIM's F_d and the 2,949 level is
  the WORK set (rows 8 and 9 there). [P2]'s "H1 is confirmed on this surface" should read "consistent with H1 (same
  items)".
- **L2.** The DEFF range quoted for m < 10 leaves out the 221-level cells without saying so (row 12).
- **L3.** `E:/TaxoArena_tmp/design-surface/probe_analyze.py` (19:22, after R69_d0) ran an in-memory analyze on partial
  parts, and the record does not mention it. Nothing changed afterwards: the plan has 0 deleted lines, the runner gained
  docstring lines only, and every part carries blob abcabdb5. Fix: disclose it in the registrar record.
- **L4.** The surface's m counts occupied leaves; m*(n) counts all leaves. At the floors that bracket m* for n <= 885,
  occupancy is >= 99% (f80 36/36, f50 57.6/58), so the effect is negligible. No fix.
- **L5.** The floor-50/32/20 trees are new objects. Under rule B's CHOICE they saw the text of the vault side, as the
  pinned axis_v1 build and FRESH-RULES-SIM did; responses read: 0. They are not candidates for any vault-side object.
- **L6 (selftest gaps; own mutants R2, R3 survived, neither decisive here).** R2: the selftest does not pin the rule's
  level set. With 221 / 442 admitted, the word is still KILLED (lowest 221/f20: D -0.0986, SE 0.1004). R3: the PD2 rho
  leg is not tested (see C2). Fix: add both to S6.

## What the run licenses, and what it does not

Licensed (WORK-side planning input for BZ-AXIS-CONFIRM-FRESH; SE structure only):
- At fixed roster, the SE of the FRESH contrasts is not a function of n alone. At n <= 885 the readers sit near zero
  (C1(V0') |g| <= 0.041 at R 69, every floor), so small fresh sets understate the SE at the planned n.
- Cell clustering rises with items per leaf for 4 of the 5 contrasts (rank correlation), but not in the constant-rho
  form.
- The roster is the strongest lever: going from R 69 to 35 multiplies the SE by about 1.6; going to 5, by 5.6-6.9.
- MDE80 at (n 2,949, R 69): the C3 numbers, as lower bounds for rule B.
- Nesting toward the parent chain shows no gain at any level (C1 bound).

Not licensed:
- No switch of any deciding estimator. The meter SE stays primary (D-2026-10-27-5 B); the clustered cell SE is a
  substitute, not the declared SE_cell.
- No switch of the tree recipe. Floor 50 doubles WORK C1(V0') at 2,949 (+0.2417 vs +0.1161), which is WORK-side
  selection; axis_v1 (floor 80) stays.
- The nest arm does not replace V0' or K'.
- No extrapolated or n* row, and the effect curves are not predictions.
- Nothing about fresh items (the pseudo-fresh items are WORK items that selected V0) or about the vault.

## Own mutants (sandbox copies under `E:/TaxoArena_tmp/review_design-surface/mut/c1`, TMP/TEMP/TMPDIR/BZ_SANDBOX redirected)

| id | change | result | decisive |
|---|---|---|---|
| R0 | control | 18/18 PASS | - |
| R1 | nest rule averages D / SE over defined draws only | killed (S6 cell means / nest levels) | yes |
| R2 | levels 221 / 442 enter the rule | SURVIVED | no (word unchanged) |
| R3 | PD2 rho leg dropped | SURVIVED | no (rho > 0 here) |
| R4 | nest SE divided by sqrt(draws) | killed (S6 nest levels) | yes |
| R5 | lowest-level tie prefers the smaller floor (campaign c2; c1 target matched twice, not applied) | killed (S6 nest rule) | no |
| R6 | KILLED threshold 1.5 SE | killed (S6 nest rule) | yes |
| R7 | PD3 reads SE_cell | killed (S6 predictions) | yes |

## Commands (read-only; scripts in the session scratchpad and `E:/TaxoArena_tmp/review_design-surface`)

```
git -C <wt> diff --numstat 35b2724..2c8dc80 | awk '{a+=$1;d+=$2}END{print a,d}'   # 2556 0; --diff-filter=A --name-only | wc -l -> 4; grep -c '^src/' -> 0
git -C <wt> diff cf91977 2c8dc80 -- examples/design-surface.py   # 9 '+' docstring lines;  47d387e..2c8dc80 plan: 0 '-' lines
git -C <wt> merge-tree --write-tree master design-surface         # clean
find E:/benchzoom_demo/followups/design-surface -type f ! -newermt "2026-10-27 17:50:11" | wc -l   # 0 (of 100)
sha256sum -c SHA256SUMS (65/65); backup sha256sum -c SHA256SUMS_all (99/99)
PYTHONPATH=src <venv>/python ds_recompute.py      # own WORK load (guard 0/0), own CR / two-way / MC SE over all parts; nest word,
                                                  # PD1-PD3, roster ratios, MDE80 table, DEFF ranges, m vs C_total
<venv>/python -c "...g2.npz vs flat-compare/parts/math.npz; R69_d0 L2949 cont vs tau-cont-all/parts/math.npz cont..."  # max|diff| 0 / 0
<venv>/python -c "...surface.csv: spearmanr(m, DEFF) at R 69; meter-SE MDE80 interpolation at m* 50.42..."
<venv>/python E:/TaxoArena_tmp/review_design-surface/rev_mutants.py c1; rev_mutants2.py c2 R5
PYTHONPATH=src <venv>/python -m pytest -q tests/test_design_surface.py tests/test_execution_graph_sync.py   # 35 passed
```
