"""k46_repost.py --selftest / --mutants: SYNTHETIC ONLY. A sealed synthetic eval view and a synthetic verdict store with REAL
request bodies (rejudge_reasoning.payload_bytes of a system turn carrying pair_noref.REF_SENTENCE), written under tempfile; a FAKE
poster injected as rejudge_reasoning.call_judge_full; the socket blocked; the REAL transport loader (archv2_pilot.pilot) on a fake
.env. No database of record is opened, nothing is posted. Every deciding path is asserted by VALUE against an INDEPENDENT
recomputation from the fixture's own truth and the fake poster's policy.

THE FIXTURE: 4 contestants, 120 items (health 40, math 80) in 60 CK-CLOSE components (twins share a component and a reference
class; one in three components ONE), 3 matches per item = 360 matches; 2 K46 INVALID matches (NONE). Order 1 shows contestant
A first. The K46 store's votes, and every pass / arm the fake poster answers, come from one policy function of (scenario, match,
arm, pass): its combined verdict is realised per order (A / B -> the shown position; TIE -> "Model A" in both orders, a flip;
INVALID -> unparseable text).
"""
import contextlib
import hashlib
import io
import json
import os
import random
import shutil
import socket
import subprocess
import sys
import tempfile
import zlib
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import k46_repost as K  # noqa: E402
from k46_repost import rr, rj, JW, REFERENCE_MARKER  # noqa: E402
from data_v2 import ro as dv2ro  # noqa: E402

MODELS = ["mA", "mB", "mC", "mD"]
REF, NOREF = K.load_n1(os.path.join(HERE, K.PAIR_NOREF_REL), K.PAIR_NOREF_BLOB)
SYSTEM = "You are an impartial judge.\n\nCorrectness first - verify before you compare:\n" + REF + "\nA wrong final answer cannot win.\n"
FAILS = []


def check(name, cond, detail=""):
    ok = bool(cond)
    print("  [%s] %s%s" % ("OK" if ok else "FAIL", name, "" if ok else "  -> " + str(detail)[:300]), flush=True)
    if not ok:
        FAILS.append(name)


def refuses(fn, *a, _want=None, **k):
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            fn(*a, **k)
        return False
    except SystemExit as e:
        return _want is None or _want in str(e)


def quiet(fn, *a, **k):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        r = fn(*a, **k)
    return r, buf.getvalue()


# ============================================================================================ fixture
def h(s):
    return int(hashlib.sha256(s.encode("utf-8")).hexdigest(), 16)


def build_fixture(tmp):
    rs = random.Random(11)
    items = []
    for anchor, n in (("health", 40), ("math", 80)):
        for j in range(n):
            iid = "i:%s%03d" % (anchor[0], j)
            items.append(dict(id=iid, var="v:" + iid[2:], comp="c:%s%03d" % (anchor[0], j // 2 * 2), anchor=anchor,
                              klass="ONE" if (j // 2) % 3 == 0 else "NONE", stem="s:" + iid[2:]))
    truth, v0 = {}, {}
    vp = os.path.join(tmp, "eval.db")
    c = dv2ro.create_new(vp)
    c.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)")
    c.execute("INSERT INTO meta VALUES ('view_kind', 'eval')")
    c.execute("CREATE TABLE side (item_id TEXT PRIMARY KEY, component_id TEXT, side TEXT, stratum_source TEXT, stratum_domain TEXT, corpora TEXT)")
    c.execute("CREATE TABLE variant (corpus_version TEXT, variant_id TEXT, item_id TEXT, PRIMARY KEY (corpus_version, variant_id))")
    c.execute("CREATE TABLE response (corpus_version TEXT, response_id TEXT, model TEXT, legacy_qid INTEGER, seen_ck TEXT, item_id TEXT,"
              " is_correct INTEGER, output_zlib BLOB, gt_raw TEXT, pred TEXT, PRIMARY KEY (corpus_version, response_id))")
    c.execute("CREATE TABLE reference (corpus_version TEXT, variant_id TEXT, vintage TEXT, source_key TEXT, item_id TEXT, correct INTEGER,"
              " PRIMARY KEY (corpus_version, variant_id, vintage, source_key))")
    k = 0
    for it in items:
        c.execute("INSERT INTO side VALUES (?,?,?,?,?,?)", (it["id"], it["comp"], "EVAL", "MMLU_PRO", it["anchor"].title(), "mmlu"))
        c.execute("INSERT INTO variant VALUES (?,?,?)", ("mmlu", it["var"], it["id"]))
        for mo in MODELS:
            k += 1
            truth[(mo, it["var"])] = int(rs.random() < 0.5)
            c.execute("INSERT INTO response VALUES (?,?,?,?,?,?,?,?,?,?)", ("mmlu", "x%d" % k, mo, k, it["var"], it["id"], truth[(mo, it["var"])], b"z", "g", "p"))
        if it["klass"] == "ONE":
            v0[it["var"]] = int(rs.random() < 0.8)
            c.execute("INSERT INTO reference VALUES (?,?,?,?,?,?)", ("mmlu", it["var"], K.VINTAGE, "sk", it["id"], v0[it["var"]]))
    c.commit()
    vsha = dv2ro.seal(c, vp, "k46_repost selftest eval view")["sha256_bytes"]
    matches = []
    n = 0
    for it in items:
        for _r in range(3):
            a, b = rs.sample(MODELS, 2)
            n += 1
            matches.append(dict(mid="F%04d" % n, it=it, a=a, b=b))
    return dict(items=items, truth=truth, v0=v0, matches=matches, view=vp, view_sha=vsha)


def key_side(fx, m):
    ka, kb = fx["truth"][(m["a"], m["it"]["var"])], fx["truth"][(m["b"], m["it"]["var"])]
    return ("A" if ka == 1 else "B") if ka + kb == 1 else None


def query_of(m, with_ref=True):
    q = "Question QID %s on %s: which option?" % (m["mid"], m["it"]["var"])
    if m["it"]["klass"] == "ONE" and with_ref:
        q += "\n\n" + REFERENCE_MARKER + "\n" + "(B) the reference's worked solution for %s" % m["it"]["var"]
    return q


def user_of(m, order):
    first, second = (m["a"], m["b"]) if order == 1 else (m["b"], m["a"])
    return rj.build_user_prompt(query_of(m), "trace by %s." % first, "trace by %s." % second)


def k46_policy(fx, m):
    i = int(m["mid"][1:])
    if m["it"]["klass"] == "NONE" and i in (7, 8):
        return "INVALID"
    r = h("k46|" + m["mid"]) % 100
    ks = key_side(fx, m) or "A"
    if r < 20:
        return "TIE"
    return ks if r < 80 else ("B" if ks == "A" else "A")


def realise(comb, m, order):
    """The text a judge returns at an order so that the two orders combine to comb."""
    if comb == "INVALID":
        return "no json here"
    if comb == "TIE":
        return '{"winner": "Model A", "confidence": 0.5}'
    winner = m["a"] if comb == "A" else m["b"]
    shown_first = m["a"] if order == 1 else m["b"]
    return '{"winner": "%s", "confidence": 0.9}' % ("Model A" if winner == shown_first else "Model B")


def vote_of(text):
    v, _c = rj.parse_judge(text)
    return {"Model A": "FIRST", "Model B": "SECOND", "TIE": "TIE"}.get(v, "INVALID")


def build_store(tmp, fx):
    from data_v2 import verdicts as dv2v
    K.configure_rr()
    sp = os.path.join(tmp, "store.db")
    s = dv2ro.create_new(sp)
    s.executescript(dv2v.DDL)
    for kk, v in (("schema_id", dv2ro.RUN_SCHEMA_ID), ("pool_id", "pv_fix"), ("run_id", "RUNFIX"), ("judge_requested", K.JUDGE),
                  ("max_tokens", "8192"), ("temperature_label", "omitted"), ("parse_version", JW.PARSE_VERSION)):
        s.execute("INSERT INTO run_meta VALUES (?, ?)", (kk, v))
    for m in fx["matches"]:
        it = m["it"]
        ref = ("ref:%s|%s|sk" % (it["var"], K.VINTAGE)) if it["klass"] == "ONE" else None
        for order in (1, 2):
            first, second = (m["a"], m["b"]) if order == 1 else (m["b"], m["a"])
            s.execute("INSERT INTO schedule VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
                "RUNFIX", m["mid"], order, 0, it["var"], it["stem"], it["comp"], m["a"], m["b"], first, second, "h1", "h2", ref,
                K.VINTAGE if ref else None, it["anchor"]))
    for m in fx["matches"]:
        it = m["it"]
        comb = k46_policy(fx, m)
        m["k46"] = comb
        ref = ("ref:%s|%s|sk" % (it["var"], K.VINTAGE)) if it["klass"] == "ONE" else None
        for order in (1, 2):
            body = rr.payload_bytes(SYSTEM, user_of(m, order))
            txt = realise(comb, m, order)
            s.execute("INSERT INTO verdict (run_id, match_id, presentation_order, draw_index, vote, raw_text, parse_version, payload_sha256,"
                      " body_zlib, body_codec, judge_requested, provider, response_model, finish_reason, max_tokens, temperature_sent,"
                      " temperature_label, content_filter, n_attempts, prompt_template_blob, script_blob, combiner_blob,"
                      " reference_row_id, reference_vintage, stem_key, pool_id, created_at) VALUES"
                      " (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
                          "RUNFIX", m["mid"], order, 0, vote_of(txt), txt, JW.PARSE_VERSION, hashlib.sha256(body).hexdigest(),
                          zlib.compress(body), "zlib", K.JUDGE, "azure", K.JUDGE, "stop", 8192, None, "omitted", 0, 1, "pt", "sb", "cb",
                          ref, K.VINTAGE if ref else None, it["stem"], "pv_fix", "t"))
    s.commit()
    s.close()
    return sp


def identity_of(fx):
    ms = fx["matches"]
    comb = Counter(m["k46"] for m in ms)
    kd = lambda kl: [m for m in ms if m["it"]["klass"] == kl and key_side(fx, m)]
    return dict(scheduled=len(ms), one=sum(1 for m in ms if m["it"]["klass"] == "ONE"), none=sum(1 for m in ms if m["it"]["klass"] == "NONE"),
                usable=comb["A"] + comb["B"] + comb["TIE"], invalid=comb["INVALID"],
                invalid_none=sum(1 for m in ms if m["k46"] == "INVALID" and m["it"]["klass"] == "NONE"),
                kd_none=len(kd("NONE")), kd_none_comps=len({m["it"]["comp"] for m in kd("NONE")}),
                kd_one=len(kd("ONE")), kd_one_comps=len({m["it"]["comp"] for m in kd("ONE")}))


# ============================================================================================ the fake poster
class Poster:
    def __init__(self, fx):
        self.fx = fx
        self.by = {m["mid"]: m for m in fx["matches"]}
        self.policy = None          # f(m, arm, pass) -> combined
        self.ctx = dict(pass_=None, leg=None)
        self.calls = 0
        self.fp = K.EXPECTED_FP

    def __call__(self, system, user, retries=6):
        self.calls += 1
        mid = user.split("QID ")[1].split(" ")[0]
        m = self.by[mid]
        order = 1 if user.index("trace by %s." % m["a"]) < user.index("trace by %s." % m["b"]) else 2
        swapped = NOREF in system
        if self.ctx["leg"] == "one":
            arm = "T1" if swapped else "C1"
        else:
            arm = "T" if swapped else "C"
        comb = self.policy(m, arm, self.ctx["pass_"])
        return (realise(comb, m, order), self.fp, 20, 0.01, "stop", {"_response_id": "fake-%s-%d" % (mid, order)})


# ============================================================================================ scenarios
PLAN_FIX = [None]
PLAN_BODY = ("# plan\n\n## Amendment 33 (x)\n\nnothing\n\n## Amendment 34 (2026-10-01) — the author's go on RP20's ONE leg: \"Yes, include it\""
             " (heading)\n\nRecorded: (1) \"Yes, include it\": the ONE leg is registered with RP20.\n\n## Amendment 35 (y)\n\nlater\n")


def stub_canary(cf, word="HELD"):
    """A canary outcome of record carrying a C1-v2 line, for RP20 / ONE scenarios whose directory has no canary run (C-K6)."""
    os.makedirs(cf.out_dir, exist_ok=True)
    open(K.outcome_path(cf, "canary"), "w", encoding="utf-8").write("=== stub ===\nC1-v2: %s\n" % word)
    return cf


def scenario_cfg(base, fx, store, name):
    d = os.path.join(base, name)
    os.makedirs(os.path.join(d, "ledger"))
    return K.Cfg(store_path=store, store_sha=K.sha256_file(store), eval_path=fx["view"], eval_sha=fx["view_sha"], pool="pv_fix", cv="mmlu",
                 run_id="RUNFIX", identity=identity_of(fx), n_set=30, set_file=os.path.join(d, "set.json"), out_dir=os.path.join(d, "out"),
                 ledger_dir=os.path.join(d, "ledger"), ready=os.path.join(d, "READY.md"), pre=dict(interval_form="normal"),
                 pair_noref=os.path.join(HERE, K.PAIR_NOREF_REL), pair_noref_blob=K.PAIR_NOREF_BLOB, boot=300, author_go_one="Yes, include it", plan_file=PLAN_FIX[0],
                 today=CLOCK["today"], now=CLOCK["now"])


import datetime  # noqa: E402
import time  # noqa: E402
CLOCK = dict(day=datetime.date(2026, 10, 5), shift=0.0)
CLOCK["today"] = lambda: CLOCK["day"]
CLOCK["now"] = lambda: time.time() + CLOCK["shift"]


def run_leg(cfg, poster, leg, pass_, budget_pilot=None, budget_run=None):
    poster.ctx.update(leg=leg, pass_=pass_)
    _r, o1 = quiet(K.launch, cfg, leg, pass_, K.PILOT_N, False, True, budget_pilot or 1000, workers=4)
    if "done:" not in o1 or " 0 calls posted" in o1:
        print("  [run_leg] the pilot of %s/%s posted nothing: %s" % (leg, pass_, o1[-1500:]), flush=True)
    _r, o2 = quiet(K.launch, cfg, leg, pass_, None, True, True, budget_run or 100000, workers=4)
    return o1 + o2


def flip(c):
    return {"A": "B", "B": "A"}.get(c, c)


def naive_dr(fx, setmids, pol1, pol2, pass1, pass2, by):
    """INDEPENDENT: convention-A difference share over the set."""
    d = 0
    for mid in setmids:
        a, b = pol1(by[mid], "C", pass1), pol2(by[mid], "C", pass2)
        d += 1 if (a == "INVALID" or b == "INVALID" or a != b) else 0
    return d, len(setmids)


def naive_delta(fx, klass, pol, by, tarm, carm):
    num, n = 0, 0
    for m in fx["matches"]:
        if m["it"]["klass"] != klass:
            continue
        ks = key_side(fx, m)
        if not ks:
            continue
        num += int(pol(m, tarm) == ks) - int(pol(m, carm) == ks)
        n += 1
    return num, n


def line_with(text, prefix):
    for l in text.split("\n"):
        if l.startswith(prefix):
            return l
    return ""


# ============================================================================================ the selftest
def selftest():
    del FAILS[:]
    print("[SELFTEST] k46_repost.py | mutant %s | script sha256-lf16 %s | 0 calls; tempfile fixtures; fake poster; socket blocked"
          % (K.MUTANT or "none", K.script_sha16_lf()), flush=True)
    base = tempfile.mkdtemp(prefix="k46_repost_selftest_")
    saved_sock = socket.socket.connect
    saved_rr = (rr.call_judge_full, rr.AZURE_ENDPOINT, rr.AZURE_KEY, rr.PROVIDER, rr.JUDGE_MODEL, rr.MAX_TOKENS, rr.TEMPERATURE)
    saved_env = os.environ.get("K46_REPOST_ENV_ROOT")
    saved_gate = K.ready_gate

    def no_net(*a, **k):
        raise SystemExit("[SELFTEST] a network connection was attempted")
    socket.socket.connect = no_net
    try:
        fx = build_fixture(base)
        store = build_store(base, fx)
        PLAN_FIX[0] = os.path.join(base, "plan.md")
        open(PLAN_FIX[0], "w", encoding="utf-8").write(PLAN_BODY)
        by = {m["mid"]: m for m in fx["matches"]}
        poster = Poster(fx)
        rr.call_judge_full = poster
        envroot = os.path.join(base, "env"); os.makedirs(envroot)
        open(os.path.join(envroot, ".env"), "w").write("AZURE_AI_ENDPOINT=https://k46r-selftest.invalid\nAZURE_GROK_API_KEY=fake\n")
        nokey = os.path.join(base, "nokey"); os.makedirs(nokey)
        open(os.path.join(nokey, ".env"), "w").write("AZURE_AI_ENDPOINT=https://k46r-selftest.invalid\n")
        os.environ["K46_REPOST_ENV_ROOT"] = envroot
        cfg0 = scenario_cfg(base, fx, store, "s0")
        ident = cfg0.identity
        print("  fixture: %s" % ident, flush=True)

        # ---- A. bodies and arms
        K.configure_rr()
        M, meta, before = quiet(K.read_store, cfg0, print)[0]
        m1 = next(m for m in M.values() if m["klass"] == "ONE")
        m0 = next(m for m in M.values() if m["klass"] == "NONE")
        s, u, b = K.stored_body(m0, 1)
        check("A1 stored body: decodes, hashes to payload_sha256, equals rr.payload_bytes(system, user)", b == rr.payload_bytes(s, u) and s == SYSTEM)
        st, ut, _p, _w = K.arm_payload(m0, "T", 1, (REF, NOREF))
        bt = rr.payload_bytes(st, ut)
        er, en = json.dumps(REF)[1:-1].encode(), json.dumps(NOREF)[1:-1].encode()
        i = b.index(er)
        check("A2 arm T: user turn byte-identical, REF swapped once, every byte outside the span equal to C's body",
              ut == u and REF not in st and st.count(NOREF) == 1 and bt[:i] == b[:i] and bt[i + len(en):] == b[i + len(er):])
        check("A3 a system turn carrying REF_SENTENCE twice is REFUSED (exactly one)",
              refuses(K.swap_system, SYSTEM + REF, (REF, NOREF), "probe", _want="2 times"))
        bad_bt = bt[:-3] + b"X" + bt[-2:]
        check("A4 a T body with one changed byte OUTSIDE the swapped span is REFUSED",
              refuses(K.check_outside_span, b, bad_bt, (REF, NOREF), "probe", _want="outside the swapped span"))
        s1, u1, b1 = K.stored_body(m1, 2)
        st1, ut1, _p, _w = K.arm_payload(m1, "T1", 2, (REF, NOREF))
        want_u = rj.build_user_prompt(query_of(by[m1["mid"]], with_ref=False), "trace by %s." % m1["b"], "trace by %s." % m1["a"])
        check("A5 arm T1: the reference block stripped (= build_user_prompt(question, traces)), the system swapped",
              ut1 == want_u and REFERENCE_MARKER not in ut1 and NOREF in st1)
        check("A6 a question slot with two reference markers is REFUSED for T1",
              refuses(K.strip_reference, u1.replace(REFERENCE_MARKER, REFERENCE_MARKER + "\n\n" + REFERENCE_MARKER, 1), "probe", _want="2 times"))
        tam = dict(m0); tam["body"] = dict(m0["body"]); tam["body"][1] = zlib.compress(b.replace(b"impartial", b"impartiaL"))
        check("A7 a stored body that no longer hashes to its payload_sha256 is REFUSED", refuses(K.stored_body, tam, 1, _want="does not hash"))
        pn = os.path.join(base, "pair_noref_copy.py")
        open(pn, "w", encoding="utf-8").write(open(os.path.join(HERE, K.PAIR_NOREF_REL), encoding="utf-8").read() + "\n# edited\n")
        check("A8 a pair_noref.py whose LF blob is not the pin is REFUSED (N1 read by AST at the pinned blob)",
              refuses(K.load_n1, pn, K.PAIR_NOREF_BLOB, _want="not the pinned"))
        check("A9 assert_body_source passes on the configured rr, and REFUSES with a temperature set",
              not refuses(K.assert_body_source) and (setattr(rr, "TEMPERATURE", 0.0) or refuses(K.assert_body_source, _want="not configured")))
        rr.TEMPERATURE = None

        # ---- B. store and identity
        bad_cfg = scenario_cfg(base, fx, store, "s_badsha"); bad_cfg.store_sha = "0" * 64
        check("B1 a store whose sha256 is not the pin is REFUSED", refuses(K.read_store, bad_cfg, print, _want="[PIN] store sha256"))
        idc = scenario_cfg(base, fx, store, "s_ident"); idc.identity = dict(idc.identity, none=idc.identity["none"] + 1)
        check("B2 an identity mismatch (NONE count + 1) is REFUSED", refuses(K.identity_gate, idc, M, meta, print, _want="[IDENTITY-GATE]"))
        check("B3 this script's combine() reproduces the store's match_status combined on %d of %d matches" % (len(M), len(M)),
              all(m["k46"] == m["k46_mine"] for m in M.values()) and not refuses(K.identity_gate, cfg0, M, meta, print))

        # ---- C. the draw
        d1 = K.draw_canary(cfg0, M); d2 = K.draw_canary(cfg0, M)
        comps = [x["component"] for x in d1["matches"]]
        check("C1 the canary draw: 30 matches in 30 distinct components (one per component), allocation sums to 30, reproducible",
              d1["n"] == 30 and len(set(comps)) == 30 and sum(v["alloc"] for v in d1["strata"].values()) == 30 and d1["set_hash"] == d2["set_hash"],
              (d1["n"], len(set(comps))))
        frame = Counter((m["klass"], m["anchor"]) for m in M.values() if m["k46"] in ("A", "B", "TIE"))
        exp = {"%s/%s" % s: 30 * c_ / sum(frame.values()) for s, c_ in frame.items()}
        check("C2 the allocation is proportional to the frame by largest remainder (|alloc - quota| < 1 per stratum)",
              all(abs(d1["strata"][s]["alloc"] - q) < 1 for s, q in exp.items()), (d1["strata"], exp))
        big = scenario_cfg(base, fx, store, "s_short"); big.n_set = 61
        check("C3 a set larger than the fresh components of a stratum is REFUSED, not filled", refuses(K.draw_canary, big, M, _want="[DRAW] REFUSED"))
        quiet(K.load_or_verify_set, cfg0, M, print, write=True)
        check("C4 the set file is written write-once and re-verified by the draw", quiet(K.load_or_verify_set, cfg0, M, print)[0][1] is True)
        js = json.load(open(cfg0.set_file)); js["matches"][0], js["matches"][1] = js["matches"][1], js["matches"][0]
        json.dump(js, open(cfg0.set_file, "w"))
        check("C5 a committed set whose order differs from the draw is REFUSED", refuses(K.load_or_verify_set, cfg0, M, print, _want="[SET]"))
        os.remove(cfg0.set_file)

        # ---- D. dry-runs (transport executed)
        cfgd = scenario_cfg(base, fx, store, "s_dry")
        quiet(K.load_or_verify_set, cfgd, M, print, write=True)
        r, out = quiet(K.launch, cfgd, "canary", "v2-1", None, False, False, None, dry=True)
        check("D1 dry-run canary: 'TRANSPORT PREFLIGHT: OK (endpoint host=k46r-selftest.invalid' printed through the REAL loader",
              any(l.startswith("TRANSPORT PREFLIGHT: OK (endpoint host=k46r-selftest.invalid") for l in out.split("\n")), out[-500:])
        check("D2 dry-run canary: 'would post 30 matches of record (60 calls)' and 0 posted, the first line is the pool",
              "[DRY-RUN] would post 30 matches of record (60 calls)" in out and out.split("\n")[0].startswith("POOL pv_fix") and poster.calls == 0, out[:200])
        r, out = quiet(K.launch, cfgd, "rp20", None, None, False, False, None, dry=True)
        check("D3 dry-run rp20: %d NONE matches x 2 arms = %d matches of record, %d calls" % (ident["none"], 2 * ident["none"], 4 * ident["none"]),
              "[DRY-RUN] would post %d matches of record (%d calls)" % (2 * ident["none"], 4 * ident["none"]) in out, line_with(out, "[DRY-RUN] would"))
        os.environ["K46_REPOST_ENV_ROOT"] = nokey
        rr.AZURE_KEY = None
        check("D4 dry-run with no key in the .env: the TRANSPORT preflight REFUSES the dry-run",
              refuses(K.launch, cfgd, "canary", "v2-1", None, False, False, None, dry=True, _want="TRANSPORT"))
        os.environ["K46_REPOST_ENV_ROOT"] = envroot

        # ---- E. gates (before any post)
        check("E1 a posting launch without --budget is REFUSED", refuses(K.launch, cfgd, "canary", "v2-1", 12, False, True, None, _want="explicit --budget")
              or refuses(K.launch, cfgd, "canary", "v2-1", 12, False, True, None, _want="[GATE]"))
        check("E2 the READY gate REFUSES with no committed READY file", refuses(K.launch, cfgd, "canary", "v2-1", 12, False, True, 24, _want="[GATE]"))
        check("E3 parse_ready: the first verdict line must name K46-REPOST and the LF sha; NOT READY anywhere refuses",
              K.parse_ready("# t\n\nREADY: K46-REPOST abc\n", "abc")[1] == [] and K.parse_ready("READY: X abc\n", "abc")[1]
              and K.parse_ready("READY: K46-REPOST abc\nNOT READY: y\n", "abc")[1])
        K.ready_gate = lambda cfg, what, go: print("[GATE] (selftest) %s OPEN" % what)
        check("E4 the ONE leg REFUSES without the author's go", refuses(K.launch, K.Cfg(**dict(cfgd.__dict__, author_go_one=None)), "one", None, 12,
                                                                         False, True, 48, _want="AUTHOR'S GO"))
        check("E5 --budget 20 < the pilot's 24 planned calls is REFUSED (iv)", refuses(K.launch, cfgd, "canary", "v2-1", 12, False, True, 20,
                                                                                        _want="(iv) this launch plans 24"))
        json.dump([{"test": "OTHER", "launch": "x", "calls": 13990, "ts": "t"}], open(os.path.join(cfgd.ledger_dir, "day_calls_2026-10-05.json"), "w"))
        check("E6 the DAY CAP: today's 13,990 + 24 > 14,000 is REFUSED, not trimmed",
              refuses(K.launch, cfgd, "canary", "v2-1", 12, False, True, 24, _want="(iii) the day cap"))
        os.remove(os.path.join(cfgd.ledger_dir, "day_calls_2026-10-05.json"))
        check("E7 --run before the pilot is cached is REFUSED", refuses(K.launch, cfgd, "canary", "v2-1", None, True, True, 100, _want="[RUN] REFUSED"))
        check("E8 v2-2 before a complete v2-1 is REFUSED", refuses(K.launch, cfgd, "canary", "v2-2", 12, False, True, 24, _want="v2-2 follows a COMPLETE v2-1"))

        # ---- F. the poster: hard cap, rollover, fingerprint
        poster.policy = lambda m, arm, ps: m["k46"]
        poster.ctx.update(leg="canary", pass_="v2-1")
        jobs = [(x["match_id"], "C") for x in K.draw_canary(cfgd, M)["matches"]][:12]
        dbp = os.path.join(base, "cap.db")
        con = K.open_cache(dbp)
        before_calls = poster.calls
        okn, err, posted, stop = K.post_jobs(cfgd, jobs, M, (REF, NOREF), con, 1, 10, "2026-10-05", {})
        con.close()
        check("F1 HARD CAP: --budget 10 inside the poster: exactly 10 posts made, 5 jobs cached, the 11th never made",
              len(posted) == 10 and poster.calls - before_calls == 10 and okn == 5 and stop and "BUDGET-STOP" in stop[0],
              (len(posted), poster.calls - before_calls, okn, stop))
        con = K.open_cache(os.path.join(base, "roll.db"))
        cnt = [0]
        CLOCK_SAVE = cfgd.today
        cfgd.today = lambda: datetime.date(2026, 10, 6) if poster.calls - cnt[0] >= 4 else datetime.date(2026, 10, 5)
        cnt[0] = poster.calls
        okn, err, posted, stop = K.post_jobs(cfgd, jobs, M, (REF, NOREF), con, 1, 1000, "2026-10-05", {})
        cfgd.today = CLOCK_SAVE
        con.close()
        check("F2 ROLLOVER: a local-date change stops the launch after the 4th post (2 jobs cached)",
              len(posted) == 4 and okn == 2 and stop and "ROLLOVER" in stop[0], (len(posted), okn, stop))
        poster.fp = "azure:another-model"
        con = K.open_cache(os.path.join(base, "fp.db"))
        okn, err, posted, stop = K.post_jobs(cfgd, jobs[:3], M, (REF, NOREF), con, 1, 1000, "2026-10-05", {})
        nrow = con.execute("SELECT COUNT(*) FROM verdict").fetchone()[0]
        con.close()
        poster.fp = K.EXPECTED_FP
        check("F3 a foreign fingerprint STOPS the run; nothing is cached for it; the posted call is counted",
              stop and "[FINGERPRINT]" in stop[0] and nrow == 0 and len(posted) >= 1, (stop, nrow, len(posted)))

        # ---- G. the canary end to end (three scenarios)
        setd = None

        def canary_scn(name, pol1, pol2):
            cf = scenario_cfg(base, fx, store, name)
            Mx = quiet(K.read_store, cf, print)[0][0]
            quiet(K.load_or_verify_set, cf, Mx, print, write=True)
            sd = K.draw_canary(cf, Mx)
            poster.policy = lambda m, arm, ps: (pol1 if ps == "v2-1" else pol2)(m)
            run_leg(cf, poster, "canary", "v2-1")
            run_leg(cf, poster, "canary", "v2-2")
            res, out = quiet(K.analyze_canary, cf)
            return cf, sd, res, out
        setmids = None
        # S1: v2-1 = K46 except 3 matches; v2-2 = v2-1 -> d_r 0 -> HELD; d_e 3/30
        sd0 = K.draw_canary(cfg0, M)
        setmids = [x["match_id"] for x in sd0["matches"]]
        diff3 = set(setmids[14:17])
        p_s1 = lambda m: (flip(m["k46"]) if m["k46"] in ("A", "B") else "A") if m["mid"] in diff3 else m["k46"]
        cf1, sd1, res1, out1 = canary_scn("can_held", p_s1, p_s1)
        t1 = res1["text"]
        dr_n = naive_dr(fx, setmids, lambda m, a, p: p_s1(m), lambda m, a, p: p_s1(m), "v2-1", "v2-2", by)
        check("G1 canary S1: C1-v2 HELD with d_r = 0/30 (independent: %d/%d), the falsifier's P1-LOW line printed" % dr_n,
              "C1-v2: HELD" in t1 and "= 0/30 =" in line_with(t1, "(C1-v2)") and dr_n == (0, 30)
              and any(l.startswith("P1 FAILS LOW") for l in t1.split("\n")), line_with(t1, "C1-v2:"))
        check("G2 canary S1: d_e(v2) = 3/30 (K46 vs v2-1)", "d_e(v2) (K46 vs v2-1) = 3/30" in t1, line_with(t1, "(C2-v2)"))
        check("G3 canary S1: C0 PASS on every row, 120 of 120 bodies byte-identical; outcome of record written (rc 0)",
              res1["rc"] == 0 and "120 of 120 (registered 120)" in t1 and "FAIL" not in "\n".join(l for l in t1.split("\n") if l.startswith("     (")),
              [l for l in t1.split("\n") if l.startswith("     (")])
        first = open(res1["path"], "rb").read()
        res1b, _o = quiet(K.analyze_canary, cf1)
        check("G4 write-once: a second --analyze-canary returns 3 and the file is byte-identical", res1b["rc"] == 3 and open(res1["path"], "rb").read() == first)
        check("G5 once the outcome exists, posting the leg is REFUSED", refuses(K.launch, cf1, "canary", "v2-2", 12, False, True, 24, _want="[RECORD]"))
        # S2: v2-2 flips 15 of 30 decisive (reversals) and 2 INVALID outside the pilot -> FAILED
        flip15 = set(setmids[12:27])
        inval2 = set(setmids[27:29])
        p_s2b = lambda m: "INVALID" if m["mid"] in inval2 else (flip(m["k46"]) if m["k46"] in ("A", "B") else "A") if m["mid"] in flip15 else m["k46"]
        cf2, sd2, res2, out2 = canary_scn("can_failed", lambda m: m["k46"], p_s2b)
        t2 = res2["text"]
        dr2 = naive_dr(fx, setmids, lambda m, a, p: m["k46"], lambda m, a, p: p_s2b(m), "v2-1", "v2-2", by)
        check("G6 canary S2: C1-v2 FAILED at d_r = %d/%d (independent), the C1-v2 falsifier sentence printed" % dr2,
              "C1-v2: FAILED" in t2 and "= %d/%d =" % dr2 in line_with(t2, "(C1-v2)")
              and any(l.startswith("FALSIFIER FIRES: C1-v2 FAILED") for l in t2.split("\n")), line_with(t2, "C1-v2:"))
        check("G7 canary S2: P6 FAILED (4 unusable calls > 3) and P3 FAILED (reversals >= 3)",
              line_with(t2, "  P6").endswith("-> FAILED") and line_with(t2, "  P3").endswith("-> FAILED"), (line_with(t2, "  P6"), line_with(t2, "  P3")))
        # S3: v2-1 differs from K46 on 4, v2-2 differs from v2-1 on the same 4 back -> d_r 4/30 = 0.133 -> UNDETERMINED (UB > 0.15)
        diff4 = set(setmids[13:17])
        p_s3a = lambda m: ("TIE" if m["k46"] != "TIE" else "A") if m["mid"] in diff4 else m["k46"]
        cf3, sd3, res3, out3 = canary_scn("can_und", p_s3a, lambda m: m["k46"])
        t3 = res3["text"]
        check("G8 canary S3: d_r = 4/30 = 0.1333 -> C1-v2 UNDETERMINED (the 95%% UB above 0.15, the LB below); P1 HELD; P2 HELD (Delta 0)",
              "C1-v2: UNDETERMINED" in t3 and "= 4/30 =" in line_with(t3, "(C1-v2)") and line_with(t3, "  P1").endswith("-> HELD")
              and line_with(t3, "  P2").endswith("-> HELD"), (line_with(t3, "C1-v2:"), line_with(t3, "  P1"), line_with(t3, "  P2")))
        sup3 = line_with(t3, "     SUPPORT (C1-v2")
        check("G8b D1: one match per component -> 'Kish mean cluster size 1.000, one per component' and 'DEFF 1.000 (ANALYTIC', n_eff 30.0",
              "Kish mean cluster size 1.000, one per component" in sup3 and "DEFF 1.000 (ANALYTIC" in sup3 and "n_eff 30.0" in sup3, sup3[:260])
        ivd = K.boot_mean([1, 1, 0, 0], ["a", "a", "b", "b"], 200, 42)
        txt_d = K.support_text(ivd, 4, 2, "probe")
        check("G8c D1: two components of two perfectly correlated matches -> DEFF exactly 2.000 (= Kish 2.000), n_eff 2.0",
              "DEFF 2.000 (ANALYTIC" in txt_d and "Kish mean cluster size 2.000" in txt_d and "n_eff 2.0 " in txt_d, txt_d[:220])
        ivu = K.boot_mean([1, 0, 1, 0], ["a", "a", "b", "b"], 200, 42)
        check("G8d D1: within-component differences only -> DEFF 0.000 (clustered variance 0), never the Kish size",
              "DEFF 0.000 (ANALYTIC" in K.support_text(ivu, 4, 2, "probe"), K.support_text(ivu, 4, 2, "probe")[:200])
        # the window
        cfw = scenario_cfg(base, fx, store, "can_window")
        Mw = quiet(K.read_store, cfw, print)[0][0]
        quiet(K.load_or_verify_set, cfw, Mw, print, write=True)
        poster.policy = lambda m, arm, ps: m["k46"]
        run_leg(cfw, poster, "canary", "v2-1")
        CLOCK["shift"] = K.WINDOW_S + 5
        check("G9 v2-2 more than 7,200 s after v2-1's last row is REFUSED (UNDETERMINED BY VALIDITY otherwise)",
              refuses(K.launch, cfw, "canary", "v2-2", 12, False, True, 24, _want="UNDETERMINED BY VALIDITY"))
        CLOCK["shift"] = 0.0
        # the pilot guard (canary: all rows): 1 INVALID of 12 = 8.3% > 5%
        cfp = scenario_cfg(base, fx, store, "can_pilot")
        Mp = quiet(K.read_store, cfp, print)[0][0]
        quiet(K.load_or_verify_set, cfp, Mp, print, write=True)
        pil = [x["match_id"] for x in K.draw_canary(cfp, Mp)["matches"]][:12]
        poster.policy = lambda m, arm, ps: "INVALID" if m["mid"] == pil[3] else m["k46"]
        poster.ctx.update(leg="canary", pass_="v2-1")
        check("G10 a canary pilot with 1 of 12 INVALID FAILS its truncation guard", refuses(K.launch, cfp, "canary", "v2-1", 12, False, True, 24,
                                                                                        _want="FAILED its truncation guard"))
        check("G11 ... and --run is then REFUSED", refuses(K.launch, cfp, "canary", "v2-1", None, True, True, 100, _want="above 5%"))
        # partial: v2-1 pilot only
        cfq = scenario_cfg(base, fx, store, "can_partial")
        Mq = quiet(K.read_store, cfq, print)[0][0]
        quiet(K.load_or_verify_set, cfq, Mq, print, write=True)
        poster.policy = lambda m, arm, ps: m["k46"]
        poster.ctx.update(leg="canary", pass_="v2-1")
        quiet(K.launch, cfq, "canary", "v2-1", 12, False, True, 24)
        rq, _o = quiet(K.analyze_canary, cfq)
        rq2, _o = quiet(K.analyze_canary, cfq)
        parts = [f for f in os.listdir(cfq.out_dir) if "_partial_" in f]
        check("G12 an incomplete canary: rc 2, a TIMESTAMPED partial file each time (two files), no outcome of record",
              rq["rc"] == 2 and rq2["rc"] == 2 and len(parts) == 2 and not os.path.exists(K.outcome_path(cfq, "canary")), (rq["rc"], parts))
        cfr = scenario_cfg(base, fx, store, "can_noform"); cfr.pre = dict(interval_form=None)
        check("G13 the interval form unset: an analysis is REFUSED (precondition)", refuses(K.analyze_canary, cfr, _want="[PRECONDITION]"))

        # ---- H. RP20 end to end
        def rp20_scn(cf, pol, leg="rp20"):
            poster.policy = lambda m, arm, ps: pol(m, arm)
            poster.ctx.update(leg=leg, pass_=None)
            run_leg(cf, poster, leg, None)
            return quiet(K.analyze_pair, cf, leg)
        # R1 identical arms, in the S3 directory (the canary floor present, d_r = 4/30): d(T, C) = 0 -> NOT shown
        pol_id = lambda m, arm: m["k46"] if m["k46"] != "INVALID" else "A"
        res_r1, o_r1 = rp20_scn(cf3, pol_id)
        tr1 = res_r1["text"]
        check("H1 RP20 identical arms: Delta_A = +0.0000, C1 EQUIVALENT, the reuse disclosure printed; d(T, C) = 0 -> 'NOT shown'",
              "C1: EQUIVALENT" in tr1 and "= +0.0000 |" in line_with(tr1, "(C1)") and any(l.startswith("C1 EQUIVALENT: reuse is admissible") for l in tr1.split("\n"))
              and "is NOT shown" in tr1, (line_with(tr1, "C1:"), line_with(tr1, "(C1)")[:200]))
        check("H2 RP20 C0: %d C bodies byte-identical, %d T bodies swapped exactly in the span, key-decidable %d in %d components"
              % (2 * ident["none"], 2 * ident["none"], ident["kd_none"], ident["kd_none_comps"]),
              "%d of %d (registered %d)" % (2 * ident["none"], 2 * ident["none"], 2 * ident["none"]) in tr1
              and "key-decidable %d in %d" % (ident["kd_none"], ident["kd_none_comps"]) in tr1 and "RP20" in tr1,
              [l for l in tr1.split("\n") if l.startswith("     (")])
        # R2 T better: T always the key side (decisive); C: the K46 policy -> GAIN; in S1's dir (floor 0/30, SE 0) -> CHANGES
        def pol_gain(m, arm):
            ks = key_side(fx, m)
            if arm == "T":
                return ks or (m["k46"] if m["k46"] != "INVALID" else "A")
            return m["k46"] if m["k46"] != "INVALID" else "A"
        res_r2, o_r2 = rp20_scn(cf1, pol_gain)
        tr2 = res_r2["text"]
        num, den = naive_delta(fx, "NONE", pol_gain, by, "T", "C")
        check("H3 RP20 T better: Delta_A = %+.4f (independent %d/%d), C1 GAIN, the falsifier sentence with the price printed" % (num / den, num, den),
              "C1: GAIN" in tr2 and "= %+.4f |" % (num / den) in line_with(tr2, "(C1)")
              and any(l.startswith("FALSIFIER FIRES: C1 GAIN") and "%+.4f" % (num / den) in l for l in tr2.split("\n")),
              (line_with(tr2, "C1:"), line_with(tr2, "(C1)")[:220]))
        check("H4 RP20 C2: d(T, C) above the canary floor by interval -> 'THE SENTENCE CHANGES VERDICTS'", "THE SENTENCE CHANGES VERDICTS" in tr2,
              line_with(tr2, "     d(T, C) - d_r"))
        # R3 T worse, in a fresh directory (no canary floor) -> LOSS, NO_FLOOR
        cfl = stub_canary(scenario_cfg(base, fx, store, "rp20_loss"))
        pol_loss = lambda m, arm: pol_gain(m, "C" if arm == "T" else "T")
        res_r3, o_r3 = rp20_scn(cfl, pol_loss)
        tr3 = res_r3["text"]
        num3, den3 = naive_delta(fx, "NONE", pol_loss, by, "T", "C")
        check("H5 RP20 T worse: Delta_A = %+.4f (independent), C1 LOSS; no canary floor -> 'NOT READ' and P3 FAILED" % (num3 / den3),
              "C1: LOSS" in tr3 and "= %+.4f |" % (num3 / den3) in line_with(tr3, "(C1)") and "d_r(v2) from RP21 C1-v2: NOT READ" in tr3
              and line_with(tr3, "  P3").endswith("-> FAILED"), line_with(tr3, "C1:"))
        # the RP20 pilot guard on the KEY-DECIDABLE rows: one unusable kd row in the pilot
        cfk = stub_canary(scenario_cfg(base, fx, store, "rp20_kdguard"))
        Mk = quiet(K.read_store, cfk, print)[0][0]
        sch = K.leg_schedule(cfk, "rp20", Mk)
        pj = K.pilot_jobs(sch)
        kd_pilot = [mid for mid, arm in pj if key_side(fx, by[mid])]
        target = kd_pilot[0]
        poster.policy = lambda m, arm, ps: "INVALID" if (m["mid"] == target and arm == "T") else pol_id(m, arm)
        poster.ctx.update(leg="rp20", pass_=None)
        n_kd_rows = sum(1 for mid, arm in pj if key_side(fx, by[mid]))
        check("H6 RP20 pilot: 1 unusable of %d rows (%.1f%% <= 5%%) but 1 of %d KEY-DECIDABLE rows (> 5%%) FAILS the guard"
              % (len(pj), 100.0 / len(pj), n_kd_rows),
              1.0 / len(pj) <= 0.05 < 1.0 / n_kd_rows and refuses(K.launch, cfk, "rp20", None, 12, False, True, 48, _want="FAILED its truncation guard"),
              (len(pj), n_kd_rows))
        # prescribed C1 bounds through the REAL readout (K.FORCE_C1_IV, SELFTEST-ONLY): re-analyse R1's caches with the outcome removed
        def forced(cf, leg, ivf):
            if os.path.exists(K.outcome_path(cf, leg)):
                os.remove(K.outcome_path(cf, leg))
            K.FORCE_C1_IV[leg] = ivf
            try:
                return quiet(K.analyze_pair, cf, leg)[0]["text"]
            finally:
                K.FORCE_C1_IV.clear()
        iv_shift = dict(point=0.02, se=0.006, n_lo90=0.010, n_hi90=0.030, p_lo90=0.010, p_hi90=0.030, n_lo95=0.008, n_hi95=0.032, p_lo95=0.008, p_hi95=0.032)
        iv_und = dict(point=0.02, se=0.02, n_lo90=-0.013, n_hi90=0.053, p_lo90=-0.013, p_hi90=0.053, n_lo95=-0.02, n_hi95=0.06, p_lo95=-0.02, p_hi95=0.06)
        tf = forced(cf3, "rp20", iv_shift)
        check("H7 RP20 readout on prescribed bounds 90% [+0.010, +0.030], 95% [+0.008, +0.032]: 'C1: EQUIVALENT, with a detectable shift of +'",
              "C1: EQUIVALENT, with a detectable shift of +" in tf.split("\n"), line_with(tf, "C1:"))
        tf = forced(cf3, "rp20", iv_und)
        check("H7b RP20 readout on 90% [-0.013, +0.053], 95% [-0.020, +0.060]: 'C1: UNDETERMINED' and the falsifier NOT FIRED (neither)",
              "C1: UNDETERMINED" in tf.split("\n") and "FALSIFIER: NOT FIRED (C1 UNDETERMINED" in tf, line_with(tf, "C1:"))
        tf = forced(cf3, "rp20", dict(point=0.002, se=0.02, n_lo90=-0.030, n_hi90=0.035, p_lo90=-0.030, p_hi90=0.035, n_lo95=-0.045, n_hi95=0.042,
                                      p_lo95=-0.045, p_hi95=0.042))
        check("H8 EQUIVALENT is read on the 90% CI: 90% (-0.030, +0.035) inside, 95% (-0.045, +0.042) not -> the readout prints 'C1: EQUIVALENT'",
              "C1: EQUIVALENT" in tf.split("\n"), line_with(tf, "C1:"))
        check("H9 both_agree: normal EQUIVALENT vs percentile UNDETERMINED -> UNDETERMINED, both printed",
              K.decide(K.word_rp20, dict(n_lo90=-0.03, n_hi90=0.03, p_lo90=-0.03, p_hi90=0.041, n_lo95=-0.04, n_hi95=0.04, p_lo95=-0.04,
                                         p_hi95=0.05), "both_agree") == ("UNDETERMINED", ("EQUIVALENT", "UNDETERMINED")))
        for lo, hi, want in ((0.10, 0.15, "HELD"), (0.10, 0.1501, "UNDETERMINED"), (0.1501, 0.30, "FAILED"), (0.15, 0.30, "UNDETERMINED")):
            got = K.word_c1v2(lambda lev: (lo, hi))
            check("H10 C1-v2 on 95%% bounds [%.4f, %.4f] -> %s (HELD iff UB <= 0.15; FAILED iff LB > 0.15)" % (lo, hi, want), got == want, got)
        for lo, hi, want in ((-0.2, -0.01, "LOSS"), (0.01, 0.2, "GAIN"), (-0.1, 0.0, "UNDETERMINED")):
            check("H11 ONE C1 on 95%% bounds [%+.2f, %+.2f] -> %s" % (lo, hi, want), K.word_one(lambda lev: (lo, hi)) == want)

        # ---- I. the ONE leg end to end
        cfo = stub_canary(scenario_cfg(base, fx, store, "one_loss"))
        def pol_one(m, arm):
            ks = key_side(fx, m) or "A"
            if arm == "C1":
                return ks if fx["v0"].get(m["it"]["var"]) == 1 else flip(ks)
            return ks if h("t1|" + m["mid"]) % 2 == 0 else flip(ks)
        res_o, o_o = rp20_scn(cfo, pol_one, leg="one")
        to = res_o["text"]
        num_o, den_o = naive_delta(fx, "ONE", pol_one, by, "T1", "C1")
        check("I1 ONE leg: Delta1_A = %+.4f (independent %d/%d), C1 LOSS (the reference helps), falsifier NOT FIRED" % (num_o / den_o, num_o, den_o),
              "C1: LOSS" in to and "= %+.4f |" % (num_o / den_o) in line_with(to, "(C1)") and "FALSIFIER: NOT FIRED." in to,
              (line_with(to, "C1:"), line_with(to, "(C1)")[:200]))
        check("I1b ONE readout prints 'per-contestant agreement with the reference side (C1 vs T1): NOT BUILT' (b3dd18ab)",
              "     per-contestant agreement with the reference side (C1 vs T1): NOT BUILT" in "\n".join(l[:76] for l in to.split("\n")))
        cfo2 = stub_canary(scenario_cfg(base, fx, store, "one_und"))
        res_o2, _o = rp20_scn(cfo2, lambda m, arm: pol_id(m, arm), leg="one")
        check("I2 ONE leg identical arms: C1 UNDETERMINED -> the falsifier FIRES (the reference's value does not transfer)",
              "C1: UNDETERMINED" in res_o2["text"] and any(l.startswith("FALSIFIER FIRES: C1 UNDETERMINED") for l in res_o2["text"].split("\n")),
              line_with(res_o2["text"], "C1:"))
        # ---- K. the delta of 2026-10-01 (C-K2, C-K3, C-K6)
        cfg_go = scenario_cfg(base, fx, store, "k_go")
        ok_go, why = K.go_one_check(cfg_go)
        check("K1 the ONE go: \"Yes, include it\" occurs exactly once in the BODY of '## Amendment 34' (heading excluded) -> VERIFIED",
              ok_go and "occurs 1 time(s) in the BODY" in why and "carries it 1 time(s), is not counted" in why, why)
        two = os.path.join(base, "plan_two.md")
        open(two, "w", encoding="utf-8").write(PLAN_BODY.replace("## Amendment 35", "again \"Yes, include it\"\n\n## Amendment 35"))
        cfg_two = stub_canary(K.Cfg(**dict(cfg_go.__dict__, plan_file=two)))
        check("K2 the quotation twice in the Amendment 34 body: a ONE posting launch is REFUSED by the count check",
              refuses(K.launch, cfg_two, "one", None, 12, False, True, 48, _want="occurs 2 time(s)"))
        head = os.path.join(base, "plan_head.md")
        open(head, "w", encoding="utf-8").write(PLAN_BODY.replace("Recorded: (1) \"Yes, include it\": the", "Recorded: (1) the"))
        check("K3 the quotation only in the heading line: REFUSED (0 in the body)",
              refuses(K.launch, stub_canary(K.Cfg(**dict(cfg_go.__dict__, plan_file=head))), "one", None, 12, False, True, 48, _want="occurs 0 time(s)"))
        check("K4 a go string other than the quoted one is REFUSED",
              refuses(K.launch, stub_canary(K.Cfg(**dict(cfg_go.__dict__, author_go_one="yes"))), "one", None, 12, False, True, 48, _want="[GO]"))
        r, out = quiet(K.launch, cfg_go, "rp20", None, None, False, False, None, dry=True)
        check("K5 every rp20 dry-run prints the combined statement: RP20 %d + ONE %d = %d matches against 4000, Amendment 34 VERIFIED"
              % (2 * ident["none"], 2 * ident["one"], 2 * (ident["none"] + ident["one"])),
              line_with(out, "[4K-RULE]").startswith("[4K-RULE] RP20 %d + ONE %d = %d matches <= 4000" % (2 * ident["none"], 2 * ident["one"],
                                                                                                         2 * (ident["none"] + ident["one"])))
              and "-> VERIFIED" in line_with(out, "[4K-RULE]"), line_with(out, "[4K-RULE]"))
        cfg_ord = scenario_cfg(base, fx, store, "k_order")
        check("K6 C-K6: an rp20 posting launch with NO canary outcome of record is REFUSED", refuses(K.launch, cfg_ord, "rp20", None, 12, False, True, 48,
                                                                                                    _want="[ORDER]"))
        stub_canary(cfg_ord, "FAILED")
        check("K7 C-K6: RP21's C1-v2 FAILED -> rp20 and one posting REFUSED (RP20 re-registered pre-data)",
              refuses(K.launch, cfg_ord, "rp20", None, 12, False, True, 48, _want="C1-v2 is FAILED")
              and refuses(K.launch, cfg_ord, "one", None, 12, False, True, 48, _want="C1-v2 is FAILED"))
        stub_canary(cfg_ord, "UNDETERMINED")
        poster.policy = lambda m, arm, ps: pol_id(m, arm)
        poster.ctx.update(leg="rp20", pass_=None)
        r, out = quiet(K.launch, cfg_ord, "rp20", None, 12, False, True, 48)
        check("K8 C-K6: C1-v2 UNDETERMINED (read, not FAILED) -> the rp20 pilot posts (48 calls)", "done: 48 calls posted" in out, line_with(out, "done:"))
        # OK4 + OK8: both passes INVALID on the same 14 non-pilot set matches -> convention A 14/30 (FAILED), convention B 0/16
        inv14 = set(setmids[12:26])
        p_both = lambda m: "INVALID" if m["mid"] in inv14 else m["k46"]
        cfa, _sda, resa, _oa = canary_scn("can_conva", p_both, p_both)
        ta = resa["text"]
        check("K9 OK4 + OK8: a pair unusable in BOTH passes is a difference (A 14/30) and C1-v2 is read on convention A: FAILED, with B 0/16 beside",
              "C1-v2: FAILED" in ta.split("\n") and "= 14/30 =" in line_with(ta, "(C1-v2)") and "convention B (usable in both) 0/16" in ta,
              (line_with(ta, "C1-v2:"), line_with(ta, "(C1-v2)")[:120]))
        check("K10 OK4 at unit level: changed(INVALID, INVALID) == 1, changed(NON_TERMINATED, CONTENT_FILTER) == 1, changed(A, A) == 0",
              K.changed("INVALID", "INVALID") == 1 and K.changed("NON_TERMINATED", "CONTENT_FILTER") == 1 and K.changed("A", "A") == 0)
        # OK5: the key-decidable census in C0 (b): a cfg whose census differs by one -> C0 FAIL -> C1 UNDETERMINED BY VALIDITY
        cf_c = K.Cfg(**dict(cf3.__dict__, identity=dict(cf3.identity, kd_none=cf3.identity["kd_none"] + 1)))
        os.remove(K.outcome_path(cf_c, "rp20"))
        rc_c, _o = quiet(K.analyze_pair, cf_c, "rp20")
        tc = rc_c["text"]
        check("K11 OK5: a key-decidable census of %d (not %d) FAILS C0 (b) and voids C1 (UNDETERMINED BY VALIDITY)" % (ident["kd_none"], ident["kd_none"] + 1),
              "C1: UNDETERMINED BY VALIDITY" in tc.split("\n") and "FAIL" in line_with(tc, "     (b) identity"), (line_with(tc, "     (b) identity")[:160],
                                                                                                                       line_with(tc, "C1:")))
        cf_o = K.Cfg(**dict(cfo.__dict__, identity=dict(cfo.identity, kd_one_comps=cfo.identity["kd_one_comps"] - 1)))
        os.remove(K.outcome_path(cf_o, "one"))
        tco = quiet(K.analyze_pair, cf_o, "one")[0]["text"]
        check("K12 OK5 (ONE leg): a component census off by one FAILS C0 (b) -> C1 UNDETERMINED BY VALIDITY", "C1: UNDETERMINED BY VALIDITY" in tco.split("\n"),
              line_with(tco, "C1:"))
        # incident aaf12c77: the --analyze path must configure rr itself (a fresh analysis process starts at rr's default model)
        cf_rr = K.Cfg(**dict(cf3.__dict__))
        os.remove(K.outcome_path(cf_rr, "rp20"))
        rr.JUDGE_MODEL = "grok-4-1-fast-reasoning"          # rejudge_reasoning's default, as a fresh --analyze process has it
        rr.MAX_TOKENS = 8192; rr.TEMPERATURE = None
        t_rr = quiet(K.analyze_pair, cf_rr, "rp20")[0]["text"]
        d_line = line_with(t_rr, "     (d) T bodies differ")
        check("K14 incident aaf12c77: --analyze from rr's DEFAULT model configures rr itself: C0 (d) PASS %d of %d, no [BODY-RECHECK] line"
              % (2 * ident["none"], 2 * ident["none"]),
              " PASS " in d_line and d_line.rstrip().endswith("%d of %d" % (2 * ident["none"], 2 * ident["none"])) and "[BODY-RECHECK]" not in t_rr
              and rr.JUDGE_MODEL == K.JUDGE, d_line)
        os.remove(K.outcome_path(cf_rr, "rp20"))
        saved_cfg_rr = K.configure_rr
        def wrong_rr():
            saved_cfg_rr(); rr.JUDGE_MODEL = "grok-4-1-fast-reasoning"
        K.configure_rr = wrong_rr
        try:
            r_bad, o_bad = quiet(K.analyze_pair, cf_rr, "rp20")
        finally:
            K.configure_rr = saved_cfg_rr
            K.configure_rr()
        check("K15 a re-check failure is PRINTED, not swallowed: '[BODY-RECHECK] %d of %d T rows FAIL' with the first mismatch and its rr model"
              % (2 * ident["none"], 2 * ident["none"]),
              ("[BODY-RECHECK] %d of %d T rows FAIL the re-check; the first: " % (2 * ident["none"], 2 * ident["none"])) in o_bad
              and "rr model 'grok-4-1-fast-reasoning'" in o_bad and "C1: UNDETERMINED BY VALIDITY" in r_bad["text"], line_with(o_bad, "[BODY-RECHECK]")[:200])
        os.remove(K.outcome_path(cf_rr, "rp20"))
        check("K13 C-K1: the interval form of record is NORMAL", K.PRECONDITIONS["interval_form"] == "normal" and K.real_cfg().pre["interval_form"] == "normal")
        # ---- J. the RP20 partial (C0 FAIL, UND) and branch coverage
        cfx = stub_canary(scenario_cfg(base, fx, store, "rp20_partial"))
        poster.policy = lambda m, arm, ps: pol_id(m, arm)
        poster.ctx.update(leg="rp20", pass_=None)
        quiet(K.launch, cfx, "rp20", None, 12, False, True, 48)
        rx, _o = quiet(K.analyze_pair, cfx, "rp20")
        check("J1 an incomplete RP20 cache: rc 2 (partial), C0 FAIL, C1 UNDETERMINED BY VALIDITY, the falsifier NOT EVALUATED",
              rx["rc"] == 2 and "C1: UNDETERMINED BY VALIDITY" in rx["text"] and "FALSIFIER: NOT EVALUATED" in rx["text"], line_with(rx["text"], "C1:"))
        # the ONE leg: prescribed bounds (GAIN; and LOSS at -0.10 for P1), and a partial ONE cache
        tf = forced(cfo, "one", dict(point=0.05, se=0.01, n_lo90=0.03, n_hi90=0.07, p_lo90=0.03, p_hi90=0.07, n_lo95=0.03, n_hi95=0.07, p_lo95=0.03, p_hi95=0.07))
        check("I3 ONE readout on 95%% [+0.03, +0.07]: 'C1: GAIN' and the falsifier FIRES", "C1: GAIN" in tf.split("\n") and "FALSIFIER FIRES: C1 GAIN" in tf,
              line_with(tf, "C1:"))
        tf = forced(cfo, "one", dict(point=-0.10, se=0.02, n_lo90=-0.13, n_hi90=-0.07, p_lo90=-0.13, p_hi90=-0.07, n_lo95=-0.14, n_hi95=-0.06, p_lo95=-0.14, p_hi95=-0.06))
        check("I4 ONE readout at Delta1 -0.10: C1 LOSS, P1 HELD ([-0.15, -0.05])", "C1: LOSS" in tf.split("\n") and line_with(tf, "  P1").endswith("-> HELD"),
              line_with(tf, "  P1"))
        cfop = stub_canary(scenario_cfg(base, fx, store, "one_partial"))
        poster.policy = lambda m, arm, ps: pol_id(m, arm)
        poster.ctx.update(leg="one", pass_=None)
        quiet(K.launch, cfop, "one", None, 12, False, True, 48)
        rop, _o = quiet(K.analyze_pair, cfop, "one")
        check("I5 an incomplete ONE cache: rc 2, C1 UNDETERMINED BY VALIDITY", rop["rc"] == 2 and "C1: UNDETERMINED BY VALIDITY" in rop["text"], line_with(rop["text"], "C1:"))
        # R4 'near' (P3 / P4 HELD, P6 FAILED): a canary with d_r 4/30 first, then T = C except a TIE on every 8th NONE match; C = K46 except a flip on
        # every 10th; one T INVALID outside the pilot
        cf4, _sd4, _r4c, _o4c = canary_scn("can_near", p_s3a, lambda m: m["k46"])
        sch4 = K.leg_schedule(cf4, "rp20", quiet(K.read_store, cf4, print)[0][0])
        pil4 = {mid for mid, _a in K.pilot_jobs(sch4)}
        nonp = [mid for mid, _a in sch4 if mid not in pil4]
        inval_t = nonp[0]
        def pol_near(m, arm):
            i = int(m["mid"][1:])
            c = m["k46"] if m["k46"] != "INVALID" else "A"
            if i % 10 == 0 and c in ("A", "B"):
                c = flip(c)
            if arm == "T":
                if m["mid"] == inval_t:
                    return "INVALID"
                if i % 7 == 0 and c in ("A", "B"):
                    return "TIE"
            return c
        res_r4, _o = rp20_scn(cf4, pol_near)
        tr4 = res_r4["text"]
        check("H12 RP20 'near': P3 HELD (d(T, C) in [0.08, 0.15], minus the floor in [-0.03, +0.05]), P4 HELD (d(C, K46) in [0.07, 0.15]), P6 FAILED"
              " (2 unusable T calls of %d > 0.3%%)" % (2 * ident["none"]),
              line_with(tr4, "  P3").endswith("-> HELD") and line_with(tr4, "  P4").endswith("-> HELD") and line_with(tr4, "  P6").endswith("-> FAILED"),
              (line_with(tr4, "  P3"), line_with(tr4, "  P4"), line_with(tr4, "  P6")))
        missing = sorted(K.BRANCHES - K.HIT)
        check("J2 every criterion / prediction / falsifier / write branch EXECUTED through the readouts (%d of %d)" % (len(K.HIT & K.BRANCHES), len(K.BRANCHES)),
              not missing, missing)
    finally:
        socket.socket.connect = saved_sock
        (rr.call_judge_full, rr.AZURE_ENDPOINT, rr.AZURE_KEY, rr.PROVIDER, rr.JUDGE_MODEL, rr.MAX_TOKENS, rr.TEMPERATURE) = saved_rr
        if saved_env is None:
            os.environ.pop("K46_REPOST_ENV_ROOT", None)
        else:
            os.environ["K46_REPOST_ENV_ROOT"] = saved_env
        K.ready_gate = saved_gate
        K.remove_db_guard()
        shutil.rmtree(base, ignore_errors=True)
    print("[SELFTEST] %s" % ("%d check(s) FAILED: %s" % (len(FAILS), FAILS) if FAILS else "all checks passed; 0 calls; nothing of record opened"),
          flush=True)
    return 1 if FAILS else 0


def mutants():
    rows = []
    for m in K.MUTANTS:
        env = dict(os.environ, K46R_MUTANT=m, PYTHONIOENCODING="utf-8")
        p = subprocess.run([sys.executable, os.path.join(HERE, "k46_repost.py"), "--selftest"], env=env, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        failed = [l.strip() for l in (p.stdout or "").split("\n") if l.strip().startswith("[FAIL]")]
        rows.append((m, "KILLED" if p.returncode != 0 else "SURVIVED", failed[0][7:100] if failed else (p.stdout or p.stderr or "")[-160:].replace("\n", " ")))
    print("MUTANT TABLE (k46_repost.py --mutants):")
    for m, st, first in rows:
        print("  %-20s %-9s %s" % (m, st, first))
    k = sum(1 for r in rows if r[1] == "KILLED")
    print("KILLED %d of %d" % (k, len(rows)))
    return 0 if k == len(rows) else 1
