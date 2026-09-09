"""M1 — online replay of R2's verdicts (docs/m_series_registration.md; registered before running).

  python tools/analysis/online_replay.py [--block 500] [--kappa 30]
"""
import os, sys, csv, math, random, sqlite3, argparse
from collections import defaultdict
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rejudge_grok as rj
import judge_free_tests as jf

R2_DB = os.path.join(ROOT, "experiment_results", "x12_profile", "ratings_x12p.db")
B = 2000


def load_stream():
    con = sqlite3.connect("file:%s?mode=ro" % R2_DB, uri=True)
    rows = con.execute("SELECT id, eval_question_id, model_a, model_b, winner, is_tie, node_id FROM match_history "
                       "WHERE condition='MAIN' ORDER BY id").fetchall()
    conf = {}
    with open(jf.R2, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if not r["Rationale"].startswith("Reconstructed"):
                conf[(int(r["QueryId"]), r["ModelA"], r["ModelB"])] = float(r["Confidence"])
    out = []
    for mid, q, a, b, w, t, nid in rows:
        out.append(dict(q=int(q), a=a, b=b, w=("TIE" if t else w), leaf=nid, conf=conf.get((int(q), a, b))))
    return out


def fit(rows, models):
    agg = defaultdict(lambda: [0.0, 0.0])
    for r in rows:
        a, b = r["a"], r["b"]
        wa = 0.5 if r["w"] == "TIE" else (1.0 if r["w"] == a else 0.0)
        if a > b:
            a, b, wa = b, a, 1.0 - wa
        rec = agg[(a, b)]
        rec[0] += wa; rec[1] += 1.0
    if not agg:
        return {m: 0.0 for m in models}
    return rj.mm_fit({k: tuple(v) for k, v in agg.items()}, models)


def sig(x):
    return 1.0 / (1.0 + math.exp(-max(-30, min(30, x))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--block", type=int, default=500)
    ap.add_argument("--kappa", type=float, default=30.0)
    ap.add_argument("--gate", type=float, default=None, help="train only on verdicts with confidence >= gate (descriptive)")
    a = ap.parse_args()
    stream = load_stream()
    models = sorted({m for r in stream for m in (r["a"], r["b"])})
    nodes = rj.load_nodes()
    parent = {c: n["id"] for n in nodes.values() for c in n.get("childIds", [])}

    def anchor_of(nid):
        n = nodes[nid]
        while n["depth"] > 1:
            n = nodes[parent[n["id"]]]
        return n["label"]
    for r in stream:
        r["anchor"] = anchor_of(r["leaf"])
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    G = {(q, m): bool(c) for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results")}
    N = len(stream)
    half = N // 2
    print("M1 replay: %d verdicts, %d models, block %d, kappa %.0f, gate %s | evaluation on matches %d..%d"
          % (N, len(models), a.block, a.kappa, a.gate, half, N))
    preds = {k: [] for k in ("global", "anchor", "cell", "hier")}
    picks = {k: [] for k in preds}
    oracle = []
    truth = []
    keyed = []
    # per-leaf key accuracy over ALL keyed questions in the leaf (oracle ceiling; uses the key, no router can)
    leaf_acc = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    for r in stream:
        for m in (r["a"], r["b"]):
            c = G.get((r["q"], m))
            if c is not None:
                leaf_acc[r["leaf"]][m][0] += int(c); leaf_acc[r["leaf"]][m][1] += 1
    t = 0
    th_g = th_anc = th_cell = None
    cnt_cell = defaultdict(lambda: defaultdict(int))
    while t < N:
        train = stream[:t]
        if a.gate is not None:
            train = [r for r in train if r["conf"] is not None and r["conf"] >= a.gate]
        th_g = fit(train, models)
        by_anc = defaultdict(list); by_leaf = defaultdict(list)
        for r in train:
            by_anc[r["anchor"]].append(r); by_leaf[r["leaf"]].append(r)
        th_anc = {k: fit(v, models) for k, v in by_anc.items()}
        th_cell = {k: fit(v, models) for k, v in by_leaf.items()}
        cnt_anc = {k: defaultdict(int) for k in by_anc}; cnt_cell = {k: defaultdict(int) for k in by_leaf}
        for r in train:
            for m in (r["a"], r["b"]):
                cnt_anc[r["anchor"]][m] += 1; cnt_cell[r["leaf"]][m] += 1
        block = stream[t:t + a.block]
        for r in block:
            if t + block.index(r) < half:
                continue
        for i, r in enumerate(block):
            if t + i < half or r["w"] == "TIE":
                continue
            y = 1.0 if r["w"] == r["a"] else 0.0

            def theta(kind, m):
                g = th_g[m]
                if kind == "global":
                    return g
                if kind == "anchor":
                    ta = th_anc.get(r["anchor"]); n = cnt_anc.get(r["anchor"], {}).get(m, 0)
                    return ta[m] if (ta and n >= 5) else g
                if kind == "cell":
                    tc = th_cell.get(r["leaf"]); n = cnt_cell.get(r["leaf"], {}).get(m, 0)
                    return tc[m] if (tc and n >= 5) else g
                tc = th_cell.get(r["leaf"]); n = cnt_cell.get(r["leaf"], {}).get(m, 0)
                if not tc:
                    return g
                return g + n / (n + a.kappa) * (tc[m] - g)
            truth.append(y)
            ca, cb = G.get((r["q"], r["a"])), G.get((r["q"], r["b"]))
            dec = None if (ca is None or cb is None or ca == cb) else (r["a"] if ca else r["b"])
            keyed.append(dec)
            for k in preds:
                p = sig(theta(k, r["a"]) - theta(k, r["b"]))
                preds[k].append(p)
                picks[k].append(r["a"] if p >= 0.5 else r["b"])
            la = leaf_acc[r["leaf"]]
            oa = la[r["a"]][0] / max(1, la[r["a"]][1]); ob = la[r["b"]][0] / max(1, la[r["b"]][1])
            oracle.append(r["a"] if oa >= ob else r["b"])
        t += a.block
    y = np.array(truth)
    n_eval = len(y)
    print("  evaluated decisive verdicts: %d | key-decidable among them: %d" % (n_eval, sum(1 for d in keyed if d)))
    ll = {}
    for k in preds:
        p = np.clip(np.array(preds[k]), 1e-6, 1 - 1e-6)
        ll[k] = -(y * np.log(p) + (1 - y) * np.log(1 - p))
        br = (p - y) ** 2
        acc = ((p >= 0.5) == (y == 1)).mean()
        print("  %-7s log-loss %.4f | Brier %.4f | win-prediction accuracy %.3f" % (k, ll[k].mean(), br.mean(), acc))
    rng = random.Random(42)
    def boot(d):
        n = len(d); bs = sorted(float(d[[rng.randrange(n) for _ in range(n)]].mean()) for _ in range(B))
        return bs[int(0.025 * B)], bs[int(0.975 * B) - 1]
    for k, tag in (("hier", "REGISTERED PRIMARY"), ("anchor", "secondary a"), ("cell", "secondary b")):
        d = ll["global"] - ll[k]
        lo, hi = boot(d)
        print("  %-7s vs global: log-loss improvement %+.4f  95%% [%+.4f, %+.4f] -> %s (%s)"
              % (k, d.mean(), lo, hi, "PASS" if lo > 0 else ("WORSE" if hi < 0 else "TIE"), tag))
    # router utility on key-decidable
    idx = [i for i, d in enumerate(keyed) if d]
    print("  -- router utility (key-decidable, n=%d): correct-pick rate --" % len(idx))
    rates = {}
    for k in list(picks) + ["oracle"]:
        pk = picks[k] if k != "oracle" else oracle
        rates[k] = sum(pk[i] == keyed[i] for i in idx) / len(idx)
        print("     %-7s %.3f" % (k, rates[k]))
    b = sum(1 for i in idx if picks["hier"][i] == keyed[i] and picks["global"][i] != keyed[i])
    c = sum(1 for i in idx if picks["global"][i] == keyed[i] and picks["hier"][i] != keyed[i])
    p = jf.rj.__dict__.get("mcnemar_p") or (lambda b_, c_: min(1.0, 2.0 * sum(math.comb(b_ + c_, i) * 0.5 ** (b_ + c_) for i in range(min(b_, c_) + 1))) if b_ + c_ else 1.0)
    print("     hier vs global discordant %d:%d, McNemar p=%.4f -> %s (secondary c)" % (b, c, p(b, c), "PASS" if (b > c and p(b, c) < 0.05) else "FAIL"))
    # gain by anchor (log-loss hier vs global)
    print("  -- log-loss improvement hier vs global by anchor --")
    ev_rows = [r for i, r in enumerate([r for r in stream[half:] if r["w"] != "TIE"])]
    by = defaultdict(list)
    for i, r in enumerate(ev_rows[:n_eval]):
        by[r["anchor"]].append(ll["global"][i] - ll["hier"][i])
    for anc, v in sorted(by.items(), key=lambda kv: -np.mean(kv[1])):
        print("     %-18s n=%5d  %+.4f" % (anc[:18], len(v), np.mean(v)))


if __name__ == "__main__":
    main()
