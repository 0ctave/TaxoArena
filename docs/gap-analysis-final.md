# Gap analysis — `report/` against the corrected evidence record

Written 2026-07-30, against every `.tex` under `report/`, paragraph by paragraph. Nothing in
`report/` was edited in producing this. The evidence baseline is `docs/README.md` and the
documents it marks CURRENT.

> **Its arena numbers are superseded (2026-07-31).** This file checks `report/` against the
> M = 12 batch, which is no longer the results. Its structural findings — placeholders,
> missing definitions, argument order, the protected devices — all stand. Its per-domain
> arena figures do not: read every one as "correct for a superseded batch". The five
> revised-scheduler runs are in `docs/newlogic-rerun-record.md`; the per-`file:line`
> replacement list is in `docs/stale-results-audit.md`. In particular, the line "Every
> printed number in this table is **correct**" is a statement about the M = 12 batch on
> 2026-07-30, and the instruction to add a computer-science row marked pending is
> executable now — computer science closed at +2.00 / +8.00, a registered null that failed
> positive.

**Ranking.** `BLOCKING` — false or unsupported; an examiner would find it. `HIGH` —
misframed or materially stale. `MEDIUM` — clarity, structure, or a missing definition.
`POLISH` — wording.

Counts: **31 BLOCKING · 47 HIGH · 44 MEDIUM · 33 POLISH.**

---

## The one-paragraph summary

The thesis is in better shape than its own notes suggest. Chapter 5 is not a placeholder —
exactly one placeholder box survives in it, and roughly sixty derived figures reconcile
arithmetically on inspection. The protected devices are all present and intact. No confidence
interval appears anywhere in the main text.

The problem is narrower and sharper than "stale numbers". **The whole report is frozen at six
paired domains and at a superseded generation of the domain screen**, and those two facts
combine into a single claim — *"the screen's classification matches the sign of `Delta rho`
in all six domains"* — that the thesis asserts in five places as its strongest result, and
that the evidence refuses. Philosophy was not flagged by the screen and produced the largest
advantage in the corpus. Physics was flagged, was run, met the threshold under both
conventions, and appears in the report only in a sentence saying it was never tested.

Behind that sits the second BLOCKING cluster: **the mathematics confound is not in the
report at all.** The thesis's one failed pre-registered prediction rests on a comparison graph
three times sparser than every domain it is compared against, the confound is registered under
Addendum 4, and no chapter mentions it. The report has the raw fact — Chapter 5 says "Run B
left 46 of 66 pairs with no data" — and never carries it into an interpretation.

Fix those two clusters and the great majority of the overclaim goes with them. Almost
everything else on this list is stale-number maintenance.

---

## BLOCKING

The 31 blocking items fall into seven clusters. Fixing a cluster fixes every member.

### Cluster 1 — the screen is presented as a clean predictor. It is not. (5 sites)

The screen predicts a **domain aggregate**: whether a domain's own ground-truth ranking
departs from the corpus ranking. It says nothing about whether cells *inside* a domain differ.
The correlation between screen p and within-domain between-leaf agreement is **+0.072**.
Philosophy, at p = 0.053, was **not flagged** and produced the largest `Delta rho` in the
corpus (+0.049 / +0.042).

| site | says | fix |
|---|---|---|
| `02_Prematter/e_Abstract.tex:52-55` | "the screen's classification matches the sign of the rank-correlation gap in all six" | State the eight-run count and the mismatch in the same sentence: the screen flags the domains where a per-leaf advantage appears, with one miss in each direction. Do not call it a predictor. |
| `03_Content/1_Introduction.tex:538-548` | "The screen therefore predicts where cell-scoped judging pays, and the one domain that departs from the pattern does so against the thesis." | Two domains depart, and one departs *in favour*. Replace the closing claim with the actual pattern and the +0.072 bound. |
| `03_Content/6_Results.tex:709-713, 1277-1287, 1388` | "six of six" concordance | Rewrite as six of seven with one false negative, and say that the false negative is the largest effect in the set. This is the chapter's strongest claim and the weakest-supported. |
| `03_Content/8_Conclusion.tex:51-54` | "it flags eight" and "matches ... in all six" | Seven clear p < 0.05, not eight. Rewrite to: correctly classified psychology, physics, history and law as reordering and engineering as not; missed philosophy; mathematics unresolved. |
| `04_Appendix/10_Appendix_ModelRoster.tex:66-73` | "its classification agrees with the arena's sign in all six domains run ... a refit could not change that agreement" | Delete "could not change that agreement". Replace with the record, including the philosophy miss. |

**The report needs one settled formulation of what the screen does, stated once and
referenced.** Right now five passages make five different strength claims.

### Cluster 2 — the mathematics confound appears nowhere. (5 sites)

Mathematics is the only paired run predating commits `5e1be09` (bootstrap floor) and
`a5c36fd` (per-(leaf,pair) shuffle). Pair coverage **20 of 66**, leader in 55% of comparisons,
against 66/66 everywhere else. Registered in Addendum 4; re-run pending.

| site | says | fix |
|---|---|---|
| `03_Content/6_Results.tex:715-726` | "it is a domain where the partition costs something. That is a result about the partition." | **The single most important missing paragraph in the report.** Add a registered-confound paragraph after 726 naming Addendum 4, the 20/66 asymmetry, the two commits and the pending re-run. Then downgrade to "recorded as failed, with a registered confound that may account for it". |
| `03_Content/8_Conclusion.tex:64-72` | "on Math it is decisively negative ... it costs where they do not, and which case applies can be determined offline" | Delete "it costs where they do not". Replace with: the one registered failure sits on a graph three times sparser than every domain it is compared against, and no property of mathematics may be inferred from it yet. Also: "decisively" holds only under half-weighting — under drop the gap is exactly at threshold. |
| `02_Prematter/e_Abstract.tex:48-52` | the failed prediction, unqualified | Add a clause naming the coverage confound and the pending re-run. A failed prediction must not stand unqualified in an abstract. |
| `03_Content/1_Introduction.tex:59-63` | "designated in advance as the domain where nothing should be found ... returned a verdict for the partition-free arm" | Same clause. Make explicit that the failure is currently unattributable to the domain. |
| `03_Content/5_Experimental_Design.tex:386-393` | the pre-registration summary stops at the void conditions | This is where a reader checks what was registered. Add the confound, the coverage numbers, the two commits, the pending re-run, and Addendum 4's three pre-fixed readings. |

### Cluster 3 — six paired domains where there are eight; physics stated as never tested. (7 sites)

| site | says | fix |
|---|---|---|
| `03_Content/6_Results.tex:759-766` | "economics, health, **physics** and *other* were flagged and never tested" | **Physics was run, is registered, and met the threshold under both conventions.** Delete it from the untested list. |
| `03_Content/8_Conclusion.tex:131-138` | same never-run list including physics | Same fix. |
| `03_Content/6_Results.tex:585-618` | `tab:c5-all-domains`, six rows | Every printed number in this table is **correct**. Add a physics row (+0.0140 / +0.0140, 83.8 / 79.8, screen "reorders") and a computer-science row marked pending. Fix the caption at 588. |
| `03_Content/5_Experimental_Design.tex:45-52` | "Six domains are reported ... four --- law, philosophy, history and psychology --- ... two --- Math and engineering" | Seven complete plus one running. Flagged-and-run: psychology, physics, history, law. Cleared-and-registered-null: engineering, mathematics, computer science. Philosophy stated separately as the threshold-region domain the screen did not flag. |
| `03_Content/1_Introduction.tex:56-59` | "the four domains whose models do reorder --- law, philosophy, history and psychology" | Physics missing; philosophy does not belong. Also "small margin that never changes sign" understates philosophy (+0.049, seven times threshold) and overstates law (+0.000 on half-ties). |
| `03_Content/1_Introduction.tex:519-537` | "Six domains were run"; "Four of the six carry a domain-specific prediction fixed in writing beforehand" | Eight. Five registered (psychology, physics, law, engineering-null, mathematics-null), two replications (history, philosophy), computer science registered and running. |
| `02_Prematter/e_Abstract.tex:55-58, 68-69` | "the four flagged domains --- law, philosophy, history, psychology"; "six domains of fourteen" | Correct the roll-call; name law as met-on-drop-only; move philosophy out of the flagged set. Eight of fourteen. |

### Cluster 4 — the screen table itself is a superseded generation. (1 site, high blast radius)

`03_Content/6_Results.tex:1228-1234, 1249-1263`. **Only psychology matches** the current
screen: history 0.003 vs 0.009, law 0.008 vs 0.011, physics 0.017 vs **0.004**, philosophy
0.046 vs **0.053**, engineering 0.706 vs 0.817, computer science 0.535 vs 0.751, mathematics
**1.000 vs 0.289**.

The mathematics row is the damaging one. *"Math is the clearest negative in the corpus"* and
*"at this band the models order identically in Math and globally, so an arena there has
nothing to detect"* are both false at p = 0.289 — engineering (0.817) and computer science
(0.751) are the clear negatives. That sentence is the stated justification for mathematics as
the registered null arm, restated at `:456-459`, `:1233-1234` and `:1294-1303`.

**Fix:** regenerate the table from `tools/analysis/domain_reorder_screen.py` at the 12-model
roster, and reconcile the mathematics and philosophy rows in the prose. The table currently
matches `docs/evidence-audit-2026-07-30.md:96`, which is itself superseded — do not use that
file as the source. Note also `08_Conclusion.tex:136` prints physics at 0.017 and
`10_Appendix:66` prints law at 0.008: state which fit each `p` came from at every quotation.

### Cluster 5 — three confidence-interval promises the thesis cannot keep. (4 sites)

The Bradley-Terry variance correction used `1/K` instead of `1/K^2`. No pre-correction
standard error is a measurement, and the intervals were never recomputed.

| site | says | fix |
|---|---|---|
| `03_Content/2_Literature.tex:193-195` | the defended conjunction includes "Bradley--Terry coefficients with Fisher-information confidence intervals" | Drop "with Fisher-information confidence intervals"; keep the estimator. Also change "consumed by a router" to "intended as a routing substrate" — the thesis deploys no router. |
| `03_Content/2_Literature.tex:645-646` | "Bradley--Terry profiles carrying Fisher-information confidence intervals" | Same. |
| `03_Content/2_Literature.tex:663-664` | "per-cell Bradley--Terry profiles carrying formal confidence intervals" | Same. All three state a deliverable the thesis cannot report. |
| `03_Content/4_Methodology.tex:165` | "No confidence interval computed **before the correction** is quoted" | Too narrow — it licenses post-correction intervals that do not exist. Change to: no Bradley-Terry confidence interval appears anywhere; the pre-correction ones are not measurements and the corrected ones were not recomputed. |

Related, `03_Content/4_Methodology.tex:412-414`: *"the query-level bootstrap intervals of
Section~\ref{sec:exp-metrics} are the reported defence against it."* That defence does not
exist — `TaxonomyRankingService.kt:875-900` shows the query bootstrap collapsing below its
inverse-variance floor and being substituted, with the leaderboard marked unreliable. Replace
with the honest version: the independence assumption is violated and nothing corrects for it.
This costs nothing, because the headline quantity is `Delta rho`, not an interval.

### Cluster 6 — three algorithm descriptions the code does not implement. (3 sites)

| site | says | evidence | fix |
|---|---|---|---|
| `03_Content/3_System_Architecture.tex:138-153` | "The loop stops when the structural edit count between consecutive iterations has been zero for five consecutive iterations ... The criterion is structural, not objective-based" | `TaxonomyEngine.kt:607-611, 651-658` — the rule is a **disjunction**, and the frozen run stopped on the *objective* arm. `TaxonomyStabilizer.kt:45-48` gives the structural arm a floor of `max(0.8 x anchors, 5)` = **11** iterations, so it could not fire by iteration 10. The run log closes with *"Early stopping triggered in iteration 10 due to convergence (J stationarity)"* and reports `GED converged=false` at every iteration. | Rewrite as the disjunction, say which branch fired and why the other could not, and keep the limitation — which is now **stronger**: the criterion that actually fired is objective-based, so a structural oscillation with a stationary `J` would satisfy it. |
| `03_Content/4_Methodology.tex:100-102` | "The verdict schema carries a numeric `confidence` ... and that field is consumed downstream rather than being decorative." | All eight paired configs set `confidenceGate = 0.0`, commented "DISABLED for both arms". Every consumer tests `confidence >= confidenceGate`, vacuously true. | The field is decorative in every reported run. Say so: the gate exists, it is disabled because the generic-prompt arm emits a near-constant value, and it affects no result. |
| `04_Appendix/11_Appendix_DAGConstructionFormalism.tex:203-213` | "`TaxonomyStabilizer` counts the structural edits ... node additions and deletions plus edge additions and deletions ... stops early once five consecutive iterations are quiescent. The canonical run stops at iteration 10, with iterations 8, 9 and 10 identical." | The tracked quantity is `jAfterEdits - jBeforeEdits` (`TaxonomyEngine.kt:483`) — an **edit-phase objective change**, not a count. The certificate has **period 1**. | As written the described rule cannot produce the described outcome. Rewrite around the actual quantity and the disjunctive rule; state which branch fired and that the certificate is period 1. This is the sentence a reader checks "certified fixed point" against. |

### Cluster 7 — five remaining singletons

| site | says | fix |
|---|---|---|
| `03_Content/1_Introduction.tex:174-197` | the within-domain vs between-domain leaf comparison, median 0.907 against 0.942, plus a three-deep caveat paragraph | **The comparison is on the irreproducible list** — its between-domain arm does not reproduce — and the caveat leans on the withdrawn 11-band flatness pair. **Cut 174-197 entirely.** Replace with one sentence forward-referencing the granularity analysis and `fig:domain-screen`, which is what `figures-plan-v3.md` recommends for this position. Cutting also removes a stacked-caveat paragraph. |
| `03_Content/1_Introduction.tex:342-348` | "an eleven-fold change in the number of cells, and a routing correction worth +10.3% ... both change the system's measured discriminative power **by zero**" | Stronger than any surviving number. The flatness pair is irreproducible (0.973/0.936 published, 0.948/0.908 returned) and the +10.3% half rests on the irreproducible re-routed 0.922. | Recompute and quote what the script returns, or weaken to "by less than the analysis can resolve" and drop the +10.3%. The author's own TODO flags this sentence. |
| `03_Content/1_Introduction.tex:550-567` | "Three scope conditions are stated in advance because they bound everything downstream" | Two that bound everything downstream are missing: the mathematics coverage confound, and the no-confidence-interval rule. Add both as fourth and fifth, one to two sentences each, each with a forward pointer. |
| `03_Content/6_Results.tex` — omission | the leaf-substructure permutation null is entirely absent | `tools/analysis/leaf_substructure_null.py` exists and its header documents both the corrected null and the error it corrects (independent sampling gave pseudo-leaves 11-26% overlap where real leaves have 1.6-4.9%). Add a subsection after §6.3.3 reporting: no domain shows sub-structure after correction; economics p = 1.000, health p = 1.000, law p = 0.957 (leaves agree **more** than random splits of the same sizes); and the wrong first version. This is the direct evidence for "cells do not create evaluative diversity" — the chapter currently supports that claim only with the granularity table, a weaker instrument. **Do not import the within-domain vs between-domain comparison from the evidence audit; it is irreproducible.** |
| `03_Content/7_Discussion.tex:305-307` | "the leaf-level between-cell agreement, 0.922 against 0.884 under two defensible assignment conventions" | 0.922 on re-routed assignments is irreproducible. Withdraw the pair into the corrections register, or re-derive before submission. |

Plus three off-plan figure placeholders, all BLOCKING because the figure budget is two
appendix figures and the report ships three placeholders:
`04_Appendix/7_Appendix_TuningProtocol.tex:182-197` (calibration sweep),
`04_Appendix/11_Appendix_DAGConstructionFormalism.tex:700-711` (proposal-gate flow; its
caption also describes the *superseded* lexicographic rule) and `:716-730` (accept/reject
scatter). Cut all three, or amend `figures-plan-v3.md`.

---

## HIGH

### Arithmetic and statistics that do not check out

| site | problem | fix |
|---|---|---|
| `6_Results.tex:970` | "$J$ is higher on 2 of 5 seeds, **sign test p = 0.812**" | An exact sign test at 2 of 5 gives p = 1.000 two-sided, 0.5 one-sided. 0.812 cannot come from a sign test on n = 5. Name the actual test or recompute. |
| `6_Results.tex:535-537` | "a 5/0 sign-test result at p = 0.031 that BT erases to 5/2/4 at **p = 0.227**" | 0.031 is correct as a one-sided exact test (1/32). 5 vs 4 with 2 ties does not give 0.227 on a sign test. Name the test and the tail, or recompute — as written the two p-values appear to come from different procedures. |
| `6_Results.tex:736-738` | "**four** of the eight decisive-threshold comparisons ... sit between one and six grid steps" | The eight in grid steps are 0, 6, 14, 12, 3, 3, 6, 6. **Five** sit in [1,6] and one sits at zero. Rewrite: "five of the eight, and law's half-weighted contrast is exactly zero." |
| `6_Results.tex:683` | `17.6\%` used at `:680` as psychology's MAIN tie rate and at `:683` as history's | Almost certainly a copy error. Prediction 2's history verdict turns on it. Verify and correct. |
| `6_Results.tex:1138-1142` | centred residuals `+0.024 / -0.024` (8-model), `-0.109 / -0.009` (11-band), against a null of `-1/(C-1)` | At C = 14 the null is -0.077, so the 8-model value +0.024 is *nearer zero than the null* and cannot support "indistinguishable from the centring null and not zero". These four replace the withdrawn quartet and are themselves unconfirmed. State honestly that the residual is small and its sign is unstable across rosters, and that this control cannot separate zero from the centring null. Cite the script. |
| `6_Results.tex:780-781` | "2,900 to 3,900 judge calls for 87 cells against a budget of about 10,000" | Unit mismatch. 87 x 32.9-45 is 2,862-3,915 **logical** comparisons; the chapter's own convention at `:40-42` gives `B_API = 2 B_logical`, so 5,724-7,830 API calls. Headroom is roughly a quarter, not two-thirds. State both sides in the same unit. |
| `6_Results.tex:338-342` | "34 of the corpus's 47 evaluated models"; "13 models ... to 37"; "maximum valid roster is 36" | 13 + 34 = 47, not 37. Ten models unaccounted for. Explain or correct. |
| `7_Appendix_TuningProtocol.tex:93` | "the **eight** hard gates in Table~\ref{tab:pareto-gates}" | The table lists **six**. |
| `7_Appendix_TuningProtocol.tex:268` | "**Four** decision rules were fixed in dated documents" | Five subsections follow. "Five decision rules, four of which govern runs that happened." |
| `5_Experimental_Design.tex:151-157` | tabular preamble declares six columns (`p{3.6cm}ccccc`); header and every row supply five | Change to `p{3.6cm}cccc`. |
| `4_Methodology.tex:405` | "Three of these are load-bearing, and **two** of the three did not hold" | Three failures are then discussed. "None of the three survived intact." |
| `6_Results.tex:792-798` | "Five measurements" | Six are listed. |

### Stale scope, roster and provenance

| site | problem | fix |
|---|---|---|
| `7_Discussion.tex:283` | "Runs~B and~C postdate the fix and ran with measured standard errors" | Run B **is** the mathematics run — the one that predates the fixes. This file says eleven lines earlier that measured SEs begin at law. Move Run B into the preceding bullet with Run A. |
| `10_Appendix_ModelRoster.tex:8-13` | the canonical 12-model roster is read off `arena_math_paired/seed_42/manifest.json` | Defensible (the roster is identical across runs) but must be said, along with the fact that this run's own coverage is a separate limitation. |
| `10_Appendix_ModelRoster.tex:29-33` | "the scheduler never paired them directly across 2,640 comparisons ... a separation well inside the **corrected** standard errors" | Two problems. The non-pairing is a consequence of the 20/66 coverage, not a scheduler choice — the text reads as though the scheduler declined. And Run B has no corrected standard errors; the Discussion says measured SEs begin at law. |
| `5_Experimental_Design.tex:136-139` | "the binding constraint is $\binom{11}{2} = 55$ at the corrected roster" | Every paired run is 12 models, `binom(12,2) = 66`, and the registered floor is a 66-pair bootstrap floor. The chapter itself says "every arena run sits on twelve" at `:232`. Keep 11 only for the screen and the reliability constant. |
| `5_Experimental_Design.tex:228-236` | "The screen and the reliability constant sit on an eleven-model roster while every arena run sits on twelve. The mismatch is **recorded rather than resolved**." | The screen half **was** resolved: Addendum 3 recomputes it at the 12-model roster with a 2000-draw size-matched null, and declares the 8- and 11-model generations superseded. Split the two halves; keep the caveat for `c = 2.52` only. |
| `5_Experimental_Design.tex:355-362` | "amended through 2026-07-28, with every amendment predating the Run~C law results" | Addenda 2 (2026-07-29), 3 and 4 (both 2026-07-30) exist, each fixing predictions before its runs launched. Extend to 2026-07-30 and add one sentence per addendum. |
| `7_Appendix_TuningProtocol.tex:267-367` | five decision rules, none covering psychology, physics, philosophy, history, engineering or the re-run | Every "registered" in Chapter 5 for those domains is uncheckable against this appendix, which is exactly what its opening sentence promises it enables. Add a per-domain amendments table: registration status, date, outcome. |
| `7_Discussion.tex:164`, `8_Conclusion.tex:76`, `6_Results.tex:34, 61, 100, 112, 575, 588, 620-624, 665-685, 754, 1386-1398` | six paired runs / seven arena runs | Eight paired runs; nine runs counting the pilot. Seventeen sites in Chapter 5 alone; the full list is in cluster 3 above plus these. |
| `6_Results.tex:128-134` | the offline-analysis inventory | Omits the polyhierarchy analysis (§6.3.5) and the leaf-substructure null. |

### Overclaim, missing bound, missing provenance

| site | problem | fix |
|---|---|---|
| `e_Abstract.tex:56-58` | the per-leaf arm "never trails", claimed with no bound | **Add the precision-gain bound.** Per-leaf rankings track the domain ranking, so the gain is a sharper estimate of one ranking, not a different one per cell. Ground truth requires this wherever a positive is claimed; the abstract claims one and does not carry it. |
| `8_Conclusion.tex:51-72` | every positive claim in the Conclusion, and the bound appears nowhere in the chapter | Insert one sentence after the domain list: what a positive `Delta rho` buys is a less noisy estimate of a ranking the two arms already share — leaf-vs-domain rho 0.895-0.993 on law — not the discovery of capability the domain arm misses. |
| `6_Results.tex:742-757` | the bound is present and correctly placed, but built entirely on the granularity null | The **direct** evidence is absent: law leaf-vs-domain rho 0.895-0.993 against GT-vs-GT 0.873-0.970, in an arena domain that was actually run. Make that the load-bearing sentence; the granularity null becomes corroboration. Check the bound also travels to `:620-624` and `:1386-1398`. |
| `1_Introduction.tex:64-66` | the bound is asserted with no number where one exists | Add the law comparison in one parenthetical. It converts the thesis's most load-bearing bound from assertion to measurement. |
| `e_Abstract.tex:46-48` | "a paired arm that removes the partition entirely matches the key to within half a percentage point (94.2% against 94.7%)" | **Mathematics only.** Four domains run the other way (physics 83.8/79.8, history 83.3/79.4, psychology 85.2/84.3, all favouring MAIN) and philosophy dissociates. Unqualified this reads as corpus-wide. Name the domain and give the range. |
| `6_Results.tex:795` | same figure, same problem | Quote the range across domains, not the single closest one. |
| `e_Abstract.tex:45-46`, `1_Introduction.tex:49-50` | "a judge given no rubric at all reaches the same winner on 99.4%" | Run A pilot, mathematics cells, and the same run has the capture gap — 4 of 8 models with no stored text, 50% of comparisons mixed. Add "on the pilot run's mathematics cells" and cross-reference the capture-gap section, which sits 500 lines later and carries far less weight than this headline. |
| `7_Discussion.tex:69` | "Two judges that disagree in 10 of 1,736 comparisons cannot produce a detectable ranking difference **at any sample size**" | Same provenance problem, plus a generalisation the eight-run result refutes. Name the run in the sentence and bound the generalisation to that roster. |
| `e_Abstract.tex:60-62` | "87 cells whose induced rubrics are cell-specific against a **size-matched** randomised null" | The test is 87 leaf rubrics against **13** random cells. "Size-matched" is not supported by that description. Drop it or state the actual design. The artifacts (`build/rubric_null/`) are untracked — one clean checkout from unsupported. |
| `6_Results.tex:688-698` | prediction 3 rests on Bradley-Terry standard errors ("2.4 SE", "2.8 SE", "2.2 SE") | The footnote says "pooled" but never names the variance convention, nor whether the `1/K^2` correction applies to these runs. Add one clause naming the corrected form and the commit, otherwise prediction 3 rests on a quantity the thesis elsewhere reports as buggy. |
| `6_Results.tex:1396` | "The high-power key-agreement statistic separates the arms in **no** domain" | Asserted without SEs. History is +3.9 pp and physics +4.0 pp; on per-arm counts of order 1,000 the combined SE is ~1.7, so both are ~2.3 SE. Add a per-domain SE column to `tab:c5-all-domains` or drop the absolute. |
| `7_Discussion.tex:274-278` | "Run~A's scheduler therefore consumed floor-constant standard errors", then three mechanical consequences | 45 of 176 stored values sat at the floor; the rest had median 0.09 — stated eleven lines earlier in the same file. Rewrite as "floored for about a quarter of nodes and understated for the rest", and downgrade the three consequences to conditionals. `12_Appendix_Numerics.tex:157-158` already has the correct absolute wording; bring this into line with it. |
| `4_Methodology.tex:161-164` | the 176-value standard-error census | A share of the stored values are `[ARENA-SE]` guard substitutions rather than fitter output, and there are two floors (variance `1e-6` before the root, `0.01` after). Name the run and the export, and add one clause: the census bounds the damage rather than measuring it. |
| `6_Results.tex:206` | the replacement value "0.90--0.93" for the withdrawn correctness-blind rho | Unsourced, and it substitutes for a value already withdrawn once for irreproducibility. Cite the script and its tie convention inline, or carry only the direction, which the paragraph already does. |
| `6_Results.tex:3-14` | the chapter opener: "the rubric contrast in §6.3 is flat" | Written when mathematics was the only paired result. Reframe to the two-part finding — the judge bypasses the partition on this corpus, **and** per-leaf judging still buys a small consistent precision gain where the screen flags. Keep the announced-reframing device; replace "flat". |
| `6_Results.tex:434-437` | §6.2.6 opener: "Removing the partition changes nothing the high-power metric can see" | A mathematics-only statement at the head of an eight-domain section. Two sentences: mathematics' verdict in its own subsection; the section opener states what the eight-domain set shows. |
| `8_Conclusion.tex:29-31` | the construction "reaches a certified structural fixed point, its acceptance rule is calibrated ..." | `11_Appendix:676-678` records that both natural corroborations of the gate were tested and **refuted**, and it is adopted on coherence alone. Append that clause. |
| `1_Introduction.tex:290-295` | "a framework that ... can discover capability dimensions the labels do not presuppose" | The permutation null shows no domain has evaluative sub-structure; three domains' leaves agree *more* than random splits. Left unqualified in the problem statement this promises what the thesis later contradicts. Keep as motivation, add the forward pointer in the same item. |
| `1_Introduction.tex:472-483` | Contribution 2 reports only the null and the failure | Restate as: a small consistent per-leaf advantage in the domains the screen flags, bounded as a precision gain; one clean registered null (engineering); one failed registered prediction (mathematics), confounded. |
| `2_Literature.tex:654-670` | the Synthesis closes the background with an unqualified gap claim | Keep the gap statement, drop the third leg of the conjunction (the intervals), and add one closing sentence naming what the test returned. That converts advocacy into a set-up. Answers the author's own TODO at `:656`. |
| `2_Literature.tex:434-437` | "ties counted as half-wins following Davidson" | Both conventions are always reported, and the difference is decisive in two domains — law is +0.000 half and +0.021 drop; engineering flips sign. Declaring one convention here contradicts the reporting rule. |
| `8_Appendix_JudgeGeneration.tex:76-78` | the same Davidson citation for the half-win convention | Davidson 1970 introduces a tie-**propensity parameter**, which is what this system does not do — `7_Discussion.tex:231-238` calls a Davidson fit "the principled repair". Citing Davidson for the convention attributes it to the paper that replaces it. |
| `8_Appendix_JudgeGeneration.tex:56-66` | the judge-prompt appendix never says the options block is shown, nor that 94.8% of traces state their own answer | **This is the mechanism of the entire RQ1 finding**, and this appendix is where a reader looks to verify it. Add a short paragraph: what is in the prompt, what is not, and the measured consequence. |
| `8_Appendix_JudgeGeneration.tex:64-66` | "Both arms therefore differ in the rubric and in nothing else ... same model pairs **where the scheduler allows**" | The subordinate clause hides the spread: overlap runs from >99% down to 83.3% on engineering, and on mathematics the arms cover 20 of 66 pairs. Give the measured range. |
| `8_Appendix_JudgeGeneration.tex:20-22` | promises the same-model rubric-generation choice is "revisited as a limitation in Section~\ref{sec:disc-debt}" | It is not. Either add it — same-model rubric induction bakes the judge's own priors into the rubric, which weakens the rubric-vs-rubric-free contrast — or repoint. |
| `7_Discussion.tex:49-54` | "cell identity adds essentially nothing to model ordering", no exception | Three of 293 within-domain leaf pairs survive Bonferroni, **all in mathematics**, separating continuous from discrete. Add the exception in one clause. It is load-bearing: the one domain where cells demonstrably differ is the one where the paired arm failed. |
| `7_Discussion.tex:107-141` | "four instances" of the apparatus catching its own errors | There is a fifth and it is the most instructive: the first evaluative-diversity null sampled pseudo-leaves independently (11-26% overlap against real 1.6-4.9%). Add it here and in the corrections register. |
| `7_Discussion.tex:37-41` | "an inference from the Math and law runs" | Add: mathematics covers 20 of 66 pairs and predates two scheduler fixes, so it carries less weight in this inference than law does. |
| `5_Experimental_Design.tex:105-108` | the screen "selects law, and it demotes Math to a null arm" | Four domains are flagged. Append the bound. Addendum 3 itself says the screen is not claimed as a clean predictor. |
| `5_Experimental_Design.tex:227` vs `:260-261` | internal contradiction on the 35.4% model | It cannot both be excluded at roster load by a hard-coded list and be the band-narrowing drop. Determine which and remove it from the other list. |
| `5_Experimental_Design.tex` — omission | the run conditions that separate mathematics from every other run are never stated in this chapter | Zero grep hits for the 66-pair bootstrap floor or the per-(leaf,pair) shuffle. Add a "Run conditions" paragraph: 12-model roster, identical question set, mandatory 66-pair floor with in-run coverage assertion, per-(leaf,pair) shuffle, confidence gate disabled, isolated ranking database, seed 42. |
| `5_Experimental_Design.tex:388` | "the decisive difference of two Spearman grid steps on Math" | State `|Delta rho| >= 0.007`, two steps of the 0.0035 grid at twelve models, and say it governs **all** paired runs. |
| `5_Experimental_Design.tex:418-467` | the statistical protocol omits the no-interval rule | Add one bullet. This section is where it belongs. |
| `5_Experimental_Design.tex:420-424` | "a standard error near 1.5%, and it resolves differences of about four points" | The prereg gives ~1%; at p ≈ 0.85, n = 1000 it is 1.1%. Observed gaps run 0.9 to 4.0 points, so the resolution claim is load-bearing. Quote ~1% and give the paired-difference SE, which is what the claim is actually about. |
| `3_System_Architecture.tex:86-88` | "no accepted edit, no query moved between cells" | Both are **objective changes** tested against `tau`, not counts. Describe the certificate as a four-term tolerance test on the edit-phase objective change, the re-routing objective change, and the maximum per-node change in direction and concentration. Do not describe any of the four as a count. |
| `3_System_Architecture.tex:42-44, 102` | "the same corpus must yield the same cells"; R3 rests on the certificate | Two of the four certificate terms are bounded but **not bit-reproducible** (they differ 7-10 orders below tolerance). And the determinism holds at fixed seed only: seed 42 gives 88 leaves against 64-68 for four other seeds, mean pairwise ARI 0.609. Bound R3 to "the same corpus **and seed**". |
| `3_System_Architecture.tex:80-81` | the frozen artifact is ambiguously identified | Two configs claim canonicity: `canonical_freeze.toml` is headed "THE FROZEN ARTIFACT" and gives 139/88 at `minClusterSize=30, acceptanceZ=0.0`; `freeze_mcs55.toml` gives the 154/87 the thesis cites. The acceptance rule described at `:69-71` is true of the second and false of the first. Quote the snapshot id and the two distinguishing parameters. |
| `3_System_Architecture.tex:107-154` | three non-guarantees, none about routing | Held-out queries reach a cell by soft routing, calibration error 0.2114, and the exported per-leaf share is a max rather than a sum. Cell membership on held-out data is the single thing every arena result depends on. Add it as a fourth item. |
| `4_Methodology.tex:218-224` | "query selection ... is a persisted round-robin offset over the leaf's pool, **not** a descending-cosine walk" | The offset walk is common to both samplers — what changed is the ordering key. `BtMatchScheduler.kt:465-480` records that a per-**leaf**-only shuffle left utilisation at exactly 250/379; only adding the **pair** key widened coverage. Describe it as a per-(leaf,pair) seeded shuffle walked by a persisted offset, and report the measured non-result. |
| `2_Literature.tex:487-499` | the bootstrap "operates on global rather than per-leaf pair counts" | This is precisely the mechanism behind the mathematics confound. Name the consequence in one sentence and forward-reference. This paragraph is the natural place for a reader to first meet it. |
| `2_Literature.tex:477-485` | the Fisher-information background "yields per-parameter standard errors" | Correct as background, but it promises what the results withhold. Add one clause pointing forward to the variance defect. |
| `1_Introduction.tex:517-519` | the scheduler "supports the arena rather than standing as a contribution" | Its pre-fix behaviour is the confound on the mathematics run. Add one clause: its coverage behaviour changed mid-project and bounds one run. |
| `1_Introduction.tex:52-54` | the screen "asks the same question one domain at a time" | It does not — it asks about the domain aggregate, not within-domain sub-structure, and the correlation between the two is +0.072. |
| `6_Results.tex:327-329, 1380` | "97.0% vs 83.2%, a 13.8-point gap" | The 97.0% cell is **n = 33**. `figures-plan-v3.md` cut the `trace_strata` figure for exactly this reason; the prose makes the claim the figure was cut for. Append "(n = 33 against 173)" at both sites. |
| `6_Results.tex` — figures | five of the six main-text figures are not wired in | M3 (§6.2.1), M4 (§6.3.2 and §6.2.4), M5 (§6.3.4), M6 (§6.2.6, **the centrepiece**) all have placements assigned in `figures-plan-v3.md` §5.2 and no `\begin{figure}` environment. The chapter the plan calls figure-heavy carries one figure, and that one is an appendix figure. |
| `6_Results.tex:1195-1208` | the one surviving placeholder box, `fig:granularity-flat` | `make_granularity_flat.py` **deliberately refuses to plot** and v3 marks it "do not fix". A placeholder implies a figure is coming. Delete the float, keep the table, and replace the `\ref` at `:1132` with one sentence saying the figure was deliberately not drawn because a box plot of four overlapping distributions would make a null look like a finding. |

---

## MEDIUM

**Undefined terms at first use.** House style requires a one-sentence definition in the main
text. None of these has one anywhere in the report:

| term | first use | suggested gloss |
|---|---|---|
| **vMF** / von Mises-Fisher | `2_Literature.tex:189` (used before expansion at `:203`); the abbreviation is **never named in the entire report** | Expand at `2_Literature.tex:189`, and name it once where `mu` and "concentration" appear at `6_Results.tex:828-831`. |
| **disattenuation** | `5_Experimental_Design.tex:444`; also `7_Discussion.tex:92`, `6_Results.tex:520, 1089` | "Disattenuation corrects a correlation for the measurement error in the two rankings it compares." Define once in Chapter 4 and reference. |
| **chance-corrected** | `2_Literature.tex:189-192`, again at `:268-269` | "measured against what the same split would score by chance, so the threshold does not drift with cell size" |
| **permutation null** | `1_Introduction.tex:189`; `4_Methodology.tex:393-395` | "the same statistic recomputed on cells whose membership has been randomly reshuffled" |
| **Minorisation-Maximisation** | `4_Methodology.tex:124-126` | "an iterative scheme that maximises a simple lower bound on the likelihood at each step" |
| **binary entropy**, **KDE valley weight** | `4_Methodology.tex:188-198` | "the binary entropy of the current win probability, largest when the pair is a coin flip"; "a kernel-density weight favouring gaps between clusters of scores" |
| **sandwich standard errors** | `2_Literature.tex:82` (author's own TODO) | "a variance estimate that stays valid when the model is misspecified" — or drop the term. |
| **the pre-registered decisive threshold** | `4_Methodology.tex:353` | Give the value. |

**Missing results that belong in the report.**

* `6_Results.tex` — the **three equal-on-average, opposite-at-margin model pairs**
  (deepseek/gpt-4o-mini swing 21.6, Qwen1.5-14B/Llama-3-8B 19.8, iask_pro/arx_3 15.7) are
  absent. `figures-plan-v3.md` cut the figure, but the *result* belongs in prose as two
  sentences with the post-hoc-threshold caveat: it is the only evidence that domain-level
  parity can hide margin-level disagreement.
* `6_Results.tex` — the **per-pair leaf divergence positive**: 3 of 293 within-domain leaf
  pairs survive Bonferroni, all in mathematics, separating continuous from discrete. This is
  the chapter's one genuine sub-structure finding and it is nowhere. It also bears on cluster
  2, being a real property of the mathematics partition.
* `4_Methodology.tex:46-49, 244-261` — the estimand section never names `Delta rho`, never
  says the comparison is paired over eight domains, and never gives the threshold. A reader
  arrives at Chapter 5 without the estimand. Add two sentences at `:261`.
* `1_Introduction.tex:429-435` (RQ2) — same gap. State the sign convention, the threshold and
  the both-conventions rule where RQ2 is posed.
* `7_Appendix_TuningProtocol.tex:369-375` — the corrections register omits the
  overlap-matched pseudo-leaf null and, if the 0.922 is withdrawn, the leaf-level agreement.
* `4_Methodology.tex:299-316` — never states that the arena judges each held-out query in its
  **primary** leaf only, so the judged assignment is a partition even though routing is soft
  (up to 5 leaves above a 0.25 floor; 1.12 leaves/query on eval).

**Descriptions that are incomplete rather than wrong.**

| site | gap |
|---|---|
| `3_System_Architecture.tex:69-71` | "accepted only when" omits the `SE = 0` fallback (accepted on strictly reducing node count — how pass-through wrappers dissolve) and the hard `tau` floor, which is what makes the termination bound finite. |
| `3_System_Architecture.tex:71-74` | "Two coarsening moves" — `TaxonomyMerger` implements at least four (below-floor absorption, sibling merging, redundant-node merging, pass-through dissolution). |
| `3_System_Architecture.tex:57-59` | clustering is proposed in a size-dependent PCA subspace (32/64/128) and every gate is evaluated in the full 256-d routed space. Say both. |
| `3_System_Architecture.tex:118-126` | the anisotropy limitation loses its bound when the counts are voided. A live bound survives: the bar sits 2.7x above the isotropic null p95 and below the within-node null median, and the one node that hit the boundary was declined. |
| `4_Methodology.tex:322-325, 343-345` | the standard-error gate is presented as universal. It is on in `freeze_mcs55.toml` and off in `canonical_freeze.toml`, where acceptance is lexicographic on `(J, -|V|)` against `tau`. |
| `4_Methodology.tex:38-39` | the tree claim is asserted without its result. Add a pointer: polyhierarchy was implemented, measured and removed. This pre-empts a reader who greps the code and finds `DAG_MAX`. |
| `4_Methodology.tex:206-209` | "that is the de-facto exit in practice" — give the number of runs that exited on the round cap versus per-pair resolution, or drop "de-facto". |
| `6_Results.tex:826-835` | states the fixed point at iteration 10 with the correct wording, but never states the five-iteration rule nor that the certificate is period 1. Both matter. Same at `7_Appendix_TuningProtocol.tex:42-45`. |
| `11_Appendix:224-228` vs `:676-678` | apparent contradiction: construction "deterministic under a fixed seed" against a refuted corroboration that the gate "tightens run-to-run stability". Name the axis at `:677` — across seeds, or across configurations. |
| `11_Appendix:744-771` | the retired cross-link section records the mechanics and twice defers the outcome without stating it. Give the finding in outline before the mechanics. |
| `7_Appendix_TuningProtocol.tex:86` vs `:18` | the canonical `minClusterSize` is 55, which is not on the swept `{50,75,100}` grid. Explain, or drop the "notably `minClusterSize`" attribution. Same shape at `:220` (iteration count 35 off a `{10,25,50}` grid — note 35 is a ceiling never reached). |
| `7_Appendix_TuningProtocol.tex:262` | `% TODO(calibration): finalize once taxonomy construction is frozen`. Construction **is** frozen, and this file says so at `:42-45`. Delete or defer explicitly. |
| `12_Appendix_Numerics.tex:89-113` | the KDE/valley section documents the scheduler in full with nothing anchoring it to Run A's degenerate variances or mathematics' 20/66 coverage. One closing sentence. |

**Residual polyhierarchy language in a tree system.**

* `11_Appendix:494-496` — "a multi-parent destination's membership is the sum over its
  incoming paths". Multi-parent nodes are zero by hard gate. Delete, or mark as retained
  dead code.
* `11_Appendix:305-307` and `12_Appendix_Numerics.tex:55-56` — "the **parents'**
  concentrations" / "the **parents'** vMF centroids". Singular in a tree.
* `2_Literature.tex:255-261` — the polyhierarchy outcome is deferred without being stated.
  Say the tree won; it costs four words.
* `11_Appendix:1` — `\label{app:dag-formalism}` on a chapter titled "Taxonomy Construction
  Formalism", in a file named `11_Appendix_DAGConstructionFormalism.tex`. A LaTeX label and a
  filename are not code identifiers. Rename both; five call sites. (`dagMode` / `DAG_MAX` at
  `7_Appendix:29, 161` **are** genuine code identifiers and are correctly footnoted — leave
  them.)
* `7_Appendix:120-121` — the "Acyclic: true" and "Multi-parent nodes: 0" hard gates are
  vacuous in a tree. Half a sentence noting they are retained as regression checks on the
  single-parent invariant.

**Ambiguities that will cause a reader to merge two things.**

* `6_Results.tex:374` vs `:1001, 1019, 1077` — `0.138` denotes rationale-rubric lexical
  overlap in one place and rubric-specificity median in another. Same chapter.
* `6_Results.tex:1112` — the row label says "corrected router" while column (A) says
  "construction assignments", so a skimming reader reads 0.922 as re-routed, which is exactly
  the withdrawn claim. Re-label the row.
* `6_Results.tex:1176` vs `:277-279` — the "pilot roster" spans 54.1 points in one place and
  70.9 in another. Different pools; the chapter never says so.
* `8_Conclusion.tex:20` vs `7_Appendix:471` — `83.2%` carries two unrelated quantities.
  Verify both against source; if both are genuine, distinguish them.
* `6_Results.tex:837-846` — `leaf_size_hist` is an **appendix** figure in
  `figures-plan-v3.md` but sits in main-text §6.3.1. Reconcile or record the deviation.

**Other.**

* `5_Experimental_Design.tex:13-19` — the lead sentence and caption both promise a "link"
  column that `tab:rq-map` does not have. Add it (RQ1 -> link 3, RQ2 -> link 2) or drop the
  promise. The three-links spine is protected and this is the one place it is mapped to
  conditions.
* `5_Experimental_Design.tex:283-284` — "three conditions carry every arena result". All
  eight paired runs use two arms. C3 ran once, on the pilot.
* `5_Experimental_Design.tex:44-45` — "the selection rule is a compute-budget trade-off";
  the referenced section states a four-criterion substantive rule and does not mention budget.
* `5_Experimental_Design.tex` — no forward reference to the reading-conventions box, no
  MEASURED/ARGUED marks, and the sign convention is never stated in the chapter that defines
  the arms. Add the sign convention beside the threshold, and one sentence pointing to the
  box.
* `8_Conclusion.tex:140-148` — "overlap is above 99% on Math, law, history and psychology".
  True and irrelevant next to a 20/66 pair graph. Add the sharper limitation.
* `10_Appendix_ModelRoster.tex:75-83` — a section named "The Pilot Roster" whose only content
  points back into Chapter 4 for the table. Move the table or retitle. And open the chapter
  with the roster-to-run map: pilot = 8 (Run A), every paired run = the 12, screen and
  reliability fit = the 11-band.
* `9_Appendix_MetricDefinitions.tex:38, 52, 71-83, 124` — `Section~\ref` pointing at
  chapter-level appendix labels. Use `Appendix~\ref` consistently, as `:38` and `:52` already
  do.
* **The routing-ECE aggregation defect is stated in full four times** —
  `7_Appendix:138-145` and `:452-460`, `9_Appendix:143-156`, `7_Discussion.tex:309-314` —
  each nearly identically. Keep the full statement once, in `9_Appendix` where the metric is
  defined; reduce the other three to a clause and a cross-reference.
* `e_Abstract.tex:15-20` — the translation comment says the English text "covers all six
  paired domains; no further arena run is outstanding, so it is safe to translate now."
  Computer science is running and the mathematics re-run is pending. Change the comment;
  keep the "translate, do not re-scope" instruction.

---

## POLISH

**Banned words — every occurrence.**

| site | word | replacement |
|---|---|---|
| `6_Results.tex:13` | "the judging **paradigm**" | "the way this judge works" |
| `6_Results.tex:1002` | "The result is **robust** across all three definitions" | "The result holds under all three definitions" |
| `7_Discussion.tex:207` | "contamination-**robust**ness" | "contamination-resilience" |
| `8_Conclusion.tex:95` | "judging **paradigm**" | "judging regime" |
| `7_Appendix:193` | "**robust**ness to the factor" | "insensitivity to the factor" |

No `delve`, `leverage`, `foster`, `utilize/utilise`, `facilitate`, `intricate`, `paramount`,
`transformative`, `ever-evolving`, or "it is worth noting" anywhere in the report. Chapters 1,
2, 3, 4 and 5 are entirely clean of the ban list.

Two false positives to leave alone: "harnesses" at `6_Results.tex:666, 672` means *model
harnesses*, and "two harnesses" at `10_Appendix:27` is the same technical noun.

**Importance puffery — four instances of the same move, in one chapter.**
`6_Results.tex:361` ("a denominator worth naming once"), `:524` ("is worth stating with the
same precision"), `:648` ("One asymmetry is worth recording rather than smoothing"), `:766`
("the only reason the concordance is worth quoting at all"). Keep at most one. For the rest,
just say the thing.

Also `5_Experimental_Design.tex:172-173` — "which is the strongest guarantee in the system."
Delete, or replace with what it does.

**Colon reveals.** The heaviest offenders, all to be split into two sentences:
`6_Results.tex:169-171, 246-247, 265, 275-277, 331-334, 337-339, 351-352, 370-371, 558-559,
1289-1291`; `5_Experimental_Design.tex:64, 128, 144, 246, 263, 269, 348, 371, 412`;
`4_Methodology.tex:16-17, 85-86, 109-110, 147-149, 305-307`; `7_Appendix:276-279`;
`7_Discussion.tex:29-35`.

**The `\textsc{measured}:` and `\textsc{argued}:` colons are the protected convention. Leave
every one of them.** The list colons at `5_Experimental_Design.tex:5, 100-104, 112, 356` are
fine.

**Repeated "X, not Y" antithesis.** 24 occurrences in Chapter 5 alone, 13 in Chapter 4, 14 in
the Discussion, 10 in Chapter 3, plus scattered use elsewhere — about 77 across the report.
The tic shows worst in two runs of five within a single paragraph: `6_Results.tex:891-946`
and `:1169-1205`.

Load-bearing, keep: `6_Results.tex:381` ("rationale-conditioned, not rationale-driven"),
`:1169` ("Power, not proof"), `:1181` ("Ceiling, not prediction"), `:1329` ("queries, not
concepts"); `5_Experimental_Design.tex:178` (answer-key-blind is not answer-blind — protected),
`:189`, `:252`, `:434`; `8_Conclusion.tex:4` ("set out to validate a taxonomy and ended by
measuring a judge"). Target: cut roughly half of the rest and write them as plain assertions.

**Em-dashes.** ~36 in Chapter 5, ~25 in the tuning appendix, 24 in the Discussion, ~15
mid-sentence in Chapters 3 and 4, 23 in the DAG appendix, 6 in the Conclusion, and 4 in three
lines of the abstract. Structural uses — `\item[R1 --- Coherence.]`, `\textbf{D1 --- ...}`,
run labels, table cells — are fine and should stay.

Worst mid-sentence offenders to convert: `6_Results.tex:643` (a dash-pair inside a
semicolon-joined sentence inside a caveat paragraph), `:554-555, 627-628, 655, 681, 692-693,
718, 730-731, 745, 755-756, 895-896, 915, 1231, 1283-1284`; `3_System_Architecture.tex:80-81`
and `:122-124` (both double-dash parentheticals in one sentence); `4_Methodology.tex:266-267`;
`5_Experimental_Design.tex:391`; `e_Abstract.tex:56-58` and `:62-63`; `8_Conclusion.tex:83-84`
and `:112-113`.

**Trailing -ing analysis clauses.** Chapter 5 is clean — zero. Three in Chapter 4:
`5_Experimental_Design.tex:98, 249-250, 430-432`. Break each into its own sentence.

**Stacked caveats mid-argument.** Three sites where "claim, bound, move on" breaks:

* `6_Results.tex:633-651` (engineering) — registration qualification, screen-policy
  disagreement, and tie-rate asymmetry, three caveats before the finding, at ~14 lines
  against a finding it qualifies. Footnote the registration qualification.
* `6_Results.tex:1041-1080` (rubric null) — "Three caveats travel with this result"
  immediately followed by "Three bookkeeping notes travel with this result". Six
  qualifications over 40 lines. Merge into one four-item list.
* `6_Results.tex:1168-1193` (granularity) — three named bounds plus an `\textsc{argued}` plus
  "the reader must not be allowed to collapse the two". Cut the last clause; it scolds.
* `4_Methodology.tex:152-167` — five distinct claims in one paragraph. Split into two.

**Smaller items.**

* `3_System_Architecture.tex:52` — "The construction is one paragraph in the main text."
  Announcing the length of your own paragraph. Delete; the paragraph demonstrates it.
* `3_System_Architecture.tex:149-153` — "reports `CERTIFIED: false` **indefinitely**". The
  certificate is evaluated once at freeze. Drop "indefinitely".
* `7_Discussion.tex:200` — "and less than an earlier version of this argument claimed". A
  meta-reference to a prior draft inside a live argument. Cut; the corrections register
  carries draft history.
* `7_Discussion.tex:158` — `theta` unglossed. Write "Bradley--Terry strength theta".
* `7_Discussion.tex:6-8` — "in most cases, a response that states its own selected option".
  The number is 94.8% and it is the hinge of the RQ1 argument. Quote it.
* `4_Methodology.tex:16-20` — the capture-gap paragraph is correct and abstract. Carry one
  number: 4 of 8 pilot models had no stored text, and the judge picked the text-bearing side
  863 of 868 times.
* `12_Appendix_Numerics.tex:168-171` — "these standard errors **slightly** underestimate the
  true uncertainty", where the Discussion calls the same margin unmeasured. Drop "slightly".
* `12_Appendix_Numerics.tex:145-163` — the `1/K^2` derivation checks out
  (`(K-1)/K^2 = 7/64 = 0.109` at K = 8) and `:157-158` has the correct absolute wording. No
  change; noted as the model for `7_Discussion.tex:274`.
* `12_Appendix_Numerics.tex:173-212` — the "Design-Document Mechanisms with No
  Implementation" section is a model of the register the report wants. No change. Confirm
  only that the `10.0` SE initialisation leaks into no reported value.
* `11_Appendix:328-340` — "The conclusion this passage originally drew ... does not survive
  its own corrected input." Exactly the right register. Keep.
* `11_Appendix:606-617` — the arithmetic checks (0.025/0.0093 = 2.69, 0.025/0.0055 = 4.55).
  Cut the trailing "both statements hold simultaneously"; the two clauses already read as
  compatible.
* `5_Experimental_Design.tex:411-414` — the dates read as an error (a reproduction dated
  2026-07-27 reported by an addendum dated 2026-07-28). Faithful to the source, but reorder
  so the reader does not stumble.
* `5_Experimental_Design.tex` — "Math" capitalised against lowercase "law", "physics",
  "history", "engineering". Pick one; the evidence record uses lowercase.
* `1_Introduction.tex:199-211` — the synthetic-figure caption is right to declare the values
  synthetic, but omits the forward reference to `fig:domain-screen` that the approved caption
  draft carries. Add the closing sentence.
* `2_Literature.tex:304-308` — "up to roughly 35% of single-order pairwise outcomes can be
  position-driven". Inconsistency is not the same as position-driven; noise contributes.
  Shorten to "a third of single-order outcomes are order-sensitive", which is what the
  statistic supports.
* `1_Introduction.tex:465-470` — "Four controls support the decomposition". The count is not
  verifiable from the introduction and the Results chapter organises them differently. Name
  them, or drop the count.
* `6_Results.tex:1420-1422` — two colons in one sentence.
* `6_Results.tex:863, 1328` — `\ref{app:dag-formalism}` in a thesis whose result is that the
  system is a tree. See the rename item under MEDIUM.

---

## Paragraphs that do not serve the thread

The thread: partitioning a benchmark is only worth doing if it changes what a judge can be
told; this work builds a certified partition, tests each link separately, finds the judge
bypasses the partition by verifying answers on a keyed corpus, and finds a small consistent
per-leaf precision gain in the domains the screen flags.

| site | why | disposition |
|---|---|---|
| `2_Literature.tex:548-562` | the mELO / Blade-Chest intransitivity review. The thesis never models intransitivity, never reports a cyclic component, and its central finding is that per-leaf rankings are near-identical to the domain ranking — the opposite of the Rock-Paper-Scissors setting. | Cut to two sentences, or keep with one clause saying why it is not adopted. |
| `2_Literature.tex:566-572` | lists an adaptive scheduler as a requirement the field sets. The scheduler is explicitly not a contribution, its interval-overlap rule depends on the defective BT variance, and its pre-fix version under-covered pairs. | Keep the requirement, note it is the one the implementation met only partially, forward-reference. |
| `6_Results.tex:532-539` | the win-rate/BT estimator note, landing mid-argument between the mathematics verdict and the law result. | Move to the reading-conventions box or a footnote on the Estimator bullet, which already promises this measurement. |
| `6_Results.tex:1289-1309` | the screen's two-reversal process history: 20 lines of superseded p-values in the chapter's most contested section, and cluster 4 makes them doubly superseded. | Compress to five sentences; keep only the transferable rule (compute the screen at the roster the arena will run). |
| `7_Discussion.tex:240-244` | budget accounting (`B_API = 2 B_logical`) filed under Construct Validity, where it is not a construct-validity threat. | Move to the reading conventions, or drop. |
| `7_Discussion.tex:29-35` | restates the preceding paragraph in a two-beat colon structure. | Cut to one sentence. |
| `8_Conclusion.tex:178-181` | routing as a deployable service, as the last future-work item. Routing is on none of the three links and the thesis rests no claim on it. | Cut, or tie to the motivation in one clause. |
| `11_Appendix:89-92` | the Phase 1 description duplicates `:383-428` in substance. | Cut to a pointer. |
| `7_Appendix:168-177` | three sentences explaining why a removed knob was ablated non-orthogonally. The table row and the "historical" marker already carry it. | Cut. |
| `4_Methodology.tex:416-444` | Persistence and Reproducibility. Only the `ratings.db` clearing defect changes what a reader should believe. | Cut the four-store inventory to two sentences; keep the two qualifications at full length. |
| `6_Results.tex:1318-1359` | polyhierarchy. Sits outside the three links, and the summary says so. | **Keep.** It is a clean, well-evidenced negative result and the chapter is better for it. |

---

## What is already right, and should not be touched

Recorded because a revision pass this large tends to break things that work.

* **No confidence interval appears anywhere in the report.** Every bracketed range in
  Chapter 5 is an explicitly labelled IQR; every standard error in the trace-strata and
  agreement tables is a binomial SE on a proportion, which is permitted. Keep it this way.
* **All protected devices are present and intact**: the MEASURED/ARGUED convention, the
  reading-conventions box (`6_Results.tex:20-55`), the announced reframing, the three-links
  spine, the capture-gap and failed-prediction reporting, and the sign convention. This
  analysis proposes removing none of them.
* **The withdrawal register works.** Every irreproducible figure that appears in the report —
  the correctness-blind 0.74-0.76, the redundancy 72.2%/42.2%, the centred-residual quartet,
  the flatness pair 0.973/0.936 — appears **only inside its own withdrawal**, which is the
  protected corrections convention working exactly as intended. The two exceptions are listed
  under BLOCKING (`7_Discussion.tex:305`) and HIGH (`6_Results.tex:206`).
* **`trace_strata` is fully gone.** No float, no `\includegraphics`, no stray reference. The
  surviving `trace-strata` strings are all `tab:trace-strata`, a table. (`figures-plan-v3.md`
  still warns that the float is present and will break the build; that warning is stale and
  is now marked as such.)
* **Chapter 5's arithmetic is sound.** Roughly sixty derived figures were re-checked and
  nearly all reconcile: the trace strata sum exactly to the correctness totals, the tie
  triples sum to 1,736, the grid steps are correct at all three roster sizes, the pair counts
  are exactly `binom(C,2)`, and **every printed value in `tab:c5-all-domains` matches the
  evidence record**. The table is incomplete, not wrong.
* `5_Experimental_Design.tex:333-351` (the pairing paragraph), `:176-179` (answer-key-blind
  vs answer-blind), `:427-429` (threshold arithmetic), `:444-450` (two-sided disattenuation
  at `c = 2.52`, with 7.66 correctly absent), `:376-379` and `:408-416` (rubric specificity),
  `:254-261` (exclusion arithmetic) — all verified correct against the pre-registrations.
* `6_Results.tex:1066-1069` — the rubric-null provenance paragraph, with the untracked-artifact
  caveat and both reproduction dates, is the best-evidenced paragraph in the report.
* `9_Appendix_MetricDefinitions.tex:102-117` — the Dendrogram Purity tree transition is the
  model for how the residual polyhierarchy passages elsewhere should read.
* `11_Appendix:328-340` and `12_Appendix_Numerics.tex:173-212` — both are exactly the
  register the house style asks for.

---

## Suggested order of work

1. **Cluster 4** — regenerate the screen table. Everything in clusters 1 and 3 depends on
   knowing the current p-values.
2. **Cluster 3** — add physics and computer science. Mechanical once the table is right.
3. **Cluster 1** — write the one settled formulation of what the screen does, then propagate
   to the five sites.
4. **Cluster 2** — write the mathematics-confound paragraph once, then place it in Results,
   Conclusion, Abstract, Introduction and Experimental Design.
5. **Clusters 5 and 6** — the three interval promises and the three algorithm descriptions.
   Small, self-contained, and each is a straightforward factual correction.
6. **Cluster 7** — the cuts (Introduction `:174-197`, the three figure placeholders) and the
   one addition (the leaf-substructure null subsection).
7. The precision-gain bound into the abstract and the Conclusion — one sentence each, and it
   is the sentence that most distinguishes this thesis from an overclaiming one.
8. HIGH arithmetic, then the rest.
