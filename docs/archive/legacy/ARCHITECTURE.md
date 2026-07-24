# ARCHITECTURE

A short architectural map of TaxoArena. Source root: `src/main/kotlin/taxonomy`.

## Core packages

- `taxonomy.dataset` — MMLU-Pro fetcher, embedding cache (Qwen3-Embedding 4096-d MRL).
- `taxonomy.utils` — DAG construction, metrics, NMI/ARI/Edge F1 implementations.
- `taxonomy.tui` — Mosaic-based terminal UI; `tui.features.arena`, `tui.features.benchmark`, `tui.features.logs`, etc.
- `taxonomy.tui.state` — UI state holders (`BenchmarkUiState`, `ArenaUiState`).

## Key files

| Path | Role |
| --- | --- |
| `src/main/kotlin/taxonomy/utils/TaxonomyMetrics.kt` | Central metrics computation (entry: `generate(...)` ~ line 100, returns `Report`). |
| `src/main/kotlin/taxonomy/utils/ShannonNmi.kt` | Flat-partition Shannon NMI (Strehl-Ghosh symmetric, added PR #68). |
| `src/main/kotlin/taxonomy/utils/OverlappingNmi.kt` | LFK 2009 cover-based NMI; retained but no longer used for the headline `nmi` metric. |
| `src/main/kotlin/taxonomy/dataset/EmbeddingCache.kt` | Embedding cache; "Generating new embedding" log is DEBUG (PR #69). |
| `src/main/kotlin/taxonomy/dataset/MMLUDatasetFetcher.kt` | Requires all 14 MMLU-Pro categories before cache short-circuit (PR #69). Reports an unknown (0) progress total for unbounded full-dataset pulls instead of the `Int.MAX_VALUE` cap sentinel, so the TUI shows an indeterminate bar (PR #71). |
| `src/main/kotlin/taxonomy/tui/features/arena/ArenaPanel.kt` | Arena benchmark config dashboard (PR #69). |
| `src/main/kotlin/taxonomy/tui/features/benchmark/BenchmarkPanel.kt` | Extended for model/domain selection. |
| `src/main/kotlin/taxonomy/tui/state/BenchmarkUiState.kt` | Fields: `selectedModels`, `selectedDomains`, `activeSection`, `liveView` enum. |
