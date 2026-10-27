# POSTRUN review: REREAD-STEPS (M2 step 1: is the L2 re-read a one-step artefact? EXPLORATORY, WORK rows only)

Authority: D-2026-10-22-2 (875253bc, `docs/agents/author_decisions/2026-10-22.md`). Reviewer: adversarial reviewer,
2026-10-23. Zero LLM calls. No vault or reserved response was read: my loads asserted `guard.reads` = 0 at load and at
the end (MATH 0, MMLU-Pro 0, MMLU helm 0 / tinyb 0). Reviewed: benchzoom branch `reread-steps` (local; remote branches
containing 6d6eb11: 0), 8610a5d..6d6eb11. 8610a5d is master's tip, so the merge is a fast-forward.
- Run of record: 983c34f, script `blob:85fea70383e16786d6a6e3608fb25578d6236b69` (LF, sha256-lf16:c87bb918e8652150; the
  CRLF rendering sha256-crlf16:63dce6fb3c3746fa is not used: the working tree has 0 CR bytes). Part JSONs carry
  `dirty ""`.
- Tip blob `92516eef` (hunk `@@ -42 +42,74 @@`, inside the module docstring only). Plan `docs/reread-steps.md` blob
  `f5824ce4`; test blob `b7396fb7`.
- Outputs: `E:/benchzoom_demo/followups/reread-steps` (SHA256SUMS sha256 38e788e0cc7d2e6e, summary.txt 0abb2577d8b9b545;
  `sha256sum -c`: 10/10, all-files list 15/15, backup 15/15, and 15/15 again after my runs).

## Verdict

**OUTCOME CONFIRMED (exploratory). The word KILLED stands. Branch MERGEABLE; one LOW correction is recommended (C1).**
- Every deciding number reproduces from my own wiring. My script is not the builder's:
  - the MAP is found by vectorised **bisection** on the penalised score, not by Newton;
  - n = 2 is my own plain Newton step;
  - per-item values and the cluster SE are my own code.
  - Library primitives used: `l2_contexts`, `meter.step`, `_shrunk`, `logloss`, `group_folds`, `safe_theta_slope`.
  - Per-item max |diff| against the builder's npz: MATH 4.2e-17, MMLU 2.0e-16, MMLU-Pro 1.9e-16.
  - R1 against the MMLU-GAP-BASELINE npz: 0.0 on all three.
- The plan preceded every statistic, the word follows the pre-specified rule, the branch touches only its own 3 files,
  and hygiene is clean.
- **In substance:** iterating to the posterior mode removes 2.0% (MATH), 2.9% (MMLU) and 6.0% (MMLU-Pro) of the re-read.
  The one-step Newton shrinkage in `meter._shrunk` is not the re-read's mechanism.
- **New descriptive lead (not tested, not a word):** the re-read appears exactly in the folds where S-TAU picked the
  lower of two adjacent grid points for tau_L2 (table T below).

## Per-claim table (deciding claims; x 1e-3 nats per cell; WORK rows only)

| # | Claim (builder) | Own result | Verdict | Sev |
|---|---|---|---|---|
| 1 | Plan d6147bd and brackets [P1]-[P3] before any statistic on responses | Author decision 23:57:01. Plan 00:06:51; [P1] 00:09:07; [P2] 00:16:50; [P3] + runner 983c34f 00:24:02. MATH part started ≈00:28:21 (end 00:35:56 − 455 s); MMLU-Pro ended 00:39:04, MMLU 01:06:52; [P4] 01:24:51. Plan lines deleted d6147bd..tip: 0 (each commit: 0). Earliest builder scratch file 00:15:48, a selftest sandbox. The 99 part JSONs in the sandboxes are all fixtures (93 fake 1×1, 4 × 900×12, 1 × 720×10, 1 empty `{}` rp_skip). Files under `E:/benchzoom_demo` (depth 3) written 21:44–00:28:30: 9, all a peer's `label-align` | CONFIRMED | - |
| 2 | R1 reproduction: per-item diff 0.0; MATH +0.1241 (0.0350), MMLU +0.0575 (0.0227), MMLU-Pro −0.0098 (0.0212) | Mine vs the comparator npz (sha256 = its SHA256SUMS; clusters equal): 0.0 / 0.0 / 0.0. Pooled +0.12405194 (0.03497383), +0.05749455 (0.02273903), −0.00981430 (0.02116004) | CONFIRMED | - |
| 3 | MATH G(L2\|L2) +0.0116 → +0.0114, SE 0.0036, 3.13 SE (the arm that fires) | G_1 +0.011641230 (0.003639453). G_inf +0.011403168 (0.003638128), builder +0.011403168 (0.003638128); gap 4.0e-17 / <1e-18. z = 3.134 | CONFIRMED | - |
| 4 | MMLU +0.0140 → +0.0136 (0.0102) | +0.0139599 → +0.0135539 (0.0101741), z 1.332; per-item ≤ 2.0e-16 | CONFIRMED | - |
| 5 | MMLU-Pro +0.0266 → +0.0250 (0.0155) | +0.0265927 → +0.0250075 (0.0154508), z 1.619; per-item ≤ 1.9e-16 | CONFIRMED | - |
| 6 | G(L3a\|L2) move: MATH −0.0009 (0.0006), MMLU +0.0023 (0.0010), MMLU-Pro −0.0007 (0.0002) | −0.0009149 (0.0005677), +0.0023267 (0.0009744), −0.0006711 (0.0001977); paired SE | CONFIRMED | - |
| 7 | Word KILLED under the pre-specified rule (any dataset > 2 SE, strict) | MATH 3.134 > 2 → KILLED; MMLU 1.33 and MMLU-Pro 1.62 SE fire nothing. SUPPORTED is excluded by construction (MATH not within 1 SE). Robustness: a 3-dataset Bonferroni z is 2.43 (3.13 clears it); the composite SE (item SE ⊕ between-seed SD/√5) gives z 3.035 | CONFIRMED | - |
| 8 | "Every value is settled by step 2" ([P4], docstring, hand-back) | MMLU n = 2 is not settled: G(L2\|L2) +0.0135289 vs inf +0.0135539 (prints +0.0135 vs +0.0136); net +0.0462 vs +0.0463; G(L2\|L1) +1.7923 vs +1.7925 (summary L22/L26). My plain Newton n = 2 reproduces +0.0135289. MATH and MMLU-Pro are settled at n = 2 | REFUTED (descriptive) | LOW |
| 9 | tau_RR = 0 in 17/25 MATH folds; 8/25 MMLU-Pro; 0/25 MMLU | Same counts, from my own `meter.step` selections. Sharper: see T | CONFIRMED | - |
| 10 | D1 recovers 75 / 88 / 93% of the converged re-read | +0.0086301 (0.0024284), +0.0120057 (0.0052652), +0.0233095 (0.0106146) → 0.757 / 0.886 / 0.932 | CONFIRMED (descriptive) | - |
| 11 | Inertness: no `src/` diff; n = 1 equals the current path bit for bit | `src/` files changed 8610a5d..6d6eb11: 0 (count); 49b18c0..8610a5d: 0. My n = 1 L2 equals `l2_contexts` L2: max diff 0.0 in all 25 MATH folds; n = 1 per-item RR equals the builder's: 0.0 | CONFIRMED | - |
| 12 | Vault / reserved reads 0 | Confirmed, but the counter cannot be anything else: an unarmed `VaultGuard.open()` raises `VaultSealed`, so `reads` stays 0 by construction. The real guarantee is structural: `masked()` NaNs every vault row, and both loaders assert that no WORK row is all-NaN. That holds, and my loads went through the same loaders | CONFIRMED (structural) | LOW |
| 13 | `--selftest` 51/51; tests pass; mutants 46/46 | Control copy 51/51 PASS. `tests/test_reread_steps.py` 2 passed (venv 3.11.1 / numpy 1.26.3; worktree porcelain 0 before and after). Full suite not re-run (0 `src/` files changed; the only test added passes). The builder's 46 mutants not re-run; my 6 below | CONFIRMED | - |
| 14 | Support: KILLED arm 0.89 (MATH), 0.81 (MMLU), 0.39 (MMLU-Pro); SUPPORTED 0.32 jointly | Re-derived: Φ(0.0116/0.0036 − 2) = 0.889; MMLU SE 0.0132·√(5530/8425) = 0.01069 → 0.808; 0.388; 0.683³ = 0.318. MDE80 = 2.842·SE: 0.0103 / 0.0304 / 0.0441. The plan names no DEFF: its SEs are the record's cluster-robust SEs. Post-run see S | CONFIRMED | LOW |

**S: support re-measured from this run's own clusters (G_inf(L2|L2), held tau²).**

| dataset | n | clusters | DEFF | n_eff | SE | MDE80 | G_inf | z |
|---|---|---|---|---|---|---|---|---|
| MATH | 2,949 | 2,946 | 1.005 | 2,934 | 0.00364 | 0.0103 | 0.0114 | 3.13 |
| MMLU | 8,425 | 8,375 | 1.005 | 8,379 | 0.01017 | 0.0289 | 0.0136 | 1.33 |
| MMLU-Pro | 7,197 | 7,085 | 1.016 | 7,086 | 0.01545 | 0.0439 | 0.0250 | 1.62 |

- The KILLED arm was adequate only through MATH. At the realised WORK effect, MMLU's arm had power Φ(1.35 − 2) = 0.26.
- Under "re-read = 0 everywhere", P(KILLED) = 1 − 0.97725³ = 0.067. KILLED is specific; SUPPORTED was never sensitive.

**T: tau_L2 against tau_RR per fold (my own selections; equal to the builder's `fold_taus`).**

| dataset | tau_L2 = 0.04 | tau_L2 = 0.08 |
|---|---|---|
| MATH | tau_RR > 0 in 8/8 | tau_RR = 0 in 17/17 |
| MMLU-Pro | tau_RR > 0 in 17/17 | tau_RR = 0 in 8/8 |
| MMLU | - | tau_L2 = 0.08 in 25/25; tau_RR > 0 in 25/25 |

- MATH fold means of G_inf: 8 of 25 are non-zero (0.0081–0.0610) and 17 are exactly 0. Per-seed values: 0.0148,
  0.0122, 0.0098, 0.0101, 0.0102.

## Defects and conditions

- **C1 (LOW, recommended at merge):** claim 8 is wrong on MMLU.
  - Fix: add an insertion-only bracket `[P5]` to `docs/reread-steps.md` and correct the docstring line: "settled by
    n = 2 on MATH and MMLU-Pro, by n = 3 on MMLU (n = 2 differs in the 4th decimal on G(L2|L2), net and G(L2|L1))".
    The registrar should not carry "settled by step 2" forward.
- **C2 (LOW):** mutants R1 and R2 survive. No fixture has a negative G_inf, so the sign of the KILLED and within-1-SE
  tests is unguarded.
  - It is not decisive here: all three G_inf are > 0.
  - Fix: add two S4 cases, G_inf = −3 SE (expect INCONCLUSIVE) and G_inf = −1.5 SE with DECAY on all three (expect
    INCONCLUSIVE).
- **C3 (LOW, reading):** the clustered SE treats each fold's tau² selection as fixed. The MATH re-read comes entirely
  from the 8 fold fits that chose tau_RR > 0.
  - The word survives a seed-level composite SE (z 3.035) and a 3-dataset Bonferroni (2.43).
  - Fix (future H-X readouts of a threshold-type tau² reader): print the per-fold means and the composite SE beside the
    word.
- **C4 (LOW):** the planning SEs name no DEFF and no source; post-run DEFF ≈ 1.01 (S), so nothing was understated.
  "guard reads 0" is a structural guarantee, not a count (claim 12). Word it that way in the record.

**What the result licenses (exploratory, WORK rows only):**
- At the tau² the current path selects, iterating every EB group offset (L1, L2, L3a, RR) from one Newton step to the
  posterior mode leaves the L2 re-read essentially unchanged. G_inf / G_1 = 0.980 (MATH), 0.971 (MMLU) and 0.940
  (MMLU-Pro). Paired drop shares: 2.0% ± 1.1, 2.9% ± 7.9 and 6.0% ± 0.7.
- The re-read persists at the MAP on MATH (3.13 SE). `meter._shrunk`'s single step is not why the re-read is positive.
- The record's net-of-re-read leaf gains move by at most 0.0023.

**What it does not license:**
- That the re-read persists above 2 SE on MMLU or MMLU-Pro individually.
- That the re-read is a prior or grid artefact. D1 and table T are descriptive. T makes "S-TAU grid coarseness (factor-2
  grid: the re-read fills the gap between 0.04 and 0.08)" the leading candidate; a finer or continuous tau_L2 grid is
  the next zero-call check.
- Any statement about a vault or reserved side; any switch of the deciding estimator (the author's).
- KILLED was close to foregone: the priors are small (G(L2|L1) moves only from 0.4556 to 0.4565 on MATH). P1 predicted
  it from the algebra, so this run confirms that algebra; it did not discover the result.

## Own mutants (sandbox copies `E:/TaxoArena_tmp/review_reread-steps/mut/<id>`; TMP/TEMP/TMPDIR/BZ_SANDBOX redirected)

| id | change | result | decisive |
|---|---|---|---|
| R0 | control (unmutated copy) | 51/51 PASS | - |
| R1 | KILLED on \|G_inf\| > 2 SE (sign-blind) | SURVIVED | no (all G_inf > 0) |
| R2 | within 1 SE as G_inf ≤ SE (sign-blind) | SURVIVED | no |
| R4 | n = 2 returns step 1 | KILLED (S2 n=2,3 plain Newton) | yes (n = 2 column) |
| R6 | SE_inf read from the n = 1 row | KILLED (S4 exactly 2 SE) | yes |
| R10 | KILLED fired from G_1 instead of G_inf | KILLED (S4, 9 fails) | yes (the estimand) |
| R18 | prior term halved in the gradient (wrong MAP) | KILLED (S2 bisection MAP) | yes (G_inf) |

## Commands (all read-only on inputs; my outputs only under `E:/TaxoArena_tmp/review_reread-steps`)
```
git -C <wt> diff --name-status 8610a5d..6d6eb11              # 3 files, all A; | grep -c '^src/' = 0
git -C <wt> diff d6147bd 6d6eb11 -- docs/reread-steps.md | grep -c '^-[^-]'    # 0 (each commit: 0)
git -C <wt> show 983c34f:examples/reread-steps.py | git hash-object --stdin       # 85fea703...; sha256 c87bb918...
git -C <wt> diff -U0 983c34f 6d6eb11 -- examples/reread-steps.py | grep '^@@'      # @@ -42 +42,74 @@ (docstring)
git -C <wt> branch -r --contains 6d6eb11 | wc -l             # 0
python -I indep.py {math|mmlu_pro|mmlu} 5                    # own recompute: bisection MAP, own Newton n=2, own SE
python -I -c "...np.max(np.abs(indep[k]-parts[held__k]))..." # 4.2e-17 / 2.0e-16 / 1.9e-16; R1 vs gap npz 0.0
python -I mutants.py R0 R1 R2 R4 R6 R10 R18                  # at most 6 at once, BLAS 1
<venv>/python -m pytest tests/test_reread_steps.py -p no:cacheprovider --basetemp=E:/TaxoArena_tmp/...   # 2 passed
sha256sum -c SHA256SUMS / SHA256SUMS_all (outputs, backup)   # 10/10, 15/15, 15/15; 15/15 after my runs
find E:/benchzoom_cache -newermt '2026-10-23 01:32' -type f | wc -l                # 0 (no input written)
```
Processes: at most 6 of my own (parent + 5 workers), OMP/OPENBLAS/MKL = 1. A peer's flat-compare run and a peer
reviewer's mutants were running alongside and were not touched. One early launch with 6 workers (7 processes) was
stopped by PID after about 30 s and relaunched with 5. Runtime: MATH 421 s, MMLU-Pro 171 s, MMLU 1,520 s.
