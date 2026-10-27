# POST-RUN review: TREE-LIKE (2026-10-05; zero calls; read-only)

Code of record `tools/analysis/tree_like.py` blob:82f79b9d, zc_common blob:c912dccf (`git hash-object` on main = the
outcome header). Outcome `E:/TaxoArena_backup_2026-10-04_tree_like/tree_like_outcome.txt` sha256 6a73f417...; the run log
(UTF-16LE) carries the same 52 lines plus the write and scratch lines (diff after `iconv`). Run 21:01:03-01:04:21 rc 0
(chain_sa_tl.log), after SCALE-AGREE and before CERT-PLANTED's arm (01:05:29): one heavy process at a time held.
Registration L24362-L24373 with the C-TL1 / TT-R1 / TT-R4 brackets.

## Verdict

**VALID.** TL0 **PASS** (control 5/5, 5/5); TL1 **MIXED** (MASSIVE 0 of 5, CLINC 5 of 5); **F-TL NOT FIRED**; TL2 AGREES
(descriptive). Words of record (C-TL1 plus C-TL3 below):

> "Against the moment-matched Gaussian null, qwen3 (native) is Gromov-tree-like on CLINC (5 of 5 subsamples, z -2.5 to -3.6)
> and not on MASSIVE (0 of 5) by the registered max-four-point estimator. A flat cluster mixture also reads tree-like under
> this test, so neither corpus's reading is evidence of hierarchy, and MIXED is not 'CLINC is hierarchical, MASSIVE is flat'.
> F-TL did not fire: the test does not show that a tree imposed on MASSIVE / CLINC is an artefact."

## Per-claim table (deciding claims)

| # | claim | reviewer's number (independent code) | printed | verdict | sev |
|---|---|---|---|---|---|
| 1 | four-point delta = (S1 - S2)/2 on sorted pair sums; delta_rel = 2 max / diam (Khrulkov) | code L259-L264 read; own impl: unit square 0.41421, star-tree metric 2.2e-16, two-cherry tree 0.0 (X2) | - | CONFIRMED | - |
| 2 | null = mu + (G/sqrt m) Cc, rows unit-normalised (siteNull withinNodeCloud) | own re-implementation, same seeds, reproduces z to 3 dp (rows 3-5); identity precondition printed 2.2e-16 (TT-R1, taken as given) | - | CONFIRMED | - |
| 3 | MASSIVE sub 0: obs delta_rel / z | 0.2648 / -1.234 | 0.2648 / -1.234 | CONFIRMED (digit) | - |
| 4 | MASSIVE sub 1: obs / z | 0.3083 / +1.473 | 0.3083 / +1.473 | CONFIRMED (digit) | - |
| 5 | CLINC sub 0: obs / z | 0.2386 / -2.535 | 0.2386 / -2.535 | CONFIRMED (digit) | - |
| 6 | data object: TRAIN, kept, in-scope rows; subsample of 2,000 | own SQL: MASSIVE 9,870, CLINC 13,487 TRAIN rows | 9870 / 13487 | CONFIRMED | - |
| 7 | TL1 counts from the 10 printed deciding z | MASSIVE 0 below -2 (max -1.386); CLINC 5 (max -2.535) -> MIXED | MIXED | CONFIRMED | - |
| 8 | TL0 control counts | 5/5 both (z -12.2 to -16.7) | PASS | CONFIRMED (from print) | - |
| 9 | TL2 means | MASSIVE qwen3 -0.492 vs gemma +0.360; CLINC -2.956 vs +0.743 | same | CONFIRMED | - |
| 10 | Brier P1 / P2 / TL1 events / P3 | 0.0225; 0.3600, 0.1600; 0.2025, 0.4900, 0.0625; 0.0900 | same | CONFIRMED | - |
| 11 | Support: DEFF 1.0, n_eff 5 | subsamples of 2,000 overlap (expected shared points about 405 of 2,000 MASSIVE, 297 CLINC): DEFF slightly above 1, n_eff slightly below 5; the classification is far from the 4-of-5 boundary on both corpora (it would need 4 subsamples to flip) | DEFF 1.0 | PARTLY (immaterial) | LOW |

## Defects / conditions

- **C-TL3 (MEDIUM; words, registrar)**: MASSIVE's "not tree-like" rests on the single most extreme sampled quadruple.
  Descriptive diagnostic (data vs ONE null draw, not a z): max dq exceeds its own 99.99th percentile by 1.37-1.58x on the
  data (MASSIVE s0 1.37, s1 1.58; CLINC s0 1.37) against 1.22-1.33x on null draw 0; at the 99.99th percentile the data sit
  BELOW the null draw on both corpora (2 q99.99 / diam: MASSIVE 0.193 / 0.196 vs 0.212 / 0.223; CLINC 0.174 vs 0.217), and
  the mean four-point delta is z -12 to -14 on both corpora in every arm (printed, descriptive). So the MASSIVE / CLINC
  contrast is a property of the max estimator's extreme tail, not a robust difference between the corpora. Fix: the
  registrar's outcome bracket quotes TL1 with "by the registered max-four-point estimator" and never reads MIXED as a
  corpus contrast in structure; no new statistic is promoted (C-7: the quantile and mean versions stay descriptive).
- **C-TL4 (LOW; record)**: the READY review's expectation (D-2) that TL1 TREE-LIKE was "near-certain" on clustered corpora
  did not hold on MASSIVE (0 of 5); the expectation came from a synthetic flat 27-cluster fixture (n 600, d 256). C-TL1's
  conclusion (a TREE-LIKE reading carries no hierarchy) is unaffected.
- **C-TL5 (LOW; descriptive gap)**: the registered DESCRIPTIVE MMLU-Pro arm (`--run --mmlu`, a pool reader) was not run;
  record it as not delivered, or schedule it in a pool slot (rule 7). No deciding consequence.
- Support (row 11) LOW: say "n_eff about 5 (overlapping subsamples)"; no change to any word.
- Backup: SHA256SUMS.txt in E:/TaxoArena_backup_2026-10-04_tree_like now covers tree_like_outcome.txt (6a73f417...),
  tree_like_run.log (e21b4104..., UTF-16LE original) and chain_sa_tl.log (39c079c8...), copied in by this review (`cp -p`);
  `sha256sum -c` 3/3 OK. The earlier one-line file covered the outcome only.

## Mutants (own; deciding path; not re-running the builder's 21/21 from the READY)

- X1 null without mu (zero-mean cloud) in my re-implementation: not run (T9 of the builder's table kills it; taken as given).
- X2 four-point delta with S1 - S3 instead of S1 - S2: SURVIVES the star-tree fixture (all three sums equal on a star) but is
  KILLED by a two-cherry tree metric (d 1 within, 2 across): correct 0.0, mutant 1.0. The run's L262 uses st[2] - st[1]
  (S1 - S2): correct. Decisive for row 1 only.

## Commands

```
cd /z/FAC/TUBerlin/THESIS/TaxoArena && git hash-object tools/analysis/tree_like.py tools/analysis/zc_common.py   # 82f79b9d c912dccf
iconv -f UTF-16LE -t UTF-8 E:/TaxoArena_tmp/tree_like_run.log | tr -d '\r' | sed -n '8,$p' | diff <(tr -d '\r' < .../tree_like_outcome.txt) -
python E:/TaxoArena_tmp/rev_tl/recompute.py massive:0 clinc:0 massive:1
   # own SQL on intent_transfer_corpora_v1.db + intent_emb_qwen3.db (mode=ro&immutable=1), own four-point / null code,
   # same seeds, B 200: 0.2648 -1.234 | 0.2386 -2.535 | 0.3083 +1.473
python E:/TaxoArena_tmp/rev_tl/diag.py      # max / p99.99 / p99.9 of the four-point values, data vs null draw 0
cd E:/TaxoArena_backup_2026-10-04_tree_like && sha256sum -c SHA256SUMS.txt                               # 3 OK
```
