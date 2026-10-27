import sqlite3, json, re, sys
DB = sys.argv[1]; ROOT = sys.argv[2]
con = sqlite3.connect("file:%s?mode=ro" % DB, uri=True)
def sid(d, m):
    return sorted(set(re.findall(r"Snapshot ID: (\S+)", open("%s/%s/%s/seed_42/headless_run.log" % (ROOT, d, m), encoding="utf-8", errors="replace").read())))[0]
def row(s):
    r = con.execute("SELECT graph, metrics, settings, reserved_queries, config FROM snapshots WHERE id=?", (s,)).fetchone()
    return {k: (json.loads(v) if v else None) for k, v in zip(("graph","metrics","settings","reserved_queries","config"), r)}
def strip(o):
    if isinstance(o, dict): return {k: strip(v) for k, v in o.items() if k not in ("configSha256Lf","config_sha256_lf")}
    if isinstance(o, list): return [strip(v) for v in o]
    return o
out = []
def walk(a, b, p, lim=[0]):
    if type(a) != type(b): out.append((p, repr(a)[:120], repr(b)[:120])); return
    if isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b: out.append((p+"/"+k, "missing" if k not in a else "present", "missing" if k not in b else "present"))
            else: walk(a[k], b[k], p+"/"+k)
    elif isinstance(a, list):
        if len(a) != len(b): out.append((p+"[len]", len(a), len(b)))
        if a != b and len(a) == len(b) and all(not isinstance(x,(dict,list)) for x in a) and sorted(map(repr,a)) == sorted(map(repr,b)):
            out.append((p, "SAME MULTISET, ORDER DIFFERS (n=%d)" % len(a), "")); return
        for i, (x, y) in enumerate(zip(a, b)): walk(x, y, "%s[%d]" % (p, i))
    elif a != b: out.append((p, repr(a)[:120], repr(b)[:120]))
for m in sys.argv[3:]:
    out.clear()
    a, b = row(sid("B0", m)), row(sid("B0p", m))
    print("=== %s %s vs %s" % (m, sid("B0", m), sid("B0p", m)))
    for k in a:
        ka, kb = strip(a[k]), strip(b[k])
        print("  %s equal(stamp-sha stripped)=%s raw_equal=%s" % (k, ka == kb, a[k] == b[k]))
    for k in a: walk(strip(a[k]), strip(b[k]), k)
    # generalise paths
    from collections import Counter
    c = Counter(re.sub(r"\[\d+\]", "[*]", p) for p, *_ in out)
    for p, n in c.most_common(25): print("   %5d  %s" % (n, p))
    for p, x, y in out[:12]: print("     e.g.", p, "|", x, "|", y)
