<!--
SPDX-FileCopyrightText: 2023 Deutsche Telekom AG

SPDX-License-Identifier: CC0-1.0    
-->
# 🌌 TaxoArena: Dynamic Hierarchical DAG Taxonomy for Model Evaluation

**TaxoArena** builds a **Dynamic Hierarchical Directed Acyclic Graph (DAG)** taxonomy directly from MMLU-Pro query distributions. Questions are embedded, mapped, and clustered into polyhierarchical domains using spherical statistical modeling. Within this taxonomy, leaf nodes host **LLM-judge** pairwise matchups to maintain local model leaderboards fitted using the Bradley-Terry probabilistic model. The result is a self-organizing, geometrically coherent map of knowledge that doubles as an active model-evaluation arena.

---

## 🚀 Key Features

*   **Self-Organizing Polyhierarchy**: Iteratively groups query embeddings on the unit sphere via von Mises–Fisher (vMF) GMMs, performing PCA bisections validated by Dasgupta split criteria.
*   **Active Dueling Matchmaker**: Prioritizes model comparisons using expected Shannon entropy and rating uncertainty (Fisher standard errors) to minimize evaluation query budget.
*   **Bayesian Rating Engine**: Updates model strengths dynamically using confidence-gated Weng-Lin updates, propagating domain-specific wins/losses/ties to ancestor categories.
*   **Interactive Terminal UI**: A real-time Compose-based TUI console featuring a live benchmark leaderboard, node-specific evaluations, metrics dashboard, and system logs.
*   **Production-Grade Architecture**: Powered by Spring Boot WebFlux, thread-safe asynchronous Kotlin Coroutine dispatchers, and concurrent SQLite WAL database backends.

---

## 📖 Project Documentation

The complete technical context and mathematical specifications live under the [`docs/`](docs/README.md) directory.

### Quick Sitemap
*   **[Core Concepts](docs/core-concepts/README.md)**: [Taxonomy DAG Topology](docs/core-concepts/taxonomy-dag.md) & [Data Schemas](docs/core-concepts/data-representations.md)
*   **[Evolutionary Pipeline](docs/evolutionary-pipeline/README.md)**: [vMF GMM Fitting](docs/evolutionary-pipeline/fitting-vmf.md), [Trickle Routing](docs/evolutionary-pipeline/trickle-routing.md), & [Discovery Splits](docs/evolutionary-pipeline/discovery-optimization.md)
*   **[Arena Evaluations](docs/arena-evaluations/README.md)**: [Judge Design](docs/arena-evaluations/judge-design.md), [Bradley-Terry fit](docs/arena-evaluations/bradley-terry-fit.md), & [Active Matchmaking](docs/arena-evaluations/active-matchmaking.md)
*   **[Validation Metrics](docs/metrics-validation/README.md)**: [Clustering](docs/metrics-validation/clustering-metrics.md), [Classification (ECE / H-F1)](docs/metrics-validation/classification-metrics.md), & [Structural Balance](docs/metrics-validation/structural-metrics.md)
*   **[System Architecture](docs/system-architecture/README.md)**: [Compose TUI Dashboard](docs/system-architecture/tui-dashboard.md), [Spring Engine](docs/system-architecture/spring-integration.md), & [SQLite Concurrency](docs/system-architecture/database-concurrency.md)

---

## 🛠️ Getting Started

### 1. Requirements & Toolchain
The build is pinned to exact toolchain versions for deterministic execution:
*   **JDK**: Temurin 21 (Compose-Mosaic layout terminal bindings require JDK 21). *Do not run with JDK ≥ 22*.
*   **Kotlin**: 2.1.10
*   **Gradle**: 8.10 (bootstrap via `./gradlew`)
*   **Spring Boot**: 3.4.3 (WebFlux)

### 2. Configure Environment Secrets
Create a `.env` file at the root of the project to set your credentials (read automatically by `spring-dotenv`):
```bash
cp .env.example .env
```
Fill in the values in your `.env` file:
```env
HUGGINGFACE_TOKEN=hf_your_huggingface_token
AZURE_AI_API_KEY=your_azure_api_key
AZURE_AI_ENDPOINT=https://your-resource.services.ai.azure.com/
GEMINI_API_KEY=your_gemini_api_key
```
*Note: If Azure credentials are left blank, the system automatically falls back to local Ollama endpoints.*

### 3. Basic Commands
*   **Build the codebase**:
    ```bash
    ./gradlew compileKotlin compileTestKotlin
    ```
*   **Execute tests**:
    ```bash
    ./gradlew test
    ```
*   **Run the application**:
    ```bash
    ./gradlew bootRun
    ```

---

## 🤝 Code of Conduct & Licensing

This project follows the [REUSE standard for software licensing](https://reuse.software/). Each file contains copyright and license information, and license texts can be found in the [./LICENSES](./LICENSES) folder.

All contributors must abide by the project's [Code of Conduct](./CODE_OF_CONDUCT.md).