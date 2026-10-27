# Pre-launch review: benchzoom recalibration v2 script (6ea6266) + criteria edits R1-R6 (21b56b5) + gate defects F1/F2 (c23cd65)

Reviewer: adversarial-reviewer, 2026-10-10. Zero LLM calls, no Ollama, nothing pushed, nothing written under
`E:/benchzoom_demo/calibration_v2` (still absent: `ls` "No such file or directory", before and after). Repo
Z:/FAC/TUBerlin/benchzoom master **6ea6266** (the brief's "HEAD de36610" is stale), tracked tree clean (`git status
--short | wc -l` = 0). Authority D-2026-10-10-1/-2. Prior: READY_BENCHZOOM-CALIB-CRITERIA-V2 (d29aa70f, R1-R6, F1-F2).

## Verdict

- **Script: READY to launch** (criteria Section 9 pre-launch review done). The conditions S1-S2 below change no
  script or criteria blob. The bars are unchanged and must stay so.
- **Criteria edits R1-R6: CONFIRMED as applied** (each `[R<n>]` present, Section 10 keeps the replaced wording verbatim,
  thresholds 5/8/10%, alpha 0.05, 1 SE unchanged). **F1/F2: CONFIRMED.**
- **Per-rule verdicts (RELIABLE / NOT RELIABLE): UNDETERMINED.** No calibration run of record exists, so there are no
  tables to recompute. My own-seed pilot (non-deciding, below) predicts **cg2 NOT ADOPTED via V1b FAIL**, the second
  independent source after the dev cache. Whether to spend about 46 CPU-h is still AUTHOR-1.

## Per-claim table (deciding claims)

| # | claim | own result | status | sev |
|---|---|---|---|---|
| 1 | criteria commit precedes every calibration output | 70e9e79 (17:12) -> 21b56b5 -> c23cd65 -> 6ea6266 (18:27); `calibration_v2` dir absent; 0 outcome files | CONFIRMED | - |
| 2 | criteria LF blob 174a86ce; script b5094b6b; test d0929b6a; lib crossfit 39bc296e / profile 514538f5 / synthetic c037405c / atlas 7a0b5c2a; shapes ff3aee1e | `git hash-object` = `git rev-parse 6ea6266:<f>`; 0 CR bytes in criteria and script (so there is no CRLF rendering) | CONFIRMED | - |
| 3 | `--selfcheck`: criteria OK, library OK, plan 1,024 | same line; registered seeds 1,024 distinct, 1,200,000-1,410,031 | CONFIRMED | - |
| 4 | pytest 260 passed / 4 deselected; ruff, mypy clean | 260 passed, 4 deselected (201 s); "All checks passed"; mypy 13 files OK | CONFIRMED | - |
| 5 | generator = criteria Section 3 | own implementation written from the text: **bit-equal Y and plant sets 40/40** (10 generators x 2 shapes x 2 seeds; libnull = `simulate_shaped`); dense pairs 9 (math) / 3 (mmlu) | CONFIRMED | - |
| 6 | run_one reads what the criteria define | own refit through the public API (mmlu nosubj s=3, own seed base): per-key tau equals the run's `cf` tau; **0 mismatches over 92 model x rule decisions** (`_top`, `_any`); tau_full equal to 4 dp; `atlas.read` uses the same `_cf_cache` key as `atlas.crossfit` | CONFIRMED | - |
| 7 | tables computed as specified (V1a ratio, cluster SE with n/(n-1), t_{n-1}, DEFF, V1b null models, open-fold strata, gate size, V2 counts) | own recompute from the pilot run JSONs agrees **to the digit** with every printed row I checked: cg2/cg1/reg, all open cells in both shapes, gate size per null cell, V2 counts | CONFIRMED | - |
| 8 | Support 6b arithmetic | 0.726 pp / 4.72% (mmlu); 0.593 pp / 4.40% (math); 0.484 / 0.618 pp, MDE 5.52%; t_{7,.975} = 2.365 | CONFIRMED (reproduces) | - |
| 9 | nested V3 masks fold k (leakage selftest non-vacuous) | own O7 (inner fit unmasked) KILLED by test_nested_choice_leakage | CONFIRMED | - |
| 10 | mutants 34/34 killed | `mutants_final.txt`: KILLED 34, SURVIVED 0 (grep -c); re-ran X1 and X7: both KILLED | CONFIRMED | - |
| 11 | test suite guards the deciding paths | own mutants: **5 of 8 SURVIVED** (O2, O3, O4, O5, O8). The code is right on each (rows 5, 6), but no test would catch a regression | PARTLY | MEDIUM (S1) |
| 12 | leakage | synthetic only; `_load_shapes` imports a constants-only module; no EVAL/real items; seeds disjoint (registered 1.20-1.41M, builder scratch 1.9M+, mine 3.0M / 4.0M); V3 masked (row 9) | none found | - |

## Own mutants (copy at E:/TaxoArena_tmp/bz_calib2_review/mut/examples/_mut_dc2.py via BZ_DC2_PATH; full test file)

- O1 planted pair keyed on the planted node, not its subject: KILLED (test_all_pass_adopted). Decisive.
- O2 V3 inner fits ungated (`ga = None`; breaks R6 "same gate_alpha"): **SURVIVED**. Decisive for V3.
- O3 completeness ignores missing V3 fields (`default_plan=default_plan`): **SURVIVED**. Decisive for "of record".
- O4 V1b counts a root descent (`below` includes depth 0): **SURVIVED**. Decisive for V1b; the root fires in practice
  (1/92 model-rules on one nosubj run).
- O5 subject offsets drawn only in hardnull: **SURVIVED**. Decisive (changes G2/G4/G6-G11).
- O6 meta mismatch only prints: KILLED (test_meta_pin_refuses).
- O7 inner cross-fit unmasked: KILLED (test_nested_choice_leakage). Decisive.
- O8 cg2 read from the ungated fit (`"cg2": ("cc", 2.0)`): **SURVIVED**. Decisive.

## Pilot with own seeds (NON-DECIDING; non-default plan, partial by construction; E:/TaxoArena_tmp/bz_calib2_review)

Plans: mmlu at seed base 3,000,000 (16 null / 8 planted seeds, V3 on s<2); math at the same base (8 / 4, V3 on s<1).

- **Gate opens under the null only in mmlu nosubj.** cg2 any-fold open: mmlu nosubj 5/16 (per-fold 11/80 = 13.75%,
  close to the 11.3% development size). hardnull, ceilnull, hard2pl, libnull: 0/16 each, and the ungated cc is 0%
  too. Math: 0/8 in all five null cells (cc nosubj 87.5%, so the gate does work there).
- **cg2 V1a** (open runs only): mmlu nosubj 13/690 = 1.88% (t-up 3.25, DEFF 0.90); dense_0.5 13/816 = 1.59% (t-up 2.57);
  dense_1.0 0.49%; math dense_0.5 10/612 = 1.63%; math residual 14/1224 = 1.14%. All far below 5% / 8%.
- **cg2 V1b**: mmlu nosubj **12/115 = 10.43%** (> 10%); sparse_1.0 mmlu 8/51 = 15.69%; mmlu residual 21/183 = 11.48%
  (enters: FAIL). Pooled with the dev cache, nosubj is 74/529 = 14.0%.
- **V2**: dense_0.5 cg2 - reg: mmlu +19.44 pp [+13.89, +25.00]; math +26.39 pp [+14.81, +37.96]. dense_1.0 mmlu -3.47 pp
  and sparse_1.0 mmlu -22.92 pp (descriptive: the strict rule wins there).
- **V3**: d < 0 in dense 0.5/1.0; d = 0 exactly in every cell where the gate stayed shut (see S2).
- **Own generator** (guessing floor 0.10 on the hard base, a misspecified 3PL-type null that the criteria family does
  not contain; mmlu, 24 seeds, base 4,000,000): cg2 gate open 1/24 (cc 6/24); in that run V1b 3/23 = 13.0%.
- Projection: V1a, V2 and V3 look passable. **V1b is predicted to FAIL** in mmlu nosubj and probably sparse_1.0 mmlu, so
  the run is likely to print NOT ADOPTED. This does not license any change to a bar.

## Conditions / defects

- **S1 MEDIUM (tests; not a launch blocker; script blob unchanged).** Add tests that kill O2, O3, O4, O5 and O8:
  - O2: assert the inner CrossFit carries `gate_alpha == outer.gate_alpha` and `centre_models` (spy on `crossfit`).
  - O3: in main, a cache with one run whose `v3` is null and s < n_v3 must write `*_partial`.
  - O4: a fixture where only the root descends must give `{rule}_any = False`.
  - O5: for every hard-base generator except nosubj, compare the generator to an independent re-draw that includes
    the subject vector (or reuse the reviewer's gencheck).
  - O8: assert `RULES`/`CF_SETTINGS` equal the criteria Section 5 table literally.
  The launch may proceed without S1: rows 5-6 verify the shipped code on these paths.
- **S2 LOW (disclosure in the post-run text, no criteria change).**
  - Under centring plus the gate, open-gate null evidence for V1a/V1b comes only from mmlu nosubj and from the null
    models of planted runs. G1, G2, G4 and G5 will mostly print `0 open / N runs` and reach the verdict only through the
    R1 residual.
  - V3 passes trivially (d = 0, SE = 0) wherever the gate stays shut. Its content is in the dense cells only.
- **S3 INFO.** The brief's HEAD (de36610) is stale; the reviewed tip is 6ea6266.

## Commands

```
cd Z:/FAC/TUBerlin/benchzoom
git rev-parse 21b56b5:docs/calibration_criteria_v2.md 6ea6266:docs/calibration_criteria_v2.md 6ea6266:examples/depth_calibration_v2.py
for f in crossfit profile synthetic atlas; do git hash-object src/benchzoom/$f.py; done; tr -cd '\r' < <file> | wc -c
ls E:/benchzoom_demo/calibration_v2          # absent
.venv/Scripts/python.exe examples/depth_calibration_v2.py --selfcheck
.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider; .venv/Scripts/ruff.exe check .; .venv/Scripts/mypy.exe src
python E:/TaxoArena_tmp/bz_calib2_review/own/gencheck.py      # bit-equal 40 of 40
python examples/depth_calibration_v2.py --out E:/TaxoArena_tmp/bz_calib2_review/pilot_mmlu --workers 12 --seed-base 3000000 --null-seeds 16 --plant-seeds 8 --v3-seeds 2 --shapes mmlu
python examples/depth_calibration_v2.py --out E:/TaxoArena_tmp/bz_calib2_review/pilot_math --workers 8 --seed-base 3000000 --null-seeds 8 --plant-seeds 4 --v3-seeds 1 --shapes math
python E:/TaxoArena_tmp/bz_calib2_review/own/rerun_one.py nosubj mmlu 3 E:/TaxoArena_tmp/bz_calib2_review/pilot_mmlu   # 0 mismatches / 92
python E:/TaxoArena_tmp/bz_calib2_review/own/recompute.py <pilot>/runs                 # own tables, digit agreement
python E:/TaxoArena_tmp/bz_calib2_review/own/owngen.py 24 12; recompute.py .../owngen  # own generator
python E:/TaxoArena_tmp/bz_calib2_review/own/mutants.py; mutants2.py                    # O1-O8, X1, X7
grep -c KILLED E:/TaxoArena_tmp/bz_calib2/mutants_final.txt                              # 34 (SURVIVED 0)
```
