# POST-RUN review: CERT-PLANTED (2026-10-05; zero calls; read-only)

Code of record: `tools/analysis/cert_planted.py` blob:028f05a2 (LF; worktree rp12-r2-run and main identical by
`git hash-object`), SeparationNullBySizeTest.kt blob:abd9c533, CertPlantedArmTest.kt blob:ab2620c6, build.gradle.kts
blob:2225cb6c (all four re-hashed in rp12-r2-run = the chain's pin lines = the registrar's READY record L24567ff).
Outcome `E:/TaxoArena_backup_2026-10-05_cert_planted/outcome.txt` sha256 55efbce9...; SHA256SUMS.txt there verifies 21/21
(`sha256sum -c`, 0 non-OK lines). Registration L24304-L24315 with the B-1 brackets (0d76dc87 record L24567-L24571).

## Verdict

**VALID**, with the scoring and the F-CP words CORRECTED below (the printed P2 / P3 / P4 scores and the printed F-CP
sentence are NOT of record). P-CPL1 DISCHARGED (the null read the planted rows).

- CP0 **SIZE-OK** (delta 0, n 486: 0 of 15 certified; 0 NOT EVALUABLE).
- CP1 **INSENSITIVE** at delta_dec 8, n 486 (economics 1, math 0, physics 1 of 5; INSENSITIVE needs <= 1 of 5 in >= 2 of 3).
- **F-CP FIRED**, in the B-1 words only: "the plain J site null, moment-matched to the site's own (planted) rows, is
  insensitive to a planted 2-way shift of delta 8 at depth-1 sizes; G12's 0 of 60 is uninformative about 2-way structure
  UNDER THAT NULL". Never "insensitive to strong 2-way structure" (the printed line 239) and never "the certificate cannot
  detect structure".
- Descriptive deliverable (power curve, n 486): delta 0/2/4/6/8/10/12 -> 0/0/0/0/2/12/15 of 15; n 441: 0/0/0/0/4/15/15.
  delta* (n 486) economics 12, math 10, physics 10; median 10. delta* (n 441) 10/10/10.

## Per-claim table (deciding claims)

| # | claim | reviewer's number | printed | verdict | sev |
|---|---|---|---|---|---|
| 1 | per-site k_d / reached from replicates.csv (211 sites x 300 reps) | 0 mismatches of 211; 63,300 reps | sites.csv | CONFIRMED | - |
| 2 | IDENTITY precondition (n 6,993; declared 0.107803; k 0; p95 0.041626) | k 0; p95 = sorted[284] 0.0416257 | same | CONFIRMED | - |
| 3 | CP0 delta 0, n 486 | 0 of 15, NE 0 -> SIZE-OK | SIZE-OK | CONFIRMED | - |
| 4 | CP1 delta 8, n 486 | econ 1, math 0, phys 1 -> INSENSITIVE | INSENSITIVE | CONFIRMED | - |
| 5 | power curve n 486 / n 441; delta* | 0/0/0/0/2/12/15; 0/0/0/0/4/15/15; 12/10/10 and 10/10/10 | same | CONFIRMED | - |
| 6 | P-CPL1: each PL null read its planted rows | median null p95 delta 0 -> 12: econ 0.0690 -> 0.2056, math 0.0692 -> 0.1832, phys 0.0670 -> 0.1997 (n 486); same at n 441; rises in 30/30 draw-cells; code: `vectors = ids.map { cplUnit(planted rows) }` -> cpcMoments (Kt L3726-L3730, L2205-L2206) | - | CONFIRMED (discharged) | - |
| 7 | printed P2 / P3 / P4 scoring | scored against the PRE-B-1 bracket (P2 delta 8 14 [10,15]; P3 0.75/0.15/0.10; P4 6 [4,8]) | Brier 1.3950; 3 OUTSIDE; P4 OUTSIDE | REFUTED as of record (C-7: superseded predictions scored) | HIGH |
| 8 | printed F-CP sentence | pre-B-1 wording | "insensitive to strong 2-way structure" | REFUTED (wording) | HIGH |
| 9 | no write to DBs of record | per-table hashes before (01:05:29) = after (04:20:15); emb_hashes json identical sha256 17c31d55; worktree embeddings_cache.db / snapshots.db mtime 2026-10-01, -wal 0 bytes | - | CONFIRMED | - |

## Rescoring under the B-1 brackets (of record; L24312 last bracket)

| prediction | B-1 band | observed | scored |
|---|---|---|---|
| P1 CP0 SIZE-OK 0.85 | delta 0: 0 [0, 1] | SIZE-OK, 0 | Brier 0.0225; inside |
| P2 delta 0 | 0 [0, 1] | 0 | inside |
| P2 delta 2 | 0 [0, 1] | 0 | inside |
| P2 delta 4 | 0 [0, 1] | 0 | inside |
| P2 delta 6 | 0 [0, 3] | 0 | inside |
| P2 delta 8 | 6 [0, 10] | 2 | inside (|2-6| = 4) |
| P2 delta 10 / 12 | no band (anchors additive 15, multiplicative 0) | 12 / 15 | descriptive: nearer the additive anchor |
| P3 SENSITIVE 0.10 / MIXED 0.50 / INSENSITIVE 0.40 | three-way Brier | INSENSITIVE | **0.6200** (0.01 + 0.25 + 0.36) |
| P4 median delta* | 10 [10, '> 12'] | 10 (12, 10, 10) | inside (at the lower edge) |

Printed beside, NOT scored: the pre-B-1 bracket (P3 Brier 1.3950; P2 delta 6/8/10 OUTSIDE; P4 6 [4, 8] OUTSIDE) and the
registered originals (line 250). Of the reviewer's two pre-data calibrations, the additive one called delta* 10 (held) but
9 of 15 at delta 8 (observed 2); the multiplicative one called 0 everywhere (refuted at delta >= 10).

## Defects / conditions

- **C-CP1 (HIGH; registrar)**: the outcome file prints P2 / P3 / P4 against the superseded in-code predictions (the build
  predates B-1; B-1 said "code kept"). Of record are the B-1 scores in the table above (P3 Brier 0.6200; every P2 band inside;
  P4 inside). Fix: registrar's OUTCOME bracket quotes this table; the printed lines 241-249 are quoted only as "pre-B-1, not
  of record". No code change (write-once outcome stands).
- **C-CP2 (HIGH; registrar)**: printed F-CP line 239 carries the withdrawn wording. Fix: the B-1 words above, verbatim.
- **C-CP3 (MEDIUM; words)**: delta 8 is the crossing point, not a margin: the median planted statistic sits at the median
  null p95 (econ 0.1176 vs 0.1211, math 0.0986 vs 0.1065, phys 0.1129 vs 0.1165); the site-own null grows with delta
  (p95 x 1.5-1.8 from delta 0 to 8). INSENSITIVE is a statement about where a self-calibrating null and the planted signal
  cross (delta about 9-10), not a power failure at a supra-threshold shift. delta* on the statistic scale (0.15-0.23) is
  4-6x G12's TOP 0.037-0.040: under this null, a TOP split would need to be about 4x stronger to certify.
- **C-CP4 (MEDIUM; carried, M-2)**: the deciding count rests on about 2-3 effective units (economics n 486 subsamples
  overlap 468-470 of 486; u_d and halves shared across categories of one draw); no interval is claimed on 1/0/1.
- **R-CP1 (disclosure, operations)**: the detached chain ran the arm 01:05:29-02:00:05 rc 0 (chain log), then `gradlew
  --stop` rc 0, then `--hashes after` REFUSED at 02:00:06 because java.exe PID 71872 (157,908 K) was alive (hashes_after.log);
  CHAIN ABORT before --analyze and before the output backup. By hand: `--hashes after` at 04:20:15 (hashes_after2.log and
  emb_hashes_after.json mtimes; NOT about 02:10 as briefed), equal to before; `--analyze` at 04:21:21 (outcome mtime);
  outputs copied by hand to E:/TaxoArena_backup_2026-10-05_cert_planted (04:21:30). The pre-arm DB backup is in a DIFFERENT
  dir, E:/TaxoArena_backup_2026-10-04_cert_planted/db (embeddings_cache.db 806,920,192 B, snapshots.db 1,144,037,376 B; the
  chain's $bk was dated at chain start). PID 71872's identity is UNDETERMINED (no process list was logged); the equal hashes
  and the 2026-10-01 DB mtimes show no write either way. backup run.log is the pre-run selftest/mutants log of 2026-10-04
  20:03 (not a chain step); analyze.log carries its own selftest 14/14.
- **L-CP1 (LOW; ops fix for future chains)**: `--hashes after` should poll for the arm's JVM to exit (bounded wait) instead
  of aborting; the chain's `$bk` should be one dir for DB backup and outputs.

## Mutants (own; deciding path is the readout over replicates.csv; small delta: 2)

- X1 recount with `>` instead of `>=` for k_d: 0 of 211 sites change certified state -> survives, not decisive (tie
  convention immaterial). Near the bar: physics_n486_d2_D8 k_d 15 (misses by one replicate) and economics_n486_d5_D10
  k_d 16; counting the first would leave CP1 INSENSITIVE (economics 1, math 0 still <= 1).
- X2 CP1 read from n 441 instead of 486: econ 2, math 0, phys 2 -> still INSENSITIVE -> survives; the word does not hinge on
  the size (descriptive robustness, not a code test).

## Commands

```
cd E:/TaxoArena_backup_2026-10-05_cert_planted && sha256sum -c SHA256SUMS.txt | grep -vc ': OK$'      # 0
python E:/TaxoArena_tmp/rev_cp/recount.py   # reads arm/sites.csv + arm/replicates.csv only: 0 mismatches of 211;
                                            # curves, CP0, CP1, delta*, median p95 per delta, P3 Brier 0.62 / 1.395
git -C .claude/worktrees/rp12-r2-run hash-object tools/analysis/cert_planted.py src/test/kotlin/taxonomy/SeparationNullBySizeTest.kt \
    src/test/kotlin/taxonomy/CertPlantedArmTest.kt build.gradle.kts     # 028f05a2 abd9c533 ab2620c6 2225cb6c
sed -n 3715,3731p src/test/kotlin/taxonomy/SeparationNullBySizeTest.kt  # PL vectors = cplUnit(planted rows) -> cpcMoments
ls -la --time-style=full-iso E:/TaxoArena_tmp/cert_planted_run/ .claude/worktrees/rp12-r2-run/{embeddings_cache,snapshots}.db*
cat E:/TaxoArena_tmp/cert_planted_chain.log E:/TaxoArena_tmp/chain_cert_planted.ps1
```
