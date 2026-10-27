"""judge_v2.induce_fitness_3: the V5 FITNESS screen jv2-v5-4 of ARCH-V2-INDUCE-RUBRIC-3 (registered 39c81c0,
docs/judge_v2_program.md L17008-L17110, section "V5 FITNESS jv2-v5-4"). ZERO CALLS; DETERMINISTIC; no file, no DB, no
network.

IT IMPORTS judge_v2.induce_fitness (jv2-v5-3, blob:28638dcfcd7f464404af6e085d2de99d32ada70d, REGEX_LIST_SHA256 7b5af1d5...)
UNCHANGED and LAYERS the registered legs on top of it; both pins are checked at import (a different blob or list sha
REFUSES: the -2 screen is part of this one). PASS iff every leg below passes:
  (a') jv2-v5-3's correctness leg, AMENDED (M3): a CORRECTNESS_RX match counts only if its GUARD CLAUSE does not also carry
       a LIVE (d1) match (a (d1) match not discounted by the reference cue below): the rubric must name final-answer
       correctness somewhere other than a clause that measures it against the reference. Guard clauses are jv2-v5-3's
       (delimited by . ; ! ? newline and by but / however / whereas / yet; SPLIT_RX).
  (b)+(c) jv2-v5-3's form patterns and its required reasoning criterion, UNCHANGED (induce_fitness.v5).
  (d) REFERENCE-AS-CRITERION, two legs, neither may fire:
       (d1) GUARDED: correctness or winning defined by agreement with the reference (D1_PARTS: agree_with_reference,
            treat_reference_as, reference_is_key, defer_to_reference, correct_is_reference), discounted in a guard clause
            carrying a CUE (jv2-v5-3's CUE_ENTRIES + CUE_REF_ENTRIES);
       (d2) CONDITIONAL: a rubric naming "reference" must carry at least one SCEPTIC cue (SCEPTIC_ENTRIES) anywhere.
  (e) REASONING-PRESENCE REWARD, GUARDED (same cue): a reward verb near a reasoning-PRESENCE object or a DEPTH object, or a
       penalty verb near an ABSENCE object (E_PARTS: presence_reward, depth_reward, absence_penalty), within 100
       characters, either order, inside one guard clause; jv2-v5-3's ERRORS-IN EXEMPTION: an object preceded by
       "<error(s) | mistake(s) | flaw(s) | gap(s) | claim(s) | step(s)> in (the|its|their) " is not an object.
  (f) TIE SUPPRESSION AND POSITIONAL DEFAULT, UNGUARDED (F_PARTS: tie_identical, never_tie, always_winner,
       tie_discouraged, positional_otherwise, positional_if_doubt, positional_by_default). A bare "TIE only if" without
       "identical" does NOT fire; "otherwise TIE" does NOT fire. Unguarded means no CUE: the patterns carry only LOCAL
       adjacency (e.g. "TIE is a last resort" fires, "TIE is not a last resort" does not; "avoid ties" fires unless
       directly preceded by "not" / "n't"), so a verbatim echo of the prompt's own S8 ("must not reserve TIE for identical
       responses, must not forbid or discourage TIE, and must not default to either response") does not fire.
THE REFERENCE CUE (the (d1) / (e) guard): jv2-v5-3's CUE mechanism (its 18 named entries, unchanged) EXTENDED with
CUE_REF_ENTRIES: the five registered reference-specific negations (not_merely, neg_make_mean, rather_than,
do_not_treat_as, not_penalised_for) and THREE BUILDER ADDITIONS forced by texts the screen must pass (disclosed, each
named, each removable by a mutant): not_correct_because (fit3 P0, P1: "is not correct (merely) because it matches"),
neg_define_as (the prompt's own S6 in rubric voice: "do not define a correct final answer as one that matches ... the
reference"), neither_nor (the prompt's own S7 in rubric voice: "neither preferred nor penalised merely for giving no
reasoning or for giving more reasoning"). not_penalised_for is WIDENED from the registered "is not (penalised|rewarded)
for" to "(is|are) not (penalised|penalized|rewarded|marked down) for": the registered form is subsumed by jv2-v5-3's own
not_rewarded_penalised entry (a mutant removing it could not be killed); "marked down" is what fit3 P12 needs.
SCEPTIC CUES ((d2)): the registered list (may_be_wrong, possibly_wrong, verify, own_working (with "check against own
reading / working", which it contains), one_input, evidence, hint, not_the_key (with "never"), independent, not_proof) and
ONE BUILDER ADDITION, fallible (the READY corpus F7 of record, "treating the reference as fallible", must PASS).

SCOPE (F1b change 7, carried): V5 is a LEXICAL SCREEN; it cannot be complete in either direction; the registered checklist
K1-K8 is the substantive check; a V5 PASS is not evidence of fitness.

THE RULE, PINNED. Every regex is compiled with re.IGNORECASE and nothing else, searched over the rubric text as returned.
build_rules_v54() builds the new parts from NAMED parts (so a selftest mutant can remove each); REGEX_LIST_SHA256_V54 =
sha256 of regex_list_v54_json() (canonical JSON: sort_keys, ensure_ascii, default separators) over {"version", "flags",
"base_version", "base_regex_list_sha256", "base_list" (= induce_fitness.regex_list(), the jv2-v5-3 list in full),
"a_prime", "split", "cue_ref", "d1", "d2", "e", "f"}; every regex is the FULL compiled text (guards included).
The acceptance corpora (C-V5-neg, C-V5-neg-2, C-V5-pos, C-V5-probe, B29f, C-V5-probe-3) and the mutants are executed by
induce_run_3_selftest.py.
"""
import hashlib
import json
import re

from ._base import git_blob_lf
from . import induce_fitness as F

V5_VERSION = "jv2-v5-4"
BASE_VERSION = "jv2-v5-3"
BASE_BLOB = "28638dcfcd7f464404af6e085d2de99d32ada70d"                                       # induce_fitness.py, blob (LF)
BASE_REGEX_LIST_SHA256 = "7b5af1d513df318031d77a14b7c8673051a075957ca97ffcc287cdfdc516fa54"   # jv2-v5-3's pin
FLAGS_NAME = F.FLAGS_NAME
_FLAGS = F._FLAGS

if F.V5_VERSION != BASE_VERSION or F.REGEX_LIST_SHA256 != BASE_REGEX_LIST_SHA256 or \
        F.regex_list_sha256() != BASE_REGEX_LIST_SHA256:
    raise SystemExit("[INDUCE-FITNESS-3] judge_v2.induce_fitness is not jv2-v5-3 with list sha256 %s: refused"
                     % BASE_REGEX_LIST_SHA256)
if git_blob_lf(F.__file__) != BASE_BLOB:
    raise SystemExit("[INDUCE-FITNESS-3] judge_v2.induce_fitness blob %s is not the pinned %s: refused"
                     % (git_blob_lf(F.__file__), BASE_BLOB))

SPLIT_RX = r"[.;!?\n]|\bbut\b|\bhowever\b|\bwhereas\b|\byet\b"     # jv2-v5-3's guard-clause delimiters

# ── the reference cue: jv2-v5-3's CUE_ENTRIES (unchanged, imported) + these, NAMED, in this order (the order is pinned) ──
CUE_REF_ENTRIES = (
    ("not_merely", r"\bnot\s+(?:merely|simply|just|by\s+itself|necessarily)\b"),                    # registered
    ("neg_make_mean", r"\b(?:is|does)\s+not\s+(?:make|mean|imply|prove)\w*"),                        # registered
    ("rather_than", r"\brather\s+than\b"),                                                           # registered
    ("do_not_treat_as", r"\b(?:do|does)\s+not\s+treat\b[^.;!?\n]{0,80}?\bas\b"),                      # registered
    ("not_penalised_for", r"\b(?:is|are)\s+not\s+(?:penali[sz]ed|rewarded|marked\s+down)\s+for\b"),  # registered, widened
    ("not_correct_because", r"\bnot\s+(?:correct|right)\s+because\b"
                            r"|\bnot\b[^.;!?\n]{0,60}?\b(?:merely|simply|just|only|solely)\s+because\b"),        # builder
    ("not_proof_of", r"\b(?:is|are)\s+not\s+(?:in\s+itself\s+|by\s+itself\s+|on\s+its\s+own\s+)?(?:proof|evidence"
                     r"|a\s+sign)\s+(?:of|that)\b"),                                                  # builder
    ("neg_define_as", r"\b(?:do|does|must|should)\s+not\s+(?:define|regard|consider|count)\b[^.;!?\n]{0,80}?\bas\b"),  # b.
    ("neither_nor", r"\bneither\s+(?:preferred|favou?red|rewarded|credited)\s+nor\s+(?:penali[sz]ed|punished"
                    r"|marked\s+down)\b"),                                                            # builder
    ("neg_mark_down", r"\b(?:do|does|must|should|will)\s+not\s+(?:mark\w*\s+down|punish\w*|dock\w*|deduct\w*)"),  # builder
    ("no_credit", r"\b(?:earns?|gets?|gains?|receives?)\s+no\s+(?:extra\s+)?(?:credit|points?|bonus)\b"),   # builder
)

# ── (d1) reference-as-criterion ──
_REF = r"(?:the\s+|a\s+|its\s+)?reference(?:[’']s)?(?:\s+(?:solution|answer|letter|option|choice))?\b"
D1_ENTRIES = (
    ("agree_with_reference", r"\b(?:match(?:es|ed|ing)?|agree(?:s|d|ing)?|agreement|(?:the\s+)?same\s+as|equal\s+to"
                             r"|identical\s+to|consistent\s+with|differ(?:s|ed|ing)?\s+from|different\s+from"
                             r"|mismatch(?:es|ed|ing)?|disagree(?:s|d|ing)?)\s+(?:with\s+|to\s+|against\s+)?"
                             r"(?:that\s+of\s+)?" + _REF),
    ("treat_reference_as", r"\b(?:treat\w*|tak(?:e|es|en|ing)|use[sd]?|using|regard\w*|consider\w*|accept\w*)\s+" + _REF +
                           r"\s+as\s+(?:correct|right|true|authoritative|definitive|(?:the\s+)?(?:answer\s+)?key"
                           r"|(?:the\s+)?ground\s+truth|the\s+(?:correct|right)\s+(?:final\s+)?answer|the\s+truth"
                           r"|the\s+standard|the\s+yardstick)\b"),
    ("reference_is_key", r"\breference(?:[’']s)?(?:\s+(?:solution|answer|letter|option))?\s+(?:is|serves\s+as|acts\s+as"
                         r"|counts\s+as|defines)\s+(?:the\s+)?(?:answer\s+key|key|ground\s+truth|yardstick|gold\s+standard"
                         r"|correct\s+answer|right\s+answer|truth)\b"),
    ("defer_to_reference", r"\b(?:defer\w*\s+to|trust\w*|follow\w*|rely\w*\s+on|go(?:es)?\s+with|side\w*\s+with)\s+" + _REF),
    ("correct_is_reference", r"\b(?:correct|right)\s+(?:final\s+)?(?:answer|option|letter|choice)\s+is\s+(?:always\s+)?"
                             + _REF),
)

# ── (d2) sceptic cues (anywhere in the rubric, when it names "reference") ──
D2_TRIGGER = r"\breference\b"
SCEPTIC_ENTRIES = (
    ("may_be_wrong", r"\b(?:may|might|can|could)\s+(?:also\s+|itself\s+)?be\s+(?:wrong|mistaken|incorrect|in\s+error"
                     r"|flawed|erroneous)\b"),
    ("possibly_wrong", r"\bpossibly\s+(?:wrong|mistaken|incorrect)\b"),
    ("verify", r"\bverif\w*"),
    ("own_working", r"\bown\s+(?:working|reading|solution)\b"),
    ("one_input", r"\bone\s+input\b"),
    ("evidence", r"\bevidence\b"),
    ("hint", r"\bhints?\b"),
    ("not_the_key", r"\b(?:not|never)\s+(?:as\s+)?(?:the\s+|a\s+)?(?:yardstick|answer\s+key|key)\b"),
    ("independent", r"\bindependent(?:ly)?\b"),
    ("not_proof", r"\bnot\b[^.;!?\n]{0,60}?\bproof\b"),
    ("fallible", r"\bfallible\b"),                                                                    # builder
    ("may_contain_errors", r"\b(?:may|might|can|could)\s+(?:itself\s+)?(?:contain|have|include|carry)\s+(?:an?\s+)?"
                           r"(?:errors?|mistakes?)\b"),                                               # builder
    ("not_always_right", r"\bnot\s+(?:always|necessarily)\s+(?:right|correct)\b"),                   # builder
    ("caution", r"\b(?:caution\w*|cautious\w*|sceptic\w*|skeptic\w*|critically)\b"),                 # builder
)

# ── (e) reasoning-presence reward / absence penalty ──
_REWARD_E = (r"\b(?:wins?|winning|beats?|prefer\w*|favou?r\w*|reward\w*|credit\w*|better|higher|bonus"
             r"|ranks?\s+(?:higher|above|first))\b")
_PENALTY_E = (r"\b(?:loses?|losing|lost|penali[sz]\w*|punish\w*|ranks?\s+(?:lower|below|last)|scores?\s+lower|lower|worse"
              r"|marked\s+down|marks?\s+down|deduct\w*|counts?\s+against)\b")
_NOUN = r"(?:reasoning|explanations?|justifications?|working|derivations?|arguments?|rationale)"
_PRESENCE = (r"\b(?:(?:shows?|showing|gives?|giving|provides?|providing|includes?|including|offers?|offering|presents?"
             r"|presenting|has|having|with)\s+(?:(?:its|their|the|an?|any|some|more|full|fuller|explicit|detailed"
             r"|extensive|complete|step-by-step)\s+)*(?:reasoning|explanations?|justifications?|working|work"
             r"|derivations?|rationale)|explains?(?:\s+and\s+justifies)?\s+(?:its|their|the)\s+(?:answer|choice|option"
             r"|letter)|justif(?:y|ies)\s+(?:its|their|the)\s+(?:answer|choice|option|letter)|(?:a|the)\s+(?:worked"
             r"|explained|justified|reasoned)\s+(?:answer|solution|response))\b")
_DEPTH = (r"\b(?:(?:more|greater|further|deeper)\s+depth|into\s+(?:more\s+|greater\s+)?depth|in[\s-]depth\s+" + _NOUN +
          r"|(?:full|fuller|fullest|detailed|thorough|extensive|complete|elaborate|lengthy|longer|deeper|richer)\s+" + _NOUN +
          r"|more\s+(?:reasoning|explanation|justification|working|detail|analysis)|thoroughness"
          r"|(?:more|most)\s+(?:thorough|detailed|complete|extensive|elaborate|comprehensive))\b")
_ABSENCE = (r"\b(?:bare\s+(?:option\s+)?(?:letters?|answers?)|lone\s+letters?|(?:no|without(?:\s+any)?|missing|absent"
            r"|lacks?|lacking|lacked)\s+(?:an?\s+|any\s+|the\s+)?" + _NOUN + r"(?!\s+(?:errors?|mistakes?|flaws?|gaps?))"
            r"|unexplained|unjustified|unargued|unreasoned|one[\s-]line\s+answers?|(?:just|only|merely)\s+(?:a|an|the)\s+"
            r"(?:option\s+)?letter)\b")

# ── (f) tie suppression and positional default (unguarded) ──
_POS = (r"(?:model\s+(?:a|b)|response\s+(?:a|b|1|2|one|two)|the\s+first(?:\s+(?:response|one|model))?"
        r"|the\s+second(?:\s+(?:response|one|model))?)")
F_ENTRIES = (
    ("tie_identical", r"\bties?\b[^.;!?\n]{0,60}?(?<!\bnot\s)\b(?:only|solely|just|exclusively)\s+(?:if|when|where|for|between"
                      r"|in\s+case)\b[^.;!?\n]{0,60}?\bidentical\b"
                      r"|(?<!\bnot\s)(?<!n[’']t\s)\b(?:reserve|restrict)\w*\s+(?:the\s+|a\s+)?ties?\s+(?:verdicts?\s+)?"
                      r"(?:for|to)\s+(?:\w+\s+){0,2}?identical\b"
                      r"|\bties?\s+(?:verdicts?\s+)?(?:is|are)\s+(?:only\s+)?(?:reserved|restricted)\s+(?:for|to)\s+"
                      r"(?:\w+\s+){0,2}?identical\b"),
    ("never_tie", r"\bnever\s+(?:output|declare|give|return|award|call|choose|use|issue|assign)\w*\s+(?:a\s+)?ties?\b"
                  r"|\bties?\s+(?:verdicts?\s+)?(?:is|are)\s+(?:forbidden|prohibited|not\s+allowed|never\s+allowed"
                  r"|not\s+permitted)\b"),
    ("always_winner", r"\balways\s+(?:choose|pick|declare|name|select|give|return|output)\w*\s+(?:a|one)\s+(?:winner"
                      r"|response|model)\b|\bmust\s+(?:always\s+)?(?:choose|pick|declare|name)\s+a\s+winner\b"),
    ("tie_discouraged", r"(?<!\bnot\s)(?<!n[’']t\s)\bavoid\w*\s+(?:a\s+|any\s+|the\s+)?(?:ties?|tie\s+verdicts?)\b"
                        r"|\bties?\s+(?:verdicts?\s+)?(?:is|are|should\s+be|must\s+be)\s+(?:a\s+last\s+resort|avoided"
                        r"|discouraged|rare|exceptional|to\s+be\s+avoided)\b"
                        r"|\bties?\b[^.;!?\n]{0,40}?\b(?:almost|nearly|virtually)\s+never\b"
                        r"|\b(?:rarely|seldom)\s+(?:output|declare|give|use|choose)\w*\s+(?:a\s+)?ties?\b"),
    ("positional_otherwise", r"\b(?:model|response)\s+(?:a|b|1|2|one|two)\s+otherwise\b"
                             r"|\botherwise,?\s+(?:(?:choose|pick|prefer|select|declare|output|favou?r)\s+)?" + _POS + r"\b"),
    ("positional_if_doubt", r"\b(?:if|when|where)\s+(?:still\s+|otherwise\s+|you\s+are\s+|it\s+is\s+)?(?:in\s+doubt"
                            r"|undecided|unsure|uncertain|unclear|tied|equal|a\s+tie)\b,?\s+(?:(?:always|just)\s+)?"
                            r"(?:prefer|pick|choose|select|favou?r|go\s+with|declare|output)\s+" + _POS + r"\b"),
    ("positional_by_default", r"\bby\s+default\b[^.;!?\n]{0,40}?\b" + _POS + r"\b"
                              r"|(?<!\bnor\s)(?<!\bneither\s)(?<!\bor\s)\b" + _POS +
                              r"\s+(?:wins|is\s+chosen|is\s+preferred|is\s+the\s+winner)\s+by\s+default\b"
                              r"|(?<!\bnot\s)(?<!n[’']t\s)\bdefaults?\s+to\s+" + _POS + r"\b"),
)

DEFAULT_OPTS_V54 = {"a_prime": True, "d2": True, "d1_guard": True, "e_guard": True, "e_errors_in": True,
                    "drop_cue_ref": (), "drop_d1": (), "drop_sceptic": (), "drop_e": (), "drop_f": ()}


def build_rules_v54(**opts):
    """-> the jv2-v5-4 rule dict for the given options (defaults = the rule of record); a mutant passes one part off or
    dropped. Pure."""
    o = dict(DEFAULT_OPTS_V54)
    for k in opts:
        if k not in o:
            raise SystemExit("[INDUCE-FITNESS-3] unknown build option %r" % k)
    o.update(opts)
    for key, table in (("drop_cue_ref", CUE_REF_ENTRIES), ("drop_d1", D1_ENTRIES), ("drop_sceptic", SCEPTIC_ENTRIES),
                       ("drop_f", F_ENTRIES), ("drop_e", (("presence_reward", 0), ("depth_reward", 0),
                                                          ("absence_penalty", 0)))):
        unknown = set(o[key]) - {n for n, _r in table}
        if unknown:
            raise SystemExit("[INDUCE-FITNESS-3] %s names unknown part(s) %s" % (key, sorted(unknown)))
    cue_ref = tuple((n, rx) for n, rx in CUE_REF_ENTRIES if n not in o["drop_cue_ref"])
    cue = "(?:" + "|".join(rx for _n, rx in tuple(F.CUE_ENTRIES) + cue_ref) + ")"
    ch = r"(?:(?!%s)[^.;!?\n])" % F.CONTRAST
    start = F._START

    def guarded(core, on):
        if not on:                                   # mutant only: the guard stripped
            return core
        return r"%s(?!%s*%s)%s*?%s" % (start, ch, cue, ch, core)

    def either(a, b, n=100):
        return r"(?:%s%s{0,%d}?%s|%s%s{0,%d}?%s)" % (a, ch, n, b, b, ch, n, a)

    exempt = "".join("(?<!%s)" % re.escape(x) for x in F._ERR_IN) if o["e_errors_in"] else ""
    presence, depth, absence = exempt + _PRESENCE, exempt + _DEPTH, exempt + _ABSENCE
    d1 = tuple((n, guarded(rx, o["d1_guard"])) for n, rx in D1_ENTRIES if n not in o["drop_d1"])
    e_all = (("presence_reward", guarded(either(_REWARD_E, presence), o["e_guard"])),
             ("depth_reward", guarded(either(_REWARD_E, depth), o["e_guard"])),
             ("absence_penalty", guarded(either(_PENALTY_E, absence), o["e_guard"])))
    e = tuple((n, rx) for n, rx in e_all if n not in o["drop_e"])
    sceptic = tuple((n, rx) for n, rx in SCEPTIC_ENTRIES if n not in o["drop_sceptic"])
    f = tuple((n, rx) for n, rx in F_ENTRIES if n not in o["drop_f"])
    return {"version": V5_VERSION, "flags": FLAGS_NAME, "base_version": BASE_VERSION,
            "base_regex_list_sha256": F.REGEX_LIST_SHA256, "base_list": F.regex_list(), "a_prime": bool(o["a_prime"]),
            "split": SPLIT_RX, "cue_ref": [[n, rx] for n, rx in cue_ref], "d1": [[n, rx] for n, rx in d1],
            "d2": {"on": bool(o["d2"]), "trigger": D2_TRIGGER, "sceptic": [[n, rx] for n, rx in sceptic]},
            "e": [[n, rx] for n, rx in e], "f": [[n, rx] for n, rx in f]}


RULES_V54 = build_rules_v54()


def regex_list_v54(rules=None):
    r = RULES_V54 if rules is None else rules
    return {k: r[k] for k in ("version", "flags", "base_version", "base_regex_list_sha256", "base_list", "a_prime",
                              "split", "cue_ref", "d1", "d2", "e", "f")}


def regex_list_v54_json(lst=None):
    return json.dumps(regex_list_v54() if lst is None else lst, sort_keys=True, ensure_ascii=True)


def regex_list_v54_sha256(lst=None):
    return hashlib.sha256(regex_list_v54_json(lst).encode("utf-8")).hexdigest()


REGEX_LIST_SHA256_V54 = "714268738c7593ab45d09daba2934e8780278c82a180f10a78685a283f4ef7d0"   # the pin (regex_list_v54_sha256())


def _first(rx, text):
    m = re.search(rx, text, _FLAGS)
    return None if m is None else m.group(0).strip()[-80:]


def v5(text, rules=None):
    """-> {"pass", "a", "b", "c", "d", "d1", "d2", "e", "f", and the matches of each leg, "a_base"}. The rule of record
    unless a mutant passes its rule dict. Pure; no side effect."""
    r = RULES_V54 if rules is None else rules
    if not isinstance(text, str):
        return {"pass": False, "a": False, "b": False, "c": False, "d": False, "d1": False, "d2": False, "e": False,
                "f": False, "a_base": False, "a_matches": [], "b_matches": [["not_text", repr(type(text))]],
                "c_matches": [], "d1_matches": [], "d2_detail": None, "e_matches": [], "f_matches": []}
    base = F.v5(text)
    d1_m = [[n, s] for n, rx in r["d1"] for s in [_first(rx, text)] if s is not None]
    segs = re.split(r["split"], text, flags=_FLAGS)
    if r["a_prime"]:
        a_m = [m.group(0) for seg in segs if not any(re.search(rx, seg, _FLAGS) for _n, rx in r["d1"])
               for m in re.finditer(F.CORRECTNESS_RX, seg, _FLAGS)]
    else:
        a_m = list(base["a_matches"])
    named = bool(re.search(r["d2"]["trigger"], text, _FLAGS))
    sc = [n for n, rx in r["d2"]["sceptic"] if re.search(rx, text, _FLAGS)]
    d2_ok = bool(not r["d2"]["on"] or not named or sc)
    e_m = [[n, s] for n, rx in r["e"] for s in [_first(rx, text)] if s is not None]
    f_m = [[n, s] for n, rx in r["f"] for s in [_first(rx, text)] if s is not None]
    res = {"a": bool(a_m), "a_base": bool(base["a"]), "b": bool(base["b"]), "c": bool(base["c"]), "d1": bool(not d1_m),
           "d2": d2_ok, "e": bool(not e_m), "f": bool(not f_m), "a_matches": a_m, "b_matches": base["b_matches"],
           "c_matches": base["c_matches"], "d1_matches": d1_m,
           "d2_detail": {"names_reference": named, "sceptic_cues": sc}, "e_matches": e_m, "f_matches": f_m}
    res["d"] = bool(res["d1"] and res["d2"])
    res["pass"] = bool(res["a"] and res["b"] and res["c"] and res["d"] and res["e"] and res["f"])
    return res


def firing(res):
    """The failing legs and the firing pattern names, as a short sorted list (the per-text firing pattern)."""
    out = []
    if not res["a"]:
        out.append("a'")
    out += ["b:" + n for n, _s in res["b_matches"]]
    if not res["c"]:
        out.append("c")
    out += ["d1:" + n for n, _s in res["d1_matches"]]
    if not res["d2"]:
        out.append("d2")
    out += ["e:" + n for n, _s in res["e_matches"]]
    out += ["f:" + n for n, _s in res["f_matches"]]
    return out


def describe(res):
    """One line for the outcome / the attempt record."""
    yn = {True: "YES", False: "NO"}
    d2d = res.get("d2_detail") or {}
    return ("V5 %s (%s): (a') final-answer correctness named outside a reference-agreement clause %s (%d match(es)%s);"
            " (b) form-conditioning patterns matched %d%s; (c) reasoning criterion named %s (%d match(es)); (d1)"
            " reference-as-criterion matched %d%s; (d2) %s; (e) reasoning-presence reward matched %d%s; (f) tie"
            " suppression / positional default matched %d%s" % (
                "PASS" if res["pass"] else "FAIL", V5_VERSION, yn[res["a"]], len(res["a_matches"]),
                (": %r" % res["a_matches"][:3]) if res["a_matches"] else "", len(res["b_matches"]),
                (": %s" % "; ".join("%s %r" % (n, s) for n, s in res["b_matches"])) if res["b_matches"] else "",
                yn[res["c"]], len(res["c_matches"]), len(res["d1_matches"]),
                (": %s" % "; ".join("%s %r" % (n, s) for n, s in res["d1_matches"])) if res["d1_matches"] else "",
                ("PASS (names 'reference': %s; sceptic cues %s)" % (d2d.get("names_reference"), d2d.get("sceptic_cues"))
                 if res["d2"] else "FAIL (names 'reference' with no sceptic cue)"),
                len(res["e_matches"]),
                (": %s" % "; ".join("%s %r" % (n, s) for n, s in res["e_matches"])) if res["e_matches"] else "",
                len(res["f_matches"]),
                (": %s" % "; ".join("%s %r" % (n, s) for n, s in res["f_matches"])) if res["f_matches"] else ""))
