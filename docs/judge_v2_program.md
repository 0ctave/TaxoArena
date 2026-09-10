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

- **L1-V (2026-09-10 00:57): PRIMARY FAIL — the reference does NOT remove the elaboration
  vulnerability; it dents it.** 337 matches (of L1's 359; 22 lack a reference) with all three arms:
  original 0.772, truncate 0.350, pad 0.783. Truncation drop 0.421 (142:0, p < 1e-4) against L1's
  0.507 (183:1); the truncate arm rises from 0.259 to 0.350 — one sixth of the gap closed, far from
  the registered halving (drop ≤ 0.25, truncate ≥ 0.55). Secondary PASS: padding does nothing
  (+0.012). Reading: on this subset (top-cluster pairs where the CORRECT answer is the long one) the
  reference adds almost nothing to the original arm (0.772 vs 0.766: the length heuristic already
  picks right here), and when the correct answer is cut to a terse one the judge still follows the
  displayed reasoning of the wrong answer 65% of the time WITH the reference in hand. So the +7.6pp
  of J2-R comes from pairs where the length heuristic points the wrong way, not from disarming the
  heuristic itself. The v1 mechanics never tell the judge to check the final answer before weighing
  the reasoning; v2 does, and J3-R showed +2.2pp exactly where the reference is right. Registered
  follow-up: **L1-V2** below. Cache experiment_results/causal_length/mistral_refgrok.db, output
  l1v_outcome.txt.

### L1-V2 — truncation under the reference AND the v2 mechanics (~2k Mistral calls; registered 2026-09-10 01:00)
L1's matches, three arms, Mistral, reference as in L1-V, SYSTEM template = v2 (prompt_v2.py:
verify the final answer first; a wrong final answer cannot win; no depth criteria). Harness
`causal_length.py --reference grok-reasoning --prompt v2`, cache mistral_refgrok_v2.db.
REGISTERED PRIMARY: truncate-arm correct-verdict rate > L1-V's 0.350 by paired McNemar p < 0.05 on
the common matches (the mechanics, not the reference, are the variable). SECONDARY: original arm
≥ 0.772 − 0.02 (no loss where the long answer is right) and pad within ±0.03 of original.
Prediction: truncate arm 0.45–0.55 — the verify-first instruction moves the judge but does not
cure it; if the truncate arm reaches ≥ 0.55, the v2 mechanics enter STACK as a second arm.

- **J2-D (2026-09-10 01:13): NULL, direction negative — the branch is closed.** Disagree stratum,
  349 key-decidable: two references 0.748 vs the reasoning reference alone 0.774 (−2.6pp, 14:23,
  p = 0.19) vs no reference 0.705. The second candidate dilutes a good reference (reasoning-ref-correct
  stratum, n = 269: 0.862 → 0.810) and rescues only the 42 cases where Mistral's answer was the right
  one (0.571 → 0.690); where neither is right (n = 38) both reference arms sit at 0.368, below the
  no-reference 0.474. Design rule confirmed: ONE reference from the strongest available solver, never a
  set of candidates; when the reference is wrong the judge is worse than with none, so reference
  quality is the whole game (B3). Cache experiment_results/x12_crossdomain/rejudge_mistral_two_refs.db,
  output j2d_outcome.txt.

- **FORMAT (2026-09-10 01:25): no format bias (B5 closed).** 383 key-decidable pairs with exactly one
  markdown-formatted trace, formatting stripped from it: correct-verdict rate 0.786 vs 0.791 original
  (−0.5pp; 6:8; p = 0.79); zero flips toward the unformatted side. Markdown carries no verdict weight
  for Mistral; the 70% "formatted side is correct" is model tier, not style. No mitigation needed.
  Cache experiment_results/x12_crossdomain/rejudge_mistral_format_stripped.db, output format_outcome.txt.

- **L1-V2 (2026-09-10 01:58): PRIMARY PASS — the first causal evidence that a prompt change moves
  the elaboration bias; secondary misses by 0.001.** Same 337 matches as L1-V, 0 errors. Truncate arm
  0.433 vs L1-V's 0.350 (+8.3pp; 42:14; p = 0.0002): with the verify-first mechanics the judge keeps the
  terse correct answer 43% of the time instead of 35% (L1 without reference: 26%). Cost: original arm
  0.751 vs 0.772 (−2.1pp; 11:18; p = 0.26) — the registered floor was −2.0pp, missed by 0.001; pad
  0.763 vs 0.783 (−2.1, n.s.). Reading: v2 trades a small, non-significant loss where the long answer
  is right for a large gain where the terse answer is right; on the full R3 sample that nets +1.4pp
  (J3-R). Truncation drop is now 0.318 (L1 0.507 → L1-V 0.421 → L1-V2 0.318): the reference and the
  mechanics each remove a slice, and 43% is still far from a judge that reads the answer rather than the
  reasoning. The auto-trigger for a v2 STACK arm (truncate ≥ 0.55) was not reached; adoption rule (a)
  bias metric moved on a paired test — YES; (b) overall accuracy did not fall — YES (J3-R +1.4); so a
  **STACK-v2 arm (~4k calls) is the author's call**, recommended. Cache
  experiment_results/causal_length/mistral_refgrok_v2.db, output l1v2_outcome.txt.

- **STACK (2026-09-10 02:10): 5 of 6 checks pass; REGISTERED FAIL on the board check.** 1,974 judged
  (1 invalid), 944 key-decidable. (1) all-decidable 0.843 ≥ 0.839 OK; (2) top cluster 0.662 ≥ 0.645 OK;
  (3) top-4 board on 599 top-cluster matches = iask > gemini > arx > gpt-4o, 2 pairwise violations vs
  the key order gemini > arx > iask > gpt-4o (limit 1) — FAIL; (4) decidable ties 6.2% OK; (5) flips
  12.3% OK; (6) long-wrong preference 0.270 vs production 0.293 OK. Paired: STACK vs production v1
  (no reference) +7.1pp (85:18, p < 1e-4); STACK vs J2-R (cell rubric + reference) −0.6pp (12:17,
  p = 0.46) — the anchor rubric is as good as the leaf rubric under the reference, at zero induction
  cost. Reading: the assembled judge is a large, significant accuracy gain over production and passes
  every bias guard, but the top-cluster BOARD still puts iask above gemini, the same judge-level
  divergence R2 established; accuracy 0.662 on top-cluster pairs is not enough to flip a board built
  from 600 noisy pairwise verdicts. EXPLORATORY (not registered; F7's rule applied to STACK's own
  confidences): the board built from verdicts with both-order confidence ≥ 0.95 (n = 117) is
  gemini > iask > arx > gpt-4o with 1 violation; at ≥ 0.85 (n = 322) still iask-first. Cache
  experiment_results/x12_crossdomain/stack_v2.db, output stack_outcome.txt.
  DEPLOYMENT: per the rule below, production does NOT change on this result alone. Two registered
  routes remain: (i) STACK-v2 (below); (ii) adopt the confidence-gated board as the reported board,
  which was already registered by F7 and passes here as an exploratory replication.

### STACK-v2 — the assembled judge with the v2 mechanics (~4k Mistral calls; registered 2026-09-10 02:15)
STACK's configuration with the SYSTEM template = v2 (prompt_v2.v2_system_template on the anchor
rubric); same 1,980 matches, Mistral, one session. Motivation: J3-R (+1.4 overall, +1.1 top cluster,
n.s.) and L1-V2 (+8.3pp on the truncated arm, p = 0.0002; long-wrong preference 0.241). REGISTERED:
the six STACK checks, with (3) evaluated on the ungated board; PRIMARY = check (3) ≤ 1 violation AND
(1)–(2) hold. Prediction: (1),(2),(4),(5),(6) pass; (3) 50/50 — the iask/gemini gap is a 1.7pp key
gap and the v2 long-wrong preference (0.241) may or may not be enough to flip it.

- **RUBRIC-512-R (2026-09-10 02:20): exactly zero for the reasoning judge — B4 closed for both
  tiers, as predicted.** grok-4-1-fast-reasoning, both arms fresh in one session, 3,956 jobs, 0
  errors, 946 key-decidable: cell 0.842 vs generic 0.842 (24:24, p = 1.0); top cluster 0.665 vs 0.665
  (12:12); discursive +0.4 (18:16), quantitative −0.5 (6:8); no anchor beyond ±7pp on n ≤ 144 (all on
  ≤ 4 discordant pairs). Secondary (gain > Mistral's +1.8) fails. Four clean measurements now agree:
  induced cell rubrics are worth 0 to +1pp to any judge tier on keyed questions; the reasoning judge
  reads the answer, not the rubric. Rubric induction is a construction-side cost that buys nothing in
  judging; the anchor rubric is the production choice. Caches
  experiment_results/rubric_512/grok_reasoning_{cell,generic}.db, output grok_reasoning_outcome.txt.

### J6 — are the rubrics just not good enough? (registered 2026-09-10 02:30, before any call)
Rubric-quality audit (free, 2026-09-10): the 87 leaf rubrics of bareq512_s42 are specific, not
boilerplate — median 2,861 chars, pairwise vocabulary Jaccard 0.08 (p90 0.14), 7% of each rubric's
vocabulary shared by ≥ 50% of rubrics — but they are PROCESS checklists ("apply the governing law,
check dimensional consistency, justify assumptions") with no discriminating content about how answers
in the cell actually go wrong. Hypothesis to test: rubric TEXT can matter if it is (a) written by a
stronger model, or (b) contrastive — induced with the cell's real wrong answers in view.
Design and criteria: tools/analysis/j6_rubrics.py docstring (induction on grok-4-1-fast-reasoning from
the ladder's clean anchor corpora ± 25 key-labelled WRONG train-side answers per anchor; judging by
Mistral without reference on R3's 1,980 matches, three arms interleaved in one session: Mistral-induced
anchor rubric, frontier-induced, contrastive; ~12k calls). PRIMARY contrastive > Mistral-induced, paired
McNemar p < 0.05; SECONDARY frontier > Mistral-induced; leakage audit clean. Prediction: both null
(+0 to +1pp); a contrastive gain > +2pp reopens induction as a design axis.

- **STACK-v2 (2026-09-10 02:50): REGISTERED PRIMARY PASS — the board is now key-ordered at the top;
  5 of 6 checks pass, the flip-rate guard misses by 1.1pp.** 1,974 judged (0 invalid), 944 key-decidable.
  (1) 0.865 ≥ 0.839 OK — the best accuracy of any Mistral configuration measured; (2) top cluster 0.699
  ≥ 0.645 OK — above the reasoning judge's own 0.647 (J1); (3) top-4 board gemini > iask > arx > gpt-4o,
  1 violation vs the key order (limit 1) OK — the ungated board is now gemini-first, which no Mistral
  configuration had achieved; (4) decidable ties 5.6% OK; (5) flip rate 13.9% vs the 12.8% limit —
  FAIL by 1.1pp (STACK-v1 12.3%, J2-R 12.8%, Mistral v1 9.7%: position sensitivity is the one bias the
  reference and v2 do not improve; flips resolve to TIE, and decidable ties stayed at 5.6%, so the cost
  is verdict yield, not accuracy); (6) long-wrong preference 0.230 vs production 0.293 OK — the lowest
  measured. Paired: vs J2-R (leaf rubric, v1 mechanics, reference) +1.6pp (29:13, p = 0.02) — with the
  v2 mechanics the anchor rubric stack is significantly better than the cell-rubric stack; vs
  production v1 (no reference) +9.3pp (105:17, p < 1e-4). Cache
  experiment_results/x12_crossdomain/stack_v2_promptv2.db, output stack_v2_outcome.txt.
  DEPLOYMENT RECOMMENDATION: adopt STACK-v2 as the production judge — cheap judge + one reasoning
  reference per question + clean anchor rubric + v2 verify-first mechanics + dual order + confidence —
  with the flip rate disclosed (13.9%) and, as F7/STACK showed, the ≥ 0.95-confidence board reported
  alongside. Every other registered bias metric moved the right way on a paired test (B1: L1-V2 +8.3pp
  on the truncated arm and long-wrong 0.293 → 0.230; B3: one strongest reference, J2-D; B4: anchor
  rubric, four nulls; B5: no format bias; B6: ties 5.6%; B7: reference; B8: confidence kept). This is
  the author's call under the deployment rule below; the rule's letter ("STACK passes") is met on the
  registered primary and missed on one guard by 1.1pp.

### RK-1 — the verification kit (registered 2026-09-10 03:20, before any judged call; design in docs/rubric_v2_design.md)
Kit per leaf of bareq512_s42 (train-side only): K2 knowledge card (≤ 12 checkable facts/formulas from
≤ 40 solved train items) + K1 failure catalogue (5–8 error patterns with sign and check, from ≤ 20
key-labelled wrong train-side answers of frontier contestants) + K3 two worked neighbours (nearest
train questions of the same leaf by cosine on the 512-slice, option-overlap filtered; built 03:15 for
1,376 of the R3 questions, median top-1 cosine 0.67). Judging: STACK-v2 (reference + v2 mechanics +
anchor rubric) vs STACK-v2 + kit, both fresh and interleaved, Mistral, R3's 1,980 matches (~8k calls).
PRIMARY: kit > STACK-v2 by ≥ +1pp at paired McNemar p < 0.05; SECONDARY: quantitative anchors' gain >
discursive; leakage audit clean (5-grams vs correct options). Prediction: +1 to +3pp, quantitative-led.
Pilot card/catalogue (Chemistry thermodynamics leaf) recorded in the harness log: the card is a list of
formulas with validity conditions, the catalogue is error / sign / check triples — the intended shape.

## Deployment rule
The production judge changes only after STACK passes, and the change ships with the measured
before/after table for B1–B8. Cost model of the adopted design: one reasoning call per question
(amortised over every match on it) + two cheap judge calls per match.
