# ROADMAP

Forward-looking work the next agent should pick up, in priority order.

1. **Metrics dashboard split** — split the metrics report into "Quality targets" vs
   "Characterization" sections in the TUI; update labels in `BenchmarkPanel`/`ArenaPanel`
   and any markdown reports. Reflect the design intent in `docs/METRICS.md`.

2. **Polyhierarchy-aware NMI** — explore multi-label NMI variants (BCubed F1; LFK with
   aligned ID spaces and multi-label gt). Owner cares about whether a leaf living between
   Math/Physics is *rewarded*, not penalized.

3. **Embedding contamination investigation** — contamination is invariant at ~16.8%
   across very different algorithm params. Owner's hypothesis: qwen3-embedding is the
   bottleneck. Suggested probe: re-embed a held-out slice with a different model
   (e.g. text-embedding-3-large or jina-embeddings-v3) and re-run on identical params;
   if contamination drops, confirm.

4. **Dendrogram purity** — currently penalizes shallow trees by design; either replace
   with a depth-normalized variant or move it to Characterization (per #1).

5. **MMLU-Pro 14-domain availability** — verify all 14 categories surface in the picker
   (was a fix in PR #69 but should be retested with a fresh cache wipe).
