# Report Quality & Style Analysis (2026-07-23)

> **STATUS: STALE-BUT-FIXABLE (2026-07-30). The instructions are right; the measurements
> are dead.**
>
> Struck: "Results/Discussion/Conclusion are stubs (42/24/4 lines)" and the whole balance
> table built on it — Results is now the largest file in the report. Struck: "no figures in
> 2,700 lines" — the set is 8 (`figures-plan-v3.md`). Struck: convergence "~iteration 15" —
> the certificate settles at **iteration 10**. Struck: the suggestion to reconsider the DAG
> demotion "now that the DAG carries novel machinery" — polyhierarchy was measured and
> retired as a negative result, so the cross-link operator is exactly what should stay
> demoted.
>
> **Still the right instructions:** the de-duplication table and the eight-item style list.

Scope: `report/03_Content/*.tex` (2,674 lines) + `report/04_Appendix/*.tex`
(1,258 lines). Results/Discussion/Conclusion are stubs (42/24/4 lines) and are
excluded except as balance data points. The logic-alignment pass of the same
date (Appendix 11 rewrite + Ch1/3/4/5 touch-ups) is assumed applied; this
analysis covers what remains.

---

## 1. Repetition — the dominant problem

The same motifs are re-explained at full paragraph length in 3–7 places. A
reader meets each of these ideas as if for the first time, several times.
Recommended rule: **one home per idea, references elsewhere.** The home is
suggested in each entry.

| Motif | Occurrences | Suggested home |
|---|---|---|
| Reference-informed / answer-key-blind dual property | Ch1 §Approach (2 ¶), Ch1 §Scope, Ch3 Goal 3, Ch3 §Judge Design (invariant ¶), Ch4 §Notation, Ch4 §Validation, Ch5 §Info Separation | Ch5 §Info Separation (the table *is* the argument); one sentence each in Ch1 and Ch3 |
| Iteration-1 bootstrap / migration-is-emergent | Ch3 §3.3 (¶1), App11 §Seed Init, App11 §Migration, Ch4 §Construction Summary | App11 §Migration; one clause in Ch3 |
| Anchor immutability | Ch1 §Contributions, Ch3 Goal 1, Ch3 §3.3, Ch3 Node Types, App11 §Seed Init, App11 §Migration (again) | App11 §Seed Init; adjective ("immutable") elsewhere |
| Held-out routing = same trickle, read-only, capped | Ch3 §3.2 stage 4, Ch3 §Arena Lifecycle, App11 §Routing (end), App11 §Polyhierarchy (end) | App11 §Routing; cross-reference elsewhere |
| Primary-path convention + 1/k fractional weighting | Ch1 Contribution 2, Ch3 §Arena Lifecycle, Ch3 §Aggregation, Ch4 §Aggregation | Ch4 §Aggregation |
| "Never average BT parameters" (full identifiability ¶) | Ch3 §Aggregation, Ch4 §Aggregation — near-duplicate paragraphs | Ch4; delete the Ch3 paragraph, keep one sentence |
| d=256 fixed / same hypersphere / no cross-depth projection | Ch3 stage 1, App11 §MRL (now merged — was two back-to-back near-duplicate sections), Ch4 summary | App11 §MRL |
| Scheduler-is-not-a-contribution demotion | Ch1 §Contributions (¶), Ch2 closing, Ch5 §RQ map | Ch1, once, one sentence |
| Selected-domain proof-of-concept scope | Ch1 §Scope, Ch5 §RQ map, Ch5 §Datasets, (planned again in Discussion) | Ch5 §RQ map; Discussion gets the *interpretive* version only |
| Migration rate / Δτ definition | App11 §Migration, Ch4 §Notation, Ch4 §Aggregation, Ch5 §RQ map | Ch4 §Aggregation for Δτ; App11 for the mechanics |
| Reproducibility tuple / manifest | Ch3 §Persistence, Ch5 §Env footnote | Ch3 §Persistence |

Estimated saving from de-duplication alone: **300–400 lines** across
Ch1/Ch3/Ch4, with zero information loss.

## 2. Per-chapter intro + summary overhead

Every chapter currently carries **three** layers of self-description:
1. Ch1 §Thesis Structure summarises all chapters (~35 lines);
2. each chapter opens with a roadmap paragraph (5–15 lines);
3. Ch3/Ch4/Ch5 close with a "Chapter Summary" section that restates the whole
   chapter in one breath (Ch3: ~24 lines; Ch4: ~20; Ch5: ~12).

The chapter summaries are pure restatement — every sentence in them appears
earlier in the same chapter, usually nearly verbatim (compare Ch3 §Summary with
Ch3's own section openers). With the heavy per-section `\textbf{Label.}`
signposting (see §4), the summaries triple-announce content.

**Recommendation:** delete the three Chapter Summary sections entirely, or
replace each with a 2–3 sentence *bridge* ("With the architecture fixed, the
next chapter derives…") that adds forward motion instead of recapitulation.
Compress Ch1 §Thesis Structure to one line per chapter. Keep the opening
roadmaps but cap them at ~4 sentences. Saving: **~70–90 lines** and, more
importantly, the sense of being told everything three times.

## 3. Emphasis balance

Current line budget vs claimed importance:

| Part | Lines | Note |
|---|---|---|
| Ch2 Literature | 878 (33 % of content) | 20 subsections; §Routing alone ~130 lines for a use case declared out of scope |
| App11 DAG formalism | ~600 | explicitly "not the headline contribution" |
| Ch4 Formal Foundations (arena = the headline) | 294 | half of which is construction summary + assumptions |
| Ch3 Architecture | ~740 | includes ~85 lines of limitations |
| Results + Discussion + Conclusion | 70 (stubs) | will need the space the others are consuming |

Specific imbalances:

- **The demoted scheduler still gets celebrity treatment**: a full utility
  formula + decay narrative in Ch4 (~40 lines), a state-machine table and two
  subsections in Ch3, and a defensive "internally consistent reading" paragraph
  (Ch4 §Scheduling) that argues with an imagined reviewer. If it is an
  engineering component, one Ch3 subsection + the Ch4 formula suffice; the
  interpretive defence can go.
- **Ch2 §Routing** (~130 lines) motivates a component the thesis explicitly
  does not build. Halve it: the motivation needs the *gap* (profiles don't
  exist), not a survey of routing systems.
- **Ch3 §Architectural Limitations** (7 items, ~85 lines) will collide with the
  Discussion's limitations section. Keep the two purely architectural ones
  (seed dependence, embedding dependence) as short notes; move
  judge-bias/tie/sparse-leaf material to Discussion where it can face the
  actual results. Decide the single home *now* to avoid writing it twice.
- **Ch2 literature positioning paragraphs**: each section ends with "the design
  choice it motivates," and Ch2's closing then re-lists all five gaps, and Ch3
  §Requirements Traceability maps them again. Two of these three passes can go
  (keep the per-section closers, cut the chapter-end re-list; shrink
  Traceability to a table row per gap if kept at all).

## 4. Style observations

1. **`\textbf{Label.}` paragraph blocks dominate the prose.** Goals, stages,
   phases, limitations, gates, effects, conventions — most of Ch3/Ch4/App11 is
   labelled blocks. It reads as specification, not argument. Fine for the
   appendix (it *is* a spec); in chapters, convert runs of labelled blocks into
   flowing paragraphs and reserve bold labels for genuinely enumerable design
   decisions (Goals, RQs, Limitations).
2. **Em-dash nesting and sentence length.** Many sentences carry two or three
   dash-parentheticals ("---the diagnosis this section develops and the
   literature review substantiates---", "---a compute-budget trade-off restated
   in the Discussion---"). One dash-insertion per sentence is a good ceiling;
   most of these are deletable meta-commentary (see next point).
3. **Defensive meta-commentary.** Recurring phrases argue with the reader
   instead of stating the design: "this is the internally consistent reading of
   the utility term", "should be read against this ramp honestly", "reflecting
   what the implementation actually executes", "restated in the Discussion and
   revisited in…", "a pending hardening step, not a correctness gap". Each is a
   symptom of an anxiety the text should resolve once, in the right place
   (usually Limitations), not inline. Cutting these tightens tone markedly.
4. **Demotion disclaimers repeated** ("not a headline RQ", "not an independent
   contribution", "not the contribution of this thesis" for the DAG — stated in
   Ch1, Ch2, Ch5, App11). Once in Ch1 is enough; repeating a disclaimer four
   times reads as protesting too much — especially now that the DAG carries
   novel machinery (proposal gate, cross-link operator, determinism). Consider
   whether the demotion is even still accurate before propagating it.
5. **Substantive content in footnotes.** Ch5 carries the 60/15/25-vs-70/30
   split realisation and (until this pass) the bridge-parameter status in
   footnotes. Design realities belong in body text; footnotes are for asides.
6. **Placeholder figure** (Fig. 3.1) and no other figures in 2,700 lines. The
   pipeline, the DAG-with-cross-links, and a proposal-gate flow diagram are the
   three figures that would pay for themselves; the six-phase table (App11) and
   the state-machine table (Ch3) both want a diagram companion.
7. **Terminology drift** (partially fixed by the logic pass): bridge vs
   cross-link vs secondary edge; anchor vs domain vs GT domain; "depth-0"
   anchors vs implementation depth. Pick: *cross-link* (mechanism), *bridge
   node* (result), *anchor* (top-level node), *domain* (MMLU-Pro label), and
   apply globally — Ch2's "gated bridge insertion" closing should become
   "proposal-gated cross-linking".
8. **Number drift to re-verify at result time**: corpus "12,000" (Ch5) vs
   8,353 construction queries at the realised 70/30 split; `numIterations`
   (now 50); `membershipFloor` (now 0.25); convergence "~iteration 15". A
   single "canonical configuration" table (App7) should be the *only* place
   numbers live; chapters should reference, not repeat, values.

## 5. Suggested execution order

1. Delete the three Chapter Summaries; compress Ch1 §Thesis Structure. (1 h,
   ~90 lines)
2. De-duplicate the eleven motifs of §1 to their homes. (2–3 h, ~350 lines)
3. Halve Ch2 §Routing; cut Ch2's closing gap re-list; shrink Ch3
   Traceability. (~1 h, ~120 lines)
4. Move judge-facing limitations from Ch3 to Discussion skeleton; keep two
   architectural ones. (30 min)
5. Style sweep: defensive meta-commentary, dash-nesting, labelled-block runs
   in Ch3/Ch4. (2 h)
6. Figures: pipeline overview, DAG-with-cross-links example, proposal-gate
   flow. (separate task)

Net effect: content chapters shrink ~20 % with no information loss, the arena
regains its position as the visibly dominant subject, and the remaining prose
stops hedging.
