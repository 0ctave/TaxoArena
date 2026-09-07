"""E1 (tree-vs-DAG phase): does reserved-pool overlap mass concentrate on leaf pairs?

Analysis of the committed reserved_leaf_assignments.csv: for each multi-leaf
question, the (primary, secondary) leaf pair; concentration = share of second-
membership mass on the top-10 pairs, tested against a marginal-preserving
permutation null (secondary column shuffled, self-pairs dropped, B=2000, seed 42).

2026-09-07 result: 411/3,445 multi-leaf (11.9%); top-10 pair share 17.8% vs null
median 5.1% (p = 0.0005); top pairs are semantically real and match H5's routing
confusion flows (Math<->CS statistics, Chem<->Engineering thermodynamics,
Phys<->Chem quantum). CAVEAT: the null is NOT beam-aware — the routing beam
censors observable overlap, so the cross-anchor comparison is only descriptive;
the beam-aware v2 and seed-recurrence check ride on the H9 counterfactual runs.
Verdict: concentrated overlap exists -> E2 (held-out likelihood with placebo
edges) is warranted, with these pairs as bridge candidates.
"""
import sys, os, csv, random
from collections import defaultdict, Counter
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rejudge_grok as rj

def main():
    nodes = rj.load_nodes()
    parent = {}
    for n in nodes.values():
        for c in n.get("childIds", []): parent[c] = n["id"]
    def anchor(nid):
        n = nodes[nid]
        while n["depth"] > 1: n = nodes[parent[n["id"]]]
        return n["label"]
    label = {n["id"]: n["label"] for n in nodes.values()}
    per_q = defaultdict(list)
    with open(os.path.join(ROOT, 'reserved_leaf_assignments.csv'), newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            per_q[int(row['question_id'])].append((float(row['weight'].replace(',', '.')), row['leaf_id']))
    multi = {q: sorted(ls, reverse=True) for q, ls in per_q.items() if len(ls) >= 2}
    print("E1: reserved %d | multi-leaf %d (%.1f%%)" % (len(per_q), len(multi), 100*len(multi)/len(per_q)))
    prim = [ls[0][1] for ls in multi.values()]
    sec = [ls[1][1] for ls in multi.values()]
    pairs = Counter(tuple(sorted(p)) for p in zip(prim, sec))
    n = len(prim)
    top10 = sum(k for _, k in pairs.most_common(10))
    print("distinct pairs %d | top-10 share %.1f%% | cross-anchor %.1f%%"
          % (len(pairs), 100*top10/n,
             100*sum(k for (a, b), k in pairs.items() if anchor(a) != anchor(b))/n))
    for (a, b), k in pairs.most_common(10):
        print("  %3d  %-45s | %-45s %s" % (k, label[a][:45], label[b][:45],
              "CROSS" if anchor(a) != anchor(b) else "within-" + anchor(a)[:10]))
    rng = random.Random(42)
    B = 2000
    null = []
    for _ in range(B):
        s = sec[:]
        rng.shuffle(s)
        pc = Counter(tuple(sorted((p, q))) for p, q in zip(prim, s) if p != q)
        null.append(sum(k for _, k in pc.most_common(10)))
    null.sort()
    p = (1 + sum(1 for v in null if v >= top10)) / (1 + B)
    print("top-10 observed %d vs null median %d p95 %d -> p = %.4f"
          % (top10, null[B//2], null[int(0.95*B)], p))

if __name__ == "__main__":
    main()
