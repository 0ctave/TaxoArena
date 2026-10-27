# READY_BZ-METER-R17: delta review of [R17] (benchzoom 72a7e66..a5dd424)

Reviewer: adversarial reviewer, 2026-10-11. Scope: `git diff 72a7e66..a5dd424` (4 files, +287/-10), plus regression
checks. Everything that READY_BZ-METER-R16 / READY_BZ-METER-BUILD CONFIRMED on code this delta does not touch is cited,
not re-derived. Zero LLM calls. No write under `E:/benchzoom_demo/meter_v1` or the vault: every run went to the scratchpad.

## Verdict

**READY** for the run order: dry-run, `--calibrate synthetic`, `--calibrate work`, vault sums plus the meter_v1 listing,
then `--vault` once with the default `--out`. This review found no blocker. R16 F1/C5 is settled by (b)+(a), and F2 is
settled by a wording bracket. Three LOW items and one MEDIUM author item are listed below. None of them gates the run.

## Per-claim table (deciding claims only)

| # | claim | mine | status | sev |
|---|---|---|---|---|
| 1 | REG_BLOB `a192f65d…` = LF blob of the registration | `git hash-object` = `git rev-parse a5dd424:docs/meter_registration.md` = a192f65d3e5ac61b132a82fd0620a58f32976054; 0 CR bytes, so the LF and CRLF renderings are identical; runner LF blob 90cb83ced263cc48e0013ebf47c16b378f23b8d1 (WT = HEAD) | CONFIRMED | - |
| 2 | registration edit is insertion-only | `git diff --numstat` gives 65 added, 0 deleted | CONFIRMED | - |
| 3 | synthetic calibration, seed 20261015, R=200: null L1\|L0 z 6.16, others NOT SUPPORTED; planted L1\|L0/L2\|L1/L3k\|C z 7.12/5.51/6.48, L3t\|L2 DEGENERATE; gate PASSED | my run `--calibrate synthetic --out <scratch>`: rc 0. Every g, SE and z matches to the digit (null +9.1216/1.4815; -0.1188/.0911; -0.0366/.0277; -0.0091/.0236; planted +11.5011/1.6157; +6.7571/1.2261; +6.6210/1.0226). Both harnesses pass; null counts are 200 per contrast | CONFIRMED | - |
| 4 | fixture power: planted z ≥ 3.4 on aux seeds (min 4.2); null L1\|L0 ≥ 3.89; no unplanted level reaches z 3 | spot check, named as such: planted seeds 1-3 give min planted z 6.17 / 6.00 / 7.07, unplanted L3t\|L2 at most 0.70; null seed 1 gives L1\|L0 6.24 and unplanted at most \|-2.15\| (below 3, NOT SUPPORTED). All are consistent | CONFIRMED (spot) | - |
| 5 | gate: planted all SUPPORTED AND unplanted none SUPPORTED, on both fixtures; exit 1 on FAILED; `--vault` recomputes the gate and refuses before load | code read (diff L782-811, L841-873); tests gate_values (every site × every bad word, exactly 1 FAIL line), weak_fixture (rc 1), vault_refuses (loaded == []). My mutants O3 and O5 are killed | CONFIRMED | - |
| 6 | the weak (PLANTED-strength) fixture fails at the seed of record (L2\|L1 z 1.22) | test asserts the line `g +0.4687 SE 0.3832 z 1.22 -> FAIL`. Passes in the full suite | CONFIRMED | - |
| 7 | tests 450 passed / 4 deselected; ruff and mypy clean | `.venv` pytest: 450 passed, 4 deselected (282 s); ruff "All checks passed!"; mypy "no issues found in 15 source files" | CONFIRMED | - |
| 8 | builder mutants 16/16 killed | not re-run one by one. The unmutated sandbox copy K0 passes for me (9 passed). My 3 own mutants are below | taken from docstring | - |
| 9 | slope blog rule: HELD fires with no slope planted; 16 models z 4.75..7.44, 64 models -1.82..+0.72 | spot check: pure Rasch seed 1 gives 16 models z 5.4 (g +3.249, SE .601) and 64 models z -0.2 (INCONCLUSIVE). The null fixture with seed 20261015 reads HELD at z 5.4. In range | CONFIRMED (spot) | MEDIUM (D1) |
| 10 | data object untouched: vault sums OK, meter_v1 absent, 0 newer files | `sha256sum -c vault/SHA256SUMS.txt` gives 2 OK (31c111e3…, 4bcd0baf…); `test -e meter_v1` gives ABSENT; `find vault -newer meter_registration.md \| wc -l` gives 0; benchzoom `git status --short \| wc -l` gives 0 | CONFIRMED | - |

Support: the deciding statistics on the real data are unchanged by [R17]. The Support section re-cut at [R16] was
confirmed to the digit in READY_BZ-METER-R16. The synthetic DEFF/n_eff are printed by the run (null L1|L0 DEFF 1.01,
n_eff 595, MDE80 5.69 against g 9.12). These are descriptive and gate nothing beyond the words.

## Own mutants (sandbox copies; `test_meter.py -k "synthetic or gate or fixtures or vault"`)

| id | change | result | decisive |
|---|---|---|---|
| O1 | `gate.txt` written only after the FAILED `return 1` (a failed gate leaves no file) | SURVIVED | no: `--vault` recomputes the gate from outcome.json, but see L2 |
| O3 | `ok = ok and good` changed to `ok = good` (only the last level decides) | killed (3 failed) | yes |
| O5 | z guard `se > 0` changed to `se >= 0` (divide by zero on DEGENERATE) | killed (4 failed) | no |

## Defects

- **D1 MEDIUM (author decision, not a run blocker).** SLOPE FIX HELD is a member of the 10-test Bonferroni family
  ([R5]). On 16-model data with no slope planted it reads HELD in every case reported (seeds 1-10; my seed 1 and the
  null fixture agree). So P1's null is not calibrated for "models differ in slope". The word is still literally true:
  held-out fit improves. [R17] limits the interpretation in writing before the read: HELD is a measurement fix, and
  v_j is "not interpretable". That is the conservative registrar-side settlement. Fix (author): either register a
  no-slope null for the slope test (a parametric bootstrap from the fitted Rasch model at the dataset's own model
  count) before `--vault`, or accept the [R17] wording as final. If the run goes first, the post must never call P1
  evidence of slope heterogeneity.
- **D2 LOW.** The code comment above `SYNTH_FIXTURES` (examples/meter_test.py, [R17] block) says "Both fixtures plant
  at the strength of the test fixture PLANTED: cat_sd .4, fine_sd .3, text_sd .3". The planted fixture is fine .6 /
  text .6. Fix: change the comment to "cat_sd .4 as PLANTED; planted fixture fine_sd .6, text_sd .6 (Section 11
  [R17])". Comment only: the registration and the values are correct, and the REG_BLOB is unaffected.
- **D3 LOW.** Mutant O1 survives: no test asserts that `gate.txt` exists after a FAILED gate. The registration says
  the gate result is written to `gate.txt` on both outcomes, and the code does write it before returning 1. Fix:
  in `test_calibrate_synthetic_weak_fixture_fails_the_gate`, add an assertion that `gate.txt` contains
  "CALIBRATION GATE ([R17]): FAILED".
- **D4 LOW.** `--vault` checks the words in the synthetic outcome files but not which fixture produced them.
  `meta.json` records `fixture=kw`, and nothing compares it with `SYNTH_FIXTURES`. A stale or foreign calibration
  directory would pass if its words matched. This cannot happen on the run of record: meter_v1 is absent and every
  write is write-once. Fix (optional): in the `--vault` refusal block, refuse unless each
  `calibration_synthetic/<nm>/meta.json` `fixture` equals `SYNTH_FIXTURES[nm]`.

## Commands

```
cd Z:/FAC/TUBerlin/benchzoom; export PYTHONPATH=src; P=.venv/Scripts/python.exe
git diff --stat 72a7e66..a5dd424; git diff --numstat 72a7e66..a5dd424 -- docs/meter_registration.md   # 65 0
git hash-object docs/meter_registration.md; git rev-parse a5dd424:docs/meter_registration.md; grep -c $'\r' docs/meter_registration.md
python examples/meter_test.py --calibrate synthetic --out <scratch>/cal; cat <scratch>/cal/calibration_synthetic/gate.txt
$P -m pytest -q -p no:cacheprovider; $P -m ruff check .; $P -m mypy src
$P <scratch>/spot.py   # synthetic_data + meter_core(R=5): planted seeds 1-3, null seed 1, pure Rasch 16/64 models seed 1
$P <scratch>/mut.py    # O0 (unmutated) 9 passed; O1 survived; O3 / O5 killed
cd E:/benchzoom_demo/research_probes && sha256sum -c vault/SHA256SUMS.txt; test -e E:/benchzoom_demo/meter_v1 || echo ABSENT
find E:/benchzoom_demo/research_probes/vault -newer Z:/FAC/TUBerlin/benchzoom/docs/meter_registration.md | wc -l   # 0
```
(scratch = the session scratchpad `r17/`; not committed.)
