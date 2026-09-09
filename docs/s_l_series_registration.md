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

## OUTCOMES

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
