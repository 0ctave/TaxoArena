"""g12_site_null.py: the G12 site-null launch of RP12 ARCH-V2-E-T, checked before it runs (READY_rp12_et2 "G12 (own review before the
site null)"). ZERO calls; it opens snapshots.db read-only and launches nothing.

REGISTRATION OF RECORD: docs/judge_v2_program.md L22028-L22060 (0a0361b): "G12 (certificate; = F-TAX N-1, set readout): N-1 FIRES iff
the hierarchical-BH set at per-family q = 0.05 (300 reps) on B0's MMLU-Pro member contains NO depth-1 site; it does not fire iff any
depth-1 site is in the set. The per-site p95 count is printed beside against Binomial(m, 0.05). UNDETERMINED-by-support if the top
family has m > 15 (1/301 > 0.05/m) or the corpus is below the site-null floor." Support (g): "at 300 reps only if the MMLU-Pro top
family has m <= 15 (14 declared categories give m = 14 if every anchor stays at depth 1)". Site null: 300 reps on B0's MMLU-Pro
member, read by cert_resolution.py's hierarchical BH (blob dbe9425d at 32c4c72). All legs at 12 threads.

WHAT --dry-run CHECKS AND PRINTS (the config experiment_configs/rp12/B0/g12_site_null.sitenull; unknown or missing keys REFUSE):
  P1 the member's snapshot id and stamp from the pointer file entry (pointerEntry of objects_of_record.json, written by
     g10_compare.py --write-pointer after B0; absent = REFUSED: the pointer is owed);
  P2 the snapshot row's stored buildStamp equals the pointer's stamp, and is pool poolId, engine pool file enginePoolSha256Lf,
     namespaces [namespace] (the MMLU_PRO_LB member of the union pool, READY_rp12_et2 B0-1);
  P3 the sites exactly as the harness enumerates them (SeparationNullBySizeTest siteNull: childIds >= 2 and dasguptaDeltaNorm
     > 0), their depths and region sizes n (the distinct queryIds under the site), and cert_resolution's families (key = the
     nearest site ancestor along parentIds[0], TOP if none): m_top = the size of the TOP family, printed against mTopMax and
     declaredDomains; m_top > mTopMax prints "UNDETERMINED-by-support (registered)"; no site at all REFUSES;
  P4 the heap estimate by the harness's own rule (live = min(reps, jvmThreads) replicates, each n_max x (7 x sliceDim + 3 x 128)
     doubles; budget 0.90 of the heap) and the -DsiteNullHeap it needs beyond the 6g default;
  P5 outCsv does not exist yet (the harness writes it; a second run is refused before launch);
  and the exact command, from the pinned worktree:
     .\\gradlew.bat siteNull --console=plain --offline -PjvmThreads=12 -PnullReps=300 "-DsnapshotId=<id>" "-DsliceDim=512"
       "-DsepBar=0.0145" "-DdropTop=0" "-Dwhiten=false" "-DoutCsv=<outCsv>" [-DsiteNullHeap=<N>g]
  (no -DembeddingCacheFile: the qwen3 cache of record; rule 7: one heavy process, never beside a construction).

  python tools/analysis/g12_site_null.py --selftest
  python tools/analysis/g12_site_null.py --dry-run [--config experiment_configs/rp12/B0/g12_site_null.sitenull] [--snapshot-db snapshots.db]

SELFTEST MUTANTS (run 2026-09-30 by a harness, one temporary edit at a time, reverted; M0 control survived): M1 sites ignore
dasguptaDeltaNorm | M2 the family key taken from a non-site parent | M3 the m bar strict (m = 15 read as over) | M4 the pointer
stamp comparison removed | M5 live replicates = reps | M6 P5 (existing outCsv) removed | M7 unknown config keys accepted:
7 of 7 killed.
[DELTA 2026-09-30 rp12-et4, READY_rp12_et3 D-12 / D-15; insertion only] D-12: dry_run REFUSES unless the TOP family's depths
are exactly [1] (a root site makes TOP = {root}, m = 1: never reported "reachable"; a registrar bracket before any launch);
tested with a root-site fixture. D-15: the fixture carries a one-child node with dasguptaDeltaNorm > 0, which is not a site
(the reviewer's RV10). Mutants D12 (the depth rule removed) and RV10 (childIds >= 1): killed.
[DELTA 2026-10-01 rp12-flat-pin, READY_rp12_pair_mc D-2 (ccef91d); insertion only] a mixed-depth fixture: a depth-1 anchor that
is not a site with a depth-2 site child, which joins TOP: depths [1, 2], m = 14, refused with no "reachable" and no COMMAND
line. Mutant RD (`!= [1]` -> `1 not in`), which survived the review: killed.
[DELTA 2026-10-01 rp12-r2-lane; insertion only] --lane {r1,r2} (tools/analysis/rp12_lane.py; default r1 = the commands of
record, unchanged): the config, its pointerFile and its outCsv of the other lane REFUSE; in lane r2 they must lie inside
experiment_configs/rp12_r2/ or experiment_results/archv2/rp12_r2/; lane r2 reads
experiment_configs/rp12_r2/B0/g12_site_null.sitenull (R1's with the lane's pointer and outCsv) and only the lane's own
pointer.
"""
import os
import sys
import json
import math
import argparse
import tomllib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from data_v2 import ro  # noqa: E402

TAG = "[G12]"
CONFIG_DEFAULT = os.path.join("experiment_configs", "rp12", "B0", "g12_site_null.sitenull")
KEYS = {"pointerFile": str, "pointerEntry": str, "poolId": str, "enginePoolSha256Lf": str, "namespace": str, "sliceDim": int,
        "sepBar": float, "dropTop": int, "whiten": bool, "nullReps": int, "jvmThreads": int, "declaredDomains": int, "mTopMax": int,
        "outCsv": str}
DEFAULT_HEAP_GB = 6.0


def refuse(msg):
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def load_config(path):
    with open(path, "rb") as f:
        cfg = tomllib.load(f)
    unknown = sorted(set(cfg) - set(KEYS))
    missing = sorted(set(KEYS) - set(cfg))
    if unknown or missing:
        refuse("config %s: unknown keys %s, missing keys %s" % (path, unknown, missing))
    for k, t in KEYS.items():
        v = cfg[k]
        if t is float and isinstance(v, int) and not isinstance(v, bool):
            v = cfg[k] = float(v)
        if not isinstance(v, t) or (t is int and isinstance(v, bool)):
            refuse("config %s: %s = %r is not a %s" % (path, k, v, t.__name__))
    if not (1 <= cfg["jvmThreads"] <= 24) or cfg["nullReps"] < 1 or cfg["sliceDim"] < 1:
        refuse("config %s: jvmThreads / nullReps / sliceDim out of range" % path)
    return cfg


def pointer_entry(cfg, root=ROOT):
    p = os.path.join(root, cfg["pointerFile"])
    if not os.path.isfile(p):
        refuse("P1: the pointer file %s is owed (g10_compare.py --write-pointer after the B0 builds)" % cfg["pointerFile"])
    doc = json.load(open(p, encoding="utf-8"))
    e = doc.get("entries", {}).get(cfg["pointerEntry"])
    if e is None:
        refuse("P1: the pointer file has no entry %s" % cfg["pointerEntry"])
    return e


def snapshot_row(db, sid):
    conn = ro.open_ro(db)
    try:
        r = conn.execute("SELECT graph, settings FROM snapshots WHERE id = ?", (sid,)).fetchone()
    finally:
        conn.close()
    if r is None:
        refuse("P2: snapshot %s is not in %s" % (sid, db))
    return json.loads(r[0]), json.loads(r[1])


def check_stamp(cfg, entry, settings):
    st = settings.get("buildStamp")
    if st is None:
        refuse("P2: snapshot %s carries no buildStamp" % entry["snapshot_id"])
    if st != entry["stamp"]:
        refuse("P2: the snapshot's stamp differs from the pointer entry %s" % cfg["pointerEntry"])
    want = {"poolId": cfg["poolId"], "enginePoolSha256Lf": cfg["enginePoolSha256Lf"], "namespacesLoaded": [cfg["namespace"]]}
    bad = ["%s %r (want %r)" % (k, st.get(k), v) for k, v in want.items() if st.get(k) != v]
    if bad:
        refuse("P2: the stamp is not the %s member of %s: %s" % (cfg["namespace"], cfg["poolId"], "; ".join(bad)))
    return st


def sites_and_families(graph):
    """P3: the harness's sites (childIds >= 2 and dasguptaDeltaNorm > 0) with depth and region n; cert_resolution's families."""
    byid = {n["id"]: n for n in graph["nodes"]}

    def region(nid):
        seen, stack, q = set(), [nid], set()
        while stack:
            c = stack.pop()
            if c in seen:
                continue
            seen.add(c)
            q.update(byid[c].get("queryIds") or [])
            stack.extend(x for x in (byid[c].get("childIds") or []) if x in byid)
        return len(q)

    sites = {n["id"] for n in graph["nodes"] if len(n.get("childIds") or []) >= 2 and (n.get("dasguptaDeltaNorm") or 0.0) > 0.0}
    fam = {}
    for s in sites:
        cur, key = s, "TOP"
        while True:
            parents = byid[cur].get("parentIds") or []
            if not parents or parents[0] not in byid:
                break
            cur = parents[0]
            if cur in sites:
                key = cur
                break
        fam[s] = key
    info = {s: (byid[s].get("depth"), region(s)) for s in sites}
    return info, fam


def heap_estimate(n_max, dim, reps, threads):
    live = min(reps, max(threads, 2))
    need = live * n_max * (7 * dim + 3 * 128) * 8 / 1024 ** 3
    heap = max(DEFAULT_HEAP_GB, math.ceil(need / 0.90))
    return need, live, int(heap)


def dry_run(cfg, db, root=ROOT, out=print):
    entry = pointer_entry(cfg, root)
    sid = entry["snapshot_id"]
    graph, settings = snapshot_row(db, sid)
    st = check_stamp(cfg, entry, settings)
    out("POOL %s (G12 site null, dry-run: counts only, NO statistic, nothing launched)" % cfg["poolId"])
    out("%s P1-P2 member %s = snapshot %s; stamp pool %s, engine pool sha256(LF) %s, namespaces %s: equal to the pointer entry"
        % (TAG, cfg["pointerEntry"], sid, st["poolId"], st["enginePoolSha256Lf"][:16], st["namespacesLoaded"]))
    info, fam = sites_and_families(graph)
    if not info:
        refuse("P3: snapshot %s has no site (childIds >= 2 and dasguptaDeltaNorm > 0)" % sid)
    top = sorted(s for s, k in fam.items() if k == "TOP")
    m_top = len(top)
    top_depths = sorted({info[s][0] for s in top})
    if top_depths != [1]:
        # READY_rp12_et3 D-12: the registered top family is the DEPTH-1 family (14 declared domains); a root site makes TOP
        # = {root} (m = 1), a vacuous pass of the support bar. STOP for a registrar bracket; never "reachable".
        refuse("P3 D-12: the TOP family's depths are %s, not [1] (m = %d): UNDETERMINED, the registered top family is not the"
               " depth-1 family; a registrar bracket before any launch" % (top_depths, m_top))
    by_depth = {}
    for s, (d, n) in info.items():
        by_depth.setdefault(d, []).append(n)
    out("%s P3 sites %d (by depth: %s); families %d; TOP family m = %d, depths %s"
        % (TAG, len(info), ", ".join("d%s %d (n %d-%d)" % (d, len(v), min(v), max(v)) for d, v in sorted(by_depth.items())),
           len(set(fam.values())), m_top, sorted({info[s][0] for s in top})))
    if m_top > cfg["mTopMax"]:
        out("%s P3 m = %d > %d: G12 is UNDETERMINED-by-support at %d reps (registered: 1/%d > 0.05/m); declared domains %d"
            % (TAG, m_top, cfg["mTopMax"], cfg["nullReps"], cfg["nullReps"] + 1, cfg["declaredDomains"]))
    else:
        out("%s P3 m = %d <= %d (declared MMLU-Pro domains %d): the top family is reachable at %d reps"
            % (TAG, m_top, cfg["mTopMax"], cfg["declaredDomains"], cfg["nullReps"]))
    n_max = max(n for _d, n in info.values())
    need, live, heap = heap_estimate(n_max, cfg["sliceDim"], cfg["nullReps"], cfg["jvmThreads"])
    out("%s P4 heap: largest site n %d, live replicates %d, peak %.2f GB -> %s" % (
        TAG, n_max, live, need, "fits the 6g default" if heap <= DEFAULT_HEAP_GB else "needs -DsiteNullHeap=%dg" % heap))
    if os.path.exists(os.path.join(root, cfg["outCsv"])):
        refuse("P5: %s exists; the site null writes it once" % cfg["outCsv"])
    cmd = ('.\\gradlew.bat siteNull --console=plain --offline -PjvmThreads=%d -PnullReps=%d "-DsnapshotId=%s" "-DsliceDim=%d"'
           ' "-DsepBar=%s" "-DdropTop=%d" "-Dwhiten=%s" "-DoutCsv=%s"%s'
           % (cfg["jvmThreads"], cfg["nullReps"], sid, cfg["sliceDim"], repr(cfg["sepBar"]), cfg["dropTop"],
              str(cfg["whiten"]).lower(), cfg["outCsv"], "" if heap <= DEFAULT_HEAP_GB else ' "-DsiteNullHeap=%dg"' % heap))
    out("%s COMMAND: %s" % (TAG, cmd))
    return dict(sid=sid, m_top=m_top, sites=len(info), heap=heap, cmd=cmd)


# ── selftest ────────────────────────────────────────────────────────────────────────────────────────────────────────

def _graph(n_anchors=14, split_anchors=14, deep=2):
    nodes = [{"id": "root", "depth": 0, "childIds": ["a%d" % i for i in range(n_anchors)], "parentIds": [], "dasguptaDeltaNorm": 0.0,
              "queryIds": []}]
    for i in range(n_anchors):
        kids = ["a%d_c%d" % (i, j) for j in range(2)] if i < split_anchors else []
        nodes.append({"id": "a%d" % i, "depth": 1, "childIds": kids, "parentIds": ["root"], "dasguptaDeltaNorm": 0.3 if kids else 0.0,
                      "queryIds": []})
        for j, k in enumerate(kids):
            sub = ["%s_g%d" % (k, t) for t in range(2)] if (i < deep and j == 0) else []
            nodes.append({"id": k, "depth": 2, "childIds": sub, "parentIds": ["a%d" % i], "dasguptaDeltaNorm": 0.2 if sub else 0.0,
                          "queryIds": ["q%d_%d_%d" % (i, j, t) for t in range(50)]})
            for s in sub:
                nodes.append({"id": s, "depth": 3, "childIds": [], "parentIds": [k], "dasguptaDeltaNorm": 0.0,
                              "queryIds": ["%s_%d" % (s, t) for t in range(10)]})
    # READY_rp12_et3 D-15: a ONE-child node with dasguptaDeltaNorm > 0 is NOT a site (childIds >= 2); no query of its own
    if n_anchors > 2 and split_anchors > 2:
        for n in nodes:
            if n["id"] == "a2_c1":
                n["childIds"] = ["a2_c1_only"]
                n["dasguptaDeltaNorm"] = 0.4
        nodes.append({"id": "a2_c1_only", "depth": 3, "childIds": [], "parentIds": ["a2_c1"], "dasguptaDeltaNorm": 0.0, "queryIds": []})
    return {"rootId": "root", "nodes": nodes}


def selftest():
    import io, tempfile, shutil, contextlib
    fails, ran = [], []

    def case(name, fn):
        ran.append(name)
        tmp = tempfile.mkdtemp(prefix="g12st_")
        try:
            fn(tmp)
            print("  ok   " + name)
        except (AssertionError, SystemExit, Exception) as e:
            fails.append(name)
            print("  FAIL %s: %s: %s" % (name, type(e).__name__, e))
        finally:
            for d, _ds, fs in os.walk(tmp):
                for f in fs:
                    os.chmod(os.path.join(d, f), 0o666)
            shutil.rmtree(tmp, ignore_errors=True)

    cfg0 = load_config(os.path.join(ROOT, CONFIG_DEFAULT))
    stamp = {"poolId": cfg0["poolId"], "enginePoolSha256Lf": cfg0["enginePoolSha256Lf"], "namespacesLoaded": ["MMLU_PRO"], "rule": "CK-CLOSE-v2"}

    def setup(tmp, graph=None, st=None, ptr_st=None, entry="B0/mmlu_pro_lb"):
        db = os.path.join(tmp, "snapshots.db")
        c = ro.create_new(db)
        c.execute("CREATE TABLE snapshots (id TEXT PRIMARY KEY, graph TEXT, settings TEXT)")
        c.execute("INSERT INTO snapshots VALUES (?,?,?)", ("SNAP1", json.dumps(graph or _graph()), json.dumps({"buildStamp": st if st is not None else stamp})))
        c.commit(); c.close()
        os.makedirs(os.path.join(tmp, "experiment_configs", "rp12"))
        with open(os.path.join(tmp, cfg0["pointerFile"]), "w") as f:
            json.dump({"format": "taxoarena-objects-of-record-v1", "entries": {entry: {"snapshot_id": "SNAP1", "stamp": ptr_st or stamp}}}, f)
        return db

    def committed_config(tmp):
        c = cfg0
        assert (c["pointerEntry"], c["poolId"], c["namespace"], c["sliceDim"], c["sepBar"], c["nullReps"], c["jvmThreads"], c["mTopMax"],
                c["declaredDomains"]) == ("B0/mmlu_pro_lb", "pv2_1575de61bb20e977", "MMLU_PRO", 512, 0.0145, 300, 12, 15, 14), c
        import hashlib
        pf = os.path.join(ROOT, "experiment_configs", "engine_pool_pv2_1575de61bb20e977.json")
        assert hashlib.sha256(open(pf, "rb").read().replace(b"\r\n", b"\n")).hexdigest() == c["enginePoolSha256Lf"]

    def dry_ok(tmp):
        db = setup(tmp)
        lines = []
        r = dry_run(cfg0, db, root=tmp, out=lines.append)
        assert lines[0] == "POOL pv2_1575de61bb20e977 (G12 site null, dry-run: counts only, NO statistic, nothing launched)", lines
        assert (r["m_top"], r["sites"]) == (14, 16), r              # 14 depth-1 sites (TOP family) + 2 depth-2 sites
        assert "[G12] P3 sites 16 (by depth: d1 14 (n 100-120), d2 2 (n 70-70)); families 3; TOP family m = 14, depths [1]" in lines, lines
        assert "[G12] P3 m = 14 <= 15 (declared MMLU-Pro domains 14): the top family is reachable at 300 reps" in lines
        assert r["cmd"] == ('.\\gradlew.bat siteNull --console=plain --offline -PjvmThreads=12 -PnullReps=300 "-DsnapshotId=SNAP1"'
                            ' "-DsliceDim=512" "-DsepBar=0.0145" "-DdropTop=0" "-Dwhiten=false"'
                            ' "-DoutCsv=experiment_results/archv2/rp12/g12/site_null_B0_mmlu_pro_lb.csv"'), r["cmd"]

    def m_over(tmp):
        g = _graph(n_anchors=17, split_anchors=17)
        db = setup(tmp, graph=g)
        lines = []
        r = dry_run(cfg0, db, root=tmp, out=lines.append)
        assert r["m_top"] == 17 and "[G12] P3 m = 17 > 15: G12 is UNDETERMINED-by-support at 300 reps (registered: 1/301 > 0.05/m);" \
            " declared domains 14" in lines, lines

    def m_boundary(tmp):
        db = setup(tmp, graph=_graph(n_anchors=15, split_anchors=15))
        lines = []
        r = dry_run(cfg0, db, root=tmp, out=lines.append)
        assert r["m_top"] == 15 and "[G12] P3 m = 15 <= 15 (declared MMLU-Pro domains 14): the top family is reachable at 300 reps" in lines, lines

    def root_site(tmp):
        # D-12: a root that is a site -> TOP = {root}, m = 1, depths [0]: refused, never "reachable"
        g = _graph()
        for n in g["nodes"]:
            if n["id"] == "root":
                n["dasguptaDeltaNorm"] = 0.3
        db = setup(tmp, graph=g)
        lines = []
        try:
            dry_run(cfg0, db, root=tmp, out=lines.append)
            raise AssertionError("root site not refused")
        except SystemExit as e:
            assert str(e) == ("%s REFUSED: P3 D-12: the TOP family's depths are [0], not [1] (m = 1): UNDETERMINED, the registered"
                              " top family is not the depth-1 family; a registrar bracket before any launch" % TAG), e
        assert not any("reachable" in l for l in lines), lines
        info, _f = sites_and_families(_graph())
        assert "a2_c1" not in info, "a one-child node is not a site (D-15)"

    def lanes(tmp):
        import rp12_lane as LN
        r2p = os.path.join(ROOT, "experiment_configs", "rp12_r2", "B0", "g12_site_null.sitenull")
        c1, c2 = load_config(os.path.join(ROOT, CONFIG_DEFAULT)), load_config(r2p)
        assert lane_check("r1", os.path.join(ROOT, CONFIG_DEFAULT), c1) and lane_check("r2", r2p, c2)
        assert (c2["pointerFile"], c2["outCsv"]) == ("experiment_configs/rp12_r2/objects_of_record.json",
                                                     "experiment_results/archv2/rp12_r2/g12/site_null_B0_mmlu_pro_lb.csv")
        assert {k: v for k, v in c1.items() if k not in ("pointerFile", "outCsv")} == {k: v for k, v in c2.items() if k not in ("pointerFile", "outCsv")}
        for lane, path, cfg, needle in (("r1", r2p, c2, "is an object of lane r2, the run is lane r1"),
                                        ("r2", os.path.join(ROOT, CONFIG_DEFAULT), c1, "is an object of lane r1, the run is lane r2"),
                                        ("r2", r2p, dict(c2, outCsv="experiment_results/archv2/rp12/g12/x.csv"), "outCsv experiment_results/archv2/rp12/g12/x.csv is an object of lane r1"),
                                        ("r2", r2p, dict(c2, pointerFile="experiment_configs/rp12_r2/other.json"), "lane r2 reads only its own pointer")):
            try:
                lane_check(lane, path, cfg)
                raise AssertionError("not refused: %s" % needle)
            except SystemExit as e:
                assert needle in str(e), (needle, str(e))
        assert LN.pointer("r2") == c2["pointerFile"]

    def mixed_depths(tmp):
        # READY_rp12_pair_mc D-2: a depth-1 anchor that is NOT a site (dasguptaDeltaNorm 0) whose depth-2 child IS a site: that
        # child joins TOP (no site ancestor), TOP = a1..a13 (depth 1) + a0_c0 (depth 2): depths [1, 2], m = 14 -> refused
        g = _graph()
        for n in g["nodes"]:
            if n["id"] == "a0":
                n["dasguptaDeltaNorm"] = 0.0
        info, fam = sites_and_families(g)
        assert fam["a0_c0"] == "TOP" and info["a0_c0"][0] == 2 and "a0" not in info and fam["a1_c0"] == "a1", (fam.get("a0_c0"), info.get("a0_c0"))
        db = setup(tmp, graph=g)
        lines = []
        try:
            dry_run(cfg0, db, root=tmp, out=lines.append)
            raise AssertionError("mixed depths [1, 2] not refused")
        except SystemExit as e:
            assert str(e) == ("%s REFUSED: P3 D-12: the TOP family's depths are [1, 2], not [1] (m = 14): UNDETERMINED, the"
                              " registered top family is not the depth-1 family; a registrar bracket before any launch" % TAG), e
        assert not any("reachable" in l or "COMMAND" in l for l in lines), lines

    def families(tmp):
        # an anchor that is NOT a site: its children sites join the TOP family (nearest site ancestor: none)
        g = _graph(n_anchors=3, split_anchors=3, deep=1)
        for n in g["nodes"]:
            if n["id"] == "a0":
                n["dasguptaDeltaNorm"] = 0.0
        info, fam = sites_and_families(g)
        assert fam["a0_c0"] == "TOP" and fam["a1"] == "TOP" and "a0" not in info, fam
        g2 = _graph(n_anchors=3, split_anchors=3, deep=1)
        info2, fam2 = sites_and_families(g2)
        assert fam2["a0_c0"] == "a0" and info2["a0"] == (1, 120) and info2["a0_c0"] == (2, 70), (fam2, info2)

    def heap(tmp):
        need, live, h = heap_estimate(7000, 512, 300, 12)
        assert live == 12 and abs(need - 12 * 7000 * (7 * 512 + 384) * 8 / 1024 ** 3) < 1e-12 and h == 6, (need, h)
        need2, live2, h2 = heap_estimate(11845, 512, 300, 24)
        assert h2 == math.ceil(need2 / 0.9) and h2 > 6, (need2, h2)

    def refusals(tmp):
        db = setup(tmp, st=dict(stamp, poolId="pv2_41dbd3dbcd399df0"), ptr_st=dict(stamp, poolId="pv2_41dbd3dbcd399df0"))
        try:
            dry_run(cfg0, db, root=tmp, out=lambda s: None)
            raise AssertionError("pv2_41 member not refused")
        except SystemExit as e:
            assert "P2: the stamp is not the MMLU_PRO member of pv2_1575de61bb20e977: poolId 'pv2_41dbd3dbcd399df0'" in str(e), e
        os.makedirs(os.path.join(tmp, "b"))
        db2 = setup(os.path.join(tmp, "b"), ptr_st=dict(stamp, rule="other"))
        try:
            dry_run(cfg0, db2, root=os.path.join(tmp, "b"), out=lambda s: None)
            raise AssertionError("pointer mismatch not refused")
        except SystemExit as e:
            assert "P2: the snapshot's stamp differs from the pointer entry B0/mmlu_pro_lb" in str(e), e
        try:
            dry_run(cfg0, db2, root=os.path.join(tmp, "nowhere"), out=lambda s: None)
            raise AssertionError("owed pointer not refused")
        except SystemExit as e:
            assert "P1: the pointer file experiment_configs/rp12/objects_of_record.json is owed" in str(e), e
        os.makedirs(os.path.join(tmp, "c"))
        db3 = setup(os.path.join(tmp, "c"))
        outp = os.path.join(tmp, "c", cfg0["outCsv"])
        os.makedirs(os.path.dirname(outp)); open(outp, "w").write("x")
        try:
            dry_run(cfg0, db3, root=os.path.join(tmp, "c"), out=lambda s: None)
            raise AssertionError("existing outCsv not refused")
        except SystemExit as e:
            assert "P5:" in str(e), e
        bad = os.path.join(tmp, "bad.toml")
        open(bad, "w").write(open(os.path.join(ROOT, CONFIG_DEFAULT)).read() + 'extraKey = 1\n')
        try:
            load_config(bad)
            raise AssertionError("unknown key accepted")
        except SystemExit as e:
            assert "unknown keys ['extraKey'], missing keys []" in str(e), e
        open(bad, "w").write(open(os.path.join(ROOT, CONFIG_DEFAULT)).read().replace("nullReps        = 300", 'nullReps        = "300"'))
        try:
            load_config(bad)
            raise AssertionError("string reps accepted")
        except SystemExit as e:
            assert "nullReps = '300' is not a int" in str(e), e

    for nm, fn in [("the committed config's values and its pool file sha", committed_config), ("dry-run on a 14-anchor member", dry_ok),
                   ("m > 15 prints UNDETERMINED-by-support", m_over), ("m = 15 is reachable (the boundary)", m_boundary), ("sites and families (cert_resolution's rule)", families),
                   ("D-12 root site refused; D-15 one-child node not a site", root_site), ("rp12-r2-lane: config lanes", lanes),
                   ("D-2 mixed TOP depths [1, 2] refused", mixed_depths),
                   ("heap estimate (the harness's rule)", heap), ("refusals: pool, pointer, owed pointer, outCsv, config keys", refusals)]:
        case(nm, fn)
    print("%s selftest: %d / %d passed" % (TAG, len(ran) - len(fails), len(ran)))
    return 1 if fails else 0


def lane_check(lane, config_path, cfg, root=ROOT):
    """rp12-r2-lane: the config, its pointer file and its outCsv belong to the lane (another lane's REFUSES; in lane r2 they lie
    inside it and the pointer is the lane's own)."""
    import rp12_lane as LN
    LN.guard(lane, [("config", config_path), ("pointerFile", cfg["pointerFile"]), ("outCsv", cfg["outCsv"])], root=root)
    if lane != "r1" and LN.rel(cfg["pointerFile"], root) != LN.pointer(lane):
        refuse("lane %s reads only its own pointer %s, not %s" % (lane, LN.pointer(lane), cfg["pointerFile"]))
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true"); g.add_argument("--dry-run", action="store_true")
    ap.add_argument("--config", default=None)
    ap.add_argument("--snapshot-db", default=os.path.join(os.environ.get("TAXOARENA_DATA_ROOT", ROOT), "snapshots.db"))
    import rp12_lane as LN
    LN.add_arg(ap)
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    a.config = a.config or os.path.join(ROOT, CONFIG_DEFAULT if a.lane == "r1" else os.path.join(*LN.configs(a.lane).split("/"), "B0", "g12_site_null.sitenull"))
    cfg = load_config(a.config)
    lane_check(a.lane, a.config, cfg)
    dry_run(cfg, a.snapshot_db)
    return 0


if __name__ == "__main__":
    sys.exit(main())
