"""T3 — routing inflation of the pool of record (docs/v2_validation_plan.md "T3", registered 2026-09-09).

The frozen tree was built with p8a29 withheld; the arena judged p2dca, 71% of which is on the
tree's train side. `routeReserved` on the frozen snapshot with p8a29 activated gives the tree's
routing of questions it never saw. Readout: primary-anchor purity of p8a29 (held-out) vs p2dca
(in-sample 71%; H5 = 73.6%), plus the purity of p2dca split into its CLEAN (in both pools) and
CONTAMINATED (train-side) parts, and the leaf-assignment agreement on the 1,020 overlap.
REGISTERED: the in-sample figure overstates held-out purity by >= 3pp.

  python tools/analysis/t3_routing_inflation.py            # adjudicates once the p8a29 CSV exists
"""
import os, sys, csv
from collections import Counter, defaultdict
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rejudge_grok as rj

P2DCA = "p2dca21ab5f4ef3ae"
P8A29 = "p8a29d8f3ff75aa55"
CSV_P2DCA = os.path.join(ROOT, "reserved_leaf_assignments.csv")
CSV_P8A29 = os.path.join(ROOT, "experiment_results", "dimsweep4", "frozen_p8a29_leaf_assignments.csv")


def primary(path):
    best = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            q = int(row["question_id"]); w = float(row["weight"].replace(",", "."))
            if q not in best or w > best[q][0]:
                best[q] = (w, row["leaf_id"], row["category"])
    return best


def anchor_fn(nodes):
    parent = {c: n["id"] for n in nodes.values() for c in n.get("childIds", [])}
    def anchor(nid):
        n = nodes[nid]
        while n["depth"] > 1:
            n = nodes[parent[n["id"]]]
        return n["label"]
    return anchor


def purity(best, anchor, keys=None):
    keys = list(best) if keys is None else [q for q in keys if q in best]
    agree = sum(anchor(best[q][1]).lower() == best[q][2].lower() for q in keys)
    return agree, len(keys)


def wilson(k, n, z=1.96):
    if n == 0: return (0.0, 0.0)
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return c - h, c + h


def main():
    nodes = rj.load_nodes(); anchor = anchor_fn(nodes)
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    pool = {pid: {r[0] for r in ev.execute("SELECT question_id FROM reserved_pool WHERE pool_id=?", (pid,))} for pid in (P2DCA, P8A29)}
    clean = pool[P2DCA] & pool[P8A29]
    b2 = primary(CSV_P2DCA)
    assert set(b2) <= pool[P2DCA] and len(b2) >= 0.99 * len(pool[P2DCA]), "root CSV is not the p2dca routing"
    k, n = purity(b2, anchor); kc, nc = purity(b2, anchor, clean); kx, nx = purity(b2, anchor, pool[P2DCA] - clean)
    print("=== T3: routing inflation of the pool of record (frozen tree %s) ===" % rj.SNAP_ID)
    print("  p2dca (arena pool, in-sample 71%%): purity %.1f%% (%d/%d)  [H5 reported 73.6%%]" % (100 * k / n, k, n))
    print("     CLEAN part (held-out for the tree):     %.1f%% (%d/%d)  95%% CI [%.1f, %.1f]" % ((100 * kc / nc, kc, nc) + tuple(100 * x for x in wilson(kc, nc))))
    print("     CONTAMINATED part (train side, in-sample): %.1f%% (%d/%d)  95%% CI [%.1f, %.1f]" % ((100 * kx / nx, kx, nx) + tuple(100 * x for x in wilson(kx, nx))))
    print("     in-sample minus clean: %+.1fpp" % (100 * (kx / nx - kc / nc)))
    if not os.path.exists(CSV_P8A29):
        print("  p8a29 routing CSV not present yet (%s) — clean/contaminated split above is the free preview; the registered contrast is p8a29 vs p2dca." % CSV_P8A29)
        return
    b8 = primary(CSV_P8A29)
    assert set(b8) <= pool[P8A29] and len(b8) >= 0.99 * len(pool[P8A29]), "p8a29 CSV does not cover the p8a29 pool"
    k8, n8 = purity(b8, anchor)
    lo8, hi8 = wilson(k8, n8)
    print("  p8a29 (the tree's TRUE held-out pool): purity %.1f%% (%d/%d)  95%% CI [%.1f, %.1f]" % (100 * k8 / n8, k8, n8, 100 * lo8, 100 * hi8))
    diff = 100 * (k / n - k8 / n8)
    print("  in-sample (p2dca) minus held-out (p8a29): %+.1fpp -> REGISTERED (>= 3pp overstatement): %s" % (diff, "PASS" if diff >= 3.0 else "FAIL"))
    common = [q for q in clean if q in b2 and q in b8]
    same_leaf = sum(b2[q][1] == b8[q][1] for q in common); same_anchor = sum(anchor(b2[q][1]) == anchor(b8[q][1]) for q in common)
    print("  overlap questions routed in both runs: n=%d | same leaf %.1f%% | same anchor %.1f%% (routing determinism check)" % (len(common), 100 * same_leaf / max(1, len(common)), 100 * same_anchor / max(1, len(common))))
    per = defaultdict(lambda: [0, 0, 0, 0])
    for q, (w, leaf, cat) in b2.items():
        per[cat][0] += anchor(leaf).lower() == cat.lower(); per[cat][1] += 1
    for q, (w, leaf, cat) in b8.items():
        per[cat][2] += anchor(leaf).lower() == cat.lower(); per[cat][3] += 1
    print("  per-category purity  (p2dca in-sample | p8a29 held-out | diff):")
    for cat in sorted(per, key=lambda c: -(per[c][0] / max(1, per[c][1]) - per[c][2] / max(1, per[c][3]))):
        a, b, c, d = per[cat]
        print("     %-18s %5.1f%% (n=%3d) | %5.1f%% (n=%3d) | %+5.1fpp" % (cat[:18], 100 * a / max(1, b), b, 100 * c / max(1, d), d, 100 * (a / max(1, b) - c / max(1, d))))


if __name__ == "__main__":
    main()
