# PR HISTORY

Tabular history of PRs that landed in this work block (#46–#71).

| PR # | Title | Key file(s) | Note |
| --- | --- | --- | --- |
| #46 | Overlapping NMI, DAG Dendrogram Purity, κ bias correction, Hierarchical F₁ | `TaxonomyMetrics.kt` | Initial metric suite. |
| #47 | TUI improvements — R-key judge, L-key expand, dataset cache detection, hotkey bar split | `taxonomy/tui` | TUI hotkeys + cache detect. |
| #48 | Plumb per-query true-leaf ground truth into NMI + Hierarchical F₁ | `TaxonomyMetrics.kt` | Ground-truth plumbing. |
| #49 | Publication-grade metrics: total Dasgupta cost, ECE, triplet accuracy, normalised Sackin | `TaxonomyMetrics.kt` | Added Dasgupta/ECE/triplet/Sackin. |
| #50 | Arena benchmark E2E test on reserved MMLU-Pro precomputed results + document ZIP schema | `taxonomy/arena` | E2E test + ZIP schema doc. |
| #51 | Restore LogsPanel live display + persist log trace in DAG snapshots | `taxonomy/tui/features/logs` | Live logs + snapshot trace. |
| #52 | Activate ECE with real ground truth (one-line follow-up to PR #48/#49) | `TaxonomyMetrics.kt` | ECE activation. |
| #53 | Fix type mismatch in computeRoutingECE call | `TaxonomyMetrics.kt` | Compile fix. |
| #54 | docs: reorganise context into docs/ + add Deterministic Build & Reproducibility section to README | `docs/`, `README.md` | Docs reorg. |
| #55 | Redesign TUI logging system: Compose-safe recomposition, full diagnostics, snapshot partitioning, generation-lifecycle hooks | `taxonomy/tui` | Logging redesign. |
| #56 | Rework Trickle Batch Benchmark with leaf-domain tagging and proper metrics | `taxonomy/tui/features/trickle` | Trickle benchmark rework. |
| #57 | Per-model eval ingestion picker + Arena O-key fix + better progress UX | `taxonomy/tui/features/arena` | Per-model picker. |
| #58 | Isolate TUI stdout (logback-spring.xml + stream redirect) + auto-save snapshot after generation | `logback-spring.xml` | Stdout isolation. |
| #59 | Fix TUI startup (ordering of jansi vs. stdout redirect) + clean application.yml | `application.yml` | Startup ordering. |
| #60 | Harden TUI startup with pre-flight TTY probe + loud non-interactive diagnostics | `taxonomy/tui` | TTY probe. |
| #61 | Remove unused spring-ai MCP server dep to fix silent TUI startup | `build.gradle.kts` | Dep removal. |
| #62 | Remove dangling autoconfigure exclude that killed JDK23/Windows startup | `application.yml` | Autoconfigure fix. |
| #63 | Revert PR #59 TUI stream ordering to the PR #58 working sequence | `taxonomy/tui` | Revert to #58 sequence. |
| #64 | Let Mosaic own the terminal — remove System.out/jansi interference (PR #58 root cause) | `taxonomy/tui` | Mosaic owns terminal. |
| #65 | Removed actuator/micrometer/opentelemetry/prometheus deps | `build.gradle.kts` | Spring bean deadlock fix. |
| #66 | `@Lazy(false)` on LogbackConfigurator + Windows `chcp 65001` | `LogbackConfigurator` | Logs panel + snapshot logs + UTF-8 glyphs. |
| #67 | Truncate Text inputs in Arena/Benchmark/Trickle/Snapshot panels | `taxonomy/tui/features` | Mosaic TextSurface Check-failed fix. |
| #68 | Fix NMI bug — replaced disjoint-cover LFK NMI with flat-partition Shannon NMI | `ShannonNmi.kt`, `ShannonNmiTest.kt`, `TaxonomyMetrics.kt` | See `docs/METRICS.md`. |
| #69 | Arena benchmark config dashboard (Models/Domains/Options/Start, Tab nav, V toggle SUMMARY↔STREAM) + 4 fixes | `ArenaPanel.kt`, `EmbeddingCache.kt`, `MMLUDatasetFetcher.kt` | DAG click row-offset (+2), restored scrollbars (Logs/AsciiTreeTable/NodeDetail), demoted "Generating new embedding" to DEBUG, MMLU-Pro cache requires all 14 categories before short-circuit. |
| #71 | Fix "Dataset download" progress bar showing `… / 2147483647 rows` | `MMLUDatasetFetcher.kt`, `TuiGatewayImpl.kt`, `MMLUDatasetFetcherProgressTest.kt` | Full-dataset pulls passed the `Int.MAX_VALUE` cap sentinel straight through to the progress `total`. Fetcher now reports `0` (unknown) for the unbounded sentinel via `resolveProgressTotal`, so the UI shows an indeterminate "Fetching… N rows" bar instead of dividing by `Int.MAX_VALUE`. |