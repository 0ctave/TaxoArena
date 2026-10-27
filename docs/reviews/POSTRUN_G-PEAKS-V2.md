# POSTRUN G-PEAKS-V2 (adversarial review, 2026-10-11)

## Verdict: NOTHING RAN (no post-run review possible; neither VALID nor INVALID)

There is no G-peaks v2 registration, no v2 runner, no calibration or power run and no held-out readout,
so no post-run claim exists to grade. This review only confirms that absence, using counts.
v1 remains closed, and may be quoted only with "method power failed" (D-2026-10-11-7). For v2 the outcome of record is the
tuning bench's "NO DETECTOR MEETS THE TARGET" (0/40 eligible), confirmed in READY_G-PEAKS-V2-CLOSURE (fe0ad848).

## Claims (deciding only)
| # | Claim (engine report) | Own check | Result | Sev |
|---|---|---|---|---|
| 1 | No v2 registration exists | `ls docs \| grep -i peaks` gives 3 files: peaks_registration.md (v1), peaks_tune_rule.md, peaks_v2_closure.md; `git log --all -- 'docs/peaks_v2_registration*'` gives 0 lines | CONFIRMED | - |
| 2 | No v2 runner / implementation | `git log --all -- 'examples/peaks_test_v2*'` gives 0 lines; `grep -c v2 src/benchzoom/peaks.py` = 0 | CONFIRMED | - |
| 3 | No execution_graph Stage D v2 / manifest update | last commit touching docs/execution_graph.md = 9e3937f (v1 Stage D, 07:23) | CONFIRMED | - |
| 4 | No commits by engine coder in this step | benchzoom HEAD = 779811d (closure note, `--name-only \| grep -c .` = 1 file: docs/peaks_v2_closure.md); `git status --short \| wc -l` = 0 | CONFIRMED | - |
| 5 | No v2 outputs anywhere | `find` for `*peaks*v2*` in the benchzoom tree and in E:/benchzoom_* finds only docs/peaks_v2_closure.md; no file newer than the closure note (count 0) | CONFIRMED | - |
| 6 | Gate correctly refused | D-2026-10-11-7 requires recovery >= 0.80 *before* registering v2; the bench gives 0/40 eligible; READY_G-PEAKS-V2-CLOSURE says CHANGES (wording only) | CONFIRMED (refusal is mechanical) | - |

Pins: docs/peaks_v2_closure.md LF blob `619717dc90f72e22494822df879d46e0cf8d5c20` (`git hash-object`).

## Plain-language summary (what the pockets show)
None. No v2 pocket has been detected, named or sized, and nothing has tested whether reading pockets predicts better.
On synthetic data the tuned detectors recovered almost no planted 5% pockets (38/40 detectors 0/60, best 2/60).
A detector that is given the true centre recovers 60/60. So the pockets were missed by these detectors, not
impossible to detect. The fair wording is "not detected by the tuned detectors", not "no pockets".

## Defects / conditions
- P1 (LOW, registrar): apply the closure-note wording edits E1-E4 of READY_G-PEAKS-V2-CLOSURE to benchzoom docs/peaks_v2_closure.md (insertion only).
- P2 (gate): any v2 run needs (i) the author's choice among options (a)/(b)/(c), (ii) under (a) a bench that passes the
  >= 0.80 recovery target (E5-E6 of the closure review), (iii) a fresh registration with a Support section and an APPROVED pre-data
  review. Until all three hold, this file stands as "nothing ran".

## Commands
```
cd benchzoom; ls docs | grep -i peaks; git log --all --name-only --format=%h -- 'examples/peaks_test_v2*' 'docs/peaks_v2_registration*' | wc -l   # 0
grep -c v2 src/benchzoom/peaks.py                      # 0
git log -1 --format=%h -- docs/execution_graph.md      # 9e3937f
git show 779811d --name-only --format= | grep -c .     # 1
git status --short | wc -l                             # 0
find . -newer docs/peaks_v2_closure.md -type f -not -path './.git/*' | grep -v __pycache__ | wc -l   # 0
find /e/benchzoom* . -iname '*peaks*v2*'               # only docs/peaks_v2_closure.md
```
