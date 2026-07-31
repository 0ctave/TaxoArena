# Thesis guidelines

Written 2026-07-31, after a day of re-running the arena and finding that several
central claims did not survive checking. Two problems showed up repeatedly: the
text defends itself far harder than a master's thesis needs to, and some claims
are stated more precisely than the evidence supports. This file is the rule set
for fixing both.

Every rule below exists because of something actually observed in the text or in
the data. Where that is the case, the reason is given — a rule you cannot check
is a rule you will not follow.

---

## 1. The story

Five steps. Everything in the thesis should attach to one of them.

1. **Problem** — leaderboards give one number per model; routing needs to know
   who is good at *what*.
2. **Idea** — split the question corpus into topic cells, rank models inside
   each cell.
3. **Build** — induce the taxonomy, write a judge rubric per cell, run pairwise
   comparisons, fit Bradley–Terry.
4. **Test** — compare the resulting rankings against how the models actually
   score on the answer key.
5. **Find** — it works at domain level; it does not resolve at cell level; and
   the cell-specific rubric makes no measurable difference, because the judge is
   mostly checking answers.

If a paragraph does not serve one of these, it is a candidate for cutting.

**The one-line version, already in the conclusion and worth keeping verbatim:**
*this thesis set out to validate a taxonomy and ended by measuring a judge.*

---

## 2. What the evidence supports

Write these as findings.

- The construction reaches a certified fixed point, its acceptance rule is
  calibrated in units of its own standard error, and its threshold sits between
  two measured nulls.
- Rubrics induced on the cells are specific to those cells against a
  size-matched random null.
- **The judge decides on answer correctness, not reasoning quality.** This is
  the strongest result in the thesis and it is supported several independent
  ways.
- The arena recovers the true model ranking well when that ranking is actually
  determined: ρ = 0.95 on a roster chosen for separability, on half the budget
  of the twelve-model runs.

Write these as limits, not failures.

- Per-cell rankings cannot be resolved on this corpus.
- The cell-scoped rubric does not beat a generic one.

---

## 3. What the evidence does NOT support

Do not write these. Each was believed at some point today and then checked.

- **"The partition improves ranking fidelity."** No arm in this thesis varies
  the partition. Both arms use the same cells, the same questions and the same
  aggregation; pooling per-cell statistics is arithmetically identical to a
  direct domain fit. The comparison tests the *rubric*.
- **"Δρ ≥ 0.007 is decisive."** Two runs of an identical configuration, differing
  only in a scheduler seed, gave Δρ of +6.00 and 0.00 grid steps. The registered
  threshold is smaller than the noise. Withdraw it explicitly.
- **"The judge is answer-key-blind at the prompt."** It is blind to the key, but
  it was shown the full option list on every run before 2026-07-31, and ~95% of
  traces state their own answer.
- **Any per-domain Δρ as evidence for or against the rubric.** On the 8-model
  roster both arms produced the *identical* ranking. There is nothing to compare.

---

## 4. Metrics

**Lead with per-verdict metrics.** Judge/answer-key agreement, tie rate,
position-flip rate. These have n in the hundreds to thousands and reproduce: the
tie rate replicated to 0.1pp across two seeds.

**Report ρ, do not lean on it.** One table, three decimals, one sentence of
interpretation. It is a rank correlation over 8–12 items and it is either noisy
(clustered roster) or saturated (separated roster). It has never discriminated
between the arms.

**Delete the grid-step machinery.** No quantisation arithmetic, no two-step
threshold, no discussion of the seam between 0.0069930 and 0.007. Replace the
whole apparatus with:

> ρ is reported to three decimals; differences below about 0.02 are within
> run-to-run variation.

**One tie convention in the main text.** Pick half-weighted, justify it in a
footnote, move the other to an appendix. Reporting both everywhere doubles every
table for a distinction no reader will use.

---

## 5. The limits, stated once

One short section. Four items. Not threaded through every paragraph.

1. **The judge checks answers, not reasoning.** On a corpus with an answer key, a
   capable judge finds the answer and the rubric adds little.
2. **Cells are too small to rank models inside them.** A cell holds around 35
   questions; separating two adjacent models would need roughly 140 comparisons.
   Structural, not a budget problem.
3. **The two arms differ only in the prompt.** Same cells, same questions, so the
   comparison tests the rubric and not the partition.
4. **One corpus, one judge model, one roster.** Nothing here shows the results
   transfer.

Add, in plain words, the transferable observation:

> Whether this approach can work depends on two numbers you can compute before
> running anything: how far apart the models are, and how many questions each
> cell holds. On this corpus both are too small. That is useful to know before
> building such a system.

---

## 6. Writing rules

### Do

- Say the result, then the caveat. One caveat, not three.
- Use plain words. "The judge checks the answer" beats "verdicts are conditioned
  on answer-level correctness rather than on the adjudication of reasoning."
- Define a term once, where it first appears.
- Put numbers in tables. Keep prose for what the numbers mean.
- State a limitation once, in the limitations section, and trust the reader to
  remember it.

### Do not

- **Do not hedge in the same sentence as the claim.** Pick one.
- **Do not repeat the pre-registration narrative.** Mention it once in methods —
  "analyses were specified in advance; see Appendix X" — and stop. It currently
  recurs as a defensive motif and reads as anxious.
- **Do not explain in the introduction that a research question was rewritten
  after seeing data.** One sentence in methods is enough and is the normal place
  for it.
- **Do not use "each separately falsifiable"-style framing.** Keep the three
  links, drop the epistemology: *"three things have to hold — the cells make
  sense, the rubrics differ, the judging improves. The first two hold; the third
  does not."*
- **Do not report a number without saying where it came from.** Every figure in
  the thesis should trace to a run, a table, or a file.
- **Do not mix number sources.** All ρ values quoted in the results were
  recomputed through one path (unpenalised MM fit, ground truth = accuracy on
  exactly the judged questions). These do **not** match the values the runs
  export, which apply a Jeffreys prior. Never quote both.

### Style (applies throughout)

- Banned: delve, foster, leverage, utilize, robust, streamline, paradigm shift,
  intricate, paramount, transformative, harness, elevate, showcase.
- No "not X, but Y" constructions. State Y.
- No colon reveals. No rhetorical questions. No summary-recap endings.
- No trailing *-ing* clauses that pretend to explain ("…, highlighting the
  importance of…").
- Active voice. Concrete nouns.
- Em dashes sparingly — a couple per page at most.

---

## 7. Keep exactly as-is

- **"Set out to validate a taxonomy and ended by measuring a judge."** The thesis
  in one line.
- The construction results — fixed point, chance-corrected acceptance, rubric
  specificity against the random null.
- The stratified judge analysis. The strongest empirical work in the thesis.
- The honesty about negative results. It is the thesis's best quality; the fix is
  to state them more simply, not to soften them.

---

## 8. Before submitting

- [ ] Every number traces to a run or a file.
- [ ] `sec:res-c5` renamed — it is not a no-partition baseline.
- [ ] The Δρ ≥ 0.007 threshold explicitly withdrawn, with the replicate that
      killed it.
- [ ] Limits appear once, in one section.
- [ ] One tie convention in the main text.
- [ ] Recent preprint citations re-checked — several are months old and
      unrefereed, and one has already been retitled.
- [ ] `arara main.tex` builds clean, no undefined references or citations.

---

## Related

- `docs/findings-2026-07-31.md` — the measurements behind sections 2 and 3
- `docs/prereg_generic_judge_baseline.md` — needs a dated addendum recording that
  Run B varies the rubric, not the partition
