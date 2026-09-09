# Judge v2 program — every change paired with a bias metric and an accuracy metric (2026-09-09/10)

Goal (author's instruction 2026-09-09): improve the judge in every way possible, and make sure each
change actually mitigates the bias it targets and improves the judge. Rule of this document: a
change is adopted only if (a) its targeted bias metric moves in the right direction on a paired
test, (b) key-decidable accuracy does not fall, and (c) the final assembled judge (STACK) beats
the current production judge end-to-end on the board metrics. Everything below is registered
before its first call; outcomes are appended under each item.

## Bias catalogue, evidence, mitigation, test

| # | bias | measured on the production judge (Mistral-Large-3, v1 prompt) | mitigation | paired test | status |
|---|---|---|---|---|---|
| B1 | verbosity / elaboration-as-evidence | beta_len +0.39/1k chars (top cluster +1.32/1k); causal: truncating the correct answer's reasoning drops the correct-verdict rate 0.766 → 0.259 (L1); "ignore length" clause not followed (99.4% prefer the longer of a stub pair) | give the judge something to VERIFY against (reference); remove the both-correct depth criteria (v2 prompt) | J2/J2-R (done: +7.6pp), J3-R (running), **L1-V** (new), F7 confidence gate (done) | partly done |
| B2 | position | second-shown wins 55.1% of single-order votes; flips 9.7–12.8% | dual order + tie-on-flip (in place; J5 showed aggregation is not better) | flip rate and second-shown rate re-measured under v2 and under the reference (free, from the new caches) | free |
| B3 | reference-following (new bias introduced by B1's mitigation) | with a 66%-correct reference: ref-wrong stratum −7.1pp; with an 85.6% reference: −3.9pp (n.s.) | better reference; two references on disagreement | **J2-D** (new); gating by solver agreement is FALSIFIED for free (0.823 < 0.849, see below) | designed |
| B4 | rubric specificity | cell rubric = generic on the frozen tree's held-out pool (0.0pp); clean 512 tree +1.8pp at p=0.0498, session confound; wrong-cell rubric harms (contaminated evidence only) | anchor-level rubric instead of leaf (ladder: anchor = leaf) | RUBRIC-512-SS (running), RUBRIC-512-R (running), STACK uses the anchor rubric | running |
| B5 | format / style (markdown, LaTeX, lists) | not measured causally; observational prevalence below | none needed unless FORMAT shows an effect | **FORMAT** (new, conditional on prevalence) | designed |
| B6 | tie inflation on decidable pairs | 19.9% ties (Mistral), 13.2% (reasoning judge), 15.3% with reference; on key-decidable pairs a tie is an error | v2's tie policy must not raise the decidable tie rate | tie rate on key-decidable pairs is a GUARD in J3-R and STACK | running |
| B7 | judge capability ceiling | Mistral solves 66%, reasoning judge 86%; judge accuracy mirrors solver accuracy (J1 +12pp top cluster) | reasoning model as the REFERENCE generator (one call per question), cheap model as the judge | J2-R (done: equals the reasoning judge) | done |
| B8 | confidence miscalibration | AUC 0.752, ECE 0.039 (calibrated); beta_len peaks at 0.85–0.95 | keep the field; gate boards at ≥ 0.95 or weight by confidence | re-measure AUC/ECE under v2 and under the reference (free) | free |
| B9 | self-preference / family | no contestant shares a family with Mistral or xAI | none | — | n/a |

Free result recorded 2026-09-09 23:55 (J2-R cache, 944 decidable): when Mistral's and the
reasoning model's independent answers AGREE (63%), the reference is 92% correct and adds +8.1pp
(0.812 → 0.892); when they DISAGREE (37%), the reasoning reference is still 77% correct and adds
+6.9pp (0.705 → 0.774). Showing the reference only on agreement would score 0.823 < 0.849.
Consequence: never gate the reference away; improve the disagree stratum instead (J2-D).

## New registered tests

### L1-V — does the reference remove the elaboration vulnerability? (~2.2k Mistral calls)
L1's 359 top-cluster matches (correct answer longer by ≥ 300 chars), same three arms (original,
truncate, pad), same session, Mistral, v1 prompt, but the question carries the reasoning
reference exactly as in J2-R. Harness: `causal_length.py --reference grok-reasoning`, cache
experiment_results/causal_length/mistral_refgrok.db.
REGISTERED PRIMARY: the truncation drop with the reference is less than HALF of L1's (−0.507),
i.e. drop ≤ 0.25, AND the truncate-arm correct-verdict rate ≥ 0.55 (L1: 0.259). SECONDARY: pad
arm within ±0.03 of original (no padding effect appears). Prediction: drop ≈ 0.15–0.25, truncate
arm ≈ 0.60 — the judge can verify a terse correct answer once it has a reference, which is the
mechanism claim behind B1's mitigation.

### J2-D — two references on the disagree stratum (~1.4k Mistral calls)
Questions where Mistral's S1 answer ≠ the reasoning model's S1 answer (37% of the R3 sample).
Arm: both answers shown as "[Two independent reference solutions — they disagree; at most one is
right]" (order fixed: reasoning model's first), v1 prompt, Mistral, dual order. Comparator: J2-R's
cached verdicts on the same matches (reasoning reference only). Harness `tools/analysis/j2d_two_refs.py`.
REGISTERED: key-decidable accuracy on the disagree stratum vs J2-R's 0.774, paired McNemar
p < 0.05, either direction reported. Prediction: NULL or slightly negative (a second, 12%-correct
candidate is noise); the point is to close the design branch with data.

### FORMAT — style perturbation (CALM-style; ~1.2k Mistral calls; conditional)
Eligibility: key-decidable R3 pairs whose two traces differ in formatting (markdown/LaTeX/list
markers present in one, absent in the other) — prevalence measured before launch and recorded
below; the test runs only if ≥ 150 such pairs exist. PREVALENCE (recorded 2026-09-09 23:55, before
launch, markdown-only definition): 383 of 946 key-decidable R3 pairs have exactly one formatted trace;
the formatted side is the correct one in 270 (70%). Formatting is confounded with model tier (iask 85%,
gpt-4o 78%, arx 63% of traces formatted; the small open models ≤ 9%), which is why only the causal
perturbation can answer the question. Arm: strip the formatting from the formatted
trace (markers removed, content and answer line intact); compare against the cached v1 verdict.
REGISTERED: verdict flip rate toward the unformatted side and the change in correct-verdict rate;
a format bias exists iff correct-verdict rate changes by > 3pp with p < 0.05. Prediction: no
effect (the L1 pad arm already showed bytes without content do nothing).

### STACK — the assembled judge v2, end-to-end (~4k Mistral calls)
Configuration = production template with: the reasoning reference (J2-R) + the v2 mechanics
(J3-R) IF J3-R passes its primary and guards, else v1 mechanics + the ANCHOR rubric of the clean
bareq512_s42 tree instead of the leaf rubric + dual order + confidence kept. Judged on R3's 1,980
matches, Mistral, one session.
REGISTERED (all must hold): (1) all-decidable accuracy ≥ J2-R's 0.849 − 1pp; (2) top-cluster
accuracy ≥ 0.665 − 2pp; (3) top-4 board from the 600 top-cluster matches has ≤ 1 key-order
violation (reasoning judge: 1; Mistral v1: 2); (4) decidable tie rate ≤ 15%; (5) flip rate ≤ J2-R's
12.8%; (6) long-wrong preference on short-correct top-cluster pairs < v1's. Prediction: passes
(1)–(5); (6) improves only if J3-R passes.

## Outcomes (appended as they land)

- **RUBRIC-512-SS (2026-09-10 00:24): B4 settled.** Cell vs same-session generic +1.0pp (35:26,
  p = 0.31); session drift alone +0.8pp. Cell rubrics ≈ +1pp for Mistral on keyed questions, not
  significant; discursive-only. STACK uses the anchor rubric (the ladder's clean anchor rubrics,
  induced with the pool of record withheld).
- **J3-R (2026-09-10 00:38): PRIMARY FAIL on the letter (p = 0.053), guards OK, direction positive.**
  v2+reference 0.862 vs v1+reference 0.849 (+1.4pp, 26:13); top cluster +1.1; reference-correct
  +2.2 (p = 0.002); reference-wrong −3.9 (n.s.). Long-wrong preference on short-correct top-cluster
  pairs 0.241 vs 0.259. B6 check: tie rate on KEY-DECIDABLE pairs is 5.9% under both v1+ref and
  v2+ref (identical) — the extra ties of v2 (22.6% vs 15.3% of all matches) fall entirely on
  non-decidable pairs, where TIE is the intended verdict. Per the STACK registration (v2 only if the
  primary passes), the assembled judge runs with the v1 mechanics; v2 stays a secondary arm.
- Free re-measurements under the reference (J2-R cache vs x12 MAIN, same matches): flip rate 12.8%
  vs 9.7% (Mistral v1 no-ref, J1 record) — position sensitivity is NOT reduced by the reference;
  decidable tie rate 5.9%.

## Deployment rule
The production judge changes only after STACK passes, and the change ships with the measured
before/after table for B1–B8. Cost model of the adopted design: one reasoning call per question
(amortised over every match on it) + two cheap judge calls per match.
