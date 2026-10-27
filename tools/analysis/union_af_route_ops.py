"""union_af_route_ops.py: the run-operator's path through the AF-U build of UNION-AF-ROUTE (RP13) under THE AUTHOR's
"one cell per unsplit member" (2026-10-03; programme L23660-L23667, section "## Author's decision 2026-10-03 ... UNION-AF-ROUTE
(RP13): "one cell per unsplit member": ..."). ZERO calls; it never starts a JVM: it classifies a finished member build, keeps
the one-cell declaration, and fills the flatLeaf graft TOML. Readers: union_af_route.py (single_evidence, the registered
constants) is imported and pinned.

  python tools/analysis/union_af_route_ops.py --plan               # the documented sequence (below), printed
  python tools/analysis/union_af_route_ops.py --member <member>    # after the member's build: rc 0 BUILT (snapshot id printed),
                                                                   #   rc 3 ONE-CELL (verified, declaration appended), rc 1 STOP
  python tools/analysis/union_af_route_ops.py --fill               # graft_flatleaf.toml from the template, one-cell members omitted
  python tools/analysis/union_af_route_ops.py --selftest | --mutants

THE SEQUENCE (the build procedure's continuation that replaces READY_union_af_route step 1's STOP; it needs the delta READY):
  1. Preconditions P1-P6 of READY_union_af_route (rule 7 W1-W5, the backup and per-table hashes, the B0-2 pool check with
     TAXOARENA_DATA_ROOT = main, one detached worktree pinned at ONE commit for every member and the graft: D-8).
  2. For each member in the order of the READY (ifeval, gpqa, musr, math, bbh, mmlu_pro_lb; READY_union_af_route L118):
       .\\gradlew.bat bootRun --console=plain -q --offline -PjvmThreads=12 --args="--config experiment_configs/union_af_route/AF-U/<member>.toml" 2>&1 | Tee-Object experiment_results/archv2/union_af_route/AF-U/<member>/build.log
     (the console MUST be teed to AF-U/<member>/build.log: the single-leaf IllegalStateException is printed there only)
       python tools/analysis/union_af_route_ops.py --member <member>
     The JVM's exit code does not decide (a single-leaf refusal exits non-zero by design); --member does:
       rc 0 BUILT     the log names "Snapshot ID: <id>"                                -> next member
       rc 3 ONE-CELL  the log carries the [ANCHOR-FREE] single-leaf refusal AND union_af_route.single_evidence verifies S1-S6
                      (anchor_free, the TOML's LF sha, no snapshot, every root GROW row NO_PROPOSAL min_pair_sep_below_bar with
                      sep < bar 0.025) -> the member is appended to experiment_results/archv2/union_af_route/AF-U/
                      single_cell_members.json (append-only; an existing entry is never changed) -> next member
       rc 1 STOP      anything else (another failure, an unverifiable refusal, a member already declared that now has a
                      snapshot) -> STOP, nothing else runs; report.
     A member that refuses keeps its outputDir as the evidence (do not delete or move it before the reader has run).
  3. python tools/analysis/union_af_route_ops.py --fill  -> experiment_configs/union_af_route/AF-U/graft_flatleaf.toml
     (write-once): the BUILT members' snapshot ids filled; every ONE-CELL member's placeholder line and its corpus REMOVED from
     unionSnapshots and corpora (the engine's assembleUnion requires corpora == the grafted members' sources, and its v2
     checkUnionMembers has no coverage requirement, so a 5-member graft needs NO engine change); refused if D-8 fails, a BUILT
     member has no snapshot id, or every member is one-cell.
  4. The graft build:  .\\gradlew.bat bootRun ... --args="--config experiment_configs/union_af_route/AF-U/graft_flatleaf.toml"
     Its readout covers the BUILT members only; the reader adds each one-cell member's items to its one cell (by source).
  5. The reader: union_af_route.py --dry-run, --build-inputs, --dry-run, --run (READY_union_af_route's launch sequence).

SELFTEST / MUTANTS: see CASES and MUTANTS at the bottom (--mutants prints the table; the commit message carries the result).
"""
import os
import sys
import re
import io
import json
import argparse
import contextlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import union_af_route as U    # noqa: E402  (pins its readers; sets the thread variables)

TAG = "[RP13-OPS]"
TEMPLATE = "graft_flatleaf.toml.tmpl"
SNAP_RE = r"Snapshot ID:\s*(\S+)"


def refuse(msg):
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def member_paths(member):
    c = U.reg()
    base = "%s/%s/seed_42" % (c["afu"], member)
    return dict(log=base + "/headless_run.log", manifest=base + "/diagnostics/run_manifest.json", base=base,
                console="%s/%s/build.log" % (c["afu"], member))


def snapshot_id(member):
    p = U.P(member_paths(member)["log"])
    if not os.path.isfile(p):
        return None, None
    log = U.read_text(p)
    ids = re.findall(SNAP_RE, log)
    return (ids[-1] if ids else None), log


def read_decl():
    p = U.P(U.reg()["single_decl"])
    if not os.path.isfile(p):
        return dict(test=U.TEST_ID, decision="THE AUTHOR's \"one cell per unsplit member\", 2026-10-03, programme L23660-L23667",
                    members=[])
    return json.load(open(p, encoding="utf-8"))


def append_decl(entry):
    """Append-only: an existing entry for the member must be identical (re-classification is idempotent), never changed."""
    d = read_decl()
    for e in d["members"]:
        if e["member"] == entry["member"]:
            if e != entry:
                refuse("the declaration already holds %s as %s; the new evidence gives %s (an entry is never changed)" % (
                    entry["member"], e, entry))
            return d, False
    d["members"].append(entry)
    p = U.P(U.reg()["single_decl"])
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp"
    with open(tmp, "x", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(d, indent=1, sort_keys=True) + "\n")
    os.replace(tmp, p)
    return d, True


def classify(member, out=print):
    """-> 0 BUILT, 3 ONE-CELL (declared), 1 STOP; prints one verdict line."""
    c = U.reg()
    names = dict(c["members"])
    if member not in names:
        refuse("%s is not a registered AF-U member %s" % (member, sorted(names)))
    src = names[member]
    sid, log = snapshot_id(member)
    declared = [e for e in read_decl()["members"] if e["member"] == member]
    if log is None:
        out("%s STOP %s: no headless_run.log at %s (the build did not run or wrote elsewhere)" % (TAG, member, member_paths(member)["log"]))
        return 1
    if sid is not None:
        if declared:
            out("%s STOP %s: the log names snapshot %s but the member is DECLARED one-cell" % (TAG, member, sid))
            return 1
        if not os.path.isfile(U.P(member_paths(member)["manifest"])):
            out("%s STOP %s: snapshot %s but no run_manifest.json" % (TAG, member, sid))
            return 1
        out("%s BUILT %s: snapshot %s -> next member" % (TAG, member, sid))
        return 0
    cp = U.P(member_paths(member)["console"])
    con = U.read_text(cp) if os.path.isfile(cp) else ""
    if U.REFUSAL_LINE not in con:
        out("%s STOP %s: no snapshot and no [ANCHOR-FREE] single-leaf refusal in the console log %s (another failure)" % (
            TAG, member, member_paths(member)["console"]))
        return 1
    try:
        ev = U.single_evidence(member, src)
    except SystemExit as e:
        out("%s STOP %s: the single-leaf refusal is not verifiable: %s" % (TAG, member, e))
        return 1
    entry = dict(member=member, source=src, best_root_sep=round(ev["best_sep"], 5), n_site=ev["n_site"], bar=c["bar"],
                 root=ev["root"], rows=ev["rows"], declared_by="union_af_route_ops.py --member %s" % member)
    _d, new = append_decl(entry)
    out("%s ONE-CELL %s (%s): no anchor-free split clears the bar (best root separation %.5f < %s, n %d, %d NO_PROPOSAL rows);"
        " declaration %s %s -> next member" % (TAG, member, src, ev["best_sep"], c["bar"], ev["n_site"], ev["rows"], c["single_decl"],
                                               "appended" if new else "already held (identical)"))
    return 3


def fill(out=print):
    """graft_flatleaf.toml (write-once) from the template: BUILT members filled, ONE-CELL members removed from unionSnapshots
    and corpora."""
    c = U.reg()
    tpl = U.P("%s/%s" % (c["tomls"], TEMPLATE))
    dest = tpl[:-len(".tmpl")]
    if os.path.exists(dest):
        refuse("%s exists (write-once)" % dest)
    single = {e["source"]: e["member"] for e in read_decl()["members"]}
    commits, ids = {}, {}
    for m, src in c["members"]:
        mp = U.P(member_paths(m)["manifest"])
        if not os.path.isfile(mp):
            refuse("member %s has no run_manifest.json" % m)
        commits[m] = json.load(open(mp, encoding="utf-8")).get("commit")
        if src in single:
            U.single_evidence(m, src)                         # re-verified at fill time
            continue
        sid, _log = snapshot_id(m)
        if sid is None:
            refuse("BUILT member %s has no snapshot id in its log (nor a one-cell declaration)" % m)
        if '"' in sid or "__SNAP_" in sid:
            refuse("snapshot id %r of %s" % (sid, m))
        ids[src] = sid
    if len(set(commits.values())) != 1:
        refuse("D-8: the members were built at %d commits %s" % (len(set(commits.values())), sorted(set(map(str, commits.values())))))
    if not ids:
        refuse("every member is one-cell: there is no graft")
    text = open(tpl, "rb").read().replace(b"\r\n", b"\n").decode("utf-8")
    m_ = re.search(r"(?ms)^unionSnapshots = \[\n(.*?)\n\]\n", text)
    c_ = re.search(r"(?m)^corpora(\s*)= \[(.*?)\]$", text)
    if not m_ or not c_:
        refuse("the template has no unionSnapshots block or corpora line")
    order = re.findall(r'"__SNAP_([A-Z_]+)__"', m_.group(1))
    corp = re.findall(r'"([A-Z_]+)"', c_.group(2))
    if order != corp or set(order) != {s for _m, s in c["members"]}:
        refuse("template order unionSnapshots %s / corpora %s is not the registered members' sources" % (order, corp))
    keep = [s for s in order if s not in single]
    block = "unionSnapshots = [\n" + ",\n".join('    "%s"' % ids[s] for s in keep) + "\n]\n"
    text = text[:m_.start()] + block + text[m_.end():]
    c_ = re.search(r"(?m)^corpora(\s*)= \[(.*?)\]$", text)
    text = text[:c_.start()] + "corpora%s= [%s]" % (c_.group(1), ", ".join('"%s"' % s for s in keep)) + text[c_.end():]
    if "__SNAP_" in text:
        refuse("a placeholder is left")
    head = ("# FILLED by tools/analysis/union_af_route_ops.py --fill: BUILT %s; ONE-CELL (omitted from the graft, filed by source by"
            " the reader; THE AUTHOR's decision 2026-10-03, programme L23660-L23667): %s; build commit %s\n" % (
                ", ".join("%s=%s" % (s, ids[s]) for s in keep), ", ".join(sorted(single)) or "none", list(commits.values())[0]))
    with open(dest, "x", encoding="utf-8", newline="\n") as f:
        f.write(head + text)
    out("%s FILLED %s: %d members grafted (%s), one-cell omitted: %s" % (TAG, dest, len(keep), ", ".join(keep), ", ".join(sorted(single)) or "none"))
    return dest


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--plan", action="store_true")
    g.add_argument("--member")
    g.add_argument("--fill", action="store_true")
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--mutants", action="store_true")
    a = ap.parse_args(argv)
    if a.plan:
        print(__doc__[__doc__.index("THE SEQUENCE"):__doc__.index("SELFTEST / MUTANTS")])
        return 0
    if a.selftest:
        selftest()
        return 0
    if a.mutants:
        return run_mutants()
    if a.member:
        return classify(a.member)
    fill()
    return 0


# ── selftest ────────────────────────────────────────────────────────────────────────────────────────────────────────────

def _layout(tmp):
    """Three fixture members (union_af_route's FX_MEMBERS): bbh BUILT, math ONE-CELL, mmlu BUILT; the template."""
    reg = dict(U.REG, members=U.FX_MEMBERS, sources=U.FX_SOURCES, afu="res/AF-U", tomls="res/tomls",
               single_decl="res/AF-U/single_cell_members.json")
    for m, so in U.FX_MEMBERS:
        d = os.path.join(tmp, "res", "AF-U", m, "seed_42", "diagnostics")
        os.makedirs(d, exist_ok=True)
        if so == "MATH":
            continue
        with open(os.path.join(tmp, "res", "AF-U", m, "seed_42", "headless_run.log"), "w", encoding="utf-8") as f:
            f.write("x\n09:39:52 [INFO ] HeadlessRunner - Successfully generated and saved snapshot. Snapshot ID: SID_%s\n" % so)
        with open(os.path.join(d, "run_manifest.json"), "w", encoding="utf-8") as f:
            json.dump(dict(commit="fixturecommit0"), f)
    U._fx_single_evidence(tmp, "res/AF-U", "math", "MATH")
    os.makedirs(os.path.join(tmp, "res", "tomls"), exist_ok=True)
    with open(os.path.join(tmp, "res", "tomls", TEMPLATE), "w", encoding="utf-8", newline="\n") as f:
        f.write("# template\nunionSnapshots = [\n    \"__SNAP_BBH__\",\n    \"__SNAP_MATH__\",\n    \"__SNAP_MMLU_PRO__\"\n]\n"
                "corpora      = [\"BBH\", \"MATH\", \"MMLU_PRO\"]\nunionRootRouting    = \"flatLeaf\"\n")
    return reg


@contextlib.contextmanager
def _env(tmp, reg):
    saved = (U._ROOT[0], U._REG[0])
    U._ROOT[0], U._REG[0] = tmp, reg
    try:
        yield
    finally:
        U._ROOT[0], U._REG[0] = saved


def st_classify(tmp):
    reg = _layout(tmp)
    lines = []
    with _env(tmp, reg):
        assert classify("bbh", lines.append) == 0 and "BUILT bbh: snapshot SID_BBH" in lines[-1], lines
        assert classify("math", lines.append) == 3 and "ONE-CELL math (MATH): no anchor-free split clears the bar (best root" \
            " separation 0.02111 < 0.025, n 450, 3 NO_PROPOSAL rows)" in lines[-1] and "appended" in lines[-1], lines[-1]
        d = read_decl()
        assert [(e["member"], e["source"], e["best_root_sep"], e["n_site"]) for e in d["members"]] == [("math", "MATH", 0.02111, 450)]
        assert classify("math", lines.append) == 3 and "already held (identical)" in lines[-1]
        # a changed entry is refused (append-only)
        e = dict(d["members"][0], best_root_sep=0.01)
        try:
            append_decl(e)
            raise AssertionError("an entry was changed")
        except SystemExit as x:
            assert "an entry is never changed" in str(x)
        # the declaration feeds the reader: U.declared_single / load_single verify it
        sv = U.load_single(lambda s: None, U.declared_single())
        assert set(sv) == {"MATH"} and "%.5f" % sv["MATH"]["best_sep"] == "0.02111"
        # STOP cases: no log; another failure; an unverifiable refusal (an ACCEPTED row); a declared member with a snapshot
        os.remove(os.path.join(tmp, "res", "AF-U", "mmlu", "seed_42", "headless_run.log"))
        assert classify("mmlu", lines.append) == 1 and "no headless_run.log" in lines[-1]
        with open(os.path.join(tmp, "res", "AF-U", "mmlu", "seed_42", "headless_run.log"), "w") as f:
            f.write("x\n")
        with open(os.path.join(tmp, "res", "AF-U", "mmlu", "build.log"), "w") as f:
            f.write("java.lang.OutOfMemoryError\n")
        assert classify("mmlu", lines.append) == 1 and "another failure" in lines[-1]
        U._fx_single_evidence(tmp, "res/AF-U", "mmlu", "MMLU_PRO", decision="REJECTED")
        assert classify("mmlu", lines.append) == 1 and "not verifiable" in lines[-1] and "S3" in lines[-1]
        U._fx_single_evidence(tmp, "res/AF-U", "math", "MATH", snapshot=True)
        assert classify("math", lines.append) == 1 and "DECLARED one-cell" in lines[-1]


def st_fill(tmp):
    reg = _layout(tmp)
    with _env(tmp, reg):
        assert classify("math", lambda s: None) == 3
        dest = fill(lambda s: None)
        t = open(dest, encoding="utf-8").read()
        assert t.splitlines()[0].startswith("# FILLED by tools/analysis/union_af_route_ops.py --fill: BUILT BBH=SID_BBH, MMLU_PRO=SID_MMLU_PRO;"
                                           " ONE-CELL (omitted") and "MATH; build commit fixturecommit0" in t.splitlines()[0]
        assert 'unionSnapshots = [\n    "SID_BBH",\n    "SID_MMLU_PRO"\n]\ncorpora      = ["BBH", "MMLU_PRO"]\nunionRootRouting' in t, t
        assert "MATH" not in t.split("\n", 1)[1] and "__SNAP_" not in t
        try:
            fill(lambda s: None)
            raise AssertionError("fill overwrote")
        except SystemExit as x:
            assert "write-once" in str(x)


def st_fill_refusals(tmp_factory):
    # a BUILT member without a snapshot id (and no declaration)
    tmp = tmp_factory()
    reg = _layout(tmp)
    with _env(tmp, reg):
        try:
            fill(lambda s: None)
            raise AssertionError("fill accepted an undeclared member without a snapshot")
        except SystemExit as x:
            assert "BUILT member math has no snapshot id" in str(x), x
    # D-8
    tmp = tmp_factory()
    reg = _layout(tmp)
    with _env(tmp, reg):
        classify("math", lambda s: None)
        with open(os.path.join(tmp, "res", "AF-U", "bbh", "seed_42", "diagnostics", "run_manifest.json"), "w") as f:
            json.dump(dict(commit="other"), f)
        try:
            fill(lambda s: None)
            raise AssertionError("fill accepted two commits")
        except SystemExit as x:
            assert "D-8" in str(x), x
    # the evidence altered after --member (an ACCEPTED row): --fill re-verifies and refuses
    tmp = tmp_factory()
    reg = _layout(tmp)
    with _env(tmp, reg):
        classify("math", lambda s: None)
        with open(os.path.join(tmp, "res", "AF-U", "math", "seed_42", "diagnostics", "proposals.csv"), "a") as f:
            f.write('3,GROW,n00000001,MATH,0.1,0.01,3,,ACCEPTED,"ok",450' + chr(10))
        try:
            fill(lambda s: None)
            raise AssertionError("fill accepted altered evidence")
        except SystemExit as x:
            assert "S3" in str(x), x
    # no graft (every member one-cell): the reader's declared_single refuses too
    tmp = tmp_factory()
    reg = _layout(tmp)
    with _env(tmp, reg):
        for m, so in U.FX_MEMBERS:
            U._fx_single_evidence(tmp, "res/AF-U", m, so)
            assert classify(m, lambda s: None) == 3
        try:
            fill(lambda s: None)
            raise AssertionError("fill with no graft member")
        except SystemExit as x:
            assert "every member is one-cell" in str(x), x
        try:
            U.declared_single()
            raise AssertionError("reader accepted an all-one-cell declaration")
        except SystemExit as x:
            assert "every member is declared one-cell" in str(x)


def st_fill_real_template(tmp):
    """--fill on the COMMITTED AF-U template (experiment_configs/union_af_route/AF-U/graft_flatleaf.toml.tmpl) with the
    registered six members, ifeval one-cell: five ids filled in order, IFEVAL removed from both lists, nothing else changed."""
    import shutil
    reg = dict(U.REG, tomls="res/tomls", afu="res/AF-U", single_decl="res/AF-U/single_cell_members.json")
    os.makedirs(os.path.join(tmp, "res", "tomls"))
    src_t = os.path.join(U.ROOT, "experiment_configs", "union_af_route", "AF-U", TEMPLATE)
    shutil.copy(src_t, os.path.join(tmp, "res", "tomls", TEMPLATE))
    for m, so in U.REG["members"]:
        d = os.path.join(tmp, "res", "AF-U", m, "seed_42", "diagnostics")
        os.makedirs(d, exist_ok=True)
        if m == "ifeval":
            continue
        with open(os.path.join(tmp, "res", "AF-U", m, "seed_42", "headless_run.log"), "w") as f:
            f.write("Snapshot ID: SID_%s" % so + chr(10))
        with open(os.path.join(d, "run_manifest.json"), "w") as f:
            json.dump(dict(commit="c1"), f)
    U._fx_single_evidence(tmp, "res/AF-U", "ifeval", "IFEVAL", rows=(("1", "0.02111", "2"), ("1", "0.01790", "3"), ("1", "0.01665", "4")),
                          n_site=325, commit="c1")
    with _env(tmp, reg):
        assert classify("ifeval", lambda s: None) == 3
        dest = fill(lambda s: None)
    t = open(dest, encoding="utf-8").read()
    orig = open(src_t, "rb").read().replace(b"\r\n", b"\n").decode("utf-8")
    want = orig.replace('    "__SNAP_IFEVAL__",' + chr(10), "").replace('"BBH", "MATH", "MUSR", "IFEVAL", "GPQA", "MMLU_PRO_LB"', '"BBH", "MATH", "MUSR", "GPQA", "MMLU_PRO_LB"')
    for so in ("BBH", "MATH", "MUSR", "GPQA", "MMLU_PRO_LB"):
        want = want.replace("__SNAP_%s__" % so, "SID_%s" % so)
    assert t.split(chr(10), 1)[1] == want, "the filled graft differs from the template beyond the registered edits"
    assert "IFEVAL" not in t.split(chr(10), 1)[1].split("unionRootRouting")[0].split("unionSnapshots")[1]


CASES = (("classify", "--member: BUILT / ONE-CELL (verified, appended, idempotent, never changed) / STOP x4", "tmp"),
         ("fill", "--fill: the exact graft TOML text with the one-cell member removed; write-once", "tmp"),
         ("fill_refusals", "--fill: undeclared member without snapshot, D-8, altered evidence, every member one-cell", "factory"),
         ("fill_real", "--fill on the committed AF-U template, ifeval one-cell: exactly the registered edits", "tmp"))
_FN = {"classify": st_classify, "fill": st_fill, "fill_refusals": st_fill_refusals, "fill_real": st_fill_real_template}


def selftest(only=None, quiet=False):
    import tempfile; import scratch_dir  # TEMP-SPRAWL: temp on E:, removed at exit
    import shutil
    made, fails, ran = [], [], 0

    def factory():
        d = tempfile.mkdtemp(prefix="rp13ops_")
        made.append(d)
        return d
    try:
        for name, desc, kind in CASES:
            if only is not None and name not in only:
                continue
            ran += 1
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    _FN[name](factory()) if kind == "tmp" else _FN[name](factory)
                if not quiet:
                    print("  ok   %-14s %s" % (name, desc))
            except BaseException as e:            # noqa: B902
                fails.append(name)
                if not quiet:
                    print("  FAIL %-14s %s: %s: %s" % (name, desc, type(e).__name__, str(e)[:300]))
    finally:
        for d in made:
            shutil.rmtree(d, ignore_errors=True)
    if not quiet:
        print("%s selftest: %d / %d passed" % (TAG, ran - len(fails), ran))
    if fails:
        raise AssertionError("selftest failed: %s" % fails)
    return ran


def run_mutants():
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    cut = src.index(chr(10) + "MUTANTS = (")
    head, tail = src[:cut], src[cut:]
    killed, n, surv = 0, 0, []
    base = {}
    for name, edits, tests in MUTANTS:
        mut = head
        for old, new in edits:
            if mut.count(old) != 1:
                raise SystemExit("%s mutant %r: target occurs %d times: %r" % (TAG, name, mut.count(old), old[:80]))
            mut = mut.replace(old, new)
        key = tuple(sorted(tests))
        if key not in base:
            base[key] = _exec(src, tests)
        res = _exec(mut + tail, tests)
        k = res is not True and base[key] is True
        if name.startswith("Q00"):
            print("  %-56s control %s" % (name, "SURVIVED (as it must)" if res is True else "KILLED (harness broken)"))
            continue
        n += 1
        killed += int(k)
        if not k:
            surv.append(name)
        print("  %-56s %s %s" % (name, "KILLED" if k else "SURVIVED", "" if res is True else res[:80]))
    print("MUTANTS: %d of %d KILLED; survivors %s" % (killed, n, surv or "none"))
    return 0 if killed == n else 1


def _exec(src, tests):
    ns = {"__name__": "union_af_route_ops_mutant", "__file__": os.path.abspath(__file__)}
    try:
        exec(compile(src, "<mutant>", "exec"), ns)
        ns["selftest"](only=set(tests), quiet=True)
        return True
    except BaseException as e:                   # noqa: B902
        return "%s: %s" % (type(e).__name__, str(e)[:160])


NL = chr(10)
MUTANTS = (
    ("Q00 control", [("    return d, False", "    return d, False")], ["classify"]),
    ("Q01 a refusal without verified evidence declared", [("        ev = U.single_evidence(member, src)" + NL + "    except SystemExit as e:",
                                                           "        ev = U.single_evidence(member, src) if False else dict(best_sep=0.0, n_site=0, rows=0, root='r')" + NL + "    except SystemExit as e:")],
     ["classify"]),
    ("Q02 any failure treated as one-cell", [("    if U.REFUSAL_LINE not in con:" + NL + "        out(", "    if False:" + NL + "        out(")], ["classify"]),
    ("Q03 a declared member with a snapshot accepted", [("        if declared:" + NL + "            out(", "        if False:" + NL + "            out(")], ["classify"]),
    ("Q04 declaration entries silently changed", [("            if e != entry:", "            if False:")], ["classify"]),
    ("Q05 fill reorders the grafted members (not the template order)", [("    keep = [s for s in order if s not in single]",
                                                                           "    keep = sorted(s for s in order if s not in single)")], ["fill_real"]),
    ("Q11 fill keeps every member (the one-cell one too)", [("    keep = [s for s in order if s not in single]", "    keep = [s for s in order]")], ["fill"]),
    ("Q06 fill leaves the one-cell corpus in corpora", [('''    text = text[:c_.start()] + "corpora%s= [%s]" % (c_.group(1), ", ".join('"%s"' % s for s in keep)) + text[c_.end():]''',
                                                         "    pass")], ["fill"]),
    ("Q07 fill D-8 check removed", [("    if len(set(commits.values())) != 1:", "    if False:")], ["fill_refusals"]),
    ("Q08 fill accepts a member without snapshot id", [("        if sid is None:" + NL + '            refuse("BUILT member', "        if False:" + NL + '            refuse("BUILT member')],
     ["fill_refusals"]),
    ("Q09 fill overwrites", [("    if os.path.exists(dest):", "    if False:")], ["fill"]),
    ("Q10 fill does not re-verify the evidence", [("            U.single_evidence(m, src)                         # re-verified at fill time", "            pass")],
     ["fill_refusals"]),
)


if __name__ == "__main__":
    sys.exit(main())
