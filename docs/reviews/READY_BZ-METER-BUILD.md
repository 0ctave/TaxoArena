# READY review: BZ-METER build (benchzoom `cbe1d78..e6d420d`)

Reviewer: adversarial-reviewer, 2026-10-11. Zero LLM calls. No vault response read: every run below went through
`VaultGuard.masked()` and printed `reads 0`. Both vault files and both v2 atlases have the same sha256 before and after
my real `--dry-run` (`sha256sum -c`: 4 OK). Objects: benchzoom master `e6d420d` (local). Registration
`docs/meter_registration.md` LF blob `ec38838980f404146b4d75a8a92d714a17a60323`; `git hash-object --no-filters` gives the
same value, so there is no CRLF rendering. It equals the runner's `REG_BLOB` and `git rev-parse e6d420d:<path>`.
Authority: D-2026-10-11-9. Prior review: READY_BZ-METER (6d918381). I did not re-derive its CONFIRMED rows (S-MOM
Support table, vault and dropped-id shas, the 22-model list).

## Verdict: READY (with conditions C1-C4)

The vault gating holds, and so do default-off identity, leakage, the nulls as registered, the verdict logic and the
execution-graph sync. The Support re-cut [R14] matches its JSON to the digit, and its arithmetic reproduces. None of
the defects below changes a deciding number on the committed code. The grid-top question (D1) is the registrar's call,
and it must be settled BEFORE the read because `TAU_GRID` goes into `meta.json`. If the grid is widened, that is a new
registration bracket, a new `REG_BLOB` and a delta review of that one line.

## Per-claim table (deciding claims only; x1e-3 nats per cell)

| # | Claim | Claimed | Reviewer | Status | Sev |
|---|---|---|---|---|---|
| 1 | Tests / ruff / mypy / manifest | 443 passed, 4 desel.; clean; OK | 443 passed, 4 deselected (247 s); ruff "All checks passed"; mypy "no issues, 15 files"; manifest OK, rc 0 | CONFIRMED | - |
| 2 | Slope off is bit-identical to b91f8c4 | digest fbfeff91... | my own script, run on `git archive b91f8c4 src` (old) and on the working tree with `difficulty_slope=False` (new): both `fbfeff9157c6...b824cd` | CONFIRMED | - |
| 3 | Real dry-run: 0 vault reads; WORK taus | MATH L3t .005, fk .04; MMLU-Pro L3t 0, fk .02 | my run: identical taus on every reader; reads 0 / 0; n_scored 1960 / 4654; dropped 5 / 143; twin items kept 0 / 58; 35 / 91 cells; dropped shas 8b578b27 / 4cd9a0a8 | CONFIRMED | - |
| 4 | [R14] table = support_meter_stau.json | rows as printed | all 30 rows match the JSON to 3 dp (sha256 b19e0e0d... = SHA256SUMS). DEFF = (SE/SE_iid)^2 recomputed: MATH L3k\|C 1.050, MMLU-Pro 1.156. Vault SE = SE x sqrt(n_W/n_V): .0518 / .0472. MDE80 = 3.84 x vault SE: .199 / .181 | CONFIRMED | - |
| 5 | S-MOM rows of the new run reproduce the original table | yes | 17 of 17 checked rows (all deciding rows, the 22-model rows, C-L2) equal at 3 dp | CONFIRMED | - |
| 6 | Predictions re-cut (P4/P5 ranges = point +- 2.5 vault SE) | P4 MATH -0.008-0.077; P5 .245-.504 / -.023-.213 | .0345 +- .0425; .374 +- .129; .095 +- .118: reproduce. "g + 2 SE = .068", "3 SE = .142": reproduce | CONFIRMED | - |
| 7 | Verdict logic = [R2], [R13], [R4], [R8] | as registered | read line by line (`level_word`, `slope_word`, `depth_word`, `backbone_trigger`, `words_for`): match. The trigger uses S2PL-L0 and S3PL_L0-L0 with vault SE | CONFIRMED | - |
| 8 | Nulls as registered ([R6], [R13]) | streams, scope, re-selection | seeds `[20261012, code, r]` with codes 1-6; harness seed `[.., 0, 0]`; permutation over fit\|score; within category except L1 / L2L0; one permutation per label serves its secondary line; tau^2 re-selected on fixed parents in every context; refusal below 200 | CONFIRMED | - |
| 9 | Vault gating | refusals before data | `--vault` refuses on: REG_BLOB, both datasets, dirty src/runner/registration, calibrations. The guard opens only when armed. meta.json and the profile are written before `open()`. The WORK side is refitted and asserted identical. Outputs are write-once | CONFIRMED | - |
| 10 | Execution graph accurate | Stage E, 3.9, step table | the Stage E mermaid and section 3.9 match the code. Every meter.py span in the step table matches `grep -n '^def'`. Sync is non-vacuous: mutant M8 (`KNN = 41`) fails `test_manifest_matches_code` | CONFIRMED | - |
| 11 | Mutants 35/36 killed | builder's table | my 9 (below): 7 killed by test_meter; **M6 survives entirely**; M3 is killed only by the manifest fingerprint | PARTLY | MEDIUM |
| 12 | Grid top .04 binds (builder's MEDIUM) | moment estimates exceed .04 | WORK probe, grid widened to .32 (5 outer folds, 0 reads). MATH: L1 .08 (4/5), L2a .08-.16, fk .08 (5/5). Deciding **L3k\|C +0.374 -> +0.435** (SE .042 -> .069), L3t\|L2 +0.034 -> +0.019, L1 +1.007 -> +1.040. MMLU-Pro: selections unchanged except L2 in 1 fold; L3k\|C +0.095 -> +0.082. No predicted word changes | PARTLY: binds on MATH; it does not decide a word on WORK | MEDIUM |
| 13 | Insertion-only registration edits | [R0]-[R15] | of 23 deleted lines, every one is kept verbatim in Section 12 or survives re-wrapped. The 5 re-wrapped ones are the same text, and "(none yet)" was the placeholder of Section 12 | CONFIRMED | - |

## Own mutants (sandbox `E:/TaxoArena_tmp/bzmeter_review`, copies of `git archive e6d420d`; test_meter + sync)

| id | change | result | decisive |
|---|---|---|---|
| M1 | tau loss also summed over the main context (vault rows in the selection) | killed (meta_written_before..., scored_answers_never_fit, own_answer..., golden) | yes |
| M2 | L3k null permuted over WORK rows only | killed (golden_synthetic only) | yes |
| M3 | DEGENERATE of L3k\|C read from `fl`'s tau | **survived test_meter**; killed only by the manifest fingerprint | yes (latent) |
| M4 | field self-exclusion off on fitting rows | killed (golden_synthetic only) | no |
| M5 | inner training rows include the inner fold | killed (inner_contexts_refit_parents, planted, golden) | yes |
| M6 | `score_lines` ignores the vault twin clusters (`groups = arange`) | **SURVIVED** (68 passed; the runner is not fingerprinted) | yes (SE) |
| M7 | L1 null permuted within category (a no-op null) | killed (null_streams..., planted, null_benchmark) | yes |
| M8 | `KNN = 41` | killed (golden, runner_signature_pins, manifest) | sync check |
| M9 | `VaultGuard.masked()` does not mask | killed (vault_guard_refuses_unarmed) | yes |

## Defects

- **D1 MEDIUM (grid top binds; registrar decides before the read).** On MATH, the cap shrinks the text reader (the
  deciding L3k|C is understated by about 1.4 SE on WORK). The capped parents also leave signal that the leaf line picks
  up. Fix: either (a) keep the grid and add one disclosure bracket citing row 12 ("grid top binds on MATH; the WORK probe
  to .32 changes no predicted word"), or (b) widen `TAU_GRID` to {.., .04, .08, .16, .32} with a bracket, re-cut [R14]
  and pin a new REG_BLOB (delta review of that line only). In either case, Section 6's text must name the binding readers.
- **D2 MEDIUM (M6 survivor, deciding SE path).** No test pins `d.groups` in `score_lines`. Fix: a test on a fixture
  with planted twin rows that asserts `n_clusters < n_scored` in `outcome.json`. Until then: condition C2.
- **D3 LOW (M3 survivor).** The `DECIDING` reader map (L3k|C -> `fk`, L3t|L2 -> `L3t`, ...) is guarded only by the
  manifest fingerprint. Fix: assert the map in `test_meter.py`, and test that a DEGENERATE word follows the tau^2 of
  its own reader.
- **D4 LOW (unregistered gate, presence check).** `--vault` requires the calibration outputs, but `calibration_ok`
  checks only `state == READ` and a passed harness. It does not check that the planted synthetic run finds its planted
  levels or that the null run reports none SUPPORTED. Fix: register the gate (one bracket in Section 11), and have the
  operator print and read the calibration words before `--vault`.
- **D5 LOW (power at the bar).** MMLU-Pro L3k|C has MDE80 .181 > delta_min .10. SUPPORTED needs g >= .142, and
  NOT SUPPORTED by the bar needs g < .006, so INCONCLUSIVE is near-certain unless the true gain is >= ~.18. The row should
  carry "underpowered at delta_min" (the prediction already says INCONCLUSIVE). MATH L3t|L2: MDE .065 < .10, SCOREABLE.
- **D6 LOW.** The secondary `L2|L0` takes its DEGENERATE from L2's tau alone (if L1 tau > 0 and L2 tau = 0, it would be
  mislabelled); this is not live (L2 tau .04 on both). The runner docstring says [R0]-[R14] (pinned [R0]-[R15]). The
  Section 12 header omits [R14]/[R15]. Cosmetic.

## Conditions for the vault read

- C1: D1 settled in writing by the registrar before `--vault` (keep + disclose, or widen + new REG_BLOB + delta review).
- C2: post-run, `outcome.json` must show `n_clusters` = 1960 (MATH) and 4625 (MMLU-Pro: 4654 scored, 29 twin pairs); a
  different count makes the SEs NOT VALID.
- C3: the default `--out` (`E:/benchzoom_demo/meter_v1`, absent today) only. Write-once is per directory, so a second
  `--out` would be a second read.
- C4: run in this order, from a clean tree at the commit that carries any D1-D4 fixes, with no edit between steps.

Exact run commands (cwd `Z:/FAC/TUBerlin/benchzoom`, venv active, `PYTHONPATH=src`):
```
python examples/meter_test.py --dry-run              # expect the row-3 lines and "DRY-RUN OK: 0 vault response reads"
python examples/meter_test.py --calibrate synthetic  # read the null/planted words (D4)
python examples/meter_test.py --calibrate work       # pseudo-vault on WORK; harness passed
python examples/meter_test.py --vault                # once; then sha256sum -c E:/benchzoom_demo/meter_v1/SHA256SUMS
```

## Commands that show each result

```
.venv/Scripts/python -m pytest -q; ruff check .; mypy src; python examples/update_graph_manifest.py --check   # row 1
python golden.py <old src from git archive b91f8c4> old ; python golden.py src new                             # row 2
examples/meter_test.py --dry-run, between sha256sum and sha256sum -c of the vault files and atlases              # rows 3, 9
inline python over support_meter_stau.json (cv and moment rows, (se/se_iid)^2, x1.2266 / x1.2435, x3.84)         # rows 4-6
probe_grid.py wide {math,mmlu_pro} (M.TAU_GRID patched; support_crossfit rule cv; masked matrix)                 # row 12
mutants.py M1..M9 (copy of base, one replace, pytest test_meter + test_execution_graph_sync)                     # row 11
git diff 06f1307 e6d420d -- docs/meter_registration.md | grep '^-'  -> 23 lines, each searched in the file        # row 13
load_dataset("mmlu_pro"): unique groups over the scored rows = 4625, 29 clusters of size 2                       # C2
```
Scripts: `E:/TaxoArena_tmp/bzmeter_review/{golden.py,probe_grid.py,mutants.py,probe_wide_*.json,dryrun.txt}`.
