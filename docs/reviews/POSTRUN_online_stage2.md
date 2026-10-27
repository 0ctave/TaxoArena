# POST-RUN review: ONLINE-STAGE2 (--run, main, blob 6bbc40dd)

Reviewer: adversarial-reviewer, 2026-10-03. Zero calls. The run was made from main after the brackets 08fe2870 (committed 20:04:08;
outcome written 20:11:07; launched with no java running). `git hash-object tools/analysis/online_stage2.py` on main =
**6bbc40dde71447f0d8844c222ea019223b3c56ff**, which is the READY blob. Outputs: `experiment_results/online_stage2/outcome.txt`
(86 lines, sha256 19e8a87a…87ff) and `online_stage2_items.csv` (36,947 lines = header + 2 x 18,473 streamed, sha256 4ddd6587…e4f5);
both untracked (`git ls-files` = 0). Console: scratchpad os2_run.log (87 lines).
**Backup (K-1 style, done by me):** `E:/TaxoArena_backup_2026-10-03_online_stage2/` holds outcome.txt, online_stage2_items.csv and
os2_run.log. SHA256SUMS.txt was written and `sha256sum -c` passes on all 3; the hashes equal the WROTE line.

## Verdict: VALID

Every deciding number reproduces to the printed digit, both from the items CSV and from my own stream re-implemented on the raw
inputs. My re-implementation covers my own calibration, frozen cells, prequential filing, rebuild every 100 and OL-R5 naming.
The outcome was written once.
**OS1 DIFFERENT (LOSS); OS2 UNDER-CATCH; F-OS FIRES; P1 HELD, P2 HELD (band edge), P3 FAILED, P4 FAILED; stage-1 identity
reproduced; INTEGRITY 0 everywhere (by construction).**

## Per-claim table

| claim (outcome) | mine | status |
|---|---|---|
| stage-1 identity -0.0386 / -0.0687; INTEGRITY churn 0 in 12 replay-arms | printed before any stage-2 statistic. Churn 0 holds by construction (frozen arrays) | CONFIRMED |
| OS1 D -0.0326 (online 0.6939 - batch 0.7265); SE 0.00614; 90% [-0.0427, -0.0225]; 95% [-0.0446, -0.0205]; DIFFERENT (LOSS) | own stream: **D -0.0326**; CSV -0.0326. My bootstrap (own RNG, B 4,000): SE 0.00638, DEFF 1.164, 95% [-0.0451, -0.0201]. The verdict is robust: \|D\| > 0.020 and the upper end is below 0 on both streams | CONFIRMED (SE gap 2.4e-4, from the stream) |
| per-member D_m tree +0.0115 / -0.0873 / -0.1128 / -0.1223 / 0.0000 / -0.1111 (MMLU_PRO_LB, BBH, MATH, MUSR, IFEVAL, GPQA) | own stream, identical (the outcome's per-replay lines carry the same in `fs(p["d"])`) | CONFIRMED |
| OS2 tree catch 0.5387 / 0.5630 / 0.3422 / 1.0000 / 0.9261 / 0.5355; median 0.5508 < 0.70; UNDER-CATCH | own stream and CSV: identical; median = (0.5387 + 0.5630) / 2 = 0.5508. **The coordinator's list (0.50 / 0.51 / 0.32 / 1.00 / 0.97 / 0.46) is the k-means arm's (median 0.5043)** | CONFIRMED |
| tau_m (12) | equal to the dry-run and to my brute-force calibration (READY_online_stage2) | CONFIRMED |
| F-OS FIRES (OS1 LOSS) | follows | CONFIRMED |
| P1 -0.0326 in [-0.035, +0.005] HELD; P2 0.5508 in [0.55, 0.88] HELD (0.0008 from the edge); CALIBRATED 0.60 Brier 0.7200; P3 false-buffer median 0.1030 outside [0.15, 0.50] FAILED; P4 k-means -0.0686 outside [-0.045, +0.005] FAILED | own: false-buffer median 0.1030 (tree), 0.0840 (k-means); k-means D -0.0686 | CONFIRMED |
| k-means arm D -0.0686 [-0.0819, -0.0553]; tree minus k-means +0.0360 [+0.0211, +0.0514]; end-of-stream D tree -0.0528 / k-means -0.0741 | own -0.0686; CSV eos -0.0528 / -0.0741 | CONFIRMED (descriptive) |
| written once; console = outcome | Both files have mtime 20:11:07 (mode "x"). One `===` block. All 86 outcome lines appear in the console in the same order; the 1 console-only line is WROTE (sha256 19e8a87a… / 4ddd6587…). 0 Traceback / REFUSED | CONFIRMED |

**Support, re-measured.** OS1 DEFF 1.080 (mine 1.164) vs 1.263 registered. n_eff 5,686. SE 0.00614 vs 0.00641. MDE80 0.0172.
DIFFERENT reach 0.0252 < \|D\| 0.0326. OS2 is decided by the point: distance 0.149 from the bar, far beyond any per-member SE
(<= 0.0225, GPQA). Not applicable: wrong-direction / McNemar counts (no judge verdict).

## Wording the registrar must use

- **W-1 (OS1 / F-OS).** "Even with frozen leaf means, a GATE-calibrated OOS buffer and buffer rebuilds every 100 items,
  prequential online filing of a left-out member falls **3.3pp below a batch rebuild: OS1 DIFFERENT (LOSS), D -0.0326, 95%
  [-0.0446, -0.0205]** (6,139 / 5,628, 6 replays, one draw); **F-OS FIRES**: memo v3's online-evolution design is not
  filing-neutral; the online claim narrows to 'stable ids at a filing cost; rebuild periodically'."
- **W-2 (stage 1 vs stage 2; DESCRIPTIVE).** "3.3pp vs stage 1's 3.9pp (+0.006)". It must carry: no interval; two changes at
  once (frozen means and threshold), so nothing is attributed to either. Never write "freezing reduced the loss". On the k-means
  arm the change is +0.0002.
- **W-3 (ids).** "Existing cells' ids are stable **by construction** (means frozen; integrity 0 in 12 replay-arms)". This is a
  design property, not a measured effect. Never write "stage 2 showed ids stay stable". Buffer-cell ids are NOT stable
  (registered).
- **W-4 (OS2).** "The GATE-calibrated trigger does not transport to new domains at the target rate: **OS2 UNDER-CATCH, median
  catch 0.55** against a 0.80 target and a 0.70 bar (tree: MMLU_PRO_LB 0.54, BBH 0.56, MATH 0.34, MUSR 1.00, IFEVAL 0.93, GPQA
  0.54; k-means median 0.50)". It must carry: the shortfall was expected below target before data (Support (g): four-member
  calibration vs five-member stream). Six sources, no sampling SE for the median. The cost side, false buffering of the
  in-members' own EVAL, has median 0.103 (P3 FAILED low).
- **W-5 (the loss is not only a catch problem; descriptive).** MUSR was caught completely (1.00) and still lost 12.2pp at
  arrival. MATH (catch 0.34) lost 11.3pp. MMLU_PRO_LB gained 1.2pp. The prequential buffer clustering at k = L_m (an oracle k
  favouring the online arm) does not recover the batch filing even when every item is buffered.
- **W-6 (transduction).** "Filing is prequential (each item is filed before it can enter the buffer); earlier EVAL items shape
  later buffer cells; the end-of-stream fully transductive filing is worse (D -0.0528), descriptive."
- **W-7 (tree vs k-means).** The k-means arm lost 6.9pp; tree minus k-means is +3.6pp [+2.1, +5.1], DESCRIPTIVE only
  (WILL-NOT-SHOW: tree-over-k-means superiority).

## Conditions / notes

- None blocking. The stage-1 backup exists as `E:/TaxoArena_backup_2026-10-03_online_replay/` (the name differs from the one
  in POSTRUN_online_replay_lomo K-1; the registrar should cite the actual path).

## Commands

```
git hash-object tools/analysis/online_stage2.py      # 6bbc40dd (main); git log -1 --format=%cI 08fe2870 -> 20:04:08
sha256sum / wc -l / ls -l --time-style=full-iso experiment_results/online_stage2/*   (both 20:11:07)
python (console vs outcome): 86/86 in order; 1 log-only WROTE line; 0 Traceback/REFUSED
python $TEMP/orl/s2_post.py   # CSV: D -0.0326 / -0.0686, catches, medians 0.5508 / 0.5043; own stream from raw: all D_m, catches, tau, false-buf equal
mkdir E:/TaxoArena_backup_2026-10-03_online_stage2; cp -p (3 files); sha256sum > SHA256SUMS.txt; sha256sum -c -> 3 OK
```
