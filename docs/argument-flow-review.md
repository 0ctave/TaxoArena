# Argument-flow review — TaxoArena thesis (report/03_Content as of 2026-07-28)

Reviewer stance: first-time examiner who knows ML but not this project, reading
`report/03_Content/1_Introduction.tex` through `8_Conclusion.tex` in order, plus
`report/02_Prematter/e_Abstract.tex`. This review is about ARGUMENT CLARITY AND FLOW
only. Correctness is audited separately in `docs/peer-review-2026-07-28.md`; where a
flow observation touches one of that review's findings, I cite it and move on.

Ground rule respected throughout: nothing here proposes weakening an honesty
guarantee. Registered-rule verdicts, both tie policies in every table, and the
MEASURED/ARGUED marks all stay. Every proposal below is about **placement and
economy** — say it once, say it where the reader can use it, and reference it after.

---

## (a) The elevator version

The argument, in five sentences a non-specialist can follow:

1. Systems that dispatch tasks to different LLMs need to know which model is best
   *per topic*, but leaderboards report one number per model.
2. TaxoArena splits an evaluation corpus into small, coherent topic cells, writes a
   judging rubric for each cell, and has an LLM judge compare model answers pairwise
   inside each cell — the idea being that a narrow cell makes a specific rubric
   writable, and a specific rubric makes a better judge.
3. Because the corpus (MMLU-Pro) has an answer key, every verdict can be checked, and
   the checks show the judge is not applying the rubric at all: it verifies which
   answer is correct — a judge with no rubric reaches the same winner 99.4% of the
   time, and agreement with the key is *highest* when there is no reasoning to judge.
4. The partition also has nothing to reveal here: under a pre-registered analysis,
   cells do not carry different true model rankings on this corpus, so per-cell
   evaluation cannot beat global evaluation no matter how good the cells are.
5. The consequence is a boundary result: wherever correctness is checkable a capable
   judge will shortcut the rubric, so cell-scoped judging can only matter on
   open-ended tasks — exactly the setting the routing motivation was about, and the
   one this thesis could not test.

**Can this be extracted from the text alone?** Yes — but the reader has to build it
themselves, from three places: the abstract (`e_Abstract.tex:31-62`), Contribution 1
(`1_Introduction.tex:344-354`), and `7_Discussion.tex:24-39`. No single passage in
the *body* states the five-sentence chain plainly before Chapter 5. Where it breaks
down for a first-time reader:

- **Sentence 3 (the headline finding) is never stated flat in the Introduction.** It
  first appears wrapped in its own caveats inside a contributions list
  (`1_Introduction.tex:344-354`: "it selects the correct response on the large
  majority of items where exactly one response is correct, its tie rate roughly
  triples on precisely those items where…"). The examiner meets the finding as a
  compound clause with three subordinate measurements before meeting it as a claim.
- **Sentence 4's relationship to sentence 3 is assembled late.** That there are *two*
  independent negatives — the judge bypasses the rubric AND the cells carry no signal
  — and that they kill the original thesis from two different directions, is only
  said clearly at `7_Discussion.tex:49-77`. Until then the reader holds two nulls
  without knowing whether they are one failure or two.
- **The RQ2 verdict exists in three framings.** `1_Introduction.tex:356-364`
  ("…and the null it returned"), `6_Results.tex:407-411` ("the Math null
  **failed**" under the registered rule), and `8_Conclusion.tex:47-50` ("counts as a
  *failed* null… the tie-scoring attribution is post hoc"). The Results and
  Conclusion framings agree; the Introduction's contribution heading still reads as
  "it returned a null". A first-time reader who trusts the Introduction is
  contradicted 250 pages later. (The substance is peer-review major issue 2; the
  *flow* problem — three tellings, one stale — is separate and cheap to fix; see
  edit 2 in section (f).)

---

## (b) Flow audit per chapter

### Chapter 1 — Introduction (`1_Introduction.tex`)

Strong spine: motivation → micro-example → "What a Partition Is For" → three links →
RQs → contributions → scope. The best material in the chapter (`1_Introduction.tex:135-159`,
the cell-as-rubric-scope argument) is genuinely simple and first-principles. Three
places lose the reader:

1. **The reframing autopsy arrives before the reader has met the thing being
   reframed.** `1_Introduction.tex:286-303`: "This decomposition was written after
   some of the results were in hand, and specifically after the pre-registered
   granularity analysis (Chapter~5) refuted the premise of the thesis's original
   second research question." At this point the reader knows neither the granularity
   analysis, nor the original RQ2, nor Δτ. Eighteen lines are then spent dissecting a
   research question that no longer exists (`:292-303`) *before* the live RQ1/RQ2
   are stated (`:305-323`). The honesty ("a reframing announced is a contribution")
   is right; the placement is backwards. State the live questions first; then one
   short paragraph: "RQ2 replaces an earlier question, for a measured reason reported
   in Section~res-granularity." The full autopsy already exists in Results and
   Conclusion.
2. **Contribution 2 uses machinery not yet introduced.** `1_Introduction.tex:361-364`:
   "The arms are indistinguishable on the high-power metric, and the apparent
   advantage on the low-power one survives only under one of two tie conventions."
   The reader has not been told what the two metrics are, what their power difference
   is, or what a tie convention is. A contributions list should be readable by
   someone who has read only the pages above it. ("…survives only under one of two
   defensible ways of scoring ties (Chapter 5)" would carry the same honesty in
   plain words.)
3. **Scope section front-loads apologies.** `1_Introduction.tex:419-427` discloses
   the capture-gap defect and the tie-policy instability before the reader has seen a
   single run. Both disclosures are honest and belong in the thesis — but at this
   point they are caveats to results the reader hasn't met, so they register as
   anxiety rather than rigour. One sentence each with a forward reference would do;
   the full statements already exist at `6_Results.tex:210-296` and `:437-457`.

### Chapter 2 — Background (`2_Literature.tex`)

Reads as a competent, well-scoped background chapter; the "sized by what the argument
consumes" principle (`2_Literature.tex:15-20`) is good even if the sentence
announcing it is meta-narration (peer-review slop item 4). Two flow failures:

1. **The Synthesis promises the pre-reframing thesis.** `2_Literature.tex:663-671`:
   "TaxoArena addresses it through two integrated contributions. The first is a
   label-bootstrapped, corpus-induced geometric taxonomy… The second is a
   reference-informed, answer-key-blind arena that produces the per-domain profiles
   required by routing." The reader was told 40 pages earlier that "The induced
   taxonomy is *not* the contribution of this thesis" (`1_Introduction.tex:226-228`).
   This is peer-review major issue 7 on substance; as pure flow, it is the single
   worst transition in the document — the chapter's last paragraph hands the reader
   into Chapter 3 holding the wrong thesis.
2. **Section 2.4's closing question is excellent and under-used.**
   `2_Literature.tex:395-408` ("what does a pairwise judge condition its verdict
   on?") is the clearest statement of the thesis's real question anywhere before
   Chapter 5. It deserves to be echoed in the Introduction (it is the plain-language
   version of RQ1's "what decides the verdicts"), not discovered mid-literature.

### Chapter 3 — Method, part 1 (`3_System_Architecture.tex`)

The R1–R4 requirements frame (`:27-48`) is exactly the "simple ideas first"
structure the author wants — state what a partition must satisfy, then show it does.
Two flow problems:

1. **A forward-referenced justification repeated before it is ever shown.** The
   eleven-fold / +10.3% fact — "both change the system's measured discriminative
   power by zero" — appears at `1_Introduction.tex:236-240`, again at
   `3_System_Architecture.tex:22-25`, again in table row R2 (`:132-135`), and again
   at `:183-185`, all before its derivation at `6_Results.tex:655-691`. Four
   assertions of an unproven number teach the reader to skim the sentence; by the
   time the actual result arrives it feels already-known rather than earned. State
   it once in Chapter 1, reference it thereafter ("for the measured reason of
   Section~res-granularity").
2. **The evidence table's void bookkeeping interrupts its own row.** Row R1
   (`:99-108`) delivers evidence and withdraws half of it in the same cell ("The
   within-node null values were computed on a superseded tree and are unresolved as
   to values; the method survives"). The honesty must stay; but a first-time reader
   cannot yet weigh "superseded tree" — the phrase presumes the project's revision
   history. One footnote defining what "superseded tree / void as to values" means
   *once* (there are three such markers: `3_System_Architecture.tex:105-108`,
   `:199-203`, `6_Results.tex:565-569`) would let the rows say "void as to values
   (see note N)" and stop re-explaining.

### Chapter 3 — Method, part 2 (`4_Methodology.tex`)

The opening is the best in the thesis: "The arena does not query models."
(`4_Methodology.tex:7`). After that, this file has the highest density of
project-log material addressed to a reader who was never a project member:

1. **"None has appeared in earlier descriptions of this system"**
   (`4_Methodology.tex:96-97`) — the examiner has read no earlier description. The
   four judging-path properties themselves are needed; the framing sentence is not.
2. **"A correction to every standard error this project has previously
   reported"** (`4_Methodology.tex:152-166`). The examiner has read none of those
   reports. What the thesis-reader needs is two sentences: the implementation
   subtracted 1/K where 1/K² was required; every pre-correction SE was the floor
   constant; no pre-correction interval is quoted. The full derivation and the
   44–209× consequence are then given *again* at `7_Discussion.tex:254-264`. Told
   twice at length, the story reads as penance; told once, it reads as a correction.
3. **"What Is Not Implemented"** (`4_Methodology.tex:264-299`) is a full page of
   negative inventory — per-pair state machines named `UNSEEN`/`INFORMATIVE`/…, a
   utility floor, an escape valve — none of which the reader has been promised. The
   stated purpose ("so that no reader finds a gap the thesis did not name", `:269-270`)
   is defensible only against a reader of the earlier drafts. For the examiner this
   is an appendix ("Deviations from the design document"), with a two-sentence
   pointer in the main text.
4. **Measurement Discipline D1–D5** (`4_Methodology.tex:301-389`) is the honesty
   machinery working as intended, and the rule-plus-scar format is persuasive — but
   at ~90 lines with *second* instances (D1's identifier-space audit `:321-326`;
   D2's iteration-counter-hardcoded-to-−1 story `:330-339`; D4's three instances
   `:363-378`) it becomes the chapter's centre of gravity. One rule, one scar, one
   sentence each; second instances to a footnote or the appendix. The rules survive
   intact; the war stories stop outweighing the method.

### Chapter 4 — Experimental Design (`5_Experimental_Design.tex`)

Structurally the cleanest chapter: RQ-map table, environment, split, rosters,
conditions, pre-registration, metrics. The three-roster paragraph
(`5_Experimental_Design.tex:176-178`: "Three rosters appear in this thesis. They are
not the same roster, and saying so is more useful than smoothing them into one") is
the model for how conventions should be handled everywhere — one clear declaration,
then names. Flow failures:

1. **The split subsection opens as an errata.** `5_Experimental_Design.tex:105-107`:
   "The intended proportions are 60/15/25, and the implementation does not match
   them." The design chapter should state the design as run, then note the
   deviation: "The split as run is 70/30… (an earlier design specified 60/15/25;
   the no-leakage property holds under both)." Same facts, no whiplash.
2. **The cut condition.** `5_Experimental_Design.tex:289-295` spends a paragraph on
   a fourth condition that does not exist, was never run, and whose motivating
   question was already refuted. The reader must parse a design in order to learn it
   is absent. Footnote.
3. **Bookkeeping interrupting the roster story.** The
   `Meta-Llama-3_1-70B-Instruct` ≠ `Meta-Llama-3-70B-Instruct` disambiguation
   (`:241-246`) and the 4.2% unattributed-rows note (`:124-127`) are exactly the
   kind of detail that belongs in a footnote: real, necessary, and fatal to momentum
   in running prose.
4. **The chapter's biggest hole is a silence, not a caveat**: "the judge is a single
   large instruction-tuned model" (`:52-54`) with the todo at `:68-73`. Peer-review
   major issue 4 covers the substance; the flow point is that every subsequent
   judge-behaviour claim is read against an unnamed actor, which makes the whole of
   Chapter 5 feel provisional.

### Chapter 5 — Results (`6_Results.tex`)

The mechanism ordering (judge first, partition second) is right and the opening
paragraph justifying it (`6_Results.tex:5-14`) earns its place. The strongest
sections — trace inversion (`:152-208`), rubric null (`:570-639`), granularity
(`:641-743`) — are strong precisely where they lead with the finding. Failures:

1. **Sections that open with the epistemic credential instead of the finding.** The
   clearest: `6_Results.tex:643-647` — "MEASURED, and the analysis was fixed in
   writing before it was run. Three outcomes were named in advance, and 'observed ρ
   is primary' was fixed in advance — which is the only reason the result is
   readable…" Twenty-nine words of registration mechanics before the reader learns
   *what question is being asked*, let alone the answer (which lands at `:657`, "It
   does not fall", after a table). Same pattern at `:761-762`: "it is the most
   instructive methodological result in this project: this conclusion reversed twice
   before settling" — the section's headline is its process history
   ("The Domain Screen, and Its Two Reversals", `:745`), and the result the argument
   needs (law reorders, Math does not, hence Math is the null arm and law the real
   test) is subordinate to the reversal narrative. Finding first, credential second,
   process third.
2. **The correctness-blind-ρ archaeology.** `6_Results.tex:134-150`: the withdrawn
   0.74–0.76 vs 0.90–0.93 episode is handled with exemplary honesty (peer review
   calls it the model for such cases) — but it takes ~17 lines plus an inline todo to
   deliver a two-sentence payload ("the magnitude is withdrawn; direction and tie
   behaviour carry the claim"). Compress in place; move the reconstruction detail
   (which convention, which subsetting) to the appendix where the eventual resolution
   will live.
3. **A project-log aside inside the thesis's most sensitive table.**
   `6_Results.tex:400-405`: "…a third convention, named here because an unstated
   convention is how three earlier figures in this project became irreproducible."
   The reader has met none of those three figures (they surface at
   `7_Discussion.tex:296-313`). Naming the third convention is required (peer-review
   major issue 5); the motivating clause about the project's history is not.
   Footnote the clause, keep the convention.
4. **The acceptance-gate subsection proves at length that the gate does nothing.**
   `6_Results.tex:541-569`: two negative results, a rule-D3 walkthrough
   (CV 14.3%→15.7%, variance ratio 1.05, F(4,4) critical 6.39), and a void caveat,
   in service of one point already argued in Chapter 3 ("a gate can be right because
   its units are right, without improving the number it gates" — stated at
   `3_System_Architecture.tex:175-177` AND `6_Results.tex:556-563`). Keep the two
   negative facts and the one-sentence moral; the statistical mechanics go to the
   appendix; the aphorism appears once, not twice.
5. **Polyhierarchy is an orphan.** `6_Results.tex:790-879` is a self-contained
   negative result whose connection to RQ1/RQ2 is never stated — it lands on no link
   of the chain. It is worth reporting (a built-measured-retired operator), but the
   operator mechanics — the capture inequality at `:815-820`, the guard list, the
   acceptance threshold — are construction formalism sitting in the results chapter.
   Result and decision stay (~half a page); mechanics join
   Appendix~dag-formalism, which already discusses the topology.
6. **The tie-policy section arrives after its main consumer.** The evidence that ρ
   is convention-unstable (`6_Results.tex:437-457`) follows the Run-B table that the
   instability nearly decides (`:379-427`). Chapter 4's metric rules partially
   pre-arm the reader, but the natural order inside Results is: conventions box
   first (see (d)), Run B second.

### Chapter 6 — Discussion and Conclusion (`7_Discussion.tex`, `8_Conclusion.tex`)

The two best argumentative sections of the thesis are here: "Where the Architecture
Binds" (`7_Discussion.tex:3-45`) and the link-by-link reading (`:47-98`). The
Conclusion's first sentence — "This thesis set out to validate a taxonomy and ended
by measuring a judge" (`8_Conclusion.tex:4-5`) — is the elevator pitch, and it is on
the last pages. Failures:

1. **The self-audit section praises the apparatus at the reader's expense.**
   `7_Discussion.tex:100-140` ("The Apparatus Caught Its Own Errors"): the
   side-channel story (`:113-124`) concerns two systems that *never entered any run*
   ("neither system entered an arena run as stored"). Twelve lines of detective
   narrative about a non-event in the evidence chain. The reliability-constant and
   screen-reversal entries point at stories already told in full elsewhere. This
   section works best as four one-line entries plus the genuinely transferable
   closing observation (`:135-140`, the newline-count / re-derive-at-decision-config
   lesson); the side-channel narrative goes to an appendix.
2. **The debt section retracts numbers the thesis never states.**
   `7_Discussion.tex:296-304`: "Figures of the form '72.2% of leaf pairs redundant,
   42.2% saturated' were reported previously." Reported *where*? Not in this
   document. A first-time reader is asked to un-believe a claim they were never
   exposed to. Same for the second telling of the BT-SE story (`:254-264`, already
   in full at `4_Methodology.tex:152-166`). The honest and economical form is a
   one-page appendix "Register of corrections to previously reported figures"
   (BT SEs, reliability constant, redundancy percentages, correctness-blind ρ,
   routing ECE) — the thesis text then keeps only the corrections that touch numbers
   *quoted in this thesis*, each in one place.

---

## (c) The simplicity test

One plain sentence per major section, with a flag where the section's own topic
sentence is worse than the plain one.

| Section | One-sentence point | Own topic sentence adequate? |
|---|---|---|
| 1.1 Motivation | Routers need per-domain rankings; leaderboards give one number per model. | Yes (`1_Introduction.tex:14-16` is close to this). |
| 1.2 What a Partition Is For | A narrow cell is what makes a specific rubric writable — that is the entire mechanism. | **No.** The section opens by negation: "A semantic partition… is usually presented as a reporting device. That is not what it is for here, and the difference decides what this thesis can claim" (`:129-134`) — the reader is told what it isn't and that something unnamed is at stake. The section's *own* best sentence, "A cell is a scope for a rubric" (`:135`), should be first. |
| 1.4 Three Links / RQs | The partition claim splits into three separately testable links, and the two RQs test them. | Yes at `:266-267`; **but** the section's actual first content is the dead-RQ autopsy (see (b)-Ch1-1). |
| 1.5 Contributions | The thesis's main finding is what the judge decides; everything else is the instrument and the negatives, honestly scoped. | Partly — each item is fine; the list as a whole never says which contribution is the thesis (that arrives at `:392-395`, after the list). |
| 2.4 LLM-as-a-Judge | Judges have known biases; what nobody has measured is what a judge conditions its verdict on when the corpus has a key. | Yes — `2_Literature.tex:395-400` is excellent. |
| 2 Synthesis | The gap is per-domain profiles over induced structure; this thesis tests whether that gap is real. | **No** — current text promises delivered profiles the thesis refutes (`:663-671`; peer-review issue 7). |
| 3.1 Requirements | A partition is usable for an arena iff its cells are coherent, big enough, stable, and honestly described (R1–R4). | Yes. |
| 3.1.2 Evidence | Each requirement has one measured line of evidence and one named caveat. | Yes. |
| 4 (Arena) | The arena re-judges stored responses inside cells and aggregates verdicts with Bradley–Terry. | Yes — `4_Methodology.tex:7` is the best topic sentence in the thesis. |
| 4 Measurement Discipline | Five reporting rules, each adopted after being violated once. | Yes (`:303-306`), though the section then over-delivers scars. |
| 5.3 Rosters | Three rosters: the defective pilot, the length-matched Run-B band, and the corrected 11-model band. | Yes (`5_Experimental_Design.tex:176-178`). |
| 5.5 Pre-registration | Four decision rules were frozen in dated documents before their data existed. | Yes. |
| 6.2.1 Correctness | The judge picks whichever answer is correct, and ties precisely where correctness stops discriminating. | Yes. |
| 6.2.2 Trace inversion | The judge agrees with the key most when there is no reasoning to evaluate — the signature of verification, not evaluation. | Yes. |
| 6.2.3 Capture gap | Half the pilot's comparisons were decided by which side had any text; what survives within-format survives more strongly. | Yes. |
| 6.2.4 Generic judge | With and without the rubric, the judge names the same winner 99.4% of the time — the verdict is fixed before the rubric enters. | Yes. |
| 6.2.5 No-partition baseline | Removing the partition changes nothing the high-power metric can see; the rank-correlation gap depends on tie scoring and formally failed the registered null toward no-partition. | **No.** The section opens with two-arm design recap (`6_Results.tex:347-356`) and the finding arrives at `:372`. Also the finding is split across four MEASURED/ARGUED blocks (`:372, :376, :407, :413`) with no single sentence stating the composite. |
| 6.2.6 Tie policy | Absolute ρ from this pipeline is unstable to convention; only paired contrasts under a stated convention are quotable. | Yes (`:450-453`). |
| 6.3.1 Construction | The construction reaches a certified fixed point and its acceptance gate is kept for its units, not for measured benefit. | Partly — split across `:507-524` and `:541-563`. |
| 6.3.2 Rubric null | Coherent cells produce measurably cell-specific rubrics; random cells produce generic ones. | Yes. |
| 6.3.3 Granularity | Cells do not carry different true model rankings, at any granularity, so per-cell evaluation had nothing to find on this corpus. | **No** — opens with registration mechanics (`:643-647`); the finding is "It does not fall" at `:657`, post-table. |
| 6.3.4 Domain screen | Only law reorders under this roster; Math does not — which makes Math the null arm and law the outstanding real test. | **No** — headline and topic sentence are the two reversals (`:745`, `:761-765`), a process story. |
| 6.3.5 Polyhierarchy | Concept-level multi-parenting was built, measured, and retired because the partition objective cannot see whether a cross-link is right. | Yes (`:790-797` is clear), though see (b)-Ch5-5 on bulk. |
| 7.1 Where it binds | On a corpus where correctness is checkable, a capable judge verifies instead of judging; the partition can only matter where it isn't. | Yes — the section is the argument's payoff. |
| 7.4 Debt | Two self-found errors are corrected; no pre-correction interval is quoted. | Yes, but see (b)-Ch6-2 on the retraction of never-stated numbers. |
| 8 Conclusion | Set out to validate a taxonomy; ended by measuring a judge; the decomposition is what makes the negatives informative. | Yes. |

---

## (d) What to demote

### The one-time mechanism: a Conventions box

The tie-policy convention is currently explained (not merely applied) at:
`1_Introduction.tex:311-313` and `:363-364`, `4_Methodology.tex:260-262` and
`:380-389` (D5), `5_Experimental_Design.tex:401-405`, `6_Results.tex:437-457`,
`7_Discussion.tex:228-237`, `8_Conclusion.tex:45-47` and `:63-65`, plus the abstract.
That is at least nine explanatory statements of one rule. The same applies, less
severely, to "BT θ never win-rate" (`4_Methodology.tex:210-217`,
`5_Experimental_Design.tex:395-399` — the 5/0-vs-5/2/4 example is given verbatim
twice), "seed 42, no multi-seed convention" (`5_Experimental_Design.tex:56-60`,
`6_Results.tex:23-25`, `7_Discussion.tex:161-163`, `8_Conclusion.tex:54-55`), and
B_logical accounting (`7_Discussion.tex:239-244`).

**Proposal.** A framed box — "Reading conventions for every result in this chapter" —
at the top of Chapter 5 Results (after `6_Results.tex:19`, or folded into "What Was
Run"), containing exactly: (i) every ρ appears under both tie conventions,
half-weighted and dropped, in that order — D5, evidence in Section res-tie-policy;
(ii) BT θ is quoted, never win-rate — reason in one clause; (iii) all runs are seed
42; (iv) comparison counts are B_logical (2 API calls each); (v) ρ quantisation grid
at M = 8/11/12; (vi) MEASURED/ARGUED marks per Section 1.4. Thereafter every result
cites the box ("both conventions, per Box 5.1") and every table keeps both rows —
**no honesty is removed; only the ninth re-explanation is.** Rule D5 itself stays in
Methods with its one scar; Section res-tie-policy stays as the evidence and moves
before res-c5 (see (b)-Ch5-6).

### Passages to demote (footnote / appendix / register), in priority order

1. `4_Methodology.tex:264-299` — "What Is Not Implemented" → appendix
   ("Deviations from the design document"), two-sentence pointer in text.
2. `4_Methodology.tex:152-166` — full BT-SE derivation → two-sentence statement here;
   derivation and consequences once, in the corrections register (see 12).
3. `4_Methodology.tex:321-326, 330-339, 363-378` — second/third instances of D1, D2,
   D4 → footnotes or appendix; one scar per rule stays in text.
4. `5_Experimental_Design.tex:289-295` — the cut fourth condition → footnote.
5. `5_Experimental_Design.tex:241-246` — Meta-Llama name-collision note → footnote
   attached to the roster table.
6. `5_Experimental_Design.tex:124-127` — 4.2% unattributed rows → footnote.
7. `6_Results.tex:400-405` — the "third convention" aside: keep the convention and
   the export values (required, peer-review issue 5); demote the motivating clause
   about three irreproducible earlier figures to a footnote.
8. `6_Results.tex:134-150` — correctness-blind-ρ reconstruction detail → compress to
   ~5 lines (withdrawal + what carries the claim); todo/mechanics to appendix.
9. `6_Results.tex:541-555` — acceptance-gate statistical mechanics (CV, F-ratio,
   correlation +0.006) → appendix; the two negative findings and the one-sentence
   moral stay.
10. `6_Results.tex:813-830` — polyhierarchy operator mechanics (capture inequality,
    guards, thresholds) → Appendix dag-formalism; result and decision stay in text.
11. `6_Results.tex:693-701` — the 0.922/0.884 assignment-convention caveat →
    footnote to Table tab:granularity (the convention must stay stated — peer-review
    minor 10 — but as a note, not a paragraph).
12. `7_Discussion.tex:254-264` and `:296-304` — second BT-SE telling and the
    redundancy-percentage retraction → a one-page appendix "Register of corrections
    to previously reported figures" (BT SEs, c = 7.66→2.52, redundancy %, routing
    ECE, correctness-blind ρ). The Discussion keeps a five-line summary table with
    pointers. Corrections affecting numbers quoted in this thesis stay in text once.
13. `7_Discussion.tex:113-124` — the side-channel detective story (two systems that
    never entered a run) → same appendix; one line stays in the self-check list.
14. Repetition of the eleven-fold/+10.3% fact — keep `1_Introduction.tex:236-240`
    and the derivation at `6_Results.tex:655-691`; convert
    `3_System_Architecture.tex:22-25` and `:183-185` to bare cross-references.
15. Void-marker boilerplate ("computed on a superseded tree… void as to values") at
    `3_System_Architecture.tex:105-108`, `:199-203`, `6_Results.tex:565-569` → define
    the marker once (a footnote at first use), then use the bare marker.

---

## (e) What is missing for conviction — the absent "so what"

The thesis is unusually good at clear question + fair test + honest answer. The
stated consequence is sometimes deferred two chapters or omitted:

1. **Link 2's positive result is never connected to its own defeat.**
   `6_Results.tex:570-639` establishes rubric specificity at p = 1.21e-6 and ends on
   three caveats (`:625-629`) — but never says the sentence the argument needs:
   *these measurably more specific rubrics are the same rubrics that Section
   res-generic-judge shows leave the winner unchanged 99.4% of the time; specificity
   is real and, on this corpus, inert.* The reader must join `:570-639` to `:297-343`
   unaided; the join happens only at `7_Discussion.tex:69-77`. One closing sentence
   in res-rubric-null fixes it.
2. **Identification cost states its number but not its load.**
   `6_Results.tex:459-476` ends at "leaf-level judging is affordable… against a
   budget of about 10,000" and a caveat. What the reader is not told: per
   `7_Discussion.tex:286-287`, after the reliability-constant correction the
   identification-cost result "probably carries alone" the entire argument about
   choosing a granularity. That promotion — this small subsection is now
   load-bearing for the one remaining granularity argument — is stated only inside
   the debt section, where nobody looking for it will look.
3. **The 94.2/94.7 secondary outcome is stated without its consequence for RQ2's
   judge-side half.** `6_Results.tex:372-374` gives the numbers; the reading — the
   high-power metric says the partition changes nothing the judge does, which
   *answers the judge-side check of RQ2 negatively regardless of how the ρ contrast
   is scored* — is left for the summary (`:885-890`) and Conclusion. One sentence at
   the point of measurement would let the reader hold the tie-policy dispute in
   proportion: the disputed statistic is the low-power one.
4. **Polyhierarchy's consequence for the thesis question is absent.**
   `6_Results.tex:790-879` closes on the invariant and the routing mechanism; it
   never says what the retirement means for the argument (e.g., that the strict tree
   simplifies the instrument without costing the multi-membership the motivating
   example needed — the 0.1549 vs 0.1518 numbers at `:856-858` support exactly this
   and are left as bare facts).
5. **The domain screen's so-what is under-stated relative to its process story.**
   The consequence — *everything reported so far was measured on the one domain
   pre-designated as having nothing to detect, so the thesis's partition verdict is
   deliberately deferred to Run C* — is scattered (`6_Results.tex:755-759`,
   `:783-788`, `8_Conclusion.tex:110-115`). Stated once, plainly, at the top of
   res-law, it would also disarm the examiner's "why defend before Run C" question
   (peer-review defense question 10) instead of leaving the answer distributed.
6. **Chapter 5's summary answers the RQs; the Results chapter never says what the
   answers imply for the title.** The thesis is called TaxoArena / "Dynamic Domains";
   by the end of Results both the taxonomy's evaluative value (link 3) and the
   rubric's causal role (link 2→3) are negative on this corpus, but the sentence "the
   system this thesis built is, on this corpus, an instrument for measuring judges —
   and that is the deliverable" appears only at `8_Conclusion.tex:4-8`. The
   Results summary (`6_Results.tex:881-930`) is where a first-time reader decides
   what they have read; one sentence of consequence there changes the whole read
   from "project that did not work, honestly reported" to "measurement with a
   boundary result".

---

## (f) Top 10 edits, ranked by clarity gained per line changed

1. **State the argument in brief at the end of Section 1.1.** After
   `1_Introduction.tex:33` ("It does not deploy a production router."), add one
   paragraph of five sentences — the elevator version of section (a), in the
   author's own words. ~8 lines added; it is the highest-leverage change in this
   list because every subsequent chapter is then read against a known destination.
   (The Conclusion's "set out to validate a taxonomy and ended by measuring a
   judge", `8_Conclusion.tex:4-5`, belongs in this paragraph too — the best sentence
   in the thesis should not debut on the last pages.)

2. **Make the Introduction's Contribution 2 agree with the registered verdict.**
   Replace at `1_Introduction.tex:356-357`: "A pre-registered no-partition baseline,
   and the null it returned." → "A pre-registered no-partition baseline, and what
   the registered rule returned." And replace `:361-364` ("The arms are
   indistinguishable on the high-power metric, and the apparent advantage on the
   low-power one survives only under one of two tie conventions") → "The arms are
   indistinguishable on the high-power agreement metric; under the registered rule
   the low-power rank-correlation contrast formally failed the null in favour of the
   partition-free arm, an outcome attributed — after the fact, and marked as such —
   to tie scoring (Section~res-c5)." Two sentences; removes the one place where the
   thesis still tells the pre-correction story (cf. peer-review issue 2).

3. **Rewrite the Chapter 2 Synthesis to promise what Chapter 5 delivers.** Replace
   `2_Literature.tex:663-671` ("TaxoArena addresses it through two integrated
   contributions… produces the per-domain profiles required by routing.") →
   "TaxoArena is built to test whether that substrate can exist: a corpus-induced
   partition supplies the cells, a reference-informed answer-key-blind arena judges
   inside them, and — because the corpus carries a verifiable key — every step of the
   chain from coherent cells to better judgments is separately measurable. Chapter 5
   reports which links held." ~6 lines changed; removes the document's worst
   transition.

4. **Lead the granularity section with the finding.** Replace
   `6_Results.tex:643-647` ("\textsc{measured}, and the analysis was fixed in
   writing before it was run. Three outcomes were named in advance, and…") →
   "\textsc{measured}: cells do not carry different true model rankings on this
   corpus, at any granularity from 14 to 152 cells. The analysis was fixed in
   writing before it was run — three outcomes named in advance, observed ρ fixed as
   primary — and that registration is the only reason the result is readable, since
   the disattenuated column moves the opposite way." Same content, finding first.

5. **Lead the domain-screen section with the result, not the reversals.** Retitle
   `6_Results.tex:745` "The Domain Screen, and Its Two Reversals" → "The Domain
   Screen: Law Reorders, Math Does Not", and move the current opening result
   sentence (`:752-755`) above the process narrative; demote "it is the most
   instructive methodological result in this project" (`:761-762`) to introduce the
   reversal paragraphs, not the section.

6. **Add the missing so-what sentence to the rubric-null section.** After
   `6_Results.tex:629` (end of the three caveats), add: "One consequence must be
   stated here rather than left to Chapter 6: these are the same rubrics that
   Section~res-generic-judge shows leave the judge's winner unchanged on 99.4% of
   comparisons. Link 2 holds — the cells produce measurably specific rubrics — and
   on this corpus that specificity is inert at the verdict." One sentence closes the
   chapter's largest inferential gap.

7. **Install the conventions box and strip the re-explanations** (full mechanism in
   section (d)). Concretely: insert the box after `6_Results.tex:19`; move
   Section res-tie-policy (`:437-457`) to directly precede res-c5; convert the
   explanatory repetitions at `5_Experimental_Design.tex:395-405` (duplicate 5/0
   example) and `8_Conclusion.tex:63-65` into references. Tables keep both tie rows
   everywhere.

8. **Move "What Is Not Implemented" (`4_Methodology.tex:264-299`) to an appendix**,
   leaving: "Several mechanisms described in earlier design documents — per-pair
   state machines, a global escape valve, fractional multi-leaf weighting, and five
   others — have no implementation; none is load-bearing for any result.
   Appendix~X inventories them." One page of main text recovered at zero honesty
   cost.

9. **Tell the BT-SE correction once.** At `4_Methodology.tex:152-166`, keep the
   first sentence, the 1/K-vs-1/K² fact, and "no confidence interval computed before
   the correction is quoted in this thesis"; move the derivation and the 44–209×
   consequence to the corrections register (edit 10), and let
   `7_Discussion.tex:254-264` shrink to a register pointer. Also replace the
   audience-breaking clause "this project has previously reported" with "reported by
   earlier versions of this pipeline" — same fact, no phantom prior document.

10. **Create the corrections register appendix** and shrink
    `7_Discussion.tex:246-332` around it: the five corrections (BT SEs, reliability
    constant, redundancy percentages, correctness-blind ρ, routing ECE) each get one
    line + pointer in the Discussion; full derivations, the side-channel narrative
    (`7_Discussion.tex:113-124`), and the retraction of never-quoted numbers
    (`:296-304`) live in the register. The reader of the Discussion then sees a
    disciplined summary instead of a second results chapter about numbers that are
    not in the thesis.

---

## Closing assessment

The thesis has a genuinely simple argument — five sentences, section (a) — and the
prose quality at the sentence level is high. What buries it is not dishonesty and
not complexity of the ideas; it is that the document is still partly addressed to
the project rather than to the examiner. Roughly a dozen passages speak to "earlier
drafts", "earlier descriptions", "previously reported" numbers, and conventions that
"became irreproducible" — a revision history the examiner never saw (nine such
addresses: `3_System_Architecture.tex:12`, `4_Methodology.tex:97`, `:154`, `:266`,
`5_Experimental_Design.tex:290`, `:427`, `6_Results.tex:466`, `:794`,
`7_Discussion.tex:202`). Each is honest; collectively they cast the reader as an
auditor of the project instead of a reader of the argument. The honesty machinery
should be *consolidated* — one conventions box, one void-marker definition, one
corrections register, one scar per rule — so that the argument (clear question, fair
test, honest answer, stated consequence) is what fills the running text. Every
guarantee survives that consolidation; only the repetition does not.
