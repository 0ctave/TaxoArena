"""g10_compare.py: G10 of RP12 ARCH-V2-E-T (determinism and stamp), plus the pointer file (READY_rp12_et C-4). ZERO calls.

REGISTRATION OF RECORD: docs/judge_v2_program.md L22028-L22060 (0a0361b): "G10 (determinism; set readout, the POINT decides):
HELD iff B0 and B0' are byte-identical on the declared artefact set (final dag snapshot, gate_ids.json, validation CSVs;
timestamp fields listed at READY and excluded) AND the snapshot stamp equals the TOML, the build manifest and the pointer file.
FAILED on any byte difference or stamp mismatch. The starved-pass accept count is printed (descriptive). A FAILED G10 stops
the lane: no other readout is scored."

THE DECLARED ARTEFACT SET, per run dir (<outputDir>/seed_42), compared B0 against B0' (the member builds and the flatLeaf graft):
  A1 dag_snapshots.jsonl, the LAST line (the final dag snapshot), as JSON
  A2 gate_ids.json, as JSON
  A3 validation/*.csv, every file, byte for byte (the set of names must be equal too)
  A4 the snapshot row in snapshots.db (graph, metrics, settings, reserved_queries, config), as JSON
  A5 diagnostics/run_manifest.json, as JSON
EXCLUDED (READY_rp12_et C-4's list, and the builder's additions, each a function of the run's wall clock or of its output dir):
  snapshots.id, snapshots.timestamp, snapshots.log_uuid (A4 reads none of them); manifest started_at_millis, finished_at_millis,
  duration_ms; headless_run.log and performance_report.json (not in the set); reserved_pool_meta.created_at (not in the set).
  Builder's additions, declared for the READY: manifest config_path, config_sha256 and proposal_memo_digest_ms (B0' is B0's TOML
  with another outputDir, so its path and sha differ by construction; the digest is a timing); the stamp's configSha256Lf inside
  A4's settings and A5's split_v2 (the same reason; the STAMP CHECK below reads it against each run's own TOML).
THE STAMP CHECK, per run (the second conjunct): S1 the snapshot's settings.buildStamp is non-null; S2 it equals the manifest's
split_v2 field for field (toManifest's names); S3 its configSha256Lf equals the sha256 of the LF rendering of the run's
diagnostics/config.toml AND of the committed TOML given; S4 it equals the pointer file's entry for the run (stamp, snapshot id,
TOML sha).
THE POINTER FILE (C-4: "undefined" until now): experiment_configs/rp12/objects_of_record.json, written ONCE by --write-pointer
after the B0 builds: {"format": "taxoarena-objects-of-record-v1", "entries": {name: {"snapshot_id", "stamp", "toml",
"toml_sha256_lf", "manifest_sha256_lf"}}}. The snapshot id of a run is read from its headless_run.log ("... Snapshot ID: <id>").
Starved-pass accept count: printed from the manifest key starved_pass_accepts when the engine records it, else "NOT RECORDED by
the engine" (the engine has no such key today; the READY decides whether that is acceptable).

  python tools/analysis/g10_compare.py --selftest
  python tools/analysis/g10_compare.py --write-pointer experiment_configs/rp12/objects_of_record.json --snapshot-db snapshots.db \
         --entry "B0/bbh=experiment_results/archv2/rp12/B0/bbh/seed_42|experiment_configs/rp12/B0/bbh.toml" ...
  python tools/analysis/g10_compare.py --g10 --pointer experiment_configs/rp12/objects_of_record.json --snapshot-db snapshots.db \
         --pair "B0/bbh=<B0 run dir>|<B0 toml>,B0p/bbh=<B0' run dir>|<B0' toml>" ...
snapshots.db is opened read-only through data_v2.ro.open_ro (a non-empty -wal refuses: a failed precondition).

SELFTEST MUTANTS (run 2026-09-30 by a harness, one temporary edit at a time, reverted; G0 control survived): G1 first dag line
compared | G2 validation CSVs skipped | G3 the whole manifest excluded | G4 a non-timestamp key excluded | G5 S2 removed | G6 S3
against the committed TOML only | G7 S4 removed | G8 the verdict ignores stamp failures | G9 the pointer overwritable | G10 a
missing artefact read as equal | G11 the CLI exit code inverted: 11 of 11 killed.
[DELTA 2026-09-30 rp12-et3, READY_rp12_et2 D-8 as ruled (builds from ONE pinned detached worktree; registrar 390f9c6); insertion
only] precondition() REFUSES before any comparison (a failed precondition, never a FAILED G10) when a pair's manifests carry
different or missing commits, or when its TOMLs (comment lines dropped) differ beyond exactly one outputDir line (and, for a
graft, the member snapshot ids inside unionSnapshots). The git-state keys stay COMPARED in A5 (commit is not excluded; RV6).
D-9 stays "NOT RECORDED by the engine" (no starved-pass counter exists in the engine; the registrar notes it). Mutants: V0
control survived; V1 the precondition not called, V2 the commit check removed, V3 the TOML pair check removed, V4 the
outputDir count rule removed, V5 any quoted line allowed, RV6 commit excluded from A5: 6 of 6 killed.
[DELTA 2026-09-30 rp12-et4, READY_rp12_et3 D-13 / D-14; insertion only] D-13: both manifests without a commit refuse (the
reviewer's RV8, tested). D-14: an inline `unionSnapshots = [...]` line closes the list on its own line, so a later differing
quoted entry (a models line) is refused; tested with an inline pair. Mutants RV8 and D14 (the inline reset removed): killed.
[DELTA 2026-10-01 g10-r2, the G10 diagnosis 2b8f809a (G10 FAILED as registered; the R2 lane); insertion only] (1) A2:
gate_ids.json's split_v2.configSha256Lf (the run's TOML sha, different by construction between B0 and B0') is stripped
(strip_gate_toml: that key inside split_v2 only), as it already was in A4 / A5. (2) A GRAFT PAIR (both TOMLs declare
unionSnapshots; is_graft_toml) reads A1 / A2 as N/A (the graft writes no dag_snapshots.jsonl and no gate_ids.json; printed) and
compares A3, A4, A5; a member run without dag_snapshots.jsonl REFUSES (it used to raise); a graft TOML paired with a member TOML
refuses. (3) Orchestrator ruling on registrar R2-1 (44518b4f), option (A), pre-R2-data: A4 compares each node's queryIds as a
SET (membership_as_sets; the node-internal order is the 12-thread reassignQueries' and carries no meaning); every other A4 field,
the node order included, stays exact; A3 (the order-sampled metrics) stays byte for byte (EVAL-METRIC-DETERMINISM's guarantee).
Mutants: listed in the commit message.
[DELTA 2026-10-01 rp12-r2-lane; insertion only] --lane {r1,r2} (tools/analysis/rp12_lane.py; default r1 = the commands of
record, unchanged; --pointer defaults to the lane's pointer). lane_guard: a run dir, TOML or pointer of another lane REFUSES; in
lane r2 they must lie inside the r2 roots and the pointer must be experiment_configs/rp12_r2/objects_of_record.json; a run whose
snapshot id is an object of another lane's pointer refuses (g10 and write_pointer). Lane r2 prints one lane line first.
"""
import os
import sys
import json
import glob
import hashlib
import argparse
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from data_v2 import ro  # noqa: E402
import rp12_lane as LN  # noqa: E402

TAG = "[G10]"
POINTER_FORMAT = "taxoarena-objects-of-record-v1"
MANIFEST_EXCLUDED = ("started_at_millis", "finished_at_millis", "duration_ms", "config_path", "config_sha256", "proposal_memo_digest_ms")
STAMP_TOML_FIELD = ("configSha256Lf", "config_sha256_lf")
# V2BuildStamp field -> V2BuildStamp.toManifest() key (the Kotlin order)
STAMP_KEYS = (("rule", "rule"), ("poolId", "pool_id"), ("corpus", "corpus"), ("enginePoolFile", "engine_pool_file"),
              ("enginePoolSha256Lf", "engine_pool_sha256_lf"), ("sideExportPath", "side_export_path"),
              ("sideExportSha256Lf", "side_export_sha256_lf"), ("sideTableSha", "side_table_sha"), ("splitSha256", "split_sha256"),
              ("legacyPoolId", "legacy_pool_id"), ("trainRows", "train_rows"), ("reservedRows", "reserved_rows"),
              ("gateRows", "gate_rows"), ("sentinelRows", "sentinel_rows"), ("globalReservedKeys", "global_reserved_keys"),
              ("configSha256Lf", "config_sha256_lf"), ("seed", "seed"), ("constructionOrderShuffleSeed", "construction_order_shuffle_seed"),
              ("namespacesLoaded", "namespaces_loaded"))
SNAP_RE = re.compile(r"Snapshot ID: (\S+)")


def refuse(msg):
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def sha_lf_bytes(data):
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def sha_lf(path):
    with open(path, "rb") as f:
        return sha_lf_bytes(f.read())


def snapshot_id_of(run):
    p = os.path.join(run, "headless_run.log")
    if not os.path.isfile(p):
        refuse("%s has no headless_run.log (the snapshot id is read from it)" % run)
    ids = SNAP_RE.findall(open(p, encoding="utf-8", errors="replace").read())
    if len(set(ids)) != 1:
        refuse("%s: headless_run.log names %d snapshot id(s) %s; exactly one is required" % (run, len(set(ids)), sorted(set(ids))[:3]))
    return ids[0]


def snapshot_row(db, sid):
    conn = ro.open_ro(db)
    try:
        r = conn.execute("SELECT graph, metrics, settings, reserved_queries, config FROM snapshots WHERE id = ?", (sid,)).fetchone()
    finally:
        conn.close()
    if r is None:
        refuse("snapshot %s is not in %s" % (sid, db))
    return {k: (json.loads(v) if v else None) for k, v in zip(("graph", "metrics", "settings", "reserved_queries", "config"), r)}


def strip_stamp_toml(obj):
    """A deep copy with the stamp's TOML sha removed (settings.buildStamp.configSha256Lf / split_v2.config_sha256_lf)."""
    if isinstance(obj, dict):
        return {k: strip_stamp_toml(v) for k, v in obj.items() if k not in STAMP_TOML_FIELD}
    if isinstance(obj, list):
        return [strip_stamp_toml(v) for v in obj]
    return obj


def strip_gate_toml(gate):
    """G10-R2 (diagnosis 2b8f809a): A2's split_v2 carries the stamp's TOML sha too (configSha256Lf / config_sha256_lf), which
    differs by construction between B0 and B0' (another outputDir); it is removed there, and only there."""
    if isinstance(gate, dict) and isinstance(gate.get("split_v2"), dict):
        gate = dict(gate, split_v2={k: v for k, v in gate["split_v2"].items() if k not in STAMP_TOML_FIELD})
    return gate


def membership_as_sets(row):
    """G10-R2, orchestrator ruling on registrar R2-1 (44518b4f), option (A): A4 compares each node's query membership
    (graph.nodes[*].queryIds) as a SET; the node-internal order comes from the 12-thread reassignQueries and carries no
    meaning. Every other A4 field (node ids, order of the nodes, kappa, mu, weights, metrics, settings, ...) stays exact."""
    g = row.get("graph") if isinstance(row, dict) else None
    if not (isinstance(g, dict) and isinstance(g.get("nodes"), list)):
        return row
    nodes = [dict(n, queryIds=sorted(set(n["queryIds"]), key=lambda x: (isinstance(x, str), x)))
             if isinstance(n, dict) and isinstance(n.get("queryIds"), list) else n for n in g["nodes"]]
    return dict(row, graph=dict(g, nodes=nodes))


def is_graft_toml(toml):
    """G10-R2: a graft build's TOML declares unionSnapshots (a non-comment line starting with the key)."""
    return any(l.lstrip().startswith("unionSnapshots") for l in _toml_lines(toml))


def artefacts(run, db, graft=False):
    """{artefact name: comparable value} of the declared set (A1-A5), exclusions applied. G10-R2: for a graft pair A1 and A2
    are N/A (the graft writes no dag_snapshots.jsonl and no gate_ids.json) and are not read; A3-A5 are compared."""
    out = {}
    if not graft:
        dag = os.path.join(run, "dag_snapshots.jsonl")
        if not os.path.isfile(dag):
            refuse("%s has no dag_snapshots.jsonl (a member build writes one; only a graft pair reads A1 / A2 as N/A)" % run)
        lines = [l for l in open(dag, encoding="utf-8").read().splitlines() if l.strip()]
        if not lines:
            refuse("%s/dag_snapshots.jsonl is empty" % run)
        out["A1 dag_snapshots.jsonl (last line)"] = json.loads(lines[-1])
        out["A2 gate_ids.json"] = strip_gate_toml(json.load(open(os.path.join(run, "gate_ids.json"), encoding="utf-8"))) \
            if os.path.exists(os.path.join(run, "gate_ids.json")) else "<absent>"
    for p in sorted(glob.glob(os.path.join(run, "validation", "*.csv"))):
        out["A3 validation/" + os.path.basename(p)] = open(p, "rb").read().replace(b"\r\n", b"\n")
    out["A4 snapshot row"] = strip_stamp_toml(membership_as_sets(snapshot_row(db, snapshot_id_of(run))))
    man = json.load(open(os.path.join(run, "diagnostics", "run_manifest.json"), encoding="utf-8"))
    out["A5 run_manifest.json"] = strip_stamp_toml({k: v for k, v in man.items() if k not in MANIFEST_EXCLUDED})
    return out


def compare(run_a, run_b, db, graft=False):
    a, b = artefacts(run_a, db, graft), artefacts(run_b, db, graft)
    diffs = sorted(k for k in set(a) | set(b) if a.get(k, "<missing>") != b.get(k, "<missing>"))
    return diffs


def stamp_checks(run, toml, db, pointer=None, name=None):
    """-> list of failures (empty = S1-S4 hold)."""
    fails = []
    sid = snapshot_id_of(run)
    st = snapshot_row(db, sid)["settings"].get("buildStamp")
    if st is None:
        return ["S1 %s: the snapshot %s carries no buildStamp" % (run, sid)]
    man = json.load(open(os.path.join(run, "diagnostics", "run_manifest.json"), encoding="utf-8"))
    mv = man.get("split_v2")
    if mv is None:
        fails.append("S2 %s: the manifest has no split_v2" % run)
    else:
        for fk, mk in STAMP_KEYS:
            if fk == "namespacesLoaded" and st.get(fk) is None and mk not in mv:
                continue
            if st.get(fk) != mv.get(mk):
                fails.append("S2 %s: stamp %s = %r but manifest split_v2.%s = %r" % (run, fk, st.get(fk), mk, mv.get(mk)))
    run_toml = sha_lf(os.path.join(run, "diagnostics", "config.toml"))
    if st.get("configSha256Lf") != run_toml or st.get("configSha256Lf") != sha_lf(toml):
        fails.append("S3 %s: stamp configSha256Lf %s vs diagnostics/config.toml %s vs %s %s"
                     % (run, st.get("configSha256Lf"), run_toml, toml, sha_lf(toml)))
    if pointer is not None:
        e = pointer["entries"].get(name)
        if e is None:
            fails.append("S4 %s: no pointer entry" % name)
        elif (e["stamp"], e["snapshot_id"], e["toml_sha256_lf"]) != (st, sid, sha_lf(toml)):
            fails.append("S4 %s: the pointer entry differs from the run (stamp %s, snapshot %s, toml %s)"
                         % (name, e["stamp"] == st, e["snapshot_id"] == sid, e["toml_sha256_lf"] == sha_lf(toml)))
    return fails


def lane_guard(lane, root, pointer_path=None, runs_tomls=(), sids=()):
    """rp12-r2-lane: every path of the run belongs to `lane` (another lane's path REFUSES; in lane r2 every run dir, TOML and
    the pointer must lie INSIDE the r2 roots, and the pointer must be the lane's own); no snapshot of another lane's pointer."""
    inside = lane != "r1"
    if pointer_path is not None:
        LN.require(lane, [pointer_path], "pointer file", root=root, inside=inside)
        if inside and LN.rel(pointer_path, root) != LN.pointer(lane):
            refuse("lane %s reads only its own pointer %s, not %s" % (lane, LN.pointer(lane), pointer_path))
    for run, toml in runs_tomls:
        LN.require(lane, [run], "run dir", root=root, inside=inside)
        LN.require(lane, [toml], "TOML", root=root, inside=inside)
    LN.require_snapshots(lane, list(sids), root)


def write_pointer(out, entries, db, lane="r1", root=ROOT):
    if os.path.exists(out):
        refuse("%s exists; the pointer file is write-once" % out)
    lane_guard(lane, root, out, list(entries.values()), [snapshot_id_of(r) for r, _t in entries.values()])
    doc = {"format": POINTER_FORMAT, "entries": {}}
    for name, (run, toml) in entries.items():
        sid = snapshot_id_of(run)
        st = snapshot_row(db, sid)["settings"].get("buildStamp")
        if st is None:
            refuse("%s: snapshot %s carries no buildStamp" % (name, sid))
        doc["entries"][name] = {"snapshot_id": sid, "stamp": st, "toml": toml.replace("\\", "/"), "toml_sha256_lf": sha_lf(toml),
                                "manifest_sha256_lf": sha_lf(os.path.join(run, "diagnostics", "run_manifest.json"))}
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "x", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(doc, indent=1, sort_keys=True) + "\n")
    return doc


def _toml_lines(path):
    """Non-comment lines of a TOML's LF rendering (a line that is only a comment is dropped; the rest kept verbatim)."""
    text = open(path, "rb").read().replace(b"\r\n", b"\n").decode("utf-8")
    return [l for l in text.split("\n") if l.strip() and not l.lstrip().startswith("#")]


def toml_pair_diff(ta, tb):
    """READY_rp12_et2 D-8: B0' is B0's TOML up to the outputDir line (and, for a graft, the member snapshot ids inside
    unionSnapshots). -> the list of disallowed differences (empty = the pair is a replay)."""
    la, lb = _toml_lines(ta), _toml_lines(tb)
    if len(la) != len(lb):
        return ["line counts differ (%d vs %d)" % (len(la), len(lb))]
    bad, out_dir, in_snaps = [], 0, False
    for x, y in zip(la, lb):
        if x.lstrip().startswith("unionSnapshots"):
            in_snaps = True
        if x != y:
            if x.lstrip().startswith("outputDir") and y.lstrip().startswith("outputDir"):
                out_dir += 1
            elif in_snaps and re.match(r'^\s*"[^"]+",?\s*(#.*)?$', x) and re.match(r'^\s*"[^"]+",?\s*(#.*)?$', y):
                pass
            else:
                bad.append("%r vs %r" % (x, y))
        if in_snaps and (x.strip().startswith("]") or (x.lstrip().startswith("unionSnapshots") and "]" in x)):
            in_snaps = False                       # READY_rp12_et3 D-14: an inline list closes on its own line
    if out_dir != 1:
        bad.append("outputDir lines differing: %d (must be 1)" % out_dir)
    return bad


def precondition(pairs):
    """READY_rp12_et2 D-8, ruled operationally (the builds run from ONE pinned detached worktree): REFUSES (a failed
    precondition, never a FAILED G10) when a pair's manifests carry different or missing commits, or its TOMLs differ in more
    than outputDir (and a graft's member snapshot ids). Returns the printed lines."""
    lines = []
    for (na, ra, ta), (nb, rb, tb) in pairs:
        ca = json.load(open(os.path.join(ra, "diagnostics", "run_manifest.json"), encoding="utf-8")).get("commit")
        cb = json.load(open(os.path.join(rb, "diagnostics", "run_manifest.json"), encoding="utf-8")).get("commit")
        if not ca or ca != cb:
            refuse("D-8: %s was built at commit %r and %s at %r; B0 and B0' must be built from one pinned worktree" % (na, ca, nb, cb))
        bad = toml_pair_diff(ta, tb)
        if bad:
            refuse("D-8: %s and %s TOMLs are not a replay: %s" % (ta, tb, "; ".join(bad)))
        lines.append("%s D-8 precondition %s vs %s: one commit %s; the TOMLs differ in outputDir only" % (TAG, na, nb, ca))
    return lines


def g10(pairs, db, pointer_path, out=print, lane="r1", root=ROOT):
    """pairs: [((name_a, run_a, toml_a), (name_b, run_b, toml_b))]; prints per pair and the verdict; returns the word."""
    lane_guard(lane, root, pointer_path, [(r, t) for pr in pairs for (_n, r, t) in pr],
               [snapshot_id_of(r) for pr in pairs for (_n, r, _t) in pr])
    if lane != "r1":
        out("%s lane %s: pointer %s; every run dir and TOML inside %s/ and %s/" % (TAG, lane, LN.pointer(lane), LN.configs(lane), LN.results(lane)))
    pointer = json.load(open(pointer_path, encoding="utf-8"))
    if pointer.get("format") != POINTER_FORMAT:
        refuse("%s is not a %s file" % (pointer_path, POINTER_FORMAT))
    for line in precondition(pairs):
        out(line)
    held = True
    for (na, ra, ta), (nb, rb, tb) in pairs:
        ga, gb = is_graft_toml(ta), is_graft_toml(tb)
        if ga != gb:
            refuse("G10-R2: %s is %sa graft TOML and %s is %s; a pair is two members or two grafts" % (
                ta, "" if ga else "not ", tb, "one" if gb else "not"))
        if ga:
            out("%s %s vs %s: A1 / A2 N/A (a graft pair: the graft writes no dag_snapshots.jsonl and no gate_ids.json); A3-A5 compared"
                % (TAG, na, nb))
        diffs = compare(ra, rb, db, ga)
        if diffs:
            held = False
            out("%s %s vs %s: DIFFERS on %s" % (TAG, na, nb, "; ".join(diffs)))
        else:
            out("%s %s vs %s: byte-identical on the declared set (%s, exclusions applied)" % (TAG, na, nb, "A3-A5" if ga else "A1-A5"))
        for name, run, toml, ptr in ((na, ra, ta, pointer), (nb, rb, tb, None)):
            f = stamp_checks(run, toml, db, ptr, name)
            if f:
                held = False
                for x in f:
                    out("%s stamp %s" % (TAG, x))
            else:
                out("%s stamp %s: S1-S%d hold" % (TAG, name, 4 if ptr is not None else 3))
        man = json.load(open(os.path.join(ra, "diagnostics", "run_manifest.json"), encoding="utf-8"))
        out("%s starved-pass accept count (%s, descriptive): %s" % (TAG, na, man.get("starved_pass_accepts", "NOT RECORDED by the engine")))
    word = "HELD" if held else "FAILED"
    out("G10: %s%s" % (word, "" if held else " (a byte difference or a stamp mismatch): the lane STOPS, no other readout is scored"))
    return word


# ── selftest ────────────────────────────────────────────────────────────────────────────────────────────────────────

def _run(tmp, name, sid, db_rows, toml_text, stamp_over=None, csv_extra=b"", manifest_over=None, start=1000, graft=False, gate_over=None,
         qids=None):
    run = os.path.join(tmp, name, "seed_42")
    os.makedirs(os.path.join(run, "validation")); os.makedirs(os.path.join(run, "diagnostics"))
    if not graft:                                      # G10-R2: a graft writes neither A1 nor A2
        with open(os.path.join(run, "dag_snapshots.jsonl"), "w") as f:
            f.write(json.dumps({"iteration": 1, "nodes": [{"id": "r"}]}) + "\n" + json.dumps({"iteration": 7, "nodes": [{"id": "r"}, {"id": "a"}]}) + "\n")
        with open(os.path.join(run, "gate_ids.json"), "w") as f:
            # as the engine writes it: split_v2 carries the run's TOML sha (configSha256Lf), which differs B0 vs B0' (diagnosis)
            g = {"gate_ids": [1, 2], "split_v2": {"poolId": "pv2_x", "configSha256Lf": hashlib.sha256(toml_text.encode()).hexdigest()}}
            g.update(gate_over or {})
            json.dump(g, f)
    with open(os.path.join(run, "validation", "MAIN_x.csv"), "wb") as f:
        f.write(b"a,b\n1,2\n" + csv_extra)
    with open(os.path.join(run, "diagnostics", "config.toml"), "w", newline="") as f:
        f.write(toml_text.replace("\n", "\r\n"))       # the copy may be CRLF: S3 reads the LF rendering
    stamp = {"rule": "CK-CLOSE-v2", "poolId": "pv2_x", "corpus": "mc6", "enginePoolFile": "e.json", "enginePoolSha256Lf": "e" * 64,
             "sideExportPath": "s.tsv", "sideExportSha256Lf": "s" * 64, "sideTableSha": "t", "splitSha256": "p", "legacyPoolId": "pL",
             "trainRows": 5, "reservedRows": 3, "gateRows": 1, "sentinelRows": 0, "globalReservedKeys": 8,
             "configSha256Lf": hashlib.sha256(toml_text.encode()).hexdigest(), "seed": 42, "constructionOrderShuffleSeed": None,
             "namespacesLoaded": ["BBH"]}
    stamp.update(stamp_over or {})
    man = {"schema_version": 1, "commit": "c", "started_at_millis": start, "finished_at_millis": start + 5, "duration_ms": 5,
           "config_path": run, "config_sha256": "x" + name, "train_size": 5,
           "split_v2": {mk: stamp[fk] for fk, mk in STAMP_KEYS}}
    man.update(manifest_over or {})
    with open(os.path.join(run, "diagnostics", "run_manifest.json"), "w") as f:
        json.dump(man, f)
    with open(os.path.join(run, "headless_run.log"), "w") as f:
        f.write("... Successfully generated and saved snapshot. Snapshot ID: %s\n" % sid)
    q = qids or {"r": [3, 1, 2], "a": [5, 4]}
    db_rows.append((sid, {"graph": {"rootId": "r", "nodes": [{"id": "r", "childIds": ["a"], "kappa": 1.5, "queryIds": q["r"]},
                                                         {"id": "a", "childIds": [], "kappa": 2.5, "queryIds": q["a"]}]},
                          "metrics": {"leaves": 1}, "settings": {"maxDepth": 8, "buildStamp": stamp},
                          "reserved_queries": {"d": [1]}, "config": {"x": 1}}))
    return run


def _db(tmp, rows):
    p = os.path.join(tmp, "snapshots.db")
    c = ro.create_new(p)
    c.execute("CREATE TABLE snapshots (id TEXT PRIMARY KEY, timestamp TEXT, description TEXT, graph TEXT, metrics TEXT, settings TEXT,"
              " log_uuid TEXT, reserved_queries TEXT, config TEXT)")
    for i, (sid, r) in enumerate(rows):
        c.execute("INSERT INTO snapshots VALUES (?,?,?,?,?,?,?,?,?)", (sid, "t%d" % i, "d", json.dumps(r["graph"]), json.dumps(r["metrics"]),
                                                                        json.dumps(r["settings"]), "u%d" % i, json.dumps(r["reserved_queries"]),
                                                                        json.dumps(r["config"])))
    c.commit(); c.close()
    return p


def selftest():
    import io, tempfile, shutil, contextlib
    fails, ran = [], []

    def case(name, fn):
        ran.append(name)
        tmp = tempfile.mkdtemp(prefix="g10st_")
        try:
            fn(tmp)
            print("  ok   " + name)
        except (AssertionError, SystemExit, Exception) as e:
            fails.append(name)
            print("  FAIL %s: %s: %s" % (name, type(e).__name__, e))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def setup(tmp, b_stamp=None, b_csv=b"", b_man=None, b_toml_extra="", graft=False, b_gate=None, b_qids=None):
        rows = []
        ta = os.path.join(tmp, "a.toml"); tb = os.path.join(tmp, "b.toml")
        un_a = 'unionSnapshots = [\n    "S1",\n]\n' if graft else ""
        un_b = 'unionSnapshots = [\n    "T1",\n]\n' if graft else ""
        tta = un_a + 'seed = 42\noutputDir = "A"\n'; ttb = un_b + 'seed = 42\noutputDir = "B"\n' + b_toml_extra
        open(ta, "w", newline="\n").write(tta); open(tb, "w", newline="\n").write(un_b + 'seed = 42\noutputDir = "B"\n')
        ra = _run(tmp, "A", "sidA", rows, tta, start=1000, graft=graft)
        rb = _run(tmp, "B", "sidB", rows, ttb, stamp_over=b_stamp, csv_extra=b_csv, manifest_over=b_man, start=9999, graft=graft,
                  gate_over=b_gate, qids=b_qids)
        db = _db(tmp, rows)
        ptr = os.path.join(tmp, "ptr", "objects_of_record.json")
        with contextlib.redirect_stdout(io.StringIO()):
            write_pointer(ptr, {"B0/x": (ra, ta)}, db)
        return [(("B0/x", ra, ta), ("B0p/x", rb, tb))], db, ptr

    def d8(tmp):
        pairs, db, ptr = setup(tmp)
        (na, ra, ta), (nb, rb, tb) = pairs[0]
        mp = os.path.join(rb, "diagnostics", "run_manifest.json")
        m = json.load(open(mp)); m["commit"] = "other"; open(mp, "w").write(json.dumps(m))
        try:
            run_g10(pairs, db, ptr)
            raise AssertionError("different commits not refused")
        except SystemExit as e:
            assert str(e) == "%s REFUSED: D-8: B0/x was built at commit 'c' and B0p/x at 'other'; B0 and B0' must be built from" \
                " one pinned worktree" % TAG, e
        # D-13 (the reviewer's RV8): both manifests WITHOUT a commit refuse too
        ma_p = os.path.join(ra, "diagnostics", "run_manifest.json")
        ma = json.load(open(ma_p)); ma.pop("commit"); open(ma_p, "w").write(json.dumps(ma))
        m.pop("commit"); open(mp, "w").write(json.dumps(m))
        try:
            run_g10(pairs, db, ptr)
            raise AssertionError("missing commits not refused")
        except SystemExit as e:
            assert str(e) == "%s REFUSED: D-8: B0/x was built at commit None and B0p/x at None; B0 and B0' must be built from" \
                " one pinned worktree" % TAG, e
        ma["commit"] = "c"; open(ma_p, "w").write(json.dumps(ma))
        m["commit"] = "c"; open(mp, "w").write(json.dumps(m))
        # D-14: an INLINE unionSnapshots list closes on its line; a later differing models entry is refused
        i1, i2 = os.path.join(tmp, "i1.toml"), os.path.join(tmp, "i2.toml")
        open(i1, "w").write('unionSnapshots = ["S1"]\noutputDir = "A"\nmodels = [\n    "m1",\n]\n')
        open(i2, "w").write('unionSnapshots = ["S1"]\noutputDir = "B"\nmodels = [\n    "m2",\n]\n')
        assert toml_pair_diff(i1, i2) == ["'    \"m1\",' vs '    \"m2\",'"], toml_pair_diff(i1, i2)
        open(i2, "w").write('unionSnapshots = ["T1"]\noutputDir = "B"\nmodels = [\n    "m1",\n]\n')
        assert toml_pair_diff(i1, i2) == ["'unionSnapshots = [\"S1\"]' vs 'unionSnapshots = [\"T1\"]'"], toml_pair_diff(i1, i2)
        with open(tb, "a") as f:
            f.write("seed = 43\n")
        try:
            run_g10(pairs, db, ptr)
            raise AssertionError("a TOML pair differing beyond outputDir not refused")
        except SystemExit as e:
            assert "TOMLs are not a replay: line counts differ" in str(e), e
        # the graft rule: member snapshot ids inside unionSnapshots may differ; any other key may not
        g1, g2 = os.path.join(tmp, "g1.toml"), os.path.join(tmp, "g2.toml")
        open(g1, "w").write('# arm B0\nunionSnapshots = [\n    "S1",   # BBH\n    "S2"\n]\noutputDir = "A"\npool = "p"\n')
        open(g2, "w").write('# arm B0p\nunionSnapshots = [\n    "T1",   # BBH\n    "T2"\n]\noutputDir = "B"\npool = "p"\n')
        assert toml_pair_diff(g1, g2) == []
        open(g2, "w").write('# arm B0p\nunionSnapshots = [\n    "T1",   # BBH\n    "T2"\n]\noutputDir = "B"\npool = "q"\n')
        assert toml_pair_diff(g1, g2) == ["'pool = \"p\"' vs 'pool = \"q\"'"], toml_pair_diff(g1, g2)
        open(g2, "w").write('# arm B0p\nunionSnapshots = [\n    "T1",   # BBH\n    "T2"\n]\noutputDir = "A"\npool = "p"\n')
        assert toml_pair_diff(g1, g2) == ["outputDir lines differing: 0 (must be 1)"]
        # a quoted list entry OUTSIDE unionSnapshots (a models entry) may not differ
        open(g1, "a").write('models = [\n    "m1",\n]\n'); open(g2, "w").write(
            '# arm B0p\nunionSnapshots = [\n    "T1",   # BBH\n    "T2"\n]\noutputDir = "B"\npool = "p"\nmodels = [\n    "m2",\n]\n')
        assert toml_pair_diff(g1, g2) == ["'    \"m1\",' vs '    \"m2\",'"], toml_pair_diff(g1, g2)
        # RV6: the commit key is a COMPARED A5 field (never excluded), besides the D-8 precondition
        assert "commit" not in MANIFEST_EXCLUDED and artefacts(ra, db)["A5 run_manifest.json"]["commit"] == "c"

    def run_g10(pairs, db, ptr):
        lines = []
        word = g10(pairs, db, ptr, out=lines.append)
        return word, lines

    def held(tmp):
        w, L = run_g10(*setup(tmp))
        assert w == "HELD" and L[-1] == "G10: HELD", L
        assert L[0] == "[G10] D-8 precondition B0/x vs B0p/x: one commit c; the TOMLs differ in outputDir only", L
        assert L[1] == "[G10] B0/x vs B0p/x: byte-identical on the declared set (A1-A5, exclusions applied)", L
        assert "[G10] stamp B0/x: S1-S4 hold" in L and "[G10] stamp B0p/x: S1-S3 hold" in L, L
        assert "[G10] starved-pass accept count (B0/x, descriptive): NOT RECORDED by the engine" in L, L

    def csv_byte(tmp):
        w, L = run_g10(*setup(tmp, b_csv=b"3,4\n"))
        assert w == "FAILED" and L[1] == "[G10] B0/x vs B0p/x: DIFFERS on A3 validation/MAIN_x.csv", L
        assert L[-1].startswith("G10: FAILED (a byte difference or a stamp mismatch): the lane STOPS"), L

    def stamp_manifest(tmp):
        # B0p's manifest split_v2 disagrees with its snapshot stamp (train_rows)
        pairs, db, ptr = setup(tmp, b_man={"split_v2": None})
        w, L = run_g10(pairs, db, ptr)
        assert w == "FAILED" and "[G10] stamp S2 %s: the manifest has no split_v2" % pairs[0][1][1] in L, L

    def stamp_field(tmp):
        # S2 field by field: B0p's manifest split_v2.train_rows edited -> the S2 line names the field
        pairs, db, ptr = setup(tmp)
        mp = os.path.join(pairs[0][1][1], "diagnostics", "run_manifest.json")
        m = json.load(open(mp)); m["split_v2"]["train_rows"] = 99; open(mp, "w").write(json.dumps(m))
        w, L = run_g10(pairs, db, ptr)
        assert w == "FAILED" and "[G10] stamp S2 %s: stamp trainRows = 5 but manifest split_v2.train_rows = 99" % pairs[0][1][1] in L, L

    def final_line(tmp):
        # the FINAL dag snapshot is compared: B0p's last line differs, its first line does not
        pairs, db, ptr = setup(tmp)
        dp = os.path.join(pairs[0][1][1], "dag_snapshots.jsonl")
        lines = open(dp).read().splitlines()
        open(dp, "w").write(lines[0] + "\n" + json.dumps({"iteration": 7, "nodes": [{"id": "r"}, {"id": "b"}]}) + "\n")
        w, L = run_g10(pairs, db, ptr)
        assert w == "FAILED" and L[1] == "[G10] B0/x vs B0p/x: DIFFERS on A1 dag_snapshots.jsonl (last line)", L

    def stamp_value(tmp):
        pairs, db, ptr = setup(tmp, b_stamp={"trainRows": 6})
        w, L = run_g10(pairs, db, ptr)
        # A4 differs (stamp inside settings) AND S2 fails (manifest built from the same stamp -> equal) -> only A4/A5
        assert w == "FAILED" and L[1].startswith("[G10] B0/x vs B0p/x: DIFFERS on A4 snapshot row; A5 run_manifest.json"), L

    def toml_sha(tmp):
        pairs, db, ptr = setup(tmp, b_toml_extra="# edited after the build\n")
        w, L = run_g10(pairs, db, ptr)
        assert w == "FAILED" and any(l.startswith("[G10] stamp S3 ") for l in L), L

    def pointer(tmp):
        pairs, db, ptr = setup(tmp)
        d = json.load(open(ptr)); d["entries"]["B0/x"]["snapshot_id"] = "other"
        open(ptr, "w").write(json.dumps(d))
        w, L = run_g10(pairs, db, ptr)
        assert w == "FAILED" and "[G10] stamp S4 B0/x: the pointer entry differs from the run (stamp True, snapshot False, toml True)" in L, L
        try:
            write_pointer(ptr, {}, db)
            raise AssertionError("pointer overwritten")
        except SystemExit as e:
            assert str(e).endswith("exists; the pointer file is write-once"), e

    def exclusions(tmp):
        # different wall clock, config path and config sha in the manifests, different ids / timestamps / log uuids in the rows:
        # still HELD (the declared exclusions); a non-excluded manifest key difference FAILS
        w, _L = run_g10(*setup(tmp))
        assert w == "HELD"
        tmp2 = os.path.join(tmp, "two"); os.makedirs(tmp2)
        w2, L2 = run_g10(*setup(tmp2, b_man={"train_size": 6}))
        assert w2 == "FAILED" and L2[1] == "[G10] B0/x vs B0p/x: DIFFERS on A5 run_manifest.json", L2

    def missing_csv(tmp):
        pairs, db, ptr = setup(tmp)
        os.remove(os.path.join(pairs[0][1][1], "validation", "MAIN_x.csv"))
        w, L = run_g10(pairs, db, ptr)
        assert w == "FAILED" and "A3 validation/MAIN_x.csv" in L[1], L

    def a2_strip(tmp):
        # G10-R2: the held fixture's gate_ids carry DIFFERENT split_v2.configSha256Lf (each run's own TOML sha): HELD; the
        # strip touches only that key: a gate id or another split_v2 field still FAILS on A2
        pairs, db, ptr = setup(tmp)
        ga = json.load(open(os.path.join(pairs[0][0][1], "gate_ids.json"))); gb = json.load(open(os.path.join(pairs[0][1][1], "gate_ids.json")))
        assert ga["split_v2"]["configSha256Lf"] != gb["split_v2"]["configSha256Lf"]
        assert artefacts(pairs[0][0][1], db)["A2 gate_ids.json"] == {"gate_ids": [1, 2], "split_v2": {"poolId": "pv2_x"}}
        w, L = run_g10(pairs, db, ptr)
        assert w == "HELD" and L[1] == "[G10] B0/x vs B0p/x: byte-identical on the declared set (A1-A5, exclusions applied)", L
        for i, over in enumerate(({"gate_ids": [1, 3]}, {"split_v2": {"poolId": "pv2_y", "configSha256Lf": "z"}})):
            t2 = os.path.join(tmp, "o%d" % i); os.makedirs(t2)
            w2, L2 = run_g10(*setup(t2, b_gate=over))
            assert w2 == "FAILED" and L2[1] == "[G10] B0/x vs B0p/x: DIFFERS on A2 gate_ids.json", (over, L2)
        assert strip_gate_toml({"split_v2": {"config_sha256_lf": "a", "k": 1}, "configSha256Lf": "top"}) == \
            {"split_v2": {"k": 1}, "configSha256Lf": "top"}

    def a4_sets(tmp):
        # ruling (A) on R2-1: the same membership in another node-internal order -> HELD; a different set -> FAILED on A4;
        # the node order and every other node field stay exact
        w, L = run_g10(*setup(tmp, b_qids={"r": [2, 3, 1], "a": [4, 5]}))
        assert w == "HELD" and L[1] == "[G10] B0/x vs B0p/x: byte-identical on the declared set (A1-A5, exclusions applied)", L
        for i, q in enumerate(({"r": [3, 1, 6], "a": [5, 4]}, {"r": [3, 1, 2, 4], "a": [5]}, {"r": [3, 1], "a": [5, 4]})):
            t2 = os.path.join(tmp, "s%d" % i); os.makedirs(t2)
            w2, L2 = run_g10(*setup(t2, b_qids=q))
            assert w2 == "FAILED" and L2[1] == "[G10] B0/x vs B0p/x: DIFFERS on A4 snapshot row", (q, L2)
        row = {"graph": {"rootId": "r", "nodes": [{"id": "r", "kappa": 1.5, "queryIds": [3, 1, 2]}, {"id": "a", "queryIds": [5, 4]}]},
               "metrics": {"m": [2, 1]}}
        got = membership_as_sets(row)
        assert got == {"graph": {"rootId": "r", "nodes": [{"id": "r", "kappa": 1.5, "queryIds": [1, 2, 3]}, {"id": "a", "queryIds": [4, 5]}]},
                       "metrics": {"m": [2, 1]}}, got
        assert membership_as_sets(dict(row, graph={"rootId": "r", "nodes": list(reversed(row["graph"]["nodes"]))})) != got   # node order exact
        assert row["graph"]["nodes"][0]["queryIds"] == [3, 1, 2]                                                          # no mutation

    def graft_pair(tmp):
        # G10-R2: a graft pair (unionSnapshots in both TOMLs; no dag_snapshots.jsonl, no gate_ids.json): A1 / A2 N/A, HELD on A3-A5
        pairs, db, ptr = setup(tmp, graft=True)
        w, L = run_g10(pairs, db, ptr)
        assert w == "HELD" and L[1] == ("[G10] B0/x vs B0p/x: A1 / A2 N/A (a graft pair: the graft writes no dag_snapshots.jsonl and"
                                        " no gate_ids.json); A3-A5 compared") and \
            L[2] == "[G10] B0/x vs B0p/x: byte-identical on the declared set (A3-A5, exclusions applied)", L
        assert sorted(artefacts(pairs[0][0][1], db, True)) == ["A3 validation/MAIN_x.csv", "A4 snapshot row", "A5 run_manifest.json"]
        for i, kw, want in ((0, dict(b_csv=b"3,4\n"), "A3 validation/MAIN_x.csv"), (1, dict(b_man={"train_size": 6}), "A5 run_manifest.json"),
                            (2, dict(b_stamp={"trainRows": 6}), "A4 snapshot row")):
            t2 = os.path.join(tmp, "g%d" % i); os.makedirs(t2)
            w2, L2 = run_g10(*setup(t2, graft=True, **kw))
            assert w2 == "FAILED" and L2[2].startswith("[G10] B0/x vs B0p/x: DIFFERS on %s" % want), (kw, L2)
        # a MEMBER pair without dag_snapshots.jsonl is refused (only a graft pair reads A1 / A2 as N/A)
        t3 = os.path.join(tmp, "m"); os.makedirs(t3)
        pm, dbm, ptm = setup(t3)
        os.remove(os.path.join(pm[0][1][1], "dag_snapshots.jsonl"))
        try:
            run_g10(pm, dbm, ptm)
            raise AssertionError("a member without dag_snapshots.jsonl not refused")
        except SystemExit as e:
            assert str(e) == "%s REFUSED: %s has no dag_snapshots.jsonl (a member build writes one; only a graft pair reads A1 / A2 as" \
                " N/A)" % (TAG, pm[0][1][1]), e
        # a graft TOML paired with a member TOML is refused
        (na, ra, ta), (nb, rb, tb) = pairs[0]
        assert is_graft_toml(ta) and not is_graft_toml(pm[0][0][2])
        try:
            g10([((na, ra, ta), (nb, rb, pm[0][0][2]))], db, ptr, out=lambda x: None)
            raise AssertionError("mixed pair not refused")
        except SystemExit as e:
            assert "a pair is two members or two grafts" in str(e) or "TOMLs are not a replay" in str(e), e
        # a commented-out unionSnapshots line does not make a graft
        tc = os.path.join(tmp, "c.toml"); open(tc, "w").write('# unionSnapshots = ["S1"]\nseed = 42\n')
        assert not is_graft_toml(tc)

    def lanes(tmp):
        # rp12-r2-lane: an R2 fixture under tmp's r2 roots reads HELD in lane r2 (the lane line first); the same objects in lane
        # r1 refuse; an R1 run dir in an r2 pair refuses; an R2 run whose snapshot is an R1 pointer object refuses; lane r2's
        # pointer must be its own; write_pointer refuses another lane's run
        rows = []
        cr, rr = os.path.join(tmp, "experiment_configs", "rp12_r2"), os.path.join(tmp, "experiment_results", "archv2", "rp12_r2")
        os.makedirs(cr)
        ta, tb = os.path.join(cr, "a.toml"), os.path.join(cr, "b.toml")
        open(ta, "w", newline="\n").write('seed = 42\noutputDir = "A"\n'); open(tb, "w", newline="\n").write('seed = 42\noutputDir = "B"\n')
        ra = _run(rr, "A", "sidA2", rows, 'seed = 42\noutputDir = "A"\n')
        rb = _run(rr, "B", "sidB2", rows, 'seed = 42\noutputDir = "B"\n', start=9999)
        r1run = _run(os.path.join(tmp, "experiment_results", "archv2", "rp12"), "A", "sidR1", rows, 'seed = 42\noutputDir = "A"\n')
        db = _db(tmp, rows)
        ptr = os.path.join(cr, "objects_of_record.json")
        with contextlib.redirect_stdout(io.StringIO()):
            write_pointer(ptr, {"B0/x": (ra, ta)}, db, lane="r2", root=tmp)
        pairs = [(("B0/x", ra, ta), ("B0p/x", rb, tb))]
        L_ = []
        w = g10(pairs, db, ptr, out=L_.append, lane="r2", root=tmp)
        assert w == "HELD" and L_[0] == ("[G10] lane r2: pointer experiment_configs/rp12_r2/objects_of_record.json; every run dir and"
                                         " TOML inside experiment_configs/rp12_r2/ and experiment_results/archv2/rp12_r2/"), L_
        assert L_[2] == "[G10] B0/x vs B0p/x: byte-identical on the declared set (A1-A5, exclusions applied)", L_
        bad_cases = [(dict(lane="r1"), "is an object of lane r2, the run is lane r1"),
                     (dict(pairs=[(("B0/x", r1run, ta), ("B0p/x", rb, tb))]), "run dir %s is an object of lane r1, the run is lane r2" % r1run),
                     (dict(ptr=os.path.join(tmp, "other_ptr.json")), "is outside lane r2's roots"),
                     (dict(ptr=os.path.join(cr, "objects_other.json")), "lane r2 reads only its own pointer experiment_configs/rp12_r2/objects_of_record.json")]
        for over, needle in bad_cases:
            try:
                g10(over.get("pairs", pairs), db, over.get("ptr", ptr), out=lambda x: None, lane=over.get("lane", "r2"), root=tmp)
                raise AssertionError("not refused: %s" % needle)
            except SystemExit as e:
                assert needle in str(e), (needle, str(e))
        # an R1 pointer naming sidB2 as an R1 object: the R2 pair refuses on the snapshot
        os.makedirs(os.path.join(tmp, "experiment_configs", "rp12"))
        with open(os.path.join(tmp, "experiment_configs", "rp12", "objects_of_record.json"), "w") as f:
            json.dump({"format": POINTER_FORMAT, "entries": {"B0p/x": {"snapshot_id": "sidB2"}}}, f)
        try:
            g10(pairs, db, ptr, out=lambda x: None, lane="r2", root=tmp)
            raise AssertionError("an R1 snapshot in an R2 pair not refused")
        except SystemExit as e:
            assert "snapshot id(s) ['sidB2'] are lane r1 objects (B0p/x), the run is lane r2" in str(e), e
        try:
            write_pointer(os.path.join(cr, "p2.json"), {"B0/x": (r1run, ta)}, db, lane="r2", root=tmp)
            raise AssertionError("write_pointer accepted an R1 run")
        except SystemExit as e:
            assert "is an object of lane r1" in str(e) or "reads only its own pointer" in str(e), e
        assert not os.path.exists(os.path.join(cr, "p2.json"))

    def cli(tmp):
        pairs, db, ptr = setup(tmp)
        (na, ra, ta), (nb, rb, tb) = pairs[0]
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = main(["--g10", "--snapshot-db", db, "--pointer", ptr, "--pair", "%s=%s|%s,%s=%s|%s" % (na, ra, ta, nb, rb, tb)])
        assert rc == 0 and buf.getvalue().splitlines()[-1] == "G10: HELD", buf.getvalue()
        try:
            _entries(["x=a:b"])
            raise AssertionError("bad entry accepted")
        except SystemExit as e:
            assert "is not NAME=RUN_DIR|TOML" in str(e)

    for nm, fn in [("D-8: one commit, a replay TOML pair; RV6 (commit compared)", d8), ("HELD on identical runs (values of every line)", held), ("the CLI end to end (--g10 --pair)", cli), ("one CSV byte -> FAILED naming it", csv_byte),
                   ("S2 manifest without split_v2 -> FAILED", stamp_manifest), ("S2 one field -> FAILED naming it", stamp_field),
                   ("the FINAL dag line is compared", final_line), ("a stamp value difference -> FAILED on A4 / A5", stamp_value),
                   ("S3 TOML edited after the build -> FAILED", toml_sha), ("S4 pointer mismatch -> FAILED; pointer write-once", pointer),
                   ("the declared exclusions only", exclusions), ("a missing artefact -> FAILED", missing_csv),
                   ("G10-R2: A2's split_v2 TOML sha stripped, nothing else", a2_strip),
                   ("G10-R2: a graft pair reads A1 / A2 as N/A and compares A3-A5", graft_pair),
                   ("G10-R2 ruling (A): A4 query membership compared as sets, everything else exact", a4_sets),
                   ("rp12-r2-lane: R2 objects read in lane r2 only; R1 objects, R1 snapshots, a foreign pointer refuse", lanes)]:
        case(nm, fn)
    print("%s selftest: %d / %d passed" % (TAG, len(ran) - len(fails), len(ran)))
    return 1 if fails else 0


def _entries(specs):
    """NAME=RUN_DIR|TOML (| separates, so Windows drive letters are safe)."""
    out = {}
    for sp in specs:
        name, rest = sp.split("=", 1)
        if rest.count("|") != 1:
            refuse("entry %r is not NAME=RUN_DIR|TOML" % sp)
        run, toml = rest.split("|")
        out[name] = (run, toml)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true"); g.add_argument("--g10", action="store_true")
    g.add_argument("--write-pointer")
    ap.add_argument("--snapshot-db"); ap.add_argument("--pointer")
    ap.add_argument("--entry", action="append", default=[]); ap.add_argument("--pair", action="append", default=[])
    LN.add_arg(ap)
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.snapshot_db:
        refuse("--snapshot-db is required")
    if a.write_pointer:
        doc = write_pointer(a.write_pointer, _entries(a.entry), a.snapshot_db, lane=a.lane)
        print("%s pointer %s written (%d entries)" % (TAG, a.write_pointer, len(doc["entries"])))
        return 0
    pairs = []
    for p in a.pair:
        ea, eb = p.split(",", 1)
        (na, (ra, ta)), = _entries([ea]).items()
        (nb, (rb, tb)), = _entries([eb]).items()
        pairs.append(((na, ra, ta), (nb, rb, tb)))
    return 0 if g10(pairs, a.snapshot_db, a.pointer or LN.pointer(a.lane), lane=a.lane) == "HELD" else 1


if __name__ == "__main__":
    sys.exit(main())
