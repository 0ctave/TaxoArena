"""THREAD-CAP B2/B3 operator helper: per-table sha256 over SELECT * ORDER BY rowid (repr(row)), read in BOTH views
(immutable=1 and mode=ro), per the construction-writes-cache-dbs rule. Read-only. usage: table_pins.py <db> [<db> ...]"""
import hashlib, os, sqlite3, sys
for db in sys.argv[1:]:
    p = os.path.abspath(db).replace("\\", "/")
    for view in ("immutable=1", "mode=ro"):
        con = sqlite3.connect("file:%s?%s" % (p, view), uri=True)
        tabs = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        for t in tabs:
            h, n = hashlib.sha256(), 0
            try:
                cur = con.execute('SELECT * FROM "%s" ORDER BY rowid' % t)
            except sqlite3.OperationalError:
                cur = con.execute('SELECT * FROM "%s"' % t)
            for r in cur:
                h.update(repr(r).encode()); n += 1
            print("PIN %s [%s] %s rows=%d sha256=%s" % (os.path.basename(db), view, t, n, h.hexdigest()), flush=True)
        con.close()
