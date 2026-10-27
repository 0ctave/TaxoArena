# POSTRUN review: CERT-POSITIVE-CONTROL (arm b5653fb7, readout e0751d7c)

Reviewer: adversarial-reviewer, 2026-10-03. Prior reviews: READY_cert_positive_control.md (b5653fb7) and
READY_cert_positive_control_delta.md (416ac436). Data root .claude/worktrees/rp12-r2-run, detached at 416ac436; readout blob
e0751d7c verified (`git hash-object`). Ops log experiment_results/cert_positive_control/ops_20261003/ (c7cf3116, d7f34193, 1597e801).
Outcome files (untracked, write-once): outcome.txt sha256-lf16:1decf875908a1559 (39 lines); cpc_sites.csv sha256-lf16:0117d37542b10657.
Zero calls. My only DB read: embeddings_cache.db opened `mode=ro&immutable=1` (-wal 0 bytes before and after; -shm unchanged).

## Verdict

**VALID. PC1 CERTIFIED (k_d 0 of 300, p_d 1/301 = 0.003322); C0 comparable; F-PC FIRED.** PC3 0 of 14 (DESCRIPTIVE-ONLY).
P1 FAILED (point and interval; 3-way Brier 1.4978), P2 HELD (event yes, Brier 0.0100), P3 HELD (0 of 14). Every deciding number
reproduces to the digit from the arm's own outputs, and the declared statistic also reproduces from an independent numpy
recompute on the cache. Wording conditions W-1..W-4 below bind the registrar's record.

## Per-claim table (deciding claims)

| # | claim (outcome) | my number | status | sev |
|---|---|---|---|---|
| 1 | declared root statistic 0.107803 (14 groups, n 6,993) | arm sites.csv 0.10780301021353667; **independent numpy** (labels file + cache, 512-slice, unit-norm, the splitter's formula) 0.107803010214; group sizes 238..809, sum 6,993 | CONFIRMED | - |
| 2 | null p05 / p50 / p95 / max 0.039256 / 0.040510 / 0.041626 / 0.042414; reached 300 of 300 | recount from replicates.csv (root SN, reps 0..299 in order): 0.0392556 / 0.0405101 / 0.0416257 / 0.0424137; 300 of 300 > 0 | CONFIRMED | - |
| 3 | PC1: k_d 0, p_d 1/301, CERTIFIED | k_d = #{SN >= 0.107803} = 0; p = 1/301; margin d - max = 0.06539, d / max = 2.54 | CONFIRMED | - |
| 4 | C0 p95 0.000604 < null p95 0.041626 (comparable); P2 event yes (< null p05 0.039256) | recount 0.000604271 (C0 max 0.000931); comparable; P2 yes. Independent check of the C0 law: 300 numpy uniform relabellings give p95 0.000567, max 0.001243, mean 0.000013 (same order; C0 is 69x below the null p95) | CONFIRMED | - |
| 5 | C0 precedence | comparable, so not exercised; code path re-confirmed in the READY (M5 KILLED) | n/a | - |
| 6 | deflated root (descriptive): k 0, p95 0.010493 | recount k 0, p95 0.0104934, max 0.0107842 | CONFIRMED | - |
| 7 | PC3: 14 of 14 scored, BH (m 14, q 0.05) 0 certified | each anchor's k recounted from its SN replicates = sites.csv (14/14); smallest p 296/301 (history); BH set empty | CONFIRMED | - |
| 8 | I-1 live 60/60 bit for bit; I-2 PASS (3 registered + 11 beside) | identity.csv: 60 live rows, 60 accepted, 60 true; I2 14 of 14 | CONFIRMED | - |
| 9 | console = outcome; write-once | all 39 outcome lines occur verbatim in the console log (grep -F -x: 39 of 39; outcome lines missing from the log: 0); the log shows the selftest 21/21 before the readout. A second `--analyze` REFUSES "outcome.txt exists: the outcome is write-once"; shas unchanged afterwards | CONFIRMED | - |
| 10 | Support after the run | DEFF 1.0 (independent seeded replicates; nothing clustered in an exceedance count), n_eff 300, SE at the bar 0.0126, MDE80 0.0352; observed p 0.0033 lies 0.0467 below the bar, past the MDE; k_d 0 against a CERTIFIED threshold of <= 14 | CONFIRMED | - |
| 11 | instrument and data object | status.txt: COMPLETE, snapshot 20261001_094311, reps 300, sliceDim 512, sepBar 0.0145, dropTop 0, whiten false, mcs 55, c0Seed 20261002, threads 12, i1Form live under L23470; labels sha256 c0a20662... = the dry-run's; emb per-table hashes before == after | CONFIRMED | - |

## C-4 (the two counts)

- (a) K11 sort by execution: 60 accepted live sites, **36 of them at k >= 3 (k=3: 21, k=4: 15), all 36 bit for bit**. MET.
- (b) Root plain null beside G12's root row: **NOT APPLICABLE**. G12's site_null_B0_mmlu_pro_lb.csv has 60 sites at depths 1-5
  (14 / 22 / 21 / 2 / 1) and no depth-0 row. The member root's persisted dasguptaDeltaNorm is 0.0, because in this anchored tree the
  root -> 14-anchor level is declared, not a splitter split. I-2's 14 of 14 anchor matches are the cross-check against G12.

## Wording conditions for the registrar (bind the record)

- **W-1 Scope (exact).** "At the root of R2's B0 MMLU_PRO_LB member (one site; 6,993 TRAIN items of draw 5a3e756; the 14 declared
  MMLU-Pro categories as the partition; qwen3 512-slice; sepBar 0.0145; 300 reps), the site-null certificate CERTIFIES the declared
  partition: statistic 0.1078 against a null maximum of 0.0424, k_d 0 of 300, p 1/301." Never "the certificate is validated",
  "the categories are geometric clusters" (H 0.31 = partial recovery) or "the tree's root split is certified": the root -> anchor level
  is declared (persisted 0.0), the PC1 partition is the LABEL partition, and the anchors' routed regions differ from it (e.g. the
  math anchor holds 770 items, the math category 809).
- **W-2 What is overturned, and where.** The registered working reading (prog L23464ff: "G12's 0 of 60 is a sensitivity limit of the
  certificate") is overturned **at root scale (n about 7,000) only**: the instrument can certify strong declared structure there.
  At depth-1 scale (G12's TOP sites, n 264-778) nothing is shown either way. The reading of N-1's empty set becomes "no data-driven
  depth-1 split certified, with the n caveat", not "the instrument cannot certify". If the record also carries a reading of the
  certificate as a "false-discovery guard", say only that it is now shown CAPABLE of certifying at one root-size site; its
  sensitivity at depth-1 sizes is untested. F-TAX N-1 FIRES and F2 stand. Nothing reinstates F-TAX's certificate clause.
- **W-3 SEEN disclosure (verbatim beside PC1).** "The declared root statistic (0.1078) was computed once by the builder before the
  null was drawn; no null replicate was seen. Seeds (20260908 / 88820260908 / C0 20261002), instrument and criteria were fixed
  before that." Seeing the statistic left no free parameter to tune; the deciding count depends only on the pre-fixed null.
- **W-4 Predictions.** P1 FAILED: prior 0.85 on NOT CERTIFIED, interval [0.05, 1.00] missed (p 0.0033); Brier 1.4978. This is the
  registrar's own prior failing and is recorded as such. P2 HELD (Brier 0.0100). P3 HELD (0 of 14; PC3 is never a power
  statement: src geometry unknown, and every src statistic sits at or below its anchor's null).

## Defects

None that affect validity. Carried LOW: R4 and R8 (Kotlin-vs-Python recount cross-checks with no test) and K10 (disclosed survivor).
The sidecars are as at launch (-wal 0 bytes; -shm 32,768 bytes, R-1 of the READY).

## Commands (compact)

```
git -C rp12-r2-run rev-parse --short HEAD (416ac436); git hash-object tools/analysis/cert_positive_control.py (e0751d7c)
python (csv) recount: replicates.csv 31 arms x 300 in order; root SN/SND/C0 quantiles (Kotlin rank ceil(q n)); k_d; PC3 k x14 + BH
python scratchpad/cpc_root.py      # immutable ro: 6,993 vectors, 14 groups, declared 0.107803010214; numpy relabel 50 draws
python scratchpad/cpc_root300.py   # 300 numpy relabels: p95 0.000567, max 0.001243
grep -F -x -c -f outcome.txt cpc_analyze.log (39); grep -v -F -x -f cpc_analyze.log outcome.txt | wc -l (0)
python tools/analysis/cert_positive_control.py --analyze --data-root ../..   # REFUSED write-once; sha256 unchanged
python (csv) G12 site_null CSV: 60 rows, depths {1:14, 2:22, 3:21, 4:2, 5:1}, no n00000001
```
