"""judge_v2.pool: the bounded posting pool of JV2-PARALLEL-POSTING (registered at bf9d80b, docs/judge_v2_program.md
L19096-L19239: section 2 of the specialist's text, verbatim block 3/3, the registrar's readings R1-R5 and the Support
section; the finding of record GROK-NR-THROUGHPUT L18908-L18977). Zero calls here: nothing in this module supplies a live
call; a driver injects rejudge_reasoning.call_judge_full (CONTEXT rule 9) through its TwoPhase transport.

WHAT IS NOT CHANGED. data_v2.verdicts (store.drain, the schema, the pin in _base) is untouched; rejudge_reasoning (pinned
blob:1339592a) is WRAPPED, never edited (its source, its body builder, its headers and its parse are unchanged). At
workers == 1 WITHOUT a rate configuration nothing in this module runs except the one registered line POOL_LINE_SEQUENTIAL
(judge_v2.writer.run prints it and then executes today's sequential path verbatim; E-1).

THE CONTRACT (E-2) a driver implements for the pooled path (class TwoPhase):
  reserve(system, user) -> Ticket   MAIN THREAD. The rollover check; the slot lookup; the journal PENDING insert + commit
                                    (the cap and the unresolved-bound triggers fire HERE, before any post); the post
                                    counter; ticket.body = rr.payload_bytes(system, user).
  send(ticket) -> call_full tuple   WORKER THREAD. Touches NO sqlite connection (every connection of the store and of the
                                    journal is opened with check_same_thread=True, so a worker touching one raises
                                    ProgrammingError), sets NO rr global, re-checks the local date and returns NOT_SENT
                                    without posting on a change; then the injected call_full (ONE HTTP attempt: below).
  resolve(ticket, outcome)          MAIN THREAD. RETURNED / RAISED; a send-time rollover is RAISED "DAY ROLLOVER: not sent"
                                    (counted and disclosed: the invocation was journaled and ledgered), with the
                                    invocation's HTTP attempts and 429s (journal v2's http_attempts / http_429).
  max_inflight                      the journal's bound (1 for a journal created at workers 1).
  http_cap, http_booked()           the ceiling HTTP attempts count against (the journal's cap) and the attempts already
                                    booked in the journal (unknown counts read as 1).

THE PIPELINE (E-3; class PostingPool). drain(poster) is called unchanged; drain calls poster(slot_i) in key order. The
  poster holds the pending list the writer read ONCE before drain (store.pending(), so a restricted store such as the
  pilot's _OnlyStore restricts the pool too), asserts slot_i's key is the i-th expected key (the in-order contract; a
  mismatch REFUSES), tops the reservations up to i + bound - 1 (each payload built by the writer's _payload_for in the
  MAIN thread: the scan witness, the schedule check and the material checks are unchanged), waits for ticket i's future,
  resolves it in the journal and returns the same ("verdict", ...) / ("error", ...) tuple drain records today. Store rows
  are therefore INSERTED IN KEY ORDER at any N; the unresolved invocations are <= N at every instant.
STOPS (E-4). On a stop condition met at a reservation (DAY ROLLOVER, the cap trigger, the unresolved-bound trigger, a
  guard's SystemExit in the payload build), a RATE STOP, the CIRCUIT BREAKER or the HTTP-attempt cap, NO further
  reservation is made; drain is fed the reserved tickets until the last is recorded, and the stop is raised then (a clean
  stop: every in-flight result is recorded, none orphaned). KeyboardInterrupt does not wait: the in-flight tickets stay
  unresolved and become ORPHANs at the relaunch's reconcile (<= N; counted and disclosed). Any other exception leaving
  drain: close() waits for the in-flight futures and resolves them in the journal (the slots stay pending).

RATE CONTROL (E-5, as registered, and the coordinator's HARD REQUIREMENTS of 2026-09-25 (items 1-6), relayed during the
build; the pooled path only). Every HTTP attempt passes through WireCounter.urlopen, a urllib.request.urlopen wrapper
installed for the pool's lifetime (JudgeBench's PostCounter pattern), which, IN THIS ORDER, per attempt:
  (a) REFUSES a request whose bytes are not the ticket's body (WireRefused; never retried);
  (b) counts the attempt against the HTTP-ATTEMPT CAP (the journal's cap minus the attempts already booked): beyond it,
      HttpCapReached (a clean stop);
  (c) waits at the GLOBAL COOL-DOWN GATE (a pause set by any worker holds EVERY worker's next attempt and every new
      reservation: the whole pool);
  (d) takes a token from the GLOBAL TOKEN BUCKET: capacity 1, one token per 60 / max_rpm s, shared by all workers, so N
      workers never exceed max_rpm attempts in any 60 s window (--max-rpm, default 20);
  (e) posts with the PER-REQUEST TIMEOUT min(rr's 600 s, request_timeout_s) (default 120 s) and reads the whole body inside
      the wrapper (a read timeout is caught here too);
  (f) on HTTP 429: the pause is max(Retry-After, 3 s), Retry-After read in BOTH forms (delta-seconds and HTTP-date);
      without the header, EXPONENTIAL BACKOFF WITH FULL JITTER: uniform(0, min(60, 2 x 2^k)) s, k the consecutive
      failures so far, floored at the registered 3 s; on 408 / 5xx / a network error the same jittered backoff; on a
      timeout the jittered backoff too;
  (g) NEUTRALISES rr's internal retry loop: a retryable failure (408, 429, 500, 502, 503, 504, a timeout, a connection
      error) is re-raised as PoolRetry, a RuntimeError that call_judge_full does NOT catch (it catches HTTPError, URLError,
      TimeoutError, ConnectionError), so rr makes exactly ONE attempt per call and never sleeps; the pool's worker retries
      the SAME invocation (same journal row, same ticket, same body) up to MAX_ATTEMPTS = 6 HTTP attempts (rr's count),
      each attempt through (a)-(f). A 400 (content_filter included) and every other status pass through unchanged, so
      rr's content-filter handling (rule 10) is unchanged.
  ADAPTIVE CONCURRENCY: the in-flight bound halves (min 1) on (i) an invocation EXHAUSTED on 429 (6 attempts; always, as
  registered), (ii) a timeout, (iii) a 429 BURST (3 HTTP 429s within 30 s), (ii) and (iii) at most once per 10 s; it RISES
  by 1 per CLEAN MINUTE (60 s without a 429, a timeout or a halving) up to the launch's workers. [DEVIATION from E-5 (c)
  "It never rises within a launch": the coordinator's item 4; for the registrar.]
  RATE STOP (E-5 (d)): at bound 1, the third invocation exhausted on 429 while the bound is already 1.
  CIRCUIT BREAKER: K consecutive HTTP attempts that timed out or got 429 (any success resets the count; default K 8):
  every worker stops retrying and the pool stops cleanly (the relaunch resumes).
  Every change is a [RATE] line printed by the main thread; HTTP attempts and 429s per invocation are journaled.
E-7. The rr globals the preflight checked (PROVIDER, JUDGE_MODEL, MAX_TOKENS, TEMPERATURE, the endpoint and the key) are
  snapshotted when the pool starts and compared before every reservation and at the end: a change REFUSES.
E-6. LedgerLock: the cross-process lock the day-ledger append takes (JudgeBench's pattern, 85a2d9f; the SAME lock file
  name, so a judge_v2 driver and JudgeBench's runner exclude each other on one ledger directory).
[CORRECTED 2026-09-25 by the JV2-PARALLEL-POSTING READY review (docs/reviews/READY_jv2_parallel_posting.md, d32fa75,
NOT READY; fixes F1, F3, F4), insertion only; the sentences above stand as the build's and are read with this bracket:
  F1 (d) THE TOKEN BUCKET is ONE SERIALISED TOKEN TAKER (RateControl.acquire): a token is GRANTED only when no pause is in
     force (now >= pause_until) AND the ACTUAL previous grant is at least one interval (60 / max_rpm s) ago, both read
     under the rate lock at the grant and re-read after EVERY wake; the grant instant is the attempt_times entry. The
     build's acquire (a pre-assigned future slot, slept to, never re-checking the pause) let workers queued at the
     bucket post INSIDE a 429 pause (review C5 / C6) and spaced tokens by schedule, not by grant (C4). The guarantee, as
     the review words it: AT MOST max_rpm ATTEMPTS LEAVE THE CLIENT IN ANY 60 s WINDOW, AND NO ATTEMPT LEAVES WHILE A
     PAUSE IS IN FORCE; an attempt that left before the 429 was received cannot be recalled (the irreducible in-flight
     race), and arrival times at the provider carry network jitter. The rate control's clock is time.perf_counter (on
     this Python time.monotonic ticks at 15.6 ms, which would let a real interval fall short of the cap by one tick).
  (c) wait_gate still runs first; the pause is now ALSO honoured by acquire, so "the whole pool" holds for workers
     already queued at the bucket.
  F3 INTERRUPT: close(interrupted=True) (the writer's KeyboardInterrupt path) sets the rate control's ABORT flag under
     the rate lock: no token is granted after it, every wait wakes, the worker's retry loop makes no further HTTP attempt
     (PoolAborted), and the wire wrapper stays installed until the last worker inside an attempt leaves (so an
     interrupted run never falls back to rr's own retry loop). An attempt already on the wire finishes (bounded by the
     per-request timeout); it is not re-sent.
  F4 LIVE GUARD (rule 11): the pooled path prints "[RATE] live guard: ..." with its inputs on every run and REFUSES,
     before any reservation, a LIVE launch (the transport's call_full is rejudge_reasoning.call_judge_full and the
     endpoint host is not loopback) when TIME_SCALE or the rate control's time_scale is not 1.0 or any SELFTEST-ONLY
     switch (a module attribute MUTANT / MUTANT_* of the judge_v2, archv2_pilot, data_v2 or archv2_arena packages) is set;
     the wire wrapper refuses a request to a non-loopback host under the same conditions BEFORE it leaves (the backstop
     for any transport). The [RATE] config line prints time_scale.]
"""
import collections
import concurrent.futures as cf
import email.utils
import hashlib
import os
import random
import re
import socket
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

from ._base import refuse, rr

MAX_INFLIGHT = 16                       # the registration's maximum N (E-2: "meta.max_inflight ... e.g. 16"; E-8's N)
POOL_LINE_SEQUENTIAL = "[POOL] workers 1 (sequential path)"
MIN_COOLDOWN_S = 3.0                    # E-5 (b): max(Retry-After, 3 s); also the floor of the jittered backoff
RATE_STOP_AT_BOUND_1 = 3                # E-5 (d)
MAX_ATTEMPTS = 6                        # HTTP attempts per invocation (rr's retries=6; now the pool's)
RETRYABLE_HTTP = (408, 429, 500, 502, 503, 504)     # rr's retryable set, verbatim
LEDGER_LOCK_NAME = ".judgebench_side_ledger.lock"   # judgebench_side.LedgerLock's file (85a2d9f), deliberately shared
WAIT_POLL_S = 0.05                      # the main thread polls its futures (a KeyboardInterrupt is honoured on Windows)
TIME_SCALE = 1.0                        # SELFTEST-ONLY: every wall wait of the rate control is x TIME_SCALE (recorded unscaled)
MUTANT = None       # SELFTEST-ONLY (judge_v2/pool_selftest.py): see the mutant table there
# [F4] the live guard: a host that cannot reach a provider, and the SELFTEST-ONLY switches it reads
LOOPBACK_HOSTS = ("127.0.0.1", "localhost", "::1")
SWITCH_PACKAGES = ("judge_v2", "archv2_pilot", "data_v2", "archv2_arena")
SWITCH_NAME = re.compile(r"^MUTANT(_[A-Z0-9]+)*$")


def endpoint_host(url):
    """The host of a URL (lower case), or None when it has none or cannot be read."""
    try:
        h = urllib.parse.urlsplit(str(url)).hostname if url else None
    except (TypeError, ValueError):
        return None
    return h.lower() if h else None


def is_loopback(host):
    return host is not None and (host in LOOPBACK_HOSTS or host.startswith("127."))


def selftest_switches():
    """[F4] Every SELFTEST-ONLY switch that is set: a module attribute named MUTANT or MUTANT_* (not None) in a loaded
    module of SWITCH_PACKAGES, as 'module.ATTR=value' (sorted)."""
    got = []
    for name in sorted(list(sys.modules)):
        mod = sys.modules.get(name)
        if mod is None or name.split(".")[0] not in SWITCH_PACKAGES:
            continue
        d = getattr(mod, "__dict__", None) or {}
        for attr in sorted(k for k in list(d) if SWITCH_NAME.match(k)):
            if d.get(attr) is not None:
                got.append("%s.%s=%r" % (name, attr, d.get(attr)))
    return got


def live_guard_reasons(time_scale):
    """[F4] Why a LIVE post must be refused (empty: admitted): a TIME_SCALE / time_scale other than 1.0, any switch."""
    bad = []
    if TIME_SCALE != 1.0:
        bad.append("judge_v2.pool.TIME_SCALE=%r" % TIME_SCALE)
    if float(time_scale) != 1.0:
        bad.append("the rate control's time_scale=%r" % float(time_scale))
    return bad + selftest_switches()


class RateConfig:
    """The pooled path's rate parameters (the coordinator's items 1-5). Defaults are conservative."""

    def __init__(self, max_rpm=20, request_timeout_s=120.0, breaker_k=8, backoff_base_s=2.0, backoff_cap_s=60.0,
                 burst_n=3, burst_window_s=30.0, halve_hold_s=10.0, raise_every_s=60.0, seed="jv2-pool-backoff"):
        for name, v, lo, hi in (("max_rpm", max_rpm, 1, 6000), ("breaker_k", breaker_k, 1, 1000),
                                ("burst_n", burst_n, 1, 1000)):
            if not isinstance(v, int) or isinstance(v, bool) or not lo <= v <= hi:
                refuse("RateConfig %s %r outside [%d, %d]" % (name, v, lo, hi))
        for name, v in (("request_timeout_s", request_timeout_s), ("backoff_base_s", backoff_base_s),
                        ("backoff_cap_s", backoff_cap_s), ("burst_window_s", burst_window_s),
                        ("halve_hold_s", halve_hold_s), ("raise_every_s", raise_every_s)):
            if not isinstance(v, (int, float)) or isinstance(v, bool) or not v > 0:
                refuse("RateConfig %s %r must be a positive number" % (name, v))
        if request_timeout_s > 600:
            refuse("RateConfig request_timeout_s %r above rr's own 600 s" % request_timeout_s)
        self.max_rpm, self.request_timeout_s, self.breaker_k = max_rpm, float(request_timeout_s), breaker_k
        self.backoff_base_s, self.backoff_cap_s = float(backoff_base_s), float(backoff_cap_s)
        self.burst_n, self.burst_window_s, self.halve_hold_s = burst_n, float(burst_window_s), float(halve_hold_s)
        self.raise_every_s, self.seed = float(raise_every_s), seed

    def line(self, time_scale=None):
        """[F4] time_scale printed (the pool passes its rate control's; the dry-run prints the module's)."""
        return ("[RATE] config: max_rpm %d (one global token bucket, all workers), request timeout %.0f s, circuit breaker"
                " K %d, %d HTTP attempts per invocation (rr's retry loop neutralised), Retry-After honoured (seconds and"
                " HTTP-date; floor %.0f s), else full-jitter backoff base %.0f s cap %.0f s; halve on exhaustion / timeout"
                " / %d 429s in %.0f s (hold %.0f s); +1 per clean %.0f s up to workers; time_scale %r" % (
                    self.max_rpm, self.request_timeout_s, self.breaker_k, MAX_ATTEMPTS, MIN_COOLDOWN_S,
                    self.backoff_base_s, self.backoff_cap_s, self.burst_n, self.burst_window_s, self.halve_hold_s,
                    self.raise_every_s, float(TIME_SCALE if time_scale is None else time_scale)))


def assert_main_thread(what):
    """E-2: reserve / resolve / every journal or store write happens on the main thread only."""
    if threading.current_thread() is not threading.main_thread():
        refuse("%s from a worker thread (%s): only the main thread touches SQLite (E-2)" % (
            what, threading.current_thread().name))


def rr_snapshot():
    return (rr.PROVIDER, rr.JUDGE_MODEL, rr.MAX_TOKENS, rr.TEMPERATURE, rr.AZURE_ENDPOINT, rr.AZURE_KEY)


RR_SNAPSHOT_NAMES = ("PROVIDER", "JUDGE_MODEL", "MAX_TOKENS", "TEMPERATURE", "AZURE_ENDPOINT", "AZURE_KEY")


def rr_changed(snap):
    """The names (never the values) of the rr globals that differ from the snapshot."""
    return [n for n, a, b in zip(RR_SNAPSHOT_NAMES, snap, rr_snapshot()) if a is not b and a != b]


class Ticket:
    """One reserved invocation: the journal seq, the payload sha and body, the turns, the (match_id, order) booked."""
    __slots__ = ("seq", "sha", "body", "system", "user", "booked", "index")

    def __init__(self, seq, sha, body, system, user, booked=None, index=None):
        self.seq, self.sha, self.body, self.system, self.user = seq, sha, body, system, user
        self.booked, self.index = booked, index


Outcome = collections.namedtuple("Outcome", "kind value http_attempts http_429 elapsed")
# kind: "returned" (value = the call_full tuple), "raised" (value = the Exception), "not_sent" (value = the note),
#       "raised_base" (value = a BaseException that is not an Exception, e.g. SystemExit raised inside send)
NOT_SENT = "DAY ROLLOVER: not sent"


class TwoPhase:
    """The E-2 contract (module docstring). A driver subclasses it; the pool calls nothing else."""
    max_inflight = 1
    http_cap = None

    def reserve(self, system, user):
        raise NotImplementedError

    def send(self, ticket):
        raise NotImplementedError

    def resolve(self, ticket, outcome):
        raise NotImplementedError

    def http_booked(self):
        return 0


# ── the wire: every HTTP attempt ────────────────────────────────────────────────────────────────────────────────────

class WireRefused(RuntimeError):
    """A request whose bytes are not the ticket's body (or one from a thread with no ticket): refused BEFORE it leaves."""


class HttpCapReached(RuntimeError):
    """The HTTP-attempt cap: refused BEFORE the attempt leaves (a clean stop of the pool)."""


class PoolAborted(RuntimeError):
    """[F3] The launch was interrupted: no token is granted and no HTTP attempt leaves after the abort flag (never
    retried; call_judge_full does not catch it)."""


class PoolRetry(RuntimeError):
    """A retryable failure of ONE HTTP attempt, re-raised past call_judge_full's except clauses (it catches HTTPError,
    URLError, TimeoutError and ConnectionError; this is none of them): rr does not retry, the pool does."""

    def __init__(self, kind, cause, retry_after=None):
        super().__init__("%s: %s" % (kind, cause))
        self.kind, self.cause, self.retry_after = kind, cause, retry_after
        self.code = getattr(cause, "code", None)


def retry_after_seconds(headers, now=None):
    """Retry-After in seconds: the delta-seconds form or the HTTP-date form (RFC 9110 10.2.3); None when absent or
    unreadable. A date in the past reads as 0."""
    try:
        v = headers.get("Retry-After") if headers is not None else None
    except Exception:  # noqa: BLE001
        return None
    if v is None or not str(v).strip():
        return None
    v = str(v).strip()
    try:
        return max(0.0, float(v))
    except ValueError:
        pass
    if MUTANT == "retry_after_date_ignored":
        return None
    try:
        d = email.utils.parsedate_to_datetime(v)
    except (TypeError, ValueError, IndexError):
        return None
    if d is None:
        return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return max(0.0, (d - (now or datetime.now(timezone.utc))).total_seconds())


class _Buffered:
    """The response of one attempt, read INSIDE the wrapper (so a read timeout is the wrapper's): what rr uses of it."""

    def __init__(self, body, headers, status):
        self._body, self.headers, self.status = body, headers, status

    def read(self, *a):
        b, self._body = self._body, b""
        return b

    def getcode(self):
        return self.status

    def close(self):
        return None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class WireCounter:
    """The urlopen wrapper (module docstring, RATE CONTROL (a)-(g))."""

    def __init__(self, rate, cfg, http_cap_remaining=None):
        self.tls = threading.local()
        self.rate, self.cfg = rate, cfg
        self.cap_remaining = http_cap_remaining
        self.real = None
        self.lock = threading.Lock()
        self.total = 0

    def install(self):
        if isinstance(getattr(urllib.request.urlopen, "__self__", None), WireCounter):
            refuse("[POOL] a previous pool's wire is still installed (an interrupted launch whose workers are still"
                   " inside an HTTP attempt): refused before any reservation")
        self.real = urllib.request.urlopen
        urllib.request.urlopen = self.urlopen

    def uninstall(self):
        if self.real is not None and urllib.request.urlopen == self.urlopen:
            urllib.request.urlopen = self.real
        self.real = None

    def begin(self, sha):
        self.tls.sha, self.tls.n, self.tls.n429 = sha, 0, 0

    def end(self):
        r = (getattr(self.tls, "n", 0), getattr(self.tls, "n429", 0))
        self.tls.sha = None
        return r

    def urlopen(self, req, *a, **k):
        host = endpoint_host(getattr(req, "full_url", None) or req)
        if not is_loopback(host):
            bad = live_guard_reasons(self.rate.time_scale)
            if bad:             # [F4] the backstop: a non-loopback request under a selftest setting never leaves
                raise WireRefused("[RATE] LIVE GUARD: a request to %s under %s: refused BEFORE it left" % (host, bad))
        exp = getattr(self.tls, "sha", None)
        data = getattr(req, "data", None)
        if exp is None or data is None or hashlib.sha256(bytes(data)).hexdigest() != exp:
            raise WireRefused("[POOL] WIRE: a request whose bytes are not the ticket's body (ticket sha %s): refused BEFORE"
                              " it left" % exp)
        with self.lock:
            if self.cap_remaining is not None and self.total + 1 > self.cap_remaining and MUTANT != "http_cap_off":
                raise HttpCapReached("[POOL] HTTP-ATTEMPT CAP: %d attempt(s) this launch reach the journal's remaining"
                                     " %d: refused BEFORE the attempt left" % (self.total, self.cap_remaining))
            self.total += 1
        self.rate.wait_gate()
        self.rate.acquire()         # [F1] the grant: no pause in force and >= one interval since the last grant
        self.tls.n += 1
        if MUTANT == "rr_retries_live":
            try:
                return self.real(req, *a, **k)
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    self.tls.n429 += 1
                raise
        k2 = dict(k)
        if MUTANT != "no_request_timeout":
            given = k2.get("timeout")
            k2["timeout"] = min(float(given), self.cfg.request_timeout_s) if isinstance(given, (int, float)) \
                else self.cfg.request_timeout_s
        try:
            resp = self.real(req, *a, **k2)
            try:
                body = resp.read()
                headers, status = resp.headers, getattr(resp, "status", 200)
            finally:
                resp.close()
        except urllib.error.HTTPError as e:
            if e.code == 429:
                self.tls.n429 += 1
                ra = retry_after_seconds(getattr(e, "headers", None))
                self.rate.on_failure("429", ra)
                raise PoolRetry("429", e, ra)
            if e.code in RETRYABLE_HTTP:
                self.rate.on_failure("http%d" % e.code)
                raise PoolRetry("http%d" % e.code, e)
            self.rate.on_ok()
            raise
        except (socket.timeout, TimeoutError) as e:
            self.rate.on_failure("timeout")
            raise PoolRetry("timeout", e)
        except urllib.error.URLError as e:
            kind = "timeout" if isinstance(getattr(e, "reason", None), (socket.timeout, TimeoutError)) else "network"
            self.rate.on_failure(kind)
            raise PoolRetry(kind, e)
        except ConnectionError as e:
            self.rate.on_failure("network")
            raise PoolRetry("network", e)
        self.rate.on_ok()
        return _Buffered(body, headers, status)


# ── the rate control ────────────────────────────────────────────────────────────────────────────────────────────────

class RateControl:
    """The global cool-down gate, the global token bucket, the adaptive in-flight bound, the RATE STOP and the circuit
    breaker (module docstring). Any thread may report; the main thread flushes the [RATE] lines. time_scale:
    SELFTEST-ONLY (every wall wait x time_scale; recorded durations unscaled)."""

    def __init__(self, workers, cfg, time_scale=1.0):
        self.workers, self.cfg, self.time_scale = int(workers), cfg, float(time_scale)
        self.bound = int(workers)
        self.lock = threading.Lock()
        self.pace_lock = threading.Lock()   # [F1] serialises the token takers; on_failure never takes it
        self.last_grant = -1e18             # [F1] the ACTUAL instant of the previous grant
        self.waiting = 0                    # [F1] threads inside acquire (the RC1b witness, recorded at each pause)
        self.pause_windows = []             # [F1] (set_at, pause_until, waiting_at_set): the instant each pause is SET
        self.abort_ev = threading.Event()   # [F3] the interrupt: set by abort() under the lock
        self.aborted_at = None
        self.rng = random.Random(cfg.seed)
        t = self._now()
        self.pause_until = 0.0
        self.pauses = []            # (kind, retry_after, ceiling, pause_s)
        self.backoff_k = 0          # consecutive failures (the backoff exponent)
        self.consec = 0             # consecutive timeouts / 429s (the breaker)
        self.recent429 = collections.deque()
        self.last_event = t         # the last 429 / timeout
        self.last_halve = -1e18
        self.last_raise = t
        self.bucket_next = 0.0
        self.tls = threading.local()
        self.attempt_times = []     # monotonic time of every attempt's token (the max_rpm witness)
        self.events = []            # (kind, detail)
        self.bounds = [self.bound]
        self.exhausted = 0
        self.exhausted_at_1 = 0
        self.breaker_msg = None
        self._lines = []

    def _now(self):
        return time.perf_counter()      # [F1] sub-microsecond and monotonic (time.monotonic ticks at 15.6 ms here)

    def _wait_until(self, t):
        """Sleep until t or the abort flag [F3], whichever comes first (the caller re-checks both)."""
        while True:
            rem = t - self._now()
            if rem <= 0 or self.abort_ev.is_set():
                return
            self.abort_ev.wait(min(rem, 0.25))

    def _check_abort(self):
        if self.abort_ev.is_set():
            raise PoolAborted("[POOL] interrupted: the abort flag is set; no HTTP attempt leaves after it")

    def abort(self):
        """[F3] The interrupt: after this no token is granted (the flag is set under the rate lock, where grants are
        made) and every wait wakes."""
        with self.lock:
            if self.aborted_at is None:
                self.aborted_at = self._now()
            if MUTANT != "abort_ignored":
                self.abort_ev.set()

    # (c) the global gate
    def wait_gate(self):
        if MUTANT == "gate_per_worker":
            self._wait_until(getattr(self.tls, "pause_until", 0.0))
            self._check_abort()
            return
        while True:
            self._check_abort()
            with self.lock:
                t = self.pause_until
            if t <= self._now():
                return
            self._wait_until(t)

    # (d) the global token bucket (capacity 1): [F1] one serialised token taker
    def acquire(self):
        interval = 60.0 / self.cfg.max_rpm * self.time_scale
        with self.lock:
            self.waiting += 1
        try:
            if MUTANT == "bucket_per_worker":           # the build's per-worker schedule (N workers x max_rpm)
                t = max(self._now(), getattr(self.tls, "bucket_next", 0.0))
                self.tls.bucket_next = t + interval
                self._wait_until(t)
                with self.lock:
                    self._check_abort()
                    self.attempt_times.append(self._now())
                return
            if MUTANT == "bucket_by_schedule":          # a pre-assigned slot, the pause re-checked after the wake
                with self.lock:
                    t = max(self._now(), self.bucket_next)
                    self.bucket_next = t + interval
                self._wait_until(t)
                while True:
                    with self.lock:
                        self._check_abort()
                        now = self._now()
                        if now >= self.pause_until:
                            self.attempt_times.append(now)
                            return
                        t = self.pause_until
                    self._wait_until(t)
            honour_pause = MUTANT != "gate_before_bucket_only"     # the mutant: the pause read by wait_gate only
            with self.pace_lock:
                while True:
                    with self.lock:
                        self._check_abort()
                        pu = self.pause_until if honour_pause else 0.0
                        now = self._now()
                        if now >= pu and now - self.last_grant >= interval:
                            self.last_grant = now
                            self.attempt_times.append(now)
                            return
                        t = max(pu, self.last_grant + interval)
                    self._wait_until(t)
        finally:
            with self.lock:
                self.waiting -= 1

    # (f) failures
    def _pause(self, kind, retry_after):
        """lock held. -> the pause in unscaled seconds."""
        if retry_after is not None and MUTANT != "gate_ignores_retry_after":
            ceiling, pause = None, max(float(retry_after), MIN_COOLDOWN_S)
        else:
            ceiling = min(self.cfg.backoff_cap_s, self.cfg.backoff_base_s * (2 ** min(self.backoff_k, 30)))
            if MUTANT == "backoff_no_growth":
                ceiling = self.cfg.backoff_base_s
            pause = max(MIN_COOLDOWN_S, self.rng.uniform(0.0, ceiling))
        self.pauses.append((kind, retry_after, ceiling, pause))
        set_at = self._now()
        until = set_at + pause * self.time_scale
        self.pause_windows.append((set_at, until, self.waiting))
        if MUTANT == "gate_per_worker":
            self.tls.pause_until = max(getattr(self.tls, "pause_until", 0.0), until)
        elif until > self.pause_until:
            self.pause_until = until
        return pause

    def on_failure(self, kind, retry_after=None):
        with self.lock:
            pause = self._pause(kind, retry_after)
            self.backoff_k += 1
            now = self._now()
            if kind in ("429", "timeout", "network"):
                self.consec += 1
                self.last_event = now
            self.events.append((kind, retry_after))
            self._lines.append("[RATE] %s (Retry-After %s): the WHOLE pool paused %.1f s" % (
                kind, "absent" if retry_after is None else "%g s" % retry_after, pause))
            if kind == "429":
                self.recent429.append(now)
                while self.recent429 and now - self.recent429[0] > self.cfg.burst_window_s * self.time_scale:
                    self.recent429.popleft()
                if len(self.recent429) >= self.cfg.burst_n:
                    self._halve("a 429 burst (%d HTTP 429s within %.0f s)" % (len(self.recent429),
                                                                              self.cfg.burst_window_s))
            elif kind in ("timeout", "network"):
                self._halve("a %s" % kind)
            if self.consec >= self.cfg.breaker_k and self.breaker_msg is None and MUTANT != "breaker_off":
                self.breaker_msg = ("[RATE] CIRCUIT BREAKER: %d consecutive HTTP attempts timed out or got 429: every"
                                    " worker stops retrying, no further reservation (a clean stop; relaunch to resume)"
                                    % self.consec)
                self._lines.append(self.breaker_msg)

    def on_ok(self):
        with self.lock:
            self.consec = 0
            self.backoff_k = 0

    # adaptive concurrency
    def _halve(self, why, force=False):
        """lock held."""
        now = self._now()
        if MUTANT == "no_halving" or self.bound <= 1:
            return
        if not force and now - self.last_halve < self.cfg.halve_hold_s * self.time_scale:
            return
        old = self.bound
        self.bound = max(1, self.bound // 2)
        self.last_halve = now
        self.bounds.append(self.bound)
        self._lines.append("[RATE] in-flight bound %d -> %d (%s)" % (old, self.bound, why))

    def maybe_raise(self):
        """Main thread, before a reservation: +1 per clean interval (no 429, timeout or halving) up to the workers."""
        if MUTANT == "no_raise":
            return
        with self.lock:
            now = self._now()
            cap = 10 ** 6 if MUTANT == "raise_unbounded" else self.workers
            if self.bound < cap and now - max(self.last_event, self.last_halve, self.last_raise) >= \
                    self.cfg.raise_every_s * self.time_scale:
                old = self.bound
                self.bound += 1
                self.last_raise = now
                self.bounds.append(self.bound)
                self._lines.append("[RATE] in-flight bound %d -> %d (a clean %.0f s; ceiling %d)" % (
                    old, self.bound, self.cfg.raise_every_s, self.workers))

    def on_exhausted(self):
        """Main thread. E-5 (c) / (d). -> a RATE STOP SystemExit (not raised) or None."""
        with self.lock:
            self.exhausted += 1
            if self.bound > 1:
                self._halve("an invocation EXHAUSTED on HTTP 429 (%d this launch)" % self.exhausted, force=True)
                return None
            self.exhausted_at_1 += 1
            self._lines.append("[RATE] invocation EXHAUSTED on HTTP 429 at bound 1 (%d of %d at bound 1)" % (
                self.exhausted_at_1, RATE_STOP_AT_BOUND_1))
            if self.exhausted_at_1 >= RATE_STOP_AT_BOUND_1:
                msg = ("[RATE] RATE STOP: %d invocations exhausted on HTTP 429 at in-flight bound 1 (%d this launch): no"
                       " further reservation; every reserved ticket is recorded first (a clean stop; relaunch to resume)"
                       % (self.exhausted_at_1, self.exhausted))
                self._lines.append(msg)
                return SystemExit(msg)
            return None

    def flush(self, out):
        with self.lock:
            lines, self._lines = self._lines, []
        for s in lines:
            out(s)


# ── E-3 / E-4: the pipeline ─────────────────────────────────────────────────────────────────────────────────────────

def slot_key(slot):
    return (slot["run_id"], slot["match_id"], slot["presentation_order"], slot["draw_index"])


class _InFlight:
    __slots__ = ("ctx", "ticket", "future", "body")

    def __init__(self, ctx, ticket, future, body):
        self.ctx, self.ticket, self.future, self.body = ctx, ticket, future, body


class PostingPool:
    """The pipelined poster (module docstring). prepare(slot) -> (ctx, system, user, body), MAIN thread (the writer's
    scan and schedule checks); finish(ctx, ticket, outcome) -> the drain tuple, MAIN thread. poster(slot) is handed to
    VerdictStore.drain unchanged."""

    def __init__(self, transport, expected, workers, prepare, finish, out=print, rate_cfg=None, time_scale=None):
        if not isinstance(transport, TwoPhase):
            refuse("the pooled path needs a TwoPhase transport (reserve / send / resolve; judge_v2.pool), got %r" %
                   type(transport).__name__)
        if not isinstance(workers, int) or isinstance(workers, bool) or not 1 <= workers <= MAX_INFLIGHT:
            refuse("the pool takes 1 <= workers <= %d, got %r" % (MAX_INFLIGHT, workers))
        if workers > int(transport.max_inflight):
            refuse("workers %d > the journal's max_inflight %d: refused before any post (a journal created at workers 1"
                   " carries max_inflight 1)" % (workers, int(transport.max_inflight)))
        assert_main_thread("PostingPool")
        self.cfg = rate_cfg or RateConfig()
        if not isinstance(self.cfg, RateConfig):
            refuse("rate_cfg must be a judge_v2.pool.RateConfig")
        self.transport, self.workers, self.prepare, self.finish, self.out = transport, workers, prepare, finish, out
        self.expected = list(expected)
        self.keys = [slot_key(s) for s in self.expected]
        self.rate = RateControl(workers, self.cfg, TIME_SCALE if time_scale is None else time_scale)
        # [F4] the live guard, printed on every pooled run, pass or fail; a refusal comes before any reservation
        call_is_rr = getattr(transport, "call_full", None) is rr.call_judge_full
        host = endpoint_host(rr.AZURE_ENDPOINT)
        live = call_is_rr and not is_loopback(host)
        bad = live_guard_reasons(self.rate.time_scale)
        switches = selftest_switches()
        verdict = ("LIVE, REFUSED" if bad else "LIVE, ADMITTED") if live else \
            "not live (an injected call or a loopback endpoint): admitted"
        out("[RATE] live guard: call_full is rejudge_reasoning.call_judge_full %s, endpoint host %s, time_scale %r"
            " (module TIME_SCALE %r), selftest switches %s -> %s" % (
                "yes" if call_is_rr else "no",
                "none" if host is None else ("loopback" if is_loopback(host) else "non-loopback"),
                self.rate.time_scale, float(TIME_SCALE), switches or "none", verdict))
        if live and bad:
            refuse("[RATE] LIVE GUARD: a live launch (rejudge_reasoning.call_judge_full to a non-loopback endpoint) under"
                   " %s: refused before any reservation (TIME_SCALE and every MUTANT are SELFTEST-ONLY)" % bad)
        self.send_lock = threading.Lock()   # [F3] the workers inside an HTTP attempt, and the deferred uninstall
        self.active = 0
        self.uninstall_pending = False
        cap = transport.http_cap
        self.http_cap_remaining = None if cap is None else int(cap) - int(transport.http_booked())
        self.wire = WireCounter(self.rate, self.cfg, self.http_cap_remaining)
        self.rr0 = rr_snapshot()
        self.i = 0
        self.next = 0
        self.inflight = {}
        self.stop = None
        self.max_inflight_seen = 0
        self.reserved = 0
        self.finished = 0
        self.not_sent = 0
        self.closed = False
        self.wire.install()
        self.ex = cf.ThreadPoolExecutor(max_workers=workers, thread_name_prefix="jv2-pool")
        out(self.cfg.line(self.rate.time_scale) + "; HTTP-attempt cap remaining %s" % (
            "none" if self.http_cap_remaining is None else self.http_cap_remaining))

    # ── E-7 ──
    def check_rr(self, when):
        bad = rr_changed(self.rr0)
        if bad:
            refuse("rejudge_reasoning global(s) %s changed %s (E-7: the workers post with the globals the preflight"
                   " checked; values not printed)" % (bad, when))

    def bound(self):
        return self.rate.bound

    # ── the worker ──
    def _send(self, ticket):
        """One invocation: up to MAX_ATTEMPTS HTTP attempts, each ONE call of the transport's send (rr's own retry loop
        is neutralised by the wire: a retryable failure comes back as PoolRetry)."""
        t0 = time.time()
        self.wire.begin(ticket.sha)
        kind, value = None, None
        limit = MAX_ATTEMPTS + (MAX_ATTEMPTS if MUTANT == "resend_exhausted" else 0)
        try:
            if MUTANT == "worker_sets_temperature":
                rr.TEMPERATURE = 0.0
            if MUTANT == "worker_resolves":
                self.transport.resolve(ticket, Outcome("returned", None, 0, 0, 0.0))
            last = None
            for _attempt in range(limit):
                if not self._enter_send():          # [F3] interrupted: no further HTTP attempt
                    kind, value = "raised", PoolAborted("[POOL] interrupted before HTTP attempt %d" % (_attempt + 1))
                    break
                try:
                    r = self.transport.send(ticket)
                    kind, value = ("not_sent", NOT_SENT) if r is NOT_SENT else ("returned", r)
                    break
                except PoolRetry as e:
                    last = e
                    if self.rate.breaker_msg is not None:
                        break
                finally:
                    self._leave_send()
            if kind is None:
                kind, value = "raised", (last.cause if last is not None else RuntimeError("no HTTP attempt"))
        except Exception as e:  # noqa: BLE001
            kind, value = "raised", e
        except BaseException as e:  # noqa: BLE001  (SystemExit inside send: carried to the main thread)
            kind, value = "raised_base", e
        finally:
            n, n429 = self.wire.end()
        return Outcome(kind, value, n, n429, time.time() - t0)

    def _enter_send(self):
        """[F3] A worker enters an HTTP attempt unless the abort flag is set (read under send_lock, where close sets it)."""
        with self.send_lock:
            if self.rate.abort_ev.is_set():
                return False
            self.active += 1
            return True

    def _leave_send(self):
        """[F3] The last worker leaving after an interrupt uninstalls the wire (never earlier: no fallback to rr's loop)."""
        with self.send_lock:
            self.active -= 1
            if self.uninstall_pending and self.active == 0:
                self.wire.uninstall()
                self.uninstall_pending = False

    # ── the main thread ──
    def _wait(self, fut):
        while True:
            try:
                return fut.result(timeout=WAIT_POLL_S)
            except cf.TimeoutError:
                continue

    def _reserve_one(self, j):
        slot = self.expected[j]
        ctx, system, user, body = self.prepare(slot)
        if MUTANT == "send_before_reserve":
            probe = Ticket(None, hashlib.sha256(body).hexdigest(), body, system, user, index=j)
            early = self.ex.submit(self._send, probe)
            self._wait(early)
            ticket = self.transport.reserve(system, user)
            ticket.index = j
            fut = cf.Future()
            fut.set_result(early.result())
            return _InFlight(ctx, ticket, fut, body)
        ticket = self.transport.reserve(system, user)
        ticket.index = j
        if ticket.body != body:
            refuse("slot %s order %s: the reserved ticket's body is not the payload the writer built and scanned (E-2:"
                   " body = rr.payload_bytes asserted equal to the stored body); refused BEFORE the post" % (
                       slot["match_id"], slot["presentation_order"]))
        fut = self.ex.submit(self._send, ticket)
        return _InFlight(ctx, ticket, fut, body)

    def _stop_now(self, e, where):
        self.stop = e
        self.out("[POOL] STOP %s: %s -- no further reservation; %d reserved ticket(s) are recorded first" % (
            where, str(e)[:200], len(self.inflight)))

    def _top_up(self, i):
        while self.stop is None and self.next < len(self.expected):
            self.rate.maybe_raise()
            self.rate.flush(self.out)
            if self.next > i + self.bound() - 1:
                break
            if self.rate.breaker_msg is not None:
                self._stop_now(SystemExit(self.rate.breaker_msg), "at the circuit breaker")
                break
            self.check_rr("before a reservation")
            self.rate.wait_gate()
            j = self.next
            try:
                inf = self._reserve_one(j)
            except SystemExit as e:
                self._stop_now(e, "at reservation %d of %d" % (j + 1, len(self.expected)))
                break
            self.next += 1
            self.reserved += 1
            self.inflight[j] = inf
            if len(self.inflight) > self.max_inflight_seen:
                self.max_inflight_seen = len(self.inflight)
            if len(self.inflight) > self.workers:
                refuse("%d tickets in flight > workers %d (E-3)" % (len(self.inflight), self.workers))

    def poster(self, slot):
        assert_main_thread("the pool's poster")
        i = self.i
        self.i += 1
        key = slot_key(slot)
        if i >= len(self.keys) or key != self.keys[i]:
            refuse("the pool's in-order contract: drain handed slot %s as call %d, the expected key is %s (E-3)" % (
                key, i, self.keys[i] if i < len(self.keys) else "none (past the end)"))
        self._top_up(i)
        self.rate.flush(self.out)
        if i not in self.inflight:
            raise self.stop if self.stop is not None else SystemExit(
                "[POOL] slot %s was never reserved and no stop is recorded (E-3)" % (key,))
        inf = self.inflight.pop(i)
        if MUTANT == "bind_shift" and self.inflight:
            other = self.inflight[max(self.inflight)]
            inf = _InFlight(inf.ctx, inf.ticket, other.future, inf.body)
        outcome = self._wait(inf.future)
        self.transport.resolve(inf.ticket, outcome)
        if MUTANT == "rereserve_errored" and outcome.kind == "raised":
            inf = self._reserve_one(i)
            outcome = self._wait(inf.future)
            self.transport.resolve(inf.ticket, outcome)
        self.finished += 1
        self.rate.flush(self.out)
        if outcome.kind == "not_sent":
            self.not_sent += 1
            if self.stop is None:
                self._stop_now(SystemExit(
                    "[ACCOUNT] DAY ROLLOVER at send: the local date changed after the reservation; the ticket was NOT sent"
                    " (journaled RAISED \"%s\", counted and ledgered); no further reservation in this launch (a clean"
                    " stop; relaunch to resume)" % NOT_SENT), "at a send")
        if outcome.kind == "raised" and isinstance(outcome.value, HttpCapReached) and self.stop is None:
            self._stop_now(SystemExit(str(outcome.value)), "at the HTTP-attempt cap")
        if outcome.kind == "raised" and exhausted_429(outcome):
            st = self.rate.on_exhausted()
            self.rate.flush(self.out)
            if st is not None and self.stop is None:
                self._stop_now(st, "at the RATE STOP")
        if self.rate.breaker_msg is not None and self.stop is None:
            self._stop_now(SystemExit(self.rate.breaker_msg), "at the circuit breaker")
        if outcome.kind == "raised_base":
            raise outcome.value
        return self.finish(inf.ctx, inf.ticket, outcome)

    def close(self, interrupted=False):
        """Resolve (journal only) any ticket still in flight after an exception, unless interrupted; stop the workers;
        uninstall the wire counter. Returns the number resolved here."""
        if self.closed:
            return 0
        self.closed = True
        n = 0
        try:
            if not interrupted:
                for j in sorted(self.inflight):
                    inf = self.inflight.pop(j)
                    outcome = self._wait(inf.future)
                    self.transport.resolve(inf.ticket, outcome)
                    n += 1
                if n:
                    self.out("[POOL] %d in-flight ticket(s) resolved in the journal after the stop (not recorded in the"
                             " store; their slots stay pending)" % n)
        finally:
            if interrupted:
                # [F3] the abort flag first (no grant, no new attempt after it); the wire stays installed while a
                # worker is inside an attempt, and the last one out uninstalls it
                with self.send_lock:
                    self.rate.abort()
                    active = self.active
                    if active:
                        self.uninstall_pending = True
                    else:
                        self.wire.uninstall()
                self.ex.shutdown(wait=False, cancel_futures=True)
                self.out("[POOL] INTERRUPTED: abort set; %d worker(s) inside an HTTP attempt finish it, no further"
                         " attempt leaves; the in-flight tickets become ORPHANs at the relaunch" % active)
            else:
                self.ex.shutdown(wait=True, cancel_futures=True)
                self.wire.uninstall()
            self.rate.flush(self.out)
        return n

    def line(self):
        return ("[POOL] workers %d: reserved %d, recorded %d, max in flight %d, bound now %d (history %s), HTTP attempts"
                " %d, pauses %d, exhausted-429 %d, not sent %d, breaker %s" % (
                    self.workers, self.reserved, self.finished, self.max_inflight_seen, self.rate.bound,
                    self.rate.bounds, self.wire.total, len(self.rate.pauses), self.rate.exhausted, self.not_sent,
                    "TRIPPED" if self.rate.breaker_msg else "closed"))


def exhausted_429(outcome):
    """E-5 (c): the invocation RAISED HTTP 429 after MAX_ATTEMPTS HTTP attempts (the pool's retries; rr's are
    neutralised)."""
    return (outcome.kind == "raised" and getattr(outcome.value, "code", None) == 429 and
            (outcome.http_attempts or 0) >= MAX_ATTEMPTS)


# ── E-6: the day-ledger lock ────────────────────────────────────────────────────────────────────────────────────────

class LedgerLock:
    """An exclusive lock file beside the day ledgers (judgebench_side.LedgerLock, 85a2d9f, the same file name): every
    day-ledger append of a judge_v2 driver takes it, so two posting processes never lose a row (finding F-4)."""

    def __init__(self, ledger_dir, timeout=120):
        self.path = os.path.join(ledger_dir, LEDGER_LOCK_NAME)
        self.timeout = timeout
        self.fd = None

    def __enter__(self):
        t0 = time.time()
        while True:
            try:
                self.fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                return self
            except FileExistsError:
                if time.time() - t0 > self.timeout:
                    refuse("the ledger lock %s is held for more than %d s; refused (remove it only if no poster runs)"
                           % (self.path, self.timeout))
                time.sleep(0.2)

    def __exit__(self, *exc):
        os.close(self.fd)
        os.remove(self.path)
        return False
