"""D1 dimension/anisotropy sweep — readout per arm (registration: docs/v2_validation_plan.md "D1").

Per build (experiment_results/dimsweep/<arm>_s<seed>/seed_<seed>/):
  leaves, Philosophy leaves, held-out Top-1 (+Wilson CI) from MAIN_trickle_validation_results.csv,
  site-level certification count from experiment_results/dimsweep/site_null_<arm>_s<seed>.csv
  (the P2 harness run on the build's own snapshot at the build's own geometry).
Per arm: cross-seed ARI of nearest-leaf-centroid train assignments (the consensus_tree.py
metric; slice width read from the build's own vmfMu length), against the 20-build baseline
0.663 (0.585-0.704) measured in P1.

Usage: python tools/analysis/dimsweep_report.py [--arms d128,d256,d512,abt2,white] [--seeds 137,2048]
"""
import os, sys, csv, json, argparse, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import consensus_tree as ct  # noqa: E402

SWEEP = os.path.join(ROOT, "experiment_results", "dimsweep")  # overridden by --sweep


def build_dir(arm, seed):
    return os.path.join(SWEEP, "%s_s%d" % (arm, seed), "seed_%d" % seed)


def metric_csv(path):
    out = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                out[row["Metric"]] = float(row["Value"])
            except ValueError:
                out[row["Metric"]] = row["Value"]
    return out


def leaves_of(snap):
    nodes = {n["id"]: n for n in snap["nodes"]}
    kid2parent = {c: n["id"] for n in snap["nodes"] for c in n.get("childIds", [])}

    def anchor(nid):
        n = nodes[nid]
        while n["depth"] > 1:
            n = nodes[kid2parent[n["id"]]]
        return n["label"]
    return [(n, anchor(n["id"])) for n in snap["nodes"] if n["isLeaf"]]


def site_cert(arm, seed):
    p = os.path.join(SWEEP, "site_null_%s_s%d.csv" % (arm, seed))
    if not os.path.exists(p):
        return None
    rows = list(csv.DictReader(open(p, newline="", encoding="utf-8")))
    n_sites = len(rows)
    cert = sum(1 for r in rows if r["cert_site_p95"] == "true")
    defl = sum(1 for r in rows if r["cert_deflated_p95"] == "true")
    trunk = sum(1 for r in rows if r["trunk_member"] == "true")
    depth1 = [r["label"] for r in rows if r["depth"] == "1" and r["cert_site_p95"] == "true"]
    return dict(sites=n_sites, cert=cert, defl=defl, trunk=trunk, depth1=depth1)


def train_vecs_for_dim(dim, cache=[None, None]):
    """consensus_tree.train_questions slices to 256; re-slice the full vectors here."""
    if cache[0] is None:
        import struct, sqlite3
        emb = sqlite3.connect("file:%s?mode=ro" % os.path.join(ROOT, "embeddings_cache.db"), uri=True)
        base = ct.train_questions()  # 256-slice, but gives us the train text set
        full = {}
        for qtext, blob in emb.execute("SELECT query, vector FROM embeddings"):
            if qtext in base and isinstance(blob, bytes) and len(blob) % 4 == 0:
                full[qtext] = np.array(struct.unpack(">%df" % (len(blob) // 4), blob), dtype=np.float64)
        cache[0] = full
    full = cache[0]
    out = {}
    for t, v in full.items():
        s = v[:dim]
        n = np.linalg.norm(s)
        if n > 0:
            out[t] = s / n
    return out


def assign(leaves, qvecs):
    qtexts = list(qvecs)
    Q = np.stack([qvecs[t] for t in qtexts])
    M = np.stack([np.array(n["vmfMu"], dtype=np.float64) for n, _ in leaves])
    idx = np.argmax(Q @ M.T, axis=1)
    return {t: leaves[i][0]["id"] for t, i in zip(qtexts, idx)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="d128,d256,d512,abt2,white")
    ap.add_argument("--seeds", default="137,2048")
    ap.add_argument("--sweep", default="dimsweep", help="experiment_results/<sweep> (D2 uses dimsweep2)")
    a = ap.parse_args()
    global SWEEP
    SWEEP = os.path.join(ROOT, "experiment_results", a.sweep)
    arms = a.arms.split(",")
    seeds = [int(s) for s in a.seeds.split(",")]

    print("%-6s %5s | %6s %7s | %7s %17s | %s" % ("arm", "seed", "leaves", "philo", "top1", "wilson", "site-cert / defl / trunk (depth-1 certified)"))
    per_arm = {}
    for arm in arms:
        per_arm[arm] = {}
        for seed in seeds:
            d = build_dir(arm, seed)
            if not os.path.exists(os.path.join(d, "dag_snapshots.jsonl")):
                print("%-6s %5d | (missing)" % (arm, seed))
                continue
            snap = ct.last_snapshot(d)
            leaves = leaves_of(snap)
            philo = sum(1 for _, anc in leaves if anc == "Philosophy")
            tv = metric_csv(os.path.join(d, "validation", "MAIN_trickle_validation_results.csv"))
            sc = site_cert(arm, seed)
            sc_txt = ("%d/%d / %d / %d (%s)" % (sc["cert"], sc["sites"], sc["defl"], sc["trunk"], ", ".join(sorted(sc["depth1"])))
                      if sc else "site-null pending")
            print("%-6s %5d | %6d %7d | %7.4f [%.4f,%.4f] | %s" % (
                arm, seed, len(leaves), philo, tv["Top1Accuracy"], tv["Top1WilsonLow"], tv["Top1WilsonHigh"], sc_txt))
            per_arm[arm][seed] = dict(leaves=leaves, top1=tv["Top1Accuracy"], lo=tv["Top1WilsonLow"],
                                      hi=tv["Top1WilsonHigh"], philo=philo, cert=sc["cert"] if sc else None)

    print()
    print("cross-seed ARI (nearest-centroid train assignments; P1 baseline 0.663, range 0.585-0.704):")
    ari = {}
    for arm in arms:
        got = per_arm[arm]
        if len(got) < 2:
            print("  %-6s: needs both seeds" % arm)
            continue
        s1, s2 = seeds[:2]
        dim = len(got[s1]["leaves"][0][0]["vmfMu"])
        qv = train_vecs_for_dim(dim)
        a1 = assign(got[s1]["leaves"], qv)
        a2 = assign(got[s2]["leaves"], qv)
        ari[arm] = ct.ari(a1, a2)
        print("  %-6s (dim %d): ARI = %.4f" % (arm, dim, ari[arm]))

    # Registered readout vs the d256 baseline arm
    print()
    base = per_arm.get("d256", {})
    if len(base) == 2 and all(base[s]["cert"] is not None for s in seeds):
        print("REGISTERED D1 CRITERION per arm (vs d256, both seeds): cert > baseline in BOTH seeds AND Top-1 Wilson CI overlaps baseline's in both seeds AND ARI >= ARI(d256) - 0.02")
        for arm in arms:
            if arm == "d256" or len(per_arm[arm]) < 2:
                continue
            g = per_arm[arm]
            if any(g[s]["cert"] is None for s in seeds):
                print("  %-6s: site-null pending" % arm); continue
            cert_ok = all(g[s]["cert"] > base[s]["cert"] for s in seeds)
            top1_ok = all(not (g[s]["hi"] < base[s]["lo"] or g[s]["lo"] > base[s]["hi"]) for s in seeds)
            ari_ok = arm in ari and "d256" in ari and ari[arm] >= ari["d256"] - 0.02
            verdict = "IMPROVES" if (cert_ok and top1_ok and ari_ok) else "NO IMPROVEMENT"
            print("  %-6s: cert>%s top1~%s ari%s -> %s" % (arm, "Y" if cert_ok else "N", "Y" if top1_ok else "N", "Y" if ari_ok else "N", verdict))
    else:
        print("d256 baseline incomplete; registered criterion not evaluated yet.")


if __name__ == "__main__":
    main()
