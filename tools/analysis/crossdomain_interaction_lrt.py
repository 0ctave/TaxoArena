"""POST-HOC pooled interaction test on the x8_crossdomain_deep verdicts.

Devised 2026-08-10, AFTER the registered per-pair test (crossdomain_pair_qdf.py) came
back null -- this is exploratory reanalysis, not the registered outcome, and it cannot
rescue the registration. What it shows is that the interaction the registration was
hunting is present in the same data when the evidence is pooled into one likelihood
instead of sliced into 21 separate per-pair tests.

THE MODELS. Additive: one BT strength vector fitted on all comparisons. Interaction:
theta_m + delta_{m,g} over cell groups g -- which is exactly an independent BT fit per
group, since within a group only the psi_{m,g} = theta_m + delta_{m,g} differences
enter the likelihood. Groups follow the registration: Math / Law+Psychology / other.

    LRT = 2 * (sum_g ll_g  -  ll_all)

calibrated by permuting group labels within each pair (the exchangeable unit under
"no model x group interaction"), NOT by the chi-square, because per-(pair, group)
counts are small and ties carry mass. Ties enter as half-wins. A Jeffreys 0.5
pseudo-count stabilises each MM fit; the likelihood is evaluated on raw counts and the
identical procedure runs on every permutation, so the calibration absorbs the
smoothing.

OUTCOME on the 2026-08-08 deep run (4,186 verdicts; groups n = 497 / 631 / 3,058):
LRT = 19.24 against a permutation null of median 2.51, p95 9.68 -- p_perm = 0.003.
The two registered models carry the two largest named-direction swings: arx_0314
+0.50 logits math over law+psych, Llama-2-7b-hf +0.59 logits law+psych over math
(ground truth predicted ~1.5 and ~1.2, so the arena recovers the direction at roughly
a third to a half of the screened magnitude).

    python tools/analysis/crossdomain_interaction_lrt.py [ratings.db]
"""
import sqlite3, json, ast, math, os, random, sys
from collections import defaultdict

random.seed(42)
NPERM = 1000
PRIOR = 0.5
SNAPSHOT = '20260727_042523_Headless_Run_Auto_ge'
GROUPS = ['math', 'lawpsy', 'other']

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
DB = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    ROOT, 'experiment_results', 'x8_crossdomain', 'ratings_x8.db')
SNAP_DB = os.path.join(ROOT, 'snapshots.db')
if not os.path.exists(SNAP_DB):  # clone without the full local store
    SNAP_DB = os.path.join(ROOT, 'snapshots_frozen.db')


def stratum_map():
    con = sqlite3.connect(f'file:{SNAP_DB}?mode=ro', uri=True)
    g = json.loads(con.execute(
        'SELECT graph FROM snapshots WHERE id=?', (SNAPSHOT,)).fetchone()[0])
    nodes = {n['id']: n for n in g['nodes']}

    def kids(nid):
        c = nodes[nid].get('childIds', [])
        return ast.literal_eval(c) if isinstance(c, str) else c
    anchor_of = {}

    def walk(nid, a):
        anchor_of[nid] = a
        for c in kids(nid):
            walk(c, a)
    for a in kids(g['rootId']):
        walk(a, nodes[a]['label'])
    named = {'Math': 'math', 'Law': 'lawpsy', 'Psychology': 'lawpsy'}
    return {cell: named.get(anc, 'other') for cell, anc in anchor_of.items()}


def main():
    strat = stratum_map()
    gi = {s: i for i, s in enumerate(GROUPS)}
    mh = sqlite3.connect(f'file:{DB}?mode=ro', uri=True)
    rows = mh.execute(
        'SELECT node_id, winner, loser, is_tie FROM match_history').fetchall()
    models = sorted({r[1] for r in rows} | {r[2] for r in rows})
    mi = {m: i for i, m in enumerate(models)}
    M, G = len(models), len(GROUPS)

    data = []
    for node, w, l, tie in rows:
        a, b = mi[w], mi[l]
        i, j = (a, b) if a < b else (b, a)
        x = 0.5 if tie else (1.0 if a == i else 0.0)
        data.append((i, j, gi[strat.get(node, 'other')], x))

    def aggregate(comps):
        agg = defaultdict(lambda: [0.0, 0])
        for i, j, _, x in comps:
            e = agg[(i, j)]
            e[0] += x
            e[1] += 1
        return agg

    def mm_fit(agg, iters=500):
        W = [0.0] * M
        Npair = defaultdict(float)
        for (i, j), (wi, n) in agg.items():
            W[i] += wi + PRIOR
            W[j] += (n - wi) + PRIOR
            Npair[(i, j)] += n + 2 * PRIOR
            Npair[(j, i)] += n + 2 * PRIOR
        p = [1.0] * M
        for _ in range(iters):
            new = []
            for m in range(M):
                den = sum(Npair[(m, o)] / (p[m] + p[o])
                          for o in range(M) if Npair[(m, o)])
                new.append(W[m] / den if den > 0 else p[m])
            s = sum(new) / M
            new = [v / s for v in new]
            if max(abs(a - b) for a, b in zip(new, p)) < 1e-10:
                p = new
                break
            p = new
        return [math.log(max(v, 1e-300)) for v in p]

    def ll_of(agg, theta):
        ll = 0.0
        for (i, j), (wi, n) in agg.items():
            p = 1.0 / (1.0 + math.exp(-(theta[i] - theta[j])))
            p = min(max(p, 1e-9), 1 - 1e-9)
            ll += wi * math.log(p) + (n - wi) * math.log(1 - p)
        return ll

    def lrt_of(comps):
        agg_all = aggregate(comps)
        ll_add = ll_of(agg_all, mm_fit(agg_all))
        ll_int, fits = 0.0, {}
        for k in range(G):
            agg = aggregate([c for c in comps if c[2] == k])
            th = mm_fit(agg)
            fits[k] = th
            ll_int += ll_of(agg, th)
        return 2 * (ll_int - ll_add), fits

    lrt, fits = lrt_of(data)
    print(f'comparisons {len(data)} | groups {GROUPS} | per-group n:',
          [sum(1 for c in data if c[2] == k) for k in range(G)])
    print(f'observed LRT = {lrt:.2f}  (nominal df {(M - 1) * (G - 1)})')

    cent = {k: [t - sum(fits[k]) / M for t in fits[k]] for k in fits}
    print(f"\n{'model':<30}" + ''.join(f'{s:>9}' for s in GROUPS) + f"{'  math-lawpsy':>14}")
    for m in sorted(range(M), key=lambda m: -(cent[0][m] - cent[1][m])):
        print(f'{models[m]:<30}' + ''.join(f'{cent[k][m]:>+9.3f}' for k in range(G))
              + f'{cent[0][m] - cent[1][m]:>+14.3f}')

    by_pair = defaultdict(list)
    for idx, c in enumerate(data):
        by_pair[(c[0], c[1])].append(idx)
    work = [list(c) for c in data]
    null, ge = [], 0
    for _ in range(NPERM):
        for idxs in by_pair.values():
            labs = [work[k][2] for k in idxs]
            random.shuffle(labs)
            for k, lab in zip(idxs, labs):
                work[k][2] = lab
        v, _ = lrt_of([tuple(c) for c in work])
        null.append(v)
        if v >= lrt - 1e-9:
            ge += 1
    null.sort()
    print(f'\npermutation null (x{NPERM}): median {null[len(null) // 2]:.2f}'
          f'  p95 {null[int(0.95 * len(null))]:.2f}')
    print(f'p_perm = {(ge + 1) / (NPERM + 1):.4f}')


if __name__ == '__main__':
    main()
