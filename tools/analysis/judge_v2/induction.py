"""judge_v2.induction: the v2 judge rubric, RE-INDUCED from the generation side only, one fixed text per corpus type.

AUTHORITY. Author's decision 2026-09-23 (2) (programme L15070-L15084): the rubric is RE-INDUCED from the GENERATION SIDE
ONLY (the physical gen_view; CK-CLOSE-v1 with its four conditions; the loader guard): NOTHING INDUCED MAY SEE AN EVAL
ITEM OR A SENTINEL. The registrar's reading: a RECIPE COMPONENT rebuilt clean, NOT a reopening of the closed rubric-value
line; no rubric-value claim follows from this module.

READS ONLY through data_v2.views.open_generation("induce", path, expect_sha256): a sealed file whose own meta says
view_kind = gen (TRAIN + GATE rows only, no EVAL text; the salted EVAL key set). No other opener, no sqlite3.connect.

INPUTS. select_inputs(): the variants of the corpus type (CONTRACT_TYPES maps the data_v2 contract_id; an unknown
contract is refused, and 'agentic' has no gen_view contract yet, so its induction is refused), on the sides admitted
(DEFAULT_SIDES = TRAIN only: GATE is generation-side but is kept out by default so the construction gates see nothing
induction saw; a registration may widen it), ordered by sha256(seed US variant_id), the first n. The examples show the
stem (and the options for mcq); NEVER an answer, a label or a response.

THE CONTENT-KEY ASSERT (assert_induction_inputs), on EVERY text handed to the model, whatever selected it:
  (a) data_v2.views.assert_not_eval: split_side.stem_key(text), salted, is NOT in gen_view's EVAL key set. Sentinels are
      EVAL units in the v2 split (split.py condition 1: the routing-only EVAL units are passed as sentinels), so the set
      covers them.
  (b) the same content key names a gen_view item on an admitted side (side table): a text whose key is absent (another
      corpus, another pool's sentinel, an EVAL item whose hash a stale view lacks) is REFUSED too.
  Both refuse by raise SystemExit (python -O safe). The check keys the TEXT; an id handed beside it is never trusted.

THE MODEL CALL IS INJECTED (model_call(system, user) -> str; attribute .provenance: dict). NO LIVE INDUCTION IS BUILT
here: StubInducer is the only implementation, and its artefacts say "STUB, NOT OF RECORD". A live inducer (through
rejudge_reasoning.call_judge_full, its own cache, its registration) is an open item.

OUTPUT. The model's reply must be JSON {"rubric": str} and nothing else. A verbatim-copy audit refuses a reply that
carries any SHINGLE-token run of an input stem or option (a corpus-type rubric carries no item content). The artefact:
corpus_type, rubric, rubric_sha256 (= payload.rubric_sha), and a PROVENANCE MANIFEST: gen_view file
basename + sha256-bytes + its meta (of_record, seed, split sha, views blob, content check, eval key count), the sides, n,
seed, sha256 of the sorted input variant ids, the content-key check counts, the induction prompt shas, the module blobs,
the model provenance; artefact_sha256 over the canonical JSON of everything else. write_artefact() opens with mode "x".

[CORRECTED 2026-09-24 by the registrar's ruling on E-J choice 2 (4aac08e, programme L15159-L15177): the induced artefact
fills the RUBRIC SLOT ONLY; the system prompt stays the fixed v2 text of record (payload.build_system with
_base.FIXED_SYSTEM_PERSONA). Induction therefore outputs ONLY the rubric: a reply carrying a system_prompt (or any key
other than "rubric") is REFUSED, and payload.load_rubric refuses an artefact carrying a system_prompt field. Inducing the
system prompt would change measured recipe mechanics (J3-R, STACK-v2); a per-cell induced judge prompt would be its own
registered choice.]

[CORRECTED 2026-09-24 on READY_archv2_EJ (2aba3ab) C5 / C6 / C7 and the registration ARCH-V2-INDUCE-SELECT-1 (0346d60),
insertion only:
  - THE SEED IS REQUIRED AND REGISTERED: induce() and select_inputs() take the seed as a parameter with NO default; the
    version-string seeds ("jv2-induce-1/2/3") are REFUSED. A record induction names its registration
    (REGISTERED_SEEDS: ARCH-V2-INDUCE-SELECT-1 -> "ARCHV2-INDUCE-1:5abb79f55c3719d122b5310151f975493609f37b") and the
    seed must equal it; any other seed must start with "DEV-" and its artefact says "DEV, NOT OF RECORD". The selection
    on REAL data runs once, after the real split draw (not here: the selftest runs it on the synthetic fixture only). The
    manifest records input_variant_ids_sha256 (sorted set) and input_variant_ids_ordered_sha256 (selection order).
  - TRAIN ONLY: the sides are fixed to ("TRAIN",); any other sides value (GATE included) is REFUSED, and select_inputs
    prints and records the GATE and EVAL-absent counts it excluded (the witness). EVAL and sentinels are never inputs.
  - OPTIONS ARE CONTENT-KEY CHECKED: leg (a) (assert_not_eval) runs on every stem AND every option text with a non-empty
    norm-v1 form (leg (b) keys stems only: an option is not an item). The docstring's earlier "they pass the SAME
    content-key assert" was FALSE for options (probe D).
  - (see the next bracket for the population filter)
  - CALLER INPUTS ARE BOUND TO gen_view: each caller-supplied input must name a gen_view variant_id, and its stem, options
    and contract must EQUAL that row's (stem, options_sorted_json, contract_id); the same check runs on the selected
    path.]
[CORRECTED 2026-09-24 by the judge-design-specialist's ruling on ARCH-V2-INDUCE-RUBRIC-1 finding 1 (eabbf45, programme
L15996-L16007), insertion only; a PRE-CALL correction, the registered seed kept: select_inputs COLLAPSES the candidate rows
(one per (corpus_version, variant_id)) to distinct variant_id, asserting that every duplicate is identical in (stem,
options_sorted_json, contract_id) and REFUSING otherwise; sorts by the UNCHANGED key sha256(seed US variant_id); and keeps
the FIRST variant of each COMPONENT (the split's side.component_id: CK-CLOSE-v1's content unit) until n. The witness adds
candidate_rows, distinct_variants, duplicates_collapsed and skipped_by_component ("train_candidates" is now the distinct
count). check_inputs_bound fetches ALL rows of a variant and requires them identical.]
[ADDED 2026-09-24 by the ruling on ARCH-V2-INDUCE-RUBRIC-1 READY C4 (coordinator), insertion only: select_inputs and
induce take an optional POPULATION {corpus_version, contracts}; with it, only variant rows of that corpus version and
those contracts (and side TRAIN) are candidates, and the witness counts the TRAIN rows excluded by (corpus version,
contract). The seed, the sort key, the dedup, the component rule and n are unchanged. The default (None) keeps the
earlier behaviour. The artefact manifest records the population and an artefact label.]
[ADDED 2026-09-24 by the ruling D1 (overlap exclusion), insertion only: select_inputs takes an optional EXCLUDE set of
variant ids (the zero-call overlap audit's list, judge_v2.induce_overlap_audit): the unchanged order is walked, an excluded
variant is skipped BEFORE the component rule (it claims no component), and the next variants REPLACE it until n; the
witness adds excluded_skipped_in_order and last_rank (the 1-based rank of the last selected variant in the order).]
[CORRECTED 2026-09-24 under ARCH-V2-INDUCE-RUBRIC-2 (registered 7e13897, programme L16326-L16348; the F1 ruling
L16274-L16324), insertion only; INDUCTION_VERSION jv2-induce-4. EXACTLY the two registered changes:
  (1) INDUCTION_SYSTEM states what the judge sees (the question with lettered options, a reference solution that may be
      wrong, the two full free-form responses, usually step-by-step reasoning ending in one option letter, possibly
      truncated, empty or with no letter); the rubric decides correctness of the final answer first, then soundness of
      the supporting reasoning; it must not reward or penalise length, formatting, or the presence or absence of an
      explanation. The genericity and no-domain-facts clauses are kept verbatim.
  (2) INDUCTION_USER_TEMPLATE renders each answer contract with its FIXED description from the corpus CONTRACT
      (CONTRACT_DESCRIPTIONS: MC_LETTER from the MMLU-Pro protocol, where the key is one option letter indexing the
      options list, and the extractor, which reads one option letter; never from an EVAL row). A contract with no fixed
      description renders as its id alone (the earlier behaviour; no registered induction uses one).
  Unchanged: the selection, the seed, the content-key asserts, the option rendering of the examples (pipe-joined, in
  options_sorted_json order, unlettered: the registration names no change to it), the reply contract, the verbatim audit,
  the artefact. The INDUCE-RUBRIC-1 prompt (system 4c4bf36f..., user template 7ed21eba...) is superseded for forward use;
  its instrument (induce_run.py) pins those shas and now REFUSES on this module by design. The V5 FITNESS gate lives in
  judge_v2.induce_fitness (not here), and runs in induce_run_2.]
[CORRECTED 2026-09-24 by the judge-design-specialist's follow-up ruling F1b (programme L16350-L16475, verbatim; recorded at
f9cd77c), insertion only; pre-call, READY-stage:
  Q1 the INDUCTION_SYSTEM sentence "The judge sees the question with its lettered options, a reference solution that may be
     wrong, and the two responses in full. " is REPLACED by the ruling's exact text "The judge sees the question text
     without its options list, a reference solution that may be wrong (given as one option letter with that option's
     text), and the two responses in full, each followed, when its chosen letter can be read, by that letter with its
     option's text. " (the D5 fact: the judge sees the stem only; the error came from the F1 ruling's wording). Nothing
     else in the prompt changes; (1) above is read with this correction.
  Q2 the example options stay pipe-joined, sorted, unlettered; the user template is unchanged.
  Q3 under INDUCTION_VERSION jv2-induce-4, corpus_type != "mcq" is REFUSED (fail-closed) in induce() and build_prompt()
     with the message JV2_INDUCE_4_MCQ_ONLY. The docstring note "no registered induction uses one" stays beside it.]
[CORRECTED 2026-09-25 under ARCH-V2-INDUCE-RUBRIC-3 (registered 39c81c0, docs/judge_v2_program.md L17008-L17110),
insertion only; INDUCTION_VERSION jv2-induce-5. EXACTLY the registered changes:
  (1) INDUCTION_SYSTEM is the text of experiment_results/archv2/induce_rubric_3_registration/
      induction_system_jv2_induce_5.txt byte for byte (sha256 e95c59b22c3df56b79f2ed9a93f8b6912ca8aff15d78d849c79c9ba17c8896d7,
      2,360 characters; S1, S2, S4, S5, S10, S11 and S12 kept byte-identical from jv2-induce-4 67b62162...; S2b, S3 and
      S6-S9 new or changed). (1) and Q1 above describe jv2-induce-4 and are read with this bracket.
  (2) the MCQ guard (rule 11): check_corpus_type_for_version compared INDUCTION_VERSION to the literal "jv2-induce-4",
      so the bump would have silently DISABLED the refusal. It is now keyed by MCQ_ONLY_BY_VERSION: under jv2-induce-5
      corpus_type != "mcq" is REFUSED with JV2_INDUCE_5_MCQ_ONLY, and a version with no entry refuses every corpus type.
  Unchanged: INDUCTION_USER_TEMPLATE (8f098049...), CONTRACT_DESCRIPTIONS (d40c4b0a...), the example option rendering,
  the selection, the seed, the content-key asserts, the reply contract, the verbatim audit, the artefact. The -2
  instrument (induce_run_2.py, its selftest) pins jv2-induce-4 and therefore REFUSES on this module by design; it
  reproduces at 541e2ae. The V5 screen jv2-v5-4 lives in judge_v2.induce_fitness_3 and runs in induce_run_3.]
"""
import hashlib
import json
import os
import re

from ._base import dv2c, dv2ro, dv2views, git_blob_lf, refuse, sha256_text, HERE
from . import payload as P

INDUCTION_VERSION = "jv2-induce-5"   # 2: rubric only (ruling 4aac08e); 3: registered seed, TRAIN only, options keyed;
#                                      4: ARCH-V2-INDUCE-RUBRIC-2 (the prompt describes what the judge compares; contract text)
#                                      5: ARCH-V2-INDUCE-RUBRIC-3 (INDUCTION_SYSTEM = induction_system_jv2_induce_5.txt)
CONTRACT_TYPES = P.CONTRACT_TYPES
DEFAULT_SIDES = ("TRAIN",)            # the ONLY admitted value (ARCH-V2-INDUCE-SELECT-1: GATE excluded)
REGISTERED_SEEDS = {"ARCH-V2-INDUCE-SELECT-1": "ARCHV2-INDUCE-1:5abb79f55c3719d122b5310151f975493609f37b"}
REFUSED_SEEDS = ("jv2-induce-1", "jv2-induce-2", "jv2-induce-3")
DEFAULT_N = 40
SHINGLE = 8

INDUCTION_SYSTEM = (
    "You write the evaluation rubric an impartial judge will use to compare two model responses to one "
    "question. The judge sees the question text without its options list, a reference solution that may be "
    "wrong (given as one option letter with that option's text), and the two responses in full, each "
    "followed, when its chosen letter can be read, by that letter with its option's text. Some questions "
    "carry no reference solution. The responses are free-form text, usually step-by-step reasoning that ends "
    "in one option letter as the final answer; a response may also be truncated, may state no letter, or may "
    "give a final answer with no reasoning at all, either as a bare letter or as an empty response that the "
    "judge sees only as a one-line note naming the option it selected or saying that it selected none. The "
    "rubric decides which response better answers the question: correctness of the final answer first, then "
    "soundness of the supporting reasoning. It must not reward or penalise length, formatting, or the "
    "presence or absence of an explanation. Correctness means correct for the question: the judge decides it "
    "by its own working on the question and uses the reference solution, when one is shown, as one input to "
    "that working that may be wrong, never as the yardstick; the rubric must not define a correct final "
    "answer as one that matches or agrees with the reference. Whether its final answer is right or wrong, a "
    "response is neither preferred nor penalised merely for giving no reasoning or for giving more "
    "reasoning: reasoning is compared only by the errors or unsupported steps it contains. TIE is the "
    "correct verdict when both final answers are right, or both are wrong, and neither response's reasoning "
    "has fewer errors or unsupported steps than the other's; the rubric must not reserve TIE for identical "
    "responses, must not forbid or discourage TIE, and must not default to either response. Call the two "
    "responses Model A and Model B, as the judge's instructions do, and make no criterion depend on which of "
    "them is shown first. You are shown example questions of ONE corpus type so that the rubric fits the "
    "type's answer contract. The rubric must be generic to the type: it must not name, quote or paraphrase "
    "any example, and it must carry no domain facts. Reply with a single JSON object and nothing else: "
    "{\"rubric\": <the rubric, at most 12 lines>}")
INDUCTION_USER_TEMPLATE = (
    "Corpus type: $corpus_type\n"
    "Answer contract(s), each with its fixed description from the corpus contract: $contracts\n"
    "Number of examples: $n\n\n"
    "Examples (questions only; no answers are shown):\n$examples")
# The FIXED contract descriptions (jv2-induce-4, change (2)): from the corpus CONTRACT, never from an EVAL row. MC_LETTER:
# the MMLU-Pro protocol keys each question by one option letter indexing its options list (mmlu_pro.answer; data_v2.ingest
# contract "MC_LETTER"), and the extractor reads one option letter from the response.
CONTRACT_DESCRIPTIONS = {
    "MC_LETTER": "one of the lettered options (A, B, C, ...); the final answer is one option letter"}


def render_contracts(contract_ids):
    """'<id> (<fixed description>)' for each contract, sorted, joined by ', '; a contract with no fixed description renders
    as its id alone."""
    return ", ".join("%s (%s)" % (c, CONTRACT_DESCRIPTIONS[c]) if c in CONTRACT_DESCRIPTIONS else c
                     for c in sorted(set(contract_ids)))


class StubInducer:
    """A deterministic stand-in for the induction LLM: no network, no call. Its artefacts are never of record."""
    provenance = {"model": "STUB (no LLM call)", "of_record": "STUB, NOT OF RECORD"}

    def __init__(self, reply=None):
        self.reply = reply
        self.calls = []

    def __call__(self, system, user):
        self.calls.append((system, user))
        if self.reply is not None:
            return self.reply
        ct = re.search(r"^Corpus type: (\S+)$", user, re.M).group(1)
        return json.dumps({"rubric": "1. Decide whether each final answer satisfies the %s question's answer"
                                     " contract.\n" % ct +
                                     "2. Prefer the response whose final answer is correct.\n"
                                     "3. When both are correct, prefer fewer unsupported steps; otherwise TIE."})


def _corpus_type_contracts(corpus_type):
    cs = sorted(c for c, t in CONTRACT_TYPES.items() if t == corpus_type)
    if corpus_type not in P.CORPUS_TYPES:
        refuse("corpus type %r is not one of %s" % (corpus_type, P.CORPUS_TYPES))
    if not cs:
        refuse("corpus type %r has no data_v2 contract (CONTRACT_TYPES): its induction is not built" % corpus_type)
    return cs


def resolve_seed(seed, registration=None):
    """-> the of_record label of a selection seed. REFUSES a missing seed, a version-string seed, a registration that is
    not in REGISTERED_SEEDS or whose seed differs, and any unregistered seed that does not start with "DEV-"."""
    if not isinstance(seed, str) or not seed:
        refuse("induction seed is required (no default)")
    if seed in REFUSED_SEEDS:
        refuse("induction seed %r is a version string, never a record seed (ARCH-V2-INDUCE-SELECT-1)" % seed)
    if registration is not None:
        want = REGISTERED_SEEDS.get(registration)
        if want is None:
            refuse("induction registration %r is not registered (%s)" % (registration, sorted(REGISTERED_SEEDS)))
        if seed != want:
            refuse("induction seed %r is not the seed registered under %s" % (seed, registration))
        return "REGISTERED %s" % registration
    if seed in REGISTERED_SEEDS.values():
        refuse("the registered seed is used only with its registration named")
    if not seed.startswith("DEV-"):
        refuse("induction seed %r is neither registered nor a DEV- seed" % seed)
    return "DEV, NOT OF RECORD"


def _check_sides(sides):
    if tuple(sides) != DEFAULT_SIDES:
        refuse("induction sides %r REFUSED: TRAIN only (ARCH-V2-INDUCE-SELECT-1; GATE is excluded, EVAL never present)"
               % (tuple(sides),))


def _check_population(population):
    """population: None (every corpus version and contract of the corpus type) or {"corpus_version": str, "contracts":
    [str, ...]} (the ARCH-V2-INDUCE-RUBRIC-1 C4 ruling: mmlu-pro-v2 / MC_LETTER). Refuses any other shape."""
    if population is None:
        return None
    if not isinstance(population, dict) or set(population) != {"corpus_version", "contracts"} or \
            not isinstance(population["corpus_version"], str) or not population["contracts"] or \
            not all(c in CONTRACT_TYPES for c in population["contracts"]):
        refuse("population %r is not {corpus_version, contracts} with known contracts" % (population,))
    return {"corpus_version": population["corpus_version"], "contracts": sorted(population["contracts"])}


def select_inputs(conn, corpus_type, n, seed, sides=DEFAULT_SIDES, witness=None, population=None, exclude=None):
    _check_sides(sides)
    population = _check_population(population)
    if not isinstance(seed, str) or not seed:
        refuse("select_inputs: the seed is required")
    contracts = _corpus_type_contracts(corpus_type)
    unknown = sorted({c for (c,) in conn.execute("SELECT DISTINCT contract_id FROM variant")} - set(CONTRACT_TYPES))
    if unknown:
        refuse("gen_view carries contract(s) %s with no corpus type in CONTRACT_TYPES: refused (declare them)" % unknown)
    side_of, comp_of = {}, {}
    for iid, side, comp in conn.execute("SELECT item_id, side, component_id FROM side"):
        side_of[iid], comp_of[iid] = side, comp
    # (1) candidate ROWS (one per (corpus_version, variant_id)), (2) collapsed to DISTINCT variant_id, every duplicate row
    # asserted identical in (stem, options_sorted_json, contract_id) (ruling on finding 1 (b), eabbf45)
    by_vid = {}
    n_rows = n_dup = 0
    n_gate = n_other = 0
    gate_v, other_v = set(), set()
    excluded_by_population = {}
    for cv, vid, iid, stem, opts, contract in conn.execute(
            "SELECT corpus_version, variant_id, item_id, stem, options_sorted_json, contract_id FROM variant"):
        if population is not None and contract in contracts and side_of.get(iid) in sides and \
                (cv != population["corpus_version"] or contract not in population["contracts"]):
            k = "%s %s" % (cv, contract)
            excluded_by_population[k] = excluded_by_population.get(k, 0) + 1
            continue
        if contract in contracts and side_of.get(iid) in sides:
            n_rows += 1
            key = (stem, opts, contract)
            if vid in by_vid:
                n_dup += 1
                if by_vid[vid]["_key"] != key or by_vid[vid]["item_id"] != iid:
                    refuse("select_inputs: variant %s has duplicate rows that DIFFER in (stem, options_sorted_json,"
                           " contract_id) or item: refused (the ruling's collapse needs identical duplicates)" % vid)
                continue
            by_vid[vid] = {"variant_id": vid, "item_id": iid, "stem": stem,
                           "options": json.loads(opts) if (corpus_type == "mcq" and opts) else [], "contract_id": contract,
                           "_key": key}
        elif contract in contracts:
            if side_of.get(iid) == "GATE":
                gate_v.add(vid)
            else:
                other_v.add(vid)
    n_gate, n_other = len(gate_v), len(other_v)
    # (3) the UNCHANGED sort key; (4) the first variant of each COMPONENT until n
    order = sorted(by_vid.values(), key=lambda r: hashlib.sha256((seed + dv2c.US + r["variant_id"]).encode("utf-8")).hexdigest())
    exclude = frozenset(exclude or ())
    chosen, seen_comp, n_skip, n_excl, last_rank = [], set(), 0, 0, 0
    for rank, r in enumerate(order, 1):
        if len(chosen) >= n:
            break
        if r["variant_id"] in exclude:
            n_excl += 1          # skipped BEFORE the component rule: an excluded variant claims no component
            continue
        comp = comp_of.get(r["item_id"])
        if comp is None:
            refuse("select_inputs: item %s has no component in the split's side table" % r["item_id"])
        if comp in seen_comp:
            n_skip += 1
            continue
        seen_comp.add(comp)
        chosen.append({k: v for k, v in r.items() if k != "_key"})
        last_rank = rank
    if witness is not None:
        if population is not None:
            witness.update({"population": population, "excluded_by_population": excluded_by_population})
        if exclude:
            witness.update({"exclusion_list_size": len(exclude), "excluded_skipped_in_order": n_excl,
                            "last_rank": last_rank})
        witness.update({"candidate_rows": n_rows, "distinct_variants": len(by_vid), "duplicates_collapsed": n_dup,
                        "skipped_by_component": n_skip, "train_candidates": len(by_vid), "gate_excluded": n_gate,
                        "other_excluded": n_other})
    return chosen


def _option_texts(inputs):
    return [o for r in inputs for o in r["options"] if isinstance(o, str) and dv2c.split_side.norm(o) != ""]


def check_inputs_bound(conn, inputs, corpus_type):
    """Every input equals its gen_view variant row (stem, options = options_sorted_json for mcq, contract). ALL rows of the
    variant are fetched (one per corpus_version) and must be identical (ruling on finding 1 (d), eabbf45)."""
    bad = []
    for r in inputs:
        allrows = conn.execute("SELECT stem, options_sorted_json, contract_id FROM variant WHERE variant_id=?",
                               (r.get("variant_id"),)).fetchall()
        if not allrows:
            bad.append((r.get("variant_id"), "no gen_view variant"))
            continue
        if len(set(allrows)) != 1:
            bad.append((r.get("variant_id"), "the variant's %d rows differ across corpus versions" % len(allrows)))
            continue
        row = allrows[0]
        opts = json.loads(row[1]) if (corpus_type == "mcq" and row[1]) else []
        if r.get("stem") != row[0] or list(r.get("options") or []) != opts or r.get("contract_id") != row[2]:
            bad.append((r.get("variant_id"), "stem / options / contract differ from gen_view"))
    if bad:
        refuse("induction inputs REFUSED: %d input(s) are not gen_view's rows (e.g. %r)" % (len(bad), bad[:2]))
    return 0


def assert_induction_inputs(conn, texts, sides=DEFAULT_SIDES, where="rubric induction", option_texts=()):
    """(a) no stem and no option text is EVAL content (salted EVAL key set; sentinels included); (b) every stem's content
    key names a gen_view item on an admitted side. Refuses on the first failing leg; returns the counts."""
    _check_sides(sides)
    if not texts:
        refuse("%s: no inputs" % where)
    dv2views.assert_not_eval(conn, list(texts) + list(option_texts), where=where)
    keys = dv2c.KeyCache()
    bad = []
    for t in texts:
        iid = dv2c.item_id_of_key(keys.stem(t))
        row = conn.execute("SELECT side FROM side WHERE item_id=?", (iid,)).fetchone()
        if row is None or row[0] not in sides:
            bad.append((t[:60], row[0] if row else None))
    if bad:
        refuse("%s: REFUSED, %d input(s) are not generation-side items on sides %s by content key (e.g. %r)"
               % (where, len(bad), "+".join(sides), bad[:2]))
    return {"n_texts": len(texts), "n_option_texts": len(option_texts), "eval_hits": 0, "not_gen_side": 0,
            "sides": list(sides)}


JV2_INDUCE_4_MCQ_ONLY = "jv2-induce-4's INDUCTION_SYSTEM is MCQ-specific; other corpus types need their own registration"
JV2_INDUCE_5_MCQ_ONLY = "jv2-induce-5's INDUCTION_SYSTEM is MCQ-specific; other corpus types need their own registration"
# ARCH-V2-INDUCE-RUBRIC-3 (rule 11): the MCQ-only refusal is keyed by version; a version with no entry refuses EVERY
# corpus type, so a future bump cannot silently switch the refusal off (it did compare to the literal "jv2-induce-4")
MCQ_ONLY_BY_VERSION = {"jv2-induce-4": JV2_INDUCE_4_MCQ_ONLY, "jv2-induce-5": JV2_INDUCE_5_MCQ_ONLY}


def check_corpus_type_for_version(corpus_type):
    """F1b Q3: under INDUCTION_VERSION jv2-induce-4 only corpus_type "mcq" is admitted (fail-closed). ARCH-V2-INDUCE-RUBRIC-3:
    the same under jv2-induce-5, with the message JV2_INDUCE_5_MCQ_ONLY; an INDUCTION_VERSION with no entry in
    MCQ_ONLY_BY_VERSION refuses every corpus type (fail-closed)."""
    msg = MCQ_ONLY_BY_VERSION.get(INDUCTION_VERSION)
    if msg is None:
        refuse("INDUCTION_VERSION %r has no corpus-type rule (MCQ_ONLY_BY_VERSION): refused, fail-closed" % INDUCTION_VERSION)
    if corpus_type != "mcq":
        refuse(msg)


def build_prompt(corpus_type, inputs):
    check_corpus_type_for_version(corpus_type)
    ex = []
    for i, r in enumerate(inputs, 1):
        line = "%d. %s" % (i, r["stem"])
        if r["options"]:
            line += "\n   Options: " + " | ".join(r["options"])
        ex.append(line)
    user = (INDUCTION_USER_TEMPLATE.replace("$corpus_type", corpus_type)
            .replace("$contracts", render_contracts(r["contract_id"] for r in inputs))
            .replace("$n", str(len(inputs))).replace("$examples", "\n".join(ex)))
    return INDUCTION_SYSTEM, user


def _tokens(s):
    return re.findall(r"\w+", s.casefold())


def verbatim_audit(text, inputs, k=SHINGLE):
    """The shingles (k-token runs) of `text` found in any input stem or option; [] passes."""
    sh = set()
    for r in inputs:
        for src in [r["stem"]] + list(r["options"]):
            t = _tokens(src)
            sh.update(tuple(t[i:i + k]) for i in range(len(t) - k + 1))
    t = _tokens(text)
    return sorted({" ".join(t[i:i + k]) for i in range(len(t) - k + 1) if tuple(t[i:i + k]) in sh})


def induce(corpus_type, model_call, gen_path=None, expect_sha256=None, n=DEFAULT_N, seed=None, registration=None,
           sides=DEFAULT_SIDES, inputs=None, out=print, population=None, label=None, exclude=None, exclude_ref=None):
    """Induce one corpus type's rubric. seed is REQUIRED (resolve_seed). inputs, when given, are handed to the model instead
    of select_inputs()'s (dicts with variant_id / item_id / stem / options / contract_id): they must equal gen_view's rows
    and pass the same content-key assert, options included."""
    if not callable(model_call):
        refuse("induce: model_call must be callable (no live inducer is built; StubInducer is the only one)")
    artefact_label = label
    label = resolve_seed(seed, registration)
    _check_sides(sides)
    _corpus_type_contracts(corpus_type)
    check_corpus_type_for_version(corpus_type)
    conn = dv2views.open_generation("induce", gen_path, expect_sha256)
    witness = {}
    try:
        gpath = gen_path or os.environ.get("TAXOARENA_V2_GEN_VIEW")
        gmeta = dict(conn.execute("SELECT key, value FROM meta"))
        chosen = list(inputs) if inputs is not None else select_inputs(conn, corpus_type, n, seed, sides, witness,
                                                                         population, exclude)
        if not chosen:
            refuse("induce(%s): no generation-side inputs on sides %s" % (corpus_type, "+".join(sides)))
        texts_stem = [r["stem"] for r in chosen]
        opt_texts = _option_texts(chosen)
        check = assert_induction_inputs(conn, texts_stem, sides, option_texts=opt_texts)
        check_inputs_bound(conn, chosen, corpus_type)
        out("[INDUCE] %s: %d inputs (%d option texts) from %s; seed %s (%s); TRAIN-only witness %s; content-key check: %d"
            " EVAL hits (stems + options), %d not TRAIN" % (corpus_type, len(chosen), len(opt_texts), os.path.basename(gpath),
                                                        seed, label, json.dumps(witness, sort_keys=True),
                                                        check["eval_hits"], check["not_gen_side"]))
    finally:
        conn.close()
    system, user = build_prompt(corpus_type, chosen)
    reply = model_call(system, user)
    try:
        d = json.loads(reply)
    except (TypeError, ValueError):
        refuse("induce(%s): the model reply is not JSON" % corpus_type)
    if isinstance(d, dict) and "system_prompt" in d:
        refuse("induce(%s): the reply carries a system_prompt: the induced artefact fills the RUBRIC SLOT ONLY (ruling"
               " 4aac08e)" % corpus_type)
    if not isinstance(d, dict) or set(d) != {"rubric"} or not isinstance(d["rubric"], str) or not d["rubric"].strip():
        refuse("induce(%s): the reply is not exactly {rubric} with a non-empty string" % corpus_type)
    copied = verbatim_audit(d["rubric"], chosen)
    if copied:
        refuse("induce(%s): the rubric copies %d %d-token run(s) of the inputs verbatim (e.g. %r)" % (
            corpus_type, len(copied), SHINGLE, copied[:2]))
    prov = dict(getattr(model_call, "provenance", {}) or {"model": "unknown"})
    of_record = prov.get("of_record", "NOT OF RECORD until registered")
    if label.startswith("DEV"):
        of_record = "%s; %s" % (of_record, label)
    art = {"corpus_type": corpus_type, "rubric": d["rubric"], "rubric_sha256": P.rubric_sha(d["rubric"]),
           "of_record": of_record,
           "manifest": {
               "induction_version": INDUCTION_VERSION, "gen_view": os.path.basename(gpath),
               "gen_view_sha256_bytes": dv2ro.file_sha256(gpath),
               "gen_view_meta": {k: gmeta.get(k) for k in ("view_kind", "of_record", "seed", "split_sha256_bytes",
                                                          "views_blob", "content_check", "eval_key_count", "sides")},
               "sides_admitted": list(sides), "n_inputs": len(chosen), "seed": seed, "seed_label": label,
               "population": _check_population(population), "artefact_label": artefact_label,
               "overlap_exclusion": exclude_ref,
               "seed_registration": registration, "train_only_witness": witness,
               "inputs_selected_by": "caller" if inputs is not None else "select_inputs",
               "input_variant_ids_sha256": sha256_text("\n".join(sorted(r["variant_id"] for r in chosen))),
               "input_variant_ids_ordered_sha256": sha256_text("\n".join(r["variant_id"] for r in chosen)),
               "content_key_check": check, "verbatim_audit": {"shingle": SHINGLE, "hits": 0},
               "prompt_system_sha256": sha256_text(system), "prompt_user_sha256": sha256_text(user),
               "induction_blob": "blob:" + git_blob_lf(os.path.join(HERE, "induction.py")),
               "views_blob": "blob:" + git_blob_lf(dv2views.__file__), "model": prov}}
    art["artefact_sha256"] = sha256_text(json.dumps(art, sort_keys=True, ensure_ascii=True))
    return art


def write_artefact(art, path):
    """Write-once (mode "x"): an existing path is refused."""
    if os.path.exists(path):
        refuse("%s exists: a rubric artefact is written once" % path)
    with open(path, "x", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(art, sort_keys=True, indent=1, ensure_ascii=True) + "\n")
    return path


def load_artefact(path, expect_artefact_sha256=None):
    with open(path, encoding="utf-8") as f:
        art = json.load(f)
    body = {k: v for k, v in art.items() if k != "artefact_sha256"}
    got = sha256_text(json.dumps(body, sort_keys=True, ensure_ascii=True))
    if got != art.get("artefact_sha256"):
        refuse("%s: artefact_sha256 %s != the recomputed %s" % (path, art.get("artefact_sha256"), got))
    if expect_artefact_sha256 is not None and got != expect_artefact_sha256:
        refuse("%s: artefact_sha256 %s != the pinned %s" % (path, got, expect_artefact_sha256))
    return P.load_rubric(art)
