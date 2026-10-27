"""The selftest of judge_v2.induce_run_3 (ARCH-V2-INDUCE-RUBRIC-3, registered 39c81c0, docs/judge_v2_program.md
L17008-L17110): a copy of induce_run_2_selftest.py (the -2 selftest, left byte-identical, blob 658e6a26...), adapted to the
-3 runner, plus the REGISTERED CONDITIONS ON V5 FOR THE READY (jv2-v5-4, judge_v2.induce_fitness_3). SYNTHETIC ONLY: the E-J
fixture (judge_v2.selftest.build_views: tiny source DBs written as NEW files under tempfile.gettempdir(), ingested, split
and viewed by data_v2), a STUB poster with call_judge_full's shape, a temporary ledger directory. No DB of record is opened;
no call is posted. The files of record READ (never written): the committed INDUCE-RUBRIC-1 artefact (C-V5-neg) and
INDUCE-RUBRIC-2 artefact (C-V5-neg-2), each through induction.load_artefact with its pinned artefact_sha256; the three
registration components under experiment_results/archv2/induce_rubric_3_registration/ (the INDUCTION_SYSTEM text, unfit3.json,
fit3.json), each checked by its git blob (LF) and its sha256 (LF and CRLF renderings); rubric_value_contrast.py, parsed by AST
(not imported) for the fallback's GENERIC_RUBRIC sha256. Scratch attempt caches are read with sqlite3 mode=ro URIs.

    python tools/analysis/judge_v2/induce_run_3_selftest.py [--transcript PATH]
    python -O tools/analysis/judge_v2/induce_run_3_selftest.py [--transcript PATH]

Every check is an explicit comparison printed PASS / FAIL (no assert: the -O run executes the same branches). Every
registered print branch is executed: P1 HELD / FAILED / NOT SCORED, P2 HELD / FAILED / NOT SCORED, P3 NOT SCORED (both
wordings), the CHECKLIST and FALLBACK lines, the falsifier FIRED / NOT FIRED, UNDETERMINED, STOPPED, V1-V5 PASS / FAIL / NOT
RUN, ARTEFACT OF RECORD YES / NO, the FITNESS formal failure with its matching pattern(s), the V2-failure fallback line; the
MCQ guard's both branches under jv2-induce-5 (and the fail-closed unknown-version branch).
V5 jv2-v5-4, the registered conditions: C-V5-neg (ef9c9e87 FAILS on (a') and (b)); C-V5-neg-2 (ace41ede FAILS on (d) AND
(f)); C-V5-pos (CONTROL_FIT_TEXT PASSES); C-V5-probe (B1-B11 FAIL / F1-F5 PASS, 329cd697...; B12-B29 FAIL / F6-F43 PASS,
30fecaff...; B29f, the full B29 text, FAILS); C-V5-probe-3 (the 20 unfit3 texts and T7 FAIL, the 13 fit3 texts PASS);
the builder's batteries (one text per new named part, so each part is observable); MUTANTS: every new named part removed
or switched off in turn, each KILLED (at least one jv2-v5-4 suite check fails under it) with a list sha differing from the
pin. The -2 selftest's jv2-v5-3 suite and mutants are executed here too (the imported screen is part of this one). The
C-V5-HELDOUT set is NOT here: the READY reviewer writes it blind to this code.
The fixture runs under a DEV seed with no registration (the registered selection runs ONCE, on the real views).
"""
import hashlib
import json
import os
import sqlite3
import sys
import tempfile

if __name__ == "__main__" and not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    __package__ = "judge_v2"
    import judge_v2  # noqa: F401

import ast  # noqa: E402
import re  # noqa: E402
from ._base import ROOT, dv2ro, dv2views, git_blob_lf, rr, sha256_text  # noqa: E402
from . import induce_cache as IC1  # noqa: E402
from . import induce_cache_2 as IC2  # noqa: E402
from . import induce_cache_3 as IC  # noqa: E402
from . import induce_fitness as F  # noqa: E402
from . import induce_fitness_3 as G  # noqa: E402
from . import induce_overlap_audit as OA  # noqa: E402
from . import induce_run_3 as R  # noqa: E402
from . import induction as I  # noqa: E402
from . import selftest as T  # noqa: E402
import accepted_tests_ledger as atl  # noqa: E402

DEV_SEED = "DEV-induce-run-3-selftest"
# the INDUCE-RUBRIC-1 artefact of record (committed), for C-V5-neg
R1_ARTEFACT_REL = "experiment_results/archv2/induce_rubric_1/rubric_mcq_ARCH-V2-INDUCE-RUBRIC-1.json"
R1_ARTEFACT_SHA = "2177d046d96aeacd925f5e76551bd863cfe55f425c69276cf4ced05d473ebdb0"
R1_RUBRIC_SHA = "ef9c9e8759147960dedff70c3b86fe9f6b8b9caad8ddc39fb0fdc1c253e0eb07"


def _ro(path):
    """A scratch attempt cache under tempfile.gettempdir(), opened read-only by URI (never a DB of record)."""
    return sqlite3.connect("file:%s?mode=ro" % os.path.abspath(path).replace("\\", "/"), uri=True)


# ── V5: the batteries and the mutants ───────────────────────────────────────────────────────

DISCLAIMERS = (
    "Do not reward formatting.",
    "Do not penalise extra text around the final answer.",
    "Ignore letter case: a lowercase letter counts.",
    "Extra text is neither rewarded nor penalised.",
    "Regardless of length or formatting, the correct final answer wins.",
    "Prefer sounder reasoning, not the longer response.",
    "No penalty for lowercase letters or extra text.",
    "The judge must not reward or penalise length, formatting, or the presence or absence of an explanation.",
    # F1b change 3 (CUE additions): each of the three new cues is needed by exactly one text here or in F2
    "Shorter responses are not preferred.",
    "Extra text neither helps nor hurts.",
    "Do not favour brief responses.",
    # kills the mutant "CUE entry not_rewarded_penalised removed" (no other text needs that entry alone)
    "Extra text is not penalised.")
FIT_PHRASINGS = (
    "A response that does not commit to a single letter has no final answer.",
    "Only the letter the response commits to as its final answer is compared with the correct option.",
    "A response that commits to exactly one letter has a final answer.",
    "A response that commits to exactly one option letter has a final answer.",
    "Score 0 if the final answer is wrong, regardless of length.")
# [F1b: "Penalise unsupported claims in the explanation." was a fit phrasing at a02a9c1; F1b change 4 adds the bare object
# "explanation(s)" to the penalty family, so it now trips penalise_form (a disclosed consequence of the ruling's list).]
TRIGGERS = {
    "no_other_text": "The answer must have no other text.",
    "extra_text": "Watch for extra text.",
    "exact_single_letter": "Output exactly one uppercase letter.",
    "only_the_letter": "Give only the letter.",
    "a_to_z": "Answer with a letter (A-Z).",
    "lowercase": "Lowercase answers are wrong.",
    "no_credit_reasoning": "No credit for reasoning.",
    "penalise_form": "Penalise verbosity.",
    "reward_form": "Prefer the more detailed response.",
    "exclusivity": "Answer with the letter and nothing else.",
    "ideal_bare_letter": "The ideal response is a bare letter.",
    "format_demand": "Output JSON only."}
NO_CORRECTNESS = "1. Compare the two responses.\n2. Prefer the sounder one; otherwise TIE."
NO_REASONING = "1. The response whose final answer is correct wins.\n2. Otherwise TIE."

# C-V5-probe (F1b change 6): the specialist's probe corpus, VERBATIM from the ruling (programme L16350-L16475; each text
# checked to occur exactly once there as '- <id> "<text>"' with newlines written \n). B1-B11 must FAIL V5; F1-F5 must
# PASS. B0 = the INDUCE-RUBRIC-1 rubric (C-V5-neg); F0 = CONTROL_FIT_TEXT (C-V5-pos). Any miss refuses the READY.
PROBE_UNFIT = {
    "B1": "The final answer must be a single letter matching an option. Score 1 if the response is one letter and nothing"
          " else. Score 0 for a wrong letter, several letters, or any added commentary.",
    "B2": "Score 1 if the final answer is correct and the response consists solely of the option letter. Any reasoning,"
          " commentary or working lowers the score to 0.",
    "B3": "1. Check the final answer against the correct option.\n2. Penalize any response that includes reasoning or an"
          " explanation.",
    "B4": "1. The correct answer wins.\n2. When both are correct, prefer the response that states just its answer letter"
          " without elaboration.",
    "B5": "1. Final answer correctness first.\n2. Among correct responses, the more concise response wins.",
    "B6": "Score 1 if the final answer is exactly one letter (A-J) with no additional text; otherwise 0.",
    "B7": "1. Correct final answer first.\n2. If tied, the shorter response wins.",
    "B8": "Correct final answer wins; do not penalize length, but penalize extra text.",
    "B9": "Score 1 only if the final answer is correct AND the response follows the required answer format (a bare"
          " letter). Responses with explanations violate the format and score 0.",
    "B10": "Score 1 if the response is a capital letter only and the final answer is correct.",
    "B11": "The ideal response outputs one option letter as its final answer. Score 0 (incorrect) if: wrong or missing"
           " letter, multiple letters, or explanations.",
}
PROBE_FIT = {
    "F1": "1. Extract each response's final answer.\n2. The response with the correct final answer wins; the reference may"
          " be wrong, so verify it.\n3. If both are correct or both wrong, prefer the one with fewer reasoning errors or"
          " unsupported steps; else TIE.\n4. Length, formatting and explanations neither help nor hurt.",
    "F2": "A correct final answer beats a wrong or missing one. When final answers tie, penalize reasoning errors. Do not"
          " prefer shorter or longer responses.",
    "F3": "Judge the final answer first: does the chosen option letter match the correct option? Then assess whether the"
          " reasoning is valid. A bare correct letter ties a correct worked answer.",
    "F4": "1. A response that is empty, truncated or states no letter has no final answer and loses to any correct final"
          " answer.\n2. Compare final answers with the correct option; verify the reference.\n3. If both final answers are"
          " correct, the response with sounder reasoning wins; if equally sound, TIE.",
    "F5": "Each response commits to a single letter as its final answer; only the letter it commits to is compared with the"
          " correct option. Then weigh the soundness of the reasoning.",
}
PROBE_SHA256 = "329cd697fd457924b5437e754bbb2c2c6d935cb40a10b65f370da7a5d4740490"    # sha256 of the canonical JSON {"unfit": PROBE_UNFIT, "fit": PROBE_FIT}


def probe_sha():
    return sha256_text(json.dumps({"unfit": PROBE_UNFIT, "fit": PROBE_FIT}, sort_keys=True, ensure_ascii=True))


# READY probe corpus (docs/reviews/READY_induce_rubric_2.md, d3e9716; the reviewer's scratch scripts adv_probe.py
# sha256 a07e6fb5448a0b9f482e5ee3e130b7d26d5568b04569905c14883b0d997de3e2 and neut_probe.py sha256
# d7faf9b477d06519066330601ab5f84a019beecce2061575f6cdfd829900fb48, texts copied by repr(), i.e. verbatim; each value is
# (the reviewer's id, text)). B12-B27 = U1-U16 and B28-B29 = the review's negated-(c) texts: must FAIL V5.
READY_UNFIT = {
    'B12': ('U1', 'The best response states its choice as a single capital letter. Score 1 if the final answer is correct; the soundness of the reasoning does not matter.'),
    'B13': ('U2', 'Answers should be terse. The correct final answer wins; among correct answers, check for errors in the reasoning, and favour the terse one.'),
    'B14': ('U3', 'The response must be a JSON object {"answer": "<letter>"}. A correct final answer in that JSON wins; a response with a reasoning error or any prose outside the JSON loses.'),
    'B15': ('U4', 'Prefer responses that get straight to the point. The correct final answer wins first; then the response with fewer reasoning errors.'),
    'B16': ('U5', "The final answer is judged correct only when the response is formatted as 'Answer: X' on its last line. Among correct responses, sounder reasoning wins."),
    'B17': ('U6', 'Responses that pad their answer with lengthy reasoning should be scored lower. Check the final answer and any reasoning errors.'),
    'B18': ('U7', 'Correct final answer first. When both are correct, the response that reaches it in fewer words, with valid reasoning steps, is better.'),
    'B19': ('U8', 'Correct final answer first. Then the response whose reasoning steps are valid and which avoids unnecessary detail wins.'),
    'B20': ('U9', 'Check the final answer against the correct option; responses written in Markdown, bullet points or headings lose, as do responses with reasoning errors.'),
    'B21': ('U10', 'The final answer must appear in bold as **X**. Correct final answer wins; then sounder reasoning.'),
    'B22': ('U11', 'A good response is a bare option letter. The correct final answer wins; if both are correct, the response with fewer reasoning errors wins, and a bare letter has none.'),
    'B23': ('U12', 'Prefer the response whose final answer is correct; ties go to the one that is quicker to read, provided its reasoning is sound.'),
    'B24': ('U13', 'The correct final answer wins. Brevity is a virtue: when both are correct, the response with sound reasoning and less text is better.'),
    'B25': ('U14', 'Only responses that output valid JSON with an "answer" field are scored. The correct final answer wins; then fewer reasoning errors.'),
    'B26': ('U15', '1. The correct final answer wins.\n2. If both are correct, the response with fewer reasoning errors wins.\n3. Regardless of the reference, the shorter response wins remaining ties.'),
    'B27': ('U16', '1. Correct final answer wins.\n2. If both are correct, prefer sound reasoning.\n3. Ignore the reasoning and prefer the concise response when still tied.'),
    'B28': ('negated-(c) 1', 'Score 1 if the final answer is correct; the soundness of the reasoning does not matter.'),
    'B29': ('negated-(c) 2', 'Reasoning errors are irrelevant; ignore the steps entirely.'),
}
# F6-F19 = G1-G14 (fit rubrics): must PASS V5.
READY_FIT = {
    'F6': ('G1', "Decide which response gets the right answer. If only one response's final answer matches the correct option, it wins. If both are right or both wrong, the one whose reasoning has fewer errors wins; otherwise TIE."),
    'F7': ('G2', '1. Determine the correct option, treating the reference as fallible.\n2. The response whose final answer is correct beats one that is wrong, missing or truncated.\n3. If the final answers tie, prefer the response with valid, well-justified steps.\n4. Length and style are irrelevant.'),
    'F8': ('G3', 'Correct final answer beats incorrect. Between two correct answers, prefer the one whose argument is logically valid; a response with a flawed derivation loses the tie. Do not penalise explanations or reward their absence.'),
    'F9': ('G4', "1. Read each response's final option letter.\n2. Right answer beats wrong answer.\n3. If both answers are right, prefer the response whose working contains fewer mistakes.\n4. A short response and a long one are judged the same way."),
    'F10': ('G5', 'The response with the correct final answer wins, even if its explanation is brief. If both are correct, the response whose reasoning contains errors loses.'),
    'F11': ('G6', 'Compare final answers to the correct option; a correct final answer wins regardless of how the response is formatted. If both are correct, prefer the response with sound reasoning and no calculation errors.'),
    'F12': ('G7', 'A correct final answer wins. If both final answers are correct, the response whose reasoning is more rigorous wins; a longer response does not win for being longer.'),
    'F13': ('G8', 'Penalise errors in the explanation, and prefer the response with the correct final answer; sound reasoning breaks ties.'),
    'F14': ('G9', 'The response whose final answer is correct wins. When both are correct or both wrong, the response whose steps contain fewer unsupported claims wins; otherwise TIE. A response that fails to state a letter loses.'),
    'F15': ('G10', "1. Identify each response's final answer letter.\n2. The correct final answer wins.\n3. If tied, the more rigorous reasoning wins; a brief but correct argument is as good as a long one."),
    'F16': ('G11', 'The final answer letter alone determines correctness; the reasoning is then checked for errors.'),
    'F17': ('G12', '1. A correct final answer beats a wrong one.\n2. If both are correct, the response with sounder reasoning wins, even when it is shorter.\n3. Otherwise TIE.'),
    'F18': ('G13', '1. Check each final answer against the correct option; the reference may be wrong.\n2. A response that states no letter has no final answer.\n3. Between equally correct answers, fewer reasoning mistakes wins.\n4. Penalise factual errors in the working, not its length.'),
    'F19': ('G14', 'The correct final answer wins. If both final answers are equally correct, prefer the response whose reasoning is valid and complete; a concise response is not better or worse than a long one.'),
}
# F20-F43 = the 24 neutrality restatements N1-N24: each must pass (b) ALONE, and must PASS V5 in full when it replaces
# sentence 5 of CONTROL_FIT_TEXT (NEUTRALITY_FRAME): a restatement is a fragment, so (a) and (c) are read on the frame.
READY_NEUTRALITY = {
    'F20': ('N1', 'Do not reward or penalise length, formatting, or the presence or absence of an explanation.'),
    'F21': ('N2', 'Length, formatting and whether an explanation is given must not affect the verdict.'),
    'F22': ('N3', 'Length, formatting, and the presence or absence of an explanation are irrelevant.'),
    'F23': ('N4', 'A longer or shorter response is neither better nor worse.'),
    'F24': ('N5', 'Formatting and length never count for or against a response.'),
    'F25': ('N6', 'Neither length nor formatting nor the presence of an explanation earns or loses credit.'),
    'F26': ('N7', 'Explanations are not required; a correct answer without reasoning is not penalised.'),
    'F27': ('N8', 'The presence or absence of an explanation does not change the outcome.'),
    'F28': ('N9', 'Do not favour longer or shorter responses, or penalise missing explanations.'),
    'F29': ('N10', 'Responses are not judged on length or formatting.'),
    'F30': ('N11', 'A short correct response wins over a long incorrect one.'),
    'F31': ('N12', 'A longer response does not score higher.'),
    'F32': ('N13', 'Length is not a criterion; neither is formatting.'),
    'F33': ('N14', 'Never penalise a response for its length, formatting, or for including or omitting an explanation.'),
    'F34': ('N15', 'Do not reward or penalize length, formatting, or whether an explanation is present.'),
    'F35': ('N16', 'A response is not better because it is longer, shorter, or more elaborately formatted.'),
    'F36': ('N17', 'An explanation is neither required nor penalized.'),
    'F37': ('N18', 'Brevity and verbosity are neutral.'),
    'F38': ('N19', "Don't reward length or formatting, and don't penalise a missing explanation."),
    'F39': ('N20', 'Ignore length and formatting; a bare letter and a full derivation are judged the same way.'),
    'F40': ('N21', 'Treat length, formatting, and the presence or absence of an explanation as irrelevant.'),
    'F41': ('N22', 'A terse response and a detailed one are judged by the same standard.'),
    'F42': ('N23', 'Length and formatting do not matter, and a response without an explanation is not penalized.'),
    'F43': ('N24', 'Length or formatting must not influence the decision.'),
}

READY_PROBE_SHA256 = "30fecaffeca205de42ea08f7a257032df73bcbda0ea78f6d7b639a6c59537327"     # sha256 of the canonical JSON of READY_UNFIT / READY_FIT / READY_NEUTRALITY
NEUTRALITY_FRAME = F.CONTROL_FIT_TEXT.rsplit("\n", 1)[0] + "\n5. "    # CONTROL_FIT_TEXT's sentences 1-4, then "5. <N>"

# KNOWN LIMITS (the READY review's M1 / F1b change 7: V5 is a screen). Constructed texts on which V5 is WRONG, pinned with
# the (wrong) outcome V5 gives today, so the limit is executed and any change to it is seen. Every text of the READY review
# (B12-B29 unfit, F6-F43 fit) is decided correctly: none of them is a known limit.
KNOWN_LIMITS = {
    "KL1": ("fit, V5 FAILS: a reasoning criterion sharing its clause with 'irrelevant' is not counted for (c)",
            "1. The correct final answer wins.\n2. If both are correct, prefer sounder reasoning, length being irrelevant.",
            False),
    "KL2": ("fit, V5 FAILS: 'working' as a penalty object", "1. The correct final answer wins.\n2. If both are correct, the"
            " response whose working is flawed loses; sound reasoning wins.", False),
    "KL3": ("unfit, V5 PASSES: a brevity reward placed after a concessive is not read (the concessive guard)",
            "1. The correct final answer wins.\n2. If both are correct, even if its reasoning is less sound, the shorter"
            " response wins.", True),
    "KL4": ("unfit, V5 PASSES: a guarded pattern sharing its clause with an unrelated form disclaimer",
            "1. The correct final answer wins, with sound reasoning next.\n2. Ignore formatting and prefer the shorter"
            " response.", True),
}


def ready_sha():
    return sha256_text(json.dumps({"unfit": READY_UNFIT, "fit": READY_FIT, "neutrality": READY_NEUTRALITY},
                                  sort_keys=True, ensure_ascii=True))


def load_r1_rubric():
    rub = I.load_artefact(os.path.join(ROOT, *R1_ARTEFACT_REL.split("/")), R1_ARTEFACT_SHA)
    return rub.rubric, rub.rubric_sha256


# ── ARCH-V2-INDUCE-RUBRIC-3: the registration components (files of record, READ ONLY; LF is the rendering of record) ──
REG_DIR_REL = "experiment_results/archv2/induce_rubric_3_registration"
# (file, blob (git hash-object of the LF bytes), sha256-lf, sha256-crlf): the registrar's pins at 39c81c0
COMPONENTS = {
    "system": ("induction_system_jv2_induce_5.txt", "f4dccb6411204543d01019b76ef9c14003372572",
               "e95c59b22c3df56b79f2ed9a93f8b6912ca8aff15d78d849c79c9ba17c8896d7",
               "e95c59b22c3df56b79f2ed9a93f8b6912ca8aff15d78d849c79c9ba17c8896d7"),
    "unfit3": ("unfit3.json", "852a1d36eae62aca30435b5c5d24d8d8bf92e475",
               "c17f4f47d0fb10afef228478e5f76f796a7921f5a828496f65f0193ddd424021",
               "0357b66a6567094c30482b527a120860523454073a34938968878189efc58fc8"),
    "fit3": ("fit3.json", "c82543248d7f6375fd1ddfbaa3126625e15dd5e2",
             "50eba5bed2fceb131c35b6d93435155593d356844bdeb0add18eb6fb4c67f17a",
             "43c57783f0f54b2b6a5c2d5e30299ac62671a88c77eeb4fe9d281361d76535b7")}
UNFIT3_KEYS = ["D%d" % k for k in range(1, 9)] + ["E%d" % k for k in range(1, 7)] + ["T%d" % k for k in range(1, 7)]
FIT3_KEYS = ["P%d" % k for k in range(13)]
# the INDUCE-RUBRIC-2 artefact of record (committed), for C-V5-neg-2 and T7
R2_ARTEFACT_REL = "experiment_results/archv2/induce_rubric_2/rubric_mcq_ARCH-V2-INDUCE-RUBRIC-2.json"
R2_ARTEFACT_SHA = "475b68536c8e0f771ba82b71370f28bb4defe91fbe11315eb64953bd00b71eea"
R2_RUBRIC_SHA = "ace41ede9b19974aaa6c29881aff2e17dae353c0ce05f5d0e246bd3edf2a49e0"
GENERIC_RUBRIC_SRC_REL = "tools/analysis/rubric_value_contrast.py"
# -2 READY D5, fixed in the -3 selftest only: B29's FULL text (the -2 selftest pins its second sentence as B29)
B29F = "The correct final answer wins. Reasoning errors are irrelevant; ignore the steps entirely."
# the jv2-induce-4 INDUCTION_SYSTEM (sha256 67b62162..., the -2 pin), for the kept-sentence check
SYSTEM_4 = (
    "You write the evaluation rubric an impartial judge will use to compare two model responses to one question. "
    "The judge sees the question text without its options list, a reference solution that may be wrong (given as one "
    "option letter with that option's text), and the two responses in full, each followed, when its chosen letter can "
    "be read, by that letter with its option's text. The responses are free-form text, usually step-by-step reasoning "
    "that ends in one option letter as the final answer; a response may be truncated or empty, or may state no letter. "
    "The rubric decides which response better answers the question: correctness of the final answer first, then "
    "soundness of the supporting reasoning. It must not reward or penalise length, formatting, or the presence or "
    "absence of an explanation. You are shown example questions of ONE corpus type so that the rubric fits the type's "
    "answer contract. The rubric must be generic to the type: it must not name, quote or paraphrase any example, and it "
    "must carry no domain facts. Reply with a single JSON object and nothing else: {\"rubric\": <the rubric, at most 12 "
    "lines>}")
SYSTEM_4_SHA = "67b621624d63e416e985c440db713ca23e550598c5f93d9ce580f2ffbb891ebf"
SENTENCE_NAMES = ("S1", "S2", "S2b", "S3", "S4", "S5", "S6", "S7", "S8", "S9", "S10", "S11", "S12")
KEPT_SENTENCES = ("S1", "S2", "S4", "S5", "S10", "S11", "S12")


def sentences(s):
    return re.split(r"(?<=\.) (?=[A-Z])", s)


def read_component(key):
    name, _blob, _lf, _crlf = COMPONENTS[key]
    path = os.path.join(ROOT, *REG_DIR_REL.split("/"), name)
    with open(path, "rb") as f:
        raw = f.read()
    lf = raw.replace(b"\r\n", b"\n")
    crlf = lf.replace(b"\n", b"\r\n")
    return raw, {"blob": git_blob_lf(path), "sha256_lf": hashlib.sha256(lf).hexdigest(),
                 "sha256_crlf": hashlib.sha256(crlf).hexdigest(), "working_tree_crlf": b"\r\n" in raw}


def load_r2_rubric():
    rub = I.load_artefact(os.path.join(ROOT, *R2_ARTEFACT_REL.split("/")), R2_ARTEFACT_SHA)
    return rub.rubric, rub.rubric_sha256


def generic_rubric_sha():
    """sha256 of rubric_value_contrast.GENERIC_RUBRIC, read by AST (the file is NOT imported)."""
    with open(os.path.join(ROOT, *GENERIC_RUBRIC_SRC_REL.split("/")), encoding="utf-8") as f:
        tree = ast.parse(f.read())
    vals = [ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign) and len(n.targets) == 1 and
            getattr(n.targets[0], "id", None) == "GENERIC_RUBRIC"]
    return (sha256_text(vals[0]), len(vals[0])) if len(vals) == 1 else (None, len(vals))


# ── the builder's batteries for jv2-v5-4 (constructed texts; NOT the registered corpora): one text per new named part, so
# each part is OBSERVABLE (its removal changes a verdict). FRAME carries (a') and (c) and no other leg's pattern. ──
FRAME = ("The correct final answer wins. If both are right or both wrong, the response with fewer reasoning errors wins;"
         " otherwise TIE. ")
FRAME_NT = "The correct final answer wins. If both are right or both wrong, the response with fewer reasoning errors wins. "
# (d2): each names the reference with EXACTLY ONE sceptic cue (the selftest checks it is exactly that one); the registered
# corpora carry the other four: may_be_wrong (F18), possibly_wrong (P3), verify (F4), fallible (F7)
SCEPTIC_FIT = {
    "own_working": FRAME + "Decide correctness by your own working and consult the reference.",
    "one_input": FRAME + "The reference is one input among others.",
    "evidence": FRAME + "Weigh the reference as evidence.",
    "hint": FRAME + "Read the reference as a hint.",
    "not_the_key": FRAME + "The reference is not the answer key.",
    "independent": FRAME + "Solve the question independently of the reference.",
    "not_proof": FRAME + "A letter shared with the reference is not proof of anything.",
    "may_contain_errors": FRAME + "The reference solution may contain errors.",
    "not_always_right": FRAME + "The reference is not always right.",
    "caution": FRAME + "Read the reference with caution."}
SCEPTIC_IN_CORPORA = {"may_be_wrong": ("ready", "F18"), "possibly_wrong": ("fit3", "P3"), "verify": ("probe", "F4"),
                      "fallible": ("ready", "F7")}
# the reference cue (the (d1) / (e) guard): a (d1) or (e) match discounted by that cue; the corpora carry not_merely (P3),
# do_not_treat_as (P6), not_penalised_for (P12), not_correct_because (P0, P1)
CUE_FIT = {
    "neg_make_mean": FRAME + "Matching the reference does not make a final answer correct, and the reference may be wrong.",
    "rather_than": FRAME + "Decide correctness by your own working rather than by matching the reference letter.",
    "not_proof_of": FRAME + "Agreement with the reference is not proof of correctness, since the reference may be wrong.",
    "not_correct_because": FRAME + "A final answer that agrees with the reference is not correct just because of that"
                                   " agreement; the reference may be wrong.",
    "neg_mark_down": FRAME + "Do not mark down a response for having no reasoning.",
    "no_credit": FRAME + "Showing more reasoning earns no credit."}
# the prompt's own S2b, S3, S6-S9 restated in rubric voice (the reply is likely to echo them): must PASS
ECHO_FIT = {
    "S2b+S6": ("Correctness means correct for the question: decide it by your own working on the question and use the"
               " reference solution, when one is shown, as one input to that working that may be wrong, never as the"
               " yardstick; do not define a correct final answer as one that matches or agrees with the reference. Some"
               " questions carry no reference solution. If both final answers are right or both wrong, the response with"
               " fewer reasoning errors wins; otherwise TIE."),
    "S7": ("The correct final answer wins. Whether its final answer is right or wrong, a response is neither preferred nor"
           " penalised merely for giving no reasoning or for giving more reasoning: reasoning is compared only by the"
           " errors or unsupported steps it contains."),
    "S8": ("The correct final answer wins. TIE is the correct verdict when both final answers are right, or both are"
           " wrong, and neither response's reasoning has fewer errors or unsupported steps than the other's; do not reserve"
           " TIE for identical responses, do not forbid or discourage TIE, and do not default to either response."),
    "S9": ("The correct final answer wins; then fewer reasoning errors wins. Call the two responses Model A and Model B,"
           " and make no criterion depend on which of them is shown first."),
    "S3": ("The correct final answer wins; then fewer reasoning errors wins. A response may give a final answer with no"
           " reasoning at all, either as a bare letter or as an empty response seen only as a one-line note naming the"
           " option it selected or saying that it selected none.")}
# negated mentions the unguarded (f) patterns must not read as suppression, and (e) negations carried by jv2-v5-3's cue;
# plus the errors-in exemption (an object after "errors in its")
NEG_FIT = {
    "tie_not_only_identical": FRAME + "A TIE is not only for identical responses.",
    "no_default_winner": FRAME + "Neither Model A nor Model B wins by default.",
    "tie_not_avoided": FRAME + "Do not avoid a TIE when it is the right verdict. TIE is not a last resort.",
    "not_preferred_for_showing": FRAME + "A response is not preferred for showing its reasoning, nor penalised for giving"
                                         " none.",
    "bare_letter_not_lose": FRAME + "A bare letter does not lose for lacking reasoning.",
    "more_not_better": FRAME + "More reasoning is not better.",
    "errors_in_exempt": ("The correct final answer wins. If both are right or both wrong, the response with fewer errors in"
                         " its detailed reasoning wins; otherwise TIE.")}
# one text per new part that fails ON THAT PART ONLY (the pinned firing list): parts the registered corpora do not isolate
PART_UNFIT = {
    "d2": (("The correct final answer wins, using the reference solution as the guide. If both are right or both wrong,"
            " the response with fewer reasoning errors wins; otherwise TIE."), ["d2"]),
    "reference_is_key": (("The reference may be wrong, but the reference is the answer key for scoring. If both are right"
                          " or both wrong, the response with fewer reasoning errors wins; otherwise TIE."),
                         ["a'", "d1:reference_is_key"]),
    "correct_is_reference": (("The reference may be wrong; still, the correct final answer is the reference's letter. If"
                              " both are right or both wrong, the response with fewer reasoning errors wins; otherwise"
                              " TIE."), ["a'", "d1:correct_is_reference"]),
    "never_tie": (FRAME_NT + "Never output TIE.", ["f:never_tie"]),
    "always_winner": (FRAME_NT + "Always choose a winner.", ["f:always_winner"]),
    "positional_by_default": (FRAME_NT + "By default, prefer Model A.", ["f:positional_by_default"])}
# the per-class leg each registered unfit text must fail ON ITSELF (not only overall)
LEG_OF_CLASS = {"D": "d1", "E": "e", "T": "f"}


BATTERY_SHA256 = "8382892021bd690edd34ca707833f96b37f19894392e504b6e4f54ca95c30290"   # sha256 of battery_sha()'s canonical JSON


def battery_sha():
    return sha256_text(json.dumps({"frame": FRAME, "frame_nt": FRAME_NT, "sceptic": SCEPTIC_FIT, "cue": CUE_FIT,
                                   "echo": ECHO_FIT, "neg": NEG_FIT, "part_unfit": PART_UNFIT}, sort_keys=True,
                                  ensure_ascii=True))


def v54_suite(r1_rubric, t7_rubric, unfit3, fit3, rules=None):
    """The jv2-v5-4 checks as (name, ok) pairs, under the rule of record (rules None) or a MUTANT rule dict
    (induce_fitness_3.build_rules_v54 with one part off), so every mutant runs through the same suite."""
    def g(t):
        return G.v5(t, rules)
    neg, neg2, pos = g(r1_rubric), g(t7_rubric), g(F.CONTROL_FIT_TEXT)
    res = [("C-V5-neg: ef9c9e87 FAILS on (a') and (b)", bool(neg["pass"] is False and neg["a"] is False and
                                                             neg["b"] is False)),
           ("C-V5-neg-2: ace41ede FAILS on (d) AND (f)", bool(neg2["pass"] is False and neg2["d"] is False and
                                                               neg2["f"] is False)),
           ("C-V5-pos: CONTROL_FIT_TEXT PASSES", bool(pos["pass"] is True)),
           ("B29f FAILS", bool(g(B29F)["pass"] is False)),
           ("(a') D1 FAILS on (a') itself (its only correctness mention sits in a live reference-agreement clause)",
            bool(g(unfit3["D1"])["a"] is False))]
    for k, t in PROBE_UNFIT.items():
        res.append(("C-V5-probe %s FAILS" % k, bool(g(t)["pass"] is False)))
    for k, t in PROBE_FIT.items():
        res.append(("C-V5-probe %s PASSES" % k, bool(g(t)["pass"] is True)))
    for k, (src, t) in READY_UNFIT.items():
        res.append(("READY probe %s (%s) FAILS" % (k, src), bool(g(t)["pass"] is False)))
    for k, (src, t) in READY_FIT.items():
        res.append(("READY probe %s (%s) PASSES" % (k, src), bool(g(t)["pass"] is True)))
    for k, (src, t) in READY_NEUTRALITY.items():
        res.append(("READY probe %s (%s) PASSES in the control frame" % (k, src),
                    bool(g(NEUTRALITY_FRAME + t)["pass"] is True)))
    for k, t in unfit3.items():
        r = g(t)
        res.append(("C-V5-probe-3 %s FAILS" % k, bool(r["pass"] is False)))
        res.append(("C-V5-probe-3 %s FAILS on its class leg (%s) itself" % (k, LEG_OF_CLASS[k[0]]),
                    bool(r[LEG_OF_CLASS[k[0]]] is False)))
    res.append(("C-V5-probe-3 T7 (ace41ede) FAILS", bool(neg2["pass"] is False)))
    for k, t in fit3.items():
        res.append(("C-V5-probe-3 %s PASSES" % k, bool(g(t)["pass"] is True)))
    for name, t in SCEPTIC_FIT.items():
        r = g(t)
        res.append(("battery sceptic %s PASSES" % name, bool(r["pass"] is True)))
    for name, t in list(CUE_FIT.items()) + list(ECHO_FIT.items()) + list(NEG_FIT.items()):
        res.append(("battery fit %s PASSES" % name, bool(g(t)["pass"] is True)))
    for name, (t, want) in PART_UNFIT.items():
        r = g(t)
        res.append(("battery unfit %s FAILS with exactly %s" % (name, want), bool(r["pass"] is False and
                                                                                  G.firing(r) == want)))
    return res


def v54_mutants():
    """-> [(name, rules)]: every NEW named part of jv2-v5-4 removed or switched off in turn."""
    out = [("(a') amendment off", G.build_rules_v54(a_prime=False)),
           ("(d2) conditional off", G.build_rules_v54(d2=False)),
           ("(d1) guard off", G.build_rules_v54(d1_guard=False)),
           ("(e) guard off", G.build_rules_v54(e_guard=False)),
           ("(e) errors-in exemption off", G.build_rules_v54(e_errors_in=False))]
    out += [("reference cue %s removed" % n, G.build_rules_v54(drop_cue_ref=(n,))) for n, _r in G.CUE_REF_ENTRIES]
    out += [("(d1) part %s removed" % n, G.build_rules_v54(drop_d1=(n,))) for n, _r in G.D1_ENTRIES]
    out += [("(d2) sceptic cue %s removed" % n, G.build_rules_v54(drop_sceptic=(n,))) for n, _r in G.SCEPTIC_ENTRIES]
    out += [("(e) part %s removed" % n, G.build_rules_v54(drop_e=(n,))) for n in ("presence_reward", "depth_reward",
                                                                                   "absence_penalty")]
    out += [("(f) part %s removed" % n, G.build_rules_v54(drop_f=(n,))) for n, _r in G.F_ENTRIES]
    return out


def v5_suite(r1_rubric, rules=None, require_correctness=True, require_reasoning=True):
    """The V5 checks as (name, ok) pairs, under the rule of record (rules None) or a MUTANT rule (induce_fitness.build_rules
    with one part off), so every mutant runs through the same suite."""
    def g(t):
        if rules is None and require_correctness and require_reasoning:
            return F.v5(t)
        r = rules if rules is not None else F.build_rules()
        return F.v5_rules(t, r, require_correctness, require_reasoning)
    neg = g(r1_rubric)
    pos = g(F.CONTROL_FIT_TEXT)
    res = [("C-V5-neg: V5 FAILS on the INDUCE-RUBRIC-1 rubric on BOTH (a) and (b)",
            bool(neg["pass"] is False and neg["a"] is False and neg["b"] is False)),
           ("C-V5-pos: V5 PASSES on the fit control text (neutrality clause included)", bool(pos["pass"] is True)),
           ("a form-clean text naming no final-answer correctness FAILS V5 on (a)", bool(g(NO_CORRECTNESS)["pass"] is False)),
           ("(c) a form-clean text naming correctness but no reasoning criterion FAILS V5 on (c)",
            bool(g(NO_REASONING)["pass"] is False)),
           ("contrastive split: B8 FAILS on (b) itself (the cue in 'do not penalize length' does not excuse 'but penalize"
            " extra text')", bool(g(PROBE_UNFIT["B8"])["b"] is False)),
           ("(c) negation: B28 (the soundness of the reasoning 'does not matter') FAILS on (c) itself",
            bool(g(READY_UNFIT["B28"][1])["c"] is False))]
    for k, t in PROBE_UNFIT.items():
        res.append(("C-V5-probe %s FAILS V5" % k, bool(g(t)["pass"] is False)))
    for k, t in PROBE_FIT.items():
        res.append(("C-V5-probe %s PASSES V5" % k, bool(g(t)["pass"] is True)))
    for k, (src, t) in READY_UNFIT.items():
        res.append(("READY probe %s (%s) FAILS V5" % (k, src), bool(g(t)["pass"] is False)))
    for k, (src, t) in READY_FIT.items():
        res.append(("READY probe %s (%s) PASSES V5" % (k, src), bool(g(t)["pass"] is True)))
    for k, (src, t) in READY_NEUTRALITY.items():
        res.append(("READY probe %s (%s) passes (b) alone and PASSES V5 in the control frame" % (k, src),
                    bool(g(t)["b"] is True and g(NEUTRALITY_FRAME + t)["pass"] is True)))
    for t in DISCLAIMERS:
        res.append(("disclaimer passes (b): %r" % t, bool(g(t)["b"] is True)))
    for t in FIT_PHRASINGS:
        res.append(("fit phrasing passes (b): %r" % t, bool(g(t)["b"] is True)))
    for name, t in sorted(TRIGGERS.items()):
        res.append(("trigger %s FAILS (b): %r" % (name, t), bool(g(t)["b"] is False)))
    return res


def mutants():
    """-> [(name, rules, require_correctness, require_reasoning)]: every part of the rule removed or reverted in turn."""
    base = F.build_rules()
    out = []
    for k, (name, _rx, _g) in enumerate(base["form"]):
        out.append(("form pattern %s removed" % name, dict(base, form=tuple(x for j, x in enumerate(base["form"])
                                                                              if j != k)), True, True))
    out.append(("correctness requirement removed", dict(base, correctness="(?!)"), False, True))
    out.append(("correctness regex loosened to a bare 'correct'", dict(base, correctness="correct"), True, True))
    out.append(("(c) reasoning requirement removed", dict(base, reasoning="(?!)"), True, False))
    for opt, label in (("a_right_correctness", "(a) 'right answer' / 'correctness' (READY H1 (v))"),
                       ("c_negation", "(c) negation guard (READY M1)"),
                       ("concessive", "concessive guard on reward_form (READY H1 (ii))"),
                       ("errors_in_exempt", "'<errors> in the explanation / working' exemption (READY H1 (iii))"),
                       ("alone_exempt", "'letter alone determines' exemption (READY H1 (iv))"),
                       ("short_correct_exempt", "'short correct' exemption"),
                       ("m1_reward_objects", "M1 reward objects (brevity, fewer words, to the point, ...)"),
                       ("guard", "negation guard"),
                       ("contrast", "contrastive guard split (but / however / whereas / yet)")):
        out.append(("%s off" % label, F.build_rules(**{opt: False}), True, True))
    for name, _rx in F.CUE_ENTRIES:
        out.append(("CUE entry %s removed" % name, F.build_rules(drop_cue=(name,)), True, True))
    out.append(("CUE ignore_form reverted to a bare 'ignore / disregard' (READY M1 narrowing)",
                F.build_rules(cue_override={"ignore_form": r"\b(?:ignor\w*|disregard\w*)\b"}), True, True))
    out.append(("CUE regardless_form reverted to a bare 'regardless / irrespective of' (READY M1 narrowing)",
                F.build_rules(cue_override={"regardless_form": r"\b(?:regardless|irrespective)\s+of\b"}), True, True))
    return out


class Stub:
    """call_judge_full's shape: (content, provider, completion_tokens, latency_s, finish_reason, msg)."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []

    def __call__(self, system, user):
        self.calls.append(hashlib.sha256(rr.payload_bytes(system, user)).hexdigest())
        r = self.replies.pop(0)
        if isinstance(r, BaseException):
            raise r
        content, finish = (r, "stop") if isinstance(r, str) else r
        rid = "resp-%d" % len(self.calls)
        if finish == "content_filter":
            return ("", "azure:refusal", 0, 0.1, "content_filter", {"_refusal": '{"error": "content_filter"}',
                                                                   "_response_id": rid})
        return (content, "azure:" + R.P.JUDGE_REQUESTED, 123, 0.2, finish, {"_response_id": rid})


GOOD = json.dumps({"rubric": "1. Decide whether each final answer satisfies the question's answer contract.\n"
                             "2. Prefer the response whose final answer is correct.\n"
                             "3. If both are correct, prefer the sounder reasoning; otherwise TIE."})   # (c): F1b
GOOD2 = json.dumps({"rubric": "1. The correct final answer wins.\n2. Both correct: fewer unsupported steps.\n3. Else TIE."})


EXCL = {"path": None}


def paths_for(tmp, gen, ev, name):
    p = R.Paths(out_dir=os.path.join(tmp, name))
    p.gen, p.eval, p.check_manifest = gen, ev, False
    p.excl = EXCL["path"]          # the fixture's own overlap exclusion list (built below with induce_overlap_audit)
    return p


def ledger_fixture(d):
    os.makedirs(d)
    rows = [{"test": "TRACE-TRUNCATION", "launch": "--run", "calls": 2178, "ts": "x"},
            {"test": "CANARY-EPOCH2-RUNG", "launch": "--run", "calls": 1252, "ts": "x"}]
    with open(atl.day_ledger_path(d), "x", encoding="utf-8") as f:
        json.dump(rows, f)
    return d


def reset_flag():
    """Each scenario stands for its own process: the eval-view flag (no call after the eval_view open, per PROCESS) is
    cleared between scenarios. Production launches are separate processes."""
    R._EVAL_OPENED["at"] = None


def launch(ck, tmp, gen, ev, name, replies, gen_sha, eval_sha, expect=None, ledger=None, stub=None, out=None):
    p = paths_for(tmp, gen, ev, name)
    stub = stub or Stub(replies)
    if expect is None:
        reset_flag()
        expect = R.dry_run(p, DEV_SEED, None, gen_sha, eval_sha, out=lambda s: None)["payload_sha256"]
    reset_flag()
    res = R.run(stub, expect, p, DEV_SEED, None, gen_sha, eval_sha, ledger_dir=ledger, atl=atl if ledger else None,
                out=out or (lambda s: None))
    return p, stub, res


def has(lines, text):
    return any(text in x for x in lines)


def brute_runs(gen, ev):
    """Independent of the audit's 8-gram chain index: the longest common run of induction._tokens between each candidate's
    texts (stem and options) and each EVAL text, by the classic O(n*m) dynamic programme. Candidates (independently):
    every gen_view variant of the C4 population (corpus_version / contract per R.POPULATION) on a TRAIN item."""
    def texts(stem, opts):
        return [stem] + [o for o in (json.loads(opts) if opts else []) if isinstance(o, str)]
    e = dv2views.open_eval("judge", ev)
    try:
        etoks = [I._tokens(t) for _v, st, op in e.execute("SELECT variant_id, stem, options_sorted_json FROM variant")
                 for t in texts(st, op)]
    finally:
        e.close()
    g = dv2views.open_generation("construct", gen)
    try:
        rows = {v: (st, op) for v, st, op in g.execute(
            "SELECT v.variant_id, v.stem, v.options_sorted_json FROM variant v JOIN side s ON s.item_id = v.item_id WHERE"
            " s.side = 'TRAIN' AND v.corpus_version = ? AND v.contract_id IN (%s)" % ",".join(
                "?" * len(R.POPULATION["contracts"])), [R.POPULATION["corpus_version"]] + R.POPULATION["contracts"])}
    finally:
        g.close()
    out = {}
    for v, (st, op) in rows.items():
        best = 0
        for t in texts(st, op):
            a = I._tokens(t)
            for b in etoks:
                prev = [0] * (len(b) + 1)
                for x in a:
                    cur = [0] * (len(b) + 1)
                    for j, y in enumerate(b, 1):
                        if x == y:
                            cur[j] = prev[j - 1] + 1
                            if cur[j] > best:
                                best = cur[j]
                    prev = cur
        out[v] = best
    return out


def selftest(out=print):
    ck = T.Checks(out)
    tmp = tempfile.mkdtemp(prefix="jv2_induce_run_")
    try:
        out("[SELFTEST-INDUCE-RUN-3] %s selftest (python %s, -O %s); synthetic fixture under %s; stub poster; zero calls"
            % (R.TEST, sys.version.split()[0], "on" if not __debug__ else "off", tmp))
        gen, ev = T.build_views(tmp, extra_mmlu=40)   # >= 40 mmlu-pro-v2 MC_LETTER TRAIN variants for the C4 population
        gen_sha, eval_sha = dv2ro.file_sha256(gen), dv2ro.file_sha256(ev)
        # ruling D1: the zero-call overlap audit on the fixture; the inducer reads ONLY its list, sha-pinned
        audit_lines = []
        arec = OA.build(gen, gen_sha, ev, eval_sha, out=audit_lines.append)
        EXCL["path"] = os.path.join(tmp, "audit", "overlap_exclusions.json")
        OA.write(arec, EXCL["path"])
        R.EXCL_SHA = arec["list_sha256"]       # the fixture's pin (production pins the list of record)
        ex_ids = {e["variant_id"] for e in arec["excluded"]}
        gpop = [r for r in T.gen_items(gen) if r[5] == "TRAIN" and r[4] == "MC_LETTER" and r[0] in
                set(T.reference_selections(gen, DEV_SEED, n=10 ** 6, population=R.POPULATION)[1])]
        with8 = {r[0] for r in gpop if "alpha beta gamma" in r[2]}
        with7 = {r[0] for r in gpop if "iota kappa" in r[2]}
        extra = {r[0] for r in gpop if "Extra population question" in r[2]}
        runs = {e["variant_id"]: e["run"] for e in arec["excluded"]}
        ck.check("D1 audit: the candidates are the population's distinct variants; every TRAIN variant sharing EXACTLY 8"
                 " tokens with an EVAL text is excluded (run 8) and none sharing 7 (the threshold's two sides)",
                 arec["candidates"] == T.reference_selections.distinct and (ex_ids & extra) == with8 and with8 and
                 with7 and not (ex_ids & with7) and all(runs[v] == 8 for v in with8),
                 "candidates %d, excluded %d (of the extra rows %d), with8 %d, with7 %d" % (
                     arec["candidates"], len(ex_ids), len(ex_ids & extra), len(with8), len(with7)))
        # [2026-09-24, SPLIT-2 re-pin: main's data_v2 fixture (CK-CLOSE-v2) carries MASKED shared runs whose items may sit
        # on both sides; the audit must find those too. Completeness and exactness against an INDEPENDENT brute force
        # (longest common token substring, no n-gram index): every candidate's run equals the audit's (0 when < 8)]
        brute = brute_runs(gen, ev)
        ck.check("D1 audit (independent brute force): every candidate with a longest shared token run >= 8 against ONE EVAL"
                 " text is excluded with that run, and no other candidate is", {v for v, b in brute.items() if b >= 8} ==
                 ex_ids and all(runs[v] == brute[v] for v in ex_ids) and len(brute) == arec["candidates"],
                 json.dumps(sorted(b for b in brute.values() if b >= 8)))
        txt = open(EXCL["path"], encoding="utf-8").read()
        ck.check("D1 audit: the list writes NO EVAL text (entries are variant_id, run, eval_variant_id only) and records"
                 " its own sha and the eval_view sha", all(set(e) == {"variant_id", "run", "eval_variant_id"}
                                                           for e in arec["excluded"]) and "alpha beta" not in txt and
                 "question number" not in txt.casefold() and arec["eval_view_sha256_bytes"] == eval_sha and
                 OA.list_sha(json.load(open(EXCL["path"], encoding="utf-8"))) == arec["list_sha256"])
        ck.refused("D1 audit: the list is written once", lambda: OA.write(arec, EXCL["path"]), ("written once",))
        ck.refused("D1: the inducer refuses a list whose sha is not the pinned one", lambda: OA.load(
            EXCL["path"], "0" * 64, eval_sha, gen_sha), ("not the pinned",))
        ck.refused("D1: the inducer refuses a list built on another eval_view", lambda: OA.load(
            EXCL["path"], arec["list_sha256"], "1" * 64, gen_sha), ("built on eval_view",))
        # the prompt pins (jv2-induce-4) and the V5 list pin
        pin_lines = []
        R.check_prompt_pins(out=pin_lines.append)
        ck.check("the registered jv2-induce-5 pins hold (INDUCTION_VERSION, INDUCTION_SYSTEM %s..., USER_TEMPLATE %s...,"
                 " contract descriptions %s..., V5 regex list %s...) and are printed" % (
                     R.SYSTEM_SHA[:8], R.USER_TEMPLATE_SHA[:8], R.DESCRIPTIONS_SHA[:8], R.V5_LIST_SHA[:8]),
                 I.INDUCTION_VERSION == "jv2-induce-5" and sha256_text(I.INDUCTION_SYSTEM) == R.SYSTEM_SHA and
                 sha256_text(I.INDUCTION_USER_TEMPLATE) == R.USER_TEMPLATE_SHA and R.descriptions_sha() ==
                 R.DESCRIPTIONS_SHA and G.regex_list_v54_sha256() == R.V5_LIST_SHA == G.REGEX_LIST_SHA256_V54 and
                 F.regex_list_sha256() == R.V5_BASE_LIST_SHA == F.REGEX_LIST_SHA256 and
                 has(pin_lines, R.SYSTEM_SHA) and has(pin_lines, R.V5_LIST_SHA), " | ".join(pin_lines))
        ck.check("the superseded INDUCE-RUBRIC-1 / -2 prompt shas are NOT the -3 pins (4c4bf36f..., 7ed21eba...; 67b62162...)",
                 R.SYSTEM_SHA != "67b621624d63e416e985c440db713ca23e550598c5f93d9ce580f2ffbb891ebf" and
                 R.SYSTEM_SHA != "4c4bf36f61f43f37f0057ce31e96b086528735aae338a60c1e19432a009823e7" and
                 R.USER_TEMPLATE_SHA != "7ed21eba7b9b9e13222b275400d0808706a1a4217b7f30db87391ea2fb9f7481")
        for nm, obj, attr, val in (("INDUCTION_SYSTEM", I, "INDUCTION_SYSTEM", I.INDUCTION_SYSTEM + " "),
                                   ("INDUCTION_USER_TEMPLATE", I, "INDUCTION_USER_TEMPLATE", I.INDUCTION_USER_TEMPLATE + " "),
                                   ("INDUCTION_VERSION", I, "INDUCTION_VERSION", "jv2-induce-4"),
                                   ("CONTRACT_DESCRIPTIONS", I, "CONTRACT_DESCRIPTIONS",
                                    {"MC_LETTER": "one uppercase letter (A-Z)"}),
                                   ("the V5 module pin", F, "REGEX_LIST_SHA256", "0" * 64),
                                   ("the V5 list (a pattern dropped)", F, "FORM_PATTERNS", F.FORM_PATTERNS[1:]),
                                   ("the C-V5-pos control text", F, "CONTROL_FIT_TEXT", F.CONTROL_FIT_TEXT + " "),
                                   ("the jv2-v5-4 module pin", G, "REGEX_LIST_SHA256_V54", "0" * 64),
                                   ("the jv2-v5-4 rule (a (f) part dropped)", G, "RULES_V54",
                                    G.build_rules_v54(drop_f=("never_tie",)))):
            real = getattr(obj, attr)
            setattr(obj, attr, val)
            try:
                ck.refused("a changed %s refuses the prompt pins" % nm, lambda: R.check_prompt_pins(out=lambda s: None),
                           ("not the",))
            finally:
                setattr(obj, attr, real)
        # the prompt itself (jv2-induce-5): the kept clauses; the sentence-level checks are in the -3 block below
        sys_t = I.INDUCTION_SYSTEM
        ck.check("jv2-induce-5 INDUCTION_SYSTEM: the registered neutrality clause verbatim, the response description, the"
                 " correctness-first order, the genericity and no-domain-facts clauses kept",
                 F.NEUTRALITY_CLAUSE in sys_t and "a reference solution that may be wrong" in sys_t and
                 "step-by-step reasoning that ends in one option letter" in sys_t and "may also be truncated" in sys_t and
                 "correctness of the final answer first, then soundness of the supporting reasoning" in sys_t and
                 "it must not name, quote or paraphrase any example, and it must carry no domain facts" in sys_t)
        for ct in ("math", "instruction", "agentic"):
            ck.refused("MCQ guard (rule 11): build_prompt(%r) under jv2-induce-5 (message names jv2-induce-5)" % ct,
                       lambda ct=ct: I.build_prompt(ct, [{"stem": "S?", "options": [], "contract_id": "MC_LETTER"}]),
                       (I.JV2_INDUCE_5_MCQ_ONLY, "jv2-induce-5"))
        ck.refused("MCQ guard: induce('math') under jv2-induce-5 refuses before any view is opened or call made", lambda:
                   I.induce("math", I.StubInducer(), gen, seed=DEV_SEED, out=lambda s: None), (I.JV2_INDUCE_5_MCQ_ONLY,))
        ck.check("MCQ guard: the admitting branch under jv2-induce-5: build_prompt('mcq') returns INDUCTION_SYSTEM and"
                 " check_corpus_type_for_version('mcq') returns without refusing",
                 I.check_corpus_type_for_version("mcq") is None and I.build_prompt("mcq", [{"stem": "S?", "options": ["x"],
                                                                                          "contract_id": "MC_LETTER"}])[0]
                 == I.INDUCTION_SYSTEM)
        ck.check("MCQ guard: the -3 message names jv2-induce-5; the jv2-induce-4 one is kept verbatim; the map covers exactly"
                 " the two versions", I.JV2_INDUCE_5_MCQ_ONLY == "jv2-induce-5's INDUCTION_SYSTEM is MCQ-specific; other"
                 " corpus types need their own registration" and I.JV2_INDUCE_4_MCQ_ONLY == "jv2-induce-4's INDUCTION_SYSTEM"
                 " is MCQ-specific; other corpus types need their own registration" and
                 sorted(I.MCQ_ONLY_BY_VERSION) == ["jv2-induce-4", "jv2-induce-5"])
        real_ver = I.INDUCTION_VERSION
        I.INDUCTION_VERSION = "jv2-induce-6"
        try:
            ck.refused("MCQ guard: an INDUCTION_VERSION with no rule refuses EVERY corpus type, mcq included (fail-closed;"
                       " a future bump cannot switch the refusal off)", lambda: I.check_corpus_type_for_version("mcq"),
                       ("no corpus-type rule",))
        finally:
            I.INDUCTION_VERSION = real_ver
        I.INDUCTION_VERSION = "jv2-induce-4"
        try:
            ck.refused("MCQ guard: the jv2-induce-4 branch still refuses with its own message", lambda:
                       I.check_corpus_type_for_version("math"), (I.JV2_INDUCE_4_MCQ_ONLY,))
        finally:
            I.INDUCTION_VERSION = real_ver
        ck.check("C-V5-probe: the pinned probe corpus (11 unfit B1-B11, 5 fit F1-F5) has its pinned sha256 %s..."
                 % PROBE_SHA256[:16], len(PROBE_UNFIT) == 11 and len(PROBE_FIT) == 5 and probe_sha() == PROBE_SHA256,
                 probe_sha())
        for k, t in list(PROBE_UNFIT.items()) + list(PROBE_FIT.items()):
            rp = F.v5(t)
            ck.check("C-V5-probe %s %s (READY acceptance)" % (k, "FAILS" if k.startswith("B") else "PASSES"),
                     rp["pass"] is (not k.startswith("B")), F.describe(rp))
        su = I.build_prompt("mcq", [{"stem": "S?", "options": ["x", "y"], "contract_id": "MC_LETTER"}])[1]
        su2 = I.build_prompt("mcq", [{"stem": "S?", "options": ["x"], "contract_id": "IMPORTED:acc_norm"}])[1]
        ck.check("the user turn renders MC_LETTER with its fixed contract description; a contract with none renders as its"
                 " id alone; the example options are still unlettered and pipe-joined (unchanged)",
                 ("MC_LETTER (%s)" % I.CONTRACT_DESCRIPTIONS["MC_LETTER"]) in su and "Options: x | y" in su and
                 "Answer contract(s), each with its fixed description from the corpus contract: IMPORTED:acc_norm\n" in su2,
                 su.splitlines()[1])
        # V5 FITNESS: C-V5-neg, C-V5-pos, the batteries, and the mutants
        r1_rubric, r1_sha = load_r1_rubric()
        neg = F.v5(r1_rubric)
        pos = F.v5(F.CONTROL_FIT_TEXT)
        ck.check("C-V5-neg: the INDUCE-RUBRIC-1 artefact of record loads with its pinned artefact_sha256 and rubric_sha256"
                 " ef9c9e87..., and V5 FAILS on BOTH (a) (no final-answer correctness named) and (b) (form patterns matched)",
                 r1_sha == R1_RUBRIC_SHA and neg["pass"] is False and neg["a"] is False and neg["b"] is False and
                 len(neg["b_matches"]) >= 1, F.describe(neg))
        ck.check("C-V5-pos: V5 PASSES on the fit control text (sha256 %s), which carries the instruction's own neutrality"
                 " clause verbatim" % F.CONTROL_FIT_SHA256, pos["pass"] is True and F.NEUTRALITY_CLAUSE in
                 F.CONTROL_FIT_TEXT and sha256_text(F.CONTROL_FIT_TEXT) == F.CONTROL_FIT_SHA256, F.describe(pos))
        suite = v5_suite(r1_rubric)
        for name, ok in suite:
            ck.check("V5 suite: " + name, ok)
        uniq = {k: [n for n, _s in F.v5(t)["b_matches"]] for k, t in TRIGGERS.items()}
        ck.check("V5 trigger battery covers EVERY form pattern, each trigger matched by its own pattern ONLY (so a removed"
                 " pattern is observable)", sorted(TRIGGERS) == sorted(n for n, _r, _g in F.FORM_PATTERNS) and
                 all(v == [k] for k, v in uniq.items()), json.dumps(uniq, sort_keys=True))
        ck.check("V5 has 12 form patterns; guarded / unguarded split as documented (extra_text, lowercase, penalise_form,"
                 " reward_form, format_demand guarded)", len(F.FORM_PATTERNS) == 12 and
                 sorted(n for n, _r, g in F.FORM_PATTERNS if g) == ["extra_text", "format_demand", "lowercase",
                                                                    "penalise_form", "reward_form"] and
                 F.regex_list_sha256(F.regex_list(F.build_rules())) == F.REGEX_LIST_SHA256)
        ck.check("READY probe corpus: 18 unfit (B12-B29), 14 fit (F6-F19), 24 neutrality restatements (F20-F43), pinned"
                 " sha256 %s..." % READY_PROBE_SHA256[:16], len(READY_UNFIT) == 18 and len(READY_FIT) == 14 and
                 len(READY_NEUTRALITY) == 24 and ready_sha() == READY_PROBE_SHA256, ready_sha())
        n_fp = n_fn = 0
        for k, (src, t) in list(READY_UNFIT.items()) + list(READY_FIT.items()):
            rp = F.v5(t)
            want = k.startswith("F")
            n_fp += int(want and not rp["pass"])
            n_fn += int((not want) and rp["pass"])
            ck.check("READY probe %s (%s) %s (acceptance)" % (k, src, "PASSES" if want else "FAILS"), rp["pass"] is want,
                     F.describe(rp))
        for k, (src, t) in READY_NEUTRALITY.items():
            rb, rf = F.v5(t), F.v5(NEUTRALITY_FRAME + t)
            n_fp += int(not (rb["b"] and rf["pass"]))
            ck.check("READY probe %s (%s) passes (b) alone and PASSES V5 in the control frame (acceptance)" % (k, src),
                     rb["b"] is True and rf["pass"] is True, "%s | framed: %s" % (rb["b_matches"], F.describe(rf)))
        ck.check("READY probe corpus totals: 0 false positives (fit failing) and 0 false negatives (unfit passing)",
                 n_fp == 0 and n_fn == 0, "FP %d, FN %d" % (n_fp, n_fn))
        for k, (what, t, got_pass) in KNOWN_LIMITS.items():
            ck.check("KNOWN LIMIT %s executed (%s): V5 %s as pinned" % (k, what, "PASSES" if got_pass else "FAILS"),
                     F.v5(t)["pass"] is got_pass, F.describe(F.v5(t)))
        mlist = mutants()
        for mname, rules, req_a, req_c in mlist:
            msuite = v5_suite(r1_rubric, rules, req_a, req_c)
            killed = [n for n, ok in msuite if not ok]
            ck.check("V5 MUTANT KILLED: %s (%d suite check(s) fail under it; its list sha differs from the pin)" % (
                mname, len(killed)), bool(killed) and F.regex_list_sha256(F.regex_list(rules)) != F.REGEX_LIST_SHA256,
                "; ".join(killed[:3]))
        ck.check("V5 mutant count: %d (12 form patterns + 3 (a)/(c) requirement mutants + 9 part switches + %d CUE entries"
                 " + 2 CUE narrowings)" % (len(mlist), len(F.CUE_ENTRIES)),
                 len(mlist) == 12 + 3 + 9 + len(F.CUE_ENTRIES) + 2, str(len(mlist)))
        # ══ ARCH-V2-INDUCE-RUBRIC-3: the prompt (jv2-induce-5) and the REGISTERED CONDITIONS ON V5 (jv2-v5-4) ══
        # the INDUCTION_SYSTEM component: blob + both sha256 renderings; the module constant equals it BYTE FOR BYTE
        comp = {}
        for key in ("system", "unfit3", "fit3"):
            raw, got = read_component(key)
            name, blob, lf, crlf = COMPONENTS[key]
            comp[key] = raw
            ck.check("component %s: blob:%s, sha256-lf %s..., sha256-crlf %s... (the registrar's pins; working tree %s)"
                     % (name, blob[:8], lf[:16], crlf[:16], "CRLF" if got["working_tree_crlf"] else "LF"),
                     got["blob"] == blob and got["sha256_lf"] == lf and got["sha256_crlf"] == crlf, json.dumps(got))
        ck.check("jv2-induce-5: induction.INDUCTION_SYSTEM equals induction_system_jv2_induce_5.txt BYTE FOR BYTE (sha256"
                 " e95c59b2..., 2,360 characters, no final newline) and R.SYSTEM_SHA is its sha256",
                 I.INDUCTION_SYSTEM.encode("utf-8") == comp["system"] and len(I.INDUCTION_SYSTEM) == 2360 and
                 sha256_text(I.INDUCTION_SYSTEM) == R.SYSTEM_SHA == COMPONENTS["system"][2], sha256_text(I.INDUCTION_SYSTEM))
        s5, s4 = sentences(I.INDUCTION_SYSTEM), sentences(SYSTEM_4)
        named = dict(zip(SENTENCE_NAMES, s5))
        ck.check("jv2-induce-5 sentences: 13 (S1, S2, S2b, S3-S12); the KEPT S1, S2, S4, S5, S10, S11, S12 each occur exactly"
                 " once, byte-identically, in the jv2-induce-4 text (sha256 67b62162...); S2b, S3, S6-S9 occur 0 times there;"
                 " the one jv2-induce-4 sentence not kept is the old S3", len(s5) == 13 and len(s4) == 8 and
                 sha256_text(SYSTEM_4) == SYSTEM_4_SHA and
                 all(SYSTEM_4.count(named[k]) == 1 for k in KEPT_SENTENCES) and
                 all(SYSTEM_4.count(named[k]) == 0 for k in SENTENCE_NAMES if k not in KEPT_SENTENCES) and
                 [x for x in s4 if x not in s5] == [s4[2]] and s4[2].startswith("The responses are free-form text"),
                 "%d / %d sentences" % (len(s5), len(s4)))
        # the registration's anchors of S2b / S3 / S6-S9 (the text of record is the component file; these are witnesses)
        ck.check("jv2-induce-5 new sentences carry the registered content: S2b no reference; S3 bare letter / empty"
                 " response note; S6 never the yardstick, not matches / agrees; S7 neither preferred nor penalised; S8 TIE,"
                 " identical, default; S9 Model A and Model B",
                 named["S2b"] == "Some questions carry no reference solution." and "bare letter" in named["S3"] and
                 "one-line note" in named["S3"] and "never as the yardstick" in named["S6"] and
                 "matches or agrees with the reference" in named["S6"] and "neither preferred nor penalised" in named["S7"]
                 and "must not reserve TIE for identical responses" in named["S8"] and "Model A and Model B" in named["S9"])
        # the fallback's GENERIC_RUBRIC, verified by AST (not imported)
        gsha, glen = generic_rubric_sha()
        ck.check("the FALLBACK: rubric_value_contrast.GENERIC_RUBRIC (by AST) has sha256 %s (%s characters) = the runner's"
                 " GENERIC_RUBRIC_SHA256, named in the FALLBACK line" % (gsha, glen), gsha == R.GENERIC_RUBRIC_SHA256 ==
                 "67f843eb7a632ae5bd411a9debcbaf9dedccd362e0c8355c366c6d85cb89b1dc" and glen == 81 and
                 R.GENERIC_RUBRIC_SHA256 in R.FALLBACK)
        # the registered corpora
        unfit3 = json.loads(comp["unfit3"].decode("utf-8"))
        fit3 = json.loads(comp["fit3"].decode("utf-8"))
        ck.check("C-V5-probe-3: unfit3.json carries the 20 texts D1-D8, E1-E6, T1-T6 and fit3.json the 13 texts P0-P12 (read"
                 " verbatim from the committed files; no CR inside any text)", list(unfit3) == UNFIT3_KEYS and
                 list(fit3) == FIT3_KEYS and all(isinstance(t, str) and "\r" not in t for t in list(unfit3.values()) +
                                                 list(fit3.values())))
        t7_rubric, t7_sha = load_r2_rubric()
        ck.check("C-V5-neg-2 / T7: the INDUCE-RUBRIC-2 artefact of record loads via induction.load_artefact(path,"
                 " 475b6853...) with rubric_sha256 ace41ede...", t7_sha == R2_RUBRIC_SHA and sha256_text(t7_rubric) ==
                 R2_RUBRIC_SHA, t7_sha)
        ck.check("C-V5-probe: the kept corpora carry their pinned sha256 (B1-B11 / F1-F5 329cd697...; B12-B29 / F6-F43"
                 " 30fecaff...) and B29f is B29's full text (B29 as pinned is its second sentence)",
                 probe_sha() == "329cd697fd457924b5437e754bbb2c2c6d935cb40a10b65f370da7a5d4740490" and
                 ready_sha() == "30fecaffeca205de42ea08f7a257032df73bcbda0ea78f6d7b639a6c59537327" and
                 B29F.endswith(" " + READY_UNFIT["B29"][1]) and B29F != READY_UNFIT["B29"][1])
        pin_v54 = G.regex_list_v54_sha256()
        ck.check("jv2-v5-4: REGEX_LIST_SHA256_V54 = regex_list_v54_sha256() = %s; it embeds the jv2-v5-3 list (7b5af1d5...)"
                 " in full; version jv2-v5-4 over jv2-v5-3; the jv2-v5-3 blob is 28638dcf" % pin_v54,
                 pin_v54 == G.REGEX_LIST_SHA256_V54 == R.V5_LIST_SHA and G.V5_VERSION == "jv2-v5-4" and
                 G.regex_list_v54()["base_list"] == F.regex_list() and
                 G.regex_list_v54()["base_regex_list_sha256"] == F.REGEX_LIST_SHA256 == R.V5_BASE_LIST_SHA and
                 git_blob_lf(F.__file__) == G.BASE_BLOB == "28638dcfcd7f464404af6e085d2de99d32ada70d")
        # C-V5-neg, C-V5-neg-2, C-V5-pos under jv2-v5-4, with the failing legs printed
        n4, n42, p4 = G.v5(r1_rubric), G.v5(t7_rubric), G.v5(F.CONTROL_FIT_TEXT)
        ck.check("C-V5-neg (jv2-v5-4): ef9c9e87 FAILS on (a') AND (b)", n4["pass"] is False and n4["a"] is False and
                 n4["b"] is False, G.describe(n4))
        ck.check("C-V5-neg-2 (jv2-v5-4): ace41ede FAILS on (d) AND (f)", n42["pass"] is False and n42["d"] is False and
                 n42["f"] is False, G.describe(n42))
        ck.check("C-V5-pos (jv2-v5-4): CONTROL_FIT_TEXT (a7b8ebb0...) PASSES", p4["pass"] is True and
                 sha256_text(F.CONTROL_FIT_TEXT) == "a7b8ebb0d36b069204703095eb8531a2565bf0e347ccff820bde94c9f590aef0",
                 G.describe(p4))
        # per-text readout on the pinned corpora (the firing pattern per text), with the FP / FN counts per corpus
        tallies = {}

        def _score(corpus, k, t, want_pass):
            r = G.v5(t)
            fp, fn = int(want_pass and not r["pass"]), int((not want_pass) and r["pass"])
            tl = tallies.setdefault(corpus, {"n_fit": 0, "n_unfit": 0, "FP": 0, "FN": 0})
            tl["n_fit" if want_pass else "n_unfit"] += 1
            tl["FP"] += fp
            tl["FN"] += fn
            ck.check("jv2-v5-4 %s %s %s; firing %s" % (corpus, k, "PASSES" if want_pass else "FAILS", G.firing(r)),
                     r["pass"] is want_pass, G.describe(r))
            return r
        for k, t in PROBE_UNFIT.items():
            _score("C-V5-probe", k, t, False)
        for k, t in PROBE_FIT.items():
            _score("C-V5-probe", k, t, True)
        for k, (src, t) in READY_UNFIT.items():
            _score("READY", "%s (%s)" % (k, src), t, False)
        for k, (src, t) in READY_FIT.items():
            _score("READY", "%s (%s)" % (k, src), t, True)
        for k, (src, t) in READY_NEUTRALITY.items():
            _score("READY-neutrality-framed", "%s (%s)" % (k, src), NEUTRALITY_FRAME + t, True)
        _score("B29f", "B29f", B29F, False)
        for k, t in unfit3.items():
            r = _score("C-V5-probe-3", k, t, False)
            ck.check("C-V5-probe-3 %s FAILS on its class leg (%s) itself" % (k, LEG_OF_CLASS[k[0]]),
                     r[LEG_OF_CLASS[k[0]]] is False, G.describe(r))
        _score("C-V5-probe-3", "T7 (ace41ede)", t7_rubric, False)
        for k, t in fit3.items():
            _score("C-V5-probe-3", k, t, True)
        out("[SELFTEST-INDUCE-RUN-3] jv2-v5-4 on the pinned corpora (FP = a fit text failing, FN = an unfit text passing):"
            " %s" % json.dumps(tallies, sort_keys=True))
        ck.check("jv2-v5-4 on the pinned corpora: 0 false positives and 0 false negatives in every corpus",
                 all(v["FP"] == 0 and v["FN"] == 0 for v in tallies.values()) and tallies["C-V5-probe-3"] ==
                 {"n_fit": 13, "n_unfit": 21, "FP": 0, "FN": 0}, json.dumps(tallies, sort_keys=True))
        # jv2-v5-3 on the same new corpora (the relay's claim, NOT RECOMPUTED by the registrar, is executed here)
        v3 = {k: bool(F.v5(t)["pass"]) for k, t in list(unfit3.items()) + [("T7", t7_rubric)] + list(fit3.items())}
        out("[SELFTEST-INDUCE-RUN-3] jv2-v5-3 on the -3 corpora: PASS %s; FAIL %s" % (
            sorted(k for k, v in v3.items() if v), sorted(k for k, v in v3.items() if not v)))
        ck.check("jv2-v5-3 (the -2 screen) passes every fit3 text and T7, and every unfit3 text but E4 (E4 FAILS (c) under"
                 " jv2-v5-3: 'logical errors count against it' names no reasoning noun; the relay's 'all 20 unfit3 texts"
                 " PASS jv2-v5-3' is therefore 19 of 20)", sorted(k for k, v in v3.items() if not v) == ["E4"])
        # the builder's batteries: each sceptic cue alone; each reference cue; the prompt echoes; negations; part isolation
        ck.check("the builder's batteries carry their pinned sha256 %s... (constructed texts, not registered corpora)"
                 % BATTERY_SHA256[:16], battery_sha() == BATTERY_SHA256, battery_sha())
        for name, t in SCEPTIC_FIT.items():
            r = G.v5(t)
            ck.check("battery sceptic %s: PASSES and its ONLY sceptic cue is %s" % (name, name), r["pass"] is True and
                     r["d2_detail"]["sceptic_cues"] == [name], G.describe(r))
        corp = {"fit3": fit3, "probe": PROBE_FIT, "ready": {k: t for k, (_s, t) in READY_FIT.items()}}
        for name, (cname, k) in SCEPTIC_IN_CORPORA.items():
            r = G.v5(corp[cname][k])
            ck.check("sceptic cue %s is the ONLY sceptic cue of the registered text %s %s, which PASSES" % (name, cname, k),
                     r["pass"] is True and r["d2_detail"]["sceptic_cues"] == [name], G.describe(r))
        ck.check("every sceptic cue is isolated by exactly one text (battery or corpus)",
                 sorted(list(SCEPTIC_FIT) + list(SCEPTIC_IN_CORPORA)) == sorted(n for n, _r in G.SCEPTIC_ENTRIES))
        for name, t in list(CUE_FIT.items()) + list(ECHO_FIT.items()) + list(NEG_FIT.items()):
            r = G.v5(t)
            ck.check("battery fit %s PASSES" % name, r["pass"] is True, G.describe(r))
        for name, (t, want) in PART_UNFIT.items():
            r = G.v5(t)
            ck.check("battery unfit %s FAILS with exactly %s" % (name, want), r["pass"] is False and G.firing(r) == want,
                     str(G.firing(r)))
        # the registered sentence S8's own text, as a rubric sentence, fires no (f) pattern (unguarded (f), local adjacency)
        ck.check("(f) is unguarded but reads local adjacency: S8's 'must not reserve TIE for identical responses, must not"
                 " forbid or discourage TIE, and must not default to either response' fires no (f) pattern; 'TIE is a last"
                 " resort' fires, 'TIE is not a last resort' does not; a bare 'TIE only if' without 'identical' does not"
                 " fire; 'otherwise TIE' does not fire", G.v5(named["S8"])["f"] is True and
                 G.v5("TIE is a last resort.")["f"] is False and G.v5("TIE is not a last resort.")["f"] is True and
                 G.v5("TIE only if neither has fewer errors.")["f"] is True and G.v5("Otherwise TIE.")["f"] is True)
        # the jv2-v5-4 suite and its MUTANTS: every new named part removed or switched off, each killed, each sha differs
        suite54 = v54_suite(r1_rubric, t7_rubric, unfit3, fit3)
        ck.check("jv2-v5-4 suite: all %d checks hold under the rule of record" % len(suite54), all(ok for _n, ok in suite54),
                 "; ".join(n for n, ok in suite54 if not ok)[:300])
        m54 = v54_mutants()
        shas = {G.regex_list_v54_sha256(G.regex_list_v54(rules)) for _n, rules in m54}
        for mname, rules in m54:
            killed = [n for n, ok in v54_suite(r1_rubric, t7_rubric, unfit3, fit3, rules) if not ok]
            ck.check("jv2-v5-4 MUTANT KILLED: %s (%d suite check(s) fail under it; its list sha differs from the pin)" % (
                mname, len(killed)), bool(killed) and G.regex_list_v54_sha256(G.regex_list_v54(rules)) !=
                G.REGEX_LIST_SHA256_V54, "; ".join(killed[:3]))
        n_named = (len(G.CUE_REF_ENTRIES) + len(G.D1_ENTRIES) + len(G.SCEPTIC_ENTRIES) + 3 + len(G.F_ENTRIES))
        ck.check("jv2-v5-4 mutant count: %d (5 switches: (a'), (d2), (d1) guard, (e) guard, errors-in exemption; + %d named"
                 " parts: %d reference cues, %d (d1), %d sceptic cues, 3 (e), %d (f)); %d distinct list shas" % (
                     len(m54), n_named, len(G.CUE_REF_ENTRIES), len(G.D1_ENTRIES), len(G.SCEPTIC_ENTRIES),
                     len(G.F_ENTRIES), len(shas)), len(m54) == 5 + n_named and len(shas) == len(m54) and
                 G.REGEX_LIST_SHA256_V54 not in shas, str(len(m54)))
        ck.refused("build_rules_v54 refuses an unknown part name (a mutant cannot silently remove nothing)", lambda:
                   G.build_rules_v54(drop_f=("no_such_part",)), ("unknown part",))
        # classify: V5 is a formal failure (FITNESS) after the -1 classes; a fit rubric is VALID
        ck.check("classify (jv2-v5-4): a format rubric (the -1 rubric) is FITNESS; a rubric naming no correctness is FITNESS;"
                 " the control text is VALID; the -2 rubric (T7) and every unfit3 text are FITNESS; every fit3 text is VALID", R.classify(json.dumps({"rubric": r1_rubric}), "stop", [])[0] == "FITNESS" and
                 R.classify(json.dumps({"rubric": NO_CORRECTNESS}), "stop", [])[0] == "FITNESS" and
                 R.classify(json.dumps({"rubric": NO_REASONING}), "stop", [])[0] == "FITNESS" and
                 R.classify(json.dumps({"rubric": F.CONTROL_FIT_TEXT}), "stop", []) == (None, F.CONTROL_FIT_TEXT) and
                 R.classify(json.dumps({"rubric": t7_rubric}), "stop", [])[0] == "FITNESS" and
                 all(R.classify(json.dumps({"rubric": t}), "stop", [])[0] == "FITNESS" for t in unfit3.values()) and
                 all(R.classify(json.dumps({"rubric": t}), "stop", []) == (None, t) for t in fit3.values()))
        # the selection pin (the registered seed must reproduce the selection of record; a DEV seed is not pinned)
        good_rec = {"input_variant_ids_sha256": R.SELECTION_SORTED_SHA, "input_variant_ids_ordered_sha256":
                    R.SELECTION_ORDERED_SHA}
        ck.check("selection pin: the pinned shas are INDUCE-RUBRIC-1's (99484486... / 89bed256...) and a record carrying"
                 " them passes under the registration", R.SELECTION_SORTED_SHA.startswith("99484486d75774b3") and
                 R.SELECTION_ORDERED_SHA.startswith("89bed2562c1f8575") and
                 R.check_selection_pin(good_rec, R.SELECT_REGISTRATION, out=lambda s: None) is True)
        ck.refused("selection pin: a different selection under the registration is a FAILED PRECONDITION", lambda:
                   R.check_selection_pin(dict(good_rec, input_variant_ids_sha256="0" * 64), R.SELECT_REGISTRATION,
                                         out=lambda s: None), ("FAILED PRECONDITION",))
        # the -2 cache admits FITNESS; the -1 cache schema (unchanged) does not
        fx = {}
        for nm, mod in (("-1", IC1), ("-2", IC2), ("-3", IC)):
            cpath = os.path.join(tmp, "fitness_class%s.db" % nm)
            cc = mod.create(cpath, {"registration": "selftest"})
            try:
                cc.execute("INSERT INTO invocation VALUES (1,'t','s','PENDING')")
                cc.execute("INSERT INTO attempt (attempt_no, invocation_seq, posted_at, committed_at, payload_sha256,"
                           " body_zlib, failure_class) VALUES (1, 1, 't', 't', 's', x'00', 'FITNESS')")
                cc.commit()
                fx[nm] = "ACCEPTED"
            except sqlite3.DatabaseError:
                cc.rollback()
                fx[nm] = "REFUSED"
            finally:
                cc.close()
        ck.check("the -3 attempt cache: the -2 DDL with ZERO substitutions (it admits FITNESS; the -1 schema refuses it);"
                 " schema id archv2-induce-rubric-3-cache-v1, differing from the -1 and -2 ids",
                 fx == {"-1": "REFUSED", "-2": "ACCEPTED", "-3": "ACCEPTED"} and IC.DDL == IC2.DDL and
                 IC.SCHEMA_ID == "archv2-induce-rubric-3-cache-v1" and IC.SCHEMA_ID not in (IC1.SCHEMA_ID, IC2.SCHEMA_ID)
                 and IC.DDL.replace(",'FITNESS'", "") == IC1.DDL, json.dumps(fx))
        ck.refused("a -2 attempt cache is not reopened as a -3 one", lambda: IC.reopen(os.path.join(tmp,
                                                                                                     "fitness_class-2.db")),
                   ("not an ARCH-V2-INDUCE-RUBRIC-3",))
        ck.refused("a -1 attempt cache is not reopened as a -3 one", lambda: IC.reopen(os.path.join(tmp,
                                                                                                     "fitness_class-1.db")),
                   ("not an ARCH-V2-INDUCE-RUBRIC-3",))
        # the dry-run
        p0 = paths_for(tmp, gen, ev, "dry")
        reset_flag()
        lines = []
        d1 = R.dry_run(p0, DEV_SEED, None, gen_sha, eval_sha, out=lines.append)
        reset_flag()
        d2 = R.dry_run(p0, DEV_SEED, None, gen_sha, eval_sha, out=lambda s: None)
        body = json.loads(d1["body"].decode("utf-8"))
        ck.check("dry-run: the payload sha is stable, the body is model / max_tokens / messages (no temperature), cap 8192,"
                 " the v2 judge", d1["payload_sha256"] == d2["payload_sha256"] and list(body) == ["model", "max_tokens",
                 "messages"] and body["max_tokens"] == 8192 and body["model"] == "grok-4-1-fast-non-reasoning" and
                 body["messages"][0]["content"] == I.INDUCTION_SYSTEM, d1["payload_sha256"])
        ck.check("dry-run: 40 TRAIN inputs; GATE refused and counted (> 0); the ids and their shas printed; posts nothing",
                 d1["ids"]["n"] == 40 and d1["witness"]["gate_excluded"] > 0 and not os.path.exists(p0.out) and
                 has(lines, "sorted-set sha256") and has(lines, "GATE"), json.dumps(d1["witness"]))
        _old, new_ref = T.reference_selections(gen, DEV_SEED, population=R.POPULATION, exclude=ex_ids)
        _o2, unex_ref = T.reference_selections(gen, DEV_SEED, population=R.POPULATION)
        ck.check("D1: excluded inputs are REPLACED in sort order (40 inputs; none excluded; kept + replaced = 40, replaced >"
                 " 0); the witness and the disclosure print kept / replaced / last rank", len(d1["ids"]["input_variant_ids"])
                 == 40 and not (set(d1["ids"]["input_variant_ids"]) & ex_ids) and d1["witness"]["replaced"] > 0 and
                 d1["witness"]["kept_from_unexcluded"] + d1["witness"]["replaced"] == 40 and
                 d1["witness"]["kept_from_unexcluded"] == len(set(unex_ref) & set(new_ref)) and
                 has(lines, "inputs sharing >= 8 consecutive tokens") and has(lines, "last rank"),
                 json.dumps({k: d1["witness"].get(k) for k in ("kept_from_unexcluded", "replaced", "last_rank")}))
        ck.check("dry-run: the selection equals the ruled rule re-derived independently (distinct variants, first per"
                 " component); the witness counts equal the fixture's", d1["ids"]["input_variant_ids"] == new_ref and
                 d1["witness"]["distinct_variants"] == T.reference_selections.distinct and
                 d1["witness"]["candidate_rows"] == T.reference_selections.rows, json.dumps(d1["witness"], sort_keys=True))
        ck.check("dry-run: V2's EVAL key material is built from the eval_view (key renderings > 0)",
                 d1["material_sizes"][0] > 0, str(d1["material_sizes"]))
        # the payload sha is registered: a different expected sha refuses before anything is written or posted
        pX = paths_for(tmp, gen, ev, "wrongsha")
        reset_flag()
        sX = Stub([GOOD])
        ck.refused("--expect-payload-sha differs from the built body", lambda: R.run(
            sX, "0" * 64, pX, DEV_SEED, None, gen_sha, eval_sha, out=lambda s: None), ("not the registered",))
        ck.check("... with ZERO posts and no cache created", not sX.calls and not os.path.exists(pX.cache))
        # A. the first attempt is valid: ONE post, the artefact of record, P1 HELD, P2 HELD, falsifier NOT FIRED
        led = ledger_fixture(os.path.join(tmp, "ledger"))
        events = []
        real_open_eval = R.dv2views.open_eval

        def spy_open_eval(*a, **k):
            events.append("open_eval")
            return real_open_eval(*a, **k)

        class SpyStub(Stub):
            def __call__(self, system, user):
                events.append("call")
                return Stub.__call__(self, system, user)
        pA = paths_for(tmp, gen, ev, "A")
        reset_flag()
        expA = R.dry_run(pA, DEV_SEED, None, gen_sha, eval_sha, out=lambda s: None)["payload_sha256"]
        reset_flag()
        sA = SpyStub([GOOD, GOOD2, GOOD2])
        R.dv2views.open_eval = spy_open_eval
        try:
            rA = R.run(sA, expA, pA, DEV_SEED, None, gen_sha, eval_sha, ledger_dir=led, atl=atl, out=lambda s: None)
        finally:
            R.dv2views.open_eval = real_open_eval
        ck.check("A: the run process opens eval_view only AFTER its call (the D1 list replaces any earlier read)",
                 events and events[0] == "call" and events.count("open_eval") == 1, str(events))
        L = rA["outcome_lines"]
        ck.check("A: a valid first reply is posted ONCE (no best-of-n, no retry on a valid reply)", len(sA.calls) == 1,
                 "posts %d" % len(sA.calls))
        ck.check("A: V1-V5 PASS, the artefact of record written (mode x) and loadable; P1 HELD, P2 HELD, falsifier NOT FIRED",
                 all(rA["validity"][k] is True for k in ("V1", "V2", "V3", "V4", "V5")) and os.path.exists(pA.artefact) and
                 has(L, "V5 FITNESS on the reply of record (regex list sha256 %s): PASS" % R.V5_LIST_SHA) and
                 has(L, "ARTEFACT OF RECORD: YES") and has(L, "P1 (the first attempt is valid, V5 included; point probability 0.70): HELD")
                 and has(L, "P2 (V1-V5 pass; point probability 0.85): HELD") and has(L, "FALSIFIER (three formal failures): NOT FIRED"), "\n".join(L[-8:]))
        art = json.load(open(pA.artefact, encoding="utf-8"))
        ids = json.load(open(pA.ids, encoding="utf-8"))
        ck.check("A: the artefact is the first reply's rubric, carries the attempt of record and the input ids' sha; the ids"
                 " file holds 40 ordered ids", art["rubric"] == json.loads(GOOD)["rubric"] and
                 art["manifest"]["model"]["attempt_of_record"] == 1 and
                 art["manifest"]["input_variant_ids_sha256"] == ids["input_variant_ids_sha256"] and
                 len(ids["input_variant_ids"]) == 40 and has(L, "artefact_sha256 %s" % art["artefact_sha256"]))
        rows = json.load(open(atl.day_ledger_path(led), encoding="utf-8"))
        ck.check("A: the day ledger got the posted count (1) for %s" % R.TEST, rows[-1]["test"] == R.TEST and
                 rows[-1]["calls"] == 1, str(rows[-1]))
        ck.check("A: V2 ORDER witnessed: the reply's commit time precedes the eval_view open time, both printed with the"
                 " eval_view sha (from the manifest / the pin)", rA["order"] is not None and rA["order"][0] < rA["order"][1]
                 and has(L, "V2 order witness") and has(L, eval_sha), str(rA["order"]))
        c = _ro(pA.cache)
        try:
            ev_seq = [w for (w,) in c.execute("SELECT what FROM event ORDER BY seq")]
        finally:
            c.close()
        ck.check("A: the cache's event log orders launch < reply_committed < eval_view_opened",
                 ev_seq == ["launch", "reply_committed", "eval_view_opened"], str(ev_seq))
        ck.check("A: the outcome carries the disclosures of record (the -3 registration's 1-5; carried: finding 1, C4"
                 " population, C5 dry-run eval_view, D1 exclusion; the stage 'judge' line), the instrument pins, P3 NOT"
                 " SCORED (the post-run reading), the CHECKLIST line and the FALLBACK line",
                 all(has(L, "DISCLOSURE (the -3 registration): %s" % d) for d in R.DISCLOSURES_RULING) and
                 has(L, "selection corrected before the first call") and has(L, "population narrowed to the judged corpus")
                 and has(L, "the dry-run process opened eval_view") and has(L, "inputs sharing >= 8 consecutive tokens")
                 and has(L, "DISCLOSURE (deviation): " + R.DISCLOSURE_STAGE) and has(L, R.SYSTEM_SHA) and
                 has(L, "V5 SCOPE (F1b change 7, carried): " + R.V5_SCOPE) and has(L, "CHECKLIST: " + R.CHECKLIST) and
                 has(L, "FALLBACK: " + R.FALLBACK) and has(L, "P3 (the checklist reads FIT in both readings; point"
                                                           " probability 0.55): NOT SCORED BY THIS INSTRUMENT (scored by the"
                                                           " post-run reading of the artefact of record)") and
                 has(L, R.USER_TEMPLATE_SHA) and has(L, R.V5_LIST_SHA))
        ck.check("A: the artefact is labelled 'MCQ rubric, population mmlu-pro-v2 TRAIN' and its manifest records the"
                 " population filter", art["manifest"]["artefact_label"] == R.ARTEFACT_LABEL and
                 art["manifest"]["population"] == {"contracts": ["MC_LETTER"], "corpus_version": "mmlu-pro-v2"})
        c = _ro(pA.cache)
        try:
            n_inv = c.execute("SELECT COUNT(*) FROM invocation").fetchone()[0]
            n_led = atl.ledger_calls(R.TEST, led)
        finally:
            c.close()
        ck.check("A: write-ahead: one invocation row for the one post, and the day ledgers equal it", n_inv == 1 and
                 n_led == 1, "invocations %d, ledger %d" % (n_inv, n_led))
        reset_flag()
        ck.refused("A: a second launch on the same outputs (the run reached its outcome; write-once)", lambda: R.run(
            Stub([GOOD]), rA["valid"]["payload_sha256"], pA, DEV_SEED, None, gen_sha, eval_sha, out=lambda s: None),
            ("reached its outcome",))
        # B. a fenced (non-JSON) reply is a formal failure, never edited; the SAME body is re-posted; attempt 2 is of record
        fenced = "```json\n" + GOOD + "\n```"
        pB, sB, rB = launch(ck, tmp, gen, ev, "B", [fenced, GOOD2, GOOD], gen_sha, eval_sha)
        L = rB["outcome_lines"]
        ck.check("B: a fenced JSON reply is NON_JSON (no repair / edit path); the SAME body re-posted; attempt 2 of record;"
                 " P1 FAILED, P2 HELD", len(sB.calls) == 2 and sB.calls[0] == sB.calls[1] and
                 [r["failure_class"] for r in rB["rows"]] == ["NON_JSON", None] and rB["valid"]["attempt_no"] == 2 and
                 json.load(open(pB.artefact, encoding="utf-8"))["rubric"] == json.loads(GOOD2)["rubric"] and
                 has(L, "): FAILED") and has(L, "P2 (V1-V5 pass; point probability 0.85): HELD"), str([r["failure_class"] for r in rB["rows"]]))
        # C. three formal failures: UNDETERMINED, no 4th attempt, no artefact, the falsifier FIRED
        bad_key = json.dumps({"system_prompt": "x", "rubric": "y"})
        pC, sC, rC = launch(ck, tmp, gen, ev, "C", [(bad_key, "stop"), ("{\"rubric\": \"cut", "length"),
                                                    ("", "content_filter"), (GOOD, "stop")], gen_sha, eval_sha)
        L = rC["outcome_lines"]
        ck.check("C: KEY, LENGTH, CONTENT_FILTER classified; exactly 3 posts of the same body (no 4th); UNDETERMINED; no"
                 " artefact; P1 FAILED, P2 NOT SCORED, P3 NOT SCORED (no artefact), falsifier FIRED, the FALLBACK named",
                 [r["failure_class"] for r in rC["rows"]] == ["KEY", "LENGTH", "CONTENT_FILTER"] and len(sC.calls) == 3 and
                 len(set(sC.calls)) == 1 and not os.path.exists(pC.artefact) and has(L, "UNDETERMINED") and
                 has(L, "ARTEFACT OF RECORD: NO") and has(L, "P2 (V1-V5 pass; point probability 0.85): NOT SCORED") and
                 has(L, "FALSIFIER (three formal failures): FIRED") and has(L, "slot takes the FALLBACK") and
                 has(L, "UNDETERMINED: three formal failures; the slot takes the FALLBACK (GENERIC_RUBRIC, sha256 %s"
                     % R.GENERIC_RUBRIC_SHA256) and has(L, "FALLBACK: " + R.FALLBACK) and
                 has(L, "NOT SCORED BY THIS INSTRUMENT (no artefact of record: the reading does not take place; the"
                        " FALLBACK applies)") and
                 has(L, "V5 FITNESS on the reply of record (regex list sha256 %s): NOT RUN" % R.V5_LIST_SHA),
                 str([r["failure_class"] for r in rC["rows"]]))
        # V5-A. a FORMAT rubric (the INDUCE-RUBRIC-1 rubric of record) is the formal failure FITNESS: disclosed with its
        # matching patterns; the SAME body re-posted; attempt 2 (a fit rubric) of record; P1 FAILED, P2 HELD
        fmt = json.dumps({"rubric": r1_rubric})
        linesF = []
        pV, sV, rV = launch(ck, tmp, gen, ev, "V5A", [fmt, GOOD], gen_sha, eval_sha, out=linesF.append)
        L = rV["outcome_lines"]
        cV = _ro(pV.cache)
        try:
            evV = [d for (d,) in cV.execute("SELECT detail FROM event WHERE what='attempt_committed'")]
            clsV = [c for (c,) in cV.execute("SELECT failure_class FROM attempt ORDER BY attempt_no")]
        finally:
            cV.close()
        ck.check("V5-A: the format rubric is FITNESS (a formal failure, attempt consumed, cached as such); the SAME body is"
                 " re-posted; attempt 2 of record; the matching patterns are printed, in the event log and in outcome.txt;"
                 " P1 FAILED, P2 HELD", [r["failure_class"] for r in rV["rows"]] == ["FITNESS", None] and clsV ==
                 ["FITNESS", None] and len(sV.calls) == 2 and sV.calls[0] == sV.calls[1] and rV["valid"]["attempt_no"] == 2
                 and has(linesF, "-> FITNESS | V5 FAIL") and evV and "a_to_z" in evV[0] and
                 has(L, "attempt 1 V5 FAIL") and has(L, "a_to_z") and has(L, "attempt 2 V5 PASS") and
                 has(L, "P1 (the first attempt is valid, V5 included; point probability 0.70): FAILED") and
                 has(L, "P2 (V1-V5 pass; point probability 0.85): HELD") and has(L, "ARTEFACT OF RECORD: YES"), " / ".join(evV))
        # V5-B. three FITNESS failures: UNDETERMINED; no 4th attempt; no artefact; the falsifier FIRED
        pW, sW, rW = launch(ck, tmp, gen, ev, "V5B", [fmt, json.dumps({"rubric": NO_CORRECTNESS}), fmt, GOOD], gen_sha,
                            eval_sha)
        L = rW["outcome_lines"]
        ck.check("V5-B: three V5 failures are three formal failures: exactly 3 posts; UNDETERMINED; no artefact; P1 FAILED,"
                 " P2 NOT SCORED, falsifier FIRED (the slot takes the FALLBACK)",
                 [r["failure_class"] for r in rW["rows"]] == ["FITNESS"] * 3 and len(sW.calls) == 3 and
                 not os.path.exists(pW.artefact) and has(L, "UNDETERMINED: three formal failures") and
                 has(L, "P2 (V1-V5 pass; point probability 0.85): NOT SCORED") and has(L, "FALSIFIER (three formal failures): FIRED") and
                 has(L, "(a') final-answer correctness named outside a reference-agreement clause NO") and
                 has(L, "slot takes the FALLBACK"), str([r["failure_class"] for r in rW["rows"]]))
        # the V5 FAIL print branch on the reply of record (unreachable through classify, which refuses such a reply
        # first): executed through outcome_lines directly
        vF = {"V1": True, "V2": True, "V3": True, "V4": False, "V5": False}
        rowF = [{"attempt_no": 1, "finish_reason": "stop", "response_id": "r", "reply_sha256": "0" * 64,
                 "failure_class": None, "reply_text": fmt}]
        LF = R.outcome_lines(rowF, rowF[0], [], vF, None, [], json.load(open(pA.ids, encoding="utf-8")),
                             rA["artefact"]["manifest"]["train_only_witness"], {"eval_hits": 0, "not_gen_side": 0}, None,
                             eval_sha, G.v5(r1_rubric))
        ck.check("the V5 FAIL branch on a reply of record prints FAIL with the patterns, ARTEFACT OF RECORD NO, P2 FAILED",
                 has(LF, "V5 FITNESS on the reply of record (regex list sha256 %s): FAIL" % R.V5_LIST_SHA) and
                 has(LF, "no_other_text") and has(LF, "ARTEFACT OF RECORD: NO") and has(LF, "P2 (V1-V5 pass; point probability 0.85): FAILED"))
        # D. V2: a valid reply that carries EVAL key material is NOT of record (no re-post: V2 is not a formal failure)
        e = dv2views.open_eval("judge", ev)     # the fixture's eval_view (stage-gated opener)
        try:
            at = e.execute("SELECT answer_text FROM response WHERE answer_text IS NOT NULL ORDER BY response_id LIMIT 1"
                           ).fetchone()[0]
        finally:
            e.close()
        leaky = json.dumps({"rubric": "1. Correct final answers win.\n2. Remember answer_text: %s\n3. Otherwise the"
                                      " sounder reasoning wins, else TIE." % at})     # passes V5 (F1b (c)): V2 decides
        linesD = []
        pD, sD, rD = launch(ck, tmp, gen, ev, "D", [leaky, GOOD], gen_sha, eval_sha, out=linesD.append)
        L = rD["outcome_lines"]
        ck.check("D: V2 failure is announced as NEVER a re-post (finding 3 (ii)), with one post only",
                 has(linesD, "NEVER a re-post") and len(sD.calls) == 1)
        ck.check("D: V2 FAILS on EVAL key material (%r); NO artefact of record; no re-post; P1 HELD, P2 FAILED; the FALLBACK"
                 " line (outcome and run print)" % at,
                 rD["validity"]["V2"] is False and bool(rD["hits"]) and not os.path.exists(pD.artefact) and
                 len(sD.calls) == 1 and has(L, "ARTEFACT OF RECORD: NO") and has(L, "P2 (V1-V5 pass; point probability 0.85): FAILED") and
                 has(L, "V2 leak check against EVAL key material: FAIL") and
                 has(L, "V2 FAILED: the artefact is NOT OF RECORD") and
                 has(L, "the slot takes the FALLBACK (GENERIC_RUBRIC, sha256 %s)" % R.GENERIC_RUBRIC_SHA256) and
                 has(linesD, "the slot takes the FALLBACK: " + R.FALLBACK), str(rD["hits"][:3]))
        mat = {"forms": set(), "texts": {"a long eval answer text"}}
        refs, rc = R.reference_material(dv2views.open_eval("judge", ev))
        ck.check("V2 reference leg (C2): the fixture's EVAL reference rows are rendered in their solver's ordering and"
                 " counted", rc["reference_rows"] > 0 and rc["rendered"] > 0, json.dumps(rc, sort_keys=True))
        mat_r = {"forms": set(), "texts": set(), "refs": {"(c) a long reference option text"}}
        ck.check("V2 reference leg (C2): a rubric carrying an EVAL reference rendering is a hit; a clean one is not",
                 R.leak_check("Use (C) a long reference option text as a model.", mat_r) == ["reference:(c) a long"
                                                                                            " reference option text"]
                 and R.leak_check("Prefer correct.", mat_r) == [])
        ck.check("V2 unit: a raw EVAL answer text of >= 12 characters is a hit; a clean rubric is not",
                 R.leak_check("Prefer A LONG  eval answer text.", mat) != [] and R.leak_check("Prefer correct.", mat) == [])
        # E. a transport error stops the launch fail-closed (logged, not an attempt, on the ledger); the relaunch re-posts the
        # IDENTICAL body and completes; the outcome discloses the error beside the attempts
        led2 = ledger_fixture(os.path.join(tmp, "ledger2"))
        expE = None
        pE, sE, rE = launch(ck, tmp, gen, ev, "E", [ConnectionError("reset by peer")], gen_sha, eval_sha, ledger=led2)
        c = _ro(pE.cache)
        try:
            trow = c.execute("SELECT seq, exception_class, message, payload_sha256, note FROM transport").fetchall()
            n_att = c.execute("SELECT COUNT(*) FROM attempt").fetchone()[0]
            expE = c.execute("SELECT value FROM meta WHERE key='payload_sha256'").fetchone()[0]
        finally:
            c.close()
        ck.check("E: a transport error STOPS the launch (no attempt consumed; logged with class, message, payload sha and"
                 " 'TRANSPORT, no reply'); no outcome yet; transport_stop_1.txt written; the call is on the day ledger",
                 rE["stopped"] and n_att == 0 and trow == [(1, "ConnectionError", "reset by peer", expE,
                                                            "TRANSPORT, no reply")] and not os.path.exists(pE.outcome) and
                 os.path.exists(os.path.join(pE.out, "transport_stop_1.txt")) and
                 json.load(open(atl.day_ledger_path(led2), encoding="utf-8"))[-1]["calls"] == 1, str(trow))
        reset_flag()
        sE2 = Stub([GOOD])
        rE2 = R.run(sE2, expE, pE, DEV_SEED, None, gen_sha, eval_sha, ledger_dir=led2, atl=atl, out=lambda s: None)
        L = rE2["outcome_lines"]
        ck.check("E: the relaunch re-posts the IDENTICAL body (same payload sha), the shared guard's (i) is read per kind"
                 " (1 transport + 3 planned passes), attempt 1 is valid, and the outcome discloses the transport error",
                 sE2.calls == [expE] and rE2["valid"] is not None and rE2["valid"]["attempt_no"] == 1 and
                 has(L, "transport error 1") and has(L, "ARTEFACT OF RECORD: YES") and
                 json.load(open(atl.day_ledger_path(led2), encoding="utf-8"))[-1]["calls"] == 1, "\n".join(L[:5]))
        # F. three transport errors: UNDETERMINED BY INSTRUMENT (the falsifier does not fire); a 4th launch is refused
        pF = paths_for(tmp, gen, ev, "F")
        reset_flag()
        expF = R.dry_run(pF, DEV_SEED, None, gen_sha, eval_sha, out=lambda s: None)["payload_sha256"]
        outs = []
        for k in range(3):
            reset_flag()
            outs.append(R.run(Stub([TimeoutError("timeout %d" % k)]), expF, pF, DEV_SEED, None, gen_sha, eval_sha,
                              out=lambda s: None))
        L = outs[-1]["outcome_lines"]
        ck.check("F: the 3rd transport error reads UNDETERMINED BY INSTRUMENT (outcome written; P1 / P2 NOT SCORED; the"
                 " falsifier NOT FIRED)", outs[0]["stopped"] and outs[1]["stopped"] and os.path.exists(pF.outcome) and
                 has(L, "UNDETERMINED BY INSTRUMENT") and has(L, "NOT FIRED (UNDETERMINED BY INSTRUMENT does not fire it)")
                 and has(L, "P1 (the first attempt is valid, V5 included; point probability 0.70): NOT SCORED"), "\n".join(L[:6]))
        reset_flag()
        ck.refused("F: a 4th launch after UNDETERMINED BY INSTRUMENT", lambda: R.run(
            Stub([GOOD]), expF, pF, DEV_SEED, None, gen_sha, eval_sha, out=lambda s: None), ("reached its outcome",))
        # G2. a relaunch whose body differs from the first launch's is refused (the identical body, asserted)
        pR = paths_for(tmp, gen, ev, "R")
        reset_flag()
        expR = R.dry_run(pR, DEV_SEED, None, gen_sha, eval_sha, out=lambda s: None)["payload_sha256"]
        reset_flag()
        R.run(Stub([ConnectionError("x")]), expR, pR, DEV_SEED, None, gen_sha, eval_sha, out=lambda s: None)
        real_bp = I.build_prompt
        I.build_prompt = lambda ct, inputs: (real_bp(ct, inputs)[0], real_bp(ct, inputs)[1] + " ")
        try:
            reset_flag()
            new_sha = R.build_payload(json.load(open(pR.ids, encoding="utf-8")) and
                                      R.select(gen, gen_sha, DEV_SEED, None, out=lambda s: None,
                                               excl=OA.load(EXCL["path"], R.EXCL_SHA, eval_sha, gen_sha))[0])[3]
            sR = Stub([GOOD])
            ck.refused("a relaunch with a different body (even with a matching --expect-payload-sha)", lambda: R.run(
                sR, new_sha, pR, DEV_SEED, None, gen_sha, eval_sha, out=lambda s: None), ("IDENTICAL body",))
            ck.check("... with ZERO posts", not sR.calls)
        finally:
            I.build_prompt = real_bp
        # the V2 order check itself: a clock that does not advance makes the open time NOT after the commit time -> refused
        real_now = R._now
        R._now = lambda: "2026-09-24T00:00:00.000000Z"
        try:
            pO = paths_for(tmp, gen, ev, "O")
            reset_flag()
            expO = R.dry_run(pO, DEV_SEED, None, gen_sha, eval_sha, out=lambda s: None)["payload_sha256"]
            reset_flag()
            ck.refused("V2 order: an eval_view open time not after the reply's commit time is refused", lambda: R.run(
                Stub([GOOD]), expO, pO, DEV_SEED, None, gen_sha, eval_sha, out=lambda s: None), ("V2 order",))
        finally:
            R._now = real_now
            reset_flag()
        # the flag: no call_judge_full after the eval_view open in this process (finding 3 (i))
        R._EVAL_OPENED["at"] = "2026-09-24T00:00:00Z"
        sF = Stub([GOOD])
        try:
            ck.refused("a call_judge_full invocation after eval_view was opened", lambda: R.guarded(sF)("s", "u"),
                       ("AFTER eval_view was opened",))
            ck.check("... the stub was never called", not sF.calls)
        finally:
            reset_flag()
        # classify: every formal failure class, and VERBATIM
        long_stem = "the quick brown fox jumps over the lazy dog near the river bank today"
        chosen = [{"stem": long_stem, "options": []}]
        cls = [R.classify("not json", "stop", chosen)[0], R.classify(json.dumps({"rubric": ""}), "stop", chosen)[0],
               R.classify(json.dumps({"rubric": "x", "extra": 1}), "stop", chosen)[0], R.classify(GOOD, "length", chosen)[0],
               R.classify("", "content_filter", chosen)[0],
               R.classify(json.dumps({"rubric": "Prefer: " + long_stem}), "stop", chosen)[0],
               R.classify(GOOD, "stop", chosen)[0]]
        ck.check("classify: NON_JSON, KEY (empty), KEY (extra key), LENGTH, CONTENT_FILTER, VERBATIM, VALID",
                 cls == ["NON_JSON", "KEY", "KEY", "LENGTH", "CONTENT_FILTER", "VERBATIM", None], str(cls))
        # the attempt cache is append-only; the INVOCATION row (written before the post) is refused after a valid reply,
        # and a reply / transport row must resolve an unresolved invocation
        c = sqlite3.connect(pB.cache)
        res = {}
        for name, sql in (("UPDATE", "UPDATE attempt SET failure_class='KEY' WHERE attempt_no=2"),
                          ("DELETE", "DELETE FROM attempt WHERE attempt_no=1"),
                          ("invocation after valid", "INSERT INTO invocation VALUES (3,'t','s','PENDING')"),
                          ("attempt without an unresolved invocation", "INSERT INTO attempt (attempt_no, invocation_seq,"
                           " posted_at, committed_at, payload_sha256, body_zlib) VALUES (3, 1,'t','t','s',x'00')"),
                          ("transport without an unresolved invocation", "INSERT INTO transport VALUES (1, 2,'t','s','X','m',"
                           "'TRANSPORT, no reply')")):
            try:
                c.execute(sql)
                c.commit()
                res[name] = "ACCEPTED"
            except sqlite3.DatabaseError as e2:
                c.rollback()
                res[name] = "REFUSED"
        c.close()
        ck.check("the attempt cache: UPDATE, DELETE, an invocation after the valid reply, and reply / transport rows that"
                 " resolve nothing all ABORT",
                 all(v == "REFUSED" for v in res.values()), json.dumps(res))
        # a non-TRAIN input reaching the selection is refused by the content-key leg before any post
        gi = [r for r in T.gen_items(gen) if r[5] == "GATE" and r[4] == "MC_LETTER"]
        real_sel = I.select_inputs
        I.select_inputs = lambda conn, ct, n, seed, sides=I.DEFAULT_SIDES, witness=None, population=None, exclude=None: \
            [T._as_input(gi[0][:5])] * 40
        try:
            pG = paths_for(tmp, gen, ev, "G")
            reset_flag()
            sG = Stub([GOOD])
            ck.refused("a GATE input reaching the selection (select_inputs replaced) refuses before any post", lambda:
                       R.run(sG, "0" * 64, pG, DEV_SEED, None, gen_sha, eval_sha, out=lambda s: None),
                       ("not generation-side",))
            ck.check("... with ZERO posts", not sG.calls)
        finally:
            I.select_inputs = real_sel
        # the backstop: a selection repeating a variant (item, component) is refused by the run AND the dry-run
        real_sel = I.select_inputs
        rows40 = [T._as_input(r[:5]) for r in T.gen_items(gen) if r[5] == "TRAIN" and r[4] == "MC_LETTER" and
                  r[0] not in ex_ids][:20]
        def _dup_sel(conn, ct, n, seed, sides=I.DEFAULT_SIDES, witness=None, population=None, exclude=None):
            # reviewer fix (READY_induce_rubric_1): fill the witness exactly as the real selection does, so the ONLY
            # thing that can stop this run is the distinct-variant / item / component backstop (IR10r)
            real_sel(conn, ct, n, seed, sides, witness, population, exclude)
            return (rows40 + rows40)[:40]
        I.select_inputs = _dup_sel
        try:
            pH = paths_for(tmp, gen, ev, "H")
            reset_flag()
            sH = Stub([GOOD])
            ck.refused("a selection with repeated variants refuses the run before any post", lambda: R.run(
                sH, "0" * 64, pH, DEV_SEED, None, gen_sha, eval_sha, out=lambda s: None), ("40 distinct components",))
            ck.refused("... and the dry-run", lambda: R.dry_run(paths_for(tmp, gen, ev, "Hdry"), DEV_SEED, None, gen_sha,
                                                                eval_sha, out=lambda s: None), ("40 distinct components",))
            ck.check("... with ZERO posts", not sH.calls)
        finally:
            I.select_inputs = real_sel
            reset_flag()
        ck.check("the fixture's own selection: 40 distinct variants; the witness prints candidate rows, distinct variants,"
                 " duplicates collapsed and variants skipped by component",
                 len(set(d1["ids"]["input_variant_ids"])) == 40 and all(k in d1["witness"] for k in (
                     "candidate_rows", "distinct_variants", "duplicates_collapsed", "skipped_by_component")) and
                 has(lines, "variants skipped by component"), json.dumps(d1["witness"], sort_keys=True))
        # C4 unit: the population filter keeps ONLY mmlu-pro-v2 x MC_LETTER rows and counts the rest by (corpus, contract)
        mu = sqlite3.connect(os.path.join(tmp, "population_unit.db"))    # a NEW scratch file under the temp dir
        mu.executescript("CREATE TABLE side (item_id TEXT, side TEXT, component_id TEXT);"
                         "CREATE TABLE variant (corpus_version TEXT, variant_id TEXT, item_id TEXT, stem TEXT,"
                         " options_sorted_json TEXT, contract_id TEXT);"
                         "INSERT INTO side VALUES ('i:a','TRAIN','c:a'), ('i:b','TRAIN','c:b'), ('i:c','TRAIN','c:c');"
                         "INSERT INTO variant VALUES ('mmlu-pro-v2','v:a','i:a','A?','[\"x\"]','MC_LETTER'),"
                         " ('mmlu-pro-v2','v:b','i:b','B?','[\"y\"]','IMPORTED:acc_norm'),"
                         " ('mc6-2026-09-11','v:c','i:c','C?','[\"z\"]','MC_LETTER');")
        wu = {}
        su = I.select_inputs(mu, "mcq", 3, DEV_SEED, witness=wu, population=R.POPULATION)
        mu.close()
        ck.check("C4 unit: the population keeps only mmlu-pro-v2 MC_LETTER (1 of 3 rows) and counts the excluded rows by"
                 " corpus and contract", [r["variant_id"] for r in su] == ["v:a"] and wu["excluded_by_population"] ==
                 {"mc6-2026-09-11 MC_LETTER": 1, "mmlu-pro-v2 IMPORTED:acc_norm": 1}, json.dumps(wu, sort_keys=True))
        # the accounting guard: the ceiling of record is 6 (ruling 1 (a)); a launch that would pass it is refused
        ck.check("the accounting ceiling of %s is 6 (3 attempts + 3 transport errors)" % R.TEST,
                 atl.CEILINGS.get(R.TEST) == 6)
        led3 = ledger_fixture(os.path.join(tmp, "ledger3"))
        atl.append(R.TEST, "--run --go", 4, led3)
        ck.refused("the accounting guard refuses a launch whose 3 planned calls would pass the ceiling (4 already posted)",
                   lambda: atl.guard(R.TEST, 3, {}, led3, "selftest"), ("(i)",))
        # C1 witnesses
        # L1: the day ledger already holds 3 invocations but the cache is fresh (lost / moved): REFUSED, 0 posts
        led4 = ledger_fixture(os.path.join(tmp, "ledger4"))
        atl.append(R.TEST, "--run --go", 3, led4)
        pL1 = paths_for(tmp, gen, ev, "L1")
        reset_flag()
        expL = R.dry_run(pL1, DEV_SEED, None, gen_sha, eval_sha, out=lambda s: None)["payload_sha256"]
        reset_flag()
        sL1 = Stub([GOOD])
        ck.refused("L1: the day ledgers hold 3 invocations for the test while the cache is fresh", lambda: R.run(
            sL1, expL, pL1, DEV_SEED, None, gen_sha, eval_sha, ledger_dir=led4, atl=atl, out=lambda s: None),
            ("the day ledgers hold 3",))
        ck.check("... with ZERO posts and nothing written", not sL1.calls and not os.path.exists(pL1.cache),
                 "posts %d" % len(sL1.calls))
        # L2: a return that makes the bookkeeping raise AFTER the post: the ledger still gets every post, the relaunch
        # counts the orphan as a transport error "no reply recorded", and the transport limit ends it
        led5 = ledger_fixture(os.path.join(tmp, "ledger5"))
        pL2 = paths_for(tmp, gen, ev, "L2")
        bad = Stub([(12345, "stop")] * 5)
        crashes = 0
        for k in range(3):
            reset_flag()
            try:
                R.run(bad, expL, pL2, DEV_SEED, None, gen_sha, eval_sha, ledger_dir=led5, atl=atl, out=lambda s: None)
            except SystemExit:
                raise
            except Exception:  # noqa: BLE001  the bookkeeping raised after the post (the probe's point)
                crashes += 1
        reset_flag()
        rL2 = R.run(bad, expL, pL2, DEV_SEED, None, gen_sha, eval_sha, ledger_dir=led5, atl=atl, out=lambda s: None)
        c = _ro(pL2.cache)
        try:
            inv = c.execute("SELECT COUNT(*) FROM invocation").fetchone()[0]
            orph = c.execute("SELECT COUNT(*) FROM transport WHERE exception_class='ORPHAN'").fetchone()[0]
        finally:
            c.close()
        ck.check("L2: 3 crashing launches post 3 times; the day ledger shows all 3; each relaunch counts the orphan as a"
                 " transport error; the 4th launch posts NOTHING and reads UNDETERMINED BY INSTRUMENT",
                 crashes == 3 and len(bad.calls) == 3 and atl.ledger_calls(R.TEST, led5) == 3 and inv == 3 and orph == 3
                 and has(rL2["outcome_lines"], "UNDETERMINED BY INSTRUMENT") and
                 has(rL2["outcome_lines"], "no reply recorded (orphan invocation)"),
                 "crashes %d, posts %d, ledger %d, invocations %d, orphans %d" % (
                     crashes, len(bad.calls), atl.ledger_calls(R.TEST, led5), inv, orph))
        # a KeyboardInterrupt during the post: the finally still ledgers it; the relaunch counts the orphan
        led6 = ledger_fixture(os.path.join(tmp, "ledger6"))
        pK = paths_for(tmp, gen, ev, "K")
        sK = Stub([KeyboardInterrupt()])
        reset_flag()
        try:
            R.run(sK, expL, pK, DEV_SEED, None, gen_sha, eval_sha, ledger_dir=led6, atl=atl, out=lambda s: None)
            k_ok = False
        except KeyboardInterrupt:
            k_ok = True
        reset_flag()
        rK = R.run(Stub([GOOD]), expL, pK, DEV_SEED, None, gen_sha, eval_sha, ledger_dir=led6, atl=atl, out=lambda s: None)
        ck.check("KeyboardInterrupt during the post: the day ledger holds the post; the relaunch records the orphan as"
                 " transport error 1 and completes (ledger 2 = invocations 2)", k_ok and rK["valid"] is not None and
                 atl.ledger_calls(R.TEST, led6) == 2 and has(rK["outcome_lines"], "orphan invocation"),
                 "k_ok %s valid %s ledger %d | %s" % (k_ok, rK.get("valid") is not None, atl.ledger_calls(R.TEST, led6),
                                                     " / ".join(x for x in rK["outcome_lines"] if "transport" in x)))
        # the triggers act BEFORE the post: after a valid reply, and after 3 attempts, attempts() refuses with 0 calls
        cc = IC.reopen(pA.cache)
        sT = Stub([GOOD, GOOD])
        try:
            ck.refused("the store refuses a further invocation after the first valid reply (IR1 / IR4) BEFORE the post",
                       lambda: R.attempts(cc, sT, "sys", "usr", rr.payload_bytes("sys", "usr"),
                                          hashlib.sha256(rr.payload_bytes("sys", "usr")).hexdigest(), [],
                                          out=lambda s: None), ("REFUSES invocation",))
            ck.check("... with 0 stub calls", not sT.calls, "calls %d" % len(sT.calls))
        finally:
            cc.close()
        cc = IC.reopen(pC.cache)
        try:
            ck.refused("the store refuses a 4th invocation after 3 attempts (IR5) BEFORE the post", lambda:
                       R._write_ahead(cc, "s"), ("3 attempts exist",))
        finally:
            cc.close()
        nums = atl.guard(R.TEST, 3, {}, led, "selftest", refuse=False)
        ck.check("the combined posting-day statement includes the other tests (4,060 + 2,178 + 1,252 + 1 posted + 3 planned)",
                 nums["combined"] == 4060 + 2178 + 1252 + 1 + 3, str(nums["combined"]))
    finally:
        T._rmtree(tmp)
    if ck.fails:
        out("[SELFTEST-INDUCE-RUN-3] FAILED %d of %d checks: %s" % (len(ck.fails), ck.n, ck.fails))
        return 1
    out("[SELFTEST-INDUCE-RUN-3] ALL PASS (%d checks; synthetic; zero calls)" % ck.n)
    return 0


def main(argv):
    lines = []

    def out(s):
        print(s, flush=True)
        lines.append(s)
    tr = argv[argv.index("--transcript") + 1] if "--transcript" in argv else None
    if tr is not None and os.path.exists(tr):
        raise SystemExit("[INDUCE-RUN] %s exists: a transcript is written once" % tr)
    try:
        return selftest(out)
    finally:
        if tr is not None:
            with open(tr, "x", encoding="utf-8", newline="\n") as f:
                f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
