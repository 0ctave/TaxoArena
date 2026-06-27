# METRICS

The metric philosophy for TaxoArena. This is the most important reference for the
next agent before touching the metrics report.

## Design intent (verbatim)

> In TaxoArena, contamination and cross-domain leaf nodes are DESIRABLE. The DAG must produce granular, polyhierarchical leaves that capture nuanced midpoints between parent domains (e.g. a node living between Mathematics and Physics), so that trickling a query yields multiple specialized judge prompts — one per relevant nuance — rather than routing to coarse parent domains.

## Two categories

### Quality targets (aligned with goal — optimize)

- `edgeF1`
- `kappaByDepth` (κ profile)
- `avgMatchCount`
- `sphericalSilhouette`
- `tripletAccuracy`
- `hF1` (when ground truth is multi-label aware)

### Characterization (informational — do NOT optimize down)

- `nmi`
- `dendrogramPurity`
- `weightedLeafPurity`
- `contaminationRatio`
- `ari`

These compare against single-category ground truth and will look "bad" precisely
when polyhierarchy is working.

## NMI specifics (post PR #68)

- Current implementation: `ShannonNmi.compute(gtSimple, predSimple)` — symmetric
  `MI / sqrt(H(X)·H(Y))` on flat hard partitions.
- Was previously `OverlappingNmi.compute(...)` over two coverings in disjoint
  node-ID spaces, which collapsed the LFK 2009 score to ~0; the fix landed in PR #68.
- **Known limitation**: even Shannon NMI on flat partitions penalizes polyhierarchy
  because `gtSimple` is single-label. A future improvement is multi-label-aware NMI
  (BCubed, set-valued LFK with aligned ID spaces). Tracked in ROADMAP.

## Run snapshot for reference

- **Run A** (min=25, ε=0.04, depth=10): 239 nodes / 123 leaves; Edge F1=0.9161;
  ARI=0.0845; NMI=0.0 (pre-fix); contamination ≈ 16.8%.
- **Run B** (min=50, ε=0.10, depth=5): 125 nodes / 66 leaves; Edge F1=0.9155;
  ARI=0.1462; NMI=0.0197 (pre-fix); contamination ≈ 16.8%; κ at depth-5 = 75
  (vs depth-7 κ=44 in Run A).
- Edge F1 ≈ 0.92 stability across very different params → algorithm's topology
  faithfulness is its strong suit.
- Contamination invariant at ~16.8% across both runs is embedding-driven
  (qwen3-embedding bottleneck), not algorithm-driven.
