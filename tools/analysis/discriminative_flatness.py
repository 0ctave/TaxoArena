"""Discriminative flatness re-derived at the 11-model length-matched band.

Replicates docs/prereg_discriminative_power.md exactly: median pairwise Spearman
between cells' model-accuracy rankings, observed-primary, with IQR; plus the
global-order-removed control (centre each model's accuracy by its global mean
before correlating) and the disattenuated column.

Disattenuation is TWO-SIDED: rho_obs / sqrt(r_A * r_B). Both sides are per-cell
rankings, so with cells of size nA, nB it is rho / sqrt(rA*rB), rA = nA/(nA+c).
The prereg used c = 7.66; that constant is now known to be 3.04x too large.
"""
import sqlite3, csv, math, statistics
from collections import defaultdict

BAND11 = ['gemini-3.1-pro_5-shots', 'arx_0314', 'arx_3', 'claude-3-5-sonnet-20241022',
          'claude-3.5-sonnet', 'deepseek-chat-v2_5', 'claude-3-5-haiku-20241022',
          'Meta-Llama-3-70B', 'Meta-Llama-3-8B-Instruct', 'Qwen1.5-14B-Chat',
          'Meta-Llama-3-8B']
ORIG8 = ['Llama-2-13b-hf', 'Llama-2-70b-hf', 'Meta-Llama-3_1-70B-Instruct',
         'Qwen1.5-72B-Chat', 'claude-3-5-haiku-20241022', 'claude-3-5-sonnet-20241022',
         'deepseek-chat-v2_5', 'gpt-4o-2024-08-06']

D = sqlite3.connect('mmlu_pro_dataset_cache_v2.db')
rec = defaultdict(dict); cat = {}
for q, c, m, ic in D.execute(
        'select question_id,category,model_name,is_correct from eval_results where is_reserved=1'):
    rec[q][m] = ic; cat[q] = c

# leaf assignments from the production router
leaf = defaultdict(set)
with open('reserved_leaf_assignments.csv') as f:
    for r in csv.DictReader(f):
        leaf[r['leaf_id']].add(int(r['question_id']))


def spearman(a, b, keys):
    n = len(keys)
    def rk(d):
        vs = sorted(keys, key=lambda k: d[k]); r = {}; i = 0
        while i < len(vs):
            j = i
            while j + 1 < len(vs) and d[vs[j + 1]] == d[vs[i]]: j += 1
            for k in range(i, j + 1): r[vs[k]] = (i + j) / 2 + 1
            i = j + 1
        return r
    ra, rb = rk(a), rk(b)
    ma = sum(ra.values()) / n; mb = sum(rb.values()) / n
    nu = sum((ra[k] - ma) * (rb[k] - mb) for k in keys)
    da = math.sqrt(sum((ra[k] - ma) ** 2 for k in keys))
    db = math.sqrt(sum((rb[k] - mb) ** 2 for k in keys))
    return nu / (da * db) if da and db else None


def analyse(roster, c_const, label):
    R = set(roster)
    covered = {q for q, d in rec.items() if R <= d.keys()}
    print(f"\n{'='*76}\n{label}   ({len(roster)} models, {len(covered)} covered reserved questions, c={c_const})\n{'='*76}")

    # global accuracy, for the centring control
    G = {m: sum(rec[q][m] for q in covered) / len(covered) for m in roster}

    groupings = [('14 domains', defaultdict(set)), ('87 leaves', defaultdict(set))]
    for q in covered: groupings[0][1][cat[q]].add(q)
    for lid, qs in leaf.items():
        s = qs & covered
        if s: groupings[1][1][lid] = s

    print(f"{'tree':<14}{'cells':>7}{'pairs':>8}{'obs rho':>10}{'IQR':>20}"
          f"{'disatt':>9}{'centred':>10}")
    out = []
    for name, groups in groupings:
        # drop cells too small to rank the roster
        cells = {k: v for k, v in groups.items() if len(v) >= len(roster)}
        accs, cents, sizes = {}, {}, {}
        for k, qs in cells.items():
            a = {m: sum(rec[q][m] for q in qs) / len(qs) for m in roster}
            accs[k] = a
            cents[k] = {m: a[m] - G[m] for m in roster}
            sizes[k] = len(qs)
        ks = sorted(cells)
        rhos, dis, cen = [], [], []
        for i in range(len(ks)):
            for j in range(i + 1, len(ks)):
                A, B = ks[i], ks[j]
                r = spearman(accs[A], accs[B], roster)
                if r is None: continue
                rhos.append(r)
                rA = sizes[A] / (sizes[A] + c_const); rB = sizes[B] / (sizes[B] + c_const)
                dis.append(r / math.sqrt(rA * rB))
                rc = spearman(cents[A], cents[B], roster)
                if rc is not None: cen.append(rc)
        rhos.sort(); dis.sort(); cen.sort()
        q1 = rhos[len(rhos) // 4]; q3 = rhos[3 * len(rhos) // 4]
        med = statistics.median(rhos)
        print(f"{name:<14}{len(ks):>7}{len(rhos):>8}{med:>10.3f}"
              f"{f'[{q1:.3f}, {q3:.3f}]':>20}{statistics.median(dis):>9.3f}"
              f"{statistics.median(cen):>10.3f}")
        out.append((name, len(ks), med, q1, q3, statistics.median(dis), statistics.median(cen)))
    if len(out) >= 2:
        d = out[0][2] - out[1][2]
        print(f"\n  granularity delta (14 domains -> 87 leaves): {d:+.3f}")
        print(f"  IQRs overlap: {'YES' if out[0][3] <= out[1][4] and out[1][3] <= out[0][4] else 'NO'}")
    return out


analyse(ORIG8, 7.66, 'REPLICATION: original 8-model roster, published constant')
analyse(BAND11, 2.52, 'RE-DERIVED: 11-model length-matched band, corrected constant')
analyse(BAND11, 7.66, 'CONTROL: 11-model band with the OLD constant (isolates roster effect)')
