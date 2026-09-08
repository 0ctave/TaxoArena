"""Permutation null for within-domain between-leaf ranking divergence.

THE QUESTION. Do a domain's induced leaves rank models differently FROM EACH OTHER
by more than sampling noise? This is the quantity that matters for whether a
partition has anything to find inside a domain -- distinct from the domain-vs-global
screen, which averages over leaves and therefore cannot see opposed sub-clusters that
cancel.

THE NULL. For each domain, shuffle that domain's reserved questions at random into
pseudo-leaves of EXACTLY the observed leaf sizes, then compute the same between-leaf
Spearman statistic. Repeat. Real leaves that carry sub-structure should sit BELOW the
shuffled distribution (lower agreement than chance); leaves whose divergence is only
small-sample scatter will sit inside it.

WHY THIS IS NEEDED. Leaf sizes are 21-88 questions, so a model's accuracy on one leaf
carries a standard error near 8-9 points while adjacent models in this roster differ
by 2-4. Two noisy rankings of near-tied models can disagree strongly with no
underlying structure at all. Reading a between-leaf rho without this null repeats the
exact error the domain screen was built to avoid.

Ground truth only: eval_results.is_correct on the reserved pool. No judge, no arena.
Bounds what an arena could find; does not show that one found it.
"""
import sqlite3, csv, math, random, statistics
from collections import defaultdict

REPS = 2000
SEED = 42
MIN_LEAF = 20          # leaves below this are excluded from both arms
ROSTER = [
    'gemini-3.1-pro_5-shots', 'iask_pro', 'arx_3', 'claude-3.5-sonnet',
    'gpt-4o-2024-08-06', 'deepseek-chat-v2_5', 'gpt-4o-mini',
    'claude-3-5-sonnet-20241022', 'Qwen1.5-72B-Chat', 'Meta-Llama-3-8B-Instruct',
    'Qwen1.5-14B-Chat', 'Meta-Llama-3-8B',
]

D = sqlite3.connect('mmlu_pro_dataset_cache_v2.db')
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from pool_guard import assert_frozen_pool; assert_frozen_pool(D)  # is_reserved mirrors the ACTIVE pool
Ms = set(ROSTER)
cor = defaultdict(dict)
for q, m, ic in D.execute(
        'select question_id,model_name,is_correct from eval_results where is_reserved=1'):
    if m in Ms:
        cor[str(q)][m] = ic
# keep only questions every roster model answered, so leaf and pseudo-leaf are comparable
full = {q for q, d in cor.items() if len(d) == len(ROSTER)}

leaf = defaultdict(set)
cat = defaultdict(lambda: defaultdict(int))
for r in csv.DictReader(open('reserved_leaf_assignments.csv')):
    if r['question_id'] in full:
        leaf[r['leaf_id']].add(r['question_id'])
        cat[r['leaf_id']][r['category']] += 1
leafdom = {l: max(c, key=c.get) for l, c in cat.items()}


def ranking(qs):
    return {m: sum(cor[q][m] for q in qs) / len(qs) for m in ROSTER}


def spearman(a, b):
    K = ROSTER
    n = len(K)
    def rk(d):
        vs = sorted(K, key=lambda k: d[k]); r = {}; i = 0
        while i < len(vs):
            j = i
            while j + 1 < len(vs) and d[vs[j + 1]] == d[vs[i]]:
                j += 1
            for k in range(i, j + 1):
                r[vs[k]] = (i + j) / 2 + 1
            i = j + 1
        return r
    ra, rb = rk(a), rk(b)
    ma = sum(ra.values()) / n; mb = sum(rb.values()) / n
    den = math.sqrt(sum((ra[k] - ma) ** 2 for k in K) * sum((rb[k] - mb) ** 2 for k in K))
    return sum((ra[k] - ma) * (rb[k] - mb) for k in K) / den if den else None


def median_pairwise(groups):
    """median between-group Spearman over all group pairs"""
    R = [ranking(g) for g in groups]
    rs = [spearman(R[i], R[j]) for i in range(len(R)) for j in range(i + 1, len(R))]
    rs = [x for x in rs if x is not None]
    return statistics.median(rs) if rs else None


bydom = defaultdict(list)
for l, d in leafdom.items():
    if len(leaf[l]) >= MIN_LEAF:
        bydom[d].append(l)

rng = random.Random(SEED)
print(f'Permutation null for within-domain between-leaf agreement')
print(f'{REPS} shuffles, seed {SEED}, roster {len(ROSTER)} models, '
      f'leaves >= {MIN_LEAF} questions, ground truth only\n')
print(f'{"domain":<17}{"leaves":>7}{"nQ":>6}{"observed":>10}{"null p5":>9}'
      f'{"null med":>10}{"p_emp":>8}   verdict')
print('-' * 84)

results = []
for d in sorted(bydom):
    ls = bydom[d]
    if len(ls) < 2:
        continue
    sizes = [min(len(leaf[l]), 10**9) for l in ls]
    pool = sorted(set().union(*(leaf[l] for l in ls)))
    obs = median_pairwise([leaf[l] for l in ls])
    if obs is None:
        continue
    null = []
    # Leaves OVERLAP (soft membership: 3,863 assignments over 3,445 questions), so a
    # disjoint slice of a shuffled pool would exhaust it. Each pseudo-leaf is instead an
    # independent uniform sample of the observed size from the domain pool, which
    # preserves both the size multiset and the overlap rate.
    # Independent sampling was WRONG: it gave pseudo-leaves 11-26% pairwise overlap
    # where real leaves have 1.6-4.9%. Shared questions correlate two groups' accuracy
    # estimates and inflate their agreement, so that null sat too high and made low
    # observed values look significant. Instead deal out the ACTUAL assignment multiset
    # (each question repeated by how many leaves hold it), which preserves both the
    # size profile and the real overlap rate.
    multiset = []
    for l in ls:
        multiset.extend(leaf[l])
    for _ in range(REPS):
        deck = multiset[:]
        rng.shuffle(deck)
        groups, i = [], 0
        ok = True
        for sz in sizes:
            g = set()
            while len(g) < sz and i < len(deck):
                g.add(deck[i]); i += 1
            if len(g) < sz:
                ok = False; break
            groups.append(g)
        if not ok:
            continue
        v = median_pairwise(groups)
        if v is not None:
            null.append(v)
    null.sort()
    # one-sided: real leaves should agree LESS than chance if sub-structure exists
    p = sum(1 for x in null if x <= obs) / len(null)
    verdict = 'SUB-STRUCTURE' if p < 0.05 else ('marginal' if p < 0.10 else 'noise')
    results.append((p, d, len(ls), len(pool), obs, null[len(null) // 20],
                    null[len(null) // 2], verdict))

for p, d, nl, nq, obs, p5, med, verdict in sorted(results):
    print(f'{d:<17}{nl:>7}{nq:>6}{obs:>10.3f}{p5:>9.3f}{med:>10.3f}{p:>8.3f}   {verdict}')

sig = [d for p, d, *_ in results if p < 0.05]
print(f'\ndomains with sub-structure beyond noise (p < 0.05): {sig if sig else "NONE"}')
print('\nA domain whose observed value sits at or above the null median has leaves')
print('that agree with each other MORE than a random split of the same sizes would,')
print('which is the opposite of sub-structure.')
