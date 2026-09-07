"""H9 stability metrics: compare counterfactual construction runs to the frozen artifact.

Usage: python tools/analysis/h9_stability.py <run_dir> [<run_dir> ...]
Each run_dir is a per-seed export directory (e.g. experiment_results/h9_seed137/seed_137).
The frozen baseline is experiment_results/freeze_mcs55/seed_42.

Metrics (H9 registration, 801acbf): structure (nodes/leaves/depth/iterations,
certificate), held-out routing Top-1 (claim alpha: spread < 2.5pp), per-anchor
mass-share drift vs frozen (claim beta part 1: < 5pp everywhere), and greedy
mu-matching of frozen leaves to counterparts at cos >= 0.95 (claim beta part 2,
substitute for per-question ARI, which the exports do not carry: leaf identity is
"unstable" when a substantial fraction of frozen leaves lack a close counterpart).
"""
import json, csv, os, sys

FROZEN = os.path.join("experiment_results", "freeze_mcs55", "seed_42")

def last_snapshot(path):
    last = None
    with open(os.path.join(path, "dag_snapshots.jsonl"), encoding="utf-8") as f:
        for line in f:
            last = line
    return json.loads(last)

def top1(path):
    with open(os.path.join(path, "validation", "MAIN_centroid_routing_results.csv")) as f:
        for row in csv.reader(f):
            if row and row[0] == "Top1Accuracy":
                return float(row[1])

def load(path):
    snap = last_snapshot(path)
    nodes = snap["nodes"]
    anchors = [n for n in nodes if n["depth"] == 1]
    tot = sum(a["subtreeQueries"] for a in anchors)
    return dict(
        it=snap["iteration"], nodes=len(nodes),
        leaves=[n for n in nodes if n["isLeaf"]],
        depth=max(n["depth"] for n in nodes), top1=top1(path),
        ashare={a["label"]: a["subtreeQueries"] / tot for a in anchors})

def cos(u, v):
    return sum(a * b for a, b in zip(u, v))

def main(run_dirs):
    fro = load(FROZEN)
    print("frozen : it %2d nodes %3d leaves %2d depth %d top1 %.3f"
          % (fro["it"], fro["nodes"], len(fro["leaves"]), fro["depth"], fro["top1"]))
    t1s = [fro["top1"]]
    for rd in run_dirs:
        d = load(rd)
        t1s.append(d["top1"])
        drift = max(abs(d["ashare"].get(a, 0) - s) for a, s in fro["ashare"].items())
        used, matched = set(), 0
        for f in fro["leaves"]:
            best, bi = -1, None
            for i, c in enumerate(d["leaves"]):
                if i in used:
                    continue
                s = cos(f["vmfMu"], c["vmfMu"])
                if s > best:
                    best, bi = s, i
            if best >= 0.95:
                matched += 1
                used.add(bi)
        print("%s: it %2d nodes %3d leaves %2d depth %d top1 %.3f | anchor drift %.2fpp | mu-match %d/%d"
              % (os.path.basename(os.path.dirname(rd)) or rd, d["it"], d["nodes"], len(d["leaves"]),
                 d["depth"], d["top1"], 100 * drift, matched, len(fro["leaves"])))
    print("alpha: Top-1 spread %.1fpp (registered bar 2.5pp): %s"
          % (100 * (max(t1s) - min(t1s)), "PASS" if max(t1s) - min(t1s) < 0.025 else "FAIL"))

if __name__ == "__main__":
    main(sys.argv[1:])
