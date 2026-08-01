# Appendix A review — A_Tuning_Protocol.tex

Scope: `report/04_Appendix/A_Tuning_Protocol.tex` only. No builds run. No labels deleted or renamed (8 before, 8 after). No numbers changed anywhere.

## Line delta

348 -> 343 (net -5).

## Goal 1 — \textsc{measured}/\textsc{argued} tags

Zero tags present at start of pass (an earlier pass evidently removed them). One
grammatical residue of that removal found and repaired: the `minClusterSize`
paragraph read "...once granularity turned out to be evaluatively flat
(Section ref) made the choice free..." — now "...(Section ref), a result that
made the choice free; its value of $55$ was not selected by any sweep." No
other residue found.

## Goal 2 — outdated content

- **Registration-table caption** (tab:domain-registration): claimed "The
  outcome column is empty because..." while the column is in fact filled.
  Reworded the status marker only: the column "records status under the
  addendum rather than per-domain verdicts". Dates, threshold, and reference
  unchanged.
- Twelve-model numbers in the P4 addendum ($|\Delta\rho| \geq 0.007$, the
  +6.00/0.00 grid-step spread) are explicit correction history and were left
  verbatim. Registered predictions (P1–P5, P4 body) left unreworded per the
  registrations-are-historical rule.

## Goal 3 — trims

- **Ablations section**: compressed the withdrawn/historical paragraph
  (marginal-separation / branching-cap / k-fallback merged into one clause
  chain; nat-margin / cross-link / routing-temperature sentence tightened).
  The $d=256$ withdrawal and the qualitative branching-cap finding are kept
  verbatim in substance; still no withdrawn value quoted.
- Removed the `TODO(author)` comment about a pending current-parameter
  ablation — its content ("future work") is already stated in the L9 paragraph
  of Section sec:app-hyperparams.
- **Kept**: hyperparameter table, all four parameter-direction paragraphs, the
  L9/leakage-boundary paragraph, the registration table with its filled
  outcome column and both footnotes, P1–P5, the full corrections register
  (including the side-channel entry, which is part of the register), and the
  P4 addendum.

## Goal 4 — P5 / RESOLVED note

Survives, and is now stronger: it existed only as a LaTeX `% TODO` comment
(invisible in the PDF). Promoted to visible prose at the end of the P5
paragraph: the settled batch runs in `RESOLVED` mode, which is adjacent to but
not the registered options-blind arm, and no result reports it as satisfying
P5. Wording preserved in substance; no numbers involved.

## Flags for the parent

1. The prompt named the file at ~340 lines with tags present; the on-disk file
   had zero tags. If a tagged draft exists elsewhere, this pass did not see it
   — the only artifact of tag removal found was the one grammar break above.
2. Minor unresolved tension, deliberately left: the preamble of app:preregs
   says P4 was "amended through 2026-07-30, every amendment predating the runs
   it governs", while sec:prereg-addendum-p4 is dated 2026-07-31. Consistent if
   the 07-31 addendum is a retrospective withdrawal rather than an amendment,
   which is how the text frames it, so no edit made.
3. The side-channel paragraph in the corrections register affects no reported
   figure; kept because the task said to keep the corrections register, but it
   is the weakest-supporting passage if a further cut is wanted.
