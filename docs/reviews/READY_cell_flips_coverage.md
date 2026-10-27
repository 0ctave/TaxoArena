# READY — CELL-FLIPS and COVERAGE-AUDIT (two zero-call readouts on the UNION-AF-ROUTE objects)

Reviewer: adversarial-reviewer, 2026-10-04. Zero calls, no JVM, no key read, no statistic computed. Object: branch
`cell-flips-coverage` tip aa5ddf04 (worktree `.claude/worktrees/cell-flips-coverage`), parent fac3d50b; the commit touches 3 files
(`git diff --name-only fac3d50b aa5ddf04 | wc -l` = 3). Registrations: prog L24143-L24154 (CELL-FLIPS), L24156-L24167
(COVERAGE-AUDIT), _as_of fac3d50b; no bracket after either (grep of both ids: headings 24143 / 24156 only, after the record 24118).

Pins (LF of record; the worktree bytes ARE the LF rendering, so no CRLF variant exists):
| file | blob (LF) | sha256-lf16 = working-tree bytes |
|---|---|---|
| tools/analysis/cell_flips.py | 998d39a7b718faa6647c4d5795dcf03044544955 | 8d5afad30919bb1b |
| tools/analysis/coverage_audit.py | 69c5526826e9a7af24481e6818067cceb1a5b9b7 | cdd4652df5767b58 |
| tools/analysis/union_cells_io.py | 92a04543b9c75eae5f37a76ae86eb189a190a9bd | 2bf4a9f441a42d3f |
| tools/analysis/union_af_route.py (imported, unchanged) | bf3f17dbdc42dbfc6803687d8739d459fc1ed75d | 50524cdfedde3256 |

## Verdict

- **CELL-FLIPS (cell_flips.py 998d39a7): READY**, with registrar brackets B-1, B-2, B-3 entered BEFORE `--run` (no code change).
- **COVERAGE-AUDIT (coverage_audit.py 69c55268): NOT READY as of this blob.** It implements the registered rule faithfully, but the
  deciding D_X carries a one-sided IFEVAL filing asymmetry (D-1, HIGH) whose cap (0.0274) exceeds the TOST margin (0.020). READY
  after: D-1's descriptive prints added, the registrar's bracket B-4 (which filing decides) and B-5 (CV-R2 dominance), and a delta
  review of that diff only (selftests + mutants + the two new lines).

## Per-claim table (deciding paths)

| # | claim | builder | mine | verdict | sev |
|---|---|---|---|---|---|
| 1 | EVAL set | 5,907 / 5,404 | 5,907 / 5,404 (own script through `U.eval_set(key=False)`); eval_view sha e35b7518 before = after | CONFIRMED | — |
| 2 | g | Qwen2.5-72B-Instruct (frozen best_single) | same, policy sha 8d68018c = pin | CONFIRMED | — |
| 3 | CF TESTED AF-U / K_0 / declared | 101 / 94 / 44 | 101 / 94 / 44 (own Counter over af_cells / k_cells_s0 / view labels × policy picks); pick = g 20 / 22 / 5; small 2 / 7 / 3; **absent picks 0 / 0 / 0** (CF-R1 fallback never fires: not vacuous); TESTED median n 45 / 45 / 75 | CONFIRMED | — |
| 4 | CF selection on TRAIN | picks frozen, g frozen | code: picks from `pol` only; M10 / M11 (EVAL re-choice) killed | CONFIRMED | — |
| 5 | CF BH q 0.05 per arm over TESTED | step-up, m = arm's TESTED | code L157-L181; M05-M08 killed; first rejection p ≤ 0.05/101 = 0.000495, reachable (floor 1/10,001 = 0.0001) | CONFIRMED | — |
| 6 | CF Support (d)-(e) | SE 0.083; D ≥ 0.27 at n 48, 0.15 at n 150 | sqrt(0.30×1.10/48) = 0.0829; 3.29×0.0829 = 0.273; sqrt(0.33/150)×3.29 = 0.154; DEFF source named (POSTRUN_union_af_route one-stage 1.03/0.99/1.02) | CONFIRMED | — |
| 7 | CF Kish (a) | prints "Kish mean cluster size 1.3115 (registered 1.09)" | Σn²/Σn = 1.3115; 5,907/5,404 = 1.093: two definitions under one name | PARTLY (D-3) | LOW |
| 8 | CV Support (b)-(e) | DEFF 1.102 (AK1), SE 0.00432, reach 0.0093 / 0.0236 | sqrt(0.10×1.102/5,907) = 0.004319; 0.020 − 2.487×0.004319 = 0.00926; 0.020 + 0.842×0.004319 = 0.02364; +0.005 sits 0.0043 inside | CONFIRMED | — |
| 9 | CV like with like (AF-U vs K_0 nearest of all) | "both label-free fits filed nearest of all" | AF-U files IFEVAL BY SOURCE (one-cell graft): 162/162 IFEVAL EVAL items in IFEVAL:n00000001, 0 non-IFEVAL items in it; K_0 has IFEVAL k = 1 searched by every item | REFUTED for IFEVAL (D-1) | HIGH |
| 10 | CV per-member n | BBH 1716, GPQA 34, IFEVAL 162, MATH 390, MMLU_PRO 3376, MUSR 229; 0 outside the bundle | same (dry-run, re-run) | CONFIRMED | — |
| 11 | CV1 rule / rule 8 / F-CV | strict 90% inside ±0.020; DIFFERENT |D| > 0.020 and 95% excludes 0 | code `cv1()`; V10-V17 killed; R6 killed | CONFIRMED | — |
| 12 | Selftests | CF 8/8, CV 5/5 | re-run: 8/8, 5/5 | CONFIRMED | — |
| 13 | Mutants | CF 40/40, CV 36/36, controls survive | re-run: 40/40, 36/36, controls survive | CONFIRMED | — |
| 14 | Dry-runs read-only | nothing written | both rc 0; POOL line first (B0-2 rc 0); manifest 53021e26 = pin; mtimes/sizes of policy, 6 cell TSVs, bundle, embeddings_cache.db, multicorpus_cache_v1.db equal before/after (diff empty); `ls experiment_results/archv2 \| grep -c 'cell_flips\|coverage_audit'` = 0 | CONFIRMED | — |

## Own mutants (8; run through each script's harness, all selftest cases)

R1 CF ratio denominator = cell items (not drawn items): KILLED, decisive. R2 CF one-sided p in the wrong tail: KILLED, decisive.
R3 CF one rng seed for all arms: **SURVIVED**, non-decisive (the seeds are not pinned by any test; see B-1). R4 CF n_EVAL counted in
components: KILLED, decisive. R5 CV dominance from EVAL rows: KILLED, decisive. R6 CV EQUIVALENT from the 95% interval: KILLED,
decisive. R7 CV component ratio over n items: KILLED, decisive. R8 CV D_X sign reversed: KILLED, decisive.

## Readings: confirmed, or needing a registrar bracket

| reading | status |
|---|---|
| CF-R1 absent pick → g, untested | CONFIRMED; 0 absent in every arm (claim 3) |
| CF-R2 n ≥ 20 inclusive, on the 5,907 set | CONFIRMED = registration |
| CF-R3 component bootstrap, ratio estimator, B 10,000, floor | CONFIRMED; **seeds 20261004 + j unregistered → B-1** |
| CF-R4 BH per arm, ties by name | CONFIRMED (ties cannot split a step-up rejection set) |
| CF-R5 tau-b, constant vectors NaN dropped, P4 on AF-U | descriptive; record in B-1 (42 AF-U cells n ≥ 50, P4 scoreable) |
| CF-R6 measured DEFF per TESTED cell | descriptive, CONFIRMED |
| CF-R7 closed bands, Brier | CONFIRMED (programme convention) |
| CV-R1 member naming (MMLU_PRO_LB → MMLU_PRO) | CONFIRMED (I01 killed) |
| CV-R2 dominance from TRAIN rows filed by EACH ARM'S OWN rule (AF-U flatLeaf modal R1, K_0 nearest of all, declared nearest centroid) | **DECIDING, not in the registration text → B-5** |
| CV-R3 tie → sorted-first member; empty cell → construction member | **→ B-5** (counts printed) |
| CV-R4 X item-weighted, D_X item-paired | CONFIRMED = registration |
| CV-R5 B 2,000, percentile rule; DEFF = Var_comp/Var_iid on D_X | **seeds 20261004 / 20261005 unregistered → B-1**; DEFF measured on D_X, printed beside the transported 1.102 (descriptive) |
| CV-R6 strict 90% ends | CONFIRMED ("lies inside") |
| CV-R7 OOS from GATE, TPR 0.95, AF-U | descriptive, CONFIRMED (V23-V25 killed) |
| CV-R8 multi-outcome Brier; P2 order | CONFIRMED |

## Defects

- **D-1 (HIGH, COVERAGE deciding).** The AF-U flatLeaf graft omits the one-cell member IFEVAL; its items are filed to IFEVAL:n00000001
  BY SOURCE and no other member's item can enter it (claim 9). K_0 "nearest of all" searches K0:IFEVAL:000 for every item. So on the
  162 IFEVAL items f_AF ≡ 0 while f_K0 ≥ 0, and foreign items filed into K0:IFEVAL:000 raise f_K0 only: the term is one-sided toward
  TREE-LESS-MIXED; from IFEVAL items alone it can reach −162/5,907 = −0.0274, beyond the ±0.020 margin. It can manufacture EQUIVALENT
  or suppress F-CV. Registration (g) describes the K_0 side only. FIX: print, descriptively, (i) D_X with the K_0 side MIRRORED
  (IFEVAL TRAIN/EVAL rows → K0:IFEVAL:000; every other row nearest among the 122 non-IFEVAL centroids: the C-S1 precedent of
  UNION-AF-ROUTE) with its interval, and (ii) D_X over the 5,745 non-IFEVAL items; add both to the selftest oracle and one mutant
  each; then B-4.
- **D-2 (MEDIUM, CELL-FLIPS wording).** D-4 holds: K_0 files by TRUE source (mirrored, registered) while AF-U's flatLeaf searches all
  leaves; K_0 FLIP and TESTED counts are no like-for-like comparator of AF-U's. The outcome prints only "K_0 is not like with like on
  labels". FIX (wording, no code): the registrar carries D-4 into the outcome record; no AF-U vs K_0 FLIP-count contrast.
- **D-3 (LOW).** "Kish mean cluster size" prints Σn²/Σn = 1.31 beside the registered 1.09 (= 5,907/5,404, the plain mean). FIX: B-1
  names both; optional print fix at D-1's delta.
- **D-4 (LOW, disclosure).** P1's TESTED band [45, 100] already FAILS from structure: 101 TESTED (dry-run, key sealed). Knowable at
  registration; it must be scored FAILED and labelled structural (B-2). The BH bar is q/101.
- **D-5 (LOW, disclosure).** COVERAGE P2's GPQA band and the "GPQA first" order rest on n 34 (SE of a proportion near 0.45 =
  sqrt(0.45×0.55/34) = 0.085, before DEFF); MATH n 390. B-3.

## Brackets needed (registrar, insertion only, before the respective --run)

- **B-1** (both): bootstrap streams as committed in aa5ddf04: CF default_rng(20261004 + j), j = 0 AF-U, 1 K_0, 2 declared, cells in
  sorted name order, TESTED cells only; CV default_rng(20261004) component, default_rng(20261005) i.i.d.; CF-R5's NaN rule; Kish
  definition (D-3).
- **B-2** (CELL-FLIPS): P1 TESTED = 101 > 100 is a structural FAILED known pre-key; D-2's D-4 wording.
- **B-3** (COVERAGE): GPQA n 34 disclosure for P2.
- **B-4** (COVERAGE, deciding; the registrar's call, the author's if contested): whether CV1 is decided by the registered nearest-of-all
  K_0 filing (mirrored and IFEVAL-excluded D_X descriptive beside) or by the mirrored filing (precedent C-S1); fixed before any run.
- **B-5** (COVERAGE, deciding): adopt CV-R2 (dominance = TRAIN rows filed by the arm's own filing rule; "the most TRAIN rows in it" is
  trivial under construction membership, where every non-empty AF-U leaf and K_0 centroid is single-source) and CV-R3 (ties, empty
  cells); X under construction-member dominance stays descriptive (printed).

## Commands

```
git -C <wt> hash-object tools/analysis/{cell_flips,coverage_audit,union_cells_io,union_af_route}.py ; git show aa5ddf04:<f> | sha256sum
git diff --name-only fac3d50b aa5ddf04 | wc -l                                  # 3
python tools/analysis/cell_flips.py --selftest      # 8/8      ; --mutants  40/40, control survived
python tools/analysis/coverage_audit.py --selftest  # 5/5      ; --mutants  36/36, control survived
python tools/analysis/{cell_flips,coverage_audit}.py --dry-run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena   # rc 0 both
scratchpad/rvcf/rv_struct.py   # own recount, no key: 5907/5404; TESTED 101/94/44; absent 0/0/0; IFEVAL 162 in one AF cell, 0 foreign
scratchpad/rvcf/own_mut.py     # R1-R8 via each script's run_mutants: 7 killed, R3 survived (non-decisive)
stat -c '%Y %s' <policy, cell TSVs, bundle, caches> before/after: diff empty; E:/TaxoArena_tmp: no cell_flips_*/coverage_audit_* left
python: sqrt(.30*1.10/48)=.0829; sqrt(.10*1.102/5907)=.004319; .020-2.487*.004319=.00926; .020+.842*.004319=.02364; 162/5907=.0274
```
