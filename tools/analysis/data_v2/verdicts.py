"""data_v2.verdicts: the v2 verdict store, as a SCHEMA and a WRITER LIBRARY only (no run, no call; ARCH-v2 R6 + R7 + R8).

ONE APPEND-ONLY DB PER REGISTERED RUN. The identity of a verdict is its SCHEDULE SLOT, never its payload:
  KEY  (run_id, match_id, presentation_order, draw_index)       R7: sha256(payload_body) collides when the same body is
                                                                 posted twice (a canary's second pass, the second
                                                                 calibration draw, a same-session control arm), so
  payload_sha256 is a COLUMN (NOT NULL, checked against the stored body), not the key.
VOTE (R6; judge §2.3): the positional six-way enum {FIRST, SECOND, TIE, INVALID, NON_TERMINATED, CONTENT_FILTER}, so a
  truncation or a provider refusal can never collapse into TIE. CHECKs tie it to the call:
  content_filter = (vote = 'CONTENT_FILTER'); (finish_reason = 'length') = (vote = 'NON_TERMINATED');
  raw_text is NULL only on CONTENT_FILTER; temperature_sent NULL means OMITTED and then temperature_label = 'omitted'
  (plan Amendment 1 D2; ruled at programme L15037).
TABLES
  run_meta   (key, value)  written at create: schema_id, run_id, registration, judge_requested, provider, max_tokens,
             temperature_label, script_blob, combiner_blob, prompt_template_blob, parse_version, pool_id, snapshot_id ...
  schedule   one row per slot, written BEFORE the first attempt (a schedule insert after any attempt ABORTS); the
             presentation (shown_first / shown_second), the contestants, the variant and stem_key (R9: references keyed
             by variant, clusters by component), the reference row and vintage
  attempt    every post, errors included (http status, error class, latency, payload sha); errors never become verdicts
  verdict    one row per slot at most, with the per-call provenance of judge §2.8 / data §3 and the posted body
             (zlib-compressed: judge §2.8 names zstd, which is not in the standard library; the codec is recorded in
             body_codec)
  v2_seal    empty until the seal; one row after it
VIEWS (derived, never stored): vote_contestant (the contestant frame: CASE on shown_first / shown_second) and
  match_verdict (the dual-order combination: rejudge_grok.combine_orders's rule, INVALID if either order is INVALID, TIE when
  the two contestant-frame votes differ, else the common vote, EXTENDED so CONTENT_FILTER and then NON_TERMINATED
  propagate as their own classes, in that precedence, before INVALID). THE COMBINER OF RECORD IS E-J's, pinned by blob in
  the run manifest; this view is the schema's default reading, not a pin.
  match_verdict is an INNER JOIN of the two orders: a match with a missing order (pending, errored) is ABSENT from it, so
  it is never a denominator. DENOMINATORS COME FROM `schedule`; the view match_status lists EVERY scheduled
  (run_id, match_id, draw_index) with its combined class or 'PENDING' and the number of order verdicts present.
  [NOTE 2026-09-24 for pooled callers: E-J's match_verdicts() (branch worktree-agent-a549c1b2890aa2a8a) does not return
  run_id; a caller that pools several run DBs must carry the run_id itself, or match ids from two runs collide.]
EQUALITY WITH THE SCHEDULE: verdict.stem_key, reference_row_id and reference_vintage repeat the slot's values; the trigger
  verdict_equals_schedule ABORTS an insert whose values differ (NULL-safe, IS), and record_verdict fills them from the slot
  when the caller omits them.
APPEND-ONLY: BEFORE UPDATE and BEFORE DELETE triggers on every table RAISE(ABORT); a BEFORE INSERT trigger on every keyed
  table aborts when the key already exists, which closes INSERT OR REPLACE (READY_archv2_ED D5); an insert into schedule after the first
  attempt, into attempt / verdict for a slot not in the schedule, or into anything after the seal ABORTS.
RELAUNCH: pending() = schedule EXCEPT verdict (by key). A cached CONTENT_FILTER is a verdict row, so it is never re-posted
  (rule 10); an errored attempt is not, so it is re-posted. drain(poster) posts exactly the pending slots.
SEAL: seal() inserts the seal row with the per-table shas (data_v2.ro.seal), checkpoints, sets journal_mode=DELETE,
  closes and makes the file read-only; returns sha256-bytes.
"""
import hashlib
import json
import zlib
from datetime import datetime, timezone

from . import ro

VOTES = ("FIRST", "SECOND", "TIE", "INVALID", "NON_TERMINATED", "CONTENT_FILTER")
REQUIRED_META = ("run_id", "registration", "judge_requested", "provider", "max_tokens", "temperature_label",
                 "script_blob", "combiner_blob", "prompt_template_blob", "parse_version", "pool_id")
TABLES = ("run_meta", "schedule", "attempt", "verdict", ro.SEAL_TABLE)

_VOTE_CHECK = "vote IN (%s)" % ", ".join("'%s'" % v for v in VOTES)

DDL = """
CREATE TABLE run_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL) WITHOUT ROWID;
CREATE TABLE schedule (
    run_id TEXT NOT NULL, match_id TEXT NOT NULL, presentation_order INTEGER NOT NULL CHECK (presentation_order IN (1, 2)),
    draw_index INTEGER NOT NULL CHECK (draw_index >= 0),
    variant_id TEXT NOT NULL, stem_key TEXT NOT NULL, component_id TEXT,
    contestant_a TEXT NOT NULL, contestant_b TEXT NOT NULL, shown_first TEXT NOT NULL, shown_second TEXT NOT NULL,
    response_first_sha TEXT NOT NULL, response_second_sha TEXT NOT NULL,
    reference_row_id TEXT, reference_vintage TEXT, batch_id TEXT,
    CHECK (contestant_a != contestant_b),
    CHECK (shown_first IN (contestant_a, contestant_b) AND shown_second IN (contestant_a, contestant_b)
           AND shown_first != shown_second),
    PRIMARY KEY (run_id, match_id, presentation_order, draw_index)) WITHOUT ROWID;
CREATE TABLE attempt (
    run_id TEXT NOT NULL, match_id TEXT NOT NULL, presentation_order INTEGER NOT NULL, draw_index INTEGER NOT NULL,
    attempt_no INTEGER NOT NULL CHECK (attempt_no >= 1), http_status INTEGER, error_class TEXT, latency_ms INTEGER,
    payload_sha256 TEXT NOT NULL, created_at TEXT NOT NULL,
    PRIMARY KEY (run_id, match_id, presentation_order, draw_index, attempt_no)) WITHOUT ROWID;
CREATE TABLE verdict (
    run_id TEXT NOT NULL, match_id TEXT NOT NULL, presentation_order INTEGER NOT NULL, draw_index INTEGER NOT NULL,
    vote TEXT NOT NULL CHECK (%(vote_check)s),
    raw_text TEXT, parse_version TEXT NOT NULL,
    payload_sha256 TEXT NOT NULL, body_zlib BLOB NOT NULL, body_codec TEXT NOT NULL CHECK (body_codec = 'zlib'),
    judge_requested TEXT NOT NULL, provider TEXT NOT NULL, response_model TEXT, system_fingerprint TEXT, response_id TEXT,
    finish_reason TEXT, prompt_tokens INTEGER, completion_tokens INTEGER, max_tokens INTEGER NOT NULL,
    temperature_sent REAL, temperature_label TEXT NOT NULL,
    content_filter INTEGER NOT NULL CHECK (content_filter IN (0, 1)),
    http_status INTEGER, n_attempts INTEGER NOT NULL CHECK (n_attempts >= 1), latency_ms INTEGER,
    system_template_sha TEXT, rubric_sha TEXT, user_template_sha TEXT, schema_sha TEXT,
    prompt_template_blob TEXT NOT NULL, script_blob TEXT NOT NULL, combiner_blob TEXT NOT NULL,
    reference_row_id TEXT, reference_vintage TEXT, stem_key TEXT NOT NULL, session_id TEXT, batch_id TEXT,
    pool_id TEXT NOT NULL, snapshot_id TEXT, created_at TEXT NOT NULL,
    CHECK (content_filter = (vote = 'CONTENT_FILTER')),
    CHECK ((COALESCE(finish_reason, '') = 'length') = (vote = 'NON_TERMINATED')),
    CHECK (raw_text IS NOT NULL OR vote = 'CONTENT_FILTER'),
    CHECK ((temperature_sent IS NULL) = (temperature_label = 'omitted')),
    PRIMARY KEY (run_id, match_id, presentation_order, draw_index)) WITHOUT ROWID;
CREATE TABLE %(seal)s (only_row INTEGER PRIMARY KEY CHECK (only_row = 1), label TEXT NOT NULL, tables_json TEXT NOT NULL);
CREATE TRIGGER schedule_fixed_before_first_call BEFORE INSERT ON schedule
    WHEN EXISTS (SELECT 1 FROM attempt) OR EXISTS (SELECT 1 FROM verdict)
    BEGIN SELECT RAISE(ABORT, 'v2 verdict store: the schedule is fixed before the first call'); END;
CREATE TRIGGER attempt_needs_slot BEFORE INSERT ON attempt
    WHEN NOT EXISTS (SELECT 1 FROM schedule s WHERE s.run_id = NEW.run_id AND s.match_id = NEW.match_id
                     AND s.presentation_order = NEW.presentation_order AND s.draw_index = NEW.draw_index)
    BEGIN SELECT RAISE(ABORT, 'v2 verdict store: attempt for a slot not in the schedule'); END;
CREATE TRIGGER verdict_needs_slot BEFORE INSERT ON verdict
    WHEN NOT EXISTS (SELECT 1 FROM schedule s WHERE s.run_id = NEW.run_id AND s.match_id = NEW.match_id
                     AND s.presentation_order = NEW.presentation_order AND s.draw_index = NEW.draw_index)
    BEGIN SELECT RAISE(ABORT, 'v2 verdict store: verdict for a slot not in the schedule'); END;
CREATE TRIGGER verdict_equals_schedule BEFORE INSERT ON verdict
    WHEN EXISTS (SELECT 1 FROM schedule s WHERE s.run_id = NEW.run_id AND s.match_id = NEW.match_id
                 AND s.presentation_order = NEW.presentation_order AND s.draw_index = NEW.draw_index)
     AND NOT EXISTS (SELECT 1 FROM schedule s WHERE s.run_id = NEW.run_id AND s.match_id = NEW.match_id
                 AND s.presentation_order = NEW.presentation_order AND s.draw_index = NEW.draw_index
                 AND s.stem_key = NEW.stem_key AND s.reference_row_id IS NEW.reference_row_id
                 AND s.reference_vintage IS NEW.reference_vintage)
    BEGIN SELECT RAISE(ABORT, 'v2 verdict store: stem_key / reference_row_id / reference_vintage differ from the schedule slot'); END;
CREATE VIEW vote_contestant AS
    SELECT v.run_id, v.match_id, v.presentation_order, v.draw_index, v.vote, s.contestant_a, s.contestant_b,
           s.shown_first, s.shown_second,
           CASE v.vote WHEN 'FIRST' THEN CASE WHEN s.shown_first = s.contestant_a THEN 'A' ELSE 'B' END
                       WHEN 'SECOND' THEN CASE WHEN s.shown_second = s.contestant_a THEN 'A' ELSE 'B' END
                       ELSE v.vote END AS vote_contestant
    FROM verdict v JOIN schedule s USING (run_id, match_id, presentation_order, draw_index);
CREATE VIEW match_verdict AS
    SELECT o1.run_id, o1.match_id, o1.draw_index, o1.vote_contestant AS order1, o2.vote_contestant AS order2,
           CASE WHEN 'CONTENT_FILTER' IN (o1.vote_contestant, o2.vote_contestant) THEN 'CONTENT_FILTER'
                WHEN 'NON_TERMINATED' IN (o1.vote_contestant, o2.vote_contestant) THEN 'NON_TERMINATED'
                WHEN 'INVALID' IN (o1.vote_contestant, o2.vote_contestant) THEN 'INVALID'
                WHEN o1.vote_contestant != o2.vote_contestant THEN 'TIE'
                ELSE o1.vote_contestant END AS combined,
           (o1.vote_contestant IN ('A', 'B', 'TIE') AND o2.vote_contestant IN ('A', 'B', 'TIE')
            AND o1.vote_contestant != o2.vote_contestant) AS flip
    FROM vote_contestant o1 JOIN vote_contestant o2
      ON o1.run_id = o2.run_id AND o1.match_id = o2.match_id AND o1.draw_index = o2.draw_index
     AND o1.presentation_order = 1 AND o2.presentation_order = 2;
CREATE VIEW match_status AS
    SELECT m.run_id, m.match_id, m.draw_index, COALESCE(v.combined, 'PENDING') AS combined, v.flip,
           (SELECT COUNT(*) FROM verdict x WHERE x.run_id = m.run_id AND x.match_id = m.match_id
             AND x.draw_index = m.draw_index) AS n_order_verdicts
    FROM (SELECT DISTINCT run_id, match_id, draw_index FROM schedule) m
    LEFT JOIN match_verdict v ON v.run_id = m.run_id AND v.match_id = m.match_id AND v.draw_index = m.draw_index;
""" %{"vote_check": _VOTE_CHECK, "seal": ro.SEAL_TABLE}

# REPLACE LOCK (READY_archv2_ED D5): `INSERT OR REPLACE` / `REPLACE INTO` deletes the conflicting row WITHOUT firing the
# DELETE triggers (recursive_triggers is 0), so UPDATE/DELETE triggers alone do not make a table append-only. Every keyed
# table therefore carries a BEFORE INSERT trigger that ABORTS when a row with NEW's key already exists; a BEFORE trigger
# runs before conflict resolution, so REPLACE, OR IGNORE and a plain duplicate insert all abort here.
KEYS = {"run_meta": ("key",), "schedule": ("run_id", "match_id", "presentation_order", "draw_index"),
        "attempt": ("run_id", "match_id", "presentation_order", "draw_index", "attempt_no"),
        "verdict": ("run_id", "match_id", "presentation_order", "draw_index"), ro.SEAL_TABLE: ("only_row",)}
for _t, _k in KEYS.items():
    DDL += ("CREATE TRIGGER %(t)s_no_rekey BEFORE INSERT ON %(t)s WHEN EXISTS (SELECT 1 FROM %(t)s x WHERE %(w)s) BEGIN"
            " SELECT RAISE(ABORT, 'v2 verdict store is append-only: key already present in %(t)s (REPLACE refused)'); END;\n"
            ) % {"t": _t, "w": " AND ".join("x.%s = NEW.%s" % (c, c) for c in _k)}

for _t in TABLES:
    DDL += ("CREATE TRIGGER %(t)s_no_update BEFORE UPDATE ON %(t)s BEGIN SELECT RAISE(ABORT, 'v2 verdict store is"
            " append-only: UPDATE on %(t)s'); END;\n"
            "CREATE TRIGGER %(t)s_no_delete BEFORE DELETE ON %(t)s BEGIN SELECT RAISE(ABORT, 'v2 verdict store is"
            " append-only: DELETE on %(t)s'); END;\n") % {"t": _t}
    if _t != ro.SEAL_TABLE:
        DDL += ("CREATE TRIGGER %(t)s_sealed BEFORE INSERT ON %(t)s WHEN EXISTS (SELECT 1 FROM %(s)s) BEGIN SELECT"
                " RAISE(ABORT, 'v2 verdict store is SEALED: INSERT on %(t)s'); END;\n") % {"t": _t, "s": ro.SEAL_TABLE}

SCHEDULE_COLS = ("run_id", "match_id", "presentation_order", "draw_index", "variant_id", "stem_key", "component_id",
                 "contestant_a", "contestant_b", "shown_first", "shown_second", "response_first_sha",
                 "response_second_sha", "reference_row_id", "reference_vintage", "batch_id")
VERDICT_FIELDS = ("vote", "raw_text", "parse_version", "judge_requested", "provider", "response_model",
                  "system_fingerprint", "response_id", "finish_reason", "prompt_tokens", "completion_tokens", "max_tokens",
                  "temperature_sent", "temperature_label", "http_status", "n_attempts", "latency_ms",
                  "system_template_sha", "rubric_sha", "user_template_sha", "schema_sha", "prompt_template_blob",
                  "script_blob", "combiner_blob", "reference_row_id", "reference_vintage", "stem_key", "session_id",
                  "batch_id", "pool_id", "snapshot_id")


def _refuse(msg):
    raise SystemExit("[VERDICT-V2] " + msg)


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


class VerdictStore:
    def __init__(self, conn, path):
        self.conn = conn
        self.path = path
        self.run_id = conn.execute("SELECT value FROM run_meta WHERE key='run_id'").fetchone()[0]

    @classmethod
    def create(cls, path, meta):
        missing = [k for k in REQUIRED_META if k not in meta or meta[k] in (None, "")]
        if missing:
            _refuse("create: run_meta lacks %s" % missing)
        if str(meta["temperature_label"]) != "omitted":
            _refuse("create: temperature_label must be 'omitted' (plan Amendment 1 D2), got %r" % meta["temperature_label"])
        conn = ro.create_new(path)
        conn.executescript(DDL)
        rows = dict(meta)
        rows["schema_id"] = ro.RUN_SCHEMA_ID
        rows["votes"] = json.dumps(VOTES)
        rows["verdicts_blob"] = ro.git_blob_lf(__file__)
        for k in sorted(rows):
            conn.execute("INSERT INTO run_meta VALUES (?, ?)", (k, str(rows[k])))
        conn.commit()
        return cls(conn, path)

    @classmethod
    def open(cls, path):
        """A relaunch: re-open an unsealed v2 verdict DB for append (anything else is refused by ro.open_run_writer)."""
        return cls(ro.open_run_writer(path), path)

    def meta(self):
        return dict(self.conn.execute("SELECT key, value FROM run_meta"))

    def add_schedule(self, rows):
        for r in rows:
            r = dict(r)
            r.setdefault("run_id", self.run_id)
            if r["run_id"] != self.run_id:
                _refuse("schedule row for run %r in the store of run %r" % (r["run_id"], self.run_id))
            self.conn.execute("INSERT INTO schedule (%s) VALUES (%s)" % (", ".join(SCHEDULE_COLS), ",".join("?" * len(SCHEDULE_COLS))),
                              tuple(r.get(c) for c in SCHEDULE_COLS))
        self.conn.commit()

    def record_attempt(self, key, attempt_no, payload_sha256, http_status=None, error_class=None, latency_ms=None):
        run_id, match_id, order, draw = key
        self.conn.execute("INSERT INTO attempt VALUES (?,?,?,?,?,?,?,?,?,?)",
                          (run_id, match_id, order, draw, attempt_no, http_status, error_class, latency_ms,
                           payload_sha256, _now()))
        self.conn.commit()

    def record_verdict(self, key, body, payload_sha256, **fields):
        """Insert the verdict of one slot. body is the exact posted bytes; payload_sha256 must be sha256(body)."""
        if not isinstance(body, (bytes, bytearray)):
            _refuse("record_verdict: body must be the exact posted bytes")
        if hashlib.sha256(body).hexdigest() != payload_sha256:
            _refuse("record_verdict: payload_sha256 is not sha256(body)")
        unknown = set(fields) - set(VERDICT_FIELDS)
        if unknown:
            _refuse("record_verdict: unknown field(s) %s" % sorted(unknown))
        if fields.get("vote") not in VOTES:
            _refuse("record_verdict: vote %r is not one of %s" % (fields.get("vote"), VOTES))
        run_id, match_id, order, draw = key
        f = {k: fields.get(k) for k in VERDICT_FIELDS}
        slot = self.conn.execute("SELECT stem_key, reference_row_id, reference_vintage FROM schedule WHERE run_id=? AND"
                                 " match_id=? AND presentation_order=? AND draw_index=?", key).fetchone()
        if slot is not None:
            # the per-verdict copies of schedule values default to the slot's; a caller that passes a different value
            # is refused by the verdict_equals_schedule trigger
            for k, v in zip(("stem_key", "reference_row_id", "reference_vintage"), slot):
                if k not in fields:
                    f[k] = v
        f["content_filter"] = int(f["vote"] == "CONTENT_FILTER")
        cols = ["run_id", "match_id", "presentation_order", "draw_index", "payload_sha256", "body_zlib", "body_codec",
                "created_at", "content_filter"] + [k for k in VERDICT_FIELDS]
        vals = [run_id, match_id, order, draw, payload_sha256, zlib.compress(bytes(body), 6), "zlib", _now(),
                f["content_filter"]] + [f[k] for k in VERDICT_FIELDS]
        self.conn.execute("INSERT INTO verdict (%s) VALUES (%s)" % (", ".join(cols), ",".join("?" * len(cols))), vals)
        self.conn.commit()

    def pending(self):
        """The relaunch anti-join: schedule slots with no verdict row, in key order."""
        return self.conn.execute(
            "SELECT %s FROM schedule s WHERE NOT EXISTS (SELECT 1 FROM verdict v WHERE v.run_id = s.run_id AND"
            " v.match_id = s.match_id AND v.presentation_order = s.presentation_order AND v.draw_index = s.draw_index)"
            " ORDER BY s.run_id, s.match_id, s.presentation_order, s.draw_index" % ", ".join("s." + c for c in SCHEDULE_COLS)
        ).fetchall()

    def drain(self, poster):
        """Post every pending slot through poster(slot_dict) -> ("verdict", body, sha, fields) or ("error", sha, status,
        error_class). Returns the number of posts. No poster in this package calls a judge; runs supply their own."""
        posts = 0
        for row in self.pending():
            slot = dict(zip(SCHEDULE_COLS, row))
            key = (slot["run_id"], slot["match_id"], slot["presentation_order"], slot["draw_index"])
            n_prev = self.conn.execute("SELECT COUNT(*) FROM attempt WHERE run_id=? AND match_id=? AND"
                                       " presentation_order=? AND draw_index=?", key).fetchone()[0]
            res = poster(slot)
            posts += 1
            if res[0] == "verdict":
                _kind, body, sha, fields = res
                self.record_attempt(key, n_prev + 1, sha, http_status=fields.get("http_status"))
                fields = dict(fields)
                fields["n_attempts"] = n_prev + 1
                self.record_verdict(key, body, sha, **fields)
            elif res[0] == "error":
                _kind, sha, status, err = res
                self.record_attempt(key, n_prev + 1, sha, http_status=status, error_class=err)
            else:
                _refuse("poster returned %r" % (res[0],))
        return posts

    def seal(self, allow_incomplete=False):
        """Seal at close. A run with pending slots is refused unless allow_incomplete, and then the seal label says
        INCOMPLETE with the pending count (an analysis that requires a complete cache reads the label)."""
        n_pending = len(self.pending())
        if n_pending and not allow_incomplete:
            _refuse("seal: %d slots are still pending; a run is sealed only when complete (or allow_incomplete)" % n_pending)
        label = "verdict run %s: %s" % (self.run_id, "COMPLETE" if not n_pending else "INCOMPLETE, %d pending" % n_pending)
        out = ro.seal(self.conn, self.path, label)
        self.conn = None
        return out
