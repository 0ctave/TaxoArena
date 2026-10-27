"""EVAL-METRIC-DETERMINISM operator helper: C1, C3, C4 pair readouts and THE VERDICT (registration docs/judge_v2_program.md
L20311-L20389, commit 55a6ce1; P2 kept at L20382, 8bf15da). Zero calls. Read-only on the legs' outputs; each leg's AG
cache (DB + -wal together) is copied into the stage dir and only THAT copy is checkpointed and read (d9b_compare's code).
Every output is WRITE-ONCE (mode "x").

MODES (exit 0 = the criterion HELD on this pair; 3 = FAILED, an outcome; 2 = INSTRUMENT REFUSAL, nothing scored):
  python emd_compare.py c1 <X root> <Y root> <$ST> <LX> <LY>
      C1 (THE criterion): validation/MAIN_taxonomy_quality.csv and ../tuning_ledger.csv, WHOLE-FILE BYTES (CommitSHA and the
      three previously dropped fields DendrogramPurity, SphericalSilhouette, TotalDasguptaCost included). Pairs (R1, R2),
      (R1, R3), (R2, R3) only. 2 objects per pair; over the three pairs, the registered 6 comparisons.
      -> $ST/c1_<LX>_<LY>.json / .txt
  python emd_compare.py c3 <P1 root> <R1 root> <$ST> P1 R1
      C3: the 24 objects of LCB-D9B-BYTE-INERTNESS's C1' with EXACTLY d9b_compare's declared drops (lists copied verbatim
      and asserted equal to the pinned original at run time). Pair (P1, R1) only. -> $ST/c3_P1_R1.json / .txt
  python emd_compare.py c4 <X root> <Y root> <$ST> <LX> <LY>
      C4 (SECONDARY, does not gate): the 24 D9 objects under D9's drops only (d9_compare.py's lists, verbatim and asserted),
      scored per OBJECT (the file set is one object, as registered: "24 objects"). Pairs as C1; 72 comparisons over the
      three pairs. -> $ST/c4_<LX>_<LY>.json / .txt
  python emd_compare.py verdict <$ST> <FIX suite XML dir> <BASE golden XML> <out txt>
      reads $ST/emd_prep.json (V1, V2), $ST/leg_<L>.json x5 (V3-V8), $ST/emd_post.json and $ST/SHA256SUMS (V9: main
      unchanged; the class lists, leg and pair readouts hashed under their own paths), the two XML sources (C2, V10),
      the 3 c1, the c3 and the 3 c4 readouts; prints V1-V10, C1-C4, the mechanism readout, P1-P9, F1 / F2 and THE VERDICT
      RULE, and writes <out> once. Exit: 0 DONE, MERGEABLE; 3 F1 and / or F2 (no merge); 5 VOID (a V failed: a failed
      precondition, never an outcome); 6 C2 VOID (a READY defect, not an outcome); 2 INSTRUMENT REFUSAL, including the
      UNMAPPED cells listed below, which the registration does not map and this script refuses to choose:
        U1 C2 FAILED and C2 VOID on the same data ((i) and (ii) both fail): two registered states fire;
        U2 C2 FAILED with C1 HELD and C3 HELD: no verdict word is registered for that cell;
        U3 DONE, but TDC(P1) != TDC(P2) reads differently in the quality CSV and in tuning_ledger.csv: the verdict rule
           does not name the source.
"""
import csv, io, json, os, re, shutil, sqlite3, sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import emd_common as E  # noqa: E402
from emd_common import Refuse  # noqa: E402

VERSION = "emd_compare-2"


# ---------------------------------------------------------------- normalisation (d9b_compare's code, verbatim semantics)
def csv_drop(b, cols):
    rows = list(csv.reader(io.StringIO(b.decode("utf-8"), newline="")))
    if not rows:
        raise Refuse("empty file under a column drop")
    hdr = rows[0]
    missing = [c for c in cols if c not in hdr]
    if missing:
        raise Refuse("declared column(s) %s absent from the header %s" % (missing, hdr))
    keep = [i for i, h in enumerate(hdr) if h not in cols]
    return "\n".join("\x1f".join(r[i] for i in keep if i < len(r)) for r in rows).encode("utf-8")


def row_drop(b, key, rows):
    lines = b.decode("utf-8").splitlines(keepends=True)
    if not lines:
        raise Refuse("empty file under a row drop")
    hdr = next(csv.reader([lines[0]]))
    if key not in hdr:
        raise Refuse("row-drop key column %r absent from the header %s" % (key, hdr))
    k = hdr.index(key)
    kept, seen = [lines[0]], []
    for ln in lines[1:]:
        f = next(csv.reader([ln]), [])
        if len(f) > k and f[k] in rows:
            seen.append(f[k])
            continue
        kept.append(ln)
    missing = [r for r in rows if r not in seen]
    if missing:
        raise Refuse("declared row(s) %s absent (%s = ...)" % (missing, key))
    return "".join(kept).encode("utf-8")


def json_drop(b, keys):
    d = json.loads(b.decode("utf-8"))
    for k in keys:
        d.pop(k, None)
    return json.dumps(d, sort_keys=True).encode("utf-8")


def files_under(root):
    base = os.path.join(root, E.OUT)
    return sorted(os.path.relpath(os.path.join(d, f), base).replace("\\", "/") for d, _s, fs in os.walk(base) for f in fs)


def pool_readout(root, stage, tag):
    src = os.path.join(root, "ag_news_smoke_cache_v1.db")
    if not os.path.isfile(src):
        raise Refuse("no AG cache at %s" % src)
    d = os.path.join(stage, "pool_%s" % tag)
    os.makedirs(d)
    for s in ("", "-wal"):
        if os.path.exists(src + s):
            shutil.copyfile(src + s, os.path.join(d, "ag.db" + s))
    con = sqlite3.connect(os.path.join(d, "ag.db"))
    con.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    out = {}
    for t in E.TABLES:
        cols = [r[1] for r in con.execute("PRAGMA table_info(%s)" % t)]
        if not cols:
            con.close()
            raise Refuse("table %s absent from the AG copy of %s" % (t, root))
        keep = [c for c in cols if c not in E.POOL_DROP.get(t, [])]
        rows = con.execute("SELECT %s FROM %s ORDER BY %s" % (", ".join(keep), t, ", ".join(keep))).fetchall()
        out[t] = (len(rows), E.sha_bytes(repr(rows).encode("utf-8")))
    con.close()
    return out


SCHEMES = {
    # mode: (objects, byte list, column drops, row drops, criterion name, allowed pairs)
    "c1": (E.C1_OBJECTS, list(E.C1_OBJECTS), {}, {}, "C1", E.C1_PAIRS),
    "c3": (E.D9B_OBJECTS, E.D9B_BYTE, E.D9B_CSV_DROP, E.D9B_ROW_DROP, "C3", E.C3_PAIRS),
    "c4": (E.D9_OBJECTS, E.D9_BYTE, E.D9_CSV_DROP, {}, "C4", E.C1_PAIRS),
}


def normalised(mode, rel, raw):
    _o, byte, cdrop, rdrop, _c, _p = SCHEMES[mode]
    if rel in byte:
        return raw
    if rel in cdrop:
        return csv_drop(raw, cdrop[rel])
    if rel in rdrop:
        return row_drop(raw, *rdrop[rel])
    if rel in E.JSON_DROP:
        return json_drop(raw, E.JSON_DROP[rel])
    raise Refuse("%s has no declared treatment under %s" % (rel, mode))


def normalised_in(mode, rel, path, label):
    try:
        return normalised(mode, rel, open(path, "rb").read())
    except Refuse as e:
        raise Refuse("%s in leg %s: %s" % (rel, label, e))


def dropped_values(root):
    """The three declared fields, as written, from the quality CSV rows and the ledger's last row (descriptive)."""
    v = {}
    q = os.path.join(root, E.OUT, E.QUALITY)
    if os.path.isfile(q):
        for r in csv.DictReader(io.StringIO(open(q, "rb").read().decode("utf-8"), newline="")):
            if r.get("Metric") in E.DECLARED:
                v["quality:" + r["Metric"]] = r.get("Value")
    t = os.path.join(root, E.OUT, E.LEDGER)
    if os.path.isfile(t):
        rows = list(csv.DictReader(io.StringIO(open(t, "rb").read().decode("utf-8"), newline="")))
        if rows:
            for f in E.DECLARED:
                v["ledger:" + f] = rows[-1].get(f)
    return v


# ---------------------------------------------------------------- pair mode
def pair(mode, rx, ry, stage, lx, ly):
    objects, byte, cdrop, rdrop, crit, pairs = SCHEMES[mode]
    if (lx, ly) not in pairs:
        raise Refuse("%s accepts only the pairs %s, not (%s, %s)" % (crit, list(pairs), lx, ly))
    if not os.path.isdir(stage):
        raise Refuse("stage dir %s does not exist" % stage)
    n_lists = E.assert_lists_match_originals()
    stem = os.path.join(stage, "%s_%s_%s" % (mode, lx, ly))
    txt, js = stem + ".txt", stem + ".json"
    pools = [os.path.join(stage, "pool_%s_%s_%s_%s" % (mode, lx, ly, l)) for l in (lx, ly)] if mode != "c1" else []
    for p in [txt, js] + pools:
        if os.path.exists(p):
            raise Refuse("%s exists (outputs are write-once)" % p)
    for r in (rx, ry):
        if not os.path.isdir(os.path.join(r, E.OUT)):
            raise Refuse("no outputDir under %s" % r)
    L = []

    def say(s):
        L.append(s)
        print(s, flush=True)
    say("[%s] %s: %s = %s ; %s = %s ; stage %s" % (VERSION, crit, lx, rx, ly, ry, stage))
    say("[LISTS] %d object / drop lists equal the pinned originals (d9_compare %s, d9b_compare %s)"
        % (n_lists, E.ORIG["d9_compare"][1][:16], E.ORIG["d9b_compare"][1][:16]))
    say("[DROPS] %s: byte-compared %d: %s" % (crit, len(byte), byte))
    say("[DROPS] %s: column drops %s ; row drops %s ; JSON key drops %s ; table column drops %s"
        % (crit, cdrop or "none", {k: v[1] for k, v in rdrop.items()} or "none",
           (E.JSON_DROP if mode != "c1" else "none"), (E.POOL_DROP if mode != "c1" else "none")))
    status, digest = {}, {}
    files = [o for o in objects if o not in (E.FILESET,) and o not in E.TABLES]
    for rel in files:
        px, py = (os.path.join(r, E.OUT, rel) for r in (rx, ry))
        ex, ey = os.path.isfile(px), os.path.isfile(py)
        if not ex and not ey:
            raise Refuse("listed file %s absent in BOTH legs (not comparable)" % rel)
        if ex != ey:
            status[rel] = "DIFFERS"
            digest[rel] = [E.sha_bytes(normalised_in(mode, rel, px, lx)) if ex else None,
                           E.sha_bytes(normalised_in(mode, rel, py, ly)) if ey else None]
            say("[%s] %-58s DIFFERS (present in %s only)" % (crit, rel, lx if ex else ly))
            continue
        a, b = normalised_in(mode, rel, px, lx), normalised_in(mode, rel, py, ly)
        status[rel] = "EQUAL" if a == b else "DIFFERS"
        digest[rel] = [E.sha_bytes(a), E.sha_bytes(b)]
        how = ("whole-file bytes" if rel in byte else "without columns %s" % cdrop[rel] if rel in cdrop
               else "without rows %s" % rdrop[rel][1] if rel in rdrop else "without %d declared keys" % len(E.JSON_DROP[rel]))
        say("[%s] %-58s (%s) %s %s %s %s %s" % (crit, rel, how, lx, digest[rel][0][:16], ly, digest[rel][1][:16], status[rel]))
    if mode != "c1":
        fx, fy = files_under(rx), files_under(ry)
        only = sorted(set(fx) ^ set(fy))
        extra = sorted(set(fx) - (set(files) | E.EXCLUDED))
        status[E.FILESET] = "EQUAL" if not only else "DIFFERS"
        digest[E.FILESET] = [E.sha_bytes("\n".join(fx).encode()), E.sha_bytes("\n".join(fy).encode())]
        say("[%s] %s: files under the outputDir: %s %d, %s %d; present in one leg only: %s; outside the declared list"
            " (compared nowhere, printed): %s -> %s" % (crit, E.FILESET, lx, len(fx), ly, len(fy),
                                                       ["%s (%s only)" % (p, lx if p in fx else ly) for p in only] or "none",
                                                       extra or "none", status[E.FILESET]))
        px_ = pool_readout(rx, stage, "%s_%s_%s_%s" % (mode, lx, ly, lx))
        py_ = pool_readout(ry, stage, "%s_%s_%s_%s" % (mode, lx, ly, ly))
        for t in E.TABLES:
            status[t] = "EQUAL" if px_[t] == py_[t] else "DIFFERS"
            digest[t] = [list(px_[t]), list(py_[t])]
            say("[%s-POOL] %s (dropped %s): %s %s rows %s, %s %s rows %s %s" % (crit, t, E.POOL_DROP.get(t, []), lx, px_[t][0],
                                                                              px_[t][1][:16], ly, py_[t][0], py_[t][1][:16], status[t]))
    if set(status) != set(objects):
        raise Refuse("instrument defect: scored %s, declared %s" % (sorted(status), sorted(objects)))
    vx, vy = dropped_values(rx), dropped_values(ry)
    for k in sorted(set(vx) | set(vy)):
        say("[FIELDS, DESCRIPTIVE] %-32s %s %s  %s %s" % (k, lx, vx.get(k), ly, vy.get(k)))
    differing = [o for o in objects if status[o] == "DIFFERS"]
    held = not differing
    say("[%s] differing: %d of %d objects on (%s, %s): %s -> %s on this pair"
        % (crit, len(differing), len(objects), lx, ly, differing or "none", "0 differ" if held else "DIFFERS"))
    E.write_json_once(js, {"version": VERSION, "mode": mode, "criterion": crit, "labels": [lx, ly], "roots": [rx, ry],
                           "objects": objects, "status": status, "digest": digest, "differing": differing,
                           "dropped_values": {lx: vx, ly: vy}})
    E.write_once(txt, "\n".join(L) + "\n")
    return 0 if held else 3


# ---------------------------------------------------------------- verdict
def load_pair(stage, mode, lx, ly):
    p = os.path.join(stage, "%s_%s_%s.json" % (mode, lx, ly))
    j = E.load_json(p, "%s readout" % mode)
    objects = SCHEMES[mode][0]
    ok = (isinstance(j, dict) and j.get("version") == VERSION and j.get("mode") == mode and j.get("labels") == [lx, ly]
          and j.get("objects") == objects and isinstance(j.get("differing"), list) and isinstance(j.get("roots"), list)
          and len(j["roots"]) == 2 and set(j["differing"]) <= set(objects))
    if not ok:
        raise Refuse("readout %s is malformed or not a %s (%s, %s) readout of this version" % (p, mode, lx, ly))
    return j


def xml_suite(path):
    try:
        root = ET.parse(path).getroot()
    except (OSError, ET.ParseError) as e:
        raise Refuse("XML %s cannot be read: %s" % (path, e))
    if root.tag != "testsuite":
        raise Refuse("XML %s is not a JUnit testsuite" % path)
    cases = []
    for tc in root.iter("testcase"):
        state = ("FAILED" if tc.find("failure") is not None else "ERROR" if tc.find("error") is not None
                 else "SKIPPED" if tc.find("skipped") is not None else "PASSED")
        cases.append((tc.get("classname"), tc.get("name"), state))
    return root.attrib, cases


def sums_check(stage):
    """V9's evidence clause: every class list, leg readout and pair readout is listed in $ST/SHA256SUMS under its own path
    (sha256sum's './x' or '*x', '\\' or '/', any case) with its current sha256."""
    want = []
    for l in E.LEGS:
        want += ["classlists/leg%s_all.txt" % l, "classlists/leg%s_%s.txt" % (l, E.X1), "leg_%s.json" % l]
    want += ["%s_%s_%s.json" % (m, x, y) for m in ("c1", "c4") for x, y in E.C1_PAIRS] + ["c3_P1_R1.json"]
    p = os.path.join(stage, "SHA256SUMS")
    listed = {}
    if os.path.isfile(p):
        for ln in E.decode(open(p, "rb").read()).replace("\r", "").split("\n"):
            m = re.match(r"^\s*([0-9A-Fa-f]{64})\s+\*?(.+?)\s*$", ln)
            if m:
                k = m.group(2).replace("\\", "/")
                while k.startswith("./"):
                    k = k[2:]
                k = k.lower()
                listed[k] = listed.get(k, set()) | {m.group(1).lower()}
    out, ok = {}, os.path.isfile(p)
    for w in want:
        f = os.path.join(stage, *w.split("/"))
        h = E.sha(f) if os.path.isfile(f) else None
        got = listed.get(w.lower())
        st = ("FILE ABSENT" if h is None else "NOT LISTED" if not got else "LISTED TWICE" if len(got) > 1
              else "own sha256" if h in got else "WRONG sha256")
        out[w] = st
        ok &= st == "own sha256"
    return ok, out


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def clause(vals):
    """vals: [(source, bool or None)] -> HOLDS iff every source holds; FAILS iff any source fails; else UNDETERMINED."""
    if any(v is False for _s, v in vals):
        return "FAILED"
    if any(v is None for _s, v in vals):
        return "UNDETERMINED"
    return "HELD"


def verdict(stage, fix_dir, base_xml, out):
    if os.path.exists(out):
        raise Refuse("%s exists (write-once)" % out)
    E.assert_lists_match_originals()
    L = []

    def say(s):
        L.append(s)
        print(s, flush=True)
    prep = E.load_json(os.path.join(stage, "emd_prep.json"), "prep readout")
    post = E.load_json(os.path.join(stage, "emd_post.json"), "post readout")
    legs = {}
    for l in E.LEGS:
        j = E.load_json(os.path.join(stage, "leg_%s.json" % l), "leg readout")
        if j.get("leg") != l or not isinstance(j.get("checks"), dict):
            raise Refuse("leg readout for %s is malformed" % l)
        legs[l] = j
    roots = prep.get("roots") or {}
    if sorted(roots) != sorted(E.LEGS):
        raise Refuse("emd_prep.json does not name the five leg roots")
    for l in E.LEGS:
        if legs[l].get("root") != roots[l]:
            raise Refuse("leg %s: the checked root %r is not the prepared root %r" % (l, legs[l].get("root"), roots[l]))
    c1 = {p: load_pair(stage, "c1", *p) for p in E.C1_PAIRS}
    c4 = {p: load_pair(stage, "c4", *p) for p in E.C1_PAIRS}
    c3 = load_pair(stage, "c3", "P1", "R1")
    for (lx, ly), j in list(c1.items()) + list(c4.items()) + [(("P1", "R1"), c3)]:
        if j["roots"] != [roots[lx], roots[ly]]:
            raise Refuse("%s readout (%s, %s) was made on roots %s, not the prepared %s"
                         % (j["mode"], lx, ly, j["roots"], [roots[lx], roots[ly]]))
    say("[%s verdict] stage %s ; FIX suite XML dir %s ; BASE golden XML %s" % (VERSION, stage, fix_dir, base_xml))
    say("[LEGS] %s" % ", ".join("%s=%s@%s" % (l, roots[l], E.COMMIT[l][:7]) for l in E.LEGS))

    # ---- validity
    V = {}
    V["V1"] = prep.get("v1") is True
    V["V2"] = prep.get("v2") is True
    x1 = {l: legs[l].get("x1_count") for l in E.LEGS}
    alls = {l: legs[l].get("classlist_all_sha") for l in E.LEGS}
    lists_ok = True
    for l in E.LEGS:
        for key, name in (("classlist_all", "all"), ("classlist_x1", E.X1)):
            p = os.path.join(stage, "classlists", "leg%s_%s.txt" % (l, name))
            got = E.sha(p) if os.path.isfile(p) else None
            ok = got is not None and got == legs[l].get(key + "_sha")
            lists_ok &= ok
            say("[V3] class list %s: sha256 %s, recorded %s -> %s" % (p, (got or "ABSENT")[:16],
                                                                    str(legs[l].get(key + "_sha"))[:16], "OK" if ok else "MISMATCH"))
    r_counts = [x1[l] for l in E.R_LEGS]
    V["V3"] = (lists_ok and all(x1[l] == 0 for l in E.P_LEGS) and all(isinstance(c, int) and c >= 1 for c in r_counts)
               and len(set(r_counts)) == 1 and len({alls[l] for l in E.R_LEGS}) == 1 and len({alls[l] for l in E.P_LEGS}) == 1)
    say("[V3 = X1] %s .class counts: %s (bar: P1 = P2 = 0; R1 = R2 = R3 >= 1); class-name lists R equal: %s, P equal: %s;"
        " the build's declared count %d (PRINTED, not the bar): R legs %s -> %s"
        % (E.X1, x1, len({alls[l] for l in E.R_LEGS}) == 1, len({alls[l] for l in E.P_LEGS}) == 1, E.X1_DECLARED_COUNT,
           "match" if all(c == E.X1_DECLARED_COUNT for c in r_counts) else "DO NOT MATCH", "MET" if V["V3"] else "NOT MET"))
    for v in ("V4", "V5", "V6", "V8"):
        V[v] = all(legs[l]["checks"].get(v) is True for l in E.LEGS)
        say("[%s] per leg: %s -> %s" % (v, {l: legs[l]["checks"].get(v) for l in E.LEGS}, "MET" if V[v] else "NOT MET"))
    misses = {l: legs[l].get("misses") for l in E.LEGS}
    V["V7"] = all(isinstance(m, int) for m in misses.values()) and len(set(misses.values())) == 1
    say("[V7] embedding misses per leg %s (bar: equal across the five legs) -> %s" % (misses, "MET" if V["V7"] else "NOT MET"))
    tcs = {l: legs[l].get("thread_cap") for l in E.LEGS}
    V["TC"] = (all(legs[l]["checks"].get("TC") is True for l in E.LEGS) and all(tcs[l] == [E.TC_WITNESS] for l in E.LEGS)
               and len({json.dumps(tcs[l]) for l in E.LEGS}) == 1)
    say("[TC] THREAD-CAP witness per leg %s (bar: [%s] in every leg, equal across the five legs) -> %s"
        % (tcs, E.TC_WITNESS, "MET" if V["TC"] else "NOT MET"))
    sums_ok, sums = sums_check(stage)
    for k in sorted(sums):
        say("[V9] SHA256SUMS %-44s %s" % (k, sums[k]))
    V["V9"] = post.get("v9") is True and sums_ok
    say("[V9] main unchanged (emd_post.json v9 %s); class lists, leg and pair readouts hashed into $ST/SHA256SUMS: %s"
        % (post.get("v9"), sums_ok))
    fix_xml = os.path.join(fix_dir, "TEST-%s.xml" % E.TEST_CLASS)
    fa, fcases = xml_suite(fix_xml)
    ba, bcases = xml_suite(base_xml)
    fmine = [c for c in fcases if c[0] == E.TEST_CLASS]
    bmine = [c for c in bcases if c[0] == E.TEST_CLASS]
    V["V10"] = len(fmine) > 0 and not any(s == "SKIPPED" for _c, _n, s in fmine) and len(bmine) > 0
    say("[V10] golden test executed: FIX suite %d testcase(s) (skipped %d), BASE leg %d testcase(s) -> %s"
        % (len(fmine), sum(s == "SKIPPED" for _c, _n, s in fmine), len(bmine), "MET" if V["V10"] else "NOT MET"))
    for v in ("V1", "V2", "V9"):
        say("[%s] %s" % (v, "MET" if V[v] else "NOT MET"))
    vmet = all(V.values())
    say("[VALIDITY] V1-V10 + TC: %s" % ("ALL MET" if vmet else "NOT MET: %s" % [k for k, v in V.items() if not v]))

    # ---- criteria
    s_c1 = {p: j["differing"] for p, j in c1.items()}
    n_c1 = sum(len(d) for d in s_c1.values())
    c1_held = n_c1 == 0
    for p, d in s_c1.items():
        say("[C1] %s/%s: %s" % (p[0], p[1], d or "0 of 2 differ"))
    say("[C1] %d of 6 comparisons differ (2 objects x 3 replicate pairs) -> C1 %s" % (n_c1, "HELD" if c1_held else "FAILED"))
    fix_ok = (len(fmine) > 0 and all(s == "PASSED" for _c, _n, s in fmine) and fa.get("failures") == "0"
              and fa.get("errors") == "0" and fa.get("skipped") == "0")
    bstate = {n: s for _c, n, s in bmine}
    base_tdc_fails = bstate.get(E.TDC_TEST) == "FAILED"
    for n in sorted(bstate):
        say("[C2 BASE per test] %-58s %s" % (n, bstate[n]))
    say("[C2] (i) FIX suite: %d testcase(s), all passed: %s ; (ii) BASE: %s %s"
        % (len(fmine), fix_ok, E.TDC_TEST, bstate.get(E.TDC_TEST, "ABSENT")))
    if fix_ok and base_tdc_fails:
        c2 = "HELD"
    elif not fix_ok and not base_tdc_fails:
        c2 = "UNMAPPED"
    elif not fix_ok:
        c2 = "FAILED"
    else:
        c2 = "VOID"
    say("[C2] %s" % {"HELD": "C2 HELD", "FAILED": "C2 FAILED ((i) fails)", "VOID": "C2 VOID ((ii) fails: a READY defect, not an outcome)",
                     "UNMAPPED": "C2 FAILED AND C2 VOID both fire on the same data (U1)"}[c2])
    c3_d = c3["differing"]
    c3_held = not c3_d
    say("[C3] P1/R1: %d of 24 objects differ: %s -> C3 %s" % (len(c3_d), c3_d or "none", "HELD" if c3_held else "FAILED"))
    n_c4 = sum(len(j["differing"]) for j in c4.values())
    for p, j in c4.items():
        say("[C4] %s/%s: %s" % (p[0], p[1], j["differing"] or "0 of 24 differ"))
    say("[C4, SECONDARY, does not gate] %d of 72 differ -> C4 %s" % (n_c4, "HELD" if n_c4 == 0 else "FAILED"))

    # ---- mechanism readout (descriptive)
    vals = {l: legs[l].get("values") or {} for l in E.LEGS}
    for l in E.LEGS:
        say("[MECHANISM, DESCRIPTIVE] %s %s" % (l, " ".join("%s=%s" % (k, vals[l].get(k)) for k in sorted(vals[l]))))

    def rel_tdc(src, x, y):
        a, b = num(vals[x].get(src + ":TotalDasguptaCost")), num(vals[y].get(src + ":TotalDasguptaCost"))
        return None if a is None or b is None or a == 0 else abs(a - b) / abs(a)

    def absd(src, f, x, y):
        a, b = num(vals[x].get("%s:%s" % (src, f))), num(vals[y].get("%s:%s" % (src, f)))
        return None if a is None or b is None else abs(a - b)
    for x, y in (("P1", "P2"), ("P1", "R1")):
        for src in ("quality", "ledger"):
            say("[MECHANISM, DESCRIPTIVE] %s/%s %-7s |dTDC|/TDC(P1) %s ; |dDP| %s ; |dSS| %s"
                % (x, y, src, rel_tdc(src, "P1", y if x == "P1" else x), absd(src, "DendrogramPurity", x, y),
                   absd(src, "SphericalSilhouette", x, y)))

    def differs(f, x, y):
        out = []
        for src in ("quality", "ledger"):
            a, b = num(vals[x].get("%s:%s" % (src, f))), num(vals[y].get("%s:%s" % (src, f)))
            out.append((src, None if a is None or b is None else a != b))
        return out

    # ---- predictions
    P = {}
    P["P1"] = "HELD" if c1_held else "FAILED"
    P["P2"] = "HELD" if (fix_ok and base_tdc_fails and bstate.get(E.TA_TEST) == "FAILED") else "FAILED"
    P["P3"] = "HELD" if c3_held else "FAILED"
    P["P4"] = "HELD" if n_c4 == 0 else "FAILED"
    P["P5"] = "HELD" if (all(x1[l] == 0 for l in E.P_LEGS) and all(isinstance(c, int) and c >= 1 for c in r_counts)
                         and len(set(r_counts)) == 1) else "FAILED"
    p6 = {f: clause(differs(f, "P1", "P2")) for f in E.DECLARED}
    P["P6"] = "; ".join("%s(P1) != %s(P2) %s" % (f, f, p6[f]) for f in ("TotalDasguptaCost", "DendrogramPurity", "SphericalSilhouette"))
    p7a = clause(differs("TotalDasguptaCost", "R1", "P1"))
    p7b = clause([(s, None if rel_tdc(s, "P1", "R1") is None else rel_tdc(s, "P1", "R1") <= E.MARGIN_TDC) for s in ("quality", "ledger")])
    p7c = clause([(s, None if absd(s, "DendrogramPurity", "P1", "R1") is None or absd(s, "SphericalSilhouette", "P1", "R1") is None
                   else (absd(s, "DendrogramPurity", "P1", "R1") <= E.P7_DP and absd(s, "SphericalSilhouette", "P1", "R1") <= E.P7_SS))
                  for s in ("quality", "ledger")])
    P["P7"] = "TDC(R1) != TDC(P1) %s; |rel dTDC| <= 1.0%% %s; |dDP| <= 1e-13 and |dSS| <= 1e-15 %s" % (p7a, p7b, p7c)
    fails = set()
    fdir_ok = os.path.isdir(fix_dir)
    for fn in (sorted(os.listdir(fix_dir)) if fdir_ok else []):
        if fn.startswith("TEST-") and fn.endswith(".xml"):
            _a, cs = xml_suite(os.path.join(fix_dir, fn))
            fails |= {(c, n) for c, n, s in cs if s in ("FAILED", "ERROR")}
    say("[P8] FIX suite failing testcases: %s (known environmental: %s)" % (sorted(fails) or "none", sorted(E.KNOWN_FAILURES)))
    P["P8"] = "HELD" if (fails <= E.KNOWN_FAILURES and V["V1"]) else "FAILED"
    p9 = {l: (legs[l].get("duration_ms"), legs[l].get("gradle_s")) for l in E.LEGS}
    P["P9"] = "HELD" if all(isinstance(d, int) and E.P9_DUR_MS[0] <= d <= E.P9_DUR_MS[1] and g is not None and g <= E.P9_GRADLE_S
                            for d, g in p9.values()) else "FAILED"
    say("[P9] per leg (duration_ms, Gradle s): %s" % p9)
    for k in sorted(P):
        say("[PREDICTION %s] %s" % (k, P[k]))

    # ---- falsifiers and the verdict rule
    f1 = vmet and not c1_held
    f2 = vmet and not c3_held
    say("[FALSIFIER F1 (FIX INCOMPLETE)] %s" % ("FIRED: C1 FAILED with V1-V10 met" if f1 else "not fired"))
    say("[FALSIFIER F2 (FIX LEAKS)] %s" % ("FIRED: C3 FAILED with V1-V10 met" if f2 else "not fired"))
    if not vmet:
        rc, v = 5, "VOID: V1-V10 not met (%s); a failed precondition, never an outcome; nothing is scored" % [k for k, x in V.items() if not x]
    elif f1 or f2:
        rc = 3
        v = ("FIX INCOMPLETE (F1) AND FIX LEAKS (F2), recorded joined" if f1 and f2 else
             "FIX INCOMPLETE (F1)" if f1 else "FIX LEAKS (F2)") + "; no merge; a new registration"
        if c2 != "HELD":
            v += "; C2 state: %s" % c2
    elif c2 == "UNMAPPED":
        raise Refuse("UNMAPPED CELL U1: C2 (i) and (ii) both fail (C2 FAILED and C2 VOID on the same data); registrar")
    elif c2 == "VOID":
        rc, v = 6, "C2 VOID ((ii): the golden test did not fail TDC's permutation assertion on BASE): a READY defect, not an outcome"
    elif c2 == "FAILED":
        raise Refuse("UNMAPPED CELL U2: C2 FAILED with C1 HELD, C3 HELD and V1-V10 met: no registered verdict word; registrar")
    else:
        d = differs("TotalDasguptaCost", "P1", "P2")
        states = {s for _src, s in d}
        if None in states:
            raise Refuse("TDC(P1) / TDC(P2) not numeric in a source: %s" % d)
        if len(states) != 1:
            raise Refuse("UNMAPPED CELL U3: TDC(P1) != TDC(P2) reads %s by source; the verdict rule names no source; registrar" % d)
        rc = 0
        if states == {True}:
            v = "DONE, MERGEABLE; MECHANISM SHOWN: the fix removed the drift (TDC(P1) != TDC(P2) in both files)"
        else:
            v = ("DONE, MERGEABLE; reproducible in 3 of 3 replicates; the pre-change drift did not reproduce in this window"
                 " (1 pair), so the fix is not shown to be its cause")
    say("[VERDICT] %s" % v)
    E.write_once(out, "\n".join(L) + "\n")
    return rc


def main(argv):
    try:
        if argv and argv[0] in ("c1", "c3", "c4"):
            if len(argv) != 6:
                raise Refuse("usage: %s <X root> <Y root> <stage> <X label> <Y label>" % argv[0])
            return pair(argv[0], *argv[1:6])
        if argv and argv[0] == "verdict":
            if len(argv) != 5:
                raise Refuse("usage: verdict <stage> <FIX suite XML dir> <BASE golden XML> <out txt>")
            return verdict(*argv[1:5])
        raise Refuse("unknown mode; see the docstring")
    except Refuse as e:
        print("[%s] INSTRUMENT REFUSAL (a failed precondition; nothing scored): %s" % (VERSION, e), flush=True)
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
