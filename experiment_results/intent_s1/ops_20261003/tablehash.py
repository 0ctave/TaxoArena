"""Per-table sha256 (repr of rows ORDER BY rowid/all cols) in two views (immutable=1 and mode=ro); prints sidecar sizes. Read-only."""
import hashlib, os, sqlite3, sys
def tables(p, uri):
    con = sqlite3.connect(uri, uri=True)
    try:
        out = {}
        for (t,) in con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"):
            cols = [r[1] for r in con.execute('PRAGMA table_info("%s")' % t)]
            h = hashlib.sha256(); n = 0
            for row in con.execute('SELECT * FROM "%s" ORDER BY %s' % (t, ",".join('"%s"' % c for c in cols))):
                h.update(repr(row).encode()); n += 1
            out[t] = (n, h.hexdigest()[:16])
        return out
    finally:
        con.close()
for p in sys.argv[1:]:
    p = os.path.abspath(p).replace("\\", "/")
    side = {s: (os.path.getsize(p + s) if os.path.exists(p + s) else None) for s in ("-wal", "-journal", "-shm")}
    a = tables(p, "file:%s?mode=ro&immutable=1" % p)
    b = tables(p, "file:%s?mode=ro" % p) if not side["-wal"] else a
    print("%s sidecars=%s views_agree=%s" % (p, side, a == b))
    for t, (n, h) in a.items():
        print("  %s %d %s" % (t, n, h))
