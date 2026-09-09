# S1 / L1 — judge tests registered 2026-09-09 (before any call)

Both reuse the R2 / x12 verdict exports and the Foundry deployments (Mistral-Large-3,
grok-4-1-fast-non-reasoning, grok-4-1-fast-reasoning). Neither touches construction or
the reserved pool's DB flag; questions are addressed by eval id from the campaign exports.

## S1 — judge solve-rate map (ceiling map)
Universe: the 2,812 distinct reserved questions judged in x12 MAIN (the domain of the
rubric-value contrast). Each judge answers each question ONCE, no traces: question stem +
lettered options, "output JSON {"answer": "<letter>"}", default temperature; correctness
vs the key (eval_results.gt_answer). Cache experiment_results/judge_solve/<judge>.db.
Readouts: judge accuracy per anchor (primary leaf's anchor from
reserved_leaf_assignments.csv); contestant mean accuracy per anchor (the 12 arena
models); CEILING MAP = judge − contestant accuracy per anchor per judge.
REGISTERED PRIMARY: over the 14 anchors, Mistral's cell-over-generic rubric gain
(rubric_value_contrast: key-decidable correct-verdict rate, cell minus generic, per
anchor) correlates NEGATIVELY with Mistral's own solve accuracy — Spearman rho < 0,
permutation p < 0.05 (14 points; low power acknowledged; rho >= 0 falsifies "rubric gain
tracks judge weakness").
SECONDARY: J1's per-anchor accuracy gain (reasoning − Mistral, all key-decidable R3
matches) correlates POSITIVELY with the per-anchor solve-rate gap (reasoning − Mistral):
rho > 0, p < 0.05.
Predictions: primary rho ≈ −0.5; secondary rho > +0.5; Mistral's solve accuracy is below
the top-4 contestants' in every anchor; grok-reasoning's is above gpt-4o's in most.
Also produces J2's synthetic reference for free (the same call).

## L1 — causal length test
Matches: R2 live top-4, key-decidable, where the CORRECT answer is longer by >= 300
chars (n = 361, 276 questions). Judge: Mistral-Large-3, byte-identical v1 prompts, dual
order, all arms in the same session (the ORIGINAL arm is re-judged, not reused).
Arms: ORIGINAL; TRUNCATE — the correct answer's model_output cut at the last sentence
boundary at or before the wrong answer's length, BEFORE the RESOLVED "[This model's
selected answer ...]" line is appended (the explicit final answer is preserved);
PAD — the wrong answer padded to the correct answer's length with a content-free filler
paragraph (fixed text, no reference to the question, repeated as needed).
REGISTERED PRIMARY: correct-verdict rate (ties wrong) ORIGINAL > TRUNCATE, paired
McNemar p < 0.05, predicted drop >= 10 points. SECONDARY: ORIGINAL > PAD, p < 0.05,
predicted drop >= 5 points. Interpretation rule stated now: TRUNCATE conflates
"elaboration rewarded" with "reasoning evidence removed"; PAD isolates pure length. If
TRUNCATE drops and PAD does not, the judge rewards CONTENT length (reasoning steps), which
is defensible; if PAD drops, the judge rewards bytes, which is not. Cost: 361 x 6 =
2,166 calls. A grok-reasoning replication of the arm that moves is queued as descriptive.

## Launched 2026-09-09 (after S1/L1), recorded before the first call
- **J2 launch record**: judge Mistral-Large-3, R3's 1,980 matches, v1 prompts byte-identical
  except the question block gains "[Reference solution — produced independently, may be
  wrong]\n(<letter>) <option text>", where the letter is Mistral's OWN S1 answer (a separate
  call that never saw the traces; correct 66.3% overall, ~52% in Math). No-reference arm =
  the x12 MAIN verdict on the same match (as J1). Criteria as registered in
  docs/judge_improvement_proposals.md J2: gain > 0 at p < 0.05 on all key-decidable pairs
  AND net-positive across the reference-correct / reference-wrong strata; both strata
  reported. Prediction (from L1): the judge verifies rather than counts steps when a
  reference is present — gain >= +5pp on all decidable, larger in quantitative anchors;
  reference-wrong stratum loses (the named pitfall) but less than reference-correct gains.
  Harness tools/analysis/rejudge_reference.py, cache rejudge_mistral_reference.db.
- **L1-R (descriptive)**: the three L1 arms replicated on grok-4-1-fast-reasoning
  (same 361 matches). Prediction: a judge that can solve the question (85.6%) resists
  truncation — drop < 15 points vs Mistral's 51.
- **PROMOTED builds** (not tests): bareq512_s42 and abt2d512_s42 — the frozen mcs=55
  recipe (labeling + rubric induction ON, seed 42) on the FROZEN split (splitSeed 42 →
  pool p2dca21ab5f4ef3ae) at the D2 geometries; reserved pool routed through each
  (experiment_results/promoted/<tag>_reserved_leaf_assignments.csv). bareq512_s42 is the
  profile tree to carry forward; abt2d512_s42 is the certified-leaf ladder's instrument.
  Configs experiment_configs/promoted/.

## OUTCOMES

- **L1-R (2026-09-09, descriptive): the reasoning judge is hurt less by truncation and is
  NOT fooled by padding — it penalises it.** grok-4-1-fast-reasoning, same 361 matches (355
  complete triples): original vs TRUNCATE drop 0.303 (112:5, p < 1e-4) vs Mistral's 0.507 —
  a judge that can solve the question still leans on shown reasoning, but half as much;
  original vs PAD drop −0.037 (3:16, p = 0.004): padding the WRONG answer with filler made
  the reasoning judge pick the correct one MORE often — it reads filler as a negative
  signal, where Mistral was indifferent. Prediction (drop < 15 points) was wrong on the
  magnitude, right on the direction. Cache experiment_results/causal_length/grok-reasoning.db.

- **S1 (2026-09-09): PRIMARY FAILS — significantly in the OPPOSITE direction; SECONDARY
  FAILS (null). The ceiling map itself is the durable result.** 2,796 questions solved
  by all three judges (11 identical request rejections; caches experiment_results/
  judge_solve/<judge>.db, output s1_outcome.txt). Overall solve accuracy: Mistral
  0.663, grok non-reasoning 0.579, grok-reasoning 0.856; top-4 contestants 0.70–0.90 per
  anchor. Mistral is BELOW the top-4 contestants' accuracy in 14/14 anchors (worst gaps:
  Math 0.52 vs 0.90, Business 0.55 vs 0.90, Physics 0.67 vs 0.86); grok-reasoning is at
  or above them in the quantitative anchors (Math 0.95, Physics 0.92, Business 0.95,
  Chemistry 0.88) and slightly below in the discursive ones (History, Philosophy,
  Psychology, Other). This is the ceiling J1 measured, seen directly: a judge weaker
  than the contestants on the question itself.
  PRIMARY: Mistral's per-anchor rubric gain vs its own solve accuracy: rho = +0.516,
  perm p = 0.032 — rubric gain is LARGEST where Mistral solves BEST (Philosophy +6.0pp
  at 0.67, Biology +5.4 at 0.86, History +3.5, Economics +2.7, Health +2.2) and ~0 where
  it solves worst (Math +1.3 at 0.52, Engineering 0.0, Chemistry −0.9, Business +0.6).
  "Rubric gain tracks judge weakness" is falsified; the earlier exploratory reading
  (rubric_value_contrast, 2026-09-06: "gain concentrates in qualitative domains,
  tracks judge weakness") had the domains right and the mechanism wrong. Reading that
  fits L1 and J1: a rubric is a checklist for applying knowledge the judge has; where
  the judge cannot solve the question (quantitative anchors) no checklist helps, and
  where it can, the checklist sharpens the verdict. Prediction rho ≈ −0.5 was wrong.
  SECONDARY: J1's per-anchor accuracy gain vs the reasoning−Mistral solve gap:
  rho = −0.125, p = 0.33 — the reasoning judge's advantage is not proportional to its
  solve advantage per anchor (14 points, noisy; the R3 sample is stratified by pair,
  not by anchor). Prediction wrong.
  Consequences: (i) rubric induction should be expected to pay off in discursive
  anchors and not in quantitative ones under a non-reasoning judge — a testable, and
  now specific, scope statement for the paper; (ii) in quantitative anchors the lever
  is judge capability (J1) or a verified reference (J2), for which these solve calls
  are the synthetic reference (Mistral's own reference would be wrong ~45% of the time
  in Math — the pitfall the J2 registration names); (iii) the caches double as a
  per-question "judge can solve it" covariate for every past verdict.

- **L1 (2026-09-09): PRIMARY PASS, SECONDARY FAIL — by the interpretation rule stated
  above, the judge rewards CONTENT length (reasoning steps), not bytes.** 359 matches
  with all three arms (6 request rejections), Mistral-Large-3, same session, dual order,
  cache experiment_results/causal_length/mistral.db, output l1_outcome.txt.
  Correct-verdict rate: original 0.766 (correct answer 1,821 chars vs wrong 840);
  TRUNCATE 0.259 (correct cut to 770 chars) — drop 0.507, discordant 183:1, p < 1e-4;
  PAD 0.769 (wrong padded to 2,013 chars with content-free filler) — drop −0.003,
  10:11, p = 1.0. Reading: adding filler to the wrong answer changes nothing; removing
  the correct answer's reasoning steps (its explicit final answer is still stated)
  flips half the verdicts to the wrong answer. So the "verbosity bias" measured
  observationally (beta_len +0.39/1k globally, +1.32 within the top cluster) is
  elaboration-as-evidence: the judge cannot verify a terse correct answer on its own
  and treats demonstrated reasoning as the correctness signal — which is exactly the
  capability-ceiling mechanism J1 established (a judge that can solve the question
  needs fewer steps shown). Defensible as judging behaviour, but it over-rates verbose
  models against the key. Consequences: (i) the prompt fix J3 targets the wrong lever
  if it asks the judge to "ignore length" — it should ask the judge to VERIFY the final
  answer (J2's synthetic reference is the mechanism); (ii) the length-matched refits and
  the confidence-gated board are corrections for a real judging limitation, not for a
  stylistic preference; (iii) queued descriptive: the TRUNCATE arm on grok-reasoning
  (does a judge that can solve the question survive truncation?).
