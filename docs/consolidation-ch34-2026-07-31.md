# Consolidation report: Chapters 3 and 4 (2026-07-31)

Scope: `report/03_Content/3_Method.tex` and
`report/03_Content/4_Experimental_Design.tex` only. No build was run. No
`\label` was deleted or renamed; no `\ref` retargeted. No number, table
value, or claim was changed — only cut or demoted to a forward reference
where the goal letter called for it.

Note on diffs: both files carry large pre-existing uncommitted changes
from the author's chapter reorganisation (3_Method carries a
"was 4_Methodology.tex; merged 2026-07-31" marker), so `git diff`
against HEAD is NOT a view of this pass. The edits of this pass are
itemised below.

---

## 3_Method.tex — 1,250 lines before, 1,229 after

(Net −21; prose shrank by roughly 55 lines, ~34 lines of that returned
as `% MOVED-CANDIDATE` comments under goal (d).)

### (a) Result-level numbers demoted to forward references
- **863/868 capture figure** (arena overview): mechanism sentence kept
  (trace accessor never returns empty string, synthesises a stub); the
  measurement replaced with "the measured size of the judge's
  preference for the text-bearing side is
  Section~\ref{sec:res-capture-gap}". The follow-on sentence ("That
  measurement is why the settled roster admits no majority-bare
  model") kept unchanged.
- **2.91× / 6.79× length-matching figures** (same paragraph): dropped;
  sentence now says the roster's length-matching sacrifice "is stated"
  in Appendix~\ref{app:models} and Section~\ref{sec:disc-debt}, where
  those numbers already live (6.79× also remains stated in
  4_Experimental_Design §Rosters — that occurrence untouched, it is
  roster description in the chapter that owns the roster).
- **49.7%–94.6% adapted-vs-canonical agreement** (Notation paragraph):
  demoted to "the per-domain agreement between them is
  Section~\ref{sec:res-adapted-partition}".
- **Pilot SE census (176 stored / 45 at floor / median 0.09 / 44–209×
  larger)**: removed as part of the goal-(c) compression; see below.
- Design-motivating constants kept as instructed: 308-slot arithmetic,
  budget clamp [8,25], resolution-at-9-comparisons, physics quota
  motivation (9.2–11.3% vs 5.6–17.8%), bootstrap-SE failure (0.0010 vs
  0.4642), cost formulas.

### (b) \textsc{measured}/\textsc{argued} tags
Only one occurrence existed (Section "What a Good Partition Needs"):
"each marked \textsc{measured} or \textsc{argued}". **Left in place**
— it does not tag a claim in this chapter; it describes the format of
the Chapter 5 evidence table (`tab:requirements-evidence`), i.e. it is
part of explaining the system the tags belong to. Flagging for the
coordinator in case the review wanted even this mention gone.

### (c) Variance-bug story (1/K vs 1/K²)
The two paragraphs after "One correction, and what it left behind"
(≈30 lines) compressed to one paragraph (~13 lines): the bug in one
sentence, the no-intervals-anywhere consequence in one sentence, and
pointers to Appendix~\ref{app:numerics}, the debt register
(Section~\ref{sec:disc-debt}), and the corrections register
(Appendix~\ref{app:corrections-register}). The corrected formula
survives: "subtracting $1/K^{2}$ from each diagonal entry" is stated in
the preceding per-cell standard-error paragraph, which was not touched.
**Coordinator check**: the pilot damage census (176 / 45 at floor /
median 0.09 / 44–209×) and the $(K-1)/K^{2} = 0.109$ arithmetic now
appear nowhere in this chapter — confirm Chapter 6's debt register (or
App. numerics) actually carries them, as the review assumed.

### (d) D-rule war stories: one instance per rule
Moved to `% MOVED-CANDIDATE` comments (text preserved verbatim, marked
for relocation to the corrections register):
- **D1**: footnote (identifier-column set-membership audit, ~100%
  everywhere).
- **D2**: footnote ("0 of 36 rescues" join on a hardcoded −1 counter;
  0/613 → 97/613; 3 rescues in 404).
- **D3**: the second inline instance (CV rose mechanically because the
  mean fell). D3 keeps the SE(ΔJ) order-of-magnitude instance.
- **D4**: footnote (level-vs-difference constant; float tolerance
  doing double duty).
- **D5**: had one instance; untouched.

### (e) Throat-clearers removed (3)
- "The corpus counts are worth stating once, because…" → "Three
  different totals appear in the artefacts, and only one of them is
  the corpus."
- "its size is worth carrying here" → gone (absorbed by the (a)
  demotion).
- "That has a cost, and it is worth stating plainly because the rubric
  is the treatment…" → "That has a cost, and the rubric is the
  treatment this thesis is about."
- Also: "for two reasons that are worth separating" → "for two
  reasons." (The tikz label "Condition 2: worth the edit" is a figure
  caption device, left alone.)

### (f) "X rather than Y": 37 → 28
Cut or restructured (9): "rather than collected as limitations
afterwards"; "rather than from all of them" (rubric sample); "rather
than sitting before or after it" (brackets); "so that a tie is
modelled rather than split" (Davidson); "rather than being topped up…"
(restructured to a plain causal sentence); "rather than bootstrapped";
"rather than against an interval" and "rather than fitter output"
(both inside the goal-(c) compression); "paired contrast rather than
an interval" (assumptions section).
Kept 28 deliberately — the remainder are load-bearing contrasts of the
"verified rather than asserted" family (e.g. "audited rather than
asserted", "forced rather than chosen", "a result rather than an
assumption", "complete rather than merely connected", "recognising a
question rather than assessing an answer", the 1/K-vs-1/K² bug
statement itself). Halving further would have cut findings-as-contrast,
which rule 5 protects. Under-delivered against the "roughly halve"
target on purpose; the review's decorative examples are all gone.

### (g) Cross-reference density
The 3+-ref paragraphs remaining are deliberate pointer maps (the
chapter roadmap; "the formalism … are given in full in
App. A/B; how the parameters were arrived at is App. C"; the
compressed correction paragraph's three registers). One real reduction:
the arena-overview roster sentence went from 4 refs + 2 quoted numbers
to 2 refs.

### (h) Inline engineering artifacts
None found in prose (the `.kt` file/line references live inside
existing `% TODO(author)` comments, which were left untouched). The
`experiment_configs/freeze_mcs55.toml` entry is a value inside the
frozen-artifact table (it *is* the artifact identity) and stays.

---

## 4_Experimental_Design.tex — 663 lines before, 660 after

### (a) Δρ-withdrawal told once
- Run-conditions paragraph (first mention, full withdrawal story with
  the six-and-zero-grid-steps evidence): **kept in full**.
- Metrics section: kept the seam explanation (0.007 vs two grid steps,
  seven millionths — unique content) and the no-decision rule; the
  duplicated seed-replicate story replaced by "did not survive the
  seed replicate of Section~\ref{sec:exp-rqmap}". The author's
  `% TODO(author): cite the replicate` comment kept.
- Pre-registration entry: now one clause — "$|\Delta\rho| \geq 0.007$,
  since withdrawn (Appendix~\ref{app:preregs}, addendum to P4)".

### (b) Replay statement told once
- Run-conditions paragraph: full statement **kept**.
- Schematic caption + figure annotations: **kept** (self-contained).
- Conditions table row for C5: kept (it is the condition's
  definition).
- Conditions prose after the table: "it replays the identical (cell,
  pair, question) triples under MAIN's cells, and pooling…" → "under
  the replay design of Section~\ref{sec:exp-rqmap}, pooling…".
- Pairing paragraph: "Both arms … judge an identical question set ---
  the replay design of Section~\ref{sec:exp-rqmap}."; "replaying one
  arm's comparisons in the other" → "replay".

### (c) "No condition removes the partition"
Full statement with the what-a-real-no-partition-arm-would-be
explanation kept in the conditions prose; caption one-liner kept; the
table's "\textbf{not} the partition" kept (already one clause). No
other occurrence found.

### (d) Commit hashes
`5e1be09` / `a5c36fd` moved to a footnote; prose now names the two
scheduler repairs descriptively.

### (e) Same treatments as file 1
- Throat-clearers: "a limitation worth naming" → "a limitation";
  "and it is worth stating in the exact scope the code enforces" →
  "in exactly the scope the code enforces".
- rather-than: 14 → 13 (cut "rather than accept it"). The rest are
  load-bearing ("stated rather than laundered", "verified by
  measurement rather than by the assertion alone", "a ceiling …
  rather than a prediction", etc.).
- No \textsc{measured}/\textsc{argued} tags existed in this file.
- Bonus under the (h) spirit: `tools/analysis/export_gt_scores.py` /
  `model_domain_scores.csv` moved from prose to a footnote
  (ground-truth accuracy paragraph). Revert if unwanted — goal (h) was
  formally scoped to file 1.

### Defect found and repaired (not a prose edit)
Line 479 contained a raw carriage-return byte (0x0D) where the
backslash of `\ref{app:preregs}` should be — the source read
`Appendix~<CR>ef{app:preregs}` and would have typeset
"Appendix efapp:preregs" silently. Fixed at byte level to
`Appendix~\ref{app:preregs}`. (An intermediate perl attempt briefly
converted the file to CRLF; it was restored to LF throughout and
verified with `file` + a zero-CR assertion.)

---

## Flagged but NOT touched (rule 4)

1. **97.6% trace-declaration rate** appears in both files; the
   existing `% TODO(author)` in 3_Method says other chapters quote
   95.1% and the code-corroborated rate is 94.8%. Numbers left exactly
   as found in both files.
2. **88τ** ("the smallest threshold any decision was taken against"),
   the **2.7–4.5× isotropic-null bound**, and **ECE 0.2114** in
   3_Method are measured frozen-run values kept as design/limitation
   context; if the coordinator wants a stricter reading of goal (a),
   these are the next candidates.
3. The **alternative cell-count numbers** (13/12 vs 11/10; 3 vs 6 for
   CS) in the "What a domain's cells are" paragraph: definitional
   contrast, left intact.
4. 4_Exp **screen-refit values** (ρ = 1.000 twelve of fourteen; law
   0.994, p = 0.003; chemistry 0.976, p < 0.001) — result-flavoured but
   ch4 was not in scope for result-stripping; they are selection
   provenance.
5. Possible inconsistency (not resolved, per rule 4): 4_Exp
   pre-registration says the third P4 addendum "refits the screen at
   the twelve-model roster, superseding its eight- and eleven-model
   generations", while §Rosters says "the screen is refitted at the
   settled eight-model roster" and the RQ-map section describes the
   refit at the settled eight-model roster. May be a
   generations-timeline subtlety, but reads as a contradiction.
6. All existing `% TODO(author)` and `% RESOLVED` comments left in
   place.

## \ref's pointing at compressed content (re-check after all agents land)

- `Section~\ref{sec:meth-bt}` is cited from 4_Exp's "No confidence
  interval" paragraph → target still states the bug and the
  no-intervals consequence after compression. OK.
- D5 (3_Method) cites `Section~\ref{sec:exp-metrics}` for the
  threshold withdrawal → metrics section still states the withdrawal
  and no-decision rule after compression. OK.
- `Section~\ref{sec:disc-debt}` now additionally carries the burden of
  the SE damage census and the length-matching numbers cut from
  3_Method — **coordinator: confirm Chapter 6's debt register states
  both** (owned by another agent in this pass).
- `Section~\ref{sec:res-capture-gap}` now owns the 863/868 figure
  exclusively (Chapter 5 — other agent). Confirm it is stated there.
- `Section~\ref{sec:res-adapted-partition}` now owns the 49.7–94.6%
  range exclusively. Confirm stated there.
