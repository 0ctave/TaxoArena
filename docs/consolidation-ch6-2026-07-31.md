# Consolidation pass — 6_Discussion_and_Conclusion.tex (2026-07-31)

Scope: only `report/03_Content/6_Discussion_and_Conclusion.tex`. No builds run.
Line count: **592 before → 578 after**. All 11 `\label{...}` intact; no `\ref`
target changed; `\textsc{measured}`/`\textsc{argued}` tags untouched; no number
or claim altered — numbers were relocated/deduplicated, never edited.

## Cuts per goal

### (a) Stop re-narrating Chapter 5
- §6.1: deleted the meta-announcement "None of the numbers is restated here;
  this section draws only the inference." (the surrounding sentence now carries
  the four-measurements pointer alone).
- §6.2, law bound paragraph: Spearman `0.929–1.000` vs split-half `0.922–1.000`
  removed; claim kept ("cells agree with the domain ranking as well as the
  ground truth agrees with itself") with a pointer to
  `Section~\ref{sec:conclusion}`, where the figures now appear exactly once
  (the "One bound travels" paragraph). No Chapter-5 label exists for this
  measurement in either telling, so the pointer is forward to the Conclusion —
  flagged below.
- §6.2, links-1-and-2 paragraph: `p = 1.21e-6` removed (kept once, in the
  Conclusion's "What was demonstrated"); the qualitative claim and the
  four-discriminators clause stay.
- Kept in §6.2 as allowed single quotes: "zero of 293" (only occurrence),
  "74 accuracy points" (only occurrence after the future-work trim), and
  "seven of eight domains / one adjacent transposition" — the magnitude IS the
  argument there ("two arms that close cannot produce a detectable ranking
  difference"), the review's own named exception.
- Future work item 5: "$74$ accuracy points" → "wide-spread roster" (the number's
  one quote stays in §6.2; the item keeps its existing
  `\ref{sec:res-granularity}`).
- §6.1's 97.6% kept: it is an architecture fact (`sec:arch-judge`), not a
  Chapter-5 result, and the inference hinges on it.

### (b) Four shortcut measurements
- Four-bullet list kept in full (contribution statement, all rates intact).
- RQ1 answer paragraph: keeps 196/200; dropped the duplicated "one shared
  ordering, recovered eight times" clause and the 86% rate; each mechanism now
  one clause, closed with "each quantified in the list above". Direction chosen:
  the bullets had the better prose for the rates.
- Same treatment applied to the RQ2 answer (light dedup only): dropped
  "$13.0\%$ against $10.9\%$" (carried by bullet 4), kept "declines to name a
  winner more often, in all eight domains, at the rates in the list above".
  Ranking sentence (seven of eight + transposition) untouched.

### (c) Variance bug (1/K vs 1/K²)
- Confirmed the full story is told exactly once, in the debt register
  (`sec:disc-debt`, bullets 1–2). No duplicate telling existed elsewhere in the
  chapter; nothing to collapse. Both bullets kept in full.

### (d) Aphorism enders
- Deleted the debt-register/section closer "…are two views of the same
  measurement discipline. What remains is to state what survives both … and
  that is the Conclusion." (recap + transition announcement). §6.4 now ends on
  the last concrete bullet (routing ECE).
- Kept "A comparison arm is a measurement and has to be checked like one" as
  the chapter's single aphorism (it is mid-section, not an ender, and is the
  strongest).
- "…rule stated as foresight…" not present here (Chapter 3) — ignored as
  instructed.

### (e) Partition / replay compressions
- The §6.2 replay statement ("the generic arm replays the cell-scoped arm's own
  triples under the same cells, Appendix preregs") kept as the ONE full telling —
  the "differ only in the rubric bundle" argument turns on it.
- All other mentions were already clause-length (bullet 4 "replaying identical
  comparisons"; RQ2 "replaying the cell-scoped arm's exact comparisons";
  future-work item 4 "replaying the same triples") — left as is.
- "No condition removes the partition" appears in body text nowhere; only
  inside an author TODO comment (left untouched).

### (f) Tics
- "Worth stating": zero instances found.
- "X rather than Y": ~15 → 10 in body text. Cut: "rather than at whatever
  configuration was convenient" (§6.3 ender), "rather than apologetically"
  (debt intro), "reported as such rather than quoted flat" (convention bullet,
  restructured), "open rather than answered" (future-work item 3 — the
  Conclusion keeps the one instance of that phrasing), "actionable rather than
  merely honest" (item 7). Remaining instances are load-bearing technical
  contrasts (ρ/r rather than ρ/√r; weights rather than prompt; etc.).
- Em-dash clusters: removed pairs via the (a)/(b)/(d) rewrites; additionally
  converted the judge-memorisation parenthetical to parentheses and the
  "become locatable ---" dash to a colon. Bullet-list trailing dashes kept
  (deliberate parallel structure).
- Throat-clearers: "The offline screen deserves one closing sentence, because…"
  → direct statement; "and that is the point:" (§6.3 intro) → "which is why".
- 3+-internal-ref paragraphs: none found after edits (citations excluded).

### (g) Commit hashes
- `a92a3ed` (debt register, scheduler bullet — note: it sits in
  `sec:disc-debt`, not the self-check section as the brief said) moved to a
  footnote: "The fix is dated,\footnote{Commit \texttt{a92a3ed}, 2026-07-27.}…"

### (h) Future-work list
- Order untouched. Only density edits: item 5 (74-point figure, see (a)),
  item 7 ("rather than merely honest"), item 3 ("open rather than answered" →
  "open"). All other items verbatim.

## no-ai-slop pass
- Colon-reveal / faux-insight: "and that is the point:" fixed; the verdict-style
  bolded openers ("**The partition can only bind where correctness is not
  checkable.**", "And the reading rule matters more than the reading.") kept
  deliberately — author voice.
- Summary-recap endings: the debt-register closer deleted (see (d)). The
  Conclusion's "What the reframing contributes" kept — it summarises the
  thesis, not the section it follows, which the brief allows.
- Trailing -ing pseudo-explanations: none found.
- Deliberate fragments kept ("Measure verdict agreement before spending a
  judging budget on an A/B arm.", "There is little such capability here to
  discover.").

## Flagged, not touched
1. **Forward pointer to the Conclusion**: §6.2's law-bound paragraph now points
   to `Section~\ref{sec:conclusion}` for the Spearman figures because no
   Chapter-5 label for that measurement is cited anywhere in this chapter
   (the "One bound travels" paragraph in the Conclusion also carries no ref).
   If a Chapter-5 home exists (res-granularity? res-leaf-null?), swap the
   pointer there.
2. **Scope statement appears twice** (external validity §6.4.2 and the
   Conclusion's "What the scope licenses"): one corpus / seed 42 / eight of
   fourteen domains / rosters 8–12. Left both — scope-setting, not a
   Chapter-5 result, and each serves its section.
3. Both author TODO comments (settled-batch Δρ restatement; mathematics
   outcome) left verbatim, including the DELETED-sentence guard.
4. The two `%%%` merge-provenance comments left in place.
5. File was 592 lines at start, not ~620 as briefed.

## Labels whose referenced content was compressed in this chapter
(no labels were deleted or renamed; these labels' *citing text here* was
shortened)
- `sec:res-judge-summary` — §6.1 evidence sentence and RQ1 answer compressed.
- `sec:res-c5` — RQ2 answer rates removed (bullet 4 carries them).
- `sec:res-granularity` — future-work item 5 lost the 74-point figure.
- `sec:res-law` — the "deserves one closing sentence" lead-in removed
  (screen-saturation numbers kept, once).
- `sec:conclusion` — gained a forward pointer from §6.2 (see flag 1).
- `subsec:disc-external-validity` — item 7 clause trimmed.
- `app:preregs` — item 3 phrasing trimmed ("open").
