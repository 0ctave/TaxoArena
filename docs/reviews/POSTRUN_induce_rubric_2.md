# POST-RUN review: ARCH-V2-INDUCE-RUBRIC-2 (run 541e2ae from main 0a77ac2; READY eeb1dec)

Adversarial reviewer, 2026-09-24. Zero calls. Every DB was opened read-only with `mode=ro&immutable=1`. The SPLIT-2 views were hashed before and after my checks and are unchanged: gen c2930c60...0ec, eval e35b7518...369, mtimes 20:23:39.418 / 20:23:51.222 +0200, 0 -wal / -journal (`ls -a | grep -c`). Scratch scripts are in the session scratchpad and are not committed: `leak2.py` (V1/V2/V3), `refexp.py` / `refexp2.py` / `refexp3.py` (reference exposure), `empty.py` (empty-trace census), `system_turn.txt` (the rendered judge system turn).

## VERDICT

**VALID.** The artefact of record is `experiment_results/archv2/induce_rubric_2/rubric_mcq_ARCH-V2-INDUCE-RUBRIC-2.json`. It was minted by 1 invocation; attempt 1 is VALID; V1-V5 PASS; P1 and P2 HELD; the falsifier did not fire. I recomputed every sha and found no difference.

**FITNESS READING: UNFIT.** Under the registered scope, the artefact is therefore NOT ADOPTED and the slot goes to THE AUTHOR. This is never a fourth attempt (F1b change 7; registration L16339 and L16343). There are two independent grounds, each sufficient:
1. **U1 (reference as the criterion).** Clause 1 defines correctness as agreement with the reference: "the stated option letter must exactly match the reference letter". That is not final-answer correctness.
   - It contradicts V2_SYSTEM_TEMPLATE's verify-first block: "(marked as produced independently; it may be wrong) ... check it against the reference and against your own reading of the question".
   - It contradicts the induction prompt the rubric was written from: "a reference solution that may be wrong".
   - It fails the registration's own fitness question: "it grades final-answer correctness" (L16328).
   - On the pilot's population, the v0 reference is wrong on 133 of 1,027 reference-bearing EVAL variants (12.95%).
   - On key-decidable, reference-bearing, answer-disagreeing pairs, clause 1 departs from the key on 8.91%:
     - on 3.40% it names the WRONG contestant as the winner;
     - on 5.51% it erases the correct contestant's advantage.
   - The exposure depends on the contestant. On the wrong-reference questions, agreement with the wrong letter ranges from 0.218 to 0.508 across the 46 models.
2. **U2 (a reward for having an explanation, and suppressed ties).** On final-answer ties the rubric says: "... has sounder reasoning ...; tie only if both identical in correctness and reasoning quality".
   - This rewards the PRESENCE of an explanation, which the induction prompt forbids ("must not reward or penalise ... the presence or absence of an explanation").
   - It contradicts the template's "If neither has any, output TIE ... a short correct response ties a long correct response" and the user turn's "If both models are genuinely equivalent, output winner: TIE".
   - 6 of the 46 roster models have EMPTY outputs on 100% of their EVAL responses. The loader replaces each with a one-line placeholder ("The model selected option X: ..."), so these models have no reasoning to be "sounder".
   - None of the 6 is in ARENA12. They sit in 255 of the pilot's 1,035 pairs per anchor and in 0 of the 66 ARENA12 pairs, so the effect cannot cancel in C1's exponent.

The rubric is a different flavour of INDUCE-1's failure: a scoring shortcut that the template forbids (reference transcription instead of bare-letter format). It is worse in one respect: it agrees with the key 91% of the time, so it does not look broken.

## PINS FOR THE REGISTRAR

Content pins. These do not depend on rendering; I recomputed them from the committed artefact and from the DB.
- artefact_sha256 `475b68536c8e0f771ba82b71370f28bb4defe91fbe11315eb64953bd00b71eea`: sha256 of `json.dumps(artefact minus artefact_sha256, sort_keys=True, ensure_ascii=True)`. `induction.load_artefact(path, expect)` returns a RubricArtifact.
- rubric_sha256 `ace41ede9b19974aaa6c29881aff2e17dae353c0ce05f5d0e246bd3edf2a49e0`: UTF-8, 570 chars, all ASCII.
- reply_sha256 `094a3a98251245f59b52372575468cf4d48336e578b8ac1e1a69493e0a865f0d` (attempt 1). It is reproduced by `json.dumps({"rubric": rubric})` with the DEFAULT separators; the -1 reply used compact separators. So the reply can be recovered from the artefact alone.
- payload_sha256 `ac02ed756a855c5839eb2390bc1eeca0adbeec078a450d5f15b50b043686d8ac` (30,719 bytes, decompressed from the DB). Keys: model, max_tokens 8192, messages. No temperature key. System 1,124 chars, sha 67b62162; user 29,310 chars, sha a66db220.
- input_variant_ids: sorted-set sha256 `99484486d75774b379bd35713063022a8c05b8949b7b2d61045f95670d9abe50` (sha of `"\n".join(sorted(ids))`); ordered `89bed2562c1f8575ed0dbfd5b9980216aa346ef26d5837fbe574b7b775ef132a`.
- response id `d23d6906-16f8-47aa-926e-b5d613fe8f69`, provider azure:grok-4-1-fast-non-reasoning, finish 'stop', 120 completion tokens.

File pins at 541e2ae. The LF rendering is of record. `git hash-object` equals the blob for all 7 paths.

| path | blob | sha256-lf | sha256-crlf16 | working tree |
|---|---|---|---|---|
| experiment_results/archv2/induce_rubric_2/rubric_mcq_ARCH-V2-INDUCE-RUBRIC-2.json | blob:6f7773129c3d69e67f0fb728d78eba6bd96ad9fe | 45a14aac1805999ac58e7588083dd04fc26cf9e62fe17d7cea4ed6f2809900e9 | 38328c979e606115 | LF, 0 CR |
| experiment_results/archv2/induce_rubric_2/outcome.txt | blob:8a8a082827a8809478673fa9d7059a4630f745de | cc8d163e9467e3c80df5d4acb94b2ced111baf7ee9f934cfc59612d287ebc635 | 3e9cb4dc40a061db | LF, 0 CR |
| experiment_results/archv2/induce_rubric_2/input_variant_ids.json | blob:c4e92a46f52e72d7ea3d963a4c5ba289cae8f556 | 852264c9ebc69dfe94a08a16d0a5a97ab14637638575900a371e9d3f9cf952fc | 1e4d5ba52f5c8195 | LF, 0 CR |
| experiment_results/archv2/induce_rubric_2/induce_rubric_2_run.txt | blob:423bbf9298e6926fd28ca106e59c8f56c4a8d399 | e7acb5871d579e7b9243d671dad4b2c0518198df05f18b46e6be0421eab45224 | 8952d77c7d90d61e | CRLF (46 CR) |
| experiment_results/archv2/induce_rubric_2/induce_rubric_2_dryrun.txt | blob:38eb966b7a293c2e7f3fb3603f16d87fc12faffa | cccff1c3053e6a61a324b617fa9790ed57f7916eb32046c60149073b25ab5e6a | 29964d2ae728ee28 | CRLF (35 CR) |
| experiment_results/archv2/induce_rubric_2/attempts.db (binary, COMMITTED this time) | blob:883d1dac2af317713ec338db478d3925ca9ab30c | bytes eb05e0e6267cbddd88e063db7c05d61df7a5fd146a5e08548ac1c74c71054658 | n/a (binary) | bytes = the blob = the backup E:\TaxoArena_backup_2026-09-24\induce_rubric_2\attempts.db (same sha) |
| experiment_results/day_calls_2026-09-24.json | blob:2885bc10ee1fde29655771ad98d68da421ef2c71 | 74fc2f99ad20f9f4053b39b311eb9ede2bfce4fb41a6716721f98189a7e48c85 | working tree 8b96846e7b8c2e31 (CRLF, no final newline) | CRLF (91 CR) |

Commands:
- `git rev-parse 541e2ae:<p>`;
- `git cat-file blob <b> | sha256sum`;
- the same piped through `sed 's/$/\r/'` for CRLF, plus `head -c -1` for the day ledger;
- `git hash-object <p>`;
- `sha256sum` of the working tree.

Pin the artefact through `load_artefact(path, "475b6853...")`, which is content-based. If raw bytes are pinned, name sha256-lf.

## PER-CLAIM TABLE (Part A: validity)

| # | claim | check (mine) | got vs claimed | status |
|---|---|---|---|---|
| 1 | 1 invocation; attempt 1 VALID; reply 094a3a98 | attempts.db (ro, immutable): `invocation` 1 row (seq 1, 20:41:09.502303Z, payload ac02ed75, PENDING); `attempt` 1 row (no 1, failure_class NULL, finish stop); `transport` 0; `unresolved` 0; sha256(reply_text) recomputed | 1 / 1 / 0 / 0; reply sha EQUAL | CONFIRMED |
| 2 | invocation count | DB 1; day ledger (`git diff 0a77ac2 541e2ae -- day_calls...`): +1 row {test ARCH-V2-INDUCE-RUBRIC-2, calls 1, ts 22:41:39}, insertion only; totals by test: TRACE-TRUNCATION 2178 / CANARY-EPOCH2-RUNG 1252 / INDUCE-1 1 / INDUCE-2 1 = 3,432 (= 3,431 + 1); run stdout "1 attempt(s) with a reply, 0 transport error(s)" and "[ACCOUNT] appended 1 posted calls" | 1 = 1 = 1 of <= 6 | CONFIRMED |
| 3 | provider-side retries | wall time from invocation stamp (20:41:09.502303Z) to attempt commit (20:41:29.367162Z) = 19.865 s; latency_s 19.840 s (last HTTP try) | gap 0.025 s: no hidden retry (unlike -1's L1). posted_at == committed_at again (field misnamed, -1 L1 carried) | CONFIRMED (L1) |
| 4 | the reply of record = attempt 1 byte for byte; artefact derived with no edit | `json.loads(reply)` keys exactly ['rubric']; artefact.rubric == reply.rubric; the file bytes == `json.dumps(art, sort_keys=True, indent=1, ensure_ascii=True)+"\n"`; `load_artefact` accepts it | all EQUAL | CONFIRMED |
| 5 | artefact_sha256 475b6853 / rubric_sha256 ace41ede | recomputed (row 4) | EQUAL to the digit | CONFIRMED |
| 6 | the payload as pinned | body decompressed from the DB: 30,719 B, sha256 ac02ed75 = the READY pin = DB meta = the `--expect-payload-sha`; system sha 67b62162, user sha a66db220 = pins | EQUAL | CONFIRMED |
| 7 | selection 99484486 / 89bed256 | sha of the input_variant_ids.json list: sorted, newline-joined = 99484486; ordered = 89bed256; 40 distinct; all 40 stems found verbatim in the posted user turn | EQUAL | CONFIRMED (not re-selected from scratch; the -1 post-run review re-selected this same set independently, and the dry-run printed REPRODUCED) |
| 8 | V1 verbatim audit PASS | own 8-gram matcher, rubric vs the 40 input stems + 392 option texts (gen_view variant by variant_id, mmlu-pro-v2). Tokenizer A = `\w+` casefold (81 rubric grams); tokenizer B = alnum runs plus punctuation (107 grams) | 0 hits / 0 hits | CONFIRMED |
| 9 | V2 leak check PASS | rubric vs ALL eval_view variant stems + options (9,899 variants; 89,110 texts; all corpora): 0 hits at k = 8, 7, 6, 5 under A and under B. EVAL answer texts (response + source_row; 4,246 distinct, 2,800 of at least 12 chars): substring 0, 8-gram 0. reference (1,095 rows): raw 8-gram 0, answer substring 0. The only letters are the generic range "(A/B/C/...)"; the only numerals are list numbers and "Response 1 / 2" | 0 everywhere | CONFIRMED (L5 on my denominator) |
| 10 | V3 content-key counts PASS | the 40 inputs: contract MC_LETTER 40, side TRAIN 40/40, items 40, components 40; in eval_view: variant_id 0, item_id 0, component_id 0, stem_key 0 | EQUAL / 0 | CONFIRMED |
| 11 | V4 mode x, committed | the file bytes are the writer's rendering; committed in 541e2ae | as claimed | CONFIRMED |
| 12 | V5 PASS | `induce_fitness.v5(rubric)` on main (REGEX_LIST_SHA256 7b5af1d5 = module pin = runner pin; 12 form patterns): a True (5 matches), b True (0 form matches), c True (2 matches) | EQUAL to the outcome line | CONFIRMED (a PASS of a weak screen; see Part B) |
| 13 | order witness | event table: seq 1 launch 20:41:09.499296Z; seq 2 reply_committed 20:41:29.376176Z; seq 3 eval_view_opened 20:41:31.074854Z | 2 < 3 by sequence number and by every clock. attempt.committed_at .367162 vs event .376176: two clocks (L2) | CONFIRMED |
| 14 | the views unchanged | sha256 + mtime before and after (see header); mtimes predate the launch | unchanged | CONFIRMED |
| 15 | instrument = pinned | DB meta script_blob 286c750e, fitness_blob 28638dcf, induction_blob 19eb10fa, cache_blob 9edfc767 = the READY pins = `git rev-parse` at 0a77ac2 and HEAD = `git hash-object` in the working tree; `git diff --quiet 0a77ac2 541e2ae -- tools/ docs/ src/` passes | EQUAL | CONFIRMED |
| 16 | the file set is complete | `git show 541e2ae --name-only --format= \| wc -l` = 7 (6 run files + the day ledger); `git ls-files experiment_results/archv2/induce_rubric_2 \| wc -l` = 6 = `ls \| wc -l` = 6; `git status --porcelain --ignored` on the dir: 0 lines | complete, and the attempt cache is COMMITTED (closes -1's M1 for this run) | CONFIRMED |
| 17 | labels | outcome "LABEL: a RECIPE COMPONENT; no rubric-value or accuracy claim." = the ruling L16301 and the registration QUESTION L16328. The stage-'judge' deviation line asks for a NEW bracket; the bracket exists (L16330, "[ACCEPTED 2026-09-24 by READY_induce_rubric_2 ...]") | match | CONFIRMED (L3) |
| 18 | P1 / P2 HELD; falsifier not fired | 1 attempt, VALID, V1-V5 recomputed PASS | HELD / HELD / NOT FIRED | CONFIRMED |

## PART B: THE REGISTERED FITNESS READING

### B1. The C2 known-limit checks (registration L16339, C2)

| check | text found | reading |
|---|---|---|
| a brevity reward | none ("ignoring length/formatting" is a neutrality clause) | CLEAR |
| an anti-explanation / anti-reasoning rule excused by an "ignore / regardless of" clause | "ignoring length/formatting" is attached to the reasoning clause and excuses nothing; there is no anti-explanation rule | CLEAR |
| a format demand not built on "letter" | none. "no letter ... loses" is the prompt's own "may state no letter" case (fit; the pinned fit probe F4 says the same) | CLEAR |
| (beyond C2) the opposite direction: a PRO-explanation reward | "has sounder reasoning ...; tie only if both identical in ... reasoning quality" | FOUND: U2 below |
| (beyond C2) deference to the reference | "the stated option letter must exactly match the reference letter" | FOUND: U1 below |

The C2 list names the FN holes of the lexical screen that the READY found. The two defects below are in classes V5 was never built to see: V5 (a) accepts "Correctness of the final answer" and does not check what correctness is measured against. The held-out set had no reference-deference text.

### B2. U1: the rubric makes the reference the criterion (the orchestrator's concern). UNFIT ground 1. Severity: BLOCKER for adoption

The full system turn is rendered with `payload.build_system(load_rubric(artefact))` on main (payload.py blob:4b0af34d) and read in full; the scratch copy is system_turn.txt. What the judge reads, in order:
- Template, verify-first: "The question carries a reference solution (marked as produced independently; it may be wrong). Before critiquing, extract each model's FINAL ANSWER and check it against the reference and against your own reading of the question. A response whose final answer is wrong cannot win against a response whose final answer is right".
- Then "Your rubric:": "1) Correctness of the final answer: the stated option letter must exactly match the reference letter (A/B/C/...); no letter or wrong letter loses even if reasoning is strong."

(i) Does it instruct deference? YES.
- The rubric's clause 1 DEFINES "correct" as "matches the reference letter" and "wrong letter" as a mismatch with it. It leaves no room for the "own reading" check.
- The template's schema asks the judge to critique each response "against the rubric".
- The induction prompt told the inducer that the reference "may be wrong" (INDUCTION_SYSTEM 67b62162, read from the posted body). The rubric drops that qualifier.

(ii) The record's priors. CITED, NOT RECOMPUTED: they are on the x12 object (p2dca), not SPLIT-2.
- CONSENSUS-FIT: `experiment_results/x12_crossdomain/consensusfit_outcome.txt` L13-L19. REF +2.177 vs KEY +0.788 (ratio 2.76).
- Judge accuracy on key-decidable matches, by what the reference agrees with:
  - 0.922 when it agrees with the key-correct model (n 5,167);
  - 0.657 when it agrees with neither (n 391);
  - 0.226 when it agrees with the WRONG model (n 491).
- The residual 0.226 / 0.657 is the judge's independent verification. The template's verify-first block exists to protect it; clause 1 instructs it away.
- ORACLE (L1326-L1332): a perfect reference buys +16.4pp (0.612 -> 0.776, 55:6).

(iii) Quantified on the pilot's population, zero calls. Object: eval_view_REG.db of the split of record, sha e35b7518; corpus mmlu-pro-v2; vintage grok-reasoning-v0 (the pilot's only vintage); scripts refexp*.py.
- **v0 error rate: 133 wrong of 1,027 reference rows = 12.95%** (Wilson 95% 11.03-15.14%).
  - `correct` equals (answer == gt) on 1,027 of 1,027 rows.
  - 1 row per variant: 1,027 distinct variants = 1,027 items.
- Over the 7 stage-1 anchors of record (chemistry, computer science, economics, health, math, other, philosophy; L16223): 58 / 515 = 11.3%.
- Per anchor: physics 0.046 to engineering 0.267. Of the 7 stage-1 anchors: philosophy 10/42 = 0.238, health 10/55 = 0.182, other 16/90 = 0.178, chemistry 0.094, computer science 0.061, economics 0.056, math 0.055.
- Coverage: 1,027 of 3,673 EVAL variants (28.0%), and 1,027 of 3,492 items (29.4%), carry a v0 reference. The rest are reference NONE (M2).

Pair-level exposure. Population:
- the 46-model roster (model_registry ACTIVE; Meta-Llama-3-70B-Instruct absent);
- every unordered pair on every reference-bearing variant;
- both contestants saw the solver's ordering (the loader's rule; otherwise excluded);
- pick texts differ (the answer-disagreement filter).

This gives 606,377 pairs. Key-decidable pairs: 379,323 (345,530 reference-right + 33,793 reference-wrong). On those 379,323:

| cell | pairs | share | what clause 1 orders |
|---|---|---|---|
| reference right, the key-correct contestant agrees with it | 345,238 | 91.01% | the key's winner (aligned) |
| reference wrong, the WRONG contestant picked the reference's letter | 12,882 | 3.40% | the WRONG winner ("wrong letter loses" is applied to the right answer) |
| reference wrong, neither contestant picked it | 20,911 | 5.51% | both "wrong": the correctness advantage is erased and reasoning decides |
| reference right, the key-correct contestant does not agree (text duplicates / quirks) | 292 | 0.08% | n/a |

Shares are pair-weighted. The pilot samples N = 2 questions per pair per anchor, so its mix differs. The weights are a guide, not the pilot's realised share.

Illustration only (transported cell accuracies, not a measurement): suppose the rubric pushed the WRONG cell from 0.226 to 0 and the neither cell from 0.657 to 0.5. The loss would then be about 0.0340 x 0.226 + 0.0551 x 0.157 = 1.6pp of key-decidable reference-bearing verdicts. The size is modest. The DIRECTION is what disqualifies it: every lost verdict is a correlated error, concentrated on 133 questions, and the key-blind nominal (C1 / C1b) cannot see it. A more deferential judge is more decisive on exactly these matches, so c rises while realised wrong-direction rises.

(iv) Exposure depends on the contestant; it is not uniform. On the 133 wrong-reference questions (clusters = questions; binomial SE about 0.043 per model), the share of each model's picks that equal the wrong reference letter spans 0.218 (Mistral-7B-Instruct-v0.2) to 0.508 (arx_0314).
- The top three are all in ARENA12: arx_0314 0.508, gpt-4o-2024-08-06 0.496, iask_pro 0.489.
- gemini-3.1-pro_5-shots (ARENA12) is key-correct on 0.585 of these questions and agrees with the wrong reference on only 0.308. Clause 1 penalises exactly the model that is right where the reference is wrong.
- This is the CONSENSUS-FIT mechanism (models agreeing with the reference's errors are rewarded), now written into the criterion. It enters the k = 12 and k = 46 sub-boards with different compositions, so it need not cancel in C1's exponent. The sign on beta is unknown (not quantifiable at zero calls).

(v) Cause, for the record. INDUCTION_SYSTEM says the reference "may be wrong" and asks for "correctness of the final answer first". It never says that correctness is judged against the question rather than the reference. The model took the shortest operational reading. Like INDUCE-1, this is a gap in the registered prompt, not a run defect.

### B3. U2: an explanation-presence reward and suppressed ties. UNFIT ground 2. Severity: HIGH

- The rubric: "2) For ties in final answer correctness, soundness of reasoning: logical accuracy, relevance to question, fidelity to option meanings, and problem-solving validity ... tie only if both identical in correctness and reasoning quality."
- The template: "Prefer the response with fewer errors or unsupported steps in its reasoning. If neither has any, output TIE. Depth, breadth, scope, edge cases and elaboration are NOT criteria — a short correct response ties a long correct response." The user turn: "If both models are genuinely equivalent, output winner: \"TIE\" with confidence <= 0.5".

Where they differ:
- The template's criterion is ERRORS (a subtractive test). The rubric's is graded QUALITY ("sounder", "relevance", "problem-solving validity"), with TIE only for "identical" quality.
- A response with no reasoning therefore cannot tie a worked one. That rewards the presence of an explanation, which INDUCTION_SYSTEM forbids.

Measured on eval_view (empty.py; 165,369 responses of the 46 ACTIVE models on mmlu-pro-v2):
- 21,465 are empty (12.98%). That is all the responses of exactly 6 models: deepseek, flash_0shots_00_35_03, gpt4o(2024-05-13), opus_2shots_00_37_14, sonnet-3.5_0shots_09_34_29, sonnet_0shots_12_01_18, each at 1.000. The other 40 models have 0 empty responses.
- The loader replaces an empty trace with a one-line placeholder (rejudge_grok.robust_trace L137-L149, as the F1b ruling verified).
- None of the 6 is in ARENA12. They appear in 6 x 40 + 15 = 255 of the 1,035 pairs per anchor, and in 0 of the 66 ARENA12 pairs.

Where it bites:
- On every correctness-tied match involving one of the 6, the rubric directs a loss where the template directs a TIE. Under the disagreement filter, a correctness tie means both are wrong, or no reference is present and the judge cannot settle correctness.
- In the same pairs, "tie only if identical" also removes the template's TIE outlet in both-wrong matches.
- Ties feed |m| in cert.cbud_v, so C1b is directly exposed (the F1 ruling's own analysis, L16285).
- This is confined to the k = 46 side, so it cannot cancel in beta.
- The size depends on how often the judge follows the rubric over the template, which is UNMEASURED.

### B4. Other contradictions with V2_SYSTEM_TEMPLATE (the full system turn walked)

- **M1 (MEDIUM): naming and a positional default.**
  - The rubric names "Response 1 / Response 2". The template, user turn and schema name "Model A / Model B" (critique_a / critique_b). The judge must map them by position.
  - "Judge Response 1 superior if ...; Response 2 otherwise" is a default to the SECOND position. Suppose two responses are equal in correctness and equally sound but not "identical". Read literally, the rubric gives them to Response 2.
  - Dual order with TIE on flip converts a consistent positional default into flips and ties. It does not remove it from the single-order verdicts, and the record's position effect is large (POSITION-DECOMP 13.5pp).
- **M2 (MEDIUM): clause 1 has no referent on reference-NONE matches.**
  - About 71% of EVAL variants have no v0 row (B2 iii). On those matches "must exactly match the reference letter" is undefined.
  - The template's "The question carries a reference solution" is equally false there. That is pre-existing, L3 of the first READY.
  - The rubric now makes the missing object the definition of correctness. The judge may fall back to its own reading or treat both as mismatches (a correctness tie, then U2). Unmeasured.
- **L4 (LOW): "fidelity to option meanings".** The judge sees the stem only, plus the selected option's text per response and the reference's option text. It cannot check fidelity to options it is not shown. This is harmless beside U1 and U2.
- Consistent with the template, and noted for completeness: "no letter ... loses" (INDUCTION_SYSTEM's "may state no letter"); "ignoring length/formatting" (the template's bias suppression).

### B5. Against INDUCE-1's failure mode

It is the same class: a rubric that encodes a scoring shortcut the template forbids.

| | INDUCE-1 (ef9c9e87) | INDUCE-2 (ace41ede) |
|---|---|---|
| shortcut | response FORMAT (bare letter) | REFERENCE TRANSCRIPTION (letter == reference letter) |
| template clause contradicted | bias suppression (formatting "all equal") and verify-first | verify-first ("may be wrong ... your own reading") and the TIE rule |
| visibility | scored every real response 0; inert or tie-inducing; obviously broken | agrees with the key on 91% of key-decidable reference-bearing pairs; looks fit and passes V5 |
| harm | contestant-dependent via terseness | contestant-dependent via agreement with the reference's errors (0.218-0.508) and via empty traces (6 models, none in ARENA12) |

The F1 ruling declined option (i) for INDUCE-1 because it "would put a component known to contradict the template into data meant for stage-1 reuse" (L16292). The same ground applies here, and a FIT reading could not repair it: conditions may not edit the rubric.

### B6. Ruling

**UNFIT.** Consequences under the registered scope:
- The artefact stays VALID and of record as minted (475b6853 / ace41ede) and is labelled NOT ADOPTED.
- No judged call uses it.
- The $rubric slot goes to THE AUTHOR, who chooses among an empty slot, GENERIC_RUBRIC (sha256 67f843eb..., measured by STACK-NORUBRIC) and other options.
- It is never a fourth attempt.
- PILOT-K46 open item 1 stays open.

If the author chooses another induction, it needs a NEW registration. That registration's prompt must say that final-answer correctness is judged against the question, with the reference as evidence that may be wrong, and that a response without reasoning is not penalised for it. The fitness screen should add a reference-deference class (for example "match(es)? the reference", "reference letter", "agree(s)? with the reference") and a held-out set that contains such texts. That is forward advice for the specialist, not a condition here.

## FINDINGS BY SEVERITY

- **U1 BLOCKER (adoption; not validity).** Reference-as-criterion. It contradicts the template's verify-first block and its own induction prompt, and fails the registration's fitness question. v0 error 12.95% (133/1,027); clause 1 departs from the key on 8.91% of key-decidable reference-bearing pairs (3.40% wrong winner, 5.51% advantage erased); exposure is contestant-dependent. Fix: NOT ADOPTED; the slot goes to the author (B6).
- **U2 HIGH.** An explanation-presence reward, and TIE only when "identical". It contradicts INDUCTION_SYSTEM and the template's TIE rules. It hits 6 all-empty models (255 of 1,035 pairs per anchor; 0 of the 66 ARENA12 pairs), so it is asymmetric across C1's sub-boards. Fix: as U1.
- **M1 MEDIUM.** "Response 1 / 2" vs "Model A / B"; the "Response 2 otherwise" default. Fix: none possible (no edits); disclose.
- **M2 MEDIUM.** Clause 1 is undefined on the ~71% reference-NONE matches. Fix: disclose; the author's choice of slot content removes it.
- **M3 MEDIUM (forward; screen scope).**
  - V5 (a) certifies "correctness" without checking its referent, and the READY held-out set held no reference-deference or pro-explanation text. V5's PASS here is a PASS on wording (review rule 5).
  - Fix: for any future induction, add the classes in B6 to the screen and to a held-out set frozen before the regexes are read.
- **L1 LOW (carried from -1).** posted_at == committed_at (the field is misnamed). No hidden HTTP retry this time: the gap is 0.025 s.
- **L2 LOW (carried).** Two clocks: attempt.committed_at 20:41:29.367162Z vs the event row .376176Z. The event table (seq, at) is the witness of record.
- **L3 LOW.** outcome.txt's static line "this run needs a NEW registrar bracket, named by the READY" is satisfied by the bracket at L16330. The registrar cites it in the outcome.
- **L4 LOW.** "fidelity to option meanings" asks about options the judge does not see.
- **L5 LOW.** My V2 answer-text denominator (4,246 distinct; 2,800 of at least 12 chars) differs from the instrument's printed 2,704 (at least 12 chars), a normalisation difference. The result is 0 hits under both.

## WHAT THIS REVIEW DOES NOT SHOW

- The realised effect of this rubric on any verdict, tie rate, nu or beta: nothing was judged, and GENERIC_SYSTEM + rubric stays UNMEASURED.
- A recomputation of CONSENSUS-FIT or ORACLE: both are cited from the committed outputs, on a different object.
- The pilot's realised pair mix: the shares above are pair-weighted over all eligible pairs.
- The integrity of the E: backup beyond its sha equality.
- Rule 1 note: the EVAL counts above (reference errors, empty traces) are post-run DIAGNOSTICS of an already-minted artefact. They must not be inputs to any future induction prompt.
