"""LCB-D9-BYTE-INERTNESS operator helper 3/3: C1 BYTE-IDENTITY, leg A vs leg B (programme L18662-L18872). Read-only on the
legs' outputs; the legs' AG cache copies are copied again (DB + -wal together) into the stage dir and only THOSE copies are
checkpointed and read. Writes <stage>/d9_compare.txt. Run it BEFORE the R3 probe.

usage: python d9_compare.py <legA root> <legB root> <stage dir>
C1 HELD iff 0 of the 21 listed files differ, the file sets agree (registrar reading R2) and the reserved_pool* readout is
equal; the exit code is 0 iff C1 HELD (a FAILED C1 is an outcome, exit 3, never a crash).
"""
import csv, hashlib, io, json, os, shutil, sqlite3, sys

OUT = os.path.join("experiment_results", "topic_partition", "ag_news_smoke_s42")
BYTE = ["seed_42/dag_snapshots.jsonl", "seed_42/gate_ids.json", "seed_42/fixed_point_certificate.txt"] + \
       ["seed_42/validation/" + f for f in ("MAIN_bridge_quality.csv", "MAIN_centroid_routing_results.csv", "MAIN_graph_validity.csv",
                                            "MAIN_heldout_leaf_support.csv", "MAIN_migration_flow_matrix.csv",
                                            "MAIN_routing_calibration.csv", "MAIN_routing_diagnostics.txt", "MAIN_taxonomy_quality.csv",
                                            "MAIN_trickle_validation_results.csv", "bridge_nodes.csv", "bridge_residuals.csv")] + \
       ["seed_42/diagnostics/" + f for f in ("dag_snapshots.jsonl", "proposals.csv", "rank_history.csv", "config.toml")]
CSV_DROP = {"seed_42/diagnostics/iteration_metrics.csv": ["wall_ms"], "tuning_ledger.csv": ["CommitSHA"]}
JSON_DROP = {"seed_42/diagnostics/run_manifest.json": ["commit", "branch", "dirty", "dirty_src", "dirty_src_files", "dirty_other",
                                                       "dirty_other_files", "dirty_files", "started_at_millis", "finished_at_millis",
                                                       "duration_ms", "config_path", "proposal_memo_digest_ms"]}
EXCLUDED = {"seed_42/headless_run.log", "seed_42/diagnostics/headless_run.log", "seed_42/performance_report.json"}
POOL_DROP = {"reserved_pool_meta": ["created_at"]}


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def csv_drop(b, cols):
    rows = list(csv.reader(io.StringIO(b.decode("utf-8"), newline="")))
    hdr = rows[0]
    missing = [c for c in cols if c not in hdr]
    if missing:
        raise SystemExit("[C1] declared column(s) %s absent from the header %s" % (missing, hdr))
    keep = [i for i, h in enumerate(hdr) if h not in cols]
    return "\n".join("\x1f".join(r[i] for i in keep if i < len(r)) for r in rows).encode("utf-8")


def json_drop(b, keys):
    d = json.loads(b.decode("utf-8"))
    for k in keys:
        d.pop(k, None)
    return json.dumps(d, sort_keys=True).encode("utf-8")


def files_under(root):
    base = os.path.join(root, OUT)
    return sorted(os.path.relpath(os.path.join(d, f), base).replace("\\", "/") for d, _s, fs in os.walk(base) for f in fs)


def pool_readout(root, stage, leg):
    d = os.path.join(stage, "pool_copy_%s" % leg)
    os.makedirs(d)
    src = os.path.join(root, "ag_news_smoke_cache_v1.db")
    for s in ("", "-wal"):
        if os.path.exists(src + s):
            shutil.copyfile(src + s, os.path.join(d, "ag.db" + s))
    con = sqlite3.connect(os.path.join(d, "ag.db"))
    con.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    out = {}
    for t in ("reserved_pool", "reserved_pool_meta"):
        cols = [r[1] for r in con.execute("PRAGMA table_info(%s)" % t)]
        keep = [c for c in cols if c not in POOL_DROP.get(t, [])]
        rows = con.execute("SELECT %s FROM %s ORDER BY %s" % (", ".join(keep), t, ", ".join(keep))).fetchall()
        out[t] = (len(rows), sha_bytes(repr(rows).encode("utf-8")))
    # DESCRIPTIVE ONLY (NOT C1): a row digest of every table of the copy
    desc = {}
    for t, in con.execute("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"):
        rows = con.execute("SELECT * FROM \"%s\"" % t).fetchall()
        desc[t] = (len(rows), sha_bytes(repr(sorted(map(repr, rows))).encode("utf-8"))[:16])
    con.close()
    return out, desc


def main(la, lb, stage):
    L = []

    def say(s):
        L.append(s)
        print(s, flush=True)
    diff = 0
    for rel in BYTE:
        a, b = (open(os.path.join(r, OUT, rel), "rb").read() for r in (la, lb))
        ha, hb = sha_bytes(a), sha_bytes(b)
        diff += ha != hb
        say("[C1] %-58s A %s B %s %s" % (rel, ha[:16], hb[:16], "EQUAL" if ha == hb else "DIFFERS"))
    for rel, cols in CSV_DROP.items():
        a, b = (csv_drop(open(os.path.join(r, OUT, rel), "rb").read(), cols) for r in (la, lb))
        diff += a != b
        say("[C1] %-58s (without %s) A %s B %s %s" % (rel, cols, sha_bytes(a)[:16], sha_bytes(b)[:16], "EQUAL" if a == b else "DIFFERS"))
    for rel, keys in JSON_DROP.items():
        a, b = (json_drop(open(os.path.join(r, OUT, rel), "rb").read(), keys) for r in (la, lb))
        diff += a != b
        say("[C1] %-58s (without %d declared keys) A %s B %s %s" % (rel, len(keys), sha_bytes(a)[:16], sha_bytes(b)[:16],
                                                                   "EQUAL" if a == b else "DIFFERS"))
    fa, fb = files_under(la), files_under(lb)
    only = sorted(set(fa) ^ set(fb))
    listed = set(BYTE) | set(CSV_DROP) | set(JSON_DROP) | EXCLUDED
    extra = sorted(set(fa) - listed)
    say("[C1-R2] files under the outputDir: A %d, B %d; present in one leg only: %s; outside the declared list (compared"
        " nowhere, printed): %s" % (len(fa), len(fb), only or "none", extra or "none"))
    diff += len(only)
    pa, da = pool_readout(la, stage, "A")
    pb, db = pool_readout(lb, stage, "B")
    for t in pa:
        eq = pa[t] == pb[t]
        diff += not eq
        say("[C1-POOL] %s (dropped %s): A %s rows %s, B %s rows %s %s" % (t, POOL_DROP.get(t, []), pa[t][0], pa[t][1][:16],
                                                                       pb[t][0], pb[t][1][:16], "EQUAL" if eq else "DIFFERS"))
    for t in sorted(set(da) | set(db)):
        say("[DESCRIPTIVE, NOT C1] AG copy table %-20s A %s B %s %s" % (t, da.get(t), db.get(t), "equal" if da.get(t) == db.get(t) else "DIFFERS"))
    ma = open(os.path.join(stage, "d9_misses_A.txt")).read().strip() if os.path.exists(os.path.join(stage, "d9_misses_A.txt")) else "?"
    mb = open(os.path.join(stage, "d9_misses_B.txt")).read().strip() if os.path.exists(os.path.join(stage, "d9_misses_B.txt")) else "?"
    say("[V7] embedding misses A %s, B %s: %s" % (ma, mb, "EQUAL" if ma == mb and ma != "?" else "NOT EQUAL (VOID)"))
    say("[C1] differing: %d (21 files + file-set + 2 pool tables) -> C1 %s" % (diff, "HELD" if diff == 0 else "FAILED"))
    with open(os.path.join(stage, "d9_compare.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    raise SystemExit(0 if diff == 0 else 3)


if __name__ == "__main__":
    main(*sys.argv[1:4])
