# POSTRUN ADAPTIVE-PROFILE run 2 (declared deviation D-2026-10-09-1), 2026-10-09

Verdict: **VALID**. AP1 GRANULARITY-PAYS reproduces to the digit from an independent fit: point, both 95% bounds, the bootstrap SD,
d* and the certified-node count. One reading condition (C-1) and two LOW notes.

Object: `experiment_results/archv2/adaptive_profile/outcome.txt` sha256 fc715e4d... (174 lines; backup
E:/TaxoArena_backup_20261009_adaptive_profile, `sha256sum -c` all OK). Script blob:f23193bb on HEAD 9f5fb487 equals the merge cf35c3e2
and the READY delta4 blob (`git rev-parse HEAD:` = `git hash-object` working tree). Zero calls.

## Per-claim table (deciding claims)

| # | claim (outcome) | mine (independent) | verdict | sev |
|---|---|---|---|---|
| 1 | Data object: EVAL 5907 / 5404 components; TRAIN 11841; GATE 1944; 18 models; R1 drops 0 among scored | Captured from the pinned read path (marker and outputs redirected to scratch): T/G/E 11841 / 1944 / 5907, components 5404, keep-dropped 0, 18 models. Correctness matrix equals WIN-MAP's separately read export on all 5907 x 18 EVAL and 11841 x 18 TRAIN cells (0 differ) | CONFIRMED | - |
| 2 | theta (global, TRAIN) and tau_l^2 by depth | Own LOMO MAP Rasch (joint L-BFGS, then a block-Newton polish to grad < 1e-10), own brentq theta: all 18 theta equal to 3 dp; tau^2 d1..d8 0.36042 / 0.06856 / 0.04283 / 0.02405 / 0.01569 / 0.03123 / 0.0379 / 0.0 (equal) | CONFIRMED | - |
| 3 | Certified (model, node) pairs 260 of 4104 | Own BH per sibling family (single member strictly \|z\| > 1.96): 260 of 4104. Export CSV: 260 rows `certified=1` of 4104 | CONFIRMED | - |
| 4 | Brier A 0.147595, C 0.148555, D_7 0.145645; share below the benchmark level 0.5485; d* = 7 | 0.147595 / 0.148555 / 0.145645; 0.5485; d* 7 (GATE argmin) | CONFIRMED | - |
| 5 | **AP1 D_C +0.000961 [+0.000784, +0.001137], SD 0.000090 -> GRANULARITY-PAYS** | +0.000961 [+0.000784, +0.001137], SD 0.000090 (component bootstrap, default_rng(20261008), seed draw consumed as registered). Independent stream (seed 7): [+0.000783, +0.001125], SD 0.000088. Rule: LB95 > 0 AND point >= 0.0005 (prog L25133ff) -> HELD | CONFIRMED | - |
| 6 | F-AP NOT FIRED | requires UB95 < 0; UB95 +0.001137 | CONFIRMED | - |
| 7 | AP2 D_d* -0.001950 -> FIXED-BETTER (sign words DESCRIPTIVE-ONLY) | -0.001950 (point). Registered FIXED-BETTER iff UB95 < 0 | CONFIRMED (point) | - |
| 8 | AP3 / AP4 KMEANS-BETTER (-0.000842 / -0.002587) | spot check only: own arithmetic from the printed arm means 0.146753 - 0.147595 = -0.000842; 0.145008 - 0.147595 = -0.002587 | spot check | - |
| 9 | Support measured: Kish 1.3115, SE 0.000090, DEFF 0.955, n_eff 6184 | Kish 1.31149. The i.i.d. item SE of D_C is 9.03e-5, so DEFF ≈ 1.0 (0.955 within bootstrap noise). n_eff 5907 / 0.955 = 6185 (6184 printed: rounding). MDE80 2.8 x 0.000090 = 0.000252 against delta_min 0.0005 | CONFIRMED | - |
| 10 | Deviation line once; marker moved with sha | `grep -c 'DECLARED DEVIATION D-2026-10-09-1'` = 1; moved marker 82a5d320 in the backup matches ops.log | CONFIRMED | - |
| 11 | No write to DBs of record | `ls -l --full-time` of the gen/eval views, multicorpus_cache_v1.db and embeddings_cache.db (+wal/shm): identical before and after my re-read. The script's own before/after sha lines are equal | CONFIRMED | - |

Wrong(established) and tie conventions: NOT APPLICABLE (keyed correctness, no judge verdict). Own mutants: none. This is a post-run
numbers review, and no code changed since READY delta4.

## Conditions and defects

- **C-1 (MEDIUM, reading condition; registrar and research-lead).** GRANULARITY-PAYS is HELD against the benchmark level C only.
  - On the same 5907 items, the registered ADAPTIVE (certified, shrunk) rule is beaten by every other granular arm:
    - D_7: -0.00195, UB95 < 0
    - the unshrunk leaves E: -0.00094 [-0.00143, -0.00046]
    - F_flat: -0.00259
    - F_bis: -0.00084
    - the same shrunk path without certification (grid q none): Brier(C) - Brier(arm) +0.00293 against A's +0.00096
  - So certification costs about 0.002 Brier.
  - Any sentence built on AP1 must say "finer than the benchmark level pays". It must never say "the adaptive certified profile pays" or "the tree beats k-means": AP3 and AP4 point the other way.
  - Relative to these 18 models, this split and this embedder.
- **L-1 (LOW).** Registered Support SE 0.00022 (DEFF 2.118, TRANSPORTED from RESP-PROFILE-INFO). The measured SE is 0.000090 and the measured DEFF ≈ 1.0.
  - The transported DEFF counted a different clustering, so the plan was about 2.4x conservative.
  - This is harmless for a HELD word. Future registrations that reuse this design should cite 0.955 (component over item) as the measured value, not 2.118.
- **L-2 (LOW, carried).** L-A1 of READY delta4: X109 was not applied on the commit blob. That affects the selftest only, not the deciding path, and stays as recorded there.

## Commands (scripts backed up: E:/TaxoArena_backup_20261009_postrun_review, SHA256SUMS.txt)

```
sha256sum -c SHA256SUMS.txt     # in the AP backup: 6/6 OK; outcome fc715e4d, marker 82a5d320
git rev-parse HEAD:tools/analysis/adaptive_profile.py; git hash-object tools/analysis/adaptive_profile.py   # f23193bb both
python E:/TaxoArena_tmp/ap_review/dump_dt.py    # (045fd116) pinned read path, out/marker/export -> scratch, Dt pickled, abort before core
python E:/TaxoArena_tmp/ap_review/recompute.py  # (06c5e9c6) own LOMO MAP Rasch (L-BFGS) + theta
python E:/TaxoArena_tmp/ap_review/recompute2.py # (54561ff7) polish; own node fits / tau / BH / stop rule / Brier / bootstrap ->
  # theta = printed; tau2 = printed; certified 260 of 4104; Brier A 0.147595 C 0.148555 D7 0.145645; D_C +0.000961;
  # below 0.5485; d* 7; seed 20261008 LB95 +0.000784 UB95 +0.001137 SD 0.000090; seed 7 +0.000783 / +0.001125; Kish 1.3115
python -c "csv count certified"  # adaptive_profile_fingerprints.csv: 4104 rows, 260 certified
grep -c 'DECLARED DEVIATION D-2026-10-09-1' experiment_results/archv2/adaptive_profile/outcome.txt   # 1
```
