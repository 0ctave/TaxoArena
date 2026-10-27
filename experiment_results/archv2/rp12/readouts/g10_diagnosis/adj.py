import sqlite3, json, re, sys
DB, ROOT = sys.argv[1], sys.argv[2]
con = sqlite3.connect("file:%s?mode=ro" % DB, uri=True)
def sid(d, m): return sorted(set(re.findall(r"Snapshot ID: (\S+)", open("%s/%s/%s/seed_42/headless_run.log" % (ROOT, d, m), encoding="utf-8", errors="replace").read())))[0]
def g(s): return json.loads(con.execute("SELECT graph FROM snapshots WHERE id=?", (s,)).fetchone()[0])["nodes"]
for m in sys.argv[3:]:
    A, B = g(sid("B0", m)), g(sid("B0p", m))
    tot = keep = 0; pos_moved = 0; n = 0
    for x, y in zip(A, B):
        qa, qb = x.get("queryIds") or [], y.get("queryIds") or []
        if len(qa) < 2: continue
        adjB = set(zip(qb, qb[1:]))
        for p in zip(qa, qa[1:]):
            tot += 1; keep += p in adjB
        pos_moved += sum(1 for i, q in enumerate(qa) if qb[i] != q); n += len(qa)
    print("%-14s adjacent pairs of B0 kept adjacent in B0' = %d/%d (%.1f%%); items at a different position %d/%d" % (m, keep, tot, 100*keep/tot, pos_moved, n))
