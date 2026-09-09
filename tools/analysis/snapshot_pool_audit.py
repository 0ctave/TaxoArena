"""AUDIT — for every snapshot, does the stored reserved list match the pool its own run activated?

  python tools/analysis/snapshot_pool_audit.py
"""
import os, re, json, glob, sqlite3, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def pool_id(ids_by_domain):
    judge = {d: [q for q in ids if q > 0] for d, ids in ids_by_domain.items()}
    judge = {d: v for d, v in judge.items() if v}
    canon = "\n".join(sorted("%s:%d" % (d, q) for d, ids in judge.items() for q in ids))
    return "p" + hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16], sum(len(v) for v in judge.values())


def run_logs():
    """snapshot id -> first 'Reserved pool ... active' line of the run log that saved it."""
    out = {}
    for f in glob.glob(os.path.join(ROOT, "experiment_results", "**", "headless_run.log"), recursive=True):
        try:
            txt = open(f, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        snaps = re.findall(r"Snapshot ID: (\S+)", txt)
        pools = re.findall(r"Reserved pool '([a-z0-9]+)' active", txt)
        for s in snaps:
            out.setdefault(s, (pools[0] if pools else None, os.path.relpath(f, ROOT)))
    return out


def main():
    logs = run_logs()
    rows = []
    for db in ("snapshots.db", "snapshots_frozen.db"):
        p = os.path.join(ROOT, db)
        if not os.path.exists(p):
            continue
        c = sqlite3.connect("file:%s?mode=ro" % p, uri=True)
        for sid, raw, uuid in c.execute("SELECT id, reserved_queries, log_uuid FROM snapshots"):
            stored = None; n = 0
            if raw:
                try:
                    stored, n = pool_id(json.loads(raw))
                except Exception:
                    stored = "unparseable"
            logged, src = logs.get(sid, (None, None))
            if logged is None and uuid:
                lp = os.path.join(ROOT, "snapshots", "logs", uuid + ".log")
                if os.path.exists(lp):
                    m = re.search(r"Reserved pool '([a-z0-9]+)' active", open(lp, encoding="utf-8", errors="replace").read())
                    logged, src = (m.group(1) if m else None), "snapshots/logs"
            status = "?" if (stored is None or logged is None) else ("OK" if stored == logged else "MISMATCH")
            rows.append((db, sid, stored, n, logged, status, src))
    print("%-19s %-40s %-18s %5s %-18s %-8s %s" % ("db", "snapshot", "stored pool", "n", "run-logged pool", "status", "log"))
    for r in sorted(rows, key=lambda r: r[1]):
        print("%-19s %-40s %-18s %5d %-18s %-8s %s" % (r[0], r[1], r[2] or "-", r[3], r[4] or "-", r[5], r[6] or "-"))
    mm = [r for r in rows if r[5] == "MISMATCH"]
    print("\nsnapshots %d | checked %d | MISMATCH %d: %s" % (len(rows), sum(1 for r in rows if r[5] != "?"), len(mm), [r[1] for r in mm]))


if __name__ == "__main__":
    main()
