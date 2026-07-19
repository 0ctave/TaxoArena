<!--
SPDX-FileCopyrightText: 2025 Deutsche Telekom AG and others

SPDX-License-Identifier: CC0-1.0
-->
# TaxoArena Documentation

## Overview

**TaxoArena** builds a **Dynamic Hierarchical Directed Acyclic Graph (DAG)** taxonomy
directly from MMLU-Pro queries: questions are embedded with **Qwen3-Embedding**, clustered
into polyhierarchical domains via **von Mises–Fisher (vMF)** statistical modeling, and the
resulting leaf domains host **LLM-judge** pairwise comparisons whose verdicts feed an
**OpenSkill** ranking of the evaluated models. The result is a self-organizing,
geometrically coherent map of knowledge that doubles as a model-evaluation arena.

This directory is the single entry point for the full organized context of the project.

## Quick navigation

| Document | Description |
| --- | --- |
| [architecture/algorithm-foundations.md](architecture/algorithm-foundations.md) | Mathematical and algorithmic foundations of the taxonomy engine. |
| [architecture/clustering.md](architecture/clustering.md) | vMF clustering, splitting, and density-based domain discovery. |
| [architecture/judge-design.md](architecture/judge-design.md) | LLM-judge design: rubrics, pairwise prompts, confidence gating. |
| [architecture/topological-paradigms.md](architecture/topological-paradigms.md) | DAG topology, union-based domain definition, polyhierarchy. |
| [phases/phase2-fitting.md](phases/phase2-fitting.md) | Phase 2 — Fit: context-aware distribution modeling. |
| [phases/phase3-trickle.md](phases/phase3-trickle.md) | Phase 3 — Trickle: top-down restrictive routing. |
| [phases/phase4-discovery.md](phases/phase4-discovery.md) | Phase 4 — Discover: adaptive splitting. |
| [phases/phase5-optimization.md](phases/phase5-optimization.md) | Phase 5 — Optimize: structural refinement. |
| [phases/phase6-stabilization.md](phases/phase6-stabilization.md) | Phase 6 — Stabilize: convergence of the mixture. |
| [research/research-notes.md](research/research-notes.md) | Research notes and background literature pointers. |
| [guides/tui-report-generation.md](guides/tui-report-generation.md) | Generating reports from the AI-agent TUI. |
| [guides/eval-results-zip-schema.md](guides/eval-results-zip-schema.md) | Schema for precomputed MMLU-Pro eval-results ZIP/JSON (PR #50). |
| [agents/gemini.md](agents/gemini.md) | AI-assistant project mandates & implementation hub. |
| [reports/](reports/) | Placeholder for generated reports (empty for now). |

## Recommended reading order for new contributors

1. [architecture/algorithm-foundations.md](architecture/algorithm-foundations.md)
2. [architecture/clustering.md](architecture/clustering.md)
3. [architecture/judge-design.md](architecture/judge-design.md)
4. [architecture/topological-paradigms.md](architecture/topological-paradigms.md)
5. Phases, in order:
   [phase2-fitting](phases/phase2-fitting.md) →
   [phase3-trickle](phases/phase3-trickle.md) →
   [phase4-discovery](phases/phase4-discovery.md) →
   [phase5-optimization](phases/phase5-optimization.md) →
   [phase6-stabilization](phases/phase6-stabilization.md)
6. [guides/tui-report-generation.md](guides/tui-report-generation.md)
7. [guides/eval-results-zip-schema.md](guides/eval-results-zip-schema.md)

## External / Space documents

Additional context is maintained **outside this repository** in the project's Perplexity
Space and is not copied in here. These can be requested by their canonical filenames when
needed:

- `taxoarena-mathematical-validation-updated.md` — mathematical validation report.
- `taxoarena_literature_review.md` — literature review.
- `taxoarena_publication_readiness_checklist.md` — publication-readiness checklist.

## Recent PRs

- [#46](https://github.com/0ctave/TaxoArena/pull/46) — Overlapping NMI, DAG Dendrogram Purity, κ bias correction, Hierarchical F₁.
- [#47](https://github.com/0ctave/TaxoArena/pull/47) — TUI improvements: R-key judge, L-key expand, dataset-cache detection, hotkey bar split.
- [#48](https://github.com/0ctave/TaxoArena/pull/48) — Plumb per-query true-leaf ground truth into NMI + Hierarchical F₁.
- [#49](https://github.com/0ctave/TaxoArena/pull/49) — Publication-grade metrics: total Dasgupta cost, ECE, triplet accuracy, normalised Sackin.
- [#50](https://github.com/0ctave/TaxoArena/pull/50) — Arena benchmark E2E test on reserved MMLU-Pro precomputed results + ZIP schema doc.
- [#51](https://github.com/0ctave/TaxoArena/pull/51) — Restore LogsPanel live display + persist log trace in DAG snapshots.
- [#52](https://github.com/0ctave/TaxoArena/pull/52) — Activate ECE with real ground truth (follow-up to #48/#49).
