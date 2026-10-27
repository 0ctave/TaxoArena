# READY review: ARCH-V2-INDUCE-RUBRIC-3 at 045834b

- Reviewer: adversarial-reviewer, 2026-09-25. Zero calls. Record data read-only.
- Build under review: commit 045834bb54e8f7306714267e9d89c068dc80d5e2 on branch worktree-agent-a3eaf03130c710c7b (worktree `.claude/worktrees/agent-a3eaf03130c710c7b`, clean: `git status --short | wc -l` = 0). Parent 39c81c0, the registration. NOT merged.
- Registration: docs/judge_v2_program.md L17008-L17110 (39c81c0).
- Held-out order witness: L17112-L17126 (5ff5e73).
- Build pins and open items: L17128-L17169 (971fd0b).
- Held-out set: frozen BEFORE I read any jv2-v5-4 regex or any builder file (order witness 5ff5e73 precedes the pin commit 971fd0b and this review).

## VERDICT: READY for --run, as registered, under conditions R1-R5

H1 below is a decision to take BEFORE the run, not after it. The build conforms to the registration. However, the screen jv2-v5-4 rejects a material share of natural fit rubrics that restate S6-S9 in negated form, which is exactly what the new prompt invites. Each such rejection burns one of three attempts. If all three are burned, the run ends UNDETERMINED and the slot takes GENERIC_RUBRIC. The registration accepts this risk ("no figure refuses the READY on its own"; P1 was lowered to 0.70 because "the new classes add FP surface that S6-S9 themselves invite"). So the risk does not refuse the READY. But it is larger than the P1 figure suggests, and the orchestrator should choose (A) or (B) of H1 knowingly.

### Conditions for --run
- R1. Merge 045834b into main by path, and run from the main checkout. The six paths are the pinned blobs; no other change. Reason: `induce_run_3.Paths` takes the outputs, the manifest and the exclusion list from ROOT (the checkout holding the script), but the day ledger from TAXOARENA_DATA_ROOT. Run from the worktree, the write-once outputs would land in the worktree.
- R2. Launch with `--run --go --expect-payload-sha e5ace2a5840fc6c15bd51fff10f6eefc0ee9b4dde9286147f7bdbeadcd19553a`.
- R3. The registrar inserts the stage-'judge' bracket (section 6) before the run.
- R4. The Q3 ruling below applies to the outcome: a transport-exhausted run takes the FALLBACK. The registrar records it at the outcome; the instrument is not changed.
- R5. Nothing else reads the SPLIT-2 views during the run (rule 7, W1-W5). The views are read-only files (`-r--r--r--`). No -wal or -journal file was present before or after my dry-run.

## Pins for the registrar

All values below were recomputed by me. The LF rendering is the rendering of record. None of the six blobs carries a CR (python count on `git cat-file blob` = 0 for each). The CRLF value is printed beside because the worktree differs for two files.

| object | kind | value | command |
|---|---|---|---|
| payload (EXPECTED_PAYLOAD_SHA) | sha256 of the body bytes | e5ace2a5840fc6c15bd51fff10f6eefc0ee9b4dde9286147f7bdbeadcd19553a (31,955 bytes) | my own dry-run `TAXOARENA_DATA_ROOT=Z:\...\TaxoArena python tools/analysis/judge_v2/induce_run_3.py --dry-run` (rc 0, 19 s). Confirmed a second way: `json.dumps(json.loads(body))` with default separators and ensure_ascii re-serialises to the same e5ace2a5; body keys = model / max_tokens / messages; model grok-4-1-fast-non-reasoning; max_tokens 8192; no temperature; roles system, user. |
| system turn | sha256 text | e95c59b22c3df56b79f2ed9a93f8b6912ca8aff15d78d849c79c9ba17c8896d7 (2,360 chars) | messages[0].content == the component file induction_system_jv2_induce_5.txt: True |
| user turn | sha256 text | a66db2209ac1b4efc360f08f9bdb0962fbf3a8000d1841d69f879d896b45f1d6 (29,310 chars, 40 examples) | = the -2 user turn (the same value in experiment_results/archv2/induce_rubric_2/induce_rubric_2_dryrun.txt) |
| selection | sorted / ordered | 99484486d75774b379bd35713063022a8c05b8949b7b2d61045f95670d9abe50 / 89bed2562c1f8575ed0dbfd5b9980216aa346ef26d5837fbe574b7b775ef132a | REPRODUCED (dry-run). Exclusion list 68c0b960... (679 excluded; 35 kept, 5 replaced) |
| INDUCTION_SYSTEM | sha256 | e95c59b22c3df56b79f2ed9a93f8b6912ca8aff15d78d849c79c9ba17c8896d7 | dry-run pin line |
| REGEX_LIST_SHA256_V54 | sha256 canonical JSON | 714268738c7593ab45d09daba2934e8780278c82a180f10a78685a283f4ef7d0 | `induce_fitness_3.regex_list_v54_sha256()` = the pin; embeds the jv2-v5-3 list 7b5af1d513df318031d77a14b7c8673051a075957ca97ffcc287cdfdc516fa54 |
| induction.py | blob / lf16 / crlf16 | blob:147e6874926b65393037cdcacd0e29aa308651ef / sha256-lf16:1117d74f06438d98 / sha256-crlf16:f5f8644ee6ae7944 | `git rev-parse 045834b:<path>`; `git hash-object` in the worktree = the blob |
| induce_fitness_3.py | blob / lf16 / crlf16 | blob:4550533c64cdbe592faed3373b4fb02291c7b418 / sha256-lf16:b60280a0889a1a73 / sha256-crlf16:0d214eaaf7677389 | same |
| induce_cache_3.py | blob / lf16 / crlf16 | blob:e6b34439d769b026f7db9bf6243125892cb44f17 / sha256-lf16:3b4d3566df559bb1 / sha256-crlf16:32660e4755faeabb | same |
| induce_run_3.py | blob / lf16 / crlf16 | blob:b13fca84a2b305f1d95288e0ec1ab6f9a6523610 / sha256-lf16:9aebe6ccd13c393e / sha256-crlf16:89ac469eec4ba805 | same |
| induce_run_3_selftest.py | blob / lf16 / crlf16 | blob:7a7b4cedf99477c1ee3f1287965e4957f5acef7f / sha256-lf16:f04e5614d3673ad0 / sha256-crlf16:a216b6cfb5c9703d | same |
| accepted_tests_ledger.py | blob / lf16 / crlf16 | blob:a4a1d7eedc0846ba601a8aba557166447f22d2e5 / sha256-lf16:b108bb76600151f1 / sha256-crlf16:3147e6cdeab6773a | same |
| C-V5-HELDOUT set | sha256 file bytes (LF; no CRLF rendering exists) | 6c33a71bca8998db8f1eee4d8c6690fd79b8ab27ba901df68f7a104449f86953 (19,649 bytes) | `sha256sum` re-hashed before scoring = the 5ff5e73 witness; committed with this review at experiment_results/archv2/induce_rubric_3_ready_heldout/induce3_heldout.json |
| -2 held-out set (regression) | sha256 file bytes | 4b44076086d53856ce6cba4651b9128cc068d69aae71c1f59e3075a845d94e29 | re-hashed by my scoring script |

Every value above equals the registrar's pin at L17128-L17169, and the payload equals the builder's "as built" value.

Views before and after my dry-run and my payload rebuild:
- gen_view_REG.db: sha256 c2930c609c67d6c7e1f8b8fbcd8f6f1970478a28f844d086d0b0db169d10c0ec; 849,633,280 bytes; mtime 2026-09-24 20:23:39.418231700 +0200.
- eval_view_REG.db: sha256 e35b7518878205837bfd16266dfdd8a6e76a226ed67957796d1d33cb72b5e369; 454,049,792 bytes; mtime 2026-09-24 20:23:51.222773400 +0200.
- Identical before and after: `stat` diff empty, `ls` diff empty, no sidecar files.
- The dry-run's eval_view open was at 2026-09-25T01:56:55.617962Z (the disclosure C5 is carried).
- The dry-run also printed: EVAL variant stems sharing an 8-token run with the user turn: 0 of 6,156.

## (1) C-V5-* conditions: all CONFIRMED independently

I did not rely on the selftest's printout. My own script imports only the pure screen modules from the worktree, loads the corpora by AST / JSON, and scores them with `induce_fitness_3.v5`.

| condition | result | my number | claimed |
|---|---|---|---|
| C-V5-neg | ef9c9e87 (loaded; sha recomputed ef9c9e87) FAILS on (a') AND (b) | FAIL: a' NO; b: 8 patterns; c NO | FAIL (a) and (b) |
| C-V5-neg-2 | ace41ede FAILS on (d) AND (f) | FAIL: d1 agree_with_reference; d2; f tie_identical, positional_otherwise | FAIL (d) and (f) |
| C-V5-pos | CONTROL_FIT_TEXT a7b8ebb0 PASSES | PASS | PASS |
| C-V5-probe | B1-B29 FAIL; F1-F43 PASS (F20-F43 on NEUTRALITY_FRAME) | 29/29 FAIL; 19 plain F + 24 framed F = 43/43 PASS | 0 FP / 0 FN |
| B29f | the full B29 text FAILS | FAIL (c) | FAIL |
| C-V5-probe-3 | 20 unfit3 + T7 FAIL; 13 fit3 PASS | 20/20 + T7 FAIL; 13/13 PASS | 0 FP / 0 FN |
| registered example phrases | every example the registration names for (d1), (d2), (e), (f) fires; the two named non-firing forms ("TIE only if" without "identical"; "otherwise TIE") do not fire | 34/34 fire; 4/4 pass | (not claimed; checked for C-7) |
| selftest | `python induce_run_3_selftest.py` and `python -O ...`: rc 0 each | 556 lines "] PASS " and 0 lines "] FAIL " in EACH transcript (grep -cE count, full file) | 556 checks |
| mutants | 45 new named parts / switches (11 cue_ref + 5 d1 + 14 sceptic + 3 e + 7 f + 5 switches), each changes the list sha and is killed | 45 "MUTANT KILLED" lines for jv2-v5-4 (89 in total, with the jv2-v5-3 suite); by my own rebuild, each of the 45 list shas differs from the pin | 45 killed |
| -2 instrument refuses | induce_run_2.py --dry-run on the build | refuses at the prompt pins, before any view opens: "[JUDGE-V2] induction.INDUCTION_VERSION jv2-induce-5 is not the registered jv2-induce-4" | refuses by design |
| Q2 (E4) | unfit3 under jv2-v5-3 | 19 PASS, E4 FAILS (c) | registrar 19/20 |

Mutant support, measured by me against REGISTERED corpora only (the 109 texts above):
- 18 of the 45 parts are killed by a registered text.
- The other 27 are killed only by the builder's batteries (D7).
- `off:a_prime` changes no verdict on any registered or held-out text (Q1).
- `off:d2` is killed by no registered text, but it moves 6 held-out verdicts: 4 unfit caught (HD1, HD3, HD5, HD7) and 2 fit rejected (HF01, HF10). d2 does real work on held-out data.

## (2) C-V5-HELDOUT (pre-registered report; descriptive; no threshold)

- Set: 55 texts, sha256 6c33a71b... (re-hashed = the witness).
- FP = a fit text that FAILS; FN = an unfit text that PASSES.
- Wilson 95% intervals.
- Script: scratchpad i3_heldout_rev/score.py. It asserts the file sha before scoring and imports induce_fitness_3 / induce_fitness from the worktree.

| screen | FP overall | FP fit_neg (S6-S9 negated paraphrases) | FP fit_plain | FN overall | FN (d) | FN (e) | FN (f) | FN c2 (optional) |
|---|---|---|---|---|---|---|---|---|
| jv2-v5-4 (71426873) | 9/28 = 32.1% [17.9, 50.7] | 5/14 = 35.7% [16.3, 61.2] | 4/14 = 28.6% [11.7, 54.6] | 7/27 = 25.9% [13.2, 44.7] | 1/8 = 12.5% [2.2, 47.1] | 1/8 = 12.5% [2.2, 47.1] | 5/8 = 62.5% [30.6, 86.3] | 0/3 [0, 56.1] |
| jv2-v5-3 (7b5af1d5), baseline | 4/28 = 14.3% [5.7, 31.5] | 0/14 = 0% [0, 21.5] | 4/14 = 28.6% [11.7, 54.6] | 18/27 = 66.7% [47.8, 81.4] | 7/8 = 87.5% [52.9, 97.8] | 4/8 = 50.0% [21.5, 78.5] | 7/8 = 87.5% [52.9, 97.8] | 0/3 [0, 56.1] |

Regression line: the frozen -2 held-out set 4b440760 (18 fit / 17 unfit).

| screen | FP | FN |
|---|---|---|
| jv2-v5-4 | 3/18 = 16.7% [5.8, 39.2] (H-F5 b:reward_form, H-F16 b:exclusivity, both inherited; H-F7 d2, NEW) | 12/17 = 70.6% [46.9, 86.7] (H-U16 now caught by e:presence_reward) |
| jv2-v5-3 | 2/18 = 11.1% [3.1, 32.8] | 13/17 = 76.5% [52.7, 90.4] |

The jv2-v5-3 line reproduces the -2 READY's figures (FP 2/18, FN 13/17) exactly: the scorer agrees with the record.

Reading of the figures:
- The four fit_plain FPs are INHERITED from jv2-v5-3's (a) and (c) legs, and the same four under both screens (HF21, HF28: no word "reasoning"; HF24, HF27: correctness named as "answers correctly" / "right or wrong"). A reply echoing the prompt's "correctness of the final answer ... soundness of the supporting reasoning" avoids them.
- The FP increment of jv2-v5-4 over jv2-v5-3 is 5/28, ALL in fit_neg (0/14 -> 5/14). This is the disclaimer-style failure the registration anticipated:
  - HF01, HF10: d2 fires. The sceptic phrasing is "something to check, not something to copy" and "agreement with the reference by itself". Neither is a cue. Unlikely in a real reply, which will echo "may be wrong" from S2/S6.
  - HF05: e:presence_reward on "Having reasoning at all is not a point in a response's favour".
  - HF06: d1:agree_with_reference on "It is not correct by virtue of matching the reference solution".
  - HF08: d1 on "an answer that differs from the reference can still be the correct one", plus d2.
- FN: (d) and (e) improve strongly (7/8 -> 1/8 and 4/8 -> 1/8).
  - (f) stays weak at 5/8. The escapes: "only when ... word-for-word the same"; "award it to Model A"; "the second response is the winner"; "reserved for ... essentially indistinguishable"; "lean toward the response presented first".
  - FN is backstopped by the checklist (K3 / K4). The residual (d) FN (HD4, "could contain mistakes, but it is the only answer key ... picks the reference's option") passes via the builder's sceptic cue may_contain_errors plus a d1 verb gap ("picks the reference's option").

Per-text firing pattern (jv2-v5-4, then the jv2-v5-3 baseline):

| key | label | subclass | jv2-v5-4 | v5-4 firing | jv2-v5-3 | v5-3 firing |
|---|---|---|---|---|---|---|
| HF01 | must PASS | fit_neg | FAIL **FP** | d2 | PASS | - |
| HF02 | must PASS | fit_neg | PASS | - | PASS | - |
| HF03 | must PASS | fit_neg | PASS | - | PASS | - |
| HF04 | must PASS | fit_neg | PASS | - | PASS | - |
| HF05 | must PASS | fit_neg | FAIL **FP** | e:presence_reward | PASS | - |
| HF06 | must PASS | fit_neg | FAIL **FP** | d1:agree_with_reference | PASS | - |
| HF07 | must PASS | fit_neg | PASS | - | PASS | - |
| HF08 | must PASS | fit_neg | FAIL **FP** | d1:agree_with_reference, d2 | PASS | - |
| HF09 | must PASS | fit_neg | PASS | - | PASS | - |
| HF10 | must PASS | fit_neg | FAIL **FP** | d2 | PASS | - |
| HF11 | must PASS | fit_neg | PASS | - | PASS | - |
| HF12 | must PASS | fit_neg | PASS | - | PASS | - |
| HF13 | must PASS | fit_neg | PASS | - | PASS | - |
| HF14 | must PASS | fit_neg | PASS | - | PASS | - |
| HF15 | must PASS | fit_plain | PASS | - | PASS | - |
| HF16 | must PASS | fit_plain | PASS | - | PASS | - |
| HF17 | must PASS | fit_plain | PASS | - | PASS | - |
| HF18 | must PASS | fit_plain | PASS | - | PASS | - |
| HF19 | must PASS | fit_plain | PASS | - | PASS | - |
| HF20 | must PASS | fit_plain | PASS | - | PASS | - |
| HF21 | must PASS | fit_plain | FAIL **FP** | c | FAIL **FP** | c |
| HF22 | must PASS | fit_plain | PASS | - | PASS | - |
| HF23 | must PASS | fit_plain | PASS | - | PASS | - |
| HF24 | must PASS | fit_plain | FAIL **FP** | a' | FAIL **FP** | a |
| HF25 | must PASS | fit_plain | PASS | - | PASS | - |
| HF26 | must PASS | fit_plain | PASS | - | PASS | - |
| HF27 | must PASS | fit_plain | FAIL **FP** | a' | FAIL **FP** | a |
| HF28 | must PASS | fit_plain | FAIL **FP** | c | FAIL **FP** | c |
| HD1 | must FAIL | d | FAIL | d2 | PASS **FN** | - |
| HD2 | must FAIL | d | FAIL | c, d1:treat_reference_as, d2 | FAIL | c |
| HD3 | must FAIL | d | FAIL | d2 | PASS **FN** | - |
| HD4 | must FAIL | d | PASS **FN** | - | PASS **FN** | - |
| HD5 | must FAIL | d | FAIL | d2 | PASS **FN** | - |
| HD6 | must FAIL | d | FAIL | d1:defer_to_reference | PASS **FN** | - |
| HD7 | must FAIL | d | FAIL | d2 | PASS **FN** | - |
| HD8 | must FAIL | d | FAIL | a', d1:agree_with_reference, d2 | PASS **FN** | - |
| HE1 | must FAIL | e | FAIL | e:presence_reward | PASS **FN** | - |
| HE2 | must FAIL | e | FAIL | e:presence_reward | PASS **FN** | - |
| HE3 | must FAIL | e | FAIL | c, e:absence_penalty | FAIL | c |
| HE4 | must FAIL | e | FAIL | c | FAIL | c |
| HE5 | must FAIL | e | FAIL | c | FAIL | c |
| HE6 | must FAIL | e | FAIL | c | FAIL | c |
| HE7 | must FAIL | e | FAIL | e:absence_penalty | PASS **FN** | - |
| HE8 | must FAIL | e | PASS **FN** | - | PASS **FN** | - |
| HT1 | must FAIL | f | PASS **FN** | - | PASS **FN** | - |
| HT2 | must FAIL | f | FAIL | f:never_tie, f:always_winner | PASS **FN** | - |
| HT3 | must FAIL | f | PASS **FN** | - | PASS **FN** | - |
| HT4 | must FAIL | f | PASS **FN** | - | PASS **FN** | - |
| HT5 | must FAIL | f | FAIL | c, f:tie_discouraged | FAIL | c |
| HT6 | must FAIL | f | FAIL | f:positional_by_default | PASS **FN** | - |
| HT7 | must FAIL | f | PASS **FN** | - | PASS **FN** | - |
| HT8 | must FAIL | f | PASS **FN** | - | PASS **FN** | - |
| HC1 | must FAIL | c2 | FAIL | b:penalise_form, b:reward_form, c, e:depth_reward | FAIL | b:penalise_form, b:reward_form, c |
| HC2 | must FAIL | c2 | FAIL | c | FAIL | c |
| HC3 | must FAIL | c2 | FAIL | b:format_demand, c | FAIL | b:format_demand, c |

## (3) Rulings on D1-D7 (each by name)

| item | ruling | evidence |
|---|---|---|
| D1 six extra reference cues | ACCEPTED as a disclosed deviation. The docstring's "THREE" is wrong; the code of record carries SIX (not_correct_because, not_proof_of, neg_define_as, neither_nor, neg_mark_down, no_credit). This review is the correction of record. The blob is NOT to be edited before the run (a docstring edit moves the pins); correct it by a docstring bracket at the next registered touch. | Only not_correct_because is needed by a registered text (fit3 P0, P1). The other five are killed only by builder batteries. They widen the (d1)/(e) guard, so they open FN holes when a negated clause shares a clause with the unfit one. Probes (post-hoc, mine): "An unexplained answer gets no bonus and loses to an explained one" PASSES (no_credit); "Do not consider formatting as relevant, and a final answer matching the reference letter is correct" PASSES (neg_define_as); "Agreement with the reference is not proof of anything else, and an answer matching the reference letter wins" PASSES (not_proof_of). The registered not_penalised_for has the same clause-scope weakness ("A response is not penalised for length, and one lacking reasoning loses a correctness tie" PASSES). FN is backstopped by the checklist: MEDIUM, disclosed. |
| D2 not_penalised_for widened | ACCEPTED. | The registered form is subsumed by jv2-v5-3's own entry (so its mutant could not be killed); "marked down" is required by fit3 P12 (mutant killed by P12). |
| D3 four extra sceptic cues | ACCEPTED as a disclosed deviation. The docstring's "ONE" is wrong; the code carries FOUR (fallible, may_contain_errors, not_always_right, caution). The docstring is corrected as for D1. | fallible is needed by F7 (registered). may_contain_errors is semantically the registered may_be_wrong ("could contain mistakes" ~ "could be wrong") and is what lets held-out HD4 through; the registered cue has the same weakness. caution also admits "critically": weak, LOW. |
| D4 (f) local adjacency | ACCEPTED. | "Unguarded" in the registration means no CUE mechanism; the adjacency negations only narrow the patterns. None of the five held-out (f) FNs is caused by adjacency (all are pattern gaps). But see H1: the adjacency list omits "never" ("Never default to Model A or Model B" FIRES positional_by_default). |
| D5 unknown-version branch | ACCEPTED (stricter than registered, fail-closed). | induction.py L372-L383. The selftest executes both branches under jv2-induce-5 and the unknown-version branch. |
| D6 outcome names the FALLBACK | ACCEPTED, read with the Q3 ruling. | FALLBACK constant L246-L249 names GENERIC_RUBRIC 67f843eb...; the selftest checks the sha by AST against rubric_value_contrast.py. |
| D7 builder batteries | ACCEPTED: they may stay in the selftest. No registered acceptance leg rests on them: I re-executed every registered corpus (109 texts) without them, all correct. They carry the kill of 27 of the 45 mutants. The registration requires "at least one mutant per new named part" and does not say by which corpus, so it is met. | Battery sha 8382892021bd690e is NOT a registered corpus and not a substitute for one. |

## (4) Rulings on Q1-Q4

- **Q1: (a') is redundant. CONFIRMED, KEPT.** A clause in which (a') drops a correctness match carries a live (d1) match, so (d) and V5 already fail. (a') changes the per-leg report only. `off:a_prime` moves 0 registered and 0 held-out verdicts. It stays as registered (M3's intent: the report names correctness outside a reference-agreement clause); it is disclosed as verdict-inert.
- **Q2: CONFIRMED.** E4 fails jv2-v5-3 on (c); 19 of 20 unfit3 pass jv2-v5-3. The bracket at L17099 is correct. No registered condition moves.
- **Q3: "ends UNDETERMINED" COVERS UNDETERMINED BY INSTRUMENT. The fallback applies; no author question is needed.**
  - The author's question was "If INDUCE-3 is also UNFIT (or ends UNDETERMINED), what should fill the rubric slot?". It does not qualify UNDETERMINED by cause. A transport-exhausted run ends with no artefact and the label UNDETERMINED (BY INSTRUMENT).
  - The registration's own reading of the decision is "in EVERY non-adoption route ... with no further author question and never a fourth attempt or re-roll" (L16999, L17072).
  - The instrument already makes that run terminal: outcome.txt is written, and a relaunch is REFUSED because outputs are write-once (selftest F: "a 4th launch after UNDETERMINED BY INSTRUMENT -> REFUSED").
  - So the outcome line "a further relaunch needs a registrar bracket" is superseded by this ruling. The slot takes GENERIC_RUBRIC (67f843eb...), and the registrar records it at the outcome. The falsifier stays NOT FIRED (it is about three formal failures). The line is not changed before the run (MEDIUM, M2).
  - If the orchestrator reads the author's intent otherwise (a transport outage is not a verdict on the induction), that is a question for the author BEFORE the run, never after.
- **Q4: (d2) whole-text. ACCEPTED.** The registration reads "a rubric naming 'reference' must carry at least one scepticism cue": rubric-level, not clause-level. The weakness: an unrelated "verify" anywhere satisfies it (HD6 carries "Verify" and is caught by d1 only). Disclosed, LOW.

## (5) Fitness of the PROMPT (system + user turn read in full)

- The system turn is the component file (2,360 chars). The user turn is 29,310 characters: the unchanged -2 template header, then 40 examples with pipe-joined unlettered options. It carries no rubric-relevant word ("reference" occurs once, inside one example's option text; "TIE", "Model A/B", "rubric", "judge": 0).
- Would a competent non-reasoning model write a rubric that reads CLEAR on K1-K8? LIKELY, consistent with P3 0.55:
  - S6 closes K1: "one input ... never the yardstick" plus the explicit "must not define a correct final answer as one that matches".
  - S7 closes K2.
  - S8's "must not reserve / forbid / discourage / default" closes K3 and K4's positional default.
  - S2b gives K5 its no-reference case.
  - Nothing in the prompt speaks of the judge's output format beyond "at most 12 lines" (K8 low).
- Sentences that invite an echo failure:
  - **S8 (K3b over-tie): the main substantive risk.** "TIE is the correct verdict when both final answers are right, or both are wrong, and neither response's reasoning has fewer errors or unsupported steps than the other's" parses two ways:
    - ((both right) or (both wrong)) and (neither has fewer errors), which is the intended reading;
    - (both right) or (both wrong and neither has fewer errors).
    A 12-line compression "TIE when both final answers are right or both are wrong" drops the conjunct and reads K3b FOUND. MEDIUM.
  - **S6 (K1b): low.** "never as the yardstick" can be compressed to "do not rely on the reference" / "ignore the reference". S6's "uses the reference ... as one input" counters it.
  - **S7 (K2c): disclosure-level.** "reasoning is compared only by the errors or unsupported steps it contains" invites "a bare letter has no errors, so it beats a wrong-with-errors response". That is the inherited template property (a DISCLOSURE under K2c), unless the rubric says the bare response wins "automatically".
  - **S6-S9 (V5, not K): the burn risk of H1.**

## (6) Stage 'judge' bracket (C3 of -1 / -2, renewed for THIS run)

data_v2/views.py `_open` (L48-L65 at 045834b): the stage only selects which view kind is admitted. The open is `ro.open_ro(require_sealed=True, expect_sha256=<manifest sha>)`: read-only, sealed, sha-pinned. The runner's order discipline is unchanged from -2:
- reply committed before eval_view is opened (selftest A: witnessed);
- the in-process flag refuses call_judge_full after the open (selftest: REFUSED);
- a V2 failure is NOT OF RECORD and never re-posted (selftest D).
VIEWS-AUDIT-STAGE is not merged. ACCEPTABLE for this run under the same conditions. The bracket to insert:

`[ACCEPTED 2026-09-25 by READY_induce_rubric_3: ARCH-V2-INDUCE-RUBRIC-3's V2 leak check (and its dry-run) opens eval_view through data_v2.views.open_eval("judge") (VIEWS-AUDIT-STAGE not merged); the stage is a label only (views._open L48-L65: read-only, sealed, expect_sha256 e35b7518...); accepted for THIS run only, under the INDUCE-RUBRIC-1 / -2 conditions: the order witness (reply committed < eval_view opened), the no-call-after-open flag, V2 failure NOT OF RECORD and never a re-post; the reviewer's dry-run opened it once at 2026-09-25T01:56:55.617962Z (disclosure C5).]`

## (7) Walks

- **Write-ahead journal.** `_write_ahead` commits a PENDING invocation row BEFORE every post. The inherited -1 DDL triggers refuse:
  - an invocation after the first valid reply;
  - a 4th attempt;
  - a 4th transport error;
  - an invocation with an unresolved orphan.
  Orphans become transport errors on relaunch. Executed by the selftest: write-ahead 1 row = 1 post = ledger 1; a KeyboardInterrupt during the post is ledgered; 3 crashing launches followed by a 4th posts nothing; the store refuses the 4th invocation before the post. The cache is created with journal_mode DELETE and refuses an existing path, -wal or -journal.
- **Ceiling 6.** `CEILINGS["ARCH-V2-INDUCE-RUBRIC-3"] = 6` (accepted_tests_ledger.py). The ledger-equality refusal (day ledgers = cache invocations) and `atl.guard` run before any post. The selftest's refusal at 4 + 3 planned = 7 > 6 was executed.
- **Write-once output directory.** OUT_REL = experiment_results/archv2/induce_rubric_3/ does not exist (`ls experiment_results/archv2 | grep -c "^induce_rubric_3$"` = 0 in main and in the worktree). ids / outcome / artefact / transport_stop files are opened with mode "x"; `_launch_state` refuses any output present without a cache, and any outcome or artefact present. Not git-ignored (`git check-ignore`: attempts.db is re-included by `.gitignore:145 !experiment_results/**/*.db`; outcome.txt is not ignored).
- **Outcome lines.**
  - CHECKLIST names K1-K8 with the three cases and the VERDICT RULE.
  - FALLBACK names GENERIC_RUBRIC 67f843eb... and the three registered routes. It does NOT list BY INSTRUMENT; read it with the Q3 ruling.
  - P1 0.70, P2 0.85, P3 0.55 (NOT SCORED by the instrument); V5 SCOPE; disclosures 1-5 plus the four carried disclosures and the stage line.
  - All of these are printed in selftest branches A, C, V5-B, D and F.

## Findings

- **H1 (HIGH). The screen rejects natural negated restatements of S6-S9, and each rejection burns an attempt. This is a decision for before the run.**
  - Held-out: fit_neg FP 5/14 under jv2-v5-4 vs 0/14 under jv2-v5-3.
  - My own POST-HOC probes (written AFTER reading the regexes, so adversarially biased and NOT held-out) show the same class on direct echoes of the prompt's own sentences:
    - "Never default to Model A or Model B" FIRES f:positional_by_default (the adjacency guard knows "not" / "n't", not "never").
    - "A response is not favoured merely for giving more reasoning, nor penalised merely for giving none" FIRES e:presence_reward and e:depth_reward (the cue needs "not merely" adjacent).
    - "No preference or penalty merely for giving no reasoning or more reasoning" FIRES e:depth_reward.
    - "A correct final answer is not one that merely matches the reference" and "An answer that disagrees with the reference is not wrong for that reason" FIRE d1:agree_with_reference.
    - Of 12 S7 paraphrases, 5 FAIL.
    - Of 3 simulated full replies in the -2 reply's style, 2 FAIL.
  - The per-attempt V5 FP rate on echo-style replies is therefore plausibly 0.2-0.4, not the ~0.1 implied by P1 0.70. Attempts are correlated (same body).
  - The build conforms to the registration (the registered cue forms are adjacency forms), so this is a design risk the registration accepted, not a build defect, and the READY is not refused.
  - Options for the orchestrator:
    - (A) Run as registered. A burn lands on the pre-decided GENERIC_RUBRIC, never on an unfit artefact.
    - (B) Before any call, register a narrow amendment. Add "never" to the (f) negation lookbehinds. Allow "not <participle> merely" and "nor <participle> merely" / "no preference or penalty" in the (e) cue. Allow "not wrong / can still be correct ... differs from the reference" in the (d1) cue. This costs a new list sha, re-pins and a delta READY. The held-out set is then SPENT: any re-score is in-sample and must be labelled so.
  - The reviewer's reading: (B) is cheap (zero calls) and protects the author's chosen route; (A) is what was registered. Not my call.
- **M1 (MEDIUM). Builder cues widen the guard and open clause-scope FN holes (D1, D3).** Backstopped by the checklist. Disclose in the outcome's V5 SCOPE reading.
- **M2 (MEDIUM). The outcome wording for BY INSTRUMENT says "a further relaunch needs a registrar bracket" and does not print the FALLBACK.** Superseded by the Q3 ruling. The registrar records the FALLBACK at the outcome. No code change before the run.
- **M3 (MEDIUM). S8 is ambiguous and invites the K3b over-tie echo** (section 5). For the post-run readers: walk K3b on the both-right case explicitly.
- **M4 (MEDIUM). Run location (R1).** Outputs follow the script's ROOT while the ledger follows TAXOARENA_DATA_ROOT. Run from main after the merge.
- **L1 (LOW).** The docstring understates D1 (three vs six) and D3 (one vs four). This review is the correction of record; fix the docstring by bracket at the next registered touch.
- **L2 (LOW).** (d2) is whole-text (Q4): any unrelated "verify" or "critically" satisfies it.
- **L3 (LOW).** (f) FN 5/8 on held-out; the checklist K3 / K4 backstops it.

## Commands (all read-only on record data; zero calls)

- `sha256sum <scratchpad>/induce3_heldout.json` -> 6c33a71b... (before scoring).
- The held-out scorer `scratchpad/i3_heldout_rev/score.py` (asserts the sha; imports induce_fitness_3 and induce_fitness from the worktree).
- The mutant-vs-registered-corpus script -> `scratchpad/i3_heldout_rev/mutants.txt`.
- `python tools/analysis/judge_v2/induce_run_3_selftest.py` and `python -O ...` (worktree) -> `st.txt` / `stO.txt`: 556 PASS, 0 FAIL each; 36.9 s.
- `TAXOARENA_DATA_ROOT='Z:\FAC\TUBerlin\THESIS\TaxoArena' python tools/analysis/judge_v2/induce_run_3.py --dry-run` (worktree) -> `dry.txt`; `stat` / `ls` / `sha256sum` of the views before and after.
- `git rev-parse 045834b:<path>`, `git cat-file blob ... | sha256sum` (LF), the same with LF -> CRLF (crlf16); `git hash-object` in the worktree.
- `git check-ignore -v` on the output and held-out paths.
