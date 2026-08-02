# TaxoArena

TaxoArena induces a semantic **tree** over MMLU-Pro questions from their embeddings, writes a
judging rubric for every terminal cell, and runs an LLM-as-a-judge pairwise arena inside those
cells. It is the system built and tested by the Master's thesis in [`report/`](report/)
(TU Berlin): the partition is the instrument, and the result is a measurement of the judge.

The construction fits von Mises–Fisher mixtures on the unit sphere, accepts splits through a
chance-corrected separation gate, and runs to a certified structural fixed point. The frozen
artifact behind every reported result is snapshot `20260727_042523_Headless_Run_Auto_ge`
(154 nodes, 87 leaves, J = 0.253129), and the settled arena results live in
[`experiment_results/r8/`](experiment_results/r8/README.md).

## Documentation

Three documents in [`docs/`](docs/README.md) carry the repository-level story:

| | |
|---|---|
| [docs/README.md](docs/README.md) | Orientation: layout, how to run, build rules |
| [docs/IMPLEMENTATION.md](docs/IMPLEMENTATION.md) | The system as built, id-space rules, known defects |
| [docs/RESULTS.md](docs/RESULTS.md) | The settled 8-domain / 8-model results, with artifact paths |

The thesis itself (`report/`, LaTeX) is the authoritative account.

## Getting started

Toolchain (pinned for deterministic execution): **JDK Temurin 21** (not ≥ 22; the Mosaic TUI
bindings require 21), **Kotlin 2.1.10**, **Gradle 8.10** via `./gradlew`, **Spring Boot 3.4.3**.

Credentials go in a `.env` file (read by `spring-dotenv`, never committed):

```bash
cp .env.example .env   # then fill in HUGGINGFACE_TOKEN, AZURE_AI_API_KEY, AZURE_AI_ENDPOINT, GEMINI_API_KEY
```

Common commands:

```bash
./gradlew test          # test suite (~30 s; slow harnesses live in `./gradlew calibration`)
./gradlew bootRun       # interactive TUI
./gradlew bootRun --args="--config experiment_configs/<run>.toml"   # headless run
```

Construction runs need the two local caches (`mmlu_pro_dataset_cache_v2.db`,
`embeddings_cache.db`); they are not in git. With them in place, a clean clone reproduces the
frozen construction exactly (verified 2026-08-02).
