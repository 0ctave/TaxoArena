# READY review: BZ-METER [R18] (v2) delta, benchzoom e1fb080..9a42c49

Reviewer: adversarial reviewer, 2026-10-12. Zero LLM calls. Zero vault reads by me: every run used WORK rows, synthetic
data, or `--dry-run`. Nothing was written to `E:/benchzoom_demo/meter_v1` or `meter_v2`; `meter_v2` is absent (`ls` exit 2).
Scope: delta review of 58c93a0 + afede98 + 9a42c49. The prior reviews READY_BZ-METER-R17.md and POSTRUN_BZ-METER-v1.md
cover the code the delta does not touch.

## Verdict: READY for the v2 run sequence
The order is: dry-run -> `--calibrate synthetic` (gate must read PASSED) -> `--calibrate work` (exit 0) -> record the
vault and meter_v1 sums and an empty meter_v2 listing -> `--vault` once, `--out E:/benchzoom_demo/meter_v2`.
Conditions:
- C1. Run every command with the default `--datasets`. `--calibrate work` takes the split index from the argument order (E4).
- C2. `--vault` exit 1 with state HARNESS FAILED is a VALID outcome, not a reason to re-run. A crash after the vault
  opens (E6) is a stop-and-report event; the operator does not re-launch without a review.
- C3. The deviation from the brief (slope null = Rasch within category, not plain Rasch) is ACCEPTED as the more
  conservative option. Its q95 is higher on every WORK line and on every synthetic seed (claim 6). It was chosen on
  synthetic auxiliary seeds only, and the WORK words do not change.

## Per-claim table (deciding claims)
| # | claim | my number | status | sev |
|---|---|---|---|---|
| 1 | registration insertion-only; REG_BLOB = LF blob | 0 removed lines in the reg diff; `git hash-object` = `rev-parse 9a42c49:` = REG_BLOB = 5c457088a52e11eecb621d945a87e033eff9859f; index and worktree are both LF (`ls-files --eol`), so there is no CRLF rendering to report | CONFIRMED | - |
| 2 | settlement and operator record untouched | 0 of 6 changed files match settlement or operator_record (`diff --name-only \| grep -c`) | CONFIRMED | - |
| 3 | tests 469 passed, 4 deselected; ruff, mypy clean | 469 passed, 4 deselected (427 s); ruff "All checks passed"; mypy "no issues, 15 files" | CONFIRMED | - |
| 4 | WORK harness misfire: [R18] 0/20 MATH, 0/19 MMLU-Pro; two-sided mean rule 11/20, 6/19 | recomputed from the draws in support_r18_{math,mmlu_pro}.json (SHA256SUMS OK): 0/20 and 0/19; two-sided 11 and 6; G-bar/SE min -3.92 / -2.67, max 0.06 / 0.51; one-sided draws 1/400 and 0/380; two-sided draws 10 and 7; G<0 109 and 71; tau2=0 262 and 282; [R7] draw-0 failures 1 and 1; MMLU-Pro split 5 LinAlgError('Singular matrix'); every stored `passed` equals the rule recomputed from the draws | CONFIRMED to the digit | - |
| 5 | binomial c = 2 | p 0.02275; P(Bin(20,p) > 1) 0.0750; P(> 2) 0.0100 | CONFIRMED | - |
| 6 | slope null on WORK (per-category, R 200, 0 failed) | MATH-69 g +4.2278 SE 0.4446 q95 +0.4921 (np.quantile recomputed from the 200 gains: +0.4921) mean +0.3345 sd 0.1120 DEFF 1.44 n_eff 819; MATH-22 +11.1320 / 1.1649 / +1.8154 / +1.4122 / 0.2795, DEFF 1.08 n_eff 1098; MMLU-Pro +8.9335 / 0.6007 / +0.1544 / +0.0158 / 0.0914, DEFF 1.23 n_eff 2337; all HELD. Plain-null q95 +0.4218 / +1.5644 / +0.0531 | CONFIRMED to the digit | - |
| 7 | synthetic spot check: per-category null HELD on 0/10 null seeds, 10/10 planted; plain null 3/10 (seeds 3, 4, 8) | 0/10 and 10/10; plain [3, 4, 8] and 10/10; [R13] alone HELD 10/10 on the null fixture; q95 3.60-4.88 vs g 2.49-4.48 | CONFIRMED | - |
| 8 | the synthetic gate PASSES at the seed of record (null INCONCLUSIVE g +3.7592 q95 +4.1233; planted HELD g +13.0006 q95 +5.8521) | my `--calibrate synthetic --out <scratch>` at 9a42c49 (clean): same four numbers; all level words ok; harness PASSED on both fixtures (null G-bar -0.0473 SE 0.0221, 0/20; planted -0.0346 SE 0.0170, 0/20); GATE PASSED, exit 0 | CONFIRMED | - |
| 9 | the real `--dry-run` reads 0 vault rows | my run at 9a42c49: "DRY-RUN OK: 0 vault response reads", v1 record OK (sha af1f8042..., HARNESS FAILED), exit 0 | CONFIRMED | - |
| 10 | power against a planted leak: MDE about 0.004 x1e-3 | arithmetic reproduces (2.84 x 0.0019 x sqrt(1181/1960) = 0.0042; MMLU-Pro 0.0038). Under a leak, though, the SE grows. Dose-response on the WORK pseudo-vault I planted (leak eps x own residual, the `_leaky_reader` mechanism): MATH s0 eps 0 / .02 / .05 / .1 / .2 gives G-bar -0.0038 / -0.0047 / +0.0017 / +0.0256 / +0.1477, PASS PASS PASS FAIL FAIL; MMLU-Pro s1 -0.0046 / -0.0066 / +0.0059 / +0.0765 / +0.4352, FAIL from eps .1. Detection starts at a shift of about +0.03 (MATH) and +0.08 (MMLU-Pro), both below delta_min 0.10 | PARTLY (the threshold is real but 7-20x the stated MDE) | LOW (E2) |
| 11 | code = registration (C-7) | K 20, z 2, c from the binomial bound, stream [20261012,0,k]; R_SLOPE 200 >= 100; stream [..,7,r]; LinAlgError counts +inf; q95 = +inf at >= 10 failures (handles the inf-inf case); HELD needs g > q95 on ALL; the 22-model word reads its own q95; dropped rows excluded (Y = rows work\|keep) | CONFIRMED | - |
| 12 | mutants 43/43 (builder) | my mutants below: 3 of 4 killed; the survivor is not decisive | PARTLY | LOW (E1) |
| 13 | Support section non-vacuous | DEFF printed beside each slope g; n_eff and MDE80 = 3.84 SE reproduce; deciding denominators 1,960 / 4,654 scored (dry-run); SCOREABLE | CONFIRMED | - |

Own mutants (sandbox copies `git archive 9a42c49`, each its own git repo; `test_meter.py -k "r18 or v1_record or
calibration_meta or harness or slope or vault or calibrat"`, 34 tests; K0 34 passed):
- Ma `v1_record_ok` sha check disabled: killed (test_v1_record_ok_values). Decisive.
- Mb `calibration_meta_ok` default `dirty` "x" -> "": SURVIVED. Not decisive: `code_state()` always writes `dirty`.
- Mc harness draw stream k -> k+1 (draw 0 no longer the [R7] draw): killed (null_fixture_negative_mean_passes). Decisive.
- Md HELD allowed when q95 is non-finite: killed (failed_replicates_are_fail_closed). Decisive.

## Defects (none blocking)
- E1 LOW. Mutant Mb survives: no test passes `calibration_meta_ok` a meta whose `code` has a commit but no `dirty`
  key. Fix: add that case to test_calibration_meta_ok_values and expect a refusal.
- E2 LOW. The "MDE 0.004" in Section 6 [R18] uses the no-leak SE(G-bar), and it ignores the negative optimism
  (G-bar about -0.004) that a leak must overcome first. On WORK the empirical detection threshold is a shift of about
  +0.03 (MATH) and +0.08 (MMLU-Pro) x1e-3 nats, still below delta_min. Fix: the post-run record quotes the empirical
  WORK figures above, not 1/25 of delta_min.
- E3 LOW. The null holds abilities fixed within each declared category only. Finer-label and text offsets that
  correlate with difficulty are not in it (disclosed in §4.2), and Section 9 adds the "within category" qualifier only
  when the word is not HELD. Fix (post wording, no code): when HELD, write "beyond a within-category no-slope Rasch null".
- E4 LOW. `--calibrate work` uses `enumerate(datas.items())` for the split index; the Support used
  `DATASETS.index(ds)`. They are equal under the default `--datasets` (C1). Fix in a later build: use `DATASETS.index`.
- E5 LOW. The afede98 message says "45/45"; the correct count is 43, corrected in the docstring and in 9a42c49.
  Record only.
- E6 LOW. Only the slope-null replicates catch `LinAlgError`. The chain refit and harness draws 1-19 on the vault are
  not guarded, while v1 exercised only the chain and draw 0. The fit is deterministic and v1 completed both datasets,
  so a crash is unlikely. If one happens: stop and report (C2); the meta/resume rules apply.

## Commands (benchzoom at 9a42c49, clean; P = .venv/Scripts/python.exe; PYTHONPATH=src)
```
git diff e1fb080..9a42c49 -- docs/meter_registration.md | grep '^-' | grep -vc '^---'      # 0
git hash-object docs/meter_registration.md; git rev-parse 9a42c49:docs/meter_registration.md; git ls-files --eol ...
git diff --name-only e1fb080..9a42c49 | grep -c "settlement\|operator_record"               # 0 (of 6, wc -l)
$P -m pytest -q; $P -m ruff check .; $P -m mypy src                                         # 469 passed, 4 desel.
$P examples/meter_test.py --dry-run                                                          # 0 reads, exit 0
$P examples/meter_test.py --calibrate synthetic --out <scratchpad>/cal_out                   # GATE PASSED, exit 0
python <inline>: recompute rule/counts from support_r18_*.json draws; np.quantile of slope gains
<scratchpad>/leak_dose.py {math 0 | mmlu_pro 1}: pseudo_vault + _leaky_reader-style eps leak -> harness_check_r18
sha256sum E:/benchzoom_demo/meter_v1/outcome.json E:/benchzoom_demo/research_probes/vault/*_vault.json
  # af1f8042...ca67b; 31c111e3...2975; 4bcd0baf...11e2
mutants: <scratchpad>/rv/{K0,Ma,Mb,Mc,Md}, pytest -k subset (34 tests)
```
