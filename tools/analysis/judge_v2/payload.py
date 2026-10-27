"""judge_v2.payload: the v2 judge payload (ARCH-v2 Stage J; judge proposal §2.1-§2.3, §2.8; SYNTHESIS R9).

THE RECIPE, AS BUILT HERE (zero calls; nothing is posted by this module):
  judge        grok-4-1-fast-non-reasoning (JUDGE_REQUESTED), provider azure, through rejudge_reasoning (rule 9)
  system       prompt_v2.v2_system_template()  .replace("$systemPrompt", FIXED_SYSTEM_PERSONA)
                                               .replace("$rubric", rubric.rubric)  + "\n\n" + SCHEMA_INSTRUCTION
               i.e. stack_judge.system_for under PROMPT = "v2", with the anchor rubric REPLACED by the corpus-type rubric
               artefact of judge_v2.induction (author's decision 2026-09-23 (2): re-induced from gen_view only; a recipe
               component, not a reopening of the rubric-value line). The artefact is sha-verified on load.
               [CORRECTED 2026-09-24 by the registrar's ruling on E-J choice 2 (4aac08e, programme L15159-L15177): the
               induced artefact fills the RUBRIC SLOT ONLY. The $systemPrompt slot carries the FIXED persona of record
               (_base.FIXED_SYSTEM_PERSONA = rubric_value_contrast.GENERIC_SYSTEM, as STACK-NORUBRIC fills it, pinned by
               sha256); the v2 mechanics text is the template itself. An artefact carrying a system_prompt field, or any
               field outside the rubric artefact's keys, is REFUSED on load.]
  user         rejudge_grok.build_user_prompt(query, trace_first, trace_second), in BOTH presentation orders
               (order 1 shows contestant A first, order 2 shows B first)
  query        the judged variant's question text + "\n\n" + REFERENCE_MARKER + "\n" + reference.rendered, the marker of
               rejudge_reference.with_reference (U+2014); no reference -> the question alone (reference_state NONE)
  reference    ONE question-level reference keyed by VARIANT (R9): reference.variant_id must equal the judged variant and
               reference.stem_key the judged stem_key; the question text re-keys to the same stem_key (judge failure 12,
               extended to the variant). Kinds: cached_solve | checker_output. A reference bound to a contestant's
               response (oracle-class, e.g. a per-response pass vector) is REFUSED.
  body         rejudge_reasoning.payload_bytes(system, user): THE one builder (json.dumps, key order model / max_tokens /
               messages), with rr.JUDGE_MODEL = JUDGE_REQUESTED, rr.MAX_TOKENS = 8192, rr.TEMPERATURE = None; the
               temperature key is therefore ABSENT from the body and recorded as the literal "omitted" (plan
               Amendment 1 D2 / W2; programme L15037). The decoded body is re-checked: exactly the keys model /
               max_tokens / messages, two messages (system, user), no temperature.
  stored       the full body bytes, sha256(body) (payload_sha256), and the zlib-compressed body (data_v2.verdicts
               stores body_zlib; judge §2.8 names zstd, which is not in the standard library: codec recorded)

G6 (Kotlin parity) is a TODO HOOK here: g6_kotlin_parity() compares a {(match_id, order): sha} map from the Kotlin path when
one is supplied and otherwise reports status TODO. THE KOTLIN CODE THAT MUST MATCH, byte for byte:
  src/main/kotlin/taxonomy/prompts/StackV2JudgeRecipe.kt  V2_SYSTEM_TEMPLATE, USER_TEMPLATE, SCHEMA_INSTRUCTION,
      REFERENCE_MARKER, withReference, buildSystem, buildUser, payloadBody (key order, temperature omitted when null)
  src/main/kotlin/taxonomy/operations/PythonJson.kt       json.dumps defaults (", " / ": " separators, ensure_ascii)
  src/main/kotlin/taxonomy/service/TracePreparation.kt    rejudge_grok.robust_trace (the traces this module is handed)
  and, NOT YET PRESENT in Kotlin (the v2 path needs them before G6 can pass): a reference keyed by variant_id (RecipeKit
  keys by question id), the corpus-type rubric slot with the FIXED GENERIC_SYSTEM persona in $systemPrompt (buildSystem takes
  the anchor persona and rubric from the kit), and the data_v2
  verdict schema as the write target (R8: JudgeCallStore -> data_v2.verdicts).
[ADDED 2026-09-24 on READY_archv2_EJ C4 / C7 and the reference-row ruling: Reference carries the SOLVER's options ordering
(options_ordered_sha), its item and its v2 side; MatchInputs carries the question block's ordering, the item and the
loader's provenance token. check_inputs also refuses a reference indexed in another ordering than the question block's,
a reference of another item, and a reference whose v2 side is not EVAL. CONTRACT_TYPES lives here (shared).]
[CORRECTED 2026-09-24 by the D5 MIXED ruling, insertion only: the judge never sees an options list; the question block is
the stem only. "The question block's ordering" above means the ordering the contestants' traces are resolved in, and both
it and Reference.options_ordered_sha now hold loader.ordering_key() (option lists equal after str(x).strip()), not a
byte sha; "MIXED:a|b" when the two contestants' orderings differ (allowed only without a reference).]
"""
import hashlib
import json
import zlib
from dataclasses import dataclass, field
from typing import Optional

from ._base import (FIXED_SYSTEM_PERSONA, REFERENCE_MARKER, SCHEMA_INSTRUCTION, TEMPLATE_SHAS, V2_SYSTEM_TEMPLATE, dv2c,
                    refuse, rj, rr, sha256_text)

JUDGE_REQUESTED = "grok-4-1-fast-non-reasoning"
PROVIDER = "azure"
CAP = 8192
TEMPERATURE_LABEL = "omitted"
CORPUS_TYPES = ("mcq", "math", "instruction", "agentic")
REFERENCE_KINDS = ("cached_solve", "checker_output")
# data_v2 contract_id -> corpus type (ruled 4aac08e choice 3: an unknown contract is refused; agentic has none yet); shared by
# loader.py and induction.py
CONTRACT_TYPES = {"MC_LETTER": "mcq", "IMPORTED:acc_norm": "mcq", "IMPORTED:exact_match": "math",
                  "IMPORTED:prompt_level_strict_acc": "instruction"}
BODY_KEYS = ["model", "max_tokens", "messages"]
BODY_CODEC = "zlib"
PAYLOAD_VERSION = "jv2-payload-2"   # 2: the rubric artefact fills the rubric slot only (ruling 4aac08e)
RUBRIC_KEYS = frozenset({"corpus_type", "rubric", "rubric_sha256"})
RUBRIC_OPTIONAL_KEYS = frozenset({"artefact_sha256", "of_record", "manifest"})


@dataclass(frozen=True)
class Reference:
    row_id: str
    variant_id: str
    stem_key: str
    vintage: str
    kind: str
    rendered: str                       # the text after the marker, e.g. "(C) option text" or a normalised answer
    bound_response: Optional[str] = None  # a contestant response id: oracle-class, REFUSED
    # added 2026-09-24 (READY_archv2_EJ C4 + the reference-row ruling): the ordered options the SOLVER saw (the
    # options_ordered_sha of the solver's response row; the letter is indexed there, never in options_sorted), the
    # reference's item, and its v2 side (the split's side of its item; side_at_mint is legacy free text, never a v2 side)
    options_ordered_sha: Optional[str] = None
    item_id: Optional[str] = None
    side_v2: Optional[str] = None


@dataclass(frozen=True)
class RubricArtifact:
    corpus_type: str
    rubric: str
    rubric_sha256: str                  # sha256(rubric), checked on load
    artefact_id: str = ""               # the induction manifest's artefact sha (provenance)


@dataclass(frozen=True)
class MatchInputs:
    match_id: str
    variant_id: str
    stem_key: str
    component_id: Optional[str]
    corpus_type: str
    question: str
    contestant_a: str
    contestant_b: str
    trace_a: str
    trace_b: str
    reference: Optional[Reference]
    batch_id: Optional[str] = None
    # added 2026-09-24 (C4; D5 ruling): the ordering key of the options the contestants' traces are resolved in
    # (loader.ordering_key; "MIXED:a|b" when they differ; the judge sees no options list), the judged item, and the
    # loader's provenance token (writer.py refuses a spec without a valid one)
    question_options_sha: Optional[str] = None
    item_id: Optional[str] = None
    provenance: Optional[str] = None


@dataclass(frozen=True)
class Payload:
    match_id: str
    order: int
    shown_first: str
    shown_second: str
    trace_first: str
    trace_second: str
    query: str
    system: str
    user: str
    body: bytes = field(repr=False)
    sha256: str = ""
    body_zlib: bytes = field(default=b"", repr=False)
    system_sha: str = ""
    user_sha: str = ""


def rubric_sha(rubric):
    return sha256_text(rubric)


def load_rubric(d):
    """A RubricArtifact from the induction artefact dict (judge_v2.induction writes it); the sha is RE-COMPUTED."""
    if not isinstance(d, dict):
        refuse("rubric artefact is not a dict")
    if "system_prompt" in d:
        refuse("rubric artefact carries a system_prompt field: the induced artefact fills the RUBRIC SLOT ONLY; the system"
               " prompt is the fixed text of record (ruling 4aac08e)")
    extra = sorted(set(d) - RUBRIC_KEYS - RUBRIC_OPTIONAL_KEYS)
    if extra:
        refuse("rubric artefact carries unknown field(s) %s" % extra)
    for k in sorted(RUBRIC_KEYS):
        if not isinstance(d.get(k), str) or not d[k]:
            refuse("rubric artefact lacks %s" % k)
    if d["corpus_type"] not in CORPUS_TYPES:
        refuse("rubric artefact corpus_type %r is not one of %s" % (d["corpus_type"], CORPUS_TYPES))
    for ph in ("$systemPrompt", "$rubric"):
        if ph in d["rubric"]:
            refuse("rubric artefact text carries the template placeholder %r" % ph)
    got = rubric_sha(d["rubric"])
    if got != d["rubric_sha256"]:
        refuse("rubric artefact sha256 %s != its recorded %s" % (got, d["rubric_sha256"]))
    return RubricArtifact(d["corpus_type"], d["rubric"], d["rubric_sha256"], d.get("artefact_sha256", ""))


def configure_rr():
    """Point the one body builder (and call_judge_full) at the v2 judge. Process-global, as stack_judge.run does."""
    rr.PROVIDER = PROVIDER
    rr.JUDGE_MODEL = JUDGE_REQUESTED
    rr.MAX_TOKENS = CAP
    rr.TEMPERATURE = None
    verify_rr_config()


def verify_rr_config():
    bad = []
    if rr.PROVIDER != PROVIDER:
        bad.append("PROVIDER %r" % rr.PROVIDER)
    if rr.JUDGE_MODEL != JUDGE_REQUESTED:
        bad.append("JUDGE_MODEL %r" % rr.JUDGE_MODEL)
    if rr.MAX_TOKENS != CAP:
        bad.append("MAX_TOKENS %r" % rr.MAX_TOKENS)
    if rr.TEMPERATURE is not None:
        bad.append("TEMPERATURE %r (must be None: omitted)" % rr.TEMPERATURE)
    if bad:
        refuse("rejudge_reasoning is not configured for the v2 judge: %s (call payload.configure_rr())" % "; ".join(bad))


def render_mcq(letter, option_text):
    """rejudge_reference.with_reference's "(letter) text" rendering."""
    return "(%s) %s" % (letter, option_text)


def build_system(rubric):
    if not isinstance(rubric, RubricArtifact):
        refuse("build_system needs a RubricArtifact (load_rubric), got %r" % type(rubric).__name__)
    return V2_SYSTEM_TEMPLATE.replace("$systemPrompt", FIXED_SYSTEM_PERSONA).replace("$rubric", rubric.rubric) + \
        "\n\n" + SCHEMA_INSTRUCTION


_KEYS = None


def _stem_key(text):
    global _KEYS
    if _KEYS is None:
        _KEYS = dv2c.KeyCache()
    return _KEYS.stem(text)


def check_inputs(inp, rubric):
    """The R9 / failure-12 checks and the input shape; every failure refuses."""
    if inp.corpus_type not in CORPUS_TYPES:
        refuse("match %s: corpus_type %r is not one of %s" % (inp.match_id, inp.corpus_type, CORPUS_TYPES))
    if rubric.corpus_type != inp.corpus_type:
        refuse("match %s: the rubric is for %r, the match is %r" % (inp.match_id, rubric.corpus_type, inp.corpus_type))
    if inp.contestant_a == inp.contestant_b:
        refuse("match %s: contestant_a == contestant_b" % inp.match_id)
    for name in ("question", "trace_a", "trace_b"):
        if not isinstance(getattr(inp, name), str) or not getattr(inp, name).strip():
            refuse("match %s: %s is empty" % (inp.match_id, name))
    if not inp.variant_id.startswith("v:"):
        refuse("match %s: variant_id %r is not a data_v2 variant id" % (inp.match_id, inp.variant_id))
    got = _stem_key(inp.question)
    if got != inp.stem_key:
        refuse("match %s: the question re-keys to stem_key %s, not the judged row's %s (failure 12)" % (inp.match_id, got,
                                                                                                     inp.stem_key))
    ref = inp.reference
    if ref is not None:
        if ref.kind not in REFERENCE_KINDS:
            refuse("match %s: reference kind %r is not question-level (%s)" % (inp.match_id, ref.kind, REFERENCE_KINDS))
        if ref.bound_response is not None:
            refuse("match %s: reference %s is bound to response %s: a per-response reference is oracle-class (failure 14)"
                   % (inp.match_id, ref.row_id, ref.bound_response))
        if ref.variant_id != inp.variant_id:
            refuse("match %s: reference %s is keyed to variant %s, the judged variant is %s (R9)" % (inp.match_id, ref.row_id,
                                                                                                  ref.variant_id, inp.variant_id))
        if ref.stem_key != inp.stem_key:
            refuse("match %s: reference %s carries stem_key %s, the judged row %s" % (inp.match_id, ref.row_id, ref.stem_key,
                                                                                   inp.stem_key))
        if not ref.rendered.strip() or not ref.vintage or not ref.row_id:
            refuse("match %s: reference %s is empty or lacks a vintage / row id" % (inp.match_id, ref.row_id))
        if ref.options_ordered_sha != inp.question_options_sha:
            refuse("match %s: reference %s is indexed in options ordering %s, the contestants' traces are resolved in %s"
                   % (inp.match_id, ref.row_id, ref.options_ordered_sha, inp.question_options_sha))
        if ref.item_id is not None and inp.item_id is not None and ref.item_id != inp.item_id:
            refuse("match %s: reference %s belongs to item %s, the judged item is %s" % (inp.match_id, ref.row_id, ref.item_id,
                                                                                      inp.item_id))
        if ref.side_v2 is not None and ref.side_v2 != "EVAL":
            refuse("match %s: reference %s sits on v2 side %r, not EVAL" % (inp.match_id, ref.row_id, ref.side_v2))


def build_query(inp):
    if inp.reference is None:
        return inp.question
    return inp.question + "\n\n" + REFERENCE_MARKER + "\n" + inp.reference.rendered


def _check_body(body, system, user):
    try:
        d = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as e:
        refuse("the built body does not decode: %s" % e)
    if list(d.keys()) != BODY_KEYS:
        refuse("the built body carries keys %s, not %s (temperature must be OMITTED)" % (list(d.keys()), BODY_KEYS))
    if d["model"] != JUDGE_REQUESTED or d["max_tokens"] != CAP:
        refuse("the built body names model %r cap %r" % (d["model"], d["max_tokens"]))
    msgs = d["messages"]
    if [m.get("role") for m in msgs] != ["system", "user"] or [sorted(m) for m in msgs] != [["content", "role"]] * 2:
        refuse("the built body's messages are not exactly [system, user]")
    if msgs[0]["content"] != system or msgs[1]["content"] != user:
        refuse("the built body's messages differ from the assembled system / user")
    return d


def build_payload(inp, rubric, order):
    """One presentation order's payload. order 1 shows A first; order 2 shows B first."""
    if order not in (1, 2):
        refuse("order %r is not 1 or 2" % (order,))
    verify_rr_config()
    check_inputs(inp, rubric)
    system = build_system(rubric)
    query = build_query(inp)
    if order == 1:
        first, second, tf, ts = inp.contestant_a, inp.contestant_b, inp.trace_a, inp.trace_b
    else:
        first, second, tf, ts = inp.contestant_b, inp.contestant_a, inp.trace_b, inp.trace_a
    user = rj.build_user_prompt(query, tf, ts)
    body = rr.payload_bytes(system, user)
    _check_body(body, system, user)
    return Payload(match_id=inp.match_id, order=order, shown_first=first, shown_second=second, trace_first=tf,
                   trace_second=ts, query=query, system=system, user=user, body=body,
                   sha256=hashlib.sha256(body).hexdigest(), body_zlib=zlib.compress(body, 6),
                   system_sha=sha256_text(system), user_sha=sha256_text(user))


def build_dual(inp, rubric):
    return build_payload(inp, rubric, 1), build_payload(inp, rubric, 2)


def recipe_manifest(rubric):
    """The recipe's identity for run_meta (hash kinds named)."""
    return {"judge_requested": JUDGE_REQUESTED, "provider": PROVIDER, "max_tokens": CAP,
            "temperature_label": TEMPERATURE_LABEL, "payload_version": PAYLOAD_VERSION, "body_codec": BODY_CODEC,
            "system_template_sha": "sha256:" + TEMPLATE_SHAS["v2_system_template"],
            "user_template_sha": "sha256:" + TEMPLATE_SHAS["user_template"],
            "schema_sha": "sha256:" + TEMPLATE_SHAS["schema_instruction"],
            "reference_marker_sha": "sha256:" + TEMPLATE_SHAS["reference_marker"],
            "system_persona_sha": "sha256:" + TEMPLATE_SHAS["fixed_system_persona"],
            "rubric_sha": "sha256:" + rubric.rubric_sha256, "rubric_corpus_type": rubric.corpus_type,
            "rubric_artefact": rubric.artefact_id}


def g6_kotlin_parity(payloads, kotlin_shas=None):
    """G6 TODO HOOK. payloads: iterable of Payload; kotlin_shas: {(match_id, order): sha256 hex} from the Kotlin v2 path.
    Without kotlin_shas the status is TODO (never a pass). With it: the count of equal / different / missing shas; status
    PASS only when every payload has an equal Kotlin sha."""
    ps = list(payloads)
    if kotlin_shas is None:
        return {"status": "TODO", "n": len(ps), "reason": "no Kotlin v2 path yet (see payload.py docstring: variant-keyed"
                " reference, corpus-type rubric slot, data_v2 write target)"}
    eq = diff = missing = 0
    for p in ps:
        k = kotlin_shas.get((p.match_id, p.order))
        if k is None:
            missing += 1
        elif k == p.sha256:
            eq += 1
        else:
            diff += 1
    return {"status": "PASS" if (ps and eq == len(ps)) else "FAIL", "n": len(ps), "equal": eq, "different": diff,
            "missing": missing}
