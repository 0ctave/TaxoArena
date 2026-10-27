NL = chr(10)


def L(*xs):
    return NL.join(xs)


FIT = {
    "H-F1": L("1. Determine each response's final answer: the option letter it commits to, or the letter shown after its text.",
              "2. Decide which option is correct; treat the reference solution as a hint that may be wrong.",
              "3. A response with a correct final answer beats one with a wrong or missing final answer.",
              "4. If both final answers are correct, or both wrong, prefer the response whose reasoning is sound and free of errors.",
              "5. Do not reward or penalise length, formatting, or whether an explanation is given.",
              "6. If neither response is better on these criteria, declare a TIE."),
    "H-F2": L("- First, check whether each final answer matches the correct option.",
              "- Correct beats incorrect; a response with no identifiable letter counts as incorrect.",
              "- When correctness is tied, favour the response with the more logically valid derivation.",
              "- Verbosity, style and formatting carry no weight in either direction."),
    "H-F3": L("1. Correctness of the final answer is decisive.",
              "2. The reference may contain mistakes; verify it independently before relying on it.",
              "3. Among equally correct (or equally incorrect) answers, the response with fewer logical gaps in its reasoning wins.",
              "4. A truncated response is judged only on what it states.",
              "5. The length of a response and the amount of explanation it gives must not influence the verdict."),
    "H-F4": ("Compare the final answers with the correct option. The response whose final answer is correct wins. If both are"
             " correct or both are wrong, the response whose reasoning steps are valid and well justified wins. Formatting,"
             " length and explanation are neutral. Otherwise, TIE."),
    "H-F5": L("1. Identify the chosen option of each response.",
              "2. Verify which option is correct; do not assume the reference is right.",
              "3. The correct final answer takes precedence over everything else.",
              "4. Tie-break on soundness of reasoning: penalise calculation errors, invalid inferences and unsupported claims.",
              "5. A response is not favoured or disfavoured for being short, long, plain or formatted."),
    "H-F6": L("1. A response that selects the correct option beats one that selects a wrong option or none.",
              "2. If the final answers agree in correctness, prefer the response with rigorous, coherent reasoning.",
              "3. Explanations are neither required nor rewarded for their own sake; judge their correctness, not their presence.",
              "4. Otherwise TIE."),
    "H-F7": ("Step 1: find each response's final answer. Step 2: establish the correct option, checking the reference rather"
             " than trusting it. Step 3: a correct final answer beats an incorrect one. Step 4: if still tied, prefer the"
             " response whose argument contains no errors. Length and presentation are irrelevant."),
    "H-F8": L("1. Final answer correctness first: the response that picks the correct option wins.",
              "2. If both pick the correct option, or both pick wrong options, compare the validity of their reasoning; flawed steps count against a response.",
              "3. An answer given without working is not penalised for that, and a long answer is not rewarded for its length.",
              "4. If still indistinguishable, TIE."),
    "H-F9": L("1. Extract the final option letter from each response; empty or truncated responses without a letter have no final answer.",
              "2. The response whose final answer is correct is better.",
              "3. With equal correctness, the response with sounder logic is better.",
              "4. Ignore differences in length and formatting."),
    "H-F10": ("Judge primarily on whether the final answer is correct, verifying the reference solution rather than accepting"
              " it. Where both final answers are equally correct, prefer the response whose reasoning has fewer mistakes. Do"
              " not let length, format or the presence of an explanation affect the decision."),
    "H-F11": L("1. Which response's final answer matches the correct option? That response wins.",
               "2. If both match or neither does, the response with the more coherent and error-free reasoning wins.",
               "3. Brevity and elaboration are both acceptable and carry no weight.",
               "4. Otherwise TIE."),
    "H-F12": L("1. Correct final answer > incorrect or missing final answer.",
               "2. Equal final-answer correctness: prefer valid reasoning over reasoning with errors.",
               "3. Length, formatting and explanation presence: no effect.",
               "4. No remaining difference: TIE."),
    "H-F13": L("1. Check the final answer of each response against the correct option, which you should determine yourself.",
               "2. A correct final answer wins over a wrong one regardless of how much explanation accompanies it.",
               "3. If the final answers are equally correct, the response with justified steps and no reasoning errors wins.",
               "4. Otherwise TIE."),
    "H-F14": ("A response wins if its final answer is correct and the other's is not. When both are correct or both"
              " incorrect, the response whose reasoning is more rigorous and contains fewer errors wins. A shorter response"
              " and a longer response are treated alike; formatting does not count. If no difference remains, TIE."),
    "H-F15": L("1. The primary criterion is the correctness of each response's final answer.",
               "2. The secondary criterion is the soundness of its supporting reasoning (valid steps, no logical errors).",
               "3. Do not use length, formatting, or the presence or absence of an explanation as a criterion.",
               "4. If both criteria are equal, TIE."),
    "H-F16": L("1. Establish the correct option; the reference may be wrong.",
               "2. The response whose committed letter is correct wins.",
               "3. If tied on correctness, the response whose reasoning is valid beats the one whose reasoning is flawed.",
               "4. A bare letter is acceptable and is judged on its correctness alone; it is not penalised for lacking an explanation."),
    "H-F17": ("First decide which final answer is correct. The correct one wins. If both final answers are correct or both"
              " wrong, favour the response with fewer reasoning errors; don't favour a response just because it is longer"
              " or shorter. Else TIE."),
    "H-F18": L("1. Determine which final answer is correct.",
               "2. Prefer the response with the correct final answer.",
               "3. If both are equally correct, prefer the response with valid reasoning and no unsupported steps.",
               "4. Concise and detailed responses are judged equally."),
}

UNFIT = {
    "H-U1": L("1. The correct final answer wins.",
              "2. If both are correct, prefer the response with sound reasoning that is also the more succinct."),
    "H-U2": ("The final answer is correct only if the response ends with the line 'The answer is (X)'. Prefer sound"
             " reasoning when both are correct."),
    "H-U3": ("Check the final answer against the correct option. A response that rambles or pads its reasoning loses to"
             " one that is crisp, provided both reasoning chains are valid."),
    "H-U4": L("1. The correct final answer wins.",
              "2. Responses must present their answer as a lone option letter on the final line; responses that do not are treated as having no final answer.",
              "3. Then prefer sound reasoning."),
    "H-U5": "The correct final answer wins; between correct answers, the one with valid reasoning and the lower word count wins.",
    "H-U6": L("1. Score the final answer: correct or incorrect.",
              "2. Deduct for any text beyond the chosen letter.",
              "3. Break ties on reasoning errors."),
    "H-U7": ("A correct final answer is required. Responses that include step-by-step working are marked down; a valid"
             " argument does not rescue them."),
    "H-U8": L("1. The correct final answer wins.",
              "2. If both are correct, the response with sound reasoning that uses headings and bullet points wins."),
    "H-U9": ("The final answer must be given in uppercase; a lowercase letter counts as no answer. Then compare the"
             " soundness of the reasoning."),
    "H-U10": L("1. Correct final answer first.",
               "2. If equal, the response that is easier to skim and less wordy wins, assuming its reasoning is valid."),
    "H-U11": ("Only a response whose output is the option letter by itself can have a correct final answer. Reasoning errors"
              " decide ties."),
    "H-U12": L("1. The correct final answer wins.",
               "2. If tied, choose the response with fewer reasoning errors.",
               "3. If still tied, choose the one with the most thorough explanation."),
    "H-U13": ("Prefer the response whose final answer is correct and which avoids superfluous explanation; valid reasoning"
              " is a secondary consideration."),
    "H-U14": ("The final answer must be wrapped in the tag <answer>X</answer>; untagged answers are incorrect. Among correct"
              " answers, prefer sounder reasoning."),
    "H-U15": L("1. Correct final answer wins.",
               "2. Tied: the response with valid reasoning and minimal extraneous content wins."),
    "H-U16": ("Award the win to the correct final answer; if both are correct, reward economy of expression, with the"
              " reasoning errors as a last tie-break."),
    "H-U17": L("1. The final answer is correct only if stated as a single character.",
               "2. Then compare reasoning soundness."),
}
