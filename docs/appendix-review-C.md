# Appendix C review — C_Metric_Definitions.tex

Date: 2026-07-31. Scope: `report/04_Appendix/C_Metric_Definitions.tex` only. No builds run.

## Goal 1 — measured/argued tags

None existed. A grep for `\textsc{measured}` / `\textsc{argued}` / any `\textsc` in the
file returned nothing; the only hit for "measured" is plain prose inside the ECE defect
statement ("by an amount nobody has measured"), which is part of the canonical telling
and was left intact.

## Goal 2 — TODO resolved

The `TODO(author)` block (uncited construction metrics) was replaced by a `% RESOLVED
2026-07-31` comment recording the decision:

- **Kept in full:** Average Match Count (`sec:app-metrics-avgmatch`) — quoted by the
  frozen-tree certificate appendix (`app:frozen-tree`); Routing ECE
  (`sec:app-metrics-ece`) — canonical statement of the export defect, pointed to by
  the debt register (`sec:disc-debt`), Method ch. 3, Results ch. 5, Discussion ch. 6,
  and Appendix A.
- **Compressed to definition-plus-pointer (~4 lines each):**
  - Total Dasgupta Cost (`sec:app-metrics-dasgupta`): kept the closed form,
    `\parencite{dasgupta2016cost}`, and the distinction from the per-split acceptance
    test (`sec:meth-split`). Dropped the MRL-clipping rationale, intuition paragraph,
    and cross-configuration comparability discussion.
  - Leaf Purity pair (`sec:app-metrics-wlp`): kept one-sentence definitions of WLP and
    Dendrogram Purity, the pointer to `sec:poly-negative`, and the one-line
    complementarity reading. Dropped the display equations and the shallowest-LCA
    implementation note.
- Each compressed section carries a `% Compressed 2026-07-31 ... full text in this
  file's history` comment; recovery is via git history of this file (same as the
  earlier Silhouette/Sackin removals).
- Neither compressed section was cut outright because the hard rules forbid deleting
  labels, and `E_Construction_Formalism.tex:678` name-drops the Dasgupta metric via
  `\ref{app:metrics}`.

## Goal 3 — ECE defect statement

Untouched, byte-for-byte: the definition, "The exported number is not this metric"
paragraph, the 0.2114 diagnostic framing, and "This is the full statement of the
defect; the other places it is mentioned point here."

## Invariants checked

- All five labels preserved: `app:metrics`, `sec:app-metrics-dasgupta`,
  `sec:app-metrics-wlp`, `sec:app-metrics-avgmatch`, `sec:app-metrics-ece`.
- No numbers changed anywhere (9,141 / 8,299 / 1.101 / 0.2114 intact).
- No other file modified; no build run (author builds with `arara main.tex`).
- File shrank from 107 to ~78 lines.
