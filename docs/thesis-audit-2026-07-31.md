# Thesis audit, 2026-07-31

Audit of `report/02_Prematter/e_Abstract.tex`, `report/03_Content/*.tex` and
`report/04_Appendix/*.tex` against the settled 8-model RESOLVED batch
(snapshot `20260727_042523_Headless_Run_Auto_ge`), `docs/results-interpretation-2026-07-31.md`
and `docs/thesis-guidelines.md`.

No `.tex` file was edited. No build was run. Two code facts were re-verified
directly (`TaxonomyJudgeService.kt:203`, `ValidationService.kt:510-517`); one is
new and is finding **B7**.

**Where the interpretation doc and the thesis disagree, the interpretation doc
wins, and every such case is named as such below** — with the exception recorded
in the retraction immediately following, where the interpretation doc is the
thing that is wrong. One place the interpretation doc and the audit brief
disagree with *each other* is flagged in **C1** — settle it before quoting
either.

Line numbers are from the files as they stand on 2026-07-31 and were read, not
inferred. Editing the files will move them; work top-down within a file.

---

## RETRACTION — routing provenance

An early version of this audit carried two severity-A findings (**A8**, **A10**)
built on the claim that **only 37.2% of judged questions carry the subject of the
cell judging them** (609/1637), with per-domain figures of 11.7% for mathematics,
8.2% for computer science and 7.8% for philosophy. **That figure is wrong and is
withdrawn.** Both findings are deleted; nothing in this report depends on them.

The verified figure is **77.8% on-subject (1273/1637)**:

| domain | on-subject |
|---|---|
| law | 94.6% |
| mathematics | 80.4% |
| physics | 77.3% |
| computer science | 75.9% |
| philosophy | 75.2% |
| history | 70.2% |
| psychology | 69.4% |
| engineering | 68.4% |

Verified three ways: cell subject taken as the dominant `ground_truth_category`
of the cell's own construction queries from `embeddings_cache.db:queries`, joined
on the snapshot's native `q_<hash>` ids, all 87 leaves resolving with zero lookup
failures; judged-question category from `eval_results.category` restricted to the
8 roster models, within which no `question_id` maps to more than one category;
category strings case-normalised (`embeddings_cache` stores "Law", `eval_results`
stores lowercase — a naive comparison returns 0%) and `eval_question_id`
normalised to TEXT. Independently cross-checked against `mmlu_pro.category` by
exact question text, 549/549 agreeing on the mathematics run.

The earlier analysis's worked example does not survive inspection either. Cell
`n00000159`, *Extremal and Enumerative Combinatorics in Graphs and Numbers*,
received 52 judged questions: 40 mathematics, 7 computer science, 2 chemistry,
and one each of psychology, physics and engineering. The seven "computer science"
items are graph-theory combinatorics ("How many trees are there on 5 unlabeled
vertices?", "maximum number of edges in a simple triangle-free planar graph")
that MMLU-Pro files under computer science and that belong semantically exactly
where they landed. "The simplest alkene has" is genuinely present and is 1 of 52.

**Consequences.**

- **The routing is good and the cells are subject-coherent at judging time.** No
  passage in the thesis should be flagged for failing to disclose a
  subject-coherence problem, and the per-sub-domain framing is not under threat
  from this direction.
- **`docs/results-interpretation-2026-07-31.md` needs correcting.** Its §4.4, §4.6
  and limitation #1 of §5 are wrong on this point, and §4.4's behavioural null
  (on-subject minus off-subject: +0.48 pp on agreement, p = 0.84; −0.44 pp on tie
  rate, p = 0.81) was computed against the retracted classification at a 42%
  on-subject base rate. That regression must be recomputed under the corrected
  labels before any of its four rows is quoted. Its other findings — the distance
  ladder of §4.2, the tie-rate decomposition of §3, and the null on
  distance-versus-behaviour in §4.3 — are unaffected and still stand, and **B10**
  below rests on §4.2 rather than on §4.4.
- One caveat is supportable and is worth a single line rather than a section:
  see **C8**.

---

## Summary

Severity A = an examiner reading only this sentence would take away something the
data contradicts. B = internally inconsistent or unsupported, but unlikely to
flip a conclusion on its own. C = presentation, guideline compliance, cosmetics.

| # | file:line | cat | in one line |
|---|---|---|---|
| **A1** | `e_Abstract.tex:72-88` | INVALID | Whole screen-and-advantage paragraph is the superseded 12-model batch read against a withdrawn threshold. |
| **A2** | `e_Abstract.tex:68-71` | INVALID | "A paired arm that removes the partition entirely" — no arm removes the partition; the numbers are superseded. |
| **A3** | `e_Abstract.tex:90-96` | INVALID | Reports the mathematics registered prediction as *failed*; Appendix A:333-336 says it is *open*. |
| **A4** | `6_Discussion_and_Conclusion.tex:445-455` | INVALID + PRESENTATION | A sentence starts inside a `%` comment and finishes outside it. The Conclusion currently prints a fragment beginning `` ``cell-scoped rubrics judge better'' `` and asserts "the partition pays". |
| **A5** | `6_Discussion_and_Conclusion.tex:85-86` | INVALID | "the eight paired runs, whose arms differ in the partition rather than only in the rubric, do separate in five domains" — wrong on both halves. |
| **A6** | `6_Discussion_and_Conclusion.tex:64-76` | INVALID | "the rank-correlation advantage the per-leaf arm shows in the flagged domains" — no such advantage survives. |
| **A7** | `5_Results.tex:12-14` | INVALID | Chapter 5 opens by promising "per-leaf judging still buys a small, consistent gain in rank fidelity". |
| ~~**A8**~~ | — | **RETRACTED** | Built on the withdrawn 37.2% provenance figure. See the retraction block above. No action. |
| **A9** | six `TODO(author)` stubs | OUTDATED | Every RQ2 stub instructs "report per-verdict answer-key agreement" — that unconditional statistic is the one the correction retired. |
| ~~**A10**~~ | — | **RETRACTED** | Same. Routing is subject-coherent (77.8%); there is no undisclosed provenance problem. See **C8** for the one line that is supportable. |
| **A11** | absent from the thesis | UNGROUNDED | 196/200 is one ordering recovered eight times (identical GT ordering in 7/8 domains). Nothing says so. |
| **A12** | `B_Judge_Generation.tex:9-17` | INVALID | `k = 25` described as a representative-pack sample size. It is a **batch** size; the whole filtered pool is used. |
| **A13** | `1_Introduction.tex:151-160`; `3_Method.tex:602-607`; `4_Experimental_Design.tex:170-176`, `tab:info-separation` row 1 | INVALID | The construction/reserved separation is enforced on **rubric induction only**, not on the partition. Row 1 of the table asserts the stronger claim. |
| **A14** | `1_Introduction.tex:166-170`; `4_Experimental_Design.tex:230-236`; `5_Results.tex:216-217`; `3_Method.tex:651-660`; `6_Discussion_and_Conclusion.tex:6-8` | INVALID | Three chapters say the judge is *not* shown the options block; two say it *is*. Both are right — for different option modes — and none says which. |
| **A15** | `4_Experimental_Design.tex:58-66, 187-193`; `3_Method.tex:487-496, 698`; `5_Results.tex:36-39` | OUTDATED | The design chapter still specifies the run as 12 models / 66 pairs. The settled batch is 8 models / 28 pairs. |
| **A16** | 16 sites pointing at `\ref{sec:res-c5}` | OUTDATED | `sec:res-c5` is now two sentences and a TODO. Sixteen cross-references route the reader to content that was deleted, including `5_Results.tex:1372` pointing at a footnote that no longer exists. |
| **B1** | `5_Results.tex:64-68, 119-139` | OUTDATED | "seven completed paired domains and an eighth still running"; "two runs are outstanding". Batch is complete. |
| **B2** | `5_Results.tex:141-162` vs `B_Judge_Generation.tex:109-116` | OUTDATED | Two different sets of arm-pairing overlaps in two files, neither saying which roster it belongs to. |
| **B3** | `5_Results.tex:542-562`; `6_Discussion_and_Conclusion.tex:317-319` | UNCLEAR | "leaf-level judging is affordable" conflates *identification* (7/28 pairs) with *resolution* (1.6–5.0 against ~143). |
| **B4** | `3_Method.tex:962-964` vs `ValidationService.kt:510-517` | INVALID | The method misstates its own cell-exclusion rule, and that rule is answer-key-dependent. No rank-recovery number carries the caveat. |
| **B5** | `1_Introduction.tex:166` and `4_Experimental_Design.tex:233` (95.1%) vs `3_Method.tex:654`, `5_Results.tex:216`, `6_Discussion_and_Conclusion.tex:7` (94.8%) | INVALID | Same quantity, two values, three chapters apart. |
| **B6** | `5_Results.tex:923-936` "run pool" column | OUTDATED | Physics 237, engineering 202, cs 159, law 277, philosophy 130 are superseded-run counts. Batch: 229, 158, 158, 276, 129. |
| **B7** | `5_Results.tex:1478-1486`; `e_Abstract.tex:59-64`; `6_Discussion_and_Conclusion.tex:365-381` | OUTDATED | 88.8% is a Run-A pilot figure, half its support format-decided, quoted as the thesis headline in Abstract, Conclusion and chapter summary. |
| **B8** | `A_Tuning_Protocol.tex:152-155` | OUTDATED | The Outcome-column TODO names the retired statistic. |
| **B9** | `6_Discussion_and_Conclusion.tex:244` (bib `Bibliography.bib:238`) | INVALID | `chen2024verbosity` cited for verbosity bias. Confirmed misattribution; the thesis's own §2.x uses the right sources. |
| **B10** | `5_Results.tex:671-696` (R1 rows of `tab:requirements-evidence`) | UNCLEAR | R1 coherence is evidenced entirely on the construction pool. Routed questions sit 0.16 cosine farther out. |
| **B11** | `5_Results.tex:1375-1382`; `4_Experimental_Design.tex:42-56` | OUTDATED | "all four flagged domains were run" and the screen record are read against the superseded batch. |
| **B12** | limitations spread across ≥5 sites | PRESENTATION | Guidelines §5 asks for one section, four items. Items 6 and 7 of the interpretation doc (§5) are missing entirely. |
| **C1** | — | — | Interpretation doc §3.1 (86.1/87.4, n=35, p=0.017) vs audit brief (86.0/87.2, n=37, p=0.020). Settle before quoting. |
| **C2** | `1_Introduction.tex:185`; `6_Discussion_and_Conclusion.tex:474-475` | PRESENTATION | "each separately falsifiable" — explicitly banned by guidelines §6. |
| **C3** | `1_Introduction.tex:202-217` | PRESENTATION | The introduction explains at length that an RQ was rewritten after seeing data. Guidelines §6 says methods, one sentence. |
| **C4** | `5_Results.tex:27-31`; rule D5 `3_Method.tex:1181-1190` | PRESENTATION | Both tie conventions mandated everywhere; guidelines §4 asks for one in the main text. |
| **C5** | `5_Results.tex:44-49`; `4_Experimental_Design.tex:543-571`; `1_Introduction.tex:383-397` | PRESENTATION | Grid-step machinery survives in three places; guidelines §4 says delete it. |
| **C6** | `e_Abstract.tex:63-65`; `6_Discussion_and_Conclusion.tex:374-377` | PRESENTATION | "97.0% against 83.2%" quoted flat; Results:389-390 says the 97.0% cell (n=33) is the table's thinnest. |
| **C7** | `C_Metric_Definitions.tex:9-16`; `A_Tuning_Protocol.tex:210-213`; `B_Judge_Generation.tex:104-107` | — | Three TODOs verified as **still correct**. No action beyond executing them. |
| **C8** | `5_Results.tex:961-987` | PRESENTATION | One supportable line on routing provenance: 77.8% on-subject, and part of the 22.2% residual is MMLU-Pro's label taxonomy rather than misrouting. |

---

# A — would mislead an examiner

## A1. The Abstract's third paragraph is the superseded batch

`report/02_Prematter/e_Abstract.tex:72-88`

> "Eight domains were then run under a paired protocol, seven of them complete.
> All four flagged domains show an advantage for cell-scoped judging that never
> reverses sign under either tie convention. Engineering, which the screen
> clears, returns the registered null. Philosophy, which the screen did *not*
> flag at $p = 0.053$, produced the largest advantage measured."

**INVALID.** Every clause after the first is a 12-model result read against
`|Δρ| ≥ 0.007`, a threshold withdrawn in `A_Tuning_Protocol.tex:318-329` because
two identical-configuration runs differing only in scheduler seed moved Δρ by six
and zero grid steps. On the 8-model roster both arms produce the *identical*
ranking, so there is no per-domain Δρ contrast left to have a sign
(`5_Results.tex:526-528` already records this). "Advantage for cell-scoped
judging" is also the wrong shape of claim under the RQ2 correction: the rubric
arm is not more accurate, it abstains more.

The last sentence of the paragraph — the screen/between-leaf correlation of
`+0.072`, and the law reliability ceiling `0.895–0.993` against `0.873–0.970` —
is ground-truth-only and survives. Keep it; cut the rest.

**Replacement:**

> Eight domains were run under one configuration with no per-domain tuning.
> Where the answer key determines an ordering, the arena recovers it: 196 of 200
> key-decidable model pairs, 98.0%, with zero crashes and zero rate-limit
> failures. The eight domains are eight disjoint question samples of one
> ordering rather than eight independent orderings — the key ranks the roster
> identically in seven of the eight, and only law differs, by one adjacent swap.
> Removing every domain criterion from the judge prompt costs nothing
> measurable: agreement with the key conditional on the judge committing is
> TODO(author: settle C1) for the induced rubric against TODO for a generic
> MT-Bench prompt. What the rubric changes is decisiveness — its tie rate on
> key-decidable comparisons is 13.0% against 10.9%, the same direction in eight
> domains of eight — and the design cannot attribute that to the rubric rather
> than to the two arms' different output formats.

## A2. "A paired arm that removes the partition entirely"

`report/02_Prematter/e_Abstract.tex:68-71`

> "A paired arm that removes the partition entirely matches the key to within
> half a percentage point on mathematics ($94.2\%$ against $94.7\%$); across the
> seven completed domains that difference runs from $-1.3$ to $+4.0$ points and
> favours the per-leaf arm in five of them."

**INVALID three ways.**

1. No arm removes the partition. `A_Tuning_Protocol.tex:300-316` establishes
   this with a measurement: C5 replays MAIN's exact (cell, pair, question)
   triples under MAIN's cells, and pooling per-cell sufficient statistics is
   arithmetically identical to a direct domain fit, maximum |θ| difference
   0.000. `4_Experimental_Design.tex:389-397` and `3_Method.tex:497-507` both say
   so already. The Abstract contradicts two of the thesis's own chapters.
2. 94.2 / 94.7 are superseded 12-model numbers.
3. "favours the per-leaf arm in five of them" is the retired unconditional
   statistic, and it favours the *generic* arm in 8/8 on the settled batch
   (74.9% against 77.9% pooled) — which is itself not an accuracy result.

**Replacement:** delete. The correct statement is folded into A1's replacement.

## A3. The Abstract reports a registered prediction as failed; Appendix A says it is open

`report/02_Prematter/e_Abstract.tex:90-96`

> "One registered prediction failed. Mathematics was designated in advance as the
> domain where nothing should be found, and under the registered rule its
> rank-correlation contrast returned a verdict for the partition-free arm."

**INVALID, and internally contradicted.** `A_Tuning_Protocol.tex:333-336`:

> "The registered prediction for mathematics stands as recorded; whether it holds
> is open rather than answered, because the run that answered it is superseded."

Two chapters of the same document say opposite things about the same
registration. The Abstract also uses "partition-free arm", which A2 disposes of,
and reads the verdict off `|Δρ|`, which is withdrawn.

**Replacement:**

> Mathematics was designated in advance as the domain where nothing should be
> found. The run that appeared to refute that prediction covered 20 of 66 model
> pairs and predates two scheduler repairs; it is superseded, and whether the
> prediction holds is open.

## A4. The Conclusion prints a broken sentence, and the surviving half is invalid

`report/03_Content/6_Discussion_and_Conclusion.tex:445-455`

Lines 446-451 are a `% TODO(author)` block. Line 451 is:

```
% prediction holds is now an open question, not a reported failure. What the completed domains support is narrower than
```

The sentence "What the completed domains support is narrower than…" begins
**inside** the comment and its continuation on line 452 is **not** commented. The
compiled Conclusion therefore reads:

> Mathematics was registered in advance as a null arm. ``cell-scoped rubrics
> judge better'' and more useful than a single-domain result: the partition pays,
> by a small margin, in the domains where a cheap offline statistic says the
> models reorder, and that statistic costs no judge calls.

**PRESENTATION** (a dangling fragment opening with a stray quotation mark, in the
Conclusion) **and INVALID** (the surviving clause asserts "the partition pays…in
the domains where a cheap offline statistic says the models reorder" — the
withdrawn 12-model screen result, and a partition claim no arm tests).

**Fix:** delete lines 452-455 with the comment block. The paragraph ends at line
445 plus A3's replacement sentence.

This is the single highest-value edit in the audit: it is currently visible in
the printed Conclusion.

## A5. "the arms differ in the partition … do separate in five domains"

`report/03_Content/6_Discussion_and_Conclusion.tex:85-86`

> "How close two arms are is itself a measurement and does not generalise: the
> eight paired runs, whose arms differ in the partition rather than only in the
> rubric, do separate in five domains."

**INVALID on both halves.** The arms do *not* differ in the partition (A2). They
do not "separate in five domains": on the settled batch both arms produce the
identical ranking in every domain, and the item-level contrast is not an accuracy
contrast. This sentence also contradicts `3_Method.tex:502-507` on the same page
of argument.

**Replacement:**

> How close two arms are is itself a measurement and does not generalise: on
> Run A's mathematics cells the two prompts flip 10 winners in 1,736, while on
> the settled batch the same two prompts differ on the tie rate in every domain —
> 13.0% against 10.9%, the same direction eight times out of eight.

## A6. "the rank-correlation advantage the per-leaf arm shows in the flagged domains"

`report/03_Content/6_Discussion_and_Conclusion.tex:64-76`

> "Because cell identity adds almost nothing to model ordering, the
> rank-correlation advantage the per-leaf arm shows in the flagged domains cannot
> be evidence that cell-scoped judging *discovers* capability the domain-level
> arm misses. … What the advantage supports is that a cell-scoped rubric
> estimates a largely shared ordering with less error. That is a smaller claim
> than the architecture was designed to make, and it is the claim the results
> jointly license."

**INVALID.** The paragraph bounds an advantage that no longer exists. Δρ is not a
decision rule (grid step 0.0119 at M=8; a scheduler-seed replicate moved it six
steps), and there is no per-domain Δρ contrast on the 8-model roster. The final
sentence — "the claim the results jointly license" — licenses the wrong claim.

The law reliability-ceiling measurement inside it (`0.895`–`0.993` against
`0.873`–`0.970`) is ground-truth-only and survives; keep it, re-attach it to the
right claim.

**Replacement:**

> Because cell identity adds almost nothing to model ordering, nothing in these
> runs could have shown cell-scoped judging *discovering* capability a
> domain-level fit misses: there is little such capability on this corpus to
> discover. Inside law, each leaf's ground-truth ranking agrees with the domain
> ranking at Spearman 0.895 to 0.993, against 0.873 to 0.970 for ground truth
> against itself. A per-cell ranking on this corpus is a noisier estimate of one
> shared ordering, not a different ordering.

## A7. Chapter 5 opens by promising a result it no longer reports

`report/03_Content/5_Results.tex:11-17`

> "The judge bypasses the partition on this corpus by verifying answers against a
> key it was never shown. And per-leaf judging still buys a small, consistent
> gain in rank fidelity in the domains the screen flags. A reader who learns in
> Section 5.2 what the judge conditions on already knows why the gain is small…"

**INVALID.** Sentence two is the withdrawn 12-model Δρ result, and the chapter no
longer contains it (`sec:res-c5` is a stub). The chapter promises a finding it
then does not deliver — the worst possible arrangement for a reader.

**Replacement:**

> The judge bypasses the partition on this corpus by verifying answers against a
> key it was never shown. The partition still does what it was built to do —
> the cells are separated, the rubrics are specific to them — and none of that
> reaches the verdict. A reader who learns in Section 5.2 what the judge
> conditions on already knows why.

## A8. RETRACTED

Withdrawn in full. It asserted that `tab:anchor-cells`'s label-agreement column
misrepresented what the runs judged, on the basis of a 37.2% on-subject figure
that is wrong. The verified figure is 77.8% pooled, and the two quantities line
up rather than conflicting: law 94.6% label agreement against 94.6% on-subject,
mathematics 81.4% against 80.4%. `5_Results.tex:968-977` — "Law is nearly pure at
94.6% and mathematics is high at 81.4%, so their runs are close to what their
names suggest" — **is correct as written and needs no change.**

One note so the two numbers are not merged later: the label-agreement column
measures the share of an *anchor's* held-out pool carrying that anchor's MMLU-Pro
label, and the on-subject share measures whether a judged question carries its
own *cell's* dominant construction category. They are different quantities and
can diverge without either being wrong — computer science sits at 49.7% on the
first and 75.9% on the second, because cells under the computer-science anchor
are dominantly built from adjacent quantitative categories. The thesis's
treatment of computer science as the extreme case
(`5_Results.tex:973-977`) is a statement about the first quantity and stands.

See **C8** for the one line worth adding.

## A9. Six TODO stubs instruct the author to report the retired statistic

The RQ2 rewrite instructions all name "per-verdict answer-key agreement" as the
replacement primary outcome:

- `5_Results.tex:524-528` — "Report per-verdict answer-key agreement as the primary outcome"
- `5_Results.tex:536-539` — "primary: per-verdict answer-key agreement per arm, per domain"
- `5_Results.tex:1493-1494` — "Report per-verdict answer-key agreement instead."
- `6_Discussion_and_Conclusion.tex:428` — "Report per-verdict answer-key agreement as the primary outcome."
- `4_Experimental_Design.tex:478-489` — instructs the outcome be restated from the 8-model batch
- `A_Tuning_Protocol.tex:152-155` — "Report per-verdict answer-key agreement on decidable comparisons, NOT Delta rho"

**OUTDATED.** Unconditional agreement on key-decidable comparisons is exactly the
quantity the correction retired: it blends decisiveness and accuracy. The
per-domain figures in the verified batch table (79.3 / 80.2 / 66.9 / 74.0 / 76.4
/ 77.0 / 70.2 / 74.1, against C5's 82.7 / 83.4 / 69.7 / 76.5 / 78.6 / 76.5 /
74.1 / 78.9) are that statistic. Following these instructions literally
reproduces the "the generic prompt beats the rubric" reading the correction
killed — 88% of the unconditional discordance involves at least one arm tying.

**Replacement instruction, to be pasted into all six:**

```
% TODO(author): RQ2 from the 8-model RESOLVED batch. Report THREE things and do
% not collapse them:
%   (1) tie rate on key-decidable comparisons, MAIN vs C5: 13.0% vs 10.9%,
%       MAIN higher in 8/8 domains. This is the robust effect.
%   (2) agreement CONDITIONAL ON THE JUDGE COMMITTING (see docs/thesis-audit
%       item C1 for which pair of numbers to use), plus the both-committed sign
%       test, which is significant in NO individual domain.
%   (3) the unconditional agreement rate ONLY as an appendix line, labelled as
%       blending decisiveness with accuracy. It is not an accuracy measure.
% Do NOT write that the rubric arm "underperforms" or "is less accurate". It
% abstains more. See docs/results-interpretation-2026-07-31.md §3.
```

Also affected: `FIGURE_PLAN.md` F2, whose stated claim ("the generic MT-Bench
prompt beats the domain rubric 97 to 51") is the retired statistic. The
interpretation doc replaces it with V3.

## A10. RETRACTED

Withdrawn in full. It claimed routing provenance was an undisclosed threat to the
per-sub-domain framing and proposed a limitations entry and a figure (V1) for it.
The premise was the withdrawn 37.2% figure. **The routing is subject-coherent —
77.8% pooled, 68.4% to 94.6% by domain — so there is nothing to disclose and no
limitation to add.**

Two things do carry over from that section, in much reduced form:

- The single supportable line, **C8**.
- The boundary statement from interpretation doc §4.6, which does *not* depend on
  provenance and which the Discussion should carry regardless, at
  `6_Discussion_and_Conclusion.tex:21-35`:

  > All of this holds where the judge can verify the answer. It says nothing
  > about a corpus where it cannot, and there the rubric is the only signal and
  > its coverage is the whole game.

The proposed on-subject-versus-off-subject RQ1 measurement is **not** usable as
written: interpretation doc §4.4's four regression rows were fitted against the
retracted classification and have to be recomputed under the corrected labels
before any of them is quoted. Under an on-subject base rate of 77.8% rather than
42% the off-subject cell is roughly a fifth the size assumed, so the test is
weaker than §4.4 reports as well as differently constituted.

## A11. 196/200 is one ordering recovered eight times

**UNGROUNDED / absent.** The ground-truth ordering is identical in seven of eight
domains; only law differs, by swapping `Meta-Llama-3_1-8B` (0.207) and
`Yi-6b-Chat` (0.217). The roster was cut to eight models for a large global
accuracy spread (`D_Model_Rosters.tex:38-45`), and that spread survives any
subsample of the corpus — which is *why* the orderings coincide, and the reason
is roster construction alone. Presenting eight domains as eight confirmations
overstates by roughly a factor of eight.

Sites that will carry the figure once written:

- `5_Results.tex:1478-1486`, RQ1 row of `tab:res-summary`. Currently: "Rank
  recovery is within about one adjacent transposition" — a superseded, imprecise
  statement of a number the batch now pins exactly.
- `6_Discussion_and_Conclusion.tex:407-412`.
- `e_Abstract.tex` (A1 replacement already includes it).
- `FIGURE_PLAN.md` F4 `rank_recovery_grid`: the interpretation doc's note applies
  — the grid is mostly white *because* the key ordering barely varies, and the
  caption must say so or the figure argues for more than it shows.

**Wording:**

> The arena recovers 196 of 200 key-decidable model pairs, 98.0%, across eight
> domains under one configuration. The eight are one replication rather than
> eight: the answer key ranks the roster identically in seven of the eight
> domains, and law differs by one adjacent swap. The question samples are
> disjoint and the verdicts independent, so this is a real replication — of one
> result, eight times.

## A12. `k = 25` is a batch size, not a sample size

`report/04_Appendix/B_Judge_Generation.tex:9-17`

> "Representative-query packs are drawn from each leaf's construction pool at
> pack size $k = 25$; a leaf with fewer than 25 construction queries uses its
> full pool as a single pack. … A leaf's rubric is therefore induced from a
> sample of its construction queries rather than from all of them."

**INVALID.** Verified in source. `TaxonomyJudgeService.generateJudgeForNode`
(`src/main/kotlin/taxonomy/service/TaxonomyJudgeService.kt:203`):

```kotlin
val chunks = details.chunked(25)
```

`details` is the leaf's *entire* filtered pool (region queries, minus the
`abs(hashCode) % 5 == 0` thinner at line 158, minus every reserved text at line
163). Every chunk is inducted (line 212, `chunks.mapIndexed`) and the partials
are synthesised. Nothing is sampled. Across the 52 cells the arena used the
induction pool runs 24 to 182 queries, median 44, and exactly one cell has a pool
under 25.

Two consequences beyond the sentence itself:

- The trailing "induced from a sample … rather than from all of them" is true
  only because of the hash filter, not because of `k`. `3_Method.tex:609-628`
  states the hash filter correctly and independently; the two passages currently
  double-count one mechanism as two.
- The pre-registered check "are leaves with fewer than 25 construction queries
  worse?" has n = 1 and cannot be run. It should be struck, not reported as a
  null.

**Replacement for `B_Judge_Generation.tex:9-17`:**

> Each leaf's rubric is induced from its whole filtered construction pool. The
> pool is chunked into batches of 25, one map call per batch, and a reduce call
> synthesises the per-batch guideline lists into a single rubric; $k = 25$ is
> therefore a batching parameter and not a sample size. The pool is the leaf's
> construction queries after two filters: the reserved-set filter, audited by a
> build-failing assertion, and a hash filter that thins the pool by roughly a
> fifth. Across the 52 cells the settled batch used, the resulting pools run 24
> to 182 queries with a median of 44, and one cell has a pool below the batch
> size. A leaf's rubric is therefore induced from about four in five of its
> construction queries — the hash filter is the only thinning — rather than from
> a fixed-size representative pack.

## A13. The reserved separation is enforced on the rubric, not on the partition

The claim appears in three chapters, and in two of them it is stated too broadly.

`report/03_Content/1_Introduction.tex:151-160`:

> "The judge-generation phase uses correct MMLU-Pro answers from the construction
> query set to induce the rubrics, so the system is *reference-informed* at
> construction time. … A hold-out filter enforces the separation in code, and a
> build-time assertion checks the filter against the membership test itself."

`report/03_Content/3_Method.tex:602-607`:

> "**Held-out queries never enter rubric generation, and this is audited rather
> than asserted.** … This is the strongest information-separation guarantee in
> the system."

Both are **correct as written** and should be kept. The problem is the table.

`report/03_Content/4_Experimental_Design.tex`, `tab:info-separation` at 201-220,
row 1:

| Phase | Q_con text | Q_con labels/answers | Q_eval text | Q_eval labels/answers |
|---|---|---|---|---|
| Taxonomy construction | ✓ | ✓ | — | — |

**INVALID.** The reserved filter lives in judge induction only —
`grep getReservedQuestionTexts` over `src/main/kotlin` returns exactly one
consumer, `TaxonomyJudgeService.kt:161`. Nothing in the construction path filters
reserved material. The frozen tree's leaf regions contain it: of 9,141
leaf-region queries, 17.0% carry a text flagged reserved-only in `eval_results`
and a further 23.6% carry a text flagged both ways. The construction sees
`Q_eval` *text* (it is the same corpus), and the dash in column 3 of row 1
asserts otherwise.

**Fix.** Change row 1 column 3 to ✓ with a footnote, and add to
`4_Experimental_Design.tex:170-176`:

> The separation the build-failing assertion enforces is on *rubric induction*,
> not on the partition. The construction runs over the whole embedded corpus and
> its leaf regions contain reserved-split material — 17.0% of leaf-region queries
> carry a text flagged reserved-only and 23.6% carry a text flagged both ways.
> What is guaranteed is that no question the arena judges was used to write the
> rubric that judged it, and that is what "answer-key-blind" means here.

**And state the verification, which is stronger than the assertion.**
`3_Method.tex:602-607` should gain one sentence:

> The guarantee was checked against the runs rather than only against the build:
> of the 1,569 distinct question texts the settled batch judged, zero appear in
> any leaf's induction pool.

This is a *strengthening*, and the thesis should take it. The filter is a
text-membership test, so it removes any text reserved under any identifier, which
makes it conservative rather than leaky (interpretation doc §0.3).

## A14. Whether the judge sees the options block: three chapters disagree

| site | says |
|---|---|
| `1_Introduction.tex:166-170` | "It carries neither the reference answer nor the multiple-choice options block." |
| `4_Experimental_Design.tex:230-236` | "The judge receives neither the answer key nor the multiple-choice options" |
| `3_Method.tex:651-660` | "The question is rendered with its multiple-choice options attached" |
| `5_Results.tex:216-217` | "the judge is answer-key-blind but not answer-blind: it sees the multiple-choice options" |
| `6_Discussion_and_Conclusion.tex:6-8` | "The judge is shown the options" |

**INVALID as a set.** Both readings are true, of different runs, and no site says
which. Verified in `TaxonomyArenaService.kt:675-681`: the options block is
appended only when `judgeOptionMode == "OPTIONS"`. Run A and every 12-model
paired run used OPTIONS. **The settled batch runs RESOLVED**, which withholds the
block and instead attaches each model's own selected option to its trace
(`B_Judge_Generation.tex:131-140`, injection 93.2–99.8%).

The existing `% TODO(author)` at `3_Method.tex:661-665` diagnoses this as
"1_Introduction and 4_Experimental_Design are wrong". **That instruction is now
itself wrong** — those two files are right about the settled batch and wrong
about Run A, and `3_Method.tex:652-653` is the reverse.

**Fix.** Make every one of the five sites option-mode-conditional. Model
sentence, for `3_Method.tex:651-660`:

> The judge is *not* answer-blind, and the channel differs by option mode. Under
> `OPTIONS`, used by the pilot and by every superseded paired run, the question
> is rendered with its multiple-choice options attached, so a judge capable of
> solving the item can solve it. Under `RESOLVED`, the settled batch's mode, the
> options block is withheld and each model's own selected option is attached to
> its trace instead. Under either mode the responses state their own answers, so
> the judge can compare two declared answers without being told the key. The mode
> narrows the channel; it does not close it.

Also fix the rate while you are there — see **B5**.

## A15. The design chapter still specifies a 12-model / 66-pair run

- `4_Experimental_Design.tex:58-66` — "**Run conditions, identical across every
  paired run but one.** Twelve-model roster; … every one of the $\binom{12}{2} =
  66$ model pairs at least two comparisons … The decisive difference was
  registered as $|\Delta\rho| \geq 0.007$, two steps of the Spearman grid at
  twelve models."
- `4_Experimental_Design.tex:187-193` — "The binding constraint is the number of
  model pairs per leaf, $\binom{12}{2} = 66$ at the twelve-model roster **every
  paired run uses**".
- `3_Method.tex:487-496` — "**Every paired run reported in this thesis** uses a
  different and larger roster --- twelve models".
- `3_Method.tex:698` — "at twelve models and eleven cells there are 726 distinct
  (cell, pair) slots".
- `5_Results.tex:36-39` — "the most-scheduled model appears in $43.2\%$ to
  $67.9\%$ of that run's comparisons, against the $16.7\%$ a uniform scheduler
  would give at twelve models."

**OUTDATED.** The settled batch is 8 models, 28 pairs, 52 cells. At 8 models a
uniform scheduler gives 25%, not 16.7%; the bootstrap floor covers 28 pairs;
28 pairs × 11 math cells is 308 slots, not 726. `D_Model_Rosters.tex:9-45`
already documents the settled roster correctly, so Appendix D and Chapter 4
contradict each other on which roster "every paired run" used.

**Fix.** Chapter 4 must be restated for the settled batch, with the 12-model
material moved into a clearly-labelled "superseded runs" paragraph that says
which chapter still cites it. Concretely, `4_Experimental_Design.tex:58-66`
becomes:

> **Run conditions, identical across all eight domains of the settled batch.**
> Eight-model roster (Appendix D, Table D.1); RESOLVED option mode; both arms on
> an identical held-out question set, verified by exact set equality, with the
> generic arm replaying the cell-scoped arm's exact (cell, pair, question)
> triples; a mandatory bootstrap phase giving every one of the $\binom{8}{2} =
> 28$ model pairs at least two comparisons before any adaptive scheduling; the
> confidence gate disabled in both arms; an isolated ranking database per run;
> seed 42. The registered decisive difference of $|\Delta\rho| \geq 0.007$ is
> withdrawn — two runs of an identical configuration differing only in a
> scheduler seed produced $\Delta\rho$ of six and zero grid steps, so a rule at
> two steps sits below the noise (Appendix A, §A.5). $\rho$ is reported for
> continuity and is not used as a decision rule.

Note that this also resolves the `% TODO(author)` at `4_Experimental_Design.tex:67-72`.

## A16. Sixteen cross-references point into a deleted section

`sec:res-c5` (`5_Results.tex:498`) is now: a commented-out removal note, two
sentences of setup, and a `TODO`. Sixteen sites send the reader there for a
result:

`1_Introduction.tex:296` (in a comment), `:397` ·
`3_Method.tex:986`, `:1073` ·
`4_Experimental_Design.tex:83`, `:577` ·
`5_Results.tex:98`, `:117`, `:127`, `:162`, `:1372`, `:1497` ·
`6_Discussion_and_Conclusion.tex:41`, `:76`, `:232`, `:530` ·
`B_Judge_Generation.tex:116` · `D_Model_Rosters.tex:112` · `F_Numerics.tex:121`

**OUTDATED.** LaTeX will not warn — the label resolves — so this will survive a
clean build. Two are specifically broken:

- `5_Results.tex:1372`: "the two arms disagree on several domains, engineering
  among them (**see the footnote in Section 5.2.6**)". That footnote was deleted
  with the section.
- `5_Results.tex:1375-1377`: "the record is stated once in Section 5.2.6 rather
  than restated here: all four flagged domains were run." Section 5.2.6 states
  no record.

**Fix.** After `sec:res-c5` is rewritten from the settled batch, walk this list
and check each pointer resolves to content that exists. Four of them
(`1_Introduction.tex:397`, `4_Experimental_Design.tex:83`, `F_Numerics.tex:121`,
`D_Model_Rosters.tex:112`) point specifically at the mathematics 20-of-66
coverage confound, which the rewritten section may not carry at all; those should
be repointed at `A_Tuning_Protocol.tex` §A.4 or given the fact inline.

---

# B — internally inconsistent or unsupported

## B1. The run inventory is stale

`report/03_Content/5_Results.tex:64-68`:

> "Eight completed arena runs and seven offline analyses produced the results in
> this chapter: the pilot, seven completed paired domains, and an eighth paired
> domain still running."

`report/03_Content/5_Results.tex:130-136`:

> "**Two runs are outstanding and no result is anticipated for either.** Computer
> science was registered as a third null arm in a dated addendum and was still
> running when this chapter was fixed. And mathematics is being re-run…"

Same claim at `4_Experimental_Design.tex:42-56` ("Eight domains were run and
seven are reported with results"; "computer science was still running"),
`4_Experimental_Design.tex:507`, `6_Discussion_and_Conclusion.tex:190` and `:460`
("eight of the corpus's fourteen domains, seven of them complete"), and
`e_Abstract.tex:76`.

**OUTDATED.** All eight domains completed, including computer science
(158 routed questions, 6 cells, 526 verdicts, 25/28 decidable, 25/25 recovered).
The `PLACEHOLDER(author)` at `5_Results.tex:137-139` is discharged by the batch.

**Replacement for 5_Results.tex:64-68:**

> One arena batch and seven offline analyses produced the results in this
> chapter. The batch is eight domains under one configuration — mathematics,
> physics, law, engineering, psychology, philosophy, history and computer
> science — each run in two arms against the same frozen snapshot, at seed 42,
> in RESOLVED option mode, on the eight-model roster of Appendix D. Two earlier
> runs are cited for material the batch does not supersede and are named by run
> letter: Run A, the pilot, and Run B, the twelve-model mathematics pair.

## B2. Two sets of arm-pairing overlaps, in two files, neither labelled

`5_Results.tex:141-155`:

> "the pairing runs above $99\%$ on mathematics, law, history and psychology, and
> falls to $89.9\%$ on philosophy and $83.3\%$ on engineering, where the arms
> also differ in total comparisons (1,319 against 1,188, and 792 against 660).
> Philosophy carries the largest $\Delta\rho$ in the set and engineering is a
> registered null…"

`B_Judge_Generation.tex:109-116`:

> "In the settled batch the two arms see the same comparison set by construction…
> Measured overlap is $100\%$ on mathematics, physics, psychology and philosophy,
> and $99.6\%$ on law and engineering…"

**OUTDATED / UNCLEAR.** These describe different roster generations of the same
quantity, in opposite directions, and only one says which batch it belongs to.
`6_Discussion_and_Conclusion.tex:527-531` repeats the *superseded* figures as
current, and cites `sec:res-c5` for them (see A16).

Additionally, "Philosophy carries the largest $\Delta\rho$ in the set" is a
superseded-batch fact stated as present-tense fact, and Δρ is not a decision
quantity.

**Fix.** Delete `5_Results.tex:141-162` and replace with the settled batch's
pairing, sourced from Appendix B; note that computer science and history are not
covered by the Appendix B measurement and either measure them or say so.
Then correct `6_Discussion_and_Conclusion.tex:524-536` — the "pairing at the
comparison rather than the question" future-work item is largely *already done*
in the settled batch (the generic arm is a replay), so the item should shrink to
the residual.

## B3. "Leaf-level judging is affordable" conflates identification with resolution

`report/03_Content/5_Results.tex:542-562`:

> "On Run~A, per-cell identification (a connected comparison graph over the
> roster) is reached at **7 model pairs of 28** … at between $32.9$ and $45$
> comparisons per cell. … The minimum, $32.9$, sits inside the $\leq 40$ band
> fixed in advance, **so leaf-level judging is affordable.**"

**UNCLEAR, and it props up a claim elsewhere.** Identification (the graph
connects) and resolution (two adjacent models can be told apart) are different
quantities with a ~20× gap between them. The settled batch achieves 1.6 to 5.0
comparisons per model pair against the ~143 resolution requires; zero cells in
any domain qualify; Cochran's Q is non-significant in every domain tested (0.064,
0.502, 0.682, 0.137); and every domain except psychology and computer science
stopped on budget exhaustion rather than convergence. Nothing at cell level is
supported.

The conflation is load-bearing because `6_Discussion_and_Conclusion.tex:317-319`
leans on it:

> "the identification-cost result of Section 5.2.7 is untouched and **probably
> carries that argument alone**."

**Fix.** Add to `5_Results.tex` after line 559:

> Identification is not resolution. A connected graph lets a Bradley–Terry fit
> exist; separating two adjacent models in this roster needs roughly 143
> comparisons per pair, and the settled batch achieves 1.6 to 5.0. No cell in any
> domain qualifies, Cochran's $Q$ finds no significant between-cell heterogeneity
> in any domain tested, and every domain except psychology and computer science
> stopped on budget exhaustion rather than on convergence. This is structural
> rather than a budget shortfall: no affordable run closes a 30-to-90-fold gap.
> What P3 registered and what §5.2.7 measures is that per-cell judging is
> *identifiable* at this budget. That per-cell *rankings* cannot be claimed is
> Section 5.3.

Then soften `6_Discussion_and_Conclusion.tex:317-319` — the identification-cost
result cannot carry an argument for judging at leaf scale once resolution is
known to be unreachable there.

This is also `FIGURE_PLAN.md` F3, which is the right figure and is not built.

## B4. The method misstates its own cell-exclusion rule, and the rule touches the oracle

`report/03_Content/3_Method.tex:962-964`:

> "Two cells are excluded from the pool. A cell with fewer than five total
> comparisons is dropped, and so is a cell where the judge agreed with the answer
> key on under half of the decidable matches it saw."

**INVALID as a description.** `src/main/kotlin/taxonomy/service/ValidationService.kt:510-517`:

```kotlin
if (totalComparisons < 5) continue

val isConsistent = domainStats.none {
    it.agreementChecks >= 5 && (it.agreementWins.toDouble() / it.agreementChecks) < 0.50
}
if (isConsistent) { eligibleStats.addAll(domainStats) }
```

The group is dropped when **any single model pair** inside it has ≥5 agreement
checks and falls under 50% — not when the cell as a whole falls under 50%. The
same predicate recurs at `:559-561` and `:698-700`. That is a materially
stricter and differently-shaped rule than the text states, and it is far easier
to trip.

**And it is answer-key-dependent.** A filter keyed on `agreementWins /
agreementChecks` selects which cells enter the pooled Bradley–Terry fit using the
oracle the fit is later validated against. Every agreement rate and every
rank-recovery number in the thesis is conditioned on it, and no result carries the
caveat. This is the "node selection touches the oracle" item from the examiner
review backlog, now located.

**Action, before anything is written:** confirm which code path produced the
batch's per-domain agreement rates and the 196/200 recovery — `ValidationService`
(filtered) or `TaxonomyBenchmarkService.judgeAccuracyAgreement`
(`TaxonomyBenchmarkService.kt:1703`, which the `% TODO(author)` at
`3_Method.tex:1029-1033` already flags as *not* carrying the decidability filter).
Two separate defects converge here and the TODO at 1029 is the right instruction,
still outstanding.

Once known, either report how many cells the filter dropped per domain (if it is
zero, say so and the problem evaporates), or report the recovery figure both with
and without the filter.

## B5. 95.1% and 94.8% are the same quantity

- `1_Introduction.tex:166` — "$95.1\%$ of the stored traces end by declaring the answering model's own choice"
- `4_Experimental_Design.tex:233` — "$95.1\%$ of stored traces ending by declaring the answering model's selected option"
- `3_Method.tex:654` — "$94.8\%$ of the stored traces end by declaring the answering model's own selected option"
- `5_Results.tex:216` — "$94.8\%$ of stored traces state the answering model's own selection"
- `6_Discussion_and_Conclusion.tex:7` — "$94.8\%$ of the stored traces state the answering model's own selected option"

**INVALID.** One number, two values, three chapters. The source comment in
`TaxonomyArenaService.kt:663` says 94.8%. Guidelines §6: "Do not report a number
without saying where it came from." Pick one, cite the derivation, use it
everywhere. Fix in the same pass as A14, since the surrounding sentences all
change.

## B6. The `run pool` column of `tab:anchor-cells` is from the superseded runs

`report/03_Content/5_Results.tex:923-936`. Comparing the column against the
verified batch:

| domain | table `run pool` | batch routed | |
|---|---|---|---|
| Mathematics | 291 | 291 | ok |
| Physics | 237 | 229 | **≠** |
| Psychology | 265 | 265 | ok |
| Computer science | 159 | 158 | **≠** |
| Law | 277 | 276 | **≠** |
| Engineering | 202 | 158 | **≠** (28% high) |
| History | 131 | 131 | ok |
| Philosophy | 130 | 129 | **≠** |

**OUTDATED.** The `cells` column matches the batch exactly (11/10/8/6/6/4/4/3,
summing to the 52 cells the arena used), so the table mixes a current column with
a superseded one and the caption — "the run pool comes from the runs themselves"
— does not say *which* runs. Engineering is 28% off.

**Fix.** Regenerate the column from the eight `ratings_r8_*.db` and say in the
caption that it is the settled batch. This is also the natural place to add the
on-subject column from A8.

## B7. 88.8% is a pilot-roster headline in the Abstract, Conclusion and summary

`e_Abstract.tex:59-64`; `5_Results.tex:181-184`, `:354-356`, `:478-481`,
`:567-568`, `:1478-1486`; `6_Discussion_and_Conclusion.tex:371-372`.

**OUTDATED, not untraceable.** The figure traces cleanly to Run A —
`5_Results.tex:181`, $914/1029$, `MAIN` condition. But:

- it is the pilot roster, in `OPTIONS` mode, and `5_Results.tex:354-356` states
  that half its support is format-decided by the capture gap;
- the Abstract and the Conclusion quote it as the thesis's headline RQ1 number
  with none of that attached;
- the settled batch's comparable quantity — agreement conditional on the judge
  committing — is 86.1% pooled (interpretation doc §1) with a per-domain range of
  78.9 (law) to 90.3 (philosophy), on 8 domains rather than one, with no format
  artefact and no options block.

Coincidence worth knowing so it is not conflated: 88.8% is also law's on-subject
share in the interpretation doc's §4.4 table. Different quantity.

**Fix.** Lead with the settled batch everywhere the number is a headline. Keep
88.8% in `5_Results.tex:181` as the pilot measurement it is, with its two
existing qualifications. `tab:res-summary`'s RQ1 row becomes:

> The judge's verdict tracks answer correctness. On the settled batch, agreement
> with the key conditional on the judge committing is TODO(author: settle C1)
> pooled over eight domains, ranging 78.9% (law) to 90.3% (philosophy); the tie
> rate triples where the key stops discriminating; agreement is highest where
> neither response carries reasoning text, 97.0% against 83.2% at matched
> capability on 33 comparisons against 173. Rank recovery is 196 of 200
> key-decidable pairs, 98.0%, on a ground-truth ordering that is identical in
> seven of the eight domains.

## B8. The registration Outcome column instruction

`report/04_Appendix/A_Tuning_Protocol.tex:152-155` — covered by **A9**; also
check that the Outcome column, once filled, does not resurrect "met"/"failed"
verdicts. Under the withdrawn threshold there is no per-domain met/failed to
record. The honest fill is a per-domain tie-rate direction and a conditional
agreement rate, with the registration's prediction column left as historical.

`A_Tuning_Protocol.tex:127-130` already says the outcome column is empty for the
right reason. Keep that sentence.

## B9. `chen2024verbosity` — confirmed misattribution

`report/03_Content/6_Discussion_and_Conclusion.tex:244`:

> "Verbosity bias~\parencite{chen2024verbosity} is not mitigated"

`report/05_Literature_and_Index/Bibliography.bib:238-245`:

```bibtex
@inproceedings{chen2024verbosity,
  title = {Humans or {LLMs} as the Judge? A Study on Judgement Bias},
  author = {Chen, Guiming Hardy and Chen, Shunian and Liu, Ziche and Jiang, Feng and Wang, Benyou},
  booktitle = {... EMNLP 2024}, pages = {8301--8327}, ...
}
```

**INVALID.** The citation key promises a verbosity-bias paper; the entry is a
general judgement-bias study. The thesis already cites the right sources for this
exact claim in its own background chapter, `2_Background.tex:326-335`:

> "**Verbosity bias.** … \textcite{zheng2023judging} first flag the effect, and
> \textcite{saito2023verbosity} characterise it directly in preference
> labelling…"

**Fix.** `\parencite{saito2023verbosity,zheng2023judging}` at
`6_Discussion_and_Conclusion.tex:244`. Then either drop `chen2024verbosity` from
the bibliography or rename the key — a key that lies about its contents will
cause this again. `grep -rn chen2024verbosity` shows this is its only use.

## B10. R1 coherence is evidenced only on the construction pool

`report/03_Content/5_Results.tex:671-696`, the three R1 rows of
`tab:requirements-evidence`, and the R1 statement at `3_Method.tex:148-150`
("Cells must be homogeneous enough that a single rubric fits every query in the
cell").

**UNCLEAR.** All three R1 rows are construction-side: the split-acceptance
separation bar, the $J$ comparison on held-out *top-1 assignment*, and the
rubric-specificity null on construction queries. None measures homogeneity of
what the arena judged. The measurement that does exists: mean cosine distance to
the induction-pool centroid is 0.3443 for construction queries in-sample, 0.3534
held out of the centroid fit, **0.5113 for a held-out query routed into the
cell**, and 0.6070 for a random held-out query. Routing closes 38% of the gap
between chance and construction-grade proximity — 103% in law, 6% in engineering,
10–13% in cs, philosophy and mathematics. 48 of 52 cells, paired Wilcoxon
p = 1.3e-9.

The counter-argument that a routed query should land near its cell's construction
queries "because routing is the same geometry that built the cells" is true in
three domains and false in five. It should not be asserted without the number.

**Fix.** Add a caveat to the R1 rows:

> R1 is evidenced on the construction pool. The queries the arena judged sit
> measurably farther out: mean cosine distance to the cell's induction centroid
> is 0.513 for a routed held-out query against 0.353 for a construction query
> held out of the centroid fit, in 48 of 52 cells (paired Wilcoxon
> $p = 1.3\times10^{-9}$). Routing closes 38% of the distance between chance and
> construction-grade proximity, and only 6–13% in five of the eight domains. The
> rubric is applied well outside the pool it was induced from — and
> Section 5.2 measures that this changes nothing the judge does.

This is `FIGURE_PLAN.md` V2 panel (a), and it is what stops the RQ1 null being
dismissed as underpowered: the exposure is real and large.

## B11. The screen's record and the selected-domain rationale

- `5_Results.tex:1375-1382` — "all four flagged domains were run", followed by a
  TODO acknowledging the record is superseded.
- `4_Experimental_Design.tex:42-56` — the whole selected-domain paragraph, which
  still describes computer science as running and philosophy/history as
  replications against a 12-model screen.

**OUTDATED.** The screen itself (`tab:domain-screen`, 12-model fit, 2,000-draw
null) is a ground-truth-only computation and survives as a *statistic*. What does
not survive is its record: "all four flagged domains show an advantage" is the
withdrawn contrast. Rewrite the record as: the screen predicted nothing the
settled batch can confirm or refute, because the quantity it was meant to predict
(a per-domain Δρ arm contrast) no longer exists.

Also note the screen's own limit, which the thesis states well twice
(`5_Results.tex:1400-1407`, `e_Abstract.tex:81-84`): the screen is computed over
the *canonical* partition while the runs are scoped by the *adapted* one, and the
mismatch is largest where label agreement is lowest. That statement is correct
and needs no revision.

## B12. Limitations are spread across five places, and two are missing

Currently: `1_Introduction.tex:355-414` (six scope conditions),
`6_Discussion_and_Conclusion.tex:169-268` (internal / external / construct
validity), `:269-343` (measurement debt), plus inline caveats throughout Chapter
5, plus `D_Model_Rosters.tex:47-71`.

**PRESENTATION**, against guidelines §5 ("One short section. Four items. Not
threaded through every paragraph") and §6 ("State a limitation once, in the
limitations section, and trust the reader to remember it").

Two items from the interpretation doc's ranked list are **absent entirely** and
are cheap to add:

- **Item 6 — eight domains are not eight independent tests.** See A11.
- **Item 7 — hyperparameters are fitted on the construction split, not confirmed
  on it.** `4_Experimental_Design.tex:162-176` states the three-way-split problem
  honestly, but the limitations section never carries it, and nothing in the
  batch bounds it.

The doc's **item 1** — "the domain label does not describe the question
population" — is void; see the retraction. It must not be added, and it must be
struck from the interpretation doc.

Also present in the doc's list and worth checking against the text: item 3
(roster not length-matched, 6.79× against 2.91× on the superseded roster) is in
`D_Model_Rosters.tex:51-58` but not in the limitations section; item 8
(`arx_0314` bare on 21.4%, rank 2 of 8) likewise.

**Recommended shape**, per guidelines:

> 1. The judge checks answers, not reasoning.
> 2. Cells are too small to rank models inside them. ~1.6–5.0 comparisons per
>    pair against ~143 needed. Structural, not a budget problem.
> 3. Eight domains are one ordering recovered eight times.
> 4. The two arms differ in four ways, and the surviving effect is the one most
>    confounded with output format.
> 5. Hyperparameters are fitted on the construction split, not confirmed on it.
> 6. One corpus, one judge model, one roster, one seed.

plus the transferable observation guidelines §5 asks for verbatim.

---

# C — presentation, guidelines, cosmetics

## C1. The two authorities disagree on the RQ2 conditional numbers

| | interpretation doc §3.1 | audit brief |
|---|---|---|
| agreement conditional on committing, MAIN | 86.1% | 86.0% |
| … C5 | 87.4% | 87.2% |
| both-committed sign test | 10 vs 25, n = 35, p = 0.017 | 11 vs 26, n = 37, p = 0.020 |
| discordant, both committed | 10 / 25 | — |

The tie rates (13.0% / 10.9%, 8/8 domains) and the pooled unconditional rates are
consistent between them. The discrepancy is presumably a different handling of
the 188 comparisons dropped for missing embeddings (interpretation doc §3.1
restricts to the 2,788 of 2,976 that carry one).

**Settle which set governs before any of these numbers is written into the
thesis**, and state the denominator with them. Guidelines §6: "Do not mix number
sources."

## C2. "each separately falsifiable"

`1_Introduction.tex:185`:

> "It is a chain of three, each separately falsifiable:"

`6_Discussion_and_Conclusion.tex:474-475`:

> "it decomposes into three separately falsifiable links: coherent cells,
> specific rubrics, better judgments."

Guidelines §6, explicit: *"Do not use 'each separately falsifiable'-style
framing. Keep the three links, drop the epistemology: 'three things have to hold
— the cells make sense, the rubrics differ, the judging improves. The first two
hold; the third does not.'"* The suggested replacement is supplied there
verbatim; use it in the Introduction and cut the Conclusion restatement.

(Note: a `grep "separately falsifiable"` finds only the Introduction — the
Conclusion instance is split across a line break. Search for `separately` alone.)

## C3. The Introduction explains that an RQ was rewritten after the data

`1_Introduction.tex:202-217`, twelve lines beginning:

> "The decomposition was written after some of the results were in hand, and
> specifically after the pre-registered granularity analysis came back against
> the premise of the original second research question. … I state this here
> rather than leave it to be inferred, because a reader who works out unaided
> that a question was rewritten after the data arrived has every reason to
> distrust whatever replaced it."

Guidelines §6, explicit: *"Do not explain in the introduction that a research
question was rewritten after seeing data. One sentence in methods is enough and
is the normal place for it."* The passage is well-written and defensive in
exactly the way the guidelines identify as the recurring problem. Move one
sentence to `4_Experimental_Design.tex` §4.5 and cut the rest.

## C4. Two tie conventions everywhere

`5_Results.tex:27-31` (the reading-conventions box: "Every table keeps both
rows") and rule D5 at `3_Method.tex:1181-1190`, reinforced at
`4_Experimental_Design.tex:579-581` and `6_Discussion_and_Conclusion.tex:258-267`.

Guidelines §4: *"One tie convention in the main text. Pick half-weighted, justify
it in a footnote, move the other to an appendix. Reporting both everywhere
doubles every table for a distinction no reader will use."* D5's *evidence*
(ties move ρ by ±0.029 in an inconsistent direction) survives and belongs in the
appendix; the *reporting rule* it generated does not.

## C5. Grid-step machinery

`5_Results.tex:44-49` (reading box, quantisation bullet);
`4_Experimental_Design.tex:543-571`; `1_Introduction.tex:383-397` (scope
conditions three and four, including "landed fourteen grid steps apart against a
decisive threshold of two"); `6_Discussion_and_Conclusion.tex:110-114`.

Guidelines §4: *"Delete the grid-step machinery. No quantisation arithmetic, no
two-step threshold, no discussion of the seam… Replace the whole apparatus with:
'ρ is reported to three decimals; differences below about 0.02 are within
run-to-run variation.'"*

Note the arithmetic is now also wrong for the settled batch — condition three
(`1_Introduction.tex:383-388`) is stated at twelve models (0.0035); at eight it
is 0.0119, and the run-to-run spread measured on the seed replicate is six of
those steps.

The one place the machinery must survive is `A_Tuning_Protocol.tex:318-329`,
which is the record of *why* the threshold was withdrawn. Keep that; delete the
rest.

## C6. "97.0% against 83.2%" quoted without its n

`e_Abstract.tex:63-65` and `6_Discussion_and_Conclusion.tex:374-377` quote the
matched-capability trace inversion flat. `5_Results.tex:387-391` states the
caveat properly:

> "$n = 33$ against $173$; the bare-letter cell is the thinnest in the table and
> the gap should be read with that in mind"

The Abstract *does* carry "on 33 comparisons against 173" (line 65) — the
Conclusion at 376-377 carries it too. So this is nearly compliant; the residual
is that neither gives the standard errors that Results Table 5.2 does give
(2.1% and 2.5%), and the Abstract states a 13.8-point gap as settled where it is
about 3 SE on a cell of 33. One clause: "a gap of about three standard errors on
the table's thinnest cell". Low priority.

## C7. Three TODOs verified as still correct

Recorded so they are not re-litigated.

- `C_Metric_Definitions.tex:9-16` — "none is currently quoted in Chapter 5 …
  either cite them where the construction is assessed, or drop the ones that stay
  uncited." Still correct: Dasgupta cost, WLP, dendrogram purity, AvgMatch and
  routing ECE are defined and none is cited in Chapter 5 except AvgMatch via
  Appendix G. Acting on it would shorten the appendix.
- `A_Tuning_Protocol.tex:210-213` — "the settled batch runs in RESOLVED mode …
  is adjacent to P5 but is not the registered options-blind arm, and must not be
  reported as satisfying it." **Still correct and important.** RESOLVED withholds
  the options block but injects each model's own answer, so the judge can still
  verify. P5 remains unrun, and `6_Discussion_and_Conclusion.tex:501-512` is right
  to keep it as future work. The interpretation doc §7 item 5 agrees: an
  option-blind arm is "the only thing that would actually answer the rubric
  question".
- `B_Judge_Generation.tex:104-107` — the rubric-isolation run (MT-Bench system
  prompt through the rubric arm's own user template and parser). Still correct,
  and now *more* important: the surviving RQ2 effect is a tie-rate gap, and the
  interpretation doc ranks output format as the most direct mechanical route to a
  tie-rate gap, ahead of the system prompt. Without this run the decisiveness
  result cannot name the rubric.

## C8. One supportable line on routing provenance

`report/03_Content/5_Results.tex:961-987`

Everything in §5.3.2 as written is correct (see A8). What is worth **adding** is
one sentence, because the measurement now exists and it supports the thesis:

> Measured on what the batch actually judged rather than on the harness export,
> 77.8% of the 1,637 routed questions carry the MMLU-Pro category their cell was
> built from — 94.6% in law and no lower than 68.4% in any domain. Part of the
> remaining fifth is MMLU-Pro's own label taxonomy rather than misrouting:
> graph-theory combinatorics is filed under computer science and routes into the
> combinatorics cell, where it belongs.

Two constraints on how this is written.

- **Do not present it as a limitation.** It is corroboration for R1 measured on
  the evaluation side rather than the construction side, which is the one place
  R1's evidence was thin (**B10**).
- **Do not attach a behavioural claim to it** until interpretation doc §4.4 is
  recomputed. "The judge does not care whether the question is on-subject" is
  currently unsupported: that regression was fitted against the retracted
  classification.

Placement: `5_Results.tex:961-987`, after the label-agreement paragraph. It does
not need a figure — `FIGURE_PLAN.md` V1 `routing_provenance` was specified to
carry a 74%-versus-37% contrast that does not exist, and should be dropped or
respecified rather than built.

## Other small items, no separate treatment needed

- `5_Results.tex:1488-1497`, RQ2 row of `tab:res-summary`: currently a TODO
  comment plus a list of withdrawn per-domain Δρ values *inside the printed
  table cell*. Check what this compiles to — the `%` comment on line 1488 is
  followed by non-commented text on 1489-1497, so the withdrawn Δρ values
  (psychology +0.0210, physics +0.0140, …) are **printed in the summary table**
  along with the sentence explaining that they are superseded. Same failure mode
  as A4 but less severe, because the surrounding text disowns them.
- `6_Discussion_and_Conclusion.tex:379-388`: the fifth bullet of "what was
  demonstrated" is a TODO comment sitting inside an `itemize`; the preceding
  bullet at 380-381 ("a paired contrast between cell-scoped and generic rubrics
  whose high-power statistic separates the arms in no domain") prints and is
  approximately right, but "high-power statistic" is the unconditional agreement
  rate — see A9.
- `4_Experimental_Design.tex:380-384`, `tab:arena-conditions`, C5 row: "What it
  controls: **the partition itself**". Contradicts the paragraph immediately
  below it (389-397) and Appendix A §A.5. Fix the table when you rename C5 per
  the TODO at 398-402.
- `D_Model_Rosters.tex:74-77`: the TODO says this section reduces to one sentence
  "once Chapter 5's Run A and Run B material is restated". Still correct. Note
  that `Table~\ref{tab:model-roster-pilot}` lives in Chapter 4
  (`4_Experimental_Design.tex:249-271`) while `tab:model-roster` lives in
  Appendix D — the two rosters are documented in different places for no reason,
  and Appendix D:112-117 has to cross-reference Chapter 4 to describe Run A's
  roster.

---

## What to write first

Ordered by damage prevented per hour.

1. **A4** — delete the broken fragment in the Conclusion. Five minutes, currently
   printing.
2. **A1, A2, A3** — the Abstract. It is the first thing an examiner reads and
   three of its five paragraphs are superseded.
3. **A9** — fix the six TODO instructions before writing `sec:res-c5`, or the
   rewrite reproduces the retired claim.
4. **A12, A13** — two appendix corrections, both short, both currently wrong
   about what the system does.
5. **A15, A16, B1, B6** — the roster/run-inventory sweep. Mechanical, large,
   and it is what makes Chapters 4 and 5 internally consistent.
6. **B4** — establish whether the oracle-dependent cell filter fired. This one
   could move a headline number and should be settled before any agreement rate
   is quoted.
7. **C8** plus correcting `docs/results-interpretation-2026-07-31.md` §4.4, §4.6
   and §5 item 1. Do this before anyone else reads that document as authority.
8. Everything else.
