# External review — TaxoArena Master's thesis

Reviewer role: external examiner, first read of the document as it stands on
2026-07-31. Scope: argument, structure, framing, defensibility. This review
sits above `docs/thesis-audit-2026-07-31.md` (line-level staleness; its A1–A7,
A12–A14, B5, B7, B9 are treated as fixed or in hand and are not re-litigated
here). Line numbers are from the files as read on 2026-07-31.

---

## 1. Overall verdict

**Major revision — but for completeness, not for soundness.** The scientific
core of this thesis is unusually good for a Master's project: a judge
measurement with matched controls, pre-registered decision rules that were
allowed to fail, a corrections register that reports the apparatus's own
errors, and negative results stated as findings rather than buried. If the
document matched its own evidence base, this would be a minor-revision
verdict. It does not, in one decisive way: **the thesis currently does not
answer its second research question anywhere in its body.** RQ2's results
section (`5_Results.tex:499-541`, `sec:res-c5`) is two sentences and a TODO;
the Conclusion's RQ2 answer is a comment block
(`6_Discussion_and_Conclusion.tex:431-442`); the pre-registration outcome
column is empty (`A_Tuning_Protocol.tex:128-150`); and sixteen
cross-references route the reader to the stub. Meanwhile the Abstract already
reports the RQ2 outcome in full (tie rate 13.0% vs 10.9%, 8/8 domains,
`e_Abstract.tex:75-83`). An examiner who reads Abstract → Results → Conclusion
finds a promise, then a hole, then a comment. No defense survives that in its
current state.

The second-order problem is that the thesis's headline evidence base — the
settled 8-model RESOLVED batch — has no home section. Its numbers (196/200
rank recovery, 86% conditional agreement, the 13.0/10.9 tie decomposition)
appear in the Abstract (`e_Abstract.tex:61-63`), the chapter summary table
(`5_Results.tex:1479-1490`), and the Conclusion (`6_Discussion_and_Conclusion.tex:381-384`),
and are derived nowhere. Every judge-mechanism section in Chapter 5 argues
from Run A, the pilot whose comparisons were half format-decided. The
strongest data the project owns is currently citation-only. Conversely the
material that *is* fully written — the construction half — is the part the
thesis itself declares to be the instrument, not the object of study.

What should reassure the author: nothing in this review found a claim that is
wrong *and* load-bearing *and* not already known to the author. The corrective
machinery (guidelines, audit, P4 addendum) has caught the substance. What
remains is to make the document say what the corrected record says, in the
right order, with the settled batch on the page — plus a handful of residual
framing inversions and unsupported-in-body numbers listed below, and a
prematter state (missing German abstract, template placeholders) that is
submission-blocking regardless of content.

---

## 2. The argument, chapter by chapter

### Abstract (`e_Abstract.tex`)

The English abstract is now the best-written statement of the thesis: it
carries the settled batch, the one-ordering-recovered-eight-times caveat
(lines 70-73), the decisiveness-not-ranking reading of RQ2 (75-83), and the
no-partition-arm disclosure (85-88). Two problems:

- **It is ahead of the body.** Every number in paragraphs 2–4 (196/200, 86%,
  13.0%/10.9%, "same ranking in every domain") lacks a supporting section in
  Chapter 5. The abstract is a set of promissory notes until `sec:res-c5` and
  a settled-batch section exist.
- **The German abstract is absent** (`e_Abstract.tex:15-40`). Blocking, as the
  file itself says. The embedded translate-last instruction (lines 29-37) also
  still describes the *pre*-settled state ("seven paired domains Chapter 6
  reports", "computer science... not yet in Chapter 6") and will mislead the
  author at translation time — the batch is complete.

### Chapter 1 — Introduction (435 lines)

The argument architecture is sound: motivation → what a partition is for →
system outline → three links → contributions → scope. The "argument, stated in
advance" subsection (lines 43-87) is a good device — it tells the reader the
punchline honestly instead of staging a reveal. Places where the chain breaks:

- **The chapter promises an RQ2 summary it cannot yet give.** The TODO at
  `1_Introduction.tex:73-81` and again at 285-297 (contribution 2). Until
  filled, the introduction sets up a question the thesis then visibly fails
  to answer.
- **Line 60: the 99.4% figure is quoted in the introduction without its
  provenance.** "a judge given no rubric at all reaches the same winner on
  99.4% of comparisons" — this is Run A, the pilot with the capture-gap
  defect. Agreement *between* the two conditions is not invalidated by the
  defect (both saw the same inputs), but the introduction should say "pilot"
  here; the reader has no way to know this number rides on a run whose
  comparisons were half format-decided until Chapter 5.
- **The scope section's condition four** (lines 390-397) leans on
  `sec:res-c5` for the fourteen-grid-steps sampler evidence — a stub.
- The three-links device (lines 182-217) works and is what makes the
  negative results legible. The known guideline violations inside it
  ("each separately falsifiable", the long RQ-rewrite apologia) are audit
  items C2/C3; noted, not re-argued.

### Chapter 2 — Background (724 lines)

The strongest conventionally-written chapter. Five literatures in dependency
order, each closed with what it does not settle, and a synthesis that narrows
the novelty claim to one sentence ("the coupling of validation and
estimation, and nothing wider", lines 698-702) instead of a gap-spotting
paragraph. The shortcut literature (`2_Background.tex:359-398`) is exactly the
right setup for Chapter 5 and the final paragraph (712-725) plants the
prediction without anticipating the result. Two observations:

- **The Discussion never returns to the synthesis's novelty claim.** The
  coupling that Section 2.6 claims as the contribution — a coherence gate
  *before* per-cell estimation — is precisely the thing the results then show
  to be evaluatively inert on this corpus (cells pass the gate; the estimates
  inside them resolve nothing). Chapter 6 should close that loop explicitly:
  what is the coupling worth now? One paragraph in `sec:conclusion` would do.
- Proportions: taxonomy induction gets ~130 lines while the judge-reliability
  section — the literature the thesis's actual finding lives in — gets ~150.
  Defensible, but if anything must be cut for length, cut from 2.2, not 2.3.

### Chapter 3 — Method (1,249 lines)

Honest and complete, but this is where the tool starts to outweigh the goal
(see §3 below). Chain problems:

- **A broken promise at `3_Method.tex:430-433`:** "Section~\ref{sec:res-construction}
  reports seed runs that stop in a period-2 cycle neither criterion can see."
  Section `sec:res-construction` does not report this. The period-2 sweep
  analysis — including the four uncertified seeds and the Fisher exact
  p = 0.0035 split by stopping arm — lives only in
  `E_Construction_Formalism.tex:241-267`. Either the promise or the content
  must move (my recommendation: move the finding into Results; it is a
  measured result about R3, not formalism).
- **The chapter argues against its own Chapter 4.** `3_Method.tex:497-507`
  correctly states that neither judging condition tests the partition and
  that pooling cancels the cell structure. Chapter 4's conditions table then
  says the opposite (see §3). Within-document contradiction on the central
  corrected claim.
- The Measurement Discipline section (D1–D5, lines 1106-1193) is distinctive
  and worth keeping, but it is the third place the tie-convention and
  threshold-withdrawal stories are told (also `sec:exp-metrics`, also
  `sec:res-tie-policy`). One telling should own each story; the others should
  be one-line pointers.
- The corpus-count paragraph (112-127) is exactly the kind of bookkeeping
  transparency an examiner wants. Good.
- Open TODOs that gate the chapter: 546-551 (withdrawn threshold not yet
  stated in text), 664-668 (options-mode contradiction, audit A14),
  1033-1036 (which agreement statistic feeds the exports — this one is a
  *correctness* question about the numbers Chapter 5 will quote, and must be
  resolved before the RQ2 rewrite, not after).

### Chapter 4 — Experimental Design (636 lines)

Fixes the configuration well; the pre-registration section with dated addenda
is a model of its kind. Breaks:

- **The conditions table contradicts the text around it.**
  `4_Experimental_Design.tex:399-404`: C5 is named "No partition" and its
  control column reads "**the partition itself**" (bold in source). The very
  next paragraph (408-416) and the P4 addendum
  (`A_Tuning_Protocol.tex:300-316`) demolish that. The table is what a
  skimming examiner reads. Rename the condition and rewrite the row.
- **A live framing inversion at 425-428:** "here the partition is the
  treatment, so pairing is what isolates it." The partition is not the
  treatment; the rubric is. This sentence survived the correction sweep.
- **Stale batch state throughout:** "Eight domains were run and seven are
  reported with results... computer science was still running" (46-56);
  twelve-model run conditions asserted as universal (58-66) while the settled
  batch is eight models (audit A15). The chapter describes the superseded
  batch as current.
- The registered threshold is stated as in force at 65-66 and withdrawn at
  578-588 of the same chapter. Both passages are honest; the sequencing is
  not. State it once as withdrawn, with the registration date, at first
  mention.

### Chapter 5 — Results (1,529 lines)

The judge half (5.2) is the thesis's best material and its internal logic is
tight: correctness-tracking → tie signature → trace inversion → capture gap
disclosed against interest → rubric-read-but-inert → tie-policy instability.
The controls-that-share-every-confound discipline is real, not rhetorical.
The partition half (5.3) is equally strong: the J-floor table
(`tab:j-floor`) is the single best construction-validation exhibit in the
document. Breaks:

- **`sec:res-c5` is a stub** (499-541). Everything downstream of it — the
  chapter summary's RQ2 row (1492-1501, currently a TODO comment plus
  withdrawn numbers), the Conclusion's contrast bullet, sixteen
  cross-references — dangles. This is the revision.
- **The settled batch has no section.** "What Was Run" (63-174) still says
  "an eighth paired domain still running" and "two runs are outstanding"
  (64-68, 131-137); the batch is complete, in RESOLVED mode, on a different
  roster than the one this section describes. The chapter needs a run-record
  entry for the settled batch and a section deriving 196/200 (with the
  one-ordering-in-7/8 caveat attached at the point of derivation, not only in
  the Abstract — audit A11).
- **Every §5.2 mechanism result is Run A.** That is defensible — the strata
  and controls are within-format and survive the capture gap — but the
  settled batch's corroborations (tie decomposition at 8 models, the
  off-subject/on-subject null, the 77.8% on-subject routing figure) are
  exactly what would let the chapter argue the mechanism on clean data. None
  is in the chapter. The interpretation doc's §4.2/§4.3 distance-ladder and
  fixed-effects nulls are publishable-quality analyses that currently exist
  only in `docs/`.
- **Line 588-595 is now half-false:** "the decisive experiment (withholding
  the multiple-choice options from the judge while holding the question set
  fixed) has not been run." The settled batch runs RESOLVED mode, which *does*
  withhold the options block (while injecting each model's selected option as
  text — `B_Judge_Generation.tex:135-144`). The registered P5 options-blind
  arm remains un-run, and `A_Tuning_Protocol.tex:210-213` correctly warns
  RESOLVED must not be reported as satisfying it — but this sentence, as
  written, tells the examiner the options question is untouched when the
  thesis's own headline batch is the intermediate condition. State the three
  rungs (OPTIONS / RESOLVED / options-blind) once, and say which rung each
  result sits on.
- The two-routing-paths disagreement (944-960) is disclosed as "not
  diagnosed". Honest, but it sits under a table whose pool column the reader
  has just been invited to use; a one-line forward pointer from the table
  caption itself would prevent misuse. (Run-pool staleness is audit B6.)

### Chapter 6 — Discussion and Conclusion (589 lines)

Argues almost entirely from what Results established — good — with three
exceptions:

- **`6_Discussion_and_Conclusion.tex:37-39`:** "This is an inference from the
  mathematics and law runs" — the section's own evidence base predates the
  settled batch, which the Abstract says spans eight domains. The inference is
  now stronger than the text claims; update, and cite the batch.
- **The Conclusion's contribution list** (380-401): item 1's 196/200 and item
  5's arm contrast cite no section (item 5 is a TODO). The five-measurements
  frame is right; the citations under it do not yet exist.
- **The future-work list** (499-589) is partially overtaken: item 2
  (options-blind arm) needs the RESOLVED-rung restatement above; item 3 says
  "the mathematics re-run... is the one measurement that would let the thesis
  say anything about mathematics" while the settled batch includes a
  mathematics run — reconcile with the P4 addendum's "open rather than
  answered" ruling.
- The limitations material is spread across §6.4's three subsections plus the
  debt register plus per-result caveats (audit B12; guidelines §5 wants one
  section, four items). Items 6 and 7 of the interpretation doc's ranked list
  (eight-domains-are-one-test; hyperparameters fitted not confirmed) are
  still missing from the chapter; both are one sentence each.

---

## 3. Framing check: arena as goal, tree as tool

The declared hierarchy — arena is the object of study, taxonomy is the
instrument — is stated clearly and early (`e_Abstract.tex:56-57`,
`1_Introduction.tex:134-149` "The induced taxonomy is *not* the contribution
of this thesis"), and Chapter 5's judge-first ordering honors it. But the
document keeps the promise rhetorically and breaks it by volume and in a
handful of surviving sentences.

**Residual inversions (each should be fixed):**

1. `4_Experimental_Design.tex:427` — "here the partition is the treatment, so
   pairing is what isolates it." Direct inversion; contradicts
   `3_Method.tex:502-507` and the P4 addendum.
2. `4_Experimental_Design.tex:399-404` — conditions table: C5 = "No
   partition", controls "**the partition itself**".
3. `02_Prematter/g_Nomenclature.tex:25` — "$\Delta\rho$ ... per-leaf arm minus
   partition-free arm." There is no partition-free arm. The nomenclature is
   the last place a stale frame should survive, because it is read as
   definitional.
4. `5_Results.tex:53` — reading-conventions box: "Positive favours cell-scoped
   per-leaf judging; negative favours the generic-rubric arm" is fine, but the
   box still frames Δρ as a headline convention for a chapter whose own
   metrics section demoted ρ to continuity-only. Keep ρ's row, but the box
   should say what `sec:exp-metrics` says: reported, not relied on.
5. The title (`b_Meta.tex:32`): *"Query-Adaptive Multidimensional Ranking for
   Agents in Dynamic Domains."* Every content word names the instrument or
   the aspiration (ranking, agents, dynamic domains); none names what the
   thesis actually measured (an LLM judge on a keyed corpus). "for Agents"
   promises a routing consumer the thesis explicitly does not build or test
   (`6_Discussion_and_Conclusion.tex:581-587` lists the routing check as
   never done). I would not fail a thesis for its title, but this title sets
   the examiner up to grade the document against a deliverable it disclaims
   in its own scope section. Consider "…: Measuring an LLM Judge under a
   Corpus-Induced Partition" or similar — the Abstract's own instrument
   sentence is the best title-source in the document.

**Volume check.** Outside Results, construction-side material ≈ 1,650 lines
(Method §§3.1–3.3 ≈ 440; Appendix E 900; Appendix A's parameter/ablation half
≈ 150; Appendix C 107; Appendix G 52) against arena-side ≈ 880 (Method
§§3.4–3.6 ≈ 550; Appendix B 177; Appendix D 156). Roughly 2:1 for the
declared *instrument*. Inside Results, the partition section (597-1461) is
about twice the judge section (176-596) — and the judge section's strongest
data is not yet in it. After the RQ2/settled-batch rewrite this ratio will
improve on its own; the E cut recommended in §6 fixes the rest. The framing
sentence at `E_Construction_Formalism.tex:6-10` ("the pipeline is the
instrument rather than the contribution") is correct and currently sits on
top of the single largest chapter-equivalent in the document.

**Where the framing is kept well:** `3_Method.tex:134-149` (instrument status
argued from a measurement, not asserted); `A_Tuning_Protocol.tex:41-47`
(minClusterSize as budget choice); `5_Results.tex:3-18` (mechanism order);
the Abstract throughout.

---

## 4. Claims triage

Bin (a): supported by the data as run. Bin (b): not supported now, defensible
with more judge budget / larger query set — with what it would take. Bin (c):
not rescuable by budget under this design.

| # | Claim | Bin | Basis / what would settle it / why unrescuable |
|---|---|---|---|
| 1 | The judge's verdict tracks answer correctness, not reasoning quality | **(a)** | Converging measurements with matched controls: tie rate triples where key stops discriminating; trace inversion survives capability control; rubric-free judge reaches same verdicts; off-subject questions judged at on-subject rates (verified batch fact). Strongest claim in the thesis. |
| 2 | Rank recovery 196/200 (98.0%) on key-decidable pairs | **(a)** — once written into the body | Supported by the settled batch, **provided** the one-ordering-recovered-eight-times qualification travels with it everywhere (currently only in the Abstract). Without the qualification it overstates by implying eight independent validations. |
| 3 | Cell-scoped rubric changes decisiveness (13.0% vs 10.9% ties, 8/8 domains), not ranking | **(a)** for the effect; **(b)** for attributing it to the *rubric* | The effect is robust. Attribution is confounded by the four-way arm bundle (JSON tie field vs `[[C]]` token, `tab:arm-differences`). The isolation run — MT-Bench system prompt through the rubric arm's own template/parser — is one condition, one domain, ~5k judge calls (`B_Judge_Generation.tex:108-111` already says it is cheap). Until run, claim the bundle, not the rubric. |
| 4 | Conditional-on-committing accuracy differs (86.0% vs 87.2%, sign test p = 0.020) | **(a)** pooled, weakly; **(b)** per domain | Rests on n = 37 both-committed discordant pairs; significant in no single domain. Per-domain resolution needs ~8× the comparisons: ≈ 50k additional judge calls across eight domains. Worth stating as pooled-only until then. |
| 5 | Construction reaches certified fixed point; gate calibrated between two nulls; rubrics cell-specific (p = 1.2e-6) | **(a)** | Links 1 and 2. Bounded caveats already attached (lexical measure; untracked null artifacts; birth-floor drift). |
| 6 | Cells do not carry different true rankings (granularity flatness; leaf-substructure null) | **(a)** within stated power bounds | Ground-truth-only, pre-registered, correctly bounded (signal below ~6 pts at leaf granularity undetectable). |
| 7 | Per-cell capability profiles | **(b)**, with a hard ceiling | Needs ~143 comparisons/pair vs 1.6–5.0 achieved. Cost: ~143 × 7 adjacent pairs × 52 cells × 2 calls ≈ **100k judge calls, ~10× the batch budget** — *and* ≥140 held-out queries per cell where cells now hold ~30–45, so the corpus must grow ~4×, or query-reuse dependence swamps the fit. And on *this* corpus/roster, claim 6 caps what could be found: budget buys precision on differences the null says are ≲ noise. Honest statement: defensible in principle on a larger corpus with a clustered roster; not on this one at any budget. |
| 8 | Rubric matters where correctness is not checkable (the routing regime) | **(b)** | Currently \textsc{argued} only. Two rungs: the registered P5 options-blind arm (one domain, both arms, ~10k calls — cheap, registered, blocked only on roster trace-completeness) tests the near version; the real version needs a non-keyed corpus with an external quality reference (annotation cost, not judge budget — order of 50–100 expert-graded items per cell to seed a reference). The thesis correctly refuses to claim it now; keep it that way. |
| 9 | Heterogeneity tests (Cochran's Q null everywhere) | **(b)** | Underpowered at 1.6–5.0 comparisons/pair; same arithmetic as claim 7 (~100k calls). Until then, report Q as uninformative, not as evidence of homogeneity — the granularity null (claim 6) is the evidence of homogeneity, and it is ground-truth-based. |
| 10 | Judge memorisation bounded | **(b)** | Paraphrase-consistency probe or post-cutoff probe set: one domain, ~5–10k calls plus probe construction. Named as future work; currently an open construct-validity hole the thesis discloses correctly. |
| 11 | Any claim that the *partition* helps or hurts judging | **(c)** | No arm removes the partition; pooling per-cell statistics is arithmetically identical to a domain fit (max |θ| diff 0.000). A real no-partition arm is a new scheduler condition, not budget on existing arms. The thesis has internalised this everywhere except the three inversion sites in §3 above. |
| 12 | Δρ as a decision statistic for anything | **(c)** | Run-to-run spread (0/+6 grid steps on a scheduler-seed change) exceeds the registered threshold 3–4×. More seeds measure the scheduler, not the arms (guidelines §"Do not"). Dead; keep it dead. |
| 13 | Verbosity/capability deconfounding on the settled roster | **(c)** on this batch | Median response length spans 6.79× and correlates with capability by roster construction (`D_Model_Rosters.tex:51-58`). Budget cannot fix a roster property; a length-matched re-run is a new roster (and the 12-model roster that had the control produced the superseded batch). The free partial fix — refit on the within-3×-band subset of the 8 models — is a reanalysis, not a run, and would bound the damage. |
| 14 | "for Agents" / routing utility of the profiles | **(c)** | No router exists, held-out routing is unvalidated (`sec:arch-limits` item 4), and claim 6 removes the premise on this corpus. Correctly disclaimed in scope; the title should stop implying it (§3). |

---

## 5. Unsourced-but-asserted claims

Rhetoric that outruns its on-page support. The audit caught stale numbers;
these are claims whose *support is absent or unlocatable*, including claims
whose only support is a stub.

1. **196/200 and 86% — headline numbers with no derivation anywhere.**
   `e_Abstract.tex:61-63`, `5_Results.tex:1479-1483` (summary table),
   `6_Discussion_and_Conclusion.tex:381-384`. No section computes, tabulates,
   or sources them; the summary table's "Where" column for RQ1 points at
   §§5.2.1–5.2.5, none of which contains them. Until the settled-batch
   section exists, these are assertions.
2. **The law reliability-ceiling range, quoted twice, derived nowhere.**
   "each leaf's ground-truth ranking agrees with the domain ranking at
   Spearman 0.895 to 0.993, against 0.873 to 0.970"
   (`6_Discussion_and_Conclusion.tex:69-71` and again 452-455). Ground-truth
   only, so plausibly sound — but no Results section, table, or script
   reference carries it. It is the load-bearing number in the
   "bounds any positive result" argument; give it a home and a source.
3. **Every claim citing `sec:res-c5`** — sixteen sites (audit A16) — is
   currently supported by a stub. Includes the Chapter 5 summary RQ2 row,
   Intro scope condition four (`1_Introduction.tex:390-397`), and Discussion
   `6_Discussion_and_Conclusion.tex:39-44`.
4. **"Qwen3-Embedding-8B ... has the property"** (`3_Method.tex:191-193`) —
   the MRL-prefix property of the one embedding model everything rests on is
   asserted with no citation, no measurement, and (per the same paragraph) an
   unrecoverable model revision. Either cite the model card/paper for
   MRL training, or measure it (prefix-vs-full-width retrieval agreement on
   the cached vectors — the vectors are retained at full width, so this is a
   free offline check), or mark the sentence \textsc{argued}.
5. **"checked rather than assumed: a rebuild ... reproduced the then-frozen
   artifact's cell partition exactly, and all 50 of its accepted-split
   separations to nine decimal places"** (`3_Method.tex:1213-1216`). The
   "then-frozen artifact" is unnamed, is not the frozen artifact of
   `tab:frozen-artifact` (which has 70 accepted edits, 68 splits —
   `E_Construction_Formalism.tex:865-869`), and no run/commit identifier is
   given. As written, the reproducibility check cannot be located, and the
   50-vs-68 mismatch invites the suspicion that the check certifies a
   different tree than the one the thesis reports. Name the artifact and
   date, or soften the claim.
6. **"That control was fixed in advance"** for the correctness-blind
   selection control (`5_Results.tex:238-240`). None of P1–P5 in
   `A_Tuning_Protocol.tex:110-213` registers this control. If it was fixed in
   a document, name it; if it was fixed informally, say "chosen before
   computation" and drop the pre-registration cadence — the thesis has earned
   real credibility on registration precisely by being scrupulous about what
   is and is not registered.
7. **"the pairing runs above 99% on mathematics, law, history and
   psychology"** (`5_Results.tex:148-156`) vs `B_Judge_Generation.tex:113-116`
   ("100% on mathematics, physics, psychology and philosophy, and 99.6% on
   law and engineering"). Two overlapping-but-different overlap sets, neither
   labelled with its roster/batch (audit B2 notes the staleness; the
   additional point here is that *both* passages present their figures as
   the measurement, and a reader cannot tell which run either belongs to).
8. **"routing raised held-out pool coverage to 246 of the 277 law
   questions"** (`5_Results.tex:107-116`) — the footnote scrupulously
   corrects an earlier 297 denominator, good; but the 277 itself is "the
   in-scope count the run recorded" with no export named, in a chapter that
   elsewhere names a CSV for every number. Minor; name the log field.
9. **Anchor-table pool column presented above a disclosure that it does not
   describe what was judged** (`5_Results.tex:904-960`). The table is sourced;
   the issue is placement: the "two routing paths disagree — NOT DIAGNOSED"
   admission comes after the table has already been read. Move one warning
   sentence into the caption.
10. **The missing 77.8% on-subject figure.** Not an unsourced claim but its
    mirror image: a verified, favourable, framing-critical measurement
    (routing is subject-coherent at judging time; per-domain 68.4–94.6%) that
    exists only in `docs/`. The thesis asserts "their runs are close to what
    their names suggest" for law and math (`5_Results.tex:968-977`) from label
    agreement alone; the on-subject measurement is the direct evidence and
    one sentence (audit C8) puts it on the record.

---

## 6. Structure and proportions

Measured line counts (source lines, `wc -l`): Intro 435 · Background 724 ·
Method 1,249 · Experimental Design 636 · Results 1,529 · Discussion+Conclusion
589 = **5,162 main text**. Appendices: A 336 · B 177 · C 107 · D 156 ·
**E 900** · F 210 · G 52 = 1,938.

**Chapter order: right.** Method before Experimental Design is defensible and
the forward references are tolerable. Do not reorder chapters; reorder within.

**The balance is wrong in one place and about to be wrong in another:**

1. **Results is 30% partition, should be judge-led by weight as well as by
   order.** Currently §5.3 (partition, ~930 lines) is twice §5.2 (judge, ~420
   lines) while the settled batch is absent. The RQ2 rewrite plus a
   settled-batch section (~250–350 lines from the interpretation doc's §§1,
   3, 4) rebalances this without cutting anything. Effort: 2–3 days, all
   material already exists in `docs/results-interpretation-2026-07-31.md`
   (respecting its retracted §4.4/§4.6 provenance claims — use the corrected
   77.8% figures and recompute the on/off-subject regression as the audit's
   retraction block requires).
2. **Appendix E at 900 lines is ~3× what the main text uses.** Dependency
   audit of what Chapters 3/5 actually reach into E for: the
   chance-corrected score definition and its expectation (~40 lines,
   E:637-676); the four-stage acceptance path and proposal gate
   (~120 lines, E:677-716, 741-849); the routing gate/beam/floor that
   limitation 4 depends on (~90 lines, E:494-621); the stopping-criteria
   detail and the twenty-seed period-2 finding (~70 lines, E:201-273); the
   single-parent invariant (~25 lines, E:875-900). Total load-bearing:
   **≈ 350 lines.** The remainder is engineering documentation with no
   inbound dependency: the six-phase walkthrough table (E:46-150, duplicates
   Method §3.2 at lower altitude), the NiW regulariser that by its own text
   "does not participate in routing" and is diagnostic-only (E:385-431), the
   MRL slice discussion duplicating Method 3.2 plus an ablation-confound
   essay for an ablation that was never run (E:432-493), dead-code notes
   ("retained dead code rather than a live mechanism", E:578-584). Cut E to
   ~400 lines; move the period-2 sweep finding to `sec:res-construction`
   (fixing the broken promise at `3_Method.tex:430-433`). Effort: one day.
3. **One appendix table belongs in a chapter:** `tab:arm-differences`
   (`B_Judge_Generation.tex:76-97`). It is the reason the decisiveness result
   cannot be attributed to the rubric — load-bearing for RQ2's reading — and
   it is hidden in the judge-generation appendix. Move to Chapter 4 beside
   the conditions table (the interpretation doc's V4 says the same). Effort:
   an hour.
4. **One chapter-resident block could shrink toward an appendix:** the
   war-story footnotes under D1–D5 (`3_Method.tex:1128-1182`). Keep the five
   rules and one instance each; the second and third instances per rule
   (three footnotes, ~40 lines) can move to the corrections register, which
   is their natural home. Effort: an hour. Do not move the rules themselves —
   they are the thesis's voice at its best.
5. **Appendix C must resolve its own TODO** (`C_Metric_Definitions.tex:9-16`):
   Dasgupta cost, WLP, AvgMatch and routing ECE are defined and never cited
   from Results. Cite AvgMatch (it is used, G:31-39) and ECE (used,
   limitation 4), cut or one-line the other two. Effort: an hour.
6. **Appendix A is doing three jobs** (parameters, registrations,
   corrections) and doing them well; leave it, but the corrections register
   is referenced often enough from Chapter 6 that a `\label` per entry would
   help the reader who arrives mid-list.
7. **Prematter is template-state and submission-blocking:**
   `b_Meta.tex:33` author "First name middle name last name"; :43-45 course
   "Mein Studiengang", matriculation "XXXXXX", advisor "My advisor, M.Sc.";
   :49-50 keywords "Keyword1, Keyword2, Keyword3" (these print under both
   abstracts); :73-77 faculty/institute/department are the template's process
   engineering defaults (Fakultät III, Dynamik und Betrieb technischer
   Anlagen) — almost certainly not this thesis's faculty. Plus the missing
   German abstract. Effort: an hour plus translation, but zero of it can be
   skipped.

**Merge/split verdicts:** the 2026-07-31 file merges (Method,
Discussion+Conclusion — `0_Text.tex:1-15`) were right. No chapter needs
splitting. `sec:res-law` is misnamed (it is the domain screen on all fourteen
domains, not a law section) — rename to `sec:res-screen` when touching the
sixteen dangling refs anyway.

---

## 7. Style / slop findings

The thesis's terse declarative register ("\textsc{measured}.", "Write it that
way") is the author's voice and is not flagged. The document is largely free
of classic AI slop — no banned-word hits in author prose (the one grep hit,
"robustness" at `2_Background.tex:31`, is HELM's own metric name and stays).
What follows are the patterns that genuinely weaken the text, worst first.

**1. Faux-insight / drama setups around results.** The findings are strong
enough not to need staging:

- `5_Results.tex:209-212`: "It arrived from a direction nobody was looking
  in: the tie rate was recorded for the Bradley–Terry sufficient statistics,
  not as a test of anything." — "nobody was looking in" is the
  what-everyone-missed move, plus a colon reveal. The second half of the
  sentence is the substance; keep it, cut the setup.
- `5_Results.tex:784`: "Four things follow, and the third is the one that
  matters most." — announce nothing; let point three carry its own weight
  (its first clause already re-announces itself at 790-791).
- `5_Results.tex:790-791`: "Third --- and this is the objection a reader
  should raise before the second point is allowed to stand ---" — a
  double-em-dash interruption staging an objection the text then answers
  itself. State the control result directly.
- `5_Results.tex:815-816`: "That second question is
  Section~5.3.4, and its answer is not the convenient one." — trailer-voice
  kicker. Cut "and its answer is not the convenient one."

**2. Aphorism kickers as section-enders.** Individually fine; as a recurring
sign-off they become a rhythm the reader starts to brace for. At least five
sections end on one:

- `5_Results.tex:838-839`: "a gate can be right because its units are right,
  without improving the number it gates" (italicised, second appearance at
  874-878).
- `6_Discussion_and_Conclusion.tex:164-165`: "A comparison arm is a
  measurement and has to be checked like one."
- `6_Discussion_and_Conclusion.tex:355-359`: "…the errors the apparatus
  caught and the debt it still carries are two views of the same measurement
  discipline." — recap-plus-profundity ending; the section did not need a
  moral.
- `3_Method.tex:1114-1116`: "A rule stated with the error behind it can be
  checked; a rule stated as foresight has to be taken on trust."
- Keep the two or three that earn it (the gate one is genuinely the point of
  its section); delete the rest and end on the last concrete fact.

**3. Binary-contrast scaffolding, systemic form.** The explicit "not X. It's
Y." construction appears once (`1_Introduction.tex:184-185`, "is not one
claim. It is a chain of three" — load-bearing, keep). But its academic cousin
— "X rather than Y" — appears **193 times** (~once per 27 lines; 38× in
Results, 37× in Method, 26× in Appendix E). Where the contrast is the finding
("verified rather than asserted", "a budget choice rather than a statistical
requirement") it earns its place. Where it is decoration it flattens the
prose: e.g. `5_Results.tex:6` "load-bearing rather than editorial";
`3_Method.tex:354` "a budget choice rather than a statistical requirement" is
then re-made at `5_Results.tex:841-842` and `A_Tuning_Protocol.tex:41-43`
(the same contrast, three tellings). A pass that deletes the "rather than"
clause wherever the sentence survives without it would remove 50+ instances
and sharpen the rest.

**4. "worth stating/naming/carrying" throat-clearing.** Six instances
(`3_Method.tex:112, 487, 615`; `4_Experimental_Design.tex:162, 171`;
`2_Background.tex:154`). Each precedes something the text then states anyway.
Delete the announcement; state the thing.

**5. Em-dash pressure at the top of the range.** ~1.4–1.8 `---` per source
page in Chapters 4–6 against the guidelines' "a couple per page at most".
Mostly fine individually; the clusters to break up are interrupted-list
constructions like `5_Results.tex:790-791` (quoted above) and
`5_Results.tex:830-838` (three dash-pairs in one paragraph).

**6. Repeated self-exemption formula.** "It is stated here because…", "It is
recorded here because…", "named because…" — the justify-this-paragraph's-
existence move — recurs across Method and the appendices
(`3_Method.tex:679-684`, `E_Construction_Formalism.tex:397-399`,
`A_Tuning_Protocol.tex:286-287`, others). Twice is a discipline; a dozen
times is a tic. Where the reason is obvious from placement, cut the meta-
sentence.

**Not flagged:** the \textsc{measured}/\textsc{argued} tags (a genuine
epistemic device, consistently applied); the assertive section headings; the
one-sentence verdict paragraphs; the corrections-register candour. These are
the document's character and its best asset.

**Terminology consistency (from question 1's checklist):**

- *cell vs leaf*: defined as interchangeable (`3_Method.tex:349-351`,
  `g_Nomenclature.tex:31`) — but "leaf" then dominates the partition half of
  Results (86 uses in Ch. 5) and "per-leaf" survives in arm names. Pick
  "cell" for evaluation contexts, "leaf" only for tree structure, and rename
  "per-leaf arm" out of `5_Results.tex:53, 482, 486` and
  `g_Nomenclature.tex:25`.
- *"generic" is ambiguous between two conditions.* C3 (\textsc{generic},
  export `GENERIC_JUDGE`, pilot only) and C5 (generic MT-Bench-style rubric,
  every paired run) are both called "the generic arm" —
  `5_Results.tex:411-476` uses "generic" for C3; `5_Results.tex:499-541` and
  the Abstract use it for C5. An examiner will conflate the pilot's 99.4%
  verdict-identity (C1 vs C3) with the paired decisiveness contrast (C1 vs
  C5) — the two results have different rosters, modes and meanings. Give C3
  a distinct small-caps name ("\textsc{rubric-free}" fits its actual delta)
  and reserve "generic" for C5.
- *arm vs condition*: "condition" in Chapter 4, "arm" in Chapter 5-6;
  tolerable, but pick one in the conditions table caption so the mapping is
  explicit.
- *domain vs anchor*: handled well — `par:cell-count` fixes the referent, and
  the screen/adapted mismatch is disclosed at `5_Results.tex:980-988`. No
  action beyond keeping that paragraph.
- *MAIN vs cell-scoped*: consistent enough once "per-leaf" is retired.

---

## 8. The five things to fix before submission, ranked

1. **Write RQ2 into the body from the settled batch.** `sec:res-c5` (the
   three-part decomposition per audit A9's corrected instruction: tie rate
   13.0/10.9 in 8/8; conditional agreement with the sign test, pooled only;
   unconditional rate demoted to a labelled appendix line), the Chapter 5
   summary RQ2 row, the Conclusion bullet and per-domain outcome, the
   pre-registration outcome column, and the six TODO stubs. Settle the
   `3_Method.tex:1033-1036` exported-statistic question *first* — it decides
   which numbers are legal to print. This is the revision; nothing else
   matters until it is done. (2–3 days; all numbers exist.)
2. **Give the settled batch a derivation section in Chapter 5** and update
   "What Was Run": roster (D's `tab:roster-r8`), RESOLVED mode, 196/200 with
   the one-ordering-in-7/8 caveat at the point of derivation, the 77.8%
   on-subject line (audit C8), and the completed-batch run record. Until
   this exists, the Abstract's and Conclusion's headline numbers are
   unsupported assertions (§5 items 1–2). (1 day.)
3. **Kill the four surviving partition-as-treatment inversions:**
   `4_Experimental_Design.tex:427` ("the partition is the treatment"), the
   C5 row of `tab:arena-conditions` (:399-404) plus the condition's name,
   `g_Nomenclature.tex:25`, and the "per-leaf arm" label in Chapter 5's
   conventions box. These are the sentences an examiner will quote back at
   the defense, because they contradict the thesis's own P4 addendum.
   (Half a day.)
4. **Tell the options-mode story once, on three rungs.** OPTIONS (pilot and
   superseded runs) / RESOLVED (settled batch: options withheld, selected
   option injected, 97.6% of traces self-declare) / options-blind (P5,
   registered, not run) — and correct `5_Results.tex:588-595`
   ("the decisive experiment … has not been run") and the Discussion's
   future-work item 2 to say which rung the settled batch occupies and what
   P5 still adds. This resolves audit A14's contradiction *and* the
   staleness A14 does not cover. (Half a day.)
5. **Prematter and packaging:** German abstract; `b_Meta.tex` placeholders
   including the wrong-faculty template defaults and the abstract keywords;
   retitle or subtitle so the title names what was measured (§3 item 5);
   then cut Appendix E to its ~400 load-bearing lines and move the period-2
   sweep finding into `sec:res-construction`, closing the broken promise at
   `3_Method.tex:430-433`. (1–2 days plus translation.)

Everything else in this review — the style pass, the triage table's (b)-bin
runs, the C-appendix TODO — improves the thesis but would not change my
verdict. Items 1–4 would: with them done, this is a minor-revision document
with an unusually defensible negative result and the best
measurement-discipline record I have seen in a Master's submission.
