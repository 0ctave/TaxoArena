"""Registered test of the x8_crossdomain prediction: per-pair Cochran Q/df vs a shuffled null.

THE REGISTRATION (experiment_configs/x8_crossdomain_deep.toml, 2026-08-08): with all 87
cells on one Bradley-Terry scale, Q/df for pairs involving arx_0314 and Llama-2-7b-hf
rises well above its shuffled null, driven by mathematics cells against law and
psychology cells.

THE TEST. Per model pair, over cells with at least MIN_N of that pair's comparisons:
ties half-weighted into the win count, pbar pooled over the pair's cells,

    Q = sum_c (x_c - n_c*pbar)^2 / (n_c*pbar*(1-pbar)),   Q/df with df = #cells - 1.

The null is empirical, not chi-square: the pair's own outcomes are shuffled across its
cells NSHUF times, preserving cell sizes, so small counts and the tie mass calibrate
themselves. The directional contrasts pool match-level win rates against all opponents
inside the registered cell groups.

OUTCOME on the 2026-08-08 deep run (4,186 verdicts): registered prediction NOT
confirmed -- named pairs median Q/df 0.84 vs shuffled 0.76 (0.72 vs 0.73 at MIN_N=3),
no named pair below p_emp 0.05; all four registered directional contrasts have the
correct sign (arx math-vs-law/psych +8.8pp z=+1.79; Llama-2-7b law-vs-math +7.9pp
z=+1.52) but none reach significance. See crossdomain_interaction_lrt.py for the
post-hoc pooled test, which does recover the interaction.

    python tools/analysis/crossdomain_pair_qdf.py [ratings.db]
"""
import sqlite3, json, ast, os, random, sys
from collections import defaultdict

random.seed(42)
NSHUF = 1000
MIN_N = 2
NAMED = ('arx_0314', 'Llama-2-7b-hf')
SNAPSHOT = '20260727_042523_Headless_Run_Auto_ge'

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
DB = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    ROOT, 'experiment_results', 'x8_crossdomain', 'ratings_x8.db')
SNAP_DB = os.path.join(ROOT, 'snapshots.db')
if not os.path.exists(SNAP_DB):  # clone without the full local store
    SNAP_DB = os.path.join(ROOT, 'snapshots_frozen.db')


def anchor_map():
    """cell id -> domain anchor label, from the frozen snapshot's tree."""
    con = sqlite3.connect(f'file:{SNAP_DB}?mode=ro', uri=True)
    g = json.loads(con.execute(
        'SELECT graph FROM snapshots WHERE id=?', (SNAPSHOT,)).fetchone()[0])
    nodes = {n['id']: n for n in g['nodes']}

    def kids(nid):
        c = nodes[nid].get('childIds', [])
        return ast.literal_eval(c) if isinstance(c, str) else c
    out = {}

    def walk(nid, a):
        out[nid] = a
        for c in kids(nid):
            walk(c, a)
    for a in kids(g['rootId']):
        walk(a, nodes[a]['label'])
    return out


def qdf(cell_outcomes):
    cells = {c: v for c, v in cell_outcomes.items() if len(v) >= MIN_N}
    if len(cells) < 2:
        return None
    tot_x = sum(sum(v) for v in cells.values())
    tot_n = sum(len(v) for v in cells.values())
    pbar = tot_x / tot_n
    if pbar <= 0 or pbar >= 1:
        return (0.0, len(cells) - 1)
    Q = sum((sum(v) - len(v) * pbar) ** 2 / (len(v) * pbar * (1 - pbar))
            for v in cells.values())
    return (Q / (len(cells) - 1), len(cells) - 1)


def main():
    anchor_of = anchor_map()
    mh = sqlite3.connect(f'file:{DB}?mode=ro', uri=True)
    rows = mh.execute(
        'SELECT node_id, winner, loser, is_tie FROM match_history').fetchall()

    pair_cells = defaultdict(lambda: defaultdict(list))
    for node, w, l, tie in rows:
        a, b = sorted((w, l))
        x = 0.5 if tie else (1.0 if w == a else 0.0)
        pair_cells[(a, b)][node].append(x)

    results = []
    for pair, cells in sorted(pair_cells.items()):
        obs = qdf(cells)
        if obs is None:
            continue
        obs_qdf, df = obs
        kept = {c: v for c, v in cells.items() if len(v) >= MIN_N}
        flat = [x for v in kept.values() for x in v]
        sizes = [(c, len(v)) for c, v in kept.items()]
        null_vals, ge = [], 0
        for _ in range(NSHUF):
            random.shuffle(flat)
            i, sh = 0, {}
            for c, n in sizes:
                sh[c] = flat[i:i + n]
                i += n
            r = qdf(sh)
            if r:
                null_vals.append(r[0])
                if r[0] >= obs_qdf - 1e-12:
                    ge += 1
        null_vals.sort()
        null_med = null_vals[len(null_vals) // 2] if null_vals else float('nan')
        results.append((pair, obs_qdf, df, null_med, (ge + 1) / (NSHUF + 1)))

    print(f'per-pair Cochran Q/df across cells (n_c >= {MIN_N}), shuffled null x{NSHUF}')
    print(f"{'pair':<58}{'Q/df':>7}{'df':>5}{'nullmed':>9}{'p_emp':>8}")
    for pair, q, df, nm, p in sorted(results, key=lambda r: -r[1]):
        tag = ' *' if (pair[0] in NAMED or pair[1] in NAMED) else ''
        print(f"{pair[0][:26] + ' vs ' + pair[1][:26]:<58}{q:>7.2f}{df:>5}{nm:>9.2f}{p:>8.3f}{tag}")

    def summ(rs, label):
        if not rs:
            print(f'{label}: no usable pairs')
            return
        qs = sorted(r[1] for r in rs)
        nm = sorted(r[3] for r in rs)
        sig = sum(1 for r in rs if r[4] < 0.05)
        print(f'{label}: {len(rs)} pairs | median Q/df {qs[len(qs) // 2]:.2f} '
              f'vs null median {nm[len(nm) // 2]:.2f} | p_emp<0.05: {sig}')

    print()
    summ(results, 'ALL pairs')
    summ([r for r in results if r[0][0] in NAMED or r[0][1] in NAMED],
         'NAMED (arx_0314 / Llama-2-7b-hf) pairs')

    print('\nDirectional contrasts (pooled match-level win rate vs all opponents):')

    def group_rate(model, domains):
        x = n = 0.0
        for (a, b), cells in pair_cells.items():
            if model not in (a, b):
                continue
            for cell, v in cells.items():
                if anchor_of.get(cell) not in domains:
                    continue
                for o in v:
                    n += 1
                    x += o if model == a else 1.0 - o
        return x, n

    for model, hi, lo in [('arx_0314', ('Math',), ('Law', 'Psychology')),
                          ('Llama-2-7b-hf', ('Law',), ('Math',)),
                          ('gpt-4o-2024-08-06', ('Math',), ('Engineering',)),
                          ('Qwen1.5-72B-Chat', ('History',), ('Physics',))]:
        xh, nh = group_rate(model, hi)
        xl, nl = group_rate(model, lo)
        ph, pl = xh / nh, xl / nl
        pp = (xh + xl) / (nh + nl)
        se = (pp * (1 - pp) * (1 / nh + 1 / nl)) ** 0.5
        z = (ph - pl) / se if se > 0 else float('nan')
        print(f"  {model:<26} {'+'.join(hi):<12} {ph:.3f} (n={nh:.0f})  vs  "
              f"{'+'.join(lo):<16} {pl:.3f} (n={nl:.0f})   diff {ph - pl:+.3f}  z={z:+.2f}")


if __name__ == '__main__':
    main()
