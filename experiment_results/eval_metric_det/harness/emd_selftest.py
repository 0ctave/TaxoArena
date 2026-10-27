"""Selftest of the EVAL-METRIC-DETERMINISM harness (emd_common, emd_compare, emd_leg_check, emd_prep, emd_legrun.cmd).
Zero calls. Fixtures are built BY FILE COPY from the D9b evidence archive (read-only):
  Z:\\FAC\\TUBerlin\\THESIS\\TaxoArena_data\\evidence_2026-09-25\\d9b\\run_d9b_1  (evidence_A / _B / _A2 outputDirs and
  transcripts; the checkpointed pool copies pool_copy_A, pool_copy_B, aa2\\pool_copy_A2; the archived d9b_compare.json of
  C1' (A, B) and C2 (A, A2)).
Every mutation is made on a copy under the work dir (default %TEMP%\\emd_selftest_work, recreated). No main DB is opened;
emd_prep is exercised with git monkeypatched and fake inputs; emd_legrun.cmd with a stub gradlew.bat.

usage: python emd_selftest.py --selftest [--work <dir>]      exit 0 iff every case reads as expected
The harness modules are imported from EMD_HARNESS_DIR when set (the mutant runner), else from this file's directory.
"""
import contextlib, csv, importlib, io, json, os, re, shutil, sqlite3, subprocess, sys, tempfile

HDIR = os.environ.get("EMD_HARNESS_DIR") or os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HDIR)
import emd_common as E  # noqa: E402
import emd_compare as C  # noqa: E402
import emd_leg_check as LC  # noqa: E402
import emd_prep as P  # noqa: E402

EVID = r"Z:\FAC\TUBerlin\THESIS\TaxoArena_data\evidence_2026-09-25\d9b\run_d9b_1"
POOLS = {"A": os.path.join(EVID, "pool_copy_A", "ag.db"), "B": os.path.join(EVID, "pool_copy_B", "ag.db"),
         "A2": os.path.join(EVID, "aa2", "pool_copy_A2", "ag.db")}
TRANSCRIPTS = {"A": os.path.join(EVID, "evidence_A", "legA_bootrun.log"), "B": os.path.join(EVID, "evidence_B", "legB_bootrun.log"),
               "A2": os.path.join(EVID, "evidence_A2", "legA_bootrun.log")}
MANIFEST_COMMIT = {"A": "a62c7e0ddb7a47f6ba691450c0cdd643cbdbe76d", "A2": "a62c7e0ddb7a47f6ba691450c0cdd643cbdbe76d",
                   "B": "6b9fc7c278121868cb79477a9e12803b36830a3a"}
RESULTS = []
WORK = None


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print("[%s] %s %s" % ("OK  " if cond else "FAIL", name, detail if not cond else ""), flush=True)


def quiet(fn, *a):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            rc = fn(*a)
        except SystemExit as e:
            rc = e.code
    return rc, buf.getvalue()


def mkroot(name, ev):
    r = os.path.join(WORK, "roots", name)
    shutil.copytree(os.path.join(EVID, "evidence_%s" % ev, "outputDir"), os.path.join(r, E.OUT))
    shutil.copyfile(POOLS[ev], os.path.join(r, "ag_news_smoke_cache_v1.db"))
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


def cmp(mode, x, y, lx, ly, st=None):
    st = st or stage()
    rc, out = quiet(C.main, [mode, x, y, st, lx, ly])
    js = os.path.join(st, "%s_%s_%s.json" % (mode, lx, ly))
    j = json.load(open(js, encoding="utf-8")) if os.path.isfile(js) else None
    return rc, out, j, st


def fpath(root, rel):
    return os.path.join(root, E.OUT, rel)


def edit_bytes(root, rel, fn):
    p = fpath(root, rel)
    b = open(p, "rb").read()
    assert b, p
    open(p, "wb").write(fn(b))


def csv_set(root, rel, col, val, row=-1):
    p = fpath(root, rel)
    raw = open(p, "rb").read().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    rows = list(csv.reader(io.StringIO(raw, newline="")))
    i = rows[0].index(col)
    rows[row][i] = val
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator=nl)
    w.writerows(rows)
    open(p, "wb").write(buf.getvalue().encode("utf-8"))


def quality_set(root, metric, val):
    p = fpath(root, E.QUALITY)
    lines = open(p, "rb").read().decode("utf-8").splitlines(keepends=True)
    out, hit = [], 0
    for ln in lines:
        if ln.split(",", 1)[0] == metric:
            end = ln[len(ln.rstrip("\r\n")):]
            ln = "%s,%s%s" % (metric, val, end)
            hit += 1
        out.append(ln)
    assert hit == 1, metric
    open(p, "wb").write("".join(out).encode("utf-8"))


def json_set(root, rel, key, val):
    p = fpath(root, rel)
    d = json.load(open(p, encoding="utf-8"))
    d[key] = val
    open(p, "w", encoding="utf-8").write(json.dumps(d, indent=2))


def sql(root, stmt):
    con = sqlite3.connect(os.path.join(root, "ag_news_smoke_cache_v1.db"))
    con.execute(stmt)
    con.commit()
    con.close()


# ------------------------------------------------------------------ leg-check fixture
TCLINE = "[THREAD-CAP] requested=12 availableProcessors=12 heapEstimate=n/a budget=6.00GB"


def mkleg(name, ev, x1_files, transcript_fn=None, jar_root=None, tc=(TCLINE,)):
    r = mkroot(name, ev)
    cls = os.path.join(r, "build", "classes", "kotlin", "main", "taxonomy", "utils")
    os.makedirs(cls)
    for i, n in enumerate(("AdditionalMetricsKt", "HierarchicalMetricsKt", "TaxonomyMetrics", "Other1", "Other2")):
        body = b"\xca\xfe\xba\xbe fake class " + n.encode() + (b" canonicalByRawText" if i < x1_files else b"")  # the literal identifier, never E.X1
        open(os.path.join(cls, n + ".class"), "wb").write(body)
    want = "file:/" + os.path.abspath(os.path.join(jar_root or r, "build", "classes", "kotlin", "main")).replace("\\", "/") + "/"
    tx = open(TRANSCRIPTS[ev], "rb").read().decode("utf-8", "replace")
    tx = re.sub(r"jar=file:/\S+?/build/classes/kotlin/main/", lambda _m: "jar=" + want, tx)
    if tc:   # the D9b transcripts predate THREAD-CAP: the witness line(s) are inserted after "> Task :bootRun"
        tx, n_ = re.subn(r"(> Task :bootRun)(\r?\n)", lambda m_: m_.group(1) + m_.group(2) + "".join(t + m_.group(2) for t in tc), tx, count=1)
        assert n_ == 1
    if transcript_fn:
        tx = transcript_fn(tx)
    tp = os.path.join(WORK, "tx_%s.log" % name)
    open(tp, "wb").write(tx.encode("utf-8"))
    return r, tp


def write_exit(stage_dir, leg, code):
    open(os.path.join(stage_dir, "leg%s_exit.txt" % leg), "w").write("START x\nEXIT %d\nEND y\n" % code)


def main():
    global WORK
    args = sys.argv[1:]
    if "--selftest" not in args:
        print(__doc__)
        return 2
    WORK = args[args.index("--work") + 1] if "--work" in args else os.path.join(tempfile.gettempdir(), "emd_selftest_work")
    if os.path.exists(WORK):
        shutil.rmtree(WORK)
    os.makedirs(os.path.join(WORK, "roots"))
    print("[emd_selftest] harness %s ; work %s ; evidence %s" % (HDIR, WORK, EVID), flush=True)

    # ---- T1 lists
    rc, _o = quiet(E.assert_lists_match_originals)
    check("T1a the copied object / drop lists equal the pinned d9_compare / d9b_compare originals (16 lists)", rc == 16, rc)
    check("T1b C3 has the 24 D9b objects, C4 the 24 D9 objects, C1 the 2 files",
          len(C.SCHEMES["c3"][0]) == 24 and len(C.SCHEMES["c4"][0]) == 24 and C.SCHEMES["c1"][0] == [E.QUALITY, E.LEDGER])
    check("T1c the D9b drops remove exactly DP, SS, TDC rows / columns (and CommitSHA, wall_ms); D9 drops CommitSHA and wall_ms only",
          E.D9B_CSV_DROP["tuning_ledger.csv"] == ["CommitSHA"] + E.DECLARED and E.D9_CSV_DROP["tuning_ledger.csv"] == ["CommitSHA"]
          and E.D9B_ROW_DROP[E.QUALITY] == ("Metric", E.DECLARED) and E.QUALITY in E.D9_BYTE)

    saved_drop = list(E.D9B_CSV_DROP["tuning_ledger.csv"])
    E.D9B_CSV_DROP["tuning_ledger.csv"].append("RoutingECE")
    try:
        E.assert_lists_match_originals()
        refused = False
    except E.Refuse:
        refused = True
    E.D9B_CSV_DROP["tuning_ledger.csv"][:] = saved_drop
    check("T1d a copied drop list that differs from the original (+RoutingECE) is refused", refused)
    fake = os.path.join(WORK, "d9b_compare_edited.py")
    open(fake, "wb").write(open(E.ORIG["d9b_compare"][0], "rb").read() + b"# edited\n")
    saved_orig = E.ORIG["d9b_compare"]
    E.ORIG["d9b_compare"] = (fake, saved_orig[1])
    try:
        E.assert_lists_match_originals()
        refused = False
    except E.Refuse as e:
        refused = "sha256-lf" in str(e)
    E.ORIG["d9b_compare"] = saved_orig
    check("T1e an original whose LF sha256 is off its pin is refused", refused)
    check("T1f the leg plan is pinned: order P1 R1 R2 P2 R3; BASE 2f080e0 / FIX 6569cd3; P legs BASE, R legs FIX; X1 canonicalByRawText;"
          " THREAD-CAP 12; AG inputs re-read",
          E.LEGS == ("P1", "R1", "R2", "P2", "R3") and E.BASE == "2f080e079f79c62c3a38337005438c6a310be81b"
          and E.FIX == "6569cd31ead59b2f822ab5c2b91347443e1cd378" and E.THREAD_CAP_N == 12 and E.TC_WITNESS == "requested=12 availableProcessors=12"
          and E.AG_BASE == {"ag_news_smoke_cache_v1.db": (1748992, "e3415684318c937c8e9073e1eb189c1f5a89006c0444794c20cf7b79ba527430"),
                            "ag_news_smoke_cache_v1.db-wal": (0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")}
          and E.COMMIT == {"P1": E.BASE, "R1": E.FIX, "R2": E.FIX, "P2": E.BASE, "R3": E.FIX}
          and E.C1_PAIRS == (("R1", "R2"), ("R1", "R3"), ("R2", "R3")) and E.C3_PAIRS == (("P1", "R1"),)
          and E.X1 == "canonicalByRawText" and E.AG_COPY_SHA.startswith("e3415684") and E.EMB_BASE[1].startswith("52229e1e"))

    A = mkroot("A", "A")
    B = mkroot("B", "B")
    A2 = mkroot("A2", "A2")
    Ad = clone(A, "A_dup")

    # ---- T2 EQUAL on duplicates
    for mode, lx, ly in (("c1", "R1", "R2"), ("c3", "P1", "R1"), ("c4", "R1", "R3")):
        rc, o, j, _ = cmp(mode, A, Ad, lx, ly)
        check("T2 %s on a byte duplicate -> exit 0, 0 differ" % mode, rc == 0 and j and j["differing"] == [], o[-300:])

    # ---- T3 C3 reproduces the archived d9b readouts digest for digest
    for ev, root, arch in (("B", B, os.path.join(EVID, "d9b_compare.json")), ("A2", A2, os.path.join(EVID, "aa2", "d9b_compare.json"))):
        rc, o, j, _ = cmp("c3", A, root, "P1", "R1")
        a = json.load(open(arch, encoding="utf-8"))
        same = j is not None and all(j["digest"][ob] == a["digest"][ob] for ob in E.D9B_OBJECTS if ob not in E.TABLES) \
            and all(j["digest"][t] == a["digest"][t] for t in E.TABLES)
        check("T3 C3 on archived A vs %s: exit %s, differing %s, and all 24 digests equal the archived d9b_compare.json"
              % (ev, rc, j and j["differing"]), rc == 0 and same)

    # ---- T4 C4 agrees with the original d9_compare on the same pair (per-file digests and the overall reading)
    orig = E.ORIG["d9_compare"][0]
    for ev, root in (("B", B), ("A2", A2)):
        st = stage()
        pr = subprocess.run([sys.executable, orig, A, root, st], capture_output=True, text=True)
        lines = {m[0]: (m[1], m[2]) for m in re.findall(r"^\[C1\] (\S+).*? A ([0-9a-f]{16}) B ([0-9a-f]{16})", pr.stdout, re.M)}
        rc, o, j, _ = cmp("c4", A, root, "R1", "R2")
        agree = j is not None and len(lines) == 21 and all(
            (j["digest"][rel][0][:16], j["digest"][rel][1][:16]) == lines[rel] for rel in lines)
        check("T4 C4 on A vs %s: 21 per-file digests equal the original d9_compare's; readings agree (orig exit %d, mine %d)"
              % (ev, pr.returncode, rc), agree and (pr.returncode == 0) == (rc == 0))

    # ---- T5 C1 on real pairs reads the DP / SS / TDC jitter that D9b dropped
    rc, o, j, _ = cmp("c1", A, B, "R1", "R2")
    check("T5a C1 on archived A vs B (TDC 2.2285e8 vs 2.2249e8) -> exit 3, both files differ", rc == 3 and j["differing"] == [E.QUALITY, E.LEDGER])
    rc, o, j, _ = cmp("c1", A, A2, "R1", "R3")
    direct = [ob for ob in (E.QUALITY, E.LEDGER) if open(fpath(A, ob), "rb").read() != open(fpath(A2, ob), "rb").read()]
    check("T5b C1 on archived A vs A2 agrees with a direct byte compare (%s)" % direct, j is not None and j["differing"] == direct
          and rc == (3 if direct else 0))

    # ---- T6 mutations, one object class at a time: expected (C1, C3, C4) differing sets
    cases = [
        ("byte file proposals.csv", lambda y: edit_bytes(y, "seed_42/diagnostics/proposals.csv", lambda b: b + b"x"),
         [], ["seed_42/diagnostics/proposals.csv"], ["seed_42/diagnostics/proposals.csv"]),
        ("byte file gate_ids.json", lambda y: edit_bytes(y, "seed_42/gate_ids.json", lambda b: b.replace(b"1", b"2", 1)),
         [], ["seed_42/gate_ids.json"], ["seed_42/gate_ids.json"]),
        ("iteration_metrics kept column (mass)", lambda y: csv_set(y, "seed_42/diagnostics/iteration_metrics.csv", "mass", "9.000"),
         [], ["seed_42/diagnostics/iteration_metrics.csv"], ["seed_42/diagnostics/iteration_metrics.csv"]),
        ("iteration_metrics dropped column (wall_ms)", lambda y: csv_set(y, "seed_42/diagnostics/iteration_metrics.csv", "wall_ms", "12345"),
         [], [], []),
        ("run_manifest kept key (exit_reason)", lambda y: json_set(y, "seed_42/diagnostics/run_manifest.json", "exit_reason", "x"),
         [], ["seed_42/diagnostics/run_manifest.json"], ["seed_42/diagnostics/run_manifest.json"]),
        ("run_manifest dropped key (duration_ms)", lambda y: json_set(y, "seed_42/diagnostics/run_manifest.json", "duration_ms", 1),
         [], [], []),
        ("quality CSV kept row (SeparationJ)", lambda y: quality_set(y, "SeparationJ", "0.5"), [E.QUALITY], [E.QUALITY], [E.QUALITY]),
        ("quality CSV DendrogramPurity", lambda y: quality_set(y, "DendrogramPurity", "0.6867787184488066"), [E.QUALITY], [], [E.QUALITY]),
        ("quality CSV SphericalSilhouette", lambda y: quality_set(y, "SphericalSilhouette", "0.12807057880923325"), [E.QUALITY], [], [E.QUALITY]),
        ("quality CSV TotalDasguptaCost", lambda y: quality_set(y, "TotalDasguptaCost", "2.2248549838590908E8"), [E.QUALITY], [], [E.QUALITY]),
        ("quality CSV line endings LF -> CRLF", lambda y: edit_bytes(y, E.QUALITY, lambda b: b.replace(b"\n", b"\r\n")),
         [E.QUALITY], [E.QUALITY], [E.QUALITY]),
        ("ledger DendrogramPurity", lambda y: csv_set(y, E.LEDGER, "DendrogramPurity", "0.1"), [E.LEDGER], [], [E.LEDGER]),
        ("ledger SphericalSilhouette", lambda y: csv_set(y, E.LEDGER, "SphericalSilhouette", "0.1"), [E.LEDGER], [], [E.LEDGER]),
        ("ledger TotalDasguptaCost", lambda y: csv_set(y, E.LEDGER, "TotalDasguptaCost", "1.0E8"), [E.LEDGER], [], [E.LEDGER]),
        ("ledger CommitSHA", lambda y: csv_set(y, E.LEDGER, "CommitSHA", "deadbeef"), [E.LEDGER], [], []),
        ("ledger kept column RoutingECE", lambda y: csv_set(y, E.LEDGER, "RoutingECE", "0.9"), [E.LEDGER], [E.LEDGER], [E.LEDGER]),
        ("file set: an extra file", lambda y: open(fpath(y, "seed_42/extra.txt"), "w").write("x"), [], [E.FILESET], [E.FILESET]),
        ("excluded file performance_report.json", lambda y: edit_bytes(y, "seed_42/performance_report.json", lambda b: b + b" "),
         [], [], []),
        ("listed file absent in one leg", lambda y: os.remove(fpath(y, "seed_42/validation/bridge_nodes.csv")),
         [], ["seed_42/validation/bridge_nodes.csv", E.FILESET], ["seed_42/validation/bridge_nodes.csv", E.FILESET]),
        ("reserved_pool row", lambda y: sql(y, "UPDATE reserved_pool SET domain = 'zzz' WHERE question_id = (SELECT min(question_id) FROM reserved_pool)"),
         [], ["reserved_pool"], ["reserved_pool"]),
        ("reserved_pool_meta dropped column created_at", lambda y: sql(y, "UPDATE reserved_pool_meta SET created_at = 1"), [], [], []),
        ("reserved_pool_meta kept column seed", lambda y: sql(y, "UPDATE reserved_pool_meta SET seed = seed + 1"),
         [], ["reserved_pool_meta"], ["reserved_pool_meta"]),
    ]
    for k, (name, fn, w1, w3, w4) in enumerate(cases):
        y = clone(A, "mut%02d" % k)
        fn(y)
        got = {}
        for mode, lx, ly in (("c1", "R1", "R2"), ("c3", "P1", "R1"), ("c4", "R1", "R2")):
            rc, o, j, _ = cmp(mode, A, y, lx, ly)
            got[mode] = (rc, j["differing"] if j else None)
        want = {"c1": w1, "c3": w3, "c4": w4}
        ok = all(got[m][1] == want[m] and got[m][0] == (3 if want[m] else 0) for m in want)
        check("T6.%02d %s -> C1 %s / C3 %s / C4 %s" % (k, name, w1 or "equal", w3 or "equal", w4 or "equal"), ok, got)

    # ---- T7 refusals (pair labels, arguments, write-once, absent in both legs)
    for mode, lx, ly in (("c1", "P1", "R1"), ("c1", "R2", "R1"), ("c1", "R1", "R1"), ("c3", "R1", "R2"), ("c3", "R1", "P1"),
                         ("c4", "P1", "P2"), ("c4", "A", "B"), ("c3", "P1", "P2")):
        rc, o, j, st = cmp(mode, A, Ad, lx, ly)
        check("T7 %s refuses the pair (%s, %s)" % (mode, lx, ly), rc == 2 and "INSTRUMENT REFUSAL" in o and not os.listdir(st))
    rc, o = quiet(C.main, ["c1", A, Ad, stage(), "R1"])
    check("T7 wrong argument count refused", rc == 2)
    rc, o = quiet(C.main, ["c9", A, Ad, stage(), "R1", "R2"])
    check("T7 unknown mode refused", rc == 2)
    st = stage()
    cmp("c1", A, Ad, "R1", "R2", st)
    rc, o, _j, _ = cmp("c1", A, Ad, "R1", "R2", st)
    check("T7 a second c1 into the same stage is refused (write-once)", rc == 2 and "write-once" in o)
    st = stage()
    cmp("c3", A, Ad, "P1", "R1", st)
    rc, o, _j, _ = cmp("c3", A, Ad, "P1", "R1", st)
    check("T7 a second c3 into the same stage is refused (write-once)", rc == 2)
    x, y = clone(A, "absx"), clone(A, "absy")
    for r in (x, y):
        os.remove(fpath(r, "seed_42/validation/bridge_nodes.csv"))
    rc, o, j, _ = cmp("c4", x, y, "R1", "R2")
    check("T7 a listed file absent in BOTH legs is an INSTRUMENT REFUSAL (exit 2), nothing written", rc == 2 and j is None)
    y = clone(A, "nopool")
    os.remove(os.path.join(y, "ag_news_smoke_cache_v1.db"))
    rc, o, j, _ = cmp("c3", A, y, "P1", "R1")
    check("T7 an absent AG DB is refused", rc == 2 and j is None)
    y = clone(A, "noledgercol")
    p = fpath(y, E.LEDGER)
    raw = open(p, "rb").read()
    open(p, "wb").write(raw.replace(b"TotalDasguptaCost", b"TDCx", 1))
    rc, o, j, _ = cmp("c3", A, y, "P1", "R1")
    check("T7 a declared column absent from the header is refused and named with the leg", rc == 2 and "leg R1" in o)
    y = clone(A, "emptycsv")
    open(fpath(y, "seed_42/diagnostics/iteration_metrics.csv"), "wb").close()
    rc, o, j, _ = cmp("c4", A, y, "R1", "R2")
    check("T7 an empty column-drop file is an INSTRUMENT REFUSAL, not a traceback", rc == 2 and "empty file" in o and j is None)

    # ---- T8 emd_leg_check
    saved_commit = dict(E.COMMIT)
    E.COMMIT.update({"P1": MANIFEST_COMMIT["A"], "R1": MANIFEST_COMMIT["A"], "R2": MANIFEST_COMMIT["A"],
                     "P2": MANIFEST_COMMIT["B"], "R3": MANIFEST_COMMIT["A2"]})

    def leg_case(name, leg, ev, x1n, exit_code=0, tfn=None, mut=None, jar_root=None, tc=(TCLINE,)):
        st = stage()
        r, tp = mkleg(name, ev, x1n, tfn, jar_root, tc)
        if mut:
            mut(r)
        write_exit(st, leg, exit_code)
        rc, o = quiet(LC.main, leg, r, tp, st)
        j = json.load(open(os.path.join(st, "leg_%s.json" % leg))) if os.path.isfile(os.path.join(st, "leg_%s.json" % leg)) else None
        return rc, o, j, st, r, tp
    rc, o, j, st, r, tp = leg_case("lcP1", "P1", "A", 0)
    check("T8a P leg with 0 X1 files: all per-leg checks pass", rc == 0 and j["x1_count"] == 0 and all(j["checks"].values()), o[-400:])
    check("T8a' misses 0, duration and Gradle seconds recorded, fields recorded",
          j["misses"] == 0 and j["duration_ms"] == 10471 and j["gradle_s"] == 58 and j["values"].get("quality:TotalDasguptaCost"))
    rc2, o2 = quiet(LC.main, "P1", r, tp, st)
    check("T8b a second check of the same leg into the same stage is refused (write-once)", rc2 == 2)
    rc, o, j, *_ = leg_case("lcR1", "R1", "A", 3)
    check("T8c R leg with 3 X1 files: pass; declared count matches", rc == 0 and j["x1_count"] == 3 and "match" in o)
    rc, o, j, *_ = leg_case("lcR1b", "R1", "A", 1)
    check("T8d R leg with 1 X1 file: V3 passes on the registered bar (>= 1), the declared-count mismatch is printed",
          rc == 0 and j["checks"]["V3"] and "DOES NOT MATCH" in o)
    rc, o, j, *_ = leg_case("lcR0", "R2", "A", 0)
    check("T8e R leg with 0 X1 files: V3 FAILS (the change did not compile in)", rc == 1 and j["checks"]["V3"] is False)
    rc, o, j, *_ = leg_case("lcP1x", "P1", "A", 1)
    check("T8f P leg with 1 X1 file: V3 FAILS", rc == 1 and j["checks"]["V3"] is False)
    other = os.path.join(WORK, "elsewhere")
    rc, o, j, *_ = leg_case("lcV4", "P1", "A", 0, jar_root=other)
    check("T8g V4: a jar token naming another classes dir FAILS", rc == 1 and j["checks"]["V4"] is False)
    rc, o, j, *_ = leg_case("lcV4b", "P1", "A", 0, tfn=lambda t: t.replace("> Task :bootRun", "> Task :bootRunX"))
    check("T8h V4: no [BOOT] line after '> Task :bootRun' FAILS", rc == 1 and j["checks"]["V4"] is False)
    rc, o, j, *_ = leg_case("lcV5", "P1", "A", 0, tfn=lambda t: re.sub(r"> Task :compileKotlin(?=\r?\n)", "> Task :compileKotlin UP-TO-DATE", t, count=1))
    check("T8i V5: compileKotlin UP-TO-DATE FAILS", rc == 1 and j["checks"]["V5"] is False)
    rc, o, j, *_ = leg_case("lcV5b", "P1", "A", 0, tfn=lambda t: re.sub(r"> Task :compileKotlin(?=\r?\n)", "> Task :compileKotlin FROM-CACHE", t, count=1))
    check("T8j V5: compileKotlin FROM-CACHE FAILS", rc == 1 and j["checks"]["V5"] is False)
    rc, o, j, *_ = leg_case("lcV6a", "P1", "A", 0, exit_code=1)
    check("T8k V6: last EXIT 1 FAILS", rc == 1 and j["checks"]["V6"] is False)
    rc, o, j, *_ = leg_case("lcV6b", "P1", "A", 0, tfn=lambda t: t + "\nBUILD FAILED in 3s\n")
    check("T8l V6: BUILD FAILED in the transcript FAILS", rc == 1 and j["checks"]["V6"] is False)
    rc, o, j, *_ = leg_case("lcV6c", "P2", "A", 0)
    check("T8m V6: run_manifest commit not the leg's assigned commit FAILS", rc == 1 and j["checks"]["V6"] is False)
    rc, o, j, *_ = leg_case("lcV6d", "P1", "A", 0, mut=lambda r: json_set(r, "seed_42/diagnostics/run_manifest.json", "dirty", True))
    check("T8n V6: dirty True FAILS", rc == 1 and j["checks"]["V6"] is False)
    rc, o, j, *_ = leg_case("lcV6e", "P1", "A", 0, mut=lambda r: edit_bytes(r, "seed_42/headless_run.log",
                                                                              lambda b: b.replace(b"[POOL] recorded", b"[POOL] rec")))
    check("T8o V6: a missing sanity line FAILS", rc == 1 and j["checks"]["V6"] is False)
    rc, o, j, *_ = leg_case("lcV6f", "P1", "A", 0, mut=lambda r: json_set(r, "seed_42/diagnostics/run_manifest.json", "exit_reason", "error"))
    check("T8p V6: exit_reason not completed FAILS", rc == 1 and j["checks"]["V6"] is False)
    rc, o, j, *_ = leg_case("lcV8a", "P1", "A", 0, mut=lambda r: json_set(r, "seed_42/diagnostics/run_manifest.json", "duration_ms", 480001))
    check("T8q V8: duration_ms above 8 min FAILS", rc == 1 and j["checks"]["V8"] is False)
    rc, o, j, *_ = leg_case("lcV8a2", "P1", "A", 0, mut=lambda r: json_set(r, "seed_42/diagnostics/run_manifest.json", "duration_ms", 480000))
    check("T8q' V8: duration_ms exactly 8 min FAILS (registered 'under 8 min')", rc == 1 and j["checks"]["V8"] is False)
    rc, o, j, *_ = leg_case("lcV8a3", "P1", "A", 0, tfn=lambda t: t.replace("BUILD SUCCESSFUL in 58s", "BUILD SUCCESSFUL in 8m"))
    check("T8q'' V8: Gradle wall exactly 8 min ('in 8m') FAILS", rc == 1 and j["checks"]["V8"] is False)
    check("T8q''' Gradle times parse: 58s, 1m 5s, 2m, 350ms, 1h 2m 3s; garbage -> None",
          [LC.gradle_seconds("BUILD SUCCESSFUL in %s\n" % t) for t in ("58s", "1m 5s", "2m", "350ms", "1h 2m 3s", "soon", "", "58s later")]
          == [58, 65, 120, 0.35, 3723, None, None, None])
    rc, o, j, *_ = leg_case("lcV8b", "P1", "A", 0, tfn=lambda t: t.replace("BUILD SUCCESSFUL in 58s", "BUILD SUCCESSFUL in 8m 1s"))
    check("T8r V8: Gradle wall above 8 min FAILS", rc == 1 and j["checks"]["V8"] is False)
    rc, o, j, *_ = leg_case("lcV8c", "P1", "A", 0, mut=lambda r: edit_bytes(r, "seed_42/diagnostics/iteration_metrics.csv",
                                                                              lambda b: b.split(b"\n", 1)[0] + b"\n"))
    check("T8s V8: no iteration_metrics data row FAILS", rc == 1 and j["checks"]["V8"] is False)
    rc, o, j, *_ = leg_case("lcV7", "P1", "A", 0, mut=lambda r: edit_bytes(r, "seed_42/headless_run.log",
                                                                            lambda b: b + b"\nComputing and caching embeddings for 7 new queries\n"))
    check("T8t V7: misses counted from the log (7)", j["misses"] == 7)
    rc, o = quiet(LC.main, "A", r, tp, stage())
    check("T8u a leg name outside P1/R1/R2/P2/R3 is refused", rc == 2)
    # TC: the THREAD-CAP witness (B-EM-1 (4))
    rc, o, j, *_ = leg_case("lcTC0", "P1", "A", 0)
    check("T8v TC: one witness line 12/12 -> TC PASS, witness recorded", rc == 0 and j["checks"]["TC"] is True
          and j["thread_cap"] == ["requested=12 availableProcessors=12"] and "[TC P1] 1 [THREAD-CAP] line(s)" in o, o[-300:])
    rc, o, j, *_ = leg_case("lcTC1", "R1", "A", 3, tc=())
    check("T8w TC: no [THREAD-CAP] line (an uncapped or pre-cap build) -> TC FAILS, the leg is VOID",
          rc == 1 and j["checks"]["TC"] is False and j["thread_cap"] == [] and "'TC'" in o, o[-300:])
    rc, o, j, *_ = leg_case("lcTC2", "P1", "A", 0, tc=("[THREAD-CAP] requested=none availableProcessors=24 heapEstimate=n/a budget=6.00GB",))
    check("T8x TC: requested=none availableProcessors=24 -> TC FAILS", rc == 1 and j["checks"]["TC"] is False)
    rc, o, j, *_ = leg_case("lcTC3", "P1", "A", 0, tc=("[THREAD-CAP] requested=12 availableProcessors=24 heapEstimate=n/a budget=6.00GB",))
    check("T8y TC: requested=12 but availableProcessors=24 (the flag did not reach the fork) -> TC FAILS",
          rc == 1 and j["checks"]["TC"] is False and j["thread_cap"] == ["requested=12 availableProcessors=24"])
    rc, o, j, *_ = leg_case("lcTC4", "R2", "A", 3, tc=(TCLINE, "[THREAD-CAP] requested=12 availableProcessors=11 heapEstimate=n/a budget=6.00GB"))
    check("T8z TC: the first line 12/12 but a later line 12/11 -> TC FAILS (every line, not the first)",
          rc == 1 and j["checks"]["TC"] is False and len(j["thread_cap"]) == 2)
    rc, o, j, *_ = leg_case("lcTC5", "R3", "A", 3, tc=(TCLINE, TCLINE))
    check("T8z' TC: two forks both 12/12 (processAot + the app) -> TC PASS, one witness", rc == 0 and j["checks"]["TC"] is True
          and j["thread_cap"] == ["requested=12 availableProcessors=12"] and "[TC R3] 2 [THREAD-CAP] line(s)" in o, o[-300:])
    E.COMMIT.clear()
    E.COMMIT.update(saved_commit)

    # ---- T9 emd_prep (git monkeypatched; fake inputs; no main DB read)
    fmain = os.path.join(WORK, "fmain")
    os.makedirs(fmain)
    shutil.copyfile(POOLS["A"], os.path.join(fmain, "ag_news_smoke_cache_v1.db"))
    open(os.path.join(fmain, "ag_news_smoke_cache_v1.db-wal"), "wb").close()
    open(os.path.join(fmain, "embeddings_cache.db"), "wb").write(b"fake embeddings")
    tmpc = os.path.join(WORK, "ckpt")
    os.makedirs(tmpc)
    shutil.copyfile(POOLS["A"], os.path.join(tmpc, "x.db"))
    con = sqlite3.connect(os.path.join(tmpc, "x.db"))
    con.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    con.close()
    saved = (dict(E.AG_BASE), E.EMB_BASE, E.AG_COPY_SHA, P.git)
    E.AG_BASE.clear()
    E.AG_BASE.update({n: (os.path.getsize(os.path.join(fmain, n)), E.sha(os.path.join(fmain, n)))
                      for n in ("ag_news_smoke_cache_v1.db", "ag_news_smoke_cache_v1.db-wal")})
    E.EMB_BASE = (15, E.sha(os.path.join(fmain, "embeddings_cache.db")))
    E.AG_COPY_SHA = E.sha(os.path.join(tmpc, "x.db"))
    legroots = {}
    for l in E.LEGS:
        legroots[l] = os.path.join(WORK, "fleg" + l)
        os.makedirs(legroots[l])
        open(os.path.join(legroots[l], ".git"), "w").write("gitdir: x")
    state = {"head": {legroots[l]: E.COMMIT[l] for l in E.LEGS}, "srcdiff": sorted(E.FIX_SRC), "test": "A\t" + E.TEST_PATH,
             "other": "", "moved": "", "blob": dict(E.FIX_SRC), "testblob": E.TEST_BLOB, "toml": E.TOML_BLOB, "status": ""}

    def fake_git(root, *a):
        if a[0] == "diff" and a[1] == "--name-only" and a[2] == E.BASE and a[3] == E.FIX and "src/main" in a:
            return "\n".join(state["srcdiff"])
        if a[0] == "diff" and a[1] == "--name-status":
            return state["test"]
        if a[0] == "diff" and "experiment_configs" in a:
            return state["other"]
        if a[0] == "diff" and a[3] == "main":
            return state["moved"]
        if a[:2] == ("rev-parse", "HEAD"):
            return state["head"][root]
        if a[0] == "rev-parse":
            c, f = a[1].split(":", 1)
            return state["toml"] if f == E.TOML else state["testblob"] if f == E.TEST_PATH else state["blob"][f]
        if a[0] == "status":
            return state["status"]
        raise AssertionError(a)
    P.git = fake_git
    argv = ["pre", fmain] + [legroots[l] for l in E.LEGS]

    def prep_run(st):
        P.LOG.clear()
        return quiet(P.main, argv + [st])
    fst = os.path.join(WORK, "fstage")
    rc, o = prep_run(fst)
    same = rc == 0 and all(E.sha(os.path.join(legroots[l], n)) == E.sha(os.path.join(fst, n))
                           for l in E.LEGS for n in ("ag_news_smoke_cache_v1.db", "embeddings_cache.db"))
    pj = json.load(open(os.path.join(fst, "emd_prep.json"))) if os.path.isfile(os.path.join(fst, "emd_prep.json")) else {}
    check("T9a emd_prep: V1 PASS, byte-identical inputs in all five legs, emd_prep.json v1/v2 True with the five roots",
          same and "[V1] PASS" in o and "[V2] PASS: all five legs" in o and pj.get("v1") and pj.get("v2")
          and pj.get("roots") == legroots and os.path.isdir(os.path.join(fst, "classlists")), o[-300:])
    rc, o = prep_run(fst)
    check("T9b emd_prep refuses an existing stage", rc == 1 and "exists" in o)

    def reset_legs():
        for l in E.LEGS:
            for n in ("ag_news_smoke_cache_v1.db", "embeddings_cache.db"):
                q = os.path.join(legroots[l], n)
                if os.path.exists(q):
                    os.remove(q)
    reset_legs()
    for name, key, val in (("an extra src/main file in BASE..FIX", "srcdiff", sorted(E.FIX_SRC) + ["src/main/kotlin/x.kt"]),
                           ("the test file Modified, not Added", "test", "M\t" + E.TEST_PATH),
                           ("a tools / experiment_configs diff", "other", "tools/x.py"),
                           ("main moved since BASE on src/main", "moved", "src/main/kotlin/y.kt"),
                           ("a FIX blob not at its pin", "blob", dict(E.FIX_SRC, **{sorted(E.FIX_SRC)[0]: "0" * 40})),
                           ("the test blob not at its pin", "testblob", "1" * 40),
                           ("the arm TOML blob differs", "toml", "2" * 40),
                           ("a dirty leg worktree", "status", " M x"),
                           ("leg R2 at BASE instead of FIX", "head", dict(state["head"], **{legroots["R2"]: E.BASE}))):
        old = state[key]
        state[key] = val
        st = os.path.join(WORK, "fst_%s" % key)
        rc, o = prep_run(st)
        check("T9c emd_prep refuses: %s" % name, rc == 1 and "REFUSED" in o and not os.path.isfile(os.path.join(st, "emd_prep.json")))
        state[key] = old
        reset_legs()
    os.makedirs(os.path.join(legroots["P2"], "build"))
    rc, o = prep_run(os.path.join(WORK, "fst_build"))
    check("T9d emd_prep refuses a leg root holding build/ (not fresh)", rc == 1 and "already holds build" in o)
    os.rmdir(os.path.join(legroots["P2"], "build"))
    open(os.path.join(legroots["R3"], "ratings_emd_R3.db"), "wb").close()
    rc, o = prep_run(os.path.join(WORK, "fst_rat"))
    check("T9e emd_prep refuses a leg root holding ratings_emd_<leg>.db", rc == 1)
    os.remove(os.path.join(legroots["R3"], "ratings_emd_R3.db"))
    reset_legs()
    open(os.path.join(fmain, "embeddings_cache.db"), "ab").write(b"!")
    rc, o = prep_run(os.path.join(WORK, "fst_emb"))
    check("T9f emd_prep refuses main's embeddings file off its pin", rc == 1 and "differs from its pin" in o)
    E.AG_BASE.clear()
    E.AG_BASE.update(saved[0])
    E.EMB_BASE, E.AG_COPY_SHA, P.git = saved[1], saved[2], saved[3]

    # pins / post (V9) on a fake main of small SQLite files
    pm = os.path.join(WORK, "pmain")
    os.makedirs(pm)
    for n in ("embeddings_cache.db", "snapshots.db"):
        con = sqlite3.connect(os.path.join(pm, n))
        con.execute("CREATE TABLE t (a, b)")
        con.executemany("INSERT INTO t VALUES (?, ?)", [(i, "v%d" % i) for i in range(20)])
        con.commit()
        con.close()
    shutil.copyfile(POOLS["A"], os.path.join(pm, "ag_news_smoke_cache_v1.db"))
    open(os.path.join(pm, "ag_news_smoke_cache_v1.db-wal"), "wb").close()
    b1, b2 = os.path.join(WORK, "pins_before.json"), os.path.join(WORK, "pins_after.json")
    rc1, _ = quiet(P.main, ["pins", pm, b1])
    rc2, _ = quiet(P.main, ["pins", pm, b2])
    pst = stage()
    rc, o = quiet(P.main, ["post", b1, b2, pst])
    check("T9g pins twice on an unchanged fake main -> V9 MET", rc1 == 0 and rc2 == 0 and rc == 0
          and json.load(open(os.path.join(pst, "emd_post.json")))["v9"] is True)
    rc, o = quiet(P.main, ["pins", pm, b1])
    check("T9h pins refuses an existing output (write-once)", rc == 1)
    con = sqlite3.connect(os.path.join(pm, "snapshots.db"))
    con.execute("UPDATE t SET b = 'changed' WHERE a = 3")
    con.commit()
    con.close()
    b3 = os.path.join(WORK, "pins_after2.json")
    quiet(P.main, ["pins", pm, b3])
    pst = stage()
    rc, o = quiet(P.main, ["post", b1, b3, pst])
    check("T9i a changed snapshots.db row -> V9 NOT MET", rc == 1 and json.load(open(os.path.join(pst, "emd_post.json")))["v9"] is False)
    os.utime(os.path.join(pm, "ag_news_smoke_cache_v1.db-wal"), None)
    b4 = os.path.join(WORK, "pins_after3.json")
    quiet(P.main, ["pins", pm, b4])
    pst = stage()
    rc, o = quiet(P.main, ["post", b3, b4, pst])
    check("T9j a touched AG -wal (mtime moved, content equal) -> V9 NOT MET", rc == 1)
    # two-view rationale: a committed WAL tail leaves the main file's bytes unchanged but moves the mode=ro view
    pw = os.path.join(WORK, "pmainw")
    os.makedirs(pw)
    for n in ("embeddings_cache.db", "snapshots.db"):
        shutil.copyfile(os.path.join(pm, n), os.path.join(pw, n))
    shutil.copyfile(os.path.join(pm, "ag_news_smoke_cache_v1.db"), os.path.join(pw, "ag_news_smoke_cache_v1.db"))
    open(os.path.join(pw, "ag_news_smoke_cache_v1.db-wal"), "wb").close()
    con = sqlite3.connect(os.path.join(pw, "snapshots.db"))
    con.execute("PRAGMA journal_mode=WAL")
    con.close()
    w1_, w2_ = os.path.join(WORK, "pw1.json"), os.path.join(WORK, "pw2.json")
    quiet(P.main, ["pins", pw, w1_])
    holder = sqlite3.connect(os.path.join(pw, "snapshots.db"))
    holder.execute("PRAGMA wal_autocheckpoint=0")
    holder.execute("INSERT INTO t VALUES (99, 'wal tail')")
    holder.commit()
    quiet(P.main, ["pins", pw, w2_])
    holder.close()
    pj1, pj2 = json.load(open(w1_)), json.load(open(w2_))
    pst = stage()
    rc, o = quiet(P.main, ["post", w1_, w2_, pst])
    check("T9k a committed WAL tail (main file sha256 unchanged) -> the mode=ro view differs -> V9 NOT MET",
          rc == 1 and pj1["files"]["snapshots.db"][2] == pj2["files"]["snapshots.db"][2], (pj1["files"]["snapshots.db"], pj2["files"]["snapshots.db"]))
    pv = os.path.join(WORK, "pmainv")
    shutil.copytree(pm, pv)
    v1_, v2_ = os.path.join(WORK, "pv1.json"), os.path.join(WORK, "pv2.json")
    con = sqlite3.connect(os.path.join(pv, "embeddings_cache.db"))
    con.execute("PRAGMA user_version = 0")
    con.close()
    quiet(P.main, ["pins", pv, v1_])
    con = sqlite3.connect(os.path.join(pv, "embeddings_cache.db"))
    con.execute("PRAGMA user_version = 7")
    con.close()
    quiet(P.main, ["pins", pv, v2_])
    q1, q2 = json.load(open(v1_)), json.load(open(v2_))
    pst = stage()
    rc, o = quiet(P.main, ["post", v1_, v2_, pst])
    check("T9l file bytes changed with every table view equal (user_version) -> the sha256 decides -> V9 NOT MET",
          rc == 1 and q1["views"]["embeddings_cache.db"] == q2["views"]["embeddings_cache.db"])

    # ---- T10 the verdict: a complete stage built by the real modes, then one cell per case
    E.COMMIT.update({"P1": MANIFEST_COMMIT["A"], "R1": MANIFEST_COMMIT["A"], "R2": MANIFEST_COMMIT["A"],
                     "P2": MANIFEST_COMMIT["B"], "R3": MANIFEST_COMMIT["A"]})
    VS = os.path.join(WORK, "vstage")
    os.makedirs(os.path.join(VS, "classlists"))
    vroots = {}
    for l, ev, x1n in (("P1", "A", 0), ("R1", "A", 3), ("R2", "A", 3), ("P2", "B", 0), ("R3", "A", 3)):
        r, tp = mkleg("v" + l, ev, x1n)
        vroots[l] = r
        write_exit(VS, l, 0)
        rc, o = quiet(LC.main, l, r, tp, VS)
        check("T10 setup: leg check %s passes" % l, rc == 0, o[-300:])
    E.COMMIT.clear()
    E.COMMIT.update(saved_commit)
    for x, y in E.C1_PAIRS:
        for mode in ("c1", "c4"):
            rc, o, j, _ = cmp(mode, vroots[x], vroots[y], x, y, VS)
            check("T10 setup: %s %s/%s exit 0" % (mode, x, y), rc == 0, o[-300:])
    rc, o, j, _ = cmp("c3", vroots["P1"], vroots["R1"], "P1", "R1", VS)
    check("T10 setup: c3 P1/R1 exit 0", rc == 0)
    E.write_json_once(os.path.join(VS, "emd_prep.json"), {"version": "t", "v1": True, "v2": True, "roots": vroots})
    E.write_json_once(os.path.join(VS, "emd_post.json"), {"version": "t", "v9": True})
    fixd = os.path.join(WORK, "fixxml")
    os.makedirs(fixd)

    def xml(path, cls, cases_):
        body = "".join('<testcase name="%s" classname="%s">%s</testcase>' % (n, cls, {"PASSED": "", "FAILED": "<failure message=\"x\"/>",
                                                                                     "SKIPPED": "<skipped/>", "ERROR": "<error/>"}[s])
                       for n, s in cases_)
        f = sum(s == "FAILED" for _n, s in cases_)
        e = sum(s == "ERROR" for _n, s in cases_)
        sk = sum(s == "SKIPPED" for _n, s in cases_)
        open(path, "w", encoding="utf-8").write('<?xml version="1.0"?><testsuite name="%s" tests="%d" skipped="%d" failures="%d" errors="%d">%s</testsuite>'
                                                % (cls, len(cases_), sk, f, e, body))
    names = ["dendrogramPurityPermutationInvariant()", "tdcExactBranchPermutationInvariant()", "goldenValuesOnUnpermutedFixture()",
             E.TA_TEST, "tieRuleKeepsTheSameRepresentativeUnderBothInputOrders()", E.TDC_TEST,
             "sphericalSilhouettePermutationInvariant()", "mainFixtureIsNonDegenerate()"]
    xml(os.path.join(fixd, "TEST-%s.xml" % E.TEST_CLASS), E.TEST_CLASS, [(n, "PASSED") for n in names])
    xml(os.path.join(fixd, "TEST-taxonomy.MrlRoutingTest.xml"), "taxonomy.MrlRoutingTest",
        [("testMrlConfigDefaults()", "FAILED"), ("other()", "PASSED")])
    basex = os.path.join(WORK, "base.xml")
    xml(basex, E.TEST_CLASS, [(n, "PASSED" if n == "mainFixtureIsNonDegenerate()" else "FAILED") for n in names])
    _k = [0]

    def write_sums(st):
        lines = []
        for d, _s, fs in os.walk(st):
            for f in fs:
                rel = os.path.relpath(os.path.join(d, f), st).replace("\\", "/")
                if rel != "SHA256SUMS":
                    lines.append("%s *./%s\n" % (E.sha(os.path.join(d, f)), rel))
        open(os.path.join(st, "SHA256SUMS"), "w", encoding="utf-8", newline="\n").write("".join(sorted(lines)))

    def vcase(mut=None, after_sums=None):
        _k[0] += 1
        st = os.path.join(WORK, "vc%02d" % _k[0])
        shutil.copytree(VS, st)
        fd = os.path.join(st, "_fix")
        shutil.copytree(fixd, fd)
        bx = os.path.join(st, "_base.xml")
        shutil.copyfile(basex, bx)
        if mut:
            mut(st, fd, bx)
        write_sums(st)
        if after_sums:
            after_sums(st)
        out = os.path.join(st, "verdict.txt")
        rc, o = quiet(C.main, ["verdict", st, fd, bx, out])
        return rc, o, out

    def jedit(st, name, fn):
        p = os.path.join(st, name)
        d = json.load(open(p, encoding="utf-8"))
        fn(d)
        open(p, "w", encoding="utf-8").write(json.dumps(d))
    rc, o, out = vcase()
    check("T10a all criteria held, TDC(P1) != TDC(P2) in both files -> exit 0, DONE, MERGEABLE; MECHANISM SHOWN",
          rc == 0 and "DONE, MERGEABLE; MECHANISM SHOWN" in o and os.path.isfile(out), o[-600:])
    check("T10a' readouts printed: V1-V10 ALL MET, C1 0 of 6, C2 HELD, C3 HELD, C4 0 of 72, F1 / F2 not fired",
          "V1-V10 + TC: ALL MET" in o and "[TC] THREAD-CAP witness per leg" in o and "-> MET" in o and "0 of 6 comparisons differ" in o and "[C2] C2 HELD" in o and "C3 HELD" in o
          and "0 of 72 differ" in o and "[FALSIFIER F1 (FIX INCOMPLETE)] not fired" in o and "[FALSIFIER F2 (FIX LEAKS)] not fired" in o)
    for p_ in ("P1", "P2", "P3", "P4", "P5", "P8", "P9"):
        check("T10a'' prediction %s HELD printed" % p_, "[PREDICTION %s] HELD" % p_ in o)
    check("T10a''' P6 HELD on all three clauses (A vs B differ in TDC, DP, SS); P7 TDC(R1) != TDC(P1) FAILED (identical fixtures)",
          "TotalDasguptaCost(P1) != TotalDasguptaCost(P2) HELD" in o and "DendrogramPurity(P1) != DendrogramPurity(P2) HELD" in o
          and "SphericalSilhouette(P1) != SphericalSilhouette(P2) HELD" in o and "TDC(R1) != TDC(P1) FAILED" in o)
    rc, o, out = vcase()
    rc2, o2 = quiet(C.main, ["verdict", os.path.join(WORK, "vc%02d" % _k[0]), os.path.join(WORK, "vc%02d" % _k[0], "_fix"),
                             os.path.join(WORK, "vc%02d" % _k[0], "_base.xml"), out])
    check("T10b the verdict output is write-once", rc2 == 2 and "write-once" in o2)

    def same_p2(st, fd, bx):
        jedit(st, "leg_P2.json", lambda d: d.__setitem__("values", json.load(open(os.path.join(st, "leg_P1.json")))["values"]))
    rc, o, _ = vcase(same_p2)
    check("T10c TDC(P1) = TDC(P2) in both files -> DONE with the fallback words (drift did not reproduce); P6 FAILED",
          rc == 0 and "did not reproduce in this window" in o and "TotalDasguptaCost(P1) != TotalDasguptaCost(P2) FAILED" in o)

    def split_p2(st, fd, bx):
        def f(d):
            d["values"]["ledger:TotalDasguptaCost"] = json.load(open(os.path.join(st, "leg_P1.json")))["values"]["ledger:TotalDasguptaCost"]
        jedit(st, "leg_P2.json", f)
    rc, o, _ = vcase(split_p2)
    check("T10d TDC(P1) vs TDC(P2) differs in one file only -> UNMAPPED U3, exit 2", rc == 2 and "U3" in o)

    def p7_held(st, fd, bx):
        def f(d):
            v = d["values"]
            for src in ("quality", "ledger"):
                t = float(v[src + ":TotalDasguptaCost"])
                v[src + ":TotalDasguptaCost"] = repr(t * 1.005)
        jedit(st, "leg_R1.json", f)
    rc, o, _ = vcase(p7_held)
    check("T10e P7 all three clauses HELD (R1 TDC +0.5%, DP / SS equal)",
          "TDC(R1) != TDC(P1) HELD; |rel dTDC| <= 1.0% HELD; |dDP| <= 1e-13 and |dSS| <= 1e-15 HELD" in o)

    def p7_fail(st, fd, bx):
        def f(d):
            v = d["values"]
            for src in ("quality", "ledger"):
                v[src + ":TotalDasguptaCost"] = repr(float(v[src + ":TotalDasguptaCost"]) * 1.02)
                v[src + ":DendrogramPurity"] = repr(float(v[src + ":DendrogramPurity"]) + 1e-12)
        jedit(st, "leg_R1.json", f)
    rc, o, _ = vcase(p7_fail)
    check("T10f P7 |rel dTDC| and |dDP| clauses FAILED (+2%, +1e-12)",
          "|rel dTDC| <= 1.0% FAILED; |dDP| <= 1e-13 and |dSS| <= 1e-15 FAILED" in o)

    def f1(st, fd, bx):
        jedit(st, "c1_R1_R3.json", lambda d: d.__setitem__("differing", [E.QUALITY]))
    rc, o, _ = vcase(f1)
    check("T10g C1 FAILED (1 of 6) -> exit 3, FIX INCOMPLETE (F1), F1 FIRED printed, P1 FAILED",
          rc == 3 and "FIX INCOMPLETE (F1); no merge" in o and "F1 (FIX INCOMPLETE)] FIRED" in o and "[PREDICTION P1] FAILED" in o
          and "1 of 6 comparisons differ" in o)

    def f2(st, fd, bx):
        jedit(st, "c3_P1_R1.json", lambda d: d.__setitem__("differing", ["seed_42/diagnostics/proposals.csv"]))
    rc, o, _ = vcase(f2)
    check("T10h C3 FAILED -> exit 3, FIX LEAKS (F2), F2 FIRED printed, P3 FAILED",
          rc == 3 and "FIX LEAKS (F2); no merge" in o and "F2 (FIX LEAKS)] FIRED" in o and "[PREDICTION P3] FAILED" in o)
    rc, o, _ = vcase(lambda st, fd, bx: (f1(st, fd, bx), f2(st, fd, bx)))
    check("T10i C1 and C3 FAILED -> exit 3, recorded joined", rc == 3 and "recorded joined" in o)

    def c4f(st, fd, bx):
        jedit(st, "c4_R2_R3.json", lambda d: d.__setitem__("differing", [E.FILESET]))
    rc, o, _ = vcase(c4f)
    check("T10j C4 FAILED does not gate: exit 0 DONE, C4 FAILED and P4 FAILED printed",
          rc == 0 and "C4 FAILED" in o and "[PREDICTION P4] FAILED" in o)

    def c2void(st, fd, bx):
        xml(bx, E.TEST_CLASS, [(n, "PASSED") for n in names])
    rc, o, _ = vcase(c2void)
    check("T10k BASE passes TDC's permutation test -> exit 6, C2 VOID (a READY defect, not an outcome), P2 FAILED",
          rc == 6 and "C2 VOID" in o and "[PREDICTION P2] FAILED" in o)

    def ta_base_pass(st, fd, bx):
        xml(bx, E.TEST_CLASS, [(n, "PASSED" if n in (E.TA_TEST, "mainFixtureIsNonDegenerate()") else "FAILED") for n in names])
    rc, o, _ = vcase(ta_base_pass)
    check("T10l BASE fails TDC but passes TA -> C2 HELD, DONE, P2 FAILED (the TA clause)", rc == 0 and "[PREDICTION P2] FAILED" in o)

    def c2fail(st, fd, bx):
        xml(os.path.join(fd, "TEST-%s.xml" % E.TEST_CLASS), E.TEST_CLASS,
            [(n, "FAILED" if n == E.TDC_TEST else "PASSED") for n in names])
    rc, o, _ = vcase(c2fail)
    check("T10m FIX suite fails the golden test, C1 / C3 held -> UNMAPPED U2, exit 2", rc == 2 and "U2" in o)
    rc, o, _ = vcase(lambda st, fd, bx: (c2fail(st, fd, bx), c2void(st, fd, bx)))
    check("T10n C2 (i) and (ii) both fail -> UNMAPPED U1, exit 2", rc == 2 and "U1" in o)
    rc, o, _ = vcase(lambda st, fd, bx: (c2fail(st, fd, bx), f1(st, fd, bx)))
    check("T10o C1 FAILED with C2 FAILED -> exit 3 F1, the C2 state appended", rc == 3 and "C2 state: FAILED" in o)

    def unknown_fail(st, fd, bx):
        xml(os.path.join(fd, "TEST-taxonomy.OtherTest.xml"), "taxonomy.OtherTest", [("x()", "FAILED")])
    rc, o, _ = vcase(unknown_fail)
    check("T10p an unknown suite failure -> P8 FAILED (the verdict is not gated by it)", rc == 0 and "[PREDICTION P8] FAILED" in o)

    def slow(st, fd, bx):
        jedit(st, "leg_R2.json", lambda d: d.__setitem__("duration_ms", 70000))
    rc, o, _ = vcase(slow)
    check("T10q a leg duration above 60 s -> P9 FAILED, V8 still met", rc == 0 and "[PREDICTION P9] FAILED" in o)
    def list_differs(st, leg):
        p = os.path.join(st, "classlists", "leg%s_all.txt" % leg)
        open(p, "a", encoding="utf-8", newline="\n").write("build/classes/kotlin/main/taxonomy/Extra.class\n")
        h = E.sha(p)
        jedit(st, "leg_%s.json" % leg, lambda d: d.__setitem__("classlist_all_sha", h))

    def r3_list_differs(st, fd, bx):
        list_differs(st, "R3")

    def p2_list_differs(st, fd, bx):
        list_differs(st, "P2")
    voids = [
        ("V1 not met (prep)", lambda st, fd, bx: jedit(st, "emd_prep.json", lambda d: d.__setitem__("v1", False))),
        ("V2 not met (prep)", lambda st, fd, bx: jedit(st, "emd_prep.json", lambda d: d.__setitem__("v2", False))),
        ("V3: an R count differs", lambda st, fd, bx: jedit(st, "leg_R2.json", lambda d: d.__setitem__("x1_count", 2))),
        ("V3: a P count is 1", lambda st, fd, bx: jedit(st, "leg_P2.json", lambda d: d.__setitem__("x1_count", 1))),
        ("V3: the R class-name lists differ (recorded consistently)", r3_list_differs),
        ("V3: the P class-name lists differ (recorded consistently)", p2_list_differs),
        ("V3: a recorded class-list sha differs from its file", lambda st, fd, bx: jedit(st, "leg_R3.json", lambda d: d.__setitem__("classlist_all_sha", "0" * 64))),
        ("V3: a class list file tampered", lambda st, fd, bx: open(os.path.join(st, "classlists", "legR1_all.txt"), "a").write("x\n")),
        ("V4 failed in a leg", lambda st, fd, bx: jedit(st, "leg_R1.json", lambda d: d["checks"].__setitem__("V4", False))),
        ("V5 failed in a leg", lambda st, fd, bx: jedit(st, "leg_P1.json", lambda d: d["checks"].__setitem__("V5", False))),
        ("V6 failed in a leg", lambda st, fd, bx: jedit(st, "leg_R3.json", lambda d: d["checks"].__setitem__("V6", False))),
        ("V7: misses differ across legs", lambda st, fd, bx: jedit(st, "leg_P2.json", lambda d: d.__setitem__("misses", 3))),
        ("V8 failed in a leg", lambda st, fd, bx: jedit(st, "leg_R2.json", lambda d: d["checks"].__setitem__("V8", False))),
        ("V9 not met (post)", lambda st, fd, bx: jedit(st, "emd_post.json", lambda d: d.__setitem__("v9", False))),
        ("TC failed in a leg", lambda st, fd, bx: jedit(st, "leg_P2.json", lambda d: d["checks"].__setitem__("TC", False))),
        ("TC witness differs in one leg (check recorded True)", lambda st, fd, bx: jedit(st, "leg_R3.json", lambda d: d.__setitem__("thread_cap", ["requested=12 availableProcessors=11"]))),
        ("TC witness absent from a leg readout", lambda st, fd, bx: jedit(st, "leg_R1.json", lambda d: d.pop("thread_cap"))),
        ("TC witness 24/24 in ALL five legs (equal, but not the cap)", lambda st, fd, bx: [jedit(st, "leg_%s.json" % l_, lambda d: d.__setitem__("thread_cap", ["requested=24 availableProcessors=24"])) for l_ in E.LEGS]),
        ("V10: the golden test skipped in the FIX suite", lambda st, fd, bx: xml(os.path.join(fd, "TEST-%s.xml" % E.TEST_CLASS),
                                                                                E.TEST_CLASS, [(n, "SKIPPED") for n in names])),
    ]
    for name, fn in voids:
        rc, o, _ = vcase(fn)
        check("T10r %s -> exit 5 VOID" % name, rc == 5 and "[VERDICT] VOID" in o, o[-300:])
        if name == "V3: an R count differs":
            check("T10r' the same case scores P5 FAILED", "[PREDICTION P5] FAILED" in o)
    def drop_line(st, needle):
        p = os.path.join(st, "SHA256SUMS")
        keep = [ln for ln in open(p, encoding="utf-8") if needle not in ln]
        open(p, "w", encoding="utf-8", newline="\n").write("".join(keep))

    def wrong_sha(st, needle):
        p = os.path.join(st, "SHA256SUMS")
        out = [("0" * 64 + ln[64:]) if needle in ln else ln for ln in open(p, encoding="utf-8")]
        open(p, "w", encoding="utf-8", newline="\n").write("".join(out))
    for name, fn in (("SHA256SUMS absent", lambda st: os.remove(os.path.join(st, "SHA256SUMS"))),
                     ("a class list not listed in SHA256SUMS", lambda st: drop_line(st, "classlists/legR2_canonicalByRawText.txt")),
                     ("a leg readout listed with a wrong sha256", lambda st: wrong_sha(st, "leg_P2.json")),
                     ("a pair readout not listed", lambda st: drop_line(st, "c4_R1_R3.json"))):
        rc, o, _ = vcase(after_sums=fn)
        check("T10r'' V9 evidence clause: %s -> exit 5 VOID" % name, rc == 5 and "[VERDICT] VOID" in o, o[-300:])
    rc, o, _ = vcase(lambda st, fd, bx: (jedit(st, "leg_R1.json", lambda d: d["checks"].__setitem__("V4", False)), f1(st, fd, bx)))
    check("T10s V failed AND C1 FAILED -> VOID, F1 not fired", rc == 5 and "[FALSIFIER F1 (FIX INCOMPLETE)] not fired" in o)
    refusals = [
        ("a missing leg readout", lambda st, fd, bx: os.remove(os.path.join(st, "leg_R3.json"))),
        ("a missing c1 readout", lambda st, fd, bx: os.remove(os.path.join(st, "c1_R2_R3.json"))),
        ("a c3 readout made on other roots", lambda st, fd, bx: jedit(st, "c3_P1_R1.json", lambda d: d.__setitem__("roots", ["x", "y"]))),
        ("a leg readout on another root", lambda st, fd, bx: jedit(st, "leg_P1.json", lambda d: d.__setitem__("root", "elsewhere"))),
        ("a c4 readout of another version", lambda st, fd, bx: jedit(st, "c4_R1_R2.json", lambda d: d.__setitem__("version", "old"))),
        ("a differing object outside the declared list", lambda st, fd, bx: jedit(st, "c1_R1_R2.json", lambda d: d.__setitem__("differing", ["zzz"]))),
        ("a corrupt BASE XML", lambda st, fd, bx: open(bx, "w").write("<not xml")),
    ]
    for name, fn in refusals:
        rc, o, _ = vcase(fn)
        check("T10t verdict refuses: %s (exit 2)" % name, rc == 2 and "INSTRUMENT REFUSAL" in o, o[-200:])

    # ---- T11 emd_legrun.cmd with a stub gradlew.bat
    cmd = os.path.join(HDIR, "emd_legrun.cmd")
    lr = os.path.join(WORK, "lroot")
    os.makedirs(lr)
    open(os.path.join(lr, "gradlew.bat"), "w").write("@echo off\r\necho stub args %*\r\necho BUILD SUCCESSFUL in 1s\r\nexit /b %STUBRC%\r\n")
    lst = stage()

    def legrun(*a, rc_=0):
        env = dict(os.environ, STUBRC=str(rc_))
        r = subprocess.run(["cmd", "/c", cmd] + list(a), capture_output=True, text=True, env=env)
        return r.returncode, r.stdout + r.stderr
    rc, o = legrun("P1", lr, lst)
    log = os.path.join(lst, "legP1_bootrun.log")
    exf = os.path.join(lst, "legP1_exit.txt")
    logt = open(log).read() if os.path.isfile(log) else ""
    ext = open(exf).read() if os.path.isfile(exf) else ""
    check("T11a legrun P1: exit 0, the registered command line captured, START / EXIT 0 / END recorded",
          rc == 0 and "bootRun --console=plain --offline --no-build-cache -PjvmThreads=12 " in logt and "ratings_emd_P1.db" in logt
          and "--config experiment_configs/topic_partition/ag_news_smoke_s42.toml" in logt
          and re.search(r"START .*\nEXIT 0\nEND ", ext.replace("\r", "")) is not None, (rc, logt, ext))
    rc, o = legrun("P1", lr, lst)
    check("T11b legrun refuses an existing log (write-once)", rc == 2 and "refusing" in o)
    os.remove(exf)
    rc, o = legrun("P1", lr, lst)
    check("T11b' legrun refuses an existing log even without its exit file", rc == 2 and "refusing" in o)
    os.rename(log, log + ".moved")
    open(exf, "w").write("START x\n")
    rc, o = legrun("P1", lr, lst)
    check("T11b'' legrun refuses an existing exit file even without its log", rc == 2 and "refusing" in o)
    rc, o = legrun("R3", lr, lst, rc_=7)
    ext = open(os.path.join(lst, "legR3_exit.txt")).read()
    check("T11c legrun records the Gradle exit code (EXIT 7) and returns it", rc == 7 and "EXIT 7" in ext)
    for bad, why in ((("A", lr, lst), "leg A"), (("P3", lr, lst), "leg P3"), (("R1", lr, os.path.join(WORK, "nostage")), "absent stage"),
                     (("R1", lr, lst, "extra"), "a fourth argument"), (("R1",), "missing arguments")):
        rc, o = legrun(*bad)
        check("T11d legrun refuses %s" % why, rc == 2)

    n_ok = sum(ok for _n, ok in RESULTS)
    print("\n%d of %d cases as expected; %d mismatches" % (n_ok, len(RESULTS), len(RESULTS) - n_ok))
    return 0 if n_ok == len(RESULTS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
