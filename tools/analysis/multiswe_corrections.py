"""MULTISWE-CORRECTIONS: re-read the MULTI-SWE-ADMISSION corpus with the two corrections of the post-run review
(5ba264c): the member-name join (mswe_join_v2) and the step-count cap read (mswe_term_v2). Zero LLM calls; CPU only;
no pool read; no pool file written.

QUEUE ITEM MULTISWE-CORRECTIONS (zero-call; lane CPU; "the `_-` vs `__` join fix + the CAP_HIT re-read"). The queue
entry carries registration null: THIS IS THE TOOL ONLY. Its --analyze (the file of record) waits for the registrar's
registration and a READY; --dry-run and --selftest post nothing and write nothing outside the scratch sandbox.
The corrections are defined by the record, verbatim in docs/judge_v2_program.md under the MULTI-SWE-ADMISSION
registration (the two "[CORRECTED 2026-09-22 by the MULTI-SWE-ADMISSION post-run review (... 5ba264c; defect 1 / defect
2 ...)]" brackets):
  defect 1: "every one of the 7,297 exit_error / submitted (exit_error) trajectories ends at exactly 51 entries with
    api_calls 50 and the last step 'exit due to runtime error: [...] Exceed maximum number of steps: 50' ... Any next
    registration on this corpus fixes mswe_term_v2 with the cap class read from the STEP-COUNT pile-up
    (len(trajectory) == 51 or the last-step text) BEFORE any count".
  defect 2: "The three python 20250426 SWE-agent zips ... name every member `org_-repo-pr.traj` where results.json and
    the other 93 zips use `org__repo-pr`; ... (replace("_-", "__", 1) joins 1,486 of 1,486) ... The next ingest aliases
    the member name as a versioned normaliser change (it touches the trajectory join, not the side)."
The review's recomputed figures this tool must reproduce on the corpus of record (printed, never scored there):
  join v2 / term v1: pooled strict D_c 12,792 / 25,709 = 0.4976; django 1,097 / 2,772 = 0.396; python EVAL 7-repo cell
    0.4448 (0.3283 as ingested); join v1 / term v2: TERMINATED 14,095, CAP_HIT 7,132, ERROR 4,482, UNKNOWN 0.

INPUTS (read-only). The DB of record experiment_results/agent/multiswe_result_2026-09-22.db, opened
mode=ro&immutable=1 after refusing a non-empty -wal / -journal (a failed precondition); its meta.ingest_complete must
be "1". The raw tree experiment_results/agent/multiswe_raw/2026-09-22/hf/<zip_path>: every MSWE-agent-class zip the DB
names is sha256-verified against submissions.zip_sha256 BEFORE it is read (refused on mismatch). multiswe_ingest.py
(blob-pinned by the record) is IMPORTED, never edited: mswe_term_v1, the class words and wilson come from it.

THE TWO VERSIONED RULES (fixed here, before any count on the corpus).
  mswe_join_v2(member key, universe): the ingest's key (the .traj basename without the suffix, else the top dir); if
    the key is NOT a checker id of that submission and key.replace("_-", "__", 1) IS, the replaced key is used (counted
    as aliased). A key already a checker id is never touched. Two members landing on one id REFUSE (collision).
  mswe_term_v2(exit_status, trajectory, ...): a missing archive / missing or unparsed trajectory is ERROR (as v1); a
    parsed trajectory whose length is CAP_STEPS + 1 = 51 OR whose LAST entry carries CAP_TEXT "Exceed maximum number of
    steps" in any of its string fields is CAP_HIT (the step-count pile-up, read FIRST); otherwise mswe_term_v1.
FAITHFULNESS GATE: the cell (join v1, term v1) recomputed from the zips must equal the DB's stored (exit_status,
mswe_term_v1) on EVERY MSWE-agent-class episode; any mismatch REFUSES every readout (the re-reader is then not the
ingest's).

READOUT (all four cells join {v1, v2} x term {v1, v2}, over the MSWE-agent-class episodes, the registered population;
denominator = every class episode, as the registered strict D_c): class counts; pooled strict D_c = TERMINATED and
checker-decided / class episodes, with Wilson 95%; per language; python per repo; the python EVAL cell (tasks.side ==
EVAL, the split of record, never TRAIN); the v1 -> v2 term transitions; the CAP signal breakdown (length only / text
only / both); members aliased and still unjoined. Everything printed is DESCRIPTIVE (the registration scored no D_c).

  python tools/analysis/multiswe_corrections.py --selftest             (sandbox fixture; asserts printed values)
  python tools/analysis/multiswe_corrections.py --dry-run [--db P] [--raw-dir P]   (prints; writes nothing)
  python tools/analysis/multiswe_corrections.py --analyze [--outcome P]  (write-once, mode "x"; after registration + READY)

MUTANTS: see the table in the commit message that adds this file (each run against --selftest, reverted).
"""
import argparse
import contextlib
import io
import json
import os
import sqlite3
import sys
import zipfile
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "ingest"))
sys.path.insert(0, HERE)
import multiswe_ingest as mi  # noqa: E402  (imported unedited; blob-pinned by the record)

DATE = "2026-09-22"
JOIN_V1, JOIN_V2 = "mswe_join_v1", "mswe_join_v2"
TERM_V1, TERM_V2 = "mswe_term_v1", "mswe_term_v2"
CAP_STEPS = 50
CAP_TEXT = "Exceed maximum number of steps"
CELLS = ((JOIN_V1, TERM_V1), (JOIN_V2, TERM_V1), (JOIN_V1, TERM_V2), (JOIN_V2, TERM_V2))
CLASSES = (mi.TERMINATED, mi.CAP_HIT, mi.ERROR, mi.UNKNOWN)


def default_outcome():
    return os.path.join(ROOT, "experiment_results", "agent", "multiswe_corrections.txt")


def script_sha():
    with open(os.path.abspath(__file__), "rb") as f:
        return mi.sha256_bytes(f.read().replace(b"\r\n", b"\n"))


# ------------------------------------------------------------------------------------------------ the two rules
def member_key(filename):
    base = filename.split("/")[-1]
    return base[:-5] if base.endswith(".traj") else filename.split("/")[0]


def member_map(names, universe, join_version):
    """{checker id: member filename}, aliased count. v2 aliases a non-id key whose first '_-' -> '__' is an id."""
    out, aliased = {}, 0
    for fn in names:
        k = member_key(fn)
        if join_version == JOIN_V2 and k not in universe:
            alt = k.replace("_-", "__", 1)
            if alt != k and alt in universe:
                k = alt
                aliased += 1
        if k in out:
            if join_version == JOIN_V2:
                raise SystemExit("[MULTISWE-CORRECTIONS] %s collision: members %s and %s both join %s: REFUSED" % (join_version, out[k], fn, k))
            continue  # v1 = the ingest's dict assignment; the ingest's first-wins is not reachable on unique names
        out[k] = fn
    return out, aliased


def last_text(entry):
    if isinstance(entry, dict):
        return " ".join(v for v in entry.values() if isinstance(v, str))
    return entry if isinstance(entry, str) else ""


def cap_signals(traj):
    if not isinstance(traj, list) or not traj:
        return False, False
    return len(traj) == CAP_STEPS + 1, CAP_TEXT in last_text(traj[-1])


def mswe_term_v2(exit_status, traj, trajectory_present, archive_present=True, parsed=True):
    if not archive_present or not trajectory_present or not parsed:
        return mi.ERROR
    by_len, by_text = cap_signals(traj)
    if by_len or by_text:
        return mi.CAP_HIT
    return mi.mswe_term_v1(exit_status, True)


def read_traj(b):
    """(exit_status as the ingest stores it, trajectory, parsed) mirroring multiswe_ingest.ingest's parse."""
    try:
        tj = json.loads(b.decode("utf-8", "replace"))
        info = tj.get("info") if isinstance(tj, dict) else None
        info = info if isinstance(info, dict) else {}
        es = info.get("exit_status")
        traj = tj.get("trajectory") if isinstance(tj, dict) else None
        return es, traj, True
    except Exception:  # noqa: BLE001 - an unparsable artefact is ERROR, as the ingest counts it
        return None, None, False


# ------------------------------------------------------------------------------------------------ inputs
def open_db_ro(path):
    if not os.path.exists(path):
        raise SystemExit("[MULTISWE-CORRECTIONS] DB %s absent: REFUSED" % path)
    for suf in ("-wal", "-journal"):
        side = path + suf
        if os.path.exists(side) and os.path.getsize(side) > 0:
            raise SystemExit("[MULTISWE-CORRECTIONS] %s is non-empty: failed precondition, REFUSED (nothing read)" % side)
    return sqlite3.connect("file:%s?mode=ro&immutable=1" % os.path.abspath(path).replace("\\", "/"), uri=True)


def load(db_path):
    c = open_db_ro(db_path)
    c.row_factory = sqlite3.Row
    meta = {r["key"]: r["value"] for r in c.execute("SELECT key, value FROM meta")}
    if meta.get("ingest_complete") != "1":
        raise SystemExit("[MULTISWE-CORRECTIONS] the DB was not written from a complete ingest: REFUSED")
    agents = {r["agent"]: dict(r) for r in c.execute("SELECT agent, swe_agent_class FROM agents")}
    tasks = {r["instance_id"]: dict(r) for r in c.execute("SELECT instance_id, language, family_id, side FROM tasks")}
    subs = [dict(r) for r in c.execute("SELECT language, dir_name, agent, zip_path, zip_sha256 FROM submissions")]
    eps = [dict(r) for r in c.execute("SELECT instance_id, agent, language, submission_dir, checker_status, checker_decided,"
                                      " trajectory_present, exit_status, mswe_term_v1 FROM episodes")]
    c.close()
    cls_eps = [e for e in eps if agents[e["agent"]]["swe_agent_class"]]
    if not cls_eps:
        raise SystemExit("[MULTISWE-CORRECTIONS] 0 MSWE-agent-class episodes in %s: REFUSED (nothing to re-read)" % db_path)
    return meta, agents, tasks, subs, cls_eps


def reread(db_path, raw_dir):
    """Per class episode: the term class in all four cells + the cap signals; asserts the faithfulness gate."""
    meta, agents, tasks, subs, cls_eps = load(db_path)
    by_sub = defaultdict(list)
    for e in cls_eps:
        by_sub[(e["language"], e["submission_dir"], e["agent"])].append(e)
    stats = Counter()
    rows = []
    for s in subs:
        key = (s["language"], s["dir_name"], s["agent"])
        group = by_sub.pop(key, [])
        if not group:
            continue
        zh = None
        if s["zip_path"]:
            zp = mi.local_hf_path(raw_dir, s["zip_path"])
            if not os.path.exists(zp):
                raise SystemExit("[MULTISWE-CORRECTIONS] zip %s named by the DB is absent: REFUSED" % zp)
            got = mi.sha256_file(zp)
            if got != s["zip_sha256"]:
                raise SystemExit("[MULTISWE-CORRECTIONS] zip %s sha256 %s != DB %s: REFUSED" % (zp, got[:16], (s["zip_sha256"] or "")[:16]))
            zh = zipfile.ZipFile(zp)
            stats["zips_verified"] += 1
        universe = {e["instance_id"] for e in group}
        names = [zi.filename for zi in zh.infolist() if not zi.is_dir()] if zh else []
        maps = {}
        for jv in (JOIN_V1, JOIN_V2):
            maps[jv], al = member_map(names, universe, jv)
            stats["aliased_" + jv] += al
        for e in group:
            r = {"e": e, "lang": e["language"], "fam": tasks[e["instance_id"]]["family_id"], "side": tasks[e["instance_id"]]["side"],
                 "decided": int(e["checker_decided"] or 0)}
            for jv in (JOIN_V1, JOIN_V2):
                if zh is None:
                    es, traj, present, parsed, arch = mi.MISSING_ARCHIVE, None, False, True, False
                elif e["instance_id"] not in maps[jv]:
                    es, traj, present, parsed, arch = mi.MISSING_TRAJ, None, False, True, True
                else:
                    raw_es, traj, parsed = read_traj(zh.read(maps[jv][e["instance_id"]]))
                    present, arch = True, True
                    es = (raw_es if isinstance(raw_es, str) else mi.ABSENT_STATUS) if parsed else mi.UNPARSED_TRAJ
                    if not parsed:
                        traj = None
                t1 = mi.mswe_term_v1(raw_es if (present and parsed) else None, present, archive_present=arch, parsed=parsed)
                t2 = mswe_term_v2(raw_es if (present and parsed) else None, traj, present, archive_present=arch, parsed=parsed)
                r[(jv, TERM_V1)], r[(jv, TERM_V2)] = t1, t2
                r["sig_" + jv] = cap_signals(traj) if present and parsed else (False, False)
                if jv == JOIN_V1:
                    r["es_v1"] = es
                if jv == JOIN_V2 and present and e["instance_id"] not in maps[JOIN_V1]:
                    stats["episodes_joined_by_v2"] += 1
            rows.append(r)
        if zh is not None:
            stats["unjoined_members_" + JOIN_V2] += len(set(maps[JOIN_V2]) - universe)
            zh.close()
    orphan = sum(len(v) for v in by_sub.values())
    if orphan:
        raise SystemExit("[MULTISWE-CORRECTIONS] %d class episodes have no submissions row: REFUSED" % orphan)
    bad = [r for r in rows if (r["es_v1"], r[(JOIN_V1, TERM_V1)]) != (r["e"]["exit_status"], r["e"]["mswe_term_v1"])]
    if bad:
        b = bad[0]
        raise SystemExit("[MULTISWE-CORRECTIONS] FAITHFULNESS GATE: %d of %d class episodes re-read under (%s, %s) differ from the DB"
                         " (first %s / %s: re-read %s %s, DB %s %s): REFUSED"
                         % (len(bad), len(rows), JOIN_V1, TERM_V1, b["e"]["instance_id"], b["e"]["agent"], b["es_v1"], b[(JOIN_V1, TERM_V1)],
                            b["e"]["exit_status"], b["e"]["mswe_term_v1"]))
    return meta, rows, stats


# ------------------------------------------------------------------------------------------------ readout
def dc(rows, cell):
    num = sum(1 for r in rows if r[cell] == mi.TERMINATED and r["decided"])
    return num, len(rows)


def fmt_dc(num, den):
    lo, hi = mi.wilson(num, den)
    return "%d / %d = %.4f [%.4f, %.4f]" % (num, den, num / den if den else float("nan"), lo, hi)


def render(meta, rows, stats, sha):
    L = []
    L.append("MULTISWE-CORRECTIONS (zero LLM calls; CPU; no pool read) script_sha=%s (LF)" % sha)
    L.append("corpus=%s db_script_sha=%s ingest term_version=%s" % (meta.get("corpus"), meta.get("script_sha"), meta.get("term_version")))
    L.append("population: MSWE-agent-class episodes %d (denominator of every D_c below); zips sha-verified %d" % (len(rows), stats["zips_verified"]))
    L.append("FAITHFULNESS GATE: (%s, %s) re-read == DB exit_status + mswe_term_v1 on %d of %d: PASSED" % (JOIN_V1, TERM_V1, len(rows), len(rows)))
    L.append("join: members aliased by %s %d; class episodes newly joined %d; members still without a checker row under %s %d"
             % (JOIN_V2, stats["aliased_" + JOIN_V2], stats["episodes_joined_by_v2"], JOIN_V2, stats["unjoined_members_" + JOIN_V2]))
    for cell in CELLS:
        cls = Counter(r[cell] for r in rows)
        L.append("CELL %s / %s: classes %s | pooled strict D_c %s" % (cell[0], cell[1], " ".join("%s=%d" % (k, cls[k]) for k in CLASSES),
                                                                     fmt_dc(*dc(rows, cell))))
    for cell in CELLS:
        per = []
        for lang in mi.LANGUAGES:
            sub = [r for r in rows if r["lang"] == lang]
            if sub:
                n, d = dc(sub, cell)
                per.append("%s %d/%d=%.3f" % (lang, n, d, n / d))
        L.append("  per language %s / %s: %s" % (cell[0], cell[1], "; ".join(per)))
    py = [r for r in rows if r["lang"] == "python"]
    fams = sorted({r["fam"] for r in py})
    for cell in ((JOIN_V1, TERM_V1), (JOIN_V2, TERM_V1), (JOIN_V2, TERM_V2)):
        parts = []
        for f in fams:
            n, d = dc([r for r in py if r["fam"] == f], cell)
            parts.append("%s %d/%d=%.3f" % (f.split("/")[-1], n, d, n / d))
        L.append("  python per repo %s / %s: %s" % (cell[0], cell[1], "; ".join(parts)))
    ev = [r for r in py if r["side"] == "EVAL"]
    for cell in CELLS:
        n, d = dc(ev, cell)
        L.append("  python EVAL cell (tasks.side == EVAL; %d repos) %s / %s: %s"
                 % (len({r["fam"] for r in ev}), cell[0], cell[1], fmt_dc(n, d) if d else "0 / 0 (no EVAL python episode)"))
    tr = Counter((r[(JOIN_V2, TERM_V1)], r[(JOIN_V2, TERM_V2)]) for r in rows)
    L.append("term transitions v1 -> v2 under %s: %s" % (JOIN_V2, "; ".join("%s->%s %d" % (a, b, n) for (a, b), n in sorted(tr.items()) if a != b) or "none"))
    sig = Counter(r["sig_" + JOIN_V2] for r in rows if r[(JOIN_V2, TERM_V2)] == mi.CAP_HIT)
    L.append("CAP signals under %s / %s: length==%d only %d; text only %d; both %d; status token only (the v1 map) %d"
             % (JOIN_V2, TERM_V2, CAP_STEPS + 1, sig[(True, False)], sig[(False, True)], sig[(True, True)], sig[(False, False)]))
    L.append("Every figure above is DESCRIPTIVE: the registration of MULTI-SWE-ADMISSION printed D_c and scored none; no criterion moves.")
    return "\n".join(L) + "\n"


def run(db_path, raw_dir, outcome=None):
    meta, rows, stats = reread(db_path, raw_dir)
    text = render(meta, rows, stats, script_sha())
    if outcome:
        with open(outcome, "x", encoding="utf-8", newline="\n") as f:
            f.write(text)
    return text


# ------------------------------------------------------------------------------------------------ selftest
def _traj(status, n_steps, last="ok"):
    t = [{"action": "a%d" % i, "observation": "", "response": "r", "thought": "t"} for i in range(n_steps - 1)]
    t.append({"action": "last", "observation": "", "response": last, "thought": last})
    return json.dumps({"trajectory": t, "info": {"exit_status": status, "model_stats": {"api_calls": n_steps - 1}}})


def _fixture(d, tamper=False, collide=False, wal=False, incomplete=False, no_class=False):
    """DB + raw tree. Hand-computed truth in selftest(). Python repo org/repo EVAL, org/other TRAIN, ab/c_-d EVAL."""
    raw = os.path.join(d, "raw")
    os.makedirs(os.path.join(raw, "hf", "python"), exist_ok=True)
    capmsg = "exit due to runtime error: [x] Exceed maximum number of steps: 50"
    za = {"org__repo-1.traj": _traj("submitted", 5),                       # TERMINATED all cells
          "org__repo-2.traj": _traj("submitted (exit_error)", 51, capmsg),  # v1 ERROR, v2 CAP_HIT (both signals)
          "org__repo-3.traj": _traj("exit_error", 10, "runtime error: other"),  # ERROR all cells
          "org__other-5.traj": _traj("submitted", 51),                      # v1 TERMINATED, v2 CAP_HIT (length only)
          "org__other-6.traj": _traj("exit_error", 30, capmsg),             # v1 ERROR, v2 CAP_HIT (text only)
          "org__repo-7.traj": _traj("submitted", 4)}                        # TERMINATED all cells, checker NOT decided
    #  org__repo-4: no member -> MISSING_TRAJ in all cells
    zb = {"org_-repo-1.traj": _traj("submitted", 3),                        # v1 MISSING, v2 TERMINATED
          "org_-repo-2.traj": _traj("exit_cost", 4),                        # v1 MISSING, v2 CAP_HIT (v1 token)
          "ab_-c_-d-8.traj": _traj("submitted", 2),                         # v2: ab__c_-d-8 (replace ONCE)
          "zz_-nope-9.traj": _traj("submitted", 2)}                         # not a checker id under any rule
    if collide:
        zb["org__repo-1.traj"] = _traj("submitted", 3)
    files = {}
    for name, members in (("20250101_SWE-agent_M1.zip", za), ("20250101_SWE-agent_M2.zip", zb)):
        p = os.path.join(raw, "hf", "python", name)
        with zipfile.ZipFile(p, "w") as z:
            for k, v in members.items():
                z.writestr(k, v)
        files[name] = mi.sha256_file(p)
    db = os.path.join(d, "fx.db")
    c = sqlite3.connect(db)
    c.executescript("""
      CREATE TABLE meta(key TEXT, value TEXT);
      CREATE TABLE agents(agent TEXT, swe_agent_class INTEGER);
      CREATE TABLE tasks(instance_id TEXT, language TEXT, family_id TEXT, side TEXT);
      CREATE TABLE submissions(language TEXT, dir_name TEXT, agent TEXT, zip_path TEXT, zip_sha256 TEXT);
      CREATE TABLE episodes(instance_id TEXT, agent TEXT, language TEXT, submission_dir TEXT, checker_status TEXT, checker_decided INTEGER,
                            trajectory_present INTEGER, exit_status TEXT, mswe_term_v1 TEXT);""")
    c.executemany("INSERT INTO meta VALUES (?,?)", [("ingest_complete", "0" if incomplete else "1"), ("corpus", "fixture"),
                                                     ("script_sha", "fixture"), ("term_version", "mswe_term_v1")])
    c.executemany("INSERT INTO agents VALUES (?,?)", [("m1", 0 if no_class else 1), ("m2", 0 if no_class else 1), ("m3", 0 if no_class else 1), ("oh", 0)])
    tasks = [("org__repo-1", "org/repo", "EVAL"), ("org__repo-2", "org/repo", "EVAL"), ("org__repo-3", "org/repo", "EVAL"),
             ("org__repo-4", "org/repo", "EVAL"), ("org__repo-7", "org/repo", "EVAL"), ("org__other-5", "org/other", "TRAIN"), ("org__other-6", "org/other", "TRAIN"),
             ("ab__c_-d-8", "ab/c_-d", "EVAL"), ("j__k-1", "j/k", "TRAIN")]
    c.executemany("INSERT INTO tasks VALUES (?,?,?,?)", [(i, "java" if i.startswith("j__") else "python", f, s) for i, f, s in tasks])
    c.executemany("INSERT INTO submissions VALUES (?,?,?,?,?)", [
        ("python", "20250101_SWE-agent_M1", "m1", "python/20250101_SWE-agent_M1.zip", files["20250101_SWE-agent_M1.zip"]),
        ("python", "20250101_SWE-agent_M2", "m2", "python/20250101_SWE-agent_M2.zip",
         ("0" * 64) if tamper == "sha" else files["20250101_SWE-agent_M2.zip"]),
        ("java", "20250101_MSWE-agent_M3", "m3", None, None), ("python", "20250101_OpenHands_X", "oh", None, None)])
    E, T, ER = mi.TERMINATED, mi.CAP_HIT, mi.ERROR
    ep = [  # (iid, agent, lang, sub, decided, present, exit_status as the ingest stored it, v1 class)
        ("org__repo-1", "m1", "python", "20250101_SWE-agent_M1", 1, 1, "submitted", E),
        ("org__repo-2", "m1", "python", "20250101_SWE-agent_M1", 1, 1, "submitted (exit_error)", ER),
        ("org__repo-3", "m1", "python", "20250101_SWE-agent_M1", 0, 1, "exit_error", ER),
        ("org__repo-4", "m1", "python", "20250101_SWE-agent_M1", 1, 0, mi.MISSING_TRAJ, ER),
        ("org__other-5", "m1", "python", "20250101_SWE-agent_M1", 1, 1, "submitted", E),
        ("org__other-6", "m1", "python", "20250101_SWE-agent_M1", 1, 1, "exit_error", ER),
        ("org__repo-7", "m1", "python", "20250101_SWE-agent_M1", 0, 1, "submitted", E),
        ("org__repo-1", "m2", "python", "20250101_SWE-agent_M2", 1, 0, mi.MISSING_TRAJ, ER),
        ("org__repo-2", "m2", "python", "20250101_SWE-agent_M2", 1, 0, mi.MISSING_TRAJ, ER),
        ("ab__c_-d-8", "m2", "python", "20250101_SWE-agent_M2", 1, 0, mi.MISSING_TRAJ, ER),
        ("j__k-1", "m3", "java", "20250101_MSWE-agent_M3", 1, 0, mi.MISSING_ARCHIVE, ER),
        ("org__repo-1", "oh", "python", "20250101_OpenHands_X", 1, 0, None, mi.UNSTAMPED)]
    if tamper == "term":
        ep[0] = ep[0][:7] + (ER,)
    c.executemany("INSERT INTO episodes VALUES (?,?,?,?,?,?,?,?,?)", [(i, a, l, s, "x", dcd, pr, es, t) for i, a, l, s, dcd, pr, es, t in ep])
    c.commit()
    c.close()
    if wal:
        with open(db + "-wal", "wb") as f:
            f.write(b"x")
    return db, raw


def _refuses(fn, needle):
    try:
        fn()
    except SystemExit as e:
        assert needle in str(e), (needle, str(e))
        return
    raise AssertionError("no refusal containing %r" % needle)


def selftest():
    import scratch_dir
    with scratch_dir.scratch("mswecorr_") as d:
        db, raw = _fixture(os.path.join(d, "ok"))
        out = os.path.join(d, "ok", "outcome.txt")
        text = run(db, raw, outcome=out)
        print(text)
        want = [
            "population: MSWE-agent-class episodes 11 (denominator of every D_c below); zips sha-verified 2",
            "FAITHFULNESS GATE: (mswe_join_v1, mswe_term_v1) re-read == DB exit_status + mswe_term_v1 on 11 of 11: PASSED",
            "join: members aliased by mswe_join_v2 3; class episodes newly joined 3; members still without a checker row under mswe_join_v2 1",
            # v1/v1: TERMINATED repo-1(m1), other-5 = 2 (both decided) ; ERROR 8
            "CELL mswe_join_v1 / mswe_term_v1: classes TERMINATED=3 CAP_HIT=0 ERROR=8 UNKNOWN=0 | pooled strict D_c 2 / 11 = 0.1818",
            # v2/v1: + m2 repo-1 TERMINATED, m2 repo-2 CAP_HIT (exit_cost), ab__c_-d-8 TERMINATED -> T=4, C=1, E=5
            "CELL mswe_join_v2 / mswe_term_v1: classes TERMINATED=5 CAP_HIT=1 ERROR=5 UNKNOWN=0 | pooled strict D_c 4 / 11 = 0.3636",
            # v1/v2: repo-2, other-5 (len), other-6 (text) -> CAP 3; T = repo-1 = 1; E = repo-3, repo-4, 3 x m2, m3 = 6
            "CELL mswe_join_v1 / mswe_term_v2: classes TERMINATED=2 CAP_HIT=3 ERROR=6 UNKNOWN=0 | pooled strict D_c 1 / 11 = 0.0909",
            "CELL mswe_join_v2 / mswe_term_v2: classes TERMINATED=4 CAP_HIT=4 ERROR=3 UNKNOWN=0 | pooled strict D_c 3 / 11 = 0.2727",
            "  per language mswe_join_v2 / mswe_term_v1: java 0/1=0.000; python 4/10=0.400",
            "  python per repo mswe_join_v2 / mswe_term_v1: c_-d 1/1=1.000; other 1/2=0.500; repo 2/7=0.286",
            # EVAL = org/repo (6 episodes) + ab/c_-d (1); TRAIN org/other excluded
            "  python EVAL cell (tasks.side == EVAL; 2 repos) mswe_join_v1 / mswe_term_v1: 1 / 8 = 0.1250",
            "  python EVAL cell (tasks.side == EVAL; 2 repos) mswe_join_v2 / mswe_term_v1: 3 / 8 = 0.3750",
            "term transitions v1 -> v2 under mswe_join_v2: ERROR->CAP_HIT 2; TERMINATED->CAP_HIT 1",
            "CAP signals under mswe_join_v2 / mswe_term_v2: length==51 only 1; text only 1; both 1; status token only (the v1 map) 1",
        ]
        for w in want:
            assert w in text, "MISSING: %s" % w
        with open(out, encoding="utf-8") as f:
            assert f.read() == text
        _refuses_exists = False
        try:
            run(db, raw, outcome=out)
        except FileExistsError:
            _refuses_exists = True
        assert _refuses_exists, "write-once outcome was overwritten"
        # refusals, each by its message
        db2, raw2 = _fixture(os.path.join(d, "term"), tamper="term")
        _refuses(lambda: run(db2, raw2), "FAITHFULNESS GATE: 1 of 11")
        db3, raw3 = _fixture(os.path.join(d, "sha"), tamper="sha")
        _refuses(lambda: run(db3, raw3), "sha256")
        db4, raw4 = _fixture(os.path.join(d, "col"), collide=True)
        _refuses(lambda: run(db4, raw4), "collision")
        db5, raw5 = _fixture(os.path.join(d, "wal"), wal=True)
        _refuses(lambda: run(db5, raw5), "-wal is non-empty")
        db6, raw6 = _fixture(os.path.join(d, "inc"), incomplete=True)
        _refuses(lambda: run(db6, raw6), "complete ingest")
        db7, raw7 = _fixture(os.path.join(d, "none"), no_class=True)
        _refuses(lambda: run(db7, raw7), "0 MSWE-agent-class episodes")
        # main() modes: --dry-run writes nothing; --analyze on an existing outcome refuses
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            main(["--dry-run", "--db", db, "--raw-dir", raw, "--outcome", os.path.join(d, "ok", "dry.txt")])
        assert not os.path.exists(os.path.join(d, "ok", "dry.txt")), "--dry-run wrote its outcome"
        assert "dry-run: nothing written" in buf.getvalue() and "pooled strict D_c 3 / 11 = 0.2727" in buf.getvalue()
        out2 = os.path.join(d, "ok", "analyze.txt")
        with contextlib.redirect_stdout(io.StringIO()):
            main(["--analyze", "--db", db, "--raw-dir", raw, "--outcome", out2])
        assert os.path.exists(out2)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                main(["--analyze", "--db", db, "--raw-dir", raw, "--outcome", out2])
            raise AssertionError("--analyze overwrote its outcome")
        except FileExistsError:
            pass
        # --analyze on an existing outcome refuses BEFORE any input is read (a missing DB would otherwise refuse first)
        try:
            main(["--analyze", "--db", os.path.join(d, "absent.db"), "--raw-dir", raw, "--outcome", out2])
            raise AssertionError("--analyze ran on an existing outcome")
        except FileExistsError:
            pass
        # a key that IS a checker id is never aliased, even when its '_-' image is also an id
        mm, al = member_map(["p__q_-r-3.traj", "p__q__r-3.traj"], {"p__q_-r-3", "p__q__r-3"}, JOIN_V2)
        assert (mm, al) == ({"p__q_-r-3": "p__q_-r-3.traj", "p__q__r-3": "p__q__r-3.traj"}, 0), (mm, al)
    print("selftest OK (4 cells, per-language / per-repo / EVAL cell, transitions, signals, write-once, 6 refusals, both modes)")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", default=mi.default_db(DATE))
    ap.add_argument("--raw-dir", default=mi.default_raw_dir(DATE))
    ap.add_argument("--outcome", default=default_outcome())
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        print("script_sha=%s (LF)" % script_sha())
        selftest()
        return 0
    if a.dry_run == a.analyze:
        ap.error("exactly one of --dry-run / --analyze / --selftest")
    if a.analyze and os.path.exists(a.outcome):
        raise FileExistsError("%s exists; write-once" % a.outcome)
    text = run(a.db, a.raw_dir, outcome=a.outcome if a.analyze else None)
    print(text, end="")
    print("dry-run: nothing written" if a.dry_run else "wrote %s" % a.outcome)
    return 0


if __name__ == "__main__":
    sys.exit(main())
