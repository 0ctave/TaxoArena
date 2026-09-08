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

J1 LAUNCH PARAMETERS (recorded 2026-09-08 before the first judged call): judge =
deepseek-ai/DeepSeek-R1-0528 via the Hugging Face inference router (no reasoning model
is deployed on the Foundry resource; Gemini key not API-registered), max_tokens 8192,
default temperature, <think> stripped before parsing; sample = the R3 1,980 matches
(rejudge_grok.sample_matches, seed 42), prompts = v1 templates byte-identical to R3;
harness tools/analysis/rejudge_reasoning.py, cache experiment_results/x12_crossdomain/
rejudge_r1.db. Family disclosure: deepseek-chat-v2_5 is a mid-tier contestant; no top-4
model is DeepSeek, so the primary is not self-preference-confounded; the all-pairs and
full-board readouts carry the caveat. Pilot of 12 matches precedes the full run.

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

## OUTCOMES

- **J5 (2026-09-08, harness 3254c96, output experiment_results/judge_free_tests_output.txt):
  PASS on the letter, NULL in substance.** On R2 (27,657 live verdicts) the order-aggregated
  board is IDENTICAL to the forced-tie board: rho 0.9510 both, same top-4 order, same 3
  pairwise violations; paired bootstrap of the rho difference [+0.000, +0.007]. x12
  (secondary) moves within noise (-0.001, CI straddles 0). Reason, obvious in hindsight:
  under BT with ties scored 1/2, a position flip (one order A, the other B) contributes
  exactly 1/2 either way, so the two rules coincide except on the ~4% of matches where
  one order emitted a tie. The literature effect (3-13pp) is about single-verdict
  accuracy, not about the aggregated board; J5's expected value was mis-ranked and is
  withdrawn as a board correction. Descriptives that DO stand: position inconsistency is
  19-28% for GT gaps < 0.20 and 7% for larger gaps (tracks the quality gap, as
  2406.07791 predicts); pooled over both orders the first-shown answer wins 44.9% of
  decisive single-order votes (n = 52,919) — a 5pp preference for the SECOND position,
  already neutralised by the dual-order protocol. The raw WinAFirst skew is the
  scheduler: ModelA is the GT-weaker model in 66.5% of R2 matches.
- **J4 (same run): registered letter PASS but non-discriminating; the informative
  result is post-hoc and labelled so.** Global LC-BT: beta_len = +0.082/1k (z = 6.0) on
  R2, +0.135 (z = 4.4) on x12; the R2 top-4 board is UNCHANGED by the covariate
  (iask > gemini > gpt-4o > arx, 3 violations — the raw board also has <= 1 ADJACENT
  violation, so the registered clause cannot separate them; adjacent-violation count
  was the wrong metric and pairwise violations are reported alongside). x12's LC board
  does move to gemini > iask > arx > gpt-4o (1 violation, rho 0.965 -> 0.979). The
  matching-threshold sweep: 100/200/300 chars give gemini > iask > arx > gpt-4o on both
  datasets; 500/800 revert R2 to iask first — 300 was not special, but the matched order
  is stable below it. EXPLORATORY (post-hoc, `--top4`): fitting LC-BT on top-4 matches
  only gives beta_len = +1.32/1k (z = 26.4, n = 6,094) on R2 and +0.88 (z = 9.7) on x12 —
  16x and 6x the global coefficient — and the within-cluster LC board is
  gemini > iask > arx > gpt-4o on BOTH datasets (1 violation each), reproducing the
  length-matched refit without discarding data. Mean answer lengths on those matches:
  gemini 861 / arx 881 chars (under-rated) vs iask 1,301 / gpt-4o 1,519 (over-rated).
  Interpretation: the length effect is HETEROGENEOUS — negligible where correctness
  separates the pair, dominant where it saturates. A single global length covariate
  cannot correct the board; the LC design that can is one whose length coefficient
  varies with the pair's quality gap (or with both-correct status).
  REGISTERED FOLLOW-UP (J4b, to be frozen before running): LC-BT with beta_len
  interacted with the GT-gap tier (< 0.10 / >= 0.10), primary = pairwise violations of
  the 12-model board vs GT strictly below the raw board's on BOTH datasets, secondary =
  top-4 order gemini > arx > iask > gpt-4o or one adjacent swap. Prediction: the
  interaction coefficient for the narrow tier is > 5x the wide tier's, and the top-4
  order becomes gemini > iask > arx > gpt-4o (the remaining iask/arx swap is a 1.7pp
  GT gap the pool cannot resolve at SE 0.15).

- **J4b (2026-09-08, registered e840c8f, run immediately after): PRIMARY PASS, secondary
  half.** beta_narrow (GT gap < 0.10) = +0.447/1k (z = 13.7, n = 10,503) vs beta_wide =
  -0.036 (z = -2.2) on R2; +0.279 (z = 5.3) vs +0.046 (z = 1.2) on x12 — the predicted
  > 5x ratio holds. 12-model board pairwise violations vs GT: R2 5 -> 4, x12 4 -> 3
  (rho 0.951 -> 0.958, 0.965 -> 0.979). Secondary: x12's top-4 becomes
  gemini > iask > arx > gpt-4o (one adjacent swap from GT — met); R2's top-4 is
  unchanged (iask > gemini > gpt-4o > arx — NOT met, prediction wrong there). Why the
  tier proxy is insufficient: gemini-vs-gpt-4o has a GT gap of 0.163 and lands in the
  "wide" tier where the coefficient is ~0, yet it is exactly the verbose-vs-terse pair
  the within-cluster fit (beta 1.32) says length dominates. Gap tier is a proxy for
  "correctness does not separate the pair"; the key labels that per MATCH.
  REGISTERED J4c (frozen here before running; the LAST free variant — further variants
  need judge calls, not more refits): LC-BT with beta_len interacted with the match's
  key status — NON-DISCRIMINATIVE (both correct or both wrong) vs DECIDABLE. Primary =
  12-model pairwise violations vs GT strictly below raw on BOTH datasets (same as J4b);
  secondary = R2 top-4 within one adjacent swap of GT. Prediction: beta_nondisc >>
  beta_decidable (the 2606.09409 "bias lives in non-discriminative pairs" claim), and
  the R2 top-4 puts gemini first. If the secondary still fails, the top-cluster
  divergence has a component that is not length, and J1 (judge strength) is the test.

- **J4c (2026-09-08, registered d024f0f): FAIL on both registered clauses.** beta_nondisc =
  +0.162/1k (z = 7.3, n = 13,349) vs beta_decidable = +0.028 (z = 1.6) on R2 (5.7x —
  the DIRECTION of the 2606.09409 claim holds), +0.282 vs +0.095 on x12; but R2's
  12-model board is unchanged (5 violations, rho 0.951) and its top-4 is unchanged.
  x12 improves as in J4b (4 -> 3, gemini first). Reading across J4/J4b/J4c: the
  non-discriminative coefficient (+0.16) is far below the top-4-only coefficient
  (+1.32), so "both correct" is NOT the regime in which length dominates — the frontier
  cluster is its own regime (weak-model both-wrong pairs are non-discriminative too and
  dilute the tier). No global or tiered length covariate corrects R2's top cluster; only
  a model fitted within the cluster does, which is a per-tier board, not a correction.
  The free-refit line is CLOSED here (3 registered variants, all reported): the
  measurement-side mitigation is a per-tier length term reported as a corrected board
  alongside the raw one, and the substantive fixes are design-level — J3 (remove the
  elaboration criteria that reward length when both are correct) and J1 (a judge whose
  correctness signal does not saturate on the frontier). Both need judge calls.

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
