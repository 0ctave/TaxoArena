# Tree-only calibration set

Canonical baseline: `experiment_configs/mcs30_eps02_tree.toml`
(seed 42 -> J=0.26696, 177 nodes / 112 leaves, converged iter 6, multi_leaf_rate=0.1518,
held-out Top-1 73.72% [72.25, 75.13]).

A converged tree run is ~175 s, so the whole set below is roughly 40 minutes serial.
Run one at a time — concurrent bootRun JVMs contend and the logs append.

    .\gradlew.bat bootRun --rerun-tasks --no-configuration-cache `
        --args="--config experiment_configs/calibration/<cfg>.toml"

## 1. Reproducibility + baselines  (run this first — it is the thesis-critical one)

`cal_seeds.toml` — seeds 42/137/2048/7/31337, `runBaselines = true`.
Answers the two reviewer blockers at once: variance on every reported metric across five
seeds, cross-seed ARI for structural stability, and recursive k-means / agglomerative at
matched leaf count as comparators.

## 2. Single-knob sweeps (seed 42, baselines off)

| set | values | what it moves | read |
|-----|--------|---------------|------|
| `cal_mcs{20,25,30,35,40}` | minClusterSize | leaf granularity | leaf count, per-leaf held-out support (arena needs >=12), Top-1 |
| `cal_mf{015,025,035}` | membershipFloor | multi-membership breadth | `multi_leaf_rate` (currently 0.1518), dist {1:,2:,3:} |
| `cal_dm{006,012,018}` | descentMargin | residual vs leaf softness | held-out residual rate, leaf population spread |

Each varies ONE parameter from canonical. Do not stack them — the interaction terms are
not what is being measured, and one-change-per-run is what made the earlier debugging
tractable.

## Metrics to collect per run
J, node/leaf count, convergence iteration, multi_leaf_rate + distribution, held-out Top-1
(with Wilson CI), Top-10, held-out residual rate, per-leaf held-out support (leaves under 12).
