"""Re-fit the Spearman-Brown reliability constant c in r = n/(n+c).

The published c = 7.66 was fitted on split-half reliability of per-cell model
rankings at the 8-model roster. The roster enters twice: the ranking being
correlated is over the roster, and the split-half correlation is itself a rank
statistic at that n. So c should depend on roster size.

Predicted direction (stated before running): at more models a ranking is harder
to reproduce from half the data, so reliability at fixed n is LOWER, so c > 7.66.

Method per draw:
  - sample a cell of n questions from the reserved pool
  - split into two halves of n/2
  - accuracy ranking of the roster on each half
  - Spearman between halves = split-half reliability r_half
  - Spearman-Brown up-correct to full cell length: r_full = 2 r_half / (1 + r_half)
Then least-squares fit of r_full(n) = n / (n + c) over the n-sweep.
"""
import sqlite3, math, random
from collections import defaultdict

D = sqlite3.connect('mmlu_pro_dataset_cache_v2.db')

BAND11 = ['gemini-3.1-pro_5-shots', 'arx_0314', 'arx_3', 'claude-3-5-sonnet-20241022',
          'claude-3.5-sonnet', 'deepseek-chat-v2_5', 'claude-3-5-haiku-20241022',
          'Meta-Llama-3-70B', 'Meta-Llama-3-8B-Instruct', 'Qwen1.5-14B-Chat',
          'Meta-Llama-3-8B']
# the roster c=7.66 was fitted on
ORIG8 = ['Llama-2-13b-hf', 'Llama-2-70b-hf', 'Meta-Llama-3_1-70B-Instruct',
         'Qwen1.5-72B-Chat', 'claude-3-5-haiku-20241022', 'claude-3-5-sonnet-20241022',
         'deepseek-chat-v2_5', 'gpt-4o-2024-08-06']

rec = defaultdict(dict)
for q, m, ic in D.execute(
        'select question_id,model_name,is_correct from eval_results where is_reserved=1'):
    rec[q][m] = ic


def spearman(a, b):
    ks = sorted(set(a) & set(b)); n = len(ks)
    if n < 3: return None
    def rk(d):
        vs = sorted(ks, key=lambda k: d[k]); r = {}; i = 0
        while i < len(vs):
            j = i
            while j + 1 < len(vs) and d[vs[j + 1]] == d[vs[i]]: j += 1
            for k in range(i, j + 1): r[vs[k]] = (i + j) / 2 + 1
            i = j + 1
        return r
    ra, rb = rk(a), rk(b); ma = sum(ra.values()) / n; mb = sum(rb.values()) / n
    nu = sum((ra[k] - ma) * (rb[k] - mb) for k in ks)
    da = math.sqrt(sum((ra[k] - ma) ** 2 for k in ks))
    db = math.sqrt(sum((rb[k] - mb) ** 2 for k in ks))
    return nu / (da * db) if da and db else None


def sweep(roster, label, reps=400):
    R = set(roster)
    pool = [q for q, d in rec.items() if R <= d.keys()]
    print(f"\n{label}: {len(roster)} models, {len(pool)} fully-covered reserved questions")
    random.seed(42)
    pts = []
    print('  %6s%10s%10s%12s' % ('n', 'r_half', 'r_full', 'n/(n+7.66)'))
    for n in (16, 24, 32, 40, 52, 64, 90, 128, 180):
        if n > len(pool) // 2: continue
        vals = []
        for _ in range(reps):
            cell = random.sample(pool, n)
            h1, h2 = cell[: n // 2], cell[n // 2:]
            a1 = {m: sum(rec[q][m] for q in h1) / len(h1) for m in roster}
            a2 = {m: sum(rec[q][m] for q in h2) / len(h2) for m in roster}
            s = spearman(a1, a2)
            if s is not None: vals.append(s)
        rh = sum(vals) / len(vals)
        rf = 2 * rh / (1 + rh) if rh > -1 else float('nan')
        pts.append((n, rh))   # fit on r_half: matches the original 7.66 method
        print('  %6d%10.3f%10.3f%12.3f' % (n, rh, rf, n / (n + 7.66)))
    # least-squares fit of c
    best, bestc = None, None
    c = 0.5
    while c < 60:
        sse = sum((rf - n / (n + c)) ** 2 for n, rf in pts)
        if best is None or sse < best: best, bestc = sse, c
        c += 0.01
    print(f"  fitted c = {bestc:.2f}   (SSE {best:.5f})")
    r1 = 1 / (1 + bestc)
    print(f"  single-query reliability r1 = 1/(1+c) = {r1:.4f}   [at c=7.66: {1/8.66:.4f}]")
    return bestc


c8 = sweep(ORIG8, 'ORIGINAL 8-MODEL ROSTER')
c11 = sweep(BAND11, '11-MODEL LENGTH-MATCHED BAND')

print(f"\n{'='*66}")
print(f"c(8 models)  = {c8:.2f}     published value 7.66")
print(f"c(11 models) = {c11:.2f}")
print(f"ratio        = {c11/c8:.2f}x")
print(f"\nDisattenuation at a 40-question cell:")
for lbl, c in (('published 7.66', 7.66), (f'refit 11-band {c11:.2f}', c11)):
    r = 40 / (40 + c)
    print(f"  {lbl:<22} r={r:.3f}  sqrt(r)={math.sqrt(r):.3f}  "
          f"an observed rho of 0.60 disattenuates to {0.60/math.sqrt(r):.3f}")
