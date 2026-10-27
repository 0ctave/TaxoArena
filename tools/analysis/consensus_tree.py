"""P1: consensus (stability-selection) construction over the 20 frozen-config seed
builds — procedure and registered test frozen in docs/v2_validation_plan.md.

Assignments per build: nearest-leaf-centroid (max cos of the question embedding's
first-256 MRL slice vs leaf vmfMu) on TRAIN-side questions — the disclosed
approximation of routing used throughout the campaign. Per majority-anchor group,
average-linkage agglomerative clustering on co-assignment distance
(1 - fraction of builds placing the pair in the same leaf), cut at co-assignment
>= 0.6; cells under 55 train questions merged into their nearest sibling cell.

REGISTERED PRIMARY (frozen before this run): disjoint 10-build halves (shuffle seed
777); PASS iff ARI(consensus_A, consensus_B) >= 0.90 on shared questions, reported
against the baseline mean pairwise ARI between individual builds; FALSIFIED iff
ARI < 0.80. Descriptives: consensus cell counts per anchor; E1 twin absorption.
"""
import os, sys, csv, json, math, random, struct, sqlite3
from collections import defaultdict, Counter
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

SEEDS_ARM1 = [("h9_seed%d" % s, s) for s in (137, 2048, 7, 31337)]
SEEDS_SWEEP = [("h9_sweep/s%d" % s, s) for s in
               (3, 11, 99, 271, 500, 777, 1234, 4242, 9001, 12345,
                54321, 65537, 111111, 314159, 999983, 424242)]
CUT = 0.6
MIN_CELL = 55
HALF_SEED = 777


def last_snapshot(path):
    last = None
    with open(os.path.join(path, "dag_snapshots.jsonl"), encoding="utf-8") as f:
        for line in f:
            last = line
    return json.loads(last)


def build_leaves(run_dir):
    snap = last_snapshot(run_dir)
    nodes = {n["id"]: n for n in snap["nodes"]}
    kid2parent = {c: n["id"] for n in snap["nodes"] for c in n.get("childIds", [])}

    def anchor(nid):
        n = nodes[nid]
        while n["depth"] > 1:
            n = nodes[kid2parent[n["id"]]]
        return n["label"]
    leaves = [(n["id"], np.array(n["vmfMu"], dtype=np.float64), anchor(n["id"]))
              for n in snap["nodes"] if n["isLeaf"]]
    return leaves


def train_questions():
    emb = sqlite3.connect("file:%s?mode=ro" % os.path.join(ROOT, "embeddings_cache.db"), uri=True)
    reserved = set()
    with open(os.path.join(ROOT, "reserved_leaf_assignments.csv"), newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            reserved.add(int(row["question_id"]))
    ev = sqlite3.connect("file:%s?mode=ro" % os.path.join(ROOT, "mmlu_pro_dataset_cache_v2.db"), uri=True)
    # reserved texts via eval db (id-space rule)
    import rejudge_grok as rj
    evdb = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    marks = ",".join("?" * len(reserved))
    rtexts = {r[0] for r in evdb.execute(
        "SELECT DISTINCT question_text FROM eval_results WHERE question_id IN (%s)" % marks,
        list(reserved))}
    out = {}
    for qtext, blob in emb.execute("SELECT query, vector FROM embeddings"):
        if qtext in rtexts or not isinstance(blob, bytes) or len(blob) % 4:
            continue
        v = np.array(struct.unpack(">%df" % (len(blob) // 4), blob), dtype=np.float64)[:256]
        n = np.linalg.norm(v)
        if n > 0:
            out[qtext] = v / n
    return out


def assign(builds, qvecs):
    """per build: qtext -> (leaf_id, anchor)"""
    out = []
    qtexts = list(qvecs)
    Q = np.stack([qvecs[t] for t in qtexts])
    for name, leaves in builds:
        M = np.stack([mu for _, mu, _ in leaves])
        idx = np.argmax(Q @ M.T, axis=1)
        out.append({t: (leaves[i][0], leaves[i][2]) for t, i in zip(qtexts, idx)})
    return out


def consensus(assignments, qvecs, tag):
    qtexts = list(qvecs)
    maj_anchor = {}
    for t in qtexts:
        maj_anchor[t] = Counter(a[t][1] for a in assignments).most_common(1)[0][0]
    cells = {}
    cell_id = 0
    for anchor in sorted(set(maj_anchor.values())):
        qs = [t for t in qtexts if maj_anchor[t] == anchor]
        if len(qs) < 2:
            for t in qs:
                cells[t] = cell_id
            cell_id += 1
            continue
        labels = np.array([[hash(a[t][0]) if a[t][1] == anchor else -1 for a in assignments]
                           for t in qs])
        valid = labels >= 0
        n = len(qs)
        # co-assignment: fraction of builds (where both in-anchor) with same leaf
        co = np.zeros((n, n))
        for b in range(labels.shape[1]):
            lb = labels[:, b]
            vb = valid[:, b]
            same = (lb[:, None] == lb[None, :]) & vb[:, None] & vb[None, :]
            co += same
        both = valid.astype(int) @ valid.astype(int).T
        with np.errstate(divide="ignore", invalid="ignore"):
            frac = np.where(both > 0, co / both, 0.0)
        d = 1.0 - frac
        np.fill_diagonal(d, 0.0)
        Z = linkage(squareform(d, checks=False), method="average")
        lab = fcluster(Z, t=1.0 - CUT, criterion="distance")
        # merge small cells into nearest sibling by centroid
        sizes = Counter(lab)
        cents = {c: np.mean([qvecs[qs[i]] for i in range(n) if lab[i] == c], axis=0)
                 for c in sizes}
        for c, sz in sorted(sizes.items(), key=lambda kv: kv[1]):
            if sz >= MIN_CELL or len(sizes) <= 1:
                continue
            others = [o for o in sizes if o != c and sizes[o] > 0]
            if not others:
                continue
            tgt = max(others, key=lambda o: float(np.dot(cents[c], cents[o])))
            lab[lab == c] = tgt
            sizes[tgt] += sz
            sizes[c] = 0
        remap = {}
        for i, t in enumerate(qs):
            if lab[i] not in remap:
                remap[lab[i]] = cell_id
                cell_id += 1
            cells[t] = remap[lab[i]]
    k = len(set(cells.values()))
    per_anchor = Counter()
    for t, c in cells.items():
        pass
    sizes = Counter(cells.values())
    print("%s: %d consensus cells | sizes p10 %d median %d p90 %d" %
          (tag, k, *np.percentile(sorted(sizes.values()), [10, 50, 90]).astype(int)))
    return cells


def ari(a, b):
    from scipy.special import comb
    common = sorted(set(a) & set(b))
    la = [a[t] for t in common]
    lb = [b[t] for t in common]
    ct = Counter(zip(la, lb))
    sum_comb = sum(comb(v, 2) for v in ct.values())
    sa = sum(comb(v, 2) for v in Counter(la).values())
    sb = sum(comb(v, 2) for v in Counter(lb).values())
    n = comb(len(common), 2)
    exp = sa * sb / n
    mx = (sa + sb) / 2
    return float((sum_comb - exp) / (mx - exp))


def main():
    print("loading builds...")
    builds = []
    for rel, seed in SEEDS_ARM1 + SEEDS_SWEEP:
        run = os.path.join(ROOT, "experiment_results", rel, "seed_%d" % seed)
        builds.append((rel, build_leaves(run)))
    print("%d builds loaded" % len(builds))
    qvecs = train_questions()
    print("%d train questions" % len(qvecs))
    assignments = assign(builds, qvecs)

    # baseline: mean pairwise ARI between individual builds (20 seeded pairs)
    rng = random.Random(42)
    pairs = [rng.sample(range(len(builds)), 2) for _ in range(20)]
    base = [ari({t: assignments[i][t][0] for t in qvecs},
                {t: assignments[j][t][0] for t in qvecs}) for i, j in pairs]
    print("baseline pairwise build ARI: mean %.3f (min %.3f max %.3f)"
          % (float(np.mean(base)), min(base), max(base)))

    # full consensus
    full = consensus(assignments, qvecs, "FULL (20 builds)")

    # registered halves test
    order = list(range(len(builds)))
    random.Random(HALF_SEED).shuffle(order)
    A = [assignments[i] for i in order[:10]]
    B = [assignments[i] for i in order[10:]]
    ca = consensus(A, qvecs, "HALF A")
    cb = consensus(B, qvecs, "HALF B")
    score = ari(ca, cb)
    print("\nREGISTERED PRIMARY: ARI(consensus_A, consensus_B) = %.4f -> %s"
          % (score, "PASS (>=0.90)" if score >= 0.90 else
             ("FALSIFIED (<0.80)" if score < 0.80 else "INDETERMINATE [0.80,0.90)")))
    json.dump({t: c for t, c in full.items()},
              open(os.path.join(ROOT, "experiment_results", "consensus_cells_v1.json"), "w"))
    print("full consensus written to experiment_results/consensus_cells_v1.json")


if __name__ == "__main__":
    main()
