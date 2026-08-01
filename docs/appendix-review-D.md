# Appendix D review — D_Model_Rosters.tex

Date: 2026-07-31. Scope: `report/04_Appendix/D_Model_Rosters.tex` only. No builds run.

## Goal 1 — measured/argued tags

None existed. A grep for `\textsc{measured}` / `\textsc{argued}` in the file returned
nothing. The word "measured" appears only as plain prose (table caption "ground-truth
accuracy measured on...", exclusion policy "each entry carrying its measured reason")
and was left intact.

## Goal 2 — protected items, verified untouched

- `tab:roster-r8` with its three honesty flags: **5-shot condition** (gemini-3.1-pro),
  **unknown provenance** (arx_0314), **base model** (Llama-2-7b-hf) — byte-for-byte.
- The three settled-roster property paragraphs: length spread $6.79\times$
  (220–1,494 chars), arx_0314 at 21.4% bare, and the 5-shot/capability confound at
  the top — byte-for-byte.
- `tab:model-roster-pilot` and its collinearity caption (the withdrawn pilot's
  format/capability record) — byte-for-byte.
- The exclusion policy with its three notes (name disambiguation
  Meta-Llama-3_1 vs Meta-Llama-3, the no-generalisation ratchet, the
  judge-in-no-roster note) — byte-for-byte.
- The eleven-model band / reliability-constant paragraph (c = 2.52, unrefitted,
  pointer to `sec:disc-debt`) — byte-for-byte.

## Goal 3 — residual 12-model-as-result-source text

One instance found and fixed: the chapter intro still read "Two rosters carry results
in this thesis: ... and the twelve-model roster of the earlier paired runs whose
material Chapter~\ref{ch:results} still cites." This contradicted the file's own
resolution comment (Chapter 5 no longer cites the withdrawn runs) and Chapter 4's
framing ("One roster carries every settled result"). Rewritten to: one roster carries
every result; the earlier rosters are recorded as history, their campaigns withdrawn,
no number in Chapter 5 rests on them. The `\ref{sec:exp-rosters}` cross-reference is
retained.

Also removed: the stale three-line `% Resolved 2026-07-31` work-note comment at the
top of `sec:roster-earlier` (its content is now true of the file and recorded here).

Everything else already frames the twelve-model band correctly ("history, not as
sources of any number"; "that control has been given up").

## Goal 4 — duplication with Chapter 4

Checked against `03_Content/4_Experimental_Design.tex` `sec:exp-rosters` (lines
255–338). The division of labour is already correct and no appendix text needed
trimming: Chapter 4 carries one-sentence versions of the accuracy-spread rationale,
the length-match sacrifice, and the exclusion counts, and defers with "The full
roster tables are in Appendix~\ref{app:models}"; the appendix carries the tables,
the full property paragraphs, and the three-note policy. No sentence is duplicated
verbatim between the two. (Chapter 4 was not modified — out of scope.)

## Invariants checked

- All labels preserved: `app:models`, `sec:roster-settled`, `tab:roster-r8`,
  `sec:roster-earlier`, `tab:model-roster-pilot`, `sec:roster-exclusion`.
- All cross-referenced labels verified to exist: `ch:results`, `sec:exp-rosters`,
  `sec:res-cost`, `sec:res-law`, `sec:disc-debt`, `sec:disc-future`.
- No numbers changed anywhere (90.5/16.5/5.5, 6.79, 2.91, 21.4, 68.4/35.4/27.6,
  c = 2.52, 287→20, r = +0.286/+0.597 all intact).
- No other file modified; no build run (author builds with `arara main.tex`).
- File went from 155 to 151 lines (intro rewrite, same length; work-note comment
  removed).
