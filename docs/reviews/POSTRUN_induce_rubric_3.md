# POST-RUN review: ARCH-V2-INDUCE-RUBRIC-3 (run b653b0a from main d6db49c; READY 598669b)

Adversarial reviewer, 2026-09-25. Zero calls. Record data read-only; every DB opened `mode=ro&immutable=1`. Checklist READING A (blind: no file of the judge-design-specialist's reading B was opened). SPLIT-2 views hashed before and after every check: gen c2930c60...0ec, eval e35b7518...369, `ls --full-time` diff empty, sidecars (-wal/-journal/-shm) 0 by `ls -a | grep -c`. attempts.db sha256 96108864... before and after. Scratch (not committed): leak3.py (V1/V2/V3), trig.py, a1_rubric.txt, system_turn_3.txt, user_cases_3.txt.

## VERDICT

**VALID.** 2 invocations; attempt 1 FITNESS (V5 d2), attempt 2 VALID and of record; V1-V5 PASS; every sha recomputed with no difference; P1 FAILED, P2 HELD, falsifier NOT FIRED.

**READING A: UNFIT.** One item FOUND at the UNFIT level: **K8** (the rubric's "Call verdict 'A', 'B', or 'TIE'" conflicts with SCHEMA_INSTRUCTION's value set; the pipeline parser maps "A"/"B" to INVALID). Every other item CLEAR, three with MEDIUM disclosures. Under the VERDICT RULE ("FIT iff no item reads UNFIT in EITHER reading") the artefact is **NOT ADOPTED** whatever reading B says, and the $rubric slot takes the pre-decided FALLBACK GENERIC_RUBRIC (sha256 67f843eb7a632ae5bd411a9debcbaf9dedccd362e0c8355c366c6d85cb89b1dc). P3 (FIT in both readings) is therefore FAILED. Never a fourth attempt.

### Item table (reading A; the artefact of record, rubric_sha256 9e0a4022...)

Rubric clauses, numbered by me (verbatim):
- R1 "The judge evaluates which response (Model A or Model B) better answers the MCQ."
- R2 "First, determine the correct option letter by independently solving the question, using the reference solution (if provided) only as one possibly erroneous input among others."
- R3 "Correctness of final answer is primary: prefer the response matching the judge's correct letter; TIE if both match or neither does."
- R4 "If final answers differ in correctness, the correct one wins regardless of reasoning."
- R5 "If both correct or both incorrect, compare reasoning quality only: prefer the one with fewer factual errors, logical gaps, or unsupported steps; TIE if reasoning error counts are equal."
- R6 "Ignore length, formatting, or presence/absence of explanation."
- R7 "Responses may end with a clear letter choice (possibly followed by option text), state no letter, or be truncated/empty (noted as selecting none or a letter)."
- R8 "Call verdict 'A', 'B', or 'TIE'."

Cases, code-rendered with synthetic text, no EVAL text: (i) question + REFERENCE_MARKER "[Reference solution — produced independently, may be wrong]" + "(B) beta", A worked (B), B worked (C); (ii) the same with no reference (NONE); (iii) side B = `robust_trace("", "C", opts)` = `The model selected option C: "gamma".`; (iii') `The model did not provide a prediction.`. System turn = `payload.build_system(payload.load_rubric(artefact))`, 2,918 chars, sha256 dafbc5ea036350540c8b882f981cbc45556097a2b5cd578fd45da087a4d0e501 (template shas as `_base.TEMPLATE_SHAS`: v2_system_template 0d064ee2, user_template 4c142bc1, schema_instruction 708a6cb3). Read in full, with the user turn and SCHEMA_INSTRUCTION.

| item | reading | rubric text | template clause met | cases |
|---|---|---|---|---|
| K1 reference as criterion | **CLEAR** | R2 "determine the correct option letter by independently solving ... reference ... only as one possibly erroneous input"; R3 "matching the judge's correct letter" | verify-first "check it against the reference and against your own reading"; marker "may be wrong" | (i): correctness = the judge's letter, not the reference's; no clause makes the reference decisive |
| K1b reference distrusted by default / own working overrides whenever they disagree | **CLEAR** (disclosure M-B) | R2 "only as one possibly erroneous input among others" | verify-first (symmetric: reference AND own reading) | no "ignore", no "distrust", no "on disagreement, own working wins". "possibly erroneous" restates "may be wrong". It does shift the framing toward the judge's own solve ("the judge's correct letter" is the yardstick; the reference is "one input among others"): the direction S6 registered. The FOUND bar is not met |
| K2 reasoning-presence reward on correctness ties | **CLEAR** | R5 "compare reasoning quality only: prefer the one with fewer factual errors, logical gaps, or unsupported steps"; R6 "Ignore ... presence/absence of explanation" | "Prefer the response with fewer errors or unsupported steps ... Depth ... elaboration are NOT criteria" | (iii) both right: subtractive error test, and R6 neutralises presence explicitly |
| K2b brevity reward / anti-reasoning / format demand | **CLEAR** | R4 "the correct one wins regardless of reasoning" is scoped to "If final answers differ in correctness"; R7 is descriptive; R3's letter is the MC_LETTER contract | "A response whose final answer is wrong cannot win ... whatever its reasoning looks like" (R4 restates it) | no brevity reward; reasoning is still compared in R5 (not the B29f class); "state no letter" responses are "neither match" (a correctness verdict under the contract, as ruled for -2's "no letter ... loses") |
| K2c placeholder walk | **CLEAR + DISCLOSURE** (M-C) | R5 as above; R7 "truncated/empty (noted as selecting none or a letter)" | "fewer errors or unsupported steps" | (iii) both right: the placeholder has 0 errors, so it ties a flawless worked answer and beats a worked answer with one error: the INHERITED template property. Nothing "automatic". "logical gaps" is the only word beyond the template; a judge could count "no derivation" as a gap, which R6 forbids. (iii') a no-prediction note vs a wrong worked answer: both incorrect, so R5 compares errors and the non-answer can win: inherited, disclosed |
| K3 TIE narrowed | **CLEAR** | R5 "TIE if reasoning error counts are equal"; R3 "TIE if both match or neither does" | "If neither has any, output TIE"; user turn "genuinely equivalent -> TIE" | TIE covers equal counts (0 = 0 included): at least as broad as the template; no "identical", no "never", no "last resort" |
| K3b over-tie (M3 walk, both-right case explicit) | **CLEAR** (ruling below; disclosure M-A) | R3 "TIE if both match or neither does" vs R5 "If both correct or both incorrect ... prefer the one with fewer ... errors ...; TIE if reasoning error counts are equal" | "When BOTH final answers are right: Prefer the response with fewer errors or unsupported steps ... If neither has any, output TIE" | both right, A one unsupported step, B none: R5 prefers B, as the template does. See the ruling |
| K4 positional default / order-dependent criterion; names | **CLEAR** | R1 "(Model A or Model B)"; no "otherwise", no default, no first/second | "CRITIQUE Model A ... Model B" | no criterion depends on order |
| K5 reference NONE | **CLEAR** | R2 "(if provided)"; correctness = the judge's own solve | (template's "The question carries a reference solution" is false on NONE: pre-existing, -1 READY L3, not the rubric's) | (ii): every criterion is defined |
| K6 options not shown | **LOW, disclosed** | R2 "determine the correct option letter"; R3 "the judge's correct letter" | the judge sees the stem only (payload D5 bracket; INDUCTION_SYSTEM "without its options list") | the letter is recoverable only through the reference line and the "[This model's selected answer: (X) text]" injection (rejudge_grok.maybe_resolve); if neither response picked the right option the judge can still rule "neither matches" |
| K7 template walk | **CLEAR except R8** (goes to K8) | R6 = bias suppression; R2's "First" = verify-first's "Before critiquing"; R4 = "cannot win ... whatever its reasoning"; R5 = the both-right rule; silent on confidence and TIE confidence <= 0.5 | each clause of V2_SYSTEM_TEMPLATE, the user turn and SCHEMA_INSTRUCTION walked | no contradiction; the user turn's "based solely on the logical rigour and domain soundness" vs the system turn's "Correctness first" is a pre-existing template tension that R3 does not create |
| **K8 output-format conflict** | **FOUND = UNFIT** | R8 "Call verdict 'A', 'B', or 'TIE'." | SCHEMA_INSTRUCTION `"winner": <Model A, Model B, or TIE>`; template step 4 `declare the winner — either "Model A", "Model B", or "TIE"`; user turn `"winner": "Model A, Model B, or TIE"` | all cases. Grounds below |

### K8 ruling (the orchestrator's question: conflict or redundant echo?) — CONFLICT

1. R8 is an output-format instruction. It names the verdict labels, in quotes, as literal tokens. The user turn names the step "Step 4 — Verdict", and the only verdict slot in the output is the JSON `winner` field.
2. Its labels are not the schema's. 'A' / 'B' vs "Model A" / "Model B". A "merely redundant echo" restates the same content (the -2 READY L4 case: "nothing else" echoing "a single valid JSON object and nothing else"). R8 changes the token set, so both cannot be obeyed literally in the `winner` field.
3. The conflict has teeth in the pipeline of record. judge_v2/writer.py L100 parses with `rejudge_grok.parse_judge`, and L178-L180 map `raw.upper()` through `{"MODEL A", "MODEL B", "TIE", "DRAW", "EQUAL"}`; the regex fallback L186-L190 uses the same map. A `"winner": "A"` or `"B"` parses to **INVALID**. TIE is the only label in both sets, so literal compliance converts every decisive verdict to INVALID and leaves only TIEs: a push toward INVALID/TIE, not a symmetric noise. INVALID counts as wrong under convention A (CONTEXT §3), and ties feed |m| in cert.cbud_v.
4. It also departs from the induction prompt it was written from: S9 "Call the two responses Model A and Model B, as the judge's instructions do". R8 reads as a compression of S9 that drops "Model".
5. The strongest counter-reading: R1 defines "(Model A or Model B)", so 'A' abbreviates the same referent, and "Call" means "name" rather than "output". This reading makes R8 a restatement of step 4's decision space in shorthand (LOW). I reject it. The item tests conflict with SCHEMA_INSTRUCTION, and the quoted tokens are what the parser consumes. How often the judge would obey R8 over the three schema statements is UNMEASURED (zero calls). The rubric cannot be edited under any condition.

### K3b ruling (M3; the orchestrator's question) — R3's TIE is SUPERSEDED by R5, not an over-tie

- R3 opens with "Correctness of final answer is **primary**". A primary criterion's tie is by definition resolved by a secondary one.
- R5 is conditioned on exactly R3's tie condition ("both correct or both incorrect" = "both match or neither does") and directs "prefer the one with fewer ... errors". If R3's TIE were a final verdict, R5 would be dead text on every case it names. The reading under which every clause has effect is the lexicographic one: correctness tie (R3), then reasoning (R5), then TIE on equal counts.
- On the both-right case with one side having fewer errors, the rubric read whole directs the template's preference. K3b CLEAR.
- The residual risk is wording: the token "TIE" serves both as a criterion-level tie (R3) and as the verdict label (R5, R8). A reader who stops at R3 over-ties on both-right. That is MEDIUM, disclosed (M-A). This is the READY's M3 compression risk, but here the conjunct survives in R5.
- My K8 FOUND decides reading A without this ruling. If reading B reads K3b FOUND, the VERDICT RULE records the disagreement; the outcome (UNFIT) is the same.

### K1 / K1b (the orchestrator's question: does R2 move the verify-first balance?)

- It moves the FRAMING, not the rule. The template's verify-first block is symmetric: check against the reference AND against your own reading, and say nothing about which wins on disagreement. R2 makes "the judge's correct letter" the yardstick and demotes the reference to "one possibly erroneous input among others".
- The words K1b names are absent: ignore; distrust by default; own working overrides whenever they disagree. The judge's letter is determined "using" the reference, so the reference stays inside the determination. CLEAR.
- Disclosure M-B (MEDIUM, direction only, not measured): the record's priors make the reference the judge's strongest input. CONSENSUS-FIT: judge accuracy 0.922 when the reference agrees with the key-correct model vs 0.226 when it agrees with the wrong one. ORACLE: +16.4pp. On the pilot population, v0 is wrong on 12.95% (the -2 post-run diagnostics, cited, not recomputed; rule 1: never an induction input). Any de-weighting of the reference by a non-reasoning judge costs accuracy on the ~87% of reference-bearing matches where the reference is right. S6 registered this direction; its size is UNMEASURED.

## PINS FOR THE REGISTRAR

Content pins (recomputed from the DB and the committed artefact):
- artefact_sha256 `9f0e4ce9f2991f5caf410ed09c77853c63e0c04a5a0f7bce3136989aef81e7a2` = sha256(`json.dumps(artefact minus artefact_sha256, sort_keys=True, ensure_ascii=True)`); `induction.load_artefact(path, "9f0e4ce9...")` returns a RubricArtifact; `payload.load_rubric` accepts it.
- rubric_sha256 `9e0a4022b58b30268e36617b46e13105354d22f2b17f6e83f3e3099ee18c04b1` (UTF-8, 914 chars, all ASCII).
- reply of record (attempt 2): reply_sha256 `d0d27f080540d355b5669030274d18bce458ec596ddeea2d98dcd1ffbe3b773f`, 928 chars, = `json.dumps({"rubric": rubric})` with the DEFAULT separators; response id `89b37a3c-d4fb-40f1-b8f9-fc704058bec8`; finish 'stop'; 192 completion tokens; provider azure:grok-4-1-fast-non-reasoning.
- attempt 1 (FITNESS, not of record): reply_sha256 `a5d81ab5015fc83a1257fc2a17a3bfbdfeb9313d4e5003dde8040c606b486386`, 461 chars; response id `94c37dda-5eba-4f9e-bcdb-02c936d7a02b`; finish 'stop'; 96 completion tokens.
- payload_sha256 `e5ace2a5840fc6c15bd51fff10f6eefc0ee9b4dde9286147f7bdbeadcd19553a` (31,955 bytes, decompressed from BOTH attempt rows; the two bodies are byte-identical); keys model / max_tokens 8192 / messages; no temperature; system 2,360 chars sha e95c59b2 (= the component file); user 29,310 chars sha a66db220.
- selection: sorted-set `99484486...` / ordered `89bed256...`, recomputed from input_variant_ids.json (40 distinct).

File pins at b653b0a (the LF rendering is of record; `git hash-object` = the blob for 7 of 7):

| path | blob | sha256-lf | sha256-crlf16 | working tree |
|---|---|---|---|---|
| experiment_results/archv2/induce_rubric_3/rubric_mcq_ARCH-V2-INDUCE-RUBRIC-3.json | blob:29e544dc2d79a97cf6c320cc9e6ad96a3cc314ad | ddfc407b87230f0b9d57ec3a42f59ce62428bf1025c4785c3fc6fdf5ae0a7049 | 4859d942faca7218 | LF, 0 CR |
| experiment_results/archv2/induce_rubric_3/outcome.txt | blob:03a52b854e5ee9ce6645b21bf5622e6078fb0c71 | f9718b5a56763b9518d69300367411e53bf88c48d77ed15e5129055f0fa00100 | b39b8e49464039d1 | LF, 0 CR |
| experiment_results/archv2/induce_rubric_3/input_variant_ids.json | blob:c3d3184245bc0d8256e7e2ab761c81832a30ac3e | a59ac8101eed2c6db08843f73689d961544bc8beff7f931cf5791184c17b0462 | baba9803a0bafef6 | LF, 0 CR |
| experiment_results/archv2/induce_rubric_3/induce_rubric_3_run.txt | blob:5fb2470f6ec8b4640cbc2038c9e9695f0f6f8a2f | cc2ac44e8c049673b1712a41b70151ef192be3ab3741c4250e949fc798510894 | 452295bbce31ba0a | CRLF (52 CR), wt = crlf16 |
| experiment_results/archv2/induce_rubric_3/induce_rubric_3_dryrun.txt | blob:31f8998ece469ba81b17dc53941a74652e7bc293 | ed4594ef8146e4e04c97a0e64b01a0925b9bd6822725a59ecab59b4f69a3c242 | eb1093b2d1eebef0 | CRLF (35 CR), wt = crlf16 |
| experiment_results/archv2/induce_rubric_3/attempts.db (binary) | blob:fceac2b1ecd50d8068dc00530959477ac242a8f0 | bytes 96108864a5416c5f420a59a1aba9e16da4c972b8ada31e67c07877e778dde980 | n/a (binary) | bytes = blob = E:\TaxoArena_backup_2026-09-24\induce_rubric_3\attempts.db (same sha256) |
| experiment_results/day_calls_2026-09-25.json | blob:9ce82e61fa742b8f2d8a1e1a4a4a88a74eae15ce | c23c38817275f61564cc9377594325375f099cecb65a08e5031bb3ef3f919b4d | 6c62a70053b2f822 (with final newline) | CRLF (7 CR), no final newline: wt sha256 32e86774cd64a121 |

Commands: `git show b653b0a --name-only --format= | wc -l` (7); `git rev-parse b653b0a:<p>`; `git cat-file blob <b> | sha256sum`; the same through `sed 's/$/\r/'` (plus `head -c -1` for the day ledger); `git hash-object <p>`; `sha256sum` of the working tree and of the E: backup.

## PER-CLAIM TABLE (Part A: validity)

| # | claim | check (mine) | got vs claimed | status |
|---|---|---|---|---|
| 1 | 2 invocations; attempt 1 FITNESS, attempt 2 VALID | attempts.db (ro, immutable): `invocation` 2 rows (seq 1 02:21:20.684969Z, seq 2 02:21:24.348259Z, both payload e5ace2a5); `attempt` 2 rows (1 FITNESS, 2 NULL); `transport` 0; `unresolved` 0 | 2 / 2 / 0 / 0 | CONFIRMED |
| 2 | invocation count in 3 places | DB 2; day ledger day_calls_2026-09-25.json: 1 row {ARCH-V2-INDUCE-RUBRIC-3, "--run --go", calls 2, ts 04:21:52}; `grep -c INDUCE-RUBRIC-3 experiment_results/day_calls_*.json` non-zero only in the 09-25 file (1); stdout "2 attempt(s) with a reply, 0 transport error(s)" and "[ACCOUNT] created ... with 2 posted calls" | 2 = 2 = 2, <= 6 (CEILINGS) | CONFIRMED |
| 3 | no hidden HTTP retry | invocation -> attempt commit: 3.6417 s vs latency 3.5336 s (gap 0.108 s); 3.5459 s vs 3.5244 s (gap 0.022 s) | no retry-sized gap | CONFIRMED (L1 carried: posted_at == committed_at) |
| 4 | reply of record = FIRST valid, byte for byte; artefact derived with no edit | attempt 2 is the first `failure_class IS NULL`; triggers `attempt_after_valid` / `invocation_after_valid` present (no row after it); `json.loads(reply)` keys ['rubric']; artefact.rubric == reply.rubric; file bytes == `json.dumps(art, sort_keys=True, indent=1, ensure_ascii=True)+"\n"` | EQUAL | CONFIRMED |
| 5 | artefact_sha256 9f0e4ce9 / rubric_sha256 9e0a4022 | recomputed | EQUAL to the digit | CONFIRMED |
| 6 | payload as pinned | both bodies decompressed: 31,955 B, sha e5ace2a5 = READY pin = DB meta = `--expect-payload-sha`; bodies identical | EQUAL | CONFIRMED |
| 7 | instrument = pinned | DB meta script b13fca84, fitness 4550533c (base 28638dcf), induction 147e6874, cache e6b34439 = the READY pins = `git hash-object` = `git rev-parse HEAD:`; `git diff --quiet d6db49c b653b0a -- tools/ docs/ src/` passes; `git diff --name-only d6db49c b653b0a \| wc -l` = 7 (the run files) | EQUAL | CONFIRMED |
| 8 | V1 verbatim audit PASS | own 8-gram matcher, rubric vs the 40 stems + 392 option texts (gen_view variant, mmlu-pro-v2). Tokenizer A `\w+` casefold (137 grams), B alnum + punctuation (178 grams); all 40 stems found verbatim in the posted user turn | 0 / 0 hits (attempt 1: 0 / 0) | CONFIRMED |
| 9 | V2 leak check PASS | rubric vs ALL eval_view variant stems + options (9,899 variants, 89,110 texts): k = 8, 7, 6 -> 0 under A and B; k = 5 -> 0 under A, 2 under B, both the punctuation run `' a ' , '` (FORTRAN stem vs "'A', 'B'"), below the registered k = 8. EVAL answer texts (response + source_row; 4,247 distinct, 2,799 of >= 12 chars): substring 0, 8-gram 0. Reference rows 1,095: raw 8-gram 0, answer substring 0. Letters in the rubric: A, B only (verdict labels) | 0 at the registered k | CONFIRMED (L3 on my denominator) |
| 10 | V3 content-key counts PASS | 40 inputs: contract MC_LETTER 40, side TRAIN 40/40, 40 items, 40 components; in eval_view: variant_id 0, item_id 0 (item and side), component_id 0, stem_key 0 | EQUAL / 0 | CONFIRMED |
| 11 | V4 mode x, committed | file bytes = the writer's rendering; committed in b653b0a | as claimed | CONFIRMED |
| 12 | V5 jv2-v5-4 on BOTH attempts | `induce_fitness_3.v5` on main (`regex_list_v54_sha256()` = 714268738c75...): attempt 1 FAIL, firing ['d2'] only (a' YES 2, b 0, c YES 1, d1 0, e 0, f 0); attempt 2 PASS, firing [] (d2 satisfied by the single cue 'independent'; "possibly erroneous" is not a registered cue). jv2-v5-3 baseline: both PASS | EQUAL to the outcome lines | CONFIRMED |
| 13 | attempt 1's burn is faithful to the REGISTERED list | cues in attempt 1: "by own calculation" (registered: own (working\|reading\|solution)); "only as input, not authority" (registered: "one input"; "not the (yardstick\|answer key\|key)"); SCEPTIC_ENTRIES L115-L132 carry neither | the screen did what was registered | CONFIRMED (a screen FP, not a build defect; see H1) |
| 14 | order witness | event seq 3 reply_committed 02:21:27.916229Z < seq 4 eval_view_opened 02:21:31.358589Z | 3 < 4 by sequence and clock; attempt.committed_at .894189 vs event .916229 (two clocks, L2 carried) | CONFIRMED |
| 15 | views unchanged | sha256 + `ls --full-time` before and after; mtimes 2026-09-24 20:23 precede the run | unchanged | CONFIRMED |
| 16 | file set complete | `git show b653b0a --name-only --format= \| wc -l` = 7 (6 run files + day ledger); `git ls-files .../induce_rubric_3 \| wc -l` = 6 = files in `ls`; `git status --porcelain --ignored` on the dir: 0 lines | complete; attempt cache committed | CONFIRMED |
| 17 | labels | outcome "LABEL: a RECIPE COMPONENT; no rubric-value or accuracy claim." = registration QUESTION; artefact label "MCQ rubric, population mmlu-pro-v2 TRAIN (ARCH-V2-INDUCE-RUBRIC-3, jv2-induce-5)"; stage-'judge' deviation line names the READY bracket, which exists (L17019) | match | CONFIRMED |
| 18 | P1 FAILED / P2 HELD / falsifier NOT FIRED | attempt 1 not VALID; attempt 2 V1-V5 PASS; 1 formal failure < 3 | FAILED / HELD / NOT FIRED | CONFIRMED |
| 19 | P3 | reading A UNFIT (K8) | **FAILED** (under the VERDICT RULE, regardless of reading B) | scored here for the registrar |

## THE H1 REALISATION (disclosure; descriptive only; attempt 1 is not of record and this reading changes nothing)

Attempt 1 verbatim: "The judge evaluates Model A vs Model B to determine which better answers the MCQ. Judge correctness of final answer (A/B/C/...) by own calculation, using reference solution (if provided) only as input, not authority. Prefer response with correct final answer; if tie, prefer one with fewer reasoning errors/unsupported steps. TIE if both correct or both wrong with equal reasoning quality. Ignore length, formatting, presence/absence of reasoning."

| item | reading of attempt 1 |
|---|---|
| K1 | CLEAR ("only as input, not authority") |
| K1b | CLEAR ("not authority" = S6's "never the yardstick"; no ignore / override-on-disagreement) |
| K2 / K2b | CLEAR ("Ignore ... presence/absence of reasoning"; no brevity or format demand) |
| K2c | CLEAR + the inherited disclosure ("fewer reasoning errors/unsupported steps" is the template's own wording) |
| K3 | CLEAR, LOW: "equal reasoning quality" is graded wording, but it is tied to the preceding error test and is not "identical" |
| K3b | CLEAR: "TIE if both correct or both wrong WITH equal reasoning quality" carries the M3 conjunct |
| K4 / K5 | CLEAR ("Model A vs Model B"; "(if provided)") |
| K6 | LOW ("(A/B/C/...)" letters; "own calculation" presumes a computable item) |
| K7 | CLEAR |
| K8 | CLEAR (no output-format instruction) |

- **Reading: attempt 1 would have read FIT in reading A.** H1 is REALISED in the broad sense (V5 burned a checklist-fit reply). The class is (d2), the held-out fit_neg d2 FP class (HF01, HF10), not the post-hoc d1 / e / f probes the READY named. The burn cost one attempt. It did NOT land on the fallback.
- The screen's two verdicts are inverted against the checklist. V5 FAILED the reply that reads FIT, and PASSED the reply of record, which reads UNFIT on K8. V5 has no output-format class (b's form patterns are about response form), so K8 was outside its reach by design (V5 SCOPE).
- Counterfactual, not of record: had attempt 1 passed, it would have been the reply of record and read FIT here.

## FINDINGS BY SEVERITY

- **U1 BLOCKER (adoption; not validity). K8 FOUND: "Call verdict 'A', 'B', or 'TIE'" conflicts with SCHEMA_INSTRUCTION.**
  - The token set differs from `"winner": <Model A, Model B, or TIE>` (and from template step 4 and the user-turn JSON).
  - `rejudge_grok.parse_judge` (L178-L180, fallback L186-L190; used by judge_v2/writer.py L100) parses "A" / "B" as INVALID, so literal compliance leaves only TIE parseable.
  - Fix: none on this artefact (no edits). NOT ADOPTED; the slot takes GENERIC_RUBRIC 67f843eb... (the FALLBACK, no author question, never a fourth attempt).
  - Forward, for any future induction (advice, not a condition): add an output-label class to the screen (quoted verdict labels other than "Model A" / "Model B" / "TIE"), and consider normalising "A" / "B" in parse_judge only by its own registration (it would move the parser's AST pin).
- **H1 HIGH (realised; screen quality). V5 burned a reply that reads FIT (attempt 1, d2) and passed one that reads UNFIT (attempt 2, K8).**
  - The burn is faithful to the registered cue list (row 13).
  - d2 passed attempt 2 on the single incidental cue 'independent' (from "independently solving"): the whole-text weakness L2 of the READY, here in the permissive direction.
  - Fix: none now. Disclose in the outcome beside the held-out FP 9/28 figure.
- **M-A MEDIUM (disclosed). R3 "TIE if both match or neither does" is a criterion-level tie that shares its token with the verdict.**
  - Ruled superseded by R5 ("primary"; R5 is conditioned on the same event), so K3b is CLEAR.
  - A stop-at-R3 reader over-ties on both-right. Unmeasured.
- **M-B MEDIUM (disclosed). R2 re-frames verify-first toward the judge's own solve** ("the judge's correct letter"; the reference "only as one possibly erroneous input among others").
  - K1b CLEAR (no ignore / distrust / override clause).
  - The direction is the registered S6's. Its cost for a non-reasoning judge, against the record's reference priors, is UNMEASURED.
- **M-C MEDIUM (disclosed). Placeholder consequences inherited from the template's subtractive test.**
  - (iii) A correct placeholder beats a correct worked answer with one error.
  - (iii') A no-prediction note can beat a wrong worked answer in a both-incorrect match.
  - "logical gaps" is the one word beyond the template that a judge could apply to "no derivation"; R6 forbids that reading.
- **L1 LOW (carried).** posted_at == committed_at (misnamed field); no hidden retry (gaps 0.108 s / 0.022 s).
- **L2 LOW (carried).** Two clocks: attempt.committed_at 02:21:27.894189Z vs event .916229Z. The event table is the witness of record.
- **L3 LOW.** My V2 answer denominator (4,247 distinct; 2,799 >= 12 chars) differs from the instrument's 2,704 (normalisation). 0 hits under both. A k = 5 tokenizer-B punctuation run (`' a ' , '`) is below the registered k = 8.
- **L4 LOW (K6).** "the correct option letter" presumes options the judge does not see. The letter is recoverable only via the reference line and the selected-answer injection.
- **L5 LOW.** The run-operator's dry-run opened eval_view at 02:20:37.483737Z. That is a second pre-run eval_view open beside the READY reviewer's 01:56:55Z: a different process, zero calls, covered by the carried disclosure ("the dry-run process opened eval_view before any call").

## WHAT THIS REVIEW DOES NOT SHOW

- How often grok-4-1-fast-non-reasoning would emit "A" / "B" under R8: zero calls, UNMEASURED. The K8 ruling is textual plus the parser's behaviour.
- Any effect of the rubric on verdicts, ties, nu or beta. Any rubric value.
- Reading B. It was not read. The combined verdict is the registrar's, under the VERDICT RULE (with K8 FOUND here, UNFIT regardless).
- A recomputation of CONSENSUS-FIT, ORACLE or the 12.95% v0 error rate. They are cited from the record, on other objects. Rule 1: they are diagnostics, never inputs to an induction.
- The integrity of the E: backup beyond sha equality (same physical disk).
