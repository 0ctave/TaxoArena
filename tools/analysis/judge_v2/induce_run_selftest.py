"""The selftest of judge_v2.induce_run (ARCH-V2-INDUCE-RUBRIC-1). SYNTHETIC ONLY: the E-J fixture (judge_v2.selftest.build_views:
tiny source DBs written as NEW files under tempfile.gettempdir(), ingested, split and viewed by data_v2), a STUB poster
with call_judge_full's shape, a temporary ledger directory. No DB of record is opened; no call is posted.

    python tools/analysis/judge_v2/induce_run_selftest.py [--transcript PATH]
    python -O tools/analysis/judge_v2/induce_run_selftest.py [--transcript PATH]

Every check is an explicit comparison printed PASS / FAIL (no assert: the -O run executes the same branches). Every
registered print branch is executed: P1 HELD / FAILED / NOT SCORED, P2 HELD / FAILED / NOT SCORED, the falsifier FIRED / NOT
FIRED, UNDETERMINED, STOPPED, V1-V4 PASS / FAIL, ARTEFACT OF RECORD YES / NO.
The fixture runs under a DEV seed with no registration (the registered selection runs ONCE, on the real split).
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

from ._base import dv2ro, dv2views, rr  # noqa: E402
from . import induce_cache as IC  # noqa: E402
from . import induce_overlap_audit as OA  # noqa: E402
from . import induce_run as R  # noqa: E402
from . import induction as I  # noqa: E402
from . import selftest as T  # noqa: E402
import accepted_tests_ledger as atl  # noqa: E402

DEV_SEED = "DEV-induce-run-selftest"


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
                             "2. Prefer the response whose final answer is correct.\n3. Otherwise TIE."})
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
        out("[SELFTEST-INDUCE-RUN] %s selftest (python %s, -O %s); synthetic fixture under %s; stub poster; zero calls"
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
        # the prompt pins
        R.check_prompt_pins(out=lambda s: None)
        ck.check("the registered prompt shas hold (INDUCTION_SYSTEM 4c4bf36f..., USER_TEMPLATE 7ed21eba...)",
                 R.sha256_text(I.INDUCTION_SYSTEM) == R.SYSTEM_SHA and
                 R.sha256_text(I.INDUCTION_USER_TEMPLATE) == R.USER_TEMPLATE_SHA)
        real = I.INDUCTION_SYSTEM
        I.INDUCTION_SYSTEM = real + " "
        try:
            ck.refused("a changed INDUCTION_SYSTEM", lambda: R.check_prompt_pins(out=lambda s: None), ("not the registered",))
        finally:
            I.INDUCTION_SYSTEM = real
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
        ck.check("A: V1-V4 PASS, the artefact of record written (mode x) and loadable; P1 HELD, P2 HELD, falsifier NOT FIRED",
                 all(rA["validity"][k] is True for k in ("V1", "V2", "V3", "V4")) and os.path.exists(pA.artefact) and
                 has(L, "ARTEFACT OF RECORD: YES") and has(L, "P1 (the first attempt is valid; point probability 0.8): HELD")
                 and has(L, "P2 (V1-V4 pass): HELD") and has(L, "FALSIFIER (three formal failures): NOT FIRED"), "\n".join(L[-8:]))
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
        c = dv2ro.open_ro(pA.cache)
        try:
            ev_seq = [w for (w,) in c.execute("SELECT what FROM event ORDER BY seq")]
        finally:
            c.close()
        ck.check("A: the cache's event log orders launch < reply_committed < eval_view_opened",
                 ev_seq == ["launch", "reply_committed", "eval_view_opened"], str(ev_seq))
        ck.check("A: the outcome carries the disclosures of record (finding 1, C4 population, C5 dry-run eval_view)",
                 has(L, "selection corrected before the first call") and has(L, "population narrowed to the judged corpus")
                 and has(L, "the dry-run process opened eval_view"))
        ck.check("A: the artefact is labelled 'MCQ rubric, population mmlu-pro-v2 TRAIN' and its manifest records the"
                 " population filter", art["manifest"]["artefact_label"] == R.ARTEFACT_LABEL and
                 art["manifest"]["population"] == {"contracts": ["MC_LETTER"], "corpus_version": "mmlu-pro-v2"})
        c = dv2ro.open_ro(pA.cache)
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
                 has(L, "): FAILED") and has(L, "P2 (V1-V4 pass): HELD"), str([r["failure_class"] for r in rB["rows"]]))
        # C. three formal failures: UNDETERMINED, no 4th attempt, no artefact, the falsifier FIRED
        bad_key = json.dumps({"system_prompt": "x", "rubric": "y"})
        pC, sC, rC = launch(ck, tmp, gen, ev, "C", [(bad_key, "stop"), ("{\"rubric\": \"cut", "length"),
                                                    ("", "content_filter"), (GOOD, "stop")], gen_sha, eval_sha)
        L = rC["outcome_lines"]
        ck.check("C: KEY, LENGTH, CONTENT_FILTER classified; exactly 3 posts of the same body (no 4th); UNDETERMINED; no"
                 " artefact; P1 FAILED, P2 NOT SCORED, falsifier FIRED",
                 [r["failure_class"] for r in rC["rows"]] == ["KEY", "LENGTH", "CONTENT_FILTER"] and len(sC.calls) == 3 and
                 len(set(sC.calls)) == 1 and not os.path.exists(pC.artefact) and has(L, "UNDETERMINED") and
                 has(L, "ARTEFACT OF RECORD: NO") and has(L, "P2 (V1-V4 pass): NOT SCORED") and
                 has(L, "FALSIFIER (three formal failures): FIRED"), str([r["failure_class"] for r in rC["rows"]]))
        # D. V2: a valid reply that carries EVAL key material is NOT of record (no re-post: V2 is not a formal failure)
        e = dv2ro.open_ro(ev)
        try:
            at = e.execute("SELECT answer_text FROM response WHERE answer_text IS NOT NULL ORDER BY response_id LIMIT 1"
                           ).fetchone()[0]
        finally:
            e.close()
        leaky = json.dumps({"rubric": "1. Correct final answers win.\n2. Remember answer_text: %s\n3. Otherwise TIE." % at})
        linesD = []
        pD, sD, rD = launch(ck, tmp, gen, ev, "D", [leaky, GOOD], gen_sha, eval_sha, out=linesD.append)
        L = rD["outcome_lines"]
        ck.check("D: V2 failure is announced as NEVER a re-post (finding 3 (ii)), with one post only",
                 has(linesD, "NEVER a re-post") and len(sD.calls) == 1)
        ck.check("D: V2 FAILS on EVAL key material (%r); NO artefact of record; no re-post; P1 HELD, P2 FAILED" % at,
                 rD["validity"]["V2"] is False and bool(rD["hits"]) and not os.path.exists(pD.artefact) and
                 len(sD.calls) == 1 and has(L, "ARTEFACT OF RECORD: NO") and has(L, "P2 (V1-V4 pass): FAILED") and
                 has(L, "V2 leak check against EVAL key material: FAIL"), str(rD["hits"][:3]))
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
        c = dv2ro.open_ro(pE.cache)
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
                 and has(L, "P1 (the first attempt is valid; point probability 0.8): NOT SCORED"), "\n".join(L[:6]))
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
        mu = dv2ro.create_new(os.path.join(tmp, "population_unit.db"))
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
        c = dv2ro.open_ro(pL2.cache)
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
        out("[SELFTEST-INDUCE-RUN] FAILED %d of %d checks: %s" % (len(ck.fails), ck.n, ck.fails))
        return 1
    out("[SELFTEST-INDUCE-RUN] ALL PASS (%d checks; synthetic; zero calls)" % ck.n)
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
