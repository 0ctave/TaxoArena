"""judge_v2.pool_selftest: the concurrency selftest of JV2-PARALLEL-POSTING (registered at bf9d80b, docs/judge_v2_program.md
L19096-L19239, section 2.5; criteria EC2 and EC3 of 2.7, read with the registrar's R2). SYNTHETIC ONLY: no DB of record
is opened; no judge call is posted (a pure fake call_full, or rejudge_reasoning.call_judge_full REAL against a LOCALHOST
stub server with rr's sleep patched to a fast recorder); every file lives under tempfile.gettempdir() and is removed.

    python tools/analysis/judge_v2/pool_selftest.py
    python -O tools/analysis/judge_v2/pool_selftest.py

No assert is used (every check is an explicit comparison, printed PASS / FAIL and counted), so -O runs the same branches.

FIXTURE: judge_v2.selftest.build_views (the E-J fixture: data_v2's fixture DBs through ingest -> split -> gen / eval
view), the requests (EVAL MC variant, model pair) that load and pre-scan clean (14 matches = 28 slots, below), loaded ONCE per
run through loader.load_matches; the accounting is archv2_pilot.accounting (journal, TwoPhaseCall, wrap_call, the day
ledger in a temp directory) driven by launch_like(), which repeats pilot.launch's accounting sequence (Journal.open ->
reconcile -> label -> begin_launch -> writer create / open -> wrap_call or TwoPhaseCall -> writer.run -> finally the
ledger append -> the ledger == journal check).

INVARIANT -> its MUTANTS (R2: a mutant is KILLED only if it is killed in EVERY registered trial of its harness; a mutant
killed in some trials and not in others counts as SURVIVING):
  I1  write-ahead: the stub, on receipt, finds a PENDING unresolved journal row with the body's sha (its own read-only
      connection). MUTANT pool send_before_reserve.
  I2  one verdict per slot, no in-launch resubmission: MUTANT pool rereserve_errored (an errored slot re-reserved in the
      launch); MUTANT writer stale_pending (the relaunch reserves from the previous launch's pending snapshot).
  I3  ledger == journal: a KeyboardInterrupt with N tickets in flight. MUTANT accounting posts_at_completion.
  I4  rollover: the clock flips between a reservation and its send, at EVERY reservation index; the kill criterion is
      "0 stub requests received after the flip". MUTANT accounting rollover_off (the check only at the launch's
      start); MUTANT accounting rollover_send_off (the reserve-time check only).
  I5  preflight first: executed by archv2_pilot/selftest.py --part pool (pilot.launch is the driver that owns the
      preflight): MUTANT pilot preflight_after_pool; MUTANT pilot preflight_skipped_pooled. Run here as a subprocess.
  I6  ceilings: cap 50, N 8, 60 pending, 1,000 stress trials: exactly 50 journal rows, <= 50 requests received, and a
      direct reservation beyond N refused by the launch-bound trigger. MUTANT accounting cap_in_workers (a python
      counter in the workers instead of the trigger); MUTANT accounting unresolved_trigger_off.
  I7  429: the stub serves 429s with and without Retry-After. An invocation exhausted (6 HTTP attempts, the pool's retries: RC2)
      is an error attempt row, never a
      verdict, re-posted next launch; the cool-down pause is max(Retry-After, 3 s); the bound halves; a RATE STOP after
      the third exhaustion at bound 1. MUTANTS writer classify_429_invalid, pool resend_exhausted (retries beyond 6),
      pool no_halving, pool gate_ignores_retry_after.
  I8  order invariance (E-8): N in {1, 2, 4, 8, 16} x 20 seeded latency permutations, the store PROJECTION (every column
      of schedule / attempt / verdict and every run_meta key, except created_at, latency_ms, session_id), the drain order
      and the journal projection equal to the N = 1 run (EC3: 100 of 100 cells). MUTANT pool bind_shift.
  I9  single writer: a worker touching the store's or the journal's connection raises ProgrammingError. MUTANT pool
      worker_resolves (a worker writes the journal's resolution).
  I10 body fidelity: MUTANT accounting body_prev_reserve (killed at the pool's reserve assert); MUTANT accounting
      body_prev_send (killed at the wire counter: the request never leaves).
  I11 rr globals frozen (E-7): after a pooled run PROVIDER, JUDGE_MODEL, MAX_TOKENS, TEMPERATURE (None), the endpoint and
      the key are unchanged. MUTANT pool worker_sets_temperature.
  I12 crash: a subprocess os._exit at 50 seeded points with N = 8; after the relaunch: verdicts per slot <= 1, re-posts
      <= N, orphans disclosed, ledger == journal after reconcile. MUTANT accounting orphans_returned.
  I13 identity: a store created by the leg-A writer (writer_blob 6db4ab32) is REFUSED on relaunch ("the recipe identity
      differs ... writer_blob"). MUTANT writer_blob dropped from IDENTITY_KEYS.
  Also: _pool_fields builds the verdict fields of _poster_factory's poster KEY FOR KEY (AST-compared, latency_ms's
  fallback excepted); workers > 1 with a plain callable, workers > MAX_INFLIGHT, workers > 1 on a journal created at
  workers 1: REFUSED before any post; the workers-1 path prints exactly the registered [POOL] line.
  [ADDED 2026-09-25: the coordinator's rate-control HARD REQUIREMENTS (items 1-6), relayed during the build; not in the
  registration's 13 invariants, checked the same way (each mutant killed in every trial):]
  RC1 Retry-After honoured in both forms (delta-seconds, HTTP-date), floored at 3 s; without it full-jitter exponential
      backoff (ceilings 2, 4, 8, 16, 32, 60 s); ONE 429 pauses the WHOLE pool. MUTANTS retry_after_date_ignored (unit and
      end to end), backoff_no_growth, gate_per_worker.
  RC2 rr's internal retry loop NEUTRALISED (rr never sleeps; the pool retries the same invocation, <= 6 HTTP attempts);
      every HTTP attempt journaled (http_attempts == stub receipts) and counted against the journal's cap (a launch stops
      at the HTTP-ATTEMPT CAP). MUTANTS rr_retries_live, http_cap_off.
  RC3 max_rpm: one global token bucket over all workers (<= max_rpm attempts in any 60 s window). MUTANT bucket_per_worker.
  RC4 adaptive concurrency: halve on a 429 burst / a timeout (10 s hold), +1 per clean 60 s up to the workers.
      MUTANTS no_halving, no_raise, raise_unbounded.
  RC5 the per-request timeout (a held response times out and is retried) and the circuit breaker (K consecutive timeouts
      / 429s: a clean stop; the relaunch resumes). MUTANTS no_request_timeout, breaker_off (unit and end to end).
  The fixture as built today loads 14 clean matches (28 slots) of the 18 judgeable variants x 2 pairs (the rest are the
  E-J fixture's deliberate leak / MIXED / no-reference rows); the small set is the first 6 (12 slots).
[ADDED 2026-09-25 on the READY review d32fa75 (NOT READY; F1-F4), insertion only; the lines above stand and are read
with this bracket:
  RC1 is now measured CLIENT-SIDE: 0 grants (RateControl.attempt_times) inside (the instant the pause was SET,
      pause_until) (RateControl.pause_windows); the 429 goes to the FOURTH slot in key order so the main thread has
      reservations to make during the pause. The stub-receipt window with its 30 ms margin is retired.
  RC1b NEW: a 429 while >= 3 workers are QUEUED at a BINDING max_rpm (6 at scale 0.01, 8 workers, Retry-After 60 s): 0
      grants inside the pause, every grant gap >= the interval, the witness waiting-at-the-429 >= 3. MUTANTS
      gate_before_bucket_only (the pause read by wait_gate only) and bucket_by_schedule (pre-assigned slots).
  RC3 is now STRICT on the client's grant instants: every gap >= 60 / max_rpm (scaled) and <= max_rpm grants in any
      window; the stub receipts keep their + 1.
  I3b NEW (F3): Ctrl-C with 4 attempts on the wire, the stub serving 429: 0 stub receipts after the abort instant, 4
      invocations unresolved, ledger == journal, the wire uninstalled by the last worker. MUTANT abort_ignored.
  F4 NEW: the live guard's branches by execution with urllib's urlopen a recorder (zero network): a live launch
      REFUSED under TIME_SCALE 0.001 and under a MUTANT at 1.0 (0 invocations, 0 requests), ADMITTED at 1.0 with no
      switch; the wire backstop refuses a non-loopback request at 0.5 and admits it at 1.0 and a loopback one at 0.5.
  The stub's receipt times are time.perf_counter (the rate control's clock).]
"""
import _thread
import ast
import email.utils
import hashlib
import http.server
import inspect
import json
import os
import pathlib
import random
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import textwrap
import threading
import time
import urllib.request
from datetime import datetime, timedelta, timezone

if __name__ == "__main__" and not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    __package__ = "judge_v2"
    import judge_v2  # noqa: F401

from ._base import dv2verdicts, git_blob_lf, rr, HERE  # noqa: E402
from . import loader as LD  # noqa: E402
from . import payload as P  # noqa: E402
from . import pool as POOL  # noqa: E402
from . import selftest as S  # noqa: E402
from . import writer as W  # noqa: E402
from archv2_pilot import accounting as ACC  # noqa: E402

TEST = "ARCH-V2-PILOT-K46"          # the only day-capped test accounting knows (temp ledgers only)
DAY = "2026-09-25"
NEXT_DAY = "2026-09-26"
LEG_A_WRITER_BLOB = "6db4ab3207a24aa61a1d4ea43ca6f2da2c68e547"     # judge_v2/writer.py on main (bf9d80b's parent line)
E8_NS = (1, 2, 4, 8, 16)
E8_SEEDS = 20
I6_TRIALS = 1000
I12_POINTS = 50
PAIRS = (("mA", "mB"), ("mA", "gpt-4o-2024-08-06"))
QUIET = lambda s: None  # noqa: E731


def _out_default(s):
    print(s, flush=True)


class Checks:
    def __init__(self, out):
        self.out, self.n, self.fails = out, 0, []
        self.mutants = []           # (invariant, name, trials, killed_trials)

    def check(self, name, ok, detail=""):
        self.n += 1
        ok = bool(ok)
        self.out("[POOL-SELFTEST] %s %s%s" % ("PASS" if ok else "FAIL", name, (" | " + str(detail)[:300]) if detail else ""))
        if not ok:
            self.fails.append(name)
        return ok

    def mutant(self, inv, name, killed_per_trial):
        """R2: KILLED iff killed in every trial."""
        k = [bool(x) for x in killed_per_trial]
        ok = bool(k) and all(k)
        self.mutants.append((inv, name, len(k), sum(k)))
        return self.check("%s MUTANT %s: killed in %d of %d trial(s) -> %s" % (inv, name, sum(k), len(k),
                                                                             "KILLED" if ok else "SURVIVED"), ok)


class _Mut:
    """Set one module MUTANT for a block; always reset."""

    def __init__(self, mod, value, attr="MUTANT"):
        self.mod, self.value, self.attr = mod, value, attr

    def __enter__(self):
        setattr(self.mod, self.attr, self.value)

    def __exit__(self, *exc):
        setattr(self.mod, self.attr, None)
        return False


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def _payload_sha(system, user):
    return _sha(rr.payload_bytes(system, user))


def ro_connect(path):
    """A read-only connection to a scratch DB of this selftest (a verdict store, a journal): never a corpus or a view."""
    return sqlite3.connect(pathlib.Path(os.path.abspath(path)).as_uri() + "?mode=ro", uri=True, timeout=10)


# ── the fixture ─────────────────────────────────────────────────────────────────────────────────────────────────────

def clean_requests(ev_path, rub, tmp):
    """(EVAL MC variant, model pair) requests that load alone and pre-scan clean (the fixture's leak rows excluded)."""
    judgeable, _sent = S.eval_variants(ev_path)
    reqs = []
    for v in judgeable:
        for a, b in PAIRS:
            mid = "pp-%s-%s-%s" % (v[2].split()[2], a, b)
            r = {"match_id": mid, "variant_id": v[0], "model_a": a, "model_b": b, "batch_id": "b1"}
            try:
                ld = LD.load_matches([r], ev_path, out=QUIET)
                w = W.JudgeWriter.create(os.path.join(tmp, "probe_%d.db" % len(reqs)), "POOL-SELFTEST", "probe", ld, rub,
                                         S._ctx())
                w.prescan(out=QUIET)
                w.close()
            except SystemExit:
                continue
            reqs.append(r)
    return reqs


def slot_of_loaded(loaded, rub):
    so = {}
    for mid, inp in loaded.specs.items():
        p1, p2 = P.build_dual(inp, rub)
        so.setdefault(p1.sha256, []).append((mid, 1))
        so.setdefault(p2.sha256, []).append((mid, 2))
    return so


def fake_reply(sha):
    """A pure function of sha256(body): the verdict, a truncation, a refusal or an error, by the sha's first bytes."""
    b = int(sha[:2], 16)
    rid = "fake-" + sha[:12]
    if b % 11 == 0:
        return ("err", 503)
    if b % 13 == 0:
        return ("ok", ('{"critique_a": "trunc', "azure:grok-4-1-fast-non-reasoning", 8192, 0.2, "length",
                       {"_response_id": rid, "_finish_reason": "length"}))
    if b % 17 == 0:
        return ("ok", ("", "azure:refusal", 0, 0.1, "content_filter",
                       {"_refusal": '{"error": {"code": "content_filter"}}', "_response_id": rid,
                        "_finish_reason": "content_filter"}))
    winner = ("Model A", "Model B", "TIE")[b % 3]
    return ("ok", (json.dumps({"critique_a": "a" + sha[2:6], "critique_b": "b", "comparison": "c", "winner": winner,
                               "confidence": 0.7}), "azure:grok-4-1-fast-non-reasoning", 100 + b, 0.3, "stop",
                   {"_response_id": rid}))


class HTTPErr(Exception):
    def __init__(self, code):
        super().__init__("HTTP %d" % code)
        self.code = code


class Fake:
    """call_full's shape; the reply is fake_reply(sha256(body)); a seeded latency per sha (the permutation); the
    received shas logged in arrival order. hook(sha, n): SELFTEST-ONLY side effects at receipt."""

    def __init__(self, seed=0, max_ms=3.0, log_path=None, hook=None, errors=True):
        self.seed, self.max_ms, self.log_path, self.hook, self.errors = seed, max_ms, log_path, hook, errors
        self.lock = threading.Lock()
        self.received = []

    def __call__(self, system, user):
        sha = _sha(rr.payload_bytes(system, user))
        with self.lock:
            self.received.append(sha)
            n = len(self.received)
            if self.log_path:
                with open(self.log_path, "a", encoding="utf-8") as f:
                    f.write(sha + "\n")
                    f.flush()
                    os.fsync(f.fileno())
        if self.hook:
            self.hook(sha, n)
        lat = random.Random("%s|%s" % (self.seed, sha)).uniform(0, self.max_ms) / 1000.0
        if lat:
            time.sleep(lat)
        kind, v = fake_reply(sha)
        if kind == "err" and self.errors:
            raise HTTPErr(v)
        if kind == "err":
            kind, v = fake_reply("ff" + sha[2:])
        return v


# ── the stub server (localhost; the wire) ────────────────────────────────────────────────────────────────────────────

class Stub:
    def __init__(self):
        self.lock = threading.Lock()
        self.received = []          # (sha, flipped, write_ahead_ok)
        self.received_t = []        # (monotonic receipt time, sha, status served)
        self.script = {}            # sha -> list of statuses served in order (then 200)
        self.default_script = None  # a list served to every sha without its own
        self.retry_after = {}       # sha -> Retry-After header value (str, or a callable returning one) or None
        self.default_retry_after = None
        self.delay = {}             # sha -> list of per-attempt delays (s) before the response
        self.flipped = lambda: False
        self.journal_path = None
        stub = self

        class H(http.server.BaseHTTPRequestHandler):
            def log_message(self, *a):
                return

            def do_POST(self):
                n = int(self.headers.get("Content-Length") or 0)
                body = self.rfile.read(n)
                sha = _sha(body)
                t_rx = time.perf_counter()     # [F2] the rate control's clock (judge_v2.pool RateControl._now)
                wa = stub._write_ahead(sha) if stub.journal_path else None
                with stub.lock:
                    stub.received.append((sha, bool(stub.flipped()), wa))
                    lst = stub.script.get(sha)
                    if lst is None and stub.default_script is not None:
                        lst = stub.script[sha] = list(stub.default_script)
                    status = lst.pop(0) if lst else 200
                    stub.received_t.append((t_rx, sha, status))
                    dl = stub.delay.get(sha)
                    d = dl.pop(0) if dl else 0.0
                if d:
                    time.sleep(d)
                if status != 200:
                    self.send_response(status)
                    ra = stub.retry_after.get(sha, stub.default_retry_after)
                    if callable(ra):
                        ra = ra()
                    if ra is not None:
                        self.send_header("Retry-After", ra)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(b'{"error": {"code": "rate_limited"}}')
                    return
                _k, v = fake_reply("aa" + sha[2:])       # always a 200 verdict from the stub
                content, _prov, ctoks, _lat, finish, _msg = v
                out = json.dumps({"id": "stub-" + sha[:12], "model": "grok-4-1-fast-non-reasoning",
                                  "choices": [{"message": {"role": "assistant", "content": content},
                                               "finish_reason": finish}],
                                  "usage": {"completion_tokens": ctoks}}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(out)))
                self.end_headers()
                self.wfile.write(out)

        class Srv(http.server.ThreadingHTTPServer):
            def handle_error(self, request, client_address):
                return          # a client that timed out closed its socket: expected in RC5

        self.srv = Srv(("127.0.0.1", 0), H)
        self.srv.daemon_threads = True
        self.port = self.srv.server_address[1]
        self.th = threading.Thread(target=self.srv.serve_forever, daemon=True)

    def _write_ahead(self, sha):
        """I1: a PENDING, unresolved journal row with this body's sha (own read-only connection)."""
        for _ in range(50):
            try:
                c = ro_connect(self.journal_path)
                try:
                    r = c.execute("SELECT COUNT(*) FROM invocation i WHERE i.payload_sha256 = ? AND NOT EXISTS (SELECT 1"
                                  " FROM resolution r WHERE r.seq = i.seq)", (sha,)).fetchone()[0]
                finally:
                    c.close()
                return r >= 1
            except sqlite3.OperationalError:
                time.sleep(0.01)
        return False

    def __enter__(self):
        self.th.start()
        self.saved = (rr.AZURE_ENDPOINT, rr.AZURE_KEY, rr.time)
        rr.AZURE_ENDPOINT = "http://127.0.0.1:%d/models/chat/completions" % self.port
        rr.AZURE_KEY = "stub-key-not-a-secret"
        self.sleeps = []
        stub = self

        class FastTime:
            time = staticmethod(time.time)

            @staticmethod
            def sleep(s):
                stub.sleeps.append(s)

        rr.time = FastTime
        return self

    def __exit__(self, *exc):
        rr.AZURE_ENDPOINT, rr.AZURE_KEY, rr.time = self.saved
        self.srv.shutdown()
        self.srv.server_close()
        return False


# ── the launcher (pilot.launch's accounting sequence) ────────────────────────────────────────────────────────────────

class Run:
    """One store directory: the store, its journal, a ledger directory."""

    def __init__(self, base, name):
        self.dir = os.path.join(base, name)
        os.makedirs(self.dir)
        self.store = os.path.join(self.dir, "store.db")
        self.journal = self.store + ".invocations.db"
        self.ledger = os.path.join(self.dir, "ledger")
        os.makedirs(self.ledger)


def launch_like(run, loaded, rub, call_full, workers, out=QUIET, day=DAY, clock=None, cap=ACC.AUTHOR_HARD_CAP,
                transport_cls=None, n_draws=1, run_id="pool", writer_hook=None, fast_io=False, rate=None):
    """Returns {"posted", "label"}; raises what the launch raises (after its finally). POOLED = workers > 1 or rate."""
    pooled = workers > 1 or rate is not None
    creating = not os.path.exists(run.journal)
    journal = ACC.Journal.open(run.journal, cap=cap, create=creating,
                               max_inflight=POOL.MAX_INFLIGHT if (pooled and creating) else None)
    if fast_io:
        fast(journal.conn)
    posts = {"n": 0}
    writer, label = None, None
    try:
        ACC.reconcile(TEST, journal, run.ledger, out)
        js = journal.state()
        label = "launch#%d %s" % (js["launches"] + 1, run_id) + (" w=%d" % workers if pooled else "")
        journal.begin_launch(label, workers, pooled)
        if os.path.exists(run.store):
            writer = W.JudgeWriter.open(run.store, loaded, rub, S._ctx())
        else:
            writer = W.JudgeWriter.create(run.store, "POOL-SELFTEST (scratch)", run_id, loaded, rub, S._ctx(),
                                          n_draws=n_draws)
        if fast_io:
            fast(writer.store.conn)
        if writer_hook:
            writer_hook(writer)
        so = slot_of_loaded(loaded, rub)
        clk = clock or (lambda: day)
        if not pooled:
            call = ACC.wrap_call(call_full, journal, so, posts, label, day, _payload_sha, clock=clk)
            writer.run(call, out=out)
        else:
            tc = transport_cls or ACC.TwoPhaseCall
            call = tc(call_full, journal, so, posts, label, day, _payload_sha, clock=clk)
            writer.run(call, out=out, workers=workers, rate=rate)
    finally:
        if writer is not None:
            writer.close()
        if posts["n"]:
            ACC.append(TEST, label, posts["n"], run.ledger, day=day)
        jn = journal.state()["invocations"]
        journal.close()
    ACC.check_equal(TEST, jn, run.ledger, "at the end of the launch")
    return {"posted": posts["n"], "label": label, "writer": writer}


def ledger_calls(run):
    import accepted_tests_ledger as atl
    return atl.ledger_calls(TEST, run.ledger)


def journal_rows(path):
    """-> ([(seq, launch, match_id, order, sha)], {seq: (outcome, note, http_attempts, http_429)})."""
    c = ro_connect(path)
    try:
        inv = c.execute("SELECT seq, launch, match_id, presentation_order, payload_sha256 FROM invocation ORDER BY seq"
                        ).fetchall()
        cols = "http_attempts, http_429" if _has_col(c, "resolution", "http_attempts") else "NULL, NULL"
        res = {r[0]: tuple(r[1:]) for r in c.execute("SELECT seq, outcome, note, %s FROM resolution" % cols)}
    finally:
        c.close()
    return inv, res


def _has_col(c, table, col):
    return any(r[1] == col for r in c.execute("PRAGMA table_info(%s)" % table))


def projection(path):
    """E-8: every column of schedule / attempt / verdict and every run_meta key, except created_at, latency_ms,
    session_id; rows in key order."""
    c = ro_connect(path)
    try:
        out = {}
        for t in ("schedule", "attempt", "verdict"):
            cols = [r[1] for r in c.execute("PRAGMA table_info(%s)" % t) if r[1] not in ("created_at", "latency_ms",
                                                                                          "session_id")]
            out[t] = c.execute("SELECT %s FROM %s ORDER BY run_id, match_id, presentation_order, draw_index%s" % (
                ", ".join(cols), t, ", attempt_no" if t == "attempt" else "")).fetchall()
        out["run_meta"] = c.execute("SELECT key, value FROM run_meta ORDER BY key").fetchall()
    finally:
        c.close()
    return out


def pending_keys(path):
    c = ro_connect(path)
    try:
        return c.execute("SELECT match_id, presentation_order FROM schedule s WHERE NOT EXISTS (SELECT 1 FROM verdict v"
                         " WHERE v.run_id = s.run_id AND v.match_id = s.match_id AND v.presentation_order ="
                         " s.presentation_order AND v.draw_index = s.draw_index) ORDER BY 1, 2").fetchall()
    finally:
        c.close()


def count(path, sql, args=()):
    c = ro_connect(path)
    try:
        return c.execute(sql, args).fetchone()[0]
    finally:
        c.close()


# ── checks ───────────────────────────────────────────────────────────────────────────────────────────────────────────

def c0_units(ck, tmp, loaded, rub):
    """The dispatch, the refusals before any post, the [POOL] line, the field-for-field identity."""
    r = Run(tmp, "c0")
    lines = []
    fk = Fake(errors=False)
    launch_like(r, loaded, rub, fk, 1, out=lines.append)
    ck.check("C0 workers 1 prints EXACTLY the registered line %r once, before the pre-scan line" % POOL.POOL_LINE_SEQUENTIAL,
             lines.count(POOL.POOL_LINE_SEQUENTIAL) == 1 and lines.index(POOL.POOL_LINE_SEQUENTIAL) <
             min(i for i, x in enumerate(lines) if x.startswith("[LEAK-SCAN]") or "pre-call" in x), lines[:3])
    ck.check("C0 workers 1: no other [POOL] / [RATE] line", [x for x in lines if x.startswith(("[POOL]", "[RATE]"))] ==
             [POOL.POOL_LINE_SEQUENTIAL])
    ck.check("C0 workers 1 creates the journal with TODAY'S DDL (no max_inflight row, no launch_bound table)",
             count(r.journal, "SELECT COUNT(*) FROM meta WHERE key='max_inflight'") == 0 and
             count(r.journal, "SELECT COUNT(*) FROM sqlite_master WHERE name='launch_bound'") == 0 and
             _ddl_text(r.journal) == _ddl_text_expected_v1())
    r2 = Run(tmp, "c0b")
    ck.check("C0 refused: workers 4 with a plain callable (no two-phase transport), 0 posts", _refused_no_post(
        lambda: _plain_pooled(r2, loaded, rub, fk), ("TwoPhase",)))
    r3 = Run(tmp, "c0c")
    ck.check("C0 refused: workers 17 > MAX_INFLIGHT 16, before any post", _refused_no_post(
        lambda: launch_like(r3, loaded, rub, Fake(), 17), ("max_inflight", "16")) and
        not os.path.exists(r3.store))
    # workers > 1 on a journal created at workers 1: refused at begin_launch, before any post
    r4 = Run(tmp, "c0d")
    ACC.Journal.open(r4.journal, create=True).close()
    fk4 = Fake()
    ck.check("C0 refused: workers 4 on a journal created at workers 1 (max_inflight 1), before any post", _refused_no_post(
        lambda: launch_like(r4, loaded, rub, fk4, 4), ("max_inflight 1",)) and not fk4.received and
        count(r4.journal, "SELECT COUNT(*) FROM invocation") == 0)
    ck.check("C0 refused: a journal max_inflight outside [2, 16]", _refused(lambda: ACC.Journal.open(
        os.path.join(tmp, "j17.db"), create=True, max_inflight=17), ("outside",)))
    # the verdict fields: _pool_fields == _poster_factory's poster, key for key
    ok, why = fields_ast_equal()
    ck.check("C0 _pool_fields builds _poster_factory's verdict fields key for key (AST; latency_ms's fallback excepted)",
             ok, why)
    # a pooled run completes and equals the sequential run
    r5 = Run(tmp, "c0e")
    lines5 = []
    launch_like(r5, loaded, rub, Fake(errors=False), 4, out=lines5.append)
    ck.check("C0 workers 4 completes; its projection equals the workers-1 run's", projection(r5.store) ==
             projection(r.store) and not pending_keys(r5.store))
    ck.check("C0 workers 4 prints the pipelined [POOL] line with the journal's max_inflight 16 and the pool summary",
             any(x.startswith("[POOL] workers 4 (pipelined path; journal max_inflight 16") for x in lines5) and
             any(x.startswith("[POOL] workers 4: reserved") for x in lines5), [x for x in lines5 if "[POOL]" in x])
    ck.check("C0 workers 4: the journal is v2 (max_inflight 16, launch_bound w=4, http columns)",
             count(r5.journal, "SELECT value FROM meta WHERE key='max_inflight'") == "16" and
             count(r5.journal, "SELECT workers FROM launch_bound") == 4 and
             count(r5.journal, "SELECT COUNT(*) FROM resolution WHERE http_attempts = 0 AND http_429 = 0") ==
             count(r5.journal, "SELECT COUNT(*) FROM resolution") == 28)   # a fake transport: no urlopen, 0 HTTP attempts
    return r


def _ddl_text(path):
    c = ro_connect(path)
    try:
        return sorted(r[0] for r in c.execute("SELECT sql FROM sqlite_master WHERE sql IS NOT NULL"))
    finally:
        c.close()


def _ddl_text_expected_v1():
    c = sqlite3.connect(":memory:")
    try:
        c.executescript(ACC._ddl(ACC.AUTHOR_HARD_CAP))
        return sorted(r[0] for r in c.execute("SELECT sql FROM sqlite_master WHERE sql IS NOT NULL"))
    finally:
        c.close()


def _plain_pooled(run, loaded, rub, fk):
    w = W.JudgeWriter.create(run.store, "POOL-SELFTEST (scratch)", "plain", loaded, rub, S._ctx())
    try:
        w.run(fk, out=QUIET, workers=4)
    finally:
        w.close()


def _refused(fn, must=()):
    try:
        fn()
    except SystemExit as e:
        return all(m in str(e) for m in must)
    return False


def _refused_no_post(fn, must=()):
    return _refused(fn, must)


def fields_ast_equal():
    src = textwrap.dedent(inspect.getsource(W.JudgeWriter._poster_factory))
    src2 = textwrap.dedent(inspect.getsource(W.JudgeWriter._pool_fields))

    def fields_dict(s):
        for n in ast.walk(ast.parse(s)):
            if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "fields" for t in n.targets) and \
                    isinstance(n.value, ast.Dict):
                return {ast.literal_eval(k): ast.dump(v) for k, v in zip(n.value.keys, n.value.values)}
        return None
    a, b = fields_dict(src), fields_dict(src2)
    if a is None or b is None:
        return False, "no fields dict found"
    if set(a) != set(b):
        return False, "keys differ: %s" % sorted(set(a) ^ set(b))
    diff = sorted(k for k in a if a[k] != b[k])
    return diff == ["latency_ms"], "differing values: %s" % diff


# I1 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def i1(ck, tmp, loaded, rub):
    def one(tag):
        r = Run(tmp, "i1_" + tag)
        with Stub() as st:
            st.journal_path = r.journal
            try:
                launch_like(r, loaded, rub, rr.call_judge_full, 4)
            except SystemExit:
                pass
        return st.received
    rec = one("ok")
    ck.check("I1 write-ahead: on receipt the stub finds a PENDING unresolved journal row with the body's sha, for every"
             " request (%d)" % len(rec), rec and all(wa for _s, _f, wa in rec), sum(1 for x in rec if not x[2]))
    with _Mut(POOL, "send_before_reserve"):
        recm = one("mut")
    ck.mutant("I1", "send_before_reserve", [bool(recm) and any(not wa for _s, _f, wa in recm)])


# I2 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def i2(ck, tmp, loaded, rub):
    def one(tag):
        r = Run(tmp, "i2_" + tag)
        fk = Fake(seed=3)
        refused = False
        try:
            launch_like(r, loaded, rub, fk, 4)
        except SystemExit:
            refused = True
        inv, _res = journal_rows(r.journal)
        per = {}
        for _s, launch, mid, order, _sha_ in inv:
            per[(launch, mid, order)] = per.get((launch, mid, order), 0) + 1
        pend1 = pending_keys(r.store)
        n1 = len(fk.received)
        refused2 = False
        try:
            launch_like(r, loaded, rub, Fake(seed=3, errors=False), 4)
        except SystemExit:
            refused2 = True
        return r, per, pend1, n1, refused, refused2
    r, per, pend1, n1, ref1, ref2 = one("ok")
    ck.check("I2 the fixture has errored slots (fake 503 by sha): %d pending after launch 1" % len(pend1), len(pend1) >= 1)
    ck.check("I2 no slot is reserved twice within a launch (journal rows per (launch, match, order) <= 1)",
             max(per.values()) == 1 and not ref1, max(per.values()))
    inv2, _ = journal_rows(r.journal)
    l2 = [x for x in inv2 if x[1].startswith("launch#2")]
    ck.check("I2 the relaunch posts EXACTLY the pending (errored) slots, once each; the run is then complete",
             sorted((m, o) for _s, _l, m, o, _h in l2) == sorted(pend1) and not ref2 and not pending_keys(r.store),
             (len(l2), len(pend1)))
    ck.check("I2 at most one verdict per slot (the store's key)", count(r.store, "SELECT MAX(c) FROM (SELECT COUNT(*) c FROM"
                                                                               " verdict GROUP BY match_id,"
                                                                               " presentation_order, draw_index)") == 1)
    with _Mut(POOL, "rereserve_errored"):
        _r, per_m, _p, _n, _a, _b = one("m1")
    ck.mutant("I2", "rereserve_errored", [max(per_m.values()) > 1])
    with _Mut(W, "stale_pending"):
        _r, _per, pend_m, _n, ref1m, ref2m = one("m2")
    ck.mutant("I2", "stale_pending", [ref2m or bool(pending_keys(_r.store))])


# I3 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def i3(ck, tmp, loaded, rub, N=4):
    def one(tag):
        r = Run(tmp, "i3_" + tag)
        release = threading.Event()
        started = {"n": 0}
        lock = threading.Lock()

        def hook(sha, n):
            with lock:
                started["n"] += 1
                k = started["n"]
            if k == N:
                _thread.interrupt_main()
            release.wait(10)
        fk = Fake(hook=hook, errors=False)
        interrupted = False
        try:
            launch_like(r, loaded, rub, fk, N)
        except KeyboardInterrupt:
            interrupted = True
        finally:
            release.set()
        time.sleep(0.2)
        js = ACC.read_journal(r.journal)
        return r, interrupted, js, ledger_calls(r)
    r, intr, js, led = one("ok")
    ck.check("I3 a KeyboardInterrupt with %d tickets in flight: the launch is interrupted, %d invocations unresolved" % (
        N, N), intr and len(js["unresolved"]) == N and js["invocations"] == N, (intr, js["unresolved"], js["invocations"]))
    ck.check("I3 ledger == journal right after the interrupt (the finally ledgers posts counted at reservation)",
             led == js["invocations"], (led, js["invocations"]))
    lines = []
    launch_like(r, loaded, rub, Fake(errors=False), N, out=lines.append)
    ck.check("I3 the relaunch discloses the %d ORPHANs and completes; ledger == journal" % N,
             sum("an ORPHAN, counted and disclosed" in x for x in lines) == N and not pending_keys(r.store) and
             ledger_calls(r) == ACC.read_journal(r.journal)["invocations"])
    with _Mut(ACC, "posts_at_completion"):
        _r, intr_m, js_m, led_m = one("mut")
    ck.mutant("I3", "posts_at_completion", [intr_m and led_m != js_m["invocations"]])


def i3b(ck, tmp, small, rub, N=4):
    """[F3, READY review d32fa75] Ctrl-C with N attempts on the wire and the stub scripted to 429: after the abort flag
    no HTTP attempt leaves (0 stub receipts after RateControl.aborted_at), the in-flight tickets stay unresolved (ORPHANs
    at the relaunch), ledger == journal, and the wire wrapper is uninstalled by the last worker out. rr.call_judge_full
    REAL against the localhost stub; every first attempt is held 0.5 s, then served 429 (Retry-After 0)."""
    def one(tag):
        r = Run(tmp, "i3b_" + tag)
        wr = {}
        with Stub() as st:
            st.default_script = [429, 200]
            st.default_retry_after = "0"
            st.delay = {h: [0.5] for h in slot_of_loaded(small, rub)}

            def watcher():
                t_end = time.perf_counter() + 10
                while time.perf_counter() < t_end:
                    with st.lock:
                        n = len(st.received)
                    if n >= N:
                        _thread.interrupt_main()
                        return
                    time.sleep(0.005)
            th = threading.Thread(target=watcher, daemon=True)
            interrupted = False
            try:
                th.start()
                launch_like(r, small, rub, rr.call_judge_full, N, writer_hook=lambda w: wr.setdefault("w", w))
            except KeyboardInterrupt:
                interrupted = True
            th.join(5)
            pool = getattr(wr.get("w"), "last_pool", None)
            if pool is not None:
                pool.ex.shutdown(wait=True)             # the workers finish their held attempt (<= 0.5 s)
            time.sleep(0.2)
            with st.lock:
                rec = list(st.received_t)
        ab = pool.rate.aborted_at if pool is not None else None
        after = None if ab is None else sum(1 for t, _s, _st in rec if t > ab)
        restored = not isinstance(getattr(urllib.request.urlopen, "__self__", None), POOL.WireCounter)
        js = ACC.read_journal(r.journal)
        return interrupted, ab, after, len(rec), restored, js, ledger_calls(r)
    intr, ab, after, nrec, restored, js, led = one("ok")
    ck.check("I3b Ctrl-C with %d attempts on the wire (stub: 429 after 0.5 s): interrupted, the abort flag set, 0 stub"
             " receipts after it (%s of %d), %d invocations unresolved, ledger == journal, the wire uninstalled by the last"
             " worker" % (N, after, nrec, N), intr and ab is not None and after == 0 and nrec == N and
             len(js["unresolved"]) == N and js["invocations"] == N and led == N and restored,
             (intr, ab is not None, after, nrec, js["unresolved"], led, restored))
    with _Mut(POOL, "abort_ignored"):
        intr_m, _ab, after_m, _n, _res, _js, _l = one("mut")
    ck.mutant("I3b", "abort_ignored (the workers' retry loop keeps posting after Ctrl-C)",
              [intr_m and after_m is not None and after_m > 0])


class _LiveT(POOL.TwoPhase):
    """[F4] a transport that names rr.call_judge_full (the live signature) and is never driven."""
    max_inflight = 4
    call_full = staticmethod(rr.call_judge_full)


class _Resp:
    headers, status = {}, 200

    def read(self, *a):
        return b"{}"

    def close(self):
        return None


def f4(ck, tmp, small, rub):
    """[F4, READY review d32fa75] The live guard, BOTH branches executed, zero network: (1) a live launch (rr.call_judge_full
    to a non-loopback endpoint) under the selftest's TIME_SCALE is REFUSED before any reservation; (2) the same with
    TIME_SCALE 1.0 and one MUTANT set is REFUSED naming it; (3) with TIME_SCALE 1.0 and no switch the pool is ADMITTED
    (constructed with no slot, never driven); (4) the wire backstop: a non-loopback request under TIME_SCALE 0.5 is
    refused BEFORE the (recording) urlopen, admitted at 1.0, and a loopback one is admitted at 0.5. urllib's urlopen is a
    recorder throughout (a request reaching it is counted, never sent)."""
    saved = (rr.AZURE_ENDPOINT, rr.AZURE_KEY, POOL.TIME_SCALE, urllib.request.urlopen)
    rec = []

    def recorder(req, *a, **k):
        rec.append(getattr(req, "full_url", req))
        return _Resp()
    try:
        urllib.request.urlopen = recorder
        rr.AZURE_ENDPOINT = "https://jv2-live-guard.invalid/models/chat/completions"
        rr.AZURE_KEY = "not-a-key"
        # (1) TIME_SCALE as the selftest sets it (0.001)
        r1 = Run(tmp, "f4_scale")
        err, _p, l1 = _pooled(r1, small, rub, 4)
        g1 = [x for x in l1 if x.startswith("[RATE] live guard:")]
        ck.check("F4 (1) a live launch under TIME_SCALE %r is REFUSED before any reservation (0 invocations, 0 requests"
                 " reached urlopen), the guard line printed with its inputs" % POOL.TIME_SCALE,
                 err is not None and "LIVE GUARD" in err and "TIME_SCALE" in err and len(g1) == 1 and
                 "LIVE, REFUSED" in g1[0] and "non-loopback" in g1[0] and ACC.read_journal(r1.journal)["invocations"] == 0
                 and rec == [], (err or "")[:200])
        # (2) TIME_SCALE 1.0, one MUTANT
        POOL.TIME_SCALE = 1.0
        r2 = Run(tmp, "f4_mutant")
        with _Mut(W, "classify_429_invalid"):
            err2, _p2, _l2 = _pooled(r2, small, rub, 4)
        ck.check("F4 (2) a live launch at TIME_SCALE 1.0 with judge_v2.writer.MUTANT set is REFUSED naming the switch (0"
                 " invocations, 0 requests)", err2 is not None and "LIVE GUARD" in err2 and "judge_v2.writer.MUTANT" in err2
                 and "TIME_SCALE=" not in err2 and ACC.read_journal(r2.journal)["invocations"] == 0 and rec == [],
                 (err2 or "")[:200])
        # (3) TIME_SCALE 1.0, no switch: ADMITTED (never driven)
        l3 = []
        sw = POOL.selftest_switches()
        pool = POOL.PostingPool(_LiveT(), [], 2, None, None, out=l3.append)
        pool.close()
        g3 = [x for x in l3 if x.startswith("[RATE] live guard:")]
        ck.check("F4 (3) a live pool at TIME_SCALE 1.0 with no switch set is ADMITTED (constructed, never driven); the"
                 " [RATE] config line prints time_scale 1.0", sw == [] and len(g3) == 1 and "LIVE, ADMITTED" in g3[0] and
                 any(x.startswith("[RATE] config:") and "time_scale 1.0" in x for x in l3) and rec == [], (sw, l3))
        # (4) the wire backstop
        body = b'{"probe": "f4"}'

        def wire_try(url, scale):
            POOL.TIME_SCALE = scale
            w = POOL.WireCounter(POOL.RateControl(1, POOL.RateConfig(max_rpm=6000), time_scale=1.0),
                                 POOL.RateConfig(max_rpm=6000))
            w.real = recorder
            w.begin(_sha(body))
            n0 = len(rec)
            try:
                w.urlopen(urllib.request.Request(url, data=body), timeout=5)
                res = "admitted"
            except POOL.WireRefused as e:
                res = "refused" if "LIVE GUARD" in str(e) else "other: %s" % e
            finally:
                w.end()
            return res, len(rec) - n0
        wa = wire_try("https://jv2-live-guard.invalid/x", 0.5)
        wb = wire_try("https://jv2-live-guard.invalid/x", 1.0)
        wc = wire_try("http://127.0.0.1:9/x", 0.5)
        ck.check("F4 (4) the wire backstop: non-loopback at TIME_SCALE 0.5 REFUSED before urlopen (0 reached), admitted"
                 " at 1.0 (1 reached the recorder), loopback at 0.5 admitted (1 reached)",
                 wa == ("refused", 0) and wb == ("admitted", 1) and wc == ("admitted", 1), (wa, wb, wc))
    finally:
        rr.AZURE_ENDPOINT, rr.AZURE_KEY, POOL.TIME_SCALE, urllib.request.urlopen = saved


# I4 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────

class FlipClock:
    """The date flips right after the k-th reservation returns (between that reservation and its send), once every
    send that is inside the transport has been received (a send that starts after the flip sees the new date)."""

    def __init__(self):
        self.lock = threading.Lock()
        self.cond = threading.Condition(self.lock)
        self.active = 0
        self.flipped = False

    def __call__(self):
        return NEXT_DAY if self.flipped else DAY

    def flip(self):
        with self.cond:
            while self.active:
                self.cond.wait(0.05)
            self.flipped = True


def flipping_transport(clock, k):
    class T(ACC.TwoPhaseCall):
        n = 0

        def reserve(self, system, user):
            t = super().reserve(system, user)
            T.n += 1
            if T.n == k:
                clock.flip()
            return t

        def send(self, ticket):
            with clock.cond:
                clock.active += 1
            try:
                return super().send(ticket)
            finally:
                with clock.cond:
                    clock.active -= 1
                    clock.cond.notify_all()
    return T


def i4(ck, tmp, small, rub, N=4):
    M = 2 * len(small.specs)

    def one(tag, k):
        r = Run(tmp, "i4_%s_%d" % (tag, k))
        clock = FlipClock()
        with Stub() as st:
            st.flipped = lambda: clock.flipped
            stopped = False
            try:
                launch_like(r, small, rub, rr.call_judge_full, N, clock=clock, transport_cls=flipping_transport(clock, k))
            except SystemExit as e:
                stopped = "DAY ROLLOVER" in str(e)
        after = sum(1 for _s, f, _w in st.received if f)
        return r, after, stopped
    res = [one("ok", k) for k in range(1, M + 1)]
    ck.check("I4 every flip point 1..%d: 0 stub requests received after the flip" % M, all(a == 0 for _r, a, _s in res),
             [a for _r, a, _s in res])
    ck.check("I4 every flip point: the launch stops with DAY ROLLOVER (a clean stop), ledger == journal",
             all(s and ledger_calls(r) == ACC.read_journal(r.journal)["invocations"] for r, _a, s in res))
    ns = [count(r.journal, "SELECT COUNT(*) FROM resolution WHERE note = ?", (POOL.NOT_SENT,)) for r, _a, _s in res]
    ck.check("I4 the reserved-but-unsent tickets are journaled RAISED \"%s\" (counted), at least 1 per flip point" %
             POOL.NOT_SENT, all(n >= 1 for n in ns), ns)
    r0 = res[0][0]
    try:
        with Stub():
            launch_like(r0, small, rub, rr.call_judge_full, N, day=NEXT_DAY)
        ok = not pending_keys(r0.store)
    except SystemExit as e:
        ok = str(e)
    ck.check("I4 a relaunch on the new day resumes and completes", ok is True, ok)
    for mut in ("rollover_off", "rollover_send_off"):
        with _Mut(ACC, mut):
            resm = [one(mut, k) for k in range(1, M + 1)]
        ck.mutant("I4", mut, [a > 0 for _r, a, _s in resm])


# I5 (the driver's preflight: archv2_pilot/selftest.py --part pool) ────────────────────────────────────────────────────

def i5(ck):
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # --main-ref HEAD: the pilot's K2 guard reads main's judge_v2 blobs; before this branch merges they are the old
    # writer's, so every launch would refuse at C0 (c). The flag resolves K2's lookups against HEAD in that process only
    # (printed there); after the merge HEAD's and main's blobs are equal and the flag changes nothing.
    cmd = [sys.executable] + (["-O"] if not __debug__ else []) + [os.path.join(here, "archv2_pilot", "selftest.py"),
                                                                   "--part", "pool", "--main-ref", "HEAD"]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    lines = (p.stdout or "").splitlines()
    tail = [x for x in lines if x.startswith("[SELFTEST-PILOT]") and "checks," in x]
    ok = p.returncode == 0 and tail and tail[-1].endswith(" 0 failed")
    ck.check("I5 archv2_pilot/selftest.py --part pool (%s): the pilot's preflight-first checks PASS" % (
        "python -O" if not __debug__ else "python"), ok, tail[-1] if tail else (p.stderr or "")[-300:])
    for m in ("preflight_after_pool", "preflight_skipped_pooled"):
        killed = [x for x in lines if ("MUTANT %s" % m) in x]
        ck.mutant("I5", m, [bool(killed) and all(x.startswith("[SELFTEST-PILOT] PASS") for x in killed)])
    for x in lines:
        if "POOL" in x and x.startswith("[SELFTEST-PILOT]"):
            ck.out("    " + x)


# I6 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────

SYN_META = {"registration": "POOL-SELFTEST (scratch)", "judge_requested": "fake", "provider": "fake", "max_tokens": "8192",
            "temperature_label": "omitted", "script_blob": "x", "combiner_blob": "x", "prompt_template_blob": "x",
            "parse_version": "x", "pool_id": "x"}


def syn_store(path, n):
    st = dv2verdicts.VerdictStore.create(path, dict(SYN_META, run_id="syn"))
    st.add_schedule([{"match_id": "s%03d" % i, "presentation_order": 1, "draw_index": 0, "variant_id": "v", "stem_key": "k",
                      "contestant_a": "a", "contestant_b": "b", "shown_first": "a", "shown_second": "b",
                      "response_first_sha": "x", "response_second_sha": "y"} for i in range(n)])
    return st


def fast(*conns):
    """SPEED ONLY (the stress harnesses): PRAGMA synchronous=OFF on scratch connections, so a commit does not fsync.
    Nothing checked depends on durability across a power cut; the triggers, the keys and the thread checks are
    unchanged. Never used by the crash harness (I12) or the inertness proof."""
    for c in conns:
        c.execute("PRAGMA synchronous=OFF")


def syn_turns(slot):
    return "system", "user of %s" % slot["match_id"]


def syn_templates(d, n, cap):
    """Fresh, EMPTY journal v2 (cap), synthetic store (n slots) and probe journal, created ONCE (under the MUTANT in
    force: the DDL is the mutant's) and byte-copied per trial (a copy of a fresh DB is that fresh DB; the DDL's fsyncs
    are paid once)."""
    os.makedirs(d)
    syn_store(os.path.join(d, "s.db"), n).conn.close()
    ACC.Journal.open(os.path.join(d, "j.db"), cap=cap, create=True, max_inflight=POOL.MAX_INFLIGHT).close()
    ACC.Journal.open(os.path.join(d, "p.db"), create=True, max_inflight=POOL.MAX_INFLIGHT).close()
    return d


def syn_pool(journal_path, store_path, n, N, cap, seed, day=DAY):
    """A pool over a synthetic store (real VerdictStore, real journal v2, real TwoPhaseCall, the fake transport)."""
    st = dv2verdicts.VerdictStore.open(store_path)
    j = ACC.Journal.open(journal_path, cap=cap, max_inflight=POOL.MAX_INFLIGHT)
    fast(st.conn, j.conn)
    posts = {"n": 0}
    label = "stress w=%d" % N
    j.begin_launch(label, N)
    so = {}
    for i in range(n):
        so.setdefault(_payload_sha(*syn_turns({"match_id": "s%03d" % i})), []).append(("s%03d" % i, 1))
    fk = Fake(seed=seed, max_ms=1.0, errors=False)
    tp = ACC.TwoPhaseCall(fk, j, so, posts, label, day, _payload_sha, clock=lambda: day)

    def prepare(slot):
        s, u = syn_turns(slot)
        return None, s, u, rr.payload_bytes(s, u)

    def finish(ctx, t, o):
        if o.kind != "returned":
            return ("error", t.sha, None, "x")
        return ("verdict", t.body, t.sha, {"vote": "TIE", "raw_text": "x", "parse_version": "x", "judge_requested": "f",
                                           "provider": "f", "max_tokens": 1, "temperature_label": "omitted",
                                           "prompt_template_blob": "x", "script_blob": "x", "combiner_blob": "x",
                                           "stem_key": "k", "pool_id": "x"})
    expected = [dict(zip(dv2verdicts.SCHEDULE_COLS, r)) for r in st.pending()]
    pool = POOL.PostingPool(tp, expected, N, prepare, finish, out=QUIET)
    stop = None
    try:
        st.drain(pool.poster)
    except SystemExit as e:
        stop = str(e)
    finally:
        pool.close()
    jrows = j.state()["invocations"]
    verdicts = st.conn.execute("SELECT COUNT(*) FROM verdict").fetchone()[0]
    st.conn.close()
    j.close()
    return {"journal": jrows, "received": len(fk.received), "verdicts": verdicts, "stop": stop, "posts": posts["n"],
            "max_seen": pool.max_inflight_seen}


def unresolved_probe(path, N):
    """Reserve N tickets directly in one launch of bound N, then one more: the launch-bound trigger must refuse it."""
    j = ACC.Journal.open(path, max_inflight=POOL.MAX_INFLIGHT)
    fast(j.conn)
    try:
        j.begin_launch("probe w=%d" % N, N)
        for i in range(N):
            j.pending("probe w=%d" % N, "m%d" % i, 1, "0" * 64, DAY)
        try:
            j.pending("probe w=%d" % N, "extra", 1, "0" * 64, DAY)
        except SystemExit:
            pass
        return len(j.state()["unresolved"])
    finally:
        j.close()


def i6(ck, tmp, trials=I6_TRIALS):
    tpl = {}

    def trial(tag, t):
        if tag not in tpl:
            tpl[tag] = syn_templates(os.path.join(tmp, "i6_tpl_" + tag), 60, 50)
        d = os.path.join(tmp, "i6_%s_%d" % (tag, t))
        shutil.copytree(tpl[tag], d)
        r = syn_pool(os.path.join(d, "j.db"), os.path.join(d, "s.db"), 60, 8, 50, seed=t)
        r["unresolved"] = unresolved_probe(os.path.join(d, "p.db"), 8)
        S._rmtree(d)
        return r
    res = [trial("ok", t) for t in range(trials)]
    ck.check("I6 cap 50, N 8, 60 pending, %d trials: exactly 50 journal rows in every trial" % trials,
             all(r["journal"] == 50 for r in res), sorted({r["journal"] for r in res}))
    ck.check("I6 <= 50 requests received in every trial (and the ledger holder == the journal)",
             all(r["received"] <= 50 and r["posts"] == r["journal"] for r in res),
             (max(r["received"] for r in res), sorted({r["posts"] for r in res})))
    ck.check("I6 every trial stops cleanly at the cap (the trigger's refusal, 50 verdicts recorded, max in flight <= 8)",
             all(r["stop"] and "hard cap" in r["stop"] and r["verdicts"] == 50 and r["max_seen"] <= 8 for r in res))
    ck.check("I6 the launch-bound trigger: a reservation beyond N = 8 is refused (unresolved stays 8) in every trial",
             all(r["unresolved"] == 8 for r in res))
    with _Mut(ACC, "cap_in_workers"):
        rm = [trial("m1", t) for t in range(trials)]
    ck.mutant("I6", "cap_in_workers", [r["journal"] != 50 for r in rm])
    with _Mut(ACC, "unresolved_trigger_off"):
        rm2 = [trial("m2", t) for t in range(trials)]
    ck.mutant("I6", "unresolved_trigger_off", [r["unresolved"] > 8 for r in rm2])


# I7 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────

# the registered I7 is isolated from the coordinator's burst / raise / breaker rules (they have their own RC checks)
I7_CFG = dict(burst_n=1000, raise_every_s=1e6, breaker_k=1000)


def _pooled(r, loaded, rub, N, lines=None, rate=None, **kw):
    """launch_like through the stub (rr.call_judge_full REAL), returning (err, pool, lines)."""
    wr = {}
    lines = [] if lines is None else lines
    err = None
    try:
        launch_like(r, loaded, rub, rr.call_judge_full, N, out=lines.append, rate=rate,
                    writer_hook=lambda w: wr.setdefault("w", w), **kw)
    except SystemExit as e:
        err = str(e)
    pool = getattr(wr.get("w"), "last_pool", None)
    return err, pool, lines


def i7(ck, tmp, small, rub, N=4):
    shas = sorted(slot_of_loaded(small, rub))
    ex_sha, ra_sha, bare_sha = shas[0], shas[1], shas[2]

    def one(tag):
        r = Run(tmp, "i7_" + tag)
        with Stub() as st:
            st.script = {ex_sha: [429] * 6, ra_sha: [429, 429, 200], bare_sha: [429, 200]}
            st.retry_after = {ex_sha: "1", ra_sha: "7"}
            err, pool, lines = _pooled(r, small, rub, N, rate=POOL.RateConfig(**I7_CFG))
            sleeps, received = list(st.sleeps), len(st.received)
        return r, lines, pool, err, sleeps, received
    r, lines, pool, err, sleeps, received = one("ok")
    mid_ex = slot_of_loaded(small, rub)[ex_sha][0]
    inv, res = journal_rows(r.journal)
    seq_ex = [s for s, _l, m, o, h in inv if h == ex_sha]
    ck.check("I7 the exhausted slot: an error attempt row HTTPError:429, NO verdict, pending after the launch", err is None
             and count(r.store, "SELECT COUNT(*) FROM attempt WHERE match_id=? AND presentation_order=? AND error_class ="
                                " 'HTTPError:429'", mid_ex) == 1 and count(
                 r.store, "SELECT COUNT(*) FROM verdict WHERE match_id=? AND presentation_order=?", mid_ex) == 0 and
             tuple(mid_ex) in [tuple(x) for x in pending_keys(r.store)], err)
    ck.check("I7 the journal: the exhausted invocation RAISED with http_attempts 6, http_429 6 (the wire counter)",
             len(seq_ex) == 1 and res[seq_ex[0]][0] == "RAISED" and res[seq_ex[0]][2:] == (6, 6), res.get(seq_ex[0]))
    seq_ra = [s for s, _l, m, o, h in inv if h == ra_sha]
    ck.check("I7 a 429-then-200 invocation: RETURNED with http_attempts 3, http_429 2; its verdict recorded",
             len(seq_ra) == 1 and res[seq_ra[0]][0] == "RETURNED" and res[seq_ra[0]][2:] == (3, 2))
    pauses = [(ra, p) for k, ra, _c, p in pool.rate.pauses if k == "429"] if pool else []
    ck.check("I7 the cool-down pauses max(Retry-After, 3 s): 7 -> 7.0, 1 -> 3.0, absent -> >= 3.0 (jittered, RC1)",
             (7.0, 7.0) in pauses and (1.0, 3.0) in pauses and any(ra is None and p >= 3.0 for ra, p in pauses), pauses)
    ck.check("I7 ... every recorded pause >= max(Retry-After, 3); 2 + 6 + 1 = 9 HTTP 429s seen", len(pauses) == 9 and
             all(p >= max(3.0, ra if ra is not None else 0.0) for ra, p in pauses), pauses)
    ck.check("I7 the bound halves once on the exhausted invocation (4 -> 2); [RATE] lines printed",
             pool is not None and pool.rate.bounds == [4, 2] and any("EXHAUSTED on HTTP 429" in x for x in lines)
             and any(x.startswith("[RATE] 429") for x in lines), pool.rate.bounds if pool else None)
    ck.check("I7 / RC2 rr's internal retry loop is NEUTRALISED (rr never slept: its patched sleep recorded nothing) and"
             " every HTTP attempt is journaled (sum http_attempts %d == stub receipts %d)" % (
                 sum((v[2] or 0) for v in res.values()), received), sleeps == [] and
             sum((v[2] or 0) for v in res.values()) == received, sleeps)
    with Stub():
        launch_like(r, small, rub, rr.call_judge_full, N)
    ck.check("I7 the relaunch re-posts the exhausted slot (now 200) and completes", not pending_keys(r.store) and
             [h for _s, l, _m, _o, h in journal_rows(r.journal)[0] if l.startswith("launch#2")] == [ex_sha])
    # RATE STOP: N = 2, every slot exhausted: bound 2 -> 1, then 3 exhausted at bound 1 -> a clean stop
    r2 = Run(tmp, "i7_stop")
    with Stub() as st3:
        st3.default_script = [429] * 6
        err2, p2, _l2 = _pooled(r2, small, rub, 2, rate=POOL.RateConfig(**I7_CFG))
    ck.check("I7 RATE STOP after the third exhaustion at bound 1: a clean stop, every reserved ticket recorded, ledger =="
             " journal", err2 is not None and "RATE STOP" in err2 and p2.rate.exhausted_at_1 == 3 and p2.rate.bounds == [2, 1]
             and not p2.inflight and ledger_calls(r2) == ACC.read_journal(r2.journal)["invocations"] ==
             count(r2.store, "SELECT COUNT(*) FROM attempt"), (err2 or "")[:120])
    with Stub():
        launch_like(r2, small, rub, rr.call_judge_full, 2)
    ck.check("I7 the relaunch after the RATE STOP resumes and completes", not pending_keys(r2.store))
    with _Mut(W, "classify_429_invalid"):
        rm = one("m_invalid")[0]
    ck.mutant("I7", "classify_429_invalid", [count(rm.store, "SELECT COUNT(*) FROM verdict WHERE match_id=? AND"
                                                            " presentation_order=?", mid_ex) > 0])
    with _Mut(POOL, "resend_exhausted"):
        rm = one("m_resend")[0]
    _inv, resm = journal_rows(rm.journal)
    ck.mutant("I7", "resend_exhausted (retries beyond 6)", [any((v[2] or 0) > 6 for v in resm.values())])
    with _Mut(POOL, "no_halving"):
        pm = one("m_nohalve")[2]
    ck.mutant("I7", "no_halving", [pm is not None and pm.rate.bounds == [4]])
    with _Mut(POOL, "gate_ignores_retry_after"):
        pm2 = one("m_gate")[2]
    ck.mutant("I7", "gate_ignores_retry_after", [pm2 is not None and not any(p == 7.0 for _k, _a, _c, p in pm2.rate.pauses)])
    with _Mut(POOL, "rr_retries_live"):
        _r, _l, _p, _e, sleeps_m, _n = one("m_rrlive")
    ck.mutant("RC2", "rr_retries_live (rr's internal retry loop left live: it sleeps 3/6/12/24/48 s, ignoring"
                     " Retry-After)", [len(sleeps_m) > 0])


# RC: the coordinator's rate-control requirements (2026-09-25, items 1-6) ─────────────────────────────────────────────

class FakeClock:
    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t


def rc_units(ck):
    """Deterministic units of the rate control on a fake clock: Retry-After both forms, the backoff ceilings, the burst /
    timeout halving with its hold, the +1 per clean minute up to the workers, the breaker."""
    now = datetime.now(timezone.utc)
    date5 = email.utils.format_datetime(now + timedelta(seconds=5), usegmt=True)
    past = email.utils.format_datetime(now - timedelta(seconds=50), usegmt=True)
    got = {"7": POOL.retry_after_seconds({"Retry-After": "7"}, now), "date+5": POOL.retry_after_seconds(
        {"Retry-After": date5}, now), "past": POOL.retry_after_seconds({"Retry-After": past}, now),
           "junk": POOL.retry_after_seconds({"Retry-After": "soon"}, now), "none": POOL.retry_after_seconds({}, now)}
    ok_ra = (got["7"] == 7.0 and got["date+5"] is not None and 4.0 <= got["date+5"] <= 5.0 and got["past"] == 0.0 and
             got["junk"] is None and got["none"] is None)
    ck.check("RC1 Retry-After: delta-seconds 7 -> 7.0; an HTTP-date 5 s ahead -> ~5; a past date -> 0; junk / absent ->"
             " None", ok_ra, got)
    with _Mut(POOL, "retry_after_date_ignored"):
        gm = POOL.retry_after_seconds({"Retry-After": date5}, now)
    ck.mutant("RC1", "retry_after_date_ignored (the HTTP-date form dropped)", [gm is None])

    def ceilings(mut=None):
        with _Mut(POOL, mut):
            rc = POOL.RateControl(4, POOL.RateConfig(burst_n=1000, breaker_k=1000), time_scale=1e-6)
            for _ in range(7):
                rc.on_failure("429")
            return [c for _k, _a, c, _p in rc.pauses], [p for _k, _a, _c, p in rc.pauses]
    cs, ps = ceilings()
    ck.check("RC1 no Retry-After: full-jitter exponential backoff, ceilings min(60, 2 x 2^k) = 2, 4, 8, 16, 32, 60, 60 and"
             " every pause in [3, max(3, ceiling)]", cs == [2.0, 4.0, 8.0, 16.0, 32.0, 60.0, 60.0] and
             all(3.0 <= p <= max(3.0, c) for p, c in zip(ps, cs)) and len(set(ps)) > 1, (cs, [round(p, 2) for p in ps]))
    csm, _psm = ceilings("backoff_no_growth")
    ck.mutant("RC1", "backoff_no_growth", [csm != [2.0, 4.0, 8.0, 16.0, 32.0, 60.0, 60.0]])

    def adaptive(mut=None):
        with _Mut(POOL, mut):
            clk = FakeClock()
            rc = POOL.RateControl(8, POOL.RateConfig(breaker_k=1000), time_scale=1.0)
            rc._now = clk
            rc.last_event = rc.last_raise = clk()
            trace = []
            for dt, ev in ((0, "429"), (1, "429"), (1, "429"),       # a burst: 8 -> 4
                           (1, "429"), (1, "429"),                   # within the 10 s hold: no second halving
                           (20, "timeout"),                           # 4 -> 2
                           (1, "timeout")):                           # within the hold: none
                clk.t += dt
                rc.on_failure(ev)
                trace.append(rc.bound)
            for dt in (59, 1, 60, 60, 60, 60, 60, 60, 60, 60):       # +1 per clean 60 s, up to 8
                clk.t += dt
                rc.maybe_raise()
                trace.append(rc.bound)
            rc.on_ok()
            return trace, rc.bounds
    tr, bh = adaptive()
    ck.check("RC4 adaptive: a 429 burst halves 8 -> 4, a second within the 10 s hold does not, a timeout halves 4 -> 2;"
             " +1 per clean 60 s up to the workers 8 and never above", tr == [8, 8, 4, 4, 4, 2, 2, 2, 3, 4, 5, 6, 7, 8, 8, 8, 8]
             and max(bh) == 8, tr)
    ck.mutant("RC4", "no_halving (burst / timeout)", [adaptive("no_halving")[0][:7] != tr[:7]])
    ck.mutant("RC4", "no_raise", [adaptive("no_raise")[0][7:] != tr[7:]])
    ck.mutant("RC4", "raise_unbounded", [max(adaptive("raise_unbounded")[1]) > 8])

    def breaker(mut=None):
        with _Mut(POOL, mut):
            rc = POOL.RateControl(4, POOL.RateConfig(breaker_k=4, burst_n=1000), time_scale=1e-6)
            seq = ["429", "timeout", "429"]
            for k in seq:
                rc.on_failure(k)
            before = rc.breaker_msg
            rc.on_ok()                                                # a success resets the count
            for k in ("429", "429", "timeout"):
                rc.on_failure(k)
            mid = rc.breaker_msg
            rc.on_failure("429")
            return before, mid, rc.breaker_msg
    b0, b1, b2 = breaker()
    ck.check("RC5 circuit breaker: K = 4 consecutive timeouts / 429s trip it; a success in between resets the count",
             b0 is None and b1 is None and b2 is not None and "CIRCUIT BREAKER" in b2, (b0, b1, b2))
    ck.mutant("RC5", "breaker_off", [breaker("breaker_off")[2] is None])


def rc_wire(ck, tmp, small, rub):
    """The wire under the stub: the whole-pool pause, the token bucket, the per-request timeout, the breaker end to end,
    Retry-After as an HTTP-date end to end, the HTTP-attempt cap."""
    shas = sorted(slot_of_loaded(small, rub))
    saved = POOL.TIME_SCALE
    try:
        # RC1 whole-pool pause: one 429 with Retry-After 3 s; time scale 0.1 -> a 300 ms pause of EVERY worker.
        # [F2 (b), READY review d32fa75] measured CLIENT-SIDE from the instant the pause was SET (RateControl.pause_windows)
        # against the grant instants (attempt_times): 0 grants in (set, pause_until). The 429 goes to the FOURTH slot in key
        # order, so the main thread has later slots to reserve while it waits (the pause must hold the reservations and
        # every worker); the build's stub-receipt window with a 30 ms margin is retired.
        POOL.TIME_SCALE = 0.1

        m1 = sorted(small.specs)[1]
        fourth = P.build_dual(small.specs[m1], rub)[1].sha256      # slot index 3 in key order

        def whole(tag):
            r = Run(tmp, "rc_whole_" + tag)
            with Stub() as st:
                st.script = {fourth: [429, 200]}
                st.retry_after = {fourth: "3"}
                st.delay = {h: [0.02, 0.02] for h in shas}
                err, pool, _l = _pooled(r, small, rub, 4, rate=POOL.RateConfig(max_rpm=6000, **I7_CFG))
            if pool is None or err is not None:
                return None
            win = list(pool.rate.pause_windows)
            inside = sum(1 for s0, u0, _w in win for g in pool.rate.attempt_times if s0 < g < u0)
            return inside, len(win), len(pool.rate.attempt_times)
        got1 = whole("ok")
        ck.check("RC1 one 429 (Retry-After 3 s) pauses the WHOLE pool: 0 grants by any worker inside (set, pause_until), 1"
                 " pause, 13 attempts (12 slots + the retry)", got1 is not None and got1[0] == 0 and got1[1] == 1 and
                 got1[2] == 13, got1)
        with _Mut(POOL, "gate_per_worker"):
            got1m = whole("mut")
        ck.mutant("RC1", "gate_per_worker (only the 429'd worker waits)", [got1m is not None and got1m[0] > 0])
        # RC1b [F2 (c)] a 429 while >= 3 workers are QUEUED at a BINDING max_rpm: max_rpm 6 at time scale 0.01 (a grant
        # every 100 ms), 8 workers, the first slot's 429 held 250 ms (the others queue at the bucket meanwhile) with
        # Retry-After 60 s (a 600 ms pause): 0 grants inside the pause, the grant gaps never below the interval, and the
        # witness: >= 3 threads inside acquire when the pause was set. MUTANTS gate_before_bucket_only (the pause read by
        # wait_gate only) and bucket_by_schedule (pre-assigned slots: the backlog fires together at the pause's end)
        POOL.TIME_SCALE = 0.01
        m0 = sorted(small.specs)[0]
        first = P.build_dual(small.specs[m0], rub)[0].sha256      # slot index 0 in key order: reserved and granted first

        def queued(tag):
            r = Run(tmp, "rc_queued_" + tag)
            with Stub() as st:
                st.script = {first: [429, 200]}
                st.retry_after = {first: "60"}
                st.delay = {first: [0.25]}
                err, pool, _l = _pooled(r, small, rub, 8, rate=POOL.RateConfig(max_rpm=6, **I7_CFG))
            if pool is None or err is not None or not pool.rate.pause_windows:
                return None
            s0, u0, w0 = pool.rate.pause_windows[0]
            g = sorted(pool.rate.attempt_times)
            inside = sum(1 for t in g if s0 < t < u0)
            gap = min((b - a for a, b in zip(g, g[1:])), default=None)
            return inside, gap, w0, len(g), 60.0 / 6 * POOL.TIME_SCALE
        q = queued("ok")
        ck.check("RC1b a 429 with >= 3 workers queued at a binding max_rpm (6 at scale 0.01; 8 workers): 0 grants inside"
                 " the 600 ms pause, every grant gap >= the 100 ms interval, 13 attempts", q is not None and q[2] >= 3 and
                 q[0] == 0 and q[1] is not None and q[1] >= q[4] and q[3] == 13,
                 None if q is None else "inside %d, min gap %.4f s (interval %.4f), waiting at the 429 %d, attempts %d" % (
                     q[0], q[1], q[4], q[2], q[3]))
        with _Mut(POOL, "gate_before_bucket_only"):
            qm1 = queued("m_gate")
        ck.mutant("RC1b", "gate_before_bucket_only (queued workers keep taking tokens inside the pause)",
                  [qm1 is not None and qm1[2] >= 3 and qm1[0] > 0])
        with _Mut(POOL, "bucket_by_schedule"):
            qm2 = queued("m_sched")
        ck.mutant("RC1b", "bucket_by_schedule (pre-assigned slots: the backlog fires together when the pause ends)",
                  [qm2 is not None and qm2[2] >= 3 and qm2[1] is not None and qm2[1] < qm2[4]])
        # RC1 end to end: Retry-After as an HTTP-date
        POOL.TIME_SCALE = 0.001

        def dated(tag):
            r = Run(tmp, "rc_date_" + tag)
            with Stub() as st:
                st.script = {shas[0]: [429, 200]}
                st.retry_after = {shas[0]: lambda: email.utils.format_datetime(
                    datetime.now(timezone.utc) + timedelta(seconds=6), usegmt=True)}
                err, pool, _l = _pooled(r, small, rub, 2, rate=POOL.RateConfig(**I7_CFG))
            return [(ra, p) for k, ra, _c, p in pool.rate.pauses if k == "429"] if pool else None
        pd = dated("ok")
        ck.check("RC1 end to end: a 429 whose Retry-After is an HTTP-date 6 s ahead pauses ~6 s (not the 3 s floor)",
                 pd and len(pd) == 1 and 4.5 <= pd[0][1] <= 6.0, pd)
        with _Mut(POOL, "retry_after_date_ignored"):
            pdm = dated("mut")
        ck.mutant("RC1", "retry_after_date_ignored (end to end)", [pdm is not None and not (4.5 <= pdm[0][1] <= 6.0)])
        # RC3 the global token bucket: max_rpm 10 at time scale 0.01 -> 10 attempts per 0.6 s window at most, 8 workers
        POOL.TIME_SCALE = 0.01

        def bucket(tag):
            r = Run(tmp, "rc_rpm_" + tag)
            with Stub() as st:
                err, pool, _l = _pooled(r, small, rub, 8, rate=POOL.RateConfig(max_rpm=10, **I7_CFG))
                rec = sorted(t for t, _s, _st in st.received_t)
            tok = sorted(pool.rate.attempt_times) if pool else []
            win = 60.0 * POOL.TIME_SCALE

            def worst(ts):
                return max((sum(1 for u in ts if t <= u < t + win) for t in ts), default=0)
            gap = min((b - a for a, b in zip(tok, tok[1:])), default=None)
            return worst(tok), worst(rec), len(tok), err, gap
        wt, wr_, n, e, gp = bucket("ok")
        ck.check("RC3 max_rpm 10 over 8 workers [F2 (a): on the client's own grant instants]: every gap between grants >="
                 " the interval 60 / 10 s (scaled), the grants never exceed 10 in any 60 s window (scaled), the stub"
                 " receipts never exceed 10 + 1 (network jitter), %d attempts" % n, e is None and n == 12 and gp is not None
                 and gp >= 6.0 * POOL.TIME_SCALE and wt <= 10 and wr_ <= 11, (wt, wr_, n, e, gp))
        with _Mut(POOL, "bucket_per_worker"):
            wtm, _wrm, _nm, _em, _gm = bucket("mut")
        ck.mutant("RC3", "bucket_per_worker (N workers x max_rpm)", [wtm > 10])
        # RC5 the per-request timeout: the stub holds the FIRST attempt of one sha 1.0 s; the timeout is 0.3 s
        POOL.TIME_SCALE = 0.001

        def timeout(tag):
            r = Run(tmp, "rc_to_" + tag)
            with Stub() as st:
                st.delay = {shas[1]: [1.0], shas[2]: [0.1]}
                err, pool, _l = _pooled(r, small, rub, 4, rate=POOL.RateConfig(request_timeout_s=0.3, **I7_CFG))
            _inv, res = journal_rows(r.journal)
            att = {h: res[s][2] for s, _l, _m, _o, h in _inv}
            return att, pool, err, r
        att, pool, err, r = timeout("ok")
        ck.check("RC5 a response held 1.0 s past the 0.3 s per-request timeout: that attempt times out, the pool retries it"
                 " (2 HTTP attempts, verdict recorded), a 0.1 s delayed response is served in 1 attempt, the run completes;"
                 " the timeout halved the bound", err is None and att.get(shas[1]) == 2 and att.get(shas[2]) == 1 and
                 not pending_keys(r.store) and pool is not None and pool.rate.bounds[:2] == [4, 2] and
                 any(k == "timeout" for k, _a in pool.rate.events), (att.get(shas[1]), att.get(shas[2]), err,
                                                                     pool.rate.bounds if pool else None))
        with _Mut(POOL, "no_request_timeout"):
            attm = timeout("mut")[0]
        ck.mutant("RC5", "no_request_timeout (rr's 600 s kept)", [attm.get(shas[1]) == 1])
        # RC5 the breaker end to end: every attempt 429 (Retry-After 0), K 4
        def brk(tag):
            r = Run(tmp, "rc_brk_" + tag)
            with Stub() as st:
                st.default_script = [429] * 50
                st.default_retry_after = "0"
                err, pool, _l = _pooled(r, small, rub, 2, rate=POOL.RateConfig(breaker_k=4, burst_n=1000,
                                                                               raise_every_s=1e6))
            return err, pool, r
        err, pool, r = brk("ok")
        ck.check("RC5 the circuit breaker end to end: K = 4 consecutive 429s stop the launch cleanly (every reserved"
                 " ticket recorded, ledger == journal); the relaunch resumes and completes", err is not None and
                 "CIRCUIT BREAKER" in err and not pool.inflight and ledger_calls(r) ==
                 ACC.read_journal(r.journal)["invocations"] and _relaunch_completes(r, small, rub), (err or "")[:160])
        with _Mut(POOL, "breaker_off"):
            errm = brk("mut")[0]
        ck.mutant("RC5", "breaker_off (end to end)", [errm is None or "CIRCUIT BREAKER" not in errm])
        # RC2 the HTTP-attempt cap: journal cap 10, every sha 429 twice then 200 -> attempts, not invocations, bind
        def cap(tag):
            r = Run(tmp, "rc_cap_" + tag)
            with Stub() as st:
                st.default_script = [429, 429, 200]
                st.default_retry_after = "0"
                err, pool, _l = _pooled(r, small, rub, 2, cap=10, rate=POOL.RateConfig(**I7_CFG))
                n = len(st.received)
            return err, n, r
        err, n, r = cap("ok")
        _inv, res = journal_rows(r.journal)
        ck.check("RC2 every HTTP attempt counts against the journal's cap 10: %d requests received, the launch stops at the"
                 " HTTP-ATTEMPT CAP, the journal's http_attempts sum %d <= 10" % (n, sum((v[2] or 0) for v in res.values())),
                 err is not None and "HTTP-ATTEMPT CAP" in err and n <= 10 and sum((v[2] or 0) for v in res.values()) <= 10
                 and ledger_calls(r) == ACC.read_journal(r.journal)["invocations"], (err or "")[:160])
        with _Mut(POOL, "http_cap_off"):
            _e, nm, _r = cap("mut")
        ck.mutant("RC2", "http_cap_off (attempts counted per invocation only)", [nm > 10])
    finally:
        POOL.TIME_SCALE = saved


def _relaunch_completes(r, loaded, rub):
    with Stub():
        try:
            launch_like(r, loaded, rub, rr.call_judge_full, 2)
        except SystemExit:
            return False
    return not pending_keys(r.store)


# I8 (E-8) ─────────────────────────────────────────────────────────────────────────────────────────────────────────────

def i8(ck, tmp, loaded, rub):
    tpl = {}

    def template(v2):
        """A fresh store (writer.create, no post) and a fresh journal (v1 for N = 1, v2 otherwise), created ONCE and
        byte-copied per cell (the DDL's fsyncs paid once); every cell, the reference included, relaunches its copy."""
        k = "v2" if v2 else "v1"
        if k not in tpl:
            d = os.path.join(tmp, "i8_tpl_" + k)
            os.makedirs(d)
            W.JudgeWriter.create(os.path.join(d, "store.db"), "POOL-SELFTEST (scratch)", "e8", loaded, rub,
                                 S._ctx()).close()
            ACC.Journal.open(os.path.join(d, "store.db.invocations.db"), create=True,
                             max_inflight=POOL.MAX_INFLIGHT if v2 else None).close()
            tpl[k] = d
        return tpl[k]

    def cell(tag, N, seed):
        r = Run(tmp, "i8_%s_%d_%d" % (tag, N, seed))
        for f in ("store.db", "store.db.invocations.db"):
            shutil.copyfile(os.path.join(template(N > 1), f), os.path.join(r.dir, f))
        order = []
        wr = {}

        def hook(w):
            base = w.store.drain

            def drain(poster):
                def rec(slot):
                    order.append((slot["match_id"], slot["presentation_order"]))
                    return poster(slot)
                return base(rec)
            w.store.drain = drain
            wr["w"] = w
        fk = Fake(seed=seed, max_ms=4.0)
        launch_like(r, loaded, rub, fk, N, writer_hook=hook, run_id="e8", fast_io=True)
        inv, res = journal_rows(r.journal)
        jproj = sorted((m, o, h, res[s][0]) for s, _l, m, o, h in inv)
        out = (projection(r.store), order, jproj, sorted(fk.received))
        S._rmtree(r.dir)
        return out
    ref = cell("ref", 1, 0)
    diffs = []
    for N in E8_NS:
        for seed in range(E8_SEEDS):
            got = cell("c", N, seed)
            if got != ref:
                diffs.append((N, seed, [i for i in range(4) if got[i] != ref[i]]))
    ck.check("I8 / EC3 E-8 order invariance: %d of %d (N, seed) cells equal to the N = 1 run (store projection, drain"
             " order, journal projection, posted bodies)" % (len(E8_NS) * E8_SEEDS - len(diffs), len(E8_NS) * E8_SEEDS),
             not diffs, diffs[:5])
    kills = []
    with _Mut(POOL, "bind_shift"):
        for N in E8_NS[1:]:
            for seed in range(E8_SEEDS):
                got = cell("m", N, seed)
                kills.append(got[0] != ref[0])
    ck.mutant("I8", "bind_shift", kills)


# I9 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def i9(ck, tmp, loaded, rub):
    r = Run(tmp, "i9")
    w = W.JudgeWriter.create(r.store, "POOL-SELFTEST (scratch)", "i9", loaded, rub, S._ctx())
    j = ACC.Journal.open(r.journal, create=True, max_inflight=POOL.MAX_INFLIGHT)
    errs = {}

    def worker():
        for name, fn in (("store", lambda: w.store.conn.execute("SELECT COUNT(*) FROM verdict").fetchone()),
                         ("journal", lambda: j.conn.execute("SELECT COUNT(*) FROM invocation").fetchone())):
            try:
                fn()
                errs[name] = None
            except sqlite3.ProgrammingError as e:
                errs[name] = type(e).__name__
    th = threading.Thread(target=worker)
    th.start()
    th.join()
    w.close()
    j.close()
    ck.check("I9 a worker thread touching the store's or the journal's connection raises ProgrammingError"
             " (check_same_thread=True)", errs == {"store": "ProgrammingError", "journal": "ProgrammingError"}, errs)
    ck.check("I9 reserve / resolve refuse off the main thread", _refused_thread(lambda: POOL.assert_main_thread("x")))

    def run_m():
        rm = Run(tmp, "i9_m")
        try:
            launch_like(rm, loaded, rub, Fake(errors=False), 4)
            return False, rm
        except SystemExit as e:
            return ("worker thread" in str(e)), rm
    with _Mut(POOL, "worker_resolves"):
        killed, rm = run_m()
    ck.mutant("I9", "worker_resolves", [killed])


def _refused_thread(fn):
    box = {}

    def t():
        try:
            fn()
            box["r"] = False
        except SystemExit as e:
            box["r"] = "worker thread" in str(e)
    th = threading.Thread(target=t)
    th.start()
    th.join()
    return box.get("r") is True


# I10 / I11 ────────────────────────────────────────────────────────────────────────────────────────────────────────────

def i10(ck, tmp, small, rub):
    def one(tag):
        r = Run(tmp, "i10_" + tag)
        with Stub() as st:
            err = None
            try:
                launch_like(r, small, rub, rr.call_judge_full, 4)
            except SystemExit as e:
                err = str(e)
        inv, res = journal_rows(r.journal)
        by_sha = {h for _s, _l, _m, _o, h in inv}
        return r, err, st.received, res
    r, err, rec, res = one("ok")
    ck.check("I10 every request's bytes are a journaled ticket's body; 0 wire refusals", err is None and rec and
             all(h in {x[4] for x in journal_rows(r.journal)[0]} for h, _f, _w in rec) and
             not any("WireRefused" in (v[1] or "") for v in res.values()))
    with _Mut(ACC, "body_prev_reserve"):
        _r, errm, recm, _res = one("m_res")
    ck.mutant("I10", "body_prev_reserve (killed at the reserve assert)", [errm is not None and "reserved ticket's body" in
                                                                          errm])
    with _Mut(ACC, "body_prev_send"):
        rm, errm2, recm2, resm2 = one("m_send")
    wire = sum(1 for v in resm2.values() if "WireRefused" in (v[1] or ""))
    ck.mutant("I10", "body_prev_send (killed at the wire counter)", [wire > 0])
    ck.check("I10 under body_prev_send no mismatched body reached the stub (refused BEFORE it left)",
             all(h in {x[4] for x in journal_rows(rm.journal)[0]} for h, _f, _w in recm2))


def i11(ck, tmp, small, rub):
    snap = POOL.rr_snapshot()
    r = Run(tmp, "i11")
    with Stub() as st:
        inner = POOL.rr_snapshot()
        launch_like(r, small, rub, rr.call_judge_full, 4)
        after = POOL.rr_snapshot()
    ck.check("I11 / E-7 after a pooled run PROVIDER, JUDGE_MODEL, MAX_TOKENS, TEMPERATURE (None), the endpoint and the key"
             " are unchanged", inner == after and after[3] is None and POOL.rr_snapshot() == snap)
    r2 = Run(tmp, "i11_m")
    killed = False
    with Stub():
        with _Mut(POOL, "worker_sets_temperature"):
            try:
                launch_like(r2, small, rub, rr.call_judge_full, 4)
            except SystemExit as e:
                killed = "TEMPERATURE" in str(e) or "changed" in str(e) or "reserved ticket" in str(e)
    rr.TEMPERATURE = None
    ck.mutant("I11", "worker_sets_temperature", [killed])


# I12 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def crash_child(cfg_path):
    """Subprocess body: one launch at N = 8 that dies (os._exit) at the configured point."""
    with open(cfg_path, encoding="utf-8") as f:
        cfg = json.load(f)
    P.configure_rr()
    rub = S.gold_rubric()
    loaded = LD.load_matches(cfg["requests"], cfg["ev_path"], out=QUIET)
    run = Run.__new__(Run)
    run.dir, run.store, run.journal, run.ledger = cfg["dir"], cfg["store"], cfg["journal"], cfg["ledger"]
    phase, k = cfg["phase"], cfg["k"]

    def hook(sha, n):
        if phase == "worker" and n == k:
            os._exit(77)

    class T(ACC.TwoPhaseCall):
        n = 0

        def reserve(self, system, user):
            t = super().reserve(system, user)
            T.n += 1
            if phase == "reserve" and T.n == k:
                os._exit(77)
            return t
    launch_like(run, loaded, rub, Fake(seed=k, max_ms=2.0, log_path=cfg["log"], hook=hook, errors=False), 8,
                transport_cls=T)
    os._exit(0)


def steward_rollback(path):
    """The documented recovery after a crash (pool_guard's message): a read-write open and close of a DB whose -journal
    is non-empty rolls the hot journal back. Returns True when a hot journal was present."""
    j = path + "-journal"
    if not (os.path.exists(j) and os.path.getsize(j) > 0):
        return False
    c = sqlite3.connect(path, isolation_level=None)
    try:
        c.execute("SELECT COUNT(*) FROM sqlite_master").fetchone()     # a HOT journal is rolled back here
        # a journal whose header is zeroed (the crash hit a commit after the header was cleared) is NOT hot: its
        # transaction is committed and SQLite leaves the file; the documented conversion removes it
        c.execute("PRAGMA journal_mode=PERSIST").fetchone()
        c.execute("PRAGMA journal_mode=DELETE").fetchone()
    finally:
        c.close()
    if os.path.exists(j) and os.path.getsize(j) > 0:
        raise SystemExit("[POOL-SELFTEST] the -journal of %s survived the steward's rollback" % path)
    return True


def i12(ck, tmp, loaded, rub, requests, ev_path, points=I12_POINTS):
    M = 2 * len(loaded.specs)
    rng = random.Random("I12-crash-points")
    cells = [(("reserve", "worker")[p % 2], rng.randint(1, M - 1)) for p in range(points)]
    ok_rows, kills = [], []
    for p, (phase, k) in enumerate(cells):
        r = Run(tmp, "i12_%d" % p)
        log = os.path.join(r.dir, "server.log")
        cfgp = os.path.join(r.dir, "cfg.json")
        with open(cfgp, "x", encoding="utf-8") as f:
            json.dump({"requests": requests, "ev_path": ev_path, "dir": r.dir, "store": r.store, "journal": r.journal,
                       "ledger": r.ledger, "phase": phase, "k": k, "log": log}, f)
        cmd = [sys.executable] + (["-O"] if not __debug__ else []) + [os.path.abspath(__file__), "--crash-child", cfgp]
        pr = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        crashed = pr.returncode == 77
        copy_dir = r.dir + "_mut"
        shutil.copytree(r.dir, copy_dir)
        hot = [steward_rollback(x) for x in (r.store, r.journal, os.path.join(copy_dir, "store.db"),
                                              os.path.join(copy_dir, "store.db.invocations.db"))]
        js0 = ACC.read_journal(r.journal)
        unres = len(js0["unresolved"])
        # the relaunch (correct)
        lines = []
        err = None
        try:
            launch_like(r, loaded, rub, Fake(seed=1000 + p, log_path=log, errors=False), 8, out=lines.append)
        except SystemExit as e:
            err = str(e)
        with open(log, encoding="utf-8") as f:
            shas = [x.strip() for x in f if x.strip()]
        reposts = sum(shas.count(h) - 1 for h in set(shas))
        per_slot = count(r.store, "SELECT MAX(c) FROM (SELECT COUNT(*) c FROM verdict GROUP BY match_id,"
                                  " presentation_order, draw_index)")
        js1 = ACC.read_journal(r.journal)
        disclosed = sum("an ORPHAN, counted and disclosed" in x for x in lines)
        ok = (crashed and err is None and unres >= 1 and per_slot == 1 and not pending_keys(r.store) and reposts <= 8 and
              disclosed == unres and js1["by_outcome"].get("ORPHAN", 0) == unres and
              ledger_calls(r) == js1["invocations"])
        ok_rows.append((p, phase, k, crashed, unres, reposts, disclosed, ok, err, pr.stderr[-200:] if not crashed else "",
                        sum(hot[:2])))
        # the mutant relaunch on the copy
        rc = Run.__new__(Run)
        rc.dir, rc.store, rc.journal, rc.ledger = copy_dir, os.path.join(copy_dir, "store.db"), os.path.join(
            copy_dir, "store.db.invocations.db"), os.path.join(copy_dir, "ledger")
        linesm = []
        with _Mut(ACC, "orphans_returned"):
            try:
                launch_like(rc, loaded, rub, Fake(seed=1000 + p, errors=False), 8, out=linesm.append)
            except SystemExit:
                pass
        jsm = ACC.read_journal(rc.journal)
        kills.append(jsm["by_outcome"].get("ORPHAN", 0) != unres or sum("ORPHAN" in x for x in linesm) != unres)
        S._rmtree(r.dir)
        S._rmtree(copy_dir)
    bad = [x for x in ok_rows if not x[7]]
    ck.check("I12 %d seeded crash points (os._exit, N = 8; phases reserve / worker): after the relaunch verdicts per slot"
             " <= 1 and the run complete, re-posts <= 8, every orphan disclosed, ledger == journal after reconcile" % points,
             not bad, bad[:3])
    ck.check("I12 every crash point left >= 1 unresolved invocation (the mutant is observable at every point); re-posts"
             " max %d, orphans %d..%d" % (max(x[5] for x in ok_rows), min(x[4] for x in ok_rows),
                                          max(x[4] for x in ok_rows)), all(x[4] >= 1 and x[3] for x in ok_rows))
    ck.check("I12 disclosure: %d of %d crash points left a hot rollback journal (store or invocation journal), rolled back"
             " by the documented read-write open / close before the relaunch (a hot -journal REFUSES every read-only"
             " opener: pool_guard / data_v2.ro)" % (sum(1 for x in ok_rows if x[10]), len(ok_rows)), True)
    ck.mutant("I12", "orphans_returned", kills)


# I13 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def i13(ck, tmp, small, rub):
    real = W.JudgeWriter.identity

    def leg_a_identity(*a, **k):
        d = real(*a, **k)
        d["writer_blob"] = LEG_A_WRITER_BLOB
        return d
    p = os.path.join(tmp, "i13.db")
    W.JudgeWriter.identity = staticmethod(leg_a_identity)
    try:
        W.JudgeWriter.create(p, "POOL-SELFTEST (scratch)", "i13", small, rub, S._ctx()).close()
    finally:
        W.JudgeWriter.identity = staticmethod(real)
    ck.check("I13 the build's writer_blob differs from the leg-A writer's (6db4ab32)",
             git_blob_lf(os.path.join(HERE, "writer.py")) != LEG_A_WRITER_BLOB)
    ck.check("I13 a store created by the leg-A writer is REFUSED on relaunch by the build (writer_blob)", _refused(
        lambda: W.JudgeWriter.open(p, small, rub, S._ctx()), ("recipe identity differs", "writer_blob")))
    saved = W.IDENTITY_KEYS
    W.IDENTITY_KEYS = tuple(k for k in saved if k != "writer_blob")
    try:
        admitted = False
        try:
            W.JudgeWriter.open(p, small, rub, S._ctx()).close()
            admitted = True
        except SystemExit:
            admitted = False
    finally:
        W.IDENTITY_KEYS = saved
    ck.mutant("I13", "writer_blob dropped from IDENTITY_KEYS", [admitted])


# ── main ─────────────────────────────────────────────────────────────────────────────────────────────────────────────

def selftest(out=_out_default, only=None):
    ck = Checks(out)
    tmp = tempfile.mkdtemp(prefix="jv2_pool_selftest_")
    saved_scale = POOL.TIME_SCALE
    t0 = time.time()
    try:
        out("[POOL-SELFTEST] python %s, -O %s; fixture under %s; no DB of record; no judge call (a fake call_full or a"
            " localhost stub)" % (sys.version.split()[0], not __debug__, tmp))
        POOL.TIME_SCALE = 0.001
        P.configure_rr()
        rub = S.gold_rubric()
        gv, ev = S.build_views(tmp)
        reqs = clean_requests(ev, rub, tmp)
        loaded = LD.load_matches(reqs, ev, out=QUIET)
        small = LD.load_matches(reqs[:6], ev, out=QUIET)
        ck.check("FIXTURE %d clean matches (%d slots); the small set %d matches" % (len(loaded.specs),
                                                                                    2 * len(loaded.specs),
                                                                                    len(small.specs)),
                 len(loaded.specs) >= 12 and len(small.specs) == 6)
        steps = [("c0", lambda: c0_units(ck, tmp, loaded, rub)), ("i1", lambda: i1(ck, tmp, loaded, rub)),
                 ("i2", lambda: i2(ck, tmp, loaded, rub)), ("i3", lambda: i3(ck, tmp, loaded, rub)),
                 ("i3b", lambda: i3b(ck, tmp, small, rub)),
                 ("i4", lambda: i4(ck, tmp, small, rub)), ("i5", lambda: i5(ck)), ("i6", lambda: i6(ck, tmp)),
                 ("i7", lambda: i7(ck, tmp, small, rub)), ("rc_units", lambda: rc_units(ck)),
                 ("rc_wire", lambda: rc_wire(ck, tmp, small, rub)),
                 ("f4", lambda: f4(ck, tmp, small, rub)), ("i8", lambda: i8(ck, tmp, loaded, rub)),
                 ("i9", lambda: i9(ck, tmp, loaded, rub)), ("i10", lambda: i10(ck, tmp, small, rub)),
                 ("i11", lambda: i11(ck, tmp, small, rub)),
                 ("i12", lambda: i12(ck, tmp, loaded, rub, reqs, ev)), ("i13", lambda: i13(ck, tmp, small, rub))]
        for name, fn in steps:
            if only and name not in only:
                continue
            t1 = time.time()
            fn()
            out("[POOL-SELFTEST] ... %s done in %.1f s" % (name, time.time() - t1))
    finally:
        POOL.TIME_SCALE = saved_scale
        for m in (POOL, W, ACC):
            m.MUTANT = None
        rr.TEMPERATURE = None
        S._rmtree(tmp)
    killed = sum(1 for _i, _n, t, k in ck.mutants if t and k == t)
    out("[POOL-SELFTEST] MUTANTS %d listed, %d KILLED in every trial, %d SURVIVED: %s" % (
        len(ck.mutants), killed, len(ck.mutants) - killed,
        "; ".join("%s %s %d/%d" % m for m in ck.mutants if m[3] != m[2]) or "none"))
    out("[POOL-SELFTEST] %d checks, %d failed%s (%.0f s)" % (ck.n, len(ck.fails), (": " + "; ".join(ck.fails)) if ck.fails
                                                            else "", time.time() - t0))
    return 1 if ck.fails else 0


def main(argv):
    if "--crash-child" in argv:
        return crash_child(argv[argv.index("--crash-child") + 1])
    only = set(argv[argv.index("--only") + 1].split(",")) if "--only" in argv else None
    return selftest(only=only)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
