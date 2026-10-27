"""SCHED — this framework's match-making vs Varco Arena's tournament (registered 2026-09-13; ZERO LLM calls).

  python tools/analysis/sched_compare.py [--seeds 20] [--noise 0.10,0.228,0.40]

Varco Arena (arXiv:2411.01281) ranks by a single-elimination tournament per prompt, (n-1) matches per prompt.
This framework schedules Bradley-Terry races stratified by taxonomy cell. Compared here at MATCHED BUDGET in the
synthetic arena: the ground truth is each model's key accuracy, and the judge is the LEAF-POWER noise model.
Arm (a) replays the REAL x12 MAIN schedule triple for triple, so it is the scheduler's own output.
Readouts: the global board (Spearman rho vs key accuracy, top-4 key-order violations) and the per-anchor mean
rho, which is what cell stratification is meant to buy and what a router consumes.
"""
import os, sys, random, sqlite3, argparse
from collections import defaultdict, Counter
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import rejudge_grok as rj
import judge_free_tests as jf
import stack_judge as sj


def load():
    con = sqlite3.connect("file:%s?mode=ro" % rj.X12_DB, uri=True)
    trip = con.execute("SELECT eval_question_id, model_a, model_b, node_id FROM match_history WHERE condition='MAIN' AND snapshot_id=?", (rj.SNAP_MAIN,)).fetchall()
    nodes = rj.load_nodes(); parent = {c: n["id"] for n in nodes.values() for c in n.get("childIds", [])}

    def anchor(nid):
        n = nodes[nid]
        while n["depth"] > 1: n = nodes[parent[n["id"]]]
        return n["label"]
    q_anchor = {}
    tmp = defaultdict(Counter)
    for q, a, b, nid in trip: tmp[int(q)][anchor(nid)] += 1
    for q, c in tmp.items(): q_anchor[q] = c.most_common(1)[0][0]
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    models = sorted({r[1] for r in trip} | {r[2] for r in trip})
    G = defaultdict(dict)
    for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results"):
        if m in models: G[q][m] = int(c)
    qs = sorted(q for q in q_anchor if all(m in G[q] for m in models))
    real = [(int(q), a, b) for q, a, b, _ in trip if int(q) in qs]
    return models, G, qs, q_anchor, real


def verdict(G, q, a, b, p, rng):
    ca, cb = G[q][a], G[q][b]
    if ca == cb:
        return float(rng.random() < 0.5) if rng.random() < 0.8 else 0.5
    right = a if ca else b
    win = right if rng.random() > p else (b if right == a else a)
    return 1.0 if win == a else 0.0


def single_elim(models, q, G, p, rng):
    alive = models[:]; rng.shuffle(alive); out = []
    while len(alive) > 1:
        nxt = []
        for i in range(0, len(alive) - 1, 2):
            a, b = alive[i], alive[i + 1]
            w = verdict(G, q, a, b, p, rng)
            out.append((q, a, b, w))
            nxt.append(a if (w > 0.5 or (w == 0.5 and rng.random() < 0.5)) else b)
        if len(alive) % 2: nxt.append(alive[-1])
        alive = nxt
    return out


def score(matches, models, G, qs_used, q_anchor):
    th = jf.board_from(((a, b, w, 1.0) for _, a, b, w in matches), models)
    acc = {m: sum(G[q][m] for q in qs_used) / len(qs_used) for m in models}
    rho = rj.spearman([th[m] for m in models], [acc[m] for m in models])
    gt4 = sorted(sj.TOP4, key=lambda m: -acc[m])
    th4 = jf.board_from(((a, b, w, 1.0) for _, a, b, w in matches if a in sj.TOP4 and b in sj.TOP4), sj.TOP4)
    _, pv, _ = jf.violations(th4, gt4)
    by = defaultdict(list)
    for q, a, b, w in matches: by[q_anchor[q]].append((q, a, b, w))
    rhos = []
    for anc, ms in by.items():
        aq = sorted({q for q, _, _, _ in ms})
        if len(ms) < 100 or len(aq) < 20: continue
        t = jf.board_from(((a, b, w, 1.0) for _, a, b, w in ms), models)
        ka = {m: sum(G[q][m] for q in aq) / len(aq) for m in models}
        rhos.append(rj.spearman([t[m] for m in models], [ka[m] for m in models]))
    return rho, pv, (float(np.mean(rhos)) if rhos else float("nan")), len(rhos)


def main(seeds, noises):
    models, G, qs, q_anchor, real = load()
    B = len(real)
    print("SCHED: %d models | %d questions | budget %d matches (the real x12 MAIN schedule) | %d anchors"
          % (len(models), len(qs), B, len({q_anchor[q] for q in qs})))
    print("arms at matched budget: THIS FRAMEWORK (real schedule) | SINGLE ELIM (Varco) | RANDOM PAIRS | ROUND ROBIN\n")
    pairs = [(models[i], models[j]) for i in range(len(models)) for j in range(i + 1, len(models))]
    per_q = len(models) - 1
    n_q_se = B // per_q
    n_q_rr = B // len(pairs)
    for p in noises:
        print("judge flip rate %.3f (accuracy %.3f on decidable pairs)" % (p, 1 - p))
        res = defaultdict(list)
        for s in range(seeds):
            rng = random.Random(1000 + s)
            ms = [(q, a, b, verdict(G, q, a, b, p, rng)) for q, a, b in real]
            res["THIS FRAMEWORK"].append(score(ms, models, G, sorted({q for q, _, _ in real}), q_anchor))
            sel = rng.sample(qs, n_q_se); ms = []
            for q in sel: ms += single_elim(models, q, G, p, rng)
            res["SINGLE ELIM"].append(score(ms, models, G, sel, q_anchor))
            ms = []
            for _ in range(B):
                q = qs[rng.randrange(len(qs))]; a, b = pairs[rng.randrange(len(pairs))]
                ms.append((q, a, b, verdict(G, q, a, b, p, rng)))
            res["RANDOM PAIRS"].append(score(ms, models, G, sorted({m[0] for m in ms}), q_anchor))
            sel = rng.sample(qs, n_q_rr); ms = []
            for q in sel:
                for a, b in pairs: ms.append((q, a, b, verdict(G, q, a, b, p, rng)))
            res["ROUND ROBIN"].append(score(ms, models, G, sel, q_anchor))
        print("  %-16s %14s %12s %18s %s" % ("arm", "global rho", "top-4 viol", "per-anchor rho", "questions / anchors"))
        for arm in ("THIS FRAMEWORK", "SINGLE ELIM", "RANDOM PAIRS", "ROUND ROBIN"):
            v = np.array([(r[0], r[1], r[2]) for r in res[arm]], dtype=float); na = res[arm][0][3]
            nq = {"THIS FRAMEWORK": len({q for q, _, _ in real}), "SINGLE ELIM": n_q_se, "RANDOM PAIRS": len(qs), "ROUND ROBIN": n_q_rr}[arm]
            print("  %-16s %7.4f±%.4f %7.2f±%.2f %10.4f±%.4f     %d / %d"
                  % (arm, v[:, 0].mean(), v[:, 0].std(ddof=1), v[:, 1].mean(), v[:, 1].std(ddof=1), np.nanmean(v[:, 2]), np.nanstd(v[:, 2], ddof=1), nq, na))
        print()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--seeds", type=int, default=20); ap.add_argument("--noise", default="0.10,0.228,0.40")
    a = ap.parse_args(); main(a.seeds, [float(x) for x in a.noise.split(",")])
