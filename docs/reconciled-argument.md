# The reconciled argument — code, docs, report

> **STATUS: SUPERSEDED AS AN ARGUMENT (2026-07-30). Parts 0 and 1 are HISTORICAL-KEEP and
> still the only place several checks exist.**
>
> The ladder's conclusion — that link 3 fails because the two judges agree too closely to
> produce a detectable ranking difference — is directly contradicted by the eight-run
> result. The load-bearing false sentence is in Rung 8: *"Two judges agreeing on 99.4% of
> winners cannot produce a detectable ranking difference at any n, any granularity, any
> domain count."* Five domains meet the 0.007 threshold. Rung 8's companion claim, that the
> null at n = 8 was "structural, not underpowered", is also wrong: it was underpowered, and
> 12 models separated the arms.
>
> Rungs 7 and 12 rest on superseded inputs — the independent-sampling permutation null
> (`void-results.md` §2) and the 11-band screen table, whose p-values were recomputed at the
> 12-model roster in Addendum 3 of `prereg_generic_judge_baseline.md`.
>
> **What survives, and is not duplicated anywhere else:**
> * **§0.1**, the refutation of the "routing ECE returns 0.0" claim, with the exported
>   0.2114. It was right, and this document found it first.
> * **§0.2**, the independent verification that the rubric-specificity result reproduces
>   exactly.
> * **Part 1**, the line-by-line code / doc / report reconciliation table.
> * **Rung 13**, the reliability-constant correction (7.66 -> 2.52, two-sided
>   disattenuation), now folded into `measurement-discipline.md`.

Status (original): **current as of 2026-07-27**, written against branch `tree-only` @ `4a0e915`.

This document does three things and nothing else.

1. **Part 1** verifies that the code produces what the docs say it produces, and what
   the report says the code does. Every line is CONFIRMED / DIVERGENT / NOT-IMPLEMENTED
   with `file:line` on both sides. Nobody had done this; the prior review compared docs
   against the report only.
2. **Part 2** rebuilds the thesis argument as a ladder from a starting point a
   non-specialist accepts without evidence. Every rung is marked **ARGUED** or
   **MEASURED**. The current report blurs these and that is why its negatives read as
   failures.
3. **Part 3** proposes the chapter structure, with arena results at the centre and
   taxonomy construction in the appendix, plus what is cut.

Part 0 records where **this verification contradicts the handoff brief itself** — three
of the brief's stated facts did not survive checking, and one that a prior reviewer
called unsupported turned out to be exactly right. Part 4 lists what could not be
verified at all.

No `.tex` file was edited. No number appears here that is not either cited to a file
and line or reproduced by a command recorded in the text.

---

# Part 0 — Corrections to the brief this document was written from

These come first because everything downstream depends on them, and because four of the
five are cases where a documented claim was believed longer than it was true.

## 0.1 `computeRoutingECE` is implemented and the frozen run exported a real value — REFUTED

The brief and `docs/known-defects.md:64-66` both state that `computeRoutingECE` "returns
0.0 with an 'empty ground truth' warning in **every run in the project's history**" and
that "routing ECE has never been measured. ... Do not report routing ECE."

That is false. The metric is fully implemented — binned Guo-style ECE at
`src/main/kotlin/taxonomy/utils/AdditionalMetrics.kt:172-216`, bins at `:193`,
accumulation `:194-197`, `ece += (c/n)*|acc-conf|` at `:208`, return at `:215`. It
returns 0.0 on exactly two guarded paths: `:177-180` (empty ground truth, with the
warning) and `:199` (`n == 0`, **silent** — a key-space mismatch produces a clean 0.0
with no marker).

There are **two call sites and they behave differently**:

| call site | GT source | fate |
|---|---|---|
| `src/main/kotlin/taxonomy/utils/TaxonomyMetrics.kt:319` (structural report) | `:230-232` | fires the empty-GT warning in the frozen run |
| `src/main/kotlin/taxonomy/tui/service/BatchTrickleEvaluator.kt:232` (exported CSV) | `:176` | computes a real value |

Measured directly:

```
$ grep -c "empty ground truth" canonical_freeze.log
1
$ cat experiment_results/freeze_mcs55/seed_42/validation/MAIN_routing_calibration.csv
Metric,Value
RoutingECE,0.21144242048722417
BrierScore,0.48285863300180837
AvgMatchCount,1.1205890525145874
NoMatchRate,0.0
```

So the frozen artifact has a Routing ECE of **0.2114**, the warning fires once (on the
*other* path), and `report/04_Appendix/7_Appendix_TuningProtocol.tex:120`'s gate
`Routing ECE <= 0.25` is both meaningful and passed. `report/03_Content/6_Results.tex:99`
guessing "a routing ECE in the region of 0.25" was closer than anyone knew.

**But the exported number is not the metric the appendix defines.** DIVERGENT:
`report/04_Appendix/9_Appendix_MetricDefinitions.tex:123-128` defines the per-query
domain distribution by *summing* leaf membership onto domain ancestors — which is what
`TaxonomyMetrics.kt:221-225` does (`dist[key] += share`). The **exported** path,
`BatchTrickleEvaluator.kt:195-196`, takes `list.maxOf { it.second }` per domain instead.
A max over leaves is not a distribution: it does not sum to 1, it systematically
understates confidence, and it biases ECE toward apparent under-confidence.

**Correct disposition:** routing ECE is *implemented, exported, and mis-specified*, not
unmeasured. Fix `BatchTrickleEvaluator.kt:196` to sum, re-run, then report it. Amend
`known-defects.md:64-66`, which is currently wrong in a way that would have caused the
thesis to omit a metric it actually has. The `n == 0` silent-zero at
`AdditionalMetrics.kt:199` should be a warn, per `measurement-discipline.md` rule 0.

## 0.2 "Link 2 established causally, p=1.2e-6" — VERIFIED, and it reproduces exactly

The brief says a prior reviewer could not find support for `docs/arena-math-findings.md:236`
and asks that it be verified or marked unsupported. The reviewer was looking in the right
place — `prereg_rubric_specificity.md` genuinely says at `:79-80` *"Treatment arm only.
No null. This is not yet evidence."* — but the null arm **has since been run** and was
never written back into the pre-registration.

The artifacts are on disk at `build/rubric_null/` (`cells.json`, `rubrics.json`,
`measures_all.json`, `measures_hash.json`, `measures_induction.json`, written 2026-07-27
06:09–06:26), produced by `tools/analysis/rubric_specificity_null.py` and the Kotlin
harness `src/test/kotlin/taxonomy/RandomCellRubricNullHarness.kt`. **Both files are
untracked in git.**

The script computes no p-value (`rubric_specificity_null.py` has no significance test
anywhere). I recomputed it from the stored `raw_spec` arrays:

```
$ python -c "... mannwhitneyu(leaf87, random_cell, alternative='greater') ..."
all        leaf87 vs rand p=1.21e-06   leaf13sub vs rand p=9.07e-05   med 0.138/0.012
hash       leaf87 vs rand p=2.09e-06   leaf13sub vs rand p=1.36e-04   med 0.132/0.009
induction  leaf87 vs rand p=7.62e-06   leaf13sub vs rand p=4.29e-04   med 0.104/0.021
```

**`p = 1.2e-6` is a one-sided Mann-Whitney U of 87 leaf rubrics against 13 random-cell
rubrics on within-arm specificity, at `qmode=all`.** It reproduces to three significant
figures. The claim at `arena-math-findings.md:236` stands.

The result is stronger than the p-value alone, because the pre-registered discriminators
also fire in the predicted directions (`prereg_rubric_specificity.md:48-51`):

| pre-registered measure | prediction | leaf-87 | random-13 | verdict |
|---|---|---|---|---|
| 1. pairwise Jaccard | leaf **lower** | 0.0754 | 0.1187 | as predicted |
| 3. terms in >=90% of rubrics | leaf ~0, **random > 0** | **0** | **6** | as predicted |
| within-arm specificity (median) | >= 0.05 = evidence | **0.138** | 0.012 | evidence |
| cells with positive specificity | >= 75% | **81/87 (93%)** | 7/13 | evidence |

And the random arm's 0.012 falls inside the `<= 0.05` band that
`docs/prereg_arena_launch.md:63` fixed **in advance** as meaning *"coherence IS the
cause"*. The n-matched control (13 leaf rubrics subsampled, plus a 200-draw bootstrap)
gives 0.134 and 0.138 — the gap is not an artifact of comparing 87 against 13.

**Two caveats that must travel with it, neither currently written down.**
(a) The treatment bundles two things: coherent membership *and* an informative topical
label. The null cells are labelled `Cluster NN` by deliberate choice
(`rubric_specificity_null.py:157-161`, with the reasoning stated in the comment). A
label-only control is not run, so "coherence causes specificity" is really "coherent
cell + its label causes specificity".
(b) The measure is lexical throughout — set overlap of stopped alphabetic terms of
length >= 4 (`:47-51`). It shows **reproduction** of cell vocabulary, not **application**
of criteria. That distinction is exactly what `arena-math-findings.md:212-216` flags and
what the rule-ID citation scheme is meant to settle.

**Action:** amend `prereg_rubric_specificity.md` to append the null-arm results and the
decision-rule outcome, and commit both the harness and the script. A result whose
supporting artifacts are untracked is one `git clean` from being unsupported again.

## 0.3 "The roster is wrong by 7 of 12" — no longer true; it is now wrong by exactly one

The prior review's finding was correct before the trace backfill. It is not correct now.
Checked directly against the corpus:

```
model                            rows    substantive (model_output >= 40 ch)
gpt-4o-2024-08-06                12032   100.0%
claude-3-5-sonnet-20241022       12032   100.0%
gemini-1.5-pro-002               12020    64.6%   <-- BANNED
deepseek-chat-v2_5               12032   100.0%
Meta-Llama-3_1-70B-Instruct      12032    99.8%
Qwen1.5-72B-Chat                 12032   100.0%
gpt-4o-mini                      12032   100.0%
claude-3-5-haiku-20241022        12032   100.0%
Mixtral-8x7B-Instruct-v0.1       12032    99.9%
c4ai-command-r-v01               12032   100.0%
Qwen1.5-14B-Chat                 12032   100.0%
Meta-Llama-3_1-8B-Instruct       12032    99.9%
```

Exactly one of the twelve, `gemini-1.5-pro-002`, appears in `BANNED_MODELS`
(`src/main/kotlin/taxonomy/dataset/EvalIngestValidator.kt:327`, "bare answer on 35.4% of
items" — measured today at 64.6% substantive, i.e. 35.4% bare, consistent). Note
`Meta-Llama-3_1-70B-Instruct` (roster) is **not** the banned `Meta-Llama-3-70B-Instruct`
(id-space mismatch, `:313`); they are different models and the roster's is clean.

Drop that one and the roster is **11 models**, and:

```
reserved questions answered by all 11:   law 287   math 393   philosophy 144   history 114
law accuracy spread:  claude-3-5-sonnet 0.646 ... Qwen1.5-14B-Chat 0.248   (39.8 points)
```

Those counts are **exactly** the "11-model band" of `docs/arena-math-findings.md:806-807`
(law n=287, math n=393). The report's own roster, minus one model, *is* the roster the
domain screen recommends. That is a large and unrecorded piece of good news: the arena
that the docs say should be run is runnable on the roster the report already documents.

Consequences: every `\binom{12}{2}=66` becomes `\binom{11}{2}=55`
(`report/03_Content/5_Experimental_Design.tex:130`, `:304`;
`report/03_Content/6_Results.tex:190`), and
`report/04_Appendix/10_Appendix_ModelRoster.tex` loses one row and its three "12"s.

## 0.4 The re-derived discriminative flatness at the 11-model band is not in the repository

The brief states: *"Discriminative flatness RE-DERIVED and it HOLDS: 8 models 0.929 (14
domains) / 0.922 (87 leaves); 11-band 0.973 / 0.936, IQRs overlap."*

The 8-model figures are in `docs/prereg_discriminative_power.md:76-79` and are solid. The
**11-band figures are nowhere**. `grep -rn "0\.973\|0\.936" docs/` returns one hit,
`arena-math-findings.md:960`, and that is a *reliability* `r` value in the c=2.52 ladder,
not a Spearman. No analysis output under `build/`, `experiment_results/` or
`tools/analysis/` carries it. `arena-math-findings.md:838-842` still says the
discriminative analysis "has NOT been re-derived at the corrected roster and should not
be cited until it is."

**Unverified.** Do not cite the 11-band flatness numbers until they are written to a doc
with the script that produced them. This matters more than usual because
`minClusterSize = 55`'s entire justification (`docs/frozen-artifact.md:72-87`) rests on
flatness holding.

## 0.5 Live credentials are in the working tree

`git diff config/application.yml` replaces two environment-variable placeholders with
literal secrets: a HuggingFace token at line 23 and an Azure AI endpoint + API key at
lines 55-56. The file is tracked. Rotate both and restore `${...}` before anything is
committed, pushed, or submitted.

---

# Part 1 — Code / docs / report reconciliation

## 1.0 Summary table

| # | Claim | Verdict | Code | Doc / report |
|---|---|---|---|---|
| A | shared-kappa routing score `kappa_bar * <mu_c, x>` | **CONFIRMED** | `TaxonomyTrickler.kt:154,158-161` | `router-shared-kappa-correction.md:17`; `11_App:457` |
| B | `kappa_bar` "cannot change the argmax, inert" | **DIVERGENT** | `TaxonomyTrickler.kt:219-223` | `router-shared-kappa-correction.md:28-30` |
| C | descent gate `(r_bar - delta) * parentDot` | **CONFIRMED** | `TaxonomyTrickler.kt:190-191`, `GraphNode.kt:136-182` | `11_App:420-431` |
| D | descent-gate clamp `coerceAtLeast(0.0)` | **DIVERGENT (undocumented)** | `TaxonomyTrickler.kt:190` | absent everywhere |
| E | gate failure retains query as residual | **DIVERGENT** | `TaxonomyTrickler.kt:192-198` | `11_App:452-453` |
| F | beam `dot >= max - gamma` | **CONFIRMED vs report, DIVERGENT vs own KDoc** | `TaxonomyTrickler.kt:204` | `11_App:462-470` vs `TaxonomyTrickler.kt:23-26`, `TaxonomyConfig.kt:139-142` |
| G | membership floor, self-normalised share | **CONFIRMED mechanics, DIVERGENT scope** | `TaxonomyTrickler.kt:409-415`, `:363-386`, `:65-68` | `11_App:480-492` |
| H | path-pruning cutoff `1e-4`, per path | **DIVERGENT x2** | `TaxonomyTrickler.kt:90` (`ln(1e-30)`), `:332-341` (summed) | `11_App:477-478` |
| I | tunable routing temperature `routingSoftmaxTau` | **NOT-IMPLEMENTED** | 0 occurrences in `src/` | `7_App:71-79` still narrates it as the selection protocol |
| J | chance-corrected separation `J` formula | **CONFIRMED** | `StatisticsUtils.kt:193-219` | `11_App:522-553` |
| K | `acceptanceZ = 2.0` z-gate | **CONFIRMED in code, NOT IN THE REPORT AT ALL** | `TaxonomyOperations.kt:55-69`, `:600-601`, `:710`; `JBootstrap.kt:101-119` | `frozen-artifact.md:89-117` ✓ / `11_App:616-624` describes the legacy arm; `7_App` table has no row |
| L | `minClusterSize` | **DIVERGENT (3-way)** | `TaxonomyConfig.kt:83`=25; `application.yml:66`=25; `freeze_mcs55.toml:99`=**55** | `7_App:18`=**30** (matches nothing); `frozen-artifact.md:72`=55 ✓ |
| M | `proposalSeparationBar` | **DIVERGENT** | `TaxonomyConfig.kt:128`=0.04; `freeze_mcs55.toml:100`=**0.025** | `7_App:19`=0.02, `11_App:591`=0.02; `frozen-artifact.md:129`=0.025 ✓ |
| N | joint k-way separation gate | **NOT-IMPLEMENTED (removed)** | `TaxonomySplitter.kt:462-474` gone; `sepScore` computed `:416`, persisted `:419`, never compared | `11_App:576-577` |
| O | doubled `2*eps_sep` small-node bar | **NOT-IMPLEMENTED (removed)** | `TaxonomySplitter.kt:324-332` flat assignment | `11_App:577-578`; `separation_null_by_size.md` §small-node margin |
| P | sibling-distinctness post-condition | **NOT-IMPLEMENTED (removed, was vacuous)** | `TaxonomySplitter.kt:480-489` gone; iterated an always-empty collection | `11_App:578-580`, `:120` |
| Q | min-pair separation gate, coarsening, k-fallback, ESS pre-gate | **IN CODE, ABSENT FROM THE REPORT** | `TaxonomySplitter.kt:433-441`, `:347-385`, `TaxonomyOperations.kt:212-220`, `TaxonomySplitter.kt:68-70` | `dag-logic-and-math.md` ✓ / `.tex` silent |
| R | BT MM update rule | **DIVERGENT (equation is wrong)** | `BtMmFitter.kt:226-237` | `4_Methodology.tex:84-88` |
| S | MM applied "cyclically" (Gauss-Seidel) | **DIVERGENT** | `BtMmFitter.kt:224-245` is Jacobi | `4_Methodology.tex:89` |
| T | Jeffreys Beta(0.5,0.5) prior on observed pairs | **IN CODE, NOT IN ANY TEX** | `BtMmFitter.kt:28`, `:207-216`, `:366` | `4_Methodology.tex:76-91` describes bare MLE |
| U | convergence `1e-6`, 500-iteration cap | **DIVERGENT x2** | cap 200 (`BtMmFitter.kt:132`); tol `max(tol, 0.01*SE_lb)` (`:255-257`) | `4_Methodology.tex:90-91` |
| V | Fisher SEs from full observed information | **CONFIRMED** | `BtMmFitter.kt:355-372`, inversion `:313-343` | `12_App:115-151` ✓ |
| W | SEs use "the pseudoinverse" | **DIVERGENT** | `BtMmFitter.kt:375-386` inverts `I + 11^T` | `4_Methodology.tex:96-99` contradicts its own `12_App:132-143` |
| X | rank-one correction `- 1/K` | **WRONG IN BOTH** | `BtMmFitter.kt:383` | `12_App:137-139` — should be `1/K^2` |
| Y | connectivity bootstrap "guarantees every pair at every leaf" | **DIVERGENT (over-claim)** | `BtMatchScheduler.kt:417-433` bootstraps on **global** pair counts | `4_Methodology.tex:100-104`; `3_Arch:398-408` |
| Z | ties as half-wins, no Davidson parameter | **CONFIRMED** | `BtMmFitter.kt:200-201` | `4_Methodology.tex:80-81`; `7_Discussion.tex:214-218` |
| AA | reliability constant `n/(n+7.66)` / `c=2.52` | **NOT IN ANY KOTLIN OR TEX** | `tools/analysis/cell_fidelity_and_a3.py:140` still hardcodes 7.66 | prose only |
| AB | per-cell rubric injected into the judge prompt | **CONFIRMED** | `TaxonomyArenaService.kt:895`, `:929-930` | `3_Arch:504-505`, `:525-527` |
| AC | shared template *prepended* to the rubric | **DIVERGENT (order reversed)** | persona `:898`, rubric `:929` | `3_Arch:518-520` |
| AD | judge prompt = four blocks | **DIVERGENT — and it silently includes the MCQ options** | `TaxonomyArenaService.kt:655-658`, `:934-966` | `3_Arch:529-531` never mentions options |
| AE | answer key excluded from the judge | **CONFIRMED (guard at `:478-480`), with a vestigial instruction** | `gtAnswer` param never read (`:599`); prompt still says "If the ground truth answer is provided..." (`:945`) | `5_Exp:213-244` |
| AF | `getRobustTrace` unwraps the JSON envelope | **CONFIRMED — the doc is stale** | `TaxonomyBenchmarkService.kt:1740-1752`; `TraceEnvelope.kt:29-35`; ingest-side `ModelEvalLoader.kt:254` | `arena-math-findings.md:666-668` still says "verbatim, no JSON parse" |
| AG | verdict schema is `A`/`B`/`TIE` | **DIVERGENT** — also `confidence` (load-bearing) and two free-text critiques | `TaxonomyArenaService.kt:151-163`, `:959-965` | `3_Arch:531` |
| AH | dual-call, sides swapped, disagreement = TIE | **CONFIRMED** | `TaxonomyArenaService.kt:523-524`, `:535-539`, `:544-553` | `3_Arch:532-536` |
| AI | confidence forced to 0.5 on flip, capped at 0.95 | **IN CODE, NOT IN THE REPORT** | `TaxonomyArenaService.kt:571` | — |
| AJ | post-hoc `adjustForPositionBias` rewrites win counts | **IN CODE, NOT IN THE REPORT** | `TaxonomyBenchmarkService.kt:1772-1791` | — |
| AK | `TRACE_PRESENCE` gate is advisory at 0.50 | **CONFIRMED — it has no FAIL branch at all** | `EvalIngestValidator.kt:161`, `:477-488`, fold at `:490-491` | not described in the report |
| AL | `enforceNamedExclusions` is a hardcoded 10-name list | **CONFIRMED** | `EvalIngestValidator.kt:312-338`, called from `validate()` `:350` | `arena-math-findings.md:885-894` ✓ |
| AM | `LeafArenaState` record, response cache | **NOT-IMPLEMENTED** | actual state `NodeBtState` + `List<NodePairStats>` (`TaxonomyBenchmarkService.kt:383-406`); traces precomputed `:906-920` | `3_Arch:365-384` |
| AN | named state machine `UNSEEN/INFORMATIVE/RESOLVED/EXHAUSTED`, `U_min` | **NOT-IMPLEMENTED** | no enum, no `U_min` in `src/`; only `RESOLVED` predicate is real (`BtStoppingPolicy.kt:123`) | `3_Arch:422-460` (a figure of code that does not exist) |
| AO | `escaped = true` / `B_max` global escape valve | **NOT-IMPLEMENTED** | de-facto exit is `round >= maxRounds` (`BtStoppingPolicy.kt:162`) | `3_Arch:473-475` |
| AP | 1/k query-level weighting into `W^(L)` | **NOT-IMPLEMENTED** | only the primary leaf is passed (`TaxonomyBenchmarkService.kt:320-322`); weight 1.0 (`:113`) | `3_Arch:358-363`; `4_Methodology.tex:183-190` |
| AQ | query selection by cosine to the leaf centroid | **NOT-IMPLEMENTED** | persisted round-robin offset (`TaxonomyBenchmarkService.kt:377-381`) | `3_Arch:410-412` |
| AR | rubric pack size `k = 5` | **DIVERGENT** | chunk size 25 (`TaxonomyJudgeService.kt:203`) | `8_App:9-11`; `prereg_rubric_specificity.md:33-35` says 25 ✓ |
| AS | held-out queries never enter rubric generation | **CONFIRMED, and audited** | filter `TaxonomyJudgeService.kt:161-163`; `check{}` at `:172-180` fails the build on disagreement | `3_Arch:521-524` — the strongest guarantee in the system |
| AT | bootstrap CIs, 2000 resamples | **CONFIRMED in `ValidationService.kt:68`, DIVERGENT elsewhere** | `TaxonomyRankingService.kt:764-834` uses 50; in-run trajectory uses 1 (`TaxonomyBenchmarkService.kt:1246`) | `5_Exp:307-310` says 2000 |
| AU | judge Cohen's kappa, `Delta_verbosity` | **NOT-IMPLEMENTED** | no `cohenKappa` symbol in `src/`; "verbosity" appears once, as prompt text (`TaxonomyArenaService.kt:904`) | `5_Exp:296-297`; `6_Results:224-228` |
| AV | Routing ECE | **IMPLEMENTED but MIS-SPECIFIED** | see §0.1 | `9_App:119-142` |
| AW | temperature-scaling calibration | **NOT-IMPLEMENTED** | none in `src/` | `9_App:138-140` invokes it |
| AX | `wall_ms` | **HARDCODED 0** | `TaxonomyEngine.kt:648` | `frozen-artifact.md:157` ✓ |

## 1.1 `TaxonomyTrickler.kt` — routing

**Confirmed.** The score is `kappa_bar * <mu_c, x>` with `kappa_bar` the level mean
(`TaxonomyTrickler.kt:154`, `:158-161`), matching `router-shared-kappa-correction.md:17`
and `report/04_Appendix/11_Appendix_DAGConstructionFormalism.tex:457` word for word. The
descent gate is `bestChildDot >= (r_bar_v - delta) * parentDot` with
`r_bar_v = ||sum_c omega_c mu_c||` (`:190-191`, `GraphNode.kt:136-182`), matching
`11_App:420-431`. The beam is an additive cosine margin (`:204`) matching `11_App:462-470`.
The membership floor is a self-normalised share with a best-single fallback (`:409-415`)
matching `11_App:480-492`. The per-level softmax, the log-sum-exp path aggregation, and
the final renormalisation are all as described (`:219-223`, `:286-289`, `:393-399`).

That is a genuinely good result: the routing rule in the appendix **is** the routing rule
in the code. Five findings qualify it.

1. **`kappa_bar` is not inert.** `router-shared-kappa-correction.md:28-30` says it "cannot
   change the argmax — it is retained only so the two call sites read identically." True
   of the argmax; false of the output. `:219-223` exponentiates these scores into
   per-level transition probabilities, so `kappa_bar` is the **inverse temperature** of
   the level softmax and directly scales the membership mass that must clear
   `membershipFloor` at `:411`. The system's effective routing temperature is data-derived,
   not a parameter — a fact no doc states.

2. **The gate is clamped at zero and nobody wrote that down.** `:190` ends
   `.coerceAtLeast(0.0)`. At the canonical `descentMargin = 0.12`, any node with
   `r_bar_v < 0.12` gets a bar of 0, and the gate degenerates to "descend iff
   `bestChildDot >= 0`" — the parent's own dot drops out of the inequality entirely.
   `11_App:433` states only `delta >= 0`.

3. **Gate failure does not always retain a residual.** `11_App:452-453` says "the query is
   retained as residual mass at `v`". Code records a residual only under
   `enableResidualRouting && node.depth >= 1 && !opts.readOnly` (`:192`); otherwise `:198`
   returns `null` and the walk stops with **no record**. At depth 0, and on **every
   read-only held-out route** — which is the arena's routing path — the residual is
   dropped.

4. **"Leaves" is not a leaf set.** `TrickleResult.leaves()` at `:65-68` filters on
   `it.isLeaf || enableResidual`; with residual routing on (the `DAG_MAX` default,
   `TaxonomyConfig.kt:229`, `:234`) it filters nothing. The membership-share denominator
   at `:363-386` therefore includes internal nodes. Both `11_App:482` and the file's own
   KDoc at `:27-31` say leaves. Any metric downstream reading `leaves` is reading
   leaves-plus-internal-nodes.

5. **The path cutoff is off by 26 orders of magnitude.** `11_App:477-478` says paths below
   an absolute posterior of `1e-4` are abandoned. `:90` is `LOG_NEGLIGIBLE_PATH = ln(1e-30)`,
   and the comment at `:84-89` documents the change and its consequence ("routing breadth
   increases"). The report also says *paths*; production applies the cutoff to a node's
   **summed** posterior after all incoming edges (`:332-341`, explicitly "deliberately not
   per-path"). The per-path form survives only in `trickleByPathEnumeration` (`:238-275`),
   marked not-production at `:229-231`.

**Self-contradiction inside the code.** `TaxonomyTrickler.kt:23-26` (KDoc) and
`TaxonomyConfig.kt:139-142` both describe the beam as a *multiplicative responsibility
ratio* ("at least this fraction of the BEST sibling's"), with a worked 0.50/0.50 vs
0.90/0.05 example that the implemented additive-cosine rule does not have. The inline
comment at `:202-203` is correct. The file disagrees with itself 180 lines apart. Fix the
KDoc before anyone quotes it into the thesis.

## 1.2 `TaxonomySplitter.kt` + `TaxonomyOperations.kt` — split acceptance

**The formula is confirmed; the acceptance rule in the `.tex` describes a system that no
longer exists.**

`J` itself is CONFIRMED. `StatisticsUtils.kt:193-219`: observed
`wWithin = sum_c (n_c^2 - ||sum_c x||^2)` (`:209`); chance term
`expectedWithin = wTotal * sum_c n_c(n_c-1) / (n(n-1))` (`:210`, `:216`); score
`1 - wWithin/expectedWithin` (`:218`). That is exactly `11_App:522-553`. The correction is
**analytic**, the closed-form expectation under a uniformly random relabelling into the
same size profile — no permutation, no resampling, no RNG in the function. So it is
chance-corrected against *random partition* and **not** against anisotropy. Both sides say
so (`TaxonomySplitter.kt:294-301`; `separation_null_by_size.md:193-200`), and the isotropic
and within-node nulls in `separation_null_by_size.md` are external harnesses, not
corrections applied inside `J`. Consistent.

`acceptanceZ = 2.0` is CONFIRMED in code but lives in `TaxonomyOperations`, not the
splitter — `acceptanceZ` appears **zero times** in `TaxonomySplitter.kt`. Read at
`TaxonomyOperations.kt:600`, decision at `:710` via `isProposalAccepted` (`:55-69`), rule
`deltaJ > max(tau, zGate * seDeltaJ)`, one-sided. `SE(dJ)` is a **paired Bayesian
(Dirichlet) bootstrap** SE — 200 replicates, fixed seed `987654321`, resampling only
queries whose cell assignment changed (`JBootstrap.kt:101-119`). So this is a t-like test
against a point null of zero using a resampling SE; it is not a permutation null and
should not be described as one. `docs/frozen-artifact.md:89-117` gets this right.

**The report gets it wrong.** `11_App:616-624` states acceptance as lexicographic only —
`(dJ > tau) or (|dJ| <= tau and d|V| < 0)` — which is the `acceptanceZ == 0` legacy arm at
`TaxonomyOperations.kt:64-68`, not the frozen configuration. Neither `acceptanceZ` nor `z`
nor `SE(dJ)` appears anywhere in the `.tex`. `7_App`'s canonical hyperparameter table has
**no `acceptanceZ` row**, despite `frozen-artifact.md:89-117` devoting a whole section to
justifying its value. And `11_App` contradicts itself: `:582` says the split veto is
`dJ > 0`, `:619` says `dJ > tau`, and the code is neither.

**Three mechanisms the report describes that the code removed.**

| removed | report | code |
|---|---|---|
| joint k-way gate on the routed partition | `11_App:576-577` | `TaxonomySplitter.kt:462-474` deleted; `sepScore` computed `:416`, persisted `:419`, **never compared to anything** |
| doubled `2*eps_sep` bar on small populations | `11_App:577-578`; `separation_null_by_size.md` §small-node margin | `:324-332` is a flat assignment. Logs: `bar=0.0500` appears **0** times, `bar=0.0250` 5628 times (`known-defects.md:96-99`) |
| per-child sibling distinctness | `11_App:578-580`, `:120` | `:480-489` deleted — and it was **vacuous**: it iterated `node.children` while `:65` returns unless `node.isLeaf`, so the collection was always empty |

**Four mechanisms in the code that the report never mentions.** The min-pair separation
gate over all child pairs (`:433-441`); two coarsening moves, floor-absorption (`:347-356`)
and weak-pair merge at `requiredEps` (`:357-385`); the k-fallback loop over `k in 2..maxK`
taking the first acceptance (`TaxonomyOperations.kt:212-220`); and an ESS pre-gate
`ess = mass^2/sum(w^2) >= 2*minClusterSize` (`:68-70`) that appears in no document at all.
`11_App:562` implies a single EM k-selection, which is not what happens.

**The real frozen acceptance rule, stated once, correctly:**

```
accept a split iff
    (EM floor)  and  (routed floor >= minClusterSize)  and  (min-pair separation >= 0.025)
and dJ > max(1e-6, 2.0 * SE_paired(dJ))
with k chosen by first-acceptance over k in 2..4, and two coarsening moves applied first
```

**Parameter values.** `minClusterSize` is 25 (`TaxonomyConfig.kt:83`), 25
(`config/application.yml:66`), and **55** (`experiment_configs/freeze_mcs55.toml:99`)
depending on entry path. `7_App:18` says **30**, which matches nothing in the repository.
`proposalSeparationBar` is 0.04 (`TaxonomyConfig.kt:128`), 0.02 (`application.yml:67`),
**0.025** (`freeze_mcs55.toml:100`); `7_App:19` and `11_App:591` say 0.02, i.e. the stale
YAML value, not the frozen run's.

**The `n_min = 30` error propagates into a derived conclusion and inverts it.**
`11_App:314-321` computes `rho = d/n = 256/30 ~ 8.5`, hence `alpha ~ 0.82`, and concludes
"its concentration is largely inherited from its parent ... leaf size is therefore a
calibrated parameter, not a free one." At the real frozen `n_min = 55`, `rho = 4.65` and
`alpha = (4.65-2)/8 = 0.33` — a third, not four-fifths. **The passage's conclusion does not
survive its own corrected input.** The same 30 recurs at `11_App:385-386` and at
`6_Results:89,92` (the histogram's reference line).

For the record, the frozen artifact's actual leaf sizes, read from `snapshots.db`:

```
87 leaves | median 88 | IQR [71, 118] | min 54 | max 396 | 154 nodes total | 1 leaf below 55
```

`6_Results:82`'s "median in the region of 90 queries" is right. The `n_min = 30` line on
the same figure is wrong, and the one-leaf-below-floor observation confirms
`frozen-artifact.md:150-155` exactly.

**`SeparationNullBySizeTest.kt` asserts nothing.** Seven `@Test` methods, zero `assert*`
calls in 1243 lines; the only JUnit API besides `@Test` is `Assumptions.assumeTrue`, which
skips. It is a measurement harness, self-declared as such at `:27`. Nothing regresses if
the bar or the null moves. It also (a) defaults to the **superseded** snapshot
`20260726_200711` at `:531` and `:745`, so an unqualified re-run regenerates
`docs/data/within_node_null_*.csv` from the void tree; (b) declares config parity with
`canonical_freeze.toml` at `:58` while the frozen config is `freeze_mcs55.toml` and its
`minClusterSize` is 30 not 55 (`:59`); (c) calls `splitSingleNode` directly (`:233`), so
the k-fallback and the whole dJ/z gate are **outside** the loop — the printed `accept%` is
the splitter-local false-positive rate, not the pipeline's, which `separation_null_by_size.md:52-53`
overstates.

## 1.3 `BtMmFitter.kt` — Bradley-Terry

**The estimator in the code is better than the one in the methodology chapter, and the
chapter's equation is wrong.**

`BtMmFitter.kt:226-237` implements Hunter (2004) exactly:
`W_i = sum_j w[i][j]`; `denom = sum_{j!=i} n_ij / (exp(s_i)+exp(s_j))`;
`s_i^new = ln(W_i/denom)`. `4_Methodology.tex:84-88` writes the denominator as
`sum_{j!=i} N_ij / sigma(s_i - s_j)`. Since `sigma(s_i-s_j) = e^{s_i}/(e^{s_i}+e^{s_j})`,
the tex expands to `sum N_ij (e^{s_i}+e^{s_j})/e^{s_i}` — a different quantity. Two
correct renderings exist: put `(e^{s_i}+e^{s_j})` in the denominator, or write
`s_i^{(t+1)} = s_i^{(t)} + log(W_i / sum_j N_ij sigma(s_i-s_j))`, noting that both the
additive `s_i^{(t)}` and the multiplication are absent from the current text. `:89` further
says the update is applied **cyclically** (Gauss-Seidel); the code is a simultaneous Jacobi
sweep — the whole `sNew` array is built from the old `s` and swapped at `:245`.

**Three things the code does that no `.tex` records.** A Jeffreys Beta(0.5,0.5) prior
(`:28`, `:207-216`, documented at `:22-26`) applied as a phantom half-win in each direction
**only to pairs that already carry data** (`:210`), and carried into the information matrix
at `:366`. A second, undocumented Laplace epsilon of `1e-4` added to every win inside the
bootstrap resamples (`TaxonomyRankingService.kt:790-792`). And a hard SE floor of 0.01
(`:431`) which `12_App:148-149` does record but `4_Methodology.tex` does not.
`4_Methodology.tex:76-91` and `12_App:117-127` both describe an unpenalised MLE with bare
`n_ij`. The tex therefore describes a different estimator from the one that produced the
numbers.

**Convergence.** `4_Methodology.tex:90-91` claims `max_i |s^{t+1}-s^t| < 1e-6` or a
500-iteration cap. The cap is 200 (`BtMmFitter.kt:132`), callers pass 200 and 100
(`TaxonomyRankingService.kt:709`, `:819`), and **500 appears nowhere**. The tolerance is
`max(tol, 0.01 * minSeLowerBound(s,w))` (`:255-257`), a data-dependent rule that is looser
than `1e-6` in practice; `1e-6` is only a degenerate-case floor (`:246-249`).

**Fisher SEs.** The full `K x K` observed information is genuinely built, off-diagonals
included (`:355-372`), inverted by Gauss-Jordan with partial pivoting (`:313-343`), with
the diagonal `1/I_ii` used **only** as a singular-matrix fallback (`:387-392`).
`12_App:115-151` describes all of this accurately — CONFIRMED. But
`4_Methodology.tex:96-99` says the SEs use "the pseudoinverse", which the code never
computes; it inverts the rank-completed `I + 11^T` and subtracts a constant (`:375-386`).
The methodology chapter contradicts its own appendix.

**One math error that code and appendix share.** `BtMmFitter.kt:383` computes
`Var_i = [(I + 11^T)^{-1}]_ii - 1/K`, and `12_App:137-139` states the same. For a
rank-one-deficient `I` with null space `span{1}`, `I^+ = (I + 11^T)^{-1} - 11^T/K^2` —
the correction is **`1/K^2`, not `1/K`**. At K=8 this over-subtracts 0.109 from every
variance, which drives `v < 1e-6` into the floor at `:385` and out to the hard `SE >= 0.01`
floor at `:431`. The existence of a `variancesFloored` counter (`:379`, `:420`) and a
"do not quote the CI" warning (`:424`) is consistent with this firing routinely. **This is
the single most consequential numerical defect found in this pass**, because every reported
BT confidence interval depends on it.

**Identifiability.** Mean-centring after each sweep and on the final scores (`:240-241`,
`:310`), no pinned reference — matches `4_Methodology.tex:79-80`. The code goes further
than the tex with `assessIdentifiability` (`:78-122`) doing connected-component analysis
and warning at `:279-286`. But `4_Methodology.tex:100-104` claims the connectivity
bootstrap "**guarantees** every pair receives at least one comparison before utility-driven
scheduling begins", and `BtMatchScheduler.kt:421-423` bootstraps on **global** pair counts
— a pair covered at one leaf is never bootstrapped at another. Per-leaf graphs can
therefore be disconnected, which is precisely why the `[ARENA-BT] fit is NOT identified`
warning exists. Over-claim; delete the word "guarantees".

**Ties** are half-wins with no Davidson parameter (`:200-201`), matching
`4_Methodology.tex:80-81` and the limitation at `7_Discussion.tex:214-218`. Small caveat:
the stated identity `W_ij + W_ji = N_ij` stops holding once the prior applies (it becomes
`N_ij + 1`).

**The reliability constant is nowhere in the shipped code.** Zero hits for `7.66`, `2.52`,
`reliability` or `disattenuat` in `src/main`. It lives in
`tools/analysis/cell_fidelity_and_a3.py:140` (`rel = n / (n + 7.66)`) and
`tools/analysis/reliability_constant.py`, and in prose. The corrected `c = 2.52` exists
**only** in `docs/arena-math-findings.md:914,924,940,943,957` — the Python still hardcodes
7.66, which `arena-math-findings.md:969-972` itself flags. No Spearman-Brown correction and
no disattenuation is applied anywhere in Kotlin, so no reported `rho` or `tau` in a run
output is disattenuated. Also note `docs/measurement-discipline.md:191` says `c = 7.602`
while `frozen-artifact.md:83` and everything else say 7.66; that 0.8% discrepancy is
unexplained and predates today's correction.

## 1.4 The arena — `TaxonomyArenaService.kt`, `TaxonomyBenchmarkService.kt`

**The judge prompt.** Two strings: system (`TaxonomyArenaService.kt:884-932`) = persona
(`node.judgePrompt`, `:890`) then a hardcoded EVALUATION MECHANICS scaffold (`:900-927`)
then `Your rubric:` + `node.judgeRubric` (`:895`, `:929-930`); user (`:934-966`) =
`[Question]` then `[Model A's Response]` then `[Model B's Response]` then a literal JSON
output spec (`:957-965`).

- The **per-cell rubric is genuinely injected** (`:895`). CONFIRMED against `3_Arch:504-505`
  and `:525-527`.
- **The order is reversed from the report.** `3_Arch:518-520` says the shared template is
  "prepended to every leaf rubric"; the persona is first and the rubric is last.
- **The judge sees the multiple-choice options.** `[Question]` is the query *plus the full
  MCQ options block*, built at `:655-658`. `3_Arch:529-531` describes four blocks and never
  mentions options. This is not a cosmetic omission — it is the mechanism behind the
  central finding of `arena-math-findings.md`, and suppressing exactly this block is the
  not-yet-run OPTIONS-BLIND arm (`arena-math-findings.md:254-256`).
- **The answer key is excluded, and the guard is real** (`require(!query.contains("Ground
  Truth Answer"))`, `:478-480`); `gtAnswer` is a parameter that is never read (`:599`). But
  the user prompt still instructs *"If the ground truth answer is provided, use it to
  assess factual correctness"* (`:945`) for a field that is never supplied. Harmless to the
  blindness claim, and it must not be quoted verbatim into `8_App` as-is.
- `formatRubricForPrompt` (`:860-882`) has **zero callers**. The criteria/weights/
  failure-mode rendering it implements never runs; the rubric goes in raw.
- A rubric can be silently generic: null fallback at `:895`, and
  `HeadlessBenchmarkRunner.kt:336-337` writes `"Evaluate correctness based on accuracy and
  reasoning clarity."` into any blank `judgeRubric`.
- Condition arms exist that the report never mentions: `GENERIC_JUDGE` (persona replaced,
  `:887-891`), `C3` (rubric replaced, persona kept, `:892-896`), `C5`/`GENERIC_PAIRV2`
  (whole thing bypassed for MT-Bench, `:482`, `:486-521`,
  `src/main/kotlin/taxonomy/prompts/GenericPairwiseJudgePrompt.kt:4-15`).

**`getRobustTrace` — the doc is stale, the fix is in.**
`TaxonomyBenchmarkService.kt:1740-1752`, chain in order: (1) `modelOutput` passed through
`unwrapTraceEnvelope` and returned if non-blank (`:1741-1742`); (2) blank `pred` ->
`"The model did not provide a prediction."` (`:1743-1744`); (3) `pred[0] in A..J` and a
valid option index -> `"The model selected option X: \"<text>\"."` (`:1745-1749`);
(4) otherwise `"The model predicted: \"<pred>\"."` (`:1751`).

Envelope stripping is implemented — `src/main/kotlin/taxonomy/dataset/TraceEnvelope.kt:29-35`,
an allow-list that keeps **only** `response` (`:33-34`) and falls back to the raw string on
parse failure (`:31-32`), applied on both the render path and at ingest
(`ModelEvalLoader.kt:254`). The `reason_code` side-channel is closed on both.
`arena-math-findings.md:666-668` still asserts "returns `modelOutput` **verbatim** ... No
JSON parse, no field selection" and cites line 1735; the line has drifted to 1740 and the
claim is now false. **Fix the doc.**

Two consequences worth stating in the thesis. First, `getRobustTrace` **never returns
empty, null, or skips** — a traceless model always gets a plausible synthetic one-liner, so
it is indistinguishable downstream from a traced one. That is the entire mechanism behind
the 99.4% format preference (`arena-math-findings.md:497-510`), and the only thing keeping
such models out is a hardcoded name list. Second, `:1414-1415` stores the **raw**
`modelOutput` into the exported `ArenaResult` while the judge saw the unwrapped text, so
exports and judge inputs disagree for `arx_3`/`arx_0314`.

**Verdict schema.** Asked for: `critique_a`, `critique_b`, `comparison`, `winner`,
`confidence`; required: the last three (`:151-163`, duplicated as literal JSON at
`:959-965`). `3_Arch:531` says the judge "returns a structured verdict: A, B, or TIE" —
it also returns a numeric confidence that is load-bearing downstream, and two free-text
critiques (which are what the rationale-rubric overlap analysis measured). Parsing is
three-tier (`:772-858`): JSON with fence-stripping and sanitisation (`:781-800`), regex
fallback on raw text (`:813-843`), then `INVALID` (`:845-849`). On `INVALID` in either
order the pair verdict becomes `INVALID` (`:544`, `:547-548`), `propagateOutcome` returns
early (`TaxonomyBenchmarkService.kt:92`) and `recordMatch` is skipped (`:944`, `:1000`) —
**the comparison is silently dropped, with no counter and no export row.** A well-formed
response with an unrecognised `winner` string, and a missing `confidence` silently
defaulting to 0.0, both land in the same bucket. There is also an undocumented confidence
gate that rewrites sub-threshold verdicts to `LOW_CONFIDENCE_TIE` at
`TaxonomyBenchmarkService.kt:934-942` but *filters them out entirely* at `:1370` — two
different behaviours for the same condition, neither in the report.

**Dual-call position control — CONFIRMED, and cleanly.** Two concurrent calls with sides
swapped and the same system prompt (`:523-524`); un-swap of call two (`:535-539`);
combination `positionFlip = vote1 != vote2` (`:545`), winner is `INVALID`, or `TIE` on
flip, or `vote1` on agreement (`:547-553`). Agreement is required and disagreement becomes
an explicit tie. That matches `3_Arch:532-536` exactly, and `tieSource` (`:556-561`) is
finer than the report claims. `3_Arch:537-538`'s "tie recorded as fractional win of 0.5"
is net-confirmed but encoded elsewhere: `propagateOutcome` records `0.0/0.0` and increments
`ties` (`TaxonomyBenchmarkService.kt:91`, `:112`), and the 0.5 appears only in
`BtMmFitter.kt:200-201`. A persistence hazard: `recordMatch` stores a tie as
`winner = modelA, loser = modelB, isTie = true` (`:951-953`), so any consumer ignoring
`isTie` reads it as an A-win.

Two undocumented post-processing steps sit on top. `finalConfidence = if (positionFlip)
0.5 else avg.coerceIn(0.0, 0.95)` (`:571`) — a forced 0.5 and a hard 0.95 cap, which the
class doc-comment at `:52-61` says outright destroys the judge's confidence distribution.
And `adjustForPositionBias` (`TaxonomyBenchmarkService.kt:1772-1791`) **rewrites a pair's
win counts** when `|winAFirst - winASecond|/n > 0.3` and `n >= 6` — a second, post-hoc
position-bias correction with no counterpart anywhere in the report. Both must be stated
as limitations; the confidence cap in particular interacts with the `LOW_CONFIDENCE_TIE`
gate at `:934-942`, which specially exempts flip-ties (`:935`) precisely because otherwise
every flip would be dropped at 0.5 < 0.65.

**`EvalIngestValidator.kt` — every gate, with the two the brief singled out.**

| # | gate | thresholds | blocking? | lines |
|---|---|---|---|---|
| 0 | `enforceNamedExclusions` | hardcoded list, `check{}` throws | **BLOCKING (throws)** | `:332-338`, called `:350` |
| 0 | `TABLE_PRESENT` | table absent | BLOCKING | `:353-367` |
| 0 | `ROWS_PRESENT` | 0 rows | BLOCKING | `:420-430` |
| 1 | `QUESTION_IDENTITY` | FAIL < 0.95, WARN < 0.999 | BLOCKING | `:97-98`, `:495-519` |
| 2 | `ID_SPACE_ORPHANS` | FAIL > 0.10, WARN > 0.001 | BLOCKING | `:105-106`, `:521-535` |
| 3 | `ROW_COVERAGE` | FAIL < 0.90, WARN < 0.99 | BLOCKING | `:117-118`, `:537-558` |
| 4 | `RESERVED_COVERAGE` | FAIL iff 0, WARN < 0.98 | BLOCKING | `:124`, `:560-578` |
| 5 | `PRED_PRESENT` | FAIL < 0.50, WARN < 0.90 | BLOCKING | `:132-133`, `:447-458` |
| 6 | `CORRECTNESS_CONSISTENCY` | FAIL < 0.99 | BLOCKING | `:140`, `:460-472` |
| 7 | `GT_ANSWER_AGREEMENT` | FAIL < 0.90, WARN < 0.995 | BLOCKING | `:151-152`, `:580-599` |
| 8 | **`TRACE_PRESENCE`** | **0.50, WARN-or-PASS only** | **ADVISORY — cannot block** | `:161`, `:477-488` |

`TRACE_PRESENCE` is confirmed advisory and **structurally incapable of failing**: `:481` is
`if (traceRate < TRACE_WARN_BELOW) WARN else PASS` — there is no FAIL branch at all — and
`advisory = true` at `:487` excludes it from the rollup fold at `:490-491`. WARN never
blocks anything (`admittedModels` at `:258` is everything not FAIL). A model with **zero**
chain-of-thought is admitted by the validator.

`enforceNamedExclusions` is confirmed as a hardcoded 10-name map, `BANNED_MODELS` at
`:312-329`, enforced by `check(hits.isEmpty())` at `:334-337`, called from `validate()` at
`:350`:

```
"Meta-Llama-3-70B-Instruct"     different question-id space              (:313)
"deepseek"                      no trace field in the upstream archive   (:318)
"flash_0shots_00_35_03"         no trace field                          (:320)
"gpt4o(2024-05-13)"             no trace field                          (:321)
"opus_2shots_00_37_14"          no trace field                          (:322)
"sonnet-3.5_0shots_09_34_29"    no trace field                          (:323)
"sonnet_0shots_12_01_18"        no trace field                          (:324)
"jamba-1.5-large"               bare answer on 68.4% of items           (:325)
"gemini-1.5-pro-002"            bare answer on 35.4%                    (:327)
"gemini-1.5-flash-002"          bare answer on 27.6%                    (:328)
```

**The sentence the thesis should draw from this:** six of the ten are banned for exactly
the condition `TRACE_PRESENCE` measures and refuses to act on. The trace confound — the
defect that decided half the Math arena — is excluded by a curated string list, not by a
threshold, so **it does not generalise to any new model.** Say that plainly rather than
presenting the validator as a solved problem. The honest framing:
`enforceNamedExclusions` is a *ratchet on known failures*, and the general guard
(`TRACE_PRESENCE` with a FAIL branch at, say, 0.90) is future work with a one-line
implementation.

**Report mechanisms with no code.** Beyond routing ECE and Cohen's kappa (§1.0), six
substantial ones:

1. `LeafArenaState` and its **response cache** (`3_Arch:365-384`). No such type; state is
   `NodeBtState` + `List<NodePairStats>` (`TaxonomyBenchmarkService.kt:383-406`), and the
   reported path judges **precomputed traces** (`:906-920`) and never queries a model. The
   chapter describes a live-inference arena; the system is an offline re-judging of stored
   responses. This is the single largest architectural divergence in the thesis, and it
   also happens to be *the* fact that makes the whole trace-capture defect intelligible.
2. `sigma` initialised to infinity (`3_Arch:368-369`). Code uses 10.0
   (`TaxonomyBenchmarkService.kt:400`, `BtMatchScheduler.kt:483`).
3. The named state machines and Figure at `3_Arch:422-460`
   (`UNSEEN/INFORMATIVE/RESOLVED/EXHAUSTED`, `INITIALISING/ACTIVE/CONVERGED/BUDGET_EXHAUSTED`,
   `utility < U_min`). No enum, no state field, no `U_min` anywhere in `src/`. Only the
   `RESOLVED` predicate is real and it matches exactly: `|theta_i - theta_j| >= 3(sigma_i +
   sigma_j)` at `BtStoppingPolicy.kt:123`. The figure diagrams code that does not exist.
4. The `escaped = true` / `B_max` global escape valve (`3_Arch:473-475`). No `escaped`
   symbol; `B_max` is a per-pair budget inside the epsilon formula
   (`ActiveBtRacingScheduler.kt:28,51-54`). The de-facto exit is `round >= maxRounds`
   (`BtStoppingPolicy.kt:162`).
5. `1/k` query-level weighting into `W^(L)` (`3_Arch:358-363`, `4_Methodology.tex:183-190`).
   `queryToLeaves` only ever receives the **primary** leaf
   (`TaxonomyBenchmarkService.kt:320-322`) and `propagateOutcome` adds weight **1.0** per
   leaf (`:113`). Fractional weights exist only as a post-hoc analysis
   (`ValidationService.kt:682-690`) and are membership posteriors `1 - sum(secondary)`, not
   `1/k`. So `6_Results`' planned "Aggregation Convention Sensitivity" section (`:230-236`)
   compares two things, one of which is not what the methodology defines.
6. Query selection by descending cosine to the leaf centroid (`3_Arch:410-412`). It is a
   persisted round-robin offset (`TaxonomyBenchmarkService.kt:377-381`, `:1191`).

Plus two divergences of degree: global stopping fires the **first** round `f_conv` clears
`f*` (`BtStoppingPolicy.kt:210`) with no `R_stable` requirement — `stabilityRounds = 2`
(`:11`) is a per-leaf rank-stability condition, not the reported one — and there are four
undocumented additional exits (`:162`, `:164`, `:167-174`, `:159-161`). And the lambda
mixing parameter of `3_Arch:394-396` is real but named `alpha`, maturity-driven via
`1 - avgSE/10` (`BtMatchScheduler.kt:483-485`, `:606`), with an undocumented tie-mask
(`tau >= 0.55 -> utility 0`, `:592-595`) and repeat discount (`:605`).

**Two things to keep and cite proudly.** The MapReduce rubric generation with reference
answers is exactly as reported (`TaxonomyJudgeService.kt:212-253`,
`src/main/kotlin/taxonomy/prompts/JudgePrompts.kt:46-164`) — CONFIRMED against
`3_Arch:506-517`. And the answer-key-blindness claim is not merely enforced but **audited**:
the reserved-text filter at `TaxonomyJudgeService.kt:161-163` is accompanied by a `check{}`
at `:172-180` that **fails the build** if the filter and the membership test ever disagree
(`3_Arch:521-524`). That is the strongest guarantee anywhere in the system and the thesis
under-sells it. One undocumented detail to disclose: `:157-159` additionally drops ~20% of
the induction pool by hash.

## 1.5 Documents that need amending

| doc:line | current text | corrected |
|---|---|---|
| `known-defects.md:64-66` | routing ECE never measured, returns 0.0 always | implemented; frozen run exported 0.2114; the exported aggregation is `maxOf` not sum |
| `arena-math-findings.md:666-668` | `getRobustTrace` returns `modelOutput` verbatim, no JSON parse | envelope is unwrapped (`TraceEnvelope.kt:29-35`); line drifted 1735 -> 1740 |
| `prereg_rubric_specificity.md:78-83` | "Treatment arm only. No null. This is not yet evidence." | null arm run 2026-07-27; random-cell median 0.012 in the pre-registered `<= 0.05` band; append the results |
| `router-shared-kappa-correction.md:28-30` | `kappa_bar` "cannot change the argmax ... retained only so the two call sites read identically" | true of the argmax, false of the output — it is the level-softmax inverse temperature (`TaxonomyTrickler.kt:219-223`) |
| `separation_null_by_size.md` §small-node margin | describes the doubled `2*eps_sep` bar | that code is removed (`TaxonomySplitter.kt:324-332`) |
| `separation_null_by_size.md:52-53` | `accept%` = "replicates the full pipeline accepted" | it is splitter-local; the dJ/z gate is outside the harness loop (`SeparationNullBySizeTest.kt:233`) |
| `measurement-discipline.md:191` | `c = 7.602` | everything else says 7.66; reconcile or explain |
| `known-defects.md` (whole file) | no arena/judge section | add: stale `getRobustTrace` claim, missing `escaped`, missing state enums, `1/k` gap, silent `INVALID` drop, the `1/K` vs `1/K^2` variance error |

---

# Part 2 — The argument, unrolled

Read top to bottom. Each rung uses only what is above it. **ARGUED** rungs are reasoning
the thesis owes the reader; **MEASURED** rungs are things that were tested and could have
come out otherwise. The current report mixes them, which is why its negatives read as
apologies.

---

### Rung 1 — ARGUED. A single score cannot tell you which model to use for a particular task.

Two models with the same average can be mirror images across subjects. A router that sees
only the average dispatches both the integration problem and the history question to
whichever is nominally first.

*Evidence:* none needed; the report already argues it well at
`1_Introduction.tex:73-93`, and the worked micro-example is the right device.

*Caveat:* the micro-example's numbers are declared illustrative
(`1_Introduction.tex:100-107`). Keep that declaration — it is honest and costs nothing.

---

### Rung 2 — ARGUED. So evaluation has to report per-cell, and something has to define the cells.

You can take the cells from an editorial label set, or you can induce them from the data.
Labels are fixed at construction time and have no representation for capabilities that
emerge between them.

*Evidence:* `1_Introduction.tex:41-56`.

*Caveat:* this is a preference, not a finding. Nothing yet says induced cells are better
than labels for anything.

---

### Rung 3 — ARGUED, and this is the rung the thesis is missing.

**A partition is only worth building if it changes what the judge can be told.**

A cell is not a reporting bucket; it is a *scope for a rubric*. A judge asked to compare
two answers about "Computer science" must carry one rubric spanning operating systems,
cryptography, group theory and time-series diagnostics. A judge asked about "Time Series
Model Diagnostics and Validation" can be told what a good answer looks like *there*.
Splitting reduces the surface over which the judge must generalise. That is the entire
mechanism.

*Evidence:* `docs/reframed-argument.md:7-13`. The report knows this rung is missing —
there is a 22-line `TODO(author)` at `1_Introduction.tex:135-156` saying so in as many
words, and calling it "large enough to warrant its own chapter."

*Caveat:* stated this way, the thesis's value proposition is a claim about **judging**,
not about partition quality. Everything below follows from taking that seriously.

---

### Rung 4 — ARGUED. The claim therefore decomposes into three links, each separately falsifiable.

```
coherent cells  ->  specific rubrics  ->  better judgments  ->  ranking closer to ground truth
      link 1              link 2                link 3
```

Naming them separately is what makes the negatives readable, because they land on
different links and mean different things.

*Evidence:* `docs/reframed-argument.md:15-25`; `docs/prereg_rubric_specificity.md:9-14`.

*Caveat:* this decomposition was written after some of the results. Say so. It is a
reframing, and a reframing announced is a contribution; a reframing concealed is a
rationalisation.

---

### Rung 5 — MEASURED. Link 1 holds: the construction produces cells separated beyond chance, and it certifies its own fixed point.

The splitter accepts a split only when the partition's chance-corrected separation clears
0.025 on every child pair **and** the improvement in the global objective exceeds twice its
own paired bootstrap standard error.

*Evidence:*
- The score and its chance correction: `StatisticsUtils.kt:193-219`, matching
  `11_App:522-553` exactly (§1.2).
- The bar's position between two measured nulls: isotropic p95 spans 0.0055-0.0093 over
  n = 75..900, within-node p50 around 0.033-0.063 (`frozen-artifact.md:129-136`;
  `separation_null_by_size.md`).
- The z-gate: `SE(dJ)` spans **13.1x** from p10 to p90 on this corpus, and the
  uncalibrated rule accepted **4 of 52** edits below z = 1, the worst at z = 0.156
  (`transferable-findings.md:48-52`; `frozen-artifact.md:96-101`).
- The certificate: `edits delta 0`, `max 1-cos(mu) 1.1e-16`, CERTIFIED true, iterations
  8/9/10 identical on every column (`frozen-artifact.md:27-39`).
- The artifact: 154 nodes, 87 leaves, J = 0.253129, 87/87 rubrics
  (`frozen-artifact.md:9-19`); leaf sizes median 88, IQR [71,118], verified today from
  `snapshots.db`.

*Caveats, all of which must travel with it:*
- "Chance-corrected" means **against random relabelling into the same size profile**, not
  against anisotropy. A cut through a node's own elongation is not excluded by `J`.
- The z-gate is defended on **coherence alone**. Two empirical corroborations were tested
  and both refuted: it does not tighten stability (additive ~4.4-leaf offset,
  `corr(reduction, seed deviation) = +0.006`, variance ratio 1.05 vs F(4,4) crit 6.39) and
  it does not raise J (2 of 5 seeds, sign test p = 0.812) — `frozen-artifact.md:104-117`.
- The certificate certifies *this artifact*, not that the loop terminates from an arbitrary
  start. It does not (`frozen-artifact.md:47-50`).
- Two certificate fields are bounded, not reproducible (`known-defects.md:9-25`).
- The within-node nulls and the six named marginal splits are **void as to values** on the
  frozen tree (`void-results.md:24`); the method survives.
- One leaf of 87 sits below the birth floor. That is a property of the mechanism, not a bug
  (`frozen-artifact.md:150-155`), and it was confirmed today.

---

### Rung 6 — MEASURED. Link 2 holds, and it holds against a randomised null.

Rubrics induced on coherent cells are specific to their cells; rubrics induced on
size-matched random cells drawn from the same corpus are not.

*Evidence:* `docs/prereg_rubric_specificity.md` (predictions and thresholds fixed in
advance), `docs/prereg_arena_launch.md:63` (the `<= 0.05` band fixed in advance), and the
run at `build/rubric_null/measures_all.json`:

| | leaf-87 | leaf-13 (matched) | random-13 |
|---|---|---|---|
| within-arm specificity, median | **0.138** | 0.134 | **0.012** |
| cells with positive specificity | 81/87 | 13/13 | 7/13 |
| pairwise Jaccard between rubrics | 0.0754 | 0.0727 | 0.1187 |
| terms in >= 90% of rubrics | **0** | 1 | **6** |

Mann-Whitney U, one-sided, leaf-87 vs random-13: **p = 1.2e-6** (reproduced today; §0.2).
Robust to the three `Q_i` definitions: 1.2e-6 / 2.1e-6 / 7.6e-6.

*Caveats:*
- Lexical only. This shows **reproduction** of cell vocabulary, not **application** of
  criteria. The rule-ID citation scheme is the instrument that would settle it, and it
  changes the verdict schema so it must land before any further arena run
  (`arena-math-findings.md:212-216`, `:250-252`).
- The treatment bundles coherent membership with an informative topical label; the null
  cells are labelled `Cluster NN` (`rubric_specificity_null.py:157-161`). A label-only arm
  is not run.
- 13 random cells against 87 leaves. The n-matched subsample and a 200-draw bootstrap both
  hold, but the null arm is small.
- The supporting artifacts are **untracked in git**.

---

### Rung 7 — MEASURED. Link 3's premise fails on this corpus: cells do not have different *true* rankings.

Before asking whether a judge ranks better inside a cell, ask whether there is anything
different to rank. Pre-registered, then run.

*Evidence:* `docs/prereg_discriminative_power.md:74-79`. Observed Spearman between cells
is flat across an 11x change in granularity — 0.929 at 14 domains, 0.922 at 88 leaves,
0.922 at 87 leaves, 0.905 at 152 — with overlapping IQRs. Centring out each model's global
mean leaves residuals of -0.119 / -0.024 / -0.024 / -0.024, all within 1.5-3.6x of the
mechanical centring null `-1/(C-1)` (`:139-148`). A routing correction worth +10.3% J
changes discriminative power by **zero** (`:92-97`).

*This is the rung that refutes the thesis statement at `1_Introduction.tex:222-223`* — the
"geometry-adapted groupings improve fidelity" half. `\Delta\tau` between adapted and
canonical measures a difference with no room to exist, so a null there says nothing about
the mechanism (`reframed-argument.md:27-46`).

*Caveats:*
- **Power, not proof.** Per-model per-cell accuracy has SE ~2.1 pp at 14 domains, 5.8 pp at
  87 leaves, 6.9 pp at 152. The null is consistent with "no cell-specific signal" and with
  "a signal below ~6 pp at leaf granularity" (`:150-169`).
- **Roster.** 54.1 accuracy points of spread. `rho ~ 0.92` was largely measuring "gpt-4o
  beats Llama-2-13b in every cell". A roster within ~10 points is untested and is the
  version that could still come out positive (`:113-114`).
- **Ceiling, not prediction.** Measured on each cell's own constituent queries and on
  ground-truth accuracy, never on routed held-out queries and never on verdicts. It bounds
  what an arena can discover; the arena can show less, never more (`:125-131`).
- The re-derivation at the corrected 11-model roster is **not in the repository** (§0.4).

---

### Rung 8 — MEASURED. Link 3's mechanism fails too, and for a reason the design did not anticipate: the two judges reach the same verdict.

The rubric-conditioned judge and a rubric-free MT-Bench-style judge, on identical
(question, model-pair) comparisons, complete overlap, 1736 each.

*Evidence:* `arena-math-findings.md:158-176`.

```
identical verdict          1529 / 1736 = 88.1%
disagreements               207, of which 197 (95%) involve a TIE on one side
actual winner flips          10 of 1736  =  99.4% agreement
```

Two judges agreeing on 99.4% of winners cannot produce a detectable ranking difference at
any n, any granularity, any domain count. **So the per-cell null is not evidence of parity;
it is a comparison whose arms barely differ.**

*The rubric is read — it is just not decisive.* Rationale-rubric lexical overlap is 0.200
(IQR [0.115, 0.280]) under the rubric judge against a 0.138 (IQR [0.077, 0.200]) baseline
from a judge that never sees it — 45% above baseline with offset IQRs
(`arena-math-findings.md:196-202`). **Rationale-conditioned, not rationale-driven**: the
verdict is fixed before the rubric enters, and the rubric shapes the justification
afterwards (`:204-208`).

*Caveats:*
- The arena cannot separate the conditions at n = 8 and that is **structural, not
  underpowered**: Spearman at n = 8 is quantised in steps of 0.0119, so the observed gap of
  0.024 is exactly two grid steps — one adjacent swap. Only more models change this; more
  judging cannot (`:150-154`).
- Win-rate manufactured a 5/0 sign-test result (p = 0.031) that BT theta erases
  (5/2/4, p = 0.227), because the adaptive scheduler over-samples uncertain pairs. **Quote
  BT** (`:178-188`).
- The pre-registered mechanism prediction (effect tracks reusable share, weakest in
  enumerative cells) **could not be tested on Math**: the decisive range `<= 0.067` is
  absent, not underpowered; Math's minimum is 0.080 (`:224-231`).

**The lesson, which is transferable and belongs in the thesis:** measure verdict agreement
*before* spending a budget on an A/B arm. It is one query and it decides whether the arm is
worth 10,000 calls (`:174-176`).

---

### Rung 9 — MEASURED. The reason: on a multiple-choice corpus the judge bypasses the partition by re-deriving the answer key.

Four measurements, each with a control that shares every confound except the treatment.

*Evidence, all `arena-math-findings.md`:*

1. **It agrees with the key.** On items where exactly one response is correct and the judge
   did not tie: 88.8% (rubric) and 88.4% (generic). The rubric moves it by 0.4 points
   (`:11-20`).
2. **It ties exactly where the key stops discriminating.** Tie rate ~11% when one response
   is correct; **38.0%** when both are; **33.1%** when neither (`:26-33`). A three-fold jump
   precisely where correctness cannot decide. This was not part of the hypothesis.
3. **Fidelity collapses when the key cannot discriminate.** On the 576 rows where both or
   neither response is correct: rho falls 0.9762 -> **0.7619** (rubric) and 0.9524 ->
   **0.7381** (generic), while the tie fraction triples 0.11 -> 0.34 (`:54-61`). At n = 8
   the Spearman grid is 0.0119, so that is ~18 grid steps — not quantisation noise.
   **Selection control, pre-registered:** the blind subset preserves the true ordering
   perfectly, `rho(GT_blind, GT_full) = +1.000`, and GT accuracy spread falls only 3.5%. So
   the drop is judgment, not range restriction (`:63-69`).
4. **Reasoning text makes it worse at matching the key.** Agreement is *highest* where
   neither response carries a trace (92.9%) and *lowest* where both do (84.2%) — an
   8.7-point gap at ~2.7 SE, same shape in both conditions (`:98-108`). That inverts the
   design assumption and is exactly what verification predicts, with prose as a distraction.

**Together these identify one mechanism: the arena is largely re-deriving the answer key
and reporting it with domain-flavoured justification** (`:35-46`).

*Caveat:* residual reasoning-based signal is real — 0.75 is well above chance — but
substantially weaker than the aggregate 0.95 implies (`:80-82`).

---

### Rung 10 — MEASURED, and it is a defect found by an independent route. Half the Math comparisons were decided by a capture gap.

*Evidence:* `arena-math-findings.md:468-547`. Four of the eight roster models had
`model_output` stored as the empty string across all 12,032 rows — a capture gap in the
eval pipeline, not model behaviour. `getRobustTrace` (`TaxonomyBenchmarkService.kt:1740`)
substituted a one-line stub. The judge picked the side with text **99.4%** of the time
(SE 0.3%), against 87.6% GT-correctness for that side. **Mixed pairs were 868/1736 = 50% of
all comparisons.**

*What this qualifies:* the 88.8% aggregate (half its support is format-decided), the
rho = 0.95-0.98 (ranking all four traced above all four bare reproduces the GT top-4/bottom-4
split for free), and rho_blind = 0.74-0.76.

*What survives, and strengthens:* within-stratum comparisons share a format. At matched
capability gap (< 20 pp), bare-letter pairs score **97.0%** and reasoning pairs **83.2%** —
a 13.8-point inversion **with capability controlled** (`:529-539`). The finding
"reasoning text degrades the judge's agreement with the key" is now a within-format result
rather than a cross-format one. And the granularity and domain-screen results never touch a
verdict, so they are unaffected (`:546-547`).

*The transferable sentence:* **an LLM judge shown a reasoned response against a bare answer
selects the reasoned one 99.4% of the time, regardless of which is correct** (`:631-633`).

*What was done about it:* the loader defect is fixed and 356,402 rows were backfilled;
the corpus went from 13 to 37 models with traces. Ten named models are now refused at roster
load (`EvalIngestValidator.kt:312-338`), written because a documented exclusion is not an
enforcement point (`arena-math-findings.md:885-894`). The `reason_code` side-channel found
in `arx_3`/`arx_0314` — a self-reported confidence field predicting correctness at
A -> 83.2% / C -> 36.5% — is closed by an allow-list unwrap on both render and ingest paths
(`TraceEnvelope.kt:29-35`, `ModelEvalLoader.kt:254`).

---

### Rung 11 — ARGUED, from rungs 8-10. This locates precisely the setting where the architecture would bind.

MMLU-Pro is multiple-choice with a verifiable key, so a capable judge can shortcut to
correctness and bypass the partition entirely. The architecture can only bind where
correctness is **not** checkable — open-ended generation, agent traces, tasks with no key.

That was always the motivation. It is now the **measured** argument for it rather than a
preamble (`arena-math-findings.md:134-141`). MMLU-Pro grounds the comparison and is
simultaneously the corpus where the judging mechanism can bypass what the comparison is
about. Both facts are true, and stating them together is the thesis's most defensible
sentence.

*Caveat:* this is an inference from a Math pilot at n = 8 with a known format artifact. It
is a hypothesis with strong support, not a demonstration. The demonstration is the
options-blind arm.

---

### Rung 12 — MEASURED. There is a domain where the partition has something to be right about, and the roster to run it exists.

Free, offline, no judge calls: per-domain ground-truth accuracy ranking against the global
ranking, with a size-matched permutation null over random subsets of the same reserved pool.

*Evidence:* `arena-math-findings.md:802-816`, at the roster the arena will actually use:

| domain | (A) per-domain roster | (B) 11-model band |
|---|---|---|
| **law** | n=285, rho=0.942, **p=0.000** | n=287, rho=0.955, **p=0.008** |
| **math** | n=391, rho=0.979, p=0.000 | n=393, rho=**1.000**, *p=1.000* |

**Law is significant under both policies at full question count. Math at the 11-model band
scores rho = 1.000 — the band's models order identically in Math as they do globally, so an
arena there has nothing to detect.** And, verified today (§0.3), that 11-model band **is**
the report's own documented roster minus `gemini-1.5-pro-002`, with law coverage 287/287
and a 39.8-point accuracy spread.

*Caveat, and it is the most instructive methodological lesson in the project:* this
conclusion **reversed twice** before settling. First, at 8 models Math looked
indistinguishable from a random subset (p = 0.217) and the recommendation was law. Then at
37 models Math became significant (p = 0.001) and the recommendation flipped to Math. Then
that flip turned out to rest on an intersection poisoned by one id-space-mismatched model,
which collapsed law from 287 questions to 20. **Both inversions came from evaluating a
ranking statistic at a model count that did not match the decision it was informing**
(`arena-math-findings.md:826-835`). The screen must be computed at the roster the arena will
actually use. Report the reversals; they are the finding.

*Second caveat:* both screens use MMLU-Pro's native category labels, not induced cells.
They **bound** what a partition could show; they do not show that induced cells separate.
That remains the test (`:461-464`, `:770-777`).

---

### Rung 13 — the standing measurement debt, stated so it is not mistaken for a result.

- **The reliability constant is 3.04x too large.** Published `c = 7.66`; two independent
  errors compound in the same direction — Spearman-Brown applied after the fit rather than
  before (x0.50) and roster dependence (x0.66) — giving **c = 2.52** at the 11-model band
  (`arena-math-findings.md:896-925`). Disattenuation is **two-sided**, `rho_obs / r`, not
  `rho_obs / sqrt(r)`, because both sides are attenuated per-cell rankings (`:926-932`).
- **Consequences invert.** At a 40.8-query cell, observed median rho = 0.823 corrects to
  0.978 under 7.66 and to **0.874** under 2.52 — below the 0.90 redundancy threshold
  (`:934-948`). The reliability ladder compresses: spread across granularities falls from
  0.219 to 0.088, which **weakens the reliability leg** of the argument for judging at a
  coarser cut; the identification-cost leg (33-45 calls/cell) is untouched and probably
  carries it alone (`:954-967`).
- **The redundancy percentages cannot be reproduced.** "72.2% redundant, 42.2% saturated"
  did not reproduce under either an observed-primary or a disattenuated reading, and the
  convention is underspecified in the pre-registration. **Treat as unresolved; do not
  restate the figure.**
- **The discriminative flatness at the corrected roster is not in the repository** (§0.4),
  and `minClusterSize = 55`'s justification depends on it.
- Everything quoting `r = n/(n+7.66)` needs revisiting: `frozen-artifact.md:83`,
  `router-shared-kappa-correction.md:129`, `dag-logic-and-math.md`,
  `prereg_discriminative_power.md`, and `tools/analysis/cell_fidelity_and_a3.py:140`.

---

# Part 3 — What goes where

**Constraint:** arena results are the centre of gravity; taxonomy construction goes to the
appendix.

That constraint is not a demotion — it is what the evidence supports. Link 1 is the
best-evidenced part of the project and it is also the part with the least *evaluative*
content: `prereg_discriminative_power.md` showed that an 11x change in granularity and a
+10.3% J routing correction both change discriminative power by zero. A construction whose
quality is evaluatively flat should be an instrument in an appendix, not a chapter of
results. And `1_Introduction.tex:225-233` already says so — "the induced taxonomy is *not*
the contribution of this thesis; it is the instrument." The current chapter allocation
contradicts the thesis's own stated position.

## 3.1 Proposed structure

| ch | title | content | source |
|---|---|---|---|
| 1 | Introduction | Rungs 1-4. The routing motivation, the evaluation gap, **and the missing argument**: a partition is worth building only if it changes what a judge can be told. Ends with the three-link chain and the reframed RQs. | `1_Introduction.tex:1-134`, plus writing the `TODO` at `:135-156`; `reframed-argument.md:7-25` |
| 2 | Related work | Five bodies, but **cut to what the argument uses**: LLM-as-judge reliability and its known biases; pairwise ranking and BT; benchmark saturation and contamination; taxonomy induction (short). | `2_Literature.tex`, trimmed |
| 3 | The system | One chapter, arena-first. Arena lifecycle, scheduling, judge design, dual-call control, aggregation. Taxonomy construction gets ~3 pages: what a cell is, what guarantees it carries, pointer to Appendix A. | `3_Arch:345-551` promoted; `:231-344` cut to a summary |
| 4 | Method and measurement discipline | BT/MM, Fisher SEs, rank agreement — **and the four measurement rules with their instances**. This chapter is a genuine contribution and currently does not exist. | `4_Methodology.tex` + `measurement-discipline.md` |
| 5 | Experimental design and pre-registration | Corpus, split, roster (11), conditions, and the pre-registrations **reproduced with their dates**, including the decision rules and outcome bands fixed before the data. | `5_Exp` + `prereg_*.md` |
| **6** | **Results: what the judge does** | **The centre.** Rungs 8-10. GT-agreement, verdict agreement, the correctness-blind split, the trace inversion, the capture-gap defect and what survives it. | `arena-math-findings.md:1-560` |
| **7** | **Results: what the partition does** | Rungs 5-7 and 12. Link 1 guarantees in summary; link 2 with its randomised null (p=1.2e-6); link 3's premise failing under pre-registration; the domain screen and its two reversals. | `prereg_rubric_specificity.md`, `build/rubric_null/`, `prereg_discriminative_power.md`, `arena-math-findings.md:790-836` |
| 8 | Discussion | Rung 11. Where the architecture binds and why this corpus cannot show it. Polyhierarchy as a measured negative. Threats, limitations, the standing measurement debt (rung 13). | `7_Discussion.tex:21-110` kept verbatim as the model; the rest rewritten |
| 9 | Conclusion | Two contributions restated as what was demonstrated; the scope caveat; the options-blind arm and the law run as the named next steps. | `8_Conclusion.tex` (currently a TODO) |
| A | Taxonomy construction formalism | The full construction: routing, splitting, acceptance, merging, the fixed-point certificate, all parameter derivations. | `11_App` **corrected per Part 1**; `frozen-artifact.md`; `separation_null_by_size.md` |
| B | Numerics and metric definitions | BT numerics, Fisher information, metric formulas. | `12_App`, `9_App` |
| C | Judge generation | Rubric MapReduce, the induction hold-out and its build-time audit. | `8_App`, corrected (pack size 25, judge model verified) |
| D | Model roster and exclusions | The 11 models, and the exclusion table **as a measurement**. | `10_App`, corrected |
| E | Transferable findings | The four results that generalise. | `transferable-findings.md` |

## 3.2 Rationale per move

**Splitting Results into two chapters (6 and 7) is the load-bearing move.** They answer
different questions, have different populations, and one is a judge result while the other
is a corpus result. Interleaving them is what currently makes the negatives read as one
undifferentiated failure. Chapter 6 is about a judge and its conclusions stand independently
of the taxonomy. Chapter 7 is about a corpus and a roster, and its conclusions stand
independently of the judge. `arena-math-findings.md:451-456` makes exactly this point:
"the Math arena validated the judge, not the taxonomy."

**Chapter 6 before chapter 7.** The judge finding is the strongest result in the project,
it is what a reader will remember, and it is what makes chapter 7's nulls interpretable
rather than disappointing. A reader who learns in chapter 6 that the judge decides on
correctness already knows why the rubric contrast in chapter 7 is flat.

**Construction to Appendix A.** Three reasons, in order of force. (i) The thesis already
says the taxonomy is the instrument, not the contribution (`1_Introduction.tex:225-233`).
(ii) Granularity is evaluatively flat over 11x, so the construction's *tuning* has no
measured evaluative consequence (`prereg_discriminative_power.md:83-97`). (iii) Part 1
found that `11_App` describes three removed mechanisms and omits four live ones — the
formalism needs a careful rewrite, and it is much easier to do that correctly in an
appendix than under chapter-level narrative pressure.

**Methodology gains a measurement-discipline section.** Four rules, each with the instance
that produced it: a test that cannot fail is not a test; report a join's overlap before its
result; report a median with its IQR; a threshold derived for one quantity at one stage
does not transfer (`measurement-discipline.md`). This is genuinely transferable and it is
currently in `docs/` only. It also pre-arms the reader for chapters 6 and 7, where three of
the four rules did real work.

**Discussion keeps `7_Discussion.tex:21-110` verbatim.** The polyhierarchy section is the
best-written thing in the report and it is the exact model to imitate: operator stated,
measurement shown (`r(f, dJ) = +0.085`, complete distributional overlap, median dJ an order
of magnitude below splits), structural reason given (a partition objective is indifferent
to polyhierarchy), decision recorded, cost of the decision named, replacement invariant
stated. Every negative result in the thesis should be written to that template.

## 3.3 Cut entirely

| cut | why | citation |
|---|---|---|
| **RQ2 as currently worded** and every `\Delta\tau` between adapted and canonical | Refuted at its premise, pre-registration, before the arena ran. Measuring a difference with no room to exist. Replace with "does adapted grouping enable better judging?" | `reframed-argument.md:27-46`; `prereg_discriminative_power.md:171-181` |
| **Condition C2** (canonical re-aggregation) | It answers only the deleted RQ2. | `5_Exp:185-189`, `:198-201` |
| **Routing ECE as a DQ1 headline** | Keep the number (it exists: 0.2114), fix the aggregation, and demote it to a routing diagnostic in Appendix A. It is not evidence about evaluation quality. | §0.1 |
| **Judge Cohen's kappa and `Delta_verbosity`** | No implementation exists. Either delete or replace with what *is* measured: dual-call agreement rate, tie rate by stratum, and the length/format analysis that produced the 99.4% result. | §1.0 AU |
| **The DQ1 baseline table** (k-means / HAC / random null, six metrics) | The runs do not exist, and the metrics do not bear on any of the three links. Replace with one paragraph reporting the certificate and the separation nulls. | `6_Results:39-74`; `5_Exp:246-285` |
| **The scheduler-efficiency diagnostic** | Already demoted to optional; nothing depends on it, and the budget-fidelity figure has no data. | `5_Exp:48-52`; `6_Results:238-256` |
| **The named arena state machines and the state diagram** | They describe code that does not exist. Replace with the four exits that are real. | §1.4, item 3 |
| **The `1/k` fractional-weight aggregation and its sensitivity section** | Not implemented as specified; the post-hoc analysis computes something else. Either implement it or describe what `ValidationService.kt:682-690` actually does. | §1.4, item 5 |
| **Three seeds `{42, 137, 2048}` as a headline convention** | Only seed 42 exists for the frozen artifact and every arena result. Report single-seed honestly with the seed-dispersion analysis as a separate, dated ablation. | `frozen-artifact.md:9-19`; `void-results.md:21` |
| **The five-metric DQ1 vocabulary in the RQ table** | Reduce to what is used. | `5_Exp:38-44` |

## 3.4 Numbers that must change wherever they appear

| wrong | right | where |
|---|---|---|
| `minClusterSize = 30` | **55** | `7_App:18`; `11_App:314-321`, `:385-386`; `6_Results:89,92` |
| `separationBar = 0.02` | **0.025** | `7_App:19`; `11_App:591` |
| `alpha ~ 0.82` from `rho = 256/30` | **`alpha = 0.33`** from `rho = 256/55` — the passage's conclusion inverts | `11_App:314-321` |
| `\binom{12}{2}=66` | **`\binom{11}{2}=55`** | `5_Exp:130`, `:304`; `6_Results:190` |
| 12 models | **11** | `5_Exp:100`, `:139`; `10_App:3,9,15`; `6_Results:174,176` |
| 500-iteration BT cap, tol `1e-6` | **200**, tol `max(tol, 0.01*SE_lb)` | `4_Methodology.tex:90-91` |
| "pseudoinverse" | rank-completed inverse of `I + 11^T` | `4_Methodology.tex:96-99` |
| `- 1/K` variance correction | **`- 1/K^2`** — fix the code too | `12_App:137-139`; `BtMmFitter.kt:383` |
| bootstrap "2,000 resamples" for BT CIs | 2000 in `ValidationService`, **50** in the ranking path, **1** in the trajectory | `5_Exp:307-310` |
| rubric pack size `k = 5` | **25** | `8_App:9-11` |
| path cutoff `1e-4`, per path | **`1e-30`**, on the summed node posterior | `11_App:477-478` |
| lexicographic acceptance | `dJ > max(tau, 2.0 * SE(dJ))`; add an `acceptanceZ` row to the table | `11_App:616-624`; `7_App:12-30` |
| `numIterations` 50 / 35 | pick one; the frozen run converged at iteration **10** | `7_App:27` vs `:142` |
| "guarantees every pair at every leaf" | bootstrap is on **global** pair counts | `4_Methodology.tex:100-104`; `3_Arch:398-408` |

---

# Part 4 — What could not be verified

Stated explicitly so nothing here is mistaken for checked.

1. **The 11-model-band discriminative flatness (0.973 / 0.936).** Not in any doc, script
   output, or artifact. `arena-math-findings.md:838-842` still says it has not been
   re-derived. §0.4.
2. **The redundancy percentages** ("72.2% redundant at rho > 0.90, 42.2% saturated"). Not
   reproducible under either convention; the convention itself is underspecified. Do not
   restate.
3. **Whether the exported Routing ECE of 0.2114 survives the aggregation fix.** The
   `maxOf`-vs-sum change will move it, and in a predictable direction (confidence rises, so
   apparent under-confidence falls), but by how much is unmeasured.
4. **Whether `c = 2.52` is right for the roster the arena will use.** It was fitted at the
   11-model band, which happens to match the corrected roster (§0.3) — but the fit was not
   re-run against that roster's *arena* rankings, only its ground-truth ones, and the
   constant is explicitly not a property of the corpus (`arena-math-findings.md:881-883`).
5. **`docs/measurement-discipline.md:191`'s `c = 7.602` vs everyone else's 7.66.** A 0.8%
   discrepancy with no stated cause, predating today's correction.
6. **The judge model actually used in the frozen arena run.** `8_App:12-13` and
   `arena-math-findings.md:618` say `Mistral-Large-3`; `TaxonomyConfig.kt:59`'s default is
   `ministral-3:14b`. Resolve against the run manifest before the appendix ships — the
   self-preference claim ("appears nowhere in the roster") depends on it.
7. **Whether `report/03_Content/2_Literature.tex` (783 lines) supports the argument as
   rebuilt.** Not read in this pass.
8. **The within-node nulls, the six named marginal splits, the lambda1 proxy, the maxK
   plateau, the five-seed sweep, core/fringe, matched-k ARI.** All void as to values on the
   frozen tree (`void-results.md:19-28`); methods survive, numbers need re-deriving. Not
   re-derived here.
9. **Anything in `report/03_Content/2_Literature.tex` and `3_System_Architecture.tex:1-344`**
   against the code. Only `:345-551` was audited.
10. **Whether the law run is affordable.** Budget arithmetic exists for a 10-model roster
    (`arena-math-findings.md:714-723`); at 11 models it is 55 pairs, which was not
    recomputed.

---

# Part 5 — Presenting the negatives as strengths

Six of this thesis's most important results are negative or self-corrected. Buried, they
read as a project that did not work. Framed correctly, they are the evidence that the
measurement was real. The device in every case is the same: **show that the result could
have come out the other way, and that the criterion for reading it was fixed before the
data.**

**1. Pre-registration is the frame.** Three documents fix predictions, decision rules and
outcome bands in advance: `prereg_discriminative_power.md` (three named outcomes, `:51-56`,
plus "observed rho is primary" fixed at `:38-42` — which is the only reason the conclusion
was readable, since the disattenuated column moves the *opposite* way and clips past 1.0),
`prereg_rubric_specificity.md` (four directional predictions with the confound direction
named per measure, `:44-52`, and thresholds at `:111-117`), and `prereg_arena_launch.md`
(the `<= 0.05` band, `:63`, and cost bands "no band is to be renegotiated after the number
is seen", `:21`). Reproduce these in chapter 5 **with their dates**. A null under a
pre-registered rule is a finding; a null under a rule chosen afterwards is a shrug.

**2. Name the link each negative lands on.** "Cells do not have different true rankings"
(link 3's premise) and "the rubric does not change the verdict" (link 3's mechanism) are
different results with different scopes, and neither touches links 1 or 2 — which both came
out positive. The three-link chain is what makes that legible.

**3. Errors found by independent routes are the credibility argument.** Four cases:
- The trace capture gap was found *while sizing the roster for a different experiment*
  (`arena-math-findings.md:470`), and it qualified numbers already written down.
- The `reason_code` side-channel was found by a format check whose only anomalous column
  was newline count (`:637-643`).
- The reliability constant was caught twice by two independent routes — a roster-size
  re-fit and a units check on the split-half length mismatch — that compounded to the same
  3.04x (`:918-925`).
- The domain screen reversed twice, and the *reason* for both reversals turned out to be
  one thing: a ranking statistic evaluated at a model count that did not match the decision
  it informed (`:826-835`).
None of these was found by looking for it. That is the point: they show the measurement
apparatus catching its own errors, which is the strongest available evidence that the
results it did not overturn are sound.

**4. Refuted corroborations are stronger than unrefuted ones.** The z-gate was adopted on
coherence alone after **both** of its empirical corroborations were tested and refuted
(`frozen-artifact.md:104-117`). The defensible sentence — *a gate can be right because its
units are right, without improving the number it gates* — is more transferable than "the
gate helped" would have been.

**5. The 99.4% verdict agreement is a methodological contribution, not an excuse.** The
arms of a pre-registered A/B contrast turned out to be nearly the same treatment, which no
amount of power fixes. The rule that follows — measure verdict agreement first, it is one
query and it decides whether the arm is worth 10,000 calls (`:174-176`) — is the kind of
thing a reader takes away and uses.

**6. The strongest negative is the one that relocates the claim.** The judge bypassing the
partition on a multiple-choice corpus is not a failure of the architecture; it is a
**measurement of the boundary of the architecture's applicability**, obtained on the corpus
that makes the comparison possible. Rung 11. That sentence is the thesis, and it is only
available because the negatives were measured rather than avoided.

**One thing to add rather than reframe.** `arena-math-findings.md:296-319` fixes the
options-blind predictions before the run — including the second possibility for
`trace x trace` ("landing near 84% unchanged would mean the judge was never using the key
on traced pairs, so the 88.8% aggregate is carried entirely by the untraced and mixed
strata"). Writing down the alternative outcome in advance, in a document with a commit
date, is the most defensible thing in this project. Reproduce it verbatim in chapter 5 and
let the reader see that the interpretation was fixed before the number.
