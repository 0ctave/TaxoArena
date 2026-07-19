# Thesis Reproduction Guide: End-to-End Experimental Protocol

This guide outlines the step-by-step protocol for reproducing all experimental results, leaderboards, and statistical analyses reported in Chapter 6 (Results) of your Master's Thesis. 

By executing this pipeline, you will:
1. Construct the canonical **Taxonomy DAG** using seed-guided Von Mises-Fisher (vMF) soft splitting and trickle routing.
2. Automatically generate three structural baseline snapshots: **Flat k-means (k=17)**, **HAC Ward (cut=17)**, and **Random Null (shuffled query topology)**.
3. Run the complete evaluation matrix back-to-back under different scheduling strategies and judge prompting paradigms.
4. Export all structural validation metrics, rank correlation coefficients (Spearman's $\rho$, Kendall's $\tau$), bootstrap confidence intervals, and publication-ready LaTeX tables.

---

## 📊 Experimental Setup & Conditions

The experiments isolate specific contributions of your methodology by comparing the following conditions sequentially:

### 1. Taxonomy Structure & Prompting Conditions
- **`MAIN` (C1 / Canonical)**: Runs the active matchmaking scheduler using entropy maximization under the **domain-adapted leaf judge** prompts and contrastive leaf rubrics generated via prompt induction.
- **`C3` (Ablated Persona)**: Runs a replay of the exact same query-model triples evaluated in `C1`, but swaps out the custom MapReduce contrastive leaf rubric for a **generic rubric template**, isolating the effect of the contrastive guidelines.
- **`C5` (FastChat pair-v2)**: Runs a replay of `C1` triples using the verbatim, static **FastChat pair-v2 system prompt** (plain-text LLM query mode parsing bracketed `[[A]]`, `[[B]]`, or `[[C]]` winners), serving as the standard LLM-arena baseline.

### 2. Scheduler Ablations
- **`RANDOM_SCHEDULER`**: Replaces the entropy-maximization active matchmaking scheduler with **uniform random matchmaking**, assessing the efficiency gains of active scheduling at matched correlation.
- **`ROUND_ROBIN`**: Iterates through all possible model pairs $\times$ all queries in the test set without active stopping or early convergence, serving as the brute-force oracle baseline.

### 3. Baseline Taxonomy Topologies
- **`KMEANS_BASELINE`**: Re-evaluates model rankings on a flat taxonomy where queries are clustered into 17 categories using **Spherical k-means** on Qwen3 embeddings.
- **`WARD_BASELINE`**: Re-evaluates model rankings on a flat taxonomy where queries are clustered into 17 categories using **Hierarchical Agglomerative Clustering (HAC)** with Ward linkage.
- **`RANDOMNULL_BASELINE`**: Shuffles the query assignments of your Taxonomy DAG while preserving the exact node sizes and structural topology, verifying that semantic grouping governs rank correlation.

---

## ⚙️ Step-by-Step Replication Protocol

### Step 1: Configure the Pipeline TOML
To reproduce the primary thesis results, configure `experiment_pipeline_config.toml` in your project root with the following parameters:

```toml
# experiment_pipeline_config_full.toml
datasetType = "MMLU_PRO"

# The models to compare (must match entries in the eval_results table)
models = [
    "gpt-4o-2024-08-06",
    "gemini-1.5-pro-002",
    "Meta-Llama-3-70B-Instruct"
]

# Primary thesis domain configuration
queryLimit = 0            # 0 runs all available queries in the domain
category = "math"         # Math sub-corpus of MMLU-Pro

# Conditions to run back-to-back
conditions = [
    "MAIN",
    "C3",
    "C5",
    "RANDOM_SCHEDULER",
    "ROUND_ROBIN",
    "KMEANS_BASELINE",
    "WARD_BASELINE",
    "RANDOMNULL_BASELINE"
]

outputDir = "experiment_results"

# 70/30 stratified train/test split protocol
testRatio = 0.3
seed = 42

# Pipeline execution controls
runPipeline = true        # Runs GMM splitting and trickle routing from scratch
judgeInduction = true     # Generates contrastive leaf judge prompts

# Topology constraints
maxDepth = 3
minClusterSize = 15
separationEpsilon = 0.08
cosineTau = 2.0
assignmentGap = 0.2
emaAlpha = 0.5
enableLabeling = true
```

### Headless Configuration Parameters Reference

The following table provides a comprehensive reference for all options available in `experiment_pipeline_config_full.toml`:

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| **`datasetType`** | String | `MMLU_PRO` | Dataset type to fetch. Supports `MMLU_PRO` and legacy formats. |
| **`category`** | String | *null* | The MMLU-Pro sub-category / domain to load (e.g., `"math"`, `"physics"`). |
| **`domains`** | List of Strings | `[]` | List of target domains to load (alternative to `category` when running multiple domains). |
| **`models`** | List of Strings | `[]` | Roster of model names to evaluate (must exactly match entries in `eval_results` table in `mmlu_pro_dataset_cache_v2.db`). |
| **`conditions`** | List of Strings | `[]` | Sequential conditions to evaluate (supports: `MAIN`, `C3`, `C5`, `RANDOM_SCHEDULER`, `ROUND_ROBIN`, `KMEANS_BASELINE`, `WARD_BASELINE`, `RANDOMNULL_BASELINE`). |
| **`outputDir`** | String | `experiment_results_old` | Target directory where validation CSVs, JSONs, and LaTeX leaderboards are saved. |
| **`runPipeline`** | Boolean | `true` | When `true`, constructs the taxonomy DAG from scratch using GMM splitting and trickle routing. |
| **`judgeInduction`** | Boolean | `true` | When `true`, runs MapReduce prompt induction to generate custom, contrastive leaf judge prompts. |
| **`runBenchmark`** | Boolean | `true` | When `true`, executes the back-to-back benchmarking evaluations for each condition in `conditions`. |
| **`runTrickle`** | Boolean | `false` | When `true`, runs additional trickle routing validation tests. |
| **`testRatio`** | Double | `0.3` | The ratio of queries reserved for the evaluation test set (e.g., `0.3` for a 70/30 train/test split). |
| **`seed`** | Long | `42` | Random seed for deterministic data splitting and reproducible results. |
| **`regenerateSplit`** | Boolean | `false` | Forces train/test split regeneration when booting from a pre-existing `snapshotId`. |
| **`snapshotId`** | String | `unsaved` | Pre-existing snapshot ID to load when `runPipeline = false`. |
| **`queryLimit`** | Integer | `0` | Max test queries to evaluate per condition (set `0` to run all available test queries). |
| **`confidenceGate`** | Double | `0.65` | Confidence gate for judge matchmaking evaluations. |
| **`parallelism`** | Integer | `6` | Concurrency limit (number of parallel coroutines) for running LLM judge evaluations. |
| **`questionsPerRound`** | Integer | `12` | Batch size of queries adjudicated in each active matchmaking round. |
| **`reservedOnly`** | Boolean | `true` | If `true`, restricts evaluations to `Q_test` (preserving strict training/testing separation). |
| **`enableLabeling`** | Boolean | `true` | Enables post-evolution LLM synthesis of semantic node labels. |
| **`maxDepth`** | Integer | `3` | Maximum depth allowed for the generated Taxonomy DAG tree structure. |
| **`minClusterSize`** | Integer | `15` | Minimum number of queries required to form a distinct category leaf node. |
| **`separationEpsilon`** | Double | `0.08` | Separation margin threshold between cluster centroids. |
| **`cosineTau`** | Double | `2.0` | Soft-clustering cosine temperature scaling parameter ($\tau$). |
| **`assignmentGap`** | Double | `0.2` | Minimum gap constraint for hard cluster assignment boundaries. |
| **`emaAlpha`** | Double | `0.5` | Exponential moving average rate ($\alpha$) for centering cluster updates. |

---

### Step 2: Generate the Dataset Split and Taxonomy
Run the boot task passing the config file to initiate the GMM splitting, trickle routing, judge prompt induction, and database logging:

```bash
./gradlew bootRun --args="--config experiment_pipeline_config.toml"
```

> [!NOTE]
> Setting `runPipeline = true` on the first execution generates the taxonomy DAG, saves it to `snapshots.db`, generates the stratified 30% test split, and writes the test query IDs to `reserved_test_queries.json`. 
>
> On subsequent evaluation runs, set `runPipeline = false` and pass the generated `snapshotId` (e.g. `20260717_021530_Headless_Run`) to ensure the exact same taxonomy structure and test pool are reused without regeneration.

### Step 3: Automated Baseline Generation (Under the Hood)
When the pipeline starts with `runPipeline = true`, it automatically invokes the Python script [generate_baselines.py](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/scripts/generate_baselines.py) as a subprocess. This script:
1. Loads the Qwen3 embeddings for all queries in the dataset from `embeddings_cache.db` (handling big-endian JVM binary byte order).
2. Normalizes and clusters the embeddings using `scikit-learn` KMeans ($k=17$) and AgglomerativeClustering with Ward linkage.
3. Generates the flat structures and centroid vectors, saving `_baseline_kmeans`, `_baseline_ward`, and `_baseline_randomnull` graphs as snapshot entries in `snapshots.db` under the base snapshot prefix.

### Step 4: Back-to-Back Condition Benchmarking
The headless runner will execute each condition sequentially, routing queries, launching parallel judge API calls (if not cached), fitting Bradley-Terry ratings locally, and logging the convergence path.

---

## 📂 Exported Metrics & Thesis Visualizations

All results are written to `../../experiment_results_old/validation/` and `../../experiment_results_old/judging/`. Use these files to compile the figures and tables in your thesis:

### 1. Complete Structural & Validation Metrics (`validation/${condition}_thesis_metrics.csv` & `.json`)
This is the primary file containing all metrics required for **Table 6.1 (Structural parameters)** and **Table 6.2 (Rank correlation coefficients)** in your thesis:

- **Structural metrics (Taxonomy DAG vs. Baselines)**:
  - `totalNodes`, `leafNodes`: Verifies the scale of the taxonomy.
  - `avgLeafDepth`, `maxDepth`: Tracks structural hierarchy.
  - `nmi` (Normalized Mutual Information), `ari` (Adjusted Rand Index): Assesses cluster similarity.
  - `dendrogramPurity`, `weightedLeafPurity`: Evaluates classification hierarchy.
  - `sphericalSilhouette`: Computes geometric clustering quality on the unit sphere.
  - `totalDasguptaCost`: Computes hierarchical cost (lower is better).
  - `normalisedSackin`: Computes topological tree balance.
  - `routingECE` (Routing Expected Calibration Error): Evaluates soft-routing calibration.
- **Rank Validation metrics (vs. Ground-Truth accuracy)**:
  - `overallSpearmanRho` ($\rho$): Primary correlation metric.
  - `overallSpearmanCiLow`, `overallSpearmanCiHigh`: 2,000-resample bootstrap percentile confidence intervals.
  - `overallKendallTau` ($\tau$): Secondary correlation metric.
  - `overallKendallCiLow`, `overallKendallCiHigh`: Bootstrap confidence intervals.
  - `overallPairwiseWinnerAccuracy`: Evaluates pairwise agreement on win/loss direction.
  - `overallTopKJaccard`: Jaccard index of the top-$k$ models.

### 2. Bootstrap Domain Details (`validation/${condition}_domain_validation_details.csv`)
Logs correlation coefficients and bootstrap confidence intervals for individual sub-domains (leaves) within the taxonomy:
```csv
Condition,Domain,SpearmanRho,SpearmanCiLow,SpearmanCiHigh,KendallTau,KendallCiLow,KendallCiHigh,PairwiseWinnerAccuracy,TopKJaccard
MAIN,Calculus,0.92,0.85,0.98,0.88,0.76,0.95,0.84,0.75
```
Use this to analyze which sub-domains exhibit the highest alignment and how tight the confidence bounds are.

### 3. LaTeX Leaderboard Table (`validation/${condition}_latex_leaderboard.tex`)
A pre-formatted, publication-ready LaTeX table containing the final model ratings, standard errors, and rankings for direct copy-paste into `6_Results.tex`:
```latex
\begin{table}[h]
\centering
\caption{Bradley-Terry ratings for condition MAIN.}
\begin{tabular}{rllc}
\toprule
Rank & Model & BT Score & Std Error \\
\midrule
1 & gpt-4o-2024-08-06 & +1.520 & 0.124 \\
2 & gemini-1.5-pro-002 & +0.814 & 0.135 \\
3 & Meta-Llama-3-70B-Instruct & +0.000 & 0.150 \\
\bottomrule
\end{tabular}
\end{table}
```

### 4. Complete Audit Trail (`judging/${condition}_verdicts.csv`)
Contains the complete row-by-row adjudication database of every match (questions, answers, correctness indicators, judge explanations, confidence scores, and position-flip indicators). Use this to extract qualitative examples of the LLM judge's reasoning for your Discussion chapter (`7_Discussion.tex`).
