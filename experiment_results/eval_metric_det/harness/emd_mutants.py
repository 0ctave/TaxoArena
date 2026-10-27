"""Mutation test of the EVAL-METRIC-DETERMINISM harness. Each mutant removes or weakens ONE check in a copy of the
instrument (emd_common, emd_compare, emd_leg_check, emd_prep, emd_legrun.cmd) and runs emd_selftest.py against that copy
(EMD_HARNESS_DIR); every mutant must be KILLED (selftest exit != 0). The unmutated copy must pass (exit 0). A mutation
pattern that does not occur exactly once is a RUNNER ERROR. Zero calls; nothing outside the temp copies is written.

usage: python emd_mutants.py [--only M07,M12]     exit 0 iff the baseline passes and every mutant is killed

RUN OF RECORD (re-cut eval-metric-det3, 2026-10-01; BASE 2f080e0 / FIX 6569cd3): baseline 184 of 184; M01-M97 (97 entries)
KILLED 97 of 97 (M01-M84 as before, M85-M97 new: the -PjvmThreads flag and its value, TC always / with no line / first line only /
requested only / outside the leg pass, the verdict TC per-leg / value / always, BASE reverted, cap 24, AG pin reverted). The first
run had one RUNNER ERROR (M86 pattern twice: the comment line); the pattern was narrowed and M86 re-run alone: KILLED.
"""
import os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FILES = ["emd_common.py", "emd_compare.py", "emd_leg_check.py", "emd_prep.py", "emd_legrun.cmd", "emd_selftest.py"]

M = [
    # emd_common
    ("M01", "emd_common.py", 'C1_PAIRS = (("R1", "R2"), ("R1", "R3"), ("R2", "R3"))', 'C1_PAIRS = (("R1", "R2"), ("R1", "R3"), ("R2", "R3"), ("P1", "R1"))', "C1 admits a P/R pair"),
    ("M02", "emd_common.py", "bad = [n for n, mine, theirs in checks if mine != theirs]", "bad = []", "list-equality assertion removed"),
    ("M03", "emd_common.py", "    if got != want:\n        raise Refuse(\"original %s", "    if False:\n        raise Refuse(\"original %s", "original pin check removed"),
    ("M04", "emd_common.py", 'X1 = "canonicalByRawText"', 'X1 = "canonicalByRawTextX"', "discriminator identifier altered"),
    ("M05", "emd_common.py", 'COMMIT = {"P1": BASE, "R1": FIX, "R2": FIX, "P2": BASE, "R3": FIX}', 'COMMIT = {"P1": BASE, "R1": FIX, "R2": FIX, "P2": FIX, "R3": FIX}', "P2 assigned FIX"),
    ("M06", "emd_common.py", 'LEGS = ("P1", "R1", "R2", "P2", "R3")', 'LEGS = ("P1", "P2", "R1", "R2", "R3")', "leg order changed"),
    ("M07", "emd_common.py", 'D9B_ROW_DROP = {"seed_42/validation/MAIN_taxonomy_quality.csv": ("Metric", DECLARED)}', 'D9B_ROW_DROP = {"seed_42/validation/MAIN_taxonomy_quality.csv": ("Metric", DECLARED + ["SeparationJ"])}', "C3 over-drops a row"),
    ("M08", "emd_common.py", 'C3_PAIRS = (("P1", "R1"),)', 'C3_PAIRS = (("P1", "R1"), ("R1", "R2"))', "C3 admits an R/R pair"),
    # emd_compare, pair mode
    ("M09", "emd_compare.py", '"c1": (E.C1_OBJECTS, list(E.C1_OBJECTS), {}, {}, "C1", E.C1_PAIRS),', '"c1": (E.C1_OBJECTS, [E.QUALITY], {E.LEDGER: ["CommitSHA"]}, {}, "C1", E.C1_PAIRS),', "C1 ledger without CommitSHA"),
    ("M10", "emd_compare.py", '"c1": (E.C1_OBJECTS, list(E.C1_OBJECTS), {}, {}, "C1", E.C1_PAIRS),', '"c1": (E.C1_OBJECTS, [E.LEDGER], {}, {E.QUALITY: ("Metric", E.DECLARED)}, "C1", E.C1_PAIRS),', "C1 quality CSV with D9b's row drop"),
    ("M11", "emd_compare.py", "    if (lx, ly) not in pairs:\n", "    if False:\n", "pair-label check removed"),
    ("M12", "emd_compare.py", 'status[E.FILESET] = "EQUAL" if not only else "DIFFERS"', 'status[E.FILESET] = "EQUAL"', "file set never differs"),
    ("M13", "emd_compare.py", 'status[t] = "EQUAL" if px_[t] == py_[t] else "DIFFERS"', 'status[t] = "EQUAL" if px_[t][0] == py_[t][0] else "DIFFERS"', "pool tables compared by row count only"),
    ("M14", "emd_compare.py", 'raise Refuse("listed file %s absent in BOTH legs (not comparable)" % rel)', 'status[rel] = "EQUAL"; digest[rel] = [None, None]; continue', "absent-in-both scored EQUAL"),
    ("M15", "emd_compare.py", "    for p in [txt, js] + pools:\n        if os.path.exists(p):", "    for p in [txt, js] + pools:\n        if False:", "write-once pre-check removed"),
    ("M16", "emd_compare.py", "        status[rel] = \"EQUAL\" if a == b else \"DIFFERS\"", "        status[rel] = \"EQUAL\"", "files never differ"),
    ("M17", "emd_compare.py", "    if not rows:\n        raise Refuse(\"empty file under a column drop\")\n", "", "empty-file refusal removed"),
    # emd_compare, verdict
    ("M18", "emd_compare.py", "    if fix_ok and base_tdc_fails:\n", "    if fix_ok:\n", "C2 HELD without the BASE failure"),
    ("M19", "emd_compare.py", 'V["V3"] = (lists_ok and all(x1[l] == 0 for l in E.P_LEGS) and ', 'V["V3"] = (lists_ok and ', "V3 P-count bar removed"),
    ("M20", "emd_compare.py", "and len(set(r_counts)) == 1 and len({alls[l] for l in E.R_LEGS}) == 1", "and len({alls[l] for l in E.R_LEGS}) == 1", "V3 R counts equality removed"),
    ("M21", "emd_compare.py", "and len({alls[l] for l in E.R_LEGS}) == 1 and len({alls[l] for l in E.P_LEGS}) == 1)", "and len({alls[l] for l in E.P_LEGS}) == 1)", "V3 R class-list equality removed"),
    ("M22", "emd_compare.py", "            ok = got is not None and got == legs[l].get(key + \"_sha\")", "            ok = True", "class-list file sha check removed"),
    ("M23", "emd_compare.py", 'V["V7"] = all(isinstance(m, int) for m in misses.values()) and len(set(misses.values())) == 1', 'V["V7"] = True', "V7 removed"),
    ("M24", "emd_compare.py", 'V["V9"] = post.get("v9") is True', 'V["V9"] = True', "V9 ignored"),
    ("M25", "emd_compare.py", 'V["V1"] = prep.get("v1") is True', 'V["V1"] = True', "V1 ignored"),
    ("M26", "emd_compare.py", 'V["V10"] = len(fmine) > 0 and not any(s == "SKIPPED" for _c, _n, s in fmine) and len(bmine) > 0', 'V["V10"] = len(fmine) > 0 and len(bmine) > 0', "V10 skip check removed"),
    ("M27", "emd_compare.py", "    f1 = vmet and not c1_held\n", "    f1 = False\n", "F1 never fires"),
    ("M28", "emd_compare.py", "    f2 = vmet and not c3_held\n", "    f2 = False\n", "F2 never fires"),
    ("M29", "emd_compare.py", "        if states == {True}:\n", "        if True:\n", "mechanism words always"),
    ("M30", "emd_compare.py", "        if len(states) != 1:\n", "        if False:\n", "U3 refusal removed"),
    ("M31", "emd_compare.py", '    elif c2 == "FAILED":\n', '    elif c2 == "FAILEDX":\n', "U2 refusal removed"),
    ("M32", "emd_compare.py", '    elif c2 == "UNMAPPED":\n', '    elif c2 == "UNMAPPEDX":\n', "U1 refusal removed"),
    ("M33", "emd_compare.py", "        if j[\"roots\"] != [roots[lx], roots[ly]]:\n", "        if False:\n", "readout-root consistency removed"),
    ("M34", "emd_compare.py", '        if legs[l].get("root") != roots[l]:\n', "        if False:\n", "leg-root consistency removed"),
    ("M35", "emd_compare.py", 'P["P8"] = "HELD" if (fails <= E.KNOWN_FAILURES and V["V1"]) else "FAILED"', 'P["P8"] = "HELD"', "P8 always held"),
    ("M36", "emd_compare.py", "E.P9_DUR_MS[0] <= d <= E.P9_DUR_MS[1]", "E.P9_DUR_MS[0] <= d", "P9 upper bound removed"),
    ("M37", "emd_compare.py", 'and bstate.get(E.TA_TEST) == "FAILED") else "FAILED"', ') else "FAILED"', "P2 TA clause removed"),
    ("M38", "emd_compare.py", "<= E.MARGIN_TDC)", "<= 1.0)", "P7 margin 100%"),
    ("M39", "emd_compare.py", "and len(j[\"roots\"]) == 2 and set(j[\"differing\"]) <= set(objects))", "and len(j[\"roots\"]) == 2)", "readout differing-subset check removed"),
    ("M40", "emd_compare.py", "    c3_held = not c3_d\n", "    c3_held = True\n", "C3 always held"),
    ("M41", "emd_compare.py", "    c1_held = n_c1 == 0\n", "    c1_held = True\n", "C1 always held"),
    ("M42", "emd_compare.py", "    if not vmet:\n        rc, v = 5,", "    if False:\n        rc, v = 5,", "VOID branch removed"),
    # emd_leg_check
    ("M43", "emd_leg_check.py", 'checks["V3"] = (x1n == 0) if leg in E.P_LEGS else (x1n >= 1)', 'checks["V3"] = True if leg in E.P_LEGS else (x1n >= 1)', "V3 P bar removed"),
    ("M44", "emd_leg_check.py", 'checks["V3"] = (x1n == 0) if leg in E.P_LEGS else (x1n >= 1)', 'checks["V3"] = (x1n == 0) if leg in E.P_LEGS else True', "V3 R bar removed"),
    ("M45", "emd_leg_check.py", "and len(after) >= 1\n", "\n", "V4 after-bootRun removed"),
    ("M46", "emd_leg_check.py", "j.lower() == want.lower()", "True", "V4 jar equality removed"),
    ("M47", "emd_leg_check.py", 'checks["V5"] = "> Task :compileKotlin" in ck and len(ck) == 1', 'checks["V5"] = len(ck) == 1', "V5 executed-state removed"),
    ("M48", "emd_leg_check.py", '    ok6 &= bool(exits) and exits[-1] == "0"\n', "", "V6 exit code removed"),
    ("M49", "emd_leg_check.py", " and m.get(\"commit\") == E.COMMIT[leg]", "", "V6 commit removed"),
    ("M50", "emd_leg_check.py", " and m.get(\"dirty\") is False", "", "V6 dirty removed"),
    ("M51", "emd_leg_check.py", "        ok6 &= n >= 1\n", "", "V6 sanity lines removed"),
    ("M52", "emd_leg_check.py", 'ok6 = "BUILD SUCCESSFUL" in tx and "BUILD FAILED" not in tx', 'ok6 = "BUILD SUCCESSFUL" in tx', "V6 BUILD FAILED removed"),
    ("M53", "emd_leg_check.py", "0 < dur < E.CEIL_S * 1000", "0 < dur", "V8 duration ceiling removed"),
    ("M54", "emd_leg_check.py", "and gs is not None and gs < E.CEIL_S and rows >= 1)", "and gs is not None and rows >= 1)", "V8 Gradle ceiling removed"),
    ("M55", "emd_leg_check.py", "and gs is not None and gs < E.CEIL_S and rows >= 1)", "and gs is not None and gs < E.CEIL_S)", "V8 rows removed"),
    ("M56", "emd_leg_check.py", 'ok6 &= m.get("exit_reason") == "completed" and', "ok6 &= ", "V6 exit_reason removed"),
    ("M57", "emd_leg_check.py", 'miss = sum(int(x) for x in re.findall(r"Computing and caching embeddings for (\\d+) new queries", hl))', "miss = 0", "V7 misses not counted"),
    # emd_prep
    ("M58", "emd_prep.py", "    if diff != sorted(E.FIX_SRC):\n", "    if False:\n", "V1 src diff check removed"),
    ("M59", "emd_prep.py", "        if got != b:\n", "        if False:\n", "V1 FIX blob pin removed"),
    ("M60", "emd_prep.py", "    if [ln.split(None, 1) for ln in tst] != [[\"A\", E.TEST_PATH]]:\n", "    if False:\n", "V1 test status removed"),
    ("M61", "emd_prep.py", "    if got != E.TEST_BLOB:\n", "    if False:\n", "V1 test blob removed"),
    ("M62", "emd_prep.py", "    if other:\n", "    if False:\n", "V1 tools/configs removed"),
    ("M63", "emd_prep.py", "        if b != E.TOML_BLOB:\n", "        if False:\n", "V1 TOML removed"),
    ("M64", "emd_prep.py", "    if moved:\n", "    if False:\n", "V1 main-moved removed"),
    ("M65", "emd_prep.py", "        if head != E.COMMIT[leg] or not os.path.isfile(os.path.join(root, \".git\")) or st:\n", "        if not os.path.isfile(os.path.join(root, \".git\")):\n", "leg HEAD / status removed"),
    ("M66", "emd_prep.py", '"ratings_emd_%s.db" % leg, "build"):', '"ratings_emd_%s.db" % leg):', "fresh-worktree build/ check removed"),
    ("M67", "emd_prep.py", '"snapshots.db", "ratings_emd_%s.db" % leg, "build"):', '"snapshots.db", "build"):', "fresh-worktree ratings check removed"),
    ("M68", "emd_prep.py", "    if not eq:\n        die(\"main embeddings_cache.db differs from its pin\")", "    if False:\n        die(\"main embeddings_cache.db differs from its pin\")", "embeddings pin removed"),
    ("M69", "emd_prep.py", " and b[\"views\"].get(n) == a[\"views\"].get(n)\n", "\n", "V9 views removed"),
    ("M70", "emd_prep.py", "fb[0] == fa[0] and fb[2] == fa[2] and", "fb[0] == fa[0] and", "V9 file sha removed"),
    ("M71", "emd_prep.py", "        eq = fb is not None and fb == fa\n", "        eq = fb is not None and fb[0::2] == fa[0::2]\n", "V9 AG mtime removed"),
    # emd_legrun.cmd
    ("M72", "emd_legrun.cmd", 'if exist "%LOG%" (echo [RUN] refusing: %LOG% exists & exit /b 2)\r\n', "", "legrun write-once removed"),
    ("M73", "emd_legrun.cmd", '"-Dranking.db.path=ratings_emd_%L%.db"', '"-Dranking.db.path=ratings_d9_%L%.db"', "legrun ratings name"),
    ("M74", "emd_legrun.cmd", "bootRun --console=plain --offline --no-build-cache", "bootRun --console=plain --offline", "legrun --no-build-cache removed"),
    ("M75", "emd_legrun.cmd", "for %%x in (P1 R1 R2 P2 R3)", "for %%x in (P1 R1 R2 P2 R3 A)", "legrun admits leg A"),
    ("M76", "emd_legrun.cmd", "exit /b %RC%", "exit /b 0", "legrun exit code dropped"),
    ("M78", "emd_legrun.cmd", 'if exist "%EXF%" (echo [RUN] refusing: %EXF% exists & exit /b 2)\r\n', "", "legrun exit-file write-once removed"),
    ("M79", "emd_compare.py", "and len({alls[l] for l in E.P_LEGS}) == 1)", ")", "V3 P class-list equality removed"),
    ("M80", "emd_compare.py", 'V["V9"] = post.get("v9") is True and sums_ok', 'V["V9"] = post.get("v9") is True', "V9 SHA256SUMS clause removed"),
    ("M81", "emd_compare.py", 'else "own sha256" if h in got else "WRONG sha256")', 'else "own sha256")', "SHA256SUMS sha comparison removed"),
    ("M82", "emd_leg_check.py", "0 < dur < E.CEIL_S * 1000", "0 < dur <= E.CEIL_S * 1000", "V8 duration bar not strict"),
    ("M83", "emd_leg_check.py", "and gs is not None and gs < E.CEIL_S and rows >= 1)", "and gs is not None and gs <= E.CEIL_S and rows >= 1)", "V8 Gradle bar not strict"),
    ("M84", "emd_leg_check.py", r'    if not toks or re.sub(r"\s*\d+(?:ms|h|m|s)(?![A-Za-z])\s*", "", t):', "    if not toks:", "Gradle time leftover check removed"),
    # re-cut 2026-09-30 (B-EM-1): the THREAD-CAP witness, the pins
    ("M85", "emd_legrun.cmd", "--no-build-cache -PjvmThreads=12 ", "--no-build-cache ", "legrun -PjvmThreads removed"),
    ("M86", "emd_legrun.cmd", "--no-build-cache -PjvmThreads=12 \"-Dranking", "--no-build-cache -PjvmThreads=24 \"-Dranking", "legrun -PjvmThreads=24"),
    ("M87", "emd_leg_check.py", 'checks["TC"] = bool(caps) and all(', 'checks["TC"] = True or all(', "TC always passes"),
    ("M88", "emd_leg_check.py", 'checks["TC"] = bool(caps) and all(', 'checks["TC"] = all(', "TC passes with no witness line"),
    ("M89", "emd_leg_check.py", "all(c == (str(E.THREAD_CAP_N), str(E.THREAD_CAP_N)) for c in caps)", "caps[:1] == [(str(E.THREAD_CAP_N), str(E.THREAD_CAP_N))]", "TC first line only"),
    ("M90", "emd_leg_check.py", "all(c == (str(E.THREAD_CAP_N), str(E.THREAD_CAP_N)) for c in caps)", "all(c[0] == str(E.THREAD_CAP_N) for c in caps)", "TC requested only (availableProcessors unchecked)"),
    ("M91", "emd_leg_check.py", 'for k in ("V3", "V4", "V5", "V6", "V8", "TC"))\n', 'for k in ("V3", "V4", "V5", "V6", "V8"))\n', "TC not in the leg pass"),
    ("M92", "emd_compare.py", 'V["TC"] = (all(legs[l]["checks"].get("TC") is True for l in E.LEGS) and ', 'V["TC"] = (', "verdict ignores per-leg TC"),
    ("M93", "emd_compare.py", " and all(tcs[l] == [E.TC_WITNESS] for l in E.LEGS)\n", "\n", "verdict: witness value unchecked (equality only)"),
    ("M94", "emd_compare.py", '    V["TC"] = (all(', '    V["TC"] = True or (all(', "verdict TC always met"),
    ("M95", "emd_common.py", 'BASE = "2f080e079f79c62c3a38337005438c6a310be81b"', 'BASE = "8bf15dac1d726940686927c8bf7b36020e4e11b8"', "BASE reverted to 8bf15da"),
    ("M96", "emd_common.py", "THREAD_CAP_N = 12 ", "THREAD_CAP_N = 24 ", "cap constant 24"),
    ("M97", "emd_common.py", '"ag_news_smoke_cache_v1.db": (1748992,', '"ag_news_smoke_cache_v1.db": (1622016,', "AG pin reverted to D9b size"),
    ("M77", "emd_legrun.cmd", 'if not "%~4"=="" (echo [RUN] refusing: exactly three arguments & exit /b 2)\r\n', "", "legrun argument count"),
]


def run_selftest(d, work):
    env = dict(os.environ, EMD_HARNESS_DIR=d, EMD_REPO=REPO)
    r = subprocess.run([sys.executable, os.path.join(d, "emd_selftest.py"), "--selftest", "--work", work],
                       capture_output=True, text=True, env=env)
    tail = [ln for ln in r.stdout.splitlines() if "cases as expected" in ln]
    return r.returncode, tail[-1] if tail else (r.stdout + r.stderr).strip().splitlines()[-1:] or ["?"]


def main(argv):
    only = set(argv[argv.index("--only") + 1].split(",")) if "--only" in argv else None
    root = tempfile.mkdtemp(prefix="emd_mut_")
    base = os.path.join(root, "base")
    os.makedirs(base)
    for f in FILES:
        shutil.copyfile(os.path.join(HERE, f), os.path.join(base, f))
    rc, tail = run_selftest(base, os.path.join(root, "w_base"))
    print("[BASELINE] unmutated copy: selftest exit %d (%s)" % (rc, tail), flush=True)
    ok = rc == 0
    killed = survived = errors = 0
    for mid, f, old, new, what in M:
        if only and mid not in only:
            continue
        d = os.path.join(root, mid)
        shutil.copytree(base, d)
        p = os.path.join(d, f)
        raw = open(p, "rb").read().decode("utf-8")
        n = raw.count(old)
        if n != 1:
            print("[%s] RUNNER ERROR: pattern occurs %d times in %s (%s)" % (mid, n, f, what), flush=True)
            errors += 1
            continue
        open(p, "wb").write(raw.replace(old, new).encode("utf-8"))
        rc, tail = run_selftest(d, os.path.join(root, "w_" + mid))
        k = rc != 0
        killed += k
        survived += not k
        print("[%s] %-8s %-16s %-44s selftest exit %d (%s)" % (mid, "KILLED" if k else "SURVIVED", f, what, rc, tail), flush=True)
        shutil.rmtree(d, ignore_errors=True)
        shutil.rmtree(os.path.join(root, "w_" + mid), ignore_errors=True)
    total = killed + survived + errors
    print("\n[MUTANTS] %d run: %d killed, %d survived, %d runner errors; baseline %s"
          % (total, killed, survived, errors, "PASS" if ok else "FAIL"))
    shutil.rmtree(root, ignore_errors=True)
    return 0 if ok and survived == 0 and errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
