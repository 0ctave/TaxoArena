# Appendix B review — B_Judge_Generation.tex

Scope: `report/04_Appendix/B_Judge_Generation.tex` only. `Figures/judge_example.tex` untouched. No builds run.

## Findings on the goal list

1. **\textsc{measured}/\textsc{argued} tags** — none present in the file at review time (verified by grep). Nothing to remove; a prior pass had evidently already stripped them.
2. **Withdrawn-run material** — three residues found and removed (see edits below). None of the removals touched a number, a label, or protected content.
3. **Protected content, verified intact:**
   - `tab:arm-differences` — untouched (referenced from 5_Results.tex lines 186, 544 and 6_Discussion_and_Conclusion.tex line 535).
   - OPTIONS/RESOLVED mode description — kept, including the 93.2%–99.8% per-domain attachment range. Note: the **97.6% pooled figure and the 0-of-1,569 verification are not in this file** — they live in the chapters (97.6%: 1_Introduction, 3_Method, 4_Experimental_Design, 5_Results, 6_Discussion; 1,569: 4_Experimental_Design lines 177/235/434). They were not added here (hard rule: no number changes); Results line 126 already points at this appendix as the single home of the per-domain range, which still holds.
   - Worked-example section (`sec:judge-example`, `\input{Figures/judge_example}`) — untouched.
   - Self-judging-cost paragraph (map/reduce LLM = arena judge, "weaker test" sentence, one-time-cost-per-snapshot) — untouched.
4. **Chapter-4 repetition** — the replay-design paragraph now opens with a pointer to `Section~\ref{sec:exp-rqmap}` instead of restating the triple-replay mechanics; the appendix-specific measured overlap (100% / 99.6%) is kept, since it appears nowhere else.

## Edits made (3)

1. Deleted the draft-history sentence "Earlier drafts of this appendix described it as a $k = 25$ representative pack, which was wrong." The batch-size-not-sample-size clarification stays.
2. Replaced the replay paragraph: mechanics restatement → pointer to `sec:exp-rqmap`; deleted "The withdrawn earlier runs scheduled each arm independently and carried a larger residual; the replay design removed it." Also deleted the stale `% TODO(author)` comment about the isolation run directly above it — Chapter 4 (line ~382) now names that run as future work, so the TODO is resolved.
3. In `sec:judge-prompt-contents`: "…and the settled batch differs from the earlier runs here" → "What varies is the option context."; dropped "This is what every earlier run used." from the OPTIONS item (its "earlier runs" antecedent was removed by the previous edit). RESOLVED still states it is the settled batch's mode.

## Invariants checked

- All five `\label`s in the file preserved (`app:judge-generation`, `sec:judge-template-full`, `tab:arm-differences`, `sec:judge-prompt-contents`, `sec:judge-example`); all are referenced from chapters or the figure file.
- All `\ref` targets used in the file exist (`ch:experimental-design`, `sec:exp-rosters`, `sec:arch-judge`, `sec:res-c5`, `ch:results`, `sec:exp-rqmap`, `subsec:disc-construct-validity`).
- No reported number altered anywhere; grep confirms zero remaining "earlier/withdrawn/pilot/Run A/12-model/\textsc" occurrences.
- Edits made with the Edit tool only; whole sentences removed, so brace/environment balance is unchanged.
