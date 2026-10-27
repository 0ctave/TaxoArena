# TaxoArena — Tuning Harness and Thesis Reproducibility Workflow

This directory contains the automated tuning harness used to optimize parameters of the TaxoArena DAG-max construction pipeline. The architecture consists of a Python orchestrator committed in-repo for research reproducibility.

## File Structure

```
tools/tuning/
  README.md                  # This thesis workflow documentation
  sweep_spec.example.toml    # Factors, levels, seeds, gates, and paths spec
  tuning_harness.py          # Unified CLI for orchestrating tuning runs
  orthogonal_arrays.py       # L9 orthogonal design mapping
  pareto.py                  # Gate-filtering and Pareto-front selection logic
```

## Parameter Space and Level Mapping

An Orthogonal Array $L_9(3^4)$ design is used for parameter screening. The 4 factors mapped onto columns A–D are:
1. **Column A: `assignmentCosineGap`** $\in \{0.02, 0.03, 0.05\}$
2. **Column B: `minBridgeCoverage`** $\in \{25, 50, 75\}$
3. **Column C: `splitThreshold`** $\in \{0.01, 0.02, 0.03\}$ (mapped to Kotlin's `separationEpsilon`)
4. **Column D: `tauFunnelFloor`** $\in \{0.75, 0.80, 0.90\}$

---

## Extended Tuning Metrics and Gates

To improve quality evaluation and structure validation, the tuning harness integrates 22 extended metrics across five categories:

### 1. Hard Gates
* **Acyclic**: Strict DAG acyclicity check.
* **DuplicateBridgeCount**: No duplicate bridges.
* **OrphanCount**: No orphan nodes.
* **MaxAssignmentCapRate**: Fraction of queries exceeding leaf routing capacity ($\le 0.20$).
* **has_depth2_sourceB**: Requires at least one Source-B bridge with depth $\ge 2$.
* **SmallLeafFraction**: Fraction of leaves with $d/N > 10$ ($\le 0.50$).
* **SelectedNodeStarvedLeafFraction**: Fraction of starved leaves under selected nodes ($\le 0.20$).
* **SourceBPerAnchorMean**: Mean Source-B bridges per anchor ($\le 3.0$).

### 2. Soft Gates
* **AvgMatchCount**: Average matches per query (band: $[1.05, 1.30]$).
* **Top1Accuracy**: Top-1 classification accuracy ($\ge 75.6\%$).
* **RoutingECE**: Expected Calibration Error ($\le 0.25$).
* **BorderlineRate**: Fraction of queries with runner-up leaves in cosine gap (band: $[0.20, 0.35]$).
* **CrossAnchorMigrationRate**: Fraction of queries migrated from ground-truth category anchor (band: $[0.10, 0.30]$).
* **CanonicalAdaptedJaccard**: Overlap between canonical and adapted query partitions (band: $[0.40, 0.70]$).

### 3. Pareto Objectives
* **Maximize**: `WeightedLeafPurity`, `DendrogramPurity`, `SphericalSilhouette`, `DeltaRhoTotal`, `CanonicalAdaptedJaccard`.
* **Minimize**: `TotalDasguptaCost`, `RoutingECE`, `BrierScore`, `NoMatchRate`, `SmallLeafFraction`, `KappaShrinkageMean`, `SelectedNodeStarvedLeafFraction`.

---

## Replication / Execution Workflow

Follow this step-by-step sequence to reproduce the tuning results:

### Step 1: Generate Configurations
Generate the 9 screening configurations for the initial design using the screening seed (default `42`):
```bash
python tools/tuning/tuning_harness.py generate --spec tools/tuning/sweep_spec.example.toml --stage screen
```
Verify that the `tuning/runs/` directory has been created and populated with 9 subfolders containing `config.toml` files, and `tuning/runs/manifest.jsonl` contains the pending runs.

### Step 2: Smoke Run
Always run a single configuration as a sanity check before launching the full sweep:
```bash
python tools/tuning/tuning_harness.py run --spec tools/tuning/sweep_spec.example.toml --only L9_001_seed42
```
Confirm the run executes successfully, creates `run.log`, and outputs the required validation CSVs in `tuning/runs/L9_001_seed42/output/seed_42/validation/`.

### Step 3: Run the Full Sweep
Execute all remaining pending screening configurations:
```bash
python tools/tuning/tuning_harness.py run --spec tools/tuning/sweep_spec.example.toml
```

### Step 4: Collect and Merge Metrics
Aggregate all run logs and CSV results into a unified database:
```bash
python tools/tuning/tuning_harness.py collect --spec tools/tuning/sweep_spec.example.toml
```
This produces the unified tables `tuning/combined_ledger.csv` and `tuning/combined_bridges.csv`.

### Step 5: Perform Pareto-Front Selection
Filter configurations by hard gates and find the Pareto-optimal configurations:
```bash
python tools/tuning/tuning_harness.py select --spec tools/tuning/sweep_spec.example.toml
```
This ranks runs by Pareto dominance count and outputs `tuning/finalists.csv` and a readable summary at `tuning/finalists.md`.

### Step 6: Validate Finalists
Generate validation configurations for the top finalists on seeds `137` and `2048`:
```bash
python tools/tuning/tuning_harness.py generate --spec tools/tuning/sweep_spec.example.toml --stage validate
```
Execute the validation runs:
```bash
python tools/tuning/tuning_harness.py run --spec tools/tuning/sweep_spec.example.toml
```
Collect the validation results and run selection:
```bash
python tools/tuning/tuning_harness.py collect --spec tools/tuning/sweep_spec.example.toml
python tools/tuning/tuning_harness.py select --spec tools/tuning/sweep_spec.example.toml
```
The final Pareto front and performance metrics (mean $\pm$ standard deviation across the three seeds) are written to `tuning/finalists.md`.
