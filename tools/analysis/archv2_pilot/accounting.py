"""The pilot's accounting, ON the accepted-tests ledger (accepted_tests_ledger, imported read-only; its file is NOT edited:
its blob 4e9db106 is pinned by the CANARY / TRACE READY reviews, and adding a test to its CEILINGS would change guard()'s
combined statement (iii) for the two accepted tests).

THE NUMBERS OF RECORD (the author's decision 2026-09-24, Amendment 18, L15909-L15911; the registration's Accounting line):
  (i)   the per-test ceiling: ARCH-V2-PILOT-K46 8,000 calls (AUTHOR_HARD_CAP; nothing may exceed it);
  (ii)  the 4,000-match rule (CONTEXT section 4 rule 5): (posted + this launch) / 2, rounded up, <= 4,000;
  (iii) THE DAY CAP of the POSTING DATE: every row of day_calls_<day>.json (all tests) + this launch <= 14,000.
All three are printed on every launch (the ledger's FULL path), pass or refuse; a breach refuses, never trims.

[ADDED on READY 65a9173 K1 (HIGH), the INDUCE runner's fix: WRITE-AHEAD INVOCATION ACCOUNTING.]
  JOURNAL  <store>.invocations.db, an append-only SQLite file of this package (never a corpus, view or verdict DB):
           invocation (seq, ts, day, launch, match_id, order, payload_sha256, state 'PENDING') is INSERTED AND COMMITTED
           BEFORE every call_full; resolution (seq, 'RETURNED' / 'RAISED' / 'ORPHAN') after it. UPDATE / DELETE abort.
  TRIGGERS act BEFORE the post: an invocation beyond AUTHOR_HARD_CAP (8,000) aborts; an invocation while an earlier one
           is unresolved aborts (orphans are resolved first).
  POSTS    are counted in a holder (`posts["n"]`, incremented before the call) that the launch's `finally` reads, so the
           day ledger gets every post (KeyboardInterrupt included).
  RELAUNCH reconcile(): every unresolved invocation (posted, then the process died) is an ORPHAN, resolved as such and
           disclosed; per posting day, the ledger's rows for the test are compared with the journal's invocations: a
           ledger BEHIND is caught up by one row labelled "reconciled after crash" on THAT day; a ledger AHEAD refuses.
           Then (the INDUCE ruling 1 (b) equality) the ledger's count for the test must EQUAL the journal's invocations,
           at the start and at the end of every launch, else REFUSED.
  own      guard_day's own = max(journal invocations, store attempt rows, ledger rows).
[ADDED 2026-09-25 (the day-rollover check, found in the JudgeBench runner by a reviewer; insertion only).] THE POSTING DAY
  is fixed ONCE at the launch's start (pilot.launch -> posting_day_ok); the guard (iii), every journal row's `day` and the
  end-of-launch ledger append (day=) all carry THAT day, so a launch's journal and ledger always agree per day and the
  reconciliation never double-counts. What a launch crossing local midnight did before this bracket: it kept posting and
  booked the posts made after midnight to the START day's ledger (the posting date of record is the new day, whose ledger
  then under-counts; the guard's (iii) of the new day never saw them). NOW wrap_call REFUSES every post once the local
  date differs from the launch's day (SystemExit before the journal row, before posts["n"], before the post): a CLEAN STOP
  -- the writer's drain propagates SystemExit, the launch's finally ledgers the posts made so far on the start day, and a
  relaunch (on the new day, its own guard (iii)) resumes the pending slots. MUTANT "rollover_off" skips the check.
[ADDED 2026-09-25 after the pilot-12 transport incident (insertion only).] PRIOR journals: reconcile() and the equality
  check take `prior` ({"invocations", "per_day"}: the invocations booked by RETIRED stores' journals of this test, read
  and sha-pinned by pilot.prior_journals_state) on the JOURNAL side, so a new store's launch reconciles against a ledger
  that already carries the retired store's rows (never "AHEAD", never a catch-up duplicate).
[ADDED 2026-09-25 by JV2-PARALLEL-POSTING (registered bf9d80b, docs/judge_v2_program.md L19096-L19239, E-2 / E-6),
  insertion only; NOTHING ABOVE CHANGES AT workers 1.] JOURNAL v2 and the TWO-PHASE TRANSPORT (judge_v2.pool's contract):
  - A journal created at workers 1 (Journal.open without max_inflight) is created with TODAY'S DDL TEXT and NO new meta
    row (byte-inert; its max_inflight is read as 1). A journal created for a pooled launch (max_inflight given, the
    registration's maximum judge_v2.pool.MAX_INFLIGHT = 16) is JOURNAL v2: meta 'max_inflight'; the trigger
    invocation_unresolved aborts when (unresolved count) >= meta.max_inflight; the resolution carries the nullable
    http_attempts / http_429 (E-5 (a)); and [BUILDER'S ADDITION, disclosed] a table launch_bound (launch, ts, workers)
    written once per pooled launch, with a trigger invocation_launch_bound that aborts when (unresolved count) >= the
    launch's workers, so the launch's N itself (not only the registration's maximum) is enforced at the DATABASE level.
  - Journal.begin_launch(launch, workers) REFUSES before any post a launch with workers > max_inflight, or workers > 1 on
    a journal created at workers 1.
  - TwoPhaseCall splits wrap_call's one callable (which stays, verbatim, the workers-1 path) into reserve (MAIN thread:
    the rollover check, the slot, the PENDING row committed -- the cap and unresolved triggers fire here -- posts["n"] += 1,
    the body), send (WORKER thread: no sqlite, no rr global; the local date re-checked, NOT_SENT without a post on a
    change; then call_full) and resolve (MAIN thread: RETURNED / RAISED, a send-time rollover RAISED "DAY ROLLOVER: not
    sent", with the wire counter's HTTP attempts and 429s).
  - E-6: every day-ledger append (append(), hence reconcile's catch-up and the launch's finally) takes judge_v2.pool's
    LedgerLock (a cross-process lock file beside the ledgers, JudgeBench's file name), closing finding F-4's lost-row
    hazard; the ledger's bytes are unchanged (the lock file is removed after the append).
"""
import hashlib
import os
import threading
import time
from datetime import datetime, timezone

import accepted_tests_ledger as atl
from judge_v2 import pool as POOL
from judge_v2._base import rr

DAY_CAP = 14000
AUTHOR_HARD_CAP = 8000
DAY_TESTS = {"ARCH-V2-PILOT-K46": AUTHOR_HARD_CAP}
MUTANT = None       # SELFTEST-ONLY: "journal_after_post", "rollover_off"; [JV2-PARALLEL-POSTING] "rollover_send_off",
#                     "posts_at_completion", "orphans_returned", "cap_in_workers", "unresolved_trigger_off",
#                     "body_prev_reserve", "body_prev_send" (judge_v2/pool_selftest.py)


def day_total(ledger_dir, day):
    return sum(int(r["calls"]) for r in atl._rows(atl.day_ledger_path(ledger_dir, day)))


def test_day_rows(test, ledger_dir):
    """{day: calls} of the test's rows in the day_calls_<day>.json files (the night file carries no row of this test)."""
    out = {}
    for f in atl.ledger_files(ledger_dir):
        b = os.path.basename(f)
        if not b.startswith("day_calls_"):
            n = sum(int(r["calls"]) for r in atl._rows(f) if r.get("test") == test)
            if n:
                raise SystemExit("[ACCOUNT] %s carries %d calls of %s: unexpected" % (f, n, test))
            continue
        day = b[len("day_calls_"):-len(".json")]
        n = sum(int(r["calls"]) for r in atl._rows(f) if r.get("test") == test)
        if n:
            out[day] = n
    return out


def guard_day(test, planned, own_store_calls, ledger_dir, day=None, what="launch", refuse=True, out=print,
              own_journal=0):
    if test not in DAY_TESTS:
        raise SystemExit("[ACCOUNT] unknown day-capped test %r" % test)
    if DAY_TESTS[test] > AUTHOR_HARD_CAP:
        raise SystemExit("[ACCOUNT] the ceiling of %s exceeds the author's hard %d" % (test, AUTHOR_HARD_CAP))
    day = day or time.strftime("%Y-%m-%d")
    own_l = atl.ledger_calls(test, ledger_dir)
    own = max(int(own_store_calls), own_l, int(own_journal))
    after = own + int(planned)
    matches_after = after // 2 + after % 2
    today = day_total(ledger_dir, day)
    nums = dict(test=test, planned=int(planned), own=own, own_store=int(own_store_calls), own_ledger=own_l,
                own_journal=int(own_journal), ceiling=DAY_TESTS[test], own_after=after, matches_after=matches_after,
                match_rule=atl.MATCH_RULE, day=day, day_total=today, day_after=today + int(planned), day_cap=DAY_CAP,
                day_ledger=os.path.abspath(atl.day_ledger_path(ledger_dir, day)))
    breaches = []
    if after > nums["ceiling"]:
        breaches.append("(i) %s would reach %d calls > its ceiling %d" % (test, after, nums["ceiling"]))
    if matches_after > atl.MATCH_RULE:
        breaches.append("(ii) %d matches > the %d-match rule" % (matches_after, atl.MATCH_RULE))
    if nums["day_after"] > DAY_CAP:
        breaches.append("(iii) day %s: %d posted + this launch %d = %d > %d" % (day, today, planned, nums["day_after"], DAY_CAP))
    out("[ACCOUNT] %s (%s): (i) own %d (journal %d, store %d, ledgers %d) + %d = %d of %d | (ii) matches %d of %d | (iii)"
        " day %s: %d + %d = %d of %d | ledger of record: %s -> %s" % (
            test, what, own, own_journal, own_store_calls, own_l, planned, after, nums["ceiling"], matches_after,
            atl.MATCH_RULE, day, today, planned, nums["day_after"], DAY_CAP, nums["day_ledger"],
            "OK" if not breaches else "REFUSED: " + "; ".join(breaches)))
    nums["breaches"] = breaches
    if breaches and refuse:
        raise SystemExit("[ACCOUNT] REFUSED, not trimmed (0 calls posted): " + "; ".join(breaches))
    return nums


def append(test, launch, calls, ledger_dir, day=None):
    with POOL.LedgerLock(ledger_dir):       # [JV2-PARALLEL-POSTING E-6] cross-process; the ledger bytes are unchanged
        return atl.append(test, launch, calls, ledger_dir, day=day)


def local_day():
    """The local date, the same clock as pilot.posting_day_ok and guard_day's default (time.strftime)."""
    return time.strftime("%Y-%m-%d")


# ── the write-ahead journal (K1) ────────────────────────────────────────────────────────────

def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _ddl(cap, max_inflight=None):
    """max_inflight None: TODAY'S DDL TEXT (a workers-1 journal, byte-inert). Otherwise JOURNAL v2 (module docstring)."""
    if max_inflight is not None:
        return _ddl_v2(cap)
    s = """
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE invocation (seq INTEGER PRIMARY KEY, ts TEXT NOT NULL, day TEXT NOT NULL, launch TEXT NOT NULL,
    match_id TEXT NOT NULL, presentation_order INTEGER NOT NULL, payload_sha256 TEXT NOT NULL,
    state TEXT NOT NULL CHECK (state = 'PENDING'));
CREATE TABLE resolution (seq INTEGER PRIMARY KEY REFERENCES invocation(seq), ts TEXT NOT NULL,
    outcome TEXT NOT NULL CHECK (outcome IN ('RETURNED', 'RAISED', 'ORPHAN')), note TEXT);
CREATE TRIGGER invocation_cap BEFORE INSERT ON invocation WHEN (SELECT COUNT(*) FROM invocation) >= %(cap)d
    BEGIN SELECT RAISE(ABORT, 'the author''s hard cap of %(cap)d invocations is reached: refused BEFORE the post'); END;
CREATE TRIGGER invocation_unresolved BEFORE INSERT ON invocation WHEN EXISTS (SELECT 1 FROM invocation i WHERE NOT EXISTS
    (SELECT 1 FROM resolution r WHERE r.seq = i.seq))
    BEGIN SELECT RAISE(ABORT, 'an earlier invocation is unresolved (an orphan): reconcile first'); END;
CREATE TRIGGER resolution_needs_invocation BEFORE INSERT ON resolution WHEN NOT EXISTS (SELECT 1 FROM invocation i WHERE
    i.seq = NEW.seq) BEGIN SELECT RAISE(ABORT, 'no such invocation'); END;
""" % {"cap": int(cap)}
    for t in ("meta", "invocation", "resolution"):
        s += ("CREATE TRIGGER %(t)s_no_update BEFORE UPDATE ON %(t)s BEGIN SELECT RAISE(ABORT, 'append-only'); END;\n"
              "CREATE TRIGGER %(t)s_no_delete BEFORE DELETE ON %(t)s BEGIN SELECT RAISE(ABORT, 'append-only'); END;\n"
              ) % {"t": t}
    return s


def _ddl_v2(cap):
    """JOURNAL v2 (JV2-PARALLEL-POSTING E-2): the unresolved bound is meta.max_inflight (and the launch's own workers,
    launch_bound); the resolution carries the wire counter's http_attempts / http_429. A missing bound reads as 1."""
    unresolved = "(SELECT COUNT(*) FROM invocation i WHERE NOT EXISTS (SELECT 1 FROM resolution r WHERE r.seq = i.seq))"
    max_inf = "COALESCE((SELECT CAST(value AS INTEGER) FROM meta WHERE key = 'max_inflight'), 1)"
    s = """
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE invocation (seq INTEGER PRIMARY KEY, ts TEXT NOT NULL, day TEXT NOT NULL, launch TEXT NOT NULL,
    match_id TEXT NOT NULL, presentation_order INTEGER NOT NULL, payload_sha256 TEXT NOT NULL,
    state TEXT NOT NULL CHECK (state = 'PENDING'));
CREATE TABLE resolution (seq INTEGER PRIMARY KEY REFERENCES invocation(seq), ts TEXT NOT NULL,
    outcome TEXT NOT NULL CHECK (outcome IN ('RETURNED', 'RAISED', 'ORPHAN')), note TEXT,
    http_attempts INTEGER, http_429 INTEGER);
CREATE TABLE launch_bound (launch TEXT PRIMARY KEY, ts TEXT NOT NULL, workers INTEGER NOT NULL CHECK (workers >= 1));
CREATE TRIGGER resolution_needs_invocation BEFORE INSERT ON resolution WHEN NOT EXISTS (SELECT 1 FROM invocation i WHERE
    i.seq = NEW.seq) BEGIN SELECT RAISE(ABORT, 'no such invocation'); END;
CREATE TRIGGER launch_bound_max BEFORE INSERT ON launch_bound WHEN NEW.workers > %(max_inf)s
    BEGIN SELECT RAISE(ABORT, 'a launch''s workers above the journal''s max_inflight'); END;
""" % {"max_inf": max_inf}
    if MUTANT != "cap_in_workers":
        s += ("CREATE TRIGGER invocation_cap BEFORE INSERT ON invocation WHEN (SELECT COUNT(*) FROM invocation) >= %(cap)d\n"
              "    BEGIN SELECT RAISE(ABORT, 'the author''s hard cap of %(cap)d invocations is reached: refused BEFORE the"
              " post'); END;\n") % {"cap": int(cap)}
    if MUTANT != "unresolved_trigger_off":
        s += ("CREATE TRIGGER invocation_unresolved BEFORE INSERT ON invocation WHEN %(u)s >= %(m)s\n"
              "    BEGIN SELECT RAISE(ABORT, 'max_inflight invocations are unresolved (orphans are reconciled first):"
              " refused BEFORE the post'); END;\n"
              "CREATE TRIGGER invocation_launch_bound BEFORE INSERT ON invocation WHEN %(u)s >= COALESCE((SELECT workers"
              " FROM launch_bound b WHERE b.launch = NEW.launch), 1)\n"
              "    BEGIN SELECT RAISE(ABORT, 'the launch''s in-flight bound (its workers) is reached: refused BEFORE the"
              " post'); END;\n") % {"u": unresolved, "m": max_inf}
    for t in ("meta", "invocation", "resolution", "launch_bound"):
        s += ("CREATE TRIGGER %(t)s_no_update BEFORE UPDATE ON %(t)s BEGIN SELECT RAISE(ABORT, 'append-only'); END;\n"
              "CREATE TRIGGER %(t)s_no_delete BEFORE DELETE ON %(t)s BEGIN SELECT RAISE(ABORT, 'append-only'); END;\n"
              ) % {"t": t}
    return s


class Journal:
    """The write-ahead invocation journal of one store (module docstring)."""

    def __init__(self, conn, path):
        self.conn, self.path = conn, path
        # [JV2-PARALLEL-POSTING] a journal created at workers 1 carries no max_inflight row: its bound is 1 (v1)
        row = conn.execute("SELECT value FROM meta WHERE key='max_inflight'").fetchone()
        self.max_inflight = int(row[0]) if row is not None else 1
        self.version = 2 if row is not None else 1

    @classmethod
    def open(cls, path, cap=AUTHOR_HARD_CAP, create=False, max_inflight=None):
        """[JV2-PARALLEL-POSTING] max_inflight: None creates TODAY'S journal (v1, byte-inert); an int in
        [2, judge_v2.pool.MAX_INFLIGHT] creates JOURNAL v2. On an existing journal it must be None or equal the
        journal's own."""
        from archv2_arena import ro as aro
        if int(cap) > AUTHOR_HARD_CAP:
            raise SystemExit("[ACCOUNT] a journal cap %d above the author's hard %d is refused" % (cap, AUTHOR_HARD_CAP))
        if max_inflight is not None and (not isinstance(max_inflight, int) or isinstance(max_inflight, bool) or
                                         not 2 <= max_inflight <= POOL.MAX_INFLIGHT):
            raise SystemExit("[ACCOUNT] a journal max_inflight %r outside [2, %d] is refused" % (
                max_inflight, POOL.MAX_INFLIGHT))
        exists = os.path.exists(path)
        if not exists and not create:
            raise SystemExit("[ACCOUNT] the invocation journal %s does not exist" % path)
        conn = aro.REAL_CONNECT(os.path.abspath(path))
        conn.execute("PRAGMA journal_mode=DELETE")
        if not exists:
            conn.executescript(_ddl(cap, max_inflight))
            conn.execute("INSERT INTO meta VALUES ('cap', ?)", (str(int(cap)),))
            conn.execute("INSERT INTO meta VALUES ('created', ?)", (_now(),))
            if max_inflight is not None:
                conn.execute("INSERT INTO meta VALUES ('max_inflight', ?)", (str(int(max_inflight)),))
                conn.execute("INSERT INTO meta VALUES ('schema', 'journal-v2 (JV2-PARALLEL-POSTING)')")
            conn.commit()
        got = conn.execute("SELECT value FROM meta WHERE key='cap'").fetchone()
        if got is None or int(got[0]) != int(cap):
            conn.close()
            raise SystemExit("[ACCOUNT] the journal %s carries cap %r, not %d" % (path, got, cap))
        j = cls(conn, path)
        if exists and max_inflight is not None and j.max_inflight != max_inflight:
            conn.close()
            raise SystemExit("[ACCOUNT] the journal %s carries max_inflight %d, not %d" % (path, j.max_inflight,
                                                                                            max_inflight))
        return j

    def begin_launch(self, launch, workers, pooled=None):
        """[JV2-PARALLEL-POSTING E-2] REFUSED before any post: workers > the journal's max_inflight (a journal created at
        workers 1: 1), or a POOLED launch (workers > 1, or workers 1 under a rate configuration) on a journal created at
        workers 1 (its resolution has no http_attempts / http_429). A pooled launch with workers > 1 books its bound in
        launch_bound (read by invocation_launch_bound)."""
        if not isinstance(workers, int) or isinstance(workers, bool) or workers < 1:
            raise SystemExit("[ACCOUNT] workers %r" % (workers,))
        pooled = (workers > 1) if pooled is None else bool(pooled)
        if pooled and self.version == 1 and workers == 1:
            raise SystemExit("[ACCOUNT] a POOLED launch (a rate configuration at workers 1) on a journal created at"
                             " workers 1 (no http_attempts / http_429 columns): REFUSED before any post")
        if workers > self.max_inflight:
            raise SystemExit("[ACCOUNT] workers %d > the journal's max_inflight %d (%s): REFUSED before any post" % (
                workers, self.max_inflight, "a journal created at workers 1 carries no max_inflight: one call in flight"
                if self.version == 1 else "journal v2"))
        if workers > 1:
            self.conn.execute("INSERT INTO launch_bound VALUES (?,?,?)", (launch, _now(), int(workers)))
            self.conn.commit()

    def close(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def pending(self, launch, match_id, order, sha, day):
        """INSERT + COMMIT the PENDING row; the triggers refuse BEFORE any post."""
        try:
            cur = self.conn.execute("INSERT INTO invocation (ts, day, launch, match_id, presentation_order, payload_sha256,"
                                    " state) VALUES (?,?,?,?,?,?, 'PENDING')", (_now(), day, launch, match_id, int(order), sha))
            self.conn.commit()
        except Exception as e:  # noqa: BLE001  (sqlite3 errors from the triggers)
            self.conn.rollback()
            raise SystemExit("[ACCOUNT] the invocation journal REFUSES the invocation BEFORE any post: %s" % e)
        return cur.lastrowid

    def resolve(self, seq, outcome, note=None, http_attempts=None, http_429=None):
        if self.version == 1:
            self.conn.execute("INSERT INTO resolution VALUES (?,?,?,?)", (seq, _now(), outcome, note))
        else:
            self.conn.execute("INSERT INTO resolution (seq, ts, outcome, note, http_attempts, http_429) VALUES"
                              " (?,?,?,?,?,?)", (seq, _now(), outcome, note, http_attempts, http_429))
        self.conn.commit()

    def state(self):
        c = self.conn
        n = c.execute("SELECT COUNT(*) FROM invocation").fetchone()[0]
        per_day = dict(c.execute("SELECT day, COUNT(*) FROM invocation GROUP BY day").fetchall())
        unresolved = [r[0] for r in c.execute("SELECT seq FROM invocation i WHERE NOT EXISTS (SELECT 1 FROM resolution r"
                                              " WHERE r.seq = i.seq) ORDER BY seq")]
        by = dict(c.execute("SELECT outcome, COUNT(*) FROM resolution GROUP BY outcome").fetchall())
        launches = c.execute("SELECT COUNT(DISTINCT launch) FROM invocation").fetchone()[0]
        return {"invocations": int(n), "per_day": per_day, "unresolved": unresolved, "by_outcome": by,
                "launches": int(launches)}

    def resolve_orphans(self, out=print):
        st = self.state()
        for seq in st["unresolved"]:
            if MUTANT == "orphans_returned":
                self.resolve(seq, "RETURNED")
                continue
            self.resolve(seq, "ORPHAN", "posted with no reply recorded (the process died)")
            out("[ACCOUNT] invocation %d was POSTED with no reply recorded: an ORPHAN, counted and disclosed" % seq)
        return len(st["unresolved"])


def read_journal(path):
    """Read-only counts (archv2_arena.ro.open_ro) for the outcome's C0 (f); zeros when absent."""
    if not os.path.exists(path):
        return {"invocations": 0, "per_day": {}, "unresolved": [], "by_outcome": {}, "launches": 0}
    from archv2_arena import ro as aro
    c = aro.open_ro(path)
    try:
        return Journal(c, path).state()
    finally:
        c.close()


def journal_max_inflight(path):
    """[JV2-PARALLEL-POSTING] the journal's max_inflight, read read-only (archv2_arena.ro.open_ro); 1 for a journal
    created at workers 1 (no max_inflight row) and for an absent journal."""
    if not os.path.exists(path):
        return 1
    from archv2_arena import ro as aro
    c = aro.open_ro(path)
    try:
        return Journal(c, path).max_inflight
    finally:
        c.close()


def reconcile(test, journal, ledger_dir, out=print, prior=None):
    """Orphans resolved; per posting day the ledger caught up to the journal ("reconciled after crash") or REFUSED when
    ahead; then the equality ledger == journal (+ prior) for the test. Returns (orphans, caught_up).
    [2026-09-25] prior: the retired stores' invocations per day, counted on the journal side (module docstring)."""
    prior = prior or {"invocations": 0, "per_day": {}}
    orphans = journal.resolve_orphans(out)
    st = journal.state()
    led = test_day_rows(test, ledger_dir)
    caught = 0
    for day in sorted(set(st["per_day"]) | set(led) | set(prior["per_day"])):
        j = int(st["per_day"].get(day, 0)) + int(prior["per_day"].get(day, 0))
        l_ = int(led.get(day, 0))
        if l_ > j:
            raise SystemExit("[ACCOUNT] REFUSED: the ledger of %s carries %d calls of %s but the journal %d: a ledger AHEAD"
                             " of the journal is never reconciled downward" % (day, l_, test, j))
        if l_ < j:
            append(test, "reconciled after crash: %d invocation(s) journaled on %s not ledgered" % (j - l_, day), j - l_,
                   ledger_dir, day=day)
            out("[ACCOUNT] RECONCILED after crash: %d invocation(s) of %s on %s appended to %s" % (
                j - l_, test, day, os.path.abspath(atl.day_ledger_path(ledger_dir, day))))
            caught += j - l_
    check_equal(test, journal.state()["invocations"] + int(prior["invocations"]), ledger_dir, "after the reconciliation")
    return orphans, caught


def check_equal(test, invocations, ledger_dir, when):
    l_ = atl.ledger_calls(test, ledger_dir)
    if l_ != int(invocations):
        raise SystemExit("[ACCOUNT] REFUSED (%s): the ledgers carry %d calls of %s but the journal records %d invocations"
                         " (ruling 1 (b): they must be EQUAL)" % (when, l_, test, invocations))
    return l_


def wrap_call(call_full, journal, slot_of, posts, launch, day, payload_sha, clock=None):
    """The injected call_full, write-ahead: the payload's slot, the PENDING row committed, posts["n"] += 1, THEN the post;
    the resolution after it returns or raises. [2026-09-25] FIRST the day-rollover check: the local date (clock(),
    default local_day) must still be the launch's `day`, else SystemExit BEFORE the journal row and the post (a clean stop;
    the relaunch resumes). clock: SELFTEST-ONLY substitute."""
    clk = clock or local_day

    def call(system, user):
        now = clk()
        if now != day and MUTANT != "rollover_off":
            raise SystemExit("[ACCOUNT] DAY ROLLOVER: this launch's posting day is %s but the local date is now %s: no"
                             " further post in this launch (a clean stop BEFORE the post; every post so far is journaled"
                             " and ledgered on %s; relaunch to resume the pending slots under %s's guard)" % (
                                 day, now, day, now))
        sha = payload_sha(system, user)
        slots = slot_of.get(sha)
        if not slots:
            raise SystemExit("[ACCOUNT] a payload that is not in the dry-run's set (sha256 %s): refused before the post" % sha)
        mid, order = slots[0]
        if MUTANT == "journal_after_post":
            posts["n"] += 1
            r = call_full(system, user)
            seq = journal.pending(launch, mid, order, sha, day)
            journal.resolve(seq, "RETURNED")
            return r
        seq = journal.pending(launch, mid, order, sha, day)
        posts["n"] += 1
        try:
            r = call_full(system, user)
        except BaseException as e:
            journal.resolve(seq, "RAISED", "%s: %s" % (type(e).__name__, str(e)[:200]))
            raise
        journal.resolve(seq, "RETURNED")
        return r
    return call


# ── [JV2-PARALLEL-POSTING E-2] the two-phase transport (workers > 1; wrap_call above stays the workers-1 path) ─────────

def rollover_message(day, now):
    return ("[ACCOUNT] DAY ROLLOVER: this launch's posting day is %s but the local date is now %s: no further post in"
            " this launch (a clean stop BEFORE the post; every post so far is journaled and ledgered on %s; relaunch to"
            " resume the pending slots under %s's guard)" % (day, now, day, now))


class TwoPhaseCall(POOL.TwoPhase):
    """wrap_call's contract split in three (module docstring; judge_v2.pool). Used only at workers > 1, on a journal v2
    (Journal.begin_launch refuses a pooled launch on a journal created at workers 1)."""

    def __init__(self, call_full, journal, slot_of, posts, launch, day, payload_sha, clock=None):
        self.call_full, self.journal, self.slot_of, self.posts = call_full, journal, slot_of, posts
        self.launch, self.day, self.payload_sha = launch, day, payload_sha
        self.clk = clock or local_day
        self.max_inflight = journal.max_inflight
        self._turns = {}
        self._prev = None
        self._lock = threading.Lock()
        self._sent_py = 0
        row = journal.conn.execute("SELECT value FROM meta WHERE key='cap'").fetchone()
        self._cap = int(row[0]) if row is not None else AUTHOR_HARD_CAP
        self.http_cap = self._cap           # [coordinator item 2] every HTTP attempt counts against the journal's cap

    def http_booked(self):
        """The HTTP attempts already booked in the journal: each resolved invocation's http_attempts (NULL, i.e. a
        workers-1 or pre-v2 invocation, and every unresolved one, read as 1)."""
        POOL.assert_main_thread("http_booked")
        c = self.journal.conn
        if self.journal.version == 1:
            return int(c.execute("SELECT COUNT(*) FROM invocation").fetchone()[0])
        return int(c.execute("SELECT COALESCE(SUM(COALESCE(r.http_attempts, 1)), 0) FROM invocation i LEFT JOIN"
                             " resolution r ON r.seq = i.seq").fetchone()[0])

    def reserve(self, system, user):
        POOL.assert_main_thread("reserve")
        if MUTANT != "rollover_off":
            now = self.clk()
            if now != self.day:
                raise SystemExit(rollover_message(self.day, now))
        sha = self.payload_sha(system, user)
        slots = self.slot_of.get(sha)
        if not slots:
            raise SystemExit("[ACCOUNT] a payload that is not in the dry-run's set (sha256 %s): refused before the post" % sha)
        mid, order = slots[0]
        seq = self.journal.pending(self.launch, mid, order, sha, self.day)
        if MUTANT != "posts_at_completion":
            self.posts["n"] += 1
        body = rr.payload_bytes(system, user)
        if hashlib.sha256(body).hexdigest() != sha:
            raise SystemExit("[ACCOUNT] the reserved body is not the payload's sha %s: refused before the post" % sha)
        t = POOL.Ticket(seq, sha, body, system, user, booked=(mid, order))
        if MUTANT == "body_prev_reserve" and self._prev is not None:
            t.body = self._prev.body
        with self._lock:
            self._turns[seq] = (system, user)
        self._prev = t
        return t

    def send(self, ticket):
        """WORKER thread: no sqlite, no rr global."""
        if MUTANT not in ("rollover_off", "rollover_send_off"):
            if self.clk() != self.day:
                return POOL.NOT_SENT
        if MUTANT == "cap_in_workers":
            with self._lock:
                if self._sent_py >= self._cap:
                    raise RuntimeError("the python cap counter is reached")
                self._sent_py += 1
        system, user = ticket.system, ticket.user
        if MUTANT == "body_prev_send":
            with self._lock:
                system, user = self._turns.get(ticket.seq - 1, (system, user))
        return self.call_full(system, user)

    def resolve(self, ticket, outcome):
        POOL.assert_main_thread("resolve")
        if MUTANT == "posts_at_completion":
            self.posts["n"] += 1
        a, n429 = outcome.http_attempts, outcome.http_429
        if outcome.kind == "returned":
            self.journal.resolve(ticket.seq, "RETURNED", None, a, n429)
        elif outcome.kind == "not_sent":
            self.journal.resolve(ticket.seq, "RAISED", POOL.NOT_SENT, a, n429)
        else:
            e = outcome.value
            self.journal.resolve(ticket.seq, "RAISED", "%s: %s" % (type(e).__name__, str(e)[:200]), a, n429)
