# Pre-data review: benchzoom calibration criteria v2 (70e9e79) and gate fix (6124465)

Reviewer: adversarial-reviewer, 2026-10-10. Zero LLM calls, no Ollama, no calibration run. Repo Z:/FAC/TUBerlin/benchzoom
master 70e9e79 (parent 6124465, parent de36610), working tree clean for tracked files. Authority D-2026-10-10-1/-2.
Prior reviews: POSTRUN_BENCHZOOM-CROSSFIT-DEPTH (C1-C3), POSTRUN_BENCHZOOM-DEMOS-V2 (D1-D5).

## Verdict: CHANGES (criteria: 2 HIGH, 3 MEDIUM, 1 LOW edits below; fix: MERGEABLE as opt-in, 1 MEDIUM doc defect)

Neither change is a reason to tune a threshold. The thresholds stay as written: 5% / 8% / 10%, alpha 0.05, 1 SE.
After the edits, re-pin the new LF blob in the script's meta. The script itself still needs its own pre-launch review
(criteria section 9).

## Per-claim table (deciding claims)

| # | claim | own result | status | sev |
|---|---|---|---|---|
| 1 | criteria LF blob e4302449; library blobs crossfit 39bc296e, profile 514538f5, synthetic c037405c, atlas 7a0b5c2a, examples/depth_calibration ff3aee1e | `git rev-parse 70e9e79:<f>` = `git hash-object` = `--no-filters`; 0 CR bytes in each file (working tree is LF, so no CRLF rendering exists) | CONFIRMED | - |
| 2 | 0 data files tracked | `git ls-files \| grep -ciE '\.(npz\|db\|parquet\|csv\|jsonl)$'` = 0 | CONFIRMED | - |
| 3 | pytest 226 passed / 4 deselected; ruff and mypy clean | 226 passed, 4 deselected (87 s); ruff "All checks passed"; mypy 13 files OK (.venv) | CONFIRMED | - |
| 4 | H1 refuted: known parent 0 gives 2 SE 3.35% vs 2.24% | runs1 (64 seeds): cc_known0 296/8832 = 3.35%, cc_lomo 198/8832 = 2.24% | CONFIRMED | - |
| 5 | truncation: oracle b and theta open the gate in 67-78% of seeds, 2 SE false zoom 1.15-1.30% | cc_oracle runs1 0.78, 115/8832 = 1.30%; runs2 0.67, 102/8832 = 1.15% | CONFIRMED | - |
| 6 | gate 0.05: 0.78% [0.45, 1.14], open in any fold 0.28; gate 0.01: 0.43% [0.17, 0.76] | 69/8832 = 0.78% [0.45, 1.14], 0.28; 38/8832 = 0.43% [0.17, 0.76] (an2.py, same bootstrap) | CONFIRMED (these are all-run, i.e. diluted, rates) | - |
| 7 | "z behaves as it should" (oracle depth 2: sd 1.05-1.09, P(z>1.645) 5.3-6.2%) | oracle CONFIRMED (0.053 / 0.062). **In the configuration that ships** (centred, LOMO, gate 0.05), depth-2 z has mean +0.24, sd 1.07 and **P(z>1.645) = 0.113 per fold**. Gate 0.01: P(z>2.326) = 0.050. Gating depth 1 (open 13%) removes the parent absorption (H1), so H2 is no longer cancelled | PARTLY | MEDIUM (F1) |
| 8 | the gate fixes the open-gate regime | conditional on an open gate (mmlu nosubj, runs2), cg-like 2 SE per pair is 69/2484 = **2.78%** (gate 0.05), 2.50% (gate 0.01) and 2.65% ungated. The gate only reduces how often the gate opens (18, 11 and 47 of 64 runs); it does not change the per-pair rate once open | PARTLY (as the builder says, "by design") | info |
| 9 | the criteria cover C1 (dilution) | V1a and V1b are conditioned on open-gate runs, and the all-run rates never decide | CONFIRMED in form; see R1 (exclusion vacuity) | HIGH |
| 10 | the criteria cover C2 | mmlu G3 nosubj is a required cell | CONFIRMED | - |
| 11 | closed gate implies no zoom (justifies V1b over open-gate runs only) | profile.py: tau = 0 sets d = 0, so the child eta equals the parent eta; delta = 0 and "equality does not descend" | CONFIRMED; builder call (b) ENDORSED | - |
| 12 | nested V3 (inner 4-fold on the items outside k; fold k masked) + flip selftest | sound design, no leakage path to fold k; "same settings" must include centre and gate_alpha (R6) | CONFIRMED | - |
| 13 | seeds are new | prior runs used 10000-170063 (depth_calibration.py) and 980000-986xxx (scratch); the new range is 1,200,000-1,410,063 | CONFIRMED | - |
| 14 | libnull G5 is a null | simulate_shaped: leaf means enter b (not model-specific); c_{m,s} is at subjects only | CONFIRMED | - |

Support from the development cache (runs2, mmlu nosubj, gate 0.05, open runs only; source for the DEFF the criteria lack):
- runs and decisions: 18 open runs, 2,484 decisions;
- per-pair rate: p = 2.78%;
- cluster SE (ratio estimator) 0.26 pp against a binomial SE of 0.33 pp, so DEFF = 0.6; for gate 0.01, DEFF = 1.9 (11 runs);
- n_eff = 3,886;
- t-based upper bound 3.33%;
- **V1b analogue (subject-level zooms only): 62/414 = 15.0% > 10%**. Gate 0.01 gives 13.0%, no gate 14.3%.
The development data therefore predict a V1b FAIL in a NULL cell, not only in dense E0.5 mmlu as the builder
expected. This does not justify changing V1b (that would be tuning). It is AUTHOR-1.

## Required edits to docs/calibration_criteria_v2.md

- **R1 HIGH: non-estimable cells must not drop out silently.** Today a null cell whose gate rarely opens leaves V1a
  and V1b without any trace in the verdict ("MET" by exclusion). That includes mmlu G1 and G2, the C1 worst cells
  (5.48%). Edit in section 7, V1a, after "does not enter V1a": "Per shape, the open-gate runs of all non-estimable
  cells are pooled into one RESIDUAL cell. The residual cell enters V1a and V1b under the same bars when it has
  >= 8 open-gate runs, and its composition is printed." Also: "a cell with 0 open-gate runs prints `0 open / N runs`."
- **R2 HIGH: Support section (missing; rule 8).** Add a section 6b with four parts.
  - The pre-data DEFF and its source: the dev cache above, DEFF 0.6-1.9, plus the CROSSFIT-DEPTH review table.
  - The arithmetic at the estimability floor. Mmlu: 8 runs x 138 = 1,104 decisions. At p = 3% and DEFF 2,
    SE = sqrt(.03 x .97 / 1104 x 2) = 0.73 pp, and the upper bound is 3 + 2.36 x 0.73 = 4.7% < 8%, so the bar is
    reachable. Math: 8 x 207.
  - The MDE against the bar. With 18 runs (2,484 decisions) and DEFF 2, n_eff = 1,242 and SE = 0.48 pp at p = 3%. The
    5% point bar therefore fails a true rate of 5 + 0.84 x 0.62 = 5.5% with 80% probability (SE 0.62 pp at 5%). Print
    this per required cell from the realised run counts.
  - SCOREABLE for V1a/V1b/V2/V3.
  - Also replace the deciding upper bound. With 8-15 clusters a percentile bootstrap is anti-conservative. Decide on
    max(percentile-bootstrap upper, ratio-estimator mean + t_{n-1, 0.975} x cluster SE) and print both.
- **R3 MEDIUM: the library-blob guard only warns** (section 1: "prints both sets"). Edit: "If the imported library
  blobs differ from section 1, the script refuses. A library change requires an insertion to section 1 before the
  first launch, which changes this file's blob."
- **R4 MEDIUM: the gate's empirical size.** In section 5 replace "alpha = 0.05 ... conventional level" with "alpha =
  0.05 is the nominal level. In the shipped configuration the per-fold depth-2 size measured in development is 11.3%
  (0.01: 5.0%)." In section 6 add: "Printed per null cell: the per-fold rate of `tau_z[k, 2] > z_crit` and the
  per-run any-fold rate (descriptive)." The adoption text (section 8) must state the empirical size, not "alpha 0.05".
- **R5 MEDIUM: the "any fold" convention is the broadest one** (builder call (a)). It admits runs that are open in a
  single fold. Keep it as deciding, but add to section 6: "V1a/V1b are also printed stratified by the number of open
  folds (1..5)." In section 8 add: "the adoption text states the cg2 open-fold count on the real MMLU-Pro demo and the
  V1a/V1b rates of the strata at or above it."
- **R6 LOW: V3 edge cases.**
  - State: "d = 0 with SE = 0 is PASS; d > 0 with SE = 0 is FAIL; equality d = SE is PASS."
  - State: "inner fits use the same centre and gate_alpha as the outer rule."
  - Disclose that V3 is 44 unadjusted one-sided 1-SE comparisons, so FAIL is the conservative direction.

Builder calls: (a) ENDORSED with R5; (b) ENDORSED (claim 11); (c) CHANGES via R1 and R2; (d) ENDORSED with R6.
Leakage: none found. The data are synthetic and no TaxoArena EVAL items are involved. The thresholds come from the
brief and are disclosed against the dev numbers. The new seeds are disjoint from all earlier runs. The nested V3 design
masks fold k.

## Defects in the fix (6124465)

- **F1 MEDIUM (docs/defaults.md L141-143, selective).** The 7.2% size quoted for "the library's centred fit" comes
  from the ungated fit, where depth 1 is open. In the gated configuration depth 2 has mean +0.24 and size 11.3% per
  fold, so "real but not the cause" (H2) no longer holds once the gate closes depth 1. Fix: insert after L143: "[With
  gate_alpha 0.05 applied at every depth (the shipped configuration): depth 2 mean +0.24, sd 1.07, P(z > 1.645)
  11.3%; gate 0.01: P(z > 2.326) 5.0%. The nominal alpha is not the realised level; runs2, an1.py.]"
- **F2 LOW (test gap).** Own mutant M1 survived. In profile.py, `if not zz > z_crit:` changed to `if zz < z_crit:`
  makes NaN (tr = 0, e.g. one informative model per node, centred) and equality open the gate, and 20/20 tests still
  pass. Fix: add a test with a degenerate depth that asserts `tau_z` is NaN and tau = 0, plus an equality case.
- Golden inertness: not re-derived. The builder's test_default_golden passes in the 226 above, and own M2/M3 were
  killed.

## Own mutants (sandbox copies under the scratchpad, PYTHONPATH first; tests test_gate_alpha + test_centre_models)

- M1: `not zz > z_crit` changed to `zz < z_crit`. SURVIVED (20 passed). Not decisive: an edge case (F2).
- M2: centred tr term `-2.0*` changed to `+2.0*`. KILLED (4 failed). Decisive: gate variance.
- M3: `_gate_z(tau2*n_use, ...)` changed to `_gate_z(tau2, ...)`. KILLED (4 failed). Decisive: z scale.

## Commands

```
cd Z:/FAC/TUBerlin/benchzoom
for f in <5 lib files> docs/calibration_criteria_v2.md; do git rev-parse 70e9e79:$f; git hash-object $f; git hash-object --no-filters $f; tr -cd '\r' <$f|wc -c; done
git ls-files | grep -ciE '\.(npz|db|parquet|csv|jsonl)$'        # 0
.venv/Scripts/pytest.exe -q ; .venv/Scripts/ruff.exe check . ; .venv/Scripts/mypy.exe src
cd E:/TaxoArena_tmp/bz_cause; python an1.py "runs1/*.json"; python an1.py "runs2/*.json"; python an2.py "runs2/*.json"
# open-gate support (inline): per run, keep runs with any(tau[:,2]>0); ratio-estimator cluster SE, DEFF=(SEclu/SEbin)^2, t-upper
# mutants: cp src to scratchpad/mut/M{1,2,3}; sed one line in profile.py; PYTHONPATH=<copy> pytest tests/test_gate_alpha.py tests/test_centre_models.py
```
