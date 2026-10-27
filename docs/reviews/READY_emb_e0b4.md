# READY REVIEW emb-e0b4 29c3e42 (delta on ee3a40f), 2026-09-29, adversarial reviewer, zero calls

Reviewed blob: `tools/analysis/embedder_cross_flat.py` blob:f8581aab0f62b7e70f64ad521e2b8d8efc13b948
(`git rev-parse 29c3e42:<path>` = `git hash-object` of the worktree file), sha256-lf16:328a7c09859b3acb,
sha256-crlf16:ff57756c6aebce0d (the emb-e0b4 working tree is CRLF). Delta = that one file, +186/-14
(`git diff --name-only ee3a40f 29c3e42 | wc -l` = 1). Prior review of the untouched code: READY_emb_e0b3 (9694555).

## VERDICT
**MERGEABLE. `--run --part embed` READY-WITH-CONDITIONS** (C-E0B4-1 below; D1/D2 are LOW, non-blocking).
Expected outcome shape under ruling (a), from my convergence-only fits: VOID set = {gemma_raw k 82} and nothing
else; F1 (embed, k 14) scored; P1/P2 already of record in the cpu outcome (ee3a40f), untouched.

## Per-claim table (deciding claims only)

| # | claim | result | evidence (mine) | sev |
|---|---|---|---|---|
| 1 | flat_mix single-arm behaviour unchanged for its own callers | CONFIRMED | flat_mix_mmlu.py blob 555ae3ac at ee3a40f, 29c3e42, main WT and emb-e0b4 WT (4 identical); B6 still `refuse()` in vmf_em (L403/L413/L429); the VOID lives only in embedder_cross_flat.fit_space's `except SystemExit`; no other module imports embedder_cross_flat (grep count 0); the selftest's vmf_em swap is restored in `finally` | - |
| 2 | every refusal exits 2 | CONFIRMED | own shell: `--run` (no part) rc 2; `--selftest --part cpu` rc 2, last line `[E0B] EXIT 2 (REFUSED)`; argparse error rc 2 (int code re-raised); E0-EXIT subprocess check rc 2. A non-refusal exception still exits 1 with a traceback (not a refusal; acceptable) | - |
| 3 | C-E0B3-2 OMX1 killed | CONFIRMED | builder mutant "OMX1 call site drops the measured spread" KILLED by E0-SPREAD (qwen3 V spread 0.2500 reaches the tag) | - |
| 4 | VOID reach: only gemma_raw k 82; F1 (k 14), P1, P2 (k 14) unaffected | CONFIRMED | convergence-only `FM.vmf_em` on the fit matrices (8125 x 256): gemma_raw k 82 seeds 3 AND 4 REFUSED B6 (seed 3 message = ee3a40f run_embed.log L45); gemma_raw k 14 all 5 converge; gemma_card k 14/82 all 10 ok; nomic_card all 10 ok; qwen3_raw all 10 ok with iters/converged = e0b_cpu_arms.csv to the digit (10/10: fidelity of the fit matrices); nomic_raw fitted 20/20 in run_embed.log L43. Own mutant OWN-1 (void every k when the last k is) KILLED by E0-VOID | - |
| 5 | no VOID cell leaks into a summary | CONFIRMED | readers of C / ms (grep): ARMS print skips VOID; contrast loop writes None via cell_void (own or reference qwen3 VOID); rederive_f, P1/P2, F1 (`gone` check before the family loop), SECONDARY lines all branch on None; the only summaries are at k 14 (ks[0]); CSV: one VOID row per cell, partitions dropped (`if k not in voids`). Mutants "B6 VOIDs one seed only", "VOID family counted as not WORSE", "reference VOID ignored" KILLED. A missed None branch crashes before `write_once` (outcome written after score_lines): fail-closed, never a silent leak | - |
| 6 | cpu outcome of record (ee3a40f) untouched | CONFIRMED | main WT e0b_cpu_outcome.txt blob a779ebbb = ee3a40f:; e0b_cpu_arms.csv blob 492b166d = ee3a40f:; delta touches 0 files under experiment_results; with no B6 the new fit_space makes the same calls in the same order (same RNG) as before | - |
| 7 | selftest + mutants | CONFIRMED | `--selftest`: SELFTEST PASSED 62 checks, rc 0; `--mutants`: 47 of 47 KILLED, rc 0 | - |

Expected embed CSV under ruling (a): 5 arms x 20 partitions - 10 + 1 VOID row = 91 data rows (the E0-VOID stub
shape). VOID reason printed will be "V seed 3" (fit_space breaks at the first B6 seed).

## Own mutants (3, delta)
- OWN-1 contrast loop `cell_void(voids, n, k)` -> `cell_void(voids, n, ks[-1])` (VOID reaches k 14): KILLED (E0-VOID). Decisive.
- OWN-2 `n2 = assert_m2_n(...) if ms[n] else 0` -> `n2 = len(W.keyed[4])` (M2-denominator guard bypassed at the call site): SURVIVED. Not decisive (guard body is mutant-covered in E0-UNIT; the unmutated call runs). -> D1.
- OWN-3 cpu P1/P2 `if c is None: ... continue` removed: SURVIVED. Not decisive (cpu is of record and write-once; a VOID there would crash before the write). -> D2.

## Defects
- **C-E0B4-1 (HIGH, operator condition)**: the embed run's rc of record is the script's, not the pipe's: log `${PIPESTATUS[0]}` (or run without a pipe) and require the last stdout line NOT to be `[E0B] EXIT 2 (REFUSED)`; the outcome must show `VOID (ruling B6)` for gemma_raw k 82 only. Any other VOID cell (e.g. qwen3_raw at a k) is a deviation from this review's expectation and is reported, not re-seeded.
- **D1 (LOW)**: the call site of `assert_m2_n` is not covered (OWN-2 survives). Fix: an E0-CPU check that a stub partition with n2 != keyed makes run_part REFUSE, plus a MUTANTS row for the call site.
- **D2 (LOW)**: the cpu-part VOID branch (P1/P2 NOT SCORED) is never executed by a selftest. Fix: a small st_void cpu case, or a note that the branch is dead for E0b (cpu is of record).
- **INFO (not a defect of the delta)**: V at k 82 often stops at the 200-iteration cap unconverged (qwen3_raw 5/5, gemma_raw seeds 1-2, nomic_card seed 3); printed in the CSV `converged` column; not a VOID under B6 and not changed by ruling (a).

## Reviewer deviation (disclosed)
One command of mine invoked `embedder_cross_flat.py --run --part embed` (no `--target-dir`) by mistake, output
discarded. Code path: write-once check, `pool_guard.assert_pool_of_record` (read-only), then `early_pins` REFUSES
"no DIR given" before any read-set, DB-of-record or Ollama access (run_part L546-L562, early_pins L521-L522). Nothing
written: `ls` of both OUT_DIRs shows cpu files only; emb-e0b4 `git status --short | wc -l` = 0. Zero calls.

## Commands
```
git diff ee3a40f 29c3e42 ; git diff --name-only ee3a40f 29c3e42 | wc -l             # 1
git rev-parse 29c3e42:tools/analysis/embedder_cross_flat.py ; git hash-object <wt file>   # f8581aab both
git rev-parse {ee3a40f,29c3e42}:tools/analysis/flat_mix_mmlu.py ; git hash-object (main, wt)  # 555ae3ac x4
git show 29c3e42:<path> | sha256sum ; sha256sum <wt file>                               # 328a7c09.. / ff57756c..
python tools/analysis/embedder_cross_flat.py --selftest    # 62 checks PASSED rc 0 (emb-e0b4 WT)
python tools/analysis/embedder_cross_flat.py --mutants     # 47 of 47 KILLED rc 0
python .../embedder_cross_flat.py --run ; echo $?          # 2 ; --selftest --part cpu -> 2 ; --bogus -> 2
scratchpad r4/conv.py: FM.vmf_em(X_arm, k in (14,82), seeds 0-4) on scratchpad b6/X_*.npy (OMP/OPENBLAS/MKL=1);
  qwen3_raw iters/converged vs experiment_results/embedder_cross_flat/e0b_cpu_arms.csv: 10/10 equal
scratchpad r4/own.py: E.MUTANTS = (OWN-1..3); E.run_mutants()   # 1 of 3 KILLED (OWN-1)
git rev-parse ee3a40f:experiment_results/embedder_cross_flat/e0b_cpu_{outcome.txt,arms.csv} vs git hash-object  # equal
```
