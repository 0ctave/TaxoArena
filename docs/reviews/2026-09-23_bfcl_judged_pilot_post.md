# Post-run review — BFCL-JUDGED-PILOT

Adversarial-reviewer, 2026-09-23, **zero calls**. Every number below was recomputed by the reviewer from
`experiment_results/agent/bfcl_judged_pilot.db` and `experiment_results/agent/bfcl_result_2025-12-16.db`
opened `mode=ro&immutable=1`, and from the raw corpus files, **never from the outcome**. Both DB md5s are
unchanged by every command in this review (`ba078155a2220d930e3f1297448b563a` /
`5aff2f2fb3d972df9bcce1f94de6bcfc`). The reviewer wrote the READY
(`docs/reviews/READY_bfcl_judged_pilot.md`, 5d1dde1 + §12 at e158975) and reviews it here as an instrument
under suspicion, not as its own work.

**ONE-LINE VERDICT: the ARITHMETIC IS CLEAN and every headline figure reproduces to the digit; the
CONCLUSION DRAWN FROM IT IS NOT SUPPORTED.** A = 0.7402 is not "the deployed recipe verifies no better than
a no-reference judge". On the committed verdicts this recipe is the **best verification rate in the record**
(0.9469 B; wrong-committed 4.15%, against PAIR-NOREF's 9.30% and RECIPE-GROK's 6.90% on MMLU-Pro). What
collapses on agentic traces is **order stability**, not verification: 21.83% order-flip ties, of which
**57 of 100 are the judge choosing the FIRST-SHOWN side in both orders and zero the second-shown**, with a
first-position rate of 0.5862 over 870 non-tie votes (z = 5.09 against 0.5). Convention A, which scores a
flip as wrong, converts an abstention failure into an apparent verification failure, and the numerical
coincidence with PAIR-NOREF's 0.738 joins two different mechanisms at the same rung.

---

## 1. Per-claim table

| # | claim (as the outcome states it) | verdict | recomputed | command |
|---|---|---|---|---|
| 1a | C1 conv A, deciding subset: 339/458 = 0.7402 on 49 tasks | **CONFIRMED** | 339/458 = 0.7402, 49 tasks | `scratchpad/recompute.py` (own `dual`/`combine_orders` re-implementation from `schedule` + `verdicts`) |
| 1b | C1 conv B, deciding subset: 339/358 = 0.9469 on 48 tasks | **CONFIRMED** | 339/358 = 0.9469, 48 tasks | same |
| 1c | all-matches conv A 342/461 = 0.7419; conv B 342/361 = 0.9474 | **CONFIRMED** | 342/461 = 0.7419; 342/361 = 0.9474 | same |
| 1d | clustered bootstrap B=2000 seed 42, cluster = task: SE 0.0389 | **CONFIRMED** | SE 0.0389 (conv A deciding); 0.0388 all-matches; 0.0183 conv B (outcome 0.0184) | own task-resampling bootstrap |
| 1e | percentile [0.6590, 0.8136], normal [0.6640, 0.8164] | **CONFIRMED** (to MC noise) | percentile [0.6590, 0.8132], normal [0.6639, 0.8164] | own bootstrap; the 4e-4 upper-tail difference is resampling noise at B = 2000, not a disagreement |
| 1f | "the two intervals AGREE about the 0.75 bar, so the UNDETERMINED clause does not fire" | **PARTLY / SUBSTITUTED** | both intervals **contain** 0.75 (0.6590 < 0.75 < 0.8132; 0.6639 < 0.75 < 0.8164). They agree — but agreeing is not the registered test. C1's own text (L11093-L11095, restated in the falsifier at L11140) makes **"the interval straddles 0.75" itself an UNDETERMINED trigger**, and it fires. See D1. | `sed -n '11090,11096p;11138,11142p' docs/judge_v2_program.md` |
| 1g | "the point 0.7402 is at or below 0.75, so the falsifier fires as registered" | **CONFIRMED** | 0.7402 <= 0.75 | as 1a |
| 2 | ladder: A "is not distinguished from" NONE 0.738 | **CONFIRMED as arithmetic, REFUTED as a reading** | t = +0.06 vs 0.738 (p = 0.96). But the interval is also not distinguished from 0.70, 0.78 or **0.80** (t = -1.54, p = 0.13). "Not distinguished from 0.738" is true of every value in [0.664, 0.816]; naming only the rung the point happens to land on is a selected comparison. See D2, D5. | `scipy.stats` t-tests on 48 df, `scratchpad/decomp.py` |
| 2b | A is BELOW CACHED_SOLVE 0.865 and BELOW MATH 0.958 | **CONFIRMED** | t = -3.21 (p = 0.0024) and t = -5.60 (p < 1e-5) on 48 df | same |
| 3a | C2 partition 458 + 3 = 461; EMPTY 1 + DEGENERATE 0 of 385 | **CONFIRMED independently** | EMPTY = 1 (`multi_turn_base_179` / `gemini-2.5-flash-FC`), DEGENERATE = 0, of 385 7-roster TERMINATED base-EVAL episodes; my own decoder + C2 rule reproduces the cached `nj` on **all 608** schedule rows with zero disagreements; 458 + 3 = 461 and 146 + 1 = 147 | `scratchpad/c2.py` (own JSONL decoder, own `nonblank`/C2 rule, asserted against `schedule.nj`) |
| 3b | the 18.3% beside-object: 56 of 385 = 0.1455 | **CONFIRMED** | 56/385 = 0.14545 | `scratchpad/corpus.py` |
| 3c | registered counts 1113 / 461 / 385 / 147, both-present 1197 / 399 | **CONFIRMED independently** | 1113, 461, 385, 147, 1197, 399 — from my own filter over `episodes`, not the script's | `scratchpad/corpus.py` |
| 4a | C3 A_grok 100/146 = 0.6849, clustered SE 0.0439 -> [0.5988, 0.7711] | **CONFIRMED** | 100/146 = 0.6849, SE 0.0440 | `scratchpad/c3.py` |
| 4b | paired-by-task delta -0.0552 [-0.1269, +0.0173] on 49 shared tasks | **CONFIRMED** | -0.05524, paired bootstrap [-0.1269, +0.0166], SE 0.0373, 49 shared tasks | same |
| 4c | grok-FC "judge win-share 0.5342 (of 146 **committed** matches)" | **REFUTED — mislabelled denominator, and the juxtaposition misleads** | 0.5342 = 78/**146**, the DECIDING subset, not the committed one. The committed count is **106** (40 ties). Grok's win-share **on committed matches is 78/106 = 0.7358**, against its checker pass-share 0.7534 — a 1.8pp gap, not the 21.9pp the printed pair implies. Script L1560-L1567: `nsp` counts `not pending and not invalid`, which INCLUDES TIE, while the same script defines `committed` at L1096 as excluding TIE. | `scratchpad/c3.py`; `sed -n '1560,1567p;1094,1098p' tools/analysis/bfcl_judged_pilot.py` |
| 4d | "no detectable self-preference" is the honest reading | **PARTLY — the direction is right, the word is wrong** | the delta is -0.055 [-0.127, +0.017] and the committed win/pass gap is -0.018. Nothing points at self-preference in either direction. But the interval covers [-0.05, +0.10] entirely: this is **UNDETERMINED at this support**, i.e. "no self-preference was detected and none could have been unless it exceeded ~7pp", not "no self-preference exists". | as 4a/4b |
| 5a | 0 truncated sides of 922 headline / 0 of 1,216; 0 state-over-cap | **CONFIRMED independently** | 0 of 1,216; 0 state-over; per-side estimated tokens median 428, p95 699, **max 1,169** against the 2,500 cap — the cap is inert by a factor of 2.1 | `scratchpad/leak.py` (own re-assembly of all 1,216 payloads) |
| 5b | reference blocks cut 0 of 57 tasks | **CONFIRMED** (denominator quibble, D11) | 0 cuts; block chars min 339, median 609, p95 947, max 1,118 against the 1,200 cap. Over the **49 scheduled** tasks the cut is also 0. | same |
| 5c | 0 unusable of 1,216 posted calls; finish_reason `stop` x 1,216 | **CONFIRMED** | `invalid=0` on all 1,216; `finish='stop'` x 1,216; `max_tokens` 8192 on every row; max completion tokens **452** | direct SQL on `verdicts` |
| 5d | order-flip TIE share 100/458 = 0.2183 | **CONFIRMED** | 100/458 = 0.21834 | `scratchpad/decomp.py` |
| 5e | "matches with both orders 604 of 608" | **REFUTED as printed** | **all 608** matches have both orders. 604 is the count on the DECIDING subset; the denominator 608 is the full schedule. Numerator and denominator come from different objects — the incident class. `guard_numbers` (L1015-L1021) computes `both` over `deciding` and `guard_line` prints it against `len(rows)`. | `select mid,count(*) from verdicts group by mid` -> 608 mids x 2 arms |
| 6a | P1-P5, P7, P8 as scored | **CONFIRMED** | P1 0.7402 vs [0.78,0.90] FAILED; P2 0.9469 in [0.85,0.95] HELD (but D6); P3 0.2183 in [0.08,0.25] HELD; P4 0.0000 vs [0.04,0.12] FAILED; P5 0.0026 vs [0.10,0.25] FAILED; P7 0.0000 <= 0.01 HELD; P8 0.8164 < 0.958 HELD | all above |
| 6b | P6 scored FAILED | **REFUTED — must read UNDETERMINED** | point -0.0552, i.e. **0.0052 = 0.14 SE** outside the band's lower edge, with an interval covering the whole band and more. The registration wrote "undecidable at this support" as an explicit allowed outcome for exactly this arithmetic; scoring FAILED makes that option unreachable. See D3. | L11122-L11124 of the registration |
| 7a | night ledger 5 rows summing to 2,944 | **CONFIRMED** | 48 + 1,580 + 100 + 24 + 1,192 = 2,944, 5 rows | `cat experiment_results/night_calls_2026-09-23.json` |
| 7b | 1,316 posted rows = 100 probe + 24 pilot + 1,192 run | **CONFIRMED** | `probe` 100 rows / 50 mids, `verdicts` 1,216 rows / 608 mids / 2 arms each; 100 + 1,216 = 1,316; the 50 probe mids are all in the schedule and all also in `verdicts` — amendment item (6)'s different-objects reading, not a rule-10 re-post | direct SQL |
| 7c | one fingerprint on all 1,216 calls | **CONFIRMED** | `azure:grok-4-1-fast-non-reasoning` x 1,216 in `verdicts` and x 100 in `probe` | direct SQL |
| 7d | schedule hash `bcf9d1654e68e4ca` identical across both shas | **CONFIRMED BY EXECUTION** | rebuilt the schedule from the corpus under BOTH script versions: `bcf9d1654e68e4ca` under each; all 608 cached schedule rows (stratum, task, both agents, checker_winner, nj, trunc) reproduce with **0 differences** | `scratchpad/one.py`, `scratchpad/leak.py` |
| 7e | the two-sha difference "touches no prompt, no denominator, no schedule and no statistic" | **CONFIRMED BY EXECUTION — stronger than the READY's diff argument** | re-assembled **all 1,216 payloads plus the system prompt under each sha in separate processes** and hashed the concatenation: **`951ec3a0a063b5a8` under `fa38c1dbe2776314` AND under `5e9db53b894eeccb`**. Byte-identical instrument. | `python scratchpad/one.py <old>` / `<new>` |
| 7f | no per-side verdict, error_type, PASS/FAIL or all_pass in any posted payload | **CONFIRMED on the FULL population, not a sample** | all 1,216 re-assembled payloads regex-audited. Only hits: `checker` x 1,216 — the reference preamble's "the task's checker is state-based", which names no verdict; and `\bfailed\b` x 12 — inside the corpus's own user-turn text ("attempts to contact customer support ... have failed") and one trace. **Zero** `all_pass`, zero `PASS`, zero `error_type`, zero `multi_turn:*`, zero `Model A - PASS`. `assert_no_per_side_verdict` executed on all 608 statements and passed. | `scratchpad/leak.py`, `scratchpad/leak2.py` |
| 7g | registration precedes code and call | **CONFIRMED** | 22c5d5f 04:26 (registration) -> 6ccf2f7 05:02 (ruling) -> 5d1dde1 05:29 (READY) -> first posted call 05:49 -> 95c6d92 05:58 (fix) -> e158975 06:01 (re-pin) -> run 06:13 -> e18e37e 06:15 (outcome) -> 5a38eca 06:17 (cache) | `git log -1 --format='%h %ad'` on each |
| 7h | cache == the committed backup | **CONFIRMED** | `bfcl_judged_pilot.db` and `_backup/bfcl_judged_pilot_COMPLETE_1316rows_2026-09-23.db` share md5 `ba078155a2220d930e3f1297448b563a` | `md5sum` |

---

## 2. The finding itself: is A = 0.7402 a finding or an underpowered null dressed as one?

### 2.1 The support

| quantity | value |
|---|---|
| deciding matches | 458 on 49 tasks (5-12 matches per task, median 10) |
| naive binomial SE | 0.0205 |
| question-clustered SE (SE of record) | 0.0389 |
| **implied DEFF** | **3.60** (the registration expected ~1.4 at 461/57; QUERY-SUPPORT's median is 2.0) |
| **n_eff** | **127 independent matches** |
| MDE, 80% power, alpha .05 two-sided | **+-0.109** — this design can separate A from 0.75 only if A >= 0.859 or A <= 0.641 |
| MDE at 50% power | +-0.076 |

### 2.2 Could A genuinely be 0.85 and this sample read 0.74?

`P(observed <= 0.7402 | true 0.85, SE 0.0389) = 0.0024`; on a t(48) reference the two-sided p against 0.85 is
**0.0069**. So no: P1's registered point 0.85 is rejected at p < 0.01, and so are 0.865 (p = 0.0024) and
0.958 (p < 1e-5). **Against 0.80, however, p = 0.13** (`P(observed <= 0.7402 | true 0.80) = 0.062`). The run
therefore establishes `A < 0.85` and does **not** establish `A < 0.80`.

### 2.3 The decomposition that refutes the outcome's causal sentence

458 deciding matches = **339 right + 19 wrong-committed + 100 order-flip ties**.

| arm | corpus | conv A | conv B | ties | **wrong-committed** |
|---|---|---|---|---|---|
| PAIR-NOREF (the rung A is placed on) | MMLU-Pro | 0.734 | 0.887 | 0.173 | **0.0930** |
| CHECKLIST | MMLU-Pro | 0.749 | 0.893 | 0.161 | 0.0900 |
| REF (fresh) | MMLU-Pro | 0.845 | 0.921 | 0.080 | 0.0750 |
| RECIPE-GROK | MMLU-Pro | 0.857 | 0.925 | 0.074 | 0.0690 |
| **BFCL-JUDGED-PILOT** | **BFCL base** | **0.740** | **0.947** | **0.218** | **0.0415** |

(the four MMLU-Pro rows are REF-CHECKLIST's table, `docs/judge_v2_program.md` L4427-L4432, n = 826, same
conventions; wrong-committed = (1 - ties) - convA, which reproduces each row's conv B to 0.001.)

BFCL has **the highest conv B and the lowest wrong-committed rate of any arm in the record**, and the
**highest tie rate**. Its conv A sits at PAIR-NOREF's rung for the opposite reason PAIR-NOREF sits there.

The tie mechanism is not noise. Of the 100 flips:

| fwd vote | rev vote | n |
|---|---|---|
| Model A | Model A | **57** |
| TIE | Model A | 24 |
| Model A | TIE | 14 |
| TIE | TIE | 3 |
| Model B | TIE | 2 |
| Model B | Model B | **0** |

57 flips are the judge naming the first-shown side **in both orders**; **none** is the mirror image. Over
all 870 non-tie votes on the deciding subset the first-shown side wins **510 (0.5862)**, z = **5.09**. The
ties are also clustered: 11 of 49 tasks are at or above 50% ties, and 5 tasks carry 32 of the 100.

**Conclusion.** "On a real agentic artefact with a real outcome checker the deployed recipe verifies no
better than a no-reference judge does on MMLU-Pro" is **NOT SUPPORTED**. The recipe verifies *better* than
any MMLU-Pro arm when it commits; it commits far less often, because a trace-shaped artefact triggers a
strong and one-sided position preference in the deployed judge. This is a **decisiveness** result, not a
**fidelity** result, and the ladder — a fidelity ladder — is the wrong instrument to read it on. (The record
already knows the distinction: it is exactly IFEVAL-RESPONSE-ORACLE's COULD-NOT-VERIFY vs WOULD-NOT-COMMIT
question, asked of the same night's other test.)

### 2.4 "The recipe fails on agentic traces" vs "this corpus is harder" — and the third hypothesis

Neither is separable here, and the outcome names only the first two. The **third** is the one the data
points at: the prompt is mis-fitted to the artefact. The frozen v2 template instructs the judge to
"extract each model's **FINAL ANSWER** and check it against the reference" and speaks throughout of "the
question" and "the response" — MMLU-Pro furniture applied to a tool-call trace that has no final answer,
only a final state. The corpus-level `RUBRIC_BFCL` patches around this in the `$rubric` slot, but the
inherited verify-first block above it (kept deliberately, for comparability with STAGE3-MATH) is left
speaking about answers. A judge told to extract a final answer from an object that has none is a plausible
generator of exactly what was measured: high fidelity when it commits, frequent order-dependent
non-commitment when it does not.

What would separate the three:

1. **Position**: re-post the 100 flipped matches under the same recipe at a different seed. If the flip
   recurs on the same matches it is a property of the pair; if it moves it is instrument noise (DECOMP's
   5.7% test-retest floor is the yardstick). ~200 calls, needs its own registration.
2. **Template fit**: one arm with the verify-first block's "final answer" sentences replaced by
   "final state" sentences, everything else byte-identical. A single knob, ~916 calls. This is **not** the
   closed rubric line — it changes the inherited template, not the rubric slot — but it is a new instrument
   and needs a registration.
3. **Corpus difficulty**: the checker-disagreement filter already guarantees one side passed and one
   failed, so "hard" cannot mean ambiguous outcome. It can only mean the trace is long or the state opaque;
   both are measurable against the per-side token counts (median 428, max 1,169) and neither is near the cap.

None of these was run. **Until one is, the run does not license any sentence about why A is 0.74.**

### 2.5 What the falsifier licenses, positively

It licenses, at this support:

- **A < 0.85 (p = 0.007), A < 0.865 (p = 0.002), A < 0.958 (p < 1e-5)** on the BFCL base stratum under
  convention A: this corpus does **not** reproduce the MATH checker rung and does not reach the
  CACHED_SOLVE rung. P8 HELD.
- **The "for Agents" bridge may not be written as a measured claim on this corpus.** The falsifier's
  consequence follows from the point estimate and stands.
- **One measured sentence** with its interval, its convention and its convention-B counterpart, and a
  calibration / canary object on an agent corpus.
- **The instrument is clean**: 0 unusable of 1,216, 0 truncation, 0 leakage on the full population, the cap
  inert by 2.1x, one fingerprint, one schedule.

It does **not** license:

- "verifies no better than a no-reference judge" (refuted, §2.3);
- `A <= 0.75` as a statement about the parameter (the interval reaches 0.816; p vs 0.75 is 0.80, p vs 0.80
  is 0.13);
- any statement about *why*;
- a profile cell, an agent ranking, a per-trajectory or process claim (already refused by the registration);
- and it overturns no BFCL number, no board, no profile, no tier and no MMLU-Pro result.

---

## 3. Defects, ranked

| # | severity | defect | fix |
|---|---|---|---|
| **D1** | **BLOCKER** | **C1's registered outcome is over-determined and the outcome resolved it silently.** The registration fires **two** clauses at this data: "FAILED iff the POINT is <= 0.75" and "UNDETERMINED if **the interval straddles 0.75**" (L11093-L11095, restated verbatim in the falsifier paragraph at L11140-L11142). The interval **does** straddle 0.75 under both forms. The outcome (L37) silently narrows the UNDETERMINED trigger to amendment (5)(d)'s two-interval-**disagreement** test, a different and narrower criterion. That is **criterion substitution (C-7)**: the registered trigger was replaced, not satisfied. | Record C1 as **FAILED AT THE POINT / UNDETERMINED BY INTERVAL**, both registered clauses named. The falsifier's *consequence* (bridge withdrawn as a measured claim) follows from the point and stands; the positive sentence does not. Registrar to bracket the conflict into the registration by insertion and state which clause governs in future tests. |
| **D2** | **BLOCKER** | **The outcome's FALSIFIER READING asserts a mechanism the data refutes.** "verifies no better than a NO-REFERENCE judge" is contradicted by conv B 0.9469 and wrong-committed 0.0415 vs PAIR-NOREF's 0.887 / 0.0930 (§2.3). The two arms share a conv A number and share nothing else. | Strike the mechanism clause. Replace with the decomposition: highest conv B and lowest wrong-committed rate in the record, at the highest tie rate; the conv A collapse is order instability, 57/100 flips one-sidedly first-position, first-position rate 0.5862 (z = 5.09). Print the wrong-committed rate beside every conv A number on this corpus. |
| **D3** | **HIGH** | **P6 is scored FAILED on a 0.14-SE excursion when the registration explicitly provided "undecidable at this support".** The interval [-0.1269, +0.0173] covers the registered band entirely. If FAILED is the call here, the "undecidable" option can never be reached and is vacuous (a flag that leaves the tree at one node). | **P6 = UNDETERMINED (undecidable at this support)**, with point and interval printed. The registration's words require it: the option was written for this arithmetic and no other. |
| **D4** | **HIGH** | **C3's win-share denominator is mislabelled "committed" and the printed juxtaposition misleads.** 0.5342 = 78/146 (deciding, ties included); the committed figure is 78/106 = **0.7358** against a checker pass-share of 0.7534. The script uses two conflicting definitions of "committed" (L1561 vs L1096). | Print both: "win-share 0.7358 of 106 committed / 0.5342 of 146 deciding, beside checker pass-share 0.7534 of 146". Fix L1561 to exclude TIE or relabel. The conclusion (no self-preference) is unchanged and in fact strengthened. |
| **D5** | **MEDIUM** | **Ladder positioning is a selected comparison.** The interval [0.664, 0.816] is "not distinguished from" everything in that range; the outcome names only the rung the point sits on. It also treats each rung as a point, ignoring the rungs' own sampling error (PAIR-NOREF's n = 826). | State the full non-distinguished range, or state the ladder only as the two exclusions the data supports (below 0.865, below 0.958). |
| **D6** | **MEDIUM** | **P2 HELD on the band, MISSED on its gloss.** The registration reads "in [0.85, 0.95], **i.e. 4-8pp above convention A**". The observed gap is **+20.68pp**, 2.6x the top of the stated range. The outcome prints the delta and scores HELD without flagging the gloss — yet that 20.68pp gap is the single most informative number in the run (it *is* D2's mechanism). | Score "P2 HELD on the band; the 4-8pp gloss MISSED at +20.68pp", and carry the miss into the finding. |
| **D7** | **LOW-MED** | **`matches with both orders 604 of 608`** (outcome L18, guard line): numerator from the deciding subset, denominator from the full schedule. All 608 have both orders. Reads as if 4 matches were incomplete. | Print "604 of 604 deciding (4 non-judgeable excluded; 608 of 608 have both orders)". Script L1015-L1021 / L1040. |
| **D8** | **LOW-MED** | **The registration pointer in the outcome AND in `run_meta` is `L10965-L11146`**, which **excludes** the five-item amendment at L11190-L11237 — including item (5)(d), the interval of record, which the outcome cites by name at L37. The section actually spans L10965-L11237 (the READY has it right). | Bracket the pointer to L10965-L11237. `run_meta.registration` is baked into a script constant and cannot be corrected in this cache; the bracket is the correction of record. |
| **D9** | **LOW-MED** | **Condition 10 of the READY is only PARTLY MET by the outcome.** It requires the outcome to state that the cache was opened under `fa38c1dbe2776314` (124 rows) and completed under `5e9db53b894eeccb`, **and that the difference is the one-line label fix touching no prompt, no denominator, no schedule and no statistic.** The outcome L5 states both shas and the word "(DIFFERS)" — nothing else. The inertness sentence exists only in commit message 5a38eca, which is not the outcome. | Registrar brackets the inertness sentence into the outcome, citing this review's executed proof: **all 1,216 payloads + the system prompt hash to `951ec3a0a063b5a8` under BOTH shas**; schedule `bcf9d1654e68e4ca` under both. |
| **D10** | **LOW-MED** | **DEFF 3.60 against the registered expectation of ~1.4** (SE 0.024 expected, 0.0389 measured). The outcome prints the expectation and the measurement but does not remark that the design's effective support is **127 matches, not 458**, nor that the MDE against the 0.75 bar is +-0.109. | Print DEFF, n_eff and the MDE beside every C1 interval on this corpus, and in the ledger row. |
| **D11** | **LOW** | **`CHECKER_TEXT_CUT 0 of 57 TASKS`** uses all EVAL tasks; only 49 are rendered into a payload. Both are 0. | Print the scheduled denominator (0 of 49) beside it. |
| **D12** | **LOW** | **`385` names two different objects in the same outcome** — selfpref terminated pairs (L16) and 7-roster terminated episodes (L22). Arithmetically distinct objects that coincide. | Label both. |
| **D13** | **LOW** | **The DBGUARD monkeypatch of `sqlite3.connect` is not idempotent**: importing two versions of the module in one process chains the wrappers into a `RecursionError`. Found by this review; harmless in production (one module per process). | Guard the patch with a sentinel attribute. Not blocking. |
| **D14** | **LOW** | READY defects 1, 2, 5 (pilot-guard denominator shrinkable by errored jobs, `--override-guard` not persisted, night ledger counts cached rows) were never exercised: 0 errors, no guard fire, no halt during posting. They remain latent for the next instrument. | Carry forward. |

Nothing in this list touches a computed number in the outcome except D4 (a label, and a second number that
should be printed beside it). **Every headline figure is correct.**

---

## 4. The sentence of record, with its mandatory brackets

> On the BFCL base stratum (pool `p2035adddedd1becb`, 57 EVAL tasks; corpus `bfcl_result_2025-12-16.db`),
> with the deployed recipe (grok-4-1-fast-non-reasoning, prompt_v2 verify-first + corpus-level
> SYSTEM_BFCL/RUBRIC_BFCL, cap 8192, temperature omitted, dual order, TIE on flip) and the task's own
> ground-truth call sequence as a blind per-task reference, the judge's agreement with the corpus checker
> on the 458 checker-disagreeing deciding matches (49 tasks) is **A = 0.7402 under convention A**
> [interval of record, point +- 1.96 x the question-clustered bootstrap SE 0.0389 over the 49 TASKS,
> B = 2000, seed 42: **[0.6640, 0.8164]**; percentile **[0.6590, 0.8136]**]
> [**and A = 0.9469 [0.9109, 0.9829] under convention B on the 358 committed matches** — both conventions
> are always reported and the B number is the one that carries the mechanism]
> [**DECOMPOSITION, mandatory with this number**: 339 right + **19 wrong-committed (0.0415)** + **100
> order-flip ties (0.2183)**; the wrong-committed rate is the LOWEST and the tie rate the HIGHEST of any
> arm in the record (PAIR-NOREF 0.0930 / 0.173, RECIPE-GROK 0.0690 / 0.074, REF-CHECKLIST table
> L4427-L4432); **57 of the 100 flips are the judge naming the FIRST-SHOWN side in both orders and 0 the
> second-shown**, first-position rate 0.5862 of 870 non-tie votes, z = 5.09]
> [**C1 = FAILED AT THE POINT (0.7402 <= 0.75, the registered falsifier) AND UNDETERMINED BY INTERVAL (the
> registered UNDETERMINED trigger "the interval straddles 0.75", L11093-L11095 and L11140-L11142, also
> fires); the outcome of record states only the first, which is a criterion substitution the registrar
> must bracket**]
> [**SUPPORT**: DEFF 3.60, n_eff 127, MDE +-0.109 at 80% power; the run establishes A < 0.85 (p = 0.007),
> A < 0.865 (p = 0.002) and A < 0.958 (p < 1e-5), and establishes NEITHER A <= 0.75 (p = 0.80) NOR
> A < 0.80 (p = 0.13)]
> [**CROSS-CORPORA**: the rungs 0.738 / 0.865 / 0.958 were measured on MMLU-Pro and MATH under the same
> recipe; this is a positioning across corpora, never a paired test. The only on-corpus contrast is the C3
> self-preference stratum. "Not distinguished from 0.738" is true of every value in [0.664, 0.816],
> including 0.80]
> [**NOT LICENSED**: "the recipe verifies no better than a no-reference judge" — refuted by conv B and the
> wrong-committed rate; any statement about WHY A is 0.74 (position bias, corpus difficulty, and a template
> mis-fitted to a trace-shaped artefact are all live and none was separated); any profile cell, agent
> ranking, per-trajectory or process claim]
> [**PROVENANCE, condition 10, supplied here because the outcome states only the two shas and the word
> DIFFERS**: the cache was opened under script LF sha `fa38c1dbe2776314` (124 rows: 100 probe + 24 pilot)
> and completed under `5e9db53b894eeccb`; the difference is the one-line `launch()` label fix plus additive
> selftest hardening, and it is INERT — verified by execution, not by diff: all 1,216 assembled payloads
> plus the system prompt hash to `951ec3a0a063b5a8` under BOTH shas, and the schedule hash is
> `bcf9d1654e68e4ca` under both]
> [**INSTRUMENT**: 1,316 posted rows (100 probe + 24 pilot + 1,192 run), one fingerprint
> `azure:grok-4-1-fast-non-reasoning` on all 1,216 judged calls, `finish_reason` `stop` on all 1,216,
> 0 unusable, 0 truncated sides of 1,216, 0 state-over-cap, reference blocks cut 0 of 57 tasks (0 of the
> 49 scheduled), max completion tokens 452 of the 8,192 cap, max per-side artefact 1,169 of the 2,500-token
> cap; **no per-side verdict, error_type, PASS/FAIL or all_pass in any of the 1,216 payloads, verified on
> the full population by re-assembly, not on a sample**; night ledger 5 rows summing to 2,944 of 14,000]
> [**it overturns no BFCL number, no board, no profile, no tier and no MMLU-Pro result**]

---

## 5. Chips

| chip | value |
|---|---|
| C1 | **FAILED AT THE POINT / UNDETERMINED BY INTERVAL** (both registered clauses fire; the outcome records only FAILED) |
| C2 | **HELD** (independently reproduced: EMPTY 1 + DEGENERATE 0 of 385; 458 + 3 = 461) |
| C3 | **HELD** on its registered condition (0 grok-FC matches in any headline figure) — **with a mislabelled win-share denominator, D4** |
| C4 | **HELD** (all counts reproduced independently; two denominator labels wrong, D7 / D11) |
| P1 | FAILED |
| P2 | HELD on the band; **gloss MISSED** (+20.68pp vs the stated 4-8pp) |
| P3 | HELD |
| P4 | FAILED (mis-calibrated band) |
| P5 | FAILED (mis-calibrated band, registration item (3)) |
| P6 | **UNDETERMINED** (the outcome says FAILED; D3) |
| P7 | HELD |
| P8 | HELD |
| arithmetic | **CLEAN** — every headline figure reproduces to the digit |
| instrument | **CLEAN** — 0 unusable, 0 truncation, 0 leakage on the full population, two-sha inertness proven by execution |
| conclusion | **NOT SUPPORTED as written** (D1, D2) |
| record state | **NOT READY for the ledger as written**; READY after D1-D4 are bracketed by insertion |

---

## 6. What the run does not show

1. That A <= 0.75. The interval reaches 0.8164; p against 0.75 is 0.80.
2. That the recipe verifies worse on agentic traces than on MMLU-Pro. On committed verdicts it verifies
   **better** than any arm in the record.
3. Why the judge flips. Position bias is measured (z = 5.09, one-sided) but its cause — the artefact shape,
   the trace length, or the MMLU-Pro-shaped verify-first template asking for a "final answer" from an object
   that has none — is not separated.
4. Anything about the three refused strata (`miss_func`, `miss_param`, `long_context`), about non-terminated
   episodes (14 CAP_HIT for `meta-llama_Llama-3.3-70B-Instruct-FC`), or about the 8 EVAL tasks that never
   entered a match.
5. Any self-preference result. The paired delta's interval covers the whole registered band; nothing above
   ~7pp in either direction could have been detected.
6. Whether the flips are reproducible. No retest was run; DECOMP's 5.7% test-retest floor is the only
   yardstick and it was measured on a different corpus.
7. Any agent ranking, profile cell, tier, per-trajectory or process claim — refused by the registration and
   still refused.

---

Reviewed by the adversarial-reviewer, 2026-09-23. Zero calls. Both DBs byte-identical before and after every
command. Recomputation scripts in the session scratchpad
(`recompute.py`, `corpus.py`, `c2.py`, `c3.py`, `decomp.py`, `leak.py`, `leak2.py`, `one.py`).
