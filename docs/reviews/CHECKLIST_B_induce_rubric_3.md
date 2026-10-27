<!-- PROVENANCE (the registrar's; 2026-09-25; zero calls). The text between the two VERBATIM markers below was WRITTEN BY THE
judge-design-specialist as READING B (blind) of the registered fitness checklist of ARCH-V2-INDUCE-RUBRIC-3, in the session
scratchpad file checklist_B_induce3.md, and COMMITTED BY THE REGISTRAR byte for byte: sha256 of those bytes
0c898ba5c8ff7ffd9ea548ab6045e3178bc2d77a1b54e6f77c9a4744a52532c3 (15,537 bytes, LF, no CR; verified by the registrar with
sha256sum before this commit; re-hash the bytes strictly between the marker lines, excluding the marker lines themselves).
Reading B was written blind to reading A (docs/reviews/POSTRUN_induce_rubric_3.md, 31420e9). Its render script and output
(render_i3.py sha256 70e584a5034f516e750193fcc942e46a8536995462c706b823779a03f56bf242; render_i3.out sha256
60895b7da1fb37f65f71d8831cad129a333de5ef09f569a9017505b5fb1dc747) stay in the scratchpad, NOT committed.
Recorded at docs/judge_v2_program.md, section "## ARCH-V2-INDUCE-RUBRIC-3 (2026-09-25, 2 invocations of <= 6; run b653b0a) ...".
Nothing below the first marker is the registrar's. -->
<!-- BEGIN VERBATIM READING B -->
# ARCH-V2-INDUCE-RUBRIC-3 — REGISTERED FITNESS READING, READER B (judge-design-specialist)

Blind to reader A (docs/reviews/POSTRUN_induce_rubric_3.md not opened). Zero calls; read-only. Attempt 1 NOT read before this verdict was written.
Procedure: docs/judge_v2_program.md L17102-L17117 ("THE REGISTERED FITNESS READING — CHECKLIST", INDUCE-3 registration L17008-L17187 as rendered at HEAD b653b0a).

## 1. Object and rendering (code, no EVAL text)

- Artefact: experiment_results/archv2/induce_rubric_3/rubric_mcq_ARCH-V2-INDUCE-RUBRIC-3.json, loaded by
  `induction.load_artefact(path, "9f0e4ce9f2991f5caf410ed09c77853c63e0c04a5a0f7bce3136989aef81e7a2")` -> PASS (no refusal);
  rubric_sha256 9e0a4022b58b30268e36617b46e13105354d22f2b17f6e83f3e3099ee18c04b1 (recomputed = recorded).
- System turn: `payload.build_system(rubric)` (V2_SYSTEM_TEMPLATE with FIXED_SYSTEM_PERSONA and the rubric + "\n\n" + SCHEMA_INSTRUCTION):
  2,918 chars, sha256 dafbc5ea036350540c8b882f981cbc45556097a2b5cd578fd45da087a4d0e501 (UTF-8).
- User turns: `rejudge_grok.build_user_prompt` on a SYNTHETIC stem ("SYNTHETIC: What is 2+3?", options [4,5,6]) with traces from
  `rejudge_grok.robust_trace`; reference block = question + "\n\n" + REFERENCE_MARKER + "\n" + `payload.render_mcq("B","5")`
  (= payload.build_query). Cases: (i) reference-bearing, A reasoned "B", B "C"; (ii) same, no reference; (iii) reference-bearing,
  B = empty output with pred "C" -> placeholder `The model selected option C: "6".` (and the no-pred placeholder
  `The model did not provide a prediction.`).
- Script and full output: scratchpad render_i3.py / render_i3.out (same folder as this file).

The rubric (verbatim; sentence labels mine):
R1 "The judge evaluates which response (Model A or Model B) better answers the MCQ."
R2 "First, determine the correct option letter by independently solving the question, using the reference solution (if provided) only as one possibly erroneous input among others."
R3 "Correctness of final answer is primary: prefer the response matching the judge's correct letter; TIE if both match or neither does."
R4 "If final answers differ in correctness, the correct one wins regardless of reasoning."
R5 "If both correct or both incorrect, compare reasoning quality only: prefer the one with fewer factual errors, logical gaps, or unsupported steps; TIE if reasoning error counts are equal."
R6 "Ignore length, formatting, or presence/absence of explanation."
R7 "Responses may end with a clear letter choice (possibly followed by option text), state no letter, or be truncated/empty (noted as selecting none or a letter)."
R8 "Call verdict 'A', 'B', or 'TIE'."

Template clauses cited: T-verify "check it against the reference and against your own reading of the question" / "A response whose final answer is wrong cannot win against a response whose final answer is right, whatever its reasoning looks like."; T-both "When BOTH final answers are right: Prefer the response with fewer errors or unsupported steps in its reasoning. If neither has any, output TIE. ... a short correct response ties a long correct response."; U-tie (user turn) "If both models are genuinely equivalent, output winner: \"TIE\" with confidence <= 0.5."; S-schema "Required shape: { ... \"winner\": <Model A, Model B, or TIE>, ... }" and the user turn's `"winner": "Model A, Model B, or TIE"`.

## 2. The walk

K1 (reference as criterion) — CLEAR. R3 keys correctness to "the judge's correct letter", and R2 builds that letter "by independently solving the question, using the reference solution (if provided) only as one possibly erroneous input among others". No clause defines right/wrong by agreement with the reference or makes it decisive. Meets T-verify ("against the reference and against your own reading"). Cases (i)/(iii): criterion = judge's letter; (ii): same, the reference clause is conditional.

K1b (converse: distrust / own-working override) — CLEAR, with a DISCLOSURE. Nothing says ignore or distrust the reference by default, or that own working overrides it whenever they disagree; the reference is "one ... input", used, and "possibly erroneous" mirrors the marker "may be wrong". DISCLOSURE: "independently solving" + "only as one possibly erroneous input among others" shades the T-verify balance (reference AND own reading) toward the judge's own solve. This is the registered S6 intent, not a K1b clause, but on the record the reference's value is its correctness as an answer (+12.6pp) and the non-reasoning judge's own solve is the weaker input (ORACLE); any down-weighting is a direction the record prices as a loss. Not measurable here; not UNFIT.

K2 (reasoning-presence reward on a correctness tie) — CLEAR. R5 compares "reasoning quality only" and defines it by the colon as "fewer factual errors, logical gaps, or unsupported steps"; R6 "Ignore ... presence/absence of explanation". No depth/thoroughness/fullness criterion; no penalty for a bare letter as such. Meets T-both.

K2b (absence reward / anti-reasoning / format demand) — CLEAR. No brevity reward. R4 "the correct one wins regardless of reasoning" is scoped to a correctness DIFFERENCE and restates T-verify's "whatever its reasoning looks like" (not the INDUCE-1/B29 class "ignore the steps entirely"). R6 is symmetric (presence/absence). R7 describes response forms; it demands nothing of the contestants.

K2c (placeholder walk, case iii) — CLEAR, with DISCLOSURES. Both-right: `The model selected option B: "5".` vs a clean derivation -> 0 vs 0 errors -> TIE (R5); vs a derivation with one slip -> placeholder wins. Both-wrong: `The model selected option C: "6".` (or `The model did not provide a prediction.`, which R3/R7 class with wrong: "neither does" / "noted as selecting none") vs a wrong derivation, which almost always carries >= 1 error -> the placeholder or the NO-ANSWER response tends to win. The mechanism is the template's own "fewer errors or unsupported steps" (T-both) applied as written; the rubric adds no automatic win/loss for a placeholder and R6 neutralises presence/absence. DISCLOSURES: (a) the inherited property (a bare letter contains no errors) in both-right; (b) R5 extends the rule to BOTH-INCORRECT, where the template is silent, so the both-wrong absence reward (my N5) is carried by the rubric's explicit extension, including a no-prediction response beating an attempted wrong answer; (c) "logical gaps, or unsupported steps" admits the opposite reading (a bare assertion is itself an unsupported step), so the direction is judge-dependent. Graded disclosure (MEDIUM), not a K2c FOUND under the registered wording ("beyond the template's ...").

K3 (TIE restricted/forbidden/narrower) — CLEAR. TIE is licensed in R3 and R5 ("TIE if reasoning error counts are equal"), which is broader than T-both's "If neither has any, output TIE"; nothing restricts TIE to identical, forbids or discourages it.

K3b (over-tie) — FOUND. R3: "Correctness of final answer is primary: prefer the response matching the judge's correct letter; TIE if both match or neither does." In the both-right case this clause directs TIE unconditionally, where T-both directs a preference ("Prefer the response with fewer errors or unsupported steps in its reasoning. If neither has any, output TIE."). It is the S8 echo with the qualifier dropped ("both right or both wrong WITH NEITHER HAVING FEWER ERRORS" -> "if both match or neither does"). R5 then directs the preference, so the rubric carries BOTH instructions for the same case; the lexicographic reading (R3's TIE = the primary criterion's tie, resolved by R5) is the likely one, but the token is the verdict token R8 names ("Call verdict ... 'TIE'"), no stage name separates it, and a judge that stops at R3 over-ties. Walked strictly, as instructed and as anticipated by N1: a clause directs TIE where the template directs a preference. FOUND = UNFIT. (Secondary to K8 below; my verdict does not rest on it alone.)

K4 (positional default / order dependence) — CLEAR. R1 names "Model A or Model B"; no default, no "otherwise", no order-dependent criterion. R8's 'A'/'B' are not positional defaults (see K8).

K5 (case ii, no reference) — CLEAR, with a DISCLOSURE. R2 "(if provided)" makes the reference optional and the correctness criterion (the judge's own letter) is defined without it; R5-R8 need no reference. DISCLOSURE (inherited, not rubric): V2_SYSTEM_TEMPLATE states "The question carries a reference solution" in case (ii), where it does not; the rubric's "(if provided)" is the only text that repairs it.

K6 (options the judge is not shown) — FOUND at LOW, disclosed. R2 "determine the correct option letter" and R3 "prefer the response matching the judge's correct letter" key correctness to a LETTER; the judge is shown the stem only (D5 MIXED ruling: no options list), and sees letters/option texts only through the "[This model's selected answer: (X) text]" injections and the reference "(B) 5". Workable through option TEXT. Sharpened hazard (MEDIUM-grade, disclosed): payload.py's docstring states the contestants' orderings may be "MIXED:a|b" when they differ, "allowed only without a reference", i.e. exactly case (ii); there the same letter can name different options for A and B, and a letter-keyed "matching" criterion can mislead. The template's option-free "final answer" wording does not carry this hazard.

K7 (template walk) —
 - persona "overall correctness and reasoning quality": CLEAR (R1, R3, R5).
 - bias suppression (length, formatting, identity, style): CLEAR (R6 restates).
 - evaluation order (critique A, critique B, compare, decide) and "Correctness first — verify before you compare ... Before critiquing": R2 "First, determine the correct option letter" sits in the template's pre-critique verify step: CLEAR.
 - verify-first (T-verify): CLEAR (K1, K1b).
 - "cannot win ... whatever its reasoning looks like": R4 restates: CLEAR.
 - both-right rule (T-both, "a short correct response ties a long correct response"): R5 + R6 restate; R3's unconditional both-match TIE CONTRADICTS "Prefer the response with fewer errors ..." at clause level: FOUND (the same defect as K3b; one defect, counted once in the verdict).
 - confidence lines (0.95-1.0 overwhelming; 0.7-0.85 default; TIE <= 0.5): rubric silent: CLEAR.
 - user turn "superior reasoning quality based solely on the logical rigour and domain soundness": R5 "compare reasoning quality only"; R4's correctness-first override is the system template's own (inherited tension): CLEAR.
 - JSON output shape: see K8.

K8 (output-format instruction vs SCHEMA_INSTRUCTION) — FOUND. R8 "Call verdict 'A', 'B', or 'TIE'." is an instruction on the verdict tokens that conflicts with S-schema ("winner": <Model A, Model B, or TIE>) and with the user turn ("winner": "Model A, Model B, or TIE"). Not a redundant echo: the tokens differ, and the conflict is consequential by execution — `rejudge_grok.parse_judge` (used by judge_v2/writer.py L100) returns INVALID for "A" and "B" (executed here: '{"winner": "A"}' -> ('INVALID', 0.8); 'B' -> INVALID; 'TIE' -> TIE; 'Model A' -> Model A). A judge that obeys the rubric over the schema on either order yields an INVALID match (combine_orders: any INVALID -> INVALID), and only the non-TIE verdicts are hit, so the damage would be asymmetric (TIEs survive, decisive verdicts are voided). FOUND = UNFIT. (Mitigation I do not credit under the registered rule: the schema comes last and says MUST, so compliance with the schema is likely; K8 is a text criterion, not a compliance forecast.)

## 3. Verdict

FOUND items reading UNFIT: K8 (conflicting verdict-token instruction; parse_judge maps 'A'/'B' to INVALID, executed), K3b (R3 directs TIE on both-right where the template directs a preference), and K7 (the same R3 clause contradicting the both-right rule; not a separate defect).
LOW/MEDIUM disclosed: K6 (letter-keyed correctness, judge not shown options; MIXED orderings in case ii); K2c disclosures (inherited no-errors property; rubric-extended both-wrong absence reward incl. no-prediction; ambiguous "unsupported steps" direction); K1b (shading toward own solve); K5 (template's false "carries a reference" in case ii).
CLEAR: K1, K1b, K2, K2b, K2c, K3, K4, K5.

VERDICT RULE applied: at least one item reads UNFIT in this reading -> READER B READS: **UNFIT**. Under the registered rule the artefact is NOT ADOPTED whatever reader A reads, and the $rubric slot takes the author's pre-decided FALLBACK (GENERIC_RUBRIC, sha256 67f843eb7a632ae5bd411a9debcbaf9dedccd362e0c8355c366c6d85cb89b1dc). P3 (FIT in both readings) is FAILED by this reading alone.

Neither finding is a V5 miss the registration promised to catch: jv2-v5-4 (f) polices TIE suppression, not over-tie, and no V5 leg polices output-format tokens; V5 is a lexical screen and "a V5 PASS is not evidence of fitness" (registration SCOPE).

RULE 1: every observation above is on the artefact's text and code, with a synthetic stem; no EVAL text or number was read or computed; nothing here is an input to any future induction.

What this does NOT show: that the judge would in fact emit 'A'/'B' or over-tie (no call was made; these are text findings under a registered text criterion); any effect of this rubric on verdicts, ties, accuracy or leakage; that GENERIC_RUBRIC is better (the closed line puts rubric text at 0 to +1.5pp of decisiveness); anything about reader A's reading.

---
[Appended after the verdict above was written: descriptive-only reading of attempt 1 — see the section below if present.]

## DESCRIPTIVE-ONLY (NOT OF RECORD): attempt 1, read AFTER the verdict above was written

Source: experiment_results/archv2/induce_rubric_3/attempts.db (opened mode=ro), attempt 1, reply sha256 a5d81ab5015fc83a1257fc2a17a3bfbdfeb9313d4e5003dde8040c606b486386, class FITNESS (outcome.txt L14-L15: V5 (d2) FAIL, "names 'reference' with no sceptic cue"). Attempt 2's reply text equals the artefact's rubric byte for byte as displayed.
Text: "The judge evaluates Model A vs Model B to determine which better answers the MCQ. Judge correctness of final answer (A/B/C/...) by own calculation, using reference solution (if provided) only as input, not authority. Prefer response with correct final answer; if tie, prefer one with fewer reasoning errors/unsupported steps. TIE if both correct or both wrong with equal reasoning quality. Ignore length, formatting, presence/absence of reasoning."
Walk (same method, not rendered separately): K1 CLEAR ("only as input, not authority"). K1b CLEAR but closer to the line than attempt 2 ("by own calculation ... not authority"). K2/K2b CLEAR. K2c same disclosures (both-wrong extension). K3 CLEAR. K3b CLEAR: TIE is conditioned ("with equal reasoning quality"), the preference comes first ("if tie, prefer one with fewer reasoning errors") — the qualifier attempt 2 dropped is present. K4 CLEAR. K5 CLEAR ("if provided"). K6 LOW ("(A/B/C/...)" letter-keyed). K7 CLEAR. K8 CLEAR (no verdict-token instruction).
Descriptive reading: attempt 1 would have read FIT in this walk; the screen rejected it because "not authority" is not in the (d2) sceptic-cue list, while the text the screen passed carries the two defects above (neither is a class V5 screens). This is one case, post hoc; it is consistent with the READY's held-out estimate (fit_neg FP 5/14, d2 among them) and shows nothing about the screen's rates. Not of record; it changes nothing: the first VALID reply is of record, no best-of-n, no re-roll.
<!-- END VERBATIM READING B -->
