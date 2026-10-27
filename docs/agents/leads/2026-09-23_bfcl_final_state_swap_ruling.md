# CLOSED-LINE RULING: BFCL-FINAL-STATE-SWAP (Amendment 11 clause 3(a))

judge-design-specialist, 2026-09-23. **Zero calls, zero execution.** A Kotlin site null was live, so nothing under `tools/analysis` was executed (no `--dry-run`, no `--selftest`) and no `.db` was opened. Every statement is read off the committed record: `docs/agents/CONTEXT.md` §4-§5; `docs/judge_v2_program.md` (registration L12316-L12600; L1-V2 L108-L146; IFEVAL-RESPONSE-ORACLE outcome L11594+; BFCL-REF-ORACLE L11001-L11032; BFCL-JUDGED-PILOT third-hypothesis paragraph L11896-L11910); `docs/test_ledger.html` L123 (H7); `docs/plan_2026-09-15.md` Amendment 11 §3(a) L405; `docs/agents/leads/2026-09-23_ifeval_ruling.md` (af116f8). The file form follows that precedent.

## Verdict

**OPEN, but narrowly, and not on the ground the registrar argued.** The admissible mechanism is not "the artefact class is new". That ground is refused as unbounded, because it would reopen every prompt finding at every corpus admission. The mechanism is **DENOTATION FAILURE**: the inherited `prompt_v2.v2_system_template()` tells the judge to extract a FINAL ANSWER, and that object does not exist in the scheduled artefact. This is a well-formedness defect in the instrument, not a candidate improvement to it. No closed line is reopened. The ruling holds only together with the fence in §5.

UNDETERMINED was considered and refused. The ruling turns on documents already in the record, so there is no missing evidence that could justify deferring it.

## 1. Closed-line checklist (CONTEXT.md §5)

| closed line | checked against | ruling |
|---|---|---|
| Rubric text at every granularity (RUBRIC, LADDER, RUBRIC-512-R, J6, RK-1, LEAF-POWERED, STACK-NORUBRIC) | The edited object is the verify-first block **above** the `$systemPrompt` / `$rubric` slots (registration L12335). `RUBRIC_BFCL` is byte-identical and the gate refuses the run otherwise (byte-identity gate (b), L12386+). STACK-NORUBRIC changed the rubric slot and left the verify-first block standing, so the rubric line's own strongest instrument treated this block as the invariant, not as part of the closed object. | NOT REOPENED |
| Rubric-shaped references (REF-CHECKLIST) | No reference change: the per-task EXPECTED OUTCOME, rendered once per task, order-invariant, no per-side verdict, same 1,200-char CHECKER_TEXT_CUT (L12360+). REF-CHECKLIST closed induced criteria text supplied as a reference. Nothing is induced here; four literal strings in a frozen, corpus-independent template are replaced. | NOT REOPENED |
| Reference ensembles / gating / confidence / two-reference (ENSEMBLE-REF, J2-D, REF-CONF, ABSTAIN; F1-F3 / BOARD-W) | One reference, one judge, no gate, no confidence threshold, no abstention mechanism. The primary endpoint is a tie rate, and that family is about ties. The distinction holds: the family closed engineering abstention as a control knob, whereas here abstention is **measured as an outcome** and no mechanism acts on it. The TIE is the recipe's own dual-order flip rule, unchanged. | NOT REOPENED |
| Single order / selective order (ORDER-1, SELECTIVE-ORDER) | Both orders on all 458 matches; C4 prints the position signature and adjudicates nothing (L12470+). | NOT TOUCHED |
| Temperature 0 (TEMP-0) | Temperature omitted (plan Amendment 1 D2). | NOT TOUCHED |
| The frontier order (FRONTIER, AGGREGATE, ORACLE) | No board, refit, ranking, argmax or rung; C2 prohibits placing `A_swap` on the reference ladder. | NOT TOUCHED |
| Escalation to a reasoning judge (ESCALATE-LLAMA-LAW) | Judge unchanged: grok-4-1-fast-non-reasoning. | NOT TOUCHED |
| Sub-anchor profiles (PROFILE-TREE-ROBUST, KEY-SUBANCHOR-SCALE) | No cell, profile or per-trajectory claim. | NOT TOUCHED |
| The proposal memo (PERF-8) | A judged arm with one knob, not a memo. | NOT TOUCHED |
| H7's length clause (`docs/test_ledger.html:123`; invoked as closed at programme L9202). Not in §5, but binding. | H7 closed **instructing the judge to discount a known bias** as a mitigation (β_len +0.278 vs +0.285 instructed). FINAL-STATE-SWAP adds no mitigation clause. Had the four strings tried to instruct the judge away from first-position preference, this ruling would be CLOSED on H7 alone. | NOT REOPENED (see fence F1) |
| BFCL-REF-ORACLE's per-side-verdict form (L11001-L11032) | Forbidden here, and asserted by `assert_no_per_side_verdict` on **all 916** re-assembled payloads, not a sample (L12374+). | OBEYED |

## 2. The sharpest objection: L1 / L1-V2 / H7 made verify-first THE causal prompt change

**Disposed of, on the polarity of the finding.** L1-V2 (L134-L146) is an ESTABLISHMENT that was ADOPTED, not a closure. A line is CLOSED when further variation of a knob is shown to buy nothing. L1-V2 showed the knob **moved** (truncate arm 0.350 → 0.433, +8.3pp, 42:14, p = 0.0002) and it was promoted into the frozen recipe. This test does not contest that. Verify-first is kept in all four replacements ("extract each model's FINAL STATE and check it"; "A response whose final state is wrong cannot win"). Only the referent of the verification target changes. The variable is not *whether verification is instructed* but *whether the instruction's target denotes in the artefact*.

**What would NOT be enough.** The following grounds are refused for touching the frozen template again, on any corpus:
1. "A new corpus / new artefact class." This is unbounded, and the registrar's stated ground is not sufficient on its own.
2. "The wording fits the artefact less well", "reads more naturally", or "is clearer". Those are fit-quality claims, which the rubric line closed.
3. "The ties are high and something in the prompt might be responsible". This is a suspicion attached to no named string.
4. Any edit whose target **does** denote ("the question", "the response" and "its reasoning" all denote on a BFCL trace).
5. Any edit chosen **after** seeing which strings correlate with the outcome.
6. Any edit that instructs the judge to discount a bias (closed by H7).

## 3. The IFEVAL precedent cuts for OPEN

The argument that IFEVAL-RESPONSE-ORACLE already measured this mechanism is **refused**, on that run's own mandatory bracket. IFEVAL changed **the evidence supplied** (an executed per-response checker vector), not the template's furniture. Its bracket (i) records that it "REMOVED THE VERIFICATION TASK rather than assisting it" and says nothing about what a weaker, non-determinative aid would buy. FINAL-STATE-SWAP supplies zero new evidence, which makes it exactly that non-determinative class. IFEVAL gives this test a **prior**, not a duplicate: it showed that a judge's decidable tie rate can move by 25.1pp (0.263 → 0.012), so BFCL's 0.2183 is a live target rather than a floor.

Riders carried from the IFEVAL ruling: (a) the 25.1pp collapse may never be quoted as an expectation for this arm, because P1 (point −0.07) is the prediction of record; (b) `A_swap` never goes on the reference ladder.

## 4. Hygiene riders

**R1: reference strata, satisfied by declaration.** The reference is the per-task EXPECTED OUTCOME, so the reference-wrong stratum is **empty by construction**. The outcome must say so in those words, and must add that this arm says nothing about the reference ceiling on BFCL and that the CONSENSUS-FIT KEY/REF contrast is not estimable on it. Per-contestant agreement with the expected outcome is printed beside every accuracy instead, together with the result of `assert_no_per_side_verdict` over all 916 payloads.

**R2: the session floor binds the reading, not just the bar.** The control is a cache from a different session. Any Δ between −0.05 and 0, whatever its interval, is **DESCRIPTIVE-ONLY** and must never be narrated as a move (CANARY pass-2 floor 0.087 [0.056, 0.122]; DECOMP 5.7%).

## 5. The fence: the DANGLING-REFERENT TEST (required; the ruling depends on it)

Falsifier clause (c) is necessary but has three gaps. It binds only in the FAILED branch, it binds only "on this corpus", and "a mechanism the record has not seen" is undefined. The fence below binds in **both branches** and on **all corpora**, and every condition can be shown at zero calls before registration.

A further edit to the frozen `prompt_v2` verify-first template, on any corpus, is admissible only if all of the following hold and are shown in the registration before any code:

- **F1: denotation failure, shown with counts rather than asserted.** The proposal names the exact literal string(s) and shows, with a count on a stated sample of the deciding artefacts, that the object each string names has no referent in the artefact. Fit-quality claims fail F1. Bias-mitigation instructions fail F1 and are separately closed by H7. `--dry-run` prints the counts.
- **F2: one knob, byte-proved, endpoint declared first.** Everything but the named strings is byte-identical, proved by a printed gate: (a) user turns equal to the comparator's; (b) a full character diff of the two system prompts, with sha16 beside the comparator's; (c) exact replacement counts; (d) the schedule hash re-derived. The endpoint and its bar are fixed **before** the strings are chosen.
- **F3: one edit per (corpus, endpoint), no accumulation.** After this test reads, HELD or FAILED, a further template edit on BFCL requires a *different* F1-qualifying referent **and** a pre-registered argument why this result does not predict the next one. **Two readings on one corpus close the template line on that corpus permanently.**
- **F4: separability.** A template edit that changes more than one referent at once is **DESCRIPTIVE-ONLY** and may never be run as the separator of a named hypothesis.
- **F5: no promotion by side effect.** Nothing this arm returns changes the STACK-v2 recipe of record. A HELD C1 licenses a corpus-local variant only. Promotion requires its own registration with an MMLU-Pro **non-inferiority** reading.

This makes the decline of **BFCL-TRACE-TEMPLATE** (~1,016 calls) a matter of admissibility, not just a duplicate: it fails F4 outright (multiple referents, unattributable), fails F1 for most of its targets (they do denote), and as a successor fails F3.

## 6. The counterfactual: what CLOSED would have cost

If this line were closed, BFCL-JUDGED-PILOT's 0.2183 (the highest tie rate in the record; REF-CHECKLIST table L4427-L4432) would stay three-way ambiguous for good, and the pilot's "template mis-fit is live" item could never be retired by an admissible instrument. The other two hypotheses would become jointly unidentified. FLIP-RESEED measures only whether the flip set is stable. BFCL-DEGRADED-CONTROL is a difficulty probe that says nothing about the template, and its corruption rule is still owed a ruling that this document does not give. Corpus difficulty and template mis-fit are confounded in the tie rate itself.

## 7. Sentence of record

> **CLOSED-LINE RULING, judge-design-specialist, 2026-09-23, zero calls (Amendment 11 clause 3(a) discharged): BFCL-FINAL-STATE-SWAP is OPEN.** The four literal replacements reopen no closed line. The `$rubric` slot is byte-identical and nothing is induced (RUBRIC / LADDER / RUBRIC-512-R / J6 / RK-1 / LEAF-POWERED / STACK-NORUBRIC, whose own instrument left this block standing). The reference form is unchanged and order-invariant, with no per-side verdict (REF-CHECKLIST, BFCL-REF-ORACLE). There is no gate, no ensemble, no confidence threshold and no abstention mechanism (ENSEMBLE-REF / J2-D / REF-CONF / ABSTAIN). Both orders are posted on every match (ORDER-1, SELECTIVE-ORDER), temperature is omitted (TEMP-0), there is no board, rung or ranking (FRONTIER / AGGREGATE / ORACLE), there is one judge (ESCALATE-LLAMA-LAW), and there is no instruction to discount a bias (H7). **The admissible mechanism is not the artefact class, which is refused as unbounded, but DENOTATION FAILURE:** the inherited verify-first block asks the judge to extract a FINAL ANSWER from an artefact that has only a final state. That is a well-formedness defect in the instrument, not a candidate improvement to it, so it does not contest L1-V2, whose verify-first mechanic is kept word for word and whose finding was positive and adopted, not closed. **IFEVAL-RESPONSE-ORACLE does not pre-empt it:** that run changed the evidence supplied, not the template, and its own bracket (i) says nothing about a non-determinative aid, which is this arm's class. **The ruling depends on the DANGLING-REFERENT TEST as a standing fence** that binds in both branches and on all corpora: (F1) denotation failure shown with counts; (F2) one knob, byte-proved, endpoint fixed first; (F3) one edit per corpus per endpoint, with two readings closing the line on that corpus; (F4) multi-referent edits are DESCRIPTIVE-ONLY, which makes BFCL-TRACE-TEMPLATE inadmissible on its own terms; (F5) no promotion into STACK-v2 without an MMLU-Pro non-inferiority registration. **Two riders bind the outcome:** the reference-wrong stratum is empty by construction, so this arm says nothing about the reference ceiling and the CONSENSUS-FIT REF contrast is not estimable on it; and any Δ between −0.05 and 0 is DESCRIPTIVE-ONLY. **Budget, statistics and scheduling are not ruled on here.**

## What this ruling does NOT show

1. It does **not** authorise BFCL-DEGRADED-CONTROL; Amendment 11 §3(b)'s design ruling on the corruption rule is separate and still owed.
2. It does **not** authorise TRACE-TRUNCATION (Amendment 11 §3(c)), and it does not make BFCL-TRACE-TEMPLATE admissible under any budget.
3. It does **not** endorse the registration's statistics (bar, delta-DEFF planning value 2.0, MDE, P1-P8, UNDETERMINED thresholds). Flag for the reviewer: the pilot measured a level-DEFF of 3.60 against a registered ~1.4, and P8 predicts a delta-DEFF of 1.9. The outcome must score against the **measured** delta-DEFF.
4. It does **not** clear the run to post. The standard flow stands, and there is no pilot without a committed READY (Amendment 11 §3(d)).
5. It does **not** rule on whether the four strings will move the tie rate, and takes no position on P1.
6. It does **not** touch any MMLU-Pro, MATH or IFEval number, board, profile, tier, rung or bridge, and it does not alter the STACK-v2 recipe of record.
7. It is **not** the author's consent. It rules on the LINE only; the author's budget authorisation is Amendment 11.

---

**[COORDINATOR'S VERIFICATION NOTE 2026-09-23, recorded beside the ruling, not part of it.]** Checked by command before this file was committed: (a) the four FROM/TO replacements match the registration verbatim at `docs/judge_v2_program.md` L12338-L12346, and verify-first survives in each; (b) STACK-NORUBRIC's arm of record (L3885+) set `$systemPrompt = GENERIC_SYSTEM` and `$rubric = GENERIC_RUBRIC`, both below the verify-first block, which confirms the invariant claim. One imprecision in §1's first row as the specialist wrote it: the original said STACK-NORUBRIC "removed the rubric slot entirely", when it replaced the slot with a generic de-induced rubric. That row now reads "changed the rubric slot". The ruling's argument and its sentence of record ("left this block standing") are unaffected.
