# Rubric v2 — from a process checklist to a verification kit (design, 2026-09-10)

## What the evidence says a rubric is, and is not

| finding | source | consequence for design |
|---|---|---|
| Induced cell rubrics are worth 0 to +1pp to either judge tier on keyed questions; anchor = leaf | RUBRIC-P8 (0.0), 512 (+1.8 boundary), 512-SS (+1.0 n.s.), 512-R (0.0, reasoning judge); ladder p=0.68 | the current rubric TEXT is not a lever; finer text is not better text |
| The rubrics are specific but are PROCESS checklists ("apply the governing law, check units, justify assumptions") with no cell-specific failure modes or facts | free audit 2026-09-10: 2,861 chars median, Jaccard 0.08, 7% boilerplate | they tell the judge what good reasoning looks like in general, which it already knows; they give it nothing it can CHECK |
| Rubric gain tracks judge competence (ρ=+0.52): rubrics help where the judge can already solve | S1 | a rubric guides evaluation; it does not substitute for the ability to verify |
| A reference answer is the lever (+7.6 all, +13.9 top cluster); a wrong reference hurts; two references are worse than one | J2, J2-R, J2-D | what helps is VERIFIABLE content about the answer, not advice about reasoning |
| Verify-first mechanics move the elaboration bias (truncated arm 0.350 → 0.433) and, with the reference and the anchor rubric, give the best judge measured (0.865, board within the <=1-violation bar - NOT key-ordered: it gives gemini > iask > arx > gpt-4o against the key's gemini > arx > iask > gpt-4o [corrected 2026-09-14 against stack_v2_outcome.txt]) | L1-V2, STACK-v2 | the prompt's job is to force verification before comparison; rubric content should feed that verification |
| Leaf-level structure is real in the key (model×leaf interaction p=0.005; Math leaf-over-anchor +12.7/1000) — what models get wrong IS cell-specific | LEAF-PROFILE A, F2, F5 | the cell's train-side wrong answers and solved examples are the information a leaf uniquely holds |
| Rubrics generated from the question alone score below no-rubric; response-in-view rubrics help; decomposed + filtered checks help most | Shen et al. 2602.05125 (in the proposals doc) | induce WITH wrong answers in view; decompose into checks; filter by the key |
| Markdown/format carries no weight; padding carries no weight; content of reasoning does | FORMAT, L1 pad, L1 truncate | do not spend rubric text on style; spend it on checkable content |

Conclusion: a rubric in this system should not be a description of quality. It should be a **verification kit**: the material a judge that cannot solve the question needs in order to check the two answers — assembled per cell from what only the cell has (its solved train-side questions and its observed failure modes), delivered in a form the prompt forces the judge to use.

## Root cause, found in the induction templates
`JudgePrompts.induceBatchGuidelines` instructs the inducer: "Focus on PROCEDURAL LOGIC and VALIDITY of
reasoning, not memorized facts or specific numbers … Rules must describe properties of a REASONING
PROCESS, never properties of an answer's content … Never state what a correct answer looks like." The
process-checklist character of every rubric is therefore by design — a leakage-safety choice (no rule
may help pick an option without reasoning) that also removed everything a non-solving judge could
verify. The kit keeps the safety property by a different mechanism (cell-general content only; the
H2-style n-gram audit against the correct options of every judged question; neighbours filtered for
option overlap) and drops the prohibition on content.

## The kit, in layers (each is separately testable and separately cheap)

**K0 Anchor process rubric** (keep). The 14 clean anchor rubrics from the ladder. Cost 0. Value ≈ the leaf's; it sets the evaluative register.

**K1 Cell failure catalogue** (contrastive, cell-specific). From the cell's TRAIN-side wrong answers (key-labelled, frontier contestants): the 5–8 recurrent error patterns, each with its tell-tale sign and the check that exposes it ("chose the unit-inconsistent option after dropping the 1/2 in ½mv²: check that kinetic-energy expressions carry the factor"). Induced by the reasoning model once per cell (1 call; the anchor-level version is J6's contrastive arm, running now). This is the only layer whose content differs between sibling leaves for a reason the key confirms (LEAF-PROFILE A).

**K2 Cell knowledge card** (content, response-blind). From the cell's train-side reference reasonings: the recurring facts, formulas, definitions, sign conventions and boundary conditions that answers in this cell must satisfy — a compact "what must hold" list (≤ 12 items). Induced once per cell (1 call). Gives the judge checkable statements without solving from scratch; it is what a Math/Physics leaf can offer that "apply the governing law" cannot.

**K3 Worked neighbours** (retrieval, zero calls). The 2 most similar TRAIN-side questions of the same leaf (embedding cosine on the 512-slice), with their key and reference reasoning, inserted next to the judged question as worked examples. Pool hygiene is preserved by construction: the reserved question is never in induction or retrieval material; neighbours are train-side only. This uses the leaf functionally — as a retrieval unit — which is the first design in the campaign where leaf granularity does something an anchor cannot.

**K4 Reference** (the lever, keep). One reasoning-model answer per question, marked as fallible (J2-R). Never gated, never doubled (free test, J2-D).

**K5 Structured verification mechanics** (prompt). v2's verify-first policy, extended into a decomposed output the judge must fill BEFORE the verdict: extracted final answer per response; agreement with the reference; for each K1 failure sign, present/absent per response; K2 facts violated per response; then the comparison and verdict. Turns the rubric from prose the judge may skim into checks the judge must answer (the "decomposed" rubric of 2602.05125). Confidence field kept; dual order kept.

**K6 Key-filtered checks** (adaptive, cell-specific weights; later). On train-side pairs only, have the judge fill the K1/K2 checks once; keep the checks whose presence predicts the key in that cell (logistic filter), drop the rest. Cell-adaptive without touching arena questions. This is the "filtered" step that made the biggest difference in the literature, and it is the mechanism by which the kit adapts to a leaf's actual discriminating signals.

## Restricted domains and arriving domains

- A leaf with 40 train questions still yields a K2 card and K3 neighbours (they need a handful of items) and a K1 catalogue as long as model outputs exist for its questions; the anchor rubric is absent for an unanchored domain (D4) but the kit does not need it. Graceful degradation is measured, not assumed (RK-3 below: kits from 20 / 40 / 80 train items).
- For agent traces without a key, K1 is built from verifier-labelled failures and K4 from a verifier or a stronger agent's run — the same shape; the kit is the reference-free judge's substitute for the key.

## Registered tests (all on R3's 1,980 matches, Mistral, dual order, one session per test; paired McNemar on key-decidable; arms interleaved)

| id | question | arms | cost | pass rule | prediction |
|---|---|---|---|---|---|
| J6 (running) | does authorship or contrastive content change the anchor rubric's value? | Mistral-induced / frontier / contrastive anchor rubric, no reference | ~12k | contrastive > Mistral-induced p<0.05 | null (+0–1pp) |
| RK-1 | does cell CONTENT (K2 card + K3 neighbours) beat the anchor rubric under the STACK-v2 mechanics? | STACK-v2 (anchor rubric) vs STACK-v2 + K2 + K3 | ~4k | +1pp at p<0.05 on all decidable; secondary: gain in Math/Physics/Chemistry/Engineering > discursive | +1–3pp, quantitative-led — the first rubric variant that could beat the anchor, because it supplies facts rather than process |
| RK-2 | does decomposed verification output (K5) beat prose? | STACK-v2 prose vs K5 structured output, same content | ~4k | accuracy ≥ and long-wrong preference lower, ties ≤ 8% | small accuracy gain, larger bias reduction |
| RK-3 | how does the kit degrade in restricted cells? | K2+K3 built from 20 / 40 / 80 train items per leaf | ~6k | gain monotone in items; 20-item kit ≥ anchor rubric | 20 items already ≥ anchor |
| RK-4 | does key-filtering the checks (K6) add value in the cells where the judge is weak? | K5 vs K5-filtered | ~2k train + ~4k | gain in the 6 lowest-S1 anchors > elsewhere | modest |

Honest prior: after four nulls on rubric text, the expected total gain of the kit over STACK-v2 is +1 to +3pp on keyed questions, concentrated where the judge is weak and the content is checkable; its real payoff is the reference-free setting, where K1–K3 are the only verification material available.

## Build plan
- `tools/analysis/rubric_kit.py`: `--induce` builds K1 and K2 per leaf of bareq512_s42 on the reasoning model from train-side material only (2 calls per leaf, ~175 calls); `--neighbours` precomputes K3 (zero calls); `--judge` runs RK-1 (STACK-v2 mechanics + kit) with its own cache; `--analyze`.
- Registration lines above are the commitments; outcomes append below.

## What the data can tell a judge about a leaf (LEAF-SIGNALS, 2026-09-10, zero calls; tools/analysis/leaf_guideline_signals.py)

**Correction of record first.** `mmlu_pro.cot_content` is EMPTY for all 12,000 questions in the dataset
cache (MMLU-Pro ships chain-of-thought only for its 70-question validation split). The induction
pipeline (`TaxonomyJudgeService`, and the ladder/J6 replicas) appends "Correct Reasoning" only when the
field is non-empty, so every rubric in the campaign was induced from question + ten options + key, with
the template forbidding option content. The proposals doc's "induction sees … the reference
chain-of-thought" was wrong. This is the second half of the root cause: no worked reasoning in, no
verifiable content out. The kit's knowledge card (K2) was likewise built from questions and keys only —
and still came out as formulas with validity conditions, because the reasoning model reconstructs them;
worked neighbours (K3) currently carry question + options + key, not a derivation.

**Pipeline per leaf (promoted bareq512_s42):** corpus = the leaf's train-side region questions (mean 86
after withholding the pool of record; 1–3 withheld per leaf, i.e. the routing puts a few arena
questions into every region and they are excluded), chunked by 25 → 4 batch-guideline calls + 1 master
synthesis + 1 persona/rubric synthesis ≈ 6 calls per leaf; the third stage compresses everything into a
"short bullet checklist" (J6 caveat). Arena side: 36 reserved questions per leaf at the median (p10 23,
min 17, max 171). Per-leaf rubric EVALUATION is therefore impossible at any budget on this pool (a +2pp
effect needs ~1,200 decidable matches per leaf [corrected 2026-09-14: rubric_hidden.txt's own power table gives n ~ 1,173 for delta +0.02 at discordant rate 0.06, and this doc quotes that table verbatim elsewhere]); rubric value can only be measured pooled across leaves,
which is what every test did. Enlarging the reserved pool would not help: the binding quantity for a
per-leaf verdict is distinct questions per leaf (H6b, LEAF-POWER), and every question moved to the
arena side is removed from the induction corpus (86 → fewer) and from construction.

**Signals mined per leaf (85 leaves ≥ 40 keyed questions), and whether they are leaf-specific**
(within-anchor share of total variance ≥ 0.5):

| signal | source | leaf-specific? | what a guideline can say |
|---|---|---|---|
| option spacing: correct value vs nearest distractor | options + key | YES (0.78) | "distractors sit within 10% of the right value here: a near-miss is wrong; carry precision" |
| near-miss error share (46 models' wrong picks) | preds + options | YES (0.90) | same, with the measured rate |
| factor-2 error share | preds + options | YES (0.79) | "half the wrong numeric answers are off by ×2 or ÷2 here: check the ½ / 2π / diameter-radius step" |
| hedging-vs-correctness correlation | model outputs + key | YES (0.63) | whether hedged language signals error in this cell |
| numeric-option share | options | no (0.14) | anchor-level |
| attractor strength (share of wrong picks on one distractor) | preds | no (0.12) | anchor-level in strength; but the attractor TEXT is per question |
| tier gap (top-5 minus rest) | key | no (0.23) | anchor-level |
| length-vs-correctness correlation | outputs + key | no (0.36) | see below |
| formula-density correlation | outputs + key | no (0.25) | anchor-level |
| sign errors | preds | none anywhere | drop |

**Length is not a correctness cue in any leaf.** Across 85 leaves, longer outputs are more often correct
(corr > 0.15) in zero leaves, less often correct in six, neutral in 79. The judge's elaboration heuristic
(L1) therefore tracks nothing in the data; it is a pure bias.

**Attractors are the misconception catalogue the data already contains.** In 119 of 400 Physics
train-side questions, ≥ 50% of all wrong picks land on ONE distractor (e.g. correct "dark" vs attractor
"black"; "21.2 MeV" vs "22.1 MeV"; E = (h/2)ν vs E = (h/2)(K/µ)^½). The distractor text IS the
misconception, key-labelled, with a prevalence — better raw material for K1 than model-output excerpts,
and zero LLM calls to collect. Constraint: only train-side questions may be used (for an arena
question the attractor implies the key).

**Consequences for the kit.** K1 should be built from train-side attractor pairs (correct text vs
dominant distractor text, with prevalence) rather than from output excerpts; K2 and K3 should be
regenerated once a reasoning source exists — either MMLU-Pro's validation CoT where a question has it
(70 only) or the reasoning model's own solve of the TRAIN-side neighbour (one call per neighbour, never
an arena question), which turns K3 into genuine worked examples; the answer-form card (numeric share,
spacing, error signature) is a free, data-only leaf guideline that no induction produced. RK-1b
(registered here, zero induction calls): the data-only leaf card (answer form + error signature +
attractor pairs) vs STACK-v2, same design as RK-1.

### RK-1b / RK-1c — registered 2026-09-10 06:50, before any judged call (tools/analysis/rubric_kit2.py)
RK-1b: STACK-v2 vs STACK-v2 + the DATA-ONLY leaf card (answer form, distractor spacing, numeric error
signature, up to 6 conceptual misconception pairs from train-side attractors; zero induction calls;
pairs whose correct text equals a judged question's correct option are dropped; 5-gram audit at judge
time). RK-1c: as RK-1b plus two worked neighbours whose solutions are the reasoning model's own solves
of the TRAIN-side neighbour questions, kept only when key-verified (never an arena question). Both:
R3's 1,980 matches, Mistral, arms fresh and interleaved, ~8k calls each; PRIMARY +1pp at paired
McNemar p < 0.05; SECONDARY quantitative > discursive. Predictions: RK-1b +0 to +2pp; RK-1c +1 to +3pp.
Queue: RK-1 (running) → RK-1b → RK-1c (after the ~2k neighbour solves on grok-reasoning, running now).

#### RK-1b OUTCOME (2026-09-10 14:30) — PRIMARY PASS, SECONDARY PASS
3,948 matches judged (12 skipped: no eval row), 0 errors, leakage audit CLEAN (0 shared 5-grams). 944 key-decidable
paired: datacard 0.875 vs STACK-v2 0.858 (+1.7pp; 32:16; McNemar p = 0.029). Quantitative anchors +3.0pp (18:5,
p = 0.011); discursive +0.6pp (14:11, p = 0.69) → secondary PASS, as predicted (the card's content is answer form,
distractor spacing and the numeric error signature — quantitative material). Top cluster 0.695 vs 0.692 (n.s.).
Per anchor: Business +9.1, Chemistry +6.0, History +4.8, Engineering +4.7, Computer science +3.7; Economics −6.2 (0:4,
n = 65) is the one loser and is flagged for the RK-1c readout. This is the first rubric-side gain on the stack that
clears its registered bar, with ZERO induction calls: the guideline that helps is the data-derived leaf context
(LEAF-SIGNALS), not induced prose. Interpretation is limited to keyed questions and one judge; the deployment
decision waits for RK-1c (card + verified worked neighbours), running now.

### RK-1b-GROK — registered 2026-09-10 15:10, before any judged call (rubric_kit2.py --judge-model grok)
Does the data-only leaf card's gain transfer across judge families as the recipe did (RECIPE-GROK)? Both arms
FRESH on grok-4-1-fast-non-reasoning in one session: STACK-v2 recipe vs STACK-v2 recipe + data card, R3's
1,980 matches, ~7.9k calls at 8 workers, same leakage audit. PRIMARY: +1pp on key-decidable at paired McNemar
p < 0.05; SECONDARY: quantitative gain > discursive gain. Prediction: +1 to +2pp, quantitative-led; if the card
helps Mistral but not grok, the card is compensating a judge-specific weakness rather than adding leaf context.

#### RK-1b-GROK OUTCOME (2026-09-10 16:20) — PRIMARY FAIL (letter), SECONDARY PASS; substance consistent with RK-1b
3,944 judged (12 skipped, 0 errors), leakage audit clean. 944 key-decidable paired on grok-4-1-fast-non-reasoning,
both arms fresh: datacard 0.871 vs STACK-v2 0.858 (+1.3pp; 25:13; p = 0.073). The gain clears the +1pp bar but
misses p < 0.05 → PRIMARY FAIL by the registered letter. Quantitative +1.9 (12:4, p = 0.077) vs discursive +0.8
(13:9) → SECONDARY PASS. Top cluster 0.733 vs 0.699 (+3.4pp, 14:5, p = 0.064). Chemistry +6.0 (4:0) and
Engineering +4.7 (2:0) lead on both judges; Economics, the Mistral loser (−6.2), is flat here (1:1).
Reading: the card's effect has the same sign, the same quantitative-led anatomy and a similar size (+1.3 vs
+1.7pp) on a second judge family, so it is leaf context rather than a Mistral-specific patch — but at n = 944 a
+1.3pp effect is under-powered (discordant pairs 38), and the registered test says FAIL. EXPLORATORY, not
registered: pooling the two judges' discordant pairs gives 57:29 (p ≈ 0.003). Deployment decision stays with
RK-1c; the card is reported as "+1.3 to +1.7pp on two judge families, significant on one".

#### RK-1c OUTCOME (2026-09-10 16:45) — PRIMARY FAIL, SECONDARY PASS: worked neighbours add nothing over the card
3,948 judged (12 skipped, 0 errors), leakage audit clean, 1,667 key-verified neighbour solves available. 944
key-decidable paired on Mistral, both arms fresh: card + verified worked neighbours 0.868 vs STACK-v2 0.859
(+0.8pp; 26:18; p = 0.29) → PRIMARY FAIL (bar +1pp at p < 0.05; prediction +1 to +3pp not met). Quantitative
+1.6 (15:8) vs discursive +0.2 (11:10) → SECONDARY PASS. Top cluster +1.1 (n.s.). Engineering +4.7, Chemistry
+4.5 lead again; Psychology −2.2, Economics −1.5. Read against RK-1b (card alone 0.875 vs 0.858, +1.7pp,
p = 0.029, same matches, separate session): adding two verified worked solutions from train-side neighbours on
top of the card does not improve on the card and, if anything, dilutes it (0.868 vs 0.875 arm values; not a
paired comparison). The judge already holds a reference answer for the judged question; worked solutions to
OTHER questions are context it does not use. RK-2 (gated on RK-1c) is NOT triggered.
DECISION: the rubric-side line closes with the DATA-ONLY leaf card as its one adopted increment
("+1.3 to +1.7pp on two judge families, significant on one, quantitative-led, zero induction calls"). Everything
induced as prose (cell rubrics, frontier/contrastive rubrics, knowledge cards, failure catalogues, worked
neighbours) is null or negative on top of the reference. The production candidate is STACK-v2 + data card,
subject to ARENA-V2's board readout (which runs STACK-v2 without the card).


### RUBRIC-HIDDEN (2026-09-14, zero calls) — was the rubric effect hidden by how we sampled and measured?
Two mechanisms could have concealed a real per-leaf rubric effect. Both are now separated.
MECHANISM 1, THE UNMEASURED PAIRS - REFUTED. Every rubric test scored key-DECIDABLE accuracy and silently
discarded the both-right and both-wrong pairs, which are 1,030 of 1,974 on R3 and are exactly where FRONTIER
showed the judge inventing biased winners. A rubric could therefore have helped invisibly, by making the judge
ABSTAIN there. Measured on the cached paired arms, it does not:
    arm                                invents a winner on non-decidable pairs | of those, the longer answer
    STACK-v2 (no card), Mistral                     62.2%                                81.9%
    + data card,        Mistral                     63.6%                                80.9%
    STACK-v2 (no card), grok                        62.1%                                80.3%
    + data card,        grok                        59.5%                                80.3%
    + card and worked neighbours                    61.0%                                80.6%
  The invented-winner rate sits near 60% and the length preference near 81% in every arm, card or no card. The
  rubric does not buy abstention, so nothing was hidden in the discarded pairs.
MECHANISM 2, POOLING ACROSS HETEROGENEOUS ANCHORS - LIVE AND UNTESTED. The pooled tests carried 944-946
decidable pairs with discordant rates near 0.05, which powers them for roughly a 3pp effect. Detecting 1pp would
need about 3,900 pairs. Per anchor there were only 30-144 decidable pairs, powering each for 10-20pp. So the
per-anchor gains that were actually observed - RUBRIC-512 Philosophy +16.7 and Biology +7.4; RK-1b Business
+9.1, Chemistry +6.0, History +4.8, Engineering +4.7, against Economics -6.2 - were never individually
testable, and a pooled average of large positives, zeros and negatives is exactly how a real heterogeneous
effect looks when it is averaged away.
STATUS OF THE LEAF LAYER SPECIFICALLY: leaf-level rubrics were tested ONCE, in RUBRIC-512, which returned the
strongest pre-card rubric result (+1.8pp, p = 0.0498) with a same-session control at +1.0 (n.s.); LEAF-SS, the
clean leaf-versus-anchor comparison, was queued and then cancelled because its gate (RUBRIC-512-R, the reasoning
judge) came back at 0.0. So "leaf rubrics do not help" rests on one ambiguous test and one cancelled follow-up,
which is weaker than the rest of the rubric line and should be stated that way.
WHAT WOULD SETTLE IT: a per-anchor powered test needs about 215 decidable pairs per anchor to detect 6pp, so
roughly 3,000 decidable pairs across 14 anchors, which at R3's 48% decidable rate and the answer-disagreement
filter is about 6,300 matches per arm - 25k calls for a two-arm test, or about 4k calls if restricted to the
four anchors where the observed gain exceeded 6pp. The cheap version is the honest one and it is a real
candidate. Output experiment_results/x12_crossdomain/rubric_hidden.txt.

### LEAF-POWERED — registered 2026-09-14, before any call (tools/analysis/leaf_powered.py)
RUBRIC-HIDDEN found the live mechanism: the rubric tests were powered for ~3pp pooled and only 10-20pp per
anchor, while the per-anchor gains actually observed were 6-17pp. And the leaf layer specifically rests on ONE
ambiguous test (RUBRIC-512, +1.8pp p=0.0498) whose clean follow-up was cancelled by a gate. This runs that
follow-up, powered, on the anchors where cell context looked strongest.
DESIGN. Arms: ANCHOR rubric (the deployed STACK-v2 configuration) versus LEAF rubric (the promoted
bareq512_s42 tree's own induced judgeRubric for the question's routed leaf - all 87 leaves already carry one,
mean 2,869 characters [rubric_text_stats.txt], so nothing is induced here). Everything else identical: grok-4-1-fast-non-reasoning, the
reasoning reference, v2 verify-first mechanics, dual order, confidence, both arms fresh and interleaved in one
session. Anchors: Philosophy, Business, Biology, Chemistry - the four where the observed per-anchor gain exceeded
6pp in RUBRIC-512 or RK-1b. Questions: the pool of record, routed to those anchors, and the pair must DISAGREE on
its own predicted answers (the shipped matchFilter rule), which raises the decidable rate to ~0.80 so that ~270
matches per anchor buy the ~215 decidable pairs that 80% power at 6pp requires. 1,080 matches per arm, 2,160
total, 4,320 calls.
REGISTERED: PRIMARY, pooled over the four anchors, leaf beats anchor by >= 2pp on key-decidable accuracy at
paired McNemar p < 0.05. SECONDARY, per anchor with Holm correction across the four, how many are individually
significant. DESCRIPTIVE: the per-anchor effect sizes against the earlier underpowered estimates, the decidable
rate the filter actually delivers, and the invalid rate. PREDICTION: pooled +1 to +3pp, one or two anchors
individually significant, and Philosophy the largest - if the pooled effect is null AND no anchor survives
correction, the leaf layer is closed properly rather than by a cancelled gate.
  AMENDMENT 2026-09-14, before any call: the run is SINGLE ORDER, not dual, halving it to 2,160 calls. The
  rationale is that dual order exists to make an ABSOLUTE board trustworthy, whereas this is a within-experiment
  paired contrast in which both arms see the same position bias, so it cancels; and ORDER-1 measured that single
  order resolves MORE pairs than the dual TIE rule (decidable ties 1% against 7%), so power per call rises
  rather than falls. Cost, not statistics, drove the change and that is stated plainly. The registered criteria
  are unchanged. Consequence to disclose with the result: the arms' absolute accuracies are single-order figures
  and are not comparable to the dual-order numbers quoted elsewhere in this document; only the leaf-minus-anchor
  contrast is.


#### LEAF-POWERED OUTCOME (2026-09-14) — PRIMARY FAIL, and for a reason that settles the leaf layer
2,150 verdicts, 0 errors, 786 key-decidable paired matches across the four anchors.
  POOLED     anchor 0.934 | leaf 0.931 (-0.003) | discordant 9:7 | McNemar p = 0.80 -> FAIL
  Chemistry  n=190 anchor 0.921 leaf 0.937 (+0.016) 0:3   Philosophy n=185 anchor 0.908 leaf 0.892 (-0.016) 4:1
  Business   n=205 anchor 0.951 leaf 0.941 (-0.010) 4:2   Biology    n=206 anchor 0.951 leaf 0.951 (0.000) 1:1
  No anchor is individually significant under Holm.
THE DECISIVE NUMBER IS NOT THE p-VALUE, IT IS THE DISCORDANCE. CORRECTION to my first write-up of this run,
which conflated two quantities: the arms return an identical verdict on 92.9% of all 1,078 matches (1,001 of
them), NOT 98%. The 98% belongs to a different and narrower statement, which is the one that carries the
argument: of the 786 KEY-DECIDABLE matches, only 16 (2.0%) differ in whether the verdict was CORRECT, split
9 to 7. So the rubric change moves plenty of verdicts (7.1% of them) but almost never moves a verdict across the
right/wrong boundary. A treatment that changes correctness on 2% of decidable pairs cannot move accuracy by the
6-17pp the underpowered per-anchor readouts had suggested; the arithmetic ceiling is about +-2pp and the
observed value is -0.3pp. So the earlier per-anchor "gains" were noise, and the leaf layer
is now closed on evidence rather than by a cancelled gate.
POWER, STATED HONESTLY AGAINST MY OWN REGISTRATION. I designed for 215 decidable pairs per anchor assuming a
discordant rate near 0.10; the observed rate is 0.02. Under that rate the run could NOT have detected a 6pp
effect, so as a significance test it is underpowered exactly as registered. It is nonetheless conclusive,
because the low discordance is itself the measurement: the intervention barely perturbs the judge.
SCOPE, so this is not over-read: the contrast is LEAF versus ANCHOR rubric, both already domain-specific. It
does not re-test cell-versus-GENERIC, which is RUBRIC-512's ambiguous +1.8pp and remains as it was.
DISCLOSURE required by the amendment: absolute accuracies here (0.93) are single-order figures on a
disagreement-filtered schedule and are NOT comparable with the dual-order unfiltered 0.86 quoted elsewhere;
only the leaf-minus-anchor contrast crosses runs.

## CORRECTION 2026-09-14 — RK-1b restated: most of the gain is ABSTENTION, not discrimination
Found by the ledger audit and reproduced here exactly from stack_v2_kit2.db and stack_v2_kit2_grok.db, 944
key-decidable paired matches, arms separated by their own `arm` column:
    judge     arm                    tie rate   accuracy   accuracy GIVEN the judge committed
    Mistral   STACK-v2 (control)       0.064      0.8581              0.9163
    Mistral   + data card              0.048      0.8750              0.9188   (+0.25pp)
    grok      STACK-v2 (control)       0.070      0.8581              0.9226
    grok      + data card              0.058      0.8708              0.9246   (+0.20pp)
Ties are scored as errors throughout the rubric line, so "key-decidable accuracy" is a DECISIVE-AND-CORRECT
rate. Conditional on the judge actually committing to a winner, the data card is worth +0.25pp on Mistral and
+0.20pp on grok. The tie-rate drop (6.4% -> 4.8%, 7.0% -> 5.8%) carries roughly 1.4 of the 1.7 points. The card
does not make the judge more discriminating; it makes it abstain less.
THREE FURTHER QUALIFICATIONS, all from the audit:
  * MULTIPLICITY. RK-1b is the single positive in a twelve-test rubric family. Holm across that family puts its
    adjusted p at 0.352 (raw 0.0293); nothing in the family survives, which also dissolves J6's "first
    significant negative" (adjusted 0.473).
  * REPLICATION. RK-1b-GROK missed its own registered bar at p=0.073, and the rescue that pooled 57:29 across
    two judges pools two arms judged on THE SAME 944 matches, which are positively correlated by construction;
    halving for the dependence gives 28:15, p=0.066.
  * THE PASS/FAIL SPLIT IS A CONTROL DRAW. Three byte-identical control arms exist across RK-1 and RK-1b:
    0.8676, 0.8581, 0.8591 (between-session SD 0.52pp), against a treatment arm at 0.8750 in both. RK-1's FAIL
    and RK-1b's PASS differ by which control was drawn. Against the three-replicate control mean the honest
    estimate is +1.34pp.
HOW TO STATE IT IN THE PAPER: "+1.3pp against a three-replicate control (0.858-0.868), of which about 0.25pp is
better discrimination and about 1.1pp is reduced abstention; Holm-adjusted p = 0.35 across the rubric family;
replication on a second judge family missed its bar at p = 0.073."
AND THE CONSEQUENCE THAT MATTERS MORE THAN THE RESTATEMENT: if the card's value is that the judge abstains less,
then AGGREGATE's replicate tie-break does the same job far better - it resolves two thirds of ties at 0.75-0.86
accuracy for +8.0pp, at about 16% more calls. The card and the tie-break are SUBSTITUTES, not complements, and
the tie-break is the one to ship. This is the central argument for cancelling ARENA-V3.

- **RUBRIC-STRATA (2026-09-14, EXPLORATORY, post-hoc, zero calls): the data card acts ONLY where the reference
  is already right, and does exactly nothing where it fails.** Stratifying the cached RK-1b verdicts by whether
  the reference was correct on that question:
      judge     stratum             n     no card   + card    delta    discordant   McNemar p
      Mistral   reference CORRECT   817    0.930     0.950    +0.020     10:26        0.011
      Mistral   reference WRONG     127    0.394     0.394    +0.000      6:6         1.000
      grok      reference CORRECT   817    0.936     0.951    +0.015      7:19        0.029
      grok      reference WRONG     127    0.354     0.354    +0.000      6:6         1.000
  THIS REFUTES THE HYPOTHESIS IT WAS BUILT TO TEST. I expected the opposite: that the rubric line came back null
  because the effect was DILUTED by the ~86% of matches the reference decides correctly, and that concentrating
  on the hard residual would reveal it. The dilution story is wrong. The rubric is not diluted by the
  reference-correct majority, it is ENABLED by it, and on the stratum where the judge is at 0.35-0.39 and most
  needs help it contributes nothing at all - on both judge families, with identical 6:6 discordance.
  WHAT IT MEANS, and it follows directly from the displacement result: a rubric is INSTRUCTIONS FOR REASONING,
  and FORMAT-REF showed that a judge's own reasoning is largely switched off once a reference is present
  (weight on correctness -0.560 when a reference is shown). Where the reference is right, the judge is
  transcribing something correct and a rubric can sharpen HOW it transcribes - worth +1.5 to +2.0pp. Where the
  reference is wrong, the judge is transcribing something wrong, and instructions for reasoning have nothing to
  act on because the reasoning is not running. A rubric cannot substitute for a reference; it can only improve
  the use of one that already works.
  CONSEQUENCE FOR THE "SPECIFIC JUDGES" LINE. The plan was to push cell-specific judges onto HARDER questions,
  on the theory that saturation was hiding the effect. This says harder questions would make it WORSE, not
  better: harder questions mean a less accurate reference, and the rubric's value is conditional on reference
  correctness. The lever that the evidence supports for a domain-specific judge is not domain-specific PROSE,
  it is a domain-specific REFERENCE - and, where one exists, a domain-specific CHECKER (GEN-ARENA: MATH 0.935
  with an exact verifier).
  STATUS: post-hoc stratification of cached verdicts, not registered in advance, and UNDERPOWERED on the stratum
  that carries the claim - n=127 with a discordance rate of ~0.09 gives a minimum detectable effect of about
  5.4pp, so a real 5pp rubric effect on reference-wrong matches would be invisible here. It is a hypothesis with
  a number attached, not a result. REF-GATED-RUBRIC below is the confirmation.
  Output experiment_results/x12_crossdomain/rubric_strata.txt.

## Registered 2026-09-14 (before any call) — REF-GATED-RUBRIC: is rubric value conditional on the reference being right?
RUBRIC-STRATA (post-hoc, above) found the data card worth +1.5 to +2.0pp where the reference is correct and
exactly 0.000 where it is wrong, on both judge families - but at n=127 on the stratum that carries the claim,
where the minimum detectable effect is ~5.4pp. This tests it properly, and it is the sharpest remaining question
in the rubric line: not "do rubrics work" but "WHEN can a rubric act at all".
DESIGN. A 2x2 run fresh in one session, because the audit showed the RK-1/RK-1b PASS-FAIL split was a control
draw across sessions and mixing a fresh arm with a cached one repeats that mistake.
  STRATUM A, reference WRONG: 900 matches drawn from the 7,691 answer-disagreeing, key-decidable pairs on the
    481 pool questions where the grok reference is wrong.
  STRATUM B, reference CORRECT: 900 matches drawn the same way from reference-correct questions.
  ARMS, within each stratum and paired on the same matches: the deployed anchor rubric alone, and the anchor
    rubric plus the RK-1b data-only leaf card of the question's routed leaf.
  Judge grok-4-1-fast-non-reasoning, v2 mechanics, the reasoning reference, SINGLE order - position is constant
  across the two rubric arms, so it cancels in the paired contrast, and LEAF-POWERED used the same economy.
  1,800 matches, 3,600 calls.
REGISTERED. (1) PRIMARY, the INTERACTION: the card's paired effect in stratum B minus its effect in stratum A,
with a bootstrap CI over matches. The claim is confirmed if that difference is positive with a CI excluding
zero. (2) Stratum A alone against zero, with its McNemar - the claim needs this to be null AT ADEQUATE POWER,
which n=900 provides (MDE ~2.2pp at a 0.09 discordance rate, ~3.5pp at 0.20). (3) Stratum B alone, as a
replication of RK-1b's +1.3 to +1.7pp on a fresh sample and a fresh session. (4) DECISIVENESS SPLIT, required
by the standing rule: decisive-and-correct and correct-given-committed reported separately for all four cells,
since RK-1b's headline turned out to be ~86% abstention reduction.
PREDICTIONS: interaction +1.5 to +3pp with a CI excluding zero; stratum A within +-1pp of zero; stratum B
reproduces +1.0 to +2.0pp; and the card's effect in stratum B is again mostly decisiveness rather than
discrimination.
IF THE INTERACTION IS NULL, then RUBRIC-STRATA was noise, the card's value is unconditional and small, and the
rubric line stays closed exactly where it was. IF IT IS CONFIRMED, the line does not reopen - it is REDIRECTED:
a cell-specific judge should mean a cell-specific REFERENCE (or checker), with rubric text as a second-order
sharpener that only pays where the reference already works. That is a more useful conclusion than either a
positive or a negative on rubrics alone, and it is the one the "specific judges" idea has been missing.
Output experiment_results/x12_crossdomain/refgated_outcome.txt; cache refgated.db;
script tools/analysis/ref_gated_rubric.py.

- **REF-GATED-RUBRIC OUTCOME (2026-09-14): the registered interaction FAILS, both cells individually reproduce
  RUBRIC-STRATA, and the failure is my sampling error rather than a property of the world.** 3,594 calls, 0 errors.
      stratum       n     no card   + card   delta   discordant   McNemar p   ties         committed
      ref_correct  900     0.969     0.982   +0.013     3:15       0.0075    .010 -> .006  .979 -> .988
      ref_wrong    899     0.389     0.389   +0.000    40:40       1.000     .101 -> .103  .433 -> .434
  (1) PRIMARY, the interaction: +0.013, bootstrap 95% CI [-0.008, +0.036] - NOT CONFIRMED.
  (2) STRATUM A IS NOW DEFINITIVELY NULL AT GOOD POWER, which is the half that matters: 40:40 discordant on 899
      matches. The card moves 80 verdicts where the reference is wrong and they cancel exactly. At a 0.089
      discordance rate the minimum detectable effect is about 2.0pp, so anything at or above that would have
      shown. The underpowered +0.000 at n=127 in RUBRIC-STRATA was not a fluke.
  (3) STRATUM B REPLICATES RK-1b on a fresh sample in a fresh session: +1.3pp, 3:15, p=0.0075. That is worth
      having on its own, because the ledger audit showed the original RK-1b PASS depended on which of three
      byte-identical control sessions was drawn. This is a clean independent replication of the effect size.
  (4) AND HERE THE CARD IS DISCRIMINATION, NOT DECISIVENESS - the opposite of the RK-1b anatomy. Ties are already
      at 1.0% in this stratum and barely move; correct-given-committed goes 0.979 to 0.988, so about 0.9pp of the
      1.3pp is better judging. On the reference-wrong stratum neither number moves at all.
  WHY THE INTERACTION FAILED, and it is a sampling error of mine rather than a property of the world. I drew both
  strata from ANSWER-DISAGREEING pairs, because that is the shipped scheduler rule. The RUBRIC-STRATA strata were
  not filtered that way. Filtering to disagreeing AND reference-correct selects the easiest matches in the pool:
  baseline accuracy is 0.969 here against 0.930 there, leaving 3.1pp of headroom for the card to work in. An
  interaction is a difference of two effects and carries the variance of both, so with one effect squeezed into a
  3pp ceiling the CI was never going to exclude zero. THE REGISTRATION SHOULD HAVE CAUGHT THIS: it inherited a
  population from the shipped filter and compared the result against an estimate taken from an unfiltered one -
  the same population-mismatch class the ledger audit flagged as C-6, committed in a registration written hours
  after recording that very finding.
  WHAT STANDS. The directional claim survives on its components rather than on the registered test: the card is
  worth +1.3pp where the reference is right (p=0.0075, replicated) and exactly nothing where it is wrong (40:40
  at about 2pp resolution). The design conclusion is unchanged and now rests on a null measured at adequate power
  instead of one measured at n=127 - a rubric cannot substitute for a reference, it can only improve the use of
  one that already works - but the formal interaction is unconfirmed and must be quoted as such.
  THE CLEAN RERUN, if it is ever worth 3,600 more calls: draw the reference-correct stratum WITHOUT the
  answer-disagreement filter, so both cells have comparable headroom. I would not spend it - the two component
  results already say what the design needs.
  Output experiment_results/x12_crossdomain/refgated_outcome.txt; script tools/analysis/ref_gated_rubric.py.
