"""JV2-RATE-PROBE selftest (registration docs/judge_v2_program.md L18979-L19094, 1.10: "--selftest under python and -O,
including a localhost stub with 200 / 429 + Retry-After / 5xx / timeout, a synthetic crash, rollover, cap and the content
gate, each with a killed mutant"). ZERO real calls: every post goes to a ThreadingHTTPServer on 127.0.0.1; the endpoint
is https://127.0.0.1:<port> (so the imported transport_preflight passes) and the wire's inner urlopen (REAL_URLOPEN, a
SELFTEST-ONLY setting the live guard refuses on any non-loopback host) rewrites it to http. rejudge_reasoning's backoff
sleeps are scaled through a patched rr.time (also refused by the live guard). The .env is a temporary file; the real
.env, the ledgers of record and every DB of record are never opened (K46 readings and corpus keys are substituted).

    python tools/analysis/jv2_rate_probe.py --selftest
    python -O tools/analysis/jv2_rate_probe.py --selftest

Each test returns through check(); an unexpected exception inside a test counts as a failure (reported separately).
A mutant is KILLED when at least one check of its target tests fails with the mutant set.
"""
import email.utils
import http.server
import json
import os
import re
import shutil
import sqlite3
import sys
import tempfile; import scratch_dir  # TEMP-SPRAWL: temp on E:, removed at exit
import threading
import time
import types
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import jv2_rate_probe as M  # noqa: E402
from archv2_pilot import accounting as ACC  # noqa: E402
from archv2_pilot import pilot as PL  # noqa: E402
from judge_v2 import payload as P  # noqa: E402
from judge_v2._base import rr  # noqa: E402
import accepted_tests_ledger as atl  # noqa: E402
import split_side  # noqa: E402

ORIG_URLOPEN = urllib.request.urlopen
KEY = "selftest-key-7f3a9c"          # never a real key; the DB bytes are scanned for it
SCALE = 0.001
DAY1, DAY2 = "2031-01-01", "2031-01-02"
ITEM_RE = re.compile(r"\(item (\d+)\)")

FAILS = []
CHECKS = {"n": 0}
LOG = []


def check(cond, label):
    CHECKS["n"] += 1
    if not cond:
        FAILS.append(label)
    return bool(cond)


def quiet(s):
    LOG.append(str(s))


# ── the stub server ────────────────────────────────────────────────────────────────────────────────────────────────

class Stub:
    """behave(idx, attempt) -> dict(status, delay, drop, headers, body, content, finish)."""

    def __init__(self):
        self.lock = threading.Lock()
        self.active = 0
        self.max_active = {}
        self.requests = []              # (t_arrival, idx, attempt, has_api_key)
        self.attempts = {}
        self.behave = lambda idx, att: {}
        self.step_of = M.step_of_slot()
        stub = self

        class H(http.server.BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, *a):
                return

            def do_POST(self):
                n = int(self.headers.get("Content-Length") or 0)
                raw = self.rfile.read(n)
                d = json.loads(raw.decode("utf-8"))
                m = ITEM_RE.search(d["messages"][1]["content"])
                idx = int(m.group(1)) if m else -1
                with stub.lock:
                    stub.attempts[idx] = stub.attempts.get(idx, 0) + 1
                    att = stub.attempts[idx]
                    stub.active += 1
                    st = stub.step_of.get(idx, "?")
                    stub.max_active[st] = max(stub.max_active.get(st, 0), stub.active)
                    stub.requests.append((time.time(), idx, att, self.headers.get("api-key") == KEY,
                                          "temperature" in d))
                try:
                    b = dict({"status": 200, "delay": 0.05, "drop": False, "headers": {}, "content": None,
                              "finish": "stop"}, **stub.behave(idx, att))
                    time.sleep(b["delay"])
                    if b["drop"]:
                        self.close_connection = True
                        return
                    if b["status"] == 200:
                        content = b["content"] if b["content"] is not None else json.dumps(
                            {"critique_a": "a", "critique_b": "b", "comparison": "c", "winner": "Model A",
                             "confidence": 0.8})
                        body = json.dumps({"id": "stub-%d-%d" % (idx, att), "model": "grok-4-1-fast-non-reasoning",
                                           "choices": [{"message": {"role": "assistant", "content": content},
                                                        "finish_reason": b["finish"]}],
                                           "usage": {"prompt_tokens": 1500, "completion_tokens": 250}}).encode()
                    else:
                        body = json.dumps(b.get("body") or {"error": {"code": str(b["status"]),
                                                                      "message": "stub %d" % b["status"]}}).encode()
                    self.send_response(b["status"])
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(body)))
                    for k, v in b["headers"].items():
                        self.send_header(k, v)
                    self.end_headers()
                    self.wfile.write(body)
                finally:
                    with stub.lock:
                        stub.active -= 1

        class Srv(http.server.ThreadingHTTPServer):
            def handle_error(self, request, client_address):      # a mutant's malformed body: counted, not printed
                stub.errors += 1
        self.errors = 0
        self.srv = Srv(("127.0.0.1", 0), H)
        self.srv.daemon_threads = True
        self.port = self.srv.server_address[1]
        self.th = threading.Thread(target=self.srv.serve_forever, daemon=True)
        self.th.start()

    def reset(self, behave=None):
        with self.lock:
            self.active = 0
            self.max_active = {}
            self.requests = []
            self.attempts = {}
        self.behave = behave or (lambda idx, att: {})

    def close(self):
        self.srv.shutdown()
        self.srv.server_close()


JOURNAL_WATCH = {"path": None, "late": []}


def rewrite(req, *a, **k):
    """SELFTEST-ONLY inner urlopen: https://127.0.0.1 -> http://127.0.0.1 (same bytes, same headers). With a
    JOURNAL_WATCH path it is also the WRITE-AHEAD WITNESS: at the instant an HTTP attempt leaves, the slot's journal row
    must already be committed (read through a separate read-only connection)."""
    if JOURNAL_WATCH["path"]:
        m = ITEM_RE.search(json.loads(req.data.decode("utf-8"))["messages"][1]["content"])
        c = sqlite3.connect("file:%s?mode=ro" % JOURNAL_WATCH["path"].replace("\\", "/"), uri=True, timeout=10)
        try:
            ok = c.execute("SELECT 1 FROM invocation WHERE match_id=?", ("JV2RP-%03d" % int(m.group(1)),)).fetchone()
        finally:
            c.close()
        if not ok:
            JOURNAL_WATCH["late"].append(int(m.group(1)))
    url = req.full_url.replace("https://127.0.0.1", "http://127.0.0.1")
    r2 = urllib.request.Request(url, data=req.data, method=req.get_method(), headers=dict(req.header_items()))
    return ORIG_URLOPEN(r2, *a, **k)


# ── the environment ────────────────────────────────────────────────────────────────────────────────────────────────

class Env:
    def __init__(self, stub, endpoint=None, key=KEY):
        self.root = tempfile.mkdtemp(prefix="jv2rp_")
        self.ledger = os.path.join(self.root, "experiment_results")
        self.out = os.path.join(self.ledger, "jv2_rate_probe")
        os.makedirs(self.ledger)
        ep = endpoint if endpoint is not None else "https://127.0.0.1:%d" % stub.port
        with open(os.path.join(self.root, ".env"), "w", encoding="utf-8") as f:
            f.write("AZURE_AI_ENDPOINT=%s\n" % ep)
            if key is not None:
                f.write("AZURE_GROK_API_KEY=%s\n" % key)
        self.day = [DAY1]

    def ledger_rows(self, day=None):
        return atl._rows(atl.day_ledger_path(self.ledger, day or self.day[0]))

    def cleanup(self):
        shutil.rmtree(self.root, ignore_errors=True)


def k46_source():
    rub, _ = PL.load_generic_rubric()
    system = P.build_system(rub)
    man = P.recipe_manifest(rub)
    import hashlib
    return {"n": 5328, "q10": 4581, "q50": 5369, "q90": 6805, "median_completion_tokens": 254.0,
            "system_template_sha": [man["system_template_sha"]], "rubric_sha": [man["rubric_sha"]],
            "system_turn_sha256": hashlib.sha256(system.encode("utf-8")).hexdigest(), "unresolved": 0, "store": "stub"}


SAVED_RR = {}


def setup(env, **over):
    """Every SELFTEST-ONLY setting for a loopback run; reset() restores all of them."""
    for n in ("PROVIDER", "JUDGE_MODEL", "MAX_TOKENS", "TEMPERATURE", "AZURE_ENDPOINT", "AZURE_KEY", "ROOT", "time"):
        SAVED_RR.setdefault(n, getattr(rr, n))
    M.TIME_SCALE = SCALE
    M.CLOCK = lambda: env.day[0]
    M.PROCESS_LIST = lambda: []
    M.OPTIMIZE = 0
    M.REAL_URLOPEN = rewrite
    M.CORPUS_KEYS = lambda: {"synthetic corpus": {"nothing"}}
    M.K46_SOURCE = K46
    rr.time = types.SimpleNamespace(time=time.time, sleep=lambda s: time.sleep(s * SCALE))
    for k, v in over.items():
        setattr(M, k, v)


def reset():
    """Every SELFTEST-ONLY setting back to its default EXCEPT MUTANT (the runner owns it)."""
    for n in M.SELFTEST_SETTINGS:
        if n != "MUTANT":
            setattr(M, n, M._DEFAULTS.get(n, None))
    JOURNAL_WATCH["path"] = None
    for n, v in SAVED_RR.items():
        setattr(rr, n, v)
    if urllib.request.urlopen is not ORIG_URLOPEN:
        urllib.request.urlopen = ORIG_URLOPEN


def launch(env, mode, expect=None):
    return M.Launch(env.out, env.ledger, mode, False, expect, env.root, quiet).execute()


def refused(fn):
    try:
        fn()
    except SystemExit as e:
        return str(e) or "SystemExit"
    return None


def db(env):
    return sqlite3.connect(os.path.join(env.out, M.DB_NAME))


def journal_state(env):
    p = os.path.join(env.out, M.DB_NAME + ".invocations.db")
    return ACC.read_journal(p) if os.path.exists(p) else {"invocations": 0, "per_day": {}, "unresolved": [],
                                                          "by_outcome": {}}


def ledger_eq(env, label):
    js = journal_state(env)
    return check(atl.ledger_calls(M.TEST, env.ledger) == js["invocations"],
                 "%s: ledger %d == journal %d" % (label, atl.ledger_calls(M.TEST, env.ledger), js["invocations"]))


K46 = None


# ── the tests ──────────────────────────────────────────────────────────────────────────────────────────────────────

def t_plan(stub):
    env = Env(stub)
    try:
        setup(env)
        P.configure_rr()
        k = dict(K46)
        a, b = M.build_plan(k, quiet), M.build_plan(k, quiet)
        check(a["plan_sha"] == b["plan_sha"], "plan: deterministic")
        import hashlib
        import subprocess
        blob, lf16, crlf16, wt = M.script_identity()
        with open(M.__file__, "rb") as f:
            lf = f.read().replace(b"\r\n", b"\n")
        g = subprocess.run(["git", "hash-object", "--stdin"], input=lf, capture_output=True, cwd=HERE)
        check((g.returncode != 0 or g.stdout.decode().strip() == blob) and
              lf16 == hashlib.sha256(lf).hexdigest()[:16] and
              crlf16 == hashlib.sha256(lf.replace(b"\n", b"\r\n")).hexdigest()[:16] and lf16 != crlf16 and
              wt in ("LF", "CRLF"), "identity: blob = git hash-object of the LF rendering; lf16 / crlf16 named kinds")
        sl = a["slots"]
        check(len(sl) == 398 and len({s["sha"] for s in sl}) == 398, "plan: 398 distinct bodies")
        check(all(s["body_bytes"] == a["targets"][s["cls"]] for s in sl), "plan: every body is exactly its target")
        by = {}
        for s in sl:
            by.setdefault(s["step"], []).append(s["cls"])
        check([len(by[x]) for x in ("S1", "S2", "S3", "S4", "S5", "S6")] == [24, 36, 48, 64, 76, 150],
              "plan: 24 / 36 / 48 / 64 / 76 / 150")
        check(by["S1"][:3] == ["q10", "q50", "q90"], "plan: classes cyclic within a step")
        d = json.loads(sl[0]["body"])
        check(list(d) == ["model", "max_tokens", "messages"] and d["model"] == "grok-4-1-fast-non-reasoning" and
              d["max_tokens"] == 8192, "plan: body keys, model, cap; temperature ABSENT")
        s = sl[7]
        item = M.make_item(s["idx"])
        q = M.rref.with_reference(item["stem"], (item["key"], item["options"]["ABCDEFGHIJ".index(item["key"])], None))
        check(s["query"] == q and q in s["user"] and "[Reference solution" in s["user"],
              "plan: the reference rendered through rejudge_reference.with_reference")
        check(a["system_sha"] == K46["system_turn_sha256"], "plan: the system turn is K46's")
        bad = dict(k, system_turn_sha256="0" * 64)
        check(refused(lambda: M.build_plan(bad, quiet)) is not None, "plan: a system turn != K46's REFUSED")
        small = dict(k, q10=3000)
        check(refused(lambda: M.build_plan(small, quiet)) is not None, "plan: a target below the minimal item REFUSED")
        # the content gate
        check(M.content_gate(a, quiet) == 0, "gate: 0 hits on a disjoint corpus")
        M.CORPUS_KEYS = lambda: {"synthetic corpus": {split_side.stem_key(sl[4]["stem"])}}
        check(M.content_gate(a, quiet) == 1, "gate: a planted stem is a hit")
        r = refused(lambda: launch(env, "pilot"))
        check(r is not None and "content gate" in r and not os.path.exists(env.out),
              "gate: a hit REFUSES the launch before any DB / journal")
    finally:
        reset()
        env.cleanup()


def t_dry_run(stub):
    env = Env(stub)
    try:
        setup(env)
        stub.reset()
        r = M.dry_run(env.out, env.ledger, env.root, quiet)
        check(r["calls"] == 0 and not stub.requests, "dry-run: 0 calls (the tripwire and the server)")
        check(not os.path.exists(env.out) and not os.listdir(env.ledger), "dry-run: nothing written")
        txt = "\n".join(LOG[-60:])
        check("TRANSPORT PREFLIGHT: OK" in txt and "key present: True" in txt and KEY not in txt,
              "dry-run: the preflight line (booleans; the key never printed)")
        check("TOTAL REAL-CALL BUDGET: at most 398" in txt and "plan sha256 %s" % r["plan_sha"] in txt,
              "dry-run: the budget and the plan sha printed")
        check(r["plan_sha"] == M.build_plan(K46, quiet)["plan_sha"], "dry-run: the plan sha equals the launch's")
    finally:
        reset()
        env.cleanup()


def happy_behave(idx, att):
    if idx == 2 and att == 1:
        return {"status": 503}
    if idx == 6 and att == 1:
        return {"drop": True}
    return {"delay": 0.08, "headers": {"x-ratelimit-remaining-requests": "499", "x-ms-region": "stub"}}


def t_happy(stub):
    """pilot 12 -> run: all admissible; S6 at N*; accounting equal; concurrency <= N; outcome write-once."""
    env = Env(stub)
    try:
        setup(env)
        stub.reset(happy_behave)
        JOURNAL_WATCH["path"], JOURNAL_WATCH["late"] = os.path.join(env.out, M.DB_NAME + ".invocations.db"), []
        real_pending = ACC.Journal.pending

        def slow_pending(self, *a, **k):     # SELFTEST-ONLY: 30 ms before the insert, so an HTTP attempt that does
            time.sleep(0.03)                  # not wait for its journal row is ALWAYS seen by the witness
            return real_pending(self, *a, **k)
        ACC.Journal.pending = slow_pending
        try:
            r1 = launch(env, "pilot")
        finally:
            ACC.Journal.pending = real_pending
        check(r1["posted"] == 12 and r1.get("pilot", {}).get("pass") is True, "happy: pilot 12 posted and PASS")
        check(os.path.exists(os.path.join(env.out, M.PILOT_NAME)), "happy: the _PILOT file written")
        jp = os.path.join(env.out, M.DB_NAME + ".invocations.db")
        c = sqlite3.connect(jp)
        cap = int(c.execute("SELECT value FROM meta WHERE key='cap'").fetchone()[0])
        c.close()
        check(cap == 400, "cap: the journal's cap trigger is the ceiling 400 (got %d)" % cap)
        ledger_eq(env, "happy after the pilot")
        late = list(JOURNAL_WATCH["late"])
        check(not late, "write-ahead: every HTTP attempt of the pilot left AFTER its slot's journal row was committed"
                        " (%d late: %s)" % (len(late), late[:5]))
        JOURNAL_WATCH["path"] = None        # the witness reads SQLite per request: pilot only (it would add latency)
        r2 = launch(env, "run")
        con = db(env)
        n = con.execute("SELECT COUNT(*) FROM invocation").fetchone()[0]
        steps = [x[0] for x in con.execute("SELECT DISTINCT step FROM invocation ORDER BY idx")]
        s6n = con.execute("SELECT DISTINCT n_inflight FROM invocation WHERE step='S6'").fetchall()
        att = con.execute("SELECT idx, attempt_no, status, error FROM attempt WHERE idx IN (2, 6) ORDER BY idx,"
                          " attempt_no").fetchall()
        rh = con.execute("SELECT rate_headers, header_names FROM attempt WHERE status=200 LIMIT 1").fetchone()
        con.close()
        check(steps[:5] == ["S1", "S2", "S3", "S4", "S5"], "happy: the ramp ran S1-S5 (%s)" % steps)
        check(n == 398 and "S6" in steps and len(s6n) == 1 and s6n[0][0] >= 4,
              "happy: S6 ran at N* >= 4 (%d invocations, S6 N %s)" % (n, s6n))
        js = journal_state(env)
        check(js["invocations"] == 398 and not js["unresolved"], "happy: journal 398, unresolved 0")
        ledger_eq(env, "happy at the end")
        check(len(stub.requests) == 400, "happy: 398 invocations + the 503 retry + the dropped retry = 400 HTTP"
                                         " attempts at the server (%d)" % len(stub.requests))
        check(all(stub.max_active.get(s, 0) <= N for s, N, _n in M.RAMP), "happy: in flight <= N per step %s" %
              stub.max_active)
        check(stub.max_active.get("S4", 0) >= 4, "happy: S4 actually ran concurrently (%s)" % stub.max_active)
        check(att[:2] == [(2, 1, 503, None), (2, 2, 200, None)], "5xx: rr retried the 503 (%s)" % att[:2])
        check(att[2][:2] == (6, 1) and att[2][2] is None and att[2][3] and att[3][2] == 200,
              "timeout class: a dropped connection retried by rr (%s)" % att[2:])
        check(rh[0] and "x-ratelimit-remaining-requests" in rh[0] and "api-key" not in (rh[1] or ""),
              "wire: rate headers recorded; api-key never recorded")
        with open(os.path.join(env.out, M.DB_NAME), "rb") as f:
            check(KEY.encode() not in f.read(), "wire: the key is not in the probe DB")
        check(all(r[3] for r in stub.requests) and not any(r[4] for r in stub.requests),
              "wire: every request carried the key header and no temperature")
        v, txt = M.analyze(env.out, env.ledger, quiet)
        check(os.path.exists(os.path.join(env.out, M.OUTCOME_NAME)), "happy: the outcome of record written")
        check(v["C0"] == "HELD" and v["P2"] == "UNDETERMINED", "happy: C0 HELD, P2 UNDETERMINED (%s)" % v)
        check("NOT READ: accuracy, ties, leakage" in txt and "SUPPORT" in txt, "happy: header and support printed")
        r = refused(lambda: M.analyze(env.out, env.ledger, quiet))
        check(r is not None and "write-once" in r, "happy: a second --analyze REFUSES (write-once)")
        r = refused(lambda: launch(env, "pilot"))
        check(r is not None and "already PASSED" in r, "refusal: a second pilot REFUSED")
        r3 = launch(env, "run")
        check(r3["posted"] == 0, "happy: a relaunch after completion posts nothing")
        ledger_eq(env, "happy after the idle relaunch")
    finally:
        reset()
        env.cleanup()


def t_retry_after(stub):
    """429 + Retry-After (both forms) in S3: recorded; rr retries; S3 inadmissible; the ramp stops; S6 at N* = 2."""
    date = email.utils.formatdate(time.time() + 2, usegmt=True)

    def behave(idx, att):
        if idx in (61, 70) and att == 1:
            return {"status": 429, "headers": {"Retry-After": "1", "x-ratelimit-remaining-requests": "0"},
                    "body": {"error": {"code": "429", "message": "Requests to the ... have exceeded rate limit"}}}
        if idx == 80 and att == 1:
            return {"status": 429, "headers": {"Retry-After": date}}
        return {"delay": 0.03}
    env = Env(stub)
    try:
        setup(env)
        stub.reset(behave)
        launch(env, "pilot")
        launch(env, "run")
        con = db(env)
        a = con.execute("SELECT idx, attempt_no, status, retry_after, retry_after_s, rate_headers, provider_error FROM"
                        " attempt WHERE status=429 ORDER BY idx").fetchall()
        steps = [x[0] for x in con.execute("SELECT DISTINCT step FROM invocation")]
        s6 = con.execute("SELECT DISTINCT n_inflight FROM invocation WHERE step='S6'").fetchall()
        re_ok = con.execute("SELECT COUNT(*) FROM attempt WHERE idx IN (61, 70, 80) AND status=200").fetchone()[0]
        con.close()
        check(len(a) == 3 and a[0][3] == "1" and a[0][4] == 1.0, "Retry-After: delta-seconds recorded (%s)" % a[:1])
        check(a[2][3] == date and a[2][4] is not None and 0 <= a[2][4] <= 3, "Retry-After: HTTP-date recorded")
        check(a[0][5] and "x-ratelimit-remaining-requests" in a[0][5], "429: rate headers recorded")
        check(a[0][6] and '"code": "429"' in a[0][6], "429: the provider's error code recorded")
        check(re_ok == 3, "429: rr retried each 429 to a 200")
        check("S4" not in steps and "S5" not in steps, "stop rule: the ramp stopped at S3 (%s)" % steps)
        check(s6 == [(2,)], "S6 at N* = 2 (%s)" % s6)
        ledger_eq(env, "retry-after")
        v, _ = M.analyze(env.out, env.ledger, quiet, write=False)
        check(v["P2"] == "FAILED", "P2 scored at the first inadmissible step S3 (share 3/51 < 10%%): %s" % v["P2"])
    finally:
        reset()
        env.cleanup()


def t_abort(stub):
    """Every request of S2 gets 429: the within-step abort at 10 HTTP-429 attempts; S2 inadmissible; no S6."""
    def behave(idx, att):
        if 25 <= idx <= 60:
            return {"status": 429, "delay": 0.01}
        return {"delay": 0.01}
    env = Env(stub)
    try:
        setup(env)
        stub.reset(behave)
        launch(env, "pilot")
        launch(env, "run")
        con = db(env)
        n2 = con.execute("SELECT COUNT(*) FROM invocation WHERE step='S2'").fetchone()[0]
        ex = con.execute("SELECT SUM(exhausted_429) FROM invocation WHERE step='S2'").fetchone()[0]
        ev = con.execute("SELECT COUNT(*) FROM step_event WHERE step='S2' AND event='abort'").fetchone()[0]
        later = con.execute("SELECT COUNT(*) FROM invocation WHERE step NOT IN ('S1', 'S2')").fetchone()[0]
        con.close()
        check(ev == 1 and 1 <= n2 <= 3, "abort: S2 aborted with %d reserved (<= N + 1)" % n2)
        check(ex == n2, "abort: every reserved S2 invocation exhausted on 429 and counted (%s)" % ex)
        check(later == 0, "abort: no step after the aborted S2, no S6")
        ledger_eq(env, "abort")
        v, _ = M.analyze(env.out, env.ledger, quiet, write=False)
        check(v["P2"] == "HELD" and "N* = 1" in "\n".join(LOG[-60:]), "abort: P2 HELD (share 100%), N* = 1")
    finally:
        reset()
        env.cleanup()


def t_rollover(stub):
    """The day changes during S2: a clean stop, ledger == journal on day 1; the relaunch resumes S2 on day 2."""
    env = Env(stub)

    def hook(event, launch=None, idx=None, outcome=None):
        if event == "resolved" and idx == 30:
            env.day[0] = DAY2
    try:
        setup(env)
        stub.reset(lambda i, a: {"delay": 0.02})
        launch(env, "pilot")
        M.HOOK = hook
        r = launch(env, "run")
        M.HOOK = None
        js = journal_state(env)
        con = db(env)
        n2a = con.execute("SELECT COUNT(*) FROM invocation WHERE step='S2'").fetchone()[0]
        con.close()
        check(r["stop"] is not None and "DAY ROLLOVER" in r["stop"], "rollover: a clean stop")
        check(set(js["per_day"]) == {DAY1} and n2a <= 9, "rollover: nothing journaled after the flip (S2 %d)" % n2a)
        ledger_eq(env, "rollover day 1")
        check(sum(int(x["calls"]) for x in env.ledger_rows(DAY1)) == js["invocations"], "rollover: all on day 1")
        stub.reset(lambda i, a: {"delay": 0.02, "status": 429} if i == 100 else {"delay": 0.02})
        launch(env, "run")
        js2 = journal_state(env)
        con = db(env)
        n2 = con.execute("SELECT COUNT(*) FROM invocation WHERE step='S2'").fetchone()[0]
        dup = con.execute("SELECT COUNT(*) - COUNT(DISTINCT idx) FROM invocation").fetchone()[0]
        con.close()
        check(DAY2 in js2["per_day"] and n2 == 36 and dup == 0, "rollover: resumed S2 on day 2 (S2 %d)" % n2)
        ledger_eq(env, "rollover day 2")
        # a send-time rollover: no HTTP attempt, NOT_SENT
        stub.reset()
        w = M.Wire(M.Clock())
        t = M.Ticket(5, 1, "x", b"", "s", "u", "S1", 1, None, 0.0)
        res = M._send(w, t, DAY1)
        check(res[0] == "not_sent" and not stub.requests, "rollover at send: NOT_SENT, nothing posted")
    finally:
        reset()
        env.cleanup()


def t_crash(stub):
    """A synthetic crash: a PENDING journal row with no reply and no ledger row; the relaunch reconciles an ORPHAN,
    catches the ledger up, and never re-posts the slot."""
    env = Env(stub)
    try:
        setup(env)
        stub.reset(lambda i, a: {"delay": 0.01, "status": 429} if i == 30 else {"delay": 0.01})
        launch(env, "pilot")
        jp = os.path.join(env.out, M.DB_NAME + ".invocations.db")
        j = ACC.Journal.open(jp, cap=400)
        j.pending("run#9 S1 N=1", "JV2RP-013", 1, "deadbeef", DAY1)     # posted, then the process died
        j.close()
        check(atl.ledger_calls(M.TEST, env.ledger) == 12, "crash: the ledger is one behind (12)")
        stub.reset(lambda i, a: {"delay": 0.01, "status": 429} if i == 30 else {"delay": 0.01})
        launch(env, "run")
        js = journal_state(env)
        con = db(env)
        o = con.execute("SELECT outcome FROM invocation WHERE idx=13").fetchone()
        con.close()
        check(js["by_outcome"].get("ORPHAN") == 1 and o == ("ORPHAN",), "crash: the slot recorded ORPHAN")
        check(not any(r[1] == 13 for r in stub.requests), "crash: slot 13 never re-posted")
        check(any("reconciled after crash" in r["launch"] for r in env.ledger_rows()), "crash: ledger caught up")
        ledger_eq(env, "crash")
    finally:
        reset()
        env.cleanup()


def t_interrupt(stub):
    """KeyboardInterrupt during S3: the abort flag; no HTTP attempt reaches the server after it; in-flight resolved."""
    env = Env(stub)
    st = {"t_abort": None, "flip": False}

    def behave(idx, att):
        if st["flip"]:
            return {"status": 429, "delay": 0.01}
        if 65 <= idx <= 108:
            return {"status": 429, "delay": 0.15}         # in flight at the interrupt: rr would retry them
        return {"delay": 0.15 if 61 <= idx <= 64 else 0.01}

    def hook(event, launch=None, idx=None, outcome=None):
        if event == "resolved" and idx == 64:
            st["flip"] = True
            st["t_abort"] = time.time()
            raise KeyboardInterrupt
    try:
        setup(env)
        stub.reset(behave)
        launch(env, "pilot")
        M.HOOK = hook
        try:
            launch(env, "run")
            check(False, "interrupt: KeyboardInterrupt propagates")
        except KeyboardInterrupt:
            pass
        M.HOOK = None
        time.sleep(0.3)
        after = [r for r in stub.requests if r[0] > st["t_abort"] + 0.001]
        check(not after, "interrupt: no HTTP attempt after the abort flag (%d)" % len(after))
        js = journal_state(env)
        check(not js["unresolved"], "interrupt: every in-flight invocation resolved")
        ledger_eq(env, "interrupt")
        con = db(env)
        ev = con.execute("SELECT COUNT(*) FROM step_event WHERE event='interrupted'").fetchone()[0]
        con.close()
        check(ev == 1, "interrupt: the interrupted event recorded")
    finally:
        reset()
        env.cleanup()


def t_pilot_fail(stub):
    def behave(idx, att):
        if idx == 3:
            return {"content": "not json at all"}
        if idx == 4:
            return {"status": 400, "body": {"error": {"code": "content_filter", "message": "content_filter"}}}
        return {"delay": 0.01}
    env = Env(stub)
    try:
        setup(env)
        stub.reset(behave)
        r = refused(lambda: launch(env, "pilot"))
        check(r is not None and "pilot-12 guard FAILED" in r, "pilot: unparsed + content_filter FAIL the guard")
        check(any(".pilot_guard_FAILED." in f for f in os.listdir(env.out)), "pilot: the FAILED file written")
        con = db(env)
        v = dict(con.execute("SELECT idx, vote FROM invocation WHERE idx IN (3, 4)").fetchall())
        con.close()
        check(v == {3: "INVALID", 4: "CONTENT_FILTER"}, "pilot: votes classified (%s)" % v)
        r = refused(lambda: launch(env, "run"))
        check(r is not None and "no PASSED pilot guard" in r, "refusal: the run REFUSED without a PASS")
        r = refused(lambda: launch(env, "pilot"))
        check(r is not None and "FAILED file exists" in r, "refusal: a pilot after a FAIL REFUSED (VOID)")
        ledger_eq(env, "pilot fail")
    finally:
        reset()
        env.cleanup()


def t_refusals(stub):
    """Each refusal leaves NO probe DB, journal or ledger row (they come before any write)."""
    def nothing(env):
        return not os.path.exists(env.out) and not [f for f in os.listdir(env.ledger) if f.startswith("day_calls")]
    cases = []
    env = Env(stub)
    try:
        setup(env, OPTIMIZE=1)
        r = refused(lambda: launch(env, "pilot"))
        cases.append(check(r is not None and "-O" in r and nothing(env), "refusal: python -O"))
        setup(env)
        if sys.flags.optimize:
            M.OPTIMIZE = None
            r = refused(lambda: launch(env, "pilot"))
            check(r is not None and "-O" in r and nothing(env), "refusal: the REAL -O flag (this run is under -O)")
        else:
            M.OPTIMIZE = None
            check(M.optimize_level() == 0, "the real flag: 0 under plain python")
        M.OPTIMIZE = 0
        with open(os.path.join(env.ledger, "day_calls_%s.json" % DAY1), "x", encoding="utf-8") as f:
            json.dump([{"test": M.JB_TEST, "launch": "arm=G x", "calls": 5, "ts": "t"}], f)
        r = refused(lambda: launch(env, "pilot"))
        check(r is not None and "X2" in r and not os.path.exists(env.out), "refusal: X2 (a JudgeBench row today)")
        os.remove(os.path.join(env.ledger, "day_calls_%s.json" % DAY1))
        M.PROCESS_LIST = lambda: [[4242, "python.exe", "python tools/analysis/judgebench_side.py --arm both"]]
        r = refused(lambda: launch(env, "pilot"))
        check(r is not None and "X1" in r and nothing(env), "refusal: X1 (a foreign posting script)")
        M.PROCESS_LIST = lambda: [[4243, "python.exe", "python tools/analysis/foo.py --selftest"]]
        check(M.x1_check("t", quiet)["ok"], "X1: a --selftest process is admitted")
        M.PROCESS_LIST = lambda: []
        M.K46_SOURCE = dict(K46, unresolved=2)
        r = refused(lambda: launch(env, "pilot"))
        check(r is not None and "K46 journal" in r and nothing(env), "refusal: the K46 journal unresolved")
        M.K46_SOURCE = K46
        r = refused(lambda: launch(env, "pilot", expect="0" * 64))
        check(r is not None and "plan sha" in r and nothing(env), "refusal: --expect-plan-sha mismatch")
        r = refused(lambda: launch(env, "run"))
        check(r is not None and "no PASSED pilot guard" in r and nothing(env), "refusal: run before the pilot")
        M.CEILING_OVERRIDE = 5
        r = refused(lambda: launch(env, "pilot"))
        check(r is not None and "ceiling" in r and nothing(env), "refusal: the ceiling (own + planned > ceiling),"
                                                                   " before any write")
        M.CEILING_OVERRIDE = None
        with open(os.path.join(env.ledger, "day_calls_%s.json" % DAY1), "x", encoding="utf-8") as f:
            json.dump([{"test": "OTHER", "launch": "x", "calls": 13700, "ts": "t"}], f)
        r = refused(lambda: launch(env, "pilot"))
        check(r is not None and "(iii)" in r, "refusal: the day cap (iii) as registered (day + 400 > 14,000)")
        os.remove(os.path.join(env.ledger, "day_calls_%s.json" % DAY1))
        shutil.rmtree(env.out, ignore_errors=True)
    finally:
        reset()
        env.cleanup()
    # the transport preflight: an empty key, an http endpoint -> refused before any file
    for label, ep, key in (("an empty key", None, ""), ("an http endpoint", "http://127.0.0.1:1", KEY)):
        env = Env(stub, endpoint=ep, key=key)
        try:
            setup(env)
            r = refused(lambda: launch(env, "pilot"))
            check(r is not None and ("TRANSPORT" in r or "PREFLIGHT" in r) and nothing(env),
                  "refusal: preflight with %s, before any journal / DB / ledger (%s)" % (label, (r or "")[:80]))
        finally:
            reset()
            env.cleanup()
    # the live guard: a non-loopback endpoint under a selftest setting
    env = Env(stub, endpoint="https://example.invalid")
    try:
        setup(env)
        r = refused(lambda: launch(env, "pilot"))
        check(r is not None and "LIVE GUARD" in r and nothing(env), "refusal: the live guard at the launch")
        calls = {"n": 0}

        def sentinel(*a, **k):
            calls["n"] += 1
            raise RuntimeError("must not be reached")
        M.REAL_URLOPEN = sentinel
        w = M.Wire(M.Clock())
        w.install()
        try:
            w.begin(1, "x")
            req = urllib.request.Request("https://example.invalid/x", data=b"body", method="POST")
            try:
                urllib.request.urlopen(req)
                ok = False
            except M.WireRefused as e:
                ok = "LIVE GUARD" in str(e)
        finally:
            w.uninstall()
        check(ok and calls["n"] == 0, "wire: a non-loopback request under a selftest setting never leaves")
    finally:
        reset()
        env.cleanup()
    # body fidelity at the wire
    stub.reset()
    w = M.Wire(M.Clock())
    M.REAL_URLOPEN = rewrite
    w.install()
    try:
        w.begin(1, "0" * 64)
        req = urllib.request.Request("http://127.0.0.1:%d/x" % stub.port, data=b"other bytes", method="POST")
        try:
            urllib.request.urlopen(req)
            ok = False
        except M.WireRefused:
            ok = True
        except Exception:  # noqa: BLE001
            ok = False
    finally:
        w.uninstall()
        reset()
    check(ok and not stub.requests, "wire: a body that is not the slot's REFUSED before it left")


def t_meta(stub):
    env = Env(stub)
    try:
        setup(env)
        stub.reset(lambda i, a: {"delay": 0.01})
        launch(env, "pilot")
        M.K46_SOURCE = dict(K46, q50=5400)
        r = refused(lambda: launch(env, "run"))
        check(r is not None and "pinned at the first launch" in r, "refusal: a changed plan against the pinned meta")
        M.K46_SOURCE = K46
        jp = os.path.join(env.out, M.DB_NAME + ".invocations.db")
        j = ACC.Journal.open(jp, cap=400)
        n0 = j.state()["invocations"]
        try:
            for _ in range(400 - n0 + 1):
                j.pending("cap-test", "JV2RP-999", 1, "x", DAY1)
                j.resolve(j.state()["invocations"], "RAISED", "cap test")
            capped = False
        except SystemExit as e:
            capped = "hard cap of 400" in str(e)
        finally:
            j.close()
        check(capped and ACC.read_journal(jp)["invocations"] == 400, "cap: the journal trigger refuses the 401st")
    finally:
        reset()
        env.cleanup()


# ── the decision rules and every print branch ─────────────────────────────────────────────────────────────────────

def st(step, N, rate, share=0.0, exh=0, p95=0.1, med=3.5, n=24, http=None, aborted=False, n429=None):
    http = http if http is not None else n
    if n429 is not None:                    # an exact 429 count (the share follows from it)
        share = n429 / http
    k = int(round(share * http)) if n429 is None else n429
    return {"step": step, "N": N, "Ns": [N], "n": n, "http": http, "n429": k,
            "share": share, "cp95": M.cp_upper(k, http), "exhausted": exh, "wall_s": 60.0,
            "rate": rate, "lat_median": med, "lat_p95": p95, "lat_max": p95, "tokens_median": 250,
            "user_bytes_median": 2634, "unparsed": 0, "returned": n, "aborted": aborted, "orphans": 0, "not_sent": 0,
            "lengths": 0, "content_filter": 0}


V_OK = {"V1": True, "V2": True, "V3": True, "V4": True, "V5_bytes": True, "V5_tokens": True, "user_bytes_median": 2634,
        "k46_user_q50": 2634, "tokens_median": 250, "rate_header_names": ["x-ratelimit-remaining-requests"]}


def t_branches(stub):
    k46 = {"median_completion_tokens": 254}
    seen = set()

    def run(stats, v, label):
        d = M.decide(stats)
        lines, verd = M.score(stats, d, v, k46)
        for x in lines:
            seen.add(x.split(":")[0] + ":" + x.split(":")[1][:9] if ":" in x else x)
        return d, lines, verd
    # A: the 09-16 regime: every step admissible, S6 admissible, falsifier fires, C2 build
    A = {"S1": st("S1", 1, 17, p95=4.6), "S2": st("S2", 2, 34, n=36, p95=4.7), "S3": st("S3", 4, 68, n=48, p95=4.8),
         "S4": st("S4", 8, 130, n=64, p95=5.0), "S5": st("S5", 12, 190, n=76, p95=5.2),
         "S6": st("S6", 12, 185, n=150, p95=5.3)}
    d, L, v = run(A, V_OK, "A")
    check(d["nstar_final"] == 12 and v["C2"] == "build" and v["FALSIFIER"] == "FIRED" and v["P1"] == "FAILED" and
          v["P2"] == "UNDETERMINED" and v["C0"] == "HELD" and v["P3"] == "HELD", "branches A: %s %s" % (d["nstar_final"],
                                                                                                      v))
    check(any("FALSIFIER: FIRED" in x for x in L) and any("P4 (readout, not scored): rate headers returned: yes" in x
                                                          for x in L), "branches A: falsifier and P4 yes printed")
    # B: the 09-24 regime: S3 inadmissible (429s), N* = 2, S6 inadmissible -> dropped to 1; P1 HELD; P2 HELD
    B = {"S1": st("S1", 1, 15, p95=4.0), "S2": st("S2", 2, 25, n=36, p95=4.5),
         "S3": st("S3", 4, 20, share=0.25, exh=2, n=48, http=60, p95=30.0),
         "S6": st("S6", 2, 22, share=0.05, n=150, http=160, p95=5.0)}
    d, L, v = run(B, dict(V_OK, V5_bytes=False, rate_header_names=[]), "B")
    check(d["nstar"] == 2 and d["nstar_final"] == 1 and v["P1"] == "HELD" and v["P2"] == "HELD" and
          v["C2"] == "deferred" and v["V5"] == "FAILED" and v["FALSIFIER"] == "NOT FIRED",
          "branches B: %s / %s %s" % (d["nstar"], d["nstar_final"], v))
    check(any("qualified under C1, else 1 (RC5 (a)): N = 1" in x for x in L) and any("SIZE CAVEAT" in x for x in L) and
          any("rate headers returned: no" in x for x in L) and any("V5 REALISM: FAILED" in x for x in L),
          "branches B: S6 drop, size caveat, P4 no, V5 FAILED printed")
    # C: stopped at S2 (p95), S3 not posted: P1 (ii) NOT OBSERVED; C3 NOT OBSERVED; P2 FAILED (share 0); C0 FAILED; P3
    C = {"S1": st("S1", 1, 15, p95=4.0, med=5.0, exh=0), "S2": st("S2", 2, 28, n=36, p95=9.0)}
    d, L, v = run(C, dict(V_OK, V1=False, V4=False), "C")
    check(v["P1"] == "HELD" and v["P2"] == "FAILED" and v["C0"] == "FAILED" and v["P3"] == "FAILED",
          "branches C: %s" % v)
    check(any("(ii) NOT OBSERVED" in x for x in L) and any("S3 NOT POSTED" in x for x in L) and
          any("C0 VALIDITY: FAILED (V1, V4)" in x for x in L), "branches C: NOT OBSERVED lines and C0 FAILED printed")
    # D: C1's 1.3x rule: S2 buys < 1.3x, S3 buys >= 1.3x over S2 -> N* = 4 (literal: the largest N qualifying)
    D = {"S1": st("S1", 1, 15, p95=4.0), "S2": st("S2", 2, 18, n=36, p95=4.1), "S3": st("S3", 4, 30, n=48, p95=4.2),
         "S4": st("S4", 8, 33, n=64, p95=4.3), "S5": st("S5", 12, 34, n=76, p95=4.4)}
    d, L, v = run(D, V_OK, "D")
    check(d["nstar"] == 4 and d["need_s6"] and d["knee"] is not None and d["knee"][0] == "S1",
          "branches D: C1's 1.3x rule (N* %s, knee %s)" % (d["nstar"], d["knee"]))
    check(v["P1"] == "FAILED" and v["FALSIFIER"] == "NOT FIRED", "branches D: P1 FAILED on (i) with (ii) held")
    # E [INVERTED 2026-09-25, A2 as revised (d10e029 RC1)]: S1 is exempt from (c); p95 10.7 s no longer stops the ramp
    E = {"S1": st("S1", 1, 12, p95=10.7)}
    d, L, v = run(E, V_OK, "E")
    check(d["stopped_at"] is None and d["nstar_final"] == 1 and d["ramp"][0][2] is True and v["P2"] == "UNDETERMINED",
          "branches E (inverted): S1 at p95 10.7 s is admissible (S1 exempt, no 10 s cap)")
    # F (kept as built, 7c6c588): the p95 bar uses p95 (not the median): 7.0 > 1.5 x 4.0 = 6.0 is inadmissible
    F = {"S1": st("S1", 1, 15, p95=4.0, med=3.0), "S2": st("S2", 2, 30, n=36, p95=7.0, med=3.1)}
    d, L, v = run(F, V_OK, "F")
    check(d["stopped_at"] == "S2", "branches F: (c) p95 7.0 > 1.5 x 4.0 = 6.0 is inadmissible")
    # F boundary (7c6c588): 6.0 = 1.5 x 4.0 admissible; 6.01 inadmissible
    F["S2"] = st("S2", 2, 30, n=36, p95=6.0, med=3.1)
    d, L, v = run(F, V_OK, "F6")
    check(d["stopped_at"] is None and d["ramp"][1][2] is True, "branches F: S2 p95 6.0 = 1.5 x 4.0 is admissible")
    F["S2"] = st("S2", 2, 30, n=36, p95=6.01, med=3.1)
    d, L, v = run(F, V_OK, "F601")
    check(d["stopped_at"] == "S2", "branches F: S2 p95 6.01 > 1.5 x 4.0 is inadmissible")
    G = {"S1": st("S1", 1, 15, p95=4.0), "S2": st("S2", 2, 30, n=36, p95=4.0, aborted=True)}
    d, L, v = run(G, V_OK, "G")
    check(d["stopped_at"] == "S2", "branches G: an aborted step is inadmissible")
    check(M.p95(list(range(1, 21))) == 19 and M.p95(list(range(1, 25))) == 23,
          "p95 is the nearest-rank p95 (19 of 1..20; 23 of 1..24)")
    check(abs(M.cp_upper(0, 48) - (1 - 0.05 ** (1 / 48))) < 1e-9 and abs(M.cp_upper(0, 24) - 0.1173) < 1e-3,
          "CP upper bound at 0 of n (the registration's 11.7% at 24)")


# ── the runner ─────────────────────────────────────────────────────────────────────────────────────────────────────

def t_amendments(stub):
    """The pre-data amendments of d10e029 as ruled: A2 revised (1.5 x p95(S1), S1 exempt, no cap, S6 not exempt), A3
    (<= 2% OR at most one 429; the falsifier literal), A4 (the qualifier and the DESCRIPTIVE label), RC5 (a)."""
    s1 = st("S1", 1, 15, p95=4.0)
    ok = lambda x, p=4.0: M.admissible(x, p)[0]          # noqa: E731
    # RC1 / A2
    check(ok(st("S1", 1, 15, p95=30.0), 30.0), "A2: S1 at p95 30 s is admissible (S1 exempt from (c))")
    check(M.c_exempt(st("S1", 1, 15)) and not M.c_exempt(st("S6", 2, 15)) and not M.c_exempt(st("S2", 2, 15)),
          "A2: S1 exempt from (c); S2 and S6 not")
    check(M.admissible(st("S1", 1, 15, p95=None), None)[0], "A2: S1 with no latency is exempt from (c) (admissible)")
    check(not ok(st("S6", 2, 25, n=150, p95=6.5)), "A2: S6 is subject to (c) (6.5 > 1.5 x 4.0)")
    check(ok(st("S6", 2, 25, n=150, p95=5.9)), "A2: S6 at 5.9 <= 6.0 admissible")
    check(not M.admissible(st("S2", 2, 30, n=36, p95=1.0), None)[0], "A2: a non-S1 step with p95(S1) None is"
                                                                        " inadmissible")
    check(ok(st("S3", 4, 60, n=48, p95=5.6)), "A2: S3 at 1.4 x p95(S1) admissible")
    check(not ok(st("S3", 4, 60, n=48, p95=6.4)), "A2: S3 at 1.6 x p95(S1) inadmissible")
    check(ok(st("S4", 8, 100, n=64, p95=12.0), 9.0), "A2: no absolute 10 s cap (S4 p95 12 s <= 1.5 x 9 s)")
    # RC2 / A3
    check(ok(st("S3", 4, 30, n=48, http=49, n429=1)), "A3: 1 x 429 in S3 (49 attempts, 2.04%) admissible")
    check(not ok(st("S3", 4, 30, n=48, http=50, n429=2)), "A3: 2 x 429 in S3 (50 attempts, 4%) inadmissible")
    check(ok(st("S4", 8, 60, n=64, http=65, n429=1)), "A3: 1 x 429 in S4 (65 attempts) admissible")
    check(ok(st("S6", 2, 30, n=150, http=153, n429=3)), "A3: 3 x 429 in 153 (1.96%) admissible (share <= 2%)")
    check(not ok(st("S3", 4, 30, n=48, http=51, n429=3)), "A3: the 3 / 51 case stays inadmissible")
    s3 = st("S3", 4, 55, n=48, http=49, n429=1, p95=4.4)
    d = M.decide({"S1": s1, "S2": st("S2", 2, 28, n=36, p95=4.2), "S3": s3})
    _L, v = M.score({"S1": s1, "S3": s3}, d, V_OK, {"median_completion_tokens": 254})
    check(d["ramp"][2][2] is True and v["FALSIFIER"] == "NOT FIRED",
          "A3: S3 at >= 50/min with 1 x 429 (2.04%) is admissible and the falsifier is NOT FIRED (literal <= 2%)")
    s3b = st("S3", 4, 55, n=48, p95=5.6)
    _L, v = M.score({"S1": s1, "S3": s3b}, d, V_OK, {"median_completion_tokens": 254})
    check(v["FALSIFIER"] == "FIRED", "falsifier: S3 >= 50/min, 0 429, p95 1.4 x p95(S1) FIRES (factor 1.5)")
    s3e = st("S3", 4, 55, n=48, p95=6.0)
    _L, v = M.score({"S1": s1, "S3": s3e}, d, V_OK, {"median_completion_tokens": 254})
    check(ok(s3e) and v["FALSIFIER"] == "FIRED", "7c6c588: S3 at 1.5 x p95(S1) is admissible and, at >= 50/min with"
                                                 " 0 x 429, the falsifier FIRES")
    s3c = st("S3", 4, 55, n=48, p95=6.4)
    _L, v = M.score({"S1": s1, "S3": s3c}, d, V_OK, {"median_completion_tokens": 254})
    check(v["FALSIFIER"] == "NOT FIRED", "falsifier: p95 1.6 x p95(S1) does not fire")
    check(M.P95_REL_FACTOR == 1.5 and M.FALSIFIER_P95_FACTOR == 1.5 and M.FALSIFIER_429_SHARE == 0.02 and
          M.ADMIT_429_MAX_COUNT == 1, "constants: admissibility and falsifier factors are separate, both 1.5 as ruled")
    # RC5 (a): branch D extended with an inadmissible S6 -> N* = 1 (S2 did not qualify under C1)
    D = {"S1": st("S1", 1, 15, p95=4.0), "S2": st("S2", 2, 18, n=36, p95=4.1), "S3": st("S3", 4, 30, n=48, p95=4.2),
         "S4": st("S4", 8, 33, n=64, p95=4.3), "S5": st("S5", 12, 34, n=76, p95=4.4),
         "S6": st("S6", 4, 20, n=150, http=160, n429=10, p95=4.5)}
    d = M.decide(D)
    check(d["nstar"] == 4 and d["s6"] is not None and not d["s6"][0] and d["nstar_final"] == 1 and d["G"] == 1.0,
          "RC5 (a): branch D with an inadmissible S6 drops to N* = 1 (got %s)" % d["nstar_final"])
    # RC3 / A4: the qualifier and the label in the outcome text (a complete synthetic probe DB)
    tmp = tempfile.mkdtemp(prefix="jv2rp_a4_")
    try:
        outd = os.path.join(tmp, "out")
        os.makedirs(outd)
        con = sqlite3.connect(os.path.join(outd, M.DB_NAME))
        con.executescript(M.DDL)
        meta = {"test": M.TEST, "script_blob": "x", "judge": "j", "provider": "azure", "cap": "8192",
                "temperature": "omitted", "seed": M.SEED, "system_sha": "s", "targets": json.dumps(
                    {"q10": 4581, "q50": 5369, "q90": 6805}), "empty_body_bytes": "2735",
                "k46_median_completion_tokens": "254", "ceiling": "400"}
        con.executemany("INSERT INTO meta VALUES (?,?)", list(meta.items()))
        con.execute("INSERT INTO launch VALUES (1, 'run#1', 'run', ?, 0, 'x', 0)", (DAY1,))
        t = 1000.0
        for i in range(1, 25):
            con.execute("INSERT INTO invocation VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
                i, "S1", 1, i, 1, "run#1 S1 N=1", t, t + 4.0, "RETURNED", 200, None, 0, 1, 0, "stop", 250, None,
                "FIRST", None, None, "sha%d" % i, 5369, 2634, "q50"))
            con.execute("INSERT INTO attempt VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                        (i, 1, t, t + 4.0, 200, None, None, None, None, "[]", None))
            t += 4.0
        con.execute("INSERT INTO invocation VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
            25, "S2", 2, 25, 1, "run#1 S2 N=2", t, t + 30.0, "RAISED", 429, "HTTPError", 1, 6, 6, None, None, None,
            None, None, None, "sha25", 5369, 2634, "q50"))
        con.execute("INSERT INTO step_event (step, launch_k, event, n_inflight, ts, note) VALUES ('S2', 1, 'abort', 2,"
                    " 0, 'x')")
        con.execute("INSERT INTO x1 (launch_k, where_, ok, x2_ok, detail, ts) VALUES (1, 'w', 1, 1, '{}', 0)")
        con.commit()
        con.close()
        led = os.path.join(tmp, "led")
        os.makedirs(led)
        _v, txt = M.analyze(outd, led, quiet, write=False)
        check(QUAL in txt and txt.count("DESCRIPTIVE (A4): quota vs capacity is reported, not decided") == 2 and
              "ADMISSIBILITY OF RECORD" in txt, "A4: the verbatim qualifier and the DESCRIPTIVE (A4) labels printed")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


QUAL = ("N* is measured under rr's retry schedule (6 attempts, Retry-After ignored); every HTTP 429 counts for"
        " admissibility; it does not transfer as-is to a pool that honours Retry-After (A4)")


TESTS = [t_plan, t_dry_run, t_happy, t_retry_after, t_abort, t_rollover, t_crash, t_interrupt, t_pilot_fail,
         t_refusals, t_meta, t_branches, t_amendments]
MUTANTS = {
    "gate_off": [t_plan], "stop_rule_off": [t_retry_after, t_branches], "abort_off": [t_abort],
    "journal_after_post": [t_happy], "ledger_skip": [t_happy], "rollover_off": [t_rollover], "cap_off": [t_happy],
    "retry_after_ignored": [t_retry_after], "body_unchecked": [t_refusals], "inflight_over": [t_happy],
    "p95_is_median": [t_branches], "preflight_after_journal": [t_refusals], "optimize_ok": [t_refusals],
    "x2_off": [t_refusals], "x1_off": [t_refusals], "pilot_guard_off": [t_pilot_fail], "c1_no_gain": [t_branches],
    "s6_no_drop": [t_branches], "abort_flag_ignored": [t_interrupt], "outcome_overwrite": [t_happy],
    "meta_unchecked": [t_meta],
    # [2026-09-25] the pre-data amendments of d10e029 as ruled (RC1, RC2, RC5 (a))
    "p95_cap_restored": [t_amendments], "s1_not_exempt": [t_amendments, t_branches], "s6_exempt": [t_amendments],
    "p95_factor_2": [t_amendments, t_branches], "a_or_dropped": [t_amendments], "a_or_as_and": [t_amendments],
    "a_count_bound_2": [t_amendments], "falsifier_reads_or": [t_amendments], "s6_drop_previous": [t_amendments],
}


def run_tests(tests, stub):
    """accepted_tests_ledger.guard / append print to stdout directly: captured here (kept in LOG)."""
    import contextlib
    import io
    before, exc = len(FAILS), []
    for t in tests:
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                t(stub)
        except BaseException as e:  # noqa: BLE001
            if isinstance(e, KeyboardInterrupt) and t is not t_interrupt:
                raise
            FAILS.append("%s raised %s: %s" % (t.__name__, type(e).__name__, str(e)[:300]))
            exc.append(t.__name__)
        finally:
            LOG.extend(buf.getvalue().splitlines())
            reset()
    return len(FAILS) - before, exc


def main():
    global K46
    t0 = time.time()
    print("JV2-RATE-PROBE selftest (python optimisation level %d); stub server on 127.0.0.1; 0 real calls" %
          sys.flags.optimize)
    P.configure_rr()
    K46 = k46_source()
    stub = Stub()
    try:
        nfail, exc = run_tests(TESTS, stub)
        print("CHECKS: %d run, %d failed%s" % (CHECKS["n"], nfail, (" (tests raising: %s)" % exc) if exc else ""))
        for f in FAILS:
            print("  FAILED: %s" % f)
        base_fails = len(FAILS)
        killed, survived = [], []
        for name, tests in MUTANTS.items():
            del FAILS[:]
            M.MUTANT = None
            orig = {}

            def with_mutant(t, name=name):
                def f(stub):
                    M.MUTANT = name
                    try:
                        return t(stub)
                    finally:
                        M.MUTANT = None
                f.__name__ = t.__name__
                return f
            n, exc = run_tests([with_mutant(t) for t in tests], stub)
            (killed if n else survived).append((name, n, exc))
            del orig
        print("MUTANTS: %d run, %d killed, %d survived" % (len(MUTANTS), len(killed), len(survived)))
        for name, n, exc in killed:
            print("  KILLED   %-24s %d failing check(s)%s" % (name, n, (" [by exception in %s]" % exc) if exc else
                                                             " [by check]"))
        for name, n, exc in survived:
            print("  SURVIVED %-24s" % name)
        ok = base_fails == 0 and not survived
        print("SELFTEST %s in %.1f s" % ("PASS" if ok else "FAIL", time.time() - t0))
        return 0 if ok else 1
    finally:
        stub.close()
        reset()


if __name__ == "__main__":
    sys.exit(main())
