# METRICS

The metric philosophy for TaxoArena. This is the most important reference for
the next agent before touching the metrics report.

## Design intent (verbatim)

> In TaxoArena, contamination and cross-domain leaf nodes are DESIRABLE. The DAG
> must produce granular, polyhierarchical leaves that capture nuanced midpoints
> between parent domains (e.g. a node living between Mathematics and Physics),
> so that trickling a query yields multiple specialised judge prompts — one per
> relevant nuance — rather than routing to coarse parent domains.

---

## Two categories

### Quality targets (aligned with goal — optimise upward)

- `edgeF1` — fraction of predicted parent→child edges matching gold taxonomy
- `kappaByDepth` (κ profile) — intra-cluster coherence signal
- `avgMatchCount` — confirms polyhierarchical routing is active (target > 1)
- `sphericalSilhouette` — cosine-distance silhouette on unit sphere
- `hF1` / `hPrecision` / `hRecall` — Hierarchical F (Kosmopoulos 2014); **reports
  0.0 until per-query GT plumbing is complete** (TODO at call site in
  `TaxonomyMetrics.kt`)
- `tripletAccuracy` — gold-free intrinsic quality; pending implementation
- `routingECE` — calibration of soft-routing probabilities; pending implementation
- `totalDasguptaCost` — theory-grounded cross-system comparison; pending implementation

### Characterisation (informational — do NOT optimise down)

- `nmi` — overlapping NMI (Lancichinetti et al. 2009); formula correct post PR #46;
  GT-covering TODO remains at call site
- `dendrogramPurity` — DAG-compatible shallowest-LCA variant (Monath 2021); PR #46
- `weightedLeafPurity` — custom metric; formal definition needed in paper
- `contaminationRatio` — ~16.8% invariant across runs; embedding-geometry bottleneck
- `ari` — flat partition comparison; penalises polyhierarchy by design
- `emar` (currently `acr`) — Exact-Match Ancestor Rate; rename pending
- `normalisedSackin` (currently `equilibriumIndex`) — supplement/replace Gini-of-leaf-sizes

These compare against single-category ground truth and will look "bad" precisely
when polyhierarchy is working.

---

## NMI specifics (post PR #46 / PR #68)

- **Current formula:** `OverlappingNmi.kt` — Lancichinetti, Fortunato & Kértesz 2009,
  `NMI_ovlp = 1 − [H(X|Y) + H(Y|X)]/2` with column-normalised fuzzy encoding.
- **Was previously:** `ShannonNmi.compute(gtSimple, predSimple)` (flat Shannon NMI
  on hard partitions) — incorrect for a DAG with overlapping assignments; fixed in
  PR #46.
- **Remaining TODO:** the GT domain-covering is not yet wired into the
  `OverlappingNmi` call site; NMI will report a partial value until that is done.
- **Known limitation:** even overlapping NMI penalises polyhierarchy when
  `gt_covering` is single-label. The future improvement is fully multi-label-aware NMI
  (BCubed, set-valued LFK). Tracked in ROADMAP.

---

## Run snapshots for reference

- **Run A** (min=25, ε=0.04, depth=10): 239 nodes / 123 leaves; Edge F1=0.9161;
  ARI=0.0845; NMI≈0.0 (pre-fix); contamination≈16.8%.
- **Run B** (min=50, ε=0.10, depth=5): 125 nodes / 66 leaves; Edge F1=0.9155;
  ARI=0.1462; NMI=0.0197 (pre-fix); contamination≈16.8%; κ at depth-5=75
  (vs depth-7 κ=44 in Run A).
- Edge F1≈0.92 stability across very different params → topology faithfulness is
  the algorithm's strong suit.
- Contamination invariant at ~16.8% across both runs is embedding-driven
  (Qwen3-embedding geometry bottleneck), not algorithm-driven.

---

## Full metric documentation

See `docs/paper/EVALUATION_METRICS.md` for complete definitions, formulas,
citations, and implementation status of every metric.
