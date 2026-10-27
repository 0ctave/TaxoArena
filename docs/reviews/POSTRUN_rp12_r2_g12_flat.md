# POSTRUN_rp12_r2_g12_flat: ARCH-V2-E-T-R2 lane r2, G12 (9c9ee9e7) and FLAT (36f1310f)

Reviewer: adversarial-reviewer, 2026-10-01, at main 36f1310f. Zero calls. Read-only: the worktree DBs
(`.claude/worktrees/rp12-r2-run`: embeddings_cache.db, mmlu_pro_dataset_cache_v2.db, snapshots.db) were copied to scratch,
sha256 equal to the originals, and every recompute ran with `TAXOARENA_DATA_ROOT=<scratch>`. Nothing written outside scratch
except this file. Against: R2 registration L22417-L22434 (G12 and FLAT verbatim from ARCH-V2-E-T L22028-L22060) and the brackets
through L22537 (R-a, R-c, D-G12-1, D-RV-1 / P3 "known pre-read (disclosed)").

## VERDICT

| readout | verdict | conditions |
|---|---|---|
| G12 | **VALID: N-1 FIRES** (hierarchical-BH set 0 of 60; 0 of 14 depth-1 sites) | W-G1, W-G2 (P3 mark), W-G3 |
| FLAT | **VALID: identity REPRODUCED; C1 PURITY HELD; C2 FAILED; L1 does not fire; F3 does not fire** | W-F1..W-F3, C-F1 (record FLAT-AN-1) |

No BLOCKER, no HIGH. Every deciding number reproduced to the printed digit by an independent script. The code that ran is the
code the READY reviewed (blobs equal the READY_g12reader_flatf3 f20a7081 pins), so no code mutants were re-run; the checks
below are the data object, the numbers, and how sensitive each verdict is.

## Pins (blob = `git hash-object`, LF of record; sha256 prefixes LF / raw)

- g12_reader.py blob:1c8bf8bccc922449422f5957af99f63c228026aa (lf16 15c7ed5d4600f8d9, crlf16 bcab0a62bb7b1776) = HEAD = READY pin.
- flat_v2.py blob:ef7bca333504c9097015d498e24a2af858d409ba (lf16 2741fa7dcd859582, crlf16 4c00c4aceeed1b4e) = HEAD = READY pin;
  state/meta.json carries the same blob.
- cert_resolution.py blob:dbe9425d (lf16 3e3fb1b91aa3d361).
- site_null_B0_mmlu_pro_lb.csv blob:ec8619f8 (lf16 d8f2c379f2823496; working file CRLF, 61 CR) = reader pin.
- G12_OUTCOME.txt blob:e3d06138eac51734fbba27de11fb852989fbf576 (0 CR; lf16 = raw16 2ce2effbf42fb1cc).
- G12_sites.csv blob:21f110afae674f5f641e992c57f9f420abb8fdb5 (0 CR; 4e89788dc3a16b9c).
- flat_v2_outcome.txt blob:2e1407cb2d1dfd8a7073770b471f521019fe87cd (0 CR; 00fefa8fe9cd798c).
- Worktree mmlu_pro_dataset_cache_v2.db sha256 4f65414f7625a1e7... = main's copy (the stub-DB ruling holds). Worktree
  embeddings_cache.db afe21525... (≠ main 52229e1e...: the builds rewrote it; the embeddings table FLAT reads, and the identity
  reproduces on it). snapshots.db 9e5536e5..., WAL 0 bytes.
- No DB write by either readout: the worktree DB mtimes (10:06-10:30) all predate the FLAT --run / --analyze (10:53-10:56) and
  the G12 read (10:54). G12 opens no DB ("pool: none").

## Per-claim table (deciding claims)

| # | claim | result | reviewer's number vs claimed | sev |
|---|---|---|---|---|
| G1 | data object = R2 B0 MMLU_PRO_LB member | CONFIRMED | site CSV: 60 rows, 1 snapshot 20261001_094311 (= pointer B0/mmlu_pro_lb), reps 300 on 60/60, feasibility OK 60/60; depths d1 14, d2 22, d3 21, d4 2, d5 1 (= claimed) | - |
| G2 | hierarchical-BH set 0 of 60, N-1 FIRES | CONFIRMED | own k = round(q_site x 300), p = (k+1)/301; TOP m 14, its k sorted [97, 249, 292, 296, 300 x10]; BH at 0.05: 0 rejections (smallest TOP p 98/301 = 0.326 vs 0.05/14 = 0.00357); no child family is reached; G12_sites.csv k and hier_bh agree on 60/60 | - |
| G3 | support bar: TOP m 14 <= 15, 1/301 = 0.003322 <= 0.003571 | CONFIRMED | same digits; UNDETERMINED-by-support does not apply | - |
| G4 | per-site p95 count 1 of 60; Binomial(60, .05) mean 3.00, P(X >= 1) 0.954 | CONFIRMED | 1 by three routes (cert_site_p95 column; observed_sep > site_null_p95; q_site < 0.05): n00000126 "Emergent Concept #111", depth 3, sep 0.088304 > p95 0.082301; 1 - 0.95^60 = 0.954 | - |
| G5 | P3: set size 0 in [0, 3] HELD; N-1 fires Brier 0.4900; UNDET Brier 0.0225 | CONFIRMED (numbers); wording PARTLY | (1 - .30)^2 = 0.49; .15^2 = 0.0225. The outcome prints "P3 set size HELD" without the bracketed mark "known pre-read (disclosed)" (L22431) | LOW (W-G2) |
| G6 | B-A2: H 0.2912 > p95 0.0264, so the alternative wording does not apply | CONFIRMED | from the pinned gold outcome blob:ec65dd67 | - |
| G7 | R-c "site-null floor" NOT EVALUATED; R-a m = all sites | CONFIRMED | as bracketed; only feasibility and reps checked (60/60) | - |
| F1 | identity REPRODUCED: af_clean_s42 M1 0.727 [0.712, 0.741], M2 +12.785 | CONFIRMED | own re-run of the identity path on the scratch copies: `{'m1': '0.727 [0.712, 0.741]', 'm2': '+12.785'}` -> REPRODUCED | - |
| F2 | af_clean_s42 copy (FLAT-AN-1): 24 files, sha-equal | CONFIRMED | own sha256 over both trees: 24 / 24, `diff` 0 lines; dag_snapshots.jsonl sha256 1b9bd34d648ef29e = the registered pin (prog L20770, L21020); `git ls-files` of that dir = 0 (untracked in main, as stated). The ruling itself is NOT in the programme (`grep -c FLAT-AN-1` = 0) | LOW (C-F1) |
| F3 | data object: held-out 3,449 in 3,358 components; label set 7,066 TRAIN; fit 6,993 TRAIN | CONFIRMED | own counts: held-out 3,449 (3,449 distinct, 3,449 EVAL in the side export); kept 7,066 all TRAIN (dropped GATE 1,176, EVAL 78); fit 6,993 all TRAIN; held-out ∩ label set 0, held-out ∩ fit 0; census 74 leaves / 6,993 root fit ids on snapshot 20261001_094311; Kish Σm²/Σm 1.0707; gap to the registered 3,492 / 3,400 = 1.24%, within 5% | - |
| F4 | arm M1 table (T 0.7709, V0 0.7463, V1 0.7489, V2 0.7422, V3 0.7617, V4 0.7547, K0-K4 0.7553 / 0.7538 / 0.7501 / 0.7718 / 0.7530) | CONFIRMED | own assignment from the state partitions (nearest leaf mean for T and K; vMF MAP for V, with my own log C_d(κ) from scipy ive), own TRAIN-majority per cell: all 11 equal to 4 dp; tie cells 0 (K1: 1, not deciding) | - |
| F5 | D1 +0.0246 [+0.0125, +0.0369] > spread_V 0.0194: C1 HELD | CONFIRMED | D1 0.02464; spread_V(M1) = V3 - V2 = 0.01943; CI with the instrument's draw rule and seed [0.0125, 0.0369]; own seed [0.0119, 0.0371]. Both clauses hold. Discordant pairs T+ 275 / V0+ 190, exact McNemar p 0.00009 (n 3,449) | - |
| F6 | D2 -0.141e-3 [-0.788, +0.513]e-3, spread_V(M2) 0.551e-3: C2 FAILED | CONFIRMED (module spot check, not independent: M2 goes through F.loo_imp) | D2 -0.1408e-3, spread 0.5513e-3, CI [-0.788, +0.513]e-3; keyed 10,925; arm M2 T +14.090, V0 +14.230 as printed | - |
| F7 | L1 does not fire; F3 does not fire | CONFIRMED | L1 needs diff < -spread AND CI upper < 0: D1 > 0; D2 -0.141 > -0.551 and upper +0.513 > 0 | - |
| F8 | Support line: DEFF 0.975, n_eff 3,537, MDE80 0.0173, bar 0.0194 | PARTLY | own cluster-robust SE 0.00628 vs iid 0.00624: DEFF 1.014, n_eff 3,402, MDE80 0.0176. The printed DEFF is a bootstrap-SE ratio (0.00616 over iid) below 1, so its n_eff (3,537) is larger than n (3,449). The bar max(MDE, spread_V) is 0.0194 either way, and C1 does not move | LOW (W-F3) |
| F9 | P7 scoring: M1 band FAILED (+0.0246 above [-0.040, +0.010]); M2 band HELD; C1-FAILED prediction missed; C2, L1 as predicted | CONFIRMED | Briers (not printed; registrar's): C1 FAILED p .85, event no: 0.7225; C2 FAILED p .85, event yes: 0.0225; L1 fires p .30, event no: 0.0900 | - |

## How sensitive each verdict is (read-only, not code mutants)

| id | change | result | decisive? |
|---|---|---|---|
| S1 | G12 with a flat BH over all 60 sites | set still empty (min p 5/301 = 0.0166 > 0.05/60) | no; N-1 is robust |
| S2 | C1 against the TRANSPORTED spread_V 0.0305 instead of the measured 0.0194 | D1 0.0246 < 0.0305: C1 would FAIL | the registered statistic is the in-run spread (FLAT-MIX-MMLU's criterion "unchanged"); not a substitution, but C1 clears its point bar by 0.0052 (0.83 SE) |
| S3 | comparator = the best V seed (V3) or the best K seed (K3) instead of V0 | T - V3 +0.0093 < spread; T - K3 -0.0009 | the registered control is V0; the words must name it (W-F1) |

## Defects and conditions

- **W-G1 (words, G12).** "N-1 FIRES: on R2's B0 MMLU_PRO_LB member, the hierarchical-BH set at per-family q 0.05 (300 reps) is
  empty: none of the 14 depth-1 sites (the first data-driven split inside each declared-domain anchor) is certified." The
  per-site count (1 of 60, a depth-3 site) is below the Binomial(60, 0.05) mean of 3. Report it as descriptive and never call
  it a certified site. Descriptive context, not a verdict: the TOP sites' k runs from 97 to 300 (13 of 14 observed separations
  below their own null median). In cert_resolution_sites.csv each of the other anchored trees has a depth-1 site at k = 0
  (bareq512_s42, o0_clean_s42, frozen). One member, one draw: write no recipe-level claim.
- **W-G2 (LOW, P3 mark).** The registrar scores P3's set-size leg as "HELD (known pre-read, disclosed)" (L22431). The
  outcome file omits the mark; insert it in the record, not in the write-once file.
- **W-G3.** "CONSEQUENCE: F-TAX N-1 = FIRES" is the reader's line. F-TAX is scored by the registrar; this review does not
  score it.
- **W-F1 (words, FLAT C1).** "On B0's MMLU-Pro member at k = 74, the v2 anchored tree's leaves are purer on held-out EVAL than
  the flat vMF control of record V0 (M1 0.771 vs 0.746, D1 +2.46pp [+1.25, +3.69], beyond V's seed spread 1.94pp)." Never write
  "purer than flat clustering" or "beats flat mixtures": a spherical k-means seed (K3 0.7718) is level with T (0.7709); T
  clears the best V seed by only 0.93pp; the point clause clears its bar by 0.52pp (0.83 SE); and against the transported spread
  0.0305 it would fail (S2). C1 is on M1 only. M2 shows no gain (C2 FAILED; D2 interval covers 0), and descriptive M4 runs
  the other way (D4 -1.42 nats [-2.11, -0.73]). A FAILED C2 is never read as parity.
- **W-F2.** F3 does not fire (L1 did not fire). FLAT-MIX-MMLU's af_clean_s42 result (worse than V0) is NOT extended to the v2
  anchored tree, which measured the other way on M1. A non-fire of L1 is never read as parity (Support (f)). M2's keyed set
  covers both sides (as registered), so M2 is not a held-out measure.
- **W-F3 (LOW, support quote).** Quote the support as "DEFF 1.014 (cluster-robust, CK-CLOSE components; bootstrap ratio
  0.975), n_eff 3,402, MDE80 0.0176; bar max(MDE, spread_V) 0.0194". The printed n_eff 3,537 exceeds n. Fix at the next
  script edit: n_eff = n / max(DEFF, 1), or print the analytic DEFF beside the bootstrap one.
- **C-F1 (LOW, record).** The registrar records the FLAT-AN-1 ruling (who decided it, the 24-file copy, 24/24 sha-equal,
  the jsonl = pin 1b9bd34d648ef29e, nothing overwritten) and the stub-DB replacement (already in L22502ff) in the outcome
  section. f660c9db's crash (rc 1 before any T2 read, no outcome) is disclosed as a failed precondition, not an outcome. The
  same state (meta blob ef7bca33) served the --analyze.
- **D-PR-1 (LOW, naming).** G12_sites.csv's column `k` is the null exceedance count, while the site-null CSV's `k` is the child
  count (2 on all 60 rows). The outcome defines it ("k = the null exceedance count"); rename at the next edit (`k_exceed`).

## Commands

```
cp -p rp12-r2-run/{embeddings_cache,mmlu_pro_dataset_cache_v2,snapshots}.db <scratch>/db/ ; sha256sum originals copies main  # equal; mmlu = main 4f65414f
for f in g12_reader.py flat_v2.py cert_resolution.py <site csv> <G12 outcome/sites> <flat outcome>: git hash-object; git rev-parse HEAD:f; tr -cd '\r'|wc -c; tr -d '\r'|sha256sum
python g12chk.py          # own k, p, TOP BH, per-site counts (3 routes), binomial, cross-check with G12_sites.csv (0 mismatches)
TAXOARENA_DATA_ROOT=<scratch>/db python flatchk.py   # own data-object counts; own M1 for 11 arms from state/part_*.json;
                          # D1, spread_V, cluster bootstrap (instrument seed + own seed), analytic cluster SE/DEFF, McNemar; M2/D2 via module
TAXOARENA_DATA_ROOT=<scratch>/db python ident.py     # FV.identity_values() -> REPRODUCED (af_clean_s42 copied into scratch)
find af_clean_s42 -type f | sort | xargs sha256sum (main vs worktree): 24/24, diff 0 ; git ls-files af_clean_s42 | wc -l = 0
grep -c FLAT-AN-1 docs/judge_v2_program.md = 0 ; git show --stat 9c9ee9e7 (4 files) / 36f1310f (2 files), all under experiment_results/
python: cert_resolution_sites.csv depth-1 k per tree (context for W-G1)
```
