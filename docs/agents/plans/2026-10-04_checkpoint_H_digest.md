# Checkpoint H: digest, 2026-10-04 (zero judge calls throughout)

## Recorded since checkpoint G (all VALID)
| Test | Verdict | One line |
|---|---|---|
| ONLINE-STAGE2 | OS1 LOSS −3.3pp; OS2 UNDER-CATCH 0.55; F-OS fires | Frozen means keep ids stable by construction; online filing still loses to a rebuild. Periodic batch rebuild stays necessary. |
| GEMMA-OWN-BAR | L = 1; F-GO fires (leaf clause) | gemma's own bar (0.0437) is stricter than qwen3's, so the M-AF-g stall is not caused by a too-strict qwen3 bar. |
| CERT-PC-K2-KNOWN | NO-CONTROL | No merged pair cleared its gate; k=2 sensitivity is undetermined. |
| CERT-K2-DEFLATED | ELONGATION-CONFOUNDED; F-DF not fired | The deflated null tracks axis variance; the plain J null stays the certificate of record. |
| CELL-FLIPS | FLIPS-EXIST 7/101 | Mostly single BBH tasks won by internlm; declared tasks show the same; not "the tree finds flips the labels miss". |
| NEARDUP-AUDIT | UNDETERMINED (R1-dependent) | 5/70 twins missed; never call the tree a safe blocking index. |

## Ready, held for the author
- COVERAGE-AUDIT: merged and READY. The run is held for the B-5 ruling (CV-R2, the "dominant member" reading); say "run it" or switch the reading.

## Infrastructure
- C: was full. 101 GB of our test leftovers and scratch DB copies were deleted with the author's go; C: now has 110 GB free.
- Temp and scratch are now on E:/TaxoArena_tmp via scratch_dir.py (f460d72c), with the purge fix e3b04426. KNOWLEDGE.md is updated.
- INCIDENT: mutants of the purge guard, run on real paths, wiped about 7,100 entries in the system Temp (no repo, DB or E: data lost). A sandbox-only rule is now in memory and KNOWLEDGE.

## Drafts (docs/drafts, not report/)
- 2026-10-03_results_SQ3_SQ5.md and 2026-10-04_results_SQ1_SQ2.md. Unsourced sentences were left out and listed at the end of each.

## Author decisions open
1. COVERAGE-AUDIT B-5: run with CV-R2, or switch the reading.
2. D2 (SQ2 instrument; gates RP19) and D6 (SQ3 wording), plus adoption of memo v3.
3. Orchestrator rulings to confirm or overrule: CERT-K2-DEFLATED option (b); COVERAGE B-4 mirrored filing.
4. Drafts: wording points listed at the end of each draft (F-GO "calibrated", closed judge-line numbers, MC antecedents, the r8 paragraph).
5. FITSET stage 1 (the research lead recommends declining).
6. Git history: rewrite 66fedf63 (83 MB of RP13 outputs) before any push.
7. Optional: remove the broad `Bash(python -c ' *)` permission rule.
