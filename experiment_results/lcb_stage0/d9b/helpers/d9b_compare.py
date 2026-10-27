"""LCB-D9B-BYTE-INERTNESS operator helper: C1' (A vs B) and C2 (A vs A2), DECLARED-DROP BYTE IDENTITY, and the D9
verdict mapping (registration: docs/judge_v2_program.md L19642-L19714, commit ab8aee9; INSTRUMENT (i), READOUTS AND
CRITERIA C1' / C2 / THE D9 VERDICT, PREDICTIONS P6, FALSIFIER F1 / F2).

Derived from d9\\d9_compare.py (sha256-lf of the file bytes 8636b21591e70a76c1d1a8d52d28ba6a59cfe238db49b4720e99355a438138a8,
blob:743cd1a1). Zero calls. Read-only on the legs' outputs; each leg's AG cache (DB + -wal together) is copied into the
stage dir and only THAT copy is checkpointed and read (d9_compare's code, unchanged).

CHANGES AGAINST d9_compare.py (the registration's "ONLY changes are the declared drops", plus what serving C1' and C2
through one code path, P6 and the verdict mapping require; each is named here for the READY):
  D1 (registered) validation/MAIN_taxonomy_quality.csv leaves the byte list and becomes a ROW drop: the lines whose Metric
     is DendrogramPurity, SphericalSilhouette or TotalDasguptaCost are removed; the header and every other line are
     compared BYTE FOR BYTE (line terminators kept), in file order.
  D2 (registered) tuning_ledger.csv's column drop becomes CommitSHA, DendrogramPurity, SphericalSilhouette,
     TotalDasguptaCost.
  D3 the two legs are labelled: the pair must be (A, B) = C1' or (A, A2) = C2; any other pair is refused.
  D4 the object count is the registered 24 (17 + 4 + the file set + 2 tables); the FILE SET is ONE object (d9_compare
     added the number of one-leg paths); a listed file present in ONE leg only makes that file AND the file set differ; a
     listed file absent in BOTH legs, a declared column / row absent, or an absent AG DB is an INSTRUMENT REFUSAL (exit 2,
     nothing scored, no file of record written) where d9_compare crashed with a traceback.
  D5 the drop lists are printed on every run; the P6 descriptive block (the three dropped fields, both legs, no bar).
  D6 outputs are WRITE-ONCE (mode "x"): <stage>/d9b_compare.txt and a machine-readable <stage>/d9b_compare.json that the
     verdict mode reads; d9_compare wrote d9_compare.txt with "w".
  D7 V7 is printed only from explicit misses files (--misses X Y); d9_compare read <stage>/d9_misses_A|B.txt, which do not
     exist in $ST\\aa2 (the R9 artefact of the delta READY).
  D8 --verdict: S_AB, S_AA, the registered mapping and the per-object reading; P6 over the three legs.
Unchanged from d9_compare.py: the 17 byte files, iteration_metrics.csv - wall_ms, run_manifest.json - the 13 keys (a
declared key absent is ignored, as in d9_compare), csv_drop (csv-parsed, \\x1f-joined), json_drop, files_under, the
EXCLUDED list, pool_readout and the descriptive AG-table digests.

usage (pair mode; the stage dir must exist and hold no d9b_compare.txt / .json / pool_copy_<label>):
  python d9b_compare.py <A root> <B root>  <$ST>      A B  [--misses <$ST\\d9_misses_A.txt> <$ST\\d9_misses_B.txt>]   (C1')
  python d9b_compare.py <A root> <A2 root> <$ST\\aa2> A A2 [--misses <$ST\\d9_misses_A.txt> <$ST\\a2\\d9_misses_A.txt>]  (C2)
  exit 0 = 0 of 24 objects differ (HELD); 3 = >= 1 differs (FAILED, an outcome, never a crash); 2 = INSTRUMENT REFUSAL.
usage (verdict mode; reads the two JSONs; writes <out> once):
  python d9b_compare.py --verdict <$ST\\d9b_compare.json> <$ST\\aa2\\d9b_compare.json> <$ST\\d9b_verdict.txt>
  exit 0 = D9 DISCHARGED on C1' and C2 (V1-V11 are NOT checked here); 3 = THE CHANGE READ (F1; in the mixed cell, S_AA
  non-empty AND S_AB not a subset of S_AA, with "F2 ALSO FIRED" disclosed: registrar ruling A1, programme L19802-L19850,
  f13736a); 6 = D9 UNDETERMINED (F2; S_AA non-empty and S_AB a subset of S_AA); 2 = INSTRUMENT REFUSAL.
  The verdict mode also scores P6 (ruling A2): TotalDasguptaCost DIFFERS on A/B and A/A2; |relative TDC difference|
  <= 0.6% (relative to leg A's TDC of the same source), |DP difference| <= 1e-13 and |SS difference| <= 1e-15 on A/B,
  A/A2 and B/A2; each clause on both sources (the quality CSV row, the tuning_ledger last row); a value not numeric in
  both legs makes its clause UNDETERMINED. P6 is DESCRIPTIVE, no bar on D9.

POST-PATCH CHANGES (registrar's record f13736a, required changes R1-R3; pre-patch file d9b_compare_prepatch.py,
sha256-lf 0f82fa76...): R1 the mixed verdict cell exits 3 (F1) with F2 ALSO FIRED and a [LIMIT] line, no exit 4; R2 the
P6 relative TDC is computed against leg A's TDC for every pair, labelled "of A", and P6 is scored; R3 a refusal raised
while applying a drop names the file and the leg.
D3 (READY d984724; pre-D3 file d9b_compare_r4.py, sha256-lf c1e0dc17...): --verdict refuses (exit 2) a missing, corrupt
or malformed readout JSON instead of raising a traceback (load_readout). Nothing else changed.
"""
import csv, hashlib, io, json, os, shutil, sqlite3, sys

VERSION = "d9b_compare"
OUT = os.path.join("experiment_results", "topic_partition", "ag_news_smoke_s42")
BYTE = ["seed_42/dag_snapshots.jsonl", "seed_42/gate_ids.json", "seed_42/fixed_point_certificate.txt"] + \
       ["seed_42/validation/" + f for f in ("MAIN_bridge_quality.csv", "MAIN_centroid_routing_results.csv", "MAIN_graph_validity.csv",
                                            "MAIN_heldout_leaf_support.csv", "MAIN_migration_flow_matrix.csv",
                                            "MAIN_routing_calibration.csv", "MAIN_routing_diagnostics.txt",
                                            "MAIN_trickle_validation_results.csv", "bridge_nodes.csv", "bridge_residuals.csv")] + \
       ["seed_42/diagnostics/" + f for f in ("dag_snapshots.jsonl", "proposals.csv", "rank_history.csv", "config.toml")]
DECLARED = ["DendrogramPurity", "SphericalSilhouette", "TotalDasguptaCost"]
CSV_DROP = {"seed_42/diagnostics/iteration_metrics.csv": ["wall_ms"], "tuning_ledger.csv": ["CommitSHA"] + DECLARED}
ROW_DROP = {"seed_42/validation/MAIN_taxonomy_quality.csv": ("Metric", DECLARED)}
JSON_DROP = {"seed_42/diagnostics/run_manifest.json": ["commit", "branch", "dirty", "dirty_src", "dirty_src_files", "dirty_other",
                                                       "dirty_other_files", "dirty_files", "started_at_millis", "finished_at_millis",
                                                       "duration_ms", "config_path", "proposal_memo_digest_ms"]}
EXCLUDED = {"seed_42/headless_run.log", "seed_42/diagnostics/headless_run.log", "seed_42/performance_report.json"}
POOL_DROP = {"reserved_pool_meta": ["created_at"]}
FILESET = "FILE-SET"
TABLES = ["reserved_pool", "reserved_pool_meta"]
OBJECTS = BYTE + list(CSV_DROP)[:1] + list(JSON_DROP) + list(ROW_DROP) + list(CSV_DROP)[1:] + [FILESET] + TABLES
PAIRS = {("A", "B"): "C1'", ("A", "A2"): "C2"}
QUALITY, LEDGER = list(ROW_DROP)[0], "tuning_ledger.csv"
assert len(BYTE) == 17 and len(JSON_DROP["seed_42/diagnostics/run_manifest.json"]) == 13
assert len(OBJECTS) == 24 and len(set(OBJECTS)) == 24


class Refuse(Exception):
    pass


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def csv_drop(b, cols):
    rows = list(csv.reader(io.StringIO(b.decode("utf-8"), newline="")))
    hdr = rows[0]
    missing = [c for c in cols if c not in hdr]
    if missing:
        raise Refuse("declared column(s) %s absent from the header %s" % (missing, hdr))
    keep = [i for i, h in enumerate(hdr) if h not in cols]
    return "\n".join("\x1f".join(r[i] for i in keep if i < len(r)) for r in rows).encode("utf-8")


def row_drop(b, key, rows):
    """The header and every line whose <key> field is not a declared row, byte for byte (terminators kept), in order."""
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
    base = os.path.join(root, OUT)
    return sorted(os.path.relpath(os.path.join(d, f), base).replace("\\", "/") for d, _s, fs in os.walk(base) for f in fs)


def pool_readout(root, stage, leg):
    src = os.path.join(root, "ag_news_smoke_cache_v1.db")
    if not os.path.isfile(src):
        raise Refuse("no AG cache at %s" % src)
    d = os.path.join(stage, "pool_copy_%s" % leg)
    os.makedirs(d)
    for s in ("", "-wal"):
        if os.path.exists(src + s):
            shutil.copyfile(src + s, os.path.join(d, "ag.db" + s))
    con = sqlite3.connect(os.path.join(d, "ag.db"))
    con.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    out = {}
    for t in TABLES:
        cols = [r[1] for r in con.execute("PRAGMA table_info(%s)" % t)]
        if not cols:
            con.close()
            raise Refuse("table %s absent from the AG copy of %s" % (t, root))
        keep = [c for c in cols if c not in POOL_DROP.get(t, [])]
        rows = con.execute("SELECT %s FROM %s ORDER BY %s" % (", ".join(keep), t, ", ".join(keep))).fetchall()
        out[t] = (len(rows), sha_bytes(repr(rows).encode("utf-8")))
    # DESCRIPTIVE ONLY (NOT C1' / C2): a row digest of every table of the copy
    desc = {}
    for t, in con.execute("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"):
        rows = con.execute("SELECT * FROM \"%s\"" % t).fetchall()
        desc[t] = (len(rows), sha_bytes(repr(sorted(map(repr, rows))).encode("utf-8"))[:16])
    con.close()
    return out, desc


def normalised(rel, raw):
    if rel in BYTE:
        return raw
    if rel in CSV_DROP:
        return csv_drop(raw, CSV_DROP[rel])
    if rel in ROW_DROP:
        return row_drop(raw, *ROW_DROP[rel])
    return json_drop(raw, JSON_DROP[rel])


def normalised_in(rel, path, label):
    """R3: a refusal raised while applying a declared drop names the file and the leg."""
    try:
        return normalised(rel, open(path, "rb").read())
    except Refuse as e:
        raise Refuse("%s in leg %s: %s" % (rel, label, e))


def dropped_values(root):
    """P6 (descriptive): the three declared fields, as written, from the quality CSV rows and the ledger's last row."""
    v = {}
    q = os.path.join(root, OUT, QUALITY)
    if os.path.isfile(q):
        for r in csv.DictReader(io.StringIO(open(q, "rb").read().decode("utf-8"), newline="")):
            if r.get("Metric") in DECLARED:
                v["quality:" + r["Metric"]] = r.get("Value")
    t = os.path.join(root, OUT, LEDGER)
    if os.path.isfile(t):
        rows = list(csv.DictReader(io.StringIO(open(t, "rb").read().decode("utf-8"), newline="")))
        if rows:
            for f in DECLARED:
                v["ledger:" + f] = rows[-1].get(f)
    return v


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def p6_lines(tag, lx, ly, vx, vy, va):
    """R2: the relative TDC difference is |TDC_x - TDC_y| / TDC_A, leg A's value of the same source, for every pair."""
    out = []
    for src in ("quality", "ledger"):
        for f in DECLARED:
            k = "%s:%s" % (src, f)
            a, b = vx.get(k), vy.get(k)
            fa, fb = num(a), num(b)
            if fa is None or fb is None:
                out.append("[P6 %s, DESCRIPTIVE, no bar] %-7s %-19s %s %s  %s %s  (not numeric in both: no difference computed)"
                           % (tag, src, f, lx, a, ly, b))
                continue
            d = abs(fa - fb)
            extra = ""
            if f == "TotalDasguptaCost":
                fA = num(va.get(k))
                extra = ("; |relative difference| %.6f%% of A" % (100 * d / abs(fA)) if fA else
                         "; |relative difference| not computed (leg A's TDC %r not numeric or 0)" % va.get(k))
            out.append("[P6 %s, DESCRIPTIVE, no bar] %-7s %-19s %s %s  %s %s  |difference| %.6g%s"
                       % (tag, src, f, lx, a, ly, b, d, extra))
    return out


P6_TDC_REL, P6_DP, P6_SS = 0.006, 1e-13, 1e-15


def p6_score(va, vb, v2):
    """R2 / ruling A2: P6 scored (DESCRIPTIVE, no bar on D9). Returns (lines, "HELD" | "FAILED" | "UNDETERMINED")."""
    legs = {"A": va, "B": vb, "A2": v2}
    rows = []   # (clause, pair, source, state, detail)
    for src in ("quality", "ledger"):
        k = src + ":TotalDasguptaCost"
        for x, y in (("A", "B"), ("A", "A2")):
            fx, fy = num(legs[x].get(k)), num(legs[y].get(k))
            if fx is None or fy is None:
                rows.append(("TDC DIFFERS", x + "/" + y, src, "UNDETERMINED", "not numeric in both"))
            else:
                rows.append(("TDC DIFFERS", x + "/" + y, src, "HOLDS" if fx != fy else "FAILS", "%r vs %r" % (fx, fy)))
        for x, y in (("A", "B"), ("A", "A2"), ("B", "A2")):
            for f, bar in (("TotalDasguptaCost", P6_TDC_REL), ("DendrogramPurity", P6_DP), ("SphericalSilhouette", P6_SS)):
                kk = "%s:%s" % (src, f)
                fx, fy = num(legs[x].get(kk)), num(legs[y].get(kk))
                name = {"TotalDasguptaCost": "|rel TDC diff| (of A) <= 0.6%", "DendrogramPurity": "|DP diff| <= 1e-13",
                        "SphericalSilhouette": "|SS diff| <= 1e-15"}[f]
                if fx is None or fy is None:
                    rows.append((name, x + "/" + y, src, "UNDETERMINED", "not numeric in both"))
                    continue
                d = abs(fx - fy)
                if f == "TotalDasguptaCost":
                    fA = num(va.get(kk))
                    if not fA:
                        rows.append((name, x + "/" + y, src, "UNDETERMINED", "leg A's TDC not numeric or 0"))
                        continue
                    d = d / abs(fA)
                    rows.append((name, x + "/" + y, src, "HOLDS" if d <= bar else "FAILS", "%.6f%% of A" % (100 * d)))
                else:
                    rows.append((name, x + "/" + y, src, "HOLDS" if d <= bar else "FAILS", "%.6g" % d))
    lines = ["[P6 SCORE, DESCRIPTIVE, no bar on D9] %-31s %-5s %-7s %-12s %s" % r for r in rows]
    failing = [r for r in rows if r[3] == "FAILS"]
    und = [r for r in rows if r[3] == "UNDETERMINED"]
    state = "FAILED" if failing else "UNDETERMINED" if und else "HELD"
    lines.append("[P6] %s (%d clause-instances: %d hold, %d fail%s, %d undetermined)"
                 % (state, len(rows), len(rows) - len(failing) - len(und), len(failing),
                    (": " + "; ".join("%s %s %s" % (r[0], r[1], r[2]) for r in failing)) if failing else "", len(und)))
    return lines, state


def write_once(path, text):
    with open(path, "x", encoding="utf-8", newline="\n") as f:
        f.write(text)


def pair(rx, ry, stage, lx, ly, misses=None):
    crit = PAIRS.get((lx, ly))
    if crit is None:
        raise Refuse("the pair must be (A, B) for C1' or (A, A2) for C2, not (%s, %s)" % (lx, ly))
    if not os.path.isdir(stage):
        raise Refuse("stage dir %s does not exist" % stage)
    txt, js = os.path.join(stage, "d9b_compare.txt"), os.path.join(stage, "d9b_compare.json")
    for p in (txt, js) + tuple(os.path.join(stage, "pool_copy_%s" % l) for l in (lx, ly)):
        if os.path.exists(p):
            raise Refuse("%s exists (outputs are write-once)" % p)
    L = []

    def say(s):
        L.append(s)
        print(s, flush=True)
    say("[%s] %s: %s = %s ; %s = %s ; stage %s" % (VERSION, crit, lx, rx, ly, ry, stage))
    say("[DROPS] byte-compared (%d): %s" % (len(BYTE), BYTE))
    say("[DROPS] column drops: %s" % CSV_DROP)
    say("[DROPS] row drops: %s" % {k: {"key": v[0], "rows": v[1]} for k, v in ROW_DROP.items()})
    say("[DROPS] JSON key drops: %s" % JSON_DROP)
    say("[DROPS] table column drops: %s ; excluded from comparison (in the file set only): %s" % (POOL_DROP, sorted(EXCLUDED)))
    status, digest = {}, {}
    fx, fy = files_under(rx), files_under(ry)
    for rel in OBJECTS[:21]:
        px, py = (os.path.join(r, OUT, rel) for r in (rx, ry))
        ex, ey = os.path.isfile(px), os.path.isfile(py)
        if not ex and not ey:
            raise Refuse("listed file %s absent in BOTH legs (not comparable)" % rel)
        if ex != ey:
            status[rel] = "DIFFERS"
            digest[rel] = [sha_bytes(normalised_in(rel, px, lx)) if ex else None,
                           sha_bytes(normalised_in(rel, py, ly)) if ey else None]
            say("[%s] %-58s DIFFERS (present in %s only)" % (crit, rel, lx if ex else ly))
            continue
        a, b = normalised_in(rel, px, lx), normalised_in(rel, py, ly)
        status[rel] = "EQUAL" if a == b else "DIFFERS"
        digest[rel] = [sha_bytes(a), sha_bytes(b)]
        how = ("bytes" if rel in BYTE else "without columns %s" % CSV_DROP[rel] if rel in CSV_DROP
               else "without rows %s" % ROW_DROP[rel][1] if rel in ROW_DROP else "without %d declared keys" % len(JSON_DROP[rel]))
        say("[%s] %-58s (%s) %s %s %s %s %s" % (crit, rel, how, lx, digest[rel][0][:16], ly, digest[rel][1][:16], status[rel]))
    only = sorted(set(fx) ^ set(fy))
    listed = set(OBJECTS[:21]) | EXCLUDED
    extra = sorted(set(fx) - listed)
    status[FILESET] = "EQUAL" if not only else "DIFFERS"
    digest[FILESET] = [sha_bytes("\n".join(fx).encode()), sha_bytes("\n".join(fy).encode())]
    say("[%s-R2] %s: files under the outputDir: %s %d, %s %d; present in one leg only: %s; outside the declared list"
        " (compared nowhere, printed): %s -> %s" % (crit, FILESET, lx, len(fx), ly, len(fy),
                                                   ["%s (%s only)" % (p, lx if p in fx else ly) for p in only] or "none",
                                                   extra or "none", status[FILESET]))
    px_, dx = pool_readout(rx, stage, lx)
    py_, dy = pool_readout(ry, stage, ly)
    for t in TABLES:
        status[t] = "EQUAL" if px_[t] == py_[t] else "DIFFERS"
        digest[t] = [list(px_[t]), list(py_[t])]
        say("[%s-POOL] %s (dropped %s): %s %s rows %s, %s %s rows %s %s" % (crit, t, POOL_DROP.get(t, []), lx, px_[t][0], px_[t][1][:16],
                                                                          ly, py_[t][0], py_[t][1][:16], status[t]))
    for t in sorted(set(dx) | set(dy)):
        say("[DESCRIPTIVE, NOT %s] AG copy table %-20s %s %s %s %s %s" % (crit, t, lx, dx.get(t), ly, dy.get(t),
                                                                          "equal" if dx.get(t) == dy.get(t) else "DIFFERS"))
    vx, vy = dropped_values(rx), dropped_values(ry)
    for s in p6_lines("%s/%s" % (lx, ly), lx, ly, vx, vy, vx):
        say(s)
    if misses:
        m = [open(p).read().strip() if os.path.isfile(p) else "?" for p in misses]
        say("[V7] embedding misses %s %s (%s), %s %s (%s): %s" % (lx, m[0], misses[0], ly, m[1], misses[1],
                                                                 "EQUAL" if m[0] == m[1] and m[0] != "?" else "NOT EQUAL OR MISSING (VOID)"))
    else:
        say("[V7] not read here (no --misses given)")
    assert set(status) == set(OBJECTS)
    differing = [o for o in OBJECTS if status[o] == "DIFFERS"]
    held = len(differing) == 0
    say("[%s] differing: %d of %d objects (21 files + the file set + 2 pool tables): %s -> %s %s"
        % (crit, len(differing), len(OBJECTS), differing or "none", crit, "HELD" if held else "FAILED"))
    write_once(js, json.dumps({"version": VERSION, "criterion": crit, "labels": [lx, ly], "roots": [rx, ry],
                               "objects": OBJECTS, "status": status, "digest": digest, "differing": differing,
                               "dropped_values": {lx: vx, ly: vy}}, indent=1, sort_keys=True) + "\n")
    write_once(txt, "\n".join(L) + "\n")
    return 0 if held else 3


MAPPING = [
    "D9 DISCHARGED iff C1' HELD AND C2 HELD AND V1-V11 met",
    "THE CHANGE READ (the falsifier fires) iff S_AB contains an object NOT in S_AA  [F1: no merge; D9 FAILED on the change]",
    "D9 UNDETERMINED (a registered outcome) iff S_AA is non-empty and S_AB is a subset of S_AA",
    "(C1' HELD and C2 FAILED is UNDETERMINED by the rule above)",
    "F2: S_AA non-empty  [consequence: D9 UNDETERMINED, a new registration] (ruling A1: the UNDETERMINED consequence applies"
    " only when S_AB is a subset of S_AA)",
]


def load_readout(p):
    """D3 (READY d984724): a missing, unreadable, corrupt or malformed readout is an INSTRUMENT REFUSAL (exit 2), never a
    traceback."""
    try:
        with open(p, encoding="utf-8") as f:
            j = json.load(f)
    except (OSError, ValueError) as e:
        raise Refuse("readout %s cannot be read as JSON: %s: %s" % (p, type(e).__name__, e))
    ok = (isinstance(j, dict) and isinstance(j.get("labels"), list) and len(j["labels"]) == 2
          and isinstance(j.get("roots"), list) and len(j["roots"]) == 2 and isinstance(j.get("differing"), list)
          and isinstance(j.get("digest"), dict) and isinstance(j.get("dropped_values"), dict)
          and all(isinstance(j["digest"].get(o), list) and len(j["digest"][o]) == 2 for o in OBJECTS)
          and all(isinstance(j["dropped_values"].get(l), dict) for l in j["labels"]))
    if not ok:
        raise Refuse("readout %s is malformed (not a %s pair readout)" % (p, VERSION))
    return j


def verdict(j_ab, j_aa, out):
    if os.path.exists(out):
        raise Refuse("%s exists (write-once)" % out)
    ab, aa = load_readout(j_ab), load_readout(j_aa)
    if ab.get("criterion") != "C1'" or ab.get("labels") != ["A", "B"]:
        raise Refuse("%s is not a C1' (A, B) readout" % j_ab)
    if aa.get("criterion") != "C2" or aa.get("labels") != ["A", "A2"]:
        raise Refuse("%s is not a C2 (A, A2) readout" % j_aa)
    for j in (ab, aa):
        if j.get("objects") != OBJECTS or j.get("version") != VERSION:
            raise Refuse("a readout was not written by this object list / version")
    a1 = {o: ab["digest"][o][0] for o in OBJECTS}
    a2 = {o: aa["digest"][o][0] for o in OBJECTS}
    if a1 != a2 or ab["roots"][0] != aa["roots"][0]:
        raise Refuse("leg A differs between the two readouts (not the same leg A)")
    L = []

    def say(s):
        L.append(s)
        print(s, flush=True)
    s_ab, s_aa = set(ab["differing"]), set(aa["differing"])
    say("[%s --verdict] C1' readout %s ; C2 readout %s" % (VERSION, j_ab, j_aa))
    say("[VERDICT] S_AB (A vs B)  = %s (%d of 24) -> C1' %s" % (sorted(s_ab) or "empty", len(s_ab), "HELD" if not s_ab else "FAILED"))
    say("[VERDICT] S_AA (A vs A2) = %s (%d of 24) -> C2 %s" % (sorted(s_aa) or "empty", len(s_aa), "HELD" if not s_aa else "FAILED"))
    only_ab = sorted(s_ab - s_aa)
    f1 = bool(only_ab)
    und = bool(s_aa) and s_ab <= s_aa
    f2 = bool(s_aa)
    dis = not s_ab and not s_aa
    say("[VERDICT] the registered mapping (verbatim), each branch evaluated:")
    say("  %s -> %s" % (MAPPING[0], "C1' HELD AND C2 HELD: fires iff V1-V11 met (NOT checked by this script)" if dis else "does not fire"))
    say("  %s -> %s" % (MAPPING[1], "FIRES on %s" % only_ab if f1 else "does not fire"))
    say("  %s -> %s" % (MAPPING[2], "FIRES" if und else "does not fire"))
    say("  %s" % MAPPING[3])
    say("  %s -> %s" % (MAPPING[4], "FIRES on %s" % sorted(s_aa) if f2 else "does not fire"))
    for o in sorted(s_ab):
        say("[READING] %s: in S_AB, %s" % (o, "NOT in S_AA -> reads THE CHANGE (F1)" if o not in s_aa
                                           else "in S_AA -> reads NON-DETERMINISM (F2), never the change"))
    for o in sorted(s_aa - s_ab):
        say("[READING] %s: in S_AA only (A/A2 differ, A/B equal) -> non-determinism (F2); the A/B identity on it is not evidence" % o)
    if dis:
        rc, v = 0, ("D9 DISCHARGED on C1' and C2 (0 of 24 in both pairs), CONDITIONAL ON V1-V11 MET (not checked here; a failed V"
                    " VOIDS the run). Words of record if discharged: \"byte-inert on every compared field except DendrogramPurity,"
                    " SphericalSilhouette and TotalDasguptaCost, which are declared non-deterministic and NOT tested\"")
    elif f1:
        rc, v = 3, "THE CHANGE READ: F1 fires on %s; D9 FAILED on the change; no merge" % only_ab
        if f2:
            v += ("; F2 ALSO FIRED on %s (non-determinism disclosed; its UNDETERMINED consequence does not apply because"
                  " S_AB is not a subset of S_AA: registrar ruling A1)" % sorted(s_aa))
    elif und:
        rc, v = 6, "D9 UNDETERMINED: S_AA non-empty and S_AB a subset of S_AA; F2 fires; not attributed to the change; no merge; a new registration"
    else:
        raise Refuse("unmapped cell: instrument defect (S_AB %s, S_AA %s)" % (sorted(s_ab), sorted(s_aa)))
    say("[VERDICT] %s" % v)
    if f1 and f2:
        say("[LIMIT] one A/A2 pair can miss a rare non-determinism (Support (e)); a non-empty S_AA shows that this arm carries"
            " undeclared non-determinism, so the F1 reading on S_AB minus S_AA rests on ONE A/A2 pair and is stated at that"
            " strength (registrar ruling A1 (c))")
    va, vb, v2 = ab["dropped_values"]["A"], ab["dropped_values"]["B"], aa["dropped_values"]["A2"]
    if va != aa["dropped_values"]["A"]:
        raise Refuse("leg A's dropped values differ between the two readouts")
    for tag, lx, ly, x, y in (("A/B", "A", "B", va, vb), ("A/A2", "A", "A2", va, v2), ("B/A2", "B", "A2", vb, v2)):
        for s in p6_lines(tag, lx, ly, x, y, va):
            say(s)
    p6l, _p6 = p6_score(va, vb, v2)
    for s in p6l:
        say(s)
    write_once(out, "\n".join(L) + "\n")
    return rc


def main(argv):
    try:
        if argv and argv[0] == "--verdict":
            if len(argv) != 4:
                raise Refuse("usage: --verdict <C1' json> <C2 json> <out txt>")
            return verdict(*argv[1:4])
        misses = None
        if "--misses" in argv:
            i = argv.index("--misses")
            misses, argv = argv[i + 1:i + 3], argv[:i] + argv[i + 3:]
            if len(misses) != 2:
                raise Refuse("--misses needs two files")
        if len(argv) != 5:
            raise Refuse("usage: <X root> <Y root> <stage> <X label> <Y label> [--misses X Y]")
        return pair(*argv, misses=misses)
    except Refuse as e:
        print("[%s] INSTRUMENT REFUSAL (a failed precondition; nothing scored): %s" % (VERSION, e), flush=True)
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
