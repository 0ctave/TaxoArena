"""H9 stability metrics: compare counterfactual construction runs to the frozen artifact.

Usage: python tools/analysis/h9_stability.py <run_dir> [<run_dir> ...]
Each run_dir is a per-seed export directory (e.g. experiment_results/h9_seed137/seed_137).
The frozen baseline is experiment_results/freeze_mcs55/seed_42.

Metrics (H9 registration, 801acbf): structure (nodes/leaves/depth/iterations,
certificate), held-out routing Top-1 (claim alpha: spread < 2.5pp), per-anchor
mass-share drift vs frozen (claim beta part 1: < 5pp everywhere), and greedy
mu-matching of frozen leaves to counterparts at cos >= 0.95 (claim beta part 2,
substitute for per-question ARI, which the exports do not carry: leaf identity is
"unstable" when a substantial fraction of frozen leaves lack a close counterpart).

[ADDED 2026-09-29 for RP12 ARCH-V2-E-T G15 (registered at 0a0361b, docs/judge_v2_program.md L22028-L22060; engine-coder,
zero calls): an optional --baseline argument re-points the baseline from the frozen artefact to a named run dir (B0):

  python tools/analysis/h9_stability.py --baseline <B0_run_dir> <o1_run_dir> <o2_run_dir>
  python tools/analysis/h9_stability.py --selftest

WITHOUT --baseline the script is the pre-RP12 script: main() below is byte-for-byte the old function and prints the old
text (the selftest runs the base blob 2b77fcd4 from git and compares stdout byte for byte). WITH --baseline, main_baseline()
prints, per arm, the leaves, depth, Top-1 ("n/a" when the arm's validation CSV has no Top1Accuracy row, e.g. a union
build's flatLeaf routing; the operator names the per-member run dirs at READY), the anchor drift by h9's rule (max over
the BASELINE's depth-1 anchors of |share(arm) - share(B0)|, an anchor absent in the arm counting share 0) and the greedy
mu-match at cos >= 0.95 AND >= 0.99; then G15's line, the POINT deciding:
  drift = max over the arms given of the per-arm drift; HELD iff drift <= 0.6pp (the synthesis bar, tree V7), FAILED
  iff drift > 0.6pp (compared in pp with a 1e-9 tolerance, so an exact 0.6pp reads HELD). G15 licenses nothing about
  order variance beyond the arms given. The alpha line is not printed in this mode (it is H9's claim, not G15's).
SELFTEST MUTANTS (run 2026-09-29 by a harness, one temporary edit at a time, reverted; H0 is the harness control):
  H0 control (comment appended)                                 survived
  H1 drift = min over arms (not max)                            killed: G15 FAILED case (arm o2 carries the 0.7pp drift)
  H2 first arm only                                             killed: G15 FAILED case
  H3 bar compared with < (exact 0.6pp reads FAILED)             killed: boundary case (0.6pp HELD)
  H4 baseline = frozen even with --baseline                     killed: baseline case (B0's own shares)
  H5 0.99 match uses 0.95                                       killed: mu-match 0.99 count
  H6 legacy main edited (drift in fraction, not pp)             killed: legacy byte-identity against the base blob
  H7 anchors of the ARM (not the baseline) iterated             killed: missing-anchor case (an arm lacking an anchor)
]
[DELTA 2026-10-01 rp12-r2-lane; insertion only] --lane {r1,r2} (tools/analysis/rp12_lane.py; default r1 = the commands of
record, unchanged): G15's run dirs (--lane r2 goes before --baseline) of the other lane REFUSE; in lane r2 they must lie
inside experiment_configs/rp12_r2/ or experiment_results/archv2/rp12_r2/; the no-flag pre-RP12 path is untouched.
"""
import json, csv, os, sys

FROZEN = os.path.join("experiment_results", "freeze_mcs55", "seed_42")

def last_snapshot(path):
    last = None
    with open(os.path.join(path, "dag_snapshots.jsonl"), encoding="utf-8") as f:
        for line in f:
            last = line
    return json.loads(last)

def top1(path):
    with open(os.path.join(path, "validation", "MAIN_centroid_routing_results.csv")) as f:
        for row in csv.reader(f):
            if row and row[0] == "Top1Accuracy":
                return float(row[1])

def load(path):
    snap = last_snapshot(path)
    nodes = snap["nodes"]
    anchors = [n for n in nodes if n["depth"] == 1]
    tot = sum(a["subtreeQueries"] for a in anchors)
    return dict(
        it=snap["iteration"], nodes=len(nodes),
        leaves=[n for n in nodes if n["isLeaf"]],
        depth=max(n["depth"] for n in nodes), top1=top1(path),
        ashare={a["label"]: a["subtreeQueries"] / tot for a in anchors})

def cos(u, v):
    return sum(a * b for a, b in zip(u, v))

def main(run_dirs):
    fro = load(FROZEN)
    print("frozen : it %2d nodes %3d leaves %2d depth %d top1 %.3f"
          % (fro["it"], fro["nodes"], len(fro["leaves"]), fro["depth"], fro["top1"]))
    t1s = [fro["top1"]]
    for rd in run_dirs:
        d = load(rd)
        t1s.append(d["top1"])
        drift = max(abs(d["ashare"].get(a, 0) - s) for a, s in fro["ashare"].items())
        used, matched = set(), 0
        for f in fro["leaves"]:
            best, bi = -1, None
            for i, c in enumerate(d["leaves"]):
                if i in used:
                    continue
                s = cos(f["vmfMu"], c["vmfMu"])
                if s > best:
                    best, bi = s, i
            if best >= 0.95:
                matched += 1
                used.add(bi)
        print("%s: it %2d nodes %3d leaves %2d depth %d top1 %.3f | anchor drift %.2fpp | mu-match %d/%d"
              % (os.path.basename(os.path.dirname(rd)) or rd, d["it"], d["nodes"], len(d["leaves"]),
                 d["depth"], d["top1"], 100 * drift, matched, len(fro["leaves"])))
    print("alpha: Top-1 spread %.1fpp (registered bar 2.5pp): %s"
          % (100 * (max(t1s) - min(t1s)), "PASS" if max(t1s) - min(t1s) < 0.025 else "FAIL"))


# ── RP12 G15: --baseline (absent = main() above, unchanged) ─────────────────────────────────────────────────────────

G15_BAR_PP = 0.6


def _top1_or_none(path):
    try:
        return top1(path)
    except OSError:
        return None


def _load_b(path):
    snap = last_snapshot(path)
    nodes = snap["nodes"]
    anchors = [n for n in nodes if n["depth"] == 1]
    tot = sum(a["subtreeQueries"] for a in anchors)
    return dict(it=snap["iteration"], nodes=len(nodes), leaves=[n for n in nodes if n["isLeaf"]],
                depth=max(n["depth"] for n in nodes), top1=_top1_or_none(path),
                ashare={a["label"]: a["subtreeQueries"] / tot for a in anchors})


def mu_match(base_leaves, arm_leaves, bar):
    """h9's greedy matching of the baseline's leaves to unused arm leaves; a match iff the best cos >= bar."""
    used, matched = set(), 0
    for f in base_leaves:
        best, bi = -1, None
        for i, c in enumerate(arm_leaves):
            if i in used:
                continue
            s = cos(f["vmfMu"], c["vmfMu"])
            if s > best:
                best, bi = s, i
        if best >= bar:
            matched += 1
            used.add(bi)
    return matched


def anchor_drift(base, arm):
    """h9's rule: max over the BASELINE's depth-1 anchors of |share(arm) - share(base)|, absent anchor = share 0."""
    return max(abs(arm["ashare"].get(a, 0) - s) for a, s in base["ashare"].items())


def g15_verdict(drift_pp):
    return "HELD" if drift_pp <= G15_BAR_PP + 1e-9 else "FAILED"


def main_baseline(baseline, run_dirs):
    if not run_dirs:
        raise SystemExit("[G15] REFUSED: --baseline needs at least one arm run dir")
    b = _load_b(baseline)
    fmt_t1 = lambda t: "n/a" if t is None else "%.3f" % t
    print("baseline %s: it %2d nodes %3d leaves %2d depth %d top1 %s"
          % (baseline, b["it"], b["nodes"], len(b["leaves"]), b["depth"], fmt_t1(b["top1"])))
    drifts = []
    for rd in run_dirs:
        d = _load_b(rd)
        dr = 100 * anchor_drift(b, d)
        drifts.append(dr)
        print("%s: it %2d nodes %3d leaves %2d depth %d top1 %s | anchor drift %.2fpp | mu-match@0.95 %d/%d"
              " | mu-match@0.99 %d/%d"
              % (rd, d["it"], d["nodes"], len(d["leaves"]), d["depth"], fmt_t1(d["top1"]), dr,
                 mu_match(b["leaves"], d["leaves"], 0.95), len(b["leaves"]),
                 mu_match(b["leaves"], d["leaves"], 0.99), len(b["leaves"])))
    drift = max(drifts)
    print("G15: drift = %.4fpp (max over %d arm(s) and the baseline's depth-1 anchors; bar %.1fpp, the POINT decides): %s"
          % (drift, len(drifts), G15_BAR_PP, g15_verdict(drift)))
    return drift


def _cli(argv):
    if argv and argv[0] == "--selftest":
        return selftest()
    lane = None
    if argv and argv[0] == "--lane":                       # rp12-r2-lane: --lane {r1,r2} before --baseline (G15 only)
        if len(argv) < 3 or argv[2] != "--baseline":
            raise SystemExit("[G15] REFUSED: --lane takes a lane and goes before --baseline")
        lane, argv = argv[1], argv[2:]
    if argv and argv[0] == "--baseline":
        if len(argv) < 2:
            raise SystemExit("[G15] REFUSED: --baseline needs a run dir")
        import rp12_lane as LN
        LN.guard(LN.check_lane(lane or LN.DEFAULT), [("run dir", d) for d in argv[1:]])
        main_baseline(argv[1], argv[2:])
        return 0
    main(argv)
    return 0


# ── selftest ────────────────────────────────────────────────────────────────────────────────────────────────────────

def _write_run(d, shares, leaves, top1_value=0.8):
    """A run dir: dag_snapshots.jsonl (last line = final) with depth-1 anchors of the given subtreeQueries and leaves of
    the given vmfMu, and validation/MAIN_centroid_routing_results.csv (omitted when top1_value is None)."""
    os.makedirs(os.path.join(d, "validation"), exist_ok=True)
    nodes = [{"id": "root", "depth": 0, "isLeaf": False, "label": "ROOT", "subtreeQueries": sum(shares.values())}]
    for lab, n in shares.items():
        nodes.append({"id": "a_" + lab, "depth": 1, "isLeaf": False, "label": lab, "subtreeQueries": n})
    for i, mu in enumerate(leaves):
        nodes.append({"id": "l%d" % i, "depth": 2, "isLeaf": True, "label": "l%d" % i, "subtreeQueries": 1, "vmfMu": mu})
    with open(os.path.join(d, "dag_snapshots.jsonl"), "w", encoding="utf-8") as f:
        f.write(json.dumps({"iteration": 1, "nodes": nodes[:1]}) + "\n")
        f.write(json.dumps({"iteration": 7, "nodes": nodes}) + "\n")
    if top1_value is not None:
        with open(os.path.join(d, "validation", "MAIN_centroid_routing_results.csv"), "w", newline="") as f:
            f.write("Metric,Value\nTop1Accuracy,%s\n" % top1_value)


def selftest():
    import io, contextlib, tempfile, shutil, subprocess, math; import scratch_dir  # TEMP-SPRAWL: temp on E:, removed at exit
    fails, ran = [], []
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(os.path.dirname(here))

    def unit(v):
        n = math.sqrt(sum(x * x for x in v))
        return [x / n for x in v]

    L = [unit([1, 0, 0]), unit([0, 1, 0]), unit([0, 0, 1])]
    near = unit([1, 0.2, 0])      # cos with L[0] = 0.9806: matches at 0.95, not at 0.99
    close = unit([1, 0.05, 0])    # cos 0.99875: matches at both

    def case(name, fn):
        ran.append(name)
        try:
            fn()
            print("  ok   " + name)
        except (AssertionError, SystemExit, Exception) as e:
            fails.append(name)
            print("  FAIL %s: %s: %s" % (name, type(e).__name__, e))

    def capture(fn, *a):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            r = fn(*a)
        return r, buf.getvalue()

    tmp = tempfile.mkdtemp(prefix="h9st_")
    try:
        B0 = os.path.join(tmp, "B0")
        _write_run(B0, {"math": 500, "law": 300, "bio": 200}, [L[0], L[1], L[2]], 0.81)
        o1 = os.path.join(tmp, "o1")
        _write_run(o1, {"math": 503, "law": 297, "bio": 200}, [close, L[1], L[2]], 0.80)   # drift 0.3pp
        o2 = os.path.join(tmp, "o2")
        _write_run(o2, {"math": 507, "law": 293, "bio": 200}, [near, L[1], L[2]], None)    # drift 0.7pp, no Top-1
        o_edge = os.path.join(tmp, "oe")
        _write_run(o_edge, {"math": 506, "law": 294, "bio": 200}, [L[0], L[1], L[2]], 0.8)  # exactly 0.6pp
        o_miss = os.path.join(tmp, "om")
        _write_run(o_miss, {"math": 700, "bio": 300}, [L[0], L[1], L[2]], 0.8)  # no 'law': 30pp by the baseline's anchors (20 by the arm's)

        def held_one_arm():
            d, out = capture(main_baseline, B0, [o1])
            assert abs(d - 0.3) < 1e-9, d
            assert out.splitlines()[-1] == ("G15: drift = 0.3000pp (max over 1 arm(s) and the baseline's depth-1 anchors;"
                                            " bar 0.6pp, the POINT decides): HELD"), out
            assert "baseline %s: it  7 nodes   7 leaves  3 depth 2 top1 0.810" % B0 in out, out
            assert "| anchor drift 0.30pp | mu-match@0.95 3/3 | mu-match@0.99 3/3" in out, out

        def failed_two_arms():
            d, out = capture(main_baseline, B0, [o1, o2])
            assert abs(d - 0.7) < 1e-9, d
            assert out.splitlines()[-1].endswith("(max over 2 arm(s) and the baseline's depth-1 anchors; bar 0.6pp,"
                                                 " the POINT decides): FAILED"), out
            assert "top1 n/a | anchor drift 0.70pp | mu-match@0.95 3/3 | mu-match@0.99 2/3" in out, out

        def boundary():
            d, out = capture(main_baseline, B0, [o_edge])
            assert out.splitlines()[-1].endswith(": HELD"), out
            assert g15_verdict(0.6000001) == "FAILED" and g15_verdict(0.6) == "HELD"

        def missing_anchor():
            d, out = capture(main_baseline, B0, [o_miss])
            assert abs(d - 30.0) < 1e-9, d

        def lanes():
            r1d, r2d = "experiment_results/archv2/rp12/B0/bbh/seed_42", "experiment_results/archv2/rp12_r2/o1/bbh/seed_42"
            for argv, needle in ((["--lane", "r2", "--baseline", r1d, r2d], "run dir %s is an object of lane r1, the run is lane r2" % r1d),
                                 (["--baseline", r2d, r2d], "run dir %s is an object of lane r2, the run is lane r1" % r2d),
                                 (["--lane", "r2", "--baseline", r2d, o1], "is outside lane r2's roots"),
                                 (["--lane", "r2", r2d], "--lane takes a lane and goes before --baseline")):
                try:
                    _cli(argv)
                    raise AssertionError("not refused: %s" % argv)
                except SystemExit as e:
                    assert needle in str(e), (needle, str(e))

        def refuses_no_arm():
            try:
                main_baseline(B0, [])
            except SystemExit as e:
                assert str(e) == "[G15] REFUSED: --baseline needs at least one arm run dir"
                return
            raise AssertionError("no refusal")

        def legacy_byte_identical():
            # the no-flag path is the pre-RP12 script: run the base blob and this file on the same fixture (FROZEN resolved
            # relative to the working dir) and compare stdout byte for byte
            base = subprocess.run(["git", "show", "2b77fcd49135a8d81b0e859c1ad702f838014f51"], cwd=root,
                                  capture_output=True, check=True).stdout
            bpath = os.path.join(tmp, "h9_base.py")
            open(bpath, "wb").write(base)
            wd = os.path.join(tmp, "wd")
            _write_run(os.path.join(wd, FROZEN), {"math": 500, "law": 300, "bio": 200}, [L[0], L[1], L[2]], 0.81)
            args = [o1, o_edge]
            a = subprocess.run([sys.executable, bpath] + args, cwd=wd, capture_output=True).stdout
            b = subprocess.run([sys.executable, os.path.abspath(__file__)] + args, cwd=wd, capture_output=True).stdout
            assert a and a == b, (a, b)
            assert b"alpha: Top-1 spread 1.0pp (registered bar 2.5pp): PASS" in b, b

        for n, f in [("G15 HELD on one arm (values)", held_one_arm), ("G15 FAILED when the second arm drifts 0.7pp", failed_two_arms),
                     ("G15 boundary 0.6pp is HELD", boundary), ("anchor absent in the arm counts share 0", missing_anchor),
                     ("--baseline without arms refuses", refuses_no_arm), ("rp12-r2-lane: --lane guards the run dirs", lanes),
                     ("no flag: byte-identical to base blob 2b77fcd4", legacy_byte_identical)]:
            case(n, f)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("[G15] selftest: %d / %d passed" % (len(ran) - len(fails), len(ran)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
