# IFEVAL RULING — may the IFEval checker's per-constraint pass vector be a reference block, and may B2 run tonight?

judge-design-specialist, 2026-09-23, PHASE A item A1. **Zero calls, zero execution**: a construction chain is live
and treats any running `python tools/analysis/...` as a reader, so nothing under `tools/analysis` was executed for
this ruling — not a `--dry-run`, not a `--selftest`. Every statement below is read off committed code, committed
record, or a raw data file read outside `tools/analysis`.

Object of the ruling: the experiment-manager's queue item **IFEVAL-CHECKER-OUTPUT** (`docs/agents/queue.json`
L931-L965, `docs/agents/queue.md` L20 / L76 / L124), proposed as B2 = a 12-match pilot + 407 key-decidable matches
x 2 orders = 838 calls, with the IFEval CHECKER OUTPUT as the reference block, offered as the analogue of the MATH
checker repair (STAGE3-MATH-CAPFREE, 0.958 A / 0.993 B) and as the last unrepaired rung of the reference ladder
(GEN-ARENA IFEval: SPECIFICATION 0.658, decidable ties 0.256, flips 0.380, rho 0.719, BRIDGE broken;
`docs/multi_corpus_design.md` L563-L600).

**VERDICT IN ONE LINE.** The pass vector is admissible as a reference block — it is an executed checker's output,
not induced criteria text, so REF-CHECKLIST does not close it — but it is a **per-response oracle**, categorically
stronger than MATH's reference, and therefore B2 may only run as a **decisiveness-and-disobedience instrument**,
never as a rung of the reference ladder; criteria 2 (rho) and 3 (the BRIDGE) must be declared NOT SCORED **before**
the run, for two independent reasons each; and the proposed 838-call form is **refused** because it has no
same-session control arm. The admissible form costs 1,628 calls.

---

## 1. What the IFEval checker actually emits, field by field

Verified by reading one raw lm-eval sample record
(`experiment_results/multicorpus/raw/Llama-3.3-70B-Instruct/meta-llama__Llama-3.3-70B-Instruct/samples_leaderboard_ifeval_2024-12-04T14-39-18.066641.jsonl`,
first line) and the two pieces of code of record that consume it: `tools/ingest/multicorpus_db.py` L66-L69 and
`tools/analysis/checker_answer_ingest.py` L290-L302 (`load_raw_ifeval_vectors`) and L498-L528 (the backfill).

Per (question, model) instance the harness record carries exactly these scored fields:

| field | shape | where it lives now |
|---|---|---|
| `doc.instruction_id_list` | list of constraint ids, e.g. `["punctuation:no_comma", "detectable_format:number_highlighted_sections", "length_constraints:number_words"]` | `corpus_questions.target` JSON, `multicorpus_cache_v1.db` |
| `doc.kwargs` | one dict per constraint, all slots present, non-applicable slots `None`, e.g. `{"num_highlights": 3}`, `{"relation": "at least", "num_words": 300}` | same `target` JSON |
| `inst_level_strict_acc` | **list of booleans, one per constraint** — the per-instruction STRICT pass/fail | `ifeval_checker_answers.strict_vector` (`checker_answers_v1.db`, 9,738 rows), with `instruction_ids`, `n_constraints`, `all_pass_strict`, `non_terminated`, `ingested_is_correct` |
| `prompt_level_strict_acc` | one boolean = `all(inst_level_strict_acc)` | `eval_results.is_correct` — **this is the key of record for IFEval** (`multicorpus_db.py` L27: `"IFEVAL": "IMPORTED:prompt_level_strict_acc"`) |
| `inst_level_loose_acc`, `prompt_level_loose_acc` | the loose analogues | present in the raw JSONL, **never ingested**: neither DB has them; the loader reads strict only |

Two facts settle the leakage question outright.

**(a) The strict vector DETERMINES the key, by definition, with no modelling step.** `prompt_level_strict_acc =
all(strict_vector)`; the backfill asserts exactly this identity row by row and aborts the whole run if it ever
fails (`checker_answer_ingest.py` L513: `all(vec) == pstrict` inside `okj`; L528 `raise SystemExit("[MISMATCH]")`).
A match is key-decidable iff exactly one of the two contestants is all-pass. Hand the judge both vectors and the
correct verdict is an AND and a comparison — no reading of either response is required, or even useful.

**(b) The fields split cleanly into two classes, and only one of them can enter a reference block without handing
over the key for the quantity a criterion would score:**

- **Question-level, response-independent**: `instruction_id_list` + `kwargs`. These describe the task, not any
  answer. They are what GEN-ARENA already showed the judge (`tools/analysis/generative_arena.py` L100-L112, the
  `reference()` branch: `"[Constraints the response must satisfy]"` + one line per id with its non-null kwargs).
  Admissible without qualification — and already measured, at 0.658.
- **Response-level**: `inst_level_strict_acc`, `prompt_level_strict_acc`, and any deterministic measurement from
  which they follow (word count 412 against "at least 300", comma count 0, highlighted sections 2 against 3).
  Every member of this class determines the key. There is no middle term: a measurement vector is the key with one
  arithmetic step interposed, which is a difference in the judge's workload, not in what it is told.

So the honest statement, which is itself a finding this ruling produces at zero calls: **on IFEval there is no
question-level checker output.** MATH's verifier emits a canonical answer string that exists before any response;
IFEval's verifier emits a predicate evaluated ON a response. GEN-ARENA finding 2's slogan — "a judge should be
given the checker's OUTPUT, not its specification" (`docs/multi_corpus_design.md` L585) — is, read strictly and on
this corpus, unrealisable: the only thing between the specification and the label is nothing.

## 2. Is a CHECKER_OUTPUT reference on IFEval the same object as MATH's checker repair? No — strictly stronger.

MATH (GEN-ARENA and STAGE3-MATH-CAPFREE): the block is `"\n\n[Verified reference answer]\n%s" % target`
(`generative_arena.py` L96; STAGE3-MATH-CAPFREE, programme L3992 ff., "the raw target is the reference verbatim").
It is appended to the **question**, is identical in both orders, is response-independent, and does **not** state
which contestant is right. The judge must still read two derivations, extract each final answer, and compare it
with the reference. Its 0.958 / 0.993 is therefore a measurement of **verification fidelity given a correct
target** — the same species of number as STACK-v2's 0.849-0.865 under a possibly-wrong solve, and that is why the
two sit on one ladder (programme L5859-L5861, L7042-L7045).

IFEval under the proposal: the block would state, for each contestant, the checker's verdict on that contestant.
It is attached to a **response**, differs between the two orders, and states the answer to the match. This is not
the MATH object one rung up; it is a different kind of object. Placed on the ladder it would read as
"CHECKER_OUTPUT (IFEval) 0.93 vs CHECKER_OUTPUT (MATH) 0.958" and a reader would conclude the rung transfers,
when in fact the two numbers measure different things: MATH's measures whether the judge can verify, IFEval's
measures whether the judge obeys a stated answer.

It is also stronger than ORACLE, the record's existing perfect-reference arm. ORACLE swapped a wrong reference for
the **key answer** — still question-level — and moved the judge 0.146 -> 0.720 on the reference-wrong stratum and
0.788 -> 0.797 on the reference-right stratum (programme L7046-L7048). A per-response vector removes even the
"which response reaches the key" step that ORACLE left in place.

**Ruling 2.** The pass vector is a legitimate reference block, but it is an ORACLE-CLASS, RESPONSE-LEVEL object.
The registration must say so in its first sentence and must **forbid** any sentence that places its accuracy on the
reference ladder beside 0.958, in the outcome, the ledger, the thesis or the blog. The ladder's IFEval rung stays
at SPECIFICATION 0.658 and this run does not repair it. Nothing repairs it: section 1 shows there is no rung to
build.

## 3. The vacuity argument, in my own words

A criterion is vacuous when its value is a deterministic function of what the instrument was handed. Under a
per-response pass vector the judge is handed `all(strict_vector)` for both contestants; the key is
`prompt_level_strict_acc`; so:

- **GEN-ARENA criterion 2 (per-corpus board Spearman rho vs key accuracy >= 0.85): NOT SCORED.** Two independent
  reasons. (i) Vacuity: the judged board becomes a noisy transcription of the key board, so rho measures the
  judge's obedience rate, not whether judged verdicts recover a key ordering — the question GEN-ARENA existed to
  ask. A rho of 0.98 here would license no claim whatever about judging without a key. (ii) **It is not even
  computable from the proposed schedule.** The 838-call form judges only the 407 key-decidable matches; the
  GEN-ARENA IFEval board was fitted on all 1,200 (`gen_arena_outcome.txt`: "IFEVAL board (n=1200 matches over 162
  questions)"). A BT fit on a correctness-selected subset is a biased board; rho against it is uninterpretable
  even setting vacuity aside.
- **GEN-ARENA criterion 3 (THE BRIDGE — judged argmax == key argmax): NOT SCORED.** Vacuous for the same reason
  (an argmax over a transcription of the key is the key's argmax), not computable for the same reason (no board),
  **and closed on the merits**: ORACLE established that a perfect reference buys 16.4pp and still misses the
  frontier order, and CONTEXT.md section 5 closes the frontier order (FRONTIER, AGGREGATE, ORACLE). The bridge
  broke on IFEval because the judged top-two gap is 0.040 logits (`gen_arena_outcome.txt`) — a frontier near-tie,
  the third independent appearance of the same phenomenon. A better reference is exactly the intervention the
  record has already shown does not fix it.
- **The exploratory router-cost readout (IFEval -0.6pp +- 3.8): NOT SCORED**, same mechanism.
- **Criterion 1 (key-decidable accuracy, bar 0.75): SCOREABLE but RENAMED.** It is no longer verification fidelity.
  It is the **obedience floor**: the share of key-decidable matches on which the judge commits to the contestant a
  correct, per-response reference names. Its complement — the disobedience rate — is a number the record does not
  have on any corpus, and it bounds the judge's irreducible error under the strongest reference that can exist.
  Report it under that name, with both tie conventions.

**What genuinely remains scoreable, and is the reason to run at all:**

1. **DECISIVENESS, paired on the same 407 matches.** GEN-ARENA's IFEval failure was as much a refusal to commit as
   an error: decidable ties 0.256 and flips 0.380, against 0.055 and 0.237 on MATH. Ties and flips are properties
   of the judge's output, not functions of the key, so they are not vacuous under an oracle reference. This
   decomposes finding 2 into two hypotheses the record cannot presently separate: **COULD NOT VERIFY** (the judge
   failed to count constraints; then ties and flips collapse when the counting is done for it) versus **WOULD NOT
   COMMIT** (the failure is abstention and order instability of the kind DECOMP and the position line describe;
   then ties and flips barely move even though accuracy jumps). Both outcomes are informative and the prediction
   is falsifiable in both directions. This is the whole value of the item.
2. **The obedience/disobedience floor** of the paragraph above, per contestant and pooled.
3. **NON_TERMINATED accounting** on IFEval traces, per rule 10.

**What the leakage readout can and cannot be, stated now so no one reaches for it later.** The CONSENSUS-FIT
KEY/REF signed-contrast logistic is **NOT ESTIMABLE** on this arm: the reference and the key coincide by
construction, so the two regressors are collinear and no REF coefficient exists. Likewise the design **cannot
produce a reference-wrong stratum** — the standing strata-by-reference-correctness requirement is satisfied by
reporting that the wrong stratum is empty by construction, which is itself the reason this arm says nothing about
the reference ceiling. What survives as a leakage readout is per-contestant agreement: the share of committed
verdicts that follow the all-pass contestant, per model and pooled, printed beside every accuracy.

## 4. What 407 key-decidable matches CAN settle, and what they cannot

Support (from `experiment_results/multicorpus/gen_arena_outcome.txt`): IFEval 1,200 matches over **162 distinct
reserved questions**, of which 407 are key-decidable — about 2.5 decidable matches per question. 162 questions sits
at the bottom of the record's support rule (120-190 distinct questions for SE 0.15; the query-support design
effect), and the record's DEFF rule is a **median 2.0x, worst 3.7x** understatement of match-level SEs. Taking
DEFF 2.0: **n_eff = 204** (worst case 110).

- Single-arm accuracy SE, question-clustered: **3.3pp** at A = 0.658, **1.8pp** at A = 0.93.
- Paired difference (both arms on the same 407 matches), SE = sqrt(d / n_eff) with d the discordant share:
  d = 0.10 -> SE 2.2pp; d = 0.20 -> SE 3.1pp; d = 0.30 -> SE 3.8pp.
- **MDE at 80% power, two-sided 0.05** (2.80 x SE): **6.2pp / 8.8pp / 10.7pp** respectively; at the worst-case
  DEFF 3.7, 8.5 / 12.0 / 14.7pp.

**CAN settle**: an accuracy move of the size the oracle reference should produce (0.658 -> 0.88-0.96, i.e. +22 to
+30pp, far above every MDE); a tie-rate collapse of the size hypothesis COULD-NOT-VERIFY predicts (0.256 -> under
0.10, about -16pp, above the MDE at the expected discordance); a flip-rate move of comparable size.

**CANNOT settle**: anything at or near the **5.7pp test-retest floor** (DECOMP) — a 5pp tie-rate change is
indistinguishable from session noise here; any per-model or per-constraint-family breakdown (162 questions over 8
models over 28 pairs leaves single-digit decidable matches per cell); any board, rho or argmax claim (section 3);
any statement about the 793 non-decidable matches; anything about the reference ceiling (the reference-wrong
stratum is empty by construction). A **null** result on decisiveness is therefore only reportable as "the tie rate
did not move by more than about 9pp", never as "the tie rate did not move".

## 5. Which closed lines are touched, and what new mechanism is named

- **REF-CHECKLIST / rubric-shaped references (CONTEXT.md section 5): NOT touched.** REF-CHECKLIST closed a
  *verification checklist written by a model* — induced criteria text, worth +1.6pp n.s. The pass vector is the
  output of executed, deterministic checker code that ran before this programme existed and is read verbatim from
  files on disk. The distinction is the one GEN-ARENA itself drew (L585). The registration must quote it, and must
  obey the manager's own binding hazard: the block states **what each response PASSED AND FAILED**, and is never
  rendered as a checklist of criteria to apply.
- **Rubric text at every granularity: NOT touched**, provided the per-source rubric string on the IFEval path
  (`generative_arena.py` L39) is left **byte-identical** between the arms. If it is reworded, the arm becomes a
  rubric-text arm and is refused on that ground alone.
- **ORACLE / the frontier order: TOUCHED, and it closes criterion 3** (section 3). Not reopened; obeyed.
- **REF-FORM-BY-CELL: TOUCHED, and this proposal names a mechanism the closure did not cover.** That closure
  (programme L7632 ff., note L7760-L7762) established that a stronger reference FORM — an executed
  program-of-thought solve — returns the incumbent's own letters on the quantitative anchors, because the
  incumbent's residual errors are modelling errors, not arithmetic. Its object throughout is a *question with a
  canonical answer* that a stronger solver might get right. The mechanism named here is different in kind: a
  corpus family whose verifier is a **predicate over the response** rather than a canonical answer string, so that
  the reference-form ladder has **no question-level rung above SPECIFICATION at all**. That is a new structural
  claim about corpora, not a new attempt to strengthen a solve, and it is why this ruling is worth writing even if
  B2 never runs.
- **JUDGE-BY-CELL: not touched** (the judge model is unchanged).

## 6. The reference block I would register, the conventions, and the guard

**Population.** GEN-ARENA's own IFEval schedule, unchanged: the 407 key-decidable matches of
`experiment_results/multicorpus/gen_arena_grok.db` (`source='IFEVAL' AND invalid=0`), so the comparison is exactly
paired. Rows whose contestant trace is `non_terminated` in `checker_answers_v1.db :: ifeval_checker_answers` (the
unclosed-`<think>` proxy) are excluded from the deciding subset per rule 10 and the count is printed.
**Recorded limit:** the *consistent* cap-hit proxy that STAGE3-MATH-CAPFREE built for MATH (cl100k tokens vs the
harness cap, abrupt end; `checker_answers_v2.db`) **does not exist for IFEval** — v1's column is the `<think>`
proxy only, and the checker's Block-1 finding (3) records that IFEval's harness cap is 1,280 (programme L3741).
This is a second, independent reason the accuracy may not be compared with MATH's 0.958: the populations differ.

**The block, verbatim shape.** Attached to each TRACE, not to the question block, and rendered per order:

    [Instruction checker output for this response — produced by executed checker code, not by a model]
    - punctuation:no_comma — PASS
    - detectable_format:number_highlighted_sections (num_highlights: 3) — FAIL
    - length_constraints:number_words (relation: at least, num_words: 300) — PASS

Field by field: one line per entry of `instruction_ids`, in the checker's own order; the constraint id verbatim;
its non-null `kwargs` slots in parentheses, in the stored order, `key: value`; an em-dash; `PASS` or `FAIL` from
the corresponding element of `strict_vector`. **No** aggregate line, **no** "3 of 3", **no** `all_pass_strict`,
**no** overall verdict, **no** loose fields (they are not ingested and must not be invented), **no** comparison
between the two responses, **no** instruction to the judge about what to do with the block beyond the existing
system and rubric strings. The header names the producer and says it is executed code, so the judge is not invited
to treat it as a fallible model opinion; the wording deliberately does **not** reuse the STACK-v2 solve wrapper
`"[Reference solution — produced independently, may be wrong]"` (`tools/analysis/rejudge_reference.py` L83-L85),
which would be a false label here.

**The order hazard, which is the load-bearing implementation clause.** GEN-ARENA's reference is appended to the
QUESTION (`generative_arena.py` L112: `q = text + reference(source, target)`) and is order-invariant. A
per-response block cannot live there. The assembler must build the two user prompts from the pair
`(trace, vector)` and re-derive the A/B labelling from the order actually posted. A transposition here produces
swapped vectors in the second order and an artefact indistinguishable from a catastrophic position effect.
**Required dry-run assertion, printed:** for a sample match, the vector shown for Model A in order 1 is
byte-identical to the vector shown for Model B in order 2, and vice versa.

**Arms, and why 838 calls is refused.** The proposal compares a fresh treatment arm against a cache written on
2026-09-13 — ten days and an unmeasured amount of provider drift ago — with no same-session control. The headline
readouts I am keeping (tie rate, flip rate) are precisely the soft quantities drift moves, and the session floor
rule exists for this. **Required:** both arms judged in the same session, interleaved match by match —
CONTROL = the GEN-ARENA IFEval prompt reproduced byte-identically (same system string L35, same rubric string L39,
same question-appended `[Constraints the response must satisfy]` block), TREATMENT = the same with the per-response
checker block. The GEN-ARENA cache is then used only as a drift readout (control-vs-cache agreement on the same
matches), never as the comparator of record. I decline the cheaper 100-match control: at 100 matches the drift
estimate's own SE is about 6.7pp, larger than the floor it is meant to certify.

**Conventions and guard.**

- Cap 8192; **temperature OMITTED** (plan Amendment 1 D2); judge grok-4-1-fast-non-reasoning; dual order, TIE on
  flip, INVALID on parse failure or `finish_reason` length; every call through `rejudge_reasoning.call_judge_full`;
  any local body copy asserts against `rejudge_reasoning.payload_body`. Confidence requested, never gated.
- **Both tie conventions always**: A (ties / INVALID / non-terminated counted wrong) and B (committed verdicts
  only). No accuracy is ever quoted without its convention.
- **NON_TERMINATED is never a verdict and never a tie** (rule 10).
- **Guard:** `--dry-run` at zero calls printing the population line, both assembled orders for one match, and the
  transposition assertion above; then a **12-match pilot in BOTH arms, interleaved (48 calls)**, read by the
  truncation guard — **refuse above 5% unparsed on the deciding subset**; `--analyze` exits non-zero on a partial
  cache; no REGISTERED line while the cache is short of the schedule. New cache file; `gen_arena_grok.db` is
  **read-only** and is not written by this item (the queue's A5 line "touch gen_arena_grok.db for write" must be
  struck).
- **Criteria I would register** (the manager's must be replaced, not amended): C1 obedience floor — key-decidable
  accuracy under both conventions, bar 0.85, prediction 0.88-0.96 (the record's nearest anchor is ORACLE's
  0.720 / 0.797 under a *question-level* key, so 1.0 is not the expectation); C2 decisiveness — paired McNemar on
  the decidable tie rate, control vs treatment, bar |delta| >= 10pp to be scored at all, prediction ties fall from
  about 0.256 to below 0.10 (COULD-NOT-VERIFY); C3 flip rate, same pairing, prediction falls from about 0.380 to
  below 0.25. **Falsifier:** if the tie rate does not fall by more than the MDE while accuracy rises above 0.88,
  the IFEval failure is WOULD-NOT-COMMIT, the abstention line owns it, and no reference of any strength repairs the
  rung. **NOT SCORED, declared before the run:** GEN-ARENA criteria 2 and 3, the BRIDGE, and the router-cost
  readout.
- **Cost:** 407 matches x 2 arms x 2 orders = **1,628 calls** (the 48-call pilot is inside this count); ceiling
  1,700. Against tonight's 14,000 ceiling with 2,181 scheduled, the headroom is ample; the 814 extra calls buy the
  only thing that makes the two headline readouts believable.

## 7. Should B2 run tonight?

**Not as proposed.** The 838-call form is refused: no same-session control, criteria 2 and 3 still standing, the
ladder framing still in the item's own value line ("the last unrepaired rung"), and an assembler hazard nobody has
written an assertion for. **Conditionally yes at 1,628 calls**, if and only if all of the following land before the
first call: (a) a registration that re-scopes the item to DECISIVENESS + the obedience floor, declares criteria 2
and 3 NOT SCORED, and forbids the ladder comparison in the same paragraph; (b) the paired same-session control arm,
interleaved; (c) the order-transposition assertion printed by `--dry-run`; (d) a reviewer READY on the dry-run
after CHAIN DONE. If PHASE A cannot deliver (a)-(d) before the chain frees the machine, **defer to 2026-09-24**:
nothing about this item decays overnight, and the zero-call finding in section 1 — that IFEval has no
question-level checker output, so the ladder's IFEval rung cannot be built at any price — is already banked by this
ruling and is the more valuable half of the item.
