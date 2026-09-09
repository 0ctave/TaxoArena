"""D4 — domain arrival (docs/v2_validation_plan.md "D4", registered 2026-09-09).

Arms arrive_philosophy_s137 / arrive_law_s137: the domain's questions are in the corpus but get
no depth-1 anchor. Region composition is EXACT (leaf queryIds -> embeddings_cache.queries
.ground_truth_category); certification from the arm's site-null CSV; held-out routing from the
run's own trickle validation (MAIN_routing_diagnostics.txt, per query: true domain + top-1 leaf).
REGISTERED: ARRIVES iff a certified split whose region is >= 60% the excluded domain exists AND
>= 50% of the domain's held-out questions route under it; PARKED iff the domain's train questions
sit mostly (>= 50%) in residual pools; else ABSORBED (spread over host anchors).
Prediction: Law ARRIVES; Philosophy ABSORBED into Psychology/History.

  python tools/analysis/d4_arrival.py [philosophy] [law]
"""
import os, sys, re, csv, json, sqlite3
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SWEEP = os.path.join(ROOT, "experiment_results", "dimsweep4")
SNAP_DB = os.path.join(ROOT, "snapshots.db")
EMB_DB = os.path.join(ROOT, "embeddings_cache.db")
SHARE = 0.60
ROUTE = 0.50


def snapshot_id(run_dir):
    ids = re.findall(r"Snapshot ID: (\S+)", open(os.path.join(run_dir, "headless_run.log"), encoding="utf-8", errors="replace").read())
    return ids[-1] if ids else None


def load_graph(snap_id):
    c = sqlite3.connect("file:%s?mode=ro" % SNAP_DB, uri=True)
    g = json.loads(c.execute("SELECT graph FROM snapshots WHERE id=?", (snap_id,)).fetchone()[0])
    lst = g["nodes"]; lst = lst if isinstance(lst, list) else list(lst.values())
    return {n["id"]: n for n in lst}


def query_categories():
    c = sqlite3.connect("file:%s?mode=ro" % EMB_DB, uri=True)
    return {i: (cat or "").lower() for i, cat in c.execute("SELECT id, ground_truth_category FROM queries")}


def held_out_routes(run_dir):
    """(true domain, top-1 leaf id) per held-out query from the trickle diagnostics."""
    out = []; dom = None
    for line in open(os.path.join(run_dir, "validation", "MAIN_routing_diagnostics.txt"), encoding="utf-8", errors="replace"):
        if line.startswith("True Domain:"):
            dom = line.split(":", 1)[1].strip().lower()
        elif line.startswith("Top-1 Leaf:"):
            m = re.search(r"\(ID: (\S+)\)", line)
            out.append((dom, m.group(1) if m else None)); dom = None
    return out


def analyze(domain):
    tag = "arrive_%s_s137" % domain
    run_dir = os.path.join(SWEEP, tag, "seed_137")
    if not os.path.exists(os.path.join(run_dir, "dag_snapshots.jsonl")):
        print("== D4 %s: build not present ==" % tag); return
    snap = snapshot_id(run_dir); nodes = load_graph(snap); qcat = query_categories()
    parent = {c: n["id"] for n in nodes.values() for c in n.get("childIds", [])}
    def anchor(nid):
        n = nodes[nid]
        while n["depth"] > 1: n = nodes[parent[n["id"]]]
        return n["label"]
    def desc_leaves(nid):
        n = nodes[nid]
        if not n.get("childIds"): return [nid]
        return [l for c in n["childIds"] for l in desc_leaves(c)]
    comp = {}
    for nid in nodes:
        cnt = Counter()
        for l in desc_leaves(nid):
            for q in nodes[l].get("queryIds", []): cnt[qcat.get(q, "?")] += 1
        comp[nid] = cnt
    site = {}
    csvp = os.path.join(SWEEP, "site_null_%s.csv" % tag)
    if os.path.exists(csvp):
        for row in csv.DictReader(open(csvp, newline="", encoding="utf-8")):
            site[row["node_id"]] = row
    anchors = [nodes[c]["label"] for c in nodes[[n for n in nodes if nodes[n]["depth"] == 0][0]]["childIds"]]
    print("== D4 %s | snapshot %s | %d nodes, %d leaves | anchors: %s | site-null rows %d ==" % (tag, snap, len(nodes), sum(1 for n in nodes.values() if not n.get("childIds")), ", ".join(anchors), len(site)))
    assert domain.capitalize() not in anchors and domain not in [a.lower() for a in anchors], "excluded domain was anchored"
    train_total = sum(cnt[domain] for nid, cnt in comp.items() if nodes[nid]["depth"] == 0)
    residual = 0
    for n in nodes.values():
        residual += sum(1 for q in n.get("residualQueries", []) if isinstance(q, str) and qcat.get(q, qcat.get("q_" + q, "")) == domain)
    print("  %s train questions in leaves: %d | in residual pools: %d" % (domain, train_total, residual))
    # host anchors of the domain's train questions
    host = Counter()
    for nid, cnt in comp.items():
        if nodes[nid]["depth"] == 1: host[nodes[nid]["label"]] = cnt[domain]
    print("  host anchors (train side): %s" % ", ".join("%s %d (%.0f%%)" % (a, k, 100 * k / max(1, train_total)) for a, k in host.most_common(6) if k))
    # candidate regions: any non-root node with >= 60% excluded-domain share
    cands = []
    for nid, cnt in comp.items():
        n = sum(cnt.values())
        if nodes[nid]["depth"] >= 1 and n >= 20 and cnt[domain] / n >= SHARE:
            r = site.get(nid); cert = (r or {}).get("cert_site_p95", "n/a")
            cands.append((nid, n, cnt[domain] / n, cert, nodes[nid]["depth"], bool(nodes[nid].get("childIds"))))
    print("  regions >= %.0f%% %s (n >= 20): %d" % (100 * SHARE, domain, len(cands)))
    for nid, n, s, cert, d, internal in sorted(cands, key=lambda x: -x[1]):
        print("     %s depth %d %-8s n=%4d share %.2f cert_site_p95=%s under %s" % (nid, d, "split" if internal else "leaf", n, s, cert, anchor(nid) if d > 1 else "(anchor)"))
    certified = [c for c in cands if c[5] and str(c[3]).lower() == "true"]
    routes = held_out_routes(run_dir)
    dom_routes = [(d, l) for d, l in routes if d == domain]
    print("  held-out %s questions: %d | routed to anchors: %s" % (domain, len(dom_routes), ", ".join("%s %d" % (a, k) for a, k in Counter(anchor(l) for _, l in dom_routes if l in nodes).most_common(5))))
    under = 0
    if certified:
        cert_leaves = set(l for c in certified for l in desc_leaves(c[0]))
        under = sum(1 for _, l in dom_routes if l in cert_leaves)
        print("  certified >= %.0f%% regions: %s | held-out %s routed under them: %d/%d = %.1f%%" % (100 * SHARE, ", ".join(c[0] for c in certified), domain, under, len(dom_routes), 100 * under / max(1, len(dom_routes))))
    frac_under = under / max(1, len(dom_routes)); frac_res = residual / max(1, residual + train_total)
    if certified and frac_under >= ROUTE: verdict = "ARRIVES"
    elif frac_res >= ROUTE: verdict = "PARKED"
    else: verdict = "ABSORBED"
    print("  REGISTERED VERDICT: %s  (certified regions %d, held-out under them %.1f%%, residual share %.1f%%)" % (verdict, len(certified), 100 * frac_under, 100 * frac_res))


if __name__ == "__main__":
    for d in (sys.argv[1:] or ["philosophy", "law"]):
        analyze(d)
