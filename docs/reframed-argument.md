# What the taxonomy is for — the reframed argument

> **STATUS: SUPERSEDED (2026-07-30). Do not write from this document.**
>
> Its two central moves are both inverted by the eight-run paired arena result.
>
> 1. It argues that `Delta rho` should be abandoned because cells have no room to differ.
>    `Delta rho` is now the headline metric, and five of seven completed domains meet the
>    registered threshold of 0.007.
> 2. It frames the work as a pre-registered **negative** result. The work now has a
>    positive result with a confounded null inside it.
>
> The premise it tested was right and the inference from it was wrong. Cells really do not
> carry different rankings — but per-leaf judging still beats a partition-free arm, because
> the gain is **precision on one shared ranking**, not discovered specialisation. That
> distinction is the thesis, and this document does not contain it.
>
> Also stale: the rubric-specificity section (lines ~93-135) plans a null arm that has since
> run (Mann-Whitney one-sided p = 1.21e-6, 0.138 vs 0.012, terms in >= 90% of rubrics 0 vs
> 6). The flatness quartet and centred-residual quartet it quotes are on the never-restate
> list in `void-results.md` §3.
>
> **What survives:** the three-link decomposition (partition -> rubric -> ranking) at the
> top of the document. That is the thesis's spine and it is unaffected. Everything after it
> is history.

Status (original, 2026-07-27): **current**. This is the argument the thesis should make. It
replaces the framing in which the taxonomy's value is that its cells produce *different*
model rankings.

## The purpose of splitting

Splitting a cell **reduces the surface over which a judge must generalise**. That is the
whole mechanism. A judge asked to compare two answers about "Computer science" must hold a
rubric that covers operating systems, cryptography, group theory and time-series
diagnostics at once. A judge asked to compare two answers about "Time Series Model
Diagnostics and Validation" can be given a rubric that says what a good answer looks like
*there*.

The causal chain:

```
coherent cells  ->  specific rubrics  ->  better judgments  ->  ranking closer to ground truth
      (1)                  (2)                   (3)
```

Every claim the thesis makes about the taxonomy's evaluative value is a claim about one of
those three links. Naming them separately is what makes the negative results readable,
because they land on different links.

## RQ2 must be reframed

Current wording (`report/03_Content/1_Introduction.tex`):

> **RQ2.** Does evaluation within geometry-adapted leaf groupings improve ranking fidelity
> over flat MMLU-Pro domain groupings?

Read literally that is a question about link 3's *output* — do adapted cells rank models
more like ground truth. But the pre-registered discriminative analysis showed that the
premise underneath it does not hold on this corpus: cells do not have different true
rankings at any granularity. So a per-cell `Delta tau` between adapted and canonical
groupings is measuring a difference that has no room to exist, and a null there is
uninformative about the mechanism.

**The question the system actually poses is:**

> Does adapted grouping enable **better judging**?

That is a question about links 1 and 2 feeding link 3, and it is answerable with the same
arena. The difference matters for what gets reported: judge-vs-ground-truth agreement
within a cell, not rank divergence between cells.

## Link 3 — measured, and it is a corpus finding, not a system finding

`prereg_discriminative_power.md` (pre-registered, then run):

* Observed Spearman rho between cells is **flat** across granularity: 0.929 (14 domains) /
  0.922 (88 leaves, biased router) / 0.922 (87 leaves, correct router) / 0.905 (152
  leaves). Overlapping IQRs throughout.
* Flat across **routers** too: 87 and 88 leaves give rho = 0.922 identically, so a routing
  correction worth +10.3% J changes discriminative power by zero.
* Centering out each model's global mean leaves a residual of -0.119 / -0.024 / -0.024 /
  -0.024, all within 1.5-3.6x of the **mechanical centering null** `-1/(C-1)`. The correct
  statement is "indistinguishable from the centering null", not "zero".
* Roster spread is 54.1 accuracy points. rho ~ 0.92 was largely measuring "gpt-4o beats
  Llama-2-13b in every cell".

**Report this as a property of the corpus and roster, not of the method.** MMLU-Pro is
saturated for a 54-point-spread roster: cell identity contributes essentially nothing to
model ranking beyond global capability ordering, at any granularity from 14 to 152, under
either router.

Scope limits that must travel with it:

* Measured on each cell's own constituent queries and on ground-truth accuracy, not on
  routed held-out queries and not on judge verdicts. It **bounds** what an arena can
  discover; it does not predict what an arena will produce. The arena can show less
  discrimination than this, never more.
* Power: per-model per-cell accuracy has SE ~ 2.1 pp at 14 domains, 5.8 pp at 87 leaves,
  6.9 pp at 152. A null residual is consistent with "no cell-specific ranking signal" and
  with "a signal smaller than ~6 pp at leaf granularity". This analysis cannot separate
  them. The 14-domain measurement is the stronger evidence precisely because it is the
  low-noise condition and its residual is also at null.
* A roster clustered within ~10 accuracy points is untested and is the version of this
  question that could still come out positive.

**Crucially: none of this says anything about judge quality.** It measures whether cells
have different *true* rankings. Judge quality is the actual claim, and it is untouched by
this measurement. Do not let a reader collapse the two.

## Link 2 — partially measured, and it currently has no null

Does coherence produce more specific rubrics? This is an **offline** question — it needs no
arena — and it is pre-registered in full, with directional predictions and decision
thresholds fixed in advance, at [`prereg_rubric_specificity.md`](prereg_rubric_specificity.md).
That document is the authority; this is the summary.

Treatment arm measured on the 87 rubrics of the frozen artifact:

| measure | leaf-87 |
|---|---|
| rubric length | median 325 words, IQR [290, 382] |
| distinct content terms per rubric | median 165 |
| pairwise Jaccard between rubrics | median **0.073**, IQR [0.056, 0.099] |
| terms unique to exactly one rubric | **2275 (54% of vocabulary)** |
| terms appearing in >= 90% of rubrics | **0** |
| rubric vocabulary found in own cell's queries | median **0.234**, IQR [0.186, 0.321] |

Lexical only — content terms are lowercase alphabetic, length >= 4, stopped. No embeddings,
no judge calls.

**State clearly, every time this is reported: this is the treatment arm with no null. It is
not yet evidence.** The numbers are equally consistent with coherence producing specificity
and with the model writing varied prose about any 87 samples. Two confounds are already
identified and neither is controlled by the table above: topical breadth per induction batch
is not matched (a random 25-query batch spans 14 domains, a coherent one spans one concept,
and the direction of the resulting bias differs per measure), and the own-cell overlap
measure has a vocabulary-size confound that could make the random arm score **higher**
through breadth alone — the same shape as the CV-from-mean-shift and
disattenuation-past-1.0 errors already made in this project.

Two ways to complete it, in increasing cost:

* **The within-arm null — free, no Azure calls.** Compare each rubric's overlap with its own
  cell against its overlap with randomly chosen *other* leaf cells; both are leaf cells, so
  vocabulary sizes are comparable and the confound cancels. A generic rubric scores ~0. The
  decision rule is fixed in advance in the pre-registration (evidence at median >= 0.05 with
  >= 75% of cells positive; no signal at <= 0.02).
* **The three-arm test — ~174 additional inductions, no judge calls.** leaf-87 (done) /
  random-87 with matched cell sizes / domain-14. The control arm already half-exists:
  `RANDOMNULL_BASELINE` (`guides/thesis-reproduction.md`) shuffles query assignments while
  preserving exact node sizes and topology, which is precisely the matched random partition
  required. It was built as a *ranking* baseline; inducing rubrics over it turns it into the
  null for this link.

The sharpest discriminator is "terms in >= 90% of rubrics". A random cell contains chemistry,
law and history at once, so its rubric must fall back on domain-general language. If that
generic core is present across random rubrics and absent from leaf rubrics, surface reduction
is demonstrated. If both are ~0, the instrument cannot see the difference and the test is
**inconclusive rather than negative** — that distinction must survive into the write-up.

Note the scope limit the pre-registration states and that must be repeated: this licenses the
**premise only**. "Rubrics are more specific" reads as though it implies "judges are better".
It does not. That is link 3, and it needs the arena (condition C3: MAIN vs GENERIC_JUDGE).

## Link 1 — the construction guarantees

Link 1 (does the construction produce coherent cells?) is where the project's measured
machinery lives, and it is the best-evidenced link:

* the chance-corrected separation score and its two nulls (`separation_null_by_size.md`),
* the paired-bootstrap acceptance gate (`frozen-artifact.md`, `acceptanceZ`),
* the fixed-point certificate,
* the named limitation: 6 of 27 clean-null splits cannot be distinguished from a cut
  through their own node's elongation, and 19.7% of leaf-held queries sit under at least
  one such ancestor.

## What the thesis contribution therefore is

Not "adapted partitioning improves ranking fidelity" — that was tested at the premise level
and refused, pre-registered, before the arena ran.

The contribution is:

1. the construction method and its guarantees (a certified fixed point, a calibrated
   structural acceptance rule, two measured nulls for a separation threshold);
2. the transferable findings (`transferable-findings.md`);
3. a measured, pre-registered **negative result** about geometry-adapted evaluation
   partitioning, scoped by power and by roster;
4. the reframing itself: the value of a taxonomy for evaluation is a claim about judge
   generalisation surface, and it decomposes into three separately-testable links, of which
   this work measures one directly, one uncontrolled, and one at the premise level.

Pre-registering before the arena ran is what makes item 3 readable as a finding rather than
as a failure.
