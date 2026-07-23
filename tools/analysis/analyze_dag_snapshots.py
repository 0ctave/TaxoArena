#!/usr/bin/env python3
"""
Analyze per-iteration DAG snapshots written by TaxonomyEngine.dumpIterationSnapshot()
(dag_snapshots.jsonl, one JSON object per iteration, gated behind enableProfiling).

Usage:
  python analyze_dag_snapshots.py --file experiment_results/diag_domains/seed_42/dag_snapshots.jsonl
  python analyze_dag_snapshots.py --file <path> --iteration 12
  python analyze_dag_snapshots.py --file <path> --iteration last --chains-only
  python analyze_dag_snapshots.py --file <path> --list-iterations
"""
import argparse
import json
import sys
from statistics import mean, median


def load_snapshots(path):
    snapshots = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            snapshots[obj["iteration"]] = obj["nodes"]
    return snapshots


def index_by_id(nodes):
    return {n["id"]: n for n in nodes}


def find_chains(nodes):
    """A chain is a maximal run of consecutive single-tree-child nodes (depth > 1, to
    exclude protected domain anchors), each with zero direct+residual queries of their
    own -- i.e. a run of pure structural pass-through wrappers. Returns a list of chains,
    each a list of node dicts from root-of-chain to leaf-of-chain (exclusive of the
    non-wrapper node the chain terminates into)."""
    by_id = index_by_id(nodes)
    children_of = {n["id"]: n["childIds"] for n in nodes}

    def is_wrapper(n):
        return (
            len(children_of.get(n["id"], [])) == 1
            and n["depth"] > 1
            and n["directQueries"] == 0
            and n["residualQueries"] == 0
        )

    wrapper_ids = {n["id"] for n in nodes if is_wrapper(n)}
    chain_starts = set()
    for wid in wrapper_ids:
        node = by_id[wid]
        parents = node["parentIds"]
        # A chain start is a wrapper whose parent is NOT itself a wrapper (or has no parent).
        if not parents or parents[0] not in wrapper_ids:
            chain_starts.add(wid)

    chains = []
    for start_id in chain_starts:
        chain = []
        cur = start_id
        while cur in wrapper_ids:
            chain.append(by_id[cur])
            nxt = children_of.get(cur, [])
            if not nxt:
                break
            cur = nxt[0]
        # Include the terminal (non-wrapper) node the chain feeds into, for context.
        if chain:
            last_children = children_of.get(chain[-1]["id"], [])
            if last_children and last_children[0] in by_id:
                chain.append(by_id[last_children[0]])
        if len(chain) >= 3:  # at least 2 wrappers + terminal to be worth reporting
            chains.append(chain)
    chains.sort(key=lambda c: -len(c))
    return chains


def leaf_repartition(nodes):
    leaves = [n for n in nodes if n["isLeaf"]]
    sizes = sorted(n["subtreeQueries"] for n in leaves)
    if not sizes:
        return None
    total = sum(sizes)
    n = len(sizes)
    gini = 0.0
    if n > 1 and total > 0:
        cum = 0
        for i, s in enumerate(sizes):
            cum += (2 * (i + 1) - n - 1) * s
        gini = cum / (n * total)
    return {
        "leafCount": n,
        "totalMass": total,
        "min": sizes[0],
        "max": sizes[-1],
        "median": median(sizes),
        "mean": round(mean(sizes), 1),
        "gini": round(gini, 3),
        "smallest5": sizes[:5],
        "largest5": sizes[-5:],
    }


def print_report(nodes, iteration, chains_only=False):
    print(f"\n{'=' * 70}\nIteration {iteration}\n{'=' * 70}")
    total = len(nodes)
    leaves = sum(1 for n in nodes if n["isLeaf"])
    print(f"Nodes: {total} ({leaves} leaves, {total - leaves} internal)")

    chains = find_chains(nodes)
    if chains:
        print(f"\n--- Single-child chains detected: {len(chains)} ---")
        for chain in chains:
            wrapper_part = chain[:-1] if len(chain) > 1 else chain
            depths = [n["depth"] for n in wrapper_part]
            kappas = [n["kappa"] for n in wrapper_part]
            path = " -> ".join(n["label"] or n["id"][:8] for n in chain)
            print(f"  len={len(wrapper_part)} depth={min(depths)}-{max(depths)} "
                  f"kappa_range=[{min(kappas):.1f},{max(kappas):.1f}]")
            print(f"    {path}")
    else:
        print("\nNo single-child wrapper chains detected.")

    if chains_only:
        return

    rep = leaf_repartition(nodes)
    if rep:
        print(f"\n--- Leaf query repartition ---")
        print(f"  leaves={rep['leafCount']} totalMass={rep['totalMass']}")
        print(f"  min={rep['min']} median={rep['median']} mean={rep['mean']} max={rep['max']}")
        print(f"  gini={rep['gini']} (0=perfectly even, 1=fully concentrated)")
        print(f"  smallest 5: {rep['smallest5']}")
        print(f"  largest 5:  {rep['largest5']}")

    c3_violations = [
        n for n in nodes
        if not n["isLeaf"] and n["directQueries"] > 0 and n["residualQueries"] == 0
    ]
    if c3_violations:
        print(f"\n--- C3 violations: {len(c3_violations)} ---")
        for n in c3_violations[:10]:
            print(f"  {n['label']} (depth={n['depth']}, directQ={n['directQueries']})")


def main():
    ap = argparse.ArgumentParser(description="Analyze TaxoArena per-iteration DAG snapshots")
    ap.add_argument("--file", required=True, help="Path to dag_snapshots.jsonl")
    ap.add_argument("--iteration", default="last", help="Iteration number, or 'last' (default), or 'all'")
    ap.add_argument("--list-iterations", action="store_true", help="List available iterations and exit")
    ap.add_argument("--chains-only", action="store_true", help="Only print chain detection, skip repartition stats")
    args = ap.parse_args()

    try:
        snapshots = load_snapshots(args.file)
    except FileNotFoundError:
        print(f"File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    if not snapshots:
        print("No snapshots found in file.", file=sys.stderr)
        sys.exit(1)

    if args.list_iterations:
        print(f"Iterations available: {sorted(snapshots.keys())}")
        return

    if args.iteration == "all":
        for it in sorted(snapshots.keys()):
            print_report(snapshots[it], it, args.chains_only)
    elif args.iteration == "last":
        last_it = max(snapshots.keys())
        print_report(snapshots[last_it], last_it, args.chains_only)
    else:
        it = int(args.iteration)
        if it not in snapshots:
            print(f"Iteration {it} not found. Available: {sorted(snapshots.keys())}", file=sys.stderr)
            sys.exit(1)
        print_report(snapshots[it], it, args.chains_only)


if __name__ == "__main__":
    main()
