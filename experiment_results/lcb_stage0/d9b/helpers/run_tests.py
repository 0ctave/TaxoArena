"""Tests for the LCB-D9B-BYTE-INERTNESS instrument (d9b_compare.py, d9b_prep.py, d9b_aux.py). Zero calls. Reads the D9
rerun evidence (scratchpad d9\\run_20260925b: evidence_A / evidence_B outputDirs and the checkpointed pool copies) and the
incident A' pseudoroot BY FILE COPY into <here>\\test_work (recreated on every run); every mutation is made on a copy.
The real A/B and A/A' readouts below are DESCRIPTIVE ONLY: they are the D9 run's outputs, which the registration forbids
scoring under C1' (C-7); they test the instrument, not the change.

usage: python run_tests.py   (exit 0 iff every case reads as expected)
"""
import contextlib, csv, importlib, io, json, os, shutil, sqlite3, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SP = os.path.dirname(HERE)
RB = os.path.join(SP, "d9", "run_20260925b")
APRIME = os.path.join(SP, "d9", "incident_legA_void_20260925", "pseudoroot")
WORK = os.path.join(HERE, "test_work")
MAIN = r"Z:\FAC\TUBerlin\THESIS\TaxoArena"
sys.path.insert(0, HERE)
import d9b_compare as C  # noqa: E402
import d9b_aux as X  # noqa: E402

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print("[%s] %s %s" % ("OK  " if cond else "FAIL", name, detail), flush=True)


def mkroot(name, out_src, db_src):
    r = os.path.join(WORK, "roots", name)
    shutil.copytree(out_src, os.path.join(r, C.OUT))
    for s in ("", "-wal"):
        if os.path.exists(db_src + s):
            shutil.copyfile(db_src + s, os.path.join(r, "ag_news_smoke_cache_v1.db" + s))
    return r


def clone(src, name):
    r = os.path.join(WORK, "roots", name)
    shutil.copytree(src, r)
    return r


_n = [0]


def stage():
    _n[0] += 1
    s = os.path.join(WORK, "st", "s%03d" % _n[0])
    os.makedirs(s)
    return s


def run(argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = C.main(argv)
    return rc, buf.getvalue()


def cmp(x, y, lx="A", ly="B", misses=None):
    s = stage()
    argv = [x, y, s, lx, ly] + (["--misses"] + misses if misses else [])
    rc, out = run(argv)
    js = os.path.join(s, "d9b_compare.json")
    j = json.load(open(js, encoding="utf-8")) if os.path.isfile(js) else None
    return rc, out, j, s


def edit(root, rel, fn):
    p = os.path.join(root, C.OUT, rel)
    b = open(p, "rb").read()
    open(p, "wb").write(fn(b))


def csv_set(root, rel, col, val, row=-1):
    p = os.path.join(root, C.OUT, rel)
    raw = open(p, "rb").read().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    rows = list(csv.reader(io.StringIO(raw, newline="")))
    i = rows[0].index(col)
    rows[row][i] = val
    o = io.StringIO()
    csv.writer(o, lineterminator=nl).writerows(rows)
    open(p, "wb").write(o.getvalue().encode("utf-8"))


def quality_set(root, metric, val):
    def f(b):
        lines = b.decode("utf-8").splitlines(keepends=True)
        out = []
        for ln in lines:
            if ln.split(",")[0] == metric:
                ln = "%s,%s%s" % (metric, val, "\n" if ln.endswith("\n") else "")
            out.append(ln)
        return "".join(out).encode("utf-8")
    edit(root, C.QUALITY, f)


def db_exec(root, sql):
    con = sqlite3.connect(os.path.join(root, "ag_news_smoke_cache_v1.db"))
    con.execute(sql)
    con.commit()
    con.close()


def main():
    if os.path.exists(WORK):
        shutil.rmtree(WORK)
    os.makedirs(WORK)
    A = mkroot("A", os.path.join(RB, "evidence_A", "outputDir"), os.path.join(RB, "pool_copy_A", "ag.db"))
    B = mkroot("B", os.path.join(RB, "evidence_B", "outputDir"), os.path.join(RB, "pool_copy_B", "ag.db"))
    AP = clone(APRIME, "Aprime")
    A_dup = clone(A, "A_dup")

    # T1 EQUAL on duplicated real outputs
    rc, out, j, _ = cmp(A, A_dup, "A", "B")
    check("T1 duplicate of real leg A reads C1' HELD, 0 of 24 differ", rc == 0 and j["differing"] == [] and
          sum(v == "EQUAL" for v in j["status"].values()) == 24, "rc %s" % rc)
    check("T1b the drop lists are printed", out.count("[DROPS]") == 5)
    rc, out, j, _ = cmp(A, A_dup, "A", "A2")
    check("T1c same through the C2 path (A, A2)", rc == 0 and j["criterion"] == "C2" and j["differing"] == [])

    # T2 DESCRIPTIVE: the D9 rerun's A vs B with the declared drops (NOT an outcome)
    rc, out, j_ab_real, _ = cmp(A, B, "A", "B", misses=[os.path.join(RB, "d9_misses_A.txt"), os.path.join(RB, "d9_misses_B.txt")])
    print("---- T2 (DESCRIPTIVE, the D9 rerun A vs B under the D9b drops; NOT an outcome) ----\n" + out + "----")
    check("T2 D9 rerun A vs B under the declared drops: 24 of 24 EQUAL (descriptive)", rc == 0 and j_ab_real["differing"] == [],
          "differing %s" % j_ab_real["differing"])
    check("T2b V7 printed EQUAL from explicit misses files", "[V7] embedding misses A 0" in out and ": EQUAL" in out)
    check("T2c P6 prints TDC relative difference and DP / SS differences",
          "TotalDasguptaCost" in out and "|relative difference|" in out and "DendrogramPurity" in out and "SphericalSilhouette" in out)
    # T3 DESCRIPTIVE: A vs the incident A' through the C2 path
    rc, out, j_aa_real, _ = cmp(A, AP, "A", "A2")
    print("---- T3 (DESCRIPTIVE, A vs the incident A' through the C2 path; NOT an outcome) ----\n" + out + "----")
    check("T3 D9 A vs A' under the declared drops: 24 of 24 EQUAL (descriptive)", rc == 0 and j_aa_real["differing"] == [],
          "differing %s" % j_aa_real["differing"])
    # T3v verdict on the real pair (descriptive)
    s = stage()
    rc, out = run(["--verdict", os.path.join(WORK, "only_one.json")])  # usage refusal
    check("T3u verdict usage refusal", rc == 2)
    ab_js = [os.path.join(WORK, "st", d, "d9b_compare.json") for d in sorted(os.listdir(os.path.join(WORK, "st")))]
    ab_js = [p for p in ab_js if os.path.isfile(p)]
    j_ab_p = [p for p in ab_js if json.load(open(p))["roots"] == [A, B]][0]
    j_aa_p = [p for p in ab_js if json.load(open(p))["roots"] == [A, AP]][0]
    rc, out = run(["--verdict", j_ab_p, j_aa_p, os.path.join(s, "d9b_verdict.txt")])
    print("---- T3v (DESCRIPTIVE verdict on D9 run data; NOT an outcome) ----\n" + out + "----")
    check("T3v verdict on the real three legs maps to DISCHARGED-conditional (descriptive)", rc == 0 and "D9 DISCHARGED" in out)
    check("T3w P6 over three pairs printed", all("[P6 %s," % t in out for t in ("A/B", "A/A2", "B/A2")))
    check("T3y (R2) P6 scored on the real three legs: HELD (descriptive), 22 clause-instances (2 sources x (2 DIFFERS + 3 pairs x 3 bounds))",
          "[P6] HELD (22 clause-instances: 22 hold, 0 fail, 0 undetermined)" in out)
    check("T3z (R2) the B/A2 relative TDC is labelled 'of A' (no 'of B' anywhere)",
          "% of A" in [l for l in out.splitlines() if l.startswith("[P6 B/A2") and "TotalDasguptaCost" in l][0] and "% of B" not in out)
    rc2, _ = run(["--verdict", j_ab_p, j_aa_p, os.path.join(s, "d9b_verdict.txt")])
    check("T3x verdict output is write-once", rc2 == 2)

    # T4 a mutation in each of the 17 byte-compared files is caught, and only that object differs
    for rel in C.BYTE:
        y = clone(A, "m_" + rel.replace("/", "_"))
        edit(y, rel, lambda b: b[:-1] + bytes([b[-1] ^ 1]) if b else b"x")
        rc, _o, j, _ = cmp(A, y)
        check("T4 byte mutation in %s -> DIFFERS" % rel, rc == 3 and j["differing"] == [rel], "%s" % (j and j["differing"]))

    IM, RM, TL = "seed_42/diagnostics/iteration_metrics.csv", "seed_42/diagnostics/run_manifest.json", C.LEDGER
    # T5 iteration_metrics
    y = clone(A, "im_wall"); csv_set(y, IM, "wall_ms", "123456")
    rc, _o, j, _ = cmp(A, y); check("T5a wall_ms changed -> ignored (EQUAL)", rc == 0 and j["differing"] == [])
    y = clone(A, "im_J"); csv_set(y, IM, "J_after_route", "0.999999")
    rc, _o, j, _ = cmp(A, y); check("T5b iteration_metrics J_after_route changed -> DIFFERS", rc == 3 and j["differing"] == [IM])
    # T6 run_manifest
    y = clone(A, "rm_dur")
    edit(y, RM, lambda b: json.dumps(dict(json.loads(b), duration_ms=1, commit="deadbeef", config_path="elsewhere"), indent=2).encode())
    rc, _o, j, _ = cmp(A, y); check("T6a declared keys changed (duration_ms, commit, config_path) -> ignored", rc == 0 and j["differing"] == [])
    y = clone(A, "rm_exit")
    edit(y, RM, lambda b: json.dumps(dict(json.loads(b), exit_reason="aborted"), indent=2).encode())
    rc, _o, j, _ = cmp(A, y); check("T6b run_manifest exit_reason changed -> DIFFERS", rc == 3 and j["differing"] == [RM])
    y = clone(A, "rm_new")
    edit(y, RM, lambda b: json.dumps(dict(json.loads(b), extra_key=1), indent=2).encode())
    rc, _o, j, _ = cmp(A, y); check("T6c run_manifest extra key -> DIFFERS", rc == 3 and j["differing"] == [RM])
    # T7 MAIN_taxonomy_quality.csv row drop
    y = clone(A, "q_drop")
    quality_set(y, "DendrogramPurity", "0.1"); quality_set(y, "SphericalSilhouette", "0.2"); quality_set(y, "TotalDasguptaCost", "3.0E8")
    rc, o7, j, _ = cmp(A, y); check("T7a the three declared rows changed -> ignored (EQUAL)", rc == 0 and j["differing"] == [])
    check("T7a' P6 shows the changed dropped values", "3.0E8" in o7)
    for metric in ("SeparationJ", "WeightedLeafPurity", "NormalisedSackinIndex"):
        y = clone(A, "q_" + metric); quality_set(y, metric, "0.5")
        rc, _o, j, _ = cmp(A, y); check("T7b %s row changed (same file) -> DIFFERS" % metric, rc == 3 and j["differing"] == [C.QUALITY])
    y = clone(A, "q_hdr"); edit(y, C.QUALITY, lambda b: b.replace(b"Metric,Value", b"Metric,value", 1))
    rc, _o, j, _ = cmp(A, y); check("T7c header byte changed -> DIFFERS", rc == 3 and j["differing"] == [C.QUALITY])
    y = clone(A, "q_order")
    edit(y, C.QUALITY, lambda b: (lambda L: "".join([L[0], L[2], L[1]] + L[3:]).encode())(b.decode().splitlines(keepends=True)))
    rc, _o, j, _ = cmp(A, y); check("T7d two kept rows swapped -> DIFFERS (order kept)", rc == 3 and j["differing"] == [C.QUALITY])
    y = clone(A, "q_crlf"); edit(y, C.QUALITY, lambda b: b.replace(b"SeparationJ,", b"SeparationJ ,", 1))
    rc, _o, j, _ = cmp(A, y); check("T7e one inserted byte in a kept row -> DIFFERS", rc == 3 and j["differing"] == [C.QUALITY])
    y = clone(A, "q_eol"); edit(y, C.QUALITY, lambda b: b.replace(b"\n", b"\r\n", 1))
    rc, _o, j, _ = cmp(A, y); check("T7f header line terminator LF->CRLF -> DIFFERS (byte for byte)", rc == 3 and j["differing"] == [C.QUALITY])
    y = clone(A, "q_dropped_extra_row"); edit(y, C.QUALITY, lambda b: b + b"TotalDasguptaCost,1.0\n")
    rc, _o, j, _ = cmp(A, y)
    check("T7g a duplicated declared row is dropped too (EQUAL; every row whose Metric is declared)", rc == 0)
    y = clone(A, "q_missing_row")
    edit(y, C.QUALITY, lambda b: b"".join(l for l in b.splitlines(keepends=True) if not l.startswith(b"SphericalSilhouette,")))
    rc, o, j, _ = cmp(A, y); check("T7h-a (R3) the refusal names the file and the leg B",
                                   "seed_42/validation/MAIN_taxonomy_quality.csv in leg B: declared row(s) ['SphericalSilhouette'] absent" in o, o.strip()[-160:])
    rc_x, o_x, j_x, _ = cmp(y, A); check("T7h-b (R3) the same row absent in leg A only -> refusal naming leg A",
                                         rc_x == 2 and j_x is None and "MAIN_taxonomy_quality.csv in leg A:" in o_x)
    rc_2, o_2, j_2, _ = cmp(A, y, "A", "A2"); check("T7h-c (R3) via the C2 path the refusal names leg A2",
                                                   rc_2 == 2 and "MAIN_taxonomy_quality.csv in leg A2:" in o_2)
    check("T7h a declared row absent -> INSTRUMENT REFUSAL (exit 2, nothing written)",
                                   rc == 2 and j is None and "INSTRUMENT REFUSAL" in o)
    # T8 tuning_ledger.csv column drop
    y = clone(A, "tl_drop")
    for col, v in (("CommitSHA", "0" * 40), ("DendrogramPurity", "0.1"), ("SphericalSilhouette", "0.2"), ("TotalDasguptaCost", "3.0E8")):
        csv_set(y, TL, col, v)
    rc, _o, j, _ = cmp(A, y); check("T8a the four declared columns changed -> ignored (EQUAL)", rc == 0 and j["differing"] == [])
    for col in ("LeafCount", "WeightedLeafPurity", "NormalisedSackinIndex", "ConfigHash", "Top1Accuracy", "BridgeStabilityScore"):
        y = clone(A, "tl_" + col); csv_set(y, TL, col, "7")
        rc, _o, j, _ = cmp(A, y); check("T8b tuning_ledger %s changed (same file) -> DIFFERS" % col, rc == 3 and j["differing"] == [TL])
    y = clone(A, "tl_nocol")
    edit(y, TL, lambda b: b.replace(b"DendrogramPurity", b"DendroPurity", 1))
    rc, o, j, _ = cmp(A, y); check("T8c a declared column absent -> INSTRUMENT REFUSAL naming the file and the leg (R3)",
                                   rc == 2 and j is None and "tuning_ledger.csv in leg B: declared column(s) ['DendrogramPurity']" in o)
    # T9 the file set
    y = clone(A, "fs_extra"); open(os.path.join(y, C.OUT, "seed_42", "stray.txt"), "w").write("x")
    rc, o, j, _ = cmp(A, y); check("T9a an extra file -> FILE-SET DIFFERS (named)", rc == 3 and j["differing"] == [C.FILESET] and "stray.txt" in o)
    y = clone(A, "fs_missing_excl"); os.remove(os.path.join(y, C.OUT, "seed_42", "performance_report.json"))
    rc, _o, j, _ = cmp(A, y); check("T9b an excluded file missing in one leg -> FILE-SET DIFFERS", rc == 3 and j["differing"] == [C.FILESET])
    y = clone(A, "fs_missing_listed"); os.remove(os.path.join(y, C.OUT, "seed_42", "gate_ids.json"))
    rc, _o, j, _ = cmp(A, y)
    check("T9c a listed file missing in one leg -> that file AND FILE-SET DIFFER", rc == 3 and j["differing"] == ["seed_42/gate_ids.json", C.FILESET])
    y = clone(A, "fs_missing_drop"); os.remove(os.path.join(y, C.OUT, TL))
    rc, _o, j, _ = cmp(y, A)
    check("T9d a declared-drop file missing in one leg (X side) -> DIFFERS", rc == 3 and j["differing"] == [TL, C.FILESET])
    x2 = clone(A, "fs_both_x"); os.remove(os.path.join(x2, C.OUT, "seed_42", "gate_ids.json"))
    y2 = clone(A, "fs_both_y"); os.remove(os.path.join(y2, C.OUT, "seed_42", "gate_ids.json"))
    rc, _o, j, _ = cmp(x2, y2); check("T9e a listed file missing in BOTH legs -> INSTRUMENT REFUSAL", rc == 2 and j is None)
    # T10 the pool tables
    y = clone(A, "pool_row"); db_exec(y, "UPDATE reserved_pool SET domain = 'World' WHERE question_id = (SELECT MIN(question_id) FROM reserved_pool)")
    rc, _o, j, _ = cmp(A, y); check("T10a reserved_pool one row changed -> DIFFERS", rc == 3 and j["differing"] == ["reserved_pool"])
    y = clone(A, "pool_del"); db_exec(y, "DELETE FROM reserved_pool WHERE question_id = (SELECT MAX(question_id) FROM reserved_pool)")
    rc, _o, j, _ = cmp(A, y); check("T10b reserved_pool one row deleted -> DIFFERS", rc == 3 and j["differing"] == ["reserved_pool"])
    y = clone(A, "meta_ts"); db_exec(y, "UPDATE reserved_pool_meta SET created_at = 1")
    rc, _o, j, _ = cmp(A, y); check("T10c reserved_pool_meta created_at changed -> ignored", rc == 0 and j["differing"] == [])
    y = clone(A, "meta_cnt"); db_exec(y, "UPDATE reserved_pool_meta SET question_count = 601")
    rc, _o, j, _ = cmp(A, y); check("T10d reserved_pool_meta question_count changed -> DIFFERS", rc == 3 and j["differing"] == ["reserved_pool_meta"])
    y = clone(A, "pool_nodb"); os.remove(os.path.join(y, "ag_news_smoke_cache_v1.db"))
    rc, _o, j, _ = cmp(A, y); check("T10e no AG DB in a leg -> INSTRUMENT REFUSAL", rc == 2 and j is None)
    # T11 labels, write-once
    rc, _o, j, _ = cmp(A, A_dup, "B", "A"); check("T11a pair (B, A) refused", rc == 2 and j is None)
    rc, _o, j, _ = cmp(A, A_dup, "A", "A3"); check("T11b pair (A, A3) refused", rc == 2 and j is None)
    s = stage(); rc1, _ = run([A, A_dup, s, "A", "B"]); rc2, o2 = run([A, A_dup, s, "A", "B"])
    check("T11c second run into the same stage refused (write-once)", rc1 == 0 and rc2 == 2 and "exists" in o2)
    rc, o, j, _ = cmp(A, A_dup, "A", "B", misses=[os.path.join(RB, "d9_misses_A.txt"), os.path.join(WORK, "nope.txt")])
    check("T11d V7 with a missing misses file prints VOID", "NOT EQUAL OR MISSING (VOID)" in o)

    # T12 the verdict mapping, every branch executed
    ya = clone(A, "v_gate"); edit(ya, "seed_42/gate_ids.json", lambda b: b + b" ")
    yp = clone(A, "v_prop"); edit(yp, "seed_42/diagnostics/proposals.csv", lambda b: b + b" ")
    yb = clone(A, "v_both"); edit(yb, "seed_42/gate_ids.json", lambda b: b + b" "); edit(yb, "seed_42/diagnostics/proposals.csv", lambda b: b + b" ")

    def verdict(yb_, ya2_):
        _r1, _o1, _j1, s1 = cmp(A, yb_, "A", "B")
        _r2, _o2, _j2, s2 = cmp(A, ya2_, "A", "A2")
        s3 = stage()
        return run(["--verdict", os.path.join(s1, "d9b_compare.json"), os.path.join(s2, "d9b_compare.json"), os.path.join(s3, "v.txt")])
    rc, o = verdict(A_dup, A_dup); check("T12a S_AB = S_AA = empty -> DISCHARGED (conditional on V1-V11), exit 0", rc == 0 and "D9 DISCHARGED" in o and "NOT checked" in o)
    rc, o = verdict(ya, A_dup); check("T12b S_AB = {gate}, S_AA empty -> THE CHANGE READ (F1), exit 3", rc == 3 and "F1 fires" in o and "reads THE CHANGE" in o)
    rc, o = verdict(A_dup, ya); check("T12c S_AB empty, S_AA = {gate} -> UNDETERMINED (F2), exit 6", rc == 6 and "D9 UNDETERMINED" in o and "S_AA only" in o)
    rc, o = verdict(ya, yb); check("T12d S_AB = {gate} subset of S_AA = {gate, prop} -> UNDETERMINED, exit 6", rc == 6 and "NON-DETERMINISM (F2)" in o)
    rc, o = verdict(ya, ya); check("T12e S_AB = S_AA = {gate} -> UNDETERMINED, exit 6", rc == 6)
    print("---- T12f (the ambiguous cell) ----")
    rc, o = verdict(yb, ya); print(o + "----")
    check("T12f (R1) S_AB = {gate, prop}, S_AA = {gate} -> THE CHANGE READ, exit 3, F1 on proposals, F2 ALSO FIRED on gate, [LIMIT]",
          rc == 3 and "F1 fires on ['seed_42/diagnostics/proposals.csv']" in o
          and "F2 ALSO FIRED on ['seed_42/gate_ids.json']" in o and "[LIMIT] one A/A2 pair" in o and "ruling A1" in o)
    rc, o = verdict(ya, yp)
    check("T12g (R1) S_AB = {gate}, S_AA = {prop} -> exit 3, F1 on gate_ids, F2 ALSO FIRED on proposals",
          rc == 3 and "F1 fires on ['seed_42/gate_ids.json']" in o and "F2 ALSO FIRED on ['seed_42/diagnostics/proposals.csv']" in o
          and "[LIMIT]" in o)
    check("T12g-a (R1) the F2 mapping line carries the ruling-A1 annotation",
          "(ruling A1: the UNDETERMINED consequence applies only when S_AB is a subset of S_AA)" in o)
    rc, o = verdict(ya, A_dup); check("T12b-a (R1) F1 with S_AA empty prints no F2 ALSO FIRED and no [LIMIT]",
                                      rc == 3 and "F2 ALSO FIRED" not in o and "[LIMIT]" not in o)
    subsets = {"{}": A_dup, "{gate}": ya, "{prop}": yp, "{gate,prop}": yb}
    grid = {}
    for kab, rab in subsets.items():
        for kaa, raa in subsets.items():
            grid[(kab, kaa)] = verdict(rab, raa)[0]
    want = {}
    for kab in subsets:
        for kaa in subsets:
            sab = set(kab.strip("{}").split(",")) - {""}
            saa = set(kaa.strip("{}").split(",")) - {""}
            want[(kab, kaa)] = 0 if not sab and not saa else 3 if sab - saa else 6
    check("T12j (R1) all 16 (S_AB, S_AA) cells over {gate, prop}: no branch returns 4; each cell exits as ruled (0 / 3 / 6)",
          4 not in grid.values() and grid == want, str({k: v for k, v in grid.items() if want[k] != v}))
    src_c = open(os.path.join(HERE, "d9b_compare.py"), encoding="utf-8").read()
    check("T12k (R1) the source holds no exit-4 verdict branch and no NOT MAPPED text outside the docstring",
          "rc, v = 4" not in src_c and "NOT MAPPED" not in src_c.split('"""', 2)[2])
    _r1, _o1, _j1, s1 = cmp(A, A_dup, "A", "B"); _r2, _o2, _j2, s2 = cmp(ya, A_dup, "A", "A2")
    rc, o = run(["--verdict", os.path.join(s1, "d9b_compare.json"), os.path.join(s2, "d9b_compare.json"), os.path.join(stage(), "v.txt")])
    check("T12h leg A not the same in the two readouts -> INSTRUMENT REFUSAL", rc == 2)
    rc, o = run(["--verdict", os.path.join(s2, "d9b_compare.json"), os.path.join(s1, "d9b_compare.json"), os.path.join(stage(), "v.txt")])
    check("T12i readouts swapped (C2 given as C1') -> INSTRUMENT REFUSAL", rc == 2)

    # T13 d9b_aux: V10 and V11
    leg = os.path.join(WORK, "leg_fake")
    cdir = os.path.join(leg, "build", "classes", "kotlin", "main", "taxonomy", "dataset")
    os.makedirs(cdir)
    open(os.path.join(cdir, "MMLUDatasetFetcher.class"), "wb").write(b"\x00LIVECODEBENCH fetchLiveCodeBench lcbWorkDirGuard\x01")
    open(os.path.join(cdir, "LcbWorkDirGuardState.class"), "wb").write(b"LcbWorkDirGuardState LIVECODEBENCH")
    open(os.path.join(cdir, "Other.class"), "wb").write(b"nothing")
    st = os.path.join(WORK, "v10st")
    for d in ("classlists", "a2"):
        os.makedirs(os.path.join(st, d))
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rcs = [X.classlists(L, leg, st) for L in ("A", "B", "A2")]
        rc_again = X.classlists("A", leg, st)
    check("T13a classlists written for A, B, A2; a second write refused", rcs == [0, 0, 0] and rc_again == 2)
    got = open(os.path.join(st, "classlists", "legB_LIVECODEBENCH.txt")).read().splitlines()
    check("T13b list content = grep -rlaF names", got == ["build/classes/kotlin/main/taxonomy/dataset/LcbWorkDirGuardState.class",
                                                       "build/classes/kotlin/main/taxonomy/dataset/MMLUDatasetFetcher.class"], str(got))
    v3 = "[V3 %s] 3 class files; files containing {'LIVECODEBENCH': 2, 'fetchLiveCodeBench': 1, 'lcbWorkDirGuard': 1, 'LcbWorkDirGuardState': 1}\n"
    open(os.path.join(st, "d9_disc.txt"), "w").write(v3 % "A" + v3 % "B")
    open(os.path.join(st, "a2", "d9_disc.txt"), "w").write(v3 % "A")
    lists = sorted(os.listdir(os.path.join(st, "classlists")))
    open(os.path.join(st, "SHA256SUMS"), "w").write("".join("%s  classlists/%s\n" % (X.sha(os.path.join(st, "classlists", f)), f) for f in lists))
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = X.v10(st)
    check("T13c V10 MET when the lists, the hashes and the V3 counts agree", rc == 0, buf.getvalue()[-60:])
    open(os.path.join(st, "a2", "d9_disc.txt"), "w").write((v3 % "A").replace("'fetchLiveCodeBench': 1", "'fetchLiveCodeBench': 0"))
    with contextlib.redirect_stdout(io.StringIO()):
        rc = X.v10(st)
    check("T13d V10 NOT MET when A2's V3 count differs from its list", rc == 1)
    open(os.path.join(st, "a2", "d9_disc.txt"), "w").write(v3 % "A")
    open(os.path.join(st, "SHA256SUMS"), "w").write("")
    with contextlib.redirect_stdout(io.StringIO()):
        rc = X.v10(st)
    check("T13e V10 NOT MET when the lists are not hashed in SHA256SUMS", rc == 1)
    arm = os.path.join(WORK, "arm.toml")
    open(arm, "wb").write(subprocess.run(["git", "-C", MAIN, "cat-file", "blob", "efd82bdacc06144439280d3b76923d38527bd7ae"],
                                         capture_output=True, check=True).stdout)
    probe = os.path.join(SP, "d9", "probe_lcb.toml")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = X.v11(arm, probe)
    print(buf.getvalue(), end="")
    check("T13f V11 MET on the arm blob efd82bda vs the D9 probe TOML (CR-stripped)", rc == 0)
    arm_crlf = os.path.join(WORK, "arm_crlf.toml")
    open(arm_crlf, "wb").write(open(arm, "rb").read().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
    with contextlib.redirect_stdout(io.StringIO()):
        rc = X.v11(arm_crlf, probe)
    check("T13g V11 MET with the arm in CRLF (CRs stripped)", rc == 0)
    p3 = os.path.join(WORK, "probe3.toml")
    open(p3, "wb").write(open(probe, "rb").read().replace(b"seed", b"sead", 1))
    with contextlib.redirect_stdout(io.StringIO()):
        rc = X.v11(arm, p3)
    check("T13h V11 NOT MET with a third differing line", rc == 1)

    # T15 (R2) P6 relative TDC against leg A; P6 scoring on all three pairs and both sources
    def vals(tdc, dp=0.5, ss=0.1, ltdc=None, ldp=None, lss=None):
        return {"quality:TotalDasguptaCost": tdc, "quality:DendrogramPurity": repr(dp), "quality:SphericalSilhouette": repr(ss),
                "ledger:TotalDasguptaCost": ltdc if ltdc is not None else tdc,
                "ledger:DendrogramPurity": repr(ldp if ldp is not None else dp),
                "ledger:SphericalSilhouette": repr(lss if lss is not None else ss)}
    va, vb, v2 = vals("1.0E8"), vals("2.0E8"), vals("2.5E8")
    ln = [l for l in C.p6_lines("B/A2", "B", "A2", vb, v2, va) if "quality" in l and "TotalDasguptaCost" in l][0]
    check("T15a (R2) B/A2 relative TDC = |B - A2| / A = 50% 'of A' (not 25% of B)", "50.000000% of A" in ln, ln)
    va, vb, v2 = vals("2.2377813825989264E8"), vals("2.2376868581711334E8"), vals("2.2409421312346172E8")
    lines, st = C.p6_score(va, vb, v2)
    check("T15b P6 HELD on the record's A/B/A' values (22 clause-instances)", st == "HELD" and "22 hold" in lines[-1], lines[-1])
    lines, st = C.p6_score(va, vals("2.2377813825989264E8"), v2)
    check("T15c P6 FAILED when TDC is EQUAL on A/B (the DIFFERS clause), named for both sources",
          st == "FAILED" and "TDC DIFFERS A/B quality" in lines[-1] and "TDC DIFFERS A/B ledger" in lines[-1], lines[-1])
    lines, st = C.p6_score(va, vb, vals("2.2409421312346172E8", ltdc="2.26E8"))
    check("T15d P6 FAILED when only the LEDGER source breaches 0.6% (A/A2 and B/A2); quality not named",
          st == "FAILED" and "A/A2 ledger" in lines[-1] and "B/A2 ledger" in lines[-1]
          and "quality" not in lines[-1].split("fail", 1)[1], lines[-1])
    lines, st = C.p6_score(va, vb, vals("2.2409421312346172E8", dp=0.5 + 2e-13))
    check("T15e P6 FAILED on |DP diff| 2e-13 > 1e-13 (A/A2 and B/A2, both sources)",
          st == "FAILED" and lines[-1].count("|DP diff|") == 4, lines[-1])
    lines, st = C.p6_score(va, vals("2.2376868581711334E8", ss=0.1 + 3e-15), v2)
    check("T15f P6 FAILED on |SS diff| > 1e-15 (A/B and B/A2)",
          st == "FAILED" and "|SS diff| <= 1e-15 A/B" in lines[-1] and "|SS diff| <= 1e-15 B/A2" in lines[-1], lines[-1])
    lines, st = C.p6_score(va, vb, vals("2.2409421312346172E8", ltdc="NaN-ish"))
    check("T15g P6 UNDETERMINED (never HELD) when a value is not numeric in both legs",
          st == "UNDETERMINED" and "0 fail" in lines[-1] and "undetermined)" in lines[-1], lines[-1])
    lines, st = C.p6_score(va, vals("2.2377813825989264E8"), vals("2.2409421312346172E8", ltdc="?"))
    check("T15h P6 FAILED beats UNDETERMINED (a failing clause with an unscoreable one)", st == "FAILED")
    b_a2 = [l for l in C.p6_score(vals("1.0E8"), vals("2.0E8"), vals("2.004E8"))[0]
            if " B/A2 " in l and "rel TDC" in l and "quality" in l][0]
    check("T15i (R2) the scored B/A2 relative TDC uses A: 0.4E6 / 1.0E8 = 0.4% HOLDS", "0.400000% of A" in b_a2 and "HOLDS" in b_a2, b_a2)

    # T16 (R4) V10 over the .class entries; a non-.class hit disclosed, not compared
    st4 = os.path.join(WORK, "v10r4")
    for d in ("classlists", "a2"):
        os.makedirs(os.path.join(st4, d))

    def write_lists(extra_meta, fetch_class_hits):
        for L in ("A", "B", "A2"):
            for i in X.IDS + ("all",):
                p = os.path.join(st4, "classlists", "leg%s_%s.txt" % (L, i))
                if i == "all":
                    body = ["build/classes/kotlin/main/a/One.class"]
                elif i == "fetchLiveCodeBench":
                    body = ["build/classes/kotlin/main/a/F%d.class" % k for k in range(fetch_class_hits)]
                    if extra_meta:
                        body.append("build/classes/kotlin/main/META-INF/taxoadapt.kotlin_module")
                else:
                    body = []
                open(p, "w", newline="\n").write("".join(x + "\n" for x in body))
        v3r = ("[V3 %s] 1 class files; files containing {'LIVECODEBENCH': 0, 'fetchLiveCodeBench': 1, 'lcbWorkDirGuard': 0,"
               " 'LcbWorkDirGuardState': 0}\n")
        open(os.path.join(st4, "d9_disc.txt"), "w").write(v3r % "A" + v3r % "B")
        open(os.path.join(st4, "a2", "d9_disc.txt"), "w").write(v3r % "A")
        fs = sorted(os.listdir(os.path.join(st4, "classlists")))
        open(os.path.join(st4, "SHA256SUMS"), "w").write(
            "".join("%s  classlists/%s\n" % (X.sha(os.path.join(st4, "classlists", f)), f) for f in fs))
    write_lists(True, 1)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = X.v10(st4)
    o = buf.getvalue()
    check("T16a (R4) one .class hit + one META-INF hit vs V3 = 1 -> V10 MET, the META-INF hit disclosed",
          rc == 0 and "list .class 1 (non-.class hits 1, DISCLOSED, not compared: "
          "['build/classes/kotlin/main/META-INF/taxoadapt.kotlin_module'])" in o, o[-300:])
    write_lists(True, 2)
    with contextlib.redirect_stdout(io.StringIO()):
        rc = X.v10(st4)
    check("T16b (R4) a .class mismatch (2 vs V3 1) -> V10 NOT MET", rc == 1)
    write_lists(True, 0)
    with contextlib.redirect_stdout(io.StringIO()):
        rc = X.v10(st4)
    check("T16c (R4) only the META-INF hit (0 .class) vs V3 1 -> V10 NOT MET", rc == 1)

    # T17 (R5, READY d984724 B1) V10 binds each list to ITS OWN PATH in SHA256SUMS
    st5 = os.path.join(WORK, "v10r5")
    for d in ("classlists", "a2"):
        os.makedirs(os.path.join(st5, d))
    for L in ("A", "B", "A2"):
        for i in X.IDS + ("all",):
            body = []
            if i == "all":
                body = ["build/classes/kotlin/main/a/One.class"] + (["build/classes/kotlin/main/a/Two.class"] if L == "B" else [])
            elif L == "B":
                body = ["build/classes/kotlin/main/a/%s.class" % i]
            open(os.path.join(st5, "classlists", "leg%s_%s.txt" % (L, i)), "w", newline="\n").write("".join(x + "\n" for x in body))
    v3a = "[V3 A] 1 class files; files containing {'LIVECODEBENCH': 0, 'fetchLiveCodeBench': 0, 'lcbWorkDirGuard': 0, 'LcbWorkDirGuardState': 0}\n"
    v3b = "[V3 B] 2 class files; files containing {'LIVECODEBENCH': 1, 'fetchLiveCodeBench': 1, 'lcbWorkDirGuard': 1, 'LcbWorkDirGuardState': 1}\n"
    open(os.path.join(st5, "d9_disc.txt"), "w").write(v3a + v3b)
    open(os.path.join(st5, "a2", "d9_disc.txt"), "w").write(v3a)
    lists = sorted(os.listdir(os.path.join(st5, "classlists")))
    shas = {f: X.sha(os.path.join(st5, "classlists", f)) for f in lists}

    def sums(lines, enc="ascii"):
        open(os.path.join(st5, "SHA256SUMS"), "w", encoding=enc, newline="\n").write("".join(l + "\n" for l in lines))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = X.v10(st5)
        return rc, buf.getvalue()
    absst = os.path.abspath(st5)
    ps_form = ["%s  %s" % (shas[f].upper() if k % 2 else shas[f], os.path.join(absst, "classlists", f)) for k, f in enumerate(lists)]
    rc, o = sums(ps_form)
    check("T17a (R5) full set in S10's Get-FileHash form (hex, two spaces, absolute backslash path) -> V10 MET", rc == 0, o[-120:])
    rc, o = sums(["%s  ./classlists/%s" % (shas[f], f) for f in lists])
    check("T17b (R5) full set in sha256sum form './classlists/...' (the reviewer's S10) -> V10 MET", rc == 0)
    rc, o = sums(["%s *./classlists/%s" % (shas[f], f) for f in lists])
    check("T17c (R5) full set in sha256sum binary form '*./classlists/...' -> V10 MET", rc == 0)
    rc, o = sums(["%s  %s" % (shas[f], os.path.join(absst, "classlists", f).upper()) for f in lists], enc="utf-16")
    check("T17d (R5) full set, upper-case path, UTF-16 SHA256SUMS (Out-File's encoding) -> V10 MET", rc == 0, o[-120:])
    four = ["legA_LIVECODEBENCH.txt", "legA_all.txt", "legB_LIVECODEBENCH.txt", "legB_all.txt"]
    rc, o = sums(["%s  ./classlists/%s" % (shas[f], f) for f in four])
    check("T17e (R5) only 4 of 15 lists named (the B1 case; A/A2 empty lists share one sha256) -> V10 NOT MET, 11 ABSENT",
          rc == 1 and o.count(": ABSENT -> FAIL") == 11, str(o.count(": ABSENT -> FAIL")))
    bad = ["%s  ./classlists/%s" % ("0" * 64 if f == "legB_all.txt" else shas[f], f) for f in lists]
    rc, o = sums(bad)
    check("T17f (R5) the right path with a wrong sha256 -> V10 NOT MET (WRONG sha256)", rc == 1 and "WRONG sha256 0000000000000000" in o)
    swap = {"legB_LIVECODEBENCH.txt": "legB_all.txt", "legB_all.txt": "legB_LIVECODEBENCH.txt"}
    rc, o = sums(["%s  ./classlists/%s" % (shas[swap.get(f, f)], f) for f in lists])
    check("T17g (R5) two lists' sha256 swapped between their paths -> V10 NOT MET", rc == 1 and o.count("WRONG sha256") == 2)
    rc, o = sums(["%s  ./classlists/%s" % (shas[f], f) for f in lists] + ["%s  ./classlists/legA_all.txt" % ("1" * 64)])
    check("T17h (R5) a list's path listed twice with different sha256 -> V10 NOT MET", rc == 1 and "LISTED TWICE" in o)
    rc, o = sums(["%s  ./classlists/%s" % (shas[f], f) for f in lists if f != "legA2_all.txt"]
                 + ["%s  ./a2/classlists/legA2_all.txt" % shas["legA2_all.txt"]])
    check("T17i (R5) a list hashed under ANOTHER path (a2/classlists/...) does not count -> V10 NOT MET", rc == 1)
    rv = os.path.join(SP, "rev_d9b", "harness", "v10st")
    if os.path.isdir(rv):
        rvc = os.path.join(WORK, "rev_v10st_copy")
        shutil.copytree(rv, rvc)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = X.v10(rvc)
        check("T17j (R5) the reviewer's B1 reproduction (copy of rev_d9b\\harness\\v10st, 4 of 15 named) -> V10 NOT MET",
              rc == 1 and buf.getvalue().count(": ABSENT -> FAIL") == 11, buf.getvalue()[-160:])
    else:
        check("T17j (R5) the reviewer's v10st is present to reproduce", False, rv)

    # T18 (D3) --verdict refuses a missing / corrupt / malformed readout with exit 2, no traceback, no output file
    _r1, _o1, _j1, s1 = cmp(A, A_dup, "A", "B")
    _r2, _o2, _j2, s2 = cmp(A, A_dup, "A", "A2")
    good_ab, good_aa = os.path.join(s1, "d9b_compare.json"), os.path.join(s2, "d9b_compare.json")
    bad_dir = os.path.join(WORK, "bad_json")
    os.makedirs(bad_dir)
    cases = {"missing": None, "truncated": open(good_ab, encoding="utf-8").read()[:200], "list": "[]", "empty": "",
             "no digest": json.dumps({k: v for k, v in json.load(open(good_ab, encoding="utf-8")).items() if k != "digest"})}
    for name, body in cases.items():
        pth = os.path.join(bad_dir, name.replace(" ", "_") + ".json")
        if body is not None:
            open(pth, "w", encoding="utf-8").write(body)
        outp = os.path.join(stage(), "v.txt")
        try:
            rc, o = run(["--verdict", pth, good_aa, outp])
            tb = False
        except Exception as e:  # a traceback escaping main() is the defect D3
            rc, o, tb = None, repr(e), True
        check("T18 (D3) --verdict with a %s C1' readout -> INSTRUMENT REFUSAL exit 2, no traceback, no output" % name,
              not tb and rc == 2 and "INSTRUMENT REFUSAL" in o and not os.path.exists(outp), o.strip()[-140:])
    rc, o = run(["--verdict", good_ab, os.path.join(bad_dir, "missing.json"), os.path.join(stage(), "v.txt")])
    check("T18f (D3) a missing C2 readout -> exit 2", rc == 2 and "cannot be read" in o)

    # T19 (D2, READY d984724 surviving mutants M1 / M6 / M9) pin the drop lists and kill over-drops
    check("T19a the drop and object lists equal the registration's literals (L19674-L19678)",
          C.CSV_DROP == {"seed_42/diagnostics/iteration_metrics.csv": ["wall_ms"],
                         "tuning_ledger.csv": ["CommitSHA", "DendrogramPurity", "SphericalSilhouette", "TotalDasguptaCost"]}
          and C.ROW_DROP == {"seed_42/validation/MAIN_taxonomy_quality.csv": ("Metric", ["DendrogramPurity", "SphericalSilhouette", "TotalDasguptaCost"])}
          and C.JSON_DROP == {"seed_42/diagnostics/run_manifest.json": ["commit", "branch", "dirty", "dirty_src", "dirty_src_files",
                                                                         "dirty_other", "dirty_other_files", "dirty_files", "started_at_millis",
                                                                         "finished_at_millis", "duration_ms", "config_path", "proposal_memo_digest_ms"]}
          and C.POOL_DROP == {"reserved_pool_meta": ["created_at"]}
          and C.EXCLUDED == {"seed_42/headless_run.log", "seed_42/diagnostics/headless_run.log", "seed_42/performance_report.json"}
          and C.BYTE == ["seed_42/dag_snapshots.jsonl", "seed_42/gate_ids.json", "seed_42/fixed_point_certificate.txt"]
          + ["seed_42/validation/" + f for f in ("MAIN_bridge_quality.csv", "MAIN_centroid_routing_results.csv", "MAIN_graph_validity.csv",
                                                 "MAIN_heldout_leaf_support.csv", "MAIN_migration_flow_matrix.csv", "MAIN_routing_calibration.csv",
                                                 "MAIN_routing_diagnostics.txt", "MAIN_trickle_validation_results.csv", "bridge_nodes.csv",
                                                 "bridge_residuals.csv")]
          + ["seed_42/diagnostics/" + f for f in ("dag_snapshots.jsonl", "proposals.csv", "rank_history.csv", "config.toml")])

    # the registration's literal lists (NOT the module's, so an over-drop in the module cannot shrink the loops)
    REG_LEDGER_DROP = ["CommitSHA", "DendrogramPurity", "SphericalSilhouette", "TotalDasguptaCost"]
    REG_IM_DROP = ["wall_ms"]
    REG_MANIFEST_DROP = ["commit", "branch", "dirty", "dirty_src", "dirty_src_files", "dirty_other", "dirty_other_files",
                         "dirty_files", "started_at_millis", "finished_at_millis", "duration_ms", "config_path",
                         "proposal_memo_digest_ms"]

    def kept_columns(rel, dropped):
        hdr = next(csv.reader(io.StringIO(open(os.path.join(A, C.OUT, rel), encoding="utf-8").read(), newline="")))
        return [c for c in hdr if c not in dropped]

    def mutate_each_column(rel, dropped, row):
        missed = []
        cols = kept_columns(rel, dropped)
        for k, col in enumerate(cols):
            y = clone(A, "col_%s_%d" % (os.path.basename(rel).split(".")[0], k))
            p = os.path.join(y, C.OUT, rel)
            rows = list(csv.reader(io.StringIO(open(p, encoding="utf-8").read(), newline="")))
            i = rows[0].index(col)
            rows[row][i] = rows[row][i] + "9"
            raw = open(p, "rb").read().decode("utf-8")
            o_ = io.StringIO()
            csv.writer(o_, lineterminator="\r\n" if "\r\n" in raw else "\n").writerows(rows)
            open(p, "wb").write(o_.getvalue().encode("utf-8"))
            rc, _o, j, s_ = cmp(A, y)
            if not (rc == 3 and j["differing"] == [rel]):
                missed.append(col)
            shutil.rmtree(y)
            shutil.rmtree(s_)
        return cols, missed
    cols, missed = mutate_each_column(C.LEDGER, REG_LEDGER_DROP, -1)
    check("T19b EVERY kept tuning_ledger column (%d) mutated -> DIFFERS (kills M1, +RoutingECE over-drop)" % len(cols),
          len(cols) > 10 and not missed, str(missed))
    IMr = "seed_42/diagnostics/iteration_metrics.csv"
    cols, missed = mutate_each_column(IMr, REG_IM_DROP, 1)
    check("T19c EVERY kept iteration_metrics column (%d) mutated -> DIFFERS (kills M6, +mass over-drop)" % len(cols),
          len(cols) > 5 and not missed, str(missed))
    RMr = "seed_42/diagnostics/run_manifest.json"
    man = json.load(open(os.path.join(A, C.OUT, RMr), encoding="utf-8"))
    kept = [k for k in man if k not in REG_MANIFEST_DROP]
    missed = []
    for k, key in enumerate(kept):
        y = clone(A, "man_%d" % k)
        d = dict(man)
        d[key] = "MUTATED" if d[key] != "MUTATED" else "MUTATED2"
        edit(y, RMr, lambda b, d=d: json.dumps(d, indent=2).encode())
        rc, _o, j, s_ = cmp(A, y)
        if not (rc == 3 and j["differing"] == [RMr]):
            missed.append(key)
        shutil.rmtree(y)
        shutil.rmtree(s_)
    check("T19d EVERY kept run_manifest key (%d) mutated -> DIFFERS" % len(kept), len(kept) >= 3 and not missed, str(missed))

    def rebuild_pool(root, table, dup=False, reverse=False, dup_index=0):
        """the table re-created WITHOUT its primary key (a synthetic schema: the real reserved_pool has PRIMARY KEY
        (pool_id, question_id), so a duplicate row cannot occur in a real leg); rows re-inserted, optionally reversed and
        with the first row duplicated"""
        con = sqlite3.connect(os.path.join(root, "ag_news_smoke_cache_v1.db"))
        cols = [r[1] for r in con.execute("PRAGMA table_info(%s)" % table)]
        rows = con.execute("SELECT %s FROM %s" % (", ".join(cols), table)).fetchall()
        con.execute("DROP TABLE %s" % table)
        con.execute("CREATE TABLE %s (%s)" % (table, ", ".join(cols)))
        rows = rows[::-1] if reverse else rows
        rows = rows + rows[dup_index:dup_index + 1] if dup else rows
        con.executemany("INSERT INTO %s VALUES (%s)" % (table, ", ".join("?" * len(cols))), rows)
        con.commit()
        con.close()
    y = clone(A, "pool_rev"); rebuild_pool(y, "reserved_pool", reverse=True)
    rc, _o, j, _ = cmp(A, y)
    check("T19e reserved_pool rows in reversed physical order -> EQUAL (d9_compare's semantics kept: ORDER BY every kept column,"
          " i.e. a multiset compare)", rc == 0 and j["differing"] == [])
    y = clone(A, "pool_dup"); rebuild_pool(y, "reserved_pool", dup=True)
    rc, _o, j, _ = cmp(A, y)
    check("T19f reserved_pool with one row duplicated (PK removed on the copy) -> DIFFERS (kills M9, set compare)",
          rc == 3 and j["differing"] == ["reserved_pool"])
    y = clone(A, "meta_dup"); rebuild_pool(y, "reserved_pool_meta", dup=True)
    rc, _o, j, _ = cmp(A, y)
    check("T19g reserved_pool_meta with its row duplicated (PK removed on the copy) -> DIFFERS",
          rc == 3 and j["differing"] == ["reserved_pool_meta"])
    x = clone(A, "pool_dupx"); rebuild_pool(x, "reserved_pool", dup=True, dup_index=0)
    y = clone(A, "pool_dupy"); rebuild_pool(y, "reserved_pool", dup=True, dup_index=1)
    rc, _o, j, _ = cmp(x, y)
    check("T19h same row count and same row SET, different multiplicities ({r0,r0,r1,...} vs {r0,r1,r1,...}) -> DIFFERS"
          " (kills M9 even with the row count kept in the readout)", rc == 3 and j["differing"] == ["reserved_pool"])

    # T14 d9b_prep: three-leg logic, with git and the INPUT BASELINE monkeypatched onto fake inputs (no main DB is read)
    P = importlib.import_module("d9b_prep")
    fmain = os.path.join(WORK, "fmain")
    os.makedirs(fmain)
    shutil.copyfile(os.path.join(RB, "pool_copy_A", "ag.db"), os.path.join(fmain, "ag_news_smoke_cache_v1.db"))
    open(os.path.join(fmain, "ag_news_smoke_cache_v1.db-wal"), "wb").close()
    open(os.path.join(fmain, "embeddings_cache.db"), "wb").write(b"fake embeddings")
    P.AG_BASE = {n: (os.path.getsize(os.path.join(fmain, n)), P.sha(os.path.join(fmain, n)))
                 for n in ("ag_news_smoke_cache_v1.db", "ag_news_smoke_cache_v1.db-wal")}
    legs = {}
    for L in ("A", "B", "A2"):
        legs[L] = os.path.join(WORK, "fleg" + L)
        os.makedirs(legs[L])
        open(os.path.join(legs[L], ".git"), "w").write("gitdir: x")
    head = {legs["A"]: P.A_SHA, legs["B"]: P.B_SHA, legs["A2"]: P.A_SHA}

    def fake_git(root, *a):
        if a[0] == "diff":
            return "\n".join(P.FOUR) if a[3] == P.B_SHA else ""
        if a[:2] == ("rev-parse", "HEAD"):
            return head[root]
        if a[0] == "rev-parse":
            c, f = a[1].split(":", 1)
            return P.TOML_BLOB if f == P.TOML else P.B_BLOBS[f] + "0" * 32
        if a[0] == "status":
            return ""
        raise AssertionError(a)
    P.git = fake_git
    fst = os.path.join(WORK, "fstage")
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            P.main(fmain, legs["A"], legs["B"], legs["A2"], fst)
        rc = 0
    except SystemExit as e:
        rc = e.code
    o = buf.getvalue()
    print(o, end="")
    same = rc == 0 and all(P.sha(os.path.join(legs[L], n)) == P.sha(os.path.join(fst, n)) for L in legs for n in ("ag_news_smoke_cache_v1.db", "embeddings_cache.db"))
    check("T14a d9b_prep copies byte-identical inputs into A, B, A2 and creates a2, aa2, classlists",
          rc == 0 and "[V2] PASS: all three legs" in o and same and all(os.path.isdir(os.path.join(fst, d)) for d in ("a2", "aa2", "classlists"))
          and os.path.isfile(os.path.join(fst, "d9b_prep.txt")), o[-200:])
    check("T14b [LEG A2] line printed", "[LEG A2]" in o)
    if os.path.exists(fst):
        shutil.rmtree(fst)
    for L in legs:
        for n in ("ag_news_smoke_cache_v1.db", "embeddings_cache.db"):
            if os.path.exists(os.path.join(legs[L], n)):
                os.remove(os.path.join(legs[L], n))
    open(os.path.join(legs["A2"], "ratings_d9_A.db"), "wb").close()
    P.LOG.clear()
    try:
        with contextlib.redirect_stdout(io.StringIO()) as b2:
            P.main(fmain, legs["A"], legs["B"], legs["A2"], fst)
        rc = 0
    except SystemExit as e:
        rc = e.code
    check("T14c d9b_prep refuses an A2 root holding ratings_d9_A.db (not fresh)", rc == 1 and not os.path.exists(fst))
    os.remove(os.path.join(legs["A2"], "ratings_d9_A.db"))
    head[legs["A2"]] = P.B_SHA
    P.LOG.clear()
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            P.main(fmain, legs["A"], legs["B"], legs["A2"], fst)
        rc = 0
    except SystemExit as e:
        rc = e.code
    check("T14d d9b_prep refuses an A2 worktree not at a62c7e0", rc == 1 and not os.path.exists(fst))

    n_ok = sum(ok for _n, ok in RESULTS)
    print("\n%d of %d cases as expected; %d mismatches" % (n_ok, len(RESULTS), len(RESULTS) - n_ok))
    return 0 if n_ok == len(RESULTS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
