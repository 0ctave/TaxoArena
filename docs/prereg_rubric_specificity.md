# Pre-registration: does cell coherence produce more specific rubrics?

Written **before** the null arms are induced. Registered because the same
discipline decided the discriminative analysis, where leading with the wrong
statistic would have given the opposite conclusion.

## The link being tested

The claim the architecture rests on is a chain:

```
coherent cells  ->  specific rubrics  ->  better judgments  ->  ranking closer to GT
   (labels: OK)      <-- THIS TEST -->      (needs C3)          (needs C3)
```

Splitting exists to **reduce the surface** over which a judge must generalise.
On a random query set only very general guidelines can be induced; on a coherent
cell, domain-specific ones should be.

This test licenses the **premise only**. "Rubrics are more specific" reads as
though it implies "judges are better". It does not. Links 3 and 4 require the
arena (C3: MAIN vs GENERIC_JUDGE).

## Arms

| arm | cells | role |
|---|---:|---|
| leaf-87 | 87 | treatment (already induced, frozen artifact 20260727_042523) |
| random-87 | 87 | null — random partition, **matched cell sizes** |
| domain-14 | 14 | intermediate: coarse but coherent |

Size matching matters mechanically: induction chunks at 25 items, so a random
cell of 88 queries yields the same batch count as a coherent cell of 88.

## The confound this must survive

Size is controlled; **topical breadth per batch is not**. A random 25-query
batch spans 14 domains, a coherent one spans one concept. If the model writes a
fixed number of high-level rules per batch regardless, the random arm's rules
are about MORE things — which could raise vocabulary diversity rather than
lower it. So "random scores worse" is not the prediction; the direction differs
per measure.

## Directional predictions, fixed in advance

| measure | if coherence works | if it is an LLM artifact |
|---|---|---|
| 1. pairwise Jaccard between rubrics | leaf **lower** (disjoint concepts) | similar, or leaf higher |
| 2. terms unique to one rubric | leaf **higher** | similar |
| 3. terms in >=90% of rubrics | leaf ~0, **random > 0** | both ~0 |
| 4. rubric vocab found in own cell's queries | leaf **higher** | similar |

**Measure 3 is the sharpest discriminator.** A random cell contains chemistry,
law and history at once, so its rubric must fall back on domain-general
language ("verify the computation", "check the claim against the passage"). If
that generic core is present across random rubrics and absent from leaf rubrics,
surface reduction is demonstrated. If both are ~0, the instrument cannot see the
difference and the test is inconclusive rather than negative.

**Measure 4 is immune to the breadth confound** — it involves no cross-rubric
comparison. A rubric induced from coherent content should reuse that content's
terminology; one induced from a mixture can only share generic terms.

## Treatment arm — measured (leaf-87, frozen artifact)

| measure | leaf-87 |
|---|---|
| rubric length | median 325 words, IQR [290, 382] |
| distinct content terms per rubric | median 165 |
| 1. pairwise Jaccard | median **0.073**, IQR [0.056, 0.099] |
| 2. terms unique to one rubric | **2275 (54% of vocabulary)** |
| 3. terms in >=90% of rubrics | **0** |
| 4. rubric vocab in own cell's queries | median **0.234**, IQR [0.186, 0.321] |

Lexical measures only (content terms = lowercase alphabetic, length >= 4, stopped).
No embeddings, no judge calls.

## Status

**Treatment arm only. No null. This is not yet evidence.** The numbers are
equally consistent with coherence producing specificity and with the model
writing varied prose about any 87 samples. Cost to complete: ~174 additional
inductions (87 random + 14 domain), no judge calls.

---

## AMENDMENT — measure 4 has a vocabulary-size confound; adding a within-arm null

Measure 4 is `|R_i ∩ Q_i| / |R_i|`. Under the random-partition null a cell spans
14 domains, so its query vocabulary is substantially BROADER than a coherent
cell's. A generic rubric term ("computation", "assumption") is then MORE likely
to appear somewhere in it. The random arm could therefore score HIGHER through
vocabulary size alone, and the confound would read as a refutation.

Same shape as two errors already made in this project: CV rising mechanically
from an additive mean shift, and disattenuation saturating past 1.0. The
statistic moves for a reason unrelated to the mechanism.

Mitigation: report `|Q_i|` alongside every overlap so the confound is visible.

### The within-arm null (free, no Azure)

For each rubric i, compare overlap against its OWN cell with overlap against
randomly chosen OTHER leaf cells j:

    specificity_i = |R_i ∩ Q_i|/|R_i|  −  mean_j |R_i ∩ Q_j|/|R_i|

Both are leaf cells, so vocabulary sizes are comparable and the confound
cancels. A generic rubric overlaps equally with both and scores ~0.

### Threshold, fixed BEFORE computing

| outcome | criterion | reading |
|---|---|---|
| **evidence** | median specificity >= 0.05 AND >= 75% of cells positive | rubrics captured cell-specific content |
| **inconclusive** | median in (0.02, 0.05) | weak; three-arm test still needed |
| **no signal** | median <= 0.02 | 0.234 is domain-general academic vocabulary present everywhere |

Decision rule fixed in advance: if **evidence**, the specificity result stands
without the 174 inductions and the three-arm test only establishes that
coherence is WHY — a much smaller inferential step. If **no signal**, the
three-arm test is unlikely to rescue it and the Azure spend is not warranted.

---

## ADDENDUM (2026-07-28) — results written back; artifact and band notes

Recorded after the fact and dated, closing the "treatment arm only, no null,
this is not yet evidence" status above.

**The null arm ran.** A random-cell arm of 13 size-matched cells (not the 87
originally specified above; see the arm-size note below) was induced by the
identical procedure and scored against the 87 leaf cells. Outcome:

- Treatment arm, within-arm specificity: median **0.138**, 81/87 (93%) of
  cells positive — inside the **evidence** band of this document
  (median >= 0.05 AND >= 75% of cells positive).
- Random arm, absolute own-cell specificity: median **0.012** — inside the
  <= 0.05 "coherence is the cause" band of `prereg_arena_launch.md`,
  Decision 3.
- Mann-Whitney U, one-sided, leaf vs. random: **p = 1.21e-6**, robust across
  all three per-cell statistic definitions considered
  (1.2e-6 / 2.1e-6 / 7.6e-6).
- All four directional predictions above fired in their predicted directions
  (thesis: `report/03_Content/6_Results.tex`, table `tab:rubric-null`).
- Arm-size control (13 vs. 87 is unbalanced): 13 leaf rubrics subsampled give
  0.134, a 200-draw bootstrap over subsamples gives 0.138 — the treatment
  value is not a function of arm size. The domain-14 intermediate arm was
  not run.

**Band disambiguation.** Two documents state decision bands without naming
the quantity each governs. Resolved: the band table in THIS document
(>= 0.05 with >= 75% positive / (0.02, 0.05) / <= 0.02) governs the
**treatment arm's within-arm specificity** (own-cell minus other-leaf-cell
overlap). The band in `prereg_arena_launch.md` Decision 3
(<= 0.05 causal / >= 0.10 refuted / between = partial) governs the **random
arm's absolute own-cell specificity**; that document's attribution of its
band to this one is an error in that document, recorded here rather than
silently repaired. Both bands were met (0.138 with 93% positive; 0.012).

**Untracked-artifact caveat.** The null-arm generation script
(`tools/analysis/rubric_specificity_null.py`) and its outputs
(`build/rubric_null/`) are untracked in version control as of this
addendum. The headline separation (p = 1.21e-6) was reproduced from those
stored artifacts on 2026-07-27. Until they are committed, this result is one
clean checkout from being unsupported; the caveat travels with the result
wherever it is cited.
