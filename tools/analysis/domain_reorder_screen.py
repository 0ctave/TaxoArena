"""Domain reordering screen under two roster policies.

(A) per-domain roster: models with >=95% coverage on THAT domain. Maximises n per
    domain; rosters differ, so cross-domain rho comparison is NOT valid.
(B) fixed 12-model length-matched band. Comparable null across domains, and it is
    the roster the arena would actually run on.
"""
import sqlite3, math, random
from collections import defaultdict

D = sqlite3.connect('mmlu_pro_dataset_cache_v2.db')

BAND = ['gemini-3.1-pro_5-shots', 'arx_0314', 'arx_3', 'claude-3-5-sonnet-20241022',
        'claude.3.5.sonnet', 'deepseek-chat-v2_5', 'claude-3-5-haiku-20241022',
        'Meta-Llama-3-70B', 'Meta-Llama-3-8B-Instruct',
        'Qwen1.5-14B-Chat', 'Meta-Llama-3-8B']
BAND[4] = 'claude-3.5-sonnet'

# traced models only
TRACED = [m for (m,) in D.execute("""
    SELECT model_name FROM eval_results WHERE is_reserved=1 GROUP BY model_name
    HAVING COUNT(*)>1000 AND
      AVG(CASE WHEN LENGTH(TRIM(COALESCE(model_output,'')))>40 THEN 1.0 ELSE 0 END)>0.9""")]

rec = defaultdict(dict); cat = {}
for q, c, m, ic in D.execute(
        'select question_id,category,model_name,is_correct from eval_results where is_reserved=1'):
    rec[q][m] = ic; cat[q] = c

def sp(a, b):
    ks = sorted(set(a) & set(b)); n = len(ks)
    if n < 3: return 0.0
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
    return nu / (da * db) if da and db else 0.0

def run(label, roster_for_domain):
    print(f"\n{'='*74}\n{label}\n{'='*74}")
    print('%-18s%5s%6s%8s%9s%9s%8s' % ('domain', 'k', 'nQ', 'rho', 'null_p5', 'null_med', 'p_emp'))
    random.seed(42)
    out = []
    domains = sorted({c for c in cat.values()})
    for dom in domains:
        R = roster_for_domain(dom)
        if len(R) < 6:
            print('%-18s%5d  -- roster too small' % (dom, len(R))); continue
        Rs = set(R)
        # global pool = all questions this roster fully covers
        pool = [q for q, d in rec.items() if Rs <= d.keys()]
        sub = [q for q in pool if cat[q] == dom]
        if len(sub) < 25:
            print('%-18s%5d%6d  -- too few questions' % (dom, len(R), len(sub))); continue
        acc = lambda S: {m: sum(rec[q][m] for q in S) / len(S) for m in R}
        G = acc(pool); r = sp(acc(sub), G)
        null = sorted(sp(acc(random.sample(pool, len(sub))), G) for _ in range(1500))
        pe = sum(1 for x in null if x <= r) / len(null)
        out.append((dom, len(R), len(sub), r, pe))
        print('%-18s%5d%6d%8.3f%9.3f%9.3f%8.3f'
              % (dom, len(R), len(sub), r, null[75], null[750], pe))
    sig = [d for d, k, n, r, p in out if p < 0.05]
    print('\nsignificant at p<0.05:', sig)
    return out

# (A) per-domain roster: >=95% coverage on that domain
dom_counts = defaultdict(lambda: defaultdict(int))
dom_total = defaultdict(int)
for q, c in cat.items():
    dom_total[c] += 1
    for m in rec[q]: dom_counts[c][m] += 1

def per_domain(dom):
    return [m for m in TRACED if dom_counts[dom].get(m, 0) >= 0.95 * dom_total[dom]]

A = run('(A) PER-DOMAIN ROSTER  (traced models with >=95% coverage of that domain)', per_domain)
B = run('(B) FIXED 11-MODEL LENGTH-MATCHED BAND', lambda d: BAND)

print(f"\n{'='*74}\nSTABILITY OF THE DOMAIN RECOMMENDATION\n{'='*74}")
da = {d: (n, p) for d, k, n, r, p in A}
db_ = {d: (n, p) for d, k, n, r, p in B}
print('%-18s%22s%22s' % ('domain', '(A) per-domain', '(B) 12-band'))
for d in sorted(set(da) | set(db_)):
    f = lambda t: ('n=%-5d p=%.3f' % t) if t else 'skipped'
    print('%-18s%22s%22s' % (d, f(da.get(d)), f(db_.get(d))))
