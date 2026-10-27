import sqlite3, json, re, sys
DB, ROOT = sys.argv[1], sys.argv[2]
con = sqlite3.connect("file:%s?mode=ro" % DB, uri=True)
def sid(d, m): return sorted(set(re.findall(r"Snapshot ID: (\S+)", open("%s/%s/%s/seed_42/headless_run.log" % (ROOT, d, m), encoding="utf-8", errors="replace").read())))[0]
def row(s):
    g, mt = con.execute("SELECT graph, metrics FROM snapshots WHERE id=?", (s,)).fetchone(); return json.loads(g), json.loads(mt)
for m in sys.argv[3:]:
    (ga, ma), (gb, mb) = row(sid("B0", m)), row(sid("B0p", m))
    na, nb = ga["nodes"], gb["nodes"]
    ids_eq = [x["id"] for x in na] == [x["id"] for x in nb]
    order = memb = withq = 0
    for x, y in zip(na, nb):
        qa, qb = x.get("queryIds") or [], y.get("queryIds") or []
        if qa: withq += 1
        if qa != qb:
            if sorted(qa) == sorted(qb): order += 1
            else: memb += 1
        if {k: v for k, v in x.items() if k != "queryIds"} != {k: v for k, v in y.items() if k != "queryIds"}: memb += 1000
    leaves = sum(1 for x in na if not x.get("childIds") and not x.get("children"))
    print("%-12s nodes=%d same-id-seq=%s nodes-with-queries=%d order-only=%d membership-or-other=%d" % (m, len(na), ids_eq, withq, order, memb))
    for k in sorted(ma):
        if ma[k] != mb.get(k): print("     %-20s %r -> %r  rel=%.2e" % (k, ma[k], mb[k], abs(ma[k]-mb[k])/max(abs(ma[k]),1e-300)))
