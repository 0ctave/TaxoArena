"""rp12_build_configs.py: the build TOMLs of RP12 ARCH-V2-E-T (READY_rp12_et C-0), generated from ONE recipe so the arms cannot drift.

REGISTRATION OF RECORD: docs/judge_v2_program.md L22028-L22060 (0a0361b) INSTRUMENT: "the promoted bareq512_s42 geometry
(experiment_configs/promoted/bareq512_s42.toml; embeddingSliceDim 512, mcs 55) with labelling and judge induction OFF,
federated per corpus under a union root, routed flatLeaf; NO D-sweep. Arms: B0 the object of record (seed 42); B0' a replay
of B0's TOML (G10); o1, o2 = B0 + constructionOrderShuffleSeed 1 / 2 (G15)". The orchestrator's C-3 ruling (2026-09-30):
G15 is read PER MEMBER; o1 and o2 rebuild the members; h9_stability reads each member against its B0' member; the union-level
G15 is dropped as vacuous (the registrar brackets it).

WHAT IS WRITTEN (write-once per file; --check compares the committed files with a fresh generation, byte for byte):
  experiment_configs/rp12/<arm>/<member>.toml         arm in B0, B0p, o1, o2; member in bbh, math, musr, ifeval, gpqa, mmlu_pro_lb
  experiment_configs/rp12/B0/graft_flatleaf.toml.tmpl  the union graft of B0's six members, flatLeaf, item-keyed readout
  experiment_configs/rp12/B0/graft_descent.toml.tmpl   the same graft read by descent (G11's D_fd pairs flatLeaf with descent)
  experiment_configs/rp12/B0p/graft_flatleaf.toml.tmpl B0''s graft (G10 compares B0 and B0' grafts too)
A template carries __SNAP_<MEMBER>__ placeholders for the member snapshot ids, which exist only after the member builds;
`--fill <template> MEMBER=<snapshot id> ...` writes the .toml beside it (write-once) and refuses a placeholder left over.

THE MEMBERS (a DEVIATION from C-0's wording, stated for the delta review): all six members are built on the multi-corpus DB
(multicorpus_cache_v1.db, corpus_questions) with v2PoolFile = the union member pool file pv2_1575de61bb20e977; the MMLU-Pro
member is MMLU_PRO_LB (the corpus version mc6-2026-09-11's MMLU_PRO source). C-0 asked for the MMLU-Pro member on the
mmlu_pro table with pv2_41dbd3dbcd399df0, but a union graft reads its corpora from ONE corpusDbPath and the multi-corpus DB
has no mmlu_pro table, so a mixed graft cannot run its readout. The EVAL items are the same: mc6's MMLU_PRO EVAL items are
exactly pv2_41dbd3dbcd399df0's 3,492 (READY_rp12_et claim 4, intersection 3,492), so FLAT (flat_v2, pv2_41's ids, text-keyed)
reads T2 = the MMLU_PRO_LB member unchanged, and no foreign-pool member enters the graft (v2ForeignMembers stays empty).

LAUNCH (per file; one construction at a time, rule 7; THREAD-CAP: 12 threads; backup before each build):
  ./gradlew.bat bootRun --console=plain --offline -PjvmThreads=12 --args="--config experiment_configs/rp12/B0/bbh.toml"
ORDER (C-2): the six B0 members, then B0's grafts, STOP for the staged proof; then B0p (members + graft), o1, o2 (members only).

  python tools/analysis/rp12_build_configs.py --write        # writes every missing file (never overwrites)
  python tools/analysis/rp12_build_configs.py --check        # 0 iff the committed files equal the generation
  python tools/analysis/rp12_build_configs.py --fill experiment_configs/rp12/B0/graft_flatleaf.toml.tmpl BBH=... MATH=... ...
  python tools/analysis/rp12_build_configs.py --selftest
[DELTA 2026-10-01 rp12-r2-lane (orchestrator: set up the R2 lane before any R2 build; insertion only)] --write, --check and
--fill take --lane {r1,r2} (tools/analysis/rp12_lane.py; default r1). Lane r1 generates exactly the bytes of record (the
committed R1 set still passes --check). Lane r2 writes experiment_configs/rp12_r2/<arm>/... with outputDir under
experiment_results/archv2/rp12_r2/ and its own launch lines, plus one header line naming the lane. --fill refuses a template
outside the lane's configs root and a snapshot id that is an object of the other lane (its pointer file). Design (a) over
(b) (git mv R1 into an archive) is argued in rp12_lane.py's docstring.
  python tools/analysis/rp12_build_configs.py --write --lane r2 ; --check --lane r2 ; --fill <rp12_r2 template> ... --lane r2
"""
import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rp12_lane as L  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join("experiment_configs", "rp12")
POOL = "pv2_1575de61bb20e977"
POOL_FILE = "experiment_configs/engine_pool_%s.json" % POOL
DB = "multicorpus_cache_v1.db"
MEMBERS = (("bbh", "BBH"), ("math", "MATH"), ("musr", "MUSR"), ("ifeval", "IFEVAL"), ("gpqa", "GPQA"), ("mmlu_pro_lb", "MMLU_PRO_LB"))
ARMS = (("B0", None), ("B0p", None), ("o1", 1), ("o2", 2))
MODELS = ("DeepSeek-R1-Distill-Llama-8B", "DeepSeek-R1-Distill-Qwen-32B", "Falcon3-10B-Instruct", "Llama-3.1-70B-Instruct",
          "Llama-3.2-3B-Instruct", "Llama-3.3-70B-Instruct", "Mistral-Small-Instruct-2409", "Mixtral-8x7B-Instruct-v0.1",
          "OLMo-2-1124-7B-Instruct", "Phi-3.5-mini-instruct", "Qwen2.5-32B-Instruct", "Qwen2.5-72B-Instruct", "Qwen2.5-7B-Instruct",
          "Qwen2.5-Coder-7B-Instruct", "Qwen2.5-Math-7B-Instruct", "Yi-1.5-34B-Chat-16K", "c4ai-command-r-plus-08-2024",
          "internlm2_5-20b-chat")
# the promoted bareq512_s42 geometry (experiment_configs/promoted/bareq512_s42.toml) with labelling / judge induction OFF
GEOMETRY = """dagMode = "DAG_MAX"

maxDepth              = 8
minClusterSize        = 55
proposalSeparationBar = 0.0145
tau                   = 1e-6
acceptanceZ           = 2.0
enableRefitGate       = false

membershipFloor       = 0.25
routingBeamGamma      = 0.2
descentMargin         = 0.12

effectiveSupportFloor = 2.0
defaultKappaPrior     = 10.0

numIterations         = 50
maxLeafAssignments    = 5

fusionSimilarityThreshold = 0.90
enableGtWarmStart         = false

enableProfiling           = true

embeddingSliceDim = 512
splitDropTopPcs   = 0
splitWhiten       = false
"""


def _models():
    return "models = [\n" + ",\n".join('    "%s"' % m for m in MODELS) + "\n]\n"


def _lane_line(lane):
    return "" if lane == "r1" else ("# LANE %s (tools/analysis/rp12_lane.py): R1's objects of record stay under %s/ and %s/.\n"
                                    % (lane.upper(), L.configs("r1"), L.results("r1")))


def member_toml(arm, shuffle, tag, corpus, lane="r1"):
    head = ("# RP12 ARCH-V2-E-T (docs/judge_v2_program.md L22028-L22060, 0a0361b), arm %s, member %s. GENERATED by\n"
            "# tools/analysis/rp12_build_configs.py (do not edit by hand; --check). Label-free build (labelling and judge induction\n"
            "# OFF), the promoted bareq512_s42 geometry, the v2 split taken as given from the union member pool file.\n"
            "# Launch: ./gradlew.bat bootRun --console=plain --offline -PjvmThreads=12 --args=\"--config %s/%s/%s.toml\"\n"
            % (arm, corpus, L.configs(lane), arm, tag)) + _lane_line(lane)
    body = ('corpora      = ["%s"]\ncorpusDbPath = "%s"\n\n' % (corpus, DB) + _models() +
            '\ncategory      = ""\nqueryLimit    = 0\noutputDir     = "%s/%s/%s"\nseed          = 42\n' % (L.results(lane), arm, tag) +
            'v2PoolFile    = "%s"\npool          = "%s"\n' % (POOL_FILE, POOL))
    if shuffle is not None:
        body += "constructionOrderShuffleSeed = %d   # G15 order arm (the orchestrator's C-3 ruling: read per member)\n" % shuffle
    body += ("\nrunPipeline        = true\nrunBenchmark       = false\nrunTrickle         = true\nrunBaselines       = false\n"
             "enableFinalMetrics = true\nenableLabeling     = false\njudgeInduction     = false\n\n")
    return head + body + GEOMETRY


def graft_template(arm, rule, lane="r1"):
    head = ("# RP12 ARCH-V2-E-T union graft of arm %s's six members, root rule %s, item-keyed readout (RP12 B3). GENERATED TEMPLATE\n"
            "# (tools/analysis/rp12_build_configs.py): fill the member snapshot ids with --fill after the six member builds.\n"
            "# Launch: ./gradlew.bat bootRun --console=plain --offline -PjvmThreads=12 --args=\"--config <the filled .toml>\"\n" % (arm, rule)
            ) + _lane_line(lane)
    snaps = "unionSnapshots = [\n" + ",\n".join('    "__SNAP_%s__"' % c for _t, c in MEMBERS) + "\n]\n"
    body = (snaps + "corpora      = [%s]\n" % ", ".join('"%s"' % c for _t, c in MEMBERS) + 'corpusDbPath = "%s"\n' % DB +
            'unionRootRouting    = "%s"\nunionRoutingItemKey = true\n' % rule +
            'v2PoolFile    = "%s"\npool          = "%s"\n\n' % (POOL_FILE, POOL) + _models() +
            '\ncategory      = ""\nqueryLimit    = 0\noutputDir     = "%s/%s/graft_%s"\nseed          = 42\n'
            % (L.results(lane), arm, rule.lower()) +
            "\nrunPipeline        = false\nrunBenchmark       = false\nrunTrickle         = true\nrunBaselines       = false\n"
            "enableFinalMetrics = false\nenableLabeling     = false\njudgeInduction     = false\n\n")
    return head + body + GEOMETRY


def plan(lane="r1"):
    """{relative path: text} of every generated file of a lane."""
    out = {}
    o = os.path.join(*L.configs(lane).split("/"))
    for arm, shuffle in ARMS:
        for tag, corpus in MEMBERS:
            out[os.path.join(o, arm, tag + ".toml")] = member_toml(arm, shuffle, tag, corpus, lane)
    out[os.path.join(o, "B0", "graft_flatleaf.toml.tmpl")] = graft_template("B0", "flatLeaf", lane)
    out[os.path.join(o, "B0", "graft_descent.toml.tmpl")] = graft_template("B0", "descent", lane)
    out[os.path.join(o, "B0p", "graft_flatleaf.toml.tmpl")] = graft_template("B0p", "flatLeaf", lane)
    return out


def write(root=ROOT, lane="r1"):
    n = 0
    for rel, text in plan(lane).items():
        p = os.path.join(root, rel)
        if os.path.exists(p):
            continue
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "x", encoding="utf-8", newline="\n") as f:
            f.write(text)
        n += 1
    return n


def check(root=ROOT, lane="r1"):
    bad = []
    for rel, text in plan(lane).items():
        p = os.path.join(root, rel)
        if not os.path.exists(p):
            bad.append((rel, "missing"))
            continue
        got = open(p, "rb").read().replace(b"\r\n", b"\n").decode("utf-8")
        if got != text:
            bad.append((rel, "differs from the generation"))
    return bad


def fill(template, pairs, lane="r1", root=ROOT):
    if not template.endswith(".toml.tmpl"):
        raise SystemExit("[RP12-CONFIGS] REFUSED: %s is not a .toml.tmpl template" % template)
    L.require(lane, [template], "template", root=root, inside=True)
    text = open(template, "rb").read().replace(b"\r\n", b"\n").decode("utf-8")
    want = {c for _t, c in MEMBERS}
    given = dict(p.split("=", 1) for p in pairs)
    if set(given) != want:
        raise SystemExit("[RP12-CONFIGS] REFUSED: --fill needs exactly %s (got %s)" % (sorted(want), sorted(given)))
    for c, sid in given.items():
        if not sid or '"' in sid or "__SNAP_" in sid:
            raise SystemExit("[RP12-CONFIGS] REFUSED: snapshot id %r for %s" % (sid, c))
        text = text.replace("__SNAP_%s__" % c, sid)
    L.require_snapshots(lane, list(given.values()), root)
    if "__SNAP_" in text:
        raise SystemExit("[RP12-CONFIGS] REFUSED: a placeholder is left in %s" % template)
    dest = template[:-len(".tmpl")]
    with open(dest, "x", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return dest


def selftest():
    import tempfile, shutil; import scratch_dir  # TEMP-SPRAWL: temp on E:, removed at exit
    fails = []
    tmp = tempfile.mkdtemp(prefix="rp12cfg_")
    try:
        n = write(tmp)
        if n != 27:
            fails.append("write count %d != 27" % n)
        if check(tmp):
            fails.append("check after write: %s" % check(tmp))
        if write(tmp) != 0:
            fails.append("a second write overwrote")
        p = os.path.join(tmp, OUT, "o1", "gpqa.toml")
        with open(p, "a", encoding="utf-8") as f:
            f.write("# edited\n")
        if check(tmp) != [(os.path.join(OUT, "o1", "gpqa.toml"), "differs from the generation")]:
            fails.append("check did not catch an edit")
        b0, b0p, o2 = (open(os.path.join(tmp, OUT, a, "bbh.toml"), encoding="utf-8").read() for a in ("B0", "B0p", "o2"))
        # B0' is B0's TOML up to the output dir and the header's arm name; o2 adds exactly the shuffle-seed line
        norm = lambda t, a: t.replace("arm %s," % a, "arm X,").replace("/%s/" % a, "/X/")
        if norm(b0, "B0") != norm(b0p, "B0p"):
            fails.append("B0p is not B0's replay")
        extra = [l for l in norm(o2, "o2").splitlines() if l not in norm(b0, "B0").splitlines()]
        if extra != ["constructionOrderShuffleSeed = 2   # G15 order arm (the orchestrator's C-3 ruling: read per member)"]:
            fails.append("o2 differs from B0 by %s" % extra)
        for line in ('v2PoolFile    = "experiment_configs/engine_pool_pv2_1575de61bb20e977.json"', 'pool          = "pv2_1575de61bb20e977"',
                     "enableLabeling     = false", "judgeInduction     = false", "embeddingSliceDim = 512", "minClusterSize        = 55",
                     "proposalSeparationBar = 0.0145"):
            if line not in b0:
                fails.append("B0 member lacks %r" % line)
        t = os.path.join(tmp, OUT, "B0", "graft_descent.toml.tmpl")
        pairs = ["%s=S_%s" % (c, c) for _t, c in MEMBERS]
        dest = fill(t, pairs, root=tmp)
        g = open(dest, encoding="utf-8").read()
        if '"S_BBH"' not in g or "__SNAP_" in g or 'unionRootRouting    = "descent"' not in g or "unionRoutingItemKey = true" not in g:
            fails.append("fill output wrong")
        for bad, needle in ((pairs[:-1], "needs exactly"), (pairs[:-1] + ["MMLU_PRO_LB=__SNAP_X__"], "snapshot id")):
            try:
                fill(os.path.join(tmp, OUT, "B0", "graft_flatleaf.toml.tmpl"), bad, root=tmp)
                fails.append("fill accepted %s" % bad[-1])
            except SystemExit as e:
                if needle not in str(e):
                    fails.append("fill refusal text %s" % e)
        try:
            fill(t, pairs, root=tmp)
            fails.append("fill overwrote")
        except FileExistsError:
            pass
        # rp12-r2-lane: the R2 lane writes its own 27 files beside R1's (none of R1's touched), each differing from R1's only
        # in the lane roots and the one lane header line; --check per lane; R1's committed set still equals lane r1's generation
        r1_before = {rel_: open(os.path.join(tmp, rel_), "rb").read() for rel_ in plan("r1")}
        if write(tmp, "r2") != 27 or check(tmp, "r2") or {rel_: open(os.path.join(tmp, rel_), "rb").read() for rel_ in plan("r1")} != r1_before:
            fails.append("the r2 write is not 27 own files beside an untouched r1")
        r2b0 = open(os.path.join(tmp, "experiment_configs", "rp12_r2", "B0", "bbh.toml"), encoding="utf-8").read()
        r1b0 = open(os.path.join(tmp, "experiment_configs", "rp12", "B0", "bbh.toml"), encoding="utf-8").read()
        if 'outputDir     = "experiment_results/archv2/rp12_r2/B0/bbh"' not in r2b0 or any("archv2/rp12/" in l for l in r2b0.splitlines() if not l.startswith("#")) \
                or '--config experiment_configs/rp12_r2/B0/bbh.toml' not in r2b0:
            fails.append("r2 member TOML roots wrong")
        lane_line = ("# LANE R2 (tools/analysis/rp12_lane.py): R1's objects of record stay under experiment_configs/rp12/ and"
                     " experiment_results/archv2/rp12/.")
        if [l for l in r2b0.splitlines() if l not in r1b0.splitlines()] != [
                '# Launch: ./gradlew.bat bootRun --console=plain --offline -PjvmThreads=12 --args="--config experiment_configs/rp12_r2/B0/bbh.toml"',
                lane_line, 'outputDir     = "experiment_results/archv2/rp12_r2/B0/bbh"']:
            fails.append("r2 differs from r1 beyond the lane roots and line: %s" % [l for l in r2b0.splitlines() if l not in r1b0.splitlines()])
        gt = open(os.path.join(tmp, "experiment_configs", "rp12_r2", "B0p", "graft_flatleaf.toml.tmpl"), encoding="utf-8").read()
        if 'outputDir     = "experiment_results/archv2/rp12_r2/B0p/graft_flatleaf"' not in gt or lane_line not in gt:
            fails.append("r2 graft template roots wrong")
        # --fill in lane r2: an R1 template refuses; an R1 snapshot id (the R1 pointer) refuses; R2 ids fill the R2 template
        os.makedirs(os.path.join(tmp, "experiment_configs", "rp12"), exist_ok=True)
        with open(os.path.join(tmp, "experiment_configs", "rp12", "objects_of_record.json"), "w") as f:
            f.write('{"entries": {"B0/bbh": {"snapshot_id": "R1_BBH"}}}')
        t2 = os.path.join(tmp, "experiment_configs", "rp12_r2", "B0", "graft_flatleaf.toml.tmpl")
        r2pairs = ["%s=R2_%s" % (c, c) for _t, c in MEMBERS]
        for args, needle in (((os.path.join(tmp, "experiment_configs", "rp12", "B0p", "graft_flatleaf.toml.tmpl"), r2pairs, "r2", tmp),
                              "is an object of lane r1, the run is lane r2"),
                             ((t2, ["BBH=R1_BBH"] + r2pairs[1:], "r2", tmp), "snapshot id(s) ['R1_BBH'] are lane r1 objects (B0/bbh)"),
                             ((t2, r2pairs, "r1", tmp), "is an object of lane r2, the run is lane r1")):
            try:
                fill(*args)
                fails.append("fill accepted: %s" % needle)
            except SystemExit as e:
                if needle not in str(e):
                    fails.append("fill refusal %r lacks %r" % (str(e), needle))
        if os.path.exists(t2[:-len(".tmpl")]):
            fails.append("a refused fill wrote")
        d2 = fill(t2, r2pairs, "r2", tmp)
        if '"R2_BBH"' not in open(d2, encoding="utf-8").read() or not d2.endswith(os.path.join("rp12_r2", "B0", "graft_flatleaf.toml")):
            fails.append("r2 fill output wrong")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    # the committed R1 set is lane r1's generation, byte for byte (the R1 objects of record are untouched by the lane code)
    bad_r1 = check(ROOT, "r1")
    if bad_r1:
        fails.append("the committed R1 set fails --check: %s" % bad_r1)
    for f_ in fails:
        print("  FAIL " + f_)
    print("[RP12-CONFIGS] selftest: %s (%d failure(s))" % ("PASS" if not fails else "FAIL", len(fails)))
    return 1 if fails else 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--write", action="store_true"); g.add_argument("--check", action="store_true")
    g.add_argument("--selftest", action="store_true"); g.add_argument("--fill", nargs="+", metavar=("TEMPLATE", "MEMBER=SNAPSHOT"))
    L.add_arg(ap)
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.lane != "r1":
        print("[RP12-CONFIGS] lane %s: %s/ and %s/" % (a.lane, L.configs(a.lane), L.results(a.lane)))
    if a.write:
        print("[RP12-CONFIGS] wrote %d file(s)" % write(lane=a.lane))
        return 0
    if a.check:
        bad = check(lane=a.lane)
        for rel, why in bad:
            print("[RP12-CONFIGS] %s: %s" % (rel, why))
        print("[RP12-CONFIGS] check: %s" % ("OK (%d files)" % len(plan(a.lane)) if not bad else "%d defect(s)" % len(bad)))
        return 1 if bad else 0
    print("[RP12-CONFIGS] wrote %s" % fill(a.fill[0], a.fill[1:], a.lane))
    return 0


if __name__ == "__main__":
    sys.exit(main())
