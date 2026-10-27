"""ARCH-V2-INDUCE-RUBRIC-3: the LIVE rubric re-inducer, THIRD induction (registered at 39c81c0,
docs/judge_v2_program.md L17008-L17110, on the author's decision (1) of 2026-09-25 "Third induction"; the pre-decided
FALLBACK L16994-L17006). Mints ONE MCQ rubric artefact for E-J's $rubric slot from the SAME 40 TRAIN inputs of record
(no new draw), with the induction prompt jv2-induce-5 (judge_v2.induction; INDUCTION_SYSTEM = the component file
induction_system_jv2_induce_5.txt, sha256 e95c59b2...) and the zero-call V5 FITNESS screen jv2-v5-4
(judge_v2.induce_fitness_3, which imports jv2-v5-3 unchanged). A RECIPE COMPONENT: no rubric-value or accuracy claim.

LAUNCH SEQUENCE (the run-operator; the READY pins EXPECTED_PAYLOAD_SHA from the dry-run):
    python tools/analysis/judge_v2/induce_run_3.py --dry-run                 # assemble and print the payload; posts nothing
    python tools/analysis/judge_v2/induce_run_3.py --run --go --expect-payload-sha <sha from the dry-run / the READY>
    python tools/analysis/judge_v2/induce_run_3.py --selftest                # synthetic fixture, stub poster; also under -O
No pilot mode: the run is 1 call (at most 3 attempts; at most 6 invocations; CEILINGS["ARCH-V2-INDUCE-RUBRIC-3"] = 6).
Data root: TAXOARENA_DATA_ROOT (the checkout holding data_v2/REG_ARCHV2-SPLIT-2_2929bd46.../), else this checkout.

WHY A SEPARATE FILE (the -3 registration, INSTRUMENT FILES). This file is judge_v2/induce_run_2.py (the INDUCE-RUBRIC-2
instrument of record, blob:286c750ee1c23550d0337840dbb8c8e17ed13617; LEFT BYTE-IDENTICAL) copied and changed ONLY where
the -3 registration says so: TEST, OUT_REL, the prompt pins, the V5 module and its list sha, the cache module, P3 and the
checklist line in outcome.txt, the new disclosures, the stage bracket line (and, with them, the author's pre-decided
FALLBACK wherever the -2 outcome sent the slot to THE AUTHOR, and the registered point probabilities P1 0.70 / P2 0.85 /
P3 0.55). By design the -2 runner and its selftest REFUSE on this checkout (they pin jv2-induce-4); the -2 instrument
reproduces at 541e2ae.
WHAT DIFFERS FROM induce_run_2.py (everything else applies as there, the -2 docstring below included):
  (a) TEST "ARCH-V2-INDUCE-RUBRIC-3"; OUTPUTS under experiment_results/archv2/induce_rubric_3/; the attempt cache is
      judge_v2.induce_cache_3 (the -2 DDL unchanged, schema id archv2-induce-rubric-3-cache-v1).
  (b) THE PROMPT PINS: INDUCTION_VERSION jv2-induce-5; SYSTEM_SHA e95c59b2... (the component file); USER_TEMPLATE_SHA and
      DESCRIPTIONS_SHA UNCHANGED; V5_LIST_SHA = induce_fitness_3.REGEX_LIST_SHA256_V54 (jv2-v5-4), and the imported
      jv2-v5-3 list pin (7b5af1d5...) is checked beside it.
  (c) V5 = jv2-v5-4 (induce_fitness_3.v5) in classify(), in the attempt record and on the reply of record in finish().
  (d) outcome.txt: the -3 DISCLOSURES OF RECORD 1-5 (6 = the four carried selection disclosures, printed as before); P1
      (0.70), P2 (0.85), P3 (0.55; the checklist reads FIT in both readings: NOT SCORED by this instrument, the post-run
      reading scores it); the CHECKLIST line (K1-K8 and the VERDICT RULE); the FALLBACK line (GENERIC_RUBRIC, sha256
      67f843eb..., in every non-adoption route, with no further author question and never a fourth attempt).
  (e) THE eval_view OPEN FOR V2: open_eval("judge") as in -1 / -2 (VIEWS-AUDIT-STAGE not merged); the registration's
      "THE eval_view OPEN" paragraph: a NEW READY bracket names it for THIS run only, under the -1 / -2 conditions.

THE -2 DOCSTRING (inherited; read "-2" as the parent instrument):
WHY A SEPARATE FILE. This file is judge_v2/induce_run.py (the INDUCE-RUBRIC-1 instrument of record, blob:4c9c0a20f998...,
sha256-lf16:add7df769d1c7efd; LEFT BYTE-IDENTICAL) copied and changed ONLY where the -2 registration says so; a
parameterisation of induce_run.py would have changed the -1 instrument's pin. The -1 runner pins the jv2-induce-3 prompt
shas and therefore REFUSES on the jv2-induce-4 induction.py by design (its run is complete; it reproduces at 3cc505f).

WHAT DIFFERS FROM induce_run.py (everything else, the rulings and brackets of the -1 docstring included, applies as there:
the sha-pinned gen_view open through open_generation("induce"); the selection; the content-key asserts; the body through
rejudge_reasoning.payload_bytes after payload.configure_rr() (grok-4-1-fast-non-reasoning, cap 8192, temperature OMITTED);
posting ONLY through rejudge_reasoning.call_judge_full; the write-ahead invocation row; transport errors (not attempts,
own limit 3, fail-closed stop, identical-body relaunch, orphans); the day-ledger equality and the shared guard; V1-V4):
  (a) TEST "ARCH-V2-INDUCE-RUBRIC-2"; OUTPUTS under experiment_results/archv2/induce_rubric_2/ (never induce_rubric_1/);
      the attempt cache is judge_v2.induce_cache_2 (the -1 schema plus the failure class FITNESS; its own schema id);
      the ledger ceiling CEILINGS["ARCH-V2-INDUCE-RUBRIC-2"] = 6 (3 attempts + 3 transport errors).
  (b) THE PROMPT PINS (printed and asserted before anything else is built): INDUCTION_VERSION jv2-induce-4;
      INDUCTION_SYSTEM sha256 SYSTEM_SHA; INDUCTION_USER_TEMPLATE sha256 USER_TEMPLATE_SHA; the fixed contract
      descriptions (induction.CONTRACT_DESCRIPTIONS, canonical JSON) sha256 DESCRIPTIONS_SHA; the V5 regex list sha256
      V5_LIST_SHA (= induce_fitness.REGEX_LIST_SHA256 = induce_fitness.regex_list_sha256()).
  (c) THE SELECTION IS REUSED UNCHANGED (no new draw): seed ARCH-V2-INDUCE-SELECT-1, population mmlu-pro-v2 x MC_LETTER x
      TRAIN, dedup, component rule, n = 40, the overlap exclusion list of record
      experiment_results/archv2/induce_rubric_1_audit/overlap_exclusions_split2.json (list_sha256 68c0b960...). Under the
      registered seed the dry-run AND the run REFUSE unless the input ids reproduce sorted-set sha256 99484486... and
      ordered sha256 89bed256... (SELECTION_SORTED_SHA / SELECTION_ORDERED_SHA): any difference is a FAILED PRECONDITION.
  (d) V5 FITNESS on EVERY reply, in classify(), after the -1 classes (CONTENT_FILTER, LENGTH, NON_JSON, KEY, VERBATIM):
      a reply that fails V5 is the formal failure FITNESS (consumes an attempt; the SAME body is re-posted, at most 3
      attempts; no best-of-n; no edit); the matching pattern(s) are printed, written to the event log and to outcome.txt.
      The reply of record is re-checked by V5 in finish() (V5 PASS required for the artefact of record).
  (e) THE eval_view OPEN FOR V2 (DEVIATION, needs a READY bracket): data_v2.views has no "audit" stage (VIEWS-AUDIT-STAGE
      not merged), so V2 opens eval_view through open_eval("judge") exactly as INDUCE-RUBRIC-1 did. The -1 acceptance of the
      "judge" label was for THAT run only; this run needs a NEW registrar bracket naming it (the registration's
      HYGIENE paragraph). Nothing in data_v2 or views.py is changed. The order discipline is -1's: eval_view is opened only
      after the valid reply is committed; the flag refuses any call_judge_full after the open; a V2 failure never re-posts.
  (f) outcome.txt: V1-V5, P1 (the first attempt VALID, V5 included; 0.8), P2 (V1-V5 all PASS), the falsifier (three
      formal failures -> UNDETERMINED; the slot goes to THE AUTHOR), the ruling's disclosures 1-5 and the four carried
      INDUCE-RUBRIC-1 selection disclosures.
[F1b 2026-09-24 (the judge-design-specialist's follow-up ruling, programme L16350-L16475, verbatim at f9cd77c), applied
before any call: SYSTEM_SHA re-pinned to the corrected INDUCTION_SYSTEM (Q1; 73d9ed4e -> 67b62162); induction refuses
corpus_type != "mcq" under jv2-induce-4 (Q3); V5 rebuilt (judge_v2.induce_fitness jv2-v5-2: (a) + (b) + the REQUIRED (c)
reasoning criterion, contrastive guard split, CUE additions, wider penalty / reward families, the unguarded exclusivity
pattern; V5_LIST_SHA cfcb9ca4 -> a9040d5d); outcome.txt carries the V5 SCOPE line (change 7); the selftest pins the probe
corpus B1-B11 / F1-F5 (C-V5-probe). The a02a9c1 values were never pinned of record.]
[READY H1 / M1 2026-09-24 (docs/reviews/READY_induce_rubric_2.md, d3e9716: NOT READY on V5 false positives), applied
before any call: V5 revised to jv2-v5-3 (judge_v2.induce_fitness: contracted and other CUE additions, the concessive guard on
reward_form, the "<errors> in the explanation / working" exemption, the "letter alone determines" exemption, (a) "right
answer" / "correctness", the (c) negation guard, M1 reward objects, the format_demand and ideal_bare_letter patterns, the
"ignore" / "regardless of" cues narrowed to form objects); V5_LIST_SHA a9040d5d -> 7b5af1d5; the selftest pins the
reviewer's corpus (B12-B29 FAIL, F6-F43 PASS) and the known limits. The payload, INDUCTION_SYSTEM and induction.py do not
move.]
OUTPUTS (write-once; a present path REFUSES the launch): <root>/experiment_results/archv2/induce_rubric_2/
    attempts.db                        the attempt cache (induce_cache_2; append-only; write-ahead invocation rows)
    input_variant_ids.json             the ordered ids, the sorted-set sha256 and the ordered sha256
    rubric_mcq_ARCH-V2-INDUCE-RUBRIC-2.json   the artefact of record (only when a valid reply passes V1-V3 and V5)
    outcome.txt                        attempts, V1-V5, P1, P2, the falsifier, the disclosures (mode "x")
"""
import argparse
import hashlib
import json
import os
import re
import sys
import sqlite3
import zlib
from datetime import datetime, timezone

if __name__ == "__main__" and not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    __package__ = "judge_v2"
    import judge_v2  # noqa: F401

from ._base import REFERENCE_MARKER, dv2views, git_blob_lf, refuse, rr, sha256_text, ROOT  # noqa: E402
from . import induce_cache_3 as IC  # noqa: E402
from . import induce_fitness as F  # noqa: E402
from . import induce_fitness_3 as F3  # noqa: E402
from . import induce_overlap_audit as OA  # noqa: E402
from . import induction as I  # noqa: E402
from . import leakage as L  # noqa: E402
from . import loader as LD  # noqa: E402
from . import payload as P  # noqa: E402

TEST = "ARCH-V2-INDUCE-RUBRIC-3"
SELECTION_OF_RECORD_FROM = "ARCH-V2-INDUCE-RUBRIC-1"   # the selection is REUSED (no new draw)
SELECT_REGISTRATION = "ARCH-V2-INDUCE-SELECT-1"
SEED = "ARCHV2-INDUCE-1:5abb79f55c3719d122b5310151f975493609f37b"
N = 40
CORPUS_TYPE = "mcq"
MAX_ATTEMPTS = 3
MAX_TRANSPORT = 3        # ruling on finding 2: errored invocations have their own limit
SPLIT_DIR = "data_v2/REG_ARCHV2-SPLIT-2_2929bd46aa271d883050bfe735f96e621ed55fd2"   # re-pin: SPLIT-1 c0303156 -> SPLIT-2
GEN_VIEW = SPLIT_DIR + "/gen_view_REG.db"
EVAL_VIEW = SPLIT_DIR + "/eval_view_REG.db"
GEN_SHA = "c2930c609c67d6c7e1f8b8fbcd8f6f1970478a28f844d086d0b0db169d10c0ec"      # SPLIT-2 manifest of record (was 690d06b8, b44227f)
EVAL_SHA = "e35b7518878205837bfd16266dfdd8a6e76a226ed67957796d1d33cb72b5e369"     # SPLIT-2 manifest of record (was 7c284b15, b51eb71)
MANIFEST = "data_v2/manifests/REG_ARCHV2-SPLIT-2_2929bd46aa271d883050bfe735f96e621ed55fd2.json"
INDUCTION_VERSION = "jv2-induce-5"
SYSTEM_SHA = "e95c59b22c3df56b79f2ed9a93f8b6912ca8aff15d78d849c79c9ba17c8896d7"          # jv2-induce-5 = induction_system_jv2_induce_5.txt (was 67b62162, -2)
USER_TEMPLATE_SHA = "8f098049e6af71fd509fc80d760ed7a4f29013cc21a93de3283737dc6cbfd53a"   # jv2-induce-4 (was 7ed21eba, -1)
DESCRIPTIONS_SHA = "d40c4b0ae9b6829157d99609cfa8b92486fad109f6b588f0ff8deb210672b416"    # CONTRACT_DESCRIPTIONS, canonical JSON
V5_LIST_SHA = "714268738c7593ab45d09daba2934e8780278c82a180f10a78685a283f4ef7d0"         # induce_fitness_3.regex_list_v54_sha256() (jv2-v5-4)
V5_BASE_LIST_SHA = "7b5af1d513df318031d77a14b7c8673051a075957ca97ffcc287cdfdc516fa54"    # the imported jv2-v5-3 list (unchanged)
# the selection of record (INDUCE-RUBRIC-1, reused): a registered-seed dry-run / run REFUSES any other ids
SELECTION_SORTED_SHA = "99484486d75774b379bd35713063022a8c05b8949b7b2d61045f95670d9abe50"
SELECTION_ORDERED_SHA = "89bed2562c1f8575ed0dbfd5b9980216aa346ef26d5837fbe574b7b775ef132a"
OUT_REL = "experiment_results/archv2/induce_rubric_3"
EXCL_REL = "experiment_results/archv2/induce_rubric_1_audit/overlap_exclusions_split2.json"   # induce_overlap_audit's output
EXCL_SHA = "68c0b960a4a7bedc76db079cdc2e0f01d5ef0b2fc4304f5486706cb27b71418a"     # SPLIT-2 (was a4f6e2b7 on SPLIT-1); the pinned list_sha256 of the overlap exclusion list of record (ruling D1)
DISCLOSURE_D1 = ("%d inputs sharing >= 8 consecutive tokens with EVAL texts excluded and replaced in sort order before the"
                 " first call; seed kept")      # the count is the witness's "replaced" (7 on the view of record)
FORMAL_FAILURES = ("NON_JSON", "KEY", "LENGTH", "CONTENT_FILTER", "VERBATIM", "FITNESS")   # FITNESS = V5 (new)
P1_POINT = 0.70
P2_POINT = 0.85
P3_POINT = 0.55
GENERIC_RUBRIC_SHA256 = "67f843eb7a632ae5bd411a9debcbaf9dedccd362e0c8355c366c6d85cb89b1dc"   # the fallback (rubric_value_contrast.GENERIC_RUBRIC)


def _data_root():
    return os.environ.get("TAXOARENA_DATA_ROOT", ROOT)


class Paths:
    def __init__(self, data_root=None, out_dir=None):
        root = data_root or _data_root()
        self.gen = os.path.join(root, *GEN_VIEW.split("/"))
        self.eval = os.path.join(root, *EVAL_VIEW.split("/"))
        self.manifest = os.path.join(ROOT, *MANIFEST.split("/"))
        self.out = out_dir or os.path.join(ROOT, *OUT_REL.split("/"))
        self.cache = os.path.join(self.out, "attempts.db")
        self.ids = os.path.join(self.out, "input_variant_ids.json")
        self.artefact = os.path.join(self.out, "rubric_mcq_%s.json" % TEST)
        self.outcome = os.path.join(self.out, "outcome.txt")
        self.excl = os.path.join(ROOT, *EXCL_REL.split("/"))
        self.check_manifest = True


def check_manifest(paths, gen_sha, eval_sha, out=print):
    """The manifest of record (b51eb71) names both views with the pinned shas (a cross-check of the constants)."""
    if not os.path.isfile(paths.manifest):
        refuse("the manifest of record %s is missing" % paths.manifest)
    m = json.load(open(paths.manifest, encoding="utf-8"))
    got = {o.get("kind"): o.get("sha256_bytes") for o in m.get("outputs", [])}
    out("[INDUCE-RUN] manifest of record %s: gen_view %s, eval_view %s" % (os.path.basename(paths.manifest),
                                                                          got.get("gen_view"), got.get("eval_view")))
    if got.get("gen_view") != gen_sha or got.get("eval_view") != eval_sha:
        refuse("the manifest of record does not name the pinned view shas (gen %s, eval %s)" % (gen_sha, eval_sha))


# ── (3) the prompt pins ──────────────────────────────────────────────────────────────────

def descriptions_sha():
    return sha256_text(json.dumps(I.CONTRACT_DESCRIPTIONS, sort_keys=True, ensure_ascii=True))


def check_prompt_pins(out=print):
    got_s, got_u = sha256_text(I.INDUCTION_SYSTEM), sha256_text(I.INDUCTION_USER_TEMPLATE)
    got_d, got_v = descriptions_sha(), F3.regex_list_v54_sha256()
    out("[INDUCE-RUN] INDUCTION_VERSION %s (registered %s) | INDUCTION_SYSTEM sha256 %s (%d chars; registered %s) |"
        " INDUCTION_USER_TEMPLATE sha256 %s (%d chars; registered %s)" % (
            I.INDUCTION_VERSION, INDUCTION_VERSION, got_s, len(I.INDUCTION_SYSTEM), SYSTEM_SHA, got_u,
            len(I.INDUCTION_USER_TEMPLATE), USER_TEMPLATE_SHA))
    out("[INDUCE-RUN] contract descriptions sha256 %s (registered %s): %s | V5 regex list sha256 %s (module pin %s,"
        " registered %s; %s over %s %s, %d form patterns, %d (d1), %d sceptic cues, %d (e), %d (f), %d reference cues,"
        " flags %s) | C-V5-pos control text sha256 %s" % (
            got_d, DESCRIPTIONS_SHA, json.dumps(I.CONTRACT_DESCRIPTIONS, sort_keys=True), got_v, F3.REGEX_LIST_SHA256_V54,
            V5_LIST_SHA, F3.V5_VERSION, F.V5_VERSION, F.regex_list_sha256(), len(F.FORM_PATTERNS),
            len(F3.RULES_V54["d1"]), len(F3.RULES_V54["d2"]["sceptic"]), len(F3.RULES_V54["e"]), len(F3.RULES_V54["f"]),
            len(F3.RULES_V54["cue_ref"]), F3.FLAGS_NAME, sha256_text(F.CONTROL_FIT_TEXT)))
    if I.INDUCTION_VERSION != INDUCTION_VERSION:
        refuse("induction.INDUCTION_VERSION %s is not the registered %s" % (I.INDUCTION_VERSION, INDUCTION_VERSION))
    if got_s != SYSTEM_SHA or got_u != USER_TEMPLATE_SHA:
        refuse("the induction prompt constants are not the registered ones (system %s, user template %s)" % (got_s, got_u))
    if got_d != DESCRIPTIONS_SHA:
        refuse("the fixed contract descriptions are not the registered ones (sha256 %s)" % got_d)
    if got_v != V5_LIST_SHA or F3.REGEX_LIST_SHA256_V54 != V5_LIST_SHA:
        refuse("the V5 regex list is not the registered one (computed %s, module pin %s, registered %s)" % (
            got_v, F3.REGEX_LIST_SHA256_V54, V5_LIST_SHA))
    if F.regex_list_sha256() != V5_BASE_LIST_SHA or F.REGEX_LIST_SHA256 != V5_BASE_LIST_SHA:
        refuse("the imported jv2-v5-3 list is not the one of record (computed %s, registered %s)" % (
            F.regex_list_sha256(), V5_BASE_LIST_SHA))
    if sha256_text(F.CONTROL_FIT_TEXT) != F.CONTROL_FIT_SHA256:
        refuse("the C-V5-pos control text is not the pinned one")


# ── (1)(2) selection ─────────────────────────────────────────────────────────────────────

DISCLOSURE = "selection corrected before the first call (duplicate corpus rows); the registered seed kept"
DISCLOSURE_C4 = "population narrowed to the judged corpus after the input list's source mix was seen; seed kept; no call"
DISCLOSURE_C5 = ("the dry-run process opened eval_view before any call to size V2's material (counts only); the ruling on"
                 " finding 3 (i) binds the run's process")
POPULATION = {"corpus_version": "mmlu-pro-v2", "contracts": ["MC_LETTER"]}
ARTEFACT_LABEL = "MCQ rubric, population mmlu-pro-v2 TRAIN (ARCH-V2-INDUCE-RUBRIC-3, jv2-induce-5)"
DISCLOSURES_RULING = (    # the -3 registration's DISCLOSURES OF RECORD 1-5 (6 = the four carried selection disclosures)
    "1. INDUCE-1 (ef9c9e87) and INDUCE-2 (ace41ede) are VALID, of record and NOT ADOPTED; no verdict uses either",
    "2. the -3 prompt changes are justified by code and template; their motivation came from the -2 post-run review,"
    " which read EVAL; no EVAL number is in the prompt",
    "3. V5 stays a lexical screen; its held-out estimate is descriptive; the checklist is the substantive check",
    "4. the -2 instrument refuses on main by design after this change and reproduces at 541e2ae",
    "5. the eval_view 'judge' label is accepted for this run only")
V5_SCOPE = ("V5 (jv2-v5-4) is a lexical screen and cannot be complete; the registered fitness reading (the checklist K1-K8 by"
            " the post-run reviewer and, blind, the judge-design-specialist) is the substantive check; a post-run reading of"
            " UNFIT makes the artefact NOT ADOPTED and the slot takes the author's pre-decided FALLBACK, never a fourth"
            " attempt or a re-roll; a V5 PASS does not show that a rubric is fit")
DISCLOSURE_STAGE = ("eval_view opened for V2 through open_eval('judge') (VIEWS-AUDIT-STAGE not merged): the -3 registration's"
                    " 'THE eval_view OPEN': a NEW READY bracket names it for THIS run only, under the -1 / -2 conditions")
CHECKLIST = ("the REGISTERED FITNESS READING (post-run; the reviewer and, independently and blind, the"
             " judge-design-specialist): render the FULL system turn (payload.build_system(load_rubric(artefact))), the user"
             " turn and SCHEMA_INSTRUCTION; walk K1 (reference as criterion), K1b (reference distrusted by default), K2"
             " (reasoning-presence reward), K2b (absence reward, anti-reasoning, format demand), K2c (placeholder walk), K3"
             " (TIE narrowed), K3b (over-tie), K4 (position), K5 (no reference), K6 (options not shown), K7 (template"
             " walk), K8 (output-format conflict) against cases (i) reference-bearing, (ii) reference NONE, (iii) the"
             " robust_trace placeholder; VERDICT RULE: FIT iff no item reads UNFIT in EITHER reading (a disagreement on any"
             " UNFIT item reads UNFIT); UNFIT -> NOT ADOPTED")
FALLBACK = ("the author's PRE-DECIDED FALLBACK (2026-09-25, 'Generic rubric (Recommended)'): in EVERY non-adoption route"
            " (three formal failures -> UNDETERMINED; a V2 failure -> NOT OF RECORD; a post-run UNFIT -> NOT ADOPTED) the"
            " $rubric slot takes GENERIC_RUBRIC (sha256 %s), with no further author question and never a fourth attempt"
            " or re-roll" % GENERIC_RUBRIC_SHA256)


def select(gen_path, gen_sha, seed, registration, out=print, excl=None):
    """Open the gen_view of record (open_generation("induce"), sha-pinned), select the TRAIN inputs (judge_v2.induction as
    amended by the ruling on finding 1: distinct variant_id, first per component) and run every content-key check.
    Returns (inputs, witness, check, gen_meta, seed label). A repeated variant, item or component is REFUSED (backstop)."""
    label = I.resolve_seed(seed, registration)
    conn = dv2views.open_generation("induce", gen_path, gen_sha)
    witness = {}
    try:
        gmeta = dict(conn.execute("SELECT key, value FROM meta"))
        excl_set, excl_rec = excl if excl is not None else (None, None)
        if excl_set is None:
            refuse("select: the overlap exclusion list (ruling D1) is required")
        base = [r["variant_id"] for r in I.select_inputs(conn, CORPUS_TYPE, N, seed, I.DEFAULT_SIDES, None, POPULATION)]
        chosen = I.select_inputs(conn, CORPUS_TYPE, N, seed, I.DEFAULT_SIDES, witness, POPULATION, excl_set)
        kept = len(set(base) & {r["variant_id"] for r in chosen})
        witness.update({"kept_from_unexcluded": kept, "replaced": N - kept, "exclusion_list_sha256": excl_rec["list_sha256"]})
        if any(r["variant_id"] in excl_set for r in chosen):
            refuse("select: an excluded variant reached the selection")
        if len(chosen) != N:
            refuse("selection: %d inputs, the registration says n = %d" % (len(chosen), N))
        stems = [r["stem"] for r in chosen]
        opts = I._option_texts(chosen)
        check = I.assert_induction_inputs(conn, stems, I.DEFAULT_SIDES, option_texts=opts)
        I.check_inputs_bound(conn, chosen, CORPUS_TYPE)
        comps = {r["item_id"]: c for r in chosen for (c,) in
                 conn.execute("SELECT component_id FROM side WHERE item_id=?", (r["item_id"],))}
        srcs = sorted({x for r in chosen for (x,) in conn.execute(
            "SELECT DISTINCT source FROM source_row WHERE variant_id=?", (r["variant_id"],))})
        ctrs = sorted({r["contract_id"] for r in chosen})
    finally:
        conn.close()
    nv, ni, nc = len({r["variant_id"] for r in chosen}), len({r["item_id"] for r in chosen}), len(set(comps.values()))
    if not (nv == ni == nc == len(chosen)):
        refuse("selection: %d rows, %d distinct variants, %d items, %d components: the ruling's 40 distinct components are"
               " not met" % (len(chosen), nv, ni, nc))
    out("[INDUCE-RUN] population %s (%s); TRAIN rows excluded by corpus version and contract %s; the inputs' contracts %s,"
        " sources %s" % (json.dumps(POPULATION, sort_keys=True), DISCLOSURE_C4,
                         json.dumps(witness.get("excluded_by_population", {}), sort_keys=True), ctrs, srcs))
    out("[INDUCE-RUN] selection (%s): seed %s (%s); candidate rows %d, distinct variants %d, duplicates collapsed %d,"
        " variants skipped by component %d; %d inputs = %d variants = %d items = %d components; REFUSED and counted: GATE %d,"
        " other non-TRAIN %d; EVAL keys in the salted set %s (EVAL and sentinel rows are absent from gen_view); content-key"
        " check %d stems + %d option texts: EVAL hits %d, not TRAIN %d" % (
            DISCLOSURE, seed, label, witness["candidate_rows"], witness["distinct_variants"],
            witness["duplicates_collapsed"], witness["skipped_by_component"], len(chosen), nv, ni, nc,
            witness["gate_excluded"], witness["other_excluded"], gmeta.get("eval_key_count"), check["n_texts"],
            check["n_option_texts"], check["eval_hits"], check["not_gen_side"]))
    witness["input_sources"], witness["input_contracts"] = srcs, ctrs
    out("[INDUCE-RUN] overlap exclusion (ruling D1): list sha256 %s (%d excluded TRAIN variants, run >= %d); in the order:"
        " %d inputs kept, %d replaced, last rank %d (%s)" % (
            excl_rec["list_sha256"], len(excl_set), OA.THRESHOLD, witness["kept_from_unexcluded"], witness["replaced"],
            witness.get("last_rank", N), DISCLOSURE_D1 % witness["replaced"]))
    return chosen, witness, check, gmeta, label


def ids_record(chosen):
    ids = [r["variant_id"] for r in chosen]
    return {"registration": TEST, "selection_registration": SELECT_REGISTRATION, "n": len(ids), "input_variant_ids": ids,
            "input_variant_ids_sha256": sha256_text("\n".join(sorted(ids))),
            "input_variant_ids_ordered_sha256": sha256_text("\n".join(ids)), "disclosure": DISCLOSURE,
            "disclosure_population": DISCLOSURE_C4, "population": POPULATION, "artefact_label": ARTEFACT_LABEL,
            "selection_of_record_from": SELECTION_OF_RECORD_FROM}


def check_selection_pin(rec, registration, out=print):
    """The selection is REUSED: under the registered seed (registration named) the ids must reproduce INDUCE-RUBRIC-1's
    sorted-set and ordered shas, else a FAILED PRECONDITION (refused). A DEV seed (the selftest fixture) is not pinned."""
    if registration is None:
        out("[INDUCE-RUN] selection pin: NOT CHECKED (DEV seed, no registration; the fixture's selection)")
        return None
    ok = bool(rec["input_variant_ids_sha256"] == SELECTION_SORTED_SHA and
              rec["input_variant_ids_ordered_sha256"] == SELECTION_ORDERED_SHA)
    out("[INDUCE-RUN] selection pin (reused from %s): sorted-set sha256 %s (pinned %s), ordered sha256 %s (pinned %s): %s"
        % (SELECTION_OF_RECORD_FROM, rec["input_variant_ids_sha256"], SELECTION_SORTED_SHA,
           rec["input_variant_ids_ordered_sha256"], SELECTION_ORDERED_SHA, "REPRODUCED" if ok else "DIFFERS"))
    if not ok:
        refuse("FAILED PRECONDITION: the selection does not reproduce the selection of record (%s): nothing is posted"
               % SELECTION_OF_RECORD_FROM)
    return True


# ── (4) the payload ──────────────────────────────────────────────────────────────────────

def build_payload(chosen):
    P.configure_rr()
    system, user = I.build_prompt(CORPUS_TYPE, chosen)
    if system != I.INDUCTION_SYSTEM:
        refuse("the built system prompt is not INDUCTION_SYSTEM")
    body = rr.payload_bytes(system, user)
    d = json.loads(body.decode("utf-8"))
    if list(d) != P.BODY_KEYS or d["model"] != P.JUDGE_REQUESTED or d["max_tokens"] != P.CAP or "temperature" in d:
        refuse("the induction body is not model / max_tokens / messages with the v2 judge, cap 8192 and no temperature")
    return system, user, body, hashlib.sha256(body).hexdigest()


# ── (5) attempts ─────────────────────────────────────────────────────────────────────────

def classify(content, finish_reason, chosen):
    """-> (failure class or None if VALID, the parsed rubric or None). No repair, no fence stripping: the reply is json.loads'
    input verbatim, exactly as judge_v2.induction.induce reads it."""
    if finish_reason == "content_filter":
        return "CONTENT_FILTER", None
    if finish_reason == "length":
        return "LENGTH", None
    try:
        d = json.loads(content)
    except (TypeError, ValueError):
        return "NON_JSON", None
    if not isinstance(d, dict) or set(d) != {"rubric"} or not isinstance(d["rubric"], str) or not d["rubric"].strip():
        return "KEY", None
    if I.verbatim_audit(d["rubric"], chosen):
        return "VERBATIM", None
    if not F3.v5(d["rubric"])["pass"]:         # V5 FITNESS (jv2-v5-4): a formal failure, consumes the attempt
        return "FITNESS", None
    return None, d["rubric"]


def fitness_detail(content):
    """The V5 line for a reply whose rubric parses (None otherwise): the matching pattern(s) are disclosed."""
    try:
        d = json.loads(content)
    except (TypeError, ValueError):
        return None
    if not isinstance(d, dict) or not isinstance(d.get("rubric"), str):
        return None
    return F3.describe(F3.v5(d["rubric"]))


# ruling on finding 3 (i): once eval_view is opened, this PROCESS makes no call_judge_full invocation (flag set on open)
_EVAL_OPENED = {"at": None}


def guarded(call_full):
    def g(system, user):
        if _EVAL_OPENED["at"] is not None:
            refuse("a call_judge_full invocation AFTER eval_view was opened (at %s) is refused (ruling on finding 3 (i))"
                   % _EVAL_OPENED["at"])
        return call_full(system, user)
    return g


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _event(conn, what, detail=""):
    at = _now()
    conn.execute("INSERT INTO event (at, what, detail) VALUES (?,?,?)", (at, what, detail))
    conn.commit()
    return at


def _write_ahead(conn, sha):
    """Insert and commit the PENDING invocation row BEFORE the post (READY C1). The cache's triggers refuse the invocation
    itself (a call after a valid reply, a 4th attempt, a 4th transport error, an unresolved orphan): nothing is posted."""
    seq = IC.state(conn)["n_invocations"] + 1
    try:
        conn.execute("INSERT INTO invocation VALUES (?,?,?,?)", (seq, _now(), sha, "PENDING"))
        conn.commit()
    except sqlite3.DatabaseError as e:
        conn.rollback()
        refuse("the attempt cache REFUSES invocation %d BEFORE any post: %s" % (seq, e))
    return seq


def resolve_orphans(conn, out=print):
    """On a relaunch: every invocation with no attempt and no transport row (posted, then the process died or the
    bookkeeping raised) becomes a TRANSPORT error 'no reply recorded': it consumes the transport limit and is disclosed."""
    st = IC.state(conn)
    for seq in st["orphans"]:
        n = IC.state(conn)["n_transport"] + 1
        if n > MAX_TRANSPORT:
            refuse("orphan invocation %d cannot be recorded: the transport limit is already reached" % seq)
        sha = conn.execute("SELECT payload_sha256 FROM invocation WHERE seq=?", (seq,)).fetchone()[0]
        conn.execute("INSERT INTO transport VALUES (?,?,?,?,?,?,?)", (n, seq, _now(), sha, "ORPHAN",
                                                                    "no reply recorded for invocation %d" % seq,
                                                                    IC.ORPHAN_NOTE))
        conn.commit()
        _event(conn, "orphan_resolved", "invocation %d -> transport error %d of %d" % (seq, n, MAX_TRANSPORT))
        out("[INDUCE-RUN] invocation %d was POSTED with no reply recorded (an orphan): counted as TRANSPORT ERROR %d of %d"
            " (%s)" % (seq, n, MAX_TRANSPORT, IC.ORPHAN_NOTE))
    return len(st["orphans"])


def attempts(conn, call_full, system, user, body, sha, chosen, out=print, posted=None):
    """Post the SAME body until the first VALID reply; attempts continue the cache's numbering (1..3). Before EVERY post a
    PENDING invocation row is committed (write-ahead); `posted["n"]` is incremented before the call, so the caller's
    `finally` ledgers every post even when this function raises (KeyboardInterrupt included). A RAISING invocation is a
    TRANSPORT error: logged (timestamp, class and message, payload sha, "TRANSPORT, no reply"), it does NOT consume an
    attempt, and the launch STOPS. Returns (new attempt rows, valid row or None, transport seq or None)."""
    posted = posted if posted is not None else {"n": 0}
    st = IC.state(conn)
    rows, valid = [], None
    call = guarded(call_full)
    for k in range(st["n_attempts"] + 1, MAX_ATTEMPTS + 1):
        if rr.payload_bytes(system, user) != body or hashlib.sha256(body).hexdigest() != sha:
            refuse("attempt %d: the body to post is not the registered body" % k)
        inv = _write_ahead(conn, sha)
        try:
            posted["n"] += 1
            content, provider, ctoks, lat, finish, msg = call(system, user)
        except Exception as e:  # noqa: BLE001  (SystemExit / KeyboardInterrupt are not Exceptions: they propagate)
            seq = IC.state(conn)["n_transport"] + 1
            conn.execute("INSERT INTO transport VALUES (?,?,?,?,?,?,?)", (seq, inv, _now(), sha, type(e).__name__,
                                                                        str(e)[:500], "TRANSPORT, no reply"))
            conn.commit()
            _event(conn, "transport_stop", "%d of %d" % (seq, MAX_TRANSPORT))
            out("[INDUCE-RUN] invocation %d: TRANSPORT ERROR %d of %d (%s: %s), payload sha256 %s, TRANSPORT, no reply: the"
                " launch STOPS fail-closed; the attempt is not consumed" % (inv, seq, MAX_TRANSPORT, type(e).__name__,
                                                                           str(e)[:120], sha))
            return rows, None, seq
        msg = msg or {}
        cls, _rubric = classify(content, finish, chosen)
        raw = content if content is not None else (msg.get("_refusal") or "")
        row = {"attempt_no": k, "payload_sha256": sha, "reply_sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
               "finish_reason": finish, "response_id": msg.get("_response_id"), "provider": provider,
               "completion_tokens": ctoks, "failure_class": cls, "reply_text": raw}
        posted_at = _now()
        conn.execute("INSERT INTO attempt (attempt_no, invocation_seq, posted_at, committed_at, payload_sha256, body_zlib,"
                     " reply_text, reply_sha256, finish_reason, response_id, provider, completion_tokens, latency_s,"
                     " failure_class) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                     (k, inv, posted_at, _now(), sha, zlib.compress(body, 6), raw, row["reply_sha256"], finish,
                      row["response_id"], provider, ctoks, float(lat) if isinstance(lat, (int, float)) else None, cls))
        conn.commit()
        fit = fitness_detail(raw) if cls in (None, "FITNESS") else None
        row["committed_at"] = _event(conn, "reply_committed" if cls is None else "attempt_committed",
                                     "attempt %d %s%s" % (k, cls or "VALID", (" | " + fit) if fit else ""))
        rows.append(row)
        out("[INDUCE-RUN] attempt %d of %d (invocation %d): finish_reason %r, response id %r, reply sha256 %s -> %s%s" % (
            k, MAX_ATTEMPTS, inv, finish, row["response_id"], row["reply_sha256"][:16],
            cls or "VALID (the reply of record)", (" | " + fit) if fit else ""))
        if cls is None:
            valid = row
            break
    return rows, valid, None


class Replay:
    """The model call handed to judge_v2.induction.induce AFTER the live attempt: it returns the stored reply of record
    and asserts the prompt is the posted one (zero calls; induce then re-runs the selection, the content-key checks and
    the verbatim audit and builds the artefact in its one format)."""

    def __init__(self, system, user, row, of_record):
        self.system, self.user, self.row = system, user, row
        self.calls = 0
        self.provenance = {"model": P.JUDGE_REQUESTED, "provider": row["provider"], "response_id": row["response_id"],
                           "finish_reason": row["finish_reason"], "attempt_of_record": row["attempt_no"],
                           "reply_sha256": row["reply_sha256"], "payload_sha256": row["payload_sha256"],
                           "max_tokens": P.CAP, "temperature_label": P.TEMPERATURE_LABEL, "of_record": of_record}

    def __call__(self, system, user):
        self.calls += 1
        if self.calls != 1 or system != self.system or user != self.user:
            refuse("replay: the artefact's prompt differs from the posted prompt (or a second call)")
        return self.row["reply_text"]


# ── (6) validity ─────────────────────────────────────────────────────────────────────────

def open_eval_for_audit(eval_path, eval_sha, conn=None, out=print):
    """Ruling on finding 3: the eval_view of record through data_v2.views.open_eval, expect_sha256 = the manifest of record's;
    the FLAG is set on open (no call_judge_full afterwards in this process); the open time is logged. Stage "judge" is a
    MISLABEL accepted for INDUCE-RUBRIC-1 only; for THIS run it is a DEVIATION that needs a NEW registrar bracket, named
    by the READY (VIEWS-AUDIT-STAGE is not merged; data_v2 / views.py are not edited)."""
    ev = dv2views.open_eval("judge", eval_path, eval_sha)
    _EVAL_OPENED["at"] = _now()
    if conn is not None:
        _event(conn, "eval_view_opened", "%s sha256 %s" % (os.path.basename(eval_path), eval_sha))
    out("[INDUCE-RUN] eval_view opened at %s: %s sha256_bytes %s (stage 'judge': %s; no call_judge_full is made after"
        " this point)" % (_EVAL_OPENED["at"], os.path.basename(eval_path), eval_sha, DISCLOSURE_STAGE))
    return ev


def _norm_text(x):
    return " ".join(str(x).casefold().split())


def reference_material(ev):
    """C2: every EVAL reference row rendered "(<answer>) <option text>" in its SOLVER's ordering (the solver's response
    row for the reference's legacy qid and variant, data_v2.ingest.SOLVER_MODEL, as loader.py renders it), and the option
    text itself; each kept when >= leakage.MIN_MATERIAL characters. Returns (set, counts)."""
    solver = {}
    for cv, q, v, sha in ev.execute("SELECT corpus_version, legacy_qid, seen_ck, options_ordered_sha FROM response WHERE"
                                    " model=?", (LD.dv2ingest.SOLVER_MODEL,)):
        solver[(cv, q, v)] = sha
    refs, n_rows, n_rendered, n_skipped = set(), 0, 0, 0
    for cv, vid, q, ans in ev.execute("SELECT corpus_version, variant_id, legacy_qid, answer FROM reference"):
        n_rows += 1
        a = (ans or "").strip()
        sha = solver.get((cv, q, vid))
        opts = LD._options_list(ev, sha) if sha is not None else None
        if not opts or not (len(a) == 1 and a in LD.LETTERS and LD.LETTERS.index(a) < len(opts)):
            n_skipped += 1
            if len(_norm_text(a)) >= L.MIN_MATERIAL:
                refs.add(_norm_text(a))
            continue
        n_rendered += 1
        for x in (LD.render_reference(a, opts), opts[LD.LETTERS.index(a)]):
            if len(_norm_text(x)) >= L.MIN_MATERIAL:
                refs.add(_norm_text(x))
    return refs, {"reference_rows": n_rows, "rendered": n_rendered, "not_renderable": n_skipped, "kept": len(refs)}


def eval_material(ev, eval_name, out=print):
    """V2's EVAL key material from an OPEN eval_view connection (closed by the caller): gt_raw / answer_text key
    renderings (loader.MATERIAL_FORMS), answer texts >= 12 characters, the EVAL reference rows (reference_material), the
    reference marker and the machine-field marker rules."""
    forms, texts, n_rows = set(), set(), 0
    for gt, at in ev.execute("SELECT DISTINCT gt_raw, answer_text FROM response"):
        n_rows += 1
        for v in (gt, at):
            if v:
                for f in LD.MATERIAL_FORMS["key"]:
                    forms.add(" ".join(f.format(v=v).casefold().split()))
        if at and len(" ".join(at.casefold().split())) >= L.MIN_MATERIAL:
            texts.add(" ".join(at.casefold().split()))
    refs, rc = reference_material(ev)
    out("[INDUCE-RUN] V2 material from %s: %d distinct (gt_raw, answer_text) pairs -> %d key renderings, %d answer texts of"
        " >= %d characters; EVAL reference rows %d (rendered in the solver's ordering %d, not renderable %d) -> %d reference"
        " strings; the reference marker, %d marker rules" % (eval_name, n_rows, len(forms), len(texts), L.MIN_MATERIAL,
                                                             rc["reference_rows"], rc["rendered"], rc["not_renderable"],
                                                             rc["kept"], len(L.MARKER_RULES)))
    return {"forms": forms, "texts": texts, "refs": refs, "ref_counts": rc}


def leak_check(rubric, material):
    """V2: the hits of the rubric text against the EVAL key material ([] passes)."""
    t = " ".join(rubric.casefold().split())
    hits = ["form:" + f for f in material["forms"] if f in t]
    hits += ["answer_text:" + x[:40] for x in material["texts"] if x in t]
    hits += ["reference:" + x[:40] for x in material.get("refs", ()) if x in t]
    if REFERENCE_MARKER.casefold() in rubric.casefold() or re.search(r"\[\s*Reference solution", rubric, re.I):
        hits.append("reference_marker")
    for name, rx in L._RULES:
        if rx.search(rubric):
            hits.append("marker:" + name)
    return sorted(hits)


# ── the launch ───────────────────────────────────────────────────────────────────────────

def _manifest_eval_sha(paths, eval_sha):
    if not paths.check_manifest:
        return eval_sha
    m = json.load(open(paths.manifest, encoding="utf-8"))
    got = {o.get("kind"): o.get("sha256_bytes") for o in m.get("outputs", [])}
    if got.get("eval_view") != EVAL_SHA:
        refuse("the manifest of record names eval_view %s, not the pinned %s" % (got.get("eval_view"), EVAL_SHA))
    return got["eval_view"]


def load_exclusions(paths, excl_sha, eval_sha, gen_sha, out=print):
    ex, rec = OA.load(paths.excl, excl_sha, eval_sha, gen_sha)
    out("[INDUCE-RUN] overlap exclusion list %s: sha256 %s = the pinned; built on eval_view %s; %d excluded" % (
        os.path.basename(paths.excl), rec["list_sha256"], rec["eval_view_sha256_bytes"], len(ex)))
    return ex, rec


def dry_run(paths=None, seed=SEED, registration=SELECT_REGISTRATION, gen_sha=GEN_SHA, eval_sha=EVAL_SHA, out=print,
            excl_sha=None):
    paths = paths or Paths()
    out("[INDUCE-RUN] %s DRY-RUN (posts nothing): gen_view %s (registered sha256_bytes %s)" % (TEST, paths.gen, gen_sha))
    if paths.check_manifest:
        check_manifest(paths, gen_sha, eval_sha, out)
    eval_sha = _manifest_eval_sha(paths, eval_sha)
    check_prompt_pins(out)
    excl = load_exclusions(paths, excl_sha or EXCL_SHA, eval_sha, gen_sha, out)
    chosen, witness, check, gmeta, label = select(paths.gen, gen_sha, seed, registration, out, excl)
    rec = ids_record(chosen)
    system, user, body, sha = build_payload(chosen)
    out("[INDUCE-RUN] input_variant_ids: n %d, sorted-set sha256 %s, ordered sha256 %s" % (
        rec["n"], rec["input_variant_ids_sha256"], rec["input_variant_ids_ordered_sha256"]))
    check_selection_pin(rec, registration, out)
    out("[INDUCE-RUN] payload: %d bytes, sha256 %s (model %s, max_tokens %d, temperature omitted); system sha256 %s, user"
        " sha256 %s" % (len(body), sha, P.JUDGE_REQUESTED, P.CAP, sha256_text(system), sha256_text(user)))
    out("[INDUCE-RUN] system turn (in full):\n" + system)
    out("[INDUCE-RUN] user turn (first 900 chars):\n" + user[:900])
    ev = open_eval_for_audit(paths.eval, eval_sha, None, out)
    try:
        mat = eval_material(ev, os.path.basename(paths.eval), out)
        sh = set()
        ut = I._tokens(user)
        sh.update(tuple(ut[i:i + I.SHINGLE]) for i in range(len(ut) - I.SHINGLE + 1))
        n_ev = n_hit = 0
        for (stem,) in ev.execute("SELECT DISTINCT stem FROM variant"):
            n_ev += 1
            t = I._tokens(stem)
            if any(tuple(t[i:i + I.SHINGLE]) in sh for i in range(len(t) - I.SHINGLE + 1)):
                n_hit += 1
        out("[INDUCE-RUN] EVAL variant stems sharing an %d-token run with the user turn: %d of %d (the review's row 4 count"
            " at the narrowed population; V1's audit refuses a rubric that copies one)" % (I.SHINGLE, n_hit, n_ev))
    finally:
        ev.close()
    return {"payload_sha256": sha, "ids": rec, "material_sizes": (len(mat["forms"]), len(mat["texts"])),
            "witness": witness, "check": check, "body": body, "ref_counts": mat["ref_counts"], "overlap": (n_hit, n_ev)}


def _launch_state(paths, rec, sha):
    """'fresh' (no output exists) or 'relaunch' (a TRANSPORT stop left the cache: the SAME ids, the SAME body, no valid
    reply, fewer than 3 attempts and fewer than 3 transport errors, no outcome and no artefact). Anything else REFUSES."""
    if not os.path.exists(paths.cache):
        for p in (paths.ids, paths.artefact, paths.outcome):
            if os.path.exists(p):
                refuse("%s exists without an attempt cache: refused" % p)
        return "fresh", None
    for p in (paths.artefact, paths.outcome):
        if os.path.exists(p):
            refuse("%s exists: the run reached its outcome; every output is written once" % p)
    old = json.load(open(paths.ids, encoding="utf-8")) if os.path.exists(paths.ids) else None
    if old is None or old.get("input_variant_ids") != rec["input_variant_ids"]:
        refuse("relaunch: the input ids differ from the first launch's (a relaunch never re-selects)")
    conn = IC.reopen(paths.cache)
    st = IC.state(conn)
    if st["meta"].get("payload_sha256") != sha:
        conn.close()
        refuse("relaunch: the payload sha256 %s is not the first launch's %s (the IDENTICAL body is re-posted, asserted)"
               % (sha, st["meta"].get("payload_sha256")))
    if st["valid"] or st["n_attempts"] >= MAX_ATTEMPTS:
        conn.close()
        refuse("relaunch: the run already has %s" % ("a valid reply" if st["valid"] else "3 attempts"))
    if st["n_transport"] >= MAX_TRANSPORT:
        conn.close()
        refuse("relaunch: %d transport errors: UNDETERMINED BY INSTRUMENT; a further relaunch needs a registrar bracket"
               % st["n_transport"])
    if st["n_transport"] + len(st["orphans"]) > MAX_TRANSPORT:
        conn.close()
        refuse("relaunch: %d transport error(s) and %d orphan invocation(s) exceed the transport limit %d"
               % (st["n_transport"], len(st["orphans"]), MAX_TRANSPORT))
    return "relaunch", conn


def run(call_full, expect_payload_sha, paths=None, seed=SEED, registration=SELECT_REGISTRATION, gen_sha=GEN_SHA,
        eval_sha=EVAL_SHA, ledger_dir=None, atl=None, out=print, excl_sha=None):
    """The live launch (call_full = rejudge_reasoning.call_judge_full in production; a stub in the selftest)."""
    paths = paths or Paths()
    if not callable(call_full):
        refuse("run: call_full must be rejudge_reasoning.call_judge_full (or the selftest's stub)")
    if paths.check_manifest:
        check_manifest(paths, gen_sha, eval_sha, out)
    eval_sha = _manifest_eval_sha(paths, eval_sha)
    check_prompt_pins(out)
    excl = load_exclusions(paths, excl_sha or EXCL_SHA, eval_sha, gen_sha, out)
    chosen, witness, check, gmeta, label = select(paths.gen, gen_sha, seed, registration, out, excl)
    rec = ids_record(chosen)
    check_selection_pin(rec, registration, out)
    system, user, body, sha = build_payload(chosen)
    out("[INDUCE-RUN] payload sha256 %s; registered (--expect-payload-sha) %s" % (sha, expect_payload_sha))
    if sha != expect_payload_sha:
        refuse("the payload sha256 %s is not the registered %s: nothing is posted" % (sha, expect_payload_sha))
    kind, conn = _launch_state(paths, rec, sha)
    st = IC.state(conn) if conn is not None else {"n_attempts": 0, "n_transport": 0, "n_invocations": 0, "orphans": []}
    planned = MAX_ATTEMPTS - st["n_attempts"]
    if atl is not None:
        # ruling 1 (b) of the READY review: the day ledgers' count for this test equals the invocations the cache records
        # (0 on a fresh launch); a lost, moved or never-written cache row cannot reset the limits
        led = atl.ledger_calls(TEST, ledger_dir)
        out("[INDUCE-RUN] ledger equality: day ledgers hold %d invocation(s) for %s; the cache records %d (%s launch)"
            % (led, TEST, st["n_invocations"], kind))
        if led != st["n_invocations"]:
            if conn is not None:
                conn.close()
            refuse("[ACCOUNT] REFUSED (0 calls posted): the day ledgers hold %d invocation(s) for %s but the cache records %d"
                   % (led, TEST, st["n_invocations"]))
        try:
            atl.guard(TEST, planned, {}, ledger_dir, "--run --go (%s)" % kind)   # ruling 1 (a): (i) REFUSES (ceiling 6)
        except SystemExit:
            if conn is not None:
                conn.close()
            raise
    if kind == "fresh":
        os.makedirs(paths.out, exist_ok=True)
        with open(paths.ids, "x", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(rec, indent=1, sort_keys=True) + "\n")
        meta = {"registration": TEST, "gen_view_sha256_bytes": gen_sha, "eval_view_sha256_bytes": eval_sha, "seed": seed,
                "seed_label": label, "n": N, "payload_sha256": sha, "system_sha256": SYSTEM_SHA,
                "user_template_sha256": USER_TEMPLATE_SHA, "judge_requested": P.JUDGE_REQUESTED, "max_tokens": P.CAP,
                "temperature_label": P.TEMPERATURE_LABEL, "max_attempts": MAX_ATTEMPTS, "max_transport": MAX_TRANSPORT,
                "script_blob": git_blob_lf(os.path.abspath(__file__)), "induction_blob": git_blob_lf(I.__file__),
                "fitness_blob": git_blob_lf(F3.__file__), "fitness_base_blob": git_blob_lf(F.__file__),
                "cache_blob": git_blob_lf(IC.__file__),
                "induction_version": I.INDUCTION_VERSION, "descriptions_sha256": DESCRIPTIONS_SHA,
                "v5_regex_list_sha256": V5_LIST_SHA, "v5_control_sha256": F.CONTROL_FIT_SHA256,
                "selection_of_record_from": SELECTION_OF_RECORD_FROM,
                "input_variant_ids_sha256": rec["input_variant_ids_sha256"], "disclosure": DISCLOSURE}
        conn = IC.create(paths.cache, meta)
    _event(conn, "launch", kind)
    posted, tseq = {"n": 0}, None
    try:
        if kind == "relaunch":
            resolve_orphans(conn, out)
        st = IC.state(conn)
        if st["n_transport"] < MAX_TRANSPORT:
            rows, valid, tseq = attempts(conn, call_full, system, user, body, sha, chosen, out, posted)
        else:
            rows, valid = [], None
        st = IC.state(conn)
        if tseq is not None and tseq < MAX_TRANSPORT:
            lines = ["%s TRANSPORT STOP %d of %d (not an outcome): payload sha256 %s; TRANSPORT, no reply; attempts so far %d;"
                     " a relaunch re-posts the IDENTICAL body" % (TEST, tseq, MAX_TRANSPORT, sha, st["n_attempts"])]
            with open(os.path.join(paths.out, "transport_stop_%d.txt" % tseq), "x", encoding="utf-8", newline="\n") as f:
                f.write("\n".join(lines) + "\n")
            for ln in lines:
                out(ln)
            return {"rows": rows, "valid": None, "stopped": True, "transport_seq": tseq, "validity": {}, "outcome_lines": lines}
        all_rows = [dict(zip(("attempt_no", "failure_class", "finish_reason", "response_id", "reply_sha256", "reply_text",
                                "provider", "payload_sha256", "committed_at"), r)) for r in conn.execute(
            "SELECT attempt_no, failure_class, finish_reason, response_id, reply_sha256, reply_text, provider, payload_sha256,"
            " committed_at FROM attempt ORDER BY attempt_no")]
        transport = conn.execute("SELECT seq, at, exception_class, message FROM transport ORDER BY seq").fetchall()
        valid_row = next((r for r in all_rows if r["failure_class"] is None), None)
        if valid_row is not None:
            # the commit time of the cached reply: the event written right AFTER its insert was committed
            valid_row["committed_at"] = conn.execute("SELECT at FROM event WHERE what='reply_committed' ORDER BY seq DESC"
                                                     " LIMIT 1").fetchone()[0]
        res = finish(conn, all_rows, valid_row, transport, system, user, chosen, rec, paths, seed, registration, gen_sha,
                     eval_sha, witness, check, out, excl)
        if res["validity"].get("V2") is False:
            out("[INDUCE-RUN] V2 FAILED: the artefact is NOT OF RECORD; never a formal failure and NEVER a re-post (ruling on"
                " finding 3 (ii)); the slot takes the FALLBACK: %s" % FALLBACK)
        return res
    finally:
        if conn is not None:
            conn.close()
        if atl is not None and posted["n"]:
            atl.append(TEST, "--run --go", posted["n"], ledger_dir)


def finish(conn, rows, valid, transport, system, user, chosen, rec, paths, seed, registration, gen_sha, eval_sha, witness,
           check, out=print, excl=None):
    v = {"V1": None, "V2": None, "V3": None, "V4": None, "V5": None}
    art, hits, order, v5res = None, None, None, None
    if valid is not None:
        rp = Replay(system, user, valid, "REGISTERED %s (attempt %d of record)" % (TEST, valid["attempt_no"]))
        art = I.induce(CORPUS_TYPE, rp, paths.gen, gen_sha, n=N, seed=seed, registration=registration, out=out,
                       population=POPULATION, label=ARTEFACT_LABEL, exclude=excl[0],
                       exclude_ref={"list_sha256": excl[1]["list_sha256"], "n_excluded": len(excl[0]),
                                    "threshold": OA.THRESHOLD, "file": os.path.basename(paths.excl)})
        m = art["manifest"]
        if m["input_variant_ids_ordered_sha256"] != rec["input_variant_ids_ordered_sha256"] or \
                m["prompt_system_sha256"] != sha256_text(system) or m["prompt_user_sha256"] != sha256_text(user):
            refuse("the artefact's inputs or prompt differ from the posted ones")
        v["V1"] = bool(m["verbatim_audit"]["hits"] == 0 and not I.verbatim_audit(art["rubric"], chosen))
        # V5 re-checked on the reply of record (classify() already required it: a VALID class implies V5 PASS)
        v5res = F3.v5(art["rubric"])
        v["V5"] = bool(v5res["pass"])
        # ruling on finding 3 (i): ORDER, WITNESSED: the cached reply's commit time, then the eval_view open time
        out("[INDUCE-RUN] V2 order witness: the reply of record (attempt %d) committed to the attempt cache at %s"
            % (valid["attempt_no"], valid["committed_at"]))
        ev = open_eval_for_audit(paths.eval, eval_sha, conn, out)
        try:
            hits = leak_check(art["rubric"], eval_material(ev, os.path.basename(paths.eval), out))
        finally:
            ev.close()
        order = (valid["committed_at"], _EVAL_OPENED["at"])
        if not order[0] < order[1]:
            refuse("V2 order: the eval_view open time %s is not after the reply's commit time %s" % (order[1], order[0]))
        v["V2"] = bool(not hits)
        v["V3"] = bool(check["eval_hits"] == 0 and check["not_gen_side"] == 0 and witness.get("train_candidates", 0) >= N)
        if v["V1"] and v["V2"] and v["V3"] and v["V5"]:
            I.write_artefact(art, paths.artefact)
            v["V4"] = bool(os.path.exists(paths.artefact) and
                           I.load_artefact(paths.artefact, art["artefact_sha256"]).rubric_sha256 == art["rubric_sha256"])
        else:
            v["V4"] = False
    lines = outcome_lines(rows, valid, transport, v, art, hits, rec, witness, check, order, eval_sha, v5res)
    with open(paths.outcome, "x", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    for ln in lines:
        out(ln)
    return {"rows": rows, "valid": valid, "stopped": False, "transport": transport, "validity": v, "artefact": art,
            "hits": hits, "outcome_lines": lines, "order": order, "v5": v5res}


def outcome_lines(rows, valid, transport, v, art, hits, rec, witness, check, order, eval_sha, v5res=None):
    L_ = ["%s OUTCOME (zero-call validity; %d attempt(s) with a reply, %d transport error(s))" % (TEST, len(rows),
                                                                                              len(transport))]
    for d in DISCLOSURES_RULING:
        L_.append("  DISCLOSURE (the -3 registration): %s" % d)
    L_.append("  DISCLOSURE (carried, the selection of record is %s's): %s" % (SELECTION_OF_RECORD_FROM, DISCLOSURE))
    L_.append("  DISCLOSURE (carried): %s" % DISCLOSURE_C4)
    L_.append("  DISCLOSURE (carried): %s" % DISCLOSURE_C5)
    L_.append("  DISCLOSURE (carried): %s" % (DISCLOSURE_D1 % witness.get("replaced", 0)))
    L_.append("  DISCLOSURE (deviation): %s" % DISCLOSURE_STAGE)
    L_.append("  ARTEFACT LABEL: %s; population %s" % (ARTEFACT_LABEL, json.dumps(POPULATION, sort_keys=True)))
    L_.append("  INSTRUMENT: INDUCTION_VERSION %s; INDUCTION_SYSTEM sha256 %s; INDUCTION_USER_TEMPLATE sha256 %s; contract"
              " descriptions sha256 %s; V5 regex list sha256 %s" % (INDUCTION_VERSION, SYSTEM_SHA, USER_TEMPLATE_SHA,
                                                                 DESCRIPTIONS_SHA, V5_LIST_SHA))
    for r in rows:
        L_.append("  attempt %d: finish_reason %r, response id %r, reply sha256 %s, class %s" % (
            r["attempt_no"], r["finish_reason"], r["response_id"], r["reply_sha256"], r["failure_class"] or "VALID"))
        if r["failure_class"] in (None, "FITNESS"):
            fd = fitness_detail(r.get("reply_text"))
            if fd:
                L_.append("    attempt %d %s" % (r["attempt_no"], fd))
    for seq, at, cls, msg in transport:
        L_.append("  transport error %d at %s: %s: %s (%s; not an attempt)" % (
            seq, at, cls, msg[:120], "TRANSPORT, no reply recorded (orphan invocation)" if cls == "ORPHAN" else
            "TRANSPORT, no reply"))
    L_.append("  input_variant_ids: n %d, sorted-set sha256 %s, ordered sha256 %s" % (
        rec["n"], rec["input_variant_ids_sha256"], rec["input_variant_ids_ordered_sha256"]))
    by_instrument = bool(valid is None and len(transport) >= MAX_TRANSPORT)
    undetermined = bool(valid is None and not by_instrument and len(rows) >= MAX_ATTEMPTS)
    if valid is not None:
        L_.append("  the reply of record: attempt %d (the FIRST valid reply, V5 included; no best-of-n, no edit)"
                  % valid["attempt_no"])
    if by_instrument:
        L_.append("  UNDETERMINED BY INSTRUMENT: %d transport errors (not by the model); a further relaunch needs a registrar"
                  " bracket" % len(transport))
    if undetermined:
        L_.append("  UNDETERMINED: three formal failures; the slot takes the FALLBACK (GENERIC_RUBRIC, sha256 %s; no"
                  " further author question)." % GENERIC_RUBRIC_SHA256)
    if order is not None:
        L_.append("  V2 order witness: reply committed %s < eval_view opened %s; eval_view sha256_bytes %s (the manifest of"
                  " record; stage 'judge': the deviation above)" % (order[0], order[1], eval_sha))
    L_.append("  V1 verbatim audit (SHINGLE %d): %s" % (I.SHINGLE, _pf(v["V1"])))
    L_.append("  V2 leak check against EVAL key material: %s%s" % (_pf(v["V2"]), (" hits %s" % hits[:6]) if hits else ""))
    if v["V2"] is False:
        L_.append("  V2 FAILED: the artefact is NOT OF RECORD (never a formal failure, never a re-post); the slot takes"
                  " the FALLBACK (GENERIC_RUBRIC, sha256 %s)" % GENERIC_RUBRIC_SHA256)
    L_.append("  V3 content-key counts: candidate rows %s, distinct variants %s, duplicates collapsed %s, skipped by"
              " component %s, GATE refused %s, other non-TRAIN %s, EVAL hits %s, not TRAIN %s: %s" % (
                  witness.get("candidate_rows"), witness.get("distinct_variants"), witness.get("duplicates_collapsed"),
                  witness.get("skipped_by_component"), witness.get("gate_excluded"), witness.get("other_excluded"),
                  check.get("eval_hits"), check.get("not_gen_side"), _pf(v["V3"])))
    L_.append("  V4 artefact written with mode x: %s%s" % (_pf(v["V4"]), (" artefact_sha256 %s rubric_sha256 %s" % (
        art["artefact_sha256"], art["rubric_sha256"])) if (art is not None and v["V4"]) else ""))
    L_.append("  V5 FITNESS on the reply of record (regex list sha256 %s): %s%s" % (
        V5_LIST_SHA, _pf(v["V5"]), (" | " + F3.describe(v5res)) if v5res is not None else ""))
    L_.append("  V5 SCOPE (F1b change 7, carried): %s" % V5_SCOPE)
    of_record = bool(valid is not None and v["V1"] and v["V2"] and v["V3"] and v["V4"] and v["V5"])
    L_.append("  ARTEFACT OF RECORD: %s" % ("YES" if of_record else "NO (not of record)"))
    p1 = bool(len(rows) >= 1 and rows[0]["failure_class"] is None)
    if not rows:
        L_.append("  P1 (the first attempt is valid, V5 included; point probability %.2f): NOT SCORED (no reply)" % P1_POINT)
    elif p1:
        L_.append("  P1 (the first attempt is valid, V5 included; point probability %.2f): HELD" % P1_POINT)
    else:
        L_.append("  P1 (the first attempt is valid, V5 included; point probability %.2f): FAILED" % P1_POINT)
    p2 = bool(valid is not None and v["V1"] and v["V2"] and v["V3"] and v["V4"] and v["V5"])
    if valid is None:
        L_.append("  P2 (V1-V5 pass; point probability %.2f): NOT SCORED (no valid reply)" % P2_POINT)
    elif p2:
        L_.append("  P2 (V1-V5 pass; point probability %.2f): HELD" % P2_POINT)
    else:
        L_.append("  P2 (V1-V5 pass; point probability %.2f): FAILED" % P2_POINT)
    L_.append("  P3 (the checklist reads FIT in both readings; point probability %.2f): NOT SCORED BY THIS INSTRUMENT (%s)"
              % (P3_POINT, "scored by the post-run reading of the artefact of record" if of_record else
                 "no artefact of record: the reading does not take place; the FALLBACK applies"))
    L_.append("  CHECKLIST: %s" % CHECKLIST)
    if undetermined:
        L_.append("  FALSIFIER (three formal failures): FIRED: the plan of the author's decision (1) of 2026-09-25 to fill"
                  " the slot by a third induction is overturned; the slot takes the FALLBACK")
    else:
        L_.append("  FALSIFIER (three formal failures): NOT FIRED%s" % (" (UNDETERMINED BY INSTRUMENT does not fire it)"
                                                                        if by_instrument else ""))
    L_.append("  FALLBACK: %s" % FALLBACK)
    L_.append("  LABEL: a RECIPE COMPONENT; no rubric-value or accuracy claim.")
    return L_


def _pf(x):
    return "PASS" if x is True else ("FAIL" if x is False else "NOT RUN")


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--run", action="store_true")
    g.add_argument("--selftest", action="store_true")
    ap.add_argument("--go", action="store_true")
    ap.add_argument("--expect-payload-sha")
    ap.add_argument("--transcript")
    a = ap.parse_args(argv)
    if a.selftest:
        from . import induce_run_3_selftest as S
        return S.main(["--transcript", a.transcript] if a.transcript else [])
    if a.dry_run:
        r = dry_run()
        print("[INDUCE-RUN] DRY-RUN done: payload sha256 %s; 0 calls" % r["payload_sha256"])
        return 0
    if not a.go or not a.expect_payload_sha:
        refuse("--run needs --go and --expect-payload-sha <the registered payload sha>")
    import accepted_tests_ledger as atl
    rr.load_env()
    res = run(rr.call_judge_full, a.expect_payload_sha, ledger_dir=os.path.join(_data_root(), "experiment_results"),
              atl=atl)
    return 0 if res.get("valid") is not None else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
