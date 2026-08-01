# Consolidation: 5_Results.tex (2026-07-31)

Scope: `report/03_Content/5_Results.tex` only. No build run. No labels deleted or
renamed; no `\ref` target changed; no number, table value, figure, or caption touched.
Line count **1626 -> 1591**.

## Cuts per goal

**(a) §5.3.1 (sec:res-construction) overload.**
- "On R1" lead-in: cut "The floor is cheap to compute and it had not been"; dangling
  "gives:" before the float replaced by "gives Table~\ref{tab:j-floor}".
- Four-things paragraph (22 lines -> 12): deleted the "Four things follow, and the third
  is the one that matters most" announcement; deleted "and this is the objection a reader
  should raise before the second point is allowed to stand"; deleted the doubling/sub-split
  restatement (0.2538/0.1270/0.1260 and "granularity buys nothing" are fully carried by
  tab:j-floor and the R1 row of tab:requirements-evidence — one summarising clause points
  at the table rows). Kept the two facts the tables cannot carry: the estimator/implementation
  check and the +0.029 / +0.098 decomposition.
- Two-limits paragraph (10 -> 8): kept the 0.2538-vs-0.2531 transfer evidence (non-duplicative);
  cut "That second question is Section 5.3.4, **and its answer is not the convenient one**"
  (trailer clause) and the self-ref to sec:res-construction.
- "On R4" (22 -> 17): cut the opening normative restatement ("An acceptance rule ... must
  express the threshold in units of ..." and "about a tenth of a standard error", both carried
  by the R4 table cell incl. z = 0.089). Kept: raw ΔJ/SE pair (appears nowhere else), the
  incoherence argument, the 88τ measurement, and the gate aphorism — its ONLY occurrence
  (the other site was already just a pointer, now removed with the argued-paragraph rewrite).
- "On R2" (8 -> 8, tightened): "consequence ... rather than its target" -> "not its target".
- Gate-neutrality paragraph title shortened ("...and both were measured rather than assumed"
  dropped); body untouched (all numbers unique to it).
- Argued gate paragraph (8 -> 5): no longer re-argues the units case; points to "the On~R4
  paragraph above"; keeps the tested-and-failed-corroboration sentence.
- Certificate paragraph and stopping-rule paragraph left as instructed/substantive.
- Section prose loss ≈ 25% of the essay region; the remainder is protected (unique numbers,
  both tables, lead-ins, certificate paragraph).

**(b) Conventions box.** The chapter was already nearly clean — a prior pass evidently swept
it. Remaining mentions (tie conventions in tab:settled-recovery caption, grid-step/seed-spread
usages in sec:res-c5) are applications or captions, not re-explanations; left. Box lead-in
compressed ("none is weakened by not being repeated..." dropped). sec:res-tie-policy untouched.

**(c) Evidence-status table.** sec:res-runs withdrawal paragraph compressed: dropped
"deliberately absent, and their absence is itself part of the record" and "their role was
diagnostic, they produced no reportable results"; first use keeps "withdrawn in their
entirety" + pointer to tab:evidence-status. Other "withdrawn"/"superseded" uses are each the
first in their section (capture-gap owns the pilot; granularity/leaf-null withdrawals are
distinct draft-number withdrawals) — left.

**(d) Replay-design restatements.** sec:res-c5 opening compressed to "under the replay design
of Section~\ref{sec:res-runs}" + the arms-differ-in-more-than-rubric-text sentence (distinct
content). Full statement survives in sec:res-runs ("What paired means here") and captions.
No other full restatement found ("replaying these same triples" at the isolation-run sentence
is already one clause).

**(e) Answer-key-blind / 97.6%.** sec:res-judge-summary ladder: middle rung compressed to
"the options block is withheld but 97.6% of responses state their own selection
(Section~\ref{sec:res-correctness})". Canonical two-qualifications paragraph in
sec:res-correctness untouched. The 97.6% in the sec:res-runs batch descriptor is a run spec,
not a mechanism restatement — left.

**(f) Editorializing.**
- "It arrived from a direction nobody was looking in": **already absent** (removed in an
  earlier pass); the substance sentence (recorded for BT sufficient statistics, not as a
  test) is present in sec:res-tie-signature and kept.
- "Four things follow..." — deleted. "the objection a reader should raise..." — deleted,
  control stated directly. "its answer is not the convenient one" — deleted.
- Gate aphorism kept exactly once (On R4).
- Chapter intro: cut "That ordering is load-bearing rather than editorial", "interpretable
  instead of merely disappointing", "The partition finding has two parts...holds them together".
- Kept structural editorializing: "Three of these rows deserve a sentence rather than a
  table cell", "The sharpest of these is the third", the no-figure-is-deliberate paragraph,
  "the fifth error this apparatus caught in its own numbers".

**Rule 7 (aphorism enders).**
- sec:res-offsubject: cut "Whatever distance does to the judge, it does it with or without a
  rubric" — now ends on the −0.04 CI.
- sec:res-cost: cut "affordable for finding out who plays ... affording who wins" — now ends
  on "two orders of magnitude short, at this budget, in every cell of every domain".
- sec:res-judge-summary: cut trailing "and no result here should be read as if it had".
- Chapter closer double-colon rewritten as plain sentences.
- Only the gate aphorism survives.

**(g) "X rather than Y".** 29 instances at session start (the review's ~38 predates today's
other edits) -> 23 now, of which 3 are inside table cells (untouchable), 1 in a LaTeX comment,
and the rest load-bearing contrasts (e.g. "format rather than content", "withdrawn rather than
qualified", "measured from the edit rather than set in advance", "evaluation order rather than
by evidence"). Cut where decorative: intro, judge-summary lead, On R2, gate paragraph title,
four-things, adapted-partition "rather than for it".

**(h) Script paths.** Moved to footnotes: `discriminative_flatness.py` (first prose use;
second use -> "the same script"), `leaf_substructure_null.py`, `export_gt_scores.py`.
Paths in table footnotes and figure/table captions left per the caption convention
(tab:anchor-cells, tab:granularity note, tab:domain-screen note, all `make_*.py` captions).

**(i) Cross-ref density.** Remaining 3+-ref paragraphs are index-style (the offline-analyses
list in sec:res-runs, the composite in sec:res-judge-summary) where each ref is the pointer
to a distinct result — left intact.

**No-ai-slop pass.** Colon-setup "and this is the point:" trimmed (verdict style kept:
"\textsc{measured}: the judge does not care"); em-dash cluster in the sec:res-c5 argued
paragraph reduced (2 of 3 pairs -> parentheses/period); "fixed in writing ... fixed in
advance" repetition in sec:res-granularity deduplicated; double-colon chapter closer fixed.
Deliberate fragments and \textsc{measured}/\textsc{argued} verdict style untouched.

## Flagged, not touched
1. **"the disattenuated column moves the opposite way and clips past $1.0$"**
   (sec:res-granularity opening): tab:granularity contains no disattenuated column — likely a
   stale reference to a column removed in an earlier revision. Claim left as written.
2. **Stale 30-line comment block** at the head of sec:res-c5 (the "REMOVED 2026-07-31 ...
   TODO(author): rewrite from the 8-model RESOLVED batch" block): the TODO appears completed
   by the current section text. Invisible in the PDF; left for the author to delete.
3. tab:anchor-cells "run pool" column vs tab:run-record "routed questions" differ by 1–8 per
   domain (e.g. physics 237 vs 229) — internally explained by the caption (budget can end
   before every in-scope question is judged); consistent, no action.
4. The "two routing paths disagree / not diagnosed" paragraph is kept in full (open defect
   record, nothing duplicates it).

## Compressed content other chapters' \refs might expect in full
Any chapter that `\ref`s these labels expecting the full statement at that anchor should be
checked (the full statements now live where noted):
- `sec:res-c5` — no longer opens with the full replay/triples statement (full version:
  `sec:res-runs`, "What paired means here").
- `sec:res-judge-summary` — 97.6% mechanism now one clause + ref (full version:
  `sec:res-correctness`).
- `sec:res-construction` — J-floor doubling/sub-split argument now lives only in
  `tab:j-floor` + the R1 rows of `tab:requirements-evidence`; the normative gate-units
  argument now only in the R4 table row + the incoherence sentence of On R4.
- `sec:res-cost` / `sec:res-offsubject` — section-ending aphorisms removed; if Discussion
  quotes "who plays / who wins" or "with or without a rubric" verbatim, the quote source
  is gone.

No labels deleted; no \ref retargeted (one self-ref to sec:res-construction removed from
inside its own section; the label remains and is referenced elsewhere).
