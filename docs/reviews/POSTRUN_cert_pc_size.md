# POSTRUN review: CERT-PC-SIZE (arm + readout at 88bbf560, cert_pc_size.py de39c648)

Reviewer: adversarial-reviewer, 2026-10-02. Prior review: READY_cert_pc_size.md (fc1d1fe5). Data root .claude/worktrees/rp12-r2-run,
detached at 88bbf560; the readout blob de39c648 was verified there with `git hash-object`. Ops commit 11752248 (log
experiment_results/cert_pc_size/ops_20261003/). Outcome files are untracked and write-once: outcome.txt sha256-lf16:6f01fbb56eb0b486
(40 lines) and pcs_sites.csv sha256-lf16:7e5fb38e8cc2e989. The backup E:\TaxoArena_backup_2026-10-03_cert_pc_size passes
`sha256sum -c` (6/6 OK). Zero calls. My only DB read: embeddings_cache.db opened `mode=ro&immutable=1`.

## Verdict

**VALID. PS1 (n 486) CERTIFIED-AT-SIZE, 5 of 5 subsamples. PS2 (n 441) CERTIFIED-AT-SIZE, 5 of 5. n 264 (descriptive) 5 of 5.
k_d 0 of 300 on all 15 subsamples (p_d 1/301). C0 comparable on 15 of 15. IDENTITY reproduced. F-PS NOT FIRED.**
Every deciding number reproduces to the digit from the arm's own outputs. All 16 declared statistics also reproduce from an
independent numpy recompute on the cache. The wording conditions W-1..W-4 below bind the registrar's record.

## Per-claim table (deciding claims)

| # | claim (outcome) | my number | status | sev |
|---|---|---|---|---|
| 1 | IDENTITY: declared 0.107803, k_d 0; null p95 / max 0.041626 / 0.042414 = PC1 (READY C-3) | recount from replicates.csv: k 0, p95 0.041626, max 0.042414, reached 300; numpy 0.107803 | CONFIRMED | - |
| 2 | 15 subsample declared statistics (0.103843-0.118311) | numpy (site file + cache, 512-slice, unit norm, the splitter's chanceCorrectedSeparation): 15 of 15 equal at 6 dp | CONFIRMED | - |
| 3 | k_d 0 of 300 on every subsample -> CERTIFIED 15/15 | #{SN >= d} = 0 for each of the 15; null max 0.053578-0.062095; margin d - max 0.0432 (PS_n441_d3) to 0.0587 | CONFIRMED | - |
| 4 | C0 comparable 15/15 (C0 p95 0.002205-0.004715 vs null p95 0.048377-0.056704) | recount = the arm's c0_p95, 15/15 to the bit; seeds = cpcSeed(20261002, name, 0), 15/15 (Java hashCode recomputed). Independent numpy check on PS_n486_d1: 300 uniform relabellings give p95 0.002838 and max 0.004713 (the arm gives 0.002562) | CONFIRMED | - |
| 5 | DEGENERATE / INFEASIBLE: none | reached 300 of 300 on all 16 sites; n >= 264 > 110 | CONFIRMED | - |
| 6 | PS1 / PS2 gate-first verdicts | certified 5, not certified 0, NOT EVALUABLE 0 (C0 0, degenerate 0) at both sizes: the gate is not exercised; 5 >= 4 | CONFIRMED | - |
| 7 | P1 Brier 0.3050; P2 0.2500; P3 HELD (0.108987; 0.055332); P4 0.0225 | (0.45)^2 + 0.20^2 + 0.25^2 = 0.3050; 0.25; medians of the 5 n-486 values: 0.108987 and 0.055332, both inside their intervals; (0.15)^2 = 0.0225 | CONFIRMED | - |
| 8 | data object and instrument | status COMPLETE, snapshot 20261001_094311, reps 300, slice 512, sepBar 0.0145, dropTop 0, whiten false, mcs 55, c0Seed 20261002, threads 12; site sha 231db2e0e119... = the READY pin (C-2 MET, so D-1's gap was not exercised); 46 arms = 1 + 15 x 3, all reps 0..299 in order; emb hashes before == after (`diff` empty) | CONFIRMED | - |
| 9 | console = outcome; write-once | 39 of 40 outcome lines appear verbatim in 08_analyze.txt. The 40th (the registration line) differs only by the em dash's console encoding. The selftest printed 11/11 before the readout. A second `--analyze` REFUSES "outcome.txt exists: the outcome is write-once"; the shas of outcome, csv and arm/* are unchanged | CONFIRMED | - |
| 10 | arm transcript = sites.csv | every 07_arm_transcript.txt [PCS] site line (declared, k, p95, reached, deflated k, C0 p95, seed) matches sites.csv / my recount | CONFIRMED | - |

## C-4: the re-derivation, Support after the run

Deflated arm (descriptive): k 0 on 15/15, with p95 0.022827-0.032248, and dims 13 on 15/15.
Support: DEFF 1.0, re-measured as the structure of the object. Each site's 300 replicates are independently seeded, and nothing in an
exceedance count is clustered. n_eff = 300 per subsample and 5 subsamples per size. The SE at the bar is 0.0126 and the MDE80 0.0352.
The observed p_d is 0.0033 on every deciding subsample, 0.0467 below the bar and past the MDE. The deciding count is 5 of 5 against a threshold of 4.
The bar is not near binding: each declared statistic exceeds its null MAXIMUM by at least 0.043.
D-3 of the READY is RETRACTED: the arm took 926 s, well under the 24-min bound (CPC's 34 min included its I-1 / anchor arms).

## D-5: overlap of same-seed draws across sizes (as the READY required)

| draw | PS_n441 within PS_n486 (of 441) | PS_n264 within PS_n441 | PS_n264 within PS_n486 |
|---|---|---|---|
| d1 | 233 | 37 | 37 |
| d2 | 207 | 39 | 41 |
| d3 | 251 | 52 | 47 |
| d4 | 260 | 44 | 34 |
| d5 | 224 | 43 | 42 |

Chance would give 30.6 (441 x 486 / 6,993) and 16.6 (264 x 441 / 6,993). PS2 shares 47-59% of its items with PS1 at the same draw.
**PS2 is therefore a partly overlapping re-read of PS1, not an independent replication.** The record must say so.

## What may be said about G12's 0 of 60 (G12 site_null_B0_mmlu_pro_lb.csv of record; descriptive beside, no new criterion)

- G12's 14 TOP (depth-1) sites: k = 2 each, n 264-778. Observed separation 0.0175-0.0757 (median 0.0359), against their own site-null
  p95 of 0.0414-0.0972 (median 0.0680). **13 of 14 sit below their own null MEDIAN** (history only: 0.0562 vs p50 0.0501).
- The PS subsamples: null p95 0.048-0.057 at n 264-486, the same order as G12's within-anchor bars. The declared 14-way statistic is 0.104-0.118.
- The k mismatch runs AGAINST certification here, so it cannot have inflated the result. The null is the splitter's optimised split
  of a moment-matched cloud, and C0 shows unoptimised 14-way relabellings score about 0.003. The bar the declared partition cleared
  is the same splitter-optimised bar a G12 split must clear.

## Wording conditions for the registrar (bind the record)

- **W-1 Scope (exact).** "On R2's B0 MMLU_PRO_LB member root (draw 5a3e756 TRAIN; qwen3 512-slice; sepBar 0.0145; 300 reps), the
  declared 14-category MMLU-Pro partition, stratified-subsampled to G12's depth-1 site sizes, is CERTIFIED by its own site null at
  n 486 (PS1, 5 of 5 subsamples) and n 441 (PS2, 5 of 5), and descriptively at n 264 (5 of 5); k_d 0 of 300 everywhere (p 1/301);
  C0 comparable 15 of 15." PS2 is not an independent replicate of PS1 (D-5: 47-59% shared items). Never write "the certificate is
  validated at depth 1" or "the certificate certifies tree sites".
- **W-2 G12 / N-1 (the reading this test buys).** "The site-null certificate is not size-limited at G12's depth-1 sizes for
  structure of the declared 14-category strength: its bar there (null p95 about 0.05-0.06) is cleared with margin. G12's 0 of 60
  is therefore NOT explained by n alone. The tree's data-driven depth-1 splits are less separated than the declared level at the
  same n, and 13 of G12's 14 TOP splits fall below their own null median." The caveats are mandatory and go beside the reading.
  (i) NOT k-matched: 14 groups vs 2. (ii) NOT population-matched: all categories vs within one anchor. CERT-POSITIVE-CONTROL's PC3,
  descriptive, found 0 of 14 declared src partitions certified inside anchors, with src geometry unknown. (iii) Nothing is shown
  about whether certifiable 2-way structure EXISTS inside an anchor, nor about the certificate's power for it there. F-TAX N-1 and
  F2 stand. The W-2 sentence of CERT-POSITIVE-CONTROL ("nothing shown at depth-1 sizes") is superseded by insertion for the
  size question only.
- **W-3 Predictions.** P1 outcome CERTIFIED-AT-SIZE (prior 0.55), 3-way Brier 0.3050. P2 HELD (Brier 0.2500). P3 HELD on both
  medians (0.108987 in [0.09, 0.14]; 0.055332 in [0.05, 0.10]). P4 event yes (Brier 0.0225).
- **W-4 Guard disclosure.** D-1 (the readout does not bind the site file to the draw) was not exercised: the site sha equals the
  READY pin. The fix stays owed before any reuse of cert_pc_size.py.

## Defects

None affects validity. Carried: D-1 (MEDIUM, guard gap, not exercised), D-2 (LOW, now met by printing: equal), D-4 (LOW, -O).
D-3 retracted. One new LOW item: the E: backup holds no emb_hashes_before/after.json (445 B each), and ops_log.txt holds only the
"after" hash text. Copy both JSONs to the backup and add them to SHA256SUMS.txt.

## Commands (compact)

```
git -C rp12-r2-run rev-parse --short HEAD (88bbf560); git hash-object tools/analysis/cert_pc_size.py (de39c648)
python scratchpad/pr_pcs.py   # immutable ro cache: 6,993 vectors; 16 declared stats (numpy) = sites.csv; k / p95 / max / reached /
                              # C0 p95 / deflated k recount from replicates.csv (46 arms x 300 in order); numpy C0 on PS_n486_d1; D-5 overlaps
python (Java String.hashCode) c0_seed check 15/15
grep -F -x -c -f outcome.txt ops_20261003/08_analyze.txt (39 of 40); grep -v -F -x -f ... (1: the em-dash line)
python tools/analysis/cert_pc_size.py --analyze   # REFUSED write-once; md5 of sha256s (outcome, csv, arm/*) unchanged
diff emb_hashes_before.json emb_hashes_after.json (empty); cd E:/TaxoArena_backup_2026-10-03_cert_pc_size && sha256sum -c (6 OK)
python (csv) G12 site_null_B0_mmlu_pro_lb.csv depth 1: 14 rows, k 2, observed vs site_null_p50 / p95
```
