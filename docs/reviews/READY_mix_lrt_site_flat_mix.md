# READY review: MIX-LRT-SITE and FLAT-MIX-MMLU at b617888 (adversarial reviewer, 2026-09-26, zero calls, no real-data statistic)

## VERDICT

**MIX-LRT-SITE: READY-WITH-CONDITIONS. FLAT-MIX-MMLU: READY-WITH-CONDITIONS. Both MERGEABLE by pathspec at the pins below.**

- The conditions are R1-R7 (section 4). None needs a code change.
- R1 (the data-steward's ck-v1 check) is **already SATISFIED** at 9073a8a (on main).
- Before the first `--run`: R2 (complete the fixture archive) and R3 (record the rulings).
- Before FLAT `--run`: R4 (FLAT `--identity-check` must print REPRODUCED).

**PCA RULING (b617888): ACCEPTED as an implementation of the registered statistic.** "Centre, PCA by SVD, top p axes" (L20612) names a subspace, not an algorithm. The top-p right singular vectors of Xc are the top-p eigenvectors of Xc^T Xc, and `np.linalg.svd` returns them in non-increasing order. On all 282 real sites the two routes give the same subspace to at most 4.5e-12 (projector 2-norm), at p = 5, 10 and 20. The observed fit and every null draw use the same route, so calibration cannot move. The thin SVD is not required. Details in section 2.

What I did NOT run: `--run`, `--analyze` or `--identity-check` on real data. I computed no LR, BIC, ICL, gain, q, purity, F6 or M4 on real data.
- My real-data reads were geometry only: principal spectra, subspace distances, radial-direction norms, and stem_key and exact-text overlap counts.
- They were opened `mode=ro&immutable=1` via `pool_guard.open_ro`.
- DB sizes and mtimes, and the -wal files (0 bytes), were identical before and after. The per-table pins in my dry-runs equal the builder's.

### Pins (the LF rendering is of record; the worktree is LF, 0 CR bytes; `git hash-object` = HEAD blob for all three)

| file @ b617888 (branch gmm-tests, worktree .claude/worktrees/gmm-tests, clean) | blob | sha256-lf16 | sha256-crlf16 |
|---|---|---|---|
| tools/analysis/mix_lrt_site.py (2,286 lines) | blob:ef965573d136d4d8457d3d79c5139e01eba544b0 | sha256-lf16:69609537de763c38 | sha256-crlf16:bb99f0eb111b093f |
| tools/analysis/flat_mix_mmlu.py (1,389 lines) | blob:c5cc7934474c6de77c36fb755cb321736d6c3b71 | sha256-lf16:70666bb7c751fd54 | sha256-crlf16:93b52490cec474af |
| tools/analysis/mix_lrt_site_fixture/WithinNodeCloudFixture.java (48 lines, unchanged since e79fdb4) | blob:e983a3c4928563e8ca4cbdbe5406f89099348ea0 | sha256-lf16:a5206e870c8f8c45 | sha256-crlf16:972ff14f9a5ed039 |

Branch scope and ancestry:
- `git diff --name-only 31d092e b617888 | wc -l` = 3, the three files above. Nothing under config/, .env, .gitignore or report/.
- `git merge-base --is-ancestor 31d092e b617888` is true, so the registration precedes the code.
- Imports are unchanged between the worktree and main: anchor_free_readout.py 514e74da, free_tests_f4_f7.py f0749d61, split_side.py 05224b5a, pool_guard.py 6521b51a.
- No state exists: `experiment_results/mix_lrt_site` and `experiment_results/flat_mix_mmlu` are absent in main.

## 1. Per-claim table

Scratch and logs are in the session scratchpad `rev_mix\`.

| # | claim | result | command / evidence | got vs claimed | sev |
|---|---|---|---|---|---|
| 1a | q with failures = (1 + c) / (B - f + 1) (A3 ii) | CONFIRMED | `q_admitted`, `summarise_site` (B = len(admitted)); ST-FAIL; my mutants R2, R2b, R2c KILLED | f = 1: 29/199; f = 0: 30/200 | - |
| 1b | VOID rules (A3 ii-vi): f >= 2 at B 199 VOIDs a site; failed observed fit VOIDs it; any failed p10 fit at a deciding site VOIDs C1 (writes `_VOID.txt`, never the outcome); a p5/p20 failure VOIDs that leg only; a failed leaf is excluded and counted; D1-D7 net of VOID | CONFIRMED | `collect` L1020-L1043, `tree_summary`, `analyze` L1405-L1410; ST-FAIL 14 checks; builder mutants f>=3, f>=1, deciding allowance, C1 VOID ignored, p20 not VOIDed, leaf kept, VOID kept: all KILLED | as ruled | - |
| 1c | per-tree R-a (A4); pooled reading printed "not of record" | CONFIRMED | `render` ra1 / ra2; branch check o0 8/11; mutant "R-a decided by the pooled reading" KILLED | as ruled | - |
| 1d | escalation: deciding sites only, band [0.02, 0.10] inclusive, draws 199..998 of the SAME stream, B = 999 decides | CONFIRMED | `escalates`, `collect` L1008-L1016, `run` L914-L929, `draw_stream(ti,row,b)`; ST4, ST-COMPLETE; my R4, R4b KILLED | as registered | - |
| 1e | drop order: above 80 CPU-min both p5 and p20 drop, p10 never | CONFIRMED | `legs_after_guard`; ST4; plan.json write-once | as registered | - |
| 1f | seeds A1, A2, A7 | CONFIRMED | `site_stream`, `draw_stream`, `leaf_stream`; ST5 cross-tree checks | as ruled | - |
| 1g | C1 point decision, both failure branches joined, R-d..R-f, MC-MARGINAL wording, P1-P8 scoring | CONFIRMED | `c1_verdict`, `render`; 32 branch checks | as registered | - |
| 1h | FLAT: T-5 joined for C1 HELD + L1 on M2 (B5) | CONFIRMED | `reading`; branch check; mutant "C1 HELD + L1 read as T-3 (B5)" KILLED | as ruled | - |
| 1i | FLAT: M4-only VOID (O2) never blocks C1 / C2; V degeneracy still refuses (B6) | CONFIRMED by execution; selftest gap | `m4_refit`, `m4_block`, `paired`. I executed analyze()'s own assembly lines verbatim (`rev_flat_o2.py`) with T's M4 VOID and a purity win: C1 HELD, reading T-3, P4 UNSCOREABLE. My mutants R3, R3b, R3d SURVIVE the selftest (it only tests O2 with C1 FAILED and never calls `paired`); R3c KILLED | isolation holds in code; untested in selftest | LOW (D5) |
| 1j | C1 / C2 / L1 clauses (point vs spread AND CI side) | CONFIRMED | `criterion`, `loss`; 25 branch checks; 4 builder mutants KILLED | as registered | - |
| 2 | PCA via SVD of Xc^T Xc is the registered "PCA by SVD, top p axes" | CONFIRMED (ruling ACCEPT) | see section 2 | real sites: max projector distance 4.5e-12; ST-PCA "4.7e-8 rad" is the arccos floor, and the true distance is about 1e-14 | - |
| 3a | ST-JVM bit-identical to the compiled Kotlin | CONFIRMED, re-executed | I recompiled WithinNodeCloudFixture.java against the ARCHIVED outer class (sha256 dfa5a30e..., = the live build class) plus the 40 inner classes from the live build. Output sha256 8da35e52493ec841 = the recorded fixture_out.txt, 29/29 lines = embedded JVM_FIXTURE. With the archive ALONE it fails: `NoClassDefFoundError: taxonomy/SeparationNullBySizeTest$LineCapture` | bit-identical | MEDIUM (D1: archive incomplete) |
| 3b | ST-EQ moments; KS D 0.0754, p 0.6253 | CONFIRMED | my full `--selftest` = 116 checks, check lines identical to the builder's log (`diff` empty), 414 s | D 0.0754, p 0.6253 | - |
| 3c | one KS test at n = 199 is enough evidence of equivalence | REFUTED as sole evidence; equivalence CONFIRMED by identity | `rev_synth.py`. KS critical D at alpha 0.01 is 0.163. MC power, 2000 reps: 0.009 against a x1.10 scale defect, 0.008 against an upper-tail-only defect, 0.287 against +0.25 SD. A defect that moves the exceedance at the bar from 0.05 to 0.08 shifts the CDF by <= 0.03, below D_crit. THE EVIDENCE THAT CARRIES IT: literal(G) == eigen(G U), draw for draw, max 3.3e-16 on 4 fixtures (m<d 110x256, 400x256, m>d 1200x512, 30x5; normalised and not), and p10 LR equal to <= 8.2e-14 relative. ST3-eigen checks every axis variance within 3% | KS blind in the tail; exact identity holds | LOW (D4) |
| 4a | cost 77.8 CPU-min (p10 + escalation + observed) against 80 | PARTLY | my `--dry-run` on the same blob: total 108.5 = p10 83.7 + esc 3.2 + p5/p20 20.7 + obs 0.9, so after the drop 87.8 CPU-min, OVER 80. Builder: 97.0 / 77.8. Same blob, synthetic timing, +13% run to run | 87.8 vs 77.8 | LOW (D3) |
| 4b | P8 (<= 60) likely fails | CONFIRMED | deciding leg with escalation: 76.9 (builder) / 86.9 (mine); registration's "about 47" refuted | P8 expected FAILED | disclosure |
| 4c | the guard never drops p10 and prints OVER; consistent with the cap rule | CONFIRMED (letter) | L20624: "p = 5 / p = 20 legs are DROPPED first ...; the deciding p = 10 leg is never dropped"; no second step is registered. `print_cost` prints each component and the budget, but the OVER wording refers to the pre-drop total; the post-drop sum is derivable only from the printed parts | consistent | LOW (D3) |
| 4d | C1 reachable; power check meaningful | PARTLY | Reachable at infinite budget: yes (L20640). Power: `rev_power.py`, `rev_curv.py` (section 3). Sphere curvature enters the top-10 subspace on the ST2 fixture (radial norm 0.16-0.71) and on the REAL sites (median 0.28-0.33, max 0.47; n00000013 0.322, n00000014 0.464, n00000055 0.461). On the fixture it inflates the null LR (median about 206 vs 106 for a flat 10-d Gaussian) and gives 0/6 at 4 within-SD. So HELD and FAILED-ALL-CERTIFY are informative, and FAILED-NO-POWER is weak | power curve plausibly transfers | MEDIUM (D2) |
| 4e | FLAT C1 / C2 scoreable at the registered MDEs | CONFIRMED (arithmetic), as registered | C1: sqrt(0.20 / 3445) = 0.007619, x2.80 = 0.02133. C2: (0.201 + 0.976) / 3.92 = 0.30026e-3, x2.80 = 0.8407e-3. Both reproduce. Scoreable only as a WIN or LOSS > max(MDE, spread_V); a tie is DESCRIPTIVE-ONLY. C2's SE is TRANSPORTED from a tree-vs-tree pair, so it is optimistic if tree-vs-flat disagrees more. C1's d = 0.20 is DECLARED | 0.0213 / 0.84e-3 | post-run check R7 |
| 4f | MIX Support arithmetic | CONFIRMED | sqrt(0.0475/199) = 0.01545, x2.80 = 0.0433; sqrt(0.0475/999) = 0.006896, x2.80 = 0.0193; D3 sqrt(0.0023188 + 0.0026667) = 0.07061, x2.80 = 0.1977. DEFF 1 BY CONSTRUCTION for C1 (source: independent seeded draws; declared); D1-D6 unmeasured (nesting), DESCRIPTIVE-ONLY | reproduces | - |
| 5a | input pins | CONFIRMED | LF blob / lf16 recomputed on the 4 CSVs and the readout: 1577e9e4/09c41b45ef5d0596, 8ed1b699/e15302b76a1aba3a, f69179a0/f44c4dbff0d8e360, f6875fc1/ae24c73beb3b7a82, b8dc4dba/69715ce266433342; site counts 66/69/60/87; J 6/14/11/10; OVERPARAM p10 3/2/3/2, p20 52/46/46/64 (my count from the CSV n); min n 126/129/119/122 | all equal | - |
| 5b | per-table DB pins | CONFIRMED | my two dry-runs print embeddings n=39631 641ff6fa...; queries n=31986 cdeca05e...; 4 snapshot graphs; mmlu_pro n=12000 dee480a9...; eval_question_link n=12257; eval_results n=560379; reserved_pool n=146568; 2 jsonl. All equal to the builder's logs | equal | - |
| 5c | every DB opened read-only + immutable; nothing written | CONFIRMED | MIX guard admits only `mode=ro&immutable=1` on 3 DBs; FLAT guard admits `mode=ro` on 4 DBs, refuses a non-empty -wal / -journal and adds immutable=1. `grep` of both scripts: no INSERT / CREATE / commit outside a tempdir selftest. Imported rejudge_grok's write path (L315) is never called and would be refused (plain path). DB sizes / mtimes / -wal 0 bytes identical before and after my reads | read-only | - |
| 5d | held-out integrity: 8,125 distinct fit texts, 0 overlap with 3,445, singleton twin groups (DEFF 1) | CONFIRMED | `rev_realdata.py A`: fit 8,125 ids = 8,125 distinct texts; exact overlap 0; stem_key overlap 0; 3,445 groups, 0 larger. Stem_key overlap with the 154 sentinels also 0, under my ASSUMED mapping id -> -(id) - 1,000,000 (154/154 rows found) | 0 / 0 / 3,445 | - |
| 5e | data-steward ck-v1 = CK-CLOSE-v1 split_side.stem_key | CONFIRMED by the steward at 9073a8a (on main; docs/reviews/STEWARD_ckv1_af_clean.md) | 11,769/11,769 keys identical Kotlin vs Python; fit x held-out 0; the 171 closure moves are absent from the fit set. Hazard: 37/3,445 (4096 d) / 45 (256 d) held-out have a fit near-copy at cos >= 0.98 | satisfied | R1 |
| 6a | builder mutants | CONFIRMED | MIX `--mutants` 49 of 49 KILLED; FLAT 28 of 28 KILLED; FLAT `--selftest` 75 checks, identical to the builder's log | equal | - |
| 6b | my mutants (13) | 7 KILLED, 6 SURVIVED | `rev_mutants.py`, section 5 | survivors: 1 equivalent, 2 fail-closed downstream, 3 selftest gaps | LOW (D5, D6) |

## 2. The PCA change (b617888): ruling ACCEPT

1. **Identity.** Xc = U S V^T gives Xc^T Xc = V S^2 V^T. The SVD of a symmetric PSD matrix is its eigendecomposition, with singular values in non-increasing order (checked). So Vt[:p] spans the same top-p principal subspace.
   - The LR is a function of the subspace only. A full-covariance Gaussian and a full-covariance GMM with k-means++ init on Euclidean distances are invariant to an orthogonal change of basis inside it: sign and permutation of the 10 axes give an LR relative difference of 0.0 (`rev_synth.py`).
   - The null draws use the same `pca_basis` as the observed site, so the change cannot move calibration.
2. **Squared condition number.** On the real sites lambda_1 / lambda_20 <= 9.9 (all four trees), so the scatter route's condition number over the axes in use is at most about 98. The eigenvector error bound eps x lambda_1 / gap is at most about 4e-12 at the worst real gap. That is what I measured.
3. **Near-degenerate eigenvalues.** Minimum relative eigen-gap at the subspace boundary over the 282 real sites:
   - p5 3.2e-3
   - p10 5.8e-5 (af_bareq512_s42)
   - p20 3.9e-4

   Max ||P_scatter - P_thin||_2 at p = 5 / 10 / 20 is 1.5e-13 / 4.5e-12 / 2.6e-13. The three deciding sites sit at p10 gaps 4.1e-3 / 2.4e-2 / 1.2e-2 with distance <= 4.1e-14 (`rev_realdata.py B`).

   A population tie (gap 1e-12) does not survive sampling. The sample gap stays >= 5e-3 at n 110-8133, and the two routes agree to 1e-14 (`rev_synth.py`).
4. **p = 20 with small n.** The minimum site n is 119 > p + 1 = 21, so no axis in use lies in the null space of Xc. The p20 legs are DESCRIPTIVE only and are DROPPED by the cost guard anyway (both projections are above 80).
5. **reg_covar 1e-6 against the data scale.** The minimum s_p^2 / n on real sites is 1.2e-2 / 8.2e-3 / 5.3e-3 at p 5 / 10 / 20, so the ridge is at most 2e-4 relative there. On a flat Gaussian at scale 0.1 the null LR is unchanged (median 105.7 vs 106.5). At scale 0.01 it breaks (median -79.4): that regime is NOT reached on these data.
6. **Record.** The change was unrequested. It rewrites a function named in the registration's words, but it stays inside them. The thin SVD is kept as `pca_basis_thin`; the builder's ST-PCA and mutant are present, and my reversed-axis mutant R1 is KILLED by ST-PCA.

## 3. Findings on power (D2) and cost (D3)

- **Curvature enters the p = 10 subspace.** On the ST2 fixture at 4 within-SD (6 clouds, B 39), `rev_curv.py`:
  - null LR median of medians 205.8;
  - certified 0 / 6;
  - radial direction's norm in the top-10 subspace 0.16-0.71.

  At 6 within-SD (3 clouds, 40 draws) the null median rises to 433-457 as the elongation grows (`rev_power.py`).

  A flat 10-d Gaussian at n 400 has null median 106.5 and p90 136.1, and it does not move with scale (`rev_invar.py`). So the fixture's null is inflated by the sphere projection, which is the registered SCOPE LIMIT. EM itself finds the split: ARI 0.86-0.89 against the truth at 4 SD.

  On the real sites the radial norm in the top-10 subspace has median 0.28-0.33 and max 0.47. That is the same regime, so the 0 / 20 at 4 SD disclosure plausibly TRANSFERS.

  Consequence: FAILED-NO-POWER (R-e) says "the LR cannot see modes below roughly 6 within-SD here". It does not say "the certificate is geometric, not modal" in substance. The registered R-e / R-f sentences stand as registered; the disclosure goes beside them (R3 (c)).
- **Cost.** The two dry-runs on the same blob give 97.0 and 108.5 total, i.e. 77.8 and 87.8 after the drop. The p10 leg will likely run OVER the 80 CPU-min figure.
  - That is the registration's letter: p10 is never dropped.
  - It stays within the author's cap, which concerns concurrency: one single-threaded process, about 90 wall-min in chunks of at most 4 min.
  - The registration's "about 47 CPU-min" (L20665) is refuted, and P8 (<= 60) is expected FAILED.

## 4. Conditions

- **R1 (SATISFIED).** The data-steward's ck-v1 = CK-CLOSE-v1 `split_side.stem_key` confirmation, 9073a8a, docs/reviews/STEWARD_ckv1_af_clean.md: CONFIRMED on all three items.
  - My independent count agrees: 0 exact, 0 stem_key, 3,445 singletons.
  - Its descriptive hazard (37 / 3,445 held-out with a fit near-copy at cos >= 0.98 at 4096 d; 45 at 256 d) is carried beside every FLAT sentence that uses "held-out". The qualifier is "content-closed under stem_key at norm-v1; near-copies below norm-v1 exist at about 1.1-1.3%".
- **R2 (before the first --run, and before any Gradle compile in the main checkout).** The data-steward copies the 40 inner classes `build/classes/kotlin/test/taxonomy/SeparationNullBySizeTest$*.class` into `Z:\FAC\TUBerlin\THESIS\TaxoArena_data\evidence_2026-09-25\mix_lrt_fixture\`, with a SHA256SUMS file.
  - The sorted-sha256 digest of the 40 today is 6aac60eb72afe9b6; `$LineCapture` is 044607b7cc5574ea.
  - Without them ST-JVM cannot be re-executed from the archive (D1).
- **R3 (the registrar, insertion only, before the run).** Record:
  - (a) the PCA ruling ACCEPT (section 2);
  - (b) the O2 narrowing as a pre-data ruling of the orchestrator. The code calls it "the orchestrator's ruling on the registrar's note O2", and the programme holds only the note (L20899).
  - (c) the curvature disclosure (D2), beside any R-e / R-f;
  - (d) the cost re-projection 77.8 / 87.8 CPU-min after the drop, with P8 expected FAILED;
  - (e) this READY with its pins.
- **R4 (FLAT only, before FLAT --run).** The run-operator runs `python tools/analysis/flat_mix_mmlu.py --identity-check` from the main checkout (registration L20731; READY condition 6 of L20911). It must print "REPRODUCED" (M1 0.727 [0.712, 0.741], M2 +12.785). A MISMATCH makes FLAT NOT READY and stops FLAT only.
- **R5 (merge).** Merge by path from b617888, the three files only.
  - Verify `git hash-object` = ef965573 / c5cc7934 / e983a3c4.
  - Commit `-- <paths>`, then `git merge-base --is-ancestor <merge> HEAD`.
  - Run from the main checkout. The chunks carry the script identity, and `--analyze` refuses a mixed identity.
- **R6 (run procedure).** Rule 7 applies: no construction, no W-window, no other pool reader or writer. Every -wal / -journal must be empty. ONE python process, single-threaded. Kill by PID only.
  1. `flat_mix_mmlu.py --identity-check` (R4).
  2. MIX-LRT-SITE: `mix_lrt_site.py --run`, repeated until it prints 0 chunks; record the `[COST]` line and plan.json, and the post-drop sum p10 + esc + obs against 80. Then `mix_lrt_site.py --analyze`, once, write-once.
  3. FLAT-MIX-MMLU: `flat_mix_mmlu.py --run` until all 12 partitions exist, then `flat_mix_mmlu.py --analyze`.

  The order is the record's (L20919 "MIX-LRT-SITE then FLAT-MIX-MMLU, sequentially"; the FLAT docstring "after MIX-LRT-SITE"). The two tests never run concurrently. A MIX C1 VOID writes `mix_lrt_site_VOID.txt` and is a failed precondition, never an outcome; FLAT still runs.
- **R7 (post-run review must re-derive).**
  - MIX: the final admitted B and f per deciding site; the CP interval; VOID counts per tree; the measured CPU against P8.
  - FLAT: the observed discordance T vs V0 against the declared 0.20, and the realised C1 SE = CI width / 3.92 against 0.00762; the realised C2 SE = F6 CI width / 3.92 against the transported 0.300e-3; spread_V against each MDE; which leg bound.

## 5. Defects

| id | sev | defect | fix |
|---|---|---|---|
| D1 | MEDIUM | The fixture archive holds the outer class only. `java` with the archived class fails with NoClassDefFoundError `$LineCapture`, so ST-JVM is re-executable only while the live build/ survives | R2 |
| D2 | MEDIUM | Sphere curvature lies inside the top-10 PCA subspace on the real sites (radial norm median about 0.3). On the matching fixture it inflates the null and removes power at 4 SD. FAILED-NO-POWER cannot carry a "not modal" substance sentence | R3 (c): disclosure beside R-e / R-f; no code change |
| D3 | LOW | The cost projection is noisy (77.8 vs 87.8 after the drop, same blob). The OVER print refers to the pre-drop total; the post-drop overrun is not stated | R6 step 2 records the post-drop sum; a future guard prints it |
| D4 | LOW | ST-EQ (ii) KS has about alpha power against tail-only or scale defects | the draw-for-draw identity (this review) carries the equivalence; add it as ST-EQ (iii) in a later build |
| D5 | LOW | FLAT selftest never executes `paired()` or `analyze()`'s assembly, and tests O2 only with C1 FAILED. My mutants R3, R3b, R3d survive. Code verified correct by my execution | a later build adds a C1-HELD + M4-VOID branch and a `paired()` call |
| D6 | LOW | MIX `run()`'s escalation decision is not unit-tested (R4c, R4d survive). It is fail-closed: `collect` refuses missing or extra escalation draws (ST-COMPLETE) | later selftest |
| D7 | LOW | ST-PCA prints the arccos floor (4.7e-8 rad) as the "max principal angle"; the projector distance is about 1e-14 | cosmetic |

My mutants (`rev_mutants.py`; tests are selftest subsets on the pinned blobs):

| mutant | result |
|---|---|
| R1 PCA takes the bottom axes (Vt[::-1]) | KILLED (ST-PCA) |
| R1b PCA axes from the centred scatter, projection of the uncentred X | SURVIVED: equivalent mutant (a translation; the LR is translation-invariant) |
| R2 q denominator = B_total with failed draws removed from c | KILLED (ST-FAIL) |
| R2b failed null draws counted as exceedances | KILLED (ST-FAIL) |
| R2c q = (1 + c) / (B - f) | KILLED (ST4) |
| R3 T's M4 VOID forces C1 FAILED | SURVIVED (D5) |
| R3b `paired()` M4-VOID guard removed | SURVIVED (D5); the guarded code executed by me: d4 None, d1 intact |
| R3c T's M4 VOID refuses the analysis | KILLED (FT-M4VOID) |
| R3d spread_V of M1 set to NA by T's M4 VOID | SURVIVED (D5) |
| R4 escalation ignored in `collect` | KILLED (ST-COMPLETE) |
| R4b band upper edge 0.11 | KILLED (ST4) |
| R4c `run()` escalates every deciding site | SURVIVED (D6; fail-closed in `collect`) |
| R4d `run()`'s q199 ignores f | SURVIVED (D6; any f > 0 at a deciding site VOIDs C1 anyway) |

## 6. Commands (session scratchpad `rev_mix\`; worktree clean after every run, `git status --short | wc -l` = 0)

- `python tools/analysis/mix_lrt_site.py --selftest` produced `rev_mix_selftest.log`: 116 checks, rc 0.
- `--mutants` produced `rev_mix_mutants.log`: 49/49. `--dry-run` produced `rev_mix_dry.log`.
- `python tools/analysis/flat_mix_mmlu.py --selftest` / `--mutants` / `--dry-run` produced `rev_flat_*.log`: 75 checks, 28/28; the dry-run is identical to the builder's except timing.
- JVM re-execution: `rev_mix\WithinNodeCloudFixture.java` (class dir redirected to a copy) produced `jvm_rerun.txt`, sha256 8da35e52493ec841.
- Own checks: `rev_synth.py`, `rev_mutants.py mix|flat`, `rev_flat_o2.py`, `rev_power.py`, `rev_invar.py`, `rev_curv.py syn|real`, `rev_realdata.py A|B`. The real-data ones are geometry and overlap counts only.
