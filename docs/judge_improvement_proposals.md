# Judge improvement proposals (J-series) — 2026-09-08

Scope: the judge itself — which model judges, what it is told, what the rubric induction
sees. Companion to docs/v2_construction_proposals.md (structure) and the D1 sweep
(geometry). Nothing here is launched; each item carries a registrable test that reuses
the existing harnesses (rejudge_grok.py-style re-judge on the x12 key-decidable subset,
paired McNemar; BT refits via refit_bt_from_matches.py; bias_audit.py).

## What is settled and constrains every proposal

- Judge = Mistral-Large-3, non-reasoning; the same model induces every rubric. Second
  judge grok-4-1-fast-non-reasoning agrees 97.8% on decisive verdicts.
- Cell rubrics beat generic (McNemar p = 0.0001, +1.5pp key-decidable; grok +2.4pp) and
  beat wrong-cell rubrics (p = 0.006); the gain concentrates where the judge is WEAK.
  Anchor-level rubrics match leaf-level (ladder, p = 0.68).
- Verbosity: beta_len = +0.39 / 1k chars in both judge families; an explicit
  "ignore length" clause did nothing (H7). Length-matched refits move the top cluster
  toward ground truth in x12 and R2.
- The top-cluster divergence (gemini / gpt-4o / iask vs GT) is a stable judge-level
  property (R2, 36,871 verdicts), not sampling.
- Prompt as shipped (TaxonomyArenaService.buildJudgeSystemPrompt): forbids TIE when both
  answers are correct and ranks them by "mechanistic depth, edge-case handling,
  quantitative precision, scope accuracy"; a Kotlin comment block is embedded in the
  string literal and reaches the judge; swap-disagreement is forced to TIE at conf 0.5.
- Rubric induction sees: every non-reserved train question in the node, all options with
  the correct one marked, and the reference chain-of-thought. It never sees a model
  answer. (Response-blind, key-informed.)
- Verdict exports keep the per-order votes (WinAFirst / WinASecond) for every LIVE verdict:
  R2 27,657 of 36,892 (the 9,235 resumed rows lost them); x12 3,184 of 9,154.

## Literature anchors (verify ids before citing; several are 2026 preprints)

- Capability ceiling: JudgeBench (Tan et al., ICLR 2025, 2410.12784) — "the judge's
  accuracy closely mirrors that of the solver"; GPT-4o 56.6% on correctness pairs,
  reasoning judges 75–81%. Fine-tuned small judges fall below chance.
- Independent synthetic reference: MT-Bench (Zheng et al., 2306.05685) — judge solves
  the question in a SEPARATE call, answer inserted as reference: math-judging failures
  70% -> 15%. Naive "answer then grade" in one call repeats the contestant's error.
- Rubric context: Rethinking Rubric Generation (Shen et al., 2602.05125) — rubrics
  generated from the question alone score BELOW no-rubric on JudgeBench (42.9 vs 55.6);
  rubrics generated with responses in view 66.8; decomposed + filtered 73.3.
  Rubrics-as-Rewards (2507.17746): reference-informed rubrics help small judges most.
- Order handling: Soumik (2604.23178) — swap-with-tie-on-disagreement HURTS by 3–13pp
  because it discards correct verdicts; aggregate both orders as evidence instead.
- Length: LC-AlpacaEval (Dubois et al., 2404.04475) — post-hoc regression on length
  difference, Spearman with Arena 0.94 -> 0.98; prompt-level mitigations "fail to
  generalize" (2602.01528). No paper isolates a positive "ignore length" instruction.
- CoT before verdict: not a free win for pairwise (Wang, Zhang & Choi, 2503.03064 —
  collapses the verdict distribution); explicit criteria matter more than CoT
  (Yamauchi et al., 2506.13639).
- Panels: PoLL (2404.18796) helps, but a 9-frontier panel carries ~2 independent votes
  and the best single judge matches it (Kohli, 2605.29800).
- Audit: CALM (Ye et al., ICLR 2025, 2410.02736) perturbation suite; Cohen's kappa,
  not raw agreement (Thakur et al., 2406.12624). "Correct Looks Better" (2606.09409):
  MMLU-Pro-style pairwise-without-key recovers accuracy rank rho > 0.9; bias lives in
  the ~60% non-discriminative (both-right / both-wrong) pairs.

## Proposals, ranked by expected value per judge call

### J5 — Order aggregation instead of forced ties  (0 judge calls)
Refit BT from the two per-order votes as two half-weight observations (or a
position-covariate BT) instead of collapsing disagreement to TIE. Data already exist
for 27,657 R2 verdicts. Why it ranks first: 69% of R2's ties (5,055 / 7,311) are
POSITION_FLIP ties, and ties are densest exactly in the top cluster where the
divergence lives; the literature says this rule costs 3–13pp.
REGISTERED: on the R2 live subset, rho(BT, GT) and the top-4 order under order-
aggregated BT vs the current TIE rule; PASS iff rho does not fall and the number of
top-cluster GT-order violations does not rise. Descriptive: position-bias coefficient
per model pair (does the flip rate track the quality gap, as 2406.07791 predicts?).

### J4 — Length-covariate BT board  (0 judge calls)
The LC-AlpacaEval move, on our own verdicts: fit BT with a per-match length-difference
covariate and report strengths at delta-length = 0. Already named as the open
mitigation in the verbosity memo; this registers it. Includes sweeping the 300-char
matching threshold that has been post-hoc since 2026-09-07.
REGISTERED: top-4 order under LC-BT vs GT in x12 AND R2 (two datasets, pre-stated:
gemini > arx > iask > gpt-4o is GT); PASS iff LC-BT has <= 1 adjacent violation in
both and beta_len on the residual is within CI of 0.

### J1 — Judge-strength ceiling test  (~4k calls)
Re-judge the 1,980-match stratified x12 sample (the R3 design, byte-identical prompts)
with a reasoning-class judge from the existing Foundry catalog (grok-4 reasoning,
DeepSeek-R1, or an o-series deployment — whichever is sold-direct/CSP-compatible like
grok was). JudgeBench predicts the biggest gain where the contestants are at or above
the judge, which is precisely the frontier top cluster.
REGISTERED PRIMARY: key-decidable accuracy on the top-cluster pairs (gemini / gpt-4o /
iask / arx) — reasoning judge > Mistral by McNemar p < 0.05. SECONDARY: the
top-cluster BT order under the reasoning judge has fewer GT violations than Mistral's.
Falsifier: no accuracy gain on top-cluster pairs => the divergence is not a
capability ceiling but a shared preference (verbosity/style), and J3/J4 carry it.

### J3 — Prompt v2: correctness-first tie policy + hygiene  (~2k calls)
The four "both-correct" ranking criteria are elaboration proxies; H7 added an
ignore-length clause ON TOP of them and measured nothing, which is consistent with the
criteria, not the clause, driving beta_len. v2: (i) when both final answers are
correct, TIE is allowed and the tie-break is "fewer errors or unsupported steps in the
reasoning", never depth/scope; (ii) remove the embedded Kotlin comment; (iii) keep
everything else byte-identical. v1 stays available — rejudge_grok.py asserts the v1
text, so v2 must be a versioned template, not an edit.
REGISTERED: paired re-judge of the H7 enriched sample; PRIMARY beta_len(v2) < beta_len(v1)
with non-overlapping CIs; GUARD key-decidable accuracy(v2) >= accuracy(v1) - 0.5pp.
Prediction: partial reduction (not to zero — the literature says prompt fixes do not
remove the bias, only the part the prompt was actively creating).

### J2 — Independent synthetic reference (solve-then-judge)  (~3.6k + ~4k calls)
Keep the key-less premise: the judge model solves each reserved question in a separate
call (no traces in context); its answer is inserted as "[Reference solution — may be
wrong]". MT-Bench's 70% -> 15% failure reduction is the largest single effect in the
scan. Because the key exists for MMLU-Pro, the reference's own accuracy is measurable,
which turns the known pitfall (a wrong reference flips the verdict) into a named
covariate: accuracy of verdicts conditional on reference-correct vs reference-wrong.
REGISTERED: key-decidable accuracy with reference vs without, paired McNemar, on the
x12 stratified sample; PASS iff gain > 0 at p < 0.05 AND the reference-wrong stratum
does not fall below the no-reference baseline by more than the reference-correct
stratum gains (net-positive by construction, reported separately). Descriptive: does
the gain concentrate in quantitative anchors (Math / Physics / Chemistry / Engineering)?

### J6 — Contrastive, frontier-induced rubrics  (induction + ~4k calls)
Two changes to what induction sees, tested separately then together:
(a) INDUCTION MODEL: decouple `inductionModel` from `judgeModel` (one config knob;
today both are judgeModel). Induce the 14 anchor rubrics (ladder says anchor
granularity carries the value) with a frontier reasoning model; judge with Mistral.
(b) CONTRASTIVE CORPUS: the eval DB holds 15 models' answers for every train question;
add, per node, a sample of WRONG train-side answers (key-labelled) alongside the
reference CoT, and ask for rules that discriminate them ("what wrong reasoning in this
cell looks like"). This is the response-in-view rubric of 2602.05125 without touching
reserved questions or contestant traces on reserved items.
REGISTERED (each arm vs current cell rubric, paired key-decidable McNemar on the x12
sample): PASS iff +1pp or more at p < 0.05; the rubric-leakage audit (shared n-gram
>= 5 with correct options) must stay clean. Prediction: (b) > (a); (a) alone is small
because the ladder shows rubric CONTENT (domain-correct) matters more than authorship.

### J7 — Verdict sampling instead of greedy  (3x calls on a sample)
Three samples at T = 0.7 per order, majority or mean; the literature says the
distribution beats the mode for pairwise. Cheap to pilot on 500 matches; promote only
if key-decidable accuracy rises >= 1pp. Lowest priority: the gain is reported as
consistent but small, and it triples cost.

### J9 — Audit protocol (analysis only)
Adopt for every judge condition: Cohen's kappa against the key on decidable pairs (not
raw agreement); CALM-style perturbations (verbosity padding, authority/citation
insertion, sentiment) on 300 matched pairs; and a NON-DISCRIMINATIVE-pair audit —
both-correct pairs (8,264 in R2) are where the verdict cannot be right or wrong, so the
verdict rate there IS the bias signature. Extends tools/analysis/bias_audit.py.

## Recommended order
J5 and J4 first (free, both refits, and they may already explain most of the
top-cluster divergence). Then J1 (settles ceiling vs preference). Then J3 as prompt
v2. J2 and J6 are the two content changes and are the ones that can raise the
rubric's value beyond +1.5pp; J2 is the bigger literature effect, J6 is the one that
keeps the thesis's induced-rubric story. J7 last. J9 runs on every arm.

## Interaction with the thesis claims
- Nothing here changes the arena's ranking of the mid/low tiers (rho 0.95, replicated
  4x). The target is the frontier top cluster and the size of the rubric effect.
- J5/J4 are measurement-side and would be reported as corrected boards alongside the
  raw ones, not as replacements of the registered results.
- J6(b) reframes "what the taxonomy gives the judge": not just similar questions but
  the cell's characteristic failure modes — the granularity argument restated in
  functional terms (a cell is worth its own rubric iff its failure modes differ from
  its parent's), which is the same functional-validation criterion the ladder applies.
