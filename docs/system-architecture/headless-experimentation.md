# Headless Experimentation Guide

The **TaxoArena Headless Experimentation Runner** provides a command-line interface (CLI) to bypass the interactive Compose TUI and execute batch benchmarks, generate deterministic dataset splits, and run the 4-condition evaluation matrix back-to-back. It automatically exports all metrics, leaf-level leaderboards, and judge rationales to structured CSV and JSON files for downstream scientific analysis (e.g., Chapter 6 of the thesis).

---

## 🚀 Execution Command

To run the headless benchmark, launch the Spring Boot application using the Gradle bootRun task and pass the `--config` parameter with the path to your configuration file:

```bash
./gradlew bootRun --args="--config experiment_config.toml"
```

If running the compiled fat JAR directly:

```bash
java -jar build/libs/TaxoArena-all.jar --config experiment_config.toml
```

> [!NOTE]
> Supplying the `--config` command-line argument automatically disables the TUI composition and standard console hooks, redirecting the execution flow entirely to the headless runner.

---

## ⚙️ Configuration Files

The runner supports both **JSON** and **TOML** configuration file formats. 

### 1. TOML Configuration Example (`experiment_config.toml`)
Create a file named `experiment_config.toml` in the project root:

```toml
# The unique ID of the taxonomy snapshot to load from snapshots.db
snapshotId = "20260705_205943_Auto_saved_after_gen"

# List of precomputed models to evaluate (must exist in eval_results table)
models = [
    "gpt-4o-2024-08-06",
    "gemini-1.5-pro-002",
    "Meta-Llama-3-70B-Instruct"
]

# Limit the number of test queries evaluated (0 = run all available test queries)
queryLimit = 100

# Optional: Restrict evaluation to one ground truth category (e.g. "economics")
# Leave out or comment out to run on all categories
# category = "economics"

# The confidence threshold for recording matchups in the leaderboard
confidenceGate = 0.65

# Parallelism configuration for the matchmaking loop
parallelism = 6
questionsPerRound = 12

# Benchmark only the reserved test pool queries (recommended for evaluation)
reservedOnly = true

# The experimental conditions to run sequentially (matrix evaluation)
conditions = ["MAIN", "CANONICAL", "GENERIC_JUDGE", "RANDOM_SCHEDULER"]

# Root directory where validation and judging CSVs are exported
outputDir = "experiment_results"

# Whether to regenerate the train/test split (70/30) and overwrite the reserved pool
regenerateSplit = false
testRatio = 0.3
seed = 42
```

### 2. JSON Configuration Example (`experiment_config.json`)
The equivalent JSON representation:

```json
{
  "snapshotId": "20260705_205943_Auto_saved_after_gen",
  "models": [
    "gpt-4o-2024-08-06",
    "gemini-1.5-pro-002",
    "Meta-Llama-3-70B-Instruct"
  ],
  "queryLimit": 100,
  "category": null,
  "confidenceGate": 0.65,
  "parallelism": 6,
  "questionsPerRound": 12,
  "reservedOnly": true,
  "conditions": ["MAIN", "CANONICAL", "GENERIC_JUDGE", "RANDOM_SCHEDULER"],
  "outputDir": "experiment_results",
  "testRatio": 0.3,
  "seed": 42,
  "regenerateSplit": false
}
```

---

## 🔍 The 4 Experimental Conditions

The runner isolates the database tables and outputs for each condition by suffixing the snapshot ID (e.g. `20260705_205943_Auto_saved_after_gen_CANONICAL`), preventing different runs from corrupting each other's leaderboards.

| Condition | Name | Scheduling Strategy | Evaluation Mechanism |
| :--- | :---: | :--- | :--- |
| **`MAIN`** | C1 (Main) | Active matchmaking (uncertainty entropy prioritisation) | Domain-adapted leaf judge prompt with custom contrastive rubrics. |
| **`C3`** | C3 (Ablated Persona) | Replay of MAIN query-model triples | Node-specific per-leaf prompt with generic static judge rubric. |
| **`C5`** | C5 (FastChat) | Replay of MAIN query-model triples | Static FastChat pair-v2 prompt (verbatim comparison mode). |
| **`GENERIC_JUDGE`** | Generic | Active matchmaking (uncertainty entropy prioritisation) | Generic static LLM judge prompt and generic static rubric. |
| **`RANDOM_SCHEDULER`**| Random | Random selection (ignores standard error / entropy) | Domain-adapted leaf judge prompt with custom contrastive rubrics. |

---

## 📂 Exported Directory Structure

Upon completion, all results are written to the directory specified by `outputDir` (e.g. `../../experiment_results_old/`):

```directory
experiment_results/
├── manifest.json
├── validation/
│   ├── MAIN_metrics.csv
│   ├── MAIN_leaf_leaderboard.csv
│   ├── MAIN_domain_stats.csv
│   ├── CANONICAL_metrics.csv
│   ├── ...
└── judging/
    ├── MAIN_verdicts.csv
    ├── CANONICAL_verdicts.csv
    └── ...
```

### 1. `manifest.json`
Contains experiment-level metadata describing the execution context:
```json
{
  "runId": "run_2026-07-16T22-12-30.079353800Z",
  "snapshotId": "20260705_205943_Auto_saved_after_gen",
  "models": ["gpt-4o-2024-08-06", "gemini-1.5-pro-002"],
  "seed": 42,
  "testRatio": 0.3,
  "conditionsRun": ["CANONICAL"],
  "runTimestamp": "2026-07-16T22:12:30.079853Z"
}
```

### 2. Validation Metrics (`validation/<condition>_metrics.csv`)
Summary of overall accuracy-judge agreement rates and question coverage:
```csv
Condition,TotalQueries,TotalModelPairs,CoverageRate,OverallJudgeAccuracyAgreement
MAIN,100,3,0.95,0.78
```

### 3. Leaf Leaderboard (`validation/<condition>_leaf_leaderboard.csv`)
Leaf-level Bradley-Terry model scores, standard errors, and total matches. Use this to track local leaf rankings:
```csv
Condition,LeafId,ModelId,BtScore,StdError,TotalComparisons
MAIN,leaf-12,gpt-4o-2024-08-06,1.45,0.18,48
MAIN,leaf-12,gemini-1.5-pro-002,0.82,0.22,48
```

### 4. Domain Stats (`validation/<condition>_domain_stats.csv`)
Leaf-level statistics on question count, average judge confidence, and local agreement rates:
```csv
Condition,Domain,TotalQueries,AgreementRate,AvgConfidence,CoverageRate
MAIN,Statistical Inference,25,0.84,0.89,1.0
```

### 5. Judge Verdicts Audit (`judging/<condition>_verdicts.csv`)
The complete row-by-row log of every match. This serves as the full audit trail of LLM judge explanations:
```csv
Condition,QueryText,Category,ModelA,ModelB,AnswerA,AnswerB,CorrectA,CorrectB,GroundTruth,Winner,Confidence,PositionFlip,Rationale
MAIN,"What is the limit of...","math","gpt-4o","gemini","A","B",true,false,"A","Model A",0.9,false,"Model A correctly applies L'Hopital's rule..."
```

---

## 💡 Best Practices for Research Runs

1. **Leverage the SQLite Cache**: Model traces are loaded from precomputed results folders, so running benchmarks incurs **zero model inference costs**. Judge responses are cached in the ratings database, meaning re-running a condition will not make duplicate LLM judge calls unless the prompts change.
2. **Use Canonical for Sanity Checks**: Running `CANONICAL` takes only seconds and executes locally without LLM APIs, making it excellent for verifying dataset setups and split sizes before initiating large LLM judging rounds.
3. **Regenerate Split once**: Set `regenerateSplit = true` only for the first run of a new dataset split to write the deterministic 70/30 split query IDs to `reserved_test_queries.json`. Keep it `false` on subsequent runs to ensure all conditions use the exact same test queries.
