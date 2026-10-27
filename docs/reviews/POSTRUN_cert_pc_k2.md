# POSTRUN review: CERT-PC-K2 (arm + readout at 85fc338a, cert_pc_k2.py 38fb0dfc)

Reviewer: adversarial-reviewer, 2026-10-03. Prior review: READY_cert_pc_k2.md. Data root .claude/worktrees/rp12-r2-run at 85fc338a
(`git rev-parse`). The blobs were verified there with `git hash-object`: cert_pc_k2.py 38fb0dfc, cert_pc_size.py de39c648. Ops commit 346a6f7e
(logs experiment_results/cert_pc_k2/ops_20261003/, 10 files). The outputs are untracked and write-once:
outcome.txt sha256-lf16:f13983bbee708a52 (66 lines); pk2_sites.csv sha256-lf16:88926f502843dcea; arm/sites.csv sha256-lf16:5948f820a7ec92ec;
arm/replicates.csv sha256-lf16:19e72ad7f1af3485. The backup E:\TaxoArena_backup_2026-10-03_cert_pc_k2 passes `sha256sum -c` (8/8 OK), and all 8 files
`cmp` equal to the run copies. It includes emb_hashes_before/after.json, which closes CPS POSTRUN's LOW item. Zero calls. My only DB read was
rp12-r2-run/embeddings_cache.db opened `mode=ro&immutable=1` (-wal 0 bytes).

## Verdict

**VALID. PK1 (n 486) K2-NOT and PK2 (n 441) K2-NOT. All 3 anchors are NOT-CERTIFIED at both sizes: 0 of 5 certified, 0 NOT EVALUABLE.
k_d is 300 of 300 on all 30 subsamples (p_d 301/301 = 1). C0 is comparable on 30 of 30. IDENTITY reproduced (= PC1). F-PK FIRED as registered.**
Every deciding number reproduces to the digit from the arm's own outputs. All 31 declared statistics reproduce at 6 dp from an independent
numpy recompute on the cache. **This is a FAILED positive control, not a negative finding about the certificate (W-1, W-2).** The declared
split is real but weak geometry: it sits below its null MINIMUM on 30 of 30 subsamples. It is also weaker than G12's own data-driven splits of the same three anchors.

## Per-claim table (deciding claims)

| # | claim (outcome) | my number | status | sev |
|---|---|---|---|---|
| 1 | IDENTITY 0.107803, k_d 0, null p95 / max 0.041626 / 0.042414 = PC1, seed n00000001, n 6,993 | recount from replicates.csv: k 0, p95 0.041626, max 0.042414, reached 300; numpy 0.107803 | CONFIRMED | - |
| 2 | 30 declared statistics 0.013884-0.018984 | numpy (site file + cache, 512 floats, unit norm, the splitter's chanceCorrectedSeparation): 30/30 equal at 6 dp | CONFIRMED | - |
| 3 | k_d 300/300 everywhere -> NOT CERTIFIED 30/30 | #{SN >= d} = 300 on each site. Null p95 0.066679-0.071182; null MIN 0.042134-0.050251 > every declared value (30/30). Declared / null p95 = 0.20-0.28 | CONFIRMED | - |
| 4 | C0 comparable 30/30 | C0 p95 recount = the arm's c0_p95, 30/30 to the bit (0.000685-0.002330, all < null p95). Declared > C0 MAX on 30/30 (C0 max 0.001254-0.004791) | CONFIRMED | - |
| 5 | no DEGENERATE / INFEASIBLE | reached 300 of 300 on all 31 sites; n >= 441 > 110; group sizes = the registered allocations (230/256, 208/233, 191/295, 173/268, 331/155, 300/141) | CONFIRMED | - |
| 6 | anchor verdicts gate-first; PK1 / PK2 K2-NOT; F-PK FIRED | certified 0, not certified 5, NE 0 per anchor and size, so PK-6 (Q-K1) is NOT exercised and the registered rule applies literally: c = 0 -> K2-NOT | CONFIRMED | - |
| 7 | P1 Brier 0.6350; P2 0.2025 / 0.1600 / 0.1225; P3 HELD 0.0225 | 0.35^2 + 0.30^2 + 0.65^2 = 0.6350; 0.45^2, 0.40^2, 0.35^2; 0.15^2 | CONFIRMED | - |
| 8 | data object and instrument | status COMPLETE, arm certPcK2, snapshot 20261001_094311, reps 300, slice 512, sepBar 0.0145, dropTop 0, whiten false, mcs 55, c0Seed 20261002, threads 12. Site sha efcc4e99... = SITES_SHA256 = my READY rebuild. 91 arms = 1 + 30 x 3, reps 0..299 in order. emb hashes before == after | CONFIRMED | - |
| 9 | console = outcome; write-once | 65 of 66 outcome lines appear verbatim in 08_analyze.txt. The 66th (the registration line) differs only in the em dash's console encoding. The selftest printed 11/11 first. A second `--analyze` REFUSES ("outcome.txt exists: the outcome is write-once"); md5 over the sha256s of outcome, csv and arm/* is unchanged (8a53ab51...) | CONFIRMED | - |
| 10 | arm transcript | 30 `[PK2] site` lines; the IDENTITY line printed before any K2 site; BUILD SUCCESSFUL in 24m 42s (READY estimate 31 min) | CONFIRMED | - |

## C-4: re-derivation and Support after the run

Deflated arm (descriptive): k 300 on 30/30, defl_dims 1. Support: DEFF 1.0, re-measured as the structure of the object (independently seeded
replicates; nothing clustered in an exceedance count). n_eff = 300 per subsample. SE at the bar 0.0126; MDE80 0.0352. The observed p_d is 1.000 on
every subsample, 0.95 above the bar, so no verdict sits near the bar. With one subsample per anchor (economics is about one effective subsample,
C-5) the reading is the same, because all 30 sit at k 300. Full counts: certified 0 / not 30 / C0 0 / degenerate 0.

## C-5: dependence (carried from READY D-3)

economics n 486: the 5 draws share 468-470 of 486 items (about 1 effective subsample); math 283-302, physics 294-310. n 441 within n 486
at the same seed: 431-435 (economics), 380-387 (math), 400-408 (physics) of 441. **PK2 is a largely overlapping re-read of PK1, not a replication.**

## Descriptive beside (no new criterion; G12 site_null_B0_mmlu_pro_lb.csv of record, TOP rows)

| anchor | K2 declared (n 441-486) | K2 null p95 | G12 TOP split observed (n) | G12 own null p50 / p95 |
|---|---|---|---|---|
| math | 0.0139-0.0167 | 0.0668-0.0702 | 0.0398 (770) | 0.0502 / 0.0539 |
| physics | 0.0160-0.0190 | 0.0667-0.0680 | 0.0370 (765) | 0.0643 / 0.0677 |
| economics | 0.0142-0.0161 | 0.0684-0.0712 | 0.0363 (483) | 0.0587 / 0.0695 |

CPS's all-category subsamples at n 486 had null p95 0.054-0.057. Inside one category the bar is higher (0.067-0.071) at the same n: the population
effect that CPS W-2 (ii) caveated is real. The G12 anchors are routed regions, not the declared categories, so the columns are not like with like.

## What may be said (the registrar's wording; binds the record)

- **W-1 Scope (exact).** "On R2's B0 MMLU_PRO_LB member (draw 5a3e756 TRAIN; qwen3 512-slice; sepBar 0.0145; 300 reps), the declared 2-way
  source-family partition (MMLU-original vs added sources) inside math, physics and economics, subsampled to n 486 and n 441, is NOT
  certified on any of 30 subsamples (k_d 300 of 300 everywhere). Its statistic, 0.014-0.019, lies below the minimum of its own site null
  (0.042-0.050) and at 20-28% of the null p95 (0.067-0.071). C0 comparable 30/30." The words "the certificate is insensitive to 2-way
  structure" are NOT licensed.
- **W-2 (a) vs (b): the test cannot separate them, and the record must say so.** What it does show: (b) in its strong form ("not geometric
  at all") is refuted descriptively. The declared split exceeds every one of 300 random size-matched relabellings on 30/30 subsamples
  (3.5-11.5x the C0 maximum), so it is real but weak structure. (a) is NOT shown. A declared partition certifies only if its
  unoptimised statistic beats the splitter's OPTIMISED split of a structureless moment-matched cloud. This partition is far below even that
  null's minimum, so the outcome would be the same for a fully sensitive certificate. The control was too weak to test sensitivity.
  **k = 2 within-category sensitivity stays UNDETERMINED: not shown, not refuted.** The quantified bar is the one licensed statement: inside
  these categories at n 441-486, a 2-way declared split must reach about 0.067-0.071 to certify.
- **W-3 CPS's W-2 ("0 of 60 not explained by n alone").** It stands as worded. It was always conditional on structure of declared-14-way
  strength, and this test neither weakens nor extends it. F-PK's registered sentence may be recorded verbatim, read with "possibly" and with
  "narrows to 14-way structure" as a SCOPE statement: the certificate's sensitivity is demonstrated for 14-way declared structure only.
  It must not be read as evidence of a k = 2 sensitivity limit. Bracket the F-PK sentence: "F-PK fired on a declared split weaker than
  its null's minimum; this does not discriminate a sensitivity limit from weak structure (POSTRUN_cert_pc_k2 W-2)."
- **W-4 G12's 0 of 60.** Unchanged: F-TAX N-1 and F2 stand. The K2-CERTIFIABLE reading ("the tree's depth-1 splits are less separated than a
  declared source-family split") is NOT available. Descriptively the order is the reverse: G12's TOP splits of math / physics / economics
  (0.037-0.040) are about twice as separated as the source-family split (0.014-0.019), and they too stay below their own null p95
  (populations differ: routed anchor vs declared category). Nothing here says whether any certifiable 2-way structure exists inside an anchor.
- **W-5 Predictions.** P1 outcome K2-NOT (prior 0.35), 3-way Brier 0.6350. P2 all three events no: physics 0.2025, economics 0.1600,
  math 0.1225. P3 HELD (Brier 0.0225).
- **W-6 Disclosures.** PK-6 / Q-K1 not exercised (0 NE anchors). READY D-1 (chemistry also met the eligibility rule) stays a registrar
  bracket; it does not affect this outcome. D-2 (twin guard untested) was not exercised: the site sha equals the pin.

## Defects

None affects validity. READY D-1 (registration text) and D-2 (LOW) are carried. D-3 is now C-5's wording. Suggested follow-up for the research
lead (zero calls, its own registration): a k = 2 control of KNOWN strength at n 486 inside one category's moment-matched cloud (planted
separation at graded strengths around 0.07), or a cross-category declared 2-way split. Either would measure k = 2 sensitivity, which this test could not.

## Commands (compact)

```
git -C rp12-r2-run rev-parse --short HEAD (85fc338a); git hash-object cert_pc_k2.py cert_pc_size.py (38fb0dfc, de39c648)
python scratchpad/pr_k2.py   # shas; hashes equal; 91 arms x 0..299; numpy declared 31/31 at 6 dp; k / p95 / max / min / reached / C0 p95 /
                             # C0 max / deflated k recount per site; ranges; CPS n486 null p95 0.0544-0.0567
grep -F -x -c -f outcome.txt <(tr -d '\r' < ops_20261003/08_analyze.txt)   # 65 of 66; the remaining line = em-dash encoding
python tools/analysis/cert_pc_k2.py --analyze (rp12-r2-run)   # REFUSED write-once; md5 of sha256s 8a53ab51... before == after
cd E:/TaxoArena_backup_2026-10-03_cert_pc_k2 && sha256sum -c SHA256SUMS.txt (8 OK); cmp backup vs run copies (8 equal)
python (csv) G12 site_null_B0_mmlu_pro_lb.csv TOP rows: observed_sep, site_null_p50 / p95 for math, physics, economics
```
