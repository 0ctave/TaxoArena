"""rp12_lane.py: the RP12 LANES (R1 = the objects of record already built; R2 = the re-run lane after G10 FAILED as registered,
diagnosis 2b8f809a). ZERO calls; no DB is opened; nothing is written here.

WHY (orchestrator, 2026-10-01): R1's TOMLs point their outputDir at experiment_results/archv2/rp12/{B0,B0p,o1,o2}/..., which R1
filled; the graft TOMLs are filled with R1 snapshot ids; experiment_configs/rp12/objects_of_record.json is write-once. R2 must
never overwrite or mix with R1. CHOSEN DESIGN (a), a lane root, rather than (b) archiving R1 by git mv: R1's committed files
REFER to their own paths (each TOML's outputDir and launch line, the pointer's "toml" fields, the run manifests' config_path,
the snapshot stamps' paths), so a byte-identical move would leave every R1 object pointing at a path that no longer holds it,
and a corrected move would not be byte-identical. With a lane root R1 stays where its own bytes say it is, untouched.

  R1: experiment_configs/rp12/    experiment_results/archv2/rp12/    pointer experiment_configs/rp12/objects_of_record.json
  R2: experiment_configs/rp12_r2/ experiment_results/archv2/rp12_r2/ pointer experiment_configs/rp12_r2/objects_of_record.json

Every RP12 readout tool takes --lane {r1,r2} (default r1, so every R1 command of record is unchanged) and calls require() on
each path it is given: a path inside the OTHER lane's roots REFUSES ("mixes R1 and R2"); require_snapshots() refuses snapshot
ids that are objects of the other lane (read from the other lane's pointer file when it exists).
"""
import os
import json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TAG = "[RP12-LANE]"
LANES = {"r1": {"configs": "experiment_configs/rp12", "results": "experiment_results/archv2/rp12"},
         "r2": {"configs": "experiment_configs/rp12_r2", "results": "experiment_results/archv2/rp12_r2"}}
DEFAULT = "r1"
POINTER_NAME = "objects_of_record.json"


def refuse(msg):
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def check_lane(lane):
    if lane not in LANES:
        refuse("unknown lane %r (want one of %s)" % (lane, sorted(LANES)))
    return lane


def configs(lane):
    return LANES[check_lane(lane)]["configs"]


def results(lane):
    return LANES[check_lane(lane)]["results"]


def pointer(lane):
    return configs(lane) + "/" + POINTER_NAME


def rel(path, root=ROOT):
    """The repo-relative posix form of a path (absolute paths under root are made relative; others are kept as given)."""
    p = str(path).replace("\\", "/")
    if os.path.isabs(str(path)):
        r = os.path.normcase(os.path.abspath(root)).replace("\\", "/").rstrip("/") + "/"
        a = os.path.normcase(os.path.abspath(str(path))).replace("\\", "/")
        if a.startswith(r):
            p = os.path.abspath(str(path)).replace("\\", "/")[len(r):]
    while p.startswith("./"):
        p = p[2:]
    return p


def lane_of(path, root=ROOT):
    """'r1' / 'r2' when the path lies under that lane's configs or results root, else None (a path outside both)."""
    p = rel(path, root)
    pl = p.lower()
    for lane, d in LANES.items():
        for base in (d["configs"], d["results"]):
            if pl == base.lower() or pl.startswith(base.lower() + "/"):
                return lane
    return None


def require(lane, paths, what="path", root=ROOT, inside=False):
    """REFUSES a path that lies in another lane's roots; with inside=True also one outside the lane's own roots."""
    check_lane(lane)
    for p in paths:
        if p is None:
            continue
        l = lane_of(p, root)
        if l is not None and l != lane:
            refuse("%s %s is an object of lane %s, the run is lane %s: R1 and R2 objects are never mixed" % (what, p, l, lane))
        if inside and l != lane:
            refuse("%s %s is outside lane %s's roots (%s, %s)" % (what, p, lane, configs(lane), results(lane)))
    return True


def lane_snapshot_ids(lane, root=ROOT):
    """The snapshot ids of a lane's pointer file (empty when the pointer is not written yet)."""
    p = os.path.join(root, pointer(lane))
    if not os.path.isfile(p):
        return {}
    doc = json.load(open(p, encoding="utf-8"))
    return {e["snapshot_id"]: name for name, e in doc.get("entries", {}).items()}


def require_snapshots(lane, ids, root=ROOT):
    """REFUSES a snapshot id that is an object of ANOTHER lane (by that lane's pointer file)."""
    check_lane(lane)
    for other in LANES:
        if other == lane:
            continue
        theirs = lane_snapshot_ids(other, root)
        bad = sorted(i for i in ids if i in theirs)
        if bad:
            refuse("snapshot id(s) %s are lane %s objects (%s), the run is lane %s: R1 and R2 objects are never mixed"
                   % (bad, other, ", ".join(theirs[i] for i in bad), lane))
    return True


def guard(lane, named_paths, root=ROOT):
    """A readout's paths [(what, path)]: another lane's path REFUSES; in a lane other than r1 every path must lie inside it."""
    for what, p in named_paths:
        require(lane, [p], what, root=root, inside=(lane != "r1"))
    return True


def out_path(lane, *parts):
    """A lane's default output path under its results root (lane r1: the same string the tools used before the lanes)."""
    return os.path.join(ROOT, *(results(lane).split("/") + list(parts)))


def add_arg(ap):
    ap.add_argument("--lane", choices=sorted(LANES), default=DEFAULT,
                    help="RP12 lane: r1 (the objects of record, default) or r2 (the re-run lane); paths of the other lane refuse")
    return ap


def selftest():
    import tempfile, shutil
    fails = []

    def expect_refuse(fn, needle):
        try:
            fn()
            fails.append("not refused: %s" % needle)
        except SystemExit as e:
            if needle not in str(e):
                fails.append("refusal %r lacks %r" % (str(e), needle))

    if (configs("r1"), results("r1"), pointer("r1")) != ("experiment_configs/rp12", "experiment_results/archv2/rp12",
                                                         "experiment_configs/rp12/objects_of_record.json"):
        fails.append("r1 roots changed")
    if (configs("r2"), results("r2"), pointer("r2")) != ("experiment_configs/rp12_r2", "experiment_results/archv2/rp12_r2",
                                                         "experiment_configs/rp12_r2/objects_of_record.json"):
        fails.append("r2 roots wrong")
    cases = [("experiment_configs/rp12/B0/bbh.toml", "r1"), ("experiment_configs/rp12_r2/B0/bbh.toml", "r2"),
             ("experiment_results/archv2/rp12/B0/bbh/seed_42", "r1"), ("experiment_results\\archv2\\rp12_r2\\B0\\bbh\\seed_42", "r2"),
             ("./experiment_results/archv2/rp12_r2", "r2"), ("experiment_results/archv2/rp12x/B0", None),
             ("experiment_results/archv2/rp12_r1/B0", None), ("experiment_configs/engine_pool_pv2_1575de61bb20e977.json", None),
             (os.path.join(ROOT, "experiment_results", "archv2", "rp12", "g11_outcome.txt"), "r1"),
             (os.path.join(ROOT, "Experiment_Results", "archv2", "RP12_R2", "x"), "r2")]
    for p, want in cases:
        if lane_of(p) != want:
            fails.append("lane_of(%r) = %r, want %r" % (p, lane_of(p), want))
    require("r2", ["experiment_results/archv2/rp12_r2/B0/bbh/seed_42", "snapshots.db", None])
    expect_refuse(lambda: require("r2", ["experiment_results/archv2/rp12/B0/bbh/seed_42"], "run dir"),
                  "run dir experiment_results/archv2/rp12/B0/bbh/seed_42 is an object of lane r1, the run is lane r2")
    expect_refuse(lambda: require("r1", ["experiment_configs/rp12_r2/B0/bbh.toml"], "TOML"), "is an object of lane r2, the run is lane r1")
    expect_refuse(lambda: require("r2", ["scratch/x.toml"], "TOML", inside=True), "is outside lane r2's roots")
    require("r2", ["experiment_configs/rp12_r2/B0/bbh.toml"], "TOML", inside=True)
    expect_refuse(lambda: check_lane("r3"), "unknown lane 'r3'")
    tmp = tempfile.mkdtemp(prefix="rp12lane_")
    try:
        os.makedirs(os.path.join(tmp, "experiment_configs", "rp12"))
        with open(os.path.join(tmp, "experiment_configs", "rp12", POINTER_NAME), "w") as f:
            json.dump({"entries": {"B0/bbh": {"snapshot_id": "R1_BBH"}, "B0/math": {"snapshot_id": "R1_MATH"}}}, f)
        if lane_snapshot_ids("r1", tmp) != {"R1_BBH": "B0/bbh", "R1_MATH": "B0/math"} or lane_snapshot_ids("r2", tmp) != {}:
            fails.append("lane_snapshot_ids wrong")
        require_snapshots("r2", ["R2_BBH", "R2_MATH"], tmp)
        expect_refuse(lambda: require_snapshots("r2", ["R2_BBH", "R1_MATH"], tmp),
                      "snapshot id(s) ['R1_MATH'] are lane r1 objects (B0/math), the run is lane r2")
        require_snapshots("r1", ["R1_BBH"], tmp)          # no R2 pointer yet: nothing to refuse
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if out_path("r1", "g11_outcome.txt") != os.path.join(ROOT, "experiment_results", "archv2", "rp12", "g11_outcome.txt") or \
            out_path("r2", "g11_outcome.txt") != os.path.join(ROOT, "experiment_results", "archv2", "rp12_r2", "g11_outcome.txt"):
        fails.append("out_path wrong")
    guard("r1", [("x", "scratch/a"), ("y", None)])
    expect_refuse(lambda: guard("r2", [("validation dir", "experiment_results/archv2/rp12_r2/B0/x"), ("out", "scratch/o.txt")]),
                  "out scratch/o.txt is outside lane r2's roots")
    for f_ in fails:
        print("  FAIL " + f_)
    print("%s selftest: %s (%d failure(s))" % (TAG, "PASS" if not fails else "FAIL", len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    import sys
    sys.exit(selftest() if sys.argv[1:] == ["--selftest"] else (print(__doc__) or 2))
