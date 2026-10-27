"""judge_v2.leakage: the PRE-CALL FULL-PAYLOAD leakage scan (judge proposal §3 failure 10; SYNTHESIS G6).

The BFCL assert (80caf70) scanned the task statement only. This scan reads THE WHOLE BODY: it decodes the exact bytes
that would be posted and scans every message content (the system turn with its rubric, the user turn with the question,
the reference block and BOTH traces). It REFUSES (raise SystemExit, never an assert: it holds under python -O) when:

  structure        the body is not exactly the recipe's recomposition from declared components: body keys model /
                   max_tokens / messages, two messages [system, user], system == payload.build_system(rubric), user ==
                   rejudge_grok.build_user_prompt(query, shown-first trace, shown-second trace) for the payload's order.
                   So no undeclared text can ride in the body; everything below is scanned inside declared slots.
  inputs           payload.check_inputs fails: the question does not re-key to the judged stem_key; the reference is
                   not question-level, is bound to a contestant's response (oracle-class), or is keyed to another
                   variant / stem (the reference result for the WRONG SIDE, R9).
  reference_count  the reference marker appears in the user turn other than exactly once with a reference (zero without
                   one), or anywhere in the system turn (two references, or a reference smuggled into a trace).
  marker:<rule>    a machine-rendered verdict field or tag anywhere in the body (MARKER_RULES: is_correct, gt_answer,
                   ground_truth, answer_key, checker_* fields, per-response pass vectors, bracketed verdict / checker /
                   grader / gold / correct-answer tags, JSON pass/correct booleans). Natural-language phrases ("the correct
                   answer is") are NOT rules: a model's own answer says that.
  side_material    any per-side verdict or checker outcome supplied by the caller (LeakMaterial.side: contestant ->
                   rendered strings, as the data layer stores them) appears anywhere in the body, for EITHER side.
  key_material     any rendered key annotation supplied by the caller appears anywhere in the body.
  wrong_reference  a reference minted for another variant, another side or another contestant (LeakMaterial.
                   other_references) appears anywhere in the body.
Material strings are compared casefolded with whitespace collapsed; a string shorter than MIN_MATERIAL characters after
normalisation cannot be scanned by substring and is REFUSED as unscannable (fail closed: render it with its context).
[ADDED 2026-09-24 on the delta review 16212c4 D3: marker rules for the key fields gt_raw and answer_text (is_correct_mathfix
is under is_correct), so the short key forms below MIN_MATERIAL are refused by rule; ScanStats counts key, side and
other-reference material separately.]
The scan prints nothing on a pass; ScanStats counts every scan and every hit by rule, and the writer prints them.
[ADDED 2026-09-24 on READY_archv2_EJ C2 / C3: ScanStats also counts scans WITH and WITHOUT material; the writer refuses a
run whose scan counts do not cover every pending slot and every post, and (unless material NONE is declared) any scan
without material. The material itself is built by loader.py from eval_view rows.]
"""
import json
import re
from collections import Counter
from dataclasses import dataclass, field

from ._base import REFERENCE_MARKER, refuse, rj
from . import payload as P

MIN_MATERIAL = 12

MARKER_RULES = (
    ("is_correct", r"\bis_correct(?:_mathfix)?\b"),
    ("gt_answer", r"\bgt_answer\b"),
    ("ground_truth", r"\bground_truth\b"),
    ("answer_key", r"\banswer_key\b"),
    # D3 (delta review 16212c4): the data_v2 key fields by name; catches the short forms ("gt_raw: B", "gt_raw=B") that are
    # below MIN_MATERIAL and so cannot be material. is_correct_mathfix is covered by the is_correct rule above.
    ("gt_raw", r"\bgt_raw\b"),
    ("answer_text", r"\banswer_text\b"),
    ("checker_field", r"\bchecker_(?:output|outcome|result|verdict|pass(?:ed)?)\b"),
    ("pass_vector", r"\b(?:pass_vector|follow_instruction_list|inst_level_(?:strict|loose)_acc|prompt_level_(?:strict|loose)_acc)\b"),
    ("verdict_tag", r"\[\s*(?:checker|verdict|grader|gold|ground truth|answer key|correct answer|test results?)\b[^\]\n]{0,120}\]"),
    ("json_pass", r"\"(?:passed|is_pass|correct|success)\"\s*:\s*(?:true|false|0|1)\b"),
)
_RULES = tuple((name, re.compile(rx, re.I)) for name, rx in MARKER_RULES)
_REF_HEAD = re.compile(r"\[\s*Reference solution", re.I)


@dataclass
class LeakMaterial:
    side: dict = field(default_factory=dict)            # contestant -> [rendered per-side verdicts / checker outcomes]
    key: list = field(default_factory=list)             # rendered key annotations
    other_references: list = field(default_factory=list)  # references of other variants / sides / contestants


@dataclass
class ScanStats:
    scanned: int = 0
    refused: int = 0
    with_material: int = 0          # scans that carried a non-empty LeakMaterial (C3: printed on every run)
    without_material: int = 0
    with_key: int = 0               # D3: per kind (a side string alone must not look like key coverage)
    with_side: int = 0
    with_other: int = 0
    hits: Counter = field(default_factory=Counter)

    def line(self):
        return ("[LEAK-SCAN] payloads scanned %d (with material %d, without material %d; with key material %d, with side"
                " material %d, with other-reference material %d), refused %d, hits by rule %s" % (
                    self.scanned, self.with_material, self.without_material, self.with_key, self.with_side,
                    self.with_other, self.refused, json.dumps(dict(sorted(self.hits.items())))))


def _has_material(m):
    return m is not None and bool(m.key or m.other_references or any(m.side.values()))


def _norm(s):
    return " ".join(s.casefold().split())


def _material(strings, what):
    out = []
    for s in strings:
        if not isinstance(s, str):
            refuse("leak material %s: %r is not a string" % (what, s))
        n = _norm(s)
        if len(n) < MIN_MATERIAL:
            refuse("leak material %s: %r is %d characters after normalisation (< %d): unscannable by substring; render it"
                   " with its context" % (what, s, len(n), MIN_MATERIAL))
        out.append(n)
    return out


def _where(components, needle_norm=None, rx=None):
    locs = []
    for name, text in components:
        if needle_norm is not None and needle_norm in _norm(text):
            locs.append(name)
        if rx is not None and rx.search(text):
            locs.append(name)
    return locs


def scan(pl, inp, rubric, material=None, stats=None):
    """Scan one payload before it can be posted: any hit REFUSES (raise SystemExit); a pass returns []. stats, when
    given, counts the scan and its hits by rule before the refusal."""
    hits = scan_hits(pl, inp, rubric, material)
    if stats is not None:
        stats.scanned += 1
        if _has_material(material):
            stats.with_material += 1
            stats.with_key += bool(material.key)
            stats.with_side += bool(any(material.side.values()))
            stats.with_other += bool(material.other_references)
        else:
            stats.without_material += 1
        for h in hits:
            stats.hits[h[0]] += 1
        if hits:
            stats.refused += 1
    if hits:
        refuse("LEAKAGE: payload %s order %d REFUSED before any call: %s" % (
            pl.match_id, pl.order, "; ".join("%s in %s" % (r, ",".join(w) or "body") for r, w in hits)))
    return hits


def scan_hits(pl, inp, rubric, material=None):
    """The hits of one payload as [(rule, [components])]; no refusal here (scan() refuses)."""
    material = material or LeakMaterial()
    hits = []
    # inputs (R9, failure 12, failure 14): payload.check_inputs refuses by SystemExit; converted to a hit
    try:
        P.check_inputs(inp, rubric)
    except SystemExit as e:
        hits.append(("inputs", [str(e)[:160]]))
    # structure: the whole body decoded and recomposed from declared components
    try:
        d = json.loads(pl.body.decode("utf-8"))
        msgs = d.get("messages") if isinstance(d, dict) else None
        ok_shape = (isinstance(d, dict) and list(d.keys()) == P.BODY_KEYS and isinstance(msgs, list) and len(msgs) == 2
                    and [m.get("role") for m in msgs] == ["system", "user"])
    except (UnicodeDecodeError, ValueError):
        d, msgs, ok_shape = None, None, False
    if not ok_shape:
        hits.append(("structure", ["body"]))
        return hits
    system, user = msgs[0].get("content", ""), msgs[1].get("content", "")
    if pl.order == 1:
        tf, ts = inp.trace_a, inp.trace_b
    elif pl.order == 2:
        tf, ts = inp.trace_b, inp.trace_a
    else:
        tf = ts = None
    try:
        exp_system = P.build_system(rubric)
    except SystemExit:
        exp_system = None
    exp_query = P.build_query(inp)
    exp_user = rj.build_user_prompt(exp_query, tf, ts) if tf is not None else None
    if system != exp_system or user != exp_user:
        hits.append(("structure", [n for n, a, b in (("system", system, exp_system), ("user", user, exp_user)) if a != b]))
    components = [("system", system), ("question", inp.question), ("reference", inp.reference.rendered if inp.reference
                                                                     else ""), ("trace_first", tf or ""),
                  ("trace_second", ts or ""), ("user", user)]
    whole = system + "\n" + user
    # reference count
    want = 1 if inp.reference is not None else 0
    n_marker_user = user.count(REFERENCE_MARKER)
    n_head_user = len(_REF_HEAD.findall(user))
    if n_marker_user != want or n_head_user != want or REFERENCE_MARKER in system or _REF_HEAD.search(system):
        hits.append(("reference_count", ["user %d marker(s) / %d head(s), want %d; system %d" % (
            n_marker_user, n_head_user, want, len(_REF_HEAD.findall(system)))]))
    # machine-rendered verdict markers, anywhere in the body
    for name, rx in _RULES:
        if rx.search(whole):
            hits.append(("marker:" + name, _where(components[:-1], rx=rx) or ["user"]))
    wn = _norm(whole)
    for contestant, strings in sorted(material.side.items()):
        for s in _material(strings, "side[%s]" % contestant):
            if s in wn:
                hits.append(("side_material", ["%s: %s" % (contestant, ",".join(_where(components[:-1], s)) or "user")]))
    for s in _material(material.key, "key"):
        if s in wn:
            hits.append(("key_material", _where(components[:-1], s) or ["user"]))
    own = _norm(inp.reference.rendered) if inp.reference is not None else None
    for s in _material(material.other_references, "other_references"):
        if s != own and s in wn:
            hits.append(("wrong_reference", _where(components[:-1], s) or ["user"]))
    return hits
