# ROADMAP

Forward-looking work in priority order. M2/M3 status reflects June 2026 state.

---

## M3 — Implementation correctness (✅ COMPLETE)

All items closed. See commit `f241f4a` for items 5–6 (enableLabeling doc,
dimension fast-fail). Items 2–4 were already done before M3.

---

## M2 — Paper writing

### Code-side unblocking (must do before running experiments)

1. **Plumb per-query true-leaf GT** through `TaxonomyService` into the
   `computeHierarchicalF1` and `OverlappingNmi` call sites (`TaxonomyMetrics.kt`).
   Unblocks H-F1 and overlapping NMI showing real values. ~2h engineering.

### New metrics to implement

2. **Total Dasgupta cost** of the final tree — add to `TaxonomyMetrics` final report.
3. **Routing ECE** — add `RoutingDecision` log to `TaxonomyTrickler`; compute
   in `RoutingCalibration.kt`.
4. **Triplet accuracy** — add to `HierarchicalMetrics.kt`.
5. **Normalised Sackin index** — supplement / replace `equilibriumIndex` in
   `TaxonomyMetrics.kt`.

### Rename / documentation

6. **Rename `ACR` → `Exact-Match Ancestor Rate (EMAR)`** — code, TUI, paper.
7. **Formal definition for WLP and Contamination Ratio** — paper §6 only.

### Paper sections to write

8. See `docs/paper/MATHEMATICAL_FOUNDATIONS.md` — §3–§5 of the paper.
9. See `docs/paper/EVALUATION_METRICS.md` — §6 and appendix.
10. See `docs/paper/EMPIRICAL_PLAN.md` — baselines, ablation matrix, multi-seed.
11. See `docs/paper/PUBLICATION_HYGIENE.md` — citations, ethics, limitations.
12. See `docs/paper/REPRODUCIBILITY.md` — artifact checklist.

---

## M4 — Experiments (blocked on M2-1)

1. Wire GT plumbing (M2-1 above).
2. Run canonical config × 3 seeds (42, 137, 2048).
3. Run ablation matrix A1–A8 (see `EMPIRICAL_PLAN.md`).
4. Run at least one supervised baseline (HiAGM or HGCLR).
5. Run flat k-means null baseline.

---

## Ongoing investigations

- **Embedding contamination** — contamination ~16.8% invariant across params;
  probe: re-embed with `text-embedding-3-large` or `jina-embeddings-v3` to
  confirm if bottleneck is Qwen3-specific geometry.

- **Polyhierarchy-aware NMI** — current overlapping NMI still penalises
  polyhierarchy when GT is single-label. Explore BCubed F1 or set-valued LFK
  with aligned ID spaces.

- **Metrics dashboard split** — split TUI metrics report into "Quality targets"
  vs "Characterisation" sections in `BenchmarkPanel` / `ArenaPanel`.

- **MMLU-Pro 14-domain availability** — verify all 14 categories surface in the
  picker (was fixed in PR #69; retest with fresh cache wipe).
