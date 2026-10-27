# DELTA review: BZ-AXIS-CONFIRM-MMLU WORK-1 crash fix (benchzoom 9f6182f..3ef4b06, branch irt-damped)

Reviewer: adversarial reviewer, 2026-10-22. Zero LLM calls. WORK side only (`guard.masked()`); the vault was never
opened. Nothing written under `E:/benchzoom_demo` or the benchzoom checkouts (both `git status --short | wc -l` = 0
after the runs). Scope: `git diff 9f6182f..3ef4b06` (7 files, +262/-21): 4cfeb77 (`irt.fit_theta_slope` line search,
maxit 50 -> 500) and 3ef4b06 (`sources._hub_call` gated order, D5 of READY1_BZ-MMLUPRO-MOREMODELS).

## VERDICT

**CORRECT. The branch may merge to master, and the WORK step may re-run.** Conditions:
- **C1 (MEDIUM, before the VAULT, not before WORK):** the synthetic gate has to be re-run on the MERGED library
  before any vault read. The existing `calibration_synthetic_01e40f15f483` gate was written by the old `irt.py`, and
  `synthetic_refusal` binds only the runner blob, so on its own it would accept that outdated gate. Today this is
  forced anyway: `SECTION_SHA = "PENDING"` changes the runner blob at READY-2, so the gate re-runs under the new
  library. WORK is not gated by the synthetic run (`main`: the `work` branch calls only `ready1_gate`).
- **C2 (MEDIUM, disclosure):** the builder's claim covers HELM only. The tinyBenchmarks roster (also loaded by
  `load_real` and read by `run_work`) has **6 columns that raised under the old code** (310, 333, 342, 350, 351, 360)
  and 2 columns that move by 1 ulp (321, 368). The [A1] / WORK record must carry these counts beside HELM's 7 + 1.
  Several of the columns that raised are WEAK models (HELM col 6, accuracy 0.281; tinyB accuracy 0.27-0.31, v about
  0.8-0.9), so "strong models" in the docstring, the commit message and the graph does not cover every case.

## Per-claim table (deciding claims)

| # | Claim | Mine | Status | Sev |
|---|-------|------|--------|-----|
| 1 | Objective = penalised log-lik whose gradient is the Newton g | `_slope_objective` = sum M(y eta - logaddexp(0,eta)) - pt t^2/2 - lam v^2/2; d/dt, d/dv match g in both branches (pt=0 / pt>0) | CONFIRMED | - |
| 2 | Acceptance cannot change a result where every full step is taken | the iterate update is `t + a[0]` with `a = step` (the same float ops as before); f2 is only read. Real data: MATH 69/69 bit-identical; MMLU-Pro-23 22/23 (col 16, \|d\| 2.2e-16); HELM 71/79 (col 30, \|d\| 2.8e-17; 7 raised) | CONFIRMED (1 ulp, as claimed) | - |
| 3 | 7 HELM cols (6,12,13,15,22,28,65) raised before and now converge | the same 7; \|grad\| in longdouble at the returned value <= 4.7e-13; -Hessian PD (min eig >= 112) -> strictly concave -> unique maximiser | CONFIRMED | - |
| 4 | Same optimum as an independent solver | scipy `root` (hybr) on an independently written gradient, started from (1, 0.3): \|dz\| <= 2.2e-15 on all 16 changed cols (HELM 8 + tinyB 8); Nelder-Mead on an independent nll from (-2, -0.5): \|dz\| <= 2.4e-7, nll(new) - nll(NM) <= 1.1e-10 (NM is the cruder one) | CONFIRMED | - |
| 5 | Convergence criterion not weakened | stop still on the FULL step `np.abs(step).max() < tol`, tol 1e-9 unchanged; the new exit (no halving helps) only fires after 51 failed trials at step/2^50 | CONFIRMED | - |
| 6 | maxit 50 -> 500 is harmless | no column on any roster was unconverged at 50 under the old code; the new code needs at most 10 steps (HELM) / 8 (tinyB); maxit=50 gives the identical value on every HELM/tinyB column | CONFIRMED (inert on the data) | LOW |
| 7 | Numbers of record untouched (MATH L3a\|L2 +0.259 / SE 0.063; MMLU-Pro NOT SUPPORTED) | those are vault reads already on record and are not re-run. A re-run would differ by at most the backbone ulps shown in row 2; MATH backbone is bit-identical on WORK | CONFIRMED (no number of record moves) | - |
| 8 | tinyB roster | not claimed: 387/395 identical, 6 raised, 2 at 1 ulp | PARTLY (claim incomplete -> C2) | MEDIUM |
| 9 | Runner blob 01e40f15 unchanged | `git hash-object` = `rev-parse 9f6182f:` = 01e40f15f483f6719c478e42968bf301084ed353 | CONFIRMED; binding gap -> C1 | MEDIUM |
| 10 | D5 fix | hub 0.26.5: `GatedRepoError.__mro__` contains `RepositoryNotFoundError`; the new order is GatedRepoError -> gated, then RNF (401 / plain), then the text check. Test covers 403/401/404-text gated, RNF 404-text and 401 not-found, plain 403 by text | CONFIRMED | - |
| 11 | Suite 884 pass / 1 fail (test_axis_marks selftest, pre-existing) | worktree (PYTHONPATH = worktree src): **885 passed, 1 skipped, 0 failed**; master 9f6182f full: **879 passed, 1 skipped, 0 failed**; test_axis_marks alone on master 5/5 | UNDETERMINED (the failure did not reproduce on either; no regression) | LOW |
| 12 | execution_graph sync | `update_graph_manifest.py --check` -> "manifest OK"; spans irt.py 121/132/187/199 and sources.py 624/632 match | CONFIRMED, with D-L1 | LOW |

Pins (LF; the working tree is LF, `hash-object` = `rev-parse HEAD:`): irt.py 57ccac737e1172f1265db2cbf0d1333d25f8a520,
sources.py 1c220438178f6b1080416f2e337d244a678ffde4, test_irt_slope_damped.py 50db335a6aebd85109607b53c8a043e5644a5296,
execution_graph.md 4aa365b152fdaaacd2f4488d8121092e4636f3d7. The builder's `irt_old.py` = `git show 9f6182f:src/benchzoom/irt.py` (cmp).

## Own mutants (sandbox copies of the worktree; tests: test_irt_slope_damped.py + the granularity fallback test)

| id | change | result | decisive |
|----|--------|--------|----------|
| R1 | `max_halvings` default 50 -> 0 | killed (3 failed) | yes |
| R2 | `maxit` default 500 -> 50 | **survived** (6 passed) | no: real data needs at most 10 steps (row 6) |
| R3 | halving `a / 2` -> `a / 1.0000001` | killed (3 failed) | yes |

## Defects

- **D-M1 (MEDIUM) = C1.** `synthetic_refusal` binds the runner blob only; a library change (here irt.py) leaves an
  old gate valid. Fix: record `git rev-parse HEAD:src/benchzoom` (the library tree) in every synthetic `meta.json`
  and refuse on a mismatch, or state in [A1] that the gate re-runs after this merge (it does at READY-2).
- **D-M2 (MEDIUM) = C2.** The tinyB columns (6 raised, 2 at 1 ulp) are missing from the claim and the record. Fix:
  add them to the WORK record / [A1] disclosure and to the graph's Docs-vs-code 26 bracket ("7 of 79 HELM" -> add
  "6 of 395 tinyB"). Drop "strong" or write "strong or weak-and-steep".
- **D-L1 (LOW).** `docs/execution_graph.md` L740: two literal TAB characters where `\t` of `\theta` was read as an
  escape (`-<TAB>heta^2/(2\sigma_<TAB>heta^2)`). The file has 2 TABs, master has 0. Fix: replace them with `\theta`.
- **D-L2 (LOW).** maxit 500 is untested (R2 survives). Fix: add a fixture that needs more than 50 damped steps, or
  note that the change is precautionary.
- **D-L3 (LOW).** `granularity_work.safe_theta_slope` and `tree_variants_work` still pass `maxit=50` explicitly, and
  their `FALLBACK["singular"]` count drops to 0 on any re-run. The values are the same optimum (row 4). Fix: when
  quoting a re-run, disclose the change in the fallback count.
- **D-L4 (LOW).** The D5 test uses local classes with the hub's names (the check matches by name). Optional: add one
  case with the real `huggingface_hub.errors.GatedRepoError`.

## Commands (scripts in scratchpad `rvdmp/`)

```
git -C benchzoom_wt_irt diff 9f6182f..HEAD            # whole diff read; --name-only | wc -l = 7
python rv_real.py   # old (9f6182f blob, cmp == builder irt_old) vs new vs scipy trust-exact, backbone on math,
                    #   mmlu_pro (meter_test.load_dataset), helm, tinyb (load_real; guard.masked(), fold_lomo(Y,~fit))
python rv_indep.py  # 16 changed cols: longdouble |grad|, min eig, scipy root(hybr) + Nelder-Mead from other starts
python rv_steps.py  # steps to the returned value; maxit=50 vs 500 on every HELM/tinyB col
bash mut.sh         # R1-R3 on sandbox copies (PYTHONPATH = sandbox src; asserted 'rvdmp' in irt.__file__)
PYTHONPATH=<wt>/src;<wt> .venv/python -m pytest -q   # worktree: 885 passed, 1 skipped
.venv/python -m pytest -q   (master checkout 9f6182f)  # 879 passed, 1 skipped
PYTHONPATH=<wt>/src python examples/update_graph_manifest.py --check   # manifest OK
python -c "...count('\t')"  # execution_graph.md TABs: new 2, master 0
```
Note: the benchzoom `.venv` imports MASTER's src (editable install). A worktree suite run without PYTHONPATH tests
master, not the branch.
