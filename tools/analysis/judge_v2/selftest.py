"""judge_v2.selftest: the E-J selftest. SYNTHETIC ONLY: no DB of record is opened, no call is posted (a fake call_full).

    python tools/analysis/judge_v2/selftest.py [--transcript PATH]
    python -O tools/analysis/judge_v2/selftest.py [--transcript PATH]

Every guard in judge_v2 refuses by raise SystemExit (never an assert), so the -O run exercises the same branches; this file
uses no assert either (each check is an explicit comparison, printed PASS / FAIL, counted).

FIXTURE. The E-D selftest fixture (data_v2.gates._fixture: two tiny source DBs with the schemas of record, written as NEW
files in a temporary directory) plus 12 extra MMLU-Pro rows with NO response (so the EVAL ones are routing-only
SENTINELS), run through E-D's own ingest -> split (seed DEV-selftest-ej) -> gen_view / eval_view. Everything lives under
tempfile.gettempdir() and is removed at the end.

CHECKS (the six the E-J brief names, and the controls that make them non-vacuous):
  S1 payload sha stability: the same inputs give the same body and sha twice; the pinned GOLDEN sha of a fixed synthetic
     payload holds (a template / builder / json change moves it); order 1 != order 2; a one-character trace change moves
     the sha; the body is rr.payload_bytes; temperature absent; zlib round trip; rr.TEMPERATURE = 0.0 is refused; the R9
     refusals (wrong-variant reference, response-bound reference, a question of another stem).
  S2 leakage: a clean payload passes with material supplied; each leak class is REFUSED before any call: per-side checker
     outcome in a trace, a machine verdict field, a reference for the wrong side, a second reference block, a tampered
     body (extra key / edited system), a verdict tag in the rubric; unscannable material refused; a leaking spec stops the
     writer's pre-scan with ZERO posts.
  S3 writer: a truncated response (finish_reason length) is stored NON_TERMINATED and a content-filter refusal
     CONTENT_FILTER (http 400, content_filter 1), neither TIE; the combiner and data_v2's match_verdict view both read
     those matches as NON_TERMINATED / CONTENT_FILTER; per-row provenance; the relaunch posts ONLY the pending (errored)
     slot, never the cached CONTENT_FILTER, and a complete run posts NOTHING; a relaunch with another rubric or other
     inputs is refused; R7: two draws of one body are two rows.
  S4 combiner: 16 / 16 equal to rejudge_grok.combine_orders on the shared domain; the AST pin holds (and a wrong pin is
     refused); a mutant combiner FAILS the table (the test discriminates); NON_TERMINATED / CONTENT_FILTER never TIE over
     all 36 pairs; the combiner equals data_v2's match_verdict view on all 36 pairs.
  S5 induction: reads through open_generation("induce"); a stub induction writes a write-once artefact that round-trips;
     an EVAL item handed to it is REFUSED, a SENTINEL is REFUSED, a GATE item (default sides TRAIN) and a foreign text are
     REFUSED by the content-key leg (b); the eval_view path is refused by its own meta; 'agentic' has no contract and
     is refused; the verbatim-copy audit fires on a copied run.
  [ADDED 2026-09-24, ruling 4aac08e on E-J choice 2 (the induced artefact fills the RUBRIC slot only): S1 checks the system
  turn is the v2 template with the FIXED persona in $systemPrompt and the artefact in $rubric only, refuses an artefact
  carrying a system_prompt field or an unknown field, and proves the GOLDEN re-pin moved only the persona slot; S5 checks
  the induced artefact and prompt carry no system_prompt and refuses a reply, and a written artefact, carrying one.]
  [ADDED 2026-09-24 on READY_archv2_EJ (2aba3ab) C1-C8, insertion only. The fixture now runs against MAIN's data_v2
  (d98b247) with its own repo_root (C8), mA's output on rows 51-60 carries its own key as "answer_text: xN" (a
  material-only leak, C3), and Q8's ordered options are rotated to ["y8", "w8", "x8"] for every active model (so the
  solver's ordering differs from options_sorted). S1 adds the reference stem_key / kind / ordering / side refusals (C7).
  S2's writer-level leak moved to S6 (the writer takes only loader-built matches now). S3 runs on loader-built matches and
  witnesses the scan counts (C2: pre-scan scans == pending, poster scans == posts, every scan with material) and C8's
  match_verdicts (run_id, match_status). S5 adds the registered-seed rules, the fixture GOLDEN of the selection (C6), the
  TRAIN-only witness, a GATE item on the SELECTED path, probe D and the options checks (C5). S6 (new): choose_reference
  unit by unit (the ruling), the loader on the fixture (v0 chosen, the solver's ordering, NONE counted), probes A and B,
  material NONE declared, and a key-material leak in the last slot refused with zero posts. S7 (new): INSERT OR REPLACE /
  REPLACE / UPDATE / DELETE on a stored verdict all abort (C1). [ADDED 2026-09-24 on the delta-2 review d429c4b E1 / E2: the
  whole-load refusals of every choose_reference refusal (P1), of a broken solver join (P2), of an unexpected / mis-classed /
  missing exclusion against expected_exclusions, of a 0-match load, and of an empty Loaded at create (probe 4); the
  case-insensitive BBH source; mixed_strata's schema check.] S8 (new): lint_opens finds 0 on the checkout and refuses
  a planted data_v2.ro.open_ro call and a planted corpus_v2 connect (C4).]
"""
import dataclasses
import hashlib
import json
import os
import shutil
import sys
import tempfile
import zlib

if __name__ == "__main__" and not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    __package__ = "judge_v2"
    import judge_v2  # noqa: F401

from ._base import dv2c, dv2ro, dv2verdicts, dv2views, git_blob_lf, rr, HERE  # noqa: E402
from . import combiner as K  # noqa: E402
from . import induction as I  # noqa: E402
from . import leakage as L  # noqa: E402
from . import loader as LD  # noqa: E402
from . import payload as P  # noqa: E402
from . import writer as W  # noqa: E402
from data_v2 import gates as dv2gates, ingest as dv2ingest, split as dv2split  # noqa: E402

# sha256 of the exact body bytes of gold_inputs() under gold_rubric() (python 3.11.1).
# First pinned at 9d993cc: order1 3f66740e75297830da4a7689c51c38902bf8aa8cc68e7d9885cc271ca0e7f84c,
#                          order2 c4b3809fdbbef0c3579e3a636a062e172c00248a2adc7f6beceb7dc759d77398.
# RE-PINNED 2026-09-24 after the ruling on E-J choice 2 (4aac08e: the induced artefact fills the RUBRIC slot only): the
# $systemPrompt slot now carries the fixed persona _base.FIXED_SYSTEM_PERSONA (rubric_value_contrast.GENERIC_SYSTEM)
# instead of the gold artefact's own system_prompt ("You are an impartial evaluator of mcq responses."). That is the ONLY
# byte change: substituting the old persona back into the new builder's system turn, with the new user turn unchanged,
# reproduces both old shas exactly (the S1 check "GOLDEN re-pin moved ONLY the persona slot" executes this).
GOLDEN = {"order1": "35d594637a780e814718f40f406ba895179bdaa8578d897265f80fb559ad240c",
          "order2": "3d6e8703fceb75994b619eec3d3d8cee0a573ccfa33cebab9445adb89ed1477d"}
GOLDEN_V1 = {"order1": "3f66740e75297830da4a7689c51c38902bf8aa8cc68e7d9885cc271ca0e7f84c",
             "order2": "c4b3809fdbbef0c3579e3a636a062e172c00248a2adc7f6beceb7dc759d77398"}
GOLDEN_V1_PERSONA = "You are an impartial evaluator of mcq responses."


class Checks:
    def __init__(self, out):
        self.out = out
        self.n = 0
        self.fails = []

    def check(self, name, ok, detail=""):
        self.n += 1
        ok = bool(ok)
        self.out("[SELFTEST-EJ] %s %s%s" % ("PASS" if ok else "FAIL", name, (" | " + detail) if detail else ""))
        if not ok:
            self.fails.append(name)
        return ok

    def refused(self, name, fn, must_contain=()):
        try:
            fn()
        except SystemExit as e:
            msg = str(e)
            ok = all(s in msg for s in must_contain)
            return self.check(name + " -> REFUSED", ok, msg[:150])
        return self.check(name + " -> REFUSED", False, "no refusal")


def _rmtree(p):
    def onerr(fn, path, _exc):
        try:
            os.chmod(path, 0o666)
            fn(path)
        except OSError:
            pass
    shutil.rmtree(p, onerror=onerr)


# ── the fixture ───────────────────────────────────────────────────────────────────────────

N_SENTINEL_ROWS = 12
LEAK_RIDS = tuple(range(51, 61))   # mA's output on these fixture rows carries its own key in a machine rendering (C3)


D1_WRONG_QIDS = (102, 106, 108, 115)   # mB's pred A != the key B on the S3 questions (D1)


def leak_line(rid):
    return "answer_text: x%d" % rid


def build_views(tmp, extra_mmlu=0):
    """extra_mmlu: that many more MMLU-Pro rows WITHOUT responses (induce_run_selftest's population fixture needs >= 40
    mmlu-pro-v2 MC_LETTER TRAIN variants); 0 (E-J's default) leaves the fixture unchanged."""
    data_root = os.path.join(tmp, "data")
    build = os.path.join(tmp, "build")
    os.mkdir(data_root)
    os.mkdir(build)
    dv2gates._fixture(data_root)
    cw = dv2ro.open_scratch_rw(os.path.join(data_root, "mmlu_pro_dataset_cache_v2.db"))
    for i in range(extra_mmlu):
        # every 3rd row carries an 8-token boilerplate (an overlap of exactly 8 between a TRAIN and an EVAL row), every 3rd
        # + 1 a 7-token one (below the D1 threshold): the overlap audit's positive and negative controls
        tail = (" alpha beta gamma delta epsilon zeta eta theta" if i % 3 == 0 else
                " iota kappa lambda mu nu xi omicron" if i % 3 == 1 else "")
        cw.execute("INSERT INTO mmlu_pro (question, category, cot_content, options, answer) VALUES (?,?,?,?,?)",
                   ("Extra population question number %d on law, case %d%s?" % (i, i, tail), "law", "",
                    json.dumps(["pa%d" % i, "pb%d" % i, "pc%d" % i]), "B"))
    for i in range(N_SENTINEL_ROWS):
        cw.execute("INSERT INTO mmlu_pro (question, category, cot_content, options, answer) VALUES (?,?,?,?,?)",
                   ("Sentinel routing question %d about law, never answered?" % i, "law", "",
                    json.dumps(["s%d" % i, "t%d" % i]), "A"))
    cw.execute("UPDATE eval_results SET options_json=? WHERE question_id=108 AND model_name != 'Meta-Llama-3-70B-Instruct'",
               (json.dumps(["y8", "w8", "x8"]),))
    for rid in LEAK_RIDS:
        cw.execute("UPDATE eval_results SET model_output = model_output || ? WHERE question_id=? AND model_name='mA'",
                   ("\n" + leak_line(rid), 100 + rid))
    # D1: mB answers A (wrong) where the key is B, on the four S3 questions: a trace must show the contestant's pred
    cw.execute("UPDATE eval_results SET pred='A', is_correct=0 WHERE model_name='mB' AND question_id IN (%s)"
               % ",".join(str(q) for q in D1_WRONG_QIDS))
    # D5: mB saw Q25's options in another order than mA and the solver (a MIXED referenced match)
    cw.execute("UPDATE eval_results SET options_json=? WHERE model_name='mB' AND question_id=125",
               (json.dumps(["x25", "y25", "w25"]),))
    # D5 ruling (3): Q42 has no reference; mB saw another ordering: a MIXED no-reference match is ALLOWED
    cw.execute("UPDATE eval_results SET options_json=? WHERE model_name='mB' AND question_id=142",
               (json.dumps(["x42", "w42", "y42"]),))
    # D5 ruling (1): mB's Q6 options differ from the solver's by whitespace only: byte-different, the SAME ordering
    cw.execute("UPDATE eval_results SET options_json=? WHERE model_name='mB' AND question_id=106",
               (json.dumps(["w6 ", "x6", " y6"]),))
    cw.commit()
    cw.close()
    js = os.path.join(data_root, "experiment_results", "judge_solve")
    # the v0 reference of Q8 answers C (a WRONG reference: the key is B), so reference != key is witnessed
    c0 = dv2ro.open_scratch_rw(os.path.join(js, "grok-reasoning.db"))
    c0.execute("UPDATE answers SET answer='C' WHERE question_id=108")
    # Q6's v0 reference answers A, whose option carries whitespace in mB's (same-key) ordering: the rendering must use the
    # SOLVER's list verbatim, "(A) w6", never a contestant's "(A) w6 " (kills N3r)
    c0.execute("UPDATE answers SET answer='A' WHERE question_id=106")
    c0.commit()
    c0.close()
    # D2: the v1 reference of Q2 answers C: another vintage's reference that differs from the chosen v0 block
    c1 = dv2ro.open_scratch_rw(os.path.join(js, "grok-reasoning-v1.db"))
    c1.execute("UPDATE answers SET answer='C' WHERE question_id=102")
    c1.commit()
    c1.close()
    quiet = lambda s: None  # noqa: E731
    repo_root = os.path.join(tmp, "repo")   # C8: the fixture's own id file (gates._fixture writes it), never the checkout's
    paths = [dv2ingest.build_corpus(cv, build, out=quiet, data_root=data_root, repo_root=repo_root)["path"]
             for cv in ("mmlu-pro-v2", "mc6-2026-09-11")]
    sp = dv2split.build_split(paths, build, "DEV-selftest-ej", out=quiet)
    gv = dv2views.build_view("gen", paths, sp["path"], build, out=quiet)
    ev = dv2views.build_view("eval", paths, sp["path"], build, out=quiet)
    return gv["path"], ev["path"]


def eval_variants(ev_path):
    """EVAL variants of the eval_view: judgeable MC_LETTER ones and routing-only sentinels."""
    c = dv2views.open_eval("judge", ev_path)
    try:
        seen = {v for (v,) in c.execute("SELECT DISTINCT r.seen_ck FROM response r JOIN model_registry m ON"
                                        " m.corpus_version = r.corpus_version AND m.model = r.model WHERE m.status='ACTIVE'")}
        rows = c.execute("SELECT variant_id, item_id, stem, options_sorted_json, contract_id FROM variant ORDER BY variant_id").fetchall()
    finally:
        c.close()
    judgeable = [r for r in rows if r[0] in seen and r[4] == "MC_LETTER"]
    sentinels = [r for r in rows if r[0] not in seen]
    return judgeable, sentinels


def gen_items(gen_path):
    c = dv2views.open_generation("construct", gen_path)
    try:
        rows = c.execute("SELECT v.variant_id, v.item_id, v.stem, v.options_sorted_json, v.contract_id, s.side FROM variant v"
                         " JOIN side s ON s.item_id = v.item_id ORDER BY v.variant_id").fetchall()
    finally:
        c.close()
    return rows


def _as_input(r):
    return {"variant_id": r[0], "item_id": r[1], "stem": r[2], "options": json.loads(r[3]) if r[3] else [],
            "contract_id": r[4]}


# ── S1 / S2 synthetic payloads ────────────────────────────────────────────────────────────

GOLD_Q = "Which planet is closest to the Sun in the Solar System?"


def gold_rubric():
    rb = "1. Correct final answer first.\n2. Otherwise TIE."
    return P.load_rubric({"corpus_type": "mcq", "rubric": rb, "rubric_sha256": P.rubric_sha(rb)})


def gold_inputs(**kw):
    sk = dv2c.KeyCache().stem(GOLD_Q)
    vid = "v:gold-variant"
    base = dict(match_id="gold-1", variant_id=vid, stem_key=sk, component_id="c:" + sk, corpus_type="mcq", question=GOLD_Q,
                contestant_a="model-alpha", contestant_b="model-beta",
                trace_a="Mercury orbits closest.\n\n[This model's selected answer: (A) Mercury]",
                trace_b="Venus is hottest, so Venus.\n\n[This model's selected answer: (B) Venus]",
                reference=P.Reference(row_id="ref:gold", variant_id=vid, stem_key=sk, vintage="v0-legacy",
                                      kind="cached_solve", rendered="(A) Mercury"))
    base.update(kw)
    return P.MatchInputs(**base)


def s1_payload(ck):
    P.configure_rr()
    rub = gold_rubric()
    inp = gold_inputs()
    a1, a2 = P.build_dual(inp, rub)
    b1, b2 = P.build_dual(inp, rub)
    ck.check("S1 same inputs -> same bodies and shas (twice)", a1.body == b1.body and a2.body == b2.body and
             a1.sha256 == b1.sha256 and a2.sha256 == b2.sha256, "order1 %s order2 %s" % (a1.sha256[:16], a2.sha256[:16]))
    ck.check("S1 GOLDEN sha order 1 (pinned)", a1.sha256 == GOLDEN["order1"], "got %s" % a1.sha256)
    ck.check("S1 GOLDEN sha order 2 (pinned)", a2.sha256 == GOLDEN["order2"], "got %s" % a2.sha256)
    old_sys = P.V2_SYSTEM_TEMPLATE.replace("$systemPrompt", GOLDEN_V1_PERSONA).replace("$rubric", rub.rubric) + \
        "\n\n" + P.SCHEMA_INSTRUCTION
    ck.check("S1 GOLDEN re-pin moved ONLY the persona slot (the old persona substituted back reproduces the 9d993cc shas)",
             hashlib.sha256(rr.payload_bytes(old_sys, a1.user)).hexdigest() == GOLDEN_V1["order1"] and
             hashlib.sha256(rr.payload_bytes(old_sys, a2.user)).hexdigest() == GOLDEN_V1["order2"])
    ck.check("S1 order 1 != order 2 (dual order; A shown first, then B)", a1.sha256 != a2.sha256 and
             a1.shown_first == "model-alpha" and a2.shown_first == "model-beta")
    c = P.build_payload(gold_inputs(trace_b=inp.trace_b + "."), rub, 1)
    ck.check("S1 a one-character trace change moves the sha", c.sha256 != a1.sha256)
    d = json.loads(a1.body.decode("utf-8"))
    ck.check("S1 body keys exactly model / max_tokens / messages; temperature OMITTED; cap 8192; judge non-reasoning",
             list(d) == ["model", "max_tokens", "messages"] and "temperature" not in d and d["max_tokens"] == 8192 and
             d["model"] == "grok-4-1-fast-non-reasoning")
    ck.check("S1 body == rejudge_reasoning.payload_bytes(system, user) (the one builder)",
             rr.payload_bytes(a1.system, a1.user) == a1.body)
    ck.check("S1 stored zlib body round-trips to the sha", hashlib.sha256(zlib.decompress(a1.body_zlib)).hexdigest() == a1.sha256)
    ck.check("S1 reference block present once, U+2014 marker", a1.user.count(P.REFERENCE_MARKER) == 1 and
             "—" in P.REFERENCE_MARKER)
    ck.check("S1 recipe manifest says temperature 'omitted'", P.recipe_manifest(rub)["temperature_label"] == "omitted")
    exp_sys = P.V2_SYSTEM_TEMPLATE.replace("$systemPrompt", P.FIXED_SYSTEM_PERSONA).replace("$rubric", rub.rubric) + \
        "\n\n" + P.SCHEMA_INSTRUCTION
    ck.check("S1 system = v2 template with the FIXED persona (GENERIC_SYSTEM) in $systemPrompt and the rubric artefact in"
             " $rubric only (ruling 4aac08e)", a1.system == exp_sys and a1.system.startswith(P.FIXED_SYSTEM_PERSONA) and
             a1.system.count(rub.rubric) == 1 and "$systemPrompt" not in a1.system and "$rubric" not in a1.system)
    ck.refused("S1 a rubric artefact carrying a system_prompt field (rubric slot only)", lambda: P.load_rubric(
        {"corpus_type": "mcq", "system_prompt": "You are a judge.", "rubric": rub.rubric, "rubric_sha256": rub.rubric_sha256}),
        ("system_prompt", "RUBRIC SLOT ONLY"))
    ck.refused("S1 a rubric artefact carrying an unknown field", lambda: P.load_rubric(
        {"corpus_type": "mcq", "rubric": rub.rubric, "rubric_sha256": rub.rubric_sha256, "persona": "x"}), ("unknown field",))
    ck.refused("S1 a rubric artefact whose sha does not match its text", lambda: P.load_rubric(
        {"corpus_type": "mcq", "rubric": rub.rubric + "!", "rubric_sha256": rub.rubric_sha256}), ("sha256",))
    rr.TEMPERATURE = 0.0
    try:
        ck.refused("S1 rr.TEMPERATURE = 0.0", lambda: P.build_payload(inp, rub, 1), ("TEMPERATURE",))
    finally:
        rr.TEMPERATURE = None
    wrong_var = dataclasses.replace(inp.reference, variant_id="v:other-variant")
    ck.refused("S1 a reference keyed to another variant (R9)", lambda: P.build_payload(
        gold_inputs(reference=wrong_var), rub, 1), ("R9",))
    bound = dataclasses.replace(inp.reference, bound_response="x:resp-of-alpha")
    ck.refused("S1 a response-bound (oracle-class) reference", lambda: P.build_payload(gold_inputs(reference=bound), rub, 1),
               ("oracle-class",))
    ck.refused("S1 a question of another stem (failure 12)", lambda: P.build_payload(
        gold_inputs(question="Which planet is farthest from the Sun?"), rub, 1), ("failure 12",))
    ck.refused("S1 a reference carrying another stem_key (C7, R2)", lambda: P.build_payload(gold_inputs(
        reference=dataclasses.replace(inp.reference, stem_key="0" * 64)), rub, 1), ("carries stem_key",))
    ck.refused("S1 a reference of an unknown kind (C7, R4)", lambda: P.build_payload(gold_inputs(
        reference=dataclasses.replace(inp.reference, kind="oracle_vector")), rub, 1), ("not question-level",))
    ck.refused("S1 a reference indexed in another options ordering than the question block's", lambda: P.build_payload(
        gold_inputs(reference=dataclasses.replace(inp.reference, options_ordered_sha="a" * 32),
                    question_options_sha="b" * 32), rub, 1), ("options ordering",))
    ck.refused("S1 a reference whose v2 side is not EVAL", lambda: P.build_payload(gold_inputs(
        reference=dataclasses.replace(inp.reference, side_v2="TRAIN")), rub, 1), ("not EVAL",))
    return rub, inp


def s2_leakage(ck, rub, inp, tmp):
    stats = L.ScanStats()
    mat = L.LeakMaterial(side={"model-alpha": ["checker_outcome model-alpha: PASS 12/12"],
                               "model-beta": ["checker_outcome model-beta: FAIL 3/12"]},
                         key=["Answer key for this question: (A) Mercury"],
                         other_references=["(B) Venus [reference minted for the other variant]"])
    pl = P.build_payload(inp, rub, 1)
    hits = L.scan(pl, inp, rub, mat, stats)
    ck.check("S2 a clean payload passes the full-payload scan with material supplied", hits == [], stats.line())

    def leak(name, inp2=None, rub2=None, pl2=None, rules=()):
        i2 = inp2 or inp
        r2 = rub2 or rub
        p2 = pl2 if pl2 is not None else P.build_payload(i2, r2, 2)
        ck.refused("S2 leak: " + name, lambda: L.scan(p2, i2, r2, mat, stats), ("LEAKAGE",) + tuple(rules))
    leak("the OTHER side's checker outcome inside trace A",
         inp2=gold_inputs(trace_a=inp.trace_a + "\n(log) Checker_Outcome   model-beta: FAIL 3/12"), rules=("side_material",))
    leak("a machine verdict field in a trace", inp2=gold_inputs(trace_b=inp.trace_b + '\n{"is_correct": 1}'),
         rules=("marker:is_correct",))
    leak("a bracketed checker tag in a trace", inp2=gold_inputs(trace_b=inp.trace_b + "\n[Checker: tests passed 12/12]"),
         rules=("marker:verdict_tag",))
    leak("a per-response pass vector in a trace", inp2=gold_inputs(trace_a=inp.trace_a + "\nfollow_instruction_list=[1,0]"),
         rules=("marker:pass_vector",))
    leak("the key annotation in a trace", inp2=gold_inputs(
        trace_a=inp.trace_a + "\nAnswer key for this question: (A) Mercury"), rules=("key_material",))
    leak("a reference minted for the other variant inside trace B (wrong side)", inp2=gold_inputs(
        trace_b=inp.trace_b + "\n(B) Venus [reference minted for the other variant]"), rules=("wrong_reference",))
    leak("a second reference block inside a trace", inp2=gold_inputs(
        trace_b=inp.trace_b + "\n\n" + P.REFERENCE_MARKER + "\n(B) Venus"), rules=("reference_count",))
    # a tampered body: an extra key, and an edited system turn (built payload, bytes replaced)
    good = P.build_payload(inp, rub, 1)
    d = json.loads(good.body.decode("utf-8"))
    d["temperature"] = 0.0
    tampered = dataclasses.replace(good, body=json.dumps(d).encode("utf-8"))
    leak("a body with an extra (temperature) key", pl2=tampered, rules=("structure",))
    d = json.loads(good.body.decode("utf-8"))
    d["messages"][0]["content"] += "\n[Verdict: Model A is correct]"
    tampered = dataclasses.replace(good, body=json.dumps(d).encode("utf-8"))
    leak("an edited system turn carrying a verdict tag", pl2=tampered, rules=("structure", "marker:verdict_tag"))
    bad_rub = P.load_rubric({"corpus_type": "mcq", "rubric": rub.rubric + "\n[Gold: model-alpha]",
                             "rubric_sha256": P.rubric_sha(rub.rubric + "\n[Gold: model-alpha]")})
    leak("a gold tag in the rubric (system turn scanned too)", rub2=bad_rub, rules=("marker:verdict_tag",))
    wrong_ref = dataclasses.replace(inp.reference, variant_id="v:other-variant")
    ck.refused("S2 leak: a wrong-variant reference in the payload (scan leg 'inputs')", lambda: L.scan(
        good, gold_inputs(reference=wrong_ref), rub, mat, stats), ("LEAKAGE", "inputs"))
    ck.refused("S2 unscannable (too short) material", lambda: L.scan(good, inp, rub, L.LeakMaterial(side={"model-alpha": ["PASS"]})),
               ("unscannable",))
    ck.check("S2 scan counters count every refusal by rule", stats.refused >= 10 and stats.hits["side_material"] >= 1,
             stats.line())


def _ctx(**kw):
    c = {"script_blob": git_blob_lf(os.path.abspath(__file__)), "pool_id": "pv2dev_selftest_ej", "snapshot_id": "none",
         "session_id": "s:selftest"}
    c.update(kw)
    return c


# ── S3 writer (on loader-built matches) ───────────────────────────────────────────────────

class HTTP503(Exception):
    code = 503


def variant_by_stem(ev_path, stem):
    c = dv2views.open_eval("judge", ev_path)
    try:
        r = c.execute("SELECT variant_id FROM variant WHERE stem=? AND contract_id='MC_LETTER'", (stem,)).fetchall()
    finally:
        c.close()
    return r[0][0] if len(r) == 1 else None


S3_STEMS = {"m1": "Question number 2 about law?", "m2": "Question number 6 about law?",
            "m3": "Question number 8 about law?", "m4": "Question number 15 about math?"}


def load_s3(ck, ev_path, out=None):
    reqs = []
    for mid, stem in sorted(S3_STEMS.items()):
        vid = variant_by_stem(ev_path, stem)
        if vid is None:
            ck.check("S3 fixture: %s is one EVAL MC variant" % stem, False)
            return None
        reqs.append({"match_id": mid, "variant_id": vid, "model_a": "mA", "model_b": "mB", "batch_id": "b1"})
    return LD.load_matches(reqs, ev_path, out=out or ck.out)


def s3_writer(ck, rub, tmp, ev_path):
    loaded = load_s3(ck, ev_path)
    if loaded is None:
        return
    specs = loaded.specs
    ok_json = lambda w: json.dumps({"critique_a": "x", "critique_b": "y", "comparison": "z", "winner": w,  # noqa: E731
                                    "confidence": 0.8})
    launch = {"n": 1}
    posted = []

    def fake(system, user):
        """call_judge_full's shape. It identifies the slot by the bytes rr would post and records their sha."""
        body = rr.payload_bytes(system, user)
        sha = hashlib.sha256(body).hexdigest()
        slot = bysha[sha]
        posted.append((launch["n"], slot))
        mid, order = slot
        rid = "resp-%s-%d-%d" % (mid, order, launch["n"])
        if (mid, order) == ("m2", 1):
            return ('{"critique_a": "the analysis of A is', "azure:grok-4-1-fast-non-reasoning", 8192, 0.2, "length",
                    {"_response_id": rid, "_finish_reason": "length"})
        if (mid, order) == ("m3", 1):
            return ("", "azure:refusal", 0, 0.1, "content_filter",
                    {"_refusal": '{"error": {"code": "content_filter"}}', "_response_id": rid, "_finish_reason": "content_filter"})
        if (mid, order) == ("m4", 1) and launch["n"] == 1:
            raise HTTP503("service unavailable")
        winner = {("m1", 1): "Model A", ("m1", 2): "Model B", ("m2", 2): "Model A", ("m3", 2): "Model A",
                  ("m4", 2): "TIE", ("m4", 1): "Model B"}[(mid, order)]
        return (ok_json(winner), "azure:grok-4-1-fast-non-reasoning", 321, 0.3, "stop", {"_response_id": rid})

    bysha = {}
    for mid, inp in specs.items():
        p1, p2 = P.build_dual(inp, rub)
        bysha[p1.sha256] = (mid, 1)
        bysha[p2.sha256] = (mid, 2)
    path = os.path.join(tmp, "s3_run.db")
    w = W.JudgeWriter.create(path, "SELFTEST-EJ (scratch)", "s3", loaded, rub, _ctx())
    n1 = w.run(fake, out=ck.out)
    pend1 = [(r[1], r[2]) for r in w.store.pending()]
    ck.check("S3 C2 witness: the pre-scan scanned every pending slot and the poster scanned every post (8 / 8 / 8), every"
             " scan with material, KEY material in every scan (D3)", w.stats.scanned == 16 and w.poster_scans == 8 and
             w.stats.with_material == 16 and w.stats.without_material == 0 and w.stats.with_key == 16,
             "%s; poster scans %d" % (w.stats.line(), w.poster_scans))
    w.close()
    ck.check("S3 launch 1 posts all 8 slots; the errored one (m4 order 1) stays pending", n1 == 8 and pend1 == [("m4", 1)],
             "posted %d, pending %s" % (n1, pend1))
    c = dv2ro.open_ro(path)
    try:
        rows = {(m, o): dict(zip(("vote", "finish", "cf", "http", "raw", "sha", "body", "tb", "jr", "rm", "rid", "ctok", "cap",
                                  "tsent", "tlabel", "fp", "ptok", "pblob", "cblob", "sblob", "pv", "ref", "vint", "sk"),
                                 rest))
                for m, o, *rest in c.execute(
                    "SELECT match_id, presentation_order, vote, finish_reason, content_filter, http_status, raw_text,"
                    " payload_sha256, body_zlib, body_codec, judge_requested, response_model, response_id,"
                    " completion_tokens, max_tokens, temperature_sent, temperature_label, system_fingerprint, prompt_tokens,"
                    " prompt_template_blob, combiner_blob, script_blob, parse_version, reference_row_id,"
                    " reference_vintage, stem_key FROM verdict")}
        n_att = c.execute("SELECT COUNT(*) FROM attempt WHERE match_id='m4' AND presentation_order=1").fetchone()[0]
    finally:
        c.close()
    nt, cf = rows[("m2", 1)], rows[("m3", 1)]
    ck.check("S3 a TRUNCATED response is stored NON_TERMINATED (finish_reason length), not TIE",
             nt["vote"] == "NON_TERMINATED" and nt["finish"] == "length", str({k: nt[k] for k in ("vote", "finish")}))
    ck.check("S3 a CONTENT-FILTERED response is stored CONTENT_FILTER (http 400, content_filter 1), not TIE",
             cf["vote"] == "CONTENT_FILTER" and cf["cf"] == 1 and cf["http"] == 400 and cf["finish"] == "content_filter",
             str({k: cf[k] for k in ("vote", "cf", "http", "finish")}))
    ck.check("S3 no stored vote is TIE except the judged TIE (m4 order 2)",
             sorted(k for k, r in rows.items() if r["vote"] == "TIE") == [("m4", 2)])
    ck.check("S3 the errored post is an attempt row, never a verdict", ("m4", 1) not in rows and n_att == 1)
    r = rows[("m1", 1)]
    prov_ok = (r["sha"] == hashlib.sha256(zlib.decompress(r["body"])).hexdigest() and r["tb"] == "zlib" and
               r["jr"] == "grok-4-1-fast-non-reasoning" and r["rm"] == "grok-4-1-fast-non-reasoning" and
               r["rid"] == "resp-m1-1-1" and r["finish"] == "stop" and r["ctok"] == 321 and r["cap"] == 8192 and
               r["tsent"] is None and r["tlabel"] == "omitted" and r["pblob"] == git_blob_lf(os.path.join(HERE, "payload.py"))
               and r["cblob"] == git_blob_lf(os.path.join(HERE, "combiner.py")) and r["pv"] == W.PARSE_VERSION and
               r["ref"] == specs["m1"].reference.row_id and r["vint"] == "grok-reasoning-v0" and
               r["sk"] == specs["m1"].stem_key)
    ck.check("S3 per-row provenance (payload sha = sha256(body), prompt blob, judge, response model, response id, finish,"
             " tokens, cap 8192, temperature omitted, combiner blob, parse version, reference row + vintage v0, stem_key)",
             prov_ok, "ref %s vintage %s; fingerprint %r prompt_tokens %r (NULL: not surfaced by call_judge_full)" % (
                 r["ref"], r["vint"], r["fp"], r["ptok"]))
    ck.check("S3 m1 votes FIRST (order 1) / SECOND (order 2): contestant A both times",
             rows[("m1", 1)]["vote"] == "FIRST" and rows[("m1", 2)]["vote"] == "SECOND")
    # relaunch: only the pending slot is posted; the cached CONTENT_FILTER is not
    launch["n"] = 2
    w2 = W.JudgeWriter.open(path, loaded, rub, _ctx())
    n2 = w2.run(fake, out=ck.out)
    w2.close()
    ck.check("S3 relaunch posts ONLY the pending slot (m4 order 1), never the cached CONTENT_FILTER",
             n2 == 1 and [s for (l, s) in posted if l == 2] == [("m4", 1)], "posted %s" % [s for (l, s) in posted if l == 2])
    launch["n"] = 3
    w3 = W.JudgeWriter.open(path, loaded, rub, _ctx())
    n3 = w3.run(fake, out=lambda s: None)
    w3.close()
    ck.check("S3 a complete run posts NOTHING on a third launch", n3 == 0 and not [1 for (l, s) in posted if l == 3])
    mv = W.match_verdicts(path)
    got = {x["match_id"]: (x["status"], x["combiner"], x["run_id"], x["n_order_verdicts"]) for x in mv}
    ck.check("S3 match verdicts (C8: run_id, denominators from match_status): m1 A, m2 NON_TERMINATED, m3 CONTENT_FILTER,"
             " m4 TIE (a flip); combiner == data_v2 view", got == {
                 "m1": ("A", "A", "s3", 2), "m2": ("NON_TERMINATED", "NON_TERMINATED", "s3", 2),
                 "m3": ("CONTENT_FILTER", "CONTENT_FILTER", "s3", 2), "m4": ("TIE", "TIE", "s3", 2)} and
             all(x["agree"] for x in mv), json.dumps(got, sort_keys=True))
    other = P.load_rubric({"corpus_type": "mcq", "rubric": rub.rubric + " ", "rubric_sha256": P.rubric_sha(rub.rubric + " ")})
    ck.refused("S3 relaunch under another rubric", lambda: W.JudgeWriter.open(path, loaded, other, _ctx()), ("rubric_sha",))
    ck.refused("S3 relaunch under another script blob", lambda: W.JudgeWriter.open(path, loaded, rub,
                                                                                _ctx(script_blob="0" * 40)), ("script_blob",))
    other_view = LD.Loaded(loaded.specs, loaded.materials, dict(loaded.manifest, eval_view_sha256_bytes="0" * 64))
    ck.refused("S3 relaunch against another eval_view file", lambda: W.JudgeWriter.open(path, other_view, rub, _ctx()),
               ("eval_view_sha256",))
    # a pending store whose relaunch inputs (validly signed) do not reproduce the schedule
    one = LD.Loaded({"m1": specs["m1"]}, {"m1": loaded.materials["m1"]}, loaded.manifest)
    path4 = os.path.join(tmp, "s3_changed.db")
    w4 = W.JudgeWriter.create(path4, "SELFTEST-EJ (scratch)", "s3c", one, rub, _ctx())
    w4.close()
    changed = LD.Loaded({"m1": LD._sign_for_selftest(dataclasses.replace(specs["m1"], trace_b=specs["m1"].trace_b + " (edited)"))},
                        {"m1": loaded.materials["m1"]}, loaded.manifest)
    w5 = W.JudgeWriter.open(path4, changed, rub, _ctx())
    try:
        ck.refused("S3 relaunch whose inputs do not reproduce the fixed schedule", lambda: w5.run(fake, out=lambda s: None),
                   ("do not reproduce",))
    finally:
        w5.close()
    unsigned = LD.Loaded({"m1": dataclasses.replace(specs["m1"], trace_b=specs["m1"].trace_b + " (edited)")},
                         {"m1": loaded.materials["m1"]}, loaded.manifest)
    ck.refused("S3 a spec edited after the loader (token no longer verifies)", lambda: W.JudgeWriter.open(
        path4, unsigned, rub, _ctx()), ("did not come from loader",))
    # R7: two draws of the same body are two rows
    path6 = os.path.join(tmp, "s3_draws.db")
    w6 = W.JudgeWriter.create(path6, "SELFTEST-EJ (scratch)", "s3d", one, rub, _ctx(), n_draws=2)
    launch["n"] = 1
    w6.run(fake, out=lambda s: None)
    w6.close()
    c = dv2ro.open_ro(path6)
    try:
        shas = [s for (s,) in c.execute("SELECT payload_sha256 FROM verdict WHERE presentation_order=1 ORDER BY draw_index")]
    finally:
        c.close()
    ck.check("S3 R7: the same body in two draws is stored as two rows (slot key, sha a column)",
             len(shas) == 2 and shas[0] == shas[1])
    # classify table: never TIE for the non-verdict classes
    cl = [W.classify('{"winner": "TIE"}', "length"), W.classify('{"winner": "TIE"}', "content_filter"),
          W.classify("", "stop"), W.classify('{"winner": "TIE"}', "tool_calls"), W.classify(None, None),
          W.classify('{"winner": "Model B"}', "stop"), W.classify('{"winner": "tie"}', None)]
    ck.check("S3 classify: length -> NON_TERMINATED, content_filter -> CONTENT_FILTER, empty / unknown finish / None ->"
             " INVALID, parsed -> FIRST/SECOND/TIE", [v for v, _ in cl] ==
             ["NON_TERMINATED", "CONTENT_FILTER", "INVALID", "INVALID", "INVALID", "SECOND", "TIE"], str([v for v, _ in cl]))
    s7_store(ck, path)
    # D5 ruling (3): the readout hook stratifies MIXED against same-ordering
    lq = LD.load_matches([{"match_id": "q42", "variant_id": variant_by_stem(ev_path, "Question number 42 about law?"),
                           "model_a": "mA", "model_b": "mB"},
                          {"match_id": "q2", "variant_id": specs["m1"].variant_id, "model_a": "mA", "model_b": "mB"}],
                         ev_path, out=lambda x: None)
    pq = os.path.join(tmp, "s3_mixed.db")
    wq = W.JudgeWriter.create(pq, "SELFTEST-EJ (scratch)", "s3q", lq, rub, _ctx())
    bysha.clear()
    for mid, inp in lq.specs.items():
        p1, p2 = P.build_dual(inp, rub)
        bysha[p1.sha256] = ("m1", 1)
        bysha[p2.sha256] = ("m1", 2)
    launch["n"] = 1
    wq.run(fake, out=lambda x: None)
    wq.close()
    ms = W.mixed_strata(pq)
    ck.refused("S3 E2: mixed_strata refuses a DB that is not a v2 verdict run (schema_id checked first)", lambda:
               W.mixed_strata(ev_path), ("not a v2 verdict run DB",))
    ck.check("S3 D5 (3) readout: mixed_strata splits the run into MIXED (Q42) and SAME (Q2)",
             sum(ms["MIXED"].values()) == 1 and sum(ms["SAME"].values()) == 1, json.dumps(ms, sort_keys=True))


# ── S7 the store is append-only from E-J's side (C1; main's no-rekey triggers) ─────────────

def s7_store(ck, path):
    """A stored verdict can be neither REPLACEd, UPDATEd nor DELETEd. The file is re-opened with data_v2.ro.open_run_writer
    (the run is unsealed) exactly as probe C did; every mutation must raise and the stored vote must be unchanged."""
    import sqlite3
    c = dv2ro.open_run_writer(path)
    try:
        before = c.execute("SELECT vote, raw_text FROM verdict WHERE match_id='m1' AND presentation_order=1").fetchone()
        cols = [r[1] for r in c.execute("PRAGMA table_info(verdict)")]
        row = list(c.execute("SELECT * FROM verdict WHERE match_id='m1' AND presentation_order=1").fetchone())
        row[cols.index("vote")] = "SECOND"
        row[cols.index("raw_text")] = "forged"
        res = {}
        for name, sql, args in (
                ("INSERT OR REPLACE", "INSERT OR REPLACE INTO verdict (%s) VALUES (%s)" % (",".join(cols), ",".join("?" * len(cols))), row),
                ("REPLACE INTO", "REPLACE INTO verdict (%s) VALUES (%s)" % (",".join(cols), ",".join("?" * len(cols))), row),
                ("UPDATE", "UPDATE verdict SET vote='SECOND' WHERE match_id='m1' AND presentation_order=1", ()),
                ("DELETE", "DELETE FROM verdict WHERE match_id='m1' AND presentation_order=1", ())):
            try:
                c.execute(sql, args)
                c.commit()
                res[name] = "ACCEPTED"
            except sqlite3.DatabaseError as e:
                c.rollback()
                res[name] = "REFUSED: " + str(e)[:60]
        after = c.execute("SELECT vote, raw_text FROM verdict WHERE match_id='m1' AND presentation_order=1").fetchone()
    finally:
        c.close()
    ck.check("S7 a stored verdict: INSERT OR REPLACE / REPLACE / UPDATE / DELETE all ABORT and the vote is unchanged",
             all(v.startswith("REFUSED") for v in res.values()) and before == after, json.dumps(res))


# ── S4 combiner ───────────────────────────────────────────────────────────────────────────

def s4_combiner(ck, tmp):
    tab = K.rj_equivalence_table()
    n_eq = sum(1 for r in tab if r[4])
    ck.check("S4 combiner == rejudge_grok.combine_orders on the shared domain (table, both functions evaluated)",
             n_eq == 16 and len(tab) == 16, "%d / %d equal" % (n_eq, len(tab)))
    ck.check("S4 the AST pin of rejudge_grok.combine_orders holds", K.check_rj_pin() == K.rj_ast_sha())
    saved = dict(K.RJ_COMBINE_AST_SHAS)
    K.RJ_COMBINE_AST_SHAS[tuple(sys.version_info[:2])] = "0" * 64
    try:
        ck.refused("S4 a wrong AST pin", K.check_rj_pin, ("AST",))
    finally:
        K.RJ_COMBINE_AST_SHAS.clear()
        K.RJ_COMBINE_AST_SHAS.update(saved)

    def mutant(p1, p2):  # TIE-on-flip removed: order 1 wins
        c1, c2 = K.to_contestant(p1, 1), K.to_contestant(p2, 2)
        if "INVALID" in (c1, c2):
            return "INVALID", False, True
        return c1, c1 != c2, False
    real = K.combine
    K.combine = mutant
    try:
        n_mut = sum(1 for r in K.rj_equivalence_table() if r[4])
    finally:
        K.combine = real
    ck.check("S4 a mutant combiner (no TIE on a flip) FAILS the table: the test discriminates", n_mut < 16,
             "mutant %d / 16 equal" % n_mut)
    allp = [(a, b) for a in K.POSITIONAL for b in K.POSITIONAL]
    bad = [(a, b) for a, b in allp if ("NON_TERMINATED" in (a, b) or "CONTENT_FILTER" in (a, b)) and
           K.combine(a, b)[0] in ("TIE", "INVALID", "A", "B")]
    ck.check("S4 NON_TERMINATED / CONTENT_FILTER are never TIE (nor INVALID, nor a winner) over all 36 pairs", not bad,
             "%d bad" % len(bad))
    # the combiner against data_v2's match_verdict view on all 36 pairs, through the real store
    path = os.path.join(tmp, "s4_view.db")
    meta = {"run_id": "s4", "registration": "SELFTEST-EJ (scratch)", "judge_requested": "none", "provider": "none",
            "max_tokens": 8192, "temperature_label": "omitted", "script_blob": "0" * 40, "combiner_blob": "0" * 40,
            "prompt_template_blob": "0" * 40, "parse_version": "none", "pool_id": "pv2dev_selftest_ej"}
    st = dv2verdicts.VerdictStore.create(path, meta)
    slots, want = [], {}
    for k, (a, b) in enumerate(allp):
        mid = "p%02d" % k
        want[mid] = (a, b)
        for order in (1, 2):
            f, s = ("mA", "mB") if order == 1 else ("mB", "mA")
            slots.append({"match_id": mid, "presentation_order": order, "draw_index": 0, "variant_id": "v:x", "stem_key": "k",
                          "component_id": None, "contestant_a": "mA", "contestant_b": "mB", "shown_first": f,
                          "shown_second": s, "response_first_sha": "r", "response_second_sha": "r"})
    st.add_schedule(slots)

    def poster(slot):
        v = want[slot["match_id"]][slot["presentation_order"] - 1]
        body = ("%s|%d" % (slot["match_id"], slot["presentation_order"])).encode()
        f = {"vote": v, "raw_text": None if v == "CONTENT_FILTER" else "raw", "parse_version": "none",
             "judge_requested": "none", "provider": "none", "max_tokens": 8192, "temperature_sent": None,
             "temperature_label": "omitted", "prompt_template_blob": "0" * 40, "script_blob": "0" * 40,
             "combiner_blob": "0" * 40, "stem_key": "k", "pool_id": "pv2dev_selftest_ej", "http_status": 200,
             "finish_reason": "length" if v == "NON_TERMINATED" else ("content_filter" if v == "CONTENT_FILTER" else "stop")}
        return ("verdict", body, hashlib.sha256(body).hexdigest(), f)
    st.drain(poster)
    st.conn.close()
    mv = W.match_verdicts(path)
    agree = sum(1 for v in mv if v["combiner"] is not None and v["combiner"] == v["status"])
    ck.check("S4 combiner == data_v2 match_status (match_verdict) on all 36 positional pairs", len(mv) == 36 and agree == 36
             and all(v["run_id"] == "s4" for v in mv), "%d / %d" % (agree, len(mv)))


# ── S5 induction ──────────────────────────────────────────────────────────────────────────

DEV_SEED = "DEV-selftest-ej-induce"
REG_ID = "ARCH-V2-INDUCE-SELECT-1"
REG_SEED = "ARCHV2-INDUCE-1:5abb79f55c3719d122b5310151f975493609f37b"
# C6: the golden of the selection ON THE SYNTHETIC FIXTURE under DEV_SEED (never the real split: the registered selection
# runs once, after the real split draw). Ordered list of the selected variant ids and the sorted set, sha256 hex.
# First pinned at 8ef0b75 (ordered 16d06e30..., sorted 0318506e..., n 40) under the PRE-RULING selection (candidate rows
# sorted, first n: duplicates and component twins admitted). RE-PINNED 2026-09-24 after the ruling on ARCH-V2-INDUCE-RUBRIC-1
# finding 1 (eabbf45: collapse to distinct variant_id, first variant per COMPONENT): S5 re-derives BOTH goldens from the
# fixture's own gen_view with an independent reference implementation of each rule, so the re-pin is witnessed to come
# from the rule change alone.
# [RE-PINNED 2026-09-24 for the INDUCE-RUBRIC-1 re-pin to SPLIT-2 (merge of main 5b89159): the FIXTURE changed, not the
# rule: data_v2.gates._fixture gained BBH items (K3, READY_ck_close_v2 D2) and data_v2.split draws under CK-CLOSE-v2, so
# the fixture's gen_view differs. Was V1 ordered 16d06e30... / sorted 0318506e..., RULED ordered 28634d52... / sorted
# 8631576c... (reproduced by the 634dba5 tree on its own data_v2). judge_v2's selection code is byte-identical across the
# re-pin; both goldens are re-derived by the independent reference implementations below on the new fixture. "The
# 8ef0b75 golden" in S5's check name now reads: the PRE-RULING rule's golden on the current fixture.]
GOLDEN_INDUCE_V1 = {"ordered": "47ea219bab083540cba739cbaf94c242659964752e4e4e71f0b7004964732183",
                    "sorted": "447c6b211682c830a881405c264dcdbf293fbc19e4f62626d7694322ab9596f9", "n_inputs": 40}
GOLDEN_INDUCE = {"ordered": "25a97ec2477e04ff427adbd9ff112bf3530c30b138b960a4cddfe7c5edd06dc0",
                 "sorted": "cb524315558a27d8c2ed2ae3f37eaf8814fec886c318446cde94b535ae157287", "n_inputs": 40}


def reference_selections(gen_path, seed, n=40, population=None, exclude=()):
    """Independent re-derivations over the fixture's gen_view: (the pre-ruling rule, the ruled rule) -> ids lists."""
    import hashlib as _h
    g = dv2views.open_generation("construct", gen_path)
    try:
        side = {i: (sd, c) for i, sd, c in g.execute("SELECT item_id, side, component_id FROM side")}
        rows = [(v, i) for cv, v, i, ct in g.execute("SELECT corpus_version, variant_id, item_id, contract_id FROM variant")
                if I.CONTRACT_TYPES.get(ct) == "mcq" and side.get(i, (None,))[0] == "TRAIN" and
                (population is None or (cv == population["corpus_version"] and ct in population["contracts"]))]
    finally:
        g.close()
    key = lambda v: _h.sha256((seed + dv2c.US + v).encode("utf-8")).hexdigest()  # noqa: E731
    reference_selections.distinct = len(dict(rows))
    reference_selections.rows = len(rows)
    old = [v for v, _i in sorted(rows, key=lambda r: key(r[0]))][:n]
    new, comps = [], set()
    for v, i in sorted(dict(rows).items(), key=lambda r: key(r[0])):
        if len(new) >= n:
            break
        if v in exclude:
            continue
        if side[i][1] in comps:
            continue
        comps.add(side[i][1])
        new.append(v)
    return old, new


def s5_induction(ck, tmp, gen_path, ev_path, judgeable, sentinels):
    stub = I.StubInducer()
    art = I.induce("mcq", stub, gen_path, seed=DEV_SEED, out=ck.out)
    man = art["manifest"]
    ck.check("S5 induction reads through open_generation('induce') and yields an mcq rubric from TRAIN inputs",
             man["gen_view_meta"]["view_kind"] == "gen" and man["n_inputs"] > 0 and
             man["content_key_check"]["eval_hits"] == 0 and len(stub.calls) == 1 and man["sides_admitted"] == ["TRAIN"],
             "n_inputs %d, sides %s" % (man["n_inputs"], man["sides_admitted"]))
    old_ref, new_ref = reference_selections(gen_path, DEV_SEED)
    shaj = lambda ids: hashlib.sha256("\n".join(ids).encode("utf-8")).hexdigest()  # noqa: E731
    ck.check("S5 re-pin witness: the PRE-RULING rule re-derived independently reproduces the 8ef0b75 golden, and the RULED"
             " rule re-derived independently equals induction.select_inputs' selection",
             shaj(old_ref) == GOLDEN_INDUCE_V1["ordered"] and shaj(sorted(old_ref)) == GOLDEN_INDUCE_V1["sorted"] and
             shaj(new_ref) == man["input_variant_ids_ordered_sha256"], "old %s / new %s" % (shaj(old_ref)[:16],
                                                                                          shaj(new_ref)[:16]))
    w = man["train_only_witness"]
    ck.check("S5 finding 1 witness: candidate rows, distinct variants, duplicates collapsed, skipped by component are"
             " printed, and the selection has 40 distinct variants in 40 distinct components",
             all(k in w for k in ("candidate_rows", "distinct_variants", "duplicates_collapsed", "skipped_by_component"))
             and w["candidate_rows"] == w["distinct_variants"] + w["duplicates_collapsed"] and
             len(set(new_ref)) == man["n_inputs"] and w["distinct_variants"] == reference_selections.distinct and
             w["candidate_rows"] == reference_selections.rows, json.dumps(w, sort_keys=True))
    # finding 1 units on a tiny scratch gen_view shape: differing duplicates are REFUSED (select_inputs and
    # check_inputs_bound), identical ones collapse, and one variant per component is kept
    m = dv2ro.create_new(os.path.join(tmp, "finding1_unit.db"))
    m.executescript("CREATE TABLE side (item_id TEXT, side TEXT, component_id TEXT);"
                    "CREATE TABLE variant (corpus_version TEXT, variant_id TEXT, item_id TEXT, stem TEXT,"
                    " options_sorted_json TEXT, contract_id TEXT);"
                    "INSERT INTO side VALUES ('i:1','TRAIN','c:1'), ('i:2','TRAIN','c:1'), ('i:3','TRAIN','c:3');"
                    "INSERT INTO variant VALUES ('a','v:1','i:1','S one','[\"x\"]','MC_LETTER'),"
                    " ('b','v:1','i:1','S one','[\"x\"]','MC_LETTER'), ('a','v:2','i:2','S two','[\"y\"]','MC_LETTER'),"
                    " ('a','v:3','i:3','S three','[\"z\"]','MC_LETTER');")
    wm = {}
    sel = I.select_inputs(m, "mcq", 3, DEV_SEED, witness=wm)
    ck.check("S5 finding 1 unit: identical duplicate rows collapse (4 rows -> 3 variants, 1 collapsed) and one variant per"
             " component is kept (c:1 holds v:1 and v:2)", wm["candidate_rows"] == 4 and wm["distinct_variants"] == 3 and
             wm["duplicates_collapsed"] == 1 and wm["skipped_by_component"] == 1 and len(sel) == 2 and
             len({r["variant_id"] for r in sel}) == 2, json.dumps(wm, sort_keys=True))
    m.execute("INSERT INTO variant VALUES ('c','v:3','i:3','S three DIFFERENT','[\"z\"]','MC_LETTER')")
    ck.refused("S5 finding 1 unit: a duplicate variant row that DIFFERS is refused by select_inputs", lambda:
               I.select_inputs(m, "mcq", 3, DEV_SEED), ("DIFFER",))
    ck.refused("S5 finding 1 unit: check_inputs_bound refuses a variant whose rows differ", lambda: I.check_inputs_bound(
        m, [{"variant_id": "v:3", "stem": "S three", "options": ["z"], "contract_id": "MC_LETTER"}], "mcq"),
        ("differ across corpus versions",))
    m.close()
    ck.check("S5 C6 GOLDEN: the selection on the fixture under the DEV seed (ordered ids, sorted set, n)",
             man["input_variant_ids_ordered_sha256"] == GOLDEN_INDUCE["ordered"] and
             man["input_variant_ids_sha256"] == GOLDEN_INDUCE["sorted"] and man["n_inputs"] == GOLDEN_INDUCE["n_inputs"],
             "got ordered %s sorted %s n %d" % (man["input_variant_ids_ordered_sha256"], man["input_variant_ids_sha256"],
                                                man["n_inputs"]))
    art2 = I.induce("mcq", I.StubInducer(), gen_path, seed=DEV_SEED, out=lambda s: None)
    art3 = I.induce("mcq", I.StubInducer(), gen_path, seed=DEV_SEED + "-other", out=lambda s: None)
    ck.check("S5 the selection is a function of the seed: same seed -> same ordered ids; another seed -> other ids",
             art2["manifest"]["input_variant_ids_ordered_sha256"] == man["input_variant_ids_ordered_sha256"] and
             art3["manifest"]["input_variant_ids_ordered_sha256"] != man["input_variant_ids_ordered_sha256"])
    wit = man["train_only_witness"]
    ck.check("S5 TRAIN-only witness: GATE mcq variants were seen and EXCLUDED by the selection (gate_excluded > 0)",
             wit.get("gate_excluded", 0) > 0 and wit.get("train_candidates", 0) >= man["n_inputs"], json.dumps(wit))
    ck.check("S5 the DEV-seed stub artefact says it is not of record",
             art["of_record"].startswith("STUB, NOT OF RECORD") and "DEV, NOT OF RECORD" in art["of_record"])
    # the seed rules (ARCH-V2-INDUCE-SELECT-1)
    ck.refused("S5 no seed (the seed is required)", lambda: I.induce("mcq", I.StubInducer(), gen_path, out=lambda s: None),
               ("required",))
    ck.refused("S5 the version-string seed 'jv2-induce-2'", lambda: I.induce(
        "mcq", I.StubInducer(), gen_path, seed="jv2-induce-2", out=lambda s: None), ("version string",))
    ck.refused("S5 an unregistered non-DEV seed", lambda: I.resolve_seed("some-seed"), ("neither registered nor",))
    ck.refused("S5 the registered seed without its registration named", lambda: I.resolve_seed(REG_SEED),
               ("registration named",))
    ck.refused("S5 a registration with another seed", lambda: I.resolve_seed(DEV_SEED, REG_ID), ("not the seed registered",))
    ck.check("S5 the registered seed resolves under its registration (the selection itself is NOT run here)",
             I.resolve_seed(REG_SEED, REG_ID) == "REGISTERED " + REG_ID and I.REGISTERED_SEEDS[REG_ID] == REG_SEED)
    ck.refused("S5 sides TRAIN+GATE (GATE is excluded)", lambda: I.induce(
        "mcq", I.StubInducer(), gen_path, seed=DEV_SEED, sides=("TRAIN", "GATE"), out=lambda s: None), ("TRAIN only",))
    apath = os.path.join(tmp, "rubric_mcq_stub.json")
    I.write_artefact(art, apath)
    ck.refused("S5 a second write of the artefact (write-once)", lambda: I.write_artefact(art, apath), ("written once",))
    rub = I.load_artefact(apath, art["artefact_sha256"])
    ck.check("S5 the artefact round-trips to a RubricArtifact with its sha", rub.rubric_sha256 == art["rubric_sha256"] and
             rub.corpus_type == "mcq")
    ck.check("S5 the induced artefact carries NO system_prompt (rubric slot only) and the induction prompt asks for the"
             " rubric only", "system_prompt" not in art and "system_prompt" not in stub.calls[0][0])
    sp_reply = I.StubInducer(reply=json.dumps({"system_prompt": "You are a judge.", "rubric": "1. Correct answers win."}))
    ck.refused("S5 an induction reply carrying a system_prompt (rubric slot only)", lambda: I.induce(
        "mcq", sp_reply, gen_path, seed=DEV_SEED, out=lambda s: None), ("system_prompt", "RUBRIC SLOT ONLY"))
    forged = dict(art)
    forged["system_prompt"] = "You are a judge."
    forged.pop("artefact_sha256")
    forged["artefact_sha256"] = hashlib.sha256(json.dumps(forged, sort_keys=True, ensure_ascii=True).encode("utf-8")).hexdigest()
    fpath = os.path.join(tmp, "rubric_mcq_forged.json")
    I.write_artefact(forged, fpath)
    ck.refused("S5 a written artefact carrying a system_prompt field (its own sha valid) on load", lambda: I.load_artefact(
        fpath), ("system_prompt", "RUBRIC SLOT ONLY"))
    if not judgeable or not sentinels:
        ck.check("S5 fixture has EVAL judgeable items and EVAL sentinels", False,
                 "judgeable %d sentinels %d" % (len(judgeable), len(sentinels)))
        return rub
    stub2 = I.StubInducer()
    ind = lambda inputs: (lambda: I.induce("mcq", stub2, gen_path, seed=DEV_SEED, inputs=inputs, out=lambda s: None))  # noqa: E731
    ck.refused("S5 an EVAL item handed to induction", ind([_as_input(judgeable[0])]), ("assert_not_eval", "EVAL content"))
    ck.refused("S5 a SENTINEL (routing-only EVAL unit) handed to induction", ind([_as_input(sentinels[0])]),
               ("assert_not_eval",))
    gi = gen_items(gen_path)
    gate = [r for r in gi if r[5] == "GATE" and I.CONTRACT_TYPES.get(r[4]) == "mcq"]
    train = [r for r in gi if r[5] == "TRAIN" and I.CONTRACT_TYPES.get(r[4]) == "mcq"]
    if gate:
        ck.refused("S5 a GATE item handed to induction -> content-key leg (b)", ind([_as_input(gate[0][:5])]),
                   ("not generation-side",))
        real_select = I.select_inputs
        I.select_inputs = lambda conn, ct, n, seed, sides=I.DEFAULT_SIDES, witness=None, population=None, exclude=None:             [_as_input(gate[0][:5])]
        try:
            ck.refused("S5 a GATE item reaching the SELECTED path (select_inputs replaced) -> leg (b) still refuses",
                       lambda: I.induce("mcq", stub2, gen_path, seed=DEV_SEED, out=lambda s: None), ("not generation-side",))
        finally:
            I.select_inputs = real_select
    else:
        ck.check("S5 fixture has a GATE mcq item", False)
    foreign = {"variant_id": "v:foreign", "item_id": "i:foreign", "stem": "A foreign question that no corpus carries?",
               "options": [], "contract_id": "MC_LETTER"}
    ck.refused("S5 a foreign text (in no view) -> content-key leg (b)", ind([foreign]), ("not generation-side",))
    lied = dict(_as_input(judgeable[0]))
    lied["item_id"] = train[0][1] if train else "i:x"
    lied["variant_id"] = train[0][0] if train else "v:x"
    ck.refused("S5 an EVAL text handed with a TRAIN item's ids (the text is keyed, the id never trusted)", ind([lied]),
               ("EVAL content",))
    # C5: options
    probe_d = dict(_as_input(train[0][:5]))
    probe_d["options"] = [judgeable[0][2], "second option text"]
    ck.refused("S5 PROBE D: an EVAL stem inside a TRAIN input's options -> leg (a) on options", ind([probe_d]),
               ("assert_not_eval", "EVAL content"))
    edited = dict(_as_input(train[0][:5]))
    edited["options"] = list(edited["options"]) + ["an option gen_view does not carry"]
    ck.refused("S5 a TRAIN input whose options differ from gen_view's row (inputs bound to gen_view)", ind([edited]),
               ("not gen_view's rows",))
    g = dv2views.open_generation("induce", gen_path)
    try:
        ck.refused("S5 assert_induction_inputs on an EVAL option text (leg a keys options)", lambda: I.assert_induction_inputs(
            g, [train[0][2]], option_texts=[judgeable[0][2]]), ("EVAL content",))
    finally:
        g.close()
    ck.check("S5 ... and the stub model was never called on a refused input", len(stub2.calls) == 0)
    ck.refused("S5 induction pointed at the eval_view (refused by the file's own meta)", lambda: I.induce(
        "mcq", I.StubInducer(), ev_path, seed=DEV_SEED, out=lambda s: None), ("REFUSED",))
    ck.refused("S5 'agentic' has no data_v2 contract", lambda: I.induce("agentic", I.StubInducer(), gen_path, seed=DEV_SEED,
                                                                        out=lambda s: None), ("no data_v2 contract",))
    copy_inputs = [{"variant_id": "v:c", "item_id": "i:c", "contract_id": "MC_LETTER", "options": [],
                    "stem": "the quick brown fox jumps over the lazy dog near the river bank today"}]
    ck.check("S5 verbatim audit fires on an 8-token copy and passes a generic rubric",
             bool(I.verbatim_audit("Prefer answers; the quick brown fox jumps over the lazy dog near it", copy_inputs)) and
             not I.verbatim_audit(rub.rubric, copy_inputs))
    longs = [r for r in train if len(I._tokens(r[2])) >= I.SHINGLE]
    if longs:
        copier = I.StubInducer(reply=json.dumps({"rubric": "Prefer: " + longs[0][2]}))
        ck.refused("S5 a reply copying a TRAIN input verbatim (induce-level audit)", lambda: I.induce(
            "mcq", copier, gen_path, seed=DEV_SEED, inputs=[_as_input(longs[0][:5])], out=lambda s: None), ("verbatim",))
    else:
        ck.check("S5 fixture has a TRAIN mcq stem of >= %d tokens for the verbatim audit" % I.SHINGLE, False)
    return rub


# ── S6 the loader, the provenance token, the reference ruling, the material, probes A and B ───

def _ref_row(**kw):
    r = {"variant_id": "v:x", "vintage": "grok-reasoning-v0", "source_key": "k1", "item_id": "i:sk", "legacy_qid": 1,
         "answer": "B", "state": None, "finish_reason": None, "side_at_mint": "EVAL", "resolution": "solver_row"}
    r.update(kw)
    return r


def s6_loader(ck, tmp, gen_path, ev_path, judgeable, sentinels, rub):
    # choose_reference: the ruling, unit by unit
    cr = LD.choose_reference
    one = _ref_row()
    ck.check("S6 choose_reference: one v0 row of the judged variant -> that row",
             cr([one], variant_id="v:x", item_id="i:sk", stem_key="sk", n_options=3)[0] is one)
    ck.check("S6 choose_reference: only a v1 row -> NONE (another vintage is never a fallback)",
             cr([_ref_row(vintage="grok-reasoning-v1")], variant_id="v:x", item_id="i:sk", stem_key="sk", n_options=3)[0] is None)
    ck.check("S6 choose_reference: v0 and v1 rows -> the v0 row, never v1",
             cr([_ref_row(vintage="grok-reasoning-v1", source_key="k9"), one], variant_id="v:x", item_id="i:sk", stem_key="sk",
                n_options=3)[0] is one)
    ck.check("S6 choose_reference: a row of another variant -> NONE",
             cr([_ref_row(variant_id="v:other")], variant_id="v:x", item_id="i:sk", stem_key="sk", n_options=3)[0] is None)
    for name, rows, kw, must in (
            ("two v0 rows (a tie is never broken)", [one, _ref_row(source_key="k2")], {}, "never tie-broken"),
            ("a board naming v1 without a separate registration", [one], {"board_vintage": "grok-reasoning-v1"},
             "never selected"),
            ("an unknown board vintage", [one], {"board_vintage": "grok-reasoning-v2"}, "is not"),
            ("an empty answer", [_ref_row(answer=" ")], {}, "empty answer"),
            ("an answer outside the option range", [_ref_row(answer="D")], {}, "outside the option range"),
            ("a NON_TERMINATED reference", [_ref_row(state="NON_TERMINATED")], {}, "NON_TERMINATED"),
            ("finish_reason length", [_ref_row(finish_reason="length")], {}, "finished"),
            ("finish_reason content_filter", [_ref_row(finish_reason="content_filter")], {}, "finished"),
            ("a reference of another item", [_ref_row(item_id="i:other")], {}, "item"),
            ("a row carrying gt / correct / raw", [_ref_row(gt="B")], {}, "never read")):
        args = dict(variant_id="v:x", item_id="i:sk", stem_key="sk", n_options=3)
        args.update(kw)
        ck.refused("S6 choose_reference: " + name, lambda rows=rows, args=args: cr(rows, **args), (must,))
    ck.check("S6 choose_reference with v1 AND a separate registration -> the v1 row (only then)",
             cr([_ref_row(vintage="grok-reasoning-v1")], board_vintage="grok-reasoning-v1", v1_registration="REG-V1",
                variant_id="v:x", item_id="i:sk", stem_key="sk", n_options=3)[0] is not None)
    ck.check("S6 the loader never selects gt / correct / raw (REF_COLS)",
             not set(LD.REF_COLS) & set(LD.FORBIDDEN_REF_COLS))
    # the loader on the fixture
    loaded = load_s3(ck, ev_path, out=ck.out)
    if loaded is None:
        return
    s = loaded.specs
    ck.check("S6 every loaded spec carries a valid provenance token", all(LD.verify(x) for x in s.values()))
    ck.check("S6 Q2 (v0 and v1 rows): the v0 row is chosen", s["m1"].reference is not None and
             s["m1"].reference.vintage == "grok-reasoning-v0", str(s["m1"].reference and s["m1"].reference.row_id))
    ck.check("S6 Q8 (solver order rotated; v0 answer C, key B): the reference is the v0 ANSWER rendered in the SOLVER's"
             " ordered options '(C) x8', not the sorted options' '(C) y8', never the key's '(B) ...'",
             s["m3"].reference is not None and s["m3"].reference.rendered == "(C) x8",
             repr(s["m3"].reference and s["m3"].reference.rendered))
    q = P.build_query(s["m3"])
    ck.check("S6 the reference block is exactly rejudge_reference.with_reference's (marker, then '(C) x8')",
             q == s["m3"].question + "\n\n" + P.REFERENCE_MARKER + "\n(C) x8")
    # D1: every trace's selected-answer letter is the contestant's own pred (never the key); some preds differ from it
    import re as _re
    ev = dv2views.open_eval("judge", ev_path)
    try:
        rows = {(m, v): (pred, gt) for m, v, pred, gt in ev.execute("SELECT model, seen_ck, pred, gt_raw FROM response")}
    finally:
        ev.close()
    letters, n_diff = [], 0
    for mid, x in sorted(s.items()):
        for who, tr in ((x.contestant_a, x.trace_a), (x.contestant_b, x.trace_b)):
            mm = _re.search(r"\[This model's selected answer: \(([A-J])\)", tr)
            pred, gt = rows[(who, x.variant_id)]
            letters.append((mid, who, mm.group(1) if mm else None, pred, gt))
            n_diff += pred != gt
    ck.check("S6 D1: each trace's '[This model's selected answer: (X)' letter is the contestant's pred, never the key"
             " (and the fixture has contestants whose pred differs from the key)",
             all(l == pred for _m, _w, l, pred, _g in letters) and n_diff >= 4, str(letters))
    ck.check("S6 the reference's ordering equals the question block's ordering; its v2 side is EVAL",
             all(x.reference.options_ordered_sha == x.question_options_sha and x.reference.side_v2 == "EVAL"
                 for x in s.values() if x.reference is not None))
    ck.check("S6 every loaded match carries leak material, KEY material included (D3)",
             all(L._has_material(loaded.materials[m]) and loaded.materials[m].key for m in s),
             json.dumps(loaded.manifest["material_counts"], sort_keys=True))
    other_blk = P.REFERENCE_MARKER + "\n(C) y2"
    ck.check("S6 D2: Q2's grok-reasoning-v1 reference (answer C) is collected as other-reference material, rendered in the"
             " solver's ordering", other_blk in loaded.materials["m1"].other_references,
             repr(loaded.materials["m1"].other_references))
    x1 = dataclasses.replace(s["m1"], trace_b=s["m1"].trace_b + "\n" + other_blk)
    hits = [h[0] for h in L.scan_hits(P.build_payload(x1, rub, 1), x1, rub, loaded.materials["m1"])]
    ck.check("S6 D2: another vintage's reference block smuggled into a loader-built trace is a wrong_reference hit",
             "wrong_reference" in hits, str(hits))
    # D3: the short key forms below MIN_MATERIAL are refused by the new marker rules
    for form in ("gt_raw: B", "gt_raw=B", '"answer_text": "x2"', "mA.is_correct_mathfix=0"):
        x2 = dataclasses.replace(s["m1"], trace_a=s["m1"].trace_a + "\n" + form)
        hits = [h[0] for h in L.scan_hits(P.build_payload(x2, rub, 1), x2, rub, loaded.materials["m1"])]
        ck.check("S6 D3: %r in a trace is a hit" % form, any(h.startswith("marker:") for h in hits), str(hits))
    side_only = LD.Loaded({"m1": s["m1"]}, {"m1": L.LeakMaterial(side=loaded.materials["m1"].side)}, loaded.manifest)
    ck.refused("S6 D3: an mcq slot with side material only (no KEY material)", lambda: W.JudgeWriter.create(
        os.path.join(tmp, "pK.db"), "PROBE", "pK", side_only, rub, _ctx()), ("no KEY material",))
    # D5: a MIXED referenced match is EXCLUDED per match (counted), the rest of the load is kept
    vid25 = variant_by_stem(ev_path, "Question number 25 about math?")
    reqs25 = [{"match_id": "x-mixed", "variant_id": vid25, "model_a": "mA", "model_b": "mB"},
              {"match_id": "x-ok", "variant_id": s["m2"].variant_id, "model_a": "mA", "model_b": "mB"}]
    ck.refused("S6 E1: a per-match exclusion the scheduler did NOT expect refuses the WHOLE load", lambda: LD.load_matches(
        reqs25, ev_path, out=lambda x: None), ("differ from the scheduler's expected_exclusions",))
    ck.refused("S6 E1: an expected exclusion under the wrong class refuses the whole load", lambda: LD.load_matches(
        reqs25, ev_path, out=lambda x: None, expected_exclusions={"x-mixed": "excluded_ordering_differs_from_solver"}),
        ("differ from",))
    ck.refused("S6 E1: an expected exclusion that does not happen refuses the whole load", lambda: LD.load_matches(
        reqs25, ev_path, out=lambda x: None, expected_exclusions={"x-mixed": "excluded_MIXED_referenced",
                                                                  "x-ok": "excluded_MIXED_referenced"}), ("differ from",))
    ck.refused("S6 E1: an expected exclusion class outside EXCLUSION_CODES", lambda: LD.load_matches(
        reqs25, ev_path, out=lambda x: None, expected_exclusions={"x-mixed": "excluded_reference_defect"}),
        ("the only per-match classes",))
    ck.refused("S6 E1: a load whose every match is excluded (0 loaded) is refused, even when expected", lambda:
               LD.load_matches(reqs25[:1], ev_path, out=lambda x: None,
                               expected_exclusions={"x-mixed": "excluded_MIXED_referenced"}), ("0 matches loaded",))
    lm = LD.load_matches(reqs25, ev_path, out=ck.out, expected_exclusions={"x-mixed": "excluded_MIXED_referenced"})
    ck.check("S6 D5: the MIXED referenced match (Q25: mB saw another ordering) is excluded per match, counted and listed;"
             " the other match of the load is kept", "x-mixed" not in lm.specs and "x-ok" in lm.specs and
             lm.manifest["counts"]["excluded_MIXED_referenced"] == 1 and
             lm.manifest["excluded"] == {"x-mixed": "excluded_MIXED_referenced"} and
             lm.manifest["excluded_by_model"] == {"mB": 1} and lm.manifest["excluded_by_variant"] == {vid25: 1},
             json.dumps([lm.manifest["excluded"], lm.manifest["excluded_by_model"]]))
    ev2 = dv2views.open_eval("judge", ev_path)
    try:
        sh6 = {m: sha for m, sha in ev2.execute("SELECT model, options_ordered_sha FROM response WHERE seen_ck=? AND model IN"
                                                 " ('mA', 'mB')", (s["m2"].variant_id,))}
        # [2026-09-24, merge of main 5b89159: data_v2's fixture gained a second BBH task (READY_ck_close_v2 D2) whose
        # variants carry ONE of uA / uB; the BBH match needs a variant BOTH answered, else an earlier refusal fires]
        bbh = ev2.execute("SELECT v.variant_id FROM variant v JOIN response r ON r.seen_ck = v.variant_id JOIN response r2"
                          " ON r2.seen_ck = v.variant_id WHERE r.source='BBH' AND r.model='uA' AND r2.model='uB'"
                          " ORDER BY v.variant_id").fetchall()
    finally:
        ev2.close()
    ck.check("S6 Q6: the reference is rendered from the SOLVER's list verbatim '(A) w6' (not mB's '(A) w6 ')",
             s["m2"].reference is not None and s["m2"].reference.rendered == "(A) w6",
             repr(s["m2"].reference and s["m2"].reference.rendered))
    ck.check("S6 D5 (1): Q6's orderings differ by whitespace only (byte shas differ) and are the SAME ordering: the"
             " referenced match is loaded, not MIXED", sh6.get("mA") != sh6.get("mB") and s["m2"].reference is not None and
             not s["m2"].question_options_sha.startswith("MIXED:"), str(sh6))
    lq = LD.load_matches([{"match_id": "q42", "variant_id": variant_by_stem(ev_path, "Question number 42 about law?"),
                           "model_a": "mA", "model_b": "mB"}], ev_path, out=lambda x: None)
    ck.check("S6 D5 (3): a MIXED NO-reference match (Q42) is ALLOWED, each trace resolved in its own ordering, keyed"
             " 'MIXED:a|b' and counted", "q42" in lq.specs and lq.specs["q42"].reference is None and
             lq.specs["q42"].question_options_sha.startswith("MIXED:ok1:") and
             lq.manifest["counts"]["loaded_MIXED_no_reference"] == 1 and
             "[This model's selected answer: (B) x42]" in lq.specs["q42"].trace_a and
             "[This model's selected answer: (B) w42]" in lq.specs["q42"].trace_b, repr(lq.specs.get("q42") and
                                                                                     lq.specs["q42"].trace_b[-60:]))
    if bbh:
        ck.refused("S6 D5 (4): a BBH match (lm-eval argument-dict options) is REFUSED from the judged path", lambda:
                   LD.load_matches([{"match_id": "bbh", "variant_id": bbh[0][0], "model_a": "uA", "model_b": "uB"}],
                                   ev_path, out=lambda x: None), ("BBH",))
        real_hs = LD._harness_shaped
        LD._harness_shaped = lambda options: False
        try:
            ck.refused("S6 D5 (4): the SOURCE leg alone (the harness-shaped backstop disabled) still refuses BBH", lambda:
                       LD.load_matches([{"match_id": "bbh", "variant_id": bbh[0][0], "model_a": "uA", "model_b": "uB"}],
                                       ev_path, out=lambda x: None), ("['BBH']",))
        finally:
            LD._harness_shaped = real_hs
    else:
        ck.check("S6 D5 (4): the fixture has an EVAL BBH variant", False)
    ln = LD.load_matches([{"match_id": "n2", "variant_id": variant_by_stem(ev_path, "Question number 42 about law?"),
                           "model_a": "mA", "model_b": "mB"}], ev_path, out=ck.out)
    ck.check("S6 NONE reference: Q42 (no row of the board's vintage) is judged with no reference, counted and printed",
             ln.specs["n2"].reference is None and ln.manifest["counts"]["reference_NONE"] == 1,
             json.dumps(ln.manifest["reference_none_reasons"], sort_keys=True))
    req31 = [{"match_id": "n1", "variant_id": variant_by_stem(ev_path, "Question number 31 about math?"),
              "model_a": "mA", "model_b": "mB"},
             {"match_id": "ok", "variant_id": s["m2"].variant_id, "model_a": "mA", "model_b": "mB"}]
    ck.refused("S6 D6 / E1: Q31 (a v0 row, no solver response row: the solver's ordering is unknown) refuses the WHOLE"
               " load, never NONE, never a per-match exclusion", lambda: LD.load_matches(req31, ev_path, out=lambda x: None),
               ("ordering", "unknown"))
    # E1: every other choose_reference refusal refuses the whole load (the reviewer's P1), and a broken solver join (P2)
    reqs_all = [{"match_id": m, "variant_id": x.variant_id, "model_a": x.contestant_a, "model_b": x.contestant_b}
                for m, x in s.items()]
    real_cr = LD.choose_reference
    for why in ("reference item i:AAA != the slot's item i:BBB", "2 grok-reasoning-v0 rows for variant v:x: more than one"
                " is REFUSED, never tie-broken", "answer 'D' of v:x is outside the option range (3 options)",
                "the reference of v:x is NON_TERMINATED", "the reference of v:x finished 'length'"):
        def raising(*a, _w=why, **k):
            raise SystemExit("[JUDGE-V2] choose_reference: " + _w)
        LD.choose_reference = raising
        try:
            ck.refused("S6 E1 (P1): a choose_reference refusal (%s) refuses the WHOLE load" % why[:40], lambda:
                       LD.load_matches(reqs_all, ev_path, out=lambda x: None), (why[:20],))
        finally:
            LD.choose_reference = real_cr
    real_sm = LD.dv2ingest.SOLVER_MODEL
    LD.dv2ingest.SOLVER_MODEL = "no-such-solver"
    try:
        ck.refused("S6 E1 (P2): a broken solver join (SOLVER_MODEL renamed) refuses the WHOLE load", lambda:
                   LD.load_matches(reqs_all, ev_path, out=lambda x: None), ("unknown",))
    finally:
        LD.dv2ingest.SOLVER_MODEL = real_sm
    ck.refused("S6 E1 (probe 4): JudgeWriter.create refuses an empty Loaded", lambda: W.JudgeWriter.create(
        os.path.join(tmp, "empty.db"), "PROBE", "empty", LD.Loaded({}, {}, loaded.manifest), rub, _ctx()),
        ("0 matches",))
    ck.check("S6 E2: the BBH source test is case-insensitive",
             all(LD.refused_source(x) for x in ("BBH", "bbh", " Bbh ")) and not LD.refused_source("MATH") and
             not LD.refused_source(None))
    ck.refused("S6 D6: choose_reference with an unknown solver ordering (callable -> None)", lambda: LD.choose_reference(
        [_ref_row()], variant_id="v:x", item_id="i:sk", stem_key="sk", n_options=lambda r: None), ("unknown",))
    ck.refused("S6 D6: the defect refusals run before the solver lookup (a NON_TERMINATED row with no solver row)",
               lambda: LD.choose_reference([_ref_row(state="NON_TERMINATED")], variant_id="v:x", item_id="i:sk",
                                           stem_key="sk", n_options=lambda r: None), ("NON_TERMINATED",))
    # PROBE B: a TRAIN item and a routing-only sentinel
    gi = gen_items(gen_path)
    tr = [r for r in gi if r[5] == "TRAIN" and r[4] == "MC_LETTER"][0]
    ck.refused("S6 PROBE B: a TRAIN (gen_view) variant requested as a match", lambda: LD.load_matches(
        [{"match_id": "b1", "variant_id": tr[0], "model_a": "mA", "model_b": "mB"}], ev_path, out=lambda x: None),
        ("not an EVAL variant",))
    ck.refused("S6 PROBE B: a routing-only EVAL sentinel requested as a match", lambda: LD.load_matches(
        [{"match_id": "b2", "variant_id": sentinels[0][0], "model_a": "mA", "model_b": "mB"}], ev_path, out=lambda x: None),
        ("not judgeable",))
    ck.refused("S6 a quarantined contestant (Llama)", lambda: LD.load_matches(
        [{"match_id": "b3", "variant_id": s["m1"].variant_id, "model_a": "mA", "model_b": "Meta-Llama-3-70B-Instruct"}],
        ev_path, out=lambda x: None), ("not judgeable",))
    ck.refused("S6 the loader pointed at the gen_view (open_eval refuses by the file's own meta)", lambda: LD.load_matches(
        [{"match_id": "b4", "variant_id": tr[0], "model_a": "mA", "model_b": "mB"}], gen_path, out=lambda x: None),
        ("REFUSED",))
    manual = {"b1": P.MatchInputs(match_id="b1", variant_id=tr[0], stem_key=tr[1][2:], component_id=None, corpus_type="mcq",
                                  question=tr[2], contestant_a="mA", contestant_b="mB", trace_a="ra", trace_b="rb",
                                  reference=None)}
    ck.refused("S6 PROBE B: hand-built MatchInputs (a TRAIN item) reach the writer -> no provenance token", lambda:
               W.JudgeWriter.create(os.path.join(tmp, "pB.db"), "PROBE", "pB", LD.Loaded(manual, {}, loaded.manifest), rub,
                                    _ctx()), ("did not come from loader",))
    # PROBE A: a key annotation + another variant's reference in the traces, no material (the reviewer's probe)
    gold = gold_inputs(match_id="A1", trace_a=gold_inputs().trace_a + "\nAnswer key for this question: (A) Mercury",
                       trace_b=gold_inputs().trace_b + "\n(B) Venus [reference minted for the other variant]")
    ck.refused("S6 PROBE A: a launch without the loader and without material", lambda: W.JudgeWriter.create(
        os.path.join(tmp, "pA.db"), "PROBE", "pA", LD.Loaded({"A1": gold}, {}, loaded.manifest), rub, _ctx()),
        ("did not come from loader",))
    signed_no_mat = LD.Loaded({"m1": s["m1"]}, {"m1": None}, loaded.manifest)
    ck.refused("S6 a loader spec with NO material and no NONE declaration", lambda: W.JudgeWriter.create(
        os.path.join(tmp, "pA2.db"), "PROBE", "pA2", signed_no_mat, rub, _ctx()), ("no leak material",))
    posted = []

    def fake(system, user):
        posted.append(1)
        return ('{"winner": "Model A"}', "azure:grok-4-1-fast-non-reasoning", 10, 0.1, "stop", {"_response_id": "r"})
    ck.refused("S6 D4: loader.sign (public name) refuses (probe H1)", lambda: LD.sign(manual["b1"]), ("private",))
    ns = {"__name__": "some_other_module", "LD": LD, "x": manual["b1"]}
    ck.refused("S6 D4: the selftest signing hook refuses any other caller", lambda: exec("LD._sign_for_selftest(x)", ns),
               ("selftest only",))
    ck.refused("S6 D4: an unregistered material-NONE declaration (probe H1's 'anything')", lambda: W.JudgeWriter.create(
        os.path.join(tmp, "pA5.db"), "PROBE", "pA5", signed_no_mat, rub, _ctx(), material_none_registration="anything"),
        ("not registered",))
    wn = W.JudgeWriter.create(os.path.join(tmp, "pA3.db"), "PROBE", "pA3", signed_no_mat, rub, _ctx(),
                              material_none_registration="DEV-material-none-selftest")
    lines = []
    wn.run(fake, out=lines.append)
    wn.close()
    ck.check("S6 with material NONE declared the slot is admitted and the scan line counts it WITHOUT material",
             len(posted) == 2 and wn.stats.without_material == 4 and wn.stats.with_material == 0 and
             any("without material 4" in x for x in lines), lines[-1][:160] if lines else "")
    # the run-level material witness on its own: material lost after create (a caller bug) refuses the run
    posted.clear()
    wm = W.JudgeWriter.create(os.path.join(tmp, "pA4.db"), "PROBE", "pA4", LD.Loaded({"m1": s["m1"]},
                              {"m1": loaded.materials["m1"]}, loaded.manifest), rub, _ctx())
    wm.materials["m1"] = None
    try:
        ck.refused("S6 material lost after create: the per-slot material check refuses before any call", lambda: wm.run(
            fake, out=lambda x: None), ("no leak material", "before any call"))
        ck.check("S6 ... with ZERO posts", len(posted) == 0, "posted %d" % len(posted))
    finally:
        wm.close()
    # D3: KEY material lost after create (side kept): the per-slot key check refuses before any call
    wk = W.JudgeWriter.create(os.path.join(tmp, "pA6.db"), "PROBE", "pA6", LD.Loaded({"m1": s["m1"]},
                              {"m1": loaded.materials["m1"]}, loaded.manifest), rub, _ctx())
    wk.materials["m1"] = L.LeakMaterial(side=loaded.materials["m1"].side)
    try:
        ck.refused("S6 D3: KEY material lost after create: the per-slot key check refuses before any call", lambda: wk.run(
            fake, out=lambda x: None), ("without KEY material", "before any call"))
        ck.check("S6 ... with ZERO posts", len(posted) == 0, "posted %d" % len(posted))
    finally:
        wk.close()
    # the key-material leg at writer level (C3): Q56's mA response carries "answer_text: x56"; the leak sorts LAST
    vid56 = variant_by_stem(ev_path, "Question number 56 about law?")
    reqs = [{"match_id": "a-clean", "variant_id": s["m2"].variant_id, "model_a": "mA", "model_b": "mB"},
            {"match_id": "z-leak", "variant_id": vid56, "model_a": "mA", "model_b": "mB"}]
    lk = LD.load_matches(reqs, ev_path, out=lambda x: None)
    hz = [h[0] for h in L.scan_hits(P.build_payload(lk.specs["z-leak"], rub, 1), lk.specs["z-leak"], rub,
                                     lk.materials["z-leak"])]
    ck.check("S6 the Q56 leak ('answer_text: x56' in mA's trace) is caught by the key material AND by the D3 marker rule",
             "answer_text: x56" in lk.materials["z-leak"].key and "key_material" in hz and "marker:answer_text" in hz,
             str(hz))
    posted.clear()
    wl = W.JudgeWriter.create(os.path.join(tmp, "pL.db"), "PROBE", "pL", lk, rub, _ctx())
    lines = []
    try:
        ck.refused("S6 a key-material leak in the LAST slot only stops the pre-scan", lambda: wl.run(fake, out=lines.append),
                   ("LEAKAGE", "key_material"))
        ck.check("S6 ... with ZERO posts, and the scan line printed on the refusal", len(posted) == 0 and
                 any("[LEAK-SCAN]" in x for x in lines), lines[-1][:160] if lines else "")
    finally:
        wl.close()


# ── S8 the opener lint (C4) is not vacuous ────────────────────────────────────────────────

def s8_lint(ck, tmp):
    from . import lint_opens as LO
    files, findings, allowed = LO.scan()
    ck.check("S8 lint_opens on this checkout: 0 findings (allowlisted calls printed)", files > 0 and not findings,
             "%d files, %d findings, %d allowlisted" % (files, len(findings), len(allowed)))
    root = os.path.join(tmp, "lintroot")
    os.makedirs(os.path.join(root, "tools", "analysis", "somepkg"))
    with open(os.path.join(root, "tools", "analysis", "somepkg", "bad.py"), "x", encoding="utf-8") as f:
        f.write("\n".join(["from data_v2 import ro as R", "import sqlite3", "", "def read(p):", "    return R.open_ro(p)", "",
                           "def read2():", "    return sqlite3." + "connect" + "('build/corpus_v2_mmlu.db')", ""]))
    _f, bad, _a = LO.scan(root)
    ck.check("S8 lint_opens REFUSES a data_v2.ro.open_ro call and a direct connect on a corpus_v2 file outside data_v2",
             sorted(r for _p, _l, r, _m in bad) == ["R1", "R2"], str(bad))
    root2 = os.path.join(tmp, "lintroot2")
    x = os.path.join(root2, "tools", "analysis", "x")
    os.makedirs(x)
    probes = {"a.py": ["import data_v2.ro", "def f(p):", "    return data_v2.ro.open_ro(p)"],
              "b.py": ["import sqlite3, os", 'EV = os.path.join("build", "eval_view_DEV.db")', "def g():",
                       '    return sqlite3.' + 'connect("file:%s?mode=ro" % EV, uri=True)'],
              "c.py": ["from data_v2 import ro", "opener = ro.open_ro", "def h(p):", "    return opener(p)"],
              "d.py": ["from judge_v2 import loader", "def k(inp):", "    return loader." + "sign(inp)"]}
    for fn, lines in probes.items():
        with open(os.path.join(x, fn), "x", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    _f, bad2, _a = LO.scan(root2)
    ck.check("S8 D4: the reviewer's four bypasses (dotted chain, path on another line, aliased opener, external sign) give"
             " 4 findings, one per file", sorted((p_, r) for p_, _l, r, _m in bad2) ==
             [("x/a.py", "R1"), ("x/b.py", "R2"), ("x/c.py", "R1"), ("x/d.py", "R3")], str(bad2))


def selftest(out=print):
    ck = Checks(out)
    tmp = tempfile.mkdtemp(prefix="jv2_selftest_")
    try:
        out("[SELFTEST-EJ] judge_v2 selftest (python %s, -O %s); synthetic fixture under %s; no DB of record; no call"
            % (sys.version.split()[0], "on" if not __debug__ else "off", tmp))
        rub_gold, inp = s1_payload(ck)
        s2_leakage(ck, rub_gold, inp, tmp)
        s4_combiner(ck, tmp)
        gen_path, ev_path = build_views(tmp)
        judgeable, sentinels = eval_variants(ev_path)
        out("[SELFTEST-EJ] fixture: gen_view %s, eval_view %s; EVAL judgeable MC variants %d, EVAL sentinels %d"
            % (os.path.basename(gen_path), os.path.basename(ev_path), len(judgeable), len(sentinels)))
        rub = s5_induction(ck, tmp, gen_path, ev_path, judgeable, sentinels)
        s6_loader(ck, tmp, gen_path, ev_path, judgeable, sentinels, rub)
        s3_writer(ck, rub, tmp, ev_path)
        s8_lint(ck, tmp)
    finally:
        _rmtree(tmp)
    if ck.fails:
        out("[SELFTEST-EJ] FAILED %d of %d checks: %s" % (len(ck.fails), ck.n, ck.fails))
        return 1
    out("[SELFTEST-EJ] ALL PASS (%d checks; synthetic; zero calls)" % ck.n)
    return 0


def main(argv):
    lines = []

    def out(s):
        print(s, flush=True)
        lines.append(s)
    tr = argv[argv.index("--transcript") + 1] if "--transcript" in argv else None
    if tr is not None and os.path.exists(tr):
        raise SystemExit("[JUDGE-V2] %s exists: a transcript is written once" % tr)
    try:
        return selftest(out)
    finally:
        if tr is not None:
            with open(tr, "x", encoding="utf-8", newline="\n") as f:
                f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
