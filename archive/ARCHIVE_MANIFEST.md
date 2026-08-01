# Archive manifest

Generated 2026-07-31. **Nothing was deleted.** Every row below is a file or directory that was
moved out of the working tree into `archive/`, keeping its original relative path underneath.
To restore any entry, move it back to the path in the "Original path" column (see `README.md`).

**293 entries, 10.76 GB reclaimed from the working tree.**

Sizes for directories are the recursive total; "Last modified" for a directory is the newest
file it contains. Tracked files were moved with `git mv` (history preserved, rename staged but
not committed); untracked files with a plain move.

## Database backups (20 entries, 10.01 GB)

| Original path | Size | Last modified | Reason archived |
|---|---|---|---|
| `mmlu_pro_dataset_cache.db` | 3.5 MB | 2026-06-26 21:29 | Superseded v1 dataset cache; only referenced by dagmax_regression_off.toml, archived in the same pass. |
| `mmlu_pro_dataset_cache_v2.db.bak-before-link-repair-shm` | 32.0 KB | 2026-07-28 23:02 | Pre-migration backup of the dataset cache; the live cache is untouched. |
| `mmlu_pro_dataset_cache_v2.db.bak-before-link-repair-wal` | 0 B | 2026-07-26 03:46 | Pre-migration backup of the dataset cache; the live cache is untouched. |
| `mmlu_pro_dataset_cache_v2.db.bak-before-link-repair` | 708.9 MB | 2026-07-26 03:14 | Pre-migration backup of the dataset cache; the live cache is untouched. |
| `mmlu_pro_dataset_cache_v2.db.bak-before-pool-migration` | 708.9 MB | 2026-07-26 13:22 | Pre-migration backup of the dataset cache; the live cache is untouched. |
| `mmlu_pro_dataset_cache_v2.db.bak-before-trace-backfill` | 713.7 MB | 2026-07-27 15:55 | Pre-migration backup of the dataset cache; the live cache is untouched. |
| `ratings.db.bak-before-math12` | 7.8 MB | 2026-07-27 18:32 | Backup/duplicate copy of a ratings store; the canonical file it was copied from stays in the working tree. |
| `ratings.db.bak-before-smoke-v2` | 7.8 MB | 2026-07-27 17:35 | Backup/duplicate copy of a ratings store; the canonical file it was copied from stays in the working tree. |
| `ratings.db.bak-before-smoke-v3` | 7.8 MB | 2026-07-27 17:43 | Backup/duplicate copy of a ratings store; the canonical file it was copied from stays in the working tree. |
| `ratings.db.smoke-v2-result` | 7.8 MB | 2026-07-27 17:41 | Backup/duplicate copy of a ratings store; the canonical file it was copied from stays in the working tree. |
| `ratings_engineering_paired.db.final` | 1.4 MB | 2026-07-30 00:39 | Backup/duplicate copy of a ratings store; the canonical file it was copied from stays in the working tree. |
| `ratings_history_paired.db.final` | 6.7 MB | 2026-07-29 09:16 | Backup/duplicate copy of a ratings store; the canonical file it was copied from stays in the working tree. |
| `ratings_law_paired.db.bak-after-MAIN` | 8.8 MB | 2026-07-28 19:05 | Backup/duplicate copy of a ratings store; the canonical file it was copied from stays in the working tree. |
| `ratings_law_paired.db.final` | 17.0 MB | 2026-07-28 22:20 | Backup/duplicate copy of a ratings store; the canonical file it was copied from stays in the working tree. |
| `ratings_math12.db` | 1.8 MB | 2026-07-27 20:46 | Ratings store from a superseded 2026-07-27 smoke/exploration run; not read by any thesis figure script. |
| `ratings_math12_shuffled.db` | 324.0 KB | 2026-07-27 23:16 | Ratings store from a superseded 2026-07-27 smoke/exploration run; not read by any thesis figure script. |
| `ratings_philosophy_paired.db.final` | 2.4 MB | 2026-07-29 01:05 | Backup/duplicate copy of a ratings store; the canonical file it was copied from stays in the working tree. |
| `ratings_physics_paired.db.final` | 2.1 MB | 2026-07-30 11:18 | Backup/duplicate copy of a ratings store; the canonical file it was copied from stays in the working tree. |
| `ratings_psychology_paired.db.final` | 4.6 MB | 2026-07-29 23:05 | Backup/duplicate copy of a ratings store; the canonical file it was copied from stays in the working tree. |
| `snapshots.db.bak-before-reset` | 7.85 GB | 2026-07-26 04:05 | Pre-reset backup of the snapshot store; the live snapshots.db is untouched. |

## Stale logs (13 entries, 0.01 GB)

| Original path | Size | Last modified | Reason archived |
|---|---|---|---|
| `algorithm_trace.log` | 1.9 KB | 2026-06-26 21:29 | Console log of a superseded exploration/calibration run; unreferenced. |
| `arena_math_baseline.log` | 57.1 KB | 2026-07-26 21:23 | Console log of a superseded exploration/calibration run; unreferenced. |
| `arena_math_scoped.log` | 2.2 MB | 2026-07-26 22:07 | Console log of a superseded exploration/calibration run; unreferenced. |
| `arena_smoke_postrepair.log` | 4.1 MB | 2026-07-26 13:18 | Console log of a superseded exploration/calibration run; unreferenced. |
| `arena_validation.log` | 1.2 MB | 2026-07-26 15:09 | Console log of a superseded exploration/calibration run; unreferenced. |
| `arena_validation_recheck.log` | 805.7 KB | 2026-07-26 16:24 | Console log of a superseded exploration/calibration run; unreferenced. |
| `canonical_freeze.log` | 216.4 KB | 2026-07-26 20:07 | Console log of a superseded exploration/calibration run; unreferenced. |
| `canonical_rerun_postrepair.log` | 206.4 KB | 2026-07-26 04:07 | Console log of a superseded exploration/calibration run; unreferenced. |
| `coherence_labels.log` | 190.9 KB | 2026-07-26 16:47 | Console log of a superseded exploration/calibration run; unreferenced. |
| `compile.log` | 918 B | 2026-06-27 16:26 | Console log of a superseded exploration/calibration run; unreferenced. |
| `logs/arenabenchmark.log` | 344.7 KB | 2026-07-20 02:05 | Console log of a superseded exploration/calibration run; unreferenced. |
| `seed_sweep.log` | 4.9 KB | 2026-07-26 18:11 | Console log of a superseded exploration/calibration run; unreferenced. |
| `test_info.log` | 44.0 KB | 2026-07-25 02:22 | Console log of a superseded exploration/calibration run; unreferenced. |

## Obsolete one-offs (11 entries, 0.00 GB)

| Original path | Size | Last modified | Reason archived |
|---|---|---|---|
| `agents` | 0 B | 2026-06-26 21:52 | Empty directory left over from an abandoned agents/ layout. |
| `bridge_candidates.csv` | 4.2 KB | 2026-07-20 16:05 | Bridge-candidate export from the 2026-07-20 polyhierarchy exploration; bridging is now off and the file is unreferenced. |
| `experiment_config.toml` | 250 B | 2026-07-25 01:50 | Root-level stray config from 2026-07-25, superseded by experiment_configs/; unreferenced. |
| `experiment_pipeline_config_full.toml` | 1.0 KB | 2026-07-25 01:50 | Root-level stray pipeline config from 2026-07-25; unreferenced. |
| `experiment_pipeline_test` | 13.5 KB | 2026-07-17 02:57 | 2026-07-17 pipeline smoke-test output directory; unreferenced. |
| `experiment_results_old` | 472.0 KB | 2026-07-18 20:28 | 2026-07-18 pre-rename results directory, superseded by experiment_results/. |
| `experiment_test_run` | 11.5 KB | 2026-07-17 00:32 | 2026-07-17 test-run output directory; unreferenced. |
| `plots` | 26.3 KB | 2026-07-17 01:31 | Two 2026-07-17 exploratory PDFs, superseded by report/Figures/; the only grep hits are matplotlib plt.subplots calls. |
| `reserved_test_queries.canonical14domains.json` | 50.5 KB | 2026-07-26 13:55 | Snapshot copy of the reserved query pool from 2026-07-26; the live reserved_test_queries.json stays. |
| `scratch` | 1.4 KB | 2026-07-17 00:21 | One-off dump/inspection scripts from 2026-07-03..17; the only grep hits are the prose from scratch. |
| `src.zip` | 382.0 KB | 2026-07-17 02:12 | 2026-07-17 source snapshot zip; superseded by git history. |

## Exploration configs (97 entries, 0.00 GB)

| Original path | Size | Last modified | Reason archived |
|---|---|---|---|
| `experiment_configs/B_arena_core_m12.toml` | 1.3 KB | 2026-07-25 14:18 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/C_baseline_arena.toml` | 1.1 KB | 2026-07-25 14:18 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/arena_math_baseline.toml` | 6.2 KB | 2026-07-26 21:38 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/arena_math_scoped.toml` | 6.2 KB | 2026-07-26 20:24 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/arena_smoke.toml` | 5.0 KB | 2026-07-26 02:27 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/arena_validation.toml` | 9.7 KB | 2026-07-26 16:09 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/bar070.toml` | 6.3 KB | 2026-07-26 00:36 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/canonical_verify_structural.toml` | 7.7 KB | 2026-07-27 00:37 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/coherence_labels.toml` | 5.1 KB | 2026-07-26 16:43 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/d2_bar020_z2_s42.toml` | 6.7 KB | 2026-07-26 00:49 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/dagmax_regression_off.toml` | 2.5 KB | 2026-07-25 14:18 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/det20_s137.toml` | 8.1 KB | 2026-07-27 04:35 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/det20_s2048.toml` | 8.1 KB | 2026-07-27 04:35 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/det20_s7.toml` | 8.1 KB | 2026-07-27 04:35 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/diag_domains.toml` | 1.6 KB | 2026-07-25 14:18 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/djse_s42.toml` | 6.6 KB | 2026-07-26 00:36 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/dm000_s42.toml` | 6.7 KB | 2026-07-26 00:36 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/iso_seed137.toml` | 6.4 KB | 2026-07-26 00:36 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/iterfix_maxk4.toml` | 8.1 KB | 2026-07-27 04:35 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/jres_s42.toml` | 6.6 KB | 2026-07-26 00:36 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/kfb_maxk10.toml` | 8.1 KB | 2026-07-27 04:35 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/kfb_maxk4.toml` | 8.1 KB | 2026-07-27 04:35 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/kfb_maxk6.toml` | 8.1 KB | 2026-07-27 04:35 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/kfb_maxk8.toml` | 8.1 KB | 2026-07-27 04:35 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/loosened_routing.toml` | 1.9 KB | 2026-07-25 14:18 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/marginaleps0_repaired.toml` | 8.1 KB | 2026-07-27 04:35 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/mcs28_test.toml` | 4.4 KB | 2026-07-25 14:18 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/mcs30_debug.toml` | 4.4 KB | 2026-07-25 14:18 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/mcs30_eps005_test.toml` | 4.6 KB | 2026-07-25 14:18 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/mcs30_eps02_gc_fast.toml` | 4.5 KB | 2026-07-25 14:18 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/mcs30_eps02_gc_test.toml` | 4.5 KB | 2026-07-25 14:18 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/mcs30_eps02_topo.toml` | 4.5 KB | 2026-07-25 14:18 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/mcs30_eps02_tree_noisefloor.toml` | 6.2 KB | 2026-07-25 18:10 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/mcs30_eps02_v2.toml` | 4.5 KB | 2026-07-25 14:18 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/mcs30_kfallback_test.toml` | 4.5 KB | 2026-07-25 14:18 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/mcs30_sigeps_test.toml` | 4.4 KB | 2026-07-25 14:18 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/mcs30_test.toml` | 4.4 KB | 2026-07-25 14:18 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/mcs35_test.toml` | 4.5 KB | 2026-07-25 14:18 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/mcs55_router.toml` | 8.1 KB | 2026-07-27 04:35 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/mcs65_router.toml` | 8.1 KB | 2026-07-27 04:35 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/me0_maxk6.toml` | 8.1 KB | 2026-07-27 04:35 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/newstable_s42.toml` | 8.1 KB | 2026-07-27 04:35 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/nofield_maxk4.toml` | 8.1 KB | 2026-07-27 04:35 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/probe_fusion_0_90.toml` | 2.2 KB | 2026-07-25 14:18 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/refitgate_s42.toml` | 6.6 KB | 2026-07-26 01:50 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/repro_seed2048.toml` | 4.4 KB | 2026-07-25 14:18 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/routerfix_maxk4.toml` | 8.1 KB | 2026-07-27 04:35 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/sc_maxk4.toml` | 8.1 KB | 2026-07-27 04:35 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/smoke_arena.toml` | 2.2 KB | 2026-07-27 06:00 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/sweep20_s1.toml` | 8.1 KB | 2026-07-27 04:35 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/sweep20_s10.toml` | 8.1 KB | 2026-07-27 04:35 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/sweep20_s11.toml` | 8.1 KB | 2026-07-27 04:35 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/sweep20_s12.toml` | 8.1 KB | 2026-07-27 04:35 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/sweep20_s13.toml` | 8.1 KB | 2026-07-27 04:35 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/sweep20_s14.toml` | 8.1 KB | 2026-07-27 04:35 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/sweep20_s15.toml` | 8.1 KB | 2026-07-27 04:35 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/sweep20_s16.toml` | 8.1 KB | 2026-07-27 04:35 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/sweep20_s17.toml` | 8.1 KB | 2026-07-27 04:35 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/sweep20_s18.toml` | 8.1 KB | 2026-07-27 04:35 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/sweep20_s19.toml` | 8.1 KB | 2026-07-27 04:35 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/sweep20_s2.toml` | 8.1 KB | 2026-07-27 04:35 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/sweep20_s20.toml` | 8.1 KB | 2026-07-27 04:35 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/sweep20_s3.toml` | 8.1 KB | 2026-07-27 04:35 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/sweep20_s4.toml` | 8.1 KB | 2026-07-27 04:35 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/sweep20_s5.toml` | 8.1 KB | 2026-07-27 04:35 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/sweep20_s6.toml` | 8.1 KB | 2026-07-27 04:35 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/sweep20_s7.toml` | 8.1 KB | 2026-07-27 04:35 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/sweep20_s8.toml` | 8.1 KB | 2026-07-27 04:35 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/sweep20_s9.toml` | 8.1 KB | 2026-07-27 04:35 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/thesis_canonical_ema_off.toml` | 1.3 KB | 2026-07-25 14:18 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/thesis_canonical_ema_on.toml` | 1.3 KB | 2026-07-25 14:18 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/thesis_canonical_no_gt.toml` | 1.7 KB | 2026-07-25 14:18 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/thesis_dagmax_test.toml` | 2.0 KB | 2026-07-25 14:18 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/z2v_s137.toml` | 6.7 KB | 2026-07-26 00:36 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/z2v_s2048.toml` | 6.7 KB | 2026-07-26 00:36 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/z2v_s31337.toml` | 6.7 KB | 2026-07-26 00:36 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/z2v_s42.toml` | 6.7 KB | 2026-07-26 00:36 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/z2v_s7.toml` | 6.7 KB | 2026-07-26 00:36 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/zgate2_repaired.toml` | 8.1 KB | 2026-07-27 04:35 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/zgate2_s137.toml` | 8.1 KB | 2026-07-27 04:35 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/zgate2_s2048.toml` | 8.1 KB | 2026-07-27 04:35 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/zgate2_s31337.toml` | 8.1 KB | 2026-07-27 04:35 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/zgate2_s7.toml` | 8.1 KB | 2026-07-27 04:35 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/zgate_tau_s137.toml` | 3.4 KB | 2026-07-25 23:53 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/zgate_tau_s2048.toml` | 3.4 KB | 2026-07-25 23:53 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/zgate_tau_s42.toml` | 3.4 KB | 2026-07-25 23:53 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/zgate_z2_s137.toml` | 3.4 KB | 2026-07-25 23:53 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/zgate_z2_s2048.toml` | 3.4 KB | 2026-07-25 23:53 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/zgate_z2_s42.toml` | 3.4 KB | 2026-07-25 23:53 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/zgate_z3_s137.toml` | 3.4 KB | 2026-07-25 23:53 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/zgate_z3_s2048.toml` | 3.4 KB | 2026-07-25 23:53 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/zgate_z3_s42.toml` | 3.4 KB | 2026-07-25 23:53 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/ztau_s137.toml` | 6.7 KB | 2026-07-26 00:36 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/ztau_s2048.toml` | 6.7 KB | 2026-07-26 00:36 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/ztau_s31337.toml` | 6.7 KB | 2026-07-26 00:36 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/ztau_s42.toml` | 6.7 KB | 2026-07-26 00:36 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |
| `experiment_configs/ztau_s7.toml` | 6.7 KB | 2026-07-26 00:36 | One-off calibration/exploration config; no reference from src, report, config, build.gradle.kts, or any surviving config. |

## Superseded run artefacts (152 entries, 0.73 GB)

| Original path | Size | Last modified | Reason archived |
|---|---|---|---|
| `benchmark_backups/benchmark_20260705_205943_Auto_saved_after_gen_20260709_152100.json` | 14.7 MB | 2026-07-09 15:21 | Benchmark JSON backup for a pre-2026-07-27 snapshot; `benchmark_backups/` is written to but never read by the codebase. |
| `benchmark_backups/benchmark_20260717_012916_Headless_Run_Auto_ge_CANONICAL_20260717_012916.json` | 220 B | 2026-07-17 01:29 | Benchmark JSON backup for a pre-2026-07-27 snapshot; `benchmark_backups/` is written to but never read by the codebase. |
| `benchmark_backups/benchmark_20260717_013143_Headless_Run_Auto_ge_CANONICAL_20260717_013143.json` | 32.4 KB | 2026-07-17 01:31 | Benchmark JSON backup for a pre-2026-07-27 snapshot; `benchmark_backups/` is written to but never read by the codebase. |
| `benchmark_backups/benchmark_20260717_025752_Headless_Run_Auto_ge_CANONICAL_20260717_025756.json` | 25.6 KB | 2026-07-17 02:57 | Benchmark JSON backup for a pre-2026-07-27 snapshot; `benchmark_backups/` is written to but never read by the codebase. |
| `benchmark_backups/benchmark_20260718_195733_Headless_Run_Auto_ge_MAIN_20260718_200022.json` | 127.5 KB | 2026-07-18 20:00 | Benchmark JSON backup for a pre-2026-07-27 snapshot; `benchmark_backups/` is written to but never read by the codebase. |
| `benchmark_backups/benchmark_20260718_200533_Headless_Run_Auto_ge_C3_20260718_201150.json` | 181.8 KB | 2026-07-18 20:11 | Benchmark JSON backup for a pre-2026-07-27 snapshot; `benchmark_backups/` is written to but never read by the codebase. |
| `benchmark_backups/benchmark_20260718_200533_Headless_Run_Auto_ge_C5_20260718_201414.json` | 246.5 KB | 2026-07-18 20:14 | Benchmark JSON backup for a pre-2026-07-27 snapshot; `benchmark_backups/` is written to but never read by the codebase. |
| `benchmark_backups/benchmark_20260718_200533_Headless_Run_Auto_ge_KMEANS_BASELINE_20260718_202215.json` | 94.5 KB | 2026-07-18 20:22 | Benchmark JSON backup for a pre-2026-07-27 snapshot; `benchmark_backups/` is written to but never read by the codebase. |
| `benchmark_backups/benchmark_20260718_200533_Headless_Run_Auto_ge_MAIN_20260718_200908.json` | 190.0 KB | 2026-07-18 20:09 | Benchmark JSON backup for a pre-2026-07-27 snapshot; `benchmark_backups/` is written to but never read by the codebase. |
| `benchmark_backups/benchmark_20260718_200533_Headless_Run_Auto_ge_RANDOMNULL_BASELINE_20260718_202847.json` | 189.8 KB | 2026-07-18 20:28 | Benchmark JSON backup for a pre-2026-07-27 snapshot; `benchmark_backups/` is written to but never read by the codebase. |
| `benchmark_backups/benchmark_20260718_200533_Headless_Run_Auto_ge_RANDOM_SCHEDULER_20260718_201743.json` | 183.8 KB | 2026-07-18 20:17 | Benchmark JSON backup for a pre-2026-07-27 snapshot; `benchmark_backups/` is written to but never read by the codebase. |
| `benchmark_backups/benchmark_20260718_200533_Headless_Run_Auto_ge_ROUND_ROBIN_20260718_202047.json` | 188.0 KB | 2026-07-18 20:20 | Benchmark JSON backup for a pre-2026-07-27 snapshot; `benchmark_backups/` is written to but never read by the codebase. |
| `benchmark_backups/benchmark_20260718_200533_Headless_Run_Auto_ge_WARD_BASELINE_20260718_202532.json` | 185.9 KB | 2026-07-18 20:25 | Benchmark JSON backup for a pre-2026-07-27 snapshot; `benchmark_backups/` is written to but never read by the codebase. |
| `benchmark_backups/benchmark_20260718_234511_Headless_Run_Auto_ge_C3_20260718_234918.json` | 91.1 KB | 2026-07-18 23:49 | Benchmark JSON backup for a pre-2026-07-27 snapshot; `benchmark_backups/` is written to but never read by the codebase. |
| `benchmark_backups/benchmark_20260718_234511_Headless_Run_Auto_ge_C5_20260718_235118.json` | 125.5 KB | 2026-07-18 23:51 | Benchmark JSON backup for a pre-2026-07-27 snapshot; `benchmark_backups/` is written to but never read by the codebase. |
| `benchmark_backups/benchmark_20260718_234511_Headless_Run_Auto_ge_KMEANS_BASELINE_20260718_235758.json` | 89.6 KB | 2026-07-18 23:57 | Benchmark JSON backup for a pre-2026-07-27 snapshot; `benchmark_backups/` is written to but never read by the codebase. |
| `benchmark_backups/benchmark_20260718_234511_Headless_Run_Auto_ge_MAIN_20260718_234730.json` | 96.2 KB | 2026-07-18 23:47 | Benchmark JSON backup for a pre-2026-07-27 snapshot; `benchmark_backups/` is written to but never read by the codebase. |
| `benchmark_backups/benchmark_20260718_234511_Headless_Run_Auto_ge_RANDOMNULL_BASELINE_20260719_000215.json` | 95.6 KB | 2026-07-19 00:02 | Benchmark JSON backup for a pre-2026-07-27 snapshot; `benchmark_backups/` is written to but never read by the codebase. |
| `benchmark_backups/benchmark_20260718_234511_Headless_Run_Auto_ge_RANDOM_SCHEDULER_20260718_235338.json` | 94.1 KB | 2026-07-18 23:53 | Benchmark JSON backup for a pre-2026-07-27 snapshot; `benchmark_backups/` is written to but never read by the codebase. |
| `benchmark_backups/benchmark_20260718_234511_Headless_Run_Auto_ge_ROUND_ROBIN_20260718_235550.json` | 95.4 KB | 2026-07-18 23:55 | Benchmark JSON backup for a pre-2026-07-27 snapshot; `benchmark_backups/` is written to but never read by the codebase. |
| `benchmark_backups/benchmark_20260718_234511_Headless_Run_Auto_ge_WARD_BASELINE_20260719_000000.json` | 95.2 KB | 2026-07-19 00:00 | Benchmark JSON backup for a pre-2026-07-27 snapshot; `benchmark_backups/` is written to but never read by the codebase. |
| `benchmark_backups/benchmark_20260726_023615_Headless_Run_Auto_ge_MAIN_20260726_023710.json` | 73.5 KB | 2026-07-26 02:37 | Benchmark JSON backup for a pre-2026-07-27 snapshot; `benchmark_backups/` is written to but never read by the codebase. |
| `benchmark_backups/benchmark_20260726_025321_Headless_Run_Auto_ge_MAIN_20260726_025409.json` | 72.6 KB | 2026-07-26 02:54 | Benchmark JSON backup for a pre-2026-07-27 snapshot; `benchmark_backups/` is written to but never read by the codebase. |
| `benchmark_backups/benchmark_20260726_131644_Headless_Run_Auto_ge_MAIN_20260726_131844.json` | 116.8 KB | 2026-07-26 13:18 | Benchmark JSON backup for a pre-2026-07-27 snapshot; `benchmark_backups/` is written to but never read by the codebase. |
| `benchmark_backups/benchmark_20260726_145101_Headless_Run_Auto_ge_GENERIC_JUDGE_20260726_150218.json` | 448.5 KB | 2026-07-26 15:02 | Benchmark JSON backup for a pre-2026-07-27 snapshot; `benchmark_backups/` is written to but never read by the codebase. |
| `benchmark_backups/benchmark_20260726_145101_Headless_Run_Auto_ge_MAIN_20260726_145742.json` | 554.4 KB | 2026-07-26 14:57 | Benchmark JSON backup for a pre-2026-07-27 snapshot; `benchmark_backups/` is written to but never read by the codebase. |
| `benchmark_backups/benchmark_20260726_145101_Headless_Run_Auto_ge_ORACLE_20260726_145750.json` | 295.4 KB | 2026-07-26 14:57 | Benchmark JSON backup for a pre-2026-07-27 snapshot; `benchmark_backups/` is written to but never read by the codebase. |
| `benchmark_backups/benchmark_20260726_145101_Headless_Run_Auto_ge_RANDOM_SCHEDULER_20260726_150922.json` | 531.4 KB | 2026-07-26 15:09 | Benchmark JSON backup for a pre-2026-07-27 snapshot; `benchmark_backups/` is written to but never read by the codebase. |
| `benchmark_backups/benchmark_20260726_160549_Headless_Run_Auto_ge_GENERIC_JUDGE_20260726_161742.json` | 541.4 KB | 2026-07-26 16:17 | Benchmark JSON backup for a pre-2026-07-27 snapshot; `benchmark_backups/` is written to but never read by the codebase. |
| `benchmark_backups/benchmark_20260726_160549_Headless_Run_Auto_ge_MAIN_20260726_161250.json` | 581.1 KB | 2026-07-26 16:12 | Benchmark JSON backup for a pre-2026-07-27 snapshot; `benchmark_backups/` is written to but never read by the codebase. |
| `benchmark_backups/benchmark_20260726_160549_Headless_Run_Auto_ge_ORACLE_20260726_161259.json` | 293.6 KB | 2026-07-26 16:12 | Benchmark JSON backup for a pre-2026-07-27 snapshot; `benchmark_backups/` is written to but never read by the codebase. |
| `benchmark_backups/benchmark_20260726_160549_Headless_Run_Auto_ge_RANDOM_SCHEDULER_20260726_162409.json` | 565.8 KB | 2026-07-26 16:24 | Benchmark JSON backup for a pre-2026-07-27 snapshot; `benchmark_backups/` is written to but never read by the codebase. |
| `benchmark_backups/benchmark_20260726_200711_Headless_Run_Auto_ge_MAIN_20260726_211241.json` | 2.5 MB | 2026-07-26 21:12 | Benchmark JSON backup for a pre-2026-07-27 snapshot; `benchmark_backups/` is written to but never read by the codebase. |
| `benchmark_backups/benchmark_20260726_200711_Headless_Run_Auto_ge_MAIN_20260726_220709.json` | 2.5 MB | 2026-07-26 22:07 | Benchmark JSON backup for a pre-2026-07-27 snapshot; `benchmark_backups/` is written to but never read by the codebase. |
| `experiment_results/arena_math_baseline` | 54.2 KB | 2026-07-26 21:23 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/arena_math_scoped_prev` | 4.9 MB | 2026-07-26 21:12 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/arena_math_scoped` | 5.6 MB | 2026-07-26 22:07 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/arena_smoke_prev` | 8.3 MB | 2026-07-26 02:54 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/arena_smoke` | 4.3 MB | 2026-07-26 13:18 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/arena_validation` | 1.7 MB | 2026-07-26 16:24 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/bar070` | 2.1 MB | 2026-07-25 18:50 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/canonical_baseline_preLinkRepair` | 4.6 MB | 2026-07-26 02:27 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/canonical_freeze_attempt1` | 9.0 MB | 2026-07-26 19:02 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/canonical_freeze_attempt2` | 9.1 MB | 2026-07-26 19:31 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/canonical_verify_structural` | 8.8 MB | 2026-07-27 01:02 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/coherence_labels` | 3.2 MB | 2026-07-26 16:47 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/d2_bar020_z2_s42` | 2.8 MB | 2026-07-26 00:54 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/dagmax_feature_on.zip` | 1.3 MB | 2026-07-19 21:04 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/dagmax_feature_on` | 5.3 MB | 2026-07-20 20:59 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/dagmax_regression_off` | 5.0 MB | 2026-07-19 16:08 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/det20_s137` | 9.4 MB | 2026-07-27 05:36 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/det20_s2048` | 9.4 MB | 2026-07-27 05:39 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/det20_s7` | 9.4 MB | 2026-07-27 05:32 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/det_s137` | 3.0 MB | 2026-07-26 18:05 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/det_s2048` | 3.0 MB | 2026-07-26 18:08 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/det_s7` | 3.0 MB | 2026-07-26 18:11 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/diag_domains_1domain_cs` | 167.4 KB | 2026-07-23 03:52 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/diag_domains_1domain_membershipfloor010` | 141.5 KB | 2026-07-23 04:28 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/diag_domains_2domain_membershipfloor010` | 421.0 KB | 2026-07-23 04:30 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/diag_domains_4domain_chain_flatten_FAILED_never_converged.log` | 728.2 KB | 2026-07-23 05:19 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/diag_domains_4domain_chain_flatten_FAILED_never_converged` | 1.3 MB | 2026-07-23 05:19 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/diag_domains_4domain_pre_veto_fix` | 655.2 KB | 2026-07-23 04:35 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/diag_domains_4domain_veto_removed_35iter` | 795.8 KB | 2026-07-23 04:41 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/diag_domains_pre_chain_flatten_fix_050329` | 846.0 KB | 2026-07-23 04:53 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/diag_domains_v2_attempt_FAILED_oscillated.log` | 383.5 KB | 2026-07-23 05:37 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/diag_domains` | 841.0 KB | 2026-07-23 07:46 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/djse_s42` | 2.8 MB | 2026-07-25 22:01 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/dm000_s42` | 2.4 MB | 2026-07-25 21:08 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/iso_seed137` | 2.6 MB | 2026-07-25 19:50 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/iterfix_maxk4` | 11.7 MB | 2026-07-27 02:51 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/jres_s42` | 2.8 MB | 2026-07-25 21:34 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/kfb_maxk4` | 9.2 MB | 2026-07-27 02:14 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/kfb_maxk6` | 11.0 MB | 2026-07-27 02:22 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/kfb_maxk8` | 2.8 MB | 2026-07-27 02:34 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/loosened_routing` | 18.6 MB | 2026-07-21 02:49 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/marginaleps0_repaired` | 8.8 MB | 2026-07-27 01:30 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/mcs28_test` | 3.7 MB | 2026-07-24 15:07 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/mcs30_debug` | 3.2 MB | 2026-07-24 21:16 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/mcs30_eps005_test` | 2.7 MB | 2026-07-24 15:11 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/mcs30_eps02_gc_fast` | 797.2 KB | 2026-07-25 03:50 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/mcs30_eps02_gc_test` | 2.2 MB | 2026-07-25 03:16 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/mcs30_eps02_topo` | 345.6 KB | 2026-07-25 12:47 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/mcs30_eps02_tree_noisefloor` | 396.8 KB | 2026-07-25 18:14 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/mcs30_eps02_v2` | 498.9 KB | 2026-07-25 13:36 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/mcs30_kfallback_test` | 4.2 MB | 2026-07-24 21:38 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/mcs30_sigeps_test` | 2.9 MB | 2026-07-24 21:55 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/mcs30_test` | 2.7 MB | 2026-07-24 14:30 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/mcs35_test` | 2.6 MB | 2026-07-24 14:44 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/mcs55_router` | 9.4 MB | 2026-07-27 03:52 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/mcs65_router` | 8.0 MB | 2026-07-27 03:55 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/me0_maxk6` | 4.4 MB | 2026-07-27 01:41 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/nofield_maxk4` | 9.2 MB | 2026-07-27 03:01 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/probe_fusion_0_90` | 5.1 MB | 2026-07-21 22:11 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/refitgate_s42` | 2.5 MB | 2026-07-26 02:03 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/repro_seed2048` | 11.4 MB | 2026-07-24 03:23 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/routerfix_maxk4` | 27.2 MB | 2026-07-27 03:15 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/sc_maxk4` | 8.3 MB | 2026-07-27 02:39 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/staged_calib_test` | 3.2 MB | 2026-07-24 01:39 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/sweep20_s10` | 8.9 MB | 2026-07-27 04:51 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/sweep20_s11` | 13.5 MB | 2026-07-27 04:56 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/sweep20_s12` | 13.9 MB | 2026-07-27 05:00 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/sweep20_s13` | 9.5 MB | 2026-07-27 05:04 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/sweep20_s14` | 9.2 MB | 2026-07-27 05:07 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/sweep20_s15` | 9.2 MB | 2026-07-27 05:11 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/sweep20_s16` | 8.4 MB | 2026-07-27 05:14 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/sweep20_s17` | 8.1 MB | 2026-07-27 05:17 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/sweep20_s18` | 8.8 MB | 2026-07-27 05:21 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/sweep20_s19` | 9.0 MB | 2026-07-27 05:25 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/sweep20_s1` | 10.1 MB | 2026-07-27 04:18 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/sweep20_s20` | 8.4 MB | 2026-07-27 05:29 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/sweep20_s2` | 8.2 MB | 2026-07-27 04:22 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/sweep20_s3` | 9.3 MB | 2026-07-27 04:25 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/sweep20_s4` | 9.6 MB | 2026-07-27 04:29 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/sweep20_s5` | 13.2 MB | 2026-07-27 04:33 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/sweep20_s6` | 8.9 MB | 2026-07-27 04:37 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/sweep20_s7` | 7.5 MB | 2026-07-27 04:40 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/sweep20_s8` | 9.1 MB | 2026-07-27 04:44 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/sweep20_s9` | 8.2 MB | 2026-07-27 04:48 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/sweep_s137` | 2.7 MB | 2026-07-26 17:53 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/sweep_s2048` | 2.8 MB | 2026-07-26 17:55 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/sweep_s31337` | 2.8 MB | 2026-07-26 18:02 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/sweep_s42` | 3.0 MB | 2026-07-26 17:50 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/sweep_s7` | 2.8 MB | 2026-07-26 17:58 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/taxonomy_m12` | 10.1 MB | 2026-07-19 13:30 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/test_dag_metrics` | 5.1 MB | 2026-07-20 05:04 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/thesis_canonical_ema_off` | 546.2 KB | 2026-07-23 00:46 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/thesis_canonical_ema_on` | 224.6 KB | 2026-07-23 00:46 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/thesis_canonical_no_gt` | 2.3 MB | 2026-07-22 17:13 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/thesis_dagmax_test` | 8.2 MB | 2026-07-21 03:56 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/wide_sweep_baseline` | 103.1 KB | 2026-07-20 16:55 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/z2v` | 13.1 MB | 2026-07-26 00:17 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/zgate2_repaired` | 7.6 MB | 2026-07-27 01:18 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/zgate2_s137` | 6.2 MB | 2026-07-27 01:51 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/zgate2_s2048` | 6.5 MB | 2026-07-27 01:54 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/zgate2_s31337` | 9.2 MB | 2026-07-27 01:57 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/zgate2_s7` | 7.1 MB | 2026-07-27 01:49 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/zgate` | 25.2 MB | 2026-07-25 23:24 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `experiment_results/ztau` | 13.3 MB | 2026-07-25 23:55 | Result directory of a superseded calibration/exploration run; its config was archived alongside it. |
| `frozen_triples_20260717_025752_Headless_Run_Auto_ge.json` | 1.6 KB | 2026-07-17 02:57 | Frozen-triples set for an obsolete snapshot id; the live 20260727_042523 set is untouched. |
| `frozen_triples_20260718_195733_Headless_Run_Auto_ge.json` | 6.2 KB | 2026-07-18 20:00 | Frozen-triples set for an obsolete snapshot id; the live 20260727_042523 set is untouched. |
| `frozen_triples_20260718_200533_Headless_Run_Auto_ge.json` | 9.1 KB | 2026-07-18 20:09 | Frozen-triples set for an obsolete snapshot id; the live 20260727_042523 set is untouched. |
| `frozen_triples_20260718_234511_Headless_Run_Auto_ge.json` | 4.7 KB | 2026-07-18 23:47 | Frozen-triples set for an obsolete snapshot id; the live 20260727_042523 set is untouched. |
| `frozen_triples_20260726_023615_Headless_Run_Auto_ge_MAIN.json` | 2.7 KB | 2026-07-26 02:37 | Frozen-triples set for an obsolete snapshot id; the live 20260727_042523 set is untouched. |
| `frozen_triples_20260726_025321_Headless_Run_Auto_ge_MAIN.json` | 2.7 KB | 2026-07-26 02:54 | Frozen-triples set for an obsolete snapshot id; the live 20260727_042523 set is untouched. |
| `frozen_triples_20260726_131644_Headless_Run_Auto_ge_MAIN.json` | 4.6 KB | 2026-07-26 13:18 | Frozen-triples set for an obsolete snapshot id; the live 20260727_042523 set is untouched. |
| `frozen_triples_20260726_145101_Headless_Run_Auto_ge_MAIN.json` | 16.1 KB | 2026-07-26 14:57 | Frozen-triples set for an obsolete snapshot id; the live 20260727_042523 set is untouched. |
| `frozen_triples_20260726_160549_Headless_Run_Auto_ge_MAIN.json` | 16.1 KB | 2026-07-26 16:12 | Frozen-triples set for an obsolete snapshot id; the live 20260727_042523 set is untouched. |
| `frozen_triples_20260726_200711_Headless_Run_Auto_ge_MAIN.json` | 81.0 KB | 2026-07-26 22:06 | Frozen-triples set for an obsolete snapshot id; the live 20260727_042523 set is untouched. |
| `frozen_triples_stubbed-snapshot.json` | 313 B | 2026-07-18 19:11 | Frozen-triples set for an obsolete snapshot id; the live 20260727_042523 set is untouched. |
| `tuning/combined_ledger_round1.csv` | 6.7 KB | 2026-07-23 21:44 | Round-1 / pre-DAG-max tuning output, superseded by tuning/runs and tuning/combined_ledger.csv which stay in place. |
| `tuning/runs_dagmax_archive_1425` | 61.6 MB | 2026-07-25 14:15 | Round-1 / pre-DAG-max tuning output, superseded by tuning/runs and tuning/combined_ledger.csv which stay in place. |
| `tuning/runs_round1` | 36.6 MB | 2026-07-25 01:50 | Round-1 / pre-DAG-max tuning output, superseded by tuning/runs and tuning/combined_ledger.csv which stay in place. |


## Second pass, 2026-07-31 evening (handover cleanup)

Same rules as above: moved, not deleted; original relative path preserved under `archive/`.

| Original path | Reason archived |
|---|---|
| `experiment_configs/arena_{cs,engineering,law,math,philosophy,physics,psychology}_newlogic.toml`, `arena_{engineering,math,physics}_qfix.toml`, `arena_history_{full,m12_newlogic,m15,optionblind,paired_v2,propalloc,resolved,resolved_s137}.toml`, `arena_math_12model.toml` (19 files) | Configs of the parked pre-baseline exploration runs (their outputs live in `testing/`); superseded by the r8 batch. |
| `experiment_configs/mcs30_eps02_test.toml`, `mcs30_eps02_tree.toml`, `mcs30_eps02_tree_treefix.toml`, `bar025.toml`, `smoke_arena_v2.toml`, `thesis_canonical.toml`, `arena_math_rerun.toml` (tracked, git mv) | Superseded calibration/exploration configs; results archived alongside where they still existed. |
| `experiment_results/{arena_history_resolved, arena_history_resolved_s137, thesis_canonical, bar025, mcs30_eps02_test, mcs30_eps02_tree, mcs30_eps02_tree_treefix}` | Result folders of the configs above; not part of the r8 evidence base. |
| `ratings_history_resolved.db` (+`-shm`,`-wal`), `ratings_history_resolved.db.SECURED-s42` (+sidecars), `ratings_history_resolved_s137.db` (+sidecars) | Validation-era RESOLVED-mode history stores, superseded by `experiment_results/r8/history/`. |
| `ratings_r8_history.db.TRIAL` | Trial run preceding the final r8 history run. |
| `ratings_baseline_math.db-shm/-wal`, `ratings_baseline_physics.db-shm/-wal` | Orphaned SQLite sidecars; their base `.db` files no longer exist. |
| `docs/compass_artifact_wf-2770ccdb-...md` | Imported research dump, not a project deliverable. |
| `.claude/tmp_abstention_distance.py`, `.claude/tmp_rubric_blindness.py`, `.claude/{abstention_triples,ladder,rubric_blindness_cells}.json` -> `archive/analysis_scratch/` | One-off session analysis scratch behind review numbers; kept for provenance. |
| `tools/tuning/sweep_spec.dagmax.toml.bak` -> `archive/tuning/` (git mv) | DAG-era sweep spec backup, superseded by the tree-calibration `sweep_spec.toml`. |

Deleted (regenerable junk, not archived): `snapshots_test.db` (recreated by any test run via TaxonomySnapshotManager), `frozen_triples_stubbed-snapshot_MAIN.json` (test stub output), `tools/tuning/__pycache__/` and `tools/analysis/__pycache__/` (Python bytecode caches).

Result reorganisation (not an archive move): the 8-domain batch was grouped under `experiment_results/r8/<domain>/` — each domain folder now holds its `ratings_r8_<domain>.db` (+sidecars) beside its `seed_42/` exports, plus `verify_agree_philosophy/` with `ratings_verify_agree.db`. See `experiment_results/r8/README.md`. `report/Figures/make_routing_provenance.py` and `make_rubric_reach.py` were updated to the new paths and re-run.

## Third pass — 2026-07-31, evening (figure-review implementation)

| Item | Reason |
|---|---|
| `ratings_{math,law,philosophy,history,psychology,engineering}_paired.db` -> `archive/` (git mv) | Databases of the withdrawn twelve-model paired campaign. The thesis withdrew the campaign in its entirety; keeping them at repo root let retired figure scripts silently regenerate withdrawn-data PDFs. Retained for provenance (registration record, corrections register). |
| `report/Figures/{verdict_mechanism,trace_strata,rho_levels,screen_vs_arena,domain_screen,routing_slopegraph,rubric_specific_not_decisive}.pdf` + their `make_*.py` | Deleted, not archived: all drew withdrawn pilot/twelve-model data or the withdrawn 0.007 threshold; recoverable from git history. `rubric_specificity_null` replaces the surviving offline panel of the last one. |
