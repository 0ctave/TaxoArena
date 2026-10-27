"""Four probes opened by the relaxed design constraints (registered 2026-09-14, ZERO calls).

  python tools/analysis/newcontext_probes.py

TIER-RECOVERY  how cheap is a tier partition, against the total order the campaign spent itself on
ANCHOR-VALUE   does the anchor layer earn its place in routing, or is it a reporting convenience
REF-BY-CELL    does reference accuracy vary enough by cell to make per-cell reference selection worth building
TIER-ROUTER    accuracy lost and cost saved by routing to a tier and taking its cheapest member
"""
import os, sys, math, random, sqlite3
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import numpy as np
import rejudge_grok as rj
import rubric_p8 as p8
import rubric_512 as r512
import stack_judge as sj
import judge_free_tests as jf
import pool_guard

OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "newcontext_probes.txt")
TIER_GAP = 0.017   # 2 SE of a key accuracy at n=3,445; also exactly the arx/iask gap


def tiers_from(acc, models, gap=TIER_GAP):
    """Maximal runs of models whose consecutive key-accuracy gaps are below `gap`."""
    order = sorted(models, key=lambda m: -acc[m])
    out = []; cur = [order[0]]
    for prev, m in zip(order, order[1:]):
        if acc[prev] - acc[m] < gap: cur.append(m)
        else: out.append(cur); cur = [m]
    out.append(cur)
    return out


def partition_key(tiers):
    return tuple(tuple(sorted(t)) for t in tiers)


def ari(a, b, models):
    ia = {m: i for i, t in enumerate(a) for m in t}; ib = {m: i for i, t in enumerate(b) for m in t}
    n = len(models); same_a = same_b = both = 0
    for i in range(n):
        for j in range(i + 1, n):
            x, y = models[i], models[j]
            sa, sb = ia[x] == ia[y], ib[x] == ib[y]
            same_a += sa; same_b += sb; both += sa and sb
    tot = n * (n - 1) / 2
    exp = same_a * same_b / tot if tot else 0
    mx = (same_a + same_b) / 2
    return (both - exp) / (mx - exp) if mx != exp else 1.0


def main():
    L = []
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    pool = {q for (q,) in ev.execute("SELECT question_id FROM reserved_pool WHERE pool_id='p2dca21ab5f4ef3ae'")}
    K = defaultdict(dict); LEN = defaultdict(dict); CAT = {}
    for q, m, c, ln, cat in ev.execute("SELECT question_id, model_name, is_correct, LENGTH(model_output), category FROM eval_results"):
        if q in pool:
            K[q][m] = int(c or 0); LEN[q][m] = ln or 0; CAT[q] = (cat or "").strip()
    models = sorted(p8.ARENA12)
    acc, _ = jf.gt_and_lengths(set(p8.ARENA12))

    # ---------------- TIER-RECOVERY ----------------
    L.append("=== TIER-RECOVERY: how cheap is a TIER partition, against the total order? ===")
    key_tiers = tiers_from(acc, models)
    L.append("  key tiers at a %.3f gap (2 SE at n=3,445; also the arx/iask gap):" % TIER_GAP)
    for i, t in enumerate(key_tiers, 1):
        L.append("    tier %d: %s" % (i, ", ".join("%s %.3f" % (m[:26], acc[m]) for m in sorted(t, key=lambda m: -acc[m]))))
    sj.PROMPT = "v2"; sj.ALL_X12 = True
    rows = [r for r in sj.open_cache().execute("SELECT model_a, model_b, winner, invalid FROM verdicts") if not r[3]]
    rng = random.Random(42)
    L.append("")
    L.append("  A 0.017 gap puts almost every model in its own tier, which is the total order again - so the")
    L.append("  real question is how COARSE a tier has to be before the arena can recover it, and at what budget.")
    L.append("")
    L.append("  Tiering the judged board by a key-scale gap would be wrong: BT theta is a logit scale and a linear")
    L.append("  rescale distorts the gaps. Instead, for each k the key implies, cut the judged board at its own")
    L.append("  k-1 largest gaps - scale-free - and compare partitions.")
    L.append("")
    L.append("  %6s %5s %26s %26s" % ("gap", "k", "exact partition match", "mean adjusted Rand"))
    L.append("  %6s %5s %8s %8s %8s %8s %8s %8s" % ("", "", "250", "1000", "all", "250", "1000", "all"))
    for gap in (0.017, 0.05, 0.08, 0.12):
        kt = tiers_from(acc, models, gap=gap)
        k = len(kt); target = partition_key(kt)
        ex = {}; ar = {}
        for budget in (250, 1000, len(rows)):
            hits = 0; aa = []
            for _ in range(200):
                sub = [rows[rng.randrange(len(rows))] for _ in range(min(budget, len(rows)))]
                th = jf.board_from([(a, b, 0.5 if w == "TIE" else (1.0 if w == a else 0.0), 1.0) for a, b, w, _ in sub], models)
                o = sorted(models, key=lambda m: -th[m])
                gaps = sorted(range(len(o) - 1), key=lambda i: -(th[o[i]] - th[o[i + 1]]))[:k - 1]
                cuts = set(gaps); jt = []; cur = [o[0]]
                for i in range(len(o) - 1):
                    if i in cuts: jt.append(cur); cur = [o[i + 1]]
                    else: cur.append(o[i + 1])
                jt.append(cur)
                hits += partition_key(jt) == target
                aa.append(ari(jt, kt, models))
            ex[budget] = 100 * hits / 200; ar[budget] = sum(aa) / len(aa)
        b = [250, 1000, len(rows)]
        L.append("  %6.3f %5d %7.0f%% %7.0f%% %7.0f%% %8.3f %8.3f %8.3f"
                 % (gap, k, ex[b[0]], ex[b[1]], ex[b[2]], ar[b[0]], ar[b[1]], ar[b[2]]))
    L.append("  READ: against rho >= 0.93 in 100%% of draws at 2,000 matches and top-4 violations that never")
    L.append("  reach <= 1 at any budget. A tier partition the arena recovers reliably is a product it can ship;")
    L.append("  one it cannot is the ordering problem in a different costume.")

    # ---------------- ANCHOR-VALUE ----------------
    L.append("")
    L.append("=== ANCHOR-VALUE: does the anchor layer earn its place in ROUTING? ===")
    try:
        import free_tests_f4_f7 as ff
        run = os.path.join("experiment_results", "promoted", "bareq512_s42", "seed_42")
        leaves = ff.tree_leaves(run)
        dim = len(leaves[0][1])
        qtext = {}
        for q, t in ev.execute("SELECT question_id, question_text FROM eval_results WHERE model_name='gpt-4o-2024-08-06'"):
            if q in pool: qtext[q] = t
        vec = ff.embed_matrix(ff.EMB_DB, [qtext[q] for q in sorted(qtext)], dim)
        qs = [q for q in sorted(qtext) if qtext[q] in vec]
        X = np.stack([vec[qtext[q]] for q in qs])
        M = np.stack([mu / (np.linalg.norm(mu) or 1.0) for _, mu, _ in leaves])
        flat = np.argmax(X @ M.T, axis=1)
        flat_leaf = {q: leaves[i][0] for q, i in zip(qs, flat)}
        flat_anchor = {q: leaves[i][2] for q, i in zip(qs, flat)}
        deployed = r512.primary_routing("bareq512_s42")
        both = [q for q in qs if q in deployed]
        agree = sum(1 for q in both if flat_leaf[q] == deployed[q]) / max(1, len(both))
        L.append("  %d pool questions embedded and routed | flat-vs-deployed leaf agreement %.3f" % (len(both), agree))
        norm = lambda x: (x or "").strip().lower()
        pure_f = sum(1 for q in both if norm(flat_anchor[q]) == norm(CAT.get(q))) / max(1, len(both))
        nodes = r512.load_graph(r512.snapshot_id("bareq512_s42")); anchor_of = r512.anchor_fn(nodes)
        pure_d = sum(1 for q in both if norm(anchor_of(deployed[q])) == norm(CAT.get(q))) / max(1, len(both))
        L.append("  category purity of the routed anchor: FLAT nearest-leaf %.3f | DEPLOYED descent %.3f (%+.3f)"
                 % (pure_f, pure_d, pure_f - pure_d))
        L.append("  READ: the union build gave flatLeaf 81.6%% against descent 72.1%%. If flat matches or beats")
        L.append("  descent here too - on the dataset whose own categories ARE the anchors - the anchor layer is a")
        L.append("  reporting convenience, and dropping it costs nothing.")
    except Exception as e:
        L.append("  UNAVAILABLE: %s" % str(e)[:160])
        L.append("  (needs the promoted tree's centroids and the embedding cache; reported as not run rather than guessed)")

    # ---------------- REF-BY-CELL ----------------
    L.append("")
    L.append("=== REF-BY-CELL: does reference accuracy vary enough by cell to select on? ===")
    import rejudge_reference as rref
    refacc = {}
    for name in ("grok-reasoning", "mistral"):
        rref.set_reference(name)
        refacc[name] = {q: bool(r[2]) for q, r in rref.references().items()}
    route = r512.primary_routing("bareq512_s42")
    nodes = r512.load_graph(r512.snapshot_id("bareq512_s42")); anchor_of = r512.anchor_fn(nodes)
    by = defaultdict(lambda: defaultdict(list))
    for q in pool:
        a = anchor_of(route[q]) if q in route else None
        if a is None: continue
        for name in refacc:
            if q in refacc[name]: by[a][name].append(refacc[name][q])
    L.append("  %-16s %6s %14s %12s %10s" % ("anchor", "n", "grok-reasoning", "mistral", "better"))
    tot_g = tot_o = 0; flips = 0
    for a in sorted(by, key=lambda a: -len(by[a]["grok-reasoning"])):
        g = by[a]["grok-reasoning"]; m = by[a]["mistral"]
        if not g or not m: continue
        ag, am = sum(g) / len(g), sum(m) / len(m)
        better = "grok" if ag >= am else "MISTRAL"
        flips += ag < am
        tot_g += ag * len(g); tot_o += max(ag, am) * len(g)
        L.append("  %-16s %6d %14.3f %12.3f %10s" % (a[:16], len(g), ag, am, better))
    accs = [sum(by[a]["grok-reasoning"]) / len(by[a]["grok-reasoning"]) for a in by if by[a]["grok-reasoning"]]
    n_all = sum(len(by[a]["grok-reasoning"]) for a in by)
    L.append("  grok-reasoning spread across anchors: %.3f (%.3f..%.3f)" % (max(accs) - min(accs), min(accs), max(accs)))
    L.append("  cells where the WEAKER reference is better: %d" % flips)
    L.append("  oracle per-cell reference selection: %.4f vs always-grok %.4f (%+.4f)"
             % (tot_o / n_all, tot_g / n_all, (tot_o - tot_g) / n_all))

    # ---------------- TIER-ROUTER ----------------
    L.append("")
    L.append("=== TIER-ROUTER: route to a TIER, then take its cheapest member ===")
    per = defaultdict(lambda: defaultdict(list)); cost = defaultdict(lambda: defaultdict(list))
    for q in pool:
        a = anchor_of(route[q]) if q in route else None
        if a is None: continue
        for m in models:
            if m in K[q]: per[a][m].append(K[q][m]); cost[a][m].append(LEN[q].get(m, 0))
    best_single = max(models, key=lambda m: acc[m])
    tot = {"best single": [0, 0], "per-anchor best": [0, 0], "per-anchor best TIER, cheapest": [0, 0]}
    for a in per:
        n = len(per[a][best_single])
        if not n: continue
        la = {m: sum(per[a][m]) / len(per[a][m]) for m in models if per[a][m]}
        lc = {m: sum(cost[a][m]) / max(1, len(cost[a][m])) for m in models if cost[a][m]}
        ba = max(la, key=lambda m: la[m])
        at = tiers_from(la, sorted(la), gap=TIER_GAP)[0]
        cheap = min(at, key=lambda m: lc[m])
        for k, m in (("best single", best_single), ("per-anchor best", ba), ("per-anchor best TIER, cheapest", cheap)):
            tot[k][0] += la.get(m, 0) * n; tot[k][1] += lc.get(m, 0) * n
    n_all = sum(len(per[a][best_single]) for a in per if per[a][best_single])
    L.append("  %-32s %10s %14s" % ("policy", "accuracy", "mean chars"))
    for k, (s, c) in tot.items():
        L.append("  %-32s %10.4f %14.0f" % (k, s / n_all, c / n_all))
    d = (tot["per-anchor best TIER, cheapest"][0] - tot["per-anchor best"][0]) / n_all
    cs = 1 - tot["per-anchor best TIER, cheapest"][1] / max(1e-9, tot["per-anchor best"][1])
    L.append("  tier-then-cheapest against per-anchor best: %+.4f accuracy, %.0f%% of the generated length" % (d, 100 * (1 - cs)))
    L.append("  READ: if the accuracy loss is within a point while the cost falls materially, tier-routing is the")
    L.append("  right product shape - and the frontier ordering the campaign could never resolve never has to be asked.")

    txt = "\n".join(L)
    print(txt)
    open(OUT, "w", encoding="utf-8").write(txt + "\n")


if __name__ == "__main__":
    pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)
    main()
