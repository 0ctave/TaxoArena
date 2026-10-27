# Post-run adversarial review — IFEVAL-RESPONSE-ORACLE (2026-09-23)

Reviewer: adversarial-reviewer. Zero calls posted. Every number below was recomputed from the cache and the
checker/population tables by the reviewer's own scripts, never read from the outcome file. All databases were opened
read-only (`mode=ro&immutable=1` for the test cache, `mode=ro` for the three source DBs). A judged BFCL run was posting
concurrently; nothing of its was touched.

Objects under review

- outcome of record `experiment_results/multicorpus/ifeval_response_oracle_outcome.txt` (commit 3d1312f)
- cache `experiment_results/multicorpus/ifeval_response_oracle.db`, 814 rows; backup
  `experiment_results/_backup/ifeval_response_oracle_2026-09-23.db` — md5 **eba2c8ed0c283a59a5b1afb1a9c13138** on BOTH
- logs `experiment_results/multicorpus/ifeval_oracle_{pilot,run,analyze}.log`
- registration `docs/judge_v2_program.md` L11239-L11423 at HEAD (= L11148-L11329 at commit 4c8379c, the pointer the
  outcome carries; the pointer is correct AT the commit it names — the file has since grown 91 lines above it)
- ruling `docs/agents/leads/2026-09-23_ifeval_ruling.md` (af116f8); READY `docs/reviews/READY_ifeval_response_oracle.md`
  (2dea289 + the §9 re-pin at 70e6476), conditions C1-C5
- script `tools/analysis/ifeval_response_oracle.py`, working tree clean, sha256[:16] raw `6196a1b4e33e9e7a` / **LF
  `b8ba94311d813ce7`** = the pinned value

---

## 1. Per-claim table

| # | Claim | Verdict | Recomputed | Claimed |
|---|---|---|---|---|
| 1a | control accuracy A | CONFIRMED | 0.65356 (266/407) | 0.654 |
| 1b | control tie rate A | CONFIRMED | 0.26290 (107/407) | 0.263 |
| 1c | control flip rate A | CONFIRMED | 0.24324 (99/407) | 0.243 |
| 1d | control accuracy B | CONFIRMED | 0.88667 (266/300) | 0.887 |
| 1e | treatment accuracy A | CONFIRMED | 0.98771 (402/407) | 0.988 |
| 1f | treatment tie / flip A | CONFIRMED | 0.01229 (5/407) both | 0.012 / 0.012 |
| 1g | treatment accuracy B | CONFIRMED | 1.00000 (402/402) | 1.000 |
| 1h | question-clustered SEs over 122 questions | CONFIRMED | control SE 0.0296 (own bootstrap, B=20k, own seed) and 0.0298 (analytic cluster-robust); treatment 0.0054 and 0.0054 | 0.030 / 0.005 |
| 1i | C1 interval [0.976, 0.998] | CONFIRMED | own bootstrap [0.9760, 0.9975] | [0.976, 0.998] |
| 1j | "both conventions" for tie and flip | **PARTLY** | the printed B is the *parsed-rows* rate, not the registered "committed verdicts only"; identical to A only because INVALID = 0 | ties A 0.263 / B 0.263 |
| 2a | pairing is on the same match ids, no match twice | CONFIRMED | 814 rows, 407 distinct match_ids, 0 duplicate (match_id, arm), control id-set == treatment id-set, `key_winner` / `qid` / `model_a` / `model_b` identical across arms on all 407 | — |
| 2b | tie discordance 5 / 107, McNemar | CONFIRMED | b=5, c=107, n=407, exact two-sided p = 5.42e-26 | 5 / 107, p = 0.0000 |
| 2c | flip discordance 5 / 99, McNemar | CONFIRMED | b=5, c=99, n=407, exact p = 9.54e-24 | 5 / 99, p = 0.0000 |
| 2d | paired deltas | CONFIRMED | tie -0.2506 (-25.06pp), flip -0.2310 (-23.10pp) | -0.251 / -0.231 |
| 2e | (not claimed; added) paired accuracy | CONFIRMED (new) | +0.3342; 136 treatment-only correct vs **0** control-only correct; exact p = 2.3e-41. Treatment is never worse on any match. | — |
| 3 | -25.1pp and -23.1pp clear the 10pp floor at the WORST end of the DEFF bracket | **CONFIRMED** | see §3 | — |
| 4a | C5 control Qwen2.5-Math-7B 0/14 against treatment 12/12 | CONFIRMED | exact; every other cell of both tables also reproduced to the unit | outcome L35-L52 |
| 4b | "the control's error is concentrated on the weakest contestant" | CONFIRMED as a measurement, **EXPLORATORY** as a claim | see §4 | not stated in the outcome |
| 5a | drift 365/407 = 0.897 | CONFIRMED | 365/407 = 0.89680 | 0.897 |
| 5b | the 2026-09-13 cache is a READOUT, never the comparator | CONFIRMED | `cache_winner` is read at exactly one line (L1137, the drift print); `cache_flip` is never read in `analyze()`; `paired()` reads both arms from the new cache only | — |
| 6a | 1,628 calls, one fingerprint, finish_reason stop x1628 | CONFIRMED | cache: 1628 finish values, all `stop`; providers all `azure:grok-4-1-fast-non-reasoning` | — |
| 6b | 0 INVALID, 0 NON_TERMINATED | CONFIRMED | `sum(invalid)` = 0; `nt_a or nt_b` = 0 of 407 | — |
| 6c | the pilot's 48 inside the 1,628, no re-post | CONFIRMED | pilot log 24 rows / 48 calls, `ok 24, errors 0`; run log `cached 24 ... to post 790 row(s) = 1580 calls`; 24+790 = 814 rows, 48+1580 = 1628 calls | — |
| 6d | [PINS] MATCH at every launch | CONFIRMED | printed in the pilot log, the run log and the analysis; the reviewer's independent rebuild of the population gives schedule hash **ba4a0ac8a2364a49** | — |
| 6e | the night ledger's two entries sum to 1,628 | CONFIRMED | `experiment_results/night_calls_2026-09-23.json`: 48 + 1580 = 1628 (BFCL's 100 + 24 appended after) | — |
| 6f | gen_arena_grok.db and checker_answers_v1.db were not written | CONFIRMED | mtimes Sep 13 12:52 and Sep 15 21:58, both predating the 05:32 launch | — |
| 6g | the population is the registered 407 / 122 | CONFIRMED | independent rebuild from gen_arena_grok.db + multicorpus_cache_v1.db + checker_answers_v1.db: 1200 IFEVAL verdicts over 162 questions -> **407** key-decidable over **122** questions, 0 non-terminated; all 407 satisfy `all(strict_vector) == all_pass_strict == is_correct` | — |
| 6h | outcome text == analyze log | CONFIRMED | `diff` differs only by the `[PINS]` line (printed by `assert_pins` and re-emitted by `analyze`) and the trailing `[ANALYZE] wrote ...` line | — |
| 6i | the MATH-comparison refusal is code, not comment | CONFIRMED | `scrub()` (L240) scans the assembled outcome text against `FORBIDDEN_TOKENS` before any write and raises; `--compare-math` exits non-zero; the outcome contains 0 occurrences of `0.958` / `0.993` / `STAGE3-MATH-CAPFREE` and exactly 1 of `reference ladder`, inside `FORBIDDEN_NOTE`, which `scrub` excises before scanning | — |
| 7 | P4 control flip leg FAILED | **REFUTED — the comparator is on the wrong denominator** | see §5 | "0.243 -> FAILED" |

Commands (all read-only; the two scripts live in the session scratchpad):

    python scratchpad/recompute.py   # arms, clustered SEs, McNemar, leakage, Kish
    python scratchpad/pop.py         # population rebuild, schedule hash, drift
    python -c "... gen_arena_grok.db: select count(*), avg(flip) from verdicts where source='IFEVAL'"
    md5sum experiment_results/multicorpus/ifeval_response_oracle.db experiment_results/_backup/ifeval_response_oracle_2026-09-23.db
    ls -la experiment_results/multicorpus/gen_arena_grok.db experiment_results/multicorpus/checker_answers_v1.db
    diff (analyze log, CR stripped) (outcome, CR stripped)
    python -c "sha256 of the script with CRLF -> LF"   ->  b8ba94311d813ce7

Measured support, independently: 407 matches over 122 questions, 3.3361 per question, **Kish 4.3759**, cluster sizes
1:23 / 2:30 / 3:16 / 4:14 / 5:22 / 6:11 / 7:4 / 8:2 — identical to the outcome's printed readout.

---

## 2. The pairing, in full

`paired()` iterates the deciding subset and requires BOTH arms present. The reviewer confirms independently that the
two arms hold exactly the same 407 match ids, that no (match_id, arm) appears twice (PRIMARY KEY plus an explicit
count), and that `key_winner` is identical across arms on all 407 rows — so no match contributes twice and no pair is
formed across different keys. Ties and flips are NOT independent events here: **flips are a strict subset of ties in
both arms** (control 99 flips inside 107 ties; treatment 5 flips inside 5 ties, the same set). C3 is therefore very
nearly a restatement of C2, not a second criterion — defect D3.

---

## 3. Power: does the conclusion survive the WORST end of the honest bracket?

**Yes, with a factor of about 1.6 to spare.** Paired difference SE = sqrt(discordance / n_eff):

| n_eff | tie (disc 0.2752) SE | MDE80 | delta/SE | flip (disc 0.2555) SE | MDE80 | delta/SE |
|---|---|---|---|---|---|---|
| 327 (DEFF 1.24, plausible end) | 2.90pp | 8.12pp | 8.64 | 2.80pp | 7.83pp | 8.26 |
| 204 (registered) | 3.67pp | 10.28pp | 6.82 | 3.54pp | 9.91pp | 6.53 |
| **93 (Kish 4.376, rho = 1, WORST)** | **5.44pp** | **15.23pp** | **4.61** | **5.24pp** | **14.68pp** | **4.41** |

At the worst end the MDE is 15.2pp / 14.7pp — both below the observed 25.1pp / 23.1pp. Inflating the McNemar z by
sqrt(DEFF 4.376): tie z 9.64 -> 4.61 (p = 4.1e-06), flip z 9.22 -> 4.41 (p = 1.1e-05). Both still reject at any
conventional level.

Stronger still, and not in the outcome: the reviewer's **question-clustered bootstrap of the paired delta itself**
(20,000 resamples of the 122 questions) gives tie **[-0.302, -0.199]** and flip **[-0.278, -0.183]**. The entire 95%
clustered interval lies below -10pp for both, so the 10pp scoreability floor is cleared at the interval, not merely at
the point estimate. Cluster-robust analytic SEs on the paired deltas: 0.0264 (tie), 0.0242 (flip).

C2 and C3 survive the worst honest assumption. This is the load-bearing result of the run and it is robust.

---

## 4. C5's leakage table and the Qwen2.5-Math-7B row

Verified to the unit, both arms, all eight contestants, both pooled rows. The control row **0 / 14 = 0.000** is real.
On the full convention-A denominator it is **0 / 16** (14 committed-and-wrong plus 2 ties).

What it means, measured:

- The control's committed error is **concentrated on the weakest contestant**: 14 of the 34 committed-and-wrong
  control verdicts (41%) fall on the 14 committed matches where Qwen2.5-Math-7B is the all-pass contestant — 3.4% of
  the 407. Fisher exact, 0/14 against the other contestants pooled 266/286: **p = 3.5e-15**.
- It is **not** the record's length-preference mechanism. On those 16 matches the all-pass Math-7B response is the
  LONGER one (median 1,564 against 1,167 characters; shorter in only 6 of 16), so verbosity bias would have favoured it
  and did not. Across all control committed verdicts the all-pass contestant is shorter in 56.0% of the correct ones
  and 44.1% of the wrong ones — the wrong ones are if anything the longer-correct-answer cases.
- So the residual after removing length is a **contestant-identity / apparent-quality prior overriding the constraint
  evidence**: shown a weak-looking model that in fact satisfies every constraint, the control judge commits to the
  other side 14 times out of 14. The oracle block repairs 12 of 16 and converts the remaining 4 into ties.
- The treatment's own residual is concentrated in the same place: **4 of the 5 treatment ties** are matches whose
  all-pass contestant is Qwen2.5-Math-7B; the fifth is Phi-3.5-mini. The 1.2% irreducible disobedience is not uniform.

**Registered or exploratory?** C5 is registered as "THE LEAKAGE READOUT, PRINTED, NO BAR" — the per-contestant table is
registered to be *printed*, with no bar and no test. Everything in the four bullets above is **EXPLORATORY**. The
registration's Cost-and-consequence clause is explicit: this schedule "gains ... NO per-model row, now or later". The
Fisher test, the concentration statement and the length control were computed by this review and are **not**
registered; n = 16 matches for the Math-7B stratum, far under the 120-question support rule. They may be recorded as a
reviewer's observation and a hypothesis-generating note, and may **not** be published as a finding, quoted as a
per-model result, or turned into a bias claim about the deployed judge, without their own registration.

---

## 5. Ruling on the two open questions

### (a) P1 FAILED HIGH — 0.988 against the registered [0.88, 0.96]

FAILED is correct and it is not marginal: the clustered interval [0.976, 0.998] lies entirely above 0.96; its lower
bound clears the band's ceiling by 1.6pp. The band cannot be rescued by noise.

What it means: **the predictor was anchored on the wrong class of object.** P1's band was transported from ORACLE's
0.720 / 0.797, which is a *question-level* key. The IFEVAL RULING's own structural finding is that IFEval's verifier
emits a *predicate on a response*, and that `all(inst_level_strict_acc) == prompt_level_strict_acc == the key`. The
treatment block therefore does not merely inform the judge, it **determines the answer**: the key is a deterministic
function of the block the judge is shown, and `population()` asserts that identity row by row before anything is
posted. C1 is consequently a measure of **transcription fidelity**, not of verification fidelity — which the
registration already says in renaming it the obedience floor, and which the 0.988 / 1.000 pair confirms. A number above
the band is the expected consequence of a determinative reference. P1's failure is a failure of the registered prior,
not of the instrument.

Does it strengthen or weaken COULD-NOT-VERIFY? **It strengthens it, structurally, and it also bounds it.**
Strengthens: the registered falsifier fires on "the tie rate does not fall by more than the MDE WHILE accuracy rises
above 0.88". A higher accuracy makes the WOULD-NOT-COMMIT branch *more* reachable, not less — had the ties held at
0.988 accuracy, the falsifier would have fired and the verdict would have been WOULD-NOT-COMMIT. The ties fell 25.1pp
instead, so the branch the data could most easily have taken against COULD-NOT-VERIFY was fully available and was not
taken. Bounds: 0.988 with a determinative reference means the treatment arm removed the verification task *entirely*
rather than assisting it. What the run establishes is the **oracle limit** of COULD-NOT-VERIFY — when the counting is
done for the judge, the indecision collapses. It does not establish that a weaker, realistic, non-determinative aid
would collapse it. That bracket is mandatory in every sentence of record.

### (b) P4's flip leg — does the "session, not the treatment, is the finding" clause fire?

**NO. The clause does not fire, and the recorded FAILED rests on a MIS-SPECIFIED COMPARATOR, not on a session anomaly.**

The comparator 0.380 is on the **wrong denominator**. Measured, read-only, from gen_arena_grok.db:

    select count(*), avg(flip) from verdicts where source='IFEVAL'      ->  1200, 0.380000   <- the registered 0.380
    the same cache restricted to the 407 key-decidable matches          ->   407, 0.228501

P4's other two legs are on the 407: the 09-13 cache on the same 407 gives accuracy **0.6585** and decidable tie rate
**0.2555** — which is exactly where the registered 0.658 and 0.256 come from, to three digits. Only the flip leg was
drawn from the whole 1,200-match schedule. The same defect exists upstream in the GEN-ARENA table of record
(`docs/multi_corpus_design.md` L568-L571): its `flip` column is whole-schedule for both corpora (MATH 0.237 = 0.23667
over 1,800; IFEVAL 0.380 over 1,200) while its `accuracy` and `decidable ties` columns are key-decidable, and the
column is not labelled. P4 inherited the ambiguity. This is the same class of error the registration itself already
bracketed for "162 distinct reserved questions" (GEN-ARENA's whole schedule, wrong for the judged population of 122) —
the support readout caught it for the question count and missed it for the flip rate.

Against the correct same-denominator comparator, all three legs of P4 HOLD:

| leg | registered target | correct comparator (09-13 cache on the 407) | control measured | gap | band |
|---|---|---|---|---|---|
| accuracy | 0.658 | 0.6585 | 0.6536 | 0.005 | ±0.07 HELD |
| tie rate | 0.256 | 0.2555 | 0.2629 | 0.007 | ±0.09 HELD |
| flip rate | 0.380 (WRONG DENOM) | **0.2285** | 0.2432 | **0.015** | ±0.09 **HELD** |

The control arm reproduces the 2026-09-13 cell to within 1.5pp on every leg. Corroborated by the drift readout
0.897 >= 0.85 (P5 HELD). There is no session anomaly to find; the session is not the finding.

**Effect on C2 and C3: none.** They are unchanged and unweakened. Note further that even had the clause fired, the
registration's own P5 text says C2/C3 "are read against the SAME-SESSION control only, as they are in any case" — the
clause could never have touched C2/C3's arithmetic; it could only have barred transporting the control's numbers back
onto GEN-ARENA. Which, on the correct denominator, they now legitimately may be.

**Required by insertion (registrar):** a dated bracket at the P4 flip line of
`experiment_results/multicorpus/ifeval_response_oracle_outcome.txt` and at the corresponding programme outcome and
ledger row, recording that the registered target 0.380 is GEN-ARENA's whole-1,200-match flip rate, that the
same-denominator comparator on the deciding subset is 0.2285, and that P4's flip leg **HOLDS** at
|0.2432 - 0.2285| = 0.015 against a ±0.09 band; plus a bracket at `docs/multi_corpus_design.md` L568-L571 labelling
the `flip` column as whole-schedule for both corpora. Nothing is rewritten.

---

## 6. Defects, ranked

| id | sev | defect | fix |
|---|---|---|---|
| **D1** | **HIGH** | **P4's flip leg was scored against 0.380, GEN-ARENA's whole-1,200-match flip rate, while its other two legs use the 407 key-decidable subset. The same-denominator comparator is 0.2285 and the leg HOLDS. A FAILED prediction stands in the outcome of record on a mis-specified comparator — the criterion-substitution class: the registered target was drawn from a different population than the registered denominator.** | registrar bracket at the outcome's P4 line, the programme outcome, the ledger row, and `docs/multi_corpus_design.md` L568-L571 (label the `flip` column). Insertion only. |
| D2 | MEDIUM | The upstream GEN-ARENA table mixes denominators across columns without labelling them; any future prediction quoting that row will repeat D1. | label the column in place by insertion and state the key-decidable flip rates (MATH and IFEVAL) beside it. |
| D3 | MEDIUM | **C2 and C3 are not two criteria.** Flips are a strict subset of ties in both arms (control 99 in 107; treatment 5 = 5). C3's discordant pairs (5/99) are 104 of C2's 112. Reporting "C2 HELD and C3 HELD" as two independent confirmations overstates the evidence. | the synthesis must say that C3 is a near-restatement of C2 under tie-on-flip, not independent corroboration. |
| D4 | MEDIUM | **Convention B is not the registered convention B for the tie and flip rates.** `analyze()` computes `tieB` / `flipB` over *parsed* (non-INVALID) rows, not over *committed* verdicts. With INVALID = 0 the printed B is numerically identical to A, so nothing in this outcome is wrong — but "both conventions always" is satisfied only vacuously here, and on a cache with INVALIDs the printed B would be mislabelled. | a note of record; fix the labelling before any reuse. The registered convention-B tie rate is 0 by construction, which is itself the reason a B tie rate is meaningless and should print as "n/a by construction". |
| D5 | LOW | C4's NON_TERMINATED machinery never fired: 0 of 407. Not structurally impossible — 53 of 9,738 IFEval checker rows carry `non_terminated = 1` — but rule 10's exclusion path was not exercised by this run, and P6 is vacuous at 0 (already declared in the build note). | none; record that the path is untested on this cache. |
| D6 | LOW | The outcome's registration pointer "L11148-L11329" is correct only at commit 4c8379c, which it names; at HEAD the section is L11239-L11423. Correct as written, brittle as a reference. | none required. |
| D7 | LOW | C1's 0.988 is measured against a reference that DETERMINES the key. "Obedience floor" carries this, but a reader may still take 0.988 for a verification-fidelity number. | the mandatory bracket in §7. |

No BLOCKER. No writes to any database of record were found: gen_arena_grok.db (Sep 13 12:52) and checker_answers_v1.db
(Sep 15 21:58) both predate the 05:32 launch; the cache and its backup are byte-identical; the script tree is clean at
the pinned LF sha. READY conditions: C1 and C2 satisfied in code (pins recomputed and printed at all three launches),
C3 satisfied (`done: ok 24, errors 0`), C4 satisfied (`--night-spent 48`, printed source "operator-supplied", quoting
both sources), C5 satisfied (the night ledger exists and its two IFEval entries sum to 1,628 against the 1,700 test
ceiling and the 14,000 night ceiling).

---

## 7. The sentence of record, with its mandatory brackets

> On the IFEval reserved side, attaching an EXECUTED per-response constraint-checker vector to each trace collapsed the
> deployed judge's indecision: on the same 407 key-decidable matches over 122 questions, judged in one interleaved
> session, the decidable tie rate fell from 0.263 to 0.012 (-25.1pp, discordant 5 against 107, exact McNemar
> p < 1e-25) and the flip rate from 0.243 to 0.012 (-23.1pp, 5 against 99, p < 1e-23), while convention-A accuracy rose
> from 0.654 to 0.988 [0.976, 0.998] question-clustered (paired: 136 matches repaired, 0 broken). GEN-ARENA's IFEval
> cell is **COULD-NOT-VERIFY, not WOULD-NOT-COMMIT**: the judge failed to count the constraints, not to commit.

Mandatory brackets, every time the sentence is used:

1. **The oracle limit.** The per-response vector DETERMINES the key
   (`prompt_level_strict_acc = all(inst_level_strict_acc)`), so the treatment arm removed the verification task rather
   than assisting it. C1's 0.988 is an obedience / transcription floor, not verification fidelity, and COULD-NOT-VERIFY
   is established AT THE ORACLE LIMIT ONLY. The run says nothing about what a weaker, non-determinative aid would buy.
2. **The 1.2% irreducible disobedience.** Under the strongest reference that can exist the deployed judge still fails
   1.2% of the time (5 of 407, all five as ties). This is the only number of that kind in the record. It is not
   uniform: 4 of the 5 sit on a single contestant (exploratory, not registered).
3. **No ladder rung.** The IFEval rung stays at SPECIFICATION 0.658 permanently.

**What may NOT be said** (the first item is refused in code by `scrub()` and `--compare-math`, so a violating outcome
file cannot be written by this script):

- Nothing may place 0.988 (or 1.000) beside MATH's 0.958 / 0.993, or on the reference ladder, or in any sentence
  ranking corpora by checker-repair accuracy. Two independent reasons: the reference objects are not the same kind, and
  no IFEval cap-hit proxy exists (checker_answers_v2.db is MATH-only; v1's `non_terminated` is the unclosed-`<think>`
  proxy; IFEval's harness cap is 1,280).
- No Spearman rho, no per-corpus board, no BRIDGE / argmax, no router claim from this schedule (declared NOT SCORED,
  twice over, before the run).
- No per-model row, no per-constraint-family row, no bias claim from the Math-7B observation (§4) without its own
  registration.
- No claim about the 793 non-decidable matches, and none about the reference ceiling (the reference-wrong stratum is
  EMPTY BY CONSTRUCTION, which is why this arm says nothing about it).
- "the tie rate did not move" is never available as a null; the registered null form is "did not move by more than
  about 9pp". Not needed here.
- The control arm's numbers may be transported back onto the GEN-ARENA cell only on the KEY-DECIDABLE denominator
  (0.6585 / 0.2555 / **0.2285**), never against the whole-schedule 0.380.

---

## 8. What the run does not show

1. **One corpus** (IFEval), **one judge** (grok-4-1-fast-non-reasoning), **one session** (2026-09-23 05:32-05:43), one
   prompt family, one temperature convention.
2. **The oracle is not the deployed condition.** There is no deployment in which a per-response executed-checker vector
   is available at judgment time — if it were, there would be nothing to judge. The treatment arm is a bound, not a
   recipe.
3. **The tie collapse and the accuracy rise are not separable here.** Because the block determines the key, the two
   move together by construction; the run cannot say what fraction of the tie collapse would survive a reference that
   informs without deciding.
4. **C3 adds almost nothing to C2** (flips are a subset of ties).
5. **122 questions**, just above the record's 120-question support rule, with Kish 4.376 — adequate for a 25pp effect
   and inadequate for anything near the 5.7pp DECOMP test-retest floor. No stratum, cell, leaf or per-model breakdown is
   supported.
6. **Ten days of provider drift sit inside the drift readout**: 1 - 0.897 = 10.3% same-question disagreement against
   the 09-13 cache, above CANARY-BASELINE's 0.087 retest floor. Harmless against a 25pp effect; it bars any future
   small-effect comparison against that cache.
7. **The NON_TERMINATED path was never exercised** (0 of 407), and IFEval has no cap-hit proxy at all, so this run's
   truncation accounting is weaker than MATH's even though it reports 0.
8. Nothing here touches **rubric text, ensembles, gating, confidence, order policy, temperature or the frontier
   order** — all unchanged and all closed.

---

## 9. Verdict and chips

**The outcome of record is ACCEPTED, with one mandatory correction by insertion (D1).** Every headline number in
`ifeval_response_oracle_outcome.txt` reproduces independently to the printed digit; the provenance is clean; the
population, the pairing and the pins were independently rebuilt; the conclusion survives the worst end of the honest
design-effect bracket.

Chips:

- **C1 HELD** — obedience floor 0.988 [0.976, 0.998] convention A, 1.000 convention B (n = 402), bar 0.85. CONFIRMED.
- **C2 HELD** — tie rate -25.1pp, exact McNemar p = 5.4e-26; clears the 10pp floor at the 95% clustered interval and at
  n_eff 93. CONFIRMED.
- **C3 HELD** — flip rate -23.1pp, p = 9.5e-24. CONFIRMED, but a near-duplicate of C2 (D3).
- **C4 PRINTED** — 0 of 407 excluded; the path was not exercised (D5).
- **C5 PRINTED, NO BAR** — the table is confirmed to the unit; the Math-7B reading is EXPLORATORY.
- **P1 FAILED HIGH** — correct, and a failure of the registered prior rather than of the instrument; it strengthens
  COULD-NOT-VERIFY and bounds it to the oracle limit.
- **P4 flip leg: recorded FAILED, REFUTED by this review** — mis-specified comparator; it HOLDS on the registered
  denominator. The "a control arm outside P4's bands makes the session, not the treatment, the finding" clause **DOES
  NOT FIRE**.
- **P2, P3, P5, P6, P7 HELD** — all reproduced.
- **Reading: COULD-NOT-VERIFY, not WOULD-NOT-COMMIT** — CONFIRMED at the oracle limit, with the three mandatory
  brackets of §7.
