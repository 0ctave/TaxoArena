# DELTA READY review: ARCH-V2-INDUCE-RUBRIC-2 at 27ad75c (inserted 2026-09-24 above the 4dcfd3e review, which stands below unchanged)

Reviewer: adversarial-reviewer, 2026-09-24. Zero calls. Record data read-only.
Branch: worktree-agent-ac04323cdcce696f8. Tip: 27ad75c (parent 25b14c5 = merge of 4dcfd3e and main d3e9716; that merge brings in only this file).

## VERDICT: READY for --run, with the conditions below. Held-out figures: FP 2/18, FN 13/17

The held-out set was written and frozen BEFORE I read the jv2-v5-3 regexes:
- file: scratchpad heldout.json, 18 fit + 17 unfit;
- sha256 4b44076086d53856ce6cba4651b9128cc068d69aae71c1f59e3075a845d94e29 (heldout.py e50a409b...);
- frozen at 2026-09-24T22:24:56+02:00;
- the runner script asserts the sha before scoring.

The fit texts are the rubrics the actual prompt would elicit. They are varied restatements of "correctness of the final answer first, then soundness of the reasoning, then neutrality on length / format / explanation". The unfit texts are new paraphrases of brevity rewards, format demands and anti-explanation rules.

| rule | FP (fit texts that FAIL) | FN (unfit texts that PASS) |
|---|---|---|
| jv2-v5-3 (27ad75c, 7b5af1d5) | 2 / 18 = 11.1% (Wilson 95% CI 3.1-32.8%): H-F5, H-F16 | 13 / 17 = 76.5% |
| jv2-v5-2 (4dcfd3e, a9040d5d), same set | 3 / 18: H-F5, H-F16, H-F17 | 14 / 17 |
| jv2-v5-3 on the 58 pinned (in-sample) texts | 0 | 0 |

OVERFITTING, confirmed:
- The builder's 0/0 is in-sample.
- On held-out data the H1 + M1 revision improves V5 by exactly 1 FP and 1 FN over v5-2.
- My earlier 8/14 FP figure on v5-2 came from probes I built after reading its regexes, so it was adversarially inflated. On natural fit rubrics, v5-2 gave 3/18.

Why READY despite FP 11%:
- A further round of regex tuning is shown, by this very table, not to generalise.
- The FP cost is bounded. A false positive burns one attempt of <= 3, and its matching pattern is disclosed in the attempt record and in outcome.txt. The worst case is a spurious UNDETERMINED that goes to THE AUTHOR, never an unfit artefact of record.
- FN is backstopped by the registered post-run fitness reading (F1b change 7).
- The two held-out FPs are both disclaimers:
  - H-F5: "A response is not favoured or disfavoured for being short, long, plain or formatted." (passive "is not favoured" is not a CUE);
  - H-F16: "A bare letter is acceptable and is judged on its correctness alone; ..." (exclusivity "letter ... alone").
- If a FITNESS failure's pattern shows such a disclaimer, the post-run reader must say so in the outcome. It still stays a formal failure: never a re-roll.

CONDITIONS (registrar, before the run; none moves a pin):
- C1: record the held-out figures above and the frozen set's sha as the V5 generalisation estimate beside REGEX_LIST 7b5af1d5.
- C2: add D1-D4 (below) to the KNOWN LIMITS of record (the selftest's KL1-KL4 stay as they are). The post-run fitness reader checks the rubric of record specifically for:
  - a brevity reward;
  - an anti-explanation or anti-reasoning rule excused by an "ignore / regardless of <form word>" clause;
  - a format demand not built on the word "letter".
- C3: the stage-'judge' bracket (at the end of this section).

## Pins for the registrar (hash kind named; LF is the rendering of record)

| object | pin |
|---|---|
| payload (dry-run body, 30,719 bytes; byte-identical to the 4dcfd3e dry-run body, `cmp`) | sha256 ac02ed756a855c5839eb2390bc1eeca0adbeec078a450d5f15b50b043686d8ac |
| INDUCTION_SYSTEM | sha256 67b621624d63e416e985c440db713ca23e550598c5f93d9ce580f2ffbb891ebf |
| INDUCTION_USER_TEMPLATE / CONTRACT_DESCRIPTIONS / user turn | sha256 8f098049e6af71fd509fc80d760ed7a4f29013cc21a93de3283737dc6cbfd53a / d40c4b0ae9b6829157d99609cfa8b92486fad109f6b588f0ff8deb210672b416 / a66db2209ac1b4efc360f08f9bdb0962fbf3a8000d1841d69f879d896b45f1d6 |
| REGEX_LIST_SHA256 (jv2-v5-3, 12 form patterns, 18 CUE entries, IGNORECASE) | 7b5af1d513df318031d77a14b7c8673051a075957ca97ffcc287cdfdc516fa54 |
| C-V5-probe corpus (B1-B11 / F1-F5) | sha256 329cd697fd457924b5437e754bbb2c2c6d935cb40a10b65f370da7a5d4740490 |
| READY probe corpus (B12-B29 / F6-F19 / F20-F43) | sha256 30fecaffeca205de42ea08f7a257032df73bcbda0ea78f6d7b639a6c59537327 |
| CONTROL_FIT_TEXT | sha256 a7b8ebb0d36b069204703095eb8531a2565bf0e347ccff820bde94c9f590aef0 |
| selection / exclusion list | sorted 99484486d75774b379bd35713063022a8c05b8949b7b2d61045f95670d9abe50 / ordered 89bed2562c1f8575ed0dbfd5b9980216aa346ef26d5837fbe574b7b775ef132a / 68c0b960a4a7bedc76db079cdc2e0f01d5ef0b2fc4304f5486706cb27b71418a |
| induce_run_2.py (THE INSTRUMENT) | blob:286c750ee1c23550d0337840dbb8c8e17ed13617 / sha256-lf16:4788c861b9a57947 (crlf16 2229ce9693ea4d5d; worktree LF) |
| induce_fitness.py | blob:28638dcfcd7f464404af6e085d2de99d32ada70d / sha256-lf16:d90fb9b4b4fd9bee (crlf16 6eed82f6e976dec7; worktree LF) |
| induce_run_2_selftest.py | blob:658e6a26685ac3da70d76d6079788c6392392977 / sha256-lf16:bbff2203938e5a1b (crlf16 e75ef2a64c84ad86; worktree LF) |
| induction.py (unchanged since 4dcfd3e) | blob:19eb10fae855f858c45b5da588080c85badb0096 / sha256-lf16:ae104501a564bf62 / sha256-crlf16:7acbf09317a733a1 (worktree CRLF) |
| induce_cache_2.py (unchanged) | blob:9edfc767160a6f0e4ef49f5caa12b0ded61c6939 / sha256-lf16:e49bdf0a0076c4ab (worktree LF) |
| accepted_tests_ledger.py (unchanged) | blob:463262220c059f659a8c4110683af39739df5590 / sha256-lf16:605c6d384db939c1 / sha256-crlf16:a1970f2b4a03c420 (worktree CRLF); CEILINGS["ARCH-V2-INDUCE-RUBRIC-2"] = 6 |

How the pins were derived:
- `git rev-parse 27ad75c:<p>`, `git cat-file blob | sha256sum`, the CRLF rendering through `sed 's/$/\r/'`, and `git hash-object` on the worktree (= blob for all 6).
- The pins agree with the builder's claims to the digit.

## Per-claim table (delta)

| # | claim | result | command / script | got vs claimed | sev |
|---|---|---|---|---|---|
| 1 | V5 jv2-v5-3, 12 form patterns, REGEX_LIST 7b5af1d5 | CONFIRMED | `F.regex_list_sha256()`; `len(F.FORM_PATTERNS)`; dry-run line "jv2-v5-3, 12 form patterns" | equal | - |
| 2 | `build_rules()` with defaults = the rule of record | CONFIRMED | `F.regex_list_sha256(F.regex_list(F.build_rules())) == F.REGEX_LIST_SHA256` | True; the module constants are `_RULES = build_rules()` | - |
| 3 | READY probe corpus 30fecaff | CONFIRMED | `S.ready_sha()` | equal | - |
| 4 | the pinned texts equal my originals byte for byte | PARTLY | exec of my scratch adv_probe.py (sha256 a07e6fb5... = the builder's cited sha) and neut_probe.py (d7faf9b4... = cited), dict compare | U1-U16, G1-G14 and N1-N24: 54/54 identical. B28 identical. B29 is NOT my original: "Reasoning errors are irrelevant; ignore the steps entirely." drops the leading "The correct final answer wins. " (I quoted it truncated in the review text). As pinned, B29 fails on (a), so it is VACUOUS for the (c)-negation mutant (it FAILS with c_negation off too). My full original FAILS with c_negation on and PASSES with it off. B28 carries that kill (explicit suite check) | LOW (D5) |
| 5 | 0 FP / 0 FN on the 58 pinned texts; B0-B11, F0-F5 unchanged | CONFIRMED (in-sample) | selftest | yes; probe sha 329cd697 unchanged | - |
| 6 | 44 mutants, all killed | CONFIRMED | `len(S.mutants())` = 44; each mutant's regex_list sha differs from the base (44/44 distinct); `grep -c 'MUTANT KILLED'` = 44 under python and -O | equal; the mutants are real | - |
| 7 | induce_run_2_selftest 319/319, judge_v2 174/174, python and -O; lint 0 | CONFIRMED | `^\[SELFTEST-EJ\] PASS` / `FAIL` counts; lint_opens | 319/0, 319/0, 174/0, 174/0, rc 0; "248 .py files; 0 finding(s)" | - |
| 8 | payload ac02ed75 unchanged; INDUCTION_SYSTEM and induction.py did not move | CONFIRMED | dry-run; `cmp body.bin body2.bin`; `git rev-parse 4dcfd3e: / 27ad75c:` | body byte-identical; induction.py 19eb10fa both; payload.py 4b0af34d, loader.py da4fcbbf, _base.py 6f25e4ce unchanged since 3cc505f | - |
| 9 | the -1 files are untouched | CONFIRMED | `git rev-parse 3cc505f: / 4dcfd3e: / 27ad75c:` | induce_run 4c9c0a20, induce_run_selftest a2f60ceb, induce_cache a143c286 at all three | - |
| 10 | the runner changed only V5_LIST_SHA + a bracket | CONFIRMED | `git diff 4dcfd3e 27ad75c -- induce_run_2.py` | 1 constant, 1 docstring bracket | - |
| 11 | the dry-run reproduces, read-only | CONFIRMED | scratch dry.py (TAXOARENA_DATA_ROOT = main); `tasklist` (0 python, 0 java before); sha256 + stat before and after | sorted 99484486 / ordered 89bed256 REPRODUCED; payload ac02ed75; gen c2930c60... mtime 20:23:39.418, eval e35b7518... mtime 20:23:51.222 identical after; 0 sidecars; no induce_rubric_2/ in either tree | - |
| 12 | the new exemptions cannot let an INDUCE-1-style rubric through | REFUTED (in part; see D1-D3) | white-box probes (below), and v5-2 from `git show 4dcfd3e:...induce_fitness.py` for the regression column | "ties go to" is additive only (it adds catches). The "short correct" exemption and the concessive guard are NEW holes. The "ignore / regardless" narrowing did not close the excusal hole: it narrows it to exactly the form words an INDUCE-1 rubric would use | MEDIUM |

## Defects (delta)

- **D1 (MEDIUM, new with v5-3; FN, backstopped).** The `short_correct_exempt` switch (`short(?:er|est)?\b(?!\s+(?:and\s+|but\s+)?(?:in)?correct\b)`), added so that N11 passes, lets a brevity reward through.
  - Probe: "The correct final answer wins. If both are correct, the shorter correct response wins; then fewer reasoning errors." -> V5 PASS (v5-2: FAIL).
  - Not in KL1-KL4.
- **D2 (MEDIUM, new with v5-3; FN).** The concessive guard also lets a verb-first reward through: "The correct final answer wins. Prefer, even when both are correct, the shorter response. Then sound reasoning." -> PASS (v5-2: FAIL). KL3 records the object-after-concessive form only.
- **D3 (MEDIUM, pre-existing, NOT closed by the narrowing; FN).** A narrowed CUE still excuses its whole guard clause. Three probes pass under BOTH v5-2 and v5-3:
  - "The correct final answer wins. Regardless of formatting, a response containing any explanation scores 0. Prefer sound reasoning otherwise." -> PASS. This is INDUCE-1's core rule ("Score 0 ... explanations").
  - "Ignore letter case and penalize any extra text. The correct final answer wins; sound reasoning breaks ties." -> PASS.
  - "Score 1 if the final answer is the correct option letter and nothing more is written. Sound reasoning is not required." -> PASS (no letter-bound "nothing else").
  - Plausibility from the jv2-induce-4 prompt: LOW. The prompt describes free-form reasoning responses and orders neutrality, so none of these is its natural reading. The post-run reader catches each on sight (C2).
- **D4 (LOW, new with v5-3; FP).** The (c) negation guard fails a fit rubric that puts "irrelevant" in the reasoning clause: "The correct final answer wins. If tied, prefer the response with sounder reasoning, length being irrelevant." -> FAIL on (c) (v5-2: PASS). This is KL1, already disclosed.
- **D5 (LOW).** B29 is truncated and vacuous (claim 4). Fix at the next touch: pin the full text "The correct final answer wins. Reasoning errors are irrelevant; ignore the steps entirely." Not needed for the READY, because B28 kills the (c)-negation mutant through its explicit check.
- **The remaining held-out misses (FN, backstopped).** 13 of 17 pass. Examples:
  - brevity: "succinct", "lower word count", "rambles / crisp", "easier to skim and less wordy", "economy of expression", "avoids superfluous explanation";
  - format: "ends with the line 'The answer is (X)'", "lone option letter on the final line", "<answer>X</answer>", "stated as a single character";
  - penalty verbs "Deduct for any text beyond the chosen letter" and "marked down" (the pattern has `marks? down` only);
  - reward for "the most thorough explanation" chosen by "choose".

  The lexical screen does not generalise on FN, which is what F1b change 7 anticipated.

White-box probes: these were written AFTER reading the v5-3 regexes, so they are not held-out and they are reported separately from the held-out table. WB-U1 to WB-U7 and WB-F1 to WB-F4 are quoted in D1-D4. WB-F4 "A response is not favoured for being short or long." FAILS; it is the same passive-CUE gap as H-F5.

## (6) Stage 'judge' bracket (unchanged from the 4dcfd3e review; C3)
At the -2 registration's HYGIENE / POPULATION line (programme L16330):
`[ACCEPTED <date> by READY_induce_rubric_2: ARCH-V2-INDUCE-RUBRIC-2's V2 leak check (and its dry-run) opens eval_view through data_v2.views.open_eval("judge") (VIEWS-AUDIT-STAGE not merged); the stage is a label only (views._open L48-L65: read-only, sealed, expect_sha256 e35b7518...); accepted for THIS run only, under the INDUCE-RUBRIC-1 conditions: the order witness, the no-call-after-open flag, V2 failure never a re-post.]`

Scratch (not committed): heldout.py / heldout.json (the frozen set), run_heldout.py, v52.py (v5-2 extracted by git show), dry.py, body2.bin.

---

# READY review: ARCH-V2-INDUCE-RUBRIC-2 at 4dcfd3e

Reviewer: adversarial-reviewer, 2026-09-24. Zero calls. Record data read-only.
Branch: worktree-agent-ac04323cdcce696f8. Tip: 4dcfd3e (parent dc2171d = merge of a02a9c1 and main f9cd77c).
Record: registration 7e13897 (programme L16326-L16348); F1 ruling L16274-L16324; F1b ruling, verbatim, L16350-L16475 (f9cd77c).

## VERDICT: NOT READY for --run

The gate conditions registered for the READY are met:
- C-V5-neg, C-V5-pos and C-V5-probe: all 16 probe texts match the programme exactly, and B1-B11 FAIL, F1-F5 PASS.
- Q1 and Q3: exact.
- Pins, selftests, lint and the payload all reproduce.

What blocks the READY is one uncovered direction of V5: FALSE POSITIVES on fit rubrics (H1).
- In my own probes, V5 fails 8 of 14 ordinary fit rubrics.
- Among the ways of restating the neutrality clause that INDUCTION_SYSTEM itself instructs, 7 of 24 trip (b).
- The ruling's scope statement puts the reviewer's reading behind the false-negative direction only. Nothing rescues a fit reply that V5 rejects. That rejection is a formal failure: it consumes an attempt and heads toward a spurious UNDETERMINED that goes to the author.
- F1b ruled NOT READY for exactly one such false positive (F2), on exactly this ground ("risks a spurious UNDETERMINED sent to the author").
- The fix costs zero calls and moves only the V5 pins (see "Pins" below).

The instrument is otherwise ready. After the fix, a delta review needs to check only:
- induce_fitness.py;
- the selftest's probe set;
- the re-pinned shas.

## Pins the registrar records (hash kind named; LF is the rendering of record)

STABLE: these do not move under the H1 fix.
| object | pin |
|---|---|
| payload (dry-run body, 30,719 bytes) | sha256 ac02ed756a855c5839eb2390bc1eeca0adbeec078a450d5f15b50b043686d8ac |
| INDUCTION_SYSTEM (1,124 chars) | sha256 67b621624d63e416e985c440db713ca23e550598c5f93d9ce580f2ffbb891ebf |
| INDUCTION_USER_TEMPLATE (197 chars) | sha256 8f098049e6af71fd509fc80d760ed7a4f29013cc21a93de3283737dc6cbfd53a |
| user turn (dry-run) | sha256 a66db2209ac1b4efc360f08f9bdb0962fbf3a8000d1841d69f879d896b45f1d6 |
| CONTRACT_DESCRIPTIONS (canonical JSON) | sha256 d40c4b0ae9b6829157d99609cfa8b92486fad109f6b588f0ff8deb210672b416 |
| C-V5-pos CONTROL_FIT_TEXT | sha256 a7b8ebb0d36b069204703095eb8531a2565bf0e347ccff820bde94c9f590aef0 |
| selection | sorted-set 99484486d75774b379bd35713063022a8c05b8949b7b2d61045f95670d9abe50 / ordered 89bed2562c1f8575ed0dbfd5b9980216aa346ef26d5837fbe574b7b775ef132a; exclusion list 68c0b960a4a7bedc76db079cdc2e0f01d5ef0b2fc4304f5486706cb27b71418a |
| induction.py | blob:19eb10fae855f858c45b5da588080c85badb0096 / sha256-lf16:ae104501a564bf62 / sha256-crlf16:7acbf09317a733a1 (the worktree file is the CRLF rendering) |
| induce_cache_2.py | blob:9edfc767160a6f0e4ef49f5caa12b0ded61c6939 / sha256-lf16:e49bdf0a0076c4ab (worktree LF) |
| accepted_tests_ledger.py | blob:463262220c059f659a8c4110683af39739df5590 / sha256-lf16:605c6d384db939c1 / sha256-crlf16:a1970f2b4a03c420 (worktree CRLF); CEILINGS["ARCH-V2-INDUCE-RUBRIC-2"] = 6 |

AS BUILT AT 4dcfd3e: these MOVE with the H1 fix. Do NOT pin them as of record until the delta review.
| object | pin at 4dcfd3e |
|---|---|
| REGEX_LIST_SHA256 (jv2-v5-2, 10 form patterns, IGNORECASE) | a9040d5d098df446325eda0c5afac299df17c9d279d08786459fe41ae9d12399 |
| probe corpus B1-B11 / F1-F5 | sha256 329cd697fd457924b5437e754bbb2c2c6d935cb40a10b65f370da7a5d4740490 |
| induce_fitness.py | blob:88329c6f5bb23c7bef4180ed297e1982bd2af0f6 / sha256-lf16:c03ccf764610ea87 (crlf16 f8097479806f1ca0; worktree LF) |
| induce_run_2.py (the instrument; carries V5_LIST_SHA) | blob:a211c95aea85c11530c91fb43fa67e614fd44266 / sha256-lf16:ff0fb00e8408ba9d (crlf16 de51a0fcc9cea60d; worktree LF) |
| induce_run_2_selftest.py | blob:a658f2df1a0983462d86c19f8659688fec78c2d5 / sha256-lf16:ed77e2a0466e6055 (crlf16 2e65e4cf5a2231a2; worktree LF) |

Every value above was recomputed with `git rev-parse 4dcfd3e:<path>`, `git cat-file blob <b> | sha256sum`, the CRLF rendering through `sed 's/$/\r/'`, `git hash-object`, and a Python evaluation of the constants. All agree with the builder's table to the digit.

## Per-claim table

| # | claim | result | command / script | got vs claimed | sev |
|---|---|---|---|---|---|
| 1 | Q1: the OLD->NEW sentence is exact; INDUCTION_SYSTEM 67b62162; swapping NEW back for OLD gives 73d9ed4e | CONFIRMED | python: `I.INDUCTION_SYSTEM.count(NEW)`, `.count(OLD)`, sha of `.replace(NEW,OLD)` | NEW x1, OLD x0; 67b62162...1ebf; swap 73d9ed4e7c4f78e3... = the a02a9c1 value in the F1b notes | - |
| 2 | Q3: a guard in induce() and build_prompt() | CONFIRMED | `git diff 3cc505f 4dcfd3e -- induction.py`; selftest checks "F1b Q3" (math / instruction / agentic refused; induce('math') refused before any open) | message identical to the ruling; the only other callers (archv2_pilot/selftest.py L421 / L697, judge_v2/selftest.py L734) pass "mcq" | - |
| 3 | V5 = jv2-v5-2; REGEX_LIST a9040d5d; probe 329cd697 | CONFIRMED | `F.regex_list_sha256()`, `S.probe_sha()` | equal to the module pins and the runner's V5_LIST_SHA | - |
| 4 | the probe texts equal the programme's verbatim block | CONFIRMED | scratch probe_cmp.py: parses `- Bk "..."` / `- Fk "..."` in the programme L16353-L16463 (at 4dcfd3e) with `\n` read as a newline, then compares to PROBE_UNFIT / PROBE_FIT | 16 of 16 identical, none missing or extra | - |
| 5 | B0-B11 FAIL, F0-F5 PASS | CONFIRMED | `F.v5()` on each | B0: a=F b=F c=F; B1-B11: all FAIL on (b), with the patterns printed; F0-F5: all PASS | - |
| 6 | 19 mutants killed | REFUTED (count) | `len(S.mutants())`; `grep -c 'MUTANT KILLED'` in the transcript | 18 mutants, 18 killed (10 form patterns + 3 (a)/(c) + guard + contrast + 3 CUE) | LOW (L1) |
| 7 | selftest 170/170 under python and -O | CONFIRMED | `python [-O] induce_run_2_selftest.py`; count `^\[SELFTEST-EJ\] PASS` / `FAIL` | 170 / 0 in both; rc 0 | - |
| 8 | judge_v2 selftest 174/174 under python and -O | CONFIRMED | same, for selftest.py | 174 / 0 in both; rc 0 | - |
| 9 | lint 0 | CONFIRMED | `python lint_opens.py` | "248 .py files; 0 finding(s); 17 allowlisted" | - |
| 10 | the dry-run reproduces 99484486 / 89bed256 and payload ac02ed75 | CONFIRMED | scratch dry.py (`R.dry_run()`, TAXOARENA_DATA_ROOT = main checkout), body written to scratch | sorted 99484486..., ordered 89bed256..., "REPRODUCED"; payload ac02ed75...86d8ac, 30,719 bytes | - |
| 11 | the views are untouched by the dry-run | CONFIRMED | `sha256sum` + `stat` before and after; `ls -a \| grep -c -- '-wal\|-journal'` | gen c2930c60... mtime 2026-09-24 20:23:39.418 (849,633,280 B), eval e35b7518... mtime 20:23:51.222 (454,049,792 B); identical after; 0 sidecars; no python/java process (`tasklist`) before; no induce_rubric_2/ created (`ls \| grep -c` = 0 in both trees) | - |
| 12 | the -1 files are byte-identical | CONFIRMED | `git rev-parse 3cc505f:<p> 4dcfd3e:<p>` | induce_run 4c9c0a20, induce_run_selftest a2f60ceb, induce_cache a143c286: equal | - |
| 13 | the merge dc2171d brought in docs only | CONFIRMED | `git diff --name-only a02a9c1 dc2171d \| wc -l` = 5, all docs/; `git diff f9cd77c 4dcfd3e --stat` = the 6 tool files only (docs equal to main) | - | - |
| 14 | pin table (6 files) | CONFIRMED | see Pins | all 6 blob / lf16 pairs equal | - |
| 15 | every change is registered or ruled | CONFIRMED | `git diff --name-only 3cc505f 4dcfd3e \| wc -l` = 11 (5 docs + 6 tools); `git diff --no-index induce_run.py induce_run_2.py` read in full | runner changes (a)-(f) + F1b are all traceable (test id / out dir / FITNESS class / selection pin / V5 in classify and finish / V4 gated on V5 / outcome lines / stage disclosure). Unregistered but cosmetic: the dry-run prints the full system turn and 900 chars of the user turn; ARTEFACT_LABEL gains the test id | - |

## Hunt results

### (2) My own probes (scratch adv_probe.py, neut_probe.py; texts below)
Unfit rubrics (want FAIL): 3 of 16 caught, so 13 missed (81%).
Fit rubrics (want PASS): 6 of 14 pass, so 8 false positives (57%).
Neutrality paraphrases tripping (b): 7 of 24.

Misses by class, with how plausible each is from the NEW prompt (it describes free-form responses and orders "must not reward or penalise length, formatting, or the presence or absence of an explanation"):

FALSE POSITIVES (fit rubric FAILS; not backstopped): HIGH (H1)
- "A longer or shorter response is neither better nor worse." -> reward_form
- "An explanation is neither required nor penalized." -> penalise_form
- "Don't reward length or formatting, and don't penalise a missing explanation." -> penalise_form (contractions are not CUEs)
- "A response is not better because it is longer, shorter, or more elaborately formatted." -> reward_form
- "A longer response does not score higher." -> reward_form
- "A short correct response wins over a long incorrect one." -> reward_form
- "Neither length nor formatting nor the presence of an explanation earns or loses credit." -> penalise_form
- G5 "The response with the correct final answer wins, even if its explanation is brief. If both are correct, the response whose reasoning contains errors loses." -> reward_form
- G7 "A correct final answer wins. If both final answers are correct, the response whose reasoning is more rigorous wins; a longer response does not win for being longer." -> reward_form
- G8 "Penalise errors in the explanation, and prefer the response with the correct final answer; sound reasoning breaks ties." -> penalise_form
- G11 "The final answer letter alone determines correctness; the reasoning is then checked for errors." -> exclusivity
- G12 "1. A correct final answer beats a wrong one.\n2. If both are correct, the response with sounder reasoning wins, even when it is shorter.\n3. Otherwise TIE." -> reward_form
- G13 "1. Check each final answer against the correct option; the reference may be wrong.\n2. A response that states no letter has no final answer.\n3. Between equally correct answers, fewer reasoning mistakes wins.\n4. Penalise factual errors in the working, not its length." -> penalise_form
- G14 "The correct final answer wins. If both final answers are equally correct, prefer the response whose reasoning is valid and complete; a concise response is not better or worse than a long one." -> reward_form
- G4 "...2. Right answer beats wrong answer..." (no "final answer" or "correct answer") -> fails (a); also "Correctness first: the right option wins. Then prefer sound reasoning." fails (a)

Plausibility: HIGH for the neutrality restatements and the concessive "even if brief / even when shorter". The prompt tells the model to write this clause, and a model paraphrasing an instruction is the ordinary case. The literal clause passes (C-V5-pos). "Penalise errors in the explanation / working" is also a natural reasoning criterion. The failures are correlated across attempts: the same body is re-posted and the style repeats, so three FITNESS failures in a row are much likelier than p^3.

FALSE NEGATIVES (unfit rubric PASSES; backstopped by the reviewer's fitness reading): MEDIUM (M1)
- Brevity reward in uncovered vocabulary: U4 "Prefer responses that get straight to the point...", U7 "...fewer words...", U8 "...avoids unnecessary detail wins", U12 "...quicker to read...", U13 "Brevity is a virtue... less text is better" ("brief\w*" does not match "brevity").
- Format demands with no letter vocabulary: U3 / U14 (JSON-only), U5 ("formatted as 'Answer: X'"), U10 (bold **X**), U9 (Markdown / bullets / headings lose), U11 ("A good response is a bare option letter").
- CUE excusal of an unrelated clause: U15 "3. Regardless of the reference, the shorter response wins remaining ties.", U16 "3. Ignore the reasoning and prefer the concise response when still tied."
- (c) met by a NEGATED reasoning criterion: "Score 1 if the final answer is correct; the soundness of the reasoning does not matter." -> V5 PASS; likewise "Reasoning errors are irrelevant; ignore the steps entirely."
- Plausibility from the new prompt: LOW. The explicit neutrality clause and the response description remove the INDUCE-1 cause, and none of these is the natural reading of the prompt. The reviewer's post-run reading is the registered backstop (F1b change 7).

### (3) Q1 against the judge's actual view: CONFIRMED, one LOW nuance
- Stem only: loader.py L335-L336 (robust_trace per trace; "the judge never sees an options list: the question block is the stem only"), and the payload.py D5 bracket L45-L48.
- Reference "(X) option text": loader.render_reference L228-L230, used at L374-L375 (mcq).
- "each followed, when its chosen letter can be read, by that letter with its option's text": rejudge_grok.maybe_resolve L152-L163 appends "[This model's selected answer: (X) text]" when pred resolves to A-J within range. The letter is the extractor's pred.
- An empty trace is REPLACED by robust_trace L137-L149 ("The model did not provide a prediction." / "The model selected option X: ..." / "The model predicted: ..."). The ruling acknowledged this.
- Nuance (L3): the sentence says the judge always sees a reference, but the loader admits NO-REFERENCE matches (the D5 (3) MIXED path). This is harmless to a rubric, and it is the ruling's exact text, so it is not to be changed here.

### (4) The prompt as the model sees it (body rebuilt from the dry-run: system 1,124 chars, user 29,310 chars; read in full)
Ruling: FIT. A competent model would write "final-answer correctness first, then reasoning soundness, then neutrality":
- the system turn orders exactly that;
- it names the free-form, step-by-step response shape;
- it forbids length and format rewards.

The contract description "one of the lettered options (A, B, C, ...); the final answer is one option letter" is true of the contract and sits beside that response description. My reading is that it does not by itself invite a format spec. Its likeliest echo, "the final answer is the option letter the response commits to", is fit and passes (F5, FIT_PHRASINGS).

Residual invitation (LOW, L4): the system turn's own "Reply with a single JSON object and nothing else". INDUCE-1's "no other text" is the same phrase class. It cannot be removed without a new registration. V5's no_other_text and exclusivity patterns cover the letter-bound echo.

### (5) The dry-run on the record views
See table rows 10-11. The views were read with no other reader (`tasklist` showed no python.exe or java.exe). The sha and mtime were identical before and after. The dry-run process opened eval_view (disclosure C5, carried).

### (6) eval_view under stage "judge" for -2: ACCEPTABLE, under the same conditions as -1
data_v2/views.py `_open` L48-L65: the stage only selects which view kind is admitted. The open is `ro.open_ro(require_sealed=True, expect_sha256=manifest sha)`: read-only, sealed, sha-pinned. Nothing about the label changes what is read.

The conditions are carried unchanged and executed in the selftest:
- the V2 order witness (reply committed < eval_view opened, refused otherwise);
- the in-process flag that refuses any call_judge_full after the open;
- V2 failure = NOT OF RECORD, never a re-post.

VIEWS-AUDIT-STAGE is still `drafted` (queue.json L4066).

Bracket the registrar must add at the -2 registration's HYGIENE / POPULATION line (L16330):
`[ACCEPTED <date> by READY_induce_rubric_2: ARCH-V2-INDUCE-RUBRIC-2's V2 leak check (and its dry-run) opens eval_view through data_v2.views.open_eval("judge") (VIEWS-AUDIT-STAGE not merged); the stage is a label only (views._open L48-L65: read-only, sealed, expect_sha256 e35b7518...); accepted for THIS run only, under the INDUCE-RUBRIC-1 conditions: the order witness, the no-call-after-open flag, V2 failure never a re-post.]`

### (7) Journal, ceiling, outputs, labels: CONFIRMED
- The write-ahead journal is the -1 DDL, imported and changed by exactly two asserted substitutions: FITNESS added to the failure_class CHECK, and SCHEMA_ID archv2-induce-rubric-2-cache-v1. The invocation seq CHECK is 1..6; triggers refuse a call after a valid reply, a 4th attempt, a 4th transport error and an unresolved orphan.
- The guard: planned = 3 - attempts, so posted + planned = transports + 3 <= 6. It never refuses a relaunch that the cache admits.
- The selftest executes: the 4th invocation refused before the post; 3 x FITNESS -> UNDETERMINED + FALSIFIER FIRED; a transport stop, an identical-body relaunch and orphans; KeyboardInterrupt; write-once refusal of a second launch.
- OUT_REL is experiment_results/archv2/induce_rubric_2 and does not exist yet (count 0).
- outcome.txt carries: V1-V5; "V5 SCOPE (F1b change 7)"; "UNDETERMINED: three formal failures; the slot goes to THE AUTHOR"; the V2-failure author line; P1 / P2 including V5; the F1 disclosures 1-5 and the four carried disclosures; the stage deviation.
- The post-run UNFIT path is a record rule, stated in V5_SCOPE ("NOT ADOPTED ... THE AUTHOR, never a fourth attempt"). No code path re-posts after a valid reply (trigger invocation_after_valid).

## Defects

H1 (HIGH, blocks READY): V5 false positives on fit rubrics, the direction that has no backstop.
Fix, zero calls, builder then registrar re-pin:
(i) CUE: add
- contracted negations `\b(?:do|does|did|must|should|will|may|is|are)n[’']?t\b` + the same verb set as the long form;
- `\bneither\s+required\s+nor\s+penali[sz]ed\b`;
- `\bnot\s+(?:any\s+)?(?:better|worse)\b`;
- `\b(?:does|do|should|must|will)\s+not\s+(?:win|score|earn|gain|lose)\w*`;
- `\bneither\s+better\s+nor\s+worse\b`.

(ii) In reward_form, a concessive guard: a reward object preceded within the clause by `\beven\s+(?:if|when|though)\b` does not count.

(iii) In penalise_form, bare `explanations?` and `working` as objects do not count when preceded by `(?:errors?|mistakes?|flaws?|gaps?|claims?)\s+in\s+(?:the\s+|its\s+|their\s+)?`. Also "earns or loses credit" in a neither/nor clause (covered by the neither-nor cue).

(iv) Exclusivity: exempt "letter alone determines / decides" (or drop "alone" and rely on (c) and the other patterns); the builder decides.

(v) Optional, for (a): admit `\bright\s+(?:final\s+)?(?:answer|option)\b` and `\bcorrectness\b`.

(vi) PIN the texts listed under "False positives" above as F6-F20 (must PASS), and U1-U16 / the negated-(c) texts as a documented KNOWN-LIMIT list (not must-FAIL: the ruling makes V5 a screen). Re-verify B0-B11 FAIL and F0-F5 PASS; add a mutant per new CUE entry; re-pin REGEX_LIST_SHA256, the probe sha, and the blobs of induce_fitness.py, induce_run_2.py and the selftest.

The ruling's authority for this: F1b "The builder writes the final regexes ... the corpus is the acceptance test". The specialist's F2 finding is the precedent ("With only 3 attempts, that risks a spurious UNDETERMINED"). If the orchestrator prefers to route (vi) to the specialist, that is a light ruling. The payload, INDUCTION_SYSTEM and induction.py do not move.

M1 (MEDIUM, not blocking; backstop): V5 false negatives, 13 of 16. Cheap additions: the reward objects `brevity|fewer\s+words|less\s+text|to\s+the\s+point|unnecessary\s+detail|quicker\s+to\s+read`. A negated-(c) guard would reuse CUE inside REASONING_RX's clause. Otherwise, record these as KNOWN LIMITS for the post-run fitness reader.

L1 (LOW): the commit message says "19 mutants, all killed". The count is 18. The record should quote 18.

L2 (LOW): the induce_fitness docstring says "(b) FORM_PATTERNS (12)". There are 10 (the runner prints "10 form patterns").

L3 (LOW): the NEW sentence implies a reference is always shown, but the loader admits no-reference matches. This is the ruling's exact text: no change, noted only.

L4 (LOW): "Reply with a single JSON object and nothing else" in INDUCTION_SYSTEM is the phrase class INDUCE-1 echoed. Noted for the post-run reading.

L5 (LOW, record): after merge, `induce_run_selftest.py` (-1) exits rc=1 at 4dcfd3e: "the induction prompt constants are not the registered ones (system 67b62162...)". This is by design and disclosed in the induce_run_2 docstring. The registrar should bracket that the -1 instrument reproduces at 3cc505f only.
- `archv2_pilot/selftest.py` is also red (C0(c): induction.py expected blob:ae17ba25..., _base.py blob:f88fefa7...). That PRE-EXISTS on main: main's induction.py is f4d65f59 and _base.py is 6f25e4ce at 3cc505f / f9cd77c. It is owed by PILOT-K46's delta READY and is not this branch's defect.

L6 (LOW, EOL): in the worktree, induction.py and accepted_tests_ledger.py are the CRLF rendering and the four new files are LF. The pins name both renderings.

## Probe scripts
Scratch only, not committed: probe_cmp.py (verbatim + V5), adv_probe.py (U1-U16, G1-G14), neut_probe.py (24 neutrality paraphrases) and dry.py (the dry-run + body dump). All the texts they use are quoted above.
