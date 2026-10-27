"""judge_v2.pool_inertness: the BYTE-INERTNESS PROOF of JV2-PARALLEL-POSTING at --workers 1 (registered at bf9d80b,
docs/judge_v2_program.md L19096-L19239, section 2.4; criterion EC1; the vacuity rule of CONTEXT rule 11, STANDING
2026-09-23). Zero calls: every leg posts to a deterministic fake call_full; no DB of record is opened (the legs use the
judge_v2 selftest's DEV fixture view in a temp directory; no rule-7 window).

    python tools/analysis/judge_v2/pool_inertness.py --leg-a-root <dir> [--keep <dir>]

  --leg-a-root  a checkout (or `git archive` extraction) of the LANDING PARENT: today's judge_v2/writer.py
                (blob 6db4ab32) and today's archv2_pilot/accounting.py; it must carry tools/analysis and
                src/main/kotlin/taxonomy/service/TaxonomyArenaService.kt (rejudge_grok reads the templates from it).
  LEG B is this checkout, invoked at workers 1; LEG B' (the POSITIVE CONTROL) is this checkout at workers 4.

IDENTICAL IN EVERY LEG: the fixture (built ONCE by the parent, read by every leg through loader.load_matches: the same
eval_view file, never written), the requests, the deterministic fake call_full (a pure function of sha256(body), some
replies errors), a FROZEN CLOCK patched at the same module attributes in every leg (data_v2.verdicts._now,
archv2_pilot.accounting._now, archv2_pilot.accounting.local_day, time.strftime for the ledger), a fixed ctx session_id
(judge_v2.selftest._ctx), a fresh ledger directory, and the SAME work-directory path (cleaned between legs; so the paths
printed are equal). Each leg is its own python process with <root>/tools/analysis first on sys.path. The sequence is
pilot.launch's accounting sequence (Journal.open -> reconcile -> label -> [begin_launch where it exists] -> writer.create
-> wrap_call (workers 1) / TwoPhaseCall (workers 4) -> writer.run -> finally the day-ledger append -> ledger == journal).

COMPARED, leg A vs leg B (2.4):
  (1) the ordered sequence of posted bodies (the fake's log): byte-identical;
  (2) the store's canonical .dump (sqlite3 iterdump): identical except run_meta.writer_blob and run_meta.pins_json, whose
      differing lines are enumerated EXHAUSTIVELY (and inside pins_json exactly the judge_v2/writer.py entry changed and
      the judge_v2/pool.py entry added);
  (3) the journal file: BYTE-identical, with sqlite_master text equal;
  (4) the ledger JSON: byte-identical (and the ledger directory holds the same file names: the lock file is gone);
  (5) stdout: identical except exactly the registered line "[POOL] workers 1 (sequential path)".
THE EXECUTION DISCRIMINATOR (a failure VOIDS leg B):
  (a) the identifiers _pipelined_poster, reserve, PostingPool, max_inflight counted as NAME tokens in the source of the
      imported judge_v2.writer, archv2_pilot.accounting (and judge_v2.pool when imported): 0 in leg A, > 0 in leg B;
  (b) leg B's sys.modules["judge_v2.writer"].__file__ is inside leg B's checkout and its git_blob_lf equals the build's
      writer blob (HEAD's, `git rev-parse HEAD:tools/analysis/judge_v2/writer.py`);
  (c) leg B's store run_meta.writer_blob equals that blob;
  (d) the [POOL] line was printed by leg B (new code on the dispatch branch that executed).
POSITIVE CONTROL: leg B' (workers 4): its store projection (E-8: every column of schedule / attempt / verdict and every
run_meta key except created_at, latency_ms, session_id) equals leg B's, and equals leg A's except the two enumerated
run_meta keys; its posted bodies are leg A's as a multiset; its journal is v2 (max_inflight 16, launch_bound workers 4).
I13 ON THE REAL LEGS: leg B's writer REFUSES a relaunch of leg A's store ("recipe identity differs ... writer_blob").
[ADDED 2026-09-25, READY review d32fa75 F5 (C1a, LOW), insertion only: THE SCOPE OF EC1. The legs drive a REPLICA of
pilot.launch's accounting sequence (Journal.open -> reconcile -> label -> begin_launch -> writer.create -> wrap_call ->
writer.run -> the ledger append), not pilot.launch itself. Through pilot.launch at workers 1 (no rate flag) the driver's
launch manifest ALSO differs between the legs, BY DESIGN (provenance, not behaviour), in exactly two keys:
judge_v2_pins (judge_v2.writer._pins(): judge_v2/writer.py moves and judge_v2/pool.py is added) and archv2_pilot_lf16
(common.package_lf16(): pilot.py and accounting.py change). The parent prints both keys' values per leg on its SCOPE
line (computed from each leg's files, never from a launch).
DISCRIMINATOR (e) [delta]: leg B imported the HEAD blob of judge_v2/pool.py (the F1 / F3 / F4 identifiers counted in it)
and leg B' executed it (its '[RATE] live guard:' and time_scale-printing '[RATE] config:' lines); leg B printed no [RATE]
line.]
"""
import difflib
import hashlib
import io
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import tokenize

HERE = os.path.dirname(os.path.abspath(__file__))
ANALYSIS = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(ANALYSIS))
DAY = "2026-09-25"
FIXED_NOW = "2026-09-25T10:00:00.000000Z"
FIXED_TS = "2026-09-25 12:00:00"
NEW_IDS = ("_pipelined_poster", "reserve", "PostingPool", "max_inflight")
POOL_LINE = "[POOL] workers 1 (sequential path)"
TEST = "ARCH-V2-PILOT-K46"


def git_blob_lf_bytes(data):
    data = data.replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest()


DELTA_IDS = ("PoolAborted", "pace_lock", "live_guard_reasons", "abort_ev")     # [delta d32fa75] F1 / F3 / F4


def count_names(path, names):
    n = {k: 0 for k in names}
    with open(path, "rb") as f:
        for tok in tokenize.tokenize(io.BytesIO(f.read()).readline):
            if tok.type == tokenize.NAME and tok.string in n:
                n[tok.string] += 1
    return n


def count_ids(path):
    n = {k: 0 for k in NEW_IDS}
    with open(path, "rb") as f:
        for tok in tokenize.tokenize(io.BytesIO(f.read()).readline):
            if tok.type == tokenize.NAME and tok.string in n:
                n[tok.string] += 1
    return n


# ── one leg (a child process) ──────────────────────────────────────────────────────────────────────────────────────

def leg(root, work, fixture_json, workers):
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path[:] = [p for p in sys.path if os.path.normcase(os.path.abspath(p or ".")) != os.path.normcase(here)]
    sys.path.insert(0, os.path.join(root, "tools", "analysis"))
    import time as _time
    real_strftime = _time.strftime

    def strftime(fmt, *a):
        if a:
            return real_strftime(fmt, *a)
        if fmt == "%Y-%m-%d":
            return DAY
        if fmt == "%Y-%m-%d %H:%M:%S":
            return FIXED_TS
        return real_strftime(fmt)
    _time.strftime = strftime
    from judge_v2 import loader as LD, payload as P, selftest as S, writer as W
    from judge_v2._base import rr, dv2verdicts
    from archv2_pilot import accounting as ACC
    dv2verdicts._now = lambda: FIXED_NOW
    ACC._now = lambda: FIXED_NOW
    ACC.local_day = lambda: DAY
    with open(fixture_json, encoding="utf-8") as f:
        fx = json.load(f)
    P.configure_rr()
    rub = S.gold_rubric()
    loaded = LD.load_matches(fx["requests"], fx["ev_path"], out=print)
    store = os.path.join(work, "store.db")
    jpath = store + ".invocations.db"
    ledger = os.path.join(work, "ledger")
    os.makedirs(ledger)
    bodies = []

    def fake(system, user):
        body = rr.payload_bytes(system, user)
        bodies.append(body)
        sha = hashlib.sha256(body).hexdigest()
        b = int(sha[:2], 16)
        if b % 11 == 0:
            e = RuntimeError("fake 503")
            e.code = 503
            raise e
        w = ("Model A", "Model B", "TIE")[b % 3]
        return (json.dumps({"critique_a": "a", "critique_b": "b", "comparison": "c", "winner": w, "confidence": 0.7}),
                "azure:grok-4-1-fast-non-reasoning", 100 + b, 0.25, "stop", {"_response_id": "fake-" + sha[:12]})

    so = {}
    for mid, inp in loaded.specs.items():
        p1, p2 = P.build_dual(inp, rub)
        so.setdefault(p1.sha256, []).append((mid, 1))
        so.setdefault(p2.sha256, []).append((mid, 2))

    def psha(system, user):
        return hashlib.sha256(rr.payload_bytes(system, user)).hexdigest()
    import inspect
    kw = {"max_inflight": 16} if workers > 1 else {}
    journal = ACC.Journal.open(jpath, cap=ACC.AUTHOR_HARD_CAP, create=True, **kw)
    posts = {"n": 0}
    writer, label = None, None
    try:
        ACC.reconcile(TEST, journal, ledger, print)
        js = journal.state()
        label = "run#%d INERTNESS" % (js["launches"] + 1) + (" w=%d" % workers if workers > 1 else "")
        if hasattr(journal, "begin_launch"):
            journal.begin_launch(label, workers)
        writer = W.JudgeWriter.create(store, "INERTNESS (scratch)", "inert", loaded, rub, S._ctx())
        run_params = inspect.signature(W.JudgeWriter.run).parameters
        if workers == 1:
            call = ACC.wrap_call(fake, journal, so, posts, label, DAY, psha)
            if "workers" in run_params:
                writer.run(call, out=print, workers=1)
            else:
                writer.run(call, out=print)
        else:
            call = ACC.TwoPhaseCall(fake, journal, so, posts, label, DAY, psha)
            writer.run(call, out=print, workers=workers)
    finally:
        if writer is not None:
            writer.close()
        if posts["n"]:
            ACC.append(TEST, label, posts["n"], ledger, day=DAY)
        jn = journal.state()["invocations"]
        journal.close()
    ACC.check_equal(TEST, jn, ledger, "at the end of the launch")
    with open(os.path.join(work, "bodies.bin"), "wb") as f:
        for b in bodies:
            f.write(b"%d\n" % len(b) + b + b"\n")
    ids = {}
    for name in ("judge_v2.writer", "archv2_pilot.accounting", "judge_v2.pool"):
        m = sys.modules.get(name)
        if m is not None:
            ids[name] = {"file": os.path.abspath(m.__file__), "ids": count_ids(m.__file__)}
    with open(W.__file__, "rb") as f:
        wblob = git_blob_lf_bytes(f.read())
    rep = {"root": os.path.abspath(root), "writer_file": os.path.abspath(W.__file__), "writer_blob_lf": wblob,
           "ids": ids, "python": sys.version.split()[0], "workers": workers}
    with open(os.path.join(work, "leg_report.json"), "w", encoding="utf-8") as f:
        json.dump(rep, f, indent=1, sort_keys=True)
    return 0


def open_leg_a_store_with_leg_b(root, a_store, fixture_json):
    """I13 on the real legs: this checkout's writer (leg B code) relaunching leg A's store."""
    sys.path.insert(0, os.path.join(root, "tools", "analysis"))
    from judge_v2 import loader as LD, payload as P, selftest as S, writer as W
    with open(fixture_json, encoding="utf-8") as f:
        fx = json.load(f)
    P.configure_rr()
    loaded = LD.load_matches(fx["requests"], fx["ev_path"], out=lambda s: None)
    try:
        W.JudgeWriter.open(a_store, loaded, S.gold_rubric(), S._ctx()).close()
        print("I13-REAL ADMITTED")
    except SystemExit as e:
        print("I13-REAL REFUSED: %s" % str(e)[:400])
    return 0


# ── the parent ─────────────────────────────────────────────────────────────────────────────────────────────────────

def ro(path):
    import pathlib
    return sqlite3.connect(pathlib.Path(path).as_uri() + "?mode=ro", uri=True)


def dump(path):
    c = ro(path)
    try:
        return list(c.iterdump())
    finally:
        c.close()


def projection(path, drop_meta=()):
    c = ro(path)
    try:
        out = {}
        for t in ("schedule", "attempt", "verdict"):
            cols = [r[1] for r in c.execute("PRAGMA table_info(%s)" % t) if r[1] not in ("created_at", "latency_ms",
                                                                                          "session_id")]
            out[t] = c.execute("SELECT %s FROM %s ORDER BY run_id, match_id, presentation_order, draw_index%s" % (
                ", ".join(cols), t, ", attempt_no" if t == "attempt" else "")).fetchall()
        out["run_meta"] = [r for r in c.execute("SELECT key, value FROM run_meta ORDER BY key") if r[0] not in drop_meta]
    finally:
        c.close()
    return out


def meta(path, key):
    c = ro(path)
    try:
        r = c.execute("SELECT value FROM run_meta WHERE key=?", (key,)).fetchone()
        return r[0] if r else None
    finally:
        c.close()


def read_bodies(path):
    with open(path, "rb") as f:
        data = f.read()
    out, i = [], 0
    while i < len(data):
        j = data.index(b"\n", i)
        n = int(data[i:j])
        out.append(data[j + 1:j + 1 + n])
        i = j + 1 + n + 1
    return out


def run_leg(root, work, fixture_json, workers, logp):
    if os.path.exists(work):
        shutil.rmtree(work)
    os.makedirs(work)
    cmd = [sys.executable, os.path.abspath(__file__), "--leg", root, "--work", work, "--fixture", fixture_json,
           "--workers", str(workers)]
    p = subprocess.run(cmd, capture_output=True, cwd=tempfile.gettempdir(), timeout=1800)
    with open(logp, "wb") as f:
        f.write(p.stdout)
    if p.returncode != 0:
        raise SystemExit("[INERT] leg %s workers %d FAILED (exit %d): %s" % (root, workers, p.returncode,
                                                                          p.stderr.decode("utf-8", "replace")[-2000:]))
    return p.stdout


def git_head_blob(rel):
    r = subprocess.run(["git", "rev-parse", "HEAD:" + rel], capture_output=True, text=True, cwd=ROOT, timeout=60)
    return r.stdout.strip() if r.returncode == 0 else None


def parent(leg_a_root, keep):
    base = tempfile.mkdtemp(prefix="jv2_inert_")
    lines, ok_all = [], []

    def say(s):
        print(s, flush=True)
        lines.append(s)

    def verdict(name, ok, detail=""):
        ok_all.append(bool(ok))
        say("[INERT] %s %s%s" % ("PASS" if ok else "FAIL", name, (" | " + str(detail)[:600]) if detail else ""))
    try:
        sys.path.insert(0, ANALYSIS)
        from judge_v2 import selftest as S, pool_selftest as PS, payload as P, loader as LD
        P.configure_rr()
        fxdir = os.path.join(base, "fixture")
        os.makedirs(fxdir)
        _gv, ev = S.build_views(fxdir)
        reqs = PS.clean_requests(ev, S.gold_rubric(), fxdir)
        ev_sha = hashlib.sha256(open(ev, "rb").read()).hexdigest()
        fixture_json = os.path.join(base, "fixture.json")
        with open(fixture_json, "x", encoding="utf-8") as f:
            json.dump({"ev_path": ev, "requests": reqs}, f)
        say("[INERT] fixture: %d requests, eval_view sha256 %s (built once, read by every leg)" % (len(reqs), ev_sha))
        work = os.path.join(base, "work")
        outs = {}
        for name, root, w in (("A", leg_a_root, 1), ("B", ROOT, 1), ("B4", ROOT, 4)):
            so = run_leg(root, work, fixture_json, w, os.path.join(base, "stdout_%s.txt" % name))
            dst = os.path.join(base, "leg_" + name)
            shutil.move(work, dst)
            outs[name] = (dst, so)
            say("[INERT] leg %s (root %s, workers %d): done" % (name, root, w))
        verdict("the fixture view was not written by any leg", hashlib.sha256(open(ev, "rb").read()).hexdigest() == ev_sha)
        (da, sa), (db, sb), (d4, s4) = outs["A"], outs["B"], outs["B4"]
        repA = json.load(open(os.path.join(da, "leg_report.json"), encoding="utf-8"))
        repB = json.load(open(os.path.join(db, "leg_report.json"), encoding="utf-8"))
        # (1) bodies
        ba, bb, b4 = (read_bodies(os.path.join(d, "bodies.bin")) for d in (da, db, d4))
        verdict("(1) the ordered posted bodies are byte-identical (%d bodies, sha256 of the log %s)" % (
            len(ba), hashlib.sha256(open(os.path.join(da, "bodies.bin"), "rb").read()).hexdigest()[:16]),
            ba == bb and open(os.path.join(da, "bodies.bin"), "rb").read() == open(os.path.join(db, "bodies.bin"),
                                                                                  "rb").read())
        # (2) the store dump
        dA, dB = dump(os.path.join(da, "store.db")), dump(os.path.join(db, "store.db"))
        only_a = [x for x in dA if x not in set(dB)]
        only_b = [x for x in dB if x not in set(dA)]
        allowed = all(("'writer_blob'" in x or "'pins_json'" in x) and x.startswith('INSERT INTO "run_meta"')
                      for x in only_a + only_b)
        pa, pb = json.loads(meta(os.path.join(da, "store.db"), "pins_json")), json.loads(meta(os.path.join(db, "store.db"),
                                                                                              "pins_json"))
        pin_diff = sorted(k for k in set(pa) | set(pb) if pa.get(k) != pb.get(k))
        verdict("(2) the store's canonical dump (%d lines) differs ONLY in run_meta.writer_blob and run_meta.pins_json"
                " (%d + %d differing lines, enumerated below)" % (len(dA), len(only_a), len(only_b)),
                allowed and len(only_a) == len(only_b) == 2 and len(dA) == len(dB) and
                [i for i, (x, y) in enumerate(zip(dA, dB)) if x != y] == [i for i, x in enumerate(dA) if x in only_a])
        for x in only_a:
            say("    A only: %s" % (x[:160] + ("..." if len(x) > 160 else "")))
        for x in only_b:
            say("    B only: %s" % (x[:160] + ("..." if len(x) > 160 else "")))
        verdict("(2) inside pins_json exactly judge_v2/writer.py changed and judge_v2/pool.py was added",
                pin_diff == ["judge_v2/pool.py", "judge_v2/writer.py"] and "judge_v2/pool.py" not in pa, pin_diff)
        say("    pins_json writer.py: A %s -> B %s; pool.py: B %s" % (pa.get("judge_v2/writer.py"),
                                                                     pb.get("judge_v2/writer.py"),
                                                                     pb.get("judge_v2/pool.py")))
        # (3) the journal
        ja, jb = (open(os.path.join(d, "store.db.invocations.db"), "rb").read() for d in (da, db))

        def master(p):
            c = ro(p)
            try:
                return c.execute("SELECT type, name, sql FROM sqlite_master ORDER BY name").fetchall()
            finally:
                c.close()
        verdict("(3) the journal file is BYTE-identical (%d bytes, sha256 %s) and sqlite_master's text equal" % (
            len(ja), hashlib.sha256(ja).hexdigest()[:16]), ja == jb and master(os.path.join(da, "store.db.invocations.db"))
            == master(os.path.join(db, "store.db.invocations.db")))
        # (4) the ledger
        la, lb = (sorted(os.listdir(os.path.join(d, "ledger"))) for d in (da, db))
        fa = [open(os.path.join(da, "ledger", n), "rb").read() for n in la]
        fb = [open(os.path.join(db, "ledger", n), "rb").read() for n in lb]
        verdict("(4) the ledger JSON is byte-identical and the ledger directory holds the same names %s (no lock file)" %
                la, la == lb and fa == fb and la == ["day_calls_%s.json" % DAY],
                hashlib.sha256(fa[0]).hexdigest()[:16] if fa else None)
        # (5) stdout
        oa, ob = sa.decode("utf-8").splitlines(), sb.decode("utf-8").splitlines()
        diff = [x for x in difflib.ndiff(oa, ob) if x[:2] in ("- ", "+ ")]
        verdict("(5) stdout identical except exactly the registered line %r (%d lines A, %d lines B)" % (
            POOL_LINE, len(oa), len(ob)), diff == ["+ " + POOL_LINE], diff[:6])
        # the discriminator
        idsA = {k: sum(v["ids"].values()) for k, v in repA["ids"].items()}
        idsB = {k: sum(v["ids"].values()) for k, v in repB["ids"].items()}
        verdict("DISCRIMINATOR (a) the new identifiers %s: leg A 0 in %s; leg B > 0 in writer and accounting (%s)" % (
            list(NEW_IDS), sorted(idsA), json.dumps({k: v["ids"] for k, v in repB["ids"].items()}, sort_keys=True)),
            sum(idsA.values()) == 0 and "judge_v2.pool" not in repA["ids"] and idsB.get("judge_v2.writer", 0) > 0 and
            idsB.get("archv2_pilot.accounting", 0) > 0, idsA)
        head_w = git_head_blob("tools/analysis/judge_v2/writer.py")
        inside = os.path.normcase(repB["writer_file"]).startswith(os.path.normcase(os.path.abspath(ROOT)) + os.sep)
        verdict("DISCRIMINATOR (b) leg B's judge_v2.writer.__file__ is inside leg B's checkout (%s) and its git_blob_lf"
                " %s equals the build's (HEAD) writer blob %s" % (repB["writer_file"], repB["writer_blob_lf"], head_w),
                inside and repB["writer_blob_lf"] == head_w and os.path.normcase(repA["writer_file"]).startswith(
                    os.path.normcase(os.path.abspath(leg_a_root))))
        wb = meta(os.path.join(db, "store.db"), "writer_blob")
        verdict("DISCRIMINATOR (c) leg B's store run_meta.writer_blob %s equals the new blob; leg A's %s" % (
            wb, meta(os.path.join(da, "store.db"), "writer_blob")), wb == head_w and
            meta(os.path.join(da, "store.db"), "writer_blob") != wb)
        verdict("DISCRIMINATOR (d) leg B printed the [POOL] line (the dispatch branch that executed); leg A did not",
                ob.count(POOL_LINE) == 1 and oa.count(POOL_LINE) == 0)
        # positive control
        prA = projection(os.path.join(da, "store.db"), drop_meta=("writer_blob", "pins_json"))
        prB = projection(os.path.join(db, "store.db"))
        pr4 = projection(os.path.join(d4, "store.db"))
        verdict("POSITIVE CONTROL leg B' (workers 4): its projection equals leg B's (every column, every run_meta key)",
                pr4 == prB)
        verdict("POSITIVE CONTROL leg B' equals leg A's projection except the two enumerated run_meta keys",
                projection(os.path.join(d4, "store.db"), drop_meta=("writer_blob", "pins_json")) == prA)
        s4l = s4.decode("utf-8").splitlines()
        c = ro(os.path.join(d4, "store.db.invocations.db"))
        try:
            mi = c.execute("SELECT value FROM meta WHERE key='max_inflight'").fetchone()
            lbw = c.execute("SELECT workers FROM launch_bound").fetchall()
        finally:
            c.close()
        verdict("POSITIVE CONTROL leg B' executed the pool: the pipelined [POOL] lines, journal v2 (max_inflight %s,"
                " launch_bound %s), the same bodies as a multiset" % (mi and mi[0], lbw),
                any(x.startswith("[POOL] workers 4 (pipelined path") for x in s4l) and
                any(x.startswith("[POOL] workers 4: reserved") for x in s4l) and mi == ("16",) and lbw == [(4,)] and
                sorted(b4) == sorted(ba) and POOL_LINE not in s4l,
                [x for x in s4l if x.startswith("[POOL]")])
        # [F2 delta, READY review d32fa75] DISCRIMINATOR (e): the DELTA's pool.py (F1 / F3 / F4) is the one leg B imported
        # and leg B' executed (its live guard and its time_scale-printing config line are new code on the pooled path)
        pf = (repB["ids"].get("judge_v2.pool") or {}).get("file")
        pblob = git_blob_lf_bytes(open(pf, "rb").read()) if pf else None
        head_p = git_head_blob("tools/analysis/judge_v2/pool.py")
        dn = count_names(pf, DELTA_IDS) if pf else {}
        verdict("DISCRIMINATOR (e) [delta] leg B imported judge_v2.pool from its checkout at the HEAD blob %s (got %s),"
                " carrying the delta identifiers %s; leg B' EXECUTED it: the '[RATE] live guard:' line and the '[RATE]"
                " config:' line with time_scale printed" % (head_p, pblob, json.dumps(dn, sort_keys=True)),
                pf is not None and os.path.normcase(pf).startswith(os.path.normcase(os.path.abspath(ROOT)) + os.sep) and
                pblob == head_p and all(v > 0 for v in dn.values()) and
                sum(x.startswith("[RATE] live guard:") for x in s4l) == 1 and
                any(x.startswith("[RATE] config:") and "time_scale" in x for x in s4l) and
                not any(x.startswith("[RATE]") for x in ob),
                [x[:120] for x in s4l if x.startswith("[RATE]")])
        # I13 on the real legs
        a_copy = os.path.join(base, "legA_store_copy.db")
        shutil.copyfile(os.path.join(da, "store.db"), a_copy)
        p = subprocess.run([sys.executable, os.path.abspath(__file__), "--i13", ROOT, "--store", a_copy, "--fixture",
                            fixture_json], capture_output=True, text=True, cwd=tempfile.gettempdir(), timeout=600)
        i13 = [x for x in p.stdout.splitlines() if x.startswith("I13-REAL")]
        verdict("I13 (real legs) leg B's writer REFUSES a relaunch of leg A's store on writer_blob",
                i13 and i13[-1].startswith("I13-REAL REFUSED") and "writer_blob" in i13[-1], i13)
        say("[INERT] EC1 %s: %d of %d comparisons PASS" % ("PASSES" if all(ok_all) else "FAILS", sum(ok_all),
                                                          len(ok_all)))
        say(scope_line(leg_a_root))
    finally:
        if keep:
            if os.path.exists(keep):
                raise SystemExit("[INERT] --keep %s exists (write-once)" % keep)
            shutil.copytree(base, keep)
            with open(os.path.join(keep, "INERTNESS_TRANSCRIPT.txt"), "x", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
        shutil.rmtree(base, ignore_errors=True)
    return 0 if all(ok_all) else 1


def _lf16_of(root):
    """common.package_lf16's rule over the 8 PACKAGE_FILES read from <root>/tools/analysis (CRLF folded)."""
    files = ("archv2_pilot/__init__.py", "archv2_pilot/common.py", "archv2_pilot/stage1.py", "archv2_pilot/supply.py",
             "archv2_pilot/pilot.py", "archv2_pilot/analysis.py", "archv2_pilot/accounting.py", "archv2_pilot/outcome.py")
    h = hashlib.sha256()
    for rel in files:
        h.update(rel.encode("utf-8") + b"\0")
        with open(os.path.join(root, "tools", "analysis", *rel.split("/")), "rb") as f:
            h.update(f.read().replace(b"\r\n", b"\n"))
    return h.hexdigest()[:16]


def _judge_pins_of(root):
    """judge_v2/writer.py and judge_v2/pool.py as git blobs (LF) in <root>; None when absent (leg A has no pool.py)."""
    got = {}
    for rel in ("judge_v2/writer.py", "judge_v2/pool.py"):
        p = os.path.join(root, "tools", "analysis", *rel.split("/"))
        got[rel] = git_blob_lf_bytes(open(p, "rb").read()) if os.path.exists(p) else None
    return got


def scope_line(leg_a_root):
    """[F5] the EC1 scope disclosure (module docstring): the two launch-manifest keys that differ through pilot.launch."""
    return ("[INERT] SCOPE (F5): EC1 is scored on the harness's replica of pilot.launch's accounting sequence; through"
            " pilot.launch at workers 1 the launch manifest ALSO differs BY DESIGN in exactly judge_v2_pins (leg A %s ->"
            " leg B %s) and archv2_pilot_lf16 (leg A %s -> leg B %s); not compared here" % (
                json.dumps(_judge_pins_of(leg_a_root), sort_keys=True), json.dumps(_judge_pins_of(ROOT), sort_keys=True),
                _lf16_of(leg_a_root), _lf16_of(ROOT)))


def main(argv):
    if "--leg" in argv:
        return leg(argv[argv.index("--leg") + 1], argv[argv.index("--work") + 1], argv[argv.index("--fixture") + 1],
                   int(argv[argv.index("--workers") + 1]))
    if "--i13" in argv:
        return open_leg_a_store_with_leg_b(argv[argv.index("--i13") + 1], argv[argv.index("--store") + 1],
                                           argv[argv.index("--fixture") + 1])
    if "--leg-a-root" not in argv:
        raise SystemExit(__doc__)
    keep = argv[argv.index("--keep") + 1] if "--keep" in argv else None
    return parent(os.path.abspath(argv[argv.index("--leg-a-root") + 1]), keep)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
