"""Every verdict-derived rho in the project, under both tie policies.

Half-weighting ties costs 0.029 in rho on the paired Math run (8 grid steps at n=12),
which is larger than most of the effects being measured. Any rho computed from
match_history inherits that choice, so it has to be reported under both.

Also recomputes the correctness-blind subset, since the key-dependence finding
(rho 0.95-0.98 -> 0.74-0.76) is the project's central judge result.
"""
import sqlite3, math, os, random
from collections import defaultdict

D = sqlite3.connect('mmlu_pro_dataset_cache_v2.db')

RUNS = [
    ('ratings.db',              'MAIN',          '8-model frozen (capture gap)'),
    ('ratings.db',              'GENERIC_JUDGE', '8-model frozen (capture gap)'),
    ('ratings_math12.db',       None,            '12-model, centrality sampling'),
    ('ratings_math_paired.db',  'MAIN',          '12-model paired, leaf rubrics'),
    ('ratings_math_paired.db',  'C5',            '12-model paired, MT-Bench'),
]


def spearman(a, b, M):
    n = len(M)
    def rk(d):
        vs = sorted(M, key=lambda k: d[k]); r = {}; i = 0
        while i < len(vs):
            j = i
            while j + 1 < len(vs) and d[vs[j + 1]] == d[vs[i]]: j += 1
            for k in range(i, j + 1): r[vs[k]] = (i + j) / 2 + 1
            i = j + 1
        return r
    ra, rb = rk(a), rk(b); ma = sum(ra.values()) / n; mb = sum(rb.values()) / n
    den = math.sqrt(sum((ra[k]-ma)**2 for k in M) * sum((rb[k]-mb)**2 for k in M))
    return sum((ra[k]-ma)*(rb[k]-mb) for k in M) / den if den else float('nan')


def bt(pairs, M):
    W = defaultdict(float); N = defaultdict(float)
    for w, l, wt in pairs: W[w] += wt; N[(w, l)] += wt; N[(l, w)] += wt
    if not any(W[m] for m in M): return None
    p = {m: 1.0 for m in M}
    for _ in range(3000):
        new = {}
        for m in M:
            den = sum(N[(m, o)]/(p[m]+p[o]) for o in M if o != m and N[(m, o)])
            new[m] = W[m]/den if den > 0 else p[m]
        g = sum(new.values())/len(new)
        if g <= 0: return None
        new = {k: v/g for k, v in new.items()}
        if max(abs(new[m]-p[m]) for m in M) < 1e-11: return new
        p = new
    return p


def load(db, cond):
    S = sqlite3.connect(db)
    q = "select eval_question_id,winner,loser,is_tie from match_history where node_id is not null"
    if cond: q += f" and condition='{cond}'"
    return list(S.execute(q))


print(f"{'run':<34}{'arm':<15}{'half-wt':>9}{'drop':>9}{'delta':>9}{'ties':>7}{'n':>7}")
print('-' * 90)
store = {}
for db, cond, label in RUNS:
    if not os.path.exists(db): continue
    rows = load(db, cond)
    if not rows: continue
    M = sorted({r[1] for r in rows} | {r[2] for r in rows})
    qs = {str(r[0]) for r in rows}
    acc = {}
    for m in M:
        v = [ic for qq, ic in D.execute('select question_id,is_correct from eval_results where model_name=?', (m,))
             if str(qq) in qs]
        if v: acc[m] = sum(v)/len(v)
    M = [m for m in M if m in acc]
    out = {}
    for mode in ('half', 'drop'):
        p = []
        for qq, w, l, t in rows:
            if t:
                if mode == 'half': p += [(w, l, .5), (l, w, .5)]
            else: p.append((w, l, 1.))
        s = bt(p, M)
        out[mode] = spearman(s, acc, M) if s else float('nan')
    ties = sum(1 for r in rows if r[3]) / len(rows)
    store[(db, cond)] = (rows, M, acc)
    print(f"{label:<34}{(cond or 'MAIN'):<15}{out['half']:>9.4f}{out['drop']:>9.4f}"
          f"{out['drop']-out['half']:>+9.4f}{ties*100:>6.1f}%{len(rows):>7}")

# ── the key-dependence finding, under both policies ────────────────────────────
print()
print('CORRECTNESS-BLIND SUBSET (pairs where the key does not discriminate)')
print(f"{'run':<34}{'arm':<15}{'half-wt':>9}{'drop':>9}{'delta':>9}{'n_blind':>9}")
print('-' * 90)
for (db, cond), (rows, M, acc) in store.items():
    qs = {str(r[0]) for r in rows}
    cor = {}
    for qq, m, ic in D.execute('select question_id,model_name,is_correct from eval_results'):
        if str(qq) in qs: cor[(str(qq), m)] = ic
    blind = [r for r in rows
             if cor.get((str(r[0]), r[1])) is not None
             and cor.get((str(r[0]), r[1])) == cor.get((str(r[0]), r[2]))]
    if len(blind) < 50: continue
    out = {}
    for mode in ('half', 'drop'):
        p = []
        for qq, w, l, t in blind:
            if t:
                if mode == 'half': p += [(w, l, .5), (l, w, .5)]
            else: p.append((w, l, 1.))
        s = bt(p, M)
        out[mode] = spearman(s, acc, M) if s else float('nan')
    lbl = [r[2] for r in RUNS if r[0] == db][0]
    print(f"{lbl:<34}{(cond or 'MAIN'):<15}{out['half']:>9.4f}{out['drop']:>9.4f}"
          f"{out['drop']-out['half']:>+9.4f}{len(blind):>9}")
