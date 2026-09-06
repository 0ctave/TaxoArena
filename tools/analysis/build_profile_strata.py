"""Build the frozen stratum map for the R2 profile-mode run.

WHY (2026-09-06). The profile run samples until SE(psi_{model,stratum}) <= target in
every cell of the model x stratum grid. The strata must be (a) finer than the 14
MMLU-Pro anchors where the embedding geometry supports it — that is the "granular
sub-domains identified from the embedding separation" claim — and (b) large enough
in reserved questions to fund the SE target. This script derives them
DETERMINISTICALLY (no RNG) from the frozen snapshot:

  Within each anchor, average-linkage agglomerative clustering on the leaves'
  vMF mean directions (cosine similarity, 256-d) proposes a 2-way split; the split
  is ACCEPTED only if both halves carry >= MIN_QUESTIONS reserved questions,
  otherwise the anchor stays a single stratum. Ties in the merge order are broken
  by node id, so the output is a pure function of the snapshot + reserved pool.

Output: experiment_configs/strata_profile_v1.json  (the artifact the R2
pre-registration freezes) + a printed report with the per-stratum budget estimate.
"""
import ast
import csv
import json
import math
import os
import sqlite3
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SNAP_DB = os.path.join(ROOT, "snapshots_frozen.db")
SNAP_ID = "20260727_042523_Headless_Run_Auto_ge"
OUT = os.path.join(ROOT, "experiment_configs", "strata_profile_v1.json")

MIN_QUESTIONS = 100     # both halves of an accepted split must carry at least this.
# 100 funds the SE target comfortably: a stratum's comparisons draw on its pool with
# cross-pair reuse (within-pair no-repeat only), so ~1,300 stratum comparisons over a
# 100-question pool means ~10 uses per question across the 66 pairs — the reuse
# pattern the 2026-08 scheduler rework was built for. 140 was tried first and left
# only Math split (most anchors hold 200-280 unioned questions, so two >=140 halves
# are arithmetically impossible); the floor, not the geometry, was binding.
SE_TARGET = 0.15        # logits, per model x stratum — the run's stopping target
INFO_PER_COMPARISON = 0.20  # planning value; realized value comes from the run
N_MODELS = 12


def load():
    con = sqlite3.connect("file:%s?mode=ro" % SNAP_DB, uri=True)
    g = json.loads(con.execute("SELECT graph FROM snapshots WHERE id=?", (SNAP_ID,)).fetchone()[0])
    nodes = {n["id"]: n for n in (g["nodes"].values() if isinstance(g["nodes"], dict) else g["nodes"])}
    kids = {}
    for nid, n in nodes.items():
        ch = n.get("childIds") or "[]"
        kids[nid] = ast.literal_eval(ch) if isinstance(ch, str) else ch
    qs = defaultdict(set)
    with open(os.path.join(ROOT, "reserved_leaf_assignments.csv"), newline="", encoding="utf-8") as f:
        rdr = csv.reader(f)
        next(rdr)
        for row in rdr:
            qs[row[2]].add(int(row[0]))
    anchors = {}
    for a in kids["n00000001"]:
        leaves = []
        stack = [a]
        while stack:
            x = stack.pop()
            if not kids.get(x):
                leaves.append(x)
            else:
                stack.extend(kids[x])
        anchors[nodes[a]["label"]] = sorted(leaves)
    return nodes, anchors, qs


def cos(u, v):
    num = sum(a * b for a, b in zip(u, v))
    du = math.sqrt(sum(a * a for a in u))
    dv = math.sqrt(sum(b * b for b in v))
    return num / (du * dv) if du and dv else 0.0


def split_anchor(leaves, nodes, qs):
    """Average-linkage agglomerative merge down to 2 clusters; deterministic."""
    if len(leaves) < 2:
        return None
    mu = {}
    for l in leaves:
        v = nodes[l].get("vmfMu")
        v = ast.literal_eval(v) if isinstance(v, str) else v
        if not v:
            return None
        mu[l] = v
    sim = {(a, b): cos(mu[a], mu[b]) for i, a in enumerate(leaves) for b in leaves[i + 1:]}
    clusters = [[l] for l in leaves]
    while len(clusters) > 2:
        best = None
        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                s = sum(sim[tuple(sorted((a, b)))] for a in clusters[i] for b in clusters[j])
                s /= len(clusters[i]) * len(clusters[j])
                key = (-s, clusters[i][0], clusters[j][0])   # deterministic tie-break
                if best is None or key < best[0]:
                    best = (key, i, j)
        _, i, j = best
        clusters[i] = sorted(clusters[i] + clusters[j])
        del clusters[j]
    a, b = sorted(clusters)
    qa = len(set().union(*(qs[l] for l in a)))
    qb = len(set().union(*(qs[l] for l in b)))
    if qa >= MIN_QUESTIONS and qb >= MIN_QUESTIONS:
        return a, b
    return None


def main():
    nodes, anchors, qs = load()
    strata = []
    for label in sorted(anchors):
        leaves = anchors[label]
        split = split_anchor(leaves, nodes, qs)
        if split:
            for k, part in enumerate(split, 1):
                strata.append({"id": "%s-%d" % (label.lower().replace(" ", "_"), k),
                               "anchor": label, "leafIds": part})
        else:
            strata.append({"id": label.lower().replace(" ", "_"),
                           "anchor": label, "leafIds": leaves})

    n_per_ms = (1.0 / SE_TARGET ** 2) / INFO_PER_COMPARISON
    total = 0
    print("%-22s %6s %10s %28s" % ("stratum", "leaves", "reserved q", "est. matches (12 models)"))
    for s in strata:
        nq = len(set().union(*(qs[l] for l in s["leafIds"])))
        s["reservedQuestions"] = nq
        est = int(N_MODELS * n_per_ms / 2)
        total += est
        print("%-22s %6d %10d %28d" % (s["id"], len(s["leafIds"]), nq, est))
    print("strata: %d | SE target %.2f | planning info/comparison %.2f" % (len(strata), SE_TARGET, INFO_PER_COMPARISON))
    print("estimated total: ~%d matches (~%d judge calls)" % (total, 2 * total))

    payload = {
        "version": "strata_profile_v1",
        "snapshotId": SNAP_ID,
        "method": "average-linkage agglomerative on leaf vmfMu cosine within anchor; "
                  "2-way split accepted iff both halves >= %d reserved questions; "
                  "deterministic (tie-breaks by node id)" % MIN_QUESTIONS,
        "seTarget": SE_TARGET,
        "strata": strata,
    }
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, indent=2)
    print("written:", OUT)


if __name__ == "__main__":
    main()
