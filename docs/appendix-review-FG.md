# Appendix review: F_Numerics.tex and G_Frozen_Taxonomy.tex

Date: 2026-07-31. Scope: `report/04_Appendix/F_Numerics.tex`,
`report/04_Appendix/G_Frozen_Taxonomy.tex`. Result: **zero edits to either
file** — every goal was already satisfied; this pass verified rather than
changed. No build was run.

## F_Numerics.tex (212 lines)

**Goal 1 — remove `\textsc{measured}`/`\textsc{argued}` tags: already done.**
Grep for `textsc|MEASURED|ARGUED` over the file returns nothing; the only
occurrence of the word "measured" is ordinary prose (line 198, "what is
measured instead is the dual-call agreement rate ..."). The tags were
evidently stripped in an earlier pass. (Note: `03_Content/5_Results.tex:730`
still contains a `\textsc{measured.}` tag — out of scope for this pass, left
untouched.)

**Goal 2 — the four derivations are all present and intact:**

- `sec:num-bessel` — log-Bessel via uniform asymptotic expansion, small-argument
  fallback, Bessel ratio + derivative for the Newton step.
- `sec:num-niw` — diagonal NiW conjugate update and Student-t predictive,
  with the honest note that the predictive is diagnostic-only.
- `sec:num-kde` — Silverman bandwidth, valley weight, gap guards.
- `sec:num-fisher` — observed Fisher information, rank completion, and the
  1/K² vs 1/K variance-bug derivation with the pilot damage census
  (45 of 176 at the floor, median 0.09, correct values 44–209x larger).

The census must stay: `03_Content/3_Method.tex:909` says "the damage census
are in Appendix~\ref{app:numerics}", and `04_Appendix/A_Tuning_Protocol.tex:230`
cites the over-subtraction result.

**Goal 3 — closing section carries no withdrawn-run numbers as current:
verified.** `app:not-implemented` (lines 184–211) contains only design
constants (1/k, 10.0 init, U_min, B_max) — no run results at all. The two
places withdrawn-run numbers do appear are outside that section and both are
explicitly framed as withdrawn/invalid, never current:

- `sec:num-kde` (lines 115–123): the leader-centric-star allocation is
  attributed to "the withdrawn runs that predate the variance fix".
- `sec:num-fisher` (lines 163–173): the pilot census is preceded by "No value
  computed under the wrong constant is a measurement either way" and points to
  `sec:disc-debt` for what may be quoted.

**Trim check:** nothing left to trim. Every paragraph either documents an
implemented computation, states an honest limitation, or is load-bearing for a
cross-reference from another chapter.

**Reference audit:** all 10 distinct outbound `\ref` targets resolve —
`ch:introduction`, `ch:methodology`, `app:dag-formalism`, `sec:meth-bt`,
`sec:res-cost`, `sec:disc-debt`, `sec:meth-assumptions`,
`sec:meth-not-implemented`, `sec:res-capture-gap`, `sec:meth-scheduling`.
All 5 labels defined in F (`app:numerics`, `sec:num-bessel`, `sec:num-niw`,
`sec:num-kde`, `sec:num-fisher`) are untouched; inbound references to
`app:numerics` exist from Introduction (1_Introduction.tex:144), Method
(3_Method.tex:307, 909), A_Tuning_Protocol (:230), and
E_Construction_Formalism (:388, :424, :905).

## G_Frozen_Taxonomy.tex (53 lines)

**Currency verified against three independent sources; no changes needed.**

- Config header `experiment_configs/freeze_mcs55.toml` confirms verbatim:
  snapshot `20260727_042523`, seed 42, minClusterSize 55, 154 nodes,
  87 leaves, max depth 6, mass 8299.00.
- Chapter 3 (`3_Method.tex:78, 118, 332–333, 348`) reports the same
  154 / 87 / 6 and "8{,}299 of 8{,}673 placed" — G's claim that
  Chapter~\ref{ch:methodology} reports 8,299 as the placed corpus is correct.
- Chapter 5 (`5_Results.tex:730–732, 828`) matches: 154 nodes, 87 leaves,
  depth 6, mass 8299.00, leaf median 88, minimum 54.

Internal arithmetic checks out: 154 = 1 root + 14 anchors + 139 split
children; 66 splits (60x2 + 5x3 + 1x4 = 139 children); membership sum
8299 + 826 + 2x8 = 9,141, matching the stated multi-membership counts.

Both figure PDFs exist and were not touched: `report/Figures/frozen_tree.pdf`
and `report/Figures/tree_full.pdf`. Labels `app:frozen-tree`,
`sec:tree-shape`, `sec:tree-full`, `fig:frozen-tree`, `fig:tree-full` are
intact; inbound references from `A_Tuning_Protocol.tex:13` and
`C_Metric_Definitions.tex:51` resolve. The membership caveat paragraph
(construction overlap withdrawn before scoring) is present and consistent
with `C_Metric_Definitions.tex:50` (AvgMatch = 1.101 = 9141/8299).

## Residual observations (out of scope, not acted on)

- `5_Results.tex:730` retains a `\textsc{measured.}` tag; if the tag-removal
  policy is global, that file needs the same pass.
- G's icicle caption says "before the maximum depth of~6"; the configured cap
  is `maxDepth = 8` and 6 is the *achieved* maximum. The sentence is accurate
  as written (6 is the tree's maximum depth) but could be misread as the cap.
  Left unchanged per the no-number-changes rule.
