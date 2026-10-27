# POSTRUN — COVERAGE-AUDIT: the readout of coverage_audit.py --run

Reviewer: adversarial-reviewer, 2026-10-04. Zero calls, no key. Object: `experiment_results/archv2/coverage_audit/`
coverage_audit_outcome.txt (65 lines, sha256 93d17e9883844c7bd0b55f6871eea09e3821100b953f848a02224fb5352bdae3), coverage_audit_occupancy.tsv
(596 lines, sha256 47daedff6f07018e32547769e87ad00d7a846e97a5edf2cf7ca29fbe3d7c5f06), coverage_audit.READ_STARTED (sha256 deee4a8c…5e65),
written 11:23:23-11:23:27 by coverage_audit.py blob:75f65a27 (LF; the main checkout's CRLF bytes are sha256-crlf16 4b5c2ab3411e07ee), merged at
0708354a (03:09:32), after the author's "run it" (B-5 CV-R2 kept). Console: `E:/TaxoArena_tmp/cv_run.log`. Registration prog L24156-L24167
with brackets B-1, B-3, B-4, B-5; reviews READY_cell_flips_coverage.md and READY_coverage_audit_delta.md.

## Verdict: VALID

Chips: **CV1 EQUIVALENT (within ±0.020)**; **F-CV NOT FIRED**; rule 8 not refuted (|D_X| 0.00322 < 0.020). P1 D_X HELD, CV1 Brier 0.3800;
P2 pooled X(AF-U) FAILED (0.032 below [0.05, 0.25]); P2 GPQA, P2 MATH and the P2 order HELD; P3 HELD.
Qualifiers that travel with the words:
- **(Q1) EQUIVALENT is not "equal".** The 90% interval [−0.00017, +0.00690] lies inside ±0.020; the point favours k-means by 0.3pp
  (AF-U files slightly MORE items into foreign cells); the 95% interval [−0.00085, +0.00746] covers 0.
- **(Q2) The filing rule mattered; the dominance rule did not.** Under the registered nearest-of-all K_0 (descriptive, B-4) D_X = −0.00508,
  with the 95% interval [−0.00981, −0.00017] excluding 0. That rule would also read EQUIVALENT, but the sign flips: K_0's IFEVAL X_m is
  0.284 under nearest-of-all and 0 under the mirror (D-1 was real). Without IFEVAL both filings agree, +0.00331 / +0.00279. B-5 is moot
  on this data: X under construction-member dominance equals X under CV-R2 for AF-U (0.03233), mirrored K_0 (0.02912) and K_0 all
  (0.03741). The two rules differ only for declared (0.06315 vs 0.05739).
- **(Q3) The per-member lines are mostly structural.** BBH and MUSR are 0 in every arm. IFEVAL is 0 in AF-U and in mirrored K_0 because
  it is filed BY SOURCE, so that 0 was not measured. Mixing lives in GPQA, MATH and MMLU-Pro only.

## Per-claim table (my independent recompute against the outcome)

Mine: my own K_0 centroids (normalised mean of the TRAIN rows per k_cells_s0 label; filed by source they reproduce 12,334 / 12,334 labels),
my own mirrored / nearest-of-all / declared-centroid filing, dominance, X, and the bootstrap (B-1 streams, loop).

| # | claim | outcome | mine | verdict | sev |
|---|---|---|---|---|---|
| CV1 | D_X mirrored, 95 / 90% | +0.00322; [−0.00085, +0.00746]; [−0.00017, +0.00690] | identical to 5 dp | CONFIRMED | — |
| X | pooled AF-U / K_0 / K_0 all / declared | 0.03233 / 0.02912 / 0.03741 / 0.05739 | identical | CONFIRMED | — |
| Xm | per member, 4 arms (outcome L34-L39) | e.g. GPQA 0.35294 / 0.47059 / 0.47059 / 0.44118 | all 24 values identical | CONFIRMED | — |
| all | nearest-of-all D_X | −0.00508 [−0.00981, −0.00017]; 90% [−0.00903, −0.00101] | identical | CONFIRMED | — |
| ex | without IFEVAL (5,745 / 5,242) | mirrored +0.00331 [−0.00087, +0.00770]; all +0.00279 [−0.00139, +0.00721] | identical | CONFIRMED | — |
| S | DEFF, SE, discordance | 0.992; 0.00211; 0.0262 | 0.992; 0.00211; 0.02624 | CONFIRMED | — |
| K0 | K0-IDENTITY | 18,473 / 18,473 | TRAIN 12,334 / 12,334 (independent centroids) | CONFIRMED | — |
| Br | P1 Brier | 0.3800 | (0.5−1)² + 0.3² + 0.2² = 0.38 | CONFIRMED | — |
| W | written once | mode "x"; one READ_STARTED | all 65 outcome lines in the console (1 differs only by the em-dash's console encoding); console-only: the OUTCOME line; 0 Traceback / REFUSED; TSV rows: cell 123 / 123 / 123 / 52 + member_cell 173 | CONFIRMED | — |

## Support re-measured

DEFF 0.992 (component vs i.i.d. bootstrap on the mirrored D_X; registered 1.102 transported from AK1); n_eff 5,953. SE 0.00211 against
the planned 0.00432, because discordance was 0.026, not 0.10. TOST reach at the measured SE: |D_true| < 0.020 − 2.487 × 0.00211 = 0.0148.
The observed 90% upper bound 0.0069 is 0.013 inside the margin, so EQUIVALENT is not marginal.

## Disclosures that bind the wording

- **GPQA n 34 (B-3).** X_m(AF-U) GPQA = 12/34 = 0.353 (SE sqrt(0.353 × 0.647 / 34) = 0.082, before DEFF); K_0 16/34 = 0.471. The P2 GPQA
  HELD and the "GPQA first" order rest on 34 items; the AF-U vs K_0 GPQA gap (4 items) is not interpretable.
- MATH: 51/390 = 0.131 foreign in AF-U, mirrored K_0 and K_0 all alike. MMLU-Pro: AF-U 128 of 3,376 (0.0379) vs mirrored K_0 105 (0.0311);
  most of D_X comes from MMLU-Pro (descriptive).
- AF-U cells with own-member coverage < 0.50: GPQA:n00000009 (0.179, n 28) and GPQA:n00000010 (0.400, n 15). Their EVAL items are
  mostly from other members.
- Foreign filing is not an error (members overlap: GPQA / MMLU-Pro science, MATH / MMLU-Pro math; registered WILL NOT SHOW).
- OOS (descriptive): EVAL OOS rate 0.045; IFEVAL 0.537. OOS validity on capability text is not established; no reading.
- B-5 (CV-R2) was the orchestrator's ruling, kept by the author ("run it"); it does not change any AF-U or K_0 number here (Q2).
- No declared-label comparison of AF-U is licensed (declared-centroid is a labelled reference, descriptive).

## Registrar's wording (proposed)

"COVERAGE-AUDIT, content-closed v2 union split, 0 calls: filing each union member's EVAL items into cells and scoring the share that land
in a cell whose TRAIN-dominant member is another member, the anchor-free tree (AF-U) and per-source k-means (K_0, mirrored one-cell filing
per B-4) mix members **EQUIVALENTLY within ±0.020: D_X = X(AF-U) − X(K_0) = +0.0032, 90% [−0.0002, +0.0069] (TOST; 5,907 items / 5,404
components; DEFF 0.99)**; F-CV not fired. Pooled X: AF-U 0.032, K_0 0.029 (registered nearest-of-all K_0 0.037, descriptive; its
D_X −0.0051 [−0.0098, −0.0002] carries the IFEVAL one-cell asymmetry; without IFEVAL both filings give +0.003). Per member (AF-U / K_0):
BBH 0 / 0, MUSR 0 / 0, IFEVAL 0 / 0 (filed by source, not measured), MATH 0.131 / 0.131, MMLU-Pro 0.038 / 0.031, GPQA 0.353 / 0.471
(**n 34**). Predictions: P1, P2 GPQA, P2 MATH, P2 order and P3 HELD; P2 pooled FAILED (0.032 < 0.05); Brier 0.38."
Not licensed: "equal" or "no difference" (equivalence within ±0.020 only); "the tree separates benchmarks better / worse than k-means";
any GPQA contrast; foreign filing read as error; any OOS claim.

## Defects

None on the deciding path. D-3 (the Kish label) stands as bracketed; the outcome prints 1.3115 = Σn²/Σn.

## Commands

```
sha256sum experiment_results/archv2/coverage_audit/*         # 93d17e98… / 47daedff… / deee4a8c…
git hash-object tools/analysis/coverage_audit.py              # 75f65a27
python E:/TaxoArena_tmp/rv_cv/post_cv.py   # (temp, removed after use) independent: centroids from k_cells_s0 TRAIN means (12,334/12,334 by-source refile),
                                           #   mirrored / all / declared filing, dominance, X_m, 4 D_X with B-1 bootstrap, DEFF, discordance
python: outcome lines in E:/TaxoArena_tmp/cv_run.log (64 exact + 1 encoding-only); grep -c 'Traceback|REFUSED' = 0; TSV row counts
E:/TaxoArena_backup_2026-10-04_coverage_audit: outcome + occupancy + READ_STARTED + SHA256SUMS.txt (sha256sum -c OK)
```
