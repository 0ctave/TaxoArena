"""judge_v2.induce_fitness: the V5 FITNESS gate of ARCH-V2-INDUCE-RUBRIC-2 (registered 7e13897, docs/judge_v2_program.md
L16326-L16348; the F1 ruling L16274-L16324; REBUILT under the judge-design-specialist's follow-up ruling F1b, programme
L16350-L16475, recorded verbatim at f9cd77c; REVISED on the READY review docs/reviews/READY_induce_rubric_2.md (d3e9716,
NOT READY on H1: false positives on fit rubrics). No V5 list has been pinned of record yet: a02a9c1's cfcb9ca4... and
4dcfd3e's a9040d5d... were never pinned). ZERO CALLS; DETERMINISTIC; no file, no DB, no network.

V5: checked on EVERY reply BEFORE it can be of record.
  (a) the rubric NAMES FINAL-ANSWER CORRECTNESS: at least one match of CORRECTNESS_RX;
  (b) it matches NONE of FORM_PATTERNS (form conditioning);
  (c) [F1b change 1, REQUIRED] it names a POSITIVE REASONING CRITERION: at least one match of REASONING_RX (a
      reasoning-quality term within 60 characters, either order, inside one clause, of a reasoning noun), in a clause that
      does not NEGATE it [READY M1: "the soundness of the reasoning does not matter", "reasoning errors are irrelevant",
      "ignore the steps"].
  FAILS if (a) has 0 matches, (b) has >= 1 match, or (c) has 0 matches. A V5 failure is a FORMAL FAILURE (class "FITNESS"
  in induce_run_2): it consumes one of the 3 attempts and is disclosed with the failing leg(s) and matching pattern(s).

SCOPE (F1b change 7, of record): V5 is a LEXICAL SCREEN; it cannot be complete, in either direction. The registered fitness
reading by the READY / post-run reviewer stays the backstop for what V5 lets through. A post-run reading of UNFIT makes the
artefact NOT ADOPTED and sends the slot to THE AUTHOR; it is NEVER a fourth attempt (a re-roll decided by a human reviewer
would be best-of-n). A V5 PASS does not show that a rubric is fit. The KNOWN LIMITS (texts V5 does not decide as the reader
would) are pinned verbatim in induce_run_2_selftest.KNOWN_LIMITS.

THE RULE, PINNED. Every regex is compiled with re.IGNORECASE and nothing else and searched over the rubric text as returned,
unnormalised. The rule is BUILT by build_rules() from named parts (so each part can be removed by a selftest mutant);
REGEX_LIST_SHA256 = sha256 of regex_list_json() (canonical JSON: sort_keys, ensure_ascii, default separators) over
{"version", "flags", "correctness", "reasoning", "clause", "contrast", "concessive", "cue": [[name, regex], ...], "form":
[[name, regex, guarded], ...]}; each regex is the FULL compiled text (guards included).

(a) CORRECTNESS_RX: "final answer(s)" | "correct(ness) (of the/each/its/their) (final) answer/option/choice" | [READY H1 (v)]
    "right (final) answer/option/choice" | "correctness"; word-bounded ("incorrect" does not count).
(c) REASONING_RX: quality terms sound*, valid*, rigo(u)r*, coheren*, error(s), mistake(s), flaw*, unsupported, gap(s),
    justif*, logic*; nouns reasoning, step(s), derivation(s), argument(s), working, logic; <= 60 characters apart, either
    order, inside one guard clause, and the guard clause carries no REASONING NEGATION (does / do not matter, don't /
    doesn't matter, irrelevant, ignore / disregard (the|any|all) reasoning|steps|working|derivation|argument, no credit for).
(b) FORM_PATTERNS (12):
    UNGUARDED (a form requirement whatever surrounds it): no_other_text; exact_single_letter (requires the uppercase /
    capital qualifier); only_the_letter (requires an output verb before "only the letter"); a_to_z; no_credit_reasoning;
    exclusivity [F1b change 5] ("letter(s)" then within 60 characters "nothing else" | "no additional/other/further/extra/
    added <word>" | "solely" | "by itself" | "alone" [READY H1 (iv): NOT "alone determines / decides / counts / is compared",
    a statement of what is compared]; or "solely|just" ... "letter(s)"; or "letter(s) only"; no bare "only");
    ideal_bare_letter [READY M1] ("the good / ideal / best / perfect response (is|consists of|contains) (just / only) a bare /
    single / lone (option) letter").
    GUARDED (discounted in a guard clause carrying a disclaimer CUE): extra_text; lowercase; penalise_form; reward_form;
    format_demand [READY M1] (JSON, Markdown, bold, **X**, bullet points, headings, "formatted as", 'Answer: X').
    penalise_form: a penalty verb (penali[sz]*, deduct*, reject*, disqualif*, score* 0|zero, marks down, lower(s), violat*,
    loses, fails) and a form object (length, lengthy, verbosity, verbose, formatting, presence|absence|lack of an
    explanation, explanation(s), commentary, elaboration, working, additional|extra|added|other text|words|content|output,
    includ*|contain*|add*|provid*|show* (any|a|an) reasoning not followed by errors/mistakes/flaws/gaps), within 120
    characters, either order. [READY H1 (iii)] "explanation(s)" / "working" do NOT count when preceded by "<error(s) |
    mistake(s) | flaw(s) | gap(s) | claim(s) | step(s)> in (the|its|their) " (a reasoning criterion, e.g. "penalise errors in
    the explanation").
    reward_form: a reward verb (wins, prefer*, favo(u)r*, reward*, better, higher, bonus, extra credit, ties go to) and a
    brevity / length / format object ((more) concise, brief*, brevity, terse*, short / shorter / shortest [not when followed
    by "(and|but) (in)correct": "a short correct response wins over a long incorrect one" is a correctness statement],
    minimal, without elaboration, fewer words, less text, to the point, unnecessary detail|elaboration, quicker to read,
    longer, lengthier, more detailed, more thorough, more verbose, better / nicer / cleaner formatting, well- /
    better-formatted), within 120 characters, either order; [READY H1 (ii)] neither the verb nor the object may follow a
    CONCESSIVE (even if / even when / even though / although) in the clause ("wins, even if its explanation is brief").
THE NEGATION GUARD. Guard clauses are delimited by . ; ! ? newline and [F1b change 2] by but / however / whereas / yet; the
    colon is not a delimiter. A guarded pattern matches only inside a guard clause carrying NO entry of CUE_ENTRIES (named;
    READY H1 (i) added the contracted negations, "neither required nor penalised", "not (any) better / worse", "does not win
    / score / earn / gain / lose", "neither better nor worse", "earns or loses", "not its length / formatting"; READY M1
    NARROWED "ignore / disregard" and "regardless / irrespective of" to FORM objects, so "Ignore the reasoning and prefer the
    concise response" and "Regardless of the reference, the shorter response wins" count). The guard is INSIDE each regex.
    KNOWN LIMITS: see induce_run_2_selftest.KNOWN_LIMITS (pinned texts), plus: a guarded pattern sharing a guard clause with
    an unrelated form disclaimer is discounted; "working" as a penalty object can trip a fit clause such as "the response
    whose working is flawed loses"; a reasoning criterion sharing a clause with "irrelevant" is not counted for (c).

C-V5-neg, C-V5-pos, C-V5-probe (F1b corpus B1-B11 / F1-F5) and the READY probe corpus (B12+ / F6+, and the known limits)
and the mutation checks are executed by induce_run_2_selftest.py.
"""
import hashlib
import json
import re

V5_VERSION = "jv2-v5-3"      # 2: F1b changes 1-5; 3: READY H1 (i)-(v) + M1
FLAGS_NAME = "IGNORECASE"
_FLAGS = re.IGNORECASE

CLAUSE = r"[.;!?\n]"
CONTRAST = r"(?:\bbut\b|\bhowever\b|\bwhereas\b|\byet\b)"
CONCESSIVE = r"(?:\beven\s+(?:if|when|though)\b|\balthough\b)"
_START = (r"(?:^|(?<=[.;!?\n])|(?<=\bbut\b)|(?<=\bhowever\b)|(?<=\bwhereas\b)|(?<=\byet\b))")
_FORMWORD = (r"(?:(?:the|any|its|their|a|all)\s+)?(?:letter\s+)?(?:length|format\w*|style|case|capitali[sz]ation|verbosity"
             r"|brevity|explanations?|extra\s+text|lower[\s-]?case|presence|absence|how)\b")

# the disclaimer CUE, as NAMED entries (each removable by a mutant); the order is part of the pin
CUE_ENTRIES = (
    ("ignore_form", r"\b(?:ignor\w*|disregard\w*)\s+" + _FORMWORD),                        # narrowed (READY M1)
    ("regardless_form", r"\b(?:regardless|irrespective)\s+of\s+" + _FORMWORD),              # narrowed (READY M1)
    ("neg_reward_penalise", r"\b(?:do|does|must|should|will|may)\s+not\s+(?:be\s+)?(?:reward|penali[sz]|affect|influence"
                            r"|matter|count)\w*"),
    ("neg_prefer_favour", r"\b(?:do|does|must|should|will|may)\s+not\s+(?:prefer|favou?r)\w*"),          # F1b change 3
    ("neg_contracted", r"\b(?:do|does|did|must|should|wo|is|are|was|were|ca)n[’']?t\s+(?:be\s+)?(?:reward|penali[sz]"
                       r"|affect|influence|matter|count|prefer|favou?r|win|score|earn|gain|lose)\w*"),     # READY H1 (i)
    ("not_rewarded_penalised", r"\bnot\s+(?:be\s+)?(?:rewarded|penali[sz]ed)\b"),
    ("not_preferred", r"\bnot\s+(?:be\s+)?preferred\b"),                                     # F1b change 3
    ("neither_rewarded_nor_penalised", r"\bneither\s+rewarded\s+nor\s+penali[sz]ed\b"),
    ("neither_helps_nor_hurts", r"\bneither\s+helps?\s+nor\s+hurts?\b"),                     # F1b change 3
    ("neither_required_nor_penalised", r"\bneither\s+required\s+nor\s+penali[sz]ed\b"),     # READY H1 (i)
    ("not_better_worse", r"\b(?:not|(?:is|are|was|were)n[’']?t)\s+(?:any\s+)?(?:better|worse)\b"),  # READY H1 (i)
    ("neg_win_score_earn", r"\b(?:does|do|should|must|will)\s+not\s+(?:win|score|earn|gain|lose)\w*"),   # READY H1 (i)
    ("neither_better_nor_worse", r"\bneither\s+better\s+nor\s+worse\b"),                    # READY H1 (i)
    ("earns_or_loses", r"\b(?:earns?|gains?|wins?)\s+or\s+loses?\b"),                       # READY H1 (i) (N6)
    ("not_its_form", r"\bnot\s+(?:its|their|the)\s+(?:length|formatting|format|style|brevity|verbosity)\b"),  # (G13)
    ("no_penalty_bonus", r"\bno\s+(?:penalty|penalties|bonus)\b"),
    ("never_reward_penalise", r"\bnever\s+(?:reward|penali[sz])\w*"),
    ("not_the_longer", r"\bnot\s+(?:the\s+)?(?:longer|shorter|lengthier|briefer|more\s+detailed|more\s+concise"
                       r"|better[\s-]formatted)\b"),
)
REASONING_NEGATION = (r"(?:\b(?:do|does)\s+not\s+matter\b|\b(?:don|doesn)[’']?t\s+matter\b|\birrelevant\b"
                      r"|\b(?:ignor\w*|disregard\w*)\s+(?:(?:the|any|all)\s+)?(?:reasoning|steps?|working|derivations?"
                      r"|arguments?)\b|\bno\s+credit\s+for\b)")

_QUALITY = (r"(?:sound\w*|valid\w*|rigou?r\w*|coheren\w*|errors?|mistakes?|flaw\w*|unsupported|gaps?|justif\w*"
            r"|logic\w*)")
_RNOUN = r"(?:reasoning|steps?|derivations?|arguments?|working|logic)"

_ERR_IN = [n + " in " + d for n in ("error", "errors", "mistake", "mistakes", "flaw", "flaws", "gap", "gaps", "claim",
                                     "claims", "step", "steps") for d in ("", "the ", "its ", "their ")]

DEFAULT_OPTS = {"a_right_correctness": True, "c_negation": True, "concessive": True, "errors_in_exempt": True,
                "alone_exempt": True, "short_correct_exempt": True, "m1_reward_objects": True, "guard": True,
                "contrast": True, "cue_override": None, "drop_cue": ()}


def build_rules(**opts):
    """-> {"correctness", "reasoning", "cue", "form", ...} for the given options (defaults = the rule of record); a mutant
    passes one option switched off. Pure."""
    o = dict(DEFAULT_OPTS)
    for k in opts:
        if k not in o:
            raise SystemExit("[INDUCE-FITNESS] unknown build option %r" % k)
    o.update(opts)
    over = dict(o["cue_override"] or {})
    cue_entries = tuple((n, over.get(n, rx)) for n, rx in CUE_ENTRIES if n not in o["drop_cue"])
    cue = "(?:" + "|".join(rx for _n, rx in cue_entries) + ")"
    if o["contrast"]:
        ch, start = r"(?:(?!%s)[^.;!?\n])" % CONTRAST, _START
    else:                                    # mutant only: no contrastive split
        ch, start = r"[^.;!?\n]", r"(?:^|(?<=[.;!?\n]))"
    if o["concessive"]:
        chr_ = (r"(?:(?!%s|%s)[^.;!?\n])" % (CONTRAST, CONCESSIVE) if o["contrast"] else
                r"(?:(?!%s)[^.;!?\n])" % CONCESSIVE)
    else:                                    # mutant only: no concessive guard
        chr_ = ch

    def guarded(core, c=ch):
        if not o["guard"]:                   # mutant only: the negation guard stripped
            return core
        return r"%s(?!%s*%s)%s*?%s" % (start, ch, cue, c, core)

    def either(a, b, c=ch, n=120):
        return r"(?:%s%s{0,%d}?%s|%s%s{0,%d}?%s)" % (a, c, n, b, b, c, n, a)

    correctness = (r"\bfinal[\s-]+answers?\b"
                   r"|\bcorrect(?:ness)?\s+(?:of\s+(?:the\s+|each\s+|its\s+|their\s+)?)?(?:final\s+)?"
                   r"(?:answers?|options?|choices?)\b")
    if o["a_right_correctness"]:
        correctness += r"|\bright\s+(?:final\s+)?(?:answers?|options?|choices?)\b|\bcorrectness\b"
    core_c = r"\b%s\b%s{0,60}?\b%s\b|\b%s\b%s{0,60}?\b%s\b" % (_QUALITY, ch, _RNOUN, _RNOUN, ch, _QUALITY)
    if o["c_negation"]:
        reasoning = r"%s(?!%s*%s)%s*?(?:%s)" % (start, ch, REASONING_NEGATION, ch, core_c)
    else:
        reasoning = core_c
    exempt = "".join("(?<!%s)" % re.escape(x) for x in _ERR_IN) if o["errors_in_exempt"] else ""
    penalty = (r"\b(?:penali[sz]\w*|deduct\w*|reject\w*|disqualif\w*|score\w*\s*(?:0|zero)\b|marks?\s+down|lowers?"
               r"|violat\w*|loses?|fails?)\b")
    form_object = (r"\b(?:length|lengthy|verbosity|verbose|formatting|(?:presence|absence|lack)\s+of\s+(?:an?\s+)?"
                   r"explanations?|%s(?:explanations?|working)|commentary|elaboration|(?:additional|extra|added|other)\s+"
                   r"(?:text|words?|content|output)|(?:includ|contain|add|provid|show)\w*\s+(?:any\s+|an?\s+)?reasoning"
                   r"(?!\s+(?:errors?|mistakes?|flaws?|gaps?)))\b" % exempt)
    reward = r"\b(?:wins?|prefer\w*|favou?r\w*|reward\w*|better|higher|bonus|extra\s+credit|ties?\s+go(?:es)?\s+to)\b"
    short = r"short(?:er|est)?\b" + (r"(?!\s+(?:and\s+|but\s+)?(?:in)?correct\b)" if o["short_correct_exempt"] else "")
    reward_object = (r"\b(?:(?:more\s+)?concise|brief\w*|terse\w*|%s|minimal|without\s+elaboration|longer|lengthier"
                     r"|more\s+detailed|more\s+thorough|more\s+verbose|(?:better|nicer|cleaner)\s+formatting|well[\s-]formatted"
                     r"|better[\s-]formatted" % short)
    if o["m1_reward_objects"]:
        reward_object += (r"|brevity|fewer\s+words|less\s+text|to\s+the\s+point|unnecessary\s+(?:detail|elaboration)"
                          r"|quicker\s+to\s+read")
    reward_object += r")"
    alone = r"\balone\b" + (r"(?!\s+(?:determines?|decides?|counts?|is\s+compared|settles?))" if o["alone_exempt"] else "")
    excl = (r"\bletters?\b[^.;!?\n]{0,60}?(?:\bnothing\s+else\b|\bno\s+(?:additional|other|further|extra|added)\s+\w+"
            r"|\bsolely\b|\bby\s+itself\b|" + alone + r")"
            r"|\b(?:solely|just)\b[^.;!?\n]{0,60}?\bletters?\b"
            r"|\bletters?\s+only\b")
    form = (
        ("no_other_text", r"\bno\s+other\s+(?:text|characters?|words?|content|output)\b", False),
        ("extra_text", guarded(r"\bextra\s+(?:text|characters?|words?|content|output)\b"), True),
        ("exact_single_letter", r"\b(?:exactly|single)\s+(?:one\s+)?(?:uppercase|capital)\s+letters?\b", False),
        ("only_the_letter", r"\b(?:output\w*|gives?|writes?|answers?\s+with|respond\w*\s+with|repl(?:y|ies)\s+with"
                            r"|contains?|consists?\s+of|be|is)\s+only\s+(?:the|a|one)\s+(?:(?:option|answer|uppercase"
                            r"|capital)\s+)?letter\b", False),
        ("a_to_z", r"\(\s*a\s*[-–—]\s*z\s*\)", False),
        ("lowercase", guarded(r"\blower[\s-]?case\b"), True),
        ("no_credit_reasoning", r"\bno\s+credit\s+for\s+(?:the\s+)?(?:reasoning|explanations?|working|steps|computations?)"
                                r"\s*(?:[,.;!?\n]|$|or\b|and\b)", False),
        ("penalise_form", guarded(either(penalty, form_object)), True),
        ("reward_form", guarded(either(reward, reward_object, chr_), chr_), True),
        ("exclusivity", excl, False),
        ("ideal_bare_letter", r"\b(?:good|ideal|best|perfect)\s+(?:response|answer)\s+(?:is|consists\s+of|contains)\s+"
                              r"(?:just\s+|only\s+)?(?:a\s+)?(?:bare|single|lone)\s+(?:option\s+)?letter\b", False),
        ("format_demand", guarded(r"(?:\bjson\b|\bmarkdown\b|\bbold\b|\*\*\s*[a-z]?\s*\*\*|\bbullet\s+points?\b"
                                  r"|\bheadings?\b|\bformatted\s+as\b|['\"‘“]\s*answer\s*:\s*[a-z]\s*"
                                  r"['\"’”])"), True),
    )
    return {"version": V5_VERSION, "flags": FLAGS_NAME, "correctness": correctness, "reasoning": reasoning,
            "clause": CLAUSE, "contrast": CONTRAST, "concessive": CONCESSIVE if o["concessive"] else None,
            "cue": [[n, rx] for n, rx in cue_entries], "form": form}


_RULES = build_rules()
CORRECTNESS_RX = _RULES["correctness"]
REASONING_RX = _RULES["reasoning"]
FORM_PATTERNS = _RULES["form"]
CUE = "(?:" + "|".join(rx for _n, rx in CUE_ENTRIES) + ")"

# C-V5-pos: a FIT control text that carries the instruction's own neutrality clause verbatim (sentence 5)
NEUTRALITY_CLAUSE = ("must not reward or penalise length, formatting, or the presence or absence of an explanation")
CONTROL_FIT_TEXT = (
    "1. Identify the final answer of each response: the one option letter it commits to; a truncated or empty response, or"
    " one that states no letter, has no final answer.\n"
    "2. Compare each final answer with the correct option, using the reference solution as a guide but checking it, since"
    " it may be wrong.\n"
    "3. A response whose final answer is correct beats one whose final answer is wrong or missing.\n"
    "4. If both final answers are correct, or both are wrong, prefer the response whose supporting reasoning is sounder;"
    " otherwise TIE.\n"
    "5. The judge " + NEUTRALITY_CLAUSE + ".")


def regex_list(rules=None):
    # the module-level constants (what v5() uses) when no rule dict is given, so a changed constant changes the sha
    r = dict(_RULES, correctness=CORRECTNESS_RX, reasoning=REASONING_RX, form=FORM_PATTERNS) if rules is None else rules
    return {"version": r["version"], "flags": r["flags"], "correctness": r["correctness"], "reasoning": r["reasoning"],
            "clause": r["clause"], "contrast": r["contrast"], "concessive": r["concessive"], "cue": r["cue"],
            "form": [[n, rx, g] for n, rx, g in r["form"]]}


def regex_list_json(lst=None):
    return json.dumps(regex_list() if lst is None else lst, sort_keys=True, ensure_ascii=True)


def regex_list_sha256(lst=None):
    return hashlib.sha256(regex_list_json(lst).encode("utf-8")).hexdigest()


REGEX_LIST_SHA256 = "7b5af1d513df318031d77a14b7c8673051a075957ca97ffcc287cdfdc516fa54"   # the pin (regex_list_sha256()); jv2-v5-3 (READY H1 + M1)
CONTROL_FIT_SHA256 = "a7b8ebb0d36b069204703095eb8531a2565bf0e347ccff820bde94c9f590aef0"    # sha256 of CONTROL_FIT_TEXT (UTF-8)


def v5(text, correctness=None, form=None, require_correctness=True, reasoning=None, require_reasoning=True):
    """-> {"pass", "a", "b", "c", "a_matches", "b_matches", "c_matches"}. The rule of record unless a mutant passes its
    parts; (a) / (c) are None when not required (mutants only). Pure; no side effect."""
    correctness = CORRECTNESS_RX if correctness is None else correctness
    form = FORM_PATTERNS if form is None else form
    reasoning = REASONING_RX if reasoning is None else reasoning
    if not isinstance(text, str):
        return {"pass": False, "a": False, "b": False, "c": False, "a_matches": [], "c_matches": [],
                "b_matches": [["not_text", repr(type(text))]]}
    a_m = [m.group(0) for m in re.finditer(correctness, text, _FLAGS)] if require_correctness else []
    c_m = [m.group(0).strip()[-80:] for m in re.finditer(reasoning, text, _FLAGS)] if require_reasoning else []
    b_m = []
    for name, rx, _g in form:
        m = re.search(rx, text, _FLAGS)
        if m is not None:
            b_m.append([name, m.group(0).strip()[-80:]])
    a_ok = bool(a_m) if require_correctness else None
    c_ok = bool(c_m) if require_reasoning else None
    b_ok = bool(not b_m)
    return {"pass": bool((a_ok is None or a_ok) and b_ok and (c_ok is None or c_ok)), "a": a_ok, "b": b_ok, "c": c_ok,
            "a_matches": a_m, "b_matches": b_m, "c_matches": c_m}


def v5_rules(text, rules, require_correctness=True, require_reasoning=True):
    """v5 under a rule dict built by build_rules() (the selftest's mutants)."""
    return v5(text, rules["correctness"], rules["form"], require_correctness, rules["reasoning"], require_reasoning)


def describe(res):
    """One line for the outcome / the attempt record."""
    yn = {True: "YES", False: "NO", None: "NOT CHECKED"}
    return ("V5 %s: (a) final-answer correctness named %s (%d match(es)%s); (b) form-conditioning patterns matched %d%s;"
            " (c) reasoning criterion named %s (%d match(es)%s)" % (
                "PASS" if res["pass"] else "FAIL", yn[res["a"]], len(res["a_matches"]),
                (": %r" % res["a_matches"][:3]) if res["a_matches"] else "", len(res["b_matches"]),
                (": %s" % "; ".join("%s %r" % (n, s) for n, s in res["b_matches"])) if res["b_matches"] else "",
                yn[res.get("c")], len(res.get("c_matches", [])),
                (": %r" % res["c_matches"][:3]) if res.get("c_matches") else ""))
